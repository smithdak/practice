# Agentic Engineering: deliver a change another engineer can recover and trust

Agentic engineering is not asking an agent to “build the feature” and accepting a confident report. It is the discipline of turning a bounded system change into a specification, an isolated implementation or reviewable brief, and evidence that lets an accountable reviewer decide whether to accept, revise, pause, or recover it.

This is Module 5 of [The AI-Native Practitioner](README.md). It builds on Module 4’s workflow boundary, permissions, approval points, and run evidence. It does not require a particular model, coding agent, source-control host, or continuous-integration service. A code-generating system may help with analysis or implementation, but it does not own acceptance, merge authority, or a consequential release decision.

## What you will produce

For one authorized system change, produce an **implementation brief** that contains:

1. The repository or system context, change boundary, constraints, dependencies, and explicit non-goals.
2. Observable acceptance criteria and a trace from each criterion to planned evidence.
3. A decomposition into bounded tasks, each with a file or component owner and an integration order.
4. An isolation and delivery plan: worktree or equivalent, review route, checks, CI evidence where available, rollback, and handoff.
5. For the technical route, an inspectable change, test outputs, diff inspection, the required independent review, and a delivery or recovery record.

The module is complete when a reviewer can determine what changed or is proposed, why it is within scope, how it was checked, what is still uncertain, and how another authorized person can continue the work. A clean-looking diff, a passing command, or an agent’s completion message alone is not sufficient evidence.

## Start with a task contract, not an implementation request

An engineering task is a small agreement about an outcome and how it will be accepted. “Improve the agent” is not a task: it hides the user, system boundary, changed behavior, affected code, and evidence needed to decide. A useful contract is specific enough that an implementer can work without silently inventing product scope, while leaving unknowns visible for the accountable owner.

Before any implementation, collect only the context needed to make the next decision. In a repository, this usually includes the relevant instructions, architecture or module docs, existing interfaces, nearby tests, change history when it explains a constraint, and the task specification. Do not treat every file in the repository—or a long chat history—as context to load by default. Record the source and version or revision for facts that control the task.

### Exercise 1 — Write the implementation brief

```text
Change name and intended outcome:
System/repository and revision or equivalent baseline:
Accountable owner, implementer, reviewer, and release/merge authority:
User or operator affected, if known:
In-scope behavior, components, files, and interfaces:
Explicit non-goals and unowned paths:
Constraints: compatibility, security/privacy, performance, data, policy, and delivery:
Dependencies, assumptions, and decisions already locked:
Authorized environment, credentials/data boundary, and prohibited actions:
Rollback or containment option if the change is delivered:
Unknowns, decision owner, and stop/escalation condition:
```

Use a safe description when the system or request contains confidential material. Keep secrets, tokens, private keys, confidential records, and unapproved personal data out of task prompts, commits, test fixtures, logs, and handoffs. If required context cannot be safely used in the available environment, stop and escalate; do not move it to a different tool or agent to complete the task.

**Checkable outcome:** a reviewer can identify the intended change, the boundary, who has authority at each decision, and at least one condition that stops work rather than inviting a guess.

## Make acceptance observable before writing code

An **acceptance criterion** describes a condition that must be true for the change to be accepted. It is not a promise such as “works well,” and it is not an implementation instruction such as “use a new helper.” Good criteria describe externally visible behavior, structural constraints, safety boundaries, and the evidence that will establish each one.

Write the verification plan beside the criterion. A test proves only the condition and environment it covers; an inspection confirms only what the reviewer actually inspected. Keep that limit in the record.

| ID | Acceptance criterion | Evidence method | Owner of check | Limit of the evidence |
|---|---|---|---|---|
| AC-1 |  | Test, inspection, source comparison, or approved manual procedure |  |  |
| AC-2 |  |  |  |  |

Prefer criteria a reviewer can answer with `pass`, `fail`, or a documented exception. For example:

- “The command rejects an input that lacks the required identifier and returns the documented error state.”
- “Only the named documentation module and its task handoff change.”
- “All relative links introduced by the change resolve in the repository validator.”
- “An independent reviewer inspects the final diff for scope, safety boundary, and evidence traceability.”

The criterion “the agent implements the requested behavior” is circular. The criterion “CI is green” is incomplete unless the relevant CI job, revision, result, and what it does not test are recorded. If a requirement is subjective, name the decision owner and decision rule; do not pretend it became objective because it was placed in a checklist.

### Connect acceptance to the Verification Gate

This module uses the planned **Agent Verification Gate Practice** as its acceptance boundary. Until that Practice is published and reviewed, use the [Practice index](../../practices/README.md) and apply the gate below as this module’s scaffold. The gate separates a proposal or generated claim from accepted work:

1. **Inspect the contract:** confirm the task, non-goals, authorized scope, and acceptance criteria are current.
2. **Inspect the artifact:** review the diff, implementation brief, configuration, or output against the contract; do not rely on a summary alone.
3. **Run or examine checks:** collect the specified test, static, structural, or manual-check evidence, including failures and environment limits.
4. **Review independently when warranted:** use a reviewer who did not make the change, especially for consequential behavior, security, data, permissions, irreversible effects, or a change too complex for the original implementer to assess alone.
5. **Decide and record:** accept, reject, revise, pause, or escalate. A release or merge authority makes the consequential delivery decision.

Independence is a control against an unchallenged assumption, not a ritual. A separate agent’s restatement of the implementer’s report is not independent review. The reviewer needs the task contract, actual artifact, check outputs, and authority to report a failure. For a low-consequence documentation correction, fresh human diff review may be proportional. For an access-control change, independent review and the applicable security process are a minimum starting point, not an optional polish step.

**Checkable outcome:** every completion claim has a named evidence method, and the acceptance record distinguishes evidence actually obtained from checks still planned.

## Decompose by interface and ownership

Task decomposition breaks a change into units that can be planned, implemented, reviewed, and integrated without two people modifying the same responsibility invisibly. It is not a request to create the maximum number of agent tasks.

Start from boundaries that already matter: public interface, data contract, state transition, migration, test suite, documentation, deployment configuration, or a single coherent file. A task should have one primary deliverable, one accountable owner, a stated dependency, and a definition of done. If it touches an interface shared with another task, assign the interface contract to exactly one owner or sequence the tasks so the dependency is explicit.

| Task | Deliverable and boundary | Files/components owned | Depends on | Acceptance evidence | Integrates after | Owner |
|---|---|---|---|---|---|---|
| T1 |  |  |  |  |  |  |
| T2 |  |  |  |  |  |  |

**File ownership** means one task has authority to edit a named file for this change. It does not mean the owner controls every future use of the file or can broaden the task. When a file must be changed by two tasks, choose one of these controls before work begins:

- combine the overlapping work under one owner;
- split the file at a stable interface and make each output a separate owned path;
- make one task produce a proposal or contract, then have a later integration task edit the shared file; or
- serialize edits, with the second task starting from the reviewed first change.

Do not solve overlap with instructions such as “be careful,” “coordinate in chat,” or “take whichever lines you need.” Those phrases leave no integration rule and make silent overwrite likely.

### Exercise 2 — Build a task graph

For each task, fill in the table and add a short dependency graph. The arrows represent required completed evidence, not merely a preferred order.

```text
T1 (contract or interface decision) → T2 (implementation) → T4 (integration and verification)
T3 (independent test or review input) ─────────────────────→ T4
```

Then test the graph:

- Can two tasks change the same file, schema, API, configuration, or release artifact? If yes, assign one owner or sequence them.
- Can each task finish without waiting on a vague question from another task? If no, move that question into a prerequisite decision.
- Does an integration task own the combined behavior and final verification? If no, create one or keep the change sequential.
- Can a task make an external effect, change permissions, or publish without the designated authority? If yes, narrow its permission or add an approval gate.

**Checkable outcome:** every changed file or component has one task owner at a time, and a reviewer can explain the integration order without reconstructing private messages.

## Plan the change, then let evidence revise the plan

Planning does not mean predicting every line of code. It means identifying the smallest safe path to the acceptance criteria, the questions that could invalidate that path, and the checks that should run before integration.

Use a plan that distinguishes facts from assumptions. An assumption is a candidate to test, not a hidden instruction for an agent. Update the plan when inspection, a failing test, a reviewer finding, or a changed dependency proves it wrong. Preserve the reason for material changes so later reviewers do not mistake a detour for the intended design.

| Step | Planned action | Input or dependency | Expected evidence | Stop/replan when | Status/revision note |
|---:|---|---|---|---|---|
| 1 | Read task-owned context and baseline behavior. | Task contract, relevant sources, baseline revision. | Context record; affected paths. | Scope or authority is unclear. |  |
| 2 | Define or confirm contract and acceptance mapping. | Requirements and existing interface. | Criterion table. | A criterion cannot be checked. |  |
| 3 | Implement in isolated area. | Approved plan and owned files. | Focused diff. | New dependency or shared ownership appears. |  |
| 4 | Run targeted checks, then broader required checks. | Build/test instructions. | Command, environment, result, limits. | A check fails or cannot run. |  |
| 5 | Inspect diff and obtain proportional independent review. | Final candidate and evidence. | Findings and resolution. | Scope, safety, or acceptance mismatch. |  |
| 6 | Integrate or hand off under designated authority. | Accepted evidence. | Commit/revision, CI and delivery status. | CI/release condition fails. |  |

A model can propose this plan, but the accountable person must decide whether its premises match the repository and authorization boundary. “The agent found no issues” is not a plan revision decision.

## Isolate implementation and keep the baseline recoverable

An isolated work area reduces accidental interference; it does not make an unreviewed change safe. For repository work, a **Git worktree** is one way to give a task its own directory and branch while sharing repository history. An equivalent isolation method may be a separate branch, sandbox, change list, or controlled environment, provided the baseline, ownership, and integration route remain visible.

Before implementation, record the baseline revision, task branch or change identifier, work area, owned paths, and commands permitted in that environment. Keep unrelated edits out. Do not overwrite a colleague’s uncommitted work, force changes onto a shared branch, or use an agent’s access to bypass normal review or deployment rules.

```text
Baseline revision or change identifier:
Isolated work area and branch/change ID:
Task-owned files/components:
Files explicitly excluded or reserved by another task:
Permitted commands and authorized environment:
Required test/static/structural checks:
Expected integration target and authority:
Rollback or revert path:
```

Small, focused commits make recovery and review easier. A commit records a unit of change; it is not proof that the unit meets the acceptance criteria. Before sharing it, inspect the status and diff for unexpected files, generated artifacts, secrets, credentials, broad formatting churn, or changes outside the task contract. If an unrelated change is present, keep it out of the task deliverable and surface the conflict to its owner.

### Exercise 3 — Write the isolation and integration record

Complete the record above and add:

```text
Integration order and prerequisite revisions:
How conflicts will be detected and who decides resolution:
Whether squashing, rebasing, or another history operation is permitted:
CI job(s), required status, and where results are recorded:
Delivery gate: who may merge, deploy, publish, or otherwise create an effect:
Post-delivery observation or rollback trigger:
```

Do not claim a rollback exists merely because version control can revert a commit. A revert may not undo a migration, message, cache change, data effect, or downstream use. State the real containment or compensating action for consequential changes.

## Verify at multiple layers

The right checks depend on the change. Use the narrowest check that can expose a likely failure early, then run the broader checks required by the task or repository. A passing unit test does not prove integration behavior; a successful build does not prove the correct behavior was built; a visual check does not prove a permission boundary; CI success does not prove a deployment occurred.

| Evidence layer | Question it answers | Example evidence | Does not establish by itself |
|---|---|---|---|
| Source/contract inspection | Did we understand the current requirement and constraints? | Approved specification, source comparison, decision record. | That the implementation matches it. |
| Static or structural check | Is a defined invariant or format satisfied? | Type check, linter, schema validation, link check. | Runtime behavior beyond the rule. |
| Focused automated test | Does the changed unit behave for specified cases? | Test name, input class, result, environment. | Untested cases or integration. |
| Integration/manual check | Does the composed path meet the criterion? | Reproducible procedure, screenshot/log where appropriate, reviewer observation. | Broad reliability or production impact. |
| Diff inspection | Did the candidate stay in scope and avoid suspicious changes? | Reviewed diff and changed-file list. | Hidden runtime behavior. |
| CI/delivery evidence | Did required automated checks run for the candidate revision? | Job URL/identifier or retained output, revision, status, timestamp when available. | That all relevant tests exist, or that a release is safe. |

Record the exact command or procedure, the relevant revision, whether it passed, failed, or was not run, and the reason. Never replace a failed check with an unqualified statement that it is “probably fine.” A check that cannot run because credentials, platform, time, or environment are unavailable is an explicit limitation. The release/merge authority decides whether it blocks delivery.

### Exercise 4 — Create the verification matrix

| Acceptance ID | Check/procedure | Preconditions and environment | Result/evidence location | Reviewer | Remaining limitation | Decision |
|---|---|---|---|---|---|---|
| AC-1 |  |  | pass / fail / not run |  |  |  |
| AC-2 |  |  |  |  |  |  |

For changes produced with an agent, inspect the diff before running commands that could have broad effects. Generated code can add an unexpected dependency, delete a guard, modify a configuration default, or turn an example into a production path. Treat generated tests as code to review too: they may exercise the implementation’s assumptions rather than the requirement.

**Checkable outcome:** the evidence matrix makes a failed or missing check visible and prevents a reviewer from mistaking a completion report for verification.

## Use parallel agents only for genuinely independent work

Parallel work is useful when tasks have independent inputs, disjoint ownership, low-cost integration, and a clear acceptance contract. It adds coordination cost: more context can drift, ownership can overlap, reports can hide failures, and integration can become the actual unsolved task. Start sequentially when the interface, architecture, risk boundary, or acceptance criteria are still changing.

Parallelize research, isolated test design, documentation, or changes to disjoint files only after the shared contract is stable. Assign a human or designated integration task ownership of the final combined behavior. Agents may prepare evidence and recommend actions; they may not silently merge, release, delete content, alter permissions, or expand their task boundary.

| Anti-pattern | Why it fails | Control or safer alternative |
|---|---|---|
| “Everyone improve the feature.” | No shared acceptance rule or boundary; duplicate and contradictory changes are likely. | Write a task contract, then assign disjoint deliverables. |
| Multiple agents edit the same central file. | Line-level conflict and semantic overwrite can survive a clean merge. | Give that file one owner; serialize or use a dedicated integration task. |
| Parallel tasks choose the API independently. | Each implementation can pass local checks while the combined system disagrees. | Set the interface contract first and make it a prerequisite. |
| Collect summaries instead of artifacts. | Confident messages conceal diffs, failed checks, and changed assumptions. | Require branch/change ID, owned paths, diff, exact checks, results, and limitations. |
| Merge every completed branch at once. | The combined failure has no clear source and review becomes shallow. | Integrate in declared order; run checks and inspect after each meaningful integration. |
| Let agents resolve conflicts by “best judgment.” | A conflict can encode product, security, or ownership decisions the agent lacks authority to make. | Stop at semantic conflicts; send options and evidence to the named decision owner. |
| Retry agents until one reports success. | Selection rewards a plausible report, not correct behavior. | Preserve failures, tighten the criterion, and verify one candidate against the same gate. |
| Give every agent broad repository, tool, or deployment access. | A local task can cause unrelated changes or expose unnecessary data. | Apply least privilege: scoped worktree, paths, tools, credentials, and no external effect without approval. |

### Decision rule for parallelism

Use this test before assigning more than one implementation task:

1. Is the task contract and interface stable enough that each worker can proceed without inventing a shared decision?
2. Does each worker have disjoint files/components and a named owner, or an explicit serialization rule?
3. Can each result be checked independently before integration?
4. Is there an integration owner, order, and final verification plan?
5. Does the expected benefit exceed the coordination, review, and recovery cost?

If any answer is `no` or `unknown`, do not parallelize that implementation boundary. Research can still proceed in parallel if it cannot change the shared artifact and its findings remain proposals.

## Worked example — a bounded Practice swarm task

This is an **illustrative plan based on Practice’s K008 task contract**, not a report of an observed outcome or a claim that the swarm has delivered reliable results. The task is to write the Agentic Engineering module and its handoff. Its declared owned outputs are one module file and one handoff; the task contract also requires a repository validator, a commit, and a clean worktree.

| Task | Owner and isolated area | Owned output | Acceptance evidence | Integration rule |
|---|---|---|---|---|
| K008 authoring | One worker in an assigned K008 worktree. | `guides/ai-native-practitioner/05-agentic-engineering.md` | Module content covers the assigned subjects; task validator passes; diff inspection. | The author does not edit the curriculum map, task manifest, or another worker’s handoff. |
| K008 handoff | Same worker because it describes the same change. | `handoffs/K008.md` | Handoff records status, validation, decisions, risks, and deferred opportunities. | Write only after the final evidence is known; do not copy a completion claim from chat. |
| Integration/review | Designated reviewer or maintainer, outside the author’s acceptance claim. | Review decision and any merge/delivery record. | Inspect contract, final diff, validation output, scope, limitations, and commit. | The reviewer decides acceptance or revision; no automatic conclusion follows from task completion. |

The decomposition is deliberately small. Splitting the module prose and its handoff across agents would create unnecessary dependency: the handoff must accurately reflect the final module and validation. Giving a second worker the curriculum file merely to add a link would violate ownership and create an unneeded integration task. The responsible plan is one isolated authoring task, then independent review.

The example also shows a useful context-recovery path. A successor begins with the task contract, project operating documents, relevant prior module, curriculum contract, baseline revision, final diff, validation command and result, and the handoff. They do not need access to the author’s private chat or to believe a summary that says “done.” This plan does not state whether any specific command, review, or merge has occurred; those belong in an actual delivery record.

## Make handoffs usable without private context

A **handoff** is an operational record for the next accountable person. It is not a victory note. It should let a successor recover the objective, baseline, choices, evidence, unfinished work, and safe next action without reconstructing an agent conversation.

Write the handoff only after checking the final artifact and collecting available evidence. Be exact about status:

- `COMPLETE` means the task’s owned artifacts and required evidence are complete under the stated acceptance decision. It does not claim system-wide reliability or production impact.
- `BLOCKED` means a concrete authority, evidence, environment, dependency, or ownership condition prevents safe completion. State the smallest decision or access needed to proceed.
- `PARTIAL` may be useful inside a local workflow, but do not represent it as accepted delivery unless the project’s process permits that status.

Use this handoff structure:

```text
# <change or task> handoff

## Status
COMPLETE | BLOCKED

## Objective and boundary
What this task was authorized to change; baseline/revision; explicit exclusions.

## Changes and rationale
Owned files/components changed and the decision each change implements.

## Acceptance and validation evidence
Criterion → inspection/test/check → command or procedure → result → limitation.
Include failed or not-run checks and their resolution or blocker.

## Integration and delivery state
Work area/branch or change ID; prerequisite and resulting revisions; CI/delivery status;
merge/release authority; rollback or containment state.

## Decisions, risks, and context recovery
Task-local decisions; open assumptions; known risks; sources/documents a successor must read;
the next safe action and named decision owner.

## Deferred opportunities
Adjacent ideas intentionally not implemented because they exceed this task boundary.
```

Link to durable artifacts or record safe identifiers rather than pasting confidential material. Record what a command actually returned, not only `PASS`. A missing CI run, unperformed independent review, or delivery pending external approval belongs in the handoff even if every local check passed.

### Exercise 5 — Recovery drill

Give the implementation brief, final diff or proposal, verification matrix, and handoff to a reviewer who did not author the work. Ask them to answer:

1. What was authorized to change, and what was excluded?
2. Which revision or baseline did the work start from?
3. Which acceptance criteria have direct evidence, and which remain unverified?
4. What failed, was not run, or required an exception?
5. Who can decide merge, release, rollback, or a scope change?
6. What is the next safe action if the original implementer is unavailable?

If the reviewer cannot answer from the artifacts, revise the handoff or implementation brief. Do not solve a recovery failure by adding a longer chat transcript; extract the missing decision, evidence reference, or ownership boundary into the durable record.

## Capstone — controlled implementation and delivery record

Complete the universal brief for one proposed or implemented system change. Technical-route Practitioners add a bounded change in an isolated work area. Applied-route Practitioners may commission, inspect, and accept or reject a reviewable brief without claiming they implemented it. Organizational-route Practitioners add decision rights, maintenance ownership, and evidence requirements for an internal or vendor delivery team.

```text
# Agentic engineering capstone

## 1. Change boundary
Outcome, owner, users, system/repository baseline, in-scope components/files,
non-goals, constraints, dependencies, data/permission boundary, and stop conditions:

## 2. Acceptance contract
For every criterion: pass/fail rule, evidence method, check owner, and limitation:

## 3. Decomposition and ownership
Task graph, owned paths/components, shared-interface decisions, integration order,
and parallelism decision with reasons:

## 4. Implementation and isolation
Plan and revisions; worktree/branch or equivalent; changed artifacts; commit/revision;
unexpected findings and how scope stayed controlled:

## 5. Verification Gate record
Contract inspection, diff inspection, tests/static/structural/manual checks, CI evidence
where available, independent-review finding and resolution, and acceptance decision:

## 6. Delivery and recovery
Merge/release authority and state; rollback/containment; handoff; known limitations;
next owner and next safe action:
```

**Completion check:** an authorized reviewer can trace each material claim to an inspected source, diff, test, check, or explicit limitation. They can recover the work without private chat history, and no agent report is accepted as evidence without the Verification Gate.

## Decide what the evidence supports

Use the weakest accurate statement. A passing targeted test supports “this candidate passed the recorded case under this environment.” It does not support “the system is reliable,” “the deployment is safe,” or “parallel agents improved engineering.” A completed review supports the scope of that review, not every possible failure mode. If the evidence is not available, say `unknown`, preserve the open question, and route the decision to the owner.

The enduring skill is not making an agent produce more code. It is making every proposed change legible enough that the next Practitioner can inspect it, verify it, recover from it, and improve the method without guessing.
