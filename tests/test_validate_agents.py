"""Failure-mode coverage for scripts/validate_agents.py.

Every test builds a synthetic repository root in a temporary directory, breaks
exactly one thing, and asserts that the validator says so. One test runs the
checker against the real repository, so the fixtures cannot drift into
describing a registry the repository does not have.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
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


validate_agents = load_module(
    "practice_validate_agents", REPOSITORY_ROOT / "scripts" / "validate_agents.py"
)


COMMUNITY = {
    "version": 1,
    "community": "Practice",
    "channels": [
        {"name": "maintainers", "visibility": "private", "type": "stream"},
        {"name": "announcements", "visibility": "open", "type": "stream"},
        {"name": "start-here", "visibility": "open", "type": "stream"},
        {"name": "learn", "visibility": "open", "type": "stream"},
    ],
}

# Synthetic stand-in for release/OWNER_REVIEW.md. Only the two anchor rows the
# validator reads matter; the wording mirrors the real packet's shape.
OWNER_REVIEW_GATE_OPEN = """# Owner review packet (fixture)

| Gate | Evidence to review | Human action | Status |
| --- | --- | --- | --- |
| Initial community-agent providers | packet (gate 6): agent profiles. | Select the first agents manually. | **OPEN** |

| Hold | Evidence | Minimum clearance evidence | Status |
| --- | --- | --- | --- |
| Steward escalation readiness | packet (hold 6): the Steward profile fails closed. | Configure and test the route. | **OPEN** |
"""

LOCKED_PROHIBITIONS = [
    "Silently removing, deleting, hiding, banning, or editing members, people, or content.",
    "Requesting, receiving, storing, or recovering the owner private key or any credential.",
    "Publishing, merging, or announcing anything without review by a human maintainer.",
    "Changing a maturity or evidence_quality field, or implying an unsupported evidence level.",
]


def base_agent() -> dict:
    return {
        "id": "example-agent",
        "name": "Example Agent",
        "profile": "buzz/agents/EXAMPLE.md",
        "mission": "Route one request to one channel with a checkable next action.",
        "autonomy": "draft",
        "channels": {"read": ["learn"], "write": [], "write_approval": {}},
        "conditional_channels": [],
        "excluded_channels": ["maintainers"],
        "identity": {
            "dedicated_identity": True,
            "shared_across_instances": False,
            "accountable_human_role": "agent-sponsor",
            "requirement": "One unique identity with one accountable human sponsor.",
        },
        "prohibited": list(LOCKED_PROHIBITIONS),
        "escalation": {
            "route": "Return the escalation block through the approved human-owned path.",
            "owner_role": "maintainer",
        },
        "enablement_prerequisites": [
            "Owner gate 6 is recorded as approved by a human in release/OWNER_REVIEW.md.",
        ],
        "status": "not_enabled",
    }


def base_registry() -> dict:
    return {
        "schema_version": 1,
        "as_of": "2026-09-02",
        "sources": ["buzz/community.json", "release/OWNER_REVIEW.md"],
        "agents": [base_agent()],
    }


def build_root(
    directory: str,
    registry: dict,
    profiles: tuple[str, ...] = ("EXAMPLE.md",),
    owner_review: str = OWNER_REVIEW_GATE_OPEN,
) -> Path:
    root = Path(directory)
    (root / "buzz" / "agents").mkdir(parents=True)
    (root / "release").mkdir(parents=True)
    for profile in profiles:
        (root / "buzz" / "agents" / profile).write_text(
            f"# {profile}\n\nProfile fixture.\n", encoding="utf-8"
        )
    (root / "buzz" / "community.json").write_text(
        json.dumps(COMMUNITY, indent=2), encoding="utf-8"
    )
    (root / "release" / "OWNER_REVIEW.md").write_text(owner_review, encoding="utf-8")
    (root / "buzz" / "agents" / "registry.yaml").write_text(
        yaml.safe_dump(registry, sort_keys=False), encoding="utf-8"
    )
    return root


class RegistryFixtureMixin(unittest.TestCase):
    def run_validator(self, registry: dict, **kwargs) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory, registry, **kwargs)
            return validate_agents.validate(root)

    def assertReports(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected an error containing {fragment!r}; got {errors}",
        )


class RealRepositoryTests(unittest.TestCase):
    def test_repository_registry_passes(self):
        self.assertEqual(validate_agents.validate(REPOSITORY_ROOT), [])

    def test_every_repository_profile_has_an_entry(self):
        registry = yaml.safe_load(
            (REPOSITORY_ROOT / "buzz" / "agents" / "registry.yaml").read_text(encoding="utf-8")
        )
        declared = {agent["profile"] for agent in registry["agents"]}
        on_disk = {
            path.relative_to(REPOSITORY_ROOT).as_posix()
            for path in (REPOSITORY_ROOT / "buzz" / "agents").glob("*.md")
        }
        self.assertEqual(declared, on_disk)

    def test_every_repository_agent_is_not_enabled(self):
        registry = yaml.safe_load(
            (REPOSITORY_ROOT / "buzz" / "agents" / "registry.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {agent["status"] for agent in registry["agents"]},
            {"not_enabled"},
        )


class BaselineTests(RegistryFixtureMixin):
    def test_valid_fixture_passes(self):
        self.assertEqual(self.run_validator(base_registry()), [])


class CoverageTests(RegistryFixtureMixin):
    def test_profile_without_a_registry_entry_fails(self):
        errors = self.run_validator(
            base_registry(), profiles=("EXAMPLE.md", "UNREGISTERED.md")
        )
        self.assertReports(errors, "buzz/agents/UNREGISTERED.md has no entry")

    def test_entry_naming_a_missing_profile_fails(self):
        registry = base_registry()
        registry["agents"][0]["profile"] = "buzz/agents/GHOST.md"
        errors = self.run_validator(registry)
        self.assertReports(errors, "names buzz/agents/GHOST.md, which does not exist")

    def test_profile_outside_the_agents_directory_fails(self):
        registry = base_registry()
        registry["agents"][0]["profile"] = "docs/EXAMPLE.md"
        errors = self.run_validator(registry)
        self.assertReports(errors, "must be a repository-relative path under buzz/agents/")

    def test_duplicate_agent_ids_fail(self):
        registry = base_registry()
        second = base_agent()
        second["profile"] = "buzz/agents/SECOND.md"
        registry["agents"].append(second)
        errors = self.run_validator(registry, profiles=("EXAMPLE.md", "SECOND.md"))
        self.assertReports(errors, "duplicate agent id 'example-agent'")

    def test_missing_required_field_fails(self):
        registry = base_registry()
        del registry["agents"][0]["mission"]
        errors = self.run_validator(registry)
        self.assertReports(errors, "missing required field 'mission'")

    def test_unrecognized_field_fails(self):
        registry = base_registry()
        registry["agents"][0]["prohibitted"] = ["typo"]
        errors = self.run_validator(registry)
        self.assertReports(errors, "unrecognized field(s) prohibitted")


class ChannelScopeTests(RegistryFixtureMixin):
    def test_unknown_read_channel_fails(self):
        registry = base_registry()
        registry["agents"][0]["channels"]["read"] = ["learn", "war-room"]
        errors = self.run_validator(registry)
        self.assertReports(errors, "declares 'war-room', which is not a channel in buzz/community.json")

    def test_unknown_write_channel_fails(self):
        registry = base_registry()
        registry["agents"][0]["channels"]["read"] = ["learn", "war-room"]
        registry["agents"][0]["channels"]["write"] = ["war-room"]
        errors = self.run_validator(registry)
        self.assertReports(errors, "'channels.write' declares 'war-room'")

    def test_unknown_conditional_channel_fails(self):
        registry = base_registry()
        registry["agents"][0]["conditional_channels"] = [
            {
                "channel": "war-room",
                "access": "read",
                "condition": "Only while an assignment is open.",
                "approver_role": "maintainer",
            }
        ]
        errors = self.run_validator(registry)
        self.assertReports(errors, "names 'war-room', which is not a channel")

    def test_write_without_read_fails(self):
        registry = base_registry()
        registry["agents"][0]["channels"]["write"] = ["learn"]
        registry["agents"][0]["channels"]["read"] = []
        errors = self.run_validator(registry)
        self.assertReports(errors, "without read access")

    def test_write_to_private_channel_without_approval_fails(self):
        registry = base_registry()
        registry["agents"][0]["channels"]["read"] = ["learn", "maintainers"]
        registry["agents"][0]["channels"]["write"] = ["maintainers"]
        registry["agents"][0]["excluded_channels"] = []
        errors = self.run_validator(registry)
        self.assertReports(errors, "no human-approval record")
        self.assertReports(errors, "'maintainers' is a private channel")

    def test_write_to_announcements_without_approval_fails(self):
        registry = base_registry()
        registry["agents"][0]["channels"]["read"] = ["learn", "announcements"]
        registry["agents"][0]["channels"]["write"] = ["announcements"]
        errors = self.run_validator(registry)
        self.assertReports(errors, "no human-approval record")

    def test_write_to_announcements_with_approval_record_passes(self):
        registry = base_registry()
        agent = registry["agents"][0]
        agent["channels"]["read"] = ["learn", "announcements"]
        agent["channels"]["write"] = ["announcements"]
        agent["channels"]["write_approval"] = {
            "announcements": {
                "approver_role": "release-owner",
                "condition": "A human approves the exact text of each post before it is sent.",
            }
        }
        self.assertEqual(self.run_validator(registry), [])

    def test_approval_record_naming_a_person_fails(self):
        registry = base_registry()
        agent = registry["agents"][0]
        agent["channels"]["read"] = ["learn", "announcements"]
        agent["channels"]["write"] = ["announcements"]
        agent["channels"]["write_approval"] = {
            "announcements": {
                "approver_role": "Dakota",
                "condition": "A human approves each post.",
            }
        }
        errors = self.run_validator(registry)
        self.assertReports(errors, "names a person, handle, or address")

    def test_stale_approval_record_fails(self):
        registry = base_registry()
        registry["agents"][0]["channels"]["write_approval"] = {
            "announcements": {"approver_role": "release-owner", "condition": "Approved per post."}
        }
        errors = self.run_validator(registry)
        self.assertReports(errors, "which is not in 'channels.write'")

    def test_channel_both_granted_and_excluded_fails(self):
        registry = base_registry()
        registry["agents"][0]["excluded_channels"] = ["learn"]
        errors = self.run_validator(registry)
        self.assertReports(errors, "is listed as excluded and as granted scope")


class ProhibitionTests(RegistryFixtureMixin):
    def _without(self, index: int) -> list[str]:
        remaining = list(LOCKED_PROHIBITIONS)
        del remaining[index]
        registry = base_registry()
        registry["agents"][0]["prohibited"] = remaining
        return self.run_validator(registry)

    def test_missing_silent_removal_prohibition_fails(self):
        self.assertReports(self._without(0), "silently removing or deleting members or content")

    def test_missing_owner_key_prohibition_fails(self):
        self.assertReports(self._without(1), "recovering the owner private key")

    def test_missing_publication_prohibition_fails(self):
        self.assertReports(self._without(2), "announcing without human review")

    def test_missing_maturity_prohibition_fails(self):
        self.assertReports(self._without(3), "changing a maturity or evidence_quality field")

    def test_empty_prohibited_list_fails(self):
        registry = base_registry()
        registry["agents"][0]["prohibited"] = []
        errors = self.run_validator(registry)
        self.assertReports(errors, "must be a non-empty list")

    def test_reworded_prohibition_still_satisfies_the_rule(self):
        registry = base_registry()
        registry["agents"][0]["prohibited"] = [
            "Silently deleting a person or their posts, rather than recommending a human action.",
            "Storing or recovering the owner private key, a token, or a recovery code.",
            "Merging or announcing work that no human maintainer has reviewed.",
            "Modifying a maturity value or an evidence_quality value in any artifact.",
        ]
        self.assertEqual(self.run_validator(registry), [])


class AutonomyTests(RegistryFixtureMixin):
    def test_autonomy_outside_the_vocabulary_fails(self):
        registry = base_registry()
        registry["agents"][0]["autonomy"] = "supervise"
        errors = self.run_validator(registry)
        self.assertReports(errors, "outside the vocabulary")

    def test_unattended_autonomy_fails_with_its_own_message(self):
        for level in ("autonomous", "unattended", "act", "auto-publish"):
            with self.subTest(level=level):
                registry = base_registry()
                registry["agents"][0]["autonomy"] = level
                errors = self.run_validator(registry)
                self.assertReports(errors, "an unattended level")

    def test_each_attended_level_passes(self):
        for level in ("observe", "draft", "recommend"):
            with self.subTest(level=level):
                registry = base_registry()
                registry["agents"][0]["autonomy"] = level
                self.assertEqual(self.run_validator(registry), [])


class EscalationTests(RegistryFixtureMixin):
    def test_escalation_owner_naming_a_person_fails(self):
        registry = base_registry()
        registry["agents"][0]["escalation"]["owner_role"] = "Dakota Smith"
        errors = self.run_validator(registry)
        self.assertReports(errors, "names a person, handle, or address")

    def test_escalation_owner_outside_the_role_vocabulary_fails(self):
        registry = base_registry()
        registry["agents"][0]["escalation"]["owner_role"] = "whoever is around"
        errors = self.run_validator(registry)
        self.assertReports(errors, "which is not a controlled role")

    def test_escalation_route_naming_a_contact_address_fails(self):
        registry = base_registry()
        registry["agents"][0]["escalation"]["route"] = "Email help@example.com directly."
        errors = self.run_validator(registry)
        self.assertReports(errors, "'escalation.route' names a person, handle, or address")

    def test_missing_escalation_route_fails(self):
        registry = base_registry()
        del registry["agents"][0]["escalation"]["route"]
        errors = self.run_validator(registry)
        self.assertReports(errors, "'escalation.route' must describe")

    def test_onward_escalation_role_is_checked(self):
        registry = base_registry()
        registry["agents"][0]["escalation"]["escalates_to"] = ["Dakota"]
        errors = self.run_validator(registry)
        self.assertReports(errors, "'escalation.escalates_to[0]' names a person")


class IdentityTests(RegistryFixtureMixin):
    def test_shared_identity_fails(self):
        registry = base_registry()
        registry["agents"][0]["identity"]["shared_across_instances"] = True
        errors = self.run_validator(registry)
        self.assertReports(errors, "'identity.shared_across_instances' must be false")

    def test_non_dedicated_identity_fails(self):
        registry = base_registry()
        registry["agents"][0]["identity"]["dedicated_identity"] = False
        errors = self.run_validator(registry)
        self.assertReports(errors, "'identity.dedicated_identity' must be true")

    def test_accountable_human_named_as_a_person_fails(self):
        registry = base_registry()
        registry["agents"][0]["identity"]["accountable_human_role"] = "dakota"
        errors = self.run_validator(registry)
        self.assertReports(errors, "'identity.accountable_human_role' names a person")


class StatusAndGateTests(RegistryFixtureMixin):
    def test_enabled_status_fails_while_gate_six_is_open(self):
        registry = base_registry()
        registry["agents"][0]["status"] = "enabled"
        errors = self.run_validator(registry)
        self.assertReports(errors, "while owner gate 6")
        self.assertReports(errors, "still recorded OPEN")

    def test_status_outside_the_vocabulary_fails(self):
        registry = base_registry()
        registry["agents"][0]["status"] = "running"
        errors = self.run_validator(registry)
        self.assertReports(errors, "'status' must be one of")

    def test_missing_gate_row_fails_closed(self):
        owner_review = OWNER_REVIEW_GATE_OPEN.replace("(gate 6)", "(gate six)")
        errors = self.run_validator(base_registry(), owner_review=owner_review)
        self.assertReports(errors, "does not contain exactly one row marked '(gate 6)'")

    def test_missing_hold_row_fails_closed(self):
        owner_review = OWNER_REVIEW_GATE_OPEN.replace("(hold 6)", "(hold six)")
        errors = self.run_validator(base_registry(), owner_review=owner_review)
        self.assertReports(errors, "does not contain exactly one row marked '(hold 6)'")

    def test_enabled_status_is_read_from_the_gate_row_not_hardcoded(self):
        # Synthetic fixture only: it proves the check reads the gate row rather
        # than always rejecting `enabled`. It records nothing about the real
        # repository, where gate 6 remains OPEN.
        owner_review = OWNER_REVIEW_GATE_OPEN.replace(
            "| Select the first agents manually. | **OPEN** |",
            "| Select the first agents manually. | **RECORDED (fixture)** |",
        )
        registry = base_registry()
        registry["agents"][0]["status"] = "enabled"
        self.assertEqual(self.run_validator(registry, owner_review=owner_review), [])


class PrerequisiteTests(RegistryFixtureMixin):
    def test_empty_prerequisites_fail(self):
        registry = base_registry()
        registry["agents"][0]["enablement_prerequisites"] = []
        errors = self.run_validator(registry)
        self.assertReports(errors, "'enablement_prerequisites' must be a non-empty list")

    def test_prerequisite_pointing_at_a_missing_path_fails(self):
        registry = base_registry()
        registry["agents"][0]["enablement_prerequisites"] = [
            "A human runs scripts/nonexistent_check.py before enabling this agent.",
        ]
        errors = self.run_validator(registry)
        self.assertReports(errors, "points at scripts/nonexistent_check.py, which does not exist")

    def test_steward_prerequisites_must_name_hold_six(self):
        registry = base_registry()
        agent = registry["agents"][0]
        agent["profile"] = "buzz/agents/STEWARD.md"
        agent["enablement_prerequisites"] = [
            "Owner gate 6 is recorded as approved by a human in release/OWNER_REVIEW.md.",
        ]
        errors = self.run_validator(registry, profiles=("STEWARD.md",))
        self.assertReports(errors, "must name hold 6")

    def test_steward_prerequisites_naming_hold_six_pass(self):
        registry = base_registry()
        agent = registry["agents"][0]
        agent["profile"] = "buzz/agents/STEWARD.md"
        agent["enablement_prerequisites"] = [
            "Owner gate 6 is recorded as approved by a human in release/OWNER_REVIEW.md.",
            "Hold 6 (Steward escalation readiness) in release/OWNER_REVIEW.md is cleared.",
        ]
        self.assertEqual(self.run_validator(registry, profiles=("STEWARD.md",)), [])


class RegistryStructureTests(RegistryFixtureMixin):
    def test_unsupported_schema_version_fails(self):
        registry = base_registry()
        registry["schema_version"] = 99
        errors = self.run_validator(registry)
        self.assertReports(errors, "'schema_version' is 99")

    def test_missing_agents_list_fails(self):
        registry = base_registry()
        registry["agents"] = []
        errors = self.run_validator(registry)
        self.assertReports(errors, "'agents' must be a non-empty list")

    def test_source_pointing_at_a_missing_path_fails(self):
        registry = base_registry()
        registry["sources"] = ["buzz/community.json", "ops/MISSING.md"]
        errors = self.run_validator(registry)
        self.assertReports(errors, "names ops/MISSING.md, which does not exist")

    def test_missing_registry_file_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "buzz" / "agents").mkdir(parents=True)
            errors = validate_agents.validate(root)
        self.assertReports(errors, "Missing buzz/agents/registry.yaml")

    def test_unparseable_registry_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory, base_registry())
            (root / "buzz" / "agents" / "registry.yaml").write_text(
                "agents: [\n", encoding="utf-8"
            )
            errors = validate_agents.validate(root)
        self.assertReports(errors, "Cannot parse buzz/agents/registry.yaml")


class CommandLineTests(unittest.TestCase):
    def run_main(self, root: Path) -> tuple[int, str]:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = validate_agents.main(["--root", str(root)])
        return code, stream.getvalue()

    def test_main_returns_zero_for_the_repository(self):
        code, output = self.run_main(REPOSITORY_ROOT)
        self.assertEqual(code, 0)
        self.assertIn("Agent registry validation passed.", output)

    def test_main_returns_one_and_prints_the_problem(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = base_registry()
            registry["agents"][0]["status"] = "enabled"
            root = build_root(directory, registry)
            code, output = self.run_main(root)
        self.assertEqual(code, 1)
        self.assertIn("still recorded OPEN", output)
        self.assertIn("1 agent registry problem(s) found.", output)


if __name__ == "__main__":
    unittest.main()
