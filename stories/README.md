# Stories

A Story is a real implementation documented through its before state, intervention, result, and lessons, with the quality of its evidence stated ([TAXONOMY.md](../docs/framework/TAXONOMY.md)). An invented, planned, or composite scenario is not a Story; label it Hypothetical or Example.

## What exists

No real Story has been published.

| File | What it is |
|---|---|
| [SAMPLE_HYPOTHETICAL.md](SAMPLE_HYPOTHETICAL.md) | A fictional sample that shows the Story format. It contains no real organization, Practitioner, measurement, or outcome, and it must not be cited as evidence ([STORY_SCHEMA.md](../docs/schemas/STORY_SCHEMA.md) says the same). |

## Add one

1. Complete the [intake and consent record](../templates/INTAKE_CONSENT.md) with a human intake contact, then run the [redaction checklist](../templates/REDACTION_CHECKLIST.md). The completed consent record is private and is never committed; the public repository receives only the redacted Story and one ledger row.
2. Open the [story.yml](../.github/ISSUE_TEMPLATE/story.yml) issue form.
3. Write from the [STORY.md](../templates/STORY.md) template and check it against [STORY_SCHEMA.md](../docs/schemas/STORY_SCHEMA.md); `python3 scripts/validate_artifacts.py` validates every `stories/*.md` except this index.
4. Follow the Story evidence row in [../CONTRIBUTING.md](../CONTRIBUTING.md): before, intervention, result, and lessons, with confidential details omitted or anonymized only with permission and no invented outcomes.

Name a real Story `NNN-slug.md`, mirroring `practices/`. A file whose name starts with `SAMPLE_` is format documentation; release validation skips it and it is never evidence.
