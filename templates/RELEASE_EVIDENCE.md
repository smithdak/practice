# Release evidence record

Fill in this record when running release validation for a release candidate.
It captures the non-secret evidence a human release owner reviews, as required
by the [launch checklist](../release/LAUNCH_CHECKLIST.md) and the
[owner review packet](../release/OWNER_REVIEW.md).

A completed record must contain no secrets: never put keys, credentials,
recovery codes, participant data, or private invitation links in the evidence
record. Anything private — identity material, the access inventory, sponsor
names, personal approval details, hosted addresses — lives in a private
maintainer record such as the private `RELEASE` maintainer item described in
the [maintainer runbook](../ops/MAINTAINER_RUNBOOK.md). This record carries
only a non-sensitive pointer to that record.

Italic guidance below each field says what to record and what to leave out.
Every command in this template exists in this repository; do not substitute
task validation for release validation.

## Run identity

*One record per validation run against one candidate. Record roles, not the
names of private individuals.*

- Baseline commit ID: `<baseline-commit-id>`
  *The immutable commit the candidate is validated against. Do not use a
  branch name or a moving ref.*
- Candidate commit ID: `<candidate-commit-id>`
  *The exact committed candidate under review. Do not use a clean worktree in
  place of this ID.*
- Record date: `<YYYY-MM-DD>`
  *The date the checks were run, not the date this file was written.*
- Operator role: `<role>` — one of `release owner`, `maintainer`,
  `release editor`, or `contributor preparing evidence`
  *Record the role that ran the checks. Never record the name or contact
  details of a private individual in this record.*
- Validation scope: `<what was in and out of scope for this run>`
  *For example, "dry-run evidence only; no hosted apply". Do not describe
  hosted setup, public copy, or launch as approved by this run.*

## Automated checks

*Run every command from a clean checkout of the candidate commit. Record the
result as `pass`, `fail`, or `not-run` — never as assumed or partial. The
evidence pointer is either a committed path holding the retained output or a
private maintainer record pointer; never paste raw output that contains
environment values, keys, credentials, recovery codes, participant data, or
private invitation links. A pass proves the committed repository structure and
task evidence only; it does not approve hosted setup, public copy, or launch.*

| Check | Command | Result | Evidence pointer |
| --- | --- | --- | --- |
| Whitespace errors across the change range | `git diff --check <baseline>..<candidate>` | | |
| Whitespace errors in the committed candidate | `git show --check <candidate>` | | |
| Release validation | `python3 scripts/validate.py --release` | | |
| Standard-library regression suite | `python3 -m unittest discover -s tests` | | |
| Practice core-skills validator | `python3 skills/evals/validate.py --root .` | | |
| Buzz bootstrap dry-run plan | `python3 scripts/buzz_bootstrap.py --dry-run` | | |

*Notes on specific rows:*

- Do not use a clean-worktree check as evidence that the committed candidate
  has no whitespace errors; the commit IDs above make the first two rows
  reproducible.
- Retain only the non-secret stdout plan of the bootstrap dry run. Confirm
  this command needs no Buzz installation or credentials, and compare its plan
  with [community configuration](../buzz/community.json) before recording the
  result.
- A structural pass of the core-skills validator checks that Project's
  structure, not its behavioral effectiveness. Do not record it as behavioral
  evidence.

## Content and claim checks

*Record each item as `pass`, `fail`, or `not-run` with a pointer to the
reviewed artifact. Record findings about artifacts, not about people; never
record participant data, private links, or unverified outcome claims as if
they were evidence.*

- Curriculum and guide modules: `<result>` — `<evidence pointer>`
  *Links resolve and evidence framing stays proposed until a promotion record
  exists.*
- Method candidates ([context pack](../practices/001-context-pack.md),
  [workflow redesign](../practices/002-workflow-redesign.md),
  [verification gate](../practices/003-verification-gate.md)):
  `<result>` — `<evidence pointer>`
  *Confirm each remains `maturity: proposed` and `evidence_quality: none`.
  Do not record any candidate as a tested Practice here.*
- Lab and Story material: `<result>` — `<evidence pointer>`
  *Templates, schemas, and the hypothetical sample stay explicitly labeled as
  proposed or hypothetical and safe to share.*
- Launch content: `<result>` — `<evidence pointer>`
  *Confirm no real case, URL, handle, invitation route, or outcome claim is
  published without human verification. Never copy those destinations into
  this record; reference the artifact that holds them.*

## Agent-permission checks

*Record per-agent results only. The full detail — sponsor identity, exact
membership, purpose, and end date — stays in the private access inventory
described in the [Buzz security runbook](../ops/BUZZ_SECURITY.md); this record
carries the result and a pointer, never the inventory contents.*

- Unique identity per active agent, with a named human sponsor:
  `<result>` — `<private-record pointer>`
  *Record agent names and the sponsor's role. Never record owner keys,
  credentials, recovery codes, or sponsor personal details here.*
- Memberships match the least-membership model: `<result>` — `<evidence pointer>`
  *Confirm no agent has an owner key, shared credentials, an unneeded private
  membership, or permission-management, moderation, merge, or
  release-publication authority.*
- Launch role boundaries reviewed
  ([Steward](../buzz/agents/STEWARD.md), [Librarian](../buzz/agents/LIBRARIAN.md),
  [Guide Maintainer](../buzz/agents/GUIDE_MAINTAINER.md),
  [Research Auditor](../buzz/agents/RESEARCH_AUDITOR.md),
  [Release Editor](../buzz/agents/RELEASE_EDITOR.md)):
  `<result>` — `<evidence pointer>`
- Safe ownership information recorded for release ownership, final
  announcement, moderation/private reporting, and continuity:
  `<result>` — `<private-record pointer>`
  *Record that eligible humans are named in the private maintainer record;
  do not copy the names here.*

## Dry-run exit summary

*State whether the dry-run exit conditions in the
[launch checklist](../release/LAUNCH_CHECKLIST.md) are met: every applicable
item has evidence; all open items in the
[owner review packet](../release/OWNER_REVIEW.md) are explicitly still open or
human-approved; and no safety, privacy, access, licensing, or factual unknown
is being treated as resolved.*

- Dry-run exit claimed: `yes` / `no`
- If `no`, the condition that blocks exit: `<one non-secret sentence>`
- Open owner-review items confirmed still open or human-approved:
  `<result and pointer>`
- Unknowns deliberately left unresolved: `<list, or none>`
  *Record the existence and category of an unknown, never its private detail.*

## Open holds remaining

*List each open gate or hold by the name used in the
[owner review packet](../release/OWNER_REVIEW.md). Do not restate gate
contents; reference them. Never record the private evidence that clears a
hold — only that clearance is recorded privately and pointed to here.*

| Hold | Status | Blocks public launch | Private-record pointer |
| --- | --- | --- | --- |
| `<hold name>` | `OPEN` / `human-approved` | `yes` / `no` | |

*An open public-launch hold can still allow a limited private beta only when
the beta does not depend on that hold. Record that dependency judgment in the
scope field of the run identity, not as a launch claim.*

## Release owner sign-off

*Only a human release owner signs. The public record keeps personal identity
private: sign by role, date, and a non-secret approval reference that points
to the private `RELEASE` maintainer record. Never put keys, credentials,
recovery codes, participant data, or private invitation links in the signature
block.*

- Release owner role: `<role>`
- Approval reference: `<non-secret pointer to the private RELEASE maintainer item>`
- Date: `<YYYY-MM-DD>`
- Signature: `<role signature or approved approval mark>`
