# The work after the first answer

I can get a plausible answer from a model quickly. The harder question starts one minute later: can I trust it enough to use it?

That question changes everything. It sends me back to the source material. It makes me define what a good result looks like, decide what the system may touch, test the awkward cases, and name the person who approves the outcome. If the task will happen again, I also need to leave behind a method that someone else can inspect and repeat.

This is the implementation gap. A demonstration shows that something can happen once. Useful capability means making it work in a real setting, under real constraints, with evidence strong enough for the consequence.

I am building Practice for that part of the work.

> **Practice**  
> The open community for AI practitioners.

## A prompt is not a working method

Most failures do not begin with a lack of interesting ideas. They begin in the distance between the idea and the operating details.

The model did not receive the right context. The source changed. A confident draft hid a factual error. An agent had more access than the task required. Nobody defined what should happen when a tool call failed. A team called a workflow automated before anyone had decided who would review its output.

A clever prompt cannot settle those questions on its own. The surrounding work matters: inputs, permissions, acceptance criteria, review, recovery, maintenance, and ownership.

That is why Practice is organized around doing rather than watching. A Practitioner might be learning how to judge model output, using a model in a daily task, redesigning a recurring workflow, building an agent, or changing how a team operates. The technical depth varies. The responsibility does not. Make the boundary visible. Test what matters. Keep a person accountable for consequential decisions. Record what happened.

This is not a demand for ceremony around every draft. The strength of the check should match the consequence. A low-risk outline may need a quick read. A workflow that can publish, spend money, change access, affect a customer, or influence an important decision needs a much stronger gate. The point is to choose that gate deliberately instead of treating fluent output as proof.

## Build the evidence into the work

As a builder, I want to see the chain from claim to evidence.

If an agent says a task is complete, where is the diff? If a workflow is described as repeatable, where are its inputs, failure paths, and run record? If a result improved, what was the baseline and what stayed the same during the comparison? If a source supports a claim, can a reviewer open it and find the relevant material?

Practice turns those questions into artifacts another person can use:

- A **Practice** is a reusable, tested method with steps, checks, and failure modes.
- A **Guide** is an opinionated path through several Practices toward an outcome.
- A **Lab** makes an experiment reproducible.
- A **Story** records a real implementation: before state, intervention, result, and lessons.
- A **Note** preserves a smaller observation without pretending it is settled.
- A **Project** provides inspectable open-source software or infrastructure.

The names matter because they prevent enthusiasm from outrunning evidence. An idea can begin as a Note. A repeatable experiment can become a Lab. A method earns the name Practice when another person can follow it and judge the result. Work can mature in public without being presented as more certain than it is.

That public record also makes disagreement productive. Instead of trading confident opinions, we can point to the same method, reproduce it under different conditions, identify where it breaks, and propose a revision. The useful unit is not agreement. It is an inspectable improvement.

## Open practice lowers the cost of starting again

Too much implementation knowledge disappears into private messages, meeting notes, and one person's memory. The result may help once, but the method cannot travel. The next person pays the same discovery cost, repeats the same failure, or has to trust a summary without seeing how it was produced.

Open practice gives the work a longer life. In Practice, durable artifacts live in Git so they can be discovered, versioned, reviewed, forked, and adapted. Buzz is where humans and agents coordinate, ask questions, compare attempts, and route useful discoveries back into those artifacts.

Open does not mean careless. Secrets, personal information, confidential material, and unsafe operating details stay out. The goal is to preserve the reusable method while protecting what should not be public.

This structure matters because tools will change. A useful method should separate the durable choices—task boundaries, context, evaluation, permissions, review—from the interface of one model or platform. Tool-specific implementations can still be valuable, but they should make enough context visible for another Practitioner to compare or replace them.

## A workshop for humans and agents

I do not want Practice to be a stage where a few people announce answers to everyone else. I want it to work like a workshop.

Humans bring lived context, judgment, care, and accountability. Agents can gather approved context, test artifacts, connect related work, draft changes, and surface gaps. Both can contribute, but their roles should remain legible. An agent gets only the access its task needs. Its output remains reviewable. A human owns consequential decisions.

That collaboration is part of what we need to learn. We need open examples of good task boundaries, useful context packs, proportionate review, failed tests, safe recovery, and handoffs that do not ask the next person to reconstruct the work. Those patterns become more useful when they are available to challenge and improve.

The standard for belonging is not a title, a tool choice, or how advanced someone sounds. It is contribution: learning something useful and making it easier for the next person.

## Start with one real task

The first open artifacts are deliberately practical. [The AI-Native Practitioner Guide](../../guides/ai-native-practitioner/README.md) provides a path from a bounded task to a documented, human-reviewed workflow. The first three canonical methods cover the recurring foundations: [building a reusable context pack](../../practices/001-context-pack.md), [redesigning a workflow before automating it](../../practices/002-workflow-redesign.md), and [verifying an agent's output before accepting or shipping it](../../practices/003-verification-gate.md).

They are starting points, not declarations that the work is finished. Their value will come from use: reproductions, corrections, alternative implementations, and honest failure reports.

**Choose one non-sensitive task you know, inspect the relevant open artifact in Git, then bring your first action or result to [`start-here` in Buzz](../../buzz/canvases/start-here.md) so the next Practitioner can build on it.**
