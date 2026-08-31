#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'buzz' / 'community.json'
REPORT = ROOT / 'buzz' / 'bootstrap-report.json'


def flatten_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from flatten_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from flatten_strings(v)


def run_buzz(cli: str, args: list[str], stdin: str | None = None) -> Any:
    env = os.environ.copy()
    proc = subprocess.run([cli, *args], input=stdin, text=True, capture_output=True, env=env)
    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip() or f'exit {proc.returncode}'
        raise RuntimeError(f"buzz {' '.join(args[:2])} failed: {err}")
    out = proc.stdout.strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Buzz returned non-JSON output for {' '.join(args)}: {exc}") from exc


def items(value: Any) -> list[dict]:
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    if isinstance(value, dict):
        for key in ('channels','items','data','results'):
            if isinstance(value.get(key), list):
                return [x for x in value[key] if isinstance(x, dict)]
        return [value]
    return []


def channel_name(ch: dict) -> str | None:
    return ch.get('name') or ch.get('channel_name')


def channel_id(ch: dict) -> str | None:
    return ch.get('channel_id') or ch.get('id') or ch.get('uuid')


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding='utf-8'))


def plan(config: dict) -> list[dict]:
    actions = []
    for c in config['channels']:
        actions.extend([
            {'action':'ensure_channel','name':c['name'],'type':c['type'],'visibility':c['visibility']},
            {'action':'set_topic','name':c['name'],'topic':c['topic']},
            {'action':'set_purpose','name':c['name'],'purpose':c['purpose']},
            {'action':'set_canvas','name':c['name'],'file':c['canvas']},
            {'action':'seed_once','name':c['name'],'file':c['seed']},
        ])
    return actions


def apply(config: dict, cli: str, skip_seeds: bool) -> list[dict]:
    existing_raw = run_buzz(cli, ['channels','list'])
    existing = {channel_name(c): c for c in items(existing_raw) if channel_name(c)}
    report = []
    for c in config['channels']:
        current = existing.get(c['name'])
        if not current:
            created = run_buzz(cli, ['channels','create','--name',c['name'],'--type',c['type'],'--visibility',c['visibility']])
            cid = channel_id(created if isinstance(created, dict) else {})
            if not cid:
                refreshed = run_buzz(cli, ['channels','list'])
                match = next((x for x in items(refreshed) if channel_name(x) == c['name']), None)
                cid = channel_id(match or {})
            if not cid:
                raise RuntimeError(f"Created channel {c['name']} but could not resolve its id")
            report.append({'channel':c['name'],'operation':'created','channel_id':cid})
        else:
            cid = channel_id(current)
            if not cid:
                raise RuntimeError(f"Existing channel {c['name']} has no recognizable id")
            report.append({'channel':c['name'],'operation':'exists','channel_id':cid})

        run_buzz(cli, ['channels','topic','--channel',cid,'--topic',c['topic']])
        run_buzz(cli, ['channels','purpose','--channel',cid,'--purpose',c['purpose']])
        canvas = (ROOT / c['canvas']).read_text(encoding='utf-8')
        run_buzz(cli, ['canvas','set','--channel',cid,'--content','-'], stdin=canvas)
        report.append({'channel':c['name'],'operation':'metadata_canvas_set'})

        if skip_seeds:
            continue
        seed = (ROOT / c['seed']).read_text(encoding='utf-8')
        marker = next((line.strip() for line in seed.splitlines() if 'practice-seed:' in line), None)
        history = run_buzz(cli, ['messages','get','--channel',cid,'--limit','100'])
        haystack = '\n'.join(flatten_strings(history))
        if marker and marker in haystack:
            report.append({'channel':c['name'],'operation':'seed_exists','marker':marker})
        else:
            sent = run_buzz(cli, ['messages','send','--channel',cid,'--content','-'], stdin=seed)
            report.append({'channel':c['name'],'operation':'seed_sent','event_id': sent.get('event_id') if isinstance(sent,dict) else None})
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description='Idempotent Practice Buzz bootstrapper')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--apply', action='store_true')
    parser.add_argument('--skip-seeds', action='store_true')
    args = parser.parse_args()
    config = load_config()
    if not args.apply:
        print(json.dumps({'mode':'dry-run','config':str(CONFIG.relative_to(ROOT)),'actions':plan(config)}, indent=2))
        return
    relay = os.environ.get('BUZZ_RELAY_URL')
    key = os.environ.get('BUZZ_PRIVATE_KEY')
    cli = os.environ.get('BUZZ_CLI','buzz')
    if not relay or not key:
        raise SystemExit('Apply requires BUZZ_RELAY_URL and BUZZ_PRIVATE_KEY in the environment.')
    if not shutil.which(cli):
        raise SystemExit(f'Buzz CLI not found: {cli}')
    result = apply(config, cli, args.skip_seeds)
    payload = {
        'applied_at': datetime.now(timezone.utc).isoformat(),
        'relay': relay,
        'operations': result,
    }
    REPORT.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(payload, indent=2))

if __name__ == '__main__':
    main()
