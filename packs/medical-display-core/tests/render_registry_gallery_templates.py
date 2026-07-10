#!/usr/bin/env python3
"""Pack-level render regression for Gallery fixture and specialist R dispatch."""

from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


PACK_ROOT = Path(__file__).resolve().parents[1]
RENDERER = PACK_ROOT / "render.R"
FIXTURE_PATH = PACK_ROOT / "fixtures" / "registry_gallery_cases.json"
EXPECTED_CASE_IDS = {
    "adult_bmi_waist_central_adiposity_bar",
    "adult_multidimensional_phenotype_heatmap",
    "availability_bar_panel",
    "dot_range_summary_panel",
    "xiangya_psychobehavioral_overlap_heatmap",
}
COHORT_DEPENDENCY_UNAVAILABLE_MARKER = (
    "cohort_flow_figure requires prepared R package `ggconsort` >= 0.1.0 "
    "with exported `create_consort_data`"
)


def load_cases() -> dict[str, dict[str, Any]]:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if fixture.get("schema_version") != 1:
        raise ValueError("registry Gallery fixture schema_version must be 1")
    if fixture.get("fixture_id") != "fenggaolab.org.medical-display-core.registry-gallery-cases.v1":
        raise ValueError("registry Gallery fixture_id is invalid")
    if fixture.get("state") != "active_fictional_refs_only_gallery_preview":
        raise ValueError("registry Gallery fixture must remain a fictional refs-only preview")
    authority = fixture.get("authority_boundary") or {}
    for field in (
        "authority",
        "publication_ready",
        "can_write_study_truth",
        "can_sign_owner_receipt",
    ):
        if authority.get(field) is not False:
            raise ValueError(f"registry Gallery fixture must keep {field}=false")
    cases = fixture.get("cases")
    if not isinstance(cases, dict) or set(cases) != EXPECTED_CASE_IDS:
        raise ValueError("registry Gallery fixture must contain the exact five template cases")
    for template_id, case in cases.items():
        payload = case.get("payload") if isinstance(case, dict) else None
        if not isinstance(payload, dict):
            raise ValueError(f"{template_id} fixture payload must be an object")
        if payload.get("template_id") != template_id:
            raise ValueError(f"{template_id} fixture payload template_id mismatch")
        if payload.get("preview_only") is not True:
            raise ValueError(f"{template_id} fixture must keep preview_only=true")
        if payload.get("authority") is not False or payload.get("publication_ready") is not False:
            raise ValueError(f"{template_id} fixture must remain non-authoritative")
        if payload.get("source_data_digest") != "gallery-synthetic-preview":
            raise ValueError(f"{template_id} fixture must declare the synthetic source digest")
        if not str(case.get("figure_purpose") or "").strip():
            raise ValueError(f"{template_id} fixture must declare figure_purpose")
    return cases


def output_paths(case_root: Path, template_id: str) -> dict[str, Path]:
    return {
        "png": case_root / f"{template_id}.png",
        "pdf": case_root / f"{template_id}.pdf",
        "layout": case_root / f"{template_id}.layout.json",
        "request": case_root / f"{template_id}.request.json",
    }


def run_renderer(
    template_id: str,
    payload: dict[str, Any],
    case_root: Path,
    *,
    dependency_environment: dict[str, Any] | None = None,
) -> tuple[subprocess.CompletedProcess[str], dict[str, Path]]:
    case_root.mkdir(parents=True, exist_ok=True)
    paths = output_paths(case_root, template_id)
    request: dict[str, Any] = {
        "short_template_id": template_id,
        "display_payload": payload,
        "output_png_path": str(paths["png"]),
        "output_pdf_path": str(paths["pdf"]),
        "layout_sidecar_path": str(paths["layout"]),
    }
    if dependency_environment is not None:
        request["dependency_environment"] = dependency_environment
    paths["request"].write_text(json.dumps(request, indent=2), encoding="utf-8")
    completed = subprocess.run(
        [
            "Rscript",
            str(RENDERER),
            "--template",
            template_id,
            "--mode",
            "candidate",
            "--request",
            str(paths["request"]),
        ],
        cwd=case_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed, paths


def output_errors(paths: dict[str, Path]) -> tuple[list[str], dict[str, Any] | None]:
    errors: list[str] = []
    if not paths["png"].is_file() or paths["png"].read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        errors.append("PNG signature missing")
    if not paths["pdf"].is_file() or not paths["pdf"].read_bytes().startswith(b"%PDF-"):
        errors.append("PDF signature missing")
    layout = None
    if not paths["layout"].is_file():
        errors.append("layout sidecar missing")
    else:
        layout = json.loads(paths["layout"].read_text(encoding="utf-8"))
    return errors, layout


def rplots_error(case_root: Path) -> list[str]:
    return ["renderer created unexpected Rplots.pdf"] if (case_root / "Rplots.pdf").exists() else []


def run_case(template_id: str, case: dict[str, Any], output_root: Path) -> list[str]:
    case_root = output_root / "registry" / template_id
    completed, paths = run_renderer(template_id, case["payload"], case_root)
    if completed.returncode != 0:
        return [f"renderer exited {completed.returncode}: {completed.stderr.strip()}"]
    errors, layout = output_errors(paths)
    errors.extend(rplots_error(case_root))
    if layout is None:
        return errors
    if layout.get("template_id") != template_id:
        errors.append("layout template_id mismatch")
    metrics = layout.get("metrics", {})
    if metrics.get("renderer_family") != "r_ggplot2":
        errors.append("layout renderer_family mismatch")
    if metrics.get("figure_purpose") != case["figure_purpose"]:
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
    if case.get("heatmap") and not any(
        box.get("box_type") == "colorbar" for box in layout.get("guide_boxes", [])
    ):
        errors.append("heatmap colorbar box missing")
    return errors


def invalid_payload_cases(cases: dict[str, dict[str, Any]]) -> list[tuple[str, str, dict[str, Any], str]]:
    checks: list[tuple[str, str, dict[str, Any], str]] = []

    dot_payload = copy.deepcopy(cases["dot_range_summary_panel"]["payload"])
    dot_payload["rows"][0]["percent"] = 90.0
    checks.append((
        "dot_range_count_percent_conflict",
        "dot_range_summary_panel",
        dot_payload,
        "percent must match positive_n/available_n",
    ))

    availability_payload = copy.deepcopy(cases["availability_bar_panel"]["payload"])
    availability_payload["rows"][0]["percent"] = 10.0
    checks.append((
        "availability_count_percent_conflict",
        "availability_bar_panel",
        availability_payload,
        "percent must match available_n/denominator_n",
    ))

    adiposity_payload = copy.deepcopy(cases["adult_bmi_waist_central_adiposity_bar"]["payload"])
    adiposity_payload["rows"][0]["central_obesity_percent"] = 75.0
    checks.append((
        "adiposity_count_percent_conflict",
        "adult_bmi_waist_central_adiposity_bar",
        adiposity_payload,
        "central_obesity_percent must match central_obesity_n/available_n",
    ))

    overlap_payload = copy.deepcopy(cases["xiangya_psychobehavioral_overlap_heatmap"]["payload"])
    overlap_payload["cells"][0]["row_percent"] = 70.0
    overlap_payload["cells"][1]["row_percent"] = 30.0
    checks.append((
        "overlap_count_row_percent_conflict",
        "xiangya_psychobehavioral_overlap_heatmap",
        overlap_payload,
        "row_percent must match the percentage derived from same-row counts",
    ))

    heatmap_payload = copy.deepcopy(cases["adult_multidimensional_phenotype_heatmap"]["payload"])
    heatmap_payload["cells"][3]["unit"] = "mm"
    checks.append((
        "multidimensional_feature_unit_conflict",
        "adult_multidimensional_phenotype_heatmap",
        heatmap_payload,
        "must use exactly one unit per feature",
    ))
    return checks


def run_invalid_case(
    check_id: str,
    template_id: str,
    payload: dict[str, Any],
    expected_error: str,
    output_root: Path,
) -> list[str]:
    case_root = output_root / "invalid" / check_id
    completed, _ = run_renderer(template_id, payload, case_root)
    errors = rplots_error(case_root)
    if completed.returncode == 0:
        errors.append("invalid payload rendered successfully")
    if expected_error not in completed.stderr:
        errors.append(f"missing expected error: {expected_error}")
    return errors


def heatmap_group_comparison_payload() -> dict[str, Any]:
    example = json.loads(
        (PACK_ROOT / "templates" / "heatmap_group_comparison" / "example_input.json").read_text(
            encoding="utf-8"
        )
    )
    row_labels = example["row_labels"]
    column_labels = example["column_labels"]
    cells = [
        {"x": column_labels[column_index], "y": row_labels[row_index], "value": value}
        for row_index, row in enumerate(example["matrix"])
        for column_index, value in enumerate(row)
    ]
    return {
        **example,
        "title": "Group comparison heatmap",
        "x_label": "Group",
        "y_label": "Marker",
        "cells": cells,
        "row_order": [{"label": item} for item in row_labels],
        "column_order": [{"label": item} for item in column_labels],
    }


def run_null_device_regression(output_root: Path) -> list[str]:
    case_root = output_root / "null-device" / "heatmap_group_comparison"
    completed, paths = run_renderer(
        "heatmap_group_comparison",
        heatmap_group_comparison_payload(),
        case_root,
    )
    if completed.returncode != 0:
        return [f"renderer exited {completed.returncode}: {completed.stderr.strip()}"]
    errors, _ = output_errors(paths)
    errors.extend(rplots_error(case_root))
    return errors


def cohort_flow_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "shell_id": "cohort_flow_figure",
        "display_id": "Gallery-Cohort-Flow",
        "title": "Cohort derivation and analysis sets",
        "caption": "Fictional reporting-flow regression preview only.",
        "layout_mode": "participant_flow",
        "steps": [
            {"step_id": "source", "label": "Source records", "n": 1200},
            {"step_id": "eligible", "label": "Eligible records", "n": 980},
            {"step_id": "analysis", "label": "Analysis cohort", "n": 920},
        ],
        "exclusions": [
            {
                "exclusion_id": "incomplete",
                "from_step_id": "source",
                "label": "Incomplete baseline data",
                "n": 220,
            }
        ],
        "render_context": {
            "layout_override": {
                "output_width_in": 6.1,
                "output_height_in": 5.8,
            }
        },
    }


def run_cohort_flow_regression(output_root: Path) -> tuple[list[str], str]:
    dependency_environment = {
        "status": "gallery_preview",
        "run_context_ref": "fixture:cohort-flow-regression",
        "run_context_fingerprint": "sha256:fictional-cohort-flow-regression",
    }
    case_root = output_root / "cohort-flow" / "valid"
    completed, paths = run_renderer(
        "cohort_flow_figure",
        cohort_flow_payload(),
        case_root,
        dependency_environment=dependency_environment,
    )
    if completed.returncode != 0:
        if COHORT_DEPENDENCY_UNAVAILABLE_MARKER in completed.stderr:
            if os.environ.get("OPL_RUNTIME_ENVIRONMENT_STATUS") == "prepared":
                return [
                    "prepared runtime reported ggconsort dependency_unavailable: "
                    f"{completed.stderr.strip()}"
                ], "render_failed"
            return [], "dependency_unavailable"
        return [f"renderer exited {completed.returncode}: {completed.stderr.strip()}"], "render_failed"
    errors, layout = output_errors(paths)
    errors.extend(rplots_error(case_root))
    metrics = (layout or {}).get("metrics", {})
    if metrics.get("uses_ggconsort") is not True:
        errors.append("cohort flow layout must record uses_ggconsort=true")
    if metrics.get("renderer_family") != "r_ggplot2":
        errors.append("cohort flow renderer_family mismatch")
    if metrics.get("source_renderer") != "MAS/ReportingFlow::cohort_flow_figure":
        errors.append("cohort flow source_renderer mismatch")

    missing_receipt_root = output_root / "cohort-flow" / "missing-receipt"
    missing_receipt, _ = run_renderer(
        "cohort_flow_figure",
        cohort_flow_payload(),
        missing_receipt_root,
    )
    errors.extend(rplots_error(missing_receipt_root))
    if missing_receipt.returncode == 0:
        errors.append("cohort flow rendered without prepared dependency receipt")
    expected = "requires OPL prepared dependency_environment receipt"
    if expected not in missing_receipt.stderr:
        errors.append(f"cohort flow missing-receipt error must contain: {expected}")
    return errors, "r_ggplot2_ggconsort"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    try:
        cases = load_cases()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "fixture_error": str(exc)}, indent=2))
        return 1
    if args.output_dir:
        output_root = args.output_dir.resolve()
        output_root.mkdir(parents=True, exist_ok=True)
        cleanup = None
    else:
        cleanup = tempfile.TemporaryDirectory(prefix="medical-display-gallery-regression-")
        output_root = Path(cleanup.name)
    failures: dict[str, list[str]] = {}
    for template_id, case in cases.items():
        errors = run_case(template_id, case, output_root)
        if errors:
            failures[template_id] = errors
    for check in invalid_payload_cases(cases):
        errors = run_invalid_case(*check, output_root)
        if errors:
            failures[check[0]] = errors
    null_device_errors = run_null_device_regression(output_root)
    if null_device_errors:
        failures["null_device_Rplots"] = null_device_errors
    cohort_errors, cohort_flow_dispatch = run_cohort_flow_regression(output_root)
    if cohort_errors:
        failures["cohort_flow_figure"] = cohort_errors
    if cleanup is not None:
        cleanup.cleanup()
    if failures:
        print(json.dumps({"ok": False, "failures": failures}, indent=2))
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "fixture_ref": str(FIXTURE_PATH.relative_to(PACK_ROOT)),
                "templates": sorted(cases),
                "negative_contract_checks": len(invalid_payload_cases(cases)),
                "cohort_flow_dispatch": cohort_flow_dispatch,
                "null_device_Rplots": False,
                "output_root": str(output_root),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
