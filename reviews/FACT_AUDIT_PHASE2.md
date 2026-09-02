# Fact and currency re-audit V2 (Q7)

**Auditor:** Q7 (Wave Q, independent re-audit; did not produce the audited outputs)
**Date:** 2026-09-01
**Method:** Every claim below was re-verified by direct fetch of the cited primary source on 2026-09-01, or by reading the current repository file. Verdicts: **verified** (source matches the claim), **corrected** (claim misstates its source), **unverifiable** (source does not establish the claim). GitHub issue pages fetched as HTML do not always expose state-change timestamps, so open/closed states are recorded as of the fetch, matching R1's convention.

## 1. BUZZ_PLATFORM_SNAPSHOT — re-verification of the 2026-09-01 additions

All re-fetches succeeded. Every new claim R1 added, and the #6116 correction, match the cited primary sources as of 2026-09-01. **17 verified, 0 corrected, 0 unverifiable.**

| # | Snapshot claim | Source re-fetched | Verdict |
|---|---|---|---|
| 1 | Voice huddles exist; README still marks huddle lifecycle events as "being wired up" | https://github.com/block/buzz (README: "drop into voice huddles" under agent surface; "Huddle lifecycle events" listed under 🚧 Being wired up) | verified |
| 2 | `channels create --type` accepts only `stream` or `forum` | https://raw.githubusercontent.com/block/buzz/main/crates/buzz-cli/src/commands/channels.rs — `cmd_create_channel` rejects anything else: `--type must be 'stream' or 'forum'` | verified |
| 3 | `channels create --visibility` accepts only `open` or `private` | Same function: `--visibility must be 'open' or 'private'` | verified |
| 4 | A hosted account can create up to three communities | https://block.github.io/buzz/support.html — "Each account can currently create up to three communities" | verified |
| 5 | Block-hosted communities are open to ages 18 and over | Support page: "Buzz is open to groups and individuals aged 18 and over" | verified |
| 6 | Invite-only; a user cannot join by entering the relay URL without an invitation | Support page: "Block-hosted communities are invite-only … A user cannot join by entering the relay URL without an invitation" | verified |
| 7 | Hosted-community storage limits were not final | Support page: "Limits apply to how much data each relay can store, and the exact limits will be published when they are final" | verified |
| 8 | Community owners manage access and can remove users; Block handles service-wide rules | Support page: "Community owners can manage access and remove users from their communities"; Block "sets service-wide rules" | verified |
| 9 | Relays are not federated; a message stays on the relay where it was sent | Support page, verbatim | verified |
| 10 | Messages, DMs, and uploaded media in Block-hosted communities are not end-to-end encrypted | Support page, verbatim | verified |
| 11 | Issue #6116 is closed via linked PR #6168 | https://github.com/block/buzz/issues/6116 shows Closed, linked to https://github.com/block/buzz/pull/6168 (merged 2026-08-17, "Fixes #6116") | verified |
| 12 | #5611 open — scheduled workflows never fire (cron and interval); manual trigger works; run history empty | https://github.com/block/buzz/issues/5611, state Open, body matches (manual trigger works, run history empty after a proven manual run) | verified |
| 13 | #4864 open — `workflows delete` accepted but list/get still return it; update resurrects it | https://github.com/block/buzz/issues/4864, state Open (fix PR #4882 also open) | verified |
| 14 | #5043 open — `{{variable}}` renders literally in `send_message` despite declared inputs | https://github.com/block/buzz/issues/5043, state Open | verified |
| 15 | #5075 open — CLI root messages land as invisible stream events in forum channels | https://github.com/block/buzz/issues/5075, state Open (fix PR #5925 also open) | verified |
| 16 | #5268 open — agent mention gaps in forum subscriptions (kinds 45001/45003) | https://github.com/block/buzz/issues/5268, state Open (fix PR #5945 also open) | verified |
| 17 | No release since Buzz Desktop v0.5.20 (released 2026-08-26) | https://github.com/block/buzz/releases/latest serves desktop-v0.5.20, released 26 Aug 00:23 | verified |

Notes (no verdict change):

- PR #6168's own description says the workflow-listing implementation "landed through #6009" and that #6168 adds the regression test. The snapshot's wording — "closed via linked PR #6168" — is exactly what the issue page shows, so it stands. A future refresh may prefer "fixed by #6009/#6168."
- The open fix PRs #4882/#5925/#5945 attached to issues #4864/#5075/#5268 confirm R1's handoff note; if any merges before the owner-operated apply, the snapshot's exclusions need a refresh pass.

## 2. COMMUNITY_LANDSCAPE — spot-check (six sources re-fetched)

Six of the thirteen cited sources were re-fetched on 2026-09-01, chosen to cover every self-reported figure in the report. **All checked claims verified; no claim misstates its source; no self-reported figure is presented as independent fact.**

| Source re-fetched | Landscape claims checked | Verdict |
|---|---|---|
| https://www.langchain.com/community | Forum (forum.langchain.com), Slack, events calendar (lu.ma/langchain), Academy; Champions/Experts/Ambassadors programs; "over 3,500 contributors" | verified — all present; the 3,500 figure appears verbatim and is labeled self-reported in the landscape |
| https://github.com/run-llama/llama_index | Discord/Reddit/X/LinkedIn channels; starter package + `llama-index-core` with "over 300 integration packages" (LlamaHub); ~52k stars / 8.1k forks | verified — README states "over 300 LlamaIndex integration packages"; page displays 52.0k stars, 8.1k forks |
| https://ollama.com | "Trusted by more than 9M developers"; nav lists model search, docs, download, pricing; footer lists GitHub, Discord, X, meetups (lu.ma/ollama) | verified — headline verbatim; all surfaces present |
| https://mlops.community | "90,000+ developers" self-reported; meetups/conferences, virtual tech talks, podcast, weekly newsletter, workshops (learn.mlops.community), jobs board, sponsor wall | verified — headline verbatim and correctly labeled |
| https://aitinkerers.org | 126,425 members, 254 cities, 90-day counts for events/speakers/hackathons (all self-reported); "Bring working code, share what broke"; "Demos over decks"; Post-Training, One-Shot, Paper Club, jobs board, talent service | verified — all figures displayed on the page; both quoted phrases verbatim |
| https://block.github.io/buzz/support.html (landscape's Buzz grounding via the snapshot) | n/a — covered in section 1 | verified |

Findings:

1. **No self-reported figure is presented as independent fact.** All five self-reported numbers in the report (3,500; 52k/8.1k; 9M; 90,000+; 126,425/254) carry an explicit "self-reported / displayed on the page" label. Verified compliant.
2. **Minor source-internal inconsistency (not a landscape error):** the MLOps Community homepage displays both "90,000+ developers" (hero) and "over 70,000 AI and ML professionals" (lower section). The landscape quoted the headline figure accurately. If the report is ever reused, note that the source itself is inconsistent.
3. The landscape's own risk note stands: these are single-fetch snapshots. The AI Tinkerers counters (member/city/event counts) are live counters that change constantly; treat the 2026-09-01 figures as illustrative of scale, not as stable reference values.
4. r/LocalLLaMA was not re-attempted; the landscape already records it as not verified and excludes it from analysis, which is the honest treatment.

## 3. Files still citing the snapshot at "reviewed 2026-08-31"

R4's out-of-class observation listed six files. **All six still carry the stale 2026-08-31 date** and need the integrator to refresh to 2026-09-01 (the snapshot's current as-of). One additional file outside R4's list has the same defect.

| File:line | Current text | Action for integrator |
|---|---|---|
| `community/ONBOARDING.md:102` | "Buzz Platform Snapshot … reviewed 2026-08-31" | Refresh to 2026-09-01 (this line cites the snapshot directly) |
| `community/ONBOARDING.md:103–105` | "reviewed 2026-08-31" for BUZZ_SECURITY, INFORMATION_ARCHITECTURE, CAPABILITY_LADDER | Refresh the two platform-derived entries (BUZZ_SECURITY, IA) to 2026-09-01; CAPABILITY_LADDER is not snapshot-derived and may keep its original review date |
| `community/CAPABILITY_SELF_ASSESSMENT.md:121–123` | "reviewed 2026-08-31" for Capability Ladder, IA, BUZZ_SECURITY | Refresh the IA and BUZZ_SECURITY entries; Capability Ladder is not snapshot-derived |
| `ops/BUZZ_SECURITY.md:9` | "based on the verified platform snapshot as of 2026-08-31" | Refresh to 2026-09-01; re-check the runbook's platform statements against the refreshed snapshot while editing (they still match it) |
| `ops/BUZZ_SECURITY.md:179–182` | source list "reviewed 2026-08-31" | Refresh to 2026-09-01 |
| `ops/outreach/INVITE_FUNNEL.md:238` | "2026-08-31: hosted invite-only constraint …" | Refresh to 2026-09-01 (invite-only and open-channel visibility claims re-verified above) |
| `ops/outreach/INVITE_FUNNEL.md:240–246` | "reviewed 2026-08-31" source list | Refresh the platform-derived entries; METRICS/CODE_OF_CONDUCT entries are not snapshot-derived |
| `release/OWNER_REVIEW.md:33, 72` | "2026-08-31" platform-fact references | Refresh to 2026-09-01 |
| `README.md:51` | "`buzz/PLATFORM_SNAPSHOT.md` — verified Buzz constraints as of 2026-08-31" | Refresh to 2026-09-01 |
| `buzz/CHANNELS.md:93` (not on R4's list) | "(as of 2026-08-31) for the verified platform assumptions" | Refresh to 2026-09-01 |

None of these dates makes a false claim today — every platform statement in these files still matches the refreshed snapshot (invite-only, open-channel visibility, and the launch-safe CLI surface were all re-verified above). The dates are stale metadata, not wrong facts.

## 4. GUIDE_CURRENCY_AUDIT (R2) and CLAIM_AUDIT (R4) — consistency with current files

### R2 findings vs. the post-G1 tree

| R2 finding | Status in current files | Assessment |
|---|---|---|
| Should-fix: maturity restatements in guide README (95/107/119/131/143/155) | **Resolved by G1** — README now defers to front matter ("at its current front-matter maturity label") and links the three trial Labs factually; review trigger at README:220 now reads "changes materially **or its maturity label changes**" | Correction applied; audit item is now historical |
| Should-fix: CURRICULUM.md restatements (15–16/199/248/299/350) + maintenance contract | **Resolved by G1** — map defers to front matter; maintenance contract adds "re-verify every stated maturity or evidence status against the linked artifact's front matter" | Correction applied |
| Note: K008 worked example needs a re-verification anchor | **Resolved by G1** — 05-agentic-engineering.md:224 now reads "K008 task contract (as of 2026-09-01)" | Correction applied |
| Routed: `practices/README.md:3–5` undated maturity restatement | **Still open** — the file still says "Each currently has `maturity: proposed` and `evidence_quality: none`; none is represented as a tested Practice yet" (now covering six candidates after G3). The statement is still true, but it is the last undated maturity restatement in the corpus | R2's proposed correction still applies; integrator should execute it (optionally noting that first recorded trials exist for 001–003 while maturity stays front-matter-controlled) |
| Routed: `labs/001-cheap-model-bounded-task.md:202` price-basis wording | **Still open** — "Convert a published per-million-token price to per-token before calculation." unchanged | R2's reword still applies ("When the recorded price basis is per-million tokens, convert to per-token; otherwise compute from the recorded basis directly") |
| Note: STEWARD membership claims unverifiable until owner apply | Still valid — no hosted apply has occurred | No change |

R2's "why it matters" framing ("Wave E runs the three trials") is now historical — the trials landed (labs/002–004) and E5's packets exist — but the audit is dated and reads correctly as a record of its own as-of. R2's per-file line numbers refer to the pre-G1 tree and should not be used to locate the (now-fixed) sentences.

### R4 findings vs. the current tree

| R4 item | Status in current files | Assessment |
|---|---|---|
| Finding #1: `README.md:43` advertises the machine-specific `swarm/README.md` runbook ("Dakota's WSL environment") | **Still present, verbatim** — owner decision still pending | Valid and unresolved; the remediation (reword to role-based description, or move the reference) plus the manual `swarm/README.md` check remain the exact actions |
| Out-of-class observation: six files cite "reviewed 2026-08-31" | **Confirmed still applicable** — see section 3, all six plus one more | Routed to integrator; now itemized with line numbers |
| SOCIAL_KIT 26-token exception | Consistent — GATE_EVIDENCE records the labs/003 checker re-verifying 26/26 twice | No drift |
| Coverage: 68-file scope | **Incomplete by design since G3/G2/O-wave/E5** — `practices/004–006.md`, `docs/schemas/NOTE_SCHEMA.md`/`PROJECT_SCHEMA.md`, `templates/NOTE.md`/`PROJECT.md`, `ops/BETA_OPS.md`, `.github/ISSUE_TEMPLATE/triage-policy.md`, `release/HOSTED_INSPECTION.md`, `release/PROMOTION_PACKETS.md`, and `reviews/ONBOARDING_DRY_RUN_PHASE2.md` were created after R4's scope was fixed | Not a defect in R4 (its scope was accurate at its as-of); the integrator should know these publishable surfaces have not had the six-class sweep. Spot-checking PROMOTION_PACKETS.md and GATE_EVIDENCE.md for this review found only numbers quoted from recorded Labs and commit ids — no invented metrics — but a full pass is owed before launch |

### R3 (COMMUNITY_LANDSCAPE) self-assessment

R3's handoff asked Q7 to re-fetch before any public use and to challenge the positioning gaps — the re-fetch is done (section 2). The five positioning gaps are labeled analysis and are not fact claims; no gap misstates a cited source. Gap 4 (ladder coverage) remains the least source-evidenced, as R3 itself warned: it is an argument from absence across twelve surfaces, which is the correct epistemic status for a positioning hypothesis but must not be cited as a measured finding.

## 5. Remaining time-sensitive claims lacking an as-of date

| Location | Problem | Recommendation |
|---|---|---|
| `reviews/ONBOARDING_DRY_RUN_PHASE2.md` | No calendar date anywhere; the only currency anchor is commit `1f80f96` | Add an audit date (2026-09-01) next to the commit anchor at integration |
| `reviews/EDITORIAL_REVIEW.md` | No date and no commit anchor; a reader cannot tell which tree revision it reviewed | Add date/commit anchor, or a "superseded — see …" note, at integration |
| `reviews/REPOSITORY_INTEGRITY.md` | Has a commit anchor (`b02c696`) but no calendar date; only the license row carries "as of 2026-08-31" | Add the audit date at integration |
| `reviews/FACT_AUDIT_PHASE1.md` | Correctly dated (2026-08-31) but now **superseded** on at least one fact: its platform picture predates the #6116 closure that the 2026-09-01 snapshot records | Add a header note: current platform facts live in `buzz/PLATFORM_SNAPSHOT.md` (as of 2026-09-01); do not cite the 2026-08-31 audit for current platform state |
| `research/*` | All four research files carry as-of dates; no undated time-sensitive claim found | None |

No time-sensitive claim in `research/` lacks an as-of date. The gaps are confined to three Phase 1/Phase 2 review files, which are historical records rather than living references — the fixes are one-line date stamps.

## Verdict summary

- **Buzz snapshot re-verification:** 17 verified, 0 corrected, 0 unverifiable.
- **Landscape spot-check:** 6 sources re-fetched; all checked claims verified; 0 self-reported-as-fact violations; 1 source-internal inconsistency noted (MLOps 90k vs 70k, in the source, not in the report).
- **Stale review dates:** 6 files from R4's list all still stale, plus `buzz/CHANNELS.md:93`; refresh to 2026-09-01 at integration.
- **Audit-of-audits:** R2's G1-scoped corrections all landed; its two routed corrections (practices/README.md, labs/001:202) are still open and still correct. R4's finding #1 is still open and still correct; R4's scope predates the G/O/E-wave outputs, which are owed the six-class sweep before launch.
- **Undated time-sensitive claims:** 3 review files need date stamps; 1 dated review needs a superseded-note.

## Risks

- The Buzz repository moves fast (2,574 commits at review time; three open fix PRs against excluded defects). The snapshot's exclusions and this audit's verdicts age in days, not weeks; re-run the section 1 table immediately before the owner-operated apply.
- All fetches were single snapshots from one environment on 2026-09-01; no archived or second-mirror confirmation was used. For the release record, the primary URLs above are the evidence, not this file.
- If a promotion decision lands before Q-INT integrates the routed R2 corrections, `practices/README.md:3–5` becomes a live false statement the same day.
