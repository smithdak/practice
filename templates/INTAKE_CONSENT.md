# Intake and Consent Record — Story or Workflow Clinic

> **How to use:** The contributor and the human intake contact complete one record per real workflow or implementation contribution before it enters publication review as a [Story](STORY.md) or Workflow Clinic artifact. The blank template is public; a completed record is **private** — keep it in the access-controlled intake location maintained by a human, and never commit it to Git or post it to Buzz. The public repository receives only the redacted artifact and one ledger row (Part 6).

These statements are operational commitments between the contributor and the Practice maintainers, not legal advice or a legal review. For ambiguous legal situations, the human maintainer routes the question to governance before publication.

## Part 1 — Contribution summary

*Record only what a safe public description allows. Write a structural summary in categories, roles, and steps — not raw records, documents, screenshots, or identifiers.*

- Record date: `[YYYY-MM-DD]`
- Intake ID: `[non-identifying ID, e.g., IC-2026-001]`
- Contributor handle (chosen public name): `[@handle]`
- Preferred reply route: `[how the maintainer reaches the contributor]` — *kept in this private record only; never copied into the ledger, Git, or Buzz*
- Artifact type: `[story | workflow-clinic draft]`
- Working title: `[title]`
- Organization disclosure: `[public | anonymized | withheld]` — *must match the definitions in the [Story schema](../docs/schemas/STORY_SCHEMA.md)*
- What is being shared: `[3–6 sentences: the recurring work, the change made, what another Practitioner can learn, and the role labels or categories used]`

## Part 2 — What must not be shared

*This contribution must meet the repository's [Safe to publish](../docs/QUALITY_BAR.md#safe-to-publish) bar and the [data red lines](../ops/METRICS.md#data-not-to-collect). The contributor confirms the summary and every attached artifact exclude:*

- secrets, credentials, tokens, private keys, recovery codes, and signed or internal-only URLs;
- client, employer, or partner-confidential material, including prompts or outputs that contain it;
- personal information about any person — the contributor's own or others' — including names, contact details, health, employment, financial, or location details;
- internal URLs, hostnames, system and dashboard names, ticket IDs, and project codenames (Part 1 categories and Part 4 substitutions are used instead);
- regulated or restricted records of any kind; and
- third-party material (quotations, images, datasets, vendor documentation) without a stated basis to reuse it.

If an excluded detail is load-bearing for the story, describe it as a category or leave it out — do not submit it and plan to redact later. When unsure whether a detail is safe to share, the contributor omits it and asks a responsible human in their own context; the session rule [stop rather than sanitize in public](../ops/FIRST_PRACTICE_SESSION.md#non-negotiable-operating-rules) applies.

## Part 3 — Consent statements

*Each statement is an independent choice with default `no`. Record the choice and date per statement; participation, capture, attribution, and publication are never inferred from one another. See the [clinic consent model](../ops/FIRST_PRACTICE_SESSION.md#consent-and-decline-record).*

| ID | Statement | Choice | Date |
|---|---|---|---|
| C1 | **Publication scope.** I consent to publishing the redacted contribution described in Part 1 as a durable Git artifact, and to maintainers referencing that published artifact in community channels. | `[yes / no]` | `[YYYY-MM-DD]` |
| C2 | **License grant.** I have the right to submit this material, and I grant Practice permission to publish it under CC BY 4.0, the repository's default content license per [locked decisions](../docs/DECISIONS.md) and [LICENSE-CONTENT.md](../LICENSE-CONTENT.md). I understand anyone may reuse and adapt it with credit. I have identified all third-party material, which remains under its own terms per [LICENSES.md](../LICENSES.md). | `[yes / no]` | `[YYYY-MM-DD]` |
| C3 | **Attribution.** Attribute my contribution as: `[chosen handle | role label only | no attribution]`. | `[as stated]` | `[YYYY-MM-DD]` |
| C4 | **Withdrawal.** I understand my withdrawal rights as recorded below: I may withdraw before publication at any time without explanation; after publication, no erasure is promised. | `[yes / no]` | `[YYYY-MM-DD]` |
| C5 | **Human review.** I understand publication is not promised and requires an independent human review pass on the exact candidate version using the [redaction checklist](REDACTION_CHECKLIST.md); a reviewer may accept, request revision, reject, or keep the artifact private. | `[yes / no]` | `[YYYY-MM-DD]` |
| C6 | **Accuracy.** The material is accurate as described, no result is invented, and anything hypothetical, approximate, or unmeasured is labeled as such. | `[yes / no]` | `[YYYY-MM-DD]` |

**Withdrawal before publication** (before merge or any public appearance): the contributor notifies the maintainer through the reply route; the draft leaves the review queue without needing an explanation, and working copies are returned or deleted per the agreed retention action.

**After publication:** the Git history persists and Practice does not promise erasure. A correction, attribution change, or withdrawal request is routed to a human maintainer, who records what is possible — which may include marking the Story `withdrawn` as the [Story schema](../docs/schemas/STORY_SCHEMA.md#status-and-evidence-guidance) allows, while retaining the record of why it is no longer recommended.

## Part 4 — Redaction requests

*The contributor marks specific details that must be removed or generalized before publication. Recording each request keeps the redaction honest and reviewable instead of silent; the resulting limitation is then stated in the artifact's evidence record.*

| Detail or phrase | Requested treatment | Recorded decision |
|---|---|---|
| `[detail]` | `[remove | generalize | replace with role label]` | `[what was done, by whom]` |
| `[detail]` | `[remove | generalize | replace with role label]` | `[what was done, by whom]` |

## Part 5 — Review acknowledgment and outcome

*Completed by the human maintainer after the review pass. Never infer consent from attendance, submission, or reviewer enthusiasm.*

- Intake contact role: `[role]`
- Redacted draft shown to contributor before review: `[yes / no]`
- Review outcome: `[accepted | revision requested | rejected | kept private]` — `[YYYY-MM-DD]`
- Review record reference: `[pointer to the completed redaction checklist and decision note]`

## Part 6 — Ledger row (non-secret)

*One row per contribution goes in the intake ledger — an access-controlled spreadsheet or Markdown file maintained by a human, following the [minimal manual measurement rules](../ops/METRICS.md#minimal-manual-measurement-at-launch). The row carries no personal data beyond the contributor's chosen handle: no real names, contact details, employers, consent-statement text, or workflow details. Completed consent records never enter Git or Buzz.*

Row format:

```text
[intake-id] | [date YYYY-MM-DD] | [story|workflow-clinic] | [contributor handle] | [publication scope: story|clinic-draft] | [attribution: handle|role-only|none] | [status] | [artifact link] | [reviewer role]
```

Example (illustrative only, not a real intake):

```text
IC-2026-014 | 2026-09-01 | workflow-clinic | @river-otter | clinic-draft | role-only | in review | practices/00X-<slug>.md | maintainer
```

Status vocabulary: `submitted` · `in review` · `revision requested` · `published` · `withdrawn` · `declined`.
