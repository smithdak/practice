# Unattended action: the records and the guard that reads them

**As of:** 2026-09-03

## Nothing here is promoted

`promotions.yaml` ships with the kill switch engaged and an empty promotion
list, and `renewals.yaml` ships with nothing renewed. Every catalogued operation
is refused, and the refusal says why:

```bash
python3 scripts/autonomy_guard.py --operation cadence-snapshot --root .
# REFUSED: 'cadence-snapshot' may not run unattended.
#   [kill-switch-released] ops/autonomy/promotions.yaml records 'kill_switch: engaged'. ...
#   [promotion-signed] ops/autonomy/promotions.yaml carries no signed promotion ...
#   [review-point-recorded] ops/autonomy/promotions.yaml records no review point for 'cadence-snapshot', because it records no promotion ...
#   [review-point-not-passed] 'cadence-snapshot' has no effective review point to be on or before ... Silence is not renewal ...
#   preconditions held: catalog-readable, operation-catalogued, ladder-readable, operation-eligible, promotions-readable, renewal-record-readable
# 4 precondition(s) failed.
```

This directory is machinery, not a proposal. A catalogued operation is one whose
bound has been written down, not one anybody has argued should run on its own,
and the guard being correct is not evidence that any operation should be
promoted. That judgment is a human decision made against the dossiers, and this
repository has made none.

## The problem

[The autonomy ladder](../../docs/framework/AUTONOMY_LADDER.md) defines A3,
act-unattended-within-bounds, and names the observable triggers that demote an
operation out of it. It had nowhere to record such a decision, nothing that
described which operations were even candidates, and nothing that checked, before
an operation acted, whether it had been permitted. Without a check that refuses
by default, "unattended within bounds" has no bounds.

## The records

| File | What it is | What it can do alone |
|---|---|---|
| `operations.yaml` | The catalog: every operation that could one day run unattended, with its command, write scope, reversal, blast radius, and current level. | Nothing. A catalog entry may not declare A3, so editing this file cannot promote anything. |
| `promotions.yaml` | The governance record: the kill switch, and the promotions a human has signed, each with the review point at which its bound is renewed or withdrawn. | Nothing on its own either. A promotion with the switch engaged is refused, and a released switch with no promotion is refused. |
| `renewals.yaml` | The renewal record: one entry per decision to keep a promotion past its review point, naming the promotion, the renewal date, the next review point, the signing role, and what was reviewed. | Nothing. A renewal extends only a promotion that exists, and it cannot release the switch. A renewal is a new entry here, never an edit to the promotion's own `review_point`. |

Two records must change before anything runs, because a single record can be
changed by a single edit. Both must change in the same reviewed decision — and
the kill switch is deliberately the cheaper half to reverse: setting it back to
`engaged` is one word and stops every operation at once, without touching a
promotion, a renewal, a catalog entry, or any code.

The third record exists because a promotion expires. The ladder requires a
review point at which a human renews the bound or withdraws it, and says silence
is not renewal. The guard refuses a run dated after the effective review point:
the promotion's own `review_point`, or the `review_point` of the latest renewal
for that promotion whose `renewed_on` is on or before the date being checked.
Editing a promotion's `review_point` after signing is not a renewal — it
rewrites the decision instead of recording a new one, and leaves no trace of the
review the ladder requires.

A `write_scope` is the only set of paths an operation may create or change. Globs
are matched with `fnmatch` against the repository-relative path, where `*` is not
special about `/`, so keep each one rooted in a directory that holds only
generated files. An empty list means the operation writes nothing; two of the five
catalogued operations are checks, and their value unattended is the report and the
ledger entry, not a file.

## What the guard checks

`scripts/autonomy_guard.py --operation <id> --root .` exits **0** permitted,
**1** refused, **2** usage error. Refusal is the default: it permits only when
every precondition below holds, and each refusal line names the one that failed
so the message points at a file and a field rather than at a mood.

| Precondition | Holds when |
|---|---|
| `catalog-readable` | `operations.yaml` exists, parses, and is a mapping. |
| `catalog-schema` | Its `schema_version` is one the guard reads, its top-level fields are known, and its `sources` resolve. |
| `catalog-entry` | Every entry has the required fields, a slug id, no unknown field, and no duplicate id. |
| `catalog-command` | The command is an argv list starting `python3`, naming a script that exists, with no shell metacharacter. |
| `catalog-write-scope` | Every glob is repository-relative, names a directory, and reaches no governance record, script, test, or workflow. |
| `catalog-level` | No catalog entry declares A3. The catalog records where an operation is, never where it may go. |
| `operation-catalogued` | The requested id has a catalog entry. |
| `ladder-readable` | The ladder's permanently ineligible section is present and lists operation ids. |
| `ladder-agreement` | The ladder still lists every operation the guard knows to be permanently ineligible. |
| `operation-eligible` | Neither the requested operation nor any promoted one is on that list. |
| `promotions-readable` | `promotions.yaml` exists, parses, and is a mapping. |
| `promotions-schema` | Known top-level fields, a supported `schema_version`, and a `kill_switch` value the guard recognizes. |
| `promotions-record` | Every promotion entry is a mapping with exactly the required fields, naming a catalogued operation. |
| `kill-switch-released` | `kill_switch` is `released`. |
| `promotion-signed` | A promotion for this operation exists. |
| `promotion-unique` | Exactly one promotion names it. |
| `promotion-level` | That promotion records `level: A3`. |
| `promotion-write-scope` | Its write scope is valid and equals the catalog entry's, exactly. |
| `promotion-evidence` | It names at least one evidence path, and every path exists. |
| `promotion-demotion-triggers` | It names the observable conditions that end it. |
| `signature-present` | It carries both `signed_by` and `signed_on`. |
| `signature-role` | `signed_by` is a controlled operating role, not a person, handle, or address. |
| `signature-authority` | That role is `founder`, `beta-owner`, or `continuity-owner`, the roles holding reserved decisions. |
| `signature-date` | `signed_on` is a real ISO date that is not in the future. |
| `review-point-recorded` | The promotion records a `review_point` that is a real ISO date strictly after `signed_on`. With no promotion for the operation there is no review point, and this fails rather than going unevaluated. |
| `renewal-record-readable` | `renewals.yaml` exists, parses to a mapping with exactly `schema_version` and `renewals`, and every entry is well-formed: exactly the six fields, naming a promotion that exists by `operation` and `promotion_signed_on`, a `renewed_on` that is not in the future and not before that promotion's `signed_on`, a `review_point` strictly after `renewed_on`, a `signed_by` holding reserved authority, and a non-empty `reviewed` list of repository paths that exist. Any defect, in any entry, refuses every operation. |
| `review-point-not-passed` | The date being checked is on or before the effective review point: the promotion's own, or the `review_point` of the latest renewal for that promotion whose `renewed_on` is on or before that date. A renewal dated later does not count on that date. The refusal says that silence is not renewal. |

Missing or malformed input refuses. An unreadable record, an unexpected schema
version, a ladder whose ineligible list has shrunk, a write scope that reaches
the records deciding whether the operation may run, a renewal that names no
promotion — each is a refusal, never a pass. The guard reads files only: it
writes nothing, runs no operation's command, records no signature, and never
asserts that an owner gate or an operating hold is cleared.

Two consequences are worth stating directly. An operation may never be given a
write scope covering `ops/autonomy/`, the ladder, the guard, the scheduled
workflow, or another governance record, because an operation that can widen its
own bound has no bound. And the six operations the ladder marks permanently
ineligible stay refused whatever a promotion says; changing that list is a
governance amendment to [locked decisions](../../docs/DECISIONS.md) and
[non-goals](../../docs/NON_GOALS.md), not a tooling change.

## How a promotion would be made

The steps a human would follow, recorded here so a future proposal is measured
against a written standard rather than one invented when it is wanted. None of
these steps has been taken.

1. **Read the dossier.** `ops/autonomy/CANDIDATES.md` states, per operation, the
   write scope, the reversal, the blast radius, and the evidence that does and
   does not exist. An operation whose evidence does not exist is not ready to be
   argued about.
2. **Write the proposal.** `ops/autonomy/PROMOTION_PROPOSAL.md` is the form the
   decision takes: the bound, the rate and scope limit, the reversal a human can
   execute without the agent, the human role that owns the bound, and the review
   point at which it is renewed or withdrawn. Silence is not renewal.
3. **Decide through the reserved-decision path.** Promotion is a reserved
   decision in [the governance model](../../community/GOVERNANCE.md): a founder
   decision recorded with rationale and effective date. No agent, runner, or
   validator may make it, and a run of good outputs is not a promotion.
4. **Record the entry** in `promotions.yaml` with the operation, `level: A3`, the
   catalog's exact write scope, evidence paths that resolve, the demotion
   triggers, the signing role, the date, and the `review_point` — an ISO date
   strictly after `signed_on` by which the bound is renewed or withdrawn. The
   guard refuses a run dated after it.
5. **Release the kill switch** in the same decision, knowing that this is the
   edit that makes the machinery live.
6. **Expect the demotion triggers to fire.** They are automatic and need no
   decision; the decision that follows one is whether to restore the level.
7. **Hold the review point.** Before it passes, a human either withdraws the
   promotion (step 1 of the reversal below) or renews it by adding an entry to
   `renewals.yaml`: the operation and the promotion's `signed_on`, the date of
   the renewal, the next review point, the signing role, and the paths that
   were reviewed — the ledger entries, the merged and closed pull requests, and
   the evidence gaps from the proposal. A renewal is a new entry, never an edit
   to the promotion. Silence is not renewal: once the review point passes with
   no renewal recorded, the guard refuses the operation, and
   `scripts/demotion_check.py` reports any run that acted after it.

## How to reverse it

In the order a person would use it under pressure:

1. **Set `kill_switch: engaged`.** One edit. Every operation is refused again
   immediately, and nothing else has to be true for that to hold.
2. **Delete the promotion entry.** The operation returns to its catalogued
   attended level. Delete any renewal entry naming that promotion in the same
   change: a renewal of a promotion that no longer exists refuses every
   operation until it is removed.
3. **Reverse the run itself** using the `reversal` line the catalog records for
   that operation — deleting a written file, or closing the pull request
   unmerged. Unattended runs arrive as reviewable pull requests rather than
   pushes, so the usual reversal is closing one.

Letting a review point pass is also a reversal, and the slowest one: the guard
refuses from the day after the effective review point without anyone editing a
file. It is not the one to reach for under pressure.

## Failure modes worth naming

- **A catalog entry read as a recommendation.** The catalog describes bounds for
  operations that are not promoted. Adding one proposes nothing.
- **A bound widened quietly.** Changing a write scope in one record and not the
  other is refused, by design: `promotion-write-scope` compares them and names
  both files.
- **A signature from a role that does not hold the decision.** A maintainer is a
  controlled role and still may not sign a promotion; the guard separates
  `signature-role` from `signature-authority` so the message says which failed.
- **A guard that never refuses.** A check that always says no passes every
  negative test. `tests/test_autonomy_guard.py` therefore builds one fully signed
  fixture and requires exit 0, so the refusals mean something. The same file
  builds one renewed fixture and checks it inside the renewed window, so a
  renewal that could never extend anything would fail too.
- **A review point moved by hand.** Changing a promotion's `review_point` after
  signing looks like a renewal to the guard and is not one: no date, no signing
  role, and nothing reviewed. The record of what was reviewed lives only in
  `renewals.yaml`, and a reviewer comparing Git history for `promotions.yaml`
  should treat a changed `review_point` as a withdrawn promotion re-signed
  without a proposal.
- **Machinery mistaken for readiness.** Nothing in this directory clears an owner
  gate or an operating hold, and none of it is evidence that an operation should
  run without a person.

## Sources

- [Autonomy ladder](../../docs/framework/AUTONOMY_LADDER.md) — the levels, the
  evidence each requires, the demotion triggers, and the operations permanently
  ineligible for A3.
- [Governance model](../../community/GOVERNANCE.md) — the reserved-decision path
  a promotion is made through.
- [Running Practice on the loop](../OPERATING_LOOP.md) — what runs without
  a person today and what requires one.
- [Private beta operating kit](../BETA_OPS.md) — the operating roles a signature
  must name.
- [Owner review packet](../../release/OWNER_REVIEW.md) — the gates and holds this
  machinery does not move.
