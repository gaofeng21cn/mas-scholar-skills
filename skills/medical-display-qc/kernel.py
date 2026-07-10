"""Refs-only helpers and a non-mutating medical display artifact inspector."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Mapping


DISPLAY_QC_REFS = (
    "display_artifact_inventory_ref",
    "programmatic_figure_audit_ref",
    "export_integrity_ref",
    "panel_caption_consistency_ref",
    "claim_display_alignment_ref",
    "accessibility_and_size_ref",
    "display_qc_support_map_ref",
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
        "candidate_package_ref": None,
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
        description="Inspect a rendered display artifact without mutating it"
    )
    parser.add_argument("--inspect", metavar="PATH", help="PNG/JPEG/TIFF/PDF path")
    args = parser.parse_args(argv)
    if args.inspect is None:
        _self_check()
        return 0
    candidate = inspect_display_artifact(args.inspect)
    print(json.dumps(candidate, indent=2, sort_keys=True))
    return 2 if candidate["export_integrity_ref"]["hard_fail"] else 0


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
                fitz = _load_pymupdf()
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

    checks = 34 if fitz_available else 30 if pillow_available else 17
    print(json.dumps({"ok": True, "checks": checks}, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(_main())
