# Contributing to Practice

The smallest useful contribution is welcome. Start by making one thing clearer, more accurate, more reproducible, or easier for the next Practitioner to use.

Practice uses Buzz for conversation and Git for durable work. Discuss an idea, question, or draft in Buzz when that helps; record the accepted change, evidence, attribution, and review in Git. Do not maintain a second, competing copy of a Practice or decision in a Buzz thread.

Practice is pre-launch and the Buzz hub is not open yet (see [where this project is right now](README.md#where-this-project-is-right-now)). Until it opens, open an issue instead of looking for a Buzz thread.

## Choose a contribution path

Choose the smallest path that matches the outcome. You can stop at any path; a correction does not need to become a full Practice.

| Path | Good starting point | Start here | Done when |
|---|---|---|---|
| Correction | A typo, broken link, unclear instruction, or inaccurate statement | [Correction form](.github/ISSUE_TEMPLATE/correction.yml) | The correction is merged with enough context for a reviewer to verify it. |
| Note | An observation, question, or small technique worth preserving | [Note form](.github/ISSUE_TEMPLATE/note.yml) · [template](templates/NOTE.md) | The Note separates observation from evidence and states its limits. |
| Practice | A repeatable method someone else can try | [Practice form](.github/ISSUE_TEMPLATE/practice.yml) · [template](templates/PRACTICE.md) | It states inputs, steps, outputs, evaluation, failure modes, and variations. |
| Guide, Lab, or Story | A learning path, reproducible experiment, or real implementation | [Lab form](.github/ISSUE_TEMPLATE/lab.yml) · [Story form](.github/ISSUE_TEMPLATE/story.yml) | It meets the artifact's definition and its claims have appropriate evidence. |
| Project proposal | A shared software or infrastructure need | [Project form](.github/ISSUE_TEMPLATE/project.yml) · [template](templates/PROJECT.md) | It names the Practitioner problem, intended users, smallest useful release, maintainer, and relationship to existing tools. |
| Maintained Project | A Project ready for continuing community stewardship | — | A maintainer accepts responsibility, the repository contains its operating and contribution information, and its release process is defined. |

If you are unsure, create an issue or ask in the relevant Buzz channel with the problem, who it affects, and the smallest useful outcome. A maintainer can help select the path.

## First contribution: no engineering required

Use this path to improve an existing artifact without writing code:

1. Pick one Practice, Guide, Lab, Story, or Note you used or tried to use.
2. Write down the exact point where you got stuck, the change you propose, and why it would help the next Practitioner.
3. Open an issue using the closest template. Link the file and heading; include a screenshot only when it makes the problem clearer and contains no private information.
4. If the change is a small wording, link, or formatting fix, open a pull request (PR) that changes only that item. The PR template is a checklist, not a requirement to make a polished artifact.
5. Respond to reviewer questions, make any agreed revision, and let a maintainer merge it.

You may also post the draft or question in Buzz first. Once a change is proposed for acceptance, link the Git issue or PR in the thread. The issue or PR becomes the durable review record.

## Contribution flow

### 1. Frame the work in an issue

Open an issue before substantial work, using the form that matches your path
(the table above links each one). Reuse an existing issue when it already
describes the same problem. Every issue is categorized, verified, and routed
under the [triage policy](.github/TRIAGE_POLICY.md). State:

- the contribution path and the concrete Practitioner problem;
- the intended user and smallest useful result;
- relevant artifact or repository area;
- evidence available now, including source links, reproduction steps, or a clearly labeled personal observation; and
- questions or assumptions that need review.

For a one-line correction, an issue is optional when the PR itself explains the problem and verification. Do not use an issue to claim work you have not done or to reserve a broad area indefinitely.

### 2. Discuss without splitting the record

Use Buzz to get context, test an idea, find collaborators, or ask for help. Link the issue or PR rather than pasting evolving full text into the thread. Summarize decisions made in Buzz in the issue or PR, including who made the decision and any evidence considered.

Buzz discussions do not by themselves publish or approve an artifact. Git history is the source of truth for accepted public work; Buzz remains the source of truth for the current conversation and coordination.

### 3. Create a focused branch

Create a branch from the current default branch using a descriptive name, such as `fix/broken-evaluation-link` or `practice/context-pack-variation`. Keep unrelated changes out of the branch. For code or a maintained Project, follow that Project's local contribution instructions when they add requirements.

### 4. Make the change and show evidence

Write for a Practitioner who will act on the artifact. Use the smallest change that solves the stated problem. Finished artifacts live one directory per type at the repository root (`guides/`, `practices/`, `labs/`, `stories/`, `notes/`, `projects/`), with templates in `templates/` and schemas in `docs/schemas/`. Never include secrets, private keys, confidential material, personal data, or unlicensed third-party content.

Evidence should fit the claim:

| Claim or change | Evidence to include |
|---|---|
| Correction | The incorrect location and a reliable source, reproduction, or explanation of the fix. |
| Reusable method or Lab | Inputs, steps, outputs, evaluation method, failure modes, and clearly labeled variations or hypotheses. |
| Story | Before, intervention, result, and lessons; omit or anonymize confidential details only with permission and do not invent missing outcomes. Complete [the intake and consent record](templates/INTAKE_CONSENT.md) and [the redaction checklist](templates/REDACTION_CHECKLIST.md) before opening the pull request. |
| Current technical claim | A primary-source URL and the date checked. |
| Code or Project change | How the change was checked, such as a test command, manual reproduction, or an explicit statement that verification was not available. |

Do not turn an unverified observation into a general result. Label examples, proposals, and hypothetical scenarios clearly.

### 5. Open a pull request

Link the issue, explain the problem and proposed outcome, list the evidence and verification performed, and name any limits or unanswered questions. Credit every substantive contributor in the PR description or in the artifact where that attribution will remain useful. Do not add someone as a contributor without their permission.

Keep the PR reviewable: one purpose, focused files, and no unrelated cleanup. If an earlier Buzz discussion informed the work, link it and summarize the conclusion in the PR instead of requiring reviewers to reconstruct it from chat.

### 6. Review, decide, and merge

Reviewers check the acceptance criteria below and request revisions when needed. A maintainer makes the merge decision and may ask for a smaller scope, more evidence, an alternate artifact type, or a follow-up issue.

After merge, acknowledge the contribution in the PR and, when useful, return to the linked Buzz discussion with the canonical Git link. Do not announce unmerged work as complete.

## Acceptance and rejection

A contribution is ready to accept when it:

- solves or clarifies a concrete Practitioner problem;
- fits a contribution path and the repository's scope;
- is accurate, attributable, safe to publish, and clear about evidence and uncertainty;
- is reproducible when it presents a method, experiment, or result;
- is focused enough to review and includes the relevant validation or a stated reason it could not be run;
- respects the content and code licenses, code of conduct, and existing maintainers' responsibilities; and
- has any required maintainer approval for the artifact or Project.

A maintainer may reject or close a contribution when it:

- is outside Practice's community and public-knowledge scope;
- duplicates an existing artifact without a material improvement;
- makes unsupported, unverifiable, misleading, vendor-exclusive, or confidential claims;
- lacks the evidence needed for the claim after a reasonable revision request;
- bundles unrelated work so it cannot be reviewed safely; or
- conflicts with licensing, safety, moderation, or governance requirements.

Rejection is about the submitted work, not the contributor. When possible, the maintainer will identify a smaller viable path, such as a correction, Note, issue, or Lab. Governance, licensing, access, and moderation decisions remain human-owned.

## Attribution and recognition

Practice recognizes usefulness, not volume. Helpful contributions make a real workflow clearer, a method more testable, an error less likely, or the next contribution easier.

Credit contributors in Git where the work is reviewed: commit history, PR descriptions, co-authorship where applicable, and durable artifact acknowledgments for substantial work. Preserve source attribution and license notices. Acknowledgment in Buzz may celebrate the work, but it does not replace Git attribution.

Maintainers may recognize contributions through release notes, artifact acknowledgments, invitations to co-maintain, or a Buzz thank-you. Recognition should name the concrete usefulness of the work rather than count posts, reactions, or streaks. No recognition creates authority over other contributors or overrides human maintainer decisions.

## Releases and maintained Projects

Merged work is not automatically a release. A maintainer decides whether a set of merged changes warrants a release, prepares release notes that link to the canonical artifacts, and verifies that the notes do not claim unmerged or unverified outcomes.

To move from a Project proposal to a maintained Project, the proposer and a maintainer must document:

- the Practitioner problem, intended users, and smallest useful release;
- a named maintainer who accepts ongoing stewardship;
- repository location, license, contribution instructions, and code of conduct expectations;
- how issues, reviews, security or safety concerns, and releases will be handled; and
- what evidence will show the Project is useful enough to continue.

Project maintenance is earned by dependable stewardship, not granted by activity alone. A maintainer may pause, transfer, or retire a Project through the human-owned governance process when stewardship or safety requirements are no longer met.

## Need help?

Open an issue with the smallest useful question. Once the Buzz hub opens, you can also ask in the channel that matches the outcome—Learn, Use, Automate, Build, or Transform. Do not share secrets, client material, credentials, private repositories, or personal information in either place.
