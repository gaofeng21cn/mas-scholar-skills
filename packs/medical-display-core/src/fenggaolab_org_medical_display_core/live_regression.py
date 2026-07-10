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
    return {
        "valid": signature_valid and eof_present and startxref_present,
        "header": header.decode("latin-1", errors="replace"),
        "signature_valid": signature_valid,
        "eof_present": eof_present,
        "startxref_present": startxref_present,
        "validation_depth": "pdf_signature_eof_and_cross_reference_structure",
    }


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
    local_name = root.tag.rsplit("}", 1)[-1].lower()
    return {
        "valid": local_name == "svg",
        "root_element": local_name,
        "child_count": len(root),
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
        elif metadata.get("valid") is not True:
            validation_errors.append(f"invalid required {kind} output")
        elif kind == "png" and metadata.get("confirmed_blank") is True:
            validation_errors.append("PNG full-resolution inspection confirms a blank render")
    return artifacts, validation_errors


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
        if completed.returncode != 0:
            dependency = _dependency_issue(completed.stderr)
            if dependency is not None:
                result.update(
                    {
                        "status": "dependency_unavailable",
                        "execution_issue_candidate": dependency,
                    }
                )
            else:
                result.update(
                    {
                        "status": "render_failed",
                        "execution_issue_candidate": {
                            "type": "render_failed",
                            "authority": False,
                            "reason": "renderer_exit_nonzero",
                            "message": _tail(completed.stderr) or f"renderer exited {completed.returncode}",
                        },
                    }
                )
        elif validation_errors:
            result.update(
                {
                    "status": "render_failed",
                    "execution_issue_candidate": {
                        "type": "render_failed",
                        "authority": False,
                        "reason": "artifact_validation_failed",
                        "message": "; ".join(validation_errors),
                    },
                }
            )
        else:
            result["status"] = "passed"
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
        png_path = root / "check.png"
        sparse_png_path = root / "sparse.png"
        pdf_path = root / "check.pdf"
        truncated_pdf_path = root / "truncated.pdf"
        layout_path = root / "check.layout.json"
        empty_layout_path = root / "empty.layout.json"
        svg_path = root / "check.svg"
        truncated_svg_path = root / "truncated.svg"
        _write_self_check_png(png_path)
        Image, _ = _pillow_modules()
        sparse = Image.new("RGB", (2048, 2048), "white")
        sparse.putpixel((1024, 1024), (0, 0, 0))
        sparse.save(sparse_png_path, format="PNG")
        Image.new("RGB", (16, 16), "white").save(pdf_path, format="PDF")
        truncated_pdf_path.write_bytes(b"%PDF-1.7\n")
        layout_path.write_text(
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
            encoding="utf-8",
        )
        empty_layout_path.write_text("{}\n", encoding="utf-8")
        svg_path.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1"/></svg>\n',
            encoding="utf-8",
        )
        truncated_svg_path.write_text("<svg", encoding="utf-8")
        png = _inspect_png(png_path)
        sparse_png = _inspect_png(sparse_png_path)
        pdf = _inspect_pdf(pdf_path)
        layout = _inspect_layout(layout_path)
        svg = _inspect_svg(svg_path)
        if png["width"] != 2 or png["height"] != 2 or png["content_density"] <= 0:
            raise ValueError("PNG inspection self-check failed")
        if sparse_png["confirmed_blank"] is not False:
            raise ValueError("sparse nonblank PNG must not be classified as blank")
        if pdf["valid"] is not True or _inspect_pdf(truncated_pdf_path)["valid"] is not False:
            raise ValueError("PDF structural inspection self-check failed")
        if layout["parse_ok"] is not True or svg["valid"] is not True:
            raise ValueError("layout/SVG inspection self-check failed")
        for invalid_path, inspector in (
            (empty_layout_path, _inspect_layout),
            (truncated_svg_path, _inspect_svg),
        ):
            try:
                inspector(invalid_path)
            except ValueError:
                pass
            else:
                raise ValueError(f"invalid artifact was accepted: {invalid_path.name}")
    checks.append("pillow_artifact_inspection")

    issue = _dependency_issue("ModuleNotFoundError: No module named 'example_dependency'")
    if issue is None or issue.get("type") != "dependency_unavailable":
        raise ValueError("dependency classification self-check failed")
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
