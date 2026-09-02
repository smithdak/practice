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
        cls.text = (REPOSITORY_ROOT / "ops" / "AUTONOMOUS_OPERATION.md").read_text(encoding="utf-8")

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
                    f"ops/AUTONOMOUS_OPERATION.md does not name {relative}; "
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


if __name__ == "__main__":
    unittest.main()
