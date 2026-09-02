#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .git ]]; then
  git init -b main >/dev/null
  git add .
  git commit -m "chore: initialize Practice swarm build kit" >/dev/null
fi

mkdir -p .taskctl .worktrees swarm/handoffs swarm/specs reviews release community docs/framework docs/schemas docs/style ops/outreach guides/ai-native-practitioner practices labs stories notes projects
cp -n .env.example .env 2>/dev/null || true
python3 scripts/taskctl.py init
python3 scripts/validate.py

echo "Practice swarm initialized."
echo "Next: python3 scripts/taskctl.py ready"
