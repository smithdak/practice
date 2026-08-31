# Story Schema

This schema defines an evidence-grounded implementation Story: a record of a real change that helps another Practitioner judge what happened, what can be reused, and what remains unknown. A Story is not a testimonial or a promise that the same result will occur elsewhere.

Use this schema with the [Story template](../../templates/STORY.md). The sample in [`stories/SAMPLE_HYPOTHETICAL.md`](../../stories/SAMPLE_HYPOTHETICAL.md) is format documentation only and is not evidence.

## Canonical metadata

Every Story begins with YAML front matter. Field names and controlled values are case-sensitive.

| Field | Required | Rule |
|---|---|---|
| `artifact_type` | Yes | Must be `story`. |
| `title` | Yes | Non-empty human-readable title. |
| `status` | Yes | One of `draft`, `review`, `published`, or `withdrawn`. |
| `organization` | Yes | One of `public`, `anonymized`, or `withheld`; accurately describes disclosure. |
| `evidence_quality` | Yes | One of the levels below; match the available record. |
| `version` | Yes | Semantic version in `MAJOR.MINOR.PATCH` form. |
| `license` | Yes | `CC-BY-4.0`, the default content license. |
| `created` | Yes | ISO date in `YYYY-MM-DD` form. |
| `updated` | Yes | ISO date in `YYYY-MM-DD` form; it must not precede `created`. |
| `authors` | No | Publishable names, handles, or organization names only. |
| `source_links` | No | Safe-to-share source URLs or relative paths; never private credentials or confidential locations. |
| `tags` | No | Descriptive discovery labels. |

## Required sections

All Stories must contain these headings:

- `Summary`
- `Before`
- `Constraint`
- `Intervention`
- `Implementation`
- `After`
- `Result`
- `Lessons`
- `Artifacts`
- `Evidence record`
- `Anonymization and consent`
- `Changelog`

The record must distinguish observed facts, contributor interpretation, and untested hypotheses. `Before`, `After`, and `Result` must not be empty. If an outcome was not measured, say `Not measured` rather than estimating it.

## Evidence-quality levels

Evidence quality describes the inspectability of this Story, not the author's credibility or the size of an outcome.

| Value | Meaning | Minimum record |
|---|---|---|
| `none` | Proposed or illustrative account with no execution evidence. | Context and intended intervention; explicitly state results are unavailable. Use for drafts or hypothetical examples only. |
| `single-run` | One documented application in one bounded context. | Safe-to-share Before, method/version, After, evaluation criteria, Result, limitations, and evidence record. |
| `repeated` | At least two documented applications of the same intervention. | The single-run record for each application, plus what remained consistent and what varied. |
| `independently-reproduced` | A separate Practitioner reproduced the frozen intervention in a separate context. | Originating and reproduction records, independence boundary, evaluation results, and remaining limits. |

Do not upgrade evidence based on testimonials, readership, a tool demo, or an uninspected claim. Redacted or summarized records are acceptable only when they retain enough context, method, criteria, and limitation for judgment.

## Anonymization rules

1. Obtain explicit permission from the contributor and any organization or person whose non-public details are included. If permission is absent or unclear, withhold the detail.
2. Prefer a role and broad context (for example, “support operations team”) over a person's name or exact employer.
3. Remove secrets, personal data, client names, internal URLs, identifiers, exact locations, and proprietary source text. Treat combinations of dates, volumes, tools, and roles as potentially identifying.
4. Generalize dates, counts, and technical details only when needed for privacy, and label them approximate or omitted. Never alter evidence to make a result look better.
5. Keep organization status honest: `public` means named with permission; `anonymized` means details were deliberately generalized; `withheld` means it cannot be identified from the published record.
6. Record what was redacted and the resulting limitation in `Evidence record` and `Anonymization and consent`.

Anonymization protects people and organizations; it does not make unsupported claims publishable.

## Status and evidence guidance

`draft` and `review` may use `none` while evidence is assembled. A `published` Story documents a real implementation and must use at least `single-run` (`single-run`, `repeated`, or `independently-reproduced`); `published` with `none` is invalid. Hypothetical or illustrative samples must remain `draft` with `evidence_quality: none`, and must be clearly labeled as non-evidence. `withdrawn` Stories retain their record and explain why they are no longer recommended.

## Review checklist

- Before, intervention, After, Result, Lessons, and Artifacts are present.
- Every result has a source record, evaluation criterion, and limitation, or is marked `Not measured`.
- The evidence level is no stronger than the records support.
- Consent, redactions, organization status, and safe-to-share links are documented.
- No secrets, personal information, confidential details, invented customer, or invented metric appears.
