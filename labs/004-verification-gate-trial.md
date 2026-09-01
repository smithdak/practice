---
artifact_type: lab
title: "Trial the agent-output verification gate on a code commit with a rollback rehearsal"
summary: "Apply Practice 003 end to end to one real committed code change (the A2 link checker at commit 421ed6e) and rehearse its rollback, recording every check result, edge-case finding, and failure mode observed."
status: completed
primary_capability: use
roles: [individual-practitioner, engineer, operator]
task_set_version: 0.1.0
run_count: 2
result_status: complete
last_run: 2026-09-01
version: 0.1.0
license: CC-BY-4.0
created: 2026-09-01
updated: 2026-09-01
---

# Trial the agent-output verification gate on a code commit with a rollback rehearsal

This Lab records the first executed trial of [Practice 003](../practices/003-verification-gate.md), "Verify an agent's output before accepting or shipping it", run inside this repository's own work per the Phase 2 plan: the gate is applied to a real worker commit, and the rollback the Practice requires is rehearsed against that commit. The gate reviewer (task E3) did not produce the gated artifact; it was produced by task A2 (see [handoffs/A2.md](../handoffs/A2.md)). The trial covers one artifact of one type; it does not establish general effectiveness of the method.

## Question

Under the fixed conditions below, can the Practice 003 gate be executed end to end by one agent reviewer on one real, already-committed code change, producing a record another reviewer could reproduce from commands and outputs alone — and does the gate's rollback procedure revert that change cleanly on this repository?

## Hypothesis

Predeclared before execution:

- H1 (gate): every mandatory artifact-scoped check in the gate record passes for commit `421ed6e`, so the record supports a recommendation of `accept` with human approval still pending.
- H2 (rollback): `git revert --no-commit 421ed6e` applies with zero conflicts, and `git revert --abort` restores a clean tree at an unchanged HEAD.

Decision thresholds: H1 fails if any mandatory check fails or is unresolvable unknown; H2 fails on any conflict, any surviving tree mutation, or any change to HEAD. These were expectations before the run, not results.

## Variables

| Type | Definition | Measurement |
|---|---|---|
| Independent variable | None manipulated. This is a single-condition trial: the gate method applied to one fixed artifact (commit `421ed6e`). Two runs: R1 gate trial, R2 rollback rehearsal. | Recorded in the run ledger. |
| Primary outcome (R1) | Gate outcome: whether all mandatory checks pass and the record supports `accept` with approval pending. | Per-check `pass`/`fail`/`unknown` with command, expected, and observed output. No aggregate score. |
| Primary outcome (R2) | Rollback cleanliness. | Staged change set, conflict count, `git status --short` emptiness, and HEAD hash before and after. |
| Secondary outcome | Checker contract-limit findings from boundary fixtures. | Count and class of false-pass and false-positive behaviors demonstrated. |
| Uncontrolled confounders | One operator-agent framed the gate, ran the checks, and wrote this record; no independent reproducer has re-executed anything. The repository moved between artifact production (commit `421ed6e`, 2026-09-01 11:56:59 -0500) and trial. Parallel Wave E/G tasks land files continuously, so repo-wide file and link counts drift after this trial. | Stated here; not eliminated or compensated. |

## Fixed conditions

- Repository: this repository at HEAD `6f205d65453c7699016abc2f4d18e5db31002544`, worktree clean at trial start (verified with `git status --short` before both runs).
- Gated artifact: commit `421ed6ea3812bb82f15c1691e98a4e814be7cb8c` ("task(A2): add link and as-of date checker").
- Tooling: Python 3.12.3, standard library only; every check runs offline; no network access is used or required.
- Execution date: 2026-09-01.
- Commands exactly as listed in Procedure; no check was retried.
- Boundary fixtures are built only under `/tmp/opencode/e3-edge`, outside the repository, and deleted after recording; nothing in the gated tree is modified by this Lab.
- All git mutations are limited to the rollback rehearsal pattern: `git revert --no-commit` followed by `git revert --abort`.

## Task set

The trial has two packets.

### Packet 1 — gate trial on commit 421ed6e

Artifact under gate: `scripts/check_links.py` (186 lines) and `tests/test_check_links.py` (350 lines) as committed in `421ed6e`, produced by task A2. Gate record, using the Practice's minimal review packet:

```text
gate record: E3-2026-09-01-A2-LINKCHECKER
artifact: scripts/check_links.py + tests/test_check_links.py (type: code/automation)
version: commit 421ed6ea3812bb82f15c1691e98a4e814be7cb8c
intended effect: acceptance of the checker as a repository validator; CI runs it
  on every pull request (.github/workflows/ci.yml)
owner: A2 worker (producer); repository maintainer (accountable human)
reviewer: E3 worker agent — assembles evidence and recommends only; no human
  approval is obtained in this trial
impact: material (CI gate: false positives block pull requests; false negatives
  let broken links merge)
criteria (mandatory):
  M1 unit tests pass
  M2 checker runs repo-wide with exit 0
  M3 complete diff reviewed
  M4 scope discipline (only A2-owned paths plus its own handoff)
  M5 scripts/validate_artifacts.py passes
  M6 rollback rehearsed
criteria (advisory):
  A1 scripts/validate.py --root . passes, or any failure is attributed outside
     the gated paths
  A2 boundary/adversarial fixtures run and findings recorded
out of scope: heading-anchor correctness, reference-style usage completeness,
  filenames containing parentheses or literal %-sequences — the checker's
  documented contract is file existence for inline links and reference
  definitions
baseline/diff: git show 421ed6e at HEAD 6f205d65; starting tree clean
sources: handoffs/A2.md (producer record); SWARM_PHASE2_PLAN.md Wave A row
  (task definition and owned paths)
rollback: git revert --no-commit 421ed6e, then git revert --abort (rehearsal);
  recovery owner: repository maintainer
decision: recorded in Results
approval: null — human review pending
release/monitoring: destination = this branch; signal = CI link-check step;
  stop trigger = broken-link report or validator failure in CI
```

Expected packet conditions: every mandatory check is observable as a command with an exit code; scope discipline is verifiable from git alone; the decision follows the Practice rule — any failed or unknown mandatory check forces `revise` or `reject`, and the agent never self-approves.

### Packet 2 — rollback rehearsal

Predeclared protocol:

1. Confirm `git status --short` is empty and record HEAD.
2. Run `git revert --no-commit 421ed6e`.
3. Inspect the staged change set; identify conflicts and any downstream breakage the revert would cause if committed.
4. Run `git revert --abort`.
5. Verify `git status --short` is empty and HEAD is unchanged.

If any step fails: abort immediately and record the incident as the outcome.

## Procedure

1. Read the Practice, the gated files, and the producer handoff; frame the gate record above before running any check.
2. Preserve the starting point: confirm a clean tree and record HEAD. The committed history is the baseline; the gate must not mutate it.
3. Run M1, M2, M5, and A1 in that order; capture full outputs and exit codes. All checks are deterministic and offline, so no rerun rule is needed.
4. Perform M3: read `scripts/check_links.py` and `tests/test_check_links.py` in full; inspect `git show 421ed6e --stat`; verify with `git log 421ed6e..HEAD` that no later commit touched the three paths; sweep the repository for references to the tool outside its owned paths.
5. Perform M4 from the stat in step 4: the commit must touch only `scripts/check_links.py`, `tests/test_check_links.py`, and `handoffs/A2.md` (A2's owned paths plus its own handoff).
6. Build the boundary fixtures under `/tmp/opencode/e3-edge` (advisory A2) and run the checker against the fixture root with `--as-of 2026-09-01`; record output and exit code; delete the fixture.
7. Execute the Packet 2 rollback rehearsal after all read-only checks; record staged state, conflicts, and recovery.
8. Decide: apply the Practice's decision rule to the check table; record the decision, approval state, and any observed failure modes in Results.

## Evaluation rubric

Each check is binary: `pass` (observed output matches expected, exit code as stated), `fail` (mismatch), or `unknown` (check not executable). No partial credit and no aggregate score; the completed record is the outcome. The gate decision rule, taken from the Practice: `accept` is recommended only when all mandatory checks pass and rollback is rehearsed; a failed or unknown mandatory check forces `revise` or `reject`; the agent never self-approves, so `approval` remains null. The rollback rehearsal passes only if the staged change set is exactly the inverse of the gated commit, conflicts are zero, the tree is clean after abort, and HEAD is byte-identical before and after. Critical error (forces `reject` in the record): any tree mutation surviving the rehearsal, or a mandatory check left unexplained.

## Cost capture

No billable usage was incurred or observable: every check ran offline with Python 3.12.3 standard-library tooling. Pricing source: not applicable — no provider request was made. Excluded costs: agent labor for the E3 session (not metered or accessible to this agent), maintainer review labor, and local compute. Formula: none.

## Results

Result status: complete. Two runs, both included; none excluded. Wall-clock timestamps were not captured per command; execution order follows Procedure.

### Run ledger

| Run ID | Packet | Date (UTC) | Evidence reference | Outcome | Cost | Excluded |
|---|---|---|---|---|---|---|
| R1 | Gate trial | 2026-09-01 | Check table below; commit `421ed6e` at HEAD `6f205d65` | All 6 mandatory and 2 advisory checks pass; recommend `accept`, approval null | none billable | no |
| R2 | Rollback rehearsal | 2026-09-01 | Rehearsal table below; HEAD `6f205d65` before and after | Clean: 0 conflicts, tree restored, HEAD unchanged | none billable | no |

### Run 1 — check results

| # | Check | Command | Expected | Observed (2026-09-01) | Status |
|---|---|---|---|---|---|
| M1 | Unit tests | `python3 -m unittest tests.test_check_links -v` | exit 0, all tests OK | `Ran 34 tests in 0.028s` / `OK`, exit 0 | pass |
| M2 | Checker repo-wide | `python3 scripts/check_links.py` | exit 0, zero broken links | `Checked 230 markdown file(s), 340 link target(s): 0 broken link(s), 0 stale as-of date(s).`, exit 0 | pass |
| M3 | Complete diff review | `git show 421ed6e`; both files read in full | change matches the producer handoff; no secrets, no network, no scope creep | 3 files, 634 insertions; standard library only; no subprocess or network calls; tests use tempfile fixtures with a pinned as-of date of 2026-09-01 | pass |
| M4 | Scope discipline | `git show 421ed6e --stat`; `git log 421ed6e..HEAD -- <paths>` | only the three owned paths, untouched since | exactly `handoffs/A2.md` (+98), `scripts/check_links.py` (+186), `tests/test_check_links.py` (+350); the later-commit log over these paths is empty | pass |
| M5 | Artifact validator | `python3 scripts/validate_artifacts.py` | exit 0 | `Artifact validation passed (1 guide, 6 guide modules, 1 lab, 3 practices, 1 story).`, exit 0 | pass |
| M6 | Rollback rehearsed | Run 2 below | clean revert and restore | clean (see Run 2) | pass |
| A1 | Repo validator (advisory) | `python3 scripts/validate.py --root .` | exit 0, or failures attributed outside the gated paths | `Validation passed.`, exit 0 | pass |
| A2-check | Boundary fixtures (advisory) | checker run on `/tmp/opencode/e3-edge` | actual behavior recorded | 1 false-positive class and 3 false-pass classes (below) | pass, findings recorded |

Note on A1: the producer handoffs ([handoffs/A1.md](../handoffs/A1.md), [handoffs/A2.md](../handoffs/A2.md)) recorded `scripts/validate.py --root .` failing on a false positive in `handoffs/R2.md`. As of this trial it passes; the earlier failure no longer reproduces as of this run; the cause and the fix are unverified.

### Boundary fixture findings — what the gate does NOT prove

Fixture: `/tmp/opencode/e3-edge` containing `a.md` with four probe links plus supporting files; command `python3 scripts/check_links.py /tmp/opencode/e3-edge --as-of 2026-09-01`. Observed summary: `Checked 4 markdown file(s), 3 link target(s): 1 broken link(s).`, exit 1.

Probes are written here as link text and target separately; in the fixture each pair was composed in the usual bracket-parenthesis form. (They are not joined in this document because `scripts/validate.py` scans raw text with no code masking and would read the examples as real links — see the frictions note below.)

| Probe | Link text / target | Reality | Checker behavior |
|---|---|---|---|
| Anchor | `[bad anchor]` / `target.md#no-such-heading` | anchor does not exist in `target.md` | passes silently; anchors are stripped and never validated |
| Reference usage | `[use][nolabel]`, no `[nolabel]:` definition anywhere | renders broken in most viewers | ignored entirely; not counted as a link target |
| Parentheses | `[x]` / `weird(1).md`, file exists | valid target | false broken: `a.md:7: broken relative link: weird(1` — the target is truncated at the first `)` |
| Directory target | `[dir link]` / `sub`, a directory | not a page target | passes the existence check |

Recording frictions, observed while writing this record: `scripts/validate.py` flagged the Lab's own backticked fixture examples as three broken relative links because it scans raw text and masks neither code fences nor inline code spans — the same false-positive class the producer handoff predicted for it. The gated checker handled the identical document correctly (0 broken links). The probes were reworded to break the bracket-parenthesis adjacency rather than modify any validator; the incident is evidence for the masking decision recorded in [handoffs/A2.md](../handoffs/A2.md).

Consequences for the gate: a checker pass proves link targets exist as files; it does not prove anchors resolve, reference usages have definitions, or that a target with literal parentheses is judged correctly. The parenthesized-target class is a false positive inside the tool's own contract — in CI it would block a pull request containing a valid file named like `weird(1).md`. Severity today: latent. No filename in the repository contains parentheses (verified with `git ls-files` on 2026-09-01), and reference-style usages currently have definitions where used.

### Run 2 — rollback rehearsal

Pre-state: `git status --short` empty; HEAD before `6f205d65453c7699016abc2f4d18e5db31002544`.

| Step | Command | Observed |
|---|---|---|
| Revert | `git revert --no-commit 421ed6e` | exit 0; no conflicts; staged exactly `D handoffs/A2.md`, `D scripts/check_links.py`, `D tests/test_check_links.py`; `git diff --cached --stat`: 3 files changed, 634 deletions(-) |
| Inspect | `git status --short`; `git diff --cached --stat` | staged deletions only, as above |
| Abort | `git revert --abort` | exit 0 |
| Verify | `git status --short`; `git rev-parse HEAD` | tree empty; HEAD after `6f205d65453c7699016abc2f4d18e5db31002544`, identical to before |

What reverted cleanly: the entire commit. All three files were added in `421ed6e` and never modified by a later commit, so the inverse patch applied with zero conflicts.

What would need manual attention if the revert were actually committed:

- CI breaks: `.github/workflows/ci.yml` runs `python3 scripts/check_links.py`, which the revert deletes. A4 wired CI to this tool, so a tool revert requires a matching CI revert in the same change.
- Stale prose references to the tool remain in `handoffs/A4.md`, `handoffs/R3.md`, and `SWARM_PHASE2_PLAN.md`.
- Confirmed non-issues: no other test module imports the deleted test file, so unittest discovery would still pass; nothing else links to `handoffs/A2.md`.

Recovery commands, exact: while the sequence is open, `git revert --abort`; if a revert had been committed, `git revert HEAD` of the revert commit, or `git reset --hard 6f205d65453c7699016abc2f4d18e5db31002544` before any push. Recovery owner: repository maintainer.

### Gate decision

- decision: `accept` (recommended) — all six mandatory checks pass and rollback is rehearsed.
- approval: null — no human has approved this artifact through this gate, and the E3 agent cannot self-approve.
- Observed failure mode, recorded against the trial itself: late approval. Commit `421ed6e` was already on the branch when this gate ran, because the swarm's flow merges worker commits before the gate task executes. The gate therefore documented the artifact and rehearsed recovery; it could not prevent the effect. The Practice lists late approval as a failure mode, and this trial's own process exhibited it.

## Interpretation

Observed: on this artifact, repository state, and date, the Practice 003 gate was executable end to end by one agent reviewer. Every check produced reproducible command evidence, the record separates mandatory from advisory checks, and the two-command rollback rehearsal restored the exact baseline with zero conflicts. The checker passed every mandatory check for its intended use, and the boundary fixtures converted four unstated tool limitations into explicit, recorded non-guarantees of the gate.

Bounded inference: the method is workable as written for code-change acceptance in this repository, and its rollback requirement is satisfiable cheaply when the gated commit's files are untouched after creation. This inference covers one code artifact at one commit; it does not cover the Practice's other artifact types.

Non-result: nothing here shows the gate improves defect detection, review speed, or cost, and no such claim is made; the Practice forbids effectiveness inference without a measurement plan.

Against the Practice's own trial bar: not fully met. The Practice's Evaluation section requires trials on artifacts of at least two different types and an intentional unsupported claim or failing test that forces the gate to refuse `accept`. This trial covers one artifact type (code) and never exercised the refusal path: no mandatory check failed, and the fixture failure was advisory and outside the gated artifact. The preserve-the-baseline requirement was exercised (Run 2). Practice 003 therefore remains `maturity: proposed`; the remaining trial evidence (second artifact type, refusal path) is listed under Limitations and deferred for a later trial.

## Limitations

- Single artifact, single type (code), single commit. No research brief, configuration, or operational action was gated, so cross-type claims about the method are unsupported.
- Single operator-agent: the same agent framed the gate, ran the checks, and wrote this record. No independent reproducer has re-executed the commands; the record is built so one could, but none has.
- Approval is null: no human reviewed this trial before it was recorded, so the accountable-human step of the Practice remains untested in this repository.
- The refusal path — the gate refusing `accept` on a mandatory failure while preserving the baseline — was never exercised; the rollback rehearsal does not substitute for it.
- Boundary findings come from synthetic fixtures outside the repository; they demonstrate checker behavior classes, not incidence in this repo's actual files.
- Repo-wide counts (230 files, 340 link targets) drift as parallel Wave E/G tasks land files; a later rerun will produce different counts.
- The rehearsal never executed a revert in a pushed history; recovery from a committed revert (`git revert HEAD`) is stated, not rehearsed.
- `python3 scripts/validate.py --task E3 --root .` reports `Unknown task E3` because Wave E tasks are not wired into `tasks/manifest.json`; task-scoped validation could not run.

## Reproduction

Environment: this repository at HEAD `6f205d65453c7699016abc2f4d18e5db31002544`, or any commit where `421ed6e` is an ancestor and the three gated paths are unmodified since; Python 3.12.3; offline.

1. Verify the start state: `git status --short` (expect empty), `git rev-parse HEAD`, `git show 421ed6e --stat`.
2. Run the gate checks in order: `python3 -m unittest tests.test_check_links -v`; `python3 scripts/check_links.py`; `python3 scripts/validate_artifacts.py`; `python3 scripts/validate.py --root .`.
3. Perform the diff review: `git show 421ed6e`, read both gated files in full, and run `git log 421ed6e..HEAD -- scripts/check_links.py tests/test_check_links.py handoffs/A2.md` (expect empty output).
4. Build the boundary fixture outside the repository: a directory containing `target.md` (`target`), a file literally named `weird(1).md` (`target`), `sub/note.md`, and `a.md` with the four probe links from the boundary table, each composed in the usual bracket-parenthesis form with the recorded link text and target. Run `python3 <repo>/scripts/check_links.py <fixture-dir> --as-of 2026-09-01` and expect the single false positive `a.md:7: broken relative link: weird(1` with exit 1.
5. Run the rollback rehearsal with the Packet 2 protocol; expect 634 staged deletions across exactly the three files, zero conflicts, and an identical HEAD after `git revert --abort`.
6. Compare observed outputs against the Run 1 and Run 2 tables. Any divergence marks the corresponding check as not reproduced for the diverging condition.

## Changelog

- 2026-09-01 — `0.1.0`: Recorded the first gate trial (commit `421ed6e`) and rollback rehearsal; two runs, both complete; Practice 003 remains proposed because the second-artifact-type and refusal-path requirements of its own trial bar are unmet.
