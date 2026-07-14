#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

lane="${1:-fast}"

run_fast() {
  node --test tests/reference-provider-adapters.test.mjs
  python3 scripts/run-kernel-self-checks.py
  python3 scripts/verify-capability-package-manifest.py
  python3 scripts/verify-repository-consistency.py
}

run_render() {
  python3 scripts/verify-display-gallery-pack.py --check
  python3 packs/medical-display-core/src/fenggaolab_org_medical_display_core/live_regression.py
  python3 packs/medical-display-core/tests/render_registry_gallery_templates.py
}

case "$lane" in
  fast)
    run_fast
    ;;
  render)
    run_render
    ;;
  full)
    run_fast
    run_render
    ;;
  *)
    echo "Unknown lane: $lane" >&2
    echo "Usage: scripts/verify.sh [fast|render|full]" >&2
    exit 2
    ;;
esac
