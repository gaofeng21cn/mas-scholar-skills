"""Deterministic helper for display regression diagnostic refs."""

from __future__ import annotations

import re
from typing import Any


DISPLAY_REFS = (
    "display_regression_symptom_ref",
    "artifact_diff_ref",
    "renderer_path_ref",
    "source_renderer_boundary_ref",
    "reproduction_probe_ref",
    "repair_route_ref",
)


def artifact_diff_row(current_ref: str, prior_ref: str, symptom: str) -> dict[str, Any]:
    return {
        "current_artifact_ref": current_ref.strip(),
        "prior_artifact_ref": prior_ref.strip(),
        "symptom": symptom.strip(),
        "requires_owner_repair": True,
        "writes_authority": False,
    }


def display_regression_skeleton(artifact_ref: str) -> dict[str, Any]:
    return {
        "surface_kind": "display_regression_diagnostic_candidate",
        "artifact_ref": artifact_ref,
        "required_refs": list(DISPLAY_REFS),
        "candidate_refs": {ref: None for ref in DISPLAY_REFS},
        "route_back_candidate": None,
        "owner_gate_handoff_ref": None,
        "authority": {
            "refs_only": True,
            "can_mutate_artifacts": False,
            "can_write_mas_truth": False,
            "can_sign_owner_receipt": False,
            "can_create_typed_blocker": False,
            "can_claim_publication_readiness": False,
        },
    }


def lint_forbidden_display_claims(text: str) -> list[str]:
    patterns = (
        r"\bartifact fixed\b",
        r"\bvisual audit receipt\b",
        r"\bowner receipt\b",
        r"\btyped blocker\b",
        r"\bpublication-ready\b",
    )
    return [pattern for pattern in patterns if re.search(pattern, text, flags=re.I)]


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = str(Path(__file__).resolve().parents[2])
    if _root not in sys.path:
        sys.path.insert(0, _root)
    from runtime.kernel_validation import delegate_self_check
    raise SystemExit(delegate_self_check("medical-display-regression-debugger", kernel_file=__file__))
