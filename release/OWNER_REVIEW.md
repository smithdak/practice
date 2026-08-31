# Owner review packet

## Decision requested

Dakota: use this packet to approve each owner gate with evidence or leave it
open. An unchecked row is not implied approval. Public launch is on hold until
all applicable owner gates and evidenced operating holds below are cleared by
a human. A structural release-validation pass is necessary but is not launch
approval.

The detailed sequence is in the [launch checklist](LAUNCH_CHECKLIST.md). This
packet neither creates a Buzz community nor authorizes an agent to use, receive,
or recover the owner identity.

## Locked launch model

These decisions are settled and need no new owner decision unless a change is
intentionally proposed through the governance path:

- Practice is an open-source community for AI practitioners; Git is the durable
  public source of truth and Buzz is the operating hub.
- The initial launch uses Buzz stream channels, direct idempotent CLI seeding,
  human-owned moderation, distinct least-privilege agent identities, and no
  scheduled-workflow dependency.
- The public structure follows Learn → Use → Automate → Build → Transform; it
  remains model-, platform-, and framework-agnostic.
- Default licenses are Apache License 2.0 for code and CC BY 4.0 for content;
  a text-only wordmark is the launch default.

Sources: [locked decisions](../DECISIONS.md), [non-goals](../NON_GOALS.md),
[Buzz architecture](../buzz/INFORMATION_ARCHITECTURE.md), and
[platform snapshot](../research/BUZZ_PLATFORM_SNAPSHOT.md) (reviewed
2026-08-31).

## Owner gates — all open until Dakota records approval

These are the complete owner decisions from [OWNER_GATES.md](../OWNER_GATES.md).
The status reflects this packet only; it does not assert whether an action has
already been done outside the repository.

| Gate | Evidence to review | Human action | Status |
| --- | --- | --- | --- |
| Buzz community address and relay URL | [Bootstrap dry-run plan](../buzz/BOOTSTRAP_RUNBOOK.md) and channel map | Create or confirm the Block-hosted community, verify the address/relay, and authorize an owner-operated apply. | **OPEN** |
| Owner identity backup | [Security recovery procedure](../ops/BUZZ_SECURITY.md) | Keep an encrypted offline backup separate from the working device; name a human recovery custodian privately. Never transmit identity material. | **OPEN** |
| GitHub destination | [Repository entry point](../README.md) and launch checklist | Confirm `smithdak/practice` if available, or record the chosen canonical public destination. | **OPEN** |
| License confirmation | [License inventory](../LICENSES.md) | Confirm Apache-2.0 for code and CC BY 4.0 for content, or make an explicit governance decision before publication. | **OPEN** |
| Public invitation path | [Invitation funnel](../ops/INVITE_FUNNEL.md) and [social kit](../content/launch/SOCIAL_KIT.md) | Approve the public route to request Buzz access after the route has been established and tested by a human. | **OPEN** |
| Initial community-agent providers | [Security membership model](../ops/BUZZ_SECURITY.md) and [agent profiles](../buzz/agents/) | Select the first three agents/providers manually; add billing credentials or provider secrets only in approved private systems. | **OPEN** |
| Launch date | Release-validation evidence and this packet | Set a public date only after final release validation and required human owners are named. | **OPEN** |
| Brand mark | [Launch materials](../content/launch/SOCIAL_KIT.md) | Use the default text-only wordmark, or explicitly approve a mark before it is used publicly. | **OPEN** |

## Evidenced operating holds

These are not new product decisions. They are launch prerequisites stated in
the integrated operating artifacts; do not waive them by treating an agent or
an unchecked checklist as a human owner.

| Hold | Evidence | Minimum clearance evidence | Status |
| --- | --- | --- | --- |
| Public invitation promotion | The [invitation funnel](../ops/INVITE_FUNNEL.md) says broad promotion remains paused until a private, human-monitored request route is named and tested. | A human establishes and tests the route; responsible humans know the authorized inviters, private intake ledger, and escalation owner; the issuer verifies current invitation/revocation controls or records the official-support fallback; then insert only approved public wording. | **OPEN — blocks public launch** |
| Human operating coverage | The [maintainer runbook](../ops/MAINTAINER_RUNBOOK.md), [moderation model](../community/MODERATION.md), and [weekly cadence](../ops/WEEKLY_CADENCE.md) require named human ownership for release, announcement, moderation/private reporting, and continuity. | Record eligible humans and escalation/recusal route in the appropriate safe private or Git record; confirm a release owner opens the `RELEASE` item. | **OPEN — blocks public launch** |
| Evidence-ready launch measurement | [Metrics](../ops/METRICS.md) requires evidenced Activation and Response quality, with data minimization. | Name the human and private, access-controlled recording setup; use the stated evidence and sampling rules, retain unknowns, and do not track joins, views, or private behavior. | **OPEN — blocks public launch** |
| Tested-Practice evidence | The [method index](../practices/README.md) and all three candidate files disclose `maturity: proposed` and `evidence_quality: none`. | Run and retain the method-specific trial evidence, obtain human review, and record an explicit promotion decision before calling a candidate a tested Practice. Until then, public copy must say proposed method or Practice candidate. | **OPEN — blocks public launch under the current release scope** |
| Hosted member-visible surface | The [onboarding dry run](../reviews/ONBOARDING_DRY_RUN.md) found configuration but no sanitized evidence that the hosted channels, canvases, seeds, membership visibility, or `start-here` path exist. | An authorized human performs the owner-operated apply and manual inspection, retaining only non-secret channel/seed evidence. | **OPEN — blocks public launch** |
| Steward escalation readiness | The [Steward profile](../buzz/agents/STEWARD.md) now fails closed unless a member-actionable, human-owned escalation reference is configured and tested. | Privately name the sponsor, configure a visible route/label that members can actually use, test human receipt, and enable the Steward only after the prerequisite passes. | **OPEN — blocks enabling the Steward for launch** |
| Publication destinations | The reusable [social kit](../content/launch/SOCIAL_KIT.md) intentionally retains 26 bracketed destination/handle tokens and is the sole whole-file publication-template exception in release validation. | For each selected post, a human replaces every token with an approved repository/Buzz/channel/issue destination or handle, click-tests it, and retains a non-secret check record. Do not use a reusable invitation link. | **OPEN — blocks public promotion** |

## Buzz constraints to accept operationally

The following constraints are verified in the
[Buzz Platform Snapshot](../research/BUZZ_PLATFORM_SNAPSHOT.md), reviewed
2026-08-31. They constrain launch operations; they do not request a new product
decision.

- Block-hosted communities are invite-only. Open channels are visible to
  members, not as an unauthenticated public site. Git and social links must
  carry public discovery and canonical artifacts.
- Messages, direct messages, and uploaded media are not end-to-end encrypted.
  Secrets, credentials, client material, private repositories, and personal or
  regulated data stay out of Buzz.
- Launch uses stream channels only. Forum root-post automation is excluded.
- Scheduled workflows and workflow deletion/template behavior are not reliable
  launch dependencies. The bootstrapper uses direct CLI operations and must be
  run dry-run first.
- Hosted storage limits and some recovery/access controls were not verified as
  stable. Before relying on a control, the responsible human checks official
  hosted documentation or support; agents do not improvise a workaround.

## Release evidence to review before approval

- Automated/repository evidence: [launch checklist](LAUNCH_CHECKLIST.md),
  `python3 scripts/validate.py --release` on final candidate, clean
  checkout/commit evidence, `git diff --check <baseline>..<candidate>`, and
  `git show --check <candidate>` with the exact commit IDs recorded. Also run
  the standard-library regression suite and the Practice core-skills validator.
- Content evidence: [curriculum](../guides/ai-native-practitioner/CURRICULUM.md),
  [three proposed method candidates](../practices/README.md),
  [first-ten briefs](../content/launch/FIRST_10.md), and
  [social kit](../content/launch/SOCIAL_KIT.md); [Lab schema](../docs/schemas/LAB_SCHEMA.md),
  [Story schema](../docs/schemas/STORY_SCHEMA.md), [Lab issue form](../.github/ISSUE_TEMPLATE/lab.yml),
  and [Project issue form](../.github/ISSUE_TEMPLATE/project.yml) resolve;
  proposed or hypothetical material stays labeled and no real result is invented.
- Hosted setup evidence: fresh bootstrap dry run, owner-operated apply report,
  and manual inspection of twelve stream channels, their canvases, and their
  one-time seed messages.
- Permission evidence: per-agent identity, sponsor, exact membership, purpose,
  expiry, and a human-maintained private access inventory; no owner key or
  agent authority beyond the [security runbook](../ops/BUZZ_SECURITY.md).
- Invitation and measurement evidence: the authorized-inviter, private-ledger,
  escalation, control-verification/support-fallback, and Activation/Response
  quality gates in the [launch checklist](LAUNCH_CHECKLIST.md) are evidenced
  without collecting joins, views, or private behavior.
- Human release evidence: a private `RELEASE` record naming release owner and
  final-announcement owner; Git release record before any public Buzz or social
  announcement.

The Practice core-skills files are explicitly included as an experimental
post-launch Project. Their catalog/evaluation structure is checked in CI and
release evidence, but they are excluded from initial public-launch promises and
carry no claim of successful multi-model behavioral evaluation.

## Approval sequence

1. Review the final candidate and release-validation result. If it fails or is
   unavailable, leave launch date and public promotion open.
2. Clear owner gates and operating holds with minimum private evidence. Do not
   place secrets or private invitation links in Git or Buzz.
3. Run the dry run again immediately before the owner-operated apply.
4. Conduct the limited private beta; stop and correct any safety, access,
   routing, or content issue before promotion.
5. Have the human release owner create the Git release record, then have the
   authorized human publish the canonical Buzz announcement and selected social
   posts.
6. If any material statement is wrong, stop promotion and use the correction
   path in the [maintainer runbook](../ops/MAINTAINER_RUNBOOK.md); do not
   silently replace the claim.

## Deferred from this review

- Scheduled Buzz workflows, forum automation, and self-hosting.
- A custom site, paid product, course, certification, or autonomous moderation.
- Real outcome claims, participant Stories, and broader service-level targets
  until consented evidence and human review exist.
