# Release briefs

**As of:** 2026-09-02

This directory holds generated release briefs: the evidence assembly step of
[Practice 005, "Write release notes from committed evidence"](../../practices/005-release-notes.md),
and the source material the [Release Editor](../../buzz/agents/RELEASE_EDITOR.md)
profile requires before it may draft anything.

A brief answers four questions from the repository itself, over one commit
range: what shipped, what is proposed but not tested, what is explicitly not
measured, and which human approvals are still outstanding. Every line in a
brief carries a repository path or a commit hash. Anything that cannot be
backed by one of those is left out.

## A brief is a draft until a named human maintainer approves it

A file in this directory is never an announcement, a release, or an approval.
It is a draft. Publication requires that a named human maintainer:

1. opens each pointer in the brief and confirms the entry says no more than
   the record shows;
2. amends, approves, or holds the brief;
3. records the approval with a name, a date, and the exact version approved,
   as the [Practice](../../practices/005-release-notes.md) "Method" step 5
   requires.

The generator cannot perform any of those three steps and does not claim to.
It also never changes an artifact's `maturity` or `evidence_quality` field and
never records an owner gate or operating hold as cleared; the live status of
every gate and hold is in the [owner review packet](../OWNER_REVIEW.md).

## Produce a brief

```bash
python3 scripts/release_brief.py \
  --since <first-commit-in-range> \
  --until <last-commit-in-range> \
  --as-of YYYY-MM-DD \
  --root . \
  --out release/briefs/YYYY-MM-DD-<label>.md
```

- `--since` is **inclusive** — it names the first commit of the range, not
  git's exclusive `A..B` baseline.
- `--until` defaults to `HEAD`. Pin it to a commit when the brief is meant to
  be reproducible later.
- `--as-of` is required and is written into the brief's `As of` line. It
  records when the brief was assembled, not when the work merged.
- `--out` is optional; without it the brief goes to standard output, which is
  the fastest way to preview one.

The generator reads file contents with `git show` at the range head rather
than from the working tree, so a rerun over the same range produces identical
bytes even if the checkout has uncommitted edits.

Outside a git checkout, on an unknown revision, or when `--since` is not an
ancestor of `--until`, the command prints one actionable message and exits 1
without writing an output file.

## Naming

`YYYY-MM-DD-<label>.md`, where the date is the `--as-of` value and the label
names the range a human would recognize — for example
[`2026-09-02-phase-2.md`](2026-09-02-phase-2.md), which covers the Phase 2
commit range.

## Do not hand-edit a generated brief

If a brief is wrong, the generator is wrong. Fix `scripts/release_brief.py`,
add the case to `tests/test_release_brief.py`, and regenerate. A hand-edited
brief no longer proves that its pointers came from committed evidence, which
is the only reason to trust it.

Editorial judgment belongs downstream: a maintainer decides which entries an
announcement uses, for which audience, and in what wording, working from the
brief and its pointers rather than by rewriting the brief in place.
