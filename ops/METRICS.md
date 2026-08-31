# Practice health and outcome metrics

Practice exists to help people become more capable of making AI work and to
leave reusable knowledge for the next Practitioner. The north star is **build
the open standard for becoming AI-native**. Measure progress toward that
standard, not attention, message volume, or membership size.

This is a measurement contract for launch. It defines what to look for, what
counts as evidence, and how to review it. It does not set targets or claim
that any result has already occurred.

## Measurement rules

- Count a person, artifact, or event only when a human can point to its source
  in a public Git change, a voluntary contribution record, or a sanitized
  Buzz link. A reaction or view is not evidence of capability.
- Record counts and short evidence links, not a profile of individual
  behavior. Use a Practitioner label or an owner-provided alias when identity
  is needed for follow-up.
- Report a period's count alongside its denominator and the evidence coverage
  (for example, `3 of 8 reviewed contributions`). Do not compare periods when
  the review method changed without noting the change.
- Segment observations by capability stage (Learn, Use, Automate, Build,
  Transform) and artifact type when useful. Keep the overall north-star view
  legible.
- Metrics are signals for learning and maintenance decisions. They are not
  scores for ranking Practitioners.

## Leading and lagging indicators

Leading indicators show that a path or support system is being used and may
lead to capability: a first useful question, a contribution draft, a review,
or a link to a Practice in context. Lagging indicators show durable outcomes:
an implemented workflow, a reusable artifact accepted by another person, or
evidence that a method worked under a stated evaluation.

Do not treat a leading indicator as proof of a lagging outcome. Review both
for the same period and inspect a small, explicitly recorded sample when the
count alone could mislead.

## Metric definitions

The terms below are deliberately defined so launch measurement can use a
spreadsheet or plain Markdown ledger. Each row names the evidence required;
without that evidence, record `unknown` rather than infer a result.

| Metric | Type | Operational definition and evidence | Useful question |
| --- | --- | --- | --- |
| Activation | Leading | A new Practitioner completes an observable first-value action: uses a published Practice, asks a concrete implementation question, or submits a useful improvement. Record the entry source, action, date, and link/alias. A join, read, or emoji alone does not activate. | Can a new person reach a practical next action? |
| Contribution | Leading | A Practitioner makes a reviewable improvement to shared knowledge or an artifact: draft, correction, example, test, issue with actionable detail, or answer that is linked into durable work. Count distinct accepted contributions; keep proposed and accepted separate. | Are people making it easier for the next person? |
| Artifact reuse | Lagging | A Practice, Guide, Lab, or other durable artifact is used by someone other than its author in a stated context, with a link or voluntary note describing what was reused and what changed. A page view is not reuse. | Does shared knowledge travel beyond its author? |
| Implementation | Lagging | A Practitioner reports that a method is running in a real workflow or project, with the scope, human review point, and an owner-provided result or observation. Mark self-report as self-reported; do not imply independent verification. | Does learning become working capability? |
| Evidence | Lagging | An artifact or implementation states its inputs, steps, output, evaluation method, limitations, and failure modes, with an inspectable example, test, or measurement record where applicable. Count evidence coverage, not positive outcomes. | Can another person judge or reproduce the claim? |
| Response quality | Leading (with lagging review) | For a reviewed response, check whether it routes to the right capability stage, answers the concrete question, links a relevant durable artifact, states uncertainty, and avoids unsafe or confidential requests. Record pass/needs-revision and the reason; use a fixed sample or review all responses during a small launch period. | Do interactions move work toward reusable knowledge? |
| Retention | Lagging | A Practitioner returns and takes another capability or contribution action in a later review period. Record the action and period; do not use login or presence as a proxy. Retention is meaningful only when the return has a useful action. | Does Practice remain useful after first value? |
| Maintainer health | Leading and lagging | Once per review period, maintainers record open review queue, oldest pending item, unresolved safety/licensing issues, and a brief load status (`sustainable`, `strained`, or `blocked`). Track whether follow-ups were completed, without measuring people by speed. | Can the community sustain review and stewardship? |

### Reading the metrics together

The strongest signal is a chain, not a single high number:

`activation → contribution → artifact reuse → implementation → evidence`

Response quality supports the chain; retention indicates that it remains useful;
maintainer health indicates whether the system can continue. If activation is
up but reuse or evidence is unknown, improve routing and documentation before
celebrating growth. If implementation is reported without evidence, ask for a
reproducible description and label the result as unverified.

## Minimal manual measurement at launch

Use one shared, access-controlled spreadsheet or Markdown file maintained by a
human. Do not build custom analytics software for launch.

1. At the start of a review period, create one row per observed activation,
   contribution, reuse report, implementation report, reviewed response, and
   maintainer check-in. Use a stable non-identifying alias only when necessary
   to avoid double-counting. Leave unavailable fields blank or `unknown`.
2. Capture: period, metric, capability stage, artifact link, evidence link or
   source reference, status (`proposed`, `accepted`, `self-reported`,
   `reviewed`, or `unknown`), and one-sentence note. Keep private source
   material out of the repository and Buzz.
3. Review the contribution and response sample consistently. For each reviewed
   item, mark the checklist result and reason for revision. Count accepted
   contributions and artifact reuse only after the required evidence is
   present.
4. At the end of the period, publish a small aggregate note: counts by metric,
   denominators where applicable, number of unknowns, evidence links to public
   artifacts, and the next change to test. Never publish personal-level rows.
5. A maintainer records what changed in the method so later periods remain
   comparable. If the sample was selective, say so.

The launch review can be as small as the work the maintainers can honestly
inspect. A missing measurement is a prompt to improve instrumentation, not a
zero.

## Data not to collect

Do not collect or retain:

- private keys, passwords, recovery codes, access tokens, or other credentials;
- client, employer, or community-confidential material, including pasted
  prompts or outputs that contain it;
- personal or regulated data that is not necessary for an explicitly agreed
  operational purpose;
- covert behavioral tracking, cross-site identifiers, device fingerprints,
  message-content scraping, or individual surveillance;
- member rankings, reputation scores, attention leaderboards, or raw counts
  used to pressure participation;
- precise location, sensitive demographic or employment details, or inferred
  traits;
- message-read receipts, session duration, page views, follower counts, and
  reaction totals as substitutes for activation, reuse, or capability;
- unreviewed claims about business impact, productivity, safety, or outcomes.

If a metric would require collecting restricted data, redesign the metric around
an aggregate, voluntary, sanitized evidence record or mark it unavailable.
Hosted Buzz is not a confidential vault; durable public claims belong in Git.

## Failure modes and review actions

| Signal | Likely interpretation | Action |
| --- | --- | --- |
| Activity rises but contributions do not | Conversation is not reaching a reusable output. | Improve prompts, routing, and contribution templates; sample responses. |
| Contributions rise but reuse is unknown | Artifacts may be hard to find or reuse is not being reported. | Add a voluntary reuse field and inspect links, without inventing usage. |
| Implementations are self-reported with thin evidence | Capability may be real but cannot yet be judged. | Request inputs, evaluation, limitations, and failure modes; label as unverified. |
| Response quality needs revision repeatedly | Routing, scope, or safety guidance is unclear. | Update the relevant Practice or escalation path and re-review a sample. |
| Maintainer status is strained or blocked | The operating model is at risk even if activity looks healthy. | Reduce intake, clarify ownership, or defer nonessential work; record the decision. |

