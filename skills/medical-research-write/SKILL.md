---
name: medical-research-write
description: "Use when a MAS medical-paper line has accepted evidence and needs manuscript writing, revision, claim-evidence mapping, section contracts, citation-integrity work, reviewer-facing prose, figure/table narrative binding, submission-minimal checks, or a route-back decision. This is the single maintained Codex skill body for MAS medical writing in mas-scholar-skills; MAS consumes it while MAS remains the runtime, artifact, owner-receipt, typed-blocker, and publication-readiness authority."
---

# Medical Research Write

Use this skill to turn accepted medical evidence into a faithful manuscript,
reviewable draft, section repair, or writing route-back packet.

This skill body is maintained in `mas-scholar-skills` / MAS Scholar Skills as
the single source for the MAS-consumed `medical-research-write` skill. MAS may
sync and consume this skill, but MAS still owns study truth, manuscript
artifacts, evidence ledgers, owner receipts, typed blockers, human gates,
current packages, and publication readiness.

Sibling skill routes are `medical-research-review` for adversarial review,
`medical-research-figure` for material figure work, and `medical-research-lit`
for PubMed-oriented literature discovery.

## Core Rule

Writing is AI-native medical authorship first and contract filling second.
Use section contracts, claim-evidence maps, reporting checklists, and display
bindings as the minimum evidence floor. Do not let a mechanically complete
template stand in for expert judgment about whether the story is weak,
misleading, under-cited, overclaimed, or aimed at the wrong journal audience.

If evidence is incomplete, contradictory, or too weak, produce one of:

- an explicit evidence gap
- a downgraded claim
- a route back to `experiment`, `analysis-campaign`, `scout`, `review`, or
  `decision`

Do not polish fiction.

## Preconditions

Before serious drafting, confirm or create durable refs for:

- active study charter or equivalent scope contract
- accepted baseline or explicit waiver
- evidence ledger and claim-evidence map skeleton
- current manuscript source or target draft surface
- display/table registry if figures or tables support claims
- reporting guideline family and submission-minimal requirement
- writing profile, defaulting to `general_medical_journal`
- citation style, defaulting to `AMA`

Major claims must trace to durable artifacts. Memory-only numbers, model recall,
or unverified citations are not evidence.

## MAS Owner Surfaces

Use these surfaces as the authority path when present:

- `paper/claim_evidence_map.json`
- `paper/evidence/evidence_ledger.json`
- `paper/section_contracts.md`
- `paper/review/revision_log.md` or review ledger
- `paper/display_registry.json`
- `paper/figure_semantics_manifest.json`
- `paper/results_narrative_map.json`
- `paper/methods_implementation_manifest.json`
- `paper/derived_analysis_manifest.json`
- `paper/manuscript_safe_reproducibility_supplement.json`
- `paper/review/submission_checklist.json`
- MAS publication eval, controller decision, owner receipt, typed blocker, or
  human gate surfaces

This skill can prepare and update manuscript-facing candidate material only when
the active MAS workspace permits it. It cannot sign owner receipts, create typed
blockers, write publication authority, mutate runtime queues, or claim
submission readiness by itself.

## Medical Publication Contract

Default to a general medical journal surface unless the user, study charter, or
submission contract overrides it:

- `writing_profile`: `general_medical_journal`
- `citation_style`: `AMA`
- `submission_minimal_required`: `true`

Record the contract durably in the active writing surface, usually
`paper/section_contracts.md`, `paper/medical_reporting_contract.json`, or the
decision artifact that routed into writing.

Manuscript body, figure titles, captions, and table notes must avoid internal
engineering terms, internal model names, workspace labels, data-freeze labels,
runtime labels, and workflow-status language. Put unresolved author,
affiliation, ethics, consent, funding, conflict, or data-availability gaps in
submission checklists or handoff notes, not in article-body prose.

## Workflow

### 1. Evidence Assembly

Assemble the accepted evidence before prose:

- cohort, endpoint, exposure/intervention, comparator, and outcome definitions
- main analyses, sensitivity analyses, and negative or equivocal results
- source tables, model outputs, run artifacts, and code refs
- figure/table candidates and display-to-claim refs
- prior reviewer findings and unresolved concerns
- current citation ledger and literature gaps

For each intended claim, answer:

- What exact artifact supports it?
- What number, table, figure, or model output supports it?
- What caveat belongs next to it?
- What claim should be downgraded if that evidence is weaker than hoped?

### 2. Section Contract

Write or refresh the manuscript contract before broad drafting. For original
clinical research, the default first complete draft should contain:

- Title
- Abstract
- Introduction
- Materials and Methods
- Results
- Discussion
- Conclusion

Methods should expose reviewer-facing subsections:

- Study design and cohort
- Variable measurement and outcome definition
- Model building when models exist
- Validation, sensitivity, and stratified analyses when applicable
- Statistical analysis

Results should be question-led and clinically integrated, not a sequence of
`Figure 1 shows ...` paragraphs.

Discussion should normally cover:

- principal findings and significance
- interpretation, clinical meaning, and literature-supported gap
- main strengths
- main limitations and future work

### 3. Draft From Evidence

Draft only sections the current evidence can support. Prefer direct medical
claims with explicit subjects, standard statistical terminology, and bounded
interpretation.

For prediction-model or time-to-event manuscripts, ensure the first complete
draft covers target population, prediction horizon, endpoint ascertainment,
candidate predictors, missing-data handling, model family, tuning, validation,
calibration, uncertainty, and clinical utility before claiming package
readiness.

For registry, real-world, phenotype-atlas, or descriptive manuscripts, use
recorded/available diagnostic fields and denominators carefully. Do not promote
selected positive fields, missingness, or source availability as prevalence,
burden, causality, prediction, or clinical deployment unless the design and
evidence support that claim.

### 4. Citation Integrity

Never fabricate citations or infer PMID/DOI metadata from memory.

For biomedical claim support, source verification, guideline lookup, DOI/PMID
lookup, or citation repair, use the read-only OPL Connect PubMed path when
available:

```bash
opl connect pubmed search --query "<query>" --limit <n> --json
```

Record candidate results as `pubmed_source_refs` and
`pubmed_connector_invocation_ref`. Screen sources before manuscript use. MAS
still owns citation acceptance, citation ledger updates, claim-evidence support,
and publication-quality judgment.

If the connector is unavailable, record a `connector_gap` with the attempted
query and route the citation repair; do not fill citation gaps from memory.

### 5. Figures And Tables

Treat a figure or table as an argument, not decoration.

Before placing a display in the manuscript:

- bind it to claim ids and source artifacts
- confirm captions, titles, labels, units, sample sizes, and visible variables
  match the evidence
- ensure figure/table catalogs and display registry are fresh enough for the
  claim
- route figure creation or material repair through `medical-research-figure`

Do not let a main-text claim-bound figure disappear from the current package
only to make a smaller bundle compile.

### 6. Reviewer-First Revision

Before calling a draft stable, run a harsh self-review:

- claim/evidence audit
- method fidelity audit
- reporting-guideline audit
- citation integrity audit
- figure/table provenance audit
- Results narrative audit
- language redline audit
- submission-minimal audit

Record major issues in `paper/reviewer_first_pass.md`,
`paper/review/revision_log.md`, or the active review ledger. Unsupported claims
must be removed, downgraded, or routed back.

When the draft is substantial enough for an independent critique, route through
`medical-research-review` before finalize.

## Required Durable Outputs

Use the smallest set that fits the paper line, but substantial medical writing
usually needs:

- `paper/section_contracts.md`
- `paper/writing_plan.md`
- `paper/draft.md` or canonical manuscript source
- `paper/claim_evidence_map.json`
- `paper/methods_implementation_manifest.json`
- `paper/results_narrative_map.json`
- `paper/figure_semantics_manifest.json`
- `paper/derived_analysis_manifest.json` when secondary analyses support claims
- `paper/manuscript_safe_reproducibility_supplement.json`
- `paper/endpoint_provenance_note.md` when endpoint caveats exist
- `paper/figures/figure_catalog.json` when figures exist
- `paper/tables/table_catalog.json` when tables exist
- `paper/review/revision_log.md`
- `paper/review/submission_checklist.json`
- `paper/paper_bundle_manifest.json` or equivalent bundle manifest when packaged

The exact paths may vary by workspace. Preserve the meaning and make the
handoff resumable without transient chat.

## Medical Draft Red Flags

Treat these as route-back or repair triggers:

- unsupported or orphan claims
- manuscript numbers without source trace
- citation placeholders or unverified citation metadata
- missing reporting-guideline fields
- missing ethics, consent/waiver, funding, COI, or data availability on
  submission-facing surfaces
- Results that paraphrase figures instead of answering medical questions
- figure captions that mention variables not visible in the figure
- prevalence or burden wording for selected/available diagnostic fields
- adult BMI categories without age/applicability handling
- internal workflow prose in manuscript body
- undefined labels such as `knowledge-guided`, `causal`, `mechanistic`, or
  `calibration-first`
- submission-ready claims without `submission_minimal` proof

## Exit Criteria

Exit writing only when one is durably true:

- the current draft is evidence-complete enough for review/finalize and the
  required manuscript contracts are present
- a clear evidence or citation gap has been recorded and routed backward
- a packaging, proofing, or owner-surface blocker has been recorded with the
  next legal action

For any `submission-ready` claim, require fresh MAS owner evidence, not this
skill alone.
