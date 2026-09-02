# A3 candidate dossiers

**As of:** 2026-09-02

## What these are

Five operations are catalogued in [the operation catalog](operations.yaml) as
things that *could* one day run unattended. None is promoted, and
[the autonomy ladder](../../docs/framework/AUTONOMY_LADDER.md) records that no
operation in this repository is at A3.

A dossier is what a human reads before deciding whether one of them should be.
It states what the operation would do without a person, the paths it may write,
how a run is undone, what accumulates if it goes wrong, the evidence that exists,
the evidence that does not, and the specific way this particular operation fails.
It is written to inform the decision, not to argue for an outcome.

**No dossier here recommends promotion.** Each ends with the decision a human
would face and what would have to exist before that decision could be made on
facts. Two of the five are judged unsuitable for unattended running as they
stand, and say so plainly; that is a finding, not a deferral.

Read a dossier alongside [the promotion proposal](PROMOTION_PROPOSAL.md), which
is the record a signature goes on. Nothing here is a signature, a bound, or a
transcription into [the promotion record](promotions.yaml).

**How to read a write scope.** The scopes below are quoted from the catalog,
which is authoritative: the guard rejects a promotion whose scope disagrees with
its catalog entry. Two of the five have an empty scope and write nothing at all;
for those, an unattended run produces a ledger entry and a pull request, and
nothing else. Globs in the catalog are matched with `fnmatchcase`, where `*`
crosses a slash — `ops/status/*.md` also permits `ops/status/archive/old.md`.
This is not the dialect used by the evidence globs in
[`ops/cadence.yaml`](../cadence.yaml), which are matched with `Path.glob`, where
`*` stops at a slash. The same pattern means two different things in two files a
proposer reads together.

## The five at a glance

| Candidate | What one unattended run leaves behind | Reversal | The finding to weigh first |
| --- | --- | --- | --- |
| `cadence-snapshot` | One dated file under `ops/status/` | Delete the file, or close the pull request unmerged | In a shallow checkout every pass date collapses to the clone's tip commit, and the report says nothing about it |
| `metrics-snapshot` | One dated file under `ops/status/`, in the same directory as the cadence snapshots | Delete the file, or close the pull request unmerged | The evidence-element heading map can drift from the schemas, and the README says coverage then falls silently |
| `contract-drift-check` | Nothing. A ledger entry and a pull request | Close the pull request unmerged; nothing was written | The one command it runs is already a named CI step on every pull request and every push to `main` |
| `staleness-sweep` | Nothing. A ledger entry and a pull request | Close the pull request unmerged; nothing was written | Stale as-of dates are warnings that never affect the exit code, and the rule can read a dated line in only 20 of 342 files |
| `release-brief-draft` | One dated brief under `release/briefs/` | Delete the file, or close the pull request unmerged | The catalogued command is missing `--since` and `--as-of`, and there is no defensible unattended rule for either |

The reversal column is nearly uniform because the design makes it so: an
unattended run arrives as a pull request, and closing it unmerged undoes the run
at no cost. Identical reversals do not make identical risks. What differs is what
a wrong output causes before anybody closes anything.

---

## `cadence-snapshot`

### What it would do unattended

Run `python3 scripts/cadence.py --root .` on a schedule, and the runner writes
the report into the declared scope as a dated file. The script reads
[`ops/cadence.yaml`](../cadence.yaml), the evidence globs each pass declares,
every file under `swarm/handoffs/`,
[`release/OWNER_REVIEW.md`](../../release/OWNER_REVIEW.md), and every markdown
file's `As of:` line. It reports which pass windows have elapsed, which handoffs
are recorded `BLOCKED`, which owner gates and operating holds are recorded open,
and which as-of dates are stale.

The script writes nothing itself — it prints to standard output. The output is
plain text, not markdown, and about 5.5 KB. Committing it as a `.md` file means
something between the script and the repository wraps it, every run, and that
wrapping is not part of the catalogued command.

### Write scope

`ops/status/*.md`. One new file per run.

The narrowness matters mechanically, in a way worth checking rather than
assuming. The Build pass in [`ops/cadence.yaml`](../cadence.yaml) declares
`ops/*.md` as evidence, and those globs are matched with `Path.glob`, which does
not descend: `ops/*.md` there means the eight files directly under `ops/` and
nothing under `ops/status/`. So a status file does not make the Build pass look
freshly worked. A reader who applied the catalog's `fnmatch` semantics to
`ops/cadence.yaml` would reach the opposite conclusion and be wrong.

### Reversal

Delete the file, or close the pull request unmerged. Since the script writes
nothing itself, a reverted run leaves no trace outside the deleted file and its
ledger entry. No credential, no runner, and no agent context is needed: `git rm`
is sufficient.

### Blast radius

One file per run. A month of daily runs is roughly 30 files in one directory and
30 pull requests. Nothing reaches a community member; nothing is published.

The files land inside `ops/`, which `scripts/validate.py --release` walks
recursively for unfinished and publication tokens. The cadence report carries
neither today, checked directly against both rules at this commit. But
`cadence.py` has no self-guard for them — unlike `scripts/release_brief.py`,
which refuses to write rather than emit one. If a future owner-review row or
handoff title contained a bracketed uppercase token, an unattended run would
commit it into `ops/` and release validation would start failing for everybody,
on a schedule.

### Evidence that exists today

- 56 tests in `tests/test_cadence.py`, all passing in the standard-library
  suite.
- The script's boundaries are stated and enforced: it reads this repository only,
  never substitutes today's date or a file mtime for a missing git date, and
  repeats gate and hold statuses verbatim without clearing one.
- It exits 0 whenever a report was produced, and 1 only on a configuration or
  usage error. It is deliberately not a gate, and
  `tests/test_contract_integration.py` records that exemption with a reason:
  "making an elapsed window a build failure would create work no person owns."
  That reason transfers to an unattended run, which produces a pull request
  somebody has to read.
- The report has been produced against this repository at `--as-of 2026-09-02`:
  6 passes, 0 with an elapsed window, 0 blocked handoffs, 8 open gates, 7 open
  holds, 0 stale as-of dates.

### Evidence that does not exist

- No run of this operation unattended, in any form. The command has never been
  executed on a schedule, and no committed status file exists — `ops/status/`
  does not exist in this repository.
- No named role has agreed to read a dated series. [The weekly
  cadence](../WEEKLY_CADENCE.md) assigns every pass an owner role; it assigns no
  owner to a generated status file.
- No record of what a reader would do differently having read one. The report
  assigns nothing to anyone by design, which is the correct boundary and also the
  reason its value is unmeasured.

### The specific way it goes wrong

**A shallow checkout silently flattens every date.** The report's last-changed
dates come from `git log`. In a `git clone --depth 1` checkout the tip commit has
no parent in the clone, so `git log --name-only` attributes every path in the
repository to that one commit. Verified against this repository: a full checkout
at `--as-of 2026-12-01` reports six distinct pass dates, including
`2026-08-31 (92d ago)` for Session and `2026-09-01 (91d ago)` for Maintenance; a
depth-1 clone of the same repository reports `2026-09-02 (90d ago)` for all six.
The header line still reads `change dates  git log`. Nothing in the output says
the dates are an artifact of the clone.

[The CI workflow](../../.github/workflows/ci.yml) sets `fetch-depth: 0` for an
unrelated reason — the release-brief range checks — and
`tests/test_contract_integration.py` asserts it stays. A new scheduled workflow
inherits none of that. If it checks out shallow, every pass reports the same
date: right after a commit everything reads "within window", and long after one
everything elapses together. Either way the per-pass signal is gone, the file is
well-formed, and a reader has no way to tell.

That is the failure that matters here. A cadence report is read at a glance for
exceptions. A report that structurally cannot produce an exception looks exactly
like a repository with no exceptions, and it looks that way for as long as the
schedule runs.

### The decision, and what would have to exist first

The decision is whether a dated series of cadence reports is worth a scheduled
writer, given that the same report is one command away and nobody has agreed to
read the series.

Before that decision could be made on facts: a named role that has agreed to read
the output and can say what they would do with it; the checkout depth pinned and
asserted in the scheduled workflow, or a line in the report itself stating the
history depth it read; and a token self-guard equivalent to the one in
`scripts/release_brief.py`, or an accepted answer for what happens when release
validation starts failing on a file no person wrote.

---

## `metrics-snapshot`

### What it would do unattended

Run `python3 scripts/collect_metrics.py --root .` on a schedule, and the runner
writes the report into the declared scope as a dated file. The collector reads
artifact front matter, changelogs, the owner review packet, and internal link
targets, and reports each repository-observable metric from
[`ops/METRICS.md`](../METRICS.md) with its denominator and evidence coverage.
Everything it cannot see is printed as "not collected", never as zero.

Its output is markdown — about 8.8 KB, roughly 140 lines, deterministic for a
given tree and `--as-of`. The catalogued command passes no `--as-of`, so an
unattended run dates the report from the clock of the machine it ran on.

### Write scope

`ops/status/*.md` — the same scope as `cadence-snapshot`.

That is worth a decision rather than a shrug. Two operations writing into one
directory produce an interleaved series of two different report kinds, told apart
only by their file names and their contents. A reader opening `ops/status/` sees
a stream, not two series, and a gap in one of them is hidden by the presence of
the other.

It also brushes against a recorded policy. [The metrics
README](../metrics/README.md) says: "Reports are generated on demand and are not
committed. If maintainers decide to retain one, keep it with the review record
for that period and keep its commit identifier with it." Promoting this operation
commits reports on a schedule, in a different directory, with no review record
attached. The policy edit belongs in the same change as the promotion, made by a
human, not discovered afterwards.

### Reversal

Delete the file, or close the pull request unmerged. The collector makes no
network call, opens no socket, and never enters `.git`, so a reverted run leaves
nothing outside the deleted file.

### Blast radius

One report per run. A month of weekly runs is four reports and four pull
requests; daily, about 30. No member data is involved: the collector has no data
structure for a person, and reads no identity, join, view, reaction, or session.

The reports land in `ops/`, which release validation walks. The collector quotes
owner-gate and operating-hold rows verbatim from
[`release/OWNER_REVIEW.md`](../../release/OWNER_REVIEW.md). Those rows contain
markdown links today, which the publication-token rule skips, so the check passes
— verified directly against both release rules at this commit. Like `cadence.py`
and unlike `release_brief.py`, the collector has no self-guard, so that stays true
only while the source rows keep their current form.

### Evidence that exists today

- 39 tests in `tests/test_collect_metrics.py`.
- The collector reuses `scripts/validate_artifacts.py` for front matter and
  `scripts/check_links.py` for link targets, so it cannot drift away from what
  the validators enforce.
- Determinism: two runs over the same tree with the same `--as-of` produce
  identical bytes, which is what makes a committed series diffable at all.
- The honesty rules are in the code, not only in prose: nothing is reported as
  zero that was not measured, no `maturity` or `evidence_quality` value is
  written, and no gate or hold is asserted cleared.
- A report exists for this working tree at `--as-of 2026-09-02`: 12 of 12
  artifact files parsed their front matter; practice coverage 42 of 42 elements
  stated; 15 dated changelog entries; 8 gates and 7 holds recorded open; 938 of
  938 internal link targets resolve across 342 markdown files.

### Evidence that does not exist

- No committed report, and no series. There is no evidence about how a series is
  read, because none has ever existed.
- No evidence that the heading map stays correct across a schema change, because
  no schema has changed since the map was written.
- No human measurement route is running. Seven of the contract's metrics —
  Activation, proposed Contribution, Artifact reuse, Implementation, Response
  quality, Retention, Maintainer health — need the human route in
  [`ops/METRICS.md`](../METRICS.md), and none is being recorded. Every committed
  report would be a repository census standing next to seven "not collected"
  rows.

### The specific way it goes wrong

**Coverage falls silently when a schema changes.** The Evidence metric maps
element names onto the headings each artifact type defines. The map lives in
`scripts/collect_metrics.py` with a copy in [the metrics
README](../metrics/README.md), which states the consequence in its own words: "If
a schema gains or renames a section, update the map in
`scripts/collect_metrics.py` and the table above in the same change, or coverage
will silently fall."

Attended, that is a caught error — the person who renamed the heading runs the
collector and sees the number move. Unattended and committed weekly, it is a
downward trend in a series, indistinguishable from artifacts genuinely losing
evidence. Today's report says every scored artifact states every element it is
scored on. A rename turns that into a falling number with no cause recorded
anywhere, and the natural reading of falling coverage is that the artifacts got
worse.

The second failure belongs to the series rather than to any report. Each report
carries the "not collected is not zero" caveat in its own body. A directory of
dated reports invites comparison across them, and the comparison carries no
caveat. That is exactly the "report read as a decision" failure
[`ops/OPERATING_LOOP.md`](../OPERATING_LOOP.md) already names, made
durable and dated.

### The decision, and what would have to exist first

The decision is whether a committed dated series of repository censuses is worth
having before any of the seven human-route metrics is being recorded — and
whether the series would be read as community health once it sits in a directory
and has a trend.

Before that decision could be made on facts: the retention policy in [the metrics
README](../metrics/README.md) rewritten by a human to say reports are committed,
where, and why; a decision about sharing `ops/status/` with `cadence-snapshot`,
or a scope of its own; a check that fails when the heading map and the schemas
disagree, so coverage cannot fall without a cause; and a named role who reads a
report and records what changed and why, since a series nobody annotates is a
trend line with no explanation attached.

---

## `contract-drift-check`

### What it would do unattended

Run `python3 scripts/validate_agents.py --root .` on a schedule. The validator
checks [the agent registry](../../buzz/agents/registry.yaml) against the profiles
it claims to describe: one entry per profile and one profile per entry, channel
scope that exists in [the channel map](../../buzz/community.json) and is
least-privilege, the locked prohibitions present in every entry, autonomy inside
the attended vocabulary, an escalation owner that is a role rather than a person,
and `status` consistent with owner gate 6.

The catalog's own note is precise about the limit: this covers the registry
contract only. The eval-definition, packet, and artifact validators are separate
commands and are not catalogued, so a clean run of this one is not evidence that
they pass.

### Write scope

Empty. The operation creates and changes no path. A run leaves a ledger entry and
a pull request, and nothing else.

### Reversal

Nothing to reverse. Close the pull request unmerged if the scheduled workflow
opened one.

### Blast radius

The smallest of the five by what it touches and the largest by what a wrong
result implies. Nothing is written, nothing reaches a member, nothing is
published. What accumulates is a series of ledger entries recording that a check
passed.

That series is an assurance artifact. If the job is silently misconfigured — a
wrong root, a missing PyYAML, a checkout that never happened — the ledger records
a pass that was never meaningfully performed, in the place a human looks for
exactly this kind of assurance.

### Evidence that exists today

- `scripts/validate_agents.py` is a named step in
  [the CI workflow](../../.github/workflows/ci.yml), which runs on every pull
  request and every push to `main`. So does `make checks`, and so does
  `make agents`.
- `tests/test_contract_integration.py` enforces that wiring:
  `test_every_check_runs_in_ci_or_is_exempt` fails when a script under `scripts/`
  neither appears in the workflow nor carries a written exemption reason.
- 53 tests in `tests/test_validate_agents.py`, plus 17 cross-contract tests in
  `tests/test_contract_integration.py`.
- The check is time-invariant. Its inputs are committed files, and neither
  `validate_agents.py` nor the sibling contract validators reads the current
  date; the only date handling anywhere in them is parsing dates out of files.
- The validator reads files only. It never enables an agent, never changes a
  status, and never asserts a gate or hold is cleared.

### Evidence that does not exist

- No evidence of drift that CI missed. There is no recorded instance of this
  check failing on a schedule after passing on a push, because no such schedule
  has run.
- No evidence that a scheduled run could observe anything a push-triggered run
  could not, given a time-invariant check over committed inputs.

### The specific way it goes wrong

**It manufactures a second, weaker copy of a signal that already exists.** The
check is time-invariant and every input is a committed file. A scheduled run can
therefore reach a different verdict from the last CI run only if the files
changed — and a change to the files arrives through a push or a pull request,
which runs CI. The window a scheduled check would cover is the window in which
nothing changed.

That leaves one real case: a change that lands without CI running, through a
misconfigured branch protection or a skipped workflow. That is an infrastructure
defect. The fix is to repair the trigger, not to add a second checker that
depends on the same infrastructure being configured correctly.

There is also a level question a signer should not skip. A3 is defined as the
action itself, performed by the agent inside a recorded bound. This operation
performs no action: it reads files and reports. The ladder already places
`read-assigned` and `report-observation` at A0, which is where the catalog puts
it. Promoting it to A3 does not authorize an action; it authorizes a schedule.
That may be a thing worth having, but it is not the thing the level was written
for, and calling it A3 makes the first entry in the promotion record an entry
that does nothing.

### The decision, and what would have to exist first

**This one should stay where it is.** It is unsuitable for unattended running —
not because it is dangerous but because it is redundant. It would spend the
repository's first promotion on re-reporting a result CI already produces on
every change, and it would leave behind an assurance record whose failure mode is
silence: when the job breaks, the symptom is that no new ledger entry appears,
and a missing entry looks like a quiet week.

If the underlying want is drift detection between pushes — a real want, since a
repository nobody touches for three months gets no CI run at all — the cheaper
answer is a scheduled CI job that runs `make checks` and writes nothing to the
repository. That needs no promotion, no bound, no reversal, and no signature,
because it performs no action in the repository. It is not an A3 operation, which
is the point.

Nothing would change this analysis except a recorded case of contract drift that
CI structurally could not have caught. If one is ever found, this dossier should
be rewritten around that case.

---

## `staleness-sweep`

### What it would do unattended

Run `python3 scripts/check_links.py .` on a schedule. The sweep scans every
markdown file outside `.git`, `.worktrees`, and `__pycache__`, resolving each
relative and repo-absolute link target and reading each `As of:` line. It reports
two different kinds of thing with two different severities: a broken or escaping
link is an **error** and sets the exit code to 1; an as-of date older than
`STALE_LIMIT_DAYS` (90) is a **warning** printed to standard output that never
affects the exit code.

[`ops/cadence.yaml`](../cadence.yaml) mirrors the limit, and `scripts/cadence.py`
refuses to load a config whose `staleness_limit_days` disagrees with the
constant, so the two cannot drift apart silently.

### Write scope

Empty. The sweep creates and changes no path. A run leaves a ledger entry and a
pull request, and nothing else.

**The scope that must stay excluded, in writing, is the one that would let the
sweep fix what it finds.** A sweep that edited `As of:` dates would make stale
documents report themselves as current. Manufacturing the appearance of currency
is the worst outcome available anywhere in this file, and it is the outcome a
well-intentioned widening of this scope produces. The catalog note already says
the sweep reports and never edits a date or a link; a proposal's negative check
should name a document it must never edit and show that the empty scope excludes
every path, not just that one.

### Reversal

Nothing to reverse. Close the pull request unmerged if the scheduled workflow
opened one.

### Blast radius

Nothing written, nothing member-visible, nothing published. What accumulates is a
series of ledger entries.

The result is almost always clean: 0 broken links and 0 stale as-of dates across
every markdown file in the repository when this dossier was written. An identical
clean result every week
for months is its own hazard — after twenty identical entries nobody reads the
twenty-first, and the only difference between "checked, nothing stale" and "the
job stopped running" is whether an entry appeared.

### Evidence that exists today

- 34 tests in `tests/test_check_links.py`, and 56 in `tests/test_cadence.py`
  covering the same rule as the cadence report applies it.
- The rule has one source. `scripts/cadence.py` raises a configuration error and
  exits 1 rather than running with a limit that disagrees with
  `scripts/check_links.py`.
- `scripts/check_links.py` is a named step in
  [the CI workflow](../../.github/workflows/ci.yml) and runs on every pull
  request and every push to `main`.
- This is the one candidate whose result changes with the calendar rather than
  with a commit. A document goes stale on its ninety-first day whether or not
  anybody pushes, so a repository nobody touches for a quarter gets no CI run and
  no staleness signal. That gap is real, and it is the only unique value in this
  list.

### Evidence that does not exist

- No evidence about coverage, because coverage has never been reported. Measured
  directly on 2026-09-02: 20 of 342 markdown files carry a dated `As of:` line
  the rule can read — 22 lines in total. Another 23 files mention "as of" in a
  form the pattern cannot date, including [`ops/BUZZ_SECURITY.md`](../BUZZ_SECURITY.md), whose
  currency claim reads "based on the verified platform snapshot as of
  2026-09-01", and
  [`reviews/GUIDE_CURRENCY_AUDIT.md`](../../reviews/GUIDE_CURRENCY_AUDIT.md),
  which is itself the audit of claims that will rot. These counts move as files
  are added; re-measure before citing them. What does not move is the shape: the
  covered set is whatever matches one regular expression, and it is a small
  fraction of the corpus.
- No decision about the overlap with `cadence-snapshot`. The cadence report
  already contains the staleness half of this check, computed through the same
  functions in `scripts/check_links.py`, and prints it as "Stale as-of dates
  (limit 90d, rule from `scripts/check_links.py`; 22 date(s) checked)". Promoting
  both puts two unattended runs on one fact.
- No record of what a maintainer does with a stale finding. The ladder places the
  `stale_as_of` check at A0 and notes that deciding staleness stays the artifact
  maintainer's call; its raise column asks for R2 only if a human wants a drafted
  disposition per stale file.

### The specific way it goes wrong

**The half that goes stale is the half that never fails.** The sweep's exit code
is 1 only when a link is broken. Every as-of warning leaves the exit code at 0.
An unattended run judged by its exit status therefore reports success on a day
when every dated document in the repository is out of date, and the finding lives
only in text somebody has to read. The link half, which does fail loudly, is
already covered by CI on every push.

**A clean sweep reads as "the repository is current" when it has checked 22
lines.** Coverage is defined by a regular expression, not by the set of documents
whose currency matters.
[`reviews/GUIDE_CURRENCY_AUDIT.md`](../../reviews/GUIDE_CURRENCY_AUDIT.md)
records six findings about claims that will "silently rot" — undated maturity
restatements, a hard-coded task contract, channel membership claims — and not one
of them is a dated `As of:` line the sweep can see. A weekly clean sweep is
literally true and, read as a currency signal, badly misleading.

That is the general hazard this phase should be most careful about, in its
sharpest form: a stale artifact that looks maintained is worse than an obviously
absent one, and an automated currency check that can read a dated line in 20 of
342 files is a machine for making stale documents look maintained.

A third, narrower failure: the rule parses any regex-matching date with
`date.fromisoformat`, so a line reading `As of: 2026-02-30` raises an uncaught
`ValueError`. Verified. The sweep crashes rather than reporting a wrong answer,
which is the right direction — but a scheduled job whose only failure signal is a
red run in a log nobody opens has stopped quietly all the same.

### The decision, and what would have to exist first

The decision is whether the calendar-driven half of this check is worth a
scheduled run, and if so whether it belongs in its own operation at all rather
than in the cadence report that already computes it.

Before that decision could be made on facts: a coverage number carried in the
result itself, so no reader mistakes a clean sweep for a current repository; a
recorded decision on the overlap with `cadence-snapshot`, since two unattended
runs reporting one fact is a governance problem rather than a tooling one; a
statement of what an unattended run does with a warning that does not change the
exit code, since the exit code is what a workflow reads; and a named role who
receives a stale finding and owns the disposition, which
[`ops/cadence.yaml`](../cadence.yaml) currently routes to the follow-up queue and
a human.

---

## `release-brief-draft`

### What it would do unattended

Assemble a draft release brief from committed evidence over a commit range and
write it under `release/briefs/`. The generator lists every commit in the range
with the paths it changed that still exist, matches `swarm/handoffs/<id>.md` for a
commit whose subject names a task, quotes front-matter `maturity` and
`evidence_quality` values verbatim, and lists the owner-review rows recorded
open. Every line carries a path or a commit hash; anything it cannot back is
omitted.

The catalogued command is `python3 scripts/release_brief.py --root .`, and it is
deliberately incomplete. `scripts/release_brief.py` requires `--since` and
`--as-of`. Run exactly as catalogued it exits 2 and writes nothing, so this
operation cannot run at all until somebody decides who supplies those two inputs
and how.

### Write scope

`release/briefs/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-*.md`. The date-shaped
prefix excludes [the directory's README](../../release/briefs/README.md), so a
run cannot rewrite the rule its own output is read under. The directory holds
that README and one committed brief, `release/briefs/2026-09-02-phase-2.md`.

### Reversal

Delete the file, or close the pull request unmerged. The generator reads through
`git show <rev>:<path>` rather than the working tree, so a run has no side effect
outside its output file.

### Blast radius

One brief per run, in a directory whose README states that a brief is never an
announcement, a release, or an approval, and that publication requires a named
human maintainer to open each pointer, amend or approve or hold, and record the
approval with a name, a date, and the exact version approved. A month of weekly
runs is four unapproved drafts beside the one artifact that went through the
human path.

`release/` is walked by `scripts/validate.py --release`, so a brief carrying an
unfinished or publication token would break release validation. The generator
guards against this itself and is the only one of the five that does: it checks
its own output before writing, raises rather than emitting, exits 1, and writes
no file.

### Evidence that exists today

- 34 tests in `tests/test_release_brief.py`, plus a CI guard:
  [the workflow](../../.github/workflows/ci.yml) sets `fetch-depth: 0`
  specifically so the test that regenerates the committed Phase 2 brief over its
  commit range does not silently skip on a shallow clone, and
  `tests/test_contract_integration.py` asserts that setting stays.
- The self-guard is code, not prose: `check_release_tokens` refuses to write a
  brief containing an unfinished or publication token in visible prose, naming
  the token and the reason.
- Commit-subject text is contained. Subjects are rendered as inline code spans,
  and the helper replaces every backtick in the subject with an apostrophe, so
  text written by anyone whose change merged cannot break out of its span.
- Reproducibility: reads come from `git show`, never the working tree, so two
  runs over the same range produce identical bytes regardless of local edits.
- Every generated brief carries a draft banner and a section stating which human
  approvals are outstanding.
- One brief has been generated and committed, for Phase 2, by a human who chose
  the range.

### Evidence that does not exist

- No rule for choosing `--since` without a person. The flag is required, has no
  default, and names the first commit of the range inclusively. Nothing in the
  repository records how an unattended run would pick it, and the catalog note
  says so.
- No evidence about unapproved drafts accumulating, because the one committed
  brief went through the human path.
- No named release owner. "Human operating coverage" is recorded OPEN in
  [the owner review packet](../../release/OWNER_REVIEW.md) and blocks public
  launch; the role that would approve or hold each generated brief is unfilled.

### The specific way it goes wrong

**The range is an editorial judgment, and there is no honest default.** A brief
is a claim about a period. "Since the last tag" fails in a repository with no
release tags. "The last seven days" cuts a phase in half and produces a brief
that is accurate line by line and wrong about the whole. "Since the last brief"
makes each brief's correctness depend on the previous one having been right. The
generator's discipline — every line carries a pointer, nothing unbacked is
emitted — is discipline about lines, and no amount of it detects a wrong range. A
brief assembled over the wrong commits contains no false statement and still
describes nothing that happened.

**The second failure is accumulation.** `release/briefs/` holds one brief that a
human assembled and that CI regenerates as a guard. Four unapproved drafts a
month change what the directory is: from a record of work someone approved into a
stream of machine output where the approved and the unread look alike. The
README's rule — a brief is a draft until a named human maintainer approves it —
survives one draft and does not survive twenty, and there is no named release
owner to hold the line.

On eligibility: drafting is not publishing. The ladder is explicit that drafting
an announcement is not publication and that the boundary is the act, not the
preparation, so this operation is not on the permanently ineligible list. But the
ladder also maps the Release pass at A1 and records that it cannot rise, because
the pass ends in `publication-and-announcement`. An unattended writer stacking
drafts in the directory that feeds that pass is the near-neighbour rule's exact
subject, and a signer should treat it as one until a human says otherwise.

### The decision, and what would have to exist first

**This one is unsuitable as it stands**, for a reason about the operation rather
than the tooling: the tooling is the best-engineered of the five, and it still
cannot choose its own range. An operation whose central input is an editorial
judgment is not a candidate for running without the person who makes that
judgment — and as catalogued it does not run at all.

Before this could be reconsidered: a rule for the range that a human has written
down and would defend against the three failure cases above; a rule for `--as-of`
that does not silently mean "whatever the runner's clock said"; a named release
owner, currently held open by an operating hold; and a rule for what happens to a
draft nobody approves — deleted after a fixed window, or never written at all. If
the want is that a brief be ready when a human sits down to release, the cheaper
answer is a command in the Release pass, which is where
[the weekly cadence](../WEEKLY_CADENCE.md) already puts it.

---

## What all five have in common

Four things are true of every candidate here, and a proposer should not have to
rediscover them one dossier at a time.

**They are all reports, and a report can be wrong quietly for a long time.** None
of the five performs an irreversible act; all five produce a description. That
makes the reversal cheap and the wrongness cheap to miss. A wrong report does not
crash, does not fail a check, and does not look different from a right one — it
sits in the repository being cited. Each dossier names the specific form this
takes: the shallow-clone flattening in `cadence-snapshot`, the silent coverage
fall in `metrics-snapshot`, and the 20-of-342 coverage in `staleness-sweep` are
one failure wearing three coats.

**A dated series looks like a maintained practice whether or not anyone reads
it.** Recording a run on a schedule creates evidence that the loop is running.
That evidence is true about the schedule and says nothing about whether a human
read the output or acted on it. Not one of the five has a named role who has
agreed to read the result, and until one does, promotion buys a directory that
looks attended.

**Absence is the failure signal, and absence is invisible.** When any of these
jobs breaks, the symptom is that no new file and no new ledger entry appears.
There is no alarm in that, and the longer a series has been quietly correct the
less anybody looks. A signer answering section 5 of
[the proposal](PROMOTION_PROPOSAL.md) — blast radius after a month unnoticed —
should answer for the case where the operation stopped as well as the case where
it misbehaved.

**Most of what these operations do already runs somewhere.**
`scripts/validate_agents.py` and `scripts/check_links.py` are named CI steps on
every pull request and every push to `main`; `scripts/cadence.py`,
`scripts/collect_metrics.py`, and `scripts/release_brief.py` are on the recorded
CI exemption list precisely because their output is a report for a person rather
than a gate. The question a promotion answers is not "should this run" — it runs
— but "should it run with nobody watching, and who has agreed to watch the
result".

## Sources

As of: 2026-09-02.

- [docs/framework/AUTONOMY_LADDER.md](../../docs/framework/AUTONOMY_LADDER.md) —
  the A3 clauses, the demotion triggers, the permanently ineligible list, and the
  current level of every cadence operation.
- [ops/autonomy/operations.yaml](operations.yaml) — the authoritative catalog
  entry for each candidate, including the write scope the guard checks a
  promotion against.
- [ops/autonomy/PROMOTION_PROPOSAL.md](PROMOTION_PROPOSAL.md) and
  [ops/autonomy/README.md](README.md) — the record a signature goes on, and how
  the guard reads the two records behind it.
- `scripts/cadence.py`, `scripts/collect_metrics.py`, `scripts/check_links.py`,
  `scripts/release_brief.py`, and `scripts/validate_agents.py` — the
  implementations every claim above was read from.
- [.github/workflows/ci.yml](../../.github/workflows/ci.yml) — the checks that
  already run on every pull request and every push to `main`.
- [ops/OPERATING_LOOP.md](../OPERATING_LOOP.md) — what runs without a
  person today, and the failure modes it already names.
- [ops/cadence.yaml](../cadence.yaml),
  [ops/WEEKLY_CADENCE.md](../WEEKLY_CADENCE.md), [ops/METRICS.md](../METRICS.md),
  [ops/metrics/README.md](../metrics/README.md), and
  [release/briefs/README.md](../../release/briefs/README.md) — the operating
  documents each candidate would write into or against.
- [release/OWNER_REVIEW.md](../../release/OWNER_REVIEW.md) — the gates and holds
  every one of these operations repeats and none of them moves.
