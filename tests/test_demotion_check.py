"""Failure-mode coverage for scripts/demotion_check.py.

Most tests build a synthetic repository in a temporary directory, copy the real
``docs/framework/AUTONOMY_LADDER.md`` into it so the parser is always exercised
against the shipped document, write one ledger entry that breaks exactly one
thing, and assert that the check fires the trigger the ladder names for it.

Three things those fixtures cannot prove are tested against the real repository
instead:

- ``test_shipped_tree_fires_nothing_for_the_right_reason``: on the tree this
  repository ships the check exits 0 because no run has ever left a record - not
  because the parser found no triggers. A check that reported a clean repository
  for a ladder it could not read would pass every other test here;
- ``test_ladder_without_a_trigger_paragraph_fails_loudly``: a ladder whose
  automatic-demotion paragraph is missing exits 2 and says so, rather than
  reporting zero triggers;
- ``test_the_check_writes_nothing``: the check reports and never demotes, so it
  writes no file - including into the real ``ops/ledger/``.

No test writes into the real ``ops/ledger/``. Every fixture ledger lives under a
temporary directory that is removed when the test ends.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LADDER_RELATIVE = "docs/framework/AUTONOMY_LADDER.md"
SCRIPT = REPOSITORY_ROOT / "scripts" / "demotion_check.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Registered before execution so the module's dataclasses can resolve their
    # own annotations, which `from __future__ import annotations` defers.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


check = load_module("practice_demotion_check", SCRIPT)

LADDER_TEXT = (REPOSITORY_ROOT / LADDER_RELATIVE).read_text(encoding="utf-8")

CATALOG = {
    "schema_version": 1,
    "operations": [
        {
            "id": "cadence-snapshot",
            "summary": "Run the cadence report and write a dated status file.",
            "command": ["python3", "scripts/cadence.py", "--root", "."],
            "write_scope": ["ops/status/*.md"],
            "reversal": "Delete the written file, or close the pull request unmerged.",
            "blast_radius": "One new file in the repository. No member contact.",
            "level": "A1",
        }
    ],
}

PROMOTIONS = {"schema_version": 1, "kill_switch": "engaged", "promotions": []}

WRITTEN_PATH = "ops/status/2026-09-02-cadence.md"

# A complete, well-behaved record of a run that stayed inside its bound. Every
# detector must stay silent on it, so each firing test below is a one-field edit
# away from a case that does not fire.
CLEAN_ENTRY = {
    "ledger_schema_version": 1,
    "run_id": "cadence-snapshot-001",
    "run_date": "2026-09-02",
    "operation": "cadence-snapshot",
    "actor": "scheduled-workflow",
    "claimed_level": "A3",
    "trigger": "schedule",
    "kill_switch": "released",
    "promotion": {"level": "A3", "signed_by": "founder", "signed_on": "2026-09-02"},
    "preconditions": [
        {
            "check": "promotion-signed",
            "result": "pass",
            "detail": "A promotion for cadence-snapshot at A3 is recorded, signed by the founder.",
        }
    ],
    "command": ["python3", "scripts/cadence.py", "--root", "."],
    "write_scope": ["ops/status/*.md"],
    "paths_read": ["ops/cadence.yaml"],
    "paths_written": [WRITTEN_PATH],
    "reversal": "Delete ops/status/2026-09-02-cadence.md, or close the pull request unmerged.",
    "outcome": "completed",
}


def entry(**overrides) -> dict:
    record = copy.deepcopy(CLEAN_ENTRY)
    record.update(overrides)
    return record


class FixtureRepository:
    """A synthetic repository root with a real ladder and a writable ledger."""

    def __init__(self, directory: Path, ladder_text: str = LADDER_TEXT):
        self.root = directory
        (self.root / "docs" / "framework").mkdir(parents=True)
        (self.root / LADDER_RELATIVE).write_text(ladder_text, encoding="utf-8")
        (self.root / "ops" / "autonomy").mkdir(parents=True)
        self.write_catalog(CATALOG)
        (self.root / "ops" / "autonomy" / "promotions.yaml").write_text(
            yaml.safe_dump(PROMOTIONS, sort_keys=False), encoding="utf-8"
        )
        (self.root / "ops" / "ledger").mkdir(parents=True)
        (self.root / "ops" / "status").mkdir(parents=True)
        self.write_output(WRITTEN_PATH, "# Cadence snapshot\n\nNo maturity field here.\n")

    def write_catalog(self, catalog: dict) -> None:
        (self.root / "ops" / "autonomy" / "operations.yaml").write_text(
            yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8"
        )

    def write_output(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def add_entry(self, record: dict, body: str | None = None) -> Path:
        name = f"{record['run_date']}-{record['run_id']}.md"
        path = self.root / "ops" / "ledger" / name
        front_matter = yaml.safe_dump(record, sort_keys=False, default_flow_style=False)
        text = body or f"# {record['operation']} run {record['run_id']}\n"
        path.write_text(f"---\n{front_matter}---\n\n{text}", encoding="utf-8")
        return path

    def add_raw_entry(self, name: str, text: str) -> Path:
        path = self.root / "ops" / "ledger" / name
        path.write_text(text, encoding="utf-8")
        return path

    def evaluate(self):
        return check.evaluate(self.root)


class FixtureCase(unittest.TestCase):
    """Base class giving each test its own temporary repository."""

    ladder_text = LADDER_TEXT

    def setUp(self):
        self._directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._directory.cleanup)
        self.repo = FixtureRepository(Path(self._directory.name), self.ladder_text)

    def fired_keys(self, report) -> list[str]:
        return sorted(
            finding.trigger_key
            for finding in report.findings
            if finding.kind == check.KIND_TRIGGER
        )

    def kinds(self, report) -> list[str]:
        return sorted(finding.kind for finding in report.findings)


class TriggerEnumerationTests(unittest.TestCase):
    """The trigger list comes from the ladder, never from a copy in this script."""

    def test_every_level_section_contributes_triggers(self):
        triggers = check.parse_ladder_triggers(REPOSITORY_ROOT)
        levels = sorted({trigger.level for trigger in triggers})
        self.assertEqual(levels, ["A0", "A1", "A2", "A3"])
        self.assertGreaterEqual(len(triggers), 8, "the ladder states more than one trigger a level")

    def test_every_ladder_trigger_is_classified_exactly_once(self):
        paired = check.classify_triggers(check.parse_ladder_triggers(REPOSITORY_ROOT))
        keys = [item.classification.key for item in paired]
        self.assertEqual(len(keys), len(set(keys)), "no classification may claim two clauses")
        self.assertEqual(
            sorted(keys),
            sorted(item.key for item in check.CLASSIFICATIONS),
            "every classification in the script must match a clause the ladder still states",
        )

    def test_each_trigger_is_evaluable_here_or_carries_a_reason(self):
        for item in check.classify_triggers(check.parse_ladder_triggers(REPOSITORY_ROOT)):
            with self.subTest(trigger=item.trigger.trigger_id):
                self.assertIn(item.classification.basis, {
                    check.BASIS_EVALUATED,
                    check.BASIS_DELEGATED,
                    check.BASIS_NOT_OBSERVABLE,
                    check.BASIS_MISSING_FIELD,
                })
                self.assertGreater(
                    len(item.classification.reason), 60, "a classification needs a real reason"
                )
                if item.classification.evaluable:
                    self.assertIn(item.classification.detector, check.DETECTORS)
                else:
                    self.assertIsNone(item.classification.detector)

    def test_the_review_point_trigger_is_classified_not_evaluable(self):
        """X1's flagged gap: no promotion record can name a review point."""
        paired = check.classify_triggers(check.parse_ladder_triggers(REPOSITORY_ROOT))
        item = next(x for x in paired if x.classification.key == "acted-after-review-point")
        self.assertFalse(item.classification.evaluable)
        self.assertEqual(item.classification.basis, check.BASIS_MISSING_FIELD)
        self.assertIn("review_point", item.classification.reason)
        self.assertIn("renewal", item.classification.reason)


class LadderDriftTests(unittest.TestCase):
    """A ladder this check cannot read is a loud failure, never a clean report."""

    def run_on(self, ladder_text: str) -> tuple[int, str, str]:
        with tempfile.TemporaryDirectory() as directory:
            FixtureRepository(Path(directory), ladder_text)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", directory],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode, result.stdout, result.stderr

    def test_ladder_without_a_trigger_paragraph_fails_loudly(self):
        """The non-vacuity test: a missing trigger section is not zero triggers."""
        stripped = "\n".join(
            line for line in LADDER_TEXT.split("\n") if not line.startswith("**Automatic demotion")
        )
        code, stdout, stderr = self.run_on(stripped)
        self.assertEqual(code, 2, "a ladder with no trigger paragraph must fail, not pass")
        self.assertIn("Automatic demotion", stderr)
        self.assertNotIn("NO TRIGGER FIRED", stdout)
        self.assertEqual(stdout.strip(), "", "nothing is reported when nothing could be read")

    def test_missing_ladder_file_fails_loudly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "ops" / "ledger").mkdir(parents=True)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", directory],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn(LADDER_RELATIVE, result.stderr)
        self.assertNotIn("NO TRIGGER FIRED", result.stdout)

    def test_missing_level_section_fails_loudly(self):
        without_a3 = LADDER_TEXT.replace("## A3 act-unattended-within-bounds", "## Removed section")
        code, _, stderr = self.run_on(without_a3)
        self.assertEqual(code, 2)
        self.assertIn("A3", stderr)

    def test_a_new_ladder_trigger_must_be_classified(self):
        added = LADDER_TEXT.replace(
            "an action taken with no reversal path recorded;",
            "an action taken with no reversal path recorded; an action taken during a freeze window;",
        )
        self.assertNotEqual(added, LADDER_TEXT)
        code, _, stderr = self.run_on(added)
        self.assertEqual(code, 2)
        self.assertIn("matches no classification", stderr)
        self.assertIn("freeze window", stderr)

    def test_a_removed_ladder_trigger_is_reported(self):
        removed = LADDER_TEXT.replace("an action taken with no reversal path recorded; ", "")
        self.assertNotEqual(removed, LADDER_TEXT)
        code, _, stderr = self.run_on(removed)
        self.assertEqual(code, 2)
        self.assertIn("no-reversal-recorded", stderr)
        self.assertIn("governance change", stderr)


class CleanRunTests(FixtureCase):
    """The not-firing side: a run inside its bound fires nothing."""

    def test_a_run_inside_its_bound_fires_nothing(self):
        self.repo.add_entry(entry())
        report = self.repo.evaluate()
        self.assertEqual(report.findings, [])
        self.assertEqual(report.exit_code, 0)
        self.assertEqual(len(report.runs_evaluated), 1)

    def test_an_empty_ledger_fires_nothing(self):
        report = self.repo.evaluate()
        self.assertEqual(report.findings, [])
        self.assertEqual(report.exit_code, 0)
        self.assertEqual(report.runs_evaluated, [])
        self.assertGreater(len(report.triggers), 0, "an empty ledger must still enumerate triggers")

    def test_a_refused_entry_is_the_guard_working_not_a_violation(self):
        self.repo.add_entry(
            entry(
                run_id="cadence-snapshot-002",
                claimed_level="A3",
                kill_switch="engaged",
                promotion="none",
                outcome="refused",
                paths_written=[],
                preconditions=[
                    {
                        "check": "promotion-signed",
                        "result": "fail",
                        "detail": "No promotion is recorded for cadence-snapshot.",
                    },
                    {
                        "check": "kill-switch-released",
                        "result": "fail",
                        "detail": "The promotion record reads kill_switch: engaged.",
                    },
                ],
                reversal="Nothing was written, so there is nothing to undo.",
            )
        )
        report = self.repo.evaluate()
        self.assertEqual(report.findings, [])
        self.assertEqual(report.exit_code, 0)

    def test_a_dry_run_entry_fires_nothing(self):
        self.repo.add_entry(
            entry(
                run_id="cadence-snapshot-003",
                outcome="dry-run",
                paths_written=[],
                reversal="Nothing was written, so there is nothing to undo.",
            )
        )
        self.assertEqual(self.repo.evaluate().findings, [])


class WriteOutsideScopeTests(FixtureCase):
    """A1: a draft edits a path outside the scope named in its assignment."""

    def test_a_write_outside_the_recorded_scope_fires(self):
        self.repo.add_entry(entry(paths_written=[WRITTEN_PATH, "docs/DECISIONS.md"]))
        report = self.repo.evaluate()
        self.assertIn("write-outside-scope", self.fired_keys(report))
        self.assertEqual(report.exit_code, 1)
        finding = next(f for f in report.findings if f.trigger_key == "write-outside-scope")
        self.assertIn("docs/DECISIONS.md", finding.observed)
        self.assertIn("ops/status/*.md", finding.declared)
        self.assertEqual(finding.operation, "cadence-snapshot")
        self.assertEqual(finding.claimed_level, "A3")
        self.assertEqual(finding.demoted_to, "A2")
        self.assertIn("2026-09-02-cadence-snapshot-001.md", finding.entry)

    def test_an_empty_write_scope_makes_any_write_a_violation(self):
        self.repo.add_entry(entry(write_scope=[], paths_written=[WRITTEN_PATH]))
        report = self.repo.evaluate()
        self.assertIn("write-outside-scope", self.fired_keys(report))

    def test_a_write_inside_the_recorded_scope_does_not_fire(self):
        self.repo.add_entry(entry(paths_written=[WRITTEN_PATH]))
        self.assertNotIn("write-outside-scope", self.fired_keys(self.repo.evaluate()))


class MaturityWriteTests(FixtureCase):
    """A1: a draft changes a `maturity` or `evidence_quality` value."""

    def test_a_write_to_a_maturity_bearing_file_fires(self):
        self.repo.write_output(WRITTEN_PATH, "---\nmaturity: proposed\n---\n\n# Method\n")
        self.repo.add_entry(entry())
        report = self.repo.evaluate()
        self.assertIn("maturity-or-evidence-change", self.fired_keys(report))
        finding = next(f for f in report.findings if f.trigger_key == "maturity-or-evidence-change")
        self.assertIn(WRITTEN_PATH, finding.observed)
        self.assertIn("records no diff", finding.observed)

    def test_an_evidence_quality_field_fires_too(self):
        self.repo.write_output(WRITTEN_PATH, "---\nevidence_quality: none\n---\n\n# Method\n")
        self.repo.add_entry(entry())
        self.assertIn("maturity-or-evidence-change", self.fired_keys(self.repo.evaluate()))

    def test_a_write_to_an_ordinary_file_does_not_fire(self):
        self.repo.add_entry(entry())
        self.assertNotIn("maturity-or-evidence-change", self.fired_keys(self.repo.evaluate()))

    def test_a_written_path_that_no_longer_exists_is_recorded_as_a_limit(self):
        (self.repo.root / WRITTEN_PATH).unlink()
        self.repo.add_entry(entry(outcome="reverted"))
        report = self.repo.evaluate()
        self.assertNotIn("maturity-or-evidence-change", self.fired_keys(report))
        self.assertTrue(any(WRITTEN_PATH in limit for limit in report.limits))


class ActedOutsideBoundTests(FixtureCase):
    """A3: an action taken outside the recorded bound."""

    def test_acting_after_a_failed_precondition_fires(self):
        self.repo.add_entry(
            entry(
                preconditions=[
                    {
                        "check": "kill-switch-released",
                        "result": "fail",
                        "detail": "The promotion record reads kill_switch: engaged.",
                    }
                ]
            )
        )
        report = self.repo.evaluate()
        self.assertIn("acted-outside-recorded-bound", self.fired_keys(report))
        finding = next(f for f in report.findings if f.trigger_key == "acted-outside-recorded-bound")
        self.assertIn("kill-switch-released", finding.observed)
        self.assertIn("fail", finding.observed)

    def test_acting_with_the_kill_switch_engaged_fires(self):
        self.repo.add_entry(entry(kill_switch="engaged"))
        report = self.repo.evaluate()
        self.assertIn("acted-outside-recorded-bound", self.fired_keys(report))
        finding = next(f for f in report.findings if f.trigger_key == "acted-outside-recorded-bound")
        self.assertIn("kill_switch: engaged", finding.observed)

    def test_claiming_a3_with_no_promotion_and_acting_fires(self):
        self.repo.add_entry(entry(promotion="none"))
        report = self.repo.evaluate()
        finding = next(f for f in report.findings if f.trigger_key == "acted-outside-recorded-bound")
        self.assertIn("promotion: none", finding.observed)

    def test_a_failed_precondition_with_no_action_does_not_fire(self):
        self.repo.add_entry(
            entry(
                outcome="refused",
                paths_written=[],
                reversal="Nothing was written, so there is nothing to undo.",
                preconditions=[
                    {
                        "check": "promotion-signed",
                        "result": "fail",
                        "detail": "No promotion is recorded for cadence-snapshot.",
                    }
                ],
            )
        )
        self.assertNotIn("acted-outside-recorded-bound", self.fired_keys(self.repo.evaluate()))

    def test_a_clean_bound_does_not_fire(self):
        self.repo.add_entry(entry())
        self.assertNotIn("acted-outside-recorded-bound", self.fired_keys(self.repo.evaluate()))


class ReversalTests(FixtureCase):
    """A3: an action taken with no reversal path recorded."""

    def test_a_placeholder_reversal_on_an_action_fires(self):
        self.repo.add_entry(entry(reversal="n/a"))
        report = self.repo.evaluate()
        self.assertIn("no-reversal-recorded", self.fired_keys(report))
        finding = next(f for f in report.findings if f.trigger_key == "no-reversal-recorded")
        self.assertIn("n/a", finding.observed)

    def test_an_absent_reversal_on_an_action_fires(self):
        record = entry()
        del record["reversal"]
        self.repo.add_entry(record)
        self.assertIn("no-reversal-recorded", self.fired_keys(self.repo.evaluate()))

    def test_a_missing_reversal_on_a_run_that_did_nothing_does_not_fire(self):
        self.repo.add_entry(entry(outcome="refused", paths_written=[], reversal=""))
        self.assertNotIn("no-reversal-recorded", self.fired_keys(self.repo.evaluate()))

    def test_a_recorded_reversal_does_not_fire(self):
        self.repo.add_entry(entry())
        self.assertNotIn("no-reversal-recorded", self.fired_keys(self.repo.evaluate()))


class IneligibleOperationTests(FixtureCase):
    """A3: an action on an operation since added to the permanently ineligible list."""

    def test_acting_on_a_permanently_ineligible_operation_fires(self):
        self.repo.add_entry(entry(operation="maturity-promotion", run_id="maturity-promotion-001"))
        report = self.repo.evaluate()
        self.assertIn("operation-since-made-ineligible", self.fired_keys(report))
        finding = next(
            f for f in report.findings if f.trigger_key == "operation-since-made-ineligible"
        )
        self.assertIn("maturity-promotion", finding.declared)
        self.assertIn(check.INELIGIBLE_HEADING, finding.declared)

    def test_a_catalogued_operation_does_not_fire(self):
        self.repo.add_entry(entry())
        self.assertNotIn("operation-since-made-ineligible", self.fired_keys(self.repo.evaluate()))

    def test_an_unreadable_ineligible_list_is_unjudged_never_clear(self):
        without_section = LADDER_TEXT.replace(
            check.INELIGIBLE_HEADING, "## Operations that stay with a person"
        )
        with tempfile.TemporaryDirectory() as directory:
            repo = FixtureRepository(Path(directory), without_section)
            repo.add_entry(entry(operation="maturity-promotion", run_id="maturity-promotion-001"))
            report = repo.evaluate()
        self.assertIn(check.KIND_UNJUDGED, self.kinds(report))
        self.assertEqual(report.exit_code, 1)
        finding = next(f for f in report.findings if f.kind == check.KIND_UNJUDGED)
        self.assertEqual(finding.trigger_key, "operation-since-made-ineligible")
        self.assertIn(LADDER_RELATIVE, finding.entry)


class SupersedesTests(FixtureCase):
    """A correction is a new entry, and the superseding entry is authoritative."""

    def test_a_superseded_entry_is_not_judged(self):
        self.repo.add_entry(entry(run_id="cadence-snapshot-001", paths_written=[WRITTEN_PATH, "docs/DECISIONS.md"]))
        self.repo.add_entry(entry(run_id="cadence-snapshot-002", supersedes="cadence-snapshot-001"))
        report = self.repo.evaluate()
        self.assertEqual(report.findings, [])
        self.assertEqual(report.exit_code, 0)
        self.assertEqual(len(report.superseded_skipped), 1)
        self.assertEqual(report.superseded_skipped[0][1], "cadence-snapshot-002")

    def test_a_chain_leaves_only_the_last_entry_authoritative(self):
        self.repo.add_entry(entry(run_id="cadence-snapshot-001"))
        self.repo.add_entry(entry(run_id="cadence-snapshot-002", supersedes="cadence-snapshot-001"))
        self.repo.add_entry(
            entry(
                run_id="cadence-snapshot-003",
                supersedes="cadence-snapshot-002",
                paths_written=[WRITTEN_PATH, "docs/NON_GOALS.md"],
            )
        )
        report = self.repo.evaluate()
        self.assertEqual(len(report.runs_evaluated), 1)
        self.assertIn("cadence-snapshot-003", report.runs_evaluated[0])
        self.assertIn("write-outside-scope", self.fired_keys(report))
        finding = next(f for f in report.findings if f.trigger_key == "write-outside-scope")
        self.assertIn("docs/NON_GOALS.md", finding.observed)

    def test_the_superseding_entry_is_still_judged(self):
        self.repo.add_entry(entry(run_id="cadence-snapshot-001"))
        self.repo.add_entry(
            entry(
                run_id="cadence-snapshot-002",
                supersedes="cadence-snapshot-001",
                paths_written=[WRITTEN_PATH, "docs/DECISIONS.md"],
            )
        )
        self.assertIn("write-outside-scope", self.fired_keys(self.repo.evaluate()))


class CatalogDisagreementTests(FixtureCase):
    """One of the two records changed after the run, and a human says which."""

    def test_a_scope_that_disagrees_with_the_catalog_is_reported(self):
        self.repo.add_entry(entry(write_scope=["ops/status/*.md", "release/briefs/*.md"]))
        report = self.repo.evaluate()
        self.assertIn(check.KIND_DISAGREEMENT, self.kinds(report))
        self.assertEqual(report.exit_code, 1)
        finding = next(f for f in report.findings if f.kind == check.KIND_DISAGREEMENT)
        self.assertIn("release/briefs/*.md", finding.observed)
        self.assertIn("ops/status/*.md", finding.declared)
        self.assertEqual(finding.operation, "cadence-snapshot")

    def test_an_operation_the_catalog_no_longer_lists_is_reported(self):
        self.repo.write_catalog({"schema_version": 1, "operations": []})
        self.repo.add_entry(entry())
        report = self.repo.evaluate()
        finding = next(f for f in report.findings if f.kind == check.KIND_DISAGREEMENT)
        self.assertIn("no operation `cadence-snapshot`", finding.declared)

    def test_a_matching_scope_is_not_reported(self):
        self.repo.add_entry(entry())
        self.assertNotIn(check.KIND_DISAGREEMENT, self.kinds(self.repo.evaluate()))

    def test_a_disagreement_is_not_labelled_a_demotion_trigger(self):
        self.repo.add_entry(entry(write_scope=["ops/status/*.md", "release/briefs/*.md"]))
        report = self.repo.evaluate()
        self.assertEqual(self.fired_keys(report), [], "a record disagreement demotes nothing by itself")
        text = check.render(report)
        self.assertIn("DISAGREEMENT", text)
        self.assertIn("Not a ladder trigger", text)
        self.assertNotIn("FIRED", text)


class UnreadableEntryTests(FixtureCase):
    """A record this check cannot read is unjudged, never clear."""

    def test_an_entry_without_front_matter_is_unjudged(self):
        self.repo.add_raw_entry("2026-09-02-broken.md", "# A run with no front matter\n")
        report = self.repo.evaluate()
        self.assertIn(check.KIND_UNJUDGED, self.kinds(report))
        self.assertEqual(report.exit_code, 1)
        self.assertIn("front matter", report.findings[0].observed)

    def test_an_entry_with_broken_yaml_is_unjudged(self):
        self.repo.add_raw_entry("2026-09-02-broken.md", "---\nrun_id: [unclosed\n---\n\n# Run\n")
        report = self.repo.evaluate()
        self.assertIn(check.KIND_UNJUDGED, self.kinds(report))
        text = check.render(report)
        self.assertIn("UNJUDGED", text)
        self.assertIn("Not a fired trigger", text)
        self.assertIn("scripts/ledger.py validate", text)

    def test_the_directory_readme_is_not_an_entry(self):
        (self.repo.root / "ops" / "ledger" / "README.md").write_text("# Ledger\n", encoding="utf-8")
        report = self.repo.evaluate()
        self.assertEqual(report.findings, [])
        self.assertEqual(report.files_read, [])


class SampleEntryTests(FixtureCase):
    """A hypothetical worked example is a document, not a run."""

    def test_a_sample_entry_is_reported_and_not_judged(self):
        path = self.repo.add_entry(entry(paths_written=[WRITTEN_PATH, "docs/DECISIONS.md"]))
        path.rename(path.parent / "SAMPLE_run.md")
        report = self.repo.evaluate()
        self.assertEqual(report.findings, [])
        self.assertEqual(report.runs_evaluated, [])
        self.assertEqual(report.samples_skipped, ["ops/ledger/SAMPLE_run.md"])
        self.assertIn("SAMPLE_run.md", check.render(report))


class OutputTests(FixtureCase):
    """The text report and the JSON report say the same things."""

    def test_json_shape(self):
        self.repo.add_entry(entry(paths_written=[WRITTEN_PATH, "docs/DECISIONS.md"]))
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.repo.root), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(
            sorted(payload),
            [
                "detects_only",
                "exit_code",
                "finding_counts",
                "findings",
                "ladder",
                "ledger",
                "limits",
                "notes",
                "root",
                "trigger_counts",
                "triggers",
            ],
        )
        self.assertEqual(payload["exit_code"], 1)
        self.assertEqual(payload["ladder"], LADDER_RELATIVE)
        self.assertEqual(
            sorted(payload["trigger_counts"]), ["evaluable_here", "not_evaluable_here", "total"]
        )
        self.assertEqual(
            payload["trigger_counts"]["total"],
            payload["trigger_counts"]["evaluable_here"]
            + payload["trigger_counts"]["not_evaluable_here"],
        )
        self.assertEqual(
            sorted(payload["ledger"]),
            ["directory", "files_read", "runs_evaluated", "samples_skipped", "superseded_skipped"],
        )
        self.assertEqual(payload["finding_counts"]["demotion-trigger"], 1)
        finding = payload["findings"][0]
        self.assertEqual(
            sorted(finding),
            [
                "claimed_level",
                "clause",
                "declared",
                "entry",
                "kind",
                "level",
                "next_step",
                "observed",
                "operation",
                "operation_demoted_to",
                "run_id",
                "trigger_id",
                "trigger_key",
            ],
        )
        self.assertEqual(finding["operation"], "cadence-snapshot")
        self.assertEqual(finding["operation_demoted_to"], "A2")
        for item in payload["triggers"]:
            with self.subTest(trigger=item["id"]):
                self.assertEqual(
                    sorted(item),
                    ["basis", "clause", "demotes_to", "detector", "evaluable_here", "id", "key", "level", "reason"],
                )

    def test_json_is_deterministic(self):
        self.repo.add_entry(entry(paths_written=[WRITTEN_PATH, "docs/DECISIONS.md"]))
        outputs = {
            subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(self.repo.root), "--json"],
                capture_output=True,
                text=True,
                check=False,
            ).stdout
            for _ in range(2)
        }
        self.assertEqual(len(outputs), 1)

    def test_a_fired_report_is_actionable_without_the_ladder(self):
        self.repo.add_entry(entry(paths_written=[WRITTEN_PATH, "docs/DECISIONS.md"]))
        text = check.render(self.repo.evaluate())
        self.assertIn("FIRED", text)
        self.assertIn("docs/DECISIONS.md", text)
        self.assertIn("cadence-snapshot", text)
        self.assertIn("would be demoted from A3 to A2", text)
        self.assertIn("2026-09-02-cadence-snapshot-001.md", text)

    def test_both_renderings_say_the_check_does_not_demote(self):
        self.repo.add_entry(entry())
        report = self.repo.evaluate()
        self.assertIn("does not demote", check.render(report))
        self.assertIn("does not demote", report.to_json()["detects_only"])
        self.assertIn("promotions.yaml", report.to_json()["detects_only"])

    def test_every_trigger_appears_in_the_text_report(self):
        report = self.repo.evaluate()
        text = check.render(report)
        for item in report.triggers:
            with self.subTest(trigger=item.trigger.trigger_id):
                self.assertIn(f"[{item.trigger.trigger_id}]", text)

    def test_a_bad_root_is_a_usage_error(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.repo.root / "nowhere")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a directory", result.stderr)


class ShippedRepositoryTests(unittest.TestCase):
    """The invariant: on the tree this repository ships, nothing has fired."""

    def test_shipped_tree_fires_nothing_for_the_right_reason(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(REPOSITORY_ROOT), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["findings"], [])
        # The right reason: triggers were enumerated and some are evaluable, and
        # the ledger holds no recorded run for them to judge.
        self.assertGreaterEqual(payload["trigger_counts"]["total"], 8)
        self.assertGreaterEqual(payload["trigger_counts"]["evaluable_here"], 1)
        self.assertEqual(payload["ledger"]["runs_evaluated"], [])
        self.assertEqual(payload["ledger"]["samples_skipped"], ["ops/ledger/SAMPLE_run.md"])

    def test_the_shipped_report_says_no_run_has_left_a_record(self):
        report = check.evaluate(REPOSITORY_ROOT)
        text = check.render(report)
        self.assertIn("NO TRIGGER FIRED", text)
        self.assertIn("No run has left a record", text)

    def test_the_check_writes_nothing(self):
        """It reports and never demotes, so it changes no file - the ledger included."""
        watched = [
            REPOSITORY_ROOT / "ops" / "ledger",
            REPOSITORY_ROOT / "ops" / "autonomy",
        ]

        def snapshot():
            state = {}
            for directory in watched:
                for path in sorted(directory.rglob("*")):
                    if path.is_file():
                        state[str(path)] = path.stat().st_mtime_ns, path.stat().st_size
            return state

        before = snapshot()
        check.evaluate(REPOSITORY_ROOT)
        subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(REPOSITORY_ROOT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(snapshot(), before)


if __name__ == "__main__":
    unittest.main()
