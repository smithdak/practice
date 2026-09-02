# A3 promotion proposal

**As of:** 2026-09-02

## The problem this record closes

[The autonomy ladder](../../docs/framework/AUTONOMY_LADDER.md) reserves A3 —
act-unattended-within-bounds — to a human, and names the evidence that decision
needs: the operation, the bound it may act inside, the rate and scope limit, the
reversal a human can execute without the agent, the human who owns the bound,
and the review point. The ladder records that no such decision exists in this
repository.

Until now there was nowhere to write one. The risk that leaves is not that an
operation gets promoted too easily. It is that one gets promoted informally — in
a message, a meeting, or a commit body — and the repository keeps no record of
what was weighed, so nobody can later tell whether the reversal was tested or
merely asserted. This file is that record.

It is fillable so the decision is legible afterwards. It is not a shortcut to
yes. A blank proposal is not a queue, and the absence of a filled one is not a
backlog.

**Nothing in this repository is at A3.** This file promotes nothing, and a copy
of it filled in and signed still promotes nothing until the two transcription
steps below are done by a human.

## Signing is half the change

Two records must change before any operation runs unattended. They are
independent: neither follows from the other, and a signature makes neither.

1. **The promotion.** A human transcribes a signed proposal into
   [the promotion record](promotions.yaml) as an entry in `promotions`, field
   by field. No script writes that entry, and this file is not that entry.
2. **The kill switch.** That same record ships `kill_switch: engaged`, and every
   operation is refused while it is engaged — including a promoted one. Releasing
   it is a separate, independent decision, recorded as its own change, and it is
   the cheaper half to reverse: setting it back to `engaged` is one word and
   stops every operation at once. A proposal written on the assumption that the
   switch will follow the signature has misread the design.

`scripts/autonomy_guard.py` refuses by default and permits only when every
precondition holds, so an unsigned proposal, an untranscribed signature, and an
engaged kill switch each independently stop the run. That is the intended
resting state.

## Before a proposal is worth writing

A proposal that fails any of these is not admissible, and the correct response is
to stop rather than to record an exception.

- **The operation is catalogued.** It has an entry in
  [the operation catalog](operations.yaml) with an id, a command, a write
  scope, a reversal, and a blast radius. An operation invented in the proposal
  itself has no catalog entry to check the write scope against.
- **It is not on the permanently ineligible list.** The seven rows under
  [Permanently ineligible for A3](../../docs/framework/AUTONOMY_LADDER.md#permanently-ineligible-for-a3)
  may never run unattended, and the ladder's near-neighbour rule applies: an
  operation adjacent to one of those rows is treated as that row until a human
  says otherwise. Publishing, merging, moderating, changing a `maturity` or
  `evidence_quality` value, and touching owner identity material are the act,
  not the preparation.
- **The attended levels already hold.** R1, R2, and R3 in
  [Raising a level](../../docs/framework/AUTONOMY_LADDER.md#raising-a-level) are
  cumulative. An operation whose R1 evidence is incomplete cannot reach R4 by
  skipping the ones underneath.
- **A dossier exists.** [The candidate dossiers](CANDIDATES.md) hold the write
  scope, reversal, blast radius, and evidence gaps this proposal is filled in
  against. A proposal for an operation with no dossier is a proposal nobody has
  examined.
- **The reversal has been executed at least once.** See section 4. An asserted
  reversal is a blank field.
- **The proposer has run the guard and seen it refuse.** Record the command and
  its exit code in section 1. A proposer who has not watched the substrate refuse
  does not know what they are changing.

---

## The proposal

Copy this section into a new file under `ops/autonomy/`, one file per operation.
Do not bundle two operations into one proposal: the write scope, the reversal,
and the blast radius are per-operation facts, and a bundled signature cannot be
partially withdrawn.

Replace each `<placeholder>` with a value. Italic guidance says what belongs in
the field and what does not. Leave a field blank rather than filling it with
something you have not checked; a blank field is a finding.

### 1. Identity of this proposal

*Roles, not the names of private individuals. Commit ids, not branch names.*

- Operation id: `<operation-id>` — must match an id in
  [the operation catalog](operations.yaml) exactly.
- Catalog entry read at commit: `<commit-id>`
- Proposal drafted on: `<YYYY-MM-DD>`
- Proposer role: `<role>` — a role from
  [the governance model](../../community/GOVERNANCE.md) or
  [the private beta operating kit](../BETA_OPS.md); for example
  `maintainer on duty` or `agent sponsor`.
- Guard refusal observed: `python3 scripts/autonomy_guard.py --operation <operation-id> --root .`
  exited `<exit-code>` with the reason `<reason the guard printed>`.
  *Record the reason verbatim. If the guard permitted the operation, stop: the
  substrate is not in the state this proposal assumes.*

### 2. What the operation does, and what unattended running is worth

*Two paragraphs, not a pitch.*

- What it does: `<one sentence, matching the catalog summary>`
- What a person does today instead: `<the exact command, and who runs it>`
- What running it unattended buys: `<the concrete saving, in the unit it is
  actually saved in>`
  *State it as time, latency, or coverage, and be specific. "Saves a maintainer
  four minutes a week" is a valid and useful answer; write it if it is the true
  one. If the honest answer is that it buys a dated series nobody has agreed to
  read, write that instead — it is the most decision-relevant sentence in this
  document.*
- Who has agreed to read the output, by role: `<role>`
  *Not who might find it useful. Who has agreed. An output with no reader is an
  artifact that looks maintained and is not, which is worse than no artifact.*

### 3. Write scope, and why it is the narrowest that works

*The write scope in the signed entry must equal the catalog entry's scope
exactly; a promotion whose scope disagrees with its catalog entry is rejected by
the guard. This section is where a human checks that the scope in both places is
the right one.*

- Declared write scope: `<glob>`, `<glob>`
- Paths inside that scope that already exist: `<paths, or "none">`
- What the scope deliberately excludes: `<the adjacent paths a wider scope would
  have included, and what would go wrong if it did>`
- A wider scope that was considered and rejected: `<the scope, and the reason>`
  *If no wider scope was considered, the narrowness has not been tested. Consider
  one.*
- Negative check: name one path in this repository the operation must never
  touch, and show that the glob excludes it: `<path>` — excluded because
  `<reason>`.
  *Two glob dialects are in play and they disagree. `scripts/autonomy_guard.py`
  matches a write scope with `fnmatchcase`, where `*` crosses a slash, so
  `ops/status/*.md` also permits `ops/status/archive/old.md`. The evidence globs
  in [`ops/cadence.yaml`](../cadence.yaml) are matched with `Path.glob`, where
  `*` stops at a slash, so `ops/*.md` there means the eight files directly under
  `ops/` and nothing below. Check the semantics of the file you are reading
  rather than the pattern's appearance.*
- Does anything read the paths in this scope as evidence? `<yes/no, and what>`
  *A scope that writes into a directory another check reads creates a loop where
  the operation's own output makes the repository look attended. Check
  [`ops/cadence.yaml`](../cadence.yaml) evidence globs and the schema and link
  validators before answering no.*

### 4. The reversal, executed rather than asserted

*This section is not filled in from the catalog. It is filled in after somebody
has actually undone a run.*

- Reversal as catalogued: `<the reversal text from operations.yaml>`
- Reversal executed on: `<YYYY-MM-DD>`
- The run it reversed: `<ops/ledger/YYYY-MM-DD-run-id.md>`
- Executed by role: `<role>`
- Exact steps taken: `<the commands or actions, in order>`
- Repository state afterwards: `<what was checked to confirm the reversal was
  complete, and the result>`
- Could a person outside the agent's context perform it? `<yes/no>` — with
  `<what they needed: repository write access, a merge button, a shell, nothing
  else>`
  *The ladder requires a reversal a human can execute without the agent. A
  reversal that needs the runner, the agent's credentials, or knowledge only the
  run has is not a reversal.*
- Time from noticing to reversed: `<duration>`

If this section cannot be filled in because no run has happened, the proposal is
not ready. Run the operation attended, reverse it, and come back.

### 5. Blast radius after a month unnoticed

*Assume the operation runs on its schedule, misbehaves from the first run, and
nobody looks for a month. Answer for that case, not for the case where somebody
notices.*

- Runs in a month at the declared rate: `<count>`
- What accumulates: `<files, entries, pull requests, and how many>`
- Who reads the wrong output, and what they do with it:
  `<role, and the decision they would make from it>`
- Does anything downstream treat the output as evidence? `<yes/no, and what>`
  *Check whether the paths appear in a cadence evidence glob, a metrics
  denominator, a release brief range, or a gate evidence packet.*
- Does any of it reach a community member or a public surface? `<yes/no>`
  *If yes, stop. That is `publication-and-announcement`, permanently ineligible.*
- Does any of it enter a released artifact or a validated directory?
  `<yes/no, and which validator>`
- Worst honest outcome: `<the single worst state the repository could be in on
  day 30>`
- How the wrongness would be noticed at all: `<the specific signal, and who sees
  it>`
  *"Someone would notice" is not an answer. A report that is quietly wrong looks
  exactly like a report that is right; name the check that distinguishes them.*

### 6. Demotion triggers that apply

The A3 triggers in the ladder are inherited and not optional. Copy the ones that
apply into the signed entry's `demotion_triggers` list, and record here which are
machine-observable and which need a person. `scripts/demotion_check.py` is this
substrate's detector for the observable triggers; name it, or name the person,
for every row.

| Trigger | Source | Observable by | How it is checked |
| --- | --- | --- | --- |
| An action taken outside the recorded bound | Ladder, A3 | `<script or person>` | `<how>` |
| An action taken with no reversal path recorded | Ladder, A3 | `<script or person>` | `<how>` |
| An action taken after the review point passed without a renewal record | Ladder, A3 | `<script or person>` | `<how>` |
| An action on an operation since added to the permanently ineligible list | Ladder, A3 | `<script or person>` | `<how>` |
| `<any inherited A0, A1, or A2 trigger that can fire for this operation>` | `<ladder section>` | `<script or person>` | `<how>` |

- What happens on a trigger: `<the exact state the operation returns to, and who
  is told>`
  *A demotion needs no decision — it is automatic on the observable trigger. The
  human decision that follows is whether to restore the level, not whether the
  demotion happened.*
- Triggers no script can see: `<list them>`
  *Every trigger in this list is one a person has to catch. Count them, and read
  section 5 again with that count in mind.*

### 7. Evidence that exists, and evidence that does not

*Two lists. Every item in the first carries a repository pointer. The second list
is not a plan to collect anything; it is what the signer is deciding without.*

**Exists** — for each item: `<claim>` — `<path or command>` — `<what it proves,
stated no more broadly than the record supports>`.

**Does not exist** — for each item: `<the evidence>` — `<why it does not exist
today>` — `<what the signer is therefore taking on trust>`.

*A test suite proves the component behaves as specified. It does not prove the
operation should run unattended, and a proposal that lists tests under "exists"
without saying which question they answer has confused the two.*

### 8. Who reviews the pull requests, and how often

An unattended run arrives as a pull request against the default branch, never as
a push. The pull request is the reversal: closing it unmerged reverses the run at
zero cost, which is why the shape was chosen.

- Reviewing role: `<role>`
- Review rhythm: `<how often, and in which cadence pass>`
  *Name the pass in [the weekly cadence](../WEEKLY_CADENCE.md) that absorbs this
  work, or state that a new pass is being created and who owns it. Review work
  that lands in no pass is work nobody has agreed to do.*
- What happens to a pull request unreviewed after `<n>` days: `<the rule>`
  *A stack of unreviewed pull requests from an unattended operation is the
  failure this design is supposed to make visible. Decide the rule now, while it
  is cheap.*
- What a reviewer checks, in order: `<the checks>`
  *At minimum: the diff touches only the declared write scope; the ledger entry
  is present and names its reversal; the content is right, not merely
  well-formed.*
- Who is told when a pull request is closed unmerged: `<role>`

### 9. Review point and renewal

- Review point: `<YYYY-MM-DD>` — no more than `<n>` days from the first run.
- Who holds it: `<role>`
- What is reviewed: `<the ledger entries, the merged and closed pull requests,
  and the evidence gaps from section 7>`
- What happens if the review point passes with no renewal record: the operation
  is demoted automatically by the ladder's A3 trigger, and the next run is
  refused.

**Silence is not renewal.** A renewal is a new record with its own date and
signing role.

### 10. Reasons to decline

*Write this section in prose. It is not a checklist and it has no boxes, because
the point is not that the risks were enumerated — it is that the proposer
understood them well enough to argue the other side.*

State at least three specific reasons a reasonable person could decline this
proposal. Each one names the concrete thing that would go wrong, not a category
of risk. Then say, for each, why you nonetheless think the proposal is worth
putting in front of a signer — or, if you cannot, say that and stop.

Prompts, to be answered rather than ticked:

- What is the strongest argument that this operation should stay at the level it
  is at now, and who would make it?
- What would make this proposal look obviously wrong in six months?
- What does the operation do when its input is malformed, missing, or larger than
  anything it has seen? Has that been observed, or is it inferred from the code?
- If the output is subtly wrong for a month, what decision gets made on it, and
  by whom?
- What is the cheapest alternative that gets most of the value with no unattended
  write at all — a scheduled check that reports and writes nothing, an extra
  command in an existing pass, or one line in a report that already runs?
- Who is worse off if this is promoted and nobody notices for a quarter?

A proposer who cannot fill this section in has not yet understood the operation
well enough to propose it.

### 11. Signature

*This block is unsigned in the template and stays unsigned. Do not pre-fill a
role or a date, and do not copy a signature between proposals.*

- Signing role: `<role>` — one of `founder`, `beta-owner`, or
  `continuity-owner`, which is the set [the promotion record](promotions.yaml)
  accepts in `signed_by`. A promotion to A3 is a reserved, hard-to-reverse
  decision under [the governance model](../../community/GOVERNANCE.md), so it is
  the founder's at launch; no maintainer, agent sponsor, or agent may sign it.
- Signed on: `<YYYY-MM-DD>`
- What the signature means: the signer has read sections 1 to 10, accepts the
  blast radius in section 5 as the cost of being wrong, owns the bound by name,
  and holds the review point in section 9.
- What the signature does not mean: it does not release the kill switch, clear an
  owner gate or operating hold, enable an agent, change any `maturity` or
  `evidence_quality` value, or authorize any operation other than the one named
  in section 1.

---

## After a proposal is signed

A signature on a document is not a change in behaviour. A human performs both of
the following; no script does either.

1. **Transcribe the entry.** Add one entry to `promotions` in
   [the promotion record](promotions.yaml), matching the shape fixed by the
   phase plan:
   `operation`, `level`, `write_scope`, `evidence`, `demotion_triggers`,
   `signed_by`, `signed_on`. The `write_scope` must equal the catalog entry's
   scope exactly — the guard rejects a promotion whose scope disagrees with its
   catalog entry, which is the mechanical check that a transcription error cannot
   widen a bound. `level` is `A3` and nothing else; `signed_by` is `founder`,
   `beta-owner`, or `continuity-owner`; `signed_on` is an ISO date that is not in
   the future; and every path in `evidence` must exist, so put the path of the
   signed proposal there and commit it first.
2. **Decide the kill switch separately.** The switch stays `engaged` until a
   human changes it in its own edit, with its own reason. Nothing about signing a
   proposal implies that change, and the two are deliberately not one edit. In
   reverse — under pressure — the order flips: set `kill_switch` back to
   `engaged` first, because that one word stops every operation at once, and
   remove the promotion entry afterwards.

Between those two steps the operation is promoted and still refused. That is a
useful state to sit in, not a misconfiguration.

## What this record cannot do

- It cannot promote an operation on the permanently ineligible list, or a near
  neighbour of one.
- It cannot clear an owner gate or an operating hold. Gate 6 is recorded OPEN in
  [the owner review packet](../../release/OWNER_REVIEW.md), every registry entry
  reads `not_enabled`, and no filled proposal changes either.
- It cannot change a `maturity` or an `evidence_quality` value, or be cited as
  evidence for a change to one.
- It cannot widen a write scope past the catalog entry.
- It cannot cover two operations, or be renewed by leaving it alone.
- It is not itself the promotion record. [`ops/autonomy/promotions.yaml`](promotions.yaml) is.

## Sources

As of: 2026-09-02.

- [docs/framework/AUTONOMY_LADDER.md](../../docs/framework/AUTONOMY_LADDER.md) —
  the A3 clauses, the R4 evidence set, the demotion triggers, and the seven
  permanently ineligible operations.
- [ops/autonomy/CANDIDATES.md](CANDIDATES.md) — the dossier a proposal is filled
  in against.
- [ops/autonomy/operations.yaml](operations.yaml),
  [ops/autonomy/promotions.yaml](promotions.yaml), and
  [ops/autonomy/README.md](README.md), with `scripts/autonomy_guard.py` — the
  catalog, the promotion record, and the guard that refuses by default.
- [community/GOVERNANCE.md](../../community/GOVERNANCE.md) — the reserved-decision
  path a promotion travels, and the roles that may sign one.
- [ops/BETA_OPS.md](../BETA_OPS.md) — the operating role vocabulary used in the
  fields above.
- [ops/AUTONOMOUS_OPERATION.md](../AUTONOMOUS_OPERATION.md) — what runs without a
  person today and what does not.
- [release/GATE_EVIDENCE.md](../../release/GATE_EVIDENCE.md) and
  [release/OWNER_REVIEW.md](../../release/OWNER_REVIEW.md) — the house pattern for
  an evidence packet, and the gates and holds no proposal moves.
- [templates/RELEASE_EVIDENCE.md](../../templates/RELEASE_EVIDENCE.md) — the
  fill-in conventions this template follows.
