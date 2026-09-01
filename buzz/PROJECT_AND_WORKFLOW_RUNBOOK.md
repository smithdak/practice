# Buzz Project and workflow pilot

Use this runbook to make the existing Practice repository discoverable as a
Buzz Project and to test one bounded workflow in `foundry`. The Project setup
is durable workspace metadata; it does not promote this repository—or any
other repository—to a maintained **Project** under Practice's contribution
model.

The Project and workflow are independent. Do not delay launch if the workflow
pilot is skipped or fails.

## Owner boundary

Every Buzz write below must be run by the same human-controlled identity in
the owner's local shell. The identity that invokes `buzz repos create` signs
the repository announcement, and Project edits are owner-only. Do not give an
owner key to an agent, paste it into Buzz, add it to command history, or commit
it. Use the local credential procedure in
[the bootstrap runbook](BOOTSTRAP_RUNBOOK.md).

This agent-prepared runbook does not authorize an agent to execute the writes.
The human operator must review the resolved relay, identity, channel UUIDs,
and command arguments before continuing.

## Resolve the two channels

First confirm that the canonical stream channels exist. Run the bootstrap dry
run before any hosted change:

```bash
python3 scripts/buzz_bootstrap.py --dry-run
buzz channels list --member
```

From the JSON output, copy the UUID for open `projects` and private `foundry`.
Set non-secret shell variables and inspect them before continuing:

```bash
export PROJECTS_CHANNEL_ID='<projects-channel-uuid>'
export FOUNDRY_CHANNEL_ID='<foundry-channel-uuid>'
```

Stop if either name, UUID, type, or visibility differs from
[`buzz/community.json`](community.json). Channel names are not accepted in
place of UUIDs. Do not put identity material into these variables.

## Create the Buzz Project container

### Intended shape

- Repository announcement ID: `practice`
- Display name: `Practice`
- Canonical clone URL: `https://github.com/smithdak/practice.git`
- Canonical web URL: `https://github.com/smithdak/practice`
- Project slug: `practice`
- Project channel: the open `projects` stream
- Project visibility: `listed`

The repository announcement deliberately has no `--channel` argument. On the
current Buzz protocol, a repository's `buzz-channel` is its Git access-control
binding. Practice continues to use GitHub permissions and review as the
canonical repository control, so this setup must not grant Buzz Git access to
everyone in the open `projects` channel. The Project's own `--channel` is only
discussion metadata and does not change member-repository authority.

### Preflight

Read the current signer's objects before creating anything:

```bash
buzz repos list --limit 100
buzz projects get practice
buzz projects list --limit 100
```

Proceed only when the current signer has neither a `practice` repository
announcement nor a `practice` Project. A `null` or not-found response is an
expected empty result. If either object exists, compare it with the intended
shape. Treat an exact match as complete; stop for human review on any mismatch.
Do not create a second object under another identity and do not delete an
existing object as a shortcut.

### Apply

Create the repository announcement first. This publishes a signed event to the
selected relay:

```bash
buzz repos create \
  --id practice \
  --name 'Practice' \
  --description 'Open community for AI practitioners; durable public artifacts live in Git.' \
  --clone 'https://github.com/smithdak/practice.git' \
  --web 'https://github.com/smithdak/practice'
```

Before publishing the Project, run `buzz repos list --limit 100` and verify the
new announcement against the intended shape, including the absence of a
channel binding. Stop if the response is missing or different.

Then publish the Project container:

```bash
buzz projects create \
  --repo practice \
  --name 'Practice' \
  --description 'Practice community workspace and its canonical public Git repository.' \
  --channel "$PROJECTS_CHANNEL_ID" \
  --visibility listed \
  practice
```

### Verify

```bash
buzz repos list --limit 100
buzz projects get practice
buzz projects list --limit 100
```

Accept the Project setup only when all of the following are visible in the CLI
response:

- the current identity owns repository announcement `practice`;
- its clone and web URLs exactly match the canonical GitHub URLs;
- the repository announcement has no `buzz-channel` binding;
- Project `practice` contains that repository, is `listed`, and references the
  resolved `projects` UUID; and
- the repository and Project descriptions do not claim release status,
  adoption, or maintained-Project acceptance.

Inspect the Project in Buzz Desktop as a secondary check. The CLI response is
the required evidence when a Desktop list is incomplete.

## Run the private workflow pilot

The pilot tests only a webhook definition, one manual trigger, and one
`send_message` action in the private `foundry` stream. It excludes schedules,
public channels, forum roots, direct messages, reactions, topic changes,
external webhooks, approval gates, agent mentions, and secrets.

The canonical definition at
[`buzz/workflows/manual-smoke-test.yaml`](workflows/manual-smoke-test.yaml)
starts with `enabled: false`. Keep that file disabled in Git.

### Preflight and create disabled

```bash
buzz workflows list --channel "$FOUNDRY_CHANNEL_ID"
buzz workflows create \
  --channel "$FOUNDRY_CHANNEL_ID" \
  --yaml - \
  < buzz/workflows/manual-smoke-test.yaml
```

Copy the returned `workflow_id` into a non-secret shell variable:

```bash
export WORKFLOW_ID='<workflow-uuid>'
buzz workflows get --workflow "$WORKFLOW_ID"
buzz workflows list --channel "$FOUNDRY_CHANNEL_ID"
```

Do not create another definition if the response is delayed or the Desktop
list looks empty. Wait for the single-channel CLI `get` or `list` response. If
a workflow with the same name already exists, stop and have its signing human
confirm its ID and disabled state.

### Enable, trigger once, and disable

Create a temporary enabled copy. The diff must change only the `enabled` line:

```bash
sed 's/^enabled: false$/enabled: true/' \
  buzz/workflows/manual-smoke-test.yaml \
  > /tmp/practice-buzz-workflow-smoke-test.enabled.yaml
diff -u \
  buzz/workflows/manual-smoke-test.yaml \
  /tmp/practice-buzz-workflow-smoke-test.enabled.yaml
```

Enable the existing definition, verify it, wait at least two seconds between
signed writes, and trigger it exactly once:

```bash
buzz workflows update \
  --channel "$FOUNDRY_CHANNEL_ID" \
  --workflow "$WORKFLOW_ID" \
  --yaml - \
  < /tmp/practice-buzz-workflow-smoke-test.enabled.yaml
buzz workflows get --workflow "$WORKFLOW_ID"
sleep 2
buzz workflows trigger \
  --workflow "$WORKFLOW_ID" \
  --inputs '{"pilot":"practice-foundry-manual-smoke-test"}'
sleep 2
buzz messages get --channel "$FOUNDRY_CHANNEL_ID" --limit 20
```

Whether the trigger succeeds or fails, restore the disabled canonical
definition before investigating anything else:

```bash
buzz workflows update \
  --channel "$FOUNDRY_CHANNEL_ID" \
  --workflow "$WORKFLOW_ID" \
  --yaml - \
  < buzz/workflows/manual-smoke-test.yaml
buzz workflows get --workflow "$WORKFLOW_ID"
```

Accept the pilot only when exactly one labeled smoke-test message is visible in
`foundry` and the final `get` response contains `enabled: false`. An empty
`buzz workflows runs` response is not evidence of failure or success; current
CLI source says run history is not emitted as queryable events. Do not retry a
trigger merely because run history is empty.

Leave the tested workflow disabled. Do not use deletion as rollback: current
issue reports describe accepted deletes that remain visible or active. If the
disabled update cannot be verified, stop all triggering, preserve the
workflow ID, and use official Buzz support. Do not test in an open channel.

## Promotion rule

The pilot does not authorize a production workflow. Consider a follow-up only
after a human repeats the test on the actual hosted relay and can verify
definition discovery, enable/disable behavior, the intended action, and an
observable failure path. Scheduled workflows remain outside the launch
critical path even if this manual pilot passes.

## Sources and evidence limits

Checked 2026-09-01:

- [Buzz CLI end-to-end workflow examples](https://github.com/block/buzz/blob/main/crates/buzz-cli/TESTING.md#69-workflows)
  document the YAML shape and create, get, update, trigger, list, and delete
  commands.
- [Buzz workflow schema](https://github.com/block/buzz/blob/main/crates/buzz-workflow/src/schema.rs)
  defines `enabled: false`, webhook triggers, and `send_message`.
- [Buzz workflow CLI source](https://github.com/block/buzz/blob/main/crates/buzz-cli/src/commands/workflows.rs)
  states that `runs` currently returns no execution events.
- [Buzz NIP-MP](https://github.com/block/buzz/blob/main/docs/nips/NIP-MP.md)
  defines Project ownership, repository membership, channel metadata, and the
  lack of authority over member repositories.
- [Buzz repository owner-signing issue](https://github.com/block/buzz/issues/5052)
  records that CLI repository creation is signed by the invoking identity and
  that an owner-reviewed draft flow was not available in the reviewed client.
- [Buzz workflow lifecycle report](https://github.com/block/buzz/issues/6116)
  records listing and deletion failures and recommends an explicit disabled
  webhook definition as a recovery state.
- [Buzz workflow action report](https://github.com/block/buzz/issues/4865)
  records incomplete or failing actions beyond `send_message` and the lack of
  visible run errors.
- [`research/BUZZ_PLATFORM_SNAPSHOT.md`](../research/BUZZ_PLATFORM_SNAPSHOT.md)
  remains the repository's launch-boundary source.

The locally installed CLI help was also checked for every command shown here
on 2026-09-01. The CLI exposes no `--version` option, and no live hosted relay
write was performed while preparing this runbook. Recheck command help and the
linked primary sources before execution if the installed client changes.
