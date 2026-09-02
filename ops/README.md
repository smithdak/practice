# Operations

How Practice is run, day to day, by the humans who maintain it. Find your
situation in the first table and open that runbook.

Practice is pre-launch. Every owner gate and operating hold is recorded OPEN in
[the owner review packet](../release/OWNER_REVIEW.md), no community agent is
enabled, and nothing is promoted to run unattended. The decision to launch
lives in [release/](../release/README.md), not here.

## Find the runbook for your situation

| Situation | Open | Also |
|---|---|---|
| I am the maintainer on duty this week | [WEEKLY_CADENCE.md](WEEKLY_CADENCE.md) — the passes, the output each one produces, and who approves it | [cadence.yaml](cadence.yaml) is its machine-readable mirror, read by `scripts/cadence.py` (`make cadence`). Change the document first, then the mirror |
| An issue or contribution arrived | [MAINTAINER_RUNBOOK.md](MAINTAINER_RUNBOOK.md) — queues, artifact review, releases, moderation, continuity | Issue triage: the policy and labels are [.github/TRIAGE_POLICY.md](../.github/TRIAGE_POLICY.md); the method is [practices/004-issue-triage.md](../practices/004-issue-triage.md); the records live in [triage/](triage/README.md) |
| We are running the private beta | [BETA_OPS.md](BETA_OPS.md) — roles (never names), the beta-only daily pass, escalation routes | |
| Someone needs Buzz access, or we suspect a security problem | [BUZZ_SECURITY.md](BUZZ_SECURITY.md) — identity ownership and recovery, the least-membership model for agents | The hub itself is mapped in [buzz/](../buzz/README.md) |
| How healthy is Practice? | [METRICS.md](METRICS.md) — the measurement contract: definitions, evidence rules, data never collected | [metrics/](metrics/README.md) holds the collector notes for `scripts/collect_metrics.py` (`make metrics`); reports are generated on demand, not committed |
| We are running the first live session | [FIRST_PRACTICE_SESSION.md](FIRST_PRACTICE_SESSION.md) — the Workflow Clinic: intake, consent, run of show, capture, follow-up | |
| We are reaching and inviting people | [outreach/](outreach/) — the kit below | Gate 5 and holds 1 and 7 in the owner review packet govern any public use |
| What may run without a person? | [OPERATING_LOOP.md](OPERATING_LOOP.md) — what runs on command, what needs a person, the four runners, the A3 substrate | [autonomy/](autonomy/README.md) and [ledger/](ledger/README.md), mapped below |

## Outreach kit

| File | What it holds |
|---|---|
| [outreach/INVITE_FUNNEL.md](outreach/INVITE_FUNNEL.md) | Public discovery to a useful Buzz entry: request review, invitation issuance, the private intake ledger |
| [outreach/SOCIAL_KIT.md](outreach/SOCIAL_KIT.md) | Reusable launch copy. A human replaces every bracketed placeholder before publishing; it is the one whole-file template exception in release validation |
| [outreach/LAUNCH_VIDEO.md](outreach/LAUNCH_VIDEO.md) | The flagship launch video brief |
| [outreach/FIRST_10.md](outreach/FIRST_10.md) | The first ten flagship content briefs. Briefs, not reports of completed events |

## Unattended action

Nothing is promoted. Every catalogued operation refuses today; run `make autonomy` to see it refuse.

| Path | What it holds |
|---|---|
| [autonomy/README.md](autonomy/README.md) | The two records, the guard that reads them, how a promotion would be made, and how to reverse one |
| [autonomy/operations.yaml](autonomy/operations.yaml) | The catalog: five operations that could one day run unattended, each with its command, write scope, reversal, and current level. A catalog entry permits nothing |
| [autonomy/promotions.yaml](autonomy/promotions.yaml) | The governance record. Ships as `kill_switch: engaged` and `promotions: []` |
| [autonomy/CANDIDATES.md](autonomy/CANDIDATES.md) | One dossier per catalogued operation: the case for and against promoting it |
| [autonomy/PROMOTION_PROPOSAL.md](autonomy/PROMOTION_PROPOSAL.md) | The form a human signs to promote an operation. None has been signed |
| [autonomy/PR_REVIEW_CONTRACT.md](autonomy/PR_REVIEW_CONTRACT.md) | What a reviewer agrees to when merging a pull request opened by an unattended run |
| [ledger/](ledger/README.md) | Append-only run records. Empty except one labeled hypothetical sample of a refused run |
| `status/` | Does not exist. It is the declared write scope of the two snapshot operations; a permitted run would write there, and such a run arrives as a pull request |

## Rules that hold across this directory

- Agents draft, triage, and recommend. A human decides acceptance, moderation,
  access, release, and promotion ([docs/DECISIONS.md](../docs/DECISIONS.md)).
- Buzz holds the working conversation; Git is the durable record
  ([docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)).
- Roles, not names. Names, handles, contact routes, and secrets stay in the
  private maintainer record, never in these files.
- Two records must both change before any operation runs unattended: a signed
  promotion and a released kill switch. Either alone is refused.

## Old paths

| Old | Now |
|---|---|
| `ops/AUTONOMOUS_OPERATION.md` | `ops/OPERATING_LOOP.md` |
| `ops/INVITE_FUNNEL.md` | `ops/outreach/INVITE_FUNNEL.md` |
| `content/launch/SOCIAL_KIT.md`, `LAUNCH_VIDEO.md`, `FIRST_10.md` | `ops/outreach/` |
