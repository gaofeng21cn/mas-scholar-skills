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
CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS_V2 = (
    "cohort_recruitment_period_ref",
    "source_population_ref",
    "inclusion_exclusion_ref",
    "extract_date_ref",
    "disease_definition_ref",
    "analytic_unit_ref",
    "deduplication_ref",
    "analysis_set_flow_ref",
    "follow_up_closure_ref",
    "follow_up_completeness_ref",
    "loss_to_follow_up_ref",
    "administrative_censoring_ref",
    "competing_event_ref",
    "early_censoring_ref",
    "exclusion_attrition_ref",
    "endpoint_source_codebook_ref",
    "endpoint_ascertainment_ref",
    "endpoint_adjudication_ref",
    "endpoint_three_state_regeneration_ref",
    "time_origin_ref",
    "cause_hierarchy_ref",
    "unknown_cause_policy_ref",
    "center_variable_definition_ref",
    "center_count_ref",
    "center_semantics_ref",
    "center_split_role_ref",
    "dictionary_ref",
    "lineage_ref",
    "ethics_approval_ref",
    "consent_or_waiver_ref",
    "data_use_release_authority_ref",
    "privacy_access_tier_ref",
    "data_code_availability_ref",
    "funding_declaration_ref",
    "conflict_declaration_ref",
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
CLINICAL_INPUT_CORE_PRESENT_FIELDS_V2 = frozenset(
    {
        "cohort_recruitment_period_ref",
        "source_population_ref",
        "inclusion_exclusion_ref",
        "extract_date_ref",
        "disease_definition_ref",
        "analytic_unit_ref",
        "deduplication_ref",
        "analysis_set_flow_ref",
        "endpoint_source_codebook_ref",
        "endpoint_ascertainment_ref",
        "endpoint_three_state_regeneration_ref",
        "time_origin_ref",
        "cause_hierarchy_ref",
        "unknown_cause_policy_ref",
        "dictionary_ref",
        "lineage_ref",
        "ethics_approval_ref",
        "consent_or_waiver_ref",
        "data_use_release_authority_ref",
        "privacy_access_tier_ref",
        "data_code_availability_ref",
        "funding_declaration_ref",
        "conflict_declaration_ref",
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
CLINICAL_INPUT_CONDITIONAL_FIELDS_V2 = {
    "follow_up_closure_ref": "has_longitudinal_follow_up",
    "follow_up_completeness_ref": "has_longitudinal_follow_up",
    "loss_to_follow_up_ref": "has_longitudinal_follow_up",
    "administrative_censoring_ref": "has_longitudinal_follow_up",
    "competing_event_ref": "has_longitudinal_follow_up",
    "early_censoring_ref": "has_longitudinal_follow_up",
    "exclusion_attrition_ref": "has_longitudinal_follow_up",
    "center_variable_definition_ref": "is_multicenter",
    "center_count_ref": "is_multicenter",
    "center_semantics_ref": "is_multicenter",
    "center_split_role_ref": "is_multicenter",
    "endpoint_adjudication_ref": "requires_endpoint_adjudication",
}
GUESSED_IDENTITY_RE = re.compile(
    r"\b(?:tbd|todo|unknown|assumed|inferred|guess(?:ed)?)\b",
    re.IGNORECASE,
)
IDENTITY_EXACT_REF_FIELDS = frozenset({"kind", "ref", "size_bytes", "sha256"})
ENDPOINT_STATE_COUNT_FIELDS = (
    "analysis_set_n",
    "target_event_count",
    "competing_event_count",
    "unknown_cause_count",
    "early_censored_count",
    "event_free_count",
)
ENDPOINT_STATE_TIME_BASES = (
    "fixed_horizon",
    "full_follow_up",
    "cross_sectional",
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
    """Audit the stable v1 clinical input identity contract."""

    return _validate_clinical_analysis_input_identity_candidate(
        candidate, strict_v2=False
    )


def validate_clinical_analysis_input_identity_candidate_v2(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Audit the v2 exact-ref and endpoint-state identity contract."""

    return _validate_clinical_analysis_input_identity_candidate(
        candidate, strict_v2=True
    )


def _validate_clinical_analysis_input_identity_candidate(
    candidate: Mapping[str, object], *, strict_v2: bool
) -> dict[str, Any]:
    """Audit the clinical input identity needed before analysis or full drafting."""

    findings: list[dict[str, object]] = []
    identity_fields = (
        CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS_V2
        if strict_v2
        else CLINICAL_ANALYSIS_INPUT_IDENTITY_FIELDS
    )
    core_present_fields = (
        CLINICAL_INPUT_CORE_PRESENT_FIELDS_V2
        if strict_v2
        else CLINICAL_INPUT_CORE_PRESENT_FIELDS
    )
    conditional_fields = (
        CLINICAL_INPUT_CONDITIONAL_FIELDS_V2
        if strict_v2
        else CLINICAL_INPUT_CONDITIONAL_FIELDS
    )
    if strict_v2 and _validate_identity_exact_ref(
        candidate.get("study_context_ref"), "study_context_ref"
    ):
        findings.append(
            _identity_finding(
                "CLINICAL_INPUT_STUDY_CONTEXT_EXACT_REF_INVALID",
                "study_context_ref",
                "bind the context triggers to an exact study-context evidence ref",
            )
        )
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
    expected = set(identity_fields)
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
    present_fields: set[str] = set()
    for field in identity_fields:
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
            present_fields.add(field)
            exact_ref_findings = (
                _validate_identity_exact_ref(item.get("ref"), item_path)
                if strict_v2
                else []
            )
            if strict_v2 and exact_ref_findings:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_IDENTITY_EXACT_REF_INVALID",
                        f"{item_path}.ref",
                        "bind the fact to an owner-bound exact ref with size and sha256",
                    )
                )
            elif not strict_v2 and not ref:
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
            ref_locator = (
                str(item.get("ref", {}).get("ref") or "")
                if isinstance(item.get("ref"), Mapping)
                else str(item.get("ref") or "")
            )
            if ref_locator and GUESSED_IDENTITY_RE.search(ref_locator):
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_IDENTITY_GUESSED_REF_FORBIDDEN",
                        f"{item_path}.ref",
                        "route the unknown fact back instead of guessing a ref",
                    )
                )
        elif status == "missing":
            if item.get("ref") not in (None, ""):
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
            if item.get("ref") not in (None, "") or not reason:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_IDENTITY_NOT_APPLICABLE_INVALID",
                        item_path,
                        "leave ref empty and provide a specific applicability reason",
                    )
                )
            if field in core_present_fields:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_CORE_FIELD_NOT_APPLICABLE_FORBIDDEN",
                        item_path,
                        "core clinical input identity must be present or routed back as missing",
                    )
                )
        if context_valid and field in conditional_fields:
            trigger = conditional_fields[field]
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
    if strict_v2 and context_valid:
        for trigger in CLINICAL_INPUT_CONTEXT_FIELDS:
            evidence_fields = {
                field
                for field, owner_trigger in conditional_fields.items()
                if owner_trigger == trigger
            }
            if present_fields.intersection(evidence_fields) and not study_context.get(
                trigger
            ):
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_STUDY_CONTEXT_EVIDENCE_CONTRADICTION",
                        f"study_context.{trigger}",
                        "set the trigger true when corresponding identity evidence is present",
                    )
                )
    endpoint_counts = candidate.get("endpoint_state_counts")
    if strict_v2 and not isinstance(endpoint_counts, Mapping):
        findings.append(
            _identity_finding(
                "CLINICAL_INPUT_ENDPOINT_STATE_COUNTS_INVALID",
                "endpoint_state_counts",
                "provide mutually exclusive target, competing, unknown, and event-free counts",
            )
        )
    elif strict_v2:
        time_basis = str(endpoint_counts.get("time_basis") or "")
        if time_basis not in ENDPOINT_STATE_TIME_BASES:
            findings.append(
                _identity_finding(
                    "CLINICAL_INPUT_ENDPOINT_TIME_BASIS_INVALID",
                    "endpoint_state_counts.time_basis",
                    "use fixed_horizon, full_follow_up, or cross_sectional",
                )
            )
        count_values: dict[str, int] = {}
        for field in ENDPOINT_STATE_COUNT_FIELDS:
            value = endpoint_counts.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_ENDPOINT_STATE_COUNT_INVALID",
                        f"endpoint_state_counts.{field}",
                        "supply a non-negative integer count",
                    )
                )
            else:
                count_values[field] = value
        if set(count_values) == set(ENDPOINT_STATE_COUNT_FIELDS):
            included_states = [
                "target_event_count",
                "competing_event_count",
                "unknown_cause_count",
                "event_free_count",
            ]
            if time_basis == "fixed_horizon":
                included_states.append("early_censored_count")
            elif count_values["early_censored_count"] != 0:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_EARLY_CENSORING_TIME_BASIS_MISMATCH",
                        "endpoint_state_counts.early_censored_count",
                        "use early-censored state only for a fixed-horizon accounting basis",
                    )
                )
            state_total = sum(count_values[field] for field in included_states)
            if state_total != count_values["analysis_set_n"]:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_ENDPOINT_STATES_NOT_EXHAUSTIVE",
                        "endpoint_state_counts",
                        "make endpoint states mutually exclusive and exhaustive for the declared time basis",
                    )
                )
        if (
            context_valid
            and time_basis in {"fixed_horizon", "full_follow_up"}
            and study_context.get("has_longitudinal_follow_up") is not True
        ):
            findings.append(
                _identity_finding(
                    "CLINICAL_INPUT_TIME_BASIS_CONTEXT_CONTRADICTION",
                    "study_context.has_longitudinal_follow_up",
                    "set longitudinal follow-up true for fixed-horizon or full-follow-up endpoint accounting",
                )
            )
        for ref_field in ("source_policy_ref", "regeneration_ref"):
            if _validate_identity_exact_ref(
                endpoint_counts.get(ref_field), f"endpoint_state_counts.{ref_field}"
            ):
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_ENDPOINT_STATE_EXACT_REF_INVALID",
                        f"endpoint_state_counts.{ref_field}",
                        "bind the endpoint policy and regeneration receipt as exact refs",
                    )
                )
    if not_applicable_count == len(identity_fields):
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


def _validate_identity_exact_ref(value: object, field: str) -> list[str]:
    if not isinstance(value, Mapping) or set(value) != IDENTITY_EXACT_REF_FIELDS:
        return [field]
    size_bytes = value.get("size_bytes")
    digest = str(value.get("sha256") or "")
    if (
        not str(value.get("kind") or "").strip()
        or not str(value.get("ref") or "").strip()
        or isinstance(size_bytes, bool)
        or not isinstance(size_bytes, int)
        or size_bytes < 1
        or re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is None
    ):
        return [field]
    return []


def _self_check() -> None:
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
    print({"checks": 18, "ok": True})


if __name__ == "__main__":
    _self_check()
