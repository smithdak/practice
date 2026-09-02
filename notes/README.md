# Notes

A Note is a bounded, dated record of one observation, question, decision, or early piece of evidence: useful now, but not yet a reusable method or a complete study ([TAXONOMY.md](../docs/framework/TAXONOMY.md), [NOTE_SCHEMA.md](../docs/schemas/NOTE_SCHEMA.md)). It separates what was observed from what is inferred, and it may later be promoted to a Practice, Lab, or Story.

This directory is empty until the first accepted Note lands. Source notes for current facts belong here too: preserve the claim as a Note, cite the primary source, and record an as-of date beside any source that can change.

## Start one

| Step | Open |
|---|---|
| Frame it | [note.yml](../.github/ISSUE_TEMPLATE/note.yml) issue form |
| Write it | [NOTE.md](../templates/NOTE.md) template |
| Check it | [NOTE_SCHEMA.md](../docs/schemas/NOTE_SCHEMA.md): required front matter, the four headings in order, and the maturity states `observation`, `validated`, `promoted`, and `withdrawn` |
| Submit it | [../CONTRIBUTING.md](../CONTRIBUTING.md), Note path |

## Naming

When the first Note arrives, name it `NNN-slug.md`, mirroring `practices/`: a three-digit sequence and a short lowercase slug, for example `001-citation-check-failure.md` (an example name, not an existing file). One Note records one claim or question; split unrelated observations into separate files.
