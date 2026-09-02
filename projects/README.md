# Projects

A Project is open-source software or infrastructure built by the Practice community, recorded with its problem, smallest useful release, boundaries, license, and an accountable maintainer ([TAXONOMY.md](../docs/framework/TAXONOMY.md), [PROJECT_SCHEMA.md](../docs/schemas/PROJECT_SCHEMA.md)). A demonstration without intended users belongs in a Lab until it has a credible Project case.

This directory is empty until the first accepted Project record lands. A record starts at `status: proposed`; it becomes `active` only when the maintainer named in its `Ownership` section has accepted stewardship, and pausing, transferring, or retiring it is a human governance decision.

## Start one

| Step | Open |
|---|---|
| Frame it | [project.yml](../.github/ISSUE_TEMPLATE/project.yml) issue form |
| Write it | [PROJECT.md](../templates/PROJECT.md) template |
| Check it | [PROJECT_SCHEMA.md](../docs/schemas/PROJECT_SCHEMA.md): required front matter and the eight headings in order |
| Submit it | [../CONTRIBUTING.md](../CONTRIBUTING.md), Project proposal path; the proposal-to-maintained path is in [CONTRIBUTION_MODEL.md](../community/CONTRIBUTION_MODEL.md) |

## Naming

When the first Project record arrives, name it `NNN-slug.md`, mirroring `practices/`: a three-digit sequence and a short lowercase slug, for example `001-verification-checker.md` (an example name, not an existing file). The record describes the Project; its code lives at the `repo_url` in the front matter, which may be a repository-relative path when the code lives here.
