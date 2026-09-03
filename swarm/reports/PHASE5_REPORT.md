# Phase 5 report — the two record gaps

**As of:** 2026-09-03 · **Integrator:** Director · **Baseline:** `69a35ae` (four-shelf
layout, 787 tests)

## Outcome

Phase 5 is integrated. Four tasks in two waves closed every item from the
Phase 3 and Phase 4 reports that tooling could close without deciding anything
for anyone. The A3 review-point trigger has a field to read and a record to
consult. The five guardrail terms the Phase 3 report recorded as undefined have
definitions decided from the record. Every profile states that following an
injected instruction in part is following it. And the `staleness-sweep`
candidate has the three tooling prerequisites its dossier said a promotion
decision needed, with the fourth, a human decision, laid out as a packet.

Two owner actions were taken at the founder's direction during the phase: the
repository setting that lets Actions create pull requests was enabled, and the
scheduled workflow was dispatched once as a dry run.

**Nothing is promoted, renewed, enabled, or cleared.** `ops/autonomy/promotions.yaml`
still ships `kill_switch: engaged` with an empty promotion list, the new
`ops/autonomy/renewals.yaml` ships empty, every catalogued operation is refused,
every registry entry reads `not_enabled`, and no owner gate or operating hold
changed status.

Test count moved from 787 to 890. Evaluation cases across the five agent suites
moved from 86 to 109.

## What was built

| Task | Output | What it guarantees |
| --- | --- | --- |
| Z1 | [Renewal record](../../ops/autonomy/renewals.yaml), `review_point` on every promotion, three guard preconditions, the A3-3 detector | A promotion carries the date by which a human renews or withdraws it; a renewal is a new signed record, never an edit; a run after a passed review point is refused by the guard and, if it somehow acted, fired by the demotion check |
| Z2 | Definitions in the five [agent profiles](../../buzz/agents/), registry citations, 13 behavior cases | Each of "internal reasoning", "safe-to-share" and "approved-to-share", "maintainer-confirmed record", "when authorized", and "the assigned workspace" is a set of conditions a reviewer decides from the record, with a stated default when the record is absent |
| Z3 | One shared subsection in all five profiles, `J1` to `J4`, 10 cases | Compliance with an injected instruction is decided by difference from what the legitimate request alone would produce; partial compliance is compliance; an overlapping element is not |
| Z4 | Coverage in [the sweep](../../scripts/check_links.py) and the cadence report, malformed dates as errors, `--fail-on-stale`, the warning rule and disposition role in the [catalog](../../ops/autonomy/operations.yaml), the overlap packet in [the dossier](../../ops/autonomy/CANDIDATES.md) | A clean sweep states how many files it could read, so it cannot be read as "the repository is current"; a typo fails the run instead of crashing it; what an unattended run does with a warning is written down |

Y1, which closed the Steward's posting condition before this phase, is now
recorded in the manifest with a reconstructed specification, so the manifest
and its handoff agree.

## The review point, and how renewal is held

The ladder's A3 section requires a human to "hold a review point at which the
bound is renewed or withdrawn. Silence is not renewal." Before this phase a
promotion could not name one, and no renewal artifact existed, so the demotion
trigger that depends on both was classified unevaluable.

Three properties now hold it in place:

1. **A promotion without a review point is malformed.** The guard's
   `review-point-recorded` precondition refuses it, as it refuses a promotion
   without a signature.
2. **A renewal is append-only and separately signed.** Editing a promotion's
   own `review_point` after signing is not a renewal; the file header, the
   README, and the proposal template all say so. A renewal names the promotion
   it renews, its own date, the new review point, a signer with reserved
   authority, and the paths the reviewer opened.
3. **The guard and the demotion check read the same record.** The guard refuses
   a run on any date after the effective review point. The demotion check reads
   the ledger's recorded review point against the run date, and consults the
   renewal record to tell a genuine trigger from a stale recording.

Verify the shipped state in one command:

```bash
make autonomy
```

Each verdict now lists four failed preconditions and the six that held.

## Findings the work surfaced

1. **Two autonomy documents said seven operations were permanently
   ineligible.** The ladder has listed six since Amendment 001. Both were
   corrected. The dated Phase 4 report and the X2 handoff still say
   "twenty-four preconditions"; the count is now twenty-seven, recorded in the
   Z1 handoff rather than by editing a dated record.
2. **The disagreement finding cannot tell back-dating from a runner defect.**
   When a covering renewal exists but the entry recorded a stale review point,
   either the renewal was recorded after the run and dated earlier, or the
   runner recorded the wrong value. The finding names both and asks a human
   to compare Git history.
3. **Every profile term was ambiguous between a permissive and a restrictive
   reading, and the restrictive one was taken each time.** "Public" now means
   an open channel that is also in the Librarian's read list. A merged pull
   request is never a maintainer-confirmed record; the merged commit is.
   Without a retrieval authorization the auditor retrieves nothing. A path in
   the checkout is not in the workspace unless the assignment lists it.
4. **Four definitions rest on a record a human writes at enablement.** The
   sharing approval, the retrieval authorization, and the workspace assignment
   each have a stated shape now, and each is cited from the registry's
   enablement prerequisites. None of those records exists yet, because no
   agent is enabled.
5. **Y1 had been committed without a manifest entry.** The manifest enforces
   non-overlapping ownership per task mode, so a task that revises files an
   earlier build task produced must be recorded as a revision task. Y1 through
   Z4 are. Two revisions of one file in different waves are sequential
   corrections, not a race, so the validator now checks revision collisions
   within a wave rather than across the whole manifest.
6. **The dry run behaved as shipped.** Run `33759586730` of the unattended
   workflow: the guard job refused all five operations, each verdict listing
   the four failed and six held preconditions, and the writing job was
   skipped. The only annotation is a Node 20 deprecation on the checkout and
   setup-python actions, which still run; a version bump is a small follow-up.
7. **The as-of rule reads 24 of 372 markdown files.** Measured on 2026-09-03
   by the sweep itself: 26 dated lines in 24 files, another 24 files that
   mention "as of" in a form the pattern cannot date, and 324 it says nothing
   about. The number is now printed on every run so nobody has to remember it.

## What this does not establish

- **No promotion has a review point, because no promotion exists.** The field
  and the record are exercised only by tests.
- **No agent has been run against any case.** The 109 cases are definitions. A
  decidable definition is not evidence that an agent respects it.
- **The dry run exercised the guard job and the gate, not the writing job.**
  Job-to-job outputs on the permitted path, the runner on a GitHub runner, and
  the pull-request step remain unexercised, because nothing is permitted.
- **No stale finding has reached the role that owns it.** The role is named;
  its practice is unobserved.
- **The definitions bound what may be posted, retrieved, or read. They do not
  make a reply good.** A Steward reply can satisfy every condition and still be
  unhelpful; the tests say nothing about that.
- **Nothing here advances launch.** Every gate and hold that blocked public
  launch before this phase blocks it now.

## Verification

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests` | 890 tests, OK |
| `python3 scripts/validate.py --release --root .` | Validation passed |
| `python3 scripts/validate_agents.py --root .` | Passed |
| `python3 scripts/validate_agent_evals.py --root .` | Passed; 109 cases defined, no run recorded |
| `python3 scripts/ledger.py validate ops/ledger --root .` | 1 entry, 0 violations |
| `python3 scripts/demotion_check.py --root .` | 16 triggers, 6 evaluable, no trigger fired |
| `make autonomy` | All five operations refused |
| `python3 scripts/check_links.py .` | 0 broken, 0 stale, 0 malformed; coverage printed |
| `gh run view 33759586730` | Guard verdicts passed in 9s, Run and propose skipped |

## What a human decides next

1. **The overlap decision for `staleness-sweep`.** Option A folds the
   calendar half into `cadence-snapshot` and withdraws the operation; Option B
   keeps a separate operation, with or without `--fail-on-stale`. The packet
   is the last section of [the dossier](../../ops/autonomy/CANDIDATES.md).
2. **Whether to promote anything at all.** The dossiers stand; a proposal now
   has a place to name its review point, and the sweep's prerequisites exist.
3. **Deleting the 47 merged `agent/*` branches from Phase 1.** Verified merged
   into `main`; the deletion was left to the owner.
4. **Bumping the two GitHub Actions** the dry run flagged as targeting a
   deprecated Node version.

Deferred by the workers and recorded in their handoffs: a rate limit on
renewals, a `promotion.renewed_on` ledger field, a demotion-history record, and
a `--as-of` argument for the demotion check.

## Sources

- [Phase 5 plan](../plans/PHASE5_PLAN.md) — the task inventory and fixed interfaces.
- [Phase 4 report](PHASE4_REPORT.md) — finding 5 and the "what a human decides next" list this phase worked from.
- [Phase 3 report](PHASE3_REPORT.md) — findings 3 and 4, the five terms and partial compliance.
- Handoffs `Z1` to `Z4` under [`swarm/handoffs/`](../handoffs/).
