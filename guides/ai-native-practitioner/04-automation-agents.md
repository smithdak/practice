# Automation and Agents: make a workflow dependable before making it autonomous

Start with a deterministic sequence and a human approval point. An automation that reliably prepares a reviewable draft, stops on exceptions, and can be undone is often more useful than an agent that can choose its own next action. This module moves a recurring task from a governed context pack to the smallest repeatable workflow that the accountable owner can inspect, run, recover, and improve.

This is Module 4 of [The AI-Native Practitioner](README.md). It uses the bounded task, checked output, and maintained context pack from Modules 1–3. It does not require a particular model, provider, framework, scheduler, or unattended execution.

**Automation** is a repeatable sequence with defined inputs, rules, outputs, and effects. **An agent** is a bounded system that can choose among permitted next steps toward a goal, usually by observing state and using tools. The distinction matters because choice creates more possible paths to test, supervise, and recover. Neither term grants authority to act.

## What you will produce

For one authorized recurring task, produce:

1. A before-and-after workflow map with triggers, decisions, handoffs, exceptions, and every human step visible.
2. A step-classification decision for each step: human-owned, deterministic, AI-assisted, or agentic.
3. A control record for inputs, context, state, tools, permissions, approval, errors, observability, rollback, and recovery.
4. Representative and adverse-case tests, an observed run record or a clearly labeled planned trial, and a reviewer decision about the next boundary.

The module is complete when another authorized person can operate the bounded workflow, see what happened in a run, contain an error, and decide whether to retain, revise, pause, or narrowly expand it. A successful demonstration does not establish broad reliability or justify more autonomy.

## Redesign the work before automating it

Do not automate a vague process merely because it recurs. First make the current method visible. Separate a required decision from a historical habit, and eliminate a step only when the accountable owner agrees that its purpose is covered elsewhere.

### Exercise 1 — Map the current workflow

Use a safe description or synthetic example if real case detail is not authorized for this record.

| Sequence | Trigger or input | Current step | Output / handoff | Decision owner | Exception or failure | Evidence kept |
|---:|---|---|---|---|---|---|
| 1 |  |  |  |  |  |  |

Mark steps that create an external effect, such as sending a message, publishing, changing a record, spending money, changing access, or making a commitment. Those effects need explicit authority and recovery rules; a model recommendation or tool result is not authorization.

Then ask, in order:

1. Can the task be removed, combined, or handled with a maintained template?
2. Is the desired output and its acceptance rule stable enough to repeat?
3. Are inputs, source authority, data handling, and the accountable owner clear?
4. Can a human review the output before a consequential effect?
5. If the workflow is wrong, can the effect be stopped, reversed, or contained?

Any `no` or `unknown` is a redesign, pause, or escalation condition. It is not a reason to add an agent.

**Checkable outcome:** the map identifies the trigger, a named decision owner, every handoff, all known exceptions, and any irreversible or hard-to-reverse effect.

## Choose the smallest control that fits each step

Autonomy is a design variable: the amount of discretion granted inside a boundary. More autonomy is not an objective. Choose it step by step, based on whether the method and branches are known, whether the result can be checked, and whether failure can be contained.

| Step type | Use it when | Required control | Do not use it when |
|---|---|---|---|
| Human-owned | Judgment, accountability, permission, or a consequential decision must remain with a person. | Named owner, decision record, and escalation route. | A repeatable rule can safely reduce clerical work without moving the decision. |
| Deterministic automation | Inputs, rules, and expected branches are known. | Input validation, versioned rules, idempotency or duplicate handling, logs, and a recovery path. | The needed judgment or branch cannot be stated and checked. |
| AI-assisted step | A person can use a generated draft, classification, extraction, or proposed next step before deciding. | Fixed output contract, source/check rule, human acceptance, and no unapproved effect. | The output cannot be reviewed before it matters. |
| Bounded agentic step | Choosing among a limited set of permitted next steps is necessary and can be observed, stopped, and recovered. | Goal, maximum loop, allowed tools, state boundary, permissions, approval gates, error paths, audit record, and stop conditions. | A sequence, queue, checklist, or human judgment is simpler or safer. |

A deterministic workflow can still contain an AI-assisted draft. For example, a fixed sequence may retrieve approved records, validate required fields, ask for a structured draft, run a deterministic completeness check, and place the draft in a review queue. The sequence—not the model—controls when it stops and what can happen next.

### When an agent is unnecessary

Do not use an agent when any of the following is true:

- the sequence and its branches are already known well enough to encode or follow as a checklist;
- a template, rule, search, calculation, integration, or queue solves the task without discretionary planning;
- the task requires a human-owned decision, authorization, interpretation, or relationship judgment;
- the output cannot be checked before an effect, or failure has no credible containment or rollback path;
- tool access, source authority, state retention, or permitted action is unclear; or
- the local value of reducing handoffs does not justify the added design, testing, monitoring, and recovery burden.

“The task is complicated” is not evidence that an agent is needed. A useful reason is narrower: “The workflow must choose one approved data source based on a documented case type, then request human review before any external action.” If that choice can instead be a deterministic mapping, use the mapping.

### Exercise 2 — Classify the redesigned workflow

For each mapped step, record a choice and reason.

| Step | Classification | Why this is the smallest adequate control | Human approval or owner | Inputs and source boundary | Effect, if any | Stop or escalation condition |
|---|---|---|---|---|---|---|
|  | human / deterministic / assisted / agentic |  |  |  |  |  |

Do not hide a manual handoff because it feels less automated. A visible approval queue can be a correct and durable design.

**Checkable outcome:** every agentic step names the decision it must make that a deterministic sequence cannot reasonably make, and every other step has an explicit non-agent rationale.

## Make deterministic automation reliable first

Begin with a dry run or review-only output. Give the workflow one clear trigger, a stable input contract, and a predictable result for the same authorized inputs. Make re-running safe where possible: an **idempotent** operation can be retried without creating an unintended duplicate effect. If true idempotency is not possible, use an explicit duplicate check, unique run identifier, or manual confirmation before repeating the effect.

| Control | Define before operation | Evidence or recovery |
|---|---|---|
| Trigger and scope | Who or what starts the run; case boundary; run identifier. | Record the trigger, time, operator or service identity, and input version. |
| Input validation | Required fields, allowed formats, source freshness, and rejected inputs. | Reject or quarantine invalid input with a reason; never guess a missing critical value. |
| Rules and versions | Deterministic rules, template, context-pack version, and output schema. | Preserve identifiers so a reviewer can reconstruct the run. |
| Duplicate protection | Idempotency key, deduplication rule, or confirmation point. | On retry, show whether the effect already occurred and who resolves ambiguity. |
| Approval | What is draft-only, who may accept it, and what acceptance permits. | Keep the approval decision, reviewer, and scope; rejected output must not proceed. |
| Rollback and recovery | Reversible action, compensating action, or containment procedure. | Test or inspect the path; record what cannot be undone and who handles it. |

Avoid connecting the first version directly to a consequential action. Route it to a reviewable artifact, queue, or sandbox first. If a proposed effect cannot be made reviewable and recoverable, keep the step human-owned or redesign the process.

### Exercise 3 — Write the deterministic run contract

```text
Workflow name and purpose:
Accountable owner, operator, reviewer, and escalation contact:
Trigger and allowed case scope:
Required inputs, source authority/freshness, and validation rule:
Deterministic steps and versioned rules:
AI-assisted step, if any; output contract and verification rule:
Draft-only output, approval point, and permitted effect after approval:
Run identifier and duplicate/retry rule:
Expected success state and observable completion signal:
Stop, quarantine, and escalation conditions:
Rollback, compensating action, or containment path:
Data/state retention and discard rule:
```

**Checkable outcome:** an authorized operator can tell whether a run is eligible to start, whether it completed, whether it is safe to retry, and what to do if it fails.

## Add an agent only inside a bounded loop

If a task truly needs an agentic step, define the loop before choosing a framework. The agent receives a narrow goal and operates only inside a declared maximum boundary. A useful generic loop is:

1. **Observe:** read the allowed task input, approved state, and permitted tool results.
2. **Propose or plan:** select a next action from the allowed action set and record the reason in the run state.
3. **Act:** call at most one permitted tool with validated, minimum-necessary input, or request approval.
4. **Check:** validate the tool result or proposed output against the task rule; do not treat a tool result as proof beyond its stated scope.
5. **Record and decide:** write an observable state transition; continue only while within the goal, budget, permission, and loop limit. Otherwise stop, hand off, or escalate.

The loop must not silently invent new tools, permissions, goals, sources, or effects. A request for an unavailable tool, ambiguous instruction, unexpected result, exceeded limit, or permission denial is a state transition to handle—not an invitation to work around the boundary.

### Agent boundary record

| Element | Define | Example of a bounded rule |
|---|---|---|
| Goal | The specific outcome, case scope, and non-goals. | “Prepare a source-backed draft exception summary for this case; do not send or decide.” |
| Allowed next actions | Small, enumerated action set and order constraints. | “Retrieve approved record, validate fields, create draft, request review, stop.” |
| Maximum boundary | Maximum tool calls, elapsed time, cost or resource budget when locally available, and loop count. | “No more than three retrieval calls and one draft attempt; then hand off.” |
| Tools | Exact purpose, minimum input, returned fields, effect level, and non-inferences. | “Lookup returns a specified record; it does not establish completeness or approval.” |
| State | Per-run facts, plan, action history, and outcome; no unstated cross-run memory. | “Discard task-specific working state after the retention rule; retain only the approved run record.” |
| Permissions | Least privilege by tool, data scope, and effect. | “Read only the named case; write a draft in the review space; no send, publish, purchase, or access changes.” |
| Human gates | Conditions requiring review or an explicit decision. | “A human accepts the draft and separately initiates any external message.” |
| Stop and escalation | Terminal states and owner. | “Stop on conflict, stale source, missing field, tool failure, uncertain match, or limit exceeded; notify the named owner.” |

### Exercise 4 — Specify the agent loop

Complete this only for a step classified as agentic. Otherwise record why no agent is required.

```text
Goal, allowed case scope, and non-goals:
Accountable owner and human acceptance point:
Allowed observations and approved context-pack version:
Allowed actions and exact tool interfaces:
Prohibited tools, data, actions, and external effects:
Per-run state fields; retained state fields; retention/correction/discard rules:
Maximum loops, tool calls, resource budget, and elapsed time:
Required checks after each action:
States: ready / running / awaiting approval / completed / stopped / failed / quarantined:
Each transition, including who or what may trigger it:
Stop conditions, error responses, and escalation contacts:
Rollback or containment plan for every permitted effect:
Run-log fields and reviewer evidence:
```

**Checkable outcome:** a reviewer can enumerate what the agent may observe, do, retain, and never do without inferring permissions from a general goal.

## Treat tools, state, and permissions as separate controls

A tool is a bounded interface, not a general capability. State is a record of a particular run, not a reason to retain everything it sees. Permissions constrain both access and effect. Define each separately; combining them under “the agent can handle it” hides the review surface.

| Tool or state item | Purpose | Minimum input or content | Output / transition | Permission and effect boundary | Error / stale / empty response | Must not infer or retain |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

Apply least privilege: provide only the data scope and tool capability needed for this step. Keep credentials, access tokens, private keys, and secrets out of prompts, logs, working state, and outputs. Do not use a tool, memory store, or agent handoff to bypass normal access controls.

For cross-run information, state a justified purpose, owner, retention limit or review trigger, and correction/removal path. A previous draft, tool result, or reviewer note is not automatically trustworthy memory. If retention is not required and authorized, discard it when the run closes.

## Design error paths, rollback, and recovery before the happy path

Reliable workflows make adverse outcomes visible. An error message alone is not recovery. Define what enters a safe stopped state, what is quarantined for review, who is notified, what evidence is preserved, and whether a retry is allowed.

| Condition | Detect with | Immediate response | Retry or rollback rule | Owner / escalation | Evidence to retain |
|---|---|---|---|---|---|
| Missing or invalid input | Input validation | Do not begin; mark incomplete. | Retry only after authorized correction. |  |  |
| Stale or conflicting source | Source register and conflict rule | Stop affected step; do not choose silently. | Resume only after controlling source or decision is recorded. |  |  |
| Tool error or empty result | Tool response and timeout | Move to failed or quarantined state. | Retry only within the duplicate rule; otherwise investigate. |  |  |
| Output fails verification | Required check | Reject draft; prevent effect. | Revise input/rule or hand off; preserve failure. |  |  |
| Unauthorized or sensitive data | Boundary check or report | Stop, contain under applicable policy, and escalate. | Do not retry by moving data to another surface. |  |  |
| Effect partially completed | Effect receipt and reconciliation | Contain downstream change; alert owner. | Use the named rollback/compensating action; record residual impact. |  |  |
| Limit exceeded or unexpected path | State machine and budgets | Stop rather than extend authority. | Human decides whether to retry, revise, or abandon. |  |  |

**Rollback** restores the prior state when that is possible. A **compensating action** records or corrects a completed effect when restoration is impossible. Do not call an apology or a rerun a rollback. For an irreversible effect, the design must name containment and human ownership before it is allowed.

### Exercise 5 — Inspect or test recovery

Choose at least one credible adverse case. If execution is not authorized, write a reproducible planned test and label it as such.

```text
Workflow version and case description:
Adverse condition and how it is introduced or observed:
Expected stopped/quarantined state:
Expected notification, evidence, and prohibited next action:
Rollback, compensating action, or containment step:
Who decides whether to resume:
Observed result or planned-test limit:
Decision: retain / revise / pause / escalate:
```

Do not claim rollback works because it is documented. An inspected procedure is evidence that a path was specified; an executed test is evidence only about the tested condition.

## Make operation observable and evaluable

**Observability** is the ability for an authorized reviewer to determine what a workflow did from its recorded inputs, state changes, tool results, checks, and decisions. It is not a reason to log sensitive inputs or hidden reasoning. Record the minimum safe evidence needed to reconstruct the run.

Use explicit states rather than “it ran”: `ready`, `running`, `awaiting approval`, `completed`, `stopped`, `failed`, and `quarantined` are examples. Define what each means for this workflow and which transitions are permitted. A completed draft is not an approved external effect.

| Run-record field | Why it matters |
|---|---|
| Run ID, workflow/version, trigger, and case-safe identifier | Separates runs and permits comparison without copying unnecessary detail. |
| Input/source identifiers, authority, and freshness status | Shows what controlled the run. |
| State transitions, timestamps where locally recorded, and actor/tool identity | Shows the sequence and where responsibility changed. |
| Tool request category, result status, and error code or safe summary | Supports diagnosis without treating the result as complete truth. |
| Checks, approval/rejection, reviewer, and reason | Shows why a draft was accepted, corrected, stopped, or escalated. |
| Effect receipt, rollback/containment decision, and residual uncertainty | Connects any effect to recovery and ownership. |

Evaluate the workflow against predeclared task criteria, not whether the output sounds capable. Test representative cases plus at least one adverse, ambiguous, or edge case. Keep the case conditions comparable when comparing versions. Record a local observation—such as pass/fail by criterion, number of review corrections, or number of stopped runs—only when you actually preserve the underlying evidence. Do not infer time savings, reliability, safety, or business impact from a small trial.

### Exercise 6 — Build the evaluation set and run record

| Case | Why it represents normal or adverse operation | Fixed inputs/context and workflow version | Expected state and acceptance rule | Observed result or planned result | Limitation and next decision |
|---|---|---|---|---|---|
| Representative case |  |  |  |  |  |
| Edge or adverse case |  |  |  |  |  |

For each observed run, preserve:

```text
Run ID and workflow version:
Case-safe description and authorization:
Starting state, input/source checks, and trigger:
Actions and tool results, with state transitions:
Output and task-specific verification result:
Human approval, correction, rejection, or escalation:
Any effect and its receipt; rollback/containment status:
Unexpected behavior and response:
Reviewer decision and remaining uncertainty:
```

**Checkable outcome:** a reviewer can distinguish a proposed workflow, a passing run, a failed run, and a production-ready claim that the evidence does not support.

## Capstone — bounded automation with review and recovery

Run the smallest safe version of a recurring workflow from its trigger to a reviewable outcome. A manual transfer between steps is allowed. The capstone may remain review-only; it does not need to perform an external effect. If no run is authorized, submit a reproducible proposed workflow or Lab plan and do not represent it as operation evidence.

An example **hypothetical** capstone is a weekly exception-summary workflow. A deterministic sequence validates an approved, de-identified export, selects the current approved context pack, creates a structured draft, checks that every exception has a source-row identifier, and places it in an operations-lead review queue. The lead corrects or accepts the draft; no system sends messages or changes records. An agent is unnecessary if the exception-selection rules are fixed. If a bounded choice among approved retrieval paths is genuinely necessary, its tool calls remain read-only, its loop has a maximum, and it stops for review before the draft leaves the queue.

Use this dossier structure:

```text
# Bounded workflow dossier

## Purpose and boundary
Recurring task, accountable owner, operator, reviewer, and authorized users:
Case scope, inputs, source authority, and context-pack version:
Intended output, acceptance criteria, non-goals, and prohibited effects:

## Before and after workflow map
Current steps, decisions, handoffs, exceptions, and evidence:
Redesigned steps and classification reasons:
Reason for deterministic automation, assistance, agent use, or no agent:

## Operation controls
Trigger, validation, output schema, versions, run ID, duplicate/retry rule:
Tools, state, permissions, data boundaries, and retention/discard rules:
Approval gate, allowed effect after approval, and effect receipt:
States, observability record, error paths, stop conditions, escalation:
Rollback, compensating action, or containment procedure:

## Tests and evidence
Representative and adverse/edge cases, expected results, and verification method:
Observed run records or clearly labeled planned trials:
Failure, recovery inspection/test, and limits of the evidence:

## Review decision
Reviewer decision: retain / revise / pause / narrowly expand:
What must be true before any autonomy or scope increase:
Owner, review trigger/date, unresolved questions, and next action:
```

### Capstone review checklist

- [ ] The workflow begins from a clear trigger with validation and a human approval point before any consequential effect.
- [ ] Every current and redesigned step, including manual work and exceptions, is visible.
- [ ] Each step is human-owned, deterministic, AI-assisted, or agentic for a stated reason; agent use is not assumed.
- [ ] The deterministic path has versioned rules, duplicate/retry handling, and a safe stop.
- [ ] Any agent has a goal, enumerated actions, limited tools, bounded state, least-privilege permissions, maximum loop, checks, and terminal conditions.
- [ ] Approval, ownership, permissions, data handling, and retained state are explicit.
- [ ] Error paths lead to a stopped, failed, or quarantined state with a named recovery or escalation owner.
- [ ] Rollback, compensating action, or containment is specified for every permitted effect and has been inspected or tested.
- [ ] The run record makes source selection, state transitions, tool status, verification, and human decisions observable without exposing inappropriate data.
- [ ] Representative and adverse or edge cases have results or reproducible planned outcomes; limits are stated honestly.
- [ ] The reviewer explicitly decides to retain, revise, pause, or narrowly expand the boundary. A passing run alone does not expand autonomy.

## Route extensions

All routes complete the capstone. Add the extension that matches the work.

- **Applied:** write an operator checklist and review-queue instructions so another authorized colleague can run the human-reviewed workflow. Record the points where the checklist or approval language caused confusion.
- **Technical:** implement the state machine, tool schemas, permission enforcement, structured logs, and at least one automated or manual rollback/recovery test. Preserve the test evidence and its untested limits.
- **Organizational:** define service ownership, approval queues, escalation coverage, affected roles, policy constraints, and a measured review cadence. Do not infer organization-wide readiness from a single workflow trial.

## Next module

Continue to Module 5, Agentic Engineering, only when the workflow has a stable boundary, accountable owner, inspectable controls, observed or reproducibly planned tests, and a reason to make a system change. Engineering an agent is not the next step for every workflow; retaining a reliable deterministic process or human review can be the correct decision.
