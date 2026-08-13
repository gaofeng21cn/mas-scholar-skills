"""Deterministic refs-only checks for one-note clinical abstraction.

The helper validates closed shape, exact spans, null consistency, assertion
enums, and completeness counts. It does not judge clinical meaning, terminology
correctness, phenotype validity, or owner acceptance.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping


PRESENCE_VALUES = frozenset({"present", "absent", "possible", "unknown"})
TEMPORALITY_VALUES = frozenset({"current", "historical", "planned", "unknown"})
EXPERIENCER_VALUES = frozenset({"patient", "family", "other", "unknown"})
NULL_REASONS = frozenset(
    {"not_documented", "explicitly_absent", "ambiguous", "not_applicable", "outside_schema"}
)
TERMINOLOGY_STATUSES = frozenset({"not_applicable", "unvalidated", "validated", "rejected"})

PAYLOAD_KEYS = frozenset({"note_ref", "abstraction_schema_ref", "records", "completeness"})
RECORD_KEYS = frozenset(
    {
        "field_id",
        "candidate_value",
        "null_reason",
        "verbatim_span",
        "span_start",
        "span_end",
        "presence",
        "temporality",
        "experiencer",
        "terminology_candidates",
        "terminology_validation_status",
        "support_ref",
        "owner_decision_ref",
    }
)
COMPLETENESS_KEYS = frozenset(
    {
        "requested_field_count",
        "completed_field_count",
        "null_field_count",
        "evidenced_field_count",
        "invalid_field_count",
    }
)


def abstraction_record_skeleton(field_id: str) -> dict[str, object]:
    """Return one explicit-null candidate record."""
    return {
        "field_id": field_id,
        "candidate_value": None,
        "null_reason": "not_documented",
        "verbatim_span": None,
        "span_start": None,
        "span_end": None,
        "presence": "unknown",
        "temporality": "unknown",
        "experiencer": "unknown",
        "terminology_candidates": [],
        "terminology_validation_status": "not_applicable",
        "support_ref": "",
        "owner_decision_ref": "",
    }


def note_abstraction_skeleton(
    note_ref: str,
    abstraction_schema_ref: str,
    field_ids: Iterable[str],
) -> dict[str, object]:
    """Return a closed one-note payload with one record per requested field."""
    records = [abstraction_record_skeleton(field_id) for field_id in field_ids]
    return {
        "note_ref": note_ref,
        "abstraction_schema_ref": abstraction_schema_ref,
        "records": records,
        "completeness": {
            "requested_field_count": len(records),
            "completed_field_count": len(records),
            "null_field_count": len(records),
            "evidenced_field_count": 0,
            "invalid_field_count": 0,
        },
    }


def validate_note_abstraction(note_text: str, payload: Mapping[str, object]) -> dict[str, object]:
    """Validate deterministic boundaries and return errors plus observed counts."""
    errors: list[str] = []
    if set(payload) != PAYLOAD_KEYS:
        errors.append("payload_shape")

    records_value = payload.get("records")
    records = records_value if isinstance(records_value, list) else []
    if not isinstance(records_value, list):
        errors.append("records_not_list")

    valid_records = 0
    null_fields = 0
    evidenced_fields = 0
    field_ids: set[str] = set()

    for index, raw_record in enumerate(records):
        prefix = f"records[{index}]"
        if not isinstance(raw_record, Mapping):
            errors.append(f"{prefix}:not_object")
            continue
        record_errors: list[str] = []
        if set(raw_record) != RECORD_KEYS:
            record_errors.append("shape")

        field_id = raw_record.get("field_id")
        if not isinstance(field_id, str) or not field_id:
            record_errors.append("field_id")
        elif field_id in field_ids:
            record_errors.append("duplicate_field_id")
        else:
            field_ids.add(field_id)

        presence = raw_record.get("presence")
        temporality = raw_record.get("temporality")
        experiencer = raw_record.get("experiencer")
        terminology_status = raw_record.get("terminology_validation_status")
        if presence not in PRESENCE_VALUES:
            record_errors.append("presence")
        if temporality not in TEMPORALITY_VALUES:
            record_errors.append("temporality")
        if experiencer not in EXPERIENCER_VALUES:
            record_errors.append("experiencer")
        if terminology_status not in TERMINOLOGY_STATUSES:
            record_errors.append("terminology_validation_status")
        if not isinstance(raw_record.get("terminology_candidates"), list):
            record_errors.append("terminology_candidates")

        value = raw_record.get("candidate_value")
        null_reason = raw_record.get("null_reason")
        if value is None:
            null_fields += 1
            if null_reason not in NULL_REASONS:
                record_errors.append("null_reason")
        elif null_reason is not None:
            record_errors.append("non_null_with_null_reason")

        span = raw_record.get("verbatim_span")
        start = raw_record.get("span_start")
        end = raw_record.get("span_end")
        has_assertion = presence in {"present", "absent", "possible"}
        requires_span = value is not None or has_assertion
        if span is None and start is None and end is None:
            if requires_span:
                record_errors.append("missing_required_span")
        elif not isinstance(span, str) or not isinstance(start, int) or not isinstance(end, int):
            record_errors.append("span_shape")
        elif start < 0 or end < start or end > len(note_text) or note_text[start:end] != span:
            record_errors.append("span_mismatch")
        else:
            evidenced_fields += 1

        if record_errors:
            errors.extend(f"{prefix}:{error}" for error in record_errors)
        else:
            valid_records += 1

    observed = {
        "requested_field_count": len(records),
        "completed_field_count": valid_records,
        "null_field_count": null_fields,
        "evidenced_field_count": evidenced_fields,
        "invalid_field_count": len(records) - valid_records,
    }
    completeness = payload.get("completeness")
    if not isinstance(completeness, Mapping) or set(completeness) != COMPLETENESS_KEYS:
        errors.append("completeness_shape")
    elif dict(completeness) != observed:
        errors.append("completeness_mismatch")

    return {"ok": not errors, "errors": errors, "observed_completeness": observed}


def clinical_note_handoff_skeleton() -> dict[str, object]:
    """Return the standard refs-only owner handoff shell."""
    return {
        "abstraction_schema_ref": "",
        "note_level_candidate_refs": [],
        "span_provenance_ref": "",
        "assertion_context_ref": "",
        "terminology_validation_ref": "",
        "completeness_ref": "",
        "chart_review_validation_candidate_ref": "",
        "candidate_refs": [],
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def _self_check() -> None:
    payload = note_abstraction_skeleton("note-1", "schema-1", ["smoking", "age"])
    assert validate_note_abstraction("No tobacco use.", payload)["ok"] is True

    payload["records"][0].update(
        {
            "null_reason": "explicitly_absent",
            "verbatim_span": "No tobacco use",
            "span_start": 0,
            "span_end": 14,
            "presence": "absent",
            "temporality": "current",
            "experiencer": "patient",
        }
    )
    payload["completeness"]["evidenced_field_count"] = 1
    assert validate_note_abstraction("No tobacco use.", payload)["ok"] is True

    payload["records"][0]["verbatim_span"] = "tobacco"
    assert "records[0]:span_mismatch" in validate_note_abstraction("No tobacco use.", payload)["errors"]

    closed_shape = note_abstraction_skeleton("note-2", "schema-1", ["age"])
    closed_shape["unexpected"] = True
    assert "payload_shape" in validate_note_abstraction("Age 42.", closed_shape)["errors"]

    null_consistency = note_abstraction_skeleton("note-3", "schema-1", ["age"])
    null_consistency["records"][0]["candidate_value"] = 42
    assert "records[0]:non_null_with_null_reason" in validate_note_abstraction(
        "Age 42.", null_consistency
    )["errors"]

    assertion_enum = note_abstraction_skeleton("note-4", "schema-1", ["age"])
    assertion_enum["records"][0]["presence"] = "confirmed"
    assert "records[0]:presence" in validate_note_abstraction("Age 42.", assertion_enum)["errors"]

    count_consistency = note_abstraction_skeleton("note-5", "schema-1", ["age"])
    count_consistency["completeness"]["null_field_count"] = 0
    assert "completeness_mismatch" in validate_note_abstraction(
        "Age 42.", count_consistency
    )["errors"]
    assert "chart_review_validation_candidate_ref" in clinical_note_handoff_skeleton()
    print(json.dumps({"ok": True, "checks": 8}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
