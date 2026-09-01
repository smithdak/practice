# Practice — Swarm Build Kit

This repository is the executable build plan for **Practice**, the open community for AI practitioners.

**Positioning:** The open community for AI practitioners.  
**Ethos:** Learn it. Build it. Use it. Share it.  
**North star:** Build the open standard for becoming AI-native.

Buzz is the human-and-agent operating hub. Git is the canonical, public, versioned source for durable artifacts. Social channels distribute the work and route people into Practice.

## Start in a fresh terminal

```bash
./scripts/init.sh
make doctor
make status
make ready
```

Then choose one operating mode:

### Director mode

Open `prompts/ORCHESTRATOR.md` in one strong model and let it coordinate bounded workers.

### Manual fan-out

```bash
python3 scripts/taskctl.py worktree F001 --agent worker-01
python3 scripts/taskctl.py prompt F001 --output .worktrees/F001/TASK_PROMPT.md
# Run a low-cost model inside .worktrees/F001 using TASK_PROMPT.md.
python3 scripts/taskctl.py integrate F001
```

Every ordinary task owns a non-overlapping file set, has explicit dependencies,
and must produce a committed handoff. The deterministic task controller rejects
ordinary task branches that change paths outside that ownership. The final
integration task has an explicit narrow exception so it can apply reviewed
corrections across artifacts.

## Core documents

- `NEW_TERMINAL.md` — exact pickup sequence for the owner's terminal environment.
- `SWARM_PLAN.md` — topology, waves, model routing, and merge protocol.
- `AGENTS.md` — rules every agent must follow.
- `tasks/manifest.json` — machine-readable dependency graph.
- `prompts/ORCHESTRATOR.md` — master swarm prompt.
- `buzz/community.json` — idempotent Buzz community specification.
- `scripts/buzz_bootstrap.py` — dry-run-first Buzz seeder.
- `buzz/PROJECT_AND_WORKFLOW_RUNBOOK.md` — owner-run Buzz Project setup and a disabled private workflow pilot.
- `research/BUZZ_PLATFORM_SNAPSHOT.md` — verified Buzz constraints as of 2026-09-01.

## Launch boundary

The first release is complete when Practice has:

1. A seeded Buzz community with clear onboarding and no empty public channels.
2. A public repository with the manifesto, governance, contribution system, licenses, and code of conduct.
3. The AI-Native Practitioner guide map plus substantive initial modules.
4. Three tested Open Practices.
5. Five scoped community-agent profiles, with human-reviewed permissions.
6. A launch narrative, first ten content briefs, invite funnel, and first Practice Session runbook.
7. Independent fact, editorial, onboarding, and repository-integrity reviews.

Construction status in `.swarm/state.json` is local, ignored operational state.
It is useful to the task controller but is not release evidence and is not
reproducible from a checkout. Release validation derives completion from the
committed manifest-owned outputs and `COMPLETE` handoffs.

The six current method files are proposed candidates with
`evidence_quality: none`. The first three have recorded trials in
`labs/002`–`004`; a recorded trial does not change a method's maturity, and no
candidate has a recorded promotion decision, so criterion 4 and public-launch
completion remain unmet pending human review.

No custom SaaS, course platform, certification program, or large marketing site belongs in this build.
