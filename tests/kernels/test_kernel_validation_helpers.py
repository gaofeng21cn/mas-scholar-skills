"""Direct unit tests for shared Pydantic v2/jsonschema helpers and shapely geometry."""

from __future__ import annotations

import math

import pytest

from runtime.kernel_validation import (
    DispositionModel,
    ExactRefModel,
    ValidationError,
    is_exact_ref,
    is_exact_ref_or_disposition,
    parse_exact_ref,
    parse_finite_number,
    parse_number_sequence,
    validate_against_schema,
)
from tests.kernels._loader import load_kernel


VALID_SHA = "sha256:" + "a" * 64


def test_exact_ref_model_enforces_strict_types_and_forbids_extra_keys() -> None:
    valid = {
        "kind": "final_png_export",
        "ref": "artifact://figure-1.png",
        "size_bytes": 128,
        "sha256": VALID_SHA,
    }
    parsed = ExactRefModel.model_validate(valid)
    assert parsed.size_bytes == 128
    assert is_exact_ref(valid)
    assert parse_exact_ref(valid) == parsed

    # Strict: bool must not coerce to int, extra keys are forbidden, size_bytes >= 1
    with pytest.raises(ValidationError):
        ExactRefModel.model_validate({**valid, "size_bytes": True})
    with pytest.raises(ValidationError):
        ExactRefModel.model_validate({**valid, "size_bytes": 0})
    with pytest.raises(ValidationError):
        ExactRefModel.model_validate({**valid, "extra": "nope"})
    assert not is_exact_ref({**valid, "sha256": "sha256:not-hex"})


def test_disposition_and_union_validator() -> None:
    disp = {"status": "not_applicable", "ref": None, "reason": "single center cohort"}
    assert DispositionModel.model_validate(disp).status == "not_applicable"
    assert is_exact_ref_or_disposition(disp, allowed_dispositions=("not_applicable",))
    assert not is_exact_ref_or_disposition(disp, allowed_dispositions=("missing",))
    exact = {
        "kind": "metric_ref",
        "ref": "artifact://m.json",
        "size_bytes": 10,
        "sha256": VALID_SHA.upper(),
    }
    assert is_exact_ref_or_disposition(
        exact, allowed_dispositions=(), normalize_case=True
    )
    assert not is_exact_ref_or_disposition(
        exact, allowed_dispositions=("not_applicable",), require_disposition=True
    )


def test_numeric_and_jsonschema_helpers() -> None:
    assert parse_finite_number(3) == 3.0
    assert parse_finite_number(True) is None
    assert parse_finite_number(math.nan) is None
    assert parse_number_sequence([1, 2.5], 2) == [1.0, 2.5]
    assert parse_number_sequence([1, True], 2) is None
    assert parse_number_sequence([1], 2) is None

    schema = {
        "type": "object",
        "required": ["name"],
        "properties": {"name": {"type": "string", "minLength": 1}},
        "additionalProperties": False,
    }
    assert validate_against_schema(schema, {"name": "ok"}) == []
    assert validate_against_schema(schema, {"name": "", "extra": 1})


def test_display_qc_shapely_geometry_primitives() -> None:
    qc = load_kernel("medical-display-qc")
    assert qc._bbox_inside((2, 2, 8, 8), (0, 0, 10, 10)) is True
    assert qc._bbox_inside((0, 0, 12, 8), (0, 0, 10, 10)) is False
    assert math.isclose(qc._bbox_overlap_area((0, 0, 4, 4), (2, 2, 6, 6)), 4.0)
    assert math.isclose(qc._bbox_overlap_area((0, 0, 2, 2), (4, 4, 6, 6)), 0.0)
    assert math.isclose(qc._bbox_gap((0, 0, 2, 2), (5, 6, 7, 8)), 5.0)
    assert qc._segments_intersect(((0, 0), (10, 10)), ((0, 10), (10, 0))) is True
    assert qc._segments_intersect(((0, 0), (10, 0)), ((0, 5), (10, 5))) is False
    assert qc._point_on_segment((5, 0), ((0, 0), (10, 0))) is True
    assert qc._point_on_segment((5, 2), ((0, 0), (10, 0))) is False
    assert qc._segment_intersects_bbox_interior(((0, 5), (10, 5)), (2, 2, 8, 8)) is True
    assert qc._segment_intersects_bbox_interior(((0, 0), (10, 0)), (2, 2, 8, 8)) is False
    assert qc._point_on_bbox_boundary((2.0, 5.0), (2, 2, 8, 8)) is True
    assert qc._point_on_bbox_boundary((5.0, 5.0), (2, 2, 8, 8)) is False
