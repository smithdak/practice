# Q-INT Handoff

## Status

COMPLETE

## Summary

Integrated all Wave R/A/E/G/O/Q outputs and applied every REVIEWED correction
without reopening settled strategy or flipping any maturity state. Q6's W1–W9
wording fixes are applied to the promotion packets, the eval report, and
labs/004, so the packets now read as three single-run demonstrations plus one
self-graded smoke test by one operator class (each packet's §6 decision
question untouched). Q7's stale-date list is refreshed to 2026-09-01 and the
three undated review files carry as-of stamps; PLATFORM_FACT_AUDIT is marked
superseded. O4's required onboarding fixes landed: truthful six-candidate copy
in README/CONTEXT, the G4 intake/consent route linked from `story.yml`,
`templates/STORY.md`, and the contributor quickstart (new Story bullet), and
the Knowledge Taxonomy linked from the quickstart and CONTRIBUTION_MODEL.
G1/R4 routed fixes landed: generalized NEW_TERMINAL reference, snapshot date
in README, front-matter-deferring practices index, conditional price-basis
wording in labs/001. OWNER_REVIEW's eight gate rows and seven hold rows now
point at their Phase 2 evidence packets with all statuses still **OPEN**;
`release/FINAL_INTEGRATION_REPORT_V2.md` records the integration, the
deferred-not-done list, and the validation evidence. No owner gate was
asserted cleared; no `maturity`/`evidence_quality` field changed.

## Files changed

- A (Q6 W1–W9): `release/PROMOTION_PACKETS.md`, `skills/evals/EVAL_REPORT.md`,
  `labs/004-verification-gate-trial.md`
- B (Q7 dates/stamps): `community/ONBOARDING.md`,
  `community/CAPABILITY_SELF_ASSESSMENT.md`, `ops/BUZZ_SECURITY.md`,
  `ops/INVITE_FUNNEL.md`, `buzz/INFORMATION_ARCHITECTURE.md`,
  `reviews/ONBOARDING_DRY_RUN_V2.md`, `reviews/EDITORIAL_REVIEW.md`,
  `reviews/REPOSITORY_INTEGRITY.md`, `reviews/PLATFORM_FACT_AUDIT.md`
- C (O4 fixes): `README.md`, `CONTEXT.md`, `.github/ISSUE_TEMPLATE/story.yml`,
  `templates/STORY.md`, `community/CONTRIBUTOR_QUICKSTART.md`,
  `community/CONTRIBUTION_MODEL.md`
- D (G1/R4): `README.md`, `practices/README.md`,
  `labs/001-cheap-model-bounded-task.md`
- E (core outputs): `release/OWNER_REVIEW.md`,
  `release/FINAL_INTEGRATION_REPORT_V2.md` (new)
- `handoffs/Q-INT.md` — this file

## Validation

- Command: `python3 scripts/validate_artifacts.py`
- Result: PASS — `Artifact validation passed (1 guide, 6 guide modules, 4
  labs, 6 practices, 1 story).` Exit 0.
- Command: `python3 scripts/check_links.py`
- Result: PASS — `Checked 273 markdown file(s), 650 link target(s): 0 broken
  link(s), 0 stale as-of date(s).` Exit 0.
- Command: `python3 -m unittest discover -s tests`
- Result: PASS — `Ran 145 tests in 0.152s` / `OK`.
- Command: `python3 scripts/validate.py --release`
- Result: PASS — `Validation passed.` Exit 0.
- Command: `python3 scripts/validate.py --task Q-INT --root .`
- Result: EXPECTED FAIL — `Unknown task Q-INT`; Phase 2 tasks are not wired
  into `tasks/manifest.json` (workers must not edit it). Same condition every
  Phase 2 handoff recorded.
- No git add/commit was run; the Director commits.

## Decisions made

- Applied Q7's precision where its audit refined the task's line ranges:
  Capability Ladder (ONBOARDING:105, SELF_ASSESSMENT:121), METRICS, and
  Code-of-Conduct entries kept their 2026-08-31 review dates because Q7
  explicitly marked them not snapshot-derived; all platform-derived entries
  moved to 2026-09-01.
- The as-of stamps on EDITORIAL_REVIEW/REPOSITORY_INTEGRITY state both the
  stamp date and the original review date/commit, so a reader cannot mistake
  the re-stamp for the review date.
- `README.md:60` ("Three tested Open Practices" launch criterion) was left
  unchanged: it is a release-scope goal, not a factual count, and resolving
  its new ambiguity (exactly vs at least three) is a strategy decision, not an
  integration correction. Noted as residual risk.
- OWNER_REVIEW: the Tested-Practice hold row's "all three candidate files"
  became "all six" (factual count, not a status change), and the content
  evidence list dropped the stale "three"; both cells/rows keep **OPEN**.
- story.yml gained one markdown block (matching the lab/project form format)
  plus a Before-field description; links use `../../templates/…` like the
  sibling forms. check_links.py scans markdown only, so these YAML links were
  hand-verified to resolve.
- W9 was applied verbatim even though it leaves "As of this trial it passes;
  … as of this run" slightly redundant — exact review wording outranks prose
  smoothing in an integration pass.

## Risks or unresolved questions

- `release/GATE_EVIDENCE.md` (outside this task's file list) still says
  "Corroborating but non-counting evidence" and "68/68 agreement" in two
  cells — mildly inconsistent with the W1/W2 reframing now in PROMOTION_PACKETS.md.
  The human-facing decision packet is fixed; a one-line GATE_EVIDENCE touch-up
  is available to the Director or a follow-up task.
- `NEW_TERMINAL.md` itself still contains machine-specific paths ("Dakota's
  WSL"); R4's manual pre-release check of that file remains an owner action.
- R4's six-class sweep gap now includes prose introduced by this integration
  (OWNER_REVIEW rows, FINAL_INTEGRATION_REPORT_V2.md).
- O4's N5 (three first-post formats) and the CONTRIBUTING.md Story row
  (`CONTRIBUTING.md` was outside this task's file list) remain open minor
  defects; the G4 route is reachable from every surface O4 named as required.
- If a Practice promotion lands after this integration, the practices index
  defers to front matter, so no sentence in it goes false — but README/CONTEXT
  candidate copy and the OWNER_REVIEW hold row are owned by those files and
  must be updated by the promotion decision owner (as PROMOTION_PACKETS §6
  already instructs).

## Deferred opportunities

- Manifest wiring for Phase 2 tasks (single authorized task per plan).
- Six-class claim sweep over all post-R4 publishable surfaces, including this
  integration's new prose.
- Second-family eval run and the human severe-failure inspection the eval
  protocol already requires.
- Second trials per packet: cold-reader trial (001), W5/W6 with independent
  reference (002), second artifact type + refusal path + human approval (003).
- O4's deferred re-run of the onboarding simulation over the fixed surfaces
  before any public invitation promotion.
- Unify the three first-post formats (O4 N5) and add G4 links to
  CONTRIBUTING.md's path table.
