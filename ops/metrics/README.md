# Repository metrics reports

## What this directory holds

This directory holds the operating notes for the metrics collector,
`scripts/collect_metrics.py`, and nothing else by default. The collector prints
a report or writes one to a path you name; it does not leave a report here.

Nothing in this directory is a measurement of the community. A generated report
is a description of what the committed files say, on the day it was produced.

## The problem it solves

[The measurement contract](../METRICS.md) is careful about evidence: count only
what a human can point to in a public Git change, a voluntary contribution
record, or a sanitized Buzz link; report a count with its denominator and its
evidence coverage; never profile individual behavior; never count joins, views,
or reactions.

Until now every one of those counts was made by hand, so the repository side of
the contract was only visible when a person sat down and counted. The collector
does the repository side, deterministically and offline, and refuses to do the
rest. It reads committed files. It has no access to the community.

## Running it

```sh
# Markdown to the terminal
python3 scripts/collect_metrics.py --root .

# A dated report written outside the repository
python3 scripts/collect_metrics.py --root . --as-of 2026-09-02 \
  --out ~/practice-review/metrics-2026-09-02.md

# Machine-readable output
python3 scripts/collect_metrics.py --root . --as-of 2026-09-02 --json
```

`--as-of` sets the report date and defaults to today. Two runs over the same
tree with the same `--as-of` produce identical bytes, so a report can be
diffed against an earlier one. Exit status is 0 when a report was produced and
2 for a usage error; the collector reports state and never fails a build.

Record the commit the report describes next to the report itself:

```sh
git rev-parse HEAD
```

Reports are generated on demand and are not committed. If maintainers decide to
retain one, keep it with the review record for that period and keep its commit
identifier with it, so a later reader can reproduce it.

## What the collector can see

| Section | What it counts | Denominator | Evidence coverage reported alongside |
| --- | --- | --- | --- |
| Artifact inventory | Artifacts by type, by declared state, by capability stage, and by declared evidence-quality label | All scored artifacts, or all artifacts of that type | How many artifact files parsed their front matter |
| Evidence coverage | Artifacts that state every evidence element the contract names | Artifacts of that type | Elements stated out of elements checked |
| Accepted contribution records | Dated entries in a committed artifact changelog | Scored artifacts | Artifacts carrying a non-empty changelog |
| Owner gates and operating holds | Rows recorded open in [the owner review packet](../../release/OWNER_REVIEW.md) | Rows in that table | Rows with a readable status cell |
| Link health | Internal markdown link targets that resolve | Internal targets checked | Markdown files scanned |

States and labels are read verbatim. The collector never writes a `maturity` or
`evidence_quality` value, and never asserts that an owner gate or operating hold
is cleared: it copies the recorded status and says so. Clearing a gate is a
human decision recorded by a human.

Front matter is parsed by reusing `scripts/validate_artifacts.py` and link
targets by reusing `scripts/check_links.py`, so the collector cannot drift away
from what the validators enforce.

### The evidence-element heading map

The Evidence metric asks whether an artifact states its inputs, steps, output,
evaluation method, limitations, and failure modes, with an inspectable record.
Those element names are not headings, so the collector maps each one onto the
headings the artifact's own schema defines. An element counts as stated when at
least one mapped heading exists and its section is not empty; a heading with
nothing under it does not count.

| Artifact type | Element | Headings that satisfy it |
| --- | --- | --- |
| Practice | inputs | `Inputs` |
| Practice | steps | `Method` |
| Practice | output | `Outcome` |
| Practice | evaluation | `Evaluation` |
| Practice | limitations | `Problem and scope` or `Use when` |
| Practice | failure modes | `Failure modes` |
| Practice | inspectable record | `Evidence` |
| Lab | inputs | `Task set` or `Fixed conditions` |
| Lab | steps | `Procedure` |
| Lab | output | `Results` |
| Lab | evaluation | `Evaluation rubric` |
| Lab | limitations | `Limitations` |
| Lab | inspectable record | `Reproduction` |
| Story | inputs | `Before` |
| Story | steps | `Intervention` or `Implementation` |
| Story | output | `After` |
| Story | evaluation | `Result` |
| Story | limitations | `Lessons` |
| Story | inspectable record | `Evidence record` |
| Guide | inputs | `Prerequisites` |
| Guide | steps | `Path` |
| Guide | output | `Outcomes` |
| Guide | evaluation | `Evaluation` |

The map is checked against the schemas in [docs/schemas](../../docs/schemas) as
of 2026-09-02. A Guide has no limitations or failure-modes section in its
schema, so a Guide is scored on four elements and its denominator says so
rather than counting the missing two as gaps. If a schema gains or renames a
section, update the map in `scripts/collect_metrics.py` and the table above in
the same change, or coverage will silently fall.

Guide modules and front-matter-less index documents are counted separately and
are not scored: neither is a standalone artifact.

## What the collector cannot see

Seven parts of the contract need a human. The collector prints each one as
`not collected` with the reason and the route from
[Minimal manual measurement at launch](../METRICS.md):

| Metric | Why a committed file cannot supply it |
| --- | --- |
| Activation | A first-value action by a new Practitioner is observed in a sanitized Buzz link or a voluntary record. A join, read, or reaction does not activate. |
| Contribution, proposed | Proposals live in open issues, drafts, and pull requests. Only accepted contributions already written into a committed changelog are counted. |
| Artifact reuse | Reuse needs a link or note from someone other than the author saying what was reused and what changed. A page view is not reuse. |
| Implementation | An implementation report is supplied by a Practitioner, with scope, human review point, and an owner-provided result. It is marked self-reported. |
| Response quality | A reviewed sample of actual responses, scored pass or needs-revision with a reason. |
| Retention | A comparison of one Practitioner's useful actions across two review periods, without using login or presence as a proxy. |
| Maintainer health | A once-per-period maintainer check-in: open review queue, oldest pending item, unresolved safety or licensing issues, and load status. |

Maintainer health is the one most easily confused with something the collector
does report. The open owner gates and operating holds it counts are a
repository record. They are not a maintainer check-in and they say nothing
about review load.

## Measured zero and not collected are different

A count of `0` in a report means the collector looked and found none. A metric
printed as `not collected` means the collector did not look, because committed
files cannot answer it. The contract is explicit that a missing measurement is a
prompt to improve instrumentation, not a zero, and the report keeps the two
apart on purpose.

When a report is summarized for anyone else, carry that distinction forward.
Turning `not collected` into `0` invents a result.

## Data the collector never reads

- member identities, aliases, and commit authorship: the collector never enters
  `.git`, so names and email addresses are unreachable to it;
- joins, reads, views, session duration, and message-read receipts;
- reactions, follower counts, and anything that could feed a ranking or
  leaderboard;
- message content from Buzz or any other hosted surface;
- any network resource: it opens no connection and reads only files under the
  root it was given.

There is no data structure for a person anywhere in the collector. This is a
property of the code, not a policy on top of it, which is why a report cannot
leak a member-level row.

## How to read a report

1. A report is evidence of repository state at one commit. It is not evidence of
   community health, capability, or outcomes, and it does not clear any owner
   gate or operating hold.
2. Read every count with its denominator. A count without one invites a
   comparison that the evidence does not support.
3. Do not compare two reports across a change in method without saying that the
   method changed. If the heading map or the collected set moved, record it.
4. A report says nothing about the people who wrote the artifacts, and must not
   be used to compare contributors.
5. Pair it with the human ledger described in the measurement contract. On its
   own it covers one of the three evidence sources, and the smaller part.

## Failure modes

| Signal | Likely cause | Action |
| --- | --- | --- |
| Evidence coverage drops with no content change | A schema heading was renamed and the map above is stale | Reconcile the map with the schemas before reading the number as a regression |
| An artifact appears under unreadable front matter | The file does not parse as its directory's type | Run `python3 scripts/validate_artifacts.py` for the file and line |
| Owner gates or holds print as not collected | The owner review packet moved or its status table changed shape | Restore the table, or fix the section lookup; do not treat a missing table as no open gates |
| A drift note appears about gate counts | The gate list and the review packet disagree | Reconcile the two documents before quoting either count |
| Changelog entries stop being counted | An artifact recorded a change without a date | Add the date; an undated entry is not a countable record |
| Link targets stop resolving | A file moved | Run `python3 scripts/check_links.py` for the file and line of each |
