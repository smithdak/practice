# Phase 2 Swarm Plan — Evidence, Currency, and Community Progression

## Problem this phase solves

The Phase 1 build is complete and release validation passes, but public launch
is blocked by evidence, not by missing artifacts: all three method candidates
are `maturity: proposed` with `evidence_quality: none`, the platform snapshot
is dated 2026-08-31, seven owner gates are open, and every handoff recorded
deferred automation that never had an owner.

Phase 2 therefore has one objective: **produce the recorded evidence, current
research, and automation that let a human clear the launch blockers quickly,
and prepare the first post-launch work**. Agents never clear gates; they make
each gate take an owner minutes instead of hours.

## Hard constraints (inherited, unchanged)

- One task = one branch = one worktree; no two active tasks own the same path.
- Workers never edit `tasks/manifest.json` or `.swarm/state.json`.
- No agent creates, receives, stores, or recovers the owner Buzz identity or
  private key; the Buzz apply is owner-operated.
- Human-owned moderation and promotion: a Practice becomes *tested* only after
  a recorded trial plus explicit human review.
- No scheduled Buzz workflows; no secrets or participant data in Git.
- Every task commits and writes `handoffs/<ID>.md` using `templates/HANDOFF.md`,
  marking `BLOCKED` with evidence rather than guessing.
- Anything touching an open owner gate produces evidence packets; it never
  asserts the gate is cleared.

## Task inventory

Tier: `code` (deterministic scripting), `cheap` (bounded prose), `balanced`
(synthesis/ops design), `strong` (reserved for final adversarial review).

### Wave R — Research and verification (no dependencies; run first, in parallel)

| ID | Title | Tier | Owned outputs |
|---|---|---|---|
| R1 | Refresh the Buzz platform snapshot against live sources | balanced | `research/BUZZ_PLATFORM_SNAPSHOT.md` |
| R2 | Currency audit of guide modules and Practices (claims, tool names, as-of dates) | balanced | `research/GUIDE_CURRENCY_AUDIT.md` |
| R3 | Adjacent-community landscape scan (what practitioners already have; positioning gaps) | cheap | `research/COMMUNITY_LANDSCAPE.md` |
| R4 | License, attribution, and claim re-audit of all publishable artifacts | balanced | `research/CLAIM_AUDIT.md` |

R1 acceptance: every capability claim re-verified against primary sources with
a new as-of date; removed or corrected claims listed; no new capabilities
asserted without a source URL. R2 acceptance: per-module table of stale or
unsourced claims with proposed corrections; no edits to guide prose (that is
G1). R3 acceptance: factual scan only, no fabricated user counts; explicit
"example/hypothetical" labels. R4 acceptance: zero unlicensed or
unattributed items; findings as a checklist, not prose.

### Wave A — Automation and integrity (parallel; independent of R)

| ID | Title | Tier | Owned outputs |
|---|---|---|---|
| A1 | Schema-aware artifact validators (Practice, Guide, Lab, Story front matter, maturity/evidence invariants) | code | `scripts/validate_artifacts.py`, `tests/test_validate_artifacts.py` |
| A2 | Link checker and as-of-date linter | code | `scripts/check_links.py`, `tests/test_check_links.py` |
| A3 | IA ↔ `buzz/community.json` parity test | code | `tests/test_buzz_parity.py` |
| A4 | GitHub CI wiring: unit tests, `validate.py --release`, link check on PR | code | `.github/workflows/ci.yml` |
| A5 | Reusable non-secret release-evidence record template | cheap | `templates/RELEASE_EVIDENCE.md` |

These fulfill recorded deferrals from K001/K002/K013/K014 (A1), B009/B010/K010
(A2), B001 (A3), B011 (A4/A5). Acceptance for all A tasks: deterministic,
offline-runnable, fail with actionable messages; A1 must flag any artifact
claiming `maturity: tested` without a linked trial record.

### Wave E — Trials and evidence (the launch-critical wave; depends on A1 for the evidence ledger, except E4)

| ID | Title | Tier | Owned outputs |
|---|---|---|---|
| E1 | Trial Practice 001 (context pack) on a real recurring task; record a Lab | balanced | `labs/002-context-pack-trial.md` |
| E2 | Trial Practice 002 (workflow redesign) on a safe, owned workflow; record a Lab | balanced | `labs/003-workflow-redesign-trial.md` |
| E3 | Trial Practice 003 (verification gate) including one rollback rehearsal; record a Lab | balanced | `labs/004-verification-gate-trial.md` |
| E4 | Run the five Practice-core skill evals on two model families; record results | code | `skills/evals/results/` , `skills/evals/EVAL_REPORT.md` |
| E5 | Assemble promotion packets per candidate: trial evidence, reviewer notes, and the human decision to make | balanced | `release/PROMOTION_PACKETS.md` |

Rules for E1–E3: trials run inside this repository's own work (a context pack
for a swarm role, a redesign of a real repo workflow, a gate applied to a
worker merge) so the evidence is real, non-confidential, and reproducible.
E1–E3 must use the LAB schema and leave `evidence_quality` claims to what the
record actually shows. E5 never flips `maturity` — it packages the decision.
Human promotion review remains the gate (E5 → owner or named maintainer).

### Wave G — Knowledge progression (depends on R2/R4 findings, not on E)

| ID | Title | Tier | Owned outputs |
|---|---|---|---|
| G1 | End-to-end guide review: fix links, apply R2 corrections, canonical-Practice cross-links | balanced | `guides/ai-native-practitioner/**` |
| G2 | Note, Project, and Issue schemas and templates (B008 deferral) | balanced | `docs/schemas/NOTE_SCHEMA.md`, `docs/schemas/PROJECT_SCHEMA.md`, `templates/NOTE.md`, `templates/PROJECT.md` |
| G3 | Scope Practices 004–006 from demonstrated needs (issue triage policy, release notes, contributor feedback instrument) | balanced | `practices/004-issue-triage.md`, `practices/005-release-notes.md`, `practices/006-feedback-instrument.md` |
| G4 | Contributor intake, consent, and redaction templates for Stories and Workflow Clinics (L002/L004 deferral) | balanced | `templates/INTAKE_CONSENT.md`, `templates/REDACTION_CHECKLIST.md` |

G3 outputs are `maturity: proposed` candidates only; promotion follows the
same trial path as Wave E in a later phase.

### Wave O — Launch-ops support (depends on E5 for the tested-Practice packet; others parallel)

| ID | Title | Tier | Owned outputs |
|---|---|---|---|
| O1 | One evidence packet per open owner gate (what to review, command outputs, exact human action) | balanced | `release/GATE_EVIDENCE.md` |
| O2 | Steward escalation readiness test script and dry-run script (human executes against the live route) | code | `scripts/steward_readiness_check.py` |
| O3 | Hosted-surface inspection checklist for the owner-operated apply | cheap | `release/HOSTED_INSPECTION.md` |
| O4 | Re-run the onboarding simulation with Phase 2 artifacts; record results | balanced | `reviews/ONBOARDING_DRY_RUN_V2.md` |
| O5 | Private-beta ops kit: facilitation prompt backlog scaffold, issue-triage labels and response guide (F005 deferral) | balanced | `ops/BETA_OPS.md`, `.github/ISSUE_TEMPLATE/triage-policy.md` |

O1 is the consolidation task an integrator runs last; it owns only
`release/GATE_EVIDENCE.md` and must not rewrite `OWNER_REVIEW.md` (the
integrator task O-INT below applies its accepted updates).

### Wave Q — Independent review and integration (strong/balanced)

| ID | Title | Tier | Owned outputs |
|---|---|---|---|
| Q6 | Adversarial review of all Wave E evidence: is any claim overreaching? | strong | `reviews/EVIDENCE_REVIEW.md` |
| Q7 | Fact and currency re-audit of research outputs | balanced | `reviews/FACT_AUDIT_V2.md` |
| Q-INT | Integrate accepted findings, update `OWNER_REVIEW.md` evidence rows, run release validation | strong | `release/OWNER_REVIEW.md`, `release/FINAL_INTEGRATION_REPORT_V2.md` |

## Execution order and parallelism

```text
R1 R2 R3 R4 ─┐
A1 A2 A3 A4 A5 ─┤
                ├─ E1 E2 E3 (need A1)   E4 (need nothing)
             G1 G2 G3 G4 (need R2/R4)
                        E5 (need E1–E3)
                        O1 O2 O3 (parallel), O4 (need A/G merged), O5
                        Q6 Q7 (need E/G/O drafted) → Q-INT → owner packet
```

Up to ten workers; the cheapest adequate tier per task. E1–E3 are deliberately
scoped small enough for balanced models: one task, one trial, one Lab.

## Post-launch backlog (do not start; recorded for Phase 3)

- Facilitation prompts and example replies from real channel questions (B004).
- Captioned short-form launch cuts after the flagship capture exists (L001).
- Production calendar with named hosts and review owners (L002).
- Plugin packaging of the stable public skill subset (PCS001).
- Measured queue service levels and cadence revision after real beta data (L007).
- A disposable-relay integration test for the bootstrapper (B005).

## Wiring and completion

- Wiring: when the owner approves this plan, a single authorized task appends
  these tasks to `tasks/manifest.json` (ids as listed, waves 6–9) and updates
  `scripts/taskctl.py` state initialization. Until then, run manual fan-out
  with `taskctl.py worktree <ID>`.
- Definition of done for the phase: all non-deferred tasks `COMPLETE`;
  `python3 scripts/validate.py --release`, `python3 -m unittest discover -s
  tests`, and `python3 skills/evals/validate.py --root .` pass; every owner
  gate has an evidence packet; three promotion packets await a human decision;
  no artifact claims tested maturity without that decision; worktree clean.
