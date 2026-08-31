# Build

Make an AI-native system reproducible enough for another Practitioner to run,
inspect, and challenge. Separate implemented behavior from the proposed next
version.

## Open with a system card

```text
Job and intended user: …
Inputs and outputs: …
Allowed tools or actions: …
Approval boundary: …
Evaluation and pass condition: …
Known failure and recovery path: …
Smallest reproducible artifact: …
```

Share the code, configuration, test, trace, or architecture decision that makes
the claim inspectable. A demo is not evidence of reliability; say what the
evaluation does and does not establish.

### Example (hypothetical)

> A tool extracts five fields from synthetic support requests. It may read only
> the fixture folder and write one JSON file. The test checks the schema and an
> intentionally missing field. A person reviews the output before any record is
> changed.

Use `projects` when the work has a bounded open-source user problem, proposed
maintainer, and contribution path. Use `showcase` for an implementation result
or lesson. Use `automate` when the main artifact is still a workflow map.

Never post credentials, private keys, confidential code, or restricted data.
Keep the capability portable unless a vendor-specific dependency is essential
and stated.
