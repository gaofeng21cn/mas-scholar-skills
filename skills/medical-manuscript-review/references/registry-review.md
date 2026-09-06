## SCI Clinical Registry Review

Apply clinical examples only to matching disease, medication and endpoint
scope. Cardiometabolic drug classes and renal criteria do not apply to an
unrelated registry. Preserve the general evidence, denominator, ascertainment
and bounded-claim checks using that study's accepted clinical definitions.

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
