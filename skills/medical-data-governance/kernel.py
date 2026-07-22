"""Deterministic refs-only helpers for medical data governance.

These helpers scaffold data dictionary, source readiness, sensitive-field,
missingness, and provenance refs. They do not mutate data or claim source
readiness.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence


DATA_LAYERS = (
    "restricted_raw",
    "deidentified_linkage",
    "master",
    "deidentified_longitudinal",
    "standardized_longitudinal",
    "external",
)

DIRECT_IDENTIFIER_TERMS = (
    "name",
    "email",
    "phone",
    "address",
    "mrn",
    "medical_record",
    "ssn",
    "passport",
    "date_of_birth",
    "dob",
)

CLINICAL_SENSITIVE_TERMS = (
    "diagnosis",
    "icd",
    "medication",
    "drug",
    "lab",
    "death",
    "pregnancy",
    "hiv",
    "mental_health",
)

RECONSTRUCTION_KINDS = (
    "exclusion_flow",
    "recoding",
    "identity_linkage",
    "derivation_provenance",
)
RECONSTRUCTION_OUTCOMES = (
    "reconstructed",
    "not_reconstructed",
)
RECONSTRUCTION_EXACT_REF_FIELDS = frozenset(
    {"kind", "ref", "size_bytes", "sha256"}
)


def data_dictionary_schema() -> dict[str, Any]:
    """Return a minimal data dictionary schema for candidate review."""

    return {
        "type": "object",
        "required": ["dataset_ref", "source_layer", "variables", "provenance_ref"],
        "properties": {
            "dataset_ref": {"type": "string"},
            "source_layer": {"type": "string", "enum": list(DATA_LAYERS)},
            "version_ref": {"type": "string"},
            "variables": {"type": "array", "items": {"type": "object"}},
            "provenance_ref": {"type": "string"},
            "privacy_tier_ref": {"type": "string"},
            "study_binding_ref": {"type": "string"},
            "route_back_candidate": {"type": "string"},
        },
    }


def normalize_field_name(value: object) -> str:
    """Normalize a source field name to a stable snake_case key."""

    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def classify_sensitive_field(name: object) -> str:
    """Classify a field name for refs-only privacy review."""

    normalized = normalize_field_name(name)
    if any(term in normalized for term in DIRECT_IDENTIFIER_TERMS):
        return "direct_identifier"
    if any(term in normalized for term in CLINICAL_SENSITIVE_TERMS):
        return "clinical_sensitive"
    if any(term in normalized for term in ("date", "zip", "postcode", "site", "location")):
        return "quasi_identifier"
    return "not_flagged_by_name"


def data_governance_handoff_skeleton(dataset_ref: str = "") -> dict[str, object]:
    """Return the standard refs-only governance handoff shell."""

    return {
        "data_governance_handoff_ref": "",
        "dataset_ref": dataset_ref,
        "source_layer": "",
        "version_ref": "",
        "data_dictionary_ref": "",
        "manifest_completeness_check_ref": "",
        "privacy_tier_check_ref": "",
        "study_impact_check_ref": "",
        "provenance_ref": "",
        "owner_gate_target": "",
        "route_back_candidate": "",
    }


def missingness_profile_skeleton(fields: Sequence[str]) -> list[dict[str, object]]:
    """Return one missingness/provenance row per field."""

    return [
        {
            "field": normalize_field_name(field),
            "label": field,
            "available_n": None,
            "missing_n": None,
            "missing_percent": None,
            "source_ref": "",
            "provenance_ref": "",
            "sensitivity_class": classify_sensitive_field(field),
        }
        for field in fields
    ]


def lint_source_readiness(record: Mapping[str, object]) -> list[dict[str, str]]:
    """Flag missing governance refs without deciding source readiness."""

    findings: list[dict[str, str]] = []
    for key in ("dataset_ref", "source_layer", "data_dictionary_ref", "provenance_ref"):
        if not str(record.get(key, "")).strip():
            findings.append({"code": "MISSING_GOVERNANCE_REF", "field": key})
    layer = str(record.get("source_layer") or "")
    if layer and layer not in DATA_LAYERS:
        findings.append({"code": "UNKNOWN_SOURCE_LAYER", "field": layer})
    for variable in record.get("variables") or []:
        if not isinstance(variable, Mapping):
            findings.append({"code": "VARIABLE_NOT_OBJECT", "field": "variables"})
            continue
        name = str(variable.get("name") or variable.get("field") or "")
        sensitivity = classify_sensitive_field(name)
        if sensitivity != "not_flagged_by_name" and not str(variable.get("privacy_tier_ref", "")).strip():
            findings.append({"code": "SENSITIVE_FIELD_WITHOUT_PRIVACY_REF", "field": name})
    return findings


def validate_governed_source_reconstruction(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Audit a bounded reconstruction before a gap becomes author input.

    The comparison is driven by structured values and tolerances. Reader-facing
    wording is deliberately outside this validator.
    """

    findings: list[dict[str, object]] = []
    if candidate.get("surface_kind") != "governed_source_reconstruction_candidate.v1":
        findings.append(
            _reconstruction_finding(
                "RECONSTRUCTION_SURFACE_KIND_INVALID",
                "surface_kind",
                "use the governed-source reconstruction candidate surface",
            )
        )
    gap_id = str(candidate.get("gap_id") or "").strip()
    if not gap_id:
        findings.append(
            _reconstruction_finding(
                "RECONSTRUCTION_GAP_ID_MISSING",
                "gap_id",
                "bind the reconstruction to one stable gap id",
            )
        )
    if candidate.get("reconstruction_kind") not in RECONSTRUCTION_KINDS:
        findings.append(
            _reconstruction_finding(
                "RECONSTRUCTION_KIND_INVALID",
                "reconstruction_kind",
                "classify the bounded reconstruction using a supported kind",
            )
        )
    if candidate.get("attempt_status") != "completed":
        findings.append(
            _reconstruction_finding(
                "RECONSTRUCTION_ATTEMPT_INCOMPLETE",
                "attempt_status",
                "complete the bounded governed-source attempt before disposition",
            )
        )
    for field in ("frozen_target_ref", "governed_source_manifest_ref"):
        if not _reconstruction_exact_ref_valid(candidate.get(field)):
            findings.append(
                _reconstruction_finding(
                    "RECONSTRUCTION_EXACT_REF_INVALID",
                    field,
                    "bind the frozen target and governed source manifest as exact refs",
                )
            )

    expected_member_ids_value = candidate.get("expected_member_ids")
    expected_member_ids: list[str] = []
    if not _reconstruction_sequence(expected_member_ids_value):
        findings.append(
            _reconstruction_finding(
                "RECONSTRUCTION_EXPECTED_MEMBERS_INVALID",
                "expected_member_ids",
                "provide the complete non-empty member-id inventory",
            )
        )
    else:
        expected_member_ids = [str(value).strip() for value in expected_member_ids_value]
        if (
            not expected_member_ids
            or any(not value for value in expected_member_ids)
            or len(expected_member_ids) != len(set(expected_member_ids))
        ):
            findings.append(
                _reconstruction_finding(
                    "RECONSTRUCTION_EXPECTED_MEMBERS_INVALID",
                    "expected_member_ids",
                    "use unique non-empty member ids",
                )
            )

    members_value = candidate.get("members")
    members = list(members_value) if _reconstruction_sequence(members_value) else []
    if not members:
        findings.append(
            _reconstruction_finding(
                "RECONSTRUCTION_MEMBERS_INVALID",
                "members",
                "record member-level row, value, source, and tolerance evidence",
            )
        )
    member_ids: list[str] = []
    normalized_members: list[dict[str, object]] = []
    all_members_match = True
    for index, member in enumerate(members):
        path = f"members[{index}]"
        if not isinstance(member, Mapping):
            findings.append(
                _reconstruction_finding(
                    "RECONSTRUCTION_MEMBER_INVALID",
                    path,
                    "provide a structured member evidence row",
                )
            )
            all_members_match = False
            continue
        member_id = str(member.get("member_id") or "").strip()
        row_locator = str(member.get("row_locator") or "").strip()
        if not member_id:
            findings.append(
                _reconstruction_finding(
                    "RECONSTRUCTION_MEMBER_ID_MISSING",
                    f"{path}.member_id",
                    "bind every evidence row to a stable member id",
                )
            )
        else:
            member_ids.append(member_id)
        if not row_locator:
            findings.append(
                _reconstruction_finding(
                    "RECONSTRUCTION_ROW_LOCATOR_MISSING",
                    f"{path}.row_locator",
                    "record the exact governed-source row locator",
                )
            )
        if not _reconstruction_exact_ref_valid(member.get("source_ref")):
            findings.append(
                _reconstruction_finding(
                    "RECONSTRUCTION_MEMBER_SOURCE_REF_INVALID",
                    f"{path}.source_ref",
                    "bind each compared value to an exact governed source member",
                )
            )

        comparison = member.get("comparison")
        comparison_valid = isinstance(comparison, Mapping)
        mode = str(comparison.get("mode") or "") if comparison_valid else ""
        tolerance = comparison.get("tolerance") if comparison_valid else None
        if mode not in {"exact", "numeric_tolerance"}:
            findings.append(
                _reconstruction_finding(
                    "RECONSTRUCTION_COMPARISON_MODE_INVALID",
                    f"{path}.comparison.mode",
                    "use exact or numeric_tolerance comparison",
                )
            )
            comparison_valid = False
        if (
            isinstance(tolerance, bool)
            or not isinstance(tolerance, (int, float))
            or tolerance < 0
            or (mode == "exact" and tolerance != 0)
        ):
            findings.append(
                _reconstruction_finding(
                    "RECONSTRUCTION_TOLERANCE_INVALID",
                    f"{path}.comparison.tolerance",
                    "record a non-negative numeric tolerance and use zero for exact comparison",
                )
            )
            comparison_valid = False

        source_value = member.get("source_value")
        reconstructed_value = member.get("reconstructed_value")
        value_delta: float | None = None
        matched = False
        if comparison_valid and mode == "numeric_tolerance":
            numeric_values = (source_value, reconstructed_value)
            if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in numeric_values):
                findings.append(
                    _reconstruction_finding(
                        "RECONSTRUCTION_NUMERIC_VALUE_INVALID",
                        path,
                        "numeric tolerance comparisons require two numeric values",
                    )
                )
            else:
                value_delta = abs(float(source_value) - float(reconstructed_value))
                matched = value_delta <= float(tolerance)
        elif comparison_valid:
            matched = source_value == reconstructed_value
            value_delta = 0.0 if matched else None
        all_members_match = all_members_match and matched
        normalized_members.append(
            {
                "member_id": member_id,
                "row_locator": row_locator,
                "source_ref": dict(member.get("source_ref"))
                if isinstance(member.get("source_ref"), Mapping)
                else None,
                "source_value": source_value,
                "reconstructed_value": reconstructed_value,
                "comparison_mode": mode,
                "tolerance": tolerance,
                "absolute_delta": value_delta,
                "matched": matched,
            }
        )

    if len(member_ids) != len(set(member_ids)):
        findings.append(
            _reconstruction_finding(
                "RECONSTRUCTION_MEMBER_ID_DUPLICATE",
                "members",
                "provide one evidence row per expected member id",
            )
        )
    if expected_member_ids and set(member_ids) != set(expected_member_ids):
        findings.append(
            _reconstruction_finding(
                "RECONSTRUCTION_MEMBER_COVERAGE_MISMATCH",
                "members",
                "close every expected member id and no others",
            )
        )

    computed_outcome = "reconstructed" if members and all_members_match else "not_reconstructed"
    if candidate.get("reconstruction_outcome") not in RECONSTRUCTION_OUTCOMES:
        findings.append(
            _reconstruction_finding(
                "RECONSTRUCTION_OUTCOME_INVALID",
                "reconstruction_outcome",
                "declare reconstructed or not_reconstructed",
            )
        )
    elif candidate.get("reconstruction_outcome") != computed_outcome:
        findings.append(
            _reconstruction_finding(
                "RECONSTRUCTION_OUTCOME_MISMATCH",
                "reconstruction_outcome",
                "derive the outcome from the member-level comparison evidence",
            )
        )
    if candidate.get("authority") is not False:
        findings.append(
            _reconstruction_finding(
                "RECONSTRUCTION_AUTHORITY_FORBIDDEN",
                "authority",
                "keep the reconstruction refs-only with authority=false",
            )
        )

    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "governed_source_reconstruction_audit_candidate.v1",
        "gap_id": gap_id,
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "reconstruction_outcome": computed_outcome if complete else None,
        "member_evidence": normalized_members,
        "findings": findings,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-data-governance",
            "reason": "governed_source_reconstruction_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def _reconstruction_exact_ref_valid(value: object) -> bool:
    if not isinstance(value, Mapping) or set(value) != RECONSTRUCTION_EXACT_REF_FIELDS:
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


def _reconstruction_sequence(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _reconstruction_finding(code: str, field: str, action: str) -> dict[str, object]:
    return {
        "code": code,
        "field": field,
        "action": action,
        "writes_authority": False,
    }


def _self_check() -> None:
    assert "variables" in data_dictionary_schema()["required"]
    assert normalize_field_name("Date of Birth") == "date_of_birth"
    assert classify_sensitive_field("patient_email") == "direct_identifier"
    assert missingness_profile_skeleton(["HbA1c lab"])[0]["sensitivity_class"] == "clinical_sensitive"
    lint = lint_source_readiness({"source_layer": "csv", "variables": [{"name": "MRN"}]})
    assert {item["code"] for item in lint} >= {
        "MISSING_GOVERNANCE_REF",
        "UNKNOWN_SOURCE_LAYER",
        "SENSITIVE_FIELD_WITHOUT_PRIVACY_REF",
    }
    fixture_path = Path(__file__).with_name("fixtures") / "governed-source-reconstruction.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    case_results = {
        case["case_id"]: validate_governed_source_reconstruction(case["candidate"])
        for case in fixture["reconstruction_cases"]
    }
    assert case_results["recoverable_identity_provenance"]["machine_check_status"] == "candidate_complete"
    assert case_results["recoverable_identity_provenance"]["reconstruction_outcome"] == "reconstructed"
    assert case_results["declared_recovery_outside_tolerance"]["machine_check_status"] == "route_back_required"
    assert "RECONSTRUCTION_OUTCOME_MISMATCH" in {
        item["code"] for item in case_results["declared_recovery_outside_tolerance"]["findings"]
    }
    print(json.dumps({"ok": True, "checks": 9}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
