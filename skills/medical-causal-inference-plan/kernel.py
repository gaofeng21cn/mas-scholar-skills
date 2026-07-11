"""Deterministic refs-only helpers for causal inference planning.

These helpers scaffold DAG, estimand, and bias-check candidates. They do not
claim causality, approve analyses, sign receipts, create blockers, or claim readiness.
"""

from __future__ import annotations

import json
import re
from typing import Iterable, Mapping


DAG_EDGE_RE = re.compile(r"([A-Za-z][A-Za-z0-9_ .-]*?)\s*(?:->|=>|causes)\s*([A-Za-z][A-Za-z0-9_ .-]*)")
ESTIMAND_FIELDS = ("population", "exposure", "comparator", "outcome", "time_zero", "follow_up", "contrast")
BIAS_TERMS = {
    "confounding": ("confound", "exchangeability", "baseline imbalance"),
    "positivity": ("positivity", "overlap", "sparse exposure"),
    "selection_bias": ("selection", "collider"),
    "immortal_time": ("immortal time",),
    "informative_censoring": ("informative censor",),
}


def parse_dag_edges(text: str) -> list[dict[str, str]]:
    """Parse simple DAG edge text such as 'A -> B; C causes D'."""
    edges = []
    for source, target in DAG_EDGE_RE.findall(text or ""):
        edges.append(
            {
                "source": re.sub(r"\s+", " ", source).strip(),
                "target": re.sub(r"\s+", " ", target).strip().rstrip(".,;"),
                "edge_ref": "",
            }
        )
    return edges


def dag_skeleton(edges: Iterable[Mapping[str, object]] | None = None) -> dict[str, object]:
    """Return a refs-only DAG/confounder-map shell."""
    return {
        "dag_or_confounder_map_ref": "",
        "edges": list(edges or []),
        "baseline_confounders": [],
        "mediators": [],
        "colliders": [],
        "unavailable_variable_caveats": [],
        "owner_gate_handoff_ref": "",
    }


def estimand_checklist_skeleton() -> list[dict[str, str]]:
    """Return causal estimand checklist slots."""
    return [{"item": field, "candidate_value": "", "support_ref": "", "owner_decision_ref": ""} for field in ESTIMAND_FIELDS]


def bias_flag_lint(text: str) -> list[dict[str, str]]:
    """Flag causal-design risk vocabulary present in free text."""
    lowered = (text or "").lower()
    findings = []
    for code, terms in BIAS_TERMS.items():
        matched = [term for term in terms if term in lowered]
        if matched:
            findings.append({"code": code.upper(), "matched": ", ".join(matched), "route_back_candidate": ""})
    return findings


def causal_handoff_skeleton() -> dict[str, object]:
    """Return the standard refs-only causal-plan handoff shell."""
    return {
        "causal_question_ref": "",
        "target_trial_candidate_ref": "",
        "estimand_ref": "",
        "dag_or_confounder_map_ref": "",
        "bias_and_identifiability_ref": "",
        "sensitivity_plan_ref": "",
        "claim_strength_calibration_ref": "",
        "candidate_refs": [],
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def _self_check() -> None:
    edges = parse_dag_edges("Age -> Treatment; Treatment causes Outcome.")
    assert edges[0]["source"] == "Age"
    assert edges[1]["target"] == "Outcome"
    assert dag_skeleton(edges)["edges"][0]["target"] == "Treatment"
    assert estimand_checklist_skeleton()[0]["item"] == "population"
    assert bias_flag_lint("check positivity and confounding")[0]["code"] == "CONFOUNDING"
    assert "sensitivity_plan_ref" in causal_handoff_skeleton()
    print(json.dumps({"ok": True, "checks": 6}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
