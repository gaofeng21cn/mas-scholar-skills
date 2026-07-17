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
    print(json.dumps({"ok": True, "checks": 15}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
