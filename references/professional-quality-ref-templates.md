# Professional Quality Ref Templates

Owner: `mas-scholar-skills`
State: `refs_only_lightweight_reference`
Boundary: these templates create candidate refs only. They cannot write domain
truth, sign an owner receipt, create a typed blocker, claim a quality verdict,
or claim publication readiness.

Use this reference when a `medical-*` specialist skill needs a compact
handoff shape instead of inventing a new checklist. Keep the filled result in
the consuming paper workspace or owner surface; this repository only defines
the ref vocabulary.

## Figure Contract Template

Use `figure_contract_template_ref` before drawing a new or repaired manuscript
figure.

Minimum fields:

- `core_conclusion_ref`: one bounded claim the figure must defend.
- `panel_evidence_chain_ref`: panel-by-panel data, cohort, statistic, model,
  table, prior result, or citation refs.
- `forbidden_claim_drift`: claims the figure must not imply.
- `data_profile_ref`: variable types, usable n, grouping structure, missingness,
  distribution shape, outliers, and the intended reader question.
- `plot_selection_ref`: data-question-first chart choice using variable type,
  grouping, sample size, distribution, uncertainty, and table-vs-figure fit.
- `plot_selection_candidate_ref`: refs-only chart recommendation plus warnings
  such as small-n mean bars, dual axes, pie/3D charts, rainbow/jet palettes,
  unexplained error bars, chartjunk, categorical lines, and missing colorbars.
- `figure_archetype`: evidence grid, mechanism schematic, mixed-modality
  composite, clinical evidence summary, or image-plus-quant panel set.
- `renderer_decision_ref`: selected renderer family and rejected alternatives.
- `style_brief_ref`: journal class, audience, hierarchy, palette, and allowed
  visual references.
- `candidate_set_ref`: one to three plans or renders when the design space is
  open.
- `critic_review_ref`: evidence fit, readability, accessibility, export, and
  reviewer-risk findings.
- `final_size_export_ref`: target dimensions, text size, vector/raster format,
  DPI if raster is required, final-scale preview readback, and source
  preservation.
- `export_lint_ref`: file format, DPI, font embedding, final dimensions,
  CJK/symbol/negative-sign glyph risk, clipping, and source/export traceability.
- `final_size_grayscale_preview_ref`: final-size raster preview and grayscale or
  color-vision separation readback.
- `programmatic_figure_audit_ref`: deterministic audit result for missing
  glyphs, CJK/negative-sign rendering, clipping, overlapping ticks, file
  format, DPI, font embedding, and dimensions.
- `visual_qa_preview_ref`: AI or human visual review of the rasterized preview
  for legend/data overlap, panel alignment, visual hierarchy, grayscale or
  color-vision separation, and whether the chart answers the data question.
- `ai_visual_review_ref`: AI visual-review findings kept separate from
  deterministic export/programmatic audit results.
- `route_back_hard_evidence_ref`: only missing source/data/evidence refs,
  unsupported claims, unreadable output, or export lint/programmatic/visual
  review FAIL conditions that cannot be repaired inside the figure contract.
- `owner_gate_handoff_ref`: MAS/domain owner target for accept, reject, or
  route-back.

Stop before plotting if `core_conclusion_ref` or `panel_evidence_chain_ref` is
missing. A visual reference is a style target, not data truth or template
authority.

Warnings such as small-n mean bars, dual axes, pie or 3D charts, rainbow/jet
palettes, unexplained error bars, chartjunk, categorical lines, or missing
continuous colorbars remain refs-only reviewer hints unless hard evidence shows
missing source/data/evidence refs, unsupported claims, unreadable output, or
export lint/programmatic/visual-review failure. External plotting runtimes and
scripts may inform the pattern, but they do not become the default backend, MAS
authority, owner receipt, typed blocker, or publication readiness evidence.

## Literature Source/Ref Chain

Use `source_ref_chain_template_ref` when a literature task needs traceable
source routing, not a memory-based citation answer.

Minimum chain:

- `literature_retrieval_contract_ref`: claim, population, endpoint, method,
  identifier, source route, server filters, local filters, expected fields, and
  completeness requirement.
- `query_plan_ref`: PICO/PECO terms, MeSH candidates, synonyms, exclusion
  logic, and justified limits.
- `search_command_ref`: command, connector receipt, access date, and source
  endpoint provenance.
- `pubmed_source_refs` / `fallback_source_refs`: normalized source refs with
  why the route was used.
- `identifier_resolution_ref`: PMID, PMCID, DOI, title, trial id, guideline id,
  preprint id, and published-version reconciliation.
- `retrieval_count_reconciliation_ref`: count and pagination notes when
  completeness matters.
- `source_acceptance_decision_ref`: retain, reject, or watchlist reason for
  each promoted source.
- `claim_support_map_ref`: exact claim, sentence, figure, table, method, or
  limitation supported by each source.
- `support_strength_matrix_ref`: direct primary, direct guideline,
  method precedent, contextual background, contradictory, weak, or not
  applicable.
- `citation_integrity_notes`: missing metadata, mismatch, stale source,
  preprint version gap, review-vs-primary issue, or official-source need.

The chain can recommend confirm/drop and route-back candidates. It cannot turn
a source into citation authority or a literature verdict.

## Claim-Citation-Quality Loop

Use `claim_citation_quality_loop_ref` in writing and review whenever prose,
citations, and evidence quality must be checked together.

Loop rows should include:

- `claim_id` and affected section, sentence, figure, table, or caption.
- `claim_text_current` and `claim_text_candidate`.
- `evidence_refs`: data, analysis, display, table, source, or literature refs.
- `citation_refs`: PMID, DOI, guideline, trial, registry, or source refs.
- `support_strength`: direct primary, guideline, method precedent,
  background, contradictory, weak, or none.
- `claim_strength_calibration`: show, demonstrate, suggest, indicate, may, or
  could.
- `quality_issue`: unsupported, overclaimed, under-cited, mismatched source,
  stale source, review-used-as-primary, missing official source, figure drift,
  table drift, or method mismatch.
- `citation_quality_action_matrix_ref`: keep, downgrade, add source, replace
  source, route to `medical-research-lit`, route to statistics/table/figure,
  route to review, human gate, or stop.
- `owner_gate_handoff_ref`: downstream MAS/domain owner surface that must record
  acceptance, rejection, owner receipt, typed blocker, or route-back.

Writing uses the loop before final prose. Review uses the same loop
adversarially before clearing a readiness label.
