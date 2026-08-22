from __future__ import annotations

from pathlib import Path


def _prepare_python_illustration_output_paths(
    *,
    output_png_path: Path,
    output_svg_path: Path,
    layout_sidecar_path: Path,
) -> None:
    output_png_path.parent.mkdir(parents=True, exist_ok=True)
    output_svg_path.parent.mkdir(parents=True, exist_ok=True)
    layout_sidecar_path.parent.mkdir(parents=True, exist_ok=True)
