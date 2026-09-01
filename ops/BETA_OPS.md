# Private beta operating kit

This kit is for the humans operating Practice's first invited beta cohort. The
beta validates setup, orientation, escalation routes, and access boundaries
with a small, known group. It is not a public launch: it does not authorize
broad invitation promotion and creates no expectation of automated support
([launch checklist, section 2](../release/LAUNCH_CHECKLIST.md#2-private-beta--controlled-human-operated-access)).

## Relationship to other documents

- [Weekly operating cadence](WEEKLY_CADENCE.md) is the controlling rhythm. This
  kit adds one beta-only daily pass and the facilitation prompt backlog; it
  changes nothing else in the weekly loop.
- [Invitation funnel](INVITE_FUNNEL.md) governs request review, invitation
  issuance, and the private intake ledger. The steps below only sequence those
  rules for beta operation.
- [Moderation model](../community/MODERATION.md) is the complete conduct
  procedure. This kit only names who watches which escalation route.
- [Metrics](METRICS.md) is the measurement contract. The recorded and
  never-recorded lists below summarize it for beta use; on any conflict,
  METRICS controls.
- Git issue triage follows the [triage policy](../.github/TRIAGE_POLICY.md);
  Buzz-side queue handling follows the
  [maintainer runbook](MAINTAINER_RUNBOOK.md).

## Roles (roles, not names)

One human may hold several roles during the beta, per the small-community
fallback in the weekly cadence. Names and contact routes live in the private
maintainer record, not in Git or Buzz.

| Role | Owns | May do | Must escalate, not do |
| --- | --- | --- | --- |
| Beta owner (founder or designated continuity owner) | Beta accountability, owner-gate items, stop/resume decisions. | Pause or resume the beta; confirm hosted setup; hold reserved decisions. | Do not delegate owner identity, private keys, or gate decisions. |
| Authorized inviter | Invitation issuance and the private intake ledger. | Run readiness reviews, send invitations, record ledger entries. | Never publish or reuse a general invitation link; never let an agent qualify people or issue invites. |
| Maintainer on duty | The daily pass, question routing, and contribution routing. | Route, deduplicate, assign owners, prepare release candidates. | Escalate conduct, access, licensing, and reserved decisions. |
| Private intake owner (human triager/moderator) | Conduct reports and immediate-risk assessment. | Preserve minimum evidence, classify, route, decide per the moderation model. | An agent never investigates, decides, or restricts anyone. |
| Release owner | `RELEASE` items and announcements. | Approve, amend, or hold releases; publish announcements. | An agent may draft notes but never publish or commit. |
| Agent sponsor | Bounded agent identities and inspection of their output. | Enable agents within the owner-approved roles; inspect representative output before relying on it. | Agents recommend; they never decide moderation, access, release, or policy. |

## Daily and weekly rhythm

**Continuous, at any hour.** Safety, privacy, access, and conduct concerns go
straight to the private intake owner. Agent overreach stops the agent task
immediately. Everything else follows the queue states in the maintainer
runbook.

**Daily beta pass (10–15 minutes, beta only).** This pass is an explicit
extension of the weekly cadence and is dropped when the beta ends. Work it in
order:

1. Check the private intake route for new requests and reports.
2. Check orientation: new members who have not posted the `start-here`
   introduction, and first questions left unanswered.
3. Route each item to a channel, artifact, or Git issue; assign a next owner.
4. Update queue states and the metrics ledger where evidence exists.

The operating rule from the weekly cadence applies: every pass has a named
output. If nothing needs routing, skip the pass and record nothing.

**Weekly loop.** Unchanged from the [weekly cadence](WEEKLY_CADENCE.md):
Intake (Monday), Build (Tuesday–Wednesday), Review (Thursday), Release (Friday,
when ready), Session (scheduled only when useful, per
[the first Practice Session guide](FIRST_PRACTICE_SESSION.md)), and Maintenance
(last Friday or next available pass). During the beta the Release pass covers
beta status only when there is something to release; the low-activity fallback
still applies.

## Private intake route handling

These steps implement the [invitation funnel](INVITE_FUNNEL.md); that document
controls on conflict.

1. Requests arrive on the single private, human-monitored request route the
   owner tested before the beta. The route asks for a reply path, one sentence
   on the non-sensitive task, and the public artifact inspected — nothing more.
2. The authorized inviter runs the lightweight readiness review from the
   invitation funnel: purpose, public-work boundary, conduct and operating
   fit, and capacity.
3. Deferred or declined requests get the smallest truthful next step. Public
   Git remains available regardless. Record the minimal ledger entry: date,
   non-identifying alias or reference, discovery source, disposition, and a
   short non-sensitive reason code.
4. Approved invitations go through the hosted flow in a private,
   intended-recipient channel. Tell the recipient not to forward it and to
   contact the issuer if it fails.
5. After entry, point the new Practitioner to
   [onboarding](../community/ONBOARDING.md) and the `start-here` introduction.
   No automated welcome, no promised reply time.
6. Follow-up is manual. When work becomes durable, route it to a Git issue or
   contribution per [CONTRIBUTING](../CONTRIBUTING.md) rather than leaving it
   in a thread.

Access incidents (forwarded invite, impersonation, join failure) follow the
abuse table in the invitation funnel; a human handles them, never an agent. A
member reporting conduct uses the private reporting route in the
[Code of Conduct](../CODE_OF_CONDUCT.md) — never a public issue or thread.

## Escalation routes

| Situation | Route | Who decides |
| --- | --- | --- |
| Conduct, safety, retaliation risk | Private reporting route in the Code of Conduct; human triager preserves the minimum record per the moderation model. | Human moderator. |
| Access incident or suspected compromise | Pause issuance; follow the recovery path in the Buzz security runbook. | Beta owner. |
| Secret or confidential material posted | Stop copying; alert the accountable human through an approved private route; rotate in the originating system. | Beta owner. |
| Unsafe or out-of-scope agent output | Stop the task; apply the [verification gate](../practices/003-verification-gate.md); record the defect per the maintainer runbook. | Requesting human maintainer. |
| Release or announcement | `RELEASE` item in the maintainers queue. | Human release owner. |
| Owner gates and reserved decisions | `AWAITING-HUMAN` item; never imply a gate is cleared. | Beta owner. |
| Issue priority, accept, or close | [Triage policy](../.github/TRIAGE_POLICY.md) routing record. | Human maintainer. |

Community agents may prepare packets and recommend routes. They never remove
content, restrict a person, resolve a case, or publish a decision. This is the
locked moderation decision in [DECISIONS.md](../DECISIONS.md).

## Facilitation prompt backlog (scaffold)

The B004 seed pass deliberately deferred example replies until real questions
exist. This scaffold defines how prompts enter, move through, and leave the
backlog. It contains no example content by design.

**Source rule.** A backlog entry may be proposed only from (a) a real question
asked by a real member in a beta channel, with a link or date, or (b) a
repeated routing gap a maintainer observed across real items. Invented,
hypothetical, or predicted questions do not enter the backlog.

**Entry record.** One entry per prompt, kept in the maintainers queue as a
`REVIEW` item or in the access-controlled ledger:

```text
Prompt ID: <short id>
Source: <channel and message link or date; sanitized>
Question summary: <sanitized; no member-identifying detail>
Capability stage: <Learn | Use | Automate | Build | Transform>
Proposed prompt: <the text a human would post>
Answer route: <published artifact link, or "none yet">
Status: proposed | approved | posted | dropped
Owner: <human>
```

**Flow.**

1. Anyone, including a bounded agent such as the
   [Steward](../buzz/agents/STEWARD.md), flags a real question and drafts the
   entry.
2. A human maintainer approves, revises, or drops it at the weekly Intake
   pass, or sooner when a thread is waiting.
3. An approved prompt is posted manually by a human into the relevant channel.
   No automation posts prompts; no agent posts to `announcements` or under
   another identity.
4. If a prompt surfaces durable guidance, open a Git issue instead of leaving
   the answer only in Buzz (maintainer runbook rule).
5. Example replies are added only after a real member exchange exists, are
   sanitized, and identify the member only with consent. Until then the
   backlog records the prompt and the answer route, not a reply.
6. At the Maintenance pass, drop prompts that duplicated an existing artifact
   or drew no engagement after two posting cycles; record the disposition.

## Evidence rules

Recorded, in the access-controlled ledger or the public aggregate note per
[metrics](METRICS.md):

- Activation with entry source and a documented first-value action (a join,
  read, or reaction alone is not activation).
- Contributions, artifact-reuse reports, and implementation self-reports
  labeled as self-reported.
- Response-quality sample results with pass or needs-revision and a reason.
- Maintainer health: queue state, oldest pending item, unresolved safety or
  access issues, and load status.
- Counts with denominators and evidence coverage; aliases instead of
  identities when follow-up is needed.

Never recorded:

- Joins, views, reactions, read receipts, or message volume as success
  measures.
- Credentials, keys, or recovery codes; client, employer, or community
  confidential material; personal data not needed for an agreed purpose.
- Behavioral profiles, rankings, leaderboards, or per-person activity rows.
- Private moderation evidence, reporter identity, or case details in Git or
  Buzz.
- Any outcome claim without its evidence link. Missing data is `unknown`,
  not a zero.

Hosted Buzz is not a confidential vault; durable public claims live in Git. A
maintainer records method changes between periods so counts stay comparable.

## First-30-days checklist

Mark a box only when the named evidence exists.

**Before the first invite** (owner-operated setup per the launch checklist):

- [ ] Owner-operated apply and hosted inspection complete, including the
      duplicate-seed check.
- [ ] Roles named privately: authorized inviter, maintainer on duty, private
      intake owner, release owner, and agent sponsor if agents are enabled.
- [ ] The single private request route tested by the owner; intake ledger
      ready.
- [ ] Escalation contacts known to the responsible humans outside Buzz.
- [ ] Metrics ledger created per the minimal manual measurement in METRICS.
- [ ] Triage labels from the [triage policy](../.github/TRIAGE_POLICY.md)
      created once the repository destination is confirmed (owner gate).

**Week 1:**

- [ ] First cohort invited: small, known group; no general invitation link.
- [ ] Orientation test passed: a member joins, reads onboarding, posts the
      `start-here` introduction, and finds the next channel.
- [ ] One safe question or contribution routed from Buzz to the Git process.
- [ ] Harmless private-reporting operational check; the named human confirmed
      receipt without publishing details.
- [ ] Daily pass running, or skipped with nothing recorded when idle.

**Weeks 2–3:**

- [ ] Weekly passes running; activation and contribution rows have evidence
      links.
- [ ] First facilitation prompts proposed only from real questions, or the
      backlog explicitly recorded as empty.
- [ ] Maintainer health recorded each week.

**Day 30:**

- [ ] Aggregate note published per METRICS: counts, denominators, unknowns.
- [ ] Stop conditions reviewed against actual events; response-time
      expectations in the triage policy checked against real data.
- [ ] A human decision recorded: continue, adjust, or hold the beta; the next
      30-day owner named.

## Stop conditions

Pause new invitations and the affected activity when any trigger below is
true. A named human decides resumption; record the decision in the private
maintainer record without sensitive detail in Buzz or Git.

| Trigger | Immediate action | Resumption decided by |
| --- | --- | --- |
| No eligible human owns private intake or moderation coverage | Pause invitations; tell affected people the route is unavailable. | Beta owner |
| Maintainer health recorded as strained or blocked | Reduce or pause intake before weakening review or safety boundaries. | Maintainer on duty with beta owner |
| Suspected compromise, secret exposure, or misdirected invitation | Follow Buzz security recovery; pause issuance. | Beta owner |
| Hosted invitation or revocation controls unusable or unverified when an incident needs them | Pause issuance; use official support, not a workaround. | Authorized inviter with beta owner |
| Conduct incident exceeds available moderator capacity, or retaliation risk | Temporary protective human action; pause the affected discussion; record owner and review point. | Human moderator |
| Participant privacy incident (personal or confidential data exposed) | Stop spread; preserve minimum evidence; rotate in the originating system. | Beta owner |
| Agent acts beyond its boundary (silent removal, access change, unapproved post) | Stop the agent task; treat as an incident; correct visibly through normal review. | Agent sponsor with beta owner |
| Setup defect breaks orientation or safety boundaries (channel, canvas, seed, access) | Stop changes; follow bootstrap failure handling. | Beta owner |
| Evidence rules cannot be kept (ledger unmaintained, or a metric would require restricted data) | Mark affected metrics `unknown`; fix instrumentation or pause. | Maintainer on duty |

These triggers extend the stop-and-escalate rule in the
[weekly cadence](WEEKLY_CADENCE.md) and the stop, rollback, and recovery table
in the [launch checklist](../release/LAUNCH_CHECKLIST.md) with beta-specific
cases; on conflict, those documents control.

## Sources

- [Weekly operating cadence](WEEKLY_CADENCE.md), [invitation funnel](INVITE_FUNNEL.md),
  [metrics](METRICS.md), and [maintainer runbook](MAINTAINER_RUNBOOK.md),
  reviewed 2026-09-01.
- [Moderation model](../community/MODERATION.md), [Code of Conduct](../CODE_OF_CONDUCT.md),
  [launch checklist](../release/LAUNCH_CHECKLIST.md), and
  [triage policy](../.github/TRIAGE_POLICY.md), reviewed 2026-09-01.
