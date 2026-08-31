# First ten flagship content briefs

## Purpose and production rule

These briefs turn Practice's thesis into a progressive public program: start
with real work, make its context visible, redesign the workflow with human
review, verify a bounded system change, and make an accountable operating
decision. They are briefs, not reports of completed events, participants, or
outcomes.

Each item is publishable only when its companion canonical artifact is opened
or improved in Git and its claims carry the maturity they have earned. A host
may use a synthetic, safe-to-share example to demonstrate a method, but must
label it **hypothetical** and may not present it as participant evidence. Never
ask contributors to share secrets, personal data, or client-confidential
material. Use a redacted description or stop the session when the work cannot
be safely discussed in public.

The named Buzz route is where the live discussion belongs; the Git artifact is
the durable source of truth. A single content item may be a written post,
recorded walkthrough, or live session, but the artifact and its review gate are
the same across formats.

## Sequence at a glance

| # | Format | Primary use case | Capability move | Canonical contribution required before publication |
| --- | --- | --- | --- | --- |
| 1 | Workflow Clinic | Individual recurring task | Learn → Use | Safe-to-share task-and-risk Note or Guide correction |
| 2 | Practitioner walkthrough | Individual recurring task | Use | Context-pack Practice example or correction |
| 3 | Method Trial | Individual review task | Use → Automate | Verification-gate trial record or improvement |
| 4 | Workflow Clinic | Operator or founder workflow | Automate | Workflow map and proposed redesign record |
| 5 | Build With Me | Engineering implementation | Build | Reproducible Lab, Project contribution, or implementation Note |
| 6 | Build With Me | Engineering review boundary | Build | Verification fixture, test, or Practice improvement |
| 7 | Making Companies AI-Native | Founder opportunity choice | Transform | Safe-to-share opportunity-map Note or Guide correction |
| 8 | Making Companies AI-Native | Organizational pilot design | Transform | Safe-to-share pilot operating-model Note or Guide correction |
| 9 | Community showcase | Any real, reviewable implementation | Use / Automate / Build / Transform, as evidenced | Evidence-grounded Story, Lab, Project, or Practice improvement |
| 10 | Community showcase | Failure, correction, or reproduction | Applicable controlled capability | Corrected canonical artifact and linked evidence record |

## 1. Workflow Clinic — Pick one task worth improving

**Audience and route:** Individual Practitioners; `start-here` for orientation,
then `learn` or `use` for the working thread. This is the entry point for
someone who has a real task but no settled AI use case.

**Hook:** “Before choosing a model or tool, can you name one recurring task,
the person accountable for its outcome, and the point where a wrong answer
matters?”

**Practitioner outcome:** The Practitioner leaves with a bounded task-and-risk
brief: intended output, allowed inputs, prohibited data or actions, acceptance
check, reviewer, and stop condition. The outcome is a better decision about
whether AI assistance is appropriate, not a promise to automate.

**Demonstration:** The host completes the Guide's Module 1 worksheet against a
clearly labeled hypothetical task, such as drafting an internal meeting brief
from approved notes. Show the system trace and reject one version that lacks a
source boundary or review point. Invite a live Practitioner only if they can
share a safe, redacted task; otherwise keep the demonstration hypothetical.

**Artifact produced:** A new or improved canonical **Note** containing the
safe-to-share task-and-risk brief, or a correction to
[`guides/ai-native-practitioner/01-foundations.md`](../../guides/ai-native-practitioner/01-foundations.md).
Completing a private worksheet is not itself a public contribution. Publication
gate: link the actual Git change and label unrun work `proposed`; when the work
cannot be shared safely, keep the session private.

**Community prompt:** “Post one task in this shape: outcome · current input ·
consequence if wrong · what must stay human-owned. Ask for help narrowing the
boundary, not for a tool recommendation.”

**Repurposing:** Turn the opening decision rule into a short `start-here`
orientation post, publish the blank worksheet as a carousel or one-page PDF,
and summarize recurring questions as a follow-up Note proposal.

## 2. Practitioner walkthrough — Make recurring context inspectable

**Audience and route:** Individual Practitioners and operators in `use`.

**Hook:** “If another authorized person had to repeat this task tomorrow,
could they find the instructions, controlling sources, constraints, and the
check without asking you?”

**Practitioner outcome:** A Practitioner can assemble a minimal context pack
for one recurring task and knows that it needs an owner, source freshness
status, and an acceptance check—not a larger prompt.

**Demonstration:** Build the six-section minimal pack from
[`practices/001-context-pack.md`](../../practices/001-context-pack.md) in real
time using only public, hypothetical material. Add a conflicting source and
show the pack's escalation rule rather than choosing a fact by intuition.

**Artifact produced:** A Git contribution that adds an approved,
safe-to-share worked example, edge case, or clarification to the Context Pack
Practice; if the method cannot yet be generalized, publish a context-pack
**Note** with inputs and uncertainty. Publication gate: the artifact contains
no confidential source content and names its freshness limitation.

**Community prompt:** “What is one source your recurring task depends on, who
owns it, and what should happen if it conflicts with another source? Share the
structure, not private contents.”

**Repurposing:** Extract the source-register and escalation fields into a
checklist post for `use`; cut the conflicting-source moment into a short video;
link the resulting examples from the Practice's variations or failure modes.

## 3. Method Trial — Can the verification gate refuse weak work?

**Audience and route:** Individual Practitioners, reviewers, and operators in
`use` and `automate`.

**Hook:** “A polished answer is not an acceptance record. What evidence would
make you revise it before it reaches anyone else?”

**Practitioner outcome:** The Practitioner can use the Verification Gate to
tie acceptance criteria to observable checks, preserve `unknown`, and keep a
reversible path before accepting a bounded artifact.

**Demonstration:** Use an openly available or purpose-built sample artifact.
Run the gate from [`practices/003-verification-gate.md`](../../practices/003-verification-gate.md)
against one unsupported claim or intentional failing check. The host must show
the `revise` decision and baseline preservation; do not claim a passing result
unless a real, reproducible record supports it.

**Artifact produced:** A reproducible **Lab** or a safe-to-share verification
trial record that improves the Verification Gate with an observed edge case,
test fixture, or clarified criterion. Publication gate: record the exact
artifact version, expected and observed result, limitations, and human review
decision.

**Community prompt:** “Bring one review criterion that sounds important but
cannot yet be checked. What observation, source, or test would make it
actionable?”

**Repurposing:** Publish the redacted gate record as a `learn` template, make
a short “pass/fail/unknown” explainer, and invite reproductions or corrections
to the linked Lab rather than collecting anecdotes in the thread.

## 4. Workflow Clinic — Redesign the work before automating it

**Audience and route:** Operators, founders, and service leaders in `automate`.

**Hook:** “Which step actually needs AI, and which one should remain
deterministic or human-owned?”

**Practitioner outcome:** The Practitioner has a visible map of one recurring
workflow, including trigger, steps, exceptions, owners, data boundary,
approval, stop condition, and recovery path. They choose a smallest safe
experiment rather than an autonomous rollout.

**Demonstration:** Facilitate a clinic using a volunteer's safe summary only
after consent, or use a hypothetical workflow if none is appropriate. Map one
normal run and one exception, then classify each step using
[`practices/002-workflow-redesign.md`](../../practices/002-workflow-redesign.md).
Keep any sending, spending, record changes, and consequential decisions
human-owned in the example.

**Artifact produced:** A redacted workflow-map **Note**, a proposed redesign
record, or an improvement to the Workflow Redesign Practice driven by a
generalizable failure mode. Publication gate: the artifact names the boundary,
permissions, reviewer, stop trigger, and rollback owner; it contains no client
or employee case data.

**Community prompt:** “Share a workflow at this level: trigger · outcome ·
steps that repeat · exception · who approves the effect. Which step is most
ambiguous, not merely most time-consuming?”

**Repurposing:** Make a short founder-facing diagram of the four
classifications, publish the blank experiment card in `automate`, and collect
clinic decisions as candidates for future Practice variations.

## 5. Build With Me — Implement the smallest reviewable boundary

**Audience and route:** Engineers and builders in `build`.

**Hook:** “Can we turn one approved workflow slice into a change that another
engineer can inspect, test, and disable?”

**Practitioner outcome:** The Practitioner can convert a workflow boundary
into a small implementation brief with ownership, permissions, tests, and a
recovery path. The goal is a reviewable change, not a live agent demo.

**Demonstration:** Start from a public or hypothetical workflow map. Specify a
single deterministic validation or draft-only interface, then build the
smallest implementation in a public repository or disposable sandbox. Show
the exact diff, an expected test, a failure or unauthorized-input test, and
how to disable the change. Do not connect private systems or use production
credentials on camera.

**Artifact produced:** A canonical **Project** contribution, **Lab** with
reproduction instructions, or implementation **Note** that includes the
boundary, setup, test evidence, and disablement/rollback instructions.
Publication gate: a reviewer can inspect the change and reproduce the listed
checks; otherwise publish the implementation brief as proposed rather than a
working-system claim.

**Community prompt:** “What is the smallest boundary you could implement with
one allowed input, one observable output, and one explicit failure response?”

**Repurposing:** Break the build into a technical design note, a code-review
checklist, and short clips on scope, permission-boundary, and rollback tests;
route critique to the linked Git issue or pull request.

## 6. Build With Me — Turn a failure into a reusable test

**Audience and route:** Engineers, builders, and reviewers in `build`.

**Hook:** “A system passed the happy path. What test would expose the failure
that is still most likely to matter?”

**Practitioner outcome:** The Practitioner can translate a specific observed
or intentionally constructed failure into a fixture, expected behavior,
evidence record, and change proposal. They learn not to use a green test as a
claim of general reliability.

**Demonstration:** Choose a public issue, a completed Lab, or a deliberately
constructed non-sensitive failure. Trace it to an acceptance criterion; add a
boundary, malformed-input, permission, or stale-context test; and show the
result before and after the bounded fix. If no real system is available, mark
the entire exercise hypothetical and publish only the test-design Note.

**Artifact produced:** An improved canonical **Lab**, **Project** test, or
Verification Gate Practice update with a fixture and stated limitation.
Publication gate: the artifact preserves the failure description, expected
behavior, observed result, and the scope of what the test does not establish.

**Community prompt:** “Name one failure mode in this form: condition → wrong
behavior → consequence → detection. What is the smallest reproducible test?”

**Repurposing:** Produce a `build` thread with the fixture, a short failure
taxonomy graphic, and a maintainer-oriented review prompt that asks for an
additional boundary case rather than praise for the fix.

## 7. Making Companies AI-Native — Choose the first opportunity without an ROI story

**Audience and route:** Founders, internal AI champions, transformation leads,
and executives in `transform`.

**Hook:** “Which operating problem is safe and specific enough to investigate
before anyone promises savings, headcount change, or a platform purchase?”

**Practitioner outcome:** The Practitioner can compare candidate workflows by
outcome, reviewability, knowledge/access readiness, reversibility, role
readiness, and evidence feasibility. They leave with one bounded next
decision, not a generic AI roadmap.

**Demonstration:** Use the opportunity-map exercise in
[`guides/ai-native-practitioner/06-organizational-ai.md`](../../guides/ai-native-practitioner/06-organizational-ai.md)
against a hypothetical company scenario. Mark unknown baseline and cost fields
as `unknown`; demonstrate why a high-consequence, unreviewable candidate is
deferred even if it sounds valuable.

**Artifact produced:** A canonical organizational opportunity-map **Note** or
an improved Guide worksheet/example, explicitly labeled proposed unless it
contains authorized observation. Publication gate: every candidate has an
owner, a reason to test, narrow, defer, or keep human-owned, and no unsupported
business result.

**Community prompt:** “Post one candidate workflow with: operating outcome ·
review point · allowed knowledge · consequence if wrong · smallest next
decision. What evidence is still unknown?”

**Repurposing:** Create a founder memo template, an executive briefing clip,
and a `transform` discussion that compares decision readiness rather than tool
lists or vendor claims.

## 8. Making Companies AI-Native — Design the pilot around changed work and decision rights

**Audience and route:** Transformation leads, founders, operators, and
executives in `transform`.

**Hook:** “If this pilot changes a role's work, who now owns the source,
review, exception, and decision—and what can they stop?”

**Practitioner outcome:** The Practitioner can produce a bounded pilot
operating model that names roles, authority, allowed data, review queue,
measurement ledger, escalation, and recovery. The pilot may remain proposed;
organization-wide rollout is out of scope.

**Demonstration:** Continue the hypothetical opportunity from Brief 7. Compare
the current and proposed operating model, make the changed work visible for
operator, reviewer, source steward, and decision owner, then design one
review-only pilot. Show a stop condition and correction path before discussing
any measure.

**Artifact produced:** A canonical proposed pilot operating-model **Note** or
a Guide improvement containing the role/decision-right and measurement
worksheets. Publication gate: the artifact distinguishes proposal, adoption,
capability, workflow observation, and measured outcome; it does not assert
return on investment.

**Community prompt:** “Which decision right would move or become visible in
your pilot? State the role, evidence it needs, and one condition that lets it
pause the work.”

**Repurposing:** Adapt the role table into a workshop handout, a short series
on source stewardship and stop authority, and a maintainer prompt for
reviewing governance gaps in proposed pilots.

## 9. Community showcase — Show the evidence, not the victory lap

**Audience and route:** Any Practitioner with a real, safe-to-share
implementation in `showcase`; route technical implementation detail to `build`
and operating-model detail to `transform`.

**Hook:** “What changed in a real implementation, what evidence supports that
claim, and what should the next Practitioner not assume from it?”

**Practitioner outcome:** A contributor can turn a real implementation into a
reviewable Story, Lab, Project update, or Practice improvement without
overstating its result. Readers can locate the reusable artifact and its
limitations.

**Demonstration:** Publish only with a consenting contributor who can provide
safe-to-share evidence, or use a previously public artifact as an annotated
example. Walk through the showcase structure: before · constraint ·
intervention · implementation · after · result · evidence quality · lessons ·
reusable artifact. Decline the showcase if the contribution cannot meet that
structure without exposing protected information.

**Artifact produced:** An evidence-grounded canonical **Story**, **Lab**,
**Project** update, or **Practice** improvement, selected with the taxonomy.
Publication gate: all material claims trace to an artifact, observation, or
source; unmeasured effects remain observations or hypotheses.

**Community prompt:** “Bring one change you can support with a before state,
intervention, and limitation. What reusable artifact can others inspect or
adapt?”

**Repurposing:** Create a written case, an annotated artifact tour, and a
short `showcase` post that links the Git source; extract one bounded lesson to
the appropriate capability channel rather than reposting the full story.

## 10. Community showcase — The correction that made the method better

**Audience and route:** Practitioners who reproduced, reviewed, or found a
failure in an existing artifact; `showcase`, plus the channel matching the
artifact's primary capability.

**Hook:** “What did a reproduction, failed check, or correction reveal that
the original artifact did not make clear?”

**Practitioner outcome:** The Practitioner can make a precise correction that
improves the commons: a source update, clearer boundary, counterexample,
failure mode, test fixture, or versioned revision. The correction earns status
without requiring a success story.

**Demonstration:** Select an open canonical artifact with a genuine, documented
issue or use a hypothetical illustration of the contribution flow. Compare the
prior text or test with the proposed change, show the evidence, and let the
maintainer review decide acceptance. Do not invent a defect merely to create
content.

**Artifact produced:** A merged or reviewable Git contribution that corrects a
canonical **Practice**, **Guide**, **Lab**, **Story**, **Note**, or **Project**;
the linked issue or evidence record explains the change. Publication gate: the
showcase names the original limitation, the verification performed, and any
remaining uncertainty. If review is pending, say `proposed change` rather than
claiming the artifact is improved.

**Community prompt:** “What is one claim, step, source, or test in an open
artifact that you can make more precise? Link the evidence and propose the
smallest reviewable revision.”

**Repurposing:** Publish a maintainer-facing change log note, a short
reproduction/correction walkthrough, and a contribution guide excerpt that
normalizes negative results and careful revisions as community work.

## Editorial and release checklist

Before producing or publishing any brief:

- Confirm the companion artifact type with
  [`docs/framework/TAXONOMY.md`](../../docs/framework/TAXONOMY.md), then link
  the exact Git path, issue, or pull request.
- Separate a demonstration from a real participant contribution. Label
  hypothetical, proposed, observation, and measured result accurately.
- Obtain explicit consent for any contributor story; remove protected details
  by default and do not publish a case that cannot be safely abstracted.
- Require human review before any public, merged, deployed, or consequential
  result. A host or agent may prepare the artifact but may not self-approve it.
- Route discussion to the outcome channel and keep the reusable record in Git.
- Close each item with one bounded community prompt that can become a Note,
  Practice, Guide improvement, Lab, Story, or Project contribution.
