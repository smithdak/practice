# Knowledge Taxonomy

## Classify by the artifact's main job

Use this taxonomy to choose one primary artifact type before drafting. The type answers what the reader should get from the artifact; capability and role tags answer who it helps and what skill it advances. One contribution can produce linked artifacts, but each file or proposal should have one primary type.

Start with these questions in order:

1. Is the main deliverable maintained, usable open-source software or infrastructure? Choose **Project**.
2. Is the main purpose to document a real implementation from before through result and lessons? Choose **Story**.
3. Is the main purpose to answer a testable question through a reproducible experiment or evaluation? Choose **Lab**.
4. Is the main purpose to teach a reusable, tested method that a Practitioner can apply? Choose **Practice**.
5. Is the main purpose to organize several Practices into an opinionated path toward an outcome? Choose **Guide**.
6. Otherwise, preserve the bounded observation, question, decision, or early evidence as a **Note**.

If two answers seem true, select the type that matches the reader's primary action. Split only when each resulting artifact has a complete purpose. For example, a Lab that discovers a reliable method can link to a new Practice; the Lab remains the evidence record and the Practice becomes the reusable instruction.

## Artifact types

| Type | Choose it when | Reader should leave with | Minimum useful contents | Do not choose it when |
|---|---|---|---|---|
| **Note** | You have a bounded observation, question, decision, failure, or early evidence that is useful but not yet a reusable method or complete study. | A clear claim or open question and its context. | Claim or question; context; evidence or explicit uncertainty; implications or next step. | You can already give reliable steps and evaluation criteria; that is a Practice. |
| **Practice** | You can teach a repeatable method for a defined problem and specify how to evaluate its output. | Steps they can apply, check, and adapt. | Outcome, problem and context, inputs, method, implementation guidance, evaluation, failure modes, evidence, and variations. | The work is principally a comparison or experiment; that is a Lab. |
| **Guide** | The outcome needs multiple Practices, sequencing, prerequisites, or a capstone rather than one method. | An opinionated path and how to know they completed it. | Intended Practitioner, outcomes, prerequisites, path, modules, capstone, evaluation, and maintainers. | It is only a collection of links or a single procedure. |
| **Lab** | You need to test a question, compare approaches, or record an evaluation under stated conditions. | A reproducible result, limitation, and interpretation. | Question, hypothesis, variables, fixed conditions, dataset or task set, procedure, rubric, results, limitations, and reproduction details. | You are reporting a real operational rollout; that is a Story. |
| **Story** | A real implementation can be documented honestly, including what changed and the quality of the evidence. | A grounded account of before, intervention, result, and lessons. | Before, constraint, intervention, implementation, after, result, evidence quality, lessons, and reusable artifacts. | The example is invented, planned, or anonymized beyond a checkable evidence description; use a Note, Lab, or clearly labeled hypothetical example instead. |
| **Project** | The durable contribution is open-source code, a tool, a library, an integration, or shared infrastructure that people can inspect and use. | A usable project boundary, setup path, and maintenance expectation. | Problem, intended Practitioners, smallest useful release, setup or use instructions, license, dependencies, contribution boundary, and maintainer. | The core value is prose instruction or evidence; publish a Practice, Lab, or Story and link any code. |

The repository templates for Practices, Guides, Labs, and Stories are the authoritative starting structures for those types. This taxonomy does not replace their required sections.

## Resolve common ambiguities

### Note vs. Practice

A **Note** preserves a useful insight or uncertainty. It may say, “this verification check caught a failure in this context,” and explain what is still unknown. A **Practice** says how to perform the check, when to use it, how to judge it, and how it fails. Promote a Note only after the method and its evaluation are concrete enough for another Practitioner to try.

### Practice vs. Lab

A **Practice** is an instruction for doing work. A **Lab** is an evidence record for testing a question. A Lab can be inconclusive; a Practice needs a usable method and explicit limits. Link them when the Lab supports the Practice, but do not rewrite experimental results as universal instructions.

### Lab vs. Story

A **Lab** controls or states test conditions to answer a question. A **Story** describes an actual implementation in context, including constraints and evidence quality. A real rollout can include a Lab, but its outcome narrative belongs in the Story.

### Story vs. Project

A **Story** explains what happened in an implementation. A **Project** is the maintained, reusable code or infrastructure. A Story may link to the Project; neither substitutes for the other.

### Guide vs. Practice

A **Guide** sequences multiple methods toward a broader outcome. A **Practice** teaches one method. If a reader can complete the stated outcome through one repeatable sequence, write a Practice; if they must choose and sequence several Practices, write a Guide.

## Capability and role tags

Apply tags after selecting the artifact type. Tags support finding and routing; they do not confer status, expertise, authority, or access.

### Capability tags

Use the controlled values from the [Capability Ladder](CAPABILITY_LADDER.md): `learn`, `use`, `automate`, `build`, and `transform`.

- Give a Practice, Lab, Story, Project, channel, or contribution one `primary_capability`.
- A Guide may list multiple `capabilities` because it intentionally sequences a path.
- Add `secondary_capabilities` only for material, usable connections. Do not tag every prerequisite or aspiration.
- The primary capability describes the artifact's outcome, not the contributor. For example, an executive may contribute a Learn artifact and an engineer may contribute a Transform artifact.

### Role tags

Use role tags to name the intended work context. The controlled role vocabulary is:

`individual-practitioner`, `engineer`, `architect`, `builder`, `operator`, `founder`, `services-leader`, `internal-ai-champion`, `transformation-lead`, `consultant`, `agency-implementer`, `executive`.

Choose one or two primary roles when the artifact has a clear intended user. Add a secondary role only when the method, evidence, or decision is directly applicable to that role; do not add roles merely to enlarge reach. If the work is broadly applicable, use `individual-practitioner` and state any specific prerequisites in the content.

Role tags describe a work context, not a capability level. Do not use `beginner`, `advanced`, `expert`, or seniority as role tags. Explain needed knowledge in prerequisites and classify the skill outcome with a capability tag.

### Cross-tagging record

Use this compact record in an artifact front matter, proposal, channel description, or contribution summary where the surface supports metadata. It is a recommended convention, not a claim about platform fields.

```yaml
artifact_type: practice
primary_capability: automate
secondary_capabilities: [use]
primary_roles: [operator]
secondary_roles: [consultant]
```

For existing templates, use their established `capability`, `capabilities`, and `roles` fields, and express primary versus secondary tags in the body or contribution summary until the template formally adds separate fields.

## Apply the taxonomy to members, channels, content, and contributions

| Surface | What to classify | How to apply it |
|---|---|---|
| Member introduction or profile | Current goal and work context, not a permanent level. | Name one next capability and one or two role tags; attach evidence only to a specific contribution. |
| Channel | The outcome the channel is organized to advance. | Give the channel one primary capability and optional role tags; route an artifact to the channel matching its primary capability. |
| Content artifact | Its main job, direct outcome, and intended work context. | Select one artifact type, one primary capability, and targeted role tags; link to companion artifacts rather than mixing types. |
| Contribution | The reusable thing changed and the action taken. | Classify the changed artifact, then describe the contribution action: correction, failure report, example, implementation, experiment, code, translation, maintenance, or help for another Practitioner. |

## Concrete classification examples

All examples below are hypothetical.

| Item | Artifact type | Tags | Reason |
|---|---|---|---|
| A short account of an unsupported claim found in an AI-generated research summary, with source links and an open question about a better check. | Note | `learn`; `individual-practitioner` | It preserves an observation and uncertainty; it does not yet establish a repeatable method. |
| Instructions for creating a context pack for recurring work, including inputs, verification, failure modes, and variations. | Practice | `use`; `individual-practitioner`, `operator` | The reader can apply and evaluate one reusable method. |
| An evaluation that compares two context-pack structures on a stated task set and publishes the rubric, results, and limitations. | Lab | `learn`; `builder`, `operator` | The central job is testing a question under stated conditions. |
| A documented client-service workflow change with its previous review path, the new human-reviewed AI workflow, evidence quality, and lessons. | Story | `automate`; `consultant`, `services-leader` | It reports a real implementation rather than prescribing a universal method. |
| A maintained repository that implements structured verification checks, with setup, tests, license, and a named maintenance boundary. | Project | `build`; `engineer`, `builder` | The durable contribution is usable software. |
| A path that sequences context, workflow, verification, and organizational adoption Practices toward an AI-native operating model. | Guide | `use`, `automate`, `build`, `transform`; `transformation-lead`, `executive` | The outcome requires multiple Practices in order. |
| A contributor corrects an outdated evaluation rubric in a Lab. | Contribution action: correction | Classify the Lab's existing tags; `learn` | The change improves a Lab; it is not a new artifact type. |
