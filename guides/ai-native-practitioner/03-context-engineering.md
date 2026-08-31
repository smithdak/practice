# Context Engineering: build a governed context pack

Use this module to make a recurring task's context explicit, controlled, and reusable. The outcome is a **context pack**: a small, maintained set of instructions, approved sources, definitions, examples, boundaries, retrieval rules, and checks that another authorized reviewer can inspect and use.

This is Module 3 of [The AI-Native Practitioner](README.md). It builds on the task brief, controlled run packet, and verification record from [Module 2](02-effective-use.md). It does not require a particular model, provider, interface, or context-window size.

Context engineering is not writing one longer prompt. It is designing the information system around a task: what controls, what is current, what may be retrieved, what must be forgotten or excluded, and how a reviewer detects failure. A fluent answer does not show that this system is sound.

## What you will produce

Keep these artifacts together for one recurring, authorized task:

1. A context inventory that separates instructions, sources, examples, definitions, task inputs, working state, and tool results.
2. A source register with authority, owner, freshness expectation, access boundary, and conflict rule.
3. Retrieval and progressive-disclosure rules that introduce only relevant approved material.
4. A context-pack exercise, including an expected output and verification method.
5. A failure diagnosis record and maintenance decision for each unstable component.

The module is complete when another authorized reviewer can identify what controls, what is current, what is excluded, and how to reproduce the intended setup without copying confidential material into an unsafe surface. It does not make the task autonomous or authorize a tool to act.

## Start with a context system, not a prompt

For recurring work, a single block of instructions tends to mix rules that change at different rates: a stable purpose, a current policy, this case's facts, a temporary scratch calculation, and an illustrative example. When those materials are mixed, a later reviewer cannot tell which part caused an error or what should be updated.

Design the pack as separate components with separate jobs.

| Component | Job | Changes when | Must not become |
|---|---|---|---|
| Stable instructions | State the task, output contract, non-goals, and human-owned decisions. | The method or boundary changes. | A container for current case facts. |
| Approved sources | Supply facts, policies, records, or specifications. | The authoritative source changes or reaches its review date. | An unranked document dump. |
| Definitions and glossary | Make task terms and labels consistent. | A term is approved, retired, or clarified. | Unapproved policy or evidence. |
| Examples | Teach format, edge cases, or a permitted method. | The lesson or format changes. | Evidence about the current case. |
| Task input | Describe the current authorized case. | Every run. | A permanent instruction or memory item. |
| Working state | Hold intermediate notes, calculations, or a run log. | During the run. | A trusted source or long-term memory by default. |
| Tool result, if used | Return a defined retrieval or deterministic operation. | Each tool call. | Proof beyond its stated scope. |

Treat a component as **context** only when it has a named job, owner or authority, and handling boundary. If it has no job, remove it. If its authority is unknown, do not put it in the approved pack.

### Exercise 1 — Inventory the task's context

Use a task from Module 2 that recurs or is likely to recur. Do not copy sensitive content into this worksheet; use safe descriptions and source identifiers.

| Component or category | Why this task needs it | Stable / per-run / temporary | Authority or owner | Safe to use in this surface? | Include, retrieve, or exclude? |
|---|---|---|---|---|---|
| Task and output contract |  | stable |  |  |  |
| Approved source |  |  |  |  |  |
| Definition |  |  |  |  |  |
| Example |  |  |  |  |  |
| Current task input |  | per-run |  |  |  |
| Working state |  | temporary |  |  |  |
| Tool result, if any |  | per-run |  |  |  |

**Checkable outcome:** every row is either included with a job and authority, retrieved under a rule, or excluded. “It might be useful” is not a reason to include it.

## Give sources an order, a date, and a conflict response

Authority answers who or what controls when sources differ. Freshness answers when a source must be reviewed, replaced, or removed. A source can be authoritative and still be stale for a particular decision.

Make the hierarchy task-specific. For example, an approved current policy may control an illustrative example, while a current record may control a summary of that record. Do not assume that a newer document automatically overrides a higher-authority one.

### Exercise 2 — Build the source register

Assign each approved source an identifier. Record only the location or safe description needed for a reviewer to locate it.

| Source ID | Purpose and permitted use | Authority rank | Owner | Version/date and freshness expectation | Access / privacy boundary | If it conflicts or is stale |
|---|---|---:|---|---|---|---|
|  |  |  |  |  |  |  |

Use a simple hierarchy only after naming the decision maker for exceptions. A common pattern is:

1. Approved task contract and applicable governing policy or specification.
2. Current, authorized record for the case.
3. Approved reference or operating guidance.
4. Approved definitions and examples, which teach format but do not override facts or policy.
5. Unverified, informal, or unknown material, which is excluded unless a named owner approves it.

Write a specific conflict rule. For example: “When `Policy-2026-04` conflicts with `Example-Intake-2`, follow the policy, identify the example as obsolete in the maintenance record, and ask the policy owner about any ambiguity.” Do not ask the model to reconcile a material conflict silently.

**Checkable outcome:** a reviewer can select the controlling source and the next action for at least one conflict without relying on the generated output.

## Separate instructions from evidence and memory

**Instructions** specify how the task is to be done. **Evidence** supports facts about a case. **Memory** is information retained across runs. **Working state** is temporary material produced or collected during one run. These are different controls.

Do not promote a previous answer, a reviewer comment, or a tool result into memory merely because it was useful once. Before retaining anything across runs, decide whether it is accurate enough, authorized to retain, still necessary, owned by someone, and safe in the destination. When any answer is no or unknown, keep it out of memory or retain only an approved, minimized record.

Use memory only for a justified purpose such as a durable preference approved by the affected person, an approved task configuration, or a maintained glossary. Memory must have a scope, retention or review rule, and a way to correct or remove it. It must not carry confidential details, credentials, access tokens, private keys, or assumptions about a person into another task.

### Exercise 3 — State boundaries

Complete this register before recurring use.

| Item | Is it instruction, evidence, memory, or working state? | Scope | Retain, refresh, or discard rule | Who can correct or remove it? | Prohibited use |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

Write explicit negative rules. Examples: “Do not treat a prior draft as a fact source,” “do not carry a case-specific exception into the next case,” and “do not infer authorization from a tool result.” A negative rule is useful only when the output or review process can reveal a violation.

**Checkable outcome:** every retained item has a reason, scope, maintenance rule, and responsible person; temporary state has a discard rule.

## Use examples and skills without hiding authority

A **skill** is a reusable operating method: its trigger, inputs, steps, outputs, checks, and boundaries. In this module, a skill might be “produce a source-backed intake summary.” A skill is not a claim that every task should use a model or a permission to take action.

Examples can teach a format, a distinction, or an edge case. Label their origin, intended lesson, and limits. An example that contains a plausible but unsupported fact can be copied as if it were evidence; do not use one unless its lesson is clear and it is safe to expose.

| Asset | Include only when | Label it with | Do not use it to |
|---|---|---|---|
| Skill definition | The recurring method, owner, and checks are known. | Trigger, inputs, output, human boundary, and stop condition. | Grant tools or autonomy not documented in the task. |
| Format example | It demonstrates the required shape. | Origin, lesson, and whether it is synthetic. | Support facts about the current case. |
| Edge-case example | It exposes a known failure or exception. | Condition, expected response, and limit. | Replace an applicable policy or decision maker. |
| Prior approved output | It is authorized and still relevant as a format reference. | Date, scope, and that it is not current evidence. | Become a source of facts or retained personal memory. |

**Checkable outcome:** a reviewer can distinguish a method, example, and current evidence without reading between the lines.

## Retrieve deliberately and disclose progressively

**Retrieval** means selecting an approved source or portion of a source for the current task. **Progressive disclosure** means loading the minimum necessary layer first, then adding more approved material only when a stated condition requires it. Both reduce irrelevant material and make the run easier to review. They do not establish that the selected material is complete or correct.

Start with the task contract, output shape, applicable stable instructions, and the smallest relevant source set. Add a source, section, definition, or tool call only when it answers a named question needed for the output. Preserve the source identifier and selection reason. Do not make broad retrieval a substitute for a source hierarchy.

### Exercise 4 — Write the disclosure rule

Define layers for the recurring task.

| Layer | Introduce | Only when | Record | Stop or escalate when |
|---|---|---|---|---|
| 1. Task frame | Task contract, allowed output, and boundary. | Every run. | Pack version and task ID. | Required purpose, owner, or approval boundary is missing. |
| 2. Core evidence | Minimum approved current sources. | The source register permits the task. | Source IDs, versions/dates, and selection reason. | A required source is unavailable, stale, or unauthorized. |
| 3. Definitions / examples | Only items needed to interpret or format the task. | A term or shape is ambiguous. | Item ID and lesson. | The example conflicts with an instruction or source. |
| 4. Additional retrieval / tool result | A specific unanswered question requires it. | The tool or source is permitted. | Query or request category, result scope, and error. | The result is out of scope, incomplete, or implies an unauthorized action. |

For each layer, state what is deliberately absent. For example, an intake-summary task may retrieve the current authorized record and approved checklist, while excluding unrelated historic records, personal notes, and previous outputs.

**Checkable outcome:** a reviewer can reconstruct why each material item entered the run and identify which items were intentionally withheld.

## Define tools as bounded interfaces

When a task uses a tool, describe the interface rather than treating the tool as an all-knowing extension of the model. Define its exact purpose, accepted inputs, returned fields, permissions, predictable errors, and what the result cannot establish. A tool may retrieve a record, calculate a value, or create a draft artifact; it must not receive more access than the task needs.

| Tool or operation | Allowed purpose | Minimum input | Returned output | Permission and effect boundary | Error / empty-result response | Do not infer |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

Examples of limits: a search result does not establish that all relevant sources were found; a retrieved record does not prove it is current; a calculator result does not validate the inputs; an empty result may mean a query mismatch rather than absence. Tool output remains an input to be checked against the task's authority and freshness rules.

If a tool can write, send, publish, purchase, change access, or otherwise create an effect, keep that effect out of this module's exercise unless an explicit task boundary, named approver, recovery path, and authorization already exist. A context pack by itself does not grant permission.

## Protect privacy, security, and the task budget

Before preparing the pack, minimize what the task needs. Use public, synthetic, de-identified, or summarized material only when it is authorized and still answers the task question. De-identification can fail when details are combined, so removing a name is not automatically sufficient.

Keep secrets, credentials, access tokens, private keys, confidential material, regulated information, and unauthorized personal information out of any surface not approved to handle them. Do not use retrieval, memory, or a tool as a route around normal access controls. Stop and escalate to the accountable owner or appropriate privacy, security, legal, policy, or subject-matter contact when handling authority is unclear.

Context also has a resource cost. More material can cost more to process, take longer to inspect, and make relevant instructions or evidence harder to locate. The appropriate limit depends on the task, model, tool, and approved environment; do not assume a universal context-window size. Control the budget by:

- keeping a concise stable instruction layer and linking to approved sources rather than duplicating them;
- retrieving the smallest relevant section or record, with its source identifier and date;
- removing repeated, irrelevant, or superseded material instead of layering it indefinitely;
- asking for an inspectable intermediate output before a broad final response; and
- measuring only local run facts you actually record, such as selected-source count, review burden, or an observed processing cost when available.

Do not claim that a larger context, lower token count, or a particular retrieval method improves quality without task-specific evidence. The objective is sufficient, authorized context that a reviewer can understand—not maximum volume or minimum cost in isolation.

### Exercise 5 — Run the boundary and budget check

Answer before each new pack version:

- Is every included item authorized for this exact surface and task?
- Is each item necessary, or is there a smaller approved alternative?
- Can a reviewer identify the source, authority, version/date, and permitted use?
- Is confidential, personal, regulated, credential, or security-sensitive material excluded or handled in an approved setting?
- Does every retained memory item have a scope, owner, and correction/removal path?
- Can any tool result be mistaken for a complete, current, or authoritative answer? If so, is its limit stated?
- Can the next layer be added only for a named question, rather than because “more context might help”?

Any `no` or `unknown` is a stop, revision, or escalation condition—not an instruction to proceed more carefully.

## Diagnose context failure at the right layer

Do not repair every weak output by adding more material. Preserve the failure and test one likely cause at a time. Change as little as possible so the result says something about the context system rather than a collection of unrelated changes.

| Observed failure | Test first | Likely response | Do not conclude |
|---|---|---|---|
| Required fact or field is missing. | Was the required source or output instruction available and specific? | Add or clarify the minimum approved item; rerun the defined check. | That every future case needs all available sources. |
| Output follows an outdated rule. | Check source date, freshness expectation, and controlling authority. | Replace or quarantine the stale item; record the maintenance action. | That a newer but lower-authority item controls. |
| Output combines incompatible instructions. | Inspect hierarchy and conflict rule. | Select the named controlling source or escalate the unresolved conflict. | That the model should decide policy precedence. |
| Output is distracted, generic, or misses a constraint. | Remove irrelevant context; test the task contract and disclosure rule. | Narrow the packet or make the constraint observable in the output contract. | That a bigger context is automatically safer. |
| Output invents a claim or hides uncertainty. | Check evidence/source boundaries and verification rule. | Require source locations and unresolved-question fields; correct or reject unsupported output. | That a citation-shaped label proves support. |
| Same task changes across runs without a known reason. | Compare pack versions, selected sources, working-state carryover, tools, and task inputs. | Version the changed component; reset unintended state; rerun a comparable case. | That the variation identifies a single cause without a controlled test. |
| Tool result leads to a wrong conclusion. | Check query scope, permissions, returned fields, error handling, and source freshness. | Correct the interface rule or reject the conclusion; verify independently. | That the tool result is complete or authoritative by default. |
| Sensitive information appears or an unsafe action is proposed. | Check data boundary, memory scope, tool permissions, and approval point. | Stop the run, contain it under applicable policy, and escalate to the accountable owner. | That a revised instruction alone resolves an exposure. |

### Exercise 6 — Run a controlled failure diagnosis

Choose one ordinary case and one case likely to expose a limitation, such as a stale reference or conflicting example. If execution is not authorized, write a reproducible planned trial instead; do not invent a result.

```text
Task and pack version:
Case identifier or safe description:
Expected output and verification rule:
Observed failure or planned failure condition:
Hypothesis: missing / stale / conflicting / irrelevant / unclear / unsafe context,
tool-interface weakness, working-state carryover, or output-check weakness:
Single controlled change:
What stayed fixed:
Result and evidence:
Maintenance decision: keep / revise / replace / remove:
Owner and next review date or trigger:
Remaining uncertainty and escalation needed:
```

For example, a **hypothetical planned trial** may compare a pack containing a current policy and a clearly marked obsolete formatting example. The expected response is to follow the policy, use the example only for layout, and flag any genuine conflict for the policy owner. The trial does not prove general reliability; it tests whether this pack makes the hierarchy visible.

**Checkable outcome:** the record identifies one cause to test, one controlled change, and a maintenance decision. It does not treat a better-sounding answer as diagnosis.

## Capstone — reusable context-pack exercise

Complete this exercise for one authorized recurring task. Until the planned [Reusable Context Pack Practice](../../practices/001-context-pack.md) is published and reviewed, this is a scaffold that implements its intended discipline, not a substitute for that Practice.

```text
# Context pack

## Purpose and accountability
Recurring task and intended outcome:
Accountable owner, final reviewer, and authorized users:
Human-owned decision, prohibited actions, and stop condition:
Pack version and last review:

## Stable instructions
Task method and output contract:
Required fields, source-support rule, and uncertainty labels:
Non-goals and prohibited claims:

## Source register and hierarchy
Source ID, purpose, authority rank, owner, version/date, freshness expectation,
access boundary, and conflict response for every approved source:

## Definitions, examples, and skill
Glossary:
Skill trigger, inputs, steps, output, checks, and human boundary:
Example ID, origin, lesson, scope, and limits:

## State, memory, and privacy boundary
What is task input, temporary working state, and retained memory:
Retention, correction/removal, and discard rules:
Minimum necessary data and prohibited categories:

## Retrieval and tools
Progressive-disclosure layers, selection conditions, and excluded material:
For each tool: purpose, input, output, permissions, errors, and non-inferences:

## Verification and failure handling
Expected output and verification method:
Required checks for sources, calculations, analysis, or procedures:
Known failure cases, conflict/staleness response, and escalation path:

## Maintenance record
Component, change trigger, owner, review date or event, and decision:
keep / revise / replace / remove
```

### Capstone review checklist

- [ ] The task, owner, reviewer, output, non-goals, and human boundary are explicit.
- [ ] Every component has a job, and stable instructions are separate from current evidence and temporary state.
- [ ] Every source has authority, freshness, permitted use, and a conflict response.
- [ ] Definitions, examples, and skills are distinguishable from evidence.
- [ ] Memory has a justified scope and correction/removal rule; temporary state has a discard rule.
- [ ] Retrieval follows a progressive-disclosure rule and preserves why each item was selected.
- [ ] Tools, if any, have minimum inputs, permissions, error handling, and non-inferences.
- [ ] Privacy, security, and resource boundaries exclude inappropriate material and unnecessary volume.
- [ ] A failure or reproducible planned trial tests a missing, stale, conflicting, excessive, unclear, unsafe, or weakly checked context condition.
- [ ] Each unstable component has a keep, revise, replace, or remove decision and a named maintenance owner.

## Route extensions

All routes complete the capstone. Add the extension that best matches the work:

- **Applied:** have an authorized colleague use the pack for one comparable case. Record where the instructions, source selection, or review questions were unclear.
- **Technical:** express components in a structured format, implement source loading or tool schemas, and test at least one conflict or stale-source response. Preserve the test result and its limits.
- **Organizational:** add source ownership, approval and update responsibilities, access boundaries across roles, and an escalation route for material conflicts. Do not infer organization-wide readiness from one pack.

## Next module

Continue to the planned Module 4, Automation and Agents, only after the context pack has a bounded task, maintained sources, clear tool and data permissions, a human acceptance point, and a tested failure response. A reusable pack improves repeatability; it does not by itself authorize delegated execution or an external effect.
