# Guide Currency Audit (R2)

As-of date: **2026-09-01**. Auditor: R2 (Phase 2, Wave R).

## Scope and method

Audited every published file in `guides/ai-native-practitioner/` (6 modules + CURRICULUM.md + README.md), `practices/*.md`, `labs/*.md`, `stories/*.md`, and `buzz/agents/*.md` — 21 files. This is a read-and-audit task; no target file was edited. Corrections are proposals for G1.

Checks applied to each file:

1. Search for stale or unsourced technical claims: model names, tool versions, product capabilities, prices, limits, dates.
2. Search for claims that need an as-of date and lack one (including repo-state claims such as "remains `maturity: proposed`").
3. Search for tool-specific statements that conflict with the model-agnostic posture (docs/DECISIONS.md; docs/QUALITY_BAR.md "Model-agnostic").
4. Search for unlabeled examples that read as fact.

Cross-reference claims were machine-verified against repo sources at HEAD: `swarm/manifest.json` (K008 contract), `swarm/specs/K008.md`, `buzz/community.json` (channel names/visibility), `docs/schemas/GUIDE_SCHEMA.md`, `docs/schemas/PRACTICE_SCHEMA.md`, `docs/schemas/STORY_SCHEMA.md`, `templates/`, and `docs/framework/`.

## Headline result

**Zero blockers. No stale, unsourced, or vendor-specific technical claim exists anywhere in the audited corpus.** A full-text sweep found no model or brand names (GPT, Claude, Gemini, Llama, OpenAI, Anthropic, LangChain, etc.), no version pins, no prices, no rate limits, and no product-capability assertions. Every hypothetical example found is explicitly labeled. The writing contracts in docs/QUALITY_BAR.md and the curriculum's downstream artifact contracts did their job.

All flagged findings are currency-maintenance risks (claims that will silently rot) or one-line wording refinements: 2 should-fix, 4 note.

## Per-file coverage

| File | Checkable claims examined | Findings |
|---|---:|---:|
| guides/ai-native-practitioner/README.md | 12 | 1 |
| guides/ai-native-practitioner/CURRICULUM.md | 14 | 1 |
| guides/ai-native-practitioner/01-foundations.md | 3 | 0 |
| guides/ai-native-practitioner/02-effective-use.md | 3 | 0 |
| guides/ai-native-practitioner/03-context-engineering.md | 3 | 0 |
| guides/ai-native-practitioner/04-automation-agents.md | 4 | 0 |
| guides/ai-native-practitioner/05-agentic-engineering.md | 10 | 1 |
| guides/ai-native-practitioner/06-organizational-ai.md | 3 | 0 |
| practices/001-context-pack.md | 4 | 1 |
| practices/002-workflow-redesign.md | 3 | 0 |
| practices/003-verification-gate.md | 3 | 0 |
| practices/README.md | 3 | 1 |
| labs/001-cheap-model-bounded-task.md | 7 | 1 |
| labs/README.md | 1 | 0 |
| stories/README.md | 1 | 0 |
| stories/SAMPLE_HYPOTHETICAL.md | 2 | 0 |
| buzz/agents/GUIDE_MAINTAINER.md | 5 | 0 |
| buzz/agents/LIBRARIAN.md | 9 | 0 |
| buzz/agents/RELEASE_EDITOR.md | 2 | 0 |
| buzz/agents/RESEARCH_AUDITOR.md | 2 | 0 |
| buzz/agents/STEWARD.md | 5 | 1 |

Claims audited: 97. Flagged: 6 findings (2 should-fix, 4 note) across 7 files. Findings marked "verified clean" were checked and are correct as of this audit; they are listed only where they will need re-verification.

## Findings

### guides/ai-native-practitioner/README.md

| Location | Claim | Issue type | Severity | Proposed correction |
|---|---|---|---|---|
| README.md:95 ("Module 1 — Methods"), 119 ("Module 3 — Methods"), and the same pattern at 107, 131, 143, 155 | Prose restates Practice maturity: "it remains `maturity: proposed`" / "its publication as a candidate does not make it tested" | Needs as-of; will silently rot on promotion | Should-fix | Do not restate the label in prose; defer to the artifact: "Use the Verification Gate at its current front-matter maturity label." If prose must keep a state statement, add "as of 2026-08" and a review trigger. Add to the review-trigger list at README.md:215: "a referenced Practice's maturity label changes" — the current trigger ("changes materially") may not be read to cover a promotion alone. |

Why it matters: Wave E runs the three trials and E5 assembles promotion packets; a human promotion decision is the expected next event for these Practices. When front matter flips to `tested`, these six sentences become false with nothing in the Guide's own maintenance contract forcing their update.

### guides/ai-native-practitioner/CURRICULUM.md

| Location | Claim | Issue type | Severity | Proposed correction |
|---|---|---|---|---|
| CURRICULUM.md:15–16 ("The linked methods are proposed candidates, not tested Practices"), :199 ("It is available for trial but is not a tested Practice"), :248, :299, :350 ("Both remain candidates pending evidence") | Same undated maturity restatements as the README, plus the map-level assertion | Needs as-of; will silently rot on promotion | Should-fix | Same fix as README: reference the artifact's current label instead of restating it ("see that artifact's `maturity` field"), or add an as-of date. At minimum, G1 must add "re-verify all 'proposed / not tested' statements against front matter" to the module-author maintenance contract at CURRICULUM.md:497–507. |

Note: CURRICULUM.md:107 ("must not depend on a current vendor-specific product claim") and the module-by-module contracts at :199–:352 were checked against the actual module files; the modules satisfy their contracts. That is coherence, not currency — G1's existing job.

### guides/ai-native-practitioner/05-agentic-engineering.md

| Location | Claim | Issue type | Severity | Proposed correction |
|---|---|---|---|---|
| 05-agentic-engineering.md:224–234 ("Worked example — a bounded Practice swarm task") | Hard-codes the K008 task contract: "declared owned outputs are one module file and one handoff"; "the task contract also requires a repository validator, a commit, and a clean worktree"; author "does not edit the curriculum map, task manifest, or another worker's handoff" | Repo-state claim, mutable source; needs re-verification anchor | Note (verified correct today) | All four assertions match `swarm/manifest.json` (K008 `outputs`, `handoff`), `swarm/specs/K008.md:42` (validator), and AGENTS.md completion rules as of 2026-09-01. The example is correctly labeled "illustrative plan … not a report of an observed outcome." G1 should re-check the manifest at publish time and consider pinning "(task contract as of 2026-08)" after "K008 task contract" at line 224. |

### practices/001-context-pack.md (pattern applies to 002 and 003)

| Location | Claim | Issue type | Severity | Proposed correction |
|---|---|---|---|---|
| practices/001-context-pack.md:130 ("This repository contains the method and a planned trial only"), practices/002-workflow-redesign.md:143, practices/003-verification-gate.md:163 | Evidence-section repo-state claims: no completed trial exists | Needs as-of; stale the moment a trial Lab lands | Note | These sections must be revised in the same task that records a trial (E1–E3) — the promotion flow in PRACTICE_SCHEMA.md already forces this, and A1's validator flags tested-maturity claims without trial records. No edit needed now; flagging so the E-wave owners know the sentence is load-bearing. |

### practices/README.md

| Location | Claim | Issue type | Severity | Proposed correction |
|---|---|---|---|---|
| practices/README.md:3–5 ("Each currently has `maturity: proposed` and `evidence_quality: none`; none is represented as a tested Practice yet") | Undated maturity restatement | Needs as-of; will silently rot on promotion | Should-fix | Same fix family as the guide: "Check each artifact's front-matter `maturity` label; none had passed a recorded trial as of 2026-08-31." This file is outside G1's owned paths (`guides/ai-native-practitioner/**`) — route to the integrator or practices owner. |

### labs/001-cheap-model-bounded-task.md

| Location | Claim | Issue type | Severity | Proposed correction |
|---|---|---|---|---|
| labs/001-cheap-model-bounded-task.md:202 ("Convert a published per-million-token price to per-token before calculation") | States the token-conversion step unconditionally, implying per-token billing is the default published basis | Technical-convention claim that varies by provider | Note | The surrounding fields already handle this ("Price basis: input, output, cached-input, batch, request, or other applicable unit price", line 189). Reword: "When the recorded price basis is per-million tokens, convert to per-token; otherwise compute from the recorded basis directly." Outside G1's paths; route to the labs owner (E-wave) or integrator. |

The Lab's currency hygiene is otherwise exemplary: pricing requires a provider URL and UTC as-of date (lines 47, 140, 187–189), the run ledger forces snapshot capture, and Limitations (line 241) explicitly warns that providers change pricing and behavior after the run date. `result_status: not-run` and `last_run: null` match the empty Results tables.

### buzz/agents/STEWARD.md

| Location | Claim | Issue type | Severity | Proposed correction |
|---|---|---|---|---|
| STEWARD.md:109–111 ("Initial membership is limited to `start-here`, `ask-practice`, `learn`, `use`, `automate`, `build`, and `transform`. It has no membership in `foundry`, `maintainers`, `announcements`, `projects`, or `showcase`") | Channel-name and membership claims | Plan statement, not yet a platform fact; cannot be verified until the owner-operated apply | Note | The two channel lists are exhaustive and correct against `buzz/community.json` (12 channels, 7 open + 5 excluded) as of 2026-09-01. The profile already fails closed when reality diverges. O3's hosted-surface inspection should confirm the applied membership matches this list; no edit needed. The same applies to the capability-ladder claim at STEWARD.md:31 (matches docs/DECISIONS.md). |

### Files with zero findings

`01-foundations.md`, `02-effective-use.md`, `03-context-engineering.md`, `04-automation-agents.md`, `06-organizational-ai.md`, `practices/002-workflow-redesign.md` (beyond the shared pattern above), `practices/003-verification-gate.md` (same), `labs/README.md`, `stories/README.md`, `stories/SAMPLE_HYPOTHETICAL.md`, `buzz/agents/GUIDE_MAINTAINER.md`, `buzz/agents/LIBRARIAN.md`, `buzz/agents/RELEASE_EDITOR.md`, `buzz/agents/RESEARCH_AUDITOR.md`.

Cross-reference claims verified clean in these files, worth recording so G1 does not re-litigate them:

- `GUIDE_MAINTAINER.md:110` cites GUIDE_SCHEMA.md's "Status and versioning" section (exists, line 63) and the `last_verified` field semantics (GUIDE_MAINTAINER.md:136–138 matches GUIDE_SCHEMA.md:73).
- `LIBRARIAN.md:145–148` template/schema paths all exist (`templates/PRACTICE.md`, `GUIDE.md`, `LAB.md`, `STORY.md`; the four schemas). `LIBRARIAN.md:149–151` correctly refuses to invent Note/Project/Issue/Decision templates that do not exist yet (G2 will add them).
- `LIBRARIAN.md:134` evidence-level vocabulary (`none | single-run | repeated | independently-reproduced`) matches PRACTICE_SCHEMA.md:87–90 and STORY_SCHEMA.md:49–54.
- `RELEASE_EDITOR.md` and `RESEARCH_AUDITOR.md` contain no platform- or product-specific claims; their "Buzz thread" and methodology references are generic and current.
- `SAMPLE_HYPOTHETICAL.md` front matter (`status: draft`, `evidence_quality: none`, `organization: withheld`) matches STORY_SCHEMA.md:71 and :16 exactly; every section carries an explicit hypothetical/illustrative/not-measured label.

## Issue-type summary

1. Stale or unsourced technical claims: **0 found.** No model names, tool versions, prices, limits, or product-capability assertions exist in the corpus.
2. Claims needing an as-of date: **4 found** (maturity restatements in the guide README and curriculum map, practices/README, the K008 contract citation). Two are should-fix; two are notes with verified-today status.
3. Model-agnostic violations: **0 found.** The only named tools are "Git worktree" (05-agentic-engineering.md:135, presented as "one way" with named equivalents — allowed as an example by docs/QUALITY_BAR.md) and Buzz channel names in agent profiles (correctly scoped to their own platform context).
4. Unlabeled examples: **0 found.** All 12+ hypothetical examples across the corpus carry explicit labels ("hypothetical", "illustrative", "synthetic", "not a report of an observed outcome").

## Prioritized fix list for G1

G1 owns `guides/ai-native-practitioner/**` only. Items outside that path are listed for routing, not for G1 to edit.

1. **Should-fix — de-prose the maturity labels (README.md:95/107/119/131/143/155 and CURRICULUM.md:15–16/199/248/299/350).** Replace "remains `maturity: proposed`"-style restatements with pointers to each artifact's front-matter label. If a state sentence is kept, date it. This is the only finding in G1's scope that can publish a false statement after Wave E completes.
2. **Should-fix — extend the review triggers.** Add "a referenced Practice's maturity label changes" to README.md:215 and to the module-author maintenance contract (CURRICULUM.md:497–507), so a promotion forces a guide pass rather than relying on "changes materially" being read broadly.
3. **Note — re-verify the K008 worked example (05-agentic-engineering.md:224–234) against `swarm/manifest.json` at publish time.** Accurate as of 2026-09-01; it hard-codes a mutable contract. Optionally pin "(as of 2026-08)" after "K008 task contract".
4. **Route to integrator/practices owner:** practices/README.md:3–5 maturity restatement (same fix as item 1).
5. **Route to labs owner (E-wave) or integrator:** labs/001:202 price-basis rewording (one line).
6. **Route to O3:** confirm applied STEWARD membership matches STEWARD.md:109–111 during the hosted-surface inspection; re-check agent-profile capability claims against R1's refreshed `buzz/PLATFORM_SNAPSHOT.md`.

## Risks

- The audit's clean result depends on the corpus staying generic. The first vendor-specific pull request (a tool example, a pricing number, a context-window figure) reintroduces every risk class at once; the Guide Maintainer profile's source-verification requirements (buzz/agents/GUIDE_MAINTAINER.md:34–40) are the standing control.
- Promotion timing: findings 1–2 become live false statements the moment a Practice is promoted; if G1 merges before the promotion decision, the fix is preventive. If promotion lands first, the fix becomes a correction.
- This audit is repo-internal. R1's refreshed platform snapshot (running in parallel) is the authority for external Buzz claims; none of the audited files assert live platform capabilities beyond the generic ones flagged in the STEWARD note.
