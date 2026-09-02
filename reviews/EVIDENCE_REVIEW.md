# Evidence review — Wave E (adversarial, Q6)

**Reviewer:** Q6 (adversarial evidence review). **Date:** 2026-09-01. **Scope:** every
evidentiary claim in the three Wave E trial Labs — [labs/002-context-pack-trial.md](../labs/002-context-pack-trial.md),
[labs/003-workflow-redesign-trial.md](../labs/003-workflow-redesign-trial.md),
[labs/004-verification-gate-trial.md](../labs/004-verification-gate-trial.md) — and the
skill eval run ([skills/evals/EVAL_REPORT.md](../skills/evals/EVAL_REPORT.md) plus the five
files under `skills/evals/results/`), as consumed by
[release/PROMOTION_PACKETS.md](../release/PROMOTION_PACKETS.md).

**Method and what was independently re-executed.** All four sets, all five Wave E
handoffs, the packets, the three practice files, the schema, and R4's underlying
audit (`reviews/CLAIM_AUDIT.md`) were read in full. Q6 then re-executed what was
re-executable from the records: (a) the lab 003 checker was extracted from the
Lab's embedded source and run against this repository — its self-reported sha256
is byte-identical to the canonical v0.4 hash the Lab records
(`dabf8f38…c504c4705`), and at today's HEAD it reports 0 class-4 and 0 class-6
findings on a corpus that has drifted from 68 to 78 files, with the exception
self-check still passing and the unmasked sensitivity variant now producing 21
extra hits (3 at trial time); (b) lab 004's M1/M2 were re-run: 34 tests OK
(matches the record), repo-wide checker now reports 270 files / 597 link targets,
0 broken (the Lab's recorded 230/340 drifted exactly as its Limitations predict);
(c) the SOCIAL_KIT exception substrate was counted directly: 26 tokens, per-token
counts 12/4/4 and six 1s — matches the transcription; (d) commits `c2a10c0` and
`421ed6e` were verified in git (fix touches only the whitespace line; gated commit
stat matches the record).

**Reviewer bias, declared:** Q6 is itself an agent of the same model family
(`z-ai/glm-5.3-flash` per the eval report) as every producer below. Re-executions
above are independent runs but not independent operator classes. No human has
verified any of this either.

**What could not be verified by anyone:** the E2 checker run outputs, E3 fixtures,
and E4 eval outputs lived in `/tmp/opencode` and are ephemeral; run-window
timestamps and per-command outputs in all three Labs are self-reported
transcriptions. Everything below attacks the records as written.

---

## Verdict summary

| Evidence set | Adequate for a human promotion decision? | Narrowest defensible claim |
|---|---|---|
| Lab 002 (Practice 001 trial) | Yes-with-caveats | One self-run application: the assembler's own pack sufficed for the assembler to execute nine deterministic checks once and route one real failure to escalation, scoring 9/10 on its own checklist. |
| Lab 003 (Practice 002 trial) | Only for a narrower claim | A checker tuned on R4's corpus, encoding R4's own exception data, produced the same null result as R4's unverified null audit on one corpus at one commit — a one-sided consistency result, not a validation of either. |
| Lab 004 (Practice 003 trial) | Yes-with-caveats (for the hold decision only) | One agent executed the gate's check procedure once against one already-merged code commit and rehearsed a clean two-command revert; approval, refusal, and prevention were never exercised. |
| Eval report + results | Only for a narrower claim; cannot support any promotion | One model family followed its own skill instructions and judged its own outputs compliant in 45 self-graded cases — a smoke test of internal consistency, not behavioral evidence. |

---

## Cross-cutting findings (apply to all four sets)

- **C1 — One operator web, zero humans.** Every producer, executor, grader, and
  reference in all four sets is an AI worker of one model family, on one day, in
  one repository: E1 assembled and executed the pack it graded (labs/002:46); the
  E2 checker was written, run, revised, and compared by one worker against R4 —
  itself "a single AI-worker pass, not an independent human reference"
  (labs/003:39); E3 framed, ran, and wrote the gate record (labs/004:43); the
  eval model produced, routed, and graded all 45 cases (EVAL_REPORT.md:50). Each
  record discloses its own single-operator limitation. No record states the
  cross-record fact: there is no human execution, verification, or review
  anywhere in the evidence chain, and every "independent" element (the gate's
  producer/reviewer split, the R4 reference, the second task) is independence
  between tasks of the same swarm, not between operator classes.
- **C2 — Shared, concurrently mutating worktree during all trials.** The records
  themselves show the trials were not isolated: E1's post-run snapshot lists
  E4's untracked files (labs/002:128); E2's corpus absorbed E3's lab file
  mid-trial (labs/003:140,150); E3 recorded "parallel Wave E/G tasks land files
  continuously" (labs/004:43). Run windows overlap: E1 ran 17:06:26Z–17:13:32Z
  while E2's runs T1–T4 executed at ~17:09:00Z–17:13:30Z inside that same window.
- **C3 — Timestamp precision is not reconcilable across records.** E1's post-run
  status at ~17:13:32Z lists exactly three untracked entries and omits
  `labs/004-verification-gate-trial.md`, which lab 003 records as existing by T4
  (17:13:30Z) — two seconds earlier. Both cannot be exactly right. T1's timestamp
  is prefixed "~" (labs/003:137); lab 004 captured no per-command wall-clock
  timestamps at all (labs/004:135). All timestamps are self-reported.
- **C4 — Aggregation framing invites convergent-evidence reading.** Each Lab
  individually and honestly discloses its limits; the packet then presents three
  decision packets plus a "corroborating evidence" section each
  (PROMOTION_PACKETS.md:85,212,345), which invites a reader to treat three
  same-day, same-operator-class single runs plus a self-graded eval as
  independent lines of evidence. They are not independent: they share C1–C3.

---

## Set 1 — labs/002 (Practice 001 context-pack trial)

### Strongest claim and the honest version

Most overreaching sentence (labs/002:158, Interpretation): "the Practice's
method produced a usable pack on the first attempt for a well-specified,
command-backed recurring task, and its pre-declared acceptance checklist was
specific enough to score the output without improvisation."

Honest version: "the Practice's method produced a pack that its own assembler
found sufficient, on the first attempt, for one well-specified, command-backed
recurring task; whether anyone other than the assembler can use it is untested,
and the checklist's sufficiency was judged by its author."

("The pack caught and correctly routed a real committed-whitespace defect that
release validation alone does not surface" (labs/002:156) is well supported and
not attacked.)

### Circularity, self-grading, single-operator, timing

- **Self-grading beyond what the record discloses.** The Lab records that the
  rubric was "scored by the operator against the produced evidence summary"
  (labs/002:66) and that the run-level "supported" disposition was self-assigned
  (labs/002:145). What neither the Lab's Limitations nor Packet 1 surfaces: the
  pack's own acceptance-checklist section designates a different reviewer —
  "Reviewer: Practice release maintainer (human)" (labs/002:337) — so the run
  deviated from the pack's designated review role, and that deviation is
  unrecorded. The C3 "no secrets" spot-check was likewise performed by the
  interested operator.
- **Circularity.** Checklist author = executor = scorer. Mild by the standards
  of usability checks, but it means the 9/10 score measures agreement between an
  artifact and the rubric written alongside it by the same author.
- **Single-operator.** Assembler = executor; Practice 001's step-7 cold-reader
  check was self-administered. This is recorded (labs/002:165) and Packet 1
  surfaces it (PROMOTION_PACKETS.md:116-117) — fair.
- **Timing.** The 7-minute run window sat inside a shared worktree with E2's
  checker runs executing concurrently (C2, C3); the post-run snapshot's
  three-entry list cannot be reconciled with lab 003's T4 enumeration.

### Demonstration vs measurement / over-generalization

The whole trial is a demonstration of one successful self-run use. The rubric
itself disclaims accuracy/speed/cost measurement (labs/002:72), and the
non-result paragraph (labs/002:160) is well hedged. The over-generalization risk
is the word "usable": a reader takes "the Practice's method produced a usable
pack" as "context packs work" or "another Practitioner can use this pack."
Neither is supported.

### Verdict

**Yes-with-caveats.** The record genuinely meets the schema's `single-run`
minimum (context, method version, inputs, criteria, outcome, limitation), and it
is an unusually honest record. It is adequate to inform a human promotion
decision only if the human consciously accepts: (a) assembler = executor,
including the operator-scored checklist and self-administered step-7 check
against the pack's own designated human reviewer; (b) one command-backed task at
one commit. Narrowest defensible claim: "On 2026-09-01, a v0.1.0 pack assembled
per Practice 001 by the executing agent let that same agent execute nine
deterministic repository checks once, route one real failure to escalation, and
score 9/10 on its own predeclared checklist."

---

## Set 2 — labs/003 (Practice 002 workflow-redesign trial)

### Strongest claim and the honest version

Most overreaching presentation is in the packet, not the Lab:
"- 68/68 per-file agreement with R4's recorded verdicts for both mechanized
classes, in both included runs (T3 checker v0.3, T4 v0.4); 0 findings."
(PROMOTION_PACKETS.md:183-185). The Lab's own phrasing is bounded ("Observed:
… the checker reproduced R4's verdicts …" labs/003:167), but "agreement" invites
a validation reading.

Honest version: "in both included runs the checker reported zero findings,
matching R4's recorded zero findings on the 68 reference files. Every reference
verdict is 'clean', so the comparison can only show the checker does not
over-flag; it measures nothing about detection. The checker was revised twice
against this same corpus before the included runs."

### Circularity, self-grading, single-operator, timing

- **Circularity, partially disclosed.** The exception data was "transcribed from
  R4's prose" (labs/003:47) and R4 is "a single AI-worker pass, not an
  independent human reference" (labs/003:39); the Lab states the consequence
  plainly — "the checker can reproduce R4's blind spots, not just its
  conclusions" (labs/003:177). Packet 2 repeats it (PROMOTION_PACKETS.md:241-244).
  The undisclosed part: checker and reference are workers of the same swarm and
  model family, so "manual audit vs checker" is same-family agent vs same-family
  agent.
- **One-sided by construction.** The Lab says it outright: "Zero available by
  construction: R4 recorded no class-4 or class-6 findings, so this measure
  cannot distinguish 'checker perfect' from 'checker shares R4's blind spots'"
  (labs/003:37). This is the single most important sentence in the Lab and the
  packet's headline number (68/68) does not carry it.
- **Tuned on the scored corpus.** "Corpus reconnaissance informed the checker
  design before the formal runs" (labs/003:49), and the checker was revised
  twice (T1, T2 excluded) until it agreed — with the same 68 files it is scored
  on. The one file created outside the tuning corpus (`labs/004`, seen only at
  T4) is explicitly excluded from the agreement metric (labs/003:150), so the
  trial contains zero held-out evaluation. (The file was recorded clean on both
  classes — but one incidental clean file is not a held-out test.)
- **Self-grading.** The comparator, the exclusion decisions, and the "explained
  delta, not a mismatch" classification are all the author's own judgments.
- **Timing.** T1's timestamp is approximate; all four runs fall inside E1's run
  window in a shared worktree; the corpus changed 68 → 69 mid-trial.

### Demonstration vs measurement / over-generalization

"68/68 agreement" is a demonstration of null-consistency, not a measurement of
detection capability. "41.5 ms" is measured but baseline-less — no speed claim
is possible, and the Lab says so (labs/003:171). The sensitivity result
(masking is load-bearing) is a real measured observation and survives my
re-execution (21 extra hits unmasked at HEAD, up from 3 — the policy becomes
more load-bearing as prose-about-markers grows). Reader over-generalization
risks: "the claim audit is mechanized," "the checker is validated," "audits now
run in 41.5 ms."

### Q6 re-execution (credit where due)

The embedded checker's sha256 matches the Lab's canonical v0.4 hash exactly, and
the null result replicates at today's HEAD (0/0 findings, exception self-check
true, corpus 78 files). The reproduction claim — the strongest thing this Lab
offers — is real. It remains a same-family re-execution of a null result, so it
strengthens consistency, not correctness.

### Verdict

**Only for a narrower claim.** Not adequate to support promoting Practice 002:
the method's differentiating machinery (W5 AI-assisted triage, W6 human
checkpoint) was never executed, so a promotion would rest on the parts that are
ordinary scripting — the packet's hold recommendation is correct and the
evidence adequately supports that hold. Narrowest defensible claim: "A stdlib
checker, tuned on R4's corpus and encoding R4's own exception data, produced the
same null result as R4's unverified null audit, on one corpus at one commit,
after two revisions made against that corpus; this demonstrates encoding
consistency, not detection capability or correctness of either method."

---

## Set 3 — labs/004 (Practice 003 verification-gate trial)

### Strongest claim and the honest version

Most overreaching sentence is in the packet: "What was actually run: the full
Practice 003 gate (frame, baseline, checks, diff review, decision) applied end
to end to one real committed code change, plus a predeclared rollback rehearsal
against that commit." (PROMOTION_PACKETS.md:308-310).

Honest version: "the gate's framing, checks, diff review, and decision steps
were executed once on one code change that had already been merged before the
gate ran, plus a rollback rehearsal. The approval step was never executed
(`approval: null`), and because the artifact pre-landed, the gate could not have
prevented the merge — the trial documents the artifact and rehearses recovery
rather than demonstrating prevention."

In the Lab itself, "The checker passed every mandatory check for its intended
use" (labs/004:205) drops the qualifier that the mandatory set was self-framed.

### Circularity, self-grading, single-operator, timing

- **Self-framed criteria carry the decision.** The mandatory/advisory split
  (labs/004:74-84) was authored by the single operator before the checks ran —
  the right sequencing, but the load-bearing judgment (what is mandatory) has no
  second opinion. The boundary check is scored "pass, findings recorded"
  (labs/004:155): it passes by having been performed, not by the checker passing
  it. A reader skimming "all 6 mandatory checks passed … both advisory checks
  passed" can miss that the advisory pass encodes a demonstrated false-positive
  class that "in CI it would block a pull request containing a valid file named
  like `weird(1).md`" (labs/004:174).
- **Gate ran after merge.** Recorded honestly and centrally: "The gate therefore
  documented the artifact and rehearsed recovery; it could not prevent the
  effect" (labs/004:201). The gate's core function — prevention — is structurally
  untested in this flow; the Lab correctly calls for a flow decision, not a Lab.
- **Single-operator.** "One operator-agent framed the gate, ran the checks, and
  wrote this record; no independent reproducer has re-executed anything"
  (labs/004:43). The producer/reviewer split (E3 did not produce `421ed6e`) is
  real but is task-level, not operator-class, independence.
- **Timing/attribution.** No per-command timestamps (labs/004:135); repo-wide
  counts drift (recorded; confirmed — now 270/597); and one unverified
  attribution slipped into the record: "the earlier failure no longer reproduces
  and was evidently fixed by another task between the A-wave handoffs and this
  run" (labs/004:157) — "evidently" asserts a cause the record does not establish.

### Demonstration vs measurement / over-generalization

Everything here is demonstration; the Lab says so ("nothing here shows the gate
improves defect detection, review speed, or cost" labs/004:209). Boundary
fixtures demonstrate behavior classes, not incidence (labs/004:219). A2's checker
is not validated by this trial — a promotion of Practice 003 must not be read as
validating the gated tool, and the packet says exactly that
(PROMOTION_PACKETS.md:384-385). Over-generalization risks: "the gate works,"
"the checker passed review," "agent output in this repo is verified." My M1/M2
re-runs confirm the mechanical results replicate (34 tests OK; 0 broken links at
a drifted count) — the record's numbers are trustworthy as far as they go.

### Verdict

**Yes-with-caveats — but only for the hold decision.** The record is adequate to
support a human decision to hold Practice 003 at `proposed` (the packet's
recommendation), and inadequate to support promotion: the Practice's own trial
bar (two artifact types, refusal path) is unmet, and the Lab states it —
"Against the Practice's own trial bar: not fully met" (labs/004:211). Narrowest
defensible claim: "One agent executed the Practice 003 check procedure once
against one already-merged code commit, produced command-backed check results,
and rehearsed a clean two-command revert; approval, refusal, and prevention were
never exercised."

---

## Set 4 — skills/evals/EVAL_REPORT.md and results/*

### Strongest claim and the honest version

Most overreaching sentence (EVAL_REPORT.md:7): "All 45 defined cases (5 skills ×
9 cases) were executed for the GLM family and graded per criterion: 45/45 pass,
0 failed criteria, 0 forbidden-behavior violations."

Honest version: "All 45 defined cases were executed and graded by the producing
model itself, against criteria it could see while responding: 45/45 self-graded
pass. No pass in this report is independently auditable."

The report's own bold hedge immediately following ("These are single-family,
self-run, self-graded results… do not count toward `tested` maturity") and the
seven limitations are honest — the defect is the headline presenting
unauditable events as a clean count.

### Circularity, self-grading, single-operator, timing

- **Self-grading, strongest form, by the report's own words:** "one model
  followed its own skill instructions and graded its own outputs against
  criteria it could see while responding. Compliance-when-instructed is what
  was measured… A 45/45 sweep under this design is the expected outcome, not
  independent proof of quality" (EVAL_REPORT.md:50).
- **Circularity, doubled in one skill:** for review-practice-artifact, "the
  grader also authored the defects" (results/review-practice-artifact.md:35) —
  finding planted defects you planted yourself is near-tautological. For
  contribute-to-practice, "the fixture validator was written by the same model,
  so the validator pass is not an independent acceptance authority"
  (results/contribute-to-practice.md:45).
- **Routing and catalog bias:** indirect/negative activation was simulated by
  the model itself with full catalog knowledge (EVAL_REPORT.md:26,54,56) — the
  routing numbers measure nothing about a real host.
- **Evidence durability:** the durable record for 41 of 45 cases is "observed
  behavior summaries" self-written by the same model; the file artifacts "may
  not persist beyond this session" (EVAL_REPORT.md:55). No third party can audit
  any individual pass, and "0 forbidden-behavior violations" — the claim most
  sensitive to grader bias — is precisely the least auditable.
- **Timing:** single session, single day, same swarm that produced the trials;
  it cannot corroborate them (see W1).

### Demonstration vs measurement / over-generalization

"45/45 pass" is a self-attestation of compliance, not a measured behavioral
result. The one genuinely executed case (ctp-direct in a git fixture) is
undermined by the self-authored validator. Over-generalization risks: "the
skills pass their evals," "routing is accurate," "the model refuses unsafe
inputs under pressure." None is measured here.

### Verdict

**Only for a narrower claim; cannot support any promotion decision.** The evals'
own policy (`record-limitation-and-do-not-count-as-pass`) forbids counting these
toward promotion, and the report honors that in words while the headline still
leads with the count. Narrowest defensible claim: "One model family produced
responses following its own skill instructions and judged them compliant in 45
self-graded cases — a smoke test of internal consistency and instruction-following,
not behavioral evidence."

---

## What is already well-hedged (stated once, then dropped)

- labs/003:37 "Zero available by construction…" — unusually honest.
- labs/004:211 "Against the Practice's own trial bar: not fully met." — and
  Packet 3's hold recommendation is consistent with the evidence rather than
  against it.
- labs/002:160 and labs/003:171 non-result paragraphs (no accuracy/speed/cost
  claims).
- All five cost-capture sections record unmeasured cost as unavailable, not zero.
- Packet 2's circularity risk (PROMOTION_PACKETS.md:241-244) and Packet 1's
  independence risk (PROMOTION_PACKETS.md:116-117) state the two worst problems
  themselves.
- Packet 1's fix note is adequately evidenced: commit `c2a10c0` is authored
  under the repository owner's git identity (verified by Q6), so "closing that
  escalation" is defensible.

## Additional findings (below top-5 severity)

- Packet header dating (PROMOTION_PACKETS.md:6-8): "the only material change
  since the trials is the whitespace fix `c2a10c0`" — "material" is undefined;
  the commit range 6f205d6..1e22021 also contains the four Wave E evidence
  commits themselves. Verifiable, but only by a reader who runs git.
- Packet 1's pack identity rests on a sha256 *prefix* only (labs/002:45;
  PROMOTION_PACKETS.md:50-51) plus an asserted-verbatim Appendix A; the full
  hash and the frozen file are not in the repository.
- Packet 1 §2 "was the sole operating input" (PROMOTION_PACKETS.md:54) drops the
  Lab's qualifier "the run follows only the pack plus the repository sources it
  names" (labs/002:36) — the launch checklist that defines the nine checks is
  one of those sources.

---

## Top 5 findings (ranked by severity)

1. **No human anywhere in the evidence chain, presented as three decision
   packets plus corroboration.** Every producer, executor, grader, and reference
   is a same-family agent on one day; each record discloses its own
   single-operator limitation, but the packet's structure
   (PROMOTION_PACKETS.md:85,212,345 "Corroborating evidence"; consolidated
   recommendations :422-427) invites a convergent-independence reading the
   records do not support. The honest frame: three single-run demonstrations
   and one self-graded smoke test, all by one operator class — sufficient to
   sequence a human's review work, not to pre-answer it.
2. **Lab 003's "68/68 per-file agreement" (PROMOTION_PACKETS.md:183-185) is a
   one-sided, tuned-on-corpus result.** All 68 reference verdicts are "clean"
   (labs/003:105), missed findings are unavailable by construction
   (labs/003:37), the checker was revised twice against the same corpus before
   the included runs (labs/003:49,113-114), and the only file outside the tuning
   corpus is excluded from the agreement metric (labs/003:150). A reader will
   infer a validated checker; nothing about detection was measured.
3. **Lab 002's acceptance checklist was scored by the operator although the pack
   designates the human release maintainer as reviewer** — "Reviewer: Practice
   release maintainer (human)" (labs/002:337) vs "scored by the operator"
   (labs/002:66) — an unrecorded deviation that Packet 1's SC-2 "Met"
   (PROMOTION_PACKETS.md:100) inherits. Distinct from the step-7 issue the
   packet does surface: this is the C1–C10 scorecard itself.
4. **The gate trial demonstrates documentation and recovery, not the gate's
   function.** Artifact pre-landed (labs/004:201), approval never obtained,
   refusal path never exercised (labs/004:211), and "all 6 mandatory checks
   passed" (PROMOTION_PACKETS.md:314) rests on a mandatory set self-framed by
   the single operator (labs/004:74-84). Packet 3's wording "the full Practice
   003 gate … applied end to end" (PROMOTION_PACKETS.md:308-309) overstates
   what happened.
5. **The eval headline "45/45 pass, 0 failed criteria, 0 forbidden-behavior
   violations" (EVAL_REPORT.md:7) counts unauditable self-graded events** —
   criteria visible during production (EVAL_REPORT.md:50), grader = author, one
   grader also authored the defects it found
   (results/review-practice-artifact.md:35), artifacts ephemeral
   (EVAL_REPORT.md:55). Its reuse as "Corroborating evidence" in all three
   packets compounds the problem.

## Required wording changes before any human reads the promotion packets

For the Q-INTegrator or owner to apply (Q6 owns none of these files):

- **W1** — PROMOTION_PACKETS.md:85, 212, 345: replace the heading
  `### 3. Corroborating evidence` with `### 3. Related eval run (same operator
  class — not corroboration)`. In each section body, replace "the
  `build-context-pack` skill passed 9 of 9 cases" (and the two analogues) with
  "the `build-context-pack` skill self-graded 9 of 9 cases". Keep the existing
  "Treat as a smoke pass, not behavioral proof" sentences.
- **W2** — PROMOTION_PACKETS.md:183-185: replace
  "- 68/68 per-file agreement with R4's recorded verdicts for both mechanized
  classes, in both included runs (T3 checker v0.3, T4 v0.4); 0 findings." with
  "- In both included runs (T3 checker v0.3, T4 v0.4) the checker reported 0
  findings, matching R4's recorded clean verdicts on the 68 reference files.
  Every reference verdict is 'clean', so the comparison can only show the
  checker does not over-flag; it measures nothing about detection. The checker
  was revised twice against this same corpus before the included runs."
- **W3** — PROMOTION_PACKETS.md:53-55: replace "was the sole operating input for
  the nine launch-checklist §1 automated/repository checks" with "was the
  operating input for the run, together with the repository sources the pack
  itself names (the launch checklist §1 that defines the nine checks is source
  S1 of that pack)".
- **W4** — PROMOTION_PACKETS.md:308-310: replace the "What was actually run"
  sentence with: "What was actually run: the gate's framing, checks, diff
  review, and decision steps executed once on one code change that had already
  been merged before the gate ran, plus a predeclared rollback rehearsal. The
  approval step was never executed (`approval: null`), and because the artifact
  pre-landed, the gate could not have prevented the merge — the trial documents
  the artifact and rehearses recovery rather than demonstrating prevention."
- **W5** — PROMOTION_PACKETS.md:314: replace "- R1: all 6 mandatory checks
  passed" with "- R1: all 6 checks that the single operator had pre-framed as
  mandatory passed (the mandatory/advisory split was authored by the same agent
  that ran the checks)".
- **W6** — PROMOTION_PACKETS.md:424: replace the strength cell "Moderate–strong"
  with "Moderate (schema-minimum only; no independent-reader evidence)".
- **W7** — PROMOTION_PACKETS.md:6-8: replace "the only material change since the
  trials is the whitespace fix `c2a10c0`" with "the only commits between the
  trials' base and this packet's assembly are the four Wave E evidence records
  themselves and the whitespace fix `c2a10c0`".
- **W8** — skills/evals/EVAL_REPORT.md:7: replace "All 45 defined cases (5 skills
  × 9 cases) were executed for the GLM family and graded per criterion: 45/45
  pass, 0 failed criteria, 0 forbidden-behavior violations." with "All 45
  defined cases (5 skills × 9 cases) were executed for the GLM family and graded
  by the producing model itself, against criteria it could see while responding:
  45/45 self-graded pass. No pass in this report is independently auditable."
  Keep the existing bold hedge that follows.
- **W9** — labs/004-verification-gate-trial.md:157 (outside Q6's ownership; for
  the owner): replace "the earlier failure no longer reproduces and was
  evidently fixed by another task between the A-wave handoffs and this run" with
  "the earlier failure no longer reproduces as of this run; the cause and the
  fix are unverified".

## Evidence required for the strongest claims to stand

- **"Another Practitioner can use the pack unaided" (Practice 001):** an
  independent cold reader — a different operator class, ideally a human —
  executing the frozen pack without the assembler present, with friction
  recorded; at least one judgment-heavy task type; the v0.2.0 pack with the
  F1–F3 fixes; then two documented applications for `repeated`.
- **"Claim-audit classes 4/6 are mechanized" (Practice 002):** a human-verified
  reference containing planted positive findings (so the missed-finding rate
  becomes measurable), the corpus pinned by commit, the checker and exception
  data promoted into versioned repository tooling with tests, and agreement
  computed on files held out of the tuning process — plus W5/W6 executed with a
  named human reviewer.
- **"The gate prevents bad agent output" (Practice 003):** a gate executed
  before merge on at least two artifact types, with a planted mandatory failure
  that forces refusal and baseline preservation, a named human executing the
  approval step, and an independent reproducer re-running the record and
  countersigning — which also requires a swarm-flow change so gates precede
  merges.
- **"The skills pass their evals":** a second model family, blind routing
  without catalog narration, an independent (ideally human) grader, persisted
  artifacts, and the human severe-failure inspection the eval protocol already
  requires.
- **Cross-cutting:** at least one human-executed or human-verified link anywhere
  in the chain — even one countersigned rerun — would convert the entire body of
  evidence from self-consistent to externally anchored.

## Review limitations

Q6 did not re-execute E1's nine §1 commands end to end, did not re-run the eval
suite, and cannot inspect the ephemeral `/tmp/opencode` artifacts; run windows
and per-command outputs remain self-reported. The SOCIAL_KIT counts, the
`c2a10c0` and `421ed6e` commits, the embedded checker's identity and null
result, and lab 004's M1/M2 were verified or re-executed as described above.
