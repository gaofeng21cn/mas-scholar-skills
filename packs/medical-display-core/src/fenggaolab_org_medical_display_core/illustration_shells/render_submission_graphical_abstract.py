from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, PathPatch
from matplotlib.path import Path as MplPath

from ..shared_parts.common import dump_json
from ..shared_parts.flow_layout import _flow_box_to_normalized, _wrap_figure_title_to_width, _wrap_flow_text_to_width
from ..shared_parts.geometry import _bbox_to_layout_box
from ..shared_parts.rendering import _prepare_python_illustration_output_paths
from .render_submission_graphical_abstract_square import _render_square_submission_graphical_abstract


_SOURCE_RENDERER = "scholarskills_pack_graphical_abstract.v2"
_CLINICAL_STORYLINE = "clinical_storyline"


def _read_float(mapping: dict[str, Any], key: str, default: float) -> float:
    value = mapping.get(key, default)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return float(default)


def _resolve_color(mapping: dict[str, Any], key: str, fallback: str) -> str:
    return str(mapping.get(key) or fallback).strip() or fallback


def _first_card(panel: dict[str, Any]) -> dict[str, Any]:
    for row in list(panel.get("rows") or []):
        if not isinstance(row, dict):
            continue
        cards = list(row.get("cards") or [])
        if cards and isinstance(cards[0], dict):
            return dict(cards[0])
    return {"card_id": "stage_message", "value": ""}


def _role_family(panel: dict[str, Any], index: int) -> str:
    role = str(panel.get("visual_role") or panel.get("panel_id") or "").strip().lower()
    if role in {"population", "source_data", "cohort", "study_population", "brief", "claim_evidence"}:
        return "population"
    if role in {"model_signal", "model", "algorithm", "mechanism", "risk_signal", "core_finding"}:
        return "signal"
    if role in {"clinical_use", "decision", "action", "care_path", "clinical_meaning", "follow_up"}:
        return "action"
    return ("population", "signal", "action")[index % 3]


def _draw_population_glyph(
    ax: Any,
    *,
    box: dict[str, float],
    accent: str,
    soft: str,
    ink: str,
) -> None:
    center_x = (box["x0"] + box["x1"]) / 2.0
    baseline = box["y0"] + (box["y1"] - box["y0"]) * 0.22
    positions = (
        (-0.30, 0.10, 0.82),
        (-0.12, 0.24, 1.00),
        (0.08, 0.16, 0.92),
        (0.27, 0.28, 0.78),
        (-0.22, -0.05, 0.68),
        (0.20, -0.02, 0.64),
    )
    glyph_width = box["x1"] - box["x0"]
    glyph_height = box["y1"] - box["y0"]
    for index, (x_offset, y_offset, scale) in enumerate(positions):
        person_x = center_x + glyph_width * x_offset
        person_y = baseline + glyph_height * (0.30 + y_offset)
        head_radius = glyph_height * 0.055 * scale
        fill = accent if index in {1, 2} else soft
        edge = accent if index in {1, 2} else ink
        ax.add_patch(Circle((person_x, person_y + head_radius * 2.35), head_radius, facecolor=fill, edgecolor=edge, linewidth=1.1))
        body_width = head_radius * 2.8
        body_height = head_radius * 3.2
        ax.add_patch(
            FancyBboxPatch(
                (person_x - body_width / 2.0, person_y - body_height * 0.52),
                body_width,
                body_height,
                boxstyle=f"round,pad=0.0,rounding_size={head_radius * 0.8}",
                facecolor=fill,
                edgecolor=edge,
                linewidth=1.1,
            )
        )


def _draw_signal_glyph(
    ax: Any,
    *,
    box: dict[str, float],
    accent: str,
    soft: str,
    ink: str,
) -> None:
    width = box["x1"] - box["x0"]
    height = box["y1"] - box["y0"]
    ax.add_patch(
        FancyBboxPatch(
            (box["x0"], box["y0"]),
            width,
            height,
            boxstyle=f"round,pad=0.0,rounding_size={height * 0.22}",
            facecolor=soft,
            edgecolor="none",
        )
    )
    xs = [box["x0"] + width * value for value in (0.12, 0.30, 0.49, 0.68, 0.88)]
    ys = [box["y0"] + height * value for value in (0.28, 0.34, 0.47, 0.62, 0.78)]
    vertices = [(xs[0], box["y0"] + height * 0.18), *zip(xs, ys), (xs[-1], box["y0"] + height * 0.18)]
    codes = [MplPath.MOVETO, *([MplPath.LINETO] * len(xs)), MplPath.LINETO]
    ax.add_patch(PathPatch(MplPath(vertices, codes), facecolor="white", edgecolor="none", alpha=0.72))
    ax.plot(xs, ys, color=accent, linewidth=3.2, solid_capstyle="round")
    for index, (x_value, y_value) in enumerate(zip(xs, ys, strict=True)):
        radius = height * (0.034 + index * 0.005)
        ax.add_patch(Circle((x_value, y_value), radius, facecolor="white", edgecolor=accent, linewidth=2.0))
    ax.add_patch(
        FancyArrowPatch(
            (xs[-2], ys[-2]),
            (xs[-1] + width * 0.015, ys[-1] + height * 0.02),
            arrowstyle="-|>",
            mutation_scale=16,
            linewidth=2.2,
            color=ink,
        )
    )


def _draw_action_glyph(
    ax: Any,
    *,
    box: dict[str, float],
    accent: str,
    soft: str,
    ink: str,
) -> None:
    width = box["x1"] - box["x0"]
    height = box["y1"] - box["y0"]
    center_x = box["x0"] + width * 0.38
    center_y = box["y0"] + height * 0.52
    hub_radius = height * 0.16
    ax.add_patch(Circle((center_x, center_y), hub_radius, facecolor=soft, edgecolor=accent, linewidth=2.0))
    cross_arm = hub_radius * 0.48
    ax.plot([center_x - cross_arm, center_x + cross_arm], [center_y, center_y], color=accent, linewidth=4.0, solid_capstyle="round")
    ax.plot([center_x, center_x], [center_y - cross_arm, center_y + cross_arm], color=accent, linewidth=4.0, solid_capstyle="round")
    endpoint_x = box["x0"] + width * 0.84
    endpoints = (box["y0"] + height * 0.28, box["y0"] + height * 0.76)
    for index, endpoint_y in enumerate(endpoints):
        ax.add_patch(
            FancyArrowPatch(
                (center_x + hub_radius * 0.75, center_y),
                (endpoint_x - height * 0.08, endpoint_y),
                arrowstyle="-|>",
                mutation_scale=16,
                connectionstyle=f"arc3,rad={0.14 if index == 0 else -0.14}",
                linewidth=2.0,
                color=ink,
            )
        )
        ax.add_patch(Circle((endpoint_x, endpoint_y), height * 0.075, facecolor="white", edgecolor=accent, linewidth=2.0))
        if index == 0:
            ax.plot(
                [endpoint_x - height * 0.03, endpoint_x - height * 0.005, endpoint_x + height * 0.04],
                [endpoint_y, endpoint_y - height * 0.025, endpoint_y + height * 0.035],
                color=accent,
                linewidth=2.4,
                solid_capstyle="round",
            )
        else:
            ax.add_patch(Circle((endpoint_x, endpoint_y), height * 0.024, facecolor=accent, edgecolor="none"))


def _draw_generic_glyph(
    ax: Any,
    *,
    box: dict[str, float],
    accent: str,
    soft: str,
    ink: str,
) -> None:
    width = box["x1"] - box["x0"]
    center_y = (box["y0"] + box["y1"]) / 2.0
    xs = [box["x0"] + width * value for value in (0.18, 0.50, 0.82)]
    ax.plot([xs[0], xs[-1]], [center_y, center_y], color=ink, linewidth=2.0)
    for index, x_value in enumerate(xs):
        ax.add_patch(Circle((x_value, center_y), width * 0.055, facecolor=accent if index == 1 else soft, edgecolor=accent, linewidth=1.8))


def _draw_stage_glyph(
    ax: Any,
    *,
    role_family: str,
    box: dict[str, float],
    accent: str,
    soft: str,
    ink: str,
) -> None:
    drawers = {
        "population": _draw_population_glyph,
        "signal": _draw_signal_glyph,
        "action": _draw_action_glyph,
    }
    drawers.get(role_family, _draw_generic_glyph)(ax, box=box, accent=accent, soft=soft, ink=ink)


def _render_submission_graphical_abstract(
    *,
    output_svg_path: Path,
    output_png_path: Path,
    output_layout_path: Path,
    shell_payload: dict[str, Any],
    render_context: dict[str, Any],
) -> None:
    requested_layout_style = str(shell_payload.get("layout_style") or "").strip()
    if requested_layout_style == "square_storyline":
        _render_square_submission_graphical_abstract(
            output_svg_path=output_svg_path,
            output_png_path=output_png_path,
            output_layout_path=output_layout_path,
            shell_payload=shell_payload,
            render_context=render_context,
        )
        return

    render_context_payload = dict(render_context or {})
    palette = dict(render_context_payload.get("palette") or {})
    style_roles = dict(render_context_payload.get("style_roles") or {})
    typography = dict(render_context_payload.get("typography") or {})
    layout_override = dict(render_context_payload.get("layout_override") or {})

    _prepare_python_illustration_output_paths(
        output_png_path=output_png_path,
        output_svg_path=output_svg_path,
        layout_sidecar_path=output_layout_path,
    )

    colors = {
        "ink": _resolve_color(style_roles, "text", _resolve_color(palette, "neutral", "#17222B")),
        "muted": _resolve_color(style_roles, "muted", "#5E6C76"),
        "primary": _resolve_color(style_roles, "model_curve", _resolve_color(palette, "primary", "#245A6B")),
        "contrast": _resolve_color(palette, "contrast", "#2166AC"),
        "secondary": _resolve_color(style_roles, "comparator_curve", _resolve_color(palette, "secondary", "#8B3A3A")),
        "primary_soft": _resolve_color(palette, "primary_soft", "#DDECF0"),
        "contrast_soft": _resolve_color(palette, "contrast_soft", "#DCE9F5"),
        "secondary_soft": _resolve_color(palette, "secondary_soft", "#F3DDDD"),
        "band": _resolve_color(palette, "light", "#F1F5F7"),
    }
    accent_colors = (colors["primary"], colors["contrast"], colors["secondary"])
    soft_colors = (colors["primary_soft"], colors["contrast_soft"], colors["secondary_soft"])

    figure_width_pt = _read_float(layout_override, "graphical_abstract_width_in", 15.0) * 72.0
    figure_height_pt = _read_float(layout_override, "graphical_abstract_height_in", 1000.0 / 120.0) * 72.0
    margin_x = _read_float(layout_override, "graphical_abstract_margin_pt", 34.0)
    panel_gap_pt = _read_float(layout_override, "graphical_abstract_panel_gap_pt", 56.0)
    title_size = max(25.0, _read_float(typography, "title_size", 12.5) * 2.15)
    panel_title_size = max(17.0, _read_float(typography, "axis_title_size", 11.0) * 1.62)
    panel_subtitle_size = max(12.8, _read_float(typography, "tick_size", 10.0) * 1.30)
    callout_size = max(16.5, _read_float(typography, "axis_title_size", 11.0) * 1.52)
    label_size = max(11.0, _read_float(typography, "panel_label_size", 11.0))

    panels = [dict(item) for item in list(shell_payload.get("panels") or [])]
    panel_count = max(1, len(panels))
    panel_width = (figure_width_pt - margin_x * 2.0 - panel_gap_pt * max(0, panel_count - 1)) / panel_count
    panel_y0 = 54.0
    panel_y1 = figure_height_pt - 118.0

    fig = plt.figure(figsize=(figure_width_pt / 72.0, figure_height_pt / 72.0), dpi=120)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0.0, figure_width_pt)
    ax.set_ylim(0.0, figure_height_pt)
    ax.axis("off")

    title_text, _ = _wrap_figure_title_to_width(
        str(shell_payload.get("title") or "Submission graphical abstract").strip(),
        max_width_pt=figure_width_pt - margin_x * 2.0,
        font_size=title_size,
    )
    title_artist = ax.text(
        margin_x,
        figure_height_pt - 36.0,
        title_text,
        fontsize=title_size,
        fontweight="bold",
        color=colors["ink"],
        ha="left",
        va="top",
    )

    band_y0 = panel_y0 + (panel_y1 - panel_y0) * 0.35
    band_height = (panel_y1 - panel_y0) * 0.36
    ax.add_patch(
        FancyBboxPatch(
            (margin_x + 10.0, band_y0),
            figure_width_pt - margin_x * 2.0 - 20.0,
            band_height,
            boxstyle=f"round,pad=0.0,rounding_size={band_height / 2.0}",
            facecolor=colors["band"],
            edgecolor="none",
            alpha=0.82,
        )
    )

    layout_boxes: list[dict[str, Any]] = []
    panel_boxes: list[dict[str, Any]] = []
    guide_boxes: list[dict[str, Any]] = []
    text_records: list[tuple[Any, str, str]] = [(title_artist, "title", "title")]
    panel_regions: list[dict[str, float]] = []
    visual_roles: list[str] = []

    for index, panel in enumerate(panels):
        panel_id = str(panel.get("panel_id") or f"stage_{index + 1}")
        x0 = margin_x + index * (panel_width + panel_gap_pt)
        panel_box = {"x0": x0, "y0": panel_y0, "x1": x0 + panel_width, "y1": panel_y1}
        panel_regions.append(panel_box)
        panel_boxes.append(
            _flow_box_to_normalized(
                **panel_box,
                canvas_width_pt=figure_width_pt,
                canvas_height_pt=figure_height_pt,
                box_id=f"panel_{panel_id}",
                box_type="panel",
            )
        )

        role_family = _role_family(panel, index)
        visual_roles.append(role_family)
        accent = accent_colors[index % len(accent_colors)]
        soft = soft_colors[index % len(soft_colors)]

        label_center = (x0 + 18.0, panel_y1 - 18.0)
        label_radius = 14.0
        ax.add_patch(Circle(label_center, label_radius, facecolor=accent, edgecolor="none"))
        layout_boxes.append(
            _flow_box_to_normalized(
                x0=label_center[0] - label_radius,
                y0=label_center[1] - label_radius,
                x1=label_center[0] + label_radius,
                y1=label_center[1] + label_radius,
                canvas_width_pt=figure_width_pt,
                canvas_height_pt=figure_height_pt,
                box_id=f"panel_label_{panel_id}",
                box_type="panel_label",
            )
        )
        label_artist = ax.text(
            *label_center,
            str(index + 1),
            fontsize=label_size,
            fontweight="bold",
            color="white",
            ha="center",
            va="center",
        )
        text_records.append((label_artist, f"panel_label_text_{panel_id}", "panel_label_text"))

        title_lines = _wrap_flow_text_to_width(
            str(panel.get("title") or "").strip(),
            max_width_pt=panel_width - 48.0,
            font_size=panel_title_size,
            font_weight="bold",
        )
        panel_title_artist = ax.text(
            x0 + 40.0,
            panel_y1 - 4.0,
            "\n".join(title_lines[:2]),
            fontsize=panel_title_size,
            fontweight="bold",
            color=colors["ink"],
            ha="left",
            va="top",
        )
        text_records.append((panel_title_artist, f"{panel_id}_title", "panel_title"))

        glyph_box = {
            "x0": x0 + panel_width * 0.12,
            "y0": panel_y0 + (panel_y1 - panel_y0) * 0.34,
            "x1": x0 + panel_width * 0.88,
            "y1": panel_y0 + (panel_y1 - panel_y0) * 0.74,
        }
        _draw_stage_glyph(
            ax,
            role_family=role_family,
            box=glyph_box,
            accent=accent,
            soft=soft,
            ink=colors["ink"],
        )
        layout_boxes.append(
            _flow_box_to_normalized(
                **glyph_box,
                canvas_width_pt=figure_width_pt,
                canvas_height_pt=figure_height_pt,
                box_id=f"{panel_id}_visual_glyph",
                box_type="visual_glyph",
            )
        )

        card = _first_card(panel)
        callout = str(card.get("value") or "").strip()
        callout_lines = _wrap_flow_text_to_width(
            callout,
            max_width_pt=panel_width * 0.82,
            font_size=callout_size,
            font_weight="bold",
        )
        if callout_lines:
            callout_artist = ax.text(
                x0 + panel_width / 2.0,
                panel_y0 + (panel_y1 - panel_y0) * 0.25,
                "\n".join(callout_lines[:2]),
                fontsize=callout_size,
                fontweight="bold",
                color=accent,
                ha="center",
                va="center",
            )
            text_records.append((callout_artist, f"{panel_id}_callout", "stage_callout"))

        subtitle_lines = _wrap_flow_text_to_width(
            str(panel.get("subtitle") or "").strip(),
            max_width_pt=panel_width * 0.88,
            font_size=panel_subtitle_size,
            font_weight="normal",
        )
        subtitle_artist = ax.text(
            x0 + panel_width / 2.0,
            panel_y0 + 8.0,
            "\n".join(subtitle_lines[:2]),
            fontsize=panel_subtitle_size,
            fontweight="normal",
            color=colors["muted"],
            ha="center",
            va="bottom",
            linespacing=1.25,
        )
        text_records.append((subtitle_artist, f"{panel_id}_subtitle", "panel_subtitle"))

    arrow_artists: list[tuple[str, Any]] = []
    story_y = band_y0 + band_height / 2.0
    for index, (left, right) in enumerate(zip(panel_regions, panel_regions[1:], strict=False), start=1):
        arrow = FancyArrowPatch(
            (left["x1"] + 8.0, story_y),
            (right["x0"] - 8.0, story_y),
            arrowstyle="-|>",
            mutation_scale=22,
            linewidth=2.2,
            color=colors["ink"],
        )
        ax.add_patch(arrow)
        arrow_artists.append((f"panel_arrow_{index}", arrow))

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for box_id, artist in arrow_artists:
        guide_boxes.append(
            _bbox_to_layout_box(
                figure=fig,
                bbox=artist.get_window_extent(renderer=renderer),
                box_id=box_id,
                box_type="arrow_connector",
            )
        )
    for artist, box_id, box_type in text_records:
        layout_boxes.append(
            _bbox_to_layout_box(
                figure=fig,
                bbox=artist.get_window_extent(renderer=renderer),
                box_id=box_id,
                box_type=box_type,
            )
        )

    dump_json(
        output_layout_path,
        {
            "template_id": "submission_graphical_abstract",
            "device": {"x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 1.0},
            "layout_boxes": layout_boxes,
            "panel_boxes": panel_boxes,
            "guide_boxes": guide_boxes,
            "metrics": {
                "layout_style": _CLINICAL_STORYLINE,
                "requested_layout_style": requested_layout_style or _CLINICAL_STORYLINE,
                "source_renderer": _SOURCE_RENDERER,
                "canvas_size_px": [1800, 1000],
                "panel_count": panel_count,
                "visual_roles": visual_roles,
                "footer_pills": list(shell_payload.get("footer_pills") or []),
                "quality_floor_policy": str(shell_payload.get("quality_floor_policy") or ""),
                "governance_metadata_visible_in_artwork": False,
                "numeric_result_policy": "card_values_with_digits_require_evidence_ref",
                "design_rules": [
                    "continuous_left_to_right_clinical_story",
                    "one_visual_glyph_per_stage",
                    "central_signal_is_visual_hero",
                    "no_nested_cards",
                    "no_visible_governance_metadata",
                    "editable_svg_source",
                ],
            },
            "render_context": render_context_payload,
        },
    )

    fig.savefig(output_svg_path, format="svg", facecolor="white")
    fig.savefig(output_png_path, format="png", dpi=120, facecolor="white")
    plt.close(fig)
