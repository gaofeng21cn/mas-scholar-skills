---
name: medical-display-qc
description: "Use when a MAS medical-paper task needs refs-only figure/table display QC: nonblank export checks, panel/caption consistency, readability, color/accessibility, claim-display alignment, artifact refs, route-back, and owner-gate handoff. This optional specialist does not mutate artifacts, sign visual audit receipts, create typed blockers, or claim publication/readiness."
---

# Medical Display QC

Use this optional MAS Scholar Skills specialist when exported figures, tables,
multi-panel composites, PDFs, or display packages need quality-control
candidate refs before MAS/domain owner consumption.

This skill is refs-only and no-authority. It can prepare display QC refs,
support maps, `route_back_candidate`, and `owner_gate_handoff_ref`; it cannot
mutate artifacts, write MAS truth, sign visual audit receipts or owner receipt,
create typed blockers, accept figures, or claim publication readiness.

## Workflow

1. Build `display_artifact_inventory_ref`: file paths/refs, pages, panels,
   tables, captions, export format, dimensions, and source artifact refs.
2. Check `export_integrity_ref`: nonblank pages/regions, missing panels,
   raster/vector presence, font embedding/readability, and broken links.
3. Check `panel_caption_consistency_ref`: panel letters, legends, table titles,
   figure numbering, duplicated identifiers, and caption payload drift.
4. Check `claim_display_alignment_ref`: displayed denominator, estimates,
   uncertainty, colors, groups, ordering, and manuscript claim consistency.
5. Check `accessibility_and_size_ref`: final-size readability, overlap,
   color-vision robustness, grayscale contrast, and journal size constraints.
6. Produce `route_back_candidate` for artifact owner repair, display redesign,
   source-data mismatch, export failure, or owner visual-audit decision.

## Handoff Shape

Return:

- `display_artifact_inventory_ref`
- `export_integrity_ref`
- `panel_caption_consistency_ref`
- `claim_display_alignment_ref`
- `accessibility_and_size_ref`
- `display_qc_support_map_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a QC candidate into artifact authority, visual audit receipt,
owner acceptance, typed blocker, current-package authority, or publication
readiness.
