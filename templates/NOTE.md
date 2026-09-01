---
artifact_type: note
title: "Note title"
summary: "The bounded claim or question this Note preserves."
maturity: observation
date: YYYY-MM-DD
author-role: individual-practitioner
license: CC-BY-4.0
tags: [example-tag]
# source_links: []
# promoted_to: "relative-path-to-practice-lab-or-story" # Required when maturity is promoted.
# withdrawn_on: YYYY-MM-DD # Required when maturity is withdrawn.
# withdrawn_reason: "Why this observation should no longer be relied on."
# superseded_by: "relative-path-or-URL" # Optional; use only when a replacement exists.
---

# Note title

> **Template note:** This template follows [the Note schema](../docs/schemas/NOTE_SCHEMA.md). Remove this note and instructional comments before publishing. One Note records one bounded claim or question; see [the Knowledge Taxonomy](../docs/framework/TAXONOMY.md#note-vs-practice) if a Practice, Lab, or Story fits better.

## Observation

State the bounded claim, question, or decision in one place, in plain language. Do not attach a result claim to it.

## Context

Describe where and when the observation was made, the work situation, and what made recording it worthwhile. Use role context instead of employer, client, or project names.

## Evidence and uncertainty

Separate observed facts, interpretation, and untested hypotheses, and state what remains unknown. Write `Not measured` when nothing was measured. Do not attach counts, percentages, or timing figures that no record supports. Link safe-to-share sources and record an as-of date beside sources that can change.

## Implications and next step

State what a reader should do differently, what to check, or what to test next. Link the Practice, Lab, or Story when one exists.

## Promotion record

Required only when `maturity: promoted`. Name the artifact that now carries the content, its relative path, and the promotion date. Leave the rest of the Note unchanged as provenance.

## Withdrawal notice

Required only when `maturity: withdrawn`. State the withdrawal date, the reason, and any safety or accuracy concern. State a replacement in `superseded_by` only when one exists.

## Changelog

Record dated, meaningful changes to the observation, evidence, scope, or maturity. Required once the Note leaves the initial `observation` state.
