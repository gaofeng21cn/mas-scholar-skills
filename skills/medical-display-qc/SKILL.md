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

Optional skill-local helper: `kernel.py` provides deterministic ref helpers and
a non-mutating rendered-artifact inspector. It imports Pillow or PyMuPDF only
when the selected file type needs them; a missing dependency becomes a typed
warning finding and is never installed automatically or turned into a blocker.

```bash
python3 skills/medical-display-qc/kernel.py --inspect <artifact.png|jpg|tiff|pdf>
```

The command prints JSON. It exits `2` only for missing, unreadable, zero-byte,
confirmed uniformly blank or fully transparent, or clearly damaged artifacts.
Review warnings such as missing DPI, small dimensions, high content density,
an unavailable PDF inspector, unverified font embedding, or a suffix that does
not match the detected artifact format exit `0` so ordinary stage progress
can continue. Low sampled density alone never proves that an artifact is blank,
and an empty Type 3 font-program extraction remains unknown rather than being
reported as an unembedded font.

## Workflow

1. Run the inspector for each final rendered PNG/JPEG/TIFF/PDF when a local
   path is available. Use its path, SHA-256, byte size, detected format,
   dimensions, page/frame count, DPI, content density, font summary, and PDF
   metadata as `display_artifact_inventory_ref` and
   `programmatic_figure_audit_ref` candidate evidence.
2. Check `export_integrity_ref`: distinguish hard artifact failures from
   non-blocking review warnings; never promote an inspector result into a
   visual quality verdict.
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
- `programmatic_figure_audit_ref`
- `export_integrity_ref`
- `panel_caption_consistency_ref`
- `claim_display_alignment_ref`
- `accessibility_and_size_ref`
- `display_qc_support_map_ref`
- `candidate_refs`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a QC candidate into artifact authority, visual audit receipt,
owner acceptance, typed blocker, current-package authority, or publication
readiness. Programmatic inspection supplies evidence for the agent's visual
review; it does not replace visual inspection, claim-display review, or the
consuming domain owner's decision.
