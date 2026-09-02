# Labs

A Lab is a reproducible experiment or evaluation that answers one bounded question under stated conditions, recording the setup, task set, procedure, results, and limitations so another Practitioner can inspect or repeat it ([TAXONOMY.md](../docs/framework/TAXONOMY.md)). A Lab can be inconclusive, and it does not establish a general ranking of models, people, tools, or organizations.

## What exists

Each file's front matter carries its `status`, `run_count`, and `result_status`; this index does not restate them. A recorded trial does not change the maturity of the method it trials: every method in [../practices/](../practices/README.md) remains `maturity: proposed`, and promotion is a separate human decision.

| Lab | Question it answers | Method it trials |
|---|---|---|
| [001-cheap-model-bounded-task.md](001-cheap-model-bounded-task.md) | Under fixed conditions, which eligible low-cost model configurations, if any, meet predeclared quality and cost gates on three synthetic, bounded artifact tasks? | None. A proposed evaluation design; its front matter records whether it has run. |
| [002-context-pack-trial.md](002-context-pack-trial.md) | Does a context pack built per the proposed Practice 001 method let an authorized agent-operator run the nine launch dry-run repository checks and produce a non-secret evidence summary? | [Practice 001, context pack](../practices/001-context-pack.md) |
| [003-workflow-redesign-trial.md](003-workflow-redesign-trial.md) | Can the six-class claim audit be split into deterministic, AI-assisted, and human-owned steps, and how does a stdlib checker compare with the recorded manual verdicts on two defect classes? | [Practice 002, workflow redesign](../practices/002-workflow-redesign.md) |
| [004-verification-gate-trial.md](004-verification-gate-trial.md) | What does the verification gate find when applied end to end to one real committed code change, and does the rollback it requires work when rehearsed? | [Practice 003, verification gate](../practices/003-verification-gate.md) |

## Add one

| Step | Open |
|---|---|
| Frame it | [lab.yml](../.github/ISSUE_TEMPLATE/lab.yml) issue form |
| Write it | [LAB.md](../templates/LAB.md) template |
| Check it | [LAB_SCHEMA.md](../docs/schemas/LAB_SCHEMA.md); `python3 scripts/validate_artifacts.py` validates every `labs/*.md` except this index |
| Submit it | [../CONTRIBUTING.md](../CONTRIBUTING.md), "Guide, Lab, or Story" path |

Name files `NNN-slug.md`, as the four above are. Label proposed or example results as such; do not invent outcomes.
