"""Deterministic helpers for the medical-figure-composer skill.

These helpers assemble already rendered panels and prepare refs-only review
prompts. They do not redraw data, mutate source panels, or decide publication
quality.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Mapping, Sequence


def figure_outline_schema() -> dict[str, object]:
    """Return the minimal schema expected by the composer helpers."""
    return {
        "type": "object",
        "required": ["claim", "width_mm", "ncol", "row_heights_mm", "panels"],
        "properties": {
            "claim": {"type": "string"},
            "width_mm": {"type": "number"},
            "ncol": {"type": "integer"},
            "row_heights_mm": {"type": "array", "items": {"type": "number"}},
            "panels": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["letter", "role", "message", "row", "col", "colspan"],
                    "properties": {
                        "letter": {"type": "string"},
                        "role": {"type": "string"},
                        "message": {"type": "string"},
                        "row": {"type": "integer"},
                        "col": {"type": "integer"},
                        "rowspan": {"type": "integer"},
                        "colspan": {"type": "integer"},
                        "panel_ref": {"type": "string"},
                        "fit_mode": {
                            "type": "string",
                            "enum": ["contain", "crop"],
                            "default": "contain",
                        },
                    },
                },
            },
        },
    }


def _panel_fit_mode(panel: Mapping[str, object]) -> str:
    fit_mode = str(panel.get("fit_mode", "contain"))
    if fit_mode not in {"contain", "crop"}:
        raise ValueError(f"invalid fit_mode for panel {panel.get('letter', '?')}: {fit_mode}")
    return fit_mode


def validate_outline(outline: Mapping[str, object]) -> None:
    """Raise ``ValueError`` for geometry that cannot be composed."""
    required = {"claim", "width_mm", "ncol", "row_heights_mm", "panels"}
    missing = required - set(outline)
    if missing:
        raise ValueError(f"outline missing required keys: {sorted(missing)}")
    ncol = int(outline["ncol"])
    row_count = len(outline["row_heights_mm"])
    seen: set[str] = set()
    occupied: dict[tuple[int, int], str] = {}
    for panel in outline["panels"]:
        letter = str(panel["letter"])
        _panel_fit_mode(panel)
        if letter in seen:
            raise ValueError(f"duplicate panel letter: {letter}")
        seen.add(letter)
        row = int(panel["row"])
        col = int(panel["col"])
        rowspan = int(panel.get("rowspan", 1))
        colspan = int(panel["colspan"])
        if row < 0 or col < 0 or rowspan < 1 or colspan < 1:
            raise ValueError(f"invalid panel geometry for {letter}")
        if row + rowspan > row_count or col + colspan > ncol:
            raise ValueError(f"panel {letter} exceeds outline grid")
        for grid_row in range(row, row + rowspan):
            for grid_col in range(col, col + colspan):
                cell = (grid_row, grid_col)
                if cell in occupied:
                    raise ValueError(
                        f"panel {letter} overlaps panel {occupied[cell]} "
                        f"at row {grid_row} col {grid_col}"
                    )
                occupied[cell] = letter


def grid_geometry(
    outline: Mapping[str, object], *, dpi: int = 300, gutter_mm: float = 4.0
) -> dict[str, object]:
    """Return deterministic pixel geometry for an outline grid."""
    validate_outline(outline)
    scale = dpi / 25.4
    width_px = int(round(float(outline["width_mm"]) * scale))
    gutter_px = int(round(gutter_mm * scale))
    ncol = int(outline["ncol"])
    col_width_px = (width_px - gutter_px * (ncol - 1)) // ncol
    row_heights_px = [int(round(float(h) * scale)) for h in outline["row_heights_mm"]]
    row_y_px = [sum(row_heights_px[:i]) + gutter_px * i for i in range(len(row_heights_px))]
    height_px = row_y_px[-1] + row_heights_px[-1] if row_heights_px else 0
    return {
        "width_px": width_px,
        "height_px": height_px,
        "ncol": ncol,
        "col_width_px": col_width_px,
        "row_heights_px": row_heights_px,
        "row_y_px": row_y_px,
        "gutter_px": gutter_px,
        "dpi": dpi,
    }


def _panel(outline: Mapping[str, object], letter: str) -> Mapping[str, object]:
    for panel in outline["panels"]:
        if panel["letter"] == letter:
            return panel
    raise KeyError(f"unknown panel letter: {letter}")


def panel_box(
    outline: Mapping[str, object], letter: str, *, dpi: int = 300, gutter_mm: float = 4.0
) -> tuple[int, int, int, int]:
    """Return ``(x0, y0, x1, y1)`` in composed-image pixels."""
    geom = grid_geometry(outline, dpi=dpi, gutter_mm=gutter_mm)
    panel = _panel(outline, letter)
    row = int(panel["row"])
    col = int(panel["col"])
    rowspan = int(panel.get("rowspan", 1))
    colspan = int(panel["colspan"])
    gutter = int(geom["gutter_px"])
    col_width = int(geom["col_width_px"])
    x0 = col * (col_width + gutter)
    y0 = geom["row_y_px"][row]
    width = col_width * colspan + gutter * (colspan - 1)
    height = sum(geom["row_heights_px"][row : row + rowspan]) + gutter * (rowspan - 1)
    return (x0, y0, x0 + width, y0 + height)


def panel_boxes(
    outline: Mapping[str, object], *, dpi: int = 300, gutter_mm: float = 4.0
) -> dict[str, tuple[int, int, int, int]]:
    """Return panel boxes keyed by letter."""
    return {
        panel["letter"]: panel_box(outline, panel["letter"], dpi=dpi, gutter_mm=gutter_mm)
        for panel in outline["panels"]
    }


def compose_crops(
    outline: Mapping[str, object],
    *,
    dpi: int = 300,
    gutter_mm: float = 4.0,
    pad_px: int = 4,
) -> dict[str, tuple[int, int, int, int]]:
    """Return padded crop boxes for composed-panel review."""
    geom = grid_geometry(outline, dpi=dpi, gutter_mm=gutter_mm)
    crops = {}
    for letter, (x0, y0, x1, y1) in panel_boxes(outline, dpi=dpi, gutter_mm=gutter_mm).items():
        crops[letter] = (
            max(0, x0 - pad_px),
            max(0, y0 - pad_px),
            min(int(geom["width_px"]), x1 + pad_px),
            min(int(geom["height_px"]), y1 + pad_px),
        )
    return crops


def compose_figure(
    outline: Mapping[str, object],
    panel_paths: Mapping[str, str],
    out_path: str,
    *,
    dpi: int = 300,
    gutter_mm: float = 4.0,
    letter_case: str = "lower",
) -> tuple[str, tuple[int, int]]:
    """Compose existing panel images with optional Pillow."""
    from PIL import Image, ImageDraw, ImageFont, ImageOps

    if letter_case not in {"lower", "upper"}:
        raise ValueError("letter_case must be 'lower' or 'upper'")
    geom = grid_geometry(outline, dpi=dpi, gutter_mm=gutter_mm)
    canvas = Image.new("RGB", (int(geom["width_px"]), int(geom["height_px"])), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", int(9 / 72 * dpi))
    except OSError:
        font = ImageFont.load_default()
    for panel in outline["panels"]:
        letter = panel["letter"]
        if letter not in panel_paths:
            raise KeyError(f"missing panel path for {letter}")
        x0, y0, x1, y1 = panel_box(outline, letter, dpi=dpi, gutter_mm=gutter_mm)
        fit_mode = _panel_fit_mode(panel)
        with Image.open(panel_paths[letter]) as source:
            image = source.convert("RGBA")
        target_size = (x1 - x0, y1 - y0)
        if image.size != target_size:
            resize = ImageOps.fit if fit_mode == "crop" else ImageOps.contain
            image = resize(image, target_size, method=Image.Resampling.LANCZOS)
        paste_at = (x0 + (target_size[0] - image.width) // 2, y0 + (target_size[1] - image.height) // 2)
        canvas.paste(image, paste_at, image)
        stamp = letter.lower() if letter_case == "lower" else letter.upper()
        draw.text((x0 + int(1.5 / 25.4 * dpi), y0 + int(1 / 25.4 * dpi)), stamp, fill="black", font=font)
    canvas.save(out_path)
    return out_path, canvas.size


def composition_layout_findings(
    outline: Mapping[str, object],
    panel_paths: Mapping[str, str],
    *,
    dpi: int = 300,
    gutter_mm: float = 4.0,
    minimum_panel_mm: float = 35.0,
) -> list[dict[str, object]]:
    """Return refs-only physical-size and aspect-ratio findings for each panel."""
    from PIL import Image

    validate_outline(outline)
    boxes = panel_boxes(outline, dpi=dpi, gutter_mm=gutter_mm)
    findings = []
    for panel in outline["panels"]:
        letter = str(panel["letter"])
        if letter not in panel_paths:
            raise KeyError(f"missing panel path for {letter}")
        x0, y0, x1, y1 = boxes[letter]
        target_width = x1 - x0
        target_height = y1 - y0
        physical_width_mm = round(target_width * 25.4 / dpi, 3)
        physical_height_mm = round(target_height * 25.4 / dpi, 3)
        warning_codes = []
        if physical_width_mm < minimum_panel_mm:
            warning_codes.append("panel_width_below_minimum")
        if physical_height_mm < minimum_panel_mm:
            warning_codes.append("panel_height_below_minimum")
        with Image.open(panel_paths[letter]) as source:
            source_width, source_height = source.size
        findings.append(
            {
                "finding_kind": "composition_layout_finding",
                "authority": False,
                "panel_letter": letter,
                "panel_ref": panel.get("panel_ref", letter),
                "fit_mode": _panel_fit_mode(panel),
                "physical_width_mm": physical_width_mm,
                "physical_height_mm": physical_height_mm,
                "source_aspect_ratio": round(source_width / source_height, 6),
                "target_aspect_ratio": round(target_width / target_height, 6),
                "minimum_panel_mm": minimum_panel_mm,
                "severity": "warning" if warning_codes else "info",
                "warning_codes": warning_codes,
                "blocks_progress": False,
            }
        )
    return findings


def composition_review_prompt(
    composite_ref: str,
    outline: Mapping[str, object],
    *,
    previous_ref: str | None = None,
) -> str:
    """Build a compact composite-review prompt skeleton."""
    rows = [
        f"- {p['letter']}: {p.get('role', 'panel')} at row {p['row']} col {p['col']} "
        f"span {p.get('rowspan', 1)}x{p['colspan']} - {p.get('message', '')}"
        for p in outline["panels"]
    ]
    previous = f"\nPrevious composite for regression check: {previous_ref}" if previous_ref else ""
    return (
        "Review this existing-panel composite as a refs-only composition hint.\n"
        f"Composite: {composite_ref}{previous}\n"
        f"Claim: {outline['claim']}\n"
        "Check panel order, letters, gutters, resized text, crop-level consistency, "
        "and route back any panel-level evidence/render defect.\n"
        "Panels:\n"
        + "\n".join(rows)
    )


def composition_review_ref(
    outline: Mapping[str, object], composite_ref: str, findings: Sequence[Mapping[str, object]]
) -> dict[str, object]:
    """Return the refs-only review skeleton for downstream owner consumption."""
    return {
        "ref_kind": "figure_composition_review_ref",
        "authority": False,
        "claim": outline["claim"],
        "composite_ref": composite_ref,
        "panel_refs": [p.get("panel_ref", p["letter"]) for p in outline["panels"]],
        "findings": list(findings),
        "owner_gate_target": "MAS/domain owner visual review",
    }


def clone_outline(outline: Mapping[str, object]) -> dict[str, object]:
    """Return a mutable copy for manual outline edits."""
    copied = deepcopy(outline)
    validate_outline(copied)
    return copied


def _sample_outline() -> dict[str, object]:
    return {
        "claim": "Treatment gap concentrates in high-risk patients.",
        "width_mm": 120,
        "ncol": 2,
        "row_heights_mm": [45, 35],
        "panels": [
            {"letter": "a", "role": "hero", "message": "Gap by risk", "row": 0, "col": 0, "colspan": 2},
            {"letter": "b", "role": "supporting", "message": "By age", "row": 1, "col": 0, "colspan": 1},
            {"letter": "c", "role": "supporting", "message": "By site", "row": 1, "col": 1, "colspan": 1},
        ],
    }


def _self_check() -> None:
    from pathlib import Path
    from tempfile import TemporaryDirectory

    from PIL import Image

    outline = _sample_outline()
    fit_schema = figure_outline_schema()["properties"]["panels"]["items"]["properties"]["fit_mode"]
    assert fit_schema == {"type": "string", "enum": ["contain", "crop"], "default": "contain"}
    geom = grid_geometry(outline)
    assert geom["width_px"] == 1417
    assert panel_box(outline, "a") == (0, 0, 1417, 531)
    assert compose_crops(outline)["b"][0] == 0
    assert "refs-only" in composition_review_prompt("figure.png", outline)
    ref = composition_review_ref(outline, "figure.png", [{"severity": "minor"}])
    assert ref["authority"] is False
    assert clone_outline(outline)["panels"][0]["letter"] == "a"

    overlapping = clone_outline(outline)
    overlapping["panels"][2]["col"] = 0
    try:
        validate_outline(overlapping)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("overlapping panels must fail validation")

    invalid_fit = clone_outline(outline)
    invalid_fit["panels"][0]["fit_mode"] = "stretch"
    try:
        validate_outline(invalid_fit)
    except ValueError as exc:
        assert "fit_mode" in str(exc)
    else:
        raise AssertionError("invalid fit_mode must fail validation")

    square_outline = {
        "claim": "Preserve panel aspect ratio.",
        "width_mm": 40,
        "ncol": 1,
        "row_heights_mm": [40],
        "panels": [
            {
                "letter": "a",
                "role": "hero",
                "message": "Wide panel",
                "row": 0,
                "col": 0,
                "colspan": 1,
            }
        ],
    }
    with TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        source_path = temp / "wide.png"
        contain_path = temp / "contain.png"
        red = (220, 20, 60)
        blue = (30, 90, 210)
        source = Image.new("RGB", (200, 100), red)
        source.paste(blue, (75, 25, 125, 75))
        source.save(source_path)
        compose_figure(square_outline, {"a": str(source_path)}, str(contain_path), dpi=25.4)
        with Image.open(contain_path) as contained:
            assert contained.getpixel((20, 5)) == (255, 255, 255)
            red_pixels = [
                (x, y)
                for y in range(contained.height)
                for x in range(contained.width)
                if contained.getpixel((x, y)) == red
            ]
            red_width = max(x for x, _ in red_pixels) - min(x for x, _ in red_pixels) + 1
            red_height = max(y for _, y in red_pixels) - min(y for _, y in red_pixels) + 1
            assert red_width / red_height == 2

        crop_outline = clone_outline(square_outline)
        crop_outline["panels"][0]["fit_mode"] = "crop"
        crop_path = temp / "crop.png"
        compose_figure(crop_outline, {"a": str(source_path)}, str(crop_path), dpi=25.4)
        with Image.open(crop_path) as cropped:
            assert cropped.getpixel((20, 5)) == red
            assert cropped.getpixel((20, 35)) == red
            blue_pixels = [
                (x, y)
                for y in range(cropped.height)
                for x in range(cropped.width)
                if cropped.getpixel((x, y)) == blue
            ]
            blue_width = max(x for x, _ in blue_pixels) - min(x for x, _ in blue_pixels) + 1
            blue_height = max(y for _, y in blue_pixels) - min(y for _, y in blue_pixels) + 1
            assert blue_width == blue_height

        narrow_outline = clone_outline(square_outline)
        narrow_outline["width_mm"] = 30
        finding = composition_layout_findings(
            narrow_outline, {"a": str(source_path)}, dpi=25.4
        )[0]
        assert finding["panel_letter"] == "a"
        assert finding["physical_width_mm"] == 30
        assert finding["physical_height_mm"] == 40
        assert finding["source_aspect_ratio"] == 2
        assert finding["target_aspect_ratio"] == 0.75
        assert finding["fit_mode"] == "contain"
        assert finding["severity"] == "warning"
        assert finding["warning_codes"] == ["panel_width_below_minimum"]
        assert finding["blocks_progress"] is False
        assert finding["authority"] is False


if __name__ == "__main__":
    _self_check()
    print("medical-figure-composer kernel self-check passed")
