#!/usr/bin/env bash
# Stage (and optionally commit) the public repo — never pushes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMMIT=false
if [[ "${1:-}" == "--commit" ]]; then
  COMMIT=true
elif [[ -n "${1:-}" ]]; then
  echo "Usage: $0 [--commit]" >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: not a git repository — run: git init -b main" >&2
  exit 1
fi

echo "==> submission-check"
make submission-check

if [ -f .env ]; then
  if git check-ignore -q .env 2>/dev/null; then
    :
  else
    echo "ERROR: .env exists but is not gitignored" >&2
    exit 1
  fi
fi

if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  echo "ERROR: .env is tracked — remove from index before publish" >&2
  exit 1
fi

echo "==> stage"
git add -A

if git diff --cached --name-only | grep -qx '.env'; then
  echo "ERROR: .env was staged — aborting" >&2
  git reset HEAD .env 2>/dev/null || true
  exit 1
fi

echo ""
git status
echo ""

STAGED="$(git diff --cached --name-only | wc -l | tr -d ' ')"
if [ "$STAGED" = "0" ]; then
  echo "Nothing staged — working tree clean or already committed."
  exit 0
fi

if [ "$COMMIT" = false ]; then
  echo "Dry run complete ($STAGED paths staged)."
  echo "Create initial commit:  bash scripts/init_public_repo.sh --commit"
  echo "Then push:              see docs/SUBMIT.md §2"
  exit 0
fi

git commit -m "$(cat <<'EOF'
Customs — MCP manifest seal and quarantine demo.

Gate 1–2 passed; make demo and make submission-check green from clean clone.
EOF
)"

echo ""
echo "Initial commit created."
echo "Next: git remote add origin https://github.com/<user>/customs.git"
echo "      git push -u origin main"
echo "See docs/SUBMIT.md"
