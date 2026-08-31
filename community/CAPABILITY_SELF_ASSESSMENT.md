# Choose the next capability for one real piece of work

Use this self-assessment to choose the next outcome for a specific task or workflow. It routes work; it does not score the Practitioner, grant access, certify skill, or prescribe a permanent level. Someone can choose different routes for different work.

Complete it with a non-sensitive real example. If the real example cannot be described safely in Buzz, use a truthful sanitized description or a clearly labeled synthetic example. Do not include credentials, private keys, recovery material, client or employer-confidential information, personal data, or private source material.

## One-minute check

Write short answers before choosing a route:

1. What task or workflow do I want to improve?
2. Is it a single task, recurring workflow, system, or team operating change?
3. What output or decision would make the next step useful?
4. What is one constraint, risk, or human check that matters?
5. What is the smallest action I can take and report back on?

If you cannot answer the first four questions, your route is **Learn**. Bring the task, one constraint, and the missing question to `learn` or `start-here`.

## Routing questions

Answer in order. Stop at the first **yes** that describes the immediate outcome you need.

1. **Transform:** Am I trying to redesign how a team or organization performs work, assigns decision rights, governs AI use, or measures adoption and outcomes?  
   **Yes → Transform.**
2. **Build:** Am I creating or materially changing an AI-enabled tool, agent, or system that needs a defined boundary and evaluation?  
   **Yes → Build.**
3. **Automate:** Am I making a recurring workflow repeatable with a trigger, expected inputs and outputs, human review, and a failure or recovery path?  
   **Yes → Automate.**
4. **Use:** Am I completing one discrete piece of real work with AI assistance and checking the result before accepting it?  
   **Yes → Use.**
5. **Learn:** Do I first need to understand how to frame the task, handle context or privacy, recognize a limitation, or define a check before applying AI to it?  
   **Yes or unsure → Learn.**

The ordering prevents a system or organizational change from being mistaken for a one-off task. It does not make Transform or Build more advanced statuses. If more than one answer is yes, choose the route that describes the immediate next output:

| Immediate next output | Route |
|---|---|
| A safe task framing, limitation explanation, or evaluation question | Learn |
| A checked draft, analysis, plan, or other discrete work result | Use |
| A reviewable recurring-workflow design or observed run | Automate |
| An inspectable tool, agent, or system change plus an evaluation plan or record | Build |
| A proposed or changed team operating model, decision path, governance, or measurement loop | Transform |

If the task itself is unclear, do not force a ladder channel. State the smallest real problem in `start-here` or `ask-practice` and ask for help framing it.

## Route cards

### Learn

Choose Learn when sound judgment must come before application.

- **Bring:** the task, intended output, and one constraint or risk.
- **First action after `start-here`:** ask in `learn` what mechanism, limitation, privacy choice, or evaluation check you need to understand.
- **A useful next result:** a plain-language explanation, a task-specific decision, a check, and one bounded test.
- **Not yet:** a production result merely because you used a model.

Hypothetical example: “I need to summarize approved meeting notes but do not know what source-grounding check would catch omissions.”

### Use

Choose Use when the goal is one checked piece of real work.

- **Bring:** a discrete task, acceptable output, approved or synthetic inputs, and the accountable human decision-maker.
- **First action after `start-here`:** try the task once and state how you will compare, correct, or reject the result.
- **A useful next result:** the method, output or decision, human check, and what still required judgment.
- **Not yet:** a dependable recurring workflow or an unreviewed generated answer.

Hypothetical example: “I will draft a project brief from approved notes, compare every claim to the notes, and record the edits before sending.”

### Automate

Choose Automate when recurring work needs a repeatable, human-reviewed workflow.

- **Bring:** the trigger, inputs, expected output, review point, failure consequence, and accountable owner.
- **First action after `start-here`:** map one pass through the workflow, including one failure and recovery path.
- **A useful next result:** a reproducible workflow description, test cases, approval rules, recovery path, and observed behavior from a run when available.
- **Not yet:** a saved prompt, an unattended system, or an automation claim with no failure handling.

Hypothetical example: “Each week, approved support themes should become a draft report that a manager reviews; missing input must route to a manual queue.”

### Build

Choose Build when you are creating or changing an AI-enabled system rather than configuring one personal workflow.

- **Bring:** intended user, system boundary, inputs, outputs, integration or runtime context, evaluation approach, and relevant safety or security constraint.
- **First action after `start-here`:** write a small boundary statement and one evaluation case in `build`.
- **A useful next result:** an inspectable implementation, setup or operating instructions, evaluation record, limitations, and failure or escalation behavior.
- **Not yet:** a prototype screenshot, an untested code sample, or an implication of production readiness.

Hypothetical example: “A tool will retrieve only approved documents for analysts, return structured summaries, and be evaluated against known questions before use.”

### Transform

Choose Transform when the work changes how a team or organization operates.

- **Bring:** affected work, roles, decision owner, constraints, risk level, and a change hypothesis.
- **First action after `start-here`:** describe the current and proposed decision path in `transform`; label it as a proposal.
- **A useful next result:** a changed operating model, role and accountability changes, controls, adoption or measurement plan, and implementation evidence where available.
- **Not yet:** buying a tool, rolling out an individual workflow, or asserting organization-wide gains without evidence.

Hypothetical example: “A support team wants to move first-draft triage to a reviewed AI-assisted step, with a named escalation owner and a measure for unresolved cases.”

## Post your result

The universal first action is one `start-here` post. Use this completed form:

> I am a **[role or work context]**. I want to work on **[non-sensitive task or workflow]**. My next outcome is **[route]** because **[immediate output I need]**. My first small action is **[checkable action]**.

Then go to the selected channel and complete the route card's first action. Return to the same `start-here` thread with what you checked, what changed, what failed, or the next smallest question.

## Help without giving up responsibility

- **Self-directed:** Choose a route, post the form, and do the small action. A reply is helpful but not required to begin.
- **Agent-assisted:** If an enabled steward agent is available in the relevant channel, ask it to suggest a route or tighten the first action using only non-sensitive context. Check its suggestion against this guide and published sources.
- **Human-assisted:** Ask a human Practitioner or maintainer for help when safety, access, policy, licensing, moderation, or an ambiguous work boundary is involved. Humans—not agents—make membership, access, moderation, governance, and contribution-acceptance decisions.

No agent should receive identity keys, passwords, recovery codes, tokens, or restricted work material. No agent can issue invitations, set up or recover identities, change membership, or make final decisions for a Practitioner.

## Sources and review date

- [Capability Ladder](../docs/framework/CAPABILITY_LADDER.md), reviewed 2026-08-31.
- [Buzz information architecture](../buzz/INFORMATION_ARCHITECTURE.md), reviewed 2026-08-31.
- [Buzz access and security runbook](../ops/BUZZ_SECURITY.md), reviewed 2026-08-31.
