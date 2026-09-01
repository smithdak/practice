# Note Schema

## Outcome

This schema makes a Note a bounded, dated record of one observation, question, decision, or early piece of evidence that is useful now but is not yet a reusable method or complete study. It lets a Practitioner preserve a small insight honestly—without dressing an anecdote up as a measurement—while leaving a visible path to promote the content into a Practice, Lab, or Story.

Use this schema with [the Note template](../../templates/NOTE.md). A Note preserves a claim or open question; a [Practice](PRACTICE_SCHEMA.md) teaches a repeatable method, and a [Lab](LAB_SCHEMA.md) records a test. See [Note vs. Practice](../framework/TAXONOMY.md#note-vs-practice) in [the Knowledge Taxonomy](../framework/TAXONOMY.md) before choosing this type.

## Canonical metadata

Every Note begins with YAML front matter. Field names and controlled values are case-sensitive.

| Field | Required | Rule |
|---|---|---|
| `artifact_type` | Yes | Must be `note`. |
| `title` | Yes | Non-empty human-readable title. |
| `summary` | Yes | Non-empty, plain-language statement of the bounded claim or question; not a result claim. |
| `maturity` | Yes | One of `observation`, `validated`, `promoted`, or `withdrawn`. |
| `date` | Yes | ISO date in `YYYY-MM-DD` form: the date the observation was made or recorded. |
| `author-role` | Yes | Exactly one controlled role value below; it names the work context in which the observation was made, not the author's seniority or credentials. |
| `license` | Yes | `CC-BY-4.0`, the default content license. |
| `tags` | Yes | Non-empty list of descriptive discovery labels; tags do not replace capability or role classification. |
| `source_links` | No | Safe-to-share source URLs or relative paths that support the observation. Record an as-of date beside sources that can change. |
| `promoted_to` | Conditional | Relative path to the Practice, Lab, or Story that now carries the content; required when `maturity` is `promoted`. |
| `withdrawn_on` | Conditional | ISO date in `YYYY-MM-DD` form; required when `maturity` is `withdrawn`. |
| `withdrawn_reason` | Conditional | Non-empty plain-language reason; required when `maturity` is `withdrawn`. |
| `superseded_by` | No | Relative path or URL to a replacement, only when one exists. |

The controlled role vocabulary is: `individual-practitioner`, `engineer`, `architect`, `builder`, `operator`, `founder`, `services-leader`, `internal-ai-champion`, `transformation-lead`, `consultant`, `agency-implementer`, and `executive`.

One Note records one bounded claim or question. Split unrelated observations into separate Notes instead of collecting them in one file.

## Required content

All Notes must contain these headings, in this order:

1. `Observation` — the bounded claim, question, or decision, stated once in plain language.
2. `Context` — where and when it was observed, the work situation, and what made recording it worthwhile. Use role context instead of employer or client names.
3. `Evidence and uncertainty` — what supports the observation, what is interpretation or hypothesis, and what is unknown. Write `Not measured` when nothing was measured.
4. `Implications and next step` — what a reader should do differently, check, or test next.

`Promotion record` is additionally required for a `promoted` Note, and `Withdrawal notice` for a `withdrawn` Note. `Changelog` is required once a Note leaves the initial `observation` state. The template's heading names are canonical; do not substitute synonyms that make automated review ambiguous.

## Maturity states and transitions

`observation → validated → promoted` is the normal progression. `withdrawn` is a terminal publication state that may be reached from `observation` or `validated`. A `promoted` Note is retained for history, not deleted; its content now lives in the artifact named by `promoted_to`.

| Maturity | Meaning | Minimum record | Permitted transition |
|---|---|---|---|
| `observation` | A bounded observation, question, or decision preserved with its context; no reliability is claimed. | All required headings; evidence labeled as fact, interpretation, or hypothesis. | Validate, promote, or withdraw. |
| `validated` | The observation has been checked again or supported by at least one linkable record, in a stated context. | Required headings, `Changelog`, and a link to the supporting record in `Evidence and uncertainty`; the context of the check is stated. | Promote or withdraw. |
| `promoted` | The content now lives in a Practice, Lab, or Story; the Note remains as provenance. | `promoted_to` and a `Promotion record` naming the artifact and date. | None. Update the target artifact, not the Note. |
| `withdrawn` | The observation was found wrong, misleading, or no longer worth acting on. | `withdrawn_on`, `withdrawn_reason`, and a `Withdrawal notice`; preserve the prior record. | None. |

## Evidence honesty rules

An observation is not a measurement.

1. State what was actually seen in the stated context. Do not attach counts, percentages, timing figures, or cost figures that no record supports.
2. Distinguish observed facts, interpretation, and untested hypotheses in `Evidence and uncertainty`. Personal experience is welcome when labeled as such.
3. One observation in one context is not a pattern. Do not write "always", "never", or "Practitioners find" from a single sighting.
4. If nothing was measured, write `Not measured` rather than estimating.
5. A Note observation cannot serve as the trial record that makes a Practice `tested`; at most it motivates a proposal. Trials are recorded under the [Lab Schema](LAB_SCHEMA.md).
6. Redact secrets, personal data, and confidential details before recording. If an observation cannot be shared without them, do not record it as a Note.

## From Note to Practice

Promote a Note when the method and its evaluation are concrete enough for another Practitioner to try—not when the observation merely attracts attention.

1. Draft a Practice from the Note using [the Practice template](../../templates/PRACTICE.md) with `maturity: proposed` and `evidence_quality: none`. The Note's anecdote may motivate the proposal; it is not evidence for it.
2. Record a bounded trial of the proposed method as a Lab.
3. Promotion of the new Practice then follows [the Practice maturity path](PRACTICE_SCHEMA.md), including human review.
4. Set the Note's `maturity` to `promoted`, add `promoted_to` and a `Promotion record`, and leave the Note published.

If the Note's next step is a question rather than a method, promote it to a [Lab](LAB_SCHEMA.md) instead. If a real implementation account exists, use a [Story](STORY_SCHEMA.md). Never rewrite the Note into the target artifact; link them.

## What disqualifies a Note

- You can already state reliable steps and evaluation criteria; that is a Practice.
- The main job is answering a testable question under stated conditions; that is a Lab.
- The main job is documenting a real implementation from before through result; that is a Story.
- The durable contribution is code or infrastructure with intended users and a maintainer; that is a [Project](PROJECT_SCHEMA.md).
- There is no bounded claim or question. Opinions, open-ended discussion, and model-release chatter belong in community discussion, not in this artifact type.
- The content is a collection of links, prompts, or tools; Practice does not maintain a prompt library.
- The observation is meaningful only with confidential material; do not record it.
- The same claim is already recorded in an existing artifact; open a correction instead.

## Consistency rules a validator can enforce

1. Front matter parses as YAML and contains every required field with controlled values.
2. `date` and `withdrawn_on` use `YYYY-MM-DD`; conditional fields are present exactly when required.
3. `author-role` is exactly one value from the controlled role vocabulary.
4. Required headings exist in canonical order; `Promotion record` appears exactly when `maturity` is `promoted`, `Withdrawal notice` exactly when `maturity` is `withdrawn`, and `Changelog` appears for `validated`, `promoted`, and `withdrawn`.
5. `promoted_to` resolves within the repository and its target declares `artifact_type: practice`, `lab`, or `story`.
6. Relative links resolve within the repository.

Human review remains necessary to judge whether the observation is genuinely bounded, the evidence layers are labeled honestly, the context is safe to publish, and promotion is warranted by the method's concreteness rather than enthusiasm.

## Worked classification example

The following is a hypothetical contribution. A Practitioner notices that a verification checklist caught a fabricated file path in one code review, records the sighting, the context, and what is still unknown, and labels the event as a single observation. No counts, timings, or reliability claims are made.

It is classified as a **Note**, not a Practice, because it preserves an observation and uncertainty without yet teaching a repeatable method. It stays `observation` until the check is applied again or a trial is recorded.

```yaml
artifact_type: note
title: "Verification checklist caught a fabricated file path"
summary: "A bounded observation that a stated verification check caught a fabricated path in one review."
maturity: observation
date: 2026-09-01
author-role: engineer
license: CC-BY-4.0
tags: [verification, review]
```

Its `Evidence and uncertainty` section labels the sighting as one observed fact, separates the interpretation ("the check may catch fabrication early") from the fact, and writes `Not measured` for any rate or reliability. If the Practitioner later specifies the check as repeatable steps with evaluation criteria, that becomes a Practice proposal with `evidence_quality: none`, and this Note is then marked `promoted` with `promoted_to` pointing at it.
