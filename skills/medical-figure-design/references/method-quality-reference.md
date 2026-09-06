## External Learning Quality Floor

Read [upstream provenance](upstream-provenance.md) when updating these methods
or checking source/license status; it separates historical learning from the
reviewed current revisions and from installed rendering dependencies.

### Task-Scoped Figure Decisions

Choose panel roles for the actual scientific question, with no fixed panel
count or order. A setup, control, primary result, validation or boundary panel
earns space through its evidence role. Independent scientific panels may be
drawn on one fixed canvas; separately rendered panels use the existing composer
route. Keep the current task's accepted backend when it remains suitable.

Preserve raw data, transformations and display output as distinct evidence.
Missing values, zero values and censoring are not interchangeable. State the
independent replication unit and the uncertainty definition; comparable panels
use comparable encodings unless a declared scientific reason requires unequal
layout. Measure the actual plot-area geometry after rendering, not just the
outer axes boxes or intended grid dimensions.

Verify physical dimensions in the final export. Tight cropping can alter them,
a scaling factor is not DPI, and editable SVG text is not proof that its font
is embedded. An interaction needs a direct comparison; overlapping error bars
do not establish equivalence or absence of a difference. Retain both the
scientific visual assessment and the deterministic artifact checks.

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

Historical ResearAI/OpenScience `f120290` contributes `claimType` + `graphWarnings`
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
outline -> single-canvas or separate-panel render -> whole-figure review loop. Do not copy their Python
helpers, runtime setup, or full style guide into MAS; use MAS/paper-local
renderers and only the minimum professional checks needed for the current
figure. If a helper is unavailable, keep the same judgment loop with current
repo tools instead of adding a dependency.

When `medical-manuscript-writing` or `medical-manuscript-review` supplies a
`paper_narrative_arc_ref`, treat its `fig1_hook_ref`, `figure_moves_ref`,
`missing_panels_ref`, and `kill_list_ref` as inputs to the figure contract. The
figure skill can turn a defensible figure claim into panels; it cannot decide
the paper's final story or publication readiness.
