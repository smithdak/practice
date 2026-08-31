# Practice Lexicon

This lexicon defines the words that carry specific meaning in Practice. Canonical terms help a reader know what kind of artifact they are opening, how mature it is, and what they should be able to do with it. They are not marketing labels.

## Core usage rules

1. Capitalize a canonical artifact name when it refers to that artifact type.
2. Use the ordinary lowercase word when no canonical meaning is intended.
3. On first reference, write **the Practice community** when “Practice” could mean either the community or an artifact.
4. Use **Practitioner** when a person’s community identity matters. Use a more specific role—reader, contributor, maintainer, engineer, manager, reviewer, or workflow owner—when that role explains the action.
5. Choose an artifact name from the evidence and structure it contains, not from how important the work sounds.

## Canonical terms

### Practitioner

A person putting AI to useful work and participating in the Practice community as a learner, builder, operator, contributor, or leader.

- Use: “A Practitioner should be able to reproduce the Lab.”
- Use a specific role when clearer: “A reviewer approves the output.”
- Avoid status substitutes such as “guru,” “ninja,” “wizard,” “rockstar,” or “thought leader.”
- Do not replace every instance of “person” or “user” with Practitioner. In a software interface, for example, “user” may be the accurate role.

### Practice

**Practice** has two canonical senses:

1. **The community:** the open community for AI practitioners. Use “the Practice community” when context is ambiguous; use “Practice” alone after the meaning is clear.
2. **An artifact:** a reusable, tested method. Write “a Practice” and “Practices.” A Practice should make its inputs, steps, expected output, evaluation, and failure modes inspectable.

Examples:

- Community: “The Practice community maintains this Guide.”
- Artifact: “Apply this Practice to one recurring workflow.”
- Ordinary usage: “The team needs more practice reviewing model output.”

Do not call a tip, prompt fragment, untested opinion, or general topic a Practice. Publish it as a Note or develop it until the method is reusable and tested.

### Guide

An opinionated path that combines multiple Practices toward a defined outcome.

- Use: “This Guide takes a Practitioner from mapping a workflow to evaluating the revised process.”
- A Guide explains sequence and tradeoffs; it is more than a list of links.
- Ordinary usage remains lowercase: “See the installation guide from the tool vendor.”
- Avoid “ultimate guide” or “complete guide” unless the scope and completeness criteria are explicit.

### Lab

A reproducible experiment or evaluation. A Lab states the question, setup, inputs, procedure, observations, and limitations so another person can repeat it.

- Use: “Run the Lab with the same test set, then compare the observations.”
- Label proposed or example results. Do not invent experimental outcomes.
- Do not call a product demonstration a Lab unless it includes a reproducible question and method.

### Story

A real implementation described through its before state, intervention, result, and lessons.

- Use: “The Story records what the team changed and how it evaluated the result.”
- A composite, imagined, or projected scenario is not a Story. Label it **Hypothetical** or **Example**.
- Do not use “success story” to hide missing evidence, mixed results, or failures.

### Note

A smaller observation that may mature into a Practice after testing and review.

- Use: “This Note records a review failure we want others to examine.”
- A Note can be tentative, but it must distinguish observation from inference.
- Do not inflate a Note into a Practice merely to make it sound authoritative.

### Project

Open-source software or infrastructure built by the Practice community.

- Use: “The Project includes the source, setup instructions, and contribution path.”
- Use lowercase for ordinary work: “The migration is an internal project.”
- Do not use Project for a closed product, confidential client implementation, or idea without an inspectable open-source artifact.

### Capability ladder

The **capability ladder** organizes Practice knowledge by outcome in this fixed order:

1. **Learn** — understand models, context, tools, limitations, security, and evaluation.
2. **Use** — integrate AI into real daily work.
3. **Automate** — turn recurring work into reliable, reviewable workflows.
4. **Build** — engineer agents, tools, and AI-native systems.
5. **Transform** — redesign teams and organizations around new capabilities.

Write the full sequence as **Learn → Use → Automate → Build → Transform**. Capitalize the five stage names when referring to the ladder; use lowercase for ordinary verbs.

The ladder is an information architecture, not a certification, job hierarchy, or claim that every person or organization follows an identical path. Do not add stages or rename them in local artifacts.

## Choosing an artifact name

Use the smallest artifact type that honestly describes the work:

| If the work primarily contains… | Call it… | It is ready when… |
|---|---|---|
| A bounded, tested, reusable method | **Practice** | Another person can follow and evaluate it |
| An ordered route through multiple Practices | **Guide** | The sequence, outcome, and tradeoffs are clear |
| A repeatable experiment or evaluation | **Lab** | The setup and observations can be reproduced |
| A documented real implementation | **Story** | Before, intervention, result, and lessons are evidenced |
| A useful but smaller or tentative observation | **Note** | Observation and inference are clearly separated |
| Inspectable open-source software or infrastructure | **Project** | Source, setup, license, and contribution path are available |

Importance does not determine the label. Evidence and structure do.

## Supporting terms

### AI-native

Use **AI-native** as the direction named in the locked north star, not as a synonym for “uses AI” or “fully autonomous.” Explain the capability in context—for example, redesigning a workflow around model capabilities while preserving evaluation and accountable ownership.

Practice aims to build the open standard for becoming AI-native. Do not write as though that standard is already established or adopted.

### Agent

A system that can use a model to decide among actions or tools toward a goal. When the distinction matters, state its tools, permissions, stopping conditions, and human review boundary. Do not use “agent” as a fashionable substitute for every chatbot or automation.

### Evaluation

A repeatable way to judge an output or system against stated criteria. Prefer **evaluation** in general-audience prose; introduce **eval** only when the audience or source convention makes the abbreviation useful.

### Human-reviewed

A workflow in which a named person examines a defined output or decision before a consequential next step. Name who reviews what; the phrase alone is not evidence of adequate oversight.

### Open

Specify what is open: source code, license, contribution process, access, or public documentation. “Open” does not mean unrestricted access to secrets, private channels, confidential inputs, or unsafe actions.

## Discouraged language and replacements

Avoid the following language by default. A direct quotation or a precisely evidenced technical statement may require one of these terms, but the surrounding text should make that reason clear.

| Avoid | Why it fails | Replace it with |
|---|---|---|
| revolutionary, game-changing, groundbreaking | Claims importance without showing the change | Name the changed workflow, decision, or result |
| cutting-edge, next-generation, state-of-the-art | Depends on a comparison and changes over time | Name the method, benchmark, date, and comparison when relevant |
| unlock, unleash, supercharge | Hides the actual action | Use a direct verb: map, test, compare, build, review, or share |
| 10x, exponential, massive impact | Implies an unsupported measured effect | Provide the metric and evidence, or describe the intended improvement |
| effortless, seamless, instant, magic | Conceals setup, judgment, and failure modes | State the required work, time, inputs, and checks |
| democratize AI | Treats access as a slogan | Say who lacks access and what concrete barrier is reduced |
| AI-powered, powered by AI | Says nothing about the system’s role | Name what the model does and what a person verifies |
| ultimate, complete, everything you need | Makes an unbounded completeness claim | State the audience, outcome, and exclusions |
| proven, guaranteed, foolproof | Overstates available evidence | Name the test, sample, observed result, and remaining limitation |
| best, leading, world-class | Requires a defined comparison | State the criteria and alternatives, or remove the ranking |
| safe, secure, private | Hides the threat model or controls | Name the data boundary, control, test, and residual risk |
| production-ready, enterprise-ready | Omits operating criteria | List the reliability, security, review, and support requirements met |
| fully autonomous, no humans needed | Erases permissions and accountability | State permitted actions, escalation rules, and human approval points |
| replace people, eliminate jobs | Generalizes from tasks to people | Name the task change and who remains accountable |
| secret prompt, prompt hack | Optimizes for novelty over reuse | Publish a tested Practice with context, limits, and evaluation |
| guru, ninja, wizard, rockstar | Creates status without describing responsibility | Practitioner or the specific role |
| join the revolution, future is here | Creates urgency without a decision | Give the reader one useful next action |
| community-driven, trusted by the community | Implies participation or endorsement | Describe the actual review or contribution mechanism and its evidence |
| success story, case study | Can imply selective or commercial proof | Use Story when the required real implementation evidence exists |

### Precision over umbrella terms

Replace a broad AI claim with the actor and behavior that matter:

- “AI checked the answer” → “A model drafted the answer; a reviewer checked each citation against the source.”
- “The agent is secure” → “The agent can read the test repository, cannot access deployment credentials, and requires approval before opening a pull request.”
- “We automated the process” → “The workflow drafts the weekly summary; the operations owner approves it before publication.”
- “The model hallucinated” → “The response cited a source that did not contain the claim.”

The more consequential the claim, the more specific the language should be.

## Capitalization and naming

- **Practice**: capitalized for the community and canonical method artifact; lowercase for the ordinary noun or verb.
- **Practitioner**: capitalized when naming the Practice community identity.
- **Guide, Lab, Story, Note, Project**: capitalized for canonical artifact types; lowercase for ordinary uses.
- **capability ladder**: lowercase as the name of the organizing system; its stages are **Learn, Use, Automate, Build, Transform**.
- **AI**: uppercase. Prefer a specific subject such as model, agent, tool, workflow, reviewer, or team when known.
- Product and model names: follow the owner’s spelling and include a version or as-of date when the detail can change.

## Language decision check

Before using a canonical or promotional-sounding term, ask:

1. Does the term tell the reader what this is or what to do?
2. Does the artifact meet the evidence and structure required by its name?
3. Is the actor more specific than “AI”?
4. Can a broad quality claim be replaced with a check or boundary?
5. Could this sentence describe almost any AI product or community? If so, rewrite it around the actual work.
6. Does the wording preserve the locked positioning and remain model-agnostic?
