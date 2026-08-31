---
artifact_type: practice
title: "Redesign a recurring workflow"
summary: "Map a recurring workflow, assign the right level of automation and human ownership, and test changes behind reviewable safety gates."
maturity: proposed
capability: automate
roles: [individual-practitioner, operator, transformation-lead]
version: 0.1.0
license: CC-BY-4.0
created: 2026-08-31
updated: 2026-08-31
evidence_quality: none
secondary_capabilities: [use, build, transform]
tags: [workflow, automation, agents, approvals, rollback, evaluation]
---

# Redesign a recurring workflow

## Outcome

For one bounded recurring workflow, produce a versioned workflow map and a smallest safe experiment. The map names each step, its trigger, inputs and data permissions, classification, risk, owner, approval gate, rollback action, and measurement. It makes clear what may be deterministic, AI-assisted, agentic, or human-owned; it does not presume that more automation is better.

## Problem and scope

Teams often automate a visible task before understanding the whole flow around it. Hidden judgment, permissions, exception handling, and recovery then become failure points. This Practice redesigns one repeatable workflow from trigger to completed outcome, including handoffs and exceptions.

It is not a mandate to automate, a substitute for legal, safety, security, financial, or domain controls, or a blueprint for unsupervised decisions. Keep consequential decisions and irreversible effects human-owned unless the responsible authority has separately approved them.

## Use when

- The work recurs often enough to observe its current path and exceptions.
- A named owner can describe the intended outcome and accept or reject changes.
- The team can access safe summaries or samples without exposing secrets or unnecessary personal data.
- There is a reversible, low-risk slice suitable for a trial.

If the work is one-off, has no accountable owner, or cannot be safely rolled back, document the current process and obtain the required governance decision before experimenting.

## Inputs

- A workflow owner, operators who perform it, and an approver for consequential effects.
- The trigger, desired outcome, service or timing constraints, and definition of done.
- A small sample of representative runs, including at least one exception, with sensitive data redacted or kept in its approved system.
- Current tools, systems of record, integrations, credentials boundaries, and data-retention rules.
- Known risks, policies, downstream consumers, and a way to restore the pre-change process.
- Baseline observations: volume, elapsed time, rework, handoffs, errors, escalations, and approval points where available.

## Method

### 1. Set the boundary and baseline

Write: “When [trigger] occurs, [owner] produces [outcome] for [recipient] using [allowed systems] within [constraint].” Mark the start and end events, exclusions, dependencies, and irreversible effects. Observe enough recent runs to describe normal work and exceptions; if a measure is unavailable, label it unknown rather than inventing a baseline.

### 2. Inventory the current workflow

List every step, including waiting, checking, handoff, exception, and recovery steps. Use this map as the working inventory:

| ID | Trigger / step / output | Actor | Inputs and system of record | Data access | Risk / failure consequence | Current control | Time or volume measure |
|---|---|---|---|---|---|---|---|
| W1 | Start condition and expected output | role | source and destination | minimum required scope | what could go wrong | existing check | observed or unknown |

Ask the operator to walk through a normal run and an exception. Record where judgment occurs, where data changes, and where a person can stop or correct the flow.

### 3. Classify each step

Assign exactly one primary classification, then record the reason and boundary in the map:

- **Deterministic:** fixed rules, validation, lookup, transformation, or routing with predictable inputs and outputs. Use code or configuration when it reduces repetition without hiding a judgment.
- **AI-assisted:** a model drafts, extracts, summarizes, ranks, or proposes; a person checks the result before it is used. Define the allowed context and acceptance check.
- **Agentic:** a bounded system selects among tools or steps and can continue across a sequence. Use only where tools, permissions, spend, stop conditions, logs, and recovery are explicit.
- **Human-owned:** a person makes the judgment, grants approval, handles an exception, or performs an irreversible or high-consequence action. Assistance may prepare evidence, but accountability stays with the named role.

Do not classify a step as agentic merely because it uses a model. If a proposed change cannot state its stop condition and recovery path, keep that step human-owned.

### 4. Add risk, access, approval, and rollback gates

For each proposed change, complete this design record:

| Step ID | Proposed class | Allowed data and least privilege | Risk level and consequence | Required human approval | Stop condition | Rollback / recovery | Audit record |
|---|---|---|---|---|---|---|---|
| W# | deterministic / AI-assisted / agentic / human-owned | systems, fields, role | low / medium / high plus concrete failure | role and point before effect | observable halt rule | how to restore prior state | inputs, output, decision, timestamp |

Place approval before publishing, sending, spending, changing a system of record, granting access, or making a consequential recommendation. Use a dry run, draft state, sandbox, or queue when available. For data access, minimize fields, use approved locations, restrict identities, log access, and define retention; never move secrets or confidential material into a shared prompt or artifact.

### 5. Design the smallest safe experiment

Select one low-risk step or narrow slice. Keep the old path available, cap volume and permissions, use representative but safe inputs, and require a person to inspect every output before any external effect. Define a stop trigger before the first run: for example, a privacy concern, an unhandled exception, a failed acceptance check, or any rollback invocation.

Write an experiment card:

```text
Change and boundary:
Owner and reviewer:
Sample and duration/volume cap:
Allowed data and tools:
Expected output and acceptance checks:
Baseline and measures:
Approval before effect:
Stop trigger:
Rollback steps and recovery owner:
Decision date: continue, revise, or revert
```

### 6. Evaluate before expanding autonomy

Compare trial outputs with the baseline and a human-reviewed reference. Check task quality, missed or invented information, exception handling, access violations, approval compliance, rollback success, operator burden, elapsed time, and rework. Review failures individually; an average score cannot hide a severe edge case.

Expand scope or autonomy only when the owner and approver accept the evidence, all defined safety checks pass, the rollback has been rehearsed, and unresolved risks have an explicit owner. Otherwise revise the map or revert. Repeat the evaluation after any material change to data, tools, instructions, permissions, or decision consequences.

### Expected output

A versioned workflow map, proposed classifications, access and risk records, approval and rollback gates, a baseline, an experiment card, and a recorded decision to continue, revise, or revert.

## Evaluation

This is a proposed method; no execution evidence is claimed. Trial it on one bounded, low-risk workflow. Accept the trial when an operator can trace a normal run and an exception from trigger to outcome, every step has a classification and owner, data access is least-necessary and approved, approval precedes consequential effects, rollback is actionable, and the experiment record contains baseline, measures, stop triggers, and a decision.

Do not infer improved accuracy, speed, cost, satisfaction, or safety from producing the map. Those outcomes require measured comparison. Before granting more tool access, larger volume, or less human review, require a new evaluation record with the relevant failure cases and approval.

## Implementation

### Minimal: one reviewable document

Create a Markdown document containing the boundary, inventory table, classification rationale, design records, baseline, experiment card, and decision log. Version it in the team's approved repository or document system. Keep links to systems of record rather than copying restricted data. The owner updates the map when a tool, policy, data source, or downstream consequence changes.

### Advanced: controlled workflow specification

Represent each step as a versioned record with typed inputs and outputs, allowed tools, identity, timeout, retry policy, stop condition, approval requirement, audit fields, and rollback handler. Run deterministic checks and AI proposals in separate stages. Put agentic actions behind a queue or sandbox until evaluation supports a narrower approval boundary. Treat automated checks as signals for human review, not proof that a workflow is safe.

## Failure modes

The following are anticipated failure hypotheses for the first trial:

- **Hidden step omitted:** An exception or waiting step is missing. Consequence: the redesign fails outside the happy path. Prevention: observe normal and exception runs with operators; recovery: revert and amend the inventory.
- **Automation assumed beneficial:** A step is automated despite little repetition or high judgment cost. Consequence: review and rework increase. Prevention: require a baseline and comparison; recovery: keep the prior path or reclassify as human-owned.
- **Excessive data access:** A tool or agent receives more data or permissions than its step needs. Consequence: privacy, security, or compliance exposure. Prevention: least privilege and access review; stop and report through the applicable incident process.
- **Approval after the effect:** A draft is sent or a record is changed before review. Consequence: an incorrect or unauthorized outcome is difficult to undo. Prevention: place approval before the effect and use draft states; recovery: invoke the documented correction and rollback owner.
- **No usable rollback:** Dependencies or side effects make restoration unclear. Consequence: the experiment becomes an uncontrolled production change. Prevention: test rollback on a safe sample and cap scope; do not proceed if recovery is unknown.
- **Agent drift or tool failure:** A model or integration behaves differently from the trial. Consequence: wrong routing, repeated actions, or unhandled exceptions. Prevention: bounded tools, idempotency where possible, logs, stop limits, and human review; recovery: halt, restore the old path, and investigate.
- **Metric gaming:** A faster or higher-throughput flow hides quality or safety failures. Consequence: apparent improvement masks harm. Prevention: measure quality, rework, exceptions, access, and approval compliance together.

## Evidence

Initial maturity is **proposed** and evidence quality is **none**. The repository contains the method, a hypothetical example, and a planned trial only; it does not contain a completed workflow redesign or measured outcome. A future tested revision should preserve a safe-to-share map version, sample description, baseline and comparison, failures, approvals, rollback result, outcome, and limitations. Redact private inputs and do not promote maturity based on an anecdote.

## Worked hypothetical example

The following is a **hypothetical example**, not a report of a real team or result.

**Workflow:** Each Monday, an operations practitioner turns approved support themes into an internal triage brief. The brief may inform queue priorities but does not change tickets or customer commitments.

| ID | Step and classification | Data / risk | Approval and rollback | Measure |
|---|---|---|---|---|
| H1 | Deterministic: fetch last week's approved, de-identified theme counts | reporting view only; low risk if aggregation is correct | operator checks query; rerun prior query or use last approved extract | elapsed time, query errors |
| H2 | AI-assisted: draft grouped themes and open questions | approved summaries only; medium risk of omission or invention | operations lead reviews against source extract before circulation; discard draft and use manual outline | factual corrections, missing themes, review time |
| H3 | Human-owned: decide which themes warrant queue attention | context may include operational constraints; medium judgment risk | operations lead owns decision; no automated ticket changes | decision completeness, escalations |
| H4 | Human-owned: approve and circulate the brief | internal audience; risk of premature or misleading communication | named lead approves before send; retract or issue correction if needed | approval compliance, rework |

The smallest safe experiment changes only H2: run the draft on two weeks of de-identified extracts, keep H3 and H4 fully human-owned, cap distribution at one reviewer, and compare corrections and review time with the manual outline. Any invented theme, unsupported claim, access violation, or failed source check stops the trial. Expansion to more data or autonomous routing requires a new evaluation and approval; it is not implied by a successful draft.

## Variations

- For a low-volume task, a checklist and manual handoff may be safer than building an integration.
- For high-consequence work, retain human ownership for every decision and use AI only to prepare traceable evidence, subject to domain controls.
- For stable, low-risk transformations, deterministic validation can precede an AI-assisted step; keep the classifications and rollback boundaries separate.

## Changelog

- **2026-08-31 — 0.1.0:** Proposed a workflow-redesign method with inventory, classification, risk and access gates, approval and rollback controls, measurement, a smallest safe experiment, and a hypothetical example.
