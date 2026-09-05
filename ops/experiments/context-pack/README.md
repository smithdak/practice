# Context-pack pilot implementation

Status: request-accounted supervised execution, a candidate Codex adapter, and
private local persistence are implemented. Live acceptance remains blocked on
an independently isolated, separately authenticated runtime and a real paired run.
No live model run, signed promotion, scheduled activation, or publication
approval is implied. This is a Lab-tooling
contribution extending the limitations recorded in `labs/002-context-pack-trial.md`.

## Original kernel task and owned paths

Build a bounded paired experiment and private staging integration, reusing the
existing autonomy guard, runner, and ledger. Owned paths:

- `ops/experiments/context-pack/README.md` (this specification and runbook)
- `ops/experiments/context-pack/cases.json`
- `scripts/context_pack_trial.py`
- `scripts/run_unattended.py`
- `tests/test_context_pack_trial.py`
- `tests/test_run_unattended.py`
- `tests/test_autonomy_guard.py` (catalogue membership expectation only)
- `tests/test_contract_integration.py` (record why a writing command is tested through unittest rather than run as a CI validator)
- `release/OWNER_REVIEW.md` (repair a setup-note heading that hides existing gate rows from the report parser; no decision changes)
- `ops/autonomy/operations.yaml` (catalogue only, never a promotion)
- `swarm/handoffs/context-pack-pilot.md`

Do not change the manifest, promotions, renewals, kill-switch state, artifact
maturity, public workflows, provider credentials, or Buzz configuration.

## Acceptance

1. Versioned synthetic held-out cases share identical source facts between
   baseline and structured-pack arms; no answer key is passed to the generator.
2. Retain requests, responses, deterministic rubric results, runtime, and
   available usage with hashes. Label replay output as synthetic machinery
   verification, not a model trial or a measured community outcome.
3. A durable journal limits background work to one trial per UTC day for seven
   days. Owner-driven trials use the separate supervised lane described below.
   Both allow one bounded repair and no blind retry after an uncertain outcome.
4. Reserve the worst-case request charge before transport. Refuse insufficient
   budget, expired windows, changed configurations, and a stopped session.
5. Keep outputs and ledger entries in explicitly chosen private staging outside
   the canonical checkout. No public PR, push, or Buzz post is part of this path.
6. Test normal execution plus interruption, duplicates, budget exhaustion,
   rubric failure, expiry, and guard/kill-switch refusal. Run release validation
   and the regression suite. Commit the reviewed local implementation only.

Live acceptance is separate: seven actual daily cycles, isolated hosting,
the selected provider/model, approved usage limits, private retention, a specific
signed promotion, and an independently released kill switch. These are not
replaced by passing replay tests.

## Implemented boundary

The corpus contains seven **authored synthetic** evidence-summary tasks: clean
checks, a whitespace failure, a missing result, malicious text in an output,
misleading success text, mixed results, and unknown-only results. These are
held out from pack examples (there are no examples); they are not secret
benchmarks or actual member activity. The task is summarizing check records,
not executing the launch checks themselves. No general context-pack benefit
can be inferred from this small, narrow task set.

Both arms receive every rule and every source record. The baseline interleaves
notes; the pack groups task instructions and sources. System messages match,
each request is stateless, arm order alternates, and the deterministic evaluator
derives expected statuses from the supplied exit codes. It receives model
outputs but is never exposed to the generator as an answer key. Initial paired
attempts are the primary measure; the single allowed repair is secondary.

`Session` retains a SQLite journal with fully committed reservations before
transport, raw request/response text, hashes, observed runtime, and supplied
usage/cost. Unknown usage stays null. Successful calls resume without another
request. A pending call blocks further work, including after a restart; it is
not retried or refunded because a timeout can still incur a charge. A partially
completed prior day also blocks advancement. There is no automatic uncertain-
call reconciliation command yet. Budget accounting conservatively retains
the full reservation even when observed charges are lower.

The transport receives system text, prompt, request ID, model, and reasoning
effort. Legacy micro-USD accounting additionally supplies a charge ceiling;
ChatGPT request accounting does not. Both return text, available usage, and
cost (always null for the ChatGPT adapter). Model and reasoning remain bound
to the session. `context_pack_trial.py` still only exposes synthetic `--replay`;
the separate `run_context_pack.py` entrypoint is owner-operated, never scheduled.
Tests use synthetic transports/processes, not actual providers.

## Selected pilot model (2026-09-05)

Owner selection: OpenAI through ChatGPT-backed Codex, `gpt-5.6-terra` with
`medium` reasoning for baseline, structured-pack, and the single permitted
repair. No fallback or mid-session upgrade: changing the model or effort would
confound the paired comparison. This selection applies to this pilot, not all
Buzz agents. Synthetic replay still uses a fixture oracle with no reasoning.

The local Codex model catalogue lists this combination. The
[official Terra model reference](https://developers.openai.com/api/docs/models/gpt-5.6-terra),
checked 2026-09-05, also lists medium reasoning. Neither check is a live pilot
execution or proof that a future unattended host is authenticated.

The owner-authorized `smithdak/practice-pilot-results` repository exists and
was verified private through GitHub on 2026-09-05. Retention wiring remains
unimplemented for remote GitHub retention. Local private retention is wired into
the supervised entrypoint. Request accounting replaces dollar reservations for
this access route: never invent dollar costs or interpret null cost as free usage.

This direct model-selection contribution owns only this runbook,
`scripts/context_pack_trial.py`, `tests/test_context_pack_trial.py`, and
`swarm/handoffs/context-pack-model.md`. Acceptance: pin the exact pair, propagate
it to both arms and repairs, retain it in reports, reject configuration drift,
and pass focused kernel/runner tests and release validation. No activation.

## Supervised and background usage (2026-09-05)

The owner clarified that work they actively drive must not be limited to three
requests per day. The limits therefore apply to different lanes:

| Lane | Local invocation bound | Trial identity and evidence |
| --- | --- | --- |
| Background | One paired trial daily; two initial invocations and at most one repair; seven-day expiry | At most seven distinct daily trials. No live background entrypoint or schedule is enabled. |
| Supervised | Multiple pairs on the same day; explicit finite per-session cap, default 21; no three-per-day ceiling | Owner supplies session ID, trial ID, and case ID. Additional same-day trials are not additional daily cycles. |

Each session uses each of the seven authored cases once. Repeating a completed
trial ID retrieves its original result without generation; reusing a case under
a different trial ID is refused. A new owner-created session can repeat the
corpus for development, but does not create independent benchmark cases.
Neither the adapter nor runner creates new sessions to escape a cap.

The session's lane, corpus, model, reasoning, invocation cap, and adapter contract
are immutable. An interrupted active trial blocks another trial until it is
completed or reconciled; a pending invocation blocks all continuation. The
journal reserves a local invocation before launching the transport. It retains
null cost, available token counters, primary/repair separation, and stable
completion counts. An older report does not change when later trials complete.

These are **local invocation bounds, not exact ChatGPT credit/token caps**.
Codex/provider behavior may involve internal retries; forceful local cancellation
does not prove provider cancellation or a refund. The adapter disables the
installed CLI's unbounded-connection-retries feature but does not claim that
every network retry is suppressed. No automatic paid fallback, credit purchase,
usage reset, or quota-limit retry exists. Shared-account quota-aware pausing is
not implemented; the owner must monitor remaining account usage before a run.

## Candidate Codex adapter and runtime boundary

`scripts/context_pack_codex.py` pins CLI `0.153.0`, Terra medium, ChatGPT auth,
and file-backed credentials in an explicitly supplied dedicated `CODEX_HOME`.
The owner authenticates that home separately; the code never reads or copies
credential files. A separate directory alone is not OS/account isolation.

Every invocation gets a fresh working directory containing only the response
schema, outside the repository. The CLI ignores user config and exec rules,
uses read-only permissions and ephemeral sessions, requests no web search, and
disables the installed shell, browser, computer-use, apps, hooks, plugins,
collaboration, image, memory, and related features listed in the adapter.
Ancestor repositories/agent configuration are refused. Environment forwarding
is allowlisted; API tokens, proxy overrides, and inherited task IDs are excluded.

**These controls do not establish a global tool denylist.** The CLI retains its
built-in instructions; the supplied task text is not represented as a replacement
provider system message. Tool/unknown/error events stop capture and reject the
trial. This is detection, not proof that an attempted tool had no side effect.
The owner must qualify external runtime isolation before supplying
`--confirm-isolated-runtime`; the flag records that prerequisite, it cannot
create or verify isolation. The shared driving desktop profile is not qualified.

Bounds per invocation: default 180-second timeout (maximum 300), 64 KiB prompt,
256 KiB stdout, and 32 KiB stderr. These byte limits are not model-token limits.
Windows uses a kill-on-close Job Object; POSIX uses a separate process group.
Cancellation is forceful. Raw stderr and provider errors are not printed or
retained in reports. Structured usage preserves unknown fields as unavailable,
not zero. No live execution or upstream cancellation has been verified yet.

Sources checked 2026-09-05: [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode),
[authentication](https://learn.chatgpt.com/docs/auth), and
[configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).
The installed CLI's `exec --help` and `features list` supplied release-specific
flag evidence. Do not use ChatGPT credential seeding in public-repository CI.
Local `features list` accepted the candidate overrides and showed the listed
features disabled. It did not honor `--disable unified_exec`, so that flag is
not part of the contract. `features list` cannot run with `--strict-config`;
strict generation-path validation remains part of the first qualified live run.

## Owner-operated commands

The following is an **example for an already qualified isolated host**, not an
instruction to copy credentials or run against the shared desktop. Paths must
be absolute; use that host's own executable and separately authenticated home.
The private journal root and disposable runtime root must not overlap.

```text
python scripts/run_context_pack.py preflight --codex-executable D:/isolated-bin/codex.exe --runtime-root D:/pilot-runtime --codex-home D:/pilot-runtime/auth --confirm-isolated-runtime
python scripts/run_context_pack.py run --private-root D:/pilot-results --session-id owner-20260905 --start-date 2026-09-05 --trial-id trial-1 --case-id all-pass --session-invocation-cap 21 --codex-executable D:/isolated-bin/codex.exe --runtime-root D:/pilot-runtime --codex-home D:/pilot-runtime/auth --confirm-isolated-runtime --approve-live-trial
python scripts/run_context_pack.py stop --private-root D:/pilot-results --session-id owner-20260905
```

Use another trial/case ID in the same session for more owner-driven work that
day. Preserve the session's start date and cap. The stop command writes a
persistent STOP marker and stops the journal; it neither reconciles nor refunds
pending calls. The running adapter polls that marker. Report-write failure can
be recovered with the original invocation arguments: completed responses remain
in the journal and are not generated again. No automated uncertainty-recovery
or unstop command is shipped.

Results live at `sessions/<session-id>/reports/<trial-id>.json` and the journal
at `sessions/<session-id>/journal.sqlite` under the chosen private root.
Publication is atomic and immutable: identical retries succeed, conflicting
content is not overwritten. Symlinks/junctions, path traversal, reserved device
IDs, and canonical-root overlap are refused. These checks are not filesystem
ACLs, encryption, or protection against a hostile concurrent host user.
No result is staged, committed, pushed to GitHub, or published to Buzz.

## Adapter contribution scope and acceptance

Direct owner task `context-pack-live-adapter` owns only:

- `scripts/context_pack_trial.py` and `tests/test_context_pack_trial.py`
- `scripts/context_pack_codex.py` and `tests/test_context_pack_codex.py`
- `scripts/context_pack_store.py` and `tests/test_context_pack_store.py`
- `scripts/run_context_pack.py` and `tests/test_run_context_pack.py`
- `tests/test_contract_integration.py` (CI coverage declarations only)
- this runbook and `swarm/handoffs/context-pack-live-adapter.md`

Acceptance: test multiple owner-driven pairs, background bounds, immutable
identity/accounting, interruption/recovery, private routing, restrictive command
construction, sanitized event parsing, byte/time bounds, process-tree cancellation,
and safe CLI refusal. Run regression and release validation. Live acceptance
additionally requires qualified hosting, independent sign-in, an approved real
pair, and retained provider evidence. Offline passes do not replace those checks.

On Windows, run the full suite with explicit UTF-8 subprocess encoding:

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
python -W error::ResourceWarning -m unittest discover -s tests
```

## Private runner integration

The existing `scripts/run_unattended.py` accepts `--private-root`:

- guard decisions still come from the canonical governance records;
- permitted private runs require those records to match the source commit;
- input files come from a pinned Git archive, excluding untracked/ignored
  files and `.git` configuration; committed secrets would still be included,
  so never commit them;
- subprocess environments retain only executable/system/temp paths plus
  Python encoding settings, not inherited provider or Buzz credentials;
- only scope-approved outputs reach the chosen private root; ledger entries
  are written there too; stdout/stderr excerpts are not printed by the runner;
- overlapping roots, linked/junction targets, and a conflicting ledger override
  are refused. A dry run creates neither the root nor the ledger.

This is private **output routing**, not proof of private hosting, filesystem
ACLs, network isolation, or a process sandbox. The existing five-minute staged
command timeout remains. The export has no Git history and is unsuitable for
commands that require `.git`. Default runner behavior remains available for
the older operations.

**Do not put a live model session's budget journal in disposable staging.**
The private routing path is verified for the offline experiment command only.
A live adapter requires a durable control-plane journal outside the disposable
worker, with provider credentials unavailable to generated code. No live path
is wired into the public unattended workflow.

## Rehearse without activation

Run from the repository checkout:

```text
python -m unittest discover -s tests -p test_context_pack_trial.py
python -m unittest discover -s tests -p test_run_unattended.py
python scripts/run_unattended.py --operation context-pack-trial --root . --dry-run
```

The first two commands exercise real synthetic execution, including a committed
fixture passed through the private-output runner. The last prints the actual
guard refusal and writes nothing. It does not authorize a trial. Exit zero for
this dry run means the simulation completed, not that the guard permitted it.
Do not run `context_pack_trial.py --replay` against the canonical checkout: it
is a writing command intended for disposable test input trees only.

## Remaining live-enablement work

1. Select and qualify an independently isolated runtime; authenticate its own
   ChatGPT-backed Codex home. Model, invocation-lane policy, and private
   repository choices are resolved. No credentials in Git, Buzz, or chat.
2. Run an approved supervised pair using the candidate adapter and retain the
   actual evidence. Verify actual CLI settings, output events, privacy, and
   cancellation on that host. Do not mount the desktop profile or grant public
   write tokens. Provider quota-aware stopping and remote retention remain open.
3. Add private daily execution and persistence with one active session, durable
   restart behavior, and a bounded expiry. Test actual cancellation and unknown
   provider outcomes. No new scheduled workflow is enabled by this contribution.
4. Retain the evidence for a specific promotion proposal. The owner records
   that decision; release the kill switch independently only after validation.
5. Run seven actual daily cycles. Review failed trials as evidence. Decide
   publication and artifact maturity separately; neither is automated here.

Do not restart general setup approvals. Remaining decisions concern usage
limits and runtime deployment, followed by the explicit
operation-specific activation decisions after its evidence exists.
