### 4a. Deterministic Render Lock

Before the first render, bind `deterministic_render_ref` to resolved font files
and their SHA-256 values, the selected renderer family and version, and the
explicit non-interactive `headless_backend` or export engine for each target
format. Validate required glyph coverage before rendering. A missing or
hash-mismatched font, unavailable backend, or renderer-family drift is a hard
figure-contract failure: repair the environment or emit `route_back_candidate`;
never substitute a system font, interactive backend, or different renderer
silently.

Lock `final_size_layout_ref` before fitting labels: set the target canvas width
and height, final output units, and final text sizes first. Resolve long labels
in this order: use an evidence-faithful short form; measure the unwrapped source
string with the final renderer/font; automatically wrap at semantic boundaries
only when that width exceeds the allocated label lane; then rotate only when the
selected grammar still requires it. Keep source strings free of manual line
breaks. Apply `wrap_policy=automatic_semantic_wrap` on the fixed final canvas
and declared font size; do not shrink text to suppress overlap or pass QA.

After each final renderer draw (`fig.canvas.draw()` plus
`get_window_extent(renderer)` in Matplotlib, or the backend-equivalent final
layout pass), fill `text_extent_safe_area_ref`. Set
`renderer_draw_complete=true` and calculate a text bounding box for
`artist_scope=all_text_artists`: axis-inside and axis-outside text artists,
categorical and tick labels, titles, annotations, legend text, and sample-size
labels. For each panel, register the expected artist ids and every measured bbox
plus its clip bbox. Use a separate `annotation_lane` when the selected grammar
has a dedicated numeric annotation column, such as an estimate/interval plot.
For direct labels, heatmaps, images, and schematics without that column, set
`annotation_lane_policy=not_applicable`, record `annotation_lane_reason`, and
register labels in their actual lane; do not add an empty decorative column.
Normalize boxes to `final_canvas` and
check registry completeness, pairwise overlap, canvas overflow, clipping,
minimum spacing, lane containment, and the explicit `safe_inset`. A pass
requires a complete `artist_extent_report` and `overflow_count=0`.

Export PNG/PDF at the locked final size with `bbox_inches=None` or the
backend-equivalent fixed canvas. `tight_layout`, `bbox_inches=tight`, `clip_on`,
and tight-crop output are not safe-area proof. When renderer, font, wrapping,
geometry, or export behavior changes, run the affected long-string,
extreme-value, and full-width regression fixtures. For a content-only artifact
using an unchanged renderer, set `validation_scope=artifact_acceptance` and
bind `renderer_baseline_ref` to the applicable already-tested renderer; do not
invent a fresh regression receipt. Bind final file SHA-256,
dimensions, safe inset, lane bounds, bbox-registry hash, and check counts in the
deterministic `layout_qc_receipt_ref`. Recheck the rendered DOCX/PDF page when
embedded and record it in `composed_page_check`; a missing or failed required
page check cannot pass this machine geometry gate. The receipt does not create
MAS visual or submission authority.

Bind `single_generation_source_ref` to one structured paper-local source for
data mappings, labels, annotations, caption payload, and catalog/manifest
metadata. The same build must derive the figure, caption, and catalog/manifest
from that source so a manual edit cannot leave those surfaces out of sync. This
ref records provenance only and does not create artifact or MAS authority.

Record the selected grammar in a figure manifest before polishing:

- figure intent
- panel ids
- evidence refs
- statistics and annotations
- renderer family
- plotting library and version when Python is used
- schematic or infographic role, if any, with explicit evidence-bearing versus
  explanatory-only panel boundaries
- exports
- QA checks
- owner-gate status

