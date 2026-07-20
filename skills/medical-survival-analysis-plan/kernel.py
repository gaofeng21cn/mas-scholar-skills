"""Deterministic refs-only helpers for survival analysis planning.

These helpers scaffold time-to-event schemas and reporting lint. They do not
approve analyses, write MAS truth, sign receipts, create blockers, or claim readiness.
"""

from __future__ import annotations

import json
import re
from typing import Any, Iterable, Mapping


SURVIVAL_SCHEMA_FIELDS = (
    "population_ref",
    "time_zero",
    "event_definition",
    "censoring_rule",
    "competing_event",
    "follow_up_horizon",
    "risk_set_rule",
)

COMPETING_EVENT_STATUSES = ("present", "absent_with_reason")
COMPETING_RISK_ESTIMANDS = (
    "cumulative_incidence",
    "cause_specific_hazard",
    "subdistribution_hazard",
    "not_applicable",
)
SURVIVAL_MODEL_FAMILIES = (
    "kaplan_meier",
    "cumulative_incidence",
    "cox",
    "fine_gray",
    "flexible_parametric",
    "other_regression",
)
REGRESSION_SURVIVAL_MODELS = {
    "cox",
    "fine_gray",
    "flexible_parametric",
    "other_regression",
}


def survival_schema_skeleton() -> dict[str, str]:
    """Return a time-zero/event/censoring schema shell."""
    out = {field: "" for field in SURVIVAL_SCHEMA_FIELDS}
    out["owner_gate_handoff_ref"] = ""
    return out


def follow_up_person_time_skeleton(groups: Iterable[str]) -> list[dict[str, object]]:
    """Create group-level follow-up/person-time rows."""
    return [
        {
            "group": group,
            "n_at_risk": None,
            "events": None,
            "censored": None,
            "person_time": None,
            "median_follow_up": None,
            "support_ref": "",
        }
        for group in groups
    ]


def survival_model_plan_skeleton(models: Iterable[str] | None = None) -> list[dict[str, str]]:
    """Return KM/Cox/competing-risk model-plan slots."""
    selected = list(models or ("Kaplan-Meier", "Cox", "competing_risk"))
    return [
        {
            "model": model,
            "estimand_or_measure": "",
            "covariates": "",
            "diagnostics": "",
            "sensitivity_ref": "",
        }
        for model in selected
    ]


def reporting_lint(text: str) -> list[dict[str, str]]:
    """Flag missing common survival-reporting elements in a plan."""
    lowered = (text or "").lower()
    checks = {
        "MISSING_TIME_ZERO": r"\b(time zero|index date|time origin)\b",
        "MISSING_CENSORING": r"\bcensor",
        "MISSING_RISK_SET": r"\brisk set|n at risk",
        "MISSING_KM_OR_CUMINC": r"\bkaplan|km\b|cumulative incidence",
        "MISSING_COX_OR_ALTERNATIVE": r"\bcox\b|fine-gray|parametric|landmark",
    }
    return [{"code": code, "route_back_candidate": ""} for code, pattern in checks.items() if not re.search(pattern, lowered)]


def survival_handoff_skeleton() -> dict[str, object]:
    """Return the standard refs-only survival-plan handoff shell."""
    return {
        "survival_question_ref": "",
        "time_origin_and_risk_set_ref": "",
        "endpoint_and_censoring_ref": "",
        "fixed_horizon_risk_semantics_ref": "",
        "competing_risk_ref": "",
        "model_plan_ref": "",
        "diagnostic_plan_ref": "",
        "decision_curve_validity_ref": "",
        "survival_support_map_ref": "",
        "candidate_refs": [],
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def validate_survival_estimand_plan(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Audit fixed-horizon and competing-risk plan semantics."""

    findings: list[dict[str, object]] = []
    for field in ("time_origin_ref", "censoring_assumption_ref"):
        if not str(candidate.get(field) or "").strip():
            findings.append(
                _survival_finding(
                    "SURVIVAL_REQUIRED_REF_MISSING",
                    field,
                    "bind the survival estimand to time origin and censoring evidence",
                )
            )
    reports_fixed_horizon = candidate.get("reports_fixed_horizon")
    if not isinstance(reports_fixed_horizon, bool):
        findings.append(
            _survival_finding(
                "FIXED_HORIZON_TRIGGER_INVALID",
                "reports_fixed_horizon",
                "declare whether the plan reports a fixed-horizon risk",
            )
        )
    elif reports_fixed_horizon:
        for field in ("prediction_horizon_ref", "fixed_horizon_risk_semantics_ref"):
            if not str(candidate.get(field) or "").strip():
                findings.append(
                    _survival_finding(
                        "FIXED_HORIZON_REQUIRED_REF_MISSING",
                        field,
                        "bind fixed-horizon output to a horizon and censoring-aware risk semantics ref",
                    )
                )
    elif not str(candidate.get("fixed_horizon_not_applicable_reason") or "").strip():
        findings.append(
            _survival_finding(
                "FIXED_HORIZON_NOT_APPLICABLE_REASON_MISSING",
                "fixed_horizon_not_applicable_reason",
                "state why no fixed-horizon risk is reported",
            )
        )
    competing_status = str(candidate.get("competing_event_status") or "")
    competing_estimand = str(candidate.get("competing_risk_estimand") or "")
    if competing_status not in COMPETING_EVENT_STATUSES:
        findings.append(
            _survival_finding(
                "COMPETING_EVENT_STATUS_INVALID",
                "competing_event_status",
                "declare present or absent_with_reason",
            )
        )
    if competing_estimand not in COMPETING_RISK_ESTIMANDS:
        findings.append(
            _survival_finding(
                "COMPETING_RISK_ESTIMAND_INVALID",
                "competing_risk_estimand",
                "declare cumulative incidence, cause-specific hazard, subdistribution hazard, or not_applicable",
            )
        )
    primary_estimator = str(candidate.get("primary_risk_estimator") or "").lower()
    model_family = str(candidate.get("model_family") or "").lower()
    if model_family not in SURVIVAL_MODEL_FAMILIES:
        findings.append(
            _survival_finding(
                "SURVIVAL_MODEL_FAMILY_INVALID",
                "model_family",
                "declare the survival estimator or regression model family",
            )
        )
    if competing_status == "present":
        if competing_estimand == "not_applicable":
            findings.append(
                _survival_finding(
                    "COMPETING_RISK_ESTIMAND_MISSING",
                    "competing_risk_estimand",
                    "choose a competing-risk estimand for the stated endpoint",
                )
            )
        if primary_estimator in {"kaplan_meier", "1-kaplan_meier", "1-km"}:
            findings.append(
                _survival_finding(
                    "KAPLAN_MEIER_RISK_WITH_COMPETING_EVENT",
                    "primary_risk_estimator",
                    "use cumulative incidence for absolute risk when competing events are present",
                )
            )
    elif competing_status == "absent_with_reason":
        if not str(candidate.get("competing_event_reason") or "").strip():
            findings.append(
                _survival_finding(
                    "COMPETING_EVENT_NOT_APPLICABLE_REASON_MISSING",
                    "competing_event_reason",
                    "state why no competing event applies",
                )
            )
        if competing_estimand != "not_applicable":
            findings.append(
                _survival_finding(
                    "COMPETING_RISK_ESTIMAND_CONTRADICTS_ABSENCE",
                    "competing_risk_estimand",
                    "use not_applicable when competing events are absent with a reason",
                )
            )
    if model_family in REGRESSION_SURVIVAL_MODELS:
        for field in (
            "ph_assessment",
            "functional_form_assessment",
            "calibration_assessment",
            "sparse_event_assessment",
        ):
            _validate_survival_evidence_item(candidate.get(field), field, findings)

    reports_dca = candidate.get("reports_dca")
    if not isinstance(reports_dca, bool):
        findings.append(
            _survival_finding(
                "SURVIVAL_DCA_TRIGGER_INVALID",
                "reports_dca",
                "declare whether decision-curve analysis is reported",
            )
        )
    elif reports_dca:
        if not str(candidate.get("decision_curve_validity_ref") or "").strip():
            findings.append(
                _survival_finding(
                    "SURVIVAL_DCA_VALIDITY_REF_MISSING",
                    "decision_curve_validity_ref",
                    "bind reported DCA to the statistical decision-curve validity ref",
                )
            )
    elif not str(candidate.get("dca_not_applicable_reason") or "").strip():
        findings.append(
            _survival_finding(
                "SURVIVAL_DCA_NOT_APPLICABLE_REASON_MISSING",
                "dca_not_applicable_reason",
                "state why DCA is not reported",
            )
        )
    if candidate.get("authority") is not False:
        findings.append(
            _survival_finding(
                "SURVIVAL_PLAN_AUTHORITY_FORBIDDEN",
                "authority",
                "keep the plan refs-only with authority=false",
            )
        )
    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "survival_estimand_plan_ref",
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "findings": findings,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-survival-analysis-plan",
            "reason": "survival_estimand_plan_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def _validate_survival_evidence_item(
    value: object,
    field: str,
    findings: list[dict[str, object]],
) -> None:
    if not isinstance(value, Mapping):
        findings.append(
            _survival_finding(
                "SURVIVAL_MODEL_ASSESSMENT_MISSING",
                field,
                "provide present evidence or not_applicable_with_reason",
            )
        )
        return
    if set(value) != {"status", "ref", "reason"}:
        findings.append(
            _survival_finding(
                "SURVIVAL_MODEL_ASSESSMENT_FIELDS_INVALID",
                field,
                "use exactly status, ref, and reason",
            )
        )
    status = str(value.get("status") or "")
    ref = str(value.get("ref") or "").strip()
    reason = str(value.get("reason") or "").strip()
    if status == "present":
        if not ref or reason:
            findings.append(
                _survival_finding(
                    "SURVIVAL_MODEL_ASSESSMENT_PRESENT_INVALID",
                    field,
                    "bind a non-empty ref and leave reason empty",
                )
            )
    elif status == "not_applicable_with_reason":
        if ref or not reason:
            findings.append(
                _survival_finding(
                    "SURVIVAL_MODEL_ASSESSMENT_NOT_APPLICABLE_INVALID",
                    field,
                    "leave ref empty and state the model-specific reason",
                )
            )
    else:
        findings.append(
            _survival_finding(
                "SURVIVAL_MODEL_ASSESSMENT_STATUS_INVALID",
                f"{field}.status",
                "use present or not_applicable_with_reason",
            )
        )


def _survival_finding(code: str, field: str, action: str) -> dict[str, object]:
    return {
        "code": code,
        "field": field,
        "action": action,
        "writes_authority": False,
    }


def _self_check() -> None:
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


if __name__ == "__main__":
    _self_check()
