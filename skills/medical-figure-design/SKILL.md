---
name: medical-figure-design
description: "Use when a MAS figure stage operating prompt needs professional medical figure design for a new or materially repaired manuscript figure, or when routing figure work between style-only and compose-only display subskills. Full figure work runs figure intent through evidence refs, panel plan, renderer/template selection, draft render, visual QA, composition, polish, and reviewer handoff. This professional specialist skill is maintained in mas-scholar-skills; MAS keeps stage authority, runtime authority, artifact authority, visual-audit authority, owner receipts, typed blockers, and publication readiness."
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

## External Learning Quality Floor

This skill absorbs the useful parts of Nature-style figure skills and broad
scientific-agent figure skills without importing their runtime or authority:

- start from a figure contract before plotting;
- classify the figure archetype before choosing a template;
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
- `renderer_decision_ref`: chosen renderer family, why it fits, and why
  alternatives were not used.
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
- `color_vision_check_ref`: grayscale and color-vision separation result for
  categorical and opposing encodings.
- `multi_panel_outline_ref`: one figure claim, hook/hero panel, panel jobs,
  panel order, and layout intent before rendering.
- `panel_render_receipt_ref`: per-panel data refs, code/command refs, output,
  and known limits.
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
guideline, PMID, DOI, or citation support, get candidate refs through:

```bash
opl connect pubmed search --query "<query>" --limit <n> --json
```

Record `pubmed_source_refs` and `pubmed_connector_invocation_ref`. Use the
returned refs only as inputs to MAS evidence, citation, and review workflows.
Do not invent citations, PMIDs, DOIs, guideline requirements, or source
metadata.

### 3. Panel Plan

Plan panels as scientific units. For every panel, name:

- panel id
- supported claim or sub-question
- required variables and units
- comparison hierarchy
- statistical annotation or uncertainty requirement
- expected visible text
- what belongs in caption, manifest, or review ledger instead of the figure

Keep in-figure text limited to panel labels, axis labels, legend labels,
necessary statistical annotations, and minimal cohort/group notes.

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
- output paths
- sidecar or lock refs
- known draft limitations

The first render is a draft, not acceptance.

### 6. Visual QA

Open the rendered output and inspect the actual figure, not only logs or code.

Keep two QA lanes separate:

- `programmatic_figure_audit_ref`: deterministic checks for missing glyphs,
  CJK/negative-sign rendering, clipped text, overlapping ticks, file format,
  DPI, font embedding, final dimensions, and source/export traceability.
- `export_lint_ref`: export-contract lint for file format, DPI, font embedding,
  final dimensions, and traceability before any owner handoff.
- `visual_qa_preview_ref` / `critic_review_ref`: AI or human visual review of
  the rasterized preview for legend/data overlap, panel alignment, visual
  hierarchy, grayscale/color-vision separation, and whether the chart answers
  the intended data question.
- `ai_visual_review_ref`: the AI visual-review lane only; it cannot replace the
  deterministic audit lane or owner visual-audit authority.

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
- claim type, graph warning, and annotation-to-source regeneration refs for any
  figure claim at risk
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
