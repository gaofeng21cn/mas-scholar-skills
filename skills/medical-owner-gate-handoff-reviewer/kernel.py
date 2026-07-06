"""Deterministic helper for owner-gate handoff review refs."""

from __future__ import annotations

import re
from typing import Any


HANDOFF_REFS = (
    "handoff_inventory_ref",
    "authority_boundary_ref",
    "evidence_to_owner_map_ref",
    "candidate_package_consistency_ref",
    "residual_risk_ref",
)


def evidence_to_owner_row(evidence_ref: str, owner_question: str, route_back_target: str) -> dict[str, Any]:
    return {
        "evidence_ref": evidence_ref.strip(),
        "owner_question": owner_question.strip(),
        "route_back_target": route_back_target.strip(),
        "owner_decision_required": True,
        "writes_authority": False,
    }


def handoff_review_skeleton(package_ref: str, owner_surface_ref: str) -> dict[str, Any]:
    return {
        "surface_kind": "owner_gate_handoff_review_candidate",
        "candidate_package_ref": package_ref,
        "owner_surface_ref": owner_surface_ref,
        "required_refs": list(HANDOFF_REFS),
        "candidate_refs": {ref: None for ref in HANDOFF_REFS},
        "route_back_candidate": None,
        "owner_gate_handoff_ref": None,
        "authority": {
            "refs_only": True,
            "can_accept_handoff": False,
            "can_write_mas_truth": False,
            "can_sign_owner_receipt": False,
            "can_create_typed_blocker": False,
            "can_claim_readiness": False,
        },
    }


def lint_forbidden_handoff_claims(text: str) -> list[str]:
    patterns = (
        r"\bhandoff accepted\b",
        r"\bowner receipt\b",
        r"\btyped blocker\b",
        r"\bpublication-ready\b",
        r"\bcurrent package\b",
    )
    return [pattern for pattern in patterns if re.search(pattern, text, flags=re.I)]


def _self_check() -> None:
    row = evidence_to_owner_row("ref:a", "accept?", "owner:study")
    assert row["owner_decision_required"] is True
    skeleton = handoff_review_skeleton("pkg:a", "owner:surface")
    assert skeleton["authority"]["can_accept_handoff"] is False
    assert "residual_risk_ref" in skeleton["required_refs"]
    assert lint_forbidden_handoff_claims("handoff accepted with owner receipt")
    print({"checks": 4, "ok": True})


if __name__ == "__main__":
    _self_check()
