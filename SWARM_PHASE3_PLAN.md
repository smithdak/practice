# Phase 3 Swarm Plan — Autonomous Operation Readiness

**As of:** 2026-09-02 · **Baseline:** `5890629` (Phase 2 complete, all four
validation gates passing)

## Problem this phase solves

Phase 1 built the artifacts. Phase 2 produced the evidence, the validators, and
the launch-ops packets. Both phases left one thing untouched: **everything
about how agents operate the community is prose.**

Five agent profiles in `buzz/agents/` describe missions and guardrails in
Markdown. [The weekly cadence](ops/WEEKLY_CADENCE.md) describes an operating
loop a person must read and apply by hand. [The metrics
contract](ops/METRICS.md) defines what to count and has no collector.
[Practice 004](practices/004-issue-triage.md) and [Practice
005](practices/005-release-notes.md) describe triage and release notes as
methods a human performs. Nothing is machine-readable, nothing is executable,
and no test anywhere establishes that an agent respects its own guardrails.

The consequence is concrete: the community cannot run a single operating pass
without a person present to work out what is due, count what happened, and
check that an agent stayed in bounds.

Phase 3 has one objective: **make the operating loop runnable and the agent
boundary machine-checkable, without moving a single human-owned decision to an
agent.**

## What this phase deliberately does not do

Autonomy here means the loop runs without a person computing it. It does not
mean agents gain authority. The following stay exactly where Phase 1 put them:

- Moderation, banning, and content removal remain human-owned decisions
  ([NON_GOALS.md](NON_GOALS.md), [DECISIONS.md](DECISIONS.md)). Agents triage
  and recommend.
- Promotion of a method to a tested Practice remains a human decision with
  recorded evidence ([release/PROMOTION_PACKETS.md](release/PROMOTION_PACKETS.md)).
- Publication, merging, and announcement remain human-approved.
- The owner identity and private key are never handled by an agent.
- No owner gate or operating hold changes status in this phase. Every gate and
  hold in [release/OWNER_REVIEW.md](release/OWNER_REVIEW.md) stays OPEN.
- No scheduled Buzz workflow becomes a dependency. Every runner in this phase
  is a local, offline script.

No agent in this phase is enabled. Owner gate 6 — initial community-agent
providers — is OPEN, so the registry records every agent as not enabled.

## Hard constraints (inherited, unchanged)

- One task owns one disjoint set of paths; no two active tasks own the same
  path.
- Workers never edit `tasks/manifest.json` or `.swarm/state.json`.
- Workers never change a `maturity` or `evidence_quality` field.
- Every task writes `handoffs/<ID>.md` using [templates/HANDOFF.md](templates/HANDOFF.md),
  marking `BLOCKED` with evidence rather than guessing.
- Scripts are Python 3.11, deterministic, offline, and fail with actionable
  messages. PyYAML is the only permitted third-party dependency; CI installs it.
- Tests are `unittest` under `tests/`, discovered by
  `python3 -m unittest discover -s tests`.
- Anything touching an open owner gate produces evidence; it never asserts the
  gate is cleared.

## Task inventory

### Wave S — Machine-readable operating contracts

| ID | Title | Owned outputs |
|---|---|---|
| S1 | Agent registry and boundary validator | `buzz/agents/registry.yaml`, `scripts/validate_agents.py`, `tests/test_validate_agents.py` |
| S2 | Agent output packet contract | `docs/schemas/AGENT_PACKET_SCHEMA.md`, `templates/AGENT_PACKET.md`, `scripts/validate_packet.py`, `tests/test_validate_packet.py` |
| S3 | Autonomy ladder and policy test | `docs/framework/AUTONOMY_LADDER.md`, `tests/test_autonomy_policy.py` |

S1 derives the registry from the five profile files — it grants no scope a
profile does not state — and fails when a declared channel is absent from
`buzz/community.json`, when a guardrail list drops a locked non-negotiable, or
when an agent claims to be enabled while gate 6 is open.

S2 turns the "bounded packet" every profile promises into a schema a validator
can check: provenance and trust level per input, a claim line that carries a
pointer or does not appear, a required refusals section, and
`human_decision_required` fixed true.

S3 defines the levels an operation can occupy — observe, draft, recommend,
act-unattended — states which operations are permanently ineligible for the
last one, and encodes the mapping as a test. Nothing in the repository sits at
act-unattended, and moving anything there is a human decision.

### Wave T — The runnable operating loop

| ID | Title | Owned outputs |
|---|---|---|
| T1 | Cadence and queue runner | `ops/cadence.yaml`, `scripts/cadence.py`, `tests/test_cadence.py` |
| T2 | Metrics collector | `scripts/collect_metrics.py`, `tests/test_collect_metrics.py`, `ops/metrics/README.md` |
| T3 | Release brief generator | `scripts/release_brief.py`, `tests/test_release_brief.py`, `release/briefs/` |
| T4 | Issue triage state machine | `scripts/triage.py`, `tests/test_triage.py`, `ops/triage/` |

Each Wave T task implements a procedure the repository already specifies. T1
encodes only the passes [the cadence](ops/WEEKLY_CADENCE.md) defines. T2
implements only the metrics [the measurement contract](ops/METRICS.md) says are
countable from committed Git evidence, and prints every other metric as
requiring the human route rather than as a zero. T3 implements the
pointer-checked draft method from [Practice
005](practices/005-release-notes.md). T4 implements the state machine from
[Practice 004](practices/004-issue-triage.md), including the rule that a record
last moved by an agent may not sit in a human-owned state.

### Wave V — Agent behavior evidence

| ID | Title | Owned outputs |
|---|---|---|
| V1 | Community-agent eval suites, including adversarial-input cases | `buzz/agents/evals/`, `scripts/validate_agent_evals.py`, `tests/test_validate_agent_evals.py` |

The five agent profiles claim to treat messages, links, and attachments as
untrusted source data rather than as instructions. No case anywhere tests that
claim. V1 defines observable cases per agent — routing, behavior, and a
required adversarial class covering instruction injection, key requests,
publish and merge requests, maturity changes, removal requests, and vendor
endorsement. It records no results: defining a case is not evidence that an
agent passed it.

### Wave W — Integration

| ID | Title | Owned outputs |
|---|---|---|
| W1 | Wire the loop, extend CI, record the phase | `ops/AUTONOMOUS_OPERATION.md`, `Makefile`, `.github/workflows/ci.yml`, `tasks/manifest.json`, `release/PHASE3_REPORT.md` |

W1 is the Director's task. It ties the contracts and runners into one
documented operating procedure, adds the new validators to CI, wires the Phase 3
tasks into the manifest so `taskctl.py` and `scripts/validate.py --task <ID>`
recognize them, and records what the phase produced against what it did not
change.

## Execution order

```text
S1 S2 T1 T2 T3 T4   (parallel; no dependencies)
        │
        ├─ S3   (needs S1's registry)
        └─ V1   (needs S1's registry and S2's packet contract)
                │
                └─ W1  (needs everything)
```

## Definition of done

- Every task `COMPLETE` with a committed handoff.
- `python3 scripts/validate.py --release --root .`,
  `python3 -m unittest discover -s tests`,
  `python3 scripts/validate_artifacts.py --root .`,
  `python3 scripts/check_links.py .`, and
  `python3 skills/evals/validate.py --root .` all pass.
- The new validators pass and run in CI.
- Every owner gate and operating hold still reads OPEN; no `maturity` or
  `evidence_quality` field changed; no agent is enabled.

## Post-phase backlog (recorded, not started)

- Behavioral eval runs of the community agents against the V1 cases, once an
  owner enables an agent under gate 6.
- A packet archive with retention rules, once real packets exist.
- Buzz-side activity signals for the cadence runner, which today reads Git only.
- The Phase 2 backlog carried forward: facilitation prompts from real channel
  questions, captioned launch cuts, a production calendar with named hosts,
  plugin packaging of the stable skill subset, measured queue service levels,
  and a disposable-relay integration test for the bootstrapper.
