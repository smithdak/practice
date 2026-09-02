# Issue triage policy

Every new issue gets exactly one category, one state label, and a written
routing record. Humans decide accept and close; agents may label and recommend
only. This policy fulfills the triage-policy deferral recorded in
[swarm/handoffs/F005.md](../swarm/handoffs/F005.md) and maps the state machine from
[Triage community issues with an evidence-backed state machine](../practices/004-issue-triage.md)
onto GitHub labels.

## Relationship to other documents

- The practice above defines the categorize–verify–route method and the
  decision-rules table. This policy adds label names and GitHub mechanics and
  does not change those rules.
- Conduct, safety, access, or legal reports never enter public triage and
  never receive a public label. Route them to the private reporting route in
  the [Code of Conduct](../CODE_OF_CONDUCT.md) under the
  [moderation model](../community/MODERATION.md).
- Weekly handling runs in the Intake pass of the
  [weekly cadence](../ops/WEEKLY_CADENCE.md). The queue states in the
  [maintainer runbook](../ops/MAINTAINER_RUNBOOK.md) (`NEW`, `NEEDS-CONTEXT`,
  and so on) are for Buzz queue items, not GitHub labels.
- First-triage response expectations are reviewed against real data at the
  day-30 beta review in [ops/BETA_OPS.md](../ops/BETA_OPS.md).

## Labels

Minimal set. The issue forms set the artifact labels; triagers add category
and state.

| Label | Meaning | Applied by |
| --- | --- | --- |
| `bug` | The artifact behaves in a way its maintainer would not intend. | Triager, after verification. |
| `enhancement` | A requested new capability or change. | Triager, after verification. |
| `needs-info` | Waiting on reporter detail. The issue records what is missing, the specific ask, and a check point. | Triager. |
| `ready-for-agent` | Verified and bounded, safe for agent-assisted work under human review. Not an acceptance. | Triager. |
| `ready-for-human` | Verified, but scope needs maintainer judgment: priority, breaking change, permissions, security, licensing, or cross-area impact. | Triager. |
| `wontfix` | Closed as expected behavior, duplicate, or without a use case. Human decision and written reason required. | Human maintainer only. |
| `blocking` | Defect that breaks a published artifact, build, link, or a contribution path. Use sparingly. | Triager. |
| `lab`, `practice`, `project`, `story` | Artifact type, set by the issue form. | Issue form. |
| `proposal` | Draft proposal on a proposal-form issue; replaced by category labels once work is accepted. | Issue form. |

An issue carries at most one state label (`needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`) at a time; adding a new one removes the previous
one. Category and state are independent. The state labels use the same names
as the practice's states, so the label set is the state machine.

Labels are created in repository settings once the GitHub destination is
confirmed; this is part of the beta setup checklist in
[ops/BETA_OPS.md](../ops/BETA_OPS.md).

## State transitions

Routing rules — which route applies to which verification result — come from
the decision-rules table in the practice. This table only records the
mechanics.

| Transition | Who may apply it | Required written record in the issue |
| --- | --- | --- |
| New → `needs-info` | Triager | What was tried, what is missing, the specific ask, and a check point. |
| New or `needs-info` → `ready-for-agent` | Triager | Category `bug`, repro steps or code path, commit checked, observed versus expected, and why the scope is bounded. |
| New or `needs-info` → `ready-for-human` | Triager | Same evidence, plus the specific decision the maintainer must make. |
| Any state → `wontfix` (closed) | Human maintainer only | Written reason; duplicates point to the retained issue. |
| Any state → reopened | Anyone with new information | Re-run categorize and verify; append the new record. |

Use the state-change form from the practice for each record. Never paste
secrets, private reporter details, or confidential material into an issue.

## Priority and response-time expectations

These are beta-period expectations, not service-level commitments. "Response"
means the state label plus routing record applied, not a fix.

| Priority | Use when | First response | Afterward |
| --- | --- | --- | --- |
| Conduct or safety | Any conduct, privacy, or safety concern. | Not in this policy: route privately immediately; no public label. | Per the moderation model. |
| `blocking` | Published artifact, build, link, or contribution path broken. | Within 2 operating days, through the continuous queue. | Daily update until contained; then normal states. |
| Everything else | All other issues and proposal forms. | Triaged in the next weekly Intake pass (within 7 days). | `needs-info` check point defaults to 7 days; extend only with a recorded reason. |

An operating day is a day on which a maintainer pass runs. If triage cannot
happen in the window, say so in the issue instead of staying silent.

## Maintainer and agent roles

| Actor | May | Must not |
| --- | --- | --- |
| Human maintainer | Accept work, set priority, close and reopen issues, merge changes. | — |
| Human triager | Categorize, verify, apply state labels, write routing records. | Close or accept without a recorded maintainer decision; decide conduct matters. |
| Bounded agent | Verify against the codebase, apply labels, comment with its own evidence, draft routing records, recommend a route. | Close, accept, merge, edit, or delete; invent repro steps, versions, or error messages; label conduct matters publicly; act beyond its assigned scope. |

Any agent action that closes, deletes, restricts, or accepts is an incident:
revert through normal review and record a correction, per the practice's
failure modes.

## How the issue forms route

| Form | Labels set by the form | First triage step | Accept means |
| --- | --- | --- | --- |
| [Lab](ISSUE_TEMPLATE/lab.yml) | `lab`, `proposal` | Check the question is bounded and the expectation falsifiable; search for duplicate Labs. | Proceed to a draft Lab via pull request using the Lab template. |
| [Practice](ISSUE_TEMPLATE/practice.yml) | `practice`, `proposal` | Check the outcome is concrete and existing evidence is labeled as such; align against existing Practices. | Draft a Practice at `maturity: proposed`. |
| [Project](ISSUE_TEMPLATE/project.yml) | `project`, `proposal` | Check the stewardship field first: no named human maintainer, no maintained project per the [contribution model](../community/CONTRIBUTION_MODEL.md). | A bounded design discussion, not an instantly maintained project. |
| [Story](ISSUE_TEMPLATE/story.yml) | `story` | Check the result claims match the evidence-quality terms in the [Story schema](../docs/schemas/STORY_SCHEMA.md); real implementations only. | Draft a Story via pull request. |

Proposal-form issues are verified like enhancements but keep the `proposal`
label until work is accepted, when the maintainer swaps it for `enhancement`
or the relevant artifact label. Issues filed without a form are categorized as
`bug` or `enhancement` directly under the practice's decision rules.
