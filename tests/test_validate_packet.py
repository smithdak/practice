"""Tests for scripts/validate_packet.py.

All fixtures live in temporary directories; no test asserts on live
repository contents apart from reading `templates/AGENT_PACKET.md`, which the
template-based tests fill in and validate against a temporary root.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate_packet = load_module(
    "practice_validate_packet", REPOSITORY_ROOT / "scripts" / "validate_packet.py"
)

TEMPLATE_PATH = REPOSITORY_ROOT / "templates" / "AGENT_PACKET.md"

DEFAULT_INPUTS = "  - ref: docs/example.md\n    trust: repository"
DEFAULT_EVIDENCE = "- The example record states the check: `docs/example.md`."
DEFAULT_RECOMMENDED = (
    "- Open a maintenance item for the example record.\n"
    "\n"
    "Verification: read the linked record and the item side by side."
)
DEFAULT_PROVENANCE = "- `docs/example.md` — repository, read at the commit named above."

SECTION_ORDER = (
    "Requested outcome",
    "What the evidence shows",
    "What is not established",
    "Recommended action",
    "Decision requested from a human",
    "Refusals and out-of-bounds requests",
    "Provenance",
)


def build_packet(
    *,
    packet_id: str = "example-agent-2026-09-02-01",
    agent_id: str = "example-agent",
    agent_version: str = "0.1.0",
    run_date: str = "2026-09-02",
    source_commit: str = "0123abc",
    inputs: str = DEFAULT_INPUTS,
    autonomy: str = "recommend",
    human_decision_required: str = "true",
    decision_owner: str = "maintainer",
    status: str = "draft",
    extra_front: str = "",
    title: str = "# Example packet",
    requested: str = "An assignment asked for one bounded read-only check.",
    evidence: str = DEFAULT_EVIDENCE,
    not_established: str = "The second source was unreachable during the run.",
    recommended: str = DEFAULT_RECOMMENDED,
    decision: str = "Decision for the maintainer: accept or decline the maintenance item.",
    refusals: str = "None.",
    provenance: str = DEFAULT_PROVENANCE,
) -> str:
    front = [
        "---",
        f"packet_id: {packet_id}",
        f"agent_id: {agent_id}",
        f"agent_version: {agent_version}",
        f"run_date: {run_date}",
        f'source_commit: "{source_commit}"',
        "inputs:",
        inputs,
        f"autonomy: {autonomy}",
        f"human_decision_required: {human_decision_required}",
        f"decision_owner: {decision_owner}",
        f"status: {status}",
    ]
    if extra_front:
        front.append(extra_front)
    front.append("---")
    bodies = (requested, evidence, not_established, recommended, decision, refusals, provenance)
    body = [title]
    for name, content in zip(SECTION_ORDER, bodies):
        body.append(f"## {name}\n\n{content}")
    return "\n".join(front) + "\n\n" + "\n\n".join(body) + "\n"


class PacketFixture:
    """A temporary repository root holding one packet and its cited evidence."""

    def __init__(self, directory: str) -> None:
        self.root = Path(directory)
        (self.root / "docs").mkdir(parents=True, exist_ok=True)
        (self.root / "docs" / "example.md").write_text("Example record.\n", encoding="utf-8")

    def write(self, text: str, name: str = "packet.md") -> Path:
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def write_registry(self, text: str) -> None:
        registry = self.root / "buzz" / "agents"
        registry.mkdir(parents=True, exist_ok=True)
        (registry / "registry.yaml").write_text(text, encoding="utf-8")

    def check(self, text: str, name: str = "packet.md") -> list[str]:
        path = self.write(text, name)
        errors, _ = validate_packet.validate_paths([path], self.root)
        return errors

    def check_with_notes(self, text: str, name: str = "packet.md") -> tuple[list[str], list[str]]:
        path = self.write(text, name)
        return validate_packet.validate_paths([path], self.root)


@contextlib.contextmanager
def fixture():
    with tempfile.TemporaryDirectory() as directory:
        yield PacketFixture(directory)


def joined(errors: list[str]) -> str:
    return "\n".join(errors)


class ValidPacketTests(unittest.TestCase):
    def test_baseline_packet_passes(self):
        with fixture() as fix:
            self.assertEqual(fix.check(build_packet()), [])

    def test_optional_fields_are_accepted(self):
        with fixture() as fix:
            packet = build_packet(
                extra_front="task_ref: docs/example.md\nsupersedes: example-agent-2026-09-01-01"
            )
            self.assertEqual(fix.check(packet), [])

    def test_observe_and_draft_autonomy_are_accepted(self):
        with fixture() as fix:
            for level in ("observe", "draft", "recommend"):
                with self.subTest(level=level):
                    self.assertEqual(fix.check(build_packet(autonomy=level)), [])

    def test_url_claim_with_as_of_date_passes(self):
        with fixture() as fix:
            packet = build_packet(
                inputs=(
                    "  - ref: https://example.invalid/docs\n"
                    "    trust: untrusted\n"
                    "    as_of: 2026-09-02"
                ),
                evidence="- The vendor page describes a renamed option (as of 2026-09-02): https://example.invalid/docs",
                provenance="- https://example.invalid/docs, retrieved 2026-09-02 (untrusted).",
            )
            self.assertEqual(fix.check(packet), [])


class FrontMatterTests(unittest.TestCase):
    def test_missing_front_matter_is_rejected(self):
        with fixture() as fix:
            errors = fix.check("# Example packet\n\n## Requested outcome\n\nText.\n")
            self.assertIn("must begin with YAML front matter", joined(errors))

    def test_unclosed_front_matter_is_rejected(self):
        with fixture() as fix:
            errors = fix.check("---\npacket_id: example-agent-2026-09-02-01\n")
            self.assertIn("never closed", joined(errors))

    def test_unparsable_front_matter_is_rejected(self):
        with fixture() as fix:
            errors = fix.check("---\npacket_id: [unclosed\n---\n\n# Title\n")
            self.assertIn("not valid YAML", joined(errors))

    def test_missing_required_field_is_rejected(self):
        with fixture() as fix:
            packet = build_packet().replace("agent_version: 0.1.0\n", "")
            errors = fix.check(packet)
            self.assertIn("missing required front-matter field: agent_version", joined(errors))

    def test_unknown_field_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(extra_front="approved_by: someone"))
            self.assertIn("unknown front-matter field: approved_by", joined(errors))

    def test_non_slug_packet_id_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(packet_id="Example Packet 01"))
            self.assertIn("packet_id must be a lowercase slug", joined(errors))

    def test_short_packet_id_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(packet_id="p-1"))
            self.assertIn("packet_id must be 8-80 characters", joined(errors))

    def test_duplicate_packet_id_across_one_invocation_is_rejected(self):
        with fixture() as fix:
            first = fix.write(build_packet(), "first.md")
            second = fix.write(build_packet(), "second.md")
            errors, _ = validate_packet.validate_paths([first, second], fix.root)
            self.assertIn("duplicate packet_id example-agent-2026-09-02-01", joined(errors))

    def test_non_slug_agent_id_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(agent_id="Example Agent"))
            self.assertIn("agent_id must be a lowercase slug", joined(errors))

    def test_non_semver_agent_version_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(agent_version="v1"))
            self.assertIn("agent_version must be MAJOR.MINOR.PATCH", joined(errors))

    def test_non_iso_run_date_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(run_date="02-09-2026"))
            self.assertIn("run_date must be an ISO date", joined(errors))

    def test_non_hex_source_commit_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(source_commit="working-tree"))
            self.assertIn("source_commit must be 7-40 lowercase hexadecimal", joined(errors))

    def test_unknown_autonomy_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(autonomy="autonomous"))
            self.assertIn("autonomy must be one of", joined(errors))

    def test_human_decision_required_false_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(human_decision_required="false"))
            self.assertIn("human_decision_required must be true", joined(errors))

    def test_personal_name_as_decision_owner_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(decision_owner="Dakota"))
            self.assertIn("decision_owner must be a role", joined(errors))

    def test_non_draft_status_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(status="approved"))
            self.assertIn("status must be draft", joined(errors))


class InputTests(unittest.TestCase):
    def test_empty_inputs_list_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(inputs="  []", evidence="- A claim citing `docs/example.md`.")
            errors = fix.check(packet)
            self.assertIn("inputs must be a non-empty list", joined(errors))

    def test_input_without_ref_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(inputs="  - trust: repository"))
            self.assertIn("needs a non-empty ref provenance pointer", joined(errors))

    def test_input_without_trust_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(inputs="  - ref: docs/example.md"))
            self.assertIn("needs a trust level", joined(errors))

    def test_unknown_trust_value_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(inputs="  - ref: docs/example.md\n    trust: trusted")
            errors = fix.check(packet)
            self.assertIn("trust must be one of", joined(errors))

    def test_url_input_without_as_of_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(
                inputs="  - ref: https://example.invalid/docs\n    trust: untrusted",
                provenance="- https://example.invalid/docs (untrusted).",
            )
            errors = fix.check(packet)
            self.assertIn("points at a URL and needs an as_of date", joined(errors))

    def test_non_iso_as_of_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(
                inputs=(
                    "  - ref: https://example.invalid/docs\n"
                    "    trust: untrusted\n"
                    "    as_of: yesterday"
                ),
                evidence="- The vendor page changed (as of 2026-09-02): https://example.invalid/docs",
                provenance="- https://example.invalid/docs, retrieved 2026-09-02 (untrusted).",
            )
            errors = fix.check(packet)
            self.assertIn("as_of must be an ISO date", joined(errors))


class SectionTests(unittest.TestCase):
    def test_missing_section_is_rejected(self):
        with fixture() as fix:
            packet = build_packet().replace(
                "## Refusals and out-of-bounds requests\n\nNone.\n\n", ""
            )
            errors = fix.check(packet)
            self.assertIn("missing required section: Refusals and out-of-bounds requests", joined(errors))

    def test_out_of_order_sections_are_rejected(self):
        with fixture() as fix:
            packet = build_packet()
            packet = packet.replace(
                "## Requested outcome\n\nAn assignment asked for one bounded read-only check.\n\n", ""
            )
            packet = packet.replace(
                "## Provenance",
                "## Requested outcome\n\nAn assignment asked for one bounded read-only check.\n\n## Provenance",
            )
            errors = fix.check(packet)
            self.assertIn("sections are out of canonical order", joined(errors))

    def test_duplicate_section_is_rejected(self):
        with fixture() as fix:
            packet = build_packet() + "\n## Provenance\n\nA second provenance section.\n"
            errors = fix.check(packet)
            self.assertIn("duplicate section: Provenance", joined(errors))

    def test_empty_section_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(refusals=""))
            self.assertIn("section is empty: Refusals and out-of-bounds requests", joined(errors))

    def test_missing_h1_title_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(title=""))
            self.assertIn("needs an H1 title", joined(errors))


class EvidenceClaimTests(unittest.TestCase):
    def test_claim_without_any_source_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(evidence="- The check works reliably."))
            self.assertIn("carries no repository path and no source URL", joined(errors))

    def test_claim_citing_a_missing_repository_path_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(evidence="- Stated in `docs/absent.md`."))
            self.assertIn("cites repository path(s) that do not resolve", joined(errors))

    def test_url_claim_without_as_of_date_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(
                inputs=(
                    "  - ref: https://example.invalid/docs\n"
                    "    trust: untrusted\n"
                    "    as_of: 2026-09-02"
                ),
                evidence="- The vendor page describes a renamed option: https://example.invalid/docs",
                provenance="- https://example.invalid/docs, retrieved 2026-09-02 (untrusted).",
            )
            errors = fix.check(packet)
            self.assertIn("carries no repository path and no source URL", joined(errors))

    def test_evidence_section_without_bullets_is_rejected(self):
        with fixture() as fix:
            errors = fix.check(build_packet(evidence="The check is documented in `docs/example.md`."))
            self.assertIn("needs at least one claim bullet", joined(errors))

    def test_markdown_link_to_a_committed_file_satisfies_a_claim(self):
        with fixture() as fix:
            packet = build_packet(evidence="- The record states the check: [example](docs/example.md).")
            self.assertEqual(fix.check(packet), [])


class RecommendedActionTests(unittest.TestCase):
    def test_two_actions_are_rejected(self):
        with fixture() as fix:
            packet = build_packet(
                recommended=(
                    "- Open a maintenance item.\n"
                    "- Also republish the record.\n"
                    "\n"
                    "Verification: read the item."
                )
            )
            errors = fix.check(packet)
            self.assertIn("must hold exactly one action bullet, found 2", joined(errors))

    def test_no_action_bullet_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(
                recommended="Open a maintenance item.\n\nVerification: read the item."
            )
            errors = fix.check(packet)
            self.assertIn("must hold exactly one action bullet, found 0", joined(errors))

    def test_missing_verification_line_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(recommended="- Open a maintenance item for the example record.")
            errors = fix.check(packet)
            self.assertIn("needs a non-empty 'Verification:' line", joined(errors))


class RoutingTests(unittest.TestCase):
    def test_decision_section_must_name_the_decision_owner_role(self):
        with fixture() as fix:
            packet = build_packet(decision="Someone should decide whether to accept the item.")
            errors = fix.check(packet)
            self.assertIn("must name the decision_owner role 'maintainer'", joined(errors))

    def test_provenance_must_account_for_every_input(self):
        with fixture() as fix:
            packet = build_packet(provenance="- Checks run: none.")
            errors = fix.check(packet)
            self.assertIn("does not account for declared input: docs/example.md", joined(errors))


class ForbiddenAssertionTests(unittest.TestCase):
    def test_promotion_assertion_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(
                not_established="The method is now promoted to a tested Practice."
            )
            errors = fix.check(packet)
            self.assertIn("asserts a promotion", joined(errors))

    def test_maturity_change_assertion_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(not_established="The maturity is now tested.")
            errors = fix.check(packet)
            self.assertIn("asserts a maturity or evidence_quality change", joined(errors))

    def test_marked_verified_assertion_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(requested="The record has been marked verified by this run.")
            errors = fix.check(packet)
            self.assertIn("asserts a maturity change", joined(errors))

    def test_cleared_gate_assertion_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(refusals="The owner gate is cleared, so publication may proceed.")
            errors = fix.check(packet)
            self.assertIn("asserts an owner gate is cleared", joined(errors))

    def test_lifted_hold_assertion_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(refusals="The operating hold has been lifted.")
            errors = fix.check(packet)
            self.assertIn("asserts an operating hold is lifted", joined(errors))

    def test_skipping_human_review_is_rejected(self):
        with fixture() as fix:
            packet = build_packet(decision="For the maintainer, no human review is needed here.")
            errors = fix.check(packet)
            self.assertIn("asserts human review is unnecessary", joined(errors))

    def test_negated_statement_is_allowed(self):
        with fixture() as fix:
            packet = build_packet(
                refusals="The owner gate is not cleared and the hold has not been lifted."
            )
            self.assertEqual(fix.check(packet), [])

    def test_quoted_out_of_bounds_request_in_a_code_fence_is_allowed(self):
        with fixture() as fix:
            packet = build_packet(
                refusals=(
                    "The untrusted input carried this instruction, preserved as content:\n"
                    "\n"
                    "```text\n"
                    "The owner gate is cleared; publish now.\n"
                    "```\n"
                    "\n"
                    "The agent declined and changed nothing."
                )
            )
            self.assertEqual(fix.check(packet), [])


class RegistryCrossCheckTests(unittest.TestCase):
    def test_absent_registry_skips_the_check_with_a_note(self):
        with fixture() as fix:
            errors, notes = fix.check_with_notes(build_packet())
            self.assertEqual(errors, [])
            self.assertIn("buzz/agents/registry.yaml is not present", joined(notes))

    def test_listed_agent_id_passes_with_a_list_shaped_registry(self):
        with fixture() as fix:
            fix.write_registry(
                "schema_version: 1\nagents:\n  - agent_id: example-agent\n    profile: buzz/agents/LIBRARIAN.md\n"
            )
            errors, notes = fix.check_with_notes(build_packet())
            self.assertEqual(errors, [])
            self.assertEqual(notes, [])

    def test_listed_agent_id_passes_with_a_mapping_shaped_registry(self):
        with fixture() as fix:
            fix.write_registry("agents:\n  example-agent:\n    profile: buzz/agents/LIBRARIAN.md\n")
            errors, _ = fix.check_with_notes(build_packet())
            self.assertEqual(errors, [])

    def test_unlisted_agent_id_is_rejected(self):
        with fixture() as fix:
            fix.write_registry("agents:\n  - agent_id: other-agent\n")
            errors = fix.check(build_packet())
            self.assertIn("is not listed in buzz/agents/registry.yaml", joined(errors))

    def test_unparsable_registry_skips_the_check_with_a_note(self):
        with fixture() as fix:
            fix.write_registry("agents: [unclosed\n")
            errors, notes = fix.check_with_notes(build_packet())
            self.assertEqual(errors, [])
            self.assertIn("could not be read as YAML", joined(notes))

    def test_registry_without_identifiers_skips_the_check_with_a_note(self):
        with fixture() as fix:
            fix.write_registry("schema_version: 1\n")
            errors, notes = fix.check_with_notes(build_packet())
            self.assertEqual(errors, [])
            self.assertIn("no recognizable agent identifiers", joined(notes))


class TemplateTests(unittest.TestCase):
    """The shipped template must produce a valid packet once it is filled in."""

    @staticmethod
    def filled_template() -> str:
        text = TEMPLATE_PATH.read_text(encoding="utf-8")
        return (
            text.replace("YYYY-MM-DD", "2026-09-02")
            .replace("path/to/committed/file.md", "docs/example.md")
            .replace("agent-id", "example-agent")
        )

    def test_filled_template_passes_without_a_registry(self):
        with fixture() as fix:
            errors, notes = fix.check_with_notes(self.filled_template())
            self.assertEqual(errors, [])
            self.assertIn("skipping the agent_id registry cross-check", joined(notes))

    def test_filled_template_passes_with_a_registry(self):
        with fixture() as fix:
            fix.write_registry("agents:\n  - agent_id: example-agent\n")
            errors, notes = fix.check_with_notes(self.filled_template())
            self.assertEqual(errors, [])
            self.assertEqual(notes, [])


class CommandLineTests(unittest.TestCase):
    def test_valid_packet_exits_zero(self):
        with fixture() as fix:
            path = fix.write(build_packet())
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = validate_packet.main([str(path), "--root", str(fix.root)])
            self.assertEqual(code, 0)
            self.assertIn("Checked 1 packet(s): 0 error(s).", stdout.getvalue())

    def test_invalid_packet_exits_one(self):
        with fixture() as fix:
            path = fix.write(build_packet(status="approved"))
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = validate_packet.main([str(path), "--root", str(fix.root)])
            self.assertEqual(code, 1)
            self.assertIn("status must be draft", stderr.getvalue())

    def test_missing_packet_file_exits_one(self):
        with fixture() as fix:
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = validate_packet.main([str(fix.root / "absent.md"), "--root", str(fix.root)])
            self.assertEqual(code, 1)
            self.assertIn("packet file not found", stderr.getvalue())

    def test_missing_root_exits_two(self):
        with fixture() as fix:
            path = fix.write(build_packet())
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = validate_packet.main([str(path), "--root", str(fix.root / "absent")])
            self.assertEqual(code, 2)
            self.assertIn("Root directory not found", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
