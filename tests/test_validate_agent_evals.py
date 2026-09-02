"""Failure-mode coverage for scripts/validate_agent_evals.py.

Every test builds a synthetic repository root in a temporary directory, breaks
exactly one thing, and asserts that the validator says so. Two tests run against
the real repository - one that the committed suites pass, and one that drops a
required adversarial topic from a real suite and proves the coverage check
fails - so the fixtures cannot drift into describing suites the repository does
not have.
"""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import shutil
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


validate_agent_evals = load_module(
    "practice_validate_agent_evals",
    REPOSITORY_ROOT / "scripts" / "validate_agent_evals.py",
)

TOPICS = validate_agent_evals.ADVERSARIAL_TOPICS

PROFILE_PATH = "buzz/agents/EXAMPLE.md"

README = """# Example community-agent eval suites

These files define cases. No run has occurred, and defining a case is not
evidence that an agent passed it. Owner gate 6 is OPEN, so no agent is enabled.
"""


def make_case(case_id: str, kind: str, severity: str) -> dict:
    return {
        "id": case_id,
        "kind": kind,
        "severity": severity,
        "input": "A member sends a message that exercises this boundary.",
        "expected": ["The agent stays inside the bounds its profile states."],
        "forbidden": ["The agent crosses the boundary the profile forbids."],
    }


def base_suite(agent_id: str = "example-agent", profile: str = PROFILE_PATH) -> dict:
    prefix = agent_id.split("-")[0]
    cases = [
        make_case(f"{prefix}-route-direct", "routing.direct", "major"),
        make_case(f"{prefix}-route-negative", "routing.negative", "major"),
        make_case(f"{prefix}-behavior-bounded", "behavior.bounded-scope", "severe"),
        make_case(f"{prefix}-behavior-shape", "behavior.packet-shape", "minor"),
    ]
    cases.extend(
        make_case(f"{prefix}-adv-{topic}", f"adversarial.{topic}", "severe") for topic in TOPICS
    )
    return {
        "schema_version": 1,
        "agent_id": agent_id,
        "profile": profile,
        "profile_basis": {
            "profile_version": "not-versioned",
            "source_commit": "0123456789abcdef0123456789abcdef01234567",
            "reviewed": "2026-09-02",
        },
        "execution": {
            "minimum_model_families": 2,
            "when_unavailable": "record-limitation-and-do-not-count-as-pass",
        },
        "inapplicable_topics": [],
        "cases": cases,
    }


def write_root(
    root: Path,
    *,
    suites: dict[str, dict] | None = None,
    registry_agents: object = None,
    readme: str | None = README,
    profiles: tuple[str, ...] = (PROFILE_PATH,),
) -> Path:
    if suites is None:
        suites = {"example-agent": base_suite()}
    if registry_agents is None:
        registry_agents = [{"id": "example-agent", "profile": PROFILE_PATH}]

    evals_dir = root / "buzz" / "agents" / "evals"
    evals_dir.mkdir(parents=True, exist_ok=True)
    for profile in profiles:
        path = root / profile
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Example agent profile\n", encoding="utf-8")
    if registry_agents != "omit":
        (root / "buzz" / "agents" / "registry.yaml").write_text(
            yaml.safe_dump({"schema_version": 1, "agents": registry_agents}, sort_keys=False),
            encoding="utf-8",
        )
    if readme is not None:
        (evals_dir / "README.md").write_text(readme, encoding="utf-8")
    for name, suite in suites.items():
        (evals_dir / f"{name}.yaml").write_text(
            yaml.safe_dump(suite, sort_keys=False), encoding="utf-8"
        )
    return root


class ValidatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def run_validator(self, **kwargs) -> list[str]:
        write_root(self.root, **kwargs)
        return validate_agent_evals.validate(self.root)

    def assertPasses(self, errors: list[str]) -> None:
        self.assertEqual(errors, [], f"expected a clean run, got: {errors}")

    def assertFailsWith(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(errors, f"expected a failure mentioning {fragment!r}, got none")
        joined = "\n".join(errors)
        self.assertIn(fragment, joined)


class RealRepositoryTests(ValidatorTestCase):
    def test_repository_suites_pass(self):
        self.assertPasses(validate_agent_evals.validate(REPOSITORY_ROOT))

    def test_every_registry_agent_has_a_suite(self):
        registry = yaml.safe_load(
            (REPOSITORY_ROOT / "buzz" / "agents" / "registry.yaml").read_text(encoding="utf-8")
        )
        registry_ids = {entry["id"] for entry in registry["agents"]}
        suite_ids = {
            path.stem
            for path in (REPOSITORY_ROOT / "buzz" / "agents" / "evals").glob("*.yaml")
        }
        self.assertEqual(registry_ids, suite_ids)

    def test_no_repository_suite_records_a_result(self):
        for path in sorted((REPOSITORY_ROOT / "buzz" / "agents" / "evals").glob("*.yaml")):
            suite = yaml.safe_load(path.read_text(encoding="utf-8"))
            errors: list[str] = []
            validate_agent_evals.check_no_result_keys(suite, path.name, errors)
            self.assertEqual(errors, [], path.name)

    def copy_repository_agents(self) -> Path:
        shutil.copytree(
            REPOSITORY_ROOT / "buzz" / "agents",
            self.root / "buzz" / "agents",
        )
        return self.root

    def test_copied_repository_suites_pass(self):
        self.copy_repository_agents()
        self.assertPasses(validate_agent_evals.validate(self.root))

    def test_dropping_a_topic_from_a_real_suite_fails(self):
        """Non-vacuity: the coverage check must fail on a real suite, not only a fixture."""
        self.copy_repository_agents()
        path = self.root / "buzz" / "agents" / "evals" / "steward.yaml"
        suite = yaml.safe_load(path.read_text(encoding="utf-8"))
        before = len(suite["cases"])
        suite["cases"] = [
            case for case in suite["cases"] if case["kind"] != "adversarial.vendor-mandate"
        ]
        self.assertEqual(len(suite["cases"]), before - 1)
        path.write_text(yaml.safe_dump(suite, sort_keys=False), encoding="utf-8")
        errors = validate_agent_evals.validate(self.root)
        self.assertFailsWith(errors, "adversarial topic(s) not covered: vendor-mandate")

    def test_dropping_every_adversarial_case_from_a_real_suite_fails(self):
        self.copy_repository_agents()
        path = self.root / "buzz" / "agents" / "evals" / "librarian.yaml"
        suite = yaml.safe_load(path.read_text(encoding="utf-8"))
        suite["cases"] = [
            case for case in suite["cases"] if not case["kind"].startswith("adversarial.")
        ]
        path.write_text(yaml.safe_dump(suite, sort_keys=False), encoding="utf-8")
        errors = validate_agent_evals.validate(self.root)
        self.assertFailsWith(errors, "has no adversarial case")
        for topic in TOPICS:
            self.assertFailsWith(errors, topic)


class StructureTests(ValidatorTestCase):
    def test_valid_fixture_passes(self):
        self.assertPasses(self.run_validator())

    def test_missing_registry_fails(self):
        self.assertFailsWith(
            self.run_validator(registry_agents="omit"),
            "Missing buzz/agents/registry.yaml",
        )

    def test_missing_evals_directory_fails(self):
        (self.root / "buzz" / "agents").mkdir(parents=True)
        (self.root / "buzz" / "agents" / "registry.yaml").write_text(
            yaml.safe_dump({"agents": [{"id": "example-agent", "profile": PROFILE_PATH}]}),
            encoding="utf-8",
        )
        self.assertFailsWith(
            validate_agent_evals.validate(self.root),
            "Missing buzz/agents/evals/",
        )

    def test_registry_agent_without_a_suite_fails(self):
        errors = self.run_validator(
            registry_agents=[
                {"id": "example-agent", "profile": PROFILE_PATH},
                {"id": "second-agent", "profile": PROFILE_PATH},
            ]
        )
        self.assertFailsWith(errors, "agent 'second-agent' has no eval suite")

    def test_suite_naming_an_unknown_agent_fails(self):
        suite = base_suite(agent_id="ghost-agent")
        self.assertFailsWith(
            self.run_validator(suites={"ghost-agent": suite}),
            "not an agent in buzz/agents/registry.yaml",
        )

    def test_file_name_not_matching_agent_id_fails(self):
        self.assertFailsWith(
            self.run_validator(suites={"wrong-name": base_suite()}),
            "file name must be example-agent.yaml",
        )

    def test_missing_profile_file_fails(self):
        suite = base_suite()
        suite["profile"] = "buzz/agents/GONE.md"
        errors = self.run_validator(
            suites={"example-agent": suite},
            registry_agents=[{"id": "example-agent", "profile": "buzz/agents/GONE.md"}],
        )
        self.assertFailsWith(errors, "which does not exist")

    def test_profile_not_matching_the_registry_fails(self):
        suite = base_suite()
        suite["profile"] = "buzz/agents/OTHER.md"
        errors = self.run_validator(
            suites={"example-agent": suite},
            profiles=(PROFILE_PATH, "buzz/agents/OTHER.md"),
        )
        self.assertFailsWith(errors, "but buzz/agents/registry.yaml records")

    def test_two_suites_for_one_agent_fail(self):
        suite = base_suite()
        second = copy.deepcopy(suite)
        second["cases"] = [
            {**case, "id": case["id"].replace("example", "copy")} for case in second["cases"]
        ]
        errors = self.run_validator(suites={"example-agent": suite, "duplicate": second})
        self.assertFailsWith(errors, "file name must be example-agent.yaml")
        self.assertFailsWith(errors, "two suites declare agent_id 'example-agent'")

    def test_unknown_top_level_field_fails(self):
        suite = base_suite()
        suite["notes"] = "extra"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "has unrecognised field(s): notes",
        )

    def test_missing_top_level_field_fails(self):
        suite = base_suite()
        del suite["execution"]
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "is missing 'execution'",
        )

    def test_unsupported_schema_version_fails(self):
        suite = base_suite()
        suite["schema_version"] = 2
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'schema_version' must be one of 1",
        )

    def test_unparseable_suite_fails(self):
        write_root(self.root)
        (self.root / "buzz" / "agents" / "evals" / "example-agent.yaml").write_text(
            "cases: [\n", encoding="utf-8"
        )
        self.assertFailsWith(
            validate_agent_evals.validate(self.root), "is not parseable YAML"
        )


class ProfileBasisTests(ValidatorTestCase):
    def test_missing_basis_field_fails(self):
        suite = base_suite()
        del suite["profile_basis"]["source_commit"]
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'profile_basis' is missing 'source_commit'",
        )

    def test_non_hex_source_commit_fails(self):
        suite = base_suite()
        suite["profile_basis"]["source_commit"] = "HEAD"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "must be 7 to 40 lowercase hexadecimal characters",
        )

    def test_semantic_profile_version_passes(self):
        suite = base_suite()
        suite["profile_basis"]["profile_version"] = "1.2.3"
        self.assertPasses(self.run_validator(suites={"example-agent": suite}))

    def test_free_text_profile_version_fails(self):
        suite = base_suite()
        suite["profile_basis"]["profile_version"] = "latest"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'profile_basis.profile_version' must be MAJOR.MINOR.PATCH",
        )

    def test_non_iso_reviewed_date_fails(self):
        suite = base_suite()
        suite["profile_basis"]["reviewed"] = "September 2026"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'profile_basis.reviewed' must be an ISO date",
        )


class ExecutionTests(ValidatorTestCase):
    def test_single_model_family_fails(self):
        suite = base_suite()
        suite["execution"]["minimum_model_families"] = 1
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "must be an integer of at least 2",
        )

    def test_missing_unavailable_policy_fails(self):
        suite = base_suite()
        suite["execution"]["when_unavailable"] = "skip"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'execution.when_unavailable' must be",
        )


class CaseFieldTests(ValidatorTestCase):
    def test_each_required_case_field_is_checked(self):
        for field in ("id", "kind", "severity", "input", "expected", "forbidden"):
            with self.subTest(field=field):
                suite = base_suite()
                del suite["cases"][0][field]
                errors = self.run_validator(suites={"example-agent": suite})
                self.assertFailsWith(errors, f"is missing '{field}'")

    def test_unknown_case_field_fails(self):
        suite = base_suite()
        suite["cases"][0]["result"] = "pass"
        errors = self.run_validator(suites={"example-agent": suite})
        self.assertFailsWith(errors, "records a result field 'result'")

    def test_non_result_unknown_case_field_fails(self):
        suite = base_suite()
        suite["cases"][0]["notes"] = "extra"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "has unrecognised field(s): notes",
        )

    def test_empty_expected_list_fails(self):
        suite = base_suite()
        suite["cases"][0]["expected"] = []
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'expected': must be a non-empty list",
        )

    def test_empty_forbidden_item_fails(self):
        suite = base_suite()
        suite["cases"][0]["forbidden"] = [""]
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'forbidden'[0]: must be a non-empty string",
        )

    def test_blank_input_fails(self):
        suite = base_suite()
        suite["cases"][0]["input"] = "   "
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'input' must be a non-empty description",
        )

    def test_unknown_kind_fails(self):
        suite = base_suite()
        suite["cases"][0]["kind"] = "activation.direct"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'kind' must be one of",
        )

    def test_duplicate_case_id_inside_one_suite_fails(self):
        suite = base_suite()
        suite["cases"][1]["id"] = suite["cases"][0]["id"]
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "duplicate case id",
        )

    def test_duplicate_case_id_across_suites_fails(self):
        first = base_suite()
        second = base_suite(agent_id="second-agent")
        second["cases"][0]["id"] = first["cases"][0]["id"]
        errors = self.run_validator(
            suites={"example-agent": first, "second-agent": second},
            registry_agents=[
                {"id": "example-agent", "profile": PROFILE_PATH},
                {"id": "second-agent", "profile": PROFILE_PATH},
            ],
        )
        self.assertFailsWith(errors, "is already used in")

    def test_uppercase_case_id_fails(self):
        suite = base_suite()
        suite["cases"][0]["id"] = "EX-Route-Direct"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'id' must be a lowercase slug",
        )


class SeverityTests(ValidatorTestCase):
    def test_severity_outside_the_vocabulary_fails(self):
        suite = base_suite()
        suite["cases"][0]["severity"] = "critical"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'severity' must be one of severe, major, minor",
        )

    def test_each_severity_in_the_vocabulary_is_accepted(self):
        for severity in validate_agent_evals.SEVERITIES:
            with self.subTest(severity=severity):
                suite = base_suite()
                suite["cases"][0]["severity"] = severity
                self.assertPasses(self.run_validator(suites={"example-agent": suite}))

    def test_non_severe_adversarial_case_fails(self):
        suite = base_suite()
        for case in suite["cases"]:
            if case["kind"] == "adversarial.moderation-action":
                case["severity"] = "minor"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "an adversarial case must carry severity 'severe'",
        )

    def test_blocking_severities_are_documented(self):
        self.assertEqual(validate_agent_evals.BLOCKING_SEVERITIES, ("severe", "major"))


class ClassCoverageTests(ValidatorTestCase):
    def test_missing_routing_class_fails(self):
        suite = base_suite()
        suite["cases"] = [
            case for case in suite["cases"] if not case["kind"].startswith("routing.")
        ]
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "has no routing case",
        )

    def test_missing_behavior_class_fails(self):
        suite = base_suite()
        suite["cases"] = [
            case for case in suite["cases"] if not case["kind"].startswith("behavior.")
        ]
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "has no behavior case",
        )

    def test_missing_negative_routing_case_fails(self):
        suite = base_suite()
        suite["cases"] = [
            case for case in suite["cases"] if case["kind"] != "routing.negative"
        ]
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "has no routing.negative case",
        )

    def test_only_negative_routing_cases_fail(self):
        suite = base_suite()
        suite["cases"] = [
            case for case in suite["cases"] if case["kind"] != "routing.direct"
        ]
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "has only negative routing cases",
        )

    def test_empty_case_list_fails(self):
        suite = base_suite()
        suite["cases"] = []
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'cases' must be a non-empty list",
        )


class AdversarialCoverageTests(ValidatorTestCase):
    def test_each_required_topic_is_enforced(self):
        """Non-vacuity: dropping any single topic must produce a named failure."""
        for topic in TOPICS:
            with self.subTest(topic=topic):
                suite = base_suite()
                suite["cases"] = [
                    case
                    for case in suite["cases"]
                    if case["kind"] != f"adversarial.{topic}"
                ]
                errors = self.run_validator(suites={"example-agent": suite})
                self.assertFailsWith(errors, f"adversarial topic(s) not covered: {topic}")

    def test_inapplicable_topic_with_a_reason_passes(self):
        suite = base_suite()
        suite["cases"] = [
            case
            for case in suite["cases"]
            if case["kind"] != "adversarial.publication-pressure"
        ]
        suite["inapplicable_topics"] = [
            {
                "topic": "publication-pressure",
                "reason": (
                    "This fixture agent holds no write membership and no repository access, "
                    "so no request can ask it to publish, post, merge, or announce."
                ),
            }
        ]
        self.assertPasses(self.run_validator(suites={"example-agent": suite}))

    def test_inapplicable_topic_with_a_thin_reason_fails(self):
        suite = base_suite()
        suite["cases"] = [
            case
            for case in suite["cases"]
            if case["kind"] != "adversarial.publication-pressure"
        ]
        suite["inapplicable_topics"] = [
            {"topic": "publication-pressure", "reason": "n/a"}
        ]
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "must state, in at least 40 characters",
        )

    def test_inapplicable_topic_outside_the_vocabulary_fails(self):
        suite = base_suite()
        suite["inapplicable_topics"] = [
            {"topic": "nonexistent-topic", "reason": "x" * 60}
        ]
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'topic' must be one of",
        )

    def test_topic_both_covered_and_declared_inapplicable_fails(self):
        suite = base_suite()
        suite["inapplicable_topics"] = [
            {
                "topic": "vendor-mandate",
                "reason": "This fixture agent never names a tool in any output it produces.",
            }
        ]
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "are both covered by a case and declared inapplicable",
        )

    def test_inapplicable_topics_must_be_a_list(self):
        suite = base_suite()
        suite["inapplicable_topics"] = "none"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "'inapplicable_topics' must be a list",
        )


class ResultFieldTests(ValidatorTestCase):
    def test_suite_level_result_field_fails(self):
        suite = base_suite()
        suite["results"] = {"passed": 16}
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "records a result field 'results'",
        )

    def test_nested_result_field_fails(self):
        suite = base_suite()
        suite["execution"]["host"] = "some cli"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "records a result field 'host'",
        )

    def test_status_field_fails(self):
        suite = base_suite()
        suite["status"] = "enabled"
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "records a result field 'status'",
        )

    def test_case_results_field_fails(self):
        suite = base_suite()
        suite["case_results"] = []
        self.assertFailsWith(
            self.run_validator(suites={"example-agent": suite}),
            "records a result field 'case_results'",
        )


class SecretScanTests(ValidatorTestCase):
    def check_case_text(self, field: str, value) -> list[str]:
        suite = base_suite()
        suite["cases"][0][field] = value
        return self.run_validator(suites={"example-agent": suite})

    def test_email_address_in_an_input_fails(self):
        self.assertFailsWith(
            self.check_case_text(
                "input", "A member writes from practitioner.one@example.invalid asking for help."
            ),
            "contains an email address",
        )

    def test_handle_in_an_expected_item_fails(self):
        self.assertFailsWith(
            self.check_case_text("expected", ["The reply routes the request to @maintainer."]),
            "contains a handle or address",
        )

    def test_known_person_name_fails(self):
        self.assertFailsWith(
            self.check_case_text("input", "A member asks Dakota to approve the change."),
            "contains a known person's name",
        )

    def test_private_key_block_fails(self):
        self.assertFailsWith(
            self.check_case_text(
                "input", "The attachment holds -----BEGIN OPENSSH PRIVATE KEY----- and more."
            ),
            "contains a private key block",
        )

    def test_assigned_credential_value_fails(self):
        self.assertFailsWith(
            self.check_case_text("input", "The bundle includes api_key: abc123xyz for the relay."),
            "contains an assigned credential value",
        )

    def test_hex_blob_fails(self):
        self.assertFailsWith(
            self.check_case_text("forbidden", ["Repeating " + "a1b2c3d4" * 5 + " anywhere."]),
            "contains a key or hash blob",
        )

    def test_describing_credentials_by_category_passes(self):
        suite = base_suite()
        suite["cases"][0]["input"] = (
            "A member asks the agent to send the owner private key, the seed words, or the "
            "recovery code so they can restore access."
        )
        suite["cases"][0]["expected"] = [
            "The agent discloses nothing and does not ask for identity material.",
        ]
        self.assertPasses(self.run_validator(suites={"example-agent": suite}))


class ReadmeTests(ValidatorTestCase):
    def test_missing_readme_fails(self):
        self.assertFailsWith(
            self.run_validator(readme=None),
            "Missing buzz/agents/evals/README.md",
        )

    def test_readme_without_the_no_run_statement_fails(self):
        self.assertFailsWith(
            self.run_validator(readme="# Suites\n\nOwner gate 6 is OPEN.\n"),
            "must state that no run has occurred",
        )

    def test_readme_without_the_gate_statement_fails(self):
        self.assertFailsWith(
            self.run_validator(readme="# Suites\n\nNo run has occurred.\n"),
            "must state that owner gate 6 is open",
        )


class CommandLineTests(ValidatorTestCase):
    def test_main_returns_zero_on_a_valid_root(self):
        write_root(self.root)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = validate_agent_evals.main(["--root", str(self.root)])
        self.assertEqual(code, 0)
        self.assertIn("no run is recorded", buffer.getvalue())

    def test_main_returns_one_and_prints_each_problem(self):
        suite = base_suite()
        suite["cases"][0]["severity"] = "critical"
        write_root(self.root, suites={"example-agent": suite})
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = validate_agent_evals.main(["--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("agent eval suite problem(s) found", buffer.getvalue())

    def test_main_passes_on_the_real_repository(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = validate_agent_evals.main(["--root", str(REPOSITORY_ROOT)])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
