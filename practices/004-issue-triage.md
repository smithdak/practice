---
artifact_type: practice
title: "Triage community issues with an evidence-backed state machine"
summary: "Move each new community issue through categorize, verify, and route states so every state change carries written evidence and a human maintainer owns the accept decision."
maturity: proposed
capability: use
roles: [operator, engineer, individual-practitioner]
version: 0.1.0
license: CC-BY-4.0
created: 2026-09-01
updated: 2026-09-01
evidence_quality: none
secondary_capabilities: [automate]
tags: [issues, triage, evidence, routing, review, moderation-boundary]
---

# Triage community issues with an evidence-backed state machine

## Outcome

For one batch of community issues, produce a routing record in which every issue sits in exactly one state — `needs-info`, `ready-for-agent`, `ready-for-human`, or `wontfix` (closed) — and every state change names its category (bug or enhancement), the verification performed against the codebase, the evidence found or missing, and the next owner. A human maintainer, not the triager, makes the accept and close decisions.

This Practice is a triage and routing method. It does not decide priority by itself, does not resolve the underlying issue, and does not replace the moderation model in [docs/DECISIONS.md](../docs/DECISIONS.md): community agents and non-maintainer triagers may categorize, verify, and recommend, but they never silently remove people or content, and they never close an issue without a human decision recorded in the issue.

## Problem and scope

Community issue queues fail in two predictable ways. Unverified reports get routed as if they were facts, sending maintainers or agents to work on defects that do not reproduce; and routing happens silently, so a reporter cannot see why their issue moved or what would change the decision. Both patterns burn maintainer attention and erode contributor trust.

The unit of triage is one issue with a reporter, a claim, and a target codebase or artifact set. This Practice covers the recurring task of categorizing and routing new and returning issues. It does not cover moderation of conduct reports, which routes immediately to private human triage under the community moderation process; does not cover the fix work itself; and does not authorize any automated closing, deleting, or access change.

## Use when

- New issues or pull requests arrive faster than a maintainer can individually read them, or triage work is shared between humans and bounded agents.
- The project has a codebase or artifact set the triager can actually inspect to verify claims.
- A human maintainer exists who can own accept, close, and priority decisions.
- Routing criteria can be written down in advance rather than decided case by case.

For a personal project with a single maintainer reading every issue directly, a lightweight checklist may be enough; still write the routing reason so the decision survives a context switch.

## Inputs

- The issue queue and access to the codebase, documentation, and artifact set the issues concern.
- Written routing criteria: what counts as a bug versus an enhancement, and what each route means.
- A named human maintainer (or rotation) who owns accept and close decisions.
- For agent-assisted triage: a bounded agent identity with read access and the ability to label and comment only, consistent with the community's agent boundaries.
- A place to record state changes: the issue itself, plus the project's durable Git record.

Never paste secrets, credentials, private reporter details, or confidential material into an issue or triage record; point to an access-controlled system of record instead.

## Method

1. **Categorize before routing.** Read the full report and assign exactly one category: `bug` (the artifact behaves in a way its maintainer would not intend) or `enhancement` (a requested new capability or change). If the report is primarily a conduct, safety, access, or legal concern, stop triage: preserve only the minimum fact needed to route it and hand it to the private human moderation process. If the category is genuinely ambiguous, record both readings and route to `ready-for-human`.
2. **Verify against the codebase before routing.** Attempt to reproduce the claim or locate the code path, documentation line, or artifact it refers to. Record the version or commit checked, what was tried, and what was observed versus expected. Never invent repro steps, environment details, error messages, or versions; an attempt that did not happen is recorded as "not attempted," and information the reporter did not provide is recorded as missing, not guessed.
3. **Apply the decision rules.** Route using the table below. Every route must carry written evidence — the triager's own verification result or an explicit statement of what is missing.
4. **Write the state-change record in the issue.** Use one short entry per change: state moved from → to, category, evidence (commands run, files or lines inspected, commit checked), the specific ask when routing to `needs-info`, and the next owner or check point. A reporter reading the record should be able to tell what would change the decision.
5. **Leave accept and close to the human maintainer.** `ready-for-agent` means verified, bounded, and safe for agent-assisted work under review — it does not mean accepted; the maintainer still reviews the resulting change. `wontfix` and all closures require a human decision with a written reason and, for duplicates, a pointer to the retained issue.
6. **Re-triage on new information.** If the reporter supplies missing details, the code changes, or verification contradicts the original route, move the issue back through steps 1–3 and append the new record. A closure may be reopened this way; it is never treated as final truth about the codebase.

| Verification result | Category | Route | Required written evidence |
|---|---|---|---|
| Claim reproduced or confirmed in the code at a recorded commit; fix is bounded and touches no permissions, security, licensing, data, or conduct scope | Bug | `ready-for-agent` | Repro steps or code path, commit checked, observed versus expected |
| Real defect, but scope needs judgment: priority, breaking change, permissions, security, licensing, or cross-area impact | Bug | `ready-for-human` | Same evidence, plus the specific decision the maintainer must make |
| Cannot reproduce; missing version, environment, or steps | Bug (unverified) | `needs-info` | What was tried, what is missing, a specific ask, and a check point |
| Behavior matches documented or intended behavior | Bug (expected) | `wontfix`, human confirms | Pointer to the doc or code line plus the verification note |
| New capability with a stated problem, benefit, and plausible scope | Enhancement | `ready-for-human` | Problem statement, affected workflow, alternatives already checked |
| Request duplicates existing work or lacks a use case | Enhancement | `needs-info` or `wontfix`, human confirms | Pointer to the duplicate, or the specific missing questions |

**Expected output:** a routing record per issue — category, verification result, state, evidence, next owner — plus a human decision record for every closure or acceptance.

## Evaluation

This is a proposed method; no execution evidence is claimed. Trial it on one bounded batch of real issues in a repository the triager can inspect. A reviewer who did not perform the triage should be able to answer all of the following from the records alone:

- For each issue: was the category supported by the report, and was verification actually performed (commit, command, or file inspected) before routing?
- Does every `ready-for-agent` route have evidence a maintainer could act on, and did a human make the accept decision?
- Does every `needs-info` ask name what is missing and a check point, and does every closure have a written human-owned reason?
- Did any state change remove content, restrict a person, or close an issue without a human decision? (Any yes fails the trial.)

Accept the trial when every question has a specific, inspectable answer and the maintainer audit finds no unverified routing and no invented repro content. Do not infer faster resolution or higher accuracy from a single batch; measuring that requires comparing triage quality across periods with a stated method.

## Implementation

### Minimal: routing record per issue

Post the state-change record directly in each issue using a fixed short form:

```text
State: needs-info -> ready-for-human
Category: bug (unverified -> escalated)
Evidence: attempted repro on commit <hash>; build fails for a different
  reason than reported; cannot confirm without <missing detail>
Ask: reporter to state version and environment; maintainer to confirm scope
Next check: <date or event>
```

Keep a running triage log (one file or ledger row per issue) so a maintainer can audit a batch without opening each thread.

### Advanced: audited state machine with agent-assisted triage

Encode the states and transitions as labels, keep the decision-rules table in the repository next to the issue templates, and have a bounded agent draft the verification record and recommended route for a human to confirm. Add a periodic audit: a maintainer who did not triage samples recent state changes and checks each against the table. Automation may propose; it may never close, delete, restrict access, or mark work accepted. The agent boundary follows the community's moderation and agent-access rules; deviations are incidents, not shortcuts.

## Failure modes

The following are anticipated failure hypotheses for the first trial:

- **Triaging without verification:** A report is routed on its face value. Consequence: maintainers or agents chase defects that do not exist while real ones wait. Prevention: no route without a recorded verification attempt or an explicit `needs-info` ask naming what is missing.
- **Invented repro steps:** The triager fills gaps with plausible commands, versions, or error messages. Consequence: the record looks authoritative and misdirects the fix. Prevention: record only what was actually run and observed; write "not attempted" or "unknown" otherwise; audit records for detail no one could have produced from the report.
- **Silent closure or moderation drift:** An agent or non-maintainer closes an issue, deletes content, or restricts a participant. Consequence: contributor trust and the community's human-owned moderation decision are violated. Prevention: closure and accept are human-owned state changes; agents label and recommend only; treat any violation as an incident with a correction record.
- **Needs-info dead end:** Issues are parked in `needs-info` forever. Consequence: reporters are ignored and the queue decays. Prevention: every `needs-info` entry carries a check point and a next owner; overdue items surface in the maintainer review.
- **Stale routing:** Code changes make an old verification result wrong. Consequence: work starts from false premises. Prevention: re-verify when the affected area changes and date every verification record.
- **Duplicate churn:** Two issues get independent, conflicting routes. Consequence: double work and contradictory decisions. Prevention: search for duplicates during categorization; mark duplicates with a pointer to the retained issue before routing.

## Evidence

Initial maturity is **proposed** and evidence quality is **none**. This repository contains the method, decision rules, a hypothetical example, and a planned trial only; it contains no completed triage run or measured outcome. What would count as promotion evidence: a recorded single application (for example, a Lab record such as `labs/NNN-issue-triage-trial.md`) containing the batch description, per-issue routing records, the maintainer audit result, observed failures and corrections, and limitations. Promote to `tested` only after a human reviews that record under the Practice schema; a clean-looking queue or positive comments are not evidence.

## Worked hypothetical example

The following is a **hypothetical example** for a hypothetical repository, not a report of a real issue or result.

A contributor files: "The link checker crashes on relative links." Triage proceeds:

1. **Categorize:** bug — the tool is documented to handle relative links.
2. **Verify:** the triager runs the checker on a sample relative link at commit `a1b2c3d` (hypothetical hash) and sees a different, handled warning instead of a crash; the reporter's claimed stack trace is not reproducible.
3. **Route:** `needs-info` — the report lacks the tool version and the actual link that crashed. The record states what was tried, what was observed, and asks specifically for the tool version and a sample link, with a check point at the next weekly triage pass.
4. **Maintainer action:** at the check point the reporter supplies the missing detail; the triager re-verifies, reproduces the crash, and moves the issue to `ready-for-human` because the fix touches the parser's security-relevant input handling — outside agent scope. The maintainer accepts the scoped fix, and only then may agent-assisted work begin under human review.

The example demonstrates the two rules this Practice exists to enforce: no routing without a recorded verification attempt, and no state change that quietly removes the reporter's issue or bypasses the human accept decision.

## Variations

- A low-volume repository may merge triage into a single maintainer's weekly pass, but every routing decision still needs the written evidence line.
- Pull requests can be triaged with the same state machine by treating "review requested" as the `new` state; verification then includes reading the diff.
- A multi-project community may keep one shared decision-rules table with per-project overrides; overrides must be stricter, not looser.

## Changelog

- **2026-09-01 — 0.1.0:** Proposed an evidence-backed issue-triage state machine with categorize-verify-route steps, decision rules, human-owned accept and close decisions, the moderation boundary for agents, and a hypothetical worked example.
