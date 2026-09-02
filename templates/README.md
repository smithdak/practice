# Templates

Where each artifact starts, which schema checks it, where the finished file goes, and which issue form opens the work. Copy the template, replace every fill-in value, and check the result against its schema before opening a pull request.

## Published artifacts

| Artifact | Template | Schema | Finished file goes to | Issue form that starts it |
|---|---|---|---|---|
| Practice | [PRACTICE.md](PRACTICE.md) | [PRACTICE_SCHEMA.md](../docs/schemas/PRACTICE_SCHEMA.md) | [../practices/](../practices/README.md) | [practice.yml](../.github/ISSUE_TEMPLATE/practice.yml) |
| Guide | [GUIDE.md](GUIDE.md) | [GUIDE_SCHEMA.md](../docs/schemas/GUIDE_SCHEMA.md) | [../guides/](../guides/README.md), one directory per Guide: the Guide is its `README.md`, with `NN-slug.md` modules beside it | None exists. [../CONTRIBUTING.md](../CONTRIBUTING.md) lists Guides on the "Guide, Lab, or Story" path, which links only the Lab and Story forms. |
| Lab | [LAB.md](LAB.md) | [LAB_SCHEMA.md](../docs/schemas/LAB_SCHEMA.md) | [../labs/](../labs/README.md) | [lab.yml](../.github/ISSUE_TEMPLATE/lab.yml) |
| Story | [STORY.md](STORY.md), after [INTAKE_CONSENT.md](INTAKE_CONSENT.md) and [REDACTION_CHECKLIST.md](REDACTION_CHECKLIST.md) | [STORY_SCHEMA.md](../docs/schemas/STORY_SCHEMA.md) | [../stories/](../stories/README.md) | [story.yml](../.github/ISSUE_TEMPLATE/story.yml) |
| Note | [NOTE.md](NOTE.md) | [NOTE_SCHEMA.md](../docs/schemas/NOTE_SCHEMA.md) | [../notes/](../notes/README.md) | [note.yml](../.github/ISSUE_TEMPLATE/note.yml) |
| Project | [PROJECT.md](PROJECT.md) | [PROJECT_SCHEMA.md](../docs/schemas/PROJECT_SCHEMA.md) | [../projects/](../projects/README.md) | [project.yml](../.github/ISSUE_TEMPLATE/project.yml) |

Story companions: the contributor and a human intake contact complete one [intake and consent record](INTAKE_CONSENT.md) per real implementation before it enters review. The blank template is public; a completed record is private and is never committed or posted. The contributor and, independently, a human reviewer run every check in the [redaction checklist](REDACTION_CHECKLIST.md) on the exact candidate version; any `fail` blocks publication.

## Operating records

| Record | Template | Contract | Where the finished record goes |
|---|---|---|---|
| Task handoff | [HANDOFF.md](HANDOFF.md) | [../AGENTS.md](../AGENTS.md) | `swarm/handoffs/<TASK_ID>.md`, one per construction task, committed with the task's work. Its status is `COMPLETE` or `BLOCKED`, and release validation reads it. |
| Agent packet | [AGENT_PACKET.md](AGENT_PACKET.md) | [AGENT_PACKET_SCHEMA.md](../docs/schemas/AGENT_PACKET_SCHEMA.md) | A packet is what a community agent hands back when it stops at human review: what it was asked to do, the evidence it has, what it could not establish, the single action it recommends, the decision it hands to a named human role, and what it refused. It never records an approval. Validate it with `python3 scripts/validate_packet.py <path> --root .`; the human decision is recorded in the affected Git record, not in the packet. No fixed directory for packets is established. |
| Release evidence record | [RELEASE_EVIDENCE.md](RELEASE_EVIDENCE.md) | [../release/LAUNCH_CHECKLIST.md](../release/LAUNCH_CHECKLIST.md), [../release/OWNER_REVIEW.md](../release/OWNER_REVIEW.md) | Filled in when release validation is run against a release candidate. It is the non-secret record a human release owner reviews; the gate evidence packets in [../release/GATE_EVIDENCE.md](../release/GATE_EVIDENCE.md) cite it and list filling it in on the final candidate as a remaining step. Private evidence is pointed to, never copied in. |
| Decision record | [DECISION.md](DECISION.md) | [../community/GOVERNANCE.md](../community/GOVERNANCE.md) | The template is the record's shape: status, date, owner, context, decision, alternatives, consequences, revisit trigger. The governance model names where a decision is recorded: the Git issue, pull request, or commit for that decision. A governance change is in force only once it appears in [../community/AMENDMENTS.md](../community/AMENDMENTS.md); the founding decisions are the locked table in [../docs/DECISIONS.md](../docs/DECISIONS.md). No directory of decision records exists. |

## Must-know rules

- Front matter field names and controlled values are case-sensitive; each schema lists them.
- A template sets the starting maturity and never raises it: a Practice starts at `maturity: proposed`, a Lab at `status: proposed`, a Guide and a Story at `status: draft`, a Note at `maturity: observation`, a Project at `status: proposed`. Raising any of them is a human review decision.
- Remove every fill-in value and template note before review. Release validation (`python3 scripts/validate.py --release`) rejects unfinished markers and bracketed placeholder tokens in visible prose under the public directories.
- `python3 scripts/validate_artifacts.py` checks Practices, Guides, Labs, and Stories against their schemas. It does not read `notes/` or `projects/`; check a Note or Project against its schema by hand.
- Templates and the content made from them are CC BY 4.0; code is Apache-2.0 ([../LICENSES.md](../LICENSES.md)).
