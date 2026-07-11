---
name: medical-display-regression-debugger
description: "Use when a MAS medical-paper task needs refs-only display regression debugging: symptom inventory, artifact diff, renderer/source boundary, nonblank export checks, reproduction probe, repair route, route-back, and owner-gate handoff. This optional specialist does not mutate artifacts, write MAS truth, sign owner receipts, create typed blockers, or claim readiness."
---

# Medical Display Regression Debugger

Use this optional MAS Scholar Skills specialist when a figure, table, PDF,
display pack, renderer output, or gallery preview regresses and needs a
refs-only diagnostic packet before artifact owner repair.

This skill is refs-only and no-authority. It can prepare display regression
diagnostic refs, support maps, `route_back_candidate`, and
`owner_gate_handoff_ref`; it cannot mutate artifacts, write MAS truth, sign an
owner receipt, create a typed blocker, or claim publication readiness.

Optional skill-local helper: use `kernel.py` for deterministic display
regression skeletons, artifact diff rows, and forbidden-authority lint.

## Workflow

1. Build `display_regression_symptom_ref`: observed regression, affected
   pages/panels/tables, expected prior behavior, viewer/export context, and
   inspection evidence.
2. Build `artifact_diff_ref`: current vs prior artifact refs, dimensions,
   hashes, visible differences, missing panels, caption drift, or blank regions.
3. Build `renderer_path_ref`: source renderer, template, data refs, command,
   dependency profile, and generated output boundary.
4. Check `source_renderer_boundary_ref`: whether the fault belongs to source
   data, renderer/template, export packaging, PDF assembly, or read-model drift.
5. Build `reproduction_probe_ref`: smallest non-mutating command or inspection
   needed to reproduce the regression and separate artifact from viewer issues.
6. Build `repair_route_ref`: owner surface, likely fix location, forbidden
   workaround, required re-export, and verification target.
7. Produce `route_back_candidate` for artifact owner repair or visual audit.

## Handoff Shape

Return:

- `display_regression_symptom_ref`
- `artifact_diff_ref`
- `renderer_path_ref`
- `source_renderer_boundary_ref`
- `reproduction_probe_ref`
- `repair_route_ref`
- `candidate_refs`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a display regression diagnostic into artifact mutation, visual
audit receipt, MAS truth, owner receipt, typed blocker, current-package
authority, or publication readiness.
