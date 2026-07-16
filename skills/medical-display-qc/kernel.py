"""Refs-only helpers and a non-mutating medical display artifact inspector."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Mapping, Sequence


DISPLAY_QC_REFS = (
    "display_artifact_inventory_ref",
    "programmatic_figure_audit_ref",
    "layout_qc_receipt_ref",
    "export_integrity_ref",
    "panel_caption_consistency_ref",
    "claim_display_alignment_ref",
    "accessibility_and_size_ref",
    "display_qc_support_map_ref",
    "page_hash_evidence_candidate_ref",
)

SUPPORTED_RASTER_FORMATS = {"JPEG", "PNG", "TIFF"}
RASTER_SUFFIXES = {".jpeg", ".jpg", ".png", ".tif", ".tiff"}
RASTER_FORMAT_SUFFIXES = {
    "JPEG": {".jpeg", ".jpg"},
    "PNG": {".png"},
    "TIFF": {".tif", ".tiff"},
}
MIN_RASTER_DIMENSION_PX = 600
MIN_RASTER_DPI = 150.0
HIGH_CONTENT_DENSITY = 0.95
LAYOUT_QC_SURFACE_KIND = "layout_qc_receipt_candidate.v1"
PAGE_HASH_EVIDENCE_SURFACE_KIND = "scholarskills_page_hash_evidence_candidate"
PAGE_HASH_RASTER_CONTRACT = {
    "contract_id": "scholarskills_pdf_page_pixel_raster",
    "contract_version": 1,
    "scale_x": 2.0,
    "scale_y": 2.0,
    "nominal_dpi": 144,
    "colorspace": "sRGB",
    "pixel_format": "RGB8",
    "alpha": False,
    "annotations": True,
    "hash_algorithm": "sha256",
    "page_order": "document_order",
}
REQUIRED_LAYOUT_REGRESSION_CASES = {
    "long_category_label",
    "extreme_numeric_annotation",
    "full_width_layout",
}

QC_ROUTE_RULES = (
    ("artifact_owner_repair", ("blank", "missing", "broken", "export", "link")),
    ("display_redesign", ("overlap", "readability", "font", "contrast", "color")),
    ("source_data_mismatch", ("denominator", "estimate", "uncertainty", "group", "ordering")),
    ("caption_numbering_repair", ("caption", "legend", "panel", "letter", "numbering")),
    ("owner_visual_audit_decision", ("accept", "approve", "publication", "readiness")),
)


def normalize_evidence_ref(value: object) -> str:
    """Normalize a display evidence ref without resolving or reading it."""

    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .;,")


def display_artifact_row(
    artifact_ref: object,
    *,
    page_ref: object = "",
    panel_ref: object = "",
    caption_ref: object = "",
    claim_ref: object = "",
) -> dict[str, Any]:
    """Return a refs-only display artifact inventory row."""

    return {
        "artifact_ref": normalize_evidence_ref(artifact_ref),
        "page_ref": normalize_evidence_ref(page_ref),
        "panel_ref": normalize_evidence_ref(panel_ref),
        "caption_ref": normalize_evidence_ref(caption_ref),
        "claim_ref": normalize_evidence_ref(claim_ref),
        "qc_candidate_ref": "",
        "route_back_candidate": "",
        "writes_authority": False,
    }


def display_qc_skeleton(artifact_ref: object) -> dict[str, Any]:
    """Return the display QC candidate package skeleton."""

    return {
        "surface_kind": "display_qc_candidate",
        "artifact_ref": normalize_evidence_ref(artifact_ref),
        "required_refs": list(DISPLAY_QC_REFS),
        "candidate_refs": {ref: None for ref in DISPLAY_QC_REFS},
        "route_back_candidate": None,
        "owner_gate_handoff_ref": None,
        "authority": {
            "refs_only": True,
            "can_mutate_artifacts": False,
            "can_write_mas_truth": False,
            "can_sign_visual_audit_receipt": False,
            "can_sign_owner_receipt": False,
            "can_create_typed_blocker": False,
            "can_claim_publication_readiness": False,
        },
    }


def classify_display_qc_route(issue_text: object) -> dict[str, str]:
    """Classify a QC issue into a route-back hint, not an authority verdict."""

    text = str(issue_text or "").lower()
    for route, keywords in QC_ROUTE_RULES:
        if any(re.search(rf"\b{re.escape(keyword)}\b", text) for keyword in keywords):
            return {"route": route, "reason": f"matched {route}"}
    return {"route": "display_qc_review_hint", "reason": "default refs-only QC hint"}


def display_qc_support_map(
    rows: list[Mapping[str, object]],
) -> list[dict[str, str | bool]]:
    """Normalize artifact-to-evidence rows for display QC handoff."""

    out: list[dict[str, str | bool]] = []
    for row in rows:
        issue = normalize_evidence_ref(row.get("issue") or row.get("finding"))
        route = normalize_evidence_ref(
            row.get("route_back_candidate") or classify_display_qc_route(issue)["route"]
        )
        out.append(
            {
                "artifact_ref": normalize_evidence_ref(row.get("artifact_ref")),
                "evidence_ref": normalize_evidence_ref(row.get("evidence_ref")),
                "issue": issue,
                "route_back_candidate": route,
                "writes_authority": False,
            }
        )
    return out


def lint_forbidden_display_qc_claims(text: str) -> list[str]:
    """Return forbidden authority phrases found in display QC prose."""

    patterns = (
        r"\bfigure accepted\b",
        r"\bartifact accepted\b",
        r"\bvisual audit receipt\b",
        r"\bowner receipt\b",
        r"\btyped blocker\b",
        r"\bpublication-ready\b",
        r"\bpublication readiness\b",
    )
    return [pattern for pattern in patterns if re.search(pattern, text, flags=re.I)]


def _finding(
    code: str,
    severity: str,
    message: str,
    route_back_candidate: str,
    **details: object,
) -> dict[str, Any]:
    finding = {
        "code": code,
        "severity": severity,
        "message": message,
        "route_back_candidate": route_back_candidate,
        "writes_authority": False,
    }
    finding.update({key: value for key, value in details.items() if value is not None})
    return finding


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_sha256(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256_digest(value: object, label: str) -> str:
    text = str(value or "").strip().lower()
    digest = text.removeprefix("sha256:")
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValueError(f"{label} must be a SHA-256 digest")
    return f"sha256:{digest}"


def _origin_ref(value: object) -> object | None:
    if not isinstance(value, Mapping) or not value:
        return None
    normalized_ref = normalize_evidence_ref(value.get("ref"))
    if not normalized_ref:
        return None
    try:
        normalized_sha256 = _sha256_digest(value.get("sha256"), "origin ref sha256")
    except ValueError:
        return None
    size_bytes = value.get("size_bytes")
    if size_bytes is not None and (
        isinstance(size_bytes, bool)
        or not isinstance(size_bytes, int)
        or size_bytes < 0
    ):
        return None
    try:
        normalized = json.loads(
            json.dumps(dict(value), ensure_ascii=True, sort_keys=True)
        )
    except (TypeError, ValueError):
        return None
    normalized["ref"] = normalized_ref
    normalized["sha256"] = normalized_sha256
    return normalized


def build_page_hash_evidence_candidate(
    pages: Sequence[Mapping[str, object]],
    *,
    review_scope_sha256: object,
    rubric_sha256: object,
    origin_reviewer_invocation_ref: object = None,
    origin_reviewer_evidence_ref: object = None,
) -> dict[str, Any]:
    """Build a no-authority cache candidate from ordered fixed-raster page pixels."""

    normalized_pages: list[dict[str, Any]] = []
    for index, value in enumerate(pages, start=1):
        page_number = value.get("page_number")
        width = value.get("width")
        height = value.get("height")
        pixel_format = str(value.get("pixel_format") or "").strip()
        if page_number != index or isinstance(page_number, bool):
            raise ValueError("pages must use contiguous document-order page_number values")
        if (
            isinstance(width, bool)
            or not isinstance(width, int)
            or width <= 0
            or isinstance(height, bool)
            or not isinstance(height, int)
            or height <= 0
        ):
            raise ValueError("page width and height must be positive integers")
        if pixel_format != PAGE_HASH_RASTER_CONTRACT["pixel_format"]:
            raise ValueError("page pixel_format must match the fixed raster contract")
        normalized_pages.append(
            {
                "page_number": page_number,
                "width": width,
                "height": height,
                "pixel_format": pixel_format,
                "pixel_sha256": _sha256_digest(
                    value.get("pixel_sha256"), f"pages[{index - 1}].pixel_sha256"
                ),
            }
        )
    if not normalized_pages:
        raise ValueError("pages must contain at least one rasterized page")

    scope_digest = _sha256_digest(review_scope_sha256, "review_scope_sha256")
    rubric_digest = _sha256_digest(rubric_sha256, "rubric_sha256")
    key_payload = {
        "ordered_pages": normalized_pages,
        "raster_contract": dict(PAGE_HASH_RASTER_CONTRACT),
        "review_scope_sha256": scope_digest,
        "rubric_sha256": rubric_digest,
    }
    invocation_ref = _origin_ref(origin_reviewer_invocation_ref)
    evidence_ref = _origin_ref(origin_reviewer_evidence_ref)
    origin_bound = invocation_ref is not None and evidence_ref is not None
    return {
        "surface_kind": PAGE_HASH_EVIDENCE_SURFACE_KIND,
        "schema_version": 1,
        "review_lane": "display",
        "review_scope_sha256": scope_digest,
        "rubric_sha256": rubric_digest,
        "raster_contract": dict(PAGE_HASH_RASTER_CONTRACT),
        "pages": normalized_pages,
        "cache_key_sha256": f"sha256:{_canonical_json_sha256(key_payload)}",
        "origin_reviewer_invocation_ref": invocation_ref,
        "origin_reviewer_evidence_ref": evidence_ref,
        "cache_reuse_eligible": origin_bound,
        "cache_authority": False,
        "requires_fresh_reviewer_invocation": True,
        "requires_fresh_reviewer_receipt": True,
        "requires_mas_judgment": True,
        "authority_boundary": {
            "can_emit_verdict": False,
            "can_sign_reviewer_receipt": False,
            "can_sign_owner_receipt": False,
            "can_create_typed_blocker": False,
            "can_claim_quality_readiness": False,
            "can_claim_publication_readiness": False,
            "can_claim_current_package_authority": False,
        },
    }


def _layout_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError(f"{label} must be a finite number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be a finite number")
    return number


def _layout_bbox(value: object, label: str) -> tuple[float, float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise ValueError(f"{label} must contain four coordinates")
    x0, y0, x1, y1 = (
        _layout_number(item, f"{label}[{index}]") for index, item in enumerate(value)
    )
    if x1 <= x0 or y1 <= y0:
        raise ValueError(f"{label} must have positive width and height")
    return (x0, y0, x1, y1)


def _bbox_inside(
    inner: tuple[float, float, float, float],
    outer: tuple[float, float, float, float],
) -> bool:
    return (
        inner[0] >= outer[0]
        and inner[1] >= outer[1]
        and inner[2] <= outer[2]
        and inner[3] <= outer[3]
    )


def _bbox_overlap_area(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
) -> float:
    width = max(0.0, min(first[2], second[2]) - max(first[0], second[0]))
    height = max(0.0, min(first[3], second[3]) - max(first[1], second[1]))
    return width * height


def _bbox_gap(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
) -> float:
    dx = max(first[0] - second[2], second[0] - first[2], 0.0)
    dy = max(first[1] - second[3], second[1] - first[3], 0.0)
    return math.hypot(dx, dy)


def _layout_violation(code: str, **details: object) -> dict[str, object]:
    return {"code": code, "writes_authority": False, **details}


def _layout_authority_boundary() -> dict[str, bool]:
    return {
        "refs_only": True,
        "can_mutate_artifacts": False,
        "can_write_mas_truth": False,
        "can_sign_visual_audit_receipt": False,
        "can_sign_owner_receipt": False,
        "can_create_typed_blocker": False,
        "can_claim_mas_visual_authority": False,
        "can_claim_submission_authority": False,
        "can_claim_artifact_authority": False,
        "can_claim_quality_verdict": False,
        "can_claim_publication_readiness": False,
    }


def audit_layout_registry(registry: Mapping[str, object]) -> dict[str, Any]:
    """Audit a renderer-produced text bbox registry on its fixed final canvas."""

    final_canvas = registry.get("final_canvas")
    if not isinstance(final_canvas, Mapping):
        raise ValueError("final_canvas must be an object")
    width_px = _layout_number(final_canvas.get("width_px"), "final_canvas.width_px")
    height_px = _layout_number(final_canvas.get("height_px"), "final_canvas.height_px")
    if width_px <= 0 or height_px <= 0:
        raise ValueError("final_canvas pixel dimensions must be positive")
    canvas_bbox = (0.0, 0.0, width_px, height_px)

    safe_inset = registry.get("safe_inset_px")
    if not isinstance(safe_inset, Mapping):
        raise ValueError("safe_inset_px must be an object")
    inset = {
        edge: _layout_number(safe_inset.get(edge), f"safe_inset_px.{edge}")
        for edge in ("left", "right", "top", "bottom")
    }
    if any(value < 0 for value in inset.values()):
        raise ValueError("safe_inset_px values must be non-negative")
    safe_bbox = (
        inset["left"],
        inset["top"],
        width_px - inset["right"],
        height_px - inset["bottom"],
    )
    if safe_bbox[2] <= safe_bbox[0] or safe_bbox[3] <= safe_bbox[1]:
        raise ValueError("safe_inset_px leaves no usable canvas")

    minimum_spacing = _layout_number(
        registry.get("minimum_spacing_px"), "minimum_spacing_px"
    )
    if minimum_spacing <= 0:
        raise ValueError("minimum_spacing_px must be positive")

    lanes_value = registry.get("lanes")
    if not isinstance(lanes_value, Mapping):
        raise ValueError("lanes must be an object")
    if not {"plotting_data", "annotation"}.issubset(lanes_value):
        raise ValueError("lanes must define plotting_data and annotation")
    lane_boxes: dict[str, tuple[float, float, float, float]] = {}
    violations: list[dict[str, object]] = []
    for lane_name in sorted(lanes_value):
        lane = lanes_value[lane_name]
        if not isinstance(lane, Mapping):
            raise ValueError(f"lane {lane_name} must be an object")
        lane_bbox = _layout_bbox(lane.get("bbox_px"), f"lanes.{lane_name}.bbox_px")
        lane_boxes[str(lane_name)] = lane_bbox
        if not _bbox_inside(lane_bbox, canvas_bbox):
            violations.append(_layout_violation("lane_canvas_overflow", lane=lane_name))
    if _bbox_overlap_area(lane_boxes["plotting_data"], lane_boxes["annotation"]) > 0:
        violations.append(_layout_violation("data_annotation_lane_overlap"))

    export_policy = registry.get("export_policy")
    if not isinstance(export_policy, Mapping):
        raise ValueError("export_policy must be an object")
    if export_policy.get("canvas_mode") != "fixed":
        violations.append(_layout_violation("canvas_mode_not_fixed"))
    if export_policy.get("bbox_inches") is not None:
        violations.append(_layout_violation("bbox_inches_not_none"))
    if export_policy.get("tight_crop") is not False:
        violations.append(_layout_violation("tight_crop_enabled_or_undeclared"))
    if registry.get("wrap_policy") != "automatic_semantic_wrap":
        violations.append(_layout_violation("automatic_wrap_policy_missing"))
    if registry.get("measurement_basis") != "renderer_drawn_text_width":
        violations.append(_layout_violation("renderer_width_measurement_missing"))

    panels = registry.get("panels")
    if not isinstance(panels, list) or not panels:
        raise ValueError("panels must be a non-empty array")
    if not all(isinstance(panel, Mapping) for panel in panels):
        raise ValueError("each panel must be an object")
    registered_artist_count = 0
    artist_id_counts: Counter[str] = Counter()
    for panel in sorted(panels, key=lambda item: str(item.get("panel_id", ""))):
        panel_id = str(panel.get("panel_id") or "").strip()
        if not panel_id:
            raise ValueError("each panel must define panel_id")
        expected_ids = panel.get("expected_text_artist_ids")
        artists = panel.get("text_artists")
        if not isinstance(expected_ids, list) or not all(
            isinstance(item, str) and item for item in expected_ids
        ):
            raise ValueError(f"panel {panel_id} expected_text_artist_ids must be strings")
        if not isinstance(artists, list):
            raise ValueError(f"panel {panel_id} text_artists must be an array")
        if not all(isinstance(artist, Mapping) for artist in artists):
            raise ValueError(f"panel {panel_id} text artist must be an object")

        artist_records: list[dict[str, object]] = []
        actual_ids: list[str] = []
        for artist in sorted(artists, key=lambda item: str(item.get("artist_id", ""))):
            artist_id = str(artist.get("artist_id") or "").strip()
            if not artist_id:
                raise ValueError(f"panel {panel_id} text artist must define artist_id")
            artist_id_counts[artist_id] += 1
            actual_ids.append(artist_id)
            registered_artist_count += 1

            bbox = _layout_bbox(
                artist.get("bbox_px"), f"panels.{panel_id}.{artist_id}.bbox_px"
            )
            clip_bbox = _layout_bbox(
                artist.get("clip_bbox_px"),
                f"panels.{panel_id}.{artist_id}.clip_bbox_px",
            )
            lane_name = str(artist.get("lane") or "")
            lane_bbox = lane_boxes.get(lane_name)
            if (
                artist.get("artist_kind") == "numeric_annotation"
                and lane_name != "annotation"
            ):
                violations.append(
                    _layout_violation(
                        "numeric_annotation_outside_annotation_lane",
                        panel_id=panel_id,
                        artist_id=artist_id,
                    )
                )
            if lane_bbox is None:
                violations.append(
                    _layout_violation(
                        "artist_lane_missing", panel_id=panel_id, artist_id=artist_id
                    )
                )
            elif not _bbox_inside(bbox, lane_bbox):
                violations.append(
                    _layout_violation(
                        "artist_outside_declared_lane",
                        panel_id=panel_id,
                        artist_id=artist_id,
                        lane=lane_name,
                    )
                )
            if not _bbox_inside(bbox, canvas_bbox):
                violations.append(
                    _layout_violation(
                        "artist_canvas_overflow", panel_id=panel_id, artist_id=artist_id
                    )
                )
            if not _bbox_inside(bbox, safe_bbox):
                violations.append(
                    _layout_violation(
                        "artist_safe_inset_violation",
                        panel_id=panel_id,
                        artist_id=artist_id,
                    )
                )
            if not _bbox_inside(bbox, clip_bbox):
                violations.append(
                    _layout_violation(
                        "artist_clipped", panel_id=panel_id, artist_id=artist_id
                    )
                )

            if artist.get("artist_kind") == "category_label":
                measurement = artist.get("text_measurement")
                if not isinstance(measurement, Mapping):
                    violations.append(
                        _layout_violation(
                            "category_label_measurement_missing",
                            panel_id=panel_id,
                            artist_id=artist_id,
                        )
                    )
                else:
                    measured_width = _layout_number(
                        measurement.get("measured_unwrapped_width_px"),
                        f"{artist_id}.measured_unwrapped_width_px",
                    )
                    available_width = _layout_number(
                        measurement.get("available_width_px"),
                        f"{artist_id}.available_width_px",
                    )
                    line_count = measurement.get("line_count")
                    source_text = str(artist.get("source_text") or "")
                    if measurement.get("method") != "renderer_drawn_text_width":
                        violations.append(
                            _layout_violation(
                                "category_label_measurement_method_invalid",
                                panel_id=panel_id,
                                artist_id=artist_id,
                            )
                        )
                    if measurement.get("manual_breaks") is not False or "\n" in source_text:
                        violations.append(
                            _layout_violation(
                                "manual_category_label_break",
                                panel_id=panel_id,
                                artist_id=artist_id,
                            )
                        )
                    if (
                        measured_width > available_width
                        and (
                            isinstance(line_count, bool)
                            or not isinstance(line_count, int)
                            or line_count < 2
                        )
                    ):
                        violations.append(
                            _layout_violation(
                                "long_category_label_not_wrapped",
                                panel_id=panel_id,
                                artist_id=artist_id,
                            )
                        )

            artist_records.append({"artist_id": artist_id, "bbox": bbox})

        missing_ids = sorted(set(expected_ids) - set(actual_ids))
        unexpected_ids = sorted(set(actual_ids) - set(expected_ids))
        if missing_ids:
            violations.append(
                _layout_violation(
                    "text_artist_registry_incomplete",
                    panel_id=panel_id,
                    missing_artist_ids=missing_ids,
                )
            )
        if unexpected_ids:
            violations.append(
                _layout_violation(
                    "text_artist_registry_expectation_stale",
                    panel_id=panel_id,
                    unexpected_artist_ids=unexpected_ids,
                )
            )

        for first, second in combinations(artist_records, 2):
            first_bbox = first["bbox"]
            second_bbox = second["bbox"]
            overlap_area = _bbox_overlap_area(first_bbox, second_bbox)
            pair = [str(first["artist_id"]), str(second["artist_id"])]
            if overlap_area > 0:
                violations.append(
                    _layout_violation(
                        "text_artist_overlap",
                        panel_id=panel_id,
                        artist_ids=pair,
                        overlap_area_px2=round(overlap_area, 6),
                    )
                )
            else:
                gap = _bbox_gap(first_bbox, second_bbox)
                if gap < minimum_spacing:
                    violations.append(
                        _layout_violation(
                            "text_artist_minimum_spacing_violation",
                            panel_id=panel_id,
                            artist_ids=pair,
                            measured_gap_px=round(gap, 6),
                            minimum_spacing_px=minimum_spacing,
                        )
                    )

    for artist_id, count in sorted(artist_id_counts.items()):
        if count > 1:
            violations.append(
                _layout_violation(
                    "duplicate_text_artist_id", artist_id=artist_id, count=count
                )
            )

    regression_cases = set(registry.get("regression_cases") or [])
    if registry.get("fixture_only") is True:
        for missing_case in sorted(REQUIRED_LAYOUT_REGRESSION_CASES - regression_cases):
            violations.append(
                _layout_violation(
                    "regression_fixture_case_missing", regression_case=missing_case
                )
            )

    violations.sort(
        key=lambda item: json.dumps(item, ensure_ascii=True, sort_keys=True)
    )
    counts = Counter(str(item["code"]) for item in violations)
    checks = {
        "registry_complete": not any(
            counts[code]
            for code in (
                "text_artist_registry_incomplete",
                "text_artist_registry_expectation_stale",
                "duplicate_text_artist_id",
            )
        ),
        "measured_wrap_valid": not any(
            counts[code]
            for code in (
                "automatic_wrap_policy_missing",
                "renderer_width_measurement_missing",
                "category_label_measurement_missing",
                "category_label_measurement_method_invalid",
                "manual_category_label_break",
                "long_category_label_not_wrapped",
            )
        ),
        "annotation_lane_separate": not any(
            counts[code]
            for code in (
                "data_annotation_lane_overlap",
                "numeric_annotation_outside_annotation_lane",
            )
        ),
        "no_text_overlap": counts["text_artist_overlap"] == 0,
        "minimum_spacing_met": counts["text_artist_minimum_spacing_violation"] == 0,
        "no_canvas_overflow": counts["artist_canvas_overflow"] == 0,
        "no_clipping": counts["artist_clipped"] == 0,
        "safe_inset_met": counts["artist_safe_inset_violation"] == 0,
        "fixed_canvas_export": not any(
            counts[code]
            for code in (
                "canvas_mode_not_fixed",
                "bbox_inches_not_none",
                "tight_crop_enabled_or_undeclared",
            )
        ),
        "regression_fixture_coverage": counts["regression_fixture_case_missing"] == 0,
    }
    return {
        "surface_kind": "layout_bbox_registry_audit_candidate.v1",
        "registry_sha256": _canonical_json_sha256(registry),
        "machine_check_status": (
            "geometry_checks_passed" if not violations else "geometry_checks_failed"
        ),
        "panel_count": len(panels),
        "registered_text_artist_count": registered_artist_count,
        "checks": checks,
        "violation_counts": dict(sorted(counts.items())),
        "violations": violations,
        "authority": _layout_authority_boundary(),
    }


def _physical_size_mm(value: float, unit: object) -> float:
    normalized = str(unit or "").lower()
    factors = {
        "mm": 1.0,
        "cm": 10.0,
        "in": 25.4,
        "inch": 25.4,
        "pt": 25.4 / 72,
    }
    if normalized not in factors:
        raise ValueError(f"unsupported final_canvas unit: {unit}")
    return value * factors[normalized]


def _inspection_binding(
    candidate: Mapping[str, object],
) -> tuple[dict[str, object] | None, list[dict[str, object]]]:
    violations: list[dict[str, object]] = []
    inventory = candidate.get("display_artifact_inventory_ref")
    audit = candidate.get("programmatic_figure_audit_ref")
    if not isinstance(inventory, Mapping) or not isinstance(audit, Mapping):
        return None, [_layout_violation("artifact_inspection_shape_invalid")]
    artifact_format = str(inventory.get("format") or "").upper()
    sha256 = str(inventory.get("sha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", sha256):
        violations.append(
            _layout_violation("artifact_sha256_invalid", artifact_format=artifact_format)
        )
    export_integrity = candidate.get("export_integrity_ref")
    if isinstance(export_integrity, Mapping) and export_integrity.get("hard_fail") is True:
        violations.append(
            _layout_violation(
                "artifact_inspection_hard_fail", artifact_format=artifact_format
            )
        )

    dimensions = inventory.get("dimensions")
    physical_size: dict[str, float] | None = None
    if artifact_format == "PNG" and isinstance(dimensions, Mapping):
        dpi = audit.get("dpi")
        if isinstance(dpi, Mapping):
            width_px = _layout_number(dimensions.get("width_px"), "PNG width_px")
            height_px = _layout_number(dimensions.get("height_px"), "PNG height_px")
            dpi_x = _layout_number(dpi.get("x"), "PNG dpi.x")
            dpi_y = _layout_number(dpi.get("y"), "PNG dpi.y")
            physical_size = {
                "width_mm": round(width_px / dpi_x * 25.4, 6),
                "height_mm": round(height_px / dpi_y * 25.4, 6),
            }
        else:
            violations.append(_layout_violation("png_dpi_missing"))
    elif artifact_format == "PDF" and isinstance(dimensions, Mapping):
        variants = dimensions.get("variants")
        if (
            isinstance(variants, list)
            and len(variants) == 1
            and isinstance(variants[0], Mapping)
        ):
            width_pt = _layout_number(variants[0].get("width_pt"), "PDF width_pt")
            height_pt = _layout_number(variants[0].get("height_pt"), "PDF height_pt")
            physical_size = {
                "width_mm": round(width_pt / 72 * 25.4, 6),
                "height_mm": round(height_pt / 72 * 25.4, 6),
            }
        else:
            violations.append(_layout_violation("pdf_page_size_not_single_fixed_canvas"))
    else:
        violations.append(
            _layout_violation(
                "paired_export_format_unsupported", artifact_format=artifact_format
            )
        )

    binding = {
        "format": artifact_format,
        "sha256": sha256,
        "size_bytes": inventory.get("size_bytes"),
        "dimensions": dimensions,
        "page_count": inventory.get("page_count"),
        "dpi": audit.get("dpi"),
        "physical_size_mm": physical_size,
    }
    return binding, violations


def build_layout_qc_receipt(
    registry: Mapping[str, object],
    artifact_inspections: Sequence[Mapping[str, object]],
) -> dict[str, Any]:
    """Bind layout checks to final PNG/PDF bytes without issuing authority."""

    layout_audit = audit_layout_registry(registry)
    violations = list(layout_audit["violations"])
    bindings: list[dict[str, object]] = []
    for candidate in artifact_inspections:
        binding, artifact_violations = _inspection_binding(candidate)
        violations.extend(artifact_violations)
        if binding is not None:
            bindings.append(binding)
    bindings.sort(key=lambda item: str(item.get("format")))

    formats = [str(item.get("format")) for item in bindings]
    format_counts = Counter(formats)
    for artifact_format in ("PNG", "PDF"):
        if format_counts[artifact_format] == 0:
            violations.append(
                _layout_violation(
                    "paired_export_format_missing", artifact_format=artifact_format
                )
            )
        elif format_counts[artifact_format] > 1:
            violations.append(
                _layout_violation(
                    "paired_export_format_duplicate", artifact_format=artifact_format
                )
            )

    canvas = registry["final_canvas"]
    target_width_mm = _physical_size_mm(
        _layout_number(canvas.get("width"), "final_canvas.width"), canvas.get("unit")
    )
    target_height_mm = _physical_size_mm(
        _layout_number(canvas.get("height"), "final_canvas.height"), canvas.get("unit")
    )
    tolerance_mm = _layout_number(
        registry.get("final_size_tolerance_mm", 0.25), "final_size_tolerance_mm"
    )
    if tolerance_mm < 0:
        raise ValueError("final_size_tolerance_mm must be non-negative")
    for binding in bindings:
        physical = binding.get("physical_size_mm")
        if not isinstance(physical, Mapping):
            violations.append(
                _layout_violation(
                    "artifact_physical_size_unavailable",
                    artifact_format=binding.get("format"),
                )
            )
            continue
        width_delta = abs(float(physical["width_mm"]) - target_width_mm)
        height_delta = abs(float(physical["height_mm"]) - target_height_mm)
        if width_delta > tolerance_mm or height_delta > tolerance_mm:
            violations.append(
                _layout_violation(
                    "artifact_final_size_mismatch",
                    artifact_format=binding.get("format"),
                    width_delta_mm=round(width_delta, 6),
                    height_delta_mm=round(height_delta, 6),
                    tolerance_mm=tolerance_mm,
                )
            )

    generation_source_ref = normalize_evidence_ref(
        registry.get("generation_source_ref")
    )
    if not generation_source_ref:
        violations.append(_layout_violation("generation_source_ref_missing"))
    fixture_refs = registry.get("regression_fixture_refs")
    if not isinstance(fixture_refs, list):
        fixture_id = registry.get("fixture_id")
        fixture_refs = [fixture_id] if fixture_id else []
    fixture_refs = sorted(str(item) for item in fixture_refs if item)
    if not fixture_refs:
        violations.append(_layout_violation("regression_fixture_ref_missing"))

    violations.sort(
        key=lambda item: json.dumps(item, ensure_ascii=True, sort_keys=True)
    )
    artifact_failure_codes = {
        "artifact_inspection_shape_invalid",
        "artifact_sha256_invalid",
        "artifact_inspection_hard_fail",
        "png_dpi_missing",
        "pdf_page_size_not_single_fixed_canvas",
        "paired_export_format_unsupported",
        "paired_export_format_missing",
        "paired_export_format_duplicate",
        "artifact_physical_size_unavailable",
        "artifact_final_size_mismatch",
    }
    checks = dict(layout_audit["checks"])
    checks["png_pdf_final_size_and_sha_bound"] = not any(
        item["code"] in artifact_failure_codes for item in violations
    )
    payload = {
        "surface_kind": LAYOUT_QC_SURFACE_KIND,
        "generation_source_ref": generation_source_ref,
        "registry_sha256": layout_audit["registry_sha256"],
        "artifact_bindings": bindings,
        "final_canvas": canvas,
        "safe_inset_px": registry["safe_inset_px"],
        "lane_bounds_px": {
            lane: registry["lanes"][lane]
            for lane in ("plotting_data", "annotation")
        },
        "bbox_registry_summary": {
            "panel_count": layout_audit["panel_count"],
            "registered_text_artist_count": layout_audit[
                "registered_text_artist_count"
            ],
        },
        "checks": checks,
        "violations": violations,
        "regression_fixture_refs": fixture_refs,
        "machine_check_status": (
            "geometry_checks_passed" if not violations else "geometry_checks_failed"
        ),
        "authority": False,
        "authority_boundary": _layout_authority_boundary(),
        "publication_ready": False,
    }
    return {
        "receipt_id": f"sha256:{_canonical_json_sha256(payload)}",
        **payload,
    }


def _normalize_dpi(value: object) -> dict[str, float] | None:
    if isinstance(value, (int, float)) and value > 0:
        return {"x": round(float(value), 3), "y": round(float(value), 3)}
    if isinstance(value, (tuple, list)) and len(value) >= 2:
        try:
            x, y = float(value[0]), float(value[1])
        except (TypeError, ValueError):
            return None
        if x > 0 and y > 0:
            return {"x": round(x, 3), "y": round(y, 3)}
    return None


def _raster_content_density(image: object) -> dict[str, Any]:
    from PIL import Image, ImageChops

    preview = image.convert("RGBA")
    preview.thumbnail((512, 512), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", preview.size, "white")
    flattened = Image.alpha_composite(canvas, preview).convert("RGB")
    width, height = flattened.size
    corners = (
        flattened.getpixel((0, 0)),
        flattened.getpixel((width - 1, 0)),
        flattened.getpixel((0, height - 1)),
        flattened.getpixel((width - 1, height - 1)),
    )
    background = max(set(corners), key=corners.count)
    difference = ImageChops.difference(
        flattened, Image.new("RGB", flattened.size, background)
    ).convert("L")
    histogram = difference.histogram()
    sampled_pixels = width * height
    active_pixels = sum(histogram[9:])
    return {
        "value": round(active_pixels / sampled_pixels, 6),
        "sampled_pixels": sampled_pixels,
        "background_rgb": list(background),
        "basis": "rendered_non_background_fraction",
    }


def _raster_blank_evidence(image: object) -> dict[str, Any]:
    bands = image.getbands()
    extrema = image.getextrema()
    if not extrema:
        return {"confirmed": False, "basis": "full_frame_extrema_unavailable"}
    band_extrema = list(extrema) if isinstance(extrema[0], tuple) else [extrema]
    if "A" in bands and band_extrema[bands.index("A")][1] == 0:
        return {"confirmed": True, "basis": "full_frame_alpha_zero"}
    return {
        "confirmed": all(low == high for low, high in band_extrema),
        "basis": "full_frame_channel_extrema",
    }


def _inspect_raster(
    path: Path,
    audit: dict[str, Any],
    findings: list[dict[str, Any]],
    *,
    expected_raster: bool,
) -> None:
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError:
        findings.append(
            _finding(
                "dependency_missing",
                "warning",
                "Pillow is required to inspect raster artifact content",
                "display_qc_review_hint",
                dependency="Pillow",
                required_for=["PNG", "JPEG", "TIFF"],
            )
        )
        return

    try:
        with Image.open(path) as image:
            audit["format"] = image.format
            frame_count = int(getattr(image, "n_frames", 1))
            audit["page_count"] = frame_count
            frame_dimensions: list[dict[str, int]] = []
            frame_densities: list[dict[str, Any]] = []
            blank_frames: list[int] = []
            for frame_index in range(frame_count):
                image.seek(frame_index)
                image.load()
                width, height = image.size
                frame_dimensions.append({"width_px": width, "height_px": height})
                density = _raster_content_density(image)
                density["frame"] = frame_index + 1
                frame_densities.append(density)
                if _raster_blank_evidence(image)["confirmed"]:
                    blank_frames.append(frame_index + 1)

            audit["dimensions"] = frame_dimensions[0]
            if frame_count > 1:
                audit["frame_dimension_variants"] = [
                    {
                        "width_px": width,
                        "height_px": height,
                        "frame_count": sum(
                            row == {"width_px": width, "height_px": height}
                            for row in frame_dimensions
                        ),
                    }
                    for width, height in dict.fromkeys(
                        (row["width_px"], row["height_px"])
                        for row in frame_dimensions
                    )
                ]
            sampled_pixels = sum(item["sampled_pixels"] for item in frame_densities)
            weighted_density = sum(
                item["value"] * item["sampled_pixels"] for item in frame_densities
            ) / sampled_pixels
            density_values = [item["value"] for item in frame_densities]
            audit["content_density"] = {
                "value": round(weighted_density, 6),
                "minimum": min(density_values),
                "maximum": max(density_values),
                "basis": "rendered_non_background_fraction",
                "inspected_frame_count": frame_count,
            }
            audit["dpi"] = _normalize_dpi(image.info.get("dpi"))
            audit["raster_metadata"] = {
                "mode": image.mode,
                "frame_count": frame_count,
                "blank_detection_basis": "full_frame_visible_uniformity",
            }
            audit["blank"] = bool(blank_frames)
            audit["content_readable"] = True
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError) as exc:
        audit["content_readable"] = False
        if expected_raster:
            findings.append(
                _finding(
                    "artifact_corrupt",
                    "hard_fail",
                    "Raster artifact could not be decoded",
                    "artifact_owner_repair",
                    error_type=type(exc).__name__,
                )
            )
        else:
            findings.append(
                _finding(
                    "unsupported_format",
                    "warning",
                    "Artifact format is outside the supported PNG/JPEG/TIFF/PDF set",
                    "display_qc_review_hint",
                    suffix=path.suffix.lower() or None,
                )
            )
        return

    if audit["format"] not in SUPPORTED_RASTER_FORMATS:
        findings.append(
            _finding(
                "unsupported_format",
                "warning",
                "Raster format is outside the supported PNG/JPEG/TIFF set",
                "display_qc_review_hint",
                detected_format=audit["format"],
            )
        )
    expected_suffixes = RASTER_FORMAT_SUFFIXES.get(audit["format"])
    if expected_suffixes and path.suffix.lower() not in expected_suffixes:
        findings.append(
            _finding(
                "artifact_format_suffix_mismatch",
                "warning",
                "Artifact suffix does not match the decoded raster format",
                "artifact_owner_repair",
                suffix=path.suffix.lower() or None,
                detected_format=audit["format"],
                expected_suffixes=sorted(expected_suffixes),
            )
        )
    if audit["blank"]:
        findings.append(
            _finding(
                "artifact_blank",
                "hard_fail",
                "One or more raster frames are confirmed uniformly blank or transparent",
                "artifact_owner_repair",
                blank_frames=blank_frames,
            )
        )
    dimensions = audit["dimensions"]
    if min(dimensions["width_px"], dimensions["height_px"]) < MIN_RASTER_DIMENSION_PX:
        findings.append(
            _finding(
                "dimensions_below_review_floor",
                "warning",
                "Raster dimensions are below the 600 px shortest-edge review floor",
                "display_redesign",
                dimensions=dimensions,
            )
        )
    if audit["dpi"] is None:
        findings.append(
            _finding(
                "dpi_missing",
                "warning",
                "Raster DPI metadata is missing",
                "display_redesign",
            )
        )
    elif min(audit["dpi"].values()) < MIN_RASTER_DPI:
        findings.append(
            _finding(
                "dpi_below_review_floor",
                "warning",
                "Raster DPI metadata is below the 150 DPI review floor",
                "display_redesign",
                dpi=audit["dpi"],
            )
        )
    if audit["content_density"]["value"] >= HIGH_CONTENT_DENSITY:
        findings.append(
            _finding(
                "content_density_high",
                "warning",
                "Rendered content density is high and merits final-size readability review",
                "display_redesign",
                content_density=audit["content_density"]["value"],
            )
        )


def _load_pymupdf() -> object | None:
    try:
        import pymupdf

        return pymupdf
    except ImportError:
        try:
            import fitz

            return fitz
        except ImportError:
            return None


def _pdf_page_density(pixmap: object) -> dict[str, Any]:
    samples = memoryview(pixmap.samples)
    width, height, stride = pixmap.width, pixmap.height, pixmap.stride
    corner_offsets = (0, width - 1, (height - 1) * stride, (height - 1) * stride + width - 1)
    corners = [int(samples[offset]) for offset in corner_offsets]
    background = max(set(corners), key=corners.count)
    active_pixels = 0
    for y in range(height):
        row = samples[y * stride : y * stride + width]
        active_pixels += sum(abs(int(value) - background) > 8 for value in row)
    sampled_pixels = width * height
    return {
        "value": round(active_pixels / sampled_pixels, 6),
        "sampled_pixels": sampled_pixels,
        "background_gray": background,
        "basis": "36_dpi_rendered_non_background_fraction",
    }


def _pdf_page_pixel_hash(page: object, fitz: object, page_number: int) -> dict[str, Any]:
    contract = PAGE_HASH_RASTER_CONTRACT
    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(contract["scale_x"], contract["scale_y"]),
        colorspace=fitz.csRGB,
        alpha=contract["alpha"],
        annots=contract["annotations"],
    )
    width = int(pixmap.width)
    height = int(pixmap.height)
    row_bytes = width * 3
    samples = memoryview(pixmap.samples)
    if pixmap.stride == row_bytes:
        pixels = bytes(samples)
    else:
        pixels = b"".join(
            bytes(samples[offset : offset + row_bytes])
            for offset in range(0, pixmap.stride * height, pixmap.stride)
        )
    return {
        "page_number": page_number,
        "width": width,
        "height": height,
        "pixel_format": contract["pixel_format"],
        "pixel_sha256": f"sha256:{hashlib.sha256(pixels).hexdigest()}",
    }


def _font_embedding_state(font_type: object, font_program: object) -> bool | None:
    if font_program:
        return True
    normalized_type = str(font_type or "").strip().lower()
    if normalized_type == "type3":
        return None
    if normalized_type in {"type1", "mmtype1", "truetype"}:
        return False
    return None


def _inspect_pdf(
    path: Path, audit: dict[str, Any], findings: list[dict[str, Any]]
) -> None:
    fitz = _load_pymupdf()
    audit["format"] = "PDF"
    if fitz is None:
        findings.append(
            _finding(
                "dependency_missing",
                "warning",
                "PyMuPDF is required to inspect PDF pages, fonts, and metadata",
                "display_qc_review_hint",
                dependency="PyMuPDF",
                import_names=["pymupdf", "fitz"],
            )
        )
        return

    try:
        document = fitz.open(str(path))
    except (OSError, RuntimeError, ValueError) as exc:
        audit["content_readable"] = False
        findings.append(
            _finding(
                "artifact_corrupt",
                "hard_fail",
                "PDF artifact could not be opened",
                "artifact_owner_repair",
                error_type=type(exc).__name__,
            )
        )
        return

    try:
        if getattr(document, "needs_pass", False):
            audit["content_readable"] = False
            findings.append(
                _finding(
                    "artifact_unreadable",
                    "hard_fail",
                    "Encrypted PDF requires a password before inspection",
                    "artifact_owner_repair",
                )
            )
            return
        audit["page_count"] = document.page_count
        if document.page_count == 0:
            audit["content_readable"] = False
            findings.append(
                _finding(
                    "artifact_corrupt",
                    "hard_fail",
                    "PDF contains no pages",
                    "artifact_owner_repair",
                )
            )
            return

        metadata = getattr(document, "metadata", {}) or {}
        audit["pdf_metadata"] = {
            str(key): value for key, value in metadata.items() if value not in (None, "")
        }
        page_dimensions: list[tuple[float, float]] = []
        page_densities: list[dict[str, Any]] = []
        page_pixel_hashes: list[dict[str, Any]] = []
        blank_pages: list[int] = []
        fonts: dict[tuple[object, object], dict[str, Any]] = {}
        has_text = False

        for page_index in range(document.page_count):
            page = document.load_page(page_index)
            rect = page.rect
            page_dimensions.append(
                (round(float(rect.width), 3), round(float(rect.height), 3))
            )
            has_text = has_text or bool(page.get_text("text").strip())
            for font in page.get_fonts(full=True):
                xref = font[0] if font else 0
                font_extension = font[1] if len(font) > 1 else ""
                font_type = font[2] if len(font) > 2 else ""
                basefont = font[3] if len(font) > 3 else ""
                key = (xref, basefont)
                if key in fonts:
                    continue
                embedded: bool | None = None
                embedding_evidence = "font_program_unverified"
                if isinstance(xref, int) and xref > 0:
                    try:
                        extracted = document.extract_font(xref)
                        font_program = extracted[-1] if extracted else None
                        embedded = _font_embedding_state(font_type, font_program)
                        if embedded is True:
                            embedding_evidence = "extractable_font_program"
                        elif embedded is False:
                            embedding_evidence = "empty_extractable_font_program"
                        elif str(font_type).lower() == "type3":
                            embedding_evidence = "type3_charprocs_not_font_program"
                    except (OSError, RuntimeError, ValueError):
                        embedded = None
                fonts[key] = {
                    "font_file_extension": font_extension,
                    "font_type": font_type,
                    "basefont": basefont,
                    "resource_name": font[4] if len(font) > 4 else "",
                    "encoding": font[5] if len(font) > 5 else "",
                    "embedded": embedded,
                    "embedding_evidence": embedding_evidence,
                }
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(0.5, 0.5), colorspace=fitz.csGRAY, alpha=False
            )
            density = _pdf_page_density(pixmap)
            density["page"] = page_index + 1
            page_densities.append(density)
            page_pixel_hashes.append(
                _pdf_page_pixel_hash(page, fitz, page_index + 1)
            )
            get_bboxlog = getattr(page, "get_bboxlog", None)
            if callable(get_bboxlog) and not get_bboxlog():
                blank_pages.append(page_index + 1)

        audit["dimensions"] = {
            "unit": "pt",
            "variants": [
                {
                    "width_pt": width,
                    "height_pt": height,
                    "page_count": page_dimensions.count((width, height)),
                }
                for width, height in dict.fromkeys(page_dimensions)
            ],
        }
        sampled_pixels = sum(item["sampled_pixels"] for item in page_densities)
        weighted_density = sum(
            item["value"] * item["sampled_pixels"] for item in page_densities
        ) / sampled_pixels
        density_values = [item["value"] for item in page_densities]
        audit["content_density"] = {
            "value": round(weighted_density, 6),
            "minimum": min(density_values),
            "maximum": max(density_values),
            "basis": "36_dpi_rendered_non_background_fraction",
            "inspected_page_count": document.page_count,
        }
        audit["page_pixel_hashes"] = page_pixel_hashes
        audit["page_pixel_raster_contract"] = dict(PAGE_HASH_RASTER_CONTRACT)
        font_rows = list(fonts.values())
        audit["font_summary"] = {
            "font_count": len(font_rows),
            "embedded_count": sum(row["embedded"] is True for row in font_rows),
            "unembedded_count": sum(row["embedded"] is False for row in font_rows),
            "unknown_embedding_count": sum(row["embedded"] is None for row in font_rows),
            "fonts": font_rows[:64],
            "fonts_truncated": len(font_rows) > 64,
        }
        audit["blank_detection"] = {
            "basis": "empty_pdf_page_display_list",
            "confirmed_blank_pages": blank_pages[:20],
        }
        audit["blank"] = bool(blank_pages)
        audit["content_readable"] = True

        if blank_pages:
            findings.append(
                _finding(
                    "artifact_blank",
                    "hard_fail",
                    "One or more PDF pages have a confirmed empty display list",
                    "artifact_owner_repair",
                    blank_page_count=len(blank_pages),
                    blank_pages=blank_pages[:20],
                    blank_pages_truncated=len(blank_pages) > 20,
                )
            )
        small_pages = [
            page_index + 1
            for page_index, dimensions in enumerate(page_dimensions)
            if min(dimensions) < 144
        ]
        if small_pages:
            findings.append(
                _finding(
                    "dimensions_below_review_floor",
                    "warning",
                    "PDF page dimensions are below the 2 inch shortest-edge review floor",
                    "display_redesign",
                    page_count=len(small_pages),
                    pages=small_pages[:20],
                    pages_truncated=len(small_pages) > 20,
                )
            )
        if has_text and not font_rows:
            findings.append(
                _finding(
                    "pdf_font_metadata_missing",
                    "warning",
                    "PDF contains text but exposed no font metadata",
                    "display_redesign",
                )
            )
        unembedded_fonts = [
            row["basefont"] or row["resource_name"] or row["font_type"]
            for row in font_rows
            if row["embedded"] is False
        ]
        if unembedded_fonts:
            findings.append(
                _finding(
                    "pdf_font_not_embedded",
                    "warning",
                    "PDF exposes one or more fonts without embedded font data",
                    "display_redesign",
                    font_count=len(unembedded_fonts),
                    fonts=unembedded_fonts[:20],
                    fonts_truncated=len(unembedded_fonts) > 20,
                )
            )
        if audit["content_density"]["value"] >= HIGH_CONTENT_DENSITY:
            findings.append(
                _finding(
                    "content_density_high",
                    "warning",
                    "Rendered PDF content density is high and merits final-size readability review",
                    "display_redesign",
                    content_density=audit["content_density"]["value"],
                )
            )
        if getattr(document, "is_repaired", False):
            findings.append(
                _finding(
                    "pdf_repaired_on_open",
                    "warning",
                    "PyMuPDF repaired the PDF while opening it",
                    "artifact_owner_repair",
                )
            )
    except (OSError, RuntimeError, ValueError) as exc:
        audit["content_readable"] = False
        findings.append(
            _finding(
                "artifact_unreadable",
                "hard_fail",
                "PDF pages could not be fully inspected",
                "artifact_owner_repair",
                error_type=type(exc).__name__,
            )
        )
    finally:
        document.close()


def _finalize_inspection(
    candidate: dict[str, Any], findings: list[dict[str, Any]]
) -> dict[str, Any]:
    audit = candidate["programmatic_figure_audit_ref"]
    hard_fail = any(finding["severity"] == "hard_fail" for finding in findings)
    warning_codes = [
        finding["code"] for finding in findings if finding["severity"] == "warning"
    ]
    finding_codes = [finding["code"] for finding in findings]
    status = (
        "hard_fail"
        if hard_fail
        else "warning"
        if warning_codes
        else "no_programmatic_findings"
    )
    route = next(
        (
            finding["route_back_candidate"]
            for finding in findings
            if finding["severity"] == "hard_fail"
        ),
        findings[0]["route_back_candidate"] if findings else None,
    )
    accessibility_codes = {
        "content_density_high",
        "dimensions_below_review_floor",
        "dpi_below_review_floor",
        "dpi_missing",
        "pdf_font_metadata_missing",
        "pdf_font_not_embedded",
    }
    audit["finding_codes"] = finding_codes
    candidate["display_artifact_inventory_ref"] = {
        key: audit[key]
        for key in ("path", "sha256", "size_bytes", "format", "dimensions", "page_count")
    }
    candidate["export_integrity_ref"] = {
        "inspection_status": status,
        "hard_fail": hard_fail,
        "file_readable": audit["file_readable"],
        "content_readable": audit["content_readable"],
        "blank": audit["blank"],
        "finding_codes": finding_codes,
        "writes_authority": False,
    }
    candidate["accessibility_and_size_ref"] = {
        "dimensions": audit["dimensions"],
        "dpi": audit["dpi"],
        "content_density": audit["content_density"],
        "font_summary": audit["font_summary"],
        "finding_codes": [code for code in warning_codes if code in accessibility_codes],
        "writes_authority": False,
    }
    candidate["findings"] = findings
    candidate["inspection_status"] = status
    candidate["route_back_candidate"] = route
    candidate["writes_authority"] = False
    for ref in (
        "display_artifact_inventory_ref",
        "programmatic_figure_audit_ref",
        "export_integrity_ref",
        "accessibility_and_size_ref",
    ):
        candidate["candidate_refs"][ref] = f"inline:#/{ref}"
    return candidate


def inspect_display_artifact(artifact_path: str | Path) -> dict[str, Any]:
    """Inspect one rendered artifact without mutating it or issuing a verdict."""

    requested_path = Path(artifact_path).expanduser()
    try:
        path = requested_path.resolve(strict=False)
    except OSError:
        path = requested_path.absolute()
    candidate = display_qc_skeleton(str(path))
    candidate["surface_kind"] = "display_artifact_qc_inspection_candidate"
    candidate["programmatic_figure_audit_ref"] = {
        "path": str(path),
        "sha256": None,
        "size_bytes": None,
        "format": None,
        "dimensions": None,
        "page_count": None,
        "dpi": None,
        "content_density": None,
        "font_summary": None,
        "pdf_metadata": None,
        "page_pixel_hashes": None,
        "page_pixel_raster_contract": None,
        "file_readable": False,
        "content_readable": None,
        "blank": None,
        "writes_authority": False,
    }
    audit = candidate["programmatic_figure_audit_ref"]
    findings: list[dict[str, Any]] = []

    try:
        stat = path.stat()
    except FileNotFoundError:
        findings.append(
            _finding(
                "artifact_missing",
                "hard_fail",
                "Artifact path does not exist",
                "artifact_owner_repair",
            )
        )
        return _finalize_inspection(candidate, findings)
    except OSError as exc:
        findings.append(
            _finding(
                "artifact_unreadable",
                "hard_fail",
                "Artifact metadata could not be read",
                "artifact_owner_repair",
                error_type=type(exc).__name__,
            )
        )
        return _finalize_inspection(candidate, findings)

    audit["size_bytes"] = stat.st_size
    if not path.is_file():
        findings.append(
            _finding(
                "artifact_unreadable",
                "hard_fail",
                "Artifact path is not a regular file",
                "artifact_owner_repair",
            )
        )
        return _finalize_inspection(candidate, findings)

    try:
        audit["sha256"] = _sha256(path)
        audit["file_readable"] = True
        with path.open("rb") as handle:
            prefix = handle.read(1024)
    except OSError as exc:
        findings.append(
            _finding(
                "artifact_unreadable",
                "hard_fail",
                "Artifact bytes could not be read",
                "artifact_owner_repair",
                error_type=type(exc).__name__,
            )
        )
        return _finalize_inspection(candidate, findings)

    if stat.st_size == 0:
        audit["content_readable"] = False
        findings.append(
            _finding(
                "artifact_zero_byte",
                "hard_fail",
                "Artifact file is empty",
                "artifact_owner_repair",
            )
        )
        return _finalize_inspection(candidate, findings)

    suffix = path.suffix.lower()
    if b"%PDF-" in prefix:
        if suffix != ".pdf":
            findings.append(
                _finding(
                    "artifact_format_suffix_mismatch",
                    "warning",
                    "Artifact suffix does not match the detected PDF format",
                    "artifact_owner_repair",
                    suffix=suffix or None,
                    detected_format="PDF",
                    expected_suffixes=[".pdf"],
                )
            )
        _inspect_pdf(path, audit, findings)
    elif suffix == ".pdf":
        audit["content_readable"] = False
        findings.append(
            _finding(
                "artifact_corrupt",
                "hard_fail",
                "PDF file does not start with a PDF signature",
                "artifact_owner_repair",
            )
        )
    else:
        _inspect_raster(
            path, audit, findings, expected_raster=suffix in RASTER_SUFFIXES
        )
    return _finalize_inspection(candidate, findings)


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect display artifacts or emit a refs-only layout QC receipt"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--inspect", metavar="PATH", help="PNG/JPEG/TIFF/PDF path")
    mode.add_argument(
        "--layout-registry", metavar="JSON", help="renderer-produced bbox registry"
    )
    parser.add_argument("--png", metavar="PATH", help="final fixed-canvas PNG")
    parser.add_argument("--pdf", metavar="PATH", help="final fixed-canvas PDF")
    args = parser.parse_args(argv)
    if args.inspect is None and args.layout_registry is None:
        if args.png or args.pdf:
            parser.error("--png and --pdf require --layout-registry")
        _self_check()
        return 0
    if args.inspect is not None:
        if args.png or args.pdf:
            parser.error("--png and --pdf cannot be combined with --inspect")
        candidate = inspect_display_artifact(args.inspect)
        print(json.dumps(candidate, indent=2, sort_keys=True))
        return 2 if candidate["export_integrity_ref"]["hard_fail"] else 0
    if not args.png or not args.pdf:
        parser.error("--layout-registry requires both --png and --pdf")
    registry_path = Path(args.layout_registry)
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    receipt = build_layout_qc_receipt(
        registry,
        [inspect_display_artifact(args.png), inspect_display_artifact(args.pdf)],
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["machine_check_status"] == "geometry_checks_passed" else 2


def _self_check() -> None:
    assert normalize_evidence_ref("  fig:1 ;") == "fig:1"
    row = display_artifact_row("artifact:pdf", page_ref=" page 2 ", panel_ref="A")
    assert row["writes_authority"] is False
    skeleton = display_qc_skeleton("artifact:pdf")
    assert "display_qc_support_map_ref" in skeleton["required_refs"]
    assert "programmatic_figure_audit_ref" in skeleton["required_refs"]
    assert skeleton["authority"]["can_sign_visual_audit_receipt"] is False
    assert classify_display_qc_route("blank exported panel")["route"] == "artifact_owner_repair"
    support = display_qc_support_map([{"artifact_ref": "fig:1", "issue": "caption drift"}])
    assert support[0]["route_back_candidate"] == "caption_numbering_repair"
    assert lint_forbidden_display_qc_claims("publication-ready with owner receipt")
    assert _font_embedding_state("Type3", b"") is None
    assert _font_embedding_state("Type1", b"") is False
    assert _font_embedding_state("Type0", b"font-program") is True

    page_a = {
        "page_number": 1,
        "width": 1224,
        "height": 1584,
        "pixel_format": "RGB8",
        "pixel_sha256": f"sha256:{'1' * 64}",
    }
    page_b = {
        "page_number": 2,
        "width": 1224,
        "height": 1584,
        "pixel_format": "RGB8",
        "pixel_sha256": f"sha256:{'2' * 64}",
    }
    cache_a = build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_invocation_ref={
            "kind": "opl_stage_attempt",
            "ref": "attempt://display-a",
            "sha256": f"sha256:{'8' * 64}",
        },
        origin_reviewer_evidence_ref={
            "kind": "scholarskills_display_evidence",
            "ref": "evidence://display-a",
            "sha256": f"sha256:{'9' * 64}",
            "size_bytes": 123,
        },
    )
    cache_same_pixels_other_provenance = build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_invocation_ref={
            "kind": "opl_stage_attempt",
            "ref": "attempt://different-model-runtime-path",
            "sha256": f"sha256:{'a' * 64}",
        },
        origin_reviewer_evidence_ref={
            "kind": "scholarskills_display_evidence",
            "ref": "evidence://different-pdf-metadata",
            "sha256": f"sha256:{'b' * 64}",
            "size_bytes": 456,
        },
    )
    assert cache_a["cache_key_sha256"] == (
        "sha256:f159ceb039e91fcdf43a3402b195592cbce25841837473284b03760a359a012a"
    )
    assert cache_a["cache_key_sha256"] == cache_same_pixels_other_provenance[
        "cache_key_sha256"
    ]
    changed_pixel = dict(page_b)
    changed_pixel["pixel_sha256"] = f"sha256:{'5' * 64}"
    assert cache_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [page_a, changed_pixel],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_invocation_ref=cache_a["origin_reviewer_invocation_ref"],
        origin_reviewer_evidence_ref=cache_a["origin_reviewer_evidence_ref"],
    )["cache_key_sha256"]
    changed_geometry = dict(page_b, width=1225)
    assert cache_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [page_a, changed_geometry],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_invocation_ref=cache_a["origin_reviewer_invocation_ref"],
        origin_reviewer_evidence_ref=cache_a["origin_reviewer_evidence_ref"],
    )["cache_key_sha256"]
    reordered_a = dict(page_b, page_number=1)
    reordered_b = dict(page_a, page_number=2)
    assert cache_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [reordered_a, reordered_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_invocation_ref=cache_a["origin_reviewer_invocation_ref"],
        origin_reviewer_evidence_ref=cache_a["origin_reviewer_evidence_ref"],
    )["cache_key_sha256"]
    assert cache_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'6' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_invocation_ref=cache_a["origin_reviewer_invocation_ref"],
        origin_reviewer_evidence_ref=cache_a["origin_reviewer_evidence_ref"],
    )["cache_key_sha256"]
    assert cache_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'7' * 64}",
        origin_reviewer_invocation_ref=cache_a["origin_reviewer_invocation_ref"],
        origin_reviewer_evidence_ref=cache_a["origin_reviewer_evidence_ref"],
    )["cache_key_sha256"]
    unbound_cache = build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
    )
    assert unbound_cache["cache_reuse_eligible"] is False
    empty_shell_cache = build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_invocation_ref={"ref": "attempt://empty-shell"},
        origin_reviewer_evidence_ref={
            "ref": "evidence://empty-shell",
            "sha256": "not-a-digest",
        },
    )
    assert empty_shell_cache["cache_reuse_eligible"] is False
    assert cache_a["cache_reuse_eligible"] is True
    assert cache_a["cache_authority"] is False
    assert cache_a["requires_fresh_reviewer_invocation"] is True
    assert cache_a["requires_fresh_reviewer_receipt"] is True
    assert cache_a["requires_mas_judgment"] is True
    assert all(value is False for value in cache_a["authority_boundary"].values())

    fixture_path = Path(__file__).with_name("fixtures") / "layout_qc_regression.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    layout_audit = audit_layout_registry(fixture)
    assert layout_audit["machine_check_status"] == "geometry_checks_passed"
    assert layout_audit["registered_text_artist_count"] == 6
    assert layout_audit["checks"]["annotation_lane_separate"] is True
    assert layout_audit["checks"]["measured_wrap_valid"] is True

    fake_png = {
        "display_artifact_inventory_ref": {
            "sha256": "1" * 64,
            "size_bytes": 1000,
            "format": "PNG",
            "dimensions": {"width_px": 1800, "height_px": 1000},
            "page_count": 1,
        },
        "programmatic_figure_audit_ref": {"dpi": {"x": 254, "y": 254}},
        "export_integrity_ref": {"hard_fail": False},
    }
    fake_pdf = {
        "display_artifact_inventory_ref": {
            "sha256": "2" * 64,
            "size_bytes": 800,
            "format": "PDF",
            "dimensions": {
                "unit": "pt",
                "variants": [
                    {
                        "width_pt": 510.2362204724,
                        "height_pt": 283.4645669291,
                        "page_count": 1,
                    }
                ],
            },
            "page_count": 1,
        },
        "programmatic_figure_audit_ref": {"dpi": None},
        "export_integrity_ref": {"hard_fail": False},
    }
    receipt = build_layout_qc_receipt(fixture, [fake_png, fake_pdf])
    assert receipt["machine_check_status"] == "geometry_checks_passed"
    assert receipt["artifact_bindings"][1]["sha256"] == "1" * 64
    assert receipt["authority"] is False
    assert receipt["authority_boundary"]["can_claim_quality_verdict"] is False
    assert receipt == build_layout_qc_receipt(fixture, [fake_pdf, fake_png])
    wrong_size_pdf = json.loads(json.dumps(fake_pdf))
    wrong_size_pdf["display_artifact_inventory_ref"]["dimensions"]["variants"][0][
        "width_pt"
    ] = 500
    wrong_size_receipt = build_layout_qc_receipt(
        fixture, [fake_png, wrong_size_pdf]
    )
    assert wrong_size_receipt["machine_check_status"] == "geometry_checks_failed"
    assert "artifact_final_size_mismatch" in {
        item["code"] for item in wrong_size_receipt["violations"]
    }

    manual_wrap = json.loads(json.dumps(fixture))
    manual_wrap["panels"][0]["text_artists"][1]["text_measurement"][
        "manual_breaks"
    ] = True
    failed_layout = audit_layout_registry(manual_wrap)
    assert failed_layout["machine_check_status"] == "geometry_checks_failed"
    assert failed_layout["checks"]["measured_wrap_valid"] is False

    overlap = json.loads(json.dumps(fixture))
    overlap["panels"][0]["text_artists"][2]["bbox_px"] = [60, 230, 260, 260]
    clipping = json.loads(json.dumps(fixture))
    clipping["panels"][0]["text_artists"][1]["clip_bbox_px"] = [80, 180, 320, 250]
    overflow = json.loads(json.dumps(fixture))
    overflow["panels"][0]["text_artists"][5]["bbox_px"] = [1750, 900, 1810, 925]
    minimum_spacing = json.loads(json.dumps(fixture))
    minimum_spacing["panels"][0]["text_artists"][2]["bbox_px"] = [60, 255, 260, 280]
    unsafe = json.loads(json.dumps(fixture))
    unsafe["panels"][0]["text_artists"][1]["bbox_px"] = [20, 180, 340, 250]
    lane_overlap = json.loads(json.dumps(fixture))
    lane_overlap["lanes"]["annotation"]["bbox_px"] = [1400, 40, 1760, 960]
    wrong_lane = json.loads(json.dumps(fixture))
    wrong_lane["panels"][0]["text_artists"][3]["lane"] = "plotting_data"
    wrong_lane["panels"][0]["text_artists"][3]["bbox_px"] = [1200, 190, 1440, 220]
    wrong_lane["panels"][0]["text_artists"][3]["clip_bbox_px"] = [380, 40, 1460, 960]
    for broken_registry, expected_code in [
        (overlap, "text_artist_overlap"),
        (clipping, "artist_clipped"),
        (overflow, "artist_canvas_overflow"),
        (minimum_spacing, "text_artist_minimum_spacing_violation"),
        (unsafe, "artist_safe_inset_violation"),
        (lane_overlap, "data_annotation_lane_overlap"),
        (wrong_lane, "numeric_annotation_outside_annotation_lane"),
    ]:
        broken_audit = audit_layout_registry(broken_registry)
        assert expected_code in {item["code"] for item in broken_audit["violations"]}

    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        missing = inspect_display_artifact(root / "missing.png")
        assert missing["export_integrity_ref"]["hard_fail"] is True
        assert "artifact_missing" in missing["export_integrity_ref"]["finding_codes"]

        pillow_available = True
        fitz_available = False
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            pillow_available = False
            dependency_probe = root / "dependency-probe.png"
            dependency_probe.write_bytes(b"\x89PNG\r\n\x1a\n")
            dependency = inspect_display_artifact(dependency_probe)
            assert dependency["export_integrity_ref"]["hard_fail"] is False
            assert "dependency_missing" in dependency["export_integrity_ref"]["finding_codes"]
        else:
            blank_path = root / "blank.png"
            Image.new("RGB", (1200, 900), "white").save(blank_path, dpi=(300, 300))
            blank = inspect_display_artifact(blank_path)
            assert blank["export_integrity_ref"]["hard_fail"] is True
            assert "artifact_blank" in blank["export_integrity_ref"]["finding_codes"]

            transparent_path = root / "transparent.png"
            transparent_image = Image.new("RGBA", (1200, 900), (255, 0, 0, 0))
            ImageDraw.Draw(transparent_image).rectangle(
                (100, 100, 1100, 800), fill=(0, 0, 255, 0)
            )
            transparent_image.save(transparent_path, dpi=(300, 300))
            transparent = inspect_display_artifact(transparent_path)
            assert transparent["export_integrity_ref"]["hard_fail"] is True
            assert "artifact_blank" in transparent["export_integrity_ref"][
                "finding_codes"
            ]

            sparse_path = root / "sparse.png"
            sparse_image = Image.new("1", (6000, 6000), 1)
            sparse_image.putpixel((3000, 3000), 0)
            sparse_image.save(sparse_path, dpi=(300, 300))
            sparse = inspect_display_artifact(sparse_path)
            assert sparse["export_integrity_ref"]["hard_fail"] is False
            assert "artifact_blank" not in sparse["export_integrity_ref"]["finding_codes"]

            nonblank_image = Image.new("RGB", (1200, 900), "white")
            ImageDraw.Draw(nonblank_image).rectangle(
                (100, 100, 1100, 800), fill="black"
            )
            nonblank_path = root / "nonblank.png"
            nonblank_image.save(nonblank_path, dpi=(300, 300))
            nonblank = inspect_display_artifact(nonblank_path)
            audit = nonblank["programmatic_figure_audit_ref"]
            assert nonblank["export_integrity_ref"]["hard_fail"] is False
            assert audit["format"] == "PNG"
            assert audit["dimensions"] == {"width_px": 1200, "height_px": 900}
            assert audit["content_density"]["value"] > 0

            mismatched_path = root / "nonblank.jpg"
            mismatched_path.write_bytes(nonblank_path.read_bytes())
            mismatched = inspect_display_artifact(mismatched_path)
            assert mismatched["export_integrity_ref"]["hard_fail"] is False
            assert "artifact_format_suffix_mismatch" in mismatched[
                "export_integrity_ref"
            ]["finding_codes"]
            assert mismatched["programmatic_figure_audit_ref"]["format"] == "PNG"

            pdf_mismatched_path = root / "minimal.png"
            nonblank_image.save(pdf_mismatched_path, "PDF", resolution=150)
            pdf_mismatched = inspect_display_artifact(pdf_mismatched_path)
            assert pdf_mismatched["export_integrity_ref"]["hard_fail"] is False
            assert "artifact_format_suffix_mismatch" in pdf_mismatched[
                "export_integrity_ref"
            ]["finding_codes"]
            assert pdf_mismatched["programmatic_figure_audit_ref"]["format"] == "PDF"

            pdf_path = root / "minimal.pdf"
            nonblank_image.save(pdf_path, "PDF", resolution=150)
            pdf = inspect_display_artifact(pdf_path)
            pdf_audit = pdf["programmatic_figure_audit_ref"]
            assert pdf["export_integrity_ref"]["hard_fail"] is False
            assert pdf_audit["format"] == "PDF"
            if pdf_audit["page_count"] is None:
                assert "dependency_missing" in pdf["export_integrity_ref"]["finding_codes"]
            else:
                fitz_available = True
                assert pdf_audit["page_count"] == 1
                assert len(pdf_audit["page_pixel_hashes"]) == 1
                assert pdf_audit["page_pixel_hashes"][0]["pixel_format"] == "RGB8"
                fitz = _load_pymupdf()
                metadata_pdf_path = root / "minimal-with-metadata.pdf"
                metadata_document = fitz.open(pdf_path)
                metadata = dict(metadata_document.metadata or {})
                metadata["title"] = "metadata-only change"
                metadata_document.set_metadata(metadata)
                metadata_document.save(metadata_pdf_path)
                metadata_document.close()
                metadata_pdf = inspect_display_artifact(metadata_pdf_path)
                assert metadata_pdf["programmatic_figure_audit_ref"][
                    "page_pixel_hashes"
                ] == pdf_audit["page_pixel_hashes"]
                empty_pdf_path = root / "empty.pdf"
                document = fitz.open()
                document.new_page(width=612, height=792)
                document.save(empty_pdf_path)
                document.close()
                empty_pdf = inspect_display_artifact(empty_pdf_path)
                assert empty_pdf["export_integrity_ref"]["hard_fail"] is True

                sparse_pdf_path = root / "sparse.pdf"
                document = fitz.open()
                page = document.new_page(width=612, height=792)
                page.draw_rect(
                    fitz.Rect(300, 400, 300.01, 400.01),
                    color=None,
                    fill=(0, 0, 0),
                    width=0,
                )
                document.save(sparse_pdf_path)
                document.close()
                sparse_pdf = inspect_display_artifact(sparse_pdf_path)
                assert sparse_pdf["export_integrity_ref"]["hard_fail"] is False
                assert "artifact_blank" not in sparse_pdf["export_integrity_ref"][
                    "finding_codes"
                ]

        unsupported_path = root / "notes.txt"
        unsupported_path.write_text("not a rendered artifact", encoding="utf-8")
        unsupported = inspect_display_artifact(unsupported_path)
        assert unsupported["export_integrity_ref"]["hard_fail"] is False
        expected_code = "unsupported_format" if pillow_available else "dependency_missing"
        assert expected_code in unsupported["export_integrity_ref"]["finding_codes"]

    checks = 69 if fitz_available else 62 if pillow_available else 49
    print(json.dumps({"ok": True, "checks": checks}, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(_main())
