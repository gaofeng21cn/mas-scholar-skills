"""Deterministic helpers for the medical-figure-style skill.

These helpers support refs-only style review. They do not redraw data,
mutate artifacts, or decide publication quality.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence


DEFAULT_FOCAL_COLOR = "#0072B2"
DEFAULT_MUTED_COLOR = "#B8B8B8"
DEFAULT_STYLE_RCPARAMS = {
    "font.family": "sans-serif",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "legend.fontsize": 7,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "axes.linewidth": 0.6,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.frameon": False,
    "figure.dpi": 200,
    "savefig.dpi": 300,
    "savefig.bbox": None,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
}


def matplotlib_style_rcparams(
    *, frame: str = "open", font: str | None = None, grid: bool = False
) -> dict[str, object]:
    """Return rcParams for a restrained publication style."""
    if frame not in {"open", "boxed", "none"}:
        raise ValueError("frame must be 'open', 'boxed', or 'none'")
    boxed = frame == "boxed"
    rc = dict(DEFAULT_STYLE_RCPARAMS)
    rc.update(
        {
            "axes.spines.top": boxed,
            "axes.spines.right": boxed,
            "axes.spines.left": frame != "none",
            "axes.spines.bottom": frame != "none",
            "axes.grid": bool(grid),
        }
    )
    if font:
        rc["font.sans-serif"] = [font, "DejaVu Sans"]
    return rc


def apply_matplotlib_style(**kwargs: object) -> dict[str, object]:
    """Apply :func:`matplotlib_style_rcparams` when matplotlib is installed."""
    import matplotlib as mpl

    rc = matplotlib_style_rcparams(**kwargs)
    mpl.rcParams.update(rc)
    return rc


def set_frame(ax: object, style: str = "open") -> object:
    """Set matplotlib axes spines to ``open``, ``boxed``, or ``none``."""
    if style not in {"open", "boxed", "none"}:
        raise ValueError("style must be 'open', 'boxed', or 'none'")
    visible = {
        "open": {"left", "bottom"},
        "boxed": {"left", "bottom", "right", "top"},
        "none": set(),
    }[style]
    for side, spine in ax.spines.items():
        spine.set_visible(side in visible)
        if side in visible:
            spine.set_linewidth(0.6)
    ax.tick_params(direction="out", length=0 if style == "none" else 3, width=0.6)
    return ax


def _hex_to_rgb(color: str) -> tuple[float, float, float]:
    value = color.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"expected #RRGGBB color, got {color!r}")
    return tuple(int(value[i : i + 2], 16) / 255 for i in (0, 2, 4))


def _rgb_to_hex(rgb: Sequence[float]) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02X}" for c in rgb)


def _mix_with_gray(color: str, amount: float = 0.7) -> str:
    r, g, b = _hex_to_rgb(color)
    mean = (r + g + b) / 3
    return _rgb_to_hex(
        (
            (1 - amount) * r + amount * mean,
            (1 - amount) * g + amount * mean,
            (1 - amount) * b + amount * mean,
        )
    )


def focal_palette(
    labels: Sequence[str],
    focal: str | Iterable[str],
    *,
    focal_color: str = DEFAULT_FOCAL_COLOR,
    base_colors: Sequence[str] | None = None,
    other: str = "muted",
) -> dict[str, str]:
    """Map labels to colors with the focal item(s) visually dominant."""
    focal_set = {focal} if isinstance(focal, str) else set(focal)
    if not focal_set.intersection(labels):
        raise ValueError("at least one focal label must be present in labels")
    if other not in {"muted", "gray", "ordinal"}:
        raise ValueError("other must be 'muted', 'gray', or 'ordinal'")
    colors = list(base_colors or ["#4C78A8", "#F58518", "#54A24B", "#B279A2"])
    palette: dict[str, str] = {}
    non_focal = [label for label in labels if label not in focal_set]
    for index, label in enumerate(labels):
        if label in focal_set:
            palette[label] = focal_color
        elif other == "gray":
            palette[label] = DEFAULT_MUTED_COLOR
        elif other == "ordinal":
            step = 0 if len(non_focal) <= 1 else non_focal.index(label) / (len(non_focal) - 1)
            shade = 0.78 - 0.3 * step
            palette[label] = _rgb_to_hex((shade, shade, shade))
        else:
            palette[label] = _mix_with_gray(colors[index % len(colors)])
    return palette


def panel_letter_plan(
    letters: int | Sequence[str],
    *,
    case: str = "lower",
    x: float = -0.16,
    y: float = 1.03,
) -> list[dict[str, object]]:
    """Return a matplotlib-ready panel-letter placement plan."""
    if case not in {"lower", "upper"}:
        raise ValueError("case must be 'lower' or 'upper'")
    raw = [chr(97 + i) for i in range(letters)] if isinstance(letters, int) else list(letters)
    return [
        {
            "letter": letter.lower() if case == "lower" else letter.upper(),
            "x": x,
            "y": y,
            "transform": "axes",
            "fontweight": "bold",
            "ha": "left",
            "va": "bottom",
        }
        for letter in raw
    ]


def crop_box_ref(
    letter: str,
    bounds_px: Sequence[int],
    *,
    pad_px: int = 4,
    image_size_px: Sequence[int] | None = None,
) -> dict[str, object]:
    """Return a padded crop-box ref skeleton for visual QA."""
    x0, y0, x1, y1 = map(int, bounds_px)
    box = (x0 - pad_px, y0 - pad_px, x1 + pad_px, y1 + pad_px)
    if image_size_px:
        width, height = map(int, image_size_px)
        box = (max(0, box[0]), max(0, box[1]), min(width, box[2]), min(height, box[3]))
    return {"letter": letter, "box_px": box, "ref_kind": "panel_crop_box_ref"}


def contrast_ratio(foreground: str, background: str = "#FFFFFF") -> float:
    """Return WCAG contrast ratio for two hex colors."""

    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    def luminance(color: str) -> float:
        r, g, b = (channel(c) for c in _hex_to_rgb(color))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    first, second = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (first + 0.05) / (second + 0.05)


def lint_readability(
    items: Sequence[Mapping[str, object]],
    *,
    background: str = "#FFFFFF",
    min_contrast: float = 3.0,
    min_font_pt: float = 6.0,
) -> list[dict[str, object]]:
    """Return lightweight contrast/font findings for rendered-label metadata."""
    findings = []
    for item in items:
        label = str(item.get("label", ""))
        color = str(item.get("color", "#000000"))
        font_pt = float(item.get("font_pt", min_font_pt))
        ratio = contrast_ratio(color, background)
        if ratio < min_contrast:
            findings.append(
                {
                    "severity": "major",
                    "label": label,
                    "finding": "low_contrast",
                    "contrast_ratio": round(ratio, 2),
                    "minimum": min_contrast,
                }
            )
        if font_pt < min_font_pt:
            findings.append(
                {
                    "severity": "major",
                    "label": label,
                    "finding": "font_too_small",
                    "font_pt": font_pt,
                    "minimum": min_font_pt,
                }
            )
    return findings


def _self_check() -> None:
    assert matplotlib_style_rcparams(frame="boxed")["axes.spines.top"] is True
    assert matplotlib_style_rcparams()["savefig.bbox"] is None
    assert focal_palette(["A", "B"], "A")["A"] == DEFAULT_FOCAL_COLOR
    assert panel_letter_plan(2, case="upper")[1]["letter"] == "B"
    assert crop_box_ref("a", (10, 10, 20, 20), image_size_px=(24, 24))["box_px"] == (6, 6, 24, 24)
    assert contrast_ratio("#000000", "#FFFFFF") > 20
    assert lint_readability([{"label": "n", "color": "#BBBBBB", "font_pt": 5}])


if __name__ == "__main__":
    _self_check()
    print("medical-figure-style kernel self-check passed")
