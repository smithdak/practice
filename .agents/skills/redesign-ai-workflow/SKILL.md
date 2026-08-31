---
name: redesign-ai-workflow
description: Redesign one bounded recurring workflow into a reviewable mix of deterministic, AI-assisted, agentic, and human-owned steps with controls and a smallest safe experiment. Use for workflow redesign or automation planning, not for isolated one-off tasks.
---

# Redesign an AI-assisted workflow

## Source of truth

Read [Practice 002](../../../practices/002-workflow-redesign.md) completely before acting. It is the canonical method. Preserve required organizational, legal, safety, security, financial, and domain controls even when the user wants more autonomy.

## Inputs

Establish the workflow owner, trigger, intended outcome, start and end boundaries, current steps and handoffs, at least one representative exception, systems of record, permitted data and tools, known risks, approval owners, baseline observations, and recovery path. Label missing measures unknown rather than estimating them.

If the request is only to design the workflow, do not provision tools, change permissions, or execute external actions. Those changes require separate, explicit authorization.

## Workflow

1. Describe the present workflow from trigger to completed outcome, including waiting, checking, exception, and recovery steps. Record the current owner and control for each step.
2. Assign each step exactly one primary class: deterministic, AI-assisted, agentic, or human-owned. Explain the boundary. Model use alone does not make a step agentic.
3. For each proposed change, record least-necessary data and permissions, concrete failure consequence, human approval point, observable stop condition, rollback or recovery action, and audit evidence.
4. Keep consequential judgment and irreversible effects human-owned unless the responsible authority has separately approved a different control. Put approval before publishing, sending, spending, record mutation, access changes, or consequential recommendations.
5. Choose one reversible, low-risk slice as the smallest safe experiment. Cap its volume, duration, tools, and data; keep the prior path available; require review before external effect.
6. Define baseline and trial measures, representative and exception cases, acceptance checks, stop triggers, and the decision rule for continue, revise, or revert. Review severe failures individually rather than hiding them in an average.

## Deliverable

Produce a versioned workflow map, step classifications, access/risk/approval/rollback records, a baseline with unknowns preserved, an experiment card, and a decision record. Distinguish the current workflow, proposed design, and observed trial evidence. Do not imply that a proposal has run or that automation improves quality, speed, cost, or safety without evidence.

## Stop and failure handling

Do not begin an experiment when there is no accountable owner, no safe sample, no approval before a consequential effect, unclear data permission, no usable rollback, or an unbounded agentic step. Return the blocker, affected step, likely consequence, and smallest decision or redesign needed. If a trial hits a stop trigger, halt, preserve the record, restore the prior path, and route the failure to the named owner.
