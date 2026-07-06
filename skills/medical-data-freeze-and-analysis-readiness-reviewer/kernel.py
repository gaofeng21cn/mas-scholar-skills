"""Deterministic helper for data-freeze and analysis-readiness refs."""

from __future__ import annotations

import re
from typing import Any


DATA_FREEZE_REFS = (
    "data_freeze_inventory_ref",
    "data_lock_window_ref",
    "analysis_dataset_boundary_ref",
    "dictionary_and_lineage_ref",
    "missingness_and_exclusion_ref",
    "analysis_readiness_gap_ref",
)


def lineage_row(variable: str, source_ref: str, transform_ref: str | None = None) -> dict[str, Any]:
    return {
        "variable": variable.strip(),
        "source_ref": source_ref.strip(),
        "transform_ref": transform_ref,
        "needs_owner_confirmation": True,
        "writes_authority": False,
    }


def data_freeze_review_skeleton(dataset_ref: str, freeze_label: str) -> dict[str, Any]:
    return {
        "surface_kind": "data_freeze_analysis_readiness_candidate",
        "dataset_ref": dataset_ref,
        "freeze_label": freeze_label,
        "required_refs": list(DATA_FREEZE_REFS),
        "candidate_refs": {ref: None for ref in DATA_FREEZE_REFS},
        "route_back_candidate": None,
        "owner_gate_handoff_ref": None,
        "authority": {
            "refs_only": True,
            "can_approve_source_readiness": False,
            "can_mutate_clinical_data": False,
            "can_write_mas_truth": False,
            "can_sign_owner_receipt": False,
            "can_create_typed_blocker": False,
            "can_claim_publication_readiness": False,
        },
    }


def lint_forbidden_data_claims(text: str) -> list[str]:
    patterns = (
        r"\bsource readiness approved\b",
        r"\banalysis-ready\b",
        r"\bowner receipt\b",
        r"\btyped blocker\b",
        r"\bdata mutated\b",
    )
    return [pattern for pattern in patterns if re.search(pattern, text, flags=re.I)]


def _self_check() -> None:
    row = lineage_row("age", "source:data-dict")
    assert row["writes_authority"] is False
    skeleton = data_freeze_review_skeleton("dataset:x", "freeze:v1")
    assert skeleton["authority"]["can_approve_source_readiness"] is False
    assert "analysis_readiness_gap_ref" in skeleton["required_refs"]
    assert lint_forbidden_data_claims("source readiness approved")
    print({"checks": 4, "ok": True})


if __name__ == "__main__":
    _self_check()
