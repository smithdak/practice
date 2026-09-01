#!/usr/bin/env python3
"""Dry-run readiness checker for enabling the Practice Steward agent.

A human maintainer runs this before enabling the Steward identity described in
``buzz/agents/STEWARD.md``. It inspects configuration only: it never contacts
the Buzz relay, never enables anything, and never handles keys or credentials.
Enabling the Steward stays a human decision and a human action.

The prerequisites are derived from the "Deployment prerequisite: actionable
human escalation" section of ``buzz/agents/STEWARD.md`` and the Steward row of
the least-membership table in ``ops/BUZZ_SECURITY.md``:

1. Sponsor configured: a role label for the accountable human sponsor. A real
   name is accepted only when the operator explicitly passes one; it belongs in
   the private deployment record, never in the public Steward profile.
2. Member-visible escalation route or label configured: a published label or
   route the agent may cite, anchored to a surface the Steward can see and
   members can use.
3. Human receipt target recorded as a non-secret pointer.
4. Test receipt confirmed via ``--confirmed-test-receipt`` or a dated
   ``test_receipt_date`` config field (YYYY-MM-DD).
5. Declared channel membership exactly matches the least-membership model.

Both source documents are re-read at runtime and checked for drift before any
prerequisite is evaluated, so a structural change fails loudly instead of
checking against stale assumptions.

Exit codes: 0 = every prerequisite is satisfiable from the provided inputs;
1 = at least one prerequisite is unmet, an input is invalid, or a source
document drifted; 2 = command-line usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STEWARD_MD = DEFAULT_ROOT / "buzz" / "agents" / "STEWARD.md"
DEFAULT_SECURITY_MD = DEFAULT_ROOT / "ops" / "BUZZ_SECURITY.md"

EXPECTED_INITIAL_MEMBERSHIP = (
    "start-here",
    "ask-practice",
    "learn",
    "use",
    "automate",
    "build",
    "transform",
)
EXPECTED_EXCLUDED_CHANNELS = (
    "foundry",
    "maintainers",
    "announcements",
    "projects",
    "showcase",
)

MEMBERSHIP_LEAD = "Initial membership is limited to"
EXCLUSION_LEAD = "It has no membership in"
STEWARD_ANCHORS = {
    "## Deployment prerequisite: actionable human escalation": (
        "the section that defines the fail-closed deployment condition"
    ),
    "configured and tested": "the tested-reference requirement behind check 4",
    "The deployment record must name the sponsor privately": (
        "the sponsor-privacy requirement behind check 1"
    ),
    "which published label or route the agent may cite": (
        "the member-visible route requirement behind check 2"
    ),
    "confirm that a human monitors it": "the human receipt requirement behind check 3",
    "fail closed": "the fail-closed behavior this checker enforces",
    MEMBERSHIP_LEAD: "the initial-membership declaration behind check 5",
    EXCLUSION_LEAD: "the exclusion declaration behind check 5",
}

CONFIG_KEYS = {
    "sponsor_role",
    "sponsor_name",
    "escalation_route",
    "receipt_target",
    "test_receipt_date",
    "confirmed_test_receipt",
    "membership",
}

SECRET_PATTERNS = (
    re.compile(r"-----begin", re.IGNORECASE),
    re.compile(r"private key", re.IGNORECASE),
    re.compile(r"\b(password|passwd|secret|token|api[-_]?key|bearer)\b", re.IGNORECASE),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
)

HEADER = (
    "Practice Steward readiness check (dry run). This is a prerequisite checker, "
    "not an enabler: it inspects configuration only, never contacts the Buzz "
    "relay, and never handles keys or credentials. Enabling the Steward stays a "
    "human decision and a human action."
)
DO_NOT_ENABLE = (
    "Do not enable the Steward while any prerequisite is unmet or unverified. "
    "Enabling is a human decision (see 'Deployment prerequisite: actionable "
    "human escalation' in buzz/agents/STEWARD.md)."
)


@dataclass
class Settings:
    sponsor_role: str | None = None
    sponsor_name: str | None = None
    escalation_route: str | None = None
    receipt_target: str | None = None
    test_receipt_date: str | None = None
    confirmed_test_receipt: bool = False
    membership: list[str] | None = None
    steward_md: Path = DEFAULT_STEWARD_MD
    security_md: Path = DEFAULT_SECURITY_MD


def secret_shaped(value: str) -> bool:
    return any(pattern.search(value) for pattern in SECRET_PATTERNS)


def mentions(text: str, channel: str) -> bool:
    pattern = re.compile(
        r"(?<![A-Za-z0-9-])" + re.escape(channel) + r"(?![A-Za-z0-9-])",
        re.IGNORECASE,
    )
    return bool(pattern.search(text))


def read_document(path: Path) -> tuple[str | None, list[str]]:
    try:
        return path.read_text(encoding="utf-8"), []
    except OSError as exc:
        return None, [
            f"DRIFT: cannot read {path}: {exc}. Run from the repository root, or "
            "pass --steward-md and --security-md pointing at buzz/agents/STEWARD.md "
            "and ops/BUZZ_SECURITY.md."
        ]


def compare_membership_model(source: Path, initial: list[str], excluded: list[str]) -> list[str]:
    drift: list[str] = []
    if sorted(set(initial)) != sorted(EXPECTED_INITIAL_MEMBERSHIP):
        drift.append(
            f"DRIFT: {source} now lists the Steward's initial membership as "
            f"{sorted(set(initial))} but this checker expects "
            f"{sorted(EXPECTED_INITIAL_MEMBERSHIP)} (least-membership model, "
            "ops/BUZZ_SECURITY.md). Reconcile the documents and update "
            "EXPECTED_INITIAL_MEMBERSHIP in scripts/steward_readiness_check.py "
            "before re-running."
        )
    if sorted(set(excluded)) != sorted(EXPECTED_EXCLUDED_CHANNELS):
        drift.append(
            f"DRIFT: {source} now lists the Steward's excluded channels as "
            f"{sorted(set(excluded))} but this checker expects "
            f"{sorted(EXPECTED_EXCLUDED_CHANNELS)}. Reconcile the documents and "
            "update EXPECTED_EXCLUDED_CHANNELS in scripts/steward_readiness_check.py "
            "before re-running."
        )
    return drift


def parse_steward_profile(path: Path) -> tuple[dict | None, list[str]]:
    raw, drift = read_document(path)
    if raw is None:
        return None, drift
    text = " ".join(raw.split())
    for anchor in sorted(STEWARD_ANCHORS):
        if anchor not in text:
            drift.append(
                f"DRIFT: {path} is missing the expected anchor {anchor!r} "
                f"({STEWARD_ANCHORS[anchor]}). The readiness checks are derived from "
                "buzz/agents/STEWARD.md; reconcile the document and update "
                "scripts/steward_readiness_check.py before re-running."
            )
    if drift:
        return None, drift
    membership_start = text.index(MEMBERSHIP_LEAD)
    membership_end = text.find(".", membership_start)
    exclusion_start = text.find(EXCLUSION_LEAD)
    exclusion_end = text.find(".", exclusion_start) if exclusion_start != -1 else -1
    if membership_end == -1 or exclusion_start == -1 or exclusion_end == -1:
        drift.append(
            f"DRIFT: {path} no longer contains a parsable initial-membership or "
            "exclusion sentence. The membership check is derived from those "
            "sentences; reconcile the document and update "
            "scripts/steward_readiness_check.py before re-running."
        )
        return None, drift
    if exclusion_start < membership_end:
        drift.append(
            f"DRIFT: {path} no longer states the initial-membership sentence before "
            "the exclusion sentence. Reconcile the document and update "
            "scripts/steward_readiness_check.py before re-running."
        )
        return None, drift
    initial = re.findall(r"`([^`\n]+)`", text[membership_start:membership_end])
    excluded = re.findall(r"`([^`\n]+)`", text[exclusion_start:exclusion_end])
    if not initial or not excluded:
        drift.append(
            f"DRIFT: the membership sentences in {path} no longer list backticked "
            "channel names. Reconcile the document and update "
            "scripts/steward_readiness_check.py before re-running."
        )
        return None, drift
    drift = compare_membership_model(path, initial, excluded)
    if drift:
        return None, drift
    return {"initial": initial, "excluded": excluded}, []


def parse_security_runbook(path: Path) -> tuple[dict | None, list[str]]:
    text, drift = read_document(path)
    if text is None:
        return None, drift
    lines = text.splitlines()
    header = next(
        (
            line
            for line in lines
            if line.strip().startswith("| Identity")
            and "Initial channel membership" in line
            and "Explicitly excluded" in line
        ),
        None,
    )
    row = next((line for line in lines if line.strip().startswith("| Steward agent")), None)
    if header is None or row is None:
        drift.append(
            f"DRIFT: {path} no longer contains the expected least-membership table "
            "(an '| Identity' header row with 'Initial channel membership' and "
            "'Explicitly excluded' columns, and a '| Steward agent' row). The "
            "membership check is derived from that table; reconcile the document "
            "and update scripts/steward_readiness_check.py before re-running."
        )
        return None, drift
    header_cells = [cell.strip() for cell in header.strip().strip("|").split("|")]
    row_cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
    if len(header_cells) != len(row_cells):
        drift.append(
            f"DRIFT: the least-membership table in {path} changed shape; the "
            "'| Steward agent' row no longer matches the header column count. "
            "Reconcile the document and update scripts/steward_readiness_check.py "
            "before re-running."
        )
        return None, drift
    initial_cell = row_cells[header_cells.index("Initial channel membership")]
    excluded_cell = row_cells[header_cells.index("Explicitly excluded")]
    initial = re.findall(r"`([^`\n]+)`", initial_cell)
    excluded = re.findall(r"`([^`\n]+)`", excluded_cell)
    if not initial or not excluded:
        drift.append(
            f"DRIFT: the Steward row in {path} no longer lists backticked channel "
            "names in its 'Initial channel membership' and 'Explicitly excluded' "
            "cells. Reconcile the document and update "
            "scripts/steward_readiness_check.py before re-running."
        )
        return None, drift
    drift = compare_membership_model(path, initial, excluded)
    if drift:
        return None, drift
    return {"initial": initial, "excluded": excluded}, []


def load_config(path: str) -> tuple[dict, list[str]]:
    errors: list[str] = []
    values: dict = {}
    try:
        loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        return {}, [f"Config error: cannot read {path}: {exc}"]
    except json.JSONDecodeError as exc:
        return {}, [f"Config error: {path} is not valid JSON: {exc}"]
    if not isinstance(loaded, dict):
        return {}, [f"Config error: {path} must contain a JSON object."]
    unknown = sorted(set(loaded) - CONFIG_KEYS)
    if unknown:
        errors.append(
            f"Config error: unknown key(s) in {path}: {', '.join(unknown)}. "
            f"Recognized keys: {', '.join(sorted(CONFIG_KEYS))}."
        )
    for key in sorted(CONFIG_KEYS & set(loaded)):
        value = loaded[key]
        if key == "membership":
            if isinstance(value, str):
                value = [part for part in value.split(",")]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                errors.append(
                    f"Config error: membership in {path} must be a list of channel "
                    "names or a comma-separated string."
                )
                continue
        elif key == "confirmed_test_receipt":
            if not isinstance(value, bool):
                errors.append(
                    f"Config error: confirmed_test_receipt in {path} must be a boolean."
                )
                continue
        elif not isinstance(value, str):
            errors.append(f"Config error: {key} in {path} must be a string.")
            continue
        values[key] = value
    return values, errors


def build_settings(args: argparse.Namespace) -> tuple[Settings, list[str]]:
    config_values, errors = ({}, [])
    if args.config:
        config_values, errors = load_config(args.config)
    settings = Settings()
    settings.sponsor_role = (
        args.sponsor_role if args.sponsor_role is not None else config_values.get("sponsor_role")
    )
    settings.sponsor_name = (
        args.sponsor_name if args.sponsor_name is not None else config_values.get("sponsor_name")
    )
    settings.escalation_route = (
        args.escalation_route
        if args.escalation_route is not None
        else config_values.get("escalation_route")
    )
    settings.receipt_target = (
        args.receipt_target
        if args.receipt_target is not None
        else config_values.get("receipt_target")
    )
    settings.test_receipt_date = (
        args.test_receipt_date
        if args.test_receipt_date is not None
        else config_values.get("test_receipt_date")
    )
    settings.confirmed_test_receipt = (
        args.confirmed_test_receipt or bool(config_values.get("confirmed_test_receipt"))
    )
    membership = args.membership if args.membership is not None else config_values.get("membership")
    if isinstance(membership, str):
        membership = membership.split(",")
    settings.membership = membership
    settings.steward_md = Path(args.steward_md)
    settings.security_md = Path(args.security_md)
    return settings, errors


def check_sponsor(settings: Settings) -> tuple[bool, list[str], list[str]]:
    failures: list[str] = []
    notes: list[str] = []
    role = (settings.sponsor_role or "").strip()
    if not role:
        failures.append(
            "FAIL [sponsor] No sponsor is configured. The deployment record must name "
            "the sponsor privately (buzz/agents/STEWARD.md). Pass --sponsor-role "
            "'ROLE LABEL' (for example 'community owner' or 'named maintainer') or "
            "set sponsor_role in the --config JSON."
        )
    elif secret_shaped(role):
        failures.append(
            "FAIL [sponsor] The sponsor role value looks like a credential, private "
            "contact detail, or key material. This checker never handles keys or "
            "credentials: pass a role label such as 'community owner', and keep "
            "private values in the private deployment record."
        )
    name = (settings.sponsor_name or "").strip()
    if name and secret_shaped(name):
        failures.append(
            "FAIL [sponsor] The sponsor name looks like a credential, private contact "
            "detail, or key material. This checker never handles keys or credentials: "
            "pass a real name or omit --sponsor-name, and keep private values in the "
            "private deployment record."
        )
    elif name:
        notes.append(
            "NOTE [sponsor] The sponsor name is accepted for the private deployment "
            "record only. Never place it in the public Steward profile: "
            "buzz/agents/STEWARD.md prohibits private contact details and owner "
            "identity there."
        )
    return not failures, failures, notes


def check_escalation_route(settings: Settings) -> tuple[bool, list[str], list[str]]:
    route = (settings.escalation_route or "").strip()
    if not route:
        return False, [
            "FAIL [route] No member-visible escalation route or label is configured. "
            "buzz/agents/STEWARD.md requires 'a member-actionable escalation reference "
            "in a surface the Steward can see and members can use' and a stated "
            "'published label or route the agent may cite'. Pass --escalation-route or "
            "set escalation_route in the --config JSON."
        ], []
    if secret_shaped(route):
        return False, [
            "FAIL [route] The escalation route looks like a credential, private "
            "contact detail, or key material. This checker never handles keys or "
            "credentials: cite a published label or route, and keep private addresses "
            "out of member-visible surfaces (buzz/agents/STEWARD.md)."
        ], []
    excluded_hits = [name for name in EXPECTED_EXCLUDED_CHANNELS if mentions(route, name)]
    if excluded_hits:
        return False, [
            f"FAIL [route] The escalation route cites {', '.join(excluded_hits)}, which "
            "the least-membership model (ops/BUZZ_SECURITY.md) excludes from the "
            "Steward. The Steward cannot see that surface. Cite a published label or "
            f"route inside: {', '.join(EXPECTED_INITIAL_MEMBERSHIP)}."
        ], []
    if re.search(r"\b(direct message|dm)\b", route, re.IGNORECASE):
        return False, [
            "FAIL [route] The escalation route cites a direct message, which is not a "
            "surface the Steward can see. Cite a published label or route inside: "
            f"{', '.join(EXPECTED_INITIAL_MEMBERSHIP)}."
        ], []
    if not any(mentions(route, name) for name in EXPECTED_INITIAL_MEMBERSHIP):
        return False, [
            "FAIL [route] The escalation route does not name a surface the Steward can "
            "see. It must cite a published label or route inside one of: "
            f"{', '.join(EXPECTED_INITIAL_MEMBERSHIP)} (buzz/agents/STEWARD.md: 'a "
            "surface the Steward can see and members can use')."
        ], []
    return True, [], []


def check_receipt_target(settings: Settings) -> tuple[bool, list[str], list[str]]:
    target = (settings.receipt_target or "").strip()
    if not target:
        return False, [
            "FAIL [receipt] No human receipt target is recorded. buzz/agents/STEWARD.md "
            "requires confirmation that a human monitors the escalation reference. "
            "Record a non-secret pointer via --receipt-target or the receipt_target "
            "config field (for example 'maintainers escalation rota, reviewed daily'); "
            "keep private addresses and credentials in the private deployment record."
        ], []
    if secret_shaped(target):
        return False, [
            "FAIL [receipt] The receipt target looks like a credential, private contact "
            "detail, or key material. This checker never handles keys or credentials: "
            "record a non-secret pointer (for example a rota or private-inventory "
            "reference) instead."
        ], []
    return True, [], []


def check_test_receipt(settings: Settings) -> tuple[bool, list[str], list[str]]:
    notes: list[str] = []
    date_value = (settings.test_receipt_date or "").strip()
    date_ok = False
    if date_value:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_value):
            try:
                date.fromisoformat(date_value)
                date_ok = True
            except ValueError:
                date_ok = False
        if not date_ok:
            return False, [
                f"FAIL [test receipt] The test receipt date {date_value!r} is not a "
                "valid calendar date in YYYY-MM-DD form. Correct --test-receipt-date or "
                "the test_receipt_date config field."
            ], []
    if settings.confirmed_test_receipt or date_ok:
        if settings.confirmed_test_receipt and not date_value:
            notes.append(
                "NOTE [test receipt] Record the date of the confirmed test receipt "
                "(--test-receipt-date or the test_receipt_date config field) so the "
                "retained evidence is dated."
            )
        return True, [], notes
    return False, [
        "FAIL [test receipt] No test receipt is confirmed. buzz/agents/STEWARD.md "
        "fails closed when the escalation reference is unverified: run a test "
        "escalation through the configured route, confirm a human received it, then "
        "pass --confirmed-test-receipt or set test_receipt_date (YYYY-MM-DD) in the "
        "--config JSON."
    ], []


def check_membership(settings: Settings) -> tuple[bool, list[str], list[str]]:
    failures: list[str] = []
    declared = settings.membership
    if not declared:
        return False, [
            "FAIL [membership] No channel membership is declared. The least-membership "
            "model (ops/BUZZ_SECURITY.md, Steward row; buzz/agents/STEWARD.md, 'Tools "
            f"and channel access') gives the Steward exactly: "
            f"{', '.join(EXPECTED_INITIAL_MEMBERSHIP)}. Pass --membership "
            "'start-here,ask-practice,...' or set membership in the --config JSON."
        ], []
    seen: set[str] = set()
    duplicates: list[str] = []
    for raw in declared:
        name = raw.strip()
        if not name:
            failures.append(
                "FAIL [membership] The declared membership contains an empty channel "
                "name. Declare each channel as a lowercase name such as 'start-here'."
            )
            continue
        if name in seen and name not in duplicates:
            duplicates.append(name)
        seen.add(name)
    for name in duplicates:
        failures.append(
            f"FAIL [membership] The declared membership lists {name} more than once. "
            "Declare each channel exactly once."
        )
    missing = [name for name in EXPECTED_INITIAL_MEMBERSHIP if name not in seen]
    if missing:
        failures.append(
            f"FAIL [membership] The declared membership is missing required channels: "
            f"{', '.join(missing)}. The model gives the Steward exactly: "
            f"{', '.join(EXPECTED_INITIAL_MEMBERSHIP)}."
        )
    for name in sorted(name for name in seen if name not in EXPECTED_INITIAL_MEMBERSHIP):
        if name in EXPECTED_EXCLUDED_CHANNELS:
            failures.append(
                f"FAIL [membership] The declared membership includes {name}, which the "
                "model explicitly excludes for the Steward (excluded: "
                f"{', '.join(EXPECTED_EXCLUDED_CHANNELS)}). Remove it before enabling."
            )
        else:
            failures.append(
                f"FAIL [membership] The declared membership includes {name}, which is "
                "not in the Steward membership model. Channel names are lowercase (for "
                "example 'start-here'); confirm against ops/BUZZ_SECURITY.md."
            )
    return not failures, failures, []


CHECKS = (
    (1, "Sponsor configured", check_sponsor),
    (2, "Member-visible escalation route or label configured", check_escalation_route),
    (3, "Human receipt target recorded", check_receipt_target),
    (4, "Test receipt confirmed", check_test_receipt),
    (5, "Declared membership matches the least-membership model", check_membership),
)


def evaluate(settings: Settings) -> tuple[list[tuple[int, str, bool, list[str]]], list[str]]:
    results: list[tuple[int, str, bool, list[str]]] = []
    notes: list[str] = []
    for index, title, check in CHECKS:
        ok, failures, check_notes = check(settings)
        results.append((index, title, ok, failures))
        notes.extend(check_notes)
    return results, notes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Dry-run readiness checker for the Practice Steward agent.\n"
            "\n"
            "This is a prerequisite checker, not an enabler: it never enables the "
            "Steward, never contacts the Buzz relay, and never handles keys or "
            "credentials. Enabling the Steward stays a human decision and a human "
            "action.\n"
            "\n"
            "It derives the prerequisites from buzz/agents/STEWARD.md ('Deployment "
            "prerequisite: actionable human escalation') and the least-membership "
            "model in ops/BUZZ_SECURITY.md, re-reading both documents at runtime and "
            "failing on drift."
        ),
        epilog=(
            "Exit codes: 0 = every prerequisite is satisfiable from the provided "
            "inputs; 1 = at least one prerequisite is unmet, an input is invalid, or "
            "a source document drifted; 2 = usage error."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        metavar="PATH",
        help=(
            "JSON config file with any of: sponsor_role, sponsor_name, "
            "escalation_route, receipt_target, test_receipt_date, "
            "confirmed_test_receipt, membership. Command-line flags override "
            "config values."
        ),
    )
    parser.add_argument(
        "--sponsor-role",
        metavar="LABEL",
        help="role label of the accountable human sponsor, e.g. 'community owner'.",
    )
    parser.add_argument(
        "--sponsor-name",
        metavar="NAME",
        help=(
            "optional real sponsor name for the private deployment record; never "
            "place it in the public Steward profile."
        ),
    )
    parser.add_argument(
        "--escalation-route",
        metavar="TEXT",
        help=(
            "member-visible escalation route or label the agent may cite; must name a "
            "surface the Steward can see, e.g. 'the escalation label pinned on the "
            "start-here canvas'."
        ),
    )
    parser.add_argument(
        "--receipt-target",
        metavar="POINTER",
        help=(
            "non-secret pointer to where escalations land and which human monitors "
            "them, e.g. 'maintainers escalation rota, reviewed daily'. Never a private "
            "address or credential."
        ),
    )
    parser.add_argument(
        "--test-receipt-date",
        metavar="YYYY-MM-DD",
        help="date a test escalation was sent and a human confirmed receipt.",
    )
    parser.add_argument(
        "--confirmed-test-receipt",
        action="store_true",
        help=(
            "confirm a test escalation was sent through the configured route and a "
            "human confirmed receipt."
        ),
    )
    parser.add_argument(
        "--membership",
        metavar="CH1,CH2,...",
        help=(
            "declared Steward channel membership as a comma-separated list; must "
            "exactly match the least-membership model in ops/BUZZ_SECURITY.md."
        ),
    )
    parser.add_argument(
        "--steward-md",
        default=str(DEFAULT_STEWARD_MD),
        help="path to buzz/agents/STEWARD.md (default: repository copy).",
    )
    parser.add_argument(
        "--security-md",
        default=str(DEFAULT_SECURITY_MD),
        help="path to ops/BUZZ_SECURITY.md (default: repository copy).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    print(HEADER)
    settings, config_errors = build_settings(args)
    if config_errors:
        for message in config_errors:
            print(message)
        print("Summary: 0/5 prerequisites evaluated; configuration invalid.")
        print(DO_NOT_ENABLE)
        return 1
    _, steward_drift = parse_steward_profile(settings.steward_md)
    _, runbook_drift = parse_security_runbook(settings.security_md)
    drift = steward_drift + runbook_drift
    if drift:
        for message in drift:
            print(message)
        print("Summary: 0/5 prerequisites evaluated; a source document drifted.")
        print(
            "Reconcile the documents or update scripts/steward_readiness_check.py, "
            "then re-run."
        )
        print(DO_NOT_ENABLE)
        return 1
    results, notes = evaluate(settings)
    for index, title, ok, failures in results:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {index}. {title}")
        for failure in failures:
            print(f"       {failure}")
    for note in notes:
        print(note)
    passed = sum(1 for _, _, ok, _ in results if ok)
    print(f"Summary: {passed}/5 prerequisites satisfied.")
    if passed == len(CHECKS):
        print(
            "All prerequisites are satisfiable from the provided inputs. Retain this "
            "output as readiness evidence for the Steward enablement record "
            "('Steward escalation readiness' in release/OWNER_REVIEW.md). Enabling "
            "the Steward remains a human action."
        )
        return 0
    print(DO_NOT_ENABLE)
    return 1


if __name__ == "__main__":
    sys.exit(main())
