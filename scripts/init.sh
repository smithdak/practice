#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .git ]]; then
  git init -b main >/dev/null
  git add .
  git commit -m "chore: initialize Practice swarm build kit" >/dev/null
fi

mkdir -p .swarm .worktrees handoffs reviews release brand community docs/framework docs/schemas ops content/launch guides/ai-native-practitioner practices labs stories sources
cp -n .env.example .env 2>/dev/null || true
python3 scripts/taskctl.py init
python3 scripts/validate.py

echo "Practice swarm initialized."
echo "Next: python3 scripts/taskctl.py ready"
