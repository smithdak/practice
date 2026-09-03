#!/usr/bin/env python3
"""Deterministic offline checker for markdown links and as-of dates.

Scans every ``*.md`` file under a repository root (skipping ``.git/``,
``.worktrees/`` and ``__pycache__/``), resolves each link target, reads each
``As of:`` line, and reports:

- broken relative links (exit 1),
- relative links that resolve outside the repository root (exit 1),
- broken repo-absolute targets such as ``/docs/x.md`` (exit 1),
- ``As of:`` lines whose date-shaped text is not a calendar date, such as
  ``2026-02-30`` (exit 1, reported with file and line like a broken link),
- as-of dates older than 90 days (a warning: printed to standard output and
  never part of the exit code unless ``--fail-on-stale`` is passed).

Every run ends with the coverage the as-of rule reached, whether or not
anything is stale: how many markdown files were scanned, how many carry a
dated ``As of:`` line the rule can read, how many dated lines were read, and
how many files mention "as of" in a form the rule cannot date. The rule sees a
date only where one regular expression matches, so a clean result is a
statement about the files it could read and about nothing else; the coverage
lines exist so that a clean result cannot be read as "the repository is
current". The counts are printed once as a labelled sentence for a person and
once as a single ``check_links_summary:`` line of ``key=value`` pairs that a
workflow or a ledger can carry; ``parse_summary_line`` reads that line back.
``scripts/cadence.py`` computes its staleness section through ``scan_as_of``
here, so the two reports cannot disagree.

External targets (``http://``, ``https://``, ``mailto:``, ``buzz://`` and any
other ``scheme://``) and fragment-only targets (``#anchor``) are skipped.
Code fences and inline code spans are masked before scanning so documented
examples are not mistaken for links or dates.

``--fail-on-stale`` is opt-in and off by default; the CI workflow and the
operation catalog pass no flag. It changes the exit code alone: everything
printed is byte-identical with and without it.

Exit codes: 0 = no error, 1 = at least one broken link or malformed as-of
date (or, with ``--fail-on-stale``, at least one stale as-of date),
2 = usage error.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".worktrees", "__pycache__"}
STALE_LIMIT_DAYS = 90
AS_OF_WINDOW_CHARS = 40

INLINE_LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^<>\n]*>|[^)\n]+?)\s*\)")
REFERENCE_DEF_RE = re.compile(r"^ {0,3}\[[^\]\n]+\]:[ \t]*(<[^<>\n]*>|[^<\s\"'][^ \t\n]*)[ \t]*[^\n]*$", re.MULTILINE)
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODE_SPAN_RE = re.compile(r"`+[^`\n]*`+")
EXTERNAL_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*://")
AS_OF_RE = re.compile(r"As\s+of\b[^:\n]{0,3}:", re.IGNORECASE)
# Any prose mention of the phrase, dated or not. A file that matches this but
# yields no readable date is a currency claim the staleness rule cannot see.
AS_OF_MENTION_RE = re.compile(r"\bas\s+of\b", re.IGNORECASE)
ISO_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

SKIPPED = "skipped"
ESCAPED = "escaped"

# The machine-readable summary line: a fixed prefix, then key=value pairs in
# this order. Every key is an integer count.
SUMMARY_PREFIX = "check_links_summary:"
SUMMARY_KEYS = (
    "files",
    "dated_files",
    "dated_lines",
    "undatable_files",
    "stale_dates",
    "broken_links",
    "malformed_dates",
    "links",
    "limit_days",
)


def find_markdown_files(root: Path) -> list[Path]:
    files = [
        path
        for path in root.rglob("*.md")
        if not any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts)
    ]
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def mask_code(text: str) -> str:
    """Blank fenced blocks and inline code spans, preserving offsets and lines."""
    masked_lines: list[str] = []
    fence = ""
    for line in text.split("\n"):
        marker = FENCE_RE.match(line)
        if fence:
            masked_lines.append(" " * len(line))
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = ""
        elif marker:
            fence = marker.group(1)
            masked_lines.append(" " * len(line))
        else:
            masked_lines.append(line)
    return CODE_SPAN_RE.sub(lambda match: " " * len(match.group(0)), "\n".join(masked_lines))


def extract_targets(masked: str):
    """Yield ``(line_number, kind, target)`` for inline links and reference definitions."""
    found: list[tuple[int, str, str]] = []
    for match in INLINE_LINK_RE.finditer(masked):
        found.append((match.start(1), "inline", match.group(1)))
    for match in REFERENCE_DEF_RE.finditer(masked):
        found.append((match.start(1), "reference", match.group(1)))
    found.sort(key=lambda item: item[0])
    for offset, kind, target in found:
        yield masked.count("\n", 0, offset) + 1, kind, target


def resolve_target(target: str, source: Path, root: Path) -> tuple[str, Path | None, str]:
    """Classify a link target.

    Returns ``(status, resolved_path, kind)`` where status is ``"skipped"`` for
    external/fragment targets, ``"escaped"`` when the target leaves the repo
    root, and ``"ok"`` otherwise; kind is ``"absolute"`` or ``"relative"``.
    """
    target = target.strip()
    if len(target) >= 2 and target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    display = target
    target = unquote(target.split("#", 1)[0]).strip()
    if not target or target.startswith("//"):
        return SKIPPED, None, "relative"
    if target.startswith(("http://", "https://", "mailto:", "buzz://")) or EXTERNAL_SCHEME_RE.match(target):
        return SKIPPED, None, "relative"
    if target.startswith("/"):
        kind = "absolute"
        candidate = root / target.lstrip("/")
    else:
        kind = "relative"
        candidate = source.parent / target
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return ESCAPED, None, kind
    return "ok", resolved, kind


def extract_as_of_dates(masked: str):
    """Yield ``(line_number, date_text)`` for each ``As of:`` line carrying date-shaped text.

    The text is whatever ``ISO_DATE_RE`` matched; it is not parsed here, so a
    line such as ``As of: 2026-02-30`` is yielded and left for the caller to
    reject.
    """
    for match in AS_OF_RE.finditer(masked):
        line_end = masked.find("\n", match.end())
        if line_end == -1:
            line_end = len(masked)
        window = masked[match.end(): min(line_end, match.end() + AS_OF_WINDOW_CHARS)]
        date_match = ISO_DATE_RE.search(window)
        if date_match:
            yield masked.count("\n", 0, match.start()) + 1, date_match.group(1)


def scan_as_of(root: Path, as_of: date | None = None, limit_days: int = STALE_LIMIT_DAYS) -> dict:
    """Read every ``As of:`` line under ``root`` once and return coverage plus findings.

    Every markdown file lands in exactly one of three buckets. ``dated_files``
    counts files the rule read at least one calendar date from.
    ``undatable_files`` counts files that mention "as of" in prose but yield no
    readable date: a placeholder, a malformed date, or a phrasing the pattern
    does not match. The remainder make no as-of claim at all. ``dated_lines``
    counts every line a date was read from; ``stale`` lists those older than
    ``limit_days``; ``malformed`` lists lines whose date-shaped text is not a
    calendar date. Both lists are ordered by path, then line.
    """
    root = Path(root).resolve()
    if as_of is None:
        as_of = date.today()
    result: dict = {
        "files": 0,
        "dated_files": 0,
        "dated_lines": 0,
        "undatable_files": 0,
        "limit_days": limit_days,
        "stale": [],
        "malformed": [],
    }
    for path in find_markdown_files(root):
        relative = path.relative_to(root).as_posix()
        masked = mask_code(path.read_text(encoding="utf-8", errors="replace"))
        result["files"] += 1
        read_a_date = False
        for line_no, text in extract_as_of_dates(masked):
            try:
                parsed = date.fromisoformat(text)
            except ValueError:
                result["malformed"].append({"path": relative, "line": line_no, "text": text})
                continue
            read_a_date = True
            result["dated_lines"] += 1
            age_days = (as_of - parsed).days
            if age_days > limit_days:
                result["stale"].append(
                    {"path": relative, "line": line_no, "as_of": text, "age_days": age_days}
                )
        if read_a_date:
            result["dated_files"] += 1
        elif AS_OF_MENTION_RE.search(masked):
            result["undatable_files"] += 1
    return result


def coverage_sentence(counts: dict) -> str:
    """One sentence a person reads: what the as-of rule could and could not see."""
    files = counts["files"]
    dated = counts["dated_files"]
    undatable = counts["undatable_files"]
    unseen = files - dated - undatable
    return (
        f"{dated} of {files} markdown file(s) carry a dated As-of line the rule can read "
        f"({counts['dated_lines']} line(s) read); {undatable} file(s) mention \"as of\" in a "
        f"form the rule cannot date; the rule says nothing about the remaining {unseen}."
    )


def summary_line(stats: dict) -> str:
    """The one machine-readable line: ``check_links_summary: key=value ...``."""
    return SUMMARY_PREFIX + " " + " ".join(f"{key}={int(stats[key])}" for key in SUMMARY_KEYS)


def parse_summary_line(line: str) -> dict[str, int] | None:
    """Return the counts carried by a ``summary_line`` string, or ``None`` if it is not one."""
    line = line.strip()
    if not line.startswith(SUMMARY_PREFIX):
        return None
    counts: dict[str, int] = {}
    for pair in line[len(SUMMARY_PREFIX):].split():
        key, separator, value = pair.partition("=")
        if separator != "=" or key not in SUMMARY_KEYS or not value.isdigit():
            return None
        counts[key] = int(value)
    if set(counts) != set(SUMMARY_KEYS):
        return None
    return counts


def check_repository(root: Path, as_of: date | None = None) -> tuple[list[str], list[str], dict[str, int]]:
    """Return ``(errors, warnings, stats)`` with ``path:line: message`` strings.

    Errors are ordered by file, and within a file link errors precede as-of
    errors. ``stats`` carries every count ``summary_line`` prints.
    """
    root = Path(root).resolve()
    if as_of is None:
        as_of = date.today()
    files = find_markdown_files(root)
    link_errors: dict[str, list[str]] = {}
    links = 0
    for path in files:
        relative = path.relative_to(root).as_posix()
        masked = mask_code(path.read_text(encoding="utf-8", errors="replace"))
        for line_no, kind, target in extract_targets(masked):
            links += 1
            status, resolved, target_kind = resolve_target(target, path, root)
            if status == SKIPPED:
                continue
            if status == ESCAPED:
                link_errors.setdefault(relative, []).append(
                    f"{relative}:{line_no}: link escapes repository: {target.strip()}"
                )
                continue
            if not resolved.exists():
                if target_kind == "absolute":
                    message = f"{relative}:{line_no}: broken repo-absolute link: {target.strip()}"
                else:
                    message = f"{relative}:{line_no}: broken relative link: {target.strip()}"
                link_errors.setdefault(relative, []).append(message)
    scan = scan_as_of(root, as_of=as_of)
    date_errors: dict[str, list[str]] = {}
    for item in scan["malformed"]:
        date_errors.setdefault(item["path"], []).append(
            f"{item['path']}:{item['line']}: malformed as-of date {item['text']} (not a calendar date)"
        )
    errors: list[str] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        errors.extend(link_errors.get(relative, []))
        errors.extend(date_errors.get(relative, []))
    warnings = [
        f"{item['path']}:{item['line']}: stale as-of date {item['as_of']} "
        f"({item['age_days']} days old, limit {scan['limit_days']})"
        for item in scan["stale"]
    ]
    stats = {
        "files": scan["files"],
        "links": links,
        "broken_links": sum(len(found) for found in link_errors.values()),
        "dated_files": scan["dated_files"],
        "dated_lines": scan["dated_lines"],
        "undatable_files": scan["undatable_files"],
        "stale_dates": len(scan["stale"]),
        "malformed_dates": len(scan["malformed"]),
        "limit_days": scan["limit_days"],
    }
    return errors, warnings, stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("root", nargs="?", default=str(DEFAULT_ROOT), help="repository root to scan")
    parser.add_argument(
        "--as-of",
        type=date.fromisoformat,
        default=None,
        help="override today's date as YYYY-MM-DD for reproducible staleness checks",
    )
    parser.add_argument(
        "--fail-on-stale",
        action="store_true",
        help=(
            "exit 1 when any as-of date is stale; the output is identical with or without "
            "this flag (default: a stale date is a warning and the exit code ignores it)"
        ),
    )
    args = parser.parse_args(argv)
    errors, warnings, stats = check_repository(Path(args.root), as_of=args.as_of)
    for warning in warnings:
        print(warning)
    for error in errors:
        print(error, file=sys.stderr)
    print("As-of coverage: " + coverage_sentence(stats))
    checked = (
        f"Checked {stats['files']} markdown file(s), {stats['links']} link target(s): "
        f"{stats['broken_links']} broken link(s), {stats['stale_dates']} stale as-of date(s)"
    )
    if stats["malformed_dates"]:
        checked += f", {stats['malformed_dates']} malformed as-of date(s)"
    print(checked + ".")
    print(summary_line(stats))
    if errors:
        return 1
    if args.fail_on_stale and stats["stale_dates"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
