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
    "editorial_page_composition_ref",
    "document_display_scope_coverage_ref",
    "display_render_integrity_ref",
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
SEMANTIC_FLOW_ARCHETYPE_TOKENS = (
    "accounting",
    "diagram",
    "flow",
    "schematic",
)
SEMANTIC_WRAP_ALGORITHM = "renderer_measured_greedy_word_boundary.v1"
DOCUMENT_DISPLAY_REQUIRED_EXACT_REFS = (
    "canonical_manuscript_ref",
    "table_catalog_ref",
    "figure_catalog_ref",
    "caption_legend_manifest_ref",
    "render_environment_ref",
    "font_inventory_ref",
    "composed_paper_pdf_exact_ref",
)
DOCUMENT_DISPLAY_PAGE_EVIDENCE_REFS = (
    "page_render_evidence_ref",
    "page_hash_evidence_candidate_ref",
)
EXACT_REF_FIELDS = frozenset({"kind", "ref", "size_bytes", "sha256"})
FIGURE_NUMBERING_OUTPUT_SURFACES = ("docx", "pdf")
FIGURE_NUMBERING_SOURCES = (
    "image_alt_text",
    "structured_legend_text",
    "renderer_caption_prefix",
)

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


def validate_display_render_integrity(candidate: Mapping[str, object]) -> dict[str, Any]:
    """Audit renderer/font locks and semantic parity of the final raster/vector pair."""

    findings: list[dict[str, object]] = []
    font_locks = candidate.get("font_locks")
    if not isinstance(font_locks, Sequence) or isinstance(font_locks, (str, bytes)) or not font_locks:
        findings.append(_layout_violation("display_font_locks_missing"))
        font_locks = []
    for index, lock in enumerate(font_locks):
        if not isinstance(lock, Mapping) or not str(lock.get("font_file_ref") or "").strip() or re.fullmatch(
            r"sha256:[0-9a-f]{64}", str(lock.get("font_file_sha256") or "")
        ) is None:
            findings.append(_layout_violation("display_font_lock_invalid", index=index))
    renderer = candidate.get("renderer_lock")
    if not isinstance(renderer, Mapping) or not all(
        str(renderer.get(field) or "").strip()
        for field in ("family", "version", "headless_backend")
    ):
        findings.append(_layout_violation("display_renderer_lock_invalid"))
    if candidate.get("renderer_draw_complete") is not True:
        findings.append(_layout_violation("display_renderer_draw_incomplete"))
    if candidate.get("artist_scope") != "all_text_artists":
        findings.append(_layout_violation("display_artist_scope_incomplete"))
    generation_ref = str(candidate.get("single_generation_source_ref") or "").strip()
    if not generation_ref:
        findings.append(_layout_violation("display_single_generation_source_missing"))
    exports = candidate.get("paired_exports")
    if not isinstance(exports, Sequence) or isinstance(exports, (str, bytes)):
        exports = []
    by_format: dict[str, Mapping[str, object]] = {}
    for index, export in enumerate(exports):
        if not isinstance(export, Mapping):
            findings.append(_layout_violation("display_paired_export_invalid", index=index))
            continue
        artifact_format = str(export.get("format") or "").lower()
        if artifact_format not in {"png", "pdf"} or artifact_format in by_format:
            findings.append(_layout_violation("display_paired_export_format_invalid", index=index))
            continue
        by_format[artifact_format] = export
        if not _display_render_exact_ref_valid(export.get("artifact_ref")):
            findings.append(
                _layout_violation(
                    "display_paired_export_exact_ref_invalid",
                    index=index,
                    field="artifact_ref",
                )
            )
        for field in (
            "visible_payload_sha256",
            "labels_sha256",
            "panel_order_sha256",
            "source_fingerprint",
        ):
            value = str(export.get(field) or "")
            valid = re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None
            if not valid:
                findings.append(
                    _layout_violation(
                        "display_paired_export_field_invalid", index=index, field=field
                    )
                )
        dimensions = export.get("dimensions")
        dimensions_valid = (
            isinstance(dimensions, Mapping)
            and set(dimensions) == {"width", "height", "unit"}
            and _display_render_finite_number(dimensions.get("width"))
            and _display_render_finite_number(dimensions.get("height"))
            and float(dimensions.get("width")) > 0
            and float(dimensions.get("height")) > 0
            and dimensions.get("unit") == ("px" if artifact_format == "png" else "pt")
        )
        if not dimensions_valid:
            findings.append(
                _layout_violation("display_paired_export_dimensions_invalid", index=index)
            )
        crop = export.get("crop_bounds")
        crop_coordinates = (
            crop.get("coordinates") if isinstance(crop, Mapping) else None
        )
        crop_valid = (
            isinstance(crop, Mapping)
            and set(crop) == {"coordinates", "unit"}
            and dimensions_valid
            and crop.get("unit") == dimensions.get("unit")
            and isinstance(crop_coordinates, Sequence)
            and not isinstance(crop_coordinates, (str, bytes))
            and len(crop_coordinates) == 4
            and all(
                _display_render_finite_number(value) for value in crop_coordinates
            )
            and float(crop_coordinates[2]) > float(crop_coordinates[0])
            and float(crop_coordinates[3]) > float(crop_coordinates[1])
        )
        if not crop_valid:
            findings.append(_layout_violation("display_paired_export_crop_invalid", index=index))
        elif (
            float(crop_coordinates[0]) < 0
            or float(crop_coordinates[1]) < 0
            or float(crop_coordinates[2]) > float(dimensions["width"])
            or float(crop_coordinates[3]) > float(dimensions["height"])
        ):
            findings.append(
                _layout_violation("display_paired_export_crop_outside_dimensions", index=index)
            )
        physical_dimensions = _display_render_number_sequence(
            export.get("physical_dimensions_inches"), 2
        )
        normalized_crop = _display_render_number_sequence(
            export.get("normalized_crop_bounds"), 4
        )
        resolution = export.get("resolution_per_inch")
        if artifact_format == "png":
            resolution_valid = (
                _display_render_finite_number(resolution)
                and float(resolution) > 0
            )
            units_per_inch = float(resolution) if resolution_valid else None
        else:
            resolution_valid = resolution is None
            units_per_inch = 72.0
        if not resolution_valid:
            findings.append(
                _layout_violation(
                    "display_paired_export_resolution_invalid", index=index
                )
            )
        if (
            physical_dimensions is None
            or any(value <= 0 for value in physical_dimensions)
            or not dimensions_valid
            or units_per_inch is None
            or not all(
                math.isclose(observed, expected, rel_tol=0.0, abs_tol=1e-6)
                for observed, expected in zip(
                    physical_dimensions,
                    (
                        float(dimensions["width"]) / units_per_inch,
                        float(dimensions["height"]) / units_per_inch,
                    ),
                    strict=True,
                )
            )
        ):
            findings.append(
                _layout_violation(
                    "display_paired_export_physical_dimensions_invalid", index=index
                )
            )
        if (
            normalized_crop is None
            or not crop_valid
            or not all(0.0 <= value <= 1.0 for value in normalized_crop)
            or not all(
                math.isclose(observed, expected, rel_tol=0.0, abs_tol=1e-9)
                for observed, expected in zip(
                    normalized_crop,
                    (
                        float(crop_coordinates[0]) / float(dimensions["width"]),
                        float(crop_coordinates[1]) / float(dimensions["height"]),
                        float(crop_coordinates[2]) / float(dimensions["width"]),
                        float(crop_coordinates[3]) / float(dimensions["height"]),
                    ),
                    strict=True,
                )
            )
        ):
            findings.append(
                _layout_violation(
                    "display_paired_export_normalized_crop_invalid", index=index
                )
            )
    if set(by_format) != {"png", "pdf"}:
        findings.append(_layout_violation("display_paired_export_pair_incomplete"))
    else:
        for field in (
            "visible_payload_sha256",
            "labels_sha256",
            "panel_order_sha256",
            "source_fingerprint",
            "physical_dimensions_inches",
            "normalized_crop_bounds",
        ):
            if by_format["png"].get(field) != by_format["pdf"].get(field):
                findings.append(
                    _layout_violation("display_paired_export_parity_mismatch", field=field)
                )
    if not str(candidate.get("final_scale_visual_note") or "").strip():
        findings.append(_layout_violation("display_final_scale_visual_note_missing"))
    if candidate.get("authority") is not False:
        findings.append(_layout_violation("display_render_integrity_authority_forbidden"))
    findings.sort(key=lambda item: json.dumps(item, sort_keys=True))
    complete = not findings
    return {
        "surface_kind": "display_render_integrity_ref",
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "findings": findings,
        "route_back_candidate": None if complete else {
            "route": "medical-display-qc",
            "reason": "display_render_integrity_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def _display_render_exact_ref_valid(value: object) -> bool:
    if not isinstance(value, Mapping) or set(value) != EXACT_REF_FIELDS:
        return False
    size_bytes = value.get("size_bytes")
    return (
        bool(normalize_evidence_ref(value.get("kind")))
        and bool(normalize_evidence_ref(value.get("ref")))
        and not isinstance(size_bytes, bool)
        and isinstance(size_bytes, int)
        and size_bytes > 0
        and re.fullmatch(
            r"sha256:[0-9a-f]{64}",
            str(value.get("sha256") or "").strip().lower(),
        )
        is not None
    )


def _display_render_finite_number(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


def _display_render_number_sequence(
    value: object, expected_length: int
) -> list[float] | None:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes))
        or len(value) != expected_length
        or not all(_display_render_finite_number(item) for item in value)
    ):
        return None
    return [float(item) for item in value]


def validate_figure_numbering_one_owner(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Require one numbering owner and one final label per figure and surface."""

    findings: list[dict[str, object]] = []
    if candidate.get("surface_kind") != "figure_numbering_one_owner_candidate.v1":
        findings.append(
            _figure_numbering_finding(
                "FIGURE_NUMBERING_SURFACE_KIND_INVALID",
                "surface_kind",
                "use the figure-numbering one-owner candidate surface",
            )
        )
    artifact_refs_value = candidate.get("output_artifact_refs")
    artifact_refs = artifact_refs_value if isinstance(artifact_refs_value, Mapping) else {}
    if set(artifact_refs) != set(FIGURE_NUMBERING_OUTPUT_SURFACES):
        findings.append(
            _figure_numbering_finding(
                "FIGURE_NUMBERING_OUTPUT_REF_SET_INVALID",
                "output_artifact_refs",
                "bind exactly the final DOCX and PDF outputs",
            )
        )
    for surface in FIGURE_NUMBERING_OUTPUT_SURFACES:
        if not _display_render_exact_ref_valid(artifact_refs.get(surface)):
            findings.append(
                _figure_numbering_finding(
                    "FIGURE_NUMBERING_OUTPUT_EXACT_REF_INVALID",
                    f"output_artifact_refs.{surface}",
                    "bind the final output as an exact ref",
                )
            )

    figures_value = candidate.get("figures")
    figures = (
        list(figures_value)
        if isinstance(figures_value, Sequence)
        and not isinstance(figures_value, (str, bytes, bytearray))
        else []
    )
    if not figures:
        findings.append(
            _figure_numbering_finding(
                "FIGURE_NUMBERING_INVENTORY_INVALID",
                "figures",
                "provide the complete final figure inventory",
            )
        )
    figure_ids: list[str] = []
    figure_numbers: list[int] = []
    invariants: list[dict[str, object]] = []
    for index, figure in enumerate(figures):
        path = f"figures[{index}]"
        if not isinstance(figure, Mapping):
            findings.append(
                _figure_numbering_finding(
                    "FIGURE_NUMBERING_ENTRY_INVALID",
                    path,
                    "provide a structured figure numbering entry",
                )
            )
            continue
        figure_id = str(figure.get("figure_id") or "").strip()
        figure_number = figure.get("figure_number")
        if not figure_id:
            findings.append(
                _figure_numbering_finding(
                    "FIGURE_NUMBERING_ID_MISSING",
                    f"{path}.figure_id",
                    "bind every final figure to a stable member id",
                )
            )
        else:
            figure_ids.append(figure_id)
        if (
            isinstance(figure_number, bool)
            or not isinstance(figure_number, int)
            or figure_number < 1
        ):
            findings.append(
                _figure_numbering_finding(
                    "FIGURE_NUMBER_INVALID",
                    f"{path}.figure_number",
                    "use a positive integer final figure number",
                )
            )
        else:
            figure_numbers.append(figure_number)
        surfaces_value = figure.get("output_surfaces")
        surfaces = surfaces_value if isinstance(surfaces_value, Mapping) else {}
        if set(surfaces) != set(FIGURE_NUMBERING_OUTPUT_SURFACES):
            findings.append(
                _figure_numbering_finding(
                    "FIGURE_NUMBERING_SURFACE_SET_INVALID",
                    f"{path}.output_surfaces",
                    "audit the figure on both final DOCX and PDF surfaces",
                )
            )
        for surface in FIGURE_NUMBERING_OUTPUT_SURFACES:
            surface_value = surfaces.get(surface)
            surface_path = f"{path}.output_surfaces.{surface}"
            if not isinstance(surface_value, Mapping):
                findings.append(
                    _figure_numbering_finding(
                        "FIGURE_NUMBERING_SURFACE_INVALID",
                        surface_path,
                        "declare one owner and structured occurrence counts",
                    )
                )
                continue
            declared_owner = str(surface_value.get("declared_numbering_owner") or "")
            if declared_owner not in FIGURE_NUMBERING_SOURCES:
                findings.append(
                    _figure_numbering_finding(
                        "FIGURE_NUMBERING_OWNER_INVALID",
                        f"{surface_path}.declared_numbering_owner",
                        "choose one supported numbering source as owner",
                    )
                )
            occurrences_value = surface_value.get("occurrences")
            occurrences = (
                list(occurrences_value)
                if isinstance(occurrences_value, Sequence)
                and not isinstance(occurrences_value, (str, bytes, bytearray))
                else []
            )
            counts: dict[str, int] = {}
            for occurrence_index, occurrence in enumerate(occurrences):
                occurrence_path = f"{surface_path}.occurrences[{occurrence_index}]"
                if not isinstance(occurrence, Mapping):
                    findings.append(
                        _figure_numbering_finding(
                            "FIGURE_NUMBERING_OCCURRENCE_INVALID",
                            occurrence_path,
                            "provide source and non-negative occurrence_count",
                        )
                    )
                    continue
                source = str(occurrence.get("source") or "")
                count = occurrence.get("occurrence_count")
                if source not in FIGURE_NUMBERING_SOURCES or source in counts:
                    findings.append(
                        _figure_numbering_finding(
                            "FIGURE_NUMBERING_SOURCE_INVALID",
                            f"{occurrence_path}.source",
                            "record each supported numbering source exactly once",
                        )
                    )
                    continue
                if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                    findings.append(
                        _figure_numbering_finding(
                            "FIGURE_NUMBERING_COUNT_INVALID",
                            f"{occurrence_path}.occurrence_count",
                            "use a non-negative integer final occurrence count",
                        )
                    )
                    continue
                counts[source] = count
            if set(counts) != set(FIGURE_NUMBERING_SOURCES):
                findings.append(
                    _figure_numbering_finding(
                        "FIGURE_NUMBERING_SOURCE_SET_INVALID",
                        f"{surface_path}.occurrences",
                        "account for alt text, structured legend, and renderer prefix",
                    )
                )
            total = sum(counts.values())
            owner_count = counts.get(declared_owner, 0)
            non_owner_count = total - owner_count
            if total != 1:
                findings.append(
                    _figure_numbering_finding(
                        "FIGURE_NUMBERING_EXACTLY_ONE_VIOLATION",
                        surface_path,
                        "compose exactly one final figure-number label",
                    )
                )
            if owner_count != 1 or non_owner_count != 0:
                findings.append(
                    _figure_numbering_finding(
                        "FIGURE_NUMBERING_OWNER_CARDINALITY_INVALID",
                        surface_path,
                        "emit the label once from the declared owner and zero times elsewhere",
                    )
                )
            invariants.append(
                {
                    "figure_id": figure_id,
                    "figure_number": figure_number,
                    "output_surface": surface,
                    "declared_numbering_owner": declared_owner,
                    "occurrence_count": total,
                }
            )
    if len(figure_ids) != len(set(figure_ids)):
        findings.append(
            _figure_numbering_finding(
                "FIGURE_NUMBERING_ID_DUPLICATE",
                "figures",
                "use one final numbering record per figure id",
            )
        )
    if len(figure_numbers) != len(set(figure_numbers)):
        findings.append(
            _figure_numbering_finding(
                "FIGURE_NUMBER_DUPLICATE",
                "figures",
                "assign each final figure number to one figure id",
            )
        )
    if candidate.get("authority") is not False:
        findings.append(
            _figure_numbering_finding(
                "FIGURE_NUMBERING_AUTHORITY_FORBIDDEN",
                "authority",
                "keep figure-numbering QA refs-only with authority=false",
            )
        )

    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "figure_numbering_one_owner_audit_candidate.v1",
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "output_artifact_refs": {
            surface: dict(artifact_refs[surface])
            for surface in FIGURE_NUMBERING_OUTPUT_SURFACES
            if isinstance(artifact_refs.get(surface), Mapping)
        },
        "figure_surface_invariants": invariants,
        "findings": findings,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-display-qc",
            "reason": "figure_numbering_one_owner_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def _figure_numbering_finding(code: str, field: str, action: str) -> dict[str, object]:
    return {
        "code": code,
        "field": field,
        "action": action,
        "writes_authority": False,
    }


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


def lint_document_layout_inventory(
    blocks: Sequence[Mapping[str, object]],
) -> list[dict[str, Any]]:
    """Flag editorial page-composition defects from a structured block map."""

    findings: list[dict[str, Any]] = []
    normalized: list[dict[str, Any]] = []
    for index, block in enumerate(blocks, start=1):
        block_id = str(block.get("block_id") or f"block_{index}").strip()
        block_kind = str(block.get("block_kind") or "").strip().lower()
        document_role = str(block.get("document_role") or "").strip().lower()
        artifact_role = str(block.get("artifact_role") or "").strip().lower()
        page_start = block.get("page_start")
        page_end = block.get("page_end")
        if (
            isinstance(page_start, bool)
            or not isinstance(page_start, int)
            or page_start <= 0
            or isinstance(page_end, bool)
            or not isinstance(page_end, int)
            or page_end < page_start
        ):
            findings.append(
                _finding(
                    "DOCUMENT_LAYOUT_PAGE_RANGE_INVALID",
                    "quality_debt",
                    "Document block has an invalid page range",
                    "display_redesign",
                    block_id=block_id,
                )
            )
            continue
        normalized.append(
            {
                "block_id": block_id,
                "block_kind": block_kind,
                "document_role": document_role,
                "artifact_role": artifact_role,
                "page_start": page_start,
                "page_end": page_end,
                "text": str(
                    block.get("text")
                    or block.get("title_text")
                    or block.get("visible_title")
                    or ""
                ),
                "panel_count": block.get("panel_count"),
                "continuation": block.get("continuation") is True
                or "continuation" in block_kind,
            }
        )
        supplementary = artifact_role.startswith("supplementary_") or block_kind.startswith(
            "supplementary_"
        )
        if supplementary and document_role in {"main", "main_document", "main_manuscript"}:
            findings.append(
                _finding(
                    "SUPPLEMENTARY_DISPLAY_IN_MAIN_DOCUMENT",
                    "quality_debt",
                    "A supplementary display is embedded in the main manuscript",
                    "display_redesign",
                    block_id=block_id,
                )
            )
        if block_kind in {"figure_caption", "figure_legend"} and page_start != page_end:
            findings.append(
                _finding(
                    "FIGURE_LEGEND_SPLIT_ACROSS_PAGES",
                    "quality_debt",
                    "A figure legend crosses a page boundary",
                    "display_redesign",
                    block_id=block_id,
                    page_start=page_start,
                    page_end=page_end,
                )
            )
        if block_kind == "table_notes" and page_start != page_end:
            findings.append(
                _finding(
                    "TABLE_NOTES_SPLIT_ACROSS_PAGES",
                    "quality_debt",
                    "Table notes cross a page boundary",
                    "display_redesign",
                    block_id=block_id,
                    page_start=page_start,
                    page_end=page_end,
                )
            )
        if block_kind in {"heading", "section_heading", "section_title"}:
            next_index = index
            if next_index < len(blocks):
                next_block = blocks[next_index]
                next_page_start = next_block.get("page_start")
                if (
                    isinstance(next_page_start, int)
                    and not isinstance(next_page_start, bool)
                    and next_page_start > page_end
                ):
                    findings.append(
                        _finding(
                            "ORPHAN_SECTION_HEADING_AT_PAGE_END",
                            "quality_debt",
                            "A section heading is stranded at the end of a page without its next content block",
                            "display_redesign",
                            block_id=block_id,
                            page_start=page_start,
                            page_end=page_end,
                            next_block_id=str(
                                next_block.get("block_id") or f"block_{next_index + 1}"
                            ),
                        )
                    )
        panel_count = block.get("panel_count")
        title_text = str(
            block.get("title_text")
            or block.get("visible_title")
            or block.get("text")
            or ""
        )
        if (
            normalized[-1]["continuation"]
            and isinstance(panel_count, int)
            and not isinstance(panel_count, bool)
            and panel_count == 1
            and re.search(r"\bpanel\s+1\s+of\s+1\b", title_text, flags=re.I)
        ):
            findings.append(
                _finding(
                    "SINGLETON_PANEL_LABEL_IN_CONTINUATION_TITLE",
                    "quality_debt",
                    "A singleton panel must not carry a continuation title formatted as panel 1 of 1",
                    "display_redesign",
                    block_id=block_id,
                    panel_count=panel_count,
                )
            )

    reference_pages = {
        page
        for block in normalized
        if block["block_kind"] in {"references", "reference_list"}
        for page in range(block["page_start"], block["page_end"] + 1)
    }
    for block in normalized:
        if block["block_kind"] not in {
            "figure",
            "main_figure",
            "supplementary_figure",
        }:
            continue
        shared_pages = sorted(
            reference_pages
            & set(range(block["page_start"], block["page_end"] + 1))
        )
        if shared_pages:
            findings.append(
                _finding(
                    "DISPLAY_AND_REFERENCES_SHARE_PAGE",
                    "quality_debt",
                    "A figure and the reference list share a page",
                    "display_redesign",
                    block_id=block["block_id"],
                    pages=shared_pages,
                )
            )
    return findings


def validate_document_display_scope_coverage(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Audit exact composed-PDF evidence and per-member display scope closure."""

    findings: list[dict[str, Any]] = []
    requires_reader_pdf = candidate.get("requires_reader_pdf")
    if not isinstance(requires_reader_pdf, bool):
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_READER_PDF_TRIGGER_INVALID",
                "quality_debt",
                "Declare requires_reader_pdf explicitly",
                "display_redesign",
            )
        )
    elif requires_reader_pdf is not True:
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_READER_PDF_NOT_APPLICABLE",
                "quality_debt",
                "This validator only evaluates a reader-PDF-applicable candidate; use the upper preflight disposition for not-applicable cases",
                "display_redesign",
            )
        )

    exact_refs: dict[str, dict[str, object] | None] = {}
    for field in DOCUMENT_DISPLAY_REQUIRED_EXACT_REFS:
        exact_refs[field] = _document_scope_exact_ref(
            candidate.get(field), field, findings
        )
    composed_paper_ref = exact_refs["composed_paper_pdf_exact_ref"]
    if composed_paper_ref is not None and Path(
        str(composed_paper_ref["ref"])
    ).name.lower() != "paper.pdf":
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_COMPOSED_EXACT_REF_FILENAME_INVALID",
                "quality_debt",
                "composed_paper_pdf_exact_ref must identify paper.pdf",
                "display_redesign",
            )
        )

    page_evidence_fields = [
        field
        for field in DOCUMENT_DISPLAY_PAGE_EVIDENCE_REFS
        if candidate.get(field) is not None
    ]
    if not page_evidence_fields:
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_PAGE_EVIDENCE_MISSING",
                "quality_debt",
                "Bind page_render_evidence_ref or page_hash_evidence_candidate_ref; an audit inventory cannot replace page evidence",
                "display_redesign",
            )
        )
    for field in page_evidence_fields:
        exact_refs[field] = _document_scope_exact_ref(
            candidate.get(field), field, findings
        )

    supplement_applicable = candidate.get("supplement_applicable")
    if not isinstance(supplement_applicable, bool):
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_SUPPLEMENT_TRIGGER_INVALID",
                "quality_debt",
                "Declare whether a supplement is applicable",
                "display_redesign",
            )
        )
    elif not supplement_applicable and not str(
        candidate.get("supplement_not_applicable_reason") or ""
    ).strip():
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_SUPPLEMENT_REASON_MISSING",
                "quality_debt",
                "State why no supplement belongs in display scope",
                "display_redesign",
            )
        )

    expected_members = _expected_document_members(
        candidate.get("expected_display_members"), findings
    )

    snapshot_entries = _document_scope_inventory(
        candidate.get("snapshot_inventory"), "snapshot_inventory", findings
    )
    audit_entries = _document_scope_inventory(
        candidate.get("audit_inventory"), "audit_inventory", findings
    )
    snapshot_main = [entry for entry in snapshot_entries if _is_main_composed_pdf(entry)]
    audit_main = [entry for entry in audit_entries if _is_main_composed_pdf(entry)]
    if not snapshot_main:
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_PAPER_PDF_MISSING_FROM_SNAPSHOT",
                "quality_debt",
                "The immutable reviewer snapshot must include paper.pdf with role selected_layout_main_manuscript",
                "display_redesign",
            )
        )
    elif composed_paper_ref is not None and not any(
        _inventory_entry_matches_exact_ref(entry, composed_paper_ref)
        for entry in snapshot_main
    ):
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_PAPER_PDF_EXACT_REF_MISMATCH_IN_SNAPSHOT",
                "quality_debt",
                "The snapshot paper.pdf bytes must match composed_paper_pdf_exact_ref",
                "display_redesign",
            )
        )
    if not audit_main:
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_PAPER_PDF_MISSING_FROM_AUDIT",
                "quality_debt",
                "The programmatic/visual audit inventory must include paper.pdf with role selected_layout_main_manuscript",
                "display_redesign",
            )
        )
    elif composed_paper_ref is not None and not any(
        _inventory_entry_matches_exact_ref(entry, composed_paper_ref)
        for entry in audit_main
    ):
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_PAPER_PDF_EXACT_REF_MISMATCH_IN_AUDIT",
                "quality_debt",
                "The audited paper.pdf bytes must match composed_paper_pdf_exact_ref",
                "display_redesign",
            )
        )

    if supplement_applicable is True:
        snapshot_supplement = [
            entry for entry in snapshot_entries if _is_supplement_composed_pdf(entry)
        ]
        audit_supplement = [
            entry for entry in audit_entries if _is_supplement_composed_pdf(entry)
        ]
        if not snapshot_supplement:
            findings.append(
                _finding(
                    "DOCUMENT_DISPLAY_SUPPLEMENT_PDF_MISSING_FROM_SNAPSHOT",
                    "quality_debt",
                    "Include the composed supplementary PDF in the immutable snapshot",
                    "display_redesign",
                )
            )
        if not audit_supplement:
            findings.append(
                _finding(
                    "DOCUMENT_DISPLAY_SUPPLEMENT_PDF_MISSING_FROM_AUDIT",
                    "quality_debt",
                    "Include the composed supplementary PDF in the audit inventory",
                    "display_redesign",
                )
            )
        if snapshot_supplement and audit_supplement and not any(
            _same_inventory_member_bytes(snapshot_entry, audit_entry)
            for snapshot_entry in snapshot_supplement
            for audit_entry in audit_supplement
        ):
            findings.append(
                _finding(
                    "DOCUMENT_DISPLAY_SUPPLEMENT_PDF_IDENTITY_MISMATCH",
                    "quality_debt",
                    "The snapshot and audited paper_with_supplementary.pdf must identify the same member bytes",
                    "display_redesign",
                )
            )

    expected_identity = {
        (entry["member_id"], entry["role"]) for entry in expected_members
    }
    snapshot_identity = {
        (entry["member_id"], entry["role"]) for entry in snapshot_entries
    }
    audit_identity = {
        (entry["member_id"], entry["role"]) for entry in audit_entries
    }
    missing_snapshot_members = sorted(
        f"{member_id}:{role}"
        for member_id, role in expected_identity - snapshot_identity
    )
    missing_audit_members = sorted(
        f"{member_id}:{role}" for member_id, role in expected_identity - audit_identity
    )
    if missing_snapshot_members:
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_EXPECTED_MEMBER_MISSING_FROM_SNAPSHOT",
                "quality_debt",
                "Expected main figure/table members are absent from the immutable snapshot",
                "display_redesign",
                members=missing_snapshot_members,
            )
        )
    if missing_audit_members:
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_EXPECTED_MEMBER_MISSING_FROM_AUDIT",
                "quality_debt",
                "Expected main figure/table members are absent from the audit inventory",
                "display_redesign",
                members=missing_audit_members,
            )
        )
    if candidate.get("authority") is not False:
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_SCOPE_AUTHORITY_FORBIDDEN",
                "quality_debt",
                "Keep document scope coverage refs-only with authority=false",
                "owner_visual_audit_decision",
            )
        )
    findings.sort(key=lambda item: str(item["code"]))
    complete = not findings
    return {
        "surface_kind": "document_display_scope_coverage_ref",
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "missing_snapshot_members": missing_snapshot_members,
        "missing_audit_members": missing_audit_members,
        "bound_exact_ref_fields": sorted(
            field for field, value in exact_refs.items() if value is not None
        ),
        "findings": findings,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-display-qc",
            "reason": "document_display_scope_coverage_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def _document_scope_exact_ref(
    value: object,
    field: str,
    findings: list[dict[str, Any]],
) -> dict[str, object] | None:
    if not isinstance(value, Mapping) or set(value) != EXACT_REF_FIELDS:
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_REQUIRED_EXACT_REF_INVALID",
                "quality_debt",
                f"{field} must contain exactly kind, ref, size_bytes, and sha256",
                "display_redesign",
                field=field,
            )
        )
        return None
    kind = normalize_evidence_ref(value.get("kind"))
    ref = normalize_evidence_ref(value.get("ref"))
    size_bytes = value.get("size_bytes")
    digest = str(value.get("sha256") or "").strip().lower()
    if (
        not kind
        or not ref
        or isinstance(size_bytes, bool)
        or not isinstance(size_bytes, int)
        or size_bytes < 1
        or re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is None
    ):
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_REQUIRED_EXACT_REF_INVALID",
                "quality_debt",
                f"{field} must be a non-empty durable exact ref",
                "display_redesign",
                field=field,
            )
        )
        return None
    return {
        "kind": kind,
        "ref": ref,
        "size_bytes": size_bytes,
        "sha256": digest,
    }


def _expected_document_members(
    value: object,
    findings: list[dict[str, Any]],
) -> list[dict[str, str]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_EXPECTED_MEMBERS_INVALID",
                "quality_debt",
                "Represent expected main figures/tables as member_id and role rows",
                "display_redesign",
            )
        )
        return []
    members: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            findings.append(
                _finding(
                    "DOCUMENT_DISPLAY_EXPECTED_MEMBER_ROW_INVALID",
                    "quality_debt",
                    f"expected_display_members[{index}] must bind member_id and role",
                    "display_redesign",
                )
            )
            continue
        member_id = normalize_evidence_ref(item.get("member_id"))
        role = str(item.get("role") or "").strip().lower()
        identity = (member_id, role)
        if not member_id or not role:
            findings.append(
                _finding(
                    "DOCUMENT_DISPLAY_EXPECTED_MEMBER_ROW_INCOMPLETE",
                    "quality_debt",
                    f"expected_display_members[{index}] must bind member_id and role",
                    "display_redesign",
                )
            )
            continue
        if identity in seen:
            findings.append(
                _finding(
                    "DOCUMENT_DISPLAY_EXPECTED_MEMBER_DUPLICATE",
                    "quality_debt",
                    "Expected display member identities must be unique",
                    "display_redesign",
                    member_id=member_id,
                    role=role,
                )
            )
            continue
        seen.add(identity)
        members.append({"member_id": member_id, "role": role})
    return members


def _document_scope_inventory(
    value: object,
    field: str,
    findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        findings.append(
            _finding(
                "DOCUMENT_DISPLAY_INVENTORY_INVALID",
                "quality_debt",
                f"{field} must be a list of exact member rows",
                "display_redesign",
            )
        )
        return []
    entries: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            findings.append(
                _finding(
                    "DOCUMENT_DISPLAY_INVENTORY_ROW_INVALID",
                    "quality_debt",
                    f"{field}[{index}] must be an exact member row",
                    "display_redesign",
                )
            )
            continue
        member_id = normalize_evidence_ref(item.get("member_id"))
        role = str(item.get("role") or "").strip().lower()
        ref = normalize_evidence_ref(item.get("ref"))
        size_bytes = item.get("size_bytes")
        digest = str(item.get("sha256") or "").strip().lower()
        if (
            not member_id
            or not role
            or not ref
            or isinstance(size_bytes, bool)
            or not isinstance(size_bytes, int)
            or size_bytes < 1
            or re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is None
        ):
            findings.append(
                _finding(
                    "DOCUMENT_DISPLAY_INVENTORY_ROW_INCOMPLETE",
                    "quality_debt",
                    f"{field}[{index}] must bind member_id, role, ref, size_bytes, and sha256",
                    "display_redesign",
                )
            )
            continue
        identity = (member_id, role)
        if identity in seen:
            findings.append(
                _finding(
                    "DOCUMENT_DISPLAY_INVENTORY_MEMBER_DUPLICATE",
                    "quality_debt",
                    f"{field} contains a duplicate member identity",
                    "display_redesign",
                    member_id=member_id,
                    role=role,
                )
            )
            continue
        seen.add(identity)
        entries.append(
            {
                "member_id": member_id,
                "role": role,
                "ref": ref,
                "size_bytes": size_bytes,
                "sha256": digest,
            }
        )
    return entries


def _is_main_composed_pdf(entry: Mapping[str, object]) -> bool:
    role = entry.get("role", "")
    name = Path(str(entry.get("ref") or "")).name.lower()
    return role == "selected_layout_main_manuscript" and name == "paper.pdf"


def _is_supplement_composed_pdf(entry: Mapping[str, object]) -> bool:
    role = entry.get("role", "")
    name = Path(str(entry.get("ref") or "")).name.lower()
    return (
        role == "reader_combined_main_and_supplementary"
        and name == "paper_with_supplementary.pdf"
    )


def _inventory_entry_matches_exact_ref(
    entry: Mapping[str, object], exact_ref: Mapping[str, object]
) -> bool:
    return (
        entry.get("sha256") == exact_ref.get("sha256")
        and entry.get("size_bytes") == exact_ref.get("size_bytes")
        and Path(str(entry.get("ref") or "")).name.lower()
        == Path(str(exact_ref.get("ref") or "")).name.lower()
    )


def _same_inventory_member_bytes(
    left: Mapping[str, object], right: Mapping[str, object]
) -> bool:
    return (
        left.get("member_id") == right.get("member_id")
        and left.get("role") == right.get("role")
        and left.get("sha256") == right.get("sha256")
        and left.get("size_bytes") == right.get("size_bytes")
    )


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
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError("origin_reviewer_evidence_ref must be an exact-ref mapping or null")
    expected_fields = {"kind", "ref", "size_bytes", "sha256"}
    if set(value) != expected_fields:
        raise ValueError(
            "origin_reviewer_evidence_ref must contain exactly kind, ref, "
            "size_bytes, and sha256"
        )
    normalized_kind = normalize_evidence_ref(value.get("kind"))
    normalized_ref = normalize_evidence_ref(value.get("ref"))
    if not normalized_kind or not normalized_ref:
        raise ValueError("origin_reviewer_evidence_ref kind and ref must be non-empty")
    normalized_sha256 = _sha256_digest(
        value.get("sha256"), "origin_reviewer_evidence_ref.sha256"
    )
    size_bytes = value.get("size_bytes")
    if isinstance(size_bytes, bool) or not isinstance(size_bytes, int) or size_bytes < 0:
        raise ValueError(
            "origin_reviewer_evidence_ref.size_bytes must be a non-negative integer"
        )
    return {
        "kind": normalized_kind,
        "ref": normalized_ref,
        "size_bytes": size_bytes,
        "sha256": normalized_sha256,
    }


def build_page_hash_evidence_candidate(
    pages: Sequence[Mapping[str, object]],
    *,
    review_scope_sha256: object,
    rubric_sha256: object,
    origin_reviewer_evidence_ref: object = None,
) -> dict[str, Any]:
    """Build a refs-only domain evidence identity from fixed-raster page pixels."""

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
    evidence_ref = _origin_ref(origin_reviewer_evidence_ref)
    return {
        "surface_kind": PAGE_HASH_EVIDENCE_SURFACE_KIND,
        "schema_version": 3,
        "review_scope_sha256": scope_digest,
        "rubric_sha256": rubric_digest,
        "evidence_payload": {
            "raster_contract": dict(PAGE_HASH_RASTER_CONTRACT),
            "pages": normalized_pages,
        },
        "cache_key_sha256": f"sha256:{_canonical_json_sha256(key_payload)}",
        "origin_reviewer_evidence_ref": evidence_ref,
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


def _semantic_bbox(
    value: object, label: str
) -> tuple[float, float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise ValueError(f"{label} must contain four coordinates")
    x0, y0, x1, y1 = (
        _layout_number(item, f"{label}[{index}]") for index, item in enumerate(value)
    )
    if x1 < x0 or y1 < y0 or (x1 == x0 and y1 == y0):
        raise ValueError(f"{label} must describe a non-empty extent")
    return (x0, y0, x1, y1)


def _bbox_inside_tolerance(
    inner: tuple[float, float, float, float],
    outer: tuple[float, float, float, float],
    tolerance: float = 0.5,
) -> bool:
    return (
        inner[0] >= outer[0] - tolerance
        and inner[1] >= outer[1] - tolerance
        and inner[2] <= outer[2] + tolerance
        and inner[3] <= outer[3] + tolerance
    )


def _bboxes_close(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
    tolerance: float = 0.5,
) -> bool:
    return all(
        math.isclose(observed, expected, abs_tol=tolerance)
        for observed, expected in zip(first, second, strict=True)
    )


def _segment_bbox(
    segment: tuple[tuple[float, float], tuple[float, float]]
) -> tuple[float, float, float, float]:
    start, end = segment
    return (
        min(start[0], end[0]),
        min(start[1], end[1]),
        max(start[0], end[0]),
        max(start[1], end[1]),
    )


def _point_on_bbox_boundary(
    point: tuple[float, float],
    bbox: tuple[float, float, float, float],
    tolerance: float = 0.5,
) -> bool:
    x_value, y_value = point
    x0, y0, x1, y1 = bbox
    inside_extended = (
        x0 - tolerance <= x_value <= x1 + tolerance
        and y0 - tolerance <= y_value <= y1 + tolerance
    )
    on_edge = any(
        math.isclose(observed, edge, abs_tol=tolerance)
        for observed, edge in (
            (x_value, x0),
            (x_value, x1),
            (y_value, y0),
            (y_value, y1),
        )
    )
    return inside_extended and on_edge


def _semantic_segment(
    value: object, label: str
) -> tuple[tuple[float, float], tuple[float, float]]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{label} must be an array")
    if len(value) == 4:
        x0, y0, x1, y1 = (
            _layout_number(item, f"{label}[{index}]")
            for index, item in enumerate(value)
        )
    elif (
        len(value) == 2
        and all(isinstance(point, (list, tuple)) and len(point) == 2 for point in value)
    ):
        x0 = _layout_number(value[0][0], f"{label}[0][0]")
        y0 = _layout_number(value[0][1], f"{label}[0][1]")
        x1 = _layout_number(value[1][0], f"{label}[1][0]")
        y1 = _layout_number(value[1][1], f"{label}[1][1]")
    else:
        raise ValueError(f"{label} must contain four coordinates or two points")
    if math.isclose(x0, x1, abs_tol=1e-12) and math.isclose(
        y0, y1, abs_tol=1e-12
    ):
        raise ValueError(f"{label} must have non-zero length")
    return ((x0, y0), (x1, y1))


def _semantic_point(value: object, label: str) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{label} must contain two coordinates")
    return (
        _layout_number(value[0], f"{label}[0]"),
        _layout_number(value[1], f"{label}[1]"),
    )


def _points_close(
    first: tuple[float, float],
    second: tuple[float, float],
    tolerance: float = 1e-6,
) -> bool:
    return math.isclose(first[0], second[0], abs_tol=tolerance) and math.isclose(
        first[1], second[1], abs_tol=tolerance
    )


def _segments_share_endpoint(
    first: tuple[tuple[float, float], tuple[float, float]],
    second: tuple[tuple[float, float], tuple[float, float]],
) -> bool:
    return any(
        _points_close(first_point, second_point)
        for first_point in first
        for second_point in second
    )


def _segments_close(
    first: tuple[tuple[float, float], tuple[float, float]],
    second: tuple[tuple[float, float], tuple[float, float]],
    *,
    tolerance: float = 0.5,
) -> bool:
    return _points_close(first[0], second[0], tolerance) and _points_close(
        first[1], second[1], tolerance
    )


def _segment_orientation(
    first: tuple[float, float],
    second: tuple[float, float],
    third: tuple[float, float],
) -> float:
    return (second[0] - first[0]) * (third[1] - first[1]) - (
        second[1] - first[1]
    ) * (third[0] - first[0])


def _point_on_segment(
    point: tuple[float, float],
    segment: tuple[tuple[float, float], tuple[float, float]],
    tolerance: float = 1e-6,
) -> bool:
    start, end = segment
    return (
        abs(_segment_orientation(start, end, point)) <= tolerance
        and min(start[0], end[0]) - tolerance
        <= point[0]
        <= max(start[0], end[0]) + tolerance
        and min(start[1], end[1]) - tolerance
        <= point[1]
        <= max(start[1], end[1]) + tolerance
    )


def _segments_intersect(
    first: tuple[tuple[float, float], tuple[float, float]],
    second: tuple[tuple[float, float], tuple[float, float]],
    tolerance: float = 1e-6,
) -> bool:
    first_start, first_end = first
    second_start, second_end = second
    orientations = (
        _segment_orientation(first_start, first_end, second_start),
        _segment_orientation(first_start, first_end, second_end),
        _segment_orientation(second_start, second_end, first_start),
        _segment_orientation(second_start, second_end, first_end),
    )
    if (
        orientations[0] * orientations[1] < -(tolerance**2)
        and orientations[2] * orientations[3] < -(tolerance**2)
    ):
        return True
    return any(
        abs(orientation) <= tolerance and _point_on_segment(point, segment, tolerance)
        for orientation, point, segment in (
            (orientations[0], second_start, first),
            (orientations[1], second_end, first),
            (orientations[2], first_start, second),
            (orientations[3], first_end, second),
        )
    )


def _segment_intersects_bbox_interior(
    segment: tuple[tuple[float, float], tuple[float, float]],
    bbox: tuple[float, float, float, float],
    inset: float = 0.5,
) -> bool:
    x0, y0, x1, y1 = bbox
    if x1 - x0 <= 2 * inset or y1 - y0 <= 2 * inset:
        inset = 0.0
    left, bottom, right, top = x0 + inset, y0 + inset, x1 - inset, y1 - inset
    start, end = segment
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    lower, upper = 0.0, 1.0
    for p_value, q_value in (
        (-dx, start[0] - left),
        (dx, right - start[0]),
        (-dy, start[1] - bottom),
        (dy, top - start[1]),
    ):
        if abs(p_value) <= 1e-12:
            if q_value < 0:
                return False
            continue
        ratio = q_value / p_value
        if p_value < 0:
            lower = max(lower, ratio)
        else:
            upper = min(upper, ratio)
        if lower > upper:
            return False
    return lower <= upper


def _semantic_scope_text(value: object) -> str:
    if isinstance(value, Mapping):
        return " ".join(
            str(value.get(key) or "") for key in ("applicability", "archetype", "scope")
        ).strip()
    return str(value or "").strip()


def _audit_segmented_group_spans(
    flow_contract: Mapping[str, object],
    *,
    nodes: Mapping[str, Mapping[str, object]],
    relations: Mapping[str, Mapping[str, object]],
    connectors: Sequence[Mapping[str, object]],
    text_source_by_id: Mapping[str, str],
) -> dict[str, object]:
    """Validate non-arrow segmented bands against renderer-bound group geometry."""

    violations: list[dict[str, object]] = []
    segmented_relation_ids = {
        relation_id
        for relation_id, relation in relations.items()
        if relation.get("encoding") == "segmented_band"
    }
    spans_value = flow_contract.get("segmented_group_spans")
    if spans_value is None:
        spans: list[Mapping[str, object]] = []
    elif not isinstance(spans_value, list) or not all(
        isinstance(item, Mapping) for item in spans_value
    ):
        violations.append(
            _layout_violation("semantic_segmented_group_registry_invalid")
        )
        spans = []
    else:
        spans = list(spans_value)

    connectors_by_id = {
        str(connector.get("connector_id") or ""): connector
        for connector in connectors
        if str(connector.get("connector_id") or "")
    }
    connectors_by_relation: dict[str, list[Mapping[str, object]]] = {}
    for connector in connectors:
        relation_id = str(connector.get("relation_id") or "")
        connectors_by_relation.setdefault(relation_id, []).append(connector)

    observed_relation_ids: list[str] = []
    seen_group_ids: set[str] = set()
    seen_connector_ids: set[str] = set()
    child_group_owner: dict[str, str] = {}
    valid_span_count = 0
    for index, span in enumerate(spans):
        span_violation_count = len(violations)
        relation_id = str(span.get("relation_id") or "").strip()
        group_node_id = str(span.get("group_node_id") or "").strip()
        connector_id = str(span.get("connector_id") or "").strip()
        child_node_ids_value = span.get("child_node_ids")
        child_node_ids = (
            [str(item).strip() for item in child_node_ids_value]
            if isinstance(child_node_ids_value, list)
            else []
        )
        if (
            not relation_id
            or not group_node_id
            or not connector_id
            or len(child_node_ids) < 2
            or any(not item for item in child_node_ids)
            or len(set(child_node_ids)) != len(child_node_ids)
            or group_node_id in child_node_ids
        ):
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_record_invalid",
                    group_index=index,
                )
            )
            continue

        observed_relation_ids.append(relation_id)
        duplicate_identifiers: list[str] = []
        if group_node_id in seen_group_ids:
            duplicate_identifiers.append(group_node_id)
        if connector_id in seen_connector_ids:
            duplicate_identifiers.append(connector_id)
        for child_node_id in child_node_ids:
            prior_group = child_group_owner.get(child_node_id)
            if prior_group is not None and prior_group != group_node_id:
                duplicate_identifiers.append(child_node_id)
            child_group_owner[child_node_id] = group_node_id
        seen_group_ids.add(group_node_id)
        seen_connector_ids.add(connector_id)
        if duplicate_identifiers:
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_identifier_not_unique",
                    relation_id=relation_id,
                    duplicate_ids=sorted(set(duplicate_identifiers)),
                )
            )

        relation = relations.get(relation_id)
        if relation is None or relation_id not in segmented_relation_ids:
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_relation_invalid",
                    relation_id=relation_id,
                )
            )
            continue
        relation_destinations = list(relation.get("destination_node_ids") or [])
        if relation_destinations != child_node_ids:
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_relation_children_mismatch",
                    relation_id=relation_id,
                    relation_destination_node_ids=relation_destinations,
                    group_child_node_ids=child_node_ids,
                )
            )
        if (
            not str(span.get("width_encoding") or "").strip()
            or span.get("width_encoding") != relation.get("width_encoding")
        ):
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_width_encoding_mismatch",
                    relation_id=relation_id,
                )
            )

        group_node = nodes.get(group_node_id)
        child_nodes = [nodes.get(child_node_id) for child_node_id in child_node_ids]
        if group_node is None or any(child is None for child in child_nodes):
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_node_missing",
                    relation_id=relation_id,
                    group_node_id=group_node_id,
                    missing_child_node_ids=[
                        child_node_id
                        for child_node_id, child in zip(
                            child_node_ids, child_nodes, strict=True
                        )
                        if child is None
                    ],
                )
            )
            continue

        relation_connectors = connectors_by_relation.get(relation_id, [])
        connector = connectors_by_id.get(connector_id)
        if (
            len(relation_connectors) != 1
            or connector is None
            or relation_connectors[0].get("connector_id") != connector_id
            or connector.get("destination_node_id") != group_node_id
            or connector.get("source_node_id") != relation.get("source_node_id")
            or connector.get("arrow_bearing") is True
            or bool(connector.get("arrowhead_artist_ids"))
        ):
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_connector_invalid",
                    relation_id=relation_id,
                    connector_id=connector_id,
                    relation_connector_ids=[
                        str(item.get("connector_id") or "")
                        for item in relation_connectors
                    ],
                )
            )
            continue

        tolerance = float(connector.get("geometry_tolerance_px") or 0.5)
        group_bbox = tuple(group_node["bbox"])
        child_bboxes = [tuple(child["bbox"]) for child in child_nodes if child]
        sorted_children = sorted(
            zip(child_node_ids, child_bboxes, strict=True),
            key=lambda item: (item[1][0], item[1][2], item[0]),
        )
        if [item[0] for item in sorted_children] != child_node_ids:
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_child_order_invalid",
                    relation_id=relation_id,
                )
            )
        child_union = (
            min(bbox[0] for bbox in child_bboxes),
            min(bbox[1] for bbox in child_bboxes),
            max(bbox[2] for bbox in child_bboxes),
            max(bbox[3] for bbox in child_bboxes),
        )
        if not (
            math.isclose(group_bbox[0], child_union[0], abs_tol=tolerance)
            and math.isclose(group_bbox[2], child_union[2], abs_tol=tolerance)
        ):
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_span_mismatch",
                    relation_id=relation_id,
                    group_span_px=[group_bbox[0], group_bbox[2]],
                    child_union_span_px=[child_union[0], child_union[2]],
                    tolerance_px=tolerance,
                )
            )

        reference_y0 = child_bboxes[0][1]
        reference_y1 = child_bboxes[0][3]
        same_y_band = all(
            math.isclose(bbox[1], reference_y0, abs_tol=tolerance)
            and math.isclose(bbox[3], reference_y1, abs_tol=tolerance)
            for bbox in child_bboxes
        )
        contiguous = same_y_band and all(
            math.isclose(
                sorted_children[position][1][2],
                sorted_children[position + 1][1][0],
                abs_tol=tolerance,
            )
            for position in range(len(sorted_children) - 1)
        )
        if not contiguous:
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_children_not_contiguous",
                    relation_id=relation_id,
                    child_node_ids=child_node_ids,
                    tolerance_px=tolerance,
                )
            )
        if not math.isclose(group_bbox[1], reference_y1, abs_tol=tolerance):
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_header_not_adjacent",
                    relation_id=relation_id,
                    group_bottom_px=group_bbox[1],
                    child_top_px=reference_y1,
                    tolerance_px=tolerance,
                )
            )

        try:
            declared_group_bbox = _layout_bbox(
                span.get("group_header_bbox_px"),
                (
                    "semantic_flow_contract.segmented_group_spans"
                    f"[{index}].group_header_bbox_px"
                ),
            )
            declared_child_union = _layout_bbox(
                span.get("child_union_bbox_px"),
                (
                    "semantic_flow_contract.segmented_group_spans"
                    f"[{index}].child_union_bbox_px"
                ),
            )
        except ValueError as exc:
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_declared_geometry_invalid",
                    relation_id=relation_id,
                    reason=str(exc),
                )
            )
        else:
            if not (
                _bboxes_close(declared_group_bbox, group_bbox, tolerance)
                and _bboxes_close(declared_child_union, child_union, tolerance)
            ):
                violations.append(
                    _layout_violation(
                        "semantic_segmented_group_declared_geometry_mismatch",
                        relation_id=relation_id,
                        tolerance_px=tolerance,
                    )
                )

        orientation = str(span.get("orientation") or "")
        entry_edge = str(span.get("entry_edge") or "")
        perceptual_anchor = span.get("perceptual_anchor")
        if orientation != "horizontal":
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_orientation_invalid",
                    relation_id=relation_id,
                    orientation=orientation,
                )
            )
        if entry_edge != "top":
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_entry_edge_invalid",
                    relation_id=relation_id,
                    entry_edge=entry_edge,
                )
            )
        if not isinstance(perceptual_anchor, Mapping):
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_perceptual_anchor_invalid",
                    relation_id=relation_id,
                )
            )
            perceptual_anchor = {}
        if (
            perceptual_anchor.get("mode") != "labeled_full_span_header"
            or perceptual_anchor.get("anchor_position") != "midpoint"
        ):
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_perceptual_anchor_invalid",
                    relation_id=relation_id,
                    mode=perceptual_anchor.get("mode"),
                    anchor_position=perceptual_anchor.get("anchor_position"),
                )
            )

        group_label = str(span.get("group_label") or "")
        label_artist_id = str(
            perceptual_anchor.get("label_artist_id") or ""
        ).strip()
        group_text_artist_ids = list(group_node.get("text_artist_ids") or [])
        if not group_label.strip():
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_label_empty",
                    relation_id=relation_id,
                )
            )
        if (
            not label_artist_id
            or label_artist_id not in group_text_artist_ids
            or text_source_by_id.get(label_artist_id) != group_label
        ):
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_label_artist_invalid",
                    relation_id=relation_id,
                    label_artist_id=label_artist_id or None,
                )
            )

        segments = list(connector.get("segments") or [])
        if not segments:
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_connector_invalid",
                    relation_id=relation_id,
                    connector_id=connector_id,
                )
            )
            continue
        actual_terminal = tuple(segments[-1][1])
        expected_anchor = (
            (group_bbox[0] + group_bbox[2]) / 2,
            group_bbox[3],
        )
        try:
            declared_expected_anchor = _semantic_point(
                span.get("expected_group_anchor_px"),
                (
                    "semantic_flow_contract.segmented_group_spans"
                    f"[{index}].expected_group_anchor_px"
                ),
            )
            declared_actual_terminal = _semantic_point(
                span.get("actual_connector_terminal_px"),
                (
                    "semantic_flow_contract.segmented_group_spans"
                    f"[{index}].actual_connector_terminal_px"
                ),
            )
        except ValueError as exc:
            violations.append(
                _layout_violation(
                    "semantic_segmented_group_anchor_geometry_invalid",
                    relation_id=relation_id,
                    reason=str(exc),
                )
            )
        else:
            if not (
                _points_close(
                    actual_terminal, expected_anchor, tolerance=tolerance
                )
                and _points_close(
                    declared_expected_anchor,
                    expected_anchor,
                    tolerance=tolerance,
                )
                and _points_close(
                    declared_actual_terminal,
                    actual_terminal,
                    tolerance=tolerance,
                )
            ):
                violations.append(
                    _layout_violation(
                        "semantic_segmented_group_anchor_mismatch",
                        relation_id=relation_id,
                        expected_top_midpoint_px=list(expected_anchor),
                        actual_connector_terminal_px=list(actual_terminal),
                        tolerance_px=tolerance,
                    )
                )
        if len(violations) == span_violation_count:
            valid_span_count += 1

    if Counter(observed_relation_ids) != Counter(
        {relation_id: 1 for relation_id in segmented_relation_ids}
    ):
        violations.append(
            _layout_violation(
                "semantic_segmented_group_relation_set_mismatch",
                expected_relation_ids=sorted(segmented_relation_ids),
                observed_relation_ids=sorted(observed_relation_ids),
            )
        )
    return {
        "segmented_group_span_count": len(spans),
        "validated_segmented_group_span_count": valid_span_count,
        "violations": violations,
    }


def _audit_semantic_artist_registry(
    registry: Mapping[str, object],
    *,
    canvas_bbox: tuple[float, float, float, float],
    safe_bbox: tuple[float, float, float, float],
    panels: Sequence[Mapping[str, object]],
) -> dict[str, Any]:
    violations: list[dict[str, object]] = []
    scope_text = _semantic_scope_text(registry.get("semantic_artist_scope"))
    archetype = str(registry.get("figure_archetype") or "")
    combined_scope = f"{scope_text} {archetype}".lower()
    flow_declared = any(
        token in combined_scope for token in SEMANTIC_FLOW_ARCHETYPE_TOKENS
    )
    not_applicable = scope_text.lower().startswith("not_applicable")
    if flow_declared and not_applicable:
        violations.append(_layout_violation("semantic_artist_scope_conflict"))

    semantic_registry = registry.get("semantic_artist_registry")
    if not isinstance(semantic_registry, Mapping):
        if flow_declared:
            violations.append(_layout_violation("semantic_artist_registry_missing"))
        counts = Counter(str(item["code"]) for item in violations)
        passed = not violations
        return {
            "applicability": (
                "required_for_declared_flow_or_schematic"
                if flow_declared
                else (
                    "not_applicable"
                    if not_applicable
                    else "not_declared_non_flow"
                )
            ),
            "flow_contract_required": flow_declared,
            "registered_semantic_artist_count": 0,
            "expected_semantic_artist_kind_count": 0,
            "checks": {
                "semantic_artist_applicability_valid": passed,
                "semantic_artist_registry_complete": passed,
                "semantic_artist_kinds_complete": passed,
                "semantic_artists_inside_canvas": passed,
                "semantic_artists_inside_safe_inset": passed,
                "semantic_node_text_contained": passed,
                "semantic_contract_geometry_bound": passed,
                "semantic_lines_clear_of_text": passed,
                "semantic_lines_clear_of_unrelated_nodes": passed,
                "semantic_connectors_non_crossing": passed,
                "semantic_arrowheads_clear_of_text": passed,
                "semantic_relation_encoding_valid": passed,
                "semantic_arrow_budget_met": passed,
                "semantic_incoming_unambiguous": passed,
                "semantic_bracket_spans_exact": passed,
                "semantic_segmented_group_spans_exact": passed,
                "semantic_segmented_group_perceptual_anchors_valid": passed,
            },
            "violation_counts": dict(sorted(counts.items())),
            "violations": violations,
        }

    expected_prefixes_value = semantic_registry.get("expected_prefixes")
    expected_prefixes = (
        sorted(set(str(item) for item in expected_prefixes_value if str(item)))
        if isinstance(expected_prefixes_value, list)
        else []
    )
    if isinstance(expected_prefixes_value, list) and len(expected_prefixes) != len(
        expected_prefixes_value
    ):
        violations.append(
            _layout_violation("semantic_expected_prefixes_duplicate_or_invalid")
        )
    artists_value = semantic_registry.get("artists")
    bindings_value = semantic_registry.get("prefix_bindings")
    if not expected_prefixes:
        violations.append(_layout_violation("semantic_expected_prefixes_missing"))
    if not isinstance(artists_value, list) or not all(
        isinstance(item, Mapping) for item in artists_value
    ):
        violations.append(_layout_violation("semantic_artist_records_invalid"))
        artists_value = []
    if not isinstance(bindings_value, list) or not all(
        isinstance(item, Mapping) for item in bindings_value
    ):
        violations.append(_layout_violation("semantic_prefix_bindings_invalid"))
        bindings_value = []

    semantic_by_id: dict[str, dict[str, object]] = {}
    actual_by_prefix: dict[str, list[str]] = {
        prefix: [] for prefix in expected_prefixes
    }
    for index, artist in enumerate(artists_value):
        artist_id = str(artist.get("artist_id") or "").strip()
        owner_prefix = str(artist.get("owner_prefix") or "").strip()
        artist_kind = str(artist.get("artist_kind") or "").strip()
        if not artist_id or not owner_prefix or not artist_kind:
            violations.append(
                _layout_violation(
                    "semantic_artist_identity_invalid", artist_index=index
                )
            )
            continue
        if artist_id in semantic_by_id:
            violations.append(
                _layout_violation(
                    "duplicate_semantic_artist_id", artist_id=artist_id
                )
            )
            continue
        try:
            bbox = _semantic_bbox(
                artist.get("bbox_px"), f"semantic_artists.{artist_id}.bbox_px"
            )
        except ValueError as exc:
            violations.append(
                _layout_violation(
                    "semantic_artist_bbox_invalid",
                    artist_id=artist_id,
                    reason=str(exc),
                )
            )
            continue
        record = {
            "artist_id": artist_id,
            "owner_prefix": owner_prefix,
            "artist_kind": artist_kind,
            "bbox": bbox,
            "geometry_px": artist.get("geometry_px"),
        }
        semantic_by_id[artist_id] = record
        if owner_prefix not in actual_by_prefix or not (
            artist_id == owner_prefix or artist_id.startswith(f"{owner_prefix}.")
        ):
            violations.append(
                _layout_violation(
                    "semantic_artist_prefix_invalid",
                    artist_id=artist_id,
                    owner_prefix=owner_prefix,
                )
            )
        else:
            actual_by_prefix[owner_prefix].append(artist_id)
        if not _bbox_inside_tolerance(bbox, canvas_bbox):
            violations.append(
                _layout_violation(
                    "semantic_artist_canvas_overflow", artist_id=artist_id
                )
            )
        if not _bbox_inside_tolerance(bbox, safe_bbox):
            violations.append(
                _layout_violation(
                    "semantic_artist_safe_inset_violation", artist_id=artist_id
                )
            )

    declared_bindings: dict[str, list[str]] = {}
    for binding in bindings_value:
        prefix = str(binding.get("prefix") or "").strip()
        artist_ids = binding.get("artist_ids")
        if (
            not prefix
            or not isinstance(artist_ids, list)
            or not all(isinstance(item, str) and item for item in artist_ids)
            or prefix in declared_bindings
        ):
            violations.append(
                _layout_violation(
                    "semantic_prefix_binding_invalid", prefix=prefix or None
                )
            )
            continue
        declared_bindings[prefix] = sorted(artist_ids)
    for prefix in expected_prefixes:
        actual_ids = sorted(actual_by_prefix.get(prefix, []))
        if not actual_ids:
            violations.append(
                _layout_violation(
                    "semantic_artist_prefix_missing", artist_prefix=prefix
                )
            )
        if declared_bindings.get(prefix) != actual_ids:
            violations.append(
                _layout_violation(
                    "semantic_prefix_binding_stale",
                    artist_prefix=prefix,
                    declared_artist_ids=declared_bindings.get(prefix, []),
                    actual_artist_ids=actual_ids,
                )
            )
    for prefix in sorted(set(declared_bindings) - set(expected_prefixes)):
        violations.append(
            _layout_violation(
                "semantic_prefix_binding_unexpected", artist_prefix=prefix
            )
        )

    text_by_id: dict[str, tuple[float, float, float, float]] = {}
    text_source_by_id: dict[str, str] = {}
    for panel in panels:
        for artist in panel.get("text_artists") or []:
            if not isinstance(artist, Mapping):
                continue
            artist_id = str(artist.get("artist_id") or "").strip()
            if not artist_id:
                continue
            try:
                text_by_id[artist_id] = _layout_bbox(
                    artist.get("bbox_px"), f"text_artists.{artist_id}.bbox_px"
                )
                text_source_by_id[artist_id] = str(artist.get("source_text") or "")
            except ValueError:
                continue

    flow_contract = registry.get("semantic_flow_contract")
    if flow_declared and not isinstance(flow_contract, Mapping):
        violations.append(_layout_violation("semantic_flow_contract_missing"))
        flow_contract = {}
    elif not isinstance(flow_contract, Mapping):
        flow_contract = {}

    expected_kinds_value = flow_contract.get("expected_artist_kinds")
    expected_kinds = (
        sorted(set(str(item) for item in expected_kinds_value if str(item)))
        if isinstance(expected_kinds_value, list)
        else []
    )
    actual_kinds = {str(item["artist_kind"]) for item in semantic_by_id.values()}
    if flow_declared and not expected_kinds:
        violations.append(_layout_violation("semantic_expected_artist_kinds_missing"))
    missing_kinds = sorted(set(expected_kinds) - actual_kinds)
    if missing_kinds:
        violations.append(
            _layout_violation(
                "semantic_artist_kinds_missing", missing_artist_kinds=missing_kinds
            )
        )

    nodes_value = flow_contract.get("nodes")
    nodes: dict[str, dict[str, object]] = {}
    if flow_declared and (
        not isinstance(nodes_value, list)
        or not all(isinstance(item, Mapping) for item in nodes_value)
    ):
        violations.append(_layout_violation("semantic_flow_nodes_invalid"))
        nodes_value = []
    elif not isinstance(nodes_value, list):
        nodes_value = []
    for index, node in enumerate(nodes_value):
        node_id = str(node.get("node_id") or "").strip()
        if not node_id or node_id in nodes:
            violations.append(
                _layout_violation(
                    "semantic_flow_node_identity_invalid", node_index=index
                )
            )
            continue
        try:
            node_bbox = _layout_bbox(
                node.get("bbox_px"), f"semantic_flow.nodes.{node_id}.bbox_px"
            )
        except ValueError as exc:
            violations.append(
                _layout_violation(
                    "semantic_flow_node_bbox_invalid",
                    node_id=node_id,
                    reason=str(exc),
                )
            )
            continue
        text_ids = node.get("text_artist_ids")
        if not isinstance(text_ids, list) or not all(
            isinstance(item, str) and item for item in text_ids
        ):
            violations.append(
                _layout_violation(
                    "semantic_node_text_registry_invalid", node_id=node_id
                )
            )
            text_ids = []
        patch_artist_id = str(node.get("patch_artist_id") or "").strip()
        patch_artist = semantic_by_id.get(patch_artist_id)
        if not patch_artist_id or patch_artist is None:
            violations.append(
                _layout_violation(
                    "semantic_node_patch_artist_missing",
                    node_id=node_id,
                    patch_artist_id=patch_artist_id or None,
                )
            )
        elif not _bboxes_close(patch_artist["bbox"], node_bbox):
            violations.append(
                _layout_violation(
                    "semantic_node_patch_bbox_mismatch",
                    node_id=node_id,
                    patch_artist_id=patch_artist_id,
                    contract_bbox_px=list(node_bbox),
                    artist_bbox_px=list(patch_artist["bbox"]),
                )
            )
        nodes[node_id] = {
            "bbox": node_bbox,
            "text_artist_ids": list(text_ids),
            "patch_artist_id": patch_artist_id,
        }
        for text_id in text_ids:
            text_bbox = text_by_id.get(text_id)
            if text_bbox is None:
                violations.append(
                    _layout_violation(
                        "semantic_node_text_artist_missing",
                        node_id=node_id,
                        text_artist_id=text_id,
                    )
                )
            elif not _bbox_inside_tolerance(text_bbox, node_bbox):
                violations.append(
                    _layout_violation(
                        "semantic_node_text_outside_node",
                        node_id=node_id,
                        text_artist_id=text_id,
                    )
                )

    grammar_value = flow_contract.get("relation_encoding_grammar")
    grammar: dict[str, set[str]] = {}
    if flow_declared and not isinstance(grammar_value, Mapping):
        violations.append(_layout_violation("semantic_relation_grammar_missing"))
    elif isinstance(grammar_value, Mapping):
        for relation_kind, encodings in grammar_value.items():
            if not isinstance(encodings, list) or not all(
                isinstance(item, str) and item for item in encodings
            ):
                violations.append(
                    _layout_violation(
                        "semantic_relation_grammar_invalid",
                        relation=str(relation_kind),
                    )
                )
                continue
            grammar[str(relation_kind)] = set(encodings)

    relations_value = flow_contract.get("relations")
    relations: dict[str, dict[str, object]] = {}
    if flow_declared and (
        not isinstance(relations_value, list)
        or not all(isinstance(item, Mapping) for item in relations_value)
    ):
        violations.append(_layout_violation("semantic_flow_relations_invalid"))
        relations_value = []
    elif not isinstance(relations_value, list):
        relations_value = []
    for index, relation in enumerate(relations_value):
        relation_id = str(relation.get("relation_id") or "").strip()
        relation_kind = str(relation.get("relation") or "").strip()
        encoding = str(relation.get("encoding") or "").strip()
        if not relation_id or relation_id in relations or not relation_kind or not encoding:
            violations.append(
                _layout_violation(
                    "semantic_relation_identity_invalid", relation_index=index
                )
            )
            continue
        relations[relation_id] = {
            "relation": relation_kind,
            "encoding": encoding,
            "source_node_id": str(relation.get("source_node_id") or "").strip(),
            "source_node_ids": [
                str(item)
                for item in (relation.get("source_node_ids") or [])
                if isinstance(item, str) and item
            ],
            "destination_node_id": str(
                relation.get("destination_node_id") or ""
            ).strip(),
            "destination_node_ids": [
                str(item)
                for item in (relation.get("destination_node_ids") or [])
                if isinstance(item, str) and item
            ],
            "width_encoding": relation.get("width_encoding"),
        }
        if encoding not in grammar.get(relation_kind, set()):
            violations.append(
                _layout_violation(
                    "semantic_relation_encoding_invalid",
                    relation_id=relation_id,
                    relation=relation_kind,
                    encoding=encoding,
                )
            )
        prefixes = relation.get("artist_prefixes")
        if not isinstance(prefixes, list) or not prefixes:
            violations.append(
                _layout_violation(
                    "semantic_relation_artist_prefixes_missing",
                    relation_id=relation_id,
                )
            )
        else:
            for prefix in prefixes:
                if not actual_by_prefix.get(str(prefix)):
                    violations.append(
                        _layout_violation(
                            "semantic_relation_artist_prefix_missing",
                            relation_id=relation_id,
                            artist_prefix=str(prefix),
                        )
                    )

    connectors_value = flow_contract.get("connectors")
    connector_records: list[dict[str, object]] = []
    if flow_declared and (
        not isinstance(connectors_value, list)
        or not all(isinstance(item, Mapping) for item in connectors_value)
    ):
        violations.append(_layout_violation("semantic_flow_connectors_invalid"))
        connectors_value = []
    elif not isinstance(connectors_value, list):
        connectors_value = []
    connector_ids: set[str] = set()
    incoming: Counter[str] = Counter()
    for index, connector in enumerate(connectors_value):
        connector_id = str(connector.get("connector_id") or "").strip()
        relation_id = str(connector.get("relation_id") or "").strip()
        source_node_id = str(connector.get("source_node_id") or "").strip()
        destination_node_id = str(
            connector.get("destination_node_id") or ""
        ).strip()
        if not connector_id or connector_id in connector_ids:
            violations.append(
                _layout_violation(
                    "semantic_connector_identity_invalid", connector_index=index
                )
            )
            continue
        connector_ids.add(connector_id)
        if relation_id not in relations:
            violations.append(
                _layout_violation(
                    "semantic_connector_relation_missing",
                    connector_id=connector_id,
                    relation_id=relation_id,
                )
            )
        if source_node_id not in nodes or destination_node_id not in nodes:
            violations.append(
                _layout_violation(
                    "semantic_connector_node_missing",
                    connector_id=connector_id,
                    source_node_id=source_node_id,
                    destination_node_id=destination_node_id,
                )
            )
        segments_value = connector.get("segments_px")
        segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
        if not isinstance(segments_value, list) or not segments_value:
            violations.append(
                _layout_violation(
                    "semantic_connector_segments_missing", connector_id=connector_id
                )
            )
        else:
            for segment_index, segment_value in enumerate(segments_value):
                try:
                    segments.append(
                        _semantic_segment(
                            segment_value,
                            f"semantic_connectors.{connector_id}.segments_px[{segment_index}]",
                        )
                    )
                except ValueError as exc:
                    violations.append(
                        _layout_violation(
                            "semantic_connector_segment_invalid",
                            connector_id=connector_id,
                            segment_index=segment_index,
                            reason=str(exc),
                        )
                    )
        for segment_index in range(len(segments) - 1):
            if not _points_close(
                segments[segment_index][1], segments[segment_index + 1][0]
            ):
                violations.append(
                    _layout_violation(
                        "semantic_connector_segments_disconnected",
                        connector_id=connector_id,
                        first_segment_index=segment_index,
                        second_segment_index=segment_index + 1,
                    )
                )
        if segments and source_node_id in nodes and destination_node_id in nodes:
            if not _point_on_bbox_boundary(
                segments[0][0], nodes[source_node_id]["bbox"]
            ):
                violations.append(
                    _layout_violation(
                        "semantic_connector_source_not_anchored",
                        connector_id=connector_id,
                        source_node_id=source_node_id,
                    )
                )
            if not _point_on_bbox_boundary(
                segments[-1][1], nodes[destination_node_id]["bbox"]
            ):
                violations.append(
                    _layout_violation(
                        "semantic_connector_destination_not_anchored",
                        connector_id=connector_id,
                        destination_node_id=destination_node_id,
                    )
                )
        arrowhead_ids = connector.get("arrowhead_artist_ids")
        if not isinstance(arrowhead_ids, list) or not all(
            isinstance(item, str) and item for item in arrowhead_ids
        ):
            violations.append(
                _layout_violation(
                    "semantic_arrowhead_registry_invalid",
                    connector_id=connector_id,
                )
            )
            arrowhead_ids = []
        for arrowhead_id in arrowhead_ids:
            if arrowhead_id not in semantic_by_id:
                violations.append(
                    _layout_violation(
                        "semantic_arrowhead_artist_missing",
                        connector_id=connector_id,
                        arrowhead_artist_id=arrowhead_id,
                    )
                )
        segment_artist_ids = connector.get("segment_artist_ids")
        if (
            not isinstance(segment_artist_ids, list)
            or len(segment_artist_ids) != len(segments)
            or not all(isinstance(item, str) and item for item in segment_artist_ids)
        ):
            violations.append(
                _layout_violation(
                    "semantic_connector_geometry_registry_invalid",
                    connector_id=connector_id,
                )
            )
            segment_artist_ids = []
        geometry_tolerance = _layout_number(
            connector.get("geometry_tolerance_px", 0.5),
            f"semantic_connectors.{connector_id}.geometry_tolerance_px",
        )
        if geometry_tolerance < 0 or geometry_tolerance > 12:
            violations.append(
                _layout_violation(
                    "semantic_connector_geometry_tolerance_invalid",
                    connector_id=connector_id,
                    geometry_tolerance_px=geometry_tolerance,
                )
            )
        for segment_index, (segment, segment_artist_id) in enumerate(
            zip(segments, segment_artist_ids)
        ):
            segment_artist = semantic_by_id.get(segment_artist_id)
            if segment_artist is None:
                violations.append(
                    _layout_violation(
                        "semantic_connector_geometry_artist_missing",
                        connector_id=connector_id,
                        segment_index=segment_index,
                        segment_artist_id=segment_artist_id,
                    )
                )
                continue
            try:
                artist_segment = _semantic_segment(
                    segment_artist.get("geometry_px"),
                    (
                        "semantic_artists."
                        f"{segment_artist_id}.geometry_px"
                    ),
                )
            except ValueError as exc:
                violations.append(
                    _layout_violation(
                        "semantic_connector_artist_geometry_invalid",
                        connector_id=connector_id,
                        segment_index=segment_index,
                        segment_artist_id=segment_artist_id,
                        reason=str(exc),
                    )
                )
                continue
            expected_segment_bbox = _segment_bbox(segment)
            if not (
                _segments_close(
                    artist_segment,
                    segment,
                    tolerance=geometry_tolerance,
                )
                and _bboxes_close(
                    segment_artist["bbox"],
                    expected_segment_bbox,
                    tolerance=geometry_tolerance,
                )
            ):
                violations.append(
                    _layout_violation(
                        "semantic_connector_geometry_mismatch",
                        connector_id=connector_id,
                        segment_index=segment_index,
                        segment_artist_id=segment_artist_id,
                        contract_segment_px=[
                            *segment[0],
                            *segment[1],
                        ],
                        artist_segment_px=[
                            *artist_segment[0],
                            *artist_segment[1],
                        ],
                        contract_segment_bbox_px=list(expected_segment_bbox),
                        artist_bbox_px=list(segment_artist["bbox"]),
                        tolerance_px=geometry_tolerance,
                    )
                )
        incoming[destination_node_id] += 1
        connector_records.append(
            {
                "connector_id": connector_id,
                "relation_id": relation_id,
                "source_node_id": source_node_id,
                "destination_node_id": destination_node_id,
                "junction_group": str(connector.get("junction_group") or ""),
                "segments": segments,
                "segment_artist_ids": list(segment_artist_ids),
                "arrowhead_artist_ids": list(arrowhead_ids),
                "arrow_bearing": connector.get("arrow_bearing") is True
                or bool(arrowhead_ids),
                "geometry_tolerance_px": geometry_tolerance,
            }
        )

    arrow_encodings_value = flow_contract.get("arrow_encodings")
    arrow_encodings = (
        set(str(item) for item in arrow_encodings_value)
        if isinstance(arrow_encodings_value, list)
        else set()
    )
    connectors_by_relation = Counter(
        str(item["relation_id"]) for item in connector_records
    )
    for relation_id, relation in relations.items():
        is_arrow_encoding = relation["encoding"] in arrow_encodings
        connector_count = connectors_by_relation[relation_id]
        if is_arrow_encoding and connector_count == 0:
            violations.append(
                _layout_violation(
                    "semantic_arrow_relation_connector_missing",
                    relation_id=relation_id,
                )
            )
        if (
            not is_arrow_encoding
            and relation["encoding"] != "segmented_band"
            and connector_count > 0
        ):
            violations.append(
                _layout_violation(
                    "semantic_non_arrow_relation_has_connector",
                    relation_id=relation_id,
                )
            )

    segmented_group_audit = _audit_segmented_group_spans(
        flow_contract,
        nodes=nodes,
        relations=relations,
        connectors=connector_records,
        text_source_by_id=text_source_by_id,
    )
    violations.extend(segmented_group_audit["violations"])

    for connector in connector_records:
        for segment in connector["segments"]:
            for text_id, text_bbox in text_by_id.items():
                if _segment_intersects_bbox_interior(segment, text_bbox):
                    violations.append(
                        _layout_violation(
                            "semantic_line_text_intersection",
                            connector_id=connector["connector_id"],
                            text_artist_id=text_id,
                        )
                    )
            for node_id, node in nodes.items():
                if node_id in {
                    connector["source_node_id"],
                    connector["destination_node_id"],
                }:
                    continue
                if _segment_intersects_bbox_interior(segment, node["bbox"]):
                    violations.append(
                        _layout_violation(
                            "semantic_line_unrelated_node_intersection",
                            connector_id=connector["connector_id"],
                            node_id=node_id,
                        )
                    )
        for arrowhead_id in connector["arrowhead_artist_ids"]:
            arrowhead = semantic_by_id.get(str(arrowhead_id))
            if arrowhead is None:
                continue
            for text_id, text_bbox in text_by_id.items():
                if _bbox_overlap_area(arrowhead["bbox"], text_bbox) > 0:
                    violations.append(
                        _layout_violation(
                            "semantic_arrowhead_text_intersection",
                            connector_id=connector["connector_id"],
                            arrowhead_artist_id=arrowhead_id,
                            text_artist_id=text_id,
                        )
                    )

    allowed_crossings_value = flow_contract.get("allowed_connector_crossing_pairs")
    if allowed_crossings_value is not None and (
        not isinstance(allowed_crossings_value, list)
        or not all(
            isinstance(pair, list)
            and len(pair) == 2
            and all(isinstance(item, str) and item for item in pair)
            for pair in allowed_crossings_value
        )
    ):
        violations.append(_layout_violation("semantic_allowed_crossings_invalid"))
        allowed_crossings_value = []
    allowed_crossings = {
        tuple(sorted(str(item) for item in pair))
        for pair in (allowed_crossings_value or [])
        if isinstance(pair, list) and len(pair) == 2
    }
    shared_junction_relations_value = flow_contract.get(
        "shared_junction_relations", ["partition"]
    )
    shared_junction_relations = (
        set(str(item) for item in shared_junction_relations_value)
        if isinstance(shared_junction_relations_value, list)
        else {"partition"}
    )
    junction_groups: dict[str, list[dict[str, object]]] = {}
    for connector in connector_records:
        junction_group = str(connector["junction_group"])
        if junction_group:
            junction_groups.setdefault(junction_group, []).append(connector)
    for junction_group, grouped_connectors in sorted(junction_groups.items()):
        relation_ids = {
            str(connector["relation_id"]) for connector in grouped_connectors
        }
        source_node_ids = {
            str(connector["source_node_id"]) for connector in grouped_connectors
        }
        relation_kinds = {
            str(relations.get(relation_id, {}).get("relation") or "")
            for relation_id in relation_ids
        }
        metadata_valid = (
            len(relation_ids) == 1
            and len(source_node_ids) == 1
            and len(relation_kinds) == 1
            and relation_kinds.issubset(shared_junction_relations)
        )
        common_prefix_count = 0
        if metadata_valid and len(grouped_connectors) > 1:
            minimum_segment_count = min(
                len(connector["segments"]) for connector in grouped_connectors
            )
            for segment_index in range(minimum_segment_count):
                reference_segment = grouped_connectors[0]["segments"][segment_index]
                if all(
                    _segments_close(
                        connector["segments"][segment_index],
                        reference_segment,
                    )
                    for connector in grouped_connectors[1:]
                ):
                    common_prefix_count += 1
                else:
                    break
        geometry_valid = (
            common_prefix_count > 0
            and all(
                len(connector["segments"]) > common_prefix_count
                for connector in grouped_connectors
            )
        )
        if geometry_valid:
            junction_point = grouped_connectors[0]["segments"][
                common_prefix_count - 1
            ][1]
            geometry_valid = all(
                _points_close(
                    connector["segments"][common_prefix_count][0],
                    junction_point,
                )
                for connector in grouped_connectors
            )
        if not (metadata_valid and geometry_valid) and len(grouped_connectors) > 1:
            violations.append(
                _layout_violation(
                    "semantic_junction_group_invalid",
                    junction_group=junction_group,
                    relation_ids=sorted(relation_ids),
                    source_node_ids=sorted(source_node_ids),
                    relation_kinds=sorted(relation_kinds),
                    common_prefix_segment_count=common_prefix_count,
                )
            )
    for first, second in combinations(connector_records, 2):
        connector_pair = tuple(
            sorted((str(first["connector_id"]), str(second["connector_id"])))
        )
        if connector_pair in allowed_crossings:
            continue
        crossing_found = False
        for first_segment in first["segments"]:
            for second_segment in second["segments"]:
                if _segments_share_endpoint(first_segment, second_segment):
                    continue
                if _segments_intersect(first_segment, second_segment):
                    crossing_found = True
                    break
            if crossing_found:
                break
        if crossing_found:
            violations.append(
                _layout_violation(
                    "semantic_connector_crossing_unauthorized",
                    connector_ids=list(connector_pair),
                )
            )

    arrow_budget = flow_contract.get("arrow_budget")
    arrow_count = sum(1 for item in connector_records if item["arrow_bearing"])
    if (
        isinstance(arrow_budget, bool)
        or not isinstance(arrow_budget, int)
        or arrow_budget < 0
    ):
        if flow_declared:
            violations.append(_layout_violation("semantic_arrow_budget_invalid"))
        arrow_budget = None
    elif arrow_count > arrow_budget:
        violations.append(
            _layout_violation(
                "semantic_arrow_budget_exceeded",
                arrow_count=arrow_count,
                arrow_budget=arrow_budget,
            )
        )
    ambiguous_incoming = {
        node_id: count
        for node_id, count in sorted(incoming.items())
        if node_id and count > 1
    }
    if ambiguous_incoming:
        violations.append(
            _layout_violation(
                "semantic_ambiguous_incoming_connectors",
                node_counts=ambiguous_incoming,
            )
        )

    brackets_value = flow_contract.get("brackets")
    if flow_declared and not isinstance(brackets_value, list):
        violations.append(_layout_violation("semantic_bracket_registry_invalid"))
        brackets_value = []
    elif not isinstance(brackets_value, list):
        brackets_value = []
    span_tolerance = _layout_number(
        flow_contract.get("bracket_span_tolerance_px", 0.5),
        "semantic_flow_contract.bracket_span_tolerance_px",
    )
    if span_tolerance < 0 or span_tolerance > 5:
        violations.append(
            _layout_violation(
                "semantic_bracket_span_tolerance_invalid",
                tolerance_px=span_tolerance,
            )
        )
        span_tolerance = 0.5
    for index, bracket in enumerate(brackets_value):
        if not isinstance(bracket, Mapping):
            violations.append(
                _layout_violation(
                    "semantic_bracket_record_invalid", bracket_index=index
                )
            )
            continue
        bracket_id = str(bracket.get("bracket_id") or "").strip()
        relation_id = str(bracket.get("relation_id") or "").strip()
        artist_prefix = str(bracket.get("artist_prefix") or "").strip()
        covered_node_ids = bracket.get("covered_node_ids")
        observed_span = bracket.get("observed_span_px")
        segment_artist_ids = bracket.get("segment_artist_ids")
        if (
            not bracket_id
            or relation_id not in relations
            or "bracket" not in str(
                relations.get(relation_id, {}).get("encoding") or ""
            )
            or not actual_by_prefix.get(artist_prefix)
            or not isinstance(covered_node_ids, list)
            or not covered_node_ids
            or not isinstance(observed_span, (list, tuple))
            or len(observed_span) != 2
            or not isinstance(segment_artist_ids, list)
            or not segment_artist_ids
            or not all(
                isinstance(item, str) and item for item in segment_artist_ids
            )
        ):
            violations.append(
                _layout_violation(
                    "semantic_bracket_record_invalid", bracket_index=index
                )
            )
            continue
        covered_nodes = [nodes.get(str(node_id)) for node_id in covered_node_ids]
        if any(node is None for node in covered_nodes):
            violations.append(
                _layout_violation(
                    "semantic_bracket_node_missing",
                    bracket_id=bracket_id,
                    covered_node_ids=[str(item) for item in covered_node_ids],
                )
            )
            continue
        bracket_artists = [
            semantic_by_id.get(segment_artist_id)
            for segment_artist_id in segment_artist_ids
        ]
        if any(artist is None for artist in bracket_artists):
            violations.append(
                _layout_violation(
                    "semantic_bracket_artist_missing",
                    bracket_id=bracket_id,
                    segment_artist_ids=list(segment_artist_ids),
                )
            )
            continue
        bracket_segments = []
        for segment_artist_id, bracket_artist in zip(
            segment_artist_ids, bracket_artists, strict=True
        ):
            try:
                bracket_segments.append(
                    _semantic_segment(
                        bracket_artist.get("geometry_px"),
                        (
                            "semantic_artists."
                            f"{segment_artist_id}.geometry_px"
                        ),
                    )
                )
            except ValueError as exc:
                violations.append(
                    _layout_violation(
                        "semantic_bracket_geometry_invalid",
                        bracket_id=bracket_id,
                        segment_artist_id=segment_artist_id,
                        reason=str(exc),
                    )
                )
        if len(bracket_segments) != len(bracket_artists):
            continue
        expected_x0 = min(node["bbox"][0] for node in covered_nodes if node)
        expected_x1 = max(node["bbox"][2] for node in covered_nodes if node)
        registered_x0 = min(
            point[0] for segment in bracket_segments for point in segment
        )
        registered_x1 = max(
            point[0] for segment in bracket_segments for point in segment
        )
        observed_x0 = _layout_number(
            observed_span[0], f"semantic_brackets.{bracket_id}.observed_span_px[0]"
        )
        observed_x1 = _layout_number(
            observed_span[1], f"semantic_brackets.{bracket_id}.observed_span_px[1]"
        )
        if not (
            math.isclose(observed_x0, registered_x0, abs_tol=span_tolerance)
            and math.isclose(observed_x1, registered_x1, abs_tol=span_tolerance)
        ):
            violations.append(
                _layout_violation(
                    "semantic_bracket_observed_span_mismatch",
                    bracket_id=bracket_id,
                    observed_span_px=[observed_x0, observed_x1],
                    registered_artist_span_px=[registered_x0, registered_x1],
                    tolerance_px=span_tolerance,
                )
            )
        if not (
            math.isclose(observed_x0, expected_x0, abs_tol=span_tolerance)
            and math.isclose(observed_x1, expected_x1, abs_tol=span_tolerance)
        ):
            violations.append(
                _layout_violation(
                    "semantic_bracket_span_mismatch",
                    bracket_id=bracket_id,
                    observed_span_px=[observed_x0, observed_x1],
                    expected_span_px=[expected_x0, expected_x1],
                    tolerance_px=span_tolerance,
                )
            )

    violations.sort(
        key=lambda item: json.dumps(item, ensure_ascii=True, sort_keys=True)
    )
    counts = Counter(str(item["code"]) for item in violations)
    check_failures = {
        "semantic_artist_applicability_valid": {
            "semantic_artist_scope_conflict",
            "semantic_artist_registry_missing",
            "semantic_flow_contract_missing",
        },
        "semantic_artist_registry_complete": {
            "semantic_expected_prefixes_missing",
            "semantic_artist_records_invalid",
            "semantic_prefix_bindings_invalid",
            "semantic_artist_identity_invalid",
            "duplicate_semantic_artist_id",
            "semantic_artist_bbox_invalid",
            "semantic_artist_prefix_invalid",
            "semantic_expected_prefixes_duplicate_or_invalid",
            "semantic_artist_prefix_missing",
            "semantic_prefix_binding_stale",
            "semantic_prefix_binding_invalid",
            "semantic_prefix_binding_unexpected",
        },
        "semantic_artist_kinds_complete": {
            "semantic_expected_artist_kinds_missing",
            "semantic_artist_kinds_missing",
        },
        "semantic_artists_inside_canvas": {"semantic_artist_canvas_overflow"},
        "semantic_artists_inside_safe_inset": {
            "semantic_artist_safe_inset_violation"
        },
        "semantic_node_text_contained": {
            "semantic_flow_nodes_invalid",
            "semantic_flow_node_identity_invalid",
            "semantic_flow_node_bbox_invalid",
            "semantic_node_text_registry_invalid",
            "semantic_node_text_artist_missing",
            "semantic_node_text_outside_node",
        },
        "semantic_contract_geometry_bound": {
            "semantic_node_patch_artist_missing",
            "semantic_node_patch_bbox_mismatch",
            "semantic_connector_geometry_registry_invalid",
            "semantic_connector_geometry_tolerance_invalid",
            "semantic_connector_geometry_artist_missing",
            "semantic_connector_artist_geometry_invalid",
            "semantic_connector_geometry_mismatch",
            "semantic_connector_segments_disconnected",
            "semantic_connector_source_not_anchored",
            "semantic_connector_destination_not_anchored",
            "semantic_allowed_crossings_invalid",
            "semantic_junction_group_invalid",
            "semantic_bracket_artist_missing",
            "semantic_bracket_geometry_invalid",
            "semantic_bracket_observed_span_mismatch",
        },
        "semantic_lines_clear_of_text": {"semantic_line_text_intersection"},
        "semantic_lines_clear_of_unrelated_nodes": {
            "semantic_line_unrelated_node_intersection"
        },
        "semantic_connectors_non_crossing": {
            "semantic_connector_crossing_unauthorized"
        },
        "semantic_arrowheads_clear_of_text": {
            "semantic_arrowhead_text_intersection"
        },
        "semantic_relation_encoding_valid": {
            "semantic_relation_grammar_missing",
            "semantic_relation_grammar_invalid",
            "semantic_flow_relations_invalid",
            "semantic_relation_identity_invalid",
            "semantic_relation_encoding_invalid",
            "semantic_relation_artist_prefixes_missing",
            "semantic_relation_artist_prefix_missing",
            "semantic_flow_connectors_invalid",
            "semantic_connector_identity_invalid",
            "semantic_connector_relation_missing",
            "semantic_connector_node_missing",
            "semantic_connector_segments_missing",
            "semantic_connector_segment_invalid",
            "semantic_arrowhead_registry_invalid",
            "semantic_arrowhead_artist_missing",
            "semantic_arrow_relation_connector_missing",
            "semantic_non_arrow_relation_has_connector",
        },
        "semantic_arrow_budget_met": {
            "semantic_arrow_budget_invalid",
            "semantic_arrow_budget_exceeded",
        },
        "semantic_incoming_unambiguous": {
            "semantic_ambiguous_incoming_connectors"
        },
        "semantic_bracket_spans_exact": {
            "semantic_bracket_registry_invalid",
            "semantic_bracket_record_invalid",
            "semantic_bracket_node_missing",
            "semantic_bracket_span_tolerance_invalid",
            "semantic_bracket_span_mismatch",
        },
        "semantic_segmented_group_spans_exact": {
            "semantic_segmented_group_registry_invalid",
            "semantic_segmented_group_record_invalid",
            "semantic_segmented_group_identifier_not_unique",
            "semantic_segmented_group_relation_invalid",
            "semantic_segmented_group_relation_children_mismatch",
            "semantic_segmented_group_width_encoding_mismatch",
            "semantic_segmented_group_node_missing",
            "semantic_segmented_group_connector_invalid",
            "semantic_segmented_group_child_order_invalid",
            "semantic_segmented_group_span_mismatch",
            "semantic_segmented_group_children_not_contiguous",
            "semantic_segmented_group_header_not_adjacent",
            "semantic_segmented_group_declared_geometry_invalid",
            "semantic_segmented_group_declared_geometry_mismatch",
            "semantic_segmented_group_relation_set_mismatch",
        },
        "semantic_segmented_group_perceptual_anchors_valid": {
            "semantic_segmented_group_orientation_invalid",
            "semantic_segmented_group_entry_edge_invalid",
            "semantic_segmented_group_perceptual_anchor_invalid",
            "semantic_segmented_group_label_empty",
            "semantic_segmented_group_label_artist_invalid",
            "semantic_segmented_group_anchor_geometry_invalid",
            "semantic_segmented_group_anchor_mismatch",
        },
    }
    checks = {
        check_name: not any(counts[code] for code in failure_codes)
        for check_name, failure_codes in check_failures.items()
    }
    return {
        "applicability": (
            "required_for_declared_flow_or_schematic"
            if flow_declared
            else ("not_applicable" if not_applicable else "registered_non_flow")
        ),
        "flow_contract_required": flow_declared,
        "registered_semantic_artist_count": len(semantic_by_id),
        "expected_semantic_artist_kind_count": len(expected_kinds),
        "actual_semantic_artist_kinds": sorted(actual_kinds),
        "arrow_count": arrow_count,
        "arrow_budget": arrow_budget,
        "ambiguous_incoming_node_count": len(ambiguous_incoming),
        "segmented_group_span_count": segmented_group_audit[
            "segmented_group_span_count"
        ],
        "validated_segmented_group_span_count": segmented_group_audit[
            "validated_segmented_group_span_count"
        ],
        "checks": checks,
        "violation_counts": dict(sorted(counts.items())),
        "violations": violations,
    }


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


def generate_semantic_wrap(
    source_text: object,
    *,
    available_width_px: object,
    word_widths_px: Sequence[object],
    space_width_px: object,
) -> dict[str, Any]:
    """Wrap renderer-measured text at lexical boundaries without changing words."""

    source = str(source_text or "")
    if "\n" in source or "\r" in source:
        raise ValueError("source_text must not contain manual line breaks")
    normalized_source = re.sub(r"\s+", " ", source).strip()
    if not normalized_source:
        raise ValueError("source_text must contain text")
    words = normalized_source.split(" ")
    if isinstance(word_widths_px, (str, bytes)) or not isinstance(
        word_widths_px, Sequence
    ):
        raise ValueError("word_widths_px must be a sequence")
    if len(word_widths_px) != len(words):
        raise ValueError("word_widths_px must contain one width per source word")

    available_width = _layout_number(available_width_px, "available_width_px")
    space_width = _layout_number(space_width_px, "space_width_px")
    if available_width <= 0:
        raise ValueError("available_width_px must be positive")
    if space_width < 0:
        raise ValueError("space_width_px must be non-negative")
    word_widths = [
        _layout_number(value, f"word_widths_px[{index}]")
        for index, value in enumerate(word_widths_px)
    ]
    if any(width <= 0 for width in word_widths):
        raise ValueError("word_widths_px values must be positive")
    if any(width > available_width for width in word_widths):
        raise ValueError("a source word exceeds the available width")

    lines: list[list[str]] = []
    line_widths: list[float] = []
    current_words: list[str] = []
    current_width = 0.0
    for word, word_width in zip(words, word_widths, strict=True):
        candidate_width = (
            word_width
            if not current_words
            else current_width + space_width + word_width
        )
        if current_words and candidate_width > available_width:
            lines.append(current_words)
            line_widths.append(current_width)
            current_words = [word]
            current_width = word_width
        else:
            current_words.append(word)
            current_width = candidate_width
    lines.append(current_words)
    line_widths.append(current_width)

    break_after_word_indices: list[int] = []
    consumed_words = 0
    for line in lines[:-1]:
        consumed_words += len(line)
        break_after_word_indices.append(consumed_words - 1)
    measured_unwrapped_width = sum(word_widths) + space_width * (len(words) - 1)
    return {
        "algorithm": SEMANTIC_WRAP_ALGORITHM,
        "break_strategy": "lexical_word_boundary",
        "source_text": normalized_source,
        "rendered_text": "\n".join(" ".join(line) for line in lines),
        "line_count": len(lines),
        "break_after_word_indices": break_after_word_indices,
        "line_widths_px": line_widths,
        "measured_unwrapped_width_px": measured_unwrapped_width,
    }


def _layout_number_sequence_matches(
    actual: object, expected: Sequence[float], label: str
) -> bool:
    if isinstance(actual, (str, bytes)) or not isinstance(actual, Sequence):
        return False
    if len(actual) != len(expected):
        return False
    try:
        actual_numbers = [
            _layout_number(value, f"{label}[{index}]")
            for index, value in enumerate(actual)
        ]
    except ValueError:
        return False
    return all(
        math.isclose(observed, wanted, rel_tol=0.0, abs_tol=1e-6)
        for observed, wanted in zip(actual_numbers, expected, strict=True)
    )


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
                    rendered_text = artist.get("rendered_text")
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
                    semantic_wrap = measurement.get("semantic_wrap")
                    generated_wrap: dict[str, Any] | None = None
                    if not isinstance(semantic_wrap, Mapping):
                        violations.append(
                            _layout_violation(
                                "semantic_wrap_provenance_missing",
                                panel_id=panel_id,
                                artist_id=artist_id,
                            )
                        )
                    elif semantic_wrap.get("algorithm") != SEMANTIC_WRAP_ALGORITHM:
                        violations.append(
                            _layout_violation(
                                "semantic_wrap_algorithm_invalid",
                                panel_id=panel_id,
                                artist_id=artist_id,
                            )
                        )
                    else:
                        try:
                            generated_wrap = generate_semantic_wrap(
                                source_text,
                                available_width_px=available_width,
                                word_widths_px=semantic_wrap.get("word_widths_px"),
                                space_width_px=semantic_wrap.get("space_width_px"),
                            )
                        except ValueError as exc:
                            violations.append(
                                _layout_violation(
                                    "semantic_wrap_generation_invalid",
                                    panel_id=panel_id,
                                    artist_id=artist_id,
                                    reason=str(exc),
                                )
                            )
                        else:
                            if rendered_text != generated_wrap["rendered_text"]:
                                violations.append(
                                    _layout_violation(
                                        "semantic_wrap_rendered_text_mismatch",
                                        panel_id=panel_id,
                                        artist_id=artist_id,
                                    )
                                )
                            if (
                                isinstance(line_count, bool)
                                or not isinstance(line_count, int)
                                or line_count != generated_wrap["line_count"]
                            ):
                                violations.append(
                                    _layout_violation(
                                        "semantic_wrap_line_count_mismatch",
                                        panel_id=panel_id,
                                        artist_id=artist_id,
                                    )
                                )
                            if semantic_wrap.get(
                                "break_after_word_indices"
                            ) != generated_wrap["break_after_word_indices"]:
                                violations.append(
                                    _layout_violation(
                                        "semantic_wrap_break_positions_mismatch",
                                        panel_id=panel_id,
                                        artist_id=artist_id,
                                    )
                                )
                            if not _layout_number_sequence_matches(
                                semantic_wrap.get("line_widths_px"),
                                generated_wrap["line_widths_px"],
                                f"{artist_id}.line_widths_px",
                            ):
                                violations.append(
                                    _layout_violation(
                                        "semantic_wrap_line_widths_mismatch",
                                        panel_id=panel_id,
                                        artist_id=artist_id,
                                    )
                                )
                            if not math.isclose(
                                measured_width,
                                generated_wrap["measured_unwrapped_width_px"],
                                rel_tol=0.0,
                                abs_tol=1e-6,
                            ):
                                violations.append(
                                    _layout_violation(
                                        "semantic_wrap_unwrapped_width_mismatch",
                                        panel_id=panel_id,
                                        artist_id=artist_id,
                                    )
                                )
                    if measured_width > available_width and (
                        generated_wrap is None
                        or generated_wrap["line_count"] < 2
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

    semantic_audit = _audit_semantic_artist_registry(
        registry,
        canvas_bbox=canvas_bbox,
        safe_bbox=safe_bbox,
        panels=panels,
    )
    violations.extend(semantic_audit["violations"])

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
                "semantic_wrap_provenance_missing",
                "semantic_wrap_algorithm_invalid",
                "semantic_wrap_generation_invalid",
                "semantic_wrap_rendered_text_mismatch",
                "semantic_wrap_line_count_mismatch",
                "semantic_wrap_break_positions_mismatch",
                "semantic_wrap_line_widths_mismatch",
                "semantic_wrap_unwrapped_width_mismatch",
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
    checks.update(semantic_audit["checks"])
    return {
        "surface_kind": "layout_bbox_registry_audit_candidate.v1",
        "registry_sha256": _canonical_json_sha256(registry),
        "machine_check_status": (
            "geometry_checks_passed" if not violations else "geometry_checks_failed"
        ),
        "panel_count": len(panels),
        "registered_text_artist_count": registered_artist_count,
        "semantic_artist_applicability": semantic_audit["applicability"],
        "semantic_flow_contract_required": semantic_audit[
            "flow_contract_required"
        ],
        "registered_semantic_artist_count": semantic_audit[
            "registered_semantic_artist_count"
        ],
        "expected_semantic_artist_kind_count": semantic_audit[
            "expected_semantic_artist_kind_count"
        ],
        "actual_semantic_artist_kinds": semantic_audit.get(
            "actual_semantic_artist_kinds", []
        ),
        "semantic_arrow_count": semantic_audit.get("arrow_count", 0),
        "semantic_arrow_budget": semantic_audit.get("arrow_budget"),
        "semantic_ambiguous_incoming_node_count": semantic_audit.get(
            "ambiguous_incoming_node_count", 0
        ),
        "semantic_segmented_group_span_count": semantic_audit.get(
            "segmented_group_span_count", 0
        ),
        "semantic_validated_segmented_group_span_count": semantic_audit.get(
            "validated_segmented_group_span_count", 0
        ),
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
        "semantic_artist_scope": registry.get(
            "semantic_artist_scope", "not_declared_non_flow"
        ),
        "bbox_registry_summary": {
            "panel_count": layout_audit["panel_count"],
            "registered_text_artist_count": layout_audit[
                "registered_text_artist_count"
            ],
            "semantic_artist_applicability": layout_audit[
                "semantic_artist_applicability"
            ],
            "registered_semantic_artist_count": layout_audit[
                "registered_semantic_artist_count"
            ],
            "expected_semantic_artist_kind_count": layout_audit[
                "expected_semantic_artist_kind_count"
            ],
            "actual_semantic_artist_kinds": layout_audit[
                "actual_semantic_artist_kinds"
            ],
        },
        "semantic_flow_summary": {
            "flow_contract_required": layout_audit[
                "semantic_flow_contract_required"
            ],
            "arrow_count": layout_audit["semantic_arrow_count"],
            "arrow_budget": layout_audit["semantic_arrow_budget"],
            "ambiguous_incoming_node_count": layout_audit[
                "semantic_ambiguous_incoming_node_count"
            ],
            "segmented_group_span_count": layout_audit[
                "semantic_segmented_group_span_count"
            ],
            "validated_segmented_group_span_count": layout_audit[
                "semantic_validated_segmented_group_span_count"
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
    digest = "sha256:" + "a" * 64
    def render_exact_ref(artifact_format: str) -> dict[str, object]:
        return {
            "kind": f"final_{artifact_format}_export",
            "ref": f"artifact://figure-1.{artifact_format}",
            "size_bytes": 100,
            "sha256": digest,
        }

    render_integrity_candidate = {
        "font_locks": [
            {"font_file_ref": "font://source-sans", "font_file_sha256": digest}
        ],
        "renderer_lock": {
            "family": "matplotlib",
            "version": "3.x",
            "headless_backend": "Agg",
        },
        "renderer_draw_complete": True,
        "artist_scope": "all_text_artists",
        "single_generation_source_ref": "source://figure-1",
        "paired_exports": [
            {
                "format": artifact_format,
                "artifact_ref": render_exact_ref(artifact_format),
                "visible_payload_sha256": digest,
                "labels_sha256": digest,
                "panel_order_sha256": digest,
                "source_fingerprint": digest,
                "dimensions": {
                    "width": 1800 if artifact_format == "png" else 432,
                    "height": 900 if artifact_format == "png" else 216,
                    "unit": "px" if artifact_format == "png" else "pt",
                },
                "crop_bounds": {
                    "coordinates": (
                        [0, 0, 1800, 900]
                        if artifact_format == "png"
                        else [0, 0, 432, 216]
                    ),
                    "unit": "px" if artifact_format == "png" else "pt",
                },
                "resolution_per_inch": 300 if artifact_format == "png" else None,
                "physical_dimensions_inches": [6, 3],
                "normalized_crop_bounds": [0, 0, 1, 1],
            }
            for artifact_format in ("png", "pdf")
        ],
        "final_scale_visual_note": "Both exports were inspected at final manuscript scale.",
        "authority": False,
    }
    render_integrity = validate_display_render_integrity(render_integrity_candidate)
    assert render_integrity["machine_check_status"] == "candidate_complete"
    payload_tamper = json.loads(json.dumps(render_integrity_candidate))
    payload_tamper["paired_exports"][1]["visible_payload_sha256"] = (
        "sha256:" + "b" * 64
    )
    payload_tamper_audit = validate_display_render_integrity(payload_tamper)
    assert "display_paired_export_parity_mismatch" in {
        item["code"] for item in payload_tamper_audit["findings"]
    }
    malformed_artifact_ref = json.loads(json.dumps(render_integrity_candidate))
    malformed_artifact_ref["paired_exports"][0]["artifact_ref"].pop("size_bytes")
    assert "display_paired_export_exact_ref_invalid" in {
        item["code"]
        for item in validate_display_render_integrity(malformed_artifact_ref)[
            "findings"
        ]
    }
    nonfinite_crop = json.loads(json.dumps(render_integrity_candidate))
    nonfinite_crop["paired_exports"][0]["crop_bounds"]["coordinates"][2] = float("inf")
    assert "display_paired_export_crop_invalid" in {
        item["code"]
        for item in validate_display_render_integrity(nonfinite_crop)["findings"]
    }
    physical_mismatch = json.loads(json.dumps(render_integrity_candidate))
    physical_mismatch["paired_exports"][1]["physical_dimensions_inches"] = [5, 3]
    assert "display_paired_export_parity_mismatch" in {
        item["code"]
        for item in validate_display_render_integrity(physical_mismatch)["findings"]
    }
    unit_mismatch = json.loads(json.dumps(render_integrity_candidate))
    unit_mismatch["paired_exports"][1]["dimensions"]["unit"] = "px"
    assert "display_paired_export_dimensions_invalid" in {
        item["code"]
        for item in validate_display_render_integrity(unit_mismatch)["findings"]
    }
    missing_visual_note = dict(render_integrity_candidate, final_scale_visual_note="")
    assert "display_final_scale_visual_note_missing" in {
        item["code"]
        for item in validate_display_render_integrity(missing_visual_note)["findings"]
    }
    assert normalize_evidence_ref("  fig:1 ;") == "fig:1"
    row = display_artifact_row("artifact:pdf", page_ref=" page 2 ", panel_ref="A")
    assert row["writes_authority"] is False
    skeleton = display_qc_skeleton("artifact:pdf")
    assert "display_qc_support_map_ref" in skeleton["required_refs"]
    assert "programmatic_figure_audit_ref" in skeleton["required_refs"]
    assert "display_render_integrity_ref" in skeleton["required_refs"]
    assert skeleton["authority"]["can_sign_visual_audit_receipt"] is False
    assert classify_display_qc_route("blank exported panel")["route"] == "artifact_owner_repair"
    support = display_qc_support_map([{"artifact_ref": "fig:1", "issue": "caption drift"}])
    assert support[0]["route_back_candidate"] == "caption_numbering_repair"
    assert lint_forbidden_display_qc_claims("publication-ready with owner receipt")
    layout_findings = lint_document_layout_inventory(
        [
            {
                "block_id": "F2-legend",
                "block_kind": "figure_legend",
                "document_role": "main_document",
                "artifact_role": "main_figure",
                "page_start": 22,
                "page_end": 23,
            },
            {
                "block_id": "S1",
                "block_kind": "supplementary_figure",
                "document_role": "main_document",
                "artifact_role": "supplementary_figure",
                "page_start": 25,
                "page_end": 25,
            },
            {
                "block_id": "references",
                "block_kind": "references",
                "document_role": "main_document",
                "artifact_role": "references",
                "page_start": 25,
                "page_end": 26,
            },
            {
                "block_id": "discussion-heading",
                "block_kind": "section_heading",
                "document_role": "main_document",
                "artifact_role": "section_heading",
                "page_start": 30,
                "page_end": 30,
                "text": "Discussion",
            },
            {
                "block_id": "discussion-body",
                "block_kind": "paragraph",
                "document_role": "main_document",
                "artifact_role": "text",
                "page_start": 31,
                "page_end": 31,
            },
            {
                "block_id": "ts25-continuation-title",
                "block_kind": "continuation_title",
                "document_role": "supplement",
                "artifact_role": "supplementary_table",
                "page_start": 32,
                "page_end": 32,
                "panel_count": 1,
                "title_text": "TS25, panel 1 of 1",
            },
        ]
    )
    assert {item["code"] for item in layout_findings} == {
        "FIGURE_LEGEND_SPLIT_ACROSS_PAGES",
        "SUPPLEMENTARY_DISPLAY_IN_MAIN_DOCUMENT",
        "DISPLAY_AND_REFERENCES_SHARE_PAGE",
        "ORPHAN_SECTION_HEADING_AT_PAGE_END",
        "SINGLETON_PANEL_LABEL_IN_CONTINUATION_TITLE",
    }
    assert all(item["writes_authority"] is False for item in layout_findings)
    def exact_ref(kind: str, ref: str, digest: str, size_bytes: int = 100) -> dict[str, object]:
        return {
            "kind": kind,
            "ref": ref,
            "size_bytes": size_bytes,
            "sha256": f"sha256:{digest * 64}",
        }

    def inventory_member(
        member_id: str,
        role: str,
        ref: str,
        digest: str,
        size_bytes: int = 100,
    ) -> dict[str, object]:
        return {
            "member_id": member_id,
            "role": role,
            "ref": ref,
            "size_bytes": size_bytes,
            "sha256": f"sha256:{digest * 64}",
        }

    valid_document_candidate = {
        "requires_reader_pdf": True,
        "canonical_manuscript_ref": exact_ref(
            "canonical_manuscript", "manuscript/paper.md", "1"
        ),
        "table_catalog_ref": exact_ref("table_catalog", "tables/catalog.json", "2"),
        "figure_catalog_ref": exact_ref(
            "figure_catalog", "figures/catalog.json", "3"
        ),
        "caption_legend_manifest_ref": exact_ref(
            "caption_legend_manifest", "manuscript/captions.json", "4"
        ),
        "render_environment_ref": exact_ref(
            "render_environment", "render/environment.json", "5"
        ),
        "font_inventory_ref": exact_ref(
            "font_inventory", "render/fonts.json", "6"
        ),
        "composed_paper_pdf_exact_ref": exact_ref(
            "composed_paper_pdf", "publication/paper.pdf", "7", 700
        ),
        "page_render_evidence_ref": exact_ref(
            "page_render_evidence", "audit/pages.json", "8"
        ),
        "supplement_applicable": True,
        "supplement_not_applicable_reason": None,
        "expected_display_members": [
            {"member_id": "figure-1", "role": "main_figure"},
            {"member_id": "figure-2", "role": "main_figure"},
            {"member_id": "table-1", "role": "main_table"},
        ],
        "snapshot_inventory": [
            inventory_member(
                "paper-main",
                "selected_layout_main_manuscript",
                "publication/paper.pdf",
                "7",
                700,
            ),
            inventory_member(
                "paper-combined",
                "reader_combined_main_and_supplementary",
                "publication/paper_with_supplementary.pdf",
                "9",
                900,
            ),
            inventory_member("figure-1", "main_figure", "figures/F1.pdf", "a"),
            inventory_member("figure-2", "main_figure", "figures/F2.pdf", "b"),
            inventory_member("table-1", "main_table", "tables/T1.docx", "c"),
        ],
        "audit_inventory": [
            inventory_member(
                "paper-main",
                "selected_layout_main_manuscript",
                "audit/paper.pdf",
                "7",
                700,
            ),
            inventory_member(
                "paper-combined",
                "reader_combined_main_and_supplementary",
                "audit/paper_with_supplementary.pdf",
                "9",
                900,
            ),
            inventory_member("figure-1", "main_figure", "audit/F1.png", "d"),
            inventory_member("figure-2", "main_figure", "audit/F2.png", "e"),
            inventory_member("table-1", "main_table", "audit/T1.png", "f"),
        ],
        "authority": False,
    }
    valid_document_scope = validate_document_display_scope_coverage(
        valid_document_candidate
    )
    assert valid_document_scope["machine_check_status"] == "candidate_complete"

    missing_members_candidate = json.loads(json.dumps(valid_document_candidate))
    missing_members_candidate["snapshot_inventory"] = [
        entry
        for entry in missing_members_candidate["snapshot_inventory"]
        if entry["member_id"] != "figure-2"
    ]
    missing_members_candidate["audit_inventory"] = [
        entry
        for entry in missing_members_candidate["audit_inventory"]
        if entry["member_id"] != "table-1"
    ]
    missing_members = validate_document_display_scope_coverage(
        missing_members_candidate
    )
    assert missing_members["missing_snapshot_members"] == ["figure-2:main_figure"]
    assert missing_members["missing_audit_members"] == ["table-1:main_table"]
    assert {item["code"] for item in missing_members["findings"]} >= {
        "DOCUMENT_DISPLAY_EXPECTED_MEMBER_MISSING_FROM_SNAPSHOT",
        "DOCUMENT_DISPLAY_EXPECTED_MEMBER_MISSING_FROM_AUDIT",
    }

    invalid_pdf_pair_candidate = json.loads(json.dumps(valid_document_candidate))
    invalid_pdf_pair_candidate["snapshot_inventory"][0]["role"] = "main_composed_pdf"
    invalid_pdf_pair_candidate["audit_inventory"][0]["ref"] = "audit/manuscript.pdf"
    invalid_pdf_pair = validate_document_display_scope_coverage(
        invalid_pdf_pair_candidate
    )
    assert {item["code"] for item in invalid_pdf_pair["findings"]} >= {
        "DOCUMENT_DISPLAY_PAPER_PDF_MISSING_FROM_SNAPSHOT",
        "DOCUMENT_DISPLAY_PAPER_PDF_MISSING_FROM_AUDIT",
    }

    missing_durable_refs_candidate = json.loads(json.dumps(valid_document_candidate))
    missing_durable_refs_candidate.pop("font_inventory_ref")
    missing_durable_refs_candidate.pop("page_render_evidence_ref")
    missing_durable_refs_candidate["audit_inventory"].append(
        inventory_member(
            "page-audit", "page_render_evidence", "audit/pages.json", "8"
        )
    )
    missing_durable_refs = validate_document_display_scope_coverage(
        missing_durable_refs_candidate
    )
    assert {item["code"] for item in missing_durable_refs["findings"]} >= {
        "DOCUMENT_DISPLAY_REQUIRED_EXACT_REF_INVALID",
        "DOCUMENT_DISPLAY_PAGE_EVIDENCE_MISSING",
    }

    inapplicable_reader_pdf_candidate = json.loads(json.dumps(valid_document_candidate))
    inapplicable_reader_pdf_candidate["requires_reader_pdf"] = False
    inapplicable_reader_pdf_candidate["not_applicable_reason"] = "no reader PDF"
    inapplicable_reader_pdf = validate_document_display_scope_coverage(
        inapplicable_reader_pdf_candidate
    )
    assert inapplicable_reader_pdf["machine_check_status"] == "route_back_required"
    assert "DOCUMENT_DISPLAY_READER_PDF_NOT_APPLICABLE" in {
        item["code"] for item in inapplicable_reader_pdf["findings"]
    }

    valid_supplement_na_candidate = json.loads(json.dumps(valid_document_candidate))
    valid_supplement_na_candidate["supplement_applicable"] = False
    valid_supplement_na_candidate[
        "supplement_not_applicable_reason"
    ] = "the study has no supplement"
    valid_supplement_na_candidate["snapshot_inventory"] = [
        entry
        for entry in valid_supplement_na_candidate["snapshot_inventory"]
        if entry["member_id"] != "paper-combined"
    ]
    valid_supplement_na_candidate["audit_inventory"] = [
        entry
        for entry in valid_supplement_na_candidate["audit_inventory"]
        if entry["member_id"] != "paper-combined"
    ]
    valid_supplement_na = validate_document_display_scope_coverage(
        valid_supplement_na_candidate
    )
    assert valid_supplement_na["machine_check_status"] == "candidate_complete"

    supplement_identity_candidate = json.loads(json.dumps(valid_document_candidate))
    supplement_identity_candidate["audit_inventory"][1]["sha256"] = f"sha256:{'a' * 64}"
    supplement_identity = validate_document_display_scope_coverage(
        supplement_identity_candidate
    )
    assert "DOCUMENT_DISPLAY_SUPPLEMENT_PDF_IDENTITY_MISMATCH" in {
        item["code"] for item in supplement_identity["findings"]
    }
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
    evidence_ref = {
        "kind": "scholarskills_display_evidence",
        "ref": "evidence://display-a",
        "size_bytes": 123,
        "sha256": f"sha256:{'9' * 64}",
    }
    candidate_a = build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_evidence_ref=evidence_ref,
    )
    same_pixels_other_provenance = build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_evidence_ref={
            "kind": "scholarskills_display_evidence",
            "ref": "evidence://different-pdf-metadata",
            "size_bytes": 456,
            "sha256": f"sha256:{'b' * 64}",
        },
    )
    assert candidate_a["cache_key_sha256"] == (
        "sha256:f159ceb039e91fcdf43a3402b195592cbce25841837473284b03760a359a012a"
    )
    assert candidate_a["cache_key_sha256"] == same_pixels_other_provenance[
        "cache_key_sha256"
    ]
    assert set(candidate_a) == {
        "surface_kind",
        "schema_version",
        "review_scope_sha256",
        "rubric_sha256",
        "evidence_payload",
        "cache_key_sha256",
        "origin_reviewer_evidence_ref",
    }
    assert candidate_a["schema_version"] == 3
    assert candidate_a["origin_reviewer_evidence_ref"] == evidence_ref
    changed_pixel = dict(page_b)
    changed_pixel["pixel_sha256"] = f"sha256:{'5' * 64}"
    assert candidate_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [page_a, changed_pixel],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_evidence_ref=evidence_ref,
    )["cache_key_sha256"]
    changed_geometry = dict(page_b, width=1225)
    assert candidate_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [page_a, changed_geometry],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_evidence_ref=evidence_ref,
    )["cache_key_sha256"]
    reordered_a = dict(page_b, page_number=1)
    reordered_b = dict(page_a, page_number=2)
    assert candidate_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [reordered_a, reordered_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_evidence_ref=evidence_ref,
    )["cache_key_sha256"]
    assert candidate_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'6' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_evidence_ref=evidence_ref,
    )["cache_key_sha256"]
    assert candidate_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'7' * 64}",
        origin_reviewer_evidence_ref=evidence_ref,
    )["cache_key_sha256"]
    unbound_candidate = build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
    )
    assert unbound_candidate["origin_reviewer_evidence_ref"] is None
    try:
        build_page_hash_evidence_candidate(
            [page_a, page_b],
            review_scope_sha256=f"sha256:{'3' * 64}",
            rubric_sha256=f"sha256:{'4' * 64}",
            origin_reviewer_evidence_ref={
                "kind": "scholarskills_display_evidence",
                "ref": "evidence://missing-size",
                "sha256": f"sha256:{'9' * 64}",
            },
        )
        raise AssertionError("incomplete origin exact ref must fail closed")
    except ValueError:
        pass

    fixture_path = Path(__file__).with_name("fixtures") / "layout_qc_regression.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    long_label = fixture["panels"][0]["text_artists"][1]
    long_label_measurement = long_label["text_measurement"]
    long_label_wrap = long_label_measurement["semantic_wrap"]
    generated_wrap = generate_semantic_wrap(
        long_label["source_text"],
        available_width_px=long_label_measurement["available_width_px"],
        word_widths_px=long_label_wrap["word_widths_px"],
        space_width_px=long_label_wrap["space_width_px"],
    )
    assert generated_wrap["rendered_text"] == long_label["rendered_text"]
    assert generated_wrap["break_after_word_indices"] == [4, 9]
    assert generated_wrap["line_widths_px"] == [265, 252, 85]
    layout_audit = audit_layout_registry(fixture)
    assert layout_audit["machine_check_status"] == "geometry_checks_passed"
    assert layout_audit["registered_text_artist_count"] == 6
    assert layout_audit["checks"]["annotation_lane_separate"] is True
    assert layout_audit["checks"]["measured_wrap_valid"] is True
    assert layout_audit["semantic_artist_applicability"] == "not_applicable"

    semantic_fixture_path = (
        Path(__file__).with_name("fixtures")
        / "semantic_artist_flow_regression.json"
    )
    semantic_fixture = json.loads(semantic_fixture_path.read_text(encoding="utf-8"))
    semantic_audit = audit_layout_registry(semantic_fixture)
    assert semantic_audit["machine_check_status"] == "geometry_checks_passed"
    assert semantic_audit["semantic_flow_contract_required"] is True
    assert semantic_audit["registered_semantic_artist_count"] == 26
    assert semantic_audit["semantic_arrow_count"] == 2
    assert semantic_audit["semantic_segmented_group_span_count"] == 1
    assert semantic_audit["semantic_validated_segmented_group_span_count"] == 1
    for semantic_check in (
        "semantic_artist_applicability_valid",
        "semantic_artist_registry_complete",
        "semantic_artist_kinds_complete",
        "semantic_artists_inside_canvas",
        "semantic_artists_inside_safe_inset",
        "semantic_node_text_contained",
        "semantic_contract_geometry_bound",
        "semantic_lines_clear_of_text",
        "semantic_lines_clear_of_unrelated_nodes",
        "semantic_connectors_non_crossing",
        "semantic_arrowheads_clear_of_text",
        "semantic_relation_encoding_valid",
        "semantic_arrow_budget_met",
        "semantic_incoming_unambiguous",
        "semantic_bracket_spans_exact",
        "semantic_segmented_group_spans_exact",
        "semantic_segmented_group_perceptual_anchors_valid",
    ):
        assert semantic_audit["checks"][semantic_check] is True

    def semantic_violation_codes(candidate: Mapping[str, object]) -> set[str]:
        return {
            str(item["code"])
            for item in audit_layout_registry(candidate)["violations"]
        }

    def semantic_flow_item(
        candidate: Mapping[str, object],
        collection: str,
        identity_key: str,
        identity_value: str,
    ) -> dict[str, object]:
        return next(
            item
            for item in candidate["semantic_flow_contract"][collection]
            if item[identity_key] == identity_value
        )

    def semantic_artist_item(
        candidate: Mapping[str, object], artist_id: str
    ) -> dict[str, object]:
        return next(
            item
            for item in candidate["semantic_artist_registry"]["artists"]
            if item["artist_id"] == artist_id
        )

    missing_segmented_group = json.loads(json.dumps(semantic_fixture))
    missing_segmented_group["semantic_flow_contract"].pop("segmented_group_spans")
    assert "semantic_segmented_group_relation_set_mismatch" in (
        semantic_violation_codes(missing_segmented_group)
    )

    segmented_connector_to_child = json.loads(json.dumps(semantic_fixture))
    child_connector = semantic_flow_item(
        segmented_connector_to_child,
        "connectors",
        "connector_id",
        "band_source_to_group",
    )
    child_connector["destination_node_id"] = "band_child_a"
    child_connector["segments_px"][0] = [900, 420, 870, 280]
    child_segment_artist = semantic_artist_item(
        segmented_connector_to_child,
        "relation.band_partition.segment.1",
    )
    child_segment_artist["bbox_px"] = [870, 280, 900, 420]
    child_segment_artist["geometry_px"] = [900, 420, 870, 280]
    assert "semantic_segmented_group_connector_invalid" in (
        semantic_violation_codes(segmented_connector_to_child)
    )

    segmented_connector_arrowed = json.loads(json.dumps(semantic_fixture))
    semantic_flow_item(
        segmented_connector_arrowed,
        "connectors",
        "connector_id",
        "band_source_to_group",
    )["arrow_bearing"] = True
    assert "semantic_segmented_group_connector_invalid" in (
        semantic_violation_codes(segmented_connector_arrowed)
    )

    segmented_header_narrow = json.loads(json.dumps(semantic_fixture))
    narrow_group_node = semantic_flow_item(
        segmented_header_narrow, "nodes", "node_id", "band_group"
    )
    narrow_group_node["bbox_px"] = [850, 280, 950, 320]
    semantic_artist_item(
        segmented_header_narrow, "node.band_group.patch"
    )["bbox_px"] = [850, 280, 950, 320]
    semantic_flow_item(
        segmented_header_narrow,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["group_header_bbox_px"] = [850, 280, 950, 320]
    assert "semantic_segmented_group_span_mismatch" in (
        semantic_violation_codes(segmented_header_narrow)
    )

    segmented_children_gap = json.loads(json.dumps(semantic_fixture))
    gap_child_node = semantic_flow_item(
        segmented_children_gap, "nodes", "node_id", "band_child_b"
    )
    gap_child_node["bbox_px"] = [910, 180, 960, 280]
    semantic_artist_item(
        segmented_children_gap, "node.band_child_b.patch"
    )["bbox_px"] = [910, 180, 960, 280]
    assert "semantic_segmented_group_children_not_contiguous" in (
        semantic_violation_codes(segmented_children_gap)
    )

    segmented_children_overlap = json.loads(json.dumps(semantic_fixture))
    overlap_child_node = semantic_flow_item(
        segmented_children_overlap, "nodes", "node_id", "band_child_b"
    )
    overlap_child_node["bbox_px"] = [890, 180, 960, 280]
    semantic_artist_item(
        segmented_children_overlap, "node.band_child_b.patch"
    )["bbox_px"] = [890, 180, 960, 280]
    assert "semantic_segmented_group_children_not_contiguous" in (
        semantic_violation_codes(segmented_children_overlap)
    )

    segmented_header_detached = json.loads(json.dumps(semantic_fixture))
    detached_group_node = semantic_flow_item(
        segmented_header_detached, "nodes", "node_id", "band_group"
    )
    detached_group_node["bbox_px"] = [840, 300, 960, 340]
    semantic_artist_item(
        segmented_header_detached, "node.band_group.patch"
    )["bbox_px"] = [840, 300, 960, 340]
    semantic_flow_item(
        segmented_header_detached,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["group_header_bbox_px"] = [840, 300, 960, 340]
    assert "semantic_segmented_group_header_not_adjacent" in (
        semantic_violation_codes(segmented_header_detached)
    )

    segmented_side_anchor = json.loads(json.dumps(semantic_fixture))
    side_connector = semantic_flow_item(
        segmented_side_anchor,
        "connectors",
        "connector_id",
        "band_source_to_group",
    )
    side_connector["segments_px"][0] = [900, 420, 840, 300]
    side_artist = semantic_artist_item(
        segmented_side_anchor, "relation.band_partition.segment.1"
    )
    side_artist["bbox_px"] = [840, 300, 900, 420]
    side_artist["geometry_px"] = [900, 420, 840, 300]
    semantic_flow_item(
        segmented_side_anchor,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["actual_connector_terminal_px"] = [840, 300]
    assert "semantic_segmented_group_anchor_mismatch" in (
        semantic_violation_codes(segmented_side_anchor)
    )

    segmented_first_child_anchor = json.loads(json.dumps(semantic_fixture))
    first_child_connector = semantic_flow_item(
        segmented_first_child_anchor,
        "connectors",
        "connector_id",
        "band_source_to_group",
    )
    first_child_connector["segments_px"][0] = [900, 420, 870, 320]
    first_child_artist = semantic_artist_item(
        segmented_first_child_anchor, "relation.band_partition.segment.1"
    )
    first_child_artist["bbox_px"] = [870, 320, 900, 420]
    first_child_artist["geometry_px"] = [900, 420, 870, 320]
    semantic_flow_item(
        segmented_first_child_anchor,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["actual_connector_terminal_px"] = [870, 320]
    assert "semantic_segmented_group_anchor_mismatch" in (
        semantic_violation_codes(segmented_first_child_anchor)
    )
    assert (
        audit_layout_registry(segmented_first_child_anchor)[
            "semantic_validated_segmented_group_span_count"
        ]
        == 0
    )

    segmented_empty_label = json.loads(json.dumps(semantic_fixture))
    semantic_flow_item(
        segmented_empty_label,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["group_label"] = ""
    assert "semantic_segmented_group_label_empty" in (
        semantic_violation_codes(segmented_empty_label)
    )

    segmented_child_label = json.loads(json.dumps(semantic_fixture))
    child_label_span = semantic_flow_item(
        segmented_child_label,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )
    child_label_span["group_label"] = "Alive n=70"
    child_label_span["perceptual_anchor"][
        "label_artist_id"
    ] = "node.band_child_a.label"
    assert "semantic_segmented_group_label_artist_invalid" in (
        semantic_violation_codes(segmented_child_label)
    )

    segmented_orientation = json.loads(json.dumps(semantic_fixture))
    semantic_flow_item(
        segmented_orientation,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["orientation"] = "vertical"
    assert "semantic_segmented_group_orientation_invalid" in (
        semantic_violation_codes(segmented_orientation)
    )

    segmented_anchor_mode = json.loads(json.dumps(semantic_fixture))
    semantic_flow_item(
        segmented_anchor_mode,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["perceptual_anchor"]["mode"] = "first_child"
    assert "semantic_segmented_group_perceptual_anchor_invalid" in (
        semantic_violation_codes(segmented_anchor_mode)
    )

    segmented_renderer_geometry = json.loads(json.dumps(semantic_fixture))
    semantic_artist_item(
        segmented_renderer_geometry, "relation.band_partition.segment.1"
    )["geometry_px"] = [900, 420, 880, 320]
    assert "semantic_connector_geometry_mismatch" in (
        semantic_violation_codes(segmented_renderer_geometry)
    )

    missing_semantic_registry = json.loads(json.dumps(semantic_fixture))
    missing_semantic_registry.pop("semantic_artist_registry")
    missing_semantic_registry_audit = audit_layout_registry(
        missing_semantic_registry
    )
    assert "semantic_artist_registry_missing" in {
        item["code"] for item in missing_semantic_registry_audit["violations"]
    }

    missing_semantic_prefix = json.loads(json.dumps(semantic_fixture))
    missing_semantic_prefix["semantic_artist_registry"]["artists"] = [
        item
        for item in missing_semantic_prefix["semantic_artist_registry"]["artists"]
        if item["owner_prefix"] != "node.child_b"
    ]
    missing_semantic_prefix_audit = audit_layout_registry(missing_semantic_prefix)
    assert "semantic_artist_prefix_missing" in {
        item["code"] for item in missing_semantic_prefix_audit["violations"]
    }

    missing_semantic_kind = json.loads(json.dumps(semantic_fixture))
    missing_semantic_kind["semantic_flow_contract"]["expected_artist_kinds"].append(
        "ConnectionPatch"
    )
    missing_semantic_kind_audit = audit_layout_registry(missing_semantic_kind)
    assert "semantic_artist_kinds_missing" in {
        item["code"] for item in missing_semantic_kind_audit["violations"]
    }

    semantic_canvas_overflow = json.loads(json.dumps(semantic_fixture))
    semantic_canvas_overflow["semantic_artist_registry"]["artists"][1][
        "bbox_px"
    ] = [100, 180, 1020, 280]
    semantic_canvas_overflow_audit = audit_layout_registry(
        semantic_canvas_overflow
    )
    assert "semantic_artist_canvas_overflow" in {
        item["code"] for item in semantic_canvas_overflow_audit["violations"]
    }

    semantic_safe_inset = json.loads(json.dumps(semantic_fixture))
    semantic_safe_inset["semantic_artist_registry"]["artists"][1]["bbox_px"] = [
        10,
        180,
        300,
        280,
    ]
    semantic_safe_inset_audit = audit_layout_registry(semantic_safe_inset)
    assert "semantic_artist_safe_inset_violation" in {
        item["code"] for item in semantic_safe_inset_audit["violations"]
    }

    node_text_outside = json.loads(json.dumps(semantic_fixture))
    node_text_outside["semantic_flow_contract"]["nodes"][0]["text_artist_ids"] = [
        "node.child_b.label"
    ]
    node_text_outside_audit = audit_layout_registry(node_text_outside)
    assert "semantic_node_text_outside_node" in {
        item["code"] for item in node_text_outside_audit["violations"]
    }

    semantic_line_text = json.loads(json.dumps(semantic_fixture))
    semantic_line_text["semantic_flow_contract"]["connectors"][0]["segments_px"][
        0
    ] = [200, 485, 200, 350]
    semantic_line_text_audit = audit_layout_registry(semantic_line_text)
    assert "semantic_line_text_intersection" in {
        item["code"] for item in semantic_line_text_audit["violations"]
    }

    semantic_geometry_mismatch = json.loads(json.dumps(semantic_fixture))
    semantic_geometry_mismatch["semantic_flow_contract"]["connectors"][0][
        "segments_px"
    ][0] = [220, 420, 220, 350]
    semantic_geometry_mismatch_audit = audit_layout_registry(
        semantic_geometry_mismatch
    )
    assert "semantic_connector_geometry_mismatch" in {
        item["code"] for item in semantic_geometry_mismatch_audit["violations"]
    }

    semantic_artist_direction_mismatch = json.loads(json.dumps(semantic_fixture))
    direction_mismatch_artist = next(
        item
        for item in semantic_artist_direction_mismatch[
            "semantic_artist_registry"
        ]["artists"]
        if item["artist_id"] == "relation.root_partition.child_a.segment.1"
    )
    direction_mismatch_artist["geometry_px"] = [200, 350, 200, 420]
    semantic_artist_direction_mismatch_audit = audit_layout_registry(
        semantic_artist_direction_mismatch
    )
    assert "semantic_connector_geometry_mismatch" in {
        item["code"]
        for item in semantic_artist_direction_mismatch_audit["violations"]
    }

    semantic_source_anchor = json.loads(json.dumps(semantic_fixture))
    semantic_source_anchor["semantic_flow_contract"]["connectors"][0][
        "segments_px"
    ][0] = [200, 410, 200, 350]
    source_anchor_artist = next(
        item
        for item in semantic_source_anchor["semantic_artist_registry"]["artists"]
        if item["artist_id"] == "relation.root_partition.child_a.segment.1"
    )
    source_anchor_artist["bbox_px"] = [200, 350, 200, 410]
    source_anchor_artist["geometry_px"] = [200, 410, 200, 350]
    semantic_source_anchor_audit = audit_layout_registry(semantic_source_anchor)
    assert "semantic_connector_source_not_anchored" in {
        item["code"] for item in semantic_source_anchor_audit["violations"]
    }

    semantic_destination_anchor = json.loads(json.dumps(semantic_fixture))
    semantic_destination_anchor["semantic_flow_contract"]["connectors"][0][
        "segments_px"
    ][1] = [200, 350, 200, 250]
    destination_anchor_artist = next(
        item
        for item in semantic_destination_anchor["semantic_artist_registry"][
            "artists"
        ]
        if item["artist_id"] == "relation.root_partition.child_a.segment.2"
    )
    destination_anchor_artist["bbox_px"] = [200, 250, 200, 350]
    destination_anchor_artist["geometry_px"] = [200, 350, 200, 250]
    semantic_destination_anchor_audit = audit_layout_registry(
        semantic_destination_anchor
    )
    assert "semantic_connector_destination_not_anchored" in {
        item["code"] for item in semantic_destination_anchor_audit["violations"]
    }

    semantic_false_junction = json.loads(json.dumps(semantic_fixture))
    false_junction_connector = semantic_false_junction["semantic_flow_contract"][
        "connectors"
    ][0]
    false_junction_connector["segments_px"] = [
        [250, 420, 250, 350],
        [250, 350, 200, 280],
    ]
    for artist_id, bbox_px, geometry_px in (
        (
            "relation.root_partition.child_a.segment.1",
            [250, 350, 250, 420],
            [250, 420, 250, 350],
        ),
        (
            "relation.root_partition.child_a.segment.2",
            [200, 280, 250, 350],
            [250, 350, 200, 280],
        ),
    ):
        artist = next(
            item
            for item in semantic_false_junction["semantic_artist_registry"][
                "artists"
            ]
            if item["artist_id"] == artist_id
        )
        artist["bbox_px"] = bbox_px
        artist["geometry_px"] = geometry_px
    semantic_false_junction_audit = audit_layout_registry(
        semantic_false_junction
    )
    assert "semantic_junction_group_invalid" in {
        item["code"] for item in semantic_false_junction_audit["violations"]
    }

    semantic_line_node = json.loads(json.dumps(semantic_fixture))
    semantic_line_node["semantic_flow_contract"]["connectors"][0]["segments_px"][
        0
    ] = [600, 500, 600, 200]
    semantic_line_node_audit = audit_layout_registry(semantic_line_node)
    assert "semantic_line_unrelated_node_intersection" in {
        item["code"] for item in semantic_line_node_audit["violations"]
    }

    semantic_crossing = json.loads(json.dumps(semantic_fixture))
    semantic_crossing["semantic_flow_contract"]["connectors"][1][
        "junction_group"
    ] = "independent_connector"
    semantic_crossing["semantic_flow_contract"]["connectors"][1]["segments_px"][
        0
    ] = [100, 385, 300, 385]
    semantic_crossing_audit = audit_layout_registry(semantic_crossing)
    assert "semantic_connector_crossing_unauthorized" in {
        item["code"] for item in semantic_crossing_audit["violations"]
    }

    semantic_arrowhead_text = json.loads(json.dumps(semantic_fixture))
    semantic_arrowhead_text["semantic_artist_registry"]["artists"][10][
        "bbox_px"
    ] = [150, 455, 250, 485]
    semantic_arrowhead_text_audit = audit_layout_registry(
        semantic_arrowhead_text
    )
    assert "semantic_arrowhead_text_intersection" in {
        item["code"] for item in semantic_arrowhead_text_audit["violations"]
    }

    semantic_relation_encoding = json.loads(json.dumps(semantic_fixture))
    next(
        relation
        for relation in semantic_relation_encoding["semantic_flow_contract"][
            "relations"
        ]
        if relation["relation_id"] == "children_identity"
    )["encoding"] = "arrow_split"
    semantic_relation_encoding_audit = audit_layout_registry(
        semantic_relation_encoding
    )
    assert "semantic_relation_encoding_invalid" in {
        item["code"] for item in semantic_relation_encoding_audit["violations"]
    }

    semantic_arrow_budget = json.loads(json.dumps(semantic_fixture))
    semantic_arrow_budget["semantic_flow_contract"]["arrow_budget"] = 1
    semantic_arrow_budget_audit = audit_layout_registry(semantic_arrow_budget)
    assert "semantic_arrow_budget_exceeded" in {
        item["code"] for item in semantic_arrow_budget_audit["violations"]
    }

    semantic_ambiguous_incoming = json.loads(json.dumps(semantic_fixture))
    semantic_ambiguous_incoming["semantic_flow_contract"]["connectors"][1][
        "destination_node_id"
    ] = "child_a"
    semantic_ambiguous_incoming_audit = audit_layout_registry(
        semantic_ambiguous_incoming
    )
    assert "semantic_ambiguous_incoming_connectors" in {
        item["code"] for item in semantic_ambiguous_incoming_audit["violations"]
    }

    semantic_bracket_span = json.loads(json.dumps(semantic_fixture))
    semantic_bracket_span["semantic_flow_contract"]["brackets"][0][
        "observed_span_px"
    ] = [100, 690]
    semantic_bracket_span_audit = audit_layout_registry(semantic_bracket_span)
    assert "semantic_bracket_span_mismatch" in {
        item["code"] for item in semantic_bracket_span_audit["violations"]
    }

    semantic_bracket_geometry = json.loads(json.dumps(semantic_fixture))
    bracket_artist = next(
        item
        for item in semantic_bracket_geometry["semantic_artist_registry"]["artists"]
        if item["artist_id"] == "relation.children_identity.segment.1"
    )
    bracket_artist.pop("geometry_px")
    semantic_bracket_geometry_audit = audit_layout_registry(
        semantic_bracket_geometry
    )
    assert "semantic_bracket_geometry_invalid" in {
        item["code"] for item in semantic_bracket_geometry_audit["violations"]
    }

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
    assert (
        receipt["semantic_artist_scope"]
        == "not_applicable:statistical_layout_regression"
    )
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

    rendered_text_counterexample = json.loads(json.dumps(fixture))
    rendered_text_counterexample["panels"][0]["text_artists"][1][
        "rendered_text"
    ] = long_label["source_text"]
    rendered_text_audit = audit_layout_registry(rendered_text_counterexample)
    assert "semantic_wrap_rendered_text_mismatch" in {
        item["code"] for item in rendered_text_audit["violations"]
    }
    assert rendered_text_audit["checks"]["measured_wrap_valid"] is False

    semantic_break_counterexample = json.loads(json.dumps(fixture))
    semantic_break_counterexample["panels"][0]["text_artists"][1][
        "text_measurement"
    ]["semantic_wrap"]["break_after_word_indices"] = [3, 9]
    semantic_break_audit = audit_layout_registry(semantic_break_counterexample)
    assert "semantic_wrap_break_positions_mismatch" in {
        item["code"] for item in semantic_break_audit["violations"]
    }
    assert semantic_break_audit["checks"]["measured_wrap_valid"] is False

    boolean_line_count_counterexample = json.loads(json.dumps(fixture))
    boolean_line_count_counterexample["panels"][0]["text_artists"][2][
        "text_measurement"
    ]["line_count"] = True
    boolean_line_count_audit = audit_layout_registry(boolean_line_count_counterexample)
    assert "semantic_wrap_line_count_mismatch" in {
        item["code"] for item in boolean_line_count_audit["violations"]
    }
    assert boolean_line_count_audit["checks"]["measured_wrap_valid"] is False

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

    numbering_fixture_path = Path(__file__).with_name("fixtures") / "figure-numbering-one-owner.json"
    numbering_fixture = json.loads(numbering_fixture_path.read_text(encoding="utf-8"))
    numbering_candidate = numbering_fixture["candidate"]
    numbering_audit = validate_figure_numbering_one_owner(numbering_candidate)
    assert numbering_audit["machine_check_status"] == "candidate_complete"
    assert all(
        item["occurrence_count"] == 1
        for item in numbering_audit["figure_surface_invariants"]
    )
    for negative in numbering_fixture["negative_cases"]:
        changed = json.loads(json.dumps(numbering_candidate))
        figure = next(
            item for item in changed["figures"]
            if item["figure_id"] == negative["figure_id"]
        )
        occurrences = figure["output_surfaces"][negative["surface"]]["occurrences"]
        occurrence = next(
            item for item in occurrences if item["source"] == negative["source"]
        )
        occurrence["occurrence_count"] = negative["replacement_count"]
        changed_audit = validate_figure_numbering_one_owner(changed)
        assert negative["expected_code"] in {
            item["code"] for item in changed_audit["findings"]
        }
    checks = 132 if fitz_available else 125 if pillow_available else 112
    print(json.dumps({"ok": True, "checks": checks}, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(_main())
