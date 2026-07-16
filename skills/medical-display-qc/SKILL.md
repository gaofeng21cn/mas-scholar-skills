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

For every fresh audit, consume the MAS `review_input_snapshot_binding` and read
only the exact `opl_reviewer_input_snapshot_manifest` immutable rendered,
caption, catalog, semantic, and layout members. Never fall through to live
workspace or checkout locators. Snapshot gaps are lane-specific refs-only
route-back candidates, not typed blockers or hosted-action liveness stops.

Optional skill-local helper: `kernel.py` provides deterministic ref helpers and
a non-mutating rendered-artifact inspector. It imports Pillow or PyMuPDF only
when the selected file type needs them; a missing dependency becomes a typed
warning finding and is never installed automatically or turned into a blocker.

```bash
python3 skills/medical-display-qc/kernel.py --inspect <artifact.png|jpg|tiff|pdf>
python3 skills/medical-display-qc/kernel.py --layout-registry <registry.json> \
  --png <final.png> --pdf <final.pdf>
```

The first mode inspects one artifact. The second audits a renderer-produced bbox
registry and emits a deterministic `layout_qc_receipt_ref` bound to final
PNG/PDF bytes. Neither mode proves renderer/font-lock fidelity,
source-to-caption synchronization, clean-rebuild reproducibility, or final-size
visual correctness; keep those as separate refs and review lanes.

The command prints JSON. Artifact inspection exits `2` only for missing,
unreadable, zero-byte, confirmed uniformly blank/transparent, or clearly
damaged artifacts. Layout mode exits `2` when its deterministic geometry checks
fail; that exit is not a visual quality, MAS, or submission verdict.
Review warnings such as missing DPI, small dimensions, high content density,
an unavailable PDF inspector, unverified font embedding, or a suffix that does
not match the detected artifact format exit `0` so ordinary stage progress
can continue. Low sampled density alone never proves that an artifact is blank,
and an empty Type 3 font-program extraction remains unknown rather than being
reported as an unembedded font.

For PDF review evidence, the kernel also rasterizes every page under one fixed
contract and emits ordered RGB8 pixel SHA-256 rows. Use
`build_page_hash_evidence_candidate` with the current display scope digest,
rubric content digest, and valid origin reviewer invocation/evidence refs. A
cache hit reuses evidence only: it never skips a fresh reviewer invocation or
fresh MAS receipt/judgment, and every verdict/readiness/authority flag remains
false. OPL owns persistent cache storage and
`opl_review_evidence_cache_receipt`.

## Workflow

1. Run the inspector for every final rendered PNG/JPEG/TIFF/PDF when a local
   path is available, including both members of the required PNG/PDF or
   paper-local raster/vector pair. Use path, SHA-256, byte size, detected
   format, dimensions, page/frame count, DPI, content density, font summary,
   and PDF metadata as `display_artifact_inventory_ref` and
   `programmatic_figure_audit_ref` candidate evidence.
2. Check `deterministic_render_ref`: resolve each `font_file_ref`, compare its
   `font_file_sha256`, confirm the renderer family/version and explicit
   `headless_backend` or export engine, and reject evidence of silent font or
   renderer fallback. Missing or mismatched lock evidence produces
   `route_back_candidate`; this skill does not create a typed blocker.
3. Check `final_size_layout_ref` at the fixed target width and height with the
   declared final text sizes. Use the renderer-measured unwrapped source-label
   width and compare it with the available label lane. When it does not
   fit, require `wrap_policy=automatic_semantic_wrap` at semantic boundaries;
   manual line breaks in source strings and shrinking text are not passing repairs.
4. Check `text_extent_safe_area_ref` after a final renderer draw. Require
   `renderer_draw_complete=true`, an explicit `final_canvas` and `safe_inset`,
   and one registered text bounding box plus clip bbox for every expected text
   artist in every panel under `artist_scope=all_text_artists`. Require a right
   `annotation_lane` geometrically separate from the plotting/data lane, a
   complete `artist_extent_report`, zero overlap,
   canvas overflow, clipping, minimum-spacing and safe-inset violations, and
   `overflow_count=0`.
5. Produce `layout_qc_receipt_ref` from the complete bbox registry and actual
   final PNG/PDF pair. Require one fixed canvas at final size,
   `bbox_inches=None` or the backend-equivalent no-tight-crop policy, both file
   SHA-256 values and dimensions, safe inset, lane bounds, registry hash, and
   deterministic check counts. Run the long-string, extreme-value, and
   full-width fixture at
   `skills/medical-display-qc/fixtures/layout_qc_regression.json`. Repeat the
   page check for the embedded DOCX/PDF and record it in `composed_page_check`.
   `tight_layout`, `bbox_inches=tight`, and `clip_on` are not proof.
6. Check `paired_export_qa_ref`: both outputs exist and come from the same
   `single_generation_source_ref`; dimensions, visible data, labels,
   annotations, crop bounds, and panel order agree. Inspect PDF font embedding
   and subtype as well as raster dimensions/DPI. For Matplotlib, an explicit
   `pdf.fonttype=42` policy is one example; require equivalent embedding checks
   for other renderer families rather than treating Matplotlib as the only
   backend. Preserve the existing rule that unverified embedding, including an
   empty Type 3 font-program extraction, remains unknown rather than passing.
7. Check `clean_rebuild_consistency_ref`: two clean rebuild receipts must carry
   the same SHA-256 `source_fingerprint` and identical per-format
   `output_fingerprints`. Any difference routes back to the source/render owner
   before owner review.
8. Keep `programmatic_figure_audit_ref` separate from
   `final_scale_visual_qa_ref`. The former checks deterministic properties and
   geometry; the latter reviews the actual raster output and a rasterized
   final-size vector output. Neither lane can be inferred from or replace the
   other.
9. In both lanes where applicable, check `annotation_headroom`,
   `boundary_clipping`, `line_text_intersection`, and `tick_label_overlap`,
   including crop edges, error bars, brackets, grid/connector lines, rotated
   labels, legends, and axis-title collisions.
10. Check `panel_caption_consistency_ref`: panel letters, legends, table titles,
   figure numbering, duplicated identifiers, and caption payload drift. Confirm
   the figure, caption, and catalog/manifest were driven by the same structured
   generation source.
11. Check `claim_display_alignment_ref`: displayed denominator, estimates,
   uncertainty, colors, groups, ordering, and manuscript claim consistency.
12. Check `accessibility_and_size_ref`: final-size readability, overlap,
    color-vision robustness, grayscale contrast, and journal size constraints.
13. Check `export_integrity_ref`: distinguish hard artifact failures from
    non-blocking review warnings; never promote an inspector result into a
    visual quality verdict.
14. Produce `route_back_candidate` for artifact owner repair, display redesign,
    source-data mismatch, deterministic rebuild drift, export failure, or owner
    visual-audit decision.

## Handoff Shape

Return:

- `display_artifact_inventory_ref`
- `deterministic_render_ref`
- `final_size_layout_ref`
- `text_extent_safe_area_ref`
- `layout_qc_receipt_ref`
- `single_generation_source_ref`
- `paired_export_qa_ref`
- `clean_rebuild_consistency_ref`
- `programmatic_figure_audit_ref`
- `final_scale_visual_qa_ref`
- `export_integrity_ref`
- `panel_caption_consistency_ref`
- `claim_display_alignment_ref`
- `accessibility_and_size_ref`
- `display_qc_support_map_ref`
- `page_hash_evidence_candidate_ref` when fixed-raster PDF evidence is available
- `input_scope_signature_ref` when exact-input provenance is available
- `candidate_refs`
- `route_back_candidate`
- `owner_gate_handoff_ref`

For `input_scope_signature_ref`, use `scope_id=display_qc` and bind the exact
rendered artifacts, visible captions and catalog metadata, source-data or
semantic refs, layout registry, deterministic render inputs, and composed-page
evidence actually inspected. Unrelated manuscript sections, bibliography
metadata, package/build scripts, checkout/model state, mtimes, and locators do
not enter this digest. A mismatch makes only the prior `display_qc` candidate
receipt non-reusable; it is not a visual verdict, lock, signature authority, or
whole-package blocker.

Do not turn a QC candidate into artifact authority, visual audit receipt,
owner acceptance, typed blocker, current-package authority, or publication
readiness. Programmatic inspection supplies evidence for the agent's visual
review; it does not replace visual inspection, claim-display review, or the
consuming domain owner's decision.
