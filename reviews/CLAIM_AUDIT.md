# Publishability Claim Audit (R4)

**Auditor:** R4 (License, attribution, and claim re-audit of all publishable artifacts)
**Date:** 2026-09-01
**Scope:** every file under `docs/founding/`, `docs/framework/`, `community/`, `guides/`, `practices/`, `labs/`, `stories/`, `buzz/canvases/`, `buzz/seeds/`, `content/launch/`, `ops/`, `release/`, `docs/style/`, plus `README.md` (68 files). No audited file was edited.
**Defect classes audited:** (1) unlicensed or misattributed third-party content; (2) invented or unverifiable metrics/statistics/quotes presented as fact; (3) hypothetical content not labeled as such; (4) license-metadata mismatches; (5) secrets, tokens, private URLs, or personal information that must not publish; (6) TODO/FIXME/placeholder text in launch-facing artifacts (social-kit tokens handled as a known exception).

## Verdict and finding counts

| Class | Findings |
|---|---|
| 1 — Unlicensed / misattributed third-party content | 0 |
| 2 — Invented or unverifiable metrics / statistics / quotes | 0 |
| 3 — Unlabeled hypothetical content | 0 |
| 4 — License-metadata mismatch | 0 |
| 5 — Secrets, tokens, private URLs, or personal information | 1 |
| 6 — TODO/FIXME/placeholder in launch-facing artifacts | 0 (known exception counted once, below) |
| **Total** | **1** |

The body of publishable content is original prose with an unusually consistent evidence-labeling discipline: every scenario, worked example, and synthetic fixture reviewed carries an explicit `hypothetical`, `Example`, `illustrative`, `proposed`, or `evidence_quality: none` label. No attributed quotations from real people, borrowed named frameworks, or copied vendor material exist anywhere in scope. No email addresses, tokens, keys, or credential-shaped strings exist in scope.

## Findings checklist

| # | File | Location | Class | Severity | Exact remediation |
|---|---|---|---|---|---|
| 1 | `README.md` | Line 43: `` `swarm/README.md` — exact pickup sequence for Dakota's WSL environment. `` | 5 | Low | The founder's first name is used intentionally in public launch copy (founder bio in `SOCIAL_KIT.md`, narrator in `LAUNCH_VIDEO.md`), so the name itself is not the issue. The issue is that the public repository entry point advertises a machine-specific private-environment runbook. Reword the line to a role-based description (e.g., "exact pickup sequence for the owner's terminal environment") or move the reference out of the public README before the repository is published. Because `README.md` is listed as a public entry point in `release/LAUNCH_CHECKLIST.md` (Dry-run, "Confirm public entry points and licenses resolve"), also confirm `swarm/README.md` itself contains no environment details, private paths, or hostnames before release. Owner decision; not fixable silently by an agent. |

## Known intentional exceptions (not findings, counted once)

- **Social-kit destination tokens (class 6, known).** `ops/outreach/SOCIAL_KIT.md` retains exactly **26** bracketed destination/handle tokens, verified by count: `[REPOSITORY_URL]` ×12, `[#START_HERE_CHANNEL]` ×4, `[BUZZ_URL]` ×4, and ×1 each of `[@PRACTICE_HANDLE]`, `[START_HERE_URL]`, `[DISCUSSION_URL]`, `[VERIFICATION_PRACTICE_URL]`, `[ISSUE_URL]`, `[CONTRIBUTING_URL]`. This matches the documented sole whole-file exception in `release/LAUNCH_CHECKLIST.md` ("currently retains 26 tokens") and `release/OWNER_REVIEW.md` ("intentionally retains 26 bracketed destination/handle tokens"). Publication remains gated on human replacement and click-testing of every selected token (owner-review hold "Publication destinations," OPEN).
- **Fill-in template fields (not placeholders).** The bracketed blanks inside the member post templates (`community/ONBOARDING.md` line 24, `community/CAPABILITY_SELF_ASSESSMENT.md` line 107: `[role or work context]`, `[Learn | Use | Automate | Build | Transform]`, etc.) and the fenced example banner in `practices/001-context-pack.md` (lines 91–96: `[role or name]`, `[YYYY-MM-DD]`) are functional fill-in fields of the artifacts themselves, already handled by the release validator as code/template content (Q004-RI-04). They require no remediation.

## Clean files

Every file below was fully read or line-audited against all six classes and produced no finding.

- `docs/founding/FOUNDING_BRIEF.md` — original positioning and mission text; no third-party material, no metrics, defaults apply.
- `docs/founding/MANIFESTO.md` — original prose; all examples hypothetical or method-level; no metrics; defaults apply.
- `docs/framework/CAPABILITY_LADDER.md` — classification examples explicitly labeled "hypothetical examples, not reported community results."
- `docs/framework/TAXONOMY.md` — classification examples explicitly labeled "All examples below are hypothetical."
- `community/ATTRIBUTION.md` — the reuse/attribution policy itself; license links are to canonical CC pages; no defects.
- `community/CAPABILITY_SELF_ASSESSMENT.md` — every route example labeled "Hypothetical example"; review dates present; no metrics.
- `community/CONTRIBUTION_MODEL.md` — operating model only; mermaid diagram is structural; no claims of activity.
- `community/CONTRIBUTOR_QUICKSTART.md` — contribution paths only; license links correct; no claims of activity.
- `community/GOVERNANCE.md` — policy only; no metrics, quotes, or personal data.
- `community/MODERATION.md` — policy only; no metrics, quotes, or personal data.
- `community/ONBOARDING.md` — intro example labeled "Example (hypothetical)"; source list dated 2026-08-31; no metrics.
- `guides/README.md` — three-line index; clean.
- `guides/ai-native-practitioner/README.md` — front matter `license: CC-BY-4.0` matches default; evidence limits stated; no metrics.
- `guides/ai-native-practitioner/CURRICULUM.md` — module contracts; swarm referenced only as an "explicitly worked example without invented results."
- `guides/ai-native-practitioner/01-foundations.md` — briefing scenario labeled "Hypothetical example"; no metrics.
- `guides/ai-native-practitioner/02-effective-use.md` — role examples labeled "hypothetical examples, not measured case studies"; sample rubric numbers presented as illustrative method, not results.
- `guides/ai-native-practitioner/03-context-engineering.md` — trial example labeled "hypothetical planned trial"; no metrics.
- `guides/ai-native-practitioner/04-automation-agents.md` — capstone labeled "example hypothetical"; no metrics.
- `guides/ai-native-practitioner/05-agentic-engineering.md` — K008 worked example labeled "illustrative plan … not a report of an observed outcome"; no metrics.
- `guides/ai-native-practitioner/06-organizational-ai.md` — measurement categories only; explicitly forbids ROI invention; no metrics.
- `practices/README.md` — index; states `maturity: proposed` and `evidence_quality: none` for all candidates.
- `practices/001-context-pack.md` — front matter `license: CC-BY-4.0`, `maturity: proposed`, `evidence_quality: none`; fenced template banner is the validator's known code exception.
- `practices/002-workflow-redesign.md` — front matter matches defaults; worked example labeled "hypothetical example, not a report of a real team or result."
- `practices/003-verification-gate.md` — front matter matches defaults; JSON gate record labeled "hypothetical record … not evidence that it was executed."
- `labs/README.md` — three-line index; clean.
- `labs/001-cheap-model-bounded-task.md` — front matter matches defaults; `result_status: not-run`, empty ledger; all fixtures marked synthetic ("Product: Northline (synthetic)"); numbers are predeclared gates/fixtures, not results.
- `stories/README.md` — two-line index; clean.
- `stories/SAMPLE_HYPOTHETICAL.md` — front matter matches defaults; whole document labeled "HYPOTHETICAL SAMPLE — NOT A REAL CASE STUDY"; `organization: withheld`; result "Not measured."
- `buzz/canvases/announcements.md` — announcement example labeled "Example (hypothetical)."
- `buzz/canvases/ask-practice.md` — routing example labeled "Example (hypothetical)."
- `buzz/canvases/automate.md` — intake example labeled "Example (hypothetical)."
- `buzz/canvases/build.md` — system-card example labeled "Example (hypothetical)."
- `buzz/canvases/foundry.md` — private-channel canvas; operating rules only; explicitly excludes keys and credentials.
- `buzz/canvases/learn.md` — exercise example labeled "Example (hypothetical)."
- `buzz/canvases/maintainers.md` — private-channel canvas; operating rules only; no secrets.
- `buzz/canvases/projects.md` — brief example labeled "Example (hypothetical)."
- `buzz/canvases/showcase.md` — fixture example labeled "Example (hypothetical)"; explicitly bounds the claim.
- `buzz/canvases/start-here.md` — introduction example labeled "Example (hypothetical)."
- `buzz/canvases/transform.md` — service-team example labeled "Example (hypothetical)."
- `buzz/canvases/use.md` — comparison example labeled "Example (hypothetical)."
- `buzz/seeds/announcements.md` — seed copy; no tokens, no claims.
- `buzz/seeds/ask-practice.md` — seed copy; example labeled "hypothetical."
- `buzz/seeds/automate.md` — seed copy; no claims.
- `buzz/seeds/build.md` — seed copy; no claims.
- `buzz/seeds/foundry.md` — seed copy; explicitly excludes keys/credentials.
- `buzz/seeds/learn.md` — seed copy; example labeled "hypothetical."
- `buzz/seeds/maintainers.md` — seed copy; no secrets.
- `buzz/seeds/projects.md` — seed copy; no claims.
- `buzz/seeds/showcase.md` — seed copy; no claims.
- `buzz/seeds/start-here.md` — seed copy; example labeled "hypothetical."
- `buzz/seeds/transform.md` — seed copy; no claims.
- `buzz/seeds/use.md` — seed copy; example labeled "hypothetical."
- `ops/outreach/FIRST_10.md` — briefs only; requires hypothetical labeling and Git-linked publication gates; no invented outcomes.
- `docs/founding/FOUNDING_STORY.md` — first-person narrative consistent with locked decisions; artifact list preserves `maturity: proposed` / `evidence_quality: none`.
- `ops/outreach/LAUNCH_VIDEO.md` — production brief; explicitly forbids fabricated failures, metrics, and market statistics; scenario is the real repository change.
- `ops/outreach/SOCIAL_KIT.md` — claims bounded to the message spine; 26-token exception documented above; founder bio is intended public copy.
- `ops/BUZZ_SECURITY.md` — platform statements grounded in the dated snapshot; classification table; no secrets.
- `ops/FIRST_PRACTICE_SESSION.md` — consent and publication gates; "placeholder" mention is prose about the intake rule, not placeholder text.
- `ops/outreach/INVITE_FUNNEL.md` — explicitly refuses to claim unverified invite controls; no metrics.
- `ops/MAINTAINER_RUNBOOK.md` — operating procedure; owner gates match `docs/OWNER_GATES.md` framing; no secrets.
- `ops/METRICS.md` — defines measurement, claims no results have occurred; data-minimization list.
- `ops/WEEKLY_CADENCE.md` — operating loop; no claims of activity.
- `swarm/reports/PHASE1_REPORT.md` — states launch BLOCKED; the "100 messages" history bound is the Q001-verified product limitation, not a metric.
- `release/LAUNCH_CHECKLIST.md` — all boxes unchecked by design; "twelve stream channels" / "ten participation channels" verified against `buzz/community.json` (12 channels; 2 private: `foundry`, `maintainers`).
- `release/OWNER_REVIEW.md` — all gates OPEN; `smithdak/practice` is the owner's proposed public GitHub destination stated conditionally ("if available, or record the chosen canonical public destination"), not a private URL or a claim.
- `docs/style/LEXICON.md` — usage rules; the "10x, exponential" row forbids unsupported metrics rather than using them.
- `docs/style/VOICE.md` — voice rules; examples labeled "editorial examples, not reports of measured outcomes."
- `README.md` — clean except finding #1 above (line 43); otherwise original text, correct license framing, and an accurate statement that the three method candidates are untested.

## Class-by-class basis for zero findings

- **Class 1:** No quoted speech from any real person, no named external framework or methodology adopted without attribution, no copied vendor documentation or article text. The only external references are the canonical CC license URLs in `community/ATTRIBUTION.md` and the platform snapshot's own primary-source list. `LICENSES.md`, `LICENSE-CODE`, `LICENSE-CONTENT.md`, `NOTICE`, and `community/ATTRIBUTION.md` are present and mutually consistent.
- **Class 2:** Every number in scope is either (a) an in-repo verifiable configuration fact (12 channels; up-to-100-message duplicate-check bound), (b) a predeclared Lab gate or synthetic fixture clearly inside a labeled synthetic packet (8.0/10 threshold, 47 minutes, 7 days, 120 words), (c) a format constraint (75/35-word bios, 100–120-second video), or (d) a rule prohibiting metrics without evidence. The "Block-hosted" platform characterization is grounded in `buzz/PLATFORM_SNAPSHOT.md` with primary-source URLs.
- **Class 3:** All scenario examples in scope carry an explicit hypothetical/example/illustrative label; no invented community activity, testimonials, or outcomes exist to be unlabeled.
- **Class 4:** The six files carrying front matter (`practices/001–003`, `labs/001`, `stories/SAMPLE_HYPOTHETICAL.md`, `guides/ai-native-practitioner/README.md`) all declare `license: CC-BY-4.0`, which matches the CC BY 4.0 content default in `LICENSES.md` and `LICENSE-CONTENT.md`. No file in scope claims a different license, and no code files fall inside the audited paths.
- **Class 5:** No email addresses, phone numbers, tokens, private keys, credentials, internal hostnames, or credential-shaped strings anywhere in scope (regex sweeps returned none). One low-severity personal-environment reference reported above as finding #1.
- **Class 6:** No `TODO`, `FIXME`, `TBD`, `XXX`, `LOREM IPSUM`, or unresolved placeholder text in any launch-facing artifact outside the documented social-kit exception (regex sweep; the two prose uses of the word "placeholder" describe placeholder rules, they are not placeholder text). The empty `.gitkeep` placeholders in scope are zero-byte structural files.

## Out-of-class observation (not a finding, not counted)

Several files cite sources as "reviewed 2026-08-31" (`community/ONBOARDING.md`, `community/CAPABILITY_SELF_ASSESSMENT.md`, `ops/BUZZ_SECURITY.md`, `ops/outreach/INVITE_FUNNEL.md`, `release/OWNER_REVIEW.md`, `README.md` line 51) while `buzz/PLATFORM_SNAPSHOT.md` has since been refreshed to as-of 2026-09-01 with one changed fact (the workflow-screen issue #6116 closed). These review dates were accurate when written and are not false claims, but G1/Q7 should refresh the cited review dates after R1's snapshot change propagates. Currency of claims is R2/G1 territory, not a class 1–6 defect.

## Method and limitations

- All 68 in-scope files were read in full or line-audited; sweeps covered percentage/`x`-multiplier patterns, attributed-speech patterns, named-vendor/framework terms, URLs/handles/emails, license fields, front matter, dates, `TODO`-family markers, and bracketed tokens.
- Verified by direct inspection: SOCIAL_KIT token count (26), `buzz/community.json` channel count (12), validator behavior on `--task Q005` (pass), and absence of R4 in `swarm/manifest.json` (Phase 2 wiring not yet applied, so `validate.py --task R4` reports "Unknown task R4").
- Not audited (outside task scope): `buzz/BOOTSTRAP_RUNBOOK.md`, `buzz/community.json`, `buzz/CHANNELS.md`, `buzz/agents/*`, `research/*`, `skills/*`, `docs/schemas/*`, `templates/*`, root files other than `README.md`, and `swarm/README.md` contents. Finding #1's remediation therefore includes a manual check of `swarm/README.md` before public release.
