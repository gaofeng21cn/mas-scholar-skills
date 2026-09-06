---
name: medical-figure-design
description: "Design or materially repair evidence-bound medical manuscript figures; route style-only review and separately assembled panel composition to the existing display specialists."
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

## Method References

When the task needs a method, reporting-standard, source or quality detail beyond the current accepted context, load [method quality reference](references/method-quality-reference.md). Reuse applicable current evidence; load only resources needed by the selected task mode.

## Figure Contract

For a new or materially repaired figure, load [figure contract](references/figure-contract.md): evidence/panel refs, backend eligibility, exact export binding and final embedding projection. Use its connected-accounting requirements only for an actual flow or schematic. A local style repair reuses an applicable accepted contract.

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
guideline, PMID, DOI, or citation support, route it to `medical-research-lit`.
Record `opl_connect_search_ref`, `opl_connect_reference_verification_ref`, and
`pubmed_source_refs` only as candidate inputs to MAS evidence, citation, and
review workflows. OPL Connect owns provider transport and receipts; MAS owns
medical screening and citation acceptance. Do not invent citations, PMIDs,
DOIs, guideline requirements, or source metadata.

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
2. Choose the production path. For a single fixed canvas, render the panels
   together and bind each panel's data refs and visible claim in the figure
   receipt. For separately rendered panels, each `panel_render_receipt_ref`
   names its own data refs and visible claim, then use `medical-figure-composer`.
3. Inspect the final whole figure plus per-panel crops before review handoff.
   A direct fixed-canvas figure does not need a composer invocation or receipt.
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

For every new or changed final render, load [deterministic render](references/deterministic-render.md). It binds fonts, renderer, final size, complete measured text geometry and PNG/PDF bytes. Choose dedicated annotation lanes only when the grammar requires them; unchanged tested renderers use artifact acceptance, while renderer changes use affected regression coverage.

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

Load [visual QA](references/visual-qa.md) for actual final raster/vector inspection and deterministic owner handoff. Keep machine geometry/export checks separate from scientific visual judgment. For deterministic handoff, compare two clean builds in isolated temporary directories without deleting prior user outputs. Rerun only changed outputs and affected checks during repair; preserve still-current accepted evidence.

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
