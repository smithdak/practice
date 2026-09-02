# Adversarial editorial and coherence review

**As of:** 2026-09-01 (currency re-stamp added at Phase 2 integration; the
review itself was recorded 2026-08-31 against the pre-Phase-2 tree).

## Outcome

**Not ready for publication.** The reviewed corpus is careful about evidence,
human ownership, and vendor neutrality, but three contradictions would mislead a
reader at launch:

1. unevidenced proposed methods are presented as canonical **Practices** even
   though the canonical lexicon reserves that name for reusable, tested methods;
2. launch content presents **Share** and **Improve** as capability stages even
   though the locked ladder has only Learn → Use → Automate → Build → Transform;
3. the Guide still tells readers that files now present in the repository are
   planned, unpublished, or unavailable.

These are publication blockers, not blockers to completing this review. The
remaining findings are ranked improvements. The strongest editorial qualities
should be preserved: examples are labeled, claims are bounded, consequential
effects retain human ownership, and no vendor or model is made a requirement.

## Scope and review lenses

The primary corpus was the 13 outputs owned by Q002's dependencies:

- `docs/founding/MANIFESTO.md`
- `guides/ai-native-practitioner/01-foundations.md` through
  `06-organizational-ai.md`
- `practices/001-context-pack.md` through
  `003-verification-gate.md`
- `docs/founding/FOUNDING_STORY.md`
- `ops/outreach/LAUNCH_VIDEO.md`
- `ops/outreach/FIRST_10.md`

Together these files contain 34,625 words. The linked Guide entry point and
curriculum map were also checked where a reviewed module directs readers to
them. Findings were tested against `docs/CONTEXT.md`, `docs/DECISIONS.md`,
`docs/QUALITY_BAR.md`, `docs/style/VOICE.md`, and `docs/style/LEXICON.md`.

Two adversarial readings were used:

- **Skeptical expert:** Does the evidence support the artifact name and claim?
  Is there one controlling rule? Can an exception silently broaden authority?
- **Capable beginner:** Can a reader identify what to do now, which record is
  authoritative, how much work is required, and where one module ends?

Severity means:

- **Blocker:** creates a direct conflict with canonical language or gives a
  false publication-state signal.
- **Major:** materially harms coherence, maintainability, or completion.
- **Improvement:** the artifact remains usable, but deletion or clarification
  would make it more precise.

## Release blockers

### 1. Proposed methods do not meet the canonical threshold for a Practice

**Conflict.** `docs/style/LEXICON.md:24-37` defines a Practice as “a reusable,
tested method” and directs untested work to a Note. `docs/CONTEXT.md:47-54` repeats
the tested-method definition. Yet all three flagship files declare
`maturity: proposed` and `evidence_quality: none`:

- `practices/001-context-pack.md:5-12` and `:128-130` say there is no completed
  application, measured effectiveness, or independent reproduction.
- `practices/002-workflow-redesign.md:5-12` and `:141-143` say there is no
  completed redesign or measured outcome.
- `practices/003-verification-gate.md:5-12` and `:161-163` say there is no
  completed trial, measured effectiveness, or independent reproduction.

The launch layer then removes even the proposed qualifier.
`docs/founding/FOUNDING_STORY.md:34-41` defines a Practice as a tested method,
and `:67-69` calls these three files “canonical methods.”
`ops/outreach/LAUNCH_VIDEO.md:60-62` likewise presents “the three canonical
Practices.” A skeptical expert receives two incompatible maturity claims; a
beginner is told to trust an artifact category the same artifact says it has
not earned.

**Required action.** Preserve the evidence threshold. Until a method has a
recorded trial and review, remove public claims that it is a canonical Practice
and label it as a proposed method or Note. Alternatively, supply the missing
trial evidence and make an explicit promotion decision. Do not solve the
conflict by deleting the `evidence_quality: none` disclosure or weakening it in
launch copy. Because `docs/CONTEXT.md:60-64` also names the “First three Practices,”
the owner or final integrator must reconcile the canonical naming before
release rather than changing one downstream label in isolation.

### 2. Launch content creates capability stages outside the locked ladder

**Conflict.** `docs/DECISIONS.md:15` locks the information architecture to Learn →
Use → Automate → Build → Transform. `docs/style/LEXICON.md:80-92` says not to add or
rename stages. In `ops/outreach/FIRST_10.md:26-37`, however, a column labeled
“Capability move” uses `Share / applicable capability` for item 9 and `Improve`
for item 10. Those are contribution actions, not capability stages.

`docs/founding/MANIFESTO.md:19-25` adds a second progression—Learn → Apply →
Measure → Share → Improve—immediately before introducing the actual capability
stages. That cycle comes from the founding brief, but calling both constructs a
progression leaves readers with two competing maps. The manifesto also makes
`Apply` visually resemble a replacement for **Use**, while **Share** and
**Improve** reappear as apparent capabilities in `FIRST_10.md`.

**Required action.** Delete the noncanonical values from the “Capability move”
column and use only the five controlled stages, or delete that column where an
item's capability varies by resulting artifact. In the manifesto, delete the
second arrow sequence or name it unambiguously as a contribution cycle rather
than a capability progression. Do not add stages to the locked ladder.

### 3. The Guide reports shipped dependencies as planned or unavailable

**Conflict.** Every linked module and all three linked methods exist, but the
reader repeatedly receives old construction-state language:

- `guides/ai-native-practitioner/02-effective-use.md:337-339` calls Module 3
  planned.
- `guides/ai-native-practitioner/03-context-engineering.md:217-220` says the
  linked Context Pack Practice is not yet published, and `:284-286` calls
  Module 4 planned.
- `guides/ai-native-practitioner/05-agentic-engineering.md:65-75` says the
  linked Verification Gate is planned and not yet published.
- `guides/ai-native-practitioner/06-organizational-ai.md:3-5` says the named
  Practices may be applied “when published.”

The Guide entry point compounds this problem. Although every module links to
it, `guides/ai-native-practitioner/README.md:77-83` says the full module set is
still being authored; `:89-155` labels existing Practices and every existing
module as planned. The curriculum map has the same stale scaffold premise at
`guides/ai-native-practitioner/CURRICULUM.md:7-14` and, for example,
`:196-198`.

**Required action.** Search the full Guide for construction-state terms and
delete `planned`, `until it exists`, `once available`, and `when published`
where the target exists. Turn module filenames into direct links. Keep maturity
language about evidence, but do not confuse evidence maturity with file
availability. This needs one systematic edit; fixing only the five passages
above would leave the entry point contradictory.

## Major findings

### 4. The Guide duplicates the canonical methods instead of sequencing them

`docs/style/LEXICON.md:39-46` says a Guide combines multiple Practices and explains
sequence and tradeoffs. In the current corpus, the Guide frequently republishes
the methods as parallel sources:

- `guides/ai-native-practitioner/03-context-engineering.md:217-274` supplies a
  complete Context Pack scaffold and checklist, overlapping
  `practices/001-context-pack.md:50-126`.
- `guides/ai-native-practitioner/04-automation-agents.md:20-116` and `:250-301`
  repeat workflow mapping, classification, approval, rollback, evaluation, and
  a dossier already covered by `practices/002-workflow-redesign.md:47-139`.
- `guides/ai-native-practitioner/05-agentic-engineering.md:65-77` embeds a local
  verification gate even though `practices/003-verification-gate.md:50-99`
  defines the canonical gate.

The stale publication labels are already evidence of the maintenance failure
this duplication creates. A skeptical expert cannot know whether the module
scaffold or Practice controls when wording diverges. A beginner is asked to
complete near-duplicate records under different names.

**Action.** After resolving Finding 1, delete duplicated method and checklist
text from the modules. Keep the concepts, prerequisite, sequencing decision,
and module-specific application; link to one canonical method for the actual
worksheet and gate. Where a module genuinely requires a different check, name
the delta rather than restating the entire method.

### 5. The cumulative Guide path is form-heavy but lacks one completed throughline

The six modules contain 37 numbered exercises and six separate capstones. The
artifact load begins with four records in
`guides/ai-native-practitioner/01-foundations.md:7-16`, adds six in
`02-effective-use.md:9-20`, and adds five more in
`03-context-engineering.md:9-19`. Later modules introduce a deterministic run
contract, agent boundary record, workflow dossier, implementation brief,
verification matrix, handoff, opportunity map, governance record, measurement
ledger, and pilot operating model.

Most examples demonstrate one paragraph, one row, or a hypothetical rule. None
shows a single safe task carried through the accumulated records so the reader
can see what is reused, replaced, or discarded. The curriculum map says to
“Keep one capstone dossier” (`guides/ai-native-practitioner/CURRICULUM.md:7-12`),
but each module presents another standalone capstone template. This is a
completion problem for the beginner and a governance-document burden for the
expert.

**Action.** Delete duplicate fields and make each module update one cumulative
record. Mark fields as carried forward, revised, or new. Prefer one compact,
filled example that grows across modules over more blank templates; if no
observed example is available, label the throughline hypothetical and keep it
short. Do not add a seventh summary document.

### 6. The Verification Gate permits and forbids an unknown mandatory check

`practices/003-verification-gate.md:52-60` says acceptance is allowed when
unknowns are “resolved or explicitly authorized,” while a failed or missing
mandatory check requires `revise` or `reject`. The same file says at `:89` that
inability to perform a required check means the status is not `accept`, and at
`:91-93` that human approval is mandatory when a mandatory check is unknown.
The machine-readable example correctly refuses acceptance for an unknown at
`:124-149`.

“Explicitly authorized” is undefined. A hurried reviewer could read it as
permission to approve past the gate, while the rest of the method says the gate
must refuse. This ambiguity is most dangerous exactly where the Practice is
supposed to remove completion theater.

**Action.** Delete “or explicitly authorized” from the acceptance rule. If an
exception process is required by an external policy, record the outcome as a
separate exception or escalation—not as the gate passing. Use one rollback
standard as well: align `available` at `:58` with `tested or clearly executable`
at `:73`.

### 7. The launch story largely restates the manifesto

The launch story's first-person opening is useful, but most subsequent sections
repeat the manifesto's structure and claims:

- implementation gap: `docs/founding/MANIFESTO.md:3-13` and
  `docs/founding/FOUNDING_STORY.md:3-12`;
- artifact taxonomy: manifesto `:33-41` and story `:32-43`;
- openness and human-agent roles: manifesto `:53-69` and story `:45-61`;
- one-task invitation: manifesto `:83-91` and story `:65-71`.

The video then repeats the launch story's claim/evidence formulation, Git/Buzz
division, and invitation at `ops/outreach/LAUNCH_VIDEO.md:54-62` and `:102-108`.
This is coherent but not additive. Repetition makes the launch corpus feel like
one thesis expanded across surfaces rather than each surface doing a distinct
job.

**Action.** Delete the taxonomy recap and one of the openness/human-agent
sections from the launch story; link to the manifesto or Guide for detail. In
the video, let the shown diff, check, and handoff carry the explanation and cut
voiceover that merely restates the page. Keep the fixed positioning and one
invitation.

## Ranked improvements

### 8. Repeated safety framing obscures the lesson specific to each module

This is repetition, not a safety objection. The same authority, data,
consequence, human-review, stop, and rollback cautions recur in almost every
module and Practice. Compare:

- `guides/ai-native-practitioner/01-foundations.md:145-171`;
- `guides/ai-native-practitioner/02-effective-use.md:41-60`;
- `guides/ai-native-practitioner/03-context-engineering.md:149-177`;
- `guides/ai-native-practitioner/04-automation-agents.md:165-208`;
- `practices/001-context-pack.md:25-48`;
- `practices/002-workflow-redesign.md:74-107`.

The repetition is precise, but it delays the distinct subject and makes later
controls harder to spot.

**Action.** Keep one shared minimum safety boundary in the Guide entry point or
cumulative record. In each module, delete the generic restatement and retain
only the new control introduced there: input handling in Foundations, delegated
effect in Effective Use, memory/retrieval in Context Engineering, and
state/rollback in Automation and Agents.

### 9. Record names multiply without a crosswalk

The corpus introduces task card, task-and-risk brief, task brief, run packet,
reviewed task record, source register, context pack, boundary record, run
contract, workflow dossier, implementation brief, verification matrix, gate
record, handoff, opportunity map, governance record, measurement ledger, and
pilot operating model. Each term is locally understandable, but the cumulative
relationship is not.

For example, Module 1's task card at
`guides/ai-native-practitioner/01-foundations.md:28-44` is followed by Module
2's task brief at `02-effective-use.md:64-96`, even though many fields repeat.
Module 4's workflow dossier at `04-automation-agents.md:250-301` overlaps the
workflow map and experiment card in `practices/002-workflow-redesign.md:47-117`.

**Action.** Delete synonyms for records that serve the same decision. Choose
one cumulative dossier vocabulary and state which canonical method owns each
section. Add no new artifact name.

### 10. The first ten briefs sometimes describe participation as the artifact

The release rule in `ops/outreach/FIRST_10.md:11-22` requires a canonical Git
artifact to be opened or improved. The sequence table at `:26-37` nevertheless
lists “Guide worksheet completion” as a contribution for items 1, 7, and 8,
and Brief 1 permits a “documented completion” at `:60-63`. Completing a
worksheet may produce useful private work, but it does not necessarily create
or improve a durable public artifact.

**Action.** Delete worksheet completion as a publication-sufficient artifact.
Require a safe-to-share Note, Guide correction, or other actual Git change;
when the work cannot be shared safely, keep the session private or do not
publish it as a flagship contribution. This uses artifact types already in the
founding brief and does not add a new content format.

### 11. “AI” is occasionally used where the actor should be more precise

The corpus usually follows the lexicon well, but a few passages regress to an
umbrella actor. `practices/001-context-pack.md:33-36` says “The AI needs stable
background information,” and `:120-124` says “the AI or Practitioner may use
the wrong source.” `guides/ai-native-practitioner/06-organizational-ai.md:94-98`
opens “AI-assisted work” before naming the actual workflow, sources, and
reviewers.

**Action.** Delete “the AI” and name the model, agent, retrieval step, or
workflow behavior. Do this only where the actor is known; do not mechanically
replace every ordinary use of AI.

## Voice and evidence checks that pass

- **No material generic hype found.** The corpus avoids the lexicon's banned
  superlatives, vendor evangelism, market statistics, and autonomous-agent
  spectacle. `ops/outreach/LAUNCH_VIDEO.md:93-100` explicitly excludes them.
- **Examples are honestly labeled.** The reviewed Practices and modules
  distinguish hypothetical or proposed work from observed evidence.
- **Current technical claims are avoided.** The corpus mostly uses enduring
  concepts and does not depend on unstable model limits or product interfaces.
- **Human ownership is explicit.** Consequential publication, spending, access,
  system changes, and decisions consistently receive named review boundaries.
- **Operational guidance is not absent.** The central weakness is excess and
  duplication: too many records and repeated controls obscure which method is
  canonical and what the reader should complete next.

## Recommended correction order

1. Resolve Practice maturity versus canonical naming.
2. Restore the locked capability vocabulary.
3. Remove stale planned/unpublished state across the full Guide.
4. Choose one source of truth for each method and gate.
5. Collapse the Guide into one cumulative dossier and remove duplicated fields.
6. Reconcile the Verification Gate's unknown-check rule.
7. Cut repeated launch and safety framing.
8. Run a fresh editorial pass from the Guide entry point and one flagship brief
   before release.
