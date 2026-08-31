# Capability Ladder

## Use the ladder to name the next demonstrated skill

The ladder classifies the capability an artifact, channel, or contribution helps a Practitioner demonstrate. It is not a rank, credential, permission system, or ordering of people. A Practitioner can be at different levels for different kinds of work, and can move in either direction when the context changes.

Choose the level from the outcome and the evidence produced, not from the tool used, job title, or amount of effort. A contribution belongs at the lowest level that fully describes its direct outcome; add cross-capability tags when it deliberately supports another level.

| Level | Demonstrated outcome | It is not |
|---|---|---|
| Learn | Explain and assess how to approach a bounded AI task safely and credibly. | Completing the task in production. |
| Use | Complete and check a discrete real-work task with AI assistance. | A dependable repeated workflow. |
| Automate | Operate a repeated, reviewable AI-assisted workflow with defined controls. | An unattended system or merely a saved prompt. |
| Build | Create or change an AI-enabled tool, agent, or system and evaluate it in its intended boundary. | Configuring a single workflow for personal use. |
| Transform | Redesign how a team or organization performs work around AI-enabled capability and governs the change. | Deploying a tool without changing the operating model. |

## Learn

**Outcome.** A Practitioner can frame a bounded task, explain relevant model, context, tool, limitation, security, and evaluation considerations, and select a safe next test.

**Entry evidence.** Name a real or representative task, its intended output, and at least one constraint or risk. A question, short scenario, or de-identified example is enough; no production result is implied.

**Exit evidence.** Show all of the following:

- a plain-language explanation of the relevant mechanism or limitation;
- a task-specific decision about context, tool use, privacy, or security;
- a check the Practitioner would use to judge the output; and
- the next bounded application or experiment.

**Anti-patterns.** Treating access to a model as understanding; memorizing prompts without explaining when they fail; presenting a reading list as a capability; or claiming a general rule from one untested example.

## Use

**Outcome.** A Practitioner uses AI to complete a discrete piece of real work and applies judgment before accepting the result.

**Entry evidence.** State the task, the acceptable output, available inputs, and who is accountable for the final decision. Use approved, non-confidential inputs or a clearly labeled synthetic example.

**Exit evidence.** Show the input or a safe description of it, the method, the resulting output or decision, and the human check, correction, or rejection criteria used. State what still required judgment.

**Anti-patterns.** Calling a one-off novelty prompt a workflow; accepting generated output without a check; obscuring where the source material came from; or reporting time, quality, or business gains without evidence.

## Automate

**Outcome.** A Practitioner turns recurring work into a repeatable AI-assisted workflow with visible review, failure handling, and an accountable owner.

**Entry evidence.** Identify a recurring trigger, inputs, expected output, review point, failure consequence, and the person or role responsible for the workflow. The workflow may be manual between steps at first.

**Exit evidence.** Provide a reproducible workflow description or configuration, representative test cases, review or approval rules, a recovery path, and observed behavior from a run. If it has not run in a real setting, label it a proposed workflow or a Lab rather than a completed automation.

**Anti-patterns.** Automating an unclear process; hiding manual steps; removing human review where consequences are material; relying on brittle prompt sequences with no test cases; or calling a scheduled action reliable without observing failures and recovery.

## Build

**Outcome.** A Practitioner creates or materially changes an AI-enabled tool, agent, or system and evaluates it against a defined task boundary.

**Entry evidence.** State the intended user, system boundary, inputs and outputs, integration or runtime context, evaluation approach, and relevant safety or security constraints.

**Exit evidence.** Provide a runnable or inspectable implementation appropriate to the contribution, setup and operating instructions, an evaluation result or test record, known limitations, and a defined failure or escalation behavior. For a shared system, name the maintainer or maintenance boundary.

**Anti-patterns.** Presenting a prototype screenshot as a system; publishing code with no task-level evaluation; adding an agent where a checked workflow would suffice; hiding model, tool, or data dependencies; or implying production readiness without supporting evidence.

## Transform

**Outcome.** A Practitioner redesigns a team or organizational workflow, decision right, governance practice, or measurement loop around AI-enabled work.

**Entry evidence.** Identify the affected work, roles, decision owner, constraints, risk level, and the change hypothesis. A transformation proposal is valid entry evidence, not proof of an outcome.

**Exit evidence.** Show the changed operating model: the before and after workflow or decision path, role and accountability changes, controls or governance, adoption or measurement plan, and evidence from implementation where available. Separate measured results, practitioner observations, and hypotheses.

**Anti-patterns.** Equating software procurement with transformation; making organization-wide claims from a single individual workflow; measuring activity instead of a defined work outcome; bypassing accountable owners; or announcing savings, adoption, or quality improvements without evidence.

## Classification rules

1. Start with the artifact's direct outcome. Do not infer level from the contributor's title, seniority, or past work.
2. Use one primary capability. Select the first level whose outcome the artifact directly enables or demonstrates.
3. Add a secondary capability only when the artifact contains a substantial, usable connection to that level. A prerequisite mentioned in passing does not earn a tag.
4. Keep evidence proportional to the claim. A proposal can be useful, but must be labeled as a proposal; it does not satisfy exit evidence for an implemented outcome.
5. When an artifact covers a path across levels, make it a Guide and tag each material capability rather than forcing it into the highest level.

## Classification examples

These are hypothetical examples, not reported community results.

| Proposed contribution | Primary capability | Why | Secondary tags, if any |
|---|---|---|---|
| A checklist explaining how to identify sensitive inputs before testing an AI summarizer, with a scenario and a verification question. | Learn | It builds task-specific judgment before application. | `use` if it also includes a complete, checked task walkthrough. |
| A de-identified walkthrough that drafts a meeting brief, compares it with source notes, and records the edits made before sending. | Use | It demonstrates a checked discrete work task. | `learn` for an accompanying explanation of source-grounding limits. |
| A documented intake-to-draft workflow for recurring support requests, with approval rules, test cases, and a fallback queue. | Automate | It makes recurring work repeatable and reviewable. | `use` because a reviewer still completes the final task. |
| A repository for a tool that retrieves approved documents, produces structured output, includes setup instructions, and records evaluation cases. | Build | The contribution creates and evaluates a system. | `automate` if the tool operates a recurring workflow. |
| A team changes its proposal-review process, assigns review ownership, introduces a verification gate, and tracks agreed outcome measures. | Transform | The unit of change is how people and decisions operate together. | `automate` if a repeatable workflow is part of the redesign. |
