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
- `data_fidelity_ref`: row inclusion/exclusion rule, grouping rule, summary
  statistic source, and the single canonical value for each quantitative claim.
- `excluded_rows_ref`: rows excluded from analysis or plotted as exclusions,
  with proof they did not enter plotted summaries.
- `comparability_ref`: whether compared arms share cohort, measurement,
  protocol, denominator, and analysis window, or how non-comparable conditions
  are visually separated.
- `replication_and_fixed_context_ref`: displayed `n`, unit of replication, and
  any variable held fixed for a summary mark or small multiple.
- `claim_title_truth_ref`: every title, panel title, legend threshold, and
  label tested against all plotted rows; failed rows force title downgrade or
  caption qualification.
- `label_economy_ref`: non-removable labels, removable labels, caption-only
  context, and the final in-panel label budget.
- `color_vision_check_ref`: grayscale and color-vision separation readback,
  especially for binary/opposing categories.
- `multi_panel_outline_ref`: one figure claim, hook/hero panel, panel jobs,
  panel order, and layout intent.
- `panel_render_receipt_ref`: one receipt per rendered panel with data refs,
  code/command refs, output path, and panel-level known limits.
- `composite_review_ref`: post-composition review of panel-letter placement,
  gutters, resized text, cross-panel consistency, and panel-level violations.
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

For multi-panel main figures, use a light outline -> panel render -> composite
review loop: first write the figure claim and panel outline, then render only
the affected panels, then review the composed figure and crops before handoff.
Do not regenerate clean panels just to make the package look more active.

## Paper Narrative / Figure Deck Arc

Use `paper_narrative_arc_ref` when a draft or figure deck needs story-level
judgment before more prose or more plotting.

Minimum fields:

- `handling_editor_brief_ref`: pitch, audience, central contribution, and the
  most reviewer-salient asset inferred from the current manuscript and captions.
- `fig1_hook_ref`: whether Figure 1 would make a handling editor keep reading,
  plus the boldest defensible Figure 1 claim.
- `deck_arc_ref`: main-figure order such as hook, mechanism, evidence,
  robustness, and application, with supplement/demotion decisions.
- `figure_moves_ref`: panels or claims that belong in a different figure.
- `missing_panels_ref`: concrete analyses, panels, tables, or evidence refs that
  must be produced before the story can carry the claim.
- `kill_list_ref`: figures, panels, repeated claims, or decorative material to
  delete or demote.
- `figure_claim_handoff_ref`: per-figure claims routed to
  `medical-figure-design` for the figure contract and render loop.

The narrative arc is a candidate editorial judgment. It can route work to
writing, review, figure design, statistics, tables, literature, or a human gate;
it cannot issue a manuscript verdict or publication readiness.

## PDF Evidence Extraction Boundary

Use `pdf_evidence_extraction_ref` when a PDF, supplement, report, or article is
source material for literature, review, data governance, or claim repair.

Minimum fields:

- `pdf_parse_once_ref`: parser/tool, file path or source ref, parse time, page
  count, and whether text or image mode was needed.
- `pdf_outline_ref`: embedded outline or manually sampled section map.
- `pdf_scan_ref`: lexical scan terms, candidate pages, and relevance decision.
- `pdf_grep_ref`: exhaustive regex extraction for identifiers such as DOI,
  PMID, accession, figure/table labels, dates, or registry ids.
- `pdf_crop_ref`: page image and crop refs used for figures, tables, axis
  labels, legends, or small values that text extraction cannot preserve.
- `pdf_claim_extract_ref`: extracted claim/value/source plus page, section,
  figure/table, and uncertainty.

PDF extraction is evidence acquisition, not source acceptance. Claude Science
helpers, local parsers, browser/PDF tools, or manual page crops may all produce
these refs; none is mandatory and none replaces the AI evidence judgment. If
parsing, outline, scan, grep, or crop tooling is unavailable, keep the attempt
and reason as a connector/tool gap and continue with the smallest available
readback. Route back only for missing source/data/evidence, authority, or human
hard gates.

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
