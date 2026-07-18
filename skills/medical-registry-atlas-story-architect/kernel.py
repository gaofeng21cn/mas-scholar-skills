"""Deterministic helper for registry/atlas story architecture refs."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence


STORY_REFS = (
    "registry_story_contract_ref",
    "handling_editor_first_draft_contract_ref",
    "cohort_and_data_lock_ref",
    "phenotype_axis_ref",
    "denominator_state_architecture_ref",
    "figure_table_story_map_ref",
    "center_sensitivity_claim_binding_ref",
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
        r"\b(treatment )?gap\b",
        r"\bintensity\b",
        r"\bburden\b",
        r"\bworkload\b",
        r"\bguideline nonadherence\b",
        r"\b(service quality|quality ranking)\b",
    )
    return [pattern for pattern in patterns if re.search(pattern, text, flags=re.I)]


def lint_center_sensitivity_claim_binding(
    central_claims: Sequence[Mapping[str, object]],
    claim_evidence_rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Check central center/site sensitivity claims against claim-map rows."""

    rows_by_ref = {
        str(row.get("claim_ref") or "").strip(): row
        for row in claim_evidence_rows
        if str(row.get("claim_ref") or "").strip()
    }
    findings: list[dict[str, object]] = []
    for index, claim in enumerate(central_claims, start=1):
        locations = claim.get("locations") or [claim.get("location")]
        normalized_locations = {
            str(location or "").strip().lower() for location in locations
        }
        is_central = bool(claim.get("is_central")) or bool(
            normalized_locations & {"abstract", "conclusion"}
        )
        if not is_central:
            continue
        claim_ref = str(claim.get("claim_ref") or "").strip()
        if not claim_ref:
            findings.append(
                _claim_binding_finding(
                    "CENTRAL_SENSITIVITY_CLAIM_REF_MISSING", f"claim_{index}"
                )
            )
            continue
        row = rows_by_ref.get(claim_ref)
        if row is None:
            findings.append(
                _claim_binding_finding(
                    "CENTRAL_SENSITIVITY_CLAIM_ROW_MISSING", claim_ref
                )
            )
            continue
        if not str(row.get("analysis_source_ref") or "").strip():
            findings.append(
                _claim_binding_finding(
                    "CENTRAL_SENSITIVITY_ANALYSIS_SOURCE_MISSING", claim_ref
                )
            )
        display_refs = {
            str(ref).strip() for ref in row.get("display_refs") or [] if str(ref).strip()
        }
        if not display_refs:
            findings.append(
                _claim_binding_finding(
                    "CENTRAL_SENSITIVITY_DISPLAY_REFS_MISSING", claim_ref
                )
            )
        expected_refs = {
            str(ref).strip()
            for ref in claim.get("expected_display_refs") or []
            if str(ref).strip()
        }
        for missing_ref in sorted(expected_refs - display_refs):
            findings.append(
                _claim_binding_finding(
                    "CENTRAL_SENSITIVITY_EXPECTED_DISPLAY_MISSING",
                    claim_ref,
                    display_ref=missing_ref,
                )
            )
    return findings


def _claim_binding_finding(
    code: str, claim_ref: str, *, display_ref: str = ""
) -> dict[str, object]:
    return {
        "code": code,
        "claim_ref": claim_ref,
        "display_ref": display_ref,
        "action": "add a claim-evidence row with analysis source and display refs",
        "writes_authority": False,
    }


def _self_check() -> None:
    assert story_axis_key("Treatment Gap / 2024") == "treatment_gap_2024"
    row = figure_table_story_row("table1", "claim:a", "denom:b")
    assert row["writes_authority"] is False
    assert registry_story_skeleton("question:x")["authority"]["refs_only"] is True
    assert lint_overclaim_terms("causal service quality claim")
    central_claim = {
        "claim_ref": "claim:center-dependence",
        "locations": ["abstract", "conclusion"],
        "expected_display_refs": ["T4", "TS4"],
    }
    missing_row = lint_center_sensitivity_claim_binding([central_claim], [])
    assert {item["code"] for item in missing_row} == {
        "CENTRAL_SENSITIVITY_CLAIM_ROW_MISSING"
    }
    incomplete_row = lint_center_sensitivity_claim_binding(
        [central_claim], [{"claim_ref": "claim:center-dependence"}]
    )
    assert {item["code"] for item in incomplete_row} >= {
        "CENTRAL_SENSITIVITY_ANALYSIS_SOURCE_MISSING",
        "CENTRAL_SENSITIVITY_DISPLAY_REFS_MISSING",
    }
    complete_row = lint_center_sensitivity_claim_binding(
        [central_claim],
        [
            {
                "claim_ref": "claim:center-dependence",
                "analysis_source_ref": "analysis://center-sensitivity",
                "display_refs": ["T4", "TS4"],
            }
        ],
    )
    assert complete_row == []
    assert all(item["writes_authority"] is False for item in missing_row)
    print({"checks": 8, "ok": True})


if __name__ == "__main__":
    _self_check()
