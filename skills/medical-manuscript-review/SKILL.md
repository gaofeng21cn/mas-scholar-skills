---
name: medical-manuscript-review
description: "Use when a MAS review stage operating prompt needs professional adversarial medical review over a manuscript, draft, claim-evidence package, reviewer response, figure/table set, or citation surface. Covers claim downgrade, citation repair routing, reviewer action matrix, SCI clinical-registry review, revision-delta audit, and route-back candidates. This professional specialist skill is maintained in mas-scholar-skills; MAS keeps stage authority, runtime authority, artifact authority, owner receipts, typed blockers, and publication readiness."
---

# Medical Manuscript Review

Use this skill when a manuscript-facing draft, claim-evidence package, display
set, or reviewer feedback needs strict medical review before the line can
advance.

This professional specialist skill is maintained in `mas-scholar-skills` /
MAS Scholar Skills. MAS stage operating prompts may sync and consume it, while MAS
still owns stage routing, study truth, review ledgers, evidence ledgers,
publication eval, controller decisions, owner receipts, typed blockers, human
gates, current packages, and publication readiness.

Shared refs: use `docs/no-authority-boundary.md` for owner-boundary limits and
`references/professional-quality-ref-templates.md` for reusable refs-only
quality-floor handoff shapes. Keep specialty details in this skill; do not copy
long boundary or checklist text here.

Sibling skill routes are `medical-manuscript-writing` for manuscript repair,
`medical-figure-design` for material figure work, `medical-research-lit` for
PubMed-oriented literature discovery, `medical-statistical-review` for
statistical pressure tests, `medical-table-design` for table repair, and
`medical-submission-prep` for submission and reviewer-response checks, and
`medical-data-governance` for clinical data manifests, source readiness support,
version impact, privacy/access tiers, and lifecycle guardrails.

Review is not copyediting. It is an adversarial medical pressure test over
claims, evidence, displays, citations, methods, limitations, and route
readiness.

## Route Contract

Key question:

- What should the strict AI reviewer send back before the line can advance?

The success condition is a reviewer action matrix that maps each concern to one
of:

- accept as-is
- claim downgrade
- citation repair
- manuscript repair
- display repair
- analysis-campaign route-back
- decision route-back
- human gate
- stop

Unsupported claims must be downgraded or routed back before finalize.

## MAS Authority Boundary

Use MAS owner surfaces before declaring a review concern closed:

- `paper/claim_evidence_map.json`
- `paper/evidence/evidence_ledger.json`
- `paper/review/review_ledger.json`
- reviewer action matrix
- citation ledger and source provenance surfaces
- `paper/display_registry.json`
- display-to-claim map
- `paper/figure_semantics_manifest.json`
- `artifacts/publication_eval/latest.json`
- `artifacts/controller_decisions/latest.json`
- owner receipt, typed blocker, human gate, or route decision surfaces

Quality verdicts, publication readiness, and submission readiness must close
through MAS owner surfaces. A contradiction flag, rubric note, external review
artifact, ScholarSkills hint, or provider completion is only an input until MAS
records the owner decision.

## AI-Native Reviewer Judgment

Be an expert medical publication judge first and a rubric user second. Use
quality packs, contracts, and checklists as the minimum floor for traceability,
coverage, and route-back language. Do not limit review to enumerated checklist
failures.

Name material concerns even when no existing rubric item names them:

- misleading emphasis or weak contribution logic
- clinically implausible interpretation
- journal-fit or audience-risk problems
- hidden negative or equivocal results
- reviewer skepticism caused by the whole paper rather than one isolated field

When open-ended judgment adds a concern, bind it to evidence refs, citation
refs, affected text/display locations, route decision, typed blocker target, or
human gate target.

## External Learning Quality Floor

This skill absorbs useful reviewer patterns from Nature-style reviewer skills
and K-Dense-style peer-review skills:

- extract a shared manuscript fact base before judging;
- evaluate significance, originality, technical soundness, readability, and
  audience fit separately;
- simulate multiple reviewer emphases when that helps identify hidden risk;
- consolidate findings into a cross-review synthesis instead of averaging them
  away;
- tie every major concern to a route-back action and owner surface.

Use these patterns as stricter review discipline, not as a foreign journal
verdict. The skill may say a Nature-style case is weak, but it cannot claim an
editorial decision or publication readiness.

K-Dense `scientific-critical-thinking` contributes evidence-quality discipline
to review, not a separate authority layer. Use it to name internal validity,
external validity, construct validity, statistical conclusion validity, bias,
confounding, reproducibility, ethics, and reporting-standard problems when the
manuscript evidence supports the concern.

K-Dense `scholar-evaluation` contributes evaluation discipline for positioning,
novelty, rigor, and likely reviewer reception. Use it to make the review
decision more explicit: separate "interesting but unsupported", "technically
adequate but low contribution", "clinically useful but under-explained", and
"submission-fit issue" findings. These are route-back labels, not editorial
accept/reject decisions.

For claim/citation disputes, read
`references/professional-quality-ref-templates.md` and use
`claim_citation_quality_loop_ref` plus `citation_quality_action_matrix_ref`.
These refs let the AI reviewer recommend keep, downgrade, replace, route back,
human gate, or stop without issuing a quality verdict, owner receipt, typed
blocker, or publication readiness claim.

OpenScience main `f120290` contributes local-first claim-warning discipline, not
a second skill catalog. For disputed manuscript, figure/table, or citation
claims, add refs-only `claim_type_ref` and `graph_warnings_ref` before the
reviewer action matrix when source material permits it. Use `claimType` to
separate descriptive, association, prediction, causal, methods, and governance
claims; use `graphWarnings` for unsupported, stale, circular, missing-source, or
source/body drift risks. When a reviewer annotation points at a claim gap, add
`annotation_to_source_regeneration_ref` that maps the annotation back to source
refs, claim-evidence refs, citation refs, or the missing ref family, then emit
`claim_warning_route_back_candidate_ref` if repair is needed. These refs are
review hints only: they are not reviewer receipts, MAS owner receipts, typed
blockers, publication verdicts, or quality verdicts.

`skill_pack_governance_policy_ref` may record allowed scope, dependency or
permission notes, and stage-use policy for the synced skill pack. Do not copy an
OpenScience skill catalog, create a new MAS default skill source, or treat this
governance ref as owner acceptance.

AcademicForge/Claude Science paper-narrative contributes a handling-editor deck
review pattern. Use it when the draft has figures, captions, or a manuscript
PDF: infer the pitch and figure claims from the work itself, then review the
full deck for `fig1_hook_ref`, `deck_arc_ref`, `figure_moves_ref`,
`missing_panels_ref`, and `kill_list_ref`. These are action-matrix inputs only;
they do not create editorial acceptance, reviewer receipt, publication
readiness, or a MAS owner verdict.

AcademicForge/Claude Science pdf-explore contributes a PDF evidence-extraction
boundary. For long PDFs or supplements, parse once, then use outline, scan,
grep, and crop refs to find evidence. Keep extraction separate from judgment:
`pdf_evidence_extraction_ref` can support review findings, but MAS still owns
source acceptance, citation acceptance, claim repair, and readiness labels. Do
not block review on Claude Science helper availability; use the current
workspace's PDF reader, text extraction, image crop, or manual page readback and
record the method as part of the extraction ref.

## Fact Base And Reviewer Lanes

Before scoring or writing findings, build `review_fact_base_ref` with:

- manuscript type and submission posture;
- central claim and bounded contribution;
- evidence shown and evidence missing;
- claimed clinical or scientific significance;
- likely interested readership;
- visible technical gaps;
- citation, figure, table, and methods surfaces under review.

For important manuscripts, include three reviewer lanes:

- `technical_reviewer_lane`: methods, statistics, reproducibility, data
  availability, and figure/table support.
- `significance_reviewer_lane`: novelty, clinical meaning, prior-work
  distinction, and overclaim risk.
- `reader_reviewer_lane`: title/abstract clarity, nonspecialist readability,
  narrative flow, terminology, and journal/audience fit.
- `validity_bias_lane`: internal/external/construct/statistical validity,
  confounding, selection bias, measurement bias, attrition, selective reporting,
  and causal overreach.
- `scholar_evaluation_lane`: contribution, novelty, clinical usefulness,
  reviewer reception risk, and journal-fit pressure without issuing an
  editorial verdict.
- `handling_editor_deck_lane`: Figure 1 hook, deck arc, figure moves, missing
  panels, kill list, and boldest defensible main-figure claim.

Then write `cross_review_synthesis_ref` that names consensus blockers,
divergent emphases, and the narrowest next route.

When the target journal or article type is known, add
`venue_review_expectation_ref`: the reviewer standards being used, their source,
and which expectations are formatting-only versus scientific blockers. Venue
templates calibrate the review; they do not authorize acceptance or rejection.

## Knowledge Obligations

Before reviewing, recover and name:

- manuscript or manuscript-facing draft under review
- active study charter and locked claim boundary
- claim-evidence map and evidence ledger refs
- display-to-claim map, figure/table registry, and display freshness refs
- study reference context and citation ledger refs
- prior reviewer findings and unresolved concerns
- current publication eval and controller decision refs when present
- known contradiction flags and their provenance
- PDF parse/outline/scan/grep/crop refs when the review relies on a manuscript
  PDF, supplement, or external article PDF rather than canonical text files.

If reference context or citation ledger refs are missing, record that as a
review blocker and create a citation repair request. Do not fill the gap with
memory-only claims.

## Prediction Model External Validation Review

For prediction-model external-validation manuscripts, run a specific review
lane before clearing draft, paper, or submission readiness. Major or blocker
findings include:

- unclear source-model origin, missing equation, missing coefficient table,
  missing predictor coding, or missing baseline survival / absolute-risk
  extraction;
- validation cohort described without source years, eligibility, diabetes or
  disease definition, endpoint ascertainment, follow-up completeness, censoring
  policy, missingness, or survey-weighting policy when relevant;
- discrimination reported as if it proves calibrated absolute risk;
- calibration slope, O:E, Brier score, grouped calibration, or recalibration
  claims lacking uncertainty or denominator support;
- a title that foregrounds implementation status such as "fixed" or "locked"
  when the clinically useful contribution is higher-risk identification,
  recalibration need, or external validation;
- a results narrative that repeats the same grouped-risk-gradient sentence in
  adjacent subsections instead of separating risk stratification from absolute
  calibration;
- discussion that invokes population transportability without anchoring the
  interpretation to Table 1 case-mix or event-rate differences when those
  differences are available;
- performance tables that label development-cohort external-validation-only
  calibration intercept/slope as "not estimated" instead of "not applicable";
- a cohort-level two-point calibration figure presented as if it were the
  calibration plot when grouped calibration by validation quantile is available;
- risk groups that mix development-cohort bins with validation self-quantiles
  without showing occupancy and calibration separately;
- decision-curve or threshold-utility figures shown while Methods/Results say
  clinical utility was not estimated, or while severe miscalibration makes the
  threshold basis unverified;
- discussion that stops at "transportability failed" without explaining the
  bounded interpretation, case-mix/support possibilities, baseline-risk
  mismatch, and why clinical deployment or absolute-risk communication is not
  supported.

Route these findings to `medical-statistical-review`, `medical-table-design`,
`medical-figure-design`, `medical-manuscript-writing`, `analysis-campaign`, or
human gate as appropriate. Do not smooth them into prose-only caveats.

## SCI Clinical Registry Review

For observational, cohort, registry, real-world, or descriptive atlas
manuscripts, include a `sci_clinical_registry_review` matrix. This is a
scientific review layer, not a prose check.

Cover these domains:

- `clinical_contribution`
- `reporting_metadata`
- `population_applicability`
- `variable_ascertainment`
- `source_heterogeneity`
- `display_to_claim`
- `risk_of_bias_or_grade_signal`

Each row should include `concern_id`, `domain`, `status`, `severity`,
`finding`, `evidence_refs`, and `required_disposition`. Any `major` or
`blocker` concern blocks publication-quality readiness and must route to write,
analysis-campaign, decision, or human gate.

Red flags include:

- missing enrollment window, source-specific data window, or data lock date
- missing inclusion/exclusion flow, ethics/consent, funding, COI, or data
  availability
- missing BMI calculation, adult/child standard, or diagnostic ascertainment
- non-model descriptive registry Methods that retain `Model building` or
  `Validation framework` headings instead of reviewer-facing descriptive
  analysis, data-check, or sensitivity-analysis headings
- missing diagnostic-variable ascertainment table when disease-control,
  hypertension, dyslipidemia, complication-burden, or phenotype labels are
  derived from structured records
- adult BMI classes promoted while age distribution or under-18 proportion is
  unresolved
- adult-focused conclusions without adult/known-age sensitivity when age is
  missing, implausible, or includes children
- selected diagnostic-field positivity described as prevalence or burden
- descriptive registry figure/table titles or legends using burden for
  populated diagnostic fields, variable availability, or subcohort-only
  screening instruments instead of recorded-field, availability, symptom-status,
  or co-occurrence wording
- figure legends that use instruction-style boundary phrasing such as `should
  not be interpreted as` instead of manuscript-ready declarative phrasing such
  as `are not prevalence estimates`
- figure titles, legends, captions, or section headings that claim variables
  not shown or overstate the design
- Results sentences that explain why a finding is clinically useful instead of
  reporting the finding and leaving interpretation to Discussion
- figure legends that import `direct_message`, panel-message, glossary, or
  instruction-style semantics into the submission legend instead of a compact
  visible-variable, denominator, and boundary statement
- PDF figure pages that show a figure heading with a blank figure region, or
  figure captions that retain double identifiers such as "F1 / Figure 1: F1"
- main-text PDF tables that are unreadable because the table is too wide,
  over-wrapped, or should route to supplementary material
- missingness/availability atlas too thin for the manuscript's registry-atlas
  claim
- phenotype-atlas or treatment-gap drafts that list groups and rates but do not
  articulate a medical discovery contract, such as burden-medication
  discordance, structured risk-treatment mismatch, trajectory pattern,
  site/service variation, or a documented reason these are out of scope
- severe-glycemia low-intensity, cardiometabolic protection gap, renal-risk
  protection gap, service-priority tier, or potential overtreatment language
  without exact eligibility, medication-class mapping, denominator, and
  unavailable-evidence boundary
- recorded medication gaps presented without exact numerator, denominator,
  medication-source, class-mapping, and medication-field-present sensitivity
- guideline-linked treatment-gap wording without guideline-specific
  eligibility, contraindication, age/eGFR target, and source refs
- transition-stability results reported as a single percentage without
  trajectory categories, plausible clinical/service interpretations, or a
  documented decision that transition analysis is out of scope
- site support used as if it were site-level gap variation, external
  validation, or service-performance evidence
- discussion that only defends limitations, enumerates too many isolated
  findings, or fails to compress findings into registry structure, adult
  metabolic phenotype, and subcohort clinical-depth themes
- internal workflow, tool pipeline, or manuscript self-evaluation language in
  article body
- revision-response phrases such as `reviewer-triggered` in Methods, Results,
  figure legends, tables, or supplements
- residual internal phrases such as "formal analytic data-lock date remains"
  in manuscript body text

Restrained wording can reduce claim risk, but it cannot clear these red flags
by itself.

## Revision Delta Audit

When review follows user, mentor, or reviewer feedback, include a
`revision_delta_audit` before clearing any publication or submission readiness
label.

Name:

- `previous_manuscript_ref`
- `revised_manuscript_ref`
- `prior_blocker_refs`
- `blocker_dispositions`
- `substantive_delta_summary`
- `unresolved_items_route`

Cleaner prose, refreshed packaging, repeated cautious caveats, or route-back
bookkeeping are not substantive revision unless they materially close the hard
items.

## Citation Repair

Review must treat citation quality as part of medical rigor.

When a finding needs external biomedical literature search, source
verification, guideline lookup, PMID lookup, DOI lookup, or citation repair,
use:

```bash
opl connect pubmed search --query "<query>" --limit <n> --json
```

Record returned `pubmed_source_refs` and
`pubmed_connector_invocation_ref`. The results are candidate refs only. MAS
still owns source screening, contradiction handling, claim-evidence mapping,
review ledger updates, route-back decisions, and publication-quality verdicts.

Open a citation repair request when:

- a claim has no citation or only a weak background citation
- a citation does not match population, endpoint, method, or time horizon
- a guideline, reporting standard, or validation claim needs a primary or
  official source
- a cited source is stale where recency matters
- source metadata, DOI, PMID, journal, year, or full-text provenance is
  incomplete

Do not fabricate citations, infer guideline requirements from memory, or use
third-party summaries as authority when official or primary sources are needed.

For each citation repair request, add the affected claim to
`claim_citation_quality_loop_ref` and assign one
`citation_quality_action_matrix_ref` action: keep, downgrade, add source,
replace source, route to `medical-research-lit`, route to writing/statistics/
table/figure repair, human gate, or stop.

## Reviewer Action Matrix

Write findings as an action matrix. Each row should include:

- concern id
- affected claim, section, figure, table, or citation
- evidence path or missing evidence path
- citation path or missing citation path
- claim-citation-quality loop row and citation-quality action
- claim type, graph warnings, and annotation-to-source regeneration refs when a
  finding depends on claim/source repair
- domain and status for `sci_clinical_registry_review` rows
- severity: `blocker`, `major`, `minor`, or `note`
- disposition
- readiness label blocked: `draft-ready`, `paper-ready`, or `submission-ready`
- owner surface that must record closure
- reviewer lane: `technical`, `significance`, `reader`, `citation`,
  `display`, `submission`, `validity_bias`, or `scholar_evaluation`
- required evidence to close, not just suggested wording

The matrix should be specific enough for another executor to continue without
transient chat.

## Route-Back Closeout

Review is complete only after it names the narrowest honest next route:

- route to `analysis-campaign` when the claim may be supportable but needs a
  bounded analysis slice
- route to `write` when evidence is adequate but wording, structure, caveats,
  limitations, citations, or display wording need repair
- route to `medical-figure-design` when figure intent, display-to-claim,
  renderer, or visual QA needs material repair
- route to `finalize` only when no blocker remains and package readiness is the
  main work
- route to `decision` when novelty, rigor, evidence, or contradiction gaps
  cannot be closed inside writing
- escalate a human gate when review would change study boundary, external
  release, submission authorization, journal direction, or non-public data use

## Forbidden Actions

- Do not review as friendly copyediting while unsupported claims remain.
- Do not treat contradiction flags as publication verdicts; they are review
  signals only.
- Do not advance to finalize with orphan claims, missing evidence refs,
  unresolved citation gaps, or unclosed reviewer blockers.
- Do not directly edit `manuscript/current_package` as final repair when
  canonical paper sources or runtime-control refs are stale.
- Do not convert external harness results, provider completion, dashboards, or
  ScholarSkills hints into MAS quality authority.
- Do not let OPL or this skill own review truth, publication readiness, memory
  writeback authority, or owner receipts.

## Closeout Packet

Before leaving review, write or refresh a closeout packet with:

- reviewer action matrix
- evidence repair and citation repair requests
- paper narrative arc findings: Fig 1 hook, deck arc, figure moves, missing
  panels, and kill list when figures drive the review
- PDF evidence extraction refs used, each marked as extraction evidence only
- claim downgrades with old claim, new claim, evidence refs, and affected text
  or display locations
- contradiction flags used, each marked as review signal only
- claim-warning refs used, each marked as refs-only review signal
- remaining blockers and blocked readiness label
- reusable critique lesson, if any
- route-back recommendation with the narrowest next route
- human-gate request if boundary, release, submission, or data-use authority
  changes
- MAS owner surface refs that must prove closure
