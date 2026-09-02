#!/usr/bin/env python3
"""Check the community-agent registry against the profiles it claims to describe.

``buzz/agents/registry.yaml`` is the machine-readable bound on every agent in
``buzz/agents/``: identity requirement, channel scope, autonomy, prohibited
actions, escalation route, enablement prerequisites, and enablement status.
This validator answers three questions a prose profile cannot:

1. Does every profile have exactly one registry entry, and every entry a
   profile that exists?
2. Is the declared channel scope real and least-privilege - do the channels
   exist in ``buzz/community.json``, and is any write into a private channel or
   into ``announcements`` covered by an explicit human-approval record?
3. Do the locked non-negotiables still appear in every ``prohibited`` list, is
   autonomy inside the attended vocabulary, is the escalation owner a role
   rather than a person, and is ``status`` consistent with owner gate 6 in
   ``release/OWNER_REVIEW.md``?

The validator reads files only. It never enables an agent, never changes a
status, and never asserts that a gate or hold is cleared. It exits 0 when the
registry is inside its declared bounds and 1 with actionable messages when it
is not; an anchor it cannot find is a failure, not a pass.

Usage:

    python3 scripts/validate_agents.py --root .
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit(
        "PyYAML is required: install it (pip install PyYAML) before running "
        "scripts/validate_agents.py"
    ) from exc


DEFAULT_ROOT = Path(__file__).resolve().parents[1]

REGISTRY_PATH = "buzz/agents/registry.yaml"
PROFILE_DIR = "buzz/agents"
COMMUNITY_PATH = "buzz/community.json"
OWNER_REVIEW_PATH = "release/OWNER_REVIEW.md"
STEWARD_PROFILE = "buzz/agents/STEWARD.md"

# Owner gate 6 is "Initial community-agent providers"; hold 6 is "Steward
# escalation readiness". Both live in release/OWNER_REVIEW.md.
PROVIDER_GATE = 6
STEWARD_HOLD = 6

SUPPORTED_SCHEMA_VERSIONS = (1,)

# Attended autonomy only. There is no unattended level this phase, so a value
# that names one is rejected with its own message rather than a generic
# vocabulary complaint.
AUTONOMY_LEVELS = ("observe", "draft", "recommend")
UNATTENDED_MARKERS = (
    "auto",
    "unattended",
    "act",
    "enact",
    "execute",
    "enforce",
    "decide",
    "moderate",
    "publish",
    "merge",
    "apply",
    "unsupervised",
)

STATUS_VALUES = ("not_enabled", "enabled")

# Controlled operating roles from community/GOVERNANCE.md and ops/BETA_OPS.md.
# A registry field that must name a human uses one of these; personal names,
# handles, and contact routes belong in the private maintainer record.
ROLE_VOCABULARY = (
    "founder",
    "beta-owner",
    "continuity-owner",
    "maintainer",
    "area-maintainer",
    "artifact-maintainer",
    "release-owner",
    "private-intake-owner",
    "authorized-inviter",
    "agent-sponsor",
    "session-facilitator",
)

# An open channel anyone can write into is still a broadcast surface, so
# announcements needs the same explicit human approval as a private channel.
APPROVAL_REQUIRED_CHANNELS = ("announcements",)

REQUIRED_AGENT_FIELDS = (
    "id",
    "name",
    "profile",
    "mission",
    "autonomy",
    "channels",
    "identity",
    "prohibited",
    "escalation",
    "enablement_prerequisites",
    "status",
)
OPTIONAL_AGENT_FIELDS = (
    "autonomy_basis",
    "conditional_channels",
    "excluded_channels",
    "channel_note",
)

REQUIRED_IDENTITY_FIELDS = (
    "dedicated_identity",
    "shared_across_instances",
    "accountable_human_role",
    "requirement",
)

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REPO_PATH_RE = re.compile(r"\b[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+\.(?:md|py|json|ya?ml)\b")
OPEN_RE = re.compile(r"\bOPEN\b")

# Known personal identifiers for the humans named in this repository, plus the
# shape of an address or handle. A role field carrying one of these names a
# person, which is exactly what the registry must not do.
PERSON_MARKER_RE = re.compile(r"@|\bdakota\b|\bsmithdak\b|\bdaksmith\d*\b", re.IGNORECASE)

# The non-negotiables every agent's `prohibited` list must still carry. Each
# rule is satisfied by one entry containing at least one term from every group,
# so rewording is allowed but dropping the boundary is not.
LOCKED_PROHIBITIONS = (
    (
        "silently removing or deleting members or content",
        (
            ("silent",),
            ("remov", "delet", "ban", "hid", "edit"),
            ("member", "people", "person", "content", "post", "participant"),
        ),
    ),
    (
        "requesting, receiving, storing, or recovering the owner private key",
        (
            ("private key",),
            ("request", "receiv", "stor", "recover", "expose", "hold", "accept"),
        ),
    ),
    (
        "publishing, merging, or announcing without human review",
        (
            ("publish", "merg", "announc"),
            ("human",),
            ("review", "approval", "approve"),
        ),
    ),
    (
        "changing a maturity or evidence_quality field",
        (
            ("chang", "modif", "edit", "alter", "updat", "rewrit", "set "),
            ("maturity",),
            ("evidence_quality", "evidence quality"),
        ),
    ),
)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def is_nonempty_str(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def is_str_list(value) -> bool:
    return isinstance(value, list) and all(is_nonempty_str(item) for item in value)


def label(agent_id, index: int) -> str:
    if is_nonempty_str(agent_id):
        return f"agent '{agent_id}'"
    return f"agent #{index + 1} (no usable id)"


def load_registry(path: Path, errors: list[str]) -> dict:
    if not path.exists():
        fail(
            errors,
            f"Missing {REGISTRY_PATH}. Every agent profile in {PROFILE_DIR}/ needs a "
            "registry entry; create the file before running this validator.",
        )
        return {}
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(errors, f"Cannot parse {REGISTRY_PATH}: {exc}")
        return {}
    if not isinstance(value, dict):
        fail(errors, f"{REGISTRY_PATH} must be a YAML mapping with 'schema_version' and 'agents'.")
        return {}
    return value


def load_channels(root: Path, errors: list[str]) -> dict[str, str] | None:
    """Return ``{channel name: visibility}`` from buzz/community.json."""
    path = root / COMMUNITY_PATH
    if not path.exists():
        fail(
            errors,
            f"Missing {COMMUNITY_PATH}; channel scope cannot be checked. Run this "
            "validator against a repository root that contains the channel map.",
        )
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(errors, f"Cannot parse {COMMUNITY_PATH}: {exc}")
        return None
    channels = data.get("channels") if isinstance(data, dict) else None
    if not isinstance(channels, list) or not channels:
        fail(errors, f"{COMMUNITY_PATH} has no 'channels' list; channel scope cannot be checked.")
        return None
    result: dict[str, str] = {}
    for channel in channels:
        if isinstance(channel, dict) and is_nonempty_str(channel.get("name")):
            result[channel["name"]] = str(channel.get("visibility", "unknown"))
    if not result:
        fail(errors, f"{COMMUNITY_PATH} lists no named channels; channel scope cannot be checked.")
        return None
    return result


def row_status(text: str, marker: str) -> str | None:
    """Return ``OPEN``/``RECORDED`` for the single owner-review row containing ``marker``."""
    rows = [line for line in text.splitlines() if marker in line]
    if len(rows) != 1:
        return None
    return "OPEN" if OPEN_RE.search(rows[0]) else "RECORDED"


def read_owner_review(root: Path, errors: list[str]) -> tuple[str | None, bool]:
    """Return ``(gate 6 status, hold 6 row found)`` from release/OWNER_REVIEW.md."""
    path = root / OWNER_REVIEW_PATH
    if not path.exists():
        fail(
            errors,
            f"Missing {OWNER_REVIEW_PATH}; owner gate {PROVIDER_GATE} cannot be read, so no "
            "agent status can be checked. Run this validator against the full repository.",
        )
        return None, False
    text = path.read_text(encoding="utf-8", errors="replace")
    gate = row_status(text, f"(gate {PROVIDER_GATE})")
    if gate is None:
        fail(
            errors,
            f"{OWNER_REVIEW_PATH} does not contain exactly one row marked "
            f"'(gate {PROVIDER_GATE})'. This validator reads that row to decide whether an "
            "agent may be enabled; restore the anchor or update PROVIDER_GATE in "
            "scripts/validate_agents.py before relying on the result.",
        )
    hold_found = row_status(text, f"(hold {STEWARD_HOLD})") is not None
    if not hold_found:
        fail(
            errors,
            f"{OWNER_REVIEW_PATH} does not contain exactly one row marked "
            f"'(hold {STEWARD_HOLD})' (Steward escalation readiness). The Steward's enablement "
            "prerequisite points at that row; restore the anchor or update STEWARD_HOLD in "
            "scripts/validate_agents.py.",
        )
    return gate, hold_found


def check_role(value, where: str, errors: list[str]) -> None:
    if not is_nonempty_str(value):
        fail(
            errors,
            f"{where} is missing or empty. Name one controlled role: "
            f"{', '.join(ROLE_VOCABULARY)}.",
        )
        return
    candidate = value.strip()
    if PERSON_MARKER_RE.search(candidate):
        fail(
            errors,
            f"{where} names a person, handle, or address ({candidate!r}). Use a controlled "
            f"role instead: {', '.join(ROLE_VOCABULARY)}. Personal names and contact routes "
            "stay in the private maintainer record.",
        )
        return
    if candidate not in ROLE_VOCABULARY:
        fail(
            errors,
            f"{where} is {candidate!r}, which is not a controlled role. Use one of: "
            f"{', '.join(ROLE_VOCABULARY)}.",
        )


def check_prose_names_no_person(value: str, where: str, errors: list[str]) -> None:
    if PERSON_MARKER_RE.search(value):
        fail(
            errors,
            f"{where} names a person, handle, or address. Describe the route by role; "
            "personal names and contact routes stay in the private maintainer record.",
        )


def check_repo_paths(value: str, where: str, root: Path, errors: list[str]) -> None:
    for candidate in REPO_PATH_RE.findall(value):
        if not (root / candidate).exists():
            fail(
                errors,
                f"{where} points at {candidate}, which does not exist. Fix the path or "
                "remove the reference.",
            )


def check_prohibited(entry: dict, where: str, errors: list[str]) -> None:
    prohibited = entry.get("prohibited")
    if not is_str_list(prohibited) or not prohibited:
        fail(
            errors,
            f"{where}: 'prohibited' must be a non-empty list of strings carrying every "
            "locked non-negotiable.",
        )
        return
    lowered = [item.lower() for item in prohibited]
    for description, groups in LOCKED_PROHIBITIONS:
        satisfied = any(
            all(any(term in item for term in group) for group in groups) for item in lowered
        )
        if not satisfied:
            fail(
                errors,
                f"{where}: 'prohibited' omits a locked non-negotiable - {description}. Add an "
                "entry stating it; this boundary is not removable by an agent or a task.",
            )


def check_channels(
    entry: dict,
    where: str,
    channels: dict[str, str] | None,
    errors: list[str],
) -> None:
    block = entry.get("channels")
    if not isinstance(block, dict):
        fail(
            errors,
            f"{where}: 'channels' must be a mapping with 'read' and 'write' lists.",
        )
        return
    unknown_keys = sorted(set(block) - {"read", "write", "write_approval"})
    if unknown_keys:
        fail(
            errors,
            f"{where}: 'channels' has unrecognized key(s) {', '.join(unknown_keys)}. "
            "Allowed keys are read, write, write_approval.",
        )
    for name in ("read", "write"):
        if name not in block:
            fail(
                errors,
                f"{where}: 'channels' is missing '{name}'. Declare both lists explicitly, "
                "using an empty list when no channel is granted.",
            )
            return
    read = block.get("read")
    write = block.get("write")
    for name, value in (("read", read), ("write", write)):
        if not is_str_list(value):
            fail(errors, f"{where}: 'channels.{name}' must be a list of channel names.")
            return
    for name, value in (("read", read), ("write", write)):
        if len(set(value)) != len(value):
            fail(errors, f"{where}: 'channels.{name}' repeats a channel name.")

    if channels is not None:
        for name, value in (("read", read), ("write", write)):
            for channel in value:
                if channel not in channels:
                    fail(
                        errors,
                        f"{where}: 'channels.{name}' declares {channel!r}, which is not a "
                        f"channel in {COMMUNITY_PATH}. Declared scope must match the real "
                        "channel map.",
                    )

    for channel in write:
        if channel not in read:
            fail(
                errors,
                f"{where}: declares write access to {channel!r} without read access. "
                "Membership grants reading; list the channel under 'channels.read' too.",
            )

    excluded = entry.get("excluded_channels", [])
    if excluded is None:
        excluded = []
    if not is_str_list(excluded):
        fail(errors, f"{where}: 'excluded_channels' must be a list of channel names.")
    else:
        for channel in excluded:
            if channels is not None and channel not in channels:
                fail(
                    errors,
                    f"{where}: 'excluded_channels' names {channel!r}, which is not a channel "
                    f"in {COMMUNITY_PATH}.",
                )
            if channel in read or channel in write:
                fail(
                    errors,
                    f"{where}: {channel!r} is listed as excluded and as granted scope. "
                    "Decide which one is true.",
                )

    approval = block.get("write_approval", {})
    if approval is None:
        approval = {}
    if not isinstance(approval, dict):
        fail(
            errors,
            f"{where}: 'channels.write_approval' must be a mapping of channel name to "
            "{approver_role, condition}.",
        )
        approval = {}
    for channel in sorted(set(approval) - set(write)):
        fail(
            errors,
            f"{where}: 'channels.write_approval' covers {channel!r}, which is not in "
            "'channels.write'. Remove the stale approval record.",
        )

    for channel in write:
        visibility = channels.get(channel) if channels is not None else None
        needs_approval = channel in APPROVAL_REQUIRED_CHANNELS or visibility == "private"
        if not needs_approval:
            continue
        reason = (
            f"{channel!r} is a private channel"
            if visibility == "private"
            else f"{channel!r} is a broadcast channel"
        )
        record = approval.get(channel)
        if not isinstance(record, dict):
            fail(
                errors,
                f"{where}: declares write access to {channel!r} with no human-approval "
                f"record. {reason.capitalize()}, so 'channels.write_approval.{channel}' must "
                "state an approver_role and the condition under which a human approves each "
                "post.",
            )
            continue
        check_role(
            record.get("approver_role"),
            f"{where}: 'channels.write_approval.{channel}.approver_role'",
            errors,
        )
        if not is_nonempty_str(record.get("condition")):
            fail(
                errors,
                f"{where}: 'channels.write_approval.{channel}.condition' must state when a "
                "human approves the write.",
            )


def check_conditional_channels(
    entry: dict,
    where: str,
    channels: dict[str, str] | None,
    errors: list[str],
) -> None:
    conditional = entry.get("conditional_channels", [])
    if conditional is None:
        conditional = []
    if not isinstance(conditional, list):
        fail(errors, f"{where}: 'conditional_channels' must be a list.")
        return
    for index, record in enumerate(conditional):
        location = f"{where}: 'conditional_channels[{index}]'"
        if not isinstance(record, dict):
            fail(errors, f"{location} must be a mapping with channel, access, condition, approver_role.")
            continue
        channel = record.get("channel")
        if not is_nonempty_str(channel):
            fail(errors, f"{location} has no 'channel'.")
        elif channels is not None and channel not in channels:
            fail(
                errors,
                f"{location} names {channel!r}, which is not a channel in {COMMUNITY_PATH}.",
            )
        access = record.get("access")
        if access not in ("read", "write"):
            fail(errors, f"{location}: 'access' must be 'read' or 'write'.")
        if not is_nonempty_str(record.get("condition")):
            fail(errors, f"{location}: 'condition' must state when the access is granted and removed.")
        check_role(record.get("approver_role"), f"{location}: 'approver_role'", errors)


def check_identity(entry: dict, where: str, errors: list[str]) -> None:
    identity = entry.get("identity")
    if not isinstance(identity, dict):
        fail(
            errors,
            f"{where}: 'identity' must be a mapping recording the separate-identity "
            "requirement from ops/BUZZ_SECURITY.md.",
        )
        return
    for field in REQUIRED_IDENTITY_FIELDS:
        if field not in identity:
            fail(errors, f"{where}: 'identity' is missing '{field}'.")
    if identity.get("dedicated_identity") is not True:
        fail(
            errors,
            f"{where}: 'identity.dedicated_identity' must be true. ops/BUZZ_SECURITY.md gives "
            "every agent one unique identity.",
        )
    if identity.get("shared_across_instances") is not False:
        fail(
            errors,
            f"{where}: 'identity.shared_across_instances' must be false. Identities are never "
            "shared, including between instances of one role.",
        )
    check_role(identity.get("accountable_human_role"), f"{where}: 'identity.accountable_human_role'", errors)
    if not is_nonempty_str(identity.get("requirement")):
        fail(errors, f"{where}: 'identity.requirement' must state the identity rule in one place.")


def check_escalation(entry: dict, where: str, errors: list[str]) -> None:
    escalation = entry.get("escalation")
    if not isinstance(escalation, dict):
        fail(
            errors,
            f"{where}: 'escalation' must be a mapping with 'route' and 'owner_role'.",
        )
        return
    route = escalation.get("route")
    if not is_nonempty_str(route):
        fail(errors, f"{where}: 'escalation.route' must describe how the escalation travels.")
    else:
        check_prose_names_no_person(route, f"{where}: 'escalation.route'", errors)
    check_role(escalation.get("owner_role"), f"{where}: 'escalation.owner_role'", errors)
    onward = escalation.get("escalates_to", [])
    if onward is None:
        onward = []
    if not isinstance(onward, list):
        fail(errors, f"{where}: 'escalation.escalates_to' must be a list of controlled roles.")
        return
    for index, role in enumerate(onward):
        check_role(role, f"{where}: 'escalation.escalates_to[{index}]'", errors)


def check_autonomy(entry: dict, where: str, errors: list[str]) -> None:
    value = entry.get("autonomy")
    if not is_nonempty_str(value):
        fail(
            errors,
            f"{where}: 'autonomy' is missing. Use one of: {', '.join(AUTONOMY_LEVELS)}.",
        )
        return
    normalized = value.strip().lower()
    if normalized in AUTONOMY_LEVELS:
        return
    if any(marker in normalized for marker in UNATTENDED_MARKERS):
        fail(
            errors,
            f"{where}: 'autonomy' is {value.strip()!r}, an unattended level. No agent runs "
            "unattended: every level requires a human decision. Use one of: "
            f"{', '.join(AUTONOMY_LEVELS)}.",
        )
        return
    fail(
        errors,
        f"{where}: 'autonomy' is {value.strip()!r}, which is outside the vocabulary. Use one "
        f"of: {', '.join(AUTONOMY_LEVELS)}.",
    )


def check_status(entry: dict, where: str, gate: str | None, errors: list[str]) -> None:
    value = entry.get("status")
    if not is_nonempty_str(value) or value.strip() not in STATUS_VALUES:
        fail(
            errors,
            f"{where}: 'status' must be one of: {', '.join(STATUS_VALUES)}.",
        )
        return
    if value.strip() == "not_enabled":
        return
    if gate is None:
        fail(
            errors,
            f"{where}: 'status' claims enabled, but owner gate {PROVIDER_GATE} could not be "
            f"read from {OWNER_REVIEW_PATH}. An unreadable gate is not an approved gate.",
        )
        return
    if gate == "OPEN":
        fail(
            errors,
            f"{where}: 'status' claims enabled while owner gate {PROVIDER_GATE} (Initial "
            f"community-agent providers) is still recorded OPEN in {OWNER_REVIEW_PATH}. Set "
            "status back to not_enabled; only a human recording the gate decision can change "
            "that.",
        )


def check_prerequisites(
    entry: dict,
    where: str,
    root: Path,
    is_steward: bool,
    hold_found: bool,
    errors: list[str],
) -> None:
    prerequisites = entry.get("enablement_prerequisites")
    if not is_str_list(prerequisites) or not prerequisites:
        fail(
            errors,
            f"{where}: 'enablement_prerequisites' must be a non-empty list of the conditions a "
            "human clears before this agent runs.",
        )
        return
    for index, item in enumerate(prerequisites):
        check_repo_paths(item, f"{where}: 'enablement_prerequisites[{index}]'", root, errors)
    if not is_steward:
        return
    hold_marker = f"hold {STEWARD_HOLD}"
    covered = any(
        hold_marker in item.lower() and OWNER_REVIEW_PATH in item for item in prerequisites
    )
    if not covered and hold_found:
        fail(
            errors,
            f"{where}: 'enablement_prerequisites' must name hold {STEWARD_HOLD} (Steward "
            f"escalation readiness) in {OWNER_REVIEW_PATH}. The Steward fails closed without a "
            "tested human escalation route.",
        )


def check_agent(
    entry,
    index: int,
    root: Path,
    channels: dict[str, str] | None,
    gate: str | None,
    hold_found: bool,
    errors: list[str],
) -> tuple[str | None, str | None]:
    """Validate one entry; return ``(id, profile path)`` for cross-entry checks."""
    if not isinstance(entry, dict):
        fail(errors, f"{REGISTRY_PATH}: agents[{index}] must be a mapping.")
        return None, None
    agent_id = entry.get("id")
    where = f"{REGISTRY_PATH}: {label(agent_id, index)}"

    for field in REQUIRED_AGENT_FIELDS:
        if field not in entry:
            fail(errors, f"{where} is missing required field '{field}'.")
    unknown = sorted(set(entry) - set(REQUIRED_AGENT_FIELDS) - set(OPTIONAL_AGENT_FIELDS))
    if unknown:
        fail(
            errors,
            f"{where} has unrecognized field(s) {', '.join(unknown)}. Check for a typo; "
            f"allowed fields are {', '.join(sorted(set(REQUIRED_AGENT_FIELDS) | set(OPTIONAL_AGENT_FIELDS)))}.",
        )

    if not is_nonempty_str(agent_id):
        fail(errors, f"{where}: 'id' must be a non-empty lowercase slug.")
        agent_id = None
    elif not ID_RE.match(agent_id):
        fail(
            errors,
            f"{where}: 'id' must be a lowercase slug like 'release-editor' so a packet can "
            "reference it.",
        )

    if not is_nonempty_str(entry.get("name")):
        fail(errors, f"{where}: 'name' must be the profile's human-readable name.")
    if not is_nonempty_str(entry.get("mission")):
        fail(errors, f"{where}: 'mission' must state the agent's job in one line.")

    profile = entry.get("profile")
    if not is_nonempty_str(profile):
        fail(errors, f"{where}: 'profile' must be the repository-relative path to its .md profile.")
        profile = None
    else:
        profile = profile.strip()
        if not profile.startswith(f"{PROFILE_DIR}/") or not profile.endswith(".md"):
            fail(
                errors,
                f"{where}: 'profile' is {profile!r}; it must be a repository-relative path "
                f"under {PROFILE_DIR}/ ending in .md.",
            )
        elif not (root / profile).exists():
            fail(
                errors,
                f"{where}: 'profile' names {profile}, which does not exist. Fix the path or "
                "remove the entry.",
            )

    check_autonomy(entry, where, errors)
    check_channels(entry, where, channels, errors)
    check_conditional_channels(entry, where, channels, errors)
    check_identity(entry, where, errors)
    check_prohibited(entry, where, errors)
    check_escalation(entry, where, errors)
    check_prerequisites(entry, where, root, profile == STEWARD_PROFILE, hold_found, errors)
    check_status(entry, where, gate, errors)

    if is_nonempty_str(entry.get("channel_note")):
        check_prose_names_no_person(entry["channel_note"], f"{where}: 'channel_note'", errors)

    return agent_id, profile


def check_coverage(root: Path, profiles_declared: list[str], errors: list[str]) -> None:
    directory = root / PROFILE_DIR
    if not directory.is_dir():
        fail(
            errors,
            f"Missing {PROFILE_DIR}/; there are no agent profiles to check against the registry.",
        )
        return
    on_disk = sorted(p.relative_to(root).as_posix() for p in directory.glob("*.md"))
    declared = set(profiles_declared)
    for path in on_disk:
        if path not in declared:
            fail(
                errors,
                f"{path} has no entry in {REGISTRY_PATH}. Every agent profile declares its "
                "identity, channels, autonomy, prohibitions, escalation, and status before it "
                "can be enabled.",
            )
    duplicates = sorted({p for p in profiles_declared if profiles_declared.count(p) > 1})
    for path in duplicates:
        fail(errors, f"{REGISTRY_PATH}: {path} is claimed by more than one entry.")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    registry = load_registry(root / REGISTRY_PATH, errors)
    if not registry:
        return errors

    version = registry.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        fail(
            errors,
            f"{REGISTRY_PATH}: 'schema_version' is {version!r}; this validator supports "
            f"{', '.join(str(v) for v in SUPPORTED_SCHEMA_VERSIONS)}.",
        )

    for index, source in enumerate(registry.get("sources", []) or []):
        if not is_nonempty_str(source):
            fail(errors, f"{REGISTRY_PATH}: 'sources[{index}]' must be a repository path.")
        elif not (root / source.strip()).exists():
            fail(
                errors,
                f"{REGISTRY_PATH}: 'sources[{index}]' names {source.strip()}, which does not exist.",
            )

    channels = load_channels(root, errors)
    gate, hold_found = read_owner_review(root, errors)

    agents = registry.get("agents")
    if not isinstance(agents, list) or not agents:
        fail(
            errors,
            f"{REGISTRY_PATH}: 'agents' must be a non-empty list, one entry per profile in "
            f"{PROFILE_DIR}/.",
        )
        return errors

    ids: list[str] = []
    profiles: list[str] = []
    for index, entry in enumerate(agents):
        agent_id, profile = check_agent(entry, index, root, channels, gate, hold_found, errors)
        if agent_id:
            ids.append(agent_id)
        if profile:
            profiles.append(profile)

    for duplicate in sorted({i for i in ids if ids.count(i) > 1}):
        fail(errors, f"{REGISTRY_PATH}: duplicate agent id {duplicate!r}.")

    check_coverage(root, profiles, errors)
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
        print(f"{len(errors)} agent registry problem(s) found.")
        return 1
    print("Agent registry validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
