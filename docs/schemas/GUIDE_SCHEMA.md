# Guide Schema

## Outcome

This schema makes a Guide an opinionated, reviewable path to a clear completion outcome. A Guide sequences existing Practices and other learning work; it does not become a second copy of each Practice. Use it with the [Guide template](../../templates/GUIDE.md).

## Canonical metadata

Every Guide begins with YAML front matter. Field names and controlled values are case-sensitive.

| Field | Required | Rule |
|---|---|---|
| `artifact_type` | Yes | Must be `guide`. |
| `title` | Yes | Non-empty human-readable title. |
| `summary` | Yes | Plain-language statement of the audience, path, and concrete completion outcome; not an unsupported impact claim. |
| `status` | Yes | One of `draft`, `published`, or `deprecated`. |
| `capability` | Yes | One primary value: `learn`, `use`, `automate`, `build`, or `transform`. It is the Guide's direct completion outcome. |
| `audience` | Yes | Non-empty list of role values from the controlled vocabulary below. |
| `version` | Yes | Semantic version in `MAJOR.MINOR.PATCH` form, such as `0.1.0`. |
| `license` | Yes | `CC-BY-4.0`, the default content license. |
| `created` | Yes | ISO date in `YYYY-MM-DD` form. |
| `updated` | Yes | ISO date in `YYYY-MM-DD` form; it must not precede `created`. |
| `secondary_capabilities` | No | List of additional capability values directly supported by the path; do not repeat `capability`. |
| `maintainers` | No | People or teams responsible for updates. |
| `source_links` | No | Safe-to-share source URLs or relative paths. |
| `last_verified` | Conditional | ISO date required when `status` is `published`; it records the most recent path and Practice-reference review. |
| `deprecated_on` | Conditional | ISO date required when `status` is `deprecated`. |
| `deprecation_reason` | Conditional | Non-empty reason required when `status` is `deprecated`. |
| `superseded_by` | No | Relative path or URL to a replacement, only when one exists. |

The controlled audience vocabulary is: `individual-practitioner`, `engineer`, `architect`, `builder`, `operator`, `founder`, `services-leader`, `internal-ai-champion`, `transformation-lead`, `consultant`, `agency-implementer`, and `executive`. Audience describes who the path serves, not a credential or access level.

## Required content

All Guides must contain these headings, in this order:

1. `Intended Practitioner` — audience, role context, and starting point.
2. `Outcomes` — observable completion outcome and criteria.
3. `Prerequisites` — required knowledge, access, inputs, and prerequisite Practices.
4. `Path` — sequence and rationale for the modules.
5. `Modules` — one or more modules, each with purpose, linked Practices, and a completion check.
6. `Capstone` — bounded integrative work with inputs, outputs, review points, and completion conditions.
7. `Evaluation` — checks, acceptance criteria, reviewer, and limitations.
8. `Maintainers` — update responsibility.
9. `Changelog` — dated version history.

`Deprecation notice` is additionally required for a deprecated Guide. The template's heading names are canonical; do not substitute synonyms that make automated review ambiguous.

## Practices and module boundaries

A collection becomes a Guide when it has all of the following:

- a named audience and starting point;
- a deliberate sequence with a reason for the order;
- multiple related Practices or other learning units that together serve one outcome;
- prerequisites and a bounded capstone that integrates the path; and
- an evaluation method with explicit completion criteria.

A list of links, a topical index, or a set of Practices without sequencing, integration, and evaluation remains a collection. A Guide may include short orientation or synthesis text, but link to the canonical Practice for instructions, inputs, failure modes, and evidence. Repeat a Practice only when a local adaptation is necessary; state the adaptation and its boundary, and keep the canonical reference.

Each module must name the Practices a Practitioner applies and the output or decision produced. A module may contain one or more Practices, but it must have a completion check. The capstone must use outputs from the path and must not be presented as a measured case study unless supporting evidence is published.

## Status and versioning

`draft` is a reviewable path that may still change. `published` is a maintained path whose links, sequence, and evaluation have been reviewed on `last_verified`. `deprecated` remains available for history but is not recommended for new starts.

Use semantic versioning as follows:

- **PATCH**: wording, formatting, or link corrections that do not change the path, Practices, outcome, evaluation, or scope.
- **MINOR**: backward-compatible additions such as an optional module, Practice reference, variation, or clarification that leaves the completion outcome and existing path usable.
- **MAJOR**: changes to the audience, prerequisites, order or required content, Practice versions or boundaries, capstone, evaluation criteria, or completion outcome that require a Practitioner to relearn or redo the path.

Update `updated` and the `Changelog` for every version change. A material change to a linked Practice is not silently absorbed: review the Guide, update its reference or instructions, and record the decision. A published Guide with a material change should return to `draft` until its path and evaluation are reviewed; update `last_verified` when it is published again.

## Update and deprecation rules

Maintainers should review a published Guide when a referenced Practice changes materially, a link breaks, a prerequisite changes, the capstone no longer exercises the stated outcome, or evaluation criteria become unsuitable. Record the review even when no change is needed.

Deprecate a Guide when it is unsafe, inaccurate, obsolete, unsupported by its referenced Practices, or replaced by a materially better path. Set `status: deprecated`, add `deprecated_on`, `deprecation_reason`, and a `Deprecation notice`, preserve the prior changelog and evaluation record, and link `superseded_by` only when a replacement exists. Do not delete the historical Guide or imply that deprecation is evidence that the path was effective.

## Consistency rules a validator can enforce

1. Front matter parses as YAML; required fields and controlled values are present.
2. Dates use `YYYY-MM-DD`, `updated` is not before `created`, and conditional dates/reason are present for `published` or `deprecated` as specified.
3. `version` matches `MAJOR.MINOR.PATCH`; primary and secondary capabilities do not overlap.
4. Required headings exist in canonical order; deprecated Guides contain `Deprecation notice`.
5. `Modules` contains at least one module with a Practice reference and completion check, and `Capstone` and `Evaluation` are non-empty.
6. Relative links resolve within the repository and Practice links point to canonical Practice artifacts.

Human review remains necessary to judge whether the sequence is genuinely opinionated, the Practices are appropriate and sufficiently distinct, the capstone demonstrates the stated outcome, and evidence or examples are honestly bounded.
