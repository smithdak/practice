# Foundations: frame a bounded AI task

Use this module to decide whether one small AI-assisted task is safe and checkable enough to test. The outcome is a **task-and-risk brief**: a record that says what goes in, what may happen, who decides, and what counts as acceptable.

This is the first module of [The AI-Native Practitioner](README.md). It requires no coding and no particular model, provider, or interface. Choose a real task you are authorized to examine, or use a clearly labeled representative task. Do not enter confidential, personal, regulated, or otherwise restricted material merely to complete an exercise.

## What you will produce

By the end, keep these four artifacts together:

1. A plain-language system trace.
2. An output contract with an acceptable example or specification and a rejection example.
3. A decision for every input category and tool permission.
4. An evaluation plan and a task-and-risk brief.

The module is complete when a named reviewer can explain where source facts, generated inference, deterministic operations, and human judgment enter the task; see the boundary; and use the acceptance and stop rules. It does not establish that a model is reliable in general or that the task is ready to automate.

## Start with a bounded task

Pick one outcome small enough to inspect in one sitting. Good starting tasks produce a draft, classification, extraction, comparison, explanation, or checklist for a person to review. Avoid a task when you lack authority for its inputs, cannot check the output, or cannot limit the consequence of a bad result.

State the task as an outcome and boundary, not as a request for a clever prompt.

> **Hypothetical example:** Turn one approved public policy document into a five-item internal briefing draft. The communications lead checks every claim before sharing it. The system may not send, publish, or decide anything.

The example is a teaching scenario, not evidence that any system performs the task well.

### Exercise 1 — Write the task card

Record the following. A short answer is enough; unknown is an acceptable answer if it changes the decision to test.

```text
Task outcome:
Accountable owner:
People who use or are affected by the output:
Current method or baseline:
In scope:
Out of scope:
Failure consequence:
Human decision that remains human-owned:
Why this is safe enough to test now:
```

**Checkable outcome:** another person can tell what will and will not be tested without opening an AI tool. If they cannot, reduce the scope before continuing.

## Understand the moving parts

An AI-assisted task is a chain, not a single answer. Trace each handoff:

```text
authorized input → instructions and relevant context → model → optional tool → output → human decision → permitted effect
```

A model produces a likely continuation from patterns in its input. Its wording can be fluent, useful, and still wrong, incomplete, outdated, or inconsistent with another run. Probabilistic behavior is not randomness without limits: instructions, context, settings, tools, and output constraints shape the result. They do not turn generated text into proof.

Keep four kinds of work distinct:

| Kind | What it does | What to record |
|---|---|---|
| Source fact | Comes from an approved document, database, observation, or person. | Source, version or date, and authority. |
| Generated inference | A model drafts, summarizes, classifies, or suggests based on its inputs. | It is generated; note uncertainty or required support. |
| Deterministic operation | A fixed rule or calculation gives the same result for the same valid input. | Rule, formula, or tool result and its inputs. |
| Human judgment | A person chooses a policy interpretation, priority, approval, or exception. | Decision maker and reason. |

Retrieved material is still source material, not a guarantee. A tool result can be incomplete, stale, mis-scoped, or misinterpreted. Treat both as inputs that need the authority and freshness appropriate to the task.

### Exercise 2 — Draw the system trace

Use the table below for your task. Do not include sensitive contents; name the category or a safe description instead.

| Step | What enters or happens | Kind | Owner or authority | Check / boundary |
|---|---|---|---|---|
| Input |  | source fact / other |  |  |
| Context |  | source fact / instruction |  |  |
| Model |  | generated inference |  |  |
| Tool, if any |  | deterministic operation / source fact |  |  |
| Output |  | generated inference |  |  |
| Decision |  | human judgment |  |  |
| Effect |  | human or deterministic action |  |  |

**Checkable outcome:** mark at least one human decision and one boundary where the test stops. If the trace includes a consequential effect without a reviewer before it, remove that effect from the test or add approval.

## Give the output a contract

Ask for an output that a reviewer can inspect. A structured output is information arranged in named fields, a table, a form, or another predictable shape. Structure makes omissions and checks easier to see; it does not make the content true, safe, or appropriate.

For every field, decide whether it is:

- generated text that needs review;
- a source-backed fact that needs a citation or source location;
- a deterministic value that needs a calculation or tool check; or
- a human decision that the model must leave blank or label for review.

Use only fields needed for the task. A smaller contract is easier to validate and less likely to invite invented detail.

### Exercise 3 — Specify acceptance and rejection

Write an output contract. For the hypothetical briefing, it might be:

```text
Required fields:
- five plain-language points
- source section or paragraph for each point
- uncertainties or missing information
- reviewer decision: accept, revise, reject

Prohibited:
- claims not supported by the approved document
- a recommendation presented as policy
- publication, sending, or a final approval
```

Then record two examples:

- **Acceptable example or specification:** enough fields are present, each factual point is traceable to an approved source, uncertainty is visible, and the reviewer can make the final decision.
- **Rejection example:** six polished points with no source locations, or a point that turns an ambiguous statement into a definite policy claim. Record why it fails and what happens next.

**Checkable outcome:** a reviewer can reject an output using the contract without relying on whether it sounds convincing.

## Treat context and tools as controlled inputs

Context is the information and instructions available to the task at the time it runs. It may include a task brief, definitions, examples, current sources, and temporary working material. More context is not automatically better: irrelevant, conflicting, or stale material can obscure the task or cause a mistaken answer.

Give each context item a job. Separate stable instructions from task-specific material, and separate approved sources from examples. If sources conflict, identify who decides which controls; do not ask the model to silently choose.

A tool lets the system retrieve information or perform an action outside the model's generated text, such as looking up an approved record or calculating a total. A tool has a boundary: inputs it receives, permissions it has, results it returns, errors it can produce, and actions it must never take. Do not grant a tool permission just because a future version of the task might need it.

### Exercise 4 — Make the context and tool register

For every input category and possible tool permission, make one decision.

| Item or permission | Needed for this test? | Authorized to use? | Safe in this surface? | Authority / freshness | Decision and reason |
|---|---:|---:|---:|---|---|
| Approved public document |  |  |  |  | allow / exclude |
| Internal material |  |  |  |  | allow / exclude |
| Personal or client data |  |  |  |  | allow / exclude |
| Web or external retrieval |  |  |  |  | allow / exclude |
| Read from an internal system |  |  |  |  | allow / exclude |
| Write, send, publish, purchase, or change access |  |  |  |  | allow / exclude |

Use “exclude” when any answer is no or unknown. For an allowed item, state the minimum necessary content and access. For an action permission, name the human approval required before an effect. A test can use no tools; that is often the clearest first boundary.

**Checkable outcome:** every input and permission is explicitly allowed or excluded. “The model will be careful” is not a control.

## Protect privacy and security before testing

Privacy asks whether people and their information are handled appropriately. Security asks whether systems, data, and permissions are protected from unwanted access or change. The two overlap, but neither replaces the other.

Before entering any material, check authorization, necessity, and the approved handling rules for the surface you plan to use. Prefer a public, synthetic, de-identified, or minimized sample when it can answer the learning question. De-identification can fail when details can be combined to identify someone, so do not assume removing a name makes data safe.

Keep the test from becoming a route around normal controls:

- do not paste secrets, access tokens, credentials, private keys, or confidential documents into an unapproved surface;
- do not use an AI system to bypass access controls or infer information you are not authorized to know;
- do not let generated instructions override the task's data, tool, or approval boundaries;
- do not connect a tool that can make a consequential change until its necessity, permission, review point, and recovery path are documented.

Stop and ask the accountable owner or appropriate privacy, security, legal, or policy contact when authorization is unclear, a sensitive category appears, or the task could materially affect a person, system, money, access, or published information. This module does not replace an organization's policies or professional advice.

### Exercise 5 — Run the boundary check

Answer yes or no before a test:

- I am authorized to use every input in this exact setting.
- The inputs are the minimum necessary for the stated task.
- I know the approved handling rules or have excluded the uncertain material.
- No secret, credential, private key, or restricted information is included.
- No output will be sent, published, acted on, or used for a consequential decision without the named review.
- I know who pauses the test if a boundary is crossed.

**Checkable outcome:** all answers are yes. Any no or unknown is a stop condition, not a prompt to proceed carefully.

## Evaluate the task, not the model in the abstract

An evaluation asks a narrow question: did this output meet these criteria for these cases under these conditions? It does not establish a general score for a model or a universal claim of reliability.

Choose checks proportional to the consequence of failure. A low-consequence draft may need completeness, source traceability, and reviewer readability checks. A task that could affect a person, system, money, access, or a public claim needs a tighter boundary, representative and adverse cases, independent review where warranted, and a clear reason not to proceed if controls are insufficient.

Make criteria observable. “Useful” becomes “contains all required fields and the reviewer can locate a supporting source for every factual statement.” “Accurate” becomes specific claim-by-claim checks against an approved source. Do not replace review with a model's self-assessment.

### Exercise 6 — Write an evaluation plan

```text
Test question:
Cases to use: include at least one ordinary case and one case likely to expose a limitation.
Fixed conditions: task instructions, allowed context, tools, and output contract.
Acceptance criteria: observable checks for completeness, support, boundaries, and task-specific quality.
Rejection criteria: what makes the output unusable or unsafe.
Who checks each criterion:
Evidence to retain: output, source/check record, reviewer notes, and decision.
Failure consequence and response: revise, reject, pause, or escalate.
Claim allowed after the test: the weakest accurate claim.
Claim not allowed: for example, general reliability, time saved, or production readiness without separate evidence.
```

**Checkable outcome:** another reviewer can run the same cases, apply the same criteria, and distinguish a pass on one case from a claim about all future cases.

## Capstone — Task-and-risk brief

Combine your artifacts into a brief for one bounded test. Use a safe description in place of sensitive details. Do not run the test if the brief leaves a privacy, security, authority, or review question unresolved.

```text
# Task-and-risk brief

Task and intended outcome:
Accountable owner and named reviewer:
Users or people affected:
Boundary and non-goals:

Inputs and context
- category, source authority, freshness expectation, minimum necessary content, allow/exclude decision

Expected structured output
- required fields; fields needing source support, deterministic check, or human judgment
- acceptable specification/example
- rejection example and response

Tools and permissions
- allowed tools, exact purpose, inputs, outputs, errors, and permission boundary
- prohibited tools, data, actions, and effects

Uncertainty and limitations
- what the model may get wrong, omit, or misinterpret
- what this test will not establish

Evaluation
- cases, fixed conditions, acceptance and rejection criteria, evidence retained
- failure consequence, reviewer decision, and escalation path

Stop condition
- the exact event that pauses the test and who decides what happens next
```

### Capstone review checklist

- [ ] The task has an owner, intended users, boundary, and non-goals.
- [ ] The trace distinguishes source facts, generated inference, deterministic operations, and human judgment.
- [ ] The output has required fields, an acceptable specification or example, and a rejection example.
- [ ] Every input category and permission is allowed or excluded with a reason.
- [ ] Prohibited data, tools, actions, and effects are visible.
- [ ] Acceptance and rejection checks are task-specific and proportional to the failure consequence.
- [ ] A reviewer, evidence record, escalation path, and stop condition are named.
- [ ] The brief makes no unsupported claim about reliability, benefit, or readiness.

If any item is unchecked, revise the boundary or do not proceed. Preserve the reason for a rejected or paused test; it is evidence about the task's current limits.

## Route extensions

All routes complete the capstone. Add only the extension that improves the evidence you need:

- **Applied:** explain the trace aloud to a nontechnical reviewer and use a manual output checklist.
- **Technical:** express the input and output contract in a testable form; specify tool inputs, outputs, permissions, failures, and invariants such as “no unsupported source field may be marked verified.”
- **Organizational:** add data authority, affected roles, policy constraints, consequence tier, and the person who can approve a wider test.

## Next module

Continue to Module 2 only after the capstone has an owner, checkable output contract, privacy/security decisions, evaluation plan, and safe stop. Module 2 uses this brief to compare a baseline and an AI-assisted result; it does not remove the need for human judgment or verification. The shared [curriculum map](CURRICULUM.md) defines the full Guide evidence gate.
