---
name: medical-manuscript-writing
description: "Write or revise medical manuscript prose from accepted MAS evidence, including section structure, claim-source alignment and figure/table narrative."
---

# Medical Manuscript Writing

Use this skill to turn accepted medical evidence into a faithful manuscript,
reviewable draft, section repair, or writing route-back packet.

This professional specialist skill is maintained in `mas-scholar-skills` /
MAS Scholar Skills. MAS stage operating prompts may sync and consume it, while MAS
still owns stage routing, study truth, manuscript artifacts, evidence ledgers,
owner receipts, typed blockers, human gates, current packages, and publication
readiness.

Shared refs: use `docs/no-authority-boundary.md` for owner-boundary limits and
`references/professional-quality-ref-templates.md` for reusable refs-only
quality-floor handoff shapes. Keep specialty details in this skill; do not copy
long boundary or checklist text here.
When MAS supplies `manuscript_argument_pack`,
`paper_reader_grounding_pack`, or related journal-family refs, consume the
foldback matrix in
`references/professional-quality-ref-templates.md#mas-journal-family-pack-foldback`.
Keep argument, paragraph, figure/table narrative, and reader-risk judgment here
as candidate refs; MAS keeps receipt and readiness authority.
When MAS supplies `registry_signal_validity_pack` or an accepted candidate
`ehr_registry_signal_validity_ref`, consume the single rule at
`references/professional-quality-ref-templates.md#ehr-registry-signal-validity-ref`
to calibrate Methods, Results, Discussion, and limitations language. Route any
missing or internally inconsistent validity evidence to
`medical-statistical-review` (and its bounded cohort/data input routes) instead
of rebuilding the checklist or deciding validity inside writing.

Optional skill-local helper: use `kernel.py` for deterministic paper brief
schemas, section scaffolds, paragraph job maps, figure arc prompts, and
claim-strength lint hints. It is a no-authority scaffold/lint helper only; MAS
or the consuming workspace still owns evidence, artifacts, owner receipts, typed
blockers, and readiness labels.

Sibling skill routes are `medical-manuscript-review` for adversarial review,
`medical-figure-design` for material figure work, `medical-research-lit` for
PubMed-oriented literature discovery, `medical-statistical-review` for
statistical claim checks, `medical-table-design` for table-to-text binding, and
`medical-submission-prep` for submission package surfaces, and
`medical-data-governance` for clinical data manifests, source readiness support,
version impact, privacy/access tiers, and lifecycle guardrails.

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

## Manuscript-Author Stance

Write as the manuscript authors, not as an unrelated third-party auditor
commenting on what the authors do or do not know. When accepted evidence
supports the scientific content, write the ideal complete medical-journal
sentence, paragraph, and section in ordinary authorial voice.

Classify an unresolved input before changing prose:

- A `scientific_evidence_gap` can require route-back, claim downgrade, an
  explicit scientific limitation, or omission.
- An `author_supplied_objective_fact` is a fact the author, institution,
  data owner, or submission owner can supply, such as names, affiliations,
  ethics identifiers, recruitment dates, funding, disclosures, data-access
  wording, or a journal selection. Keep the ideal manuscript structure and
  insert the minimum local `[AUTHOR INPUT: ...]` annotation needed to complete
  it. Do not downgrade the scientific claim, stop ordinary authoring, or add
  defensive prose because this class of fact is pending.

Do not write statements such as `the frozen candidate does not establish`,
`status: author input required`, `this manuscript is not ready because`, or
`the information is unknown` on reader-facing manuscript, title-page,
declaration, cover-letter, table, figure, or supplement surfaces. Put workflow
status and responsibility in a derived author-input To-Do surface.

For a substantial draft, maintain one structured `author_input_registry_ref`.
Each grouped item must have a stable id, category, requested objective fact,
responsible owner, and every exact inline annotation location. Generate the
human and machine-readable To-Do lists from that registry, report the exact
main-manuscript annotation count, and fail review handoff on missing, orphaned,
or duplicate annotations. A To-Do list is a projection, not independent truth.

## AI-First Judgment Contract

Default to professional medical judgment before filling module fields. The
skill should decide, from the accepted evidence refs, whether the next honest
output is manuscript prose, a claim downgrade, a negative/equivocal finding
section, a citation repair request, a figure/table repair request, or a
route-back packet.

When evidence supports writing, emit concise refs such as
`paper_mission_framing_ref`, `claim_evidence_decision_ref`,
`claim_evidence_strength_ref`, `negative_or_equivocal_finding_ref`,
`figure_table_binding_decision_ref`, `writing_verdict_candidate`, and
`stop_or_continue_recommendation`. When it does not, emit
`route_back_candidate` with the missing source, analysis, citation, display,
table, submission, or owner-gate target. These are AI-readable candidate
judgments only. They do not write MAS truth, mutate a current package, sign an
owner receipt, create a typed blocker, or prove publication/submission
readiness.

## Method References

When the task needs a method, reporting-standard, source or quality detail beyond the current accepted context, load [method quality reference](references/method-quality-reference.md). Reuse applicable current evidence; load only resources needed by the selected task mode.

## Argument And Reader Contract

Before a substantial section or full draft, write a compact contract:

- `one_sentence_argument_ref`: in this problem/population, we show this bounded
  advance, using this approach, supported by these evidence refs.
- `paper_mission_framing_ref`: the paper mission in reviewer-facing terms:
  what this manuscript must prove, what it is not trying to prove, the intended
  reader, and the narrowest next route if the mission is not yet supportable.
- `reader_question_ref`: which reader question the section must answer first:
  relevance, novelty, trust, reuse, or clinical meaning.
- `section_outline_ref`: section-level points, required evidence refs, and
  source gaps before prose drafting.
- `terminology_ledger_ref`: canonical terms, abbreviations, endpoint names,
  dataset labels, model names, and statistical terms.
- `paragraph_job_map_ref`: one job per paragraph: context, gap, approach,
  result, comparison, implication, limitation, or route-back.
- `claim_strength_calibration_ref`: verbs matched to evidence strength, such as
  show, demonstrate, suggest, indicate, may, or could.
- `claim_evidence_strength_ref`: per-claim support class, such as direct
  primary evidence, direct guideline support, method precedent, contextual
  background, contradictory, weak, not applicable, or missing.
- `citation_style_ref`: AMA, Vancouver, or journal-specific style source plus
  any known deviations.
- `claim_citation_quality_loop_ref`: claim, evidence, citation, support
  strength, wording strength, and route-back action when a paragraph depends on
  biomedical literature or fragile evidence.
- `reporting_guideline_check_ref`: STROBE, CONSORT, PRISMA, TRIPOD, RECORD, or
  other guideline status mapped to sections.

If the core claim, evidence, or boundary is ambiguous, produce an alignment
block and route back before drafting a full section. If MAS already supplied an
equivalent stage prompt or section contract, reuse it and continue.

### First-Draft Handling-Editor Contract

Before writing sentences, produce `first_draft_story_contract_ref` with exactly
one `unique_scientific_claim_ref`, the `clinical_or_operational_value_ref`, a
`falsifiable_boundary_ref`, a job for every Results paragraph, the complete
`figure_table_narrative_arc_ref`, and `main_supplement_placement_ref`. Judge the
story as a handling editor: each Results paragraph and display must advance the
single bounded claim, and material denominator, missingness, heterogeneity, or
sensitivity evidence must be assigned to main text or supplement before prose.
Professional Skill judgment is mandatory; a journal or display template is a
reference floor only and cannot substitute for this decision.

Create `terminology_surface_ledger_ref` as an inventory of all six surfaces:
manuscript text, table titles, figure legends, CSV headers, machine-readable
endpoints, and supplement. Check every surface that exists; for a surface the
study does not produce, record `not_applicable` and why rather than fabricating
a placeholder. Machine identifiers are publication-facing semantics too.
Words such as `gap`, `intensity`, `burden`, `adherence`, `workload`, or
`quality ranking` require an explicit `term_justification_ref` linked to the
accepted claim boundary; otherwise replace
them with bounded wording such as `candidate audit signal`, `recorded-field
signal`, or `absolute flagged-record count`. A clean manuscript does not waive
terminology drift in CSV or machine-readable outputs.

If center/site dependence or center sensitivity enters the abstract or
conclusion, require `center_sensitivity_claim_binding_ref`: one explicit
claim-evidence-map row with `claim_ref`, `analysis_source_ref`, and every main
or supplementary display ref that supports it. Do not rely on prose or a table
existing somewhere in the package.

For eligible percentages, candidate percentages, resolved percentages, and
absolute flagged counts, consume `denominator_semantics_matrix_ref`. Keep the
numerator, denominator population, unit, and visual semantic distinct; an
absolute count cannot inherit a percent legend or axis meaning. Before draft
handoff, check the final embedded table/figure size and human readability;
programmatic non-overflow alone is not evidence of readable journal output.

Run a cross-domain `first_draft_pre_review_ref` before treating the initial
draft as stable. Missing story, terminology, claim-binding, denominator,
statistics, table, or display refs become `quality_debt_candidate_refs` with
the narrowest route back. This is fail-open for ordinary drafting: it may yield
`completed_with_quality_debt` as a candidate state, but it cannot create a
typed blocker, stop hosted execution, issue an authority verdict, or authorize
quality, export, publication, or submission readiness.

### Initial Draft And Freeze

For a complete initial draft or authoring freeze, load [initial-draft preflight](references/initial-draft-preflight.md). A local section revision reuses still-current accepted refs and reruns only changed dependencies; it does not require a new complete-draft cycle.

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
affiliation, ethics, consent, funding, conflict, or data-availability facts in
concise `[AUTHOR INPUT: ...]` annotations at the exact title-page, Methods, or
declaration location where the authors will complete them. Keep responsibility,
status, and formal-submission gating in the registry-derived To-Do or handoff,
not in article-body prose.

Run `lint_reader_facing_workflow_language()` across manuscript text, table
titles and notes, figure legends, and supplement text before first-draft
handoff and again before export. Authoring instructions, review-companion
language, row-trace metadata, generation/authority labels, or human-gate
bookkeeping on a reader-facing surface are repairable quality debt. Removing
them does not itself establish scientific or publication quality.

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
- Which citation metadata or source lookup still needs `medical-research-lit`
  before the claim can enter final prose?
- Which `citation_quality_action_matrix_ref` action applies: keep, downgrade,
  add source, replace source, route to Lit, route to review, human gate, or stop?

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

For a high-impact or SCI-facing draft, also record:

- novelty and audience boundary;
- reporting guideline family, such as STROBE, CONSORT, PRISMA, TRIPOD, or
  RECORD when relevant;
- data availability, code availability, ethics/consent, funding, COI, and
  author contribution annotations driven by `author_input_registry_ref`;
- figure/table narrative map showing where each display supports a text claim;
- expected supplementary material when missingness, source heterogeneity, model
  details, or sensitivity analyses need space.
- `paper_narrative_arc_ref` when the figure deck rather than a single section is
  the main weakness: hook, main-figure order, figure moves, missing panels, and
  kill list.

### 3. Draft From Evidence

Draft only sections the current evidence can support. Prefer direct medical
claims with explicit subjects, standard statistical terminology, and bounded
interpretation.

For prediction or time-to-event papers, load [prediction and external-validation writing](references/prediction-validation-writing.md). The external-validation requirements apply only to that study design.

For registry or phenotype-atlas papers, load [registry writing](references/registry-writing.md) and use `medical-registry-atlas-story-architect` when the medical story needs repair. Disease-specific examples apply only to the studied disease and available data; do not add diabetes or cardiometabolic criteria to an unrelated registry.

Write final manuscript text in full paragraphs. Use bullets only in planning
surfaces, review ledgers, checklists, or route-back packets. In Results, lead
with the medical question and evidence answer; use figure/table references as
support, not as the paragraph's only logic.

Do not leave final manuscript sections as outline bullets. If the evidence is
not ready for prose, keep the outline as a candidate planning ref and route the
missing evidence, citation, table, figure, or statistical item to the owning
skill.

### 4. Citation Integrity

Never fabricate citations or infer PMID/DOI metadata from memory.

For biomedical claim support, source verification, guideline lookup, DOI/PMID
lookup, or citation repair, route the request to `medical-research-lit`. It uses
OPL Connect PubMed/PMC discovery and strict reference verification, returning
`opl_connect_search_ref`, `opl_connect_reference_verification_ref`, and
`pubmed_source_refs` as non-authoritative evidence inputs. Crossref/OpenAlex
coverage stays in `fallback_source_refs`; do not perform source acceptance
inside writing. OPL Connect owns provider transport and receipts. MAS still
owns medical screening, citation acceptance, citation-ledger updates,
claim-evidence support, and publication-quality judgment.

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
- route figure creation or material repair through `medical-figure-design`

Do not let a main-text claim-bound figure disappear from the current package
only to make a smaller bundle compile.

When a figure deck is weak, do not compensate with more explanatory prose.
First ask whether Figure 1 carries the hook, whether the main figures follow a
coherent arc, whether panels belong in a different figure, whether concrete
missing panels must be produced, and which panels should be killed or demoted.
Only then draft the surrounding Results and Discussion narrative.

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
- terminology consistency audit
- paragraph-flow audit
- data/code availability audit when the target journal expects it
- reviewer-response readiness audit when the draft follows external comments

Record major issues in `paper/reviewer_first_pass.md`,
`paper/review/revision_log.md`, or the active review ledger. Unsupported claims
must be removed, downgraded, or routed back.

When the draft is substantial enough for an independent critique, route through
`medical-manuscript-review` before finalize.

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
- exact `medical_initial_draft_preflight_candidate_ref` and owner-gate handoff
  ref for a complete initial-draft attempt
- `immutable_candidate_snapshot_ref` for an applicable fixed-horizon or
  external-validation authoring freeze; this is not a reviewer-currentness or
  owner-acceptance receipt
- explicit `immutable_candidate_snapshot_manifest_locator`, excluded from the
  snapshot content identity
- `post_csl_reader_semantics_ref` and `figure_numbering_one_owner_ref` for final
  reader outputs
- `anomaly_evidence_parity_ref` when a reviewer response discusses an anomaly
  sensitivity

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
