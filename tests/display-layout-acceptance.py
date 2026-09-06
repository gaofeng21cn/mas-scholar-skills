#!/usr/bin/env python3
"""Exercise the display CLI using real final exports and measured text extents."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "skills/medical-display-qc/kernel.py"


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="scholar-display-acceptance-") as folder:
        output = Path(folder)
        os.environ["MPLCONFIGDIR"] = str(output / "mpl-cache")
        import matplotlib

        matplotlib.use("Agg")
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure

        figure = Figure(figsize=(6, 4), dpi=150)
        FigureCanvasAgg(figure)
        axes = figure.add_axes((0.12, 0.15, 0.76, 0.7))
        axes.plot([1, 2, 3], [2, 3, 2], color="#126957", marker="o")
        axes.set_axis_off()
        artists = [
            ("label.a", figure.text(0.18, 0.78, "Group A", fontsize=12)),
            ("label.b", figure.text(0.64, 0.70, "Group B", fontsize=12)),
        ]
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        width, height = figure.canvas.get_width_height()
        records = []
        for artist_id, artist in artists:
            bounds = artist.get_window_extent(renderer)
            records.append({
                "artist_id": artist_id,
                "artist_kind": "annotation",
                "lane": "plotting_data",
                "source_text": artist.get_text(),
                "bbox_px": [bounds.x0, height - bounds.y1, bounds.x1, height - bounds.y0],
                "clip_bbox_px": [0, 0, width, height],
            })
        baseline = output / "renderer-baseline.json"
        baseline.write_text(json.dumps({"matplotlib": matplotlib.__version__, "case": "direct-label-regression"}))
        registry = {
            "generation_source_ref": str(Path(__file__).resolve()),
            "semantic_artist_scope": "not_applicable:line_plot",
            "validation_scope": "artifact_acceptance",
            "renderer_baseline_ref": {
                "kind": "renderer_regression_baseline",
                "ref": str(baseline),
                "size_bytes": baseline.stat().st_size,
                "sha256": "sha256:" + hashlib.sha256(baseline.read_bytes()).hexdigest(),
            },
            "annotation_lane_policy": "not_applicable",
            "annotation_lane_reason": "Direct labels on the data canvas; no numeric column",
            "final_canvas": {"width": 6, "height": 4, "unit": "in", "width_px": width, "height_px": height},
            "safe_inset_px": {"left": 12, "right": 12, "top": 12, "bottom": 12},
            "minimum_spacing_px": 6,
            "wrap_policy": "automatic_semantic_wrap",
            "measurement_basis": "renderer_drawn_text_width",
            "export_policy": {"canvas_mode": "fixed", "bbox_inches": None, "tight_crop": False},
            "lanes": {"plotting_data": {"bbox_px": [0, 0, width, height]}},
            "panels": [{"panel_id": "a", "expected_text_artist_ids": [item[0] for item in artists], "text_artists": records}],
        }
        png, pdf = output / "figure.png", output / "figure.pdf"
        figure.savefig(png, dpi=150, bbox_inches=None)
        figure.savefig(pdf, bbox_inches=None, metadata={"CreationDate": None, "ModDate": None})
        sidecar = output / "layout.json"

        def run(candidate: dict, expected_code: int) -> dict:
            sidecar.write_text(json.dumps(candidate))
            result = subprocess.run(
                [sys.executable, str(KERNEL), "--layout-registry", str(sidecar), "--png", str(png), "--pdf", str(pdf)],
                capture_output=True, text=True, check=False,
            )
            assert result.returncode == expected_code, result.stdout + result.stderr
            return json.loads(result.stdout)

        receipt = run(registry, 0)
        assert receipt["machine_check_status"] == "geometry_checks_passed"
        assert receipt["regression_fixture_refs"] == []
        assert set(receipt["lane_bounds_px"]) == {"plotting_data"}
        assert {binding["format"] for binding in receipt["artifact_bindings"]} == {"PNG", "PDF"}
        assert receipt["authority"] is False
        missing_baseline = dict(registry)
        missing_baseline.pop("renderer_baseline_ref")
        assert "renderer_baseline_ref_invalid" in {item["code"] for item in run(missing_baseline, 2)["violations"]}
        overlap = json.loads(json.dumps(registry))
        overlap["panels"][0]["text_artists"][1]["bbox_px"] = records[0]["bbox_px"]
        assert "text_artist_overlap" in {item["code"] for item in run(overlap, 2)["violations"]}
        regression = dict(registry, validation_scope="renderer_regression")
        assert "regression_fixture_ref_missing" in {item["code"] for item in run(regression, 2)["violations"]}
        print("display layout CLI: real PNG/PDF acceptance and 3 negative cases passed")


if __name__ == "__main__":
    main()
