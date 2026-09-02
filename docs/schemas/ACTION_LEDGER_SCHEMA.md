# Action Ledger Schema

## Outcome

If an operation ever runs without a person, the only way anyone learns what it
did is the record it writes itself. There was no such record and no shape for
one. That makes an unattended run unauditable and, after the fact, unreversible:
nobody can answer what it read, what it changed, whether it stayed inside the
bound a human recorded, or how to put the repository back.

This schema makes that record a file with a checkable contract. One entry
records one run of one operation: what triggered it, the promotion record and
kill-switch state it observed, the preconditions it checked and their results,
the paths it read, every path it wrote, the reversal a human can execute without
the agent, and how the run ended. Entries live in
[`ops/ledger/`](../../ops/ledger/README.md) and are read and written by
[`scripts/ledger.py`](../../scripts/ledger.py).

The ledger is the record side of the substrate described by the
[autonomy ladder](../framework/AUTONOMY_LADDER.md). The ladder's A3 section says
what must be recorded when an unattended run happens: the action taken, the
bound it ran inside, the reversal available or performed, the human who owns the
bound, and the review point. This schema is that sentence turned into fields.
Nothing in this repository is at A3, so the expected state of the ledger today
is empty except for the committed sample.

## An entry is a record, never an authorization

Read this before anything else in the schema.

- **A valid entry does not mean the run was permitted.** The checker verifies
  that the record is complete and internally consistent. It does not verify that
  a promotion existed, that the kill switch was released, that the actor was
  entitled to act, or that the operation should ever run unattended. An entry
  recording a run that should never have happened is a *valid entry* and a
  serious finding; the record is how the finding becomes visible.
- **The ledger grants nothing.** Eligibility comes from a signed promotion
  record and the ladder, and the decision behind it is a human's. Writing an
  entry claiming a level does not confer that level.
- **The ledger is append-only.** An entry is never edited and never deleted. A
  correction is a new entry that names the earlier one in `supersedes`; both
  files stay. `scripts/ledger.py append` refuses to overwrite an existing entry
  for this reason.
- **The record may contradict the bound.** An entry whose `paths_written` falls
  outside its own `write_scope`, or whose `claimed_level` is A3 while
  `kill_switch` reads `engaged`, still validates. Judging a recorded run against
  the ladder's demotion triggers is the demotion check's job and a human's, not
  this validator's. A validator that rejected such an entry would make the worst
  case the one the ledger could not record.

## Where entries live and how they are named

One entry is one markdown file with YAML front matter at:

```text
ops/ledger/<YYYY-MM-DD>-<run_id>.md
```

The date is the entry's `run_date` and the slug is its `run_id`, so the
directory sorts by run and a file name names exactly one run. A file whose base
name starts with `SAMPLE_` is exempt from the name rule and is checked like any
other entry; that is how
[`ops/ledger/SAMPLE_run.md`](../../ops/ledger/SAMPLE_run.md) can be a worked
example and a validated entry at once. Directory arguments expand to every
`*.md` file below them except `README.md`.

## Canonical front matter

Field names and controlled values are case-sensitive. No other field is
accepted, so a run cannot quietly add a field that carries something the schema
never reviewed.

| Field | Required | Rule |
|---|---|---|
| `ledger_schema_version` | Yes | The integer `1`. A new required field, a new controlled value, or a new file-name shape is version 2, not a silent change. |
| `run_id` | Yes | Lowercase slug of 4 to 80 characters matching `^[a-z0-9]+(-[a-z0-9]+)*$`, unique across the ledger. `next_run_id()` produces `<operation>-NNN`, for example `cadence-snapshot-001`. |
| `run_date` | Yes | ISO date in `YYYY-MM-DD` form: the date the run happened, and the date in the file name. |
| `operation` | Yes | The operation id the run executed. When `ops/autonomy/operations.yaml` exists and lists ids, the value must appear in it; when it is absent or unreadable the check is skipped with an informational message rather than a failure. |
| `actor` | Yes | Lowercase slug naming the identity that ran the operation, for example `scheduled-workflow` or an agent id from the registry. A role or automation label, never a personal name, handle, address, or contact route. |
| `claimed_level` | Yes | One of `A0`, `A1`, `A2`, `A3` — the level the run claimed, not the level it was granted. The registry and packet values `observe`, `draft`, and `recommend` are not level ids and are rejected here. |
| `trigger` | Yes | What started the run: `schedule` or `manual`. |
| `kill_switch` | Yes | The kill-switch state read from the promotion record at run time: `engaged` or `released`. |
| `promotion` | Yes | The promotion the run observed, as a mapping, or the literal `none` when it found no promotion for this operation. See [Promotion observed](#promotion-observed). |
| `preconditions` | Yes | Non-empty list of checks the run made before acting, each with its result. See [Preconditions](#preconditions). |
| `command` | No | The operation's command as an argv list, for example `["python3", "scripts/cadence.py", "--root", "."]`. For a refused or dry run this is the command that was not executed. |
| `source_commit` | No | 7 to 40 lowercase hexadecimal characters naming the commit the run read. Record it whenever the run can name one; a run nobody can reproduce is worth less to an auditor. |
| `write_scope` | Yes | The write bound recorded for the operation at run time, as repository-relative patterns such as `ops/status/*.md`. Copied into the entry so a reviewer reading it later does not have to reconstruct what the catalog said that day. `[]` means the operation may write nothing. |
| `paths_read` | Yes | Every repository-relative path the run read. `[]` when it read none. Existence is not checked: a later commit may remove a file a past run read, and the entry is a historical record, not a live index. |
| `paths_written` | Yes | Every repository-relative path the run created or changed. `[]` when it wrote none. Concrete paths, never patterns. |
| `reversal` | Yes | How a human undoes this run without the agent, in at least 8 characters and never a placeholder. When nothing was written, say so and name the reversal the operation would have needed. |
| `outcome` | Yes | How the run ended: `refused`, `dry-run`, `completed`, `failed`, or `reverted`. |
| `supersedes` | No | The `run_id` of the earlier entry this one corrects. Never this entry's own id. |

### Promotion observed

`promotion: none` records that the run found no promotion for the operation.
That is the expected value today. Otherwise the field is a mapping copied from
the promotion record the run read:

| Key | Required | Rule |
|---|---|---|
| `level` | Yes | The level the promotion grants: `A0`, `A1`, `A2`, or `A3`. |
| `signed_by` | Yes | The role that signed it, as a slug from the operating role vocabulary. A role, never a person. |
| `signed_on` | Yes | ISO date the promotion was signed. |
| `review_point` | No | ISO date the bound is renewed or withdrawn. Record it whenever the promotion names one: the ladder demotes on an action taken after the review point passed without a renewal record, and that is checkable only from the entry. |

### Preconditions

`preconditions` is a non-empty list. Each item is a mapping:

| Key | Required | Rule |
|---|---|---|
| `check` | Yes | Lowercase slug naming the precondition, recorded as the guard reports it. |
| `result` | Yes | `pass` or `fail`. |
| `detail` | Yes | What the check read and what it found, in at least 8 characters and never a placeholder. |

The ledger does not fix which checks exist; that vocabulary belongs to
`scripts/autonomy_guard.py`. It fixes that every check the run made is named,
that each carries a result, and that each says what it read. A check id may
appear only once per entry.

An entry with no preconditions is rejected. A run that checked nothing before
acting has no record that it stayed in bounds, and an empty list would let the
most dangerous run produce the cheapest entry.

### Outcomes

| Outcome | Meaning | What the checker requires |
|---|---|---|
| `refused` | A precondition failed and the operation never ran. | `paths_written` is empty, and at least one precondition records `result: fail`. |
| `dry-run` | The operation was simulated and wrote nothing. | `paths_written` is empty. |
| `completed` | The operation ran and finished. | Every path in `paths_written` exists under `--root`. |
| `failed` | The operation ran and errored. | Written paths are recorded but not required to exist; a partial write may already have been cleaned up. |
| `reverted` | The reversal was executed. | Written paths are recorded and not required to exist, because the reversal may have removed them. |

## Consistency rules a validator can enforce

`python3 scripts/ledger.py validate <path...> [--root .]` takes entry files or
directories and exits 0 when every entry is valid, 1 on any violation, and 2 on
a usage error such as a path that does not exist. Every violation names the
file, the field, the problem, and the fix. It checks:

1. Front matter parses as YAML and is a mapping; every required field is present
   and no unknown field appears; `ledger_schema_version` is `1`.
2. `run_id` matches the slug pattern and is unique across the invocation;
   `run_date` is a real ISO date; `source_commit`, when present, is hexadecimal.
3. `claimed_level` is one of `A0`, `A1`, `A2`, `A3`. A level outside the ladder's
   vocabulary is rejected, including the packet values.
4. `trigger`, `kill_switch`, `outcome`, and every precondition `result` are in
   their controlled vocabularies.
5. `operation` and `actor` are slugs, and `operation` appears in the operation
   catalog when the catalog can be read.
6. `promotion` is `none` or a mapping carrying `level`, `signed_by`, and
   `signed_on`, with dates that parse.
7. `preconditions` is non-empty, each item names a `check`, a `result`, and a
   `detail` that is not a placeholder, and no check id repeats.
8. `reversal` is present, at least 8 characters, and not a placeholder such as
   `n/a` or a dash. **An entry that omits its reversal fails.**
9. `write_scope`, `paths_read`, and `paths_written` are lists of
   repository-relative paths: no absolute path, no `..`, no backslash. Patterns
   are allowed in `write_scope` only.
10. An entry whose outcome is `refused` or `dry-run` lists no written path, and
    a `refused` entry names at least one failed precondition.
11. An entry whose outcome is `completed` lists only written paths that exist
    under `--root`.
12. The file name is `<run_date>-<run_id>.md`, unless the base name starts with
    `SAMPLE_`.
13. The body is non-empty and carries an H1 title.
14. No line of the file carries an email address, a handle, or a phone number.

What it does not check is as important. It does not check that a promotion
existed, that the actor was entitled to run, that the written paths match the
write scope, that the level claimed was granted, or that the run should have
happened. Those are the demotion check's questions and a human's.

## Writing an entry from a runner

A runner records a run by calling this module rather than reproducing the
format. `scripts/run_unattended.py` sits beside it in `scripts/`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger import LedgerError, append_entry, next_run_id

entry = {
    "ledger_schema_version": 1,
    "run_id": next_run_id("cadence-snapshot", root=root),
    "run_date": "2026-09-02",
    "operation": "cadence-snapshot",
    "actor": "scheduled-workflow",
    "claimed_level": "A3",
    "trigger": "schedule",
    "kill_switch": "engaged",
    "promotion": "none",
    "preconditions": [
        {"check": "promotion-signed", "result": "fail",
         "detail": "No promotion is recorded for cadence-snapshot."},
    ],
    "command": ["python3", "scripts/cadence.py", "--root", "."],
    "write_scope": ["ops/status/*.md"],
    "paths_read": ["ops/autonomy/promotions.yaml"],
    "paths_written": [],
    "reversal": "Nothing was written, so there is nothing to undo.",
    "outcome": "refused",
}

try:
    written = append_entry(entry, root=root)          # -> Path of the new entry
except LedgerError as error:
    print(error.report(), file=sys.stderr)            # message plus each violation
    raise SystemExit(1)
```

The interface:

| Name | Signature | Behavior |
|---|---|---|
| `append_entry` | `append_entry(entry, *, ledger_dir=None, root=DEFAULT_ROOT, body=None) -> Path` | Validates the entry, then writes `<ledger_dir>/<run_date>-<run_id>.md` and returns the path. `ledger_dir` defaults to `<root>/ops/ledger` and is created if missing. Raises `LedgerError` and writes nothing when the entry is invalid, when the target exists, or when `root` is not a directory. |
| `next_run_id` | `next_run_id(operation, *, ledger_dir=None, root=DEFAULT_ROOT) -> str` | Reads the entry file names already in the ledger and returns the next unused `<operation>-NNN`. A runner may set its own `run_id` instead; the only rule is that it is a unique lowercase slug. |
| `render_entry` | `render_entry(entry, body=None) -> str` | The markdown text of an entry: front matter in canonical field order, then the body. Useful for a dry run that wants to show the entry it would append without writing it. |
| `default_body` | `default_body(entry) -> str` | The body `append_entry` writes when `body` is `None`: the outcome, the level, the trigger, the preconditions, the paths, the reversal, and the statement that an entry is not an authorization. |
| `validate_entry_file` | `validate_entry_file(path, root, seen_run_ids=None) -> list[str]` | Every violation in one entry file, as actionable strings. Empty means valid. |
| `LedgerError` | exception | Carries `.violations`, the list of violation strings, and `.report()`, the message plus one line per violation. |

`append_entry` validates before it writes, so a runner cannot leave a malformed
entry behind, and it refuses to overwrite, so a rerun with a reused id fails
loudly instead of erasing the first run's record.

The same thing from a shell, for a workflow that would rather not import
Python:

```bash
python3 scripts/ledger.py append --entry run.json --root .
python3 scripts/ledger.py append --entry - --root . < run.json
python3 scripts/ledger.py append --entry run.json --body-file body.md --root .
```

`--entry` takes a JSON or YAML file, or `-` for standard input. On success the
command prints the path it wrote and exits 0; on an invalid entry it prints the
violations and exits 1; on a usage error it exits 2.

## Worked examples

Both are hypothetical. No unattended run has happened in this repository.

A refused run, which is what the substrate produces today, is committed in full
at [`ops/ledger/SAMPLE_run.md`](../../ops/ledger/SAMPLE_run.md).

A dry run, which is the most an operator can produce today without signing
anything:

```yaml
---
ledger_schema_version: 1
run_id: cadence-snapshot-002
run_date: 2026-09-02
operation: cadence-snapshot
actor: maintainer-on-duty
claimed_level: A1
trigger: manual
kill_switch: engaged
promotion: none
preconditions:
  - check: dry-run-requested
    result: pass
    detail: "The operator passed --dry-run, so the operation is simulated and writes nothing."
  - check: promotion-signed
    result: fail
    detail: "No promotion is recorded for cadence-snapshot; the run may not act, and did not."
command: ["python3", "scripts/cadence.py", "--root", "."]
write_scope: ["ops/status/*.md"]
paths_read: ["ops/cadence.yaml"]
paths_written: []
reversal: "Nothing was written, so there is nothing to undo."
outcome: dry-run
---
```

A completed run, shown only to make the field rules concrete. Producing one
requires a signed promotion and a released kill switch, neither of which exists:

```yaml
---
ledger_schema_version: 1
run_id: cadence-snapshot-003
run_date: 2026-09-02
operation: cadence-snapshot
actor: scheduled-workflow
claimed_level: A3
trigger: schedule
kill_switch: released
promotion:
  level: A3
  signed_by: founder
  signed_on: 2026-09-02
  review_point: 2026-12-02
preconditions:
  - check: promotion-signed
    result: pass
    detail: "A promotion for cadence-snapshot at A3 is recorded, signed by the founder."
  - check: kill-switch-released
    result: pass
    detail: "The promotion record reads kill_switch: released."
  - check: write-scope-matches-catalog
    result: pass
    detail: "The promotion write scope equals the catalog write scope for this operation."
command: ["python3", "scripts/cadence.py", "--root", "."]
source_commit: a1b2c3d
write_scope: ["ops/status/*.md"]
paths_read: ["ops/cadence.yaml"]
paths_written: ["ops/status/2026-09-02-cadence.md"]
reversal: "Delete ops/status/2026-09-02-cadence.md, or close the pull request that carries it without merging."
outcome: completed
---
```

## What the ledger gives the demotion check

The ladder demotes on observable triggers, and a demotion needs no decision. An
entry carries what a checker needs to evaluate the A3 triggers without asking
anyone:

| Ladder trigger | Fields it is read from |
|---|---|
| An action taken outside the recorded bound | `paths_written` against `write_scope`, both recorded in the entry; and `paths_read` against a read scope when the operation's record carries one |
| An action taken with no reversal path recorded | `reversal`, which the validator already refuses to leave blank |
| An action taken after the review point passed without a renewal record | `run_date` against `promotion.review_point` |
| An action on an operation since added to the permanently ineligible list | `operation` against the ladder's ineligible list |
| An action taken with no bound recorded in advance | `promotion` and `kill_switch`, both recorded as the run observed them |

Because those fields are recorded as the run observed them, the check reads the
entry rather than the current state of the governance records, which may have
changed since. Deciding what to do about a fired trigger stays with a human; the
demotion itself is automatic.

## Related documents

- [`ops/ledger/README.md`](../../ops/ledger/README.md) — the directory, retention, and why an empty ledger is the expected state.
- [`docs/framework/AUTONOMY_LADDER.md`](../framework/AUTONOMY_LADDER.md) — the levels, the evidence that raises one, the triggers that lower one, and the operations that may never run unattended.
- [`docs/schemas/AGENT_PACKET_SCHEMA.md`](AGENT_PACKET_SCHEMA.md) — the sibling record for attended runs. A packet is what an agent hands a human; a ledger entry is what a run leaves behind. A run that produced a packet records the packet path in `paths_written`.
- [`ops/triage/README.md`](../../ops/triage/README.md) — the other checked operating record in this repository, and the model this schema follows.
- [`tests/test_ledger.py`](../../tests/test_ledger.py) — the executable statement of every rule above.

## Sources

As of: 2026-09-02.

- [docs/framework/AUTONOMY_LADDER.md](../framework/AUTONOMY_LADDER.md) — A3's "recorded when it runs" clause and the demotion triggers this schema makes checkable.
- [docs/schemas/AGENT_PACKET_SCHEMA.md](AGENT_PACKET_SCHEMA.md) — the front-matter conventions, the role vocabulary, and the forbidden-assertion boundary reused here.
- [ops/OPERATING_LOOP.md](../../ops/OPERATING_LOOP.md) — what runs without a person and what does not.
- [docs/DECISIONS.md](../DECISIONS.md) and [docs/NON_GOALS.md](../NON_GOALS.md) — the locked decisions behind the operations no entry may ever record.
