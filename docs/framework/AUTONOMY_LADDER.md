# Autonomy Ladder

## Use the ladder to name what may run without a person

Every agent in [the community-agent registry](../../buzz/agents/registry.yaml) carries an autonomy value, and every packet written against [the agent packet schema](../schemas/AGENT_PACKET_SCHEMA.md) records one. Until now that value was a label. Nothing stated what an agent may do at `draft` that it may not do at `observe`, what has to be true before an operation runs at a level, what pulls it back down, or which operations may never run unattended no matter what evidence accumulates. Two artifacts could use the same word for different bounds and no check would notice.

This ladder is the sibling of [the capability ladder](CAPABILITY_LADDER.md). That one classifies what a Practitioner demonstrates; this one classifies what an operation is permitted to run without a person, and what evidence would move it. It is not a ranking of agents and not a roadmap: a level is a ceiling the repository's own documents set, not a schedule for reaching the next one.

Three rules hold at every level.

1. **Every level ends in a human decision.** Even an `observe` packet names the smallest human next step, because the packet schema requires one. Naming a next step is therefore not what separates the levels.
2. **What separates the levels is what leaves the agent and who receives it.** A0 returns a description of what was read. A1 adds candidate content nobody has applied. A2 delivers a named action into an assigned channel where a Practitioner reads it. A3 would perform the action.
3. **Levels are cumulative.** An agent at A2 may do everything A0 and A1 permit and nothing more. An agent that finds it needs a level above the one it was assigned stops and escalates instead of upgrading itself.

Owner gate 6, initial community-agent providers, is recorded **OPEN** in [the owner review packet](../../release/OWNER_REVIEW.md), and every registry status reads `not_enabled`. No agent operates at any level today. The levels below describe bounds, not activity.

## Levels

| Level | Registry and packet value | Attended | What leaves the agent |
|---|---|---|---|
| A0 | `observe` | Yes | A description of what the agent read, every claim carrying a pointer, returned to the requesting human role. |
| A1 | `draft` | Yes | The same, plus candidate content — text, a patch, or an artifact — that nobody has applied. |
| A2 | `recommend` | Yes | The same, plus one named action delivered as a reply in a channel the registry lists under `channels.write`. |
| A3 | `act-unattended-within-bounds` | No | The action itself, performed by the agent inside a recorded bound. |

The three attended values are exactly the vocabulary already used by [the registry](../../buzz/agents/registry.yaml) and [the packet schema](../schemas/AGENT_PACKET_SCHEMA.md). Do not introduce a synonym for any of them. The A3 identifier appears in no registry entry and in no packet, because no operation is at A3; adding a fourth value to either file is a governance change, not an editorial one.

## A0 observe

**The agent may.** Read the material named in its assignment, inside the channel and path scope recorded in its registry entry, and return what it read with a resolvable pointer for every claim. Name the smallest human next step. Flag a possible quality or conduct concern with a link and a concise, non-diagnostic summary, as [the moderation model](../../community/MODERATION.md) permits. Stop and escalate.

**The human must.** Assign the work, name the role that receives the output, and decide what follows from it. An observation is an input to a decision and is never itself a decision, an approval, or evidence that a gate or hold moved.

**Evidence required before an operation runs here.** The `R1` set in [Raising a level](#raising-a-level): a registry entry that passes `python3 scripts/validate_agents.py --root .`, owner gate 6 recorded approved by a human, every enablement prerequisite in the entry satisfied, and a named accountable human role receiving the output.

**Recorded when it runs.** One packet conforming to [the packet schema](../schemas/AGENT_PACKET_SCHEMA.md) with `autonomy: observe`, a `source_commit`, every input carrying its provenance pointer and trust level, a populated refusals section, and `human_decision_required: true`.

**Automatic demotion.** The agent stops and its entry returns to `not_enabled`, pending a human decision, when any of these is observed: `scripts/validate_agents.py` fails on its entry; a packet `Provenance` pointer does not resolve at the recorded `source_commit`; a run reads a channel or path outside the scope recorded in its entry; or an enablement prerequisite recorded in its entry stops holding, such as an escalation route that no longer reaches a human.

## A1 draft

**The agent may.** Everything A0 permits, plus produce candidate content — draft text, a proposed patch, a candidate artifact — and return it to the requesting human role unapplied. Nothing the agent drafts is applied, posted, merged, or published by the agent.

**The human must.** Own a review queue that accepts, revises, rejects, or escalates every candidate, apply the accepted version themselves, and record the decision in the affected Git record per [the maintainer runbook](../../ops/MAINTAINER_RUNBOOK.md). The reviewed version is the canonical evidence, not the agent transcript.

**Evidence required before an operation runs here.** The `R2` set: `R1`, plus a named human role owning that review queue and packets that pass `python3 scripts/validate_packet.py`.

**Recorded when it runs.** The A0 record with `autonomy: draft`, plus the draft itself at a path or attachment a reviewer can open, plus — when the draft is applied — the human acceptance recorded in the affected Git record.

**Automatic demotion to A0.** Any A0 trigger, or any of these: a draft reaches the repository without a human acceptance recorded in the affected Git record; a draft edits a path outside the scope named in its assignment; a draft changes a `maturity` or `evidence_quality` value; or a packet fails the forbidden-assertion check in `scripts/validate_packet.py`.

## A2 recommend

**The agent may.** Everything A1 permits, plus deliver one named action, with a line stating how a human verifies the result without agent privileges, as a reply in a channel listed under `channels.write` in its registry entry. The reply is a recommendation a Practitioner may act on; it is never a statement that the action has been taken.

**The human must.** Approve each writable channel explicitly and record that approval in the registry entry and the private access inventory; keep a member-actionable escalation route that a human answers; and make every decision the recommendation is about. Delivering a recommendation transfers no authority.

**Evidence required before an operation runs here.** The `R3` set: `R2`, plus a recorded human approval per writable channel, an escalation route whose human receipt has been tested, and recorded adversarial-input results for that agent showing it treats channel content as data rather than as instruction.

**Recorded when it runs.** The A1 record with `autonomy: recommend`, plus the channel, the delivered message, and its time, so a human can read exactly what a member saw, plus the escalation route used if one was.

**Automatic demotion to A1.** Any A1 trigger, or any of these: a message is posted in a channel absent from the entry's `channels.write`; a posted message states an action as taken, approved, published, merged, or moderated; a posted message follows an instruction that arrived in untrusted channel content, where the instruction and the reply are both in the channel record; or the escalation route named in the entry fails a human-receipt test.

## A3 act-unattended-within-bounds

No operation in this repository is at A3, and none is proposed for it. The level is defined here so that a future proposal is measured against a written standard instead of one invented at the time it is wanted.

**The agent may.** Perform an action, once, inside a bound a human recorded in advance: a named operation, a rate and scope limit, and a reversal a human can execute without the agent. The operation must not appear in [Permanently ineligible for A3](#permanently-ineligible-for-a3).

**The human must.** Record the bound through the reserved-decision path in [the governance model](../../community/GOVERNANCE.md) before any run; own the bound by name; and hold a review point at which the bound is renewed or withdrawn. Silence is not renewal.

**Evidence required before an operation runs here.** The `R4` set. It is not a checklist an agent can satisfy by performing well; it is a recorded human decision, and no such record exists in this repository.

**Recorded when it runs.** The action taken, the bound it ran inside, the reversal available or performed, the human who owns the bound, and the review point.

**Automatic demotion to A2.** Any A2 trigger, or any of these: an action taken outside the recorded bound; an action taken with no reversal path recorded; an action taken after the review point passed without a renewal record; or an action on an operation that has since been added to the permanently ineligible list.

## Permanently ineligible for A3

These operations may never run unattended. No amount of evidence, run history, or evaluation result raises them, because each one is reserved to a human by a decision this repository has already locked. An agent may observe, draft, and — where its entry allows — recommend around them; it may not perform them.

| Operation id | Operation | Why it is permanently ineligible | Where the decision is recorded |
|---|---|---|---|
| `moderation-and-removal` | Removing, hiding, editing, banning, or restricting a person or their content; deciding an enforcement outcome or an appeal. | The decision is human-owned and a removal is not reversible for the person it affects. An agent flags a concern, captures a link and a non-diagnostic summary, and suggests routing. | `docs/DECISIONS.md` (Moderation), `docs/NON_GOALS.md` (autonomous moderation, banning, or content deletion), `community/MODERATION.md` (Roles and authority) |
| `maturity-promotion` | Changing a `maturity` or `evidence_quality` value, or presenting a proposed method as a tested Practice. | A promotion is a human decision with recorded trial evidence; an agent that could set the field could manufacture the evidence level it reports. | `release/OWNER_REVIEW.md` (hold 4, Tested-Practice evidence), `buzz/agents/registry.yaml` (every entry's prohibited list) |
| `publication-approval` | Deciding that an artifact, release, decision, or policy may be published or announced, in any public or member-visible surface. | A public claim cannot be silently retracted, and the final launch announcement is a manual action the owner never delegates. Approval is the judgment; delivering content already approved is a separate operation and is not this row. | `docs/OWNER_GATES.md` (Manual actions never delegated), `ops/MAINTAINER_RUNBOOK.md` (Releases), `buzz/agents/registry.yaml`, `community/AMENDMENTS.md` (001) |
| `owner-identity-and-keys` | Creating, recovering, holding, entering, or requesting the owner identity, a private key, a credential, a token, or a recovery code. | One identity per agent with least access is a locked decision, and identity creation and key handling are manual actions never delegated. | `docs/DECISIONS.md` (Agent security), `docs/OWNER_GATES.md` (Manual actions never delegated), `ops/BUZZ_SECURITY.md` |
| `license-and-governance-change` | Changing a license, the governance model, the mission, the non-goals, repository ownership, privileged access, or a maintainer appointment. | These are reserved, hard-to-reverse decisions; the governance model states that no agent may make them. | `docs/OWNER_GATES.md` (Manual actions never delegated), `community/GOVERNANCE.md` (Decision paths), `docs/DECISIONS.md` |
| `owner-reserved-decision` | Any decision `docs/OWNER_GATES.md` reserves to the owner: every gate row, and every manual action listed as never delegated. | The gate exists because a human has to look at the thing before it is true. An agent that could close a gate would be closing it on its own report. | `docs/OWNER_GATES.md`, `release/OWNER_REVIEW.md` (Owner gates) |

An operation that is a near neighbour of one of these rows is treated as the row until a human says otherwise. Recommending a removal is not moderation; drafting an announcement is not publication; proposing a patch is not a merge. The boundary is the act, not the preparation.

This list held seven rows until [amendment 001](../../community/AMENDMENTS.md)
narrowed two of them. `merge` left the list in favour of bounded auto-merge, and
`publication-and-announcement` split so that only the approval half remains here.
Both replacements are *eligible*, which means they may be proposed through the
normal path and nothing more: a signed promotion in `ops/autonomy/promotions.yaml`
and an independently released kill switch. Neither is catalogued, promoted, or
running.

**Bounded auto-merge.** A merge may run unattended only when the pull request was
opened by the unattended runner itself and never by a person, changes nothing
outside the promoted operation's declared write scope, passes every required
check with no reviewer requesting changes, and is recorded in the action ledger
with the resulting commit and the exact command that reverts it.

**Approved-content delivery.** A delivery may run unattended only when a signed
approval record in Git identifies the exact content by commit or content hash,
the content is delivered byte-identical with no edit or reformatting, the
destination is named in the approval rather than chosen by the agent, the
approval is within the window the promotion states, and the delivery is recorded
against the approval reference. Selecting an audience, scheduling, and
re-publishing stay outside it.

### The self-modification exclusion

No A3 operation may create, change, merge, or deliver a change to a file that
governs its own bounds — at minimum `docs/DECISIONS.md`, `docs/NON_GOALS.md`,
`docs/OWNER_GATES.md`, `community/GOVERNANCE.md`, `community/AMENDMENTS.md`, this
document, anything under `ops/autonomy/`, and anything under `.github/`.

This exclusion is not waivable by a promotion, because an agent that can widen
its own bounds has no bounds. `scripts/autonomy_guard.py` enforces it by
refusing any write scope that could reach a governed path, matching loosely so
that a scope dangerous under the widest reading is refused;
`scripts/run_unattended.py` enforces the other half, applying a written path
only when it is in scope under the narrowest reading. The two matchers
deliberately disagree, and both err toward refusing.

## Action vocabulary

The mapping table below records what each operation is allowed to do in these terms. An action may be used only at or above its minimum level.

| Action | Minimum level | Meaning |
|---|---|---|
| `read-assigned` | A0 | Read material inside the channel and path scope recorded in the agent's registry entry or the assignment. |
| `report-observation` | A0 | Report what was read, with a resolvable pointer for every claim. |
| `name-next-action` | A0 | Name, in the returned packet, exactly one smallest next step for a human, with a verification line. |
| `flag-concern` | A0 | Flag a possible quality or conduct concern with a link and a concise, non-diagnostic summary, for human routing. |
| `escalate` | A0 | Stop the affected work and hand the smallest safe context and the exact decision needed to a named human role. |
| `draft-artifact` | A1 | Produce candidate text or a candidate artifact that nobody has applied. |
| `draft-patch` | A1 | Produce a proposed change to an existing file, unapplied, for a human to review and apply. |
| `deliver-recommendation` | A2 | Post the named action as a reply in a channel listed under `channels.write` in the agent's registry entry. |

## Raising a level

Raising an operation is a human decision recorded in Git. An agent never raises its own level, and a run of good outputs is not a raise.

- `R1` — **Bounded and declared.** A registry entry recording identity, sponsor role, exact channel scope, prohibitions, and escalation route; `python3 scripts/validate_agents.py --root .` passing; owner gate 6 recorded approved by a human in [the owner review packet](../../release/OWNER_REVIEW.md); every enablement prerequisite in the entry satisfied and recorded in the private access inventory described in [the Buzz security model](../../ops/BUZZ_SECURITY.md).
- `R2` — **Reviewable draft.** `R1`, plus a named human role owning a review queue that accepts, revises, rejects, or escalates every candidate before a human applies it, and packets that pass `python3 scripts/validate_packet.py`.
- `R3` — **Delivered recommendation.** `R2`, plus an explicit human approval per channel in `channels.write`, recorded in the registry entry and the private access inventory; a member-actionable escalation route whose human receipt has been tested; and recorded adversarial-input results for that agent covering instruction injection, credential requests, publication and merge requests, maturity changes, and removal requests.
- `R4` — **Unattended action.** A founder decision recorded through the reserved-decision path in [the governance model](../../community/GOVERNANCE.md), naming the operation, the bound it may act inside, the rate and scope limit, the reversal a human can execute without the agent, the human who owns the bound, and the review point — for an operation absent from the permanently ineligible list. No such record exists in this repository.

A demotion needs no decision. It is automatic on the observable triggers in the level sections above, and the human decision that follows is whether to restore the level, not whether the demotion happened.

## Current level of every agent and cadence operation

The table maps every agent in [the registry](../../buzz/agents/registry.yaml) and every pass, queue, check, and escalation in [the cadence index](../../ops/cadence.yaml) to the level its own source document bounds it to. **Nothing in this repository is at A3.** Raising anything to A3 is a human decision recorded through the governance path described above; it is not an agent's decision, not a consequence of an agent performing well, and not something a validator can conclude.

A level here is a ceiling, not a status. Every agent entry reads `not_enabled` while owner gate 6 is recorded OPEN. Some passes have no standing agent at all: the cadence gives Build to an assigned bounded construction agent and records that no persistent general builder profile exists, so that row bounds an assignment rather than a registered identity.

| Item | Kind | Current level | Allowed actions | Evidence required to raise it |
|---|---|---|---|---|
| `steward` | agent | A2 | `read-assigned`, `report-observation`, `name-next-action`, `flag-concern`, `escalate`, `draft-artifact`, `deliver-recommendation` | At the attended ceiling. A rise means A3, and a member may act on a delivered reply before a human reads it, so `R4` would need a reversal the agent cannot perform. |
| `librarian` | agent | A1 | `read-assigned`, `report-observation`, `name-next-action`, `flag-concern`, `escalate`, `draft-artifact` | `R3`, plus a profile that states a posting capability and a channel under `channels.write`. The profile ends at returning the candidate to a human maintainer, so the registry grants no write. |
| `release-editor` | agent | A1 | `read-assigned`, `report-observation`, `name-next-action`, `escalate`, `draft-artifact` | `R3`, plus a writable channel that is not a publication surface. Its only conditional channel is `announcements`, and publication and announcement are permanently ineligible. |
| `research-auditor` | agent | A1 | `read-assigned`, `report-observation`, `name-next-action`, `escalate`, `draft-artifact` | `R3`, plus the approved audit assignment naming the exact public channel, which the entry's `channel_note` records as not yet named. |
| `guide-maintainer` | agent | A1 | `read-assigned`, `report-observation`, `name-next-action`, `escalate`, `draft-artifact`, `draft-patch` | `R3`, plus a stated posting capability. The profile states it does not publish or merge, so its patch stays a proposal a human applies. |
| `intake` | pass | A2 | `read-assigned`, `report-observation`, `name-next-action`, `flag-concern`, `escalate`, `draft-artifact`, `deliver-recommendation` | `R4`, plus a reversal for a route a member has already acted on. The cadence assigns confirmation of routing, scope, and priority to a Maintainer. |
| `build` | pass | A1 | `read-assigned`, `report-observation`, `name-next-action`, `escalate`, `draft-artifact`, `draft-patch` | Nothing to deliver at A2: the output is a draft for review. A rise to A3 needs `R4`, and the merge that ends the pass is permanently ineligible. |
| `review` | pass | A1 | `read-assigned`, `report-observation`, `name-next-action`, `escalate`, `draft-artifact`, `draft-patch` | `R4`. Reviewing agents return findings; the merge, request-changes, redirect, or decline decision is the area maintainer's. |
| `release` | pass | A1 | `read-assigned`, `report-observation`, `name-next-action`, `escalate`, `draft-artifact` | Cannot rise. The pass ends in `publication-approval`, which is permanently ineligible for A3 regardless of evidence. |
| `session` | pass | A1 | `read-assigned`, `report-observation`, `name-next-action`, `escalate`, `draft-artifact` | `R4`, plus consent handling that stays with the human facilitator. Participant material is never committed to this repository, so there is no record an unattended run could work from. |
| `maintenance` | pass | A1 | `read-assigned`, `report-observation`, `name-next-action`, `flag-concern`, `escalate`, `draft-artifact`, `draft-patch` | `R4`. Disposition is the artifact maintainer's decision, and a deprecation changes an artifact's standing, which is human-owned. |
| `safety_privacy_access_conduct` | queue | A0 | `read-assigned`, `flag-concern`, `name-next-action`, `escalate` | Cannot rise. The case record is private by design, so there is nothing here an agent may draft, and the operation is permanently ineligible as `moderation-and-removal`. |
| `questions_and_contributions` | queue | A2 | `read-assigned`, `report-observation`, `name-next-action`, `flag-concern`, `escalate`, `draft-artifact`, `deliver-recommendation` | `R4`, plus a reversal for a route a member has acted on. The human owner and the next action are recorded by a person. |
| `agent_review` | queue | A1 | `read-assigned`, `report-observation`, `name-next-action`, `escalate`, `draft-artifact` | `R4`. Acceptance is the requesting human maintainer's decision, and agent output is never itself evidence of publication, merge, moderation, or release approval. |
| `follow_up_and_broken_links` | queue | A1 | `read-assigned`, `report-observation`, `name-next-action`, `escalate`, `draft-artifact`, `draft-patch` | `R4`, plus a bound separating a mechanical reference fix from a content change. A human decides the status change today. |
| `stop_and_escalate` | escalation | A0 | `read-assigned`, `report-observation`, `name-next-action`, `escalate` | Cannot rise. Escalation exists because the next decision is reserved to a human; an unattended handler would be deciding the matter it escalated. |
| `blocked_handoffs` | check | A0 | `read-assigned`, `report-observation` | Nothing to draft: the check reports which bounded tasks stopped. A blocked handoff waits on a human decision, not on more agent output. |
| `open_owner_gates` | check | A0 | `read-assigned`, `report-observation` | Cannot rise. Each gate is an `owner-reserved-decision`; the check repeats the recorded status and never records, implies, or infers an approval. |
| `stale_as_of` | check | A0 | `read-assigned`, `report-observation` | `R2`, if a human wants a drafted disposition per stale file. Deciding staleness remains the artifact maintainer's call. |

The mapping is checked by `tests/test_autonomy_policy.py`. Adding an agent to the registry or a pass, queue, check, or escalation to the cadence index without adding a row here fails that test.

## Sources

As of: 2026-09-02.

- [buzz/agents/registry.yaml](../../buzz/agents/registry.yaml) — the autonomy value, channel scope, prohibitions, and enablement prerequisites each level is read against.
- [docs/schemas/AGENT_PACKET_SCHEMA.md](../schemas/AGENT_PACKET_SCHEMA.md) — the record every level produces and the assertions a packet may never make.
- [ops/cadence.yaml](../../ops/cadence.yaml) and [ops/WEEKLY_CADENCE.md](../../ops/WEEKLY_CADENCE.md) — the operations mapped above and the human owner of each pass.
- [ops/MAINTAINER_RUNBOOK.md](../../ops/MAINTAINER_RUNBOOK.md) — the human review checklist an A1 or A2 output is read against.
- [community/MODERATION.md](../../community/MODERATION.md) and [community/GOVERNANCE.md](../../community/GOVERNANCE.md) — the human-owned enforcement boundary and the reserved-decision path.
- [docs/DECISIONS.md](../DECISIONS.md), [docs/NON_GOALS.md](../NON_GOALS.md), and [docs/OWNER_GATES.md](../OWNER_GATES.md) — the locked decisions behind the permanently ineligible list.
- [release/OWNER_REVIEW.md](../../release/OWNER_REVIEW.md) — owner gate 6 and the operating holds that keep every agent `not_enabled`.
- [ops/triage/README.md](../../ops/triage/README.md) — the worked case of an agent that recommends a state and a human who owns the closing one.
