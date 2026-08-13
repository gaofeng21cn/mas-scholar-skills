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
INTERVENTIONAL_DESIGN_FIELDS = (
    "intervention_and_comparator",
    "allocation_sequence",
    "allocation_concealment",
    "randomization_unit_and_stratification",
    "blinding",
    "controlled_unblinding",
    "adherence_and_accountability",
    "concomitant_care",
    "protocol_deviations",
)
SAFETY_OVERSIGHT_FIELDS = (
    "ae_definition_and_collection_window",
    "sae_definition_and_collection_window",
    "expedited_reporting_route",
    "dsmb_or_independent_monitoring",
    "interim_analysis",
    "stopping_rules",
    "medical_monitoring",
    "intervention_or_device_accountability",
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


def interventional_design_checklist_skeleton() -> list[dict[str, str]]:
    """Return drug/device interventional-design candidate slots."""
    return [
        {
            "item": item,
            "candidate_value": "",
            "current_source_ref": "",
            "owner_or_regulatory_decision_ref": "",
        }
        for item in INTERVENTIONAL_DESIGN_FIELDS
    ]


def schedule_of_activities_skeleton(visits: Iterable[str]) -> list[dict[str, object]]:
    """Return visit rows without inventing assessments or windows."""
    return [
        {
            "visit": visit,
            "target_day": None,
            "window": "",
            "intervention_or_device_activity_refs": [],
            "efficacy_assessment_refs": [],
            "safety_assessment_refs": [],
            "specimen_refs": [],
            "early_withdrawal_or_followup_ref": "",
        }
        for visit in visits
    ]


def safety_oversight_checklist_skeleton() -> list[dict[str, str]]:
    """Return AE/SAE, monitoring, and stopping-rule candidate slots."""
    return [
        {
            "item": item,
            "candidate_value": "",
            "current_source_ref": "",
            "owner_or_regulatory_decision_ref": "",
        }
        for item in SAFETY_OVERSIGHT_FIELDS
    ]


def trial_registry_evidence_map_skeleton(source_roles: Iterable[str]) -> list[dict[str, str]]:
    """Return current-source evidence rows without claiming registry compliance."""
    return [
        {
            "source_role": source_role,
            "source_ref": "",
            "retrieved_at": "",
            "scope": "",
            "currentness_status": "unverified",
            "owner_or_regulatory_decision_ref": "",
        }
        for source_role in source_roles
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
        "interventional_design_ref": "",
        "schedule_of_activities_ref": "",
        "safety_oversight_ref": "",
        "trial_registry_evidence_map_ref": "",
        "support_map_ref": "",
        "candidate_refs": [],
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def _self_check() -> None:
    assert pico_skeleton("q1")["protocol_question_ref"] == "q1"
    assert estimand_checklist_skeleton()[0]["item"] == "treatment_condition"
    assert endpoint_sap_checklist_skeleton(["endpoint"])[0]["item"] == "endpoint"
    assert interventional_design_checklist_skeleton()[2]["item"] == "allocation_concealment"
    assert schedule_of_activities_skeleton(["baseline"])[0]["target_day"] is None
    assert safety_oversight_checklist_skeleton()[0]["item"] == "ae_definition_and_collection_window"
    assert trial_registry_evidence_map_skeleton(["trial_registry"])[0]["currentness_status"] == "unverified"
    assert "sap_candidate_ref" in protocol_handoff_skeleton()
    assert "trial_registry_evidence_map_ref" in protocol_handoff_skeleton()
    print(json.dumps({"ok": True, "checks": 9}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
