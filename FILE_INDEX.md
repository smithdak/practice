# Retired construction file index

This hand-maintained inventory is retired because it became incomplete as the
repository grew. Do not use it to infer release contents, task completion, or
artifact status.

Use these reproducible sources instead:

- `git ls-files` for the exact files in a candidate commit;
- `tasks/manifest.json` for task specifications, dependencies, owned outputs,
  and handoff paths; and
- `python3 scripts/validate.py --release` for committed completion evidence.

The `status` fields in `tasks/manifest.json` are construction-era defaults and
are not authoritative. The task controller uses ignored `.swarm/state.json` as
ephemeral local orchestration state; release validation deliberately does not.
