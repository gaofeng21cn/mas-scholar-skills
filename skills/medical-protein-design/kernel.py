"""Deterministic refs-only helpers for medical protein design.

No design model execution, endpoint call, experimental claim, MAS truth, owner
receipt, typed blocker, or publication-readiness claim lives here.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


AA_RE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWYXBZUO*\-]+$")
AUTHORITY_RE = re.compile(
    r"\b(experimental\s+evidence|domain\s+truth|owner\s+(accepted|receipt)|typed\s+blocker|publication\s+ready)\b",
    re.I,
)


def normalize_design_constraints(constraints: Mapping[str, Any]) -> dict[str, Any]:
    """Return stable design constraints for handoff refs."""

    fixed_positions = sorted({int(value) for value in _as_list(constraints.get("fixed_positions"))})
    allowed_mutations = {
        str(key): sorted({str(item).upper() for item in _as_list(value)})
        for key, value in sorted((constraints.get("allowed_mutations") or {}).items())
    }
    return {
        "design_target_ref": str(constraints.get("design_target_ref") or ""),
        "backbone_or_complex_ref": str(constraints.get("backbone_or_complex_ref") or ""),
        "fixed_positions": fixed_positions,
        "allowed_mutations": allowed_mutations,
        "ligand_context_ref": str(constraints.get("ligand_context_ref") or ""),
        "limitations_ref": str(constraints.get("limitations_ref") or ""),
    }


def design_handoff_skeleton(design_question: str = "") -> dict[str, Any]:
    """Return the refs-only protein-design handoff shell."""

    return {
        "design_question": design_question,
        "design_target_ref": "",
        "backbone_or_complex_ref": "",
        "constraint_ref": "",
        "sequence_candidate_refs": [],
        "design_score_ref": "",
        "embedding_ref": "",
        "fold_back_validation_ref": "",
        "environment_receipt_ref": "",
        "candidate_package_ref": "",
        "execution_receipt_ref": "",
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def summarize_sequence_candidates(sequences: Sequence[str]) -> dict[str, Any]:
    """Return deterministic sequence hygiene metrics for candidate refs."""

    normalized = [re.sub(r"\s+", "", seq or "").upper() for seq in sequences]
    invalid = [seq for seq in normalized if seq and not AA_RE.match(seq)]
    unique = list(dict.fromkeys(normalized))
    return {
        "n_sequences": len(normalized),
        "n_unique": len(unique),
        "lengths": sorted({len(seq) for seq in normalized}),
        "duplicate_count": len(normalized) - len(unique),
        "invalid_sequences": invalid,
        "authority": False,
    }


def lint_forbidden_authority_claims(text: str) -> list[dict[str, str]]:
    """Flag authority drift in protein-design notes."""

    return [{"code": "FORBIDDEN_AUTHORITY_CLAIM", "note": match.group(0)} for match in AUTHORITY_RE.finditer(text or "")]


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value) if isinstance(value, Sequence) else [value]


def _self_check() -> None:
    constraints = normalize_design_constraints({"fixed_positions": ["3", 1], "allowed_mutations": {"2": ["a", "G"]}})
    assert constraints["fixed_positions"] == [1, 3]
    assert constraints["allowed_mutations"]["2"] == ["A", "G"]
    summary = summarize_sequence_candidates(["ACD", "acd", "AC$"])
    assert summary["duplicate_count"] == 1
    assert summary["invalid_sequences"] == ["AC$"]
    assert design_handoff_skeleton("binder")["sequence_candidate_refs"] == []
    assert lint_forbidden_authority_claims("owner accepted")
    print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
