# Practice Core Skills

Practice Core Skills turn a small number of canonical Practice methods into agent-executable workflows without creating a second source of truth. This is a post-launch Project; it is not part of the initial release critical path. All five initial skills are **experimental** until their behavioral evaluations have recorded passing evidence.

## System boundary

| Layer | Owns | Does not own |
|---|---|---|
| Practice | The canonical, human-readable method, its evidence, and its limits. | Host-specific activation or execution guidance. |
| Skill | Portable instructions that adapt one Practice or governance workflow to a user's task. | New policy, task state, or evidence that the source artifact does not contain. |
| Script | Deterministic validation or enforcement when instructions alone are insufficient. | Human judgment or an alternative workflow definition. |
| Plugin | Optional installation and distribution after a set of skills is proven. | The canonical source format or a launch dependency. |

As of **2026-08-31**, official OpenAI documentation says Codex discovers repository skills by scanning `.agents/skills` from the current working directory to the repository root. It also identifies the open Agent Skills format as the shared authoring format and plugins as a later distribution layer. See [Build skills](https://learn.chatgpt.com/docs/build-skills). Host behavior can change; re-check that primary source when discovery or packaging behavior matters.

Runtime skill directories stay flat under `.agents/skills/` so discovery does not depend on category nesting. The maintained [catalog](catalog.yaml) carries classification, provenance, maturity, environment, tool, and ownership metadata. Capability tags use the repository's controlled `learn`, `use`, `automate`, `build`, and `transform` values; they classify the outcome, not the Practitioner.

## Initial set

| Skill | Canonical source | Distribution intent |
|---|---|---|
| `build-context-pack` | Practice 001 | Public candidate after evidence supports promotion. |
| `redesign-ai-workflow` | Practice 002 | Public candidate after evidence supports promotion. |
| `verify-agent-output` | Practice 003 | Public candidate after evidence supports promotion. |
| `contribute-to-practice` | Repository contribution and swarm governance | Repository only. |
| `review-practice-artifact` | Quality Bar, locked scope, and artifact taxonomy | Repository only. |

An empty capability category is acceptable. Add a skill only after repeated work demonstrates a stable, reusable decision process that is not already covered by an existing skill or deterministic script.

## Use and authority

A compatible host may select a skill from its description or a user may invoke it explicitly, for example `$build-context-pack`. Read the selected `SKILL.md` and its named canonical source completely before acting. User intent, authorization boundaries, stronger domain controls, and repository instructions still apply.

The three public candidates are instruction-only and require no named tool; a host can return their artifact in conversation or write it using tools the user has authorized. Repository operations declare their minimum tools in the catalog. Environment entries describe intended format/runtime compatibility, not evidence that a model has passed the behavior suite.

For swarm work, `scripts/taskctl.py` remains authoritative for task state, worktrees, validation, and integration. A skill must call that mechanism when the operation is authorized; it must never reproduce task state, edit the manifest or state files directly, weaken acceptance criteria, or claim authority to merge.

## Version and maturity rules

Skill IDs and folder names are stable. Versions use semantic versioning:

- Patch: clarification that preserves activation, inputs, output contract, and source decisions.
- Minor: backward-compatible capability, case, or output addition.
- Major: changed trigger boundary, required input, safety rule, or output contract.

Maturity is evidence-based:

- `experimental`: the workflow and eval cases exist, but behavioral evidence is absent, incomplete, or has an unresolved severe failure.
- `tested`: required activation and behavior cases pass in recorded runs, including two model families where available, and the canonical source is current.
- `stable`: the tested skill has also been exercised in real Practice work, has a named human maintainer, has no unresolved severe activation or safety failure, and has passed review for its intended environments.

Do not promote from prose review or a structural validator alone. A model family that is unavailable must be recorded as a limitation; it is not a passing run.

## Evaluation and drift

Run the deterministic catalog and eval check:

```bash
python3 skills/evals/validate.py --root .
```

When the Codex skill creator is available, also run its `quick_validate.py` against every runtime skill. Then follow the [behavioral evaluation protocol](evals/README.md). It covers direct and indirect activation, nearby non-activation, incomplete and unsafe inputs, output shape, verification, source adherence, and source drift.

A material source Practice or governance change makes each linked skill review-due immediately. Before reuse or promotion, compare the source change with the skill's trigger, inputs, decisions, safety rules, and output; update the catalog version and evals together; then rerun the complete suite. `last_reviewed` is a review fact, not a freshness guarantee.

## Distribution, maintenance, and retirement

Exercise all five skills locally before packaging anything. Package only the stable public candidates, and only after a human approves the distribution boundary. The repository operations skills stay local unless governance separately approves a portable form that does not expose or override Practice-specific controls.

Review a skill when its source, host behavior, permissions, intended user, maintainer, or a severe eval result changes. Retire or replace it when its canonical workflow is retired, it duplicates a better maintained skill, it cannot activate safely and precisely, required tooling is no longer supported, or no human maintainer accepts responsibility. Retirement removes it from runtime discovery, marks the catalog record, and preserves prior evaluation evidence; it does not silently redirect the old ID to a materially different job.
