# P2-CLEANUP Handoff

Owner-directed director pass. Not a manifest task; recorded here because the
repository's convention is that every unit of work leaves a handoff.

## Status

COMPLETE

## Summary

Four requested pieces of work: close the loose ends Q-INT recorded, wire the
Phase 2 tasks into `swarm/manifest.json`, polish the GitHub-facing documents,
and rewrite the root `README.md` as a community front door rather than a
swarm-operator page.

**Loose ends.** `release/GATE_EVIDENCE.md` now matches the Q6 W1/W2 reframing
in three places: the two "68/68 one-sided agreement" cells state that the
checker reported 0 findings against 68 clean reference verdicts and that the
comparison measures nothing about detection, and "Corroborating but
non-counting evidence" became "Related eval run (same operator class — not
corroboration)". `swarm/README.md` is generalized: two shell variables replace
the hard-coded `/home/dakota` and `/mnt/c/Users/dakot` paths, the destructive
archive route carries a warning, and a Git-clone route is offered first. The
machine-specific paths remaining in `reviews/` and `swarm/handoffs/` are evidence
records of commands actually run and were deliberately left alone.
`CONTRIBUTING.md`'s Story evidence row now routes to the G4 intake/consent and
redaction templates. The three drifted first-post formats are unified:
`community/ONBOARDING.md` is named canonical, and
`community/CAPABILITY_SELF_ASSESSMENT.md` and `buzz/canvases/start-here.md`
reproduce its wording verbatim and link to it (the self-assessment's "because"
clause and the canvas's four-line block are gone, and the canvas example was
restated to fit the form).

**Phase 2 wiring.** All 26 Phase 2 tasks are appended to `swarm/manifest.json`
as waves 6–9 with dependencies as planned, and each has a generated
`swarm/specs/<ID>.md` in the existing spec format. `taskctl.py` already
backfills unseen manifest ids into `.taskctl/state.json`, so no state-init change
was needed; the 26 entries were set to `done` with the commit each landed in
and a note that they predate the wiring. `taskctl.py status` now reports 73
done. A new `revision` mode was added for tasks that rework an artifact another
task created (only G1, over K003's guide modules): `validate.py` enforces
exclusive path ownership within a mode instead of only across `build` tasks,
and `taskctl.py` gained `BROAD_SCOPE_MODES = {integration, revision}`.
`swarm/plans/PHASE2_PLAN.md`'s wiring bullet records that this is done.

**GitHub documents.** `.github/workflows/validate.yml` was deleted as a
near-duplicate of `ci.yml`; `ci.yml` absorbed its pinned Python 3.12 and its
`pip install PyYAML` — which `ci.yml` had been missing while running
`skills/evals/validate.py`, a latent failure on a clean runner — and gained
`concurrency` cancellation, named steps, and `validate_artifacts.py`. New:
`.github/ISSUE_TEMPLATE/config.yml` (blank issues off, four contact links),
`note.yml`, `correction.yml`, and a root `SECURITY.md`. The PR template was
rewritten around the checks CI actually runs plus Story-consent and
maturity-field boxes. `CONTRIBUTING.md`'s path table gained a "Start here"
column linking every issue form, and `CONTRIBUTOR_QUICKSTART.md` gained Note
and Correction bullets.

**README.** Rewritten for a non-technical first-time reader: centered header,
audience and start-here tables, a mermaid capability ladder, an artifact-type
table, an honest three-line project-status block, and a contribution path. The
swarm-operator material is now a short closing section plus a collapsed
build-kit reference that preserves the seven release criteria, the
`.taskctl/state.json` caveat, and the key-file list from the previous README.
This closes O4 finding N6.

## Files changed

- Loose ends: `release/GATE_EVIDENCE.md`, `swarm/README.md`, `CONTRIBUTING.md`,
  `community/ONBOARDING.md`, `community/CAPABILITY_SELF_ASSESSMENT.md`,
  `buzz/canvases/start-here.md`
- Wiring: `swarm/manifest.json`, `swarm/specs/{R1-R4,A1-A5,E1-E5,G1-G4,O1-O5,Q6,Q7,Q-INT}.md` (new),
  `scripts/validate.py`, `scripts/taskctl.py`, `swarm/plans/PHASE2_PLAN.md`,
  `.taskctl/state.json` (ignored local state)
- GitHub: `.github/workflows/ci.yml`, `.github/workflows/validate.yml` (deleted),
  `.github/ISSUE_TEMPLATE/config.yml` (new), `.github/ISSUE_TEMPLATE/note.yml` (new),
  `.github/ISSUE_TEMPLATE/correction.yml` (new), `.github/PULL_REQUEST_TEMPLATE.md`,
  `SECURITY.md` (new), `community/CONTRIBUTOR_QUICKSTART.md`
- README: `README.md`
- `swarm/handoffs/P2-CLEANUP.md` — this file

## Validation

- `python3 scripts/validate.py --release` — PASS, `Validation passed.`
- `python3 -m unittest discover -s tests` — PASS, `Ran 145 tests` / `OK`
- `python3 scripts/validate_artifacts.py` — PASS, `1 guide, 6 guide modules, 4 labs, 6 practices, 1 story`
- `python3 scripts/check_links.py` — PASS, `301 markdown file(s), 712 link target(s): 0 broken link(s), 0 stale as-of date(s)`
- `python3 skills/evals/validate.py --root .` — PASS, `5 skills`
- `python3 scripts/validate.py --task Q-INT --root .` and `--task G1` — now PASS
  (previously `Unknown task`, the condition every Phase 2 handoff recorded)
- `python3 scripts/taskctl.py status` — 73 done, 0 claimed, 0 blocked, 0 todo

## Decisions made

- Phase 2 task metadata was reconstructed from `swarm/plans/PHASE2_PLAN.md` and the
  committed outputs, not invented: every `outputs` entry is a file that exists
  in `git ls-files`, and glob-shaped plan entries (`guides/…/**`,
  `skills/evals/results/`) were expanded to the real paths.
- The plan named O5's second output `.github/ISSUE_TEMPLATE/triage-policy.md`;
  the manifest records the built path `.github/TRIAGE_POLICY.md`, which is
  correct — a `.md` inside `ISSUE_TEMPLATE/` would render as an issue template.
- Ownership is now enforced per mode rather than globally, so G1 can own the
  guide edits without colliding with K003's ownership of the same files. Phase 1
  and Phase 2 never run concurrently, so the "no two active tasks own one path"
  invariant is preserved.
- `SECURITY.md` names no private reporting contact, because that route is an
  open owner gate. It routes to GitHub private vulnerability reporting or the
  Code of Conduct fallback and says plainly that the route is not yet
  established.
- `.github/ISSUE_TEMPLATE/config.yml` uses `smithdak/practice` absolute URLs
  because `contact_links` cannot take relative paths. That is the recorded
  default in `docs/OWNER_GATES.md`, not an assertion that gate 3 is cleared; if the
  destination changes, this file needs updating.
- The README says "an open Git repository", not "public": the repository is not
  published yet.
- README release criterion 4 keeps its original wording and adds a pointer to
  the project-status block stating that it is unmet, rather than being silently
  softened.

## Risks or unresolved questions

- The mermaid ladder diagram was not rendered against GitHub; syntax is valid
  and node labels are quoted, but it is worth a visual check on first push.
- `.github/ISSUE_TEMPLATE/config.yml` hard-codes the default GitHub destination
  and must be revisited when owner gate 3 is decided.
- Deleting `.github/workflows/validate.yml` changes the required-check name from
  `validate` to `ci`; any branch protection configured later must reference `ci`.
- The 26 backfilled `.taskctl/state.json` entries record a landing commit but no
  branch or worktree, because these tasks were not integrated through
  `taskctl.py integrate`. The file is ignored local state and is not release
  evidence.
- No owner gate or operating hold changed status. All eight gates and seven
  holds in `release/OWNER_REVIEW.md` remain **OPEN**.

## Deferred opportunities

- A six-class claim sweep over the prose this pass introduced (README,
  `SECURITY.md`, the new issue forms).
- `CODEOWNERS` and a repository description, both of which need the GitHub
  destination gate decided first.
- A cold read of the new README by someone with no context on the project.
- The remaining Q-INT deferrals are unchanged: second-family eval run, second
  trials per promotion packet, and the onboarding re-run over the fixed
  surfaces.
