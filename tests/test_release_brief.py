"""Tests for scripts/release_brief.py.

The generator's contract is that a brief only ever says what a commit hash or a
repository path backs, that it stays a draft, and that it fails loudly instead
of writing a partial file. These tests build throwaway git repositories to
exercise that contract, then run one smoke test against this repository.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PHASE_2_SINCE = "9097a59"
PHASE_2_UNTIL = "5890629"
HASH_OR_PATH_RE = re.compile(r"`(?:[0-9a-f]{7,40}|[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+)`")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Registered before execution so the module's dataclasses can resolve their
    # own annotations, which `from __future__ import annotations` defers.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


release_brief = load_module("practice_release_brief", REPOSITORY_ROOT / "scripts" / "release_brief.py")
validate = load_module("practice_validate_for_brief", REPOSITORY_ROOT / "scripts" / "validate.py")

GIT_AVAILABLE = shutil.which("git") is not None


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = release_brief.main(argv)
    return code, out.getvalue(), err.getvalue()


def section(text: str, heading: str) -> str:
    start = text.index(heading)
    rest = text[start + len(heading):]
    match = re.search(r"^## ", rest, re.MULTILINE)
    return rest[: match.start()] if match else rest


class Fixture:
    """A throwaway git repository with deterministic commit metadata."""

    def __init__(self, root: Path):
        self.root = root
        self._git("init", "-q")
        self._git("config", "user.name", "Fixture")
        self._git("config", "user.email", "fixture@example.invalid")

    def _git(self, *args: str) -> str:
        env = os.environ.copy()
        env.update(
            {
                "GIT_AUTHOR_NAME": "Fixture",
                "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                "GIT_COMMITTER_NAME": "Fixture",
                "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
                "GIT_AUTHOR_DATE": "2026-09-01T09:00:00+00:00",
                "GIT_COMMITTER_DATE": "2026-09-01T09:00:00+00:00",
            }
        )
        result = subprocess.run(
            ["git", "-c", "commit.gpgsign=false", "-C", str(self.root), *args],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        return result.stdout

    def commit(self, subject: str, write: dict[str, str] | None = None, remove: list[str] | None = None) -> str:
        for rel, body in (write or {}).items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        for rel in remove or []:
            (self.root / rel).unlink()
        self._git("add", "-A")
        self._git("commit", "-q", "-m", subject)
        return self._git("rev-parse", "HEAD").strip()


HANDOFF_COMPLETE = "# Handoff\n\n## Status\n\nCOMPLETE\n"
HANDOFF_BLOCKED = "# Handoff\n\n## Status\n\nBLOCKED\n"
PRACTICE_CANDIDATE = (
    "---\n"
    "artifact_type: practice\n"
    'title: "Example candidate"\n'
    "maturity: proposed\n"
    "evidence_quality: none\n"
    "---\n\n"
    "# Example candidate\n"
)
LAB_RECORD = (
    "---\n"
    "artifact_type: lab\n"
    'title: "Example trial"\n'
    "---\n\n"
    "# Example trial\n\nThe outcome is not measured.\n"
)
OWNER_REVIEW = (
    "# Owner review packet\n\n"
    "## Owner gates\n\n"
    "| Gate | Evidence to review | Human action | Status |\n"
    "| --- | --- | --- | --- |\n"
    "| Example open gate | [packet](GATE_EVIDENCE.md) | confirm the destination | **OPEN** |\n"
    "| Example settled gate | [packet](GATE_EVIDENCE.md) | confirm the license | **human-approved** |\n\n"
    "## Evidenced operating holds\n\n"
    "| Hold | Evidence | Minimum clearance evidence | Status |\n"
    "| --- | --- | --- | --- |\n"
    "| Example open hold | the runbook | a human tests the route | **OPEN — blocks public launch** |\n"
)


def build_repository(root: Path) -> dict[str, str]:
    """Build a fixture history covering every branch of the brief's rules."""
    fixture = Fixture(root)
    shas = {}
    shas["first"] = fixture.commit(
        "task(T1): add a practice candidate",
        write={"practices/900-example.md": PRACTICE_CANDIDATE, "handoffs/T1.md": HANDOFF_COMPLETE},
    )
    shas["blocked"] = fixture.commit(
        "task(T2): add a document that is removed later",
        write={"docs/gone.md": "temporary\n", "handoffs/T2.md": HANDOFF_BLOCKED},
    )
    shas["no_task"] = fixture.commit(
        "chore: touch a file without a task id",
        write={"docs/kept.md": "kept\n"},
    )
    shas["no_handoff"] = fixture.commit(
        "task(T9): record a trial and drop the temporary document",
        write={"labs/900-trial.md": LAB_RECORD},
        remove=["docs/gone.md"],
    )
    shas["last"] = fixture.commit(
        "task(T5): TODO leftovers and [BRACKET] tokens in a subject",
        write={"release/OWNER_REVIEW.md": OWNER_REVIEW, "handoffs/T5.md": HANDOFF_COMPLETE},
    )
    return shas


@unittest.skipUnless(GIT_AVAILABLE, "git is required to build the fixture repositories")
class FixtureRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "repo"
        self.root.mkdir()
        self.shas = build_repository(self.root)
        self.brief = release_brief.build_brief(
            self.root, self.shas["first"], self.shas["last"], "2026-09-02"
        )

    def test_every_shipped_line_carries_a_pointer(self):
        shipped = section(self.brief, "## What shipped")
        claim_lines = [
            line
            for line in shipped.splitlines()
            if line.strip().startswith(("-", "#"))
        ]
        self.assertTrue(claim_lines)
        for line in claim_lines:
            with self.subTest(line=line):
                self.assertRegex(line, HASH_OR_PATH_RE)

    def test_prose_in_the_shipped_section_is_only_the_stated_caveat(self):
        shipped = section(self.brief, "## What shipped")
        prose = [
            line
            for line in shipped.splitlines()
            if line.strip() and not line.strip().startswith(("-", "#"))
        ]
        self.assertEqual(len(prose), 1)
        self.assertIn("not evidence of a release", prose[0])

    def test_commit_without_a_task_id_claims_no_handoff(self):
        shipped = section(self.brief, "## What shipped")
        self.assertIn("names no task in `task(<id>)` form, so no handoff is matched", shipped)

    def test_missing_handoff_is_reported_not_guessed(self):
        shipped = section(self.brief, "## What shipped")
        self.assertIn("Handoff `handoffs/T9.md` is not present", shipped)
        entry = shipped[shipped.index("task(T9)") : shipped.index("task(T5)")]
        self.assertNotIn("COMPLETE", entry)
        self.assertNotIn("BLOCKED", entry)

    def test_handoff_status_is_quoted_verbatim(self):
        shipped = section(self.brief, "## What shipped")
        self.assertIn("Handoff `handoffs/T1.md` records `## Status` `COMPLETE`", shipped)
        self.assertIn("Handoff `handoffs/T2.md` records `## Status` `BLOCKED`", shipped)

    def test_path_removed_before_the_range_head_is_omitted(self):
        self.assertNotIn("docs/gone.md", self.brief)
        self.assertIn("docs/kept.md", self.brief)
        self.assertIn("absent at", self.brief)

    def test_front_matter_values_are_quoted_and_never_upgraded(self):
        proposed = section(self.brief, "## What is proposed but not tested")
        self.assertIn("`practices/900-example.md`", proposed)
        self.assertIn("`maturity: proposed`", proposed)
        self.assertIn("`labs/900-trial.md`", proposed)
        self.assertNotIn("maturity: tested", self.brief)

    def test_not_measured_section_points_at_files(self):
        not_measured = section(self.brief, "## What is explicitly not measured")
        self.assertIn("`practices/900-example.md`", not_measured)
        self.assertIn("`evidence_quality: none`", not_measured)
        self.assertIn("`labs/900-trial.md` — 1 matching line", not_measured)

    def test_outstanding_approvals_list_open_rows_only(self):
        approvals = section(self.brief, "## Human approvals still outstanding")
        self.assertIn("`release/OWNER_REVIEW.md`", approvals)
        self.assertIn("Example open gate — status recorded as `OPEN`", approvals)
        self.assertIn("Example open hold", approvals)
        self.assertIn("OPEN — blocks public launch", approvals)
        self.assertNotIn("Example settled gate", approvals)

    def test_no_clearance_or_approval_is_asserted(self):
        self.assertIn("DRAFT — HUMAN REVIEW REQUIRED", self.brief)
        self.assertIn("No human maintainer has approved this brief", self.brief)
        # "cleared" may only ever appear inside an explicit denial.
        for match in re.finditer(r"\bclear(?:ed|s)?\b", self.brief):
            context = self.brief[max(0, match.start() - 90) : match.end()]
            with self.subTest(context=context):
                self.assertRegex(context, r"\b(does not|cannot|never)\b")

    def test_generated_output_passes_the_release_token_rules(self):
        errors: list[str] = []
        validate.validate_publication_tokens("release/briefs/fixture.md", self.brief, errors)
        self.assertEqual(errors, [])
        self.assertIn("TODO", self.brief, "the fixture subject should still be recorded verbatim")

    def test_two_runs_produce_identical_bytes(self):
        again = release_brief.build_brief(
            self.root, self.shas["first"], self.shas["last"], "2026-09-02"
        )
        self.assertEqual(self.brief, again)

    def test_working_tree_edits_do_not_change_the_brief(self):
        (self.root / "practices" / "900-example.md").write_text(
            PRACTICE_CANDIDATE.replace("proposed", "tested"), encoding="utf-8"
        )
        again = release_brief.build_brief(
            self.root, self.shas["first"], self.shas["last"], "2026-09-02"
        )
        self.assertEqual(self.brief, again)

    def test_since_is_inclusive(self):
        shipped = section(self.brief, "## What shipped")
        self.assertIn("task(T1): add a practice candidate", shipped)
        self.assertIn("5 commits are present", shipped)

    def test_root_inside_the_checkout_reads_the_whole_repository(self):
        nested = release_brief.build_brief(
            self.root / "practices", self.shas["first"], self.shas["last"], "2026-09-02"
        )
        self.assertEqual(self.brief, nested)

    def test_single_commit_range_is_allowed(self):
        brief = release_brief.build_brief(
            self.root, self.shas["first"], self.shas["first"], "2026-09-02"
        )
        self.assertIn("1 commit is present", brief)
        self.assertIn("task(T1)", brief)

    def test_out_writes_the_file_and_reports_the_path(self):
        out = Path(self.directory.name) / "briefs" / "brief.md"
        code, stdout, stderr = run_cli(
            [
                "--since", self.shas["first"],
                "--until", self.shas["last"],
                "--root", str(self.root),
                "--as-of", "2026-09-02",
                "--out", str(out),
            ]
        )
        self.assertEqual(code, 0, stderr)
        self.assertIn(str(out), stdout)
        self.assertEqual(out.read_text(encoding="utf-8"), self.brief)


@unittest.skipUnless(GIT_AVAILABLE, "git is required to build the fixture repositories")
class MissingOwnerReviewTests(unittest.TestCase):
    def test_absent_owner_review_names_the_unknown_instead_of_guessing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = Fixture(root)
            first = fixture.commit("task(T1): add a note", write={"docs/a.md": "a\n"})
            brief = release_brief.build_brief(root, first, first, "2026-09-02")
            approvals = section(brief, "## Human approvals still outstanding")
            self.assertIn("`release/OWNER_REVIEW.md` is not present", approvals)
            self.assertIn("unknown", approvals)
            errors: list[str] = []
            validate.validate_publication_tokens("release/briefs/fixture.md", brief, errors)
            self.assertEqual(errors, [])


@unittest.skipUnless(GIT_AVAILABLE, "git is required to build the fixture repositories")
class ErrorPathTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "repo"
        self.root.mkdir()
        fixture = Fixture(self.root)
        self.first = fixture.commit("task(T1): add a note", write={"docs/a.md": "a\n"})
        self.second = fixture.commit("task(T2): add another note", write={"docs/b.md": "b\n"})
        self.out = Path(self.directory.name) / "out" / "brief.md"

    def assert_failed(self, argv: list[str], expected: str) -> None:
        code, stdout, stderr = run_cli(argv + ["--out", str(self.out)])
        self.assertEqual(code, 1, stdout)
        self.assertIn(expected, stderr)
        self.assertFalse(self.out.exists(), "a failed run must not leave a partial file")

    def test_unknown_revision_fails_without_writing(self):
        self.assert_failed(
            ["--since", "0000000", "--root", str(self.root), "--as-of", "2026-09-02"],
            "unknown revision: 0000000",
        )

    def test_outside_a_git_checkout_fails_without_writing(self):
        plain = Path(self.directory.name) / "plain"
        plain.mkdir()
        self.assert_failed(
            ["--since", self.first, "--root", str(plain), "--as-of", "2026-09-02"],
            "is not inside a git checkout",
        )

    def test_missing_root_fails_without_writing(self):
        self.assert_failed(
            [
                "--since", self.first,
                "--root", str(Path(self.directory.name) / "absent"),
                "--as-of", "2026-09-02",
            ],
            "--root is not a directory",
        )

    def test_reversed_range_fails_without_writing(self):
        self.assert_failed(
            [
                "--since", self.second,
                "--until", self.first,
                "--root", str(self.root),
                "--as-of", "2026-09-02",
            ],
            "is not an ancestor of",
        )

    def test_non_iso_as_of_fails_without_writing(self):
        self.assert_failed(
            ["--since", self.first, "--root", str(self.root), "--as-of", "02-09-2026"],
            "--as-of must be an ISO date",
        )

    def test_impossible_as_of_date_fails_without_writing(self):
        self.assert_failed(
            ["--since", self.first, "--root", str(self.root), "--as-of", "2026-13-02"],
            "--as-of is not a real date",
        )

    def test_output_containing_an_unfinished_token_is_refused(self):
        with self.assertRaises(release_brief.BriefError) as raised:
            release_brief.check_release_tokens("A line with a TODO in prose.\n")
        self.assertIn("unfinished token", str(raised.exception))

    def test_output_containing_a_publication_token_is_refused(self):
        with self.assertRaises(release_brief.BriefError) as raised:
            release_brief.check_release_tokens("Post to [CHANNEL] today.\n")
        self.assertIn("publication token", str(raised.exception))


class ParsingTests(unittest.TestCase):
    def test_task_ids_are_read_only_from_task_subjects(self):
        self.assertEqual(release_brief.task_ids("task(E1): trial"), ["E1"])
        self.assertEqual(release_brief.task_ids("task(Q6,Q7): reviews"), ["Q6", "Q7"])
        self.assertEqual(release_brief.task_ids("task(P2-CLEANUP): wire"), ["P2-CLEANUP"])
        self.assertEqual(release_brief.task_ids("fix(research): strip whitespace"), [])
        self.assertEqual(release_brief.task_ids("docs: add a plan"), [])
        self.assertEqual(release_brief.task_ids("task(../etc/passwd): bad"), [])

    def test_front_matter_reads_top_level_fields_only(self):
        text = "---\nmaturity: proposed\nroles: [operator]\n  nested: value\n---\n\n# Title\n"
        fields = release_brief.front_matter(text)
        self.assertEqual(fields.get("maturity"), "proposed")
        self.assertNotIn("nested", fields)
        self.assertEqual(release_brief.front_matter("# No front matter\n"), {})

    def test_open_rows_are_selected_and_cells_are_cleaned(self):
        text = (
            "## Owner gates\n\n"
            "| Gate | Status |\n| --- | --- |\n"
            "| [Named](x.md) gate | **OPEN** |\n"
            "| Settled gate | approved |\n"
        )
        approvals = release_brief.outstanding_approvals(text)
        self.assertEqual(len(approvals), 1)
        self.assertEqual(approvals[0].name, "Named gate")
        self.assertEqual(approvals[0].status, "OPEN")
        self.assertEqual(approvals[0].section, "Owner gates")

    def test_handoff_status_requires_the_documented_shape(self):
        self.assertEqual(release_brief.handoff_status("## Status\n\nCOMPLETE\n"), "COMPLETE")
        self.assertEqual(release_brief.handoff_status("## Status\n\nBLOCKED\n"), "BLOCKED")
        self.assertIsNone(release_brief.handoff_status("## Status\n\nmostly done\n"))


def phase_2_range_present() -> bool:
    if not GIT_AVAILABLE:
        return False
    for rev in (PHASE_2_SINCE, PHASE_2_UNTIL):
        result = subprocess.run(
            ["git", "-C", str(REPOSITORY_ROOT), "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return False
    return True


@unittest.skipUnless(phase_2_range_present(), "the Phase 2 commit range is not in this checkout")
class RepositorySmokeTests(unittest.TestCase):
    """Run the generator over the real Phase 2 range in this repository."""

    @classmethod
    def setUpClass(cls):
        cls.brief = release_brief.build_brief(
            REPOSITORY_ROOT, PHASE_2_SINCE, PHASE_2_UNTIL, "2026-09-02"
        )

    def test_real_range_produces_a_pointer_backed_draft(self):
        self.assertIn("DRAFT — HUMAN REVIEW REQUIRED", self.brief)
        self.assertIn("28 commits", self.brief)
        self.assertIn("`research/BUZZ_PLATFORM_SNAPSHOT.md`", self.brief)
        self.assertIn("`handoffs/R1.md` records `## Status` `COMPLETE`", self.brief)
        self.assertIn("`practices/005-release-notes.md`", self.brief)
        self.assertIn("`maturity: proposed`", self.brief)
        self.assertNotIn("maturity: tested", self.brief)

    def test_real_range_lists_open_owner_gates_without_clearing_them(self):
        approvals = section(self.brief, "## Human approvals still outstanding")
        self.assertIn("Launch date — status recorded as `OPEN`", approvals)
        self.assertIn("Hosted member-visible surface", approvals)
        self.assertIn("does not clear an owner gate", self.brief)

    def test_committed_brief_matches_the_generator_output(self):
        committed = REPOSITORY_ROOT / "release" / "briefs" / "2026-09-02-phase-2.md"
        self.assertTrue(committed.is_file(), "the Phase 2 brief should be committed")
        self.assertEqual(
            committed.read_text(encoding="utf-8"),
            self.brief,
            "release/briefs/2026-09-02-phase-2.md is hand-edited; fix the generator and regenerate",
        )

    def test_real_output_passes_the_release_token_rules(self):
        errors: list[str] = []
        validate.validate_publication_tokens(
            "release/briefs/2026-09-02-phase-2.md", self.brief, errors
        )
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
