# Buzz information architecture

## Launch decision

Practice launches with twelve Buzz channels: two private operating channels and
ten open participation channels. Every channel is a stream. This is the
smallest set that covers the capability ladder, community operations, and the
two main contribution paths (projects and evidence). No additional channel is
needed for launch.

Buzz is the operating hub, not the durable source of truth. Reusable Practices,
Guides, Labs, Stories, Notes, and Projects belong in Git; Buzz holds the
conversation, current context, questions, and routing.

## Channel map

| Channel | Access | Distinct outcome | Use it when | Do not use it for |
| --- | --- | --- | --- | --- |
| `foundry` | Private | Construction work has a visible status, decision, blocker, or review summary. | Coordinating tasks and agents. | Public discussion or durable artifacts. |
| `maintainers` | Private | A human maintainer has an actionable governance, release, moderation, or escalation decision. | Reviewing changes that affect Practice itself. | Routine construction status or autonomous enforcement. |
| `start-here` | Open | A new Practitioner identifies a next capability and a real problem to work on. | Orientation, introductions, and first routing. | Detailed technical questions or announcements. |
| `announcements` | Open | The community can find one canonical, low-volume update or decision. | Releases, major decisions, Sessions, and new Guides or Practices. | Discussion, questions, or repeated activity updates. |
| `ask-practice` | Open | A real problem is framed well enough to receive useful help and possibly become a reusable artifact. | A workflow or decision needs community input. | Sharing a completed implementation or asking for generic tool recommendations. |
| `learn` | Open | A Practitioner gains a checkable foundation or understanding. | Models, context, tools, limitations, security, evaluation, and learning paths. | Applying a known method to a specific workflow. |
| `use` | Open | A Practitioner improves a real daily-work task while retaining appropriate judgment. | Research, writing, planning, development, analysis, and role-specific use. | Designing recurring automation or an AI-native system. |
| `automate` | Open | A repeated workflow has a decomposed, reviewable automation design. | Triggers, integrations, approvals, failure paths, and rollback. | One-off assistance or system architecture. |
| `build` | Open | An AI-native system has a reproducible technical design and evaluation approach. | Agents, tools, context architecture, retrieval, evaluation, and observability. | Organization-wide adoption or an unscoped project pitch. |
| `transform` | Open | A team or organization has a concrete operating-model or adoption decision to investigate. | Opportunity mapping, governance, measurement, and change. | Individual how-to questions or product promotion. |
| `projects` | Open | An open-source project has a bounded proposal, maintainer, and first contribution boundary. | Building Practice software or infrastructure. | Unreproducible demos or implementation results without a project need. |
| `showcase` | Open | Others can learn from a working implementation and the quality of its evidence. | Practice Stories, results, failures, lessons, and reusable artifacts. | Announcing work without evidence or seeking initial design help. |

## Routing rules

1. Start with the desired outcome, not the tool or model. Use `start-here` if
   the next outcome is unclear.
2. Use the capability ladder as the primary route: `learn` → `use` →
   `automate` → `build` → `transform`. A contribution may move forward as its
   evidence and scope mature.
3. Use `ask-practice` for an unresolved real problem. Move the resulting
   reusable answer to Git and link it from the relevant ladder channel.
4. Use `projects` only when there is a bounded open-source project proposal.
   Use `showcase` when there is an implementation or result to report.
5. Use `announcements` only for canonical updates; continue the discussion in
   the channel where the work belongs.
6. Keep construction and maintainer material in the private channels. Do not
   copy private context into an open channel by default.

## Channel lifecycle

The maintainer owner reviews channel shape as evidence accumulates. Changes are
deliberate and recorded in Git alongside the community configuration.

### Create

Create a channel only when all of these are true:

- a recurring outcome is not served by an existing channel;
- the proposed audience, access, and moderation owner are clear;
- at least three concrete launch topics or artifacts justify separation; and
- the maintainer review records why routing to an existing channel would fail.

New channels must be streams and must have a distinct name, topic, purpose,
canvas, and idempotent seed. Update this document and `buzz/community.json`
together.

### Rename

Rename only to remove ambiguity or align a channel with a settled Practice
term. Preserve the channel's outcome and update its topic, purpose, canvas,
seed, and links in the same change. Treat a rename as a routing change and
announce it once in `announcements` when members could otherwise miss it.

### Archive

Archive when the outcome is no longer needed, has been merged into another
channel, or cannot sustain useful work. Before archiving, identify the
replacement route, preserve durable artifacts in Git, and post a final pointer
in the channel. Do not delete history merely to reduce channel count.

### Split

Split only when one channel has two recurring outcomes that cannot be served by
clear prefixes or routing guidance. Define both new outcomes, demonstrate
repeated collision in the existing channel, name owners, and publish the
migration path before creating the split. Never split solely for volume,
status, role, or vendor preference.

## Platform boundary

This launch plan relies on Buzz stream channels and direct CLI seeding. It does
not depend on forum channels or scheduled workflows. See
[`research/BUZZ_PLATFORM_SNAPSHOT.md`](../research/BUZZ_PLATFORM_SNAPSHOT.md)
(as of 2026-09-01) for the verified platform assumptions.
