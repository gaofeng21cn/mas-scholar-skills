---
name: medical-figure-design
description: "Use when a MAS figure stage operating prompt needs professional medical figure design for a new or materially repaired manuscript figure, from figure intent through evidence refs, panel plan, renderer/template selection, draft render, visual QA, polish, and reviewer handoff. This professional specialist skill is maintained in mas-scholar-skills; MAS keeps stage authority, runtime authority, artifact authority, visual-audit authority, owner receipts, typed blockers, and publication readiness."
---

# Medical Figure Design

Use this skill when a paper-facing figure needs to be created or materially
repaired from zero to one.

This professional specialist skill is maintained in `mas-scholar-skills` /
MAS Scholar Skills. MAS stage operating prompts may sync and consume it, while MAS
still owns stage routing, study truth, display registry, figure semantics,
visual audit receipts, owner receipts, typed blockers, human gates, current
packages, and publication readiness.

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

## Figure Contract

Before writing plotting code, produce or refresh a compact contract:

- `core_conclusion_ref`: the one-sentence claim the figure must defend.
- `evidence_chain_ref`: data, cohort, statistic, model, table, or prior result
  refs for every panel.
- `figure_archetype`: `quantitative_grid`, `schematic_led_composite`,
  `image_plate_plus_quant`, `asymmetric_mixed_modality`, or
  `clinical_evidence_summary`.
- `renderer_decision_ref`: chosen renderer family, why it fits, and why
  alternatives were not used.
- `journal_export_contract_ref`: target size, editable text requirement,
  export formats, source-data expectation, and image-integrity notes.

If the contract cannot name the core conclusion and evidence chain, route back
before drawing. If MAS or the user has not fixed a backend, recommend one from
the paper-local contract and record the reason; once recorded, keep it exclusive
for rendering, preview, export, and visual QA.

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

### 4. Template And Backend Selection

Choose the figure grammar only after intent and refs are clear.

- Prefer MAS Display Pack and paper-local figure grammar for paper-facing
  evidence figures.
- Use ScholarSkills display refs as enhancement or reference material, not MAS
  owner authority.
- Prefer `r_ggplot2` for manuscript evidence figures when the current display
  contract supports it.
- Use `python` or `html_svg` only when the figure class and contract allow it.
- Evidence figures may use only `python` or `r_ggplot2`.
- Illustration figures may use `python`, `r_ggplot2`, or `html_svg`.
- `html_svg` is never allowed for evidence figures.

If the selected backend cannot run, stop and fix the environment or route a
blocker. Do not silently fallback to a different renderer family.

Record the selected grammar in a figure manifest before polishing:

- figure intent
- panel ids
- evidence refs
- statistics and annotations
- renderer family
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

Check:

- whether the main comparison is obvious in a few seconds
- labels, units, sample sizes, uncertainty, and baselines
- panel order and visual hierarchy
- color accessibility and grayscale robustness
- text size after likely manuscript scaling
- overlap, truncation, clipped legends, duplicate titles, and prose cards
- whether every visible claim is supported by evidence refs
- grayscale and color-vision robustness for categorical encodings
- figure legend consistency with visible variables, units, sample sizes, and
  statistical annotations
- source-data and code traceability for every evidence panel

Every failed check must be fixed, downgraded to a named caveat, routed back to
the correct owner, or carried as a human gate.

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
- panel plan
- figure contract, style brief, and renderer decision refs
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
- Do not make synthetic data look like evidence.
- Do not use ScholarSkills display refs, gallery screenshots, or template
  matches as visual quality authority.
- Do not put long caveats, governance notes, or workflow explanations inside
  visible figure text.
- Do not claim publication readiness, owner acceptance, current-package
  authority, or artifact truth from a local render.
