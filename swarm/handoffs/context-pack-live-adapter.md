# context-pack-live-adapter Handoff

## Status

BLOCKED

Offline implementation is complete; live acceptance is blocked on isolated
runtime selection/qualification, independent ChatGPT sign-in, and a real pair.

## Summary

Added a candidate ChatGPT-backed Codex transport, owner-operated entrypoint,
private local persistence, and request-count accounting. Owner-driven work can
run multiple distinct paired trials on one day under a finite session budget;
the three-invocation daily bound applies only to the dormant background lane.
Both arms and the single repair remain Terra medium. Dollar costs stay null.

The owner requested fan-out to cheaper models. A Terra-medium worker implemented
the usage kernel; Luna-medium workers implemented storage/tests and investigated
CLI capabilities. The coordinating agent integrated and reviewed their work.
No claim about measured delegation savings is made.

## Files changed

- `scripts/context_pack_trial.py`
- `tests/test_context_pack_trial.py`
- `scripts/context_pack_codex.py`
- `tests/test_context_pack_codex.py`
- `scripts/context_pack_store.py`
- `tests/test_context_pack_store.py`
- `scripts/run_context_pack.py`
- `tests/test_run_context_pack.py`
- `tests/test_contract_integration.py`
- `ops/experiments/context-pack/README.md`
- `swarm/handoffs/context-pack-live-adapter.md`

## Validation

- Kernel: 28 focused tests passed, including same-day supervised trials,
  background bounds, pending/active-trial refusal, cap/config drift, stable old
  reports, and no-USD request envelopes.
- Store: 7 focused tests passed with 2 explicit symlink-support skips on this
  Windows host. Mocked reparse checks, hardlinks, device IDs, no outside creation,
  atomic concurrency, idempotence, and conflict refusal were covered.
- Adapter: 17 synthetic-process tests cover pinned command construction,
  environment stripping, auth/isolation refusal, bounded capture, bad/unknown
  events, timeout, cancellation, and Windows descendant-process termination.
  These tests never call Codex or a model.
- Runner: 5 focused tests passed with ResourceWarning treated as an error.
  Evidence covers multi-trial persistence, recovery after report-write failure
  without new model invocations, contract drift, stop behavior, and CLI refusal.
- First full suite: 954 tests, 2 failures and 2 skips. Existing release-brief
  subprocess decoding used Windows cp1252, producing UnicodeDecodeErrors and
  two comparison failures. With `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8`, all
  34 release-brief tests passed without modifying release artifacts.
- Final full suite: `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`, then
  `python -W error::ResourceWarning -m unittest discover -s tests`: 955 tests,
  all successful with the same 2 explicit symlink-support skips.
- `python scripts/validate.py --release --root .`: passed.
- `python skills/evals/validate.py --root .`: passed for five skills.
- `git diff --check`: passed; line-ending notices only.
- Actual `python scripts/run_context_pack.py run`: refused before adapter
  construction because no explicit live approval was supplied. No model call.
- Local CLI `exec --help`/`features list` and official OpenAI documentation
  checked on 2026-09-05; links and exact limitations are in the runbook.
- Direct owner task, not a registered swarm task: no manifest/state edits or
  fabricated task activation. Release validation is the applicable repository check.

## Decisions made

- Supervised sessions default to 21 local invocations, not 3/day. The owner can
  choose a finite cap when creating a session; it does not drift in progress.
  The corpus remains seven authored cases, not a general autonomous work queue.
- Retain active/pending state before transport. No automatic retry, refund,
  model escalation, usage reset, credit purchase, new session, or reconciliation.
- Model invocation and result storage use disjoint roots. The store is path
  safety, not an ACL or isolation mechanism; GitHub upload is not implemented.
- Use a separately authenticated, file-backed Codex home on an externally
  isolated runtime. Do not copy or reuse desktop credentials. The owner-isolation
  flag records an operator prerequisite, not a technical sandbox proof.
- `unified_exec` could not be disabled effectively on this CLI and was excluded
  from claimed controls. No verified global tool denylist exists. Unexpected
  tool events trigger refusal, but cannot prove that no side effect occurred.
- No live pilot calls, schedule, promotion, kill-switch release, public write,
  Buzz change, push, credential copying, or machine/account provisioning.

## Risks or unresolved questions

The smallest missing decision is which isolated machine/account will host the
pilot. It must be qualified and independently authenticated before a supervised
live attempt. CLI strict generation-path compatibility, actual provider output,
upstream cancellation, and shared-quota behavior remain unverified. Local
invocation/byte/time caps are not exact ChatGPT credit or model-token caps.
No remote private-result retention or background quota-aware stopping is wired.

## Acceptance record

- Artifact: this bounded adapter change against baseline `53d532f` on
  `codex/context-pack-pilot`; final commit identifies the reviewed local version.
- Intended effect/impact: material, credential-adjacent pilot execution;
  offline implementation only until live prerequisites are satisfied.
- Accountable owner: Practice founder. Agent reviewers supplied test evidence
  and defect review, not human acceptance or deployment approval.
- Scope/provenance/checks: pass for the declared paths and offline evidence
  above. Contribution skill constrained scope; verify-agent-output skill keeps
  missing live and human-review evidence explicitly unresolved.
- Human diff review/qualified-host safety/live behavior: unknown. A directory
  plus an isolation flag cannot convert these unknowns into a pass.
- Recommendation: revise before live deployment; local implementation is ready
  for owner review. User's Proceed authorized implementation and delegation,
  not a fabricated isolation attestation or unattended activation.
- Recovery owner: founder. Keep the feature branch unpublished; an owner-approved
  revert can restore the preserved baseline. For a started session use the stop
  command, preserve the journal, and reconcile pending provider outcomes without
  deleting reservations. Maintain this recovery path throughout the seven-day
  window; no automatic unstop/recovery is provided.
- Monitoring before any live release: inspect the first pair, actual usage,
  tool events, and private artifacts. Stop on any unexpected tool, timeout,
  provider error/quota refusal, output overflow, persistence conflict, or drift.
- Approval: implementation authorized in this task; live deployment/publication
  and unattended-operation acceptance have not been recorded.

## Deferred opportunities

- Qualified isolated-host setup, supervised provider proof, and remote retention.
- Background quota-aware pausing, signed promotion, and seven real daily cycles.
- Community growth workflows and role-specific model routing beyond this pilot.
