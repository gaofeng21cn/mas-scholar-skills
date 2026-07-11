"""Deterministic refs-only helpers for protocol and SAP planning.

These helpers create checklist skeletons only. They do not approve studies,
write MAS truth, sign owner receipts, create typed blockers, or claim readiness.
"""

from __future__ import annotations

import json
from typing import Iterable


PICO_FIELDS = ("population", "intervention_or_exposure", "comparator", "outcome", "time_horizon")
ESTIMAND_FIELDS = (
    "treatment_condition",
    "population",
    "variable_or_endpoint",
    "intercurrent_events",
    "population_level_summary",
)
SAP_FIELDS = (
    "analysis_set",
    "endpoint_definition",
    "covariate_plan",
    "missingness_plan",
    "multiplicity_plan",
    "subgroup_plan",
    "sensitivity_plan",
)


def pico_skeleton(question_ref: str = "") -> dict[str, str]:
    """Return a PICO/PECO shell for a protocol question."""
    out = {field: "" for field in PICO_FIELDS}
    out["protocol_question_ref"] = question_ref
    out["owner_gate_handoff_ref"] = ""
    return out


def estimand_checklist_skeleton() -> list[dict[str, str]]:
    """Return ICH E9-style estimand checklist slots."""
    return [{"item": field, "candidate_value": "", "support_ref": "", "owner_decision_ref": ""} for field in ESTIMAND_FIELDS]


def endpoint_sap_checklist_skeleton(items: Iterable[str] | None = None) -> list[dict[str, str]]:
    """Return endpoint/SAP checklist slots."""
    selected = list(items or SAP_FIELDS)
    return [
        {
            "item": item,
            "candidate_value": "",
            "support_ref": "",
            "missing_or_owner_decision": "",
        }
        for item in selected
    ]


def protocol_handoff_skeleton() -> dict[str, object]:
    """Return the standard refs-only protocol/SAP handoff shell."""
    return {
        "protocol_question_ref": "",
        "protocol_scope_ref": "",
        "eligibility_and_flow_ref": "",
        "endpoint_definition_ref": "",
        "estimand_and_analysis_set_ref": "",
        "sap_candidate_ref": "",
        "missingness_and_sensitivity_ref": "",
        "reporting_guideline_ref": "",
        "support_map_ref": "",
        "candidate_refs": [],
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def _self_check() -> None:
    assert pico_skeleton("q1")["protocol_question_ref"] == "q1"
    assert estimand_checklist_skeleton()[0]["item"] == "treatment_condition"
    assert endpoint_sap_checklist_skeleton(["endpoint"])[0]["item"] == "endpoint"
    assert "sap_candidate_ref" in protocol_handoff_skeleton()
    print(json.dumps({"ok": True, "checks": 4}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
