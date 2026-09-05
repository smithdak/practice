"""Synthetic integration coverage for the owner-operated context-pack runner."""
from datetime import datetime, timezone
from contextlib import redirect_stderr
import io
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import context_pack_trial as kernel
import run_context_pack as runner


class RunContextPackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.root = base / "canonical"
        cases = self.root / "ops" / "experiments" / "context-pack"
        cases.mkdir(parents=True)
        shutil.copy2(Path(__file__).resolve().parents[1] / "ops" / "experiments" /
                     "context-pack" / "cases.json", cases / "cases.json")
        self.private = base / "private"
        self.clock = lambda: datetime(2026, 9, 5, 12, tzinfo=timezone.utc)
        self.config = {"session_id": "owner-session", "start_date": "2026-09-05",
                       "mode": "live", "model": "gpt-5.6-terra", "reasoning_effort": "medium",
                       "accounting": "requests", "lane": "supervised", "session_invocation_cap": 21}
        self.contract = {"provider": "synthetic", "revision": "test-1"}
        self.calls = []

    def transport(self, request):
        self.calls.append(request)
        case = next(item for item in kernel.load_cases(self.root)["cases"]
                    if kernel.encoded(item["checks"][0]) in request["prompt"])
        return {"text": kernel.encoded(kernel.expected(case)), "usage": None, "cost_microusd": None}

    def run_trial(self, trial_id, case_id, *, contract=None):
        return runner.run_supervised(self.root, self.private, self.config, trial_id, case_id,
                                     self.transport, self.contract if contract is None else contract, self.clock)

    def test_two_same_day_trials_persist_separately_and_prior_result_is_stable(self):
        first_path, first = self.run_trial("trial-one", "all-pass")
        second_path, second = self.run_trial("trial-two", "whitespace-failure")
        self.assertEqual(len(self.calls), 4)
        self.assertTrue(first_path.is_file())
        self.assertTrue(second_path.is_file())
        self.assertNotEqual(first_path, second_path)
        self.assertEqual(first["trial_id"], "trial-one")
        self.assertEqual(second["trial_id"], "trial-two")
        self.assertEqual(first["session_invocations"], 2)
        replay_path, replay = self.run_trial("trial-one", "all-pass")
        self.assertEqual(replay_path, first_path)
        self.assertEqual(replay, first)
        self.assertEqual(len(self.calls), 4)
        self.assertEqual(first_path.read_bytes(), replay_path.read_bytes())

    def test_completed_journal_recovers_after_report_store_failure_without_transport_retry(self):
        with patch.object(runner, "persist_report", side_effect=runner.StoreRefused("store unavailable")):
            with self.assertRaisesRegex(runner.StoreRefused, "store unavailable"):
                self.run_trial("trial-one", "all-pass")
        self.assertEqual(len(self.calls), 2)
        target, report = self.run_trial("trial-one", "all-pass")
        self.assertTrue(target.is_file())
        self.assertEqual(report["trial_id"], "trial-one")
        self.assertEqual(len(self.calls), 2)

    def test_transport_contract_drift_refuses_before_any_new_transport_call(self):
        self.run_trial("trial-one", "all-pass")
        with self.assertRaisesRegex(kernel.Refused, "Transport contract changed"):
            self.run_trial("trial-two", "whitespace-failure", contract={"provider": "synthetic", "revision": "test-2"})
        self.assertEqual(len(self.calls), 2)

    def test_stop_marker_prevents_new_calls_and_never_refunds_completed_attempts(self):
        self.run_trial("trial-one", "all-pass")
        runner.stop_session(self.private, self.config["session_id"])
        with self.assertRaises(kernel.Refused):
            self.run_trial("trial-two", "whitespace-failure")
        self.assertEqual(len(self.calls), 2)
        journal = self.private / "sessions" / self.config["session_id"] / "journal.sqlite"
        database = sqlite3.connect(journal)
        try:
            self.assertEqual(database.execute("SELECT COUNT(*) FROM calls").fetchone()[0], 2)
            self.assertEqual(database.execute("SELECT COUNT(*) FROM calls WHERE status='completed'").fetchone()[0], 2)
        finally:
            database.close()

    def test_cli_refuses_unapproved_or_unsupported_background_before_adapter_creation(self):
        with redirect_stderr(io.StringIO()):
            with patch.object(runner, "CodexTransport") as adapter:
                self.assertEqual(runner.main(["run"]), 1)
                adapter.assert_not_called()
            with patch.object(runner, "CodexTransport") as adapter:
                with self.assertRaises(SystemExit) as exited:
                    runner.main(["background"])
                self.assertEqual(exited.exception.code, 2)
                adapter.assert_not_called()


if __name__ == "__main__":
    unittest.main()
