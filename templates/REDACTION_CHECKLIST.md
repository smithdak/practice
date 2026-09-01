# Redaction Checklist — Story or Workflow Clinic publication

> **How to use:** The contributor runs every check on the exact draft before submitting it for review; a human reviewer then runs every check independently on the exact candidate version before publication. One pass each, recorded in the results table at the end. Any `fail` blocks publication until it is fixed, redacted, or the artifact is kept private. Pair this checklist with the [intake and consent record](INTAKE_CONSENT.md).

## Candidate

- Artifact: `[relative path]`
- Version or commit: `[version or commit ID]`
- Checklist date: `[YYYY-MM-DD]`
- Contributor handle: `[@handle]`
- Reviewer role: `[role]` — *the reviewer is not the contributor; a host who prepared the artifact may not self-approve (see the [editorial checklist](../content/launch/FIRST_10.md#editorial-and-release-checklist))*

Record each check as `pass`, `fail`, or `n-a` with a one-line note. A check that could not be completed is a `fail`, not a pass. When any item is uncertain, redact or keep the artifact private.

## 1. Third-party content

- [ ] Every quotation, excerpt, image, dataset, diagram, or code block created by someone else is identified with its source and license or permission basis.
- [ ] Summarize-and-link was preferred over copying; nothing was included merely because it is publicly accessible per the [licensing map](../LICENSES.md).
- [ ] Required credit, license link, and change indication are present per the [Attribution and Reuse Policy](../community/ATTRIBUTION.md), and nothing is reused under a broader claim than its terms allow.
- [ ] Vendor documentation, articles, transcripts, and screenshots from other sources are not included without a stated basis to reuse them.

## 2. Metrics provenance

- [ ] Every number — counts, durations, sizes, costs, percentages — traces to a source record named in the artifact, or is labeled `approximate` or `hypothetical`.
- [ ] Unmeasured results say `Not measured` instead of an estimate, per the [Story template](STORY.md).
- [ ] Self-reported results are marked self-reported and do not imply independent verification, per the [metrics contract](../ops/METRICS.md).
- [ ] No invented customer, user, outcome, or case study appears.

## 3. Personal information scan

- [ ] No personal information about any person beyond the contributor's chosen handle and agreed role labels.
- [ ] Client, employee, customer, and other third-party identifiers are removed or generalized.
- [ ] Combinations of dates, volumes, locations, tool versions, and team details cannot re-identify a person or organization, per the [Story schema anonymization rules](../docs/schemas/STORY_SCHEMA.md#anonymization-rules).
- [ ] The `organization` status matches reality: `public` named with permission, `anonymized` deliberately generalized, `withheld` not identifiable.

## 4. Secrets scan

- [ ] No credentials, tokens, private keys, recovery codes, connection strings, session identifiers, or signed URLs anywhere in the artifact — including code blocks, config or environment dumps, logs, and pasted chat excerpts.
- [ ] Example values are obvious placeholders, not modified real credentials.
- [ ] No unlisted internal endpoint or account identifier appears.

## 5. Internal-system name substitution

- [ ] Internal hostnames, internal URLs, dashboard and tool names, repository names, ticket IDs, and project codenames are replaced with role labels such as "the internal review queue".
- [ ] Each substitution is recorded in the artifact's anonymization or evidence section so the redaction is visible, per the [Story schema](../docs/schemas/STORY_SCHEMA.md#anonymization-rules) requirement to record what was redacted.
- [ ] Publicly documented product names are kept only where the account needs them and disclosure implies no confidential access.

## 6. Screenshots and media

- [ ] No media shows real customer or personal data, live dashboards, internal URLs, revealing browser tabs or titles, file paths, or people who have not consented.
- [ ] Media rebuilt as illustrative mockups is labeled `hypothetical`.
- [ ] Media adds reviewable information; decorative media that only adds risk is removed.

## 7. Consent and license

- [ ] A completed [intake and consent record](INTAKE_CONSENT.md) exists for this contribution, and the submitted draft matches its recorded publication scope and redaction requests.
- [ ] Attribution matches the agreed choice, and `authors` lists publishable handles only.
- [ ] The license statement matches the content default ([LICENSE-CONTENT.md](../LICENSE-CONTENT.md)), and third-party items keep their own notices.

## Results

| Check | Contributor | Human reviewer |
|---|---|---|
| 1. Third-party content | `[pass / fail]` | `[pass / fail]` |
| 2. Metrics provenance | `[pass / fail]` | `[pass / fail]` |
| 3. Personal information | `[pass / fail]` | `[pass / fail]` |
| 4. Secrets | `[pass / fail]` | `[pass / fail]` |
| 5. Internal-system names | `[pass / fail]` | `[pass / fail]` |
| 6. Screenshots and media | `[pass / fail]` | `[pass / fail]` |
| 7. Consent and license | `[pass / fail]` | `[pass / fail]` |

## Sign-off

*Both sign for the same candidate version. One person cannot sign both roles.*

- Contributor: `[@handle]` — `[YYYY-MM-DD]` — every check passed on this version, or unresolved fails mean the artifact is being kept private.
- Human reviewer (role): `[role]` — `[YYYY-MM-DD]` — `[passed | blocked: reason]`; the publication decision is recorded in the consent record (Part 5).

For ambiguous legal situations — rights, license scope, re-identification risk, or confidentiality — the human maintainer routes the question to governance before publication, and [uncertain material is not merged](../community/ATTRIBUTION.md#when-uncertain).
