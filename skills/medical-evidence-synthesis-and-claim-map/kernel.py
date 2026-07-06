"""Deterministic refs-only helpers for evidence synthesis and claim maps.

These helpers scaffold candidate matrices and lint labels. They do not accept
citations, issue verdicts, sign receipts, create blockers, or claim readiness.
"""

from __future__ import annotations

import json
from typing import Iterable, Mapping


SUPPORT_STRENGTHS = (
    "direct_primary",
    "direct_guideline",
    "method_precedent",
    "contextual_background",
    "contradictory",
    "weak",
    "missing",
    "not_applicable",
)

CLAIM_TYPES = (
    "background",
    "method",
    "result",
    "interpretation",
    "limitation",
    "guideline",
    "causal",
    "predictive",
)


def claim_evidence_matrix_skeleton(
    claims: Iterable[str | Mapping[str, object]],
    evidence_refs: Iterable[str] | None = None,
) -> list[dict[str, object]]:
    """Return refs-only claim/evidence matrix rows."""
    refs = list(evidence_refs or [])
    rows: list[dict[str, object]] = []
    for index, item in enumerate(claims, start=1):
        if isinstance(item, Mapping):
            claim_ref = str(item.get("claim_ref") or f"claim_{index}")
            claim = str(item.get("claim") or "")
            claim_type = str(item.get("claim_type") or "")
        else:
            claim_ref = f"claim_{index}"
            claim = str(item)
            claim_type = ""
        rows.append(
            {
                "claim_ref": claim_ref,
                "claim": claim,
                "claim_type": claim_type,
                "evidence_refs": refs,
                "support_strength": "missing",
                "contradiction_or_gap_ref": "",
                "route_back_candidate": "",
            }
        )
    return rows


def support_strength_vocab_lint(rows: Iterable[Mapping[str, object]]) -> list[dict[str, str]]:
    """Flag unsupported support-strength labels."""
    allowed = set(SUPPORT_STRENGTHS)
    findings: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        value = str(row.get("support_strength") or "").strip()
        if value not in allowed:
            findings.append(
                {
                    "row": str(index),
                    "code": "INVALID_SUPPORT_STRENGTH",
                    "value": value,
                    "allowed": ", ".join(SUPPORT_STRENGTHS),
                }
            )
    return findings


def claim_inventory_skeleton(claim_texts: Iterable[str]) -> list[dict[str, str]]:
    """Return compact claim inventory rows."""
    return [
        {
            "claim_ref": f"claim_{index}",
            "claim": claim,
            "claim_type": "",
            "manuscript_location_ref": "",
            "owner_gate_handoff_ref": "",
        }
        for index, claim in enumerate(claim_texts, start=1)
    ]


def evidence_synthesis_handoff_skeleton() -> dict[str, object]:
    """Return the standard refs-only claim-map handoff shell."""
    return {
        "claim_inventory_ref": "",
        "claim_type_map_ref": "",
        "source_support_ref": "",
        "support_strength_map_ref": "",
        "contradiction_and_gap_ref": "",
        "claim_revision_candidate_ref": "",
        "candidate_package_ref": "",
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def _self_check() -> None:
    rows = claim_evidence_matrix_skeleton(["A"], ["source:1"])
    assert rows[0]["claim_ref"] == "claim_1"
    assert rows[0]["support_strength"] == "missing"
    assert support_strength_vocab_lint([{"support_strength": "strong"}])[0]["code"]
    assert not support_strength_vocab_lint([{"support_strength": "direct_primary"}])
    assert claim_inventory_skeleton(["A"])[0]["claim"] == "A"
    assert "owner_gate_handoff_ref" in evidence_synthesis_handoff_skeleton()
    print(json.dumps({"ok": True, "checks": 6}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
