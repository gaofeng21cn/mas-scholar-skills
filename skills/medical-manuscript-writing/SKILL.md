---
name: medical-manuscript-writing
description: "Use when a MAS write stage operating prompt has accepted evidence and needs professional medical manuscript writing, revision, claim-evidence mapping, section contracts, citation-integrity work, reviewer-facing prose, figure/table narrative binding, submission-minimal checks, or a route-back candidate. This professional specialist skill is maintained in mas-scholar-skills; MAS keeps stage authority, runtime authority, artifact authority, owner receipts, typed blockers, and publication readiness."
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

## External Learning Quality Floor

This skill absorbs the useful parts of Nature-style writing skills and
K-Dense-style scientific writing skills as MAS-owned writing discipline:

- write the paper argument before writing sentences;
- maintain a terminology ledger before drafting;
- map every paragraph to one job;
- draft from evidence outward;
- use full manuscript prose for final text, not bullet lists;
- treat reporting guidelines, statistics, citations, figures, tables, and data
  availability as writing inputs rather than after-the-fact formatting.

Do not import foreign defaults that conflict with MAS. A MAS medical manuscript
does not need a mandatory graphical abstract, a fixed Nature voice, or extra
figures by default. It needs a defendable medical argument with claim-evidence
traceability.

K-Dense `scientific-writing` contributes only the durable writing discipline:
two-stage outline-to-prose drafting, IMRAD/reporting guideline awareness,
citation-style control, and final full-paragraph manuscript prose. Its mandatory
graphical abstract and high figure-count defaults are rejected unless the target
journal, study charter, or MAS figure contract requires them.

For citation-heavy prose or draft repair, read
`references/professional-quality-ref-templates.md` and use
`claim_citation_quality_loop_ref`. The loop lets AI judge whether a claim should
be kept, downgraded, cited, rewritten, or routed back without turning the draft
into paper truth, owner receipt, typed blocker, or publication readiness.

## Argument And Reader Contract

Before a substantial section or full draft, write a compact contract:

- `one_sentence_argument_ref`: in this problem/population, we show this bounded
  advance, using this approach, supported by these evidence refs.
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
  author contribution placeholders;
- figure/table narrative map showing where each display supports a text claim;
- expected supplementary material when missingness, source heterogeneity, model
  details, or sensitivity analyses need space.

### 3. Draft From Evidence

Draft only sections the current evidence can support. Prefer direct medical
claims with explicit subjects, standard statistical terminology, and bounded
interpretation.

For prediction-model or time-to-event manuscripts, ensure the first complete
draft covers target population, prediction horizon, endpoint ascertainment,
candidate predictors, missing-data handling, model family, tuning, validation,
calibration, uncertainty, and clinical utility before claiming package
readiness.

For prediction-model external-validation manuscripts, the first complete draft
must read as an external-validation paper rather than a brief metric note. It
should include:

- source-model provenance, full equation or coefficient table, predictor coding,
  unit conversions, and baseline survival or absolute-risk extraction;
- when the source model survives mainly as an archived fixed equation, state
  that boundary in a neutral Methods sentence, foreground the preserved
  coefficients plus baseline survival needed for transport, and move missing
  development-package details such as exact penalty form or incomplete
  development provenance into Limitations rather than centering them in the main
  story;
- validation-cohort source years, eligibility, endpoint ascertainment, follow-up
  completeness or censoring policy, missing-data strategy, and weighting policy;
- visible Table 1 cohort comparison, Table 2 validation metrics, and a grouped
  calibration table when grouped calibration drives the claim;
- discrimination and calibration reported separately, with uncertainty for
  C-statistic, observed/expected ratio, Brier or prediction error, calibration
  intercept/slope, and grouped observed risk where available;
- plain-language interpretation of risk-scale compression when predicted risk
  occupies a narrow range but observed risk separates across groups;
- recalibration or model-updating policy stated as future/required work unless
  verified recalibration evidence is already accepted;
- decision-curve or threshold-utility displays omitted unless threshold range,
  net-benefit calculation, and calibration basis are verified.

For near-submission external-validation revisions, prefer a discrete
`Limitations` paragraph when the draft already has stable Methods, Results, and
main displays. Keep the final Conclusion clinically operational: whether the
score can be used for absolute-risk communication, thresholds, or deployment in
the target population.

If any of these items are missing, route the gap to statistical review, table
design, figure design, analysis-campaign, or a MAS owner gate before writing a
submission-shaped conclusion.

For registry, real-world, phenotype-atlas, or descriptive manuscripts, use
recorded/available diagnostic fields and denominators carefully. Do not promote
selected positive fields, missingness, or source availability as prevalence,
burden, causality, prediction, or clinical deployment unless the design and
evidence support that claim.

For descriptive registry figure titles, legends, captions, table titles, and
table notes, treat `burden` as a red flag when the numerator comes from selected
or populated diagnostic fields, variable availability, or subcohort-only
screening instruments. Prefer wording such as `recorded diagnostic fields`,
`positive status among populated records`, `available-record denominators`,
`instrument availability`, `symptom status`, or `screening-instrument
co-occurrence`. Use manuscript-ready declarative boundaries such as
`percentages exclude unknown values and are not prevalence estimates` rather
than instruction-style wording such as `should not be interpreted as`.

Before packaging a descriptive registry manuscript, run a final medical-SCI
language polish pass. Remove internal report phrasing from the article body,
including authoring-status statements, submission TODO prose, repeated
defensive caveats, revision-response phrases such as `reviewer-triggered`, and
nonstandard terms such as `analytic surface` or `data surface`. Write Methods
as completed study methods when evidence exists, move
unconfirmed ethics, funding, COI, author, data-availability, enrollment-period,
and data-lock facts to submission checklists or human-gate TODO surfaces, and
keep Results finding-led rather than explanation-led. For non-model registry
papers, use headings such as `Analytical scope` and `Data checks and sensitivity
analysis` instead of `Model building` and `Validation framework`. Compress
figure legends to the visible variables, denominator, and interpretation
boundary only; do not let figure semantics fields such as `direct_message`,
panel messages, or glossary notes spill into submission legends as internal
instructions.

For phenotype-atlas or treatment-gap descriptive drafts, do not let the first
draft become "we split patients into groups and reported rates." Before prose,
define the medical pattern the atlas is meant to reveal. Route back if the
paper lacks:

- a one-sentence discovery contract, such as phenotype-specific recorded
  burden-medication discordance, structured risk-treatment mismatch, or
  service-review priority patterns;
- a rationale for the rule hierarchy and its ordering;
- a primary finding framed as a medical mismatch pattern, such as severe
  glycemic burden with low recorded glucose-lowering intensity, cardiometabolic
  risk context with low recorded preventive medication coverage, or dynamic
  transition between glycemic, adiposity-linked, and cardiometabolic profiles;
- exact gap definitions with numerator, denominator, eligibility, medication
  source, class mapping, and interpretation label;
- exact low-intensity definitions for high-risk subgroups, including which
  diabetes medication classes count, whether insulin, GLP-1RA, SGLT2i,
  metformin, ACEI/ARB, statins, age, eGFR, contraindications, and single-lab
  abnormalities were considered or explicitly unavailable;
- medication-field-present or any-recorded-medication sensitivity when
  medication capture is incomplete;
- diagnostic ascertainment table when diagnostic state, uncontrolled disease,
  hypertension, dyslipidemia, or complication burden is derived from structured
  records;
- a missingness/plausibility table for phenotype-defining variables;
- site-level gap variability, transition trajectory categories, calendar-year,
  threshold, adult/known-age, medication-source, renal-risk/cardiometabolic
  protection, or age-stratified sensitivity when the manuscript asks for more
  than a local descriptive atlas;
- a clear decision on whether service-priority tiers, cardiometabolic-renal
  protection gaps, medication-intensity patterns, or potential overtreatment
  signals are in scope, waived, or routed to follow-up analysis;
- figure/table contracts that show the medical pattern rather than only group
  counts.

Use terms such as recorded medication-coverage gap, treatment-review signal,
burden-medication discordance, and risk-treatment mismatch. Use
`guideline-linked` only for tiered review signals with explicit guideline
source, eligibility, age/eGFR boundary, contraindication, and medication-source
refs. Avoid guideline nonadherence, true untreated status, treatment failure, or
individualized treatment allocation unless MAS has accepted evidence and
guideline-specific eligibility refs.

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
- route figure creation or material repair through `medical-figure-design`

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
