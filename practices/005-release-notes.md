---
artifact_type: practice
title: "Write release notes from committed evidence"
summary: "Draft release notes where every entry traces to a merged commit, review record, or handoff, is written for one stated audience, and waits for human release-owner approval before publication."
maturity: proposed
capability: use
roles: [operator, engineer, individual-practitioner]
version: 0.1.0
license: CC-BY-4.0
created: 2026-09-01
updated: 2026-09-01
evidence_quality: none
secondary_capabilities: [automate]
tags: [release-notes, evidence, review, publishing, releases]
---

# Write release notes from committed evidence

## Outcome

For one release, produce a set of release notes in which every entry names what changed, who it helps, and a pointer to committed evidence — a merged commit or pull request, a review record, or the release handoff — and which a human release owner has approved before anything is published. Notes exist in exactly one of two states: draft awaiting approval, or published with a record of where and when.

This Practice does not create a release, does not merge work, and does not replace the release-owner decision recorded in the operating cadence. An agent or non-maintainer may draft; a human release owner decides what goes out.

## Problem and scope

Release notes are written at exactly the moment the writer has the most incentive and the least accountability to embellish: the work is done, the audience is waiting, and no one re-checks each sentence against the repository. The predictable results are invented highlights, unverifiable benefit claims, and announcements of work that never actually merged.

The unit of work is one release: a bounded set of merged changes with a cutoff. This Practice covers drafting, verifying, and preparing notes for approval. It does not cover the merge or release-engineering mechanics, the announcement channel logistics, or marketing copy for external campaigns. Notes derived here state what happened; they do not claim outcomes no one measured.

## Use when

- A release is being prepared from a set of merged, review-complete changes.
- A human release owner exists who can approve, amend, or hold the notes.
- The evidence trail — commits, pull requests, review records, handoffs — is reachable by both the drafter and the approver.
- Notes will be read by people who cannot ask the author what a claim meant.

For an internal throwaway build note, a bullet list of commit references may suffice; the approval step can shrink, but every claim that names a benefit still needs a pointer.

## Inputs

- The release boundary: version or date cutoff, and the list of changes considered in scope.
- Committed evidence only: merged commit and pull-request records, review records, and the release handoff for the window. Unmerged or unreviewed work is out of bounds.
- A stated audience for the notes (see Method step 1).
- A named human release owner with authority to approve, amend, or hold publication.
- Any known limitations, breaking changes, or follow-ups recorded during review.

Do not copy secrets, confidential client material, private review discussion, or personal information into notes; summarize and point to the durable record instead.

## Method

1. **Fix the audience and the unit.** Choose one primary audience per note set and state it at the top of the draft. The unit is one release with a stated cutoff; nothing merges into the notes after the cutoff without an explicit amendment.
2. **Collect the committed evidence.** List every change in the release with its evidence pointer: commit or pull-request reference, review record, and handoff section. Work only from this list. A change with no reachable record is either recovered from the repository first or left out; it is never described from memory.
3. **Draft one entry per change.** For each entry write: what changed, who it helps, the evidence pointer, and any limitation or follow-up. Entries for the community audience name the reader's next action or the artifact to use; entries for maintainers name what merged and what was deferred.
4. **Verify every entry against its evidence.** Open each pointer and confirm the entry says what the record shows — no more. Delete every claim that has no pointer, including superlatives ("dramatically faster," "loved by the community") unless a record actually supports them. A highlight that cannot be traced is removed, not softened.
5. **Submit for human release-owner approval.** The draft stays visibly draft. The release owner reviews each entry against its pointer, amends, approves, or holds. Approval is recorded with the person, date, and the exact version of the notes approved.
6. **Publish and reconcile.** Publish only the approved version, record where it went and when, and keep the draft plus approval record with the release evidence. If a published note needs a change, publish a visible correction or amended version; never silently rewrite published notes.

| Audience | Entries include | Entries exclude |
|---|---|---|
| Community (practitioners using the work) | What changed, who it helps, link to the canonical artifact or method, limitations a user must know | Internal queue state, private review discussion, unresolved-risk details, personnel matters |
| Maintainers | What merged with references, what was deferred and why, open risks and follow-up owners | Marketing framing, unmerged aspirations |

**Expected output:** a draft with one evidence pointer per entry, an approval record naming the human release owner and approved version, and — after approval — published notes with a record of where they appeared.

## Evaluation

This is a proposed method; no execution evidence is claimed. Trial it on one real release. A reviewer who was not involved should be able to answer all of the following from the draft, the pointers, and the approval record:

- Does every entry trace to a merged commit, review record, or handoff section, and does each pointer resolve?
- Does any entry claim an outcome, adjective, or highlight its pointer does not support?
- Does the note state one audience and does its content match that audience's row in the table?
- Was publication preceded by a recorded human approval of the exact version published?

Accept the trial when every question has a specific, inspectable answer — ideally with the reviewer finding and fixing at least one unsupported entry. Do not infer reader engagement or better adoption from producing notes; that requires a separate measurement plan.

## Implementation

### Minimal: pointer-checked draft

Keep the working draft beside the release record using one line per entry:

```text
- Context-pack freshness review now records source owners
  Evidence: practices/001-context-pack.md@<commit>; review record <PR#>
  For: community — anyone maintaining a context pack
  Limitation: method unchanged for first-time assembly
```

The release owner reads each pointer, then signs the approval line with name, date, and version.

### Advanced: release-evidence packet

Assemble the notes with the release's evidence packet: the change list with pointers, the per-entry verification result, the approval record, and the publication log. For agent-assisted drafting, a bounded agent may generate the first-pass draft from the change list and flag entries lacking evidence, but the agent may not approve, publish, or fill a missing pointer from memory. Add a standing check in the release review: sample three entries and confirm the pointers resolve to merged work. Publication follows the community's release-pass boundaries; the Git release record is created first, and only an authorized human publishes to announcement channels.

## Failure modes

The following are anticipated failure hypotheses for the first trial:

- **Marketing inflation:** Entries grow superlatives and implied outcomes that no record supports. Consequence: readers distrust the notes and the release. Prevention: every adjective and outcome claim must trace to its pointer in step 4; the approver checks entries against evidence, not tone.
- **Unverifiable claims:** A benefit, metric, or user statement appears with no committed source. Consequence: the claim cannot be corrected or defended later. Prevention: no pointer, no entry; recover the source or delete the line.
- **Announcing unmerged work:** A draft includes a change still under review because it "will land today." Consequence: the notes describe a release that does not exist. Prevention: the evidence list is built from merged records only, after the cutoff; the approver confirms merge status of any suspect entry.
- **Wrong audience:** Community notes leak internal risk detail, or maintainer notes read like an announcement. Consequence: confusion or disclosure of material that was not reviewable. Prevention: state the audience at the top and apply the audience table during verification.
- **Approval bypass:** Notes publish before or without the release owner's recorded approval. Consequence: the gate cannot do its job and corrections get awkward. Prevention: draft state is explicit; publication tooling or the publishing human checks for the approval record first.
- **Silent amendment:** Published notes are edited in place after release. Consequence: readers cite content that no longer matches what they read. Prevention: corrections are published as visible amendments; the original stays in the release record.

## Evidence

Initial maturity is **proposed** and evidence quality is **none**. This repository contains the method and a planned trial only; it contains no completed release run or measured outcome. What would count as promotion evidence: a recorded single application (for example, a Lab record such as `labs/NNN-release-notes-trial.md`) containing the release boundary, the per-entry pointer list, the reviewer's verification findings including any removed entries, the approval record, the published result, and limitations. Promote to `tested` only after a human reviews that record under the Practice schema.

## Worked hypothetical example

The following is a **hypothetical example**, not a real release or result.

Release `0.3.0` (hypothetical) contains three merged changes. The draft:

- New issue-triage decision-rules table — Evidence: `docs/triage-rules.md@f4e5d6`; review record PR #77. For: community. Limitation: proposed method, not yet trialed.
- Faster link checking — Evidence: *none recoverable; the performance claim traces to a chat message, not a measurement record.* Removed.
- Bug fix: relative-link crash — Evidence: commit `9a8b7c`; review record PR #81. For: community. Limitation: fix unverified on Windows.

The release owner confirms the two surviving pointers resolve to merged work, amends the first entry's wording to match the review record, and approves version `notes-0.3.0-r2` on the record. The removed entry stays in the draft history with its reason, so the next drafter can see why "faster" did not survive.

The example demonstrates the core rule: an entry survives on the strength of its pointer, not on the appeal of its claim.

## Variations

- A small project may combine the notes with the release record itself, provided the approval and audience statements remain.
- Security or safety releases may add a required entry type — exposure, fix, and required reader action — with the same pointer rule.
- A multi-project community may publish one note set per project plus a combined digest; each entry still carries exactly one evidence pointer.

## Changelog

- **2026-09-01 — 0.1.0:** Proposed a release-notes method with audience selection, committed-evidence-only sourcing, per-entry verification, human release-owner approval, and a hypothetical worked example.
