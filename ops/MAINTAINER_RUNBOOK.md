# Maintainer Operating Runbook

## Outcome and boundary

This runbook lets a human maintainer turn incoming questions and contributions
into safe, durable, useful Practice work. It is an operating procedure, not a
new governance policy. The controlling rules remain the
[governance model](../community/GOVERNANCE.md),
[contribution model](../community/CONTRIBUTION_MODEL.md),
[moderation model](../community/MODERATION.md), and
[Owner Gates](../docs/OWNER_GATES.md).

Buzz is the place for working conversation and routing. Git is the durable
record for issues, pull requests, accepted artifacts, decisions, and releases.
Do not make a Buzz thread the only record of a decision or reusable artifact.
Do not place credentials, private keys, recovery codes, confidential material,
or private moderation evidence in either public queue.

Operate through the queues below, not standing meetings. A maintainer clears
the actionable entries during each operating pass and records a next owner and
action before leaving anything open. An immediate safety, privacy, access, or
security concern interrupts the normal queue.

## Responsibilities and decision boundaries

| Role | Owns | May do | Must escalate or not do |
| --- | --- | --- | --- |
| Human maintainer | Routine artifact, question, and release-readiness queues in an assigned area. | Route work, review contributions, merge routine in-scope changes, and explain the decision in the Git record. | Escalate conflicts, cross-area changes, reserved decisions, access, licensing, and conduct enforcement. |
| Human moderator or triager | Private conduct intake and case routing. | Preserve the minimum evidence, assess immediate risk, and follow the moderation process. | An agent never investigates, decides, warns, restricts, removes access, or resolves an appeal. A conflicted human routes the case to an eligible human. |
| Founder | Reserved decisions and launch accountability. | Decide the matters reserved in governance; appoint or remove maintainers; confirm owner gates. | Does not need to review each routine contribution. |
| Community agent | A bounded, assigned support task. | Summarize published material, find broken links or stale sections, draft a review packet or pull request, and recommend routing. | Cannot merge, publish a release, make policy or licensing decisions, expand its own access, make moderation decisions, or claim unverified results. |

When a maintainer has a material authorship, employment, financial, client,
sponsorship, personal, or close-relationship conflict, they disclose it in the
record and route the final decision to an eligible uninvolved human. If none is
available, route it to the founder. See
[Governance: Conflicts, recusal, and reconsideration](../community/GOVERNANCE.md#conflicts-recusal-and-reconsideration).

## Queues and records

Use a small number of explicit queues. Keep an entry bounded and give it one
state: `NEW`, `NEEDS-CONTEXT`, `IN-REVIEW`, `AWAITING-HUMAN`, `DECIDED`, or
`FOLLOW-UP`. `DECIDED` records the outcome and rationale; `FOLLOW-UP` has a
named owner and a check point. Close duplicates with a pointer to the retained
record.

| Queue | Intake and durable record | Human owner | Route when it cannot be resolved routinely |
| --- | --- | --- | --- |
| Questions | Public Buzz question, linked to a Git issue only when durable work is needed. | Area maintainer. | Safety, privacy, access, policy, licensing, or a missing owner goes to the maintainer queue. |
| Contribution and artifact review | Git issue or pull request; Buzz discussion links back to it. | Assigned area maintainer. | Cross-area, material operating, or reserved change uses the governance decision path. |
| Agent review | The source task, agent output, and human review note in the affected Git record. | Requesting human maintainer. | Unsafe output, access request, policy conflict, or decision outside the assignment is stopped and escalated. |
| Release | Git release candidate and the private `RELEASE` maintainer item. | Release owner, who is human. | Public release, material exception, or unresolved risk awaits the founder or other required human decision. |
| Moderation and safety | Private reporting route and minimum necessary private case record. | Eligible human triager or moderator. | Immediate risk, conflict, appeal, or lack of coverage follows the moderation model. |
| Stale-content review | Git issue or pull request naming the artifact, trigger, evidence, and proposed disposition. | Artifact maintainer. | A material scope, governance, license, or project-retirement decision follows governance. |
| Continuity and backup | Private owner-maintained recovery record; a safe Git issue or maintainer item may record only that a check occurred. | Founder or designated human continuity owner. | Access loss, compromised identity, or missing recovery material goes to the founder; do not reconstruct secrets in a queue. |

For a private Buzz `maintainers` queue item, use the established form:

`DECISION|REVIEW|RELEASE|MODERATION · context · evidence/link · recommendation · human owner/action`

Use `DECISION` for a question that needs a human choice, `REVIEW` for a bounded
review packet, `RELEASE` for readiness or announcement approval, and
`MODERATION` only for a private escalation. Do not put sensitive case details,
secrets, or credentials in the item.

## Each operating pass

Work this checklist in order. It keeps urgent work from disappearing behind
routine activity.

1. Check private moderation, security, access, and owner-gate escalations
   first. Assign an eligible human; immediately route anything urgent under the
   relevant recovery procedure.
2. Read `NEW` and `FOLLOW-UP` queue entries. Deduplicate, classify, and name a
   human owner. Ask for the smallest missing context instead of guessing.
3. Route questions to an existing Practice, Guide, Lab, contribution path, or
   a specific next action. Convert a discussion into a Git record when it
   proposes durable work or a decision.
4. Work ready artifact and agent review packets. Make the human decision in
   the Git record; do not leave an agent recommendation appearing to be a
   decision.
5. Check the release and stale-content queues for entries that are waiting on
   a human action or whose review point has arrived.
6. Record a result, next action, and owner for every item touched. Link any
   accepted Git change back to the relevant Buzz conversation when that helps
   the Practitioner find the outcome.

## Inbox triage and questions

### Triage checklist

For every new item, identify the smallest valid route before answering.

- Is there an immediate safety, privacy, security, access, or conduct concern?
  Stop ordinary handling and route it privately to an eligible human.
- Is it a question seeking a next action? Answer from a published artifact when
  possible; otherwise ask for the missing workflow, input, output, or
  constraint.
- Is it a correction, Note, Practice, Guide, Lab, Story, or Project proposal?
  Route it through the [contribution ladder](../community/CONTRIBUTION_MODEL.md#contribution-ladder).
- Is it a request to change policy, governance, license, access, permissions,
  a public commitment, or a maintained Project's status? Create a bounded
  `DECISION` item and use the governance path.
- Does it contain secrets, confidential information, personal data, unlicensed
  material, or a claim presented as evidence without support? Do not reproduce
  it. Ask the contributor to remove or safely summarize it; route a possible
  conduct concern privately.

### Answering questions

Aim to move the Practitioner one step forward, not to simulate expertise or
close discussion quickly.

1. Restate the concrete outcome or uncertainty in plain language.
2. Link the most relevant existing artifact or channel, if one exists.
3. Give one bounded next action and state what result to return with.
4. Mark assumptions, hypothetical examples, and unverified claims as such.
5. If the answer would create durable guidance, open or link a Git issue rather
   than letting the answer become an unreviewed canonical rule.

Do not answer a question with model-release chatter, generic tool lists, or a
claim that an approach will work in the questioner's context. Questions about
private data, credentials, proprietary inputs, or security-sensitive systems
need a safe abstraction or an eligible human, not an agent request for details.

## Artifact review

The review owner verifies the work itself. Approval is never delegated to the
author or an agent.

### Review checklist

- The issue or pull request names the Practitioner problem and the smallest
  useful change.
- The change fits a defined artifact type and its applicable schema or
  template; a reusable Practice states inputs, method, output, evaluation, and
  failure modes appropriate to its maturity.
- Claims distinguish evidence, interpretation, hypothesis, and personal
  experience. Current technical claims have a primary source and an as-of date.
- Links resolve, attribution and license notices are present where needed, and
  no secrets, personal data, client-confidential material, or unlicensed
  content is included.
- The change is model-agnostic unless a tool-specific example is clearly only
  an example; it does not broaden Practice into a non-goal.
- Required tests or validation have run, or the record states exactly what was
  unavailable and why.
- The scope is reviewable. Out-of-scope improvements become a separately owned
  issue rather than blocking a useful small change.
- A human maintainer records `merge`, `request changes`, `redirect`, or
  `decline`, with a concise reason and links to any follow-up.

If a claim lacks evidence, keep it only when it is honestly framed as a
proposal, question, hypothesis, or personal experience and is otherwise safe.
Otherwise request removal or correction. Do not turn a weak contribution into a
conduct case unless behavior independently meets the Code of Conduct.

## Agent-assisted work and review

An agent assignment is a bounded draft or inspection task. The requesting human
maintainer creates a reviewable packet before acting on its output:

- exact task and allowed files or channels;
- source artifacts or links the agent may use;
- agent identity, permissions, and any tools used;
- output, including uncertainty, missing evidence, and external claims;
- checks run and their results; and
- the human reviewer's accept, revise, reject, or escalate decision.

### Human review checklist for agent output

- Compare each material claim, link, quote, and instruction against the named
  source; remove invented facts, results, citations, or capabilities.
- Check that the output did not reveal sensitive information, request secrets,
  or exceed assigned file, channel, or access scope.
- Verify the output did not silently decide moderation, access, policy,
  licensing, governance, or release status.
- Run relevant validation and inspect the actual diff or proposed action.
- Make the human decision in the affected Git record. If accepted, preserve the
  human-reviewed version, not an uninspected agent transcript as canonical
  evidence.

Stop an agent task when its premise is ambiguous, evidence is unavailable, it
needs expanded access, it produces unsafe or unsupported material, or the next
step is a human-reserved decision. Preserve only the minimum safe review record,
then route the question to the owner. Never give an agent the owner private key,
passwords, recovery codes, or provider secrets.

## Releases

A merge is not automatically a release. A human release owner opens a bounded
`RELEASE` item and checks the candidate before any public announcement.

### Release checklist

- Every included change is merged and has a durable Git record; no unmerged
  draft is described as complete.
- The release names what changed, who it helps, the evidence or limitations
  that matter, and a route to the canonical artifacts.
- Relevant validations, links, licenses, attribution, and artifact metadata
  have been checked. Exceptions are explicit and have the required human
  approval.
- There are no unresolved safety, privacy, access, conduct, or critical stale
  content concerns tied to the release.
- The release owner, final announcement owner, and any owner-gate decision are
  named. An agent may draft notes but may not publish or make commitments.
- The Git release record is created first; then an authorized human publishes a
  concise Buzz announcement that links to it.

If a release needs a correction, stop promotion, record the problem in the
release item, and decide whether to amend, withdraw, or publish a visible
correction. Do not silently replace a material public claim. See the
[Release Editor boundary](../buzz/agents/RELEASE_EDITOR.md) for the agent role.

## Moderation and safety

Use the [moderation model](../community/MODERATION.md) and
[Code of Conduct](../CODE_OF_CONDUCT.md) as the complete conduct procedure.
The operational rule is simple: quality feedback stays in the normal review
queue; a possible conduct concern is preserved and routed privately to a human.

### Human triage checklist

1. Check immediate safety, privacy, or credible retaliation risk and notify an
   eligible human moderator. A human may take a temporary protective action;
   an agent may not.
2. Preserve the smallest necessary record: original links, timestamps,
   supplied evidence, requested confidentiality, conflict disclosures, and
   the risk assessment. Do not publish sensitive details.
3. Classify the item as quality, conduct, or mixed. Handle quality work and
   behavior separately.
4. Record the human owner, conflict route, next action, and any review point.
   The moderator makes and communicates the outcome; appeals go to an eligible
   human who did not make the original decision.

If no eligible human is available, tell the reporter that promptly when safe,
record the coverage gap privately, and route it to the founder. Do not let an
agent fill the role or promise an outcome or timeline.

## Stale content and deprecation

Review content when a broken link, changed prerequisite, failed evaluation,
obsolete technical claim, unsafe method, new contrary evidence, or maintainer
gap is reported. Treat the report as a review trigger, not proof that the
artifact is wrong.

### Staleness checklist

1. Open a Git record with the artifact, trigger, affected claim or step,
   evidence, and review owner.
2. Re-check the stated scope, sources, links, versions, evaluation, and current
   claims. Record what could not be verified.
3. Choose the smallest honest disposition: correct, clarify a limitation,
   return to draft or proposed status where its schema permits, deprecate, or
   retain unchanged with a recorded rationale.
4. For a deprecation, preserve the artifact and prior evidence, add the schema's
   required date and reason, and link a replacement only when one exists. Do
   not delete history or imply the old artifact was proven effective.
5. Review artifacts that depend materially on the changed work and link their
   decisions. Announce a material change when Practitioners could otherwise
   follow unsafe or obsolete guidance.

An agent may find links, collect a packet, and propose a disposition. A human
maintainer decides the status change and verifies its effects on dependent work.

## Backups, continuity, and restoration

The repository's Git history is the durable public record, but it is not a
substitute for a continuity plan. The founder maintains the private succession
and recovery record required by [Governance: Succession and continuity](../community/GOVERNANCE.md#succession-and-continuity).
It identifies a willing human successor or interim steward, transfer steps, and
where recovery instructions are held. It contains no secrets in this repository.

### Continuity check checklist

- Confirm the canonical repository is available from a clean checkout and the
  relevant validation command can run.
- Confirm a recent recovery record exists in its approved private location;
  record only the completion of this check in a safe maintainer item.
- Confirm a named human owns moderation and access decisions and that a conflict
  or absence has a documented escalation route.
- Confirm owner identity backup and recovery instructions are kept offline as
  required by the Owner Gates. Do not ask anyone to paste or transmit keys.
- Reconcile the Git release record with public announcements so a future
  maintainer can identify the canonical version.

### Recovery procedure

For a lost account, missing access, suspected identity compromise, or an
unavailable maintainer: pause privileged changes; preserve non-sensitive facts
and timestamps; contact the founder or documented continuity owner through an
independent trusted route; use the approved private recovery procedure; then
review access, moderation ownership, and outstanding decisions before resuming.
Do not "repair" access by sharing credentials, private keys, or recovery codes
in Buzz, Git, chat, or an agent prompt.

For a damaged or missing canonical artifact: restore the last known-good Git
revision through normal review, validate it in a clean checkout, record the
restoration decision, and publish a correction when public guidance changed.
For a Buzz bootstrap or channel-configuration problem, stop automated changes
and follow the inspection and failure handling in the
[Buzz bootstrap runbook](../buzz/BOOTSTRAP_RUNBOOK.md); it does not authorize
deletion, member removal, or an agent-made access decision.

## Owner gates

The following actions remain with Dakota or another explicitly authorized human
before public launch. A maintainer may prepare evidence and a recommendation,
but must create an `AWAITING-HUMAN` item rather than imply the gate is cleared.

| Owner gate | Prepare | Human action required |
| --- | --- | --- |
| Buzz community address and relay URL | Dry-run bootstrap evidence and the intended address. | Create or confirm the hosted Buzz community and authorize application. |
| Owner identity backup | Safe confirmation that a continuity check is due or complete. | Back up the Buzz identity offline. |
| GitHub destination | Repository readiness and destination options. | Confirm the publication destination. |
| License confirmation | Inventory of content and code licenses. | Accept Apache-2.0 for code and CC BY 4.0 for content, or explicitly change the decision. |
| Public invitation path | Proposed wording and safe public links. | Approve the invitation route. |
| Initial community-agent providers | Bounded role, permissions, and estimated operational need. | Select providers and add credentials privately. |
| Launch date | Release-readiness evidence and unresolved risks. | Set the date after release validation. |
| Brand mark | Text-only launch materials. | Approve a mark if one is added; launch uses text only by default. |

Never delegate creating or recovering the owner Buzz identity, storing or
entering the owner private key, final moderation action, license or governance
acceptance, final launch publication, or adding billing credentials or provider
secrets. The authoritative list is [Owner Gates](../docs/OWNER_GATES.md).

## Failure and recovery table

| Failure signal | Immediate action | Recovery record and owner |
| --- | --- | --- |
| Inbox overload or an unowned item | Stop trying to answer everything; triage safety first, deduplicate, and give remaining entries `NEEDS-CONTEXT` or a named owner. | Maintainer queue lists the backlog owner and next check point. |
| Unsupported, unsafe, or scope-exceeding agent output | Stop the task; do not merge, publish, or reuse the output as evidence. | Requesting human records the defect, safe retained context, and whether to revise, reject, or escalate. |
| Bad or incomplete merge | Stop release promotion; open a correction record and assess affected artifacts or claims. | Human maintainer restores or corrects through a reviewed Git change and links any public correction. |
| Public privacy, secret, or security exposure | Limit further spread; preserve the minimum evidence; alert an eligible human immediately. | Human owner follows the relevant security or moderation process and records only safe details. Agents do not investigate private data. |
| Conduct report, retaliation concern, or moderator conflict | Move the matter to private human triage and protect immediate safety. | Moderation record names the eligible owner, conflict route, action, and review point. |
| Release announcement conflicts with Git or contains an error | Stop further promotion and use the Git record to establish the actual state. | Release owner issues a visible correction or withdrawal when needed. |
| Artifact is stale or a current claim cannot be verified | Do not repeat the claim; create a stale-content review record. | Artifact maintainer corrects, limits, returns to review status, or deprecates under the schema. |
| Lost access or continuity gap | Pause privileged changes and use the approved private recovery route. | Founder or continuity owner records the access review and resumption decision without secrets. |

## Handoff between maintainers

When responsibility changes, the outgoing or assigning maintainer leaves a
short queue handoff: artifact or case link, current state, evidence already
checked, open risk, exact next action, decision boundary, and new human owner.
The incoming maintainer confirms receipt in the same durable record. This is
enough continuity for routine work; a role, permission, or governance change
still uses the applicable human approval path.
