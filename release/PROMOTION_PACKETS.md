# Promotion packets — first three Practice candidates

Decision packet for a human reviewer deciding whether the three method
candidates become tested Practices. Evidence is dated 2026-09-01; the three
trials were recorded against repository commit `6f205d65453c7699016abc2f4d18e5db31002544`
(this packet was assembled at `1e22021` the same day; the only commits between
the trials' base and this packet's assembly are the four Wave E evidence
records themselves and the whitespace fix `c2a10c0`, noted in Packet 1). Numbers
are quoted only from the Labs and the eval report; anything not recorded in a
source is labeled unknown, not estimated.

**No maturity value is changed by this file.** All three candidates remain
`maturity: proposed` / `evidence_quality: none`. The recommendations below are
agent-generated and non-binding; human review is the promotion gate
([practices/README.md](../practices/README.md) and the "Tested-Practice
evidence" hold in [OWNER_REVIEW.md](OWNER_REVIEW.md)).

## Decision rules in force

- `proposed → tested` requires a documented application of the stated method; a
  tested Practice carries `evidence_quality: single-run` or `repeated` and must
  contain Implementation, Evaluation with checks/criteria/observed result,
  Failure modes with observed failures, and an Evidence section
  ([PRACTICE_SCHEMA.md](../docs/schemas/PRACTICE_SCHEMA.md)).
- "A human maintainer may promote a method only after the artifact records the
  trial and review evidence required by its schema"
  ([practices/README.md](../practices/README.md)).
- `scripts/validate_artifacts.py` enforces the mechanical part: a `tested`
  Practice must declare `single-run`/`repeated`, keep the mature headings, and
  link a trial record (`labs/…`) in its body.
- The [launch checklist](LAUNCH_CHECKLIST.md) content check keeps public copy at
  "proposed method or Practice candidate" "until the trial, review, and
  promotion record exists."

---

## Packet 1 — Practice 001 "Build a reusable context pack"

### 1. Current state

- Front matter: `maturity: proposed`, `evidence_quality: none`, version 0.1.0,
  `capability: use` ([practices/001-context-pack.md](../practices/001-context-pack.md)).
- Method in one line: prepare stable instructions, approved sources,
  constraints, examples, and checks so recurring AI work starts from the same
  reviewable context.

### 2. Trial evidence

Source: [labs/002-context-pack-trial.md](../labs/002-context-pack-trial.md)
(`status: completed`, `result_status: complete`, `run_count: 1`). Run E1-R1,
2026-09-01 17:06:26Z–17:13:32Z, at commit `6f205d65`, pack v0.1.0 frozen before
the run (sha256 prefix `8025c2e83c0f87a4`), single agent operator.

What was actually run: a context pack assembled strictly per the Practice's
seven Method steps was the operating input for the run, together with the
repository sources the pack itself names (the launch checklist §1 that defines
the nine checks is source S1 of that pack), producing a non-secret evidence
summary.

What passed and failed (real numbers):

- 8 of 9 §1 checks passed. Item 1a failed for real: `git diff --check
  d97fe4a6..6f205d65` exited 2 with one trailing-whitespace finding at
  `buzz/PLATFORM_SNAPSHOT.md:3`; the pack routed it correctly (record
  verbatim, no repair, continue, escalate to the release maintainer).
  Repository state as of this packet: the whitespace was fixed post-trial in
  commit `c2a10c0` (2026-09-01), closing that escalation.
- The pack's own acceptance checklist C1–C10 scored 9 PASS, 1 FAIL-as-written
  (C10, strict pre/post worktree equality — broken by 3 untracked files created
  concurrently by worker E4, not by the run). Run-level disposition: supported
  at the predeclared threshold.
- Friction log: F1 baseline ambiguity (resolved during assembly), F2
  environment-dependent "no Buzz CLI installed" confirmation (mid-run
  deviation), F3 strict-equality worktree check under concurrency (mid-run
  deviation), F4 the real failure exercised the escalation path as designed.

Observed failure modes (recorded in the Lab): the C10 strict-equality defect
under concurrent workers; the F2 environment-dependent criterion; two pack gaps
handled as recorded deviations without mid-run pack edits.

What the trial does NOT cover: reliability (one run), one repository and
commit snapshot, an operator who is also the pack assembler (Practice 001's
step-7 independent cold-reader check was only self-administered),
judgment-heavy tasks (every trial step was a deterministic command with
readable exit codes), accuracy/speed/cost effects (explicitly not measured),
and drift after the candidate commit.

### 3. Related eval run (same operator class — not corroboration)

[skills/evals/EVAL_REPORT.md](../skills/evals/EVAL_REPORT.md) (2026-09-01): the
`build-context-pack` skill self-graded 9 of 9 cases. Self-graded limitation, stated
by the report itself: all 45 cases were run by one model family (GLM,
`z-ai/glm-5.3-flash`), self-run and self-graded, activation simulated rather
than host-driven, no human reviewer; per the eval YAMLs' own policy these
results "do not count as passes" for promotion. Treat as a smoke pass, not
behavioral proof.

### 4. Promotion criteria checklist

| # | Criterion (source) | Status | Evidence pointer |
|---|---|---|---|
| SC-1 | Documented application of the stated method — context, method version, safe inputs (schema "tested" row; `single-run` minimum) | Met | labs/002 run E1-R1: commit, run window, frozen pack v0.1.0, read-only task |
| SC-2 | Evaluation with checks, criteria, and observed result (schema "tested" row) | Met | labs/002: predeclared C1–C10 dispositions (9 pass / 1 escalated), rubric, run ledger |
| SC-3 | Implementation section (schema "tested" row) | Met | practice §Implementation (minimal and advanced) |
| SC-4 | Failure modes record observed or deliberately tested failures with consequence and response (schema "tested" row) | Not met (artifact) | Observed failures exist in labs/002 (F2, F3, C10, F4); practice §Failure modes still lists hypotheses only |
| SC-5 | Evidence section preserving the safe-to-share record and limitations (schema "tested" row) | Not met (artifact) | practice §Evidence still says "a planned trial only" — now stale; must be rewritten with the labs/002 link |
| SC-6 | Record satisfies the `single-run` evidence minimum (schema evidence-quality table) | Met | labs/002 records context, method version, inputs, criteria, outcome, limitations |
| SC-7 | The practice's own Evaluation acceptance is met | Partial | Checklist pass-or-escalated condition met; the "Practitioner who did not assemble it" reader element was self-administered (labs/002 Limitations) |
| PR-1 | Human maintainer review recorded (practices/README; OWNER_REVIEW hold row) | Not met | This packet requests that review; no decision recorded yet |
| PR-2 | The practice artifact records the trial — front matter plus a `labs/…` body link (practices/README; validator mechanics) | Not met | No practice file was modified; the validator requires the body link once `maturity: tested` |

Count: 4 met · 1 partial · 4 not met. SC-4, SC-5, and PR-2 are resolved by
executing the promotion edit; PR-1 is the decision itself.

### 5. Residual risks vs. a second trial

Risks of promoting now:

- The strongest unverified claim is independence: assembler = executor, so
  "another Practitioner can use the pack unaided" is untested.
- The one observed task is fully command-backed; packs for judgment-heavy tasks
  may fail in ways this trial could not expose (labs/002 Limitations).
- No effectiveness claim is licensed: the rubric measured usability and
  compliance only; public copy must not drift into accuracy/speed/cost claims.
- Pack gaps F1–F3 would recur in a shared worktree or a different environment
  until a pack v0.2.0 revision exists.

A second trial should cover: an independent cold reader executing the pack
(step 7 of the Method), a second task type (ideally judgment-heavy), the v0.2.0
pack incorporating the F1–F3 fixes, and — with two documented applications —
movement toward `repeated`.

### 6. Decision requested

**Question for the reviewer:** Do you promote Practice 001 to
`maturity: tested` with `evidence_quality: single-run` on the evidence of
labs/002 (run E1-R1), accepting its recorded limitations — or hold until an
independent cold reader has executed the pack once?

To execute a promotion, the reviewer records (in the practice file — this
packet does not execute it):

1. Front matter: `maturity: tested`, `evidence_quality: single-run`, `updated`
   set to the decision date; a version bump only if the Method itself changes
   (schema material-change rule).
2. Body: rewrite §Evidence to cite [labs/002](../labs/002-context-pack-trial.md)
   (run E1-R1) with the outcome, the F1–F4 friction results, the C10 failure,
   and the limitations; update §Failure modes from hypotheses to observed,
   keeping unobserved items labeled as hypotheses.
3. A Changelog entry; then `python3 scripts/validate_artifacts.py --root .`
   must pass (it enforces the tested/evidence pairing and the `labs/…` body
   link).
4. Downstream copy owned by other files — practices/README.md index,
   [LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md) content check, OWNER_REVIEW.md
   hold row, docs/CONTEXT.md candidate note — is updated by those files' owners to
   match the decision.

---

## Packet 2 — Practice 002 "Redesign a recurring workflow"

### 1. Current state

- Front matter: `maturity: proposed`, `evidence_quality: none`, version 0.1.0,
  `capability: automate` ([practices/002-workflow-redesign.md](../practices/002-workflow-redesign.md)).
- Method in one line: map a recurring workflow, assign the right level of
  automation and human ownership, and test changes behind reviewable safety
  gates.

### 2. Trial evidence

Source: [labs/003-workflow-redesign-trial.md](../labs/003-workflow-redesign-trial.md)
(`status: completed`, `result_status: complete`, `run_count: 2` included runs;
two earlier defective runs excluded and retained). Runs T3/T4 on 2026-09-01 at
commit `6f205d6`, Python 3.12.3 standard library, offline, read-only.

What was actually run: the six-class publishability claim audit that worker R4
executed manually was mapped (B1–B9), classified, and redesigned into W1–W7
(deterministic, AI-assisted, human-owned); the deterministic slice was then
executed for real — a stdlib checker for class 6 (placeholder text and
unresolved bracketed tokens) and class 4 (license front matter), compared
against R4's recorded verdicts on 68 reference files.

What passed and failed (real numbers):

- In both included runs (T3 checker v0.3, T4 v0.4) the checker reported 0
  findings, matching R4's recorded clean verdicts on the 68 reference files.
  Every reference verdict is "clean", so the comparison can only show the
  checker does not over-flag; it measures nothing about detection. The checker
  was revised twice against this same corpus before the included runs.
- SOCIAL_KIT exception self-check: 26/26 tokens (per-token counts 12/4/4 and
  six 1s) in both included runs.
- Front-matter inventory: T3 matched R4's claim 6/6; T4 found 7 — the seventh
  was `labs/004-verification-gate-trial.md`, created concurrently by worker E3
  between runs; an explained delta, not a mismatch.
- Elapsed time: 41.5 ms per included run (excluded runs: T1 41.2 ms, T2
  39.6 ms).
- Two of four recorded runs were excluded checker defects (T1: `@`/`#` prefix
  matched outside the brackets, exception-spec count 21/26; T2: literal `@`
  instead of the optional class `[@#]?`, count 1/26). Both were caught by
  comparison against the recorded reference, not by the checker itself.
- Sensitivity: removing the masking policy produces 3 extra hits in 1 file
  (`swarm/reports/PHASE1_REPORT.md:87`) — the masking policy is
  load-bearing for agreement.

Observed failure modes (recorded in the Lab): transcription error twice (T1,
T2); a load-bearing implicit policy that existed only as repository convention;
shared-worktree drift (corpus changed 68 → 69 mid-trial). Guarded but not
observed: approval-after-effect and no-usable-rollback — the trial was
read-only and published nothing.

What the trial does NOT cover: classes 1, 2, 3, and 5 (unmeasured, including
the live class-5 finding at `README.md:43` awaiting the owner decision R4
recorded); the AI-assisted triage step (W5) and the human review checkpoint
(W6) — designed but never executed; any speed or cost comparison (the manual
audit's duration is unknown); generalization beyond this corpus and commit.

### 3. Related eval run (same operator class — not corroboration)

[skills/evals/EVAL_REPORT.md](../skills/evals/EVAL_REPORT.md) (2026-09-01): the
`redesign-ai-workflow` skill self-graded 9 of 9 cases, including an unsafe-input
case that kept payment approval human-owned. Same self-graded limitation as
Packet 1: single model family, self-run/self-graded, simulated routing, no
human reviewer; by the evals' own policy these results do not count toward
promotion.

### 4. Promotion criteria checklist

| # | Criterion (source) | Status | Evidence pointer |
|---|---|---|---|
| SC-1 | Documented application of the stated method — context, method version, safe inputs (schema "tested" row; `single-run` minimum) | Met, scoped | labs/003: the redesign method was applied for real (map, classification, gates, comparison experiment), but only through the deterministic slice; W5/W6 were never executed |
| SC-2 | Evaluation with checks, criteria, and observed result (schema "tested" row) | Met | labs/003: T1–T4 ledger, measured-comparison table, predeclared decision rule |
| SC-3 | Implementation section (schema "tested" row) | Met | practice §Implementation (minimal and advanced) |
| SC-4 | Failure modes record observed or deliberately tested failures with consequence and response (schema "tested" row) | Not met (artifact) | Observed failure modes are in labs/003; practice §Failure modes still lists hypotheses only |
| SC-5 | Evidence section preserving the safe-to-share record and limitations (schema "tested" row) | Not met (artifact) | practice §Evidence still says "a planned trial only" — stale; must be rewritten with the labs/003 link |
| SC-6 | Record satisfies the `single-run` evidence minimum (schema evidence-quality table) | Met, scoped | labs/003 records context, versions, inputs, criteria, outcome, limitations — with its own bounded-inference note limiting the claim to the executed slice |
| SC-7 | The practice's own Evaluation acceptance is met | Partial | Map-level criteria met (traceable run and exception, classifications, owners); "approval precedes consequential effects" and "rollback is actionable" untested (read-only trial); the continue/revise/revert decision is recorded only implicitly in the Interpretation section |
| PR-1 | Human maintainer review recorded (practices/README; OWNER_REVIEW hold row) | Not met | Pending the decision this packet requests |
| PR-2 | The practice artifact records the trial — front matter plus a `labs/…` body link (practices/README; validator mechanics) | Not met | No practice file was modified |

Count: 4 met · 1 partial · 4 not met.

### 5. Residual risks vs. a second trial

Risks of promoting now:

- The agreement is partially circular: the checker's exception data was
  transcribed from R4's prose, and R4's verdicts are a single AI-worker pass
  that no human has independently verified — the checker can reproduce R4's
  blind spots, not just its conclusions (labs/003 Limitations).
- The method's differentiating machinery — the human-machine boundary (W5
  AI-assisted triage, W6 human checkpoint) — has never been executed. A
  promotion today would rest on the parts of the method that are ordinary
  scripting.
- 4 of 6 defect classes are unmeasured; the live class-5 finding at
  `README.md:43` still awaits an owner decision.
- The checker, masking policy, and exception data live in `/tmp/opencode`, not
  as versioned repository artifacts; they can drift from the prose they encode.
- The corpus drifted mid-trial (68 → 69 files), so a pinned corpus is a
  precondition before checker verdicts can act as a release gate.
- No timing baseline for the manual audit exists, so no speed claim is
  possible.

A second trial should cover: executing the W6 human checkpoint with a named
human reviewer on real findings; running the W5 AI-triage slice for classes
1/2/3/5 over the W4 signal extractor; promoting the checker into `scripts/`
with tests and versioned exception data; pinning the corpus by commit; and
using an independent reference to break the circularity.

### 6. Decision requested

**Question for the reviewer:** Do you promote Practice 002 now with a claim
scoped to the executed deterministic slice (classes 4 and 6), or hold until a
second trial executes the human review checkpoint (W6) and the AI-assisted
triage slice (W5)?

To execute a promotion, the reviewer records (in the practice file — this
packet does not execute it):

1. Front matter: `maturity: tested`, `evidence_quality: single-run`, `updated`
   set to the decision date; version bump if the Method changes.
2. Body: rewrite §Evidence to cite
   [labs/003](../labs/003-workflow-redesign-trial.md) with the scoped claim
   (deterministic slice only; W5/W6 unexecuted; partially circular reference),
   the T1–T4 results, and the limitations; update §Failure modes to the
   observed items; consider whether the summary must be reworded to match the
   scoped evidence.
3. A Changelog entry; then `python3 scripts/validate_artifacts.py --root .`
   must pass.
4. Downstream copy owned by other files (practices/README.md index,
   [LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md), OWNER_REVIEW.md hold row,
   docs/CONTEXT.md candidate note) is updated by those files' owners.

---

## Packet 3 — Practice 003 "Verify an agent's output before accepting or shipping it"

### 1. Current state

- Front matter: `maturity: proposed`, `evidence_quality: none`, version 0.2.0,
  `capability: use` ([practices/003-verification-gate.md](../practices/003-verification-gate.md)).
- Method in one line: apply universal and artifact-specific checks, record
  evidence, obtain required human approval, and keep a reversible path before
  accepting agent-produced work.

### 2. Trial evidence

Source: [labs/004-verification-gate-trial.md](../labs/004-verification-gate-trial.md)
(`status: completed`, `result_status: complete`, `run_count: 2` — R1 gate
trial, R2 rollback rehearsal). Executed 2026-09-01 at HEAD `6f205d65`; gated
artifact: commit `421ed6e` (task A2's link checker), produced by a different
task than the one running the gate.

What was actually run: the gate's framing, checks, diff review, and decision
steps executed once on one code change that had already been merged before the
gate ran, plus a predeclared rollback rehearsal. The approval step was never
executed (`approval: null`), and because the artifact pre-landed, the gate
could not have prevented the merge — the trial documents the artifact and
rehearses recovery rather than demonstrating prevention.

What passed and failed (real numbers):

- R1: all 6 checks that the single operator had pre-framed as mandatory passed
  (the mandatory/advisory split was authored by the same agent that ran the
  checks) — M1 unit tests: `34 tests` OK in `0.028s`;
  M2 repo-wide run: `Checked 230 markdown file(s), 340 link target(s): 0
  broken link(s), 0 stale as-of date(s)`, exit 0; M3 full diff review: 3 files,
  634 insertions, standard library only, no secrets or network; M4 scope
  discipline: exactly the three owned paths, untouched since; M5 artifact
  validator exit 0; M6 rollback rehearsed. Both advisory checks passed (A1
  `validate.py --root .` exit 0; A2 boundary fixtures: 1 false-positive class
  and 3 false-pass classes recorded).
- Gate decision: recommended `accept` with `approval: null` — the agent cannot
  self-approve.
- R2: `git revert --no-commit 421ed6e` staged exactly 3 files / 634 deletions
  with 0 conflicts; `git revert --abort` left the tree clean and HEAD
  byte-identical before and after.
- Boundary findings — what the gate does NOT prove: anchors are never
  validated; reference-style usages without definitions are ignored; directory
  targets pass; a valid file named like `weird(1).md` is falsely reported
  broken (target truncated at the first `)`). Latent only: no parenthesized
  filename existed in the repository as of 2026-09-01.

Observed failure modes (recorded in the Lab): the trial process itself
exhibited the Practice's listed "late approval" failure mode — commit
`421ed6e` was already on the branch when the gate ran, so the gate documented
the artifact and rehearsed recovery but could not prevent the effect.

What the trial does NOT cover, in the Lab's own words: "Against the Practice's
own trial bar: not fully met." One artifact type (code) instead of the two the
Practice's Evaluation requires; the refusal path was never exercised (no
mandatory check failed, so the gate never had to refuse `accept` and preserve
the baseline); no human approval was obtained; no independent reproducer has
re-executed the record.

### 3. Related eval run (same operator class — not corroboration)

[skills/evals/EVAL_REPORT.md](../skills/evals/EVAL_REPORT.md) (2026-09-01): the
`verify-agent-output` skill self-graded 9 of 9 cases; the produced hypothetical gate
record contained a failing mandatory permission-boundary check → decision
`revise`, approval `null` — the correct refusal shape, but as a produced
artifact in an eval, not as an executed gate. Same self-graded limitation:
single model family, self-run/self-graded, no human reviewer; by the evals' own
policy these results do not count toward promotion.

### 4. Promotion criteria checklist

| # | Criterion (source) | Status | Evidence pointer |
|---|---|---|---|
| SC-1 | Documented application of the stated method — context, method version, safe inputs (schema "tested" row; `single-run` minimum) | Met | labs/004: one complete gate application on one real code artifact, gate record predeclared before checks |
| SC-2 | Evaluation with checks, criteria, and observed result (schema "tested" row) | Met | labs/004: per-check table with command, expected, observed, status; rollback rehearsal table |
| SC-3 | Implementation section (schema "tested" row) | Met | practice §Implementation (minimal review packet, machine-readable example) |
| SC-4 | Failure modes record observed or deliberately tested failures with consequence and response (schema "tested" row) | Not met (artifact) | Observed items (late approval; boundary false-pass/false-positive classes) are in labs/004; practice §Failure modes lists hypotheses only |
| SC-5 | Evidence section preserving the safe-to-share record and limitations (schema "tested" row) | Not met (artifact) | practice §Evidence still says "a hypothetical machine-readable example only" — stale; must be rewritten with the labs/004 link |
| SC-6 | Record satisfies the `single-run` evidence minimum (schema evidence-quality table) | Met | labs/004 records context, artifact version, criteria, check results, rollback, outcome, limitations |
| SC-7 | The practice's own Evaluation acceptance is met | Not met | The Practice's Evaluation requires trials "on one bounded artifact from at least two different types" and an intentional unsupported claim or failing test that forces the gate to refuse `accept`; neither happened — labs/004 records this itself |
| PR-1 | Human maintainer review recorded (practices/README; OWNER_REVIEW hold row) | Not met | Pending the decision this packet requests |
| PR-2 | The practice artifact records the trial — front matter plus a `labs/…` body link (practices/README; validator mechanics) | Not met | No practice file was modified |

Count: 4 met · 0 partial · 5 not met.

### 5. Residual risks vs. a second trial

Risks of promoting now:

- Promoting would contradict the Practice's own stated trial bar while its own
  Lab records the bar as unmet — the promotion record would have to explain
  why the bar was waived, which the schema's honesty rules make costly.
- The mandatory human-approval step has never been executed (approval is null
  in the only gate record); "late approval" proved structural in the swarm
  flow (worker commits land before the gate runs) and needs a flow decision,
  not a Lab.
- Single operator-agent framed, ran, and wrote the record; no independent
  reproducer has re-executed anything.
- The boundary findings are latent tool defects, not gate defects — but a
  promotion should not be read as validating the gated checker itself.
- The gate is proven only for code-change acceptance in this repository;
  research briefs, configuration, and operational actions remain ungated.

A second trial should cover: gating a second artifact type (for example a
research brief) with a planted unsupported claim or failing mandatory check to
force the refusal path and baseline preservation; a named human executing the
approval step on a real record; and an independent reproducer re-running the
Reproduction section and countersigning.

### 6. Decision requested

**Question for the reviewer:** Do you hold Practice 003 at `maturity: proposed`
until a second trial covers a second artifact type and the refusal path — and
if you promote despite the unmet bar, which limitation do you record in the
Evidence section?

If promoting anyway, the reviewer records (in the practice file — this packet
does not execute it):

1. Front matter: `maturity: tested`, `evidence_quality: single-run`, `updated`
   set to the decision date; version bump if the Method changes.
2. Body: rewrite §Evidence to cite
   [labs/004](../labs/004-verification-gate-trial.md) and explicitly record the
   two unmet trial-bar conditions (second artifact type, refusal path) and the
   null approval; update §Failure modes with the observed late-approval and
   boundary findings.
3. A Changelog entry; then `python3 scripts/validate_artifacts.py --root .`
   must pass.
4. Downstream copy owned by other files (practices/README.md index,
   [LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md), OWNER_REVIEW.md hold row,
   docs/CONTEXT.md candidate note) is updated by those files' owners.

---

## Decisions requested (consolidated)

| Candidate | Agent recommendation (non-binding) | Strength | What would change the recommendation |
|---|---|---|---|
| 001 — Build a reusable context pack | Promote now, recording the independent-reader limitation in the Evidence section | Moderate (schema-minimum only; no independent-reader evidence) | An independent cold-reader trial that fails; evidence that pack usability does not extend beyond command-backed tasks |
| 002 — Redesign a recurring workflow | Hold; promote after the human review checkpoint is executed | Moderate | A second trial executing W6 with a named human reviewer and the W5 AI-triage slice, against an independent reference |
| 003 — Verify an agent's output | Hold | Strong | A second gate trial on a different artifact type whose planted mandatory failure forces refusal and baseline preservation, plus a human-executed approval step |

**These recommendations are agent-generated and non-binding.** Human review is
the promotion gate: per [practices/README.md](../practices/README.md) a human
maintainer promotes, and the [OWNER_REVIEW.md](OWNER_REVIEW.md)
"Tested-Practice evidence" hold blocks public launch until the trial evidence,
human review, and an explicit promotion decision are recorded. Until that
decision, public copy must describe all three candidates as proposed methods or
Practice candidates. No maturity field was changed in producing this packet.
