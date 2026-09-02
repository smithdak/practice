# Final integration report V2 — Phase 2

**As of:** 2026-09-01 · **Integrator:** Q-INT · **Baseline:** `d97fe4a6` (Phase 1
Q005 candidate) · **Phase 2 head at integration:** `5727aa4` plus the uncommitted
Q6/Q7 review files and this task's fixes (the Director commits the integration).

## Outcome

Phase 2 is integrated: every Wave R/A/E/G/O/Q output is merged, the REVIEWED
corrections from the adversarial evidence review (Q6 W1–W9), the fact and
currency re-audit (Q7), the onboarding dry run V2 (O4), and the G1/R4 routed
findings are applied, and all four validation gates pass. **Public launch
remains blocked on human decisions only.** No owner gate or operating hold
changed status, no `maturity` or `evidence_quality` field was modified, and no
promotion was executed: all six method candidates remain `maturity: proposed` /
`evidence_quality: none`, and every row in [OWNER_REVIEW.md](../../release/OWNER_REVIEW.md)
remains **OPEN** pending human approval.

## What was integrated

| Wave | Tasks and outputs | Commits |
| --- | --- | --- |
| R — research | R1 snapshot refresh (`buzz/PLATFORM_SNAPSHOT.md`), R2 currency audit, R3 landscape scan, R4 claim audit | `9097a59`, `4f07612`, `5be8506`, `561d077` |
| A — automation | A1 artifact validator, A2 link/as-of checker, A3 Buzz parity test, A4 CI workflow, A5 release-evidence template | `73d7012`, `421ed6e`, `b969315`, `f0c3eab`, `6f205d6` |
| E — trials | E1–E3 trial labs 002–004, E4 single-family eval run, E5 promotion packets | `08123e5`, `42869f4`, `39f290c`, `1e22021`, `df16c27` |
| G — progression | G1 guide review, G2 Note/Project schemas, G3 Practices 004–006, G4 intake/consent templates | `cda441a`, `7a0573c`, `3ffe31e`, `1f80f96` |
| O — launch ops | O1 gate-evidence packets, O2 steward readiness checker, O3 hosted inspection checklist, O4 onboarding dry run V2, O5 beta ops kit | `96e0e6c`, `218080b`, `96c409a`, `5a9f275`, `03c4c18`, `79feb9b`, `5727aa4` |
| Q — review and integration | Q6 evidence review, Q7 fact re-audit, Q-INT integration (this task) | Q6/Q7 and this task's fixes committed by the Director |

## Fixes applied by category

Each fix traces to a review finding; cited locations were verified before
editing. Full decision detail lives in the handoffs and the reports named below.

### A — Q6 required wording fixes (W1–W9)

Source: [reviews/EVIDENCE_REVIEW.md](../../reviews/EVIDENCE_REVIEW.md) "Required
wording changes". The promotion packets now read as what the evidence is:
three single-run demonstrations and one self-graded smoke test, all one
operator class — not convergent independent evidence. Each packet's §6
decision question is unchanged.

- `release/PROMOTION_PACKETS.md` — W1 (`### 3. Corroborating evidence` →
  `### 3. Related eval run (same operator class — not corroboration)` at all
  three packets, with "passed 9 of 9" → "self-graded 9 of 9"); W2 (the 68/68
  agreement headline replaced with the bounded zero-findings rewrite that
  states the one-sided, tuned-on-corpus design); W3 (Packet 1 "sole operating
  input" → pack-plus-named-sources wording); W4 (Packet 3 "full gate applied
  end to end" → pre-merged artifact, approval never executed, prevention not
  demonstrated); W5 ("all 6 mandatory checks passed" → operator-pre-framed
  mandatory set); W6 (recommendation strength "Moderate–strong" → "Moderate
  (schema-minimum only; no independent-reader evidence)"); W7 (packet header
  commit-range sentence corrected to name the four Wave E evidence commits).
- `skills/evals/EVAL_REPORT.md` — W8 (headline rewritten: 45/45 is a
  self-graded pass against criteria visible during production; no pass is
  independently auditable). The bold hedge and limitations are unchanged.
- `labs/004-verification-gate-trial.md` — W9 ("was evidently fixed by another
  task" → "no longer reproduces as of this run; the cause and the fix are
  unverified").

### B — Stale snapshot dates and undated reviews (Q7)

Source: [reviews/FACT_AUDIT_PHASE2.md](../../reviews/FACT_AUDIT_PHASE2.md) sections 3 and
5. Platform-derived "reviewed 2026-08-31" entries refreshed to 2026-09-01;
entries Q7 explicitly marked not snapshot-derived (Capability Ladder,
METRICS, Code of Conduct) kept their original review dates.

- `community/ONBOARDING.md` — snapshot, BUZZ_SECURITY, and IA entries
  refreshed; Capability Ladder entry intentionally unchanged.
- `community/CAPABILITY_SELF_ASSESSMENT.md` — IA and BUZZ_SECURITY entries
  refreshed; Capability Ladder entry unchanged.
- `ops/BUZZ_SECURITY.md` — snapshot basis line and both source entries.
- `ops/outreach/INVITE_FUNNEL.md` — snapshot, onboarding, and security-runbook entries
  refreshed; METRICS and Code of Conduct entries unchanged.
- `buzz/CHANNELS.md` — snapshot as-of parenthetical.
- `README.md` — snapshot date in Core documents (also D below).
- `release/OWNER_REVIEW.md` — snapshot dates in the Sources paragraph and the
  Buzz-constraints section.
- `reviews/ONBOARDING_DRY_RUN_PHASE2.md`, `reviews/EDITORIAL_REVIEW.md`,
  `reviews/REPOSITORY_INTEGRITY.md` — one-line as-of date stamps added at the
  top (each also states its original review date/commit so the stamp cannot be
  misread as the review date).
- `reviews/FACT_AUDIT_PHASE1.md` — superseded-note header pointing at
  FACT_AUDIT_V2 and the 2026-09-01 snapshot.

### C — O4 required onboarding fixes

Source: [reviews/ONBOARDING_DRY_RUN_PHASE2.md](../../reviews/ONBOARDING_DRY_RUN_PHASE2.md)
findings N1, N2, N4 (ranked defects 1, 2, 4 — copy portion).

- Six-vs-three copy: `README.md` and `docs/CONTEXT.md` now state the truth — six
  candidate method files; the first three have recorded trials in
  `labs/002`–`004`; a recorded trial does not change maturity; all remain
  `maturity: proposed` pending human review. `docs/CONTEXT.md` lists all six
  candidates.
- G4 intake/consent route linked from every named surface:
  `.github/ISSUE_TEMPLATE/story.yml` (new markdown block plus a Before-field
  description, matching the lab/project form format), `templates/STORY.md`
  (Anonymization and consent section), and
  `community/CONTRIBUTOR_QUICKSTART.md` (new Story bullet linking
  `templates/INTAKE_CONSENT.md`, `templates/REDACTION_CHECKLIST.md`, the Story
  issue form, and the Story template).
- Taxonomy discoverability: `docs/framework/TAXONOMY.md` now linked from the
  quickstart's "Choose a path" intro and from
  `community/CONTRIBUTION_MODEL.md`'s contribution-ladder paragraph.

### D — G1/R4 routed integrator fixes

Source: [swarm/handoffs/G1.md](../handoffs/G1.md) notes 1–3,
[reviews/FACT_AUDIT_PHASE2.md](../../reviews/FACT_AUDIT_PHASE2.md) section 4 (R2/R4 items
still open).

- `README.md:43` — the personal-environment reference generalized to
  "exact pickup sequence for the owner's terminal environment" (R4 finding #1
  remediation; the manual pre-release check of `swarm/README.md` itself
  remains an owner action).
- `README.md:51` — snapshot date refreshed to 2026-09-01.
- `practices/README.md` — the undated maturity restatement removed; the index
  now defers to each file's front matter and states factually that the first
  three candidates have recorded trials that do not change front-matter
  maturity (R2 correction, as updated by Q7 for six candidates).
- `labs/001-cheap-model-bounded-task.md:202` — price-basis instruction made
  conditional per R2's proposed wording.

### E — Core outputs

- `release/OWNER_REVIEW.md` — every owner-gate and operating-hold row's
  evidence column now names its Phase 2 evidence packet:
  [GATE_EVIDENCE.md](../../release/GATE_EVIDENCE.md) (per gate/hold number),
  [PROMOTION_PACKETS.md](../../release/PROMOTION_PACKETS.md),
  [HOSTED_INSPECTION.md](../../release/HOSTED_INSPECTION.md),
  `scripts/steward_readiness_check.py`, the platform snapshot as of
  2026-09-01, and [ONBOARDING_DRY_RUN_PHASE2](../../reviews/ONBOARDING_DRY_RUN_PHASE2.md).
  All eight gate rows and all seven hold rows remain **OPEN**; statuses were
  not changed by this integration. The Tested-Practice hold row now says six
  candidate files (was "all three"), and the content-evidence list drops the
  stale "three".
- `swarm/reports/PHASE2_REPORT.md` — this report.

## Deferred — not done, by deliberate scope decision

- **Manifest wiring.** Phase 2 tasks are not registered in
  `swarm/manifest.json`; `python3 scripts/validate.py --task Q-INT --root .`
  therefore reports "Unknown task Q-INT". Wiring is reserved to the single
  authorized task per swarm/plans/PHASE2_PLAN.md; workers must not edit the
  manifest. Release validation of Phase 1 manifest-owned evidence is
  unaffected and passes.
- **Six-class claim sweep over post-R4 files (Q7 coverage gap).** Files
  created after R4's 68-file scope was fixed — `practices/004-006`, the G2
  schemas/templates, `ops/BETA_OPS.md`, `.github/ISSUE_TEMPLATE/triage-policy.md`
  (and CI file), `release/HOSTED_INSPECTION.md`, `release/PROMOTION_PACKETS.md`,
  `reviews/ONBOARDING_DRY_RUN_PHASE2.md`, and this report — have not had the
  six-class publishability sweep. Q7's spot-check found no invented metrics in
  the packets; a full pass is owed before launch. Note this integration
  introduced new prose (this report, OWNER_REVIEW rows) that also awaits that
  sweep.
- **Second-family evals.** The five skill evals ran on one model family; the
  second-family dimension is recorded as not run, and results do not count
  toward `tested` maturity by the evals' own policy.
- **Second trials.** Practice 001's independent cold-reader trial, Practice
  002's W5/W6 execution against an independent reference, and Practice 003's
  second artifact type with the refusal path and human approval remain
  unexecuted; the promotion packets' decision questions rest on that fact.
- **First-post format unification (O4 N5) and CONTRIBUTING.md Story-row
  links (O4 defect 1's optional third surface).** Outside this task's file
  list; left as recorded minor defects.
- **`reviews/ONBOARDING_DRY_RUN_PHASE2.md` re-run.** O4's deferred opportunity to
  re-simulate the fixed surfaces before public invitation promotion; the
  entry-path fixes above are merged but unverified by a fresh persona walk.

## Final validation evidence

All four gates pass on the integrated worktree:

```text
$ python3 scripts/validate_artifacts.py
Artifact validation passed (1 guide, 6 guide modules, 4 labs, 6 practices, 1 story).
Exit 0

$ python3 scripts/check_links.py
Checked 272 markdown file(s), 638 link target(s): 0 broken link(s), 0 stale as-of date(s).
Exit 0

$ python3 -m unittest discover -s tests
Ran 145 tests in 0.164s
OK

$ python3 scripts/validate.py --release
Validation passed.
Exit 0
```

A validator pass is evidence only for the checks it ran. It does not clear any
owner gate, flip any maturity value, or authorize publication.

## What a human still owns before launch

Everything in [OWNER_REVIEW.md](../../release/OWNER_REVIEW.md): the eight owner gates, the
seven evidenced operating holds, the three promotion decisions packaged in
[PROMOTION_PACKETS.md](../../release/PROMOTION_PACKETS.md), the owner-operated Buzz apply and
hosted inspection, and the final release record. Q6's cross-cutting finding
stands: no human has executed or verified any link in the Phase 2 evidence
chain; at least one human-executed or countersigned rerun is the single
cheapest anchor for the whole body of evidence.
