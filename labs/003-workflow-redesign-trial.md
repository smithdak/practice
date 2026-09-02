---
artifact_type: lab
title: "Mechanize two claim-audit defect classes with a stdlib checker"
summary: "First recorded trial of Practice 002: the six-class publishability claim audit is redesigned into deterministic, AI-assisted, and human-owned steps, and a stdlib checker is measured against the manual audit's recorded verdicts for the placeholder and license-frontmatter classes on the same file corpus."
status: completed
primary_capability: automate
roles: [individual-practitioner, operator]
task_set_version: 0.1.0
run_count: 2
result_status: complete
last_run: 2026-09-01
version: 0.1.0
license: CC-BY-4.0
created: 2026-09-01
updated: 2026-09-01
---

# Mechanize two claim-audit defect classes with a stdlib checker

This Lab records the first trial of [Practice 002](../practices/002-workflow-redesign.md) (redesign a recurring workflow) on a real workflow in this repository: the six-class publishability claim audit that worker R4 executed manually on 2026-09-01 across all publishable artifacts (recorded in [reviews/CLAIM_AUDIT.md](../reviews/CLAIM_AUDIT.md) and `swarm/handoffs/R4.md`). The trial redesigns that workflow into deterministic, AI-assisted, and human-owned steps, then executes the deterministic slice: a Python-stdlib checker for defect class 6 (placeholder text) and class 4 (license-metadata mismatch), compared against R4's recorded manual verdicts. Classes 1, 2, 3, and 5 were not measured; the human review checkpoint was designed but not executed.

## Question

For the two defect classes a fixed rule can express — class 6 (placeholder text and unresolved bracketed tokens) and class 4 (front-matter license vs. repository content default) — does a frozen stdlib checker reproduce R4's per-file manual verdicts across R4's 68-file corpus, and what does the disagreement behavior of the first checker revisions reveal about the cost of mechanizing this workflow?

## Hypothesis

Predeclared before the included runs: with the documented masking policy and exception data encoded, the checker reports zero findings for classes 4 and 6, agreeing with R4's recorded all-clean verdicts on 68 of 68 reference files per class. Any disagreement is treated as a defect in the operational definition (checker logic or exception encoding), not as a corpus finding, and blocks acceptance until individually explained. Secondary expectation: both sweeps complete in a single process in under 5 seconds.

## Variables

| Type | Definition | Measurement |
|---|---|---|
| Independent variable | Audit method for the two mechanized classes: R4's manual full-read plus ad-hoc regex sweeps (2026-09-01) versus the frozen E2 stdlib checker v0.3/v0.4. | Recorded per run in the ledger. |
| Primary outcome | Per-file verdict agreement between checker and R4's recorded verdict, per class. | Files where the checker verdict equals the R4 reference verdict, divided by the 68 reference files. R4's reference verdict for classes 4 and 6 is clean for every reference file. |
| False-finding outcome | Checker flags a file R4 recorded clean. | Counted per run; each is diagnosed to a named cause. |
| Missed-finding outcome | R4 records a class-4/6 finding the checker misses. | Zero available by construction: R4 recorded no class-4 or class-6 findings, so this measure cannot distinguish "checker perfect" from "checker shares R4's blind spots." |
| Policy self-check outcomes | SOCIAL_KIT exception token counts; front-matter inventory count. | Checker reports per-token counts (must equal the documented exception exactly) and the list of front-matter files (R4 claims exactly six). |
| Uncontrolled confounders | R4's verdicts are a single AI-worker pass, not an independent human reference; exception data was transcribed from R4's prose, so agreement is partially circular; the shared worktree changed during the trial (a new `labs/` file appeared between runs); checker revisions occurred mid-trial. | Recorded in the ledger and in Observed failure modes; not claimed eliminated. |

## Fixed conditions

- Repository commit `6f205d6` (worktree). The trial modified no repository file; the checker and all outputs live outside the repository.
- Corpus definition identical to R4's scope: all `*.md` under `docs/founding/`, `docs/framework/`, `community/`, `guides/` (including `guides/ai-native-practitioner/`), `practices/`, `labs/`, `stories/`, `buzz/canvases/`, `buzz/seeds/`, `content/launch/`, `ops/`, `release/`, `docs/style/`, plus root `README.md` — 68 files at the reference commit. The comparison set is pinned to these 68 files.
- Python 3.12.3, standard library only, offline, read-only; one process per run.
- Masking policy: fenced code blocks and inline code spans are masked before scanning, matching `scripts/check_links.py` and the Q004-RI-04 gate behavior documented in `swarm/reports/PHASE1_REPORT.md`.
- Exception data version: the SOCIAL_KIT whole-file bracket-token exception with per-token counts transcribed from `reviews/CLAIM_AUDIT.md` (26 tokens total; per-token counts in the checker source below).
- One run = one full checker execution over the enumerated corpus, producing verdicts for both mechanized classes. Two included runs (T3, T4); two earlier defective runs (T1, T2) excluded and retained per the rerun rule in **Procedure**.
- Design transparency: corpus reconnaissance informed the checker design before the formal runs; the hypothesis and decision thresholds were fixed before the included runs, and the two excluded runs are part of the record.

## Task set

### The workflow under trial

**Trigger:** the Director assigns a publishability re-audit before launch. **Owner:** the audit worker (R4). **Outcome:** a findings checklist over every publishable artifact. **Boundary:** read-only; remediation and publication decisions stay with the owner.

**Current workflow, as R4 actually ran it** (reconstructed from `reviews/CLAIM_AUDIT.md` "Method and limitations" and `swarm/handoffs/R4.md`):

| ID | Step | Actor | As-run classification | Control in the record |
|---|---|---|---|---|
| B1 | Receive task: six defect classes, 68-file corpus, acceptance criteria | Director → worker | Human-owned (delegation) | Task specification |
| B2 | Enumerate the 68-file corpus | R4 (AI worker) | AI-assisted (deterministic in nature, done by hand) | Count stated in report |
| B3 | Full read / line-audit of every file against the six classes | R4 | AI-assisted | Single pass, no independent reference |
| B4 | Ad-hoc regex sweeps (metric patterns, attributed speech, vendor terms, URLs/emails, license fields, dates, marker words, bracketed tokens) | R4 | Deterministic operations executed agentically; commands not preserved | Results asserted in prose; not re-runnable |
| B5 | Direct-inspection verifications (SOCIAL_KIT token count = 26; `buzz/community.json` channels = 12; validator control check on task Q005) | R4 | Deterministic checks executed by hand | Counts recorded in report |
| B6 | Exception judgment calls (founder first name = intentional public identity; template fill-in fields are not placeholders; stale review dates are out of class) | R4 | Human-equivalent judgment performed by an AI worker | Documented as decisions for later human review |
| B7 | Write `reviews/CLAIM_AUDIT.md` (verdict table, findings checklist, clean-file list) | R4 | AI-assisted | Director and Q-wave review after the fact |
| B8 | Run `scripts/validate.py` (task unwired: fails) plus control check | R4 | Deterministic | Recorded in handoff |
| B9 | Commit; Director review; owner remediation decision on the one finding | Director / owner | Human-owned | `release/OWNER_REVIEW.md` gates |

**Observed weakness that motivates the redesign:** the class-4 and class-6 verdicts in B4/B5 are deterministic in nature but exist only as asserted results; re-running the audit after any content edit requires a full manual redo (R4's own recorded deferral).

**Redesigned workflow** (per Practice 002 steps 3–5; deterministic first, AI-assisted only with review, consequential effects human-owned):

| ID | Step | Proposed class | Review checkpoint (before any effect) | Stop condition / rollback |
|---|---|---|---|---|
| W1 | Corpus enumeration and inventory (file list, front-matter inventory, content-default anchor) | Deterministic script | Runner confirms the file count against the pinned corpus manifest | Read-only; rerun |
| W2 | Class-6 sweep: marker words and unresolved bracketed tokens under the masking policy, with the versioned exception list and its count self-check | Deterministic script | Exception data is human-owned; any count mismatch fails loudly instead of reporting clean | Read-only; revert exception file |
| W3 | Class-4 sweep: front-matter license parity against the `LICENSE-CONTENT.md` content default | Deterministic script | — | Read-only |
| W4 | Candidate-signal extraction for classes 1/2/3/5 (URL list, attributed-speech patterns, number inventory, credential-shaped strings) | Deterministic script (proposed; not built in this trial) | — | Read-only |
| W5 | AI-assisted triage of classes 1/2/3/5 over W4 signals; every output is a *proposal* | AI-assisted | Human reviews each proposal before it is used | Discard draft; revert to manual audit |
| W6 | Human-owned findings review: accept, reject, or remediate each finding | Human-owned | Named reviewer decides per finding before any repo edit | Reject restores pre-trial state |
| W7 | Human-owned publication decision | Human-owned | Existing `release/OWNER_REVIEW.md` gates; checker verdicts are input, never the decision | Existing gate process |

**Classification of the six defect classes in the redesign:**

| Class | Redesigned owner | Why |
|---|---|---|
| 1 — Third-party content / misattribution | AI-assisted triage → human review (W5→W6) | Attribution adequacy is judgment; script can only surface URL/quote candidates |
| 2 — Invented metrics / quotes | AI-assisted triage with script-supplied number inventory → human review | Verifiability judgment; the deterministic inventory bounds the AI pass |
| 3 — Unlabeled hypotheticals | AI-assisted triage → human review | Context judgment about whether text reads as a claim |
| 4 — License-metadata mismatch | Deterministic script (W3) | Fixed rule against a declared default |
| 5 — Secrets / PII / private references | Deterministic shape screen + AI-assisted triage → human review | Regexes catch credential shapes; "intentional public identity" calls stay human (R4's founder-name decision) |
| 6 — Placeholders / unresolved tokens | Deterministic script with versioned, human-owned exception data (W2) | Fixed rules; the exception list is a publication-policy judgment encoded as data |

**Human checkpoint — designed, NOT executed in this trial.** The reviewer would see one page: (a) the checker verdict table per class with exception self-check results; (b) each AI-proposed finding as a row: `file:line`, class, exact quoted evidence, proposed remediation; (c) a diff of the exception list against the last run; (d) an explicit decision list (accept remediation / reject / defer). For the one live audit finding (`README.md:43`, class 5, the README advertising the machine-specific `swarm/README.md` runbook), the card would show R4's severity (low) and its two remediation options; the accept/waive decision remains with the owner per R4's handoff. No human executed this checkpoint for this trial; it is a design record only.

### Mechanized-class operational definitions

- **Class 6 (placeholders and unresolved tokens):** case-sensitive marker words `TODO`, `FIXME`, `TBD`, `XXX`, `LOREM IPSUM` at word boundaries, plus uppercase bracketed tokens with an optional `@`/`#` prefix inside the brackets (for example `[REPOSITORY_URL]`, `[@PRACTICE_HANDLE]`, `[#START_HERE_CHANNEL]`), excluding markdown link labels, all measured on text with fenced blocks and inline code spans masked. The SOCIAL_KIT whole-file token exception is encoded with per-token expected counts and must match exactly (26 total); any mismatch is reported as an exception-spec finding, never silently accepted.
- **Class 4 (license-metadata mismatch):** every corpus file beginning with front matter must declare `license: CC-BY-4.0` (the repository content default anchored in `LICENSE-CONTENT.md`); findings are missing license field, unknown license value, or a value different from the content default.

### Reference verdicts

R4 recorded zero findings for classes 4 and 6 across all 68 reference files (its single finding was class 5, not mechanized here). R4 also asserted two inventory facts the checker verifies mechanically: exactly six corpus files carry front matter, and SOCIAL_KIT retains exactly 26 bracketed tokens.

## Procedure

1. Map the current workflow from `reviews/CLAIM_AUDIT.md` and `swarm/handoffs/R4.md` (done; recorded above).
2. Classify steps and design the redesigned map with gates (done; recorded above).
3. Write the checker v0.1 in `/tmp/opencode` (not committed). Run it (run T1, 2026-09-01 ~17:09:00Z).
4. T1 disagreed with R4 on class 6. Diagnose the cause; revise the token regex (v0.2); rerun (run T2, 17:11:06Z). T2 disagreed again with a different count; diagnose again.
5. Revision rule applied after each disagreement: fix the named defect, add a pre-run unit check that reproduces the missed case (the full documented 26-token exception count), record the prior run as excluded, and rerun. Checker v0.3 passed the unit check before the formal run.
6. Execute the included runs: run T3 (checker v0.3, 17:11:43Z) and run T4 (checker v0.4, 17:13:30Z; same logic with the repository root taken from `argv` instead of a hard-coded path, so the published script contains no personal path). Each run executes both class sweeps once over the enumerated corpus and emits one JSON record.
7. Compare checker verdicts with R4's recorded verdicts for the 68 reference files; record agreement, false findings, and the sensitivity variant (marker scan without masking).
8. Record the concurrent-worktree observation and classify the new file's verdicts separately from the reference set.

## Evaluation rubric

- **Per-class agreement** = reference files where checker verdict equals R4's verdict / 68.
- **Critical mismatch** = any checker finding on a reference file R4 recorded clean without a diagnosable cause, or any missed reference finding (none available by construction).
- **Policy self-check** = exception token counts equal the documented exception exactly; front-matter inventory reconciles with R4's claim or the delta has a named cause.
- **Decision rule:** classes 4 and 6 may be proposed as deterministic pre-checks (with human-owned exception data) only at 100% agreement with all policy encodings documented; any critical mismatch forces revision of the operational definition, not acceptance of either verdict. This rubric never automates remediation or publication decisions.

## Cost capture

The included runs are deterministic local executions: no model requests, no billable usage, cost 0; no pricing source applies. Excluded from cost and time measures: R4's manual-audit labor (duration not recorded — labeled unknown rather than estimated, per Practice 002), E2 worker labor, and local compute. If the redesigned W5 AI-triage step is trialed later, its token usage and pricing source must be captured under this section's rules.

## Results

**Result status:** complete. Two included runs (T3, T4); two excluded defective runs (T1, T2) retained below. All runs on commit `6f205d6`, Python 3.12.3.

### Run ledger

| Run | Checker | UTC time (2026-09-01) | Corpus | Class-6 findings | Class-4 findings | Elapsed | Verdict vs R4 | Status |
|---|---|---|---|---|---|---|---|---|
| T1 | v0.1 (`sha256 c2d650b1…`) | ~17:09:00Z | 68 | 1 (exception-spec: 21/26 tokens) | 0 | 41.2 ms | Disagree (class 6) | Excluded — checker defect: `@`/`#` prefix matched outside the brackets |
| T2 | v0.2 (`sha256 840f609e…`) | 17:11:06Z | 68 | 1 (exception-spec: 1/26 tokens) | 0 | 39.6 ms | Disagree (class 6) | Excluded — checker defect: `@#?` written as literal `@` instead of the optional class `[@#]?` |
| T3 | v0.3 (`sha256 3fc05386…`) | 17:11:43Z | 68 | 0 | 0 | 41.5 ms | Agree, both classes | Included |
| T4 (canonical) | v0.4 (`sha256 dabf8f38…`) | 17:13:30Z | 69 (see below) | 0 | 0 | 41.5 ms | Agree on all 68 reference files | Included |

### Measured comparison for the two mechanized classes

| Measure | Class 6 (placeholders/tokens) | Class 4 (license front matter) |
|---|---|---|
| R4 reference verdicts (68 files) | all clean | all clean |
| Checker verdicts, T3 | 0 findings on 68 files | 0 findings; 6 front-matter files, all `CC-BY-4.0` |
| Agreement (T3) | 68/68 | 68/68 |
| Agreement (T4, reference subset) | 68/68 | 68/68 |
| Front-matter inventory vs R4's "six files" claim | — | T3: 6/6 match. T4: 7 found — the seventh is `labs/004-verification-gate-trial.md`, created concurrently by worker E3 between T3 and T4; explained delta, not a mismatch |
| SOCIAL_KIT exception self-check | T3/T4: per-token counts match the documented exception exactly (12/4/4 and six 1s = 26/26) | — |
| Elapsed time | 41.5 ms per run, both classes, one process | same process |

### Sensitivity observation (not an included run)

Removing the masking policy (scanning raw text for marker words) yields 3 extra hits in 1 file: `swarm/reports/PHASE1_REPORT.md:87`, where `TODO`, `TBD`, and `LOREM IPSUM` appear inside inline code describing the scan gate itself — prose about markers, not placeholder text. Without the masking policy the checker would report a one-file false positive against R4's verdict; the policy is load-bearing for agreement.

### Observed failure modes (mapped to Practice 002's hypotheses)

- **Transcription error, twice (T1, T2).** Encoding the prose exception spec into regexes failed twice with different defects; both were caught by comparison against the recorded reference, not by the checker itself. Had the checker been trusted without the comparison, the owner would have received a false "exception drift" alarm. This is the trial's most instructive result: mechanization without a human-reviewed reference ships confident false alarms.
- **Load-bearing implicit policy.** The masking rule existed only as repository convention (`scripts/check_links.py`, Q004-RI-04), not as audit-method documentation; a naive transcription of R4's sweep produces a false positive. Hidden conventions must be encoded and versioned as explicit policy data.
- **Shared-worktree drift.** The corpus changed mid-trial (68 → 69 files) because a concurrent worker created a new `labs/` file. A pinned corpus manifest or a commit-pinned clean-worktree precondition is required before the checker's verdicts can be trusted as a release gate.
- **Guarded, not observed:** approval-after-effect and no-usable-rollback did not occur — the trial is read-only, publishes nothing, and has nothing to roll back.

## Interpretation

Observed: under the encoded masking and exception policy, the checker reproduced R4's verdicts for both mechanized classes on all 68 reference files, in 41.5 ms, and mechanically verified two inventory facts R4 had asserted by hand (26/26 exception tokens; six front-matter files). Reaching agreement required two diagnosed checker revisions, both caught by the comparison.

Bounded inference: classes 4 and 6 are mechanically checkable by a stdlib script whose clean verdict is conditional on (a) the documented masking policy, (b) the versioned exception data passing its self-check, and (c) a pinned corpus. The redesigned W2/W3 steps are supported as re-runnable pre-checks; their clean output is an input to human review, not a publication decision.

Non-results: nothing was measured for classes 1, 2, 3, or 5; the AI-assisted triage step and the human checkpoint were designed but not executed. Agreement does not prove R4's audit correct — the checker's exception data was transcribed from R4's prose, so the two methods share provenance. No speed claim is possible (the manual audit's duration is unknown). Practice 002's maturity is unchanged; promotion remains a human decision.

## Limitations

- Single trial, one corpus, one commit; no repetition, no statistical claims.
- Two of six defect classes mechanized; classes 1/2/3/5 are unmeasured, including the live class-5 finding at `README.md:43`.
- The reference verdicts come from one AI-worker pass that no human has independently verified; the exception data's shared provenance makes agreement partially circular — the checker can reproduce R4's blind spots, not just its conclusions.
- The human review checkpoint was not executed; the "what the human would see" record is a design, not an observation.
- The masking and exception policies live as script data in `/tmp/opencode`, not as versioned repository artifacts; until promoted, they can drift from the prose they encode.
- The checker-defect rate (2 of 4 recorded runs) measures this trial's transcription risk only; it is not a model or tool benchmark.
- No elapsed-time baseline for the manual audit exists, so no speed or cost comparison is possible.

## Reproduction

Environment: Python 3.12.3, Linux, repository at commit `6f205d6` with the reference corpus (68 files listed in R4's scope). The trial edited no repository file. The checker is reproduced verbatim below; save it outside the repository (for example `/tmp/opencode/e2_check.py`) and run `python3 e2_check.py <repo-root>` from anywhere. Its JSON output contains the verdicts, exception counts, sensitivity hits, elapsed time, and the checker's own sha256; compare `class6.finding_count` and `class4.finding_count` (expect 0) against the class-4/6 rows of `reviews/CLAIM_AUDIT.md`, and compare `class4.front_matter_files` against R4's six-file claim (allowing explained deltas from concurrent edits, as in run T4). Checker versions: v0.1 `c2d650b1…`, v0.2 `840f609e…`, v0.3 `3fc05386…`, v0.4 `dabf8f388d8b20e3f5c937a6f173ac47d2563f89f3505887273fb95c504c4705` (canonical).

```python
#!/usr/bin/env python3
"""E2 trial checker: deterministic sweeps for claim-audit classes 6 and 4.

First recorded trial of Practice 002 (redesign a recurring workflow) applied to
the R4 six-class publishability claim audit. Stdlib only, offline, read-only.

Mechanized classes:
- Class 6: TODO/FIXME/TBD/XXX/LOREM IPSUM markers and unresolved uppercase
  bracketed tokens, under the documented masking policy (fenced blocks and
  inline code spans are masked, matching scripts/check_links.py and the
  Q004-RI-04 gate behavior) and the documented SOCIAL_KIT token exception
  (counts must match the exception spec exactly).
- Class 4: front-matter license fields must equal the repository content
  default (CC-BY-4.0) anchored in LICENSE-CONTENT.md.

Not mechanized here (remain AI-assisted + human review): classes 1, 2, 3, 5.
"""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
CORPUS_DIRS = (
    "docs/founding", "docs/framework", "community", "guides", "practices",
    "labs", "stories", "buzz/canvases", "buzz/seeds", "content/launch",
    "ops", "release", "brand",
)
CONTENT_DEFAULT = "CC-BY-4.0"
KNOWN_LICENSES = {"CC-BY-4.0", "Apache-2.0"}

FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODE_SPAN_RE = re.compile(r"`+[^`\n]*`+")
MARKER_RE = re.compile(r"\b(TODO|FIXME|TBD|XXX|LOREM IPSUM)\b")
# Uppercase bracketed token with optional @/# prefix inside the brackets
# (e.g. [REPOSITORY_URL], [@PRACTICE_HANDLE], [#START_HERE_CHANNEL]);
# excludes markdown link labels ("[NOTICE](../NOTICE)") via the trailing
# "(!\s*\()" guard.
TOKEN_RE = re.compile(r"(?<!\w)\[[@#]?([A-Z][A-Z0-9_]*)\](?!\s*\()")
SOCIAL_KIT = "ops/outreach/SOCIAL_KIT.md"
SOCIAL_KIT_EXPECTED = {
    "[REPOSITORY_URL]": 12,
    "[#START_HERE_CHANNEL]": 4,
    "[BUZZ_URL]": 4,
    "[@PRACTICE_HANDLE]": 1,
    "[START_HERE_URL]": 1,
    "[DISCUSSION_URL]": 1,
    "[VERIFICATION_PRACTICE_URL]": 1,
    "[ISSUE_URL]": 1,
    "[CONTRIBUTING_URL]": 1,
}
SOCIAL_KIT_EXPECTED_TOTAL = 26

LICENSE_LINE_RE = re.compile(r"^license:\s*(.+?)\s*$")


def mask_code(text: str) -> str:
    masked_lines = []
    fence = ""
    for line in text.split("\n"):
        marker = FENCE_RE.match(line)
        if fence:
            masked_lines.append(" " * len(line))
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = ""
        elif marker:
            fence = marker.group(1)
            masked_lines.append(" " * len(line))
        else:
            masked_lines.append(line)
    return CODE_SPAN_RE.sub(lambda m: " " * len(m.group(0)), "\n".join(masked_lines))


def load_corpus():
    files = {}
    for dirname in CORPUS_DIRS:
        for path in sorted((ROOT / dirname).rglob("*.md")):
            rel = path.relative_to(ROOT).as_posix()
            files[rel] = path.read_text(encoding="utf-8", errors="replace")
    files["README.md"] = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")
    return files


def scan_lines(masked_text, fn):
    hits = []
    for i, line in enumerate(masked_text.split("\n"), 1):
        for hit in fn(line):
            hits.append({"line": i, "match": hit})
    return hits


def class6_scan(files):
    findings = []
    for rel, text in sorted(files.items()):
        masked = mask_code(text)
        marker_hits = scan_lines(masked, lambda line: [m.group(0) for m in MARKER_RE.finditer(line)])
        token_hits = []
        if rel != SOCIAL_KIT:
            token_hits = scan_lines(masked, lambda line: [m.group(0) for m in TOKEN_RE.finditer(line)])
        for hit in marker_hits:
            findings.append({"file": rel, "kind": "marker", **hit})
        for hit in token_hits:
            findings.append({"file": rel, "kind": "bracket_token", **hit})
    sk_masked = mask_code(files[SOCIAL_KIT])
    sk_counts = {}
    for m in TOKEN_RE.finditer(sk_masked):
        token = m.group(0)
        sk_counts[token] = sk_counts.get(token, 0) + 1
    exception_ok = sk_counts == SOCIAL_KIT_EXPECTED
    exception_detail = {
        "counts": sk_counts,
        "expected_total": SOCIAL_KIT_EXPECTED_TOTAL,
        "actual_total": sum(sk_counts.values()),
        "matches_documented_exception": exception_ok,
    }
    if not exception_ok:
        findings.append({"file": SOCIAL_KIT, "kind": "exception_spec_drift",
                         "line": 0, "match": json.dumps(sk_counts, sort_keys=True)})
    return findings, exception_detail


def class4_scan(files):
    findings = []
    front_matter_files = []
    for rel, text in sorted(files.items()):
        lines = text.split("\n")
        if not lines or lines[0].strip() != "---":
            continue
        front_matter_files.append(rel)
        license_value = None
        for line in lines[1:]:
            if line.strip() == "---":
                break
            m = LICENSE_LINE_RE.match(line)
            if m:
                license_value = m.group(1).strip()
        if license_value is None:
            findings.append({"file": rel, "kind": "front_matter_without_license_field",
                             "value": None})
        elif license_value not in KNOWN_LICENSES:
            findings.append({"file": rel, "kind": "unknown_license_value",
                             "value": license_value})
        elif license_value != CONTENT_DEFAULT:
            findings.append({"file": rel, "kind": "license_mismatch_vs_content_default",
                             "value": license_value})
    anchor_text = (ROOT / "LICENSE-CONTENT.md").read_text(encoding="utf-8", errors="replace")
    anchor_ok = "CC BY 4.0" in anchor_text and "Creative Commons Attribution 4.0" in anchor_text
    return findings, front_matter_files, anchor_ok


def unmasked_marker_sensitivity(files):
    extra = []
    for rel, text in sorted(files.items()):
        for i, line in enumerate(text.split("\n"), 1):
            for m in MARKER_RE.finditer(line):
                extra.append({"file": rel, "line": i, "match": m.group(0)})
    return extra


def main():
    started = time.perf_counter()
    files = load_corpus()
    c6_findings, exception_detail = class6_scan(files)
    c4_findings, front_files, anchor_ok = class4_scan(files)
    sensitivity_extra = unmasked_marker_sensitivity(files)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout.strip()
    script_text = Path(__file__).read_text(encoding="utf-8")
    result = {
        "trial": "E2 Practice 002 first recorded trial (claim-audit redesign)",
        "repo_commit": commit,
        "python": sys.version.split()[0],
        "corpus_file_count": len(files),
        "elapsed_ms": elapsed_ms,
        "class6": {
            "findings": c6_findings,
            "finding_count": len(c6_findings),
            "files_scanned": len(files),
            "clean_files": len(files) - len({f["file"] for f in c6_findings}),
            "social_kit_exception": exception_detail,
        },
        "class4": {
            "findings": c4_findings,
            "finding_count": len(c4_findings),
            "files_scanned": len(files),
            "front_matter_files": front_files,
            "front_matter_file_count": len(front_files),
            "content_default_anchor_ok": anchor_ok,
        },
        "sensitivity_unmasked_marker_extra_hits": sensitivity_extra,
        "script_sha256": hashlib.sha256(script_text.encode("utf-8")).hexdigest(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

To repeat the comparison: run the checker, then verify (a) both `finding_count` fields are 0, (b) the SOCIAL_KIT exception self-check reports `matches_documented_exception: true` with the per-token counts above, (c) the front-matter inventory reconciles against R4's six files plus any explained concurrent additions. Any nonzero count is a finding for human review, not an automatic remediation trigger.

## Changelog

- 2026-09-01 — `0.1.0`: Created the Lab with the workflow redesign maps, classification, and the completed first comparison trial (runs T1–T4; two excluded checker-defect runs retained; two included runs agreeing with the manual audit on both mechanized classes).