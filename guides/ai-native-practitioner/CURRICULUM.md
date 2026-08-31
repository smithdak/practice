# The AI-Native Practitioner Curriculum Map

This map is the implementation contract for the flagship Guide. It tells Practitioners what to produce and tells module authors what each module must enable. The canonical Guide outcome, metadata, and evaluation gate live in the [Guide README](README.md).

## How to use this map

1. Select one recurring task you know and are authorized to examine.
2. Choose a route based on the evidence you need to produce, not your job title.
3. Complete every universal checkpoint in Modules 1–6 in order.
4. Deepen the exercises marked for your route without skipping the common concepts.
5. Keep one capstone dossier and add evidence to it as you progress.
6. Use the optional Frontier Studio only after the core controls are understood.

If a module file or planned Practice does not yet exist, use the module contract and starter worksheets here. Record that you used the scaffold. Do not represent scaffold completion as completion of unpublished instructional material or as full Guide completion.

## Curriculum architecture

| Stage | Module | Direct capability | Universal checkpoint | Capstone contribution |
|---|---|---|---|---|
| Frame | 1. Foundations | Learn | Make a task-specific model, context, risk, and evaluation decision. | Task-and-risk brief |
| Apply | 2. Effective Use | Use | Complete and check one discrete task against a baseline. | Baseline, work artifact, and verification record |
| Supply | 3. Context Engineering | Use | Build a governed, maintainable context pack. | Context pack and maintenance record |
| Operate | 4. Automation and Agents | Automate | Run a bounded workflow with review and recovery. | Workflow map, controls, tests, and run record |
| Engineer | 5. Agentic Engineering | Build | Specify and verify an inspectable system change. | System brief or implementation and handoff |
| Change | 6. Organizational AI | Transform | Tie the workflow to accountable operating change. | Opportunity map and change brief or pilot model |
| Investigate | Optional Frontier Studio | Learn; Build when implemented | Design a reproducible test without promoting an unsettled idea to Practice. | Lab or research brief kept outside the core completion claim |

The progression is cumulative. Later modules may expose a faulty assumption in earlier evidence. When that happens, revise the earlier artifact and record the change rather than preserving a false linear story.

## Choose a route

All routes share the six-module spine and the same capstone gate.

| Route | Choose it when | Depth emphasis | Final route extension | Does not require |
|---|---|---|---|---|
| Applied | You operate knowledge work, a service, or a business process and need a dependable AI-assisted workflow. | Task framing, context quality, human review, operating instructions, and failure recovery. | Another authorized person can operate the documented human-reviewed workflow. | Coding or an unattended agent |
| Technical | You build or materially change an AI-enabled tool, agent, or integration. | Specifications, system boundaries, permissions, tests, repository controls, independent review, and delivery. | A runnable or inspectable implementation with task-level evidence. | A particular framework or model provider |
| Organizational | You own or influence a team workflow, operating model, governance practice, or adoption program. | Opportunity selection, role and decision-right change, enablement, proportional governance, and operating measures. | A bounded pilot operating model with review and stop conditions. | Organization-wide rollout or invented return-on-investment claims |

A Practitioner can combine routes, but should name one primary capstone. For example, an engineer leading a team pilot may submit the technical capstone and attach the organizational extension. Combining routes adds evidence; it does not lower either route's acceptance criteria.

## Evidence rules

Keep an evidence ledger with each module artifact. For every material claim, record:

| Record | Question it answers |
|---|---|
| Claim | What exactly are we saying happened or is true? |
| Evidence | What artifact, observation, source, test, diff, or measurement supports it? |
| Context | Under what task, inputs, version, permissions, and conditions? |
| Result type | Is it an observation, measurement, example, hypothesis, or unknown? |
| Limitation | What does this evidence not establish? |
| Decision | Accept, reject, revise, pause, or escalate? Who decided? |

Use the weakest accurate claim. One successful output supports “passed this case,” not “reliable.” A documented run supports observed behavior in that context, not a general benefit. Adoption activity shows use, not capability. A prototype shows a possible implementation, not production readiness.

Evidence must be safe to share. Redact or abstract sensitive material while preserving enough information for the reviewer to understand the task and limitation. If redaction destroys reviewability, use an authorized private review process and publish only the bounded conclusion.

## Module contracts

### Module 1 — Foundations

**Direct capability:** Learn — explain and assess a bounded AI task safely and credibly.

**Prerequisites**

- A real or representative task, intended output, and at least one constraint or risk.
- No coding knowledge required.

**Module outcome**

Frame a bounded test that accounts for probabilistic output, context, tool access, structured output, privacy, security, and evaluation. The Practitioner should reason about behavior and controls without relying on a vendor's interface or a volatile product limit.

**Core work**

- Trace the task from input through context, model processing, optional tools, output, and human decision.
- Separate generated content from retrieved source material and deterministic computation.
- Specify the expected output structure and the fields that need source support or human judgment.
- Classify inputs by whether they are authorized, necessary, and safe to provide.
- Define an acceptance check proportional to the consequence of failure.
- Decide what the system must not do and when the test must stop.

**Module capstone**

Produce a task-and-risk brief for one bounded test. Include the task, owner, users, inputs, expected structured output, allowed tools, prohibited data or actions, known uncertainty, failure consequence, acceptance criteria, reviewer, and stop condition.

**Required evidence**

- A plain-language system trace.
- One acceptable-output example or specification and one rejection example.
- A privacy/security decision for every input category and tool permission.
- An evaluation plan tied to the task rather than to general impressions.

**Universal checkpoint**

The Practitioner can explain where source facts, generated inference, deterministic operations, and human judgment enter the task. The planned test has an owner, boundary, acceptance rule, and safe stop.

**Route depth**

- **Applied:** explain the system trace without code and focus on output review.
- **Technical:** add input/output contracts, tool boundaries, and testable invariants.
- **Organizational:** add data authority, affected roles, policy constraints, and consequence tier.

**Downstream artifact contract:** `01-foundations.md` must teach this checkpoint through exercises and include its own capstone. It must not depend on a current vendor-specific product claim.

### Module 2 — Effective Use

**Direct capability:** Use — complete and check a discrete real-work task with AI assistance.

**Prerequisites**

- Module 1 task-and-risk brief.
- A baseline example completed without the proposed AI assistance, or a safe description of the current result.

**Module outcome**

Use deliberate task framing, context, iteration, critique, and verification across a real work task. Distinguish assistance, where a person drives each decision, from delegated execution, where a system chooses or performs steps inside a defined boundary.

**Core work**

- Write a task brief with outcome, audience, inputs, constraints, acceptance criteria, and non-goals.
- Decide whether AI is appropriate. Do not use it when authority is missing, inputs cannot be handled safely, the output cannot be checked, the task is already simpler deterministically, or the consequence exceeds available controls.
- Produce an initial output, critique it against the task criteria, and revise only with a stated reason.
- Verify factual, analytical, and procedural claims using suitable sources or checks.
- Preserve human judgment: record what was accepted, corrected, rejected, or escalated and why.
- Compare the baseline and assisted result using the same rubric.

**Module capstone**

Run one discrete real-work task from brief to reviewed result. Keep the baseline, task brief, relevant inputs or safe descriptions, output versions, critique, source/check record, final decision, and a decision about continued use.

**Required evidence**

- Before-and-after artifacts or safe descriptions.
- A stable rubric applied to both.
- The corrections, rejection criteria, and remaining uncertainty.
- Any observed change reported with its measurement method; no inferred time, quality, or business gain.

**Universal checkpoint**

The result is acceptable under the predeclared criteria, or is explicitly rejected with the failure preserved. The Practitioner can say what still required judgment and whether AI added a controllable benefit for this task.

**Route depth**

- **Applied:** apply the pattern to research, analysis, writing, planning, learning, or professional work without turning the module into a prompt collection.
- **Technical:** add structured inputs/outputs and compare manual versus tool-supported checks.
- **Organizational:** add review ownership, downstream user impact, and evidence that a role can apply the method—not merely that a tool was opened.

**Downstream artifact contract:** `02-effective-use.md` must include role-neutral patterns, role examples, decision rules for non-use, measurable local comparison, and a real-work capstone.

### Module 3 — Context Engineering

**Direct capability:** Use — make a recurring task's context explicit, governed, and reusable.

**Prerequisites**

- Module 2 task brief, checked output, and verification record.
- Access to the approved instructions and sources needed for repeat work.

**Module outcome**

Build context as a designed system: stable instructions, source hierarchy, examples, definitions, state or memory boundaries, retrieval rules, tool definitions, progressive disclosure, and output verification. The design must account for freshness, conflict, privacy, and resource constraints conceptually rather than assume a specific context window.

**Core work**

- Inventory what the task needs to know, decide, retrieve, remember, and ignore.
- Separate stable instructions from task-specific inputs and temporary working state.
- Assign source authority, owner, freshness expectation, and conflict rule.
- Include examples only when their origin, intended lesson, and limits are clear.
- Define retrieval and progressive-disclosure rules so only relevant approved material is introduced.
- Define tool inputs, outputs, permissions, errors, and what the model must not infer from a tool result.
- Diagnose failures by testing missing context, conflicting context, stale context, excessive irrelevant context, unclear instructions, and output-check weakness separately.

**Module capstone**

Produce a reusable context pack for the recurring task. Include purpose, stable instructions, approved sources, source hierarchy, glossary, examples, boundaries, retrieval/disclosure rule, tool definitions if used, expected output, verification, owner, and freshness review.

**Required evidence**

- A manifest of every context component and why it is necessary.
- Source authority and freshness records.
- At least one conflict or stale-source scenario and the expected response.
- A before-and-after run or a reproducible planned trial if execution is not yet authorized.
- A maintenance decision: keep, revise, replace, or remove each unstable component.

**Universal checkpoint**

Another authorized reviewer can tell what controls, what is current, what is excluded, and how to detect context failure. The pack is reusable without copying confidential material into an unsafe surface.

**Route depth**

- **Applied:** create and maintain the pack with ordinary documents and checklists.
- **Technical:** implement structured source loading, retrieval, tool schemas, or state boundaries and test conflicts.
- **Organizational:** define source ownership, approval, update responsibilities, and access boundaries across roles.

**Planned Practice dependency:** Reusable Context Pack, `practices/001-context-pack.md`. Until it exists, the worksheet below is a scaffold, not a mature Practice.

**Downstream artifact contract:** `03-context-engineering.md` must connect to that Practice, include the context-pack exercise and failure diagnosis, and avoid vendor-specific context-window claims.

### Module 4 — Automation and Agents

**Direct capability:** Automate — operate a repeated, reviewable AI-assisted workflow with defined controls.

**Prerequisites**

- Module 3 context pack and maintenance record.
- A recurring trigger, expected output, accountable owner, review point, and known failure consequence.

**Module outcome**

Redesign the work before automating it. Choose deterministic automation, AI assistance, a bounded agent loop, or human ownership step by step. Treat autonomy as a design variable and use an agent only when its ability to choose among steps is necessary and controllable.

**Core work**

- Map the current trigger, steps, decisions, handoffs, data access, output, and exceptions.
- Remove unnecessary work and stabilize ambiguous steps before adding AI.
- Classify each step as human-owned, deterministic, AI-assisted, or agentic and justify the choice.
- For an agentic step, define goal, loop, tools, state, permissions, stop conditions, maximum boundary, and escalation.
- Add observable states, error paths, approval, audit evidence, rollback, and recovery.
- Test representative cases and adverse or edge cases before widening scope or autonomy.
- Prefer a deterministic sequence when the steps and branches are known, or a checked manual workflow when automation cost exceeds the local value.

**Module capstone**

Run the smallest safe version of the redesigned workflow. Human transfer between steps is allowed. Preserve the before-and-after map, step decisions, permissions, review rules, test cases, run log, failure or edge-case behavior, rollback test or inspection, and next autonomy decision.

**Required evidence**

- A workflow map with every manual step visible.
- The reason for each step classification and for agent use or non-use.
- Representative test cases plus at least one adverse or edge case.
- Observed run behavior, including failures; if not run, label it a proposed workflow or Lab.
- A reviewer decision to retain, revise, pause, or expand the boundary.

**Universal checkpoint**

The workflow is reproducible, human review and accountable ownership are visible, failures have a recovery path, and no increase in autonomy is justified solely by a successful demonstration.

**Route depth**

- **Applied:** operate the workflow through checklists and available tools, with manual approvals.
- **Technical:** implement tools, state, observability, error handling, permission limits, and rollback tests.
- **Organizational:** align review queues, escalation, service ownership, policy, and affected roles.

**Planned Practice dependencies:** Workflow Redesign, `practices/002-workflow-redesign.md`, and Agent Verification Gate, `practices/003-verification-gate.md`.

**Downstream artifact contract:** `04-automation-agents.md` must begin with deterministic automation and approval, define the agent boundary, explain when no agent is needed, and make reliability and rollback first-class.

### Module 5 — Agentic Engineering

**Direct capability:** Build — create or materially change an AI-enabled system and evaluate it within a defined boundary.

**Prerequisites**

- Module 4 workflow map, controls, and run evidence.
- For implementation work: an inspectable repository or equivalent change record and an authorized execution environment.

**Module outcome**

Convert a workflow boundary into a precise engineering task and deliver reviewable evidence. Every route learns to specify, commission, inspect, and accept system work; only the technical extension requires writing code.

**Core work**

- Capture repository or system context, constraints, non-goals, dependencies, and acceptance criteria.
- Decompose work into bounded tasks with explicit file or component ownership.
- Plan before implementation and revise the plan when evidence changes.
- Isolate parallel changes, define integration order, and avoid overlapping ownership.
- Require tests, static or structural checks, diff review, independent review where warranted, and continuous-integration evidence where available.
- Record handoffs so another person can recover the objective, decisions, changes, validation, risks, and next action.
- Reject uncontrolled parallelism: no vague shared scope, silent overwrite, unverified aggregation, or completion claim based only on agent messages.

**Module capstone**

Universal: produce an implementation brief containing system context, boundary, acceptance criteria, decomposition, ownership, verification plan, integration order, rollback, and handoff.

Technical extension: implement one bounded change in an isolated work area, run the specified checks, inspect the diff, obtain the required review, and preserve delivery or recovery evidence.

**Required evidence**

- Traceability from each acceptance criterion to an inspection, source, diff, or test.
- Ownership boundaries and integration sequence.
- Test outputs and reviewer findings, including failed checks and their resolution.
- A handoff that supports context recovery without relying on private chat history.
- Known limitations and any unverified claim explicitly rejected or deferred.

**Universal checkpoint**

A reviewer can determine what changed or is proposed, why it satisfies the task, how it was checked, what remains uncertain, and how to recover. Nontechnical Practitioners may pass with a reviewable implementation brief; only a technical-route capstone may claim Build exit evidence.

**Route depth**

- **Applied:** specify a system change, inspect evidence, and make an acceptance decision without claiming implementation capability.
- **Technical:** implement, test, independently review, integrate, and hand off the change.
- **Organizational:** define commissioning boundaries, decision rights, vendor or internal team evidence requirements, and maintenance ownership.

**Planned Practice dependency:** Agent Verification Gate, `practices/003-verification-gate.md`.

**Downstream artifact contract:** `05-agentic-engineering.md` must cover repository context, specifications, planning, worktrees or equivalent isolation, ownership, tests, independent review, CI, handoffs, and safe parallelism. Practice's swarm may appear only as an explicitly worked example without invented results.

### Module 6 — Organizational AI

**Direct capability:** Transform — redesign a team or organizational workflow, decision right, governance practice, or measurement loop around AI-enabled work.

**Prerequisites**

- Module 4 workflow evidence and Module 5 system or implementation brief.
- An identifiable work owner and affected role; authority to propose, though not necessarily approve, a pilot.

**Module outcome**

Start from work and operating outcomes, select a bounded opportunity, and design the role, knowledge, governance, enablement, and measurement changes required to test it. Separate tool adoption from demonstrated capability and business impact.

**Core work**

- Inventory recurring work, constraints, decision points, failure consequences, and current evidence.
- Map opportunities by outcome relevance, feasibility, reviewability, data/access readiness, reversibility, and consequence. Do not invent return on investment.
- Define before and proposed workflows, role changes, decision rights, service ownership, and human accountability.
- Design enablement around role-specific work and evidence, not generic tool exposure.
- Apply governance proportional to consequence, including data, access, approval, monitoring, incident, and rollback responsibilities.
- Define a baseline, process measures, output measures, capability evidence, adoption signals, and review cadence without conflating them.
- Choose a bounded pilot, explicit non-goals, stop conditions, and decision rule for revise, expand, pause, or end.

**Module capstone**

Universal: produce an opportunity map and change brief for the workflow.

Organizational extension: produce a pilot operating model containing the before/proposed work, role and decision-right changes, knowledge sources, controls, enablement, baseline, measures, review cadence, owner, and rollback or stop conditions. Observed results may be added only after a real authorized pilot.

**Required evidence**

- A trace from the selected opportunity to a defined operating outcome and current baseline.
- Separate records for adoption activity, demonstrated capability, workflow performance, and business outcome.
- Named human decision owners and governance controls proportional to risk.
- An explicit distinction between proposal, observed process change, measurement, and hypothesis.
- A decision record after any pilot; before execution, label the artifact as a proposal.

**Universal checkpoint**

The proposal or pilot changes how work and decisions operate, not merely which tool is available. Claims are bounded to measured evidence, and accountable people retain consequential decisions.

**Route depth**

- **Applied:** document how the workflow affects adjacent roles, ownership, and maintenance.
- **Technical:** define service ownership, operational evidence, incidents, changes, and decommissioning.
- **Organizational:** run or prepare the bounded pilot and evaluate operating change with accountable leaders and affected roles.

**Planned Practice dependencies:** Workflow Redesign, `practices/002-workflow-redesign.md`, and Agent Verification Gate, `practices/003-verification-gate.md`.

**Downstream artifact contract:** `06-organizational-ai.md` must connect interventions to measurable operating changes, distinguish adoption from capability, use proportional governance, and avoid a generic transformation narrative.

## Optional Frontier Studio — experiment, do not promote

Frontier work covers techniques whose conditions, reliability, safety, maintenance burden, or value are not established for the Practitioner's task. A topic can be familiar in public discussion and still be frontier work in a specific operating context.

Potential subjects include longer-horizon tool use, adaptive memory, multi-agent coordination, novel interfaces, or systems that revise parts of their own working process. These are examples of experiment areas, not claims about current product capability and not recommendations.

### Entry boundary

Enter only with:

- a completed core task boundary and evaluation gate;
- an isolated, reversible environment;
- safe inputs and least-necessary permissions;
- a testable hypothesis and a simpler baseline; and
- a stop condition that does not depend on the experimental system complying voluntarily.

### Studio outcome

Produce a Lab or research brief that another Practitioner could reproduce. Include:

1. question and hypothesis;
2. task set and baseline;
3. fixed and variable conditions;
4. rubric and evidence capture;
5. permissions, safety boundary, and stop condition;
6. procedure and version record;
7. results, including failures or inconclusive findings; and
8. limitations and the next decision.

### Exit boundary

Studio completion supports a claim about the documented experiment only. It does not promote the technique to an established Practice, justify production deployment, or satisfy the core capstone. Promotion requires the artifact type and evidence process defined in the [knowledge taxonomy](../../docs/framework/TAXONOMY.md) and [Practice schema](../../docs/schemas/PRACTICE_SCHEMA.md).

## Starter path while modules are incomplete

The scaffold below lets a Practitioner begin Modules 1–4 now. It is deliberately smaller than the complete instruction that downstream module files and Practices will provide.

### Starter worksheet A — Task and risk brief

```text
Task:
Accountable owner:
People affected:
Current inputs and authority to use them:
Acceptable output:
Failure consequence:
Human-owned decisions:
Prohibited data, tools, or actions:
Acceptance criteria:
Reviewer:
Stop condition:
```

### Starter worksheet B — Checked use record

```text
Baseline artifact or safe description:
Task brief and non-goals:
Assisted output versions:
Critique against criteria:
Sources or checks used:
Corrections, rejection, or escalation:
Observed comparison using the same rubric:
What the comparison does not establish:
Continue, revise, or stop decision:
```

### Starter worksheet C — Context-pack manifest

```text
Component | Purpose | Authority | Owner | Freshness rule | Conflict rule | Access boundary
Stable instructions:
Approved sources:
Definitions:
Examples and intended lesson:
Task-specific inputs:
Retrieval or disclosure rule:
Tool input/output/permission contract:
Expected output structure:
Verification rule:
Maintenance trigger:
```

### Starter worksheet D — Workflow and run record

```text
Trigger, owner, and expected output:
Before workflow:
After workflow:
For each step: human-owned | deterministic | AI-assisted | agentic, with reason
Inputs, data access, and permissions:
Approval points:
Observable states and run log:
Representative cases:
Adverse or edge case:
Failure, escalation, recovery, and rollback:
Observed result and limitation:
Retain, revise, pause, or expand decision:
```

The starter path is complete when the four records are reviewable and one bounded workflow trial has an explicit accept, reject, revise, or pause decision. It advances Learn, Use, and early Automate evidence. It does not substitute for Modules 5–6, route extensions, downstream canonical Practices, or the full capstone review.

## Shared capstone dossier

Use one directory, repository, or controlled record with this structure:

```text
00-scope-and-baseline
01-task-risk-and-evaluation
02-effective-use-record
03-context-pack
04-workflow-controls-and-runs
05-system-brief-or-implementation
06-operating-change
07-verification-and-review
08-limitations-maintenance-and-next-decision
```

Equivalent names and non-file formats are acceptable if the same evidence is traceable. Do not copy secrets or confidential inputs into the dossier. Record safe descriptions and the authorized location of private evidence instead.

### Route-specific completion

**Applied capstone:** Another authorized person can operate the human-reviewed workflow from the documented trigger through the acceptance decision. The dossier contains observed runs, failure handling, maintenance ownership, and a verification record.

**Technical capstone:** The dossier adds a runnable or inspectable implementation, setup and operating instructions, task-level tests, change review, delivery evidence, known limitations, and recovery behavior.

**Organizational capstone:** The dossier adds a bounded pilot operating model: before/proposed workflow, roles, decision rights, controls, enablement, baseline, measures, review cadence, owner, and stop or rollback conditions. If the pilot has not run, label it a proposal and do not claim Transform exit evidence.

### Final review record

For each Guide evaluation check—boundary, traceability, task performance, reliability, control, reproducibility, honesty, and maintenance—record:

```text
Check:
Evidence inspected:
Result: pass | revise | incomplete
Reviewer and role:
Decision and rationale:
Remaining limitation:
```

Full completion requires every check to pass. Preserve failed or incomplete records so the evidence does not become a polished success narrative after the fact.

## Maintenance contract for module authors

Each downstream module must:

- preserve its direct capability, prerequisite boundary, universal checkpoint, module capstone, and evidence requirements;
- teach operational decisions and failure modes rather than provide a topical reading list;
- keep universal content usable across all three routes and label route extensions clearly;
- link canonical Practices when they exist and avoid copying their full method;
- state when evidence is proposed, observed, measured, independently reviewed, or unknown;
- avoid current product claims when an enduring principle serves the lesson; and
- report any necessary change to the shared path so Guide maintainers can version and review it.

Module completion alone does not establish the next capability level. The relevant exit evidence in the [Capability Ladder](../../docs/framework/CAPABILITY_LADDER.md) remains the controlling standard.
