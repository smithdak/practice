# Release

Should Practice launch? The status of every owner gate and operating hold lives
in [OWNER_REVIEW.md](OWNER_REVIEW.md), and every row is **OPEN**. Nothing in
this directory is an approval.

Practice is pre-launch. All six method candidates carry `maturity: proposed`,
and the community hub is not open. A human records each approval; an unchecked
box or an agent-generated packet is not one.

## What is here

| File | What it holds | Open it when |
|---|---|---|
| [OWNER_REVIEW.md](OWNER_REVIEW.md) | Status per owner gate (eight) and evidenced operating hold (seven), the locked launch model, and the approval sequence. Human-owned | Deciding, or checking what is still open |
| [GATE_EVIDENCE.md](GATE_EVIDENCE.md) | One evidence packet per open gate and per hold: what the repository can show, and what a human still has to supply | Reviewing one gate before deciding it |
| [LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md) | Dry run, then private beta, then public launch. Every box is unchecked by design | Sequencing the launch steps |
| [HOSTED_INSPECTION.md](HOSTED_INSPECTION.md) | The post-bootstrap check that the hosted Buzz surface matches `buzz/community.json`; the evidence for hold 5 | After the owner-operated apply |
| [PROMOTION_PACKETS.md](PROMOTION_PACKETS.md) | The decision packet for the first three method candidates. None is promoted, and no maturity value changes here | Deciding whether a candidate becomes a tested Practice |
| [briefs/](briefs/README.md) | Generated release briefs, drafts until a named human approves one; its README states the rules | Assembling or reviewing a release brief |

## Where the rest lives

- The gate list and its defaults: [docs/OWNER_GATES.md](../docs/OWNER_GATES.md).
- The independent findings the evidence cites: [reviews/](../reviews/README.md).
- The phase integration reports: [swarm/reports/](../swarm/reports/).
- The runbooks a launch step points at: [ops/](../ops/README.md) and [buzz/](../buzz/README.md).

## Rules

- Release validation, `python3 scripts/validate.py --release`, is structural.
  Passing it is necessary and is not launch approval.
- No keys, credentials, recovery codes, participant data, or private invitation
  links in any evidence record.
- Public copy says "proposed method" or "Practice candidate" until a human
  records a promotion decision.

## Old paths

| Old | Now |
|---|---|
| `release/FINAL_INTEGRATION_REPORT.md` | `swarm/reports/PHASE1_REPORT.md` |
| `release/FINAL_INTEGRATION_REPORT_V2.md` | `swarm/reports/PHASE2_REPORT.md` |
| `release/PHASE3_REPORT.md` | `swarm/reports/PHASE3_REPORT.md` |
| `release/PHASE4_REPORT.md` | `swarm/reports/PHASE4_REPORT.md` |
