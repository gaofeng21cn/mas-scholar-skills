from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


ENGINE_ID = "fenggaolab.org.medical-display-core.fixed-input-live-regression.v1"
PACK_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PACK_ROOT.parents[1]
TAIL_CHARS = 4000
RENDER_TIMEOUT_SECONDS = 120


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _repo_ref(repo_root: Path, ref: str) -> Path:
    path = (repo_root / ref).resolve()
    try:
        path.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"repository ref escapes the repository root: {ref}") from exc
    if not path.is_file():
        raise ValueError(f"repository ref does not exist: {ref}")
    return path


def load_golden_manifest(pack_root: Path = PACK_ROOT) -> dict[str, Any]:
    manifest = _read_json(pack_root / "golden_manifest.json")
    templates = manifest.get("golden_templates")
    if not isinstance(templates, list) or not templates:
        raise ValueError("golden_manifest.json must contain golden_templates")
    if manifest.get("authority_boundary", {}).get("authority") is not False:
        raise ValueError("golden_manifest.json must retain authority=false")
    if manifest.get("authority_boundary", {}).get("publication_ready") is not False:
        raise ValueError("golden_manifest.json must retain publication_ready=false")
    return manifest


def _load_descriptor(entry: dict[str, Any], repo_root: Path) -> tuple[Path, dict[str, Any]]:
    descriptor_path = _repo_ref(repo_root, str(entry["descriptor_ref"]))
    with descriptor_path.open("rb") as handle:
        descriptor = tomllib.load(handle)
    for field in ("template_id", "kind", "renderer_family", "execution_mode"):
        if descriptor.get(field) != entry.get(field):
            raise ValueError(f"{entry.get('template_id')} descriptor {field} does not match golden manifest")
    return descriptor_path, descriptor


def _require_list(value: Any, label: str, *, minimum: int = 1) -> list[Any]:
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(f"{label} must contain at least {minimum} item(s)")
    return value


def _curve_xy(points: list[Any], x_field: str, y_field: str, label: str) -> tuple[list[float], list[float]]:
    x_values: list[float] = []
    y_values: list[float] = []
    for index, point in enumerate(points):
        if not isinstance(point, dict):
            raise ValueError(f"{label}[{index}] must be an object")
        x_values.append(float(point[x_field]))
        y_values.append(float(point[y_field]))
    return x_values, y_values


def _required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _required_probability(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a finite probability")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a finite probability") from exc
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        raise ValueError(f"{label} must be between 0 and 1")
    return number


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _adapt_fixed_input(template_id: str, example: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if template_id == "roc_curve_binary":
        curve = _require_list(example.get("curve"), "roc_curve_binary.curve", minimum=2)
        x_values, y_values = _curve_xy(curve, "false_positive_rate", "true_positive_rate", "curve")
        auc = _required_probability(example.get("auc"), "roc_curve_binary.auc")
        return "roc_example_to_r_series_v1", {
            **example,
            "title": "Receiver operating characteristic",
            "x_label": "False-positive rate",
            "y_label": "True-positive rate",
            "series": [{"label": f"Model (AUC {auc:.2f})", "x": x_values, "y": y_values}],
            "reference_line": {"x": [0.0, 1.0], "y": [0.0, 1.0]},
        }

    if template_id == "calibration_curve_binary":
        points = _require_list(example.get("calibration_points"), "calibration_curve_binary.calibration_points", minimum=2)
        x_values, y_values = _curve_xy(points, "predicted_probability", "observed_event_rate", "calibration_points")
        return "calibration_example_to_r_series_v1", {
            **example,
            "title": "Calibration curve",
            "x_label": "Predicted probability",
            "y_label": "Observed event rate",
            "series": [
                {
                    "label": _required_text(
                        example.get("model_label"),
                        "calibration_curve_binary.model_label",
                    ),
                    "x": x_values,
                    "y": y_values,
                }
            ],
            "reference_line": {"x": [0.0, 1.0], "y": [0.0, 1.0]},
        }

    if template_id == "kaplan_meier_grouped":
        groups_payload = _require_list(example.get("groups"), "kaplan_meier_grouped.groups")
        groups: list[dict[str, Any]] = []
        risk_table: list[dict[str, Any]] = []
        for index, group in enumerate(groups_payload):
            if not isinstance(group, dict):
                raise ValueError(f"groups[{index}] must be an object")
            curve = _require_list(group.get("curve"), f"groups[{index}].curve", minimum=2)
            times, values = _curve_xy(curve, "time", "survival_probability", f"groups[{index}].curve")
            label = _required_text(group.get("label"), f"groups[{index}].label")
            groups.append({"label": label, "times": times, "values": values})
            risk_table.append(
                {
                    "label": label,
                    "times": times,
                    "at_risk": [int(item["at_risk"]) for item in curve],
                }
            )
        return "kaplan_meier_example_to_r_groups_v1", {
            **example,
            "title": "Kaplan-Meier survival by group",
            "x_label": _required_text(
                example.get("time_unit"), "kaplan_meier_grouped.time_unit"
            ),
            "y_label": "Survival probability",
            "groups": groups,
            "risk_table": risk_table,
            "annotation": (
                "Log-rank p="
                f"{_required_probability(example.get('log_rank_p'), 'kaplan_meier_grouped.log_rank_p'):.3g}"
            ),
        }

    if template_id == "heatmap_group_comparison":
        row_labels = [str(item) for item in _require_list(example.get("row_labels"), "heatmap_group_comparison.row_labels")]
        column_labels = [str(item) for item in _require_list(example.get("column_labels"), "heatmap_group_comparison.column_labels")]
        matrix = _require_list(example.get("matrix"), "heatmap_group_comparison.matrix")
        if len(matrix) != len(row_labels):
            raise ValueError("heatmap_group_comparison.matrix row count must match row_labels")
        cells: list[dict[str, Any]] = []
        for row_index, row in enumerate(matrix):
            values = _require_list(row, f"matrix[{row_index}]", minimum=len(column_labels))
            if len(values) != len(column_labels):
                raise ValueError(f"matrix[{row_index}] column count must match column_labels")
            for column_index, value in enumerate(values):
                cells.append({"x": column_labels[column_index], "y": row_labels[row_index], "value": float(value)})
        return "heatmap_example_to_r_cells_v1", {
            **example,
            "title": "Group comparison heatmap",
            "x_label": "Group",
            "y_label": "Marker",
            "cells": cells,
            "row_order": [{"label": item} for item in row_labels],
            "column_order": [{"label": item} for item in column_labels],
        }

    if template_id == "table1_baseline_characteristics":
        columns = [str(item) for item in _require_list(example.get("columns"), "table1_baseline_characteristics.columns")]
        rows = _require_list(example.get("rows"), "table1_baseline_characteristics.rows")
        variables: list[dict[str, Any]] = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError(f"rows[{index}] must be an object")
            variables.append(
                {
                    "label": str(row["label"]),
                    "values": [str(row[_slug(column)]) for column in columns],
                }
            )
        return "table1_example_to_python_shell_v1", {
            **example,
            "title": "Baseline characteristics",
            "groups": [{"label": item} for item in columns],
            "variables": variables,
        }

    if template_id == "submission_graphical_abstract":
        sections = _require_list(example.get("sections"), "submission_graphical_abstract.sections")
        accent_roles = ("primary", "secondary", "contrast")
        panels: list[dict[str, Any]] = []
        for index, section in enumerate(sections):
            if not isinstance(section, dict):
                raise ValueError(f"sections[{index}] must be an object")
            label = str(section["label"])
            value = str(section["text"])
            panel_id = _slug(label) or f"panel_{index + 1}"
            panels.append(
                {
                    "panel_id": panel_id,
                    "panel_label": chr(ord("A") + index),
                    "title": label,
                    "subtitle": value,
                    "visual_role": panel_id,
                    "rows": [
                        {
                            "cards": [
                                {
                                    "card_id": f"{panel_id}_summary",
                                    "title": label,
                                    "value": value,
                                    "accent_role": accent_roles[index % len(accent_roles)],
                                }
                            ]
                        }
                    ],
                }
            )
        return "submission_ga_example_to_python_shell_v1", {
            **example,
            "shell_id": "fenggaolab.org.medical-display-core::submission_graphical_abstract",
            "display_id": _required_text(
                example.get("figure_id"),
                "submission_graphical_abstract.figure_id",
            ),
            "catalog_id": "example:medical-display-core/submission_graphical_abstract",
            "title": "Study pathway to clinical use",
            "caption": "Example-only graphical abstract rendered for fixed-input regression.",
            "panels": panels,
            "footer_pills": [],
        }

    raise ValueError(f"no fixed-input adapter is registered for {template_id}")


def _pillow_modules() -> tuple[Any, Any]:
    try:
        from PIL import Image, ImageChops
    except ImportError as exc:
        raise ModuleNotFoundError(
            "Pillow is required for PNG verification and content-density inspection; "
            "the live-regression engine does not install dependencies."
        ) from exc
    return Image, ImageChops


def _inspect_png(path: Path) -> dict[str, Any]:
    Image, ImageChops = _pillow_modules()
    with Image.open(path) as source:
        image_format = source.format
        source_mode = source.mode
        width, height = source.size
        source.verify()
    if image_format != "PNG":
        raise ValueError(f"expected PNG output, found {image_format or 'unknown format'}")

    with Image.open(path) as source:
        rendered = source.convert("RGBA")
        extrema = rendered.getextrema()
        alpha_extrema = extrema[3]
        confirmed_blank = alpha_extrema[1] == 0 or (
            alpha_extrema == (255, 255)
            and all(channel_min == channel_max for channel_min, channel_max in extrema[:3])
        )
        sample = rendered.copy()
        sample.thumbnail((512, 512), Image.Resampling.LANCZOS, reducing_gap=2.0)
    sample_width, sample_height = sample.size
    corners = [
        sample.getpixel((0, 0)),
        sample.getpixel((sample_width - 1, 0)),
        sample.getpixel((0, sample_height - 1)),
        sample.getpixel((sample_width - 1, sample_height - 1)),
    ]
    corner_counts = {pixel: corners.count(pixel) for pixel in corners}
    background = max(corner_counts, key=corner_counts.get)
    background_image = Image.new("RGBA", sample.size, background)
    difference = ImageChops.difference(sample, background_image)
    threshold = [0 if value <= 8 else 255 for value in range(256)]
    channels = [channel.point(threshold) for channel in difference.split()]
    content_mask = channels[0]
    for channel in channels[1:]:
        content_mask = ImageChops.lighter(content_mask, channel)
    content_pixels = content_mask.histogram()[255]
    return {
        "valid": True,
        "width": width,
        "height": height,
        "source_mode": source_mode,
        "sample_width": sample_width,
        "sample_height": sample_height,
        "background_rgba": list(background),
        "content_density": round(content_pixels / max(1, sample_width * sample_height), 6),
        "confirmed_blank": confirmed_blank,
        "blank_basis": "full_resolution_visible_uniformity_or_full_transparency",
    }


def _inspect_pdf(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    header = data[:8]
    tail = data[-4096:]
    signature_valid = header.startswith(b"%PDF-")
    eof_present = b"%%EOF" in tail
    startxref_present = b"startxref" in tail
    structure_valid = signature_valid and eof_present and startxref_present
    metadata: dict[str, Any] = {
        "valid": structure_valid,
        "header": header.decode("latin-1", errors="replace"),
        "signature_valid": signature_valid,
        "eof_present": eof_present,
        "startxref_present": startxref_present,
        "validation_depth": "pdf_signature_eof_and_cross_reference_structure",
    }
    if not structure_valid:
        return metadata

    pdf_module = None
    for module_name in ("pymupdf", "fitz"):
        try:
            candidate = importlib.import_module(module_name)
        except ImportError:
            continue
        if all(hasattr(candidate, attribute) for attribute in ("open", "Matrix", "csRGB")):
            pdf_module = candidate
            break
    if pdf_module is None:
        metadata.update(
            {
                "valid": None,
                "confirmed_blank": None,
                "confirmed_blank_pages": None,
                "validation_depth": "pdf_visual_inspection_dependency_unavailable",
                "execution_issue_candidate": {
                    "type": "dependency_unavailable",
                    "authority": False,
                    "dependency_kind": "python_module",
                    "dependency": "PyMuPDF",
                    "import_names": ["pymupdf", "fitz"],
                    "message": (
                        "PyMuPDF is required for PDF visual blank inspection; "
                        "the live-regression engine does not install dependencies."
                    ),
                },
            }
        )
        return metadata

    try:
        document = pdf_module.open(str(path))
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError(f"PDF could not be opened: {exc}") from exc
    try:
        if getattr(document, "needs_pass", False):
            raise ValueError("PDF requires a password before visual inspection")
        page_count = int(document.page_count)
        if page_count < 1:
            raise ValueError("PDF contains no pages")
        confirmed_blank_pages: list[int] = []
        for page_index in range(page_count):
            page = document.load_page(page_index)
            pixmap = page.get_pixmap(
                matrix=pdf_module.Matrix(1.0, 1.0),
                colorspace=pdf_module.csRGB,
                alpha=False,
            )
            samples = memoryview(pixmap.samples)
            if not samples:
                raise ValueError(f"PDF page {page_index + 1} rendered no pixels")
            channel_count = int(pixmap.n)
            channel_extrema = [
                {
                    "min": min(samples[offset::channel_count]),
                    "max": max(samples[offset::channel_count]),
                }
                for offset in range(channel_count)
            ]
            if all(item["min"] == item["max"] for item in channel_extrema):
                confirmed_blank_pages.append(page_index + 1)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError(f"PDF pages could not be visually inspected: {exc}") from exc
    finally:
        document.close()

    metadata.update(
        {
            "valid": True,
            "page_count": page_count,
            "confirmed_blank": bool(confirmed_blank_pages),
            "confirmed_blank_pages": confirmed_blank_pages,
            "blank_basis": "72_dpi_full_page_rgb_uniformity",
            "validation_depth": "pdf_structure_and_rendered_page_blank_inspection",
        }
    )
    return metadata


def _inspect_layout(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("layout sidecar must contain a JSON object")
    template_id = _required_text(value.get("template_id"), "layout.template_id")
    device = value.get("device")
    if not isinstance(device, dict):
        raise ValueError("layout.device must be an object")
    box_families: dict[str, list[Any]] = {}
    boxes: list[tuple[str, int, dict[str, Any]]] = []
    for family in ("layout_boxes", "panel_boxes", "guide_boxes"):
        rows = value.get(family, [])
        if not isinstance(rows, list):
            raise ValueError(f"layout.{family} must be an array")
        box_families[family] = rows
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError(f"layout.{family}[{index}] must be an object")
            boxes.append((family, index, row))
    if not boxes:
        raise ValueError("layout sidecar must contain at least one layout, panel, or guide box")

    for family, index, box in [("device", 0, device), *boxes]:
        coordinates: dict[str, float] = {}
        for coordinate in ("x0", "y0", "x1", "y1"):
            raw_value = box.get(coordinate)
            if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
                raise ValueError(f"layout.{family}[{index}].{coordinate} must be numeric")
            coordinates[coordinate] = float(raw_value)
            if not math.isfinite(coordinates[coordinate]):
                raise ValueError(f"layout.{family}[{index}].{coordinate} must be finite")
        width = coordinates["x1"] - coordinates["x0"]
        height = coordinates["y1"] - coordinates["y0"]
        if width < 0 or height < 0:
            raise ValueError(f"layout.{family}[{index}] has inverted geometry")
        if family in {"device", "panel_boxes"} and (width == 0 or height == 0):
            raise ValueError(f"layout.{family}[{index}] must have positive width and height")
        if family in {"layout_boxes", "guide_boxes"} and width == 0 and height == 0:
            raise ValueError(f"layout.{family}[{index}] must span at least one dimension")
    return {
        "valid": True,
        "parse_ok": True,
        "template_id": template_id,
        "top_level_keys": sorted(value),
        "layout_box_count": len(box_families["layout_boxes"]),
        "panel_box_count": len(box_families["panel_boxes"]),
        "guide_box_count": len(box_families["guide_boxes"]),
    }


def _inspect_svg(path: Path) -> dict[str, Any]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"SVG XML could not be parsed: {exc}") from exc
    svg_namespace = "http://www.w3.org/2000/svg"
    xlink_href = "{http://www.w3.org/1999/xlink}href"

    def expanded_name(element: ET.Element) -> tuple[str | None, str]:
        tag = str(element.tag)
        if tag.startswith("{") and "}" in tag:
            namespace, name = tag[1:].split("}", 1)
            return namespace, name.lower()
        return None, tag.lower()

    def definitely_nonpositive_length(value: str | None, *, missing_is_zero: bool) -> bool:
        if value is None:
            return missing_is_zero
        text = value.strip()
        if not text:
            return True
        match = re.fullmatch(
            r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(?:[A-Za-z%]+)?",
            text,
        )
        return match is not None and float(match.group(1)) <= 0

    def renderable_candidate(element: ET.Element, name: str) -> bool:
        if name == "text":
            return bool("".join(element.itertext()).strip())
        if name == "path":
            return bool((element.get("d") or "").strip())
        required_lengths = {
            "rect": ("width", "height"),
            "circle": ("r",),
            "ellipse": ("rx", "ry"),
        }
        if name in required_lengths:
            return not any(
                definitely_nonpositive_length(element.get(attribute), missing_is_zero=True)
                for attribute in required_lengths[name]
            )
        if name in {"polygon", "polyline"}:
            return bool((element.get("points") or "").strip())
        if name in {"image", "use"}:
            href = element.get("href") or element.get(xlink_href)
            if not href or not href.strip():
                return False
            return not any(
                definitely_nonpositive_length(element.get(attribute), missing_is_zero=False)
                for attribute in ("width", "height")
            )
        if name == "foreignobject":
            if any(
                definitely_nonpositive_length(element.get(attribute), missing_is_zero=True)
                for attribute in ("width", "height")
            ):
                return False
            return bool(len(element) or "".join(element.itertext()).strip())
        return True

    root_namespace, local_name = expanded_name(root)
    root_valid = local_name == "svg" and root_namespace in {None, svg_namespace}
    renderable_elements = {
        "circle",
        "ellipse",
        "foreignobject",
        "image",
        "line",
        "path",
        "polygon",
        "polyline",
        "rect",
        "text",
        "use",
    }
    non_rendered_containers = {
        "clippath",
        "desc",
        "defs",
        "marker",
        "mask",
        "metadata",
        "pattern",
        "script",
        "style",
        "symbol",
        "title",
    }
    candidate_counts: dict[str, int] = {}
    if root_valid:
        stack: list[tuple[ET.Element, bool]] = [(root, False)]
        while stack:
            element, suppressed = stack.pop()
            element_namespace, element_name = expanded_name(element)
            suppressed = (
                suppressed
                or element_namespace != root_namespace
                or element_name in non_rendered_containers
            )
            if (
                not suppressed
                and element_name in renderable_elements
                and renderable_candidate(element, element_name)
            ):
                candidate_counts[element_name] = candidate_counts.get(element_name, 0) + 1
            stack.extend((child, suppressed) for child in reversed(element))
    candidate_count = sum(candidate_counts.values())
    return {
        "valid": root_valid,
        "root_element": local_name,
        "root_namespace": root_namespace,
        "child_count": len(root),
        "renderable_element_candidate_count": candidate_count,
        "renderable_element_candidate_counts": candidate_counts,
        "confirmed_blank": root_valid and candidate_count == 0,
        "blank_basis": "no_definitely_renderable_svg_element_candidate",
    }


def _inspect_text(path: Path) -> dict[str, Any]:
    value = path.read_text(encoding="utf-8-sig").lstrip("\ufeff")
    if "\x00" in value:
        raise ValueError("text export contains a NUL character")
    return {
        "valid": True,
        "encoding": "utf-8-sig",
        "character_count": len(value),
        "confirmed_blank": not value.strip(),
        "blank_basis": "utf8_text_empty_after_bom_and_whitespace_strip",
    }


def _artifact_metadata(path: Path, kind: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "applicable": True,
        "path": str(path),
        "exists": path.is_file(),
    }
    if not path.is_file():
        return metadata
    metadata.update({"size_bytes": path.stat().st_size, "sha256": _sha256(path)})
    try:
        if kind == "png":
            metadata.update(_inspect_png(path))
        elif kind == "pdf":
            metadata.update(_inspect_pdf(path))
        elif kind == "layout":
            metadata.update(_inspect_layout(path))
        elif kind == "svg":
            metadata.update(_inspect_svg(path))
        elif kind in {"csv", "md"}:
            metadata.update(_inspect_text(path))
        else:
            metadata["valid"] = path.stat().st_size > 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        metadata.update({"valid": False, "validation_error": str(exc)})
    return metadata


def _output_paths(output_dir: Path, template_id: str) -> dict[str, Path]:
    return {
        "png": output_dir / f"{template_id}.png",
        "pdf": output_dir / f"{template_id}.pdf",
        "layout": output_dir / f"{template_id}.layout.json",
        "svg": output_dir / f"{template_id}.svg",
        "csv": output_dir / f"{template_id}.csv",
        "md": output_dir / f"{template_id}.md",
    }


def _collect_artifacts(
    paths: dict[str, Path], descriptor: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    required = {str(item) for item in descriptor.get("required_exports", [])}
    if descriptor.get("execution_mode") == "subprocess" or descriptor.get("kind") == "illustration_shell":
        required.add("layout")
    artifacts: dict[str, dict[str, Any]] = {}
    validation_errors: list[str] = []
    for kind, path in paths.items():
        if kind not in required:
            artifacts[kind] = {"applicable": False, "path": None}
            continue
        metadata = _artifact_metadata(path, kind)
        artifacts[kind] = metadata
        if not metadata.get("exists"):
            validation_errors.append(f"missing required {kind} output")
        elif (
            isinstance(metadata.get("execution_issue_candidate"), dict)
            and metadata["execution_issue_candidate"].get("type") == "dependency_unavailable"
        ):
            continue
        elif metadata.get("valid") is not True:
            validation_errors.append(f"invalid required {kind} output")
        elif metadata.get("confirmed_blank") is True:
            validation_errors.append(
                f"{kind.upper()} content inspection confirms a blank required output"
            )
    return artifacts, validation_errors


def _artifact_dependency_issue(
    artifacts: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    for metadata in artifacts.values():
        issue = metadata.get("execution_issue_candidate")
        if isinstance(issue, dict) and issue.get("type") == "dependency_unavailable":
            return {**issue, "authority": False}
    return None


def _tail(value: str) -> str:
    return value[-TAIL_CHARS:]


def _dependency_issue(stderr: str) -> dict[str, Any] | None:
    patterns = (
        (r"No module named ['\"]([^'\"]+)", "python_module"),
        (r"there is no package called [\u2018'\"]([^\u2019'\"]+)", "r_package"),
        (r"package or namespace load failed for [\u2018'\"]([^\u2019'\"]+)", "r_package"),
    )
    for pattern, dependency_kind in patterns:
        match = re.search(pattern, stderr, flags=re.IGNORECASE)
        if match:
            return {
                "type": "dependency_unavailable",
                "authority": False,
                "dependency_kind": dependency_kind,
                "dependency": match.group(1),
                "message": _tail(stderr),
            }
    lowered = stderr.lower()
    if "font family not found" in lowered or "unable to start png device" in lowered:
        return {
            "type": "dependency_unavailable",
            "authority": False,
            "dependency_kind": "font_or_render_device",
            "dependency": "font_or_render_device",
            "message": _tail(stderr),
        }
    return None


def _execution_result_update(
    *,
    exit_code: int,
    stderr: str,
    artifacts: dict[str, dict[str, Any]],
    validation_errors: list[str],
) -> dict[str, Any]:
    def render_failure(reason: str, message: str) -> dict[str, Any]:
        return {
            "status": "render_failed",
            "execution_issue_candidate": {
                "type": "render_failed",
                "authority": False,
                "reason": reason,
                "message": message,
            },
        }

    if any(metadata.get("confirmed_blank") is True for metadata in artifacts.values()):
        return render_failure(
            "artifact_validation_failed",
            "; ".join(validation_errors)
            or "content inspection confirms a blank required output",
        )
    if exit_code != 0:
        dependency = _dependency_issue(stderr)
        if dependency is not None:
            return {
                "status": "dependency_unavailable",
                "execution_issue_candidate": dependency,
            }
        return render_failure(
            "renderer_exit_nonzero", _tail(stderr) or f"renderer exited {exit_code}"
        )
    if validation_errors:
        return render_failure("artifact_validation_failed", "; ".join(validation_errors))
    artifact_dependency_issue = _artifact_dependency_issue(artifacts)
    if artifact_dependency_issue is not None:
        return {
            "status": "dependency_unavailable",
            "execution_issue_candidate": artifact_dependency_issue,
        }
    return {"status": "passed"}


def _python_plugin_command(request_path: Path, template_id: str) -> list[str]:
    return [
        sys.executable,
        str(Path(__file__).resolve()),
        "--_run-python-plugin",
        template_id,
        "--request",
        str(request_path),
    ]


def _run_python_plugin(template_id: str, request_path: Path) -> int:
    request = _read_json(request_path)
    pack_root = Path(request["pack_root"])
    source_root = pack_root / "src"
    sys.path.insert(0, str(source_root))
    module_name, function_name = str(request["entrypoint"]).split(":", 1)
    renderer = getattr(importlib.import_module(module_name), function_name)
    payload = request["display_payload"]
    output_paths = {key: Path(value) for key, value in request["output_paths"].items()}
    full_template_id = str(request["full_template_id"])
    kind = str(request["kind"])
    if kind == "table_shell":
        response = renderer(
            template_id=full_template_id,
            payload_path=Path(request["source_payload_path"]),
            payload=payload,
            output_md_path=output_paths["md"],
            output_csv_path=output_paths["csv"],
        )
    elif kind == "illustration_shell":
        response = renderer(
            template_id=full_template_id,
            shell_payload=payload,
            render_context={"render_mode": "candidate", "authority": False, "publication_ready": False},
            output_svg_path=output_paths["svg"],
            output_png_path=output_paths["png"],
            output_layout_path=output_paths["layout"],
            payload_path=Path(request["source_payload_path"]),
        )
    else:
        raise ValueError(f"unsupported python plugin kind: {kind}")
    print(json.dumps(response, sort_keys=True))
    return 0


def _run_one(
    entry: dict[str, Any], *, pack_root: Path, repo_root: Path, temporary_root: Path
) -> dict[str, Any]:
    template_id = str(entry["template_id"])
    started = time.monotonic()
    result: dict[str, Any] = {
        "template_id": template_id,
        "kind": entry.get("kind"),
        "renderer_family": entry.get("renderer_family"),
        "execution_mode": entry.get("execution_mode"),
        "status": "render_failed",
        "authority": False,
        "publication_ready": False,
        "command": None,
        "exit_code": None,
        "stdout_tail": "",
        "stderr_tail": "",
        "artifacts": {},
    }
    try:
        descriptor_path, descriptor = _load_descriptor(entry, repo_root)
        input_path = _repo_ref(repo_root, str(entry["example_input_ref"]))
        receipt_path = _repo_ref(repo_root, str(entry["example_render_receipt_ref"]))
        example = _read_json(input_path)
        adapter_id, display_payload = _adapt_fixed_input(template_id, example)
        output_dir = temporary_root / template_id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_paths = _output_paths(output_dir, template_id)
        request = {
            "short_template_id": template_id,
            "template_id": descriptor.get("full_template_id", template_id),
            "full_template_id": descriptor.get("full_template_id", template_id),
            "kind": descriptor["kind"],
            "entrypoint": descriptor["entrypoint"],
            "display_payload": display_payload,
            "source_payload_path": str(input_path),
            "output_png_path": str(output_paths["png"]),
            "output_pdf_path": str(output_paths["pdf"]),
            "layout_sidecar_path": str(output_paths["layout"]),
            "output_paths": {key: str(value) for key, value in output_paths.items()},
            "pack_root": str(pack_root),
            "authority": False,
            "publication_ready": False,
        }
        request_path = output_dir / f"{template_id}.request.json"
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result.update(
            {
                "adapter_id": adapter_id,
                "descriptor_ref": str(descriptor_path.relative_to(repo_root)),
                "descriptor_sha256": _sha256(descriptor_path),
                "example_input_ref": str(input_path.relative_to(repo_root)),
                "example_input_sha256": _sha256(input_path),
                "example_render_receipt_ref": str(receipt_path.relative_to(repo_root)),
                "example_render_receipt_sha256": _sha256(receipt_path),
                "request_sha256": _sha256(request_path),
                "temporary_output_policy": "ephemeral_no_repo_write",
            }
        )

        execution_mode = str(descriptor["execution_mode"])
        if execution_mode == "subprocess" and descriptor.get("renderer_family") == "r_ggplot2":
            rscript = shutil.which("Rscript")
            command = [
                rscript or "Rscript",
                str(pack_root / "render.R"),
                "--template",
                template_id,
                "--mode",
                "candidate",
                "--request",
                str(request_path),
            ]
            result["command"] = command
            if rscript is None:
                result.update(
                    {
                        "status": "dependency_unavailable",
                        "execution_issue_candidate": {
                            "type": "dependency_unavailable",
                            "authority": False,
                            "dependency_kind": "runtime_binary",
                            "dependency": "Rscript",
                            "message": "Rscript was not found on PATH; the engine does not install runtime dependencies.",
                        },
                    }
                )
                result["artifacts"], _ = _collect_artifacts(output_paths, descriptor)
                return result
        elif execution_mode == "python_plugin":
            command = _python_plugin_command(request_path, template_id)
            result["command"] = command
        else:
            result.update(
                {
                    "status": "render_failed",
                    "execution_issue_candidate": {
                        "type": "render_failed",
                        "authority": False,
                        "reason": "unsupported_execution_mode",
                        "message": f"unsupported renderer_family/execution_mode: {descriptor.get('renderer_family')}/{execution_mode}",
                    },
                }
            )
            result["artifacts"], _ = _collect_artifacts(output_paths, descriptor)
            return result

        if "png" in descriptor.get("required_exports", []):
            try:
                _pillow_modules()
            except ModuleNotFoundError as exc:
                result.update(
                    {
                        "status": "dependency_unavailable",
                        "execution_issue_candidate": {
                            "type": "dependency_unavailable",
                            "authority": False,
                            "dependency_kind": "python_module",
                            "dependency": "Pillow",
                            "message": str(exc),
                        },
                    }
                )
                result["artifacts"], _ = _collect_artifacts(output_paths, descriptor)
                return result

        environment = os.environ.copy()
        source_root = str(pack_root / "src")
        environment["PYTHONPATH"] = source_root + (
            os.pathsep + environment["PYTHONPATH"] if environment.get("PYTHONPATH") else ""
        )
        try:
            completed = subprocess.run(
                command,
                cwd=output_dir,
                env=environment,
                capture_output=True,
                text=True,
                timeout=RENDER_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            result.update(
                {
                    "status": "render_failed",
                    "stdout_tail": _tail(str(exc.stdout or "")),
                    "stderr_tail": _tail(str(exc.stderr or "")),
                    "execution_issue_candidate": {
                        "type": "render_failed",
                        "authority": False,
                        "reason": "timeout",
                        "message": f"renderer exceeded {RENDER_TIMEOUT_SECONDS} seconds",
                    },
                }
            )
            result["artifacts"], _ = _collect_artifacts(output_paths, descriptor)
            return result

        result.update(
            {
                "exit_code": completed.returncode,
                "stdout_tail": _tail(completed.stdout),
                "stderr_tail": _tail(completed.stderr),
            }
        )
        artifacts, validation_errors = _collect_artifacts(output_paths, descriptor)
        result["artifacts"] = artifacts
        result.update(
            _execution_result_update(
                exit_code=completed.returncode,
                stderr=completed.stderr,
                artifacts=artifacts,
                validation_errors=validation_errors,
            )
        )
    except (KeyError, OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        result.update(
            {
                "status": "render_failed",
                "execution_issue_candidate": {
                    "type": "render_failed",
                    "authority": False,
                    "reason": "fixed_input_or_contract_invalid",
                    "message": str(exc),
                },
            }
        )
    finally:
        result["duration_seconds"] = round(time.monotonic() - started, 3)
    return result


def run_live_regression(
    *,
    template_ids: Sequence[str] | None = None,
    pack_root: Path = PACK_ROOT,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    manifest = load_golden_manifest(pack_root)
    entries = [dict(item) for item in manifest["golden_templates"]]
    available = {str(item["template_id"]): item for item in entries}
    selected_ids = list(template_ids or available)
    unknown = [item for item in selected_ids if item not in available]
    if unknown:
        raise ValueError(f"unknown golden template(s): {', '.join(unknown)}")

    started_at = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix="medical-display-live-regression-") as temporary:
        temporary_root = Path(temporary)
        results = [
            _run_one(available[template_id], pack_root=pack_root, repo_root=repo_root, temporary_root=temporary_root)
            for template_id in selected_ids
        ]
        temporary_output_root = str(temporary_root)

    counts = {
        status: sum(item["status"] == status for item in results)
        for status in ("passed", "dependency_unavailable", "render_failed")
    }
    if counts["render_failed"]:
        state = "failed"
    elif counts["dependency_unavailable"]:
        state = "dependency_unavailable"
    else:
        state = "passed"
    return {
        "schema_version": 1,
        "engine_id": ENGINE_ID,
        "state": state,
        "execution_candidate": True,
        "authority": False,
        "publication_ready": False,
        "can_claim_artifact_authority": False,
        "can_sign_owner_receipt": False,
        "can_create_typed_blocker": False,
        "started_at": started_at,
        "manifest_ref": str((pack_root / "golden_manifest.json").relative_to(repo_root)),
        "manifest_sha256": _sha256(pack_root / "golden_manifest.json"),
        "selected_template_ids": selected_ids,
        "temporary_output_root": temporary_output_root,
        "temporary_outputs_retained": False,
        "summary": {
            "total": len(results),
            "passed": counts["passed"],
            "dependency_unavailable": counts["dependency_unavailable"],
            "render_failed": counts["render_failed"],
        },
        "results": results,
    }


def _write_self_check_png(path: Path) -> None:
    Image, _ = _pillow_modules()
    image = Image.new("RGBA", (2, 2), "white")
    image.putpixel((0, 1), (0, 0, 0, 255))
    image.putpixel((1, 1), (220, 20, 60, 255))
    image.save(path, format="PNG")


def run_self_check(pack_root: Path = PACK_ROOT, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    checks: list[str] = []
    manifest = load_golden_manifest(pack_root)
    entries = manifest["golden_templates"]
    if len(entries) != 6:
        raise ValueError(f"self-check expected 6 golden templates, found {len(entries)}")
    examples: dict[str, dict[str, Any]] = {}
    for entry in entries:
        template_id = str(entry["template_id"])
        input_path = _repo_ref(repo_root, str(entry["example_input_ref"]))
        examples[template_id] = _read_json(input_path)
        adapter_id, payload = _adapt_fixed_input(template_id, examples[template_id])
        if not adapter_id or not isinstance(payload, dict):
            raise ValueError(f"fixed-input adapter failed for {template_id}")
    missing_auc = dict(examples["roc_curve_binary"])
    missing_auc.pop("auc")
    try:
        _adapt_fixed_input("roc_curve_binary", missing_auc)
    except ValueError:
        pass
    else:
        raise ValueError("ROC fixed-input adapter must not invent a missing AUC")
    missing_log_rank = dict(examples["kaplan_meier_grouped"])
    missing_log_rank.pop("log_rank_p")
    try:
        _adapt_fixed_input("kaplan_meier_grouped", missing_log_rank)
    except ValueError:
        pass
    else:
        raise ValueError("Kaplan-Meier adapter must not invent a missing log-rank p value")
    checks.append("six_fixed_input_adapters")

    with tempfile.TemporaryDirectory(prefix="medical-display-live-regression-self-check-") as temporary:
        root = Path(temporary)

        def fixture(name: str, value: str | bytes) -> Path:
            path = root / name
            if isinstance(value, bytes):
                path.write_bytes(value)
            else:
                path.write_text(value, encoding="utf-8")
            return path

        png_path = root / "check.png"
        sparse_png_path = root / "sparse.png"
        blank_pdf_path = root / "blank.pdf"
        nonblank_pdf_path = root / "nonblank.pdf"
        mixed_pdf_path = root / "mixed.pdf"
        _write_self_check_png(png_path)
        Image, _ = _pillow_modules()
        sparse = Image.new("RGB", (2048, 2048), "white")
        sparse.putpixel((1024, 1024), (0, 0, 0))
        sparse.save(sparse_png_path, format="PNG")
        blank_page = Image.new("RGB", (64, 64), "white")
        nonblank_page = blank_page.copy()
        nonblank_page.putpixel((32, 32), (0, 0, 0))
        blank_page.save(blank_pdf_path, format="PDF")
        nonblank_page.save(nonblank_pdf_path, format="PDF")
        blank_page.save(
            mixed_pdf_path,
            format="PDF",
            save_all=True,
            append_images=[nonblank_page],
        )
        truncated_pdf_path = fixture("truncated.pdf", b"%PDF-1.7\n")
        layout_path = fixture(
            "check.layout.json",
            json.dumps(
                {
                    "template_id": "self_check",
                    "device": {"x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 1.0},
                    "layout_boxes": [
                        {
                            "box_id": "panel",
                            "x0": 0.1,
                            "y0": 0.1,
                            "x1": 0.9,
                            "y1": 0.9,
                        }
                    ],
                }
            )
            + "\n",
        )
        empty_layout_path = fixture("empty.layout.json", "{}\n")
        svg_paths = {
            "visible": fixture(
                "visible.svg",
                '<svg xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1"/><text>label</text></svg>\n',
            ),
            "empty": fixture("empty.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>\n'),
            "definitely_empty": fixture(
                "definitely-empty.svg",
                '<svg xmlns="http://www.w3.org/2000/svg" xmlns:x="urn:example">'
                '<rect width="0" height="1"/><path d=""/><image width="1" height="1"/>'
                '<x:rect width="1" height="1"/></svg>\n',
            ),
            "uncertain": fixture(
                "uncertain.svg",
                '<svg xmlns="http://www.w3.org/2000/svg"><rect width="calc(1px)" '
                'height="var(--height)" style="opacity:var(--opacity)"/></svg>\n',
            ),
            "deep": fixture(
                "deep.svg",
                '<svg xmlns="http://www.w3.org/2000/svg">'
                + "<g>" * 1100
                + '<rect width="1" height="1"/>'
                + "</g>" * 1100
                + "</svg>\n",
            ),
        }
        truncated_svg_path = fixture("truncated.svg", "<svg")
        text_paths = {
            "csv": (fixture("check.csv", "name,value\nexample,1\n"), "csv"),
            "blank_csv": (fixture("blank.csv", " \n\t"), "csv"),
            "md": (fixture("check.md", "# Example\n"), "md"),
            "blank_md": (fixture("blank.md", b"\xef\xbb\xbf\n \t"), "md"),
            "nul_md": (fixture("nul.md", b"\x00"), "md"),
            "invalid_md": (fixture("invalid.md", b"\xff\xfe"), "md"),
        }

        png = _inspect_png(png_path)
        sparse_png = _inspect_png(sparse_png_path)
        blank_pdf = _inspect_pdf(blank_pdf_path)
        nonblank_pdf = _inspect_pdf(nonblank_pdf_path)
        mixed_pdf = _inspect_pdf(mixed_pdf_path)
        layout = _inspect_layout(layout_path)
        svg_metadata = {name: _artifact_metadata(path, "svg") for name, path in svg_paths.items()}
        text_metadata = {
            name: _artifact_metadata(path, kind) for name, (path, kind) in text_paths.items()
        }

        content_failures: list[str] = []

        def expect(condition: bool, message: str) -> None:
            if not condition:
                content_failures.append(message)

        expect(
            png["width"] == 2 and png["height"] == 2 and png["content_density"] > 0,
            "PNG inspection failed",
        )
        expect(sparse_png["confirmed_blank"] is False, "sparse PNG was classified blank")
        expect(_inspect_pdf(truncated_pdf_path)["valid"] is False, "corrupt PDF was accepted")
        expect(layout["parse_ok"] is True, "layout inspection failed")
        for invalid_path, inspector in (
            (empty_layout_path, _inspect_layout),
            (truncated_svg_path, _inspect_svg),
        ):
            try:
                inspector(invalid_path)
            except ValueError:
                pass
            else:
                content_failures.append(f"invalid artifact was accepted: {invalid_path.name}")

        pdf_issue = blank_pdf.get("execution_issue_candidate")
        if pdf_issue is not None:
            expect(
                blank_pdf.get("valid") is None
                and pdf_issue.get("type") == "dependency_unavailable"
                and pdf_issue.get("authority") is False,
                "missing PyMuPDF was not a non-authoritative dependency issue",
            )
        else:
            expect(blank_pdf.get("confirmed_blank") is True, "uniform PDF was not blank")
            expect(nonblank_pdf.get("confirmed_blank") is False, "sparse PDF was blank")
            expect(mixed_pdf.get("confirmed_blank_pages") == [1], "PDF blank pages were wrong")

        for name, expected_blank in (
            ("visible", False),
            ("empty", True),
            ("definitely_empty", True),
            ("uncertain", False),
            ("deep", False),
        ):
            expect(
                svg_metadata[name].get("confirmed_blank") is expected_blank,
                f"SVG {name} blank classification failed",
            )
        for name, expected_valid, expected_blank in (
            ("csv", True, False),
            ("blank_csv", True, True),
            ("md", True, False),
            ("blank_md", True, True),
            ("nul_md", False, None),
            ("invalid_md", False, None),
        ):
            metadata = text_metadata[name]
            expect(metadata.get("valid") is expected_valid, f"text {name} validity failed")
            if expected_blank is not None:
                expect(
                    metadata.get("confirmed_blank") is expected_blank,
                    f"text {name} blank classification failed",
                )

        _, blank_errors = _collect_artifacts(
            {
                "svg": svg_paths["empty"],
                "csv": text_paths["blank_csv"][0],
                "md": text_paths["blank_md"][0],
            },
            {"required_exports": ["svg", "csv", "md"]},
        )
        expect(len(blank_errors) == 3, "required non-PNG blanks did not all fail collection")
        if content_failures:
            raise ValueError(
                "artifact content inspection self-check failed: "
                + "; ".join(content_failures)
            )
    checks.append("artifact_content_inspection")

    issue = _dependency_issue("ModuleNotFoundError: No module named 'example_dependency'")
    if issue is None or issue.get("type") != "dependency_unavailable":
        raise ValueError("dependency classification self-check failed")
    artifact_issue = _artifact_dependency_issue(
        {
            "pdf": {
                "execution_issue_candidate": {
                    "type": "dependency_unavailable",
                    "authority": True,
                    "dependency": "PyMuPDF",
                }
            }
        }
    )
    if (
        artifact_issue is None
        or artifact_issue.get("type") != "dependency_unavailable"
        or artifact_issue.get("authority") is not False
    ):
        raise ValueError("artifact dependency projection self-check failed")
    blank_over_dependency = _execution_result_update(
        exit_code=1,
        stderr="ModuleNotFoundError: No module named 'renderer_dependency'",
        artifacts={"pdf": {"confirmed_blank": True}},
        validation_errors=["PDF content inspection confirms a blank required output"],
    )
    missing_under_dependency = _execution_result_update(
        exit_code=1,
        stderr="ModuleNotFoundError: No module named 'renderer_dependency'",
        artifacts={"pdf": {"exists": False}},
        validation_errors=["missing required pdf output"],
    )
    if (
        blank_over_dependency.get("status") != "render_failed"
        or blank_over_dependency.get("execution_issue_candidate", {}).get("reason")
        != "artifact_validation_failed"
        or missing_under_dependency.get("status") != "dependency_unavailable"
    ):
        raise ValueError("blank/dependency priority self-check failed")
    checks.append("non_authoritative_dependency_classification")
    return {
        "schema_version": 1,
        "engine_id": ENGINE_ID,
        "state": "passed",
        "self_check": True,
        "checks": checks,
        "authority": False,
        "publication_ready": False,
        "can_create_typed_blocker": False,
    }


def _print_human(report: dict[str, Any]) -> None:
    if report.get("self_check"):
        print(f"live regression self-check: {report['state']} ({', '.join(report['checks'])})")
        return
    if "summary" not in report:
        issue = report.get("execution_issue_candidate", "unknown execution issue")
        message = issue.get("message", str(issue)) if isinstance(issue, dict) else str(issue)
        print(f"live regression: {report['state']} ({message})")
        return
    summary = report["summary"]
    print(
        "live regression: "
        f"{report['state']} "
        f"passed={summary['passed']} "
        f"dependency_unavailable={summary['dependency_unavailable']} "
        f"render_failed={summary['render_failed']}"
    )
    for item in report["results"]:
        print(f"- {item['template_id']}: {item['status']}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run fixed-input medical display live regression candidates.")
    parser.add_argument("--check", action="store_true", help="Render selected golden templates in a temporary directory.")
    parser.add_argument("--template", action="append", default=[], help="Limit live regression to one golden template; repeatable.")
    parser.add_argument("--json", action="store_true", help="Print the structured report as JSON.")
    parser.add_argument("--_run-python-plugin", dest="python_plugin", help=argparse.SUPPRESS)
    parser.add_argument("--request", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.python_plugin:
        if not args.request:
            parser.error("--_run-python-plugin requires --request")
        return _run_python_plugin(args.python_plugin, Path(args.request))

    try:
        report = (
            run_live_regression(template_ids=args.template or None)
            if args.check or args.template
            else run_self_check()
        )
    except ModuleNotFoundError as exc:
        report = {
            "schema_version": 1,
            "engine_id": ENGINE_ID,
            "state": "dependency_unavailable",
            "authority": False,
            "publication_ready": False,
            "can_create_typed_blocker": False,
            "execution_issue_candidate": {
                "type": "dependency_unavailable",
                "authority": False,
                "dependency_kind": "python_module",
                "dependency": "Pillow",
                "message": str(exc),
            },
        }
    except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        report = {
            "schema_version": 1,
            "engine_id": ENGINE_ID,
            "state": "failed",
            "authority": False,
            "publication_ready": False,
            "can_create_typed_blocker": False,
            "execution_issue_candidate": {
                "type": "self_check_or_contract_invalid",
                "authority": False,
                "message": str(exc),
            },
        }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_human(report)
    if report["state"] == "passed":
        return 0
    if report["state"] == "dependency_unavailable":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
