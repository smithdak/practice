# Hosted-surface inspection checklist

Run this checklist **after** the owner-operated bootstrapper apply to confirm
that the hosted Buzz surface matches [`buzz/community.json`](../buzz/community.json).
It produces only non-secret evidence for the "Hosted member-visible surface"
hold in [Owner review](OWNER_REVIEW.md). It verifies existence and
configuration; it fixes nothing, clears no other gate, and never constitutes
launch approval.

Why this exists: the [onboarding dry run](../reviews/ONBOARDING_DRY_RUN.md)
found repository configuration but no evidence that the hosted channels,
canvases, seeds, membership visibility, or the `start-here` path actually
exist. This checklist is the manual inspection the
[bootstrap runbook](../buzz/BOOTSTRAP_RUNBOOK.md) requires after apply.

## Preconditions

All must be true before inspection starts. If any is unmet, stop and record;
do not inspect a half-verified apply.

- **Operator.** The community owner or a human maintainer the owner explicitly
  authorized for this inspection. The apply itself is owner-operated per the
  [Buzz security runbook](../ops/BUZZ_SECURITY.md); an agent never performs,
  assists, or records this inspection.
- **Apply run.** The bootstrapper `--apply` described in the
  [bootstrap runbook](../buzz/BOOTSTRAP_RUNBOOK.md), immediately preceded by a
  fresh `python3 scripts/buzz_bootstrap.py --dry-run`, per the owner-operated
  setup items in the [launch checklist](LAUNCH_CHECKLIST.md). Record the apply
  mode: default, or `--skip-seeds`. With `--skip-seeds`, the seed rows below
  cannot pass.
- **Configuration commit.** Record the exact commit ID of the repository state
  (including `buzz/community.json`, `buzz/canvases/`, and `buzz/seeds/`) the
  apply reconciled against. If it differs from the release candidate under
  review, stop and record before inspecting.
- **Private-channel access.** The inspector needs membership in `foundry` and
  `maintainers`. If the inspector is not a member, the owner inspects those
  rows; record them `not-run` with that reason.
- **Recording setup.** Record observations as plain text in a filled copy of
  this checklist. Do not attach screenshots: images can capture member
  identifiers and personal data that text evidence would exclude.

### Run identity

Record roles and commit IDs, never private individual names, hosted addresses,
or relay credentials.

- Configuration commit ID: `<commit-id>`
- Inspection date: `<YYYY-MM-DD>`
- Operator role: `<owner | authorized maintainer>`
- Apply mode: `default` / `--skip-seeds`
- Apply report retained: `<pointer to the retained non-secret stdout JSON plan>`
  *The bootstrapper writes no report file and redacts credential values;
  retain only the non-secret report and reference it by pointer.*

## Evidence rules

**Retain (per row):** channel name; type and visibility as observed; whether
topic and purpose are visible and match the configured values; canvas presence
and non-emptiness; the seed marker label observed and how it was observed;
membership observations as channel-name sets and agent roles; a result of
`pass`, `fail`, or `not-run` with a one-line non-secret reason for anything
else.

**Never record:** private keys, tokens, recovery codes, or any credential; the
relay URL or other hosted addresses; private invitation links; member or
sponsor personal data (names, handles of private individuals, contact
details); the content of private channels beyond an existence check; or any
message text beyond the seed marker label. If a secret-class item appears in
hosted content during inspection, do not copy it anywhere: treat it as exposed
per the [security runbook](../ops/BUZZ_SECURITY.md) and record only that it
was found and where.

**How to observe.** Use manual UI inspection: open each channel as a member;
read the channel header for topic and purpose; open the channel's canvas view;
read the channel's first seed message. The seed marker is an HTML comment, so
confirm it either from the retained apply report (the bootstrapper checks the
marker against the message history it reads) or from the message source if the
hosted UI exposes it. If neither is available to you, record the marker cell
`unverified`, not `pass`. The only commands this checklist relies on are the
bootstrapper's own `--dry-run` and `--apply`, plus `buzz messages get` as
documented in the [bootstrap runbook](../buzz/BOOTSTRAP_RUNBOOK.md) for
bounded history inspection.

## Per-channel inspection

Fill one row per channel. Expected visibility is the configured value in
[`buzz/community.json`](../buzz/community.json); compare hosted topic and
purpose text against the configured values in that file. Every channel must be
a stream: if the UI shows any other type, record `fail`. Results are
`pass` / `fail` / `not-run` only.

| Channel | Expected visibility | Exists as stream | Observed visibility | Topic matches | Purpose matches | Canvas non-empty | Seed marker observed | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `foundry` | private | | | | | | `<marker>` or `unverified` | |
| `maintainers` | private | | | | | | `<marker>` or `unverified` | |
| `start-here` | open | | | | | | `<marker>` or `unverified` | |
| `announcements` | open | | | | | | `<marker>` or `unverified` | |
| `ask-practice` | open | | | | | | `<marker>` or `unverified` | |
| `learn` | open | | | | | | `<marker>` or `unverified` | |
| `use` | open | | | | | | `<marker>` or `unverified` | |
| `automate` | open | | | | | | `<marker>` or `unverified` | |
| `build` | open | | | | | | `<marker>` or `unverified` | |
| `transform` | open | | | | | | `<marker>` or `unverified` | |
| `projects` | open | | | | | | `<marker>` or `unverified` | |
| `showcase` | open | | | | | | `<marker>` or `unverified` | |

Expected seed marker labels are `<channel>-v1` (for example,
`practice-seed:foundry-v1`, `practice-seed:start-here-v1`); each canonical
seed file in `buzz/seeds/` carries exactly one such marker. Record the label
you actually observed, or `unverified`. Record the channel-set check:

- The hosted community contains exactly these twelve stream channels and no
  configured channel is missing: `<pass / fail / not-run>`
- Any extra channel, forum-type channel, or unexpected workflow observed:
  `<none found, or one non-secret line>` — the apply never creates these, so
  their presence is a finding, not something to fix inline.

## Membership spot-checks

Spot-check the [least-membership model](../ops/BUZZ_SECURITY.md) by manual
inspection of channel member lists or the hosted administration path available
to the authorized human. Record agent identities by role and observed
membership as channel-name sets. For human members record presence counts
only, never names; sponsor identity stays in the private access inventory.
An agent that is absent entirely is a valid observation for a role that is not
yet active.

| Identity | Expected membership and authority | Observed | Result |
| --- | --- | --- | --- |
| Community owner (human) | Owner is the break-glass role; used only for administration and the bootstrap apply. No owner key or identity material is stored or posted anywhere in Buzz. | | |
| Construction agent | `foundry` only; excluded from `maintainers` and all open channels; membership expires when its task is accepted or stopped. | | |
| Steward agent | `start-here`, `ask-practice`, `learn`, `use`, `automate`, `build`, `transform`; not in `foundry`, `maintainers`, `announcements`, `projects`, `showcase`. | | |
| Librarian agent | `ask-practice`, `learn`, `use`, `automate`, `build`, `transform`, `projects`, `showcase`; not in `foundry`, `maintainers`, `start-here`, `announcements`. | | |
| Guide Maintainer agent | `learn`, `use`, `automate`, `build`, `transform` only. | | |
| Research Auditor agent | No channel membership by default; only channels named in its approved audit assignment. | | |
| Release Editor agent | `announcements` only when assigned a human-reviewed release item; none otherwise. | | |
| All active agents | No agent identity holds owner, maintainer, moderation, permission-management, merge, or release-publication authority; no shared identities; each has one accountable human sponsor. | | |
| Active agent set | Only the owner-approved agent roles are active; any unexpected agent identity is a finding. | | |

## `start-here` path for a new member

Verify from a plain member identity that is not the owner, a maintainer, or an
administrator. Open channels are member-visible, not a public site: an
unauthenticated visitor cannot substitute for a member view. Record results
without quoting member content or recording who posts.

- [ ] A plain member can see `start-here`, its topic, its purpose, and its
  canvas.
- [ ] The seed message is visible to that member and contains the four-line
  reply template (I work on … / I want to improve or understand … / next
  outcome / first small action).
- [ ] The routes the seed and [information architecture](../buzz/INFORMATION_ARCHITECTURE.md)
  point to exist and are member-visible (covered by the table above; record
  `pass` only if both are true).
- [ ] The interactive posting test — a member posts the bounded introduction
  and receives a human follow-up — belongs to the private-beta orientation
  item in the [launch checklist](LAUNCH_CHECKLIST.md). If it is performed
  during this inspection, record only that a member reply succeeded; never
  quote the reply or identify the member.

## Steward enablement gate

- Expected default at inspection time: **the Steward is not enabled.** If no
  Steward identity is active, record `pass`.
- If a Steward identity is active, enabling it is justified only when the
  readiness check `scripts/steward_readiness_check.py` has passed with
  retained evidence, and the deployment record privately names the sponsor and
  confirms a tested, member-actionable escalation route, per the
  [Steward profile](../buzz/agents/STEWARD.md) and the "Steward escalation
  readiness" hold in [Owner review](OWNER_REVIEW.md). Record `pass` only with
  a pointer to that evidence.
- Without that evidence, record `fail`: a human maintainer pauses the identity
  through the hosted administration path. This checklist never disables,
  modifies, or re-enables an identity, and the Steward stays disabled until a
  human re-runs and passes the readiness check.

Steward gate result: `<pass / fail / not-run>` — `<evidence pointer or reason>`

## Failure handling

Any `fail` or blocking `not-run` row stops this inspection. Do not improvise
fixes on the hosted relay; record the row, the observed value, and a one-line
non-secret reason, then route to the human recovery path.

| Finding | Immediate action | Human recovery path |
| --- | --- | --- |
| Missing, misconfigured, or empty channel, canvas, or seed | Stop and record; run no further applies. | [Bootstrap failure handling](../buzz/BOOTSTRAP_RUNBOOK.md): maintainer review, smallest manual change after review, then dry-run and apply again. Never delete, archive, or use automated rollback as recovery. |
| Seed duplicated or marker ambiguous | Stop repeated applies; inspect recent history manually. | The duplicate check sees up to 100 messages returned by `buzz messages get`; it does not establish ordering or complete history coverage. Resolve manually per the runbook. |
| Membership mismatch or unexpected agent | Pause the affected identity's work by human decision; stop promotion of the hold. | [Offboarding and least-membership review](../ops/BUZZ_SECURITY.md); treat unexpected identity activity as suspected compromise. |
| Secret or restricted material found in hosted content | Do not copy it into evidence; treat it as exposed. | Rotate or revoke it in the originating system per the [security runbook](../ops/BUZZ_SECURITY.md); removal is not a substitute for rotation. |
| Extra channel, forum channel, or unexpected workflow | Record and stop. | The apply never creates these; a human reviews provenance before the hosted-surface hold is considered. |
| Inspector cannot verify a row (no access, no marker visibility) | Record `not-run` with the reason. | The owner or another authorized human with the needed access completes the row. |

## Sign-off

Complete only after every row is `pass` with retained evidence, or every
failure is recorded with its recovery path. Sign by role and date with a
non-secret approval reference; this checklist feeds the release evidence
record ([template](../templates/RELEASE_EVIDENCE.md)) and the consolidated
gate packet `release/GATE_EVIDENCE.md`, which the "Hosted member-visible
surface" hold in [Owner review](OWNER_REVIEW.md) reviews.

- Inspection result: `pass` / `fail`
- Rows failed or not run: `<list, or none>`
- Holds still blocked by this inspection: `<list, or none>` — a pass here
  supports only the "Hosted member-visible surface" hold; all other gates and
  holds stay governed by [Owner review](OWNER_REVIEW.md).
- Evidence pointer: `<path or pointer to the filled checklist and retained
  apply report>`
- Operator role: `<owner | authorized maintainer>`
- Date: `<YYYY-MM-DD>`
- Approval reference: `<non-secret pointer to the private RELEASE maintainer item>`
