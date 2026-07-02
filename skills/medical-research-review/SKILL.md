---
name: medical-research-review
description: "Use when a MAS medical manuscript, draft, claim-evidence package, reviewer response, figure/table set, or citation surface needs adversarial medical review, claim downgrade, citation repair routing, reviewer action matrix, SCI clinical-registry review, revision-delta audit, or route-back closeout. This is the single maintained Codex skill body for MAS medical review in mas-scholar-skills; MAS consumes it while MAS remains the runtime, artifact, owner-receipt, typed-blocker, and publication-readiness authority."
---

# Medical Research Review

Use this skill when a manuscript-facing draft, claim-evidence package, display
set, or reviewer feedback needs strict medical review before the line can
advance.

This skill body is maintained in `mas-scholar-skills` / MAS Scholar Skills as
the single source for the MAS-consumed `medical-research-review` skill. MAS may
sync and consume this skill, but MAS still owns study truth, review ledgers,
evidence ledgers, publication eval, controller decisions, owner receipts, typed
blockers, human gates, current packages, and publication readiness.

Sibling skill routes are `medical-research-write` for manuscript repair,
`medical-research-figure` for material figure work, and `medical-research-lit`
for PubMed-oriented literature discovery.

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

If reference context or citation ledger refs are missing, record that as a
review blocker and create a citation repair request. Do not fill the gap with
memory-only claims.

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

Each row should include `concern_id`, `domain`, `status`, `severity`,
`finding`, `evidence_refs`, and `required_disposition`. Any `major` or
`blocker` concern blocks publication-quality readiness and must route to write,
analysis-campaign, decision, or human gate.

Red flags include:

- missing enrollment window, source-specific data window, or data lock date
- missing inclusion/exclusion flow, ethics/consent, funding, COI, or data
  availability
- missing BMI calculation, adult/child standard, or diagnostic ascertainment
- adult BMI classes promoted while age distribution or under-18 proportion is
  unresolved
- selected diagnostic-field positivity described as prevalence or burden
- figure titles, legends, captions, or section headings that claim variables
  not shown or overstate the design
- missingness/availability atlas too thin for the manuscript's registry-atlas
  claim
- discussion that only defends limitations instead of explaining source
  heterogeneity, clinical meaning, and data-quality roadmap
- internal workflow, tool pipeline, or manuscript self-evaluation language in
  article body

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

## Reviewer Action Matrix

Write findings as an action matrix. Each row should include:

- concern id
- affected claim, section, figure, table, or citation
- evidence path or missing evidence path
- citation path or missing citation path
- domain and status for `sci_clinical_registry_review` rows
- severity: `blocker`, `major`, `minor`, or `note`
- disposition
- readiness label blocked: `draft-ready`, `paper-ready`, or `submission-ready`
- owner surface that must record closure

The matrix should be specific enough for another executor to continue without
transient chat.

## Route-Back Closeout

Review is complete only after it names the narrowest honest next route:

- route to `analysis-campaign` when the claim may be supportable but needs a
  bounded analysis slice
- route to `write` when evidence is adequate but wording, structure, caveats,
  limitations, citations, or display wording need repair
- route to `medical-research-figure` when figure intent, display-to-claim,
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
- claim downgrades with old claim, new claim, evidence refs, and affected text
  or display locations
- contradiction flags used, each marked as review signal only
- remaining blockers and blocked readiness label
- reusable critique lesson, if any
- route-back recommendation with the narrowest next route
- human-gate request if boundary, release, submission, or data-use authority
  changes
- MAS owner surface refs that must prove closure
