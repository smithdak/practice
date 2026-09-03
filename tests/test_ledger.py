from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ledger = load_module("practice_ledger", REPOSITORY_ROOT / "scripts" / "ledger.py")

BODY = "\n# Hypothetical run\n\nWhat ran, what it wrote, and how to undo it.\n"

# The entry the shipped substrate produces: a run the guard refused.
BASE_ENTRY = {
    "ledger_schema_version": 1,
    "run_id": "cadence-snapshot-001",
    "run_date": "2026-09-02",
    "operation": "cadence-snapshot",
    "actor": "scheduled-workflow",
    "claimed_level": "A3",
    "trigger": "schedule",
    "kill_switch": "engaged",
    "promotion": "none",
    "preconditions": [
        {
            "check": "operation-in-catalog",
            "result": "pass",
            "detail": "cadence-snapshot is listed in the operation catalog.",
        },
        {
            "check": "promotion-signed",
            "result": "fail",
            "detail": "No promotion is recorded for cadence-snapshot.",
        },
    ],
    "command": ["python3", "scripts/cadence.py", "--root", "."],
    "write_scope": ["ops/status/*.md"],
    "paths_read": ["ops/autonomy/promotions.yaml"],
    "paths_written": [],
    "reversal": "Nothing was written, so there is nothing to undo.",
    "outcome": "refused",
}

WRITTEN_PATH = "ops/status/2026-09-02-cadence.md"

COMPLETED_OVERRIDES = {
    "kill_switch": "released",
    "promotion": {
        "level": "A3",
        "signed_by": "founder",
        "signed_on": "2026-09-02",
        "review_point": "2026-12-02",
    },
    "preconditions": [
        {
            "check": "promotion-signed",
            "result": "pass",
            "detail": "A promotion for cadence-snapshot at A3 is recorded.",
        },
    ],
    "paths_written": [WRITTEN_PATH],
    "reversal": "Delete the written status file, or close the pull request without merging.",
    "outcome": "completed",
}


class _Remove:
    """Sentinel: passing it as an override deletes that field from the entry."""


REMOVE = _Remove()


def build_root(directory: str) -> Path:
    """A temporary repository root holding the paths a completed entry points at."""
    root = Path(directory)
    (root / "ops" / "ledger").mkdir(parents=True, exist_ok=True)
    (root / "ops" / "status").mkdir(parents=True, exist_ok=True)
    (root / "ops" / "status" / "2026-09-02-cadence.md").write_text("# fixture\n", encoding="utf-8")
    return root


def entry_text(entry: dict, body: str = BODY) -> str:
    front_matter = yaml.safe_dump(entry, sort_keys=False, default_flow_style=False, allow_unicode=True)
    return f"---\n{front_matter}---{body}"


def build_entry(**overrides) -> dict:
    entry = copy.deepcopy(BASE_ENTRY)
    entry.update(overrides)
    for key in [key for key, value in entry.items() if isinstance(value, _Remove)]:
        del entry[key]
    return entry


def write_entry(root: Path, name: str | None = None, **overrides) -> Path:
    body = overrides.pop("body", BODY)
    entry = build_entry(**overrides)
    if name is None:
        name = f"{entry.get('run_date', 'undated')}-{entry.get('run_id', 'unnamed')}.md"
    path = root / "ops" / "ledger" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(entry_text(entry, body), encoding="utf-8")
    return path


def violations(root: Path, path: Path) -> list[str]:
    return ledger.validate_entry_file(path, root)


def write_catalog(root: Path, ids=("cadence-snapshot", "metrics-snapshot")) -> None:
    path = root / "ops" / "autonomy" / "operations.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": 1, "operations": [{"id": name} for name in ids]}
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


class RequiredFieldTests(unittest.TestCase):
    def test_the_refused_entry_validates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            self.assertEqual(violations(root, write_entry(root)), [])

    def test_every_required_field_is_required(self):
        for field in ledger.REQUIRED_FIELDS:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = build_root(directory)
                path = write_entry(root, name="2026-09-02-cadence-snapshot-001.md", **{field: REMOVE})
                found = violations(root, path)
                self.assertTrue(found, f"removing {field} produced no violation")
                self.assertTrue(
                    any(f": {field}:" in message for message in found),
                    f"no violation named {field}: {found}",
                )

    def test_unknown_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, approved_by="founder")
            self.assertTrue(any("is not an action ledger field" in message for message in violations(root, path)))

    def test_schema_version_must_be_the_version_this_checker_reads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, ledger_schema_version=2)
            self.assertTrue(any("ledger_schema_version" in message for message in violations(root, path)))

    def test_missing_front_matter_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = root / "ops" / "ledger" / "2026-09-02-cadence-snapshot-001.md"
            path.write_text("# No front matter\n", encoding="utf-8")
            self.assertTrue(any("no YAML front matter" in message for message in violations(root, path)))

    def test_body_must_carry_a_title(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            empty = write_entry(root, name="2026-09-02-cadence-snapshot-001.md", body="\n")
            self.assertTrue(any("has no run record" in message for message in violations(root, empty)))
            untitled = write_entry(root, name="2026-09-02-cadence-snapshot-002.md", run_id="cadence-snapshot-002", body="\nplain prose\n")
            self.assertTrue(any("has no H1 title" in message for message in violations(root, untitled)))


class LevelVocabularyTests(unittest.TestCase):
    def test_every_ladder_level_is_accepted(self):
        for level in ledger.LEVEL_ORDER:
            with self.subTest(level=level), tempfile.TemporaryDirectory() as directory:
                root = build_root(directory)
                self.assertEqual(violations(root, write_entry(root, claimed_level=level)), [])

    def test_a_level_outside_the_ladder_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, claimed_level="A4")
            found = violations(root, path)
            self.assertTrue(any("is not an autonomy level" in message for message in found))
            self.assertTrue(any("A0, A1, A2, A3" in message for message in found))

    def test_a_packet_autonomy_value_is_not_a_level_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, claimed_level="recommend")
            self.assertTrue(any("is not an autonomy level" in message for message in violations(root, path)))


class ReversalTests(unittest.TestCase):
    def test_an_entry_missing_its_reversal_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, reversal=REMOVE)
            self.assertTrue(any(": reversal:" in message for message in violations(root, path)))

    def test_a_placeholder_reversal_fails(self):
        for placeholder in ("n/a", "none", "TBD", "-"):
            with self.subTest(value=placeholder), tempfile.TemporaryDirectory() as directory:
                root = build_root(directory)
                path = write_entry(root, reversal=placeholder)
                self.assertTrue(any("is a placeholder" in message for message in violations(root, path)))

    def test_a_reversal_too_short_to_read_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, reversal="undo it")
            self.assertTrue(any("too short" in message for message in violations(root, path)))


class PreconditionTests(unittest.TestCase):
    def test_an_entry_with_no_preconditions_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, preconditions=[])
            self.assertTrue(any("records no check" in message for message in violations(root, path)))

    def test_a_precondition_needs_a_check_a_result_and_a_detail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, preconditions=[{"check": "promotion-signed"}])
            found = violations(root, path)
            self.assertTrue(any("preconditions[0].result" in message for message in found))
            self.assertTrue(any("preconditions[0].detail" in message for message in found))

    def test_a_precondition_result_is_pass_or_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(
                root,
                preconditions=[{"check": "promotion-signed", "result": "maybe", "detail": "It was unclear."}],
            )
            self.assertTrue(any("is not a precondition result" in message for message in violations(root, path)))

    def test_a_repeated_check_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            twice = [
                {"check": "promotion-signed", "result": "fail", "detail": "No promotion is recorded."},
                {"check": "promotion-signed", "result": "pass", "detail": "A promotion is recorded."},
            ]
            path = write_entry(root, preconditions=twice)
            self.assertTrue(any("is recorded twice" in message for message in violations(root, path)))

    def test_a_placeholder_detail_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(
                root,
                preconditions=[{"check": "promotion-signed", "result": "fail", "detail": "TBD"}],
            )
            self.assertTrue(any("is a placeholder" in message for message in violations(root, path)))

    def test_a_refusal_names_the_precondition_that_failed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            passing = [{"check": "promotion-signed", "result": "pass", "detail": "A promotion is recorded."}]
            path = write_entry(root, preconditions=passing)
            self.assertTrue(any("records no failed check" in message for message in violations(root, path)))


class PathAndOutcomeTests(unittest.TestCase):
    def test_a_completed_entry_whose_written_path_is_absent_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            overrides = dict(COMPLETED_OVERRIDES)
            overrides["paths_written"] = ["ops/status/never-written.md"]
            path = write_entry(root, **overrides)
            found = violations(root, path)
            self.assertTrue(any("does not exist under the root" in message for message in found))

    def test_a_completed_entry_whose_written_path_exists_validates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            self.assertEqual(violations(root, write_entry(root, **COMPLETED_OVERRIDES)), [])

    def test_a_failed_run_may_name_a_path_that_is_no_longer_there(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            overrides = dict(COMPLETED_OVERRIDES)
            overrides["outcome"] = "failed"
            overrides["paths_written"] = ["ops/status/partial.md"]
            self.assertEqual(violations(root, write_entry(root, **overrides)), [])

    def test_a_refused_or_dry_run_cannot_have_written_anything(self):
        for outcome in ("refused", "dry-run"):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as directory:
                root = build_root(directory)
                path = write_entry(root, outcome=outcome, paths_written=[WRITTEN_PATH])
                self.assertTrue(any("says the run wrote nothing" in message for message in violations(root, path)))

    def test_paths_are_repository_relative(self):
        for bad in ("/etc/passwd", "../outside.md", "ops\\status\\file.md"):
            with self.subTest(path=bad), tempfile.TemporaryDirectory() as directory:
                root = build_root(directory)
                overrides = dict(COMPLETED_OVERRIDES)
                overrides["paths_written"] = [bad]
                path = write_entry(root, **overrides)
                self.assertTrue(violations(root, path))

    def test_a_written_path_is_a_path_and_a_write_scope_is_a_pattern(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            overrides = dict(COMPLETED_OVERRIDES)
            overrides["paths_written"] = ["ops/status/*.md"]
            path = write_entry(root, **overrides)
            self.assertTrue(any("is a pattern, not a path" in message for message in violations(root, path)))

    def test_an_out_of_scope_write_is_recorded_not_rejected(self):
        """The ledger records what happened; the demotion check judges it."""
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            (root / "community").mkdir(parents=True, exist_ok=True)
            (root / "community" / "GOVERNANCE.md").write_text("# fixture\n", encoding="utf-8")
            overrides = dict(COMPLETED_OVERRIDES)
            overrides["paths_written"] = [WRITTEN_PATH, "community/GOVERNANCE.md"]
            self.assertEqual(violations(root, write_entry(root, **overrides)), [])

    def test_an_unknown_outcome_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, outcome="ok")
            self.assertTrue(any("is not an outcome" in message for message in violations(root, path)))

    def test_an_unknown_trigger_or_kill_switch_state_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, trigger="webhook", kill_switch="off")
            found = violations(root, path)
            self.assertTrue(any("is not a trigger" in message for message in found))
            self.assertTrue(any("is not a kill-switch state" in message for message in found))


class PromotionTests(unittest.TestCase):
    def test_none_records_that_no_promotion_was_found(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            self.assertEqual(violations(root, write_entry(root, promotion="none")), [])

    def test_a_promotion_mapping_needs_level_signer_date_and_review_point(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, promotion={"level": "A3"})
            found = violations(root, path)
            self.assertTrue(any("promotion.signed_by" in message for message in found))
            self.assertTrue(any("promotion.signed_on" in message for message in found))
            self.assertTrue(any("promotion.review_point" in message for message in found))

    def test_a_promotion_without_a_review_point_is_rejected(self):
        """The ladder's review-point trigger is checkable only from the entry."""
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            promotion = dict(COMPLETED_OVERRIDES["promotion"])
            del promotion["review_point"]
            path = write_entry(root, **dict(COMPLETED_OVERRIDES, promotion=promotion))
            found = violations(root, path)
            self.assertTrue(any("promotion.review_point" in message and "is missing" in message for message in found))
            self.assertEqual([m for m in found if "promotion.review_point" not in m], [])

    def test_the_review_point_is_required_by_the_schema_constants(self):
        self.assertIn("review_point", ledger.PROMOTION_REQUIRED)
        self.assertEqual(ledger.PROMOTION_OPTIONAL, ())

    def test_promotion_none_needs_no_review_point(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            self.assertEqual(violations(root, write_entry(root, promotion="none")), [])

    def test_a_promotion_level_outside_the_ladder_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(
                root,
                promotion=dict(COMPLETED_OVERRIDES["promotion"], level="A9"),
            )
            found = violations(root, path)
            self.assertTrue(any("promotion.level" in message for message in found))
            self.assertEqual([m for m in found if "promotion.level" not in m], [])

    def test_an_unknown_promotion_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(
                root,
                promotion=dict(COMPLETED_OVERRIDES["promotion"], approved=True),
            )
            found = violations(root, path)
            self.assertTrue(any("promotion.approved" in message for message in found))
            self.assertEqual([m for m in found if "promotion.approved" not in m], [])

    def test_the_default_body_names_the_review_point_of_a_recorded_promotion(self):
        text = ledger.default_body(build_entry(**COMPLETED_OVERRIDES))
        self.assertIn("review point 2026-12-02", text)

    def test_a_review_point_must_be_a_date(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(
                root,
                promotion={
                    "level": "A3",
                    "signed_by": "founder",
                    "signed_on": "2026-09-02",
                    "review_point": "in three months",
                },
            )
            self.assertTrue(any("promotion.review_point" in message for message in violations(root, path)))

    def test_a_promotion_that_is_neither_none_nor_a_mapping_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, promotion="signed")
            self.assertTrue(any("is not a promotion record" in message for message in violations(root, path)))


class NamingTests(unittest.TestCase):
    def test_the_file_name_carries_the_run_date_and_run_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, name="cadence.md")
            found = violations(root, path)
            self.assertTrue(any("file name" in message for message in found))
            self.assertTrue(any("2026-09-02-cadence-snapshot-001.md" in message for message in found))

    def test_a_sample_file_is_exempt_from_the_name_rule(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            self.assertEqual(violations(root, write_entry(root, name="SAMPLE_run.md")), [])

    def test_a_run_id_is_a_slug(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, name="2026-09-02-run.md", run_id="Cadence Snapshot 1")
            self.assertTrue(any("is not a run id" in message for message in violations(root, path)))

    def test_two_entries_may_not_share_a_run_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            write_entry(root)
            write_entry(root, name="2026-09-03-cadence-snapshot-001.md", run_date="2026-09-03")
            seen: dict[str, str] = {}
            found: list[str] = []
            for path in sorted((root / "ops" / "ledger").glob("*.md")):
                found.extend(ledger.validate_entry_file(path, root, seen))
            self.assertTrue(any("is already used by" in message for message in found))

    def test_supersedes_names_another_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, supersedes="cadence-snapshot-001")
            self.assertTrue(any("names this entry" in message for message in violations(root, path)))
            fine = write_entry(
                root,
                name="2026-09-02-cadence-snapshot-002.md",
                run_id="cadence-snapshot-002",
                supersedes="cadence-snapshot-001",
            )
            self.assertEqual(violations(root, fine), [])


class PrivacyTests(unittest.TestCase):
    def test_an_email_address_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, body="\n# Run\n\nReported to maintainer@example.invalid.\n")
            self.assertTrue(any("contains an email address" in message for message in violations(root, path)))

    def test_a_handle_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, body="\n# Run\n\nRequested by @practitioner.\n")
            self.assertTrue(any("contains a handle" in message for message in violations(root, path)))


class CatalogTests(unittest.TestCase):
    def test_an_operation_absent_from_the_catalog_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            write_catalog(root)
            path = write_entry(root, operation="delete-everything")
            self.assertTrue(any("is not an operation in" in message for message in violations(root, path)))

    def test_an_operation_in_the_catalog_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            write_catalog(root)
            self.assertEqual(violations(root, write_entry(root)), [])

    def test_the_check_is_skipped_when_the_catalog_is_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            self.assertIsNone(ledger.catalog_operation_ids(root))
            self.assertEqual(violations(root, write_entry(root, operation="not-yet-catalogued")), [])


class AppendInterfaceTests(unittest.TestCase):
    def test_append_round_trips_through_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            entry = build_entry()
            written = ledger.append_entry(entry, root=root)
            self.assertEqual(written.name, "2026-09-02-cadence-snapshot-001.md")
            self.assertEqual(written.parent, root / "ops" / "ledger")
            self.assertEqual(violations(root, written), [])
            front_matter, _body = ledger.split_front_matter(written.read_text(encoding="utf-8"))
            self.assertEqual(yaml.safe_load(front_matter), entry)

    def test_append_does_not_mutate_the_caller_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            entry = build_entry()
            before = copy.deepcopy(entry)
            ledger.append_entry(entry, root=root)
            self.assertEqual(entry, before)

    def test_the_default_body_states_what_the_entry_is_not(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            written = ledger.append_entry(build_entry(), root=root)
            text = written.read_text(encoding="utf-8")
            self.assertIn("It is not a permission", text)
            self.assertIn("append-only", text)
            self.assertIn("Nothing was written, so there is nothing to undo.", text)

    def test_a_caller_supplied_body_is_written_verbatim(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            written = ledger.append_entry(build_entry(), root=root, body="# Run record\n\nOne paragraph.\n")
            self.assertIn("One paragraph.", written.read_text(encoding="utf-8"))

    def test_append_refuses_to_overwrite_an_existing_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            written = ledger.append_entry(build_entry(), root=root, body="# First\n\nOriginal record.\n")
            with self.assertRaises(ledger.LedgerError) as raised:
                ledger.append_entry(build_entry(), root=root, body="# Second\n\nReplacement.\n")
            self.assertIn("append-only", str(raised.exception))
            self.assertIn("Original record.", written.read_text(encoding="utf-8"))

    def test_append_writes_nothing_when_the_entry_is_invalid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            with self.assertRaises(ledger.LedgerError) as raised:
                ledger.append_entry(build_entry(reversal=REMOVE), root=root)
            self.assertTrue(any(": reversal:" in message for message in raised.exception.violations))
            self.assertIn("reversal", raised.exception.report())
            self.assertEqual(list((root / "ops" / "ledger").glob("*.md")), [])

    def test_append_creates_the_ledger_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            written = ledger.append_entry(build_entry(), root=root)
            self.assertTrue(written.is_file())

    def test_append_accepts_an_explicit_ledger_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            target = root / "ops" / "ledger" / "2026"
            written = ledger.append_entry(build_entry(), ledger_dir=target, root=root)
            self.assertEqual(written.parent, target)

    def test_next_run_id_counts_from_the_entries_already_there(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            self.assertEqual(ledger.next_run_id("cadence-snapshot", root=root), "cadence-snapshot-001")
            ledger.append_entry(build_entry(), root=root)
            self.assertEqual(ledger.next_run_id("cadence-snapshot", root=root), "cadence-snapshot-002")
            self.assertEqual(ledger.next_run_id("metrics-snapshot", root=root), "metrics-snapshot-001")

    def test_render_entry_orders_the_front_matter_canonically(self):
        entry = build_entry()
        shuffled = {key: entry[key] for key in reversed(list(entry))}
        text = ledger.render_entry(shuffled, body=BODY)
        front_matter, _body = ledger.split_front_matter(text)
        self.assertEqual(list(yaml.safe_load(front_matter)), [key for key in ledger.FIELD_ORDER if key in entry])


class CommittedSampleTests(unittest.TestCase):
    def setUp(self):
        self.sample = REPOSITORY_ROOT / "ops" / "ledger" / "SAMPLE_run.md"

    def test_the_committed_sample_validates(self):
        self.assertEqual(ledger.validate_entry_file(self.sample, REPOSITORY_ROOT), [])

    def test_the_committed_ledger_directory_validates(self):
        code, out, err = run_cli(["validate", str(REPOSITORY_ROOT / "ops" / "ledger"), "--root", str(REPOSITORY_ROOT)])
        self.assertEqual(code, 0, err)
        self.assertIn("violation(s)", out)

    def test_the_sample_depicts_a_refused_run_and_no_promotion(self):
        front_matter, _body = ledger.split_front_matter(self.sample.read_text(encoding="utf-8"))
        data = yaml.safe_load(front_matter)
        self.assertEqual(data["outcome"], "refused")
        self.assertEqual(data["paths_written"], [])
        self.assertEqual(data["kill_switch"], "engaged")
        self.assertEqual(data["promotion"], "none")

    def test_the_sample_is_labeled_hypothetical(self):
        text = self.sample.read_text(encoding="utf-8")
        self.assertIn("hypothetical", text.lower())


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = ledger.main(argv)
    return code, out.getvalue(), err.getvalue()


class CommandLineTests(unittest.TestCase):
    def test_a_valid_entry_exits_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root)
            code, out, _err = run_cli(["validate", str(path), "--root", str(root)])
            self.assertEqual(code, 0)
            self.assertIn("0 violation(s)", out)
            self.assertIn("not a permission", out)

    def test_a_violation_exits_one(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root, reversal=REMOVE)
            code, _out, err = run_cli(["validate", str(path), "--root", str(root)])
            self.assertEqual(code, 1)
            self.assertIn("reversal", err)

    def test_a_missing_path_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            code, _out, err = run_cli(["validate", str(root / "absent.md"), "--root", str(root)])
            self.assertEqual(code, 2)
            self.assertIn("usage error", err)

    def test_a_missing_root_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_entry(root)
            code, _out, err = run_cli(["validate", str(path), "--root", str(root / "absent")])
            self.assertEqual(code, 2)
            self.assertIn("usage error", err)

    def test_no_subcommand_is_a_usage_error(self):
        with self.assertRaises(SystemExit) as raised:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                ledger.main([])
        self.assertEqual(raised.exception.code, 2)

    def test_an_empty_ledger_is_the_expected_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            code, out, _err = run_cli(["validate", str(root / "ops" / "ledger"), "--root", str(root)])
            self.assertEqual(code, 0)
            self.assertIn("Checked 0 ledger entries", out)
            self.assertIn("expected state", out)

    def test_directory_expansion_skips_the_readme(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            write_entry(root)
            (root / "ops" / "ledger" / "README.md").write_text("# Not an entry\n", encoding="utf-8")
            code, out, _err = run_cli(["validate", str(root / "ops" / "ledger"), "--root", str(root)])
            self.assertEqual(code, 0)
            self.assertIn("Checked 1 ledger entry(s)", out)

    def test_append_from_a_json_file_writes_one_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            source = root / "run.json"
            source.write_text(json.dumps(build_entry()), encoding="utf-8")
            code, out, _err = run_cli(["append", "--entry", str(source), "--root", str(root)])
            self.assertEqual(code, 0)
            self.assertEqual(out.strip(), "ops/ledger/2026-09-02-cadence-snapshot-001.md")
            self.assertTrue((root / "ops" / "ledger" / "2026-09-02-cadence-snapshot-001.md").is_file())

    def test_append_from_standard_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            saved = sys.stdin
            sys.stdin = io.StringIO(json.dumps(build_entry()))
            try:
                code, out, _err = run_cli(["append", "--entry", "-", "--root", str(root)])
            finally:
                sys.stdin = saved
            self.assertEqual(code, 0)
            self.assertIn("2026-09-02-cadence-snapshot-001.md", out)

    def test_append_with_a_body_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            source = root / "run.json"
            source.write_text(json.dumps(build_entry()), encoding="utf-8")
            body = root / "body.md"
            body.write_text("# Run record\n\nWritten by the runner.\n", encoding="utf-8")
            code, _out, _err = run_cli(
                ["append", "--entry", str(source), "--body-file", str(body), "--root", str(root)]
            )
            self.assertEqual(code, 0)
            written = root / "ops" / "ledger" / "2026-09-02-cadence-snapshot-001.md"
            self.assertIn("Written by the runner.", written.read_text(encoding="utf-8"))

    def test_append_of_an_invalid_entry_exits_one(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            source = root / "run.json"
            source.write_text(json.dumps(build_entry(preconditions=[])), encoding="utf-8")
            code, _out, err = run_cli(["append", "--entry", str(source), "--root", str(root)])
            self.assertEqual(code, 1)
            self.assertIn("records no check", err)
            self.assertEqual(list((root / "ops" / "ledger").glob("*.md")), [])

    def test_append_of_a_missing_entry_file_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            code, _out, err = run_cli(["append", "--entry", str(root / "absent.json"), "--root", str(root)])
            self.assertEqual(code, 2)
            self.assertIn("usage error", err)


if __name__ == "__main__":
    unittest.main()
