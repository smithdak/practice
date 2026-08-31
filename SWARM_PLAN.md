# Swarm Execution Plan

## Objective

Build the complete launch baseline for Practice with many low-cost agents while preserving coherence, factuality, and merge safety.

The system optimizes for parallelism only after decomposing work into non-overlapping ownership boundaries. More agents do not help when they share files, reinterpret decisions, or create integration debt.

## Agent topology

### 1. Director — one strong model

The Director does not draft most artifacts. It:

- reads the canonical context and decisions;
- initializes task state;
- selects only dependency-ready tasks;
- creates isolated worktrees;
- assigns the cheapest adequate model tier;
- monitors handoffs and blocked work;
- starts reviews after build tasks complete;
- integrates only validated branches;
- prepares owner gates rather than inventing decisions.

### 2. Workers — up to ten concurrent low-cost or balanced models

Each worker receives exactly one task prompt and one worktree. It may read the repository but may modify only the files listed in its task specification plus its unique handoff file.

### 3. Reviewers — independent contexts

Reviewers do not inherit the drafting conversation. They evaluate platform facts, editorial coherence, onboarding usability, and repository integrity. Review reports are artifacts, not informal comments.

### 4. Integrator — one strong model

The Integrator resolves cross-file inconsistencies, applies reviewer findings, runs release validation, and produces the final owner review packet. It does not reopen settled strategy.

## Model routing

| Tier | Use | Typical share |
|---|---|---:|
| Deterministic | validation, task state, link checks, Buzz seeding | first choice |
| Cheap | templates, seed posts, constrained rewrites, checklists, bounded profiles | majority |
| Balanced | governance, curricula modules, runbooks, synthesis | substantial minority |
| Strong | manifesto, flagship architecture, launch narrative, adversarial editorial review, final integration | minimal |

Do not use a strong model merely because a task is large. Split the task until a cheaper model can complete it reliably.

## Context minimization

Every worker prompt contains:

1. `AGENTS.md` operating rules;
2. the task's exact specification;
3. references to required canonical files;
4. owned output paths;
5. acceptance checks;
6. the handoff contract.

Workers should not load the full repository when their task depends on four files. This reduces cost and conflicting interpretation.

## Merge isolation

- One task = one branch = one worktree.
- No two active tasks own the same path.
- Workers never edit `tasks/manifest.json` or `.swarm/state.json`.
- Workers commit before handoff.
- Integration rejects dirty worktrees, missing outputs, unchanged owned files, or failed validation.
- Review tasks begin only when their dependencies are marked done.

## Waves

### Wave 1 — foundation

Brand language, manifesto, capability taxonomy, governance, contribution, moderation, licensing, metrics, and contributor experience.

### Wave 2 — Buzz system

Channel architecture, onboarding, canvases, seed posts, bootstrap automation, security, and community-agent profiles.

### Wave 3 — knowledge system

Artifact schemas, flagship guide map and modules, first Practices, first Lab, and first Story.

### Wave 4 — launch and operations

Launch narrative, content briefs, social kit, first session, maintainer cadence, invitation flow, and launch checklist.

### Wave 5 — independent review and integration

Platform fact audit, voice review, onboarding simulation, repository integrity review, and final integration.

## Director loop

```text
initialize state
  → list ready tasks
  → create up to 10 worktrees
  → dispatch bounded workers
  → inspect handoffs
  → integrate passing branches
  → mark blocked tasks with evidence
  → list newly ready tasks
  → repeat
  → run independent reviews
  → integrate review fixes
  → run release validation
  → prepare owner packet
```

## Failure handling

A worker must stop and write `BLOCKED` in its handoff when:

- a required decision conflicts with `DECISIONS.md`;
- the task would require editing an unowned file;
- a current platform capability cannot be verified;
- required source material is unavailable;
- an acceptance criterion is mutually inconsistent.

The Director may split or reassign the task. It must not let a worker guess through the block.

## Buzz use during construction

Use the private `foundry` channel for status, decisions, and review summaries. Give each construction agent its own Buzz identity if it participates in the relay. Do not give any agent the owner private key.

The critical path uses direct CLI commands, not scheduled workflows. Forum channels are not used for automated seeding in this release.

## Completion criteria

The build is ready for Dakota's review only when:

- all non-deferred tasks are done;
- all review reports exist;
- `python3 scripts/validate.py --release` passes;
- Buzz bootstrap dry run shows no unintended destructive action;
- the owner packet lists every remaining manual gate and its default;
- no public launch artifact contains TODOs, invented evidence, or unverified platform claims.
