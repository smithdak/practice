# Hosted setup — 2026-09-04

## Outcome and authority

The owner explicitly authorized implementation, forum enablement, and getting
Practice running in the current setup task. This record covers that delegated
setup, not approval of every public-launch gate or promotion of any artifact.

Relay: `wss://practice-ai.communities.buzz.xyz`. Canonical repository:
[smithdak/practice](https://github.com/smithdak/practice).

## Applied and inspected

- Recovered the Windows desktop by returning to Buzz 0.5.20 after the 0.5.22
  blank-window regression. The profile was backed up before recovery. Do not
  accept the pending upgrade until its Windows loading behavior is verified.
- Applied and checked all twelve canonical stream channels, their metadata,
  canvases, and versioned seed messages. `foundry` and `maintainers` are private.
- Archived the three superseded channels `Welcome`, `welcome-everyone`, and
  `general`; archive is reversible and their content was not deleted.
- Enabled Forums and created the two supplemental forums below. Both appeared
  in the desktop sidebar. Their canvases explain human-created topic structure;
  no forum root posts were automated.
- Published the Practice repository announcement and the Practice project
  grouping. The project appeared in the Projects directory with one repository.
  Its sidebar shortcut was not configured. No Git write ACL binding was added.
- Verified one manual foundry workflow run; left the workflow disabled, without
  a schedule. It is a diagnostic fixture, not a launch dependency.
- Replaced stale WSL profile pointers with the complete canonical Steward,
  Librarian, and Research Auditor profiles and `D:/github/practice` context.
  Saved and restarted each agent; verified the persisted profile content.

| Supplemental forum | Channel ID | Canvas event |
| --- | --- | --- |
| `practice-reviews` | `12fa9612-c427-4114-b539-f8cc4018fedd` | `ee409b75d786b21f6404817081364cf6a6ff489c2355573486eea4cc98504524` |
| `labs-and-experiments` | `90c88745-84fa-43a4-bc5f-3323ceaacce0` | `7c5f8c4af436ba14796256bc2c43a1155b4f2fd38e706ed965e3c8db65d1e261` |

The reviews canvas requests an artifact revision, intended reader, review
question, evidence and limitations, and one decision. The experiments canvas
requests a falsifiable question, inputs/versions/date, method/baseline, observed
results, limitations, and replication step. Both point durable artifacts to Git.
These owner-requested forums are supplemental to the twelve-stream bootstrap;
do not add forum root-message seeding to that bootstrap.

Project event: `78a22037349176657d285d33260a27dc138035d10d8680a3d998a1012dec2fe5`.
Manual workflow ID: `e7c420b7-93d2-43d1-b6f3-dc881578f27a`.

## Agent pilot and observed tests

All three use the existing Codex ACP integration. The desktop's “CLI missing”
label was contradicted by successful runtime initialization and actual replies;
no new provider credentials or harness installation was needed.

| Agent | Practice channel scope | Verified behavior |
| --- | --- | --- |
| Steward | `start-here`, `ask-practice`, `learn`, `use`, `automate`, `build`, `transform` | Routed a hypothetical learning request to `learn`; returned a human-review draft for a moderation/access request and took no action. |
| Librarian | Read assignment for `ask-practice`, `learn`, `use`, `automate`, `build`, `transform`, `projects`, `showcase`; output to owner DM review queue | Produced a draft Note outline from the public learn canvas, cited a real repository commit, retained evidence status `none`, and identified missing trial evidence. |
| Research Auditor | No community channel assignment; owner DM, named supplied file only | Audited the platform snapshot, identified citation gaps, and distinguished missing evidence from verified deployment behavior. No external-source retrieval was assigned. |

Owner receipt event: `69d6bb30af838cd8703e4cf23009ba1e32c14c3fdbfbef3cd05a9969930f7dd1`.
The owner replied `ACKNOWLEDGED` to the `[HUMAN REVIEW TEST]` in `start-here`.
This is evidence of human receipt, not an automation trigger.

Response events:

- Steward routing: `5f4afb86521600bd6f985c5f90e7cd0ba85a1af578e90ff54470ef772277887a`.
- Steward boundary: `735ff94d328b93a2a614f28473ac7a86e939d584f436a25329c1e95a334332a3`.
- Librarian draft: `85bf9fddb2328acc6e671b140d6e467898e39eb51ef04f2909f89ba1b4f2614a`.
- Auditor report: `7733914bf24d3dfafb4c74894134428da1617a3fadac53df1c892915d3ab3643`.

The auditor's first request preceded its completed relay subscription. A new
explicit mention after connection produced the report in approximately 53
seconds. The Librarian also needed an explicit mention. These are individual
smoke tests, not a response-time service commitment.

The Steward readiness checker passed all five configuration checks with the
owner-sponsored route, dated receipt, and exact seven-channel membership.
Identity, sponsor, scope, purpose, and review date are retained in the private
local access inventory. Review is due **2026-09-11**. Profiles instruct agents
to fail closed after expiry; there is no mechanically scheduled revocation.

## Operational boundary

**Owner-only pilot, not unrestricted member-triggered agents.** Runtime logs
show `respond_to=owner-only`, mention subscriptions, and
`permission_mode=bypassPermissions`. Keep owner-only until a separately
isolated runtime and least-privilege tool boundary are tested. A profile prompt
is not a sandbox, and the Buzz `bot` membership is not a proven read-only ACL.
Librarian draft-only behavior is an instruction and tested behavior, not a
mechanically enforced prohibition on channel writes.

To invoke an agent, the owner directly mentions it in its assigned channel or
owner DM. Review and accept drafts manually. Do not send confidential material
through Buzz, including DMs. Research Auditor's setup assignment is complete;
future work needs a new bounded source assignment.

No scheduled automation, autonomous moderation, arbitrary publication,
unattended promotion, paid integration, or broad invitation campaign was
enabled. Huddles, media, search, and Pulse are available UI surfaces, but no
multi-person huddle, media-sharing test, or usage measurement was fabricated.

Public launch still needs the outstanding human backup/recovery, invitation,
operating-coverage, measurement, release, and artifact-evidence decisions in
[OWNER_REVIEW.md](../release/OWNER_REVIEW.md). Successful setup does not clear
those gates. An ordinary non-owner onboarding test has not been performed.
