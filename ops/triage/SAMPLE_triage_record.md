---
record_id: TR-2026-001
subject_ref: "issue #4212"
state: needs-info
category: bug
owner_role: reporter
last_actor: agent
updated: 2026-09-02
evidence:
  verification_attempt: "Ran the link checker against a fixture containing one relative link and one missing target; it reported a handled broken-link error and exited 1. No traceback occurred."
  commit_checked: "a1b2c3d"
  inspected_paths:
    - scripts/check_links.py
    - tests/test_check_links.py
  observed_vs_expected: "Observed a handled broken-link message and exit code 1; the report claims an unhandled traceback on a relative link."
  missing_information: "The report does not state the Python version, the command that was run, or a relative link that produces the traceback."
  specific_ask: "Supply the Python version, the exact command, and one relative link that produced the traceback."
  check_point: 2026-09-09
history:
  - from: new
    to: needs-info
    actor: agent
    role: bounded-agent
    date: 2026-09-02
---

# Hypothetical triage record TR-2026-001

**This record is a hypothetical example.** There is no issue #4212, no real
reporter, no real message, and no real triage run behind it. The commit id
`a1b2c3d` is a placeholder in the same sense as the hypothetical hash in the
[issue triage practice](../../practices/004-issue-triage.md#worked-hypothetical-example).
It exists so a triager can see a complete record and so `scripts/triage.py` has
a committed record to check itself against.

## Routing record

```text
State: new -> needs-info
Category: bug (unverified)
Evidence: ran the link checker against a fixture with one relative link and one
  missing target; observed a handled broken-link message and exit code 1, not
  the reported traceback
Ask: reporter to supply the Python version, the exact command, and one relative
  link that produced the traceback
Next owner: reporter
Next check: 2026-09-09
```

## Why this record looks the way it does

- **A bounded agent moved it.** `last_actor: agent` with `role: bounded-agent`
  is legal here: `needs-info` asks the reporter a question, it removes nothing,
  and it decides nothing. The same actor may not move a record into `wontfix`,
  which is reserved to a human maintainer.
- **The evidence is what was actually run.** The verification line records the
  fixture that was checked and the result observed. Nothing that did not happen
  is recorded, and no version, environment, or error message the report did not
  contain is filled in.
- **The pointers resolve.** `inspected_paths` names files that exist in this
  repository, so a reviewer can open exactly what the triager read.
- **The ask is specific and dated.** `specific_ask` names the three things that
  would change the route, and `check_point` stops the record from parking in
  `needs-info` forever.
- **No person appears.** The reporter is a role label. The record carries no
  name, handle, contact route, or message text; those belong to the private
  intake record, not to Git.

## What happens next

Run `python3 scripts/triage.py next ops/triage/SAMPLE_triage_record.md` to see
the legal moves from `needs-info` and the evidence each one needs. If the
reporter answers and the crash reproduces, the record moves to
`ready-for-agent` only when the fix touches no permissions, security,
licensing, data, or conduct scope; otherwise it moves to `ready-for-human` with
the specific decision the maintainer must make. Closing it is a human
maintainer's decision, recorded with a written reason.
