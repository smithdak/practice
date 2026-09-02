---
ledger_schema_version: 1
run_id: cadence-snapshot-001
run_date: 2026-09-02
operation: cadence-snapshot
actor: scheduled-workflow
claimed_level: A3
trigger: schedule
kill_switch: engaged
promotion: none
preconditions:
  - check: operation-in-catalog
    result: pass
    detail: "cadence-snapshot is listed in the operation catalog with a write scope and a reversal."
  - check: operation-not-permanently-ineligible
    result: pass
    detail: "cadence-snapshot is absent from the permanently ineligible list in the autonomy ladder."
  - check: promotion-signed
    result: fail
    detail: "The promotion record lists no promotion for cadence-snapshot, so no human has signed a bound for it."
  - check: kill-switch-released
    result: fail
    detail: "The promotion record reads kill_switch: engaged, which refuses every operation regardless of promotion."
command:
  - python3
  - scripts/cadence.py
  - --root
  - .
source_commit: a1b2c3d
write_scope:
  - ops/status/*.md
paths_read:
  - ops/autonomy/operations.yaml
  - ops/autonomy/promotions.yaml
paths_written: []
reversal: "Nothing was written, so there is nothing to undo. Had the run proceeded, the reversal is to delete the file it wrote under ops/status/, or to close the pull request that carried it without merging."
outcome: refused
---

# Hypothetical ledger entry: a refused cadence-snapshot run

**This entry is a hypothetical example.** No unattended run has happened in this
repository. Nothing is promoted to act unattended, the kill switch is engaged,
and the commit id `a1b2c3d` is a placeholder in the same sense as the
hypothetical hash in the
[sample triage record](../triage/SAMPLE_triage_record.md). The entry exists so a
reviewer can read a complete record before one is ever produced, and so
`scripts/ledger.py` has a committed entry to check itself against.

It deliberately depicts a **refused** run. An entry depicting a completed
unattended run would misrepresent the state of this repository, where no
promotion has been signed.

## What this entry records

```text
Operation: cadence-snapshot, claimed at A3, started by the schedule
Preconditions: 2 passed, 2 failed (promotion-signed, kill-switch-released)
Read: the operation catalog and the promotion record
Wrote: nothing
Outcome: refused
Reversal: none needed; the reversal that would have applied is recorded anyway
```

## Why it looks the way it does

- **The refusal names the precondition that failed.** Two checks failed and both
  are recorded with what they read. An entry whose outcome is `refused` and
  whose preconditions all pass is rejected by the checker, because a refusal
  nobody can trace is not a record.
- **The claimed level is what the run asked for, not what it was granted.**
  `claimed_level: A3` with `promotion: none` is the honest record of a run that
  wanted to act unattended and was stopped. The ledger records the claim; the
  [autonomy ladder](../../docs/framework/AUTONOMY_LADDER.md) and the promotion
  record decide whether the claim was ever legitimate.
- **The state of both governance records is captured at run time.** A reviewer
  reading this entry in a year does not have to reconstruct what
  `promotions.yaml` said on the day; the entry says.
- **`paths_written` is empty, and the outcome agrees with it.** The checker
  rejects a `refused` or `dry-run` entry that lists a written path, so the inert
  case cannot be recorded as anything else.
- **The reversal is recorded even though nothing was written.** The field is
  never blank and never a placeholder. Recording it here also proves the
  operation had a reversal before it was attempted.
- **The precondition ids are the guard's, not the ledger's.** The ledger checks
  that each id is a slug, that each result is `pass` or `fail`, and that each
  carries a detail line. Which checks exist is the guard's business.

## What a completed entry would add

A run that actually acted would carry `outcome: completed`, every path it
created or changed in `paths_written`, and a `promotion` mapping naming the
level, the role that signed it, the date, and the review point. Every path in
`paths_written` would have to exist under the repository root for the entry to
validate. The reversal would then be the operative instruction: the thing a
human executes without the agent to put the repository back.

## What this entry does not mean

It does not mean the run was permitted. A valid entry is a complete record, not
an authorization; nothing in this file makes an operation eligible to run
unattended, and no ledger entry ever will. It is also final: correcting it means
writing a new entry that names `cadence-snapshot-001` in `supersedes`, never
editing this file. See the [action ledger schema](../../docs/schemas/ACTION_LEDGER_SCHEMA.md)
and the [directory README](README.md).
