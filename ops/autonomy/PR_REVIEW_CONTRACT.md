# Reviewing a pull request opened by an unattended run

**As of:** 2026-09-02

## No such pull request can exist today

`promotions.yaml` ships with the kill switch engaged and an empty promotion list,
so [the guard](../../scripts/autonomy_guard.py) refuses every catalogued
operation and [the scheduled workflow](../../.github/workflows/unattended.yml)
stops after saying which ones it refused. Nothing has run unattended in this
repository, and nothing can until a human signs a promotion and separately
releases the switch.

This document exists so that the first such pull request is read against a
standard written before anyone wanted it approved. If one appears while
`promotions.yaml` still reads `kill_switch: engaged` with `promotions: []`, that
is not a pull request to review. It is a security finding: close it, and treat
the question of how it was opened as the incident.

## What you are agreeing to when you merge

**You are accepting the content, not the process.** The workflow, the guard, and
the runner establish that a machine was permitted to propose this change and
stayed inside a recorded bound while producing it. None of that is a claim that
the change is correct, useful, or true. Merging says a named human read what the
run produced and is willing to have it in the repository under their name.

The distinction matters because everything upstream of the pull request is
mechanical, and mechanical checks are exactly the ones that pass while a file
says something wrong. A cadence report can be inside its write scope, validated,
recorded, reversible, and still describe the wrong week.

Three things you are specifically not agreeing to:

- **Not that the operation should keep running.** Merging one pull request is not
  a renewal of the promotion. The promotion's own review point, recorded in
  `promotions.yaml`, is where that decision is made.
- **Not that the substrate is working.** A run that produced a clean diff is not
  evidence about the ninety-nine cases that did not occur.
- **Not that anything in the diff is evidence for a maturity or gate change.** No
  unattended run may change a `maturity` or `evidence_quality` field, close an
  owner gate, or clear an operating hold, and merging one cannot do it either.

## What a machine already checked, so you need not

Do not re-derive any of this by hand. It is checked before the pull request
exists, and the ledger entry in the pull request body records each result.

| Already checked | By what | Where you can see it |
|---|---|---|
| A human signed a promotion for this operation at A3, and the kill switch was released | `scripts/autonomy_guard.py` | The `preconditions` list in the ledger entry, and `kill_switch` and `promotion` in its front matter |
| The operation is not on the permanently ineligible list | `scripts/autonomy_guard.py` | The `operation-eligible` precondition |
| The promotion's write scope equals the catalog entry's, and its evidence paths exist | `scripts/autonomy_guard.py` | The `promotion-write-scope` and `promotion-evidence` preconditions |
| The signature names a real operating role and is not dated in the future | `scripts/autonomy_guard.py` | The `signature-role`, `signature-authority`, and `signature-date` preconditions |
| Every path the command created or changed is inside the declared write scope | `scripts/run_unattended.py`, which executes in a staging copy and applies nothing from a run that left its bound | The `write-scope-enforced` precondition, and `paths_written` |
| Nothing was deleted, and no symlink was changed | `scripts/run_unattended.py` | The same precondition; a violation records the run as `failed` and applies nothing |
| The run changed no file that governs its own bounds | The workflow's self-modification backstop, per [amendment 001](../../community/AMENDMENTS.md) | The workflow log; the step fails and no pull request is opened |
| The ledger entry is complete and internally consistent | `scripts/ledger.py` | The entry itself, and `python3 scripts/ledger.py validate ops/ledger --root .` |

A valid ledger entry is a complete record, never a permission. An entry
describing a run that should not have happened is a *valid entry* and a serious
finding.

## What to check, in order

Five minutes, in this order. Stop at the first one that fails and close the pull
request.

1. **The promotion is still the one you think it is.** Open `promotions.yaml` at
   the base branch. Does it carry a signed promotion for every operation named in
   the pull request body, at A3, with the switch released? If a promotion was
   withdrawn or the switch was re-engaged after the run started, the run is
   stale — close it.
2. **The diff is only what the write scope allows, plus one ledger entry per
   run.** Read the file list, not the summary. Every path must match the
   operation's `write_scope` in `operations.yaml`, except entries under
   `ops/ledger/`, which the runner writes and no operation may.
3. **The content is right.** This is the part only you can do. Open the produced
   file and check it against the thing it claims to describe: does the dated
   status file describe the week it names, does the metrics snapshot's count
   match what you can count, does the drafted brief describe work that was
   actually merged. A number with no source in the repository is a defect
   whatever the ledger says.
4. **The ledger entry matches the diff.** `paths_written` should list exactly the
   non-ledger files in the diff. A disagreement between the record and the diff
   is more serious than either being wrong on its own, because it means the
   record cannot be trusted for the runs nobody reviewed.
5. **The reversal in the body works.** Read it. If you cannot say what you would
   type to undo this after merging, do not merge it.

If all five hold, merge it the way you would merge a contributor's pull request,
and let the branch be deleted. If any fail, use the next section.

## Closeable without discussion

Close these immediately. Say which rule applied, and nothing else is owed —
these are machine output, and a closed pull request costs nobody an explanation.

- **Nothing is promoted for the operation it names.** Including the shipped state
  of this repository. See the first section.
- **The diff touches a path outside the operation's write scope**, other than the
  run's own ledger entry.
- **The diff touches any file that governs the run's bounds** — anything under
  `.github/`, `ops/autonomy/`, `scripts/`, `tests/`, `docs/framework/`,
  `docs/schemas/`, or the locked decision records. Amendment 001 makes this
  exclusion non-waivable, so no promotion can authorize it.
- **The pull request carries no ledger entry**, or carries one that
  `scripts/ledger.py validate` rejects.
- **A second pull request proposes the same run.** Keep the earlier one, close
  the later.
- **The content is wrong and the fix is not obvious.** Close it rather than
  editing it. The next scheduled run reproduces the work; a human-edited machine
  pull request is neither a machine record nor a human change, and the ledger
  entry stops describing what was merged.
- **You are not the person who owns the promotion's bound and no owner is
  available.** Closing loses nothing: the operation runs again on the schedule.

Closing is a complete reversal. Nothing outside the branch changed, so a closed
pull request leaves the repository exactly as the run found it.

## A pull request nobody reviewed

**Rule: an unattended pull request that is still open when the next scheduled run
fires is closed unreviewed, by whoever notices first.** No discussion, no
apology, no attempt to catch up.

Two failures this prevents. A queue of stale machine pull requests trains people
to merge without reading, which removes the only human step in the design. And an
old proposal describes a repository that has since changed, so approving it later
approves something nobody checked.

There is one escalation, and it is not "review it faster". If unattended pull
requests are closing unreviewed for two consecutive cycles, the operation is
producing work nobody wants at a rate nobody can absorb. Re-engage the kill
switch or withdraw the promotion, and record why. That is a normal outcome of
this design, not a failure of it: the demotion triggers in
[the autonomy ladder](../../docs/framework/AUTONOMY_LADDER.md) exist so that an
operation can be pulled back without an argument about whether it deserved to be.

## What this contract does not cover

- **Merging by machine.** Nothing merges these pull requests except a person.
  Amendment 001 made bounded merge *eligible* for A3, which is not promoted, not
  catalogued, and not enabled; the workflow implements no auto-merge, and adding
  one is a governance decision rather than a workflow change.
- **Pull requests opened by people.** They are reviewed under
  [the maintainer runbook](../MAINTAINER_RUNBOOK.md). This contract applies only
  to a pull request whose body says it was opened by
  `.github/workflows/unattended.yml`, and the body is not proof — check the
  branch's author and the workflow run it names.
- **Whether an operation should have been promoted at all.** That case is argued
  in [the candidate dossiers](CANDIDATES.md) and decided on
  [the promotion proposal](PROMOTION_PROPOSAL.md), before any pull request
  exists.

## Sources

- [The scheduled workflow](../../.github/workflows/unattended.yml) — what opens
  the pull request, and what it refuses to open.
- [Unattended action: the two records and the guard](README.md) — the catalog,
  the promotion record, and why there are two.
- [Action ledger schema](../../docs/schemas/ACTION_LEDGER_SCHEMA.md) — the fields
  in the entry carried by the pull request body.
- [Autonomy ladder](../../docs/framework/AUTONOMY_LADDER.md) — A3, its evidence
  requirement, and the demotion triggers.
- [Governance amendments](../../community/AMENDMENTS.md) — amendment 001, bounded
  merge eligibility, and the self-modification exclusion.
- [Maintainer operating runbook](../MAINTAINER_RUNBOOK.md) — how a
  human-authored pull request is reviewed.
