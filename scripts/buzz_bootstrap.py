#!/usr/bin/env python3
"""Create and maintain Practice Buzz stream channels without destructive actions."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "buzz" / "community.json"
MARKER_RE = re.compile(r"<!--\s*(practice-seed:[^\s>]+)\s*-->")
SENSITIVE_NAME_RE = re.compile(r"(private[ _-]?key|api[ _-]?key|token|secret|password)", re.I)


class BootstrapError(RuntimeError):
    """An actionable failure that is safe to show in a terminal."""


def redact(value: str, secrets: tuple[str, ...] = ()) -> str:
    """Remove credential values and common credential assignments from diagnostics."""
    redacted = value
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    redacted = re.sub(
        r"(?i)\b(buzz_private_key|api[_-]?key|access[_-]?token|token|secret|password)"
        r"\s*([=:])\s*([^\s,;]+)",
        r"\1\2[REDACTED]",
        redacted,
    )
    return re.sub(r"(https?://)[^\s/@:]+:[^\s/@]+@", r"\1[REDACTED]@", redacted)


def command_label(args: list[str]) -> str:
    return "buzz " + " ".join(args[:2])


def run_buzz(cli: str, args: list[str], *, stdin: str | None, secrets: tuple[str, ...]) -> Any:
    proc = subprocess.run(
        [cli, *args], input=stdin, text=True, capture_output=True, env=os.environ.copy()
    )
    if proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit status {proc.returncode}"
        raise BootstrapError(f"{command_label(args)} failed: {redact(detail, secrets)}")
    output = proc.stdout.strip()
    if not output:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise BootstrapError(
            f"{command_label(args)} returned non-JSON output: {redact(str(exc), secrets)}"
        ) from exc


def mappings(value: Any):
    """Yield mappings from nested JSON envelopes used by current CLI responses."""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from mappings(child)
    elif isinstance(value, list):
        for child in value:
            yield from mappings(child)


def channel_name(channel: dict[str, Any]) -> str | None:
    value = channel.get("name") or channel.get("channel_name")
    return value if isinstance(value, str) and value else None


def records(value: Any) -> list[dict[str, Any]]:
    """Find channel records in direct lists and common data/items/results envelopes."""
    return [
        candidate
        for candidate in mappings(value)
        if channel_name(candidate) is not None
        and any(isinstance(candidate.get(field), str) and candidate[field] for field in ("channel_id", "id", "uuid"))
    ]


def identifier(value: Any, fields: tuple[str, ...]) -> str | None:
    for candidate in mappings(value):
        for field in fields:
            found = candidate.get(field)
            if isinstance(found, str) and found:
                return found
    return None


def channel_id(channel: Any) -> str | None:
    return identifier(channel, ("channel_id", "id", "uuid"))


def flatten_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from flatten_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from flatten_strings(child)


def read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BootstrapError(f"Cannot read {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise BootstrapError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return parsed


def artifact_path(relative: Any, *, channel: str, kind: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise BootstrapError(f"Channel {channel} has no {kind} file path")
    path = (ROOT / relative).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise BootstrapError(f"Channel {channel} {kind} path escapes the repository") from exc
    if not path.is_file():
        raise BootstrapError(f"Channel {channel} {kind} file is missing: {relative}")
    return path


def load_config() -> dict[str, Any]:
    config = read_json(CONFIG)
    channels = config.get("channels")
    if not isinstance(channels, list) or not channels:
        raise BootstrapError("buzz/community.json must contain a non-empty channels list")
    names: set[str] = set()
    for channel in channels:
        if not isinstance(channel, dict):
            raise BootstrapError("Each channel definition must be a JSON object")
        name = channel.get("name")
        if not isinstance(name, str) or not name:
            raise BootstrapError("Each channel needs a non-empty name")
        if name in names:
            raise BootstrapError(f"Duplicate channel name in configuration: {name}")
        names.add(name)
        if channel.get("type") != "stream":
            raise BootstrapError(f"Channel {name} must be type stream for automated seeding")
        if channel.get("visibility") not in {"open", "private"}:
            raise BootstrapError(f"Channel {name} needs visibility open or private")
        for field in ("topic", "purpose"):
            if not isinstance(channel.get(field), str) or not channel[field]:
                raise BootstrapError(f"Channel {name} needs a non-empty {field}")
        artifact_path(channel.get("canvas"), channel=name, kind="canvas")
        seed_path = artifact_path(channel.get("seed"), channel=name, kind="seed")
        if not MARKER_RE.search(seed_path.read_text(encoding="utf-8")):
            raise BootstrapError(f"Channel {name} seed has no practice-seed marker")
    return config


def plan(config: dict[str, Any], skip_seeds: bool) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for channel in config["channels"]:
        name = channel["name"]
        actions.extend([
            {"action": "ensure_channel", "channel": name, "type": "stream", "visibility": channel["visibility"]},
            {"action": "set_topic", "channel": name},
            {"action": "set_purpose", "channel": name},
            {"action": "set_canvas", "channel": name, "source": channel["canvas"]},
        ])
        if not skip_seeds:
            actions.append({"action": "seed_if_marker_missing", "channel": name, "source": channel["seed"]})
    return actions


def channel_index(response: Any) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records(response):
        name = channel_name(record)
        if name:
            indexed[name] = record
    return indexed


def ensure_channel(channel: dict[str, Any], existing: dict[str, dict[str, Any]], cli: str,
                   secrets: tuple[str, ...]) -> tuple[str, str]:
    name = channel["name"]
    current = existing.get(name)
    if current:
        found = channel_id(current)
        if found:
            return found, "exists"
        raise BootstrapError(f"Existing channel {name} has no recognizable channel ID; inspect it in Buzz")
    try:
        created = run_buzz(
            cli,
            ["channels", "create", "--name", name, "--type", "stream", "--visibility", channel["visibility"]],
            stdin=None, secrets=secrets,
        )
    except BootstrapError as create_error:
        # A concurrent successful bootstrap can cause a create conflict. Confirm before proceeding.
        refreshed = channel_index(run_buzz(cli, ["channels", "list"], stdin=None, secrets=secrets))
        current = refreshed.get(name)
        found = channel_id(current) if current else None
        if found:
            return found, "exists_after_create_conflict"
        raise create_error
    found = channel_id(created)
    if not found:
        refreshed = channel_index(run_buzz(cli, ["channels", "list"], stdin=None, secrets=secrets))
        current = refreshed.get(name)
        found = channel_id(current) if current else None
    if not found:
        raise BootstrapError(f"Created channel {name} but could not resolve its ID; inspect it in Buzz")
    return found, "created"


def apply(config: dict[str, Any], cli: str, skip_seeds: bool,
          secrets: tuple[str, ...]) -> list[dict[str, str]]:
    existing = channel_index(run_buzz(cli, ["channels", "list"], stdin=None, secrets=secrets))
    operations: list[dict[str, str]] = []
    for channel in config["channels"]:
        name = channel["name"]
        cid, outcome = ensure_channel(channel, existing, cli, secrets)
        operations.append({"channel": name, "operation": outcome, "channel_id": cid})
        run_buzz(cli, ["channels", "topic", "--channel", cid, "--topic", channel["topic"]], stdin=None, secrets=secrets)
        run_buzz(cli, ["channels", "purpose", "--channel", cid, "--purpose", channel["purpose"]], stdin=None, secrets=secrets)
        canvas = artifact_path(channel["canvas"], channel=name, kind="canvas").read_text(encoding="utf-8")
        run_buzz(cli, ["canvas", "set", "--channel", cid, "--content", "-"], stdin=canvas, secrets=secrets)
        operations.append({"channel": name, "operation": "metadata_and_canvas_set"})
        if skip_seeds:
            operations.append({"channel": name, "operation": "seed_skipped"})
            continue
        seed = artifact_path(channel["seed"], channel=name, kind="seed").read_text(encoding="utf-8")
        marker_match = MARKER_RE.search(seed)
        if not marker_match:
            raise BootstrapError(f"Channel {name} seed has no practice-seed marker")
        marker = marker_match.group(1)
        history = run_buzz(cli, ["messages", "get", "--channel", cid, "--limit", "100"], stdin=None, secrets=secrets)
        if marker in "\n".join(flatten_strings(history)):
            operations.append({"channel": name, "operation": "seed_exists", "marker": marker})
            continue
        sent = run_buzz(cli, ["messages", "send", "--channel", cid, "--content", "-"], stdin=seed, secrets=secrets)
        record = {"channel": name, "operation": "seed_sent", "marker": marker}
        event_id = identifier(sent, ("event_id", "id", "uuid"))
        if event_id:
            record["event_id"] = event_id
        operations.append(record)
    return operations


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run-first, non-destructive Practice Buzz bootstrapper")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="print the plan without Buzz or credentials (default)")
    mode.add_argument("--apply", action="store_true", help="make the listed create/update/send calls")
    parser.add_argument("--skip-seeds", action="store_true", help="do not inspect or send seed messages")
    args = parser.parse_args()
    try:
        config = load_config()
        if not args.apply:
            print(json.dumps({"mode": "dry-run", "config": "buzz/community.json", "actions": plan(config, args.skip_seeds)}, indent=2))
            return 0
        relay = os.environ.get("BUZZ_RELAY_URL", "")
        private_key = os.environ.get("BUZZ_PRIVATE_KEY", "")
        if not relay or not private_key:
            raise BootstrapError("Apply requires non-empty BUZZ_RELAY_URL and BUZZ_PRIVATE_KEY environment variables")
        cli = os.environ.get("BUZZ_CLI", "buzz")
        if not shutil.which(cli):
            raise BootstrapError(f"Buzz CLI not found: {cli}. Install it or set BUZZ_CLI to its executable")
        secrets = tuple(value for key, value in os.environ.items() if SENSITIVE_NAME_RE.search(key) and value)
        operations = apply(config, cli, args.skip_seeds, secrets)
        # stdout is inspectable but avoids persisting relay or credential context in a report file.
        print(json.dumps({"mode": "apply", "applied_at": datetime.now(timezone.utc).isoformat(), "operations": operations}, indent=2))
        return 0
    except BootstrapError as exc:
        print(f"Bootstrap failed: {redact(str(exc))}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
