"""Deterministic helper for data-freeze and analysis-readiness refs."""

from __future__ import annotations

import re
from typing import Any, Mapping


DATA_FREEZE_REFS = (
    "data_freeze_inventory_ref",
    "data_lock_window_ref",
    "analysis_dataset_boundary_ref",
    "dictionary_and_lineage_ref",
    "missingness_and_exclusion_ref",
    "clinical_analysis_input_identity_ref",
    "analysis_readiness_gap_ref",
)

CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS = (
    "cohort_and_enrollment_period_ref",
    "extract_date_ref",
    "follow_up_closure_ref",
    "follow_up_completeness_ref",
    "disease_definition_ref",
    "endpoint_ascertainment_ref",
    "endpoint_adjudication_ref",
    "center_inventory_ref",
    "dictionary_ref",
    "lineage_ref",
    "ethics_governance_locator_ref",
    "analysis_set_boundary_ref",
)
CLINICAL_INPUT_ITEM_STATUSES = (
    "present",
    "missing",
    "not_applicable_with_reason",
)
CLINICAL_INPUT_CORE_PRESENT_FIELDS = frozenset(
    {
        "cohort_and_enrollment_period_ref",
        "extract_date_ref",
        "disease_definition_ref",
        "endpoint_ascertainment_ref",
        "dictionary_ref",
        "lineage_ref",
        "ethics_governance_locator_ref",
        "analysis_set_boundary_ref",
    }
)
CLINICAL_INPUT_CONTEXT_FIELDS = (
    "has_longitudinal_follow_up",
    "is_multicenter",
    "requires_endpoint_adjudication",
)
CLINICAL_INPUT_CONDITIONAL_FIELDS = {
    "follow_up_closure_ref": "has_longitudinal_follow_up",
    "follow_up_completeness_ref": "has_longitudinal_follow_up",
    "center_inventory_ref": "is_multicenter",
    "endpoint_adjudication_ref": "requires_endpoint_adjudication",
}
GUESSED_IDENTITY_RE = re.compile(
    r"\b(?:tbd|todo|unknown|assumed|inferred|guess(?:ed)?)\b",
    re.IGNORECASE,
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


def validate_clinical_analysis_input_identity_candidate(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Audit the clinical input identity needed before analysis or full drafting."""

    findings: list[dict[str, object]] = []
    study_context = candidate.get("study_context")
    context_valid = isinstance(study_context, Mapping)
    if not context_valid:
        findings.append(
            _identity_finding(
                "CLINICAL_INPUT_STUDY_CONTEXT_INVALID",
                "study_context",
                "provide the explicit follow-up, center, and adjudication triggers",
            )
        )
        study_context = {}
    else:
        actual_context_fields = set(study_context)
        expected_context_fields = set(CLINICAL_INPUT_CONTEXT_FIELDS)
        if actual_context_fields != expected_context_fields:
            findings.append(
                _identity_finding(
                    "CLINICAL_INPUT_STUDY_CONTEXT_FIELDS_INVALID",
                    "study_context",
                    "use exactly the canonical study-context trigger fields",
                )
            )
            context_valid = False
        for field in CLINICAL_INPUT_CONTEXT_FIELDS:
            if not isinstance(study_context.get(field), bool):
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_STUDY_CONTEXT_TRIGGER_INVALID",
                        f"study_context.{field}",
                        "use an explicit boolean trigger",
                    )
                )
                context_valid = False
    items = candidate.get("items")
    if not isinstance(items, Mapping):
        findings.append(
            _identity_finding(
                "CLINICAL_INPUT_IDENTITY_ITEMS_INVALID",
                "items",
                "provide a field-keyed clinical input identity map",
            )
        )
        items = {}
    expected = set(CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS)
    actual = set(items)
    for field in sorted(expected - actual):
        findings.append(
            _identity_finding(
                "CLINICAL_INPUT_IDENTITY_FIELD_MISSING",
                f"items.{field}",
                "record present, missing, or not_applicable_with_reason",
            )
        )
    for field in sorted(actual - expected):
        findings.append(
            _identity_finding(
                "CLINICAL_INPUT_IDENTITY_FIELD_UNEXPECTED",
                f"items.{field}",
                "use the canonical clinical input identity field inventory",
            )
        )
    not_applicable_count = 0
    for field in CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS:
        item = items.get(field)
        item_path = f"items.{field}"
        if not isinstance(item, Mapping):
            if field in actual:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_IDENTITY_ITEM_INVALID",
                        item_path,
                        "provide status, ref, and reason fields",
                    )
                )
            continue
        if set(item) != {"status", "ref", "reason"}:
            findings.append(
                _identity_finding(
                    "CLINICAL_INPUT_IDENTITY_ITEM_FIELDS_INVALID",
                    item_path,
                    "use exactly status, ref, and reason",
                )
            )
        status = str(item.get("status") or "")
        ref = str(item.get("ref") or "").strip()
        reason = str(item.get("reason") or "").strip()
        if status not in CLINICAL_INPUT_ITEM_STATUSES:
            findings.append(
                _identity_finding(
                    "CLINICAL_INPUT_IDENTITY_STATUS_INVALID",
                    f"{item_path}.status",
                    "use present, missing, or not_applicable_with_reason",
                )
            )
        elif status == "present":
            if not ref:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_IDENTITY_REF_MISSING",
                        f"{item_path}.ref",
                        "bind the fact to a durable source ref",
                    )
                )
            if reason:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_IDENTITY_PRESENT_REASON_CONTRADICTORY",
                        f"{item_path}.reason",
                        "leave reason empty for a present ref",
                    )
                )
            if ref and GUESSED_IDENTITY_RE.search(ref):
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_IDENTITY_GUESSED_REF_FORBIDDEN",
                        f"{item_path}.ref",
                        "route the unknown fact back instead of guessing a ref",
                    )
                )
        elif status == "missing":
            if ref:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_IDENTITY_MISSING_REF_CONTRADICTORY",
                        f"{item_path}.ref",
                        "remove the unsupported ref",
                    )
                )
            if not reason:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_IDENTITY_MISSING_REASON_REQUIRED",
                        f"{item_path}.reason",
                        "state the unresolved fact and its owner route",
                    )
                )
            findings.append(
                _identity_finding(
                    "CLINICAL_INPUT_IDENTITY_ROUTE_BACK_REQUIRED",
                    item_path,
                    "obtain the missing clinical input identity evidence",
                )
            )
        elif status == "not_applicable_with_reason":
            not_applicable_count += 1
            if ref or not reason:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_IDENTITY_NOT_APPLICABLE_INVALID",
                        item_path,
                        "leave ref empty and provide a specific applicability reason",
                    )
                )
            if field in CLINICAL_INPUT_CORE_PRESENT_FIELDS:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_CORE_FIELD_NOT_APPLICABLE_FORBIDDEN",
                        item_path,
                        "core clinical input identity must be present or routed back as missing",
                    )
                )
        if context_valid and field in CLINICAL_INPUT_CONDITIONAL_FIELDS:
            trigger = CLINICAL_INPUT_CONDITIONAL_FIELDS[field]
            applies = bool(study_context.get(trigger))
            expected_status = "present" if applies else "not_applicable_with_reason"
            if status != expected_status:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_CONTEXT_DISPOSITION_MISMATCH",
                        item_path,
                        f"use {expected_status} when {trigger}={str(applies).lower()}",
                    )
                )
        if reason and GUESSED_IDENTITY_RE.search(reason):
            findings.append(
                _identity_finding(
                    "CLINICAL_INPUT_IDENTITY_GUESSED_REASON_FORBIDDEN",
                    f"{item_path}.reason",
                    "record a known reason or mark the fact missing without inference",
                )
            )
    if not_applicable_count == len(CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS):
        findings.append(
            _identity_finding(
                "CLINICAL_INPUT_IDENTITY_ALL_NOT_APPLICABLE_FORBIDDEN",
                "items",
                "clinical input identity cannot be satisfied by an all-N/A inventory",
            )
        )
    if candidate.get("authority") is not False:
        findings.append(
            _identity_finding(
                "CLINICAL_INPUT_IDENTITY_AUTHORITY_FORBIDDEN",
                "authority",
                "keep the identity inventory refs-only with authority=false",
            )
        )
    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "clinical_analysis_input_identity_ref",
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "findings": findings,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-data-freeze-and-analysis-readiness-reviewer",
            "reason": "clinical_analysis_input_identity_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def _identity_finding(code: str, field: str, action: str) -> dict[str, object]:
    return {
        "code": code,
        "field": field,
        "action": action,
        "writes_authority": False,
    }


def _self_check() -> None:
    row = lineage_row("age", "source:data-dict")
    assert row["writes_authority"] is False
    skeleton = data_freeze_review_skeleton("dataset:x", "freeze:v1")
    assert skeleton["authority"]["can_approve_source_readiness"] is False
    assert "analysis_readiness_gap_ref" in skeleton["required_refs"]
    assert "clinical_analysis_input_identity_ref" in skeleton["required_refs"]
    assert lint_forbidden_data_claims("source readiness approved")
    complete_items = {
        field: {"status": "present", "ref": f"evidence:{field}", "reason": None}
        for field in CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS
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
    complete_identity = validate_clinical_analysis_input_identity_candidate(
        {
            "study_context": longitudinal_multicenter_context,
            "items": complete_items,
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
        "center_inventory_ref": "the supplied analysis is single-center",
        "endpoint_adjudication_ref": "no separate endpoint adjudication applies",
    }.items():
        cross_sectional_single_center_items[field] = {
            "status": "not_applicable_with_reason",
            "ref": None,
            "reason": reason,
        }
    cross_sectional_single_center = validate_clinical_analysis_input_identity_candidate(
        {
            "study_context": {
                "has_longitudinal_follow_up": False,
                "is_multicenter": False,
                "requires_endpoint_adjudication": False,
            },
            "items": cross_sectional_single_center_items,
            "authority": False,
        }
    )
    assert cross_sectional_single_center["machine_check_status"] == (
        "candidate_complete"
    )
    all_not_applicable = validate_clinical_analysis_input_identity_candidate(
        {
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
                for field in CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS
            },
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
    missing_identity = validate_clinical_analysis_input_identity_candidate(
        {
            "study_context": longitudinal_multicenter_context,
            "items": missing_items,
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
    guessed_identity = validate_clinical_analysis_input_identity_candidate(
        {
            "study_context": longitudinal_multicenter_context,
            "items": guessed_items,
            "authority": False,
        }
    )
    assert "CLINICAL_INPUT_IDENTITY_GUESSED_REF_FORBIDDEN" in {
        item["code"] for item in guessed_identity["findings"]
    }
    print({"checks": 11, "ok": True})


if __name__ == "__main__":
    _self_check()
