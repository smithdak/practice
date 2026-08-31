---
artifact_type: practice
title: "Verify an agent's output before accepting or shipping it"
summary: "Apply universal and artifact-specific checks, record evidence, obtain required human approval, and keep a reversible path before accepting agent-produced work."
maturity: proposed
capability: use
roles: [individual-practitioner, operator, engineer]
version: 0.2.0
license: CC-BY-4.0
created: 2026-08-31
updated: 2026-08-31
evidence_quality: none
secondary_capabilities: [learn, automate, build]
tags: [agents, verification, review, evidence, rollback]
---

# Verify an agent's output before accepting or shipping it

## Outcome

Produce an acceptance record that ties each material acceptance claim to observable evidence, records failed or unknown checks, identifies the accountable human, and states whether the artifact may be accepted, revised, or rejected. Keep the artifact unchanged and reversible until the gate passes.

This Practice is a review method, not a guarantee that an agent is correct. An agent may prepare evidence, run permitted checks, and suggest a decision; a human remains accountable for acceptance where this Practice requires it.

## Problem and scope

Agent output can look complete while containing unsupported claims, broken behavior, unsafe settings, or an unreviewed side effect. The same verification habit must work for a research brief, a public article, source code, configuration, or an operational action.

The unit of review is one bounded artifact or change set with a named owner, intended use, and acceptance criteria. Do not use this Practice as a substitute for required legal, clinical, security, financial, safety, privacy, or organizational controls. Do not approve a consequential action solely because an automated check passed.

## Use when

- An agent creates, edits, summarizes, transforms, recommends, or executes work that another person may rely on.
- The output will be published, merged, deployed, sent externally, used to change data or access, spend money, or inform a consequential decision.
- A reviewer needs a reproducible reason to accept, request changes, or reject the result.

For a disposable, low-risk draft, a lighter informal check may be enough; label it as a draft and do not treat it as accepted work.

## Inputs

- The task request, scope, intended audience or system, and a unique artifact or change identifier.
- Acceptance criteria stated before review, including exclusions and stop conditions.
- The agent's output, relevant intermediate files, and a diff against the approved starting state when applicable.
- Source register or provenance for material facts, inputs, dependencies, and generated content.
- Permitted test fixtures, test commands, sample cases, or review tools.
- An owner, a reviewer with suitable domain authority, and an approved rollback or recovery procedure.

Never place secrets, private keys, access tokens, or unnecessary personal or confidential data in the evidence record. Point to an approved system of record instead.

## Method

1. **Frame the gate.** Record the artifact type, version or commit, intended effect, owner, reviewer, acceptance criteria, and what is explicitly out of scope. Classify impact: low, material, or consequential. If the intended effect is unclear, stop and ask the owner.
2. **Preserve the starting point.** Save the original artifact or a recoverable version and capture the exact diff. For an external action, use a dry run, staging area, or approval queue when available. Do not overwrite the accepted baseline before the gate passes.
3. **Check provenance and sources.** For every material claim, input, dependency, or changed setting, record its source, version/date, permitted use, and the location of supporting evidence. Validate primary or authoritative sources for claims that can change. Mark unavailable, conflicting, or stale evidence as `unknown` or `fail`; never fill the gap from memory.
4. **Run universal checks.** Apply the checklist below. An automated pass is evidence about that check only, not proof of overall correctness. Attach commands, test identifiers, screenshots, logs, links, or reviewer observations sufficient for another authorized reviewer to reproduce the decision.
5. **Run artifact-specific checks.** Select the checks for the output type below and add domain controls required by the owner or policy. Test representative cases and at least one boundary, adversarial, or failure case. Record expected versus observed behavior.
6. **Review the diff and side effects.** A human inspects what changed, what did not change, permissions, dependencies, citations, and any possible effect outside the stated scope. Ask: “Could this pass while still causing the intended harm or an unsupported claim?” Add a check or escalate if yes.
7. **Decide before effect.** The reviewer records `accept`, `revise`, or `reject`, with each criterion linked to evidence. `accept` is allowed only when required checks pass, mandatory unknowns are resolved, and rollback is tested or clearly executable. A failed, unknown, or missing mandatory check means `revise` or `reject`. If an external policy permits an exception, record it as a separate human-owned escalation; the gate itself does not pass.
8. **Obtain mandatory approval and release.** The accountable human signs the record before publication, merge, deployment, external communication, data mutation, access or permission change, spending, or a consequential recommendation. Release the exact reviewed version; record where it went and when.
9. **Monitor and recover.** For material or consequential work, watch the first relevant outcome and keep the rollback path available for the defined recovery window. If a defect, unexpected side effect, or new contradictory source appears, stop further release, notify the owner, revert or contain using the approved procedure, and append the incident and correction to the record.

### Universal checklist

Mark each item `pass`, `fail`, or `unknown`; attach evidence, not just a statement.

- **Identity and scope:** Is the artifact/version and intended effect unambiguous? Did the work stay within the request and permissions?
- **Acceptance criteria:** Is every criterion observable, and is each one tied to a result?
- **Evidence:** Does every material factual or behavioral claim have provenance or a reproducible observation? Are uncertainty and conflicts labeled?
- **Source validation:** Were authoritative sources checked for freshness, scope, and permitted use? Are citations or references accurate and sufficient?
- **Tests or examples:** Were representative cases plus a boundary, adversarial, or failure case checked? Are expected and observed results recorded?
- **Diff review:** Did a human inspect the complete change and unintended additions, deletions, dependencies, and side effects?
- **Safety and access:** Were privacy, security, licensing, policy, and least-necessary-access constraints checked for this context?
- **Rollback:** Is the pre-change state preserved, and is a tested or clearly executable recovery path owned by someone?
- **Approval:** Has the right human approved before the relevant external or consequential effect?
- **Record quality:** Could another authorized reviewer reproduce the decision from the record without relying on an oral explanation?

### Artifact-specific checks

Use only checks that apply, then add domain-specific controls. Examples are not evidence of a successful run.

| Artifact | Minimum checks before acceptance |
| --- | --- |
| Research, analysis, or data brief | Trace every material claim to a source or supplied dataset; check dates, scope, calculations, units, and contradictory evidence; label inference, uncertainty, and missing data; manually inspect quoted or tabulated material. |
| Public or internal content | Compare against the brief and style/accessibility requirements; verify names, links, citations, permissions, and sensitive details; check that examples are labeled and claims are not stronger than their evidence; preview the rendered artifact. |
| Code or automation | Review the full diff; run relevant tests, lint/type checks, and a failure or permission-boundary case; inspect dependencies, secrets handling, error paths, logging, and resource effects; test rollback or disablement in a safe environment. |
| Configuration, prompt, or policy | Compare each setting with the approved baseline; validate schema, precedence, defaults, permissions, and incompatible combinations; test safe behavior for missing, malformed, and unauthorized input; preserve the prior version. |
| Operational action or recommendation | Use dry run or staging where possible; confirm target, scope, authorization, timing, and blast radius; obtain domain-owner approval; record execution and monitoring signals; define a stop trigger and recovery action before starting. |

If an artifact spans types, apply every relevant row. If the reviewer cannot perform a required check or lacks authority, the status is not `accept`.

## When human approval is mandatory

Named human approval is required before an artifact is published, merged, deployed, sent to an external party, used to change records or permissions, used to spend or commit resources, or used to make a high-impact decision. It is also required when evidence conflicts, a mandatory check is unknown, the work exceeds scope, a rollback has not been tested for a material change, or a policy or domain owner requires it. The agent may assemble the packet and recommend a decision, but may not self-approve or silently bypass a failed gate.

## Evaluation

This is a proposed method; no execution evidence or effectiveness claim is made. Trial it on one bounded artifact from at least two different types (for example, a research brief and a configuration change). A reviewer who did not produce the artifact should be able to identify the exact version, reproduce the listed checks, trace material claims or behavior, explain every `fail`/`unknown`, and locate the recovery path.

Accept the trial when the record contains all universal checks, applicable artifact checks, a diff or baseline comparison, source validation, test observations, rollback details, and the required approval decision. Intentionally include one unsupported claim or failing test; the gate must refuse `accept` and preserve the baseline. Record the trial version, context, failures, corrections, and limitations. Do not infer improved accuracy, safety, speed, or cost without a separate measurement plan.

## Implementation

### Minimal review packet

Keep this information beside the artifact or in its approved system of record:

```text
gate record: unique-id
artifact: name and type
version: commit, file hash, or dated revision
intended effect: what acceptance permits
owner: accountable role
reviewer: approving human and authority
criteria: observable acceptance conditions
baseline/diff: location
sources: source, version/date, claim or setting supported
checks: status, evidence location, expected, observed
rollback: owner, steps, recovery window
decision: accept | revise | reject
approval: person, timestamp, exact version approved
release/monitoring: destination, timestamp, signal, stop trigger
```

### Machine-readable example

The following is a hypothetical record for a draft configuration review, not evidence that it was executed. Systems may extend the fields, but must preserve the meaning of `unknown` and the rule that mandatory failures block acceptance.

```json
{
  "gate_record": "example-2026-08-31-001",
  "artifact": {"name": "routing.yaml", "type": "configuration", "version": "sha256:example"},
  "impact": "material",
  "owner": "workflow-owner",
  "reviewer": {"name": "authorized-reviewer", "authority": "configuration-owner"},
  "criteria": ["schema-valid", "no-new-privilege", "safe-fallback"],
  "baseline_diff": "approved-system://change/example-001",
  "checks": [
    {"id": "scope", "status": "pass", "evidence": "review://example-001/scope"},
    {"id": "schema", "status": "pass", "evidence": "test://example-001/schema", "expected": "valid", "observed": "valid"},
    {"id": "unauthorized-input", "status": "fail", "evidence": "test://example-001/unauthorized", "expected": "reject", "observed": "accepted"},
    {"id": "source-freshness", "status": "unknown", "evidence": "approved-system://sources/example-001"}
  ],
  "rollback": {"baseline": "approved-system://baseline/example-001", "owner": "workflow-owner", "procedure": "disable change and restore baseline"},
  "decision": "revise",
  "approval": null
}
```

The example must remain `revise`: a failed security-boundary test and unknown source freshness cannot be converted into acceptance by adding a comment. After correction, rerun affected checks and issue a new exact version for approval.

## Failure modes

- **Completion theater:** A green status or polished prose is treated as proof. Consequence: unsupported or broken work ships. Prevention: require criterion-level evidence and a human diff review; reject claims without support.
- **Check substitution:** A lint, schema, or unit test is treated as an all-purpose correctness check. Consequence: source, permission, or domain failures remain hidden. Prevention: combine universal and artifact-specific checks and record their limits.
- **Unknown laundering:** Missing or stale evidence is silently inferred. Consequence: a reviewer accepts a claim that cannot be verified. Prevention: preserve `unknown`; block mandatory acceptance until resolved or explicitly escalated under policy.
- **Scope drift:** The agent changes files, systems, or permissions outside the request. Consequence: unintended side effects or data exposure. Prevention: baseline, complete diff, least privilege, and a stop trigger.
- **Late approval:** Review happens after publication or execution. Consequence: the gate cannot prevent harm. Prevention: put the approval step before the effect and use staging or a queue.
- **Unusable rollback:** A backup exists but no owner, steps, or recovery window are known. Consequence: a defect persists. Prevention: name the recovery owner, preserve the exact baseline, and test or rehearse recovery for material changes.
- **Evidence leakage:** Logs or packets contain secrets or unnecessary personal information. Consequence: the verification process creates a new exposure. Prevention: redact, minimize, and link to access-controlled records.

## Evidence

Initial maturity is **proposed** and evidence quality is **none**. This repository contains the method and a hypothetical machine-readable example only; it does not contain a completed trial, measured effectiveness, or independent reproduction. A future tested revision should preserve a safe-to-share gate record containing context, exact artifact version, criteria, source register, check results, diff review, approval, rollback, observed failures, and limitations. Redact private inputs and promote maturity only when the evidence meets the Practice schema.

## Variations

- A low-risk draft can use a reduced packet, but must still label its status and cannot be represented as accepted or shipped.
- A team may automate repeatable checks and packet generation. Automation reports evidence for its defined check; a human still reviews material scope and approval conditions.
- High-impact work may require multiple approvers, independent testing, or a formal change-management record. Add those controls; do not weaken this gate.

## Changelog

- **2026-08-31 — 0.2.0:** Made mandatory unknowns release-blocking, separated policy exceptions from a passing gate, and aligned the rollback requirement to a tested or clearly executable recovery path.
- **2026-08-31 — 0.1.0:** Proposed a cross-artifact verification gate with universal checks, artifact-specific checks, evidence and rollback requirements, mandatory approval rules, and a machine-readable example.
