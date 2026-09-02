#!/usr/bin/env python3
"""Deterministic offline checker for Practice issue-triage records.

A triage record is a markdown file with YAML front matter under ``ops/triage/``.
It records where one reported issue sits in the state machine defined by
``practices/004-issue-triage.md`` and mapped onto labels by
``.github/TRIAGE_POLICY.md``. The record carries evidence pointers and role
labels only: no personal data, no member identities, no message contents.

``validate`` checks one or more records:

- the state and category are in the controlled vocabulary;
- the evidence the state requires is present, and path pointers resolve to
  files that exist under ``--root``;
- a state that needs an owner names an owner *role*, never a person;
- no field or line carries personal data, a handle, or a secret;
- every transition in ``history`` is legal, chains from ``new``, and ends at
  the record's current state; and
- the agent boundary holds: a record whose last actor is ``agent`` may not sit
  in a human-owned state, and a safety, privacy, access, conduct, or legal
  record is routed to a human and is never actored or resolved by an agent.

``next`` prints the legal next states for a record and the evidence each one
requires, so an agent can prepare a recommendation it cannot enact.

This tool records and checks triage. It never applies a label, closes an issue,
removes content, or restricts a person.

Exit codes: 0 = every record valid, 1 = at least one violation,
2 = usage error.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    print(
        "scripts/triage.py needs PyYAML to read record front matter. "
        "Fix: python3 -m pip install PyYAML",
        file=sys.stderr,
    )
    raise SystemExit(2)

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

# --- Vocabulary -------------------------------------------------------------
# States come from practices/004-issue-triage.md ("needs-info",
# "ready-for-agent", "ready-for-human", "wontfix") plus the entry state "New"
# used by the transition table in .github/TRIAGE_POLICY.md.
STATE_ORDER = ("new", "needs-info", "ready-for-agent", "ready-for-human", "wontfix")
STATES = frozenset(STATE_ORDER)

# Transitions are the mechanics table in .github/TRIAGE_POLICY.md, extended by
# step 6 of the practice: a closure is reopened by returning to "new" and
# re-running categorize and verify.
LEGAL_TRANSITIONS = {
    "new": frozenset({"needs-info", "ready-for-agent", "ready-for-human", "wontfix"}),
    "needs-info": frozenset({"ready-for-agent", "ready-for-human", "wontfix"}),
    "ready-for-agent": frozenset({"needs-info", "ready-for-human", "wontfix"}),
    "ready-for-human": frozenset({"needs-info", "ready-for-agent", "wontfix"}),
    "wontfix": frozenset({"new"}),
}

# "wontfix" is the only state the triage policy reserves to a human maintainer
# ("Human maintainer only" in both its label and transition tables).
HUMAN_ENTRY_STATES = frozenset({"wontfix"})

PUBLIC_CATEGORIES = ("bug", "enhancement")
# Practice step 1 stops triage for conduct, safety, access, and legal reports;
# ops/BETA_OPS.md routes safety, privacy, access, and conduct straight to the
# private intake owner. The union is the private-routing set.
PRIVATE_CATEGORIES = ("access", "conduct", "legal", "privacy", "safety")
CATEGORY_ORDER = tuple(sorted(PUBLIC_CATEGORIES + PRIVATE_CATEGORIES))
CATEGORIES = frozenset(CATEGORY_ORDER)
PRIVATE_CATEGORY_SET = frozenset(PRIVATE_CATEGORIES)

ACTORS = ("agent", "human")

# Role labels drawn from ops/BETA_OPS.md (roles table), .github/TRIAGE_POLICY.md
# (maintainer and agent roles) and community/MODERATION.md (roles and authority).
ROLE_ORDER = (
    "agent-sponsor",
    "authorized-inviter",
    "beta-owner",
    "bounded-agent",
    "human-maintainer",
    "human-moderator",
    "human-triager",
    "maintainer-on-duty",
    "private-intake-owner",
    "release-owner",
    "reporter",
)
ROLES = frozenset(ROLE_ORDER)
AGENT_ROLES = frozenset({"bounded-agent"})
HUMAN_ROLES = ROLES - AGENT_ROLES
# Closure is a maintainer decision (triage policy, "Maintainer and agent roles").
MAINTAINER_ROLES = frozenset({"beta-owner", "human-maintainer", "maintainer-on-duty"})
# Private intake owner and human moderator own conduct and safety matters
# (ops/BETA_OPS.md escalation routes; community/MODERATION.md).
PRIVATE_ROUTE_ROLES = frozenset({"human-moderator", "private-intake-owner"})
PRIVATE_ROUTES = ("code-of-conduct-private-report", "private-intake-route")

STATES_REQUIRING_OWNER = frozenset({"needs-info", "ready-for-agent", "ready-for-human", "wontfix"})

ALLOWED_FIELDS = (
    "record_id",
    "subject_ref",
    "state",
    "category",
    "owner_role",
    "last_actor",
    "updated",
    "evidence",
    "history",
)
REQUIRED_FIELDS = ("record_id", "subject_ref", "state", "category", "last_actor", "updated")
HISTORY_FIELDS = ("from", "to", "actor", "role", "date")

# Keys that would put a person, an identity, or message content into a record.
DENIED_FIELDS = frozenset(
    {
        "assignee", "attachment", "author", "contact", "conversation", "dm",
        "email", "employer", "excerpt", "handle", "ip", "ip_address",
        "location", "member", "message", "message_body", "name",
        "organization", "phone", "quote", "reporter_handle", "reporter_name",
        "screenshot", "thread", "transcript", "user", "username",
    }
)

EVIDENCE_SPECS = {
    "verification_attempt": ("text", "what was actually run, read, or inspected; write \"not attempted\" when nothing was"),
    "commit_checked": ("commit", "the commit id verification ran against, 7-40 hexadecimal characters"),
    "inspected_paths": ("paths", "repository-relative paths that exist under --root"),
    "observed_vs_expected": ("text", "what was observed and what the artifact should do instead"),
    "bounded_scope_reason": ("text", "why the fix touches no permissions, security, licensing, data, or conduct scope"),
    "missing_information": ("text", "what the report does not contain"),
    "specific_ask": ("text", "the one thing the next owner must supply"),
    "check_point": ("date", "ISO date when an unanswered record returns to the queue"),
    "maintainer_decision": ("text", "the specific decision the human maintainer must make"),
    "problem_statement": ("text", "the Practitioner problem the request states"),
    "affected_workflow": ("text", "the recurring work the request would change"),
    "alternatives_checked": ("text", "existing artifacts or approaches already checked"),
    "human_decision_reason": ("text", "the human maintainer's written reason for closing"),
    "duplicate_of": ("subject-ref", "the retained item, as \"issue #N\", \"pull-request #N\", or a record id"),
    "private_route": ("route", "the named private route the report was handed to; no case detail"),
    "routing_fact": ("text", "the minimum non-sensitive fact needed to route it; no identities, no evidence"),
}

RECORD_ID_RE = re.compile(r"^[A-Z]{2,6}-\d{4}-\d{2,6}$")
SUBJECT_REF_RE = re.compile(r"^(issue|pull-request) #\d+$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PLACEHOLDER_RE = re.compile(r"^(todo|tbd|n/?a|none|unknown|\?+|-+)$", re.IGNORECASE)
MIN_TEXT_LENGTH = 8

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
HANDLE_RE = re.compile(r"(?<![A-Za-z0-9._%+/-])@[A-Za-z][A-Za-z0-9._-]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(?:\+\d{1,3}[ .\-]?)?(?:\(\d{3}\)|\d{3})[ .\-]\d{3}[ .\-]\d{4}(?!\d)")
SECRET_RE = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|ghp_[A-Za-z0-9]{16,}"
    r"|xox[baprs]-[A-Za-z0-9-]{10,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|sk-[A-Za-z0-9]{20,}"
)

REDACTION_REF = "templates/REDACTION_CHECKLIST.md section 3"


class UsageError(Exception):
    """Raised for an operator mistake, reported with exit code 2."""


def problem(relative: str, locator: str, message: str, fix: str) -> str:
    return f"{relative}: {locator}: {message} Fix: {fix}."


def joined(values) -> str:
    return ", ".join(values)


# --- Loading ----------------------------------------------------------------

def split_front_matter(text: str) -> tuple[str | None, str]:
    """Return ``(front_matter_text, body)``; front matter is ``None`` when absent."""
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1:])
    return None, text


def load_record(path: Path, relative: str) -> tuple[dict | None, str, list[str]]:
    """Parse a record file into ``(front_matter, body, errors)``."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, "", [problem(relative, "file", f"cannot be read ({exc}).", "check the path and permissions")]
    front_matter_text, body = split_front_matter(text)
    if front_matter_text is None:
        return None, text, [
            problem(
                relative,
                "front matter",
                "no YAML front matter found.",
                "start the file with a `---` line, the record fields, and a closing `---` line",
            )
        ]
    try:
        data = yaml.safe_load(front_matter_text)
    except yaml.YAMLError as exc:
        detail = str(exc).replace("\n", " ")
        return None, body, [problem(relative, "front matter", f"is not valid YAML ({detail}).", "correct the YAML syntax")]
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return None, body, [
            problem(relative, "front matter", "is not a mapping of fields.", "write one `field: value` pair per line")
        ]
    return data, body, []


def as_text(value) -> str:
    """Render a scalar front-matter value as the string the checks read."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


# --- Field-level checks -----------------------------------------------------

def check_denied_keys(node, relative: str, prefix: str, errors: list[str]) -> None:
    if isinstance(node, dict):
        for key in node:
            name = as_text(key)
            locator = f"{prefix}{name}" if prefix else name
            if name.lower() in DENIED_FIELDS:
                errors.append(
                    problem(
                        relative,
                        locator,
                        "names a person, an identity, or message content, which a triage record never carries.",
                        f"remove the field and reference the item with `subject_ref` only ({REDACTION_REF})",
                    )
                )
            check_denied_keys(node[key], relative, f"{locator}.", errors)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            check_denied_keys(item, relative, f"{prefix[:-1]}[{index}]." if prefix else f"[{index}].", errors)


def scan_personal_data(text: str, relative: str) -> list[str]:
    """Report personal data, identities, and secrets anywhere in the record."""
    errors: list[str] = []
    for number, line in enumerate(text.split("\n"), start=1):
        locator = f"line {number}"
        emails = EMAIL_RE.findall(line)
        if emails:
            errors.append(
                problem(
                    relative,
                    locator,
                    "contains an email address.",
                    f"remove it; a triage record carries no personal data ({REDACTION_REF})",
                )
            )
        stripped = EMAIL_RE.sub(" ", line)
        if HANDLE_RE.search(stripped):
            errors.append(
                problem(
                    relative,
                    locator,
                    "contains a member handle.",
                    f"remove it and use a role label instead ({REDACTION_REF})",
                )
            )
        if PHONE_RE.search(stripped):
            errors.append(
                problem(
                    relative,
                    locator,
                    "contains a phone number.",
                    f"remove it; a triage record carries no personal data ({REDACTION_REF})",
                )
            )
        if SECRET_RE.search(line):
            errors.append(
                problem(
                    relative,
                    locator,
                    "contains a credential or key.",
                    "remove it and rotate the secret in its originating system (templates/REDACTION_CHECKLIST.md section 4)",
                )
            )
    return errors


def check_text_value(value, relative: str, locator: str, errors: list[str]) -> None:
    text = as_text(value).strip()
    if PLACEHOLDER_RE.match(text) or len(text) < MIN_TEXT_LENGTH:
        errors.append(
            problem(
                relative,
                locator,
                "is a placeholder or too short to be evidence.",
                f"write at least {MIN_TEXT_LENGTH} characters describing what was actually observed or asked",
            )
        )


def check_paths_value(value, relative: str, locator: str, root: Path, errors: list[str]) -> None:
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        errors.append(
            problem(relative, locator, "is not a path or a list of paths.", "write a list of repository-relative paths")
        )
        return
    if not items:
        errors.append(problem(relative, locator, "is an empty list.", "name at least one repository-relative path"))
        return
    for index, item in enumerate(items):
        target = as_text(item).strip()
        entry = f"{locator}[{index}]"
        if not target:
            errors.append(problem(relative, entry, "is empty.", "name a repository-relative path"))
            continue
        if target.startswith("/") or target.startswith("~"):
            errors.append(
                problem(relative, entry, f"'{target}' is not repository-relative.", "write the path relative to --root")
            )
            continue
        resolved = (root / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(
                problem(relative, entry, f"'{target}' resolves outside the repository.", "point at a path inside --root")
            )
            continue
        if not resolved.exists():
            errors.append(
                problem(
                    relative,
                    entry,
                    f"'{target}' does not exist under {root}.",
                    "point at a file or directory that exists, or record what is missing instead",
                )
            )


def check_commit_value(value, relative: str, locator: str, errors: list[str]) -> None:
    text = as_text(value).strip()
    if not COMMIT_RE.match(text):
        errors.append(
            problem(
                relative,
                locator,
                f"'{text}' is not a commit id.",
                "record 7-40 hexadecimal characters; quote a numeric-looking id so it stays a string",
            )
        )


def check_date_value(value, relative: str, locator: str, errors: list[str]) -> str | None:
    text = as_text(value).strip()
    if not ISO_DATE_RE.match(text):
        errors.append(problem(relative, locator, f"'{text}' is not an ISO date.", "write the date as YYYY-MM-DD"))
        return None
    try:
        date.fromisoformat(text)
    except ValueError:
        errors.append(problem(relative, locator, f"'{text}' is not a real calendar date.", "write a valid YYYY-MM-DD date"))
        return None
    return text


def check_subject_ref_value(value, relative: str, locator: str, errors: list[str], allow_record_id: bool = False) -> None:
    text = as_text(value).strip()
    if SUBJECT_REF_RE.match(text):
        return
    if allow_record_id and RECORD_ID_RE.match(text):
        return
    forms = '"issue #N" or "pull-request #N"'
    if allow_record_id:
        forms += ' or a record id such as "TR-2026-001"'
    errors.append(
        problem(
            relative,
            locator,
            f"'{text}' is not a permitted reference.",
            f"use {forms}; never a title, a link to a message, or a person",
        )
    )


def check_route_value(value, relative: str, locator: str, errors: list[str]) -> None:
    text = as_text(value).strip()
    if text not in PRIVATE_ROUTES:
        errors.append(
            problem(
                relative,
                locator,
                f"'{text}' is not a named private route.",
                f"use one of: {joined(PRIVATE_ROUTES)}; never a link, an address, or case detail",
            )
        )


def check_evidence_value(name: str, value, relative: str, root: Path, errors: list[str]) -> None:
    kind = EVIDENCE_SPECS[name][0]
    locator = f"evidence.{name}"
    if value is None:
        errors.append(problem(relative, locator, "is empty.", f"record {EVIDENCE_SPECS[name][1]}"))
        return
    if kind == "text":
        check_text_value(value, relative, locator, errors)
    elif kind == "paths":
        check_paths_value(value, relative, locator, root, errors)
    elif kind == "commit":
        check_commit_value(value, relative, locator, errors)
    elif kind == "date":
        check_date_value(value, relative, locator, errors)
    elif kind == "subject-ref":
        check_subject_ref_value(value, relative, locator, errors, allow_record_id=True)
    elif kind == "route":
        check_route_value(value, relative, locator, errors)


# --- State machine rules ----------------------------------------------------

def required_evidence(state: str, category: str) -> tuple[str, ...]:
    """Evidence the practice's decision-rules table requires for a state."""
    if state == "needs-info":
        return ("verification_attempt", "missing_information", "specific_ask", "check_point")
    if state == "ready-for-agent":
        return (
            "verification_attempt",
            "commit_checked",
            "inspected_paths",
            "observed_vs_expected",
            "bounded_scope_reason",
        )
    if state == "ready-for-human":
        if category in PRIVATE_CATEGORY_SET:
            return ("private_route", "routing_fact")
        if category == "enhancement":
            return ("problem_statement", "affected_workflow", "alternatives_checked", "maintainer_decision")
        return (
            "verification_attempt",
            "commit_checked",
            "inspected_paths",
            "observed_vs_expected",
            "maintainer_decision",
        )
    if state == "wontfix":
        return ("human_decision_reason",)
    return ()


def alternative_evidence(state: str, category: str) -> tuple[str, ...]:
    """Evidence of which at least one member must be present."""
    if state == "wontfix":
        return ("inspected_paths", "duplicate_of")
    return ()


def category_state_conflict(state: str, category: str) -> tuple[str, str] | None:
    """Return ``(message, fix)`` when a category may not sit in a state."""
    if category in PRIVATE_CATEGORY_SET and state != "ready-for-human":
        return (
            f"category '{category}' is a private-routing category, so it may not sit in state '{state}'.",
            "stop public triage, keep only the minimum routing fact, and set state to ready-for-human "
            "with owner_role private-intake-owner or human-moderator "
            "(practices/004-issue-triage.md, Method step 1)",
        )
    if state == "ready-for-agent" and category != "bug":
        return (
            f"state 'ready-for-agent' requires category 'bug', not '{category}'.",
            "route a verified enhancement or a private-routing category to ready-for-human instead "
            "(practices/004-issue-triage.md, decision rules)",
        )
    return None


def required_owner_roles(state: str, category: str) -> frozenset[str] | None:
    """Roles permitted to own a record in a state, or ``None`` for any role."""
    if category in PRIVATE_CATEGORY_SET:
        return PRIVATE_ROUTE_ROLES
    if state == "wontfix":
        return MAINTAINER_ROLES
    if state == "ready-for-human":
        return frozenset(HUMAN_ROLES)
    return None


def actor_state_conflict(actor: str, state: str, category: str) -> tuple[str, str] | None:
    """Return ``(message, fix)`` when an actor may not leave a record in a state."""
    if actor != "agent":
        return None
    if state in HUMAN_ENTRY_STATES:
        return (
            f"last_actor 'agent' may not leave a record in the human-owned state '{state}'.",
            "an agent labels, verifies, and recommends; a human maintainer records the close decision "
            "and becomes the last actor (.github/TRIAGE_POLICY.md, maintainer and agent roles)",
        )
    if category in PRIVATE_CATEGORY_SET:
        return (
            f"last_actor 'agent' may not hold a '{category}' record; it is human-owned end to end.",
            "hand the record to the private intake owner and record the human as last_actor "
            "(community/MODERATION.md, roles and authority)",
        )
    return None


# --- Record validation ------------------------------------------------------

def validate_record(path: Path, root: Path) -> list[str]:
    """Return every violation found in one triage record."""
    root = Path(root).resolve()
    try:
        relative = Path(path).resolve().relative_to(root).as_posix()
    except ValueError:
        relative = Path(path).as_posix()
    data, body, errors = load_record(Path(path), relative)
    if data is None:
        return errors

    raw_text = Path(path).read_text(encoding="utf-8")
    errors.extend(scan_personal_data(raw_text, relative))
    check_denied_keys(data, relative, "", errors)

    for key in data:
        name = as_text(key)
        if name not in ALLOWED_FIELDS and name.lower() not in DENIED_FIELDS:
            errors.append(
                problem(
                    relative,
                    name,
                    "is not a triage record field.",
                    f"remove it; the record fields are: {joined(ALLOWED_FIELDS)}",
                )
            )
    for name in REQUIRED_FIELDS:
        if data.get(name) in (None, ""):
            errors.append(problem(relative, name, "is missing.", f"add `{name}` to the front matter"))

    if not body.strip():
        errors.append(
            problem(
                relative,
                "body",
                "has no routing record.",
                "write the state-change record below the front matter so a reader can see what would change the decision",
            )
        )

    record_id = as_text(data.get("record_id", "")).strip()
    if record_id and not RECORD_ID_RE.match(record_id):
        errors.append(
            problem(
                relative,
                "record_id",
                f"'{record_id}' is not a non-identifying record id.",
                "use PREFIX-YYYY-NNN, for example TR-2026-001; never a name or a handle",
            )
        )
    if data.get("subject_ref") not in (None, ""):
        check_subject_ref_value(data["subject_ref"], relative, "subject_ref", errors)
    if data.get("updated") not in (None, ""):
        updated = check_date_value(data["updated"], relative, "updated", errors)
    else:
        updated = None

    state = as_text(data.get("state", "")).strip()
    if state and state not in STATES:
        errors.append(
            problem(relative, "state", f"'{state}' is not a triage state.", f"use one of: {joined(STATE_ORDER)}")
        )
        state = ""
    category = as_text(data.get("category", "")).strip()
    if category and category not in CATEGORIES:
        errors.append(
            problem(
                relative,
                "category",
                f"'{category}' is not a triage category.",
                f"use one of: {joined(CATEGORY_ORDER)}",
            )
        )
        category = ""
    actor = as_text(data.get("last_actor", "")).strip()
    if actor and actor not in ACTORS:
        errors.append(
            problem(relative, "last_actor", f"'{actor}' is not an actor.", f"use one of: {joined(ACTORS)}")
        )
        actor = ""

    owner = data.get("owner_role")
    owner_present = owner not in (None, "")
    owner_role = as_text(owner).strip() if owner_present else ""
    if owner_role and owner_role not in ROLES:
        errors.append(
            problem(
                relative,
                "owner_role",
                f"'{owner_role}' is not a role label.",
                f"name a role, never a person: {joined(ROLE_ORDER)}",
            )
        )
        owner_role = ""
    if state and state in STATES_REQUIRING_OWNER and not owner_present:
        errors.append(
            problem(
                relative,
                "owner_role",
                f"is missing, and state '{state}' needs a next owner.",
                f"name the owning role: {joined(ROLE_ORDER)}",
            )
        )
    if state == "new" and owner_present:
        errors.append(
            problem(
                relative,
                "owner_role",
                "is set while the record is still in state 'new'.",
                "categorize and route the record first, then name the next owner",
            )
        )

    if state and category:
        conflict = category_state_conflict(state, category)
        if conflict:
            errors.append(problem(relative, "state", conflict[0], conflict[1]))
    if actor and state and category:
        conflict = actor_state_conflict(actor, state, category)
        if conflict:
            errors.append(problem(relative, "last_actor", conflict[0], conflict[1]))
    if owner_role and state and category:
        permitted = required_owner_roles(state, category)
        if permitted is not None and owner_role not in permitted:
            errors.append(
                problem(
                    relative,
                    "owner_role",
                    f"'{owner_role}' may not own a '{category}' record in state '{state}'.",
                    f"name one of: {joined(sorted(permitted))}",
                )
            )

    errors.extend(validate_evidence(data, relative, root, state, category))
    errors.extend(validate_history(data, relative, state, actor, updated))
    return sorted(set(errors))


def validate_evidence(data: dict, relative: str, root: Path, state: str, category: str) -> list[str]:
    errors: list[str] = []
    evidence = data.get("evidence")
    if evidence is None:
        evidence = {}
    if not isinstance(evidence, dict):
        return [
            problem(
                relative,
                "evidence",
                "is not a mapping of evidence fields.",
                f"write `evidence:` followed by indented `name: value` pairs from: {joined(sorted(EVIDENCE_SPECS))}",
            )
        ]
    for key in evidence:
        name = as_text(key)
        if name not in EVIDENCE_SPECS:
            if name.lower() not in DENIED_FIELDS:
                errors.append(
                    problem(
                        relative,
                        f"evidence.{name}",
                        "is not a known evidence field.",
                        f"use one of: {joined(sorted(EVIDENCE_SPECS))}",
                    )
                )
            continue
        check_evidence_value(name, evidence[key], relative, root, errors)

    if not state:
        return errors
    if state == "new" and evidence:
        errors.append(
            problem(
                relative,
                "evidence",
                "is recorded while the record is still in state 'new'.",
                "route the record to the state its evidence supports, or remove the evidence",
            )
        )
    for name in required_evidence(state, category or "bug"):
        if evidence.get(name) in (None, "", [], {}):
            errors.append(
                problem(
                    relative,
                    f"evidence.{name}",
                    f"is missing, and state '{state}' requires it.",
                    f"record {EVIDENCE_SPECS[name][1]}",
                )
            )
    alternatives = alternative_evidence(state, category or "bug")
    if alternatives and not any(evidence.get(name) not in (None, "", [], {}) for name in alternatives):
        errors.append(
            problem(
                relative,
                "evidence",
                f"state '{state}' needs at least one of: {joined(alternatives)}.",
                "point at the documented behavior that makes the report expected, or at the retained duplicate",
            )
        )
    return errors


def validate_history(data: dict, relative: str, state: str, actor: str, updated: str | None) -> list[str]:
    errors: list[str] = []
    history = data.get("history")
    if history is None:
        return errors
    if not isinstance(history, list) or not history:
        return [
            problem(
                relative,
                "history",
                "is not a non-empty list of transitions.",
                "write one `- from: ... / to: ... / actor: ... / role: ... / date: ...` entry per state change",
            )
        ]

    previous_state: str | None = None
    previous_date: str | None = None
    last_entry_state = ""
    last_entry_actor = ""
    for index, entry in enumerate(history):
        locator = f"history[{index}]"
        if not isinstance(entry, dict):
            errors.append(
                problem(relative, locator, "is not a transition mapping.", f"give it the fields: {joined(HISTORY_FIELDS)}")
            )
            previous_state = None
            continue
        for name in HISTORY_FIELDS:
            if entry.get(name) in (None, ""):
                errors.append(problem(relative, f"{locator}.{name}", "is missing.", f"add `{name}` to the transition"))
        source = as_text(entry.get("from", "")).strip()
        target = as_text(entry.get("to", "")).strip()
        entry_actor = as_text(entry.get("actor", "")).strip()
        entry_role = as_text(entry.get("role", "")).strip()
        for name, value in (("from", source), ("to", target)):
            if value and value not in STATES:
                errors.append(
                    problem(
                        relative,
                        f"{locator}.{name}",
                        f"'{value}' is not a triage state.",
                        f"use one of: {joined(STATE_ORDER)}",
                    )
                )
        if entry_actor and entry_actor not in ACTORS:
            errors.append(
                problem(relative, f"{locator}.actor", f"'{entry_actor}' is not an actor.", f"use one of: {joined(ACTORS)}")
            )
        if entry_role and entry_role not in ROLES:
            errors.append(
                problem(
                    relative,
                    f"{locator}.role",
                    f"'{entry_role}' is not a role label.",
                    f"name a role, never a person: {joined(ROLE_ORDER)}",
                )
            )
        if entry_role and entry_actor == "human" and entry_role in AGENT_ROLES:
            errors.append(
                problem(
                    relative,
                    f"{locator}.role",
                    f"'{entry_role}' is an agent role, but the actor is 'human'.",
                    "name the human role that made the move",
                )
            )
        if entry_role and entry_actor == "agent" and entry_role not in AGENT_ROLES:
            errors.append(
                problem(
                    relative,
                    f"{locator}.role",
                    f"'{entry_role}' is a human role, but the actor is 'agent'.",
                    "record `role: bounded-agent` for an agent move",
                )
            )
        entry_date = None
        if entry.get("date") not in (None, ""):
            entry_date = check_date_value(entry["date"], relative, f"{locator}.date", errors)
        if entry_date and previous_date and entry_date < previous_date:
            errors.append(
                problem(
                    relative,
                    f"{locator}.date",
                    f"'{entry_date}' precedes the previous transition on {previous_date}.",
                    "record transitions oldest first with non-decreasing dates",
                )
            )
        if entry_date:
            previous_date = entry_date

        if index == 0 and source and source != "new":
            errors.append(
                problem(
                    relative,
                    f"{locator}.from",
                    f"the first transition starts at '{source}'.",
                    "a record enters triage in state 'new'; start the history there",
                )
            )
        if previous_state and source and source != previous_state:
            errors.append(
                problem(
                    relative,
                    f"{locator}.from",
                    f"'{source}' does not continue from the previous transition, which ended at '{previous_state}'.",
                    "chain each transition to the one before it",
                )
            )
        if source in STATES and target in STATES:
            if target not in LEGAL_TRANSITIONS[source]:
                errors.append(
                    problem(
                        relative,
                        f"{locator}.to",
                        f"'{source}' -> '{target}' is not a legal transition.",
                        f"legal moves from '{source}': {joined(sorted(LEGAL_TRANSITIONS[source])) or 'none'} "
                        "(.github/TRIAGE_POLICY.md, state transitions)",
                    )
                )
        if target in HUMAN_ENTRY_STATES and entry_actor == "agent":
            errors.append(
                problem(
                    relative,
                    f"{locator}.actor",
                    f"an agent recorded the move into the human-owned state '{target}'.",
                    "a human maintainer makes and records the close decision "
                    "(.github/TRIAGE_POLICY.md, maintainer and agent roles)",
                )
            )
        previous_state = target if target in STATES else None
        last_entry_state = target
        last_entry_actor = entry_actor

    if state and last_entry_state and last_entry_state != state:
        errors.append(
            problem(
                relative,
                "state",
                f"'{state}' does not match the last transition, which ended at '{last_entry_state}'.",
                "append the transition that moved the record, or correct `state`",
            )
        )
    if actor and last_entry_actor and last_entry_actor != actor:
        errors.append(
            problem(
                relative,
                "last_actor",
                f"'{actor}' does not match the last transition, made by '{last_entry_actor}'.",
                "record the actor that actually made the last move",
            )
        )
    if updated and previous_date and previous_date > updated:
        errors.append(
            problem(
                relative,
                "updated",
                f"'{updated}' precedes the last transition on {previous_date}.",
                "set `updated` to the date of the last transition or later",
            )
        )
    return errors


# --- next -------------------------------------------------------------------

def describe_evidence(names) -> list[str]:
    return [f"      - {name}: {EVIDENCE_SPECS[name][1]}" for name in names]


def plan_next(path: Path, root: Path) -> tuple[list[str], list[str]]:
    """Return ``(report_lines, errors)`` for the ``next`` command."""
    root = Path(root).resolve()
    try:
        relative = Path(path).resolve().relative_to(root).as_posix()
    except ValueError:
        relative = Path(path).as_posix()
    data, _body, errors = load_record(Path(path), relative)
    if data is None:
        return [], errors

    state = as_text(data.get("state", "")).strip()
    category = as_text(data.get("category", "")).strip()
    actor = as_text(data.get("last_actor", "")).strip()
    record_id = as_text(data.get("record_id", "")).strip() or "(no record_id)"
    if state not in STATES:
        return [], [
            problem(
                relative,
                "state",
                f"'{state}' is not a triage state, so the legal next states are undefined.",
                f"set `state` to one of: {joined(STATE_ORDER)}",
            )
        ]
    if category not in CATEGORIES:
        return [], [
            problem(
                relative,
                "category",
                f"'{category}' is not a triage category, so the legal next states are undefined.",
                f"set `category` to one of: {joined(CATEGORY_ORDER)}",
            )
        ]

    lines = [
        f"{relative}",
        f"Record {record_id}: state '{state}', category '{category}', last actor '{actor or 'unrecorded'}'.",
        "",
    ]
    candidates = [target for target in STATE_ORDER if target in LEGAL_TRANSITIONS[state]]
    permitted = [target for target in candidates if category_state_conflict(target, category) is None]
    blocked = [target for target in candidates if category_state_conflict(target, category) is not None]

    if not permitted:
        lines.append("Legal next states: none.")
        if category in PRIVATE_CATEGORY_SET:
            lines.append(
                f"  A '{category}' record stays with the private intake owner or human moderator; "
                "public triage does not move it."
            )
    else:
        lines.append("Legal next states:")
        for target in permitted:
            lines.append("")
            lines.append(f"  {target}")
            if target in HUMAN_ENTRY_STATES:
                mover = "human maintainer only (beta-owner, human-maintainer, or maintainer-on-duty)"
            else:
                mover = "human triager, or a bounded agent recording a recommendation"
            lines.append(f"    may be moved by: {mover}")
            owners = required_owner_roles(target, category)
            if target == "new":
                lines.append("    owner_role: cleared; re-run categorize and verify before routing again")
            elif owners is None:
                lines.append(f"    owner_role: required, any role label ({joined(ROLE_ORDER)})")
            else:
                lines.append(f"    owner_role: required, one of {joined(sorted(owners))}")
            required = required_evidence(target, category)
            alternatives = alternative_evidence(target, category)
            if required:
                lines.append("    required evidence:")
                lines.extend(describe_evidence(required))
            elif not alternatives:
                lines.append("    required evidence: none")
            if alternatives:
                lines.append("    plus at least one of:")
                lines.extend(describe_evidence(alternatives))
    if blocked:
        lines.append("")
        lines.append("Blocked by category:")
        for target in blocked:
            message, _fix = category_state_conflict(target, category)
            lines.append(f"  {target} - {message}")
    lines.append("")
    lines.append(
        "This tool records and checks triage. It never applies a label, closes an issue, "
        "removes content, or restricts a person; a human maintainer owns accept and close."
    )
    return lines, []


# --- CLI --------------------------------------------------------------------

def collect_records(paths, root: Path) -> list[Path]:
    """Expand CLI paths into record files; directories skip `README.md`."""
    found: list[Path] = []
    for raw in paths:
        candidate = Path(raw)
        if not candidate.exists():
            raise UsageError(f"no such path: {raw}")
        if candidate.is_dir():
            for markdown in sorted(candidate.rglob("*.md")):
                if markdown.name == "README.md":
                    continue
                found.append(markdown)
        else:
            found.append(candidate)
    if not found:
        raise UsageError("no triage records found in the given paths")
    return found


def run_validate(paths, root: Path) -> int:
    records = collect_records(paths, root)
    errors: list[str] = []
    for record in records:
        errors.extend(validate_record(record, root))
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Checked {len(records)} triage record(s): {len(errors)} violation(s).")
    return 1 if errors else 0


def run_next(path: str, root: Path) -> int:
    candidate = Path(path)
    if not candidate.exists():
        raise UsageError(f"no such path: {path}")
    if candidate.is_dir():
        raise UsageError(f"next takes one record file, not a directory: {path}")
    lines, errors = plan_next(candidate, root)
    for error in errors:
        print(error, file=sys.stderr)
    for line in lines:
        print(line)
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    validate_parser = sub.add_parser("validate", help="check triage records against the state machine")
    validate_parser.add_argument("paths", nargs="+", help="record files or directories to check")
    validate_parser.add_argument("--root", default=str(DEFAULT_ROOT), help="repository root evidence paths resolve against")
    next_parser = sub.add_parser("next", help="print the legal next states and the evidence each requires")
    next_parser.add_argument("path", help="the record file to read")
    next_parser.add_argument("--root", default=str(DEFAULT_ROOT), help="repository root evidence paths resolve against")
    args = parser.parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f"usage error: --root is not a directory: {args.root}", file=sys.stderr)
        return 2
    try:
        if args.command == "validate":
            return run_validate(args.paths, root)
        return run_next(args.path, root)
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
