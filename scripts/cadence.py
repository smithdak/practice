#!/usr/bin/env python3
"""Deterministic offline status report for the Practice operating cadence.

Reads ``ops/cadence.yaml`` -- the machine-readable index of the passes and
queues defined in ``ops/WEEKLY_CADENCE.md`` -- and reports, for every pass:
when its named output last changed, whether its window has elapsed, and which
evidence globs matched nothing. It then reports the queue checks that the
cadence document supports from repository evidence: handoffs recorded
``BLOCKED``, owner gates and operating holds recorded ``OPEN`` in the owner
review packet, and markdown files whose ``As of:`` date is older than the
staleness limit shared with ``scripts/check_links.py``.

Boundaries this report keeps:

- It reads files in this repository only. It cannot see Buzz channel activity,
  Git issues or pull requests, or the private maintainers queue, so a pass can
  be complete outside these files and still show an elapsed window here.
- "Due" means the window has elapsed since the named output last changed. The
  operating rule stands: a pass with no output is skipped and records nothing,
  so an elapsed window is not overdue work for any person, and this report
  assigns nothing to anyone.
- It repeats the recorded status of owner gates and operating holds. It never
  clears one, and it approves, merges, publishes, and moderates nothing.

Last-changed dates come from ``git log``. Outside a git checkout, or when git
is unavailable, every date is reported as ``unknown`` and no window is
computed; the report never substitutes today's date or a file modification
time.

Exit codes: 0 = the report was produced, whatever it found (this is a report,
not a gate); 1 = configuration or usage error.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import textwrap
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = SCRIPT_DIR.parent
DEFAULT_CONFIG_RELATIVE = "ops/cadence.yaml"
SCHEMA_VERSION = 1
EXCLUDED_DIRS = {".git", ".worktrees", "__pycache__"}
GIT_TIMEOUT_SECONDS = 60

DUE_RULES = {"elapsed", "on_trigger"}
REQUIRED_PASS_KEYS = (
    "id",
    "name",
    "rhythm",
    "named_output",
    "owner_role",
    "skip_rule",
    "evidence",
    "source_section",
    "due_rule",
)
REQUIRED_QUEUE_KEYS = ("id", "name", "source_section", "repo_check")
KNOWN_REPO_CHECKS = {"none", "blocked_handoffs", "stale_as_of", "open_owner_gates"}
# The cadence assigns every pass to a role. This guard catches the one personal
# name the repository uses (the founder, per OWNER_GATES.md) being set as an
# owner_role, which would turn a role contract into an assignment to a person.
FOUNDER_NAME = "Dakota"

# Same status contract as scripts/validate.py, so a handoff reads the same way
# to the release validator and to this report.
HANDOFF_STATUS_RE = re.compile(r"^## Status\s*\n+\s*(COMPLETE|BLOCKED)\s*$", re.MULTILINE)
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")
TABLE_SEPARATOR_CELL_RE = re.compile(r"^:?-{3,}:?$")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
GATE_SECTION_HINT = "owner gate"
HOLD_SECTION_HINT = "hold"

SCOPE_NOTE = (
    "This report reads files in this repository only. It cannot see Buzz channel "
    "activity, Git issues or pull requests, or the private maintainers queue, so a "
    "pass can be complete outside these files and still show an elapsed window here.",
    "\"Due\" means the pass window has elapsed since its named output last changed. "
    "The operating rule stands: a pass with no output is skipped and records nothing, "
    "so an elapsed window is not overdue work for any person and this report assigns "
    "nothing to anyone.",
    "Owner gates and operating holds are repeated exactly as the owner review packet "
    "records them. This report clears no gate and no hold, and it approves, merges, "
    "publishes, and moderates nothing.",
)


class ConfigError(Exception):
    """A configuration or usage problem the operator must fix (exit code 1)."""


class ExitOneParser(argparse.ArgumentParser):
    """Argument parser that reports a usage error with exit code 1."""

    def error(self, message: str):
        self.print_usage(sys.stderr)
        print(f"{self.prog}: usage error: {message}", file=sys.stderr)
        raise SystemExit(1)


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------


def load_check_links():
    """Import ``check_links.py`` so the as-of staleness rule is defined once."""
    path = SCRIPT_DIR / "check_links.py"
    if not path.is_file():
        raise ConfigError(
            f"Missing {path}. cadence.py reuses the as-of staleness rule from "
            "scripts/check_links.py; restore that file or run from a full checkout."
        )
    spec = importlib.util.spec_from_file_location("practice_check_links_for_cadence", path)
    if spec is None or spec.loader is None:  # pragma: no cover - import plumbing
        raise ConfigError(f"Could not load {path} as a Python module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_yaml_module():
    try:
        import yaml
    except ImportError as exc:
        raise ConfigError(
            "PyYAML is required to read ops/cadence.yaml: install it with "
            "'python3 -m pip install PyYAML' and run the report again."
        ) from exc
    return yaml


def require(mapping: object, key: str, label: str, kinds: tuple[type, ...]):
    if not isinstance(mapping, dict) or key not in mapping:
        raise ConfigError(f"{label} is missing the required key '{key}'.")
    value = mapping[key]
    if not isinstance(value, kinds):
        wanted = " or ".join(kind.__name__ for kind in kinds)
        raise ConfigError(f"{label} key '{key}' must be {wanted}, got {type(value).__name__}.")
    return value


def validate_config(config: object, config_label: str, staleness_limit: int) -> dict:
    """Return the validated config or raise ``ConfigError`` with a fix to make."""
    if not isinstance(config, dict):
        raise ConfigError(f"{config_label} must contain a YAML mapping at the top level.")
    version = config.get("schema_version")
    if version != SCHEMA_VERSION:
        raise ConfigError(
            f"{config_label} has schema_version {version!r}; this script reads "
            f"schema_version {SCHEMA_VERSION}."
        )
    configured_limit = require(config, "staleness_limit_days", config_label, (int,))
    if configured_limit != staleness_limit:
        raise ConfigError(
            f"{config_label} staleness_limit_days is {configured_limit} but "
            f"STALE_LIMIT_DAYS in scripts/check_links.py is {staleness_limit}. "
            "The repository keeps one staleness rule: change it in check_links.py "
            "and mirror the same number here."
        )
    passes = require(config, "passes", config_label, (list,))
    if not passes:
        raise ConfigError(f"{config_label} defines no passes; it must mirror ops/WEEKLY_CADENCE.md.")
    seen: set[str] = set()
    for index, entry in enumerate(passes):
        label = f"{config_label} passes[{index}]"
        for key in REQUIRED_PASS_KEYS:
            require(entry, key, label, (str, list))
        pass_id = entry["id"]
        if not isinstance(pass_id, str) or not pass_id:
            raise ConfigError(f"{label} key 'id' must be a non-empty string.")
        if pass_id in seen:
            raise ConfigError(f"{config_label} defines pass id '{pass_id}' more than once.")
        seen.add(pass_id)
        if not isinstance(entry["evidence"], list) or not entry["evidence"]:
            raise ConfigError(f"{label} key 'evidence' must be a non-empty list of path globs.")
        for glob in entry["evidence"]:
            if not isinstance(glob, str) or not glob.strip():
                raise ConfigError(f"{label} key 'evidence' contains an entry that is not a path glob.")
        owner_role = entry["owner_role"]
        if not isinstance(owner_role, str) or not owner_role.strip():
            raise ConfigError(f"{label} key 'owner_role' must be a non-empty string.")
        if FOUNDER_NAME.lower() in owner_role.lower():
            raise ConfigError(
                f"{label} key 'owner_role' names a person ('{owner_role}'). The cadence "
                "assigns passes to roles; name the role instead."
            )
        due_rule = entry["due_rule"]
        if due_rule not in DUE_RULES:
            raise ConfigError(
                f"{label} key 'due_rule' is {due_rule!r}; expected one of "
                f"{', '.join(sorted(DUE_RULES))}."
            )
        interval = entry.get("interval_days")
        if due_rule == "elapsed":
            if not isinstance(interval, int) or isinstance(interval, bool) or interval <= 0:
                raise ConfigError(
                    f"{label} has due_rule 'elapsed' and needs a positive integer "
                    f"'interval_days'; got {interval!r}."
                )
        elif interval is not None:
            raise ConfigError(
                f"{label} has due_rule 'on_trigger', which never uses a window; set "
                "'interval_days' to null."
            )
    queues = require(config, "queues", config_label, (list,))
    queue_ids: set[str] = set()
    for index, entry in enumerate(queues):
        label = f"{config_label} queues[{index}]"
        for key in REQUIRED_QUEUE_KEYS:
            require(entry, key, label, (str,))
        if entry["id"] in queue_ids:
            raise ConfigError(f"{config_label} defines queue id '{entry['id']}' more than once.")
        queue_ids.add(entry["id"])
        if entry["repo_check"] not in KNOWN_REPO_CHECKS:
            raise ConfigError(
                f"{label} key 'repo_check' is {entry['repo_check']!r}; expected one of "
                f"{', '.join(sorted(KNOWN_REPO_CHECKS))}."
            )
    checks = require(config, "checks", config_label, (dict,))
    for name in ("blocked_handoffs", "open_owner_gates", "stale_as_of"):
        entry = require(checks, name, f"{config_label} checks", (dict,))
        require(entry, "scans", f"{config_label} checks.{name}", (str,))
    fallback = require(config, "low_activity_fallback", config_label, (dict,))
    fallback_interval = require(fallback, "interval_days", f"{config_label} low_activity_fallback", (int,))
    if fallback_interval <= 0:
        raise ConfigError(f"{config_label} low_activity_fallback interval_days must be positive.")
    return config


def load_config(path: Path, staleness_limit: int) -> dict:
    yaml = load_yaml_module()
    if not path.is_file():
        raise ConfigError(
            f"Missing cadence configuration: {path}. It mirrors ops/WEEKLY_CADENCE.md; "
            "pass --config to point at another copy."
        )
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"Could not parse {path} as YAML: {exc}") from exc
    return validate_config(raw, str(path), staleness_limit)


# --------------------------------------------------------------------------
# Filesystem and git evidence
# --------------------------------------------------------------------------


def is_visible(relative: Path) -> bool:
    return not any(part in EXCLUDED_DIRS for part in relative.parts)


def glob_files(root: Path, pattern: str) -> list[str]:
    """Return sorted repo-relative paths of files matching one glob."""
    matches: list[str] = []
    for path in root.glob(pattern):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if is_visible(relative):
            matches.append(relative.as_posix())
    return sorted(set(matches))


def git_change_dates(root: Path) -> tuple[dict[str, date] | None, str]:
    """Map repo-relative path to its last commit date.

    Returns ``(None, reason)`` when git history is unavailable. The caller then
    reports dates as unknown; it never substitutes today's date or an mtime.
    """
    probe = run_git(root, ["rev-parse", "--is-inside-work-tree"])
    if probe is None:
        return None, "git executable not found on PATH"
    if probe is False or probe.strip() != "true":
        return None, f"{root} is not inside a git work tree"
    log = run_git(
        root,
        ["log", "--format=%x00%cd", "--date=short", "--name-only", "--relative", "--", "."],
    )
    if log is None or log is False:
        return None, "git log could not be read"
    dates: dict[str, date] = {}
    current: date | None = None
    for line in log.split("\n"):
        if line.startswith("\x00"):
            try:
                current = date.fromisoformat(line[1:].strip())
            except ValueError:
                current = None
            continue
        name = line.strip()
        if not name or current is None:
            continue
        if name not in dates:
            dates[name] = current
    return dates, "git log"


def run_git(root: Path, args: list[str]):
    """Return git stdout, ``False`` on a git error, or ``None`` when git is absent."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return False
    if result.returncode != 0:
        return False
    return result.stdout


# --------------------------------------------------------------------------
# Pass evaluation
# --------------------------------------------------------------------------


def pass_window(last_change: date | None, as_of: date, interval_days: int | None, due_rule: str):
    """Return ``(status, due, days_since)`` for one pass.

    ``due`` is ``None`` whenever the answer is not computable, so an unknown is
    never rendered as "not due".
    """
    days_since = None if last_change is None else (as_of - last_change).days
    if due_rule == "on_trigger":
        return "not scheduled (runs only on trigger)", False, days_since
    if last_change is None:
        return "unknown (no last-changed date)", None, None
    if not isinstance(interval_days, int) or interval_days <= 0:
        return "unknown (no window configured)", None, days_since
    if days_since >= interval_days:
        return "window elapsed", True, days_since
    return "within window", False, days_since


def evaluate_pass(entry: dict, root: Path, as_of: date, dates: dict[str, date] | None) -> dict:
    evidence: list[dict] = []
    matched_paths: list[str] = []
    for glob in entry["evidence"]:
        matches = glob_files(root, glob)
        matched_paths.extend(matches)
        newest = None
        if dates is not None:
            glob_dates = [dates[path] for path in matches if path in dates]
            newest = max(glob_dates).isoformat() if glob_dates else None
        evidence.append(
            {
                "glob": glob,
                "matches": len(matches),
                "newest_match": newest,
                "example": matches[0] if matches else None,
            }
        )
    matched_paths = sorted(set(matched_paths))
    last_change: date | None = None
    if dates is not None:
        known = [dates[path] for path in matched_paths if path in dates]
        if known:
            last_change = max(known)
    interval = entry.get("interval_days")
    status, due, days_since = pass_window(last_change, as_of, interval, entry["due_rule"])
    missing = sorted(record["glob"] for record in evidence if record["matches"] == 0)
    untracked = sorted(path for path in matched_paths if dates is not None and path not in dates)
    return {
        "id": entry["id"],
        "name": entry["name"],
        "rhythm": entry["rhythm"],
        "source_section": entry["source_section"],
        "named_output": entry["named_output"],
        "owner_role": entry["owner_role"],
        "skip_rule": entry["skip_rule"],
        "note": entry.get("note"),
        "due_rule": entry["due_rule"],
        "interval_days": interval,
        "last_output_change": last_change.isoformat() if last_change else None,
        "days_since": days_since,
        "due": due,
        "status": status,
        "evidence": evidence,
        "evidence_files": len(matched_paths),
        "missing_evidence": missing,
        "untracked_evidence": untracked,
        "off_repo_records": list(entry.get("off_repo_records") or []),
    }


# --------------------------------------------------------------------------
# Queue checks
# --------------------------------------------------------------------------


def check_blocked_handoffs(root: Path, pattern: str) -> dict:
    blocked: list[dict] = []
    unreadable: list[str] = []
    paths = glob_files(root, pattern)
    for relative in paths:
        text = (root / relative).read_text(encoding="utf-8", errors="replace")
        match = HANDOFF_STATUS_RE.search(text)
        if match is None:
            unreadable.append(relative)
        elif match.group(1) == "BLOCKED":
            blocked.append({"path": relative, "status": "BLOCKED"})
    return {
        "scanned": pattern,
        "records": len(paths),
        "blocked": blocked,
        "unreadable_status": unreadable,
    }


def strip_markdown(cell: str) -> str:
    return MARKDOWN_LINK_RE.sub(r"\1", cell).replace("**", "").strip()


def parse_status_tables(text: str) -> list[dict]:
    """Return rows of every markdown table whose last column is named Status."""
    rows: list[dict] = []
    section = ""
    header_seen = False
    for line in text.split("\n"):
        heading = HEADING_RE.match(line)
        if heading:
            section = heading.group(1)
            header_seen = False
            continue
        stripped = line.strip()
        if not stripped.startswith("|"):
            header_seen = False
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if all(TABLE_SEPARATOR_CELL_RE.match(cell) for cell in cells if cell):
            continue
        if strip_markdown(cells[-1]).lower() == "status":
            header_seen = True
            continue
        if not header_seen:
            continue
        rows.append(
            {
                "section": section,
                "name": strip_markdown(cells[0]),
                "status": strip_markdown(cells[-1]),
            }
        )
    return rows


def check_open_owner_gates(root: Path, relative: str) -> dict:
    path = root / relative
    if not path.is_file():
        return {
            "scanned": relative,
            "available": False,
            "reason": f"{relative} not found",
            "gates": [],
            "holds": [],
            "other_rows": [],
            "rows_scanned": 0,
        }
    rows = parse_status_tables(path.read_text(encoding="utf-8", errors="replace"))
    gates: list[dict] = []
    holds: list[dict] = []
    other: list[dict] = []
    for row in rows:
        section = row["section"].lower()
        record = {"name": row["name"], "status": row["status"], "open": "OPEN" in row["status"].upper()}
        if GATE_SECTION_HINT in section:
            gates.append(record)
        elif HOLD_SECTION_HINT in section:
            holds.append(record)
        else:
            other.append(record)
    return {
        "scanned": relative,
        "available": True,
        "reason": None,
        "gates": gates,
        "holds": holds,
        "other_rows": other,
        "rows_scanned": len(rows),
    }


def check_stale_as_of(root: Path, as_of: date, limit_days: int, check_links) -> dict:
    """Apply the as-of staleness rule from scripts/check_links.py."""
    stale: list[dict] = []
    dated = 0
    for path in check_links.find_markdown_files(root):
        relative = path.relative_to(root).as_posix()
        masked = check_links.mask_code(path.read_text(encoding="utf-8", errors="replace"))
        for line_no, iso_date in check_links.extract_as_of_dates(masked):
            dated += 1
            age_days = (as_of - date.fromisoformat(iso_date)).days
            if age_days > limit_days:
                stale.append(
                    {"path": relative, "line": line_no, "as_of": iso_date, "age_days": age_days}
                )
    stale.sort(key=lambda item: (item["path"], item["line"]))
    return {
        "limit_days": limit_days,
        "rule_source": "scripts/check_links.py",
        "dates_checked": dated,
        "stale": stale,
    }


# --------------------------------------------------------------------------
# Report assembly
# --------------------------------------------------------------------------


def build_report(root: Path, config_path: Path, config: dict, as_of: date, check_links) -> dict:
    dates, git_reason = git_change_dates(root)
    passes = [evaluate_pass(entry, root, as_of, dates) for entry in config["passes"]]
    checks_config = config["checks"]
    blocked = check_blocked_handoffs(root, checks_config["blocked_handoffs"]["scans"])
    gates = check_open_owner_gates(root, checks_config["open_owner_gates"]["scans"])
    stale = check_stale_as_of(root, as_of, config["staleness_limit_days"], check_links)
    queues = []
    for entry in config["queues"]:
        queues.append(
            {
                "id": entry["id"],
                "name": entry["name"],
                "source_section": entry["source_section"],
                "human_owner_role": entry.get("human_owner_role"),
                "agent_boundary": entry.get("agent_boundary"),
                "repo_check": entry["repo_check"],
                "repo_check_reason": entry.get("repo_check_reason"),
                "repo_check_note": entry.get("repo_check_note"),
            }
        )
    fallback = dict(config["low_activity_fallback"])
    newest = [p["last_output_change"] for p in passes if p["last_output_change"]]
    fallback_last = max(newest) if newest else None
    if fallback_last is None:
        fallback_status = "unknown (no last-changed date)"
        fallback_days = None
    else:
        fallback_days = (as_of - date.fromisoformat(fallback_last)).days
        fallback_status = (
            "window elapsed" if fallback_days >= int(fallback["interval_days"]) else "within window"
        )
    escalations = dict(config.get("escalations") or {})
    open_gates = [row for row in gates["gates"] if row["open"]]
    open_holds = [row for row in gates["holds"] if row["open"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "as_of": as_of.isoformat(),
        "root": str(root),
        "config": config_path.as_posix(),
        "source": config.get("source"),
        "scope_note": list(SCOPE_NOTE),
        "operating_rule": config.get("operating_rule"),
        "git": {"available": dates is not None, "reason": git_reason},
        "passes": passes,
        "queues": queues,
        "escalations": {
            "id": escalations.get("id"),
            "name": escalations.get("name"),
            "source_section": escalations.get("source_section"),
            "rule": escalations.get("rule"),
            "repo_check": escalations.get("repo_check"),
        },
        "checks": {
            "blocked_handoffs": blocked,
            "open_owner_gates": gates,
            "stale_as_of": stale,
        },
        "low_activity_fallback": {
            "source_section": fallback.get("source_section"),
            "interval_days": fallback["interval_days"],
            "rule": fallback.get("rule"),
            "last_evidence_change": fallback_last,
            "days_since": fallback_days,
            "status": fallback_status,
        },
        "summary": {
            "passes": len(passes),
            "passes_with_elapsed_window": sum(1 for p in passes if p["due"] is True),
            "passes_unknown": sum(1 for p in passes if p["due"] is None),
            "passes_missing_evidence": sum(1 for p in passes if p["missing_evidence"]),
            "blocked_handoffs": len(blocked["blocked"]),
            "open_owner_gates": len(open_gates),
            "open_operating_holds": len(open_holds),
            "stale_as_of_dates": len(stale["stale"]),
        },
    }


def wrap(text: str, first: str = "  ", rest: str | None = None, width: int = 88) -> list[str]:
    """Wrap prose deterministically for the text report."""
    body = " ".join(str(text).split())
    if not body:
        return []
    return textwrap.wrap(
        body,
        width=width,
        initial_indent=first,
        subsequent_indent=" " * len(first) if rest is None else rest,
        break_long_words=False,
        break_on_hyphens=False,
    )


def render_text(report: dict) -> str:
    out: list[str] = []
    out.append("Practice cadence report")
    out.append(f"  as of         {report['as_of']}")
    out.append(f"  repository    {report['root']}")
    out.append(f"  cadence index {report['config']} (mirrors {report['source']})")
    git = report["git"]
    out.append(
        f"  change dates  {'git log' if git['available'] else 'unknown -- ' + git['reason']}"
    )
    out.append("")
    out.append("Scope and limits")
    for note in report["scope_note"]:
        out.extend(wrap(note, first="  - ", rest="    "))
    out.append("")
    out.append("Passes")
    for entry in report["passes"]:
        days = "unknown" if entry["days_since"] is None else f"{entry['days_since']}d ago"
        last = entry["last_output_change"] or "unknown"
        window = "n/a" if entry["interval_days"] is None else f"{entry['interval_days']}d"
        out.append(f"  {entry['id']}")
        out.append(f"    name          {entry['name']} ({entry['rhythm']})")
        out.append(f"    owner role    {' '.join(entry['owner_role'].split())}")
        out.append(f"    last output   {last} ({days})")
        out.append(f"    window        {window} -- {entry['status']}")
        if entry["missing_evidence"]:
            out.append(f"    missing       {', '.join(entry['missing_evidence'])} (no file matched)")
        else:
            out.append(f"    evidence      {entry['evidence_files']} file(s) matched")
        if entry["untracked_evidence"]:
            out.append(
                f"    untracked     {len(entry['untracked_evidence'])} matched file(s) have no commit yet"
            )
        if entry["note"]:
            out.extend(wrap(entry["note"], first="    note: ", rest="          "))
    out.append("")
    out.append("Queues")
    for entry in report["queues"]:
        out.append(f"  {entry['id']} -- {entry['name']}")
        if entry["repo_check"] == "none":
            reason = entry["repo_check_reason"] or "not observable from repository files"
            out.extend(wrap(f"no repository check: {reason}", first="    "))
        else:
            out.append(f"    repository check: {entry['repo_check']}")
    out.append("")
    blocked = report["checks"]["blocked_handoffs"]
    out.append(f"Blocked handoffs (agent review queue, {blocked['records']} record(s) scanned)")
    if blocked["blocked"]:
        for record in blocked["blocked"]:
            out.append(f"  BLOCKED  {record['path']}")
    else:
        out.append("  none")
    for path in blocked["unreadable_status"]:
        out.append(f"  status line unreadable  {path}")
    out.append("")
    gates = report["checks"]["open_owner_gates"]
    out.append(f"Owner gates and operating holds ({gates['scanned']})")
    if not gates["available"]:
        out.append(f"  unavailable: {gates['reason']}")
    else:
        for label, rows in (("gate", gates["gates"]), ("hold", gates["holds"])):
            for row in rows:
                state = "OPEN" if row["open"] else "recorded"
                out.append(f"  {state:9}{label}: {row['name']} -- {row['status']}")
        out.extend(
            wrap(
                "These rows are repeated as recorded. This report clears nothing; each "
                "one needs a human decision recorded in the owner review packet."
            )
        )
    out.append("")
    stale = report["checks"]["stale_as_of"]
    out.append(
        f"Stale as-of dates (limit {stale['limit_days']}d, rule from {stale['rule_source']}; "
        f"{stale['dates_checked']} date(s) checked)"
    )
    if stale["stale"]:
        for record in stale["stale"]:
            out.append(
                f"  {record['path']}:{record['line']}: as of {record['as_of']} "
                f"({record['age_days']}d old)"
            )
    else:
        out.append("  none")
    out.append("")
    fallback = report["low_activity_fallback"]
    out.append("Low-activity fallback")
    out.append(
        f"  one short operating pass every {fallback['interval_days']}d -- {fallback['status']}"
    )
    if fallback["last_evidence_change"] is None:
        out.append("  newest pass evidence change: unknown")
    else:
        out.append(
            f"  newest pass evidence change: {fallback['last_evidence_change']} "
            f"({fallback['days_since']}d ago)"
        )
    out.append("")
    summary = report["summary"]
    out.append("Summary")
    for key in sorted(summary):
        out.append(f"  {key.replace('_', ' '):28}{summary[key]}")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected a YYYY-MM-DD date, got {value!r}")


def build_parser() -> ExitOneParser:
    parser = ExitOneParser(
        prog="cadence.py",
        description=__doc__.splitlines()[0],
    )
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="repository root to inspect")
    parser.add_argument(
        "--config",
        default=None,
        help=f"cadence index to read (default: <root>/{DEFAULT_CONFIG_RELATIVE})",
    )
    parser.add_argument(
        "--as-of",
        type=iso_date,
        default=None,
        help="override today's date as YYYY-MM-DD so the report is reproducible",
    )
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = Path(args.root).resolve()
        if not root.is_dir():
            raise ConfigError(f"--root is not a directory: {args.root}")
        config_path = Path(args.config).resolve() if args.config else root / DEFAULT_CONFIG_RELATIVE
        check_links = load_check_links()
        config = load_config(config_path, check_links.STALE_LIMIT_DAYS)
        as_of = args.as_of or date.today()
        try:
            shown_config = config_path.relative_to(root)
        except ValueError:
            shown_config = config_path
        report = build_report(root, Path(shown_config), config, as_of, check_links)
    except ConfigError as exc:
        print(f"cadence.py: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
