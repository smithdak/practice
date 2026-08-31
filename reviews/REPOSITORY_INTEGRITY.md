# Repository integrity and release validation review

## Outcome

**Revision needed; do not represent this candidate as release-validated.** The
repository has four real broken relative-link occurrences, and the release gate
cannot produce reproducible evidence from a clean checkout or from the final
task's worktree. Current schemas, licenses, configured Buzz paths, seed markers,
and registered task histories otherwise passed the bounded checks recorded
below.

This is an acceptance review, not approval to publish. Q005 owns correction and
disposition; a human release owner owns final approval and public effect.

## Gate frame

- **Record:** Q004 repository-integrity review.
- **Reviewed source version:**
  `0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf` on
  `agent/q004-run-repository-integrity-and-release-validation-`.
- **Starting baseline:** root commit
  `b02c696e020796b890ecb9ae691893b66dae4291` for committed-candidate
  whitespace inspection.
- **Intended effect:** decide whether the integrated Git candidate has
  reproducible structure, reference, schema, license, task-state, configuration,
  and release-validation evidence.
- **Impact:** material. A false pass could publish broken navigation or a
  release claim that another reviewer cannot reproduce.
- **Owner:** Q005 final integrator for repository corrections; human release
  owner for acceptance and publication.
- **Reviewer/approval:** Q004 performed an independent repository review. No
  human release approval was supplied or inferred.
- **Out of scope:** hosted Buzz execution, owner gates, invitation operation,
  participant outcomes, and correction of reviewed artifacts.
- **Recovery:** preserve this commit; make corrections in Q005; rerun all
  affected checks on the corrected exact commit. If a post-release check fails,
  stop promotion and restore the last approved Git commit or publish a visible
  corrective commit under `release/LAUNCH_CHECKLIST.md`.

## Ranked findings

### Q004-RI-01 — Blocker — release validation is not reproducible and is circular for Q005

**Locations:** `.gitignore:2`, `scripts/validate.py:131-150`,
`scripts/taskctl.py:205-222`, and `tasks/specs/Q005.md:30-44`.

**Criterion:** release validation must be runnable on the exact candidate and
must distinguish construction state from release content.

**Evidence:** `.swarm/state.json` is ignored and is absent from the Q004 linked
worktree. It would also be absent from a clean checkout. In the primary
orchestration worktree, the ignored state has 45 `done`, Q004 `claimed`, and
Q005 `todo`. `validate_release()` rejects every state other than `done`.
Q005, however, is not marked `done` until `taskctl integrate` has verified and
merged its worktree; `taskctl integrate` runs only task validation before the
merge and performs no release validation after updating state. Therefore Q005
cannot satisfy its requested release pass inside its worktree, and a clean
checkout cannot reproduce a later local pass from the commit alone.

The missing `release/FINAL_INTEGRATION_REPORT.md` and incomplete Q004/Q005
messages are expected at this pre-integration version. They are not source
content defects in `0ec7ad9`; the state/ordering contract that makes them
unresolvable during Q005 is the defect.

**Consequence:** a local orchestrator may eventually obtain a pass that CI, a
clean clone, and an independent reviewer cannot reproduce. Q005's acceptance
language can produce a circular failure or a false claim about the reviewed
version.

**Smallest correction and recovery:** Q005 should make the release gate derive
task completion from committed evidence, or add an explicit post-integration
validation transaction that can roll back/contain a failed merge. If a
pre-integration exception is supported, it must permit only the current final
task, require all dependencies and owned outputs, and record the exact commit;
it must not ignore arbitrary incomplete tasks. Then test both a clean-checkout
case and a deliberately incomplete-task failure case. Owner paths:
`scripts/validate.py`, `scripts/taskctl.py`, and, only if the workflow contract
needs clarification, `tasks/specs/Q005.md`/release documentation.

### Q004-RI-02 — Blocker — four Release Editor template links are broken

**Location:** `buzz/agents/RELEASE_EDITOR.md:91`, `:93`, `:105`, and `:106`.

**Criterion:** every relative Markdown link resolves and normal validation
passes from the primary repository root.

**Evidence:** all four output-template examples use
`[canonical artifact](<link>)`. A tracked-file path audit checked 270 relative
link occurrences across Markdown and YAML and found exactly these four missing
targets. Primary-root normal validation independently reports the same four
errors.

**Consequence:** normal CI validation fails, and a copied Release Editor draft
starts with invalid navigation syntax.

**Smallest correction and recovery:** Q005 should replace these with
non-link placeholder instructions or a real, repository-resolving example,
without weakening the requirement that an actual output contain its canonical
link. Rerun normal validation from a root whose path does not contain
`.worktrees`, plus the direct tracked-file link audit. Owner path:
`buzz/agents/RELEASE_EDITOR.md`.

### Q004-RI-03 — Major validator defect — linked worktrees skip every Markdown link

**Location:** `scripts/validate.py:97-101`.

**Criterion:** the task validator must exercise the same relative-link check in
the isolated worktrees used by every worker.

**Evidence:** `validate_links()` tests the absolute `p.parts` against
`{'.worktrees', '.swarm', '.git'}`. Every Markdown path under this task contains
the ancestor component `.worktrees`, so every Markdown file is skipped. Thus
`--root .` reports `Validation passed.` in Q004 while the same commit checked
from `/home/dakota/projects/practice` reports the four failures in RI-02.

**Consequence:** task and integration checks can accept broken links; the
primary checkout or CI discovers them only later. Q004's eventual task-validator
pass is evidence of output presence and the checks not skipped, not evidence
that links pass.

**Smallest correction and recovery:** test ignored components on each path
relative to `root`, not on the absolute path. Add a fixture where the repository
itself is below a directory named `.worktrees`, and verify that only nested
ignored directories are skipped. Owner path: `scripts/validate.py`.

### Q004-RI-04 — Major validator defect — placeholder detection has false positives and misses the publication tokens

**Locations:** `scripts/validate.py:151-162`,
`content/launch/SOCIAL_KIT.md:5` and throughout that file, and
`ops/FIRST_PRACTICE_SESSION.md:106`.

**Criterion:** release validation must distinguish unfinished publication
values from ordinary explanatory prose.

**Evidence:** the two reported "Release placeholder" failures match the word
`placeholder` in valid instructions: replace bracketed values before publishing,
and use a category or placeholder to protect a participant's real details.
They are false positives, not unfinished content. Conversely, a targeted scan
found 26 actual bracketed publication-token occurrences in
`content/launch/SOCIAL_KIT.md`, including repository, Buzz, channel, handle,
issue, and contribution destinations; the release regex does not detect them.
Q003 already records these tokens as a public-promotion blocker, and the launch
packet keeps the relevant owner gates open.

**Consequence:** deleting or rewording two useful sentences could make this
check green while literal publication tokens remain. The reusable kit may
retain explicit tokens, but no selected post is ready to publish until a human
replaces and click-tests them.

**Smallest correction and recovery:** define an explicit token grammar and a
clear policy for reusable templates versus publication-ready derivatives.
Exclude prose and code examples from unfinished-content detection, retain the
Q003/human publication check, and add positive and negative fixtures. Do not
fill owner-only URLs by guessing. Owner paths: `scripts/validate.py`,
`content/launch/SOCIAL_KIT.md`, and release documentation.

### Q004-RI-05 — Major scope/coverage gap — a post-launch Project is in the launch candidate but outside its manifest and release checks

**Locations:** commit `2127f8f`, `handoffs/PCS001.md`, `.agents/skills/`,
`skills/`, `tasks/manifest.json`, `.github/workflows/validate.yml:14`, and the
artifact map in `release/LAUNCH_CHECKLIST.md`.

**Criterion:** every release artifact has provenance, an explicit release
disposition, and an automated check included in the release evidence.

**Evidence:** commit `task(PCS001): add Practice core skills` adds 15 tracked
files and explicitly identifies itself as a post-launch Project. PCS001 has no
manifest entry or task spec. Its handoff records that the normal task validator
cannot recognize it. The Project-specific command currently passes:
`Practice skill validation passed for 5 skills.`, but normal CI and the release
validator do not run that command, and the L008 release artifact map does not
include the Project.

**Consequence:** the candidate silently includes an experimental Project that
is outside the launch graph and final release evidence. Its five skills may be
valid today but can drift without failing CI.

**Smallest correction and recovery:** Q005/human release ownership should make
an explicit include-or-defer decision. If included, add the Project and its
validator to the release packet/CI without claiming behavioral validation; if
deferred, remove it from the release commit without discarding its preserved
branch/commit. Do not retrofit PCS001 into construction state merely to erase
the discrepancy.

### Q004-RI-06 — Major integrity gap — task scope is documented but not enforced

**Locations:** `scripts/taskctl.py:171-193` and `README.md` (claim that the task
controller prevents concurrent file edits).

**Criterion:** task changes stay within manifest-owned paths.

**Evidence:** `verify_task()` checks only that every expected path changed; it
never rejects `changed_files - expected`. A history audit of 52 registered
`task(<ID>)` commits covering 46 registered task IDs found no registered task
that changed an unowned path, and every such task history changed all owned
paths. That is evidence that this candidate's registered task commits followed
scope; it does not support the README's claim that the controller prevents an
agent from changing an unowned or colliding path.

**Consequence:** a future task can pass deterministic integration while also
changing another task's file. Human instruction compliance is the only current
barrier.

**Smallest correction and recovery:** compare the complete branch diff with the
allowed output/handoff set and reject extras, with an explicit exception for
the intentionally broad Q005 integration mode. Add allowed/disallowed fixtures
and narrow the README claim until enforcement exists. Owner paths:
`scripts/taskctl.py` and `README.md`.

### Q004-RI-07 — Moderate content/config defect — file and task status indexes are stale

**Locations:** `FILE_INDEX.md` and every `status` field in
`tasks/manifest.json` (first occurrence at line 45).

**Criterion:** indexes and machine-readable status do not contradict the
candidate they describe.

**Evidence:** `FILE_INDEX.md` names 134 paths; all exist, but 111 of 245 tracked
paths are absent, including the completed community artifacts, Guide/modules,
schemas, Practices, launch content, two issue forms, `NOTICE`, reviews, and the
skills Project. The manifest contains 47 `status: todo` values. Live state has
45 `done`, Q004 `claimed`, and Q005 `todo`, producing 46 status mismatches.
`taskctl.py` ignores manifest status and uses `.swarm/state.json`, so the stale
field is redundant rather than authoritative.

**Consequence:** readers and tools that reasonably treat these files as indexes
receive an incomplete structure and obsolete construction status.

**Smallest correction and recovery:** regenerate or retire `FILE_INDEX.md`;
for status, either remove the manifest field and document `.swarm/state.json`
as ephemeral operational state, or generate a committed completion record that
does not undermine clean-checkout reproducibility. Owner paths:
`FILE_INDEX.md`, `tasks/manifest.json`, and task-controller documentation.

## Release-validation result classification

| Observed message | Classification | Release disposition |
| --- | --- | --- |
| `.swarm/state.json` absent in Q004 | Expected for an ignored isolated/clean checkout; also evidence of RI-01 | Does not prove incomplete content; blocks a reproducible release pass until the gate is corrected. |
| `Q004, Q005` incomplete in primary state | Expected pre-integration state | Do not mark them done early. The Q005 circular ordering still requires RI-01 correction. |
| `release/FINAL_INTEGRATION_REPORT.md` missing | Expected Q005-owned final artifact | Q005 must create it, then validate the exact integrated version. |
| Four `RELEASE_EDITOR.md -> <link>` errors | Actual candidate content defect | Correct under RI-02; normal CI cannot pass otherwise. |
| `SOCIAL_KIT.md` placeholder match | Validator false positive on prose; 26 real publication tokens remain | Correct RI-04 and keep public promotion blocked until human substitution/click testing. |
| `FIRST_PRACTICE_SESSION.md` placeholder match | Validator false positive on privacy-preserving prose | Correct the check, not the safe instruction. |

## Exact normal and release validation evidence

The required local command wrapper was `rtk`; commands below are recorded
exactly as invoked.

### Isolated Q004 worktree, before review outputs

Command:

```text
rtk python3 scripts/validate.py --root .
```

Output:

```text
Validation passed.
```

This is not a link pass because RI-03 skips every Markdown file.

Command:

```text
rtk python3 scripts/validate.py --release --root .
```

Output:

```text
Validation failed:
- Release validation requires .swarm/state.json
- Release missing required artifact: release/FINAL_INTEGRATION_REPORT.md
- Release placeholder found in content/launch/SOCIAL_KIT.md
- Release placeholder found in ops/FIRST_PRACTICE_SESSION.md
```

Command:

```text
rtk python3 scripts/validate.py --task Q004 --root .
```

Output before the owned files existed:

```text
Validation failed:
- Task Q004 missing output reviews/REPOSITORY_INTEGRITY.md
- Task Q004 missing output handoffs/Q004.md
```

The final Q004 task result is recorded in the handoff after both files exist.

### Primary orchestration root at the same Git commit

Command:

```text
rtk python3 scripts/validate.py --root /home/dakota/projects/practice
```

Output:

```text
Validation failed:
- Broken relative link: buzz/agents/RELEASE_EDITOR.md -> <link>
- Broken relative link: buzz/agents/RELEASE_EDITOR.md -> <link>
- Broken relative link: buzz/agents/RELEASE_EDITOR.md -> <link>
- Broken relative link: buzz/agents/RELEASE_EDITOR.md -> <link>
```

Command:

```text
rtk python3 scripts/validate.py --release --root /home/dakota/projects/practice
```

Output:

```text
Validation failed:
- Broken relative link: buzz/agents/RELEASE_EDITOR.md -> <link>
- Broken relative link: buzz/agents/RELEASE_EDITOR.md -> <link>
- Broken relative link: buzz/agents/RELEASE_EDITOR.md -> <link>
- Broken relative link: buzz/agents/RELEASE_EDITOR.md -> <link>
- Release has incomplete tasks: Q004, Q005
- Release missing required artifact: release/FINAL_INTEGRATION_REPORT.md
- Release placeholder found in content/launch/SOCIAL_KIT.md
- Release placeholder found in ops/FIRST_PRACTICE_SESSION.md
```

## Checks performed

| Check | Expected | Observed evidence | Result and limit |
| --- | --- | --- | --- |
| Tracked relative links and references | Every relative target exists inside the repository | 245 tracked files; 283 inline links in tracked Markdown/YAML; 270 relative occurrences; four missing occurrences, all RI-02. Manifest: 248 input refs and 47 spec refs, none missing; before Q004 output, only Q004/Q005 outputs/handoffs were absent as expected. Buzz: 24 canvas/seed refs, none missing. Four relative fragment links point to present headings. | **FAIL** because of RI-02. The direct audit covers inline Markdown/YAML links, manifest paths, and Buzz configured paths; it does not test external URLs. |
| Manifest graph/state | Unique IDs, known dependencies, expected readiness | 47 unique manifest IDs; no unknown dependencies; manifest/state ID sets equal. Q004 dependencies F009/L008 are `done`; Q005 waits only for Q004. All 45 state-`done` tasks have outputs and handoffs. Status fields disagree as RI-07 records. | **PASS** for IDs, dependencies, ready ordering, and completed output presence; **FAIL** for status consistency/reproducibility. |
| Task change scope | Registered task commits change only owned paths | 52 task commits, 46 registered task IDs; zero registered out-of-scope paths and zero owned paths missing across each task history. PCS001 is the one explicit unregistered task identifier. | **PASS** for observed registered history; controller enforcement remains **FAIL** under RI-06. |
| Schema conformance | Current canonical artifacts follow their documented mechanical schema | Three Practices, Guide entry point, proposed Lab, and hypothetical Story: required metadata and required heading order passed; enum/date/version/license/state relationships checked with zero errors. `python3 skills/evals/validate.py --root .` reported `Practice skill validation passed for 5 skills.` | **PASS** for the six current content records and five skill records checked. Main CI does not enforce the content schemas or skill validator. Human evidence quality was not inferred from structure. |
| Licenses and attribution | Dual-license policy is present and internally consistent | `LICENSE-CODE` contains the Apache License 2.0 text; `LICENSE-CONTENT.md`, `LICENSES.md`, `NOTICE`, `community/ATTRIBUTION.md`, and all six artifact metadata records consistently assign Apache-2.0 to code and CC BY 4.0 to content. Q001 separately traced these terms to canonical sources as of 2026-08-31. | **PASS** for repository consistency and presence. Final license confirmation remains an open human owner gate. |
| Configured/generated files | Tracked configs parse; scripts have basic syntax integrity; generated local files are excluded | 2 JSON files and 11 YAML files parsed; 4 Python files parsed as syntax trees; `bash -n scripts/init.sh scripts/doctor.sh` produced no output. Tracked modes make the two shell entrypoints executable. Q004 status was clean; only ignored `TASK_PROMPT.md` was present. | **PASS** for parsing/syntax/modes and expected ignored task prompt. No hosted Buzz apply or GitHub Actions execution was performed. |
| Buzz config and seed identity | Twelve streams, all referenced artifacts, one unique marker per seed | Normal validator and dry run accepted 12 configured stream channels. Direct scan: 12 seed files, 12 markers, no file with other than one marker, no duplicate marker values. Dry run emitted 60 ensure/set/seed-if-missing actions and no delete/archive/membership/workflow action. | **PASS** for repository configuration only; no hosted state is claimed. |
| TODO/TBD/placeholders | No unfinished public scaffold is misclassified | No `TODO`, `TBD`, or `LOREM IPSUM` token in public Markdown. Two prose `placeholder` matches are false positives. Social kit contains 26 actual publication tokens; template-style examples also occur in agent profiles and templates. | **FAIL** for release-validator accuracy; **HOLD** for publishing social copy; no generic repository-template failure. |
| Secret/credential patterns | No committed credential or private key | Known-format scan found no AWS/GitHub/OpenAI/Slack token or PEM private-key header. Assignment heuristic found only documented `BUZZ_PRIVATE_KEY='local-identity-key'` in `buzz/BOOTSTRAP_RUNBOOK.md`; it is an explicit example value. `.env.example` leaves secret fields empty, and `.env` is ignored. | **PASS** for the bounded current-tree pattern scan. This is not proof against every possible secret format or Git history. |
| Committed-candidate whitespace | No whitespace errors in the integrated range or candidate commit | `git diff --check b02c696e020796b890ecb9ae691893b66dae4291..0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf` and `git show --check --oneline 0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf` produced no output. | **PASS** for that exact pre-review candidate. Final Q004 and Q005 commits require their own checks. |
| Existing independent review gates | Blocking findings remain visible | `reviews/EDITORIAL_REVIEW.md` says not ready for publication; `reviews/ONBOARDING_DRY_RUN.md` says revision needed before public invitation promotion; L008 keeps every owner gate and three operating holds open. | **FAIL/HOLD** for public launch. Q004 does not re-adjudicate or silently clear those owners' findings. |

## Areas not verified

- External HTTP links, GitHub rendering/issue-form behavior, hosted Buzz state,
  invitation/revocation controls, or public destinations were not exercised.
- No live credential, private key, `.env`, owner identity, or confidential
  system was accessed.
- Content-schema checks covered the current Guide, three Practices, one Lab,
  and hypothetical Story; they do not substitute for editorial/evidence review.
- Secret detection used named token/header/assignment patterns on the current
  tree, not a dedicated historical secret scanner.
- Q005's future corrections, final integration report, final state transition,
  final commit whitespace, and post-integration release result do not yet exist.

## Taxonomy and recommendation

This file is a **review/acceptance record**, not a Practice, Guide, Lab, Story,
or Project. Its primary action is a maintainer release decision backed by
reproducible repository observations.

**Recommendation: revise.** Correct RI-01 through RI-04 before claiming a
release-validation pass; explicitly disposition RI-05; enforce or narrow the
claims in RI-06; and resolve or knowingly defer RI-07. After correction, run
normal and release validation from both the isolated/fresh-checkout context and
the primary integration context, run the direct reference/schema/secret/seed
checks, inspect the full diff, and obtain human approval for the exact commit.

