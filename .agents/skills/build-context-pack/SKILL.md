---
name: build-context-pack
description: Build or update a reusable context pack for one recurring task, including approved sources, constraints, examples, ownership, freshness, and review checks. Use when recurring AI-assisted work needs a repeatable starting context; do not use for a one-off low-risk prompt.
---

# Build a reusable context pack

## Source of truth

Read [Practice 001](../../../practices/001-context-pack.md) completely before acting. Treat it as the canonical method. This skill adapts that Practice to the user's environment; it does not weaken its evidence, privacy, approval, or maintenance rules.

## Inputs

Establish the recurring task and expected output, task owner, reviewer, approved sources, constraints, representative examples, acceptance checks, and an appropriate storage location. Ask only for missing information that materially changes the boundary, permissions, or deliverable. Mark unavailable facts as unknown.

Never request or copy passwords, API keys, private keys, unnecessary personal data, or confidential material into a shared pack. Keep restricted sources in their approved systems and use permitted references or safe summaries.

## Workflow

1. State the task, audience, allowed inputs, output, exclusions, owner, reviewer, and any effect that requires human approval.
2. Choose the smallest usable form: one maintained document for a simple task or a folder when sources, instructions, examples, and checks need separate ownership.
3. Build a source register. For each source, record its owner, location, date or version, permitted use, purpose, and freshness. Separate authoritative from optional material.
4. Write operating instructions separately from source content. Define precedence, missing-input and conflict handling, output shape, and escalation conditions.
5. Record privacy, access, safety, scope, and style constraints. Label examples as examples and explain what decision each demonstrates.
6. Define observable acceptance checks before the first run. Include at least one missing, conflicting, stale, or out-of-scope case and say who reviews a failed check.
7. Add a version, owner, reviewed date, event-based review triggers, and change record. Dry-check whether another authorized Practitioner can locate the rules, trace a sample fact, and handle the edge case without oral context.

## Deliverable

Return or create a versioned context pack containing the task boundary, instructions, source register, constraints, labeled examples where useful, acceptance checklist, and owner/reviewer details. Include a short review record or a ready-to-use review-record template. State unknowns and limitations; do not claim improved accuracy, speed, cost, or outcomes without measured evidence.

## Stop and failure handling

Pause the affected work when a critical source is stale or unavailable, instructions conflict, permissions are unclear, no accountable owner exists, or the requested pack would expose restricted information. Report the exact gap, its consequence, and the smallest owner decision or safe substitute needed. Do not fill gaps from memory or silently discard a constraint.
