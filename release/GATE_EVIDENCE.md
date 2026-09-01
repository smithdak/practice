# Gate evidence packets

One evidence packet per open owner gate and per evidenced operating hold in the
[owner review packet](OWNER_REVIEW.md). The repository-side work that can
prepare each human decision is now done and cited here; no rating below clears
or half-clears anything — every gate and hold stays **OPEN** until Dakota
records the approval or supplies the private evidence, and an unchecked row is
not implied approval.

**Evidence basis.** Phase 2 trials were recorded on 2026-09-01 at commit
`6f205d65453c7699016abc2f4d18e5db31002544` (baseline
`d97fe4a6e3c6c143b0587ee24f005e13d54b7cea` per the Q005 acceptance record in
[FINAL_INTEGRATION_REPORT.md](FINAL_INTEGRATION_REPORT.md)); commit ids were
verified with `git log`. Since that commit, only the E-wave evidence commits
(08123e5, 42869f4, 39f290c, 1e22021, df16c27) and the whitespace fix `c2a10c0`
have touched the paths cited here. Platform facts are as of 2026-09-01 per the
[Buzz platform snapshot](../research/BUZZ_PLATFORM_SNAPSHOT.md).

**Readiness scale** (repository evidence completeness for the human decision,
derived only from what is cited in the section):

- `none` — the evidence the decision requires does not yet exist in the repository.
- `partial` — repository-side evidence exists and is cited; one or more required inputs can only come from a human or a live hosted surface.
- `ready-for-decision` — everything the repository can supply is in place and cited; the remaining step is the human decision itself (plus any private execution it triggers).

## Readiness summary

| Item | Type | Evidence completeness | First human step |
| --- | --- | --- | --- |
| 1. Buzz community address and relay URL | Gate | partial | Create the hosted community with the owner identity |
| 2. Owner identity backup | Gate | partial | Make the encrypted offline backup; name the custodian privately |
| 3. GitHub destination | Gate | ready-for-decision | Confirm `smithdak/practice` or record the chosen destination |
| 4. License confirmation | Gate | ready-for-decision | Confirm Apache-2.0 / CC BY 4.0 |
| 5. Public invitation path | Gate | partial | Establish and test one private request route |
| 6. Initial community-agent providers | Gate | ready-for-decision (selection) | Select the first three agents from the documented roles |
| 7. Launch date | Gate | none | Complete the release record first; then set the date |
| 8. Brand mark | Gate | ready-for-decision | Confirm the text-only wordmark |
| 1. Public invitation promotion | Hold | partial | Establish and test the route; name the private intake roles |
| 2. Human operating coverage | Hold | partial | Name eligible humans in a private record; open the `RELEASE` item |
| 3. Evidence-ready launch measurement | Hold | partial | Name the human and the private, access-controlled ledger |
| 4. Tested-Practice evidence | Hold | ready-for-decision | Decide each candidate in [PROMOTION_PACKETS.md](PROMOTION_PACKETS.md) |
| 5. Hosted member-visible surface | Hold | partial | Owner-operated apply, then manual hosted inspection |
| 6. Steward escalation readiness | Hold | partial | Name the sponsor privately; configure and test the escalation route |
| 7. Publication destinations | Hold | partial | Replace and click-test tokens per selected post |

---

## Owner gates

### Gate 1 — Buzz community address and relay URL

1. **What the gate needs.** Create or confirm the Block-hosted community,
   verify the address/relay, and authorize an owner-operated apply.
2. **Evidence now available.** The dry-run-first procedure and its guardrails
   are in the [bootstrap runbook](../buzz/BOOTSTRAP_RUNBOOK.md). The dry run
   was executed for real at `6f205d6` (labs/002 §1 item 5: exit 0, non-secret
   294-line plan, 12 `ensure_channel` actions, no credentials needed), the plan
   matched [buzz/community.json](../buzz/community.json) 12/12 across type,
   visibility, topic/purpose, canvas, and seed (items 6–7), and all 12
   canvases/seeds exist with exactly one marker each. Platform facts are
   re-verified as of 2026-09-01: hosted communities are invite-only, a hosted
   account can create up to three communities, and the launch-safe CLI surface
   is confirmed ([snapshot](../research/BUZZ_PLATFORM_SNAPSHOT.md)).
3. **Still missing and why.** The hosted community does not exist yet; the
   address/relay URL becomes knowable only after the owner creates the
   community with the owner identity. No agent may create or receive the owner
   identity or run `--apply` — creating the owner identity is on the
   never-delegated list in [OWNER_GATES.md](../OWNER_GATES.md), and only the
   owner may apply with the owner's local environment
   ([security runbook](../ops/BUZZ_SECURITY.md)).
4. **Human action checklist.**
   - [ ] Create the Block-hosted community with the owner identity; record the address/relay URL in a private record.
   - [ ] Confirm the local owner identity is authorized to create and update the listed channels (runbook "Before applying" step 3).
   - [ ] Immediately before apply, run `python3 scripts/buzz_bootstrap.py --dry-run` again and compare against `buzz/community.json`.
   - [ ] Run the bootstrapper locally with `--apply` (owner environment only); inspect every affected channel per the runbook; retain the non-secret report.
5. **Evidence completeness.** partial — procedures and dry-run evidence are
   ready; the hosted decision and apply are owner-only.

### Gate 2 — Owner identity backup

1. **What the gate needs.** Keep an encrypted offline backup of the owner
   identity separate from the working device and name a human recovery
   custodian privately; never transmit identity material.
2. **Evidence now available.** The full procedure exists: owner
   responsibilities 1–4 and the recovery procedure in the [security
   runbook](../ops/BUZZ_SECURITY.md); the continuity checklist and the
   prepare/human-action split in the [maintainer
   runbook](../ops/MAINTAINER_RUNBOOK.md); the launch-checklist §2 requirement
   ([LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md)). The evidence-record template
   explicitly keeps identity material out of Git
   ([RELEASE_EVIDENCE.md](../templates/RELEASE_EVIDENCE.md)).
3. **Still missing and why.** Whether the backup exists and who the custodian
   is are private facts that must never enter Git or Buzz; no agent may
   create, receive, store, or recover the owner identity or private key.
4. **Human action checklist.**
   - [ ] Create the owner identity locally only.
   - [ ] Make an encrypted offline backup held separately from the working device.
   - [ ] Name the human recovery custodian privately (outside Buzz and Git) with the recovery instructions and authorization contact.
   - [ ] Verify the backup restores on a controlled machine; record date, authorizing human, and outcome in the private identity inventory (no secret values).
5. **Evidence completeness.** partial — the procedure is complete and cited;
   the private evidence cannot exist in this repository by rule.

### Gate 3 — GitHub destination

1. **What the gate needs.** Confirm `smithdak/practice` if available, or
   record the chosen canonical public destination.
2. **Evidence now available.** [README.md](../README.md) is the entry point
   and names no conflicting public destination; it passed the entry-point
   check at `6f205d6` (labs/002 §1 item 8: 9 of 9 public entry points found).
   Git as the durable source of truth is locked in
   [DECISIONS.md](../DECISIONS.md), and the launch-checklist §3 first item
   names this gate ([LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md)).
3. **Still missing and why.** Only the availability check on GitHub and the
   choice itself — external facts only the owner can establish.
4. **Human action checklist.**
   - [ ] Check whether `smithdak/practice` is available.
   - [ ] Confirm it as canonical, or record the chosen destination in a private record.
   - [ ] Record the destination wherever public copy needs it (handled per post under the Publication destinations hold).
5. **Evidence completeness.** ready-for-decision — a pure owner choice with
   the repository entry points validated.

### Gate 4 — License confirmation

1. **What the gate needs.** Confirm Apache-2.0 for code and CC BY 4.0 for
   content, or make an explicit governance decision before publication.
2. **Evidence now available.** [LICENSES.md](../LICENSES.md) maps both;
   `LICENSE-CODE` and `LICENSE-CONTENT.md` exist (labs/002 §1 item 8: 9 of 9
   at `6f205d6`). The defaults are locked in [DECISIONS.md](../DECISIONS.md).
   The R4 claim re-audit found zero license/attribution defects
   ([CLAIM_AUDIT.md](../research/CLAIM_AUDIT.md)), and labs/003 mechanized the
   license front-matter class with 68/68 agreement against that audit
   ([labs/003](../labs/003-workflow-redesign-trial.md), runs T3/T4).
3. **Still missing and why.** License and governance acceptance is on the
   never-delegated list in [OWNER_GATES.md](../OWNER_GATES.md) — only a human
   can accept it.
4. **Human action checklist.**
   - [ ] Confirm Apache-2.0 for code (`LICENSE-CODE`) and CC BY 4.0 for content (`LICENSE-CONTENT.md`).
   - [ ] Or open the governance path to change either default before any publication.
5. **Evidence completeness.** ready-for-decision — inventory verified, no
   outstanding license findings, acceptance is the remaining act.

### Gate 5 — Public invitation path

1. **What the gate needs.** Approve the public route to request Buzz access
   after the route has been established and tested by a human.
2. **Evidence now available.** The route specification is complete: what a
   requester may provide, who may invite, the readiness review, issuance
   recordkeeping, and the launch-readiness checklist in the [invitation
   funnel](../ops/INVITE_FUNNEL.md); reusable invitation links are banned and
   the social kit carries the wording slots
   ([SOCIAL_KIT.md](../content/launch/SOCIAL_KIT.md)). The [onboarding dry
   run](../reviews/ONBOARDING_DRY_RUN.md) records the invitation stage FAIL
   (live) — no named, tested route exists.
3. **Still missing and why.** The route itself does not exist; establishing
   and testing it requires a live hosted community and a human receiver.
   Agents may not qualify people or create/forward invitations
   ([funnel](../ops/INVITE_FUNNEL.md)), and approval before the test would
   violate the funnel's own rule.
4. **Human action checklist.**
   - [ ] Designate one existing, private, human-monitored request route.
   - [ ] Test that a request reaches the accountable human and that the route can be paused or changed without touching public artifacts.
   - [ ] Verify the current hosted invitation/revocation controls, or record the official-support fallback for an unresolved control.
   - [ ] Only then approve the public wording and insert it into approved public copy.
5. **Evidence completeness.** partial — the specification and failure modes
   are done; the route and its test are human-hosted work.

### Gate 6 — Initial community-agent providers

1. **What the gate needs.** Select the first three agents/providers manually;
   add billing credentials or provider secrets only in approved private
   systems.
2. **Evidence now available.** The least-membership model names five agent
   roles with sponsors, exact memberships, and exclusions
   ([security runbook](../ops/BUZZ_SECURITY.md)); the five profiles exist
   ([Steward](../buzz/agents/STEWARD.md),
   [Librarian](../buzz/agents/LIBRARIAN.md),
   [Guide Maintainer](../buzz/agents/GUIDE_MAINTAINER.md),
   [Research Auditor](../buzz/agents/RESEARCH_AUDITOR.md),
   [Release Editor](../buzz/agents/RELEASE_EDITOR.md)); the never-delegate
   list covers billing credentials and provider secrets
   ([OWNER_GATES.md](../OWNER_GATES.md)).
3. **Still missing and why.** The selection is a human choice reserved to the
   owner; billing credentials and provider secrets may never pass through an
   agent.
4. **Human action checklist.**
   - [ ] Select the first three roles from the documented set.
   - [ ] Name a human sponsor for each; record identity, exact channels, purpose, and end date in the private access inventory.
   - [ ] Add provider billing credentials only in the approved private system.
   - [ ] When agents are activated, inspect representative output before relying on it (launch-checklist beta rule).
5. **Evidence completeness.** ready-for-decision (selection) — the menu and
   boundaries are complete; credential entry is private execution that
   follows, and hosted activation additionally depends on Gate 1.

### Gate 7 — Launch date

1. **What the gate needs.** Set a public date only after final release
   validation and the required human owners are named.
2. **Evidence now available.** The sequence and exit conditions are defined
   ([LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md)); the fill-in release record is
   ready ([RELEASE_EVIDENCE.md](../templates/RELEASE_EVIDENCE.md), commit
   `6f205d6`); interim validation evidence exists at `6f205d6` — release
   validation, 100 unit tests, skills validator, dry run, and 8 of 9 §1 checks
   pass (labs/002), with the one failure (trailing whitespace) fixed in
   `c2a10c0`; the promotion decisions awaiting a human are packaged in
   [PROMOTION_PACKETS.md](PROMOTION_PACKETS.md).
3. **Still missing and why.** The evidence this gate names does not exist yet:
   no final-candidate release-validation record is filled (that runs after
   final integration per [SWARM_PHASE2_PLAN.md](../SWARM_PHASE2_PLAN.md)), no
   private `RELEASE` item is open, and no human release owner is named —
   naming humans is reserved to humans (see Human operating coverage below).
4. **Human action checklist.**
   - [ ] After final integration, run release validation on the final candidate and fill `templates/RELEASE_EVIDENCE.md` (baseline/candidate commit IDs, all automated and content checks, agent-permission checks, dry-run exit summary).
   - [ ] Confirm the required human owners are named (Human operating coverage hold).
   - [ ] Confirm every gate and hold above is human-approved.
   - [ ] Then set the date in the private release record.
5. **Evidence completeness.** none — the decision-required evidence (final
   release record, named owners) does not yet exist in the repository;
   interim evidence is cited only to show the path is executable.

### Gate 8 — Brand mark

1. **What the gate needs.** Use the default text-only wordmark, or explicitly
   approve a mark before it is used publicly.
2. **Evidence now available.** The text-only wordmark is the locked launch
   default ([DECISIONS.md](../DECISIONS.md)); the launch materials are
   text-only today — the social kit contains only text tokens (26 bracketed
   placeholders, verified below under the Publication destinations hold); a
   complex brand identity is a non-goal ([NON_GOALS.md](../NON_GOALS.md)).
3. **Still missing and why.** Only the owner's confirmation — or, if a mark is
   ever proposed, a human-created and human-approved design; agents must not
   invent a mark for approval.
4. **Human action checklist.**
   - [ ] Confirm the text-only wordmark for launch.
   - [ ] Or approve a specific mark explicitly before any public use.
5. **Evidence completeness.** ready-for-decision — the default is consistent
   across every launch artifact.

---

## Evidenced operating holds

### Hold 1 — Public invitation promotion

1. **What the hold needs.** Broad promotion stays paused until a private,
   human-monitored request route is named and tested, the private intake roles
   are known to the responsible humans, and current invitation/revocation
   controls are verified or an official-support fallback is recorded.
2. **Evidence now available.** The pause rule and the complete operating
   procedure are in the [invitation funnel](../ops/INVITE_FUNNEL.md) (its
   launch-readiness checklist is unchecked by design); the live gap is
   evidenced in the [onboarding dry run](../reviews/ONBOARDING_DRY_RUN.md)
   (invitation stage FAIL (live) for all three personas); the data-minimized
   intake ledger and review rules are in
   [METRICS.md](../ops/METRICS.md); hosted invitation/revocation controls are
   explicitly unverified per the platform snapshot (as of 2026-09-01).
3. **Still missing and why.** The tested route, the authorized-inviter /
   private-ledger / escalation-owner knowledge, and the control verification
   are hosted and private facts; agents cannot establish routes, hold ledger
   knowledge, or verify host controls — the snapshot forbids assuming a
   control that official documentation does not confirm.
4. **Human action checklist.**
   - [ ] Establish and test one private, human-monitored request route (see Gate 5).
   - [ ] Make sure the responsible humans know the authorized inviters, private intake ledger, and escalation owner — outside Buzz.
   - [ ] Verify current hosted invitation/revocation controls, or record the official-support fallback.
   - [ ] Insert only approved public wording into public copy; never a reusable invitation link.
5. **Evidence completeness.** partial — every private input is specified and
   bounded; none of it can be produced by an agent.

### Hold 2 — Human operating coverage

1. **What the hold needs.** Named human ownership for release, announcement,
   moderation/private reporting, and continuity, with a confirmed release
   owner opening the `RELEASE` item.
2. **Evidence now available.** The role boundaries, queues, the private
   `RELEASE` item format, and the owner-gate prepare/action table are in the
   [maintainer runbook](../ops/MAINTAINER_RUNBOOK.md); the moderation model
   requires at least one named human maintainer owning the private reporting
   route before public participation opens
   ([MODERATION.md](../community/MODERATION.md)); the weekly cadence assigns
   each queue a human owner ([WEEKLY_CADENCE.md](../ops/WEEKLY_CADENCE.md));
   the release record keeps only roles and a private-record pointer, never
   names ([RELEASE_EVIDENCE.md](../templates/RELEASE_EVIDENCE.md)).
3. **Still missing and why.** The humans' names and the escalation/recusal
   route belong in a private record or a safe Git record maintained by a
   human; no agent may name owners, accept ownership, or open a `RELEASE`
   item on a human's behalf.
4. **Human action checklist.**
   - [ ] Record eligible humans and the escalation/recusal route in the appropriate private (or safe Git) record for: release ownership, final announcement, moderation/private reporting, and continuity.
   - [ ] Confirm the release owner opens the private `RELEASE` item per the runbook's queue format.
5. **Evidence completeness.** partial — the role model is complete; the names
   are human-only inputs.

### Hold 3 — Evidence-ready launch measurement

1. **What the hold needs.** Evidenced Activation and Response quality with
   data minimization: a named human and a private, access-controlled recording
   setup, using the stated evidence and sampling rules, retaining unknowns,
   and never tracking joins, views, or private behavior.
2. **Evidence now available.** The full metric contract — Activation and
   Response-quality operational definitions, evidence rules, denominators,
   unknown-retention, and the explicit do-not-collect list — is in
   [METRICS.md](../ops/METRICS.md); the launch review wiring (entry source per
   Activation, sampled Response quality, maintainer health) is in the
   funnel's measurement section ([INVITE_FUNNEL.md](../ops/INVITE_FUNNEL.md));
   the launch checklist requires the human and setup to be named before beta
   exit ([LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md)).
3. **Still missing and why.** The named human and the private,
   access-controlled spreadsheet/ledger are private operational facts; agents
   must never run measurement or hold access to private behavior data.
4. **Human action checklist.**
   - [ ] Name the human who will record Activation and Response quality.
   - [ ] Set up the private, access-controlled ledger (spreadsheet or Markdown) per METRICS.md's minimal manual method.
   - [ ] Confirm the setup uses the stated evidence and sampling rules, keeps unknowns, and collects none of the do-not-collect data.
5. **Evidence completeness.** partial — definitions and minimization rules
   are launch-ready; the human and private setup are the missing inputs.

### Hold 4 — Tested-Practice evidence

1. **What the hold needs.** Run and retain method-specific trial evidence,
   obtain human review, and record an explicit promotion decision before any
   candidate is called a tested Practice; until then public copy says
   "proposed method or Practice candidate."
2. **Evidence now available.** All three trials are recorded and complete:
   [labs/002](../labs/002-context-pack-trial.md) (run E1-R1 at `6f205d6`:
   8 of 9 launch-checklist §1 checks passed, one real trailing-whitespace
   failure correctly routed and later fixed in `c2a10c0`; pack checklist 9
   PASS / 1 FAIL-as-written), [labs/003](../labs/003-workflow-redesign-trial.md)
   (runs T3/T4: 68/68 agreement for the two mechanized claim-audit classes,
   26/26 token exception verified twice, two excluded defective runs
   retained), and [labs/004](../labs/004-verification-gate-trial.md) (gate
   trial on commit `421ed6e` plus a clean rollback rehearsal; the Practice's
   own two-artifact/refusal-path bar recorded as unmet). The human decision
   packets are assembled in [PROMOTION_PACKETS.md](PROMOTION_PACKETS.md):
   per-candidate criteria checklists (001: 4 met / 1 partial / 4 not met;
   002: 4/1/4; 003: 4/0/5), residual risks, and the exact decision questions.
   Corroborating but non-counting evidence:
   [EVAL_REPORT.md](../skills/evals/EVAL_REPORT.md) — 45/45 single-family,
   self-run/self-graded, does not count toward promotion by its own policy.
   The index and candidates all still read `maturity: proposed` /
   `evidence_quality: none` ([practices/README.md](../practices/README.md)).
3. **Still missing and why.** The promotion decision itself is human-only —
   "a human maintainer may promote a method only after the artifact records
   the trial and review evidence required by its schema"; the agent
   recommendations in the packet are explicitly non-binding (and recommend
   promoting 001 only, holding 002 and 003). The promotion edits to the
   practice files follow the decision; agents must not pre-execute them.
4. **Human action checklist.**
   - [ ] Read [PROMOTION_PACKETS.md](PROMOTION_PACKETS.md) Packets 1–3.
   - [ ] Record a promote-or-hold decision per candidate (Packet §6 states each question and the exact edits a promotion requires).
   - [ ] If promoting: apply the packet's edit steps, then run `python3 scripts/validate_artifacts.py --root .` (it enforces the tested/evidence pairing and the `labs/…` body link).
   - [ ] Have the owners of downstream copy (practices index, launch checklist, this hold's row, CONTEXT.md note) update the wording to match.
5. **Evidence completeness.** ready-for-decision — trials, criteria
   checklists, and decision questions are all in place; only the human
   decision and the edits it authorizes remain.

### Hold 5 — Hosted member-visible surface

1. **What the hold needs.** An authorized human performs the owner-operated
   apply and manual inspection of the hosted channels, canvases, seeds,
   membership visibility, and the `start-here` path, retaining only non-secret
   channel/seed evidence.
2. **Evidence now available.** The [onboarding dry
   run](../reviews/ONBOARDING_DRY_RUN.md) found full configuration but
   explicitly no sanitized evidence that any hosted surface exists. Repository
   side is verified at `6f205d6`: the dry-run plan matches
   [buzz/community.json](../buzz/community.json) 12/12, all canvases and seeds
   exist with exactly one marker each, and the private `foundry`/`maintainers`
   plus ten open channels match the intended visibility (labs/002 §1 items
   6–7). The inspection procedure and failure handling are in the
   [bootstrap runbook](../buzz/BOOTSTRAP_RUNBOOK.md); a dedicated hosted
   inspection checklist is planned as Wave O work
   ([SWARM_PHASE2_PLAN.md](../SWARM_PHASE2_PLAN.md), task O3 — not yet in the
   repository).
3. **Still missing and why.** Nothing hosted can be evidenced before the
   owner-operated apply, which requires the owner identity and the hosted
   community (Gate 1). Agents must never run `--apply` or hold owner
   credentials.
4. **Human action checklist.**
   - [ ] After Gate 1 and a fresh dry run: run the bootstrapper locally with `--apply` (owner environment only).
   - [ ] Inspect all twelve channels: streams only, `foundry` and `maintainers` private, the ten participation channels open as intended.
   - [ ] Inspect every canvas and one-time seed message; check the `start-here` path.
   - [ ] If a seed may be duplicated, stop repeated applies and inspect recent history manually (marker check sees up to 100 messages only).
   - [ ] Retain only non-secret channel/seed evidence.
5. **Evidence completeness.** partial — configuration and dry-run evidence are
   verified; the hosted inspection is impossible until the owner applies.

### Hold 6 — Steward escalation readiness

1. **What the hold needs.** Privately name the sponsor, configure a visible
   member-usable escalation route/label, test human receipt, and enable the
   Steward only after the prerequisite passes.
2. **Evidence now available.** The Steward profile fails closed: "Do not
   enable this profile until the human sponsor has configured and tested a
   member-actionable escalation reference," with a prescribed fallback message
   when the reference is absent ([STEWARD.md](../buzz/agents/STEWARD.md)); the
   sponsor model and channel exclusions are in the least-membership table
   ([security runbook](../ops/BUZZ_SECURITY.md)); a human-executed readiness
   test script is planned as Wave O work
   ([SWARM_PHASE2_PLAN.md](../SWARM_PHASE2_PLAN.md), task O2 — not yet in the
   repository).
3. **Still missing and why.** The sponsor name is private; the visible route
   and its receipt test live on the hosted surface (needs Gate 1) and require
   a human to receive and confirm — agents can neither configure a member
   escalation route nor verify that a human received anything.
4. **Human action checklist.**
   - [ ] Privately name the Steward's human sponsor.
   - [ ] Configure a visible escalation route/label members can actually use, citing no private address or invitation link.
   - [ ] Test that a human receives and can act on an escalation through it.
   - [ ] Record the deployment prerequisite as passed (sponsor named privately, route cited, receipt confirmed); only then enable the Steward.
5. **Evidence completeness.** partial — the fail-closed prerequisite is
   specified; configuration and testing are human-hosted work.

### Hold 7 — Publication destinations

1. **What the hold needs.** For each selected post, a human replaces every
   bracketed token with an approved repository/Buzz/channel/issue destination
   or handle, click-tests it, and retains a non-secret check record; no
   reusable invitation link.
2. **Evidence now available.** The social kit intentionally retains its 26
   bracketed tokens and is the sole whole-file publication-template exception
   ([SOCIAL_KIT.md](../content/launch/SOCIAL_KIT.md)); the token inventory was
   verified twice by the labs/003 checker (26/26 per-token counts in runs T3
   and T4 at `6f205d6`, against the R4 claim-audit exception data
   [labs/003](../labs/003-workflow-redesign-trial.md)), and the publication
   checks each post must pass are in the
   [funnel](../ops/INVITE_FUNNEL.md). The real destinations do not exist
   until Gate 3 (GitHub) and Gate 1 (Buzz) are confirmed.
3. **Still missing and why.** Token replacement and click-testing are
   inherently per-post human work with real, approved destinations; an agent
   must not invent handles, publish, or verify links on a human's behalf.
4. **Human action checklist.**
   - [ ] For each selected post, replace every bracketed token with the approved destination or handle.
   - [ ] Click-test every link and confirm the invitation wording follows the funnel rules (no reusable invitation link).
   - [ ] Retain a non-secret check record per post.
5. **Evidence completeness.** partial — the inventory and its verification are
   solid; substitution and click-testing await the confirmed destinations.

---

## What no packet can supply

Five inputs are human or hosted by design, and every gate above reduces to
some combination of them: the owner Buzz identity and anything derived from it
(creation, backup, apply); private names (recovery custodian, sponsors,
release/moderation owners); the live hosted community and its inspection;
provider billing credentials; and the recorded human decisions themselves
(gate approvals, promotion decisions, launch date). The [evidence-record
template](../templates/RELEASE_EVIDENCE.md) shows where the private evidence
is pointed to without being copied.
