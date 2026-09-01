from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


steward_readiness = load_module(
    "practice_steward_readiness", REPOSITORY_ROOT / "scripts" / "steward_readiness_check.py"
)


STEWARD_FIXTURE = """# Practice Steward

## Mission

Route members to one useful next action.

## Deployment prerequisite: actionable human escalation

Do not enable this profile until the human sponsor has configured and tested a
member-actionable escalation reference in a surface the Steward can see and
members can use. The deployment record must name the sponsor privately, state
which published label or route the agent may cite, and confirm that a human
monitors it.

If the reference is absent, inaccessible, or unverified, fail closed.

## Tools and channel access

Initial membership is limited to `start-here`, `ask-practice`, `learn`, `use`,
`automate`, `build`, and `transform`. It has no membership in `foundry`,
`maintainers`, `announcements`, `projects`, or `showcase`, and no owner,
maintainer, moderation, repository-write, identity-management, or private-key
privilege.
"""


SECURITY_FIXTURE = """# Buzz access and security runbook

## Least-membership model

| Identity | Accountable human | Initial channel membership | Explicitly excluded | Access rule |
| --- | --- | --- | --- | --- |
| Community owner (human) | Owner | All launch channels | None by default | Break-glass role. |
| Steward agent | Named human sponsor | `start-here`, `ask-practice`, `learn`, `use`, `automate`, `build`, `transform` | `foundry`, `maintainers`, `announcements`, `projects`, `showcase` | Routes from published artifacts. |
| Librarian agent | Named human sponsor | `ask-practice`, `learn` | `foundry`, `maintainers` | Proposes durable artifacts. |
"""


GOOD_INPUTS = {
    "sponsor_role": "community owner",
    "escalation_route": "the escalation label pinned on the start-here canvas",
    "receipt_target": "maintainers escalation rota, reviewed daily",
    "confirmed_test_receipt": True,
    "membership": "start-here,ask-practice,learn,use,automate,build,transform",
}

CONFIG_PATH_FLAG_ORDER = [
    ("sponsor_role", "--sponsor-role"),
    ("sponsor_name", "--sponsor-name"),
    ("escalation_route", "--escalation-route"),
    ("receipt_target", "--receipt-target"),
    ("test_receipt_date", "--test-receipt-date"),
]


def write_documents(
    root: Path,
    steward_text: str = STEWARD_FIXTURE,
    security_text: str = SECURITY_FIXTURE,
) -> tuple[Path, Path]:
    steward = root / "buzz" / "agents" / "STEWARD.md"
    steward.parent.mkdir(parents=True, exist_ok=True)
    steward.write_text(steward_text, encoding="utf-8")
    security = root / "ops" / "BUZZ_SECURITY.md"
    security.parent.mkdir(parents=True, exist_ok=True)
    security.write_text(security_text, encoding="utf-8")
    return steward, security


def build_args(steward: Path, security: Path, **overrides) -> list[str]:
    values = {**GOOD_INPUTS, **overrides}
    args = ["--steward-md", str(steward), "--security-md", str(security)]
    for key, flag in CONFIG_PATH_FLAG_ORDER:
        if values.get(key) is not None:
            args += [flag, str(values[key])]
    if values.get("confirmed_test_receipt"):
        args.append("--confirmed-test-receipt")
    if values.get("membership") is not None:
        args += ["--membership", values["membership"]]
    return args


def run_main(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = steward_readiness.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class FixtureContextMixin(unittest.TestCase):
    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name)

    def make_docs(self, **kwargs) -> tuple[Path, Path]:
        return write_documents(self.root, **kwargs)

    def run_good(self, **overrides) -> tuple[int, str, str]:
        steward, security = self.make_docs()
        return run_main(build_args(steward, security, **overrides))


class AllSatisfiedTests(FixtureContextMixin):
    def test_all_prerequisites_satisfied_exits_zero(self):
        code, out, err = self.run_good()
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        for index in range(1, 6):
            self.assertIn(f"[PASS] {index}.", out)
        self.assertNotIn("[FAIL]", out)
        self.assertIn("5/5 prerequisites satisfied", out)

    def test_output_is_deterministic(self):
        first = self.run_good()
        second = self.run_good()
        self.assertEqual(first, second)

    def test_sponsor_name_produced_privacy_note(self):
        code, out, _ = self.run_good(sponsor_name="Dakota")
        self.assertEqual(code, 0)
        self.assertIn("private deployment record", out)
        self.assertIn("Never place it in the public Steward profile", out)

    def test_config_file_alone_can_satisfy_everything(self):
        steward, security = self.make_docs()
        config = self.root / "readiness.json"
        config.write_text(
            json.dumps(
                {
                    "sponsor_role": "community owner",
                    "escalation_route": "the escalation label pinned on the start-here canvas",
                    "receipt_target": "maintainers escalation rota, reviewed daily",
                    "test_receipt_date": "2026-08-31",
                    "membership": [
                        "start-here",
                        "ask-practice",
                        "learn",
                        "use",
                        "automate",
                        "build",
                        "transform",
                    ],
                }
            ),
            encoding="utf-8",
        )
        code, out, _ = run_main(
            ["--config", str(config), "--steward-md", str(steward), "--security-md", str(security)]
        )
        self.assertEqual(code, 0)
        self.assertIn("5/5 prerequisites satisfied", out)

    def test_flags_override_config_values(self):
        steward, security = self.make_docs()
        config = self.root / "readiness.json"
        config.write_text(
            json.dumps(
                {
                    "sponsor_role": "community owner",
                    "escalation_route": "post in maintainers",
                    "receipt_target": "maintainers escalation rota, reviewed daily",
                    "confirmed_test_receipt": True,
                    "membership": "start-here,ask-practice,learn,use,automate,build,transform",
                }
            ),
            encoding="utf-8",
        )
        code, out, _ = run_main(
            [
                "--config",
                str(config),
                "--escalation-route",
                "the escalation label pinned on the start-here canvas",
                "--steward-md",
                str(steward),
                "--security-md",
                str(security),
            ]
        )
        self.assertEqual(code, 0)
        self.assertIn("5/5 prerequisites satisfied", out)


class UnmetPrerequisitesTests(FixtureContextMixin):
    def test_no_prerequisite_inputs_fails_all_five_checks(self):
        steward, security = self.make_docs()
        code, out, _ = run_main(["--steward-md", str(steward), "--security-md", str(security)])
        self.assertEqual(code, 1)
        self.assertEqual(out.count("[FAIL]"), 5)
        self.assertIn("0/5 prerequisites satisfied", out)
        self.assertIn("Do not enable the Steward", out)


class SponsorTests(FixtureContextMixin):
    def test_missing_sponsor_role_fails_with_flag_guidance(self):
        code, out, _ = self.run_good(sponsor_role=None)
        self.assertEqual(code, 1)
        self.assertIn("FAIL [sponsor]", out)
        self.assertIn("--sponsor-role", out)

    def test_blank_sponsor_role_fails(self):
        code, out, _ = self.run_good(sponsor_role="   ")
        self.assertEqual(code, 1)
        self.assertIn("FAIL [sponsor]", out)

    def test_secret_shaped_sponsor_role_is_refused(self):
        code, out, _ = self.run_good(sponsor_role="owner token abcdef1234567890")
        self.assertEqual(code, 1)
        self.assertIn("never handles keys or credentials", out)


class EscalationRouteTests(FixtureContextMixin):
    def test_missing_route_fails_with_guidance(self):
        code, out, _ = self.run_good(escalation_route=None)
        self.assertEqual(code, 1)
        self.assertIn("FAIL [route]", out)
        self.assertIn("--escalation-route", out)

    def test_route_citing_excluded_channel_fails(self):
        code, out, _ = self.run_good(escalation_route="post the escalation in maintainers")
        self.assertEqual(code, 1)
        self.assertIn("FAIL [route]", out)
        self.assertIn("maintainers", out)
        self.assertIn("excludes", out)

    def test_route_citing_direct_message_fails(self):
        code, out, _ = self.run_good(
            escalation_route="send a direct message to the on-call human"
        )
        self.assertEqual(code, 1)
        self.assertIn("FAIL [route]", out)
        self.assertIn("direct message", out)

    def test_route_without_visible_anchor_fails(self):
        code, out, _ = self.run_good(escalation_route="the pinned escalation label")
        self.assertEqual(code, 1)
        self.assertIn("FAIL [route]", out)
        self.assertIn("does not name a surface the Steward can see", out)

    def test_partial_channel_name_does_not_count_as_anchor(self):
        code, out, _ = self.run_good(escalation_route="see the task-practice escalation page")
        self.assertEqual(code, 1)
        self.assertIn("does not name a surface the Steward can see", out)

    def test_route_with_email_address_is_refused(self):
        code, out, _ = self.run_good(
            escalation_route="email escalations@example.com from the start-here canvas"
        )
        self.assertEqual(code, 1)
        self.assertIn("never handles keys or credentials", out)

    def test_member_visible_route_on_steward_channel_passes(self):
        code, out, _ = self.run_good(
            escalation_route="the escalation label on the ask-practice canvas"
        )
        self.assertEqual(code, 0)


class ReceiptTargetTests(FixtureContextMixin):
    def test_missing_receipt_target_fails(self):
        code, out, _ = self.run_good(receipt_target=None)
        self.assertEqual(code, 1)
        self.assertIn("FAIL [receipt]", out)
        self.assertIn("--receipt-target", out)

    def test_email_receipt_target_is_refused(self):
        code, out, _ = self.run_good(receipt_target="oncall-owner@example.com")
        self.assertEqual(code, 1)
        self.assertIn("never handles keys or credentials", out)

    def test_key_material_receipt_target_is_refused(self):
        code, out, _ = self.run_good(receipt_target="-----BEGIN PRIVATE KEY-----")
        self.assertEqual(code, 1)
        self.assertIn("never handles keys or credentials", out)


class TestReceiptTests(FixtureContextMixin):
    def test_unconfirmed_test_receipt_fails(self):
        code, out, _ = self.run_good(confirmed_test_receipt=False)
        self.assertEqual(code, 1)
        self.assertIn("FAIL [test receipt]", out)
        self.assertIn("fails closed", out)

    def test_flag_without_date_passes_with_dating_note(self):
        code, out, _ = self.run_good()
        self.assertEqual(code, 0)
        self.assertIn("NOTE [test receipt]", out)
        self.assertIn("Record the date", out)

    def test_dated_config_field_alone_passes_without_note(self):
        code, out, _ = self.run_good(
            confirmed_test_receipt=False, test_receipt_date="2026-08-31"
        )
        self.assertEqual(code, 0)
        self.assertNotIn("NOTE [test receipt]", out)

    def test_invalid_calendar_date_fails(self):
        code, out, _ = self.run_good(test_receipt_date="2026-13-40")
        self.assertEqual(code, 1)
        self.assertIn("not a valid calendar date", out)

    def test_wrong_date_format_fails(self):
        code, out, _ = self.run_good(test_receipt_date="31/08/2026")
        self.assertEqual(code, 1)
        self.assertIn("not a valid calendar date", out)


class MembershipTests(FixtureContextMixin):
    def test_missing_declaration_fails(self):
        code, out, _ = self.run_good(membership=None)
        self.assertEqual(code, 1)
        self.assertIn("FAIL [membership]", out)
        self.assertIn("--membership", out)

    def test_missing_channel_is_named(self):
        code, out, _ = self.run_good(
            membership="start-here,ask-practice,use,automate,build,transform"
        )
        self.assertEqual(code, 1)
        self.assertIn("missing required channels: learn", out)

    def test_excluded_channel_is_named(self):
        code, out, _ = self.run_good(
            membership="start-here,ask-practice,learn,use,automate,build,transform,foundry"
        )
        self.assertEqual(code, 1)
        self.assertIn("explicitly excludes", out)
        self.assertIn("foundry", out)

    def test_unknown_channel_is_named(self):
        code, out, _ = self.run_good(
            membership="start-here,ask-practice,learn,use,automate,build,transform,watercooler"
        )
        self.assertEqual(code, 1)
        self.assertIn("not in the Steward membership model", out)

    def test_duplicate_channel_is_named(self):
        code, out, _ = self.run_good(
            membership="start-here,start-here,ask-practice,learn,use,automate,build,transform"
        )
        self.assertEqual(code, 1)
        self.assertIn("more than once", out)

    def test_empty_channel_name_is_named(self):
        code, out, _ = self.run_good(membership="start-here,,learn")
        self.assertEqual(code, 1)
        self.assertIn("empty channel name", out)

    def test_whitespace_around_commas_is_tolerated(self):
        code, out, _ = self.run_good(
            membership="start-here, ask-practice, learn, use, automate, build, transform"
        )
        self.assertEqual(code, 0)

    def test_membership_config_string_form_is_accepted(self):
        steward, security = self.make_docs()
        config = self.root / "readiness.json"
        config.write_text(
            json.dumps(
                {
                    "sponsor_role": "community owner",
                    "escalation_route": "the escalation label pinned on the start-here canvas",
                    "receipt_target": "maintainers escalation rota, reviewed daily",
                    "test_receipt_date": "2026-08-31",
                    "membership": "start-here,ask-practice,learn,use,automate,build,transform",
                }
            ),
            encoding="utf-8",
        )
        code, out, _ = run_main(
            ["--config", str(config), "--steward-md", str(steward), "--security-md", str(security)]
        )
        self.assertEqual(code, 0)


class ConfigFileErrorTests(FixtureContextMixin):
    def test_unknown_config_key_fails(self):
        steward, security = self.make_docs()
        config = self.root / "readiness.json"
        config.write_text(json.dumps({"sponser_role": "community owner"}), encoding="utf-8")
        code, out, _ = run_main(
            ["--config", str(config), "--steward-md", str(steward), "--security-md", str(security)]
        )
        self.assertEqual(code, 1)
        self.assertIn("unknown key(s)", out)
        self.assertIn("sponser_role", out)

    def test_invalid_json_fails(self):
        steward, security = self.make_docs()
        config = self.root / "readiness.json"
        config.write_text("{oops", encoding="utf-8")
        code, out, _ = run_main(
            ["--config", str(config), "--steward-md", str(steward), "--security-md", str(security)]
        )
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", out)

    def test_non_string_scalar_fails(self):
        steward, security = self.make_docs()
        config = self.root / "readiness.json"
        config.write_text(json.dumps({"sponsor_role": 7}), encoding="utf-8")
        code, out, _ = run_main(
            ["--config", str(config), "--steward-md", str(steward), "--security-md", str(security)]
        )
        self.assertEqual(code, 1)
        self.assertIn("sponsor_role in", out)
        self.assertIn("must be a string", out)

    def test_unreadable_config_fails(self):
        steward, security = self.make_docs()
        code, out, _ = run_main(
            [
                "--config",
                str(self.root / "missing.json"),
                "--steward-md",
                str(steward),
                "--security-md",
                str(security),
            ]
        )
        self.assertEqual(code, 1)
        self.assertIn("cannot read", out)


class DriftDetectionTests(FixtureContextMixin):
    def test_missing_prerequisite_heading_is_drift(self):
        drifted = STEWARD_FIXTURE.replace(
            "## Deployment prerequisite: actionable human escalation",
            "## Deployment prerequisite",
        )
        steward, security = self.make_docs(steward_text=drifted)
        code, out, _ = run_main(build_args(steward, security))
        self.assertEqual(code, 1)
        self.assertIn("DRIFT", out)
        self.assertIn("0/5 prerequisites evaluated", out)
        self.assertNotIn("[PASS]", out)

    def test_changed_membership_sentence_is_drift(self):
        drifted = STEWARD_FIXTURE.replace("`, `use`", "`")
        steward, security = self.make_docs(steward_text=drifted)
        code, out, _ = run_main(build_args(steward, security))
        self.assertEqual(code, 1)
        self.assertIn("DRIFT", out)
        self.assertIn("initial membership", out)

    def test_changed_exclusion_sentence_is_drift(self):
        drifted = STEWARD_FIXTURE.replace("`projects`", "")
        steward, security = self.make_docs(steward_text=drifted)
        code, out, _ = run_main(build_args(steward, security))
        self.assertEqual(code, 1)
        self.assertIn("DRIFT", out)
        self.assertIn("excluded channels", out)

    def test_missing_fail_closed_phrase_is_drift(self):
        drifted = STEWARD_FIXTURE.replace("fail closed", "stop and ask a human")
        steward, security = self.make_docs(steward_text=drifted)
        code, out, _ = run_main(build_args(steward, security))
        self.assertEqual(code, 1)
        self.assertIn("DRIFT", out)

    def test_changed_runbook_steward_row_is_drift(self):
        drifted = SECURITY_FIXTURE.replace("`use`, `automate`", "`automate`")
        steward, security = self.make_docs(security_text=drifted)
        code, out, _ = run_main(build_args(steward, security))
        self.assertEqual(code, 1)
        self.assertIn("DRIFT", out)
        self.assertIn("ops", out)

    def test_missing_runbook_steward_row_is_drift(self):
        drifted = "\n".join(
            line
            for line in SECURITY_FIXTURE.splitlines()
            if not line.strip().startswith("| Steward agent")
        )
        steward, security = self.make_docs(security_text=drifted)
        code, out, _ = run_main(build_args(steward, security))
        self.assertEqual(code, 1)
        self.assertIn("DRIFT", out)
        self.assertIn("| Steward agent", out)

    def test_missing_source_file_is_reported(self):
        code, out, _ = run_main(
            [
                "--steward-md",
                str(self.root / "nowhere" / "STEWARD.md"),
                "--security-md",
                str(self.root / "nowhere" / "BUZZ_SECURITY.md"),
            ]
        )
        self.assertEqual(code, 1)
        self.assertIn("DRIFT", out)
        self.assertIn("cannot read", out)


class HelpAndRealRepositoryTests(unittest.TestCase):
    def test_help_states_prerequisite_checker_not_enabler(self):
        out, err = io.StringIO(), io.StringIO()
        with self.assertRaises(SystemExit) as raised:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                steward_readiness.main(["--help"])
        self.assertEqual(raised.exception.code, 0)
        text = " ".join((out.getvalue() + err.getvalue()).split())
        self.assertIn("prerequisite checker, not an enabler", text)
        self.assertIn("never handles keys or credentials", text)
        self.assertIn("human decision", text)

    def test_real_repository_documents_pass_drift_detection(self):
        steward = REPOSITORY_ROOT / "buzz" / "agents" / "STEWARD.md"
        security = REPOSITORY_ROOT / "ops" / "BUZZ_SECURITY.md"
        if not (steward.exists() and security.exists()):
            self.skipTest("repository source documents not present")
        code, out, _ = run_main(["--steward-md", str(steward), "--security-md", str(security)])
        self.assertEqual(code, 1)
        self.assertNotIn("DRIFT", out)
        self.assertEqual(out.count("[FAIL]"), 5)
        self.assertIn("0/5 prerequisites satisfied", out)


if __name__ == "__main__":
    unittest.main()
