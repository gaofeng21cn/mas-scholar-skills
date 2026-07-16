---
name: medical-figure-composer
description: "Use when a MAS figure task only needs multi-panel assembly, layout, export QA, or composite review from existing rendered panels. This thin MAS Scholar Skills display subskill checks panel order, gutters, labels, resized text, crop-level consistency, and composite export without redrawing data figures, changing panel evidence, or claiming MAS authority."
---

# Medical Figure Composer

Use this thin display subskill when the task is compose-only: assemble existing
rendered panels into a multi-panel figure, inspect the composite, and prepare
layout/export QA findings.

Use `medical-figure-design` instead when claims, evidence refs, renderer
selection, or panel creation are still open. Use `medical-figure-style` when the
task is only visual grammar or style QA for an existing figure or panel.

Shared refs: `docs/no-authority-boundary.md` and
`references/professional-quality-ref-templates.md`. This subskill preserves the
Claude Science figure-composer discipline already absorbed in MAS Scholar
Skills: outline -> panel render receipt -> composite review, with existing
panels treated as inputs rather than data to redraw.

Optional helper: use `kernel.py` for deterministic outline schema, grid
geometry, panel boxes/crops, physical-layout findings, optional Pillow
composition from existing panel exports, and composite review prompt/ref
skeletons. The helper is a refs-only style/composition aid; it must not redraw
data, mutate artifacts, or decide publication quality.

## Boundary

This subskill owns only refs-only multi-panel assembly and composite QA
guidance. It must not redraw data panels, change panel-level claims or
statistics, invent evidence, switch renderer families, mutate artifact bodies,
write publication truth, sign owner receipts, create typed blockers, claim
visual-audit authority, or claim publication readiness.
If a composite annotation reveals a panel/source mismatch, emit
`annotation_to_source_regeneration_ref` and route that panel back to
`medical-figure-design`; do not solve scientific drift with layout edits.

## Geometry And Fit Policy

- `validate_outline` hard-fails non-finite or non-positive physical dimensions,
  non-integer grid coordinates/spans, duplicate panel letters, out-of-grid
  geometry, overlapping grid cells, and unsupported `fit_mode` values.
  `grid_geometry` also rejects non-positive `dpi`, negative `gutter_mm`, and
  non-positive derived pixel boxes. Do not coerce invalid values or silently
  move, shrink, or reorder panels to repair an invalid outline.
- Each panel may set `fit_mode: contain|crop`; the default is `contain`.
  `contain` preserves aspect ratio and centers the panel on white background.
  `crop` must be explicit; it preserves aspect ratio while filling the target
  box and may remove edge content. Never stretch a panel to fit.
- Preserve each panel's text bbox registry through the selected scale/crop
  transform, and register composer-added panel letters or text. The transformed
  registry must still keep right annotations in a lane separate from plotted
  data (`plotting/data`) and must expose overlap, canvas-overflow, clipping,
  minimum-spacing, and safe-inset failures. A crop that removes a registered
  text artist fails.
- The figure contract and AI-selected outline continue to decide the hook or
  hero panel, panel order, and grid. Do not add a hero-selection or layout
  heuristic in the composer.
- Use `composition_layout_findings` to report each panel's physical width and
  height, source/target aspect ratio, and fit mode. A width or height below the
  default 35 mm floor is a refs-only warning with `blocks_progress: false`, not
  a composition gate. Keep clean work moving and route only the affected panel
  or composite for final-scale review. Invalid geometry or fit mode remains a
  hard failure.

Use `professional_ai_quality_floor_ref` without expanding this subskill's
authority. Composite critique becomes `critique_as_repair_hint_ref` only for
panel order, crop, gutter, panel-letter, resized-text, export, or final-scale
repair. Add `claim_type_ref` and `graph_warnings_ref` when panel labels or
composite captions imply unsupported, stale, circular, missing-source, or
visible-payload drift. Consume `rerun_receipt_ref` only as composite/export
check evidence, and trigger `triggered_meta_review_ref` when the issue must
return to figure design, statistics, table, data, writing, or review.

## Workflow

1. Confirm `multi_panel_outline_ref`: one figure claim, hook or hero panel,
   panel jobs, panel order, and layout intent.
2. Confirm each `panel_render_receipt_ref` and `layout_qc_receipt_ref`: panel
   input ref, data/evidence refs, output SHA and dimensions, complete text bbox
   registry, visible claim, and known panel-level limits.
3. Validate the outline and choose explicit per-panel `fit_mode` only where
   cropping is intended and reviewable. Record physical-layout warnings without
   blocking unaffected panel progress.
4. Compose from existing panel exports only. If a panel needs scientific
   rerendering, route that panel back to `medical-figure-design`.
5. Check `composite_review_ref`: panel letters, gutters, resized text,
   transformed bbox registries, cross-panel consistency, crop-level violations,
   and export dimensions. Export the final PNG/PDF at one declared size on a
   fixed canvas (`bbox_inches=None` or backend equivalent), then use
   `medical-display-qc` to emit a deterministic composite
   `layout_qc_receipt_ref` bound to both SHA-256 values, dimensions, safe inset,
   lanes, and registry hash. Add
   `final_scale_visual_qa_ref` for final manuscript-size inspection.
6. Rerender only affected panels or the composite when the finding is scoped.
   Do not regenerate clean panels for activity.

## Output

Produce a compact `figure_composition_review_ref` with:

- input panel refs and panel render receipts
- layout/export decision and composite output ref
- refs-only `composition_layout_findings` with physical size, aspect-ratio, fit
  mode, and non-blocking sub-35 mm warnings
- composite findings and scoped fixes
- `visual_qa_receipt_ref` when the composite export was inspected
- panel and composite `layout_qc_receipt_ref` values as machine geometry
  evidence only, never as MAS visual/submission authority
- `final_scale_visual_qa_ref` when final-size composite readability was
  inspected
- `annotation_to_source_regeneration_ref` for panel/source mismatches that need
  evidence or render repair
- `claim_type_ref` and `graph_warnings_ref` for composite-visible claim risks
- `critique_as_repair_hint_ref`, `triggered_meta_review_ref`, and
  `rerun_receipt_ref` when the composition pass consumed those candidate refs
- route-back items for panel-level evidence or render defects
- owner-gate target for MAS/domain review

`figure_composition_review_ref` and `visual_qa_receipt_ref` are candidate
composition refs only. MAS or the consuming domain owner decides acceptance,
route-back, typed blocker, artifact mutation, visual-audit receipt, and
publication readiness.
