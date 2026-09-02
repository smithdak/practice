# Launch checklist

## Outcome and evidence rule

Use this checklist to move Practice through a reversible dry run, a controlled
private beta, and a human-approved public launch. Every box is intentionally
unchecked: mark one only after the named command output, Git/release link, or
safe private maintainer record exists. A failed or unknown check stops
promotion. Never put keys, credentials, recovery codes, participant data, or
private invitation links in the evidence record.

Read [Owner review](OWNER_REVIEW.md), the [maintainer runbook](../ops/MAINTAINER_RUNBOOK.md),
[Buzz bootstrap runbook](../buzz/BOOTSTRAP_RUNBOOK.md), [Buzz security runbook](../ops/BUZZ_SECURITY.md),
and [invitation funnel](../ops/outreach/INVITE_FUNNEL.md) before acting.

## 1. Dry run — no hosted changes

Dry run inspects the proposed configuration without a relay, identity, invite,
channel, message, or other hosted change. It does not clear an owner gate.

### Automated and repository checks

- [ ] Record the immutable baseline and candidate commit IDs in the release
  record, then run `git diff --check <baseline>..<candidate>` and
  `git show --check <candidate>`. Do not use a clean-worktree check as evidence
  that the committed candidate has no whitespace errors.
- [ ] After final integration supplies all release artifacts, run
  `python3 scripts/validate.py --release`; retain the complete result. Task
  validation is not a substitute for release validation. A pass proves the
  committed repository structure and task evidence only; it does not approve
  hosted setup, public copy, or launch.
- [ ] Run `python3 -m unittest discover -s tests`; retain the result for the
  release-validator and task-scope regression boundaries.
- [ ] Run `python3 skills/evals/validate.py --root .`; retain the result. This
  checks the experimental post-launch Practice core-skills Project's structure,
  not its behavioral effectiveness.
- [ ] Run `python3 scripts/buzz_bootstrap.py --dry-run`; retain only its
  non-secret stdout plan. Confirm this step does not need Buzz installation or
  credentials.
- [ ] Compare that plan with [community configuration](../buzz/community.json):
  twelve stream channels, their visibility, topic, purpose, canvas, and seed
  paths must match.
- [ ] Check every configured canvas and seed exists and each seed has one
  idempotency marker. Do not change a marker merely to make a rerun look new.
- [ ] Confirm public entry points and licenses resolve: [README](../README.md),
  [quickstart](../community/CONTRIBUTOR_QUICKSTART.md),
  [contribution model](../community/CONTRIBUTION_MODEL.md),
  [Code of Conduct](../CODE_OF_CONDUCT.md), [governance](../community/GOVERNANCE.md),
  [onboarding](../community/ONBOARDING.md), [license inventory](../LICENSES.md),
  [code license](../LICENSE-CODE), and [content license](../LICENSE-CONTENT.md).
- [ ] Confirm the durable contribution intake routes resolve: [Lab issue form](../.github/ISSUE_TEMPLATE/lab.yml)
  and [Project issue form](../.github/ISSUE_TEMPLATE/project.yml).

### Content and claim checks

- [ ] Review the [curriculum](../guides/ai-native-practitioner/CURRICULUM.md)
  and six modules for correct links and proposed-evidence framing.
- [ ] Review the three proposed method candidates: [context pack](../practices/001-context-pack.md),
  [workflow redesign](../practices/002-workflow-redesign.md), and
  [verification gate](../practices/003-verification-gate.md). Each remains
  `maturity: proposed` and `evidence_quality: none`; do not call any of them a
  tested Practice until the trial, review, and promotion record exists.
- [ ] Review the proposed [Lab](../labs/001-cheap-model-bounded-task.md),
  [Lab template](../templates/LAB.md), [Lab schema](../docs/schemas/LAB_SCHEMA.md),
  [Story template](../templates/STORY.md), [Story schema](../docs/schemas/STORY_SCHEMA.md),
  and [hypothetical Story sample](../stories/SAMPLE_HYPOTHETICAL.md) for
  explicit evidence status and safe sharing.
- [ ] Review [first-ten briefs](../ops/outreach/FIRST_10.md),
  [launch narrative](../docs/founding/FOUNDING_STORY.md),
  [social kit](../ops/outreach/SOCIAL_KIT.md), and
  [launch video plan](../ops/outreach/LAUNCH_VIDEO.md). Do not publish a
  real case, URL, handle, invitation route, or outcome claim until a human has
  verified it. The social kit is the sole whole-file publication-token
  exception and currently retains 26 tokens for human replacement/testing.

### Agent-permission checks

- [ ] Name a human sponsor and create a unique identity for each active agent.
  Record exact channels, purpose, and end date in the private access inventory.
- [ ] Compare memberships against the [least-membership model](../ops/BUZZ_SECURITY.md).
  Confirm no agent has an owner key, shared credentials, unneeded private
  membership, permission-management authority, moderation authority, merge
  authority, or release-publication authority.
- [ ] Review all launch role boundaries: [Steward](../buzz/agents/STEWARD.md),
  [Librarian](../buzz/agents/LIBRARIAN.md),
  [Guide Maintainer](../buzz/agents/GUIDE_MAINTAINER.md),
  [Research Auditor](../buzz/agents/RESEARCH_AUDITOR.md), and
  [Release Editor](../buzz/agents/RELEASE_EDITOR.md).
- [ ] Name eligible humans for release ownership, final announcement,
  moderation/private reporting, and continuity before opening public
  participation; record only safe ownership information.

**Dry-run exit:** every applicable item has evidence; all open items in
[Owner review](OWNER_REVIEW.md) are explicitly still open or human-approved;
and no safety, privacy, access, licensing, or factual unknown is being treated
as resolved. An open public-launch hold can still allow a limited private beta
only when the beta does not depend on that hold.

## 2. Private beta — controlled human-operated access

Private beta validates setup and orientation with invited people. It is not a
public launch, does not authorize broad invitation promotion, and creates no
expectation of automated support.

### Owner-operated setup

- [ ] An authorized human confirms the hosted community address and relay URL,
  completes the offline owner-identity backup, and keeps identity material in a
  controlled local environment only.
- [ ] Immediately before apply, the authorized human runs the dry run again,
  then runs the bootstrapper locally with `--apply`. Never put environment
  values in Git, Buzz, chat, or this checklist.
- [ ] Inspect the stdout report and hosted community: all twelve configured
  channels are streams; `foundry` and `maintainers` are private; the ten
  participation channels have intended open visibility; canvases and one seed
  message are present.
- [ ] If a seed may be duplicated, stop repeated applies and inspect recent
  message history manually. The duplicate check sees up to 100 messages
  returned by `buzz messages get`; it does not establish message order or
  complete history coverage.
- [ ] Confirm a human can use the private `maintainers` queue for a
  non-sensitive `RELEASE` item under the
  [maintainer runbook](../ops/MAINTAINER_RUNBOOK.md).

### Beta path

- [ ] Invite a small, known group through the human-owned hosted flow. Do not
  publish or reuse a general invitation link.
- [ ] Confirm the responsible humans know the authorized inviters, private
  intake ledger, and escalation owner outside Buzz. Do not publish these
  operational details or turn them into an agent-managed access workflow.
- [ ] Verify the current hosted invitation and revocation controls before
  relying on them, or record the official-support fallback for an unresolved
  control. Do not infer these controls from an earlier hosted setup.
- [ ] Test orientation: a member joins, reads
  [onboarding](../community/ONBOARDING.md), posts the bounded `start-here`
  introduction, and finds the appropriate next channel.
- [ ] Test one safe, non-sensitive question or contribution route from Buzz to
  the canonical Git process. Do not generalize a result from this test.
- [ ] Test the private reporting route with a harmless operational check; the
  named human confirms receipt without publishing details.
- [ ] Name the human and private, access-controlled setup that will record
  evidenced Activation and Response quality. It must use the definitions and
  sampling rules in [metrics](../ops/METRICS.md), distinguish unknowns, and
  avoid tracking joins, views, or private behavior.
- [ ] Test manual access review/offboarding only with a non-production identity
  and only if hosted controls are verified. If unclear, stop and use official
  support; do not improvise a workaround.
- [ ] If agents are activated, start only with the owner-approved three
  providers/roles, narrow memberships, and human inspection of representative
  output before relying on it.

**Private-beta exit:** setup inspection, orientation, human escalation, and
access boundaries are evidenced. Any defect has a human owner, containment
action, and review point. The public-invitation hold in
[Owner review](OWNER_REVIEW.md) must be cleared before broad promotion.

## 3. Public launch — human release and announcement

Public launch is allowed only when private-beta evidence and every applicable
owner gate and launch hold in [Owner review](OWNER_REVIEW.md) are cleared.

- [ ] Dakota confirms the public GitHub destination, code/content licenses,
  public invitation path, initial agent providers, launch date, and text-only
  brand treatment (or records an approved brand mark) under
  [Owner Gates](../docs/OWNER_GATES.md).
- [ ] A private, human-monitored invitation-request route is established and
  tested. Public copy names it only after that test; public Git access remains
  available even when Buzz invitations are paused.
- [ ] A human verifies final social destinations, handles, repository URL,
  invitation wording, and visuals against the
  [social kit](../ops/outreach/SOCIAL_KIT.md).
- [ ] The human release owner opens and decides a `RELEASE` record with the
  release commit, validation evidence, included artifacts, limitations,
  unresolved risks, and final-announcement owner.
- [ ] Create the Git release record first. Then an authorized human publishes
  the concise `announcements` post and selected social posts, linking each to
  canonical Git artifacts. An agent may draft but may not publish or commit.
- [ ] Record publication links, announcement owner, date, and correction path
  in the release record. Do not describe unmerged, unverified, or planned work
  as launched.

## Stop, rollback, and recovery

Stop promotion on a failed check, unsupported claim, open gate, absent human
owner, or safety/privacy/access concern. Preserve minimum non-sensitive
evidence; do not repair a failure by deleting people, content, or history.

| Signal | Immediate action | Human recovery path |
| --- | --- | --- |
| Validation, link, license, or content defect | Stop release and public promotion. | Correct through reviewed Git change, rerun from clean checkout, and amend or withdraw release record if needed. |
| Bootstrap, channel, canvas, or duplicate-seed defect | Stop automated applies. | Follow [bootstrap failure handling](../buzz/BOOTSTRAP_RUNBOOK.md); human decides the smallest safe correction. |
| Wrong membership, lost access, compromise, or secret exposure | Pause affected identity/agent and stop promotion. | Follow [Buzz security recovery](../ops/BUZZ_SECURITY.md); rotate/revoke in originating system and recheck membership. |
| Unsafe agent output or autonomous decision attempt | Do not merge, publish, moderate, or act on it. | Human accepts, revises, rejects, or escalates using the [verification gate](../practices/003-verification-gate.md). |
| Public claim conflicts with Git | Stop further promotion. | Release owner publishes visible correction or withdrawal; never silently replace a material claim. |
| Invitation, conduct, or privacy concern | Pause affected invitation or discussion; keep restricted details out of Buzz. | Eligible human uses [invitation funnel](../ops/outreach/INVITE_FUNNEL.md) and [moderation model](../community/MODERATION.md). |

## Artifact map

| Area | Required review artifacts |
| --- | --- |
| Public foundation | [manifesto](../docs/founding/MANIFESTO.md), [README](../README.md), [contributing](../CONTRIBUTING.md), [Lab issue form](../.github/ISSUE_TEMPLATE/lab.yml), [Project issue form](../.github/ISSUE_TEMPLATE/project.yml), [Code of Conduct](../CODE_OF_CONDUCT.md), [governance](../community/GOVERNANCE.md), [moderation](../community/MODERATION.md), [onboarding](../community/ONBOARDING.md), [quickstart](../community/CONTRIBUTOR_QUICKSTART.md), [licenses](../LICENSES.md) |
| Learning and methods | [curriculum](../guides/ai-native-practitioner/CURRICULUM.md), [foundations](../guides/ai-native-practitioner/01-foundations.md), [effective use](../guides/ai-native-practitioner/02-effective-use.md), [context engineering](../guides/ai-native-practitioner/03-context-engineering.md), [automation and agents](../guides/ai-native-practitioner/04-automation-agents.md), [agentic engineering](../guides/ai-native-practitioner/05-agentic-engineering.md), [organizational AI](../guides/ai-native-practitioner/06-organizational-ai.md), [Practices](../practices/README.md), [Lab](../labs/001-cheap-model-bounded-task.md), [Lab schema](../docs/schemas/LAB_SCHEMA.md), [Story sample](../stories/SAMPLE_HYPOTHETICAL.md), [Story schema](../docs/schemas/STORY_SCHEMA.md) |
| Experimental post-launch Project | [Practice core skills](../skills/README.md), [catalog](../skills/catalog.yaml), [evaluation specifications](../skills/evals/README.md), and `python3 skills/evals/validate.py --root .`. Inclusion in the repository is explicit; it is not part of public-launch claims and its structural pass is not behavioral validation. |
| Buzz setup and safety | [architecture](../buzz/CHANNELS.md), [community map](../buzz/community.json), [canvases](../buzz/canvases/), [seeds](../buzz/seeds/), [bootstrap](../buzz/BOOTSTRAP_RUNBOOK.md), [platform snapshot](../buzz/PLATFORM_SNAPSHOT.md), [security](../ops/BUZZ_SECURITY.md), [agent profiles](../buzz/agents/) |
| Operations and launch | [maintainer runbook](../ops/MAINTAINER_RUNBOOK.md), [metrics](../ops/METRICS.md), [first Practice Session](../ops/FIRST_PRACTICE_SESSION.md), [invitation funnel](../ops/outreach/INVITE_FUNNEL.md), [weekly cadence](../ops/WEEKLY_CADENCE.md), [first ten](../ops/outreach/FIRST_10.md), [social kit](../ops/outreach/SOCIAL_KIT.md), [launch video](../ops/outreach/LAUNCH_VIDEO.md), [Owner Gates](../docs/OWNER_GATES.md) |

## Explicitly deferred

- Scheduled Buzz workflows, forum automation, and self-hosting.
- A custom site, paid product, course, certification, or autonomous moderation.
- Measured outcomes, participant Stories, generalized reliability claims, and
  broader service-level targets until honest evidence and human review exist.
