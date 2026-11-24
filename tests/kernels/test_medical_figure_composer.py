"""Extracted pytest suite for skills/medical-figure-composer/kernel.py."""

from __future__ import annotations

from copy import deepcopy
import math

from tests.kernels._loader import load_kernel

KERNEL = load_kernel("medical-figure-composer")
_sample_outline = KERNEL._sample_outline
clone_outline = KERNEL.clone_outline
compose_crops = KERNEL.compose_crops
compose_figure = KERNEL.compose_figure
composition_layout_findings = KERNEL.composition_layout_findings
composition_review_prompt = KERNEL.composition_review_prompt
composition_review_ref = KERNEL.composition_review_ref
figure_outline_schema = KERNEL.figure_outline_schema
grid_geometry = KERNEL.grid_geometry
panel_box = KERNEL.panel_box
validate_outline = KERNEL.validate_outline

def _self_check(*, include_pillow: bool = False) -> None:
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

    strict_outline = {
        "claim": "Strict geometry.",
        "width_mm": 40,
        "ncol": 2,
        "row_heights_mm": [40, 40],
        "panels": [
            {
                "letter": "a",
                "role": "hero",
                "message": "Panel",
                "row": 0,
                "col": 0,
                "rowspan": 1,
                "colspan": 1,
            }
        ],
    }
    invalid_numeric_outlines = []
    for field, values in {
        "ncol": (2.5, 2.0, True, "2"),
        "width_mm": (0, -1, math.nan, math.inf, 10**400, True, "40"),
    }.items():
        for value in values:
            candidate = deepcopy(strict_outline)
            candidate[field] = value
            invalid_numeric_outlines.append((field, repr(value), candidate))
    for field, values in {
        "row": (0.5, 0.0, True, "0"),
        "col": (0.5, 0.0, True, "0"),
        "rowspan": (1.5, 1.0, True, "1"),
        "colspan": (1.5, 1.0, True, "1"),
    }.items():
        for value in values:
            candidate = deepcopy(strict_outline)
            candidate["panels"][0][field] = value
            invalid_numeric_outlines.append((field, repr(value), candidate))
    for value in ([0], [-1], [math.nan], [math.inf], [True], ["40"]):
        candidate = deepcopy(strict_outline)
        candidate["row_heights_mm"] = value
        invalid_numeric_outlines.append(("row_heights_mm", repr(value), candidate))
    empty_rows = deepcopy(strict_outline)
    empty_rows["row_heights_mm"] = []
    empty_rows["panels"] = []
    invalid_numeric_outlines.append(("row_heights_mm", "[]", empty_rows))
    zero_columns = deepcopy(strict_outline)
    zero_columns["ncol"] = 0
    zero_columns["panels"] = []
    invalid_numeric_outlines.append(("ncol", "0", zero_columns))

    rejection_failures = []

    def check_rejected(label: str, value: str, operation) -> None:
        try:
            operation()
        except ValueError as exc:
            if label not in str(exc):
                rejection_failures.append(
                    f"{label}={value} raised ValueError without field context: {exc}"
                )
        except Exception as exc:
            rejection_failures.append(
                f"{label}={value} raised {type(exc).__name__}, expected ValueError"
            )
        else:
            rejection_failures.append(f"{label}={value} was accepted")

    for field, value, candidate in invalid_numeric_outlines:
        check_rejected(field, value, lambda candidate=candidate: validate_outline(candidate))

    for value in (0, -1, math.nan, math.inf, True, "300"):
        check_rejected("dpi", repr(value), lambda value=value: grid_geometry(outline, dpi=value))
    for value in (-1, math.nan, math.inf, True, "4"):
        check_rejected(
            "gutter_mm",
            repr(value),
            lambda value=value: grid_geometry(outline, gutter_mm=value),
        )

    zero_width_box = deepcopy(outline)
    zero_width_box["width_mm"] = 1
    check_rejected(
        "pixel",
        "zero-width box",
        lambda: panel_box(zero_width_box, "a", dpi=25.4, gutter_mm=4),
    )
    zero_height_box = deepcopy(outline)
    zero_height_box["row_heights_mm"][0] = 0.01
    check_rejected(
        "pixel",
        "zero-height box",
        lambda: panel_box(zero_height_box, "a", dpi=1, gutter_mm=0),
    )
    overflow_width = deepcopy(outline)
    overflow_width["width_mm"] = 1e308
    check_rejected(
        "pixel",
        "overflow width",
        lambda: grid_geometry(overflow_width, dpi=300),
    )
    overflow_height = deepcopy(outline)
    overflow_height["row_heights_mm"][0] = 1e308
    check_rejected(
        "pixel",
        "overflow row height",
        lambda: grid_geometry(overflow_height, dpi=300),
    )
    check_rejected(
        "pixel",
        "overflow dpi",
        lambda: grid_geometry(outline, dpi=1e308),
    )
    check_rejected(
        "pixel",
        "overflow gutter",
        lambda: grid_geometry(outline, gutter_mm=1e308),
    )
    assert not rejection_failures, "\n".join(rejection_failures)

    outline_properties = figure_outline_schema()["properties"]
    assert outline_properties["width_mm"]["exclusiveMinimum"] == 0
    assert outline_properties["ncol"]["minimum"] == 1
    assert outline_properties["row_heights_mm"]["minItems"] == 1
    assert outline_properties["row_heights_mm"]["items"]["exclusiveMinimum"] == 0
    panel_properties = outline_properties["panels"]["items"]["properties"]
    assert panel_properties["row"]["minimum"] == 0
    assert panel_properties["col"]["minimum"] == 0
    assert panel_properties["rowspan"]["minimum"] == 1
    assert panel_properties["colspan"]["minimum"] == 1

    if not include_pillow:
        return

    from pathlib import Path
    from tempfile import TemporaryDirectory

    try:
        from PIL import Image
    except ModuleNotFoundError as exc:
        raise RuntimeError("Pillow is required for the image-composition self-check") from exc

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


def test_medical_figure_composer_core() -> None:
    _self_check(include_pillow=False)
