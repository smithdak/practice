# Buzz Bootstrap Runbook

Use the bootstrapper to reconcile the stream channels in `buzz/community.json` with their canonical topic, purpose, canvas, and first seed message. It only uses the launch-safe Buzz CLI commands recorded in [the platform snapshot](../research/BUZZ_PLATFORM_SNAPSHOT.md).

## Before applying

1. Review the intended channel content in `buzz/community.json`, `buzz/canvases/`, and `buzz/seeds/`.
2. Run the credential-free plan. This is the required first step before every apply and does not require Buzz to be installed.

```bash
python3 scripts/buzz_bootstrap.py --dry-run
```

3. Confirm the target relay and that the local identity is authorized to create and update the listed channels. Keep the owner private key in the owner's local shell only; do not paste it into Buzz, commits, or agent prompts.

## Apply

`--apply` is required for any change. Export the relay and identity key only for the local command session, then run:

```bash
BUZZ_RELAY_URL='https://relay.example' \
BUZZ_PRIVATE_KEY='local-identity-key' \
python3 scripts/buzz_bootstrap.py --apply
```

The example values are placeholders. The script requires non-empty `BUZZ_RELAY_URL` and `BUZZ_PRIVATE_KEY`, verifies that the `buzz` CLI is available, and emits a JSON report to standard output. It does not write a report file, so relay context and credentials are not persisted by this tool. Error output redacts known credential values and common credential assignments.

The apply operation is limited to:

- creating a missing `stream` channel with its configured visibility;
- setting its topic, purpose, and canonical canvas;
- reading the most recent 100 messages; and
- sending a seed only if its `practice-seed:` marker is absent from that history.

It never deletes, archives, removes members, creates workflows, or automates forum root posts. Re-running apply updates the canonical metadata and canvas, but it will not repeat a seed when its marker is present in recent history. To reconcile metadata and canvases without messages, use `--skip-seeds`.

## Inspect and manual rollback

Review the JSON result and inspect every affected channel in Buzz: channel identity and visibility, topic, purpose, canvas, and the seed marker/message. The bootstrapper has no destructive rollback path by design.

If an apply needs correction, stop automated changes, have a maintainer review the affected channel, correct the canonical repository file if appropriate, and make the smallest manual change needed in Buzz. Re-run dry-run and then apply only after that review. Do not use deletion, archiving, or automated rollback as recovery mechanisms.

## Failure handling

The script stops on the first actionable failure and reports the operation that failed without printing credential values. Typical actions are:

- **Missing credentials or CLI:** set both required environment variables in the local shell and install or point `BUZZ_CLI` at the Buzz executable.
- **Channel ID cannot be resolved:** inspect the existing channel in Buzz; the script will not guess an ID.
- **Create conflict:** the script re-lists channels once to allow for a concurrent successful bootstrap; if the channel still is not discoverable, inspect permissions or the relay response.
- **Missing or malformed canonical file:** restore or correct the referenced canvas/seed file and run dry-run again.
- **Seed unexpectedly repeated:** stop, inspect the channel history and marker, and resolve manually. Marker-based detection is intentionally bounded to the latest 100 messages.
