#!/usr/bin/env python3
"""Deterministic offline validator for agent output packets.

A packet is the bounded record an agent hands to a human reviewer: YAML front
matter plus the fixed sections defined in ``docs/schemas/AGENT_PACKET_SCHEMA.md``.
This validator makes the packet contract machine-checkable so a reviewer can
tell a bounded packet from an agent that widened its own scope.

Checks applied to every packet:

- front matter parses as YAML and carries every required field with a
  controlled value; ``status`` is ``draft`` and ``human_decision_required``
  is ``true``;
- ``packet_id`` is a slug and is unique across the invocation,
  ``agent_version`` is ``MAJOR.MINOR.PATCH``, ``run_date`` is an ISO date and
  ``source_commit`` is hexadecimal;
- ``decision_owner`` is one controlled operating role, so a personal name
  cannot be recorded there;
- ``agent_id`` appears in ``buzz/agents/registry.yaml`` when that file exists
  and lists identifiers; the cross-check is skipped with an informational note
  when it does not;
- every ``inputs`` entry has a provenance pointer and a trust level, with an
  as-of date whenever the pointer is a URL;
- the seven required sections exist exactly once, in canonical order, and none
  is empty;
- every claim bullet under ``What the evidence shows`` carries a repository
  path that resolves under ``--root`` or a source URL with an as-of date;
- ``Recommended action`` holds exactly one action plus a ``Verification:``
  line a human can run without agent privileges;
- ``Decision requested from a human`` names the ``decision_owner`` role and
  ``Provenance`` accounts for every declared input; and
- visible prose asserts no promotion, no maturity or evidence change, and no
  cleared gate or lifted hold.

The validator never decides anything. A packet that passes is worth reading,
not worth accepting; the human decision belongs in the affected Git record.

Exit codes: 0 = every packet valid, 1 = at least one packet invalid or
unreadable, 2 = usage error.
"""
from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit("PyYAML is required: install it before running this validator") from exc

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_RELATIVE = "buzz/agents/registry.yaml"

REQUIRED_FIELDS = (
    "packet_id",
    "agent_id",
    "agent_version",
    "run_date",
    "source_commit",
    "inputs",
    "autonomy",
    "human_decision_required",
    "decision_owner",
    "status",
)
KNOWN_FIELDS = frozenset(REQUIRED_FIELDS) | {"task_ref", "supersedes"}

AUTONOMY_LEVELS = frozenset({"observe", "draft", "recommend"})
TRUST_LEVELS = frozenset({"untrusted", "repository", "human_supplied"})
DECISION_OWNER_ROLES = frozenset(
    {
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
    }
)

REQUESTED_OUTCOME = "Requested outcome"
EVIDENCE_SECTION = "What the evidence shows"
NOT_ESTABLISHED = "What is not established"
RECOMMENDED_ACTION = "Recommended action"
DECISION_SECTION = "Decision requested from a human"
REFUSALS_SECTION = "Refusals and out-of-bounds requests"
PROVENANCE_SECTION = "Provenance"

REQUIRED_SECTIONS = (
    REQUESTED_OUTCOME,
    EVIDENCE_SECTION,
    NOT_ESTABLISHED,
    RECOMMENDED_ACTION,
    DECISION_SECTION,
    REFUSALS_SECTION,
    PROVENANCE_SECTION,
)

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
H1_RE = re.compile(r"^#\s+(\S.*)$")
H2_RE = re.compile(r"^##\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODE_SPAN_RE = re.compile(r"`+[^`\n]*`+")
TOP_BULLET_RE = re.compile(r"^(?:[-*+]|\d+\.)\s+\S")
URL_RE = re.compile(r"https?://\S+")
AS_OF_DATE_RE = re.compile(r"as[\s-]+of\b[^\n]{0,40}?(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
VERIFICATION_RE = re.compile(r"^Verification:\s*(\S.*)$", re.MULTILINE)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]\n]*\]\(\s*([^)\s]+)\s*\)")
REPO_PATH_RE = re.compile(
    r"(?<![\w./-])([\w.-]+(?:/[\w.-]+)*\.(?:md|py|json|ya?ml|txt|sh|toml|cfg|ini))(?![\w/-])"
)
NEGATION_RE = re.compile(r"\b(?:not|never|no|cannot|without|neither|nor)\b", re.IGNORECASE)
NEGATION_WINDOW = 40

PACKET_ID_MIN = 8
PACKET_ID_MAX = 80

FORBIDDEN_ASSERTIONS = (
    (
        re.compile(r"\b(?:is|are|was|were|has been|have been|now)\s+(?:hereby\s+)?promoted\b", re.IGNORECASE),
        "asserts a promotion; promotion is a human decision recorded outside the packet",
    ),
    (
        re.compile(r"\bpromotion\s+(?:is\s+)?(?:approved|complete|completed|granted|confirmed)\b", re.IGNORECASE),
        "asserts a promotion; promotion is a human decision recorded outside the packet",
    ),
    (
        re.compile(
            r"\b(?:maturity|evidence[_ ]quality)\b[^.\n]{0,40}?"
            r"\b(?:is now|has been (?:changed|updated|set|raised)|changed to|updated to|set to|raised to)\b",
            re.IGNORECASE,
        ),
        "asserts a maturity or evidence_quality change; an agent never changes those fields",
    ),
    (
        re.compile(
            r"\b(?:is|are|was|were|has been|have been|now)\s+marked\s+(?:as\s+)?"
            r"(?:tested|verified|stable|promoted)\b",
            re.IGNORECASE,
        ),
        "asserts a maturity change; an agent never changes those fields",
    ),
    (
        re.compile(
            r"\bgates?\b[^.\n]{0,40}?\b(?:is|are|was|were|has been|have been)\s+(?:now\s+)?"
            r"(?:cleared|met|satisfied|passed|closed|approved)\b",
            re.IGNORECASE,
        ),
        "asserts an owner gate is cleared; only the gate owner clears a gate",
    ),
    (
        re.compile(r"\bclear(?:ed|s)?\s+the\s+(?:owner\s+)?gate\b", re.IGNORECASE),
        "asserts an owner gate is cleared; only the gate owner clears a gate",
    ),
    (
        re.compile(
            r"\bholds?\b[^.\n]{0,40}?\b(?:is|are|was|were|has been|have been)\s+(?:now\s+)?"
            r"(?:lifted|cleared|released|removed)\b",
            re.IGNORECASE,
        ),
        "asserts an operating hold is lifted; only the hold owner lifts a hold",
    ),
    (
        re.compile(
            r"\bno\s+human\s+(?:review|decision|approval)\s+(?:is\s+)?(?:needed|required)\b",
            re.IGNORECASE,
        ),
        "asserts human review is unnecessary; every packet requires a human decision",
    ),
)


class Packet:
    """One parsed packet: front matter, masked body, and section index."""

    def __init__(self, relative: str, text: str) -> None:
        self.relative = relative
        self.text = text
        self.data: dict | None = None
        self.parse_errors: list[tuple[int, str]] = []
        self.front_lines: dict[str, int] = {}
        self.lines = text.split("\n")
        self.body_offset = 0
        self._parse_front_matter()
        body = self.lines[self.body_offset :]
        self.body_lines = body
        self.masked_lines = mask_code("\n".join(body)).split("\n")
        self.headings = [
            (index, match.group(1).strip())
            for index, line in enumerate(self.masked_lines)
            if (match := H2_RE.match(line))
        ]

    def _parse_front_matter(self) -> None:
        start = 0
        while start < len(self.lines) and self.lines[start].strip() == "":
            start += 1
        if start >= len(self.lines) or self.lines[start].strip() != "---":
            self.parse_errors.append((start + 1, "packet must begin with YAML front matter opened by '---'"))
            return
        end = None
        for index in range(start + 1, len(self.lines)):
            if self.lines[index].strip() == "---":
                end = index
                break
        if end is None:
            self.parse_errors.append((start + 1, "front matter is never closed with a second '---' line"))
            return
        block_lines = self.lines[start + 1 : end]
        self.body_offset = end + 1
        for offset, line in enumerate(block_lines):
            match = re.match(r"^([A-Za-z_][\w-]*)\s*:", line)
            if match:
                self.front_lines.setdefault(match.group(1), start + 2 + offset)
        try:
            data = yaml.safe_load("\n".join(block_lines))
        except yaml.YAMLError as exc:
            self.parse_errors.append((start + 1, f"front matter is not valid YAML: {compact(exc)}"))
            return
        if data is None:
            self.parse_errors.append((start + 1, "front matter is empty"))
            return
        if not isinstance(data, dict):
            self.parse_errors.append((start + 1, "front matter must be a mapping of fields"))
            return
        self.data = data

    def line_of(self, field: str) -> int:
        return self.front_lines.get(field, 1)

    def heading_line(self, name: str) -> int:
        for index, heading in self.headings:
            if heading == name:
                return self.body_offset + index + 1
        return 1

    def section_bounds(self, name: str) -> tuple[int, int] | None:
        for position, (index, heading) in enumerate(self.headings):
            if heading != name:
                continue
            following = self.headings[position + 1][0] if position + 1 < len(self.headings) else len(self.body_lines)
            return index + 1, following
        return None

    def section_lines(self, name: str) -> list[str]:
        bounds = self.section_bounds(name)
        if bounds is None:
            return []
        start, end = bounds
        return self.body_lines[start:end]

    def masked_section_lines(self, name: str) -> list[str]:
        bounds = self.section_bounds(name)
        if bounds is None:
            return []
        start, end = bounds
        return self.masked_lines[start:end]


def compact(value: object) -> str:
    return " ".join(str(value).split())


def mask_code(text: str) -> str:
    """Blank fenced blocks and inline code spans, preserving offsets and lines."""
    masked: list[str] = []
    fence = ""
    for line in text.split("\n"):
        marker = FENCE_RE.match(line)
        if fence:
            masked.append(" " * len(line))
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = ""
        elif marker:
            fence = marker.group(1)
            masked.append(" " * len(line))
        else:
            masked.append(line)
    return CODE_SPAN_RE.sub(lambda match: " " * len(match.group(0)), "\n".join(masked))


def as_text(value: object) -> str | None:
    """Normalize a scalar front-matter value to a string, or None when unusable."""
    if isinstance(value, bool):
        return None
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    return None


def is_iso_date(value: str) -> bool:
    if not DATE_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def top_level_bullets(lines: list[str]) -> list[tuple[int, str]]:
    """Return ``(offset, block_text)`` for each top-level list item in ``lines``."""
    bullets: list[tuple[int, str]] = []
    current: list[str] | None = None
    start = 0
    for offset, line in enumerate(lines):
        if TOP_BULLET_RE.match(line):
            if current is not None:
                bullets.append((start, "\n".join(current)))
            current = [line]
            start = offset
        elif current is not None:
            if line.startswith((" ", "\t")) and line.strip():
                current.append(line)
            elif not line.strip():
                continue
            else:
                bullets.append((start, "\n".join(current)))
                current = None
    if current is not None:
        bullets.append((start, "\n".join(current)))
    return bullets


def repository_path_candidates(block: str) -> list[str]:
    candidates: list[str] = []
    for target in MARKDOWN_LINK_RE.findall(block):
        if not re.match(r"^[A-Za-z][A-Za-z0-9+.\-]*:", target) and not target.startswith("#"):
            candidates.append(target.split("#", 1)[0])
    for token in REPO_PATH_RE.findall(block):
        candidates.append(token)
    seen: set[str] = set()
    ordered: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.add(candidate)
            ordered.append(candidate)
    return ordered


def resolves(root: Path, packet_dir: Path, candidate: str) -> bool:
    for base in (root, packet_dir):
        try:
            resolved = (base / candidate).resolve()
        except (OSError, ValueError):
            continue
        if resolved.exists():
            return True
    return False


def is_negated(masked_body: str, start: int) -> bool:
    """Report whether a negation appears earlier in the same sentence.

    The window stops at the start of the line and at the previous sentence
    boundary so a nearby heading or an earlier sentence cannot silence a
    genuine assertion.
    """
    line_start = masked_body.rfind("\n", 0, start) + 1
    sentence_start = masked_body.rfind(". ", line_start, start)
    window_start = max(line_start, sentence_start + 2, start - NEGATION_WINDOW)
    return bool(NEGATION_RE.search(masked_body[window_start:start]))


def collect_agent_ids(node: object) -> set[str]:
    """Collect agent identifiers from a registry document of unknown shape."""
    found: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if key in {"agent_id", "id"} and isinstance(value, str) and SLUG_RE.match(value.strip()):
                found.add(value.strip())
            if key == "agents" and isinstance(value, dict):
                found.update(name for name in value if isinstance(name, str) and SLUG_RE.match(name.strip()))
            found |= collect_agent_ids(value)
    elif isinstance(node, list):
        for item in node:
            found |= collect_agent_ids(item)
    return found


def load_registry_ids(root: Path, notes: list[str]) -> set[str] | None:
    """Return known agent identifiers, or None when the cross-check is skipped."""
    path = root / REGISTRY_RELATIVE
    if not path.is_file():
        notes.append(
            f"note: {REGISTRY_RELATIVE} is not present under {root}; "
            "skipping the agent_id registry cross-check."
        )
        return None
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        notes.append(
            f"note: {REGISTRY_RELATIVE} could not be read as YAML ({compact(exc)}); "
            "skipping the agent_id registry cross-check."
        )
        return None
    identifiers = collect_agent_ids(document)
    if not identifiers:
        notes.append(
            f"note: {REGISTRY_RELATIVE} lists no recognizable agent identifiers; "
            "skipping the agent_id registry cross-check."
        )
        return None
    return identifiers


def check_front_matter(packet: Packet, registry_ids: set[str] | None, seen_ids: dict[str, str], errors: list[str]) -> None:
    data = packet.data
    assert data is not None

    def add(field: str, message: str) -> None:
        errors.append(f"{packet.relative}:{packet.line_of(field)}: {message}")

    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            add(field, f"missing required front-matter field: {field}")
    for field in sorted(data):
        if field not in KNOWN_FIELDS:
            add(field, f"unknown front-matter field: {field}")

    packet_id = as_text(data.get("packet_id"))
    if packet_id:
        if not SLUG_RE.match(packet_id):
            add("packet_id", f"packet_id must be a lowercase slug: {packet_id}")
        elif not PACKET_ID_MIN <= len(packet_id) <= PACKET_ID_MAX:
            add("packet_id", f"packet_id must be {PACKET_ID_MIN}-{PACKET_ID_MAX} characters: {packet_id}")
        if packet_id in seen_ids:
            add("packet_id", f"duplicate packet_id {packet_id}; already used by {seen_ids[packet_id]}")
        else:
            seen_ids[packet_id] = packet.relative

    agent_id = as_text(data.get("agent_id"))
    if agent_id:
        if not SLUG_RE.match(agent_id):
            add("agent_id", f"agent_id must be a lowercase slug: {agent_id}")
        elif registry_ids is not None and agent_id not in registry_ids:
            known = ", ".join(sorted(registry_ids)) or "none"
            add("agent_id", f"agent_id {agent_id} is not listed in {REGISTRY_RELATIVE} (known: {known})")

    agent_version = as_text(data.get("agent_version"))
    if agent_version and not SEMVER_RE.match(agent_version):
        add("agent_version", f"agent_version must be MAJOR.MINOR.PATCH: {agent_version}")

    run_date = as_text(data.get("run_date"))
    if run_date and not is_iso_date(run_date):
        add("run_date", f"run_date must be an ISO date in YYYY-MM-DD form: {run_date}")

    source_commit = as_text(data.get("source_commit"))
    if source_commit and not COMMIT_RE.match(source_commit):
        add(
            "source_commit",
            f"source_commit must be 7-40 lowercase hexadecimal characters: {source_commit}",
        )

    autonomy = as_text(data.get("autonomy"))
    if autonomy and autonomy not in AUTONOMY_LEVELS:
        add("autonomy", f"autonomy must be one of {sorted(AUTONOMY_LEVELS)}: {autonomy}")

    if "human_decision_required" in data and data["human_decision_required"] is not True:
        add(
            "human_decision_required",
            "human_decision_required must be true; a packet never carries its own decision",
        )

    decision_owner = as_text(data.get("decision_owner"))
    if decision_owner and decision_owner not in DECISION_OWNER_ROLES:
        add(
            "decision_owner",
            f"decision_owner must be a role from {sorted(DECISION_OWNER_ROLES)}, "
            f"never a personal name: {decision_owner}",
        )

    status = as_text(data.get("status"))
    if status and status != "draft":
        add("status", f"status must be draft; a packet records no outcome: {status}")

    check_inputs(packet, errors)


def check_inputs(packet: Packet, errors: list[str]) -> None:
    data = packet.data
    assert data is not None
    line = packet.line_of("inputs")
    entries = data.get("inputs")
    if entries is None:
        return
    if not isinstance(entries, list) or not entries:
        errors.append(f"{packet.relative}:{line}: inputs must be a non-empty list of input records")
        return
    for position, entry in enumerate(entries, start=1):
        label = f"inputs[{position}]"
        if not isinstance(entry, dict):
            errors.append(f"{packet.relative}:{line}: {label} must be a mapping with ref and trust")
            continue
        ref = as_text(entry.get("ref"))
        if not ref:
            errors.append(f"{packet.relative}:{line}: {label} needs a non-empty ref provenance pointer")
        trust = as_text(entry.get("trust"))
        if not trust:
            errors.append(f"{packet.relative}:{line}: {label} needs a trust level")
        elif trust not in TRUST_LEVELS:
            errors.append(
                f"{packet.relative}:{line}: {label} trust must be one of {sorted(TRUST_LEVELS)}: {trust}"
            )
        as_of = as_text(entry.get("as_of"))
        if ref and URL_RE.match(ref):
            if not as_of:
                errors.append(
                    f"{packet.relative}:{line}: {label} points at a URL and needs an as_of date"
                )
            elif not is_iso_date(as_of):
                errors.append(
                    f"{packet.relative}:{line}: {label} as_of must be an ISO date in YYYY-MM-DD form: {as_of}"
                )
        elif as_of and not is_iso_date(as_of):
            errors.append(
                f"{packet.relative}:{line}: {label} as_of must be an ISO date in YYYY-MM-DD form: {as_of}"
            )


def check_sections(packet: Packet, errors: list[str]) -> None:
    if not any(H1_RE.match(line) for line in packet.masked_lines):
        errors.append(f"{packet.relative}:{packet.body_offset + 1}: packet body needs an H1 title")
    present = [heading for _, heading in packet.headings if heading in REQUIRED_SECTIONS]
    for name in REQUIRED_SECTIONS:
        count = present.count(name)
        if count == 0:
            errors.append(f"{packet.relative}:1: missing required section: {name}")
        elif count > 1:
            errors.append(f"{packet.relative}:{packet.heading_line(name)}: duplicate section: {name}")
    if len(present) == len(set(present)) and set(present) == set(REQUIRED_SECTIONS):
        expected = list(REQUIRED_SECTIONS)
        if present != expected:
            errors.append(
                f"{packet.relative}:1: sections are out of canonical order: "
                f"found {present}, expected {expected}"
            )
    for name in REQUIRED_SECTIONS:
        if name not in present:
            continue
        if not any(line.strip() for line in packet.masked_section_lines(name)):
            errors.append(f"{packet.relative}:{packet.heading_line(name)}: section is empty: {name}")


def check_evidence_claims(packet: Packet, root: Path, errors: list[str]) -> None:
    bounds = packet.section_bounds(EVIDENCE_SECTION)
    if bounds is None:
        return
    start, _ = bounds
    lines = packet.section_lines(EVIDENCE_SECTION)
    bullets = top_level_bullets(lines)
    if not bullets:
        errors.append(
            f"{packet.relative}:{packet.heading_line(EVIDENCE_SECTION)}: "
            f"{EVIDENCE_SECTION} needs at least one claim bullet"
        )
        return
    packet_dir = (root / packet.relative).parent
    for offset, block in bullets:
        line_no = packet.body_offset + start + offset + 1
        candidates = repository_path_candidates(block)
        resolved = [candidate for candidate in candidates if resolves(root, packet_dir, candidate)]
        if resolved:
            continue
        as_of_match = AS_OF_DATE_RE.search(block)
        if URL_RE.search(block) and as_of_match and is_iso_date(as_of_match.group(1)):
            continue
        if candidates:
            errors.append(
                f"{packet.relative}:{line_no}: claim cites repository path(s) that do not resolve "
                f"under the root ({', '.join(candidates)}); cite a committed path or a source URL "
                "with an as-of date"
            )
        else:
            errors.append(
                f"{packet.relative}:{line_no}: claim carries no repository path and no source URL "
                "with an as-of date; move an unsupported claim to "
                f"'{NOT_ESTABLISHED}'"
            )


def check_recommended_action(packet: Packet, errors: list[str]) -> None:
    if packet.section_bounds(RECOMMENDED_ACTION) is None:
        return
    lines = packet.section_lines(RECOMMENDED_ACTION)
    bullets = top_level_bullets(lines)
    line_no = packet.heading_line(RECOMMENDED_ACTION)
    if len(bullets) != 1:
        errors.append(
            f"{packet.relative}:{line_no}: {RECOMMENDED_ACTION} must hold exactly one action bullet, "
            f"found {len(bullets)}"
        )
    if not VERIFICATION_RE.search("\n".join(lines)):
        errors.append(
            f"{packet.relative}:{line_no}: {RECOMMENDED_ACTION} needs a non-empty 'Verification:' line "
            "stating how a human checks the result without agent privileges"
        )


def check_decision_owner_named(packet: Packet, errors: list[str]) -> None:
    if packet.data is None or packet.section_bounds(DECISION_SECTION) is None:
        return
    role = as_text(packet.data.get("decision_owner"))
    if not role:
        return
    text = "\n".join(packet.section_lines(DECISION_SECTION))
    if role not in text:
        errors.append(
            f"{packet.relative}:{packet.heading_line(DECISION_SECTION)}: "
            f"{DECISION_SECTION} must name the decision_owner role '{role}'"
        )


def check_provenance_covers_inputs(packet: Packet, errors: list[str]) -> None:
    if packet.data is None or packet.section_bounds(PROVENANCE_SECTION) is None:
        return
    entries = packet.data.get("inputs")
    if not isinstance(entries, list):
        return
    text = "\n".join(packet.section_lines(PROVENANCE_SECTION))
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        ref = as_text(entry.get("ref"))
        if ref and ref not in text:
            errors.append(
                f"{packet.relative}:{packet.heading_line(PROVENANCE_SECTION)}: "
                f"{PROVENANCE_SECTION} does not account for declared input: {ref}"
            )


def check_forbidden_assertions(packet: Packet, errors: list[str]) -> None:
    masked_body = "\n".join(packet.masked_lines)
    for pattern, message in FORBIDDEN_ASSERTIONS:
        for match in pattern.finditer(masked_body):
            if is_negated(masked_body, match.start()):
                continue
            line_no = packet.body_offset + masked_body.count("\n", 0, match.start()) + 1
            errors.append(f"{packet.relative}:{line_no}: {message}: {compact(match.group(0))!r}")


def validate_packet(path: Path, root: Path, registry_ids: set[str] | None, seen_ids: dict[str, str]) -> list[str]:
    try:
        relative = path.resolve().relative_to(root).as_posix()
    except ValueError:
        relative = path.as_posix()
    if not path.is_file():
        return [f"{relative}: packet file not found"]
    text = path.read_text(encoding="utf-8", errors="replace")
    packet = Packet(relative, text)
    errors: list[str] = [f"{relative}:{line}: {message}" for line, message in packet.parse_errors]
    if packet.data is not None:
        check_front_matter(packet, registry_ids, seen_ids, errors)
    check_sections(packet, errors)
    check_evidence_claims(packet, root, errors)
    check_recommended_action(packet, errors)
    check_decision_owner_named(packet, errors)
    check_provenance_covers_inputs(packet, errors)
    check_forbidden_assertions(packet, errors)
    return errors


def validate_paths(paths: list[Path], root: Path) -> tuple[list[str], list[str]]:
    notes: list[str] = []
    registry_ids = load_registry_ids(root, notes)
    seen_ids: dict[str, str] = {}
    errors: list[str] = []
    for path in paths:
        errors.extend(validate_packet(path, root, registry_ids, seen_ids))
    return errors, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("packets", nargs="+", help="one or more packet markdown files")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="repository root the packets cite")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Root directory not found: {root}", file=sys.stderr)
        return 2
    paths = [Path(item) for item in args.packets]
    errors, notes = validate_paths(paths, root)
    for note in notes:
        print(note)
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Checked {len(paths)} packet(s): {len(errors)} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
