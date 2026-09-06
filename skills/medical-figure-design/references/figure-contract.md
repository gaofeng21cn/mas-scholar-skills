## Figure Contract

Before writing plotting code, produce or refresh a compact contract:

- `figure_contract_template_ref`: the filled contract shape used for the
  figure handoff.
- `core_conclusion_ref`: the one-sentence claim the figure must defend.
- `evidence_chain_ref`: data, cohort, statistic, model, table, or prior result
  refs for every panel.
- `panel_evidence_chain_ref`: per-panel claim, source, statistic, citation, and
  forbidden-drift refs when the figure has more than one scientific unit.
- `figure_archetype`: `quantitative_grid`, `schematic_led_composite`,
  `image_plate_plus_quant`, `asymmetric_mixed_modality`, or
  `clinical_evidence_summary`.
- `template_selection_ref` (optional): record only the pack template,
  paper-local grammar, or source asset actually consumed and the panel jobs it
  supports. A template is a reference quality floor, not a mandatory layout.
  When no template is used, record only `template_usage.used=false` and a short
  `decision_reason`; do not invent template provenance or an artificial
  `template_id`.
- `template_or_asset_ref`: the exact template or source asset used for each
  panel, or an explicit `not_applicable:new_render` value when no reusable
  asset is consumed.
- `semantic_match_ref`: why the selected template or asset fits the panel's
  variable types, comparison, uncertainty, visible claim, and evidence role;
  record mismatches instead of hiding them behind styling.
- `adaptation_mode`: one of `declared_template`,
  `schema_adapted_template`, `reference_guided_new_render`, or
  `original_new_render`. Pair `original_new_render` only with
  `template_or_asset_ref=not_applicable:new_render`; set both
  `semantic_match_ref` and `transform_delta_ref` to
  `not_applicable:no_reusable_source` for a panel without a reusable source.
- `transform_delta_ref`: the data mapping, geometry, crop, label, palette,
  annotation, or panel-order changes made relative to the selected template or
  asset.
- `source_data_ref`: the canonical source-data or analysis-output ref used to
  regenerate the panel.
- `degradation_reason`: `none` when the intended render is preserved, otherwise
  the explicit missing asset, unsupported transform, renderer limit, or export
  constraint that reduced fidelity.
- `renderer_decision_ref`: chosen renderer family, why it fits, and why
  alternatives were not used.
- `deterministic_render_ref`: exact `font_file_ref` and `font_file_sha256` for
  every selected font, renderer family and version, explicit `headless_backend`
  or export engine, render command/config refs, and a no-silent-fallback policy.
- `final_size_layout_ref`: target canvas width and height, output units, final
  text sizes, and the fixed-font long-label policy. Any categorical or tick
  label whose renderer-measured unwrapped width exceeds its label lane must use
  `wrap_policy=automatic_semantic_wrap` at semantic boundaries on the fixed
  canvas. Keep source labels free of manual line breaks. Evidence-faithful
  shortening may precede wrapping, and justified rotation may follow it, but
  shrinking text is not a passing repair.
- `text_extent_safe_area_ref`: renderer-drawn text-extent evidence using the
  reusable template in
  `references/professional-quality-ref-templates.md#text-extent-safe-area-ref`,
  including a per-panel bbox registry for all text artists, separate
  plotting/data and applicable `annotation_lane` bounds, overlap, clipping, minimum
  spacing, canvas-overflow and safe-inset checks, and `overflow_count=0`.
- `semantic_artist_registry_ref`: for a declared flow, schematic, diagram, or
  connected accounting display, register every visible node, band, bracket,
  connector segment, arrowhead, and associated text artist after the final
  renderer draw. Bind each relation to its encoding and exact artist prefixes.
  Pure statistical plots may record `not_applicable`; a declared flow or
  schematic may not omit this registry.
- `layout_qc_receipt_ref`: deterministic machine-readable geometry evidence
  bound to the final PNG/PDF SHA-256 values, dimensions, safe inset, lane
  bounds, bbox-registry hash, and regression fixture refs. It is not a MAS
  visual-audit receipt or submission authority.
- `single_generation_source_ref`: one structured generation source that drives
  the figure, caption, and catalog/manifest fields in the same build rather than
  relying on manually synchronized copies.
  After any numeric, denominator, estimand, or construct change, invalidate
  render requests whose payload embeds superseded values and rebuild the
  affected figure from this current structured source; visual similarity or a
  successful renderer exit does not prove source currentness.
- `paired_export_qa_ref`: the required PNG/PDF or paper-local raster/vector
  pair, payload and geometry parity, PDF font-embedding/subtype inspection,
  raster dimensions/DPI, per-output fingerprints, and fixed-canvas export with
  `bbox_inches=None` or the backend-equivalent no-tight-crop policy.
- `clean_rebuild_consistency_ref`: receipts from two clean rebuilds using the
  same `source_fingerprint`, with identical per-format `output_fingerprints`;
  any mismatch produces `route_back_candidate` before owner handoff.
- `data_profile_ref`: variable types, usable sample sizes, grouping structure,
  missingness, distribution shape, outliers, and the intended reader question.
- `plot_selection_ref`: why the chart type fits the variable type,
  comparison, uncertainty, sample size, distribution shape, and
  table-vs-figure tradeoff.
- `plot_selection_candidate_ref`: refs-only chart choice candidate, including
  warnings that should remain reviewer hints unless they hit the route-back
  threshold.
- `journal_export_contract_ref`: target size, editable text requirement,
  export formats, source-data expectation, and image-integrity notes.
- `export_lint_ref`: format, DPI, font embedding, dimensions, CJK/symbol glyph,
  clipping, and source/export traceability audit result.
- `final_size_export_ref`: vector/raster format, DPI where raster is required,
  final print dimensions, text-size inspection, and final-scale preview
  readback.
- `final_scale_visual_qa_ref`: final manuscript-scale visual inspection result
  over the actual export, including whether labels, glyphs, panel crops,
  legends, and visible claims survive journal-scale viewing.
- `final_size_grayscale_preview_ref`: final manuscript-scale raster preview and
  grayscale/color-vision separation readback.
- `data_fidelity_ref`: included/excluded rows, grouping rule, summary statistic
  source, and one canonical value per quantitative claim.
- `excluded_rows_ref`: rows excluded or drawn as exclusions, with proof they
  did not enter plotted summaries.
- `comparability_ref`: whether compared arms share cohort, measurement,
  protocol, denominator, and analysis window, or how the figure separates
  non-comparable conditions.
- `replication_and_fixed_context_ref`: displayed `n`, replication unit, and
  any value held fixed in a summary mark or small multiple.
- `claim_title_truth_ref`: each title, threshold, legend label, and panel label
  checked against all plotted rows; any contradiction downgrades the title or
  moves the claim to caption.
- `label_economy_ref`: non-removable identity labels, removable annotations,
  caption-only context, and the final panel label budget.
- `figure_text_policy_ref`: evidence figures must not embed a figure title,
  subtitle, or prose footer. Keep only panel labels, axes/ticks, legends, and
  necessary statistical annotations in the image; move narrative context,
  caveats, sources, and maintenance-sensitive notes to the manuscript caption.
  A purpose-built graphical abstract is explicitly outside this evidence-figure
  text rule.
- `color_vision_check_ref`: grayscale and color-vision separation result for
  categorical and opposing encodings.
- `multi_panel_outline_ref`: one figure claim, hook/hero panel, panel jobs,
  panel order, and layout intent before rendering.
- `panel_render_receipt_ref`: per-panel `template_or_asset_ref`,
  `semantic_match_ref`, `adaptation_mode`, `transform_delta_ref`,
  `source_data_ref`, code/command refs, output, `degradation_reason`, and known
  limits.
- `composite_review_ref`: panel-letter, gutter, resized-text, cross-panel
  consistency, and crop-level violation review.

If the contract cannot name the core conclusion and evidence chain, route back
before drawing. If MAS or the user has not fixed a backend, recommend one from
the paper-local contract and record the reason; once recorded, keep it exclusive
for rendering, preview, export, and visual QA.

### Narrowest Final Embedding Projection

Apply final-scale readability to every paper-facing figure, not only figures
that look dense during authoring. Before rendering, declare the narrowest width
at which the figure can appear in the manuscript or supplement. Project every
text size and every safe inset from the source canvas to that width, then require
the projected values to meet the paper or journal floor. A full-width source
export is not evidence that a later scaled-down embedding remains readable.

Emit `final_scale_projection_ref` with source width, narrowest embedding width,
scale factor, observed source and projected minimum font sizes, required and
target font floors, observed source and projected safe insets, and zero
overflow/collision/spacing violations from the actual final PNG/PDF pair. Run
the same check for all main and supplementary figures. Do not waive it because
a figure uses few panels, and do not pass by shrinking labels, relying on a
tight crop, or checking only a visually dense subset.
The machine shape records `minimum_final_embed_width_inches` and
`minimum_projected_safe_inset_points` explicitly so a consuming workflow can
recompute the projection instead of trusting prose.

### Connected Accounting Flow

When a flow or schematic contains quantitative cohort, record, episode,
participant, specimen, or event states, every count must be connected to the
parent denominator it partitions or transforms. Declare each unit transition,
such as episodes to patients, and test the corresponding denominator identity.
An exclusion box, residual state, or alternative analysis set drawn as an
unconnected satellite is a hard route-back even when the arithmetic itself is
correct.

Emit `flow_accounting_integrity_ref` for every figure. Use
`applicable=false` with a reason for non-accounting figures. For an accounting
flow, record the unit levels, total and connected quantitative-state counts,
unconnected satellite count, denominator-identity result, unit-transition
result, and the machine receipt that proves the drawn edges and arithmetic.
Require all quantitative states connected, zero satellites, all denominator
identities passed, and all unit transitions declared before visual handoff.
The machine fields are `all_quantitative_states_connected`,
`unconnected_satellite_state_count`, `denominator_identities_passed`, and
`unit_transitions_declared`.

For prediction-model external-validation figures, keep the figure grammar tied
to the validation question:

- show discrimination, absolute calibration, and risk distribution/support as
  separate visual jobs unless a contract proves a combined panel is clearer;
- do not use a one-arrow "cohort flow" to compare two cohorts; if the figure is
  a cohort-flow figure, use side-by-side cohort construction columns with
  source population, exclusions or analysis-set restrictions, final analysis n,
  endpoint/event counts, and the shared model-input boundary in the caption or
  a compact final row;
- for cohort-level observed-versus-predicted calibration, choose an axis window
  from the observed and predicted risks being compared; avoid a default 0-1
  probability frame when all informative points occupy the lower-left corner;
- for discrimination summaries such as C-index, do not use a 0-1 bar axis when
  the scientific comparison is a narrow difference around the observed
  estimates; prefer point-style displays with a data-driven y-axis and an
  explicit 0.5 reference only when it helps interpretation;
- for risk probability panels, keep zero when bars encode risk magnitudes, but
  set the upper axis bound from the displayed predicted and observed risks
  rather than defaulting to 0-1 unless the full probability range is the
  scientific message;
- when development-cohort risk bins collapse in the validation cohort, split
  occupancy by development bins from validation-cohort self-quantile grouped
  calibration rather than labeling one as the other;
- when grouped calibration is repaired into a single-panel validation-cohort
  decile plot, make the legend state the decile basis, observed-risk interval,
  and no-threshold caveat directly; do not inherit stale Panel A/Panel B
  legend boilerplate from an older multi-panel variant;
- show observed and predicted risk with denominators or intervals when grouped
  calibration carries the claim;
- do not keep a decision-curve or threshold-utility figure unless the accepted
  evidence includes threshold range, net benefit, calibration basis, and a
  clinical action scenario;
- avoid governance cards or process-summary panels when numeric calibration,
  support overlap, or risk-scale compression is the scientific point.
- before retaining a study-design or cohort-flow main figure, state the
  figure's specific job. If it only restates two cohort sizes already reported
  in text or tables, drop it from the main manuscript or demote it to
  supplementary context; if retained, it must show a real design boundary such
  as fixed-model derivation, harmonization, no-refit validation, endpoint
  accounting, or analysis-set construction.

For every retained flow or schematic, define a relation-to-encoding grammar
before rendering. Use arrows only for directional operations such as
partition/filter or model transfer. Use brackets or segmented bands for
identity, union, membership, and horizon-support relations so an arrow cannot
silently imply temporal order or filtering. Declare an arrow budget, require
zero ambiguous incoming arrows, and derive bracket spans from the exact node
bounds they cover.

The deterministic audit must compute, rather than assert, semantic registry
completeness, artist-kind coverage, canvas and safe-inset containment,
node-text containment, connector-text and connector-unrelated-node
intersections, unauthorized connector crossings, arrowhead-text overlap,
relation-encoding validity, arrow-budget compliance, incoming-arrow
ambiguity, and bracket-span equality. A text-only bbox pass is insufficient,
and fixed zero counts without renderer-derived geometry are invalid evidence.
Bind every node bbox to its registered patch artist, every connector segment
to renderer-derived line/path endpoints, and every bracket span to its
registered renderer-path segments so a second unrendered geometry declaration
or bbox-only proxy cannot substitute for the visible artists. A declared
shared junction must prove a common path prefix and branch point; it may not
silence crossings elsewhere in the grouped connectors.
When a partition is encoded as a segmented band, declare one
`segmented_group_spans` row rather than treating its parent connector as an
ordinary arrow or an unbound line. Bind the relation, source node, one
non-arrow connector, one full-span labeled group header, and the ordered child
nodes. For a horizontal band, require the header span to equal the child union,
children to share one contiguous y-band without gap or overlap, the header
bottom to touch the child top, and the renderer-bound connector terminal to
land on the header top midpoint. The parent label must be non-empty, owned by
the header node, and declared through
`perceptual_anchor.mode=labeled_full_span_header` with
`anchor_position=midpoint`; a first-child, side, bottom, empty, or child-label
anchor is not an acceptable perceptual grouping.

