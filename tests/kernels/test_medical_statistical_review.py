"""Extracted pytest suite for skills/medical-statistical-review/kernel.py."""

from __future__ import annotations

from collections.abc import Mapping
import json

from tests.kernels._loader import load_kernel

KERNEL = load_kernel("medical-statistical-review")
PREDICTION_CONTEXT_POLICY_ID = KERNEL.PREDICTION_CONTEXT_POLICY_ID
PREDICTION_SURFACE_NAMES = KERNEL.PREDICTION_SURFACE_NAMES
REGISTRY_SIGNAL_MEMBER_REFS = KERNEL.REGISTRY_SIGNAL_MEMBER_REFS
REGISTRY_SIGNAL_REF_FAMILY = KERNEL.REGISTRY_SIGNAL_REF_FAMILY
_prediction_limiting_phrase_supported = KERNEL._prediction_limiting_phrase_supported
construct_comparability_schema = KERNEL.construct_comparability_schema
fixed_horizon_risk_semantics_schema = KERNEL.fixed_horizon_risk_semantics_schema
lint_denominator_semantic_separation = KERNEL.lint_denominator_semantic_separation
lint_statistical_reporting = KERNEL.lint_statistical_reporting
missingness_plan_skeleton = KERNEL.missingness_plan_skeleton
normalize_model_family = KERNEL.normalize_model_family
reporting_checklist_skeleton = KERNEL.reporting_checklist_skeleton
statistical_review_schema = KERNEL.statistical_review_schema
validate_decision_curve_validity = KERNEL.validate_decision_curve_validity
validate_ehr_registry_signal_validity_candidate = KERNEL.validate_ehr_registry_signal_validity_candidate
validate_endpoint_analysis_set_reconciliation = KERNEL.validate_endpoint_analysis_set_reconciliation
validate_endpoint_analysis_set_reconciliation_v2 = KERNEL.validate_endpoint_analysis_set_reconciliation_v2
validate_fixed_horizon_risk_semantics = KERNEL.validate_fixed_horizon_risk_semantics
validate_linked_prediction_performance = KERNEL.validate_linked_prediction_performance
validate_linked_prediction_performance_v2 = KERNEL.validate_linked_prediction_performance_v2
validate_model_complexity_sparse_event = KERNEL.validate_model_complexity_sparse_event
validate_validation_partition_integrity = KERNEL.validate_validation_partition_integrity

def test_medical_statistical_review() -> None:
    def exact_ref(tag: str) -> dict[str, object]:
        return {
            "kind": "statistical_evidence",
            "ref": f"evidence://{tag}",
            "size_bytes": 100,
            "sha256": "sha256:" + "a" * 64,
        }

    def endpoint_support(
        n: int, events: int, *, fixed_horizon: bool = True
    ) -> dict[str, object]:
        competing_events = 96 if fixed_horizon else 0
        early_censoring_count = 1 if fixed_horizon else 0
        return {
            "competing_events": competing_events,
            "unknown_cause_count": 0,
            "early_censoring_count": early_censoring_count,
            "event_free_count": (
                n - events - competing_events - early_censoring_count
            ),
            "observed_risk_estimator": (
                "cumulative_incidence" if fixed_horizon else "not_applicable_with_reason"
            ),
            "observed_risk_ref": (
                exact_ref("risk-cumulative-incidence")
                if fixed_horizon
                else {
                    "status": "not_applicable_with_reason",
                    "ref": None,
                    "reason": "full-follow-up estimand has no fixed-horizon observed risk",
                }
            ),
            "prediction_error_estimator": (
                "ipcw_brier" if fixed_horizon else "not_applicable_with_reason"
            ),
            "prediction_error_ref": (
                exact_ref("prediction-error-ipcw-brier")
                if fixed_horizon
                else {
                    "status": "not_applicable_with_reason",
                    "ref": None,
                    "reason": "full-follow-up estimand has no fixed-horizon prediction error",
                }
            ),
        }

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

    legacy_endpoint_candidate = {
        "rows": [
            {
                "endpoint_id": "cvd-death-5y",
                "endpoint_role": "primary",
                "follow_up_basis": "fixed_horizon",
                "analysis_set_ref": "set:7408",
                "n": 7408,
                "events": 48,
                "estimand_ref": "estimand:5y-cumulative-incidence",
                "source_metric_ref": "metric:primary-5y",
            }
        ],
        "authority": False,
    }
    assert validate_endpoint_analysis_set_reconciliation(legacy_endpoint_candidate)[
        "machine_check_status"
    ] == "candidate_complete"
    assert validate_endpoint_analysis_set_reconciliation_v2(
        legacy_endpoint_candidate
    )["machine_check_status"] == "route_back_required"

    conflated_analysis_sets = validate_endpoint_analysis_set_reconciliation_v2(
        {
            "rows": [
                {
                    "endpoint_id": "cvd-death-5y",
                    "endpoint_role": "primary",
                    "follow_up_basis": "fixed_horizon",
                    "analysis_set_ref": "set:7311",
                    "n": 7311,
                    "events": 48,
                    **endpoint_support(7311, 48),
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
                    **endpoint_support(7408, 50),
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
    reconciled_analysis_sets = validate_endpoint_analysis_set_reconciliation_v2(
        {
            "rows": [
                {
                    "endpoint_id": "cvd-death-5y",
                    "endpoint_role": "primary",
                    "follow_up_basis": "fixed_horizon",
                    "analysis_set_ref": "set:7311",
                    "n": 7311,
                    "events": 48,
                    **endpoint_support(7311, 48),
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
                    **endpoint_support(7408, 50, fixed_horizon=False),
                    "estimand_ref": "estimand:cause-specific-hazard",
                    "source_metric_ref": "metric:secondary-full-followup",
                },
            ],
            "authority": False,
        }
    )
    assert reconciled_analysis_sets["machine_check_status"] == "candidate_complete"
    nonconserving_endpoint = validate_endpoint_analysis_set_reconciliation_v2(
        {
            "rows": [
                {
                    "endpoint_id": "cvd-death-5y",
                    "endpoint_role": "primary",
                    "follow_up_basis": "fixed_horizon",
                    "analysis_set_ref": "set:100",
                    "n": 100,
                    "events": 20,
                    "competing_events": 70,
                    "unknown_cause_count": 0,
                    "early_censoring_count": 20,
                    "event_free_count": 0,
                    "observed_risk_estimator": "cumulative_incidence",
                    "observed_risk_ref": exact_ref("risk-nonconserving"),
                    "prediction_error_estimator": "ipcw_brier",
                    "prediction_error_ref": exact_ref("error-nonconserving"),
                    "estimand_ref": "estimand:5y",
                    "source_metric_ref": "metric:5y",
                }
            ],
            "authority": False,
        }
    )
    assert "ENDPOINT_STATE_COUNT_CONSERVATION_VIOLATION" in {
        item["code"] for item in nonconserving_endpoint["findings"]
    }
    arbitrary_full_follow_up_ref = validate_endpoint_analysis_set_reconciliation_v2(
        {
            "rows": [
                {
                    "endpoint_id": "cvd-death-all-followup",
                    "endpoint_role": "primary",
                    "follow_up_basis": "full_follow_up",
                    "analysis_set_ref": "set:7408",
                    "n": 7408,
                    "events": 50,
                    "competing_events": 0,
                    "unknown_cause_count": 0,
                    "early_censoring_count": 0,
                    "event_free_count": 7358,
                    "observed_risk_estimator": "not_applicable_full_follow_up",
                    "observed_risk_ref": "not_applicable:full-follow-up",
                    "prediction_error_estimator": "not_applicable_full_follow_up",
                    "prediction_error_ref": "not_applicable:full-follow-up",
                    "estimand_ref": "estimand:cause-specific-hazard",
                    "source_metric_ref": "metric:secondary-full-followup",
                }
            ],
            "authority": False,
        }
    )
    assert "ENDPOINT_FULL_FOLLOW_UP_DISPOSITION_INVALID" in {
        item["code"] for item in arbitrary_full_follow_up_ref["findings"]
    }
    parallel_secondary_endpoints = validate_endpoint_analysis_set_reconciliation_v2(
        {
            "rows": [
                {
                    "endpoint_id": "cvd-death-5y",
                    "endpoint_role": "primary",
                    "follow_up_basis": "fixed_horizon",
                    "analysis_set_ref": "set:cvd-death",
                    "n": 7210,
                    "events": 45,
                    **endpoint_support(7210, 45),
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
                    **endpoint_support(7200, 31),
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
                    **endpoint_support(7190, 27),
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
    linked_performance = {
        "discrimination_metric_type": "time_dependent_auc",
        "discrimination_metric_ref": exact_ref("metric-auc"),
        "discrimination_estimate": 0.857,
        "discrimination_uncertainty_ref": exact_ref("ci-auc"),
        "brier_ref": exact_ref("metric-brier"),
        "brier_value": 0.00638,
        "null_brier_ref": exact_ref("metric-null-brier"),
        "null_brier_value": 0.00644,
        "ipa_ref": exact_ref("metric-ipa"),
        "ipa_value": 0.0082,
        "calibration_slope_ref": exact_ref("metric-calibration-slope"),
        "calibration_slope": 3.37,
        "calibration_intercept_ref": exact_ref("metric-calibration-intercept"),
        "calibration_intercept": 0.10,
        "oe_ratio_ref": exact_ref("metric-oe"),
        "oe_ratio": 1.30,
        "grouped_calibration_ref": exact_ref("metric-grouped-calibration"),
        "ipa_consistency_tolerance": 0.002,
        "calibration_reasonable_bounds": {
            "slope": [0.8, 1.2],
            "intercept": [-0.2, 0.2],
            "oe_ratio": [0.8, 1.2],
        },
        "performance_boundary": "ranking_only",
        "limiting_evidence": [
            {
                "metric_ref": exact_ref("metric-ipa"),
                "interpretation": "incremental prediction-error improvement is limited",
                "required_surface_phrase": "IPA 0.82%",
            },
            {
                "metric_ref": exact_ref("metric-calibration-slope"),
                "interpretation": "absolute-risk calibration is distorted",
                "required_surface_phrase": "calibration slope 3.37",
            },
        ],
        "surface_text": {
            "abstract_conclusion": "Ranking was promising, but IPA 0.82% and calibration slope 3.37 do not support reliable individual absolute risk.",
            "main_conclusion": "The model supports provisional ranking; IPA 0.82% and calibration slope 3.37 preclude threshold-based use.",
        },
        "authority": False,
    }
    linked_performance_audit = validate_linked_prediction_performance(
        linked_performance
    )
    assert linked_performance_audit["machine_check_status"] == "candidate_complete"
    not_estimable_grouped_calibration = json.loads(json.dumps(linked_performance))
    not_estimable_grouped_calibration["grouped_calibration_ref"] = {
        "status": "not_estimable_with_reason",
        "ref": None,
        "reason": "too few endpoint events for stable grouped calibration",
    }
    assert validate_linked_prediction_performance(not_estimable_grouped_calibration)[
        "machine_check_status"
    ] == "candidate_complete"
    not_estimable_calibration_slope = json.loads(json.dumps(linked_performance))
    not_estimable_calibration_slope["calibration_slope_ref"] = {
        "status": "not_estimable_with_reason",
        "ref": None,
        "reason": "calibration slope could not be estimated reliably",
    }
    not_estimable_calibration_slope["calibration_slope"] = None
    not_estimable_calibration_slope["limiting_evidence"] = [
        linked_performance["limiting_evidence"][0]
    ]
    not_estimable_calibration_slope["surface_text"] = {
        "abstract_conclusion": (
            "Ranking was promising, but IPA 0.82% does not support reliable "
            "individual absolute risk."
        ),
        "main_conclusion": "The model supports provisional ranking; IPA 0.82% precludes threshold-based use.",
    }
    assert validate_linked_prediction_performance(not_estimable_calibration_slope)[
        "machine_check_status"
    ] == "candidate_complete"
    malformed_metric_ref = json.loads(json.dumps(linked_performance))
    malformed_metric_ref["brier_ref"].pop("size_bytes")
    assert "PREDICTION_PERFORMANCE_REF_INVALID" in {
        item["code"]
        for item in validate_linked_prediction_performance(malformed_metric_ref)[
            "findings"
        ]
    }
    nan_metric = dict(linked_performance, brier_value=float("nan"))
    infinite_metric = dict(linked_performance, calibration_slope=float("inf"))
    for nonfinite_candidate in (nan_metric, infinite_metric):
        assert "PREDICTION_PERFORMANCE_VALUE_INVALID" in {
            item["code"]
            for item in validate_linked_prediction_performance(
                nonfinite_candidate
            )["findings"]
        }
    invalid_brier = dict(linked_performance, brier_value=1.1)
    zero_null_brier = dict(linked_performance, null_brier_value=0.0)
    ipa_mismatch = dict(linked_performance, ipa_value=0.5)
    assert "PREDICTION_BRIER_RANGE_INVALID" in {
        item["code"]
        for item in validate_linked_prediction_performance(invalid_brier)["findings"]
    }
    assert "PREDICTION_NULL_BRIER_RANGE_INVALID" in {
        item["code"]
        for item in validate_linked_prediction_performance(zero_null_brier)[
            "findings"
        ]
    }
    assert "PREDICTION_IPA_IDENTITY_MISMATCH" in {
        item["code"]
        for item in validate_linked_prediction_performance(ipa_mismatch)["findings"]
    }
    invalid_discrimination_type = dict(
        linked_performance, discrimination_metric_type="accuracy"
    )
    assert "PREDICTION_DISCRIMINATION_METRIC_TYPE_INVALID" in {
        item["code"]
        for item in validate_linked_prediction_performance(
            invalid_discrimination_type
        )["findings"]
    }
    invalid_discrimination_range = dict(
        linked_performance, discrimination_estimate=42
    )
    assert "PREDICTION_DISCRIMINATION_RANGE_INVALID" in {
        item["code"]
        for item in validate_linked_prediction_performance(
            invalid_discrimination_range
        )["findings"]
    }
    unsupported_limiting_locator = json.loads(json.dumps(linked_performance))
    unsupported_limiting_locator["limiting_evidence"][0]["metric_ref"] = exact_ref(
        "unrelated-metric"
    )
    assert "PREDICTION_LIMITING_EVIDENCE_METRIC_NOT_IN_PANEL" in {
        item["code"]
        for item in validate_linked_prediction_performance(
            unsupported_limiting_locator
        )["findings"]
    }
    arbitrary_string_limiting_ref = json.loads(json.dumps(linked_performance))
    arbitrary_string_limiting_ref["limiting_evidence"][0]["metric_ref"] = (
        "metric:ipa"
    )
    assert "PREDICTION_LIMITING_EVIDENCE_METRIC_REF_INVALID" in {
        item["code"]
        for item in validate_linked_prediction_performance(
            arbitrary_string_limiting_ref
        )["findings"]
    }
    unsupported_limiting_phrase = json.loads(json.dumps(linked_performance))
    unsupported_limiting_phrase["limiting_evidence"][0][
        "required_surface_phrase"
    ] = "model performance was limited"
    assert "PREDICTION_LIMITING_EVIDENCE_PHRASE_UNSUPPORTED" in {
        item["code"]
        for item in validate_linked_prediction_performance(
            unsupported_limiting_phrase
        )["findings"]
    }
    limiting_phrase_numeric_values = {
        field: value
        for field, value in (
            ("brier_value", linked_performance["brier_value"]),
            ("ipa_value", linked_performance["ipa_value"]),
            ("calibration_slope", linked_performance["calibration_slope"]),
            (
                "calibration_intercept",
                linked_performance["calibration_intercept"],
            ),
            ("oe_ratio", linked_performance["oe_ratio"]),
        )
        if isinstance(value, float)
    }
    for limiting_index, invalid_phrase in (
        (0, "IPA 0.0082%"),
        (0, "IPA -0.82%"),
        (0, "IPA 0.0082e3"),
        (1, "calibration slope 3.37%"),
        (1, "calibration slope -3.37"),
        (1, "calibration slope 3.37e2"),
    ):
        invalid_percentage_semantics = json.loads(json.dumps(linked_performance))
        invalid_percentage_semantics["limiting_evidence"][limiting_index][
            "required_surface_phrase"
        ] = invalid_phrase
        invalid_percentage_semantics["surface_text"] = {
            "abstract_conclusion": f"Ranking only; {invalid_phrase} limits use.",
            "main_conclusion": f"Ranking only; {invalid_phrase} precludes use.",
        }
        assert "PREDICTION_LIMITING_EVIDENCE_PHRASE_UNSUPPORTED" in {
            item["code"]
            for item in validate_linked_prediction_performance(
                invalid_percentage_semantics
            )["findings"]
        }
    assert _prediction_limiting_phrase_supported(
        "ipa_ref", "IPA 0.82%", limiting_phrase_numeric_values
    )
    assert _prediction_limiting_phrase_supported(
        "ipa_ref", "IPA 0.0082", limiting_phrase_numeric_values
    )
    assert _prediction_limiting_phrase_supported(
        "calibration_slope_ref",
        "calibration slope 3.37",
        limiting_phrase_numeric_values,
    )
    assert _prediction_limiting_phrase_supported(
        "calibration_slope_ref",
        "calibration slope 3.370e0",
        limiting_phrase_numeric_values,
    )
    good_performance_as_limit = json.loads(json.dumps(linked_performance))
    good_performance_as_limit.update(
        {
            "brier_value": 0.1,
            "null_brier_value": 0.2,
            "ipa_value": 0.5,
            "calibration_slope": 1.0,
            "calibration_intercept": 0.0,
            "oe_ratio": 1.0,
            "limiting_evidence": [
                {
                    "metric_ref": exact_ref("metric-brier"),
                    "interpretation": "the caller labels a well-performing metric as limiting",
                    "required_surface_phrase": "Brier 0.10",
                }
            ],
            "surface_text": {
                "abstract_conclusion": "Ranking only; Brier 0.10 was caller-labeled as limiting.",
                "main_conclusion": "Ranking only; Brier 0.10 was caller-labeled as limiting.",
            },
        }
    )
    assert {
        "PREDICTION_LIMITING_EVIDENCE_METRIC_NOT_IN_PANEL",
        "PREDICTION_RANKING_LIMITING_METRIC_MISSING",
    }.issubset(
        {
            item["code"]
            for item in validate_linked_prediction_performance(
                good_performance_as_limit
            )["findings"]
        }
    )
    limited_prediction_error_boundary = json.loads(json.dumps(linked_performance))
    limited_prediction_error_boundary.update(
        {
            "brier_value": 0.098,
            "null_brier_value": 0.1,
            "ipa_value": 0.02,
            "calibration_slope": 1.0,
            "calibration_intercept": 0.0,
            "oe_ratio": 1.0,
            "limiting_evidence": [
                {
                    "metric_ref": exact_ref("metric-ipa"),
                    "interpretation": "prediction-error improvement is at the kernel limit",
                    "required_surface_phrase": "IPA 2.00%",
                }
            ],
            "surface_text": {
                "abstract_conclusion": "Ranking only; IPA 2.00% limits absolute-risk use.",
                "main_conclusion": "Ranking only; IPA 2.00% precludes threshold use.",
            },
        }
    )
    assert validate_linked_prediction_performance(
        limited_prediction_error_boundary
    )["machine_check_status"] == "candidate_complete"
    adverse_calibration_boundary = json.loads(json.dumps(linked_performance))
    adverse_calibration_boundary.update(
        {
            "brier_value": 0.05,
            "null_brier_value": 0.1,
            "ipa_value": 0.5,
            "calibration_slope": 1.2001,
            "calibration_intercept": 0.0,
            "oe_ratio": 1.0,
            "limiting_evidence": [
                {
                    "metric_ref": exact_ref("metric-calibration-slope"),
                    "interpretation": "calibration slope is beyond the kernel bound",
                    "required_surface_phrase": "calibration slope 1.2001",
                }
            ],
            "surface_text": {
                "abstract_conclusion": "Ranking only; calibration slope 1.2001 limits absolute-risk use.",
                "main_conclusion": "Ranking only; calibration slope 1.2001 precludes threshold use.",
            },
        }
    )
    assert validate_linked_prediction_performance(adverse_calibration_boundary)[
        "machine_check_status"
    ] == "candidate_complete"
    caller_limiting_policy_override = dict(
        linked_performance, limited_prediction_error_ipa_upper_bound=0.9
    )
    assert "PREDICTION_LIMITING_POLICY_CALLER_OVERRIDE_FORBIDDEN" in {
        item["code"]
        for item in validate_linked_prediction_performance(
            caller_limiting_policy_override
        )["findings"]
    }
    slope_only_absolute_risk = dict(
        linked_performance,
        performance_boundary="absolute_risk_supported",
        calibration_slope=1.0,
        calibration_intercept=0.5,
        oe_ratio=1.5,
    )
    assert "ABSOLUTE_RISK_SUPPORT_CONTRADICTS_LINKED_PERFORMANCE" in {
        item["code"]
        for item in validate_linked_prediction_performance(
            slope_only_absolute_risk
        )["findings"]
    }
    caller_policy_override = dict(
        linked_performance,
        performance_boundary="absolute_risk_supported",
        ipa_value=0.04,
        ipa_consistency_tolerance=0.05,
        calibration_reasonable_bounds={
            "slope": [-100.0, 100.0],
            "intercept": [-100.0, 100.0],
            "oe_ratio": [-100.0, 100.0],
        },
    )
    caller_policy_override_codes = {
        item["code"]
        for item in validate_linked_prediction_performance(
            caller_policy_override
        )["findings"]
    }
    assert {
        "PREDICTION_IPA_TOLERANCE_CALLER_OVERRIDE_FORBIDDEN",
        "PREDICTION_CALIBRATION_BOUNDS_CALLER_OVERRIDE_FORBIDDEN",
        "PREDICTION_IPA_IDENTITY_MISMATCH",
        "ABSOLUTE_RISK_SUPPORT_CONTRADICTS_LINKED_PERFORMANCE",
    }.issubset(caller_policy_override_codes)
    hidden_limit = json.loads(json.dumps(linked_performance))
    hidden_limit["surface_text"]["abstract_conclusion"] = (
        "AUC 0.857 supports accurate individual absolute risk and clinical deployment."
    )
    hidden_limit_audit = validate_linked_prediction_performance(hidden_limit)
    assert {
        "PREDICTION_LIMIT_NOT_VISIBLE_ON_SURFACE",
        "PREDICTION_CLAIM_EXCEEDS_PERFORMANCE_BOUNDARY",
    }.issubset({item["code"] for item in hidden_limit_audit["findings"]})
    contextual = json.loads(json.dumps(good_performance_as_limit))
    contextual.pop("calibration_reasonable_bounds")
    contextual["clinical_assessment"] = {
        "study_ref": exact_ref("study-protocol"),
        "assessment_ref": exact_ref("prediction-performance-interpretation"),
        "population": "External validation cohort",
        "outcome": "Prespecified clinical endpoint",
        "prediction_horizon": "3 years",
        "intended_use": "Research ranking; individual risk counseling needs further evaluation",
        "calibration_status": "adequate",
        "calibration_rationale": "The linked curve and uncertainty support calibration in the evaluated range.",
        "prediction_error_status": "limited",
        "prediction_error_rationale": "Improvement over the null model remains insufficient for this intended use under the study assessment.",
        "metric_refs": {
            field: contextual[field]
            for field in ("brier_ref", "null_brier_ref", "ipa_ref", "calibration_slope_ref",
                          "calibration_intercept_ref", "oe_ratio_ref", "grouped_calibration_ref")
        },
        "surface_assessments": {
            surface: {
                "text": text,
                "performance_boundary": contextual["performance_boundary"],
                "clinical_use_claimed": False,
                "rationale": "The statement reports the research performance and its study-specific limitation.",
            }
            for surface, text in contextual["surface_text"].items()
        },
    }
    context_audit = validate_linked_prediction_performance_v2(contextual)
    assert context_audit["machine_check_status"] == "candidate_complete", context_audit
    assert "calibration_reasonable_bounds" not in context_audit
    assert context_audit["performance_policy_id"] == PREDICTION_CONTEXT_POLICY_ID

    def context_codes(value: Mapping[str, object]) -> set[str]:
        return {item["code"] for item in validate_linked_prediction_performance_v2(value)["findings"]}

    missing_context = dict(contextual, clinical_assessment=None)
    assert "PREDICTION_CLINICAL_ASSESSMENT_MISSING" in context_codes(missing_context)
    stale_context = json.loads(json.dumps(contextual))
    stale_context["clinical_assessment"]["metric_refs"]["ipa_ref"] = exact_ref("old-ipa")
    assert "PREDICTION_CLINICAL_ASSESSMENT_STALE" in context_codes(stale_context)
    unbound_context = json.loads(json.dumps(contextual))
    unbound_context["clinical_assessment"]["assessment_ref"] = "assessment.txt"
    assert "PREDICTION_CLINICAL_ASSESSMENT_REF_INVALID" in context_codes(unbound_context)
    assert "PREDICTION_IPA_IDENTITY_MISMATCH" in context_codes(dict(contextual, ipa_value=0.2))
    assert "PREDICTION_BRIER_RANGE_INVALID" in context_codes(dict(contextual, brier_value=1.1))
    assert "PREDICTION_CONTEXT_GLOBAL_BOUNDS_FORBIDDEN" in context_codes(
        dict(contextual, calibration_reasonable_bounds=linked_performance["calibration_reasonable_bounds"])
    )
    changed_text = json.loads(json.dumps(contextual))
    changed_text["surface_text"]["abstract_conclusion"] = "Clinical deployment is supported."
    assert "PREDICTION_SURFACE_ASSESSMENT_UNBOUND" in context_codes(changed_text)
    clinical_claim = json.loads(json.dumps(contextual))
    clinical_claim["clinical_assessment"]["surface_assessments"]["main_conclusion"]["clinical_use_claimed"] = True
    assert "PREDICTION_SURFACE_ASSESSMENT_UNBOUND" in context_codes(clinical_claim)
    absolute_context = json.loads(json.dumps(contextual))
    absolute_context.update(performance_boundary="absolute_risk_supported", calibration_slope=1.25, limiting_evidence=[])
    for surface in PREDICTION_SURFACE_NAMES:
        absolute_context["surface_text"][surface] = "Study-bound absolute-risk estimation is supported; clinical utility is not established."
        absolute_context["clinical_assessment"]["surface_assessments"][surface].update(
            text=absolute_context["surface_text"][surface], performance_boundary="absolute_risk_supported",
        )
    assert "ABSOLUTE_RISK_SUPPORT_CONTRADICTS_LINKED_PERFORMANCE" in context_codes(absolute_context)
    absolute_context["clinical_assessment"]["prediction_error_status"] = "adequate"
    absolute_context["clinical_assessment"]["prediction_error_rationale"] = "The protocol-specific error analysis supports the declared risk estimation scope."
    absolute_context["clinical_assessment"]["calibration_rationale"] = "The intended-use assessment accepts the linked slope 1.25, its uncertainty and curve for this research scope."
    assert validate_linked_prediction_performance_v2(absolute_context)["machine_check_status"] == "candidate_complete"
    assert "PREDICTION_OE_RATIO_RANGE_INVALID" in context_codes(dict(absolute_context, oe_ratio=-1.0))
    null_equivalent = dict(absolute_context, brier_value=0.2, null_brier_value=0.2, ipa_value=0.0)
    assert validate_linked_prediction_performance_v2(null_equivalent)["machine_check_status"] == "candidate_complete"
    absent_calibration = json.loads(json.dumps(contextual))
    for field in ("calibration_slope_ref", "calibration_intercept_ref", "oe_ratio_ref", "grouped_calibration_ref"):
        absent_calibration[field] = {"status": "not_estimable_with_reason", "reason": "insufficient data"}
        absent_calibration["clinical_assessment"]["metric_refs"][field] = absent_calibration[field]
    for field in ("calibration_slope", "calibration_intercept", "oe_ratio"):
        absent_calibration[field] = None
    assert "PREDICTION_CLINICAL_JUDGMENT_CONTRADICTS_AVAILABILITY" in context_codes(absent_calibration)
    missing_calibration = json.loads(json.dumps(absolute_context))
    missing_calibration["calibration_slope"] = None
    missing_calibration["calibration_slope_ref"] = {"status": "not_estimable_with_reason", "reason": "insufficient events"}
    missing_calibration["clinical_assessment"]["metric_refs"]["calibration_slope_ref"] = missing_calibration["calibration_slope_ref"]
    assert "ABSOLUTE_RISK_SUPPORT_CONTRADICTS_LINKED_PERFORMANCE" in context_codes(missing_calibration)
    assert all(
        item["writes_authority"] is False
        for audit in (
            validation_leakage,
            conflated_analysis_sets,
            sparse_model,
            invalid_dca,
            validate_linked_prediction_performance(caller_policy_override),
            hidden_limit_audit,
        )
        for item in audit["findings"]
    )
    print(json.dumps({"ok": True, "checks": 80, "study_context_cases": 15}, indent=2, sort_keys=True))
