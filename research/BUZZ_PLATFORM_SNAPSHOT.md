# Buzz Platform Snapshot

**As of:** 2026-08-31  
**Purpose:** Prevent construction agents from inventing or depending on unstable Buzz capabilities.

## Verified current capabilities

Official sources state that Buzz currently provides:

- Block-hosted or self-hosted communities;
- channels, threads, direct messages, canvases, media, search, and audit history;
- first-class human and agent identities;
- a JSON-in/JSON-out `buzz` CLI;
- CLI creation and management of stream channels;
- CLI message sending, search, channel canvases, membership, repositories, memory, and workflows;
- ACP support for agent harnesses including Codex, Claude Code, and goose;
- Git-related events and a self-hostable relay.

Primary sources:

- https://github.com/block/buzz
- https://github.com/block/buzz/tree/main/crates/buzz-cli
- https://block.xyz/inside/introducing-buzz-where-humans-and-agents-work-together
- https://block.github.io/buzz/support.html

## Hosted-community constraints

- Block-hosted communities are currently invite-only.
- Open channels are visible to people who have joined the community; they are not an unauthenticated public website.
- A hosted account can currently create up to three communities.
- Hosted-community storage limits were not final in the support documentation reviewed.
- Messages, direct messages, and uploaded media in Block-hosted communities are not end-to-end encrypted.

Planning consequence: Buzz remains the hub, but public open-source artifacts and discovery must also be available in Git and social channels.

## Launch-safe CLI surface

The bootstrapper may use:

```text
buzz channels list
buzz channels create --name <name> --type stream --visibility <open|private>
buzz channels topic --channel <uuid> --topic <text>
buzz channels purpose --channel <uuid> --purpose <text>
buzz canvas set --channel <uuid> --content -
buzz messages send --channel <uuid> --content -
buzz messages get --channel <uuid> --limit <n>
```

The official end-to-end test documentation shows `channels create` returning `channel_id` and `messages send` returning `event_id`.

## Capabilities excluded from the critical path

### Scheduled workflows

Open issues report scheduled workflows not firing on hosted relays and workflow lists appearing empty even when definitions exist. Workflow creation may still be useful experimentally, but it cannot block launch.

- https://github.com/block/buzz/issues/5611
- https://github.com/block/buzz/issues/6116

### Workflow deletion and template interpolation

Open issues report deletion and template-interpolation defects. The launch system therefore never creates workflows automatically and never assumes delete is reliable.

- https://github.com/block/buzz/issues/4864
- https://github.com/block/buzz/issues/5043

### Forum automation

Open issues report CLI root messages landing as invisible stream events in forum channels and agent mention gaps in forum subscriptions. Automated seeding uses stream channels only.

- https://github.com/block/buzz/issues/5075
- https://github.com/block/buzz/issues/5268

## Security rules

- Never commit `BUZZ_PRIVATE_KEY`.
- Never give the owner identity key to an agent.
- Give each agent its own identity and only required channel membership.
- Do not post client secrets, provider credentials, private repositories, or confidential business material into a hosted community.
- Run the bootstrapper in dry-run mode before every apply.
