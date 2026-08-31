#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SEED_RE = re.compile(r"<!--\s*practice-seed:([^\s]+)\s*-->")


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_json(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(errors, f"Invalid JSON {path}: {exc}")
        return None


def validate_manifest(root: Path, errors: list[str]) -> dict | None:
    path = root / "tasks" / "manifest.json"
    manifest = load_json(path, errors)
    if not manifest:
        return None
    tasks = manifest.get("tasks", [])
    ids = [t.get("id") for t in tasks]
    if len(ids) != len(set(ids)):
        fail(errors, "Duplicate task IDs")
    known = set(ids)
    owners: dict[str, str] = {}
    for t in tasks:
        for dep in t.get("dependencies", []):
            if dep not in known:
                fail(errors, f"{t['id']} depends on unknown task {dep}")
        spec = root / t.get("spec", "")
        if not spec.exists():
            fail(errors, f"Missing task spec for {t['id']}: {spec}")
        if t.get("mode") == "build":
            for out in t.get("outputs", []):
                if out in owners:
                    fail(errors, f"Output collision: {out} owned by {owners[out]} and {t['id']}")
                owners[out] = t["id"]
    # Cycle check
    graph = {t["id"]: t.get("dependencies", []) for t in tasks}
    visiting, visited = set(), set()
    def dfs(node: str):
        if node in visiting:
            fail(errors, f"Dependency cycle includes {node}")
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in graph.get(node, []):
            dfs(dep)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        dfs(node)
    return manifest


def validate_buzz(root: Path, errors: list[str]) -> None:
    cfg = load_json(root / "buzz" / "community.json", errors)
    if not cfg:
        return
    names = set()
    markers = set()
    for c in cfg.get("channels", []):
        name = c.get("name")
        if not name or name in names:
            fail(errors, f"Missing or duplicate Buzz channel name: {name}")
        names.add(name)
        if c.get("type") != "stream":
            fail(errors, f"Launch channel {name} is not stream")
        for key in ("canvas", "seed"):
            p = root / c.get(key, "")
            if not p.exists():
                fail(errors, f"Buzz channel {name} missing {key}: {p}")
        seed = root / c.get("seed", "")
        if seed.exists():
            found = SEED_RE.findall(seed.read_text(encoding="utf-8"))
            if len(found) != 1:
                fail(errors, f"Seed {seed} must contain exactly one idempotency marker")
            elif found[0] in markers:
                fail(errors, f"Duplicate seed marker: {found[0]}")
            else:
                markers.add(found[0])


def validate_links(root: Path, errors: list[str]) -> None:
    ignored = {'.worktrees', '.swarm', '.git'}
    for p in root.rglob("*.md"):
        if any(part in ignored for part in p.parts):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for target in LINK_RE.findall(text):
            target = target.strip().split('#', 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:", "buzz://")):
                continue
            candidate = (p.parent / target).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                fail(errors, f"Link escapes repository: {p} -> {target}")
                continue
            if not candidate.exists():
                fail(errors, f"Broken relative link: {p.relative_to(root)} -> {target}")


def validate_task(root: Path, manifest: dict, task_id: str, errors: list[str]) -> None:
    tasks = {t['id']: t for t in manifest['tasks']}
    if task_id not in tasks:
        fail(errors, f"Unknown task {task_id}")
        return
    task = tasks[task_id]
    for rel in task.get('outputs', []) + [task.get('handoff')]:
        p = root / rel
        if not p.exists():
            fail(errors, f"Task {task_id} missing output {rel}")
        elif p.is_file() and p.stat().st_size == 0:
            fail(errors, f"Task {task_id} empty output {rel}")


def validate_release(root: Path, manifest: dict, errors: list[str]) -> None:
    state_path = root / '.swarm' / 'state.json'
    if not state_path.exists():
        fail(errors, 'Release validation requires .swarm/state.json')
    else:
        state = load_json(state_path, errors) or {}
        incomplete = [tid for tid, rec in state.get('tasks', {}).items() if rec.get('status') != 'done']
        if incomplete:
            fail(errors, f"Release has incomplete tasks: {', '.join(incomplete)}")
    required = [
        'docs/founding/MANIFESTO.md', 'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md',
        'community/GOVERNANCE.md', 'community/ONBOARDING.md',
        'guides/ai-native-practitioner/CURRICULUM.md',
        'practices/001-context-pack.md', 'practices/002-workflow-redesign.md',
        'practices/003-verification-gate.md', 'release/OWNER_REVIEW.md',
        'release/FINAL_INTEGRATION_REPORT.md',
    ]
    for rel in required:
        if not (root / rel).exists():
            fail(errors, f"Release missing required artifact: {rel}")
    placeholder_re = re.compile(r"\b(TODO|TBD|PLACEHOLDER|LOREM IPSUM)\b", re.I)
    public_roots = ['docs','community','guides','practices','labs','stories','content','ops','release','brand']
    for base in public_roots:
        d = root / base
        if not d.exists():
            continue
        for p in d.rglob('*.md'):
            if p.name.startswith('SAMPLE_'):
                continue
            text = p.read_text(encoding='utf-8', errors='replace')
            if placeholder_re.search(text):
                fail(errors, f"Release placeholder found in {p.relative_to(root)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=str(DEFAULT_ROOT))
    parser.add_argument('--task')
    parser.add_argument('--release', action='store_true')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []
    required = ['README.md','AGENTS.md','CONTEXT.md','DECISIONS.md','SWARM_PLAN.md','tasks/manifest.json','buzz/community.json']
    for rel in required:
        if not (root / rel).exists():
            fail(errors, f"Missing required file: {rel}")
    manifest = validate_manifest(root, errors)
    validate_buzz(root, errors)
    validate_links(root, errors)
    if args.task and manifest:
        validate_task(root, manifest, args.task, errors)
    if args.release and manifest:
        validate_release(root, manifest, errors)
    if errors:
        print('Validation failed:', file=sys.stderr)
        for error in errors:
            print(f'- {error}', file=sys.stderr)
        raise SystemExit(1)
    print('Validation passed.')

if __name__ == '__main__':
    main()
