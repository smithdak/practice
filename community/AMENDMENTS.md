# Governance amendments

A running record of founder-approved governance changes, newest first.

[The governance model](GOVERNANCE.md) classes a change to governance, mission,
non-goals, or licensing as a reserved decision: a human founder decides, records
the rationale and effective date, and no agent may make the decision. This file
is that record. An amendment is in force only once it appears here.

---

## Amendment 001 — A3 eligibility for bounded merge and approved-content delivery

- **Status:** in force
- **Decided by:** founder
- **Recorded:** 2026-09-02
- **Effective:** 2026-09-02, as an eligibility change only. No operation is
  promoted by this amendment, and none runs unattended because of it.
- **Amends:** [the autonomy ladder](../docs/framework/AUTONOMY_LADDER.md)
  permanently-ineligible list, and [locked decisions](../docs/DECISIONS.md).
- **Does not amend:** [non-goals](../docs/NON_GOALS.md), which names autonomous
  moderation, banning, and content deletion, and scheduled Buzz workflows as a
  launch dependency. Both remain non-goals and neither is affected.

### What changed

The autonomy ladder listed seven operations as permanently ineligible for A3,
the act-unattended-within-bounds level. Two of those seven become eligible,
meaning they may be promoted through the normal path — a signed promotion in
`ops/autonomy/promotions.yaml` and an independently released kill switch. Both
gates still apply. Eligible does not mean enabled, promoted, or running.

**1. `merge` becomes eligible, narrowed to bounded auto-merge.**

An unattended run may merge a pull request only when every one of these holds:

- the pull request was opened by the unattended runner itself, never by a person;
- it changes nothing outside the promoted operation's declared `write_scope`;
- every required check passes and no reviewer has requested changes;
- the merge is recorded in the action ledger with the resulting commit and the
  exact command that reverts it.

**2. `publication-and-announcement` splits, and only the delivery half becomes
eligible.**

The single operation is replaced by two, because approving content and
delivering approved content are different acts that were fused into one word:

- **`publication-approval`** — deciding that content may be published.
  **Remains permanently ineligible for A3.** This is the judgment, and it stays
  human.
- **`publication-delivery`** — delivering content a human already approved.
  Becomes eligible, narrowed so that an unattended run may deliver content only
  when every one of these holds:
  - a signed approval record in Git identifies the exact content by commit or
    content hash;
  - the content is delivered byte-identical, with no edit, summary, reformat, or
    substitution of any kind;
  - the destination is named in the approval, never chosen by the agent;
  - the approval is not older than the window the promotion states, and a stale
    approval refuses rather than delivers;
  - the delivery is recorded in the action ledger against the approval reference.

  Selecting an audience, scheduling, re-publishing, and publishing anything not
  covered by a specific approval all remain outside this operation.

**3. A self-modification exclusion applies to every A3 operation, including the
two above.**

No unattended run may create, change, merge, or deliver a change to any file
that governs its own bounds. At minimum: `docs/DECISIONS.md`, `docs/NON_GOALS.md`,
`docs/OWNER_GATES.md`, `community/GOVERNANCE.md`, this file,
`docs/framework/AUTONOMY_LADDER.md`, anything under `ops/autonomy/`, and
anything under `.github/`. An agent that can widen its own bounds has no bounds,
so this exclusion is not itself waivable by a promotion.

### Rationale

The four candidates considered were merge, publication, maturity promotion, and
moderation. These two were selected because they are the two whose failures are
recoverable.

A bounded merge is reversible with a single `git revert`, is repository-scoped,
and reaches no member. It was also the operation without which the unattended
loop does not close: every scheduled run would still wait on a person to merge a
pull request that a machine had already checked.

Delivery of already-approved content moves no judgment. A human still decides
that the content is fit to publish and where it goes; what becomes automatable
is carrying an approved artifact, unchanged, to a named destination. Splitting
the operation is what makes this safe to state — the previous wording fused the
decision and the delivery, so eligibility for either would have implied both.

### What was considered and declined

Recording these matters as much as recording what passed, because a future
reader will otherwise assume they were never raised.

- **`maturity-promotion` — declined.** A method is a tested Practice because a
  human reviewed recorded evidence and said so. Automating that flip would make
  the label mean that a script checked boxes, which is the thing Practice exists
  to be an alternative to. Declining this protects the project's central claim
  about itself.
- **`moderation-and-removal` — declined.** It is the one category here that acts
  on people rather than files, it is not reversible the way a file write is, and
  it is named in [non-goals](../docs/NON_GOALS.md) and built around in [the
  moderation model](MODERATION.md).
- **`owner-identity-and-keys` — not proposed.** There is no legitimate form of an
  agent holding owner identity material. This is a security boundary rather than
  a policy preference.
- **`license-and-governance-change` — not proposed.** An agent able to amend the
  rules that bound it can widen its own bounds. The self-modification exclusion
  above states the general form of this.
- **`owner-reserved-decision` — not proposed.** Automating the decisions an owner
  reserved to themselves is self-contradictory.

### What is still required before either operation runs

This amendment changes eligibility and nothing else. Before either operation
runs unattended, all of the following must still happen, and each is a separate
human act:

1. a promotion proposal completed and signed for that specific operation;
2. the promotion transcribed into `ops/autonomy/promotions.yaml`;
3. the kill switch released, as a separate change;
4. the guard permitting the operation, which it will not do while any
   precondition fails.

`publication-delivery` additionally depends on decisions outside this
repository: gate 5 (public invitation path), hold 1 (public invitation
promotion), and hold 7 (publication destinations) all remain open in [the owner
review packet](../release/OWNER_REVIEW.md). Nothing here clears them.

### Review point

Reconsider this amendment when the first promotion proposal is signed for either
operation, and again after the first month in which either has actually run. A
person affected by it may request reconsideration through the path in [the
governance model](GOVERNANCE.md).
