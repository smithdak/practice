#!/usr/bin/env python3
"""Deterministic offline recorder and checker for Practice action ledger entries.

An action ledger entry is a markdown file with YAML front matter under
``ops/ledger/``, named ``<YYYY-MM-DD>-<run_id>.md``. One entry records one run
of one operation: what triggered it, the promotion record and kill-switch state
it observed, the preconditions it checked and their results, the paths it read,
every path it wrote, the reversal a human can execute without the agent, and how
the run ended. The shape is defined in ``docs/schemas/ACTION_LEDGER_SCHEMA.md``.

``validate`` checks one or more entries or directories of them:

- every required field is present and uses its controlled vocabulary;
- a recorded promotion names its level, its signing role, its signing date, and
  the review point in force at run time; ``promotion: none`` needs none of them;
- the reversal is recorded and is not a placeholder;
- the claimed level is one the autonomy ladder defines;
- at least one precondition is recorded, and a refused run names the
  precondition that failed;
- a run recording no writes is not also recording written paths, and a run that
  claims to have completed lists written paths that exist under ``--root``;
- the file name matches the ``run_date`` and ``run_id`` it carries; and
- no entry carries an email address, a handle, or a phone number.

``append`` writes one entry from structured input, so a runner records a run
without reproducing the format. It refuses to overwrite an existing entry: the
ledger is append-only, and a correction is a new entry naming the one it
supersedes.

This tool records and checks runs. **A valid entry is not a permission.** It
does not mean the run was allowed, that a promotion exists, or that the kill
switch was released; it means the record of the run is complete enough to audit.
Whether a recorded run was within its bounds is judged by the demotion check and
by a human, not here.

Exit codes: 0 = every entry valid (or written), 1 = at least one violation,
2 = usage error.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    print(
        "scripts/ledger.py needs PyYAML to read entry front matter. "
        "Fix: python3 -m pip install PyYAML",
        file=sys.stderr,
    )
    raise SystemExit(2)

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER_DIR = ("ops", "ledger")
SCHEMA_REF = "docs/schemas/ACTION_LEDGER_SCHEMA.md"
LADDER_REF = "docs/framework/AUTONOMY_LADDER.md"
CATALOG_REF = "ops/autonomy/operations.yaml"

# The one schema version this checker reads. A new required field, a new
# controlled value, or a new file-name shape is version 2, not an edit here.
LEDGER_SCHEMA_VERSION = 1

# Level ids from docs/framework/AUTONOMY_LADDER.md. A0-A2 map to the registry
# and packet values observe, draft, and recommend; A3 is
# act-unattended-within-bounds, which no operation in this repository holds.
LEVEL_ORDER = ("A0", "A1", "A2", "A3")
LEVELS = frozenset(LEVEL_ORDER)
LEVEL_PACKET_VALUE = {"A0": "observe", "A1": "draft", "A2": "recommend"}

TRIGGER_ORDER = ("manual", "schedule")
TRIGGERS = frozenset(TRIGGER_ORDER)

KILL_SWITCH_ORDER = ("engaged", "released")
KILL_SWITCH_STATES = frozenset(KILL_SWITCH_ORDER)

OUTCOME_ORDER = ("refused", "dry-run", "completed", "failed", "reverted")
OUTCOMES = frozenset(OUTCOME_ORDER)
# A run that never acted cannot also have written something.
OUTCOMES_WITHOUT_WRITES = frozenset({"refused", "dry-run"})
# The successful outcome: what it says it wrote must be there to read.
OUTCOMES_REQUIRING_WRITES_TO_EXIST = frozenset({"completed"})

RESULT_ORDER = ("pass", "fail")
RESULTS = frozenset(RESULT_ORDER)

FIELD_ORDER = (
    "ledger_schema_version",
    "run_id",
    "run_date",
    "operation",
    "actor",
    "claimed_level",
    "trigger",
    "kill_switch",
    "promotion",
    "preconditions",
    "command",
    "source_commit",
    "write_scope",
    "paths_read",
    "paths_written",
    "reversal",
    "outcome",
    "supersedes",
)
REQUIRED_FIELDS = (
    "ledger_schema_version",
    "run_id",
    "run_date",
    "operation",
    "actor",
    "claimed_level",
    "trigger",
    "kill_switch",
    "promotion",
    "preconditions",
    "write_scope",
    "paths_read",
    "paths_written",
    "reversal",
    "outcome",
)
OPTIONAL_FIELDS = ("command", "source_commit", "supersedes")
ALLOWED_FIELDS = FIELD_ORDER

FIELD_HELP = {
    "ledger_schema_version": f"the integer {LEDGER_SCHEMA_VERSION}",
    "run_id": "a lowercase slug naming this run, unique in the ledger",
    "run_date": "the ISO date the run happened, matching the file name",
    "operation": "the operation id the run executed",
    "actor": "a slug naming the identity that ran it; a role or automation label, never a person",
    "claimed_level": f"the autonomy level the run claimed: one of {', '.join(LEVEL_ORDER)}",
    "trigger": f"what started the run: one of {', '.join(TRIGGER_ORDER)}",
    "kill_switch": f"the kill-switch state read at run time: one of {', '.join(KILL_SWITCH_ORDER)}",
    "promotion": "the promotion record observed at run time, or `none` when there was none",
    "preconditions": "the checks the run made before acting, each with its result",
    "command": "the operation's command as argv, when one was recorded",
    "source_commit": "7 to 40 hexadecimal characters naming the commit the run read",
    "write_scope": "the write bound recorded for the operation at run time, as repository-relative patterns",
    "paths_read": "every repository-relative path the run read",
    "paths_written": "every repository-relative path the run created or changed",
    "reversal": "how a human undoes this run without the agent",
    "outcome": f"how the run ended: one of {', '.join(OUTCOME_ORDER)}",
    "supersedes": "the run_id of the entry this one corrects",
}

# A recorded promotion carries its review point: the ladder demotes on an
# action taken after the review point passed without a renewal record, and
# that is checkable only from the entry. `promotion: none` needs no such field.
PROMOTION_REQUIRED = ("level", "signed_by", "signed_on", "review_point")
PROMOTION_OPTIONAL: tuple[str, ...] = ()
PROMOTION_FIELDS = PROMOTION_REQUIRED + PROMOTION_OPTIONAL
PRECONDITION_REQUIRED = ("check", "result", "detail")
PRECONDITION_FIELDS = PRECONDITION_REQUIRED

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RUN_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
PLACEHOLDER_RE = re.compile(r"^(todo|tbd|n/?a|none|null|unknown|pending|\?+|-+|\.+)$", re.IGNORECASE)
GLOB_CHARS = "*?[]"
MIN_TEXT_LENGTH = 8

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
HANDLE_RE = re.compile(r"(?<![A-Za-z0-9._%+/-])@[A-Za-z][A-Za-z0-9._-]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(?:\+\d{1,3}[ .\-]?)?(?:\(\d{3}\)|\d{3})[ .\-]\d{3}[ .\-]\d{4}(?!\d)")
H1_RE = re.compile(r"^#\s+\S", re.MULTILINE)

SAMPLE_PREFIX = "SAMPLE_"


class UsageError(Exception):
    """Raised for an operator mistake, reported with exit code 2."""


class LedgerError(Exception):
    """Raised when an entry cannot be written; carries the violations found."""

    def __init__(self, message: str, violations: list[str] | None = None) -> None:
        super().__init__(message)
        self.violations = list(violations or [])

    def report(self) -> str:
        if not self.violations:
            return str(self)
        return "\n".join([str(self), *[f"- {violation}" for violation in self.violations]])


def problem(relative: str, locator: str, message: str, fix: str) -> str:
    return f"{relative}: {locator}: {message} Fix: {fix}."


def joined(values) -> str:
    return ", ".join(values)


def as_text(value) -> str:
    """Render a scalar front-matter value as the string the checks read."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def display_path(path: Path, root: Path) -> str:
    try:
        return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


# --- Loading ----------------------------------------------------------------

def split_front_matter(text: str) -> tuple[str | None, str]:
    """Return ``(front_matter_text, body)``; front matter is ``None`` when absent."""
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1:])
    return None, text


def load_entry(path: Path, relative: str) -> tuple[dict | None, str, str, list[str]]:
    """Parse an entry file into ``(front_matter, body, raw_text, errors)``."""
    try:
        raw_text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        return None, "", "", [problem(relative, "file", f"cannot be read ({exc}).", "check the path and permissions")]
    front_matter_text, body = split_front_matter(raw_text)
    if front_matter_text is None:
        return None, body, raw_text, [
            problem(
                relative,
                "front matter",
                "no YAML front matter found.",
                "start the file with a `---` line, the entry fields, and a closing `---` line",
            )
        ]
    try:
        data = yaml.safe_load(front_matter_text)
    except yaml.YAMLError as exc:
        detail = str(exc).replace("\n", " ")
        return None, body, raw_text, [
            problem(relative, "front matter", f"is not valid YAML ({detail}).", "correct the YAML syntax")
        ]
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return None, body, raw_text, [
            problem(relative, "front matter", "is not a mapping of fields.", "write one `field: value` pair per line")
        ]
    return data, body, raw_text, []


# --- Field-level checks -----------------------------------------------------

def check_text_value(value, relative: str, locator: str, errors: list[str], purpose: str) -> str:
    text = as_text(value).strip()
    if not text:
        errors.append(problem(relative, locator, "is empty.", f"record {purpose}"))
        return ""
    if PLACEHOLDER_RE.match(text):
        errors.append(
            problem(
                relative,
                locator,
                f"'{text}' is a placeholder, not a record of what happened.",
                f"record {purpose}",
            )
        )
        return text
    if len(text) < MIN_TEXT_LENGTH:
        errors.append(
            problem(
                relative,
                locator,
                f"'{text}' is too short to be readable by an auditor.",
                f"record {purpose} in at least {MIN_TEXT_LENGTH} characters",
            )
        )
    return text


def check_slug_value(value, relative: str, locator: str, errors: list[str], purpose: str) -> str:
    text = as_text(value).strip()
    if not SLUG_RE.match(text):
        errors.append(
            problem(
                relative,
                locator,
                f"'{text}' is not a lowercase slug.",
                f"use lowercase words joined by hyphens, for example `cadence-snapshot`; it names {purpose}",
            )
        )
    return text


def check_date_value(value, relative: str, locator: str, errors: list[str]) -> str:
    text = as_text(value).strip()
    if not ISO_DATE_RE.match(text):
        errors.append(problem(relative, locator, f"'{text}' is not an ISO date.", "write it as YYYY-MM-DD"))
        return ""
    try:
        date.fromisoformat(text)
    except ValueError:
        errors.append(problem(relative, locator, f"'{text}' is not a real date.", "write a calendar date as YYYY-MM-DD"))
        return ""
    return text


def check_repository_path(value, relative: str, locator: str, errors: list[str], allow_glob: bool) -> str:
    text = as_text(value).strip()
    if not text:
        errors.append(problem(relative, locator, "is empty.", "write a repository-relative path"))
        return ""
    if "\\" in text:
        errors.append(
            problem(relative, locator, f"'{text}' uses a backslash.", "write repository-relative paths with `/`")
        )
        return text
    if text.startswith("/") or re.match(r"^[A-Za-z]:", text):
        errors.append(
            problem(
                relative,
                locator,
                f"'{text}' is an absolute path.",
                "write it relative to the repository root, for example `ops/status/2026-09-02.md`",
            )
        )
        return text
    if ".." in Path(text).parts:
        errors.append(
            problem(
                relative,
                locator,
                f"'{text}' escapes the repository root.",
                "write a path inside the repository, without `..`",
            )
        )
        return text
    if not allow_glob and any(character in text for character in GLOB_CHARS):
        errors.append(
            problem(
                relative,
                locator,
                f"'{text}' is a pattern, not a path.",
                "record the exact path the run touched; patterns belong in `write_scope`",
            )
        )
    return text


def check_path_list(value, relative: str, field: str, errors: list[str], allow_glob: bool) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        errors.append(
            problem(
                relative,
                field,
                "is not a list.",
                f"write a YAML list, or `[]` when there is nothing to record; it holds {FIELD_HELP[field]}",
            )
        )
        return []
    paths: list[str] = []
    for index, item in enumerate(value):
        if isinstance(item, (dict, list, tuple)):
            errors.append(problem(relative, f"{field}[{index}]", "is not a path.", "write one path per list item"))
            continue
        paths.append(check_repository_path(item, relative, f"{field}[{index}]", errors, allow_glob))
    return [path for path in paths if path]


def check_promotion(value, relative: str, errors: list[str]) -> dict | None:
    """Return the promotion mapping, or ``None`` when the entry records `none`."""
    if isinstance(value, str):
        text = value.strip()
        if text.lower() == "none":
            return None
        errors.append(
            problem(
                relative,
                "promotion",
                f"'{text}' is not a promotion record.",
                "write `promotion: none` when no promotion was found, or a mapping with "
                f"{joined(PROMOTION_REQUIRED)}",
            )
        )
        return None
    if not isinstance(value, dict):
        errors.append(
            problem(
                relative,
                "promotion",
                "is neither `none` nor a mapping.",
                "write `promotion: none`, or the promotion the run read, with "
                f"{joined(PROMOTION_REQUIRED)}",
            )
        )
        return None
    for key in value:
        name = as_text(key)
        if name not in PROMOTION_FIELDS:
            errors.append(
                problem(
                    relative,
                    f"promotion.{name}",
                    "is not a promotion field.",
                    f"remove it; the fields are: {joined(PROMOTION_FIELDS)}",
                )
            )
    for name in PROMOTION_REQUIRED:
        if value.get(name) in (None, ""):
            errors.append(
                problem(
                    relative,
                    f"promotion.{name}",
                    "is missing.",
                    "copy it from the promotion record the run read, so the entry stands on its own",
                )
            )
    level = as_text(value.get("level", "")).strip()
    if level and level not in LEVELS:
        errors.append(
            problem(
                relative,
                "promotion.level",
                f"'{level}' is not an autonomy level.",
                f"use one of: {joined(LEVEL_ORDER)} ({LADDER_REF})",
            )
        )
    if value.get("signed_by") not in (None, ""):
        check_slug_value(value["signed_by"], relative, "promotion.signed_by", errors, "the role that signed the promotion")
    if value.get("signed_on") not in (None, ""):
        check_date_value(value["signed_on"], relative, "promotion.signed_on", errors)
    if value.get("review_point") not in (None, ""):
        check_date_value(value["review_point"], relative, "promotion.review_point", errors)
    return value


def check_preconditions(value, relative: str, errors: list[str]) -> list[dict]:
    if value is None or (isinstance(value, (list, tuple)) and not value):
        errors.append(
            problem(
                relative,
                "preconditions",
                "records no check.",
                "list every precondition the run evaluated and its result; a run that checked nothing "
                "before acting has no record that it stayed in bounds",
            )
        )
        return []
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        errors.append(
            problem(
                relative,
                "preconditions",
                "is not a list of checks.",
                "write a YAML list of `check`, `result`, `detail` mappings",
            )
        )
        return []
    checks: list[dict] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        locator = f"preconditions[{index}]"
        if not isinstance(item, dict):
            errors.append(
                problem(relative, locator, "is not a mapping.", f"write {joined(PRECONDITION_REQUIRED)} for each check")
            )
            continue
        for key in item:
            name = as_text(key)
            if name not in PRECONDITION_FIELDS:
                errors.append(
                    problem(
                        relative,
                        f"{locator}.{name}",
                        "is not a precondition field.",
                        f"remove it; the fields are: {joined(PRECONDITION_FIELDS)}",
                    )
                )
        for name in PRECONDITION_REQUIRED:
            if item.get(name) in (None, ""):
                errors.append(problem(relative, f"{locator}.{name}", "is missing.", f"add `{name}`"))
        name = as_text(item.get("check", "")).strip()
        if name:
            check_slug_value(item["check"], relative, f"{locator}.check", errors, "the precondition the guard evaluated")
            if name in seen:
                errors.append(
                    problem(
                        relative,
                        f"{locator}.check",
                        f"'{name}' is recorded twice.",
                        "record each precondition once, with the result the run observed",
                    )
                )
            seen.add(name)
        result = as_text(item.get("result", "")).strip()
        if result and result not in RESULTS:
            errors.append(
                problem(
                    relative,
                    f"{locator}.result",
                    f"'{result}' is not a precondition result.",
                    f"use one of: {joined(RESULT_ORDER)}",
                )
            )
        if item.get("detail") not in (None, ""):
            check_text_value(
                item["detail"], relative, f"{locator}.detail", errors, "what the check read and what it found"
            )
        checks.append(item)
    return checks


def scan_personal_data(text: str, relative: str) -> list[str]:
    """Report an email address, a handle, or a phone number anywhere in the entry."""
    errors: list[str] = []
    for number, line in enumerate(text.split("\n"), start=1):
        locator = f"line {number}"
        if EMAIL_RE.search(line):
            errors.append(
                problem(relative, locator, "contains an email address.", "record a role or automation label instead")
            )
        stripped = EMAIL_RE.sub(" ", line)
        if HANDLE_RE.search(stripped):
            errors.append(
                problem(relative, locator, "contains a handle.", "record a role or automation label instead")
            )
        if PHONE_RE.search(stripped):
            errors.append(
                problem(relative, locator, "contains a phone number.", "remove it; a ledger entry carries no personal data")
            )
    return errors


# --- Catalog cross-check ----------------------------------------------------

def catalog_operation_ids(root: Path) -> frozenset[str] | None:
    """Operation ids from the catalog, or ``None`` when it cannot be read."""
    path = Path(root) / Path(CATALOG_REF)
    if not path.is_file():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(data, dict):
        return None
    operations = data.get("operations")
    if not isinstance(operations, list):
        return None
    ids = {
        as_text(entry["id"]).strip()
        for entry in operations
        if isinstance(entry, dict) and entry.get("id") not in (None, "")
    }
    return frozenset(ids) if ids else None


# --- Entry validation -------------------------------------------------------

def validate_entry(data: dict, body: str, relative: str, root: Path, seen_run_ids: dict | None = None) -> list[str]:
    """Return every violation in one parsed entry."""
    root = Path(root)
    errors: list[str] = []

    for key in data:
        name = as_text(key)
        if name not in ALLOWED_FIELDS:
            errors.append(
                problem(
                    relative,
                    name,
                    "is not an action ledger field.",
                    f"remove it; the fields are: {joined(ALLOWED_FIELDS)} ({SCHEMA_REF})",
                )
            )
    for name in REQUIRED_FIELDS:
        value = data.get(name)
        missing = name not in data or value is None or (isinstance(value, str) and not value.strip())
        if missing:
            errors.append(problem(relative, name, "is missing.", f"add `{name}`: {FIELD_HELP[name]}"))

    version = data.get("ledger_schema_version")
    if version not in (None, ""):
        try:
            number = int(as_text(version).strip())
        except ValueError:
            number = None
        if number != LEDGER_SCHEMA_VERSION:
            errors.append(
                problem(
                    relative,
                    "ledger_schema_version",
                    f"'{as_text(version)}' is not a version this checker reads.",
                    f"write `ledger_schema_version: {LEDGER_SCHEMA_VERSION}`",
                )
            )

    run_id = ""
    if data.get("run_id") not in (None, ""):
        run_id = as_text(data["run_id"]).strip()
        if not RUN_ID_RE.match(run_id) or not (4 <= len(run_id) <= 80):
            errors.append(
                problem(
                    relative,
                    "run_id",
                    f"'{run_id}' is not a run id.",
                    "use a lowercase slug of 4 to 80 characters, for example `cadence-snapshot-2026-09-02-01`",
                )
            )
        elif seen_run_ids is not None:
            if run_id in seen_run_ids:
                errors.append(
                    problem(
                        relative,
                        "run_id",
                        f"'{run_id}' is already used by {seen_run_ids[run_id]}.",
                        "give each run its own id; a correction is a new entry with `supersedes`",
                    )
                )
            else:
                seen_run_ids[run_id] = relative

    run_date = ""
    if data.get("run_date") not in (None, ""):
        run_date = check_date_value(data["run_date"], relative, "run_date", errors)

    if data.get("operation") not in (None, ""):
        operation = check_slug_value(data["operation"], relative, "operation", errors, "the operation that ran")
        known = catalog_operation_ids(root)
        if known is not None and operation and operation not in known:
            errors.append(
                problem(
                    relative,
                    "operation",
                    f"'{operation}' is not an operation in {CATALOG_REF}.",
                    f"use one of: {joined(sorted(known))}, or add the operation to the catalog first",
                )
            )

    if data.get("actor") not in (None, ""):
        check_slug_value(data["actor"], relative, "actor", errors, "the identity that ran the operation")

    claimed_level = ""
    if data.get("claimed_level") not in (None, ""):
        claimed_level = as_text(data["claimed_level"]).strip()
        if claimed_level not in LEVELS:
            errors.append(
                problem(
                    relative,
                    "claimed_level",
                    f"'{claimed_level}' is not an autonomy level.",
                    f"use one of: {joined(LEVEL_ORDER)} ({LADDER_REF}); the packet values "
                    f"{joined(sorted(LEVEL_PACKET_VALUE.values()))} are not level ids",
                )
            )

    if data.get("trigger") not in (None, ""):
        trigger = as_text(data["trigger"]).strip()
        if trigger not in TRIGGERS:
            errors.append(
                problem(
                    relative,
                    "trigger",
                    f"'{trigger}' is not a trigger.",
                    f"use one of: {joined(TRIGGER_ORDER)}",
                )
            )

    if data.get("kill_switch") not in (None, ""):
        kill_switch = as_text(data["kill_switch"]).strip()
        if kill_switch not in KILL_SWITCH_STATES:
            errors.append(
                problem(
                    relative,
                    "kill_switch",
                    f"'{kill_switch}' is not a kill-switch state.",
                    f"record what the run read: one of {joined(KILL_SWITCH_ORDER)}",
                )
            )

    if "promotion" in data and data.get("promotion") is not None:
        check_promotion(data["promotion"], relative, errors)

    checks = check_preconditions(data.get("preconditions"), relative, errors)

    if "command" in data:
        command = data["command"]
        if isinstance(command, str) or not isinstance(command, (list, tuple)) or not command:
            errors.append(
                problem(
                    relative,
                    "command",
                    "is not a non-empty argv list.",
                    'write the command as a list, for example ["python3", "scripts/cadence.py"]',
                )
            )
        else:
            for index, item in enumerate(command):
                if not as_text(item).strip():
                    errors.append(problem(relative, f"command[{index}]", "is empty.", "remove it or write the argument"))

    if data.get("source_commit") not in (None, ""):
        commit = as_text(data["source_commit"]).strip()
        if not COMMIT_RE.match(commit):
            errors.append(
                problem(
                    relative,
                    "source_commit",
                    f"'{commit}' is not a commit id.",
                    "write 7 to 40 lowercase hexadecimal characters",
                )
            )

    if data.get("supersedes") not in (None, ""):
        superseded = check_slug_value(
            data["supersedes"], relative, "supersedes", errors, "the entry this one corrects"
        )
        if superseded and superseded == run_id:
            errors.append(
                problem(
                    relative,
                    "supersedes",
                    "names this entry.",
                    "name the earlier entry this one corrects, or remove the field",
                )
            )

    check_path_list(data.get("write_scope"), relative, "write_scope", errors, allow_glob=True)
    check_path_list(data.get("paths_read"), relative, "paths_read", errors, allow_glob=False)
    written = check_path_list(data.get("paths_written"), relative, "paths_written", errors, allow_glob=False)

    if data.get("reversal") not in (None, ""):
        check_text_value(
            data["reversal"],
            relative,
            "reversal",
            errors,
            "how a human undoes this run without the agent; when nothing was written, say so and name the "
            "reversal the operation would have needed",
        )

    outcome = ""
    if data.get("outcome") not in (None, ""):
        outcome = as_text(data["outcome"]).strip()
        if outcome not in OUTCOMES:
            errors.append(
                problem(
                    relative,
                    "outcome",
                    f"'{outcome}' is not an outcome.",
                    f"use one of: {joined(OUTCOME_ORDER)}",
                )
            )

    if outcome in OUTCOMES_WITHOUT_WRITES and written:
        errors.append(
            problem(
                relative,
                "paths_written",
                f"lists {len(written)} path(s) while `outcome: {outcome}` says the run wrote nothing.",
                f"record `outcome: {'failed' if outcome == 'refused' else 'completed'}` if the run wrote, "
                "or remove paths it did not write; a refused or dry run writes nothing but this entry",
            )
        )
    if outcome in OUTCOMES_REQUIRING_WRITES_TO_EXIST:
        for index, path in enumerate(written):
            if not (root / path).exists():
                errors.append(
                    problem(
                        relative,
                        f"paths_written[{index}]",
                        f"'{path}' does not exist under the root, but `outcome: {outcome}` claims the run wrote it.",
                        "record the path the run actually wrote, or record the outcome that matches "
                        "(`failed`, or `reverted` when the reversal was executed)",
                    )
                )
    if outcome == "refused" and checks and not any(as_text(item.get("result", "")).strip() == "fail" for item in checks):
        errors.append(
            problem(
                relative,
                "preconditions",
                "records no failed check, but `outcome: refused` says the run was stopped.",
                "record the precondition that refused the run, with `result: fail` and what it read",
            )
        )

    if not body.strip():
        errors.append(
            problem(
                relative,
                "body",
                "has no run record.",
                "write, below the front matter, what ran and what a reviewer should check",
            )
        )
    elif not H1_RE.search(body):
        errors.append(
            problem(relative, "body", "has no H1 title.", "start the body with `# ` and a title naming the run")
        )
    return errors


def check_file_name(path: Path, data: dict, relative: str) -> list[str]:
    """The file name carries the run date and run id, so the directory sorts by run."""
    name = Path(path).name
    if name.startswith(SAMPLE_PREFIX):
        return []
    run_date = as_text(data.get("run_date", "")).strip()
    run_id = as_text(data.get("run_id", "")).strip()
    if not ISO_DATE_RE.match(run_date) or not RUN_ID_RE.match(run_id):
        return []
    expected = f"{run_date}-{run_id}.md"
    if name != expected:
        return [
            problem(
                relative,
                "file name",
                f"is '{name}', but the entry records run_date {run_date} and run_id {run_id}.",
                f"name the file `{expected}`",
            )
        ]
    return []


def validate_entry_file(path: Path, root: Path, seen_run_ids: dict | None = None) -> list[str]:
    """Return every violation found in one ledger entry file."""
    path = Path(path)
    root = Path(root)
    relative = display_path(path, root)
    data, body, raw_text, errors = load_entry(path, relative)
    if data is None:
        return errors
    errors.extend(scan_personal_data(raw_text, relative))
    errors.extend(validate_entry(data, body, relative, root, seen_run_ids))
    errors.extend(check_file_name(path, data, relative))
    return errors


# --- Appending --------------------------------------------------------------

def entry_file_name(entry: dict) -> str | None:
    run_date = as_text(entry.get("run_date", "")).strip()
    run_id = as_text(entry.get("run_id", "")).strip()
    if not ISO_DATE_RE.match(run_date) or not RUN_ID_RE.match(run_id):
        return None
    return f"{run_date}-{run_id}.md"


RUN_FILE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-(?P<run_id>[a-z0-9-]+)\.md$")


def recorded_run_id(path: Path) -> str | None:
    """Return the ``run_id`` a ledger file records, or None when unreadable.

    Used for id allocation, which must see every id already in the ledger even
    in a file the naming rule exempts or a file too malformed to validate.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.split("\n")[:60]:
        if line.startswith("run_id:"):
            value = line.split(":", 1)[1].strip().strip("'\"")
            return value or None
    return None


def next_run_id(operation, *, ledger_dir: Path | str | None = None, root: Path | str = DEFAULT_ROOT) -> str:
    """Return the next unused run id for ``operation``, shaped ``<operation>-NNN``.

    The sequence is read from the ``run_id`` recorded inside every entry in the
    ledger, not from file names, so two runs of one operation never collide and
    ``supersedes`` names exactly one entry. Front matter is authoritative
    because a file whose name the run-file pattern does not match can still
    hold a run id: ``SAMPLE_run.md`` is exempt from the naming rule and records
    ``cadence-snapshot-001``, so a name-only scan would hand that same id to the
    first real cadence run and the ledger would then fail its own duplicate
    check. A runner that prefers its own id scheme may set ``run_id`` itself;
    the only rule is that the id is a lowercase slug unique across the ledger.
    """
    name = as_text(operation).strip()
    if not SLUG_RE.match(name):
        raise LedgerError(f"'{name}' is not an operation id. Fix: pass a lowercase slug such as `cadence-snapshot`")
    directory = Path(ledger_dir) if ledger_dir is not None else Path(root).joinpath(*DEFAULT_LEDGER_DIR)
    highest = 0
    if directory.is_dir():
        for path in sorted(directory.glob("*.md")):
            recorded = recorded_run_id(path)
            candidates = [recorded] if recorded else []
            match = RUN_FILE_RE.match(path.name)
            if match:
                candidates.append(match.group("run_id"))
            for run_id in candidates:
                if not run_id.startswith(f"{name}-"):
                    continue
                tail = run_id[len(name) + 1:]
                if tail.isdigit():
                    highest = max(highest, int(tail))
    return f"{name}-{highest + 1:03d}"


def bullet_list(values, empty: str) -> str:
    items = [as_text(value).strip() for value in values or []]
    items = [item for item in items if item]
    if not items:
        return empty
    return "\n".join(f"- `{item}`" for item in items)


def default_body(entry: dict) -> str:
    """Render the body a runner writes when it supplies no prose of its own."""
    operation = as_text(entry.get("operation", "unknown-operation")).strip()
    run_id = as_text(entry.get("run_id", "unknown-run")).strip()
    promotion = entry.get("promotion")
    if isinstance(promotion, dict):
        promotion_line = (
            f"{as_text(promotion.get('level', '')).strip()} signed by "
            f"{as_text(promotion.get('signed_by', '')).strip()} on "
            f"{as_text(promotion.get('signed_on', '')).strip()}, review point "
            f"{as_text(promotion.get('review_point', '')).strip() or '(not recorded)'}"
        ).strip()
    else:
        promotion_line = "none"
    lines = [
        f"# {operation} run {run_id}",
        "",
        f"- Outcome: {as_text(entry.get('outcome', '')).strip()}",
        f"- Claimed level: {as_text(entry.get('claimed_level', '')).strip()}",
        f"- Trigger: {as_text(entry.get('trigger', '')).strip()}",
        f"- Actor: {as_text(entry.get('actor', '')).strip()}",
        f"- Kill switch at run time: {as_text(entry.get('kill_switch', '')).strip()}",
        f"- Promotion observed: {promotion_line}",
        "",
        "## Preconditions checked",
        "",
    ]
    checks = entry.get("preconditions") or []
    if isinstance(checks, (list, tuple)) and checks:
        for item in checks:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"- `{as_text(item.get('check', '')).strip()}`: "
                f"{as_text(item.get('result', '')).strip()} - {as_text(item.get('detail', '')).strip()}"
            )
    else:
        lines.append("None recorded.")
    lines += [
        "",
        "## Paths read",
        "",
        bullet_list(entry.get("paths_read"), "None recorded."),
        "",
        "## Paths written",
        "",
        bullet_list(entry.get("paths_written"), "None recorded."),
        "",
        "## Reversal",
        "",
        as_text(entry.get("reversal", "")).strip(),
        "",
        "## What this entry is not",
        "",
        "This entry records what happened. It is not a permission, an approval, or evidence that the run",
        "was allowed. The ledger is append-only: a correction is a new entry naming this one in",
        "`supersedes`, never an edit to this file.",
        "",
    ]
    return "\n".join(lines)


def render_entry(entry: dict, body: str | None = None) -> str:
    """Render the markdown text of one entry: front matter in canonical order, then the body."""
    ordered: dict = {}
    for name in FIELD_ORDER:
        if name in entry:
            ordered[name] = entry[name]
    for name in entry:
        if name not in ordered:
            ordered[name] = entry[name]
    front_matter = yaml.safe_dump(ordered, sort_keys=False, default_flow_style=False, allow_unicode=True)
    text = default_body(entry) if body is None else body
    if not text.startswith("\n"):
        text = "\n" + text
    if not text.endswith("\n"):
        text = text + "\n"
    return f"---\n{front_matter}---{text}"


def append_entry(
    entry: dict,
    *,
    ledger_dir: Path | str | None = None,
    root: Path | str = DEFAULT_ROOT,
    body: str | None = None,
) -> Path:
    """Write one entry and return its path.

    ``entry`` is the front matter as a mapping; ``body`` is the prose below it,
    defaulting to a rendering of the fields. The entry is validated before
    anything is written, and an existing file is never overwritten: the ledger is
    append-only, so a correction is a new entry naming the earlier one in
    ``supersedes``.

    Raises ``LedgerError`` when the entry is invalid, when the target already
    exists, or when the root is not a directory. Nothing is written in any of
    those cases.
    """
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise LedgerError(f"--root is not a directory: {root}")
    if not isinstance(entry, dict):
        raise LedgerError("an entry must be a mapping of ledger fields, not " + type(entry).__name__)
    data = dict(entry)
    directory = Path(ledger_dir) if ledger_dir is not None else root_path.joinpath(*DEFAULT_LEDGER_DIR)
    name = entry_file_name(data)
    target = directory / (name or "<unnamed entry>.md")
    relative = display_path(target, root_path) if name else "<new entry>"
    text = default_body(data) if body is None else body
    violations = validate_entry(data, text, relative, root_path, None)
    if violations:
        raise LedgerError(
            f"the entry is not a valid ledger entry, so nothing was written to {relative}",
            violations,
        )
    if target.exists():
        raise LedgerError(
            f"{relative} already exists, and the ledger is append-only. "
            "Fix: write a new entry with a new run_id and `supersedes` naming this one; never edit or "
            "overwrite a recorded run."
        )
    directory.mkdir(parents=True, exist_ok=True)
    target.write_text(render_entry(data, text), encoding="utf-8")
    return target


# --- CLI --------------------------------------------------------------------

def collect_entries(paths, root: Path) -> list[Path]:
    """Expand CLI paths into entry files; directories skip `README.md`."""
    found: list[Path] = []
    for raw in paths:
        candidate = Path(raw)
        if not candidate.exists():
            raise UsageError(f"no such path: {raw}")
        if candidate.is_dir():
            for markdown in sorted(candidate.rglob("*.md")):
                if markdown.name == "README.md":
                    continue
                found.append(markdown)
        else:
            found.append(candidate)
    return found


def run_validate(paths, root: Path) -> int:
    entries = collect_entries(paths, root)
    seen_run_ids: dict[str, str] = {}
    errors: list[str] = []
    for entry in entries:
        errors.extend(validate_entry_file(entry, root, seen_run_ids))
    for error in errors:
        print(error, file=sys.stderr)
    if not entries:
        print(
            "Checked 0 ledger entries. An empty ledger is the expected state while no operation is "
            "promoted to act unattended."
        )
        return 0
    print(f"Checked {len(entries)} ledger entry(s): {len(errors)} violation(s).")
    if catalog_operation_ids(root) is None:
        print(f"Note: {CATALOG_REF} was not readable, so operation ids were not checked against the catalog.")
    print(
        "A valid entry is a complete record, not a permission. Whether the run was allowed is judged "
        "from the promotion record and by a human."
    )
    return 1 if errors else 0


def load_structured_input(raw: str) -> dict:
    if raw == "-":
        text = sys.stdin.read()
        source = "standard input"
    else:
        path = Path(raw)
        if not path.is_file():
            raise UsageError(f"no such entry file: {raw}")
        text = path.read_text(encoding="utf-8")
        source = raw
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise UsageError(f"{source} is not valid JSON or YAML: {str(exc).splitlines()[0]}")
    if not isinstance(data, dict):
        raise UsageError(f"{source} is not a mapping of ledger fields")
    return data


def run_append(args, root: Path) -> int:
    data = load_structured_input(args.entry)
    body = None
    if args.body_file:
        body_path = Path(args.body_file)
        if not body_path.is_file():
            raise UsageError(f"no such body file: {args.body_file}")
        body = body_path.read_text(encoding="utf-8")
    try:
        written = append_entry(data, ledger_dir=args.ledger_dir, root=root, body=body)
    except LedgerError as exc:
        print(exc.report(), file=sys.stderr)
        return 1
    print(display_path(written, root))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    validate_parser = sub.add_parser("validate", help="check ledger entries against the action ledger schema")
    validate_parser.add_argument("paths", nargs="+", help="entry files or directories to check")
    validate_parser.add_argument(
        "--root", default=str(DEFAULT_ROOT), help="repository root written paths resolve against"
    )

    append_parser = sub.add_parser("append", help="write one entry from structured input")
    append_parser.add_argument(
        "--entry", required=True, help="JSON or YAML file holding the entry front matter, or `-` for standard input"
    )
    append_parser.add_argument("--body-file", help="markdown body to write below the front matter")
    append_parser.add_argument("--ledger-dir", help="directory the entry is written to (default: <root>/ops/ledger)")
    append_parser.add_argument(
        "--root", default=str(DEFAULT_ROOT), help="repository root written paths resolve against"
    )

    args = parser.parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f"usage error: --root is not a directory: {args.root}", file=sys.stderr)
        return 2
    try:
        if args.command == "validate":
            return run_validate(args.paths, root)
        return run_append(args, root)
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
