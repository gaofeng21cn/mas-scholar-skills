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

## AI-First Professional Quality Floor

Use `professional_ai_quality_floor_ref` when an existing `medical-*` skill needs
the shared AI-first quality floor. This is a skill-method rule, not a new
module, runtime owner, receipt signer, or authority surface.

Minimum refs:

- `critique_as_repair_hint_ref`: convert each critique into a concrete repair
  hint with affected claim/source/table/figure/data/package refs, the narrowest
  owning skill route, and the evidence needed to clear the issue.
- `reusable_lesson_ref`: extract a reusable lesson only when the same issue can
  improve future writing, review, literature, statistics, table, submission,
  data, or display work; keep one-off observations as local findings.
- `triggered_meta_review_ref`: request a second-pass review when evidence
  conflicts, route-back repeats, a claim crosses discipline boundaries, or the
  candidate would otherwise approach domain truth, owner receipt, typed blocker,
  artifact authority, or readiness.
- `opportunistic_knowledge_prefetch_ref`: prefetch only immediately useful
  source, guideline, journal instruction, data dictionary, citation graph,
  figure/table, prior review, or rerun receipt refs. Do not start broad research
  or provider/runtime setup just because it might help later.
- `claim_type_ref`: classify manuscript, figure, table, statistic, data,
  package, or citation claims as descriptive, association, prediction, causal,
  methods, governance, or submission/package claims before deciding strength.
- `graph_warnings_ref`: flag unsupported, stale, circular, missing-source,
  source/body drift, denominator drift, visible-payload drift, or package
  mismatch risks as refs-only warnings.
- `annotation_to_source_regeneration_ref`: map a reviewer annotation back to
  the source/data/evidence/citation/analysis/display/package refs needed for
  repair instead of treating the annotation as free-text feedback.
- `project_local_ledger_pointer_ref`: record a local ledger pointer, locator,
  or hash only as provenance for a candidate package. It is not an owner ledger,
  MAS truth, or source-readiness verdict.
- `rerun_receipt_ref`: consume rerun, re-render, re-query, re-export, or
  re-check receipts as evidence only when input refs, fingerprints, command
  refs, and limits are visible. A rerun receipt is not runtime readiness,
  owner acceptance, artifact authority, or publication readiness.
- `verdict_candidate`, `route_back_candidate`, and
  `stop_or_continue_recommendation`: AI-consumable candidate judgment and next
  route, stopping only at real authority or human gates.

Keep the quality floor inside the active professional skill that owns the
judgment. Module catalogs and contracts should carry only ids, ref families,
receipt shapes, owner routes, hashes, and no-authority flags.

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
- `template_selection_ref`: the selected Display Pack template, paper-local
  grammar, source asset, or explicit new-render choice and the panel jobs it may
  support.
- `template_or_asset_ref`: exact per-panel template or source asset ref, or
  `not_applicable:new_render` when no reusable asset is consumed.
- `semantic_match_ref`: variable, comparison, uncertainty, visible-claim, and
  evidence-role compatibility between the source and the intended panel.
- `adaptation_mode`: `declared_template`, `schema_adapted_template`,
  `reference_guided_new_render`, or `original_new_render`. Use
  `original_new_render` exactly when `template_or_asset_ref` is
  `not_applicable:new_render`; set both semantic/transform refs to
  `not_applicable:no_reusable_source` and do not invent provenance.
- `transform_delta_ref`: data mapping, geometry, crop, label, palette,
  annotation, and panel-order differences from the selected source.
- `source_data_ref`: canonical data or analysis-output ref that regenerates the
  panel.
- `degradation_reason`: `none` or the explicit asset, transform, renderer, or
  export limitation that reduced fidelity.
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
- `panel_render_receipt_ref`: one receipt per rendered panel with
  `template_or_asset_ref`, `semantic_match_ref`, `adaptation_mode`,
  `transform_delta_ref`, `source_data_ref`, code/command refs, output path,
  `degradation_reason`, and panel-level known limits.
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

## Template And Asset Adaptation Ref

Use the provenance fields above for every reused template or source asset.
Confirm semantic compatibility before rendering, then select exactly one
adaptation mode:

- `declared_template`: the input already satisfies the declared template
  contract without changing scientific meaning.
- `schema_adapted_template`: the template remains the rendering basis, while
  schema, mappings, geometry, or annotations are explicitly transformed.
- `reference_guided_new_render`: the source is only a visual or workflow
  reference and the current panel is rendered anew from current evidence; keep
  the actual source ref visible.
- `original_new_render`: no reusable template or source asset is consumed. Set
  `template_or_asset_ref` to `not_applicable:new_render`; set both
  `semantic_match_ref` and `transform_delta_ref` to
  `not_applicable:no_reusable_source` rather than fabricating a source.

Do not mechanically copy a plotting script and replace only its data path. Do
not silently stretch an asset, substitute a renderer, or omit transform
differences. Treat a weak semantic match as a repair hint and choose a better
template or a new render so progress can continue. Route back only for missing
required evidence, missing/unreadable/blank output, invalid geometry,
unsupported visible claims, or another hard contract failure.

## Display Pack Receipt Chain

Use `contracts/display-pack-receipt-templates.json` when a figure handoff needs a
machine-readable minimum shape for the Display Pack loop:

- `figure_contract_ref`: the claim, evidence, archetype, template-selection,
  renderer-decision, export, forbidden-drift, and owner-gate handoff refs before
  drawing.
- `render_receipt_ref`: the pack id, template id, renderer family, render mode,
  output refs, layout sidecar ref, per-panel template/asset provenance,
  adaptation and source-data refs, degradation reason, and known limits after
  the pack render.
- `visual_qa_receipt_ref`: final-size export, export lint, grayscale or
  color-vision readback, label economy, route-back items, and owner-gate target
  after inspecting the real output.

These receipts are candidate refs only. A passed render receipt or visual QA
receipt is not MAS artifact authority, owner acceptance, typed blocker,
current-package freshness, quality verdict, or publication readiness.
Do not emit a render receipt before an actual pack render or invent pack,
template, layout-sidecar, output, or degradation values to complete a draft;
keep pre-render decisions in `figure_contract_ref`.
`original_new_render` does not make pack runtime fields optional: if the pack
does not return real template and layout-sidecar refs, do not emit a Display
Pack receipt for that paper-local render.

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

## MAS Journal-Family Pack Foldback

Use this matrix when a MAS stage packet names journal-family quality packs.
The pack name is only a route hint. Keep the elastic professional judgment in
the existing `medical-*` skill, and keep MAS contracts limited to pack refs,
output refs, owner route, receipt shape, and forbidden-authority flags.

| Pack ref | Owning professional skill | Candidate refs to return |
| --- | --- | --- |
| `journal_response_pack` | `medical-submission-prep` with `medical-manuscript-review` for critique | `review_comment_inventory_ref`, `response_route_ref`, `difficult_case_route_ref`, `author_input_needed_ref`, `reviewer_response_candidate_ref`, `route_back_candidate` |
| `manuscript_argument_pack` | `medical-manuscript-writing` with `medical-manuscript-review` for independent pressure test | `one_sentence_argument_ref`, `section_job_map_ref`, `paragraph_flow_review_ref`, `claim_strength_calibration_ref`, `paper_narrative_arc_ref`, `route_back_candidate` |
| `statistical_reporting_pack` | `medical-statistical-review` | `statistical_question_ref`, `denominator_and_missingness_ref`, `effect_size_and_uncertainty_ref`, `assumption_diagnostic_ref`, `statistical_action_matrix_ref`, `route_back_candidate` |
| `data_availability_fair_pack` | `medical-data-governance` with `medical-submission-prep` for journal-facing wording | `data_code_availability_ref`, `fair_metadata_gap_ref`, `restricted_access_route_ref`, `dataset_citation_ref`, `owner_decision_ref`, `route_back_candidate` |
| `citation_integrity_pack` | `medical-research-lit` with `medical-manuscript-review` for claim critique | `literature_retrieval_contract_ref`, `identifier_resolution_ref`, `claim_support_map_ref`, `support_strength_matrix_ref`, `citation_integrity_notes`, `route_back_candidate` |
| `figure_evidence_contract_pack` | `medical-figure-design`, `medical-figure-style`, `medical-figure-composer`, and `medical-table-design` as needed | `figure_contract_template_ref`, `panel_evidence_chain_ref`, `source_metric_ref`, `export_lint_ref`, `visual_qa_receipt_ref`, `table_qc_ref`, `route_back_candidate` |
| `paper_reader_grounding_pack` | `medical-manuscript-review` with `medical-manuscript-writing` for repair | `paper_narrative_arc_ref`, `claim_citation_quality_loop_ref`, `pdf_evidence_extraction_ref`, `reader_risk_ref`, `claim_warning_route_back_candidate_ref` |
| `paper_presentation_pack` | `medical-submission-prep` for package audit and `medical-figure-design` for asset evidence | `presentation_asset_manifest_ref`, `crop_qa_ref`, `pptx_reopen_qa_ref`, `slide_readability_ref`, `speaker_notes_context_ref`, `route_back_candidate` |

These refs are candidate handoffs. They do not create MAS study truth, artifact
authority, owner receipts, typed blockers, human gates, quality verdicts,
current-package authority, submission readiness, or publication readiness.
- `citation_quality_action_matrix_ref`: keep, downgrade, add source, replace
  source, route to `medical-research-lit`, route to statistics/table/figure,
  route to review, human gate, or stop.
- `owner_gate_handoff_ref`: downstream MAS/domain owner surface that must record
  acceptance, rejection, owner receipt, typed blocker, or route-back.

Writing uses the loop before final prose. Review uses the same loop
adversarially before clearing a readiness label.
