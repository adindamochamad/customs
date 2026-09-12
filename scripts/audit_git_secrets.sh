#!/usr/bin/env bash
# Fail if tracked files look like they contain real secrets.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "WARN: not a git repository — skipping history audit"
  exit 0
fi

if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  echo "ERROR: .env is tracked by git" >&2
  exit 1
fi

PATTERN='(sk-[a-zA-Z0-9]{20,}|OPENAI_API_KEY=sk-|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36})'
MATCHES="$(git grep -nE "$PATTERN" -- \
  ':!demo/.env.demo' \
  ':!docs/SUBMISSION.md' \
  ':!scripts/audit_git_secrets.sh' \
  || true)"

if [ -n "$MATCHES" ]; then
  echo "ERROR: possible secrets in tracked files:" >&2
  echo "$MATCHES" >&2
  exit 1
fi

if git rev-parse HEAD >/dev/null 2>&1; then
  HISTORY="$(git log --all -p -E --regexp-ignore-case \
    -e 'sk-[a-zA-Z0-9]{20,}' -e 'AKIA[0-9A-Z]{16}' -e 'ghp_[a-zA-Z0-9]{36}' 2>/dev/null | head -20 || true)"
  if [ -n "$HISTORY" ]; then
    echo "ERROR: possible secrets in git history (first 20 lines):" >&2
    echo "$HISTORY" >&2
    exit 1
  fi
fi

echo "Git secret audit passed"
