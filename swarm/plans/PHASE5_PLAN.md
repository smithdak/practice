# Phase 5 plan — close the two record gaps the Phase 4 report left open

**As of:** 2026-09-03 · **Baseline:** `69a35ae` (four-shelf layout, 787 tests, all checks passing)

## Why this phase exists

The Phase 4 report ends with four things a human decides next. Two of them are decisions only a human can make: whether to promote anything, and enabling the repository setting the scheduled workflow needs. The other two are record gaps that tooling can close without deciding anything for anyone:

1. **The A3 review-point trigger is unevaluable** (Phase 4 finding 5). The promotion record has no `review_point` field and there is no renewal record of any kind. The ladder requires both: "hold a review point at which the bound is renewed or withdrawn. Silence is not renewal."
2. **Five profile terms carry guardrail weight and have no observable definition** (Phase 3 finding 3). Y1 closed the sharpest one, the Steward's posting condition, and left these.

This phase adds the records and the definitions. It signs nothing, promotes nothing, enables nothing, and clears nothing.

## Tasks

| Task | Lane | Owned surface | Depends on |
| --- | --- | --- | --- |
| Z1 | operations | `ops/autonomy/` records and docs, the four autonomy scripts, their tests, the ledger schema, the operating loop's record table | X1–X4, W2 |
| Z2 | agents | the five profiles, the registry's prose fields, the five eval suites and their README | S1, S3, V1, Y1 |
| Z3 | agents | the same surface as Z2, one wave later | V1, Y1, Z2 |
| Z4 | operations | the link checker and cadence report with their tests, the stale-content queue entry, the `staleness-sweep` catalog entry's prose, and its dossier | X2, X6, Z1 |

Z1 and Z2 run in wave 17; Z3 and Z4 in wave 18. Each wave's two path sets are disjoint. Y1 is recorded in the manifest retroactively as wave 16 so the manifest and its handoff agree.

Wave 18 exists because the founder, asked what to do with the two remaining human items, chose to build the `staleness-sweep` prerequisites rather than record a decline or leave the promotion question open, and because Phase 3 finding 4 (partial compliance with an injected instruction) was the last profile gap the Phase 3 report left.

## Fixed interfaces

Stated in full in `swarm/specs/Z1.md` and `swarm/specs/Z2.md`. The ones another task or a later phase depends on:

- `review_point` is a required field on every promotion in `ops/autonomy/promotions.yaml`.
- A renewal is an entry in `ops/autonomy/renewals.yaml`, never an edit to a promotion.
- The guard gains three named preconditions: `review-point-recorded`, `renewal-record-readable`, `review-point-not-passed`.
- The ledger's promotion block requires `review_point`; the runner records the effective value.
- A profile definition is a set of conditions decided from the record, in the profile that uses the term, with at least one behavior case per term.

## Hard rules for every worker

- Own only your paths; never run `git add`, `git commit`, or `git checkout`. The Director commits.
- Never edit `swarm/manifest.json`, `.taskctl/state.json`, or another task's handoff.
- Never change a `maturity` or `evidence_quality` value, a gate or hold status, a registry `status` or `autonomy` value, `kill_switch`, or the promotion list.
- Never assert a gate is cleared, an agent is enabled, or a run has occurred.

## Director work

- Housekeeping: delete the 47 `agent/*` branches from Phase 1, all merged into `main`. (Blocked by the session's permission classifier on the first attempt; left to the owner.)
- GitHub, at the founder's direction on 2026-09-03: push `main`; enable the repository setting that lets Actions create pull requests (`can_approve_pull_request_reviews`, off by default); dispatch `unattended.yml` once with `dry_run` at its default. Run `33759586730`: the guard job refused all five operations and the writing job was skipped.
- Integration: refresh `profile_basis.source_commit` in the five eval suites after each profile change lands, relax the manifest's revision-collision rule to per-wave so sequential revisions of one file do not collide, run `make checks`, write `swarm/reports/PHASE5_REPORT.md`.

## What this phase does not do

- It does not decide whether to promote anything. The dossiers in `ops/autonomy/CANDIDATES.md` stand.
- It does not touch the ladder's demotion paragraphs; the demotion check drift-guards them.
- It does not advance launch. Every owner gate and operating hold stays OPEN.
