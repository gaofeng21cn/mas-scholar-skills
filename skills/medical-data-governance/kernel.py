"""Deterministic refs-only helpers for medical data governance.

These helpers scaffold data dictionary, source readiness, sensitive-field,
missingness, and provenance refs. They do not mutate data or claim source
readiness.
"""

from __future__ import annotations

import json
import re
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
    print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
