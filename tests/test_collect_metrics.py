from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 9, 2)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


collect_metrics = load_module(
    "practice_collect_metrics", REPOSITORY_ROOT / "scripts" / "collect_metrics.py"
)


def write(root: Path, name: str, text: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


PRACTICE = """---
artifact_type: practice
title: "A method"
summary: "A summary."
maturity: proposed
capability: use
roles: [operator]
version: 0.1.0
license: CC-BY-4.0
created: 2026-08-31
updated: 2026-08-31
evidence_quality: none
---

# A method

## Outcome

An outcome.

## Problem and scope

A problem.

## Use when

A trigger.

## Inputs

An input.

## Method

A step.

## Evaluation

A check.

## Failure modes

A failure mode.

## Evidence

An evidence note.

## Changelog

- 2026-08-31 — 0.1.0: Created the method.
"""

LAB = """---
artifact_type: lab
title: "A trial"
summary: "A summary."
status: completed
primary_capability: automate
run_count: 1
result_status: complete
last_run: 2026-09-01
version: 0.1.0
license: CC-BY-4.0
created: 2026-09-01
updated: 2026-09-01
---

# A trial

## Task set

A task.

## Procedure

A step.

## Evaluation rubric

A rubric.

## Results

A result.

## Limitations

A limitation.

## Reproduction

A reproduction note.

## Changelog

- 2026-09-01 — 0.1.0: Recorded the trial.
- 2026-09-02 — 0.1.1: Corrected a rubric row.
"""

STORY = """---
artifact_type: story
title: "A case"
status: draft
organization: withheld
evidence_quality: none
version: 0.1.0
license: CC-BY-4.0
created: 2026-08-31
updated: 2026-08-31
---

# A case

## Before

A starting point.

## Intervention

A change.

## Implementation

A rollout.

## After

An end point.

## Result

A result.

## Lessons

A lesson.

## Evidence record

A record.

## Changelog

- 2026-08-31: Added the case.
"""

GUIDE = """---
artifact_type: guide
title: "A path"
summary: "A summary."
status: draft
capability: build
audience: [engineer]
version: 0.1.0
license: CC-BY-4.0
created: 2026-08-31
updated: 2026-08-31
---

# A path

## Prerequisites

A prerequisite.

## Outcomes

An outcome.

## Path

A step.

## Evaluation

A check.

## Changelog

- 2026-08-31 — 0.1.0: Created the path.
"""

OWNER_REVIEW = """# Owner review packet

## Owner gates — open until a human records approval

| Gate | Evidence to review | Human action | Status |
| --- | --- | --- | --- |
| Gate one | Evidence. | Action. | **OPEN** |
| Gate two | Evidence. | Action. | **OPEN** |

## Evidenced operating holds

| Hold | Evidence | Minimum clearance evidence | Status |
| --- | --- | --- | --- |
| Hold one | Evidence. | Clearance evidence. | **OPEN — blocks public launch** |
"""

OWNER_GATES = """# Owner Gates

| Gate | Needed for | Default | Blocks agent work? |
|---|---|---|---|
| Gate one | Something | A default | No |
| Gate two | Something | A default | No |
"""


def build_fixture(root: Path) -> Path:
    """A small repository with one artifact of each type plus the review packet."""
    write(root, "practices/001-method.md", PRACTICE)
    write(root, "practices/README.md", "# Index\n\nNo front matter here.\n")
    write(root, "labs/001-trial.md", LAB)
    write(root, "stories/001-case.md", STORY)
    write(root, "guides/a-path/README.md", GUIDE)
    write(root, "guides/a-path/01-module.md", "# A module\n\nBody.\n")
    write(root, "guides/README.md", "# Guides\n\nNo front matter here.\n")
    write(root, "release/OWNER_REVIEW.md", OWNER_REVIEW)
    write(root, "OWNER_GATES.md", OWNER_GATES)
    return root


def report_for(root: Path) -> dict:
    return collect_metrics.build_report(root, AS_OF)


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = collect_metrics.main(argv)
    return code, out.getvalue(), err.getvalue()


def index_by(entries: list[dict], key: str) -> dict:
    return {entry[key]: entry for entry in entries}


class ArtifactInventoryTests(unittest.TestCase):
    def test_counts_each_artifact_type_against_a_shared_denominator(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            inventory = report_for(root)["collected"]["artifact_inventory"]

            counts = {e["artifact_type"]: e["count"] for e in inventory["by_type"]}
            self.assertEqual(counts, {"guide": 1, "lab": 1, "practice": 1, "story": 1})
            self.assertEqual(inventory["scored_artifacts"], 4)
            self.assertEqual(
                inventory["evidence_coverage"],
                "4 of 4 artifact file(s) parsed their front matter",
            )

    def test_guide_modules_and_index_documents_are_counted_but_not_scored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            inventory = report_for(root)["collected"]["artifact_inventory"]

            self.assertEqual(inventory["guide_modules"], 1)
            self.assertEqual(inventory["index_documents"], 2)
            self.assertEqual(inventory["scored_artifacts"], 4)

    def test_declared_state_is_read_verbatim_from_front_matter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            write(root, "practices/002-second.md", PRACTICE.replace("001", "002"))
            inventory = report_for(root)["collected"]["artifact_inventory"]

            states = {
                (e["artifact_type"], e["state"]): (e["count"], e["denominator"])
                for e in inventory["by_state"]
            }
            self.assertEqual(states[("practice", "proposed")], (2, 2))
            self.assertEqual(states[("lab", "completed")], (1, 1))
            self.assertEqual(states[("guide", "draft")], (1, 1))

    def test_capability_stage_segmentation_marks_undeclared_stages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            inventory = report_for(root)["collected"]["artifact_inventory"]

            stages = {e["capability_stage"]: e["count"] for e in inventory["by_capability_stage"]}
            self.assertEqual(stages, {"automate": 1, "build": 1, "not declared": 1, "use": 1})
            self.assertTrue(
                all(e["denominator"] == 4 for e in inventory["by_capability_stage"])
            )

    def test_declared_evidence_quality_is_reported_without_being_changed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            before = (root / "practices" / "001-method.md").read_text(encoding="utf-8")
            inventory = report_for(root)["collected"]["artifact_inventory"]

            labels = {e["evidence_quality"]: e["count"] for e in inventory["by_declared_evidence_quality"]}
            self.assertEqual(labels, {"none": 2, "not declared": 2})
            self.assertEqual(
                (root / "practices" / "001-method.md").read_text(encoding="utf-8"), before
            )

    def test_unreadable_artifact_is_excluded_and_shrinks_evidence_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            write(root, "practices/002-wrong-type.md", PRACTICE.replace("artifact_type: practice", "artifact_type: lab"))
            inventory = report_for(root)["collected"]["artifact_inventory"]

            self.assertEqual(inventory["scored_artifacts"], 4)
            self.assertEqual(inventory["unreadable_front_matter"], ["practices/002-wrong-type.md"])
            self.assertEqual(
                inventory["evidence_coverage"],
                "4 of 5 artifact file(s) parsed their front matter",
            )


class EvidenceCoverageTests(unittest.TestCase):
    def test_every_mapped_element_is_reported_with_its_denominator(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            coverage = report_for(root)["collected"]["evidence_coverage"]

            by_type = index_by(coverage["by_type"], "artifact_type")
            self.assertEqual(by_type["practice"]["artifacts_stating_every_element"], 1)
            self.assertEqual(by_type["practice"]["denominator"], 1)
            self.assertEqual(by_type["practice"]["elements_present"], 7)
            self.assertEqual(by_type["practice"]["elements_checked"], 7)
            self.assertEqual(by_type["lab"]["elements_checked"], 6)
            self.assertEqual(by_type["story"]["elements_checked"], 6)
            self.assertEqual(by_type["guide"]["elements_checked"], 4)

            practice_elements = {
                entry["element"]
                for entry in coverage["by_element"]
                if entry["artifact_type"] == "practice"
            }
            self.assertEqual(
                practice_elements,
                {"inputs", "steps", "output", "evaluation", "limitations", "failure modes", "inspectable record"},
            )

    def test_a_missing_section_is_counted_as_an_unstated_element(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            write(
                root,
                "practices/001-method.md",
                PRACTICE.replace("## Evidence\n\nAn evidence note.\n\n", ""),
            )
            coverage = report_for(root)["collected"]["evidence_coverage"]

            by_type = index_by(coverage["by_type"], "artifact_type")
            self.assertEqual(by_type["practice"]["artifacts_stating_every_element"], 0)
            self.assertEqual(by_type["practice"]["elements_present"], 6)
            self.assertEqual(by_type["practice"]["elements_checked"], 7)

    def test_an_empty_section_does_not_count_as_a_stated_element(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            write(
                root,
                "practices/001-method.md",
                PRACTICE.replace("## Evidence\n\nAn evidence note.\n", "## Evidence\n\n"),
            )
            coverage = report_for(root)["collected"]["evidence_coverage"]

            elements = {
                entry["element"]: entry["present"]
                for entry in coverage["by_element"]
                if entry["artifact_type"] == "practice"
            }
            self.assertEqual(elements["inspectable record"], 0)
            self.assertEqual(elements["inputs"], 1)

    def test_an_alternative_mapped_heading_satisfies_an_element(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            write(root, "labs/001-trial.md", LAB.replace("## Task set", "## Fixed conditions"))
            coverage = report_for(root)["collected"]["evidence_coverage"]

            by_type = index_by(coverage["by_type"], "artifact_type")
            self.assertEqual(by_type["lab"]["artifacts_stating_every_element"], 1)


class ContributionRecordTests(unittest.TestCase):
    def test_dated_changelog_bullets_are_counted_as_accepted_contributions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            contributions = report_for(root)["collected"]["contribution_records"]

            self.assertEqual(contributions["accepted_changelog_entries"], 5)
            by_type = index_by(contributions["by_type"], "artifact_type")
            self.assertEqual(by_type["lab"]["accepted_changelog_entries"], 2)
            self.assertEqual(by_type["practice"]["accepted_changelog_entries"], 1)

    def test_undated_changelog_prose_is_not_counted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            write(
                root,
                "practices/001-method.md",
                PRACTICE.replace(
                    "- 2026-08-31 — 0.1.0: Created the method.",
                    "- Created the method at some point.\n- Revised it later.",
                ),
            )
            contributions = report_for(root)["collected"]["contribution_records"]

            by_type = index_by(contributions["by_type"], "artifact_type")
            self.assertEqual(by_type["practice"]["accepted_changelog_entries"], 0)
            self.assertEqual(by_type["practice"]["artifacts_with_changelog"], 1)

    def test_count_is_paired_with_a_denominator_and_evidence_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            write(
                root,
                "stories/001-case.md",
                STORY.replace("## Changelog\n\n- 2026-08-31: Added the case.\n", ""),
            )
            contributions = report_for(root)["collected"]["contribution_records"]

            self.assertEqual(contributions["denominator"], 4)
            self.assertEqual(contributions["artifacts_with_changelog"], 3)
            self.assertEqual(contributions["accepted_changelog_entries"], 4)

            markdown = collect_metrics.render_markdown(report_for(root))
            self.assertIn(
                "| Dated changelog entries | 4 | 4 scored artifact(s) | "
                "3 of 4 artifact(s) carry a non-empty changelog |",
                markdown,
            )


class GateAndHoldTests(unittest.TestCase):
    def test_open_rows_are_counted_against_the_table_denominator(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            payload = report_for(root)["collected"]["owner_gates_and_holds"]

            self.assertEqual(payload["owner_gates"]["status"], "collected")
            self.assertEqual(payload["owner_gates"]["recorded_open"], 2)
            self.assertEqual(payload["owner_gates"]["denominator"], 2)
            self.assertEqual(payload["owner_gates"]["rows_with_a_readable_status"], 2)
            self.assertEqual(payload["operating_holds"]["recorded_open"], 1)
            self.assertEqual(payload["operating_holds"]["denominator"], 1)
            self.assertEqual(payload["notes"], [])

    def test_a_row_not_recorded_open_is_copied_verbatim_and_never_called_cleared(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            write(
                root,
                "release/OWNER_REVIEW.md",
                OWNER_REVIEW.replace(
                    "| Gate two | Evidence. | Action. | **OPEN** |",
                    "| Gate two | Evidence. | Action. | Approved 2026-09-01 |",
                ),
            )
            report = report_for(root)
            payload = report["collected"]["owner_gates_and_holds"]["owner_gates"]

            self.assertEqual(payload["recorded_open"], 1)
            self.assertEqual(payload["denominator"], 2)
            self.assertEqual(
                payload["rows_not_recorded_open"],
                [{"row": "Gate two", "recorded_status": "Approved 2026-09-01"}],
            )

            markdown = collect_metrics.render_markdown(report)
            self.assertIn('is recorded as "Approved 2026-09-01"', markdown)
            self.assertIn("not a clearance established here", markdown)
            self.assertNotIn("cleared gate", markdown.lower())

    def test_gate_count_drift_between_the_two_documents_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            write(
                root,
                "OWNER_GATES.md",
                OWNER_GATES + "| Gate three | Something | A default | No |\n",
            )
            notes = report_for(root)["collected"]["owner_gates_and_holds"]["notes"]

            self.assertEqual(len(notes), 1)
            self.assertIn("lists 3 gate row(s)", notes[0])
            self.assertIn("lists 2", notes[0])

    def test_missing_review_packet_is_not_collected_rather_than_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            (root / "release" / "OWNER_REVIEW.md").unlink()
            report = report_for(root)
            payload = report["collected"]["owner_gates_and_holds"]

            for key in ("owner_gates", "operating_holds"):
                self.assertEqual(payload[key]["status"], "not collected")
                self.assertIsNone(payload[key]["recorded_open"])
                self.assertIsNone(payload[key]["denominator"])
                self.assertIn("release/OWNER_REVIEW.md", payload[key]["reason"])

            markdown = collect_metrics.render_markdown(report)
            self.assertIn("| Owner gates | not collected | not collected |", markdown)
            self.assertNotIn("| Owner gates | 0 |", markdown)


class LinkHealthTests(unittest.TestCase):
    def test_resolving_targets_are_counted_against_targets_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[ok](b.md) [missing](nope.md)\n")
            write(root, "b.md", "target\n")
            health = report_for(root)["collected"]["link_health"]

            self.assertEqual(health["internal_targets_checked"], 2)
            self.assertEqual(health["internal_targets_resolving"], 1)
            self.assertEqual(health["markdown_files_scanned"], 2)
            self.assertEqual(len(health["unresolved_targets"]), 1)
            self.assertIn("nope.md", health["unresolved_targets"][0])

    def test_external_and_fragment_targets_are_not_counted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[x](https://example.invalid) [y](#anchor) [z](`code`)\n")
            health = report_for(root)["collected"]["link_health"]

            self.assertEqual(health["internal_targets_checked"], 0)
            self.assertEqual(health["internal_targets_resolving"], 0)

    def test_code_fenced_examples_are_not_treated_as_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "```\n[example](missing.md)\n```\n")
            health = report_for(root)["collected"]["link_health"]

            self.assertEqual(health["internal_targets_checked"], 0)


class DataMinimizationTests(unittest.TestCase):
    def test_the_git_directory_is_never_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            write(root, ".git/config", "[user]\n\temail = person@example.invalid\n")
            write(root, ".git/notes.md", "[broken](does-not-exist.md)\n")
            report = report_for(root)
            markdown = collect_metrics.render_markdown(report)

            self.assertEqual(report["collected"]["link_health"]["unresolved_targets"], [])
            self.assertNotIn("person@example.invalid", markdown)
            self.assertIsNone(EMAIL_RE.search(markdown))

    def test_the_collector_has_no_network_or_subprocess_capability(self):
        source = (REPOSITORY_ROOT / "scripts" / "collect_metrics.py").read_text(encoding="utf-8")
        imports = re.findall(r"^\s*(?:from|import)\s+([A-Za-z_][\w.]*)", source, re.MULTILINE)

        for module in imports:
            self.assertNotIn(
                module.split(".")[0],
                {"socket", "ssl", "urllib", "http", "requests", "httpx", "subprocess", "os"},
                f"{module} must not be importable capability in the collector",
            )

    def test_the_report_declares_what_it_never_reads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            report = report_for(root)
            markdown = collect_metrics.render_markdown(report)

            self.assertTrue(report["never_read"])
            for item in report["never_read"]:
                self.assertIn(item, markdown)
            joined = " ".join(report["never_read"]).lower()
            for forbidden in ("identit", "join", "view", "reaction", "network"):
                self.assertIn(forbidden, joined)


class NotCollectedTests(unittest.TestCase):
    def test_every_uncollectable_metric_is_listed_with_a_route_and_no_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            report = report_for(root)

            metrics = [entry["metric"] for entry in report["not_collected"]]
            self.assertEqual(
                metrics,
                [
                    "Activation",
                    "Contribution (proposed)",
                    "Artifact reuse",
                    "Implementation",
                    "Response quality",
                    "Retention",
                    "Maintainer health",
                ],
            )
            for entry in report["not_collected"]:
                self.assertIsNone(entry["count"])
                self.assertEqual(entry["status"], "not collected")
                self.assertTrue(entry["reason"].strip())
                self.assertTrue(entry["human_route"].strip())

    def test_markdown_prints_not_collected_instead_of_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            markdown = collect_metrics.render_markdown(report_for(root))

            for metric in ("Activation", "Artifact reuse", "Retention", "Maintainer health"):
                self.assertIn(f"| {metric} |", markdown)
            self.assertNotIn("| Activation | Leading | 0 |", markdown)
            self.assertIn("Each is unmeasured, not zero.", markdown)

    def test_a_measured_zero_is_still_printed_as_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "practices/README.md", "# Index\n")
            report = report_for(root)
            markdown = collect_metrics.render_markdown(report)

            self.assertEqual(report["collected"]["artifact_inventory"]["scored_artifacts"], 0)
            self.assertIn("| practice | 0 | 0 scored artifact(s) |", markdown)


class DeterminismTests(unittest.TestCase):
    def test_markdown_bytes_are_identical_across_two_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            first = collect_metrics.render_markdown(report_for(root))
            second = collect_metrics.render_markdown(report_for(root))

            self.assertEqual(first.encode("utf-8"), second.encode("utf-8"))

    def test_json_bytes_are_identical_across_two_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            first = collect_metrics.render_json(report_for(root))
            second = collect_metrics.render_json(report_for(root))

            self.assertEqual(first.encode("utf-8"), second.encode("utf-8"))

    def test_cli_output_is_identical_across_two_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            argv = ["--root", str(root), "--as-of", "2026-09-02"]
            first_code, first_out, _ = run_cli(argv)
            second_code, second_out, _ = run_cli(argv)

            self.assertEqual((first_code, second_code), (0, 0))
            self.assertEqual(first_out, second_out)
            self.assertIn("- As of: 2026-09-02", first_out)

    def test_file_ordering_does_not_change_the_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            write(root, "practices/003-third.md", PRACTICE.replace("A method", "Third"))
            write(root, "practices/002-second.md", PRACTICE.replace("A method", "Second"))
            first = collect_metrics.render_json(report_for(root))

        with tempfile.TemporaryDirectory() as directory:
            other = build_fixture(Path(directory))
            write(other, "practices/002-second.md", PRACTICE.replace("A method", "Second"))
            write(other, "practices/003-third.md", PRACTICE.replace("A method", "Third"))
            second = collect_metrics.render_json(report_for(other))

        self.assertEqual(first, second)


class JsonShapeTests(unittest.TestCase):
    def test_top_level_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            payload = json.loads(collect_metrics.render_json(report_for(root)))

            self.assertEqual(
                sorted(payload),
                ["as_of", "collected", "collector", "contract", "never_read", "not_collected"],
            )
            self.assertEqual(payload["as_of"], "2026-09-02")
            self.assertEqual(payload["collector"], "scripts/collect_metrics.py")
            self.assertEqual(payload["contract"], "ops/METRICS.md")
            self.assertEqual(
                sorted(payload["collected"]),
                [
                    "artifact_inventory",
                    "contribution_records",
                    "evidence_coverage",
                    "link_health",
                    "owner_gates_and_holds",
                ],
            )

    def test_collected_sections_pair_counts_with_denominators(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            payload = json.loads(collect_metrics.render_json(report_for(root)))
            collected = payload["collected"]

            for entry in collected["evidence_coverage"]["by_type"]:
                self.assertEqual(
                    sorted(entry),
                    [
                        "artifact_type",
                        "artifacts_stating_every_element",
                        "denominator",
                        "elements_checked",
                        "elements_present",
                    ],
                )
            for entry in collected["evidence_coverage"]["by_element"]:
                self.assertEqual(sorted(entry), ["artifact_type", "denominator", "element", "present"])
            self.assertEqual(
                sorted(collected["contribution_records"]),
                ["accepted_changelog_entries", "artifacts_with_changelog", "by_type", "denominator"],
            )
            self.assertEqual(
                sorted(collected["link_health"]),
                [
                    "internal_targets_checked",
                    "internal_targets_resolving",
                    "markdown_files_scanned",
                    "unresolved_targets",
                ],
            )

    def test_not_collected_entry_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            payload = json.loads(collect_metrics.render_json(report_for(root)))

            for entry in payload["not_collected"]:
                self.assertEqual(
                    sorted(entry),
                    ["count", "human_route", "metric", "metric_type", "reason", "status"],
                )

    def test_json_is_valid_from_the_command_line(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            code, out, _ = run_cli(["--root", str(root), "--as-of", "2026-09-02", "--json"])

            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)["as_of"], "2026-09-02")
            self.assertTrue(out.endswith("\n"))


class CommandLineTests(unittest.TestCase):
    def test_out_writes_the_same_bytes_it_would_have_printed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            target = Path(directory) / "out" / "metrics-2026-09-02.md"
            target.parent.mkdir()
            _, printed, _ = run_cli(["--root", str(root), "--as-of", "2026-09-02"])
            code, message, _ = run_cli(
                ["--root", str(root), "--as-of", "2026-09-02", "--out", str(target)]
            )

            self.assertEqual(code, 0)
            self.assertIn("Wrote markdown metrics report for 2026-09-02", message)
            self.assertEqual(target.read_text(encoding="utf-8"), printed)

    def test_missing_root_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as directory:
            code, _, err = run_cli(["--root", str(Path(directory) / "absent")])

            self.assertEqual(code, 2)
            self.assertIn("is not a directory", err)

    def test_out_pointing_at_a_directory_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            code, _, err = run_cli(["--root", str(root), "--out", str(root)])

            self.assertEqual(code, 2)
            self.assertIn("is a directory", err)

    def test_out_into_a_missing_directory_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_fixture(Path(directory))
            target = Path(directory) / "absent" / "report.md"
            code, _, err = run_cli(["--root", str(root), "--out", str(target)])

            self.assertEqual(code, 2)
            self.assertIn("does not exist", err)


class RepositorySmokeTests(unittest.TestCase):
    def test_collector_runs_against_the_real_repository(self):
        report = collect_metrics.build_report(REPOSITORY_ROOT, AS_OF)
        collected = report["collected"]
        inventory = collected["artifact_inventory"]

        self.assertEqual(inventory["unreadable_front_matter"], [])
        counts = {entry["artifact_type"]: entry["count"] for entry in inventory["by_type"]}
        for kind in ("practice", "lab", "story", "guide"):
            self.assertGreater(counts[kind], 0, f"expected at least one {kind} artifact")
        self.assertEqual(sum(counts.values()), inventory["scored_artifacts"])

        gates = collected["owner_gates_and_holds"]["owner_gates"]
        holds = collected["owner_gates_and_holds"]["operating_holds"]
        for payload in (gates, holds):
            self.assertEqual(payload["status"], "collected")
            self.assertGreater(payload["denominator"], 0)
            self.assertLessEqual(payload["recorded_open"], payload["denominator"])

        health = collected["link_health"]
        self.assertGreater(health["markdown_files_scanned"], 0)
        self.assertEqual(
            health["internal_targets_resolving"],
            health["internal_targets_checked"] - len(health["unresolved_targets"]),
        )

        markdown = collect_metrics.render_markdown(report)
        self.assertIn("# Practice repository metrics report", markdown)
        self.assertIsNone(EMAIL_RE.search(markdown))
        self.assertIn("it does not clear any owner gate or operating hold", markdown)


if __name__ == "__main__":
    unittest.main()
