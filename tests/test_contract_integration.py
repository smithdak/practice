"""Cross-contract invariants that no single Phase 3 task owns.

The agent registry, the packet contract, the autonomy ladder, and the eval
suites are each validated by their own script. Nothing validated the joins
between them, and the joins are where the agent boundary would quietly drift:
a packet may declare a level the registry never granted, the schema's own
worked example may fall out of step with the registry, and a new validator may
be written without ever running anywhere.

These tests cover those joins.
"""
from __future__ import annotations

import subprocess
import sys

import yaml
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import validate_packet  # noqa: E402

SCHEMA_RELATIVE = "docs/schemas/AGENT_PACKET_SCHEMA.md"
REGISTRY_RELATIVE = "buzz/agents/registry.yaml"
LADDER_RELATIVE = "docs/framework/AUTONOMY_LADDER.md"
WORKFLOW_RELATIVE = ".github/workflows/ci.yml"


def worked_example() -> str:
    """Return the packet inside the schema's worked-example fence."""
    lines = (REPOSITORY_ROOT / SCHEMA_RELATIVE).read_text(encoding="utf-8").split("\n")
    opens = [index for index, line in enumerate(lines) if line.startswith("```markdown")]
    if len(opens) != 1:
        raise AssertionError(
            f"{SCHEMA_RELATIVE} should hold exactly one markdown fence, found {len(opens)}"
        )
    start = opens[0]
    closes = [index for index in range(start + 1, len(lines)) if lines[index].strip() == "```"]
    if not closes:
        raise AssertionError(f"{SCHEMA_RELATIVE} has an unclosed worked-example fence")
    return "\n".join(lines[start + 1:closes[0]]) + "\n"


def validate_text(text: str, root: Path) -> list[str]:
    """Validate packet text as a file, since the validator takes paths."""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "packet.md"
        path.write_text(text, encoding="utf-8")
        errors, _ = validate_packet.validate_paths([path], root)
    return errors


class WorkedExampleTests(unittest.TestCase):
    """The schema's example is the one packet that must always be valid.

    It is the only packet in the repository, so it is the only thing that would
    notice the packet contract and the registry drifting apart. It caught
    exactly that when the autonomy bound was first enforced.
    """

    def test_worked_example_validates_against_the_real_repository(self):
        errors = validate_text(worked_example(), REPOSITORY_ROOT)
        self.assertEqual(errors, [], "the schema's worked example must satisfy its own rules")

    def test_worked_example_declares_an_agent_the_registry_lists(self):
        bounds = validate_packet.load_registry_autonomy(REPOSITORY_ROOT, [])
        self.assertTrue(bounds, f"{REGISTRY_RELATIVE} should grant at least one agent a level")
        example = worked_example()
        agent_ids = [line.split(":", 1)[1].strip() for line in example.split("\n") if line.startswith("agent_id:")]
        self.assertEqual(len(agent_ids), 1)
        self.assertIn(agent_ids[0], bounds)


class AutonomyBoundTests(unittest.TestCase):
    """A packet may declare less autonomy than it was granted, never more."""

    def setUp(self):
        self.example = worked_example()
        self.bounds = validate_packet.load_registry_autonomy(REPOSITORY_ROOT, [])

    def declare(self, level: str) -> str:
        return self.example.replace("autonomy: draft", f"autonomy: {level}", 1)

    def test_a_packet_may_not_exceed_its_registry_grant(self):
        errors = validate_text(self.declare("recommend"), REPOSITORY_ROOT)
        self.assertTrue(errors, "a packet above its grant must be rejected")
        joined = "\n".join(errors)
        self.assertIn("exceeds the draft level", joined)
        self.assertIn(REGISTRY_RELATIVE, joined)
        self.assertIn(LADDER_RELATIVE, joined, "the message should name where the grant is raised")

    def test_a_packet_may_declare_less_than_its_grant(self):
        self.assertEqual(validate_text(self.declare("observe"), REPOSITORY_ROOT), [])

    def test_a_packet_at_its_grant_passes(self):
        self.assertEqual(validate_text(self.declare("draft"), REPOSITORY_ROOT), [])

    def test_the_bound_is_skipped_rather_than_guessed_without_a_grant(self):
        """An agent the registry does not bound is not silently held to a level."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "buzz" / "agents").mkdir(parents=True)
            (root / "buzz" / "agents" / "registry.yaml").write_text(
                "schema_version: 1\nagents:\n  - id: research-auditor\n    name: Research Auditor\n",
                encoding="utf-8",
            )
            (root / "practices").mkdir()
            (root / "practices" / "001-context-pack.md").write_text("placeholder\n", encoding="utf-8")
            errors = validate_text(self.declare("recommend"), root)
        self.assertEqual(
            [error for error in errors if "autonomy" in error],
            [],
            "an unbounded agent should skip the check, not fail it",
        )

    def test_every_registry_grant_is_a_known_level(self):
        for agent_id, granted in self.bounds.items():
            with self.subTest(agent=agent_id):
                self.assertIn(granted, validate_packet.AUTONOMY_RANK)


class ValidatorWiringTests(unittest.TestCase):
    """Every repository check either runs in CI or is exempt for a stated reason.

    A validator nobody runs is a validator that rots. Adding a script without
    deciding where it runs should fail here rather than pass unnoticed.
    """

    # Each entry is a script that is deliberately not a CI gate, and why.
    EXEMPT = {
        "scripts/context_pack_trial.py": (
            "generates unpublished experiment evidence, not a read-only check; live CLI "
            "refuses while no transport is configured. Offline invariants and the private "
            "runner integration are exercised by test_context_pack_trial.py and "
            "test_run_unattended.py under the existing CI unittest step"
        ),
        "scripts/validate_packet.py": (
            "takes explicit packet paths; no packet corpus exists yet, and its rules "
            "are exercised by tests/test_validate_packet.py and this module"
        ),
        "scripts/cadence.py": (
            "reports what is due; making an elapsed window a build failure would "
            "create work no person owns"
        ),
        "scripts/collect_metrics.py": "reports repository state; a count is not a gate",
        "scripts/release_brief.py": (
            "generates a draft for human approval; its output is guarded by "
            "tests/test_release_brief.py"
        ),
        "scripts/buzz_bootstrap.py": "owner-operated apply; never runs unattended",
        "scripts/taskctl.py": "local swarm orchestration, not a repository check",
        "scripts/steward_readiness_check.py": (
            "a human runs it against a live route before enabling the Steward"
        ),
        "scripts/validate.py": "run by CI through its --release mode, asserted separately",
        "scripts/autonomy_guard.py": (
            "decides whether one operation may run; its exit code is a decision, not a "
            "build verdict, and wiring it as a step would fail CI precisely because the "
            "substrate is inert. The refusal invariant is asserted by "
            "tests/test_autonomy_guard.py, which CI runs"
        ),
        "scripts/run_unattended.py": (
            "executes one catalogued operation and exits 1 while nothing is promoted, "
            "which is the shipped state; its refusal and containment invariants are "
            "asserted by tests/test_run_unattended.py"
        ),
    }

    @classmethod
    def setUpClass(cls):
        cls.workflow = (REPOSITORY_ROOT / WORKFLOW_RELATIVE).read_text(encoding="utf-8")

    def python_checks(self) -> list[str]:
        found = sorted(
            path.relative_to(REPOSITORY_ROOT).as_posix()
            for path in (REPOSITORY_ROOT / "scripts").glob("*.py")
        )
        found.append("skills/evals/validate.py")
        return found

    def test_every_check_runs_in_ci_or_is_exempt(self):
        for relative in self.python_checks():
            with self.subTest(script=relative):
                if relative in self.EXEMPT:
                    self.assertTrue(self.EXEMPT[relative].strip(), "an exemption needs a reason")
                    continue
                self.assertIn(
                    relative,
                    self.workflow,
                    f"{relative} runs nowhere: add it to {WORKFLOW_RELATIVE} or "
                    "record why it is exempt in ValidatorWiringTests.EXEMPT",
                )

    def test_release_validation_runs_in_ci(self):
        self.assertIn("scripts/validate.py --release", self.workflow)

    def test_every_exemption_names_a_script_that_exists(self):
        for relative in self.EXEMPT:
            with self.subTest(script=relative):
                self.assertTrue(
                    (REPOSITORY_ROOT / relative).is_file(),
                    f"{relative} is exempt but does not exist; drop the exemption",
                )

    def test_ci_fetches_enough_history_for_the_range_checks(self):
        """A shallow clone silently skips the brief-versus-generator guard."""
        self.assertIn("fetch-depth: 0", self.workflow)

    def test_the_unit_suite_runs_in_ci(self):
        self.assertIn("unittest discover -s tests", self.workflow)


class OperatingDocumentTests(unittest.TestCase):
    """The operating procedure must point at the contracts it depends on."""

    @classmethod
    def setUpClass(cls):
        cls.text = (REPOSITORY_ROOT / "ops" / "OPERATING_LOOP.md").read_text(encoding="utf-8")

    def test_it_links_every_contract_and_runner(self):
        for relative in (
            REGISTRY_RELATIVE,
            LADDER_RELATIVE,
            SCHEMA_RELATIVE,
            "ops/cadence.yaml",
            "scripts/cadence.py",
            "scripts/collect_metrics.py",
            "scripts/release_brief.py",
            "scripts/triage.py",
            "buzz/agents/evals/README.md",
        ):
            with self.subTest(target=relative):
                self.assertTrue(
                    Path(relative).name in self.text,
                    f"ops/OPERATING_LOOP.md does not name {relative}; "
                    "the operating procedure should route to every contract and runner",
                )

    def test_it_states_that_no_agent_is_enabled(self):
        self.assertIn("not_enabled", self.text)


def run_script(*arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *arguments],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class RepositoryCheckTests(unittest.TestCase):
    """The checks CI runs must pass on this tree."""

    def test_agent_registry_validates(self):
        result = run_script("scripts/validate_agents.py", "--root", ".")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_agent_eval_suites_validate(self):
        result = run_script("scripts/validate_agent_evals.py", "--root", ".")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_triage_records_validate(self):
        result = run_script("scripts/triage.py", "validate", "ops/triage", "--root", ".")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class AmendmentConsistencyTests(unittest.TestCase):
    """Amendment 001, the ladder, and the guard must say the same thing.

    A governance amendment that reaches one of the three and not the others is
    the failure mode the guard's ladder-agreement precondition exists to catch:
    it refused this amendment until the tooling was updated deliberately.
    """

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))
        import autonomy_guard  # noqa: E402

        cls.guard = autonomy_guard
        cls.ladder = (REPOSITORY_ROOT / LADDER_RELATIVE).read_text(encoding="utf-8")
        cls.amendment = (REPOSITORY_ROOT / "community" / "AMENDMENTS.md").read_text(encoding="utf-8")

    def test_the_split_publication_operation_is_still_ineligible(self):
        self.assertIn("publication-approval", self.guard.INELIGIBLE_OPERATIONS)
        self.assertIn("`publication-approval`", self.ladder)

    def test_merge_left_the_ineligible_list_in_both_places(self):
        self.assertNotIn("merge", self.guard.INELIGIBLE_OPERATIONS)
        section = self.ladder.split("## Permanently ineligible for A3", 1)[1].split("\n## ", 1)[0]
        self.assertNotIn("| `merge` |", section)

    def test_the_amendment_is_recorded_before_the_lists_changed(self):
        self.assertIn("Amendment 001", self.amendment)
        self.assertIn("publication-approval", self.amendment)
        self.assertIn("self-modification", self.amendment.lower())

    def test_nothing_the_amendment_declined_became_eligible(self):
        for declined in ("moderation-and-removal", "maturity-promotion",
                         "owner-identity-and-keys", "license-and-governance-change",
                         "owner-reserved-decision"):
            with self.subTest(operation=declined):
                self.assertIn(declined, self.guard.INELIGIBLE_OPERATIONS)

    def test_the_ladder_states_the_self_modification_exclusion(self):
        self.assertIn("self-modification exclusion", self.ladder.lower())
        self.assertIn("not waivable", self.ladder.lower())


class ContainmentTests(unittest.TestCase):
    """The two write-scope matchers disagree on purpose, both toward refusing."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))
        import autonomy_guard  # noqa: E402
        import run_unattended  # noqa: E402

        cls.guard = autonomy_guard
        cls.runner = run_unattended

    def test_the_runner_does_not_let_a_glob_cross_a_directory(self):
        """Plain fnmatch would admit this, widening the scope by a directory."""
        self.assertFalse(self.runner.matches_scope("ops/status/archive/old.md", ["ops/status/*.md"]))
        self.assertTrue(self.runner.matches_scope("ops/status/today.md", ["ops/status/*.md"]))

    def test_a_subtree_scope_has_to_say_so(self):
        self.assertTrue(self.runner.matches_scope("ops/status/archive/old.md", ["ops/status/**"]))

    def test_the_shipped_catalog_scopes_reach_no_governed_path(self):
        catalog = yaml.safe_load((REPOSITORY_ROOT / "ops" / "autonomy" / "operations.yaml").read_text())
        for operation in catalog["operations"]:
            for pattern in operation.get("write_scope") or []:
                with self.subTest(operation=operation["id"], pattern=pattern):
                    self.assertIsNone(
                        self.guard.glob_reaches_governed_path(pattern),
                        "a catalogued write scope must not reach a file governing the agent's bounds",
                    )

    def test_no_catalogued_scope_admits_a_governing_file(self):
        catalog = yaml.safe_load((REPOSITORY_ROOT / "ops" / "autonomy" / "operations.yaml").read_text())
        scopes = [p for op in catalog["operations"] for p in (op.get("write_scope") or [])]
        for governed in ("docs/DECISIONS.md", "docs/NON_GOALS.md", "community/GOVERNANCE.md",
                         "community/AMENDMENTS.md", LADDER_RELATIVE,
                         "ops/autonomy/promotions.yaml", "ops/autonomy/renewals.yaml",
                         ".github/workflows/ci.yml"):
            with self.subTest(path=governed):
                self.assertFalse(self.runner.matches_scope(governed, scopes))

    def test_the_renewal_record_is_a_governed_path_for_the_guard(self):
        self.assertIsNotNone(self.guard.glob_reaches_governed_path("ops/autonomy/renewals.yaml"))
        self.assertIn("ops/autonomy/renewals.yaml", self.guard.GOVERNED_PATHS)


class ReviewPointContractTests(unittest.TestCase):
    """The guard, the ledger, the runner, and the demotion check agree on the review point.

    The guard requires it on a promotion, the ledger requires it on a recorded
    promotion, the runner records the effective value, and the demotion check
    reads it back. Each has its own tests; this is the join.
    """

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))
        import autonomy_guard  # noqa: E402
        import demotion_check  # noqa: E402
        import ledger  # noqa: E402
        import run_unattended  # noqa: E402

        cls.guard = autonomy_guard
        cls.check = demotion_check
        cls.ledger = ledger
        cls.runner = run_unattended

    def test_the_guard_requires_a_review_point_on_every_promotion(self):
        self.assertIn("review_point", self.guard.REQUIRED_PROMOTION_FIELDS)

    def test_the_ledger_requires_a_review_point_on_every_recorded_promotion(self):
        self.assertIn("review_point", self.ledger.PROMOTION_REQUIRED)
        self.assertNotIn("review_point", self.ledger.PROMOTION_OPTIONAL)

    def test_the_runner_records_exactly_the_ledger_promotion_fields(self):
        self.assertEqual(sorted(self.runner.RECORDED_PROMOTION_KEYS), sorted(self.ledger.PROMOTION_FIELDS))

    def test_every_ledger_promotion_field_is_a_guard_promotion_field(self):
        """What the runner copies out of a promotion, the guard must have required."""
        self.assertLessEqual(set(self.ledger.PROMOTION_FIELDS), set(self.guard.REQUIRED_PROMOTION_FIELDS))

    def test_the_four_scripts_name_the_same_renewal_record(self):
        self.assertEqual(self.guard.RENEWALS_PATH, "ops/autonomy/renewals.yaml")
        self.assertEqual(self.runner.RENEWALS_PATH, self.guard.RENEWALS_PATH)
        self.assertEqual(self.check.RENEWALS_PATH, self.guard.RENEWALS_PATH)
        self.assertIn(self.guard.RENEWALS_PATH, self.runner.GUARD_INPUTS)

    def test_the_shipped_renewal_record_matches_the_guard_schema(self):
        record = yaml.safe_load((REPOSITORY_ROOT / self.guard.RENEWALS_PATH).read_text(encoding="utf-8"))
        self.assertEqual(sorted(record), sorted(self.guard.RENEWALS_TOP_LEVEL_FIELDS))
        self.assertIn(record["schema_version"], self.guard.SUPPORTED_SCHEMA_VERSIONS)
        self.assertEqual(record["renewals"], [])

    def test_the_shipped_promotion_record_is_unchanged_in_state(self):
        record = yaml.safe_load((REPOSITORY_ROOT / self.guard.PROMOTIONS_PATH).read_text(encoding="utf-8"))
        self.assertEqual(record["kill_switch"], "engaged")
        self.assertEqual(record["promotions"], [])

    def test_the_guard_names_the_three_review_point_preconditions_the_check_can_read(self):
        decision = self.guard.evaluate(REPOSITORY_ROOT, "cadence-snapshot")
        named = set(decision.checked) | {refusal.precondition for refusal in decision.refusals}
        for precondition in ("review-point-recorded", "renewal-record-readable", "review-point-not-passed"):
            with self.subTest(precondition=precondition):
                self.assertIn(precondition, named)
                self.assertRegex(precondition, self.ledger.SLUG_RE)

    def test_the_schema_and_the_records_readme_describe_the_renewal_record(self):
        schema = (REPOSITORY_ROOT / "docs" / "schemas" / "ACTION_LEDGER_SCHEMA.md").read_text(encoding="utf-8")
        readme = (REPOSITORY_ROOT / "ops" / "autonomy" / "README.md").read_text(encoding="utf-8")
        loop = (REPOSITORY_ROOT / "ops" / "OPERATING_LOOP.md").read_text(encoding="utf-8")
        for text, name in ((schema, "schema"), (readme, "README"), (loop, "operating loop")):
            with self.subTest(document=name):
                self.assertIn("renewals.yaml", text)
        for precondition in ("review-point-recorded", "renewal-record-readable", "review-point-not-passed"):
            with self.subTest(precondition=precondition):
                self.assertIn(f"`{precondition}`", readme)


class LedgerIdentityTests(unittest.TestCase):
    """Run ids are allocated from recorded ids, not file names."""

    def test_the_next_id_does_not_collide_with_the_sample(self):
        sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))
        import ledger  # noqa: E402

        sample = (REPOSITORY_ROOT / "ops" / "ledger" / "SAMPLE_run.md").read_text(encoding="utf-8")
        recorded = [line for line in sample.split("\n") if line.startswith("run_id:")]
        self.assertEqual(len(recorded), 1, "the sample should record exactly one run id")
        taken = recorded[0].split(":", 1)[1].strip()
        operation = taken.rsplit("-", 1)[0]
        self.assertNotEqual(
            ledger.next_run_id(operation, root=REPOSITORY_ROOT),
            taken,
            "the sample is exempt from the file-naming rule, so a name-only scan reissues its id",
        )


if __name__ == "__main__":
    unittest.main()
