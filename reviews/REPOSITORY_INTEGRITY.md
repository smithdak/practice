# Repository integrity and release validation review

**As of:** 2026-09-01 (currency re-stamp added at Phase 2 integration; the
audit itself was recorded 2026-08-31 at commit `b02c696`).

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
`scripts/taskctl.py:205-222`, and `swarm/specs/Q005.md:30-44`.

**Criterion:** release validation must be runnable on the exact candidate and
must distinguish construction state from release content.

**Evidence:** `.taskctl/state.json` is ignored and is absent from the Q004 linked
worktree. It would also be absent from a clean checkout. In the primary
orchestration worktree, the ignored state has 45 `done`, Q004 `claimed`, and
Q005 `todo`. `validate_release()` rejects every state other than `done`.
Q005, however, is not marked `done` until `taskctl integrate` has verified and
merged its worktree; `taskctl integrate` runs only task validation before the
merge and performs no release validation after updating state. Therefore Q005
cannot satisfy its requested release pass inside its worktree, and a clean
checkout cannot reproduce a later local pass from the commit alone.

The missing `swarm/reports/PHASE1_REPORT.md` and incomplete Q004/Q005
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
needs clarification, `swarm/specs/Q005.md`/release documentation.

### Q004-RI-02 — Blocker — four Release Editor template links are broken

**Location:** `buzz/agents/RELEASE_EDITOR.md:91`, `:93`, `:105`, and `:106`.

**Criterion:** every relative Markdown link resolves and normal validation
passes from the primary repository root.

**Evidence:** all four output-template examples use
a canonical-artifact Markdown link whose target is the literal token `<link>`.
A source-commit scan checked 245 tracked files,
283 inline Markdown-link matches, 13 external targets, and 270 relative target
occurrences across tracked Markdown and YAML; exactly these four relative
occurrences were missing. The release-public Markdown subset, which omits the
two issue-form YAML links and the intentionally excluded `SAMPLE_` file, has
280 inline matches and 267 relative targets. Primary-root normal validation
independently reports the same four errors.

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
`ops/outreach/SOCIAL_KIT.md:5` and throughout that file, and
`ops/FIRST_PRACTICE_SESSION.md:106`.

**Criterion:** release validation must distinguish unfinished publication
values from ordinary explanatory prose.

**Evidence:** the two reported "Release placeholder" failures match the word
`placeholder` in valid instructions: replace bracketed values before publishing,
and use a category or placeholder to protect a participant's real details.
They are false positives, not unfinished content. A Q005 correction reran the
scan with optional `@`/`#` prefixes and found 26 actual bracketed
publication-token occurrences in
`ops/outreach/SOCIAL_KIT.md`, including repository, Buzz, channel, handle,
issue, and contribution destinations; the release regex reviewed by Q004 did
not detect them.
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
`ops/outreach/SOCIAL_KIT.md`, and release documentation.

### Q004-RI-05 — Major scope/coverage gap — a post-launch Project is in the launch candidate but outside its manifest and release checks

**Locations:** commit `2127f8f`, `swarm/handoffs/PCS001.md`, `.agents/skills/`,
`skills/`, `swarm/manifest.json`, `.github/workflows/validate.yml:14`, and the
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
never rejects `changed_files - expected`. The source history contains 52
`task(<ID>)` commits across 46 identifiers in total. Excluding the explicitly
unregistered PCS001 commit leaves 51 registered commits across 45 registered
task IDs. The registered histories contained no out-of-scope path, and their
combined changes covered every owned path. That is evidence that this
candidate's registered task commits followed scope; it does not support the
README's claim that the controller prevents an agent from changing an unowned
or colliding path.

**Consequence:** a future task can pass deterministic integration while also
changing another task's file. Human instruction compliance is the only current
barrier.

**Smallest correction and recovery:** compare the complete branch diff with the
allowed output/handoff set and reject extras, with an explicit exception for
the intentionally broad Q005 integration mode. Add allowed/disallowed fixtures
and narrow the README claim until enforcement exists. Owner paths:
`scripts/taskctl.py` and `README.md`.

### Q004-RI-07 — Moderate content/config defect — file and task status indexes are stale

**Locations:** `swarm/README.md` and every `status` field in
`swarm/manifest.json` (first occurrence at line 45).

**Criterion:** indexes and machine-readable status do not contradict the
candidate they describe.

**Evidence:** `swarm/README.md` names 134 paths; all exist, but 111 of 245 tracked
paths are absent, including the completed community artifacts, Guide/modules,
schemas, Practices, launch content, two issue forms, `NOTICE`, reviews, and the
skills Project. The manifest contains 47 `status: todo` values. Live state has
45 `done`, Q004 `claimed`, and Q005 `todo`, producing 46 status mismatches.
`taskctl.py` ignores manifest status and uses `.taskctl/state.json`, so the stale
field is redundant rather than authoritative.

**Consequence:** readers and tools that reasonably treat these files as indexes
receive an incomplete structure and obsolete construction status.

**Smallest correction and recovery:** regenerate or retire `swarm/README.md`;
for status, either remove the manifest field and document `.taskctl/state.json`
as ephemeral operational state, or generate a committed completion record that
does not undermine clean-checkout reproducibility. Owner paths:
`swarm/README.md`, `swarm/manifest.json`, and task-controller documentation.

## Release-validation result classification

| Observed message | Classification | Release disposition |
| --- | --- | --- |
| `.taskctl/state.json` absent in Q004 | Expected for an ignored isolated/clean checkout; also evidence of RI-01 | Does not prove incomplete content; blocks a reproducible release pass until the gate is corrected. |
| `Q004, Q005` incomplete in primary state | Expected pre-integration state | Do not mark them done early. The Q005 circular ordering still requires RI-01 correction. |
| `swarm/reports/PHASE1_REPORT.md` missing | Expected Q005-owned final artifact | Q005 must create it, then validate the exact integrated version. |
| Four `RELEASE_EDITOR.md -> <link>` errors | Actual candidate content defect | Correct under RI-02; normal CI cannot pass otherwise. |
| `SOCIAL_KIT.md` placeholder match | Validator false positive on prose; corrected grammar finds 26 real publication tokens | Correct RI-04 and keep public promotion blocked until human substitution/click testing. |
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
- Release validation requires .taskctl/state.json
- Release missing required artifact: swarm/reports/PHASE1_REPORT.md
- Release placeholder found in ops/outreach/SOCIAL_KIT.md
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
- Task Q004 missing output swarm/handoffs/Q004.md
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
- Release missing required artifact: swarm/reports/PHASE1_REPORT.md
- Release placeholder found in ops/outreach/SOCIAL_KIT.md
- Release placeholder found in ops/FIRST_PRACTICE_SESSION.md
```

## Checks performed

| Check | Expected | Observed evidence | Result and limit |
| --- | --- | --- | --- |
| Tracked relative links and references | Every relative target exists inside the repository | 245 tracked files; 283 inline link matches in tracked Markdown/YAML; 13 external and 270 relative target occurrences; four missing occurrences, all RI-02. The release-public Markdown subset has 280 inline and 267 relative occurrences. Manifest: 248 input refs and 47 spec refs, none missing; before Q004 output, only Q004/Q005 outputs/handoffs were absent as expected. Buzz: 24 canvas/seed refs, none missing. Four relative occurrences include fragments. | **FAIL** because of RI-02. The direct audit covers inline Markdown/YAML base targets, manifest paths, and Buzz configured paths; it does not test external URLs or renderer-specific fragment semantics. |
| Manifest graph/state | Unique IDs, known dependencies, expected readiness | 47 unique manifest IDs; no unknown dependencies; manifest/state ID sets equal. Q004 dependencies F009/L008 are `done`; Q005 waits only for Q004. All 45 state-`done` tasks have outputs and handoffs. Status fields disagree as RI-07 records. | **PASS** for IDs, dependencies, ready ordering, and completed output presence; **FAIL** for status consistency/reproducibility. |
| Task change scope | Registered task commits change only owned paths | 52 task commits across 46 identifiers total; after excluding PCS001, 51 commits across 45 registered task IDs. Registered histories had zero out-of-scope paths and zero owned paths missing in aggregate. | **PASS** for observed registered history; controller enforcement remains **FAIL** under RI-06. |
| Schema conformance | Current canonical artifacts follow their documented mechanical schema | Three Practices, Guide entry point, proposed Lab, and hypothetical Story: required metadata, required heading order, semantic version, license, and current Practice/Lab state relationships checked with zero errors. `python3 skills/evals/validate.py --root .` reported `Practice skill validation passed for 5 skills.` | **PASS** for the six current content records and five skill records checked. Main CI does not enforce the content schemas or skill validator. Human evidence quality was not inferred from structure. |
| Licenses and attribution | Dual-license policy is present and internally consistent | `LICENSE-CODE` contains the Apache License 2.0 text; `LICENSE-CONTENT.md`, `LICENSES.md`, `NOTICE`, `community/ATTRIBUTION.md`, and all six artifact metadata records consistently assign Apache-2.0 to code and CC BY 4.0 to content. Q001 separately traced these terms to canonical sources as of 2026-08-31. | **PASS** for repository consistency and presence. Final license confirmation remains an open human owner gate. |
| Configured/generated files | Tracked configs parse; scripts have basic syntax integrity | 2 JSON files and 11 YAML files parsed; 4 Python files parsed as syntax trees; `bash -n scripts/init.sh scripts/doctor.sh` produced no output. Tracked modes make the two shell entrypoints executable. | **PASS** for parsing, syntax, and modes. No hosted Buzz apply or GitHub Actions execution was performed. |
| Buzz config and seed identity | Twelve streams, all referenced artifacts, one unique marker per seed | Normal validator and dry run accepted 12 configured stream channels. Direct scan: 12 seed files, 12 markers, no file with other than one marker, no duplicate marker values. Dry run emitted 60 ensure/set/seed-if-missing actions and no delete/archive/membership/workflow action. | **PASS** for repository configuration only; no hosted state is claimed. |
| TODO/TBD/placeholders | No unfinished public scaffold is misclassified | No `TODO`, `TBD`, or `LOREM IPSUM` token in public Markdown. Two prose `placeholder` matches are false positives. The corrected optional-prefix grammar finds 26 actual publication tokens in the social kit; template-style examples also occur in agent profiles and templates. | **FAIL** for release-validator accuracy; **HOLD** for publishing social copy; no generic repository-template failure. |
| Secret/credential patterns | No committed credential or private key | Known-format scan found no AWS/GitHub/OpenAI/Slack token or PEM private-key header. Assignment heuristic found only documented `BUZZ_PRIVATE_KEY='local-identity-key'` in `buzz/BOOTSTRAP_RUNBOOK.md`; it is an explicit example value. `.env.example` leaves secret fields empty, and `.env` is ignored. | **PASS** for the bounded current-tree pattern scan. This is not proof against every possible secret format or Git history. |
| Committed-candidate whitespace | No whitespace errors in the integrated range or candidate commit | `git diff --check b02c696e020796b890ecb9ae691893b66dae4291..0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf` and `git show --check --oneline 0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf` produced no output. | **PASS** for that exact pre-review candidate. Final Q004 and Q005 commits require their own checks. |
| Existing independent review gates | Blocking findings remain visible | `reviews/EDITORIAL_REVIEW.md` says not ready for publication; `reviews/ONBOARDING_DRY_RUN_PHASE1.md` says revision needed before public invitation promotion; L008 keeps every owner gate and three operating holds open. | **FAIL/HOLD** for public launch. Q004 does not re-adjudicate or silently clear those owners' findings. |

## Reproducibility appendix for bounded checks

Unless a command says otherwise, these commands ran from the Q004 linked
worktree against source commit
0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf. Outputs below are exact.

### Links and referenced files

Command:

    rtk python3 - <<'PY'
    import json
    import posixpath
    import re
    import subprocess

    source = "0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf"
    files = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", source], text=True
    ).splitlines()
    known = set(files)
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

    def blob(path):
        return subprocess.check_output(
            ["git", "show", f"{source}:{path}"], text=True, errors="replace"
        )

    def audit(public_only):
        inline = external = relative = fragments = 0
        broken = []
        for path in files:
            if public_only:
                if not path.endswith(".md") or posixpath.basename(path).startswith("SAMPLE_"):
                    continue
            elif not path.endswith((".md", ".yml", ".yaml")):
                continue
            for raw in link_re.findall(blob(path)):
                inline += 1
                target = raw.strip()
                if target.startswith(("http://", "https://", "mailto:", "buzz://")):
                    external += 1
                    continue
                relative += 1
                fragments += "#" in target
                base = target.split("#", 1)[0]
                if not base:
                    continue
                candidate = posixpath.normpath(
                    posixpath.join(posixpath.dirname(path), base)
                )
                if candidate not in known and not any(
                    item.startswith(candidate.rstrip("/") + "/") for item in files
                ):
                    broken.append((path, target))
        return inline, external, relative, fragments, broken

    for label, public_only in (("full", False), ("release_public", True)):
        inline, external, relative, fragments, broken = audit(public_only)
        print(
            f"links[{label}] tracked={len(files)} inline={inline} "
            f"external={external} relative={relative} fragments={fragments} "
            f"broken={broken}"
        )

    manifest = json.loads(blob("swarm/manifest.json"))
    inputs = [path for task in manifest["tasks"] for path in task["inputs"]]
    specs = [task["spec"] for task in manifest["tasks"]]
    community = json.loads(blob("buzz/community.json"))
    buzz_refs = [
        channel[key]
        for channel in community["channels"]
        for key in ("canvas", "seed")
    ]
    print(
        f"references input_refs={len(inputs)} missing_inputs={sorted(set(inputs) - known)} "
        f"spec_refs={len(specs)} missing_specs={sorted(set(specs) - known)} "
        f"buzz_refs={len(buzz_refs)} missing_buzz={sorted(set(buzz_refs) - known)}"
    )
    PY

Output:

    links[full] tracked=245 inline=283 external=13 relative=270 fragments=4 broken=[('buzz/agents/RELEASE_EDITOR.md', '<link>'), ('buzz/agents/RELEASE_EDITOR.md', '<link>'), ('buzz/agents/RELEASE_EDITOR.md', '<link>'), ('buzz/agents/RELEASE_EDITOR.md', '<link>')]
    links[release_public] tracked=245 inline=280 external=13 relative=267 fragments=4 broken=[('buzz/agents/RELEASE_EDITOR.md', '<link>'), ('buzz/agents/RELEASE_EDITOR.md', '<link>'), ('buzz/agents/RELEASE_EDITOR.md', '<link>'), ('buzz/agents/RELEASE_EDITOR.md', '<link>')]
    references input_refs=248 missing_inputs=[] spec_refs=47 missing_specs=[] buzz_refs=24 missing_buzz=[]

The full scope is all tracked Markdown and YAML. The release-public scope is
tracked Markdown excluding files whose basename begins with SAMPLE_. This
explains the three-occurrence difference without changing the four broken
targets.

### Manifest state and registered task history

Command:

    rtk python3 - <<'PY'
    import collections
    import json
    import re
    import subprocess
    from pathlib import Path

    source = "0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf"
    manifest = json.loads(subprocess.check_output(
        ["git", "show", f"{source}:swarm/manifest.json"], text=True
    ))
    tasks = {task["id"]: task for task in manifest["tasks"]}
    state = json.loads(
        Path("/home/dakota/projects/practice/.swarm/state.json").read_text()
    )["tasks"]
    unknown_dependencies = sorted(
        (task["id"], dependency)
        for task in tasks.values()
        for dependency in task["dependencies"]
        if dependency not in tasks
    )
    done_missing_outputs = []
    for task_id, record in state.items():
        if record.get("status") != "done" or task_id not in tasks:
            continue
        for path in tasks[task_id]["outputs"] + [tasks[task_id]["handoff"]]:
            result = subprocess.run(
                ["git", "cat-file", "-e", f"{source}:{path}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if result.returncode:
                done_missing_outputs.append((task_id, path))
    state_counts = dict(collections.Counter(
        record.get("status", "todo") for record in state.values()
    ))
    manifest_status_counts = dict(collections.Counter(
        task.get("status") for task in tasks.values()
    ))
    print(
        f"manifest_ids={len(tasks)} unique={len(tasks) == len(set(tasks))} "
        f"state_ids_match={set(tasks) == set(state)} "
        f"unknown_dependencies={unknown_dependencies}"
    )
    print(
        f"state_counts={state_counts} done_missing_outputs={done_missing_outputs}"
    )
    print(f"manifest_status_counts={manifest_status_counts}")

    owned = {
        task_id: set(task["outputs"] + [task["handoff"]])
        for task_id, task in tasks.items()
    }
    task_commits = []
    for line in subprocess.check_output(
        ["git", "log", "--format=%H%x09%s", source], text=True
    ).splitlines():
        commit, subject = line.split("\t", 1)
        match = re.match(r"task\(([^)]+)\):", subject)
        if match:
            task_commits.append((commit, match.group(1)))
    registered = [row for row in task_commits if row[1] in owned]
    changed = collections.defaultdict(set)
    out_of_scope = {}
    for commit, task_id in registered:
        paths = set(subprocess.check_output(
            [
                "git", "diff-tree", "--root", "--no-commit-id",
                "--name-only", "-r", commit
            ],
            text=True,
        ).splitlines())
        changed[task_id] |= paths
        if paths - owned[task_id]:
            out_of_scope[commit] = sorted(paths - owned[task_id])
    registered_ids = {task_id for _, task_id in registered}
    owned_missing = {
        task_id: sorted(paths - changed[task_id])
        for task_id, paths in owned.items()
        if task_id in registered_ids and paths - changed[task_id]
    }
    unregistered = dict(collections.Counter(
        task_id for _, task_id in task_commits if task_id not in owned
    ))
    print(
        f"all_task_commits={len(task_commits)} "
        f"identifiers={len(set(task_id for _, task_id in task_commits))} "
        f"unregistered={unregistered}"
    )
    print(
        f"registered_task_commits={len(registered)} "
        f"registered_ids={len(registered_ids)}"
    )
    print(f"out_of_scope={out_of_scope}")
    print(f"owned_missing={owned_missing}")
    PY

Output:

    manifest_ids=47 unique=True state_ids_match=True unknown_dependencies=[]
    state_counts={'done': 45, 'claimed': 1, 'todo': 1} done_missing_outputs=[]
    manifest_status_counts={'todo': 47}
    all_task_commits=52 identifiers=46 unregistered={'PCS001': 1}
    registered_task_commits=51 registered_ids=45
    out_of_scope={}
    owned_missing={}

The state portion reads the primary orchestrator's ignored state file and is
therefore environment evidence, not clean-checkout evidence; RI-01 records that
limit.

### Artifact schemas, licensing, and skill records

Schema command:

    rtk python3 - <<'PY'
    import re
    import subprocess

    import yaml

    source = "0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf"
    pairs = [
        ("docs/schemas/PRACTICE_SCHEMA.md", "practices/001-context-pack.md"),
        ("docs/schemas/PRACTICE_SCHEMA.md", "practices/002-workflow-redesign.md"),
        ("docs/schemas/PRACTICE_SCHEMA.md", "practices/003-verification-gate.md"),
        ("docs/schemas/GUIDE_SCHEMA.md", "guides/ai-native-practitioner/README.md"),
        ("docs/schemas/LAB_SCHEMA.md", "labs/001-cheap-model-bounded-task.md"),
        ("docs/schemas/STORY_SCHEMA.md", "stories/SAMPLE_HYPOTHETICAL.md"),
    ]
    tick = chr(96)
    errors = []
    for schema_path, artifact_path in pairs:
        schema = subprocess.check_output(
            ["git", "show", f"{source}:{schema_path}"], text=True
        )
        artifact = subprocess.check_output(
            ["git", "show", f"{source}:{artifact_path}"], text=True
        )
        required_fields = {
            line.split(tick, 2)[1]
            for line in schema.splitlines()
            if line.startswith("| " + tick) and "| Yes |" in line
        }
        required_block = re.search(
            r"^## Required [^\n]+\n(.*?)(?=^## )", schema, re.M | re.S
        ).group(1)
        required_headings = [
            line.split(tick, 2)[1]
            for line in required_block.splitlines()
            if re.match(r"^(?:\d+\.|-)", line) and tick in line
        ]
        metadata = yaml.safe_load(artifact.split("---", 2)[1]) or {}
        missing_fields = sorted(required_fields - set(metadata))
        headings = [
            match.group(1).strip()
            for match in re.finditer(r"^## (.+)$", artifact, re.M)
        ]
        positions = [
            headings.index(heading) if heading in headings else -1
            for heading in required_headings
        ]
        if missing_fields:
            errors.append((artifact_path, "metadata", missing_fields))
        if -1 in positions or positions != sorted(positions):
            errors.append((artifact_path, "heading_order", positions))
        if not re.fullmatch(r"\d+\.\d+\.\d+", str(metadata.get("version", ""))):
            errors.append((artifact_path, "version", metadata.get("version")))
        if metadata.get("license") != "CC-BY-4.0":
            errors.append((artifact_path, "license", metadata.get("license")))
        if metadata.get("artifact_type") == "practice" and (
            metadata.get("maturity"), metadata.get("evidence_quality")
        ) != ("proposed", "none"):
            errors.append((artifact_path, "practice_state"))
        if metadata.get("artifact_type") == "lab" and (
            metadata.get("status"),
            metadata.get("result_status"),
            metadata.get("run_count"),
            metadata.get("last_run"),
        ) != ("proposed", "not-run", 0, None):
            errors.append((artifact_path, "lab_state"))
    print(f"artifact_schema_records={len(pairs)} errors={errors}")
    PY

Output:

    artifact_schema_records=6 errors=[]

License command:

    rtk python3 - <<'PY'
    import subprocess
    import yaml

    source = "0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf"
    def blob(path):
        return subprocess.check_output(
            ["git", "show", f"{source}:{path}"], text=True
        )
    checks = {
        "apache_text": (
            "Apache License" in blob("LICENSE-CODE")
            and "Version 2.0" in blob("LICENSE-CODE")
        ),
        "content_license": "CC BY 4.0" in blob("LICENSE-CONTENT.md"),
        "license_map": (
            "Apache License 2.0" in blob("LICENSES.md")
            and "CC BY 4.0" in blob("LICENSES.md")
        ),
        "notice_map": (
            "Apache License, Version 2.0" in blob("NOTICE")
            and "Creative Commons Attribution 4.0" in blob("NOTICE")
        ),
        "attribution_map": (
            "Apache License 2.0" in blob("community/ATTRIBUTION.md")
            and "CC BY 4.0" in blob("community/ATTRIBUTION.md")
        ),
    }
    artifacts = [
        "practices/001-context-pack.md",
        "practices/002-workflow-redesign.md",
        "practices/003-verification-gate.md",
        "guides/ai-native-practitioner/README.md",
        "labs/001-cheap-model-bounded-task.md",
        "stories/SAMPLE_HYPOTHETICAL.md",
    ]
    licenses = sorted({
        (yaml.safe_load(blob(path).split("---", 2)[1]) or {}).get("license")
        for path in artifacts
    })
    print(f"policy_files=5 checks={checks}")
    print(f"artifact_metadata={len(artifacts)} licenses={licenses}")
    PY

Output:

    policy_files=5 checks={'apache_text': True, 'content_license': True, 'license_map': True, 'notice_map': True, 'attribution_map': True}
    artifact_metadata=6 licenses=['CC-BY-4.0']

Skill command and output:

    rtk python3 skills/evals/validate.py --root .
    Practice skill validation passed for 5 skills.

These are structural and consistency checks. They do not independently
establish legal advice, substantive evidence quality, or skill effectiveness.

### Parsed configuration and executable script modes

Parse command:

    rtk python3 - <<'PY'
    import ast
    import json
    import subprocess

    import yaml

    source = "0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf"
    files = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", source], text=True
    ).splitlines()
    parsed = {"json": 0, "yaml": 0, "python": 0}
    errors = []
    for path in files:
        try:
            text = subprocess.check_output(
                ["git", "show", f"{source}:{path}"], text=True
            )
            if path.endswith(".json"):
                json.loads(text)
                parsed["json"] += 1
            elif path.endswith((".yml", ".yaml")):
                yaml.safe_load(text)
                parsed["yaml"] += 1
            elif path.endswith(".py"):
                ast.parse(text, filename=path)
                parsed["python"] += 1
        except Exception as exc:
            errors.append((path, type(exc).__name__, str(exc)))
    print(f"parsed={parsed} errors={errors}")
    PY

Output:

    parsed={'json': 2, 'yaml': 11, 'python': 4} errors=[]

Shell-syntax command:

    rtk bash -n scripts/init.sh scripts/doctor.sh

Output: none; exit status 0.

Mode command:

    rtk git ls-tree 0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf scripts/init.sh scripts/doctor.sh

Output:

    100755 blob c5fe105b690fe56abfafbf578dbca595ade27f14	scripts/doctor.sh
    100755 blob 5c91d0b2ccc8b42ce52d3a670e88fa9e08b4db7f	scripts/init.sh

### Buzz dry-run actions and seed identity

Command:

    rtk python3 - <<'PY'
    import collections
    import json
    import re
    import subprocess

    source = "0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf"
    config = json.loads(subprocess.check_output(
        ["git", "show", f"{source}:buzz/community.json"], text=True
    ))
    dry_run = json.loads(subprocess.check_output(
        ["python3", "scripts/buzz_bootstrap.py", "--dry-run"], text=True
    ))
    actions = dry_run["actions"]
    action_counts = dict(collections.Counter(
        action["action"] for action in actions
    ))
    forbidden_names = {
        "delete", "archive", "remove_member", "add_member",
        "schedule", "create_workflow"
    }
    forbidden = sorted({
        action["action"] for action in actions
        if action["action"] in forbidden_names
    })
    markers = {}
    counts = {}
    for channel in config["channels"]:
        path = channel["seed"]
        text = subprocess.check_output(
            ["git", "show", f"{source}:{path}"], text=True
        )
        found = re.findall(r"<!--\s*(practice-seed:[^>\s]+)\s*-->", text)
        counts[path] = len(found)
        if found:
            markers[path] = found[0]
    print(
        f"mode={dry_run['mode']} channels={len(config['channels'])} "
        f"stream={sum(c['type'] == 'stream' for c in config['channels'])} "
        f"open={sum(c['visibility'] == 'open' for c in config['channels'])} "
        f"private={sum(c['visibility'] == 'private' for c in config['channels'])}"
    )
    print(
        f"actions={len(actions)} action_counts={action_counts} "
        f"forbidden_actions={forbidden}"
    )
    print(
        f"seed_files={len(counts)} unique_markers={len(set(markers.values()))} "
        f"one_per_seed={all(count == 1 for count in counts.values())}"
    )
    PY

Output:

    mode=dry-run channels=12 stream=12 open=10 private=2
    actions=60 action_counts={'ensure_channel': 12, 'set_topic': 12, 'set_purpose': 12, 'set_canvas': 12, 'seed_if_marker_missing': 12} forbidden_actions=[]
    seed_files=12 unique_markers=12 one_per_seed=True

### Placeholder, publication-token, and secret scans

Public-root placeholder command:

    rtk rg -n -i '\b(TODO|TBD|PLACEHOLDER|LOREM IPSUM)\b' docs community guides practices labs stories content ops release brand

Output:

    ops/FIRST_PRACTICE_SESSION.md:106:   Practitioner may replace every real detail with a category or placeholder.
    ops/outreach/SOCIAL_KIT.md:5:format. Replace every bracketed placeholder before publishing.

Publication-token command:

    rtk python3 - <<'PY'
    import collections
    import re
    import subprocess

    source = "0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf"
    files = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", source], text=True
    ).splitlines()
    roots = (
        "docs/", "community/", "guides/", "practices/", "labs/",
        "stories/", "content/", "ops/", "release/", "docs/style/"
    )
    token_re = re.compile(r"\[[@#]?[A-Z][A-Z0-9_ -]*\](?!\()")
    tokens = collections.Counter()
    for path in files:
        if not path.endswith(".md") or not path.startswith(roots):
            continue
        text = subprocess.check_output(
            ["git", "show", f"{source}:{path}"], text=True
        )
        tokens[path] += len(token_re.findall(text))
    tokens = {path: count for path, count in tokens.items() if count}
    print(
        f"publication_token_occurrences={sum(tokens.values())} files={tokens}"
    )
    PY

Output:

    publication_token_occurrences=27 files={'ops/outreach/SOCIAL_KIT.md': 26, 'practices/001-context-pack.md': 1}

The social publication hold covers its 26 occurrences. The other raw occurrence
is the fenced date example in the context-pack record template; corrected
release validation strips code examples before applying the token rule.

Known-format secret command:

    rtk git grep -n -E 'AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----' 0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf -- .

Output: none; exit status 1, meaning no match.

Secret-assignment heuristic command:

    rtk git grep -n -E '(PRIVATE_KEY|TOKEN|SECRET|PASSWORD)[[:space:]]*=' 0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf -- .

Output:

    0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf:.env.example:3:BUZZ_PRIVATE_KEY=
    0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf:buzz/BOOTSTRAP_RUNBOOK.md:22:BUZZ_PRIVATE_KEY='local-identity-key' \

### File index coverage

Command:

    rtk python3 - <<'PY'
    import subprocess

    source = "0ec7ad9e6ad1b152a68e2b7f53fa12dbcecf7ccf"
    files = set(subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", source], text=True
    ).splitlines())
    index = subprocess.check_output(
        ["git", "show", f"{source}:swarm/README.md"], text=True
    )
    tick = chr(96)
    listed = {
        line[3:-1]
        for line in index.splitlines()
        if line.startswith("- " + tick) and line.endswith(tick)
    }
    print(
        f"tracked={len(files)} indexed={len(listed)} "
        f"listed_missing={len(listed - files)} "
        f"tracked_absent_from_index={len(files - listed)}"
    )
    PY

Output:

    tracked=245 indexed=134 listed_missing=0 tracked_absent_from_index=111

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
