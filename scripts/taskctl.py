#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "tasks" / "manifest.json"
STATE_PATH = ROOT / ".swarm" / "state.json"


def run(cmd: list[str], cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, check=check)


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def task_map() -> dict[str, dict]:
    return {t["id"]: t for t in load_manifest()["tasks"]}


def initial_state() -> dict:
    return {
        "schema_version": 1,
        "tasks": {t["id"]: {"status": "todo"} for t in load_manifest()["tasks"]},
    }


def load_state() -> dict:
    if not STATE_PATH.exists():
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        save_state(initial_state())
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    for tid in task_map():
        state.setdefault("tasks", {}).setdefault(tid, {"status": "todo"})
    return state


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    tmp.replace(STATE_PATH)


def get_task(tid: str) -> dict:
    tasks = task_map()
    if tid not in tasks:
        raise SystemExit(f"Unknown task: {tid}")
    return tasks[tid]


def is_ready(task: dict, state: dict) -> bool:
    if state["tasks"][task["id"]].get("status", "todo") != "todo":
        return False
    return all(state["tasks"].get(dep, {}).get("status") == "done" for dep in task["dependencies"])


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:48]


def cmd_init(_: argparse.Namespace) -> None:
    state = load_state()
    save_state(state)
    print(f"Initialized {len(state['tasks'])} tasks in {STATE_PATH.relative_to(ROOT)}")


def cmd_status(_: argparse.Namespace) -> None:
    manifest = load_manifest()
    state = load_state()
    counts: dict[str, int] = {}
    for t in manifest["tasks"]:
        s = state["tasks"][t["id"]].get("status", "todo")
        counts[s] = counts.get(s, 0) + 1
    print("Practice swarm status")
    for key in ["done", "claimed", "blocked", "todo"]:
        print(f"  {key:8} {counts.get(key, 0)}")
    print("\nActive")
    active = [(tid, rec) for tid, rec in state["tasks"].items() if rec.get("status") in {"claimed", "blocked"}]
    if not active:
        print("  none")
    for tid, rec in active:
        print(f"  {tid:5} {rec.get('status'):8} {rec.get('agent','-'):16} {rec.get('branch','-')}")


def cmd_ready(args: argparse.Namespace) -> None:
    manifest = load_manifest()
    state = load_state()
    ready = [t for t in manifest["tasks"] if is_ready(t, state)]
    if args.wave is not None:
        ready = [t for t in ready if t["wave"] == args.wave]
    if args.json:
        print(json.dumps(ready, indent=2))
        return
    if not ready:
        print("No tasks are currently ready.")
        return
    for t in ready:
        print(f"{t['id']:5} wave={t['wave']} tier={t['model_tier']:8} {t['title']}")


def cmd_show(args: argparse.Namespace) -> None:
    task = get_task(args.task_id)
    print((ROOT / task["spec"]).read_text(encoding="utf-8"))


def render_prompt(task: dict) -> str:
    worker = (ROOT / "prompts" / "WORKER.md").read_text(encoding="utf-8")
    spec = (ROOT / task["spec"]).read_text(encoding="utf-8")
    return f"{worker}\n\n---\n\n{spec}\n"


def cmd_prompt(args: argparse.Namespace) -> None:
    task = get_task(args.task_id)
    content = render_prompt(task)
    if args.output:
        out = Path(args.output)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        print(out)
    else:
        print(content)


def require_clean(path: Path) -> None:
    result = subprocess.run(["git", "status", "--porcelain"], cwd=path, text=True, capture_output=True, check=True)
    if result.stdout.strip():
        raise SystemExit(f"Worktree is not clean: {path}\n{result.stdout}")


def cmd_worktree(args: argparse.Namespace) -> None:
    task = get_task(args.task_id)
    state = load_state()
    rec = state["tasks"][task["id"]]
    if rec.get("status") != "todo":
        raise SystemExit(f"Task {task['id']} is {rec.get('status')}, not todo")
    if not is_ready(task, state):
        missing = [d for d in task["dependencies"] if state["tasks"].get(d, {}).get("status") != "done"]
        raise SystemExit(f"Task {task['id']} is not ready; incomplete dependencies: {', '.join(missing)}")
    require_clean(ROOT)
    branch = f"agent/{task['id'].lower()}-{slug(task['title'])}"
    path = ROOT / ".worktrees" / task["id"]
    if path.exists():
        raise SystemExit(f"Worktree path already exists: {path}")
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    run(["git", "worktree", "add", "-b", branch, str(path), "HEAD"])
    (path / "TASK_PROMPT.md").write_text(render_prompt(task), encoding="utf-8")
    rec.update({
        "status": "claimed",
        "agent": args.agent or "unassigned",
        "branch": branch,
        "worktree": str(path),
        "base_commit": base,
    })
    save_state(state)
    print(path)
    print(f"Branch: {branch}")
    print(f"Prompt: {path / 'TASK_PROMPT.md'}")


def changed_files(base: str, branch: str) -> set[str]:
    out = subprocess.check_output(["git", "diff", "--name-only", f"{base}..{branch}"], cwd=ROOT, text=True)
    return {line.strip() for line in out.splitlines() if line.strip()}


# Modes allowed to touch paths beyond their declared output set. `integration`
# applies reviewed corrections across artifacts; `revision` reworks an existing
# artifact and may need to follow a correction into a neighbouring file.
BROAD_SCOPE_MODES = {"integration", "revision"}


def validate_changed_scope(task: dict, files: set[str]) -> tuple[list[str], list[str]]:
    expected = set(task["outputs"] + [task["handoff"]])
    unchanged = sorted(expected - files)
    unexpected = [] if task.get("mode") in BROAD_SCOPE_MODES else sorted(files - expected)
    return unchanged, unexpected


def verify_task(task: dict, rec: dict, root: Path, require_changed: bool) -> None:
    missing = []
    empty = []
    for rel in task["outputs"] + [task["handoff"]]:
        p = root / rel
        if not p.exists():
            missing.append(rel)
        elif p.is_file() and p.stat().st_size == 0:
            empty.append(rel)
    if missing or empty:
        raise SystemExit(f"Task output failure. Missing={missing}; empty={empty}")
    if require_changed:
        files = changed_files(rec["base_commit"], rec["branch"])
        unchanged, unexpected = validate_changed_scope(task, files)
        if unchanged:
            raise SystemExit(f"Task did not change every owned output: {unchanged}")
        if unexpected:
            raise SystemExit(f"Task changed files outside its owned outputs: {unexpected}")
    run([sys.executable, "scripts/validate.py", "--task", task["id"], "--root", str(root)], cwd=root)


def cmd_verify(args: argparse.Namespace) -> None:
    task = get_task(args.task_id)
    state = load_state()
    rec = state["tasks"][task["id"]]
    root = Path(args.root).resolve() if args.root else Path(rec.get("worktree", ROOT)).resolve()
    verify_task(task, rec, root, require_changed=bool(rec.get("branch") and rec.get("base_commit")))
    print(f"Verified {task['id']} at {root}")


def cmd_integrate(args: argparse.Namespace) -> None:
    task = get_task(args.task_id)
    state = load_state()
    rec = state["tasks"][task["id"]]
    if rec.get("status") != "claimed":
        raise SystemExit(f"Task {task['id']} is {rec.get('status')}, not claimed")
    path = Path(rec["worktree"])
    require_clean(path)
    verify_task(task, rec, path, require_changed=True)
    require_clean(ROOT)
    branch = rec["branch"]
    run(["git", "merge", "--no-ff", branch, "-m", f"merge: {task['id']} {task['title']}"])
    merge_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    rec.update({"status": "done", "merge_commit": merge_commit})
    save_state(state)
    if not args.keep_worktree:
        run(["git", "worktree", "remove", str(path)])
    print(f"Integrated {task['id']} at {merge_commit}")


def cmd_block(args: argparse.Namespace) -> None:
    task = get_task(args.task_id)
    state = load_state()
    rec = state["tasks"][task["id"]]
    rec.update({"status": "blocked", "reason": args.reason})
    save_state(state)
    print(f"Blocked {task['id']}: {args.reason}")


def cmd_reset(args: argparse.Namespace) -> None:
    task = get_task(args.task_id)
    state = load_state()
    rec = state["tasks"][task["id"]]
    path = rec.get("worktree")
    if path and Path(path).exists() and not args.force:
        raise SystemExit("Worktree still exists. Remove it or pass --force after reviewing unmerged work.")
    state["tasks"][task["id"]] = {"status": "todo"}
    save_state(state)
    print(f"Reset {task['id']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Practice swarm task controller")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("init"); p.set_defaults(func=cmd_init)
    p = sub.add_parser("status"); p.set_defaults(func=cmd_status)
    p = sub.add_parser("ready"); p.add_argument("--wave", type=int); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_ready)
    p = sub.add_parser("show"); p.add_argument("task_id"); p.set_defaults(func=cmd_show)
    p = sub.add_parser("prompt"); p.add_argument("task_id"); p.add_argument("--output"); p.set_defaults(func=cmd_prompt)
    p = sub.add_parser("worktree"); p.add_argument("task_id"); p.add_argument("--agent"); p.set_defaults(func=cmd_worktree)
    p = sub.add_parser("verify"); p.add_argument("task_id"); p.add_argument("--root"); p.set_defaults(func=cmd_verify)
    p = sub.add_parser("integrate"); p.add_argument("task_id"); p.add_argument("--keep-worktree", action="store_true"); p.set_defaults(func=cmd_integrate)
    p = sub.add_parser("block"); p.add_argument("task_id"); p.add_argument("--reason", required=True); p.set_defaults(func=cmd_block)
    p = sub.add_parser("reset"); p.add_argument("task_id"); p.add_argument("--force", action="store_true"); p.set_defaults(func=cmd_reset)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
