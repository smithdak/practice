# Buzz

The hosted community hub. Buzz is the operating hub; Git is the durable truth
([docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)). Reusable Practices, Guides,
Labs, Stories, Notes, and Projects live in this repository; Buzz holds the
conversation, current context, questions, and routing.

The hub is not open. There is no public invitation route yet
([README.md](../README.md), project status), and owner gate 1, the community
address and relay, is OPEN in [the owner review packet](../release/OWNER_REVIEW.md).

## What is here

| File | What it holds | Open it when |
|---|---|---|
| [CHANNELS.md](CHANNELS.md) | The twelve launch channels (two private, ten open, all streams), the routing rules, and the create, rename, archive, and split lifecycle | Deciding where a conversation belongs, or proposing a channel change |
| [community.json](community.json) | The idempotent channel spec the bootstrapper applies: name, visibility, topic, purpose, and the canvas and seed path of each channel | Changing a channel. Update CHANNELS.md in the same change |
| [canvases/](canvases/) | One orientation canvas per channel | Editing what a member sees pinned in a channel |
| [seeds/](seeds/) | One first seed message per channel, applied once | Editing a channel's opening post |
| [agents/](agents/) | Five community-agent profiles, [registry.yaml](agents/registry.yaml) declaring each one's bounds, and [evals/](agents/evals/README.md) defining cases with no run recorded. Every status is `not_enabled`; owner gate 6 is OPEN | Reading what an agent may do before any is enabled |
| [PLATFORM_SNAPSHOT.md](PLATFORM_SNAPSHOT.md) | Verified Buzz capabilities and exclusions, with primary sources and an as-of date (2026-09-01) | Any assumption about what Buzz can do. Agents use this file, not memory |
| [BOOTSTRAP_RUNBOOK.md](BOOTSTRAP_RUNBOOK.md) | Dry-run-first reconciliation of the channels by `scripts/buzz_bootstrap.py`; the owner runs the apply | Preparing or running the bootstrapper |
| [PROJECT_AND_WORKFLOW_RUNBOOK.md](PROJECT_AND_WORKFLOW_RUNBOOK.md) | Owner-run setup of this repository as a Buzz Project (workspace metadata, not a Practice Project) and a disabled workflow pilot in `foundry` | Making the repository discoverable inside Buzz |
| [workflows/manual-smoke-test.yaml](workflows/manual-smoke-test.yaml) | One human-triggered workflow, `enabled: false` | Testing the bounded workflow path by hand |

Access, identity ownership, recovery, and the least-membership model for agents
are in [ops/BUZZ_SECURITY.md](../ops/BUZZ_SECURITY.md). The post-apply check
that the hosted surface matches `community.json` is
[release/HOSTED_INSPECTION.md](../release/HOSTED_INSPECTION.md).

## Rules

- Run `python3 scripts/buzz_bootstrap.py --dry-run` before every apply. Only
  the owner applies, from the owner's local shell.
- Launch uses stream channels and direct CLI seeding only. No forum automation
  and no scheduled workflows ([CHANNELS.md](CHANNELS.md), platform boundary).
- Secrets, credentials, client material, and personal or regulated data stay
  out of Buzz. Messages and uploads are not end-to-end encrypted
  ([PLATFORM_SNAPSHOT.md](PLATFORM_SNAPSHOT.md)).
- A useful Buzz thread is distilled into a Note, Practice, Guide update, Lab,
  Story, issue, or decision in Git.

## Old names

| Old | Now |
|---|---|
| `buzz/INFORMATION_ARCHITECTURE.md` | `buzz/CHANNELS.md` |
| `research/BUZZ_PLATFORM_SNAPSHOT.md` | `buzz/PLATFORM_SNAPSHOT.md` |
