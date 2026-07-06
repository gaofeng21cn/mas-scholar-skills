"""Deterministic refs-only helpers for survival analysis planning.

These helpers scaffold time-to-event schemas and reporting lint. They do not
approve analyses, write MAS truth, sign receipts, create blockers, or claim readiness.
"""

from __future__ import annotations

import json
import re
from typing import Iterable


SURVIVAL_SCHEMA_FIELDS = (
    "population_ref",
    "time_zero",
    "event_definition",
    "censoring_rule",
    "competing_event",
    "follow_up_horizon",
    "risk_set_rule",
)


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
        "competing_risk_ref": "",
        "model_plan_ref": "",
        "diagnostic_plan_ref": "",
        "survival_support_map_ref": "",
        "candidate_package_ref": "",
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def _self_check() -> None:
    assert survival_schema_skeleton()["time_zero"] == ""
    assert follow_up_person_time_skeleton(["treated"])[0]["events"] is None
    assert survival_model_plan_skeleton(["Cox"])[0]["model"] == "Cox"
    assert reporting_lint("time zero, censoring, risk set, KM, Cox") == []
    assert reporting_lint("KM only")[0]["code"] == "MISSING_TIME_ZERO"
    assert "model_plan_ref" in survival_handoff_skeleton()
    print(json.dumps({"ok": True, "checks": 6}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
