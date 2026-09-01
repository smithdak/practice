# Public discovery to a useful Buzz entry

Practice can be discovered and used without joining Buzz. An invitation only
unlocks the coordination hub; it does not gate the repository, create a member
rank, or confer authority. This operating guide turns public interest into a
safe, human-reviewed invitation and then routes the new Practitioner to the
existing onboarding path.

Hosted Buzz communities are invite-only, and their open channels are visible
only after a person joins the community. Therefore, Git and public social posts
must carry the durable artifacts and the initial call to action. Buzz is the
hub after entry, while Git remains the source of truth for reusable work.

## Entry surfaces and one path

| Stage | Public or member surface | What the person can do | Human owner action | Completion signal |
| --- | --- | --- | --- | --- |
| Discover | Git repository, linked social posts, or a referral | Read, fork, use, or contribute to an open artifact without membership. | Keep public links pointing to canonical Git work. | The person can identify one non-sensitive task or contribution they want to pursue. |
| Request access | A maintainer-published request route or a direct invitation from an authorized human | Make a minimal request or accept an invitation. | Review the request or send an invite through the available hosted process. | A valid invite is issued, or the person receives a clear, human-made next step. |
| Join | Hosted Buzz join flow | Set up and control their own identity. | Help only with an access problem; never collect identity material. | The person can enter Practice. |
| Orient | `start-here` and the onboarding materials in Buzz | State a bounded, non-sensitive task and choose a next outcome. | Route when useful; do not promise an automated reply. | The person posts the standard `start-here` introduction. |
| Follow through | Relevant Buzz stream and Git | Take the stated action and link durable work to Git when appropriate. | Review or assist when available. | A checked result, blocker, contribution, or next decision is recorded. |

The public call to action should be: **inspect an open Practice, try it on one
non-sensitive task, then use the published request route if Buzz coordination
would help.** It should not suggest that the repository, contribution, or
learning paths require an invitation.

## Public discovery operations

### Git is the first destination

Every public post and referral should link to the repository or a specific
canonical artifact first. A visitor can read, reproduce, fork, open an issue,
or submit a contribution through the documented Git process without joining
Buzz. When a conversation needs real-time routing or collaboration, the post
may also name the invitation request route, but it must never make Buzz access
sound like the only way to participate.

Use the claim set and publishing checks in the [social launch kit](../content/launch/SOCIAL_KIT.md).
Before publishing, the human publisher verifies that each social post:

1. links to a public Git artifact and does not put substantive knowledge only
   in the social post;
2. identifies one small, non-sensitive action rather than promising outcomes,
   access, or a reply time;
3. distinguishes the public Git destination from the invite-only Buzz hub; and
4. gives the current, human-owned invitation request route only after it has
   been tested by the owner.

Do not post a reusable Buzz invitation link in a social profile, launch post,
or repository issue. A link intended for a known person can be forwarded,
scraped, or misdirected. Public discovery remains public; community entry is
deliberate.

### Publish a request route before soliciting requests

Practice does not need a custom application or automated signup system. Before
an invitation CTA is published, a human owner designates one existing,
private, human-monitored request route and publishes it alongside the public
Git entry point. The owner tests that it reaches the accountable human and can
be paused or changed without changing the public artifacts.

The request route must tell a requester to provide only:

- a public profile or reply path, if they want a response;
- one sentence about the non-sensitive task, question, or contribution they
  want to work on; and
- the public artifact they inspected, if any.

It must explicitly prohibit passwords, recovery codes, private keys, tokens,
client material, employer-confidential information, and personal details not
needed for a reply. A public issue, comment, or social reply is not an
acceptable place to collect an email address, account-recovery material, or
conduct report. Route those needs to the designated private human contact
instead.

If no private, human-monitored request route exists, continue linking only to
the public repository and do not invite broad access requests yet. This is a
launch-readiness hold, not a reason to make Git access private or build a
custom form.

## Invitation decision and issuance

### Who may invite

Only the community owner or a human the owner has explicitly authorized may
issue an invitation. Agents may point to the public route or summarize a
sanitized request for a human; they may not qualify people, create or forward
invitations, change membership, recover identities, or handle identity
credentials.

An authorized human may invite a known collaborator directly when the person
has a clear reason to coordinate in Buzz. All other public requests receive a
lightweight readiness review. This review is about the proposed participation,
not seniority, employer, tool choice, popularity, or predicted contribution
volume.

### Lightweight readiness review

The reviewing human checks only the following:

| Check | Invite when | Route elsewhere or defer when |
| --- | --- | --- |
| Purpose | The requester names a bounded, non-sensitive problem, question, or public contribution path. | The request is only for access, promotion, or an unbounded tool recommendation; point to the relevant public artifact or ask for the smallest useful question. |
| Public-work boundary | The request can proceed without posting restricted material. | It depends on secrets, client data, a private repository, personal data, or unlicensed material; ask for a sanitized description or keep the work outside Buzz. |
| Conduct and operating fit | Nothing in the request indicates an immediate safety, impersonation, or disruption risk, and the requester can follow the Code of Conduct. | There is a credible safety or conduct concern; use the private human moderation route rather than debating it publicly. |
| Capacity | A human can own the invitation and the current intake can be reviewed safely. | The queue is strained or no human can handle the request; pause issuance and state that the public materials remain available. |

This is not a test, credential, payment screen, or promise that a person will
contribute. A person whose request is deferred can still use and contribute to
all public Git material. The reviewer gives the smallest truthful next step and
does not publish personal reasons for a decline or deferral.

### Issuance and recordkeeping

1. The authorized human uses the hosted invitation mechanism currently
   available to them. The platform snapshot confirms that hosted communities
   are invite-only but does not establish stable invite-link controls; do not
   claim an expiry, revocation, or bulk-invite feature without checking the
   current hosted documentation or support.
2. Send an invitation only through a private, intended-recipient channel. Tell
   the recipient not to forward it and to contact the issuer if it fails or
   reaches the wrong account.
3. The issuer records the minimum operational entry in the access-controlled
   intake ledger: date, non-identifying alias or request reference, discovery
   source, disposition (`issued`, `deferred`, `declined`, `failed`, or
   `revoked`), and a short non-sensitive reason code. Do not put the ledger,
   invitations, account details, or private correspondence in Git or Buzz.
4. An invitation is access to the community only. It does not grant a role,
   maintainer authority, special channel access, or permission to represent
   Practice.

The issuer should not ask a person to prove identity with credentials or send
recovery material. The person completes the hosted account and identity steps
with their own identity, following the boundaries in the [Buzz access and
security runbook](BUZZ_SECURITY.md).

## After entry: Buzz is the hub

After a successful join, send or point the Practitioner to [onboarding](../community/ONBOARDING.md), not to a separate welcome product or mailing sequence.
Their universal first action is the `start-here` post that names a role or work
context, a non-sensitive task, a capability outcome, and one checkable action.
From there, the Practitioner follows the established route to `learn`, `use`,
`automate`, `build`, `transform`, or `ask-practice`; `projects` and `showcase`
have their existing bounded uses.

Follow-up is deliberately manual:

1. The Practitioner completes the small action and replies in the same thread
   with what they checked, what changed, what failed, or the smallest blocker.
2. A human helper or an enabled steward agent may route the work or link a
   published artifact when they encounter it. Neither guarantees a response or
   makes access, moderation, or acceptance decisions.
3. When work becomes durable, the Practitioner opens or links the smallest
   appropriate Git issue or contribution and returns the canonical Git link to
   Buzz. Follow [the contribution guide](../CONTRIBUTING.md) rather than
   maintaining a competing artifact in a thread.

No scheduled workflow, forum automation, custom application, or automated
root post is required for this funnel.

## Abuse, mistakes, and revoked invitations

Treat an unexpected request, forwarded invite, failed join, impersonation
signal, or invitation sent to the wrong recipient as an access incident to be
handled by a human. Do not troubleshoot it in a public thread or ask for
secrets.

| Situation | Human response | Boundary |
| --- | --- | --- |
| Spam, promotion-only, or repeated automated requests | Do not issue an invite. Preserve only the minimum request reference needed to recognize repetition, then mute or block through the request surface's normal human controls where available. | Do not expose the requester, build an automated scoring system, or let an agent silently block someone. |
| Suspected impersonation or a forwarded/misdirected invite | Pause issuance. Verify the intended recipient through an independent, non-secret route; invalidate or replace the invitation if the current hosted controls permit. | Never ask for a private key, password, recovery code, or token as proof. |
| Invitation fails or expires | The recipient contacts the issuer through the designated private route. The issuer checks the hosted process or official support and may send a new invite after confirming the intended recipient. | Do not ask an agent to bypass access controls or ask the person to create a second identity. |
| Invitation needs revocation before entry | The issuer uses the documented host control if available; otherwise stops relying on the invite and asks official support for the supported action. Record the result privately. | Do not claim a revocation succeeded until a human has verified it. |
| Person has entered and access must be removed | A human maintainer follows the access-removal and moderation process in the security runbook and, when relevant, the moderation model. | An invitation revocation is not a substitute for removing an existing member's access; agents cannot make this decision. |
| Restricted material appears in a request or Buzz | Stop copying it, alert the accountable human through an approved private route, and follow the suspected-compromise procedure when applicable. | Removing a message does not make a disclosed secret safe; its owner must revoke or rotate it in the originating system. |

For a conduct concern, use the private reporting route in the [Code of
Conduct](../CODE_OF_CONDUCT.md). An access decision may be urgent, but remains
human-owned and proportionate; no agent silently removes people or content.

## Measurement and review

Use the manual, access-controlled measurement record defined in
[Practice health and outcome metrics](METRICS.md). The invitation ledger is an
operational access record, not a growth dashboard and not a member profile.
Keep it separate from public reports and retain only the minimal
non-identifying reference needed to operate safely.

At each review period, a human owner:

1. records the **entry source** for each qualifying Activation: a new
   Practitioner must take a documented first-value action, such as the
   `start-here` action, a concrete implementation question, or a useful
   improvement. An invite issued, a join, a read, a view, or an emoji is not
   Activation.
2. counts Activation by entry source, capability stage, and evidence coverage
   only when the metric contract's evidence exists; otherwise records
   `unknown`. Report the denominator, for example, reviewed activation records
   by source, rather than presenting invites or membership as success.
3. reviews a small, consistently selected sample of post-entry responses for
   **Response quality**: correct route, concrete answer, durable-artifact link
   where relevant, stated uncertainty, and safe handling. Record pass or
   needs-revision with a reason.
4. follows the same people only through voluntary, evidenced **Contribution**,
   **Artifact reuse**, **Implementation**, and **Evidence** records. Do not
   infer these from membership, messages, reactions, or private behavior.
5. records **Maintainer health** separately: invitation queue state, oldest
   pending request, unresolved access/safety issue, and load status
   (`sustainable`, `strained`, or `blocked`). If it is strained, pause broad
   invitation promotion before weakening review or safety boundaries.

Publish only the aggregate public note specified in `ops/METRICS.md`; do not
publish request records, invite status, personal information, or conduct and
security details. A missing source or outcome is `unknown`, not evidence of
failure or success.

## Launch readiness checklist

- [ ] Every discovery post links to a public Git artifact and does not gate it
      behind Buzz membership.
- [ ] A human owner has tested one private, monitored request route and can
      pause it.
- [ ] Authorized inviters, the private intake ledger, and the escalation owner
      are known to the responsible humans outside Buzz.
- [ ] The issuer has checked the current hosted invitation/revocation controls
      or knows the official support route for an unresolved control.
- [ ] The `start-here` canvas and onboarding links are available after entry.
- [ ] The owner can measure evidenced Activation and Response quality without
      tracking views, joins, or private behavior.
- [ ] The public conduct-reporting and access-escalation routes are verified
      as private and human-owned.

## Sources and review date

- [Buzz Platform Snapshot](../research/BUZZ_PLATFORM_SNAPSHOT.md), reviewed
  2026-09-01: hosted invite-only constraint, member-visible open channels, and
  the limit of verified hosted capabilities.
- [Practice onboarding](../community/ONBOARDING.md), reviewed 2026-09-01:
  post-entry path, first action, routing, and manual follow-up.
- [Buzz access and security runbook](BUZZ_SECURITY.md), reviewed 2026-09-01:
  identity, offboarding, compromise, and human-access boundaries.
- [Practice health and outcome metrics](METRICS.md), reviewed 2026-08-31:
  definitions, evidence rules, data minimization, and maintainer-health review.
- [Code of Conduct](../CODE_OF_CONDUCT.md), reviewed 2026-08-31: private
  reporting and human-owned enforcement.
