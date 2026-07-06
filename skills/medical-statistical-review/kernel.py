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
            "route_back_candidate": {"type": "string"},
        },
    }


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


def _finding(ref: str, code: str, action: str) -> dict[str, str]:
    return {"claim_ref": ref, "code": code, "action": action}


def _self_check() -> None:
    assert "analysis_plan_ref" in statistical_review_schema()["required"]
    assert normalize_model_family("Cox proportional hazards") == "survival"
    assert reporting_checklist_skeleton(["c1"])[0]["claim_ref"] == "c1"
    assert missingness_plan_skeleton(["age"])[0]["variable"] == "age"
    lint = lint_statistical_reporting(
        [{"claim_ref": "c1", "claim": "p=0.03 with missingness noted"}]
    )
    assert {item["code"] for item in lint} >= {"P_VALUE_ALONE", "MISSINGNESS_STRATEGY_MISSING"}
    print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
