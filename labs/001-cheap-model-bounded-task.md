---
artifact_type: lab
title: "Compare low-cost model configurations on bounded artifact tasks"
summary: "Evaluate whether candidate low-cost model configurations complete three fixed, synthetic artifact tasks to a predeclared quality bar."
status: proposed
primary_capability: learn
roles: [individual-practitioner, builder]
task_set_version: 0.1.0
run_count: 0
result_status: not-run
last_run: null
version: 0.1.0
license: CC-BY-4.0
created: 2026-08-31
updated: 2026-08-31
---

# Compare low-cost model configurations on bounded artifact tasks

This proposed Lab gives a Practitioner a repeatable way to compare task-completion quality and request cost for a small set of artifact tasks. It does not test general model intelligence, safety outside the packets, tool use, long-context work, or real operational outcomes.

## Question

Under the fixed conditions below, which eligible low-cost model configurations, if any, meet the predeclared quality and cost gates on three synthetic, bounded artifact tasks?

## Hypothesis

At least one eligible candidate configuration will achieve a mean task-completion score of at least 8.0 out of 10.0, will have no critical error in any included run, and will stay at or below the cost ceiling declared before the first request.

This is a proposed expectation, not a claim that any configuration meets the gates.

## Variables

| Type | Definition | Measurement |
|---|---|---|
| Independent variable | Candidate model configuration: provider, model identifier, endpoint, model version or snapshot when supplied, and parameters. | Record exactly in the run ledger. Do not substitute a newer version into an existing run group. |
| Primary outcome | Task-completion quality. | Mean of the two evaluator scores for each run, using the 10-point rubric. Report each task separately and the mean across all included runs. |
| Gate outcome | Critical-error rate. | Number of included runs with one or more critical errors divided by included runs. Any critical error makes that configuration ineligible. |
| Cost outcome | Direct model-request cost per run. | Calculate from recorded actual usage and the captured published price using the stated formula. Report currency and do not treat it as total operating cost. |
| Uncontrolled confounders | Provider-side serving changes, hidden model revisions, transient availability, and evaluator judgment. | Record timestamps, provider identifier or snapshot, retry/exclusion reason, evaluator disagreement, and adjudication. Do not claim these are eliminated. |

## Fixed conditions

- Use exactly the task packets and canonical request prompt in this document, task-set version `0.1.0`.
- Use three trials for every candidate-and-task pair. A run is one trial of one candidate configuration on one task; the planned run count is `candidate configurations × 3 tasks × 3 trials`.
- Before the first request, set and record one cost ceiling in the execution record as currency per run. The ceiling applies to direct model-request cost, not evaluator labor or infrastructure. It must not be changed within a run group.
- Choose two to four candidate configurations before execution. A candidate is eligible to enter only when its provider publishes a usable input and output price that can be captured with a URL and as-of date. Candidate selection is not a quality ranking or endorsement.
- Send no task packet to a model with browsing, retrieval, file access, code execution, plugins, or tools enabled. If the interface cannot disable one of these, do not include that run.
- Use the same role message, canonical request prompt, output-token limit of 900, temperature of 0, top-p of 1 when the interface exposes it, and default values for other parameters. Record an unavailable parameter as `not exposed` rather than guessing.
- Use a fresh conversation or request for every run. Do not add prior output, corrections, or evaluator feedback to later runs.
- Use only the synthetic material below. Do not add external facts, brand policies, customer data, or hidden reference documents.
- Assign opaque run IDs before evaluator review. Two evaluators score independently without candidate identity when practical. Record any failure of blinding.

### Canonical request prompt

Use this message after the role message and before the selected task packet:

```text
Create only the requested Markdown artifact from the supplied task packet.
Use no facts beyond the packet. If a required detail is missing, state that it is missing rather than inventing it.
Follow every stated format and constraint. Do not explain your reasoning or add a preface.
```

### Role message

```text
You produce bounded work artifacts for review. Accuracy to the supplied packet and compliance with explicit constraints matter more than adding detail.
```

## Task set

All packets are synthetic fixtures designed for this Lab. Each packet is self-contained and public. Give the model the role message, canonical request prompt, and exactly one packet.

### Task A — Release-readiness checklist

**Requested artifact:** A Markdown checklist titled `CSV export release readiness` with the sections `Access`, `Audit record`, and `Release review` in that order. Include one checkbox item for every required condition. Do not add product requirements.

**Packet:**

```text
Product: Northline (synthetic)
Change: Administrators can export an account report as CSV.

Required conditions:
1. Only administrators may start an export.
2. The audit record must include requester, timestamp, and selected export filters.
3. A download link expires after 7 days.
4. A reviewer must confirm the access rule before release.
5. A reviewer must confirm the audit fields before release.

Out of scope: redesigning permissions, changing report content, and a dashboard.
```

**Expected conditions for scoring:** The three required headings appear in order; all five requirements appear without contradiction; no out-of-scope work becomes a requirement; Markdown checkboxes are used.

### Task B — Routing-assistant test matrix

**Requested artifact:** A Markdown table titled `Routing test matrix` with exactly five data rows and these columns: `Scenario`, `Expected route`, `Human review required`, and `Check`. The `Check` column must name a concrete observable check, not a generic statement such as “works.”

**Packet:**

```text
System: Support routing assistant (synthetic)
Allowed routes: billing, access, deletion.

Rules:
- A duplicate charge routes to billing without human review.
- A person who cannot sign in routes to access without human review.
- A request to delete an account routes to deletion and requires human review.
- A request that contains both a duplicate charge and cannot sign in routes to billing and requires human review because it has more than one issue.
- A request with too little information to choose a route requires human review and must be marked unresolved; do not guess a route.
```

**Expected conditions for scoring:** There is one row for each rule; each route and review value is correct; the unresolved row does not select an allowed route; every check makes the expected route or review state inspectable; there are exactly five data rows and the required columns.

### Task C — Source-grounded incident update

**Requested artifact:** A Markdown status update of no more than 120 words followed by a heading `Unsupported claims removed` and a bullet list. The update must use only supported facts. The bullet list must identify every unsupported claim in the supplied draft.

**Packet:**

```text
Source A — incident record
- Notification delivery was delayed for 47 minutes on 2026-08-14.
- The incident affected delayed notifications; the record does not state a count of affected people.
- The identified cause was an incorrect queue configuration.
- No customer data was lost.
- The operations team will add a configuration-validation check before future queue changes.

Source B — draft to correct
"On 2026-08-14, a two-hour outage caused notification delays and customer data loss.
We permanently fixed the queue issue and every affected customer has been contacted."
```

**Expected conditions for scoring:** The update states the correct date, 47-minute delay, notification impact, queue-configuration cause, no data loss, and planned validation check without presenting it as complete. The bullet list identifies all four unsupported draft claims: two-hour duration, customer data loss, permanent fix, and every affected customer contacted. The response stays within 120 words and uses the required heading and bullets.

## Procedure

1. Create an execution record outside this proposed Lab. Record the repository commit, task-set version, execution owner, UTC start time, currency, cost ceiling, and candidate-selection rationale. Do not record credentials or account identifiers.
2. Select two to four candidate configurations that satisfy the low-cost entry rule in **Fixed conditions**. Capture the pricing URL, as-of date, model identifier, endpoint, and any provider version or snapshot before the first request. Assign each candidate an opaque code such as `C1` or `C2` for evaluator materials.
3. Prepare nine run IDs per candidate: three trials for each of Tasks A, B, and C. Randomize request order once and retain the randomization list.
4. For each run, send the fixed role message, canonical request prompt, and selected task packet in a fresh request. Record request timestamp, parameter values or `not exposed`, actual input and output usage, raw response, response identifier when safe to share, and any retry.
5. Exclude and retain a run only for a documented technical failure before an artifact is returned, such as a provider error or a response truncated below the requested artifact. Do not silently rerun a scored output. If a retry is permitted by the predeclared execution record, link it to the excluded run and state why.
6. Remove candidate identity from the evaluator packet. Two evaluators independently apply the rubric to every returned artifact. They cite the required condition or output text supporting each score.
7. If evaluators differ by more than one point on a criterion or disagree on a critical error, an adjudicator compares the artifact with the packet and rubric. Preserve both original scores and the adjudicated score with its reason.
8. Calculate per-run quality, per-task mean quality, critical-error rate, and direct request cost. Apply the decision rule without combining quality and cost into one score.
9. Populate **Results** only with observed records. Then write **Interpretation** within the limits of the completed task set. If the planned run group cannot be completed comparably, set `result_status: invalidated` and explain why.

## Evaluation rubric

Each evaluator assigns 0, 1, or 2 points for each criterion. The maximum score is 10 points per run. Use the mean of the two evaluator totals unless adjudication is required.

| Criterion | 0 points | 1 point | 2 points |
|---|---|---|---|
| Required facts and decisions | Missing, contradicted, or invented material changes the artifact. | Most required facts are present but one is missing, vague, or weakly contradicted. | All required facts and decisions are correct and no unsupported fact is added. |
| Required structure | Required format or major section is absent. | Structure is present with a minor heading, column, order, or format defect. | All required headings, columns, order, and format constraints are met. |
| Task-specific completeness | Two or more required conditions or cases are absent. | One required condition or case is absent or materially incomplete. | Every required condition or case is represented and usable. |
| Constraint compliance | Violates a hard constraint, such as a word limit, row count, or out-of-scope instruction. | Meets hard limits but includes one avoidable unsupported or distracting addition. | Meets all stated limits and excludes out-of-scope additions. |
| Review usability | A reviewer cannot reliably check the artifact against the packet. | Usable with notable ambiguity or an unclear check. | Clear, scannable, and directly reviewable against the packet. |

### Critical errors

Mark a run as a critical error when any of the following occurs:

- Task A permits non-administrators to start an export, omits the 7-day expiry, or makes an out-of-scope change a release requirement.
- Task B routes account deletion without human review, routes the unresolved case to a category, or omits human review for the multi-issue case.
- Task C says data was lost, reports a duration other than 47 minutes, presents the planned validation check as completed, or fails to identify an unsupported claim from the draft.

Critical errors are recorded in addition to points. A configuration with any critical error in an included run cannot pass the quality gate, even if its mean score is high.

### Decision rule

A candidate configuration is eligible for this task set only when all of the following are true:

1. Its mean quality across included runs is at least 8.0 out of 10.0.
2. It has zero critical errors across included runs.
3. Its mean direct model-request cost per run is at or below the predeclared cost ceiling.

Report all configurations and outcomes. If more than one configuration is eligible, report their quality and cost separately; do not name a general winner or infer performance outside these tasks.

## Cost capture

For each candidate configuration, capture before execution:

| Field | Record |
|---|---|
| Candidate code and full identifier | Opaque evaluator code plus provider, model identifier, endpoint, and version or snapshot when supplied. |
| Pricing source | Provider-published URL and the UTC date accessed. |
| Price basis | Input, output, cached-input, batch, request, or other applicable unit price and currency. |
| Usage basis | Actual per-run input, output, cached, or other billed unit count from the response or usage record. |

For each run, calculate direct model-request cost in the declared currency:

```text
run cost =
  (input tokens × input price per token) +
  (cached input tokens × cached-input price per token, if applicable) +
  (output tokens × output price per token) +
  fixed per-request charges, if applicable
```

When the recorded price basis is per-million tokens, convert it to per-token before calculation; otherwise compute from the recorded basis directly. Do not convert currencies for comparison unless the exchange-rate source, date, and calculation are recorded. Exclude evaluator labor, local compute, network, subscriptions not charged by usage, taxes, and failed requests with no billable usage; list any exception in the run ledger.

## Results

**Result status:** Not run. No candidate configuration, score, cost, or endorsement exists yet.

### Execution record

| Field | Value |
|---|---|
| Repository commit | Not run |
| Execution date range (UTC) | Not run |
| Cost ceiling and currency | Not run |
| Candidate configurations | Not selected |
| Planned / included / excluded runs | Not run / 0 / 0 |
| Evaluator blinding exceptions | Not run |

### Run ledger

| Run ID | Candidate code | Task | Trial | UTC timestamp | Output reference or hash | Input / output usage | Direct request cost | Evaluator totals | Critical error | Included or excluded, with reason |
|---|---|---|---:|---|---|---|---|---|---|---|
| No runs recorded | — | — | — | — | — | — | — | — | — | — |

### Per-candidate task summary

| Candidate code | Task A mean / 10 | Task B mean / 10 | Task C mean / 10 | Overall mean / 10 | Critical errors / included runs | Mean direct request cost | Meets all gates? |
|---|---:|---:|---:|---:|---|---|---|
| No results recorded | — | — | — | — | — | — | — |

## Interpretation

Pending execution. Do not infer a candidate's general ability, reliability, cost efficiency, or suitability for work beyond the three synthetic task packets.

## Limitations

- Three synthetic tasks cannot represent general model intelligence, real work quality, domain expertise, long-context performance, tool use, or safety in other contexts.
- The task packets and rubric favor explicit, short Markdown artifacts; results may not transfer to ambiguous, iterative, multilingual, confidential, or high-consequence work.
- Three trials per task can expose some variation but are not a basis for broad statistical claims.
- Evaluator judgment remains a source of variation even with blinded scoring and an adjudication rule.
- Providers may change pricing, endpoint behavior, hidden model revisions, rate limits, or usage accounting after the recorded run date.
- Direct request cost excludes the labor and infrastructure needed to operate a real workflow.
- A configuration can meet these gates and still be unsuitable where stronger verification, privacy controls, or human review are needed.

## Reproduction

1. Check out the repository commit recorded in the execution record and verify this file's `task_set_version` is `0.1.0`.
2. Copy the role message, canonical request prompt, and one complete task packet per request without alteration. Use fresh conversations and the fixed conditions listed above.
3. Before sending requests, select two to four candidates, set one cost ceiling, record the candidate metadata and provider-published pricing sources with UTC access dates, and prepare three randomized trials for each task and candidate.
4. Run the requests without tools, retrieval, or external material. Store raw outputs in a safe-to-share location, or retain a cryptographic hash and access-controlled record when outputs cannot be published.
5. Create a run ledger using the exact columns in **Results**. Record every returned output, billable usage, cost calculation, technical failure, retry, and exclusion.
6. Give de-identified artifacts and task packets to two evaluators. Preserve each score, cited evidence, disagreement, and adjudication before calculating aggregates.
7. Apply the decision rule exactly. Publish observed results, limitations, and any invalidating condition; do not substitute a later model version or changed task packet into the same run group.

## Changelog

- 2026-08-31 — `0.1.0`: Created the proposed Lab, synthetic task set, scoring rubric, cost-capture method, and empty execution record.
