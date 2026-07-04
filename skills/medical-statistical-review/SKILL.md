---
name: medical-statistical-review
description: "Use when a MAS medical-paper task needs professional statistical review before writing, review, figure, table, or submission handoff. Covers analysis-plan fit, estimand/outcome clarity, denominator and missingness checks, assumption diagnostics, effect-size and uncertainty reporting, multiplicity/sensitivity review, statistical prose repair, and refs-only route-back. This professional specialist skill is maintained in mas-scholar-skills; MAS keeps study truth, analysis authority, owner receipts, typed blockers, artifact authority, and publication readiness."
---

# Medical Statistical Review

Use this skill when a MAS paper task needs an expert statistical pressure test
over a methods plan, result package, table, figure, or manuscript claim.

This professional specialist skill is maintained in `mas-scholar-skills` /
MAS Scholar Skills. MAS stage operating prompts may sync and consume it, while
MAS still owns stage routing, study truth, analysis artifacts, evidence ledgers,
owner receipts, typed blockers, human gates, current packages, and publication
readiness.

Shared refs: use `docs/no-authority-boundary.md` for owner-boundary limits and
`references/professional-quality-ref-templates.md` for reusable refs-only
quality-floor handoff shapes. Keep specialty details in this skill; do not copy
long boundary or checklist text here.

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
10. Check whether figures and tables show the same estimates, denominators, and
   uncertainty as the manuscript text.
11. Produce a statistical action matrix and route-back candidate.

For descriptive registry, phenotype-atlas, or treatment-gap papers, the
statistical review should prefer robustness and denominator discipline over
p-value accumulation. Route back or downgrade when a draft claims medical
discovery from group counts alone without:

- phenotype x burden x recorded medication-coverage matrix or explicit waiver;
- exact gap numerator, denominator, eligibility, index/time window, medication
  source, and class mapping;
- medication-field-present / any-recorded-medication sensitivity when drug
  capture is incomplete;
- variable missingness and plausibility atlas for phenotype-defining fields;
- site-level gap variability or a reason site variation is out of scope;
- transition-category, calendar-year, threshold, or age-stratified sensitivity
  when the text claims trajectory, service variation, or guideline priority;
- rate/count separation in figures and tables.

Do not interpret selected diagnostic-field positivity, absent recorded drug
classes, or release-level counts as prevalence, true non-treatment, guideline
nonadherence, or treatment effect without the required design and evidence.

If a statistical method, reporting claim, guideline statement, or clinical
interpretation needs biomedical literature support, use:

```bash
opl connect pubmed search --query "<query>" --limit <n> --json
```

Record returned `pubmed_source_refs` and
`pubmed_connector_invocation_ref`. The results are candidate refs only; MAS
still decides citation acceptance and manuscript use.

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
- `statistical_action_matrix_ref`
- `claim_strength_calibration_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

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
