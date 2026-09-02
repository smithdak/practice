from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 9, 2)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cadence = load_module("practice_cadence", REPOSITORY_ROOT / "scripts" / "cadence.py")
check_links = load_module("practice_check_links_for_cadence_tests", REPOSITORY_ROOT / "scripts" / "check_links.py")

OWNER_REVIEW = """# Owner review packet

## Owner gates

| Gate | Evidence | Human action | Status |
| --- | --- | --- | --- |
| Launch date | [packet](GATE_EVIDENCE.md) | Set the date. | **OPEN** |
| Brand mark | none | Approve a mark. | Recorded 2026-08-30 |

## Evidenced operating holds

| Hold | Evidence | Minimum clearance evidence | Status |
| --- | --- | --- | --- |
| Human operating coverage | runbook | Name the humans. | **OPEN - blocks public launch** |
"""


def minimal_config(**overrides) -> dict:
    config = {
        "schema_version": 1,
        "source": "ops/WEEKLY_CADENCE.md",
        "staleness_limit_days": check_links.STALE_LIMIT_DAYS,
        "operating_rule": {"source_section": "Operating rule", "text": "Skip a pass with no output."},
        "passes": [
            {
                "id": "build",
                "name": "Build",
                "rhythm": "weekly review window",
                "interval_days": 7,
                "due_rule": "elapsed",
                "source_section": "Weekly loop",
                "named_output": "Draft artifact or pull request.",
                "owner_role": "Author or area maintainer",
                "skip_rule": "Skip when Intake selected no bounded change.",
                "evidence": ["practices/*.md"],
            },
            {
                "id": "review",
                "name": "Review",
                "rhythm": "weekly review window",
                "interval_days": 7,
                "due_rule": "elapsed",
                "source_section": "Weekly loop",
                "named_output": "Review record in the Git issue or pull request.",
                "owner_role": "Area maintainer",
                "skip_rule": "Skip when there is no draft to inspect.",
                "evidence": ["reviews/*.md", "labs/*.md"],
            },
            {
                "id": "release",
                "name": "Release",
                "rhythm": "weekly window, only when a packet is ready",
                "interval_days": None,
                "due_rule": "on_trigger",
                "source_section": "Weekly loop",
                "named_output": "Git release record.",
                "owner_role": "Human release owner",
                "skip_rule": "A release happens only when a human approves its packet.",
                "evidence": ["release/*.md"],
            },
        ],
        "queues": [
            {
                "id": "safety_privacy_access_conduct",
                "name": "Safety, privacy, access, and conduct",
                "source_section": "Two kinds of work / Continuous queues",
                "human_owner_role": "Eligible human moderator or founder",
                "repo_check": "none",
                "repo_check_reason": "The case record is private by design.",
            },
            {
                "id": "agent_review",
                "name": "Agent review",
                "source_section": "Two kinds of work / Continuous queues",
                "human_owner_role": "Requesting human maintainer",
                "repo_check": "blocked_handoffs",
            },
            {
                "id": "follow_up_and_broken_links",
                "name": "Follow-up and broken links",
                "source_section": "Two kinds of work / Continuous queues",
                "human_owner_role": "Artifact maintainer",
                "repo_check": "stale_as_of",
            },
        ],
        "escalations": {
            "id": "stop_and_escalate",
            "name": "Stop and escalate",
            "source_section": "Stop and escalate",
            "rule": "Pause when a decision belongs to a reserved human owner.",
            "repo_check": "open_owner_gates",
        },
        "checks": {
            "blocked_handoffs": {"scans": "handoffs/*.md"},
            "open_owner_gates": {"scans": "release/OWNER_REVIEW.md"},
            "stale_as_of": {"scans": "**/*.md"},
        },
        "low_activity_fallback": {
            "source_section": "Small-community and low-activity fallback",
            "interval_days": 14,
            "rule": "Run one short operating pass every two weeks.",
        },
    }
    config.update(overrides)
    return config


def write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def build_fixture(root: Path, config: dict | None = None) -> Path:
    """Create a small repository-shaped tree with a cadence index."""
    write(root, "ops/cadence.yaml", yaml.safe_dump(config or minimal_config(), sort_keys=False))
    write(root, "practices/001-context-pack.md", "# Practice\n")
    write(root, "reviews/EVIDENCE_REVIEW.md", "# Review\n")
    write(root, "release/OWNER_REVIEW.md", OWNER_REVIEW)
    write(root, "handoffs/A1.md", "# A1 Handoff\n\n## Status\n\nCOMPLETE\n")
    return root


def run_main(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = cadence.main(argv)
        except SystemExit as exc:  # argparse usage errors
            code = int(exc.code or 0)
    return code, out.getvalue(), err.getvalue()


def run_json(root: Path, as_of: str = "2026-09-02") -> dict:
    code, out, err = run_main(["--root", str(root), "--as-of", as_of, "--json"])
    assert code == 0, f"exit {code}: {err}"
    return json.loads(out)


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        build_fixture(self.root)

    def report(self, as_of: str = "2026-09-02") -> dict:
        return run_json(self.root, as_of)

    def pass_by_id(self, report: dict, pass_id: str) -> dict:
        for entry in report["passes"]:
            if entry["id"] == pass_id:
                return entry
        raise AssertionError(f"no pass {pass_id} in report")


class PassWindowTests(unittest.TestCase):
    """Due/not-due logic, isolated from the filesystem and from git."""

    def test_window_not_elapsed_is_not_due(self):
        status, due, days = cadence.pass_window(date(2026, 8, 30), AS_OF, 7, "elapsed")
        self.assertEqual((status, due, days), ("within window", False, 3))

    def test_window_elapsed_is_due(self):
        status, due, days = cadence.pass_window(date(2026, 8, 20), AS_OF, 7, "elapsed")
        self.assertEqual((status, due, days), ("window elapsed", True, 13))

    def test_exactly_one_interval_is_due(self):
        status, due, days = cadence.pass_window(date(2026, 8, 26), AS_OF, 7, "elapsed")
        self.assertEqual((status, due, days), ("window elapsed", True, 7))

    def test_monthly_window_uses_its_own_interval(self):
        self.assertFalse(cadence.pass_window(date(2026, 8, 20), AS_OF, 30, "elapsed")[1])
        self.assertTrue(cadence.pass_window(date(2026, 7, 20), AS_OF, 30, "elapsed")[1])

    def test_unknown_last_change_is_not_reported_as_not_due(self):
        status, due, days = cadence.pass_window(None, AS_OF, 7, "elapsed")
        self.assertIsNone(due)
        self.assertIsNone(days)
        self.assertIn("unknown", status)

    def test_on_trigger_pass_is_never_due_by_elapsed_time(self):
        status, due, days = cadence.pass_window(date(2026, 1, 1), AS_OF, None, "on_trigger")
        self.assertFalse(due)
        self.assertEqual(days, 244)
        self.assertIn("not scheduled", status)

    def test_elapsed_rule_without_an_interval_is_unknown(self):
        status, due, _ = cadence.pass_window(date(2026, 8, 1), AS_OF, None, "elapsed")
        self.assertIsNone(due)
        self.assertIn("unknown", status)


class EvidenceTests(FixtureCase):
    def test_matched_and_missing_evidence_are_reported_per_glob(self):
        report = self.report()
        review = self.pass_by_id(report, "review")
        self.assertEqual(review["missing_evidence"], ["labs/*.md"])
        globs = {record["glob"]: record["matches"] for record in review["evidence"]}
        self.assertEqual(globs, {"reviews/*.md": 1, "labs/*.md": 0})
        self.assertEqual(self.pass_by_id(report, "build")["missing_evidence"], [])

    def test_named_output_owner_role_and_skip_rule_come_from_the_index(self):
        entry = self.pass_by_id(self.report(), "build")
        self.assertEqual(entry["owner_role"], "Author or area maintainer")
        self.assertEqual(entry["named_output"], "Draft artifact or pull request.")
        self.assertIn("Skip", entry["skip_rule"])
        self.assertEqual(entry["source_section"], "Weekly loop")

    def test_report_is_deterministic(self):
        first = run_main(["--root", str(self.root), "--as-of", "2026-09-02"])
        second = run_main(["--root", str(self.root), "--as-of", "2026-09-02"])
        self.assertEqual(first, second)


class BlockedHandoffQueueTests(FixtureCase):
    def test_blocked_handoff_is_listed(self):
        write(self.root, "handoffs/B2.md", "# B2 Handoff\n\n## Status\n\nBLOCKED\n")
        report = self.report()
        blocked = report["checks"]["blocked_handoffs"]
        self.assertEqual([record["path"] for record in blocked["blocked"]], ["handoffs/B2.md"])
        self.assertEqual(report["summary"]["blocked_handoffs"], 1)

    def test_complete_handoff_is_not_listed(self):
        report = self.report()
        self.assertEqual(report["checks"]["blocked_handoffs"]["blocked"], [])
        self.assertEqual(report["checks"]["blocked_handoffs"]["records"], 1)

    def test_unreadable_status_is_reported_separately(self):
        write(self.root, "handoffs/C3.md", "# C3 Handoff\n\n## Status\n\nmostly done\n")
        blocked = self.report()["checks"]["blocked_handoffs"]
        self.assertEqual(blocked["unreadable_status"], ["handoffs/C3.md"])
        self.assertEqual(blocked["blocked"], [])

    def test_text_report_names_the_blocked_record(self):
        write(self.root, "handoffs/B2.md", "# B2 Handoff\n\n## Status\n\nBLOCKED\n")
        code, out, _ = run_main(["--root", str(self.root), "--as-of", "2026-09-02"])
        self.assertEqual(code, 0)
        self.assertIn("BLOCKED  handoffs/B2.md", out)


class OwnerGateQueueTests(FixtureCase):
    def test_open_gates_and_holds_are_counted_separately(self):
        report = self.report()
        gates = report["checks"]["open_owner_gates"]
        self.assertTrue(gates["available"])
        self.assertEqual([row["name"] for row in gates["gates"]], ["Launch date", "Brand mark"])
        self.assertEqual([row["open"] for row in gates["gates"]], [True, False])
        self.assertEqual([row["name"] for row in gates["holds"]], ["Human operating coverage"])
        self.assertEqual(report["summary"]["open_owner_gates"], 1)
        self.assertEqual(report["summary"]["open_operating_holds"], 1)

    def test_recorded_status_text_is_repeated_verbatim(self):
        gates = self.report()["checks"]["open_owner_gates"]
        self.assertEqual(gates["holds"][0]["status"], "OPEN - blocks public launch")

    def test_report_never_claims_a_gate_is_cleared(self):
        code, out, _ = run_main(["--root", str(self.root), "--as-of", "2026-09-02"])
        self.assertEqual(code, 0)
        self.assertIn("This report clears no gate and no hold", out)
        self.assertNotIn("cleared", out.lower())

    def test_missing_owner_review_degrades_without_failing(self):
        (self.root / "release" / "OWNER_REVIEW.md").unlink()
        code, out, _ = run_main(["--root", str(self.root), "--as-of", "2026-09-02"])
        self.assertEqual(code, 0)
        self.assertIn("unavailable", out)
        report = self.report()
        self.assertFalse(report["checks"]["open_owner_gates"]["available"])
        self.assertEqual(report["summary"]["open_owner_gates"], 0)


class StalenessTests(FixtureCase):
    def test_limit_matches_check_links(self):
        report = self.report()
        self.assertEqual(report["checks"]["stale_as_of"]["limit_days"], check_links.STALE_LIMIT_DAYS)
        self.assertEqual(report["checks"]["stale_as_of"]["rule_source"], "scripts/check_links.py")

    def test_date_older_than_the_limit_is_reported(self):
        write(self.root, "reviews/OLD.md", "# Old\n\nAs of: 2026-01-01 the snapshot was checked.\n")
        stale = self.report()["checks"]["stale_as_of"]["stale"]
        self.assertEqual(len(stale), 1)
        self.assertEqual(stale[0]["path"], "reviews/OLD.md")
        self.assertEqual(stale[0]["line"], 3)
        self.assertEqual(stale[0]["as_of"], "2026-01-01")
        self.assertEqual(stale[0]["age_days"], 244)

    def test_date_exactly_at_the_limit_is_not_stale(self):
        limit = check_links.STALE_LIMIT_DAYS
        fresh = (AS_OF - timedelta(days=limit)).isoformat()
        write(self.root, "reviews/EDGE.md", f"# Edge\n\nAs of: {fresh} the source was checked.\n")
        self.assertEqual(self.report()["checks"]["stale_as_of"]["stale"], [])

    def test_as_of_inside_a_code_fence_is_ignored(self):
        write(self.root, "reviews/FENCE.md", "# Fence\n\n```\nAs of: 2026-01-01\n```\n")
        report = self.report()
        self.assertEqual(report["checks"]["stale_as_of"]["stale"], [])
        self.assertEqual(report["checks"]["stale_as_of"]["dates_checked"], 0)

    def test_as_of_flag_moves_the_staleness_window(self):
        write(self.root, "reviews/OLD.md", "# Old\n\nAs of: 2026-06-01 the source was checked.\n")
        self.assertEqual(self.report("2026-07-01")["checks"]["stale_as_of"]["stale"], [])
        self.assertEqual(len(self.report("2026-12-01")["checks"]["stale_as_of"]["stale"]), 1)


class JsonShapeTests(FixtureCase):
    def test_top_level_keys(self):
        report = self.report()
        self.assertEqual(
            sorted(report),
            [
                "as_of",
                "checks",
                "config",
                "escalations",
                "git",
                "low_activity_fallback",
                "operating_rule",
                "passes",
                "queues",
                "root",
                "schema_version",
                "scope_note",
                "source",
                "summary",
            ],
        )
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["as_of"], "2026-09-02")
        self.assertEqual(report["config"], "ops/cadence.yaml")

    def test_pass_keys(self):
        entry = self.pass_by_id(self.report(), "build")
        self.assertEqual(
            sorted(entry),
            [
                "days_since",
                "due",
                "due_rule",
                "evidence",
                "evidence_files",
                "id",
                "interval_days",
                "last_output_change",
                "missing_evidence",
                "name",
                "named_output",
                "note",
                "off_repo_records",
                "owner_role",
                "rhythm",
                "skip_rule",
                "source_section",
                "status",
                "untracked_evidence",
            ],
        )
        self.assertEqual(sorted(entry["evidence"][0]), ["example", "glob", "matches", "newest_match"])

    def test_check_and_summary_keys(self):
        report = self.report()
        self.assertEqual(sorted(report["checks"]), ["blocked_handoffs", "open_owner_gates", "stale_as_of"])
        self.assertEqual(
            sorted(report["summary"]),
            [
                "blocked_handoffs",
                "open_operating_holds",
                "open_owner_gates",
                "passes",
                "passes_missing_evidence",
                "passes_unknown",
                "passes_with_elapsed_window",
                "stale_as_of_dates",
            ],
        )

    def test_queues_carry_their_source_section_and_check(self):
        queues = {entry["id"]: entry for entry in self.report()["queues"]}
        self.assertEqual(queues["agent_review"]["repo_check"], "blocked_handoffs")
        self.assertEqual(queues["safety_privacy_access_conduct"]["repo_check"], "none")
        self.assertIn("private", queues["safety_privacy_access_conduct"]["repo_check_reason"])
        for entry in queues.values():
            self.assertTrue(entry["source_section"])

    def test_json_is_stable_between_runs(self):
        self.assertEqual(
            run_main(["--root", str(self.root), "--as-of", "2026-09-02", "--json"]),
            run_main(["--root", str(self.root), "--as-of", "2026-09-02", "--json"]),
        )


class NoGitDegradationTests(FixtureCase):
    """A temporary directory is not a git checkout: dates degrade to unknown."""

    def test_git_is_reported_unavailable_with_a_reason(self):
        report = self.report()
        self.assertFalse(report["git"]["available"])
        self.assertIn("not inside a git work tree", report["git"]["reason"])

    def test_no_pass_reports_a_last_changed_date(self):
        for entry in self.report()["passes"]:
            self.assertIsNone(entry["last_output_change"], entry["id"])
            self.assertIsNone(entry["days_since"], entry["id"])

    def test_todays_date_is_never_substituted(self):
        code, out, _ = run_main(["--root", str(self.root), "--as-of", "2026-09-02"])
        self.assertEqual(code, 0)
        self.assertIn("change dates  unknown", out)
        self.assertNotIn("last output   2026-09-02", out)

    def test_elapsed_passes_report_unknown_rather_than_not_due(self):
        report = self.report()
        self.assertIsNone(self.pass_by_id(report, "build")["due"])
        self.assertIsNone(self.pass_by_id(report, "review")["due"])
        self.assertEqual(report["summary"]["passes_unknown"], 2)
        self.assertEqual(report["summary"]["passes_with_elapsed_window"], 0)

    def test_queue_checks_still_run_without_git(self):
        write(self.root, "handoffs/B2.md", "# B2 Handoff\n\n## Status\n\nBLOCKED\n")
        report = self.report()
        self.assertEqual(report["summary"]["blocked_handoffs"], 1)
        self.assertEqual(report["summary"]["open_owner_gates"], 1)

    def test_low_activity_fallback_is_unknown_without_dates(self):
        fallback = self.report()["low_activity_fallback"]
        self.assertIsNone(fallback["last_evidence_change"])
        self.assertIn("unknown", fallback["status"])


@unittest.skipUnless(shutil.which("git"), "git is not installed")
class GitDatedFixtureTests(unittest.TestCase):
    """The git path: last-changed dates drive the due/not-due answer."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        build_fixture(self.root)
        self.git("init", "--quiet")
        self.commit("2026-08-01T09:00:00")
        write(self.root, "practices/002-workflow-redesign.md", "# Practice\n")
        self.commit("2026-09-01T09:00:00")

    def git(self, *args: str, env_date: str | None = None) -> None:
        env = os.environ.copy()
        # Point HOME at the fixture so a developer's global git config, hooks,
        # and signing settings cannot change the result.
        env["HOME"] = str(self.root)
        if env_date:
            env["GIT_AUTHOR_DATE"] = env_date
            env["GIT_COMMITTER_DATE"] = env_date
        subprocess.run(
            ["git", "-C", str(self.root), "-c", "user.email=t@example.com", "-c", "user.name=Test",
             "-c", "commit.gpgsign=false", *args],
            check=True,
            capture_output=True,
            env=env,
        )

    def commit(self, iso_datetime: str) -> None:
        self.git("add", "--all")
        self.git("commit", "--quiet", "--no-verify", "-m", "fixture", env_date=iso_datetime)

    def test_dates_come_from_git_history(self):
        report = run_json(self.root)
        self.assertTrue(report["git"]["available"])
        passes = {entry["id"]: entry for entry in report["passes"]}
        self.assertEqual(passes["build"]["last_output_change"], "2026-09-01")
        self.assertEqual(passes["review"]["last_output_change"], "2026-08-01")

    def test_stale_pass_is_due_and_fresh_pass_is_not(self):
        passes = {entry["id"]: entry for entry in run_json(self.root)["passes"]}
        self.assertFalse(passes["build"]["due"])
        self.assertEqual(passes["build"]["status"], "within window")
        self.assertTrue(passes["review"]["due"])
        self.assertEqual(passes["review"]["status"], "window elapsed")
        self.assertEqual(passes["review"]["days_since"], 32)

    def test_on_trigger_pass_stays_not_due_however_old_it_is(self):
        passes = {entry["id"]: entry for entry in run_json(self.root)["passes"]}
        self.assertEqual(passes["release"]["last_output_change"], "2026-08-01")
        self.assertFalse(passes["release"]["due"])
        self.assertIn("not scheduled", passes["release"]["status"])

    def test_uncommitted_evidence_is_reported_as_untracked(self):
        write(self.root, "practices/003-verification-gate.md", "# Practice\n")
        passes = {entry["id"]: entry for entry in run_json(self.root)["passes"]}
        self.assertEqual(passes["build"]["untracked_evidence"], ["practices/003-verification-gate.md"])

    def test_low_activity_fallback_window_uses_the_newest_evidence(self):
        fallback = run_json(self.root)["low_activity_fallback"]
        self.assertEqual(fallback["last_evidence_change"], "2026-09-01")
        self.assertEqual(fallback["status"], "within window")


class ConfigurationErrorTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def run_with(self, config: dict | None) -> tuple[int, str, str]:
        build_fixture(self.root, config or minimal_config())
        return run_main(["--root", str(self.root), "--as-of", "2026-09-02"])

    def test_missing_config_exits_one_with_a_fix(self):
        build_fixture(self.root)
        (self.root / "ops" / "cadence.yaml").unlink()
        code, _, err = run_main(["--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("Missing cadence configuration", err)
        self.assertIn("--config", err)

    def test_unreadable_yaml_exits_one(self):
        build_fixture(self.root)
        write(self.root, "ops/cadence.yaml", "passes: [\n")
        code, _, err = run_main(["--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("Could not parse", err)

    def test_wrong_schema_version_exits_one(self):
        code, _, err = self.run_with(minimal_config(schema_version=99))
        self.assertEqual(code, 1)
        self.assertIn("schema_version", err)

    def test_staleness_limit_must_match_check_links(self):
        code, _, err = self.run_with(minimal_config(staleness_limit_days=45))
        self.assertEqual(code, 1)
        self.assertIn("one staleness rule", err)

    def test_owner_role_naming_a_person_is_rejected(self):
        config = minimal_config()
        config["passes"][0]["owner_role"] = "Dakota"
        code, _, err = self.run_with(config)
        self.assertEqual(code, 1)
        self.assertIn("names a person", err)

    def test_elapsed_pass_without_an_interval_is_rejected(self):
        config = minimal_config()
        config["passes"][0]["interval_days"] = None
        code, _, err = self.run_with(config)
        self.assertEqual(code, 1)
        self.assertIn("interval_days", err)

    def test_on_trigger_pass_with_an_interval_is_rejected(self):
        config = minimal_config()
        config["passes"][2]["interval_days"] = 7
        code, _, err = self.run_with(config)
        self.assertEqual(code, 1)
        self.assertIn("never uses a window", err)

    def test_unknown_due_rule_is_rejected(self):
        config = minimal_config()
        config["passes"][0]["due_rule"] = "whenever"
        code, _, err = self.run_with(config)
        self.assertEqual(code, 1)
        self.assertIn("due_rule", err)

    def test_duplicate_pass_id_is_rejected(self):
        config = minimal_config()
        config["passes"][1]["id"] = "build"
        code, _, err = self.run_with(config)
        self.assertEqual(code, 1)
        self.assertIn("more than once", err)

    def test_missing_required_pass_key_is_rejected(self):
        config = minimal_config()
        del config["passes"][0]["skip_rule"]
        code, _, err = self.run_with(config)
        self.assertEqual(code, 1)
        self.assertIn("skip_rule", err)

    def test_unknown_queue_check_is_rejected(self):
        config = minimal_config()
        config["queues"][1]["repo_check"] = "read_buzz"
        code, _, err = self.run_with(config)
        self.assertEqual(code, 1)
        self.assertIn("repo_check", err)

    def test_bad_root_exits_one(self):
        code, _, err = run_main(["--root", str(self.root / "nope")])
        self.assertEqual(code, 1)
        self.assertIn("not a directory", err)

    def test_usage_error_exits_one(self):
        code, _, err = run_main(["--as-of", "not-a-date"])
        self.assertEqual(code, 1)
        self.assertIn("YYYY-MM-DD", err)


class RealRepositoryTests(unittest.TestCase):
    """Smoke test against the repository this script ships in."""

    def test_report_runs_and_reports_every_documented_pass(self):
        report = run_json(REPOSITORY_ROOT)
        self.assertEqual(report["source"], "ops/WEEKLY_CADENCE.md")
        self.assertEqual(
            [entry["id"] for entry in report["passes"]],
            ["intake", "build", "review", "release", "session", "maintenance"],
        )
        for entry in report["passes"]:
            self.assertTrue(entry["evidence"], entry["id"])
            self.assertTrue(entry["named_output"], entry["id"])
            self.assertTrue(entry["owner_role"], entry["id"])

    def test_open_owner_gates_are_surfaced_from_the_owner_review_packet(self):
        report = run_json(REPOSITORY_ROOT)
        gates = report["checks"]["open_owner_gates"]
        self.assertTrue(gates["available"])
        self.assertGreaterEqual(report["summary"]["open_owner_gates"], 1)
        self.assertGreaterEqual(report["summary"]["open_operating_holds"], 1)

    def test_text_report_states_its_limits(self):
        code, out, _ = run_main(["--root", str(REPOSITORY_ROOT), "--as-of", "2026-09-02"])
        self.assertEqual(code, 0)
        self.assertIn("reads files in this repository only", out)
        self.assertIn("Buzz channel", out)
        self.assertIn("not overdue work for any person", out)

    def test_index_cites_only_sections_that_exist_in_the_cadence_document(self):
        config = yaml.safe_load((REPOSITORY_ROOT / "ops" / "cadence.yaml").read_text(encoding="utf-8"))
        document = (REPOSITORY_ROOT / "ops" / "WEEKLY_CADENCE.md").read_text(encoding="utf-8")
        headings = {
            match.group(1).strip()
            for match in re.finditer(r"^#{1,6}\s+(.*?)\s*$", document, re.MULTILINE)
        }
        cited = [config["operating_rule"]["source_section"], config["escalations"]["source_section"]]
        cited.append(config["low_activity_fallback"]["source_section"])
        cited.extend(entry["source_section"] for entry in config["passes"])
        cited.extend(entry["source_section"] for entry in config["queues"])
        for citation in cited:
            for segment in citation.split("/"):
                self.assertIn(segment.strip(), headings, citation)


if __name__ == "__main__":
    unittest.main()
