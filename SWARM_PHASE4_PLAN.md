# Phase 4 Swarm Plan — The A3 Substrate

**As of:** 2026-09-02 · **Baseline:** `9c59ac5` (Phase 3 complete, 562 tests
passing)

## Problem this phase solves

Phase 3 defined four autonomy levels and mapped nineteen operations onto the
first three. The fourth — A3, act-unattended-within-bounds — is defined and
empty. Nothing in the repository sits there, and nothing could: there is no way
for an operation to run without a person, no record of what an unattended run
did, no way to reverse it, no precondition that fails closed, and no mechanism
that enforces the demotion triggers the ladder already names.

Phase 4 builds that substrate. It promotes nothing.

## The owner decision this phase implements

Recorded 2026-09-02. Two choices shape everything below:

1. **Build the machinery, promote nothing yet.** Ship the ledger, the guard, the
   kill switch, reversibility, and demotion enforcement, plus the governance
   record an owner signs to promote an operation. Nothing runs unattended until
   that record is signed.
2. **Unattended runs fire as scheduled GitHub Actions that open a pull
   request.** An unattended action arrives as a reviewable diff, never as a push
   to the default branch. Reversibility is structural rather than procedural.

The seven operations [the ladder](docs/framework/AUTONOMY_LADDER.md) marks
permanently ineligible for A3 stay ineligible. Changing that list is a
governance amendment to [locked decisions](DECISIONS.md) and
[non-goals](NON_GOALS.md), not a tooling change, and this phase does not make
it.

## The safety invariant

**Shipped, the substrate is inert.** With no signed promotion and the kill
switch engaged, every operation is refused, and the scheduled workflow does
nothing but say so. Two independent records — a promotion signed by a human and
a released kill switch — must both change before any operation runs on its own.

Every task in this phase carries a test proving its own component refuses by
default. A component that would act on a repository in this state has failed its
acceptance, not passed it.

## Fixed interfaces

Workers build against these in parallel. They are settled; a task that needs one
changed writes a `BLOCKED` handoff rather than changing it unilaterally.

### The operation catalog — `ops/autonomy/operations.yaml`

Every operation that *could* one day run unattended, whether or not it is
promoted. Owned by X2.

```yaml
schema_version: 1
operations:
  - id: cadence-snapshot
    summary: Run the cadence report and write a dated status file.
    command: ["python3", "scripts/cadence.py", "--root", "."]
    write_scope: ["ops/status/*.md"]     # the ONLY paths it may create or change
    reversal: Delete the written file, or close the pull request unmerged.
    blast_radius: One new file in the repository. No member contact.
    level: A1                            # current level; A3 requires a promotion
```

The five catalog entries this phase defines, all at their current level:
`cadence-snapshot`, `metrics-snapshot`, `contract-drift-check`,
`staleness-sweep`, `release-brief-draft`.

### The promotion record — `ops/autonomy/promotions.yaml`

The governance artifact. Ships with `kill_switch: engaged` and an empty
promotion list. Owned by X2.

```yaml
schema_version: 1
kill_switch: engaged                     # engaged | released
promotions: []                           # empty: nothing is promoted
```

A promotion entry, once a human signs one:

```yaml
  - operation: cadence-snapshot
    level: A3
    write_scope: ["ops/status/*.md"]     # must equal the catalog entry's scope
    evidence: ["path/to/evidence.md"]
    demotion_triggers: ["wrote outside write_scope", "guard precondition failed"]
    signed_by: founder                   # a role from the operating vocabulary
    signed_on: 2026-09-02
```

### The guard — `scripts/autonomy_guard.py`

`--operation <id> --root .` · exit 0 permitted, 1 refused with the reason,
2 usage error. Refusal is the default; it permits only when every precondition
holds. Owned by X2.

### The runner — `scripts/run_unattended.py`

`--operation <id> --root . [--dry-run]` · calls the guard first and stops on
refusal, executes within the declared write scope, and appends a ledger entry.
Owned by X3.

### The ledger — `ops/ledger/`

One markdown file with YAML front matter per run, named
`ops/ledger/<YYYY-MM-DD>-<run_id>.md`. Schema and validator owned by X1.

## Task inventory

### Wave X-1 — parallel, no dependencies

| ID | Title | Owned outputs |
|---|---|---|
| X1 | Action ledger schema, validator, and sample | `docs/schemas/ACTION_LEDGER_SCHEMA.md`, `ops/ledger/README.md`, `ops/ledger/SAMPLE_run.md`, `scripts/ledger.py`, `tests/test_ledger.py` |
| X2 | Operation catalog, promotion record, and fail-closed guard | `ops/autonomy/operations.yaml`, `ops/autonomy/promotions.yaml`, `ops/autonomy/README.md`, `scripts/autonomy_guard.py`, `tests/test_autonomy_guard.py` |
| X6 | Promotion proposal template and candidate dossiers | `ops/autonomy/PROMOTION_PROPOSAL.md`, `ops/autonomy/CANDIDATES.md` |

X1 acceptance: a ledger entry records what ran, what it read, every path it
wrote, the reversal, and the outcome; an entry missing its reversal fails
validation. X2 acceptance: with the shipped records every operation is refused,
and the refusal names which precondition failed; a promotion whose write scope
disagrees with its catalog entry is rejected. X6 acceptance: each of the five
candidates gets a dossier stating write scope, reversal, blast radius, and the
evidence that does and does not exist — so an owner can sign or decline on
facts; no dossier recommends promotion.

### Wave X-2 — depends on X1 and X2

| ID | Title | Owned outputs |
|---|---|---|
| X3 | Unattended runner with bounded writes and reversibility | `scripts/run_unattended.py`, `tests/test_run_unattended.py` |
| X4 | Demotion trigger detection | `scripts/demotion_check.py`, `tests/test_demotion_check.py` |

X3 acceptance: refuses whenever the guard refuses; writes nothing outside the
declared scope even when the operation's command tries to; `--dry-run` writes
nothing at all; every run appends a valid ledger entry naming its reversal. X4
acceptance: evaluates the ladder's observable demotion triggers against the
ledger and the working tree, exits non-zero on a trigger, and names the entry
that fired it.

### Wave X-3 — depends on X3

| ID | Title | Owned outputs |
|---|---|---|
| X5 | Scheduled workflow that opens a pull request | `.github/workflows/unattended.yml`, `ops/autonomy/PR_REVIEW_CONTRACT.md` |

X5 acceptance: the workflow runs the guard first and exits cleanly with an
explanatory message when nothing is promoted; it never pushes to the default
branch; it opens a pull request whose body carries the ledger entry and the
reversal; its permissions are the minimum that can open a pull request.

### Wave W — integration

| ID | Title | Owned outputs |
|---|---|---|
| W2 | Wire the substrate, extend the ladder and CI, record the phase | `ops/AUTONOMOUS_OPERATION.md`, `docs/framework/AUTONOMY_LADDER.md`, `tests/test_contract_integration.py`, `release/PHASE4_REPORT.md` |

## Execution order

```text
X1  X2  X6      (parallel)
      │
      ├─ X3  X4  (need X1 and X2)
      │     │
      │     └─ X5  (needs X3)
      │
      └─ W2  (needs everything)
```

## Hard constraints (inherited, unchanged)

- One task owns one disjoint set of paths.
- Workers never edit `tasks/manifest.json` or `.swarm/state.json`, and never run
  a git command that changes state. The Director commits.
- No `maturity` or `evidence_quality` field changes. No owner gate or operating
  hold changes status.
- No agent is enabled; owner gate 6 stays open.
- Nothing is promoted to A3. `promotions.yaml` ships empty with the kill switch
  engaged.
- Python 3.11 and PyYAML only; deterministic, offline, actionable failures.
- Every task writes `handoffs/<ID>.md` using [templates/HANDOFF.md](templates/HANDOFF.md).

## Definition of done

- Every task `COMPLETE` with a committed handoff.
- `make checks` passes, and the new components run in CI.
- With the shipped records, `scripts/autonomy_guard.py` refuses all five
  operations and `scripts/run_unattended.py` refuses to act.
- The scheduled workflow is committed and inert.
- A human has a signable promotion proposal and five candidate dossiers, and has
  signed none of them.

## What this phase does not establish

The substrate being correct is not evidence that any operation should run
unattended. That judgment needs the dossiers, and it stays with a human.
