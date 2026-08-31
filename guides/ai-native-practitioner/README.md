---
artifact_type: guide
title: "The AI-Native Practitioner"
summary: "A shared path for Practitioners to design, run, verify, and improve a bounded human-reviewed AI workflow, with applied, technical, and organizational extensions."
status: draft
capability: automate
secondary_capabilities: [learn, use, build, transform]
audience: [individual-practitioner, engineer, builder, operator, internal-ai-champion, transformation-lead, consultant, executive]
version: 0.2.0
license: CC-BY-4.0
created: 2026-08-31
updated: 2026-08-31
maintainers: [Practice guide maintainers]
source_links:
  - "../../docs/framework/CAPABILITY_LADDER.md"
  - "../../docs/schemas/GUIDE_SCHEMA.md"
---

# The AI-Native Practitioner

## Intended Practitioner

This Guide is for someone responsible for making AI useful in real work. You may work mainly through documents and operating processes, build software, or lead organizational change. You do not need to begin as a programmer or hold a particular title.

Start with one recurring task you understand well and are allowed to examine. You should be able to describe its inputs, intended output, current steps, accountable owner, and consequences of failure. If you cannot safely use the real inputs, create a representative synthetic case and label it as such.

The Guide uses one shared spine rather than separate courses. Every Practitioner learns the same task-framing, context, workflow, verification, and governance concepts. An **applied**, **technical**, or **organizational** route changes the depth of selected exercises and the form of the final capstone; it does not waive the common completion checks.

## Outcomes

The core completion outcome is observable: design, run, verify, and document one bounded, repeatable, human-reviewed AI workflow. The workflow may remain manual between steps. Reliable operation matters more than unattended automation.

On completion, a Practitioner can:

- decide whether AI belongs in a task and explain the boundary;
- produce and maintain an approved context pack for recurring work;
- separate deterministic, AI-assisted, agentic, and human-owned steps;
- define permissions, approval points, failure handling, rollback, and ownership;
- evaluate outputs against task-specific acceptance criteria and preserve the evidence;
- distinguish a successful trial from a repeatable workflow or a transformed operating model; and
- communicate an implementation so another person can inspect, run, challenge, or maintain it.

Full completion requires a capstone dossier, an observed run on representative cases, a verification record, a named reviewer, and an honest limitations record. Completion does not prove universal effectiveness, confer a credential, or justify expanding autonomy.

## Prerequisites

Bring:

- one recurring work task and an accountable owner;
- safe-to-use inputs or a clearly labeled synthetic substitute;
- the current workflow, even if it is only a rough list of steps;
- a definition of an acceptable result and the consequence of a bad one;
- access to an AI system appropriate to the task, if policy permits; and
- a place to keep versions, decisions, run records, and review evidence.

Read the [Capability Ladder](../../docs/framework/CAPABILITY_LADDER.md) before selecting a route. Use it to classify demonstrated outcomes, not people. No specific model, platform, framework, programming language, or automation service is required.

Do not use confidential, personal, regulated, licensed, or security-sensitive material unless you have explicit authority and an approved handling method. Choose a different task or use synthetic inputs when those conditions are not met.

## Path

The common spine follows the dependency structure of dependable AI work:

1. **Foundations** establishes how to reason about model output, context, tools, privacy, security, structured outputs, and evaluation.
2. **Effective Use** applies that judgment to a discrete task and compares the result with a baseline.
3. **Context Engineering** turns ad hoc instructions and sources into a maintained context system.
4. **Automation and Agents** redesigns the recurring workflow before adding tools or autonomy.
5. **Agentic Engineering** makes specifications, implementation boundaries, tests, review, and delivery controls inspectable.
6. **Organizational AI** connects the workflow to roles, governance, adoption, operating measures, and accountable change.

These modules build from Learn through Use, Automate, Build, and Transform. Everyone completes the universal checkpoint in every module. Route overlays in the [curriculum map](CURRICULUM.md) specify where to deepen the work:

- **Applied route:** emphasize a dependable workflow a nontechnical Practitioner can operate and review.
- **Technical route:** add a runnable or inspectable implementation, task-level tests, and delivery controls.
- **Organizational route:** add a bounded pilot, role and decision-right changes, proportional governance, and an operating measurement plan.

Modules 1–4 form a usable **starter path**. All six modules are available, but a
Practitioner can stop after the starter path with a checked workflow trial.
That is interim evidence, not full Guide completion and not a claim that the
workflow is mature.

**Frontier work is separate.** After the core path, an optional Frontier Studio teaches how to frame and test an unsettled technique as a Lab. Frontier material is not a prerequisite, a production recommendation, or established Practice merely because it is included here.

## Modules

The detailed curriculum contracts—including prerequisites, module capstones,
and evidence—are in the [curriculum map](CURRICULUM.md). Each module and
proposed method is linked below. File availability does not imply tested
evidence; follow each artifact's maturity label.

### Module 1 — Foundations

**Purpose:** Advance **Learn** capability by explaining the relevant behavior and limits of an AI-assisted task, then choosing a safe bounded test.

**Methods:** Use the proposed [Verification Gate](../../practices/003-verification-gate.md) for the acceptance record; it remains `maturity: proposed`.

**Output:** A task-and-risk brief, structured-output specification, and evaluation plan for the chosen task.

**Completion check:** The Practitioner can explain what the system receives, what it may produce, where uncertainty enters, what must remain human-owned, and how an output will be accepted or rejected.

**Module:** [Foundations](01-foundations.md)

### Module 2 — Effective Use

**Purpose:** Advance **Use** capability by completing and checking one discrete real-work task with deliberate framing, iteration, critique, and source-aware verification.

**Methods:** Apply the proposed [Verification Gate](../../practices/003-verification-gate.md) and preserve its current evidence limits.

**Output:** A baseline record, assisted work artifact, revision history, verification record, and decision about whether AI should remain in the task.

**Completion check:** The Practitioner compares baseline and assisted work using the same criteria, records corrections or rejection, and makes no improvement claim beyond the evidence collected.

**Module:** [Effective Use](02-effective-use.md)

### Module 3 — Context Engineering

**Purpose:** Advance **Use** capability by designing context as a maintained system of instructions, approved sources, examples, boundaries, and checks rather than as one long prompt.

**Methods:** Apply the proposed [Reusable Context Pack](../../practices/001-context-pack.md); its publication as a candidate does not make it tested.

**Output:** A context pack with source authority, freshness, conflict, privacy, disclosure, and maintenance rules.

**Completion check:** Another reviewer can identify which source controls, detect stale or conflicting material, see what must not be included, and use the pack to reproduce the intended task setup.

**Module:** [Context Engineering](03-context-engineering.md)

### Module 4 — Automation and Agents

**Purpose:** Advance **Automate** capability by turning the recurring task into a reviewable workflow with the smallest justified amount of autonomy.

**Methods:** Apply the proposed [Workflow Redesign](../../practices/002-workflow-redesign.md) and [Verification Gate](../../practices/003-verification-gate.md), retaining their evidence labels.

**Output:** A workflow map, step classification, permissions table, test set, approval rules, failure paths, rollback, and run record.

**Completion check:** The workflow has an owner, observable state, representative tests, a human approval point where consequences require it, and a recovery path. The Practitioner can explain why an agent is or is not necessary.

**Module:** [Automation and Agents](04-automation-agents.md)

### Module 5 — Agentic Engineering

**Purpose:** Advance **Build** capability by turning a bounded system change into an inspectable specification, implementation or implementation brief, test record, independent review, and controlled handoff.

**Methods:** The proposed [Verification Gate](../../practices/003-verification-gate.md) is the acceptance boundary for the module.

**Output:** Everyone produces a system boundary, acceptance criteria, test plan, file or component ownership, and handoff. Technical-route Practitioners also produce a runnable or inspectable change with test and delivery evidence.

**Completion check:** A reviewer can trace each completion claim to a diff, test, inspection, source, or explicit limitation; no unverified output is accepted because an agent reported success.

**Module:** [Agentic Engineering](05-agentic-engineering.md)

### Module 6 — Organizational AI

**Purpose:** Advance **Transform** capability by connecting the workflow to an operating outcome, roles, decision rights, knowledge, governance, enablement, and measurement.

**Methods:** Apply the proposed [Workflow Redesign](../../practices/002-workflow-redesign.md) and [Verification Gate](../../practices/003-verification-gate.md); do not treat tool deployment or activity as transformation evidence.

**Output:** An opportunity map and change brief. Organizational-route Practitioners add a bounded pilot operating model with owners, controls, enablement, measures, review cadence, and stop or rollback conditions.

**Completion check:** The Practitioner distinguishes baseline, observed operating change, adoption signal, capability evidence, and hypothesis. Any claim about quality, time, cost, risk, or business outcome is supported by a stated local measure or omitted.

**Module:** [Organizational AI](06-organizational-ai.md)

### Optional studio — Frontier Work

**Purpose:** Advance **Learn** capability—and **Build** when an implementation is produced—by turning an unsettled idea into a bounded, reproducible experiment.

**Practices:** Frontier work is not a canonical Practice by default. Use the [artifact taxonomy](../../docs/framework/TAXONOMY.md) to publish a Lab, Note, or Project at the maturity the evidence supports.

**Output:** A research brief or Lab plan with a hypothesis, fixed conditions, task set, rubric, safety boundary, stop condition, result record, and limitations.

**Completion check:** The Practitioner can separate observation from inference, report negative or inconclusive results, and explain why the experiment does not yet justify production use or a general recommendation.

## Capstone

Complete one bounded piece of recurring work using the shared capstone dossier in the [curriculum map](CURRICULUM.md). The dossier must contain:

1. a task, boundary, accountable owner, baseline, and explicit non-goals;
2. an approved context pack with source and maintenance rules;
3. a before-and-after workflow map that identifies human-owned, deterministic, AI-assisted, and agentic steps;
4. acceptance criteria, representative cases, an adverse or edge case, and run records;
5. permissions, approval points, observability, failure handling, rollback, and escalation;
6. a verification record linking completion claims to evidence;
7. an operating and maintenance note covering ownership, review triggers, known limits, and the next bounded decision; and
8. the route extension below.

Choose one route extension:

- **Applied:** a repeatable human-reviewed workflow that another authorized person can operate from the documentation.
- **Technical:** a runnable or inspectable implementation with setup, task-level tests, change review, and a delivery or recovery record.
- **Organizational:** a pilot operating model showing role and decision-right changes, proportional controls, enablement, measures, and review or stop conditions.

Human review is required before the workflow affects other people, publishes content, changes systems or data, spends money, grants access, or informs a consequential decision. Capstone examples remain examples unless a real evidence record is supplied.

## Evaluation

The Practitioner and a named reviewer evaluate the capstone against one gate:

- **Boundary:** the intended task, exclusions, owner, users, inputs, outputs, and risk are explicit.
- **Traceability:** important instructions, sources, changes, decisions, and completion claims can be traced to evidence.
- **Task performance:** the same acceptance criteria are applied to the baseline and workflow output where comparison is claimed.
- **Reliability:** representative cases and at least one adverse or edge case are recorded; failure and recovery behavior are visible.
- **Control:** permissions are least-necessary, approval is placed before consequential effects, and stop or rollback paths are usable.
- **Reproducibility:** another authorized person can follow the documented workflow or identify exactly what access is missing.
- **Honesty:** observations, measurements, examples, hypotheses, and unknowns are distinguishable; unsupported benefit claims are removed.
- **Maintenance:** an owner, review trigger, freshness rule, and unresolved limitations are recorded.

All eight checks must pass for full Guide completion. A failed check produces a revision or an explicitly incomplete dossier, never a partial success claim. The reviewer should be independent of the work where consequences are material or where the Practitioner cannot credibly inspect their own output.

Evaluation shows that the stated artifact met the stated gate in the documented context. It does not establish universal reliability, business value, production readiness, or competence outside the demonstrated boundary.

## Maintainers

Practice guide maintainers own the sequence, cross-module terminology, module contracts, Practice references, capstone gate, and changelog. Module maintainers own the instructional detail and must not silently change the shared outcomes or evidence requirements.

Review this Guide when a referenced Practice changes materially, a module changes its completion check, a route no longer reaches the shared capstone, a link breaks, or the evaluation gate no longer matches the stated outcome. A material path change returns the Guide to draft until the end-to-end path is reviewed.

## Changelog

- **2026-08-31 — 0.2.0 (draft):** Linked all available modules and proposed methods directly, removed stale construction-state language, and kept evidence maturity distinct from file availability.
- **2026-08-31 — 0.1.0 (draft):** Established the shared six-module spine, applied/technical/organizational route overlays, starter path, evidence gate, route-specific capstones, and separately bounded Frontier Studio.
