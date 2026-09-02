# Action ledger

> **Why this directory is empty.** No operation is promoted, so no scheduled run
> has occurred. A refusal from a scheduled run would appear here, because a
> refusal is evidence and an unrecorded refusal is indistinguishable from a run
> that never happened. A refusal produced by a person verifying the substrate by
> hand belongs in a temporary directory instead: pass `--ledger-dir` so a manual
> check does not leave a scheduled run's record behind.

An action ledger entry is what a run leaves behind. One file records one run of
one operation: what triggered it, the promotion record and kill-switch state it
observed, the preconditions it checked, what it read, every path it wrote, the
reversal a human can execute without the agent, and how it ended. The shape is
fixed by the [action ledger schema](../../docs/schemas/ACTION_LEDGER_SCHEMA.md)
and checked by [`scripts/ledger.py`](../../scripts/ledger.py).

Before this directory existed, an operation that ran without a person left no
trace anyone could audit. Nobody could answer what it read, what it changed,
whether it stayed inside a recorded bound, or how to undo it. Those five
questions are the fields.

## This directory is expected to be empty

No operation in this repository is promoted to run unattended. The
[autonomy ladder](../../docs/framework/AUTONOMY_LADDER.md) defines A3,
act-unattended-within-bounds, and places nothing there; the promotion record
ships with an engaged kill switch and no signed promotion. So the substrate is
inert, and an empty ledger is the correct state, not a gap in the evidence.

The only committed entry is [`SAMPLE_run.md`](SAMPLE_run.md), a hypothetical
worked example that depicts a **refused** run. It exists so a reviewer can read a
complete record before one is ever produced, and so the checker has a committed
entry to check itself against. `python3 scripts/ledger.py validate ops/ledger`
on an otherwise empty directory exits 0 and says so.

If entries start appearing here, two records changed: a human signed a promotion
and the kill switch was released. Both are visible in Git history, and both are
the first thing to read before reading the entries.

## Naming

```text
ops/ledger/<YYYY-MM-DD>-<run_id>.md      for example 2026-09-02-cadence-snapshot-001.md
```

The date is the entry's `run_date` and the slug is its `run_id`, so the
directory sorts by run and one file name names one run. A file whose base name
starts with `SAMPLE_` is exempt from the name rule and is checked like any other
entry. `README.md` is not an entry and is skipped.

## Commands

```bash
# Check one entry, a list of entries, or this whole directory.
python3 scripts/ledger.py validate ops/ledger/SAMPLE_run.md --root .
python3 scripts/ledger.py validate ops/ledger --root .

# Append one entry from structured input; prints the path it wrote.
python3 scripts/ledger.py append --entry run.json --root .
```

`--root` is the repository root that written paths resolve against; it defaults
to the repository containing the script. Exit codes: `0` when every entry
validates, `1` on any violation, `2` on a usage error such as a path that does
not exist. Each violation names the file, the field, the problem, and the fix.

A runner records a run by calling `append_entry` from `scripts/ledger.py` rather
than writing the format by hand. The schema documents that interface.

## Append-only

An entry is never edited and never deleted.

- **A correction is a new entry.** Write a new run id, name the earlier entry in
  `supersedes`, and say in the body what the earlier record got wrong. Both
  files stay. A reader who finds the superseded entry can follow it forward; a
  reader of an edited file cannot know what it used to say.
- **`append` refuses to overwrite.** Reusing a run id for a second run fails
  loudly rather than erasing the first run's record.
- **Deleting an entry is not a correction.** An entry recording a run that
  should never have happened is the most valuable file in this directory. It is
  the evidence a demotion is built on. Removing it removes the finding, not the
  event.

The one exception is the ordinary Git one: a commit that adds an entry can be
reverted before it merges, because the entry has not yet been published. After
it merges, correct it forward.

## Retention

Every entry is kept for the life of the repository. Nothing here is pruned on a
schedule, for three reasons:

1. The demotion check reads run history, so a pruned entry is a trigger nobody
   can evaluate.
2. Entries are small and rare. An operation that runs weekly produces about
   fifty files a year, all of them plain text.
3. Entries carry no personal data. `actor` is a role or automation label, and
   the checker rejects a file carrying an email address, a handle, or a phone
   number, so nothing here creates an obligation to delete.

If the directory ever grows past what a reviewer can scan, the fix is a schema
change that defines an archive layout, recorded as version 2 with a migration —
not a cleanup pass over the records.

## What this tooling does and does not do

`scripts/ledger.py` reads, writes, and checks records. **It never runs an
operation, grants a permission, or approves anything.** A valid entry means the
record is complete and internally consistent. It does not mean the run was
permitted, that a promotion existed, or that the kill switch was released; an
entry recording a run that should never have happened is a valid entry and a
serious finding.

The checker is offline and deterministic. It makes no network call. It checks
the shape and internal consistency of an entry and the existence of written
paths under `--root` when the entry claims the run completed. It cannot tell you
whether the run should have happened, whether the recorded reversal actually
works, or whether the paths listed are the only ones touched — only that the
record says what was done and points at something a reviewer can open.

Judging a recorded run against the ladder's demotion triggers is a separate
step, and deciding what follows from a fired trigger stays with a human.

## How this fits the operating loop

The ledger is the record side of the substrate described in
[running Practice on the loop](../OPERATING_LOOP.md). It is the sibling of
[the triage records](../triage/README.md): both are checked markdown records of
something an agent did or proposed, and both stop at a human decision. The
difference is that a triage record proposes a route and a ledger entry reports a
completed fact, which is why the ledger's rules are about completeness and the
triage record's are about evidence.

## Sources

As of: 2026-09-02.

- [docs/schemas/ACTION_LEDGER_SCHEMA.md](../../docs/schemas/ACTION_LEDGER_SCHEMA.md) — the fields, the controlled values, and every rule the checker enforces.
- [docs/framework/AUTONOMY_LADDER.md](../../docs/framework/AUTONOMY_LADDER.md) — A3, what must be recorded when a run happens, and the triggers that demote it.
- [ops/OPERATING_LOOP.md](../OPERATING_LOOP.md) — what runs without a person and what does not.
- [docs/DECISIONS.md](../../docs/DECISIONS.md) and [docs/NON_GOALS.md](../../docs/NON_GOALS.md) — the locked decisions behind the operations no run may perform.
- [tests/test_ledger.py](../../tests/test_ledger.py) — the executable statement of the rules.
