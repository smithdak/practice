#!/usr/bin/env python3
"""Owner-operated live pilot entrypoint. Never schedules or promotes itself.

The operator must qualify an isolated runtime and authenticate it separately.
--confirm-isolated-runtime records that external prerequisite; it is NOT an
OS sandbox switch. Background activation is deliberately unavailable here.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

from context_pack_codex import (CodexTransport, TransportRefused, DISABLED_FEATURES,
                               SUPPORTED_VERSION, MAX_TIMEOUT_SECONDS)
from context_pack_store import (StoreRefused, prepare_private_root, journal_path,
                                persist_report, _existing_components, _safe_id)
from context_pack_trial import (Session, Refused, load_cases, digest,
                                PILOT_MODEL, PILOT_REASONING_EFFORT)


def source_hash(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def bind_transport(session, contract):
    """Do not vary the live adapter or limits inside a paired experiment."""
    binding = digest(contract)
    with session.db:
        session.db.execute("CREATE TABLE IF NOT EXISTS transport_binding (id INTEGER PRIMARY KEY, binding TEXT NOT NULL)")
        session.db.execute("INSERT OR IGNORE INTO transport_binding VALUES (1, ?)", (binding,))
        if session.db.execute("SELECT binding FROM transport_binding WHERE id=1").fetchone()[0] != binding:
            raise Refused("Transport contract changed; do not rewrite the current session")


def run_supervised(root, private_root, config, trial_id, case_id, transport, contract,
                   clock=lambda: datetime.now(timezone.utc)):
    """Trusted integration seam, exercised with synthetic transports in CI."""
    if config.get("accounting") != "requests" or config.get("lane") != "supervised":
        raise Refused("This entrypoint only supports owner-driven request-accounted trials")
    _safe_id(config["session_id"], "session ID")
    _safe_id(trial_id, "trial ID")
    private_root = prepare_private_root(Path(private_root), Path(root).resolve())
    path = journal_path(private_root, config["session_id"])
    stop_path = path.parent / "STOP"
    _existing_components(stop_path)
    def gate():
        _existing_components(stop_path)
        return not stop_path.exists()
    session = Session(path, config, load_cases(root))
    try:
        bind_transport(session, contract)
        result = session.run_trial(trial_id, case_id, transport, gate, clock)
        result["transport_contract"] = contract
        target = persist_report(private_root, config["session_id"], trial_id, result)
        return target, result
    finally:
        session.close()


def stop_session(private_root, session_id):
    """Persistent owner stop. It does not refund/reconcile any pending call."""
    private_root = Path(private_root)
    _safe_id(session_id, "session ID")
    directory = private_root / "sessions" / session_id
    _existing_components(directory)
    if not directory.is_dir():
        raise Refused("No existing private session to stop")
    path = journal_path(private_root, session_id)
    if not path.is_file():
        raise Refused("No existing private journal to stop")
    marker = directory / "STOP"
    _existing_components(marker)
    try:
        with marker.open("x", encoding="utf-8") as stream:
            stream.write("Owner requested stop. Pending provider outcomes remain uncertain.\n")
    except FileExistsError:
        pass
    database = sqlite3.connect(path, timeout=5)
    try:
        with database:
            database.execute("UPDATE meta SET stopped=1 WHERE id=1")
    finally:
        database.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preflight", "run", "stop"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--private-root", type=Path)
    parser.add_argument("--session-id")
    parser.add_argument("--trial-id")
    parser.add_argument("--case-id")
    parser.add_argument("--start-date", help="fixed UTC date for the seven-day session; required for run")
    parser.add_argument("--session-invocation-cap", type=int, default=21,
                        help="local invocations per owner session, not a daily or exact credit cap")
    parser.add_argument("--codex-executable", type=Path)
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--confirm-isolated-runtime", action="store_true",
                        help="owner attests external isolation was verified; this flag cannot create isolation")
    parser.add_argument("--approve-live-trial", action="store_true",
                        help="explicit owner approval for this one foreground trial; consumes ChatGPT usage")
    args = parser.parse_args(argv)
    try:
        if args.action == "stop":
            if not args.private_root or not args.session_id:
                parser.error("stop requires --private-root and --session-id")
            # Refuse canonical/ancestor targets before touching the existing session.
            if not args.private_root.is_dir():
                raise Refused("No existing private root to stop")
            private = prepare_private_root(args.private_root, args.root.resolve())
            stop_session(private, args.session_id)
            print("Session stopped. Pending calls were not retried or refunded.")
            return 0
        if args.action == "run" and not args.approve_live_trial:
            raise Refused("Live trial requires explicit --approve-live-trial; no model was invoked")
        if not all((args.codex_executable, args.runtime_root, args.codex_home)):
            raise Refused("Identify an isolated runtime, its native Codex executable, and separately authenticated Codex home")
        if not 0 < args.timeout_seconds <= MAX_TIMEOUT_SECONDS:
            raise Refused("Timeout must be between 1 and 300 seconds")
        if args.action == "run" and not all((args.private_root, args.session_id, args.trial_id, args.case_id, args.start_date)):
            parser.error("run requires --private-root, --session-id, --trial-id, --case-id, and --start-date")
        stop_path = None
        if args.action == "run":
            _safe_id(args.session_id, "session ID")
            _safe_id(args.trial_id, "trial ID")
            # Never make the durable journal accessible through the model cwd.
            runtime, private = args.runtime_root.resolve(), args.private_root.resolve()
            if private.is_relative_to(runtime) or runtime.is_relative_to(private):
                raise Refused("Private journal and model runtime roots must not overlap")
            stop_path = private / "sessions" / args.session_id / "STOP"
        def cancelled():
            if stop_path is None:
                return False
            _existing_components(stop_path)
            return stop_path.exists()
        adapter = CodexTransport(args.codex_executable, args.runtime_root, args.codex_home,
            isolated_runtime_confirmed=args.confirm_isolated_runtime,
            timeout_seconds=args.timeout_seconds, cancel=cancelled)
        readiness = adapter.preflight()
        if args.action == "preflight":
            print(json.dumps(readiness, indent=2))
            return 0 if readiness["ready_for_supervised_run"] else 1
        if not readiness["ready_for_supervised_run"]:
            raise Refused("Isolated runtime qualification or ChatGPT authentication remains incomplete")
        config = {"session_id": args.session_id, "start_date": args.start_date, "mode": "live",
                  "model": PILOT_MODEL, "reasoning_effort": PILOT_REASONING_EFFORT,
                  "accounting": "requests", "lane": "supervised",
                  "session_invocation_cap": args.session_invocation_cap}
        contract = {"provider": "codex-chatgpt", "cli_version": SUPPORTED_VERSION,
                    "executable_sha256": source_hash(args.codex_executable),
                    "adapter_sha256": source_hash(Path(__file__).with_name("context_pack_codex.py")),
                    "timeout_seconds": args.timeout_seconds, "disabled_features": list(DISABLED_FEATURES),
                    "runtime_identity_sha256": digest([str(adapter.runtime_root), str(adapter.codex_home)]),
                    "isolation": "owner-confirmed-external-boundary-not-verified-by-cli",
                    "usage_limit": "local-invocations-not-exact-provider-quota"}
        target, report = run_supervised(args.root, args.private_root, config, args.trial_id,
                                       args.case_id, adapter, contract)
        print(f"Supervised trial retained: {target}")
        print(f"Local session invocations: {report['session_invocations']}/{report['session_invocation_cap']}. "
              "Not a scheduled daily cycle or a publication decision.")
        return 0
    except (Refused, StoreRefused, TransportRefused) as exc:
        print(f"Refused: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Cancelled. Any pending invocation remains uncertain; do not retry blindly.", file=sys.stderr)
        return 130
    except (OSError, sqlite3.Error, ValueError):
        print("Private runtime failed; inspect local state before any retry. No automatic recovery attempted.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
