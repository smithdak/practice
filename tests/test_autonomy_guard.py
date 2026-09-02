"""Failure-mode coverage for scripts/autonomy_guard.py.

Most tests build a synthetic repository in a temporary directory, break exactly
one precondition, and assert that the guard refuses and names it. Two things
those fixtures cannot prove are tested against the real repository instead:

- the safety invariant, ``test_shipped_records_refuse_every_operation``: with
  the records this repository actually ships, all five catalogued operations are
  refused. That is the most important test in this file. A change that makes it
  pass silently would mean something in this repository can act on its own;
- that the guard can permit at all. ``test_complete_bound_is_permitted`` builds
  a fully signed fixture and expects exit 0, so a guard that refused
  unconditionally - which would pass every other test here - fails.
"""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
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
    # Registered before execution so the module's dataclasses can resolve their
    # own annotations, which `from __future__ import annotations` defers.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


guard = load_module("practice_autonomy_guard", REPOSITORY_ROOT / "scripts" / "autonomy_guard.py")


AS_OF = "2026-09-02"

CATALOGUED_OPERATIONS = (
    "cadence-snapshot",
    "metrics-snapshot",
    "contract-drift-check",
    "staleness-sweep",
    "release-brief-draft",
)

CATALOG_ENTRY = {
    "id": "cadence-snapshot",
    "summary": "Run the cadence report and write a dated status file.",
    "command": ["python3", "scripts/cadence.py", "--root", "."],
    "write_scope": ["ops/status/*.md"],
    "reversal": "Delete the written file, or close the pull request unmerged.",
    "blast_radius": "One new file in the repository. No member contact.",
    "level": "A1",
}

PROMOTION = {
    "operation": "cadence-snapshot",
    "level": "A3",
    "write_scope": ["ops/status/*.md"],
    "evidence": ["evidence/promotion-record.md"],
    "demotion_triggers": ["wrote outside write_scope", "guard precondition failed"],
    "signed_by": "founder",
    "signed_on": AS_OF,
}

LADDER_HEADER = """# Autonomy Ladder (fixture)

## Permanently ineligible for A3

| Operation id | Operation | Why it is permanently ineligible | Where recorded |
|---|---|---|---|
"""


def ladder_text(ineligible=None) -> str:
    ids = guard.INELIGIBLE_OPERATIONS if ineligible is None else ineligible
    rows = "".join(f"| `{item}` | text | reason | record |\n" for item in ids)
    return f"{LADDER_HEADER}{rows}\n## Action vocabulary\n\nUnrelated section.\n"


def catalog(entries=None) -> dict:
    return {
        "schema_version": 1,
        "operations": copy.deepcopy(entries) if entries is not None else [copy.deepcopy(CATALOG_ENTRY)],
    }


def promotions(kill_switch: str = "released", entries=None, schema_version: int = 1) -> dict:
    return {
        "schema_version": schema_version,
        "kill_switch": kill_switch,
        "promotions": copy.deepcopy(entries) if entries is not None else [copy.deepcopy(PROMOTION)],
    }


class GuardTestCase(unittest.TestCase):
    """Shared fixture builder: a repository root with exactly one thing wrong."""

    def build(self, *, catalog_record=None, promotions_record=None, ladder=None) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "ops" / "autonomy").mkdir(parents=True)
        (root / "docs" / "framework").mkdir(parents=True)
        (root / "scripts").mkdir(parents=True)
        (root / "evidence").mkdir(parents=True)
        (root / "scripts" / "cadence.py").write_text("print('fixture')\n", encoding="utf-8")
        (root / "evidence" / "promotion-record.md").write_text("# Fixture evidence\n", encoding="utf-8")
        (root / "docs" / "framework" / "AUTONOMY_LADDER.md").write_text(
            ladder_text() if ladder is None else ladder, encoding="utf-8"
        )
        self.write_yaml(root / "ops" / "autonomy" / "operations.yaml", catalog() if catalog_record is None else catalog_record)
        self.write_yaml(
            root / "ops" / "autonomy" / "promotions.yaml",
            promotions() if promotions_record is None else promotions_record,
        )
        return root

    @staticmethod
    def write_yaml(path: Path, value) -> None:
        if isinstance(value, str):
            path.write_text(value, encoding="utf-8")
        elif value is None:
            if path.exists():
                path.unlink()
        else:
            path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")

    def run_guard(self, root: Path, operation: str = "cadence-snapshot", as_of: str = AS_OF):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = guard.main(["--operation", operation, "--root", str(root), "--as-of", as_of])
        return code, buffer.getvalue()

    def assertRefused(self, root: Path, precondition: str, operation: str = "cadence-snapshot", as_of: str = AS_OF):
        code, output = self.run_guard(root, operation, as_of)
        self.assertEqual(code, 1, msg=f"expected a refusal, got:\n{output}")
        self.assertIn("REFUSED", output)
        self.assertIn(
            f"[{precondition}]",
            output,
            msg=f"refusal did not name precondition {precondition!r}:\n{output}",
        )
        return output


class SafetyInvariantTest(GuardTestCase):
    """The shipped substrate is inert. These run against the real repository."""

    def test_shipped_records_refuse_every_operation(self):
        for operation in CATALOGUED_OPERATIONS:
            with self.subTest(operation=operation):
                code, output = self.run_guard(REPOSITORY_ROOT, operation)
                self.assertEqual(code, 1, msg=f"{operation} was not refused:\n{output}")
                self.assertIn("[kill-switch-released]", output)
                self.assertIn("[promotion-signed]", output)

    def test_shipped_promotion_record_is_empty_with_the_switch_engaged(self):
        record = yaml.safe_load((REPOSITORY_ROOT / guard.PROMOTIONS_PATH).read_text(encoding="utf-8"))
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(record["kill_switch"], "engaged")
        self.assertEqual(record["promotions"], [])

    def test_shipped_catalog_holds_the_five_operations_at_attended_levels(self):
        record = yaml.safe_load((REPOSITORY_ROOT / guard.CATALOG_PATH).read_text(encoding="utf-8"))
        ids = [entry["id"] for entry in record["operations"]]
        self.assertEqual(sorted(ids), sorted(CATALOGUED_OPERATIONS))
        for entry in record["operations"]:
            with self.subTest(operation=entry["id"]):
                self.assertIn(entry["level"], guard.CATALOG_LEVELS)
                self.assertNotIn(entry["id"], guard.INELIGIBLE_OPERATIONS)

    def test_shipped_catalog_passes_its_own_structural_checks(self):
        for operation in CATALOGUED_OPERATIONS:
            with self.subTest(operation=operation):
                decision = guard.evaluate(REPOSITORY_ROOT, operation)
                named = {refusal.precondition for refusal in decision.refusals}
                self.assertEqual(named, {"kill-switch-released", "promotion-signed"})

    def test_shipped_ladder_still_carries_the_ineligible_list(self):
        decision = guard.Decision(operation="probe")
        found = guard.read_ineligible_operations(REPOSITORY_ROOT, decision)
        self.assertEqual(decision.refusals, [])
        for operation in guard.INELIGIBLE_OPERATIONS:
            self.assertIn(operation, found)


class TwoRecordsTest(GuardTestCase):
    """Neither record alone permits anything."""

    def test_complete_bound_is_permitted(self):
        code, output = self.run_guard(self.build())
        self.assertEqual(code, 0, msg=output)
        self.assertIn("PERMITTED", output)
        self.assertIn("python3 scripts/cadence.py --root .", output)
        self.assertIn("ops/status/*.md", output)
        self.assertIn("founder", output)

    def test_promotion_without_a_released_kill_switch_is_refused(self):
        root = self.build(promotions_record=promotions(kill_switch="engaged"))
        output = self.assertRefused(root, "kill-switch-released")
        self.assertNotIn("[promotion-signed]", output)

    def test_released_kill_switch_without_a_promotion_is_refused(self):
        root = self.build(promotions_record=promotions(kill_switch="released", entries=[]))
        output = self.assertRefused(root, "promotion-signed")
        self.assertNotIn("[kill-switch-released]", output)

    def test_catalog_cannot_promote_itself(self):
        entry = dict(CATALOG_ENTRY, level="A3")
        root = self.build(
            catalog_record=catalog([entry]),
            promotions_record=promotions(kill_switch="released", entries=[]),
        )
        self.assertRefused(root, "catalog-level")


class RecordIntegrityTest(GuardTestCase):
    """A record that cannot be read or trusted refuses; it never defaults to permitted."""

    def test_missing_catalog_is_refused(self):
        root = self.build()
        (root / guard.CATALOG_PATH).unlink()
        self.assertRefused(root, "catalog-readable")

    def test_missing_promotion_record_is_refused(self):
        root = self.build()
        (root / guard.PROMOTIONS_PATH).unlink()
        self.assertRefused(root, "promotions-readable")

    def test_unparsable_catalog_is_refused(self):
        root = self.build(catalog_record="operations: [oops\n")
        self.assertRefused(root, "catalog-readable")

    def test_unparsable_promotion_record_is_refused(self):
        root = self.build(promotions_record="kill_switch: [released\n")
        self.assertRefused(root, "promotions-readable")

    def test_catalog_that_is_not_a_mapping_is_refused(self):
        root = self.build(catalog_record="- one\n- two\n")
        self.assertRefused(root, "catalog-readable")

    def test_unexpected_catalog_schema_version_is_refused(self):
        record = catalog()
        record["schema_version"] = 2
        self.assertRefused(self.build(catalog_record=record), "catalog-schema")

    def test_unexpected_promotion_schema_version_is_refused(self):
        self.assertRefused(self.build(promotions_record=promotions(schema_version=99)), "promotions-schema")

    def test_unknown_top_level_promotion_field_is_refused(self):
        record = promotions()
        record["kill_swtich"] = "released"
        self.assertRefused(self.build(promotions_record=record), "promotions-schema")

    def test_unreadable_kill_switch_value_is_refused(self):
        self.assertRefused(self.build(promotions_record=promotions(kill_switch="off")), "promotions-schema")

    def test_empty_catalog_is_refused(self):
        self.assertRefused(self.build(catalog_record=catalog([])), "catalog-schema")

    def test_duplicate_catalog_ids_are_refused(self):
        record = catalog([copy.deepcopy(CATALOG_ENTRY), copy.deepcopy(CATALOG_ENTRY)])
        self.assertRefused(self.build(catalog_record=record), "catalog-entry")

    def test_unknown_catalog_field_is_refused(self):
        entry = dict(CATALOG_ENTRY, autonomy="A3")
        self.assertRefused(self.build(catalog_record=catalog([entry])), "catalog-entry")

    def test_missing_catalog_field_is_refused(self):
        entry = dict(CATALOG_ENTRY)
        del entry["reversal"]
        self.assertRefused(self.build(catalog_record=catalog([entry])), "catalog-entry")

    def test_unknown_promotion_field_is_refused(self):
        entry = dict(PROMOTION, rate_limit="hourly")
        self.assertRefused(self.build(promotions_record=promotions(entries=[entry])), "promotions-record")

    def test_missing_promotion_field_is_refused(self):
        entry = dict(PROMOTION)
        del entry["demotion_triggers"]
        self.assertRefused(self.build(promotions_record=promotions(entries=[entry])), "promotions-record")

    def test_promotion_of_an_uncatalogued_operation_refuses_the_record(self):
        entry = dict(PROMOTION, operation="invented-operation")
        root = self.build(promotions_record=promotions(entries=[entry]))
        output = self.assertRefused(root, "promotions-record")
        self.assertIn("[promotion-signed]", output)

    def test_two_promotions_for_one_operation_are_refused(self):
        record = promotions(entries=[copy.deepcopy(PROMOTION), copy.deepcopy(PROMOTION)])
        self.assertRefused(self.build(promotions_record=record), "promotion-unique")


class CatalogBoundTest(GuardTestCase):
    """The catalog describes a real, narrow bound or the guard refuses."""

    def test_uncatalogued_operation_is_refused(self):
        self.assertRefused(self.build(), "operation-catalogued", operation="metrics-snapshot")

    def test_command_naming_a_missing_script_is_refused(self):
        entry = dict(CATALOG_ENTRY, command=["python3", "scripts/absent.py", "--root", "."])
        self.assertRefused(self.build(catalog_record=catalog([entry])), "catalog-command")

    def test_command_with_a_shell_metacharacter_is_refused(self):
        entry = dict(CATALOG_ENTRY, command=["python3", "scripts/cadence.py", "&&", "rm -rf ."])
        self.assertRefused(self.build(catalog_record=catalog([entry])), "catalog-command")

    def test_write_scope_reaching_a_governance_record_is_refused(self):
        entry = dict(CATALOG_ENTRY, write_scope=["ops/autonomy/*.yaml"])
        promotion = dict(PROMOTION, write_scope=["ops/autonomy/*.yaml"])
        root = self.build(catalog_record=catalog([entry]), promotions_record=promotions(entries=[promotion]))
        self.assertRefused(root, "catalog-write-scope")

    def test_write_scope_reaching_the_guard_itself_is_refused(self):
        entry = dict(CATALOG_ENTRY, write_scope=["scripts/*.py"])
        self.assertRefused(self.build(catalog_record=catalog([entry])), "catalog-write-scope")

    def test_write_scope_escaping_the_repository_is_refused(self):
        entry = dict(CATALOG_ENTRY, write_scope=["../elsewhere/*.md"])
        self.assertRefused(self.build(catalog_record=catalog([entry])), "catalog-write-scope")

    def test_absolute_write_scope_is_refused(self):
        entry = dict(CATALOG_ENTRY, write_scope=["/etc/*.conf"])
        self.assertRefused(self.build(catalog_record=catalog([entry])), "catalog-write-scope")

    def test_repository_root_write_scope_is_refused(self):
        entry = dict(CATALOG_ENTRY, write_scope=["*.md"])
        self.assertRefused(self.build(catalog_record=catalog([entry])), "catalog-write-scope")

    def test_operation_that_writes_nothing_is_permitted_with_an_empty_scope(self):
        entry = dict(CATALOG_ENTRY, write_scope=[])
        promotion = dict(PROMOTION, write_scope=[])
        root = self.build(catalog_record=catalog([entry]), promotions_record=promotions(entries=[promotion]))
        code, output = self.run_guard(root)
        self.assertEqual(code, 0, msg=output)
        self.assertIn("writes nothing", output)


class PromotionAgreementTest(GuardTestCase):
    """A promotion must agree with the catalog and with the ladder."""

    def test_write_scope_disagreeing_with_the_catalog_is_refused(self):
        promotion = dict(PROMOTION, write_scope=["ops/status/*.md", "release/briefs/*.md"])
        output = self.assertRefused(
            self.build(promotions_record=promotions(entries=[promotion])), "promotion-write-scope"
        )
        self.assertIn("ops/autonomy/operations.yaml", output)

    def test_narrower_write_scope_than_the_catalog_is_refused(self):
        promotion = dict(PROMOTION, write_scope=["ops/status/cadence.md"])
        self.assertRefused(self.build(promotions_record=promotions(entries=[promotion])), "promotion-write-scope")

    def test_promotion_below_the_unattended_level_is_refused(self):
        promotion = dict(PROMOTION, level="A2")
        self.assertRefused(self.build(promotions_record=promotions(entries=[promotion])), "promotion-level")

    def test_promotion_of_a_permanently_ineligible_operation_is_refused(self):
        entry = dict(
            CATALOG_ENTRY,
            id="maturity-promotion",
            summary="Change a maturity value.",
            level="A1",
        )
        promotion = dict(PROMOTION, operation="maturity-promotion")
        root = self.build(catalog_record=catalog([entry]), promotions_record=promotions(entries=[promotion]))
        output = self.assertRefused(root, "operation-eligible", operation="maturity-promotion")
        self.assertIn("permanently ineligible", output)

    def test_evidence_path_that_does_not_exist_is_refused(self):
        promotion = dict(PROMOTION, evidence=["evidence/absent.md"])
        self.assertRefused(self.build(promotions_record=promotions(entries=[promotion])), "promotion-evidence")

    def test_promotion_without_evidence_is_refused(self):
        promotion = dict(PROMOTION, evidence=[])
        self.assertRefused(self.build(promotions_record=promotions(entries=[promotion])), "promotion-evidence")

    def test_promotion_without_demotion_triggers_is_refused(self):
        promotion = dict(PROMOTION, demotion_triggers=[])
        self.assertRefused(
            self.build(promotions_record=promotions(entries=[promotion])), "promotion-demotion-triggers"
        )


class SignatureTest(GuardTestCase):
    """A promotion is a signed human decision or it is nothing."""

    def test_promotion_without_a_signature_is_refused(self):
        promotion = dict(PROMOTION)
        promotion["signed_by"] = ""
        self.assertRefused(self.build(promotions_record=promotions(entries=[promotion])), "signature-present")

    def test_promotion_without_a_date_is_refused(self):
        promotion = dict(PROMOTION)
        promotion["signed_on"] = None
        self.assertRefused(self.build(promotions_record=promotions(entries=[promotion])), "signature-present")

    def test_signature_naming_a_person_is_refused(self):
        promotion = dict(PROMOTION, signed_by="dakota")
        output = self.assertRefused(
            self.build(promotions_record=promotions(entries=[promotion])), "signature-role"
        )
        self.assertIn("controlled operating role", output)

    def test_signature_by_a_role_without_reserved_authority_is_refused(self):
        promotion = dict(PROMOTION, signed_by="maintainer")
        self.assertRefused(self.build(promotions_record=promotions(entries=[promotion])), "signature-authority")

    def test_signature_dated_in_the_future_is_refused(self):
        promotion = dict(PROMOTION, signed_on="2026-12-01")
        self.assertRefused(self.build(promotions_record=promotions(entries=[promotion])), "signature-date")

    def test_signature_with_an_unreadable_date_is_refused(self):
        promotion = dict(PROMOTION, signed_on="soon")
        self.assertRefused(self.build(promotions_record=promotions(entries=[promotion])), "signature-date")

    def test_yaml_date_signature_is_accepted(self):
        from datetime import date

        promotion = dict(PROMOTION, signed_on=date(2026, 9, 1))
        code, output = self.run_guard(self.build(promotions_record=promotions(entries=[promotion])))
        self.assertEqual(code, 0, msg=output)


class LadderTest(GuardTestCase):
    """The permanently ineligible list is read from the ladder, not assumed."""

    def test_missing_ladder_is_refused(self):
        root = self.build()
        (root / guard.LADDER_PATH).unlink()
        self.assertRefused(root, "ladder-readable")

    def test_ladder_without_the_section_is_refused(self):
        root = self.build(ladder="# Autonomy Ladder\n\n## Levels\n\nNo ineligible section here.\n")
        self.assertRefused(root, "ladder-readable")

    def test_ladder_section_with_no_ids_is_refused(self):
        root = self.build(ladder=f"{LADDER_HEADER}| moderation | text | reason | record |\n")
        self.assertRefused(root, "ladder-readable")

    def test_ladder_dropping_an_ineligible_operation_is_refused(self):
        kept = [item for item in guard.INELIGIBLE_OPERATIONS if item != "maturity-promotion"]
        output = self.assertRefused(self.build(ladder=ladder_text(kept)), "ladder-agreement")
        self.assertIn("maturity-promotion", output)

    def test_ladder_adding_an_ineligible_operation_is_honored(self):
        extended = list(guard.INELIGIBLE_OPERATIONS) + ["cadence-snapshot"]
        self.assertRefused(self.build(ladder=ladder_text(extended)), "operation-eligible")


class UsageTest(GuardTestCase):
    """Exit 2 is a usage error and never a decision about an operation."""

    def test_missing_operation_argument_exits_two(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                guard.main(["--root", str(REPOSITORY_ROOT)])
        self.assertEqual(raised.exception.code, 2)

    def test_root_that_is_not_a_directory_exits_two(self):
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            code = guard.main(["--operation", "cadence-snapshot", "--root", str(REPOSITORY_ROOT / "README.md")])
        self.assertEqual(code, 2)
        self.assertIn("not a directory", buffer.getvalue())

    def test_unreadable_as_of_exits_two(self):
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer):
            code = guard.main(
                ["--operation", "cadence-snapshot", "--root", str(REPOSITORY_ROOT), "--as-of", "yesterday"]
            )
        self.assertEqual(code, 2)
        self.assertIn("ISO date", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
