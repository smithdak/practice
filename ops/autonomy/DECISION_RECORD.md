# Unattended-action decisions

A running record of human decisions about what may be *attempted* unattended:
what is catalogued, what is promoted, and what was declined. Newest first.

[The governance model](../../community/GOVERNANCE.md) makes promotion to A3 a
reserved decision and [the autonomy ladder](../../docs/framework/AUTONOMY_LADDER.md)
requires it to be recorded with rationale and an effective date. A decision not
to promote is recorded the same way, so that "nothing is promoted" is a decision
someone made on a date for reasons, not a default nobody looked at. Governance
*changes* are recorded in [the amendments record](../../community/AMENDMENTS.md);
this file records decisions made under the governance as it stands.

A decision is in force only once it appears here. Anyone may request
reconsideration in a Git issue naming a factual error, new evidence, or a
material conflict, per the governance model.

---

## Decision 001 — Withdraw `staleness-sweep`; promote nothing

- **Status:** in force
- **Decided by:** founder
- **Recommended by:** the Director agent, from the candidate dossiers' own
  analysis. The recommendation was put to the founder as a question with the
  alternatives stated; the decision is the founder's.
- **Recorded:** 2026-09-03
- **Effective:** 2026-09-03
- **Changes:** [the operation catalog](operations.yaml), from which the
  `staleness-sweep` entry is removed; [the candidate dossiers](CANDIDATES.md),
  where its dossier stays as the record of why.
- **Does not change:** [the promotion record](promotions.yaml), which still
  reads `kill_switch: engaged` with an empty promotion list; [the renewal
  record](renewals.yaml), which is empty; the ladder; any owner gate or
  operating hold.

### What was decided

**1. The staleness sweep is folded into the cadence snapshot.** Of the two
options the dossier laid out, the founder chose Option A. The calendar-driven
half of the check, stale `As of:` dates and the coverage the rule reached, is
already computed by `scripts/cadence.py` through the same function in
`scripts/check_links.py` and printed in the cadence report's staleness section,
so one fact is reported by one run. The three tooling prerequisites the dossier
named stay where they were built: coverage in every run of the sweep and in the
cadence report, a malformed date reported as an error, and the opt-in
`--fail-on-stale` flag on the link checker. The link half of the sweep keeps
running in CI on every push, as it did before. The artifact-maintainer role
still owns the disposition of a stale finding, per the stale-content queue in
[`ops/cadence.yaml`](../cadence.yaml).

**2. No operation is promoted to A3.** Each remaining candidate was declined
for the reason its own dossier records, and each names what would reopen it:

| Candidate | Why not now | What would reopen it |
| --- | --- | --- |
| `cadence-snapshot` | Nobody has agreed to read a dated series that is one command away. | A named role that has agreed to read the series and can say what they would do with it; a line in the report stating the history depth it read; a token self-guard equivalent to the one in `scripts/release_brief.py`. |
| `metrics-snapshot` | A committed census series with no annotator is a trend line with no explanation, and the heading map can drift from the schemas silently. | The metrics README's retention policy rewritten by a human; a decision on sharing `ops/status/`; a check that fails when the heading map and the schemas disagree; a named reader role. |
| `contract-drift-check` | Redundant: CI already runs the same command on every push, and its failure mode is silence. | A recorded case of contract drift that CI structurally could not have caught. |
| `release-brief-draft` | The catalogued command lacks `--since` and `--as-of`, and there is no defensible unattended rule for either. | A recorded rule for both, or a redesign that removes the judgment. |

**3. Nothing here advances launch.** Every owner gate and operating hold that
was OPEN before this decision is OPEN after it.

### Why

The substrate exists so that a promotion, when one is made, is a record a
validator checks rather than a hope. It also exists so that *not* promoting is
cheap, and the dossiers make the case that today it is the right call: the one
candidate with unique calendar-driven value is better carried by a report the
operating loop already reads, and the others each name a prerequisite no person
has yet supplied. A first promotion should carry unique value and a named
reader. None does yet. Two independent records must change before anything
runs; neither changes here.

### Sources

- [The candidate dossiers](CANDIDATES.md), in particular the `staleness-sweep`
  section's overlap packet and each candidate's "The decision" section.
- [The promotion proposal template](PROMOTION_PROPOSAL.md), which a future
  proposal fills in.
- [Phase 5 report](../../swarm/reports/PHASE5_REPORT.md), where the
  prerequisites were built and the question was put.
