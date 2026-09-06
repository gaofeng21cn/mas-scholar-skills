### 6. Visual QA

Open the rendered output and inspect the actual figure, not only logs or code.

Keep two QA lanes separate:

- `programmatic_figure_audit_ref`: deterministic checks for missing glyphs,
  CJK/negative-sign rendering, bound font-file hashes, clipped text,
  `annotation_headroom`, `boundary_clipping`, `line_text_intersection`,
  `tick_label_overlap`, the renderer-drawn `text_extent_safe_area_ref`, complete
  bbox registry, lane separation, minimum spacing, fixed-canvas export, and the
  SHA-bound `layout_qc_receipt_ref`, plus file format, DPI, font
  embedding/subtype, final dimensions, and source/export traceability.
- `export_lint_ref`: export-contract lint for file format, DPI, font embedding,
  final dimensions, and traceability before any owner handoff.
- `paired_export_qa_ref`: separate raster/vector checks for payload, dimensions,
  labels, annotations, crop bounds, font behavior, and output fingerprints.
- `visual_qa_preview_ref` / `critic_review_ref`: AI or human visual review of
  a rasterized final-size preview for legend/data overlap, annotation headroom,
  edge clipping, lines crossing text, tick-label overlap, panel alignment,
  visual hierarchy, grayscale/color-vision separation, and whether the chart
  answers the intended data question.
- `final_scale_visual_qa_ref`: the final manuscript-scale readback of the
  actual raster output and a rasterization of the vector output; use it before
  owner handoff, not as a substitute for owner visual-audit authority.
- `ai_visual_review_ref`: the AI visual-review lane only; it cannot replace the
  deterministic audit lane or owner visual-audit authority.

Do not infer visual correctness from the programmatic lane or infer export
integrity from the visual lane. Both must report independently over the actual
final-size outputs.

For deterministic owner handoff, run the same pinned build twice in separate
empty temporary output/cache directories. Preserve existing user artifacts and
render caches; never delete them to make a clean build. For each run, record
`clean_rebuild_consistency_ref` with a
SHA-256 `source_fingerprint` over source data, render code/config, caption and
catalog/manifest source, bound font files, and renderer/backend versions, plus
byte-level `output_fingerprints` for every required export. Fix or omit volatile
export metadata such as creation timestamps instead of normalizing mismatched
files after rendering. The two clean runs must have identical source and output
fingerprints. Any drift routes back to the source/render owner; do not waive it
as a refs-only caveat.

Check:

- whether the main comparison is obvious in a few seconds
- whether the chart type follows the data question, variable types, grouping,
  sample size, and distribution rather than habit or template reuse
- whether excluded rows are omitted from summaries or visibly marked as
  exclusions
- whether compared conditions are genuinely comparable or visually separated
- whether summary marks state `n`, replication unit, and fixed context when
  those affect interpretation
- whether sentence-style titles and panel labels are true for every plotted row
- whether each quantitative claim uses the same canonical value in panel,
  caption, and manuscript
- whether the label set meets the floor for mark identity and the ceiling for
  narrative annotations
- labels, units, sample sizes, uncertainty, and baselines
- panel order and visual hierarchy
- color accessibility and grayscale robustness
- text size after likely manuscript scaling
- overlap, truncation, clipped legends, duplicate titles, and prose cards
- annotation headroom above confidence intervals, bars, points, brackets, and
  significance labels at the fixed target dimensions
- boundary clipping on every canvas and panel edge, including strokes, error
  bars, labels, legends, and crop boxes
- line, curve, gridline, or connector intersections that cross text or
  annotations and make them ambiguous
- complete semantic-artist registration for every declared flow or schematic,
  including nodes, bands, brackets, connector segments, arrowheads, and text;
  zero line-text, line-unrelated-node, unauthorized connector-crossing,
  arrowhead-text, node-text-containment, relation-encoding, arrow-budget,
  ambiguous-incoming, or bracket-span violations
- tick-label overlap, truncation, collision with axis titles, or overlap created
  by rotation at final manuscript size
- complete renderer-drawn text extents for all axis-inside and axis-outside text,
  annotations, legends, and sample-size labels, with the declared safe inset and
  zero overflow
- automatic measured-width wrapping without source-level manual breaks
- separate plotting/data and annotation lanes when the grammar needs them;
  an explicit reason and actual label geometry otherwise; complete per-panel bbox
  registries; zero overlap, canvas overflow, clipping, minimum-spacing, and
  safe-inset violations
- fixed-canvas final PNG/PDF checks and deterministic SHA/dimension/safe-area
  receipt evidence, plus successful checks on the embedded DOCX/PDF page
- missing glyphs, CJK tofu boxes, special-symbol loss, or negative-sign boxes
- whether every visible claim is supported by evidence refs
- whether schematic icons, arrows, or explanatory simplifications preserve the
  evidence boundary instead of implying unshown mechanism or causality
- grayscale and color-vision robustness for categorical encodings
- avoidance of misleading palettes such as rainbow/jet for ordered scientific
  data
- avoidance of small-n mean bars, dual Y axes, pie or 3D charts, chartjunk,
  categorical lines, unexplained error bars, and missing colorbars for
  continuous mappings
- figure legend consistency with visible variables, units, sample sizes, and
  statistical annotations
- vector/source export availability or documented raster DPI reason
- raster/vector pair parity and PDF font embedding/subtype evidence when both
  formats are required
- figure, caption, and catalog/manifest agreement from the same structured
  generation source
- identical source and output fingerprints from two clean rebuilds
- source-data and code traceability for every evidence panel

For phenotype-atlas heatmaps or service-review maps, figure titles, panel
titles, captions, legends, and axis labels must carry the same bounded
terminology as the manuscript. If the paper has moved from generic treatment
gaps to recorded risk-treatment mismatch, update figure metadata and renderer
defaults together. Shorten heatmap axis labels at manuscript scale rather than
letting long clinical phrases overlap; move detailed definitions to the legend,
caption, or table note.

Warnings alone are not default blockers. Route back only when hard evidence
shows missing refs, unsupported claims, unreadable or misleading visual output,
programmatic audit failure, or an AI/human visual review failure that cannot be
repaired inside the figure contract. Otherwise record the warning as a
refs-only caveat or reviewer hint. Use `route_back_hard_evidence_ref` for that
threshold; do not create a MAS typed blocker or owner receipt from this skill.

