#!/usr/bin/env python3
"""Deterministic offline collector for the repository-observable part of ops/METRICS.md.

``ops/METRICS.md`` is a measurement contract, not an analytics plan. It says to
count only what a human can point to in a public Git change, a voluntary
contribution record, or a sanitized Buzz link, and to report every count with
its denominator and evidence coverage. This collector supplies the first of
those three sources and nothing else: it reads committed files under ``--root``
and reports what they state.

Collected from committed files:

- artifact inventory by type, declared state, capability stage, and declared
  evidence-quality label (labels are read, never written);
- evidence coverage: whether each artifact states the evidence elements
  ``ops/METRICS.md`` names (inputs, steps, output, evaluation, limitations,
  failure modes, and an inspectable record), mapped onto the schema headings
  each artifact type actually defines;
- accepted contribution records already written into a committed artifact
  changelog;
- owner gates and operating holds recorded in ``release/OWNER_REVIEW.md``,
  reported verbatim;
- link health: internal markdown link targets that resolve.

Not collected, and printed as such rather than as a zero: Activation, Artifact
reuse, Implementation, Response quality, Retention, Maintainer health, and
proposed (as opposed to accepted) contributions. Each needs the human
measurement route in ``ops/METRICS.md`` under "Minimal manual measurement at
launch". A missing measurement is a prompt to improve instrumentation, not a
zero, so the report never prints ``0`` for anything it did not measure.

Honoring "Data not to collect" in code, not only in prose. This collector:

- makes no network calls of any kind and opens no socket;
- reads only files under the scanned root, and never enters ``.git``, so commit
  authorship, names, and email addresses are unreachable to it;
- has no data structure for a person: no member identity, alias, join, view,
  read receipt, session, reaction, follower count, or behavioral profile is
  parsed, stored, or emitted;
- never asserts that an owner gate or operating hold is cleared, and never
  changes a ``maturity`` or ``evidence_quality`` field.

A report produced here is evidence of repository state at one commit. It is not
evidence of community health.

Front matter is parsed by reusing ``scripts/validate_artifacts.py`` and link
targets by reusing ``scripts/check_links.py``, so this script does not carry a
second parser that could drift from the validators.

Exit codes: 0 = report produced, 2 = usage error.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
DEFAULT_ROOT = SCRIPTS_DIR.parent
COLLECTOR = "scripts/collect_metrics.py"
CONTRACT = "ops/METRICS.md"
OWNER_REVIEW_REL = "release/OWNER_REVIEW.md"
OWNER_GATES_REL = "docs/OWNER_GATES.md"

NOT_COLLECTED_LABEL = "not collected"


def _load_sibling(module_name: str, filename: str):
    """Import a sibling script by path so this collector reuses its parsers."""
    path = SCRIPTS_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - packaging failure
        raise SystemExit(f"{COLLECTOR}: cannot load required helper {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


artifacts = _load_sibling("practice_collect_metrics_artifacts", "validate_artifacts.py")
links = _load_sibling("practice_collect_metrics_links", "check_links.py")

CHANGELOG_ENTRY_RE = re.compile(r"^\s*[-*]\s+\**\s*(\d{4}-\d{2}-\d{2})\b")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
NOT_DECLARED = "not declared"

# Which schema headings carry each evidence element named in ops/METRICS.md.
# An element counts as stated when at least one mapped heading exists and its
# section is not empty. Types differ because their schemas differ; the mapping
# is documented in ops/metrics/README.md.
EVIDENCE_ELEMENTS: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "practice": (
        ("inputs", ("Inputs",)),
        ("steps", ("Method",)),
        ("output", ("Outcome",)),
        ("evaluation", ("Evaluation",)),
        ("limitations", ("Problem and scope", "Use when")),
        ("failure modes", ("Failure modes",)),
        ("inspectable record", ("Evidence",)),
    ),
    "lab": (
        ("inputs", ("Task set", "Fixed conditions")),
        ("steps", ("Procedure",)),
        ("output", ("Results",)),
        ("evaluation", ("Evaluation rubric",)),
        ("limitations", ("Limitations",)),
        ("inspectable record", ("Reproduction",)),
    ),
    "story": (
        ("inputs", ("Before",)),
        ("steps", ("Intervention", "Implementation")),
        ("output", ("After",)),
        ("evaluation", ("Result",)),
        ("limitations", ("Lessons",)),
        ("inspectable record", ("Evidence record",)),
    ),
    "guide": (
        ("inputs", ("Prerequisites",)),
        ("steps", ("Path",)),
        ("output", ("Outcomes",)),
        ("evaluation", ("Evaluation",)),
    ),
}

ARTIFACT_KINDS = ("guide", "lab", "practice", "story")

# Metrics that ops/METRICS.md defines but committed files cannot supply.
# Every one is reported as unmeasured; none is reported as zero.
NOT_COLLECTED: tuple[tuple[str, str, str, str], ...] = (
    (
        "Activation",
        "Leading",
        "A first-value action by a new Practitioner is observed in a sanitized Buzz "
        "link or a voluntary record, not in a committed file. A join, read, or "
        "reaction does not activate, and this collector reads none of them.",
        "Record one row per observed activation, with entry source, action, date, and "
        "link or alias, in the human-maintained access-controlled ledger "
        "(steps 1-2).",
    ),
    (
        "Contribution (proposed)",
        "Leading",
        "Proposed contributions live in open issues, drafts, and pull requests, which "
        "are not committed files. Only accepted contributions already written into a "
        "committed artifact changelog are counted above.",
        "Keep proposed and accepted contributions in separate ledger rows and count "
        "accepted ones only after the required evidence is present (steps 1-3).",
    ),
    (
        "Artifact reuse",
        "Lagging",
        "Reuse requires a link or voluntary note from someone other than the author "
        "stating what was reused and what changed. A page view is not reuse, and no "
        "committed file records either.",
        "Add a voluntary reuse field, inspect the supplied links, and record one row "
        "per reuse report without inventing usage (steps 1-3).",
    ),
    (
        "Implementation",
        "Lagging",
        "An implementation report states the scope, the human review point, and an "
        "owner-provided result. It is supplied by a Practitioner, not derivable from "
        "repository contents.",
        "Record one row per implementation report, marked self-reported, and do not "
        "imply independent verification (steps 1-2).",
    ),
    (
        "Response quality",
        "Leading (with lagging review)",
        "Response quality needs a reviewed sample of actual responses scored "
        "pass or needs-revision with a reason. The responses are not committed files.",
        "Review the response sample consistently, mark the checklist result and the "
        "reason for revision, and use a fixed sample or review all responses during a "
        "small launch period (step 3).",
    ),
    (
        "Retention",
        "Lagging",
        "Retention compares a Practitioner's useful actions across two review periods. "
        "Login or presence may not be used as a proxy, and this collector holds no "
        "per-person record to compare.",
        "Record the returning action and its period in the ledger, and note any change "
        "in method so later periods stay comparable (steps 1 and 5).",
    ),
    (
        "Maintainer health",
        "Leading and lagging",
        "Maintainer health is a once-per-period maintainer check-in: open review queue, "
        "oldest pending item, unresolved safety or licensing issues, and a load status. "
        "The owner gates and operating holds counted above are a repository record, not "
        "that check-in.",
        "Have maintainers record the check-in for the period and whether follow-ups "
        "were completed, without measuring people by speed (step 1).",
    ),
)

NEVER_READ = (
    "member identities, aliases, and commit authorship (the collector never enters .git)",
    "joins, reads, views, session duration, and message-read receipts",
    "reactions, follower counts, and any ranking or leaderboard input",
    "message content from Buzz or any other hosted surface",
    "any network resource: the collector runs offline and reads only files under the scanned root",
)


@dataclass
class ScannedArtifact:
    rel: str
    kind: str
    state: str
    stage: str
    evidence_quality: str
    elements: dict[str, bool]
    changelog_entries: int
    has_changelog: bool


@dataclass
class ArtifactScan:
    scored: list[ScannedArtifact] = field(default_factory=list)
    unreadable: list[str] = field(default_factory=list)
    guide_modules: int = 0
    index_documents: int = 0


@dataclass
class TableScan:
    open_rows: int = 0
    readable_rows: int = 0
    total_rows: int = 0
    other_rows: list[tuple[str, str]] = field(default_factory=list)
    available: bool = False
    reason: str = ""


def section_lines(art, name: str) -> list[str]:
    """Return the code-masked body lines under the first ``## name`` heading."""
    starts = art.headings(name)
    if not starts:
        return []
    start = starts[0]
    body_offset = art.front.body_start - 1 if art.front else 0
    end = next(
        (lineno for lineno, _ in art.heading_lines if lineno > start),
        body_offset + len(art.masked_lines) + 1,
    )
    return [
        line
        for offset, line in enumerate(art.masked_lines)
        if start < body_offset + offset + 1 < end
    ]


def _label(value) -> str:
    if value is None or value == "" or value == []:
        return NOT_DECLARED
    return str(value)


def scan_artifacts(root: Path) -> ArtifactScan:
    """Read every artifact file the schemas own and record only its stated facts."""
    scan = ArtifactScan()
    for rel, kind in artifacts.collect_artifacts(root):
        path = root / rel
        text = path.read_text(encoding="utf-8", errors="replace")
        front = artifacts.parse_front_matter(text)
        if kind == "guide_module":
            scan.guide_modules += 1
            continue
        if front is None or front.data is None:
            if kind == "guide" or Path(rel).name == "README.md":
                scan.index_documents += 1
            else:
                scan.unreadable.append(rel)
            continue
        art = artifacts.Artifact(rel, text, front)
        if art.data.get("artifact_type") != kind:
            scan.unreadable.append(rel)
            continue
        state_field = "maturity" if kind == "practice" else "status"
        stage_field = "primary_capability" if kind == "lab" else "capability"
        elements = {
            name: any(
                art.headings(heading) and not art.section_is_empty(heading)
                for heading in headings
            )
            for name, headings in EVIDENCE_ELEMENTS[kind]
        }
        changelog_lines = section_lines(art, "Changelog")
        scan.scored.append(
            ScannedArtifact(
                rel=rel,
                kind=kind,
                state=_label(art.data.get(state_field)),
                stage=_label(art.data.get(stage_field)),
                evidence_quality=_label(art.data.get("evidence_quality")),
                elements=elements,
                changelog_entries=sum(
                    1 for line in changelog_lines if CHANGELOG_ENTRY_RE.match(line)
                ),
                has_changelog=bool(art.headings("Changelog"))
                and not art.section_is_empty("Changelog"),
            )
        )
    scan.scored.sort(key=lambda item: item.rel)
    scan.unreadable.sort()
    return scan


def _table_rows(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if TABLE_SEPARATOR_RE.match(line):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows.append(cells)
    return rows[1:] if rows else []


def scan_status_table(text: str | None, heading_marker: str, missing_reason: str) -> TableScan:
    """Count rows recorded open in one status table, copying other statuses verbatim."""
    scan = TableScan()
    if text is None:
        scan.reason = missing_reason
        return scan
    lines = text.split("\n")
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if line.startswith("## ") and heading_marker.lower() in line.lower()
        ),
        None,
    )
    if start is None:
        scan.reason = f"no '## ...{heading_marker}...' section found in {OWNER_REVIEW_REL}"
        return scan
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    rows = _table_rows(lines[start:end])
    if not rows:
        scan.reason = f"the '{heading_marker}' section of {OWNER_REVIEW_REL} has no status table"
        return scan
    scan.available = True
    scan.total_rows = len(rows)
    for cells in rows:
        name = cells[0] if cells else ""
        status = cells[-1].strip().strip("*").strip() if len(cells) > 1 else ""
        if not status:
            continue
        scan.readable_rows += 1
        if "OPEN" in status.upper():
            scan.open_rows += 1
        else:
            scan.other_rows.append((name, status))
    scan.other_rows.sort()
    return scan


def count_table_rows(text: str | None, heading_marker: str | None = None) -> int | None:
    """Count body rows of the first markdown table in a document or section."""
    if text is None:
        return None
    lines = text.split("\n")
    if heading_marker is not None:
        start = next(
            (
                index
                for index, line in enumerate(lines)
                if line.startswith("#") and heading_marker.lower() in line.lower()
            ),
            None,
        )
        if start is None:
            return None
        lines = lines[start:]
    rows = _table_rows(lines)
    return len(rows) if rows else None


def read_optional(root: Path, rel: str) -> str | None:
    path = root / rel
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def measure_link_health(root: Path) -> dict:
    """Count internal markdown link targets that resolve, reusing check_links."""
    resolved_root = root.resolve()
    files = links.find_markdown_files(resolved_root)
    checked = 0
    resolving = 0
    unresolved: list[str] = []
    for path in files:
        relative = path.relative_to(resolved_root).as_posix()
        masked = links.mask_code(path.read_text(encoding="utf-8", errors="replace"))
        for line_no, _kind, target in links.extract_targets(masked):
            status, candidate, _target_kind = links.resolve_target(target, path, resolved_root)
            if status == links.SKIPPED:
                continue
            checked += 1
            if status == links.ESCAPED or candidate is None or not candidate.exists():
                unresolved.append(f"{relative}:{line_no}: {target.strip()}")
                continue
            resolving += 1
    unresolved.sort()
    return {
        "internal_targets_resolving": resolving,
        "internal_targets_checked": checked,
        "markdown_files_scanned": len(files),
        "unresolved_targets": unresolved,
    }


def _tally(values) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return sorted(counts.items())


def build_report(root: Path, as_of: date) -> dict:
    """Assemble the whole report as plain data so markdown and JSON agree."""
    scan = scan_artifacts(root)
    scored = scan.scored
    total = len(scored)
    parsed_denominator = total + len(scan.unreadable)

    by_type = [
        {"artifact_type": kind, "count": sum(1 for item in scored if item.kind == kind)}
        for kind in ARTIFACT_KINDS
    ]
    by_state = [
        {"artifact_type": kind, "state": state, "count": count,
         "denominator": sum(1 for item in scored if item.kind == kind)}
        for kind in ARTIFACT_KINDS
        for state, count in _tally(item.state for item in scored if item.kind == kind)
    ]
    by_stage = [
        {"capability_stage": stage, "count": count, "denominator": total}
        for stage, count in _tally(item.stage for item in scored)
    ]
    by_evidence_quality = [
        {"evidence_quality": label, "count": count, "denominator": total}
        for label, count in _tally(item.evidence_quality for item in scored)
    ]

    evidence_by_type = []
    evidence_by_element = []
    for kind in ARTIFACT_KINDS:
        members = [item for item in scored if item.kind == kind]
        if not members:
            continue
        element_names = [name for name, _ in EVIDENCE_ELEMENTS[kind]]
        elements_present = sum(
            1 for item in members for name in element_names if item.elements[name]
        )
        evidence_by_type.append(
            {
                "artifact_type": kind,
                "artifacts_stating_every_element": sum(
                    1 for item in members if all(item.elements[name] for name in element_names)
                ),
                "denominator": len(members),
                "elements_present": elements_present,
                "elements_checked": len(members) * len(element_names),
            }
        )
        for name in element_names:
            evidence_by_element.append(
                {
                    "artifact_type": kind,
                    "element": name,
                    "present": sum(1 for item in members if item.elements[name]),
                    "denominator": len(members),
                }
            )

    contribution_by_type = [
        {
            "artifact_type": kind,
            "accepted_changelog_entries": sum(
                item.changelog_entries for item in scored if item.kind == kind
            ),
            "artifacts_with_changelog": sum(
                1 for item in scored if item.kind == kind and item.has_changelog
            ),
            "denominator": sum(1 for item in scored if item.kind == kind),
        }
        for kind in ARTIFACT_KINDS
        if any(item.kind == kind for item in scored)
    ]

    owner_review = read_optional(root, OWNER_REVIEW_REL)
    missing = f"{OWNER_REVIEW_REL} is not present under the scanned root"
    gates = scan_status_table(owner_review, "Owner gates", missing)
    holds = scan_status_table(owner_review, "operating holds", missing)
    gate_notes: list[str] = []
    declared_gates = count_table_rows(read_optional(root, OWNER_GATES_REL))
    if gates.available and declared_gates is not None and declared_gates != gates.total_rows:
        gate_notes.append(
            f"{OWNER_GATES_REL} lists {declared_gates} gate row(s) but {OWNER_REVIEW_REL} "
            f"lists {gates.total_rows}. Reconcile the two documents before using this count."
        )

    link_health = measure_link_health(root)

    return {
        "as_of": as_of.isoformat(),
        "collector": COLLECTOR,
        "contract": CONTRACT,
        "collected": {
            "artifact_inventory": {
                "scored_artifacts": total,
                "evidence_coverage": (
                    f"{total} of {parsed_denominator} artifact file(s) parsed their front matter"
                ),
                "guide_modules": scan.guide_modules,
                "index_documents": scan.index_documents,
                "unreadable_front_matter": scan.unreadable,
                "by_type": by_type,
                "by_state": by_state,
                "by_capability_stage": by_stage,
                "by_declared_evidence_quality": by_evidence_quality,
            },
            "evidence_coverage": {
                "by_type": evidence_by_type,
                "by_element": evidence_by_element,
            },
            "contribution_records": {
                "accepted_changelog_entries": sum(item.changelog_entries for item in scored),
                "artifacts_with_changelog": sum(1 for item in scored if item.has_changelog),
                "denominator": total,
                "by_type": contribution_by_type,
            },
            "owner_gates_and_holds": {
                "owner_gates": _table_payload(gates),
                "operating_holds": _table_payload(holds),
                "notes": gate_notes,
            },
            "link_health": link_health,
        },
        "not_collected": [
            {
                "metric": metric,
                "metric_type": metric_type,
                "status": NOT_COLLECTED_LABEL,
                "count": None,
                "reason": reason,
                "human_route": route,
            }
            for metric, metric_type, reason, route in NOT_COLLECTED
        ],
        "never_read": list(NEVER_READ),
    }


def _table_payload(scan: TableScan) -> dict:
    if not scan.available:
        return {
            "status": NOT_COLLECTED_LABEL,
            "recorded_open": None,
            "denominator": None,
            "reason": scan.reason,
        }
    return {
        "status": "collected",
        "recorded_open": scan.open_rows,
        "denominator": scan.total_rows,
        "rows_with_a_readable_status": scan.readable_rows,
        "rows_not_recorded_open": [
            {"row": name, "recorded_status": status} for name, status in scan.other_rows
        ],
    }


def _row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    out = [_row(header), _row(["---"] * len(header))]
    out.extend(_row(cells) for cells in rows)
    return out


def render_markdown(report: dict) -> str:
    collected = report["collected"]
    inventory = collected["artifact_inventory"]
    total = inventory["scored_artifacts"]
    out: list[str] = []
    out.append("# Practice repository metrics report")
    out.append("")
    out.append(f"- As of: {report['as_of']}")
    out.append(f"- Produced by: `{report['collector']}`")
    out.append(f"- Measurement contract: `{report['contract']}`")
    out.append("- Source: committed files under the scanned repository root")
    out.append("")
    out.append(
        "This report records repository state at one commit. It is not evidence of "
        "community health, and it does not clear any owner gate or operating hold. "
        "Entries under \"Not collected here\" are unmeasured; do not read them as zero."
    )
    out.append("")

    out.append("## Collected from committed Git evidence")
    out.append("")
    out.append("### Artifact inventory")
    out.append("")
    out.append(f"- Evidence coverage: {inventory['evidence_coverage']}.")
    out.append(
        f"- Also present: {inventory['guide_modules']} guide module(s) and "
        f"{inventory['index_documents']} front-matter-less index document(s). "
        "Neither is a standalone artifact, so neither is scored below."
    )
    if inventory["unreadable_front_matter"]:
        out.append(
            f"- {len(inventory['unreadable_front_matter'])} artifact file(s) could not be "
            "read as their directory's type and are excluded from every count below: "
            + ", ".join(f"`{rel}`" for rel in inventory["unreadable_front_matter"])
            + ". Run `python3 scripts/validate_artifacts.py` for the reason."
        )
    out.append("")
    out.extend(
        _table(
            ["Artifact type", "Count", "Denominator"],
            [
                [entry["artifact_type"], str(entry["count"]), f"{total} scored artifact(s)"]
                for entry in inventory["by_type"]
            ],
        )
    )
    out.append("")
    out.append("#### By declared state")
    out.append("")
    out.append(
        "States are read verbatim from front matter (`maturity` for a Practice, "
        "`status` otherwise). This collector never changes them."
    )
    out.append("")
    if inventory["by_state"]:
        out.extend(
            _table(
                ["Artifact type", "Declared state", "Count", "Denominator"],
                [
                    [
                        entry["artifact_type"],
                        entry["state"],
                        str(entry["count"]),
                        f"{entry['denominator']} {entry['artifact_type']} artifact(s)",
                    ]
                    for entry in inventory["by_state"]
                ],
            )
        )
    else:
        out.append("No artifact declared a state.")
    out.append("")
    out.append("#### By capability stage")
    out.append("")
    if inventory["by_capability_stage"]:
        out.extend(
            _table(
                ["Capability stage", "Count", "Denominator"],
                [
                    [
                        entry["capability_stage"],
                        str(entry["count"]),
                        f"{entry['denominator']} scored artifact(s)",
                    ]
                    for entry in inventory["by_capability_stage"]
                ],
            )
        )
    else:
        out.append("No artifact declared a capability stage.")
    out.append("")
    out.append("#### By declared evidence-quality label")
    out.append("")
    if inventory["by_declared_evidence_quality"]:
        out.extend(
            _table(
                ["Declared evidence quality", "Count", "Denominator"],
                [
                    [
                        entry["evidence_quality"],
                        str(entry["count"]),
                        f"{entry['denominator']} scored artifact(s)",
                    ]
                    for entry in inventory["by_declared_evidence_quality"]
                ],
            )
        )
    else:
        out.append("No artifact declared an evidence-quality label.")
    out.append("")

    out.append("### Evidence coverage")
    out.append("")
    out.append(
        "The Evidence metric counts coverage, not positive outcomes: whether an "
        "artifact states its inputs, steps, output, evaluation, limitations, failure "
        "modes, and an inspectable record. Each element is mapped onto the schema "
        "headings its artifact type defines; the map is in `ops/metrics/README.md`. "
        "A heading that exists but is empty does not count."
    )
    out.append("")
    evidence = collected["evidence_coverage"]
    if evidence["by_type"]:
        out.extend(
            _table(
                ["Artifact type", "Artifacts stating every element", "Denominator", "Element coverage"],
                [
                    [
                        entry["artifact_type"],
                        str(entry["artifacts_stating_every_element"]),
                        f"{entry['denominator']} {entry['artifact_type']} artifact(s)",
                        f"{entry['elements_present']} of {entry['elements_checked']} elements stated",
                    ]
                    for entry in evidence["by_type"]
                ],
            )
        )
        out.append("")
        out.append("#### By element")
        out.append("")
        out.extend(
            _table(
                ["Artifact type", "Element", "Stated", "Denominator"],
                [
                    [
                        entry["artifact_type"],
                        entry["element"],
                        str(entry["present"]),
                        f"{entry['denominator']} {entry['artifact_type']} artifact(s)",
                    ]
                    for entry in evidence["by_element"]
                ],
            )
        )
    else:
        out.append("No artifact was in scope for evidence coverage.")
    out.append("")

    out.append("### Accepted contribution records")
    out.append("")
    contributions = collected["contribution_records"]
    out.append(
        "Counted here: accepted contributions already written into a committed "
        "artifact changelog, which is the only contribution evidence a committed file "
        "can supply. Proposed contributions are listed under \"Not collected here\"."
    )
    out.append("")
    out.extend(
        _table(
            ["Measure", "Count", "Denominator", "Evidence coverage"],
            [
                [
                    "Dated changelog entries",
                    str(contributions["accepted_changelog_entries"]),
                    f"{contributions['denominator']} scored artifact(s)",
                    f"{contributions['artifacts_with_changelog']} of "
                    f"{contributions['denominator']} artifact(s) carry a non-empty changelog",
                ]
            ],
        )
    )
    if contributions["by_type"]:
        out.append("")
        out.extend(
            _table(
                ["Artifact type", "Dated changelog entries", "Denominator", "Evidence coverage"],
                [
                    [
                        entry["artifact_type"],
                        str(entry["accepted_changelog_entries"]),
                        f"{entry['denominator']} {entry['artifact_type']} artifact(s)",
                        f"{entry['artifacts_with_changelog']} of {entry['denominator']} "
                        "carry a non-empty changelog",
                    ]
                    for entry in contributions["by_type"]
                ],
            )
        )
    out.append("")

    out.append("### Owner gates and operating holds")
    out.append("")
    out.append(
        f"Statuses are copied verbatim from `{OWNER_REVIEW_REL}`. This collector never "
        "asserts that a gate or hold is cleared; a row that is not recorded open is a "
        "repository record only, and clearing one is a human decision recorded by a human."
    )
    out.append("")
    gate_rows: list[list[str]] = []
    for label, key in (("Owner gates", "owner_gates"), ("Operating holds", "operating_holds")):
        payload = collected["owner_gates_and_holds"][key]
        if payload["status"] == NOT_COLLECTED_LABEL:
            gate_rows.append([label, NOT_COLLECTED_LABEL, NOT_COLLECTED_LABEL, payload["reason"]])
        else:
            gate_rows.append(
                [
                    label,
                    str(payload["recorded_open"]),
                    f"{payload['denominator']} row(s)",
                    f"{payload['rows_with_a_readable_status']} of {payload['denominator']} "
                    "row(s) had a readable status cell",
                ]
            )
    out.extend(_table(["Record", "Recorded open", "Denominator", "Evidence coverage"], gate_rows))
    for label, key in (("owner gate", "owner_gates"), ("operating hold", "operating_holds")):
        payload = collected["owner_gates_and_holds"][key]
        for entry in payload.get("rows_not_recorded_open", []) or []:
            out.append("")
            out.append(
                f"- The {label} \"{entry['row']}\" is recorded as "
                f"\"{entry['recorded_status']}\". That is the packet's wording, not a "
                "clearance established here."
            )
    for note in collected["owner_gates_and_holds"]["notes"]:
        out.append("")
        out.append(f"- Drift: {note}")
    out.append("")

    out.append("### Link health")
    out.append("")
    health = collected["link_health"]
    out.extend(
        _table(
            ["Measure", "Count", "Denominator", "Evidence coverage"],
            [
                [
                    "Internal link targets that resolve",
                    str(health["internal_targets_resolving"]),
                    f"{health['internal_targets_checked']} internal target(s) checked",
                    f"{health['markdown_files_scanned']} markdown file(s) scanned",
                ]
            ],
        )
    )
    if health["unresolved_targets"]:
        out.append("")
        out.append(
            f"- {len(health['unresolved_targets'])} target(s) did not resolve. Run "
            "`python3 scripts/check_links.py` for the file and line of each."
        )
    out.append("")

    out.append("## Not collected here")
    out.append("")
    out.append(
        f"Each metric below is defined in `{report['contract']}` and cannot be supplied "
        "by committed files. Each is unmeasured, not zero. Step numbers refer to "
        "\"Minimal manual measurement at launch\"."
    )
    out.append("")
    out.extend(
        _table(
            ["Metric", "Type", "Count", "Why committed files cannot supply it", "Human measurement route"],
            [
                [
                    entry["metric"],
                    entry["metric_type"],
                    NOT_COLLECTED_LABEL,
                    entry["reason"],
                    entry["human_route"],
                ]
                for entry in report["not_collected"]
            ],
        )
    )
    out.append("")
    out.append("## Data this collector never reads")
    out.append("")
    out.extend(f"- {item}" for item in report["never_read"])
    out.append("")
    return "\n".join(out)


def render_json(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Collect the repository-observable part of the ops/METRICS.md measurement "
            "contract from committed files. Offline; reads only the scanned root."
        )
    )
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="repository root to scan")
    parser.add_argument(
        "--as-of",
        type=date.fromisoformat,
        default=None,
        help="report date as YYYY-MM-DD (default: today)",
    )
    parser.add_argument("--out", default=None, help="write the report to this path instead of stdout")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(
            f"{COLLECTOR}: --root {args.root!r} is not a directory. "
            "Pass the repository root, for example --root .",
            file=sys.stderr,
        )
        return 2
    root = root.resolve()
    as_of = args.as_of or date.today()
    report = build_report(root, as_of)
    text = render_json(report) if args.json else render_markdown(report)
    if args.out is None:
        sys.stdout.write(text)
        return 0
    out_path = Path(args.out)
    if out_path.is_dir():
        print(
            f"{COLLECTOR}: --out {args.out!r} is a directory. "
            "Pass a file path, for example --out metrics-2026-09-02.md",
            file=sys.stderr,
        )
        return 2
    if out_path.parent and not out_path.parent.exists():
        print(
            f"{COLLECTOR}: --out directory {str(out_path.parent)!r} does not exist. "
            "Create it first or choose an existing directory.",
            file=sys.stderr,
        )
        return 2
    out_path.write_text(text, encoding="utf-8")
    print(f"Wrote {'JSON' if args.json else 'markdown'} metrics report for {as_of.isoformat()} to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
