"""Deterministic helper for risk-model transportability review refs.

This helper is skill-local and no-authority. It does not accept models, compute
clinical verdicts, write MAS truth, sign owner receipts, or claim readiness.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


REQUIRED_REFS = (
    "source_model_ref",
    "target_population_ref",
    "predictor_mapping_ref",
    "fixed_horizon_risk_semantics_ref",
    "construct_comparability_ref",
    "transportability_assessment_ref",
    "calibration_and_performance_ref",
    "clinical_utility_boundary_ref",
)

CONSTRUCT_COMPARABILITY_LAYERS = (
    "codebook",
    "identity_linkage",
    "field_role",
    "accepted_mapping",
    "current_evidence",
)
CONSTRUCT_LAYER_STATUSES = {
    "codebook": {"present", "absent"},
    "identity_linkage": {"identity_preserving", "absent"},
    "field_role": {"accepted", "unaccepted"},
    "accepted_mapping": {"accepted", "unaccepted"},
    "current_evidence": {"current", "stale"},
}
CONSTRUCT_LAYER_PASS_STATUS = {
    "codebook": "present",
    "identity_linkage": "identity_preserving",
    "field_role": "accepted",
    "accepted_mapping": "accepted",
    "current_evidence": "current",
}
CONSTRUCT_LAYER_STOP_CODES = {
    "codebook": "codebook_absent",
    "identity_linkage": "identity_linkage_absent",
    "field_role": "field_role_unaccepted",
    "accepted_mapping": "accepted_mapping_absent",
    "current_evidence": "current_evidence_stale",
}
CONSTRUCT_EXACT_REF_FIELDS = frozenset({"kind", "ref", "size_bytes", "sha256"})


def normalize_predictor_name(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return re.sub(r"_+", "_", text).strip("_")


def predictor_mapping_row(source: str, target: str, *, status: str = "needs_review") -> dict[str, Any]:
    return {
        "source_predictor": source.strip(),
        "source_predictor_key": normalize_predictor_name(source),
        "target_variable": target.strip(),
        "target_variable_key": normalize_predictor_name(target),
        "mapping_status": status,
        "writes_authority": False,
    }


def transportability_review_skeleton(model_ref: str, target_ref: str) -> dict[str, Any]:
    return {
        "surface_kind": "risk_model_transportability_review_candidate",
        "model_ref": model_ref,
        "target_population_ref": target_ref,
        "required_refs": list(REQUIRED_REFS),
        "candidate_refs": {ref: None for ref in REQUIRED_REFS},
        "route_back_candidate": None,
        "owner_gate_handoff_ref": None,
        "authority": {
            "refs_only": True,
            "can_accept_model": False,
            "can_write_mas_truth": False,
            "can_sign_owner_receipt": False,
            "can_create_typed_blocker": False,
            "can_claim_readiness": False,
        },
    }


def lint_forbidden_authority_claims(text: str) -> list[dict[str, str]]:
    patterns = {
        "MODEL_ACCEPTANCE": r"\b(model accepted|model is valid|transportable)\b",
        "OWNER_RECEIPT": r"\bowner receipt\b",
        "TYPED_BLOCKER": r"\btyped blocker\b",
        "READINESS": r"\b(publication|analysis|source)-ready\b",
    }
    return [
        {"code": code, "match": pattern}
        for code, pattern in patterns.items()
        if re.search(pattern, text, flags=re.I)
    ]


def validate_construct_comparability_currentness(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Audit layered stop reasons and invalidate claims superseded by evidence."""

    findings: list[dict[str, object]] = []
    if candidate.get("surface_kind") != "construct_comparability_currentness_candidate.v1":
        findings.append(
            _construct_finding(
                "CONSTRUCT_SURFACE_KIND_INVALID",
                "surface_kind",
                "use the construct-comparability currentness candidate surface",
            )
        )
    construct_id = str(candidate.get("construct_id") or "").strip()
    if not construct_id:
        findings.append(
            _construct_finding(
                "CONSTRUCT_ID_MISSING",
                "construct_id",
                "bind the audit to one stable construct id",
            )
        )
    evidence_generation = candidate.get("evidence_generation")
    if (
        isinstance(evidence_generation, bool)
        or not isinstance(evidence_generation, int)
        or evidence_generation < 1
    ):
        findings.append(
            _construct_finding(
                "CONSTRUCT_EVIDENCE_GENERATION_INVALID",
                "evidence_generation",
                "use a positive integer evidence generation",
            )
        )
        evidence_generation = 0

    layers_value = candidate.get("layers")
    layers = layers_value if isinstance(layers_value, Mapping) else {}
    if set(layers) != set(CONSTRUCT_COMPARABILITY_LAYERS):
        findings.append(
            _construct_finding(
                "CONSTRUCT_LAYER_SET_INVALID",
                "layers",
                "provide exactly the five construct-comparability evidence layers",
            )
        )
    failing_layers: set[str] = set()
    normalized_layers: dict[str, dict[str, object]] = {}
    for layer in CONSTRUCT_COMPARABILITY_LAYERS:
        item = layers.get(layer)
        path = f"layers.{layer}"
        if not isinstance(item, Mapping):
            findings.append(
                _construct_finding(
                    "CONSTRUCT_LAYER_INVALID",
                    path,
                    "provide status and exact evidence ref for every layer",
                )
            )
            failing_layers.add(layer)
            continue
        status = str(item.get("status") or "")
        if status not in CONSTRUCT_LAYER_STATUSES[layer]:
            findings.append(
                _construct_finding(
                    "CONSTRUCT_LAYER_STATUS_INVALID",
                    f"{path}.status",
                    "use the canonical status vocabulary for this layer",
                )
            )
        if not _construct_exact_ref_valid(item.get("evidence_ref")):
            findings.append(
                _construct_finding(
                    "CONSTRUCT_LAYER_EVIDENCE_REF_INVALID",
                    f"{path}.evidence_ref",
                    "bind the layer status to an exact evidence ref",
                )
            )
        if status != CONSTRUCT_LAYER_PASS_STATUS[layer]:
            failing_layers.add(layer)
        normalized_layers[layer] = {
            "status": status,
            "evidence_ref": dict(item.get("evidence_ref"))
            if isinstance(item.get("evidence_ref"), Mapping)
            else None,
        }

    reasons_value = candidate.get("stop_reasons")
    reasons = list(reasons_value) if _construct_sequence(reasons_value) else []
    if not _construct_sequence(reasons_value):
        findings.append(
            _construct_finding(
                "CONSTRUCT_STOP_REASONS_INVALID",
                "stop_reasons",
                "provide a structured current and invalidated stop-reason history",
            )
        )
    reason_ids: list[str] = []
    active_reason_layers: list[str] = []
    invalidated_reason_ids: list[str] = []
    for index, reason in enumerate(reasons):
        path = f"stop_reasons[{index}]"
        if not isinstance(reason, Mapping):
            findings.append(
                _construct_finding(
                    "CONSTRUCT_STOP_REASON_INVALID",
                    path,
                    "provide a structured stop-reason record",
                )
            )
            continue
        reason_id = str(reason.get("reason_id") or "").strip()
        layer = str(reason.get("layer") or "")
        claim_code = str(reason.get("claim_code") or "")
        status = str(reason.get("status") or "")
        generation = reason.get("evidence_generation")
        if not reason_id:
            findings.append(
                _construct_finding(
                    "CONSTRUCT_STOP_REASON_ID_MISSING",
                    f"{path}.reason_id",
                    "bind every stop reason to a stable id",
                )
            )
        else:
            reason_ids.append(reason_id)
        if layer not in CONSTRUCT_COMPARABILITY_LAYERS:
            findings.append(
                _construct_finding(
                    "CONSTRUCT_STOP_REASON_LAYER_INVALID",
                    f"{path}.layer",
                    "bind the reason to one of the five evidence layers",
                )
            )
        elif claim_code != CONSTRUCT_LAYER_STOP_CODES[layer]:
            findings.append(
                _construct_finding(
                    "CONSTRUCT_STOP_REASON_CODE_INVALID",
                    f"{path}.claim_code",
                    "use the structured stop code for the selected layer",
                )
            )
        if not _construct_exact_ref_valid(reason.get("evidence_ref")):
            findings.append(
                _construct_finding(
                    "CONSTRUCT_STOP_REASON_EVIDENCE_REF_INVALID",
                    f"{path}.evidence_ref",
                    "bind the reason to exact evidence from its generation",
                )
            )
        if status == "active":
            if layer in CONSTRUCT_COMPARABILITY_LAYERS:
                active_reason_layers.append(layer)
                if layer not in failing_layers:
                    findings.append(
                        _construct_finding(
                            "CONSTRUCT_STOP_REASON_STALE_ACTIVE",
                            path,
                            "invalidate a prior absence claim after source recovery",
                        )
                    )
            if generation != evidence_generation:
                findings.append(
                    _construct_finding(
                        "CONSTRUCT_ACTIVE_REASON_GENERATION_STALE",
                        f"{path}.evidence_generation",
                        "bind active reasons to the current evidence generation",
                    )
                )
            if reason.get("invalidated_by_ref") is not None:
                findings.append(
                    _construct_finding(
                        "CONSTRUCT_ACTIVE_REASON_INVALIDATION_REF_FORBIDDEN",
                        f"{path}.invalidated_by_ref",
                        "active reasons cannot carry an invalidation ref",
                    )
                )
        elif status == "invalidated":
            if reason_id:
                invalidated_reason_ids.append(reason_id)
            if (
                isinstance(generation, bool)
                or not isinstance(generation, int)
                or generation < 1
                or generation >= evidence_generation
            ):
                findings.append(
                    _construct_finding(
                        "CONSTRUCT_INVALIDATED_REASON_GENERATION_INVALID",
                        f"{path}.evidence_generation",
                        "an invalidated reason must precede the current evidence generation",
                    )
                )
            if not _construct_exact_ref_valid(reason.get("invalidated_by_ref")):
                findings.append(
                    _construct_finding(
                        "CONSTRUCT_INVALIDATION_REF_INVALID",
                        f"{path}.invalidated_by_ref",
                        "bind invalidation to the exact recovered or refreshed evidence",
                    )
                )
        else:
            findings.append(
                _construct_finding(
                    "CONSTRUCT_STOP_REASON_STATUS_INVALID",
                    f"{path}.status",
                    "mark each reason active or invalidated",
                )
            )

    if len(reason_ids) != len(set(reason_ids)):
        findings.append(
            _construct_finding(
                "CONSTRUCT_STOP_REASON_ID_DUPLICATE",
                "stop_reasons",
                "use unique stable reason ids",
            )
        )
    active_counts = {layer: active_reason_layers.count(layer) for layer in CONSTRUCT_COMPARABILITY_LAYERS}
    for layer in sorted(failing_layers):
        if active_counts[layer] != 1:
            findings.append(
                _construct_finding(
                    "CONSTRUCT_ACTIVE_STOP_REASON_CARDINALITY_INVALID",
                    f"stop_reasons.{layer}",
                    "provide exactly one current active reason for every failing layer",
                )
            )

    derived_estimability = "not_estimable" if failing_layers else "owner_estimation_decision_required"
    if candidate.get("estimability_status") != derived_estimability:
        findings.append(
            _construct_finding(
                "CONSTRUCT_ESTIMABILITY_STATUS_MISMATCH",
                "estimability_status",
                "derive estimability from the current layered stop reasons",
            )
        )
    if candidate.get("estimation_authorized") is not False:
        findings.append(
            _construct_finding(
                "CONSTRUCT_ESTIMATION_AUTHORIZATION_FORBIDDEN",
                "estimation_authorized",
                "source recovery does not authorize estimation",
            )
        )
    if candidate.get("authority") is not False:
        findings.append(
            _construct_finding(
                "CONSTRUCT_AUTHORITY_FORBIDDEN",
                "authority",
                "keep construct comparability refs-only with authority=false",
            )
        )

    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "construct_comparability_currentness_audit_candidate.v1",
        "construct_id": construct_id,
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "layers": normalized_layers,
        "active_stop_layers": sorted(failing_layers),
        "invalidated_stop_reason_ids": sorted(invalidated_reason_ids),
        "estimability_status": derived_estimability,
        "estimation_authorized": False,
        "findings": findings,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-risk-model-transportability-reviewer",
            "reason": "construct_comparability_currentness_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def _construct_exact_ref_valid(value: object) -> bool:
    if not isinstance(value, Mapping) or set(value) != CONSTRUCT_EXACT_REF_FIELDS:
        return False
    size_bytes = value.get("size_bytes")
    return bool(
        str(value.get("kind") or "").strip()
        and str(value.get("ref") or "").strip()
        and not isinstance(size_bytes, bool)
        and isinstance(size_bytes, int)
        and size_bytes > 0
        and re.fullmatch(r"sha256:[0-9a-f]{64}", str(value.get("sha256") or ""))
    )


def _construct_sequence(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _construct_finding(code: str, field: str, action: str) -> dict[str, object]:
    return {
        "code": code,
        "field": field,
        "action": action,
        "writes_authority": False,
    }


def _self_check() -> None:
    assert normalize_predictor_name("LDL-C (mg/dL)") == "ldl_c_mg_dl"
    row = predictor_mapping_row("Age", "age_years")
    assert row["writes_authority"] is False
    skeleton = transportability_review_skeleton("model:abc", "cohort:def")
    assert skeleton["authority"]["refs_only"] is True
    assert lint_forbidden_authority_claims("model accepted with owner receipt")
    fixture_path = Path(__file__).with_name("fixtures") / "construct-comparability-currentness.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    results = {
        case["case_id"]: validate_construct_comparability_currentness(case["candidate"])
        for case in fixture["cases"]
    }
    recovered = results["recovered_codebook_and_linkage_field_role_open"]
    assert recovered["machine_check_status"] == "candidate_complete"
    assert recovered["active_stop_layers"] == ["field_role"]
    assert recovered["estimability_status"] == "not_estimable"
    assert recovered["estimation_authorized"] is False
    stale = results["recovered_layers_keep_absence_reasons_active"]
    assert stale["machine_check_status"] == "route_back_required"
    assert "CONSTRUCT_STOP_REASON_STALE_ACTIVE" in {
        item["code"] for item in stale["findings"]
    }
    print(json.dumps({"checks": 10, "ok": True}, sort_keys=True))


if __name__ == "__main__":
    _self_check()
