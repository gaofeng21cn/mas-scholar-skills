"""Extracted pytest suite for skills/medical-data-freeze-and-analysis-readiness-reviewer/kernel.py."""

from __future__ import annotations

from pathlib import Path
import json

from tests.kernels._loader import kernel_file, load_kernel

KERNEL = load_kernel("medical-data-freeze-and-analysis-readiness-reviewer")
KERNEL_FILE = str(kernel_file("medical-data-freeze-and-analysis-readiness-reviewer"))
CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS = KERNEL.CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS
CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS_V2 = KERNEL.CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS_V2
data_freeze_review_skeleton = KERNEL.data_freeze_review_skeleton
lineage_row = KERNEL.lineage_row
lint_forbidden_data_claims = KERNEL.lint_forbidden_data_claims
validate_clinical_analysis_input_identity_candidate = KERNEL.validate_clinical_analysis_input_identity_candidate
validate_clinical_analysis_input_identity_candidate_v2 = KERNEL.validate_clinical_analysis_input_identity_candidate_v2
validate_recoverable_gap_disposition = KERNEL.validate_recoverable_gap_disposition

def test_medical_data_freeze_and_analysis_readiness_reviewer() -> None:
    def exact_ref(field: str) -> dict[str, object]:
        digest = (field.encode("utf-8").hex() + "0" * 64)[:64]
        return {
            "kind": field,
            "ref": f"artifact://identity/{field}",
            "size_bytes": 1,
            "sha256": f"sha256:{digest}",
        }

    endpoint_state_counts = {
        "time_basis": "fixed_horizon",
        "analysis_set_n": 1000,
        "target_event_count": 50,
        "competing_event_count": 100,
        "unknown_cause_count": 10,
        "early_censored_count": 97,
        "event_free_count": 743,
        "source_policy_ref": exact_ref("endpoint_source_policy_ref"),
        "regeneration_ref": exact_ref("endpoint_regeneration_ref"),
    }
    cross_sectional_endpoint_state_counts = dict(
        endpoint_state_counts,
        time_basis="cross_sectional",
        early_censored_count=0,
        event_free_count=840,
    )

    row = lineage_row("age", "source:data-dict")
    assert row["writes_authority"] is False
    skeleton = data_freeze_review_skeleton("dataset:x", "freeze:v1")
    assert skeleton["authority"]["can_approve_source_readiness"] is False
    assert "analysis_readiness_gap_ref" in skeleton["required_refs"]
    assert "clinical_analysis_input_identity_ref" in skeleton["required_refs"]
    assert lint_forbidden_data_claims("source readiness approved")
    legacy_context = {
        "has_longitudinal_follow_up": True,
        "is_multicenter": True,
        "requires_endpoint_adjudication": False,
    }
    legacy_items = {
        field: {"status": "present", "ref": f"evidence:{field}", "reason": None}
        for field in CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS
    }
    legacy_items["endpoint_adjudication_ref"] = {
        "status": "not_applicable_with_reason",
        "ref": None,
        "reason": "outcomes are registry-linked deaths with no separate adjudication process",
    }
    legacy_candidate = {
        "study_context": legacy_context,
        "items": legacy_items,
        "authority": False,
    }
    assert validate_clinical_analysis_input_identity_candidate(legacy_candidate)[
        "machine_check_status"
    ] == "candidate_complete"
    assert validate_clinical_analysis_input_identity_candidate_v2(legacy_candidate)[
        "machine_check_status"
    ] == "route_back_required"
    complete_items = {
        field: {"status": "present", "ref": exact_ref(field), "reason": None}
        for field in CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS_V2
    }
    complete_items["endpoint_adjudication_ref"] = {
        "status": "not_applicable_with_reason",
        "ref": None,
        "reason": "outcomes are registry-linked deaths with no separate adjudication process",
    }
    longitudinal_multicenter_context = {
        "has_longitudinal_follow_up": True,
        "is_multicenter": True,
        "requires_endpoint_adjudication": False,
    }
    complete_identity = validate_clinical_analysis_input_identity_candidate_v2(
        {
            "study_context_ref": exact_ref("study_context_ref"),
            "study_context": longitudinal_multicenter_context,
            "items": complete_items,
            "endpoint_state_counts": endpoint_state_counts,
            "authority": False,
        }
    )
    assert complete_identity["machine_check_status"] == "candidate_complete"
    cross_sectional_single_center_items = {
        field: dict(value) for field, value in complete_items.items()
    }
    for field, reason in {
        "follow_up_closure_ref": "the analysis is cross-sectional",
        "follow_up_completeness_ref": "the analysis is cross-sectional",
        "loss_to_follow_up_ref": "the analysis is cross-sectional",
        "administrative_censoring_ref": "the analysis is cross-sectional",
        "competing_event_ref": "the analysis is cross-sectional",
        "early_censoring_ref": "the analysis is cross-sectional",
        "exclusion_attrition_ref": "the analysis is cross-sectional",
        "center_variable_definition_ref": "the supplied analysis is single-center",
        "center_count_ref": "the supplied analysis is single-center",
        "center_semantics_ref": "the supplied analysis is single-center",
        "center_split_role_ref": "the supplied analysis is single-center",
        "endpoint_adjudication_ref": "no separate endpoint adjudication applies",
    }.items():
        cross_sectional_single_center_items[field] = {
            "status": "not_applicable_with_reason",
            "ref": None,
            "reason": reason,
        }
    cross_sectional_single_center = validate_clinical_analysis_input_identity_candidate_v2(
        {
            "study_context_ref": exact_ref("cross_sectional_study_context_ref"),
            "study_context": {
                "has_longitudinal_follow_up": False,
                "is_multicenter": False,
                "requires_endpoint_adjudication": False,
            },
            "items": cross_sectional_single_center_items,
            "endpoint_state_counts": cross_sectional_endpoint_state_counts,
            "authority": False,
        }
    )
    assert cross_sectional_single_center["machine_check_status"] == (
        "candidate_complete"
    )
    all_not_applicable = validate_clinical_analysis_input_identity_candidate_v2(
        {
            "study_context_ref": exact_ref("all_na_study_context_ref"),
            "study_context": {
                "has_longitudinal_follow_up": False,
                "is_multicenter": False,
                "requires_endpoint_adjudication": False,
            },
            "items": {
                field: {
                    "status": "not_applicable_with_reason",
                    "ref": None,
                    "reason": "declared not applicable",
                }
                for field in CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS_V2
            },
            "endpoint_state_counts": cross_sectional_endpoint_state_counts,
            "authority": False,
        }
    )
    assert {
        "CLINICAL_INPUT_IDENTITY_ALL_NOT_APPLICABLE_FORBIDDEN",
        "CLINICAL_INPUT_CORE_FIELD_NOT_APPLICABLE_FORBIDDEN",
    }.issubset({item["code"] for item in all_not_applicable["findings"]})
    missing_items = {field: dict(value) for field, value in complete_items.items()}
    missing_items["follow_up_closure_ref"] = {
        "status": "missing",
        "ref": None,
        "reason": "follow-up closure evidence is not in the supplied snapshot",
    }
    missing_identity = validate_clinical_analysis_input_identity_candidate_v2(
        {
            "study_context_ref": exact_ref("missing_study_context_ref"),
            "study_context": longitudinal_multicenter_context,
            "items": missing_items,
            "endpoint_state_counts": endpoint_state_counts,
            "authority": False,
        }
    )
    assert "CLINICAL_INPUT_IDENTITY_ROUTE_BACK_REQUIRED" in {
        item["code"] for item in missing_identity["findings"]
    }
    guessed_items = {field: dict(value) for field, value in complete_items.items()}
    guessed_items["extract_date_ref"] = {
        "status": "present",
        "ref": "assumed extract date",
        "reason": None,
    }
    guessed_identity = validate_clinical_analysis_input_identity_candidate_v2(
        {
            "study_context_ref": exact_ref("guessed_study_context_ref"),
            "study_context": longitudinal_multicenter_context,
            "items": guessed_items,
            "endpoint_state_counts": endpoint_state_counts,
            "authority": False,
        }
    )
    assert "CLINICAL_INPUT_IDENTITY_GUESSED_REF_FORBIDDEN" in {
        item["code"] for item in guessed_identity["findings"]
    }
    non_exhaustive_counts = dict(endpoint_state_counts, event_free_count=839)
    non_exhaustive = validate_clinical_analysis_input_identity_candidate_v2(
        {
            "study_context_ref": exact_ref("non_exhaustive_study_context_ref"),
            "study_context": longitudinal_multicenter_context,
            "items": complete_items,
            "endpoint_state_counts": non_exhaustive_counts,
            "authority": False,
        }
    )
    assert "CLINICAL_INPUT_ENDPOINT_STATES_NOT_EXHAUSTIVE" in {
        item["code"] for item in non_exhaustive["findings"]
    }
    false_longitudinal_bypass = validate_clinical_analysis_input_identity_candidate_v2(
        {
            "study_context_ref": exact_ref("false_longitudinal_context_ref"),
            "study_context": {
                "has_longitudinal_follow_up": False,
                "is_multicenter": True,
                "requires_endpoint_adjudication": False,
            },
            "items": complete_items,
            "endpoint_state_counts": endpoint_state_counts,
            "authority": False,
        }
    )
    assert {
        "CLINICAL_INPUT_STUDY_CONTEXT_EVIDENCE_CONTRADICTION",
        "CLINICAL_INPUT_TIME_BASIS_CONTEXT_CONTRADICTION",
    }.issubset({item["code"] for item in false_longitudinal_bypass["findings"]})
    missing_context_ref = validate_clinical_analysis_input_identity_candidate_v2(
        {
            "study_context": longitudinal_multicenter_context,
            "items": complete_items,
            "endpoint_state_counts": endpoint_state_counts,
            "authority": False,
        }
    )
    assert "CLINICAL_INPUT_STUDY_CONTEXT_EXACT_REF_INVALID" in {
        item["code"] for item in missing_context_ref["findings"]
    }
    fixture_path = (
        Path(KERNEL_FILE).parents[1]
        / "medical-data-governance"
        / "fixtures"
        / "governed-source-reconstruction.json"
    )
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    disposition_results = {
        case["case_id"]: validate_recoverable_gap_disposition(case["candidate"])
        for case in fixture["disposition_cases"]
    }
    assert disposition_results["recovered_gap_closes_todo"]["machine_check_status"] == "candidate_complete"
    stale = disposition_results["recovered_gap_keeps_human_todo"]
    assert stale["machine_check_status"] == "route_back_required"
    assert "RECOVERABLE_GAP_STALE_LIMITATION_OR_TODO" in {
        item["code"] for item in stale["findings"]
    }
    print({"checks": 21, "ok": True})
