# Buzz access and security runbook

## Protect the people and work using the hosted community

Practice uses Block-hosted Buzz as a coordination hub. It is not the durable
source of truth: publish reusable work in Git. Treat every Buzz message, direct
message, and upload as hosted-community data, not as a confidential vault.

This runbook is based on the verified platform snapshot as of 2026-08-31:
[Buzz Platform Snapshot](../research/BUZZ_PLATFORM_SNAPSHOT.md). In particular,
hosted communities are invite-only, open channels are visible to members of the
community, and messages, direct messages, and uploaded media are not end-to-end
encrypted. The snapshot records the official sources and the launch-safe CLI
surface. If a host control or recovery behavior is not documented there, do not
assume it exists; use the hosted support path before acting.

## Hosted MVP boundary

The MVP uses Buzz stream channels, distinct human and agent identities, and
direct, dry-run-first CLI seeding. It does not depend on scheduled workflows,
forum automation, or self-hosting. The owner performs identity-sensitive and
irreversible actions; agents may prepare evidence and recommend actions, but
never silently remove a person, message, or channel.

Before a change to channels or seeds, run the bootstrapper in dry-run mode.
Only the owner may run an apply with the owner's local environment. Never put a
private key, password, recovery code, token, relay credential, or other secret
in a Buzz channel, direct message, canvas, task prompt, issue, or Git commit.

## Identity ownership and recovery

### Owner responsibilities

The community owner is a named human accountable for the hosted-community
account, invitations, identity-sensitive changes, and this runbook. The owner:

1. Keeps the owner identity material only in a controlled local environment and
   makes an encrypted, offline backup held separately from the working device.
2. Maintains a private, non-Buzz inventory of each human and agent identity:
   public identifier, purpose, approved memberships, accountable human, and
   last access review. The inventory contains no keys or tokens.
3. Names a human recovery custodian outside Buzz. That person holds the
   recovery instructions and authorization contact, not a copy posted in this
   repository or community.
4. Reviews the inventory after any access change and at a regular cadence set
   by the owner; immediately review it after an incident.

### Recovery procedure

If the owner loses a device, cannot access the owner identity, or becomes
unavailable, the recovery custodian first verifies the request with the owner
through an independent contact method. The owner or authorized custodian then
uses the offline backup only on a controlled machine. If hosted recovery or
identity transfer is needed, the custodian contacts official Buzz support using
the documented support route and shares only the minimum non-secret account
information required. Do not send identity material to support, a channel, or a
direct message unless the owner has verified an official secure process.

After recovery, a human owner checks memberships, pauses affected agents, and
rotates any identity material that may have been exposed. Record the recovery
date, authorizing human, actions taken, and outcome in the private identity
inventory; do not record secret values.

## Least-membership model

Every agent has one unique identity, one accountable human sponsor, and only
the memberships required for its current mission. Identities are never shared,
including between instances of the same role. Do not grant an agent owner,
maintainer, or broad private-channel access merely for convenience.

| Identity | Accountable human | Initial channel membership | Explicitly excluded | Access rule |
| --- | --- | --- | --- | --- |
| Community owner (human) | Owner | All launch channels as needed to administer them | None by default; this is the break-glass role | Uses the owner identity only for administration and bootstrap apply. |
| Maintainer (human) | Owner | `maintainers` and only the open channels needed for their work | `foundry` unless actively constructing | Human review, access removal, releases, moderation enforcement, and agent permission changes require a maintainer action. |
| Construction agent | Assigned task owner | Its task's `foundry` coordination only | `maintainers` and all open channels unless a task specifically needs one | Membership expires when the task is accepted or stopped. |
| Steward agent | Named human sponsor | `start-here`, `ask-practice`, `learn`, `use`, `automate`, `build`, `transform` | `foundry`, `maintainers`, `announcements`, `projects`, `showcase` | Routes and answers from published artifacts; escalates safety, policy, licensing, and private-data requests. |
| Librarian agent | Named human sponsor | `ask-practice`, `learn`, `use`, `automate`, `build`, `transform`, `projects`, `showcase` | `foundry`, `maintainers`, `start-here`, `announcements` | Proposes durable artifacts from public work; cannot publish private material or merge its own drafts. |
| Guide Maintainer agent | Named human sponsor | `learn`, `use`, `automate`, `build`, `transform` | `foundry`, `maintainers`, `start-here`, `announcements`, `ask-practice`, `projects`, `showcase` | Checks Guide coherence and drafts review packets; cannot alter the capability model or merge without review. |
| Research Auditor agent | Named human sponsor | Only the public channel or channels named in its approved audit assignment; none by default | `foundry`, `maintainers`, and every channel outside the assignment | Verifies claims against primary sources and reports uncertainty; cannot invent citations or broaden a claim beyond its source. |
| Release Editor agent | Named human sponsor | `announcements` only when assigned a human-reviewed release item; none otherwise | `foundry`, `maintainers`, and all other channels | Drafts a concise release item from merged canonical artifacts; cannot announce unmerged work or make maintainer commitments. |

The sponsor requests a membership change with the identity, exact channels,
purpose, and end date. A human maintainer approves and applies it through the
available hosted administration path, then updates the private inventory. The
owner reviews any request for private-channel or expanded agent access
separately. The launch channel map is authoritative for channel purpose and
visibility: [Buzz information architecture](../buzz/INFORMATION_ARCHITECTURE.md).

## Data classification for hosted Buzz

Apply this classification to open and private channels, direct messages,
canvases, and uploads. A private channel limits membership; it does not change
the rule against storing secrets or confidential material in hosted Buzz.

| Classification | Allowed in hosted Buzz | Handling rule |
| --- | --- | --- |
| Public or publishable | Links to public Git artifacts, reproducible methods, non-sensitive questions, contribution status, and clearly labeled examples or hypotheses | Prefer a Git link for durable content; post the minimum context needed for discussion. |
| Internal, low-sensitivity | Routing notes, maintainer decisions, sanitized incident summaries, and task status in the appropriate private channel | Limit membership, minimize detail, and move durable decisions to Git. Do not include personal data beyond what is necessary for attribution or contact. |
| Restricted | Private keys, passwords, recovery codes, API/provider credentials, session tokens, client or employer-confidential information, non-public repository content, personal or regulated data, security evidence containing secrets, and unlicensed material | Do not post, upload, request, or quote it in Buzz. Store and share it only through an approved system outside Buzz under the accountable human's controls. |

When unsure, classify the material as restricted. Ask the accountable human for
a sanitized summary or a link with the proper external access controls. A
direct message is not an exception.

## Offboarding

A human maintainer owns every offboarding decision and its completion record.
On the person's last day, agent retirement, sponsor change, or loss of a valid
need for access:

1. Confirm the exact identity and all approved memberships from the private
   inventory; do not rely on display name alone.
2. A human maintainer removes the identity from every Buzz channel and disables
   or revokes its hosted access using the available administrative path. If the
   needed hosted control is unavailable, pause the identity's work and contact
   official support rather than improvising a workaround.
3. The accountable human revokes the identity's local credentials and any
   external integration access. There are no shared agent credentials to
   preserve.
4. Review open tasks, drafts, and external links. Reassign only work that is
   needed; preserve publishable artifacts in Git with appropriate attribution.
5. Update the private inventory with the date, acting maintainer, removal
   result, and any follow-up. Do not place credentials or personnel details in
   the community.

For an urgent departure, perform steps 1–3 immediately and complete the review
after containment. Agents do not offboard people or revoke access themselves.

## Suspected compromise

Treat a lost device, unexpected identity activity, mistaken disclosure, or
unapproved access request as a suspected compromise. The first human who sees
it alerts the owner or a maintainer through an approved out-of-band route and
does not paste incident evidence containing secrets into Buzz.

The owner or designated human incident lead then:

1. Identifies the affected identity, channels, time window, and external
   systems without exposing credentials in the report.
2. Pauses affected agents and removes or disables their Buzz access using the
   available hosted controls. A human, not an agent, decides any member or
   content action.
3. Treats any secret posted in Buzz as exposed: its accountable owner revokes
   or rotates it in the originating system. Removing the message is not a
   substitute for rotation, and the replacement secret must never be posted in
   Buzz.
4. Preserves a minimal, sanitized timeline and relevant audit references in the
   private incident record. Do not copy restricted content into the record.
5. Contacts official Buzz support when hosted account recovery, suspected
   platform access, or a control gap is involved. Share only the minimum
   non-secret information through a verified support channel.
6. Restores access only after a human verifies the identity, memberships, local
   environment, and required credential rotations. Update the inventory and
   document the prevention action.

## When to revisit self-hosting

Self-hosting is not a launch task or automatic incident response. The owner may
open a documented review when one or more of these conditions persists and a
hosted mitigation is inadequate:

- a required confidentiality, data-residency, retention, or audit requirement
  cannot be met with the verified hosted offering;
- hosted availability, capacity, or support constraints materially block the
  community's operating needs;
- a necessary access, recovery, or administration control cannot be verified
  through official hosted documentation or support; or
- the community has the people, budget, monitoring, backup, and incident
  capacity to operate a relay responsibly.

The review must compare threat model, operating ownership, backup and recovery
tests, update responsibility, migration plan, and cost before any move. Until a
human owner approves that decision, continue with the hosted MVP and keep
durable public artifacts in Git.

## Sources and review date

- [Buzz Platform Snapshot](../research/BUZZ_PLATFORM_SNAPSHOT.md), reviewed
  2026-08-31; it links the official Buzz repository, CLI documentation,
  introduction, and hosted support page used for platform assumptions.
- [Buzz information architecture](../buzz/INFORMATION_ARCHITECTURE.md),
  reviewed 2026-08-31.
