# Practice Voice

This guide governs public artifacts, community messages, repository documentation, and calls to action. Its job is to help a reader understand the work, judge it, and take a useful next step. It is not a collection of campaign slogans.

## Fixed language

Use the locked positioning exactly when positioning is needed:

> **Practice**  
> The open community for AI practitioners.

Use the locked ethos exactly when the ethos is needed:

> **Learn it. Build it. Use it. Share it.**

Do not paraphrase either line into a replacement tagline. A headline should describe the specific subject beneath it, not compete with the positioning.

## Voice attributes

### 1. Outcome-first, not future-first

Lead with the concrete problem, decision, artifact, or result. A reader should not have to pass through a prediction about AI before learning why the page exists.

- Write: “Turn one recurring review into a human-reviewed AI workflow.”
- Not: “Step into the limitless future of intelligent work.”

### 2. Operational, not inspirational

Give the reader inputs, steps, checks, owners, and failure modes. Motivation is useful only when it supports action.

- Write: “Choose one recurring task, record its inputs, and define what a reviewer must approve.”
- Not: “Dream bigger and let AI transform the way you work.”

### 3. Precise, not inflated

Name what a model, tool, person, or process actually does. State the boundary of a claim and distinguish observed results from proposals and examples.

- Write: “This Lab compares two review methods on the same ten example outputs.”
- Not: “This proven framework guarantees reliable AI at scale.”

### 4. Candid, not certain by default

Say what is known, what is assumed, and what still needs testing. Include limitations when they could change a reader’s decision.

- Write: “This is a proposed workflow. Test it with non-sensitive inputs before adopting it.”
- Not: “This workflow is safe and production-ready.”

### 5. Rigorous and accessible, not simplified past usefulness

Use the correct technical term, define it on first use, and then explain what the reader should do with it. Do not assume that every Practitioner is an engineer.

- Write: “An evaluation is a repeatable check of a system’s output. Start by defining one pass condition.”
- Not: “Simply implement an eval harness with deterministic graders.”

### 6. Peer-level, not guru-led

Write as one Practitioner helping another inspect and reuse the work. Invite scrutiny and contribution without manufactured familiarity or status language.

- Write: “Reproduce the steps, report what changed, and propose a correction if the method breaks.”
- Not: “Learn the secret workflow our AI experts do not want you to miss.”

### 7. Model-agnostic, not vendor-centered

Describe the capability or constraint first. Name a product only when the artifact genuinely depends on it, and present tool-specific implementations as examples rather than universal requirements.

- Write: “Use a model that can return structured output; record the model and version in your Lab notes.”
- Not: “Every modern team needs Vendor X to become AI-native.”

## Four context examples

These are editorial examples, not reports of measured outcomes.

| Context | Use | Avoid |
|---|---|---|
| Beginner | “Pick one task you already understand. Write down the input, the desired output, and one check before asking a model to help.” | “Master AI in minutes with one perfect prompt.” |
| Technical | “Test the agent against a fixed set of cases, record tool calls, and require review before it can merge code.” | “Deploy a fully autonomous, production-grade agent with complete confidence.” |
| Organizational | “Assign a workflow owner, define the approval boundary, and measure whether the change improves the existing process.” | “Revolutionize the enterprise by putting AI everywhere.” |
| Community | “Share the method, its limits, and enough evidence for another Practitioner to reproduce it.” | “Join the world’s leading movement of AI innovators.” |

## Information order

Most Practice writing should answer these questions in order:

1. What concrete problem or outcome is this about?
2. Who is it for, and in what context?
3. What can the reader do or reuse?
4. What inputs, permissions, or prior knowledge are required?
5. How can the reader check whether it worked?
6. What can fail, and where is human judgment required?
7. What is the next useful action?

Short announcements and channel messages may compress the sequence, but they should preserve the problem, action, and next step.

## Headline patterns

A headline makes one concrete promise about the page. Prefer sentence case and a specific noun or verb.

Use these patterns:

- **Verb + object + boundary:** “Evaluate an agent before it can merge code”
- **How to + outcome + constraint:** “How to add AI review without hiding human ownership”
- **Artifact + specific job:** “Lab: Compare two methods for checking citations”
- **Question tied to a decision:** “Which parts of this workflow require approval?”
- **Result to examine, without exaggeration:** “What changed when we added a review checklist”

Avoid patterns that offer only novelty, urgency, or status:

- “The future of AI is here”
- “The ultimate guide to everything AI”
- “Ten game-changing prompts you need today”
- “Become an AI expert overnight”

Do not add a campaign line beneath the Practice name as though it were new positioning. Use the locked positioning or a descriptive page title.

## Description pattern

A useful description states the context, the work, and the verification boundary in one to three sentences:

> **For [person or context] facing [specific problem], this [artifact] provides [method or output]. It includes [evidence, check, or limitation] so the reader can [judge or reproduce it].**

Example:

> For a team reviewing recurring client briefs, this Practice defines the input contract, draft step, and human approval boundary. It includes a checklist so another Practitioner can test the method against their own briefs.

When space is tight, keep the specific problem and deliverable. Remove claims about importance, novelty, or momentum first.

## Call-to-action patterns

A call to action names the action, its object, and the useful state it creates. Use one primary action at a time.

| Intent | Pattern | Example |
|---|---|---|
| Learn | Read or inspect + named material | “Inspect the evaluation criteria.” |
| Try | Run or apply + bounded method | “Run the Lab with five non-sensitive examples.” |
| Verify | Check or compare + observable output | “Compare the draft with the acceptance checklist.” |
| Contribute | Share or propose + required evidence | “Propose an edit and include a reproducible example.” |
| Discuss | Answer + decision-focused question | “Name the failure mode this checklist misses.” |
| Continue | Choose + explicit next step | “Choose one recurring workflow to map.” |

Avoid empty actions such as “Learn more,” “Get started,” “Join the revolution,” or “Unlock the power” when they do not say what happens next.

## Evidence and examples

- Label invented scenarios as **Example**, **Hypothetical**, or **Proposed**.
- Call something a result only when the observation and method are available.
- Use a **Story** only for a real implementation with a before state, intervention, result, and lessons.
- Give current technical claims a primary source and an as-of date.
- Replace “proven,” “best,” “safe,” “secure,” and “production-ready” with the actual test, comparison, threat boundary, or operating criteria.
- Never imply community adoption, activity, or outcomes without evidence.

## Sentence-level guidance

- Prefer active voice and name the responsible person: “A maintainer reviews the change,” not “The change is reviewed.”
- Use “you” for a direct instruction and “we” only for a real shared commitment or documented community decision.
- Keep one main claim per sentence.
- Define specialized terms on first use. Do not replace precision with unexplained acronyms.
- Name the relevant component: model output, agent action, tool call, workflow step, reviewer, or owner. Avoid using “AI” as the actor when a more precise subject is known.
- Use lists for steps, checks, and alternatives—not for stacking benefits.
- Use exclamation marks rarely. Importance should come from the content.
- Prefer “can” for a demonstrated capability and “may” for a possibility. Avoid “will” when the outcome depends on context.

## Final voice check

Before publishing, ask:

- Does the first paragraph name a problem, outcome, or decision?
- Can the intended reader identify a concrete next action?
- Are examples clearly separated from evidence?
- Are claims bounded by their test, source, or limitation?
- Is every specialized term either defined or unnecessary?
- Could a reader use the artifact without adopting a particular vendor?
- Does the language respect beginners without withholding technical detail?
- Does the page use canonical artifact names correctly?
- Did generic hype survive where an operational detail should be?
- Is the locked positioning preserved rather than replaced?
