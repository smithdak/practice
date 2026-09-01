# Onboarding dry run V2 — Phase 2 persona simulation

**As of:** 2026-09-01 — repository at commit `1f80f96` at review start; the
integration fixes for this review's findings are recorded in
[FINAL_INTEGRATION_REPORT_V2.md](../release/FINAL_INTEGRATION_REPORT_V2.md).

## Outcome

**Conditional yes for private beta; no for public invitation promotion.** All
three simulated personas can still complete a safe, self-directed first
contribution in Git, and the post-entry Buzz route remains desk-complete. The
Phase 2 additions did not break the entry path, but they left one major gap:
the new intake/consent route for real Stories (G4) is not reachable from any
surface a newcomer would actually use, so a Practitioner arriving with a real
implementation would file client or personal details straight into a public
issue template. Two smaller Phase 2 regressions — a stale "three Practices"
copy set and a contribution quickstart that no longer covers the artifact
taxonomy — are cheap to fix before a private beta opens.

All persona reactions below are **simulation by a reviewer working from the
repository text**, not user research. No person was recruited, no hosted Buzz
surface was accessed, and no claim about real newcomer behavior is made.

## Scope, baseline, and method

- **Artifact/version:** repository at commit
  `1f80f967baeb68ee4bef82111b3943fd5dc5c5e0` (post-Wave A/E/G, mid-Wave O;
  parallel O-task outputs present but uncommitted were read only where the
  entry path references them).
- **Intended effect:** move a new Practitioner from public discovery
  (README → contributor quickstart → onboarding → `start-here` canvas) to a
  bounded first contribution, now including the Phase 2 artifacts
  (practices 004–006, Note/Project schemas and templates, intake/consent and
  redaction templates, refreshed guide entry point).
- **Impact:** material. A misrouted first contribution can put confidential
  material into a public issue; a stranded persona becomes a lost member.
- **Owner and approval:** humans own invitations, membership, promotion, and
  publication. This review approves nothing external.
- **Evidence boundary:** repository text only. No hosted relay, invitation,
  account, agent, or message was accessed, and no external execution is
  claimed.

Status codes in the persona tables:

- **PASS (repo):** the repository supplies a concrete, safe, findable next
  instruction from the current step.
- **PASS (friction):** the next instruction exists but is not linked from the
  artifact the persona is reading; success requires guessing or browsing.
- **STALL:** the persona cannot determine a safe next action from the artifact
  at that step.
- **FAIL (live):** the required external precondition (invitation, hosted
  community) is absent; a verification failure does not assert the untested
  hosted behavior is broken.

Method: each persona walks the entry path step by step; at the first-contribution
step the persona is explicitly tested against
[the Knowledge Taxonomy](../docs/framework/TAXONOMY.md) and the new Phase 2
schemas/templates. The walk starts at the repository root README, which the
first dry run did not cover; scope-expansion findings are labeled as new.

## Persona simulations

### 1. Nia — nontechnical operations coordinator

**Simulated need (hypothetical):** produce a safe, source-grounded weekly
meeting brief from approved notes; she can describe the task without sharing
the notes.

| Step | Result | What happens and the exact gap |
| --- | --- | --- |
| README | STALL | `README.md:1` presents the repository as "Practice — Swarm Build Kit" and `README.md:3` as "the executable build plan for **Practice**". Steps `README.md:11-39` (init.sh, Director mode, taskctl worktrees) are swarm-operator instructions. `README.md:41-51` lists only operator documents. There is no link to `CONTRIBUTING.md`, `community/`, or any "I want to join/participate" pointer. Nia's only move is browsing the file tree and guessing that `CONTRIBUTING.md` or `community/ONBOARDING.md` is for her. |
| Contributor quickstart | PASS (friction) | `community/CONTRIBUTOR_QUICKSTART.md:3-7` reads correctly for her. The "Choose a path" list at `CONTRIBUTOR_QUICKSTART.md:10` offers "Correction or Note" and correctly matches her situation ("preserve a bounded observation"). Gap: the Note bullet links no template or schema — unlike the Practice, Lab, and Project bullets, which each link their template or form — so she never learns `templates/NOTE.md` and `docs/schemas/NOTE_SCHEMA.md` exist. |
| Onboarding | PASS (repo); FAIL (live) | `community/ONBOARDING.md:9-16` assumes Buzz membership; without an invitation she cannot execute stage 1. The failure-modes row `ONBOARDING.md:93` correctly sends her to "the public Git contribution path" — but that row links nothing, so she is back to guessing the quickstart exists. The Buzz-side first post (`ONBOARDING.md:24`) is desk-draftable and safe. |
| `start-here` canvas | PASS (repo); FAIL (live) | `buzz/canvases/start-here.md:21-28` gives her a four-line post and a hypothetical operations example (`:30-35`). She cannot post without membership. Gap (minor): the canvas format (`:23-28`) differs from the onboarding template (`ONBOARDING.md:24`) and again from the self-assessment form (`community/CAPABILITY_SELF_ASSESSMENT.md:107`, which adds a "because" clause) — three shapes for the same first post. |
| First contribution | PASS (friction) | Taxonomy question 6 (`docs/framework/TAXONOMY.md:14`) routes her sanitized observation to a **Note** — correct. But the taxonomy is not linked from the quickstart, `CONTRIBUTING.md`, or onboarding; she finds the right type only because "Note" happens to be the first bullet. If she reaches `templates/NOTE.md:19`, the schema link (`docs/schemas/NOTE_SCHEMA.md`) is present and the required headings are followable by a non-engineer. A one-line correction PR remains the smallest safe alternative. |

**Persona verdict (simulation):** she converges on a safe Note or correction,
but only through unlinked-file luck at three separate steps.

### 2. Arun — technical builder

**Simulated need (hypothetical):** propose a small internal-facing retrieval
tool that uses only approved documents and must be evaluated before use; he can
publish a sanitized boundary but not the documents or credentials.

| Step | Result | What happens and the exact gap |
| --- | --- | --- |
| README | STALL | Same operator-facing root as Nia. Arun reads `README.md:3` and plausibly concludes the repository is a private build tool for an existing swarm, not an open community. Nothing on the page contradicts him. |
| Contributor quickstart | PASS (repo) | `CONTRIBUTOR_QUICKSTART.md:13` sends him to the Project issue form; the form links [the contribution model] and its own checklist. The Lab path (`:12`) links both `lab.yml` and `templates/LAB.md`. The Git-native section (`:18-21`) is executable without Buzz. |
| Onboarding | PASS (repo); FAIL (live) | The self-assessment correctly routes an AI-enabled system to **Build** (`community/CAPABILITY_SELF_ASSESSMENT.md:26-27, 81-90`); the `start-here` first action is desk-complete. Live entry remains gated by the still-unnamed invitation request route (see comparison below). |
| `start-here` canvas | PASS (repo); FAIL (live) | `buzz/canvases/start-here.md:12` and `:16-17` point Build work to `build` and bounded proposals to `projects`. Consistent with the channel map (`buzz/INFORMATION_ARCHITECTURE.md:27,29`). |
| First contribution | PASS (repo) | Taxonomy question 1 (`docs/framework/TAXONOMY.md:9`) sends a maintained-tool intent to **Project** — correct, and the G2 artifacts make the path real: `templates/PROJECT.md:19` links `docs/schemas/PROJECT_SCHEMA.md` and the intake form. The schema's Project-or-Lab boundary (`PROJECT_SCHEMA.md:57-62`) correctly redirects his pre-maintainer prototype to a Lab. This is the best-wired persona path. |
| Phase 2 practices exposure | PASS (friction) | Reading `practices/README.md:3-13`, he sees six method candidates where `README.md:70` told him there are "three current method files". The practices index text itself is accurate for six; the contradiction sits in the root README and `CONTEXT.md` (see new-artifact tests below). No persona-blocking confusion. |

**Persona verdict (simulation):** fully wired Git path; the only friction is
the stale method count and the unmarked operator-facing README.

### 3. Mei — internal AI lead

**Simulated need (hypothetical):** document a real proposal that moved
first-draft support triage to a reviewed AI-assisted step with a named decision
owner; her employer data stays out of Buzz. She arrives with a real
implementation account — the persona the G4 intake/consent route was built for.

| Step | Result | What happens and the exact gap |
| --- | --- | --- |
| README | STALL | Same operator-facing root; nothing signals a community of practice she could join as a transformation lead. |
| Contributor quickstart | **MISROUTE** | `CONTRIBUTOR_QUICKSTART.md:9-13` offers Correction/Note, Practice, Lab, Project — **no Story row**, though a real implementation is exactly a Story (`docs/framework/TAXONOMY.md:10`). `CONTRIBUTING.md:16` mentions "Guide, Lab, or Story" with no template, schema, or intake link. The most likely outcome is that Mei files under the closest visible path (a Note or the Story issue form) with no consent step. |
| Story issue form | **STALL — highest-risk gap** | `.github/ISSUE_TEMPLATE/story.yml` asks for raw Before / Intervention / Result text with no pointer to `templates/INTAKE_CONSENT.md` or `templates/REDACTION_CHECKLIST.md`. A real implementation submitted here goes straight into a public issue with no redaction gate — the exact failure the G4 templates exist to prevent. |
| Intake/consent route (G4) | **NOT FOUND** | `templates/INTAKE_CONSENT.md:1-3` and `templates/REDACTION_CHECKLIST.md:1-3` are complete and correctly cross-linked to each other — but nothing else links them. The only inbound references in the repository are their mutual links, `handoffs/G4.md`, and `SWARM_PHASE2_PLAN.md:91`. Every newcomer-facing Story surface (`CONTRIBUTOR_QUICKSTART.md`, `CONTRIBUTING.md:16`, `story.yml`, `templates/STORY.md`, `community/ONBOARDING.md:84`, `content/launch/FIRST_10.md:377` "obtain explicit consent") omits the route. Mei cannot find it by walking the documented path. |
| Onboarding / self-assessment | PASS (repo); FAIL (live) | The assessment routes her correctly to **Transform** (`community/CAPABILITY_SELF_ASSESSMENT.md:23-24, 92-101`), and the first post is desk-draftable. Live entry is gated by the same missing request route. |
| `start-here` canvas | PASS (repo); FAIL (live) | `buzz/canvases/start-here.md:13` routes Transform; consistent with the IA. |
| First contribution | PASS (friction, degraded) | Failing to find the Story route, her safe fallback is a sanitized Note (`docs/framework/TAXONOMY.md:14`, `docs/schemas/NOTE_SCHEMA.md:5` explicitly keeps an anecdote from becoming a measurement). This preserves safety but silently discards the structured Story path, its evidence-quality labels, and the private intake ledger row. |

**Persona verdict (simulation):** the only persona whose primary contribution
type is unreachable through the documented path, and the only persona exposed
to a public-disclosure failure mode.

## New-artifact tests

### Can each persona choose the right artifact type?

| Persona | Correct type (taxonomy) | Chosen via documented path | Why |
| --- | --- | --- | --- |
| Nia | Note | Yes, but only because "Note" is the first quickstart bullet; taxonomy and `templates/NOTE.md` are not linked from her entry surfaces | `CONTRIBUTOR_QUICKSTART.md:10` |
| Arun | Project (or Lab pre-maintainer) | Yes; quickstart, issue form, template, and schema chain is complete | `CONTRIBUTOR_QUICKSTART.md:12-13`, `PROJECT_SCHEMA.md:57-62` |
| Mei | Story | **No** — no Story path in the quickstart, no intake/consent link anywhere she walks | `CONTRIBUTOR_QUICKSTART.md:9-13`, orphaned `templates/INTAKE_CONSENT.md` |

The taxonomy decision questions themselves (`docs/framework/TAXONOMY.md:9-14`)
are clear and correctly ordered. The failure is discoverability, not content:
the taxonomy is linked only from schemas, templates, the Guide's Frontier
section (`guides/ai-native-practitioner/README.md:172`), and
`FIRST_10.md:373` — never from the contribution entry points.

### Can a newcomer with a real story find the intake/consent route (G4)?

**No.** Tested by walking every surface a Story author touches:
`CONTRIBUTOR_QUICKSTART.md` (no Story row), `CONTRIBUTING.md:16` (Story named,
no links), `.github/ISSUE_TEMPLATE/story.yml` (no intake or redaction
pointer), `templates/STORY.md:61-63` ("Anonymization and consent" section with
no link to the intake record), `docs/schemas/STORY_SCHEMA.md:58-66`
(anonymization rules, no intake link), `content/launch/FIRST_10.md:377`
(consent required, route unnamed). The templates themselves
(`templates/INTAKE_CONSENT.md`, `templates/REDACTION_CHECKLIST.md`) are
operationally sound — private record, handle-only ledger, two-signature
redaction pass — but they form a closed loop. Until one newcomer-facing
surface links them, G4 is effectively unshipped.

### Do practices 004–006 break the "three Practices" messaging?

Partially — the directory grew, the copy did not. Specific conflicts:

- `README.md:70-72`: "The **three current method files** are proposed
  candidates with `evidence_quality: none`…" — there are six
  (`practices/001-006`). Factually stale at HEAD.
- `CONTEXT.md:60-68`: "First three Practice candidates" presents 001–003 as
  the candidate set without acknowledging 004–006 exist.
- `README.md:60`: launch criterion "Three tested Open Practices" is now
  ambiguous against six candidates (exactly three, or at least three?).
- `guides/ai-native-practitioner/README.md:86-94` links only 001–003 and the
  three trial Labs. This is internally consistent for the Guide's spine and
  not a defect by itself, but a Guide reader who then opens `practices/` meets
  three candidates the Guide never mentions.
- `practices/README.md:1-13` is accurate and lists all six with correct
  maturity framing — the one file that survived G3 unchanged.

Practices 004–006 do not appear in any onboarding, IA, canvas, or seed
material, so they cannot misroute a persona's first post. The residual risk is
copy inconsistency, not navigation.

## Comparison against ONBOARDING_DRY_RUN (Q003)

| # | Original finding | Status now | Evidence |
| --- | --- | --- | --- |
| 1 | Blocker — no operational invitation request route | **Persists** | `ops/INVITE_FUNNEL.md:78-81` still holds broad invitation promotion ("If no private, human-monitored request route exists, continue linking only to the public repository"); no route is named anywhere in the repository. Direct invitation of known collaborators remains available (`INVITE_FUNNEL.md:93-95`), which is what keeps private beta possible. |
| 2 | Blocker — launch copy cannot carry a visitor to a real destination | **Persists (publish-time by design)** | `content/launch/SOCIAL_KIT.md` placeholders (`[REPOSITORY_URL]`, `[BUZZ_URL]`, `[#START_HERE_CHANNEL]`, …) remain; the replace-and-click-test checklist is unchanged at `SOCIAL_KIT.md:233`. This cannot be fixed in Git and stays an owner publish gate. |
| 3 | Major — no evidence the member-visible Buzz surface exists | **Partially addressed** | `release/HOSTED_INSPECTION.md` (O3) now supplies the post-apply inspection checklist with evidence rules and a run-identity record; its fields are unfilled templates (`HOSTED_INSPECTION.md:42-53`), so no executed inspection evidence exists yet. |
| 4 | Major — Steward escalation has no actionable human destination | **Addressed at profile level** | `buzz/agents/STEWARD.md:83-93` adds the deployment prerequisite the original review requested: the profile may not be enabled until a tested, member-actionable escalation reference exists, and it specifies a fallback message. The actual configured destination is still a human deployment act; the O2 readiness-check script (`scripts/steward_readiness_check.py`) is not yet present. |

New findings in V2 (none were present in the original scope):

- **N1 (Major) — G4 intake/consent route unreachable from every Story
  surface.** Detailed above; the risk is public disclosure of a real
  implementation's confidential details via `story.yml`.
- **N2 (Major) — the artifact taxonomy is not linked from any contribution
  entry point.** `docs/framework/TAXONOMY.md` has zero inbound links from
  `CONTRIBUTOR_QUICKSTART.md`, `CONTRIBUTING.md`, `community/ONBOARDING.md`,
  or the canvas. Personas classify from the quickstart's partial path list
  instead, which is how Mei is misrouted.
- **N3 (Minor) — quickstart path list is incomplete against the taxonomy:**
  no Story or Guide row, and the Note bullet links no template/schema while
  Practice, Lab, and Project bullets each link theirs
  (`CONTRIBUTOR_QUICKSTART.md:9-13`).
- **N4 (Minor) — "three" copy stale after G3:** `README.md:70-72`,
  `CONTEXT.md:60-68`, and the ambiguity of `README.md:60` (detailed above).
- **N5 (Minor) — three different first-post formats:** `ONBOARDING.md:24`,
  `CAPABILITY_SELF_ASSESSMENT.md:107` (adds a "because" clause), and
  `buzz/canvases/start-here.md:23-28` (drops the role line). A persona
  cross-reading them cannot tell which is canonical.
- **N6 (Minor, scope expansion) — the repository root README is
  swarm-operator-facing:** `README.md:1-51` contains no community entry
  pointer. Not flagged by the original dry run because it did not walk from
  the README; V2's wider entry path exposes it for all three personas.

## Ranked defects for this report

1. **Major — Story contribution path has no intake/consent gate and no
   Story row in the contribution quickstart** (N1). Smallest correction: add a
   Story bullet to `CONTRIBUTOR_QUICKSTART.md` linking
   `templates/INTAKE_CONSENT.md` and `templates/REDACTION_CHECKLIST.md`; add
   the same links to `story.yml`, `templates/STORY.md`, and the
   `CONTRIBUTING.md` Story row. Owner files: `community/CONTRIBUTOR_QUICKSTART.md`,
   `.github/ISSUE_TEMPLATE/story.yml`.
2. **Major — taxonomy not linked from contribution entry points** (N2).
   Smallest correction: one taxonomy link in the quickstart's "Choose a path"
   intro and in `CONTRIBUTING.md`'s path-table intro.
3. **Blocker for public promotion, unchanged — no named request route**
   (original #1, persists). Required before any public invitation CTA; not
   required for a private beta that uses direct human invitations.
4. **Minor — stale "three" copy and first-post format drift** (N4, N5). One
   commit: update `README.md:60,70-72` and `CONTEXT.md:60-68`; pick one
   first-post template and reference it from the other two surfaces.

## Checks and acceptance record

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| Identity and scope | Only this report and its handoff changed | No other file edited; no git operations run | PASS |
| Persona coverage | Three distinct personas walk README → quickstart → onboarding → canvas → first contribution | Nia/Learn-Note, Arun/Build-Project, Mei/Transform-Story recorded above | PASS |
| New-artifact test | Taxonomy choice, G4 route findability, 004–006 messaging tested explicitly | Sections above; G4 route found unreachable; six-vs-three copy conflict recorded | PASS |
| Comparison to Q003 | Each original finding dispositioned with current evidence | Table above: 1 persists, 2 persists (publish-time), 3 partial, 4 addressed at profile level | PASS |
| Simulation labeling | No persona reaction presented as user research | All sections labeled simulation/hypothetical | PASS |
| Link and release validation | `check_links.py` and `validate.py` pass after the review is added | Both run clean after writing (see handoff) | PASS |
| Hosted execution | None claimed | No relay, invitation, account, or message accessed | PASS |

**Recommendation:** **conditional yes for private beta** — proceed only with
direct human invitations per `INVITE_FUNNEL.md:93-95`, and only after defects
1, 2, and 4 above are merged (small, single-commit fixes). Public invitation
promotion remains blocked by the still-unnamed request route (original #1) and
the publish-time placeholder replacement (original #2). The best-wired path
(Arun → Project) shows the Phase 2 schema/template wiring works when it is
linked; the Story path needs the same treatment.

## Areas not verified

- Hosted Buzz invitation, join, channel, canvas, seed, thread, or agent
  behavior; the hosted inspection checklist remains unexecuted.
- Whether any real newcomer can actually find or read these files; all
  navigation findings are simulations against the repository text.
- The O1 gate-evidence packet and O2 steward-readiness script (parallel Wave O
  outputs not yet present at review time); their absence is recorded, not
  judged.
- Real maintainer capacity, invitation-queue state, or moderation readiness.

## Taxonomy decision

This is a **review record**: its primary reader action is a human launch
decision from reproducible repository observations. It is not a Practice,
Guide, Lab, Story, Note, or Project.
