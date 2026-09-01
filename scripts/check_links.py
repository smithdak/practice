#!/usr/bin/env python3
"""Deterministic offline checker for markdown links and as-of dates.

Scans every ``*.md`` file under a repository root (skipping ``.git/``,
``.worktrees/`` and ``__pycache__/``), resolves each link target and reports:

- broken relative links (exit 1),
- relative links that resolve outside the repository root (exit 1),
- broken repo-absolute targets such as ``/docs/x.md`` (exit 1),
- as-of dates older than 90 days (warning only, never affects the exit code).

External targets (``http://``, ``https://``, ``mailto:``, ``buzz://`` and any
other ``scheme://``) and fragment-only targets (``#anchor``) are skipped.
Code fences and inline code spans are masked before scanning so documented
examples are not mistaken for links.

Exit codes: 0 = no broken links, 1 = at least one broken link,
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
ISO_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

SKIPPED = "skipped"
ESCAPED = "escaped"


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
    """Yield ``(line_number, iso_date)`` for each ``As of:`` date in prose."""
    for match in AS_OF_RE.finditer(masked):
        line_end = masked.find("\n", match.end())
        if line_end == -1:
            line_end = len(masked)
        window = masked[match.end(): min(line_end, match.end() + AS_OF_WINDOW_CHARS)]
        date_match = ISO_DATE_RE.search(window)
        if date_match:
            yield masked.count("\n", 0, match.start()) + 1, date_match.group(1)


def check_repository(root: Path, as_of: date | None = None) -> tuple[list[str], list[str], dict[str, int]]:
    """Return ``(errors, warnings, stats)`` with ``path:line: message`` strings."""
    root = Path(root).resolve()
    if as_of is None:
        as_of = date.today()
    errors: list[str] = []
    warnings: list[str] = []
    stats = {"files": 0, "links": 0}
    for path in find_markdown_files(root):
        relative = path.relative_to(root).as_posix()
        masked = mask_code(path.read_text(encoding="utf-8", errors="replace"))
        stats["files"] += 1
        for line_no, kind, target in extract_targets(masked):
            stats["links"] += 1
            status, resolved, target_kind = resolve_target(target, path, root)
            if status == SKIPPED:
                continue
            if status == ESCAPED:
                errors.append(f"{relative}:{line_no}: link escapes repository: {target.strip()}")
                continue
            if not resolved.exists():
                if target_kind == "absolute":
                    errors.append(f"{relative}:{line_no}: broken repo-absolute link: {target.strip()}")
                else:
                    errors.append(f"{relative}:{line_no}: broken relative link: {target.strip()}")
        for line_no, iso_date in extract_as_of_dates(masked):
            parsed = date.fromisoformat(iso_date)
            age_days = (as_of - parsed).days
            if age_days > STALE_LIMIT_DAYS:
                warnings.append(
                    f"{relative}:{line_no}: stale as-of date {iso_date} "
                    f"({age_days} days old, limit {STALE_LIMIT_DAYS})"
                )
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
    args = parser.parse_args(argv)
    errors, warnings, stats = check_repository(Path(args.root), as_of=args.as_of)
    for warning in warnings:
        print(warning)
    for error in errors:
        print(error, file=sys.stderr)
    print(
        f"Checked {stats['files']} markdown file(s), {stats['links']} link target(s): "
        f"{len(errors)} broken link(s), {len(warnings)} stale as-of date(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
