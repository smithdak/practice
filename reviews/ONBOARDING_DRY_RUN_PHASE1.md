# Onboarding dry run

**Superseded:** superseded as the current finding by
[ONBOARDING_DRY_RUN_PHASE2.md](ONBOARDING_DRY_RUN_PHASE2.md) (2026-09-01); kept
as the Phase 1 baseline that the Phase 2 run re-tested.

## Outcome

**Revision needed before public invitation promotion.** The repository gives all
three tested Practitioners a clear, safe, self-directed route *after* they have
joined Buzz: one `start-here` post, an outcome-based channel, a bounded first
action, a Git contribution path, and a manual follow-up. The documented route
does not require scheduled workflows, forum automation, agent identity access,
or secrets.

The public-to-member boundary is not ready to execute. There is no named,
tested private request route; the launch copy still has required URL/channel
placeholders; and there is no retained evidence that the configured community,
canvases, seeds, or agent memberships exist on a hosted relay. Consequently,
this is a repository dry run, not evidence that a person joined or posted in
Buzz. The repository explicitly says to pause broad invitation promotion in
this condition.

## Scope, baseline, and method

- **Artifact/version:** onboarding system at commit
  `716c89a6824c69f59efecb94cf51b9da869b3d4f`.
- **Intended effect:** move a new Practitioner from public discovery to a
  bounded first action without unsafe disclosure or unsupported automation.
- **Impact:** material. An error could strand a prospective member, invite them
  through an unsafe path, or create an unresolvable access/safety escalation.
- **Owner and approval:** the community owner and authorized human maintainers
  own invitations, membership, agent sponsorship, publication, and acceptance.
  This review does not approve external execution.
- **Evidence boundary:** reviewed the Q003 dependencies B002, B003, B004,
  B007–B011, and L006; the cited canonical inputs; the Buzz platform snapshot
  (as of 2026-08-31); the channel configuration; the bootstrap/security
  runbooks; and Git contribution guidance. No hosted relay, invitation,
  account, agent, or message was accessed.

Status codes in the persona tables:

- **PASS (desk):** the repository supplies a concrete, safe instruction.
- **FAIL (live):** the required external precondition is absent or the action
  was not completed in this non-mutating review. A verification failure does
  not assert that the untested hosted behavior itself is broken.

The dry run uses only documented Buzz constraints: Block-hosted communities
are invite-only; open stream channels are visible after joining; and canvases
and ordinary messages are available after membership. It does not assume a
public channel URL, invite API/link behavior, scheduled workflow, forum-root
post, DM escalation, or any unrecorded hosted control.

## Persona simulations

### 1. Nia — nontechnical operations coordinator

**Need:** learn how to produce a safe, source-grounded meeting brief from
approved notes. She can describe the task without sharing the notes.

| Step | Result | Evidence and exact next action |
| --- | --- | --- |
| Public discovery | PASS (desk); FAIL (live) | The funnel keeps Git usable without membership. Nia can inspect onboarding and choose a non-sensitive task. Public availability was not externally tested. |
| Invitation | FAIL (live) | The intended next step is a published private request route, but none is named or evidenced as tested. She cannot safely request access from the repository. |
| Buzz setup | FAIL (live) | No invitation was issued; therefore Nia cannot enter the hosted join flow. The flow correctly forbids sending keys, passwords, recovery codes, or tokens to an agent. |
| `start-here` | PASS (desk); FAIL (live) | Her completed draft is: “I am an operations coordinator. I want to work on a non-sensitive meeting-brief task. My next outcome is Learn. My first small action is to identify one source-grounding check before drafting.” She cannot post it without entry. |
| Channel selection | PASS (desk); FAIL (live) | The assessment routes the immediate need to `learn`; the first action is a bounded question naming the task, risk, and check. |
| Asking | PASS (desk); FAIL (live) | In `learn`, she would ask what check catches omissions against approved notes, using a sanitized description. This uses a normal stream message, not an agent or workflow. |
| Contribution | PASS (desk); FAIL (live) | If her check reveals unclear guidance, the smallest contribution is a Git correction or Note. The contributor quickstart permits this without Buzz membership; no GitHub issue/PR was opened. |
| Follow-up | PASS (desk); FAIL (live) | The documented action is to reply in the same `start-here` thread with the check or blocker. No thread exists because entry failed. |

### 2. Arun — technical builder

**Need:** propose a small internal-facing retrieval tool that uses only
approved documents and must be evaluated before use. He can publish a
sanitized system boundary but not the documents or credentials.

| Step | Result | Evidence and exact next action |
| --- | --- | --- |
| Public discovery | PASS (desk); FAIL (live) | Git is a valid first destination for an inspectable project or contribution path. Public availability was not externally tested. |
| Invitation | FAIL (live) | Arun is a public visitor, not a known collaborator with a direct human invitation. The repository offers no current private route for his minimal request. |
| Buzz setup | FAIL (live) | Without a valid invitation, he cannot create/enter with his own human identity. No identity setup was attempted. |
| `start-here` | PASS (desk); FAIL (live) | His draft names the retrieval-tool boundary, **Build**, and a first action: write one evaluation case using approved/synthetic inputs. |
| Channel selection | PASS (desk); FAIL (live) | The assessment correctly selects `build` for an AI-enabled system needing a boundary and evaluation; the canvas asks for job, inputs, allowed actions, approval boundary, and pass condition. |
| Asking | PASS (desk); FAIL (live) | He would ask for critique of the boundary and evaluation case in `build`, without code, credentials, or private documents. |
| Contribution | PASS (desk); FAIL (live) | He can open a Git Project proposal with the Practitioner problem/users, smallest useful release, approach/boundaries, evidence/success check, and maintainer/operating plan; or a Lab issue with a question/hypothesis, task set/fixed conditions, procedure/evaluation, evidence, and limitations. The Librarian is not needed and could only draft from a visible, source-linked thread for human review. |
| Follow-up | PASS (desk); FAIL (live) | He would link the resulting Git issue/PR back to the `start-here` thread and report the evaluated boundary or blocker. No Buzz thread exists. |

### 3. Mei — internal AI lead

**Need:** assess a proposal to move first-draft support triage to a reviewed
AI-assisted step, retaining a named decision owner and a measure for unresolved
cases. Her employer data stays out of Buzz.

| Step | Result | Evidence and exact next action |
| --- | --- | --- |
| Public discovery | PASS (desk); FAIL (live) | The public Git-first funnel lets Mei inspect methods before deciding whether coordination would help. Public availability was not externally tested. |
| Invitation | FAIL (live) | No named, tested request route lets her send the allowed one-sentence sanitized request. She must not post access/contact material in a public issue or reply. |
| Buzz setup | FAIL (live) | The invite prerequisite is absent. The system correctly keeps identity and recovery material with Mei and a human host process. |
| `start-here` | PASS (desk); FAIL (live) | Her draft names an internal-AI-lead context, a sanitized triage workflow, **Transform**, and the first action: map current/proposed decision paths with an owner and measure. |
| Channel selection | PASS (desk); FAIL (live) | The assessment routes an operating-model and governance change to `transform`, not to a vendor/tool discussion. |
| Asking | PASS (desk); FAIL (live) | In `transform`, she would post the affected workflow, decision owner, constraint, change hypothesis, and a measure; no outcome claim is implied. |
| Contribution | PASS (desk); FAIL (live) | A bounded Git Note or proposal can preserve the sanitized operating-model question. A Story is not appropriate until a real implementation has evidence; the Librarian profile correctly preserves that boundary. |
| Follow-up | PASS (desk); FAIL (live) | She would reply in the `start-here` thread with the mapped decision, blocker, or Git link. No thread exists before entry. |

## Agent and empty-state checks

The post-entry behavior is appropriately bounded in the reviewed agent
profiles. The Steward can route Nia, Arun, and Mei to `learn`, `build`, and
`transform` respectively; it cannot create accounts, issue invitations, change
membership, post outside its channels, or make acceptance/moderation decisions.
The Librarian requires a visible source thread and prepares only a human-review
draft. The Guide Maintainer, Research Auditor, and Release Editor also keep
maintenance, evidence checking, and publication separate from member routing.

The substantive agent failure is escalation delivery: the Steward says to
escalate to a named sponsor or human maintainer through an approved path, but
the deployable profile provides neither a configured destination nor a
member-facing fallback. Its declared tools only support reading/searching and
replying in assigned channels. A person who asks it for access or a private-data
decision can receive a correct escalation packet but cannot act on it.

For empty states, every configured channel has a local canvas and exactly one
seed artifact, and `start-here` has a useful first-post template. This is a
repository pass, not proof that the content was seeded. The bootstrap runbook
requires a human to inspect the post-apply channel identity, visibility,
canvas, and seed marker; no resulting JSON report or inspection record was
available to review.

## Ranked defects

### 1. Blocker — no operational invitation request route

**Location:** `ops/outreach/INVITE_FUNNEL.md` (request-route requirement and launch
readiness checklist); `community/ONBOARDING.md` (failed-invitation fallback).

**Criterion affected:** public discovery → invitation → hosted setup for every
new public Practitioner.

**Evidence:** the funnel requires a private, human-monitored route to be
designated and tested before soliciting requests, and expressly says to pause
broad invitation promotion if it does not exist. The L006 handoff confirms
that no such route is named in the repository. Onboarding then directs a
failed invite to an “existing public contact path,” which is likewise not
identified.

**Consequence:** all three personas stop before joining. The missing route also
means the allowed minimal request cannot be sent without inventing a contact
method or exposing contact/access data in public.

**Smallest correction:** before publishing an invitation CTA, the accountable
human must designate and test one private, monitored request route; record the
owner, pause mechanism, and safe public pointer outside public intake data.
Then make the generic fallback point to that controlled route without exposing
secrets or a reusable invitation link.

**Severity:** Blocker. **Proposed owner file:** `ops/outreach/INVITE_FUNNEL.md`.

### 2. Blocker — launch copy cannot carry a visitor to a real destination

**Location:** `ops/outreach/SOCIAL_KIT.md` (profile descriptions, launch
posts, response templates, and publishing checklist).

**Criterion affected:** public discovery and invitation handoff.

**Evidence:** every repository, Buzz, channel, issue, and contribution target
is still a bracketed placeholder. The kit itself says every placeholder must be
replaced before publishing. No deployed post or completed URL substitution is
available in the reviewed evidence.

**Consequence:** even after an invitation route is configured, a published
copy/paste post could leave a prospective member at a literal placeholder and
prevent the first public action or safe request for access.

**Smallest correction:** have the human publisher replace and click-test every
target in the selected launch variant, including the controlled request route;
retain a non-secret publication check record. Do not substitute a reusable
invite link.

**Severity:** Blocker. **Proposed owner file:** `ops/outreach/SOCIAL_KIT.md`.

### 3. Major — no evidence that the member-visible Buzz surface exists

**Location:** `buzz/BOOTSTRAP_RUNBOOK.md` (apply and inspection procedure);
`buzz/community.json`; `buzz/canvases/`; `buzz/seeds/`.

**Criterion affected:** Buzz setup, `start-here`, channel selection, asking,
and empty-state prevention.

**Evidence:** the repository configuration defines stream channels, canvases,
and seeds, and the runbook requires a dry run, human apply, JSON inspection,
and manual inspection. The reviewed record contains configuration only—no
target relay, non-secret apply result, channel IDs, seed-marker inspection, or
confirmation of open-channel membership visibility.

**Consequence:** the desk routes may be correct while the actual community is
missing, misconfigured, empty, or inaccessible. A validator pass cannot check
the hosted state.

**Smallest correction:** an authorized human should run the required dry run
and apply, then retain a sanitized verification record showing each channel's
name/type/visibility, canvas, seed marker, and the `start-here` path. Stop
promotion if any expected surface is absent. The existing manual correction
path is the recovery procedure; no destructive rollback is proposed.

**Severity:** Major. **Proposed owner file:** `buzz/BOOTSTRAP_RUNBOOK.md`.

### 4. Major — Steward escalation has no actionable human destination

**Location:** `buzz/agents/STEWARD.md` (tools/channel access and escalation);
`ops/BUZZ_SECURITY.md` (agent sponsorship and membership).

**Criterion affected:** agent-assisted onboarding and escalation of access,
policy, licensing, private-data, and safety concerns.

**Evidence:** the profile correctly requires escalation to a named human
sponsor or maintainer but does not specify a configured destination or a
member-visible fallback. Its permitted tools are limited to assigned-channel
reading/search and replies, so the agent cannot send an unapproved direct
escalation. The security runbook leaves the sponsor as a deployment detail.

**Consequence:** the agent can identify a boundary but leaves a new
Practitioner unable to deliver the escalation. This is especially harmful at
the access and privacy moments where the agent correctly refuses to proceed.

**Smallest correction:** make enabling the Steward contingent on a configured,
human-owned escalation reference and a safe fallback message. Keep the actual
sponsor/private contact out of public artifacts where it would expose personal
information; the reference must nevertheless be actionable for a member.

**Severity:** Major. **Proposed owner file:** `buzz/agents/STEWARD.md`.

## Checks and acceptance record

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| Identity and scope | Exact review output only; no artifact edits | Only this report and its handoff were changed | PASS |
| Repository configuration | Twelve stream channels, canvases, and one seed each | `buzz/community.json` and deterministic validation agree | PASS (repository only) |
| Persona cases | Three distinct roles complete/fail every requested step | Nia/Learn, Arun/Build, and Mei/Transform are recorded above | PASS |
| Failure/adversarial case | No route/invite; agent access escalation | All personas fail safely before entry; Steward delivery gap identified | PASS as a review finding |
| Evidence/source boundary | Do not claim hosted behavior without evidence | Snapshot and repository were used; no hosted action was claimed | PASS |
| Safety/access | No keys, confidential details, autonomous moderation, or invented platform feature | All persona examples are sanitized; human ownership preserved | PASS |
| External execution | Valid invitation, join, seeded channels, configured agent and follow-up path | No external execution evidence was supplied or obtained | UNKNOWN / release gate |
| Approval and release | Human approval before public promotion or hosted changes | No approval record | UNKNOWN / do not release |

**Baseline and recovery:** the reviewed baseline is the commit above. No
external change was made. For a failed future bootstrap, stop promotion and use
the runbook's human-reviewed manual correction procedure; for a bad invitation
or escalation route, pause the route and correct it through the accountable
human before resuming.

**Recommendation:** **revise**. Do not promote a public invitation CTA or
represent Buzz onboarding as live until the two blockers are corrected and the
external execution gate has evidence. The internal post-entry route is otherwise
ready for a human-owned, staged dry run.

## Areas not verified

- Whether the Git remote/repository and any social posts are publicly reachable.
- Hosted Buzz invitation, account, channel, canvas, seed, thread, search, or
  agent behavior; no credentials or identity were requested or used.
- A private contact route, human capacity, invitation/revocation controls, or
  named escalation sponsor. These must be verified by authorized humans using
  current hosted documentation/support where needed.
- Any participant outcome, activation, response time, contribution acceptance,
  or community activity. None is inferred from repository content.

## Taxonomy decision

This is a **review record** (not a Practice, Guide, Lab, Story, or Project):
its primary reader action is to make a human release decision from reproducible
repository observations.
