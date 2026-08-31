# Governance

## Outcome

Practice starts founder-led so decisions are accountable and reversible where possible. It can broaden responsibility as people demonstrate reliable stewardship. Governance exists to protect the community's purpose, safety, durable public work, and ability to continue—not to create status.

The canonical record for a governance decision is its Git issue, pull request, or commit. Buzz may host discussion, but the final decision and rationale must be summarized in Git.

## Launch authority and roles

At launch, the founder is the sole governance authority and is responsible for appointing and supporting maintainers. The founder remains accountable for decisions reserved below until this document is changed through its own approval path. This does not make the founder the sole reviewer of every routine contribution.

| Role | Responsibilities | Authority boundary |
|---|---|---|
| Founder | Protect the mission and non-goals; appoint or remove maintainers; decide reserved decisions; maintain a succession record; ensure a human owns moderation and access decisions. | May delegate routine work, never final accountability for reserved decisions at launch. |
| Maintainer | Review and merge work in their assigned area; explain routine decisions; uphold contribution, safety, attribution, and conduct expectations; disclose conflicts; escalate reserved decisions. | May decide routine, reversible work within an established area. Cannot unilaterally change policy, licenses, governance, access, or enforcement outcomes. |
| Contributor | Propose, improve, review when invited, disclose relevant conflicts, and keep claims, sources, and attribution reviewable. | Has no implied governance authority from activity, authorship, or sponsorship. |
| Practitioner | Use, test, question, and share methods; report problems, evidence gaps, or conduct concerns; respect the Code of Conduct. | May participate without contributing code or content and may not be required to take on maintenance. |

Community agents may help route work or flag a concern, but cannot appoint roles, merge changes, decide policy, impose moderation outcomes, or remove people or content.

## Decision paths

Use the smallest path that keeps the decision reviewable. A decision-maker records the outcome and brief rationale in the relevant Git record; a simple merge record is sufficient for ordinary artifact work.

| Category | Examples | Approval path |
|---|---|---|
| Routine, reversible work | Correcting an artifact, accepting a scoped contribution, updating a maintained area within its documented rules, or closing a duplicate issue. | The responsible human maintainer decides after normal review. A maintainer with a conflict routes it to another eligible human or the founder. |
| Cross-area or material operating change | Changing shared conventions, starting or pausing a maintained Project, assigning a new review area, or adopting a trial process. | Discussion in a Git issue; affected maintainers provide input; founder approves at launch. A trial states its owner, scope, and review point, and does not override reserved decisions. |
| Reserved or hard-to-reverse decision | Governance, mission, non-goals, licensing, repository ownership or transfer, privileged access, maintainer appointment or removal, formal partnerships, public commitments made for the community, or retirement of a maintained Project. | A human founder decision at launch, recorded with rationale and effective date. Seek affected maintainer input when practical. No agent may make this decision. |
| Conduct or safety enforcement | Warnings, restrictions, access removal, appeals, or urgent temporary protections. | Follow [the moderation model](MODERATION.md). The designated eligible human decides; the founder retains final launch accountability and handles conflicts or gaps in coverage. |

Anyone may open an issue to request a decision, identify an unclear owner, or ask for reconsideration. A request is not a vote. Maintainers explain a routine decision when practical; reserved decisions include enough rationale for future review without disclosing private reports or security-sensitive details.

## Earning responsibility

Responsibility follows demonstrated stewardship, not post volume, popularity, seniority, or affiliation. A potential maintainer first contributes in the relevant area and leaves a reviewable record of:

- useful, accurate, and scope-respecting contributions or reviews;
- constructive handling of feedback, evidence, attribution, and uncertainty;
- reliable follow-through on a bounded responsibility; and
- conduct consistent with the Code of Conduct and no unmanaged conflict that would compromise the role.

Any contributor or maintainer may nominate a candidate in a Git issue or pull request. The record names the proposed area, examples of demonstrated work, expected responsibilities, access needed, conflicts disclosed, and a review point. At launch, the founder makes the appointment. The appointment may begin as a time-bounded or narrowly scoped trial; passing a trial extends only the documented responsibility, not automatic authority elsewhere.

As the community gains active maintainers, the founder may delegate additional routine decisions by documenting the area, limits, and review route in Git. This document's reserved decisions stay human-owned until a founder-approved governance change explicitly reallocates them.

## Conflicts, recusal, and reconsideration

People making or advising on a decision disclose a material personal, financial, employment, client, sponsorship, close-relationship, or authorship interest that could reasonably call their impartiality into question. Disclosure is not misconduct; hiding a material conflict is.

A conflicted maintainer does not make the final decision. They may supply factual context if it is clearly identified and another eligible human can assess it. Route the matter to an uninvolved maintainer; if none is available, route it to the founder. For a founder conflict, the founder identifies an uninvolved human reviewer and records the recusal and route. Conduct matters use the conflict rules in the moderation model.

A person affected by a routine or reserved decision may request reconsideration in the same Git record, naming a factual error, new evidence, material conflict, or disproportionate effect. An eligible human who did not make the decision reviews the request where available. Reconsideration does not automatically pause a safety measure or a necessary access protection.

## Role changes and removal

Removing or narrowing a role is a protection for the work, not a judgment of a person's worth. A human may pause a maintainer's privileged access when there is credible safety, security, conduct, conflict, or stewardship risk. The founder records the scope, reason at an appropriate privacy level, and review point; conduct enforcement follows the moderation model.

For a non-urgent role change, the founder gives the maintainer the reason and a reasonable opportunity to respond, then records the decision and effective date in Git or a private record when public detail would expose confidential, personal, or security information. Access is reduced to the minimum needed. Removing a role does not itself remove someone from the community; participation restrictions require the human moderation process.

## Succession and continuity

The founder keeps a private, current succession record that identifies a willing human successor or interim steward, the repository and account-transfer procedure, and the location of necessary recovery instructions. It must not contain private keys, credentials, or secrets in this repository.

When the founder expects to step back, they publish a transition record naming the successor, effective date, responsibilities, access changes, and unresolved decisions. The successor accepts the role before the transition takes effect. If the founder becomes unavailable without a published transition, active maintainers may preserve routine work and propose an interim steward, but no one may make reserved decisions until a willing human successor is confirmed through a documented, lawful transfer of control. The first confirmed successor reviews outstanding access, moderation ownership, and the governance record.

## Keep it lightweight

This model asks for a record only when responsibility, policy, access, safety, or a durable decision changes. It does not require elections, committees, titles, or consensus for ordinary contributions. Review the model when real use exposes a gap; change it only through the reserved decision path.
