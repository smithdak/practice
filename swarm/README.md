# Construction swarm

This directory answers one question: **how is the Practice repository built?**

Practice is assembled by a swarm of AI agents working from a dependency graph.
A Director model reads the canonical context, selects only dependency-ready
tasks, and creates one isolated git worktree per task. A worker completes
exactly one task, modifies only the paths that task owns, and writes
`swarm/handoffs/<ID>.md`. Independent reviewers report defects as artifacts, and
one integration task per phase applies the reviewed corrections. A human
reviews the result; the Director commits. The topology and merge protocol are
in [plans/PHASE1_PLAN.md](plans/PHASE1_PLAN.md); the Director's operating rules
are in [prompts/ORCHESTRATOR.md](prompts/ORCHESTRATOR.md).

## Map of this directory

| Path | What it holds | When to open it |
|---|---|---|
| [manifest.json](manifest.json) | The task graph. Each task records `id`, `wave`, `dependencies`, `inputs`, `outputs`, `spec`, and `handoff`, plus its title, lane, model tier, mode, objective, requirements, and acceptance. | To see what a task owns, what it waits on, and which files prove it finished. |
| [specs/](specs/) | One specification per manifest task: objective, files to read, owned outputs, scope rule, requirements, acceptance, stop conditions. | Before starting or reviewing a task. |
| [handoffs/](handoffs/) | One committed handoff per task in the shape of [templates/HANDOFF.md](../templates/HANDOFF.md): status, files changed, validation, decisions, risks, deferred opportunities. | To learn what a task did and what it left unresolved. |
| [prompts/](prompts/) | Role prompts: `ORCHESTRATOR.md` (the Director), `WORKER.md` (prepended to every generated task prompt), `REVIEWER.md`, `INTEGRATOR.md`, `BUZZ_PROVISIONER.md`. | When you run one of those roles. |
| [plans/](plans/) | `PHASE1_PLAN.md` to `PHASE5_PLAN.md`: the objective, waves, task inventory, and hard constraints of each construction phase. | To understand why a set of tasks exists. |
| [reports/](reports/) | `PHASE1_REPORT.md` to `PHASE5_REPORT.md`: the integration report for each phase, written by that phase's integration task and committed by the Director. Commands run, findings dispositioned, remaining risks. | To see how a phase ended and what it left blocked. |

For any task id, open the pair `specs/<ID>.md` and `handoffs/<ID>.md`. Example:
[specs/K007.md](specs/K007.md) says K007 owns `guides/ai-native-practitioner/04-automation-agents.md`;
[handoffs/K007.md](handoffs/K007.md) records that it was written and validated, the
decisions taken, and what was deferred.

Three handoffs have no manifest task: `P2-CLEANUP` (an owner-directed Director
pass), `PCS001` (a post-launch Project, deliberately not registered in the launch
manifest), and `Y1`. They follow the convention that every unit of work leaves a handoff.

## Set up a terminal

You need a copy of the repository (a Git clone or a downloaded archive) and a POSIX
shell with Python 3. Set two variables once; the rest is copy-paste. Adjust the paths.

```bash
PRACTICE_DIR="$HOME/projects/practice"
PRACTICE_ARCHIVE="$HOME/Downloads/practice-swarm-kit.zip"   # only for the archive route
```

> On WSL, a Windows download usually lives under
> `/mnt/c/Users/<your-windows-user>/Downloads`.

From a Git clone:

```bash
mkdir -p "$(dirname "$PRACTICE_DIR")"
git clone <repository-url> "$PRACTICE_DIR"
cd "$PRACTICE_DIR"
./scripts/init.sh
```

From a downloaded archive (this **removes** any existing copy at the target
path; check it first if you have local work there):

```bash
mkdir -p "$(dirname "$PRACTICE_DIR")"
cd "$(dirname "$PRACTICE_DIR")"
rm -rf practice-swarm-kit "$PRACTICE_DIR"
unzip "$PRACTICE_ARCHIVE"
mv practice-swarm-kit "$PRACTICE_DIR"
cd "$PRACTICE_DIR"
./scripts/init.sh
```

Open or attach a persistent terminal session:

```bash
tmux new-session -A -s practice
```

Run the environment and repository checks:

```bash
cd "$PRACTICE_DIR"
make doctor
make validate
make status
make ready
```

On a fresh checkout the controller state in `.taskctl/state.json` starts with
every task `todo`, so `make ready` lists every task that has no dependencies,
including tasks whose committed handoffs already record `COMPLETE`. The
committed record of what is done is `python3 scripts/validate.py --release`;
`ready` is authoritative only for the controller's local state.

## Run a phase

Use one high-capability model as the Director. Give it the complete contents of
[prompts/ORCHESTRATOR.md](prompts/ORCHESTRATOR.md) while its working directory
is this repository.

`python3 scripts/taskctl.py ready` is the source of truth for what can start: a
task is ready when its own status is `todo` and every dependency is `done`. The
Director creates up to ten isolated worktrees from that set. `F001` below is an
example id.

```bash
python3 scripts/taskctl.py ready
python3 scripts/taskctl.py worktree F001 --agent worker-01
python3 scripts/taskctl.py prompt F001 --output .worktrees/F001/TASK_PROMPT.md
```

Run a lower-cost worker in each `.worktrees/<TASK_ID>` directory with the
generated prompt as its only task. Workers must commit their work. Integrate
only after deterministic validation:

```bash
python3 scripts/taskctl.py integrate F001
python3 scripts/taskctl.py status
python3 scripts/taskctl.py ready
```

`integrate` refuses a dirty worktree, a missing or empty owned output, an owned
output the branch did not change, a change outside the owned set, and a failed
`validate.py --task` run. The remaining subcommands are `init`, `show <ID>`
(print the spec), `verify <ID>`, `block <ID> --reason <text>`, and `reset <ID>`.

## Seed Buzz after the content baseline exists

Run `make buzz-dry-run`, then follow [buzz/BOOTSTRAP_RUNBOOK.md](../buzz/BOOTSTRAP_RUNBOOK.md).
It is the only apply procedure. Keep the owner private key out of Buzz, out of
commits, and out of prompts.

## Where the truth lives

| Question | Source | Note |
|---|---|---|
| Which files exist? | `git ls-files` | There is no maintained file index. |
| What does a task own, depend on, and prove itself with? | [manifest.json](manifest.json) | The `outputs`, `dependencies`, and `handoff` fields. |
| Is construction complete? | `python3 scripts/validate.py --release` | Passes only when every manifest-owned output is committed and non-empty and every handoff's status is `COMPLETE`. |
| What is a task's construction status? | Not the manifest. | Its `status` field is a construction-era default (`todo` on every task) and is not authoritative. |
| What is the task controller doing right now? | `.taskctl/state.json` | Ignored local orchestration state (listed in `.gitignore`). Useful to the controller; never release evidence, and not reproducible from a checkout. |
| May Practice launch? | [release/OWNER_REVIEW.md](../release/OWNER_REVIEW.md) | Every owner gate and operating hold there is OPEN. Agents produce evidence; only a human clears a gate. |

## First-release criteria

The first release requires all seven of the following. This page asserts none
of them met: whether each holds is decided in
[release/LAUNCH_CHECKLIST.md](../release/LAUNCH_CHECKLIST.md) against the owner
gates and operating holds in
[release/OWNER_REVIEW.md](../release/OWNER_REVIEW.md), every one of which is
OPEN.

1. A seeded Buzz community with clear onboarding and no empty public channels.
2. A public repository with the manifesto, governance, contribution system, licenses, and code of conduct.
3. The AI-Native Practitioner guide map plus substantive initial modules.
4. Three tested Open Practices.
5. Five scoped community-agent profiles, with human-reviewed permissions.
6. A launch narrative, first ten content briefs, invite funnel, and first Practice Session runbook.
7. Independent fact, editorial, onboarding, and repository-integrity reviews.

Criterion 4 is explicitly unmet. All six methods in `practices/` carry `maturity: proposed`;
three have recorded trials in Labs 002 to 004, and no candidate has a recorded promotion
decision. The decision packets are in [release/PROMOTION_PACKETS.md](../release/PROMOTION_PACKETS.md).

Every ordinary task owns a non-overlapping file set, has explicit dependencies,
and must produce a committed handoff. The task controller rejects branches that
change paths outside that ownership; integration and revision tasks carry a
narrow, declared exception so they can apply reviewed corrections.

## Old paths

Translate a path cited in a dated handoff, spec, or report with this table.

| Old path | Current path |
|---|---|
| `CONTEXT.md` | `docs/CONTEXT.md` |
| `DECISIONS.md` | `docs/DECISIONS.md` |
| `NON_GOALS.md` | `docs/NON_GOALS.md` |
| `QUALITY_BAR.md` | `docs/QUALITY_BAR.md` |
| `ARCHITECTURE.md` | `docs/ARCHITECTURE.md` |
| `OWNER_GATES.md` | `docs/OWNER_GATES.md` |
| `brand/` | `docs/style/` |
| `research/BUZZ_PLATFORM_SNAPSHOT.md` | `buzz/PLATFORM_SNAPSHOT.md` |
| `SWARM_PLAN.md` | `swarm/plans/PHASE1_PLAN.md` |
| `SWARM_PHASE2_PLAN.md` | `swarm/plans/PHASE2_PLAN.md` |
| `SWARM_PHASE3_PLAN.md` | `swarm/plans/PHASE3_PLAN.md` |
| `SWARM_PHASE4_PLAN.md` | `swarm/plans/PHASE4_PLAN.md` |
| `NEW_TERMINAL.md` | `swarm/README.md` (this page) |
| `FILE_INDEX.md` | Folded into this page; use `git ls-files`. |
| `HANDOFF.md` (root) | Folded into this page; the template is `templates/HANDOFF.md`. |
| `tasks/manifest.json` | `swarm/manifest.json` |
| `tasks/specs/` | `swarm/specs/` |
| `handoffs/` | `swarm/handoffs/` |
| `prompts/` | `swarm/prompts/` |
| `release/FINAL_INTEGRATION_REPORT.md` | `swarm/reports/PHASE1_REPORT.md` |
| `release/FINAL_INTEGRATION_REPORT_V2.md` | `swarm/reports/PHASE2_REPORT.md` |
| `release/PHASE3_REPORT.md` | `swarm/reports/PHASE3_REPORT.md` |
| `release/PHASE4_REPORT.md` | `swarm/reports/PHASE4_REPORT.md` |
| `.swarm/` (ignored controller state) | `.taskctl/` |
