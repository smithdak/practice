# Buzz Bootstrap Runbook

The bootstrapper is dry-run-first and non-destructive.

```bash
python3 scripts/buzz_bootstrap.py --dry-run
```

To apply, export the owner relay URL and owner private key only in Dakota's local shell. Do not paste either into Buzz or a worker prompt.

```bash
set -a
. ./.env
set +a
python3 scripts/buzz_bootstrap.py --apply
```

The script:

- creates missing stream channels;
- sets topic and purpose;
- replaces each channel canvas with the canonical file;
- posts a seed only when its marker is absent from recent history;
- writes a local report;
- never deletes, archives, creates agents, or creates workflows.

After apply, inspect every channel in Buzz Desktop. Manual recovery consists of correcting the canonical file and re-running apply. Destructive rollback is intentionally not automated.
