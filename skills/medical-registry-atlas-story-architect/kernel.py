"""Deterministic helper for registry/atlas story architecture refs."""

from __future__ import annotations

import re
from typing import Any


STORY_REFS = (
    "registry_story_contract_ref",
    "cohort_and_data_lock_ref",
    "phenotype_axis_ref",
    "figure_table_story_map_ref",
    "claim_boundary_ref",
    "discussion_theme_ref",
)


def story_axis_key(label: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", label.lower())).strip("_")


def figure_table_story_row(artifact_id: str, claim_ref: str, denominator_ref: str) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id.strip(),
        "claim_ref": claim_ref.strip(),
        "denominator_ref": denominator_ref.strip(),
        "caption_boundary_ref": None,
        "writes_authority": False,
    }


def registry_story_skeleton(question_ref: str) -> dict[str, Any]:
    return {
        "surface_kind": "registry_atlas_story_candidate",
        "question_ref": question_ref,
        "required_refs": list(STORY_REFS),
        "candidate_refs": {ref: None for ref in STORY_REFS},
        "route_back_candidate": None,
        "owner_gate_handoff_ref": None,
        "authority": {
            "refs_only": True,
            "can_accept_claims": False,
            "can_write_mas_truth": False,
            "can_sign_owner_receipt": False,
            "can_create_typed_blocker": False,
            "can_claim_publication_readiness": False,
        },
    }


def lint_overclaim_terms(text: str) -> list[str]:
    patterns = (
        r"\bcaus(e|al|ality)\b",
        r"\bpredict(s|ion|ive)?\b",
        r"\bguideline nonadherence\b",
        r"\bservice quality\b",
    )
    return [pattern for pattern in patterns if re.search(pattern, text, flags=re.I)]


def _self_check() -> None:
    assert story_axis_key("Treatment Gap / 2024") == "treatment_gap_2024"
    row = figure_table_story_row("table1", "claim:a", "denom:b")
    assert row["writes_authority"] is False
    assert registry_story_skeleton("question:x")["authority"]["refs_only"] is True
    assert lint_overclaim_terms("causal service quality claim")
    print({"checks": 4, "ok": True})


if __name__ == "__main__":
    _self_check()
