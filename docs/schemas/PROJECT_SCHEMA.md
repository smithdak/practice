# Project Schema

## Outcome

This schema makes a Project a reviewable record of open-source software or infrastructure built by the community, with a stated problem, an accountable maintainer, and an explicit operating boundary. It keeps a demonstration from being mistaken for maintained software: a Project claims users, stewardship, and a license, and each claim must be true when the status says it is.

Use this schema with [the Project template](../../templates/PROJECT.md). A [Lab](LAB_SCHEMA.md) answers a bounded experimental question and ends when the runs end; a Project is maintained software people can inspect, use, and contribute to. See [Artifact types](../framework/TAXONOMY.md#artifact-types) in [the Knowledge Taxonomy](../framework/TAXONOMY.md) and [the contribution model](../../community/CONTRIBUTION_MODEL.md) for the proposal-to-maintained path this schema records.

## Canonical metadata

Every Project begins with YAML front matter. Field names and controlled values are case-sensitive.

| Field | Required | Rule |
|---|---|---|
| `artifact_type` | Yes | Must be `project`. |
| `name` | Yes | Non-empty project name as it should appear in listings. |
| `repo_url` | Yes | `https://` URL of the source repository, or a repository-relative path when the code lives inside this repository. |
| `status` | Yes | One of `proposed`, `active`, `paused`, or `retired`. |
| `maintainers-role` | Yes | Non-empty list naming each maintainer with their project role in `Name (role)` form, such as `Alex (lead)` or `infra-team (release)`. The role describes the stewardship responsibility, not community status. |
| `license` | Yes | `Apache-2.0`, the default code license. State a different code license explicitly when one applies. |
| `associated-capability` | Yes | One of `learn`, `use`, `automate`, `build`, or `transform`; the Project's direct outcome. This is the taxonomy's primary capability for the Project. |
| `created` | Yes | ISO date in `YYYY-MM-DD` form: the date the Project record was created. |
| `paused_on` | Conditional | ISO date required when `status` is `paused`. |
| `pause_reason` | Conditional | Non-empty plain-language reason required when `status` is `paused`; state what users and contributors should expect while paused. |
| `retired_on` | Conditional | ISO date required when `status` is `retired`. |
| `retired_reason` | Conditional | Non-empty plain-language reason required when `status` is `retired`. |
| `superseded_by` | No | Relative path or URL to a successor, only when one exists. |

A `proposed` Project may name a maintainer candidate in `maintainers-role`. An `active` Project's listed maintainer must have accepted stewardship in the `Ownership` section.

## Required content

All Projects must contain these headings, in this order:

1. `Problem` — the concrete Practitioner problem, the intended users, and the context; why an existing tool or artifact is not enough.
2. `Smallest useful release` — the narrowest usable first release and what is explicitly out of scope.
3. `Approach and boundaries` — inputs, outputs, interfaces, and dependencies; the boundary against scope growth.
4. `Evidence and success check` — the linked prototype, Lab, or observation that motivates the Project, and what evidence will show the release is useful. Label hypotheses as hypotheses.
5. `Ownership` — the named maintainer who accepted stewardship, their role, and how maintainer decisions are delegated. Governance, licensing, access, and exceptions remain human-owned.
6. `Access` — repository location and license, the setup or use path, and who may commit directly versus propose changes. No secrets, credentials, or confidential material are stored in the repository.
7. `Review` — how issues, changes, security or safety reports, and releases are handled, and what a maintainer checks before merging. Automated checks and agent-assisted triage may prepare a decision; a human maintainer makes it.
8. `Changelog` — dated record of status, maintainer, scope, and boundary changes.

Sections 1–4 correspond to the fields of [the Project intake form](../../.github/ISSUE_TEMPLATE/project.yml) (`problem`, `smallest_release`, `approach`, `evidence`); section 5 records the intake form's stewardship answers once a maintainer accepts. The template's heading names are canonical; do not substitute synonyms that make automated review ambiguous.

## Lifecycle states

| Status | Meaning | Minimum record | Permitted transition |
|---|---|---|---|
| `proposed` | The need, release boundary, and evidence are recorded; no maintainer has accepted stewardship yet. | Required sections with a proposed maintainer or an explicit request for one; `Evidence and success check` states what would make the release useful. | `active` when a named maintainer accepts in `Ownership`; otherwise redirect to a Lab or close with a recorded reason. |
| `active` | Maintained software with an accepted maintainer, a stated review and release process, and a usable access path. | All required sections; `Ownership` names the maintainer who accepted stewardship; `Access` and `Review` describe the operating process. | `paused` or `retired`. |
| `paused` | Temporarily without dependable stewardship; no new-release expectations. | `paused_on`, `pause_reason`; keep `Access` accurate about what still works. | `active` when stewardship is re-accepted, or `retired`. |
| `retired` | Terminal; the Project is no longer maintained and the record is retained for history. | `retired_on`, `retired_reason`; preserve prior content. | None. |

Status changes are maintainer decisions recorded in the `Changelog`. Activity counts, enthusiasm, or community discussion never establish `active` status; dependable, named stewardship does.

## Project or Lab boundary

- A Lab ends: it answers its stated question and records results, limitations, and reproduction material. A Project continues: it expects users, changes, and releases over time.
- A demonstration or prototype without intended users or an accepted maintainer belongs in a Lab until it has a credible Project case.
- A Lab may contain a prototype; the prototype becomes a Project only through the proposal path in the contribution model and a human maintainer's acceptance. An idea recorded before any release exists can start as a [Note](NOTE_SCHEMA.md) or a Lab.
- If the durable value is prose instruction or an evidence record, publish a Practice, Lab, or Story and link any code from it instead of creating a Project.

## Consistency rules a validator can enforce

1. Front matter parses as YAML and contains every required field with controlled values.
2. `status` uses the controlled values; `paused_on` and `pause_reason` are present exactly when `status` is `paused`, and `retired_on` and `retired_reason` exactly when `status` is `retired`.
3. `created` uses `YYYY-MM-DD`; `repo_url` is an `https://` URL or a repository-relative path that resolves.
4. `maintainers-role` is a non-empty list; an `active` Project's `Ownership` section names at least one maintainer.
5. `associated-capability` is exactly one controlled capability value.
6. Required headings exist in canonical order.
7. Relative links resolve within the repository.

Human review remains necessary to judge whether the maintainer genuinely accepted stewardship, the access and review processes are real, the release boundary holds, and no secrets or confidential material entered the repository.
