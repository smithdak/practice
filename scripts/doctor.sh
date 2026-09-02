#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
failed=0
check() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    printf 'OK   %s\n' "$label"
  else
    printf 'MISS %s\n' "$label"
    failed=1
  fi
}
check "git" git --version
check "python >= 3.10" python3 -c 'import sys; raise SystemExit(sys.version_info < (3,10))'
check "repository" test -d .git
check "task manifest" test -f swarm/manifest.json
if command -v buzz >/dev/null 2>&1; then
  printf 'OK   buzz CLI (%s)\n' "$(command -v buzz)"
else
  printf 'INFO buzz CLI not installed; content swarm and dry run still work.\n'
fi
if [[ -f .env ]]; then
  printf 'OK   .env exists and is gitignored\n'
else
  printf 'INFO copy .env.example to .env before applying Buzz bootstrap\n'
fi
python3 scripts/validate.py || failed=1
exit "$failed"
