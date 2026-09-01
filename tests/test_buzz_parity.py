"""Parity tests between buzz/INFORMATION_ARCHITECTURE.md and buzz/community.json.

The document and the configuration describe the same channel set at different
levels of detail, and the test encodes that mapping explicitly:

- The "Channel map" table names each channel and its access level. The
  configuration must carry exactly those names, and the documented access
  maps to visibility as Private -> "private" and Open -> "open".
- The "Launch decision" section fixes the totals: twelve channels, two
  private, ten open, and every channel is a stream, so every configured
  channel must have type "stream".
- The "Channel lifecycle" section requires each channel to have a distinct
  name, topic, purpose, canvas, and idempotent seed, but the document does
  not enumerate per-channel topic, purpose, canvas, or seed text.
  buzz/community.json is the canonical configuration for those fields (see
  buzz/BOOTSTRAP_RUNBOOK.md), so parity requires them to be present,
  non-empty, and distinct across channels rather than equal to prose in the
  document.
- Canvas and seed values are repository paths relative to the repository
  root; each must exist on disk, and each seed must carry exactly one
  practice-seed idempotency marker.
- release/LAUNCH_CHECKLIST.md independently pins the expected channel count
  ("twelve stream channels").
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
COMMUNITY_CONFIG_PATH = REPOSITORY_ROOT / "buzz" / "community.json"
INFORMATION_ARCHITECTURE_PATH = REPOSITORY_ROOT / "buzz" / "INFORMATION_ARCHITECTURE.md"
LAUNCH_CHECKLIST_PATH = REPOSITORY_ROOT / "release" / "LAUNCH_CHECKLIST.md"

DOCUMENT_ACCESS_TO_CONFIG_VISIBILITY = {"Private": "private", "Open": "open"}

WORD_TO_INT = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}

SEED_MARKER_PATTERN = re.compile(r"<!--\s*practice-seed:[^\s>]+\s*-->")


def fail(message: str):
    raise AssertionError(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def int_from_word(word: str, context: str) -> int:
    number = WORD_TO_INT.get(word.lower())
    if number is None:
        fail(f"{context}: cannot parse the count word {word!r}; extend WORD_TO_INT")
    return number


def document_section(text: str, heading: str) -> str:
    start = re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE)
    if start is None:
        fail(f"{INFORMATION_ARCHITECTURE_PATH.name}: missing '## {heading}' section")
    next_section = re.search(r"^## ", text[start.end():], re.MULTILINE)
    end = start.end() + next_section.start() if next_section else len(text)
    return text[start.end():end]


def parse_documented_channels(doc_text: str) -> list[tuple[str, str]]:
    section = document_section(doc_text, "Channel map")
    rows: list[list[str]] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        fail("Channel map: expected a header row plus one row per channel")
    header, channel_rows = rows[0], rows[1:]
    if header[:2] != ["Channel", "Access"]:
        fail(f"Channel map: unexpected table header {header[:2]!r}; expected ['Channel', 'Access', ...]")
    documented: list[tuple[str, str]] = []
    for cells in channel_rows:
        if len(cells) < 2:
            fail(f"Channel map: row {cells!r} lacks Channel and Access cells")
        documented.append((cells[0].strip("`"), cells[1]))
    return documented


def parse_launch_decision(doc_text: str) -> dict:
    section = document_section(doc_text, "Launch decision")

    def documented_count(pattern: str, label: str) -> int:
        match = re.search(pattern, section)
        if match is None:
            fail(f"Launch decision: no sentence matches {pattern!r}")
        return int_from_word(match.group(1), "Launch decision")

    return {
        "total": documented_count(r"(\w+) Buzz channels", "total"),
        "private": documented_count(r"(\w+) private operating channels", "private"),
        "open": documented_count(r"(\w+) open participation channels", "open"),
        "streams_only": "Every channel is a stream" in section,
    }


def parse_expected_channel_count(checklist_text: str) -> int:
    matches = re.findall(r"(\w+) stream channels", checklist_text)
    if len(matches) != 1:
        fail(f"{LAUNCH_CHECKLIST_PATH.name}: expected exactly one 'N stream channels' phrase, found {matches!r}")
    return int_from_word(matches[0], LAUNCH_CHECKLIST_PATH.name)


def load_configured_channels() -> dict[str, dict]:
    config = json.loads(read_text(COMMUNITY_CONFIG_PATH))
    channels = config.get("channels")
    if not isinstance(channels, list):
        fail(f"{COMMUNITY_CONFIG_PATH.name}: 'channels' must be a list")
    configured: dict[str, dict] = {}
    for channel in channels:
        name = channel.get("name")
        if not isinstance(name, str) or not name:
            fail(f"{COMMUNITY_CONFIG_PATH.name}: channel without a usable name: {channel!r}")
        if name in configured:
            fail(f"{COMMUNITY_CONFIG_PATH.name}: duplicate channel name {name!r}")
        configured[name] = channel
    return configured


class BuzzCommunityParityTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.doc_text = read_text(INFORMATION_ARCHITECTURE_PATH)
        cls.documented_channels = parse_documented_channels(cls.doc_text)
        cls.launch_decision = parse_launch_decision(cls.doc_text)
        cls.expected_channel_count = parse_expected_channel_count(read_text(LAUNCH_CHECKLIST_PATH))
        cls.configured_channels = load_configured_channels()

    def test_channel_names_match_the_documented_set(self):
        documented_names = [name for name, _ in self.documented_channels]
        documented = set(documented_names)
        configured = set(self.configured_channels)
        self.assertEqual(
            len(documented_names),
            len(documented),
            f"Channel map lists a duplicate channel name in {documented_names!r}",
        )
        self.assertEqual(
            documented,
            configured,
            f"Channel sets differ; documented only: {sorted(documented - configured)}; "
            f"configured only: {sorted(configured - documented)}",
        )

    def test_channel_count_matches_the_documented_totals(self):
        self.assertEqual(
            len(self.configured_channels),
            self.expected_channel_count,
            f"{COMMUNITY_CONFIG_PATH.name} configures {len(self.configured_channels)} channels; "
            f"{LAUNCH_CHECKLIST_PATH.name} expects {self.expected_channel_count}",
        )
        self.assertEqual(
            len(self.documented_channels),
            self.launch_decision["total"],
            f"Channel map lists {len(self.documented_channels)} channels; "
            f"Launch decision states {self.launch_decision['total']}",
        )

    def test_visibility_counts_match_the_launch_decision(self):
        for visibility in ("private", "open"):
            configured_count = sum(
                1
                for channel in self.configured_channels.values()
                if channel.get("visibility") == visibility
            )
            self.assertEqual(
                configured_count,
                self.launch_decision[visibility],
                f"Launch decision states {self.launch_decision[visibility]} {visibility} channels; "
                f"{COMMUNITY_CONFIG_PATH.name} configures {configured_count}",
            )

    def test_documented_access_matches_configured_visibility(self):
        mismatches = []
        for name, access in self.documented_channels:
            expected_visibility = DOCUMENT_ACCESS_TO_CONFIG_VISIBILITY.get(access)
            if expected_visibility is None:
                mismatches.append(f"{name}: unknown documented access {access!r}; extend DOCUMENT_ACCESS_TO_CONFIG_VISIBILITY")
                continue
            actual_visibility = self.configured_channels[name].get("visibility")
            if actual_visibility != expected_visibility:
                mismatches.append(
                    f"{name}: documented {access!r} maps to {expected_visibility!r} "
                    f"but configuration has {actual_visibility!r}"
                )
        self.assertEqual(mismatches, [], "Visibility mismatches between document and configuration")

    def test_every_configured_channel_is_a_stream(self):
        self.assertTrue(
            self.launch_decision["streams_only"],
            "Launch decision no longer states that every channel is a stream; re-derive the type requirement",
        )
        non_streams = sorted(
            name for name, channel in self.configured_channels.items() if channel.get("type") != "stream"
        )
        self.assertEqual(
            non_streams,
            [],
            f"Configuration must set type 'stream' on every channel; non-stream channels: {non_streams}",
        )

    def test_every_channel_has_a_distinct_topic_and_purpose(self):
        problems: list[str] = []
        for field in ("topic", "purpose"):
            seen: dict[str, str] = {}
            for name, channel in sorted(self.configured_channels.items()):
                value = channel.get(field)
                if not isinstance(value, str) or not value.strip():
                    problems.append(f"{name}: missing or empty {field}")
                elif value in seen:
                    problems.append(f"{field} of {name!r} duplicates the {field} of {seen[value]!r}")
                else:
                    seen[value] = name
        self.assertEqual(
            problems,
            [],
            "Channel lifecycle requires a distinct topic and purpose per channel",
        )

    def test_canvas_and_seed_paths_exist_and_are_distinct(self):
        problems: list[str] = []
        for field in ("canvas", "seed"):
            seen: dict[str, str] = {}
            for name, channel in sorted(self.configured_channels.items()):
                relative_path = channel.get(field)
                if not isinstance(relative_path, str) or not relative_path:
                    problems.append(f"{name}: missing or empty {field} path")
                    continue
                if not (REPOSITORY_ROOT / relative_path).is_file():
                    problems.append(f"{name}: {field} path does not exist: {relative_path}")
                if relative_path in seen:
                    problems.append(f"{field} path {relative_path!r} is shared by {seen[relative_path]!r} and {name!r}")
                else:
                    seen[relative_path] = name
        self.assertEqual(
            problems,
            [],
            "Every channel needs its own existing canvas and seed file",
        )

    def test_every_seed_carries_exactly_one_idempotency_marker(self):
        problems: list[str] = []
        for name, channel in sorted(self.configured_channels.items()):
            relative_path = channel.get("seed")
            if not isinstance(relative_path, str) or not relative_path:
                problems.append(f"{name}: missing or empty seed path")
                continue
            path = REPOSITORY_ROOT / relative_path
            if not path.is_file():
                problems.append(f"{name}: seed path does not exist: {relative_path}")
                continue
            marker_count = len(SEED_MARKER_PATTERN.findall(read_text(path)))
            if marker_count != 1:
                problems.append(
                    f"{name}: seed {relative_path} carries {marker_count} practice-seed markers, expected exactly 1"
                )
        self.assertEqual(problems, [], "Every seed needs exactly one practice-seed idempotency marker")


if __name__ == "__main__":
    unittest.main()
