"""Deterministic refs-only helpers for medical structural biology.

These helpers shape candidate refs and confidence diagnostics only. They do
not run folding/docking models, mutate artifacts, or claim MAS authority.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any


AA_RE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWYXBZUO*\-]+$")
AUTHORITY_RE = re.compile(
    r"\b(publication\s+ready|owner\s+(accepted|receipt)|typed\s+blocker|clinical\s+interpretation|quality\s+verdict)\b",
    re.I,
)


def normalize_sequence(sequence: str) -> str:
    """Normalize an amino-acid sequence string for refs-only input hygiene."""

    cleaned = re.sub(r"\s+", "", sequence or "").upper()
    if cleaned and not AA_RE.match(cleaned):
        raise ValueError("sequence contains non-amino-acid symbols")
    return cleaned


def structure_candidate_skeleton(structural_question: str = "") -> dict[str, Any]:
    """Return the standard structure/docking candidate handoff shell."""

    return {
        "structural_question": structural_question,
        "sequence_input_ref": "",
        "ligand_input_ref": "",
        "model_selection_ref": "",
        "environment_receipt_ref": "",
        "structure_candidate_ref": "",
        "docking_candidate_ref": "",
        "confidence_metrics_ref": "",
        "model_output_manifest_ref": "",
        "candidate_refs": [],
        "failure_or_warning_ref": "",
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def summarize_confidence_metrics(metrics: Mapping[str, Any]) -> dict[str, Any]:
    """Summarize confidence metrics without accepting or rejecting a model."""

    values = {key: _float_or_none(metrics.get(key)) for key in ("plddt", "ptm", "iptm", "pae_mean")}
    warnings = []
    if values["plddt"] is not None and values["plddt"] < 70:
        warnings.append("low_plddt")
    if values["iptm"] is not None and values["iptm"] < 0.6:
        warnings.append("low_iptm")
    if values["pae_mean"] is not None and values["pae_mean"] > 10:
        warnings.append("high_pae_mean")
    return {"metrics": values, "warnings": warnings, "authority": False}


def model_output_manifest_skeleton(output_refs: Sequence[str] | None = None) -> dict[str, Any]:
    """Return a deterministic model-output manifest ref skeleton."""

    return {
        "ref_kind": "structural_model_output_manifest_ref",
        "authority": False,
        "output_refs": list(output_refs or []),
        "confidence_metrics_ref": "",
        "limitations_ref": "",
        "owner_gate_handoff_ref": "",
    }


def lint_forbidden_authority_claims(text: str) -> list[dict[str, str]]:
    """Flag authority drift in structure/docking notes."""

    return [{"code": "FORBIDDEN_AUTHORITY_CLAIM", "note": match.group(0)} for match in AUTHORITY_RE.finditer(text or "")]


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = str(Path(__file__).resolve().parents[2])
    if _root not in sys.path:
        sys.path.insert(0, _root)
    from runtime.kernel_validation import delegate_self_check
    raise SystemExit(delegate_self_check("medical-structural-biology", kernel_file=__file__))
