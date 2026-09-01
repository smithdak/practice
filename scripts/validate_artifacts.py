#!/usr/bin/env python3
"""Deterministic offline schema validator for Practice artifact markdown files.

Validates Practice, Guide, Lab, and Story artifacts against the schemas in
``docs/schemas/`` using only the Python standard library.

Checks applied to every artifact with front matter:

- front matter parses as the schema's YAML-ish subset (a ``---`` block that
  starts the file) with actionable ``path:line:`` errors;
- required fields are present and non-empty;
- enum fields use only the controlled vocabulary values from the schemas;
- ``version`` fields match ``MAJOR.MINOR.PATCH``;
- ``created``/``updated``/``last_verified``/``deprecated_on`` are ISO dates
  and ``updated`` does not precede ``created``;
- ``license`` is a known value (``CC-BY-4.0`` or ``Apache-2.0``);
- ``artifact_type`` matches the directory that owns the file;
- maturity/status and evidence pairings hold (for example a ``tested``
  Practice needs ``evidence_quality: single-run`` or ``repeated``, a linked
  trial or evidence record in the body, and the mature content headings);
- schema-defined headings are present, in canonical order where the schema
  requires an order (Guides and Labs);
- conditional fields appear when required (``last_verified`` for verified
  Practices and published Guides, ``deprecated_on``/``deprecation_reason``
  for deprecated artifacts).

Discovery rules, tuned so the validator only claims files the schemas own:

- ``practices/``, ``labs/``, ``stories/``: every ``*.md`` other than a bare
  ``README.md`` index must be an artifact of that directory's type and must
  begin with front matter;
- ``guides/``: ``NN-*.md`` files are Guide modules. Modules are not full
  Guide artifacts, so front matter is optional; when present,
  ``artifact_type`` (if set) must be ``guide`` and any present controlled
  fields are validated. Any other ``guides/`` file that carries front matter
  is validated as a full Guide; front-matter-less index documents such as
  ``CURRICULUM.md`` are skipped.

Exit codes: 0 = all artifacts valid, 1 = at least one validation error,
2 = usage error.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_DIRS = {".git", ".worktrees", "__pycache__"}
ARTIFACT_DIRS = {"practices": "practice", "labs": "lab", "stories": "story"}
GUIDE_DIR = "guides"
GUIDE_MODULE_RE = re.compile(r"^\d{2}-")
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
H1_RE = re.compile(r"^#\s+\S")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TRIAL_REF_RE = re.compile(r"(?<!\w)(?:labs|evidence)/[\w./-]+")

ROLE_VOCABULARY = frozenset(
    {
        "individual-practitioner",
        "engineer",
        "architect",
        "builder",
        "operator",
        "founder",
        "services-leader",
        "internal-ai-champion",
        "transformation-lead",
        "consultant",
        "agency-implementer",
        "executive",
    }
)
CAPABILITIES = frozenset({"learn", "use", "automate", "build", "transform"})
EVIDENCE_LEVELS = frozenset({"none", "single-run", "repeated", "independently-reproduced"})
KNOWN_LICENSES = frozenset({"CC-BY-4.0", "Apache-2.0"})
MATURITIES = frozenset({"proposed", "tested", "verified", "deprecated"})
GUIDE_STATUSES = frozenset({"draft", "published", "deprecated"})
LAB_STATUSES = frozenset({"proposed", "running", "completed", "deprecated"})
LAB_RESULT_STATUSES = frozenset({"not-run", "partial", "complete", "invalidated"})
STORY_STATUSES = frozenset({"draft", "review", "published", "withdrawn"})
STORY_ORGANIZATIONS = frozenset({"public", "anonymized", "withheld"})

MATURITY_EVIDENCE = {
    "proposed": frozenset({"none"}),
    "tested": frozenset({"single-run", "repeated"}),
    "verified": frozenset({"independently-reproduced"}),
    "deprecated": EVIDENCE_LEVELS,
}

REQUIRED_FIELDS = {
    "practice": (
        "artifact_type", "title", "summary", "maturity", "capability",
        "roles", "version", "license", "created", "updated", "evidence_quality",
    ),
    "guide": (
        "artifact_type", "title", "summary", "status", "capability",
        "audience", "version", "license", "created", "updated",
    ),
    "lab": (
        "artifact_type", "title", "summary", "status", "primary_capability",
        "roles", "task_set_version", "run_count", "result_status", "last_run",
        "version", "license", "created", "updated",
    ),
    "story": (
        "artifact_type", "title", "status", "organization", "evidence_quality",
        "version", "license", "created", "updated",
    ),
}

ENUM_FIELDS = {
    "practice": {"maturity": MATURITIES, "capability": CAPABILITIES},
    "guide": {"status": GUIDE_STATUSES, "capability": CAPABILITIES},
    "lab": {
        "status": LAB_STATUSES,
        "result_status": LAB_RESULT_STATUSES,
        "primary_capability": CAPABILITIES,
    },
    "story": {"status": STORY_STATUSES, "organization": STORY_ORGANIZATIONS},
}

PRACTICE_CORE_HEADINGS = (
    "Outcome", "Problem and scope", "Use when", "Inputs", "Method", "Evaluation", "Changelog",
)
PRACTICE_MATURE_HEADINGS = ("Implementation", "Failure modes", "Evidence")
GUIDE_HEADINGS = (
    "Intended Practitioner", "Outcomes", "Prerequisites", "Path", "Modules",
    "Capstone", "Evaluation", "Maintainers", "Changelog",
)
LAB_HEADINGS = (
    "Question", "Hypothesis", "Variables", "Fixed conditions", "Task set", "Procedure",
    "Evaluation rubric", "Cost capture", "Results", "Interpretation", "Limitations",
    "Reproduction", "Changelog",
)
STORY_SECTIONS = (
    "Summary", "Before", "Constraint", "Intervention", "Implementation", "After",
    "Result", "Lessons", "Artifacts", "Evidence record", "Anonymization and consent",
    "Changelog",
)
STORY_NONEMPTY_SECTIONS = ("Before", "After", "Result")


class FrontMatter:
    def __init__(self, data, field_lines, errors, body_start):
        self.data = data
        self.field_lines = field_lines
        self.errors = errors
        self.body_start = body_start


class Artifact:
    def __init__(self, rel: str, text: str, front: FrontMatter | None):
        self.rel = rel
        self.front = front
        self.data = front.data if front else None
        lines = text.split("\n")
        body_offset = (front.body_start - 1) if front else 0
        self.body_lines = lines[body_offset:]
        masked = FENCED_CODE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), "\n".join(self.body_lines))
        self.masked_lines = masked.split("\n")
        self.heading_lines = [
            (body_offset + i + 1, match.group(2).strip())
            for i, line in enumerate(self.masked_lines)
            if (match := HEADING_RE.match(line)) and match.group(1) == "##"
        ]
        self.masked_body = masked

    def line_of(self, field: str) -> int:
        if self.front and field in self.front.field_lines:
            return self.front.field_lines[field]
        return self.front.body_start if self.front else 1

    def headings(self, name: str) -> list[int]:
        return [lineno for lineno, heading in self.heading_lines if heading == name]

    def section_is_empty(self, name: str) -> bool:
        starts = self.headings(name)
        if not starts:
            return True
        start = starts[0]
        body_offset = self.front.body_start - 1 if self.front else 0
        end = next(
            (lineno for lineno, _ in self.heading_lines if lineno > start),
            body_offset + len(self.masked_lines) + 1,
        )
        content = [
            line
            for offset, line in enumerate(self.masked_lines)
            if start < body_offset + offset + 1 < end and line.strip()
        ]
        return not content


def parse_scalar(raw: str):
    text = raw.strip()
    if text in ("", "null", "~", "None"):
        return None
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item) for item in _split_flow_items(inner)]
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        return text[1:-1]
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if text in ("true", "false"):
        return text == "true"
    return text


def _split_flow_items(raw: str) -> list[str]:
    items: list[str] = []
    buffer = ""
    quote: str | None = None
    for char in raw:
        if quote:
            buffer += char
            if char == quote:
                quote = None
        elif char in {'"', "'"}:
            quote = char
            buffer += char
        elif char == ",":
            items.append(buffer)
            buffer = ""
        else:
            buffer += char
    if buffer.strip():
        items.append(buffer)
    return items


def parse_front_matter(text: str) -> FrontMatter | None:
    lines = text.split("\n")
    start = 0
    while start < len(lines) and lines[start].strip() == "":
        start += 1
    if start >= len(lines) or lines[start].strip() != "---":
        return None
    data: dict = {}
    field_lines: dict[str, int] = {}
    errors: list[tuple[int, str]] = []
    current_key: str | None = None
    closed = False
    for index in range(start + 1, len(lines)):
        raw = lines[index]
        stripped = raw.strip()
        lineno = index + 1
        if stripped == "---":
            body_start = lineno + 1
            closed = True
            break
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_key is not None:
            existing = data.get(current_key)
            if not isinstance(existing, list):
                existing = []
            existing.append(parse_scalar(stripped[2:]))
            data[current_key] = existing
            continue
        match = re.match(r"^([A-Za-z_][\w-]*)\s*:(.*)$", raw.rstrip())
        if not match:
            errors.append((lineno, f"unparsable front matter line: {stripped!r}"))
            continue
        key = match.group(1)
        current_key = key
        field_lines.setdefault(key, lineno)
        data[key] = parse_scalar(match.group(2))
    if not closed:
        return FrontMatter(None, {}, [(start + 1, "front matter is never closed with a second '---' line")], start + 2)
    return FrontMatter(data, field_lines, errors, body_start)


def is_iso_date(value) -> bool:
    return isinstance(value, str) and bool(DATE_RE.match(value)) and _parse_date(value) is not None


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def add(errors: list[tuple[int, str]], art: Artifact, field: str, message: str) -> None:
    errors.append((art.rel, art.line_of(field), message))


def check_required(art: Artifact, kind: str, errors: list[tuple[int, str]], skip: frozenset[str] = frozenset()) -> None:
    for name in REQUIRED_FIELDS[kind]:
        if name in skip:
            continue
        if art.data.get(name) in (None, "", []):
            add(errors, art, name, f"required front matter field '{name}' is missing or empty")


def check_enums(art: Artifact, kind: str, errors: list[tuple[int, str]]) -> None:
    for name, allowed in ENUM_FIELDS[kind].items():
        value = art.data.get(name)
        if value is None:
            continue
        if value not in allowed:
            add(
                errors,
                art,
                name,
                f"'{name}' value {value!r} is not one of: {', '.join(sorted(allowed))}",
            )


def check_version(art: Artifact, field: str, errors: list[tuple[int, str]]) -> None:
    value = art.data.get(field)
    if value is None:
        return
    if not isinstance(value, str) or not SEMVER_RE.match(value):
        add(errors, art, field, f"'{field}' must be semantic version MAJOR.MINOR.PATCH, found {value!r}")


def check_license(art: Artifact, errors: list[tuple[int, str]]) -> None:
    value = art.data.get("license")
    if value is None:
        return
    if value not in KNOWN_LICENSES:
        add(
            errors,
            art,
            "license",
            f"'license' value {value!r} is not a known license: {', '.join(sorted(KNOWN_LICENSES))}",
        )


def check_dates(art: Artifact, errors: list[tuple[int, str]]) -> None:
    created = art.data.get("created")
    updated = art.data.get("updated")
    for field in ("created", "updated", "last_verified", "deprecated_on"):
        value = art.data.get(field)
        if value is not None and not is_iso_date(value):
            add(errors, art, field, f"'{field}' must be an ISO date YYYY-MM-DD, found {value!r}")
    if is_iso_date(created) and is_iso_date(updated) and _parse_date(updated) < _parse_date(created):
        add(errors, art, "updated", f"'updated' ({updated}) must not precede 'created' ({created})")


def check_role_list(art: Artifact, field: str, errors: list[tuple[int, str]], nonempty: bool) -> None:
    value = art.data.get(field)
    if value is None:
        return
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        add(errors, art, field, f"'{field}' must be a list of values")
        return
    if nonempty and not value:
        add(errors, art, field, f"'{field}' must be a non-empty list")
        return
    duplicates = sorted({item for item in value if value.count(item) > 1})
    if duplicates:
        add(errors, art, field, f"'{field}' contains duplicate values: {', '.join(duplicates)}")
    unknown = sorted(set(value) - ROLE_VOCABULARY)
    if unknown:
        add(errors, art, field, f"'{field}' contains uncontrolled values: {', '.join(unknown)}")


def check_secondary(
    art: Artifact,
    field: str,
    allowed: frozenset,
    primary: str,
    errors: list[tuple[int, str]],
) -> None:
    value = art.data.get(field)
    if value is None:
        return
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        add(errors, art, field, f"'{field}' must be a list of values")
        return
    duplicates = sorted({item for item in value if value.count(item) > 1})
    if duplicates:
        add(errors, art, field, f"'{field}' contains duplicate values: {', '.join(duplicates)}")
    unknown = sorted(set(value) - allowed)
    if unknown:
        add(errors, art, field, f"'{field}' contains uncontrolled values: {', '.join(unknown)}")
    primary_set = {primary} if isinstance(primary, str) else set(primary)
    overlap = sorted(set(value) & primary_set)
    if overlap:
        add(errors, art, field, f"'{field}' must not repeat the primary value: {', '.join(overlap)}")


def check_conditional_dates(art: Artifact, errors: list[tuple[int, str]]) -> None:
    reason = art.data.get("deprecation_reason")
    if reason is not None and (not isinstance(reason, str) or not reason.strip()):
        add(errors, art, "deprecation_reason", "'deprecation_reason' must be a non-empty plain-language reason")


def check_heading_presence(art: Artifact, names: tuple[str, ...], errors: list[tuple[int, str]], context: str) -> None:
    for name in names:
        if not art.headings(name):
            add(errors, art, "title", f"{context} requires a '## {name}' section")


def check_heading_order(art: Artifact, names: tuple[str, ...], errors: list[tuple[int, str]]) -> None:
    positions = {}
    for lineno, heading in art.heading_lines:
        positions.setdefault(heading, lineno)
    for name in names:
        if name not in positions:
            add(errors, art, "title", f"required section '## {name}' is missing")
    for earlier, later in zip(names, names[1:]):
        if earlier in positions and later in positions and positions[later] < positions[earlier]:
            add(
                errors,
                art,
                "title",
                f"section '## {later}' appears before '## {earlier}'; canonical order must be followed",
            )


def validate_practice(art: Artifact, errors: list[tuple[int, str]]) -> None:
    check_required(art, "practice", errors)
    check_enums(art, "practice", errors)
    check_version(art, "version", errors)
    check_license(art, errors)
    check_dates(art, errors)
    check_role_list(art, "roles", errors, nonempty=True)
    check_secondary(art, "secondary_capabilities", CAPABILITIES, art.data.get("capability"), errors)
    check_secondary(art, "secondary_roles", ROLE_VOCABULARY, art.data.get("roles") or [], errors)
    check_conditional_dates(art, errors)

    maturity = art.data.get("maturity")
    evidence = art.data.get("evidence_quality")
    if maturity in MATURITY_EVIDENCE and evidence is not None and evidence not in MATURITY_EVIDENCE[maturity]:
        expected = ", ".join(sorted(MATURITY_EVIDENCE[maturity]))
        add(
            errors,
            art,
            "evidence_quality",
            f"maturity '{maturity}' requires evidence_quality {expected}, found {evidence!r}",
        )

    if maturity in ("tested", "verified"):
        check_heading_presence(art, PRACTICE_MATURE_HEADINGS, errors, f"maturity '{maturity}'")
        if not TRIAL_REF_RE.search(art.masked_body):
            add(
                errors,
                art,
                "maturity",
                f"maturity '{maturity}' requires a linked trial or evidence record in the body "
                "(a Lab reference such as labs/NNN-name.md or an evidence/ path)",
            )

    check_heading_presence(art, PRACTICE_CORE_HEADINGS, errors, "a Practice")

    if maturity == "verified" and art.data.get("last_verified") is None:
        add(errors, art, "last_verified", "maturity 'verified' requires 'last_verified'")
    if maturity == "deprecated":
        if art.data.get("deprecated_on") is None:
            add(errors, art, "deprecated_on", "maturity 'deprecated' requires 'deprecated_on'")
        if art.data.get("deprecation_reason") in (None, ""):
            add(errors, art, "deprecation_reason", "maturity 'deprecated' requires 'deprecation_reason'")
        check_heading_presence(art, ("Deprecation notice",), errors, "maturity 'deprecated'")


def validate_guide(art: Artifact, errors: list[tuple[int, str]]) -> None:
    check_required(art, "guide", errors)
    check_enums(art, "guide", errors)
    check_version(art, "version", errors)
    check_license(art, errors)
    check_dates(art, errors)
    check_role_list(art, "audience", errors, nonempty=True)
    check_secondary(art, "secondary_capabilities", CAPABILITIES, art.data.get("capability"), errors)
    check_conditional_dates(art, errors)
    check_heading_order(art, GUIDE_HEADINGS, errors)

    status = art.data.get("status")
    if status == "published" and art.data.get("last_verified") is None:
        add(errors, art, "last_verified", "status 'published' requires 'last_verified'")
    if status == "deprecated":
        if art.data.get("deprecated_on") is None:
            add(errors, art, "deprecated_on", "status 'deprecated' requires 'deprecated_on'")
        if art.data.get("deprecation_reason") in (None, ""):
            add(errors, art, "deprecation_reason", "status 'deprecated' requires 'deprecation_reason'")
        check_heading_presence(art, ("Deprecation notice",), errors, "status 'deprecated'")


def validate_lab(art: Artifact, errors: list[tuple[int, str]]) -> None:
    check_required(art, "lab", errors, skip=frozenset({"last_run"}))
    check_enums(art, "lab", errors)
    check_version(art, "version", errors)
    check_version(art, "task_set_version", errors)
    check_license(art, errors)
    check_dates(art, errors)
    check_role_list(art, "roles", errors, nonempty=True)
    check_secondary(art, "secondary_capabilities", CAPABILITIES, art.data.get("primary_capability"), errors)
    check_secondary(art, "secondary_roles", ROLE_VOCABULARY, art.data.get("roles") or [], errors)
    check_conditional_dates(art, errors)

    run_count = art.data.get("run_count")
    if run_count is not None and (isinstance(run_count, bool) or not isinstance(run_count, int) or run_count < 0):
        add(errors, art, "run_count", f"'run_count' must be a non-negative integer, found {run_count!r}")

    last_run = art.data.get("last_run")
    result_status = art.data.get("result_status")
    if last_run is not None and not is_iso_date(last_run):
        add(errors, art, "last_run", f"'last_run' must be null or an ISO date YYYY-MM-DD, found {last_run!r}")
    if result_status == "not-run" and last_run is not None:
        add(errors, art, "last_run", "'last_run' must be null when result_status is 'not-run'")
    if result_status in ("partial", "complete", "invalidated") and last_run is None:
        add(errors, art, "last_run", f"'last_run' must be an ISO date when result_status is '{result_status}'")

    check_heading_order(art, LAB_HEADINGS, errors)

    if art.data.get("status") == "deprecated":
        if art.data.get("deprecated_on") is None:
            add(errors, art, "deprecated_on", "status 'deprecated' requires 'deprecated_on'")
        if art.data.get("deprecation_reason") in (None, ""):
            add(errors, art, "deprecation_reason", "status 'deprecated' requires 'deprecation_reason'")


def validate_story(art: Artifact, errors: list[tuple[int, str]]) -> None:
    check_required(art, "story", errors)
    check_enums(art, "story", errors)
    check_version(art, "version", errors)
    check_license(art, errors)
    check_dates(art, errors)
    check_conditional_dates(art, errors)

    if art.data.get("status") == "published" and art.data.get("evidence_quality") == "none":
        add(
            errors,
            art,
            "evidence_quality",
            "status 'published' requires evidence_quality 'single-run', 'repeated', or 'independently-reproduced'",
        )

    check_heading_presence(art, STORY_SECTIONS, errors, "a Story")
    for name in STORY_NONEMPTY_SECTIONS:
        if art.headings(name) and art.section_is_empty(name):
            add(errors, art, "title", f"section '## {name}' must not be empty")


def validate_guide_module(art: Artifact, errors: list[tuple[int, str]]) -> None:
    if not any(H1_RE.match(line) for line in art.masked_lines):
        add(errors, art, "title", "guide module must begin with a '# ' title heading")
    if art.data is None:
        return
    declared = art.data.get("artifact_type")
    if declared is not None and declared != "guide":
        add(
            errors,
            art,
            "artifact_type",
            f"guide module 'artifact_type' must be 'guide' when present, found {declared!r}",
        )
    for name, allowed in (
        ("maturity", MATURITIES),
        ("status", GUIDE_STATUSES),
        ("capability", CAPABILITIES),
        ("evidence_quality", EVIDENCE_LEVELS),
    ):
        value = art.data.get(name)
        if value is not None and value not in allowed:
            add(errors, art, name, f"'{name}' value {value!r} is not one of: {', '.join(sorted(allowed))}")
    for name in ("version", "task_set_version"):
        check_version(art, name, errors)
    check_license(art, errors)
    check_dates(art, errors)
    for name in ("roles", "audience"):
        check_role_list(art, name, errors, nonempty=True)
    check_secondary(art, "secondary_capabilities", CAPABILITIES, art.data.get("capability"), errors)
    check_secondary(art, "secondary_roles", ROLE_VOCABULARY, art.data.get("roles") or [], errors)


VALIDATORS = {
    "practice": validate_practice,
    "guide": validate_guide,
    "lab": validate_lab,
    "story": validate_story,
}


def collect_artifacts(root: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for dirname, kind in sorted(ARTIFACT_DIRS.items()):
        base = root / dirname
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
                continue
            entries.append((path.relative_to(root).as_posix(), kind))
    guide_base = root / GUIDE_DIR
    if guide_base.is_dir():
        for path in sorted(guide_base.rglob("*.md")):
            if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
                continue
            kind = "guide_module" if GUIDE_MODULE_RE.match(path.name) else "guide"
            entries.append((path.relative_to(root).as_posix(), kind))
    return entries


def validate_root(root: Path) -> tuple[list[str], Counter]:
    errors: list[tuple[str, int, str]] = []
    counts: Counter = Counter()
    for rel, kind in collect_artifacts(root):
        path = root / rel
        text = path.read_text(encoding="utf-8", errors="replace")
        front = parse_front_matter(text)
        art = Artifact(rel, text, front)
        if front is None:
            if kind == "guide_module":
                counts["guide module"] += 1
                validate_guide_module(art, errors)
            elif kind == "guide":
                continue
            elif path.name == "README.md":
                continue
            else:
                errors.append((rel, 1, f"{kind} artifact must begin with '---' front matter"))
            continue
        for lineno, message in front.errors:
            errors.append((rel, lineno, message))
        if front.data is None:
            continue
        if kind == "guide_module":
            counts["guide module"] += 1
            validate_guide_module(art, errors)
            continue
        declared = art.data.get("artifact_type")
        if declared is None:
            add(errors, art, "artifact_type", "required front matter field 'artifact_type' is missing or empty")
            continue
        if declared != kind:
            add(
                errors,
                art,
                "artifact_type",
                f"artifact_type '{declared}' does not match expected '{kind}' for this directory",
            )
            continue
        counts[kind] += 1
        VALIDATORS[kind](art, errors)
    formatted = [f"{rel}:{lineno}: {message}" for rel, lineno, message in sorted(errors)]
    return formatted, counts


def summarize(counts: Counter) -> str:
    labels = {
        "practice": ("practice", "practices"),
        "guide": ("guide", "guides"),
        "lab": ("lab", "labs"),
        "story": ("story", "stories"),
        "guide module": ("guide module", "guide modules"),
    }
    if not counts:
        return "no artifacts found"
    return ", ".join(
        f"{counts[key]} {labels[key][0] if counts[key] == 1 else labels[key][1]}"
        for key in sorted(counts)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Practice artifact schemas and invariants.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="repository root to validate")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    errors, counts = validate_root(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"Artifact validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Artifact validation passed ({summarize(counts)}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
