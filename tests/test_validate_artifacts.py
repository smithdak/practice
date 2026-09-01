"""Tests for scripts/validate_artifacts.py.

All fixtures live in temporary directories; no test asserts on live
repository contents.
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


validate_artifacts = load_module(
    "practice_validate_artifacts", REPOSITORY_ROOT / "scripts" / "validate_artifacts.py"
)

PRACTICE_CORE_HEADINGS = validate_artifacts.PRACTICE_CORE_HEADINGS
PRACTICE_MATURE_HEADINGS = validate_artifacts.PRACTICE_MATURE_HEADINGS
GUIDE_HEADINGS = validate_artifacts.GUIDE_HEADINGS
LAB_HEADINGS = validate_artifacts.LAB_HEADINGS
STORY_SECTIONS = validate_artifacts.STORY_SECTIONS

PRACTICE_FIELDS = {
    "artifact_type": "practice",
    "title": "Test practice",
    "summary": "Do a bounded thing.",
    "maturity": "proposed",
    "capability": "use",
    "roles": ["individual-practitioner"],
    "version": "0.1.0",
    "license": "CC-BY-4.0",
    "created": "2026-01-01",
    "updated": "2026-01-02",
    "evidence_quality": "none",
}

LAB_FIELDS = {
    "artifact_type": "lab",
    "title": "Test lab",
    "summary": "Answer one bounded question.",
    "status": "proposed",
    "primary_capability": "learn",
    "roles": ["builder"],
    "task_set_version": "0.1.0",
    "run_count": 0,
    "result_status": "not-run",
    "last_run": None,
    "version": "0.1.0",
    "license": "CC-BY-4.0",
    "created": "2026-01-01",
    "updated": "2026-01-01",
}

STORY_FIELDS = {
    "artifact_type": "story",
    "title": "Test story",
    "status": "draft",
    "organization": "withheld",
    "evidence_quality": "none",
    "version": "0.1.0",
    "license": "CC-BY-4.0",
    "created": "2026-01-01",
    "updated": "2026-01-01",
}

GUIDE_FIELDS = {
    "artifact_type": "guide",
    "title": "Test guide",
    "summary": "A path to one outcome.",
    "status": "draft",
    "capability": "use",
    "audience": ["individual-practitioner"],
    "version": "0.1.0",
    "license": "CC-BY-4.0",
    "created": "2026-01-01",
    "updated": "2026-01-01",
}


def front_matter(fields: dict) -> str:
    lines = ["---"]
    for key, value in fields.items():
        if isinstance(value, list):
            lines.append(f"{key}: [{', '.join(value)}]")
        elif value is None:
            lines.append(f"{key}: null")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def body_for(headings: list[str], extra: str = "") -> str:
    sections = [f"## {name}\n\nContent for {name}.\n" for name in headings]
    return "\n".join(sections) + extra


def practice_body(mature: bool = False, trial_link: bool = False) -> str:
    headings = list(PRACTICE_CORE_HEADINGS)
    if mature:
        headings += list(PRACTICE_MATURE_HEADINGS)
    extra = "\n[Recorded trial](../labs/001-trial.md)\n" if trial_link else ""
    return body_for(headings, extra)


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class TempRootTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def errors_for(self, rel: str, text: str) -> list[str]:
        write(self.root, rel, text)
        errors, _ = validate_artifacts.validate_root(self.root)
        return errors


class PracticeTests(TempRootTestCase):
    def test_valid_proposed_practice_passes(self):
        text = front_matter(PRACTICE_FIELDS) + "\n" + practice_body()
        self.assertEqual(self.errors_for("practices/001-thing.md", text), [])

    def test_missing_required_field_is_reported(self):
        fields = {k: v for k, v in PRACTICE_FIELDS.items() if k != "summary"}
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + practice_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("required front matter field 'summary'", errors[0])

    def test_artifact_type_must_match_directory(self):
        fields = dict(PRACTICE_FIELDS, artifact_type="story")
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + practice_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("does not match expected 'practice'", errors[0])

    def test_invalid_maturity_value_is_rejected(self):
        fields = dict(PRACTICE_FIELDS, maturity="draft")
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + practice_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("'maturity' value 'draft'", errors[0])

    def test_tested_with_none_evidence_is_rejected(self):
        fields = dict(PRACTICE_FIELDS, maturity="tested", evidence_quality="none")
        body = practice_body(mature=True, trial_link=True)
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + body)
        self.assertEqual(len(errors), 1)
        self.assertIn("maturity 'tested' requires evidence_quality", errors[0])

    def test_tested_without_trial_link_is_rejected(self):
        fields = dict(PRACTICE_FIELDS, maturity="tested", evidence_quality="single-run")
        body = practice_body(mature=True, trial_link=False)
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + body)
        self.assertEqual(len(errors), 1)
        self.assertIn("linked trial or evidence record", errors[0])

    def test_tested_with_trial_link_and_evidence_passes(self):
        fields = dict(PRACTICE_FIELDS, maturity="tested", evidence_quality="single-run")
        body = practice_body(mature=True, trial_link=True)
        self.assertEqual(self.errors_for("practices/001-thing.md", front_matter(fields) + body), [])

    def test_tested_missing_mature_headings_is_rejected(self):
        fields = dict(PRACTICE_FIELDS, maturity="tested", evidence_quality="single-run")
        body = practice_body(mature=False, trial_link=True)
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + body)
        self.assertEqual(len(errors), 3)
        for name in PRACTICE_MATURE_HEADINGS:
            self.assertTrue(any(f"'## {name}'" in error for error in errors), errors)

    def test_verified_requires_last_verified_and_evidence(self):
        fields = dict(PRACTICE_FIELDS, maturity="verified", evidence_quality="none")
        body = practice_body(mature=True, trial_link=True)
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + body)
        joined = "\n".join(errors)
        self.assertIn("maturity 'verified' requires evidence_quality", joined)
        self.assertIn("'last_verified'", joined)

    def test_deprecated_requires_dates_and_notice(self):
        fields = dict(PRACTICE_FIELDS, maturity="deprecated")
        body = practice_body()
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + body)
        joined = "\n".join(errors)
        self.assertIn("'deprecated_on'", joined)
        self.assertIn("'deprecation_reason'", joined)
        self.assertIn("'## Deprecation notice'", joined)

    def test_updated_before_created_is_rejected(self):
        fields = dict(PRACTICE_FIELDS, created="2026-02-01", updated="2026-01-01")
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + practice_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("must not precede", errors[0])

    def test_bad_semver_is_rejected(self):
        fields = dict(PRACTICE_FIELDS, version="1.0")
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + practice_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("MAJOR.MINOR.PATCH", errors[0])

    def test_unknown_license_is_rejected(self):
        fields = dict(PRACTICE_FIELDS, license="MIT")
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + practice_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("'license' value 'MIT'", errors[0])

    def test_uncontrolled_role_is_rejected(self):
        fields = dict(PRACTICE_FIELDS, roles=["wizard"])
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + practice_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("uncontrolled values: wizard", errors[0])

    def test_secondary_capability_repeating_primary_is_rejected(self):
        fields = dict(PRACTICE_FIELDS, secondary_capabilities=["use", "learn"])
        errors = self.errors_for("practices/001-thing.md", front_matter(fields) + practice_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("must not repeat the primary value: use", errors[0])

    def test_missing_front_matter_is_rejected(self):
        errors = self.errors_for("practices/001-thing.md", "# Just a title\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("must begin with '---' front matter", errors[0])
        self.assertRegex(errors[0], r"^practices/001-thing\.md:1: ")

    def test_unclosed_front_matter_reports_line(self):
        errors = self.errors_for("practices/001-thing.md", "---\nartifact_type: practice\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("never closed", errors[0])

    def test_index_readme_without_front_matter_is_skipped(self):
        write(self.root, "practices/README.md", "# Practices index\n")
        text = front_matter(PRACTICE_FIELDS) + "\n" + practice_body()
        self.assertEqual(self.errors_for("practices/001-thing.md", text), [])


class LabTests(TempRootTestCase):
    def lab_body(self) -> str:
        return body_for(list(LAB_HEADINGS))

    def test_valid_not_run_lab_passes(self):
        text = front_matter(LAB_FIELDS) + "\n" + self.lab_body()
        self.assertEqual(self.errors_for("labs/001-trial.md", text), [])

    def test_last_run_must_be_null_when_not_run(self):
        fields = dict(LAB_FIELDS, last_run="2026-01-02")
        errors = self.errors_for("labs/001-trial.md", front_matter(fields) + self.lab_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("'last_run' must be null", errors[0])

    def test_last_run_required_when_partial(self):
        fields = dict(LAB_FIELDS, status="running", result_status="partial", run_count=2, last_run=None)
        errors = self.errors_for("labs/001-trial.md", front_matter(fields) + self.lab_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("'last_run' must be an ISO date", errors[0])

    def test_negative_run_count_is_rejected(self):
        fields = dict(LAB_FIELDS, run_count=-1)
        errors = self.errors_for("labs/001-trial.md", front_matter(fields) + self.lab_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("non-negative integer", errors[0])

    def test_invalid_result_status_is_rejected(self):
        fields = dict(LAB_FIELDS, result_status="maybe")
        errors = self.errors_for("labs/001-trial.md", front_matter(fields) + self.lab_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("'result_status' value 'maybe'", errors[0])

    def test_missing_canonical_heading_is_rejected(self):
        headings = [h for h in LAB_HEADINGS if h != "Cost capture"]
        errors = self.errors_for("labs/001-trial.md", front_matter(LAB_FIELDS) + body_for(headings))
        self.assertEqual(len(errors), 1)
        self.assertIn("'## Cost capture' is missing", errors[0])

    def test_out_of_order_headings_are_rejected(self):
        headings = list(LAB_HEADINGS)
        headings[0], headings[1] = headings[1], headings[0]
        errors = self.errors_for("labs/001-trial.md", front_matter(LAB_FIELDS) + body_for(headings))
        self.assertEqual(len(errors), 1)
        self.assertIn("appears before", errors[0])

    def test_deprecated_lab_requires_dates_and_reason(self):
        fields = dict(LAB_FIELDS, status="deprecated")
        errors = self.errors_for("labs/001-trial.md", front_matter(fields) + self.lab_body())
        joined = "\n".join(errors)
        self.assertIn("'deprecated_on'", joined)
        self.assertIn("'deprecation_reason'", joined)


class StoryTests(TempRootTestCase):
    def story_body(self) -> str:
        return body_for(list(STORY_SECTIONS))

    def test_valid_draft_story_passes(self):
        text = front_matter(STORY_FIELDS) + "\n" + self.story_body()
        self.assertEqual(self.errors_for("stories/001-real.md", text), [])

    def test_published_story_with_none_evidence_is_rejected(self):
        fields = dict(STORY_FIELDS, status="published")
        errors = self.errors_for("stories/001-real.md", front_matter(fields) + self.story_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("status 'published' requires evidence_quality", errors[0])

    def test_missing_required_section_is_rejected(self):
        sections = [s for s in STORY_SECTIONS if s != "Result"]
        errors = self.errors_for("stories/001-real.md", front_matter(STORY_FIELDS) + body_for(sections))
        self.assertEqual(len(errors), 1)
        self.assertIn("'## Result'", errors[0])

    def test_empty_result_section_is_rejected(self):
        sections = [f"## {name}\n\n{x}\n" for name, x in zip(STORY_SECTIONS, ["content"] * len(STORY_SECTIONS))]
        sections[STORY_SECTIONS.index("Result")] = "## Result\n\n"
        errors = self.errors_for("stories/001-real.md", front_matter(STORY_FIELDS) + "\n" + "".join(sections))
        self.assertEqual(len(errors), 1)
        self.assertIn("'## Result' must not be empty", errors[0])

    def test_invalid_organization_is_rejected(self):
        fields = dict(STORY_FIELDS, organization="secret")
        errors = self.errors_for("stories/001-real.md", front_matter(fields) + self.story_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("'organization' value 'secret'", errors[0])

    def test_story_does_not_require_summary_front_matter(self):
        self.assertNotIn("summary", validate_artifacts.REQUIRED_FIELDS["story"])
        text = front_matter(STORY_FIELDS) + "\n" + self.story_body()
        self.assertEqual(self.errors_for("stories/001-real.md", text), [])


class GuideTests(TempRootTestCase):
    def guide_body(self) -> str:
        return body_for(list(GUIDE_HEADINGS))

    def test_valid_draft_guide_passes(self):
        text = front_matter(GUIDE_FIELDS) + "\n" + self.guide_body()
        self.assertEqual(self.errors_for("guides/example/README.md", text), [])

    def test_published_guide_requires_last_verified(self):
        fields = dict(GUIDE_FIELDS, status="published")
        errors = self.errors_for("guides/example/README.md", front_matter(fields) + self.guide_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("status 'published' requires 'last_verified'", errors[0])

    def test_out_of_order_headings_are_rejected(self):
        headings = list(GUIDE_HEADINGS)
        headings[0], headings[1] = headings[1], headings[0]
        errors = self.errors_for("guides/example/README.md", front_matter(GUIDE_FIELDS) + body_for(headings))
        self.assertEqual(len(errors), 1)
        self.assertIn("appears before", errors[0])

    def test_deprecated_guide_requires_notice(self):
        fields = dict(GUIDE_FIELDS, status="deprecated")
        errors = self.errors_for("guides/example/README.md", front_matter(fields) + self.guide_body())
        joined = "\n".join(errors)
        self.assertIn("'deprecated_on'", joined)
        self.assertIn("'deprecation_reason'", joined)
        self.assertIn("'## Deprecation notice'", joined)

    def test_uncontrolled_audience_role_is_rejected(self):
        fields = dict(GUIDE_FIELDS, audience=["celebrity"])
        errors = self.errors_for("guides/example/README.md", front_matter(fields) + self.guide_body())
        self.assertEqual(len(errors), 1)
        self.assertIn("uncontrolled values: celebrity", errors[0])


class GuideModuleTests(TempRootTestCase):
    def test_module_without_front_matter_passes(self):
        text = "# A module\n\nSome content.\n"
        self.assertEqual(self.errors_for("guides/ai-native-practitioner/01-x.md", text), [])

    def test_module_with_mismatched_artifact_type_is_rejected(self):
        text = "---\nartifact_type: practice\n---\n\n# A module\n"
        errors = self.errors_for("guides/ai-native-practitioner/01-x.md", text)
        self.assertEqual(len(errors), 1)
        self.assertIn("must be 'guide'", errors[0])

    def test_module_without_h1_is_rejected(self):
        text = "No title here.\n"
        errors = self.errors_for("guides/ai-native-practitioner/01-x.md", text)
        self.assertEqual(len(errors), 1)
        self.assertIn("'# ' title heading", errors[0])

    def test_index_documents_without_front_matter_are_skipped(self):
        write(self.root, "guides/README.md", "# Guides index\n")
        write(self.root, "guides/ai-native-practitioner/CURRICULUM.md", "# Curriculum map\n")
        errors, counts = validate_artifacts.validate_root(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(dict(counts), {})


class DiscoveryAndCliTests(TempRootTestCase):
    def test_artifact_without_front_matter_in_story_dir_is_rejected(self):
        errors = self.errors_for("stories/loose.md", "# Not an artifact\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("must begin with '---' front matter", errors[0])

    def test_error_format_is_path_line_message(self):
        errors = self.errors_for("stories/001-real.md", front_matter(STORY_FIELDS) + body_for(["Summary"]))
        self.assertTrue(errors)
        for error in errors:
            self.assertRegex(error, r"^[^:]+:\d+: .+$")

    def test_cli_exit_codes(self):
        write(self.root, "stories/001-real.md", front_matter(STORY_FIELDS) + body_for(list(STORY_SECTIONS)))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code_ok = validate_artifacts.main(["--root", str(self.root)])
        self.assertEqual(code_ok, 0)
        self.assertIn("1 story", out.getvalue())
        write(self.root, "stories/002-bad.md", front_matter(dict(STORY_FIELDS, status="published")))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            code_bad = validate_artifacts.main(["--root", str(self.root)])
        self.assertEqual(code_ok, 0)
        self.assertEqual(code_bad, 1)
        self.assertIn("stories/002-bad.md:", err.getvalue())

    def test_empty_root_passes_with_no_artifacts(self):
        errors, counts = validate_artifacts.validate_root(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(sum(counts.values()), 0)


if __name__ == "__main__":
    unittest.main()
