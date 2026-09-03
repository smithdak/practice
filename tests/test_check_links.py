from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check_links = load_module("practice_check_links", REPOSITORY_ROOT / "scripts" / "check_links.py")

AS_OF = date(2026, 9, 1)


def write(root: Path, name: str, text: str) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def check(root: Path):
    return check_links.check_repository(root, as_of=AS_OF)


class RelativeLinkTests(unittest.TestCase):
    def test_existing_relative_link_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "docs/a.md", "[text](b.md)\n")
            write(root, "docs/b.md", "target\n")
            errors, warnings, _ = check(root)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_parent_segments_are_resolved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "docs/sub/a.md", "[text](../b.md)\n")
            write(root, "docs/b.md", "target\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])

    def test_missing_relative_link_fails_with_line_number(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "docs/a.md", "first\n\nsecond [text](missing.md)\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, ["docs/a.md:3: broken relative link: missing.md"])

    def test_anchor_is_stripped_before_existence_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[text](b.md#does-not-exist)\n")
            write(root, "b.md", "target\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])

    def test_fragment_only_link_is_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[text](#section)\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])

    def test_percent_encoded_target_is_decoded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[text](my%20file.md)\n")
            write(root, "my file.md", "target\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])

    def test_angle_wrapped_target_with_spaces_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[text](<my file.md>)\n")
            write(root, "my file.md", "target\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])


class ExternalTargetTests(unittest.TestCase):
    def test_http_https_mailto_and_buzz_are_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root,
                "a.md",
                "[a](http://example.com/x)\n"
                "[b](https://example.com/x)\n"
                "[c](mailto:someone@example.com)\n"
                "[d](buzz://channel/123)\n",
            )
            errors, _, _ = check(root)
            self.assertEqual(errors, [])

    def test_other_scheme_urls_are_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[a](ftp://example.com/file.txt)\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])


class RepoAbsoluteLinkTests(unittest.TestCase):
    def test_repo_absolute_target_resolves_against_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "docs/a.md", "[text](/docs/b.md)\n")
            write(root, "docs/b.md", "target\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])

    def test_missing_repo_absolute_target_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "docs/a.md", "[text](/docs/missing.md)\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, ["docs/a.md:1: broken repo-absolute link: /docs/missing.md"])


class ReferenceDefinitionTests(unittest.TestCase):
    def test_reference_definition_target_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[text][label]\n\n[label]: ./b.md\n")
            write(root, "b.md", "target\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])

    def test_broken_reference_definition_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[text][label]\n\n[label]: missing.md\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, ["a.md:3: broken relative link: missing.md"])

    def test_reference_definition_with_title_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[label]: b.md \"Title\"\n")
            write(root, "b.md", "target\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])

    def test_reference_definition_to_fragment_is_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[label]: #section\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])

    def test_external_reference_definition_is_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[label]: https://example.com\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])


class EscapeTests(unittest.TestCase):
    def test_link_leaving_repository_root_fails_even_if_file_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory)
            root = outside / "repo"
            root.mkdir()
            write(root, "docs/a.md", "[text](../../outside.md)\n")
            write(outside, "outside.md", "target\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, ["docs/a.md:1: link escapes repository: ../../outside.md"])


class CodeMaskingTests(unittest.TestCase):
    def test_link_inside_fenced_code_block_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            text = "prose\n\n```text\n[example](missing.md)\n```\n\nmore\n"
            write(root, "a.md", text)
            errors, _, _ = check(root)
            self.assertEqual(errors, [])

    def test_link_inside_tilde_fence_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "~~~\n[example](missing.md)\n~~~\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])

    def test_link_inside_inline_code_span_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "Use `[example](missing.md)` inline.\n")
            errors, _, _ = check(root)
            self.assertEqual(errors, [])

    def test_line_numbers_survive_masked_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            text = "```text\nignored\n```\n\n[text](missing.md)\n"
            write(root, "a.md", text)
            errors, _, _ = check(root)
            self.assertEqual(errors, ["a.md:5: broken relative link: missing.md"])


class AsOfDateTests(unittest.TestCase):
    def test_stale_as_of_date_warns_without_failing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "As of: 2026-01-01\n\n[text](b.md)\n")
            write(root, "b.md", "target\n")
            errors, warnings, _ = check(root)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, ["a.md:1: stale as-of date 2026-01-01 (243 days old, limit 90)"])

    def test_bold_as_of_header_is_parsed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "**As of:** 2026-01-01\n")
            _, warnings, _ = check(root)
            self.assertEqual(warnings, ["a.md:1: stale as-of date 2026-01-01 (243 days old, limit 90)"])

    def test_fresh_as_of_date_does_not_warn(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "As of: 2026-08-15\n")
            _, warnings, _ = check(root)
            self.assertEqual(warnings, [])

    def test_boundary_90_days_does_not_warn_but_91_does(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            boundary = (AS_OF - timedelta(days=90)).isoformat()
            write(root, "boundary.md", f"As of: {boundary}\n")
            _, warnings, _ = check(root)
            self.assertEqual(warnings, [])
            stale = (AS_OF - timedelta(days=91)).isoformat()
            write(root, "stale.md", f"As of: {stale}\n")
            _, warnings, _ = check(root)
            self.assertEqual(len(warnings), 1)
            self.assertIn("stale.md:1", warnings[0])

    def test_placeholder_as_of_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "As of: <YYYY-MM-DD>\n")
            _, warnings, _ = check(root)
            self.assertEqual(warnings, [])

    def test_future_as_of_date_does_not_warn(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "As of: 2027-01-01\n")
            _, warnings, _ = check(root)
            self.assertEqual(warnings, [])

    def test_as_of_date_inside_code_fence_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "```text\nAs of: 2020-01-01\n```\n")
            _, warnings, _ = check(root)
            self.assertEqual(warnings, [])


class ScanScopeTests(unittest.TestCase):
    def test_excluded_directories_are_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (".git/x.md", ".worktrees/x.md", "__pycache__/x.md", "sub/__pycache__/x.md"):
                write(root, name, "[text](missing.md)\n")
            errors, _, stats = check(root)
            self.assertEqual(errors, [])
            self.assertEqual(stats["files"], 0)

    def test_non_markdown_files_are_not_scanned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "notes.txt", "[text](missing.md)\n")
            errors, _, stats = check(root)
            self.assertEqual(errors, [])
            self.assertEqual(stats["files"], 0)


class DeterminismTests(unittest.TestCase):
    def test_errors_are_sorted_by_path_then_line(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "z.md", "[a](missing-a.md)\n[b](missing-b.md)\n")
            write(root, "a.md", "[c](missing-c.md)\n")
            errors, _, _ = check(root)
            self.assertEqual(
                errors,
                [
                    "a.md:1: broken relative link: missing-c.md",
                    "z.md:1: broken relative link: missing-a.md",
                    "z.md:2: broken relative link: missing-b.md",
                ],
            )


class MainTests(unittest.TestCase):
    def test_clean_repository_exits_zero_and_prints_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[text](b.md)\n")
            write(root, "b.md", "target\n")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = check_links.main([str(root), "--as-of", AS_OF.isoformat()])
            self.assertEqual(code, 0)
            self.assertIn("0 broken link(s), 0 stale as-of date(s)", stdout.getvalue())

    def test_broken_link_exits_one_with_path_line_message(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "[text](missing.md)\n")
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = check_links.main([str(root), "--as-of", AS_OF.isoformat()])
            self.assertEqual(code, 1)
            self.assertEqual(stderr.getvalue(), "a.md:1: broken relative link: missing.md\n")

    def test_stale_warning_does_not_change_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "As of: 2020-01-01\n\n[text](b.md)\n")
            write(root, "b.md", "target\n")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = check_links.main([str(root), "--as-of", AS_OF.isoformat()])
            self.assertEqual(code, 0)
            self.assertIn("1 stale as-of date(s)", stdout.getvalue())
            self.assertIn("a.md:1: stale as-of date 2020-01-01", stdout.getvalue())


class CoverageTests(unittest.TestCase):
    """Every markdown file lands in exactly one bucket, and the counts say which."""

    def test_dated_undatable_and_silent_files_are_counted_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "dated.md", "As of: 2026-08-01\n\nAs of: 2026-08-15\n")
            write(root, "undatable.md", "Current as of the last platform snapshot.\n")
            write(root, "placeholder.md", "As of: YYYY-MM-DD\n")
            write(root, "silent.md", "No currency claim here.\n")
            errors, warnings, stats = check(root)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])
            self.assertEqual(stats["files"], 4)
            self.assertEqual(stats["dated_files"], 1)
            self.assertEqual(stats["dated_lines"], 2)
            self.assertEqual(stats["undatable_files"], 2)
            self.assertEqual(stats["stale_dates"], 0)
            self.assertEqual(stats["malformed_dates"], 0)

    def test_coverage_sentence_names_the_files_the_rule_cannot_see(self):
        sentence = check_links.coverage_sentence(
            {"files": 10, "dated_files": 2, "dated_lines": 3, "undatable_files": 1}
        )
        self.assertEqual(
            sentence,
            '2 of 10 markdown file(s) carry a dated As-of line the rule can read (3 line(s) read); '
            '1 file(s) mention "as of" in a form the rule cannot date; the rule says nothing about '
            "the remaining 7.",
        )

    def test_coverage_is_printed_on_a_clean_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "As of: 2026-08-20\n")
            write(root, "b.md", "plain\n")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = check_links.main([str(root), "--as-of", AS_OF.isoformat()])
            self.assertEqual(code, 0)
            lines = stdout.getvalue().splitlines()
            self.assertTrue(lines[0].startswith("As-of coverage: 1 of 2 markdown file(s)"), lines[0])
            self.assertTrue(lines[-1].startswith("check_links_summary: "), lines[-1])

    def test_as_of_mention_inside_code_is_not_a_currency_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "```\nAs of: 2020-01-01\n```\n")
            _errors, _warnings, stats = check(root)
            self.assertEqual(stats["dated_files"], 0)
            self.assertEqual(stats["undatable_files"], 0)


class MalformedDateTests(unittest.TestCase):
    def test_non_calendar_date_is_an_error_with_path_and_line(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "intro\n\nAs of: 2026-02-30\n")
            errors, warnings, stats = check(root)
            self.assertEqual(errors, ["a.md:3: malformed as-of date 2026-02-30 (not a calendar date)"])
            self.assertEqual(warnings, [])
            self.assertEqual(stats["malformed_dates"], 1)
            self.assertEqual(stats["dated_lines"], 0)
            self.assertEqual(stats["undatable_files"], 1)

    def test_malformed_date_exits_one_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "As of: 2026-13-01\n")
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = check_links.main([str(root), "--as-of", AS_OF.isoformat()])
            self.assertEqual(code, 1)
            self.assertEqual(stderr.getvalue(), "a.md:1: malformed as-of date 2026-13-01 (not a calendar date)\n")
            self.assertIn("1 malformed as-of date(s)", stdout.getvalue())

    def test_link_errors_precede_date_errors_within_a_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "As of: 2026-02-30\n\n[x](missing.md)\n")
            errors, _warnings, _stats = check(root)
            self.assertEqual(
                errors,
                [
                    "a.md:3: broken relative link: missing.md",
                    "a.md:1: malformed as-of date 2026-02-30 (not a calendar date)",
                ],
            )


class FailOnStaleTests(unittest.TestCase):
    def run_main(self, root: Path, *flags: str) -> tuple[int, str]:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = check_links.main([str(root), "--as-of", AS_OF.isoformat(), *flags])
        return code, stdout.getvalue()

    def test_flag_turns_a_stale_warning_into_exit_one(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "As of: 2020-01-01\n")
            self.assertEqual(self.run_main(root)[0], 0)
            self.assertEqual(self.run_main(root, "--fail-on-stale")[0], 1)

    def test_flag_changes_nothing_but_the_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "As of: 2020-01-01\n")
            self.assertEqual(self.run_main(root)[1], self.run_main(root, "--fail-on-stale")[1])

    def test_flag_is_inert_when_nothing_is_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "As of: 2026-08-20\n")
            self.assertEqual(self.run_main(root, "--fail-on-stale")[0], 0)


class SummaryLineTests(unittest.TestCase):
    def test_summary_line_round_trips_through_parse(self):
        stats = {
            "files": 5, "dated_files": 2, "dated_lines": 3, "undatable_files": 1,
            "stale_dates": 1, "broken_links": 0, "malformed_dates": 0, "links": 12, "limit_days": 90,
        }
        line = check_links.summary_line(stats)
        self.assertEqual(
            line,
            "check_links_summary: files=5 dated_files=2 dated_lines=3 undatable_files=1 "
            "stale_dates=1 broken_links=0 malformed_dates=0 links=12 limit_days=90",
        )
        self.assertEqual(check_links.parse_summary_line(line), stats)

    def test_parse_rejects_lines_that_are_not_a_summary(self):
        self.assertIsNone(check_links.parse_summary_line("Checked 3 markdown file(s)"))
        self.assertIsNone(check_links.parse_summary_line("check_links_summary: files=3"))
        self.assertIsNone(check_links.parse_summary_line("check_links_summary: files=3 bogus=1"))

    def test_summary_line_is_the_last_line_of_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, "a.md", "As of: 2020-01-01\n\n[x](b.md)\n")
            write(root, "b.md", "ok\n")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                check_links.main([str(root), "--as-of", AS_OF.isoformat()])
            last = stdout.getvalue().splitlines()[-1]
            counts = check_links.parse_summary_line(last)
            self.assertIsNotNone(counts)
            self.assertEqual(counts["stale_dates"], 1)
            self.assertEqual(counts["links"], 1)


if __name__ == "__main__":
    unittest.main()
