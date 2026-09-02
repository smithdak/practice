#!/usr/bin/env python3
"""Assemble a draft release brief from committed evidence in a git range.

The brief follows the method in ``practices/005-release-notes.md``: collect the
committed evidence first, write one entry per change, give every entry a
pointer, and leave the result explicitly in draft state until a named human
maintainer approves it.

What the generator does:

- lists every commit in ``--since``..``--until`` (``--since`` included), with
  the paths each commit changed that still exist at the range head;
- matches ``handoffs/<id>.md`` for a commit whose subject names a task in
  ``task(<id>)`` form and quotes that handoff's ``## Status`` value;
- reports front-matter ``maturity`` and ``evidence_quality`` values verbatim
  for the files the range touched;
- lists the rows of ``release/OWNER_REVIEW.md`` whose status cell records OPEN.

What it never does: guess a pointer, soften an unbacked claim into prose,
assert a maturity change, assert that an owner gate or operating hold is
cleared, or emit an unfinished or bracketed publication token into ``release/``.
Anything it cannot back with a repository path or a commit hash is omitted.

Reads are done with ``git show <rev>:<path>``, never from the working tree, so
two runs over the same range produce identical bytes regardless of local edits.

Exit codes: 0 = brief produced, 1 = the range or the repository could not be
read (no output file is written), 2 = usage error.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

RECORD_SEP = "\x1e"
FIELD_SEP = "\x1f"
CHUNK = 100

OWNER_REVIEW_PATH = "release/OWNER_REVIEW.md"
TASK_SUBJECT_RE = re.compile(r"^\w+\(([^)]*)\)\s*:")
HANDOFF_STATUS_RE = re.compile(r"^## Status\s*\n+\s*(COMPLETE|BLOCKED)\s*$", re.MULTILINE)
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
FRONT_MATTER_FIELD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*?)\s*$")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
ISO_DATE_RE = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")
NOT_MEASURED_RE = re.compile(r"not\s+measured", re.IGNORECASE)

# Mirrors the release rules enforced by scripts/validate.py, which stays the
# authority. Applied to the generated text before anything is written so a
# brief can never introduce a token that release validation would reject.
UNFINISHED_RE = re.compile(r"\b(TODO|TBD|LOREM IPSUM)\b", re.IGNORECASE)
PUBLICATION_TOKEN_RE = re.compile(r"\[[@#]?[A-Z][A-Z0-9_ -]*\](?!\()")
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

TESTED_MATURITIES = {"tested"}


class BriefError(Exception):
    """A condition that stops the brief before any output is written."""


@dataclass(frozen=True)
class Commit:
    sha: str
    short: str
    authored: str
    subject: str
    raw_paths: tuple[str, ...]
    live_paths: tuple[str, ...]

    @property
    def removed_path_count(self) -> int:
        return len(self.raw_paths) - len(self.live_paths)


@dataclass(frozen=True)
class Approval:
    section: str
    name: str
    status: str


# --------------------------------------------------------------------------
# git access
# --------------------------------------------------------------------------


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", "-c", "core.quotePath=false", "-C", str(root), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:  # pragma: no cover - environment specific
        raise BriefError("git executable not found on PATH; a git checkout is required") from exc


def git_out(root: Path, args: list[str], failure: str) -> str:
    result = run_git(root, args)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        suffix = f": {detail[0]}" if detail else ""
        raise BriefError(f"{failure}{suffix}")
    return result.stdout


def ensure_checkout(root: Path) -> Path:
    """Return the checkout's top level so every path is repository-relative."""
    if not root.is_dir():
        raise BriefError(f"--root is not a directory: {root}")
    result = run_git(root, ["rev-parse", "--show-toplevel"])
    toplevel = result.stdout.strip()
    if result.returncode != 0 or not toplevel:
        raise BriefError(
            f"{root} is not inside a git checkout; the brief is assembled from commits, "
            "so run it against a checkout of this repository"
        )
    return Path(toplevel)


def resolve_commit(root: Path, rev: str) -> str:
    result = run_git(root, ["rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"])
    sha = result.stdout.strip()
    if result.returncode != 0 or not sha:
        raise BriefError(
            f"unknown revision: {rev}; pass a commit that exists in this checkout "
            "(check it with `git log --oneline`)"
        )
    return sha


def commit_range(root: Path, since: str, until: str, since_rev: str, until_rev: str) -> list[str]:
    ancestry = run_git(root, ["merge-base", "--is-ancestor", since, until])
    if ancestry.returncode != 0:
        raise BriefError(
            f"{since_rev} is not an ancestor of {until_rev}; --since must name the first commit "
            "of the range and --until a commit that descends from it"
        )
    listed = git_out(
        root,
        ["rev-list", "--reverse", f"{since}..{until}"],
        f"could not list commits between {since_rev} and {until_rev}",
    )
    return [since] + [line.strip() for line in listed.splitlines() if line.strip()]


def collect_commits(root: Path, shas: list[str], live_paths: set[str]) -> list[Commit]:
    commits: list[Commit] = []
    fmt = f"--format={RECORD_SEP}%H{FIELD_SEP}%h{FIELD_SEP}%aI{FIELD_SEP}%s"
    for start in range(0, len(shas), CHUNK):
        batch = shas[start : start + CHUNK]
        out = git_out(
            root,
            ["log", "--no-walk=unsorted", fmt, "--name-only", *batch],
            "could not read commit details",
        )
        by_sha = {}
        for record in out.split(RECORD_SEP):
            if not record.strip():
                continue
            head, _, body = record.partition("\n")
            fields = head.split(FIELD_SEP)
            if len(fields) != 4:
                raise BriefError("could not parse `git log` output for the range")
            sha, short, authored, subject = fields
            raw = tuple(sorted({line.strip() for line in body.splitlines() if line.strip()}))
            by_sha[sha] = Commit(
                sha=sha,
                short=short,
                authored=authored[:10],
                subject=subject,
                raw_paths=raw,
                live_paths=tuple(p for p in raw if p in live_paths),
            )
        for sha in batch:
            if sha not in by_sha:
                raise BriefError(f"could not read commit {sha[:7]} in the range")
            commits.append(by_sha[sha])
    return commits


def tree_paths(root: Path, rev: str, rev_label: str) -> set[str]:
    out = git_out(
        root,
        ["ls-tree", "-r", "--full-name", "--name-only", rev],
        f"could not list the files present at {rev_label}",
    )
    return {line.strip() for line in out.splitlines() if line.strip()}


def read_blob(root: Path, rev: str, path: str) -> str | None:
    result = run_git(root, ["show", f"{rev}:{path}"])
    if result.returncode != 0:
        return None
    return result.stdout


# --------------------------------------------------------------------------
# evidence extraction
# --------------------------------------------------------------------------


def front_matter(text: str) -> dict[str, str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if line.startswith((" ", "\t", "#")):
            continue
        field = FRONT_MATTER_FIELD_RE.match(line)
        if field:
            fields[field.group(1)] = field.group(2).strip().strip('"').strip("'")
    return fields


def task_ids(subject: str) -> list[str]:
    match = TASK_SUBJECT_RE.match(subject)
    if not match or not subject.startswith("task("):
        return []
    ids = [part.strip() for part in match.group(1).split(",")]
    return [i for i in ids if i and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", i)]


def handoff_status(text: str) -> str | None:
    match = HANDOFF_STATUS_RE.search(text)
    return match.group(1) if match else None


def clean_cell(cell: str) -> str:
    text = MARKDOWN_LINK_RE.sub(r"\1", cell)
    text = text.replace("**", "").replace("`", "").replace("[", "").replace("]", "")
    return " ".join(text.split())


def outstanding_approvals(text: str) -> list[Approval]:
    approvals: list[Approval] = []
    section = "unnamed section"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            section = clean_cell(stripped.lstrip("#").strip())
            continue
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        name, status = clean_cell(cells[0]), clean_cell(cells[-1])
        if not name or name.lower() in {"gate", "hold", "item", "decision"}:
            continue
        if "OPEN" not in status.upper():
            continue
        approvals.append(Approval(section=section, name=name, status=status))
    return approvals


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------


def code(value: str) -> str:
    """Render a value as an inline code span, which never carries a claim."""
    return "`" + value.replace("`", "'") + "`"


def visible_prose(text: str) -> str:
    return INLINE_CODE_RE.sub("", FENCED_CODE_RE.sub("", text))


def check_release_tokens(text: str) -> None:
    prose = visible_prose(text)
    unfinished = UNFINISHED_RE.search(prose)
    if unfinished:
        raise BriefError(
            f"refusing to write a brief containing the unfinished token {unfinished.group(0)!r} "
            "in visible prose; release validation rejects it"
        )
    token = PUBLICATION_TOKEN_RE.search(prose)
    if token:
        raise BriefError(
            f"refusing to write a brief containing the publication token {token.group(0)!r} "
            "in visible prose; release validation rejects it"
        )


def render_shipped(commits: list[Commit], handoffs: dict[str, list[tuple[str, str | None, bool]]], until_short: str) -> list[str]:
    verb = "commit is" if len(commits) == 1 else "commits are"
    lines = [
        "## What shipped",
        "",
        f"{len(commits)} {verb} present in this repository's history in the stated range. "
        "Presence in history is evidence that the work merged. It is not evidence of a release, "
        "an outcome, an adoption, or a measurement.",
        "",
    ]
    for index, commit in enumerate(commits, start=1):
        lines.append(f"### {index}. {code(commit.short)} — {code(commit.subject)}")
        lines.append("")
        lines.append(f"- Commit {code(commit.sha)}, author date {code(commit.authored)}.")
        for name, status, present in handoffs[commit.sha]:
            path = code(f"handoffs/{name}.md")
            if not present:
                lines.append(
                    f"- Handoff {path} is not present at {code(until_short)}; no handoff status is claimed."
                )
            elif status is None:
                lines.append(
                    f"- Handoff {path} is present; its `## Status` value could not be read, "
                    "so no status is claimed."
                )
            else:
                lines.append(f"- Handoff {path} records `## Status` {code(status)}.")
        if not handoffs[commit.sha]:
            lines.append(
                f"- The subject of {code(commit.short)} names no task in `task(<id>)` form, "
                "so no handoff is matched."
            )
        if commit.live_paths:
            lines.append(
                f"- Paths changed by {code(commit.short)} and still present at {code(until_short)}:"
            )
            for path in commit.live_paths:
                lines.append(f"  - {code(path)}")
            if commit.removed_path_count:
                plural = "path" if commit.removed_path_count == 1 else "paths"
                lines.append(
                    f"- {code(commit.short)} also changed {commit.removed_path_count} {plural} "
                    f"absent at {code(until_short)}, left out here; the commit hash remains the "
                    "only pointer that resolves."
                )
        elif commit.raw_paths:
            lines.append(
                f"- Every path {code(commit.short)} changed is absent at {code(until_short)}; "
                "the commit hash is the only pointer that resolves."
            )
        else:
            lines.append(
                f"- No file list is recorded for {code(commit.short)} against its first parent "
                "(a merge commit records none here); the commit hash is the pointer."
            )
        lines.append("")
    return lines


def render_proposed(
    maturity_rows: list[tuple[str, str, str, str]],
    lab_rows: list[tuple[str, str]],
    until_short: str,
) -> list[str]:
    lines = [
        "## What is proposed but not tested",
        "",
        f"Read from the front matter of the files this range touched, as those files stand at "
        f"{code(until_short)}. Values are quoted from the file. This brief does not change a "
        "`maturity` or an `evidence_quality` field and records no promotion decision.",
        "",
    ]
    if maturity_rows:
        for path, maturity, evidence, sha in maturity_rows:
            evidence_note = f", {code('evidence_quality: ' + evidence)}" if evidence else ""
            lines.append(
                f"- {code(path)} — front matter records {code('maturity: ' + maturity)}"
                f"{evidence_note} (touched by {code(sha)})."
            )
    else:
        lines.append(
            "- No file this range touched records a `maturity` field other than `tested`."
        )
    lines.append("")
    lines.append("Recorded trials in this range:")
    lines.append("")
    if lab_rows:
        for path, sha in lab_rows:
            lines.append(
                f"- {code(path)} — a recorded trial run (touched by {code(sha)}). "
                "Recording a trial does not change the maturity of the method it exercises."
            )
    else:
        lines.append("- No Lab file was touched in this range.")
    lines.append("")
    return lines


def render_not_measured(
    evidence_rows: list[tuple[str, str, str]],
    phrase_rows: list[tuple[str, int, str]],
    until_short: str,
) -> list[str]:
    lines = [
        "## What is explicitly not measured",
        "",
        "This brief reports no measured outcome for any item above. The pointers below are the "
        "places in the range that record the absence of measurement themselves.",
        "",
    ]
    if evidence_rows:
        for path, evidence, sha in evidence_rows:
            lines.append(
                f"- {code(path)} — front matter records {code('evidence_quality: ' + evidence)} "
                f"(touched by {code(sha)})."
            )
    else:
        lines.append("- No file this range touched records an `evidence_quality` field.")
    lines.append("")
    lines.append(
        f"Files this range touched whose text at {code(until_short)} contains the phrase "
        "\"not measured\" (case-insensitive), with the number of matching lines:"
    )
    lines.append("")
    if phrase_rows:
        for path, count, sha in phrase_rows:
            plural = "line" if count == 1 else "lines"
            lines.append(f"- {code(path)} — {count} matching {plural} (touched by {code(sha)}).")
    else:
        lines.append("- No touched file contains that phrase.")
    lines.append("")
    return lines


def render_approvals(
    approvals: list[Approval], owner_review_present: bool, until_short: str
) -> list[str]:
    lines = ["## Human approvals still outstanding", ""]
    if not owner_review_present:
        lines.append(
            f"{code(OWNER_REVIEW_PATH)} is not present at {code(until_short)}, so this brief cannot "
            "say which human approvals are outstanding. What is outstanding is unknown here and "
            "must be read from wherever the owner review packet lives."
        )
        lines.append("")
        return lines
    lines.append(
        f"Read from {code(OWNER_REVIEW_PATH)} at {code(until_short)}. Only rows whose status cell "
        "records OPEN are listed. This brief does not clear an owner gate or an operating hold and "
        "does not assert that any has been cleared; the absence of a row from this list is not "
        "approval of it."
    )
    lines.append("")
    if not approvals:
        lines.append(
            f"- No row in {code(OWNER_REVIEW_PATH)} records an OPEN status at {code(until_short)}. "
            "Read the file itself before treating that as approval of anything."
        )
        lines.append("")
        return lines
    current = None
    for approval in approvals:
        if approval.section != current:
            if current is not None:
                lines.append("")
            current = approval.section
            lines.append(f"**{current}**")
            lines.append("")
        lines.append(f"- {approval.name} — status recorded as {code(approval.status)}.")
    lines.append("")
    return lines


def build_brief(
    root: Path,
    since_rev: str,
    until_rev: str,
    as_of: str,
) -> str:
    root = ensure_checkout(root)
    since = resolve_commit(root, since_rev)
    until = resolve_commit(root, until_rev)
    shas = commit_range(root, since, until, since_rev, until_rev)
    live = tree_paths(root, until, until_rev)
    commits = collect_commits(root, shas, live)
    until_short = commits[-1].short if commits[-1].sha == until else until[:7]
    since_short = commits[0].short
    commit_word = "commit" if len(commits) == 1 else "commits"

    handoffs: dict[str, list[tuple[str, str | None, bool]]] = {}
    for commit in commits:
        entries: list[tuple[str, str | None, bool]] = []
        for task_id in task_ids(commit.subject):
            rel = f"handoffs/{task_id}.md"
            if rel not in live:
                entries.append((task_id, None, False))
                continue
            text = read_blob(root, until, rel)
            entries.append((task_id, handoff_status(text or ""), True))
        handoffs[commit.sha] = entries

    first_touch: dict[str, str] = {}
    for commit in commits:
        for path in commit.live_paths:
            first_touch.setdefault(path, commit.short)

    maturity_rows: list[tuple[str, str, str, str]] = []
    lab_rows: list[tuple[str, str]] = []
    evidence_rows: list[tuple[str, str, str]] = []
    phrase_rows: list[tuple[str, int, str]] = []
    for path in sorted(first_touch):
        if not path.endswith(".md"):
            continue
        text = read_blob(root, until, path)
        if text is None:
            continue
        short = first_touch[path]
        fields = front_matter(text)
        maturity = fields.get("maturity", "")
        evidence = fields.get("evidence_quality", "")
        if maturity and maturity not in TESTED_MATURITIES:
            maturity_rows.append((path, maturity, evidence, short))
        if fields.get("artifact_type") == "lab":
            lab_rows.append((path, short))
        if evidence:
            evidence_rows.append((path, evidence, short))
        matches = sum(1 for line in text.splitlines() if NOT_MEASURED_RE.search(line))
        if matches:
            phrase_rows.append((path, matches, short))

    lines: list[str] = [
        f"# Release brief — {as_of} (draft)",
        "",
        "- **Status:** DRAFT — HUMAN REVIEW REQUIRED",
        f"- **As of:** {as_of}",
        f"- **Range:** {code(since_short)} through {code(until_short)}, {len(commits)} "
        f"{commit_word}, {code(since_short)} included",
        f"- **Range boundaries:** since {code(since)}, until {code(until)}",
        f"- **Generated by:** {code('scripts/release_brief.py')} from committed evidence in this repository",
        "",
        "No human maintainer has approved this brief. A named human maintainer approves a brief "
        "before any part of it is published; until then it is a draft and nothing in it is an "
        "announcement. This brief records what is in the repository's history. It does not change "
        "any artifact's `maturity` or `evidence_quality` field, does not clear an owner gate or an "
        "operating hold, and does not claim a measured outcome.",
        "",
        "## How this brief was assembled",
        "",
        "- One entry per commit in the range, oldest first. Every line carries a repository path or "
        "a commit hash.",
        f"- Paths are the files each commit changed that still exist at {code(until_short)}. A path "
        "removed before the range head is left out rather than pointed at.",
        "- A handoff is matched when the commit subject names a task in `task(<id>)` form and the "
        "matching file exists under `handoffs/`; its `## Status` value is quoted, not interpreted.",
        f"- File contents are read with `git show` at {code(until_short)}, not from a working tree, "
        "so a rerun over the same range produces the same brief.",
        "- Anything that cannot be backed by a repository path or a commit hash is omitted. It is "
        "never guessed and never softened into prose.",
        "",
    ]
    lines += render_shipped(commits, handoffs, until_short)
    lines += render_proposed(maturity_rows, lab_rows, until_short)
    lines += render_not_measured(evidence_rows, phrase_rows, until_short)
    owner_review_text = read_blob(root, until, OWNER_REVIEW_PATH) if OWNER_REVIEW_PATH in live else None
    lines += render_approvals(
        outstanding_approvals(owner_review_text or ""),
        owner_review_text is not None,
        until_short,
    )
    lines += [
        "## Before any of this is published",
        "",
        "1. A named human maintainer opens each pointer above and confirms the entry says no more "
        "than the record shows, per the verification step in `practices/005-release-notes.md`.",
        "2. The maintainer amends, approves, or holds the brief, and records the approval with a "
        "name, a date, and the exact version approved.",
        "3. Publication follows that recorded approval. A generated file is never the approval.",
        "",
    ]

    text = "\n".join(lines).rstrip("\n") + "\n"
    check_release_tokens(text)
    return text


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Assemble a draft release brief from committed evidence in a git range.",
    )
    parser.add_argument(
        "--since",
        required=True,
        metavar="REV",
        help="first commit included in the brief (inclusive, unlike git's A..B).",
    )
    parser.add_argument(
        "--until",
        default="HEAD",
        metavar="REV",
        help="last commit included in the brief (default: HEAD).",
    )
    parser.add_argument(
        "--root",
        default=str(DEFAULT_ROOT),
        metavar="PATH",
        help="repository checkout to read (default: this repository).",
    )
    parser.add_argument(
        "--out",
        metavar="PATH",
        help="write the brief to this path (default: standard output).",
    )
    parser.add_argument(
        "--as-of",
        required=True,
        metavar="YYYY-MM-DD",
        help="the date the brief was assembled; written into its As of line.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if not ISO_DATE_RE.match(args.as_of):
            raise BriefError(f"--as-of must be an ISO date such as 2026-09-02, got: {args.as_of}")
        try:
            date.fromisoformat(args.as_of)
        except ValueError as exc:
            raise BriefError(f"--as-of is not a real date: {args.as_of} ({exc})") from exc
        text = build_brief(Path(args.root).resolve(), args.since, args.until, args.as_of)
    except BriefError as exc:
        print(f"release_brief: {exc}", file=sys.stderr)
        return 1
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"Wrote draft brief to {out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
