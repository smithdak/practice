# Platform and license fact audit

**Superseded:** superseded by [FACT_AUDIT_V2.md](FACT_AUDIT_V2.md) (2026-09-01);
current platform facts live in
[research/BUZZ_PLATFORM_SNAPSHOT.md](../research/BUZZ_PLATFORM_SNAPSHOT.md) as
of 2026-09-01. Do not cite this 2026-08-31 audit for current platform state —
its platform picture predates the #6116 closure the refreshed snapshot records.

## Outcome

No blocking factual contradiction was found in the launch-critical outputs for
F007, B005, and B006. The Buzz CLI surface, hosted-community constraints, and
Apache-2.0/CC BY 4.0 descriptions are supported by first-party sources checked
on **2026-08-31**. One non-blocking wording correction would make the
bootstrapper's bounded seed check more precise.

## Sources checked

- [Buzz CLI README](https://github.com/block/buzz/blob/main/crates/buzz-cli/README.md), Block's current CLI documentation; checked 2026-08-31.
- [Buzz CLI testing guide](https://github.com/block/buzz/blob/main/crates/buzz-cli/TESTING.md), Block's current end-to-end CLI reference; checked 2026-08-31.
- [Buzz CLI message implementation](https://raw.githubusercontent.com/block/buzz/main/crates/buzz-cli/src/commands/messages.rs), Block's current source; checked 2026-08-31.
- [Buzz CLI channel implementation](https://raw.githubusercontent.com/block/buzz/main/crates/buzz-cli/src/commands/channels.rs), Block's current source; checked 2026-08-31.
- [Buzz Support](https://block.github.io/buzz/support.html), Block's hosted-community documentation; checked 2026-08-31.
- [Scheduled-workflow report #5611](https://github.com/block/buzz/issues/5611) and [forum-root report #5075](https://github.com/block/buzz/issues/5075), open reports in Block's official repository; checked 2026-08-31. These are evidence of reported limitations, not product guarantees.
- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.html), canonical license text; checked 2026-08-31.
- [CC BY 4.0 legal code](https://creativecommons.org/licenses/by/4.0/legalcode.en) and [deed](https://creativecommons.org/licenses/by/4.0/), canonical Creative Commons sources; checked 2026-08-31.

## Claim map

| ID | Audited claim and location | Primary evidence | Disposition | Required correction |
| --- | --- | --- | --- | --- |
| B005-1 | `buzz/BOOTSTRAP_RUNBOOK.md` and `scripts/buzz_bootstrap.py` use JSON CLI output and `BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY` for apply. | Buzz CLI README documents JSON stdout/stderr, the relay environment variable, and private-key authentication. | Supported | None. |
| B005-2 | The bootstrapper uses only `channels list/create/topic/purpose`, `canvas set`, and `messages get/send`. | Buzz CLI README lists each command; current channel implementation dispatches topic, purpose, and canvas-set operations. | Supported | None. |
| B005-3 | Automated channel creation is restricted to `stream` channels with `open` or `private` visibility. | Buzz CLI README documents stream creation; current channel implementation requires a type and visibility before create. | Supported | None. |
| B005-4 | A successful channel creation exposes `channel_id`; a sent message can expose `event_id`. | Buzz CLI testing guide specifies both response fields. | Supported | None. |
| B005-5 | Seed idempotency checks the “most recent 100 messages.” | Current message implementation accepts `--limit 100` (its hard maximum is 200), but the public CLI README only says the command lists channel messages and does not promise ordering or completeness. | Partially supported; non-blocking | In the runbook, replace “the most recent 100 messages” with “up to 100 messages returned by `buzz messages get`.” Keep the existing manual duplicate-resolution warning. |
| B005-6 | The bootstrapper does not delete, archive, create workflows, or automate forum-root posts. | Direct inspection of `scripts/buzz_bootstrap.py` finds no calls to those commands; the launch-safe command list above omits them. | Supported (implementation fact) | None. |
| B005-7 | Scheduled workflows and forum-root automation remain outside the launch path. | The two open official-repository reports still describe hosted scheduled workflows failing and forum roots sent as invisible stream events. The implementation also has no workflow or forum call. | Supported as a conservative launch constraint | None. Do not treat either issue report as a permanence guarantee. |
| B006-1 | Block-hosted communities are invite-only; open channels are community-member visible and private channels are limited to added users/agents. | Buzz Support states all three constraints. | Supported | None. |
| B006-2 | Hosted messages, direct messages, and uploads are not end-to-end encrypted; hosted Buzz is not a confidential vault. | Buzz Support states the three data types are not end-to-end encrypted and may be accessed to operate, secure, or moderate the service. | Supported | None. |
| B006-3 | Human and agent identities are distinct, and agents receive only channel access granted to them. | Buzz Support says an agent has its own profile and public key and can read/send only in channels it can access. | Supported | None. |
| B006-4 | Private keys must not be shared with support, agents, or others; a backup can restore an identity on another device. | Buzz Support expressly says never share a private key and describes secure backup/import. | Supported | None. |
| B006-5 | Owner/support escalation, access removal, and compromise guidance remain human-controlled. | Buzz Support assigns community owners access management/removal and directs account-access or compromise reports to official support. The runbook's extra approvals are Practice policy, not a platform claim. | Supported | None. |
| F007-1 | Apache-2.0 code may be used, modified, and distributed commercially, subject to license conditions. | Apache License 2.0 grants reproduction, derivative-work, sublicense, and distribution rights; its redistribution section sets the conditions. | Supported | None. |
| F007-2 | Apache-2.0 redistribution requires a license copy, modified-file notices, applicable source notices, and applicable NOTICE attribution. | Apache License 2.0 §4 specifies these requirements; its NOTICE requirement applies when the original work includes a NOTICE file. | Supported | None. |
| F007-3 | Apache-2.0 does not grant trademark rights beyond customary origin description and NOTICE reproduction. | Apache License 2.0 §6 says this explicitly. | Supported | None. |
| F007-4 | Intentional code contributions default to Apache-2.0 unless explicitly stated otherwise; the policy need not add a CLA. | Apache License 2.0 §5 supplies that default for contributions. The no-CLA choice is a Practice governance decision, not a claim made by the license. | Supported | None. |
| F007-5 | CC BY 4.0 content may be shared and adapted commercially with appropriate credit, license link, and change indication. | CC BY 4.0 legal code §3(a) and deed state these terms. | Supported | None. |
| F007-6 | CC BY credit must not imply endorsement, and the exact placement may vary with medium and context. | CC BY 4.0 deed prohibits implied endorsement; legal code §3(a)(2) permits reasonable attribution appropriate to the medium, means, and context. | Supported | None. |
| F007-7 | License grants do not by themselves settle trademark, privacy, publicity, or other non-copyright rights. | Apache License 2.0 §6 reserves trademarks; CC BY 4.0 legal code limits licensed rights and preserves other rights. | Supported | None. |
| F007-8 | The repository applies Apache-2.0 to code and CC BY 4.0 to content unless a file says otherwise. | This is a repository licensing decision consistently stated in `LICENSES.md`, `LICENSE-CODE`, `LICENSE-CONTENT.md`, `NOTICE`, and `community/ATTRIBUTION.md`; the canonical licenses support the described terms. | Supported (repository policy) | None. |

## Blocking findings

None.

## Non-blocking findings

1. **Bounded history wording:** `buzz messages get --limit 100` is a valid
   current CLI request, but the public CLI documentation does not promise that
   those returned messages are the “most recent” ones or that the result is a
   complete history. Correct the runbook wording in B005's owned path before a
   future release edit. The existing explicit warning that marker detection is
   bounded remains appropriate.

2. **Issue-status volatility:** Workflow and forum exclusions are correctly
   conservative today. Their cited issue reports are current evidence rather
   than a stable compatibility contract; recheck them and the CLI documentation
   before making either capability launch-critical.

## Excluded-capability check

- **Scheduled workflows:** excluded by `DECISIONS.md`, the runbook, the
  security runbook, and the bootstrapper implementation. No workflow command
  occurs in the bootstrapper.
- **Forum root automation:** excluded by the same launch documentation and
  implementation. All configured launch channels are `stream`, and no forum
  command occurs in the bootstrapper.
- **Destructive recovery:** excluded. The bootstrapper does not call delete,
  archive, membership-removal, or workflow commands; the runbook requires
  human manual review for correction.
