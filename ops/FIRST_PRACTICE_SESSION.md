# First Practice Session: Workflow Clinic

## Outcome

Run one repeatable, live **Workflow Clinic** that helps a Practitioner turn a
safe-to-share recurring workflow into a concrete **draft Practice artifact**.
The session produces a versioned draft, not a claim that the method works or a
commitment to automate it. The default artifact maturity is `proposed` with
`evidence_quality: none` unless independently reviewable evidence supports a
different classification under the [Practice schema](../docs/schemas/PRACTICE_SCHEMA.md).

The clinic is appropriate for a bounded workflow with a named outcome and
owner. It is not consulting, a product demonstration, a substitute for domain
controls, or a place to disclose client, employee, patient, account, or other
restricted information. A hypothetical workflow is the default demonstration
when no safe participant workflow is available.

## Non-negotiable operating rules

- Start from a summary, not source documents. Do not request or accept secrets,
  credentials, private keys, personal data, client-confidential material,
  private attachments, recordings, or system access.
- Keep sending, spending, system-of-record changes, access changes, and
  consequential decisions human-owned. The clinic may map those steps; it does
  not perform or approve them.
- Treat live discussion, a draft, and publication as separate permissions.
  Participation never implies recording, attribution, publication, or a right
  to reuse a participant's private context.
- Use Git for the reviewable artifact. Buzz may host an optional working
  discussion, but no scheduled workflow, automated forum post, or agent action
  is required.
- Stop rather than sanitize in public when the host cannot confidently separate
  the workflow structure from restricted information.

## Roles and boundaries

| Role | Accountable for | May do | Must not do |
| --- | --- | --- | --- |
| **Host (human)** | Safe session operation, selection, facilitation, and escalation | Explain boundaries; pause or end a discussion; use a hypothetical substitute; coordinate the review packet. | Request restricted material; decide publication alone; promise outcomes; make domain, access, moderation, or governance decisions for a participant. |
| **Practitioner** | Their workflow description and permission choices | Supply a minimal safe summary; correct the map; approve or decline each consent choice; review a proposed public abstraction. | Treat the clinic as professional advice or disclose information they are not authorized to share. |
| **Steward** | Routing and bounded orientation | Screen the non-sensitive intake for route fit; provide one next action; identify an escalation. | Handle private data, choose participants, make access or moderation decisions, publish, or represent a draft as approved. |
| **Librarian** | Faithful, attributable artifact capture | Turn the agreed safe notes into a structured draft; identify the appropriate artifact type; link sources and disagreement; ask the Practitioner to verify its interpretation. | Publish private material, erase disagreement, invent evidence or consensus, merge its own draft, or decide publication. |
| **Research Auditor** | Accuracy of material current technical claims | Check each such claim against a primary source; record source URL, retrieval/as-of date, support, and uncertainty; recommend narrowing or removal. | Invent citations, rely on a search snippet when a primary source is available, broaden a claim beyond its source, or certify an operational result it did not observe. |
| **Human reviewer / maintainer** | Acceptance and publication decision | Review the exact draft, provenance, consent record, license/attribution, and scope; accept, request revision, reject, or keep private. | Infer consent from attendance or let an agent make the final publication decision. |

The Host may also be the human reviewer only when that person documents the
separate review pass. The Steward, Librarian, and Research Auditor may be
humans or agents operating within their published role boundaries; a human
remains accountable for all decisions in the last row.

## Intake and selection

### 1. Use a minimal, safe intake

The Host or Steward asks for the following in a form, message, or conversation.
The response must be a structural summary; do not collect raw documents or
identifiers.

| Ask | Safe response shape | Decision it supports |
| --- | --- | --- |
| Recurring work | “Weekly internal status-brief drafting” | Whether the work recurs and can be mapped. |
| Outcome and accountable role | “A lead approves a concise brief for an internal team.” | Boundary and human owner. |
| Trigger, broad steps, and one exception | “Approved summary arrives; draft; review; correction if source conflicts.” | Map normal and exception paths. |
| Data boundary | Categories only, such as “approved internal summaries; no personal data.” | Whether a safe discussion is possible. |
| Consequence if wrong | A plain-language category, such as “misleading internal prioritization.” | Risk and review depth. |
| What must remain human-owned | For example, approval and external communication. | Classification and stop boundary. |
| Permission to participate | `yes`, `no`, or `need more information`. | Whether to proceed live. |

Do not ask for names, organization, account, ticket, customer, employee,
financial, health, security, legal, authentication, or proprietary-product
details. A person who needs help deciding whether a detail is safe should omit
it and ask a responsible human in their own context.

### 2. Screen before accepting

The Host checks all of the following:

- The work is recurring enough to describe a normal run and an exception.
- A named accountable human owns the outcome and can keep consequential
  decisions human-owned.
- The proposed discussion can use a structural summary without restricted
  information.
- The intended artifact is a reusable method, variation, failure mode, or
  evaluation design—not a disguised case study or a tool recommendation.
- A small, reversible, low-risk next step could be designed, even if it is
  never run.

Accept when all checks are true. If a check is unknown, ask one bounded
clarifying question or offer the hypothetical demonstration. Decline the live
workflow when any sensitive or unsuitable condition below applies; declining is
not a judgment about the Practitioner or the value of their work.

### 3. Send the preparation packet

For an accepted workflow, the Host sends a plain-language packet containing:

1. The purpose, boundaries, and no-recording-by-default rule.
2. The exact consent choices in the next section, with `decline` and `withdraw
   before publication` options.
3. A blank, safe workflow-map outline: trigger, outcome, roles, steps,
   exception, allowed data categories, review point, stop condition, and
   recovery owner.
4. The [workflow-redesign Practice](../practices/002-workflow-redesign.md) and
   a request to read only the boundary and inputs sections if time is limited.
5. A reminder to bring no raw records, screenshots, credentials, or files. The
   Practitioner may replace every real detail with a category or placeholder.

The Host prepares a hypothetical fallback and a blank artifact branch or draft
file. No participant material is copied into the repository before the session.

## Consent and decline record

At the opening, the Host restates that each choice is independent and records
only the choices, date, artifact identifier, and responsible Host. Store no
private workflow details in this record.

| Choice | Default | If declined |
| --- | --- | --- |
| Participate in the live mapping | No until affirmative agreement | Use the hypothetical workflow or end the person's segment. |
| Capture notes needed for a draft | No until affirmative agreement | Give the Practitioner the blank template; do not retain notes. |
| Attribute the contribution by a chosen public name | No | Use no attribution or do not publish, as the Practitioner chooses. |
| Record audio/video or share a transcript | No | Do not record, retain, or distribute a recording/transcript. |
| Submit the redacted draft for publication review | No | Keep it private to the Practitioner, or discard it at their direction. |

Before a draft enters publication review, show the Practitioner the exact
redacted text and ask for a separate affirmative `submit for review` decision.
They may decline without explanation or withdraw that submission before the
publication decision. A withdrawal stops review and publication; the Host
removes the draft from the review queue and follows the agreed retention action
(return, delete from the working location, or retain only where the
Practitioner is authorized to retain it). Once material is merged or otherwise
public, do not promise erasure; route any correction, attribution, or removal
request to a human maintainer under the applicable policy.

## Facilitation run of show

This sequence is repeatable at any reasonable live-session length. The Host
protects the order; if time is short, finish a smaller map rather than skipping
the safety or review steps.

1. **Open and confirm boundaries.** State the outcome, no-share rules, roles,
   consent choices, and stop signal. Confirm whether the case is participant
   supplied, redacted, or hypothetical. If consent is absent, use hypothetical.
2. **Set the workflow boundary.** Complete: “When `[trigger]` occurs,
   `[owner]` produces `[outcome]` for `[recipient]` using `[allowed systems or
   categories]` within `[constraint]`.” State exclusions and irreversible
   effects. Mark unknowns as `unknown`.
3. **Map a normal run and one exception.** Capture only roles, categories, and
   transitions. Include waits, handoffs, checks, corrections, and recovery.
   The Practitioner may say “stop” at any point; the Host then removes the
   detail from shared notes and either abstracts further or switches examples.
4. **Classify and assign ownership.** For every step, choose one primary class:
   deterministic, AI-assisted, agentic, or human-owned. Record why. Keep
   approvals, consequential recommendations, external sends, spend, access,
   and record changes human-owned unless a separate responsible authority has
   approved another arrangement; that authority is outside this clinic.
5. **Design gates, not a rollout.** Record allowed data categories, least
   privilege, risk consequence, required human approval, observable stop
   condition, rollback or recovery owner, and audit record. A missing stop or
   recovery path keeps the step human-owned.
6. **Choose the smallest safe experiment.** Select one low-risk, reversible
   slice or explicitly decide `no experiment`. Define its sample/volume cap,
   output acceptance check, reviewer, decision date, and `continue`, `revise`,
   or `revert` criteria. The clinic does not run it.
7. **Read back and decide artifact direction.** The Host reads the map and
   unknowns. The Librarian proposes: a draft Practice variation/improvement,
   a Note, or no public artifact. The Practitioner corrects inaccuracies and
   chooses whether to take the draft privately or submit the redacted draft for
   review.

Use the [Workflow Redesign Practice](../practices/002-workflow-redesign.md) as
the method source. Do not present its proposed status as tested evidence.

## Artifact capture and handoff

### Required session record

The Librarian creates a session record with a non-identifying ID and a clear
label: `hypothetical`, `participant-supplied redacted`, or `private not for
publication`. It contains only:

- boundary statement and exclusions;
- normal-run map and one exception, using roles and categories;
- classification and human-ownership rationale for each step;
- allowed-data categories, approvals, stop condition, recovery owner, and
  unknowns;
- smallest-safe-experiment design or the reason no experiment is proposed;
- artifact direction and all consent choices; and
- correction requests, open questions, and the next human owner.

The session record is not public by default. Keep restricted source material in
the participant's approved system, not in the record, chat, repository, or an
agent prompt.

### Minimum draft artifact

If the Practitioner submits a draft for review, the Librarian creates the
appropriate draft in the [Practice template](../templates/PRACTICE.md) when
the output is a reusable method. A Practice draft must include a bounded
outcome, scope, inputs, method, expected output, evaluation plan, anticipated
failure modes, evidence state, and a clearly labeled hypothetical example if
one is used. It must not use the participant's story as proof of effectiveness.

The draft may instead be a Note when the material is an observation, a
workflow-specific decision, or an untested question that cannot honestly
generalize. If no durable claim can be made safely, retain no draft and give
the Practitioner the blank workflow map.

The Librarian links the session record only when it is safe and authorized; a
public artifact should normally state the reusable method without linking to a
participant record. The Librarian preserves meaningful disagreement as an
unknown, limitation, or alternative rather than resolving it by assertion.

## Follow-up and publication review

### Manual follow-up

Within the follow-up route chosen by the Practitioner, the Host sends the
redacted draft or blank template, its status, and one next action: correct the
map, confirm consent, run a separately authorized low-risk experiment, or
decline further work. Do not promise a response time or use scheduled
automation. A Steward may route a public, non-sensitive question to the
appropriate channel; it must not post a participant's workflow on their
behalf.

### Publication gate

The human reviewer or maintainer reviews the exact version proposed for
publication and records `accept`, `revise`, `reject`, or `keep private`.
`Accept` requires every applicable check below; a missing check is `revise`,
`reject`, or `keep private`.

- **Consent:** Separate affirmative submission for this exact redacted draft;
  any attribution is exactly as agreed. Declining publication is final for this
  draft and has no adverse participation consequence.
- **Privacy and scope:** A fresh reader cannot recover personal, client,
  employee, customer, credential, internal-system, or other restricted
  information. The artifact contains no raw case materials or claims that it
  is a case study.
- **Artifact quality:** The artifact follows its canonical template and labels
  hypotheses, unknowns, and maturity honestly. For a Practice, it meets the
  [Practice schema](../docs/schemas/PRACTICE_SCHEMA.md), including evaluation
  and failure-mode requirements appropriate to its maturity.
- **Evidence and claims:** The Research Auditor has reviewed every material
  current technical claim against a primary source, recording its URL and
  as-of date. Unsupported, stale, or non-generalizable claims are removed,
  narrowed, or labeled unknown. No outcome is inferred from completing the
  clinic or producing a map.
- **Attribution and rights:** The reviewer verifies the contributor's right to
  submit the material, required source attribution, and the applicable content
  license using the [Attribution and Reuse Policy](../community/ATTRIBUTION.md).
  Unclear rights mean no publication.
- **Safety and ownership:** Consequential decisions remain human-owned; the
  proposed experiment has an explicit review, stop, and recovery path. Any
  needed legal, clinical, financial, security, privacy, HR, or other domain
  review is identified as outside the clinic and complete before publication
  only when the responsible authority has actually confirmed it.

Publish only the reviewed Git version. Link the optional live discussion only
if it independently meets the same privacy and consent requirements. The Host
notifies the Practitioner of the recorded decision without claiming that
publication validates their workflow or produces a measured result.

## Sensitive, unsuitable, and disruption contingencies

| Signal | Immediate action | Safe disposition |
| --- | --- | --- |
| The workflow involves personal data, credentials, security details, legal/clinical/financial advice, regulated or confidential records, or an ongoing incident. | Stop sharing details. Do not redact live, inspect the material, or ask for a private upload. | Switch to a fully hypothetical analogue, provide the blank map, or direct the Practitioner to their authorized human owner or relevant process. No public artifact from the case. |
| A participant begins disclosing restricted information. | Interrupt kindly, stop capture/recording, and remove the detail from shared notes before continuing. | Continue only with a safe abstraction approved by the participant; otherwise end their segment and use hypothetical material. Escalate a possible exposure to a responsible human through the approved path. |
| No recurring workflow, accountable owner, safe boundary, review point, or recovery path exists. | Do not force an automation design. | Decline the clinic case; produce no Practice draft. Offer a task-and-risk brief, a process-observation step, or a hypothetical demonstration. |
| The work is high-consequence or cannot be reversibly trialed. | Keep every decision and effect human-owned; do not design an autonomous experiment. | Capture only a high-level map or decline. Refer required governance and domain controls to the responsible human authority. |
| Consent is denied, withdrawn, ambiguous, or disputed. | Stop capture, review, and publication for that person's material. | Use hypothetical material or a blank template. Keep no public attribution or artifact based on the material. |
| The draft contains a current claim without primary-source support, an unclear license, or a claim of success without evidence. | Mark it `unknown` and pause publication. | Research Auditor recommends a supported, narrower wording; otherwise remove the claim or keep the draft private. |
| A conduct, retaliation, access, or moderation concern arises. | Do not investigate or decide it in the session; preserve only the minimum safe fact needed to route it. | Move it to private human triage under the [Moderation Model](../community/MODERATION.md). Agents may recommend routing only. |

## Completion criteria

A clinic is complete when it has either:

1. a consented, non-sensitive session record and a concrete, redacted draft
   artifact (normally a `proposed` Practice draft) with an assigned human
   publication-review owner; **or**
2. a documented safe decline or hypothetical substitution, the reason no
   participant artifact was captured, and one next action that does not require
   sharing restricted material.

It is not complete merely because a live meeting occurred, an agent generated
text, or a workflow map looks polished.

## Facilitation checklist

- [ ] Minimal safe intake and selection screen completed.
- [ ] Participation, capture, recording, attribution, and publication choices
      recorded separately.
- [ ] Case labeled participant-supplied redacted, hypothetical, or private.
- [ ] Normal run and exception mapped without raw restricted material.
- [ ] Every step classified; human-owned decisions and review gates named.
- [ ] Stop condition and recovery owner recorded, or no experiment proposed.
- [ ] Librarian captured the appropriate artifact direction without inventing
      evidence or consensus.
- [ ] Research Auditor queued or completed review of material current claims.
- [ ] Practitioner saw the exact redacted draft before any submission.
- [ ] Human reviewer recorded publication decision, or the artifact remained
      private.
