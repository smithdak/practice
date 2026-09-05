# Context-pack pilot implementation

Status: offline kernel and private-runner integration verified; live adapter
and deployment remain blocked on usage controls, runtime integration, and activation.
No live model run, signed promotion, scheduled activation, or publication
approval is implied. This is a Lab-tooling
contribution extending the limitations recorded in `labs/002-context-pack-trial.md`.

## Task and owned paths

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
3. A durable journal allows one trial per UTC day, at most seven trial days,
   one bounded repair, and no blind retry after an uncertain provider outcome.
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

The model transport is a Python callable receiving only system text, prompt,
request ID, model, reasoning effort, and maximum charge; it returns text, usage,
and charge. Model and reasoning effort are immutable session settings and are
retained in each report. Live configurations must use the selected pair below.
**No live provider adapter is implemented.** The CLI refuses without `--replay`;
replay uses a fixture oracle and costs no model requests. The journal tests use
synthetic transports, not actual providers. A provider integration must enforce
token/request/time limits upstream and supply dated price bounds; a local
reservation is not itself a cap on a provider invoice.

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
unimplemented. The kernel's micro-USD reservations are an API-oriented control,
not ChatGPT subscription accounting. Do not substitute invented dollar costs
or zero-cost reservations for ChatGPT usage. The selected adapter still needs
explicit request/token/time bounds and a shared-quota stop policy.

This direct model-selection contribution owns only this runbook,
`scripts/context_pack_trial.py`, `tests/test_context_pack_trial.py`, and
`swarm/handoffs/context-pack-model.md`. Acceptance: pin the exact pair, propagate
it to both arms and repairs, retain it in reports, reject configuration drift,
and pass focused kernel/runner tests and release validation. No activation.

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

1. Establish approved seven-day usage limits and the authenticated isolated
   runtime for the selected ChatGPT-backed Codex route. Model and private
   repository choices are resolved. No credentials in Git, Buzz, or chat.
2. Implement the selected transport, upstream usage and time limits, and durable
   private-journal integration. Prove privacy and runtime isolation on the
   selected host; do not mount the desktop profile or grant public write tokens.
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
