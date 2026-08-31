---
artifact_type: lab
title: "Lab title"
summary: "The bounded question this evaluation answers and the artifact task it measures."
status: proposed
primary_capability: learn
roles: [individual-practitioner]
task_set_version: 0.1.0
run_count: 0
result_status: not-run
last_run: null
version: 0.1.0
license: CC-BY-4.0
created: YYYY-MM-DD
updated: YYYY-MM-DD
# secondary_capabilities: []
# secondary_roles: []
# authors: []
# maintainers: []
# source_links: []
# deprecated_on: YYYY-MM-DD # Required when status is deprecated.
# deprecation_reason: "Why this Lab should no longer be run."
# superseded_by: "relative-path-or-URL" # Optional; use only when a replacement exists.
---

# Lab title

## Question

State one answerable question about a defined task, condition, or comparison. Do not frame it as a claim about general model intelligence.

## Hypothesis

State the proposed, falsifiable expectation and the threshold or decision it will be tested against. A hypothesis is not a result.

## Variables

Name the independent variable, every outcome measure, and any confounder that cannot be controlled. Define how each measure is calculated.

## Fixed conditions

List the frozen prompt, task-set version, tools and retrieval access, model parameters, output limits, number of trials, evaluator process, and environment details that must stay the same.

## Task set

Provide the complete dataset or task packets, required output, and expected facts or conditions. Label synthetic fixtures and disclose any redaction or access restriction that prevents exact reproduction.

## Procedure

Give ordered execution steps, including candidate selection, run identification, output storage, evaluator blinding, and the stop or rerun rule.

## Evaluation rubric

Define a scoring scale, task-specific pass conditions, critical errors, evaluator roles, disagreement handling, and the decision rule. Score the stated task-completion quality; do not infer a broad ranking.

## Cost capture

Record the pricing source and as-of date, actual input and output tokens, any cached-token or request charge, currency, and formula. State which costs are excluded.

## Results

Start with `result_status: not-run` until execution. Record the run ledger, per-task quality scores, cost per run, exclusions, and the calculation used for any aggregate. Preserve raw outputs or safe-to-share hashes and paths. Empty tables are acceptable for a proposed Lab; do not insert illustrative values as results.

## Interpretation

After execution, answer the Question only within the stated tasks and conditions. Separate observed result, inference, and non-result. Do not endorse a model or generalize beyond the task set.

## Limitations

State coverage gaps, evaluator subjectivity, provider or version drift, price changes, sampling limits, and any conditions that make comparison invalid.

## Reproduction

State the exact inputs, environment record, run count, parameters, cost source, scoring materials, output locations or hashes, and steps another Practitioner needs to repeat the Lab.

## Changelog

Record dated, meaningful changes to the task set, procedure, rubric, results, scope, or status. A material change requires a new task-set version and must not be pooled with prior runs.
