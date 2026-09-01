---
artifact_type: project
name: "Project name"
repo_url: "https://example.com/project-repository" # or a repository-relative path when the code lives here
status: proposed
maintainers-role: ["Maintainer name (lead)"]
license: Apache-2.0
associated-capability: build
created: YYYY-MM-DD
# paused_on: YYYY-MM-DD # Required when status is paused.
# pause_reason: "What users and contributors should expect while paused."
# retired_on: YYYY-MM-DD # Required when status is retired.
# retired_reason: "Why the Project is no longer maintained."
# superseded_by: "relative-path-or-URL" # Optional; use only when a successor exists.
---

# Project name

> **Template note:** This template follows [the Project schema](../docs/schemas/PROJECT_SCHEMA.md) and records a proposal from [the Project intake form](../.github/ISSUE_TEMPLATE/project.yml). Remove this note and instructional comments before publishing. A named maintainer must accept stewardship before the Project becomes `active`; see [the contribution model](../community/CONTRIBUTION_MODEL.md).

## Problem

Name the concrete Practitioner problem, the intended users, and the context. State why an existing tool or artifact is not enough.

## Smallest useful release

Describe the narrowest usable first release. List what is explicitly out of scope.

## Approach and boundaries

Describe inputs, outputs, interfaces, and dependencies. State the boundary that keeps the Project from growing past its stated problem.

## Evidence and success check

Link the prototype, Lab, reproduction, or observation that motivates the Project, and state what evidence will show the release is useful. Label hypotheses as hypotheses.

## Ownership

Name the maintainer who has accepted—or, for `status: proposed`, is asked to accept—ongoing stewardship, their role, and how maintainer decisions are delegated. Governance, licensing, access, and exceptions remain human-owned decisions.

## Access

State the repository location and license, the setup or use path, and who may commit directly versus propose changes. Do not include secrets, credentials, or confidential material; state how security concerns are reported instead of where credentials live.

## Review

Describe how issues, changes, and security or safety reports are handled and what a maintainer checks before merging. State the release process. Automated checks and agent-assisted triage may prepare a decision; a human maintainer makes it.

## Changelog

Record dated changes to status, maintainers, scope, or boundary. The first entry records the proposal date and the initial status.
