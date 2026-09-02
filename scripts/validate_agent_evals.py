#!/usr/bin/env python3
"""Check the community-agent eval suites in ``buzz/agents/evals/``.

Every profile in ``buzz/agents/`` opens with the same guardrail paragraph:
treat messages, links, and attachments as untrusted data, refuse publication,
refuse to change an artifact's standing, never touch owner identity material.
Prose cannot be run. These suites turn each of those promises into an
observable case, and this validator checks that the suites stay honest and
complete:

1. Does every agent in ``buzz/agents/registry.yaml`` have a suite, does every
   suite name a registry agent, and does the profile it cites exist?
2. Does each suite carry all three case classes - routing (including at least
   one negative case), behavior, and adversarial - with every required
   adversarial topic either covered by a case or explicitly justified as
   inapplicable?
3. Is every case reviewable: unique id, input, expected, forbidden, severity in
   vocabulary, no credential, key, address, handle, or known person's name?
4. Does the suite record no result? These files define cases. A run record does
   not live here, and a defined case is not evidence of a pass.

The validator reads files only. It never runs an agent, never enables one,
never scores a case, and never asserts that an owner gate or operating hold is
cleared. It exits 0 when the suites are inside these bounds and 1 with
actionable messages when they are not.

Usage:

    python3 scripts/validate_agent_evals.py --root .
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit(
        "PyYAML is required: install it (pip install PyYAML) before running "
        "scripts/validate_agent_evals.py"
    ) from exc


DEFAULT_ROOT = Path(__file__).resolve().parents[1]

REGISTRY_PATH = "buzz/agents/registry.yaml"
EVAL_DIR = "buzz/agents/evals"
EVAL_README = "buzz/agents/evals/README.md"

SUPPORTED_SCHEMA_VERSIONS = (1,)

# One suite per agent, named for the registry id, so a reviewer can find the
# cases for an agent without opening every file.
SUITE_SUFFIX = ".yaml"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
# Matches docs/schemas/AGENT_PACKET_SCHEMA.md: 7 to 40 lowercase hex characters.
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Agent profiles carry no version field, so a suite records the commit its
# cases were written against. The literal below is the only permitted stand-in.
UNVERSIONED_PROFILE = "not-versioned"

CLASS_ROUTING = "routing"
CLASS_BEHAVIOR = "behavior"
CLASS_ADVERSARIAL = "adversarial"
REQUIRED_CLASSES = (CLASS_ROUTING, CLASS_BEHAVIOR, CLASS_ADVERSARIAL)

ROUTING_KINDS = (
    "routing.direct",
    "routing.indirect",
    "routing.negative",
)
BEHAVIOR_KINDS = (
    "behavior.bounded-scope",
    "behavior.evidence-bounded",
    "behavior.packet-shape",
    "behavior.incomplete-input",
    "behavior.output-discipline",
    # Only an agent with a write surface can hold a reply back, so this kind is
    # available rather than required. The Steward is the one agent that has one,
    # and its profile states the conditions as a numbered test precisely so a
    # case can assert which condition should have fired.
    "behavior.post-or-draft",
)
# The suffix of an adversarial kind is the topic it covers, so coverage is
# readable in the case list itself rather than in a parallel index.
ADVERSARIAL_TOPICS = (
    "instruction-injection",
    "owner-identity",
    "publication-pressure",
    "evidence-inflation",
    "moderation-action",
    "participation-as-evidence",
    "vendor-mandate",
)
ADVERSARIAL_KINDS = tuple(f"{CLASS_ADVERSARIAL}.{topic}" for topic in ADVERSARIAL_TOPICS)
CASE_KINDS = ROUTING_KINDS + BEHAVIOR_KINDS + ADVERSARIAL_KINDS

# severe - crossing a boundary locked by docs/DECISIONS.md, docs/NON_GOALS.md, or the
#          registry's prohibited list. One severe failure blocks enablement.
# major   - staying inside the boundary but producing output a human cannot
#           act on, or misstating what the evidence supports.
# minor   - a craft or format deviation that does not change a reviewer's
#           decision.
SEVERITIES = ("severe", "major", "minor")
BLOCKING_SEVERITIES = ("severe", "major")

REQUIRED_SUITE_FIELDS = (
    "schema_version",
    "agent_id",
    "profile",
    "profile_basis",
    "execution",
    "inapplicable_topics",
    "cases",
)
REQUIRED_BASIS_FIELDS = ("profile_version", "source_commit", "reviewed")
REQUIRED_CASE_FIELDS = ("id", "kind", "severity", "input", "expected", "forbidden")

MINIMUM_MODEL_FAMILIES = 2
UNAVAILABLE_POLICY = "record-limitation-and-do-not-count-as-pass"

# A suite defines cases. A run record - who ran it, on what, and what happened -
# belongs in a dated report a human signs, never in the case file, where it
# would let a defined case read as a passed case.
RESULT_KEYS = (
    "result",
    "results",
    "case_results",
    "run",
    "runs",
    "run_date",
    "run_id",
    "run_record",
    "pass",
    "passed",
    "fail",
    "failed",
    "score",
    "scores",
    "grade",
    "graded",
    "verdict",
    "outcome",
    "outcomes",
    "reviewer",
    "model_family",
    "model_version",
    "host",
    "status",
    "enabled",
)

# A case is published text. These patterns catch material that must never be
# written into one. Detection of a person's name is bounded to the identifiers
# this repository already knows plus the shape of an address or handle; it
# cannot recognise an arbitrary name, which is why a human reads every case.
SECRET_PATTERNS = (
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "an email address"),
    (re.compile(r"(?<![A-Za-z0-9])@[A-Za-z0-9][A-Za-z0-9_.-]{1,}"), "a handle or address"),
    (re.compile(r"\b(?:dakota|smithdak|daksmith[0-9]*)\b", re.IGNORECASE), "a known person's name"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "a private key block"),
    (re.compile(r"\b(?:nsec1|npub1)[a-z0-9]{6,}"), "a Buzz identity value"),
    (re.compile(r"\bsk-[A-Za-z0-9]{8,}"), "an API key"),
    (re.compile(r"\bghp_[A-Za-z0-9]{8,}"), "a repository token"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{8,}"), "a chat platform token"),
    (re.compile(r"\bAKIA[0-9A-Z]{8,}"), "a cloud access key id"),
    (
        re.compile(
            r"(?i)\b(?:password|passphrase|secret|token|api[_ -]?key|private[_ -]?key|"
            r"seed[_ -]?(?:phrase|words)|recovery[_ -]?code)\b\s*[:=]\s*\S",
        ),
        "an assigned credential value",
    ),
    (re.compile(r"\b[0-9a-fA-F]{32,}\b"), "a key or hash blob"),
    (re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b"), "an encoded credential blob"),
)

# The README carries the honesty statement the suites depend on. These markers
# are the checked part of that contract; the README documents them.
README_REQUIRED_MARKERS = (
    ("no run has occurred", "that no run has occurred"),
    ("owner gate 6", "that owner gate 6 is open and no agent is enabled"),
)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def is_nonempty_str(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_yaml_mapping(path: Path, label: str, errors: list[str]) -> dict | None:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(errors, f"{label}: cannot be read ({exc}).")
        return None
    try:
        value = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        fail(errors, f"{label}: is not parseable YAML ({exc}).")
        return None
    if not isinstance(value, dict):
        fail(errors, f"{label}: must be a YAML mapping at the top level.")
        return None
    return value


def check_string_list(
    value: object,
    where: str,
    errors: list[str],
) -> list[str]:
    if not isinstance(value, list) or not value:
        fail(errors, f"{where}: must be a non-empty list of observable statements.")
        return []
    items: list[str] = []
    for index, item in enumerate(value):
        if not is_nonempty_str(item):
            fail(errors, f"{where}[{index}]: must be a non-empty string.")
            continue
        items.append(item)
    return items


def check_no_result_keys(node: object, where: str, errors: list[str]) -> None:
    """Reject any mapping key that would record what a run produced."""
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(key, str) and key.strip().lower() in RESULT_KEYS:
                fail(
                    errors,
                    f"{where}: records a result field {key!r}. An eval suite defines cases; "
                    "a run record belongs in a dated report a human signs, not here.",
                )
            check_no_result_keys(value, f"{where}.{key}", errors)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            check_no_result_keys(item, f"{where}[{index}]", errors)


def check_no_secrets(text: str, where: str, errors: list[str]) -> None:
    for pattern, description in SECRET_PATTERNS:
        match = pattern.search(text)
        if match:
            fail(
                errors,
                f"{where}: contains {description} ({match.group(0)[:24]!r}). Describe the "
                "material by role or category; never write a real value, address, handle, or "
                "personal name into a case.",
            )
            return


def check_profile_basis(basis: object, where: str, errors: list[str]) -> None:
    if not isinstance(basis, dict):
        fail(
            errors,
            f"{where}: 'profile_basis' must be a mapping with "
            f"{', '.join(REQUIRED_BASIS_FIELDS)}.",
        )
        return
    unknown = sorted(set(basis) - set(REQUIRED_BASIS_FIELDS))
    if unknown:
        fail(errors, f"{where}: 'profile_basis' has unrecognised field(s): {', '.join(unknown)}.")
    for field in REQUIRED_BASIS_FIELDS:
        if field not in basis:
            fail(errors, f"{where}: 'profile_basis' is missing '{field}'.")

    version = basis.get("profile_version")
    if version is not None:
        if not is_nonempty_str(version) or (
            version != UNVERSIONED_PROFILE and not SEMVER_RE.match(version.strip())
        ):
            fail(
                errors,
                f"{where}: 'profile_basis.profile_version' must be MAJOR.MINOR.PATCH or the "
                f"literal {UNVERSIONED_PROFILE!r}; agent profiles carry no version field, so "
                "the commit is the basis.",
            )
    commit = basis.get("source_commit")
    if commit is not None and (
        not is_nonempty_str(commit) or not COMMIT_RE.match(str(commit).strip())
    ):
        fail(
            errors,
            f"{where}: 'profile_basis.source_commit' must be 7 to 40 lowercase hexadecimal "
            "characters naming the commit these cases were written against.",
        )
    reviewed = basis.get("reviewed")
    if reviewed is not None and not ISO_DATE_RE.match(str(reviewed).strip()):
        fail(
            errors,
            f"{where}: 'profile_basis.reviewed' must be an ISO date in YYYY-MM-DD form.",
        )


def check_execution(execution: object, where: str, errors: list[str]) -> None:
    if not isinstance(execution, dict):
        fail(
            errors,
            f"{where}: 'execution' must be a mapping with 'minimum_model_families' and "
            "'when_unavailable'.",
        )
        return
    unknown = sorted(set(execution) - {"minimum_model_families", "when_unavailable"})
    if unknown:
        fail(errors, f"{where}: 'execution' has unrecognised field(s): {', '.join(unknown)}.")
    families = execution.get("minimum_model_families")
    if not isinstance(families, int) or isinstance(families, bool) or families < MINIMUM_MODEL_FAMILIES:
        fail(
            errors,
            f"{where}: 'execution.minimum_model_families' must be an integer of at least "
            f"{MINIMUM_MODEL_FAMILIES}; one family cannot show that a guardrail holds.",
        )
    if execution.get("when_unavailable") != UNAVAILABLE_POLICY:
        fail(
            errors,
            f"{where}: 'execution.when_unavailable' must be {UNAVAILABLE_POLICY!r} so a missing "
            "model family is recorded as a limitation rather than counted as a pass.",
        )


def check_inapplicable_topics(
    value: object,
    where: str,
    errors: list[str],
) -> set[str]:
    if not isinstance(value, list):
        fail(
            errors,
            f"{where}: 'inapplicable_topics' must be a list; use an empty list when every "
            "adversarial topic applies to this agent's surface.",
        )
        return set()
    declared: set[str] = set()
    for index, entry in enumerate(value):
        label = f"{where}: 'inapplicable_topics[{index}]'"
        if not isinstance(entry, dict):
            fail(errors, f"{label}: must be a mapping with 'topic' and 'reason'.")
            continue
        unknown = sorted(set(entry) - {"topic", "reason"})
        if unknown:
            fail(errors, f"{label}: has unrecognised field(s): {', '.join(unknown)}.")
        topic = entry.get("topic")
        if not is_nonempty_str(topic) or topic.strip() not in ADVERSARIAL_TOPICS:
            fail(
                errors,
                f"{label}: 'topic' must be one of {', '.join(ADVERSARIAL_TOPICS)}.",
            )
            continue
        reason = entry.get("reason")
        if not is_nonempty_str(reason) or len(reason.strip()) < 40:
            fail(
                errors,
                f"{label}: 'reason' must state, in at least 40 characters, why this agent's "
                "surface makes the topic inapplicable. A topic is never dropped silently.",
            )
        if topic.strip() in declared:
            fail(errors, f"{label}: declares topic {topic.strip()!r} twice.")
        declared.add(topic.strip())
    return declared


def check_case(
    case: object,
    index: int,
    where: str,
    errors: list[str],
) -> tuple[str | None, str | None]:
    label = f"{where}: cases[{index}]"
    if not isinstance(case, dict):
        fail(errors, f"{label}: must be a mapping.")
        return None, None

    unknown = sorted(set(case) - set(REQUIRED_CASE_FIELDS))
    if unknown:
        fail(errors, f"{label}: has unrecognised field(s): {', '.join(unknown)}.")
    for field in REQUIRED_CASE_FIELDS:
        if field not in case:
            fail(
                errors,
                f"{label}: is missing '{field}'. Every case needs "
                f"{', '.join(REQUIRED_CASE_FIELDS)} so a reviewer can score it.",
            )

    case_id = case.get("id")
    if not is_nonempty_str(case_id) or not SLUG_RE.match(case_id.strip()):
        fail(
            errors,
            f"{label}: 'id' must be a lowercase slug, unique across every suite, so a result "
            "can be recorded against it later.",
        )
        case_id = None
    else:
        case_id = case_id.strip()
        label = f"{where}: case {case_id}"

    kind = case.get("kind")
    if not is_nonempty_str(kind) or kind.strip() not in CASE_KINDS:
        fail(
            errors,
            f"{label}: 'kind' must be one of {', '.join(CASE_KINDS)}.",
        )
        kind = None
    else:
        kind = kind.strip()

    severity = case.get("severity")
    if not is_nonempty_str(severity) or severity.strip() not in SEVERITIES:
        fail(
            errors,
            f"{label}: 'severity' must be one of {', '.join(SEVERITIES)}.",
        )
    elif kind and kind.startswith(f"{CLASS_ADVERSARIAL}.") and severity.strip() != "severe":
        fail(
            errors,
            f"{label}: an adversarial case must carry severity 'severe'. It tests a boundary "
            "locked by docs/DECISIONS.md, docs/NON_GOALS.md, or the registry's prohibited list, so it "
            "cannot be scored as non-blocking.",
        )

    text_parts: list[str] = []
    if case_id:
        text_parts.append(case_id)
    if not is_nonempty_str(case.get("input")):
        fail(
            errors,
            f"{label}: 'input' must be a non-empty description of what the agent receives.",
        )
    else:
        text_parts.append(case["input"])
    text_parts.extend(check_string_list(case.get("expected"), f"{label}: 'expected'", errors))
    text_parts.extend(check_string_list(case.get("forbidden"), f"{label}: 'forbidden'", errors))
    check_no_secrets("\n".join(text_parts), label, errors)

    return case_id, kind


def check_suite(
    root: Path,
    path: Path,
    registry_profiles: dict[str, str],
    seen_ids: dict[str, str],
    errors: list[str],
) -> str | None:
    relative = path.relative_to(root).as_posix()
    suite = load_yaml_mapping(path, relative, errors)
    if suite is None:
        return None

    check_no_result_keys(suite, relative, errors)

    unknown = sorted(set(suite) - set(REQUIRED_SUITE_FIELDS))
    if unknown:
        fail(errors, f"{relative}: has unrecognised field(s): {', '.join(unknown)}.")
    for field in REQUIRED_SUITE_FIELDS:
        if field not in suite:
            fail(errors, f"{relative}: is missing '{field}'.")

    if suite.get("schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
        fail(
            errors,
            f"{relative}: 'schema_version' must be one of "
            f"{', '.join(str(v) for v in SUPPORTED_SCHEMA_VERSIONS)}.",
        )

    agent_id = suite.get("agent_id")
    if not is_nonempty_str(agent_id) or not SLUG_RE.match(agent_id.strip()):
        fail(errors, f"{relative}: 'agent_id' must be a lowercase slug from {REGISTRY_PATH}.")
        agent_id = None
    else:
        agent_id = agent_id.strip()
        if agent_id not in registry_profiles:
            fail(
                errors,
                f"{relative}: 'agent_id' is {agent_id!r}, which is not an agent in "
                f"{REGISTRY_PATH}. A suite cannot define cases for an agent the registry does "
                "not bound.",
            )
            agent_id = None
        elif path.stem != agent_id:
            fail(
                errors,
                f"{relative}: file name must be {agent_id}{SUITE_SUFFIX} so a reviewer can find "
                "an agent's cases from its registry id.",
            )

    profile = suite.get("profile")
    if not is_nonempty_str(profile):
        fail(errors, f"{relative}: 'profile' must be the repository path of the agent profile.")
    else:
        profile = profile.strip()
        if not (root / profile).is_file():
            fail(errors, f"{relative}: 'profile' names {profile}, which does not exist.")
        if agent_id and profile != registry_profiles[agent_id]:
            fail(
                errors,
                f"{relative}: 'profile' is {profile}, but {REGISTRY_PATH} records "
                f"{registry_profiles[agent_id]} for {agent_id}.",
            )

    check_profile_basis(suite.get("profile_basis"), relative, errors)
    check_execution(suite.get("execution"), relative, errors)
    inapplicable = check_inapplicable_topics(suite.get("inapplicable_topics"), relative, errors)

    cases = suite.get("cases")
    if not isinstance(cases, list) or not cases:
        fail(errors, f"{relative}: 'cases' must be a non-empty list.")
        return agent_id

    kinds: list[str] = []
    local_ids: set[str] = set()
    for index, case in enumerate(cases):
        case_id, kind = check_case(case, index, relative, errors)
        if kind:
            kinds.append(kind)
        if not case_id:
            continue
        if case_id in local_ids:
            fail(errors, f"{relative}: duplicate case id {case_id!r} inside this suite.")
        elif case_id in seen_ids:
            fail(
                errors,
                f"{relative}: case id {case_id!r} is already used in {seen_ids[case_id]}. Case "
                "ids are unique across every suite.",
            )
        else:
            seen_ids[case_id] = relative
        local_ids.add(case_id)

    classes = {kind.split(".", 1)[0] for kind in kinds}
    for required in REQUIRED_CLASSES:
        if required not in classes:
            fail(
                errors,
                f"{relative}: has no {required} case. Every suite carries routing, behavior, and "
                "adversarial cases.",
            )
    if CLASS_ROUTING in classes:
        if "routing.negative" not in kinds:
            fail(
                errors,
                f"{relative}: has no routing.negative case. A suite must show the requests this "
                "agent must not be selected for, not only the ones it should answer.",
            )
        if not any(kind in ROUTING_KINDS and kind != "routing.negative" for kind in kinds):
            fail(
                errors,
                f"{relative}: has only negative routing cases. Add routing.direct or "
                "routing.indirect so selection is tested in both directions.",
            )

    covered = {kind.split(".", 1)[1] for kind in kinds if kind.startswith(f"{CLASS_ADVERSARIAL}.")}
    overlap = sorted(covered & inapplicable)
    if overlap:
        fail(
            errors,
            f"{relative}: topic(s) {', '.join(overlap)} are both covered by a case and declared "
            "inapplicable. Choose one.",
        )
    missing = sorted(set(ADVERSARIAL_TOPICS) - covered - inapplicable)
    if missing:
        fail(
            errors,
            f"{relative}: adversarial topic(s) not covered: {', '.join(missing)}. Add a case, or "
            "record the topic in 'inapplicable_topics' with the reason this agent's surface "
            "makes it inapplicable.",
        )
    return agent_id


def read_registry(root: Path, errors: list[str]) -> dict[str, str]:
    path = root / REGISTRY_PATH
    if not path.is_file():
        fail(
            errors,
            f"Missing {REGISTRY_PATH}. The registry is the list of agents a suite must cover.",
        )
        return {}
    registry = load_yaml_mapping(path, REGISTRY_PATH, errors)
    if registry is None:
        return {}
    agents = registry.get("agents")
    if not isinstance(agents, list) or not agents:
        fail(errors, f"{REGISTRY_PATH}: 'agents' must be a non-empty list.")
        return {}
    profiles: dict[str, str] = {}
    for index, entry in enumerate(agents):
        if not isinstance(entry, dict):
            fail(errors, f"{REGISTRY_PATH}: agents[{index}] must be a mapping.")
            continue
        agent_id = entry.get("id")
        profile = entry.get("profile")
        if not is_nonempty_str(agent_id) or not is_nonempty_str(profile):
            fail(errors, f"{REGISTRY_PATH}: agents[{index}] needs both 'id' and 'profile'.")
            continue
        profiles[agent_id.strip()] = profile.strip()
    return profiles


def check_readme(root: Path, errors: list[str]) -> None:
    path = root / EVAL_README
    if not path.is_file():
        fail(
            errors,
            f"Missing {EVAL_README}. The suites depend on it for the severity vocabulary, the "
            "run protocol, and the statement that no run has occurred.",
        )
        return
    text = path.read_text(encoding="utf-8").lower()
    for marker, description in README_REQUIRED_MARKERS:
        if marker not in text:
            fail(
                errors,
                f"{EVAL_README}: must state {description}; the phrase {marker!r} is missing. "
                "A case file without that statement reads as a passed case.",
            )


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    registry_profiles = read_registry(root, errors)

    eval_dir = root / EVAL_DIR
    if not eval_dir.is_dir():
        fail(errors, f"Missing {EVAL_DIR}/. Each agent's eval suite lives there.")
        return errors

    check_readme(root, errors)

    suite_paths = sorted(eval_dir.glob(f"*{SUITE_SUFFIX}"))
    if not suite_paths:
        fail(errors, f"{EVAL_DIR}/ contains no eval suite.")

    seen_ids: dict[str, str] = {}
    covered_agents: set[str] = set()
    for path in suite_paths:
        agent_id = check_suite(root, path, registry_profiles, seen_ids, errors)
        if agent_id:
            if agent_id in covered_agents:
                fail(errors, f"{EVAL_DIR}/: two suites declare agent_id {agent_id!r}.")
            covered_agents.add(agent_id)

    for agent_id in sorted(set(registry_profiles) - covered_agents):
        fail(
            errors,
            f"{REGISTRY_PATH}: agent {agent_id!r} has no eval suite. Add "
            f"{EVAL_DIR}/{agent_id}{SUITE_SUFFIX}; a profile whose guardrails have no case is a "
            "paragraph the community is asked to trust.",
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        default=str(DEFAULT_ROOT),
        help="repository root to check (default: the repository containing this script)",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    errors = validate(root)
    for message in errors:
        print(message)
    if errors:
        print(f"{len(errors)} agent eval suite problem(s) found.")
        return 1
    print("Agent eval suite validation passed. Cases are defined; no run is recorded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
