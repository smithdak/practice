# Agent Operating Contract

You are working on **Practice**, an open-source community for AI practitioners.

## Read before acting

1. `docs/CONTEXT.md`
2. `docs/DECISIONS.md`
3. `docs/NON_GOALS.md`
4. `docs/QUALITY_BAR.md`
5. your assigned task specification

## Orientation

- Setup, the task loop, and where construction truth lives: `swarm/README.md`.
- The repository layout: the Repository map in `README.md`.

## Scope

- Complete exactly one task.
- Modify only the output paths listed in the task plus `swarm/handoffs/<TASK_ID>.md`.
- Do not edit `swarm/manifest.json`, `.taskctl/state.json`, or another task's handoff.
- Do not expand the product scope.
- Record adjacent ideas under **Deferred opportunities** in the handoff.

## Evidence

- Never invent facts, metrics, quotes, case studies, users, outcomes, or platform features.
- For current technical claims, prefer primary sources and record the source URL and as-of date.
- Use `buzz/PLATFORM_SNAPSHOT.md` for Buzz assumptions.
- Label examples and hypothetical scenarios explicitly.

## Writing

- Lead with the concrete problem or outcome.
- Prefer operational steps, decision rules, examples, and failure modes.
- Remove generic AI enthusiasm and repeated slogans.
- Keep the brand model-agnostic.
- Use **Practitioner** for a community member when the identity matters.
- Use **Practice** for a reusable method and **Practice** for the community only when context is clear.

## Buzz constraints

- Do not require scheduled workflows for launch.
- Do not automate forum root posts.
- Do not put secrets or confidential information into Buzz.
- Never request or expose an owner private key.
- Community agents may recommend moderation actions but may not silently remove people or content.

## Completion

1. Run `python3 scripts/validate.py --task <TASK_ID> --root .`.
2. Create `swarm/handoffs/<TASK_ID>.md` using `templates/HANDOFF.md`.
3. Commit all changes with `task(<TASK_ID>): <concise description>`.
4. Leave the worktree clean.

If blocked, still create and commit the handoff with the exact evidence and smallest decision needed to proceed.
