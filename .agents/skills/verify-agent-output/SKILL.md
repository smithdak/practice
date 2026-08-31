---
name: verify-agent-output
description: Verify one bounded agent-produced artifact or change before it is accepted, merged, deployed, published, or used, tying each criterion to reproducible evidence and a recovery path. Use for acceptance review, not as a general quality slogan or a substitute for domain controls.
---

# Verify agent output

## Source of truth

Read [Practice 003](../../../practices/003-verification-gate.md) completely before acting. It is the canonical verification method. Apply any stronger domain, policy, or organizational controls in addition to it.

## Inputs

Identify the exact artifact or change version, intended effect, owner, authorized reviewer, acceptance criteria, exclusions, source or provenance record, approved checks and fixtures, baseline or diff, and rollback procedure. Classify impact as low, material, or consequential. If the effect or reviewed version is ambiguous, stop and resolve it first.

## Workflow

1. Preserve the accepted baseline and capture the exact diff or comparable before state. Use a dry run, staging area, or approval queue when available.
2. Trace each material claim, input, dependency, and changed setting to a permitted source or reproducible observation. Check current claims against authoritative sources and record the date or version. Preserve conflicts and missing evidence as `unknown` or `fail`.
3. Run the canonical universal checks for scope, criteria, evidence, source validity, representative and failure cases, diff review, safety and access, rollback, approval, and record quality.
4. Add every applicable artifact-specific check. Record commands or review procedures, expected behavior, observed behavior, result, and evidence location. An automated pass supports only the check it ran.
5. Inspect the complete change and possible side effects. Ask how the artifact could pass the listed checks while still violating scope or causing the relevant harm; add a check or escalate when that path is plausible.
6. Recommend `accept`, `revise`, or `reject`. A failed or unknown mandatory check cannot produce `accept`. Obtain the accountable human's approval before any publish, merge, deploy, external send, data or permission change, spending, or consequential use.
7. Release only the exact approved version. For material or consequential work, record monitoring, a stop trigger, and the recovery window.

## Deliverable

Produce an acceptance record containing the artifact identity and version, intended effect, impact, owner, reviewer, observable criteria, baseline/diff, sources, check results and evidence, failed or unknown items, rollback owner and steps, decision recommendation, and approval status. Keep secrets and unnecessary confidential or personal data out of the record; link to an approved system instead.

## Stop and failure handling

Do not self-approve, treat one green check as overall correctness, overwrite the baseline before acceptance, or convert missing evidence into a pass. When evidence, authority, permissions, or recovery is insufficient, preserve the artifact, recommend `revise` or `reject`, and state the smallest check, correction, or human decision needed. If an unexpected effect appears after release, stop further release and invoke the approved containment or rollback path.
