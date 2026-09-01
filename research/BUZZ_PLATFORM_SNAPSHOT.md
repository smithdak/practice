# Buzz Platform Snapshot

**As of:** 2026-09-01  
**Purpose:** Prevent construction agents from inventing or depending on unstable Buzz capabilities.

## Changes since 2026-08-31

- All four primary sources were re-fetched successfully on 2026-09-01; every capability claim below was re-verified against them and none required removal.
- Issue [#6116](https://github.com/block/buzz/issues/6116) (desktop Workflows screen showing "No workflows yet" despite existing workflows) is now closed via linked PR [#6168](https://github.com/block/buzz/pull/6168). It no longer supports the workflow exclusions; the scheduled-workflows exclusion rests on [#5611](https://github.com/block/buzz/issues/5611), which remains open.
- Issues [#5611](https://github.com/block/buzz/issues/5611), [#4864](https://github.com/block/buzz/issues/4864), [#5043](https://github.com/block/buzz/issues/5043), [#5075](https://github.com/block/buzz/issues/5075), and [#5268](https://github.com/block/buzz/issues/5268) remain open as of 2026-09-01.
- No new release since Buzz Desktop v0.5.20 (released 2026-08-26), so no release-level changes occurred in the window.

## Verified current capabilities

Official sources state that Buzz currently provides:

- Block-hosted or self-hosted communities;
- channels, threads, direct messages, canvases, media, search, and audit history;
- voice huddles in the desktop app (the README still marks huddle lifecycle events as being wired up);
- first-class human and agent identities;
- a JSON-in/JSON-out `buzz` CLI;
- CLI creation and management of stream channels (`--type` accepts `stream` or `forum`; `--visibility` accepts `open` or `private`);
- CLI message sending, search, channel canvases, membership, repositories, memory, and workflows;
- ACP support for agent harnesses including Codex, Claude Code, and goose;
- Git-related events (NIP-34 patches, repo announcements, status) and a self-hostable relay (the README still marks the git hosting backend as being wired up).

Primary sources:

- https://github.com/block/buzz
- https://github.com/block/buzz/tree/main/crates/buzz-cli
- https://block.xyz/inside/introducing-buzz-where-humans-and-agents-work-together
- https://block.github.io/buzz/support.html

Deeper official documentation also used:

- https://github.com/block/buzz/blob/main/crates/buzz-cli/TESTING.md
- https://github.com/block/buzz/blob/main/CHANGELOG.md

## Hosted-community constraints

- Block-hosted communities are currently invite-only; a user cannot join by entering the relay URL without an invitation.
- Open channels are visible to people who have joined the community; they are not an unauthenticated public website.
- A hosted account can currently create up to three communities.
- Block-hosted communities are open to groups and individuals aged 18 and over.
- Community owners manage access and can remove users from their communities; Block operates the hosted service and handles service-wide rules.
- Buzz relays are not federated: relays do not share content, and a message stays on the relay where it was sent.
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

The official end-to-end test documentation shows `channels create` returning `channel_id` and `messages send` returning `event_id`, and demonstrates `canvas set` and `messages send` reading content from stdin:

- https://github.com/block/buzz/blob/main/crates/buzz-cli/TESTING.md

## Capabilities excluded from the critical path

### Scheduled workflows

An open issue reports scheduled workflows never firing on hosted relays (cron and interval), with manual triggers working and run history remaining empty even after a proven manual run. Workflow creation may still be useful experimentally, but it cannot block launch. A related desktop bug that showed an empty workflow list despite existing workflows was closed as fixed via PR #6168 and no longer supports this exclusion.

- https://github.com/block/buzz/issues/5611

### Workflow deletion and template interpolation

Open issues report deletion (`buzz workflows delete` returns `accepted` while list/get still return the workflow, and a later update can resurrect it) and template-interpolation defects (`{{variable}}` rendering literally in `send_message` despite declared inputs). The launch system therefore never creates workflows automatically and never assumes delete is reliable.

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
