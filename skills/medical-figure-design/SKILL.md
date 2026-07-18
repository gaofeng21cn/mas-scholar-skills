---
name: medical-figure-design
description: "Use when a MAS figure stage operating prompt needs professional medical figure design for a new or materially repaired manuscript figure, or when routing figure work between style-only and compose-only display subskills. Full figure work runs figure intent through evidence refs, panel plan, renderer choice, optional template reference, draft render, visual QA, composition, polish, and reviewer handoff. This professional specialist skill is maintained in mas-scholar-skills; MAS keeps stage authority, runtime authority, artifact authority, visual-audit authority, owner receipts, typed blockers, and publication readiness."
---

# Medical Figure Design

Use this skill when a paper-facing figure needs to be created or materially
repaired from zero to one, or when a figure request needs routing between the
display subskills.

This professional specialist skill is maintained in `mas-scholar-skills` /
MAS Scholar Skills. MAS stage operating prompts may sync and consume it, while MAS
still owns stage routing, study truth, display registry, figure semantics,
visual audit receipts, owner receipts, typed blockers, human gates, current
packages, and publication readiness.

Shared refs: use `docs/no-authority-boundary.md` for owner-boundary limits and
`references/professional-quality-ref-templates.md` for reusable refs-only
quality-floor handoff shapes. Keep specialty details in this skill; do not copy
long boundary or checklist text here.
When MAS supplies `figure_evidence_contract_pack` or
`paper_presentation_pack`, consume
`references/professional-quality-ref-templates.md#mas-journal-family-pack-foldback`.
Keep renderer, source-data, statistics, export, crop, and visual-QA judgment in
the display skill family; MAS keeps artifact and visual-audit authority.

Receipt loop: design owns the refs-only `figure_contract_ref` handoff, the
display pack returns `render_receipt_ref`, display QC returns the deterministic
`layout_qc_receipt_ref`, and style/composer return `visual_qa_receipt_ref`,
`figure_style_review_ref`, or `figure_composition_review_ref` for MAS/domain
owner consumption. None of these refs is artifact authority, owner receipt,
visual-audit authority, typed blocker, or publication readiness.

For every new or materially repaired paper-facing figure, emit a
`professional_figure_workflow_ref` conforming to
`contracts/professional-figure-workflow.schema.json`. Bind this Skill's exact
source ref/version/SHA, the figure-contract input SHA, consumed rule refs, and
the final PNG/PDF byte hashes. OPL catalog or hosted-interface unavailability
may fall open to the currently materialized canonical Skill source; it must not
fall open to ungoverned free drawing. Missing or stale consumption evidence is
non-blocking for stage liveness, but remains quality debt and prevents quality,
export, or publication-readiness claims until repaired.

Thin display subskill routes:

- Use `medical-figure-style` for style-only visual grammar, readability,
  claim-title truth, label economy, color accessibility, final-scale inspection,
  and export-visible style QA on an existing figure or panel.
- Use `medical-figure-composer` for compose-only multi-panel assembly, layout,
  panel-letter/gutter/resized-text checks, crop-level consistency, and composite
  export QA from existing rendered panels.
- Keep `medical-figure-design` as the orchestrator for full figure work. It
  may call style QA, render/panel repair, compose QA, and final visual review in
  sequence, but the outputs remain refs-only candidate handoffs.

Sibling skill routes are `medical-manuscript-writing` for manuscript narrative
repair, `medical-manuscript-review` for adversarial review,
`medical-research-lit` for PubMed-oriented literature discovery,
`medical-statistical-review` for statistical annotation checks,
`medical-table-design` for table/figure consistency, and
`medical-submission-prep` for export and submission package checks, and
`medical-data-governance` for clinical data manifests, source readiness support,
version impact, privacy/access tiers, and lifecycle guardrails.

MAS `figure-polish` is only the polish/review phase entry for an already scoped
figure. It is not an independent specialist source.

## Core Rule

Medical figures are evidence surfaces. The AI executor owns the scientific
figure reasoning first:

- what claim the figure should support
- which evidence refs are allowed
- what each panel means
- what the figure must not claim
- whether the rendered result can survive reviewer scrutiny

Scripts, renderers, MAS Display Pack, OPL Connect, Fabric, or ScholarSkills
display material may execute bounded searches, renders, manifest checks, or QA
tasks. They must not decide claims, invent evidence, silently switch backend, or
turn a local render into MAS owner authority.

## AI-First Figure Judgment

The skill should decide whether the requested figure is scientifically needed,
which claim it may carry, whether a table/prose/supplement is a better surface,
whether negative or equivocal evidence must be visible, and whether a visual QA
failure should route back before owner review.

Emit `figure_verdict_candidate`, `figure_table_decision_ref`,
`negative_or_equivocal_display_ref`, `visual_qa_route_ref`,
`final_scale_visual_qa_ref`, `annotation_to_source_regeneration_ref`,
`route_back_hard_evidence_ref`, and `route_back_candidate` when the evidence,
claim, renderer, export, or visual readability is not defensible. These refs are
candidate judgments only; they do not create visual-audit authority, artifact
authority, owner receipt, typed blocker, current-package authority, or
publication readiness.

## External Learning Quality Floor

This skill absorbs the useful parts of Nature-style figure skills and broad
scientific-agent figure skills without importing their runtime or authority:

- start from a figure contract before plotting;
- classify the figure archetype before deciding whether a template is useful;
- prefer a strong hero panel plus supporting panels over equal-size grids when
  the science needs hierarchy;
- keep the selected renderer family stable after it is recorded;
- inspect the actual exported figure at final manuscript scale;
- produce reviewer-facing evidence refs, not just an image file.

Use K-Dense-style scientific visualization skills as package/tool references
and Nature-style figure skills as workflow references. Do not copy their
mandatory graphical-abstract or "generate many figures" defaults into MAS.
Medical figures must earn their place through claim and evidence.

K-Dense `scientific-visualization`, `matplotlib`, and `seaborn` contribute
plotting discipline: choose the visualization from the data question, preserve a
stable renderer family, inspect the final exported figure at manuscript scale,
and verify accessibility and source-data traceability. They do not create a
requirement to use Python or generate extra figures when MAS has chosen another
paper-local renderer.

SciPilot Figure contributes data-question-first plot selection and visual QA
discipline: use `data_profile_ref` to profile variables, sample sizes, grouping
structure, missingness, distributions, outliers, and the intended reader
question before choosing a chart; record `plot_selection_candidate_ref` for the
chart choice; warn on small-n mean bars, dual axes, pie charts, 3D charts,
rainbow/jet palettes, unexplained error bars, chartjunk, categorical lines, and
missing continuous colorbars; use `export_lint_ref` plus
`final_size_grayscale_preview_ref` to inspect final-size exports; split
`programmatic_figure_audit_ref` from `ai_visual_review_ref`; and treat CJK
glyphs, special symbols, and negative signs as export risks. These are
refs-only quality checks and route-back hints, not a requirement to install
SciPilot, import its scripts, make Python the default backend, or accept any
external runtime as authority.

K-Dense `scientific-schematics` and `infographics` contribute a useful
schematic discipline for mechanism, workflow, and graphical-abstract candidates:
define the message hierarchy, separate evidence-bearing panels from explanatory
illustration, preserve source refs for every quantitative element, and keep
icons or simplified shapes subordinate to the manuscript claim. Use this only
when the figure contract calls for a schematic or explanatory shell; do not turn
an evidence figure into a decorative infographic.

For a concrete lightweight handoff shape, read
`references/professional-quality-ref-templates.md` and use
`figure_contract_template_ref` plus `panel_evidence_chain_ref`. The template is
refs-only guidance; it is not a MAS figure artifact, visual audit receipt, owner
receipt, typed blocker, or publication readiness surface.

OpenScience main `f120290` contributes `claimType` + `graphWarnings`
claim-warning and annotation-repair patterns for figure work, not an additional
figure runtime or skill catalog.
When a figure contract, caption, panel label, or reviewer annotation carries a
scientific claim, add refs-only `claim_type_ref` and `graph_warnings_ref` to
classify the claim and flag unsupported, stale, circular, missing-source, or
visible-payload drift risks. If a reviewer annotation must be traced back to
evidence, data, source, or claim-evidence refs, add
`annotation_to_source_regeneration_ref` as a repair hint. Use
`skill_pack_governance_policy_ref` only for allowed scope, dependency/
permission notes, and stage-use policy. These refs do not create visual-audit
authority, owner receipt, typed blocker, publication readiness, or a second
skill catalog.

Use `professional_ai_quality_floor_ref` for the display-family JIT quality
floor. Convert critic review into `critique_as_repair_hint_ref` with the
affected panel, source data, statistic, caption, claim, renderer, export, or
composition ref and the smallest repair route. Extract `reusable_lesson_ref`
only for repeatable figure-design failures. Trigger `triggered_meta_review_ref`
when visual claims conflict with data, figure/table/statistics disagree,
route-back repeats, or a local render would otherwise be treated as authority.
Use `opportunistic_knowledge_prefetch_ref` only for immediately needed source,
table, statistic, journal, style reference, gallery, or rerun/render receipt
refs. Consume `project_local_ledger_pointer_ref` and `rerun_receipt_ref` as
local provenance and re-render/check evidence only when fingerprints, command
refs, and known limits are visible.

AcademicForge/Claude Science figure-style and figure-composer contribute
figure-correctness patterns only. Absorb them as refs-only design discipline:
data fidelity before chart choice, claim-title truth checks, excluded-row
handling, comparable-condition separation, displayed `n` and fixed context,
label economy, color-vision robustness, render-then-verify, and a multi-panel
outline -> panel render -> composite review loop. Do not copy their Python
helpers, runtime setup, or full style guide into MAS; use MAS/paper-local
renderers and only the minimum professional checks needed for the current
figure. If a helper is unavailable, keep the same judgment loop with current
repo tools instead of adding a dependency.

When `medical-manuscript-writing` or `medical-manuscript-review` supplies a
`paper_narrative_arc_ref`, treat its `fig1_hook_ref`, `figure_moves_ref`,
`missing_panels_ref`, and `kill_list_ref` as inputs to the figure contract. The
figure skill can turn a defensible figure claim into panels; it cannot decide
the paper's final story or publication readiness.

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
  plotting/data and right `annotation_lane` bounds, overlap, clipping, minimum
  spacing, canvas-overflow and safe-inset checks, and `overflow_count=0`.
- `layout_qc_receipt_ref`: deterministic machine-readable geometry evidence
  bound to the final PNG/PDF SHA-256 values, dimensions, safe inset, lane
  bounds, bbox-registry hash, and regression fixture refs. It is not a MAS
  visual-audit receipt or submission authority.
- `single_generation_source_ref`: one structured generation source that drives
  the figure, caption, and catalog/manifest fields in the same build rather than
  relying on manually synchronized copies.
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

## MAS Authority Boundary

Use MAS owner surfaces before declaring a figure accepted:

- `paper/claim_evidence_map.json`
- `paper/evidence/evidence_ledger.json`
- `paper/display_registry.json`
- `paper/figure_semantics_manifest.json`
- `paper/figure_polish_lifecycle.json`
- display-to-claim map
- visual-audit receipt
- review ledger
- publication eval
- controller decision
- owner receipt
- typed blocker
- human gate

Do not write or imply authority through chat text, local preview files,
renderer logs, template catalog matches, ScholarSkills refs, provider
completion, or passing tests. Do not directly write publication eval,
controller decisions, owner receipts, typed blockers, human gates,
`current_package`, runtime queues, provider attempts, or other domain truth
surfaces from this skill.

## Workflow

Before the numbered workflow, record the `medical-figure-design` invocation and
its exact Skill identity. Finalize that refs-only receipt only after it binds the
exact final PNG/PDF bytes. Selecting a template is optional; consuming this
professional Skill is not.

### 1. Figure Intent And Claim

Start by writing the figure intent in plain scientific terms:

- figure id or proposed figure id
- manuscript location or role
- target claim, reviewer concern, or descriptive question
- clinical or scientific comparison the reader must understand
- what the figure must not claim

If the claim is missing, too broad, or not accepted by MAS evidence surfaces,
route to `medical-manuscript-writing`, `medical-manuscript-review`,
`analysis-campaign`, `decision`, or human gate before drawing.
If a reviewer annotation names a visual/source mismatch, add
`annotation_to_source_regeneration_ref` that points back to the source data,
claim-evidence map, figure contract, or missing ref family before attempting a
style-only fix.

### 2. Evidence Refs

Bind the figure to concrete refs before choosing a visual form:

- data or cohort ref
- analysis, statistic, or model-output ref
- claim-evidence ref
- display registry or figure semantics ref when present
- prior reviewer concern or route reason when the figure is a repair

Missing refs are blockers, not styling issues. Do not fill missing evidence
with template defaults, synthetic labels, or caption prose.

If the caption, methods note, or reviewer handoff needs biomedical literature,
guideline, PMID, DOI, or citation support, route it to MAS
`research-integrity-reference-verification`. Record `mas_provider_lookup_ref`
and `pubmed_source_refs` only as inputs to MAS evidence, citation, and review
workflows. Do not invent citations, PMIDs, DOIs, guideline requirements, or
source metadata.

### 3. Panel Plan

Plan panels as scientific units. For every panel, name:

- panel id
- supported claim or sub-question
- required variables and units
- comparison hierarchy
- statistical annotation or uncertainty requirement
- expected visible text
- what belongs in caption, manifest, or review ledger instead of the figure

For evidence figures, keep in-figure text limited to panel labels, axis and tick
labels, legend labels, and necessary statistical annotations. Do not embed a
figure title, subtitle, prose footer, source paragraph, caveat paragraph, or
workflow narration. Put those items in the manuscript caption. Purpose-built
graphical abstracts are exempt from this evidence-figure rule.

For each panel, add a `panel_job`: discovery, mechanism, validation,
comparison, robustness, clinical relevance, source flow, or limitation. Drop
panels that do not carry a distinct job. For a multi-panel figure, choose the
hero panel first and make the remaining panels support or qualify that hero
claim.

For main-text multi-panel figures, use this minimal loop:

1. Write `multi_panel_outline_ref`: one sentence the figure must make true,
   Figure-1-style hook or hero panel, claim-carrying panel, supporting or
   limiting panels, and panel jobs.
2. Render panels as separate scientific units. Each `panel_render_receipt_ref`
   must name its own data refs and visible claim.
3. Compose the figure and inspect the composite plus per-panel crops before
   review handoff.
4. Record `composite_review_ref` findings as outline-level fixes or panel-level
   fixes, then rerender only affected panels.

Stop the loop when remaining findings are minor refs-only reviewer hints. Do
not regenerate clean panels or add labels to a passing panel.

### 4. Template And Backend Selection

Choose the figure grammar only after intent and refs are clear.

For every reused template or asset, record the provenance and adaptation before
rendering:

- confirm the selected source is semantically compatible with the panel job;
- use `declared_template` only when the current input matches the declared
  template contract without a schema or meaning change;
- use `schema_adapted_template` when the template remains the rendering basis
  but input schema, mappings, geometry, or annotations change;
- use `reference_guided_new_render` when a source is only a visual or workflow
  reference and the panel is rendered anew from current evidence; keep the
  actual source ref visible;
- use `original_new_render` when no reusable template or source asset is
  consumed; set `template_or_asset_ref` to `not_applicable:new_render`, and set
  both `semantic_match_ref` and `transform_delta_ref` to
  `not_applicable:no_reusable_source` instead of fabricating reference
  provenance;
- record all transformations and the canonical source-data ref; never copy a
  plotting script and replace only its data path;
- record an explicit degradation reason when the intended asset, transform, or
  export cannot be preserved. Do not silently stretch, substitute, or switch
  renderer family.

An imperfect semantic match is normally a design repair hint: select a better
template, move to `reference_guided_new_render` when a real reference remains
in use, or use `original_new_render` when no reusable source is consumed while
the candidate can still advance. Stop or route back only when required
evidence is missing, the output is missing/unreadable/blank, geometry is
invalid, the visible claim becomes unsupported, or another hard
figure-contract condition fails.

- Prefer MAS Display Pack and paper-local figure grammar for paper-facing
  evidence figures.
- Use ScholarSkills display refs as enhancement or reference material, not MAS
  owner authority.
- Do not import SciPilot scripts, requirements, or Python helpers as authority;
  adapt only the reusable review pattern into the paper-local renderer contract.
- Prefer `r_ggplot2` for manuscript evidence figures when the current display
  contract supports it.
- Use `python` or `html_svg` only when the figure class and contract allow it.
- Evidence figures may use only `python` or `r_ggplot2`.
- Illustration figures may use `python`, `r_ggplot2`, or `html_svg`.
- `html_svg` is never allowed for evidence figures.
- If Python is selected, prefer explicit Matplotlib object-oriented figure/axes
  code for publication figures. Seaborn is acceptable for statistical draft
  plots or simple paper figures only when its aggregation, error bars, hue/order,
  and axis labels are explicit and reproducible.

If the selected backend cannot run, stop and fix the environment or route a
blocker. Do not silently fallback to a different renderer family.

### 4a. Deterministic Render Lock

Before the first render, bind `deterministic_render_ref` to resolved font files
and their SHA-256 values, the selected renderer family and version, and the
explicit non-interactive `headless_backend` or export engine for each target
format. Validate required glyph coverage before rendering. A missing or
hash-mismatched font, unavailable backend, or renderer-family drift is a hard
figure-contract failure: repair the environment or emit `route_back_candidate`;
never substitute a system font, interactive backend, or different renderer
silently.

Lock `final_size_layout_ref` before fitting labels: set the target canvas width
and height, final output units, and final text sizes first. Resolve long labels
in this order: use an evidence-faithful short form; measure the unwrapped source
string with the final renderer/font; automatically wrap at semantic boundaries
only when that width exceeds the allocated label lane; then rotate only when the
selected grammar still requires it. Keep source strings free of manual line
breaks. Apply `wrap_policy=automatic_semantic_wrap` on the fixed final canvas
and declared font size; do not shrink text to suppress overlap or pass QA.

After each final renderer draw (`fig.canvas.draw()` plus
`get_window_extent(renderer)` in Matplotlib, or the backend-equivalent final
layout pass), fill `text_extent_safe_area_ref`. Set
`renderer_draw_complete=true` and calculate a text bounding box for
`artist_scope=all_text_artists`: axis-inside and axis-outside text artists,
categorical and tick labels, titles, annotations, legend text, and sample-size
labels. For each panel, register the expected artist ids and every measured bbox
plus its clip bbox. Reserve a right `annotation_lane` that is geometrically
separate from the plotting/data lane. Normalize boxes to `final_canvas` and
check registry completeness, pairwise overlap, canvas overflow, clipping,
minimum spacing, lane containment, and the explicit `safe_inset`. A pass
requires a complete `artist_extent_report` and `overflow_count=0`.

Export PNG/PDF at the locked final size with `bbox_inches=None` or the
backend-equivalent fixed canvas. `tight_layout`, `bbox_inches=tight`, `clip_on`,
and tight-crop output are not safe-area proof. Run the long-string,
extreme-value, and full-width regression fixture, then bind final file SHA-256,
dimensions, safe inset, lane bounds, bbox-registry hash, and check counts in the
deterministic `layout_qc_receipt_ref`. Recheck the rendered DOCX/PDF page when
embedded and record it in `composed_page_check`; a missing or failed required
page check cannot pass this machine geometry gate. The receipt does not create
MAS visual or submission authority.

Bind `single_generation_source_ref` to one structured paper-local source for
data mappings, labels, annotations, caption payload, and catalog/manifest
metadata. The same build must derive the figure, caption, and catalog/manifest
from that source so a manual edit cannot leave those surfaces out of sync. This
ref records provenance only and does not create artifact or MAS authority.

Record the selected grammar in a figure manifest before polishing:

- figure intent
- panel ids
- evidence refs
- statistics and annotations
- renderer family
- plotting library and version when Python is used
- schematic or infographic role, if any, with explicit evidence-bearing versus
  explanatory-only panel boundaries
- exports
- QA checks
- owner-gate status

### 4b. Reference-Guided Candidate Loop

When a figure is important enough for a manuscript main figure, use an
AI-first candidate loop:

1. `figure_contract_ref`: bind the figure to the accepted claim, evidence refs,
   allowed comparisons, forbidden claim drift, and owner-gate target.
2. `style_brief_ref`: summarize the intended reader, journal class, figure
   archetype, visual hierarchy, allowed palette, and forbidden claim drift.
3. `reference_selection_ref`: cite visual references or local gallery refs as
   style targets only. They are not data truth or template authority.
4. `candidate_set_ref`: create one to three candidate plans or renders when the
   design space is open.
5. `critic_review_ref`: judge the candidates against evidence, readability,
   reviewer risk, color accessibility, and export constraints.
6. `selected_candidate_ref`: record the selected route and the concrete fixes
   still required before owner review.

For a small repair, one candidate is enough. For a new main figure, skipping the
brief/reference/candidate/critic loop is allowed only when MAS has already
provided an equivalent figure contract.

### 5. Draft Render

Render the first draft through a deterministic script or MAS display command
when available. Record:

- source data ref
- render script or command
- renderer family
- deterministic render, final-size layout, and single-generation-source refs
- `source_fingerprint` over the source data, render code/config, caption and
  catalog/manifest source, font files, and renderer/backend versions
- output paths
- display-pack `render_receipt_ref` when a pack renderer produced the draft
- sidecar or lock refs
- known draft limitations

The first render and its `render_receipt_ref` are refs-only draft evidence, not
acceptance or artifact authority.
Do not create a `render_receipt_ref` before an actual pack render or invent
pack, template, layout-sidecar, output, or degradation values to fill one;
keep pre-render decisions in the figure contract.
`original_new_render` does not make pack runtime fields optional. If a pack did
not return real template and layout-sidecar refs, do not emit a Display Pack
receipt for that paper-local render.
Treat checked-in `example_render_receipt.json` files marked `example_only=true`
as non-issued schema fixtures, never as render evidence or permission to fill
runtime fields before execution.

Generate the paper-local raster/vector pair from the same source and render
lock whenever both formats are required, commonly PNG plus PDF. Record
`paired_export_qa_ref`; do not treat a passing PNG as proof that the PDF has the
same payload, geometry, labels, annotations, crop, or font behavior. For a
Matplotlib-backed PDF, an explicit setting such as `pdf.fonttype=42` is one
acceptable embedding policy example; other renderer families must use their
equivalent explicit font-embedding and subtype checks. Matplotlib is not the
default or sole backend.

### 6. Visual QA

Open the rendered output and inspect the actual figure, not only logs or code.

Keep two QA lanes separate:

- `programmatic_figure_audit_ref`: deterministic checks for missing glyphs,
  CJK/negative-sign rendering, bound font-file hashes, clipped text,
  `annotation_headroom`, `boundary_clipping`, `line_text_intersection`,
  `tick_label_overlap`, the renderer-drawn `text_extent_safe_area_ref`, complete
  bbox registry, lane separation, minimum spacing, fixed-canvas export, and the
  SHA-bound `layout_qc_receipt_ref`, plus file format, DPI, font
  embedding/subtype, final dimensions, and source/export traceability.
- `export_lint_ref`: export-contract lint for file format, DPI, font embedding,
  final dimensions, and traceability before any owner handoff.
- `paired_export_qa_ref`: separate raster/vector checks for payload, dimensions,
  labels, annotations, crop bounds, font behavior, and output fingerprints.
- `visual_qa_preview_ref` / `critic_review_ref`: AI or human visual review of
  a rasterized final-size preview for legend/data overlap, annotation headroom,
  edge clipping, lines crossing text, tick-label overlap, panel alignment,
  visual hierarchy, grayscale/color-vision separation, and whether the chart
  answers the intended data question.
- `final_scale_visual_qa_ref`: the final manuscript-scale readback of the
  actual raster output and a rasterization of the vector output; use it before
  owner handoff, not as a substitute for owner visual-audit authority.
- `ai_visual_review_ref`: the AI visual-review lane only; it cannot replace the
  deterministic audit lane or owner visual-audit authority.

Do not infer visual correctness from the programmatic lane or infer export
integrity from the visual lane. Both must report independently over the actual
final-size outputs.

Before owner handoff, remove prior outputs and render caches, then run the same
pinned build twice. For each run, record `clean_rebuild_consistency_ref` with a
SHA-256 `source_fingerprint` over source data, render code/config, caption and
catalog/manifest source, bound font files, and renderer/backend versions, plus
byte-level `output_fingerprints` for every required export. Fix or omit volatile
export metadata such as creation timestamps instead of normalizing mismatched
files after rendering. The two clean runs must have identical source and output
fingerprints. Any drift routes back to the source/render owner; do not waive it
as a refs-only caveat.

Check:

- whether the main comparison is obvious in a few seconds
- whether the chart type follows the data question, variable types, grouping,
  sample size, and distribution rather than habit or template reuse
- whether excluded rows are omitted from summaries or visibly marked as
  exclusions
- whether compared conditions are genuinely comparable or visually separated
- whether summary marks state `n`, replication unit, and fixed context when
  those affect interpretation
- whether sentence-style titles and panel labels are true for every plotted row
- whether each quantitative claim uses the same canonical value in panel,
  caption, and manuscript
- whether the label set meets the floor for mark identity and the ceiling for
  narrative annotations
- labels, units, sample sizes, uncertainty, and baselines
- panel order and visual hierarchy
- color accessibility and grayscale robustness
- text size after likely manuscript scaling
- overlap, truncation, clipped legends, duplicate titles, and prose cards
- annotation headroom above confidence intervals, bars, points, brackets, and
  significance labels at the fixed target dimensions
- boundary clipping on every canvas and panel edge, including strokes, error
  bars, labels, legends, and crop boxes
- line, curve, gridline, or connector intersections that cross text or
  annotations and make them ambiguous
- tick-label overlap, truncation, collision with axis titles, or overlap created
  by rotation at final manuscript size
- complete renderer-drawn text extents for all axis-inside and axis-outside text,
  annotations, legends, and sample-size labels, with the declared safe inset and
  zero overflow
- automatic measured-width wrapping without source-level manual breaks
- separate plotting/data and right annotation lanes; complete per-panel bbox
  registries; zero overlap, canvas overflow, clipping, minimum-spacing, and
  safe-inset violations
- fixed-canvas final PNG/PDF checks and deterministic SHA/dimension/safe-area
  receipt evidence, plus successful checks on the embedded DOCX/PDF page
- missing glyphs, CJK tofu boxes, special-symbol loss, or negative-sign boxes
- whether every visible claim is supported by evidence refs
- whether schematic icons, arrows, or explanatory simplifications preserve the
  evidence boundary instead of implying unshown mechanism or causality
- grayscale and color-vision robustness for categorical encodings
- avoidance of misleading palettes such as rainbow/jet for ordered scientific
  data
- avoidance of small-n mean bars, dual Y axes, pie or 3D charts, chartjunk,
  categorical lines, unexplained error bars, and missing colorbars for
  continuous mappings
- figure legend consistency with visible variables, units, sample sizes, and
  statistical annotations
- vector/source export availability or documented raster DPI reason
- raster/vector pair parity and PDF font embedding/subtype evidence when both
  formats are required
- figure, caption, and catalog/manifest agreement from the same structured
  generation source
- identical source and output fingerprints from two clean rebuilds
- source-data and code traceability for every evidence panel

For phenotype-atlas heatmaps or service-review maps, figure titles, panel
titles, captions, legends, and axis labels must carry the same bounded
terminology as the manuscript. If the paper has moved from generic treatment
gaps to recorded risk-treatment mismatch, update figure metadata and renderer
defaults together. Shorten heatmap axis labels at manuscript scale rather than
letting long clinical phrases overlap; move detailed definitions to the legend,
caption, or table note.

Warnings alone are not default blockers. Route back only when hard evidence
shows missing refs, unsupported claims, unreadable or misleading visual output,
programmatic audit failure, or an AI/human visual review failure that cannot be
repaired inside the figure contract. Otherwise record the warning as a
refs-only caveat or reviewer hint. Use `route_back_hard_evidence_ref` for that
threshold; do not create a MAS typed blocker or owner receipt from this skill.

### 7. Polish

Use polish for presentation-only repair:

- layout
- labels
- ordering
- sizing
- palette
- spacing
- legends
- export settings
- manuscript-safe visible text

Polish must not change data, statistics, cohort labels, model results, claim
strength, or manuscript methods labels. When requested polish would change
meaning, route to analysis-campaign, write, review, decision, or human gate.

## Reviewer Handoff

Before handoff, produce a compact reviewer packet:

- figure intent and supported claim
- evidence refs and data/statistic refs
- figure contract template and panel evidence chain refs
- panel plan
- figure contract, style brief, and renderer decision refs
- deterministic render, final-size layout, text-extent safe-area, layout-QC
  receipt, single-generation-source, paired-export QA, and clean-rebuild
  consistency refs
- claim type, graph warning, and annotation-to-source regeneration refs for any
  figure claim at risk
- critique-as-repair hints, triggered meta-review refs, and reusable lessons
- opportunistic prefetch refs or rerun/render receipts consumed as evidence
- selected template/backend and why it fits
- candidate set and selected draft/final export refs
- visual QA findings and fixes
- remaining caveats, blockers, or human decisions
- next MAS route

The reviewer handoff is candidate evidence. MAS owner surfaces still decide
whether the figure is accepted, routed back, blocked, or ready for downstream
package work.

## Forbidden Actions

- Do not create a figure before claim and evidence refs are named.
- Do not switch renderer family because a package or environment fails.
- Do not silently substitute fonts, font files, headless backends, export
  engines, or renderer versions after the deterministic render lock is recorded.
- Do not shrink fixed final-size text below the readability floor to rescue long
  categorical or tick labels; apply automatic semantic wrapping at the declared
  font size after measuring the unwrapped renderer width, then rotate only when
  justified, or move detail to the caption. Do not encode wrapping as manual
  source-string line breaks.
- Do not treat `tight_layout`, `bbox_inches=tight`, `clip_on`, or an unclipped
  preview as proof that all renderer-drawn text stays inside the safe inset, and
  do not use tight crop to replace `bbox_inches=None` or an equivalent fixed
  canvas.
- Do not hand-edit figure, caption, and catalog/manifest copies independently
  when they are required to share one generation source.
- Do not pass deterministic closeout after only one clean rebuild or when any
  required output fingerprint differs between the two clean runs.
- Do not make Python, SciPilot, Matplotlib, Seaborn, SciencePlots, Plotly, or
  any external plotting runtime the default backend unless the paper-local
  figure contract selected it.
- Do not import external scripts or generated checks as MAS owner authority.
- Do not make synthetic data look like evidence.
- Do not use ScholarSkills display refs, gallery screenshots, or template
  matches as visual quality authority.
- Do not put long caveats, governance notes, or workflow explanations inside
  visible figure text.
- Do not claim publication readiness, owner acceptance, current-package
  authority, or artifact truth from a local render.
