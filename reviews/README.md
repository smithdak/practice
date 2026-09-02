# Reviews

What did the independent reviewers find? Each file here is one dated review or
audit record, written by a reviewer who did not produce the work it examines.

These are records, not living documents. A record is not rewritten when the
repository changes; a path it cites is the path at its as-of date, and a
finding it reports may since have been corrected. The integration reports in
[swarm/reports/](../swarm/reports/) record what was done with each finding, and
[release/GATE_EVIDENCE.md](../release/GATE_EVIDENCE.md) cites the findings that
bear on a gate.

## Records

"Current" below means no later record of the same kind exists here. It does
not mean every finding still holds at the current commit.

| Record | Scope | As-of date | Status |
|---|---|---|---|
| [EDITORIAL_REVIEW.md](EDITORIAL_REVIEW.md) | Adversarial editorial and coherence review of the public corpus: artifact naming, the ladder, Guide currency | 2026-09-01 re-stamp; recorded 2026-08-31 against the pre-Phase-2 tree | Current |
| [EVIDENCE_REVIEW.md](EVIDENCE_REVIEW.md) | Adversarial review of every evidentiary claim in Labs 002 to 004 and the skill eval run, as the promotion packets consume them | 2026-09-01 | Current |
| [REPOSITORY_INTEGRITY.md](REPOSITORY_INTEGRITY.md) | Repository integrity and release validation: links, schemas, licenses, secret patterns, task histories | 2026-09-01 re-stamp; recorded 2026-08-31 at commit `b02c696` | Current |
| [ONBOARDING_DRY_RUN_PHASE1.md](ONBOARDING_DRY_RUN_PHASE1.md) | Three-persona desk run of the onboarding path at commit `716c89a` | No calendar date; uses the 2026-08-31 platform snapshot | Superseded by [ONBOARDING_DRY_RUN_PHASE2.md](ONBOARDING_DRY_RUN_PHASE2.md), which dispositions each of its findings |
| [ONBOARDING_DRY_RUN_PHASE2.md](ONBOARDING_DRY_RUN_PHASE2.md) | The same personas against the Phase 2 tree at commit `1f80f96`, plus the new intake and consent route | 2026-09-01 | Current |
| [FACT_AUDIT_PHASE1.md](FACT_AUDIT_PHASE1.md) | Platform and license fact audit of the launch-critical outputs | 2026-08-31 | Superseded by [FACT_AUDIT_PHASE2.md](FACT_AUDIT_PHASE2.md); its header says so |
| [FACT_AUDIT_PHASE2.md](FACT_AUDIT_PHASE2.md) | Re-verification of the platform snapshot, a landscape spot-check, and an audit of the other audits | 2026-09-01 | Current |
| [CLAIM_AUDIT.md](CLAIM_AUDIT.md) | Publishability audit of 68 public files: third-party content, invented metrics, unlabeled hypotheticals, license metadata, secrets, placeholders | 2026-09-01 | Current |
| [GUIDE_CURRENCY_AUDIT.md](GUIDE_CURRENCY_AUDIT.md) | Stale, unsourced, or vendor-specific claims across the Guide, the method candidates, Labs, Stories, and agent profiles (21 files) | 2026-09-01 | Current |

## Rules

- A review returns findings, not approval. Every gate and hold in
  [release/OWNER_REVIEW.md](../release/OWNER_REVIEW.md) stays OPEN until a human
  records a decision.
- A later review is a new dated file. A superseded record gets a note at its
  head, as [FACT_AUDIT_PHASE1.md](FACT_AUDIT_PHASE1.md) has; its findings are
  not rewritten.
- This directory is outside the release token scan in `scripts/validate.py`,
  because these records quote the marker words the scan rejects. Do not add a
  file here that must pass that scan.

## Old names

| Old | Now |
|---|---|
| `reviews/ONBOARDING_DRY_RUN.md` | `reviews/ONBOARDING_DRY_RUN_PHASE1.md` |
| `reviews/ONBOARDING_DRY_RUN_V2.md` | `reviews/ONBOARDING_DRY_RUN_PHASE2.md` |
| `reviews/PLATFORM_FACT_AUDIT.md` | `reviews/FACT_AUDIT_PHASE1.md` |
| `reviews/FACT_AUDIT_V2.md` | `reviews/FACT_AUDIT_PHASE2.md` |
| `research/CLAIM_AUDIT.md` | `reviews/CLAIM_AUDIT.md` |
| `research/GUIDE_CURRENCY_AUDIT.md` | `reviews/GUIDE_CURRENCY_AUDIT.md` |
| `research/BUZZ_PLATFORM_SNAPSHOT.md` | [`buzz/PLATFORM_SNAPSHOT.md`](../buzz/PLATFORM_SNAPSHOT.md) |
| `research/COMMUNITY_LANDSCAPE.md` | [`docs/founding/COMMUNITY_LANDSCAPE.md`](../docs/founding/COMMUNITY_LANDSCAPE.md) |
