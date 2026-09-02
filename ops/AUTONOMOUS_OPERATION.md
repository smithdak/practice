# Running Practice on the loop

**As of:** 2026-09-02

## Outcome and boundary

A maintainer should be able to find out what the community needs, in one
command, without reading six documents and working it out by hand. That is what
this document routes to.

It is deliberately not a plan to hand the community to agents. Autonomy here
means **the loop computes itself**; it does not mean an agent gains authority.
Every decision that was human-owned before this tooling existed is human-owned
after it. What changed is that the state of the loop, the bounds an agent
operates under, and the shape of what an agent hands back are now machine-
readable and checked, instead of being paragraphs each reader interprets alone.

Nothing in this document enables an agent. Owner gate 6 in
[the owner review packet](../release/OWNER_REVIEW.md) is open, so every entry in
the agent registry reads `status: not_enabled`, and every eval suite records
cases with no run behind them.

## What runs without a person, and what does not

| Runs without a person | Requires a person |
|---|---|
| Computing which cadence pass is due and what evidence is missing | Deciding to run a pass, or to skip it |
| Counting the repository-observable metrics with denominators | Every metric that needs a human observation |
| Assembling a release brief from committed evidence | Approving and publishing the brief |
| Checking a triage record carries the evidence its state requires | Moving a record into a human-owned state |
| Checking an agent's declared bounds against the channel map | Enabling an agent, or widening its bounds |
| Checking a returned packet against its contract | Judging whether the evidence supports the claim |

The right-hand column is not a temporary state of the tooling. It is
[the locked decisions](../DECISIONS.md) and [the non-goals](../NON_GOALS.md)
expressed as operations, and the left-hand column exists to make the right-hand
column cheap rather than to shrink it.

## The three contracts

| Contract | File | What it fixes |
|---|---|---|
| Agent bounds | [`buzz/agents/registry.yaml`](../buzz/agents/registry.yaml) | Which channels an agent reads and writes, what it may never do, who it escalates to, what must be true before it is enabled |
| Autonomy levels | [`docs/framework/AUTONOMY_LADDER.md`](../docs/framework/AUTONOMY_LADDER.md) | What `observe`, `draft`, `recommend`, and act-unattended mean; what evidence raises a level; what demotes one; which operations may never be automated |
| Handback shape | [`docs/schemas/AGENT_PACKET_SCHEMA.md`](../docs/schemas/AGENT_PACKET_SCHEMA.md) | What an agent returns: provenance and trust per input, a claim only when it carries a pointer, the refusals it made, and the one decision it hands to a role |

The three join at the agent id. A packet naming an agent the registry does not
list is rejected; a packet declaring more autonomy than the registry grants that
agent is rejected; the ladder's mapping fails its test if an agent or a cadence
pass is added without placing it. Those joins are checked in
`tests/test_contract_integration.py`, because each contract's own validator
would otherwise pass while the set of them drifted apart.

Verify the contracts:

```bash
make agents                                  # registry bounds and eval definitions
make packets PACKETS="path/to/packet.md"     # one or more returned packets
```

## The four runners

Each implements a procedure this repository already specified in prose. None of
them decides anything, and none is a build gate.

| Runner | Command | Reads | Hands back |
|---|---|---|---|
| Cadence | `make cadence` <br>`scripts/cadence.py` | [`ops/cadence.yaml`](cadence.yaml), handoffs, the owner review packet | Which pass is due, which handoffs are blocked, which gates and holds are open, which as-of dates are stale |
| Metrics | `make metrics` <br>`scripts/collect_metrics.py` | Artifact front matter, changelogs, link health | Each Git-observable metric with its denominator and coverage, and each remaining metric named as needing the human route |
| Release brief | `make brief SINCE=<rev> AS_OF=<date>` <br>`scripts/release_brief.py` | A commit range and its handoffs | A draft brief where every line carries a path or a commit, marked as needing approval |
| Triage | `make triage` <br>`scripts/triage.py` | Records under [`ops/triage/`](triage/README.md) | Whether each record carries the evidence its state requires, and who may move it next |

The cadence runner reads Git and knows nothing about Buzz activity. It reports;
it never exits non-zero on a due pass, because a report that behaves like a gate
creates work nobody has agreed to own. The same reasoning applies to the metrics
collector: see [`ops/metrics/README.md`](metrics/README.md) for what it can and
cannot see, and [`release/briefs/README.md`](../release/briefs/README.md) for the
approval rule a brief is subject to.

## A week on the loop

1. **Open the loop.** `make cadence` names the due passes, the blocked handoffs,
   the open gates and holds, and anything stale. Skip a pass with no output, as
   [the cadence](WEEKLY_CADENCE.md) already instructs; record nothing for it.
2. **Work the queues.** Triage arriving items into `ops/triage/` and check them
   with `make triage`. Safety, privacy, access, conduct, and legal items go
   straight to a human — the state machine refuses to let an agent resolve them,
   which is [the moderation model](../community/MODERATION.md) enforced rather
   than restated.
3. **Take agent work back.** An agent hands back a packet. Run `make packets`
   on it. A packet that validates is a packet worth reading, not a packet worth
   accepting: [the maintainer runbook](MAINTAINER_RUNBOOK.md) owns the judgment
   the validator cannot make.
4. **Measure honestly.** `make metrics` produces counts with denominators. Every
   metric it cannot see is printed as needing the human route in
   [the measurement contract](METRICS.md), never as a zero.
5. **Close the loop.** When a release is ready, `make brief` assembles the draft
   from committed evidence. A named human maintainer approves it before any part
   of it is published.

Steps 1, 2, 4, and 5 run today without an agent enabled — they read the
repository. Step 3 is the step waiting on gate 6.

## Before any agent is enabled

These are prerequisites, not a checklist an agent may complete on its own
behalf. Each traces to a record in [the owner review packet](../release/OWNER_REVIEW.md).

- **Gate 6, community-agent providers.** A human selects the agents and
  providers and adds credentials only in approved private systems.
- **Hold 6, steward escalation readiness.** The Steward fails closed until a
  member-actionable, human-owned escalation route is configured and a human has
  tested receipt. `scripts/steward_readiness_check.py` checks configuration
  only; it cannot test the route.
- **Behavioral eval evidence.** The cases in
  [`buzz/agents/evals/README.md`](../buzz/agents/evals/README.md) are defined and
  unrun. Defining a case is not evidence an agent passed it. A severe or major
  failure blocks enablement regardless of the aggregate.
- **A named human reviewer** for the packets that agent will hand back.

## Failure modes worth naming

- **A report read as a decision.** The cadence and metrics runners describe the
  repository. Treating a due pass as an assignment, or a count as a community
  outcome, converts a description into a claim nothing supports.
- **A validating packet read as an accepted packet.** The contract checks shape
  and provenance. It cannot check whether the evidence supports the claim or
  whether the work should have gone to an agent at all.
- **Bounds widened by editing one file.** Widening an agent's scope means
  changing the registry, the ladder mapping, and the eval suite together; the
  tests fail on a partial change, which is the point.
- **A brief published from a draft.** Every generated brief says it needs
  approval. Removing that line does not constitute approval.
- **Tooling mistaken for readiness.** None of this clears a gate or a hold. The
  repository is more operable than it was; it is not closer to launch by a
  single decision.

## Sources

- [Weekly operating cadence](WEEKLY_CADENCE.md) — the loop these runners compute.
- [Maintainer operating runbook](MAINTAINER_RUNBOOK.md) — the human judgment the
  runners do not replace.
- [Health and outcome metrics](METRICS.md) — the measurement contract.
- [Private beta operating kit](BETA_OPS.md) — intake routes and escalation.
- [Triage community issues](../practices/004-issue-triage.md) and [write release
  notes from committed evidence](../practices/005-release-notes.md) — the two
  methods the triage and brief runners implement.
- [Owner gates](../OWNER_GATES.md) and [owner review packet](../release/OWNER_REVIEW.md)
  — the decisions reserved to a human.
