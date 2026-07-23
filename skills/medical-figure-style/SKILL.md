---
name: medical-figure-style
description: "Use when a MAS figure task only needs professional visual grammar or style QA for an existing figure, panel, or draft export. This thin MAS Scholar Skills display subskill checks data fidelity, claim-title truth, label economy, color accessibility, final-scale readability, and export-visible style risk without composing panels, redrawing data figures, mutating artifacts, or claiming MAS authority."
---

# Medical Figure Style

Use this thin display subskill when the task is style-only: visual grammar,
readability, label economy, palette, final-size inspection, or style QA for an
existing figure, panel, or draft export.

Every final visual QA pass for a new or materially repaired paper-facing figure
must emit a `medical-figure-style` invocation receipt through
`contracts/professional-figure-workflow.schema.json`. The receipt binds this
Skill's exact source identity, the reviewed input contract, consumed rule refs,
and the exact final PNG/PDF bytes. It remains refs-only and no-authority.

Use `medical-figure-design` instead when the figure claim, evidence chain,
panel plan, renderer choice, or full figure workflow is still being created or
repaired. Use `medical-figure-composer` when the task is only assembling
already rendered panels into a multi-panel figure.

Shared refs: `docs/no-authority-boundary.md` and
`references/professional-quality-ref-templates.md`. This subskill preserves the
Claude Science figure-style discipline already absorbed in MAS Scholar Skills:
data fidelity before chart judgment, claim-title truth, excluded-row handling,
comparable-condition separation, displayed `n` and fixed context, label
economy, color-vision robustness, and render-then-verify.

Optional helper: use `kernel.py` for deterministic style utilities such as
matplotlib rcParams, focal palettes, panel-letter placement refs, frame helpers,
crop-box refs, and lightweight contrast/readability lint. The helper is a
refs-only style/composition aid; its Matplotlib export default keeps the fixed
canvas with `savefig.bbox=None`. It must not redraw data, mutate artifacts, or
decide publication quality.

## Boundary

This subskill owns only refs-only visual grammar and style QA guidance. It must
not redraw data figures, choose a new panel composition, switch renderer
families, mutate artifact bodies, write publication truth, sign owner receipts,
create typed blockers, claim visual-audit authority, or claim publication
readiness.
If a style annotation exposes a source, evidence, or claim mismatch, emit
`annotation_to_source_regeneration_ref` and route to `medical-figure-design`
instead of hiding the issue with visual polish.

Use `professional_ai_quality_floor_ref` without expanding this subskill's
authority. Style critique becomes `critique_as_repair_hint_ref` only for
visible grammar, readability, label, color, export, or final-scale repair. Add
`claim_type_ref` and `graph_warnings_ref` when titles, labels, or legends imply
unsupported, stale, circular, missing-source, or visible-payload drift. Consume
`rerun_receipt_ref` only as export/style-check evidence, and trigger
`triggered_meta_review_ref` when the issue is no longer style-only.

## Workflow

1. Confirm the existing figure or panel export and its claim/evidence refs.
   Missing evidence is a route-back issue for `medical-figure-design`, not a
   styling problem.
2. Check `data_fidelity_ref`, `excluded_rows_ref`, `comparability_ref`,
   `replication_and_fixed_context_ref`, and `claim_title_truth_ref` before any
   visual polish recommendation.
3. Consume the renderer's `text_extent_safe_area_ref` and
   `layout_qc_receipt_ref`. Confirm measured-width automatic wrapping without
   manual source breaks, separate plotting/data and right annotation lanes, a
   complete per-panel text bbox registry, zero overlap/overflow/clipping/minimum
   spacing/safe-inset violations, and final-size PNG/PDF SHA and dimensions on a
   fixed canvas. Consume `final_scale_projection_ref` for every main and
   supplementary figure and verify its font and safe-inset projection at the
   narrowest permitted manuscript embedding width, even when the source export
   is full width or the figure does not look dense. For a declared flow or
   schematic, also require the complete semantic-artist registry and computed
   connector/node/arrowhead/bracket geometry checks from `medical-display-qc`;
   a text-only bbox pass cannot support style acceptance. A tight crop cannot
   repair a failure.
4. Check `label_economy_ref`, `color_vision_check_ref`,
   `final_size_grayscale_preview_ref`, `export_lint_ref`, and
   `visual_qa_preview_ref` on the actual rendered output. Add
   `final_scale_visual_qa_ref` when the figure was inspected at final
   manuscript dimensions.
   For evidence figures, reject embedded figure titles, subtitles, and prose
   footers; those belong in the manuscript caption. This restriction does not
   apply to a purpose-built graphical abstract.
5. Return style findings as candidate refs: what can be fixed inside visual
   style, what must route back to evidence/renderer work, and what remains a
   reviewer hint.

## Output

Produce a compact `figure_style_review_ref` with:

- input figure or panel ref
- checked claim/evidence refs
- style-only findings and proposed fixes
- `visual_qa_receipt_ref` when the actual rendered export was inspected
- `professional_figure_style_invocation_ref` bound to the exact final PNG/PDF
  SHA-256 values
- `layout_qc_receipt_ref` as deterministic machine evidence only, never as MAS
  visual/submission authority
- `final_scale_visual_qa_ref` when final-size readability was inspected
- `annotation_to_source_regeneration_ref` for source/claim mismatches that must
  route back to figure design or evidence repair
- `claim_type_ref` and `graph_warnings_ref` for style-visible claim risks
- `critique_as_repair_hint_ref`, `triggered_meta_review_ref`, and
  `rerun_receipt_ref` when the style pass consumed those candidate refs
- hard route-back items, if evidence or readability fails
- owner-gate target for MAS/domain review

`figure_style_review_ref` and `visual_qa_receipt_ref` are candidate review refs
only. MAS or the consuming domain owner decides acceptance, route-back, typed
blocker, artifact mutation, visual-audit receipt, and publication readiness.
