"""Deterministic helper for risk-model transportability review refs.

This helper is skill-local and no-authority. It does not accept models, compute
clinical verdicts, write MAS truth, sign owner receipts, or claim readiness.
"""

from __future__ import annotations

import re
from typing import Any


REQUIRED_REFS = (
    "source_model_ref",
    "target_population_ref",
    "predictor_mapping_ref",
    "transportability_assessment_ref",
    "calibration_and_performance_ref",
    "clinical_utility_boundary_ref",
)


def normalize_predictor_name(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return re.sub(r"_+", "_", text).strip("_")


def predictor_mapping_row(source: str, target: str, *, status: str = "needs_review") -> dict[str, Any]:
    return {
        "source_predictor": source.strip(),
        "source_predictor_key": normalize_predictor_name(source),
        "target_variable": target.strip(),
        "target_variable_key": normalize_predictor_name(target),
        "mapping_status": status,
        "writes_authority": False,
    }


def transportability_review_skeleton(model_ref: str, target_ref: str) -> dict[str, Any]:
    return {
        "surface_kind": "risk_model_transportability_review_candidate",
        "model_ref": model_ref,
        "target_population_ref": target_ref,
        "required_refs": list(REQUIRED_REFS),
        "candidate_refs": {ref: None for ref in REQUIRED_REFS},
        "route_back_candidate": None,
        "owner_gate_handoff_ref": None,
        "authority": {
            "refs_only": True,
            "can_accept_model": False,
            "can_write_mas_truth": False,
            "can_sign_owner_receipt": False,
            "can_create_typed_blocker": False,
            "can_claim_readiness": False,
        },
    }


def lint_forbidden_authority_claims(text: str) -> list[dict[str, str]]:
    patterns = {
        "MODEL_ACCEPTANCE": r"\b(model accepted|model is valid|transportable)\b",
        "OWNER_RECEIPT": r"\bowner receipt\b",
        "TYPED_BLOCKER": r"\btyped blocker\b",
        "READINESS": r"\b(publication|analysis|source)-ready\b",
    }
    return [
        {"code": code, "match": pattern}
        for code, pattern in patterns.items()
        if re.search(pattern, text, flags=re.I)
    ]


def _self_check() -> None:
    assert normalize_predictor_name("LDL-C (mg/dL)") == "ldl_c_mg_dl"
    row = predictor_mapping_row("Age", "age_years")
    assert row["writes_authority"] is False
    skeleton = transportability_review_skeleton("model:abc", "cohort:def")
    assert skeleton["authority"]["refs_only"] is True
    assert lint_forbidden_authority_claims("model accepted with owner receipt")
    print({"checks": 4, "ok": True})


if __name__ == "__main__":
    _self_check()
