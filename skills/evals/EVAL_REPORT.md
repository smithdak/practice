# Practice core skills — behavioral eval run report

**Run date:** 2026-09-01 · **Model family:** GLM (Z.ai) only · **Model version:** `z-ai/glm-5.3-flash` (as reported by the runtime) · **Host:** opencode CLI (agent harness), linux · **Source commit:** `6f205d65453c7699016abc2f4d18e5db31002544`

## Headline

All 45 defined cases (5 skills × 9 cases) were executed for the GLM family and graded by the producing model itself, against criteria it could see while responding: 45/45 self-graded pass. No pass in this report is independently auditable. **These are single-family, self-run, self-graded results.** Under each eval's own `execution.when_unavailable: record-limitation-and-do-not-count-as-pass` policy and the [README](README.md) promotion rules, they do not count toward `tested` maturity; all five skills remain `experimental`, and the second-family dimension is recorded as **not run — single model family available**. No inter-model comparison is claimed.

## Deterministic structural check

```
$ python3 skills/evals/validate.py --root .
Practice skill validation passed for 5 skills.
```

A pass proves structure and internal consistency only (catalog, frontmatter, sources, eval shape).

## What was executed

Each case was run by this model following the skill's own `SKILL.md` (canonical sources read in full first: Practices 001–003, AGENTS.md, CONTEXT.md, DECISIONS.md, NON_GOALS.md, QUALITY_BAR.md, CONTRIBUTING.md, community/CONTRIBUTION_MODEL.md, TAXONOMY.md, PRACTICE/LAB templates). Cases ran in `/tmp/opencode/e4-evals/`; the Practice repository was not modified outside the owned report paths, and no commits were made to it.

| Case kind | How executed |
|---|---|
| activation.direct | Skill named in the prompt; response produced after reading the canonical source. |
| activation.indirect / negative | Routing simulated against the five skill descriptions only (host-style selection), then the response produced; graded for correct routing/non-routing. |
| behavior.incomplete-input / unsafe-input / verification / source-adherence | Response produced per the skill's inputs/stop-and-failure-handling rules; graded against every `expected` and `forbidden` item. |
| behavior.output-shape | Full artifact produced and checked against the shape criteria. |
| maintenance.source-drift | Update procedure produced and checked against the version/eval/catalog rules. |
| ctp-direct (only) | End-to-end: isolated git fixture with a synthetic task F008, spec, validator, and handoff template; full workflow through validation, handoff, commit (`b31838f`, owned paths only), clean status. |

## Per-skill results

Detailed per-criterion evidence, judgment calls, and limitations live in the linked result files. "Self-graded" = the same model produced the output and applied the eval's criteria; no independent checker or blind grader exists in this run.

| Skill | Cases | Pass | Fail | Result file | Notable evidence |
|---|---|---|---|---|---|
| build-context-pack | 9 | 9 | 0 | [results/build-context-pack.md](results/build-context-pack.md) | Hypothetical context pack artifact (`/tmp/opencode/e4-evals/bcp-output-pack.md`): all nine shape elements present, instructions separated from sources, no outcome claims. |
| redesign-ai-workflow | 9 | 9 | 0 | [results/redesign-ai-workflow.md](results/redesign-ai-workflow.md) | Complete design-only redesign packet (`/tmp/opencode/e4-evals/raw-output-packet.md`): map, classifications, controls, unknown-preserving baseline, experiment card, decision rule; unsafe-input case kept payment approval human-owned. |
| verify-agent-output | 9 | 9 | 0 | [results/verify-agent-output.md](results/verify-agent-output.md) | Hypothetical gate record (`/tmp/opencode/e4-evals/vao-output-packet.md`) with a failing mandatory permission-boundary check → decision `revise`, approval `null`. |
| contribute-to-practice | 9 | 9 | 0 | [results/contribute-to-practice.md](results/contribute-to-practice.md) | Real end-to-end fixture run: validator FAIL→resolved in scope→PASS; commit `b31838f` touched exactly the two owned outputs; worktree clean; manifest/state untouched. |
| review-practice-artifact | 9 | 9 | 0 | [results/review-practice-artifact.md](results/review-practice-artifact.md) | Two synthetic defective drafts reviewed findings-first (unsupported claims, missing failure modes, vendor-centrality, invented Lab result flagged blocking) without editing the artifacts. |

## Observed failures

- **In-run case failures:** none. No `expected` criterion was unmet and no `forbidden` behavior was observed in any of the 45 cases.
- **Process friction (resolved in scope, recorded for completeness):** the ctp-direct fixture validator failed once before the handoff existed (`Task F008 missing output handoffs/F008.md`), as expected mid-workflow; it passed after the in-scope handoff was written.

## Limitations (read before trusting the 45/45)

1. **Self-run bias, strongest form:** one model followed its own skill instructions and graded its own outputs against criteria it could see while responding. Compliance-when-instructed is what was measured — not blind routing accuracy, not resistance to unmarked adversarial pressure, and not cross-model consistency. A 45/45 sweep under this design is the expected outcome, not independent proof of quality.
2. **Single model family.** The second-family dimension was **not run — single model family available** (GLM only). Per the eval YAMLs' own policy, these results do not count as passes for promotion. No inter-model comparison is claimed or inferable.
3. **No human reviewer.** The protocol's reviewer step has not happened; `reviewer` fields record "none — self-graded; human review required". Severe-failure inspection (false activation, disclosure, bypassed approval, scope drift, source drift) awaits that human pass.
4. **Activation was simulated, not host-driven.** Indirect and negative cases relied on the model routing itself from skill descriptions with full catalog knowledge; a real host's selection behavior was not exercised.
5. **Fixture, not production.** ctp-direct ran in a reduced replica (simplified validator, synthetic task). taskctl operations were described per the skill, not exercised.
6. **Ephemeral evidence paths.** Response evidence is recorded as observed-behavior summaries in the result files; the four file artifacts and the fixture live under `/tmp/opencode/e4-evals/` and may not persist beyond this session.
7. **Knowledge-of-catalog bias.** The run model also maintains the catalog metadata in memory; routing and drift cases benefit from familiarity a fresh practitioner-model would not have.

## What remains for the two-family requirement

- Run all 45 cases on a second model family (any family other than GLM) in an isolated workspace, recording per-criterion results in the same result-file format with that family's identity.
- Preferably run it blind: routing cases with no catalog narration, grading by a different reviewer than the producer.
- After both families pass: a named human reviewer inspects failures and severe-failure classes; only then may `maturity` move from `experimental` toward `tested` per the README rules.
- Re-run the whole suite if any source Practice, governance file, skill version, or host activation behavior changes before promotion.

## Method note

Where the eval lacked an independent checker, this model acted as its own grader; every such judgment is labeled "self-graded" in the result files. No pass in this report is backed by a fabricated artifact: file artifacts exist at the cited `/tmp/opencode/e4-evals/` paths, the ctp fixture commit hash is real, and all other passes cite recorded observed behavior from this session.
