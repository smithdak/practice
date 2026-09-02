# Phase 3 report — autonomous operation readiness

**As of:** 2026-09-02 · **Integrator:** W1 · **Baseline:** `5890629` (Phase 2
complete) · **Phase 3 commits:** `ce2c2f2` (plan), `502eee9` (wave 1),
`fdb4c45` (wave 2), and the integration commit carrying this report.

## Outcome

Phase 3 is integrated. Nine tasks turned the repository's prose operating
procedure into machine-readable contracts, deterministic offline runners, and
observable test cases, and joined them into one operating document.

**No owner gate or operating hold changed status. No `maturity` or
`evidence_quality` field changed. No agent was enabled.** Every row in
[the owner review packet](../../release/OWNER_REVIEW.md) remains open, all six method
candidates remain proposed with no evidence quality claimed, and every entry in
the agent registry reads `status: not_enabled` because owner gate 6 is open.

The repository is more operable than it was. It is not closer to launch by a
single decision, and nothing here substitutes for one.

## What was built

| Wave | Task | Output |
| --- | --- | --- |
| S — contracts | S1 | [`buzz/agents/registry.yaml`](../../buzz/agents/registry.yaml) and its boundary validator: channel scope, guardrails, escalation, enablement prerequisites |
| | S2 | [The packet contract](../../docs/schemas/AGENT_PACKET_SCHEMA.md), template, and validator: provenance per input, no claim without a pointer, a required refusals section |
| | S3 | [The autonomy ladder](../../docs/framework/AUTONOMY_LADDER.md) and its policy test: four levels, seven permanently ineligible operations, nineteen operations mapped |
| T — runners | T1 | [`ops/cadence.yaml`](../../ops/cadence.yaml) and `scripts/cadence.py`: what is due, what is blocked, what is open, what is stale |
| | T2 | `scripts/collect_metrics.py`: the Git-observable part of [the measurement contract](../../ops/METRICS.md), with denominators |
| | T3 | `scripts/release_brief.py` and [the first generated brief](../../release/briefs/2026-09-02-phase-2.md) |
| | T4 | `scripts/triage.py`: the [Practice 004](../../practices/004-issue-triage.md) state machine, enforced |
| V — evidence | V1 | [`buzz/agents/evals/`](../../buzz/agents/evals/README.md): 80 cases across five agents, including seven adversarial topics each |
| W — integration | W1 | [The operating procedure](../../ops/OPERATING_LOOP.md), the cross-contract tests, CI wiring, and this report |

Test count moved from 145 to 562.

## What the phase deliberately did not do

Autonomy here means the loop computes itself. It does not mean an agent gained
authority. The following were reviewed and left exactly where they were:

- Moderation, banning, and content removal stay human-owned. The triage state
  machine encodes this rather than restating it: a record whose last actor is an
  agent cannot sit in a human-owned state, and the safety, privacy, access,
  conduct, and legal categories are never agent-actored in any state.
- Promotion of a method to a tested Practice stays a human decision with
  recorded evidence.
- Publication, merging, and announcement stay human-approved. Every generated
  brief says so on its face.
- The owner identity and private key are never handled by an agent.
- No scheduled Buzz workflow became a dependency. Every runner is a local,
  offline script.
- Nothing is mapped to the unattended autonomy level, and raising anything there
  is a human decision recorded through the governance path.

## Findings the work surfaced

These were found by building the checks, not asserted in advance.

1. **The packet schema's own worked example declared an autonomy level the
   registry does not grant.** Enforcing the cross-contract bound rejected the
   example on its first run: it declared `recommend` for the Research Auditor,
   which the registry bounds to `draft`. The example is corrected and the
   schema's claim that the validator "checks only the identifier" is no longer
   true. This is the drift the join was written to catch, found immediately.
2. **The Steward's most consequential guardrail is not observable.** It is the
   only agent with a write surface, and its profile says to provide a draft for
   human review instead of posting when a reply is "ambiguous or consequential".
   No case can distinguish a correct post from one that should have been
   withheld, because the condition has no stated boundary. The eval suite
   records the closest observable case and the gap.
3. **Five profile terms are used as if they were defined and are not**:
   "internal reasoning", "safe-to-share" and "approved-to-share",
   "maintainer-confirmed record", "when authorized", and "the assigned
   workspace". Each carries weight in a guardrail. Each is recorded in
   [the V1 handoff](../handoffs/V1.md).
4. **All five profiles are silent on partial compliance with an injected
   instruction.** The cases score all-or-nothing, which is stricter than the
   profiles state.
5. **The Release Editor has no realistic path above `draft`.** Its only
   conditional channel is `announcements`, and publication is permanently
   ineligible even for the unattended level.
6. **One cadence pass has no registered agent.** The build pass names an
   assigned construction agent; no persistent builder profile exists, so that
   row bounds an assignment rather than an identity.
7. **The Guide Maintainer holds five channel memberships its own profile never
   uses.** Recorded read-only pending a human decision on whether it needs Buzz
   membership at all.

## What this does not establish

- **No agent has been run against any case.** The 80 eval cases are definitions.
  Defining a case is not evidence an agent passed it, and no behavioral run
  exists for any community agent.
- **No metric here measures the community.** The collector reads repository
  state. Seven metrics the measurement contract defines are printed as needing a
  human observation route, not as zeros.
- **A validating packet is not an accepted packet.** The contract checks shape,
  provenance, and bounds. Whether the evidence supports the claim, whether the
  action is proportionate, and whether the work should have gone to an agent at
  all remain human judgments.
- **The cadence report is not an assignment.** It says what the repository shows;
  it does not create an obligation, which is why it never exits non-zero on a due
  pass.
- **None of this is launch readiness.** Every gate and hold that blocked public
  launch before this phase blocks it now.

## Verification

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests` | 562 tests, OK |
| `python3 scripts/validate.py --release --root .` | Validation passed |
| `python3 scripts/validate_artifacts.py --root .` | Passed: 1 guide, 6 guide modules, 4 labs, 6 practices, 1 story |
| `python3 skills/evals/validate.py --root .` | Passed for 5 skills |
| `python3 scripts/validate_agents.py --root .` | Agent registry validation passed |
| `python3 scripts/validate_agent_evals.py --root .` | Passed; cases are defined, no run is recorded |
| `python3 scripts/triage.py validate ops/triage --root .` | 1 record, 0 violations |
| `python3 scripts/check_links.py .` | 321 files, 846 targets, 0 broken, 0 stale |

`make checks` runs all of these in the order CI runs them. CI now fetches full
history, because the guard comparing the committed brief against a fresh
generator run skips itself on a shallow clone.

## What a human decides next

Nothing in this phase is actionable by an agent. In rough order of what unblocks
the most:

1. **Whether the Steward's posting condition should be tightened before it is
   ever enabled.** Finding 2 is the one place where a bound exists on paper and
   not in anything checkable. Either the profile gains an observable condition,
   or the Steward launches at `draft` with no write surface.
2. **The five undefined profile terms** in finding 3, each of which currently
   means whatever its reader assumes.
3. **Owner gate 6 and hold 6**, which together govern whether any agent runs at
   all, and which no amount of tooling can clear.
4. **Whether the eval cases are the right cases**, before any run makes them
   look authoritative.

## Sources

- [Phase 3 plan](../plans/PHASE3_PLAN.md) — the task inventory and constraints.
- [Running Practice on the loop](../../ops/OPERATING_LOOP.md) — the operating
  procedure this phase produced.
- [Owner review packet](../../release/OWNER_REVIEW.md) — the gates and holds, all still open.
- Handoffs `S1`, `S2`, `S3`, `T1`, `T2`, `T3`, `T4`, `V1`, and `W1` under
  [`swarm/handoffs/`](../handoffs/) — per-task decisions, risks, and deferrals.
