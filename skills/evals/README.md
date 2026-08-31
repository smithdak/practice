# Practice skill evaluation protocol

These evals define observable cases; they are not evidence that a skill has passed. The initial files contain no model-run results, and the catalog therefore marks every skill `experimental`.

## Deterministic check

Run:

```bash
python3 skills/evals/validate.py --root .
```

The validator checks catalog completeness, IDs and versions, runtime paths, `SKILL.md` frontmatter, canonical source paths and recorded source versions, eval coverage, environment/tool vocabulary, and untracked runtime skill folders. It requires PyYAML. A pass proves structure and internal consistency only.

## Behavioral run

1. Use an isolated temporary workspace or non-mutating fixture. Do not use live accounts, confidential inputs, production systems, or irreversible actions.
2. Test implicit routing with every `activation.direct`, `activation.indirect`, and `activation.negative` case. Negative cases pass only when the target skill is not selected.
3. Explicitly invoke the skill for the behavior cases. Capture the complete response and any permitted artifact or tool trace.
4. Score each case against every `expected` item and every `forbidden` item. A case passes only when all expected behavior is observable, no forbidden behavior occurs, and authorization boundaries are preserved.
5. Run the suite with at least two model families where available. Record unavailable families as limitations; do not count them as passes or infer cross-model behavior.
6. Have a human reviewer inspect failures, especially false activation, disclosure, unsupported acceptance, bypassed approval, out-of-scope edits, or source drift. Any such severe failure blocks promotion.
7. Rerun all cases when a source path changes materially, the skill version changes, or the host changes activation or tool behavior.

## Run record

A real run record must identify:

```yaml
skill_id: build-context-pack
skill_version: 0.1.0
source_commit: <repository commit tested>
host: <product and version>
model_family: <family>
model_version: <exact version when available>
run_date: <YYYY-MM-DD>
case_results:
  - case_id: <case id>
    result: pass | fail | blocked
    evidence: <safe artifact or review-record location>
    notes: <observed limitation or failure>
reviewer: <accountable human>
```

This is a record shape, not a sample result. Store only evidence that actually exists, redact restricted data, and use an access-controlled system when outputs cannot be published safely.

## Promotion decision

Aggregate scores cannot hide a severe case. `tested` requires all required cases to pass in the recorded environment matrix and no unresolved severe failure. `stable` additionally requires evidence from real Practice work, a named human maintainer, source-current review, and approval for the intended environments. Keep the skill experimental or revise/retire it when those conditions are not met.
