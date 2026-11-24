#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

lane="${1:-fast}"

run_fast() {
  node --test tests/codex-plugin-marketplace.test.mjs
  node --test tests/reference-provider-adapters.test.mjs
  node --test tests/scientific-search-adapters.test.mjs
  uv run --frozen pytest -q
  uv run --frozen python scripts/verify-professional-figure-workflow.py --self-test
  uv run --frozen python scripts/verify-publication-layout-profiles.py
  uv run --frozen python scripts/verify-capability-package-manifest.py
}

run_render() {
  uv run --frozen --extra render python tests/display-layout-acceptance.py
  uv run --frozen python scripts/verify-display-gallery-pack.py --check
  uv run --frozen python packs/medical-display-core/src/fenggaolab_org_medical_display_core/live_regression.py
  uv run --frozen python packs/medical-display-core/tests/render_registry_gallery_templates.py
  Rscript --vanilla packs/medical-display-core/tests/test_cohort_flow_heading_overrides.R
  Rscript --vanilla packs/medical-display-core/tests/test_render_session.R
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
