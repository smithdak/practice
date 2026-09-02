---
name: review-practice-artifact
description: Review a Practice community artifact or repository change for usefulness, evidence, reproducibility, safety, model neutrality, taxonomy fit, and repository quality. Use for an acceptance-oriented Practice review; do not use for generic proofreading or silently editing the artifact.
---

# Review a Practice artifact

## Source of truth

Read [docs/QUALITY_BAR.md](../../../docs/QUALITY_BAR.md), [docs/DECISIONS.md](../../../docs/DECISIONS.md), [docs/NON_GOALS.md](../../../docs/NON_GOALS.md), and the [artifact taxonomy](../../../docs/framework/TAXONOMY.md) before reviewing. Read the applicable repository template for a [Practice](../../../templates/PRACTICE.md), [Guide](../../../templates/GUIDE.md), [Lab](../../../templates/LAB.md), or [Story](../../../templates/STORY.md). For code or infrastructure, apply the Project definition in the taxonomy and the project's local checks.

Report findings only unless the user explicitly requests fixes. An agent recommends; a human maintainer makes acceptance, merge, governance, access, licensing, and moderation decisions.

## Inputs

Identify the exact artifact or diff, artifact type, intended Practitioner and outcome, maturity and evidence claims, applicable task or review criteria, and evidence locations. If the type is ambiguous, choose it from the reader's primary action and explain the classification before applying a template.

## Review method

1. Check scope and taxonomy fit. Flag mixed artifact types, launch-scope expansion, conflicts with locked decisions, and changes outside owned paths.
2. Test usefulness: a Practitioner should have a concrete next action, decision rule, or reproducible path rather than motivation or an unprioritized list.
3. Test reproducibility for the artifact type. Practices need inputs, method, outputs, evaluation, failure modes, and variations; Labs need inspectable conditions and results; Stories need real evidence and explicit evidence quality; Projects need setup, operating, evaluation, licensing, contribution, and maintenance boundaries.
4. Trace factual, technical, outcome, and maturity claims. Require appropriate evidence; require a primary-source URL and as-of date for current technical claims. Flag invented, generalized, stale, or unlabeled hypothetical material.
5. Check safety and publication readiness: secrets, private or confidential data, permissions, licensing, privacy, human-owned decisions, rollback where relevant, and prohibited silent moderation or external effects.
6. Check model neutrality, mixed-skill accessibility, clarity, internal links, and duplication. Tool-specific examples may remain examples but must not become universal requirements without evidence.
7. Run permitted deterministic checks and inspect their limits. A validator pass does not erase a substantive evidence, safety, or usability failure.
8. Reconcile each acceptance criterion with evidence and produce a recommendation: `ready for human decision`, `revision needed`, or `cannot assess with available evidence`.

## Deliverable

Lead with actionable findings ordered by consequence. For each finding, name the file and location, affected criterion, concrete evidence, consequence, and smallest correction. Separate blocking findings, non-blocking improvements, and questions. Then list checks performed, areas not verified, taxonomy decision, and the recommendation. If no findings remain, say so and still state residual risks or unverified areas.

## Stop and failure handling

Do not manufacture missing evidence, accept a Story whose outcome cannot be supported, expose restricted material in the review, or silently change or remove content. When a required source, test environment, authority, or artifact version is unavailable, identify exactly what cannot be assessed and route the decision to the appropriate human maintainer.
