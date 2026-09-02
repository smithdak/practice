from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
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


triage = load_module("practice_triage", REPOSITORY_ROOT / "scripts" / "triage.py")

BODY = "\n# Hypothetical record\n\nRouting record for a hypothetical issue.\n"

BASE_RECORD = {
    "record_id": "TR-2026-001",
    "subject_ref": "issue #4212",
    "state": "needs-info",
    "category": "bug",
    "owner_role": "reporter",
    "last_actor": "agent",
    "updated": "2026-09-02",
    "evidence": {
        "verification_attempt": "Ran the checker against a fixture and observed a handled error.",
        "inspected_paths": ["scripts/check_links.py"],
        "missing_information": "The report does not state the version or the command.",
        "specific_ask": "Supply the version, the command, and one failing input.",
        "check_point": "2026-09-09",
    },
    "history": [
        {"from": "new", "to": "needs-info", "actor": "agent", "role": "bounded-agent", "date": "2026-09-02"},
    ],
}


def build_root(directory: str) -> Path:
    """A temporary repository root holding the paths sample evidence points at."""
    root = Path(directory)
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "check_links.py").write_text("# fixture\n", encoding="utf-8")
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "behavior.md").write_text("documented behavior\n", encoding="utf-8")
    (root / "ops" / "triage").mkdir(parents=True, exist_ok=True)
    return root


def record_text(record: dict, body: str = BODY) -> str:
    front_matter = yaml.safe_dump(record, sort_keys=False, default_flow_style=False, allow_unicode=True)
    return f"---\n{front_matter}---\n{body}"


class _Remove:
    """Sentinel: passing it as an override deletes that field from the record."""


REMOVE = _Remove()


def write_record(root: Path, name: str = "TR-2026-001.md", **overrides) -> Path:
    record = copy.deepcopy(BASE_RECORD)
    body = overrides.pop("body", BODY)
    record.update(overrides)
    for key in [key for key, value in record.items() if isinstance(value, _Remove)]:
        del record[key]
    path = root / "ops" / "triage" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(record_text(record, body), encoding="utf-8")
    return path


def write_raw(root: Path, text: str, name: str = "TR-2026-001.md") -> Path:
    path = root / "ops" / "triage" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def errors_for(root: Path, path: Path) -> list[str]:
    return triage.validate_record(path, root)


def joined_errors(errors: list[str]) -> str:
    return "\n".join(errors)


class SampleRecordTests(unittest.TestCase):
    def test_committed_sample_record_validates(self):
        sample = REPOSITORY_ROOT / "ops" / "triage" / "SAMPLE_triage_record.md"
        self.assertTrue(sample.is_file(), "the committed sample record is missing")
        self.assertEqual(triage.validate_record(sample, REPOSITORY_ROOT), [])

    def test_committed_sample_record_is_labeled_hypothetical(self):
        sample = REPOSITORY_ROOT / "ops" / "triage" / "SAMPLE_triage_record.md"
        self.assertIn("hypothetical", sample.read_text(encoding="utf-8").lower())

    def test_committed_sample_record_next_lists_legal_moves(self):
        sample = REPOSITORY_ROOT / "ops" / "triage" / "SAMPLE_triage_record.md"
        lines, errors = triage.plan_next(sample, REPOSITORY_ROOT)
        self.assertEqual(errors, [])
        report = "\n".join(lines)
        self.assertIn("ready-for-agent", report)
        self.assertIn("ready-for-human", report)
        self.assertIn("wontfix", report)


class VocabularyTests(unittest.TestCase):
    def test_valid_record_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            self.assertEqual(errors_for(root, write_record(root)), [])

    def test_unknown_state_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(root, write_record(root, state="triaged"))
            self.assertTrue(any("'triaged' is not a triage state" in error for error in errors), joined_errors(errors))

    def test_unknown_category_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(root, write_record(root, category="question"))
            self.assertTrue(any("'question' is not a triage category" in error for error in errors), joined_errors(errors))

    def test_unknown_actor_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(root, write_record(root, last_actor="automation"))
            self.assertTrue(any("'automation' is not an actor" in error for error in errors), joined_errors(errors))

    def test_record_id_must_be_non_identifying(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(root, write_record(root, record_id="alice-triage"))
            self.assertTrue(any("record_id" in error for error in errors), joined_errors(errors))

    def test_subject_ref_must_be_an_issue_or_pull_request_number(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(root, write_record(root, subject_ref="the crash thread in general chat"))
            self.assertTrue(any("subject_ref" in error for error in errors), joined_errors(errors))

    def test_unknown_top_level_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            record = copy.deepcopy(BASE_RECORD)
            record["priority"] = "high"
            path = write_raw(root, record_text(record))
            errors = errors_for(root, path)
            self.assertTrue(any("is not a triage record field" in error for error in errors), joined_errors(errors))


class StructureTests(unittest.TestCase):
    def test_missing_front_matter_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_raw(root, "# Just prose\n")
            errors = errors_for(root, path)
            self.assertTrue(any("no YAML front matter" in error for error in errors), joined_errors(errors))

    def test_invalid_yaml_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_raw(root, "---\nstate: [unclosed\n---\n\nbody\n")
            errors = errors_for(root, path)
            self.assertTrue(any("not valid YAML" in error for error in errors), joined_errors(errors))

    def test_empty_body_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(root, write_record(root, body="\n"))
            self.assertTrue(any("no routing record" in error for error in errors), joined_errors(errors))

    def test_every_error_names_file_field_and_fix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(root, write_record(root, state="triaged"))
            self.assertTrue(errors)
            for error in errors:
                self.assertIn("TR-2026-001.md", error)
                self.assertIn("Fix:", error)


class EvidenceTests(unittest.TestCase):
    def test_missing_required_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            evidence = copy.deepcopy(BASE_RECORD["evidence"])
            del evidence["check_point"]
            errors = errors_for(root, write_record(root, evidence=evidence))
            self.assertTrue(
                any("evidence.check_point" in error and "requires it" in error for error in errors),
                joined_errors(errors),
            )

    def test_evidence_pointer_must_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            evidence = copy.deepcopy(BASE_RECORD["evidence"])
            evidence["inspected_paths"] = ["scripts/does_not_exist.py"]
            errors = errors_for(root, write_record(root, evidence=evidence))
            self.assertTrue(any("does not exist under" in error for error in errors), joined_errors(errors))

    def test_evidence_pointer_may_not_escape_the_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            evidence = copy.deepcopy(BASE_RECORD["evidence"])
            evidence["inspected_paths"] = ["../outside.md"]
            errors = errors_for(root, write_record(root, evidence=evidence))
            self.assertTrue(any("outside the repository" in error for error in errors), joined_errors(errors))

    def test_placeholder_evidence_text_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            evidence = copy.deepcopy(BASE_RECORD["evidence"])
            evidence["specific_ask"] = "TBD"
            errors = errors_for(root, write_record(root, evidence=evidence))
            self.assertTrue(any("placeholder or too short" in error for error in errors), joined_errors(errors))

    def test_unknown_evidence_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            evidence = copy.deepcopy(BASE_RECORD["evidence"])
            evidence["gut_feel"] = "seems real enough"
            errors = errors_for(root, write_record(root, evidence=evidence))
            self.assertTrue(any("not a known evidence field" in error for error in errors), joined_errors(errors))

    def test_check_point_must_be_an_iso_date(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            evidence = copy.deepcopy(BASE_RECORD["evidence"])
            evidence["check_point"] = "next Tuesday"
            errors = errors_for(root, write_record(root, evidence=evidence))
            self.assertTrue(any("evidence.check_point" in error and "ISO date" in error for error in errors), joined_errors(errors))

    def test_commit_must_look_like_a_commit_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    state="ready-for-agent",
                    owner_role="human-triager",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "ready-for-agent", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                    ],
                    evidence={
                        "verification_attempt": "Reproduced the crash against the fixture.",
                        "commit_checked": "yesterday's build",
                        "inspected_paths": ["scripts/check_links.py"],
                        "observed_vs_expected": "Observed a traceback; expected a handled warning.",
                        "bounded_scope_reason": "The fix touches only the link parser and no permissions.",
                    },
                ),
            )
            self.assertTrue(any("is not a commit id" in error for error in errors), joined_errors(errors))

    def test_new_state_may_not_carry_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(root, state="new", owner_role=REMOVE, history=REMOVE),
            )
            self.assertTrue(any("still in state 'new'" in error for error in errors), joined_errors(errors))

    def test_wontfix_needs_a_pointer_or_a_duplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    state="wontfix",
                    owner_role="human-maintainer",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "wontfix", "actor": "human", "role": "human-maintainer", "date": "2026-09-02"},
                    ],
                    evidence={"human_decision_reason": "The behavior matches the documented contract."},
                ),
            )
            self.assertTrue(any("at least one of" in error for error in errors), joined_errors(errors))

    def test_wontfix_with_a_pointer_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    state="wontfix",
                    owner_role="human-maintainer",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "wontfix", "actor": "human", "role": "human-maintainer", "date": "2026-09-02"},
                    ],
                    evidence={
                        "human_decision_reason": "The behavior matches the documented contract.",
                        "inspected_paths": ["docs/behavior.md"],
                    },
                ),
            )
            self.assertEqual(errors, [])


class OwnerRoleTests(unittest.TestCase):
    def test_personal_name_as_owner_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(root, write_record(root, owner_role="Dana Okafor"))
            self.assertTrue(
                any("is not a role label" in error and "never a person" in error for error in errors),
                joined_errors(errors),
            )

    def test_missing_owner_role_is_rejected_when_the_state_needs_one(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(root, write_record(root, owner_role=REMOVE))
            self.assertTrue(any("needs a next owner" in error for error in errors), joined_errors(errors))

    def test_wontfix_owner_must_be_a_maintainer_role(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    state="wontfix",
                    owner_role="reporter",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "wontfix", "actor": "human", "role": "human-maintainer", "date": "2026-09-02"},
                    ],
                    evidence={
                        "human_decision_reason": "The behavior matches the documented contract.",
                        "inspected_paths": ["docs/behavior.md"],
                    },
                ),
            )
            self.assertTrue(any("may not own" in error for error in errors), joined_errors(errors))

    def test_agent_may_not_own_a_ready_for_human_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    state="ready-for-human",
                    owner_role="bounded-agent",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "ready-for-human", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                    ],
                    evidence={
                        "verification_attempt": "Reproduced the crash against the fixture.",
                        "commit_checked": "a1b2c3d",
                        "inspected_paths": ["scripts/check_links.py"],
                        "observed_vs_expected": "Observed a traceback; expected a handled warning.",
                        "maintainer_decision": "Whether the parser change is a breaking change.",
                    },
                ),
            )
            self.assertTrue(any("may not own" in error for error in errors), joined_errors(errors))


class AgentBoundaryTests(unittest.TestCase):
    def test_agent_may_not_leave_a_record_in_a_human_owned_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    state="wontfix",
                    owner_role="human-maintainer",
                    last_actor="agent",
                    history=[
                        {"from": "new", "to": "wontfix", "actor": "human", "role": "human-maintainer", "date": "2026-09-02"},
                    ],
                    evidence={
                        "human_decision_reason": "The behavior matches the documented contract.",
                        "inspected_paths": ["docs/behavior.md"],
                    },
                ),
            )
            self.assertTrue(
                any("may not leave a record in the human-owned state 'wontfix'" in error for error in errors),
                joined_errors(errors),
            )

    def test_agent_may_not_record_the_move_into_wontfix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    state="wontfix",
                    owner_role="human-maintainer",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "wontfix", "actor": "agent", "role": "bounded-agent", "date": "2026-09-02"},
                    ],
                    evidence={
                        "human_decision_reason": "The behavior matches the documented contract.",
                        "inspected_paths": ["docs/behavior.md"],
                    },
                ),
            )
            self.assertTrue(
                any("an agent recorded the move into the human-owned state" in error for error in errors),
                joined_errors(errors),
            )

    def test_agent_may_hold_a_needs_info_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            self.assertEqual(errors_for(root, write_record(root, last_actor="agent")), [])

    def test_safety_category_may_not_be_held_by_an_agent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    category="safety",
                    state="ready-for-human",
                    owner_role="private-intake-owner",
                    last_actor="agent",
                    history=[
                        {"from": "new", "to": "ready-for-human", "actor": "agent", "role": "bounded-agent", "date": "2026-09-02"},
                    ],
                    evidence={
                        "private_route": "code-of-conduct-private-report",
                        "routing_fact": "A safety concern was raised about a published artifact.",
                    },
                ),
            )
            self.assertTrue(
                any("may not hold a 'safety' record" in error for error in errors),
                joined_errors(errors),
            )

    def test_conduct_category_must_sit_in_ready_for_human(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    category="conduct",
                    state="needs-info",
                    owner_role="private-intake-owner",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "needs-info", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                    ],
                ),
            )
            self.assertTrue(
                any("private-routing category" in error for error in errors),
                joined_errors(errors),
            )

    def test_privacy_category_owner_must_be_a_private_route_role(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    category="privacy",
                    state="ready-for-human",
                    owner_role="human-triager",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "ready-for-human", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                    ],
                    evidence={
                        "private_route": "private-intake-route",
                        "routing_fact": "A privacy concern was raised about a published artifact.",
                    },
                ),
            )
            self.assertTrue(any("may not own a 'privacy' record" in error for error in errors), joined_errors(errors))

    def test_access_category_routed_to_a_human_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    category="access",
                    state="ready-for-human",
                    owner_role="private-intake-owner",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "ready-for-human", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                    ],
                    evidence={
                        "private_route": "private-intake-route",
                        "routing_fact": "An access incident was reported against the invitation flow.",
                    },
                ),
            )
            self.assertEqual(errors, [])

    def test_private_route_must_be_a_named_route(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    category="conduct",
                    state="ready-for-human",
                    owner_role="human-moderator",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "ready-for-human", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                    ],
                    evidence={
                        "private_route": "https://example.invalid/report/17",
                        "routing_fact": "A conduct concern was raised in a beta channel.",
                    },
                ),
            )
            self.assertTrue(any("is not a named private route" in error for error in errors), joined_errors(errors))

    def test_enhancement_may_not_be_ready_for_agent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    category="enhancement",
                    state="ready-for-agent",
                    owner_role="human-triager",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "ready-for-agent", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                    ],
                    evidence={
                        "verification_attempt": "Read the request and searched for an existing artifact.",
                        "commit_checked": "a1b2c3d",
                        "inspected_paths": ["scripts/check_links.py"],
                        "observed_vs_expected": "No existing artifact covers the requested capability.",
                        "bounded_scope_reason": "The change would only add a flag.",
                    },
                ),
            )
            self.assertTrue(any("requires category 'bug'" in error for error in errors), joined_errors(errors))


class PersonalDataTests(unittest.TestCase):
    def test_email_address_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            evidence = copy.deepcopy(BASE_RECORD["evidence"])
            evidence["specific_ask"] = "Reply to reporter at someone@example.invalid with the version."
            errors = errors_for(root, write_record(root, evidence=evidence))
            self.assertTrue(any("email address" in error for error in errors), joined_errors(errors))

    def test_member_handle_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            evidence = copy.deepcopy(BASE_RECORD["evidence"])
            evidence["specific_ask"] = "Ask @river-otter for the version and the command."
            errors = errors_for(root, write_record(root, evidence=evidence))
            self.assertTrue(any("member handle" in error for error in errors), joined_errors(errors))

    def test_phone_number_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            evidence = copy.deepcopy(BASE_RECORD["evidence"])
            evidence["specific_ask"] = "Call 555-123-4567 to collect the missing version detail."
            errors = errors_for(root, write_record(root, evidence=evidence))
            self.assertTrue(any("phone number" in error for error in errors), joined_errors(errors))

    def test_credential_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            evidence = copy.deepcopy(BASE_RECORD["evidence"])
            evidence["verification_attempt"] = "Reran the checker with token ghp_abcdefghijklmnopqrstuvwxyz012345."
            errors = errors_for(root, write_record(root, evidence=evidence))
            self.assertTrue(any("credential or key" in error for error in errors), joined_errors(errors))

    def test_identity_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            record = copy.deepcopy(BASE_RECORD)
            record["reporter_name"] = "a person"
            path = write_raw(root, record_text(record))
            errors = errors_for(root, path)
            self.assertTrue(
                any("names a person, an identity, or message content" in error for error in errors),
                joined_errors(errors),
            )

    def test_message_content_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            record = copy.deepcopy(BASE_RECORD)
            record["evidence"]["transcript"] = "the reporter wrote something"
            path = write_raw(root, record_text(record))
            errors = errors_for(root, path)
            self.assertTrue(
                any("evidence.transcript" in error and "message content" in error for error in errors),
                joined_errors(errors),
            )

    def test_personal_data_in_the_body_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(root, write_record(root, body="\n# Record\n\nReported by someone@example.invalid.\n"))
            self.assertTrue(any("email address" in error for error in errors), joined_errors(errors))


class TransitionTests(unittest.TestCase):
    def test_legal_multi_step_history_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    state="ready-for-human",
                    owner_role="human-maintainer",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "needs-info", "actor": "agent", "role": "bounded-agent", "date": "2026-09-01"},
                        {"from": "needs-info", "to": "ready-for-human", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                    ],
                    evidence={
                        "verification_attempt": "Reproduced the crash against the fixture after the reporter answered.",
                        "commit_checked": "a1b2c3d",
                        "inspected_paths": ["scripts/check_links.py"],
                        "observed_vs_expected": "Observed a traceback; expected a handled warning.",
                        "maintainer_decision": "Whether the parser change is a breaking change.",
                    },
                ),
            )
            self.assertEqual(errors, [])

    def test_reopening_a_closure_returns_to_new(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    state="new",
                    owner_role=REMOVE,
                    last_actor="human",
                    evidence=REMOVE,
                    history=[
                        {"from": "new", "to": "wontfix", "actor": "human", "role": "human-maintainer", "date": "2026-09-01"},
                        {"from": "wontfix", "to": "new", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                    ],
                ),
            )
            self.assertEqual(errors, [])

    def test_illegal_transition_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    state="ready-for-agent",
                    owner_role="human-triager",
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "wontfix", "actor": "human", "role": "human-maintainer", "date": "2026-09-01"},
                        {"from": "wontfix", "to": "ready-for-agent", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                    ],
                    evidence={
                        "verification_attempt": "Reproduced the crash against the fixture.",
                        "commit_checked": "a1b2c3d",
                        "inspected_paths": ["scripts/check_links.py"],
                        "observed_vs_expected": "Observed a traceback; expected a handled warning.",
                        "bounded_scope_reason": "The fix touches only the link parser and no permissions.",
                    },
                ),
            )
            self.assertTrue(
                any("is not a legal transition" in error for error in errors),
                joined_errors(errors),
            )

    def test_history_must_start_at_new(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    history=[
                        {"from": "ready-for-human", "to": "needs-info", "actor": "agent", "role": "bounded-agent", "date": "2026-09-02"},
                    ],
                ),
            )
            self.assertTrue(any("enters triage in state 'new'" in error for error in errors), joined_errors(errors))

    def test_broken_history_chain_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    history=[
                        {"from": "new", "to": "ready-for-human", "actor": "human", "role": "human-triager", "date": "2026-09-01"},
                        {"from": "ready-for-agent", "to": "needs-info", "actor": "agent", "role": "bounded-agent", "date": "2026-09-02"},
                    ],
                ),
            )
            self.assertTrue(any("does not continue from the previous transition" in error for error in errors), joined_errors(errors))

    def test_history_must_end_at_the_recorded_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    history=[
                        {"from": "new", "to": "ready-for-human", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                    ],
                ),
            )
            self.assertTrue(any("does not match the last transition" in error for error in errors), joined_errors(errors))

    def test_last_actor_must_match_the_last_transition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    last_actor="human",
                    history=[
                        {"from": "new", "to": "needs-info", "actor": "agent", "role": "bounded-agent", "date": "2026-09-02"},
                    ],
                ),
            )
            self.assertTrue(any("does not match the last transition, made by 'agent'" in error for error in errors), joined_errors(errors))

    def test_agent_actor_needs_the_agent_role(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    history=[
                        {"from": "new", "to": "needs-info", "actor": "agent", "role": "human-triager", "date": "2026-09-02"},
                    ],
                ),
            )
            self.assertTrue(any("is a human role, but the actor is 'agent'" in error for error in errors), joined_errors(errors))

    def test_transition_dates_must_not_go_backwards(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(
                root,
                write_record(
                    root,
                    history=[
                        {"from": "new", "to": "ready-for-human", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                        {"from": "ready-for-human", "to": "needs-info", "actor": "agent", "role": "bounded-agent", "date": "2026-09-01"},
                    ],
                ),
            )
            self.assertTrue(any("precedes the previous transition" in error for error in errors), joined_errors(errors))

    def test_updated_may_not_precede_the_last_transition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            errors = errors_for(root, write_record(root, updated="2026-08-30"))
            self.assertTrue(any("precedes the last transition" in error for error in errors), joined_errors(errors))


class NextCommandTests(unittest.TestCase):
    def test_next_lists_legal_states_and_required_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            lines, errors = triage.plan_next(write_record(root), root)
            self.assertEqual(errors, [])
            report = "\n".join(lines)
            self.assertIn("ready-for-agent", report)
            self.assertIn("bounded_scope_reason", report)
            self.assertIn("human maintainer only", report)
            self.assertNotIn("  new\n", report)

    def test_next_says_the_tool_never_enacts_a_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            lines, _errors = triage.plan_next(write_record(root), root)
            report = "\n".join(lines)
            self.assertIn("never applies a label", report)

    def test_next_blocks_ready_for_agent_for_an_enhancement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_record(
                root,
                category="enhancement",
                state="new",
                owner_role=REMOVE,
                evidence=REMOVE,
                history=REMOVE,
            )
            lines, errors = triage.plan_next(path, root)
            self.assertEqual(errors, [])
            report = "\n".join(lines)
            self.assertIn("Blocked by category:", report)
            self.assertIn("ready-for-agent - state 'ready-for-agent' requires category 'bug'", report)
            self.assertIn("problem_statement", report)

    def test_next_offers_no_public_move_for_a_private_category(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_record(
                root,
                category="conduct",
                state="ready-for-human",
                owner_role="human-moderator",
                last_actor="human",
                history=[
                    {"from": "new", "to": "ready-for-human", "actor": "human", "role": "human-triager", "date": "2026-09-02"},
                ],
                evidence={
                    "private_route": "code-of-conduct-private-report",
                    "routing_fact": "A conduct concern was raised in a beta channel.",
                },
            )
            lines, errors = triage.plan_next(path, root)
            self.assertEqual(errors, [])
            report = "\n".join(lines)
            self.assertIn("Legal next states: none.", report)
            self.assertIn("private intake owner", report)

    def test_next_reports_an_unknown_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            lines, errors = triage.plan_next(write_record(root, state="triaged"), root)
            self.assertEqual(lines, [])
            self.assertTrue(any("legal next states are undefined" in error for error in errors), joined_errors(errors))


class CommandLineTests(unittest.TestCase):
    def run_main(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = triage.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_valid_record_exits_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_record(root)
            code, out, _err = self.run_main(["validate", str(path), "--root", str(root)])
            self.assertEqual(code, 0)
            self.assertIn("0 violation(s)", out)

    def test_violation_exits_one(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_record(root, state="triaged")
            code, _out, err = self.run_main(["validate", str(path), "--root", str(root)])
            self.assertEqual(code, 1)
            self.assertIn("is not a triage state", err)

    def test_missing_path_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            code, _out, err = self.run_main(["validate", str(root / "nope.md"), "--root", str(root)])
            self.assertEqual(code, 2)
            self.assertIn("usage error", err)

    def test_missing_root_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            path = write_record(root)
            code, _out, err = self.run_main(["validate", str(path), "--root", str(root / "absent")])
            self.assertEqual(code, 2)
            self.assertIn("usage error", err)

    def test_no_subcommand_is_a_usage_error(self):
        with self.assertRaises(SystemExit) as raised:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                triage.main([])
        self.assertEqual(raised.exception.code, 2)

    def test_directory_expansion_skips_the_readme(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            write_record(root)
            (root / "ops" / "triage" / "README.md").write_text("# Not a record\n", encoding="utf-8")
            code, out, _err = self.run_main(["validate", str(root / "ops" / "triage"), "--root", str(root)])
            self.assertEqual(code, 0)
            self.assertIn("Checked 1 triage record(s)", out)

    def test_next_on_a_directory_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = build_root(directory)
            write_record(root)
            code, _out, err = self.run_main(["next", str(root / "ops" / "triage"), "--root", str(root)])
            self.assertEqual(code, 2)
            self.assertIn("usage error", err)

    def test_next_on_the_committed_sample_exits_zero(self):
        code, out, _err = self.run_main(
            ["next", str(REPOSITORY_ROOT / "ops" / "triage" / "SAMPLE_triage_record.md"), "--root", str(REPOSITORY_ROOT)]
        )
        self.assertEqual(code, 0)
        self.assertIn("Legal next states:", out)


if __name__ == "__main__":
    unittest.main()
