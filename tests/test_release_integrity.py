from __future__ import annotations

import importlib.util
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


validate = load_module("practice_validate", REPOSITORY_ROOT / "scripts" / "validate.py")
taskctl = load_module("practice_taskctl", REPOSITORY_ROOT / "scripts" / "taskctl.py")


class LinkValidationTests(unittest.TestCase):
    def test_repository_below_dot_worktrees_is_still_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / ".worktrees" / "Q005"
            root.mkdir(parents=True)
            (root / "entry.md").write_text("[missing](missing.md)\n", encoding="utf-8")
            errors: list[str] = []

            validate.validate_links(root, errors)

            self.assertEqual(errors, ["Broken relative link: entry.md -> missing.md"])

    def test_nested_ignored_directory_is_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / ".git"
            nested.mkdir()
            (nested / "ignored.md").write_text("[missing](missing.md)\n", encoding="utf-8")
            errors: list[str] = []

            validate.validate_links(root, errors)

            self.assertEqual(errors, [])


class ReleaseEvidenceTests(unittest.TestCase):
    def test_complete_committed_task_evidence_passes_without_local_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "output.md").write_text("result\n", encoding="utf-8")
            (root / "handoff.md").write_text("# Handoff\n\n## Status\n\nCOMPLETE\n", encoding="utf-8")
            manifest = {"tasks": [{"id": "T001", "outputs": ["output.md"], "handoff": "handoff.md"}]}
            errors: list[str] = []

            validate.validate_committed_task_evidence(root, manifest, errors)

            self.assertEqual(errors, [])

    def test_blocked_handoff_cannot_pass_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "output.md").write_text("result\n", encoding="utf-8")
            (root / "handoff.md").write_text("# Handoff\n\n## Status\n\nBLOCKED\n", encoding="utf-8")
            manifest = {"tasks": [{"id": "T001", "outputs": ["output.md"], "handoff": "handoff.md"}]}
            errors: list[str] = []

            validate.validate_committed_task_evidence(root, manifest, errors)

            self.assertEqual(errors, ["Release task T001 handoff is BLOCKED: handoff.md"])

    def test_missing_and_empty_committed_evidence_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "empty.md").write_text("", encoding="utf-8")
            (root / "handoff.md").write_text("# Handoff\n\n## Status\n\nCOMPLETE\n", encoding="utf-8")
            manifest = {
                "tasks": [
                    {
                        "id": "T001",
                        "outputs": ["missing.md", "empty.md"],
                        "handoff": "handoff.md",
                    }
                ]
            }
            errors: list[str] = []

            validate.validate_committed_task_evidence(root, manifest, errors)

            self.assertEqual(
                errors,
                [
                    "Release task T001 missing committed evidence: missing.md",
                    "Release task T001 has empty committed evidence: empty.md",
                ],
            )


class PublicationTokenTests(unittest.TestCase):
    def test_prose_placeholder_is_allowed(self):
        errors: list[str] = []
        validate.validate_publication_tokens(
            "ops/example.md",
            "Use a category or placeholder to protect the real detail.",
            errors,
        )
        self.assertEqual(errors, [])

    def test_social_kit_publication_token_is_an_approved_template_hold(self):
        errors: list[str] = []
        validate.validate_publication_tokens(
            "content/launch/SOCIAL_KIT.md",
            "Inspect [REPOSITORY_URL] before publication.",
            errors,
        )
        self.assertEqual(errors, [])

    def test_publication_token_outside_approved_template_fails(self):
        errors: list[str] = []
        validate.validate_publication_tokens(
            "practices/001-context-pack.md",
            "Approval owner: [OWNER NAME]",
            errors,
        )
        self.assertEqual(
            errors,
            ["Release publication token found outside an approved template: practices/001-context-pack.md"],
        )

    def test_at_handle_outside_social_kit_fails(self):
        errors: list[str] = []
        validate.validate_publication_tokens(
            "release/announcement.md",
            "Follow [@OWNER_HANDLE] for updates.",
            errors,
        )
        self.assertEqual(
            errors,
            ["Release publication token found outside an approved template: release/announcement.md"],
        )

    def test_fenced_context_pack_date_example_passes(self):
        errors: list[str] = []
        validate.validate_publication_tokens(
            "practices/001-context-pack.md",
            "```text\nLast reviewed: [YYYY-MM-DD]\n```\n",
            errors,
        )
        self.assertEqual(errors, [])

    def test_code_example_tokens_are_not_publication_values(self):
        errors: list[str] = []
        validate.validate_publication_tokens(
            "release/example.md",
            "Use `TODO` only as a scanner example.\n\n```text\n[OWNER NAME]\n```\n",
            errors,
        )
        self.assertEqual(errors, [])


class TaskScopeTests(unittest.TestCase):
    def test_build_task_rejects_unexpected_path(self):
        task = {"mode": "build", "outputs": ["owned.md"], "handoff": "handoff.md"}
        unchanged, unexpected = taskctl.validate_changed_scope(task, {"owned.md", "handoff.md", "other.md"})
        self.assertEqual(unchanged, [])
        self.assertEqual(unexpected, ["other.md"])

    def test_integration_task_allows_review_corrections(self):
        task = {"mode": "integration", "outputs": ["report.md"], "handoff": "handoff.md"}
        unchanged, unexpected = taskctl.validate_changed_scope(task, {"report.md", "handoff.md", "reviewed.md"})
        self.assertEqual(unchanged, [])
        self.assertEqual(unexpected, [])


if __name__ == "__main__":
    unittest.main()
