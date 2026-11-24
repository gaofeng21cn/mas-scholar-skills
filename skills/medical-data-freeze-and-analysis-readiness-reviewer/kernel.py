"""Deterministic helper for data-freeze and analysis-readiness refs."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Literal, Mapping

_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from runtime.kernel_validation import (  # noqa: E402
    ExactRefModel,
    NonEmptyStr,
    StrictBool,
    StrictKernelModel,
    StrictNonNegativeInt,
    ValidationError,
    is_exact_ref,
)


class _StudyContextModel(StrictKernelModel):
    has_longitudinal_follow_up: StrictBool
    is_multicenter: StrictBool
    requires_endpoint_adjudication: StrictBool


class _ClinicalInputItemModel(StrictKernelModel):
    status: Literal["present", "missing", "not_applicable_with_reason"]
    ref: Any
    reason: Any


class _EndpointStateCountsModel(StrictKernelModel):
    time_basis: Literal["fixed_horizon", "full_follow_up", "cross_sectional"]
    analysis_set_n: StrictNonNegativeInt
    target_event_count: StrictNonNegativeInt
    competing_event_count: StrictNonNegativeInt
    unknown_cause_count: StrictNonNegativeInt
    early_censored_count: StrictNonNegativeInt
    event_free_count: StrictNonNegativeInt
    source_policy_ref: ExactRefModel
    regeneration_ref: ExactRefModel


class _RecoverableGapAuditModel(StrictKernelModel):
    machine_check_status: Literal["candidate_complete"]
    gap_id: NonEmptyStr
    reconstruction_outcome: Literal["reconstructed", "not_reconstructed"]
    authority: Literal[False]


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
    context_valid = False
    if not isinstance(study_context, Mapping):
        findings.append(
            _identity_finding(
                "CLINICAL_INPUT_STUDY_CONTEXT_INVALID",
                "study_context",
                "provide the explicit follow-up, center, and adjudication triggers",
            )
        )
        study_context = {}
    else:
        try:
            _StudyContextModel.model_validate(dict(study_context))
            context_valid = True
        except ValidationError:
            if set(study_context) != set(CLINICAL_INPUT_CONTEXT_FIELDS):
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_STUDY_CONTEXT_FIELDS_INVALID",
                        "study_context",
                        "use exactly the canonical study-context trigger fields",
                    )
                )
            for field in CLINICAL_INPUT_CONTEXT_FIELDS:
                if not isinstance(study_context.get(field), bool):
                    findings.append(
                        _identity_finding(
                            "CLINICAL_INPUT_STUDY_CONTEXT_TRIGGER_INVALID",
                            f"study_context.{field}",
                            "use an explicit boolean trigger",
                        )
                    )
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
        try:
            _ClinicalInputItemModel.model_validate(dict(item))
        except ValidationError:
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
        parsed_counts: _EndpointStateCountsModel | None = None
        try:
            parsed_counts = _EndpointStateCountsModel.model_validate(dict(endpoint_counts))
        except ValidationError:
            parsed_counts = None
        if parsed_counts is not None:
            time_basis = parsed_counts.time_basis
            count_values = {
                field: getattr(parsed_counts, field) for field in ENDPOINT_STATE_COUNT_FIELDS
            }
        else:
            time_basis = str(endpoint_counts.get("time_basis") or "")
            if time_basis not in ENDPOINT_STATE_TIME_BASES:
                findings.append(
                    _identity_finding(
                        "CLINICAL_INPUT_ENDPOINT_TIME_BASIS_INVALID",
                        "endpoint_state_counts.time_basis",
                        "use fixed_horizon, full_follow_up, or cross_sectional",
                    )
                )
            count_values = {}
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
    return [] if is_exact_ref(value) else [field]


def validate_recoverable_gap_disposition(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Require a complete reconstruction audit before limitation or human TODO."""

    findings: list[dict[str, object]] = []
    if candidate.get("surface_kind") != "recoverable_gap_disposition_candidate.v1":
        findings.append(
            _identity_finding(
                "RECOVERABLE_GAP_SURFACE_KIND_INVALID",
                "surface_kind",
                "use the recoverable-gap disposition candidate surface",
            )
        )
    gap_id = str(candidate.get("gap_id") or "").strip()
    if not gap_id:
        findings.append(
            _identity_finding(
                "RECOVERABLE_GAP_ID_MISSING",
                "gap_id",
                "bind the disposition to one stable gap id",
            )
        )
    if _validate_identity_exact_ref(
        candidate.get("reconstruction_audit_ref"), "reconstruction_audit_ref"
    ):
        findings.append(
            _identity_finding(
                "RECOVERABLE_GAP_AUDIT_EXACT_REF_INVALID",
                "reconstruction_audit_ref",
                "bind the consumed reconstruction audit as an exact ref",
            )
        )

    audit = candidate.get("reconstruction_audit")
    outcome = None
    if not isinstance(audit, Mapping):
        findings.append(
            _identity_finding(
                "RECOVERABLE_GAP_AUDIT_INVALID",
                "reconstruction_audit",
                "consume the structured governed-source reconstruction audit",
            )
        )
    else:
        if audit.get("machine_check_status") != "candidate_complete":
            findings.append(
                _identity_finding(
                    "RECOVERABLE_GAP_AUDIT_INCOMPLETE",
                    "reconstruction_audit.machine_check_status",
                    "repair the bounded reconstruction audit before disposition",
                )
            )
        if str(audit.get("gap_id") or "").strip() != gap_id:
            findings.append(
                _identity_finding(
                    "RECOVERABLE_GAP_AUDIT_BINDING_MISMATCH",
                    "reconstruction_audit.gap_id",
                    "consume the audit for the same gap id",
                )
            )
        outcome = audit.get("reconstruction_outcome")
        if outcome not in {"reconstructed", "not_reconstructed"}:
            findings.append(
                _identity_finding(
                    "RECOVERABLE_GAP_AUDIT_OUTCOME_INVALID",
                    "reconstruction_audit.reconstruction_outcome",
                    "consume a complete structured reconstruction outcome",
                )
            )
        if audit.get("authority") is not False:
            findings.append(
                _identity_finding(
                    "RECOVERABLE_GAP_AUDIT_AUTHORITY_FORBIDDEN",
                    "reconstruction_audit.authority",
                    "consume a refs-only reconstruction audit",
                )
            )

    disposition = candidate.get("disposition")
    limitation_active = candidate.get("limitation_active")
    human_todo_active = candidate.get("human_todo_active")
    if not isinstance(limitation_active, bool) or not isinstance(human_todo_active, bool):
        findings.append(
            _identity_finding(
                "RECOVERABLE_GAP_DISPOSITION_FLAGS_INVALID",
                "limitation_active|human_todo_active",
                "use explicit boolean limitation and human-TODO flags",
            )
        )
    elif outcome == "reconstructed":
        if disposition != "closed_from_governed_sources":
            findings.append(
                _identity_finding(
                    "RECOVERABLE_GAP_RECONSTRUCTED_DISPOSITION_INVALID",
                    "disposition",
                    "close a recovered gap from governed sources",
                )
            )
        if limitation_active or human_todo_active:
            findings.append(
                _identity_finding(
                    "RECOVERABLE_GAP_STALE_LIMITATION_OR_TODO",
                    "limitation_active|human_todo_active",
                    "remove the limitation and human TODO after exact recovery",
                )
            )
    elif outcome == "not_reconstructed":
        expected_flags = {
            "limitation": (True, False),
            "human_input_required": (False, True),
        }
        if disposition not in expected_flags:
            findings.append(
                _identity_finding(
                    "RECOVERABLE_GAP_UNRESOLVED_DISPOSITION_INVALID",
                    "disposition",
                    "classify the bounded unresolved gap as limitation or human input",
                )
            )
        elif (limitation_active, human_todo_active) != expected_flags[disposition]:
            findings.append(
                _identity_finding(
                    "RECOVERABLE_GAP_UNRESOLVED_FLAGS_MISMATCH",
                    "limitation_active|human_todo_active",
                    "align the active flag with the selected unresolved disposition",
                )
            )
    if candidate.get("authority") is not False:
        findings.append(
            _identity_finding(
                "RECOVERABLE_GAP_AUTHORITY_FORBIDDEN",
                "authority",
                "keep the disposition refs-only with authority=false",
            )
        )

    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "recoverable_gap_disposition_audit_candidate.v1",
        "gap_id": gap_id,
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "disposition": disposition if complete else None,
        "findings": findings,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-data-freeze-and-analysis-readiness-reviewer",
            "reason": "recoverable_gap_disposition_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = str(Path(__file__).resolve().parents[2])
    if _root not in sys.path:
        sys.path.insert(0, _root)
    from runtime.kernel_validation import delegate_self_check
    raise SystemExit(delegate_self_check("medical-data-freeze-and-analysis-readiness-reviewer", kernel_file=__file__))
