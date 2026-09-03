# Phase 5 report — the two record gaps

**As of:** 2026-09-03 · **Integrator:** Director · **Baseline:** `69a35ae` (four-shelf
layout, 787 tests)

## Outcome

Phase 5 is integrated. Two tasks closed the two items from the Phase 4 report
that tooling could close without deciding anything for anyone: the A3
review-point trigger now has a field to read and a record to consult, and the
five guardrail terms the Phase 3 report recorded as undefined now have
definitions decided from the record, each with evaluation cases.

**Nothing is promoted, renewed, enabled, or cleared.** `ops/autonomy/promotions.yaml`
still ships `kill_switch: engaged` with an empty promotion list, the new
`ops/autonomy/renewals.yaml` ships empty, every catalogued operation is refused,
every registry entry reads `not_enabled`, and no owner gate or operating hold
changed status.

Test count moved from 787 to 876. Evaluation cases across the five agent suites
moved from 86 to 99.

## What was built

| Task | Output | What it guarantees |
| --- | --- | --- |
| Z1 | [Renewal record](../../ops/autonomy/renewals.yaml), `review_point` on every promotion, three guard preconditions, the A3-3 detector | A promotion carries the date by which a human renews or withdraws it; a renewal is a new signed record, never an edit; a run after a passed review point is refused by the guard and, if it somehow acted, fired by the demotion check |
| Z2 | Definitions in the five [agent profiles](../../buzz/agents/), registry citations, 13 behavior cases | Each of "internal reasoning", "safe-to-share" and "approved-to-share", "maintainer-confirmed record", "when authorized", and "the assigned workspace" is a set of conditions a reviewer decides from the record, with a stated default when the record is absent |

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
   earlier build task produced must be recorded as a revision task. Y1, Z1,
   and Z2 are.

## What this does not establish

- **No promotion has a review point, because no promotion exists.** The field
  and the record are exercised only by tests.
- **No agent has been run against any case.** The 99 cases are definitions. A
  decidable definition is not evidence that an agent respects it.
- **The definitions bound what may be posted, retrieved, or read. They do not
  make a reply good.** A Steward reply can satisfy every condition and still be
  unhelpful; the tests say nothing about that.
- **Nothing here advances launch.** Every gate and hold that blocked public
  launch before this phase blocks it now.

## Verification

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests` | 876 tests, OK |
| `python3 scripts/validate.py --release --root .` | Validation passed |
| `python3 scripts/validate_agents.py --root .` | Passed |
| `python3 scripts/validate_agent_evals.py --root .` | Passed; 99 cases defined, no run recorded |
| `python3 scripts/ledger.py validate ops/ledger --root .` | 1 entry, 0 violations |
| `python3 scripts/demotion_check.py --root .` | 16 triggers, 6 evaluable, no trigger fired |
| `make autonomy` | All five operations refused |
| `python3 scripts/check_links.py .` | 0 broken, 0 stale |

## What a human decides next

1. **Whether to promote anything at all.** Unchanged from Phase 4. The
   dossiers in [the candidate record](../../ops/autonomy/CANDIDATES.md) stand,
   and a proposal now has a place to name its review point.
2. **Enabling the repository setting** the scheduled workflow needs, and a
   manual dry run before any schedule fires. Unchanged from Phase 4.
3. **Deleting the 47 merged `agent/*` branches from Phase 1.** Verified merged
   into `main`; the deletion was left to the owner.
4. **Phase 3 finding 4**, partial compliance with an injected instruction,
   which all five profiles are still silent on.

Deferred by the workers and recorded in their handoffs: a rate limit on
renewals, a `promotion.renewed_on` ledger field, a demotion-history record, and
a `--as-of` argument for the demotion check.

## Sources

- [Phase 5 plan](../plans/PHASE5_PLAN.md) — the task inventory and fixed interfaces.
- [Phase 4 report](PHASE4_REPORT.md) — finding 5 and the "what a human decides next" list this phase worked from.
- [Phase 3 report](PHASE3_REPORT.md) — finding 3, the five terms.
- Handoffs `Z1` and `Z2` under [`swarm/handoffs/`](../handoffs/).
