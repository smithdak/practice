# Triage records

- Policy and labels: [.github/TRIAGE_POLICY.md](../../.github/TRIAGE_POLICY.md)
- The method: [practices/004-issue-triage.md](../../practices/004-issue-triage.md)
- This directory: the records, one markdown file with YAML front matter per issue, checked by [`scripts/triage.py`](../../scripts/triage.py)

A triage record is where one reported issue sits in the state machine the
method defines and the policy maps onto GitHub labels. The checker verifies
that a record carries the evidence its state requires and that no agent has
moved an issue into a state a human owns.

## What this tooling does and does not do

`scripts/triage.py` reads and checks records. **It never performs a moderation
action.** It does not label an issue, close or reopen one, remove content,
restrict a person, change access, or accept work. Those remain human decisions
under [docs/DECISIONS.md](../../docs/DECISIONS.md) and the
[moderation model](../../community/MODERATION.md), and autonomous moderation is
a [non-goal](../../docs/NON_GOALS.md).

The checker is offline and deterministic. It makes no network call and reads no
issue tracker. It checks the shape and internal consistency of a record and the
existence of the repository paths a record points at. It cannot tell you whether
a claim is true, whether a commit id names a real commit, or whether a
verification actually happened — only that the record says what was done and
points at something a reviewer can open.

## Commands

```bash
# Check one record, a list of records, or a directory of them.
python3 scripts/triage.py validate ops/triage/SAMPLE_triage_record.md --root .
python3 scripts/triage.py validate ops/triage --root .

# Print the legal next states and the evidence each one requires.
python3 scripts/triage.py next ops/triage/SAMPLE_triage_record.md
```

`--root` is the repository root that evidence paths resolve against; it
defaults to the repository containing the script. Directory arguments expand to
every `*.md` file below them except `README.md`.

Exit codes: `0` when every record validates, `1` on any violation, `2` on a
usage error such as a path that does not exist. Each violation names the file,
the field, the problem, and the fix.

## Record format

One file per issue. Name it after the record id, for example `TR-2026-001.md`.
[`SAMPLE_triage_record.md`](SAMPLE_triage_record.md) is a complete worked
example, explicitly labeled hypothetical.

```yaml
---
record_id: TR-2026-001
subject_ref: "issue #4212"
state: needs-info
category: bug
owner_role: reporter
last_actor: agent
updated: 2026-09-02
evidence:
  verification_attempt: "Ran the checker against a fixture; observed a handled error, not a traceback."
  inspected_paths:
    - scripts/check_links.py
  missing_information: "The report does not state the version or the command."
  specific_ask: "Supply the version, the command, and one failing input."
  check_point: 2026-09-09
history:
  - from: new
    to: needs-info
    actor: agent
    role: bounded-agent
    date: 2026-09-02
---
```

Below the front matter, write the routing record a reporter can read: state
moved from and to, category, evidence, the specific ask, and the next owner or
check point. The body is required.

| Field | Required | Contents |
| --- | --- | --- |
| `record_id` | Always | A non-identifying id shaped `PREFIX-YYYY-NNN`, for example `TR-2026-001`. Never a name or a handle. |
| `subject_ref` | Always | The public item, written exactly as `issue #N` or `pull-request #N`. Never a title, a link to a message, or a person. |
| `state` | Always | One state from the vocabulary below. |
| `category` | Always | One category from the vocabulary below. |
| `owner_role` | Every state except `new` | The role that owns the next move. A role label, never a personal name. |
| `last_actor` | Always | `human` or `agent` — who made the most recent move. |
| `updated` | Always | ISO date of the most recent move. Never earlier than the last transition. |
| `evidence` | Every state except `new` | The evidence fields that state requires. A record in `new` carries none. |
| `history` | Optional | Ordered transitions, oldest first. When present it must start at `new`, chain, end at the current `state`, and its last actor must match `last_actor`. |

No other field is accepted. Fields that would carry a person, an identity, or
message content — a name, handle, email, contact route, transcript, quotation,
or screenshot — are rejected by name, and the checker also scans the whole file
for email addresses, handles, phone numbers, and credentials. Those details
belong in the access-controlled private record described in the
[intake and consent template](../../templates/INTAKE_CONSENT.md), not in Git.
The rule is section 3 of the [redaction checklist](../../templates/REDACTION_CHECKLIST.md).

## States

| State | Meaning | Source |
| --- | --- | --- |
| `new` | Arrived, not yet routed. Categorize and verify before it moves. | Entry state of the transition table in the [triage policy](../../.github/TRIAGE_POLICY.md). |
| `needs-info` | Waiting on detail the report does not contain. | Practice decision rules. |
| `ready-for-agent` | A reproduced bug, bounded, safe for agent-assisted work under human review. Not an acceptance. | Practice decision rules. |
| `ready-for-human` | Verified, but the next decision needs maintainer judgment: priority, breaking change, permissions, security, licensing, or cross-area impact. Also the only state a private-routing category may sit in. | Practice decision rules. |
| `wontfix` | Closed. A human maintainer decided it, with a written reason. | Practice decision rules; closure is human-owned. |

## Categories

| Category | Route |
| --- | --- |
| `bug` | The artifact behaves in a way its maintainer would not intend. The only category that may reach `ready-for-agent`. |
| `enhancement` | A requested new capability or change. Routes to `ready-for-human` or `needs-info`, never to `ready-for-agent`. |
| `safety`, `privacy`, `access`, `conduct`, `legal` | Private-routing categories. Public triage stops. The record keeps only the minimum fact needed to route it, sits in `ready-for-human`, is owned by the private intake owner or a human moderator, and is never actored by an agent. |

The private-routing set is the union of the categories that stop triage in
[practice 004](../../practices/004-issue-triage.md) step 1 (conduct, safety,
access, legal) and the concerns [BETA_OPS](../BETA_OPS.md) sends straight to the
private intake owner (safety, privacy, access, conduct). Reports in this set go
to the private route in the [Code of Conduct](../../CODE_OF_CONDUCT.md); the
record in Git is a routing pointer, not a case file.

## Who may move a record between which states

| Transition | Who may apply it |
| --- | --- |
| `new` to `needs-info`, `ready-for-agent`, or `ready-for-human` | Human triager, or a bounded agent recording a recommendation. |
| `needs-info` to `ready-for-agent` or `ready-for-human` | Human triager, or a bounded agent recording a recommendation. |
| `ready-for-agent` or `ready-for-human` to another open state | Human triager, or a bounded agent recording a recommendation, on new information. |
| Any state to `wontfix` | Human maintainer only, with a written reason. |
| `wontfix` to `new` | Anyone with new information; categorize and verify again before routing. |

Everything else is rejected. In particular there is no direct move out of
`wontfix` into a route: reopening returns the record to `new` so the practice's
categorize-and-verify steps run again.

`wontfix` is the human-owned state. A record whose `last_actor` is `agent` may
not sit in it, and no `history` entry may show an agent making the move into it.
The same holds for every private-routing category, in every state. This is the
locked moderation decision: agents triage and recommend; humans decide.

## Evidence each state requires

| State | Required evidence |
| --- | --- |
| `new` | None. A record in `new` carries no evidence. |
| `needs-info` | `verification_attempt`, `missing_information`, `specific_ask`, `check_point`. |
| `ready-for-agent` | `verification_attempt`, `commit_checked`, `inspected_paths`, `observed_vs_expected`, `bounded_scope_reason`. |
| `ready-for-human`, category `bug` | `verification_attempt`, `commit_checked`, `inspected_paths`, `observed_vs_expected`, `maintainer_decision`. |
| `ready-for-human`, category `enhancement` | `problem_statement`, `affected_workflow`, `alternatives_checked`, `maintainer_decision`. |
| `ready-for-human`, private-routing category | `private_route`, `routing_fact`. |
| `wontfix` | `human_decision_reason`, plus at least one of `inspected_paths` or `duplicate_of`. |

`inspected_paths` must name repository-relative paths that exist under `--root`,
so a reviewer can open exactly what the triager read. `commit_checked` must be
7 to 40 hexadecimal characters. `check_point` must be an ISO date.
`private_route` must be one of the two named routes, `code-of-conduct-private-report`
or `private-intake-route`, so no address or case detail lands in Git. Free-text
evidence must be at least eight characters and may not be a placeholder; write
`not attempted` when nothing was tried rather than inventing a result.

## Owner roles

`owner_role` and each `history` entry's `role` come from one vocabulary, drawn
from the operating documents: `agent-sponsor`, `authorized-inviter`,
`beta-owner`, `bounded-agent`, `human-maintainer`, `human-moderator`,
`human-triager`, `maintainer-on-duty`, `private-intake-owner`, `release-owner`,
`reporter`. `agent-sponsor`, `authorized-inviter`, `beta-owner`,
`maintainer-on-duty`, `private-intake-owner`, and `release-owner` are defined in
[BETA_OPS](../BETA_OPS.md); `human-maintainer`, `human-triager`, and
`bounded-agent` in the [triage policy](../../.github/TRIAGE_POLICY.md);
`human-moderator` and `reporter` in the
[moderation model](../../community/MODERATION.md).

Constraints the checker enforces:

- `wontfix` is owned by `beta-owner`, `human-maintainer`, or `maintainer-on-duty`.
- `ready-for-human` is never owned by `bounded-agent`.
- A private-routing category is owned by `private-intake-owner` or `human-moderator`.
- A transition recorded with `actor: agent` uses `role: bounded-agent`; a
  transition recorded with `actor: human` uses a human role.

## How this fits the operating loop

Weekly handling runs in the Intake pass of the
[weekly cadence](../WEEKLY_CADENCE.md), and Buzz-side queue handling follows the
[maintainer runbook](../MAINTAINER_RUNBOOK.md). A bounded agent may run
`validate` on a record it drafted and `next` to see what a route would require,
then post its recommendation for a human. It cannot use this tooling to enact
one.

## Sources

As of: 2026-09-02.

- [practices/004-issue-triage.md](../../practices/004-issue-triage.md) — the states, the decision rules, and the failure modes this checker encodes.
- [.github/TRIAGE_POLICY.md](../../.github/TRIAGE_POLICY.md) — the transition mechanics and the maintainer and agent roles.
- [ops/BETA_OPS.md](../BETA_OPS.md) — private intake route handling and escalation routes.
- [ops/MAINTAINER_RUNBOOK.md](../MAINTAINER_RUNBOOK.md) — inbox triage and the human moderation checklist.
- [community/MODERATION.md](../../community/MODERATION.md) — roles, authority, and the human-owned enforcement boundary.
- [templates/REDACTION_CHECKLIST.md](../../templates/REDACTION_CHECKLIST.md) and [templates/INTAKE_CONSENT.md](../../templates/INTAKE_CONSENT.md) — the data-minimization rules a record respects.
- [tests/test_triage.py](../../tests/test_triage.py) — the executable statement of every rule above.
