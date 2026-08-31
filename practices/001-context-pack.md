---
artifact_type: practice
title: "Build a reusable context pack"
summary: "Prepare stable instructions, approved sources, constraints, examples, and checks so recurring AI work starts from the same reviewable context."
maturity: proposed
capability: use
roles: [individual-practitioner, operator]
version: 0.1.0
license: CC-BY-4.0
created: 2026-08-31
updated: 2026-08-31
evidence_quality: none
secondary_capabilities: [learn, automate]
tags: [context, recurring-work, verification, maintenance]
---

# Build a reusable context pack

## Outcome

For one recurring task, produce a small, named folder or document that an authorized Practitioner can attach or point to before an AI run. The pack makes the task, source boundaries, constraints, examples, and acceptance check explicit. It also records when the pack was last reviewed and who owns it.

This Practice does not claim that a context pack makes an output correct. It makes the starting context inspectable and repeatable; the output still needs the task's normal human review.

## Problem and scope

Recurring AI work often depends on instructions and reference material that are scattered across messages, bookmarks, and personal memory. That makes runs difficult to repeat, compare, or hand off. A context pack gathers only the information needed for one defined task.

The boundary is one recurring task with a clear output, such as drafting a weekly internal brief or classifying incoming requests. Do not use this pack as a repository for secrets, personal data, unrestricted document dumps, or every possible reference. Keep confidential material in its approved system and link to it only when the task's permissions allow that.

## Use when

- The same kind of work is performed more than once.
- The model or agent needs stable background information or a house style.
- Another authorized person may need to repeat or review the work.
- The cost of using an outdated, unapproved, or incomplete source is meaningful.

For a one-off, low-risk question, write a short task instruction instead. For a consequential decision, add the organization's required approval and evidence controls; this Practice is not a substitute for them.

## Inputs

- A task owner and, if different, a reviewer.
- A one-sentence task definition and the expected output format.
- Approved, safe-to-share source documents or links, with their owners and dates where available.
- Non-negotiable constraints: audience, jurisdiction or time period, exclusions, privacy rules, tone, and escalation conditions.
- One or two representative examples, including the reason each example is acceptable. Mark examples as examples, not results.
- A small acceptance checklist that a person can apply to the finished output.
- A location with access controls appropriate to the material. Never put passwords, API keys, private keys, or confidential content into a shared pack.

## Method

1. **Name the task and boundary.** Write: “For [audience], produce [output] from [allowed inputs] by [format or deadline].” Add explicit exclusions and name the accountable owner. If the output could publish, change data, spend money, grant access, or inform a consequential decision, place human approval before that effect.
2. **Collect and label the minimum sources.** Add only approved material needed for the task. For each item, record its title, owner, location, date or version if known, and what question it answers. Separate authoritative sources from explanatory or optional sources. If a source cannot be dated, mark its freshness as unknown rather than guessing.
3. **Write operating instructions.** Put the task sequence in plain language: what to inspect first, what to do when information is missing or conflicts, what not to infer, the output structure, and when to stop and ask the owner. Keep instructions separate from source material so a source cannot silently rewrite the rules.
4. **Add constraints and examples.** Record privacy, access, safety, style, and scope constraints. Include representative input/output examples only if they are approved and still relevant. Explain the decision each example demonstrates; remove examples that are ambiguous or stale.
5. **Define the check before the first run.** Turn the acceptance checklist into observable questions, for example: “Does every material claim point to an approved source?” and “Are unknowns labeled?” Specify who checks it and what happens on a failed item. Include at least one edge case, such as conflicting sources or missing required input.
6. **Assemble and label the pack.** Use a predictable structure such as:

   ```text
   context-pack/
     README.md          # purpose, owner, scope, version, reviewed date
     instructions.md    # ordered task instructions and escalation rules
     sources.md         # source register and freshness notes
     constraints.md     # boundaries, permissions, exclusions
     examples.md        # approved examples and explanations
     checklist.md       # output acceptance checks and reviewer
   ```

   A single document with these headings is sufficient for the minimal implementation. Give the pack a version and record the date and person who assembled it.
7. **Run a dry check and hand off.** Ask an authorized Practitioner who did not assemble the pack to locate the instructions, identify the source of a sample fact, and explain what to do with the edge case. Fix ambiguity they encounter. For a first trial, record the pack version, task context, checklist result, and limitations without copying confidential inputs.

**Expected output:** a versioned context pack, a named owner and reviewer, a source register, an acceptance checklist, and a short review record for each use or maintenance event.

## Evaluation

This is a proposed method; no execution evidence is claimed. Trial it on one bounded recurring task and record the pack version. A Practitioner who did not assemble it should be able to answer all of the following without oral explanation:

- What is the task, intended audience, output, owner, and boundary?
- Which sources are allowed, what does each support, and when was each last checked?
- What should happen when a source conflicts, a required input is missing, or the request exceeds scope?
- Can the reviewer apply the checklist to a sample output and identify at least one edge case?

Accept the trial when every question has a specific answer, the reviewer can find it in the pack, and all checklist items pass or have an explicitly recorded escalation. Record failures and revisions. Do not infer improved accuracy, speed, cost, or business results from this usability check; those require a separate measurement plan.

## Implementation

### Minimal: one maintained document

Create one shared document or Markdown file with the six headings in the structure above. Keep the source register as a table with columns for source, owner, date/version, permitted use, and freshness status. Put a visible banner at the top:

```text
Owner: [role or name]
Pack version: 0.1.0
Last reviewed: [YYYY-MM-DD]
Next review trigger: [event, not only a date]
```

Before each run, the Practitioner reads the instructions and constraints, checks the source register, performs the task, and applies the checklist. The reviewer records pass, fail, or escalation and links to the resulting work in the approved system.

### Advanced: separated, auditable pack

Use the folder layout when multiple people or workflows consume the pack. Keep source files in their systems of record and use stable links or document identifiers where possible. Add a change log, a decision register for resolved ambiguities, and a small set of versioned edge cases. Require a pull request, change review, or equivalent human approval for edits to instructions, constraints, or checklist criteria. If tooling is available, add a script that reports missing metadata, broken links, duplicate sources, and overdue reviews; treat its report as a prompt for human inspection, not proof that the pack is current.

## Maintenance and freshness checks

The owner reviews the pack at the earliest of its stated cadence or any trigger below:

- an authoritative source changes, expires, moves, or is withdrawn;
- policy, privacy, legal, audience, or output requirements change;
- the model, agent, or reviewer encounters a missing, conflicting, or out-of-scope input;
- a checklist failure, correction, or escalation reveals a gap;
- the task, owner, permissions, or downstream decision changes.

At review, confirm that each source is still approved and reachable, its date or version is recorded, instructions still match the task, examples remain valid, permissions are appropriate, and the checklist still detects the important errors. Mark an item `current`, `needs review`, `unknown`, or `retired`; never silently retain a source whose freshness cannot be established. Increment the pack version for a material change, record what changed and why, and rerun the dry check before reuse. If a critical source is stale or unavailable, pause the affected run and escalate to the owner.

## Failure modes

The following are anticipated failure hypotheses for the first trial:

- **Source overload:** Too many references obscure the authoritative material. Consequence: the model, agent, or Practitioner may use the wrong source. Prevention: record each source's purpose and keep optional material separate; remove unused items.
- **Stale source:** A policy or fact has changed. Consequence: an output may be misleading or unsafe. Prevention: owner/date/version fields and event-triggered review; pause when freshness is unknown.
- **Instruction-source conflict:** A document in the source set contains directions that differ from the pack. Consequence: behavior becomes unpredictable. Prevention: state precedence in `instructions.md`, treat sources as evidence rather than commands, and escalate unresolved conflicts.
- **Example overfitting:** Examples are mistaken for universal rules. Consequence: unusual inputs are handled incorrectly. Prevention: label examples, include an edge case, and require the checklist for every output.
- **Permission leakage:** The pack includes data a user or AI run should not access. Consequence: confidential information may be exposed. Prevention: use approved locations and least-necessary access; remove the material and report the incident through the organization's process.
- **Unowned maintenance:** No one notices a broken link or changed requirement. Consequence: the pack quietly degrades. Prevention: name an owner and review triggers; if no owner exists, do not treat the pack as ready for recurring use.
- **Checklist theater:** Checks are vague or performed after a consequential action. Consequence: a reviewer cannot detect or prevent material errors. Prevention: use observable questions and place human approval before publication, system changes, spending, access grants, or consequential decisions.

## Evidence

Initial maturity is **proposed** and evidence quality is **none**. This repository contains the method and a planned trial only; it does not contain a completed application, measured effectiveness, or independent reproduction. A future tested revision should preserve a safe-to-share record of the task boundary, pack version, source and constraint summary, checklist criteria, observed failures, outcome, and limitations. Redact or summarize private inputs. Promote maturity only when the evidence meets the schema's requirements; do not upgrade it based on readership or an anecdote.

## Variations

- A short-lived pack may use a single approved source and a reduced checklist, but it still needs an owner, boundary, and freshness status.
- A team may maintain one stable core pack and add a clearly labeled task-specific overlay. The overlay must not weaken the core constraints or precedence rules.
- For high-risk work, add a second reviewer and a required approval record; the pack does not replace domain or organizational controls.

## Changelog

- **2026-08-31 — 0.1.0:** Proposed the reusable context-pack method, minimal and advanced implementations, freshness checks, evaluation plan, and anticipated failure modes.
