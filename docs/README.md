# How Practice thinks

This directory holds what Practice is, what it believes, what it has decided, and what it requires of every artifact. Open it for the reasoning behind a rule.

Not here: how people join, contribute, get credit, and are governed is in [community/](../community/); runbooks are in [ops/](../ops/); the status of every launch decision is in [release/OWNER_REVIEW.md](../release/OWNER_REVIEW.md).

## Charter

| File | What it holds | When to open it |
|---|---|---|
| [CONTEXT.md](CONTEXT.md) | Canonical context: product, positioning, ethos, mission, north star, audience, the capability ladder, the six artifact types, and the six proposed method candidates | Before describing Practice anywhere |
| [DECISIONS.md](DECISIONS.md) | Locked decisions that agents treat as settled: name, positioning, hub, source of truth, licenses, agent security, moderation, and unattended-action posture | When a choice looks open and you want to know whether it is |
| [NON_GOALS.md](NON_GOALS.md) | What the first release must not become: a platform, an LMS, a certification, a paid membership, a prompt library, autonomous moderation, and more | Before proposing new scope |
| [QUALITY_BAR.md](QUALITY_BAR.md) | What every merged artifact must satisfy: useful, reproducible, honest, current where it matters, model-agnostic, concise, accessible, safe to publish, reviewable | Before writing, reviewing, or merging any artifact |
| [OWNER_GATES.md](OWNER_GATES.md) | The decisions reserved to the owner, the default the swarm uses for each, and the manual actions never delegated | To learn which decisions an agent may not make |
| [ARCHITECTURE.md](ARCHITECTURE.md) | The four surfaces (Buzz, Git, Social, terminal swarm), the source-of-truth rules between them, and a short note on the repository layout | When deciding where an artifact or a conversation belongs |

OWNER_GATES.md lists gates and their defaults. It is not a status page. The status of each gate and each operating hold lives in [release/OWNER_REVIEW.md](../release/OWNER_REVIEW.md), where a row stays OPEN until a human records approval with evidence.

## Subdirectories

| Directory | What it holds | When to open it |
|---|---|---|
| [founding/](founding/) | [MANIFESTO.md](founding/MANIFESTO.md): what Practice believes, starting from the implementation gap between a fast answer and work that improved.<br>[FOUNDING_BRIEF.md](founding/FOUNDING_BRIEF.md): the idea, mission, north star, what Practice is and is not, and its long-term direction.<br>[FOUNDING_STORY.md](founding/FOUNDING_STORY.md): a first-person account of the work after the first answer and why Practice is being built for it.<br>[COMMUNITY_LANDSCAPE.md](founding/COMMUNITY_LANDSCAPE.md): a sourced scan of adjacent communities as of 2026-09-01; its gap statements are labeled analysis, not fact | To understand why Practice exists and how it is positioned |
| [framework/](framework/) | [CAPABILITY_LADDER.md](framework/CAPABILITY_LADDER.md): Learn → Use → Automate → Build → Transform, what each level demonstrates, and the classification rules.<br>[TAXONOMY.md](framework/TAXONOMY.md): how to choose one primary artifact type, resolve ambiguities, and apply capability and role tags.<br>[AUTONOMY_LADDER.md](framework/AUTONOMY_LADDER.md): A0 observe, A1 draft, A2 recommend, A3 act-unattended-within-bounds, the operations permanently ineligible for A3, and the current level of every agent and cadence operation | To classify an artifact, a contribution, or an agent operation |
| [schemas/](schemas/) | One schema per artifact type: [PRACTICE](schemas/PRACTICE_SCHEMA.md), [GUIDE](schemas/GUIDE_SCHEMA.md), [LAB](schemas/LAB_SCHEMA.md), [STORY](schemas/STORY_SCHEMA.md), [NOTE](schemas/NOTE_SCHEMA.md), [PROJECT](schemas/PROJECT_SCHEMA.md).<br>Two record schemas: [AGENT_PACKET](schemas/AGENT_PACKET_SCHEMA.md), the bounded packet every community agent returns before stopping at human review; [ACTION_LEDGER](schemas/ACTION_LEDGER_SCHEMA.md), the entry one unattended run would write, which is a record and never an authorization | Before drafting or validating any artifact or record |
| [style/](style/) | [VOICE.md](style/VOICE.md): the voice attributes, information order, headline, description, and call-to-action patterns, and the evidence rules.<br>[LEXICON.md](style/LEXICON.md): the canonical terms Practitioner, Practice, Guide, Lab, Story, Note, and Project, the capability ladder, and the discouraged language with its replacements | Before writing any public artifact, message, or repository document |

## Read in this order if you are new

1. [MANIFESTO](founding/MANIFESTO.md) → [CONTEXT](CONTEXT.md) → [DECISIONS](DECISIONS.md) → [NON_GOALS](NON_GOALS.md) → [QUALITY_BAR](QUALITY_BAR.md).
2. Then the schema and the two style files for whatever you are about to write.

## Rules that apply here

- Agents treat DECISIONS.md as settled unless OWNER_GATES.md explicitly reopens an item.
- An attractive idea that falls under NON_GOALS.md is recorded under Deferred opportunities in a handoff, not implemented.
- The six artifact schemas and the agent packet schema each name a blank template in [templates/](../templates/); write from the template, then check against the schema. Ledger entries are written by `scripts/ledger.py`, not from a template.
- Practice is pre-launch. All six method candidates carry `maturity: proposed`, and the autonomy ladder places nothing at A3.
