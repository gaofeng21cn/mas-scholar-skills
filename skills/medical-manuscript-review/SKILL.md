---
name: medical-manuscript-review
description: "Independently review medical manuscripts, evidence claims, displays and revision deltas for scientific defects and actionable repairs within the declared MAS review scope."
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
For every fresh review, consume the MAS `review_input_snapshot_binding` and read
only the exact `opl_reviewer_input_snapshot_manifest` immutable members. Do not
reopen live manuscript, evidence, citation, display, workspace, or checkout
locators during judgment. Snapshot gaps produce lane-specific refs-only
route-back; they do not create a typed blocker or hosted-action liveness stop.
When MAS supplies journal-family pack refs, use
`references/professional-quality-ref-templates.md#mas-journal-family-pack-foldback`
to route response, argument, citation, reader-grounding, and presentation
judgment back to the existing professional skills instead of creating a new
physical skill.
When MAS supplies `registry_signal_validity_pack` or an
`ehr_registry_signal_validity_ref`, pressure-test the aggregate ref against the
manuscript claims using the single rule at
`references/professional-quality-ref-templates.md#ehr-registry-signal-validity-ref`.
Route gaps to `medical-statistical-review` and its bounded cohort/data input
owners; do not copy the checklist or promote review findings into an independent
signal-validity verdict.

Optional skill-local helper: use `kernel.py` for deterministic review fact-base
schemas, reviewer action matrix skeletons, issue action labels, and
claim-citation-figure matrix scaffolds. It is a no-authority diagnostic helper
only; MAS or the consuming workspace still owns review ledgers, verdicts, owner
receipts, typed blockers, and readiness labels.

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
Reviewer-first route-back means the review names the narrowest next owner
before prose repair: literature/source gaps go to Lit, claim/evidence or
negative-finding gaps go to Write/Stats/analysis, visual gaps go to Display,
data/source-lineage gaps go to Data, and authority questions go to the MAS or
human owner. Do not keep rewriting text when a reviewer route-back is the
honest next action.

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

## AI-First Judgment Contract

Default to AI reviewer judgment over professional publication risk, not to a
contract checklist. The reviewer may emit `verdict_candidate`,
`quality_review_candidate_ref`, `paper_mission_framing_ref`,
`claim_evidence_strength_ref`, `negative_finding_ref`,
`claim_evidence_route_ref`, `route_back_candidate`, and
`stop_or_continue_recommendation` when the manuscript evidence supports that
judgment.

Keep the action modular at the route-back layer: send claim/source gaps to
evidence or lit review, statistical gaps to stats, display gaps to figure
design, table gaps to table design, submission gaps to submission prep, and
source/data gaps to data governance. The AI judgment remains a candidate until
MAS or the consuming owner records reviewer receipt, owner receipt, typed
blocker, human gate, artifact mutation, quality verdict, or readiness.

## Method References

When the task needs a method, reporting-standard, source or quality detail beyond the current accepted context, load [method quality reference](references/method-quality-reference.md). Reuse applicable current evidence; load only resources needed by the selected task mode.

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

For an initial draft, also produce `first_draft_pre_review_ref` across story,
medical interpretation, statistics, terminology, claim-evidence binding,
tables, and figures. Check `terminology_surface_ledger_ref` across manuscript,
table titles, figure legends, CSV headers, machine-readable endpoints, and
supplement. Require `center_sensitivity_claim_binding_ref` when center/site
dependence enters the abstract or conclusion. Consume
`denominator_semantics_matrix_ref` to distinguish eligible, candidate,
resolved, and absolute-count meanings; different percentages may share a real
denominator when their numerator, denominator role, formula, unit, and visual
semantics remain explicit and self-consistent.

Return unresolved items as `quality_debt_candidate_refs` with the narrowest
route back. The fail-open candidate state may be
`completed_with_quality_debt`: ordinary drafting can continue, while a MAS or
domain owner decides whether the debt prevents quality, export, publication,
or submission claims. This review cannot turn quality debt into an authority
verdict, typed blocker, hosted-execution stop, or reviewer receipt.

For a complete initial-draft review, independently consume the exact
`medical_initial_draft_preflight_candidate_ref` from the immutable reviewer
snapshot and recheck its seven gate dispositions, exact refs, unresolved-item
closure, dependency ordering, canonical earliest owner, and no-authority
boundary. Do not accept the authoring invocation's machine status as review
evidence. Reconcile the manuscript, data/statistical/reference/table/display
members actually present in the snapshot with the candidate, including every
expected main Figure 1-N and Table 1-N member and the exact composed
`paper.pdf` when a reader PDF is required. A shared display role cannot stand
in for a missing member. Require the authoring freeze to expose its explicit
`immutable_candidate_snapshot_manifest_locator`; use it only to locate the
canonical member manifest and never include locator text in content identity.

Return an independent review finding and the narrowest route-back when the
candidate is missing, stale, contradictory, or incompletely bound. Review may
confirm candidate-shape evidence; it cannot sign first-draft readiness, replace
the MAS owner receipt, create a typed blocker, or promote provider/render
completion into a quality verdict.

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

## Study-Design Review

For prediction-model external validation, load [prediction-validation review](references/prediction-validation-review.md).

For registry or phenotype-atlas review, load [registry review](references/registry-review.md). Apply its disease-specific examples only when the study population, endpoints and medication scope match; review other registries against their own accepted definitions.

## Epistemic Evidence Context

When the OPL Attempt or domain owner supplies an optional
`epistemic_review_scope_ref`, use it only to locate the manuscript text,
claims, supporting results and references, limitations, and contextual refs
actually reviewed. Record those consumed refs in the review candidate so the
reasoning can be audited and reproduced.

Do not compute a scope digest, build an upstream hash closure, decide receipt
reuse/currentness, or schedule another review. Hashes are optional locator or
stale hints only. Package, layout, checklist, receipt, checkout, model, or Skill
metadata changes do not invalidate a manuscript review unless the reviewed
content or a declared dependency actually changed.

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

When one receipt supersedes another, run
`validate_receipt_version_member_delta()`. Bind distinct previous and current
receipt exact refs, provide both member inventories, and normalize every member
as added, removed, changed, or unchanged. A package digest, receipt summary, or
aggregate count cannot replace member ids with previous/current exact refs.

When an anomaly sensitivity is discussed, run
`validate_anomaly_evidence_parity()` over the exact manuscript, supplement, and
reviewer-response artifacts. The structured flagged count, extreme-value
count, threshold status, source-mutation status, and exact result deltas must be
identical across all three surfaces. Any qualifier or result change routes all
three surfaces back together.

## Citation Repair

Review must treat citation quality as part of medical rigor.

When a finding needs external biomedical literature search, source
verification, guideline lookup, PMID lookup, DOI lookup, or citation repair,
route it to `medical-research-lit`. Record its OPL Connect
`opl_connect_search_ref`, `opl_connect_reference_verification_ref`, and
`pubmed_source_refs` as candidate evidence. Crossref/OpenAlex coverage stays in
`fallback_source_refs`; the review records route-back, not source acceptance.
OPL Connect owns provider transport and receipts. MAS still owns medical source
screening, contradiction handling, claim-evidence mapping, citation acceptance,
review-ledger updates, route-back decisions, and publication-quality verdicts.

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
- paper mission framing and claim/evidence strength refs when the concern is
  about contribution, support level, negative findings, or overclaiming
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
- critique-as-repair hints and any triggered meta-review refs
- opportunistic prefetch refs or rerun receipts consumed as evidence
- artifact, claim, result, reference, limitation, and reproduction refs
  actually inspected, plus the optional owner-provided
  `epistemic_review_scope_ref` locator when available
- exact `medical_initial_draft_preflight_candidate_ref` consumed and the
  independent preflight audit/route-back finding
- `receipt_version_member_delta_ref` for every superseded review receipt
- `anomaly_evidence_parity_ref` when anomaly sensitivities appear in a reviewer
  response
- remaining blockers and blocked readiness label
- reusable critique lesson, if any
- route-back recommendation with the narrowest next route
- human-gate request if boundary, release, submission, or data-use authority
  changes
- MAS owner surface refs that must prove closure
