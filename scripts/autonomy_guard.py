#!/usr/bin/env python3
"""Refuse an unattended run unless every recorded precondition holds.

``docs/framework/AUTONOMY_LADDER.md`` defines A3, act-unattended-within-bounds,
and says that raising an operation to it is a human governance decision. This
guard is the check that reads that decision before anything acts. It answers one
question about one operation:

    May this operation run without a person right now?

The default answer is no. The guard permits a run only when every precondition
below holds, and it names the ones that failed when it refuses. A record that is
missing, unparsable, self-inconsistent, or carrying an unexpected schema version
is a refusal, never a pass.

Two independent records must both change before the answer is yes:

1. ``ops/autonomy/promotions.yaml`` carries a promotion for the operation at A3,
   signed by a role that holds reserved decisions, dated, backed by evidence
   paths that exist, naming its demotion triggers, and declaring the same write
   scope as the catalog entry.
2. The same file records ``kill_switch: released``.

Editing one of those two records is not enough, and neither is editing the
catalog: ``ops/autonomy/operations.yaml`` may not declare A3 for anything, so it
cannot promote an operation on its own.

The guard reads files only. It never writes, never runs an operation's command,
never changes a level, never records a signature, and never asserts that an
owner gate or an operating hold is cleared. It makes no network call.

Usage:

    python3 scripts/autonomy_guard.py --operation cadence-snapshot --root .

Exit codes: 0 = permitted, 1 = refused (each failed precondition is printed),
2 = usage error.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from fnmatch import fnmatchcase
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit(
        "PyYAML is required: install it (pip install PyYAML) before running "
        "scripts/autonomy_guard.py"
    ) from exc


DEFAULT_ROOT = Path(__file__).resolve().parents[1]

CATALOG_PATH = "ops/autonomy/operations.yaml"
PROMOTIONS_PATH = "ops/autonomy/promotions.yaml"
LADDER_PATH = "docs/framework/AUTONOMY_LADDER.md"

SUPPORTED_SCHEMA_VERSIONS = (1,)

# A catalog entry records the level an operation is at today. A0-A2 are the
# attended levels in the ladder. A3 is deliberately absent: only a signed
# promotion grants it, so the catalog alone can never permit a run.
CATALOG_LEVELS = ("A0", "A1", "A2")
UNATTENDED_LEVEL = "A3"

KILL_SWITCH_VALUES = ("engaged", "released")
KILL_SWITCH_RELEASED = "released"

# Controlled operating roles from community/GOVERNANCE.md and ops/BETA_OPS.md,
# identical to ROLE_VOCABULARY in scripts/validate_agents.py. A signature that
# names a person rather than a role is not a governance record.
ROLE_VOCABULARY = (
    "founder",
    "beta-owner",
    "continuity-owner",
    "maintainer",
    "area-maintainer",
    "artifact-maintainer",
    "release-owner",
    "private-intake-owner",
    "authorized-inviter",
    "agent-sponsor",
    "session-facilitator",
)

# community/GOVERNANCE.md reserves hard-to-reverse decisions to a founder
# decision at launch; ops/BETA_OPS.md records the beta owner as "founder or
# designated continuity owner" holding reserved decisions. An A3 promotion is a
# reserved decision, so no other role may sign one.
RESERVED_DECISION_ROLES = ("founder", "beta-owner", "continuity-owner")

# The operation ids docs/framework/AUTONOMY_LADDER.md marks permanently
# ineligible for A3. The guard also reads that section at run time; a
# disagreement between this list and the document is a refusal, and an id the
# document adds is honored without changing this file.
# Amended by community/AMENDMENTS.md (001): `merge` left this list in favour
# of bounded auto-merge, and `publication-and-announcement` split so that only
# `publication-approval` remains. Both replacements are eligible, not promoted.
INELIGIBLE_OPERATIONS = (
    "moderation-and-removal",
    "maturity-promotion",
    "publication-approval",
    "owner-identity-and-keys",
    "license-and-governance-change",
    "owner-reserved-decision",
)
LADDER_SECTION_HEADING = "## Permanently ineligible for A3"

CATALOG_TOP_LEVEL_FIELDS = ("schema_version", "operations", "sources")
REQUIRED_OPERATION_FIELDS = (
    "id",
    "summary",
    "command",
    "write_scope",
    "reversal",
    "blast_radius",
    "level",
)
OPTIONAL_OPERATION_FIELDS = ("level_basis", "note")

PROMOTIONS_TOP_LEVEL_FIELDS = ("schema_version", "kill_switch", "promotions")
REQUIRED_PROMOTION_FIELDS = (
    "operation",
    "level",
    "write_scope",
    "evidence",
    "demotion_triggers",
    "signed_by",
    "signed_on",
)

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LADDER_ID_RE = re.compile(r"^`([a-z0-9]+(?:-[a-z0-9]+)*)`$")
GLOB_RE = re.compile(r"^[A-Za-z0-9_*?/.\[\]-]+$")
SHELL_METACHARACTER_RE = re.compile(r"[;&|<>$`\n\r\\\"']")

# A write scope may never reach the records that decide whether an operation may
# run, the code that enforces the decision, or the workflow that schedules it.
# An operation able to widen its own bound has no bound.
GOVERNED_PATHS = (
    "ops/autonomy/operations.yaml",
    "ops/autonomy/promotions.yaml",
    "ops/autonomy/README.md",
    "docs/framework/AUTONOMY_LADDER.md",
    "release/OWNER_REVIEW.md",
    "buzz/agents/registry.yaml",
    "tasks/manifest.json",
    "AGENTS.md",
    "DECISIONS.md",
    "NON_GOALS.md",
    "OWNER_GATES.md",
    "QUALITY_BAR.md",
    "Makefile",
)
GOVERNED_PREFIXES = (
    ".git/",
    ".github/",
    ".swarm/",
    "buzz/agents/",
    "docs/framework/",
    "docs/schemas/",
    "handoffs/",
    "ops/autonomy/",
    "ops/ledger/",
    "scripts/",
    "tasks/",
    "tests/",
)
GOVERNED_PROBE_SUFFIXES = ("probe.md", "probe.py", "probe.yaml", "probe.json", "sub/probe.md")


@dataclass(frozen=True)
class Refusal:
    """One failed precondition and the message a human acts on."""

    precondition: str
    message: str


@dataclass
class Decision:
    """The result of one guard evaluation. ``permitted`` is false by default."""

    operation: str
    permitted: bool = False
    refusals: list[Refusal] = field(default_factory=list)
    checked: list[str] = field(default_factory=list)
    command: list[str] | None = None
    write_scope: list[str] | None = None
    signed_by: str | None = None
    signed_on: str | None = None

    def refuse(self, precondition: str, message: str) -> None:
        self.permitted = False
        self.refusals.append(Refusal(precondition, message))

    def passed(self, precondition: str) -> None:
        if precondition not in self.checked:
            self.checked.append(precondition)


def is_nonempty_str(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def is_str_list(value) -> bool:
    return isinstance(value, list) and all(is_nonempty_str(item) for item in value)


def load_yaml_mapping(path: Path, relative: str, precondition: str, decision: Decision):
    """Return the mapping at ``path``, or ``None`` after recording a refusal."""
    if not path.exists():
        decision.refuse(
            precondition,
            f"{relative} does not exist. The guard cannot read the record that would "
            "permit an unattended run, so it refuses. Restore the file from version "
            "control before running anything unattended.",
        )
        return None
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        decision.refuse(
            precondition,
            f"{relative} cannot be parsed as YAML: {exc}. An unreadable record is not "
            "an approval; fix the file before running anything unattended.",
        )
        return None
    if not isinstance(value, dict):
        decision.refuse(
            precondition,
            f"{relative} is not a YAML mapping. It must be a mapping with "
            f"{', '.join(repr(f) for f in (CATALOG_TOP_LEVEL_FIELDS if relative == CATALOG_PATH else PROMOTIONS_TOP_LEVEL_FIELDS))}.",
        )
        return None
    return value


def check_schema_version(record: dict, relative: str, precondition: str, decision: Decision) -> None:
    version = record.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        decision.refuse(
            precondition,
            f"{relative}: 'schema_version' is {version!r}; this guard reads "
            f"{', '.join(str(v) for v in SUPPORTED_SCHEMA_VERSIONS)}. A record written to a "
            "schema the guard does not know is refused rather than guessed at.",
        )


def check_top_level_fields(
    record: dict, relative: str, allowed: tuple[str, ...], precondition: str, decision: Decision
) -> None:
    unknown = sorted(set(record) - set(allowed))
    if unknown:
        decision.refuse(
            precondition,
            f"{relative} has unrecognized top-level field(s) {', '.join(unknown)}. Allowed "
            f"fields are {', '.join(allowed)}. A misspelled field silently drops a bound, so "
            "it is refused.",
        )


def glob_reaches_governed_path(pattern: str) -> str | None:
    """Return the governed path a write-scope glob would cover, or ``None``."""
    for governed in GOVERNED_PATHS:
        if fnmatchcase(governed, pattern):
            return governed
    for prefix in GOVERNED_PREFIXES:
        for suffix in GOVERNED_PROBE_SUFFIXES:
            probe = f"{prefix}{suffix}"
            if fnmatchcase(probe, pattern):
                return f"{prefix}*"
    return None


def check_write_scope(value, where: str, precondition: str, decision: Decision) -> bool:
    """Validate one write-scope list. Returns True when it is usable."""
    if not isinstance(value, list):
        decision.refuse(
            precondition,
            f"{where}: 'write_scope' must be a list of repository-relative globs. Use an "
            "empty list for an operation that writes nothing.",
        )
        return False
    ok = True
    for index, item in enumerate(value):
        label = f"{where}: 'write_scope[{index}]'"
        if not is_nonempty_str(item):
            decision.refuse(precondition, f"{label} must be a non-empty string.")
            ok = False
            continue
        pattern = item.strip()
        if pattern != item:
            decision.refuse(precondition, f"{label} is {item!r}; remove the surrounding whitespace.")
            ok = False
            continue
        if pattern.startswith("/") or pattern.startswith("~"):
            decision.refuse(
                precondition,
                f"{label} is {pattern!r}; a write scope is repository-relative and may not be "
                "an absolute or home-relative path.",
            )
            ok = False
            continue
        if ".." in pattern.split("/"):
            decision.refuse(
                precondition,
                f"{label} is {pattern!r}; '..' would let a run write outside the repository.",
            )
            ok = False
            continue
        if not GLOB_RE.match(pattern):
            decision.refuse(
                precondition,
                f"{label} is {pattern!r}; a glob may contain only letters, digits, '_', '-', "
                "'.', '/', '*', '?', and character classes.",
            )
            ok = False
            continue
        if "/" not in pattern:
            decision.refuse(
                precondition,
                f"{label} is {pattern!r}; a write scope names a directory and a file pattern "
                "inside it, such as 'ops/status/*.md', so a run cannot write at the "
                "repository root.",
            )
            ok = False
            continue
        governed = glob_reaches_governed_path(pattern)
        if governed is not None:
            decision.refuse(
                precondition,
                f"{label} is {pattern!r}, which covers {governed}. A write scope may never "
                "reach the promotion record, the catalog, the ladder, the guard, the "
                "scheduled workflow, or another governance record: an operation that can "
                "widen its own bound has no bound. Narrow the glob.",
            )
            ok = False
    return ok


def check_command(value, where: str, root: Path, decision: Decision) -> None:
    precondition = "catalog-command"
    if not is_str_list(value) or len(value) < 2:
        decision.refuse(
            precondition,
            f"{where}: 'command' must be a list of at least two non-empty strings, the "
            "argv an unattended run would execute, such as "
            "[\"python3\", \"scripts/cadence.py\", \"--root\", \".\"].",
        )
        return
    for index, item in enumerate(value):
        if SHELL_METACHARACTER_RE.search(item):
            decision.refuse(
                precondition,
                f"{where}: 'command[{index}]' is {item!r}, which contains a shell "
                "metacharacter. A command is an argv list executed without a shell; a "
                "metacharacter here means the entry was written for a shell that will not "
                "run it.",
            )
            return
    if value[0] != "python3":
        decision.refuse(
            precondition,
            f"{where}: 'command[0]' is {value[0]!r}; every catalogued operation is a Python "
            "3 script in this repository, so the first element must be 'python3'.",
        )
        return
    script = value[1]
    if script.startswith("/") or ".." in script.split("/") or not script.endswith(".py"):
        decision.refuse(
            precondition,
            f"{where}: 'command[1]' is {script!r}; it must be a repository-relative path to "
            "a .py file, such as 'scripts/cadence.py'.",
        )
        return
    if not (root / script).is_file():
        decision.refuse(
            precondition,
            f"{where}: 'command[1]' names {script}, which does not exist under the root "
            "being checked. An operation whose implementation is missing or moved is "
            "refused rather than run.",
        )


def check_catalog_entry(entry, index: int, root: Path, decision: Decision) -> str | None:
    """Validate one catalog entry; return its id when it is usable."""
    where = f"{CATALOG_PATH}: operations[{index}]"
    if not isinstance(entry, dict):
        decision.refuse("catalog-entry", f"{where} must be a mapping.")
        return None

    operation_id = entry.get("id")
    if is_nonempty_str(operation_id) and ID_RE.match(operation_id.strip()):
        operation_id = operation_id.strip()
        where = f"{CATALOG_PATH}: operation '{operation_id}'"
    else:
        decision.refuse(
            "catalog-entry",
            f"{where}: 'id' must be a lowercase slug such as 'cadence-snapshot' so a "
            "promotion and a ledger entry can reference it.",
        )
        operation_id = None

    for missing in [f for f in REQUIRED_OPERATION_FIELDS if f not in entry]:
        decision.refuse("catalog-entry", f"{where} is missing required field '{missing}'.")
    unknown = sorted(set(entry) - set(REQUIRED_OPERATION_FIELDS) - set(OPTIONAL_OPERATION_FIELDS))
    if unknown:
        decision.refuse(
            "catalog-entry",
            f"{where} has unrecognized field(s) {', '.join(unknown)}. Allowed fields are "
            f"{', '.join(REQUIRED_OPERATION_FIELDS + OPTIONAL_OPERATION_FIELDS)}.",
        )

    for prose_field in ("summary", "reversal", "blast_radius"):
        if prose_field in entry and not is_nonempty_str(entry.get(prose_field)):
            decision.refuse(
                "catalog-entry",
                f"{where}: '{prose_field}' must be a non-empty line. An operation with no "
                "recorded reversal or blast radius cannot be reviewed for promotion.",
            )

    if "command" in entry:
        check_command(entry.get("command"), where, root, decision)
    if "write_scope" in entry:
        check_write_scope(entry.get("write_scope"), where, "catalog-write-scope", decision)

    level = entry.get("level")
    if level == UNATTENDED_LEVEL:
        decision.refuse(
            "catalog-level",
            f"{where}: 'level' is {UNATTENDED_LEVEL}. The catalog records the level an "
            "operation is at today and cannot grant an unattended one; A3 comes only from a "
            f"signed promotion in {PROMOTIONS_PATH}. Set the catalog level back to the "
            "current attended level.",
        )
    elif level not in CATALOG_LEVELS:
        decision.refuse(
            "catalog-entry",
            f"{where}: 'level' is {level!r}; it must be one of {', '.join(CATALOG_LEVELS)} "
            "as defined in docs/framework/AUTONOMY_LADDER.md.",
        )

    return operation_id


def load_catalog(root: Path, decision: Decision) -> dict[str, dict] | None:
    """Return ``{operation id: entry}``, or ``None`` when the catalog is unusable."""
    record = load_yaml_mapping(root / CATALOG_PATH, CATALOG_PATH, "catalog-readable", decision)
    if record is None:
        return None
    check_schema_version(record, CATALOG_PATH, "catalog-schema", decision)
    check_top_level_fields(record, CATALOG_PATH, CATALOG_TOP_LEVEL_FIELDS, "catalog-schema", decision)

    for index, source in enumerate(record.get("sources") or []):
        if not is_nonempty_str(source):
            decision.refuse("catalog-schema", f"{CATALOG_PATH}: 'sources[{index}]' must be a path.")
        elif not (root / source.strip()).exists():
            decision.refuse(
                "catalog-schema",
                f"{CATALOG_PATH}: 'sources[{index}]' names {source.strip()}, which does not exist.",
            )

    operations = record.get("operations")
    if not isinstance(operations, list) or not operations:
        decision.refuse(
            "catalog-schema",
            f"{CATALOG_PATH}: 'operations' must be a non-empty list, one entry per operation "
            "that could one day run unattended.",
        )
        return None

    catalog: dict[str, dict] = {}
    for index, entry in enumerate(operations):
        operation_id = check_catalog_entry(entry, index, root, decision)
        if operation_id is None:
            continue
        if operation_id in catalog:
            decision.refuse(
                "catalog-entry",
                f"{CATALOG_PATH}: duplicate operation id {operation_id!r}. Two entries for one "
                "id make the bound ambiguous, so the guard refuses.",
            )
            continue
        catalog[operation_id] = entry if isinstance(entry, dict) else {}
    return catalog


def read_ineligible_operations(root: Path, decision: Decision) -> set[str] | None:
    """Return the ids the ladder marks permanently ineligible for A3."""
    path = root / LADDER_PATH
    if not path.is_file():
        decision.refuse(
            "ladder-readable",
            f"{LADDER_PATH} does not exist. The guard reads the permanently ineligible list "
            "from it before permitting anything; without that list it refuses.",
        )
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == LADDER_SECTION_HEADING:
            start = index + 1
            break
    if start is None:
        decision.refuse(
            "ladder-readable",
            f"{LADDER_PATH} has no '{LADDER_SECTION_HEADING}' section. The guard reads the "
            "operations that may never run unattended from that section; a missing anchor is "
            "a refusal, not a pass. Restore the section or update LADDER_SECTION_HEADING in "
            "scripts/autonomy_guard.py.",
        )
        return None

    found: set[str] = set()
    for line in lines[start:]:
        if line.startswith("## "):
            break
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells:
            continue
        match = LADDER_ID_RE.match(cells[0])
        if match:
            found.add(match.group(1))
    if not found:
        decision.refuse(
            "ladder-readable",
            f"{LADDER_PATH}: the '{LADDER_SECTION_HEADING}' section lists no operation ids in "
            "its first table column. The guard cannot confirm what may never run unattended, "
            "so it refuses.",
        )
        return None

    missing = sorted(set(INELIGIBLE_OPERATIONS) - found)
    if missing:
        decision.refuse(
            "ladder-agreement",
            f"{LADDER_PATH} no longer lists {', '.join(missing)} as permanently ineligible "
            "for A3, but scripts/autonomy_guard.py still does. Removing an operation from "
            "that list is a governance amendment to DECISIONS.md and NON_GOALS.md, not a "
            "tooling change; until the two agree the guard refuses.",
        )
        return None
    return found | set(INELIGIBLE_OPERATIONS)


def normalize_signed_on(value) -> tuple[date | None, str]:
    """Return ``(date, rendered)`` for a YAML date or ISO string."""
    if isinstance(value, date):
        return value, value.isoformat()
    if isinstance(value, str) and ISO_DATE_RE.match(value.strip()):
        try:
            return date.fromisoformat(value.strip()), value.strip()
        except ValueError:
            return None, value.strip()
    return None, repr(value)


def check_promotion_shape(entry, index: int, decision: Decision) -> str | None:
    """Validate one promotion entry's structure; return the operation id it names."""
    where = f"{PROMOTIONS_PATH}: promotions[{index}]"
    if not isinstance(entry, dict):
        decision.refuse("promotions-record", f"{where} must be a mapping.")
        return None
    operation = entry.get("operation")
    if is_nonempty_str(operation) and ID_RE.match(operation.strip()):
        operation = operation.strip()
    else:
        decision.refuse(
            "promotions-record",
            f"{where}: 'operation' must be the lowercase id of a catalogued operation.",
        )
        operation = None
    for missing in [f for f in REQUIRED_PROMOTION_FIELDS if f not in entry]:
        decision.refuse(
            "promotions-record",
            f"{where} is missing required field '{missing}'. A promotion records the whole "
            f"bound: {', '.join(REQUIRED_PROMOTION_FIELDS)}.",
        )
    unknown = sorted(set(entry) - set(REQUIRED_PROMOTION_FIELDS))
    if unknown:
        decision.refuse(
            "promotions-record",
            f"{where} has unrecognized field(s) {', '.join(unknown)}. Allowed fields are "
            f"{', '.join(REQUIRED_PROMOTION_FIELDS)}; a misspelled field silently drops part "
            "of the bound.",
        )
    return operation


def check_promotion(
    promotion: dict,
    operation: str,
    catalog_entry: dict,
    root: Path,
    as_of: date,
    decision: Decision,
) -> None:
    """Check the promotion that names ``operation`` against the catalog and the ladder."""
    where = f"{PROMOTIONS_PATH}: promotion for '{operation}'"

    level = promotion.get("level")
    if level != UNATTENDED_LEVEL:
        decision.refuse(
            "promotion-level",
            f"{where}: 'level' is {level!r}. This guard authorizes unattended action only, so "
            f"a promotion it reads must record 'level: {UNATTENDED_LEVEL}'. An attended level "
            "needs no unattended run.",
        )
    else:
        decision.passed("promotion-level")

    promoted_scope = promotion.get("write_scope")
    scope_usable = check_write_scope(promoted_scope, where, "promotion-write-scope", decision)
    catalogued_scope = catalog_entry.get("write_scope")
    if scope_usable and isinstance(catalogued_scope, list):
        if sorted(promoted_scope) != sorted(str(item) for item in catalogued_scope):
            decision.refuse(
                "promotion-write-scope",
                f"{where}: 'write_scope' is {promoted_scope!r}, but {CATALOG_PATH} records "
                f"{catalogued_scope!r} for '{operation}'. The two records must declare the "
                "same bound; a promotion cannot widen, narrow, or redirect the scope the "
                "catalog describes. Change both in one reviewed decision or neither.",
            )
        else:
            decision.passed("promotion-write-scope")
            decision.write_scope = list(promoted_scope)

    evidence = promotion.get("evidence")
    if not is_str_list(evidence) or not evidence:
        decision.refuse(
            "promotion-evidence",
            f"{where}: 'evidence' must be a non-empty list of repository paths a reviewer can "
            "open. A promotion with no evidence is an assertion, not a record.",
        )
    else:
        missing = [item for item in evidence if not (root / item.strip()).exists()]
        if missing:
            decision.refuse(
                "promotion-evidence",
                f"{where}: 'evidence' names {', '.join(missing)}, which does not exist under "
                "the root being checked. Evidence that cannot be opened cannot be reviewed.",
            )
        else:
            decision.passed("promotion-evidence")

    triggers = promotion.get("demotion_triggers")
    if not is_str_list(triggers) or not triggers:
        decision.refuse(
            "promotion-demotion-triggers",
            f"{where}: 'demotion_triggers' must be a non-empty list of the observable "
            "conditions that end this promotion. docs/framework/AUTONOMY_LADDER.md demotes "
            "automatically on its triggers; a promotion that names none is refused.",
        )
    else:
        decision.passed("promotion-demotion-triggers")

    signed_by = promotion.get("signed_by")
    signed_on = promotion.get("signed_on")
    if not is_nonempty_str(signed_by) or signed_on is None:
        decision.refuse(
            "signature-present",
            f"{where} carries no complete signature: 'signed_by' must name the role that made "
            "the decision and 'signed_on' the ISO date it was made. An unsigned promotion is "
            "not a governance record.",
        )
    else:
        decision.passed("signature-present")
        role = signed_by.strip()
        if role not in ROLE_VOCABULARY:
            decision.refuse(
                "signature-role",
                f"{where}: 'signed_by' is {role!r}, which is not a controlled operating role. "
                f"Use one of: {', '.join(ROLE_VOCABULARY)}. Personal names, handles, and "
                "contact routes stay in the private maintainer record.",
            )
        elif role not in RESERVED_DECISION_ROLES:
            decision.refuse(
                "signature-authority",
                f"{where}: 'signed_by' is {role!r}. Promoting an operation to "
                f"{UNATTENDED_LEVEL} is a reserved decision under community/GOVERNANCE.md, so "
                f"only {', '.join(RESERVED_DECISION_ROLES)} may sign one.",
            )
        else:
            decision.passed("signature-role")
            decision.passed("signature-authority")
            decision.signed_by = role

        signed_date, rendered = normalize_signed_on(signed_on)
        if signed_date is None:
            decision.refuse(
                "signature-date",
                f"{where}: 'signed_on' is {rendered}; it must be an ISO date such as "
                "2026-09-02.",
            )
        elif signed_date > as_of:
            decision.refuse(
                "signature-date",
                f"{where}: 'signed_on' is {rendered}, which is after the date being checked "
                f"({as_of.isoformat()}). A promotion cannot be signed in the future.",
            )
        else:
            decision.passed("signature-date")
            decision.signed_on = rendered


def evaluate(root: Path, operation: str, as_of: date | None = None) -> Decision:
    """Decide whether ``operation`` may run unattended under ``root``.

    The returned ``Decision`` is refused unless every precondition held.
    """
    as_of = as_of or date.today()
    decision = Decision(operation=operation)

    catalog = load_catalog(root, decision)
    if catalog is None:
        return decision
    decision.passed("catalog-readable")

    entry = catalog.get(operation)
    if entry is None:
        known = ", ".join(sorted(catalog)) or "none"
        decision.refuse(
            "operation-catalogued",
            f"'{operation}' is not in {CATALOG_PATH}. The guard permits only operations a "
            f"human has catalogued with a command, a write scope, a reversal, and a blast "
            f"radius. Catalogued operations: {known}.",
        )
    else:
        decision.passed("operation-catalogued")
        decision.command = list(entry.get("command")) if is_str_list(entry.get("command")) else None

    ineligible = read_ineligible_operations(root, decision)
    if ineligible is not None:
        decision.passed("ladder-readable")
        if operation in ineligible:
            decision.refuse(
                "operation-eligible",
                f"'{operation}' is on the permanently ineligible list in {LADDER_PATH}. No "
                "amount of evidence, run history, or evaluation result raises it, because the "
                "decision is reserved to a human by a decision this repository has already "
                "locked. The guard refuses regardless of what any promotion says.",
            )
        else:
            decision.passed("operation-eligible")

    promotions_record = load_yaml_mapping(
        root / PROMOTIONS_PATH, PROMOTIONS_PATH, "promotions-readable", decision
    )
    if promotions_record is None:
        return decision
    decision.passed("promotions-readable")
    check_schema_version(promotions_record, PROMOTIONS_PATH, "promotions-schema", decision)
    check_top_level_fields(
        promotions_record, PROMOTIONS_PATH, PROMOTIONS_TOP_LEVEL_FIELDS, "promotions-schema", decision
    )

    kill_switch = promotions_record.get("kill_switch")
    if kill_switch not in KILL_SWITCH_VALUES:
        decision.refuse(
            "promotions-schema",
            f"{PROMOTIONS_PATH}: 'kill_switch' is {kill_switch!r}; it must be one of "
            f"{', '.join(KILL_SWITCH_VALUES)}. A value the guard cannot read is treated as "
            "engaged.",
        )
    elif kill_switch != KILL_SWITCH_RELEASED:
        decision.refuse(
            "kill-switch-released",
            f"{PROMOTIONS_PATH} records 'kill_switch: {kill_switch}'. Every unattended run is "
            "refused while the switch is engaged, whatever else the record says. Releasing it "
            "is a human decision recorded in the same file, and it is the second of the two "
            "records that must change.",
        )
    else:
        decision.passed("kill-switch-released")

    promotions = promotions_record.get("promotions")
    if promotions is None or (isinstance(promotions, list) and not promotions):
        promotions = []
    if not isinstance(promotions, list):
        decision.refuse(
            "promotions-schema",
            f"{PROMOTIONS_PATH}: 'promotions' must be a list. Use '[]' to record that nothing "
            "is promoted.",
        )
        return decision

    named: list[tuple[int, dict]] = []
    for index, item in enumerate(promotions):
        promoted_operation = check_promotion_shape(item, index, decision)
        if promoted_operation is None:
            continue
        if ineligible is not None and promoted_operation in ineligible:
            decision.refuse(
                "operation-eligible",
                f"{PROMOTIONS_PATH}: promotions[{index}] promotes '{promoted_operation}', "
                f"which {LADDER_PATH} marks permanently ineligible for A3. The record is "
                "invalid until that entry is removed, so the guard refuses every operation it "
                "is asked about.",
            )
            continue
        if promoted_operation not in catalog:
            decision.refuse(
                "promotions-record",
                f"{PROMOTIONS_PATH}: promotions[{index}] promotes '{promoted_operation}', "
                f"which has no entry in {CATALOG_PATH}. A promotion with no catalogued command, "
                "write scope, and reversal has no bound to enforce.",
            )
            continue
        if promoted_operation == operation and isinstance(item, dict):
            named.append((index, item))

    if entry is not None:
        if not named:
            decision.refuse(
                "promotion-signed",
                f"{PROMOTIONS_PATH} carries no signed promotion for '{operation}' at "
                f"{UNATTENDED_LEVEL}. Nothing in this repository is promoted, so every "
                "operation is refused. A promotion is a human governance decision recorded "
                "through the reserved-decision path in community/GOVERNANCE.md; it is not "
                "something this guard, a runner, or an agent can record.",
            )
        elif len(named) > 1:
            positions = ", ".join(str(index) for index, _ in named)
            decision.refuse(
                "promotion-unique",
                f"{PROMOTIONS_PATH} carries {len(named)} promotions for '{operation}' "
                f"(entries {positions}). Two bounds for one operation are ambiguous, so the "
                "guard refuses until exactly one remains.",
            )
        else:
            decision.passed("promotion-signed")
            check_promotion(named[0][1], operation, entry, root, as_of, decision)

    decision.permitted = not decision.refusals
    return decision


def render(decision: Decision) -> str:
    lines: list[str] = []
    if decision.permitted:
        lines.append(
            f"PERMITTED: '{decision.operation}' may run unattended inside the bound recorded "
            f"in {PROMOTIONS_PATH}."
        )
        if decision.command:
            lines.append(f"  command: {' '.join(decision.command)}")
        scope = decision.write_scope if decision.write_scope is not None else []
        lines.append(f"  write_scope: {', '.join(scope) if scope else '(writes nothing)'}")
        lines.append(f"  signed_by: {decision.signed_by} on {decision.signed_on}")
        lines.append(f"  preconditions held: {', '.join(decision.checked)}")
        lines.append(
            "This permits one bounded run of this operation. It is not an approval of any "
            "other operation, and it does not clear an owner gate or an operating hold."
        )
        return "\n".join(lines) + "\n"

    lines.append(f"REFUSED: '{decision.operation}' may not run unattended.")
    for refusal in decision.refusals:
        lines.append(f"  [{refusal.precondition}] {refusal.message}")
    lines.append(
        f"{len(decision.refusals)} precondition(s) failed. Refusal is the default: the guard "
        "permits a run only when every precondition holds."
    )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autonomy_guard.py",
        description=(
            "Decide whether one operation may run unattended. Exit 0 permitted, 1 refused, "
            "2 usage error. Refusal is the default."
        ),
    )
    parser.add_argument(
        "--operation",
        required=True,
        metavar="ID",
        help=f"operation id catalogued in {CATALOG_PATH}",
    )
    parser.add_argument(
        "--root",
        default=str(DEFAULT_ROOT),
        metavar="PATH",
        help="repository root to read (default: the repository containing this script)",
    )
    parser.add_argument(
        "--as-of",
        default=None,
        metavar="YYYY-MM-DD",
        help="date the signature is checked against (default: today)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(
            f"autonomy_guard.py: --root {args.root!r} is not a directory. Pass the repository "
            "root, for example --root .",
            file=sys.stderr,
        )
        return 2
    as_of = None
    if args.as_of is not None:
        if not ISO_DATE_RE.match(args.as_of):
            print(
                f"autonomy_guard.py: --as-of must be an ISO date such as 2026-09-02, got "
                f"{args.as_of!r}.",
                file=sys.stderr,
            )
            return 2
        try:
            as_of = date.fromisoformat(args.as_of)
        except ValueError as exc:
            print(f"autonomy_guard.py: --as-of is not a real date: {args.as_of} ({exc}).", file=sys.stderr)
            return 2
    decision = evaluate(root.resolve(), args.operation.strip(), as_of)
    sys.stdout.write(render(decision))
    return 0 if decision.permitted else 1


if __name__ == "__main__":
    sys.exit(main())
