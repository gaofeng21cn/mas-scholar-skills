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
geometry, panel boxes/crops, optional Pillow composition from existing panel
exports, and composite review prompt/ref skeletons. The helper is a refs-only
style/composition aid; it must not redraw data, mutate artifacts, or decide
publication quality.

## Boundary

This subskill owns only refs-only multi-panel assembly and composite QA
guidance. It must not redraw data panels, change panel-level claims or
statistics, invent evidence, switch renderer families, mutate artifact bodies,
write publication truth, sign owner receipts, create typed blockers, claim
visual-audit authority, or claim publication readiness.

## Workflow

1. Confirm `multi_panel_outline_ref`: one figure claim, hook or hero panel,
   panel jobs, panel order, and layout intent.
2. Confirm each `panel_render_receipt_ref`: panel input ref, data/evidence refs,
   output path, visible claim, and known panel-level limits.
3. Compose from existing panel exports only. If a panel needs scientific
   rerendering, route that panel back to `medical-figure-design`.
4. Check `composite_review_ref`: panel letters, gutters, resized text,
   cross-panel consistency, crop-level violations, and export dimensions.
5. Rerender only affected panels or the composite when the finding is scoped.
   Do not regenerate clean panels for activity.

## Output

Produce a compact `figure_composition_review_ref` with:

- input panel refs and panel render receipts
- layout/export decision and composite output ref
- composite findings and scoped fixes
- `visual_qa_receipt_ref` when the composite export was inspected
- route-back items for panel-level evidence or render defects
- owner-gate target for MAS/domain review

`figure_composition_review_ref` and `visual_qa_receipt_ref` are candidate
composition refs only. MAS or the consuming domain owner decides acceptance,
route-back, typed blocker, artifact mutation, visual-audit receipt, and
publication readiness.
