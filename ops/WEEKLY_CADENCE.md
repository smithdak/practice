# Weekly Operating Cadence

Practice should produce a small number of useful, reviewable artifacts—not a
constant stream of messages. This cadence gives a founder and a small set of
agents a repeatable operating loop. The day names are a suggested rhythm; the
queues remain usable when a person is unavailable.

## Operating rule

Every pass has a named output. If there is no output to create, decide, route,
or maintain, skip the pass and record nothing. Buzz is used for working
conversation and routing; Git remains the durable record. Scheduled Buzz
workflows are not required.

## Two kinds of work

### Continuous queues

These are handled when an item arrives or when a safety threshold is reached:

- **Safety, privacy, access, and conduct:** route immediately to an eligible
  human moderator or founder through the private process. An agent may triage
  and recommend; it never enforces or resolves the case.
- **Questions and contributions:** record the smallest next action, route to
  an existing artifact or Git issue, and assign a human owner.
- **Agent review:** an agent may prepare a bounded packet; the requesting
  human maintainer accepts, revises, rejects, or escalates it in the Git
  record.
- **Follow-up and broken links:** keep the item open with an owner and check
  point until it is resolved or deliberately deferred.

Queue states and routing follow the [Maintainer Operating
Runbook](MAINTAINER_RUNBOOK.md). No weekly meeting is needed to clear an
urgent item.

### Scheduled review

The weekly pass below is a review window, not a promise to publish every week.
It inspects the queues, selects bounded work, and records decisions. A release
or Session happens only when its packet is ready and a human approves it.

## Weekly loop

| Pass | What happens | Packet/output | Agent preparation | Human approval or action |
| --- | --- | --- | --- | --- |
| **Intake (Monday)** | Review new and follow-up entries, deduplicate, classify, and choose the smallest useful work. Safety and access items are handled first whenever they arrive. | Updated queue entries with state, owner, next action, and a selected work brief. | **Practice Steward** drafts next-action and routing summaries; **Practice Librarian** identifies duplicates and the appropriate artifact path. Both exclude private evidence and secrets. | Maintainer confirms routing, scope, and priority; unresolved policy, access, licensing, governance, or conduct matters escalate. |
| **Build (Tuesday–Wednesday)** | Produce or revise one bounded Practice, Guide, Lab, Note, Story, Project change, or operational record. Keep work in Git and link any related Buzz discussion. | Draft artifact or pull request with inputs, source links where needed, acceptance checks, limitations, and a reviewer. | The **assigned bounded construction agent** drafts from the brief (there is no persistent general builder profile); **Practice Librarian** can structure the artifact path. They report uncertainty and missing evidence. | Author/maintainer verifies the actual change and decides whether it is ready for review. |
| **Review (Thursday)** | Inspect the draft against the relevant schema, quality bar, safety boundaries, links, and evidence. Record requested changes or a decision. | Review record in the Git issue/PR, including decision, rationale, unresolved risks, and follow-up owner. | **Guide Maintainer** checks coherence, references, and prerequisites; **Research Auditor** checks current claims and primary sources; **Practice Librarian** checks artifact fit and attribution. They return findings—not an approval. | Area maintainer makes the merge/request-changes/redirect/decline decision. A conflicted reviewer recuses and routes to an eligible human. |
| **Release (Friday, when ready)** | Assemble only merged, review-complete work into a release candidate. Draft a concise announcement that says what changed, who it helps, and where the canonical artifact lives. | Git release record and, if approved, a Buzz announcement or other launch-channel post. | Release Editor prepares the candidate notes and flags missing evidence, unmerged work, or unresolved risk. | Human release owner approves, amends, or holds the release and announcement. An agent never announces unmerged work or makes commitments. |
| **Session (scheduled only when useful)** | Run a Practice Session when there is a participant need and a concrete artifact to produce: intake and consent, preparation, facilitation, capture, follow-up, and publication review. | Session brief, captured draft or decision, participant-safe follow-up, and a publication decision. | **Practice Steward** prepares the participant-facing next action and **Practice Librarian** prepares the agenda, source links, prompts, and capture template; they label hypothetical examples and do not publish participant material. | Human facilitator owns participant safety and consent; human maintainer approves any durable or public artifact. |
| **Maintenance (last Friday or next available pass)** | Check due freshness reviews, stale links, owner coverage, open follow-ups, access inventory, and backup/recovery confirmations. Trigger maintenance early when a source or policy changes. | Maintenance record naming each item, evidence checked, disposition (keep/revise/replace/**deprecate**), owner, and next check point. | **Guide Maintainer** finds stale references and proposes version changes or deprecations; **Research Auditor** checks current claims and **Practice Steward** flags unclear next actions. They propose changes without silently altering policy. | Artifact maintainer decides the disposition. Founder or designated continuity owner handles reserved access, recovery, and owner-gate decisions. |

The release and maintenance passes may be combined when there is little work.
The review pass still records a decision even when the decision is “hold” or
“no release.”

## Packet contracts

Agents work from a bounded packet containing the task, allowed paths or
channels, source artifacts, expected output, checks, and escalation boundary.
The resulting packet links to the source task and includes:

1. the output or findings;
2. uncertainty, missing context, and unsupported claims;
3. checks run and their results; and
4. a recommended next action for a named human.

The human decision is recorded in the affected Git record. Agent output is
never itself evidence of publication, merge, moderation, or release approval.

## Small-community and low-activity fallback

When there are few contributors, the founder or one maintainer may own the
human actions, while agents prepare only the packet types that save time. Run
one short operating pass every two weeks, or on the next available day, and
process urgent queue items continuously. In a low-activity week:

- do not manufacture a release, Session, announcement, or discussion;
- carry forward only items with a named owner and next check point;
- perform maintenance only where a trigger or due review exists; and
- record `No release` or `No Session` in the private maintainer record when a
  scheduled review considered that decision.

This fallback preserves a usable queue and durable decisions without requiring
volume, standing meetings, or daily channel activity.

## Stop and escalate

Pause the affected work when required evidence is unavailable, a source or
policy conflicts, an agent requests expanded access, a risk cannot be bounded,
or a decision belongs to the founder or another reserved human owner. Record
the smallest safe context, the exact decision needed, and the next owner. Do
not place secrets, confidential material, private moderation evidence, or
owner private keys in a Buzz or Git packet.
