"""Policy tests for the autonomy ladder.

``docs/framework/AUTONOMY_LADDER.md`` states what an agent may do at each
autonomy level, which operations may never run unattended, and where every
agent and cadence operation currently sits. These tests hold that document to
the files it claims to describe:

- every ``autonomy`` value in ``buzz/agents/registry.yaml`` is in the ladder's
  vocabulary, and the ladder's attended vocabulary is exactly the packet
  schema's;
- nothing -- no agent, no mapped operation -- is at A3;
- every permanently ineligible operation is listed and appears in no
  operation's allowed actions;
- every registry agent and every cadence pass, queue, check, and escalation
  appears in the mapping table, at the level its own source records.

The parser fails loudly. A ladder missing a section, or a section missing its
table, raises ``LadderFormatError`` rather than yielding an empty set that
would let every assertion below pass vacuously; ``ParserIsNonVacuous`` proves
that.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LADDER_PATH = REPOSITORY_ROOT / "docs" / "framework" / "AUTONOMY_LADDER.md"
REGISTRY_PATH = REPOSITORY_ROOT / "buzz" / "agents" / "registry.yaml"
PACKET_SCHEMA_PATH = REPOSITORY_ROOT / "docs" / "schemas" / "AGENT_PACKET_SCHEMA.md"
CADENCE_PATH = REPOSITORY_ROOT / "ops" / "cadence.yaml"

LEVELS_SECTION = "Levels"
INELIGIBLE_SECTION = "Permanently ineligible for A3"
ACTIONS_SECTION = "Action vocabulary"
MAPPING_SECTION = "Current level of every agent and cadence operation"
RAISING_SECTION = "Raising a level"

UNATTENDED_LEVEL = "A3"

# The operations the repository has already reserved to a human. Each one must
# appear in the ladder's ineligible table and in no operation's allowed
# actions. Adding a row to that table is allowed; dropping one of these is not.
REQUIRED_INELIGIBLE = (
    "moderation-and-removal",
    "maturity-promotion",
    "publication-and-announcement",
    "merge",
    "owner-identity-and-keys",
    "license-and-governance-change",
    "owner-reserved-decision",
)

# The ineligible section must cite the documents that make these operations
# human-owned, by path, so a reader can check the claim.
REQUIRED_CITATIONS = (
    "DECISIONS.md",
    "NON_GOALS.md",
    "OWNER_GATES.md",
    "community/MODERATION.md",
)

REQUIRED_CLAUSES = (
    "**The agent may.**",
    "**The human must.**",
    "**Evidence required before an operation runs here.**",
    "**Recorded when it runs.**",
)
DEMOTION_CLAUSE_RE = re.compile(r"\*\*Automatic demotion(?: to A\d)?\.\*\*")
CLAUSE_BODY_MINIMUM = 40

LEVEL_ID_RE = re.compile(r"^A\d$")
BACKTICKED_RE = re.compile(r"`([^`]+)`")
TABLE_SEPARATOR_RE = re.compile(r"^:?-{2,}:?$")


class LadderFormatError(AssertionError):
    """The ladder does not have a structure these tests can read."""


def read(path: Path) -> str:
    if not path.is_file():
        raise LadderFormatError(
            f"Missing {path.relative_to(REPOSITORY_ROOT)}. These tests read it directly; "
            "create it before running them."
        )
    return path.read_text(encoding="utf-8")


def sections(text: str) -> dict[str, str]:
    """Return ``{H2 heading: body}`` for a markdown document."""
    found: dict[str, str] = {}
    heading: str | None = None
    body: list[str] = []
    for line in text.split("\n"):
        if line.startswith("## "):
            if heading is not None:
                found[heading] = "\n".join(body)
            heading = line[3:].strip()
            body = []
        else:
            body.append(line)
    if heading is not None:
        found[heading] = "\n".join(body)
    return found


def section_body(text: str, heading: str, source: str) -> str:
    found = sections(text)
    if heading not in found:
        raise LadderFormatError(
            f"{source} has no '## {heading}' section. These tests read that section; "
            "restore the heading exactly, or update the test constant if the "
            "section was deliberately renamed."
        )
    return found[heading]


def table_rows(body: str, heading: str, source: str) -> list[list[str]]:
    """Return the data rows of the first markdown table in ``body``."""
    rows: list[list[str]] = []
    started = False
    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("|"):
            if started:
                break
            continue
        started = True
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(TABLE_SEPARATOR_RE.match(cell) for cell in cells if cell):
            continue
        rows.append(cells)
    if len(rows) < 2:
        raise LadderFormatError(
            f"Section '## {heading}' in {source} has no table with a header and at "
            "least one row. These tests read that table; restore it."
        )
    return rows[1:]


def cell(row: list[str], index: int, heading: str, source: str) -> str:
    if index >= len(row):
        raise LadderFormatError(
            f"A row in '## {heading}' of {source} has {len(row)} columns; column "
            f"{index + 1} is required. Restore the table's columns."
        )
    return row[index]


def parse_levels(text: str, source: str) -> list[dict[str, str]]:
    """Return ``[{level, value, attended}]`` from the Levels table."""
    body = section_body(text, LEVELS_SECTION, source)
    levels: list[dict[str, str]] = []
    for row in table_rows(body, LEVELS_SECTION, source):
        level = cell(row, 0, LEVELS_SECTION, source)
        if not LEVEL_ID_RE.match(level):
            continue
        values = BACKTICKED_RE.findall(cell(row, 1, LEVELS_SECTION, source))
        if len(values) != 1:
            raise LadderFormatError(
                f"Level {level} in '## {LEVELS_SECTION}' of {source} must name exactly "
                "one backticked vocabulary value in its second column."
            )
        levels.append(
            {
                "level": level,
                "value": values[0],
                "attended": cell(row, 2, LEVELS_SECTION, source).strip().lower(),
            }
        )
    if not levels:
        raise LadderFormatError(
            f"'## {LEVELS_SECTION}' in {source} names no level. Rows must start with a "
            "level id such as A0."
        )
    return levels


def parse_ineligible(text: str, source: str) -> list[str]:
    body = section_body(text, INELIGIBLE_SECTION, source)
    ids: list[str] = []
    for row in table_rows(body, INELIGIBLE_SECTION, source):
        found = BACKTICKED_RE.findall(cell(row, 0, INELIGIBLE_SECTION, source))
        if len(found) != 1:
            raise LadderFormatError(
                f"Every row of '## {INELIGIBLE_SECTION}' in {source} must open with one "
                f"backticked operation id; found {found!r}."
            )
        ids.append(found[0])
    return ids


def parse_actions(text: str, source: str) -> dict[str, int]:
    """Return ``{action id: minimum level as an integer}``."""
    body = section_body(text, ACTIONS_SECTION, source)
    actions: dict[str, int] = {}
    for row in table_rows(body, ACTIONS_SECTION, source):
        found = BACKTICKED_RE.findall(cell(row, 0, ACTIONS_SECTION, source))
        minimum = cell(row, 1, ACTIONS_SECTION, source)
        if len(found) != 1 or not LEVEL_ID_RE.match(minimum):
            raise LadderFormatError(
                f"Every row of '## {ACTIONS_SECTION}' in {source} must open with one "
                "backticked action id and name a minimum level such as A1; found "
                f"{found!r} and {minimum!r}."
            )
        actions[found[0]] = int(minimum[1:])
    return actions


def parse_mapping(text: str, source: str) -> list[dict[str, object]]:
    """Return ``[{item, kind, level, actions}]`` from the mapping table."""
    body = section_body(text, MAPPING_SECTION, source)
    mapped: list[dict[str, object]] = []
    for row in table_rows(body, MAPPING_SECTION, source):
        found = BACKTICKED_RE.findall(cell(row, 0, MAPPING_SECTION, source))
        level = cell(row, 2, MAPPING_SECTION, source)
        if len(found) != 1 or not LEVEL_ID_RE.match(level):
            raise LadderFormatError(
                f"Every row of '## {MAPPING_SECTION}' in {source} must open with one "
                "backticked item id and name a level such as A1; found "
                f"{found!r} and {level!r}."
            )
        actions_cell = cell(row, 3, MAPPING_SECTION, source)
        mapped.append(
            {
                "item": found[0],
                "kind": cell(row, 1, MAPPING_SECTION, source),
                "level": level,
                "actions": BACKTICKED_RE.findall(actions_cell),
                "actions_text": actions_cell,
                "raise_evidence": cell(row, 4, MAPPING_SECTION, source),
            }
        )
    return mapped


def parse_packet_autonomy(text: str, source: str) -> list[str]:
    body = section_body(text, "Autonomy levels", source)
    values: list[str] = []
    for row in table_rows(body, "Autonomy levels", source):
        found = BACKTICKED_RE.findall(cell(row, 0, "Autonomy levels", source))
        if len(found) != 1:
            raise LadderFormatError(
                f"Every row of '## Autonomy levels' in {source} must open with one "
                f"backticked autonomy value; found {found!r}."
            )
        values.append(found[0])
    return values


def cadence_operations(config: dict) -> dict[str, str]:
    """Return ``{operation id: kind}`` for everything ops/cadence.yaml names."""
    operations: dict[str, str] = {}
    for kind, key in (("pass", "passes"), ("queue", "queues")):
        for entry in config.get(key) or []:
            if isinstance(entry, dict) and entry.get("id"):
                operations[str(entry["id"])] = kind
    escalations = config.get("escalations") or {}
    if isinstance(escalations, dict) and escalations.get("id"):
        operations[str(escalations["id"])] = "escalation"
    for name in (config.get("checks") or {}):
        operations[str(name)] = "check"
    return operations


LADDER_TEXT = read(LADDER_PATH)
LADDER_SOURCE = "docs/framework/AUTONOMY_LADDER.md"
REGISTRY = yaml.safe_load(read(REGISTRY_PATH))
CADENCE = yaml.safe_load(read(CADENCE_PATH))
PACKET_TEXT = read(PACKET_SCHEMA_PATH)


class AutonomyVocabulary(unittest.TestCase):
    def setUp(self) -> None:
        self.levels = parse_levels(LADDER_TEXT, LADDER_SOURCE)
        self.attended = [entry["value"] for entry in self.levels if entry["attended"] == "yes"]
        self.unattended = [entry for entry in self.levels if entry["attended"] != "yes"]

    def test_registry_autonomy_values_are_in_the_ladder_vocabulary(self) -> None:
        vocabulary = {entry["value"] for entry in self.levels}
        for agent in REGISTRY["agents"]:
            with self.subTest(agent=agent["id"]):
                self.assertIn(
                    agent["autonomy"],
                    vocabulary,
                    f"buzz/agents/registry.yaml gives {agent['id']} autonomy "
                    f"'{agent['autonomy']}', which the ladder does not define. Add the "
                    f"level to {LADDER_SOURCE} or correct the registry value.",
                )
                self.assertIn(
                    agent["autonomy"],
                    self.attended,
                    f"Agent {agent['id']} declares '{agent['autonomy']}', which the ladder "
                    "records as unattended. Every agent operates at an attended level.",
                )

    def test_ladder_attended_vocabulary_matches_the_packet_schema(self) -> None:
        packet_values = parse_packet_autonomy(PACKET_TEXT, "docs/schemas/AGENT_PACKET_SCHEMA.md")
        self.assertEqual(
            sorted(self.attended),
            sorted(packet_values),
            "The ladder's attended levels and the packet schema's autonomy values must "
            "be the same vocabulary. Change both files together.",
        )

    def test_the_unattended_level_is_declared_and_unused(self) -> None:
        self.assertEqual(
            [entry["level"] for entry in self.unattended],
            [UNATTENDED_LEVEL],
            f"The ladder must declare exactly one unattended level, {UNATTENDED_LEVEL}.",
        )
        unattended_value = self.unattended[0]["value"]
        self.assertNotIn(
            unattended_value,
            parse_packet_autonomy(PACKET_TEXT, "docs/schemas/AGENT_PACKET_SCHEMA.md"),
            "The unattended level must not be a packet autonomy value: no packet may "
            "record an unattended run.",
        )
        for agent in REGISTRY["agents"]:
            self.assertNotEqual(
                agent["autonomy"],
                unattended_value,
                f"Agent {agent['id']} declares the unattended level. Raising an agent to "
                f"{UNATTENDED_LEVEL} is a recorded human governance decision, not a "
                "registry edit.",
            )


class UnattendedOperations(unittest.TestCase):
    def setUp(self) -> None:
        self.mapping = parse_mapping(LADDER_TEXT, LADDER_SOURCE)
        self.ineligible = parse_ineligible(LADDER_TEXT, LADDER_SOURCE)

    def test_nothing_is_mapped_to_the_unattended_level(self) -> None:
        at_a3 = [entry["item"] for entry in self.mapping if entry["level"] == UNATTENDED_LEVEL]
        self.assertEqual(
            at_a3,
            [],
            f"{LADDER_SOURCE} maps {at_a3} to {UNATTENDED_LEVEL}. Nothing in this "
            "repository is unattended; moving an operation there is a human decision "
            "recorded through the governance path.",
        )

    def test_every_reserved_operation_is_listed_as_permanently_ineligible(self) -> None:
        for operation in REQUIRED_INELIGIBLE:
            with self.subTest(operation=operation):
                self.assertIn(
                    operation,
                    self.ineligible,
                    f"'{operation}' must stay in the permanently ineligible table of "
                    f"{LADDER_SOURCE}. It is reserved to a human by a locked decision.",
                )

    def test_the_ineligible_section_cites_the_decisions_by_path(self) -> None:
        body = section_body(LADDER_TEXT, INELIGIBLE_SECTION, LADDER_SOURCE)
        for citation in REQUIRED_CITATIONS:
            with self.subTest(citation=citation):
                self.assertIn(
                    citation,
                    body,
                    f"'## {INELIGIBLE_SECTION}' must cite {citation} by path so a reader "
                    "can check which decision reserves the operation.",
                )

    def test_no_operation_is_allowed_to_perform_an_ineligible_operation(self) -> None:
        for entry in self.mapping:
            for operation in self.ineligible:
                with self.subTest(item=entry["item"], operation=operation):
                    self.assertNotIn(
                        operation,
                        entry["actions_text"],
                        f"{entry['item']} lists '{operation}' among its allowed actions. "
                        "That operation may never be performed by an agent at any level.",
                    )


class MappingCoverage(unittest.TestCase):
    def setUp(self) -> None:
        self.levels = parse_levels(LADDER_TEXT, LADDER_SOURCE)
        self.mapping = parse_mapping(LADDER_TEXT, LADDER_SOURCE)
        self.actions = parse_actions(LADDER_TEXT, LADDER_SOURCE)
        self.by_item = {entry["item"]: entry for entry in self.mapping}
        self.value_to_level = {entry["value"]: entry["level"] for entry in self.levels}

    def test_item_ids_are_unique(self) -> None:
        self.assertEqual(
            len(self.by_item),
            len(self.mapping),
            "Two rows of the mapping table share one item id.",
        )

    def test_every_registry_agent_appears_at_its_declared_level(self) -> None:
        for agent in REGISTRY["agents"]:
            with self.subTest(agent=agent["id"]):
                entry = self.by_item.get(agent["id"])
                self.assertIsNotNone(
                    entry,
                    f"Agent '{agent['id']}' is in buzz/agents/registry.yaml but has no row "
                    f"in the mapping table of {LADDER_SOURCE}. Add the row.",
                )
                self.assertEqual(entry["kind"], "agent")
                self.assertEqual(
                    entry["level"],
                    self.value_to_level[agent["autonomy"]],
                    f"The registry gives '{agent['id']}' autonomy "
                    f"'{agent['autonomy']}' but the ladder maps it to "
                    f"{entry['level']}. The two files must agree.",
                )

    def test_the_mapping_lists_no_agent_the_registry_does_not(self) -> None:
        registered = {agent["id"] for agent in REGISTRY["agents"]}
        mapped = {entry["item"] for entry in self.mapping if entry["kind"] == "agent"}
        self.assertEqual(
            mapped,
            registered,
            "The mapping table's agent rows and buzz/agents/registry.yaml must name the "
            "same agents.",
        )

    def test_every_cadence_operation_appears_with_its_kind(self) -> None:
        operations = cadence_operations(CADENCE)
        self.assertTrue(operations, "ops/cadence.yaml named no operation to map.")
        for operation, kind in sorted(operations.items()):
            with self.subTest(operation=operation):
                entry = self.by_item.get(operation)
                self.assertIsNotNone(
                    entry,
                    f"ops/cadence.yaml defines '{operation}' but the mapping table in "
                    f"{LADDER_SOURCE} has no row for it. Add the row with its level and "
                    "the evidence that would raise it.",
                )
                self.assertEqual(
                    entry["kind"],
                    kind,
                    f"'{operation}' is a {kind} in ops/cadence.yaml but the ladder calls "
                    f"it a {entry['kind']}.",
                )

    def test_the_mapping_lists_no_operation_the_cadence_does_not(self) -> None:
        operations = set(cadence_operations(CADENCE))
        mapped = {entry["item"] for entry in self.mapping if entry["kind"] != "agent"}
        self.assertEqual(
            mapped,
            operations,
            "The mapping table's non-agent rows and ops/cadence.yaml must name the same "
            "operations.",
        )

    def test_allowed_actions_are_defined_and_within_the_row_level(self) -> None:
        for entry in self.mapping:
            self.assertTrue(
                entry["actions"],
                f"{entry['item']} lists no allowed action. Every row states what the "
                "operation may do.",
            )
            row_level = int(entry["level"][1:])
            for action in entry["actions"]:
                with self.subTest(item=entry["item"], action=action):
                    self.assertIn(
                        action,
                        self.actions,
                        f"'{action}' is not defined in '## {ACTIONS_SECTION}'. Define it "
                        "there or correct the row.",
                    )
                    self.assertLessEqual(
                        self.actions[action],
                        row_level,
                        f"{entry['item']} is at {entry['level']} but is allowed "
                        f"'{action}', which needs A{self.actions[action]}.",
                    )

    def test_every_row_states_the_evidence_that_would_raise_it(self) -> None:
        for entry in self.mapping:
            with self.subTest(item=entry["item"]):
                self.assertGreaterEqual(
                    len(entry["raise_evidence"]),
                    20,
                    f"{entry['item']} does not state what evidence would raise its level.",
                )


class LevelDefinitions(unittest.TestCase):
    def setUp(self) -> None:
        self.levels = parse_levels(LADDER_TEXT, LADDER_SOURCE)
        self.found = sections(LADDER_TEXT)

    def test_every_level_has_its_own_section(self) -> None:
        for entry in self.levels:
            heading = f"{entry['level']} {entry['value']}"
            with self.subTest(level=heading):
                self.assertIn(
                    heading,
                    self.found,
                    f"{LADDER_SOURCE} declares level {entry['level']} but has no "
                    f"'## {heading}' section defining it.",
                )

    def test_every_level_states_permissions_evidence_record_and_demotion(self) -> None:
        for entry in self.levels:
            heading = f"{entry['level']} {entry['value']}"
            body = self.found.get(heading, "")
            for clause in REQUIRED_CLAUSES:
                with self.subTest(level=heading, clause=clause):
                    self.assertIn(
                        clause,
                        body,
                        f"'## {heading}' is missing the clause '{clause}'. Each level "
                        "states what the agent may do, what the human must do, the "
                        "evidence required, and what is recorded.",
                    )
                    after = body.split(clause, 1)[1].split("\n\n", 1)[0]
                    self.assertGreaterEqual(
                        len(after.strip()),
                        CLAUSE_BODY_MINIMUM,
                        f"'{clause}' in '## {heading}' has no substantive text after it.",
                    )
            with self.subTest(level=heading, clause="demotion"):
                match = DEMOTION_CLAUSE_RE.search(body)
                self.assertIsNotNone(
                    match,
                    f"'## {heading}' states no automatic demotion. Demotion criteria must "
                    "be observable and written down.",
                )
                after = body[match.end():].split("\n\n", 1)[0]
                self.assertGreaterEqual(
                    len(after.strip()),
                    CLAUSE_BODY_MINIMUM,
                    f"The demotion clause in '## {heading}' names no trigger.",
                )

    def test_the_raising_section_exists_and_names_its_evidence_sets(self) -> None:
        body = section_body(LADDER_TEXT, RAISING_SECTION, LADDER_SOURCE)
        for code in ("`R1`", "`R2`", "`R3`", "`R4`"):
            with self.subTest(code=code):
                self.assertIn(
                    code,
                    body,
                    f"'## {RAISING_SECTION}' must define {code}; the mapping table cites "
                    "these evidence sets.",
                )


class ParserIsNonVacuous(unittest.TestCase):
    """The parser must find real content and refuse a ladder that lost a section."""

    def test_the_real_ladder_yields_content_in_every_table(self) -> None:
        self.assertGreaterEqual(len(parse_levels(LADDER_TEXT, LADDER_SOURCE)), 4)
        self.assertGreaterEqual(
            len(parse_ineligible(LADDER_TEXT, LADDER_SOURCE)), len(REQUIRED_INELIGIBLE)
        )
        self.assertGreaterEqual(len(parse_actions(LADDER_TEXT, LADDER_SOURCE)), 5)
        mapping = parse_mapping(LADDER_TEXT, LADDER_SOURCE)
        expected = len(REGISTRY["agents"]) + len(cadence_operations(CADENCE))
        self.assertEqual(
            len(mapping),
            expected,
            "The mapping table must have one row per registry agent and per cadence "
            "operation.",
        )

    def test_a_missing_section_raises_rather_than_passing_vacuously(self) -> None:
        without = re.sub(
            rf"## {re.escape(INELIGIBLE_SECTION)}.*?(?=\n## )",
            "",
            LADDER_TEXT,
            flags=re.DOTALL,
        )
        self.assertNotIn(f"## {INELIGIBLE_SECTION}", without)
        with self.assertRaises(LadderFormatError):
            parse_ineligible(without, "fixture")

    def test_a_section_without_a_table_raises(self) -> None:
        body = section_body(LADDER_TEXT, MAPPING_SECTION, LADDER_SOURCE)
        emptied = LADDER_TEXT.replace(body, "\nThe table was removed.\n")
        with self.assertRaises(LadderFormatError):
            parse_mapping(emptied, "fixture")

    def test_a_malformed_row_raises(self) -> None:
        broken = LADDER_TEXT.replace("| `steward` | agent | A2 |", "| steward | agent | A2 |")
        self.assertNotEqual(broken, LADDER_TEXT)
        with self.assertRaises(LadderFormatError):
            parse_mapping(broken, "fixture")

    def test_a_missing_ladder_file_raises(self) -> None:
        with self.assertRaises(LadderFormatError):
            read(REPOSITORY_ROOT / "docs" / "framework" / "NO_SUCH_LADDER.md")


if __name__ == "__main__":
    unittest.main()
