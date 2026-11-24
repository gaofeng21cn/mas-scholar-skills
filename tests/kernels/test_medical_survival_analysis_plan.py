"""Extracted pytest suite for skills/medical-survival-analysis-plan/kernel.py."""

from __future__ import annotations

import json

from tests.kernels._loader import load_kernel

KERNEL = load_kernel("medical-survival-analysis-plan")
follow_up_person_time_skeleton = KERNEL.follow_up_person_time_skeleton
reporting_lint = KERNEL.reporting_lint
survival_handoff_skeleton = KERNEL.survival_handoff_skeleton
survival_model_plan_skeleton = KERNEL.survival_model_plan_skeleton
survival_schema_skeleton = KERNEL.survival_schema_skeleton
validate_survival_estimand_plan = KERNEL.validate_survival_estimand_plan

def test_medical_survival_analysis_plan() -> None:
    assert survival_schema_skeleton()["time_zero"] == ""
    assert follow_up_person_time_skeleton(["treated"])[0]["events"] is None
    assert survival_model_plan_skeleton(["Cox"])[0]["model"] == "Cox"
    assert reporting_lint("time zero, censoring, risk set, KM, Cox") == []
    assert reporting_lint("KM only")[0]["code"] == "MISSING_TIME_ZERO"
    assert "model_plan_ref" in survival_handoff_skeleton()
    assert "fixed_horizon_risk_semantics_ref" in survival_handoff_skeleton()
    assert "decision_curve_validity_ref" in survival_handoff_skeleton()
    competing_event_failure = validate_survival_estimand_plan(
        {
            "time_origin_ref": "time:index",
            "reports_fixed_horizon": True,
            "prediction_horizon_ref": "horizon:5y",
            "fixed_horizon_risk_semantics_ref": "risk:5y-censoring-aware",
            "censoring_assumption_ref": "assumption:independent",
            "competing_event_status": "present",
            "competing_risk_estimand": "not_applicable",
            "primary_risk_estimator": "kaplan_meier",
            "model_family": "cumulative_incidence",
            "reports_dca": False,
            "dca_not_applicable_reason": "the plan does not report clinical utility",
            "authority": False,
        }
    )
    assert {item["code"] for item in competing_event_failure["findings"]} >= {
        "COMPETING_RISK_ESTIMAND_MISSING",
        "KAPLAN_MEIER_RISK_WITH_COMPETING_EVENT",
    }
    valid_competing_risk = validate_survival_estimand_plan(
        {
            "time_origin_ref": "time:index",
            "reports_fixed_horizon": True,
            "prediction_horizon_ref": "horizon:5y",
            "fixed_horizon_risk_semantics_ref": "risk:5y-censoring-aware",
            "censoring_assumption_ref": "assumption:independent",
            "competing_event_status": "present",
            "competing_risk_estimand": "cumulative_incidence",
            "primary_risk_estimator": "cumulative_incidence",
            "model_family": "cumulative_incidence",
            "reports_dca": False,
            "dca_not_applicable_reason": "the plan does not report clinical utility",
            "authority": False,
        }
    )
    assert valid_competing_risk["machine_check_status"] == "candidate_complete"
    valid_km_without_horizon_or_dca = validate_survival_estimand_plan(
        {
            "time_origin_ref": "time:index",
            "reports_fixed_horizon": False,
            "fixed_horizon_not_applicable_reason": "the estimand is median survival",
            "censoring_assumption_ref": "assumption:independent",
            "competing_event_status": "absent_with_reason",
            "competing_event_reason": "all-cause mortality has no competing death event",
            "competing_risk_estimand": "not_applicable",
            "primary_risk_estimator": "kaplan_meier",
            "model_family": "kaplan_meier",
            "reports_dca": False,
            "dca_not_applicable_reason": "the plan does not report threshold utility",
            "authority": False,
        }
    )
    assert valid_km_without_horizon_or_dca["machine_check_status"] == (
        "candidate_complete"
    )
    print(json.dumps({"ok": True, "checks": 12}, indent=2, sort_keys=True))
