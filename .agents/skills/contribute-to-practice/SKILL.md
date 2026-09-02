---
name: contribute-to-practice
description: Produce one scoped, reviewable change in the Practice repository, selecting the smallest contribution path and following an assigned swarm task when one exists. Use for implementing a Practice repository contribution; do not use for general contribution questions with no requested repository change.
---

# Contribute to Practice

## Source of truth

Read [AGENTS.md](../../../AGENTS.md), [docs/CONTEXT.md](../../../docs/CONTEXT.md), [docs/DECISIONS.md](../../../docs/DECISIONS.md), [docs/NON_GOALS.md](../../../docs/NON_GOALS.md), and [docs/QUALITY_BAR.md](../../../docs/QUALITY_BAR.md) before editing. Use [CONTRIBUTING.md](../../../CONTRIBUTING.md) and the [Contribution Model](../../../community/CONTRIBUTION_MODEL.md) to choose the smallest contribution path.

For a registered swarm task, its task specification owns scope and paths. [`scripts/taskctl.py`](../../../scripts/taskctl.py) is authoritative for task state, worktrees, verification, and integration. Never edit `swarm/manifest.json` or `.taskctl/state.json` directly and never imitate their state in another file.

## Inputs and routing

Establish the concrete Practitioner problem, intended user, smallest useful outcome, evidence, repository state, and authorization to edit. If a swarm task is assigned, require its ID and specification, then use its owned outputs and acceptance checks. If no task is assigned, choose correction, Note, Practice, Guide/Lab/Story, Project proposal, or maintained Project from the canonical contribution guidance; do not invent a swarm task or handoff requirement.

Stop before editing when the required scope or owned paths are missing, a locked decision conflicts with the request, or completion requires an unowned path. Ask for the smallest missing decision.

## Workflow

1. Inspect the worktree and preserve unrelated user changes. Read the complete assigned specification and all named inputs before acting.
2. State the exact output paths and acceptance checks. Make the smallest change that solves the assigned problem; record adjacent ideas for later rather than expanding scope.
3. Keep claims proportional to evidence. Label examples, proposals, hypotheses, and unknowns. For current technical claims, use a primary source and record its URL and as-of date. Do not include secrets, confidential material, unnecessary personal data, or unlicensed content.
4. Run checks appropriate to the artifact. For a swarm task, run the exact task validation command and resolve failures only within owned paths.
5. For a swarm task, create `swarm/handoffs/<TASK_ID>.md` from the handoff template with status, changed files, validation evidence, task-local decisions, risks, and deferred opportunities. If blocked, record the exact evidence and smallest decision needed rather than guessing.
6. Review the complete diff for scope, accidental changes, and unsupported claims. Commit only the owned paths with `task(<TASK_ID>): <concise description>` when the task contract requires a commit, then confirm the worktree is clean.

Do not claim or integrate a task, open an external issue or pull request, publish to Buzz, or make another external change unless the user explicitly requested that action and the current environment authorizes it.

## Deliverable

Return one focused repository change with evidence suited to its artifact type. For a swarm task, include the required handoff, validation result, commit identifier, and clean-worktree result. For an ordinary contribution, report the contribution path, changed files, verification, evidence limits, and the next human review step.

## Stop and failure handling

Do not work around a failed gate by editing task state, widening permissions, modifying another task's files, or weakening acceptance criteria. When a failure cannot be resolved inside scope, leave safe partial work only if the task contract permits it, write a `BLOCKED` handoff when required, and name the precise owner decision or evidence needed.
