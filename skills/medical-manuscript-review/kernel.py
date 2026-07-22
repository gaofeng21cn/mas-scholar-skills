"""Deterministic refs-only helpers for medical manuscript review.

These helpers scaffold review facts, matrices, and labels. They do not issue
MAS reviewer receipts, owner receipts, typed blockers, verdicts, or readiness.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


REVIEW_ACTIONS = (
    "accept_as_is",
    "claim_downgrade",
    "citation_repair",
    "manuscript_repair",
    "display_repair",
    "analysis_campaign_route_back",
    "decision_route_back",
    "human_gate",
    "stop",
)

ISSUE_RULES = (
    ("citation_repair", ("citation", "reference", "pmid", "source", "uncited")),
    ("display_repair", ("figure", "caption", "panel", "table", "display")),
    ("analysis_campaign_route_back", ("analysis", "sensitivity", "model", "calibration")),
    ("claim_downgrade", ("causal", "prove", "burden", "prevalence", "overclaim")),
    ("human_gate", ("ethics", "consent", "coi", "funding", "data availability")),
)

ANOMALY_PARITY_SURFACES = (
    "manuscript",
    "supplement",
    "reviewer_response",
)
REVIEW_EXACT_REF_FIELDS = frozenset({"kind", "ref", "size_bytes", "sha256"})


def review_fact_base_schema() -> dict[str, Any]:
    """Return the shared fact-base schema for AI reviewer judgment."""

    return {
        "type": "object",
        "required": [
            "manuscript_type",
            "central_claim",
            "evidence_shown_refs",
            "evidence_missing_refs",
            "surfaces_under_review",
        ],
        "properties": {
            "manuscript_type": {"type": "string"},
            "submission_posture": {"type": "string"},
            "central_claim": {"type": "string"},
            "bounded_contribution": {"type": "string"},
            "evidence_shown_refs": {"type": "array", "items": {"type": "string"}},
            "evidence_missing_refs": {"type": "array", "items": {"type": "string"}},
            "likely_readership": {"type": "string"},
            "technical_gap_refs": {"type": "array", "items": {"type": "string"}},
            "surfaces_under_review": {"type": "array", "items": {"type": "string"}},
        },
    }


def review_matrix_skeleton(
    concerns: list[str] | None = None, lanes: list[str] | None = None
) -> list[dict[str, str]]:
    """Return a reviewer action matrix skeleton."""

    lane_names = lanes or ["technical", "significance", "reader", "validity_bias"]
    if concerns:
        return [_matrix_row(concern, "auto", classify_issue(concern)["action"]) for concern in concerns]
    return [_matrix_row("", lane, "") for lane in lane_names]


def classify_issue(issue_text: str) -> dict[str, str]:
    """Classify a review issue into the narrowest refs-only action label."""

    text = issue_text.lower()
    for action, keywords in ISSUE_RULES:
        if any(re.search(rf"\b{re.escape(keyword)}\b", text) for keyword in keywords):
            return {"action": action, "reason": f"matched {action}"}
    return {"action": "manuscript_repair", "reason": "default manuscript repair"}


def claim_citation_figure_matrix_skeleton(
    claims: list[str | dict[str, Any]]
) -> list[dict[str, str]]:
    """Return claim-citation-figure review rows without judging readiness."""

    rows: list[dict[str, str]] = []
    for index, item in enumerate(claims, start=1):
        if isinstance(item, dict):
            claim_ref = str(item.get("claim_ref") or f"claim_{index}")
            claim = str(item.get("claim", ""))
            citation_ref = str(item.get("citation_ref", ""))
            figure_ref = str(item.get("figure_ref", ""))
        else:
            claim_ref = f"claim_{index}"
            claim = str(item)
            citation_ref = ""
            figure_ref = ""
        rows.append(
            {
                "claim_ref": claim_ref,
                "claim": claim,
                "citation_ref": citation_ref,
                "figure_or_table_ref": figure_ref,
                "support_status": "",
                "review_action": "",
                "route_back_candidate": "",
            }
        )
    return rows


def validate_anomaly_evidence_parity(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Require anomaly evidence parity across all reader and reviewer surfaces."""

    findings: list[dict[str, object]] = []
    if candidate.get("surface_kind") != "anomaly_evidence_parity_candidate.v1":
        findings.append(
            _review_finding(
                "ANOMALY_PARITY_SURFACE_KIND_INVALID",
                "surface_kind",
                "use the anomaly evidence-parity candidate surface",
            )
        )
    anomaly_id = str(candidate.get("anomaly_id") or "").strip()
    if not anomaly_id:
        findings.append(
            _review_finding(
                "ANOMALY_PARITY_ID_MISSING",
                "anomaly_id",
                "bind the comparison to one stable anomaly id",
            )
        )
    if not _review_exact_ref_valid(candidate.get("structured_evidence_ref")):
        findings.append(
            _review_finding(
                "ANOMALY_PARITY_EVIDENCE_EXACT_REF_INVALID",
                "structured_evidence_ref",
                "bind all three surfaces to one exact structured evidence ref",
            )
        )

    output_surfaces_value = candidate.get("output_surfaces")
    output_surfaces = output_surfaces_value if isinstance(output_surfaces_value, Mapping) else {}
    if set(output_surfaces) != set(ANOMALY_PARITY_SURFACES):
        findings.append(
            _review_finding(
                "ANOMALY_PARITY_SURFACE_SET_INVALID",
                "output_surfaces",
                "provide exactly manuscript, supplement, and reviewer response",
            )
        )
    normalized_payloads: dict[str, dict[str, object]] = {}
    for surface in ANOMALY_PARITY_SURFACES:
        surface_value = output_surfaces.get(surface)
        path = f"output_surfaces.{surface}"
        if not isinstance(surface_value, Mapping):
            findings.append(
                _review_finding(
                    "ANOMALY_PARITY_SURFACE_INVALID",
                    path,
                    "provide exact artifact and structured anomaly fields",
                )
            )
            continue
        if not _review_exact_ref_valid(surface_value.get("artifact_ref")):
            findings.append(
                _review_finding(
                    "ANOMALY_PARITY_ARTIFACT_EXACT_REF_INVALID",
                    f"{path}.artifact_ref",
                    "bind each surface to exact final artifact bytes",
                )
            )
        flagged_count = surface_value.get("flagged_count")
        extreme_value_count = surface_value.get("extreme_value_count")
        for field, value in (
            ("flagged_count", flagged_count),
            ("extreme_value_count", extreme_value_count),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                findings.append(
                    _review_finding(
                        "ANOMALY_PARITY_COUNT_INVALID",
                        f"{path}.{field}",
                        "use a non-negative integer count",
                    )
                )
        if (
            isinstance(flagged_count, int)
            and not isinstance(flagged_count, bool)
            and isinstance(extreme_value_count, int)
            and not isinstance(extreme_value_count, bool)
            and extreme_value_count > flagged_count
        ):
            findings.append(
                _review_finding(
                    "ANOMALY_PARITY_COUNT_CONTRADICTION",
                    path,
                    "extreme-value count cannot exceed flagged count",
                )
            )
        threshold_status = str(surface_value.get("threshold_status") or "").strip()
        source_mutation_status = str(surface_value.get("source_mutation_status") or "").strip()
        if not threshold_status:
            findings.append(
                _review_finding(
                    "ANOMALY_PARITY_THRESHOLD_STATUS_MISSING",
                    f"{path}.threshold_status",
                    "record the structured threshold status",
                )
            )
        if not source_mutation_status:
            findings.append(
                _review_finding(
                    "ANOMALY_PARITY_SOURCE_MUTATION_STATUS_MISSING",
                    f"{path}.source_mutation_status",
                    "record whether governed source values changed",
                )
            )
        normalized_deltas = _normalize_result_deltas(
            surface_value.get("result_deltas"), path, findings
        )
        normalized_payloads[surface] = {
            "flagged_count": flagged_count,
            "extreme_value_count": extreme_value_count,
            "threshold_status": threshold_status,
            "source_mutation_status": source_mutation_status,
            "result_deltas": normalized_deltas,
        }

    baseline = normalized_payloads.get("manuscript")
    if baseline is not None:
        for surface in ("supplement", "reviewer_response"):
            payload = normalized_payloads.get(surface)
            if payload is None:
                continue
            for field in (
                "flagged_count",
                "extreme_value_count",
                "threshold_status",
                "source_mutation_status",
                "result_deltas",
            ):
                if payload[field] != baseline[field]:
                    findings.append(
                        _review_finding(
                            "ANOMALY_EVIDENCE_PARITY_MISMATCH",
                            f"output_surfaces.{surface}.{field}",
                            "update manuscript, supplement, and reviewer response together",
                        )
                    )
    if candidate.get("authority") is not False:
        findings.append(
            _review_finding(
                "ANOMALY_PARITY_AUTHORITY_FORBIDDEN",
                "authority",
                "keep anomaly parity QA refs-only with authority=false",
            )
        )

    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "anomaly_evidence_parity_audit_candidate.v1",
        "anomaly_id": anomaly_id,
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "surface_payloads": normalized_payloads,
        "findings": findings,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-manuscript-review",
            "reason": "anomaly_evidence_parity_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def validate_receipt_version_member_delta(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Require exact receipt refs and a normalized member-level version delta."""

    findings: list[dict[str, object]] = []
    if candidate.get("surface_kind") != "receipt_version_member_delta_candidate.v1":
        findings.append(
            _review_finding(
                "RECEIPT_DELTA_SURFACE_KIND_INVALID",
                "surface_kind",
                "use the receipt version member-delta candidate surface",
            )
        )
    for field in ("previous_receipt_ref", "current_receipt_ref"):
        if not _review_exact_ref_valid(candidate.get(field)):
            findings.append(
                _review_finding(
                    "RECEIPT_DELTA_EXACT_REF_INVALID",
                    field,
                    "bind both receipt versions as exact refs",
                )
            )
    if (
        _review_exact_ref_valid(candidate.get("previous_receipt_ref"))
        and candidate.get("previous_receipt_ref") == candidate.get("current_receipt_ref")
    ):
        findings.append(
            _review_finding(
                "RECEIPT_DELTA_VERSION_REFS_IDENTICAL",
                "previous_receipt_ref|current_receipt_ref",
                "compare two distinct receipt versions",
            )
        )

    previous = _receipt_member_inventory(
        candidate.get("previous_members"), "previous_members", findings
    )
    current = _receipt_member_inventory(
        candidate.get("current_members"), "current_members", findings
    )
    previous_ids = set(previous)
    current_ids = set(current)
    normalized_delta: dict[str, list[dict[str, object]]] = {
        "added": [
            {"member_id": member_id, "current_ref": current[member_id]}
            for member_id in sorted(current_ids - previous_ids)
        ],
        "removed": [
            {"member_id": member_id, "previous_ref": previous[member_id]}
            for member_id in sorted(previous_ids - current_ids)
        ],
        "changed": [
            {
                "member_id": member_id,
                "previous_ref": previous[member_id],
                "current_ref": current[member_id],
            }
            for member_id in sorted(previous_ids & current_ids)
            if previous[member_id] != current[member_id]
        ],
        "unchanged": [
            {"member_id": member_id, "ref": current[member_id]}
            for member_id in sorted(previous_ids & current_ids)
            if previous[member_id] == current[member_id]
        ],
    }
    declared_delta = candidate.get("member_delta")
    if not isinstance(declared_delta, Mapping) or set(declared_delta) != set(normalized_delta):
        findings.append(
            _review_finding(
                "RECEIPT_DELTA_MEMBER_DELTA_INVALID",
                "member_delta",
                "provide added, removed, changed, and unchanged member arrays",
            )
        )
    elif declared_delta != normalized_delta:
        findings.append(
            _review_finding(
                "RECEIPT_DELTA_MEMBER_DELTA_MISMATCH",
                "member_delta",
                "derive the normalized member delta from both exact inventories",
            )
        )
    if candidate.get("authority") is not False:
        findings.append(
            _review_finding(
                "RECEIPT_DELTA_AUTHORITY_FORBIDDEN",
                "authority",
                "keep receipt supersedence QA refs-only with authority=false",
            )
        )

    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "receipt_version_member_delta_audit_candidate.v1",
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "normalized_member_delta": normalized_delta,
        "findings": findings,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-manuscript-review",
            "reason": "receipt_version_member_delta_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def _normalize_result_deltas(
    value: object,
    surface_path: str,
    findings: list[dict[str, object]],
) -> list[dict[str, object]]:
    values = (
        list(value)
        if isinstance(value, Sequence)
        and not isinstance(value, (str, bytes, bytearray))
        else []
    )
    if not values:
        findings.append(
            _review_finding(
                "ANOMALY_PARITY_RESULT_DELTAS_INVALID",
                f"{surface_path}.result_deltas",
                "provide non-empty member-level exact result deltas",
            )
        )
        return []
    normalized: list[dict[str, object]] = []
    result_ids: list[str] = []
    for index, item in enumerate(values):
        path = f"{surface_path}.result_deltas[{index}]"
        if not isinstance(item, Mapping) or set(item) != {"result_id", "delta", "unit"}:
            findings.append(
                _review_finding(
                    "ANOMALY_PARITY_RESULT_DELTA_INVALID",
                    path,
                    "provide exactly result_id, delta, and unit",
                )
            )
            continue
        result_id = str(item.get("result_id") or "").strip()
        delta = item.get("delta")
        unit = str(item.get("unit") or "").strip()
        if not result_id or not unit:
            findings.append(
                _review_finding(
                    "ANOMALY_PARITY_RESULT_DELTA_FIELD_MISSING",
                    path,
                    "bind every delta to a stable result id and unit",
                )
            )
        if (
            isinstance(delta, bool)
            or not isinstance(delta, (int, float))
            or not math.isfinite(float(delta))
        ):
            findings.append(
                _review_finding(
                    "ANOMALY_PARITY_RESULT_DELTA_VALUE_INVALID",
                    f"{path}.delta",
                    "use a finite numeric result delta",
                )
            )
        result_ids.append(result_id)
        normalized.append({"result_id": result_id, "delta": delta, "unit": unit})
    if len(result_ids) != len(set(result_ids)):
        findings.append(
            _review_finding(
                "ANOMALY_PARITY_RESULT_ID_DUPLICATE",
                f"{surface_path}.result_deltas",
                "provide one delta per result id",
            )
        )
    return sorted(normalized, key=lambda item: str(item["result_id"]))


def _receipt_member_inventory(
    value: object,
    field: str,
    findings: list[dict[str, object]],
) -> dict[str, dict[str, object]]:
    values = (
        list(value)
        if isinstance(value, Sequence)
        and not isinstance(value, (str, bytes, bytearray))
        else []
    )
    if not values:
        findings.append(
            _review_finding(
                "RECEIPT_DELTA_MEMBER_INVENTORY_INVALID",
                field,
                "provide a non-empty member-level exact-ref inventory",
            )
        )
        return {}
    inventory: dict[str, dict[str, object]] = {}
    for index, item in enumerate(values):
        path = f"{field}[{index}]"
        if not isinstance(item, Mapping) or set(item) != REVIEW_EXACT_REF_FIELDS | {"member_id"}:
            findings.append(
                _review_finding(
                    "RECEIPT_DELTA_MEMBER_INVALID",
                    path,
                    "provide member_id plus kind/ref/size_bytes/sha256",
                )
            )
            continue
        member_id = str(item.get("member_id") or "").strip()
        exact_ref = {key: item[key] for key in REVIEW_EXACT_REF_FIELDS}
        if not member_id:
            findings.append(
                _review_finding(
                    "RECEIPT_DELTA_MEMBER_ID_MISSING",
                    f"{path}.member_id",
                    "bind each member to a stable id",
                )
            )
            continue
        if member_id in inventory:
            findings.append(
                _review_finding(
                    "RECEIPT_DELTA_MEMBER_ID_DUPLICATE",
                    f"{path}.member_id",
                    "provide one exact ref per member id",
                )
            )
            continue
        if not _review_exact_ref_valid(exact_ref):
            findings.append(
                _review_finding(
                    "RECEIPT_DELTA_MEMBER_EXACT_REF_INVALID",
                    path,
                    "bind every member to exact bytes, not a digest-only summary",
                )
            )
            continue
        inventory[member_id] = exact_ref
    return inventory


def _review_exact_ref_valid(value: object) -> bool:
    if not isinstance(value, Mapping) or set(value) != REVIEW_EXACT_REF_FIELDS:
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


def _review_finding(code: str, field: str, action: str) -> dict[str, object]:
    return {
        "code": code,
        "field": field,
        "action": action,
        "writes_authority": False,
    }


def _matrix_row(concern: str, lane: str, action: str) -> dict[str, str]:
    return {
        "review_lane": lane,
        "concern": concern,
        "evidence_ref": "",
        "affected_text_or_display_ref": "",
        "action": action,
        "owner_surface": "",
        "route_back_candidate": "",
    }


def _self_check() -> None:
    assert "central_claim" in review_fact_base_schema()["required"]
    assert classify_issue("Figure caption drifts")["action"] == "display_repair"
    assert classify_issue("missing citation")["action"] == "citation_repair"
    assert review_matrix_skeleton(["causal overclaim"])[0]["action"] == "claim_downgrade"
    assert claim_citation_figure_matrix_skeleton(["A"])[0]["claim_ref"] == "claim_1"
    anomaly_fixture_path = Path(__file__).with_name("fixtures") / "anomaly-evidence-parity.json"
    anomaly_fixture = json.loads(anomaly_fixture_path.read_text(encoding="utf-8"))
    anomaly_candidate = anomaly_fixture["candidate"]
    assert validate_anomaly_evidence_parity(anomaly_candidate)["machine_check_status"] == "candidate_complete"
    for negative in anomaly_fixture["negative_cases"]:
        changed = json.loads(json.dumps(anomaly_candidate))
        surface = changed["output_surfaces"][negative["surface"]]
        if negative["field"] == "result_delta":
            result = next(
                item for item in surface["result_deltas"]
                if item["result_id"] == negative["result_id"]
            )
            result["delta"] = negative["replacement"]
        else:
            surface[negative["field"]] = negative["replacement"]
        audit = validate_anomaly_evidence_parity(changed)
        assert "ANOMALY_EVIDENCE_PARITY_MISMATCH" in {
            item["code"] for item in audit["findings"]
        }

    receipt_fixture_path = Path(__file__).with_name("fixtures") / "receipt-version-member-delta.json"
    receipt_fixture = json.loads(receipt_fixture_path.read_text(encoding="utf-8"))
    receipt_candidate = receipt_fixture["candidate"]
    receipt_audit = validate_receipt_version_member_delta(receipt_candidate)
    assert receipt_audit["machine_check_status"] == "candidate_complete"
    assert all(receipt_audit["normalized_member_delta"][key] for key in ("added", "removed", "changed", "unchanged"))
    digest_only = json.loads(json.dumps(receipt_candidate))
    digest_only["member_delta"] = receipt_fixture["digest_only_member_delta"]
    assert "RECEIPT_DELTA_MEMBER_DELTA_INVALID" in {
        item["code"] for item in validate_receipt_version_member_delta(digest_only)["findings"]
    }
    print(json.dumps({"ok": True, "checks": 13}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
