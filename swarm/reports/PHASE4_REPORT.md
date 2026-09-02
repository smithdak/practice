# Phase 4 report — the A3 substrate

**As of:** 2026-09-02 · **Integrator:** W2 · **Baseline:** `9c59ac5` (Phase 3
complete, 562 tests)

## Outcome

Phase 4 is integrated. Seven tasks built the machinery an operation would need
to run without a person — a catalog, a promotion record, a fail-closed guard, a
bounded runner, an append-only ledger, demotion detection, and a scheduled
workflow that opens a pull request — and carried a founder governance amendment
into the ladder and the tooling.

**Nothing is promoted. Nothing runs unattended.** `ops/autonomy/promotions.yaml`
ships with `kill_switch: engaged` and an empty promotion list, and all five
catalogued operations refuse. No owner gate or operating hold changed status, no
`maturity` or `evidence_quality` field changed, and no agent is enabled.

Test count moved from 562 to 787.

## The safety invariant, and how it is held

**Two independent records must both change before anything runs.** A signed
promotion alone is refused while the kill switch is engaged; a released kill
switch alone is refused with nothing promoted. A single mistaken edit is
therefore harmless, and each half is a separate human act.

Four further properties hold it in place:

1. **Refusal is the default.** The guard's twenty-four preconditions refuse on
   missing, malformed, or disagreeing records. It never falls back to permitted.
2. **The writing job never starts.** The scheduled workflow's second job is
   gated on an operation being permitted, so in the shipped state the run holds
   no token that can write.
3. **Out-of-scope writes are never applied.** The runner executes the operation
   in a staging copy and copies results back only when every touched path is in
   scope, so no reversal has to repair the repository.
4. **A catalog entry may not declare A3.** One file can never promote something.

Verify it in one command:

```bash
make autonomy
```

## What was built

| Task | Output | What it guarantees |
| --- | --- | --- |
| X1 | [Action ledger](../../ops/ledger/README.md), schema, validator | Append-only record of what a run read, wrote, and how to reverse it |
| X2 | [Catalog, promotion record, guard](../../ops/autonomy/README.md) | Eligibility is a record a validator checks; refusal is the default |
| X3 | `scripts/run_unattended.py` | Staging-copy execution; a write outside scope is never applied |
| X4 | `scripts/demotion_check.py` | The ladder's observable triggers evaluated, so a level can go down |
| X5 | `.github/workflows/unattended.yml`, [review contract](../../ops/autonomy/PR_REVIEW_CONTRACT.md) | An unattended action arrives as a pull request; closing it is a complete reversal |
| X6 | [Proposal](../../ops/autonomy/PROMOTION_PROPOSAL.md), [candidate dossiers](../../ops/autonomy/CANDIDATES.md) | The decision is recordable and informed, not easier to approve |
| W2 | [Amendment 001](../../community/AMENDMENTS.md), this report, the wiring | The governance change is recorded, and the tooling agrees with it deliberately |

## Amendment 001, and the guard that refused it

The founder decided to make two of the seven permanently ineligible operations
eligible for A3: `merge`, narrowed to bounded auto-merge, and
`publication-and-announcement`, split so that only `publication-approval`
remains ineligible while `publication-delivery` — byte-identical delivery of
already-approved content to a destination named in the approval — becomes
eligible. `maturity-promotion` and `moderation-and-removal` were considered and
declined; owner identity and keys, license and governance change, and
owner-reserved decisions were not proposed. All of that is recorded, with
reasoning, in [the amendments record](../../community/AMENDMENTS.md).

**Applying it was itself a test of the design.** Editing the ladder's ineligible
list immediately made the guard refuse every operation with a new precondition
failure:

> `docs/framework/AUTONOMY_LADDER.md` no longer lists merge,
> publication-and-announcement as permanently ineligible for A3, but
> `scripts/autonomy_guard.py` still does. Removing an operation from that list
> is a governance amendment to `docs/DECISIONS.md` and `docs/NON_GOALS.md`, not a tooling
> change; until the two agree the guard refuses.

That is the correct behavior. A governance change has to be deliberate in both
the document and the tooling, and the guard would not let a document edit alone
widen what may run. Three further test suites failed on the same edit for the
same reason. Each was updated explicitly, and a new cross-contract suite now
asserts that the amendment, the ladder, and the guard say the same thing — and
that nothing the amendment declined became eligible.

Eligible is not promoted. Neither replacement is catalogued, and neither can run.

## Findings the work surfaced

1. **A write scope was one directory level wider than it read.** `fnmatch`
   lets `*` cross `/`, so `ops/status/*.md` also admitted
   `ops/status/archive/old.md`. The runner now matches segment-wise, and a scope
   that wants a subtree must say `**`. The guard's matcher deliberately stays
   loose, because it asks the opposite question — whether a declared scope
   *could reach* a governed path — and both halves now err toward refusing.
2. **Run ids could collide on the first real run.** Allocation read file names,
   and the sample entry is exempt from the naming rule while recording
   `cadence-snapshot-001`. The first real cadence run would have been handed that
   id and failed the ledger's own duplicate check. Allocation now reads recorded
   ids, which are authoritative.
3. **Two of five candidates argue against their own promotion.**
   `contract-drift-check` is already a CI step on every push and is time-invariant
   over committed inputs, so a scheduled run can only differ when nothing
   changed; its write scope is empty, so promoting it would authorize a schedule
   rather than an action. `release-brief-draft` needs `--since` and `--as-of`,
   which are per-run judgments no record binds, and a wrong range yields a brief
   accurate line by line and wrong about the whole.
4. **A shallow clone silently corrupts the cadence report.** Verified rather than
   reasoned: a full checkout reports six distinct pass dates; a `--depth 1` clone
   of the same repository reports one date for all six, with no warning. Both
   workflows now use `fetch-depth: 0`.
5. **The A3 review-point trigger is unevaluable, for two reasons.** The promotion
   record has no `review_point` field, and there is no renewal record of any
   kind. That is a gap against the ladder's own standard.
6. **Eleven of sixteen demotion triggers cannot be evaluated in this
   repository.** Five are; the rest need a Buzz channel record, a packet corpus,
   a human-receipt test, or a record field that does not exist. Each is
   classified with a reason rather than silently skipped.
7. **The scheduled workflow duplicates the guard's governed-path list** as a
   backstop, and nothing checked the two agreed. A cross-contract test now
   asserts no catalogued scope admits a governing file.

## What this does not establish

- **No operation has ever run unattended.** The permitted path has never
  executed against a real promotion. The runner was rehearsed against a simulated
  promotion in a scratch copy; that is a rehearsal, not evidence.
- **No step of the scheduled workflow has run on GitHub.** Actions expression
  syntax, job-to-job outputs, and step summaries are unexercised. Opening a pull
  request will fail until an owner enables *Allow GitHub Actions to create and
  approve pull requests*, which is off by default.
- **The runner is not a sandbox.** It contains writes into a staging copy of the
  repository. Absolute paths, `$HOME`, `/tmp`, and surviving child processes are
  neither stopped nor detected, and a pre-existing symlink pointing out of the
  tree is an escape route it does not close.
- **A correct substrate is not a reason to promote anything.** That judgment
  needs the dossiers, and it stays with a human.
- **Nothing here advances launch.** Every gate and hold that blocked public
  launch before this phase blocks it now.

## Verification

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests` | 787 tests, OK |
| `python3 scripts/validate.py --release --root .` | Validation passed |
| `python3 scripts/validate_artifacts.py --root .` | Passed |
| `python3 skills/evals/validate.py --root .` | Passed for 5 skills |
| `python3 scripts/validate_agents.py --root .` | Passed |
| `python3 scripts/validate_agent_evals.py --root .` | Passed; no run recorded |
| `python3 scripts/triage.py validate ops/triage --root .` | 1 record, 0 violations |
| `python3 scripts/ledger.py validate ops/ledger --root .` | 1 entry, 0 violations |
| `python3 scripts/demotion_check.py --root .` | 16 triggers, 5 evaluable, no trigger fired |
| `make autonomy` | All five operations refused |
| `python3 scripts/check_links.py .` | 347 files, 999 targets, 0 broken, 0 stale |

## What a human decides next

1. **Whether to promote anything at all.** Two of the five dossiers argue
   against themselves. `staleness-sweep` is the only candidate with genuine
   calendar-driven value, and even it duplicates part of the cadence report.
2. **Enabling the repository setting** the scheduled workflow needs, and running
   a `workflow_dispatch` with `dry_run` left at its default before any schedule
   fires.
3. **Adding a `review_point` field and a renewal record**, without which a
   promotion cannot expire and finding 5 stays open.
4. **The Steward's unobservable posting condition**, carried forward from the
   Phase 3 report and still the sharpest open question about any agent here.

## Sources

- [Phase 4 plan](../plans/PHASE4_PLAN.md) — the task inventory and fixed interfaces.
- [Amendment 001](../../community/AMENDMENTS.md) — the governance decision this phase implements.
- [Running Practice on the loop](../../ops/OPERATING_LOOP.md) — the operating procedure, now including the substrate.
- [Autonomy ladder](../../docs/framework/AUTONOMY_LADDER.md) — the levels and the remaining ineligible list.
- Handoffs `X1` through `X6` and `W2` under [`swarm/handoffs/`](../handoffs/).
