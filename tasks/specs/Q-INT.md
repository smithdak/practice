# Q-INT — Integrate accepted Phase 2 findings and re-run release validation

- **Wave:** 9
- **Lane:** integration
- **Recommended model tier:** strong
- **Mode:** integration
- **Dependencies:** Q6, Q7, O1, O2, O3, O4, O5

## Objective

Apply every accepted review correction across the repository, update the owner review evidence rows, and record the validation evidence.

## Read

- `AGENTS.md`
- `CONTEXT.md`
- `DECISIONS.md`
- `NON_GOALS.md`
- `QUALITY_BAR.md`

## Owned outputs

- `release/FINAL_INTEGRATION_REPORT_V2.md`
- `handoffs/Q-INT.md`

## Scope rule

This is an integration task. It may edit any project artifact except locked decisions, and must record a disposition for every finding it applies or declines.

## Requirements

- Apply accepted findings without reopening settled strategy.
- Update release/OWNER_REVIEW.md gate and hold rows to point at their Phase 2 evidence packets.
- Never assert an owner gate is cleared and never change a `maturity` or `evidence_quality` field.
- Run release validation, the unit tests, the link checker, and artifact validation.

## Acceptance

- [ ] Every accepted finding is applied or explicitly declined with a reason.
- [ ] All gate and hold statuses remain OPEN.
- [ ] All four validation commands pass and their output is recorded.
- [ ] `python3 scripts/validate.py --task Q-INT --root .` passes.
- [ ] `handoffs/Q-INT.md` records status, validation, decisions, risks, and deferred opportunities.
- [ ] The worktree is committed and clean.

## Stop conditions

Stop and write a `BLOCKED` handoff rather than guessing when a locked decision conflicts with this task, a current claim cannot be verified, required evidence is unavailable, or completing the task requires editing an unowned path.
