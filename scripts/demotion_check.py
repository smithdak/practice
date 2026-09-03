#!/usr/bin/env python3
"""Evaluate the autonomy ladder's demotion triggers against the action ledger.

The ladder in ``docs/framework/AUTONOMY_LADDER.md`` names the events that
automatically demote an operation, and states them as observable events rather
than judgment calls. Every one of them was stated and none was detected. A
demotion trigger nobody evaluates is a paragraph, and an autonomy level that can
only ever go up is not a level.

This check enumerates those triggers by parsing the ladder, classifies each one
as evaluable here or not evaluable here, evaluates the evaluable ones against
the ledger entries in ``ops/ledger/`` and the working tree, and reports what
fired. It never transcribes the trigger list: a clause the ladder adds, drops,
or rewords is a loud failure rather than a silent gap.

**This tool detects and reports. It does not demote.** Removing a promotion from
``ops/autonomy/promotions.yaml`` is a human act, exactly as adding one is. This
script writes no file anywhere, holds no authority, and clears no gate: a run
that fires nothing is not evidence that an operation may run unattended, and a
run that fires something is a finding a human acts on.

Usage::

    python3 scripts/demotion_check.py --root .
    python3 scripts/demotion_check.py --root . --json

Exit codes: ``0`` when nothing fired and nothing was left unjudged, ``1`` when at
least one demotion trigger fired, a record disagreement was found, or a recorded
run could not be judged, and ``2`` on a usage error, including a ladder this
check cannot read.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import yaml


DEFAULT_ROOT = Path(__file__).resolve().parents[1]

LADDER_PATH = "docs/framework/AUTONOMY_LADDER.md"
LEDGER_DIR = "ops/ledger"
CATALOG_PATH = "ops/autonomy/operations.yaml"
PROMOTIONS_PATH = "ops/autonomy/promotions.yaml"
RENEWALS_PATH = "ops/autonomy/renewals.yaml"
SCHEMA_PATH = "docs/schemas/ACTION_LEDGER_SCHEMA.md"

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

INELIGIBLE_HEADING = "## Permanently ineligible for A3"

LEVEL_HEADING_RE = re.compile(r"^##\s+(A[0-3])\b")
DEMOTION_LEAD_RE = re.compile(r"^\*\*Automatic demotion(?:\s+to\s+(A[0-2]))?\.\*\*\s*(.*)$")
LADDER_ID_RE = re.compile(r"^`([a-z0-9]+(?:-[a-z0-9]+)*)`$")

LEVEL_ORDER = ("A0", "A1", "A2", "A3")
# What a fired trigger costs the operation that fired it. Levels are cumulative,
# so an A1 clause fired by an operation at A3 demotes it one step, to A2.
DEMOTED_TO = {"A0": "not_enabled", "A1": "A0", "A2": "A1", "A3": "A2"}

# Outcomes that record a run which actually did something. `refused` and
# `dry-run` are the guard working, not a violation.
ACTING_OUTCOMES = frozenset({"completed", "failed", "reverted"})

SAMPLE_PREFIX = "SAMPLE_"
PLACEHOLDER_RE = re.compile(r"^(todo|tbd|n/?a|none|null|unknown|pending|\?+|-+|\.+)$", re.IGNORECASE)
MIN_REVERSAL_LENGTH = 8
MATURITY_FIELD_RE = re.compile(r"^\s*(maturity|evidence_quality)\s*:", re.MULTILINE)

DETECTS_ONLY = (
    "This check detects and reports. It does not demote. Removing a promotion from "
    f"{PROMOTIONS_PATH} is a human act, exactly as adding one is, and this script writes no file."
)

# Finding kinds, in the order they are rendered.
KIND_TRIGGER = "demotion-trigger"
KIND_DISAGREEMENT = "record-disagreement"
KIND_UNJUDGED = "unjudged-record"
KIND_ORDER = (KIND_TRIGGER, KIND_DISAGREEMENT, KIND_UNJUDGED)


class UsageError(Exception):
    """The check cannot run: a bad argument, or a ladder it cannot read."""


# --- The ladder's trigger list ----------------------------------------------

@dataclass(frozen=True)
class Trigger:
    """One demotion clause as the ladder states it."""

    trigger_id: str
    level: str
    ordinal: int
    clause: str
    demotes_to: str


@dataclass(frozen=True)
class Classification:
    """This check's standing judgment about one ladder clause.

    ``tokens`` are the substrings that identify the clause in the ladder text,
    matched against a normalized form of the clause. They are how the check
    stays keyed to the document instead of to a transcribed copy: a clause that
    matches no classification, and a classification that matches no clause, are
    both loud failures.
    """

    key: str
    level: str
    tokens: tuple[str, ...]
    evaluable: bool
    basis: str
    reason: str
    detector: str | None = None


# `basis` values, so a reader can tell three different kinds of "no" apart.
BASIS_EVALUATED = "evaluated-here"
BASIS_DELEGATED = "delegated-to-another-command"
BASIS_NOT_OBSERVABLE = "not-observable-in-this-repository"
BASIS_MISSING_FIELD = "missing-record-field"


CLASSIFICATIONS: tuple[Classification, ...] = (
    # --- A0 observe ---------------------------------------------------------
    Classification(
        key="registry-entry-fails-validation",
        level="A0",
        tokens=("validate_agents.py", "fails on its entry"),
        evaluable=False,
        basis=BASIS_DELEGATED,
        reason=(
            "The trigger is the exit code of `python3 scripts/validate_agents.py --root .`, a "
            "separate command already run in CI and covered by tests/test_validate_agents.py. "
            "This check reads records and never shells out to another validator, so its own exit "
            "code stays a statement about recorded runs rather than about an unrelated file. Its "
            "subject is also an agent's registry entry, and every entry in buzz/agents/registry.yaml "
            "reads not_enabled while owner gate 6 is recorded OPEN, so no agent holds a level to "
            "lose. Run that command to evaluate this trigger."
        ),
    ),
    Classification(
        key="provenance-pointer-unresolved",
        level="A0",
        tokens=("provenance", "does not resolve"),
        evaluable=False,
        basis=BASIS_NOT_OBSERVABLE,
        reason=(
            "The pointer lives in an agent packet's Provenance section, and resolving it means "
            "reading the repository as it stood at the packet's recorded source_commit. This "
            "repository holds no packet file, no ledger field names a packet a run produced, and "
            "this check reads only the working tree as it stands now. `python3 "
            "scripts/validate_packet.py` checks a packet a human points it at, at the current "
            "commit; nothing here reads history."
        ),
    ),
    Classification(
        key="read-outside-recorded-scope",
        level="A0",
        tokens=("reads a channel or path outside",),
        evaluable=False,
        basis=BASIS_MISSING_FIELD,
        reason=(
            "A ledger entry records paths_read but no read scope to judge it against. Neither "
            f"{CATALOG_PATH} nor {PROMOTIONS_PATH} carries one either: write_scope is the only "
            "bound either record states. Channels appear in no ledger field at all. Missing "
            f"record field: a read scope on the operation record. {SCHEMA_PATH} already "
            "anticipates it, listing this trigger as readable from 'paths_read against a read "
            "scope when the operation's record carries one' - and none does."
        ),
    ),
    Classification(
        key="enablement-prerequisite-stopped-holding",
        level="A0",
        tokens=("enablement prerequisite", "stops holding"),
        evaluable=False,
        basis=BASIS_NOT_OBSERVABLE,
        reason=(
            "Whether an escalation route still reaches a human is an event outside this "
            "repository. A file can record that a route is named; no file can record that a "
            "person answered. `scripts/steward_readiness_check.py` exists because a human runs "
            "that test against a live route."
        ),
    ),
    # --- A1 draft -----------------------------------------------------------
    Classification(
        key="draft-without-human-acceptance",
        level="A1",
        tokens=("reaches the repository", "human acceptance"),
        evaluable=False,
        basis=BASIS_MISSING_FIELD,
        reason=(
            "Nothing links a written path to a human acceptance. The ledger has no acceptance "
            "field, and the Phase 4 design routes acceptance through a merged pull request, which "
            "a checkout cannot see. Missing record field: an acceptance reference on the ledger "
            "entry naming the pull request or the approving commit. Until one exists, an entry "
            "recording a completed write is indistinguishable from an accepted one."
        ),
    ),
    Classification(
        key="write-outside-scope",
        level="A1",
        tokens=("edits a path outside",),
        evaluable=True,
        basis=BASIS_EVALUATED,
        detector="write_outside_scope",
        reason=(
            "Compares every path in an entry's paths_written against the write_scope the same "
            "entry recorded at run time, matching each glob with fnmatch against the "
            f"repository-relative POSIX path, as {CATALOG_PATH} documents. Judged at every level: "
            "at A0 the level permits no write at all, so an empty scope makes any write a "
            "violation."
        ),
    ),
    Classification(
        key="maturity-or-evidence-change",
        level="A1",
        tokens=("maturity", "evidence_quality"),
        evaluable=True,
        basis=BASIS_EVALUATED,
        detector="maturity_or_evidence_write",
        reason=(
            "Fires when an entry's paths_written names a file that currently carries a `maturity:` "
            "or `evidence_quality:` field. It detects the write to such a file, never the value "
            "change: no diff is recorded in the ledger. A fired finding is a file for a human to "
            "read the diff of. A written path that no longer exists under the root cannot be "
            "opened, and the report names every such path under Limits."
        ),
    ),
    Classification(
        key="packet-forbidden-assertion",
        level="A1",
        tokens=("forbidden-assertion",),
        evaluable=False,
        basis=BASIS_DELEGATED,
        reason=(
            "The check is the forbidden-assertion rule inside `scripts/validate_packet.py`, run on "
            "a packet a human points it at. This repository contains no packet file, and no ledger "
            "field names the packet a run produced, so there is nothing here to run it against."
        ),
    ),
    # --- A2 recommend -------------------------------------------------------
    Classification(
        key="posted-outside-write-channels",
        level="A2",
        tokens=("channel absent from",),
        evaluable=False,
        basis=BASIS_NOT_OBSERVABLE,
        reason=(
            "The event is a post in a Buzz channel. The ledger records paths, never channels or "
            "messages, and the channel record is outside this repository. Missing input: the "
            "channel transcript, plus a ledger field naming the channel a run posted into."
        ),
    ),
    Classification(
        key="message-states-action-as-taken",
        level="A2",
        tokens=("states an action as taken",),
        evaluable=False,
        basis=BASIS_NOT_OBSERVABLE,
        reason=(
            "Judging the wording needs the delivered message, which lives in the channel record "
            "outside this repository. The rule that would judge it exists in "
            "`scripts/validate_packet.py`, but that reads a packet, and a delivered message is not "
            "a packet and is not committed here."
        ),
    ),
    Classification(
        key="followed-untrusted-instruction",
        level="A2",
        tokens=("untrusted channel content",),
        evaluable=False,
        basis=BASIS_NOT_OBSERVABLE,
        reason=(
            "The clause names its own evidence: the instruction and the reply are both in the "
            "channel record. That record is outside this repository, and nothing in the ledger "
            "carries either half."
        ),
    ),
    Classification(
        key="escalation-receipt-failed",
        level="A2",
        tokens=("human-receipt test",),
        evaluable=False,
        basis=BASIS_NOT_OBSERVABLE,
        reason=(
            "A human receipt is an event outside the repository. No committed file can record "
            "that a person answered a route; a human runs the receipt test and records the result."
        ),
    ),
    # --- A3 act-unattended-within-bounds ------------------------------------
    Classification(
        key="acted-outside-recorded-bound",
        level="A3",
        tokens=("action taken outside", "bound"),
        evaluable=True,
        basis=BASIS_EVALUATED,
        detector="acted_outside_recorded_bound",
        reason=(
            "Fires when an entry records that the run acted - outcome completed, failed or "
            "reverted, or any path written - while the bound it recorded did not permit it: a "
            "precondition recorded result fail, the kill switch read engaged, or no promotion was "
            "observed while the run claimed A3. An entry whose outcome is refused or dry-run and "
            "which wrote nothing does not fire this: that is the guard working."
        ),
    ),
    Classification(
        key="no-reversal-recorded",
        level="A3",
        tokens=("no reversal path",),
        evaluable=True,
        basis=BASIS_EVALUATED,
        detector="no_reversal_recorded",
        reason=(
            "Fires when an entry records that the run acted and its reversal field is absent, "
            "blank, shorter than eight characters, or a placeholder such as `n/a`. "
            "`scripts/ledger.py` refuses to write such an entry; this check re-reads the field "
            "because an entry can reach the repository without passing that validator."
        ),
    ),
    Classification(
        key="acted-after-review-point",
        level="A3",
        tokens=("review point",),
        evaluable=True,
        basis=BASIS_EVALUATED,
        detector="acted_after_review_point",
        reason=(
            "Fires when an entry records that the run acted and its run_date is after the "
            "promotion.review_point the run recorded - the review point in force on the run "
            f"date, as the guard computed it - unless {RENEWALS_PATH} carries a renewal for that "
            "promotion (same operation, same promotion signing date) with renewed_on on or before "
            "the run date and review_point on or after it. A covering renewal turns the finding "
            "into a record disagreement instead: the run recorded a stale review point. An acting "
            "entry that claims A3 and records no review_point, or one that cannot be read as a "
            "date, is reported as unjudged and never counted as clear. A renewal record that is "
            "missing or unreadable excuses nothing: silence is not renewal."
        ),
    ),
    Classification(
        key="operation-since-made-ineligible",
        level="A3",
        tokens=("permanently ineligible",),
        evaluable=True,
        basis=BASIS_EVALUATED,
        detector="operation_since_made_ineligible",
        reason=(
            "Reads the operation ids listed in the ladder's "
            f"'{INELIGIBLE_HEADING}' table and fires when an entry records that a run acted on one "
            "of them. The list is read from the ladder at run time, never transcribed, so an "
            "operation a governance amendment adds is honored without editing this script. A "
            "ladder whose table cannot be read is reported as unjudged, never as clear."
        ),
    ),
)


def normalize_clause(text: str) -> str:
    """Lowercase, strip backticks, and collapse whitespace, for token matching."""
    return re.sub(r"\s+", " ", text.replace("`", "")).strip().lower()


def read_ladder(root: Path) -> list[str]:
    path = root / LADDER_PATH
    if not path.is_file():
        raise UsageError(
            f"{LADDER_PATH} does not exist under {root}. This check enumerates the demotion "
            "triggers from that document; without it there is no trigger list to evaluate, and "
            "reporting zero triggers would be worse than failing."
        )
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def parse_ladder_triggers(root: Path) -> list[Trigger]:
    """Return every demotion clause the ladder states, in document order.

    Raises ``UsageError`` when the ladder carries no level section, when a level
    section carries no ``**Automatic demotion...**`` paragraph, or when such a
    paragraph yields no clause. Failing loudly is the point: a parser that
    returned an empty list would report a clean repository for a document it
    could not read.
    """
    lines = read_ladder(root)
    level: str | None = None
    counts: dict[str, int] = {}
    triggers: list[Trigger] = []
    seen_levels: list[str] = []

    index = 0
    while index < len(lines):
        line = lines[index]
        heading = LEVEL_HEADING_RE.match(line)
        if heading:
            level = heading.group(1)
            if level not in seen_levels:
                seen_levels.append(level)
            index += 1
            continue
        if line.startswith("## "):
            level = None
            index += 1
            continue
        lead = DEMOTION_LEAD_RE.match(line)
        if not lead:
            index += 1
            continue
        if level is None:
            raise UsageError(
                f"{LADDER_PATH} line {index + 1}: an 'Automatic demotion' paragraph sits outside "
                "any '## A0'..'## A3' level section, so this check cannot say which level it "
                "lowers. Move it under its level heading."
            )
        paragraph = [lead.group(2)]
        cursor = index + 1
        while cursor < len(lines) and lines[cursor].strip():
            paragraph.append(lines[cursor])
            cursor += 1
        clauses = split_clauses(" ".join(paragraph))
        if not clauses:
            raise UsageError(
                f"{LADDER_PATH} line {index + 1}: the '{level}' automatic-demotion paragraph lists "
                "no trigger. This check expects the clauses after the first colon, separated by "
                "semicolons. Restore the list or update parse_ladder_triggers in "
                "scripts/demotion_check.py."
            )
        for clause in clauses:
            counts[level] = counts.get(level, 0) + 1
            triggers.append(
                Trigger(
                    trigger_id=f"{level}-{counts[level]}",
                    level=level,
                    ordinal=counts[level],
                    clause=clause,
                    demotes_to=lead.group(1) or DEMOTED_TO[level],
                )
            )
        index = cursor

    if not seen_levels:
        raise UsageError(
            f"{LADDER_PATH} carries no '## A0'..'## A3' level section. This check reads the "
            "demotion triggers from those sections; a missing anchor is a failure, not a pass. "
            "Restore the sections or update LEVEL_HEADING_RE in scripts/demotion_check.py."
        )
    missing = [name for name in LEVEL_ORDER if name not in seen_levels]
    if missing:
        raise UsageError(
            f"{LADDER_PATH} has no section for {', '.join(missing)}. Every level states the "
            "triggers that lower it, so a missing section is a trigger list this check cannot "
            "read. Restore the section or update LEVEL_ORDER in scripts/demotion_check.py."
        )
    empty = [name for name in LEVEL_ORDER if not counts.get(name)]
    if empty:
        raise UsageError(
            f"{LADDER_PATH}: the {', '.join(empty)} section(s) carry no "
            "'**Automatic demotion...**' paragraph. This check refuses to report zero triggers "
            "for a level whose trigger list it could not find. Restore the paragraph or update "
            "DEMOTION_LEAD_RE in scripts/demotion_check.py."
        )
    return triggers


def split_clauses(paragraph: str) -> list[str]:
    """Split a demotion paragraph into its clauses.

    The paragraph introduces its list with a colon and separates clauses with
    semicolons; the last clause is introduced by `or`.
    """
    _, separator, listed = paragraph.partition(":")
    if not separator:
        return []
    clauses = []
    for raw in listed.split(";"):
        clause = raw.strip()
        if clause.lower().startswith("or "):
            clause = clause[3:].strip()
        clause = clause.rstrip(".").strip()
        if clause:
            clauses.append(clause)
    return clauses


@dataclass(frozen=True)
class ClassifiedTrigger:
    trigger: Trigger
    classification: Classification


def classify_triggers(triggers: list[Trigger]) -> list[ClassifiedTrigger]:
    """Pair every ladder clause with exactly one standing classification.

    Drift in either direction is a ``UsageError``. A clause with no
    classification means the ladder now names a trigger nobody has decided
    about; a classification with no clause means this script carries a judgment
    about a trigger the ladder no longer states. Both are governance changes a
    human must see, so neither is allowed to pass quietly.
    """
    paired: list[ClassifiedTrigger] = []
    used: dict[str, str] = {}
    for trigger in triggers:
        text = normalize_clause(trigger.clause)
        matches = [
            item
            for item in CLASSIFICATIONS
            if item.level == trigger.level and all(token.lower() in text for token in item.tokens)
        ]
        if not matches:
            raise UsageError(
                f"{LADDER_PATH}: the {trigger.level} trigger \"{trigger.clause}\" matches no "
                "classification in scripts/demotion_check.py, so this check cannot say whether it "
                "is evaluable here. Add a Classification for it to CLASSIFICATIONS rather than "
                "letting an unclassified trigger pass as clear."
            )
        if len(matches) > 1:
            names = ", ".join(sorted(item.key for item in matches))
            raise UsageError(
                f"{LADDER_PATH}: the {trigger.level} trigger \"{trigger.clause}\" matches more "
                f"than one classification ({names}). Narrow their `tokens` in "
                "scripts/demotion_check.py so each trigger maps to exactly one judgment."
            )
        item = matches[0]
        if item.key in used:
            raise UsageError(
                f"{LADDER_PATH}: classification '{item.key}' matches both \"{used[item.key]}\" and "
                f"\"{trigger.clause}\". Narrow its `tokens` in scripts/demotion_check.py."
            )
        used[item.key] = trigger.clause
        paired.append(ClassifiedTrigger(trigger=trigger, classification=item))
    orphans = sorted(item.key for item in CLASSIFICATIONS if item.key not in used)
    if orphans:
        raise UsageError(
            f"{LADDER_PATH} no longer states the trigger(s) classified here as "
            f"{', '.join(orphans)}. Removing a demotion trigger is a governance change, not an "
            "editorial one: restore the clause, or remove its Classification from "
            "scripts/demotion_check.py deliberately."
        )
    return paired


def read_ineligible_operations(root: Path) -> tuple[set[str] | None, str | None]:
    """Return the ids the ladder marks permanently ineligible, and why not if absent."""
    lines = read_ladder(root)
    start = None
    for index, line in enumerate(lines):
        if line.strip() == INELIGIBLE_HEADING:
            start = index + 1
            break
    if start is None:
        return None, (
            f"{LADDER_PATH} has no '{INELIGIBLE_HEADING}' section, so the operations that may "
            "never run unattended cannot be read. Restore the section or update "
            "INELIGIBLE_HEADING in scripts/demotion_check.py."
        )
    found: set[str] = set()
    for line in lines[start:]:
        if line.startswith("## "):
            break
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells:
            match = LADDER_ID_RE.match(cells[0])
            if match:
                found.add(match.group(1))
    if not found:
        return None, (
            f"{LADDER_PATH}: the '{INELIGIBLE_HEADING}' section lists no operation id in its first "
            "table column, so this check cannot tell which operations may never run unattended."
        )
    return found, None


# --- Ledger entries ---------------------------------------------------------

@dataclass
class Record:
    """One ledger entry, read as the run left it."""

    path: Path
    relative: str
    data: dict
    is_sample: bool = False

    @property
    def run_id(self) -> str:
        return text_of(self.data.get("run_id")) or "(no run_id recorded)"

    @property
    def operation(self) -> str:
        return text_of(self.data.get("operation")) or "(no operation recorded)"

    @property
    def claimed_level(self) -> str:
        value = text_of(self.data.get("claimed_level"))
        return value if value in LEVEL_ORDER else ""

    @property
    def outcome(self) -> str:
        return text_of(self.data.get("outcome"))

    @property
    def kill_switch(self) -> str:
        return text_of(self.data.get("kill_switch"))

    @property
    def paths_written(self) -> list[str]:
        return string_list(self.data.get("paths_written"))

    @property
    def write_scope(self) -> list[str]:
        return string_list(self.data.get("write_scope"))

    @property
    def preconditions(self) -> list[dict]:
        value = self.data.get("preconditions")
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

    @property
    def failed_preconditions(self) -> list[dict]:
        return [item for item in self.preconditions if text_of(item.get("result")) == "fail"]

    @property
    def promotion_observed(self) -> bool:
        return isinstance(self.data.get("promotion"), dict)

    @property
    def promotion(self) -> dict:
        value = self.data.get("promotion")
        return value if isinstance(value, dict) else {}

    @property
    def run_date(self) -> date | None:
        return parse_date(self.data.get("run_date"))

    @property
    def acted(self) -> bool:
        return self.outcome in ACTING_OUTCOMES or bool(self.paths_written)

    @property
    def demoted_to(self) -> str:
        return DEMOTED_TO.get(self.claimed_level, "not_enabled")


def text_of(value) -> str:
    return value.strip() if isinstance(value, str) else ""


def rendered_date(value) -> str:
    """The date as the record wrote it, for a finding a human reads."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return text_of(value) if isinstance(value, str) else repr(value)


def parse_date(value) -> date | None:
    """Read a front-matter date: a YAML date, or an ISO string. Anything else is None."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and ISO_DATE_RE.match(value.strip()):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def string_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def split_front_matter(text: str) -> str | None:
    """Return the YAML front matter of an entry file, or ``None`` when absent."""
    if not text.startswith("---"):
        return None
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index])
    return None


def collect_entry_files(root: Path) -> list[Path]:
    directory = root / LEDGER_DIR
    if not directory.is_dir():
        return []
    return sorted(path for path in directory.rglob("*.md") if path.name != "README.md")


def display(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


# --- Findings ---------------------------------------------------------------

@dataclass
class Finding:
    kind: str
    trigger_id: str
    trigger_key: str
    level: str
    clause: str
    entry: str
    run_id: str
    operation: str
    claimed_level: str
    demoted_to: str
    declared: str
    observed: str
    next_step: str

    def sort_key(self) -> tuple:
        return (KIND_ORDER.index(self.kind), self.entry, self.trigger_id, self.observed)

    def to_json(self) -> dict:
        return {
            "kind": self.kind,
            "trigger_id": self.trigger_id,
            "trigger_key": self.trigger_key,
            "level": self.level,
            "clause": self.clause,
            "entry": self.entry,
            "run_id": self.run_id,
            "operation": self.operation,
            "claimed_level": self.claimed_level,
            "operation_demoted_to": self.demoted_to,
            "declared": self.declared,
            "observed": self.observed,
            "next_step": self.next_step,
        }


@dataclass
class Context:
    root: Path
    ineligible: set[str] | None
    catalog: dict[str, dict] | None
    promoted_operations: set[str]
    # Renewals read from RENEWALS_PATH, each with its dates parsed. ``None``
    # when the record is missing or unreadable, which excuses nothing.
    renewals: list[dict] | None = None
    notes: list[str] = field(default_factory=list)
    limits: list[str] = field(default_factory=list)


def promotion_sentence(ctx: Context, operation: str) -> str:
    if operation in ctx.promoted_operations:
        return (
            f"A promotion for `{operation}` is recorded in {PROMOTIONS_PATH}. Deciding whether to "
            "remove it is a human edit to that file; this check does not make it."
        )
    return (
        f"No promotion for `{operation}` is recorded in {PROMOTIONS_PATH}, so there is none to "
        "remove and the operation is already at its catalogued level. The finding still needs a "
        "human: it records that a run acted anyway."
    )


def path_in_scope(path: str, patterns: list[str]) -> bool:
    """Match one written path against a write scope, as the catalog documents."""
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


# --- Detectors --------------------------------------------------------------
#
# Each takes the shared context, one record, and the ladder clause it evaluates,
# and returns the findings that clause fires for that record.

def detect_write_outside_scope(ctx: Context, record: Record, item: ClassifiedTrigger) -> list[Finding]:
    scope = record.write_scope
    outside = [path for path in record.paths_written if not path_in_scope(path, scope)]
    if not outside:
        return []
    declared = ", ".join(scope) if scope else "write_scope: [] (the run may write nothing)"
    return [
        Finding(
            kind=KIND_TRIGGER,
            trigger_id=item.trigger.trigger_id,
            trigger_key=item.classification.key,
            level=item.trigger.level,
            clause=item.trigger.clause,
            entry=record.relative,
            run_id=record.run_id,
            operation=record.operation,
            claimed_level=record.claimed_level or "(not recorded)",
            demoted_to=record.demoted_to,
            declared=f"write_scope recorded by the run: {declared}",
            observed=f"paths_written outside that scope: {', '.join(sorted(outside))}",
            next_step=(
                f"Open {record.relative} and read the diff for {', '.join(sorted(outside))}. "
                + promotion_sentence(ctx, record.operation)
            ),
        )
    ]


def detect_maturity_or_evidence_write(
    ctx: Context, record: Record, item: ClassifiedTrigger
) -> list[Finding]:
    hits: list[str] = []
    for relative in record.paths_written:
        candidate = ctx.root / relative
        if not candidate.is_file():
            ctx.limits.append(
                f"{record.relative}: paths_written names `{relative}`, which does not exist under "
                "the root, so it could not be read for a `maturity:` or `evidence_quality:` field."
            )
            continue
        try:
            text = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            ctx.limits.append(f"{record.relative}: `{relative}` could not be read ({exc}).")
            continue
        if MATURITY_FIELD_RE.search(text):
            hits.append(relative)
    if not hits:
        return []
    return [
        Finding(
            kind=KIND_TRIGGER,
            trigger_id=item.trigger.trigger_id,
            trigger_key=item.classification.key,
            level=item.trigger.level,
            clause=item.trigger.clause,
            entry=record.relative,
            run_id=record.run_id,
            operation=record.operation,
            claimed_level=record.claimed_level or "(not recorded)",
            demoted_to=record.demoted_to,
            declared=(
                "No run may change a `maturity` or `evidence_quality` value; the ladder lists "
                "`maturity-promotion` as permanently ineligible for A3."
            ),
            observed=(
                "paths_written names file(s) that carry a `maturity:` or `evidence_quality:` "
                f"field: {', '.join(sorted(hits))}. The ledger records no diff, so this check "
                "reports the write, not the value change."
            ),
            next_step=(
                f"Read the diff for {', '.join(sorted(hits))} and confirm no maturity or "
                "evidence_quality value moved. " + promotion_sentence(ctx, record.operation)
            ),
        )
    ]


def detect_acted_outside_recorded_bound(
    ctx: Context, record: Record, item: ClassifiedTrigger
) -> list[Finding]:
    if not record.acted:
        return []
    observed: list[str] = []
    for failure in record.failed_preconditions:
        check = text_of(failure.get("check")) or "(unnamed check)"
        detail = text_of(failure.get("detail")) or "(no detail recorded)"
        observed.append(f"precondition `{check}` recorded result: fail - {detail}")
    if record.claimed_level == "A3":
        if record.kill_switch == "engaged":
            observed.append(
                "the run recorded kill_switch: engaged, which refuses every operation regardless "
                "of promotion, and acted anyway"
            )
        if not record.promotion_observed:
            observed.append(
                "the run claimed A3 and recorded promotion: none, so it acted with no bound a "
                "human had recorded in advance"
            )
    if not observed:
        return []
    return [
        Finding(
            kind=KIND_TRIGGER,
            trigger_id=item.trigger.trigger_id,
            trigger_key=item.classification.key,
            level=item.trigger.level,
            clause=item.trigger.clause,
            entry=record.relative,
            run_id=record.run_id,
            operation=record.operation,
            claimed_level=record.claimed_level or "(not recorded)",
            demoted_to=record.demoted_to,
            declared=(
                "A run acts only inside a bound recorded in advance: every precondition passing, "
                "the kill switch released, and a signed promotion for the operation."
            ),
            observed=(
                f"outcome: {record.outcome or '(not recorded)'}, "
                f"paths_written: {len(record.paths_written)}; " + "; ".join(observed)
            ),
            next_step=(
                f"Open {record.relative}, then reverse the run using its recorded reversal. "
                + promotion_sentence(ctx, record.operation)
            ),
        )
    ]


def detect_no_reversal_recorded(
    ctx: Context, record: Record, item: ClassifiedTrigger
) -> list[Finding]:
    if not record.acted:
        return []
    reversal = text_of(record.data.get("reversal"))
    if reversal and len(reversal) >= MIN_REVERSAL_LENGTH and not PLACEHOLDER_RE.match(reversal):
        return []
    observed = f"reversal: {reversal!r}" if reversal else "reversal: absent or blank"
    return [
        Finding(
            kind=KIND_TRIGGER,
            trigger_id=item.trigger.trigger_id,
            trigger_key=item.classification.key,
            level=item.trigger.level,
            clause=item.trigger.clause,
            entry=record.relative,
            run_id=record.run_id,
            operation=record.operation,
            claimed_level=record.claimed_level or "(not recorded)",
            demoted_to=record.demoted_to,
            declared=(
                "Every run records the reversal a human can execute without the agent, in at "
                f"least {MIN_REVERSAL_LENGTH} characters and never a placeholder."
            ),
            observed=(
                f"the run acted (outcome: {record.outcome or '(not recorded)'}, "
                f"paths_written: {len(record.paths_written)}) and {observed}"
            ),
            next_step=(
                f"Reconstruct how to undo {record.run_id} from paths_written in {record.relative}, "
                "record it in a new ledger entry naming this one in `supersedes`, and execute it. "
                + promotion_sentence(ctx, record.operation)
            ),
        )
    ]


def detect_operation_since_made_ineligible(
    ctx: Context, record: Record, item: ClassifiedTrigger
) -> list[Finding]:
    if ctx.ineligible is None or not record.acted:
        return []
    operation = text_of(record.data.get("operation"))
    if operation not in ctx.ineligible:
        return []
    return [
        Finding(
            kind=KIND_TRIGGER,
            trigger_id=item.trigger.trigger_id,
            trigger_key=item.classification.key,
            level=item.trigger.level,
            clause=item.trigger.clause,
            entry=record.relative,
            run_id=record.run_id,
            operation=record.operation,
            claimed_level=record.claimed_level or "(not recorded)",
            demoted_to=record.demoted_to,
            declared=(
                f"{LADDER_PATH} lists `{operation}` under '{INELIGIBLE_HEADING}'. No amount of "
                "evidence raises it, and no run may perform it."
            ),
            observed=(
                f"the entry records a run of `{operation}` that acted (outcome: "
                f"{record.outcome or '(not recorded)'}, paths_written: "
                f"{len(record.paths_written)})"
            ),
            next_step=(
                f"Reverse the run using the reversal in {record.relative}. Removing `{operation}` "
                f"from {CATALOG_PATH} and from any promotion is a human act. "
                + promotion_sentence(ctx, record.operation)
            ),
        )
    ]


def covering_renewal(ctx: Context, record: Record, run_date: date) -> dict | None:
    """The latest renewal that covers ``run_date`` for the promotion the run recorded.

    A renewal covers a run when it names the same operation and the same
    promotion signing date, was signed on or before the run date, and sets a
    review point on or after it. A renewal record that could not be read is
    treated as empty: an unreadable renewal is not a renewal.
    """
    if not ctx.renewals:
        return None
    operation = text_of(record.data.get("operation"))
    signed_on = parse_date(record.promotion.get("signed_on"))
    matching = [
        item
        for item in ctx.renewals
        if item["operation"] == operation
        and signed_on is not None
        and item["promotion_signed_on"] == signed_on
        and item["renewed_on"] <= run_date <= item["review_point"]
    ]
    if not matching:
        return None
    return max(matching, key=lambda item: item["renewed_on"])


def detect_acted_after_review_point(
    ctx: Context, record: Record, item: ClassifiedTrigger
) -> list[Finding]:
    if not record.acted:
        return []
    common = dict(
        trigger_id=item.trigger.trigger_id,
        trigger_key=item.classification.key,
        level=item.trigger.level,
        clause=item.trigger.clause,
        entry=record.relative,
        run_id=record.run_id,
        operation=record.operation,
        claimed_level=record.claimed_level or "(not recorded)",
        demoted_to=record.demoted_to,
    )
    if not record.promotion_observed:
        # No promotion means no review point to be after; the bound trigger
        # (acted outside the recorded bound) is the one that fires for that.
        return []
    raw_review_point = record.promotion.get("review_point")
    review_point = parse_date(raw_review_point)
    run_date = record.run_date
    if review_point is None or run_date is None:
        if raw_review_point is None:
            observed = (
                "the run acted with a promotion recorded and no promotion.review_point, so "
                "there is no date to judge the run against"
            )
        elif review_point is None:
            observed = (
                f"promotion.review_point is {rendered_date(raw_review_point)!r}, which is not "
                "a date this check can read"
            )
        else:
            observed = (
                f"run_date is {rendered_date(record.data.get('run_date'))!r}, which is not a "
                "date this check can read"
            )
        return [
            Finding(
                kind=KIND_UNJUDGED,
                declared=(
                    "An acting run records the review point in force on its run date, as "
                    f"{SCHEMA_PATH} requires, so this trigger can be judged from the entry."
                ),
                observed=observed,
                next_step=(
                    f"Open {record.relative} and the promotion it ran under, establish the "
                    "review point that was in force, and correct the record forward with a new "
                    "entry naming this one in `supersedes`. Until then the run is unjudged, "
                    "never clear. " + promotion_sentence(ctx, record.operation)
                ),
                **common,
            )
        ]
    if run_date <= review_point:
        return []
    renewal = covering_renewal(ctx, record, run_date)
    if renewal is not None:
        return [
            Finding(
                kind=KIND_DISAGREEMENT,
                declared=(
                    f"{RENEWALS_PATH} (renewals[{renewal['index']}]) renews this promotion on "
                    f"{renewal['renewed_on'].isoformat()} with review point "
                    f"{renewal['review_point'].isoformat()}, which covers the run date."
                ),
                observed=(
                    f"the entry records promotion.review_point {review_point.isoformat()} and "
                    f"run_date {run_date.isoformat()}: a stale review point, recorded after the "
                    "renewal that superseded it"
                ),
                next_step=(
                    f"Compare {record.relative} with {RENEWALS_PATH} in Git history: either the "
                    "renewal was recorded after the run and back-dated, or the runner recorded "
                    "the promotion's own review point instead of the effective one. The trigger "
                    "did not fire because the renewal covers the run, but a record that "
                    "disagrees with the renewal record needs a human to say why."
                ),
                **dict(common, trigger_id="-", trigger_key="review-point-disagreement"),
            )
        ]
    if ctx.renewals is None:
        renewal_state = f"{RENEWALS_PATH} could not be read, and an unreadable renewal is not a renewal"
    else:
        renewal_state = (
            f"{RENEWALS_PATH} carries no renewal for this promotion that was signed on or "
            "before the run date and sets a review point on or after it"
        )
    return [
        Finding(
            kind=KIND_TRIGGER,
            declared=(
                "A bound ends at its review point unless a human records a renewal. Silence "
                "is not renewal."
            ),
            observed=(
                f"the run acted (outcome: {record.outcome or '(not recorded)'}, paths_written: "
                f"{len(record.paths_written)}) on {run_date.isoformat()}, after the recorded "
                f"review point {review_point.isoformat()}; {renewal_state}"
            ),
            next_step=(
                f"Reverse the run using the reversal in {record.relative}. Renewing the bound is "
                f"a new entry in {RENEWALS_PATH}; withdrawing it is an edit to {PROMOTIONS_PATH}. "
                "Both are human acts. " + promotion_sentence(ctx, record.operation)
            ),
            **common,
        )
    ]


DETECTORS = {
    "write_outside_scope": detect_write_outside_scope,
    "maturity_or_evidence_write": detect_maturity_or_evidence_write,
    "acted_outside_recorded_bound": detect_acted_outside_recorded_bound,
    "no_reversal_recorded": detect_no_reversal_recorded,
    "operation_since_made_ineligible": detect_operation_since_made_ineligible,
    "acted_after_review_point": detect_acted_after_review_point,
}


# --- Record disagreement ----------------------------------------------------

def detect_catalog_disagreement(ctx: Context, record: Record) -> list[Finding]:
    """Report an entry whose recorded write scope no longer matches the catalog.

    This is not a ladder trigger. It is a disagreement between two records that
    were equal when the run happened, which means one of them changed
    afterwards. It matters because it makes the scope trigger unjudgeable under
    today's rules: a human has to say which record is right.
    """
    if ctx.catalog is None:
        return []
    operation = text_of(record.data.get("operation"))
    if not operation:
        return []
    catalogued = ctx.catalog.get(operation)
    if catalogued is None:
        return [
            Finding(
                kind=KIND_DISAGREEMENT,
                trigger_id="-",
                trigger_key="catalog-disagreement",
                level=record.claimed_level or "(not recorded)",
                clause=(
                    "A recorded run's operation is no longer catalogued, so the bound it ran "
                    "inside cannot be compared with the bound in force today."
                ),
                entry=record.relative,
                run_id=record.run_id,
                operation=record.operation,
                claimed_level=record.claimed_level or "(not recorded)",
                demoted_to=record.demoted_to,
                declared=f"{CATALOG_PATH} lists no operation `{operation}`.",
                observed=(
                    f"the entry records a run of `{operation}` with write_scope "
                    f"{record.write_scope or '[]'}"
                ),
                next_step=(
                    f"Decide which record is right: the operation was removed from {CATALOG_PATH} "
                    f"after {record.run_id} ran, or the entry names an operation that was never "
                    "catalogued. Both are human decisions."
                ),
            )
        ]
    catalogued_scope = string_list(catalogued.get("write_scope"))
    if sorted(catalogued_scope) == sorted(record.write_scope):
        return []
    return [
        Finding(
            kind=KIND_DISAGREEMENT,
            trigger_id="-",
            trigger_key="catalog-disagreement",
            level=record.claimed_level or "(not recorded)",
            clause=(
                "A recorded run's write scope disagrees with the catalogued scope, so one of the "
                "two changed after the run."
            ),
            entry=record.relative,
            run_id=record.run_id,
            operation=record.operation,
            claimed_level=record.claimed_level or "(not recorded)",
            demoted_to=record.demoted_to,
            declared=(
                f"{CATALOG_PATH} records write_scope for `{operation}`: "
                f"{', '.join(catalogued_scope) if catalogued_scope else '[]'}"
            ),
            observed=(
                "the entry recorded write_scope at run time: "
                f"{', '.join(record.write_scope) if record.write_scope else '[]'}"
            ),
            next_step=(
                f"Compare {record.relative} with {CATALOG_PATH} in Git history and decide which "
                "changed. Until a human says which scope is right, the scope trigger cannot be "
                "judged against today's rules for this run."
            ),
        )
    ]


# --- Loading the governance records -----------------------------------------

def load_catalog(root: Path, notes: list[str]) -> dict[str, dict] | None:
    path = root / CATALOG_PATH
    if not path.is_file():
        notes.append(
            f"{CATALOG_PATH} does not exist, so no recorded write scope was compared with the "
            "catalogued one. The guard refuses every operation without that file, so nothing can "
            "have run under it."
        )
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        notes.append(
            f"{CATALOG_PATH} could not be read ({str(exc).splitlines()[0]}), so no recorded write "
            "scope was compared with the catalogued one."
        )
        return None
    operations = data.get("operations") if isinstance(data, dict) else None
    if not isinstance(operations, list):
        notes.append(
            f"{CATALOG_PATH} carries no `operations` list, so no recorded write scope was compared "
            "with the catalogued one."
        )
        return None
    catalog: dict[str, dict] = {}
    for entry in operations:
        if isinstance(entry, dict):
            operation_id = text_of(entry.get("id"))
            if operation_id:
                catalog[operation_id] = entry
    return catalog


def load_renewals(root: Path, notes: list[str]) -> list[dict] | None:
    """Read the renewal record as it stands, with each entry's dates parsed.

    This check reads the record leniently: an entry it can date is a renewal
    that may cover a run, and an entry it cannot is noted and covers nothing.
    Whether the record is well-formed is `scripts/autonomy_guard.py`'s
    question, and a malformed record refuses every run there. A missing or
    unreadable file returns ``None``, and the caller treats that as no renewal
    at all.
    """
    path = root / RENEWALS_PATH
    if not path.is_file():
        notes.append(
            f"{RENEWALS_PATH} does not exist, so no renewal can excuse a run after its review "
            "point. The guard refuses every operation without that file, so nothing can have "
            "run under it."
        )
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        notes.append(
            f"{RENEWALS_PATH} could not be read ({str(exc).splitlines()[0]}), so no renewal can "
            "excuse a run after its review point. An unreadable renewal is not a renewal."
        )
        return None
    renewals = data.get("renewals") if isinstance(data, dict) else None
    if renewals is None:
        renewals = []
    if not isinstance(renewals, list):
        notes.append(
            f"{RENEWALS_PATH} carries no `renewals` list, so no renewal can excuse a run after "
            "its review point."
        )
        return None
    usable: list[dict] = []
    skipped = 0
    for index, item in enumerate(renewals):
        if not isinstance(item, dict):
            skipped += 1
            continue
        operation = text_of(item.get("operation"))
        promotion_signed_on = parse_date(item.get("promotion_signed_on"))
        renewed_on = parse_date(item.get("renewed_on"))
        review_point = parse_date(item.get("review_point"))
        if not operation or None in (promotion_signed_on, renewed_on, review_point):
            skipped += 1
            continue
        usable.append(
            {
                "index": index,
                "operation": operation,
                "promotion_signed_on": promotion_signed_on,
                "renewed_on": renewed_on,
                "review_point": review_point,
            }
        )
    if skipped:
        notes.append(
            f"{RENEWALS_PATH}: {skipped} renewal entry(s) could not be read as a renewal (no "
            "operation, or a date that is not a date) and cover nothing. Run "
            "`python3 scripts/autonomy_guard.py --operation <id> --root .` for the field-level "
            "refusal."
        )
    return usable


def load_promoted_operations(root: Path, notes: list[str]) -> set[str]:
    path = root / PROMOTIONS_PATH
    if not path.is_file():
        notes.append(f"{PROMOTIONS_PATH} does not exist, so no operation is promoted.")
        return set()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        notes.append(
            f"{PROMOTIONS_PATH} could not be read ({str(exc).splitlines()[0]}); findings name no "
            "promotion state."
        )
        return set()
    promotions = data.get("promotions") if isinstance(data, dict) else None
    if not isinstance(promotions, list):
        return set()
    return {
        text_of(entry.get("operation"))
        for entry in promotions
        if isinstance(entry, dict) and text_of(entry.get("operation"))
    }


# --- The report -------------------------------------------------------------

@dataclass
class Report:
    root: str
    triggers: list[ClassifiedTrigger]
    findings: list[Finding]
    files_read: list[str]
    runs_evaluated: list[str]
    samples_skipped: list[str]
    superseded_skipped: list[tuple[str, str]]
    notes: list[str]
    limits: list[str]

    @property
    def exit_code(self) -> int:
        return 1 if self.findings else 0

    def counts(self) -> dict[str, int]:
        counts = {kind: 0 for kind in KIND_ORDER}
        for finding in self.findings:
            counts[finding.kind] = counts.get(finding.kind, 0) + 1
        counts["total"] = len(self.findings)
        return counts

    def to_json(self) -> dict:
        evaluable = [item for item in self.triggers if item.classification.evaluable]
        return {
            "detects_only": DETECTS_ONLY,
            "exit_code": self.exit_code,
            "finding_counts": self.counts(),
            "findings": [finding.to_json() for finding in self.findings],
            "ladder": LADDER_PATH,
            "ledger": {
                "directory": LEDGER_DIR,
                "files_read": self.files_read,
                "runs_evaluated": self.runs_evaluated,
                "samples_skipped": self.samples_skipped,
                "superseded_skipped": [
                    {"entry": entry, "superseded_by": by} for entry, by in self.superseded_skipped
                ],
            },
            "limits": self.limits,
            "notes": self.notes,
            "root": self.root,
            "trigger_counts": {
                "total": len(self.triggers),
                "evaluable_here": len(evaluable),
                "not_evaluable_here": len(self.triggers) - len(evaluable),
            },
            "triggers": [
                {
                    "id": item.trigger.trigger_id,
                    "level": item.trigger.level,
                    "clause": item.trigger.clause,
                    "demotes_to": item.trigger.demotes_to,
                    "key": item.classification.key,
                    "evaluable_here": item.classification.evaluable,
                    "basis": item.classification.basis,
                    "reason": item.classification.reason,
                    "detector": item.classification.detector,
                }
                for item in self.triggers
            ],
        }


def evaluate(root: Path) -> Report:
    """Evaluate every evaluable trigger against the ledger and the working tree."""
    triggers = classify_triggers(parse_ladder_triggers(root))

    notes: list[str] = []
    ineligible, ineligible_problem = read_ineligible_operations(root)
    catalog = load_catalog(root, notes)
    ctx = Context(
        root=root,
        ineligible=ineligible,
        catalog=catalog,
        promoted_operations=load_promoted_operations(root, notes),
        renewals=load_renewals(root, notes),
        notes=notes,
    )

    findings: list[Finding] = []
    if ineligible_problem is not None:
        clause = next(
            (
                item
                for item in triggers
                if item.classification.key == "operation-since-made-ineligible"
            ),
            None,
        )
        findings.append(
            Finding(
                kind=KIND_UNJUDGED,
                trigger_id=clause.trigger.trigger_id if clause else "-",
                trigger_key="operation-since-made-ineligible",
                level="A3",
                clause=clause.trigger.clause if clause else "(clause unavailable)",
                entry=LADDER_PATH,
                run_id="-",
                operation="(every recorded run)",
                claimed_level="-",
                demoted_to="-",
                declared="The ladder names the operations that may never run unattended.",
                observed=ineligible_problem,
                next_step=(
                    "Restore the section in the ladder. Until it is readable this check reports "
                    "the trigger as unjudged rather than clear."
                ),
            )
        )

    files_read: list[str] = []
    samples: list[str] = []
    records: list[Record] = []
    if not (root / LEDGER_DIR).is_dir():
        notes.append(
            f"{LEDGER_DIR} does not exist, so no run has left a record. An absent ledger and an "
            "empty ledger read the same here."
        )
    for path in collect_entry_files(root):
        relative = display(path, root)
        files_read.append(relative)
        if path.name.startswith(SAMPLE_PREFIX):
            samples.append(relative)
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            findings.append(unjudged_entry(relative, f"the file could not be read ({exc})"))
            continue
        front_matter = split_front_matter(raw)
        if front_matter is None:
            findings.append(unjudged_entry(relative, "the file carries no YAML front matter"))
            continue
        try:
            data = yaml.safe_load(front_matter)
        except yaml.YAMLError as exc:
            detail = str(exc).replace("\n", " ")
            findings.append(unjudged_entry(relative, f"the front matter is not valid YAML ({detail})"))
            continue
        if not isinstance(data, dict):
            findings.append(unjudged_entry(relative, "the front matter is not a mapping of fields"))
            continue
        records.append(Record(path=path, relative=relative, data=data))

    superseded: dict[str, str] = {}
    for record in records:
        earlier = text_of(record.data.get("supersedes"))
        if earlier and earlier != text_of(record.data.get("run_id")):
            superseded[earlier] = record.run_id

    authoritative: list[Record] = []
    superseded_skipped: list[tuple[str, str]] = []
    for record in records:
        run_id = text_of(record.data.get("run_id"))
        if run_id and run_id in superseded:
            superseded_skipped.append((record.relative, superseded[run_id]))
            continue
        authoritative.append(record)

    evaluable = [item for item in triggers if item.classification.evaluable]
    for record in authoritative:
        for item in evaluable:
            detector = DETECTORS.get(item.classification.detector or "")
            if detector is None:
                raise UsageError(
                    f"trigger {item.trigger.trigger_id} is classified evaluable but names no "
                    "detector in scripts/demotion_check.py. A trigger this check claims to "
                    "evaluate must have one."
                )
            findings.extend(detector(ctx, record, item))
        findings.extend(detect_catalog_disagreement(ctx, record))

    findings.sort(key=Finding.sort_key)
    return Report(
        root=str(root),
        triggers=triggers,
        findings=findings,
        files_read=files_read,
        runs_evaluated=sorted(record.relative for record in authoritative),
        samples_skipped=samples,
        superseded_skipped=sorted(superseded_skipped),
        notes=sorted(set(ctx.notes)),
        limits=sorted(set(ctx.limits)),
    )


def unjudged_entry(relative: str, problem: str) -> Finding:
    return Finding(
        kind=KIND_UNJUDGED,
        trigger_id="-",
        trigger_key="entry-unreadable",
        level="-",
        clause="A recorded run this check cannot read is a run no trigger can be evaluated against.",
        entry=relative,
        run_id="(unreadable)",
        operation="(unreadable)",
        claimed_level="-",
        demoted_to="-",
        declared=f"Every ledger entry parses as YAML front matter, per {SCHEMA_PATH}.",
        observed=problem,
        next_step=(
            f"Run `python3 scripts/ledger.py validate {relative} --root .` for the field-level "
            "violations, then correct the record forward with a new entry naming this one in "
            "`supersedes`. This check reports the entry as unjudged, never as clear."
        ),
    )


# --- Rendering --------------------------------------------------------------

def field_lines(label: str, value: str, indent: str = "    ", width: int = 96) -> list[str]:
    """Render one labelled field, wrapped so the continuation lines stay under the value."""
    prefix = f"{indent}{label:<10} "
    wrapped = textwrap.wrap(
        " ".join(value.split()),
        width=width,
        initial_indent=prefix,
        subsequent_indent=" " * len(prefix),
        break_long_words=False,
        break_on_hyphens=False,
    )
    return wrapped or [prefix.rstrip()]


def wrap(text: str, indent: str, width: int = 96) -> list[str]:
    """Wrap one field to a fixed width so a long reason stays readable in a terminal."""
    wrapped = textwrap.wrap(
        " ".join(text.split()),
        width=width,
        initial_indent=indent,
        subsequent_indent=indent + "  " if indent else "",
        break_long_words=False,
        break_on_hyphens=False,
    )
    return wrapped or [indent.rstrip()]


def render(report: Report) -> str:
    counts = report.counts()
    evaluable = [item for item in report.triggers if item.classification.evaluable]
    not_evaluable = [item for item in report.triggers if not item.classification.evaluable]

    lines = [f"DEMOTION CHECK: {report.root}", ""]
    lines.append(
        f"Triggers enumerated from {LADDER_PATH}: {len(report.triggers)} "
        f"({len(evaluable)} evaluable here, {len(not_evaluable)} not)"
    )
    lines.append(
        f"Ledger entries read from {LEDGER_DIR}: {len(report.files_read)} "
        f"({len(report.runs_evaluated)} recorded run(s) evaluated, "
        f"{len(report.samples_skipped)} sample(s) skipped, "
        f"{len(report.superseded_skipped)} superseded entry(s) skipped)"
    )
    lines.append("")

    if not report.findings:
        lines.append("NO TRIGGER FIRED.")
        if not report.runs_evaluated:
            lines.append(
                "No run has left a record, so every evaluable trigger had nothing to judge. That "
                "is the expected state while nothing is promoted; it is not evidence that any "
                "operation may run unattended."
            )
    else:
        lines.append(
            f"{counts['total']} finding(s): {counts[KIND_TRIGGER]} demotion trigger(s) fired, "
            f"{counts[KIND_DISAGREEMENT]} record disagreement(s), "
            f"{counts[KIND_UNJUDGED]} record(s) that could not be judged."
        )
    lines.append("")

    for kind, heading in (
        (KIND_TRIGGER, "FIRED"),
        (KIND_DISAGREEMENT, "DISAGREEMENT"),
        (KIND_UNJUDGED, "UNJUDGED"),
    ):
        for finding in [item for item in report.findings if item.kind == kind]:
            marker = f"[{finding.trigger_id}] " if finding.trigger_id != "-" else ""
            lines.extend(wrap(f"{heading} {marker}{finding.clause}", ""))
            lines.extend(field_lines("entry:", f"{finding.entry} (run_id {finding.run_id})"))
            if kind == KIND_TRIGGER:
                lines.extend(
                    field_lines(
                        "operation:",
                        f"{finding.operation} - would be demoted from "
                        f"{finding.claimed_level} to {finding.demoted_to}",
                    )
                )
            else:
                lines.extend(field_lines("operation:", finding.operation))
            lines.extend(field_lines("declared:", finding.declared))
            lines.extend(field_lines("observed:", finding.observed))
            if kind == KIND_TRIGGER:
                lines.extend(field_lines("ladder:", f"{LADDER_PATH}, level {finding.level}"))
            elif kind == KIND_DISAGREEMENT:
                lines.extend(
                    field_lines(
                        "note:",
                        "Not a ladder trigger. A record disagreement demotes nothing by itself; "
                        "it means two records changed relative to each other, and until a "
                        "human says which is right the trigger that reads them cannot be "
                        "judged for this run.",
                    )
                )
            else:
                lines.extend(
                    field_lines(
                        "note:",
                        "Not a fired trigger. This record could not be judged at all, which is "
                        "reported rather than counted as clear.",
                    )
                )
            lines.extend(field_lines("next:", finding.next_step))
            lines.append("")

    lines.append(f"Evaluated here ({len(evaluable)}):")
    for item in evaluable:
        lines.extend(wrap(f"[{item.trigger.trigger_id}] {item.trigger.clause}", "  "))
        lines.extend(wrap(item.classification.reason, "      "))
    lines.append("")
    lines.append(f"Not evaluable here ({len(not_evaluable)}), each with the reason:")
    for item in not_evaluable:
        lines.extend(
            wrap(f"[{item.trigger.trigger_id}] {item.trigger.clause}  ({item.classification.basis})", "  ")
        )
        lines.extend(wrap(item.classification.reason, "      "))
    lines.append("")

    if report.superseded_skipped:
        lines.append("Superseded entries, not judged (the superseding entry is authoritative):")
        for entry, by in report.superseded_skipped:
            lines.append(f"  {entry} superseded by run_id {by}")
        lines.append("")
    if report.samples_skipped:
        lines.append("Sample entries, not judged (a hypothetical record is not a run):")
        for entry in report.samples_skipped:
            lines.append(f"  {entry}")
        lines.append("")
    if report.limits:
        lines.append("Limits on what was judged:")
        for limit in report.limits:
            lines.extend(wrap(limit, "  "))
        lines.append("")
    if report.notes:
        lines.append("Notes:")
        for note in report.notes:
            lines.extend(wrap(note, "  "))
        lines.append("")

    lines.extend(wrap(DETECTS_ONLY, ""))
    return "\n".join(lines).rstrip("\n") + "\n"


# --- CLI --------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    return _add_arguments(
        argparse.ArgumentParser(
            prog="demotion_check.py",
            description=(
                "Evaluate the autonomy ladder's demotion triggers against the action ledger and "
                "the working tree. Exit 0 when nothing fired, 1 when a trigger fired, a record "
                "disagreement was found, or a recorded run could not be judged, and 2 on a usage "
                "error including a ladder this check cannot read. It reports; it never demotes."
            ),
        )
    )


def _add_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "--root",
        default=str(DEFAULT_ROOT),
        metavar="PATH",
        help="repository root to read (default: the repository containing this script)",
    )
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(
            f"demotion_check.py: --root {args.root!r} is not a directory. Pass the repository "
            "root, for example --root .",
            file=sys.stderr,
        )
        return 2
    try:
        report = evaluate(root.resolve())
    except UsageError as exc:
        print(f"demotion_check.py: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report.to_json(), indent=2, sort_keys=True))
    else:
        sys.stdout.write(render(report))
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
