# Practice Schema

## Outcome

This schema makes a Practice a reusable method with a stated boundary, evaluation, and evidence level. It lets an author publish a useful proposal without presenting it as tested, while requiring more evidence and operational detail before the Practice is called mature.

Use this schema with [the Practice template](../../templates/PRACTICE.md). A Practice is an instruction for doing work; a [Lab](../framework/TAXONOMY.md#practice-vs-lab) is the record for answering an experimental question. Link them when a Lab supports a Practice instead of turning limited test results into a universal rule.

## Canonical metadata

Every Practice begins with YAML front matter. Field names and controlled values are case-sensitive.

| Field | Required | Rule |
|---|---|---|
| `artifact_type` | Yes | Must be `practice`. |
| `title` | Yes | Non-empty human-readable title. |
| `summary` | Yes | Non-empty, plain-language statement of the method's concrete outcome; not an unsupported result claim. |
| `maturity` | Yes | One of `proposed`, `tested`, `verified`, or `deprecated`. |
| `capability` | Yes | One of `learn`, `use`, `automate`, `build`, or `transform`. Select the method's direct outcome. |
| `roles` | Yes | Non-empty list of controlled role values below. |
| `version` | Yes | Semantic version in `MAJOR.MINOR.PATCH` form, such as `0.1.0`. |
| `license` | Yes | `CC-BY-4.0`, the default content license. |
| `created` | Yes | ISO date in `YYYY-MM-DD` form. |
| `updated` | Yes | ISO date in `YYYY-MM-DD` form; it must not precede `created`. |
| `evidence_quality` | Yes | One of the evidence-quality values below; it must meet the maturity rule. |
| `secondary_capabilities` | No | List of additional controlled capability values directly supported by the method. Do not repeat `capability`. |
| `secondary_roles` | No | List of additional controlled role values directly served by the method. Do not repeat `roles`. |
| `authors` | No | List of names, handles, or organization names that may be published. |
| `maintainers` | No | List of the people or teams responsible for updates. |
| `source_links` | No | List of relevant safe-to-share source URLs or relative paths. |
| `tags` | No | List of descriptive discovery labels; tags do not replace capability or role classification. |
| `last_verified` | Conditional | ISO date required when `maturity` is `verified`; optional otherwise. It records the most recent evidence review, not a promise of permanent validity. |
| `deprecated_on` | Conditional | ISO date required when `maturity` is `deprecated`. |
| `deprecation_reason` | Conditional | Non-empty plain-language reason required when `maturity` is `deprecated`. |
| `superseded_by` | No | Relative path or URL to a replacement, only when one exists. A replacement is never required to deprecate an unsafe or inaccurate method. |

The controlled role vocabulary is: `individual-practitioner`, `engineer`, `architect`, `builder`, `operator`, `founder`, `services-leader`, `internal-ai-champion`, `transformation-lead`, `consultant`, `agency-implementer`, and `executive`.

Metadata describes the artifact, not the author's seniority or identity. Do not use role or capability fields as credentials, permissions, or claims of expertise.

## Required content by maturity

All Practices must have these template sections:

- `Outcome`
- `Problem and scope`
- `Use when`
- `Inputs`
- `Method`
- `Evaluation`
- `Changelog`

`Method` must be ordered steps and name the expected output. `Evaluation` must name the criteria and the check used to judge that output. A proposed Practice supplies an evaluation plan; a mature Practice supplies the actual evaluation record.

| Section or record | Proposed | Tested | Verified | Deprecated |
|---|---|---|---|---|
| Defined outcome, scope, inputs, and ordered method | Required | Required | Required | Preserve existing record |
| Evaluation | Required as a planned trial with criteria | Required with checks, criteria, and observed result | Required with checks, criteria, and evidence of independent reproduction | Preserve prior evaluation; state why it is no longer recommended |
| Implementation | Optional | Required | Required | Preserve existing record |
| Failure modes | Optional; label anticipated items as hypotheses | Required; record observed or deliberately tested failures, consequence, and response | Required; include failures or limits found across the supporting evidence | Preserve existing record and add relevant deprecation risk |
| Evidence section | Optional | Required | Required | Preserve existing record |
| Deprecation notice | Not used | Not used | Not used | Required |

This is deliberate author burden: a proposal needs enough detail for a bounded trial, not a retrospective report. Once a method is called tested or verified, a reader must be able to inspect how it was evaluated and how it can fail.

## Maturity states and transitions

`proposed → tested → verified` is the normal progression. `deprecated` is a terminal publication state that may be reached from any prior state. Deprecation retains the artifact and its evidence; it does not erase the historical record.

A deprecated Practice retains the evidence-quality value it had when it was retired. Therefore `none` is valid for a deprecated proposal, while a deprecated verified Practice retains `independently-reproduced`; deprecation never upgrades evidence.

| Maturity | Meaning | Minimum evidence and content | Permitted transition |
|---|---|---|---|
| `proposed` | A bounded method ready for a first trial; no effectiveness is claimed. | `evidence_quality: none`; required core sections; evaluation plan. | Promote to `tested` after a documented application. Deprecate if it should not be tried. |
| `tested` | The stated method has been applied and evaluated in at least one documented context. | `evidence_quality: single-run` or `repeated`; implementation, evaluation result, failure modes, and evidence section. | Promote to `verified` after independent reproduction. Revise scope or deprecate when the evidence contradicts the method. |
| `verified` | The method and its stated limits have supporting evidence from independent reproduction. This does not mean it works in every context. | `evidence_quality: independently-reproduced`; all tested requirements; `last_verified`; evidence identifies the independent reproduction and remaining limits. | Deprecate when it becomes unsafe, inaccurate, obsolete, or superseded. Material method changes require a new evaluation and may warrant returning to `tested`. |
| `deprecated` | The method is retained for history but is no longer recommended for new use. | `deprecated_on`, `deprecation_reason`, and a `Deprecation notice`; preserve prior content and evidence. | No promotion. Publish a new or revised Practice rather than removing the notice. |

Changing the method's inputs, ordered steps, evaluation criteria, or stated outcome is a material change. Increment `version`, update `updated` and `Changelog`, and reassess maturity. Correcting wording or links without changing the method does not by itself lower maturity.

## Evidence-quality levels

Evidence quality describes the strength of the evidence record, not the value of the author or the general importance of the method.

| Value | Meaning | Minimum record |
|---|---|---|
| `none` | No execution evidence is available. | A proposed method and evaluation plan only. |
| `single-run` | One documented application of the stated method. | Context, method version, inputs described safely, evaluation criteria, outcome, and limitation. |
| `repeated` | At least two documented applications of the same stated method. | The `single-run` record for each application, plus what remained consistent and what varied. |
| `independently-reproduced` | At least one documented reproduction in addition to the originating application, performed by a different Practitioner using the frozen method in a separately documented context. | The supporting records, the independence boundary, evaluation results, and limitations. |

Do not infer a higher evidence level from enthusiasm, number of readers, a tool demonstration, or an uninspected testimonial. Evidence records may be redacted or summarized to protect confidential inputs, but they must still state enough context and limitation for a reader to judge the claim.

## Consistency rules a validator can enforce

A validator can check the following mechanically:

1. Front matter parses as YAML and contains every required field.
2. Enum fields use only the controlled values in this schema.
3. Dates use `YYYY-MM-DD`, `updated` is not before `created`, and conditional dates are present when required.
4. `version` matches `MAJOR.MINOR.PATCH`.
5. `proposed` uses `none`; `tested` uses `single-run` or `repeated`; `verified` uses `independently-reproduced` and has `last_verified`; `deprecated` has `deprecated_on` and `deprecation_reason`.
6. Required headings exist for the selected maturity; mature Practices contain `Implementation`, `Failure modes`, and `Evidence`, and deprecated Practices contain `Deprecation notice`.
7. Primary and secondary capability or role lists contain no duplicate values.

Human review remains necessary to determine whether a method is genuinely repeatable, a run is independent, evidence supports the stated claim, failure modes are meaningful, and confidential information has been excluded.

## Worked classification example

The following is a hypothetical contribution. A Practitioner writes instructions for assembling an approved-document context pack before drafting a recurring internal brief. They apply the exact steps once, compare the draft against the approved documents with a stated checklist, and record that the checklist found omissions. The record contains no measured claim about time, quality, or business impact.

It is classified as a **Practice**, not a Lab, because its primary reader action is to apply the reusable context-pack method. Its direct outcome is completing a discrete work task with a check, so it uses `capability: use`. The intended work contexts are `individual-practitioner` and `operator`. It is `tested`, rather than `verified`, because there is one documented application and no independent reproduction.

```yaml
artifact_type: practice
title: "Assemble an approved-document context pack"
summary: "Prepare approved source material for a checked recurring draft."
maturity: tested
capability: use
roles: [individual-practitioner, operator]
version: 0.1.0
license: CC-BY-4.0
created: 2026-08-31
updated: 2026-08-31
evidence_quality: single-run
```

Its `Evaluation` section names the checklist and the acceptance criteria; its `Failure modes` section explains how missing or stale source material is detected and escalated; and its `Evidence` section preserves the safe-to-share run record and limitation. A second Practitioner could later reproduce the unchanged method in a documented separate context. Only then, with evidence quality `independently-reproduced`, could the author consider promotion to `verified`.
