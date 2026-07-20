"""Deterministic refs-only helpers for medical statistical review.

These helpers scaffold statistical review refs and lint hints. They do not
issue analysis verdicts, owner receipts, typed blockers, or publication
readiness.
"""

from __future__ import annotations

import json
import re
from typing import Any, Mapping, Sequence


MODEL_FAMILY_RULES = (
    ("survival", ("cox", "kaplan", "time-to-event", "hazard", "censor")),
    ("logistic", ("logistic", "odds ratio", "or", "binary")),
    ("linear", ("linear", "mean difference", "regression coefficient")),
    ("count", ("poisson", "negative binomial", "rate ratio", "incidence")),
    ("mixed", ("mixed", "random effect", "cluster", "repeated")),
    ("prediction", ("auc", "c-statistic", "calibration", "brier")),
    ("descriptive", ("median", "iqr", "mean", "sd", "count", "percent")),
)

REPORTING_ITEMS = (
    "statistical_question_ref",
    "estimand_or_target_parameter_ref",
    "analysis_plan_ref",
    "denominator_and_missingness_ref",
    "effect_size_and_uncertainty_ref",
    "assumption_diagnostic_ref",
    "multiplicity_and_sensitivity_ref",
    "statistical_action_matrix_ref",
)

FIXED_HORIZON_OBSERVED_RISK_ESTIMATORS = (
    "binary_proportion",
    "kaplan_meier",
    "cumulative_incidence",
    "ipcw",
    "other_censoring_aware",
)

CONSTRUCT_COMPARABILITY_STATUSES = (
    "comparable",
    "not_comparable",
    "not_estimable",
    "not_applicable",
)

REGISTRY_SIGNAL_REF_FAMILY = "ehr_registry_signal_validity_ref"
REGISTRY_SIGNAL_MEMBER_REFS = (
    "paper_identity_ref",
    "chart_review_validation_ref",
    "phenotype_outcome_coupling_ref",
    "availability_mechanism_ref",
    "observation_opportunity_bias_ref",
    "source_generation_quality_ref",
    "claim_boundary_ref",
)
REGISTRY_SIGNAL_FORBIDDEN_AUTHORITY_FIELDS = (
    "authority",
    "statistical_conclusion",
    "statistical_verdict",
    "quality_verdict",
    "owner_receipt",
    "typed_blocker",
    "publication_ready",
    "writes_domain_truth",
)

DENOMINATOR_SEMANTIC_KINDS = (
    "eligible_percent",
    "candidate_percent",
    "resolved_percent",
    "absolute_flagged_count",
)

VALIDATION_PARTITION_STRATEGIES = (
    "random_split",
    "temporal_split",
    "center_disjoint",
    "site_disjoint",
    "independent_external_dataset",
)
VALIDATION_TYPES = ("internal", "internal_external", "external")
SOURCE_POPULATION_RELATIONS = (
    "same_cohort_partition",
    "independently_assembled_external_population",
    "unclear",
)
DEVELOPMENT_SELECTION_PARTITIONS = {
    "development",
    "development_resampling",
}
ENDPOINT_ROLES = ("primary", "secondary", "sensitivity")
FOLLOW_UP_BASES = ("fixed_horizon", "full_follow_up")
MODEL_SEPARATION_STATUSES = ("none", "suspected", "detected", "not_assessed")
MODEL_PENALTY_SOURCES = (
    "prespecified",
    "development_resampling",
    "external_prior",
    "validation_outcome",
)
MODEL_ADEQUACY_METHODS = (
    "riley_pmsampsize",
    "bootstrap_optimism",
    "simulation_based",
    "owner_declared_equivalent",
)
DIAGNOSTIC_APPLICABILITY_STATUSES = (
    "required",
    "not_applicable_with_reason",
)
DCA_CENSORING_METHODS = (
    "none_complete_follow_up",
    "ipcw",
    "survival_dca",
)
DCA_CALIBRATION_BASIS_STATUSES = (
    "validated_absolute_risk",
    "recalibrated_absolute_risk",
    "unverified",
)
DCA_UNCERTAINTY_METHODS = (
    "bootstrap",
    "influence_function",
    "cross_validation",
    "other_prespecified",
)

P_VALUE_RE = re.compile(r"\bp\s*[<=>]\s*0?\.\d+|\bp-value\b", re.I)
CI_RE = re.compile(r"\b(?:ci|confidence interval|credible interval)\b", re.I)
EFFECT_RE = re.compile(r"\b(?:or|hr|rr|risk ratio|mean difference|effect size|estimate)\b", re.I)
MISSING_RE = re.compile(r"\bmissing(?:ness)?\b", re.I)


def statistical_review_schema() -> dict[str, Any]:
    """Return the compact refs-only statistical review schema."""

    return {
        "type": "object",
        "required": list(REPORTING_ITEMS),
        "properties": {
            "statistical_question_ref": {"type": "string"},
            "estimand_or_target_parameter_ref": {"type": "string"},
            "analysis_plan_ref": {"type": "string"},
            "model_family_ref": {"type": "string"},
            "denominator_and_missingness_ref": {"type": "string"},
            "effect_size_and_uncertainty_ref": {"type": "string"},
            "assumption_diagnostic_ref": {"type": "string"},
            "multiplicity_and_sensitivity_ref": {"type": "string"},
            "statistical_action_matrix_ref": {"type": "array", "items": {"type": "object"}},
            "ehr_registry_signal_validity_ref": {"type": "object"},
            "denominator_semantics_matrix_ref": {"type": "array", "items": {"type": "object"}},
            "validation_partition_integrity_ref": {"type": "object"},
            "endpoint_analysis_set_reconciliation_ref": {"type": "object"},
            "model_complexity_sparse_event_ref": {"type": "object"},
            "decision_curve_validity_ref": {"type": "object"},
            "route_back_candidate": {"type": "string"},
        },
    }


def fixed_horizon_risk_semantics_schema() -> dict[str, Any]:
    """Return the refs-only contract for fixed-horizon outcome semantics."""

    required = (
        "time_origin_ref",
        "horizon_ref",
        "event_count_ref",
        "recorded_event_proportion_ref",
        "recorded_event_proportion_role",
        "censored_before_horizon_count",
        "follow_up_completeness_ref",
        "observed_risk_estimator",
        "observed_risk_ref",
        "prediction_error_ref",
        "independent_censoring_assumption_ref",
        "weighting_policy_ref",
        "claim_boundary_ref",
    )
    return {
        "type": "object",
        "required": list(required),
        "properties": {
            "time_origin_ref": {"type": "string"},
            "horizon_ref": {"type": "string"},
            "event_count_ref": {"type": "string"},
            "recorded_event_proportion_ref": {"type": "string"},
            "recorded_event_proportion_role": {
                "const": "descriptive_count_fraction_not_risk_estimate"
            },
            "censored_before_horizon_count": {"type": "integer", "minimum": 0},
            "follow_up_completeness_ref": {"type": "string"},
            "observed_risk_estimator": {
                "enum": list(FIXED_HORIZON_OBSERVED_RISK_ESTIMATORS)
            },
            "observed_risk_ref": {"type": "string"},
            "prediction_error_ref": {"type": "string"},
            "independent_censoring_assumption_ref": {"type": "string"},
            "weighting_policy_ref": {"type": "string"},
            "claim_boundary_ref": {"type": "string"},
            "authority": {"const": False},
        },
    }


def construct_comparability_schema() -> dict[str, Any]:
    """Return the cross-source construct and identity-linkage contract."""

    required = (
        "source_construct_ref",
        "target_construct_ref",
        "codebook_mapping_ref",
        "identity_linkage_ref",
        "comparability_status",
        "estimability_ref",
        "allowed_claim_ref",
        "forbidden_claim_ref",
    )
    return {
        "type": "object",
        "required": list(required),
        "properties": {
            "source_construct_ref": {"type": "string"},
            "target_construct_ref": {"type": "string"},
            "codebook_mapping_ref": {"type": "string"},
            "identity_linkage_ref": {"type": "string"},
            "comparability_status": {
                "enum": list(CONSTRUCT_COMPARABILITY_STATUSES)
            },
            "estimability_ref": {"type": "string"},
            "allowed_claim_ref": {"type": "string"},
            "forbidden_claim_ref": {"type": "string"},
            "authority": {"const": False},
        },
    }


def validate_fixed_horizon_risk_semantics(
    candidate: Mapping[str, object],
) -> list[dict[str, str]]:
    """Flag semantic contradictions without accepting the analysis."""

    findings: list[dict[str, str]] = []
    schema = fixed_horizon_risk_semantics_schema()
    for field in schema["required"]:
        if candidate.get(field) in (None, ""):
            findings.append(
                _finding(
                    str(candidate.get("claim_ref") or "fixed_horizon_risk"),
                    "FIXED_HORIZON_SEMANTICS_REF_MISSING",
                    f"add {field}",
                )
            )
    if candidate.get("recorded_event_proportion_role") != (
        "descriptive_count_fraction_not_risk_estimate"
    ):
        findings.append(
            _finding(
                "recorded_event_proportion_ref",
                "RECORDED_EVENT_PROPORTION_MISLABELED_AS_RISK",
                "label the count fraction as descriptive and report observed risk separately",
            )
        )
    censored = candidate.get("censored_before_horizon_count")
    estimator = candidate.get("observed_risk_estimator")
    if isinstance(censored, int) and censored > 0 and estimator == "binary_proportion":
        findings.append(
            _finding(
                "observed_risk_ref",
                "BINARY_RISK_WITH_EARLY_CENSORING",
                "use a censoring-aware observed-risk estimator or route back",
            )
        )
    if estimator not in FIXED_HORIZON_OBSERVED_RISK_ESTIMATORS:
        findings.append(
            _finding(
                "observed_risk_ref",
                "OBSERVED_RISK_ESTIMATOR_UNDECLARED",
                "declare the fixed-horizon observed-risk estimator",
            )
        )
    return findings


def validate_validation_partition_integrity(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Audit partition independence and outcome-free model selection."""

    findings: list[dict[str, object]] = []
    required = (
        "development_partition_ref",
        "validation_partition_ref",
        "partition_strategy",
        "partitions_disjoint",
        "claimed_validation_type",
        "source_population_relation",
        "validation_outcome_ref",
        "selection_decisions",
        "authority",
    )
    _require_candidate_fields(candidate, required, findings, "VALIDATION_PARTITION")
    strategy = str(candidate.get("partition_strategy") or "")
    validation_type = str(candidate.get("claimed_validation_type") or "")
    source_relation = str(candidate.get("source_population_relation") or "")
    if strategy not in VALIDATION_PARTITION_STRATEGIES:
        findings.append(
            _candidate_finding(
                "VALIDATION_PARTITION_STRATEGY_INVALID",
                "partition_strategy",
                "declare the actual split or independent external dataset strategy",
            )
        )
    if validation_type not in VALIDATION_TYPES:
        findings.append(
            _candidate_finding(
                "VALIDATION_TYPE_INVALID",
                "claimed_validation_type",
                "use internal, internal_external, or external",
            )
        )
    if source_relation not in SOURCE_POPULATION_RELATIONS:
        findings.append(
            _candidate_finding(
                "VALIDATION_SOURCE_POPULATION_RELATION_INVALID",
                "source_population_relation",
                "declare same-cohort partition, independently assembled external population, or unclear",
            )
        )
    elif source_relation == "unclear":
        findings.append(
            _candidate_finding(
                "VALIDATION_SOURCE_POPULATION_PROVENANCE_UNRESOLVED",
                "source_population_relation",
                "resolve whether validation participants come from the same cohort or an independently assembled population",
            )
        )
    development_ref = _candidate_ref_identity(candidate.get("development_partition_ref"))
    validation_ref = _candidate_ref_identity(candidate.get("validation_partition_ref"))
    if development_ref and development_ref == validation_ref:
        findings.append(
            _candidate_finding(
                "VALIDATION_PARTITIONS_NOT_DISTINCT",
                "validation_partition_ref",
                "bind development and validation to distinct partition refs",
            )
        )
    if candidate.get("partitions_disjoint") is not True:
        findings.append(
            _candidate_finding(
                "VALIDATION_PARTITIONS_NOT_DISJOINT",
                "partitions_disjoint",
                "supply disjoint subject or cluster membership evidence",
            )
        )
    if source_relation == "same_cohort_partition" and validation_type == "external":
        findings.append(
            _candidate_finding(
                "SAME_SOURCE_SPLIT_MISLABELED_AS_EXTERNAL_VALIDATION",
                "claimed_validation_type",
                "label a within-cohort split as internal or internal_external validation",
            )
        )
    if validation_type == "external":
        if source_relation != "independently_assembled_external_population" or not _candidate_ref_identity(
            candidate.get("independent_external_cohort_ref")
        ):
            findings.append(
                _candidate_finding(
                    "EXTERNAL_VALIDATION_INDEPENDENT_COHORT_MISSING",
                    "independent_external_cohort_ref",
                    "bind the external claim to an independent source population",
                )
            )

    decisions = candidate.get("selection_decisions")
    if not isinstance(decisions, Sequence) or isinstance(decisions, (str, bytes)):
        findings.append(
            _candidate_finding(
                "VALIDATION_SELECTION_DECISIONS_INVALID",
                "selection_decisions",
                "provide a list of tuning, penalty, and model-selection decisions",
            )
        )
        decisions = []
    if not decisions:
        findings.append(
            _candidate_finding(
                "VALIDATION_SELECTION_POLICY_MISSING",
                "selection_decisions",
                "declare the tuning/model-selection timeline, including a prespecified no-tuning policy",
            )
        )
    for index, decision in enumerate(decisions):
        field = f"selection_decisions[{index}]"
        if not isinstance(decision, Mapping):
            findings.append(
                _candidate_finding(
                    "VALIDATION_SELECTION_DECISION_INVALID",
                    field,
                    "provide a structured decision row",
                )
            )
            continue
        for required_field in (
            "decision_kind",
            "metric_ref",
            "metric_partition",
            "uses_validation_outcomes",
        ):
            if decision.get(required_field) in (None, ""):
                findings.append(
                    _candidate_finding(
                        "VALIDATION_SELECTION_DECISION_FIELD_MISSING",
                        f"{field}.{required_field}",
                        "bind each selection decision to development-only evidence",
                    )
                )
        metric_partition = str(decision.get("metric_partition") or "")
        if (
            metric_partition not in DEVELOPMENT_SELECTION_PARTITIONS
            or decision.get("uses_validation_outcomes") is not False
        ):
            findings.append(
                _candidate_finding(
                    "VALIDATION_OUTCOME_USED_FOR_MODEL_SELECTION",
                    field,
                    "select penalty, tuning, and model form using development-only resampling",
                )
            )
    _require_no_authority(candidate, findings, "validation_partition_integrity_ref")
    return _candidate_audit_result(
        "validation_partition_integrity_ref",
        findings,
        claimed_validation_type=validation_type,
    )


def validate_endpoint_analysis_set_reconciliation(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Audit endpoint, follow-up basis, N/event, estimand, and source separation."""

    findings: list[dict[str, object]] = []
    rows = candidate.get("rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        findings.append(
            _candidate_finding(
                "ENDPOINT_ANALYSIS_SET_ROWS_INVALID",
                "rows",
                "provide at least one endpoint-specific analysis-set row",
            )
        )
        rows = []
    normalized: list[dict[str, object]] = []
    required_fields = (
        "endpoint_id",
        "endpoint_role",
        "follow_up_basis",
        "analysis_set_ref",
        "n",
        "events",
        "estimand_ref",
        "source_metric_ref",
    )
    for index, row in enumerate(rows):
        field = f"rows[{index}]"
        if not isinstance(row, Mapping):
            findings.append(
                _candidate_finding(
                    "ENDPOINT_ANALYSIS_SET_ROW_INVALID",
                    field,
                    "provide a structured reconciliation row",
                )
            )
            continue
        for required_field in required_fields:
            if row.get(required_field) in (None, ""):
                findings.append(
                    _candidate_finding(
                        "ENDPOINT_ANALYSIS_SET_FIELD_MISSING",
                        f"{field}.{required_field}",
                        "separate endpoint, time basis, analysis set, estimand, and source",
                    )
                )
        endpoint_role = str(row.get("endpoint_role") or "")
        follow_up_basis = str(row.get("follow_up_basis") or "")
        if endpoint_role not in ENDPOINT_ROLES:
            findings.append(
                _candidate_finding(
                    "ENDPOINT_ROLE_INVALID",
                    f"{field}.endpoint_role",
                    "use primary, secondary, or sensitivity",
                )
            )
        if follow_up_basis not in FOLLOW_UP_BASES:
            findings.append(
                _candidate_finding(
                    "FOLLOW_UP_BASIS_INVALID",
                    f"{field}.follow_up_basis",
                    "separate fixed-horizon from full-follow-up analyses",
                )
            )
        n_value = row.get("n")
        events = row.get("events")
        if (
            isinstance(n_value, bool)
            or not isinstance(n_value, int)
            or n_value <= 0
            or isinstance(events, bool)
            or not isinstance(events, int)
            or events < 0
            or (isinstance(n_value, int) and isinstance(events, int) and events > n_value)
        ):
            findings.append(
                _candidate_finding(
                    "ENDPOINT_N_EVENT_COUNT_INVALID",
                    field,
                    "supply integer N and event counts with 0 <= events <= N",
                )
            )
        normalized.append(
            {
                "index": index,
                "pair": (n_value, events),
                "endpoint_id": str(row.get("endpoint_id") or ""),
                "endpoint_role": endpoint_role,
                "follow_up_basis": follow_up_basis,
                "estimand_ref": _candidate_ref_identity(row.get("estimand_ref")),
                "source_metric_ref": _candidate_ref_identity(row.get("source_metric_ref")),
            }
        )
    if normalized and not any(row["endpoint_role"] == "primary" for row in normalized):
        findings.append(
            _candidate_finding(
                "PRIMARY_ENDPOINT_ANALYSIS_SET_MISSING",
                "rows",
                "identify the primary endpoint analysis set",
            )
        )
    for left_index, left in enumerate(normalized):
        for right in normalized[left_index + 1 :]:
            if left["pair"] == right["pair"]:
                continue
            shared_estimand = bool(left["estimand_ref"]) and (
                left["estimand_ref"] == right["estimand_ref"]
            )
            shared_source = bool(left["source_metric_ref"]) and (
                left["source_metric_ref"] == right["source_metric_ref"]
            )
            if shared_estimand or shared_source:
                findings.append(
                    _candidate_finding(
                        "ENDPOINT_ANALYSIS_SET_ESTIMAND_SOURCE_CONFLATED",
                        f"rows[{left['index']}]|rows[{right['index']}]",
                        "bind each distinct N/event pair to its endpoint role, follow-up basis, estimand, and source metric",
                    )
                )
    _require_no_authority(candidate, findings, "endpoint_analysis_set_reconciliation_ref")
    return _candidate_audit_result(
        "endpoint_analysis_set_reconciliation_ref",
        findings,
        row_count=len(normalized),
    )


def validate_model_complexity_sparse_event(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Audit model degrees of freedom against events and required diagnostics."""

    findings: list[dict[str, object]] = []
    required = (
        "model_family",
        "event_count",
        "candidate_parameter_df",
        "effective_parameter_df",
        "continuous_predictor_count",
        "sample_size_adequacy_method",
        "sample_size_adequacy_inputs_ref",
        "sample_size_adequacy_result_ref",
        "expected_shrinkage_or_optimism_ref",
        "observed_shrinkage_or_optimism_ref",
        "separation_status",
        "penalty_source",
        "ph_assessment_applicability",
        "ph_assessment_ref",
        "nonlinearity_assessment_ref",
        "calibration_intercept_ref",
        "calibration_slope_ref",
        "full_model_parameter_ref",
        "authority",
    )
    _require_candidate_fields(candidate, required, findings, "MODEL_COMPLEXITY")
    events = candidate.get("event_count")
    effective_df = candidate.get("effective_parameter_df")
    candidate_df = candidate.get("candidate_parameter_df")
    numeric_valid = True
    continuous_predictor_count = candidate.get("continuous_predictor_count")
    for field, value, minimum in (
        ("event_count", events, 1),
        ("candidate_parameter_df", candidate_df, 1),
        ("effective_parameter_df", effective_df, 1),
        ("continuous_predictor_count", continuous_predictor_count, 0),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            numeric_valid = False
            findings.append(
                _candidate_finding(
                    "MODEL_COMPLEXITY_COUNT_INVALID",
                    field,
                    "supply positive integer event and parameter-degree counts",
                )
            )
    events_per_df = None
    if numeric_valid:
        events_per_df = float(events) / float(effective_df)
    adequacy_method = str(candidate.get("sample_size_adequacy_method") or "")
    if adequacy_method not in MODEL_ADEQUACY_METHODS:
        findings.append(
            _candidate_finding(
                "MODEL_SAMPLE_SIZE_ADEQUACY_METHOD_INVALID",
                "sample_size_adequacy_method",
                "use Riley/pmsampsize inputs, bootstrap optimism, simulation, or an owner-declared equivalent",
            )
        )
    for ref_field in (
        "sample_size_adequacy_inputs_ref",
        "sample_size_adequacy_result_ref",
        "expected_shrinkage_or_optimism_ref",
        "observed_shrinkage_or_optimism_ref",
    ):
        if not _candidate_ref_identity(candidate.get(ref_field)):
            findings.append(
                _candidate_finding(
                    "MODEL_FORMAL_ADEQUACY_EVIDENCE_MISSING",
                    ref_field,
                    "bind a formal sample-size/overfitting assessment and shrinkage or optimism evidence",
                    severity="route_back_required",
                )
            )
    separation = str(candidate.get("separation_status") or "")
    if separation not in MODEL_SEPARATION_STATUSES:
        findings.append(
            _candidate_finding(
                "MODEL_SEPARATION_STATUS_INVALID",
                "separation_status",
                "declare none, suspected, detected, or not_assessed",
            )
        )
    elif separation in {"suspected", "detected", "not_assessed"}:
        findings.append(
            _candidate_finding(
                "MODEL_SEPARATION_ROUTE_BACK_REQUIRED",
                "separation_status",
                "resolve or explicitly model sparse-level separation before full-draft claims",
                severity="route_back_required",
            )
        )
    penalty_source = str(candidate.get("penalty_source") or "")
    if penalty_source not in MODEL_PENALTY_SOURCES:
        findings.append(
            _candidate_finding(
                "MODEL_PENALTY_SOURCE_INVALID",
                "penalty_source",
                "declare prespecified, development-resampling, or external-prior penalty evidence",
            )
        )
    elif penalty_source == "validation_outcome":
        findings.append(
            _candidate_finding(
                "VALIDATION_OUTCOME_USED_FOR_PENALTY_SELECTION",
                "penalty_source",
                "select penalty strength without validation outcomes",
                severity="route_back_required",
            )
        )
    ph_applicability = str(candidate.get("ph_assessment_applicability") or "")
    if ph_applicability not in DIAGNOSTIC_APPLICABILITY_STATUSES:
        findings.append(
            _candidate_finding(
                "MODEL_PH_APPLICABILITY_INVALID",
                "ph_assessment_applicability",
                "declare required or not_applicable_with_reason explicitly",
            )
        )
    nonlinearity_required = (
        isinstance(continuous_predictor_count, int)
        and not isinstance(continuous_predictor_count, bool)
        and continuous_predictor_count > 0
    )
    for ref_field, allow_not_applicable, require_not_applicable in (
        (
            "ph_assessment_ref",
            ph_applicability == "not_applicable_with_reason",
            ph_applicability == "not_applicable_with_reason",
        ),
        ("nonlinearity_assessment_ref", not nonlinearity_required, False),
        ("calibration_intercept_ref", True, False),
        ("calibration_slope_ref", True, False),
    ):
        _validate_conditional_model_evidence(
            candidate.get(ref_field),
            ref_field,
            findings,
            allow_not_applicable=allow_not_applicable,
            require_not_applicable=require_not_applicable,
        )
    if not _candidate_ref_identity(candidate.get("full_model_parameter_ref")):
        findings.append(
            _candidate_finding(
                "MODEL_DIAGNOSTIC_OR_PARAMETER_REF_MISSING",
                "full_model_parameter_ref",
                "bind the full model parameter evidence",
            )
        )
    _require_no_authority(candidate, findings, "model_complexity_sparse_event_ref")
    return _candidate_audit_result(
        "model_complexity_sparse_event_ref",
        findings,
        events_per_effective_parameter_df=events_per_df,
        events_per_parameter_role="descriptive_only_not_adequacy_verdict",
    )


def _validate_conditional_model_evidence(
    value: object,
    field: str,
    findings: list[dict[str, object]],
    *,
    allow_not_applicable: bool,
    require_not_applicable: bool,
) -> None:
    """Accept a ref or an explicit status/ref/reason disposition."""

    if isinstance(value, Mapping) and "status" in value:
        if set(value) != {"status", "ref", "reason"}:
            findings.append(
                _candidate_finding(
                    "MODEL_DIAGNOSTIC_DISPOSITION_FIELDS_INVALID",
                    field,
                    "use exactly status, ref, and reason",
                )
            )
        status = str(value.get("status") or "")
        ref = _candidate_ref_identity(value.get("ref"))
        reason = str(value.get("reason") or "").strip()
        if status == "present":
            if not ref or reason:
                findings.append(
                    _candidate_finding(
                        "MODEL_DIAGNOSTIC_PRESENT_INVALID",
                        field,
                        "bind a non-empty ref and leave reason empty",
                    )
                )
            elif require_not_applicable:
                findings.append(
                    _candidate_finding(
                        "MODEL_DIAGNOSTIC_APPLICABILITY_DISPOSITION_MISMATCH",
                        field,
                        "match the evidence disposition to the declared applicability",
                    )
                )
        elif status == "not_applicable_with_reason":
            if not allow_not_applicable or ref or not reason:
                findings.append(
                    _candidate_finding(
                        "MODEL_DIAGNOSTIC_NOT_APPLICABLE_INVALID",
                        field,
                        "use not_applicable_with_reason only when the diagnostic does not apply",
                    )
                )
        else:
            findings.append(
                _candidate_finding(
                    "MODEL_DIAGNOSTIC_DISPOSITION_STATUS_INVALID",
                    f"{field}.status",
                    "use present or not_applicable_with_reason",
                )
            )
        return
    if not _candidate_ref_identity(value):
        findings.append(
            _candidate_finding(
                "MODEL_DIAGNOSTIC_OR_PARAMETER_REF_MISSING",
                field,
                "bind diagnostic evidence or an explicit not-applicable disposition",
            )
        )
    elif require_not_applicable:
        findings.append(
            _candidate_finding(
                "MODEL_DIAGNOSTIC_APPLICABILITY_DISPOSITION_MISMATCH",
                field,
                "match the evidence disposition to the declared applicability",
            )
        )


def validate_decision_curve_validity(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Audit fixed-horizon decision-curve semantics under censoring."""

    findings: list[dict[str, object]] = []
    required = (
        "prediction_horizon_ref",
        "censoring_before_horizon_count",
        "censoring_method",
        "analysis_set_policy",
        "uncertainty_method",
        "uncertainty_interval_ref",
        "calibration_basis_ref",
        "calibration_basis_status",
        "threshold_range_ref",
        "net_benefit_source_ref",
        "clinical_action_scenarios",
        "authority",
    )
    _require_candidate_fields(candidate, required, findings, "DECISION_CURVE")
    censored = candidate.get("censoring_before_horizon_count")
    if isinstance(censored, bool) or not isinstance(censored, int) or censored < 0:
        findings.append(
            _candidate_finding(
                "DECISION_CURVE_CENSORING_COUNT_INVALID",
                "censoring_before_horizon_count",
                "supply a non-negative count",
            )
        )
        censored = None
    method = str(candidate.get("censoring_method") or "")
    if method not in DCA_CENSORING_METHODS:
        findings.append(
            _candidate_finding(
                "DECISION_CURVE_CENSORING_METHOD_INVALID",
                "censoring_method",
                "use complete-follow-up, IPCW, or survival-DCA semantics",
            )
        )
    if isinstance(censored, int) and censored > 0:
        if method not in {"ipcw", "survival_dca"}:
            findings.append(
                _candidate_finding(
                    "DECISION_CURVE_EARLY_CENSORING_UNCORRECTED",
                    "censoring_method",
                    "use IPCW or survival decision-curve estimation at the fixed horizon",
                    severity="route_back_required",
                )
            )
        if str(candidate.get("analysis_set_policy") or "").startswith("complete_case"):
            findings.append(
                _candidate_finding(
                    "DECISION_CURVE_COMPLETE_CASE_WITH_EARLY_CENSORING",
                    "analysis_set_policy",
                    "retain the censoring risk set and use a censoring-aware estimator",
                    severity="route_back_required",
                )
            )
    uncertainty_method = str(candidate.get("uncertainty_method") or "")
    if uncertainty_method not in DCA_UNCERTAINTY_METHODS:
        findings.append(
            _candidate_finding(
                "DECISION_CURVE_UNCERTAINTY_METHOD_INVALID",
                "uncertainty_method",
                "declare the bootstrap, influence-function, cross-validation, or other prespecified uncertainty method",
            )
        )
    calibration_status = str(candidate.get("calibration_basis_status") or "")
    if calibration_status not in DCA_CALIBRATION_BASIS_STATUSES:
        findings.append(
            _candidate_finding(
                "DECISION_CURVE_CALIBRATION_BASIS_STATUS_INVALID",
                "calibration_basis_status",
                "declare validated_absolute_risk, recalibrated_absolute_risk, or unverified",
            )
        )
    elif calibration_status == "unverified":
        findings.append(
            _candidate_finding(
                "DECISION_CURVE_CALIBRATION_BASIS_UNVERIFIED",
                "calibration_basis_status",
                "validate or recalibrate absolute risk before threshold net-benefit claims",
                severity="route_back_required",
            )
        )
    for ref_field in (
        "prediction_horizon_ref",
        "uncertainty_interval_ref",
        "calibration_basis_ref",
        "threshold_range_ref",
        "net_benefit_source_ref",
    ):
        if not _candidate_ref_identity(candidate.get(ref_field)):
            findings.append(
                _candidate_finding(
                    "DECISION_CURVE_REQUIRED_REF_MISSING",
                    ref_field,
                    "bind the fixed horizon, uncertainty, calibration, threshold, and net-benefit source",
                )
            )
    scenarios = candidate.get("clinical_action_scenarios")
    if not isinstance(scenarios, Sequence) or isinstance(scenarios, (str, bytes)):
        scenarios = []
    if len(scenarios) != 1:
        findings.append(
            _candidate_finding(
                "DECISION_CURVE_ACTION_SCENARIO_NOT_UNIQUE",
                "clinical_action_scenarios",
                "declare exactly one clinically actionable decision scenario",
            )
        )
    elif not isinstance(scenarios[0], Mapping) or not all(
        _candidate_ref_identity(scenarios[0].get(field))
        for field in ("scenario_ref", "action_ref")
    ):
        findings.append(
            _candidate_finding(
                "DECISION_CURVE_ACTION_SCENARIO_INCOMPLETE",
                "clinical_action_scenarios[0]",
                "bind the scenario and resulting clinical action",
            )
        )
    _require_no_authority(candidate, findings, "decision_curve_validity_ref")
    return _candidate_audit_result(
        "decision_curve_validity_ref",
        findings,
        censoring_method=method,
        calibration_basis_status=calibration_status,
    )


def normalize_model_family(value: object) -> str:
    """Normalize a method label to a broad model family."""

    text = str(value or "").strip().lower()
    for family, terms in MODEL_FAMILY_RULES:
        if any(re.search(rf"\b{re.escape(term)}\b", text) for term in terms):
            return family
    return "unspecified" if not text else "other"


def reporting_checklist_skeleton(claim_refs: Sequence[str] | None = None) -> list[dict[str, str]]:
    """Return checklist rows for p-value, CI, effect-size, model, and missingness refs."""

    claims = list(claim_refs or [""])
    return [
        {
            "claim_ref": claim,
            "p_value_policy_ref": "",
            "confidence_interval_ref": "",
            "effect_size_ref": "",
            "model_family_ref": "",
            "missingness_strategy_ref": "",
            "reporting_action": "",
            "route_back_candidate": "",
        }
        for claim in claims
    ]


def missingness_plan_skeleton(variables: Sequence[str]) -> list[dict[str, object]]:
    """Return one missingness review row per variable."""

    return [
        {
            "variable": variable,
            "available_n": None,
            "missing_n": None,
            "missing_percent": None,
            "pattern_ref": "",
            "strategy_ref": "",
            "impact_on_claim_refs": [],
        }
        for variable in variables
    ]


def lint_statistical_reporting(items: Sequence[str | Mapping[str, object]]) -> list[dict[str, str]]:
    """Flag missing reporting elements without judging the analysis."""

    findings: list[dict[str, str]] = []
    for index, item in enumerate(items, start=1):
        if isinstance(item, Mapping):
            text = str(item.get("text") or item.get("claim") or "")
            ref = str(item.get("claim_ref") or f"item_{index}")
            model = str(item.get("model_family") or item.get("model") or "")
            missingness = str(item.get("missingness_strategy") or "")
        else:
            text = str(item)
            ref = f"item_{index}"
            model = ""
            missingness = ""
        has_p = bool(P_VALUE_RE.search(text))
        has_ci = bool(CI_RE.search(text))
        has_effect = bool(EFFECT_RE.search(text))
        if has_p and not (has_ci or has_effect):
            findings.append(_finding(ref, "P_VALUE_ALONE", "add effect size or uncertainty ref"))
        if has_ci and not has_effect:
            findings.append(_finding(ref, "CI_WITHOUT_EFFECT", "name the estimate/effect measure"))
        if normalize_model_family(model or text) == "unspecified":
            findings.append(_finding(ref, "MODEL_FAMILY_UNSPECIFIED", "add model_family_ref"))
        if MISSING_RE.search(text) and not missingness:
            findings.append(_finding(ref, "MISSINGNESS_STRATEGY_MISSING", "add missingness_strategy_ref"))
    return findings


def lint_denominator_semantic_separation(
    rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Flag ambiguous percentage/count denominator or display semantics."""

    findings: list[dict[str, object]] = []
    normalized: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        metric_ref = str(row.get("metric_ref") or f"metric_{index}").strip()
        metric_kind = str(row.get("metric_kind") or "").strip()
        normalized_row = {
            "metric_ref": metric_ref,
            "metric_kind": metric_kind,
            "numerator_ref": str(row.get("numerator_ref") or "").strip(),
            "denominator_ref": str(row.get("denominator_ref") or "").strip(),
            "denominator_semantics_ref": str(
                row.get("denominator_semantics_ref") or ""
            ).strip(),
            "denominator_role": str(row.get("denominator_role") or "").strip(),
            "visual_semantic_ref": str(row.get("visual_semantic_ref") or "").strip(),
            "unit": str(row.get("unit") or "").strip().lower(),
        }
        normalized.append(normalized_row)
        if metric_kind not in DENOMINATOR_SEMANTIC_KINDS:
            findings.append(
                _denominator_finding(
                    "DENOMINATOR_METRIC_KIND_UNKNOWN", metric_ref
                )
            )
            continue
        for field in (
            "numerator_ref",
            "denominator_ref",
            "denominator_semantics_ref",
            "denominator_role",
            "unit",
            "visual_semantic_ref",
        ):
            if not normalized_row[field]:
                findings.append(
                    _denominator_finding(f"{field.upper()}_MISSING", metric_ref)
                )
        formula = row.get("formula")
        if not isinstance(formula, Mapping):
            findings.append(
                _denominator_finding("FORMULA_MISSING_OR_INVALID", metric_ref)
            )
        else:
            for field in (
                "numerator_ref",
                "denominator_ref",
                "denominator_role",
                "unit",
            ):
                declared = normalized_row[field]
                formula_value = str(formula.get(field) or "").strip()
                if field == "unit":
                    formula_value = formula_value.lower()
                if declared and formula_value != declared:
                    findings.append(
                        _denominator_finding(
                            f"FORMULA_{field.upper()}_MISMATCH", metric_ref
                        )
                    )
        if metric_kind.endswith("_percent"):
            if normalized_row["unit"] not in {"percent", "%"}:
                findings.append(
                    _denominator_finding("PERCENT_UNIT_INVALID", metric_ref)
                )
        else:
            if normalized_row["unit"] != "count":
                findings.append(
                    _denominator_finding("ABSOLUTE_COUNT_UNIT_INVALID", metric_ref)
                )

    for left_index, left in enumerate(normalized):
        for right in normalized[left_index + 1 :]:
            left_is_percent = left["metric_kind"].endswith("_percent")
            right_is_percent = right["metric_kind"].endswith("_percent")
            if left_is_percent == right_is_percent:
                continue
            if (
                left["visual_semantic_ref"]
                and left["visual_semantic_ref"] == right["visual_semantic_ref"]
            ):
                findings.append(
                    _denominator_finding(
                        "AMBIGUOUS_PERCENT_COUNT_VISUAL_SEMANTIC",
                        f"{left['metric_ref']}|{right['metric_ref']}",
                    )
                )
            if (
                left["unit"]
                and left["unit"] == right["unit"]
            ):
                findings.append(
                    _denominator_finding(
                        "AMBIGUOUS_PERCENT_COUNT_UNIT",
                        f"{left['metric_ref']}|{right['metric_ref']}",
                    )
                )
    return sorted(
        findings, key=lambda item: (str(item["code"]), str(item["metric_ref"]))
    )


def _denominator_finding(code: str, metric_ref: str) -> dict[str, object]:
    return {
        "code": code,
        "metric_ref": metric_ref,
        "action": "separate numerator, denominator, unit, and visual semantics",
        "writes_authority": False,
    }


def _candidate_finding(
    code: str,
    field: str,
    action: str,
    *,
    severity: str = "quality_debt",
) -> dict[str, object]:
    return {
        "code": code,
        "field": field,
        "severity": severity,
        "action": action,
        "writes_authority": False,
    }


def _require_candidate_fields(
    candidate: Mapping[str, object],
    required: Sequence[str],
    findings: list[dict[str, object]],
    prefix: str,
) -> None:
    for field in required:
        if candidate.get(field) in (None, ""):
            findings.append(
                _candidate_finding(
                    f"{prefix}_FIELD_MISSING",
                    field,
                    "supply the required refs-only candidate field",
                )
            )


def _require_no_authority(
    candidate: Mapping[str, object],
    findings: list[dict[str, object]],
    surface_kind: str,
) -> None:
    if candidate.get("authority") is not False:
        findings.append(
            _candidate_finding(
                "STATISTICAL_CANDIDATE_AUTHORITY_FORBIDDEN",
                "authority",
                f"keep {surface_kind} refs-only with authority=false",
            )
        )


def _candidate_audit_result(
    surface_kind: str,
    findings: Sequence[Mapping[str, object]],
    **details: object,
) -> dict[str, Any]:
    ordered_findings = sorted(
        (dict(item) for item in findings),
        key=lambda item: (str(item.get("code")), str(item.get("field"))),
    )
    complete = not ordered_findings
    return {
        "surface_kind": surface_kind,
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "findings": ordered_findings,
        **details,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-statistical-review",
            "reason": f"{surface_kind}_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def _candidate_ref_identity(value: object) -> str:
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    if isinstance(value, Mapping):
        for key in ("ref", "uri", "path"):
            identity = value.get(key)
            if isinstance(identity, str) and identity.strip():
                return re.sub(r"\s+", " ", identity).strip()
    return ""


def _registry_signal_violation(
    code: str, field: str, action: str
) -> dict[str, str | bool]:
    return {
        "code": code,
        "field": field,
        "action": action,
        "writes_authority": False,
    }


def validate_ehr_registry_signal_validity_candidate(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Validate one coupled refs-only EHR/registry signal candidate.

    This checks candidate-reference completeness and the no-authority boundary.
    It does not decide whether the recorded clinical signal is valid.
    """

    if not isinstance(candidate, Mapping):
        raise ValueError("registry signal validity candidate must be an object")
    violations: list[dict[str, str | bool]] = []
    ref_family = str(candidate.get("ref_family") or REGISTRY_SIGNAL_REF_FAMILY)
    if ref_family != REGISTRY_SIGNAL_REF_FAMILY:
        violations.append(
            _registry_signal_violation(
                "REGISTRY_SIGNAL_REF_FAMILY_INVALID",
                "ref_family",
                f"use the single {REGISTRY_SIGNAL_REF_FAMILY} family",
            )
        )
    for field in ("producer_skill", "owner_route"):
        value = candidate.get(field)
        if value is not None and value != "medical-statistical-review":
            violations.append(
                _registry_signal_violation(
                    "REGISTRY_SIGNAL_OWNER_ROUTE_INVALID",
                    field,
                    "route the integrated candidate through medical-statistical-review",
                )
            )

    identities: dict[str, str] = {}
    missing_member_refs: list[str] = []
    for member_ref in REGISTRY_SIGNAL_MEMBER_REFS:
        identity = _candidate_ref_identity(candidate.get(member_ref))
        if not identity:
            missing_member_refs.append(member_ref)
            violations.append(
                _registry_signal_violation(
                    "REGISTRY_SIGNAL_MEMBER_REF_MISSING",
                    member_ref,
                    "supply the bounded candidate ref or route back for evidence",
                )
            )
        else:
            identities[member_ref] = identity

    for field in REGISTRY_SIGNAL_FORBIDDEN_AUTHORITY_FIELDS:
        value = candidate.get(field)
        if value is not None and value is not False:
            violations.append(
                _registry_signal_violation(
                    "REGISTRY_SIGNAL_AUTHORITY_CLAIM_FORBIDDEN",
                    field,
                    "remove the claim and route any decision to MAS or the domain owner",
                )
            )

    declared_boundary = candidate.get("authority_boundary")
    if declared_boundary is not None:
        if not isinstance(declared_boundary, Mapping):
            violations.append(
                _registry_signal_violation(
                    "REGISTRY_SIGNAL_AUTHORITY_BOUNDARY_INVALID",
                    "authority_boundary",
                    "declare refs_only=true and keep every authority capability false",
                )
            )
        else:
            for field, value in declared_boundary.items():
                allowed = value is True if field == "refs_only" else value is False
                if not allowed:
                    violations.append(
                        _registry_signal_violation(
                            "REGISTRY_SIGNAL_AUTHORITY_BOUNDARY_INVALID",
                            f"authority_boundary.{field}",
                            "declare refs_only=true and keep every authority capability false",
                        )
                    )

    violations.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not violations
    return {
        "surface_kind": "ehr_registry_signal_validity_kernel_audit_candidate.v1",
        "ref_family": REGISTRY_SIGNAL_REF_FAMILY,
        "producer_skill": "medical-statistical-review",
        "owner_route": "medical-statistical-review",
        "machine_check_status": (
            "candidate_ref_shape_complete"
            if complete
            else "candidate_ref_shape_incomplete"
        ),
        "coupled_member_ref_count": len(identities),
        "member_ref_identities": identities,
        "missing_member_refs": missing_member_refs,
        "violations": violations,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-statistical-review",
            "reason": "registry_signal_validity_candidate_requires_repair",
            "missing_member_refs": missing_member_refs,
            "authority": False,
        },
        "authority": False,
        "authority_boundary": {
            "refs_only": True,
            "can_write_domain_truth": False,
            "can_claim_statistical_conclusion": False,
            "can_claim_quality_verdict": False,
            "can_sign_owner_receipt": False,
            "can_create_typed_blocker": False,
            "can_claim_publication_readiness": False,
        },
    }


def _finding(ref: str, code: str, action: str) -> dict[str, str]:
    return {"claim_ref": ref, "code": code, "action": action}


def _self_check() -> None:
    assert "analysis_plan_ref" in statistical_review_schema()["required"]
    assert normalize_model_family("Cox proportional hazards") == "survival"
    assert reporting_checklist_skeleton(["c1"])[0]["claim_ref"] == "c1"
    assert missingness_plan_skeleton(["age"])[0]["variable"] == "age"
    assert fixed_horizon_risk_semantics_schema()["properties"][
        "recorded_event_proportion_role"
    ] == {"const": "descriptive_count_fraction_not_risk_estimate"}
    assert "identity_linkage_ref" in construct_comparability_schema()["required"]
    horizon_findings = validate_fixed_horizon_risk_semantics(
        {
            "time_origin_ref": "time:exam",
            "horizon_ref": "horizon:5y",
            "event_count_ref": "count:events",
            "recorded_event_proportion_ref": "fraction:events",
            "recorded_event_proportion_role": "risk_estimate",
            "censored_before_horizon_count": 4,
            "follow_up_completeness_ref": "followup:summary",
            "observed_risk_estimator": "binary_proportion",
            "observed_risk_ref": "risk:binary",
            "prediction_error_ref": "error:ipcw",
            "independent_censoring_assumption_ref": "assumption:independent",
            "weighting_policy_ref": "weighting:unweighted",
            "claim_boundary_ref": "claim:analysis-sample",
        }
    )
    assert {item["code"] for item in horizon_findings} >= {
        "RECORDED_EVENT_PROPORTION_MISLABELED_AS_RISK",
        "BINARY_RISK_WITH_EARLY_CENSORING",
    }
    lint = lint_statistical_reporting(
        [{"claim_ref": "c1", "claim": "p=0.03 with missingness noted"}]
    )
    assert {item["code"] for item in lint} >= {"P_VALUE_ALONE", "MISSINGNESS_STRATEGY_MISSING"}
    registry_candidate = {
        "ref_family": REGISTRY_SIGNAL_REF_FAMILY,
        "producer_skill": "medical-statistical-review",
        "owner_route": "medical-statistical-review",
        **{
            member_ref: {
                "kind": "candidate_evidence_ref",
                "ref": f"evidence://registry-signal/{member_ref}",
            }
            for member_ref in REGISTRY_SIGNAL_MEMBER_REFS
        },
    }
    registry_audit = validate_ehr_registry_signal_validity_candidate(
        registry_candidate
    )
    assert registry_audit["machine_check_status"] == "candidate_ref_shape_complete"
    assert registry_audit["coupled_member_ref_count"] == 7
    assert registry_audit["authority"] is False
    assert all(
        value is False
        for key, value in registry_audit["authority_boundary"].items()
        if key != "refs_only"
    )

    missing_claim_boundary = dict(registry_candidate)
    missing_claim_boundary["claim_boundary_ref"] = None
    missing_audit = validate_ehr_registry_signal_validity_candidate(
        missing_claim_boundary
    )
    assert missing_audit["machine_check_status"] == "candidate_ref_shape_incomplete"
    assert missing_audit["missing_member_refs"] == ["claim_boundary_ref"]
    assert missing_audit["route_back_candidate"]["authority"] is False

    authority_counterexample = dict(registry_candidate, owner_receipt="accepted")
    authority_audit = validate_ehr_registry_signal_validity_candidate(
        authority_counterexample
    )
    assert "REGISTRY_SIGNAL_AUTHORITY_CLAIM_FORBIDDEN" in {
        item["code"] for item in authority_audit["violations"]
    }
    nested_authority_counterexample = dict(
        registry_candidate,
        authority_boundary={"refs_only": True, "can_sign_owner_receipt": True},
    )
    nested_authority_audit = validate_ehr_registry_signal_validity_candidate(
        nested_authority_counterexample
    )
    assert "REGISTRY_SIGNAL_AUTHORITY_BOUNDARY_INVALID" in {
        item["code"] for item in nested_authority_audit["violations"]
    }
    mixed_semantics = lint_denominator_semantic_separation(
        [
            {
                "metric_ref": "eligible-rate",
                "metric_kind": "eligible_percent",
                "numerator_ref": "n:eligible",
                "denominator_ref": "n:all",
                "denominator_semantics_ref": "denom:all",
                "denominator_role": "all_records",
                "visual_semantic_ref": "bar:rate",
                "unit": "percent",
                "formula": {
                    "numerator_ref": "n:eligible",
                    "denominator_ref": "n:all",
                    "denominator_role": "all_records",
                    "unit": "percent",
                },
            },
            {
                "metric_ref": "resolved-rate",
                "metric_kind": "resolved_percent",
                "numerator_ref": "n:resolved",
                "denominator_ref": "n:all",
                "denominator_semantics_ref": "denom:all",
                "denominator_role": "candidate_records",
                "visual_semantic_ref": "bar:rate",
                "unit": "percent",
                "formula": {
                    "numerator_ref": "n:resolved",
                    "denominator_ref": "n:candidate",
                    "denominator_role": "candidate_records",
                    "unit": "percent",
                },
            },
            {
                "metric_ref": "flagged-volume",
                "metric_kind": "absolute_flagged_count",
                "numerator_ref": "n:flagged",
                "denominator_ref": "scope:generation",
                "denominator_semantics_ref": "scope:all-generation-records",
                "denominator_role": "generation_scope",
                "visual_semantic_ref": "bar:rate",
                "unit": "percent",
                "formula": {
                    "numerator_ref": "n:flagged",
                    "denominator_ref": "scope:generation",
                    "denominator_role": "generation_scope",
                    "unit": "count",
                },
            },
        ]
    )
    assert {item["code"] for item in mixed_semantics} >= {
        "AMBIGUOUS_PERCENT_COUNT_VISUAL_SEMANTIC",
        "AMBIGUOUS_PERCENT_COUNT_UNIT",
        "ABSOLUTE_COUNT_UNIT_INVALID",
        "FORMULA_DENOMINATOR_REF_MISMATCH",
        "FORMULA_UNIT_MISMATCH",
    }
    shared_denominator_is_valid = lint_denominator_semantic_separation(
        [
            {
                "metric_ref": "eligible-of-all",
                "metric_kind": "eligible_percent",
                "numerator_ref": "n:eligible",
                "denominator_ref": "n:all",
                "denominator_semantics_ref": "denom:all-records",
                "denominator_role": "all_records",
                "visual_semantic_ref": "rate:eligible-of-all",
                "unit": "percent",
                "formula": {
                    "numerator_ref": "n:eligible",
                    "denominator_ref": "n:all",
                    "denominator_role": "all_records",
                    "unit": "percent",
                },
            },
            {
                "metric_ref": "candidate-of-all",
                "metric_kind": "candidate_percent",
                "numerator_ref": "n:candidate",
                "denominator_ref": "n:all",
                "denominator_semantics_ref": "denom:all-records",
                "denominator_role": "all_records",
                "visual_semantic_ref": "rate:candidate-of-all",
                "unit": "percent",
                "formula": {
                    "numerator_ref": "n:candidate",
                    "denominator_ref": "n:all",
                    "denominator_role": "all_records",
                    "unit": "percent",
                },
            },
        ]
    )
    assert shared_denominator_is_valid == []
    separated_semantics = lint_denominator_semantic_separation(
        [
            {
                "metric_ref": "resolved-of-candidate",
                "metric_kind": "resolved_percent",
                "numerator_ref": "n:resolved",
                "denominator_ref": "n:candidate",
                "denominator_semantics_ref": "denom:candidate",
                "denominator_role": "candidate_records",
                "visual_semantic_ref": "rate:resolved-of-candidate",
                "unit": "percent",
                "formula": {
                    "numerator_ref": "n:resolved",
                    "denominator_ref": "n:candidate",
                    "denominator_role": "candidate_records",
                    "unit": "percent",
                },
            },
            {
                "metric_ref": "absolute-flagged-records",
                "metric_kind": "absolute_flagged_count",
                "numerator_ref": "n:flagged",
                "denominator_ref": "scope:generation",
                "denominator_semantics_ref": "scope:all-generation-records",
                "denominator_role": "generation_scope",
                "visual_semantic_ref": "count:absolute-flagged-records",
                "unit": "count",
                "formula": {
                    "numerator_ref": "n:flagged",
                    "denominator_ref": "scope:generation",
                    "denominator_role": "generation_scope",
                    "unit": "count",
                },
            },
        ]
    )
    assert separated_semantics == []
    assert all(item["writes_authority"] is False for item in mixed_semantics)

    validation_leakage = validate_validation_partition_integrity(
        {
            "development_partition_ref": "partition:centers-a-b",
            "validation_partition_ref": "partition:center-c",
            "partition_strategy": "center_disjoint",
            "partitions_disjoint": True,
            "claimed_validation_type": "external",
            "source_population_relation": "same_cohort_partition",
            "validation_outcome_ref": "outcome:validation-5y",
            "selection_decisions": [
                {
                    "decision_kind": "ridge_penalty_selection",
                    "metric_ref": "metric:validation-c-index",
                    "metric_partition": "validation",
                    "uses_validation_outcomes": True,
                }
            ],
            "authority": False,
        }
    )
    assert {item["code"] for item in validation_leakage["findings"]} >= {
        "VALIDATION_OUTCOME_USED_FOR_MODEL_SELECTION",
        "SAME_SOURCE_SPLIT_MISLABELED_AS_EXTERNAL_VALIDATION",
    }
    clean_internal_validation = validate_validation_partition_integrity(
        {
            "development_partition_ref": "partition:centers-a-b",
            "validation_partition_ref": "partition:center-c",
            "partition_strategy": "center_disjoint",
            "partitions_disjoint": True,
            "claimed_validation_type": "internal_external",
            "source_population_relation": "same_cohort_partition",
            "validation_outcome_ref": "outcome:validation-5y",
            "selection_decisions": [
                {
                    "decision_kind": "ridge_penalty_selection",
                    "metric_ref": "metric:development-cross-validation",
                    "metric_partition": "development_resampling",
                    "uses_validation_outcomes": False,
                }
            ],
            "authority": False,
        }
    )
    assert clean_internal_validation["machine_check_status"] == "candidate_complete"
    independent_external_center = validate_validation_partition_integrity(
        {
            "development_partition_ref": "partition:source-population-a",
            "validation_partition_ref": "partition:external-center-b",
            "partition_strategy": "center_disjoint",
            "partitions_disjoint": True,
            "claimed_validation_type": "external",
            "source_population_relation": "independently_assembled_external_population",
            "independent_external_cohort_ref": "cohort:external-center-b",
            "validation_outcome_ref": "outcome:external-5y",
            "selection_decisions": [
                {
                    "decision_kind": "no_tuning_prespecified",
                    "metric_ref": "policy:prespecified-model",
                    "metric_partition": "development",
                    "uses_validation_outcomes": False,
                }
            ],
            "authority": False,
        }
    )
    assert independent_external_center["machine_check_status"] == "candidate_complete"

    conflated_analysis_sets = validate_endpoint_analysis_set_reconciliation(
        {
            "rows": [
                {
                    "endpoint_id": "cvd-death-5y",
                    "endpoint_role": "primary",
                    "follow_up_basis": "fixed_horizon",
                    "analysis_set_ref": "set:7311",
                    "n": 7311,
                    "events": 48,
                    "estimand_ref": "estimand:unspecified",
                    "source_metric_ref": "metric:mixed-analysis-set",
                },
                {
                    "endpoint_id": "cvd-death-all-followup",
                    "endpoint_role": "primary",
                    "follow_up_basis": "fixed_horizon",
                    "analysis_set_ref": "set:7408",
                    "n": 7408,
                    "events": 50,
                    "estimand_ref": "estimand:unspecified",
                    "source_metric_ref": "metric:mixed-analysis-set",
                },
            ],
            "authority": False,
        }
    )
    assert "ENDPOINT_ANALYSIS_SET_ESTIMAND_SOURCE_CONFLATED" in {
        item["code"] for item in conflated_analysis_sets["findings"]
    }
    reconciled_analysis_sets = validate_endpoint_analysis_set_reconciliation(
        {
            "rows": [
                {
                    "endpoint_id": "cvd-death-5y",
                    "endpoint_role": "primary",
                    "follow_up_basis": "fixed_horizon",
                    "analysis_set_ref": "set:7311",
                    "n": 7311,
                    "events": 48,
                    "estimand_ref": "estimand:5y-cumulative-incidence",
                    "source_metric_ref": "metric:primary-5y",
                },
                {
                    "endpoint_id": "cvd-death-all-followup",
                    "endpoint_role": "secondary",
                    "follow_up_basis": "full_follow_up",
                    "analysis_set_ref": "set:7408",
                    "n": 7408,
                    "events": 50,
                    "estimand_ref": "estimand:cause-specific-hazard",
                    "source_metric_ref": "metric:secondary-full-followup",
                },
            ],
            "authority": False,
        }
    )
    assert reconciled_analysis_sets["machine_check_status"] == "candidate_complete"
    parallel_secondary_endpoints = validate_endpoint_analysis_set_reconciliation(
        {
            "rows": [
                {
                    "endpoint_id": "cvd-death-5y",
                    "endpoint_role": "primary",
                    "follow_up_basis": "fixed_horizon",
                    "analysis_set_ref": "set:cvd-death",
                    "n": 7210,
                    "events": 45,
                    "estimand_ref": "estimand:cvd-death-cumulative-incidence",
                    "source_metric_ref": "metric:cvd-death-5y",
                },
                {
                    "endpoint_id": "stroke-5y",
                    "endpoint_role": "secondary",
                    "follow_up_basis": "fixed_horizon",
                    "analysis_set_ref": "set:stroke",
                    "n": 7200,
                    "events": 31,
                    "estimand_ref": "estimand:stroke-cumulative-incidence",
                    "source_metric_ref": "metric:stroke-5y",
                },
                {
                    "endpoint_id": "mi-5y",
                    "endpoint_role": "secondary",
                    "follow_up_basis": "fixed_horizon",
                    "analysis_set_ref": "set:mi",
                    "n": 7190,
                    "events": 27,
                    "estimand_ref": "estimand:mi-cumulative-incidence",
                    "source_metric_ref": "metric:mi-5y",
                },
            ],
            "authority": False,
        }
    )
    assert parallel_secondary_endpoints["machine_check_status"] == (
        "candidate_complete"
    )

    sparse_model = validate_model_complexity_sparse_event(
        {
            "model_family": "Cox",
            "event_count": 52,
            "candidate_parameter_df": 30,
            "effective_parameter_df": 30,
            "continuous_predictor_count": 8,
            "sample_size_adequacy_method": "riley_pmsampsize",
            "separation_status": "detected",
            "penalty_source": "development_resampling",
            "ph_assessment_applicability": "required",
            "ph_assessment_ref": "diagnostic:ph",
            "nonlinearity_assessment_ref": "diagnostic:splines",
            "calibration_intercept_ref": "calibration:intercept",
            "calibration_slope_ref": "calibration:slope",
            "full_model_parameter_ref": "model:full-parameters",
            "authority": False,
        }
    )
    assert {item["code"] for item in sparse_model["findings"]} >= {
        "MODEL_FORMAL_ADEQUACY_EVIDENCE_MISSING",
        "MODEL_SEPARATION_ROUTE_BACK_REQUIRED",
    }
    formally_assessed_low_information_model = validate_model_complexity_sparse_event(
        {
            "model_family": "Cox",
            "event_count": 52,
            "candidate_parameter_df": 30,
            "effective_parameter_df": 30,
            "continuous_predictor_count": 8,
            "sample_size_adequacy_method": "owner_declared_equivalent",
            "sample_size_adequacy_inputs_ref": "adequacy:inputs",
            "sample_size_adequacy_result_ref": "adequacy:result",
            "expected_shrinkage_or_optimism_ref": "adequacy:expected-shrinkage",
            "observed_shrinkage_or_optimism_ref": "adequacy:bootstrap-optimism",
            "separation_status": "none",
            "penalty_source": "development_resampling",
            "ph_assessment_applicability": "required",
            "ph_assessment_ref": "diagnostic:ph",
            "nonlinearity_assessment_ref": "diagnostic:splines",
            "calibration_intercept_ref": "calibration:intercept",
            "calibration_slope_ref": "calibration:slope",
            "full_model_parameter_ref": "model:full-parameters",
            "authority": False,
        }
    )
    assert formally_assessed_low_information_model["machine_check_status"] == (
        "candidate_complete"
    )
    assert formally_assessed_low_information_model[
        "events_per_parameter_role"
    ] == "descriptive_only_not_adequacy_verdict"
    classification_without_continuous_predictors = validate_model_complexity_sparse_event(
        {
            "model_family": "logistic classification",
            "event_count": 120,
            "candidate_parameter_df": 6,
            "effective_parameter_df": 6,
            "continuous_predictor_count": 0,
            "sample_size_adequacy_method": "owner_declared_equivalent",
            "sample_size_adequacy_inputs_ref": "adequacy:classification-inputs",
            "sample_size_adequacy_result_ref": "adequacy:classification-result",
            "expected_shrinkage_or_optimism_ref": "adequacy:expected-shrinkage",
            "observed_shrinkage_or_optimism_ref": "adequacy:bootstrap-optimism",
            "separation_status": "none",
            "penalty_source": "prespecified",
            "ph_assessment_applicability": "not_applicable_with_reason",
            "ph_assessment_ref": {
                "status": "not_applicable_with_reason",
                "ref": "",
                "reason": "the logistic model is not a proportional-hazards model",
            },
            "nonlinearity_assessment_ref": {
                "status": "not_applicable_with_reason",
                "ref": "",
                "reason": "the model contains no continuous predictors",
            },
            "calibration_intercept_ref": "calibration:intercept",
            "calibration_slope_ref": "calibration:slope",
            "full_model_parameter_ref": "model:full-parameters",
            "authority": False,
        }
    )
    assert classification_without_continuous_predictors[
        "machine_check_status"
    ] == "candidate_complete"
    continuous_predictor_without_assessment = validate_model_complexity_sparse_event(
        {
            "model_family": "logistic classification",
            "event_count": 120,
            "candidate_parameter_df": 6,
            "effective_parameter_df": 6,
            "continuous_predictor_count": 2,
            "sample_size_adequacy_method": "owner_declared_equivalent",
            "sample_size_adequacy_inputs_ref": "adequacy:classification-inputs",
            "sample_size_adequacy_result_ref": "adequacy:classification-result",
            "expected_shrinkage_or_optimism_ref": "adequacy:expected-shrinkage",
            "observed_shrinkage_or_optimism_ref": "adequacy:bootstrap-optimism",
            "separation_status": "none",
            "penalty_source": "prespecified",
            "ph_assessment_applicability": "not_applicable_with_reason",
            "ph_assessment_ref": {
                "status": "not_applicable_with_reason",
                "ref": "",
                "reason": "the logistic model is not a proportional-hazards model",
            },
            "nonlinearity_assessment_ref": {
                "status": "not_applicable_with_reason",
                "ref": "",
                "reason": "not evaluated",
            },
            "calibration_intercept_ref": "calibration:intercept",
            "calibration_slope_ref": "calibration:slope",
            "full_model_parameter_ref": "model:full-parameters",
            "authority": False,
        }
    )
    assert "MODEL_DIAGNOSTIC_NOT_APPLICABLE_INVALID" in {
        item["code"]
        for item in continuous_predictor_without_assessment["findings"]
    }
    coxph_with_inconsistent_ph_disposition = validate_model_complexity_sparse_event(
        {
            "model_family": "CoxPH",
            "event_count": 120,
            "candidate_parameter_df": 6,
            "effective_parameter_df": 6,
            "continuous_predictor_count": 2,
            "sample_size_adequacy_method": "owner_declared_equivalent",
            "sample_size_adequacy_inputs_ref": "adequacy:coxph-inputs",
            "sample_size_adequacy_result_ref": "adequacy:coxph-result",
            "expected_shrinkage_or_optimism_ref": "adequacy:expected-shrinkage",
            "observed_shrinkage_or_optimism_ref": "adequacy:bootstrap-optimism",
            "separation_status": "none",
            "penalty_source": "prespecified",
            "ph_assessment_applicability": "required",
            "ph_assessment_ref": {
                "status": "not_applicable_with_reason",
                "ref": "",
                "reason": "incorrectly declared not applicable",
            },
            "nonlinearity_assessment_ref": "diagnostic:functional-form",
            "calibration_intercept_ref": "calibration:intercept",
            "calibration_slope_ref": "calibration:slope",
            "full_model_parameter_ref": "model:full-parameters",
            "authority": False,
        }
    )
    assert "MODEL_DIAGNOSTIC_NOT_APPLICABLE_INVALID" in {
        item["code"]
        for item in coxph_with_inconsistent_ph_disposition["findings"]
    }

    invalid_dca = validate_decision_curve_validity(
        {
            "prediction_horizon_ref": "horizon:5y",
            "censoring_before_horizon_count": 97,
            "censoring_method": "none_complete_follow_up",
            "analysis_set_policy": "complete_case_horizon_outcome",
            "uncertainty_method": "bootstrap",
            "uncertainty_interval_ref": "ci:bootstrap",
            "calibration_basis_ref": "calibration:unrecalibrated-risk",
            "calibration_basis_status": "unverified",
            "threshold_range_ref": "threshold:0.01-0.20",
            "net_benefit_source_ref": "metric:net-benefit",
            "clinical_action_scenarios": [
                {
                    "scenario_ref": "scenario:preventive-review",
                    "action_ref": "action:invite-review",
                }
            ],
            "authority": False,
        }
    )
    assert {item["code"] for item in invalid_dca["findings"]} >= {
        "DECISION_CURVE_EARLY_CENSORING_UNCORRECTED",
        "DECISION_CURVE_COMPLETE_CASE_WITH_EARLY_CENSORING",
        "DECISION_CURVE_CALIBRATION_BASIS_UNVERIFIED",
    }
    valid_dca = validate_decision_curve_validity(
        {
            "prediction_horizon_ref": "horizon:5y",
            "censoring_before_horizon_count": 97,
            "censoring_method": "ipcw",
            "analysis_set_policy": "ipcw_risk_set",
            "uncertainty_method": "bootstrap",
            "uncertainty_interval_ref": "ci:bootstrap-95",
            "calibration_basis_ref": "calibration:validated-absolute-risk",
            "calibration_basis_status": "validated_absolute_risk",
            "threshold_range_ref": "threshold:0.01-0.20",
            "net_benefit_source_ref": "metric:ipcw-net-benefit",
            "clinical_action_scenarios": [
                {
                    "scenario_ref": "scenario:preventive-review",
                    "action_ref": "action:invite-review",
                }
            ],
            "authority": False,
        }
    )
    assert valid_dca["machine_check_status"] == "candidate_complete"
    assert all(
        item["writes_authority"] is False
        for audit in (
            validation_leakage,
            conflated_analysis_sets,
            sparse_model,
            invalid_dca,
        )
        for item in audit["findings"]
    )
    print(json.dumps({"ok": True, "checks": 39}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
