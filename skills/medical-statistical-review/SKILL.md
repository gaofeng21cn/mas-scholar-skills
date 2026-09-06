---
name: medical-statistical-review
description: "Review medical study analyses, model performance, uncertainty, and statistical claims for MAS or MAG using the declared protocol and current evidence."
---

# Medical Statistical Review

Use this skill when a profiled MAS paper or MAG grant task needs an expert
statistical pressure test over a methods plan, result package, table, figure,
manuscript claim, preliminary-study claim, or proposed analysis.

This professional specialist skill is maintained in `mas-scholar-skills` /
MAS Scholar Skills. MAS stage operating prompts may sync and consume it, while
MAS still owns stage routing, study truth, analysis artifacts, evidence ledgers,
owner receipts, typed blockers, human gates, current packages, and publication
readiness.

Shared refs: use `docs/no-authority-boundary.md` for owner-boundary limits and
`references/professional-quality-ref-templates.md` for reusable refs-only
quality-floor handoff shapes. Keep specialty details in this skill; do not copy
long boundary or checklist text here.

## Consumer Modes

- MAS paper mode preserves the existing immutable reviewer snapshot, manuscript,
  journal-family, display, submission, and publication workflow.
- MAG grant mode consumes only owner-supplied grant artifact refs,
  `source_pack_ref`, and any owner-provided epistemic scope. Ignore MAS-only
  reviewer snapshots, manuscript/display inventories, journal packs, and
  publication refs when absent. Review proposed design, power or precision,
  endpoints, analysis feasibility, preliminary evidence, bias, missingness,
  sensitivity, and claim calibration in grant context.

In MAG grant mode, return `grant_statistical_review_candidate_ref` through
`candidate_refs` with `route_back_candidate` and
`owner_gate_handoff_ref`. It cannot write grant truth or claim fundability, a
quality verdict, export readiness, analysis approval, a receipt, or a blocker.

For every fresh MAS paper review, consume the MAS
`review_input_snapshot_binding` and read
only the exact `opl_reviewer_input_snapshot_manifest` immutable members. Do not
reopen live analysis, data, manuscript, table, figure, workspace, or checkout
locators during judgment. Snapshot gaps produce lane-specific refs-only
route-back; they do not create a typed blocker or hosted-action liveness stop.
When MAS supplies `statistical_reporting_pack`, use
`references/professional-quality-ref-templates.md#mas-journal-family-pack-foldback`
as the compact route map. The pack points here for statistical judgment; MAS
contracts should only carry consumed pack refs, output refs, route-back, and
authority flags.
When MAS supplies `registry_signal_validity_pack`, consume the canonical
`ehr_registry_signal_validity_ref` shape in
`references/professional-quality-ref-templates.md#ehr-registry-signal-validity-ref`.
This skill is the sole producer and professional owner route for the integrated
ref; sibling skills contribute or consume bounded inputs and do not create
parallel signal-validity checklists or verdicts.

Optional local helper: `kernel.py` provides deterministic stdlib-only schema,
checklist, missingness, model-family, reporting-lint, and
`validate_ehr_registry_signal_validity_candidate` helpers. The registry helper
checks all seven coupled member refs, the single professional owner route, and
the no-authority boundary; its machine result is candidate-shape evidence, not
a signal-validity or statistical verdict. The kernel remains refs-only and
cannot issue MAS authority claims.

Sibling skill routes are `medical-table-design` for table shells and formatting,
`medical-figure-design` for figure design, `medical-manuscript-writing` for
statistical prose repair, `medical-manuscript-review` for full-paper critique,
`medical-research-lit` for PubMed-oriented literature support, and
`medical-submission-prep` for submission-facing statistical checklist items, and
`medical-data-governance` for clinical data manifests, source readiness support,
version impact, privacy/access tiers, and lifecycle guardrails.

## Core Rule

Statistical review is not a script picker. Start from the clinical question,
estimand, data-generating context, outcome definition, denominator, missingness,
and claim strength. Use tests, models, diagnostics, and reporting checklists as
evidence tools.

Do not make a weak or under-specified analysis look acceptable by adding a more
complex model. If the design cannot support the claim, produce a claim
downgrade or route-back candidate.

## AI-First Statistical Judgment

The main output is an expert statistical judgment candidate. Decide whether the
analysis supports the stated claim, only supports a narrower descriptive or
exploratory claim, exposes a negative/equivocal result, or must route back to
analysis, data governance, table, figure, writing, review, or owner decision.

Emit `statistical_verdict_candidate`, `claim_strength_calibration_ref`,
`negative_or_equivocal_result_ref`, `statistical_action_matrix_ref`, and
`route_back_candidate` as needed. These refs may guide MAS consumption, but they
cannot claim statistical conclusion authority, analysis acceptance, owner
receipt, typed blocker, quality verdict, artifact authority, or readiness.

## External Learning Quality Floor

This skill absorbs maintainable patterns from broad statistical-analysis,
scientific-critical-thinking, Nature-style data, and reviewer-response skills:

- select tests from question, variable type, independence, repeated measures,
  censoring, clustering, and distribution, not from a name in a draft;
- check assumptions before interpreting results;
- report effect sizes, uncertainty, denominators, missingness, and multiplicity;
- separate statistical significance from clinical meaning;
- bind every statistical claim to an analysis output, table, figure, or source
  ref;
- preserve the no-authority boundary: this skill proposes candidate judgments,
  while MAS or the domain owner accepts, rejects, or routes them back.
- use K-Dense statistical-power and experimental-design patterns to check
  design unit, randomization, blocking, clustering, power/MDE sensitivity, and
  pseudoreplication before interpreting model output.
- use K-Dense exploratory-data-analysis and `statsmodels` patterns as review
  discipline: require data profiling, coding distribution checks, missingness
  maps, influential-observation review, model specification trace, and
  reproducible formula/contrast refs before trusting downstream estimates.

When a statistical review needs a specialty outside the default MAS Scholar
Skills package, such as omics statistics, single-cell analysis, survival-model
tooling (`scikit-survival`), classical ML (`scikit-learn` / `shap`), Nextflow,
RDKit, PyHealth, or a named database/API workflow, first run
`opl connect external-skills search --query "<need>" --json`, inspect the
candidate with `opl connect external-skills inspect --skill <skill_id> --json`,
then sync only that one skill into the active workspace or quest if needed.
Keep the output as refs-only method support; it does not replace this skill,
the analysis plan owner, or MAS statistical acceptance authority.

Historical patterns from `ResearAI/OpenScience` at
`f120290c19a79212a1576a1046e64707e9dbb6f0` inform a refs-only `claimType` +
`graphWarnings` claim-warning floor for statistical claims. Add
`claim_type_ref` when a result sentence, table, figure,
or methods claim needs classification as descriptive, association, prediction,
causal, methods, or governance. Add `graph_warnings_ref` for unsupported,
stale, circular, missing-source, denominator-drift, or analysis-output/source
drift risks. If a reviewer annotation identifies a statistical claim gap, add
`annotation_to_source_regeneration_ref` that maps it back to analysis outputs,
data/source refs, claim-evidence refs, or the missing ref family. Keep
`skill_pack_governance_policy_ref` limited to allowed scope, dependency/
permission notes, and stage-use policy. These refs can drive
`route_back_candidate`, but cannot claim statistical conclusion, quality
verdict, owner receipt, typed blocker, or publication readiness.

Use `professional_ai_quality_floor_ref` for AI-first statistical repair loops.
Each critique should become `critique_as_repair_hint_ref` with the affected
claim, analysis output, denominator, model, table, figure, or source ref and the
smallest repair route. Trigger `triggered_meta_review_ref` for conflicting
diagnostics, repeated route-back, causal/prediction boundary crossings, or
model results that would otherwise be promoted to authority. Use
`opportunistic_knowledge_prefetch_ref` only for immediately needed analysis
plan, data dictionary, model specification, table/figure, literature, or rerun
receipt refs. Consume `project_local_ledger_pointer_ref` and
`rerun_receipt_ref` as local provenance and re-analysis evidence only when
inputs, fingerprints, commands, and limits are visible.

The [current OpenScience repository](https://github.com/ResearAI/OpenScience)
no longer distributes source under the historical open-source model. The local
implementation retains independently maintained historical patterns; do not
fetch a closed-source binary or adopt a new license as a Skill update.

Power and design review should use a clinically justified smallest effect of
interest, sensitivity analysis, and the independent experimental unit. Keep
Monte Carlo uncertainty when simulation estimates power. Do not use observed
post-hoc power to interpret a completed study, infer equivalence from overlapping
error bars, select tests solely from normality-test significance, or treat a
sample-size rule of thumb as proof of robustness.

## Review Contract

Before judging the analysis, create or refresh:

- `statistical_question_ref`: clinical question, population, exposure or
  intervention, comparator, outcome, time horizon, and intended claim.
- `estimand_or_target_parameter_ref`: what quantity is being estimated and why.
- `analysis_plan_ref`: model/test family, covariates, stratification,
  clustering, repeated-measure, censoring, multiplicity, and sensitivity plan.
- `design_unit_ref`: the unit randomized or sampled, independent replicate
  level, clustering/nesting, repeated-measure structure, and pseudoreplication
  risk.
- `randomization_blocking_ref`: randomization, blocking, stratification,
  allocation, batch/run-order, or owner-declared nonrandom design caveats.
- `power_or_mde_ref`: a priori power, minimum detectable effect, or sensitivity
  analysis when sample-size justification is needed; do not use observed power
  as evidence of adequacy.
- `denominator_and_missingness_ref`: analysis set, exclusions, missingness
  pattern, imputation or complete-case strategy, and denominator consistency.
- `effect_size_and_uncertainty_ref`: effect measure, confidence interval or
  credible interval, p-value policy, and clinically meaningful threshold.
- `assumption_diagnostic_ref`: required diagnostics and observed concerns.
- `eda_profile_ref`: sample size by analysis set, variable distributions,
  missingness pattern, outlier/influence candidates, coding-system checks, and
  implausible-value screen.
- `model_specification_ref`: formula, link/function family, contrast coding,
  reference groups, covariate handling, interaction policy, and software
  package/version when a statistical library such as `statsmodels` is used.
- `claim_strength_calibration_ref`: wording allowed by the evidence.

If these refs are missing, route back before polishing statistical language.

For registry/atlas counts and percentages, create
`denominator_semantics_matrix_ref` before prose or display review. Every metric
must name its numerator, `denominator_ref`, `denominator_role`, explicit
`formula`, unit, and visual semantic. Different percentages may legitimately
share the same real denominator; do not flag that alone. Route back only when a
declared denominator role/formula contradicts its refs, or when a percentage
and an absolute count reuse the same visual semantic or unit. Absolute flagged
records are counts within a declared scope, not a percentage or measured
workload.

When center/site dependence or center sensitivity appears in an abstract or
conclusion, require `center_sensitivity_claim_binding_ref`: the claim-evidence
map must contain the central claim row, its `analysis_source_ref`, and every
supporting main/supplement display ref. Missing binding is a refs-only
statistical route-back candidate, not a statistical verdict or execution stop.

## Prediction Models

For prediction-model development, external validation, or initial-draft performance review,
read [prediction-model-review.md](references/prediction-model-review.md). It contains
partition, analysis-set, model-complexity, decision-curve and study-bound interpretation
requirements. Other statistical reviews do not load this mode.

## EHR And Registry Studies

For recorded-field, phenotype, registry, chart-derived or claims-linked analyses,
read [ehr-registry-review.md](references/ehr-registry-review.md). Preserve the coupled
source-generation, observation-opportunity and claim-validity assessment.

## Workflow

1. Identify the paper type: descriptive registry, observational association,
   prediction, time-to-event, intervention, diagnostic, systematic review, or
   other.
2. Map each statistical claim to the exact result artifact, table, figure,
   model output, or manuscript sentence that carries it.
3. Verify denominator, inclusion/exclusion, data window, missingness, and
   endpoint ascertainment before reviewing tests or models.
4. Check whether the design can support the claim: randomization, blocking,
   stratification, cluster or repeated-measure structure, independence,
   confounding, sample size/power, and pseudoreplication risk.
5. Check whether the model/test family matches the design: independence,
   pairing, repeated measures, clustering, distribution, censoring, competing
   risks, confounding, and sample size.
6. Require effect size and uncertainty for every inferential claim. P-values
   alone are not enough.
7. Inspect the exploratory data profile before accepting the model path: missing
   data structure, implausible values, sparse levels, separation, influential
   observations, and codebook-to-analysis mismatches.
8. Check assumptions and diagnostics. Name the diagnostic that supports or
   weakens interpretation.
9. Check multiplicity, subgroup, sensitivity, and robustness claims. Downgrade
   exploratory or underpowered claims.
10. For an applicable fixed-horizon initial draft, consume the survival
    estimand plan. For a fixed-horizon or external-validation draft, produce
    `verification_scope_contract_ref`; if a data-governance anomaly inventory
    records material anomalies, also produce `anomaly_sensitivity_ref` before
    prose handoff.
11. Check whether figures and tables show the same estimates, denominators, and
    uncertainty as the manuscript text.
12. Produce a statistical action matrix and route-back candidate.

For descriptive registry, phenotype-atlas, or treatment-gap papers, the
statistical review should prefer robustness and denominator discipline over
p-value accumulation. Route back or downgrade when a draft claims medical
discovery from group counts alone without:

- phenotype x burden x recorded medication-coverage matrix or explicit waiver;
- exact gap numerator, denominator, eligibility, index/time window, medication
  source, and class mapping;
- exact high-risk low-intensity definitions for severe glycemia and other
  service-priority signals, including how many medication classes count as
  low intensity and whether organ-protective drugs, contraindication proxies,
  age/eGFR boundaries, or single-measurement abnormalities are handled;
- medication-field-present / any-recorded-medication sensitivity when drug
  capture is incomplete;
- diagnostic-variable ascertainment table when disease control, hypertension,
  dyslipidemia, complication burden, or phenotype assignment depends on
  structured diagnostic or measurement fields;
- variable missingness and plausibility atlas for phenotype-defining fields;
- site-level gap variability or a reason site variation is out of scope;
- transition trajectory categories, such as persistent high burden, glycemic
  improvement/de-escalation, cardiometabolic risk accumulation, lower-burden
  stable, or documentation-sensitive transition, when stability or repeated
  visits are interpreted clinically;
- cardiometabolic-renal protection or medication-intensity summaries when the
  Results claim risk-treatment mismatch rather than simple record gaps;
- transition-category, calendar-year, threshold, adult/known-age, or
  age-stratified sensitivity when the text claims trajectory, service
  variation, or guideline priority;
- rate/count separation for gap figures, and site-adjusted or phenotype-mix
  checks when the paper claims site/service variation;
- rate/count separation in figures and tables.

Do not interpret selected diagnostic-field positivity, absent recorded drug
classes, or release-level counts as prevalence, true non-treatment, guideline
nonadherence, or treatment effect without the required design and evidence.

If a statistical method, reporting claim, guideline statement, or clinical
interpretation needs biomedical literature support, route it to
`medical-research-lit`. Record `opl_connect_search_ref`,
`opl_connect_reference_verification_ref`, and `pubmed_source_refs` as candidate
refs only. OPL Connect owns provider transport and receipts; MAS still decides
medical support strength, citation acceptance, and manuscript use.

## Common Route-Backs

Route back when:

- the outcome, exposure, comparator, or time horizon is not defined;
- denominators differ across abstract, text, tables, and figures;
- missingness is high or differential without an explicit strategy;
- a selected diagnostic-field positive rate is written as prevalence or burden;
- a prediction model lacks validation, calibration, decision utility, or target
  population clarity;
- a time-to-event result omits censoring, risk set, proportional hazards, or
  competing-risk considerations when relevant;
- subgroup or sensitivity claims are stronger than their design allows;
- statistical prose claims causality, clinical deployment, or treatment benefit
  without supporting design.

For prediction-model external validation, also route back when:

- source-model coefficients, feature order/coding, baseline survival, unit
  conversions, or absolute-risk extraction are not reproducible;
- 5-year or fixed-horizon outcome handling does not state complete follow-up,
  censoring, Kaplan-Meier/IPCW policy, or why a binary endpoint is acceptable;
- NHANES or other complex-survey data are analyzed without an explicit
  unweighted boundary and, when needed, a survey-weighted sensitivity plan;
- calibration slope is extreme but not interpreted as possible effect-size
  compression, support mismatch, or risk-scale narrowing;
- recalibration claims are made without intercept-only and intercept+slope
  evidence or a clear decision to leave recalibration as future work;
- threshold utility or decision-curve claims are made without verified threshold
  range, net-benefit calculation, calibration basis, and clinical action
  scenario.

Before first-draft handoff, consume `fixed_horizon_risk_semantics_ref` from
`medical-survival-analysis-plan` for each fixed-horizon endpoint. Confirm that it
separates the recorded event count and count
fraction from the observed-risk estimand. If any participant is censored before
the horizon, or horizon completeness is unknown, the count fraction is
descriptive only and cannot serve as the primary observed risk without a
documented design justification. Bind the censoring-aware risk, prediction-error
or Brier, O:E, and grouped-calibration estimands to their exact source refs and
state the independent-censoring and survey-weighting boundaries.

Also require `verification_scope_contract_ref` for every applicable
fixed-horizon or external-validation initial draft and
`anomaly_sensitivity_ref` only when the analysis-input anomaly inventory is
material. Ordinary initial drafts without either analysis type do not inherit
these requirements; record not-applicable only when an owner surface asks for
a disposition.

For cross-cohort endpoints, cause categories, phenotypes, or secondary
attribution layers, create `construct_comparability_ref` with source and target
constructs, accepted codebook mapping, identity-preserving linkage, estimability,
and allowed/forbidden claims. When mapping or linkage is absent, report the
comparison as not estimable. Do not substitute a convenient proxy or infer that
the cohort constructs are similar or different.

## Handoff Shape

Return refs-only candidate output:

- `statistical_question_ref`
- `estimand_or_target_parameter_ref`
- `analysis_plan_ref`
- `design_unit_ref`
- `randomization_blocking_ref`
- `power_or_mde_ref`
- `denominator_and_missingness_ref`
- `assumption_diagnostic_ref`
- `eda_profile_ref`
- `model_specification_ref`
- `effect_size_and_uncertainty_ref`
- `multiplicity_and_sensitivity_ref`
- `table_figure_consistency_ref`
- `claim_type_ref`
- `graph_warnings_ref`
- `annotation_to_source_regeneration_ref`
- `critique_as_repair_hint_ref`
- `triggered_meta_review_ref`
- `opportunistic_knowledge_prefetch_ref`
- `project_local_ledger_pointer_ref`
- `rerun_receipt_ref`
- optional owner-provided `epistemic_review_scope_ref` locator
- `skill_pack_governance_policy_ref`
- `statistical_action_matrix_ref`
- `validation_partition_integrity_ref` for prediction-model validation
- `endpoint_analysis_set_reconciliation_ref` for endpoint/horizon accounting
- `model_complexity_sparse_event_ref` for model adequacy and diagnostics
- `linked_prediction_performance_ref` for linked discrimination, prediction
  error, calibration, and claim boundaries
- `decision_curve_validity_ref` when decision curves are reported
- consumed `fixed_horizon_risk_semantics_ref` when a fixed horizon is used
- `anomaly_sensitivity_ref` when a fixed-horizon or external-validation draft has material input anomalies
- `verification_scope_contract_ref` for an applicable fixed-horizon or external-validation initial draft
- `construct_comparability_ref` when sources or cohorts are compared
- `ehr_registry_signal_validity_ref` when EHR/registry signal validity is material
- `claim_strength_calibration_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

When `epistemic_review_scope_ref` is present in the OPL Attempt or owner
context, use it only to locate the estimand, denominator and missingness
context, analysis code and parameters, results and diagnostics, claims,
limitations, and reproduction instructions actually assessed. Record those
consumed refs in the candidate. Do not compute a scope digest, compare an
upstream hash closure, decide review currentness, or schedule a retry. Hashes
are optional locator or stale hints only; layout, package, checklist, receipt,
checkout, model, or Skill metadata changes do not invalidate statistical
review unless a declared statistical dependency actually changed.

## MAS Boundary

This skill may write or propose candidate review notes only where the active
workspace permits candidate material. It must not write MAS domain truth,
analysis authority, publication eval, controller decisions, owner receipts,
typed blockers, human gates, current package authority, runtime queues, or
provider attempts.

Do not claim statistical approval, quality verdict, artifact authority,
publication readiness, owner acceptance, or submission readiness. MAS or the
domain owner must consume the refs and issue any owner receipt, typed blocker,
route-back, artifact mutation, or publication decision.
