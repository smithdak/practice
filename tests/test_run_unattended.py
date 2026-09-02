"""Failure-mode coverage for scripts/run_unattended.py.

Most tests build a synthetic repository in a temporary directory, give it a
command that misbehaves in exactly one way, and assert that the runner detects
it, applies nothing, and records what happened. Three things those fixtures
cannot prove are tested separately:

- the safety invariant, ``test_shipped_records_refuse_every_operation``: with the
  records this repository actually ships, all five catalogued operations are
  refused, no operation output is written, and the repository is left byte-for-
  byte as it was. That is the most important test in this file. Its refusal
  entries go to a temporary ledger directory, never to ``ops/ledger/``;
- that the runner can act at all. ``test_in_scope_write_is_applied`` builds a
  fully signed fixture and expects a completed run, so a runner that refused or
  failed unconditionally - which would pass every containment test here - fails;
- that the bound is enforced rather than declared.
  ``test_out_of_scope_write_never_reaches_the_repository`` runs a command that
  writes one file inside its scope and one outside, and asserts that neither
  file exists afterwards.

No test writes into the real ``ops/ledger/``, ``ops/status/``, or
``release/briefs/``.
"""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Registered before execution so the module's own imports of its siblings
    # resolve the same objects this test compares against.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runner = load_module("practice_run_unattended", REPOSITORY_ROOT / "scripts" / "run_unattended.py")
guard = load_module("practice_guard_for_runner", REPOSITORY_ROOT / "scripts" / "autonomy_guard.py")
ledger = load_module("practice_ledger_for_runner", REPOSITORY_ROOT / "scripts" / "ledger.py")


AS_OF = "2026-09-02"

CATALOGUED_OPERATIONS = (
    "cadence-snapshot",
    "metrics-snapshot",
    "contract-drift-check",
    "staleness-sweep",
    "release-brief-draft",
)

OPERATION = "cadence-snapshot"

CATALOG_ENTRY = {
    "id": OPERATION,
    "summary": "Write a dated status file.",
    "command": ["python3", "scripts/operation.py", "--root", "."],
    "write_scope": ["ops/status/*.md"],
    "reversal": "Delete the written file, or close the pull request unmerged.",
    "blast_radius": "One new file in the repository. No member contact.",
    "level": "A1",
}

PROMOTION = {
    "operation": OPERATION,
    "level": "A3",
    "write_scope": ["ops/status/*.md"],
    "evidence": ["evidence/promotion-record.md"],
    "demotion_triggers": ["wrote outside write_scope", "guard precondition failed"],
    "signed_by": "founder",
    "signed_on": AS_OF,
}

# A command that writes one file inside the declared scope and nothing else.
IN_SCOPE_WRITER = """
import pathlib
import sys

root = pathlib.Path(sys.argv[sys.argv.index("--root") + 1]).resolve()
target = root / "ops" / "status" / "2026-09-02-report.md"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("# report\\n", encoding="utf-8")
"""

# The same, plus one file the catalogued scope does not cover.
ESCAPING_WRITER = """
import pathlib
import sys

root = pathlib.Path(sys.argv[sys.argv.index("--root") + 1]).resolve()
target = root / "ops" / "status" / "2026-09-02-report.md"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("# report\\n", encoding="utf-8")
escaped = root / "notes" / "escaped.md"
escaped.parent.mkdir(parents=True, exist_ok=True)
escaped.write_text("# outside the bound\\n", encoding="utf-8")
"""

WRITES_NOTHING = """
print("checked everything and changed nothing")
"""

FAILING_WRITER = """
import pathlib
import sys

root = pathlib.Path(sys.argv[sys.argv.index("--root") + 1]).resolve()
target = root / "ops" / "status" / "2026-09-02-report.md"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("# partial\\n", encoding="utf-8")
sys.exit(3)
"""

DELETING_COMMAND = """
import pathlib
import sys

root = pathlib.Path(sys.argv[sys.argv.index("--root") + 1]).resolve()
(root / "evidence" / "promotion-record.md").unlink()
"""

SLEEPING_COMMAND = """
import time

time.sleep(30)
"""

LADDER_HEADER = """# Autonomy Ladder (fixture)

## Permanently ineligible for A3

| Operation id | Operation | Why it is permanently ineligible | Where recorded |
|---|---|---|---|
"""


def ladder_text() -> str:
    rows = "".join(f"| `{item}` | text | reason | record |\n" for item in guard.INELIGIBLE_OPERATIONS)
    return f"{LADDER_HEADER}{rows}\n## Action vocabulary\n\nUnrelated section.\n"


def catalog(entries=None) -> dict:
    return {
        "schema_version": 1,
        "operations": copy.deepcopy(entries) if entries is not None else [copy.deepcopy(CATALOG_ENTRY)],
    }


def promotions(kill_switch: str = "released", entries=None) -> dict:
    return {
        "schema_version": 1,
        "kill_switch": kill_switch,
        "promotions": copy.deepcopy(entries) if entries is not None else [copy.deepcopy(PROMOTION)],
    }


def tree_file_names(root: Path) -> set[str]:
    """Every file under ``root`` that a run could plausibly disturb.

    ``.git`` is excluded because reading a repository refreshes its index,
    ``__pycache__`` because importing a module writes one, and ``.swarm`` and
    ``.worktrees`` because they are local orchestration state this repository
    does not track.
    """
    skipped = {".git", "__pycache__", ".swarm", ".worktrees"}
    names: set[str] = set()
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in skipped]
        base = Path(current)
        for name in filenames:
            names.add((base / name).relative_to(root).as_posix())
    return names


class RunnerTestCase(unittest.TestCase):
    """Shared fixture builder: a repository whose command misbehaves in one way."""

    def temporary_directory(self) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return Path(directory.name)

    def build(self, *, catalog_record=None, promotions_record=None, command_source=IN_SCOPE_WRITER) -> Path:
        root = self.temporary_directory()
        (root / "ops" / "autonomy").mkdir(parents=True)
        (root / "docs" / "framework").mkdir(parents=True)
        (root / "scripts").mkdir(parents=True)
        (root / "evidence").mkdir(parents=True)
        (root / "evidence" / "promotion-record.md").write_text("# Fixture evidence\n", encoding="utf-8")
        (root / "scripts" / "operation.py").write_text(command_source, encoding="utf-8")
        (root / "docs" / "framework" / "AUTONOMY_LADDER.md").write_text(ladder_text(), encoding="utf-8")
        self.write_yaml(root / "ops" / "autonomy" / "operations.yaml", catalog() if catalog_record is None else catalog_record)
        self.write_yaml(
            root / "ops" / "autonomy" / "promotions.yaml",
            promotions() if promotions_record is None else promotions_record,
        )
        return root

    @staticmethod
    def write_yaml(path: Path, value) -> None:
        if value is None:
            if path.exists():
                path.unlink()
        elif isinstance(value, str):
            path.write_text(value, encoding="utf-8")
        else:
            path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")

    def run_runner(self, root: Path, *extra: str, operation: str = OPERATION, ledger_dir: Path | None = None):
        argv = ["--operation", operation, "--root", str(root), "--as-of", AS_OF, *extra]
        if ledger_dir is not None:
            argv += ["--ledger-dir", str(ledger_dir)]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = runner.main(argv)
        return code, out.getvalue(), err.getvalue()

    def ledger_entries(self, ledger_dir: Path) -> list[tuple[Path, dict]]:
        if not ledger_dir.is_dir():
            return []
        found = []
        for path in sorted(ledger_dir.glob("*.md")):
            front_matter, _ = ledger.split_front_matter(path.read_text(encoding="utf-8"))
            self.assertIsNotNone(front_matter, msg=f"{path} has no front matter")
            found.append((path, yaml.safe_load(front_matter)))
        return found

    def single_entry(self, ledger_dir: Path) -> tuple[Path, dict]:
        found = self.ledger_entries(ledger_dir)
        self.assertEqual(len(found), 1, msg=f"expected exactly one ledger entry, found {[p.name for p, _ in found]}")
        return found[0]

    def assertEntryValidates(self, path: Path, root: Path) -> None:
        violations = ledger.validate_entry_file(path, root)
        self.assertEqual(violations, [], msg="the entry does not validate under scripts/ledger.py")

    def assertPrecondition(self, entry: dict, check: str, result: str) -> dict:
        matching = [item for item in entry["preconditions"] if item["check"] == check]
        self.assertEqual(
            len(matching),
            1,
            msg=f"expected exactly one '{check}' precondition, found {[i['check'] for i in entry['preconditions']]}",
        )
        self.assertEqual(matching[0]["result"], result, msg=f"'{check}' recorded {matching[0]}")
        return matching[0]


class SafetyInvariantTest(RunnerTestCase):
    """Shipped, the substrate is inert. These run against the real repository."""

    def test_shipped_records_refuse_every_operation(self):
        for operation in CATALOGUED_OPERATIONS:
            with self.subTest(operation=operation):
                ledger_dir = self.temporary_directory() / "ledger"
                code, out, err = self.run_runner(
                    REPOSITORY_ROOT, operation=operation, ledger_dir=ledger_dir
                )
                self.assertEqual(code, 1, msg=f"{operation} was not refused:\n{out}\n{err}")
                self.assertIn("REFUSED", out)
                self.assertIn("[kill-switch-released]", out)
                self.assertIn("[promotion-signed]", out)
                self.assertNotIn("Running:", out)

                path, entry = self.single_entry(ledger_dir)
                self.assertEqual(entry["outcome"], "refused")
                self.assertEqual(entry["paths_written"], [])
                self.assertEqual(entry["operation"], operation)
                self.assertEqual(entry["kill_switch"], "engaged")
                self.assertEqual(entry["promotion"], "none")
                failed = [item for item in entry["preconditions"] if item["result"] == "fail"]
                self.assertTrue(failed, msg="a refusal must name the precondition that failed")
                self.assertEntryValidates(path, REPOSITORY_ROOT)

    def test_refusing_every_operation_leaves_the_repository_unchanged(self):
        before = tree_file_names(REPOSITORY_ROOT)
        ledger_dir = self.temporary_directory() / "ledger"
        for operation in CATALOGUED_OPERATIONS:
            self.run_runner(REPOSITORY_ROOT, operation=operation, ledger_dir=ledger_dir)
        after = tree_file_names(REPOSITORY_ROOT)
        self.assertEqual(after, before, msg="a refused run changed the repository")
        self.assertFalse(
            (REPOSITORY_ROOT / "ops" / "status").exists(),
            msg="a refused run created the status directory an operation would write into",
        )
        self.assertEqual(len(self.ledger_entries(ledger_dir)), len(CATALOGUED_OPERATIONS))

    def test_dry_run_against_the_shipped_records_writes_nothing(self):
        before = tree_file_names(REPOSITORY_ROOT)
        ledger_dir = self.temporary_directory() / "ledger"
        code, out, err = self.run_runner(REPOSITORY_ROOT, "--dry-run", ledger_dir=ledger_dir)
        self.assertEqual(code, 0, msg=f"a dry run should exit 0:\n{out}\n{err}")
        self.assertIn("DRY RUN: nothing was written.", out)
        self.assertIn("outcome: dry-run", out)
        self.assertIn("[kill-switch-released]", out)
        self.assertFalse(ledger_dir.exists(), msg="a dry run created a ledger directory")
        self.assertEqual(tree_file_names(REPOSITORY_ROOT), before)

    def test_the_real_ledger_directory_is_untouched_by_these_tests(self):
        entries = sorted(path.name for path in (REPOSITORY_ROOT / "ops" / "ledger").glob("*.md"))
        self.assertEqual(
            entries,
            ["README.md", "SAMPLE_run.md"],
            msg="ops/ledger/ holds something other than its README and the committed sample",
        )


class GuardRefusalTest(RunnerTestCase):
    """The guard decides, and its refusal ends the run and is still recorded."""

    def test_engaged_kill_switch_refuses_and_runs_no_command(self):
        root = self.build(promotions_record=promotions(kill_switch="engaged"))
        ledger_dir = root / "ops" / "ledger"
        code, out, _ = self.run_runner(root)
        self.assertEqual(code, 1)
        self.assertIn("[kill-switch-released]", out)
        self.assertFalse((root / "ops" / "status").exists(), msg="the command ran despite the refusal")

        path, entry = self.single_entry(ledger_dir)
        self.assertEqual(entry["outcome"], "refused")
        self.assertEqual(entry["kill_switch"], "engaged")
        self.assertPrecondition(entry, "kill-switch-released", "fail")
        self.assertEntryValidates(path, root)

    def test_missing_promotion_refuses(self):
        root = self.build(promotions_record=promotions(entries=[]))
        code, out, _ = self.run_runner(root)
        self.assertEqual(code, 1)
        self.assertIn("[promotion-signed]", out)
        _, entry = self.single_entry(root / "ops" / "ledger")
        self.assertPrecondition(entry, "promotion-signed", "fail")

    def test_refusal_records_the_promotion_the_run_observed(self):
        root = self.build(promotions_record=promotions(kill_switch="engaged"))
        _, entry = self.single_entry_after_run(root)
        self.assertEqual(entry["promotion"]["level"], "A3")
        self.assertEqual(entry["promotion"]["signed_by"], "founder")
        self.assertEqual(str(entry["promotion"]["signed_on"]), AS_OF)

    def single_entry_after_run(self, root: Path):
        self.run_runner(root)
        return self.single_entry(root / "ops" / "ledger")

    def test_uncatalogued_operation_refuses_and_says_why_no_entry_exists(self):
        root = self.build()
        code, out, err = self.run_runner(root, operation="not-catalogued")
        self.assertEqual(code, 1)
        self.assertIn("[operation-catalogued]", out)
        self.assertIn("ledger entry could not be written", err)
        self.assertEqual(self.ledger_entries(root / "ops" / "ledger"), [])

    def test_permanently_ineligible_operation_refuses(self):
        entry = copy.deepcopy(CATALOG_ENTRY)
        entry["id"] = "maturity-promotion"
        root = self.build(
            catalog_record=catalog([entry]),
            promotions_record=promotions(entries=[]),
        )
        code, out, _ = self.run_runner(root, operation="maturity-promotion")
        self.assertEqual(code, 1)
        self.assertIn("[operation-eligible]", out)
        self.assertFalse((root / "ops" / "status").exists())


class WriteScopeTest(RunnerTestCase):
    """The command is untrusted with respect to its own bound."""

    def test_out_of_scope_write_never_reaches_the_repository(self):
        root = self.build(command_source=ESCAPING_WRITER)
        code, out, _ = self.run_runner(root)
        self.assertEqual(code, 1, msg=out)
        self.assertIn("FAILED", out)
        self.assertIn("notes/escaped.md", out)
        self.assertFalse(
            (root / "notes" / "escaped.md").exists(),
            msg="the out-of-scope file was left behind",
        )
        self.assertFalse(
            (root / "ops" / "status" / "2026-09-02-report.md").exists(),
            msg="a run that broke its bound applied part of its output anyway",
        )

        path, entry = self.single_entry(root / "ops" / "ledger")
        self.assertEqual(entry["outcome"], "failed")
        self.assertEqual(entry["paths_written"], [])
        self.assertEqual(entry["write_scope"], ["ops/status/*.md"])
        detail = self.assertPrecondition(entry, "write-scope-enforced", "fail")["detail"]
        self.assertIn("notes/escaped.md", detail)
        self.assertEntryValidates(path, root)

    def test_in_scope_write_is_applied(self):
        root = self.build()
        code, out, _ = self.run_runner(root)
        self.assertEqual(code, 0, msg=out)
        self.assertIn("COMPLETED", out)
        written = root / "ops" / "status" / "2026-09-02-report.md"
        self.assertTrue(written.is_file(), msg="the in-scope result was not applied")
        self.assertEqual(written.read_text(encoding="utf-8"), "# report\n")

        path, entry = self.single_entry(root / "ops" / "ledger")
        self.assertEqual(entry["outcome"], "completed")
        self.assertEqual(entry["paths_written"], ["ops/status/2026-09-02-report.md"])
        self.assertEqual(entry["write_scope"], ["ops/status/*.md"])
        self.assertEqual(entry["command"], CATALOG_ENTRY["command"])
        self.assertPrecondition(entry, "write-scope-enforced", "pass")
        self.assertEntryValidates(path, root)

    def test_empty_write_scope_refuses_every_write(self):
        entry = copy.deepcopy(CATALOG_ENTRY)
        entry["write_scope"] = []
        promotion = copy.deepcopy(PROMOTION)
        promotion["write_scope"] = []
        root = self.build(catalog_record=catalog([entry]), promotions_record=promotions(entries=[promotion]))
        code, out, _ = self.run_runner(root)
        self.assertEqual(code, 1, msg=out)
        self.assertFalse((root / "ops" / "status").exists())
        _, recorded = self.single_entry(root / "ops" / "ledger")
        self.assertEqual(recorded["outcome"], "failed")
        self.assertEqual(recorded["write_scope"], [])

    def test_empty_write_scope_completes_when_the_command_writes_nothing(self):
        entry = copy.deepcopy(CATALOG_ENTRY)
        entry["write_scope"] = []
        promotion = copy.deepcopy(PROMOTION)
        promotion["write_scope"] = []
        root = self.build(
            catalog_record=catalog([entry]),
            promotions_record=promotions(entries=[promotion]),
            command_source=WRITES_NOTHING,
        )
        code, out, _ = self.run_runner(root)
        self.assertEqual(code, 0, msg=out)
        path, recorded = self.single_entry(root / "ops" / "ledger")
        self.assertEqual(recorded["outcome"], "completed")
        self.assertEqual(recorded["paths_written"], [])
        self.assertEntryValidates(path, root)

    def test_deleting_a_file_is_a_bound_violation(self):
        root = self.build(command_source=DELETING_COMMAND)
        code, out, _ = self.run_runner(root)
        self.assertEqual(code, 1, msg=out)
        self.assertTrue(
            (root / "evidence" / "promotion-record.md").is_file(),
            msg="the runner applied a deletion",
        )
        _, entry = self.single_entry(root / "ops" / "ledger")
        self.assertEqual(entry["outcome"], "failed")

    def test_modifying_an_in_scope_file_is_applied_and_its_reversal_restores_it(self):
        root = self.build()
        target = root / "ops" / "status" / "2026-09-02-report.md"
        target.parent.mkdir(parents=True)
        target.write_text("# earlier\n", encoding="utf-8")
        code, out, _ = self.run_runner(root)
        self.assertEqual(code, 0, msg=out)
        self.assertEqual(target.read_text(encoding="utf-8"), "# report\n")
        _, entry = self.single_entry(root / "ops" / "ledger")
        self.assertEqual(entry["paths_written"], ["ops/status/2026-09-02-report.md"])
        self.assertIn("git checkout -- ops/status/2026-09-02-report.md", entry["reversal"])

    def test_the_command_runs_against_a_copy_and_not_the_repository(self):
        """A failed run leaves no trace, so the command cannot have run in place."""
        root = self.build(command_source=FAILING_WRITER)
        before = tree_file_names(root)
        self.run_runner(root)
        after = tree_file_names(root) - {
            path.relative_to(root).as_posix() for path in (root / "ops" / "ledger").glob("*.md")
        }
        self.assertEqual(after, before)


class DryRunTest(RunnerTestCase):
    """A dry run writes nothing at all, including its own record."""

    def test_dry_run_writes_no_ledger_entry_and_no_operation_output(self):
        root = self.build()
        before = tree_file_names(root)
        code, out, err = self.run_runner(root, "--dry-run")
        self.assertEqual(code, 0, msg=f"{out}\n{err}")
        self.assertEqual(tree_file_names(root), before)
        self.assertFalse((root / "ops" / "ledger").exists())
        self.assertFalse((root / "ops" / "status").exists())

    def test_dry_run_renders_the_entry_it_would_have_appended(self):
        root = self.build()
        _, out, _ = self.run_runner(root, "--dry-run")
        front_matter, body = ledger.split_front_matter(out[out.index("---\n"):])
        self.assertIsNotNone(front_matter)
        entry = yaml.safe_load(front_matter)
        self.assertEqual(entry["outcome"], "dry-run")
        self.assertEqual(entry["paths_written"], [])
        self.assertEqual(entry["operation"], OPERATION)
        self.assertEqual(entry["write_scope"], ["ops/status/*.md"])
        self.assertPrecondition(entry, "dry-run-requested", "pass")
        self.assertIn("# ", body)

    def test_the_rendered_dry_run_entry_would_validate_if_written(self):
        root = self.build()
        _, out, _ = self.run_runner(root, "--dry-run")
        rendered = out[out.index("---\n"):]
        entry = yaml.safe_load(ledger.split_front_matter(rendered)[0])
        destination = self.temporary_directory() / f"{entry['run_date']}-{entry['run_id']}.md"
        destination.write_text(rendered, encoding="utf-8")
        self.assertEntryValidates(destination, root)


class CommandFailureTest(RunnerTestCase):
    """A command that does not succeed is recorded as failed and applied not at all."""

    def test_non_zero_exit_is_recorded_as_failed(self):
        root = self.build(command_source=FAILING_WRITER)
        code, out, _ = self.run_runner(root)
        self.assertEqual(code, 1, msg=out)
        self.assertIn("exited 3", out)
        self.assertFalse(
            (root / "ops" / "status" / "2026-09-02-report.md").exists(),
            msg="a failed run's in-scope output was applied anyway",
        )
        path, entry = self.single_entry(root / "ops" / "ledger")
        self.assertEqual(entry["outcome"], "failed")
        self.assertEqual(entry["paths_written"], [])
        self.assertEntryValidates(path, root)
        # The command respected its bound and still failed; the entry says both.
        detail = self.assertPrecondition(entry, "write-scope-enforced", "pass")["detail"]
        self.assertIn("was not applied", detail)

    def test_a_command_that_does_not_finish_is_stopped_and_recorded_as_failed(self):
        root = self.build(command_source=SLEEPING_COMMAND)
        with mock.patch.object(runner, "COMMAND_TIMEOUT_SECONDS", 1):
            code, out, _ = self.run_runner(root)
        self.assertEqual(code, 1, msg=out)
        self.assertIn("did not finish within 1 seconds", out)
        _, entry = self.single_entry(root / "ops" / "ledger")
        self.assertEqual(entry["outcome"], "failed")


class MalformedCatalogTest(RunnerTestCase):
    """A bound the runner cannot read is a refusal, never a run."""

    def test_entry_without_a_reversal_refuses(self):
        entry = copy.deepcopy(CATALOG_ENTRY)
        entry.pop("reversal")
        root = self.build(catalog_record=catalog([entry]))
        code, out, _ = self.run_runner(root)
        self.assertEqual(code, 1, msg=out)
        self.assertFalse((root / "ops" / "status").exists())
        path, recorded = self.single_entry(root / "ops" / "ledger")
        self.assertEqual(recorded["outcome"], "refused")
        self.assertPrecondition(recorded, "catalog-entry-usable", "fail")
        self.assertEntryValidates(path, root)

    def test_entry_whose_write_scope_is_not_a_list_refuses(self):
        entry = copy.deepcopy(CATALOG_ENTRY)
        entry["write_scope"] = "ops/status/*.md"
        root = self.build(catalog_record=catalog([entry]))
        code, out, _ = self.run_runner(root)
        self.assertEqual(code, 1, msg=out)
        _, recorded = self.single_entry(root / "ops" / "ledger")
        self.assertPrecondition(recorded, "catalog-entry-usable", "fail")
        self.assertEqual(recorded["write_scope"], [])

    def test_unparsable_catalog_refuses(self):
        root = self.build(catalog_record="operations: [oh dear\n")
        code, out, err = self.run_runner(root)
        self.assertEqual(code, 1, msg=f"{out}\n{err}")
        self.assertIn("REFUSED", out)
        self.assertFalse((root / "ops" / "status").exists())

    def test_missing_catalog_refuses(self):
        root = self.build()
        (root / "ops" / "autonomy" / "operations.yaml").unlink()
        code, out, err = self.run_runner(root)
        self.assertEqual(code, 1, msg=f"{out}\n{err}")
        self.assertFalse((root / "ops" / "status").exists())
        _, entry = self.single_entry(root / "ops" / "ledger")
        self.assertPrecondition(entry, "catalog-entry-usable", "fail")


class LedgerEntryTest(RunnerTestCase):
    """Every non-dry run appends exactly one valid entry."""

    def test_the_entry_records_the_bound_the_reversal_and_what_was_read(self):
        root = self.build()
        self.run_runner(root)
        path, entry = self.single_entry(root / "ops" / "ledger")
        self.assertEqual(entry["claimed_level"], "A3")
        self.assertEqual(entry["trigger"], "manual")
        self.assertEqual(entry["actor"], "local-operator")
        self.assertEqual(entry["kill_switch"], "released")
        self.assertIn("ops/autonomy/operations.yaml", entry["paths_read"])
        self.assertIn("ops/autonomy/promotions.yaml", entry["paths_read"])
        self.assertIn("docs/framework/AUTONOMY_LADDER.md", entry["paths_read"])
        self.assertIn("scripts/operation.py", entry["paths_read"])
        self.assertIn(CATALOG_ENTRY["reversal"], entry["reversal"])
        self.assertIn("rm ops/status/2026-09-02-report.md", entry["reversal"])
        self.assertEqual(path.name, f"{AS_OF}-{entry['run_id']}.md")
        self.assertEntryValidates(path, root)

    def test_a_refused_run_records_the_catalogued_reversal(self):
        root = self.build(promotions_record=promotions(kill_switch="engaged"))
        self.run_runner(root)
        _, entry = self.single_entry(root / "ops" / "ledger")
        self.assertIn(CATALOG_ENTRY["reversal"], entry["reversal"])
        self.assertIn("nothing to undo", entry["reversal"])

    def test_the_trigger_and_actor_are_recorded_as_given(self):
        root = self.build()
        self.run_runner(root, "--trigger", "schedule")
        _, entry = self.single_entry(root / "ops" / "ledger")
        self.assertEqual(entry["trigger"], "schedule")
        self.assertEqual(entry["actor"], "scheduled-workflow")

    def test_a_second_run_gets_its_own_run_id(self):
        root = self.build()
        self.run_runner(root)
        self.run_runner(root)
        found = self.ledger_entries(root / "ops" / "ledger")
        self.assertEqual(len(found), 2)
        self.assertEqual(len({entry["run_id"] for _, entry in found}), 2)
        seen: dict[str, str] = {}
        for path, _ in found:
            self.assertEqual(ledger.validate_entry_file(path, root, seen), [])

    def test_a_run_id_already_used_by_a_sample_entry_is_stepped_over(self):
        root = self.build()
        ledger_dir = root / "ops" / "ledger"
        ledger_dir.mkdir(parents=True)
        sample = ledger_dir / "SAMPLE_run.md"
        sample.write_text(f"---\nrun_id: {OPERATION}-001\n---\n\n# sample\n", encoding="utf-8")
        self.run_runner(root)
        appended = [(path, entry) for path, entry in self.ledger_entries(ledger_dir) if path != sample]
        self.assertEqual(len(appended), 1)
        self.assertEqual(appended[0][1]["run_id"], f"{OPERATION}-002")

    def test_each_precondition_id_appears_once(self):
        root = self.build(promotions_record=promotions(kill_switch="engaged"))
        self.run_runner(root)
        _, entry = self.single_entry(root / "ops" / "ledger")
        names = [item["check"] for item in entry["preconditions"]]
        self.assertEqual(len(names), len(set(names)), msg=f"a precondition id repeats: {names}")


class UsageTest(RunnerTestCase):
    """An operator mistake exits 2 and changes nothing."""

    def test_root_that_is_not_a_directory_exits_two(self):
        code, _, err = self.run_runner(Path("/no/such/repository"))
        self.assertEqual(code, 2)
        self.assertIn("is not a directory", err)

    def test_operation_that_is_not_a_slug_exits_two(self):
        root = self.build()
        code, _, err = self.run_runner(root, operation="Cadence Snapshot")
        self.assertEqual(code, 2)
        self.assertIn("is not an operation id", err)

    def test_actor_that_is_not_a_slug_exits_two(self):
        root = self.build()
        code, _, err = self.run_runner(root, "--actor", "Some Person")
        self.assertEqual(code, 2)
        self.assertIn("is not an actor label", err)

    def test_as_of_that_is_not_a_date_exits_two(self):
        root = self.build()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = runner.main(["--operation", OPERATION, "--root", str(root), "--as-of", "yesterday"])
        self.assertEqual(code, 2)
        self.assertIn("must be an ISO date", err.getvalue())

    def test_missing_operation_exits_two(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                runner.main(["--root", "."])
        self.assertEqual(raised.exception.code, 2)


class ScopeMatchingTest(unittest.TestCase):
    """The runner matches a scope the way the catalog says it is matched."""

    def test_fnmatch_semantics_match_the_catalogued_rule(self):
        self.assertTrue(runner.matches_scope("ops/status/a.md", ["ops/status/*.md"]))
        self.assertFalse(runner.matches_scope("ops/status/a.txt", ["ops/status/*.md"]))
        self.assertFalse(runner.matches_scope("DECISIONS.md", ["ops/status/*.md"]))
        self.assertFalse(runner.matches_scope("ops/status/a.md", []))
        self.assertTrue(
            runner.matches_scope(
                "release/briefs/2026-09-02-phase-4.md",
                ["release/briefs/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-*.md"],
            )
        )
        self.assertFalse(
            runner.matches_scope(
                "release/briefs/README.md",
                ["release/briefs/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-*.md"],
            )
        )


if __name__ == "__main__":
    unittest.main()
