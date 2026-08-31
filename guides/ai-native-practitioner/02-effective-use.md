# Effective Use: complete one task deliberately

Use this module to find out whether AI assistance improves one discrete piece of work under conditions you can inspect. The outcome is a **reviewed task record**: a baseline, an assisted artifact, the changes made during review, a verification record, and a decision about using AI for this task again.

This is Module 2 of [The AI-Native Practitioner](README.md). It builds on the task-and-risk brief from [Module 1](01-foundations.md). It is not a collection of prompts and it does not require a particular model, provider, interface, or job title.

Choose one real task you are authorized to perform and can evaluate. If real material is not safe to use, work from a representative synthetic case and label it as such. Do not enter confidential, personal, regulated, licensed, or security-sensitive material into a surface that is not approved to handle it.

## What you will produce

Keep these artifacts together for one task run:

1. A task brief and a decision on whether to use AI.
2. A baseline result or safe description of the current result.
3. A controlled context packet and an initial assisted output.
4. A revision history with critique reasons.
5. A verification record and final reviewer decision.
6. A before-and-after comparison using the same rubric, with measured observations and limitations.

The module is complete when the result is accepted under predeclared criteria, or explicitly rejected with the failure preserved. A polished answer, a favorable impression, or a shorter elapsed time alone is not completion.

## Keep assistance distinct from delegation

**Assistance** means a person directs the task, supplies or approves the inputs, decides what to ask next, checks the output, and performs any consequential action. This module teaches assistance.

**Delegated execution** means a system is allowed to select steps, use tools, or cause an effect within a defined boundary. For example, a system that chooses records to retrieve or sends a prepared message is doing more than drafting. Delegation needs explicit permissions, approval points, error handling, and recovery; Module 4 addresses how to design that workflow.

| Question | Assistance in this module | Delegated execution |
|---|---|---|
| Who selects the task and inputs? | The Practitioner or named reviewer. | A system may select within an approved rule. |
| Who decides the next step? | The person, after inspecting the result. | The system may decide within a specified boundary. |
| What may the system do? | Produce a draft, analysis, comparison, explanation, or proposed plan. | Use tools or perform defined steps; effects require the documented authority. |
| Who accepts or acts on the result? | A named human. | A named human remains accountable; approvals and rollback must be explicit. |

Do not describe a task as assistance if the system can send, publish, purchase, change access, make a consequential decision, or otherwise create an effect without the human review stated in the task brief. Remove that effect from this module's run.

## Start with the decision to use AI

AI is useful here only when it helps with a defined part of work while leaving acceptance under human control. It can be reasonable for drafting, organizing authorized material, proposing alternatives, translating a known structure into a new form, explaining material, or surfacing questions for a reviewer. It is not automatically the best tool for a task that mentions language or knowledge.

### Exercise 1 — Make a use decision

Before opening an AI system, answer the following. A `no` or `unknown` may be the correct outcome.

| Decision rule | Use AI only when | Do not use AI when |
|---|---|---|
| Authority | You are authorized to use the exact inputs in the chosen surface. | Input ownership, consent, policy, or handling rules are unclear. |
| Safety | You can minimize inputs and keep prohibited data out. | The task would expose secrets, private keys, personal data, confidential material, or restricted information. |
| Checkability | A reviewer can apply a task-specific acceptance rule before any effect. | You cannot tell whether a result is correct, complete, safe, or appropriate. |
| Consequence | The task is low enough consequence for the available controls, or a reviewer can contain failure. | A bad output could materially affect a person, money, access, safety, a public claim, or a binding decision beyond the available review. |
| Method | Generated assistance addresses a real uncertainty or drafting burden. | A deterministic rule, search, calculator, template, existing source, or direct human decision is simpler and sufficient. |
| Evidence | You can preserve a baseline and a checked result. | You need to claim quality, time, cost, or business benefit but cannot measure the relevant local evidence. |

If any right-hand condition applies, select one of these decisions and record why:

- **Do not use AI:** finish with the existing method or a deterministic tool.
- **Reframe:** narrow the task, remove unsafe inputs, or turn a consequential output into a review-only draft.
- **Pause and escalate:** ask the accountable owner or appropriate privacy, security, legal, policy, or subject-matter contact.

Do not compensate for an unsuitable task with a more elaborate prompt. “The model will be careful” is not a control.

**Checkable outcome:** the record names `use`, `do not use`, `reframe`, or `pause and escalate`, and a reviewer can see the rule that led to it.

## Frame the task before requesting an output

A useful task brief gives the system only the work it needs and gives the reviewer a standard for deciding. It is not prose to persuade a model; it is the contract for the run.

### Exercise 2 — Write a task brief

Use this form. Keep unknowns visible instead of filling them with assumptions.

```text
Task outcome:
Accountable owner and final reviewer:
Audience and intended use:
Input categories and source authority:
Minimum necessary context:
Required output shape and length:
Acceptance criteria:
Known uncertainty or judgment calls:
Non-goals and prohibited claims/actions:
What remains human-owned:
Consequence if wrong and stop condition:
```

For example, a **hypothetical** task brief might say: “Prepare a one-page comparison of two approved internal proposals for a program manager. Cite the supplied sections for each factual comparison; label trade-offs as analysis; do not choose a proposal. The program manager verifies every factual statement and makes the decision.” It does not say “make this compelling” or “decide the best option,” because those phrases hide the output contract and ownership.

State criteria that can be observed. Replace “make it accurate and useful” with criteria such as:

- includes every required heading;
- gives a source location for each factual statement;
- separates source-backed facts, generated analysis, and unresolved questions;
- has no claim outside the supplied material; and
- is understandable to the named audience.

**Checkable outcome:** a reviewer who has not watched the run can tell what belongs in the output, what does not, and who makes the final judgment.

## Establish a fair baseline

A baseline is the result of the current method for the same or a meaningfully comparable case. It may be a previous approved artifact, a fresh manual run, or a safe description when the artifact cannot be retained. Do not compare an easy assisted case with a hard manual case and call the difference improvement.

### Exercise 3 — Record the baseline

Use the same task brief, source set, output contract, and rubric you plan to use for the assisted run. Record:

```text
Case identifier and why it is comparable:
Baseline method and version of any template or tool:
Start and finish time, if time is being measured:
Baseline artifact or safe description:
Rubric score or criterion-by-criterion result:
Corrections needed before acceptance:
Reviewer and final decision:
Conditions that make this baseline unlike the assisted run:
```

Time is optional, but if you claim a time difference, record start and finish boundaries consistently. Include human review, source checking, formatting, and rework when they are part of the task. A time measurement from one run is an observation about that run, not a forecast.

Use a simple rubric with no more dimensions than the task needs. For a source-aware briefing, it might be:

| Criterion | Pass condition | Baseline result | Assisted result |
|---|---|---|---|
| Completeness | All required sections and questions are present. |  |  |
| Source support | Every factual statement has a valid source location. |  |  |
| Analysis boundary | Inference is labeled and does not become a fact claim. |  |  |
| Audience fit | Named reviewer can use the result for the stated purpose. |  |  |
| Safety boundary | No prohibited data, action, or claim is present. |  |  |

For each cell, record `pass`, `fail`, or a count such as “2 unsupported factual statements,” with brief evidence. Do not turn subjective judgment into a fictional precise score. If a criterion requires judgment, record the reviewer and reason.

**Checkable outcome:** both methods can be assessed against the same criteria; the record makes material differences in case, inputs, or reviewer visible.

## Control the context, then make a first attempt

Context is the approved information and instructions available at the time of the run. Treat it as a small, versioned packet, not an unbounded conversation. Include only material that has a job in this task.

### Exercise 4 — Assemble a run packet

Separate the packet into four parts:

| Part | Include | Exclude or handle separately |
|---|---|---|
| Task contract | Outcome, audience, output shape, criteria, non-goals, and boundary. | Vague style requests that replace the task contract. |
| Approved sources | Minimum necessary documents, excerpts, records, or safe descriptions with authority and date/version. | Unverified snippets, stale material, and sources whose use is not authorized. |
| Definitions and examples | Terms, formatting rules, and clearly labeled examples that teach the needed structure. | Examples presented as source facts or instructions that conflict with the task. |
| Reviewer controls | Required citations, uncertainty labels, and questions the output must surface. | A request to conceal uncertainty or claim verification that has not occurred. |

Give each source an identifier the reviewer can use, such as `Proposal-A §3` or `Policy-v2 p.4`. Record the packet version or date. If sources conflict, state which authority controls or leave a question for the named decision maker; do not ask the model to silently resolve the conflict.

Ask for the smallest inspectable output first. A table, outline, claim list, or draft with named fields is often easier to verify than a polished, expansive response. The request should restate the output contract and ask the system to mark missing information rather than invent it.

**Checkable outcome:** another person can reconstruct what information and instructions were available for this run without seeing sensitive content.

## Iterate with a stated reason

Iteration is a controlled response to observed gaps, not repeated asking until an answer feels agreeable. Preserve the initial output. Then change one or a small number of things with a reason tied to the task brief or rubric.

### Exercise 5 — Run a critique-and-revision loop

For each output version, record:

```text
Version and timestamp or sequence number:
What changed in task instructions, context, or requested structure:
Why it changed (criterion, observed error, or reviewer question):
What remained fixed:
What the output now passes or still fails:
Whether the change introduced a new uncertainty:
```

Use this sequence:

1. Produce a first output from the approved run packet.
2. Inspect it against the rubric before editing it into a final-looking form.
3. Identify a specific gap: missing field, unsupported claim, misread constraint, unclear audience language, or unresolved question.
4. Revise the instructions, context, or output structure only as needed to address that gap.
5. Re-run or revise, then check the changed output and any parts affected by the change.
6. Stop when the output meets the criteria or the remaining failure triggers rejection or escalation.

Do not use the model's statement that it “checked,” “verified,” or “fixed” something as the check record. It may help propose checks, but a human or appropriate deterministic process must perform them.

**Checkable outcome:** every material revision has a reason, and a reviewer can distinguish a better-controlled run from an answer selected only because it sounds better.

## Critique the work at the right layer

Critique asks whether the output meets the task contract. It is different from requesting a different tone or asking the system to praise its own answer. Use questions that locate an issue:

| Layer | Questions for the reviewer |
|---|---|
| Scope | Did it answer the stated task and avoid the non-goals? |
| Completeness | Are all required fields, cases, and questions present? |
| Evidence | Can every factual claim be traced to an approved source or check? |
| Reasoning | Are comparisons, assumptions, and uncertainty visible rather than presented as facts? |
| Audience | Can the intended reader understand the result and act only within the stated purpose? |
| Boundary | Did it reveal prohibited information, propose an unauthorized action, or cross a human-owned decision? |

Some errors are not repair requests. Reject or pause the run when it contains unauthorized data, a fabricated or materially unsupported claim, a source conflict that matters to the decision, an instruction that crosses the boundary, or a consequence that the current review cannot safely contain.

## Verify output before accepting it

Verification compares the output with an independent source, rule, calculation, or authorized reviewer decision. The appropriate check depends on the claim.

### Exercise 6 — Build a verification record

Use a row for each material claim, calculation, classification, or procedural instruction.

| Item to verify | Type | Check method and independent source/rule | Result | Reviewer | Response if failed |
|---|---|---|---|---|---|
|  | source fact / calculation / analysis / procedure |  | pass / fail / unresolved |  | correct / remove / reject / escalate |

Apply these rules:

- **Factual claims:** compare them with the approved source and preserve the location. A citation is a pointer, not proof; verify that it actually supports the claim.
- **Calculations:** recompute with an approved deterministic method, input record, or tool. Do not accept an arithmetic explanation as a calculation check.
- **Analysis and recommendations:** check that the source facts support the stated reasoning, counterarguments or uncertainty are visible when material, and the final decision remains with the named human.
- **Procedures:** compare steps with the authoritative policy, instructions, or subject-matter reviewer. If authority is unclear, mark the item unresolved rather than treating a plausible procedure as correct.
- **Generated code or structured data, when relevant:** run the task-level test or validator that demonstrates the stated requirement; inspect the result and limits. A successful run does not prove untested behavior.

Verification is not necessarily a second model call. A second generated answer can expose a disagreement, but it is not independent evidence of truth.

**Checkable outcome:** each material output element is accepted, corrected, removed, rejected, or explicitly unresolved; no final artifact implies verification that the record does not show.

## Use patterns, not role-specific prompts

The same deliberate sequence works across roles: frame, bound context, produce, critique, verify, decide. The task and verification method change with the work.

| Work pattern | Useful bounded output | Primary verification | Human-owned judgment |
|---|---|---|---|
| Research | Source map, evidence table, or question list. | Open each cited source; check date, authority, and support. | Which sources are credible enough and what conclusion follows. |
| Analysis | Comparison table, assumptions register, or scenario explanation. | Recompute values; trace evidence; test stated assumptions. | Which trade-off or decision criterion matters. |
| Writing | Outline or draft with source notes and open questions. | Check claims, required content, audience fit, and approvals. | Message, voice, publication, and final wording. |
| Planning | Draft plan, dependency map, risk list, or agenda. | Compare with commitments, constraints, owners, and dates. | Priorities, commitments, resources, and approval. |
| Learning | Explanation, practice questions, or error log. | Solve independently, consult an authoritative source, or have an instructor review. | Whether understanding is sufficient and what to study next. |
| Professional work | Draft deliverable or checklist from approved material. | Use the governing standard, client-approved source, or authorized reviewer. | Advice, sign-off, representation, and any consequential action. |

These are patterns, not a guarantee that every task in a category is suitable. A research summary involving confidential records, a planning task that commits resources, or professional advice affecting another person can require a different surface, extra review, or no AI use at all.

### Role examples

The following are hypothetical examples, not measured case studies or recommendations to use a particular tool.

- **Operations practitioner:** prepares a draft weekly exception summary from an approved, de-identified export. The run records each exception's source row, labels proposed follow-up as a draft, and the operations lead decides whether any action is taken. It does not connect to the system that changes orders or customer accounts.
- **Engineer:** turns an approved issue description and repository conventions into a proposed test plan. The engineer checks that every proposed test maps to a stated behavior, runs applicable tests separately, and decides whether to implement. A passing test run is evidence about those cases, not proof that the change is complete.
- **Consultant or professional-services lead:** creates a discovery-question outline from public client materials and an approved brief. The lead checks every client-specific claim, removes unsupported assumptions, and obtains the required review before sharing. The outline does not provide professional advice or make commitments for the client.
- **Manager or internal champion:** drafts a meeting options memo from approved notes. The manager verifies attributed decisions and owners, marks unresolved trade-offs, and retains the decision. The output does not assign work or announce a policy.

## Compare the result honestly

Compare the baseline and assisted result only after both have been reviewed against the same rubric. The comparison can show an observed difference for this case; it cannot establish general reliability, expected savings, or a business outcome without additional evidence.

### Exercise 7 — Write a before-and-after record

```text
Case and fixed conditions:
Baseline result by rubric:
Assisted result by rubric:
Measured values and method (for example, elapsed task time, required-section count,
unsupported-claim count, or reviewer corrections):
Material differences in inputs, tools, reviewer, or case difficulty:
What AI assistance contributed, if anything:
What still required human judgment or manual work:
Remaining uncertainty and failures:
Decision: retain as assisted practice / revise and retest / do not use / pause and escalate
Decision maker and date:
Weakest accurate claim:
Claim this evidence does not support:
```

For example, a measured observation might be: “On this identified case, the assisted draft met 4 of 5 rubric criteria before review and required two factual corrections; the manual baseline met 5 of 5 and required one correction. Timing was not measured. Decision: revise the source-check step before another trial.” This says more than “AI was helpful” because it preserves the method, failure, and limit.

Possible measurable evidence includes elapsed time under a consistent boundary, count of required sections present, count and kind of reviewer corrections, rubric result, number of source-backed claims, or number of unresolved items. Choose measures that reflect the task's real acceptance criteria. Do not combine unlike measures into an invented quality score.

**Checkable outcome:** the continued-use decision is supported by artifacts and local measurements, and the claim stops at what this run actually shows.

## Capstone — a reviewed real-work run

Run one bounded task from brief to decision. Use a real workflow you are authorized to examine. A recurring task is preferable because the resulting record can inform the next run, but this capstone does not authorize automation.

If the real workflow cannot be used safely, complete the exercise with a representative synthetic case and state that it is synthetic. Do not represent it as evidence of workplace impact.

```text
# Reviewed task record

## Task and decision
Task outcome:
Owner, reviewer, audience, and intended use:
Use decision and reason:
Boundary, non-goals, human-owned decision, and stop condition:

## Comparable case and baseline
Case identifier or safe description:
Baseline method, artifact/safe description, and fixed conditions:
Baseline rubric and review result:

## Assisted run
Approved context packet and version/date:
Initial output and output contract:
Version history: change, reason, result, and new uncertainty:
Assistance/delegation boundary and tools used:

## Critique and verification
Rubric applied to both methods:
Verification record for material claims, calculations, procedures, or analysis:
Corrections, removals, rejected output, and unresolved items:
Final reviewer decision:

## Before-and-after evidence
Measures, method, and values:
Differences that limit comparison:
Weakest accurate claim and unsupported claim to avoid:
Continued-use decision, owner, and next bounded action:
```

### Capstone review checklist

- [ ] The task is real and authorized, or is explicitly identified as a representative synthetic case.
- [ ] A task brief identifies the audience, criteria, non-goals, owner, and human-owned decision.
- [ ] The record states why AI was used, reframed, or not used.
- [ ] Baseline and assisted work use the same rubric and comparable conditions.
- [ ] The run packet identifies approved context and excludes prohibited material.
- [ ] The initial output and material revisions are preserved with reasons.
- [ ] Factual, analytical, calculated, and procedural elements have appropriate checks.
- [ ] Corrections, rejection criteria, and remaining uncertainty are visible.
- [ ] At least one local before-and-after measure has a stated method and value, or the record explains why no comparative measure is being claimed.
- [ ] The final decision names what remains human-owned and whether to retain, revise, stop, or escalate the practice.

If the assisted result fails the rubric, preserve the failure. A rejected run can be a successful learning outcome when it shows that the task, context, controls, or use decision needs to change.

## Route extensions

All routes complete the capstone. Add the extension that improves the evidence needed for your work:

- **Applied:** have an authorized colleague use the same task brief and rubric on one comparable case; record where operating instructions or review questions were unclear.
- **Technical:** express the input and output contract in a testable structure, compare manual and tool-supported checks, and retain the test command or check result with its limits.
- **Organizational:** add the review owner, downstream users, decision-right boundary, and a small adoption check that shows whether a role can apply the method; do not infer organization-wide impact from one run.

## Next module

Continue to the planned Module 3, Context Engineering, only after this record shows a bounded task, a controlled context packet, a reviewable output, and an honest decision about continued use. That module turns the useful parts of this one-off run into a maintained context system; it does not convert a passing run into permission for delegated execution.
