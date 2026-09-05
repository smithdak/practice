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
                       "mode": "live", "model": "gpt-5.6-terra", "reasoning_effort": "medium"}
        self.clock = lambda: datetime(2026, 9, 4, 12, tzinfo=timezone.utc)
        self.calls = []

    def session(self, config=None):
        session = trial.Session(self.path, config or self.config, self.data)
        self.addCleanup(session.close)
        return session

    def request_config(self, lane="supervised", cap=21):
        return {"session_id": "request-session", "start_date": "2026-09-04",
                "mode": "live", "model": "gpt-5.6-terra", "reasoning_effort": "medium",
                "accounting": "requests", "lane": lane, "session_invocation_cap": cap}

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

    def test_selected_model_and_reasoning_reach_both_arms_and_repair(self):
        def bad(request):
            self.calls.append(request)
            return {"text": "bad JSON", "usage": None, "cost_microusd": 70}
        report = self.session().run_day(bad, lambda: True, self.clock)
        self.assertEqual(len(self.calls), 3)
        for request in self.calls:
            self.assertEqual(request["model"], "gpt-5.6-terra")
            self.assertEqual(request["reasoning_effort"], "medium")
        self.assertEqual(report["model"], "gpt-5.6-terra")
        self.assertEqual(report["reasoning_effort"], "medium")

    def test_missing_or_unselected_model_settings_refused_before_transport(self):
        missing = dict(self.config)
        del missing["reasoning_effort"]
        for config in (missing, dict(self.config, reasoning_effort="high"),
                       dict(self.config, reasoning_effort=None),
                       dict(self.config, model="gpt-5.6-luna")):
            with self.subTest(config=config), self.assertRaises(trial.Refused):
                self.session(config)
        self.assertEqual(self.calls, [])

    def test_reasoning_cannot_change_in_running_session(self):
        session = self.session()
        session.config["reasoning_effort"] = "high"
        with self.assertRaises(trial.Refused):
            session.run_day(self.good, lambda: True, self.clock)
        self.assertEqual(self.calls, [])

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

    def test_request_accounting_refuses_legacy_journal_before_schema_migration(self):
        self.session()
        with self.assertRaisesRegex(trial.Refused, "changed"):
            self.session(self.request_config())

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
        self.assertTrue(all(r["reasoning_effort"] == "none" for r in report["reports"]))
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

    def test_supervised_allows_distinct_same_day_cases_without_daily_cycle_claim(self):
        session = self.session(self.request_config())
        def good_for_requested_case(request):
            self.calls.append(request)
            case = next(c for c in self.data["cases"] if trial.encoded(c["checks"][0]) in request["prompt"])
            return {"text": trial.encoded(trial.expected(case)), "usage": None, "cost_microusd": None}
        first = session.run_trial("owner-1", "all-pass", good_for_requested_case, lambda: True, self.clock)
        second = session.run_trial("owner-2", "whitespace-failure", good_for_requested_case, lambda: True, self.clock)
        self.assertEqual(len(self.calls), 4)
        self.assertEqual(first["trial_id"], "owner-1")
        self.assertEqual(second["trial_id"], "owner-2")
        self.assertEqual(len(first["calls"]), 2)
        self.assertEqual(len(second["calls"]), 2)
        self.assertEqual(first["lane"], "supervised")
        self.assertNotIn("daily", first["interpretation"].lower())
        self.assertEqual(first["calls"][0]["response"]["cost_microusd"], None)
        self.assertNotIn("max_charge_microusd", self.calls[0])
        self.assertEqual(first, session.run_trial("owner-1", "all-pass", good_for_requested_case, lambda: True, self.clock))

    def test_supervised_trial_id_is_idempotent_and_case_cannot_be_reused(self):
        session = self.session(self.request_config())
        report = session.run_trial("owner-1", "all-pass", self._request_good, lambda: True, self.clock)
        self.assertEqual(report, session.run_trial("owner-1", "all-pass", self._request_good, lambda: True, self.clock))
        self.assertEqual(len(self.calls), 2)
        with self.assertRaisesRegex(trial.Refused, "already has a trial ID"):
            session.run_trial("owner-2", "all-pass", self._request_good, lambda: True, self.clock)
        with self.assertRaisesRegex(trial.Refused, "changed"):
            session.run_trial("owner-1", "whitespace-failure", self._request_good, lambda: True, self.clock)

    def _request_good(self, request):
        self.calls.append(request)
        case = next(c for c in self.data["cases"] if trial.encoded(c["checks"][0]) in request["prompt"])
        return {"text": trial.encoded(trial.expected(case)), "usage": None, "cost_microusd": None}

    def test_background_is_one_paired_trial_per_day(self):
        session = self.session(self.request_config(lane="background"))
        session.run_trial("background-a", "all-pass", self._request_good, lambda: True, self.clock)
        with self.assertRaisesRegex(trial.Refused, "one paired trial"):
            session.run_trial("background-b", "whitespace-failure", self._request_good, lambda: True, self.clock)
        self.assertEqual(len(self.calls), 2)

    def test_request_session_cap_counts_attempts_before_transport(self):
        session = self.session(self.request_config(cap=2))
        session.run_trial("owner-1", "all-pass", self._request_good, lambda: True, self.clock)
        with self.assertRaisesRegex(trial.Refused, "invocation cap"):
            session.run_trial("owner-2", "whitespace-failure", self._request_good, lambda: True, self.clock)
        self.assertEqual(len(self.calls), 2)

    def test_request_pending_crash_expiry_and_configuration_mixing_refuse(self):
        session = self.session(self.request_config())
        def crash(request):
            self.calls.append(request)
            raise TimeoutError("outcome unknown")
        with self.assertRaises(TimeoutError):
            session.run_trial("owner-1", "all-pass", crash, lambda: True, self.clock)
        with self.assertRaisesRegex(trial.Refused, "Uncertain"):
            session.run_trial("owner-1", "all-pass", self._request_good, lambda: True, self.clock)
        fresh = self.session(self.request_config())
        with self.assertRaisesRegex(trial.Refused, "seven-day"):
            fresh.run_trial("owner-x", "all-pass", self._request_good, lambda: True,
                            lambda: datetime(2026, 9, 11, tzinfo=timezone.utc))
        mixed = dict(self.request_config(), total_budget_microusd=1)
        with self.assertRaises(trial.Refused):
            trial.validate_config(mixed)
        with self.assertRaises(trial.Refused):
            trial.validate_config(self.request_config(cap=False))

    def test_request_active_trial_blocks_parallel_owner_work_and_resumes(self):
        session = self.session(self.request_config())
        other = self.session(self.request_config())
        with self.assertRaisesRegex(trial.Refused, "Kill switch"):
            session.run_trial("owner-1", "all-pass", self._request_good,
                              lambda: len(self.calls) == 0, self.clock)
        with self.assertRaisesRegex(trial.Refused, "active trial"):
            other.run_trial("owner-2", "whitespace-failure", self._request_good, lambda: True, self.clock)
        report = session.run_trial("owner-1", "all-pass", self._request_good, lambda: True, self.clock)
        self.assertEqual(len(report["calls"]), 2)
        self.assertEqual(len(self.calls), 2)

    def test_background_active_previous_day_cannot_advance_without_a_pending_call(self):
        session = self.session(self.request_config(lane="background"))
        with session.db:
            session.db.execute("INSERT INTO request_trials (trial_id,day,case_id,lane,status) VALUES (?,?,?,?,?)",
                               ("background-old", "2026-09-04", "all-pass", "background", "active"))
        with self.assertRaisesRegex(trial.Refused, "active trial"):
            session.run_day(self._request_good, lambda: True,
                            lambda: datetime(2026, 9, 5, 12, tzinfo=timezone.utc))
        self.assertEqual(self.calls, [])

    def test_request_lane_cap_and_model_drift_are_immutable(self):
        self.session(self.request_config())
        for changed in (self.request_config(lane="background"), self.request_config(cap=22),
                        dict(self.request_config(), model="gpt-5.6-luna")):
            with self.subTest(changed=changed), self.assertRaisesRegex(trial.Refused, "changed|Pilot requires"):
                self.session(changed)


if __name__ == "__main__":
    unittest.main()
