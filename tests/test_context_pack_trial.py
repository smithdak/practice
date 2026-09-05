"""Offline synthetic transport tests, not model performance evidence."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import context_pack_trial as trial

ROOT = Path(__file__).resolve().parents[1]


class TrialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "journal.sqlite"
        self.data = trial.load_cases(ROOT)
        self.config = {"session_id": "test-session", "start_date": "2026-09-04",
                       "total_budget_microusd": 300, "request_ceiling_microusd": 100,
                       "mode": "live", "model": "synthetic-test-double"}
        self.clock = lambda: datetime(2026, 9, 4, 12, tzinfo=timezone.utc)
        self.calls = []

    def session(self, config=None):
        session = trial.Session(self.path, config or self.config, self.data)
        self.addCleanup(session.close)
        return session

    def good(self, request):
        self.calls.append(request)
        return {"text": trial.encoded(trial.expected(self.data["cases"][0])),
                "usage": None, "cost_microusd": 70}

    def test_equal_source_access_no_answer_key(self):
        for case in self.data["cases"]:
            a, b = [trial.request_for(self.data, case, arm) for arm in ("baseline", "pack")]
            self.assertEqual(a["system"], b["system"])
            self.assertNotEqual(a["prompt"], b["prompt"])
            for rule in self.data["rules"]:
                self.assertEqual(a["prompt"].count(rule), 1)
                self.assertEqual(b["prompt"].count(rule), 1)
            for check in case["checks"]:
                for request in (a, b):
                    self.assertIn(trial.encoded(check), request["prompt"])
                    self.assertNotIn(trial.encoded(trial.expected(case)), request["prompt"])

    def test_pair_retained_and_duplicate_reuses_completed_calls(self):
        session = self.session()
        report = session.run_day(self.good, lambda: True, self.clock)
        self.assertEqual(len(self.calls), 2)
        self.assertTrue(all(c["rubric"]["passed"] for c in report["calls"]))
        self.assertTrue(report["human_review_required"])
        self.assertEqual(report, session.run_day(self.good, lambda: True, self.clock))
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(sum(c["reserved_microusd"] for c in report["calls"]), 200)
        self.assertIsNone(report["calls"][0]["response"]["usage"])

    def test_one_repair_total_primary_result_preserved(self):
        session = self.session()
        def bad(request):
            self.calls.append(request)
            return {"text": "not JSON", "usage": None, "cost_microusd": None}
        report = session.run_day(bad, lambda: True, self.clock)
        self.assertEqual([c["attempt"] for c in report["calls"]], [0, 0, 1])
        self.assertFalse(any(c["rubric"]["passed"] for c in report["calls"]))
        self.assertEqual(len(self.calls), 3)
        session.run_day(bad, lambda: True, self.clock)
        self.assertEqual(len(self.calls), 3)

    def test_budget_reserved_before_transport(self):
        config = dict(self.config, total_budget_microusd=100)
        session = self.session(config)
        with self.assertRaisesRegex(trial.Refused, "Budget"):
            session.run_day(self.good, lambda: True, self.clock)
        self.assertEqual(len(self.calls), 1)
        # Actual lower cost is deliberately NOT a refund.
        self.assertEqual(session.db.execute("SELECT SUM(ceiling) FROM calls").fetchone()[0], 100)

    def test_repair_cannot_rewrite_primary_pair(self):
        session = self.session()
        def first_bad(request):
            if not self.calls:
                self.calls.append(request)
                return {"text": "bad JSON", "usage": None, "cost_microusd": 70}
            return self.good(request)
        report = session.run_day(first_bad, lambda: True, self.clock)
        self.assertEqual(report["primary_pass"], {"baseline": False, "pack": True})
        self.assertEqual(report["primary_pack_minus_baseline"], 1)
        self.assertTrue(report["calls"][-1]["rubric"]["passed"])

    def test_crash_is_durable_and_blocks_blind_retry(self):
        session = self.session()
        def crash(request):
            self.calls.append(request)
            raise TimeoutError("outcome unknown")
        with self.assertRaises(TimeoutError):
            session.run_day(crash, lambda: True, self.clock)
        reopened = self.session()
        with self.assertRaisesRegex(trial.Refused, "Uncertain"):
            reopened.run_day(self.good, lambda: True, self.clock)
        self.assertEqual(len(self.calls), 1)

    def test_completed_call_survives_interruption_between_arms(self):
        session = self.session()
        def gate():
            return not self.calls
        with self.assertRaisesRegex(trial.Refused, "Kill switch"):
            session.run_day(self.good, gate, self.clock)
        reopened = self.session()
        report = reopened.run_day(self.good, lambda: True, self.clock)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(len(report["calls"]), 2)

    def test_stop_and_guard_refusal_prevent_transport(self):
        session = self.session()
        with self.assertRaises(trial.Refused):
            session.run_day(self.good, lambda: False, self.clock)
        session.stop()
        with self.assertRaises(trial.Refused):
            self.session().run_day(self.good, lambda: True, self.clock)
        self.assertEqual(self.calls, [])

    def test_expiry_and_naive_clock(self):
        session = self.session()
        for now in (datetime(2026, 9, 3, tzinfo=timezone.utc), datetime(2026, 9, 11, tzinfo=timezone.utc),
                    datetime(2026, 9, 4)):
            with self.assertRaises(trial.Refused):
                session.run_day(self.good, lambda: True, lambda value=now: value)
        self.assertEqual(self.calls, [])

    def test_binding_rejects_configuration_and_corpus_changes(self):
        self.session()
        with self.assertRaisesRegex(trial.Refused, "changed"):
            self.session(dict(self.config, total_budget_microusd=500))
        data = copy.deepcopy(self.data)
        data["rules"][0] += " Changed."
        with self.assertRaisesRegex(trial.Refused, "changed"):
            trial.Session(self.path, self.config, data)

    def test_overcharge_or_invalid_response_blocks_future_calls(self):
        session = self.session()
        def invalid(request):
            return {"text": "{}", "usage": None, "cost_microusd": 101}
        with self.assertRaisesRegex(trial.Refused, "over-budget"):
            session.run_day(invalid, lambda: True, self.clock)
        with self.assertRaisesRegex(trial.Refused, "Uncertain"):
            session.run_day(self.good, lambda: True, self.clock)

    def test_rubric_rejects_duplicate_missing_extra_and_claims(self):
        case = self.data["cases"][0]
        for change in (lambda r: r.update(launch_approved=True),
                       lambda r: r["checks"].append(r["checks"][0]),
                       lambda r: r["checks"].pop(),
                       lambda r: r.update(extra="unexpected"),
                       lambda r: r["checks"][0].update(source="invented")):
            response = trial.expected(case)
            change(response)
            self.assertFalse(trial.evaluate(case, json.dumps(response))["passed"])
        for response in ("null", "[]", "42", '{"checks":[{"id":[]}]}'):
            self.assertFalse(trial.evaluate(case, response)["passed"])

    def test_seven_days_replay_counterbalanced_and_labelled(self):
        report = trial.replay(ROOT)
        self.assertEqual(report["live_model_calls"], 0)
        self.assertEqual(len(report["reports"]), 7)
        self.assertEqual(report["reports"][0]["calls"][0]["arm"], "baseline")
        self.assertEqual(report["reports"][1]["calls"][0]["arm"], "pack")
        self.assertEqual(len({r["case_id"] for r in report["reports"]}), 7)

    def test_live_zero_reservation_is_rejected(self):
        with self.assertRaises(trial.Refused):
            self.session(dict(self.config, request_ceiling_microusd=0))

    def test_partial_prior_day_cannot_silently_advance(self):
        session = self.session()
        with self.assertRaises(trial.Refused):
            session.run_day(self.good, lambda: not self.calls, self.clock)
        with self.assertRaisesRegex(trial.Refused, "earlier day"):
            session.run_day(self.good, lambda: True, lambda: datetime(2026, 9, 5, tzinfo=timezone.utc))
        self.assertEqual(len(self.calls), 1)

    def test_second_connection_cannot_race_a_pending_call(self):
        session = self.session()
        other = self.session()
        def transport(request):
            with self.assertRaisesRegex(trial.Refused, "Uncertain"):
                other.run_day(self.good, lambda: True, self.clock)
            return self.good(request)
        session.run_day(transport, lambda: True, self.clock)
        self.assertEqual(len(self.calls), 2)


if __name__ == "__main__":
    unittest.main()
