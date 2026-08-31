# From invitation to a useful first contribution

Practice onboarding gets a new Practitioner to one small, public, non-sensitive action: post a short introduction and next action in `start-here`. The post gives another Practitioner, a human maintainer, or an enabled steward agent enough context to route useful help without requiring prior AI experience.

Buzz is the coordination hub, not the durable source of truth. Keep reusable work, accepted decisions, and contributions in Git. Do not post confidential work, personal data, credentials, private keys, recovery material, client material, or unlicensed material in Buzz—including in direct messages or private channels.

## The standard path

| Stage | Member action | Accountable helper | Completion signal |
|---|---|---|---|
| 1. Invitation | Receive a valid invitation from the community owner or an authorized human inviter. | Human owner or authorized human inviter | The person can begin the hosted join flow. |
| 2. Identity setup | Complete Buzz's hosted account and identity steps using their own human identity. Keep identity and recovery material private. | The member; a human owner or maintainer for an access problem | The person can enter the Practice community. |
| 3. Orientation | Read the `start-here` canvas and the community expectations; identify one real, non-sensitive work problem. | The member | The person can state a problem without sharing restricted material. |
| 4. Self-assessment | Use the [capability self-assessment](CAPABILITY_SELF_ASSESSMENT.md) to select the next outcome: Learn, Use, Automate, Build, or Transform. | The member; optional routing help | The person has one route and one bounded next action. |
| 5. First action | Post the introduction below in `start-here`. | The member | The post links a real problem to a next action. |
| 6. Follow-up | Take the selected action, return with what happened, and turn durable work into a Git issue or contribution when appropriate. | The member; a human helper or enabled steward agent | A next decision, a checked result, or a clearly stated blocker is visible. |

Hosted Buzz communities are invite-only; joining an open channel is possible only after joining the community. An invitation is access to the community, not an endorsement, role, or permission to act for Practice. If an invitation expires, fails, or goes to the wrong account, contact the human who issued it. Do not ask an agent to create, recover, transfer, or troubleshoot an identity with keys, recovery codes, passwords, or tokens.

### First action: make one `start-here` post

After selecting a route, copy, complete, and post this message in `start-here`:

> I am a **[role or work context]**. I want to work on **[a non-sensitive real task or workflow]**. My next outcome is **[Learn | Use | Automate | Build | Transform]**. My first small action is **[one checkable action I can take next]**.

Example (hypothetical):

> I am an operations coordinator. I want to work on a non-sensitive meeting-brief task. My next outcome is **Use**. My first small action is to draft one brief from approved notes and compare it with the source before sharing it.

Do not wait for a perfect introduction, an advanced use case, or a reply before taking the stated small action. If the task cannot be described safely, replace details with a truthful, non-sensitive description or a clearly labeled synthetic example; do not move restricted material into Buzz.

## Orientation before posting

1. Read the `start-here` canvas and identify the channel whose outcome matches the assessment result.
2. Read the [capability self-assessment](CAPABILITY_SELF_ASSESSMENT.md). Capability labels describe the next outcome for this work, not a person's rank or permanent level.
3. Keep the first problem bounded. Name the output you need, the constraint or risk, and the smallest test or decision that would move it forward.
4. Use `ask-practice` instead of a ladder channel when the real problem is not yet clear enough to route. Use `projects` only for a bounded open-source project proposal, and `showcase` only when there is an implementation or result with evidence.
5. Read the applicable Git contribution guidance before proposing a durable artifact. A useful correction or Note is a valid first contribution; nobody must progress through a fixed ladder.

## Choosing and taking the route

The assessment selects a channel by the immediate outcome, not the product, model, job title, or amount of experience.

| Route | Go to | Take this first route-specific action |
|---|---|---|
| Learn | `learn` | Post a bounded question that names the task, one constraint or risk, and the check you would use before applying an answer. |
| Use | `use` | Try one discrete task with approved or synthetic inputs, then state the human check that determines whether the output is usable. |
| Automate | `automate` | Map one recurring workflow: trigger, inputs, expected output, human review point, and one failure path. |
| Build | `build` | Describe one system boundary: intended user, inputs, outputs, evaluation approach, and a relevant safety or security constraint. |
| Transform | `transform` | State one affected team workflow, decision owner, constraint, and change hypothesis; label it as a proposal until evidence exists. |

The `start-here` post remains the only universal first action. The route-specific action is the first step after that post. A member may move to a different route when the work changes; this is routing, not a status change.

## Help paths and boundaries

### Self-directed path

A member can complete the standard path alone: assess, post in `start-here`, take the route-specific action, and return to the same thread with the result or blocker. The member does not need to wait for a helper to proceed.

### Agent-assisted path

Where Practice has enabled a steward agent with access to the relevant open channels, a member may ask it to:

- restate the member's non-sensitive problem and suggest the most likely capability route;
- turn a broad description into a bounded first-action draft;
- point to the relevant channel or published Git artifact; or
- identify when the question should be redirected to `ask-practice`.

Treat an agent's suggestion as a draft, not a decision or evidence. The member remains responsible for choosing the route, checking any technical claim, and deciding whether a result is acceptable. An agent must not create or recover an account, send or manage invitations, request or handle identity material, change access, make maintainer commitments, or receive restricted material. It escalates access, safety, policy, licensing, moderation, and private-data concerns to a human rather than attempting to resolve them.

### Human-assisted path

Ask a human owner or maintainer for invitation and access issues. Ask another Practitioner or a human maintainer in the relevant open channel for help framing a problem, selecting a safe example, or deciding whether a result is ready to become a Git contribution. Human maintainers retain all decisions about membership, access, moderation, governance, and acceptance of contributions.

For a conduct concern, use the private reporting route in the Code of Conduct rather than `start-here`. Do not put the report or its evidence in a public post.

## Manual follow-up loop

Onboarding must work even when no scheduled workflow or automated reminder is available.

1. The member carries out the small action named in their `start-here` post.
2. The member replies in that thread with one of: what they checked, what changed, what failed, or the smallest remaining question.
3. A human helper or enabled steward agent who encounters the thread may give a concise route, resource, or escalation. No reply is promised by a bot or timer.
4. If the work becomes durable, the member opens or links the smallest appropriate Git issue, correction PR, Note, Practice, Lab, Story, or Project proposal. Link the resulting canonical artifact back to the relevant Buzz conversation.
5. If the member has no response or next step, they post one concise follow-up in the same thread naming the blocker. A maintainer may review it when available; this is a manual operating practice, not an automated service-level commitment.

This loop deliberately avoids scheduled workflows, automated forum posts, and account automation. It relies only on an invite, the hosted join flow, stream channels, and ordinary human or agent messages after membership exists.

## Failure modes

| Situation | Do this | Do not do this |
|---|---|---|
| No invitation or a failed invitation | Contact the issuer or another authorized human through the existing public contact path. | Create a second identity or ask an agent to bypass access controls. |
| Unsure which capability applies | Use the assessment; if the outcome is still unclear, post the smallest real question in `start-here` or `ask-practice`. | Choose a route based on seniority, employer, or a preferred tool. |
| Only confidential work is available | Use a truthful sanitized description or a clearly labeled synthetic example. | Paste source documents, credentials, customer data, or internal details into Buzz. |
| No prior AI experience | Start with Learn and name one task, constraint, and check. | Assume a technical background is required. |
| An agent gives an uncertain or unsafe answer | Stop, keep restricted details out of the conversation, and ask a human or verify against the published artifact or primary source. | Treat the agent as an access administrator, moderator, or final decision-maker. |
| A contribution feels too large | Reduce it to a correction, question, Note, or bounded test. | Wait until it looks like a finished case study or project. |

## Sources and review date

- [Buzz Platform Snapshot](../research/BUZZ_PLATFORM_SNAPSHOT.md), reviewed 2026-08-31: invite-only hosted-community constraint, open-channel visibility after joining, and launch-safe capabilities.
- [Buzz access and security runbook](../ops/BUZZ_SECURITY.md), reviewed 2026-08-31: identity ownership, restricted data, and agent boundaries.
- [Buzz information architecture](../buzz/INFORMATION_ARCHITECTURE.md), reviewed 2026-08-31: channel outcomes and routing.
- [Capability Ladder](../docs/framework/CAPABILITY_LADDER.md), reviewed 2026-08-31: outcome definitions and evidence boundaries.
