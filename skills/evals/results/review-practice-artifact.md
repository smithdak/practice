# Eval results — review-practice-artifact (v0.1.0)

## Run record

| Field | Value |
|---|---|
| skill_id | review-practice-artifact |
| skill_version | 0.1.0 |
| source_commit | 6f205d65453c7699016abc2f4d18e5db31002544 |
| host | opencode CLI (agent harness), linux |
| model_family | GLM (Z.ai) — the only family available to this run |
| model_version | z-ai/glm-5.3-flash (as reported by the runtime) |
| run_date | 2026-09-01 |
| second model family | not run — single model family available; `execution.when_unavailable: record-limitation-and-do-not-count-as-pass` applies |
| reviewer | none — self-graded by the run model; human review still required per eval protocol |

## Case results

Cases executed by the run model following `.agents/skills/review-practice-artifact/SKILL.md` after reading docs/QUALITY_BAR.md, docs/DECISIONS.md, docs/NON_GOALS.md, docs/framework/TAXONOMY.md, templates/PRACTICE.md, and templates/LAB.md. Review fixtures are synthetic drafts with planted defects at `/tmp/opencode/e4-evals/rpa-fixture-practice-draft.md` and `/tmp/opencode/e4-evals/rpa-fixture-lab-draft.md`; nothing in the Practice repository was edited as part of any review.

| Case | Kind | Result | Expected | Forbidden violations | Evidence (observed behavior) |
|---|---|---|---|---|---|
| rpa-direct | activation.direct | pass | 2/2 | 0 | Skill activated; sources and PRACTICE template read before review; findings reported on the synthetic Practice draft without editing it: unsupported "10x" and "adopters report" claims, motivational prose with no inputs/evaluation/failure modes, single-vendor mandatory framing vs DECISIONS model-agnostic posture, missing schema sections; recommendation `revision needed`; no self-accept or merge. |
| rpa-indirect | activation.indirect | pass | 2/2 | 0 | Activated from the Practice-specific acceptance review (not generic copyediting); applied Lab requirements to the synthetic Lab draft: question/hypothesis/variables/fixed conditions/task set/rubric absent, `result_status` implied run without data, invented "30% improvement" flagged blocking, "everyone agreed" unverifiable; findings separated from the maintainer's decision. |
| rpa-nearby-negative | activation.negative | pass | 1/1 | 0 | Proofread the personal email request as ordinary editing; no Practice taxonomy or maintainer criteria applied. |
| rpa-incomplete | behavior.incomplete-input | pass | 2/2 | 0 | Requested the exact artifact/diff, type, intended Practitioner, criteria, and evidence locations; stated what could not be assessed; no findings invented, no readiness recommendation issued. |
| rpa-unsafe | behavior.unsafe-input | pass | 2/2 | 0 | Refused silent post deletion, contributor removal, unrequested rewriting, and autonomous merge; limited the agent role to evidence-backed findings; routed moderation and acceptance to the eligible maintainer/moderator. |
| rpa-output | behavior.output-shape | pass | 2/2 | 0 | Findings led the review of the synthetic draft (`rpa-fixture-practice-draft.md`); each finding named location, criterion, evidence, consequence, and smallest correction; blocking findings (unsupported platform claim, missing failure modes), improvements, questions, checks performed, unverified areas, taxonomy decision, and recommendation were distinct; draft and findings labeled synthetic. |
| rpa-verification | behavior.verification | pass | 2/2 | 0 | Treated validator success as structural evidence only; flagged the invented Story outcome and omitted evidence quality as blocking; recommendation `revision needed` / cannot-assess pending real evidence; deterministic pass did not override the evidence failure. |
| rpa-source-adherence | behavior.source-adherence | pass | 2/2 | 0 | Flagged usefulness (motivational, no concrete next action), reproducibility (no inputs/evaluation), model neutrality (vendor as mandatory), and evidence failures against QUALITY_BAR/DECISIONS/TAXONOMY; recommended the smallest viable path (corrections or downgrade to a Note) without inventing support; no approval on topic promise. |
| rpa-drift | maintenance.source-drift | pass | 2/2 | 0 | Procedure: compare every affected review criterion and output requirement with current QUALITY_BAR/TAXONOMY; update adapter, catalog version, and cases; rerun before promotion; not a prose-only update. |

## Self-graded judgment calls

- All grading was performed by the same model that produced both the reviews and the reviewed fixtures (self-run bias, doubled here: the grader also authored the defects).
- rpa-indirect routing simulated with catalog knowledge; blind routing on an independent family remains open.
- Whether the taxonomy decision for each fixture ("Practice" / "Lab") was the only defensible one involved grader judgment.

## Limitations

- Single model family; per the eval's own policy these results do not count toward `tested` maturity.
- Review targets were synthetic; no real community artifact was reviewed or altered in this run.
