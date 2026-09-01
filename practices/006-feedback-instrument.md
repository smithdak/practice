---
artifact_type: practice
title: "Run a lightweight contributor feedback instrument"
summary: "Collect small, consent-based contributor feedback on one defined question per period with a data-minimal instrument, fixed sampling rules, retention limits, and a named human data owner."
maturity: proposed
capability: use
roles: [operator, internal-ai-champion, individual-practitioner]
version: 0.1.0
license: CC-BY-4.0
created: 2026-09-01
updated: 2026-09-01
evidence_quality: none
secondary_capabilities: [learn]
tags: [feedback, privacy, consent, sampling, retention, measurement]
---

# Run a lightweight contributor feedback instrument

## Outcome

For one review period and one defined question, produce an aggregate feedback record: what was asked, who was sampled under what consent, what respondents said as counts and labeled themes, what the data owner decided or changed because of it, and confirmation that raw responses were deleted on schedule. Individual responses are never published.

This Practice exists to inform a named decision, not to display that feedback was gathered. If no decision is waiting on the answer, do not run the instrument this period.

## Problem and scope

Feedback collection expands by default: one question becomes a survey bank, a free-text field becomes a personal-data store, and a helpful pulse check becomes a recurring obligation respondents learn to dodge or to game. The result is over-collected, stale data and survey fatigue that degrades every later measurement.

The unit of work is one instrument — a short question set aimed at one respondent group — run once per period for one stated decision. This Practice covers designing, sampling, running, aggregating, and deleting that instrument. It does not cover behavioral analytics, telemetry, A/B testing, or any collection requiring identifiers or tracking; those need a separate privacy review. All collection boundaries here follow the community metrics contract in [ops/METRICS.md](../ops/METRICS.md).

## Use when

- A maintainer or operator faces a concrete, nameable decision about contributor experience or process — for example, whether to change an onboarding step or a review cadence.
- The population is small enough to sample honestly (in the tens, not thousands).
- A named human can own the data for the instrument's full lifecycle, including deletion.
- Respondents can participate without risking their standing; declining is visibly safe.

For a one-off question answerable from existing public records — issues, contributions, published artifacts — read the records instead of asking people to answer again.

## Inputs

- One decision question with a named decision owner and the period by which the decision is due.
- A defined respondent group (the sampling frame) the owner can reach through an existing, expected channel — not covert or cross-platform targeting.
- An access-controlled store for responses (shared spreadsheet or Markdown ledger), owned by a named human.
- The privacy rules from the community metrics contract, applied as hard exclusions.
- A consent statement template: purpose, who sees responses, retention window, how to withdraw.

Never collect credentials, client or employer-confidential material, precise location, sensitive demographic or employment details, or any identifier not strictly required for the stated decision.

## Method

1. **Name the decision before the question.** Write: "[Owner] will decide [change or keep X] by [date] based on [the question]." If the sentence cannot be completed, stop. Every instrument field must map to this decision; fields that serve no named decision are cut at design time.
2. **Design data-minimal.** Use closed questions (a small scale plus one optional free-text prompt) and cap the instrument at a few minutes to answer. For each planned field, record what decision it serves and who will see it. Apply the not-to-collect list from [ops/METRICS.md](../ops/METRICS.md): no credentials, confidential pastes, sensitive personal attributes, precise location, covert identifiers, message scraping, or read/engagement proxies. Instruct respondents not to include names, employer, or client details in free text, and provide an anonymous path for those who prefer it.
3. **Fix consent and sampling.** State, where the instrument is presented: purpose, audience, retention window, whether responses are anonymous, and how to decline or withdraw. Choose a fixed, stateable sampling rule — for example, all contributors active in the period when the frame is small, or every *k*-th contributor when it is not — and record the frame size. Sample the same way each period so results stay comparable; changing the rule is a method change that must be noted.
4. **Collect in one bounded window.** Run the instrument once per period with at most one reminder. Participation is voluntary and never tied to standing, privileges, or visibility; there is no leaderboard or list of who responded. Close the window on schedule even if the response count is low — a low count recorded with its denominator is a valid result.
5. **Aggregate and label.** Produce counts with denominators (for example, `7 of 12 invited responded`), labeled themes from free text, and explicit `unknown` entries for non-response. Record the known bias: voluntary respondents are self-selected, so the aggregate describes respondents, not the whole group. Publish aggregates only, through the metrics review; never publish or retain individual rows beyond the retention window.
6. **Decide and record.** The decision owner records what was decided, what changed, or what stays open and why — including "no change." A feedback round that produces no recorded decision was overhead for everyone involved; treat that as a design failure to avoid next period.
7. **Delete on schedule.** After the stated retention window, the data owner deletes raw responses, keeps the aggregate and decision record, and confirms deletion in the owner-maintained record. Access to the response store is limited to the owner and any named assistant during the window only.

**Expected output:** the instrument design with field-to-decision mapping, the consent statement, the sampling record, an aggregate with denominators and labeled limitations, a recorded decision, and a deletion confirmation.

## Evaluation

This is a proposed method; no execution evidence is claimed. Trial it for one period on one real decision. A reviewer who did not run the instrument should be able to answer all of the following from the records alone:

- Was there one named decision and owner, and did every field map to it?
- Does the instrument and consent statement avoid every category on the not-to-collect list, and was an anonymous or declining path stated?
- Does the sampling record state the rule, frame size, and response count with denominator?
- Does the published output contain aggregates only, with self-selection and non-response labeled?
- Did the owner record a decision, and did deletion happen within the stated window?

Accept the trial when every question has a specific, inspectable answer. Do not infer community health, satisfaction, or retention trends from one instrument run; those claims need repeated periods, a stable method, and stated comparisons.

## Implementation

### Minimal: one form, one owner

Use the community's existing survey or form tool, or a plain text reply route. Keep the question set to one page: one scale question, one or two closed questions, one optional free-text prompt. Store responses in an access-controlled spreadsheet owned by a named human, aggregate into the period's metrics review, then delete. The consent statement is three sentences at the top of the instrument.

### Advanced: versioned per-period instrument

Maintain a versioned question set and consent template in the repository, an aggregate ledger aligned with the metrics contract, and a deletion log the owner signs each period. Keep the sampling rule and any method changes in the ledger so period-over-period comparisons are honest. Agents may draft questions, summarize aggregates, and check the instrument against the not-to-collect list; they do not hold raw responses, contact respondents, or report individual answers. If the decision grows beyond what one instrument supports, escalate to a dedicated privacy review rather than expanding collection quietly.

## Failure modes

The following are anticipated failure hypotheses for the first trial:

- **Over-collection:** Fields accumulate because they might be interesting. Consequence: a private-data store with no owner and no purpose, exposed to the next incident. Prevention: field-to-decision mapping at design time; any field without a mapped decision is removed before launch.
- **Survey fatigue:** The same people are asked every period with visible effect on nothing. Consequence: response rates fall and respondents game the questions. Prevention: one instrument per period, tied to a recorded decision, with visible follow-through from the previous round.
- **Leading questions:** Questions presuppose the desired answer ("How much faster did this make you?"). Consequence: the aggregate flatters the process and misdirects the decision. Prevention: neutral phrasing, a genuine "no change / not applicable" option on every scale, and a review of the question set by someone other than the author.
- **Consent drift:** Responses collected for one purpose get reused for another, or the anonymity promise is weakened mid-stream. Consequence: trust damage that no later privacy statement repairs. Prevention: the consent statement travels with the data; new purposes require a new, explicit consent round.
- **Retention creep:** "We'll delete later" becomes never. Consequence: raw responses outlive their window and their risk assessment. Prevention: a stated window at collection, a signed deletion confirmation, and the aggregate — not the raw data — as the durable artifact.
- **Sample mistaken for population:** A 5-response aggregate is read as what "the community" thinks. Consequence: decisions built on noise. Prevention: always publish the denominator and the self-selection caveat; below a stated minimum, record the result as `unknown` rather than interpret it.
- **Free-text deanonymization:** Respondents identify themselves or others in prose, or paste confidential material. Consequence: the anonymity promise breaks or private data enters the store. Prevention: instruct against it at the prompt, review text before aggregation, and exclude or redact identifying content before the aggregate is shared.

## Evidence

Initial maturity is **proposed** and evidence quality is **none**. This repository contains the method and a planned trial only; it contains no completed collection round or measured outcome. What would count as promotion evidence: a recorded single application (for example, a Lab record such as `labs/NNN-feedback-instrument-trial.md`) containing the decision question, the instrument and consent statement as used, the sampling record, the aggregate with denominators and labeled limitations, the recorded decision, and the deletion confirmation — with no individual response data. Promote to `tested` only after a human reviews that record under the Practice schema; a second, comparable period by a different Practitioner using the unchanged method would support `repeated` and, with independent reproduction, `verified`.

## Variations

- An interview-style variant (one short conversation with a handful of contributors) follows the same rules: stated decision, consent, data-minimal notes, aggregate-only output, deletion.
- A period with no decision may run a standing one-question "what blocked you" prompt instead, but it must still have an owner, a consent statement, and a retention window.
- For sensitive topics — conduct, compensation, personal circumstances — this Practice is not sufficient; route to a process with a designated privacy or safety owner.

## Changelog

- **2026-09-01 — 0.1.0:** Proposed a consent-based, data-minimal contributor feedback method with decision-first design, sampling rules, retention limits, a named human data owner, and anticipated failure modes.
