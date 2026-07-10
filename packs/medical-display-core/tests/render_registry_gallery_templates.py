#!/usr/bin/env python3
"""Pack-level render regression for current registry/gallery evidence templates."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


PACK_ROOT = Path(__file__).resolve().parents[1]
RENDERER = PACK_ROOT / "render.R"

COMMON_PAYLOAD = {
    "preview_only": True,
    "authority": False,
    "publication_ready": False,
    "source_data_digest": "gallery-synthetic-preview",
    "render_context": {
        "layout_override": {"show_figure_title": True},
    },
}

CASES = {
    "dot_range_summary_panel": {
        "purpose": "bmi_stratified_descriptive_prevalence_dot_range_summary",
        "payload": {
            "title": "BMI-stratified phenotype prevalence",
            "x_label": "Participants with measure-defined phenotype (%)",
            "y_label": "BMI category",
            "size_scale_label": "Available n",
            "rows": [
                {"bmi_category": "18.5-22.9", "measure": "Elevated waist", "positive_n": 31, "available_n": 120, "percent": 25.8},
                {"bmi_category": "23.0-24.9", "measure": "Elevated waist", "positive_n": 48, "available_n": 110, "percent": 43.6},
                {"bmi_category": "25.0-29.9", "measure": "Elevated waist", "positive_n": 76, "available_n": 105, "percent": 72.4},
                {"bmi_category": ">=30.0", "measure": "Elevated waist", "positive_n": 72, "available_n": 82, "percent": 87.8},
                {"bmi_category": "18.5-22.9", "measure": "Elevated WHR", "positive_n": 27, "available_n": 118, "percent": 22.9},
                {"bmi_category": "23.0-24.9", "measure": "Elevated WHR", "positive_n": 43, "available_n": 108, "percent": 39.8},
                {"bmi_category": "25.0-29.9", "measure": "Elevated WHR", "positive_n": 69, "available_n": 101, "percent": 68.3},
                {"bmi_category": ">=30.0", "measure": "Elevated WHR", "positive_n": 66, "available_n": 80, "percent": 82.5},
            ],
            "render_context": {"layout_override": {"show_figure_title": True, "output_width_in": 8.4, "output_height_in": 4.3}},
        },
    },
    "availability_bar_panel": {
        "purpose": "registry_measure_availability_with_denominator_audit",
        "payload": {
            "title": "Availability of registry phenotype measures",
            "x_label": "Available participants (%)",
            "y_label": "Registry measure",
            "rows": [
                {"measure": "BMI", "available_n": 512, "denominator_n": 520, "percent": 98.5},
                {"measure": "Waist circumference", "available_n": 468, "denominator_n": 520, "percent": 90.0},
                {"measure": "Waist-to-hip ratio", "available_n": 431, "denominator_n": 520, "percent": 82.9},
                {"measure": "PHQ-9", "available_n": 394, "denominator_n": 520, "percent": 75.8},
                {"measure": "GAD-7", "available_n": 381, "denominator_n": 520, "percent": 73.3},
            ],
            "render_context": {"layout_override": {"show_figure_title": True, "output_width_in": 7.2, "output_height_in": 3.8}},
        },
    },
    "adult_multidimensional_phenotype_heatmap": {
        "purpose": "adult_bmi_stratified_multidimensional_phenotype_heatmap",
        "heatmap": True,
        "payload": {
            "title": "Adult multidimensional phenotype profile",
            "x_label": "BMI category",
            "y_label": "Phenotype feature",
            "heatmap_scale_label": "Within-feature relative level",
            "cells": [
                {"bmi_category": bmi, "feature": feature, "unit": unit, "median": value, "available_n": 96 - index}
                for index, (bmi, values) in enumerate(
                    [
                        ("18.5-22.9", (78.0, 0.83, 4.0)),
                        ("23.0-24.9", (84.0, 0.88, 5.0)),
                        ("25.0-29.9", (92.0, 0.94, 6.0)),
                        (">=30.0", (101.0, 1.01, 7.0)),
                    ]
                )
                for feature, unit, value in zip(
                    ("Waist circumference", "Waist-to-hip ratio", "PHQ-9"),
                    ("cm", "ratio", "score"),
                    values,
                    strict=True,
                )
            ],
            "render_context": {"layout_override": {"show_figure_title": True, "output_width_in": 7.2, "output_height_in": 4.2}},
        },
    },
    "xiangya_psychobehavioral_overlap_heatmap": {
        "purpose": "psychobehavioral_symptom_overlap_row_percentage_heatmap",
        "heatmap": True,
        "payload": {
            "title": "Psychobehavioral symptom overlap",
            "x_label": "GAD-7 status",
            "y_label": "PHQ-9 status",
            "heatmap_scale_label": "Row percentage (%)",
            "cells": [
                {"phq9_status": "Below threshold", "gad7_status": "Below threshold", "count": 242, "row_percent": 78.1},
                {"phq9_status": "Below threshold", "gad7_status": "Above threshold", "count": 68, "row_percent": 21.9},
                {"phq9_status": "Above threshold", "gad7_status": "Below threshold", "count": 51, "row_percent": 43.6},
                {"phq9_status": "Above threshold", "gad7_status": "Above threshold", "count": 66, "row_percent": 56.4},
            ],
            "render_context": {"layout_override": {"show_figure_title": True, "output_width_in": 4.6, "output_height_in": 2.8}},
        },
    },
    "adult_bmi_waist_central_adiposity_bar": {
        "purpose": "central_adiposity_prevalence_across_adult_bmi_categories",
        "payload": {
            "title": "Central adiposity across adult BMI categories",
            "x_label": "BMI category",
            "y_label": "Central adiposity prevalence (%)",
            "rows": [
                {"bmi_category": "18.5-22.9", "central_obesity_percent": 18.6, "available_n": 118, "central_obesity_n": 22},
                {"bmi_category": "23.0-24.9", "central_obesity_percent": 38.2, "available_n": 110, "central_obesity_n": 42},
                {"bmi_category": "25.0-29.9", "central_obesity_percent": 69.5, "available_n": 105, "central_obesity_n": 73},
                {"bmi_category": ">=30.0", "central_obesity_percent": 88.8, "available_n": 80, "central_obesity_n": 71},
            ],
            "render_context": {"layout_override": {"show_figure_title": True, "output_width_in": 5.8, "output_height_in": 3.4}},
        },
    },
}


def run_case(template_id: str, case: dict, output_root: Path) -> list[str]:
    case_root = output_root / template_id
    case_root.mkdir(parents=True, exist_ok=True)
    output_png = case_root / f"{template_id}.png"
    output_pdf = case_root / f"{template_id}.pdf"
    output_layout = case_root / f"{template_id}.layout.json"
    request_path = case_root / f"{template_id}.request.json"
    payload = COMMON_PAYLOAD | case["payload"]
    request = {
        "short_template_id": template_id,
        "display_payload": payload,
        "output_png_path": str(output_png),
        "output_pdf_path": str(output_pdf),
        "layout_sidecar_path": str(output_layout),
    }
    request_path.write_text(json.dumps(request, indent=2), encoding="utf-8")
    command = [
        "Rscript",
        str(RENDERER),
        "--template",
        template_id,
        "--mode",
        "candidate",
        "--request",
        str(request_path),
    ]
    completed = subprocess.run(command, cwd=PACK_ROOT, text=True, capture_output=True, check=False)
    errors = []
    if completed.returncode != 0:
        return [f"renderer exited {completed.returncode}: {completed.stderr.strip()}"]
    if output_png.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        errors.append("PNG signature missing")
    if not output_pdf.read_bytes().startswith(b"%PDF-"):
        errors.append("PDF signature missing")
    layout = json.loads(output_layout.read_text(encoding="utf-8"))
    if layout.get("template_id") != template_id:
        errors.append("layout template_id mismatch")
    metrics = layout.get("metrics", {})
    if metrics.get("renderer_family") != "r_ggplot2":
        errors.append("layout renderer_family mismatch")
    if metrics.get("figure_purpose") != case["purpose"]:
        errors.append("layout figure_purpose mismatch")
    if metrics.get("source_data_digest") != "gallery-synthetic-preview":
        errors.append("layout synthetic source_data_digest missing")
    if metrics.get("preview_only") is not True:
        errors.append("layout preview_only must be true")
    if metrics.get("authority") is not False:
        errors.append("layout authority must be false")
    if metrics.get("publication_ready") is not False:
        errors.append("layout publication_ready must be false")
    if not layout.get("panel_boxes"):
        errors.append("layout panel_boxes missing")
    if case.get("heatmap") and not any(box.get("box_type") == "colorbar" for box in layout.get("guide_boxes", [])):
        errors.append("heatmap colorbar box missing")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.output_dir:
        output_root = args.output_dir.resolve()
        output_root.mkdir(parents=True, exist_ok=True)
        cleanup = None
    else:
        cleanup = tempfile.TemporaryDirectory(prefix="medical-display-gallery-regression-")
        output_root = Path(cleanup.name)
    failures = {}
    for template_id, case in CASES.items():
        errors = run_case(template_id, case, output_root)
        if errors:
            failures[template_id] = errors
    if cleanup is not None:
        cleanup.cleanup()
    if failures:
        print(json.dumps({"ok": False, "failures": failures}, indent=2))
        return 1
    print(json.dumps({"ok": True, "templates": sorted(CASES), "output_root": str(output_root)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
