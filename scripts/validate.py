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
HANDOFF_STATUS_RE = re.compile(r"^## Status\s*\n+\s*(COMPLETE|BLOCKED)\s*$", re.MULTILINE)
UNFINISHED_RE = re.compile(r"\b(TODO|TBD|LOREM IPSUM)\b", re.IGNORECASE)
PUBLICATION_TOKEN_RE = re.compile(r"\[[@#]?[A-Z][A-Z0-9_ -]*\](?!\()")
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
REUSABLE_PUBLICATION_TEMPLATES = {
    "ops/outreach/SOCIAL_KIT.md",
}


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def load_json(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(errors, f"Invalid JSON {path}: {exc}")
        return None


def validate_manifest(root: Path, errors: list[str]) -> dict | None:
    path = root / "swarm" / "manifest.json"
    manifest = load_json(path, errors)
    if not manifest:
        return None
    tasks = manifest.get("tasks", [])
    ids = [t.get("id") for t in tasks]
    if len(ids) != len(set(ids)):
        fail(errors, "Duplicate task IDs")
    known = set(ids)
    # Exclusive path ownership is enforced within a mode, not across modes: a
    # `build` task creates an artifact, and a later-phase `revision` task may be
    # the sole owner of edits to that same artifact. Two `build` tasks may never
    # own one path. Two `revision` tasks may never own one path in the same
    # wave; revisions of one file in different waves are sequential corrections,
    # each recorded in its own handoff, not a race for the working tree.
    owners: dict[str, dict[str, str]] = {"build": {}}
    revision_owners: dict[object, dict[str, str]] = {}
    for t in tasks:
        for dep in t.get("dependencies", []):
            if dep not in known:
                fail(errors, f"{t['id']} depends on unknown task {dep}")
        spec = root / t.get("spec", "")
        if not spec.exists():
            fail(errors, f"Missing task spec for {t['id']}: {spec}")
        mode = t.get("mode")
        bucket = None
        if mode in owners:
            bucket = owners[mode]
        elif mode == "revision":
            bucket = revision_owners.setdefault(t.get("wave"), {})
        if bucket is not None:
            for out in t.get("outputs", []):
                if out in bucket:
                    fail(errors, f"Output collision: {out} owned by {bucket[out]} and {t['id']}")
                bucket[out] = t["id"]
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
    ignored = {'.worktrees', '.taskctl', '.git'}
    for p in root.rglob("*.md"):
        relative = p.relative_to(root)
        if any(part in ignored for part in relative.parts):
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
                fail(errors, f"Broken relative link: {relative} -> {target}")


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


def validate_committed_task_evidence(root: Path, manifest: dict, errors: list[str]) -> None:
    """Validate release completion from files reproducible in a clean checkout."""
    for task in manifest.get("tasks", []):
        task_id = task.get("id", "<unknown>")
        for rel in task.get("outputs", []) + [task.get("handoff")]:
            if not rel:
                fail(errors, f"Task {task_id} has an empty release evidence path")
                continue
            path = root / rel
            if not path.is_file():
                fail(errors, f"Release task {task_id} missing committed evidence: {rel}")
            elif path.stat().st_size == 0:
                fail(errors, f"Release task {task_id} has empty committed evidence: {rel}")
        handoff_path = root / task.get("handoff", "")
        if handoff_path.is_file():
            match = HANDOFF_STATUS_RE.search(handoff_path.read_text(encoding="utf-8", errors="replace"))
            if not match:
                fail(errors, f"Release task {task_id} handoff has no recognized Status: {task.get('handoff')}")
            elif match.group(1) != "COMPLETE":
                fail(errors, f"Release task {task_id} handoff is {match.group(1)}: {task.get('handoff')}")


def validate_publication_tokens(relative: str, text: str, errors: list[str]) -> None:
    visible_prose = INLINE_CODE_RE.sub("", FENCED_CODE_RE.sub("", text))
    if UNFINISHED_RE.search(visible_prose):
        fail(errors, f"Release unfinished token found in {relative}")
    if relative not in REUSABLE_PUBLICATION_TEMPLATES and PUBLICATION_TOKEN_RE.search(visible_prose):
        fail(errors, f"Release publication token found outside an approved template: {relative}")


def validate_release(root: Path, manifest: dict, errors: list[str]) -> None:
    validate_committed_task_evidence(root, manifest, errors)
    required = [
        'docs/founding/MANIFESTO.md', 'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md',
        'community/GOVERNANCE.md', 'community/ONBOARDING.md',
        'guides/ai-native-practitioner/CURRICULUM.md',
        'practices/001-context-pack.md', 'practices/002-workflow-redesign.md',
        'practices/003-verification-gate.md', 'release/OWNER_REVIEW.md',
        'swarm/reports/PHASE1_REPORT.md',
    ]
    for rel in required:
        if not (root / rel).exists():
            fail(errors, f"Release missing required artifact: {rel}")
    public_roots = ['docs','community','guides','practices','labs','stories','notes','projects','ops','release']
    for base in public_roots:
        d = root / base
        if not d.exists():
            continue
        for p in d.rglob('*.md'):
            if p.name.startswith('SAMPLE_'):
                continue
            text = p.read_text(encoding='utf-8', errors='replace')
            relative = p.relative_to(root).as_posix()
            validate_publication_tokens(relative, text, errors)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=str(DEFAULT_ROOT))
    parser.add_argument('--task')
    parser.add_argument('--release', action='store_true')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []
    required = ['README.md','AGENTS.md','docs/CONTEXT.md','docs/DECISIONS.md','swarm/plans/PHASE1_PLAN.md','swarm/manifest.json','buzz/community.json']
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
