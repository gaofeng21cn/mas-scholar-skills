#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${MAS_SCHOLAR_SKILLS_SKIP_DISPLAY_GALLERY:-0}" != "1" ]]; then
  python3 scripts/verify-display-gallery-pack.py --check
fi

for skill_kernel in skills/*/kernel.py; do
  [[ -e "$skill_kernel" ]] || continue
  python3 "$skill_kernel"
done

python3 scripts/verify-repository-consistency.py
