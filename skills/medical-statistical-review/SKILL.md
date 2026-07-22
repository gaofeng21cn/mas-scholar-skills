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
For every fresh review, consume the MAS `review_input_snapshot_binding` and read
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

OpenScience main `f120290` contributes a refs-only `claimType` +
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

## Initial-Draft Prediction-Model Integrity

Before a prediction-model initial draft is treated as complete, build and
pressure-test four separate refs: `validation_partition_integrity_ref`,
`endpoint_analysis_set_reconciliation_ref`,
`model_complexity_sparse_event_ref`, and `linked_prediction_performance_ref`;
also build `decision_curve_validity_ref` when decision curves are reported.

For partition integrity, bind development, tuning, and validation partitions,
their disjointness, source-population relation, and every penalty/tuning/model
selection decision. An empty decision list is not evidence; record an explicit
prespecified `no_tuning_prespecified` row when no tuning occurred. Validation
outcomes cannot select hyperparameters, penalties, transforms, or model form.
A center-disjoint split from one cohort is internal or internal-external
validation, not external validation.

For endpoint reconciliation, use one row per endpoint and follow-up basis with
its exact analysis-set ref, N, events, estimand, and source metric. Distinct
endpoints or horizons may legitimately have different N/events; this is not a
conflict when their estimands and sources are independently bound. Never reuse
one estimand or source ref to hide incompatible event counts. Require events,
competing events, and early censoring to conserve the analysis N. Fixed-horizon
risk and prediction-error evidence uses exact refs; full-follow-up rows use an
explicit `not_applicable_with_reason` disposition rather than a placeholder ref.
Run `validate_endpoint_analysis_set_reconciliation_v2()` for new candidates.
The unversioned validator preserves the earlier eight-field v1 row contract for
same-major callers.

For model complexity, report candidate and effective degrees of freedom,
continuous-predictor count, formal sample-size/overfitting method and inputs,
expected and observed shrinkage or optimism, separation, penalty source,
calibration, and full parameters. Events per parameter is descriptive context,
not a mechanical 5- or 10-events-per-variable pass rule. Declare proportional-
hazards applicability explicitly as `required` or
`not_applicable_with_reason`; do not infer it from a model-name string.
Nonlinearity evidence is required when any continuous predictor is modeled and
may be explicitly inapplicable only when none exists.

For decision curves, bind the horizon, censoring count and method, analysis-set
policy, uncertainty method and interval, calibration basis and status,
threshold range, net-benefit source, and at least one real clinical action
scenario. Complete-case binary point estimates, unverified calibration, or a
plot alone do not support clinical-utility language.

For linked prediction performance, assess discrimination, Brier and null Brier,
IPA, calibration slope/intercept, O:E, and grouped calibration together. Check
that discrimination declares `harrell_c_index`, `uno_c_index`, or
`time_dependent_auc` and lies within `[0, 1]`. For a `ranking_only` boundary,
bind every limiting-evidence row to the exact current Brier, IPA, or calibration
metric ref and require its surface phrase to carry that metric's current value.
IPA may use either its raw proportion or the corresponding `value * 100`
percentage. A percent suffix cannot be attached to the raw IPA value, Brier,
calibration slope/intercept, or O:E value. The metric label must be followed by
a complete signed decimal or scientific numeric token whose parsed value and
unit match the current metric; substring, wrong-sign, and wrong-exponent
matches are invalid.
The versioned kernel limiting-evidence policy treats prediction-error evidence
as limited only when the validated IPA is at most 0.02; reasonable calibration,
larger IPA, or a favorable Brier/null-Brier pair cannot be relabeled as a
limitation. Callers cannot override this threshold or the kernel calibration
bounds.
Then check the Brier ranges and the identity `IPA = 1 - Brier/null Brier` against the
versioned, kernel-owned tolerance. Require finite intercept and O:E values or
typed dispositions, and judge calibration against versioned, kernel-owned
bounds. Candidate producers cannot override either policy. Absolute-risk
support is a joint performance and calibration decision and cannot be inferred
from calibration slope alone. Each metric uses an exact ref or explicit
`not_estimable_with_reason` disposition.
When the boundary is `ranking_only`, carry adverse calibration or limited
prediction-error evidence into both abstract and main conclusions and forbid
absolute-risk, threshold-use, or deployment claims.

For every applicable fixed-horizon initial draft, consume
`fixed_horizon_risk_semantics_ref` from `medical-survival-analysis-plan`. For
every fixed-horizon or external-validation initial draft, produce
`verification_scope_contract_ref`. Produce `anomaly_sensitivity_ref` when
`analysis_input_anomaly_inventory_ref` from `medical-data-governance` records an
implausible, extreme, sentinel-like, unit-inconsistent, or codebook-conflicting
value. Bind the primary
handling, at least one justified sensitivity or an explicit reason none is
estimable, affected N/events, each key estimand under both analyses, tolerance
or interpretation rule, and claim impact. Do not use post hoc deletion or
winsorization to make a result look stable.

The verification scope must enumerate the exact analysis inputs, estimands,
methods, anomaly rules, sensitivity variants, tables, figures, and claims that
were actually checked, plus excluded or unverified items and the command/output
or rerun refs used. A successful script, build, or spot check verifies only its
declared scope. This refs-only contract does not establish artifact currentness,
review currentness, analysis acceptance, or readiness; it is consumed by
`medical-evidence-integrity-reviewer` and `medical-manuscript-writing` and
remains subject to MAS/domain-owner acceptance.

## EHR And Registry Signal Validity Rule

For EHR, registry, chart-derived, claims-linked, or other real-world-data work,
do not treat a recorded field as a direct measurement of the target clinical
state. The analyzable signal is jointly shaped by the underlying state, the
opportunity to observe it, the care/documentation/coding process, and the
extraction or transformation path. Review those mechanisms together before
interpreting a count, rate, phenotype, outcome, association, or model result.

Produce one `ehr_registry_signal_validity_ref` under
`registry_signal_validity_pack`:

- `paper_identity_ref` must lock the paper type, target population, unit, source
  and time window, intended inference, and scientific identity. A descriptive
  registry atlas, phenotype validation study, association study, and prediction
  study cannot share an unstated validity target.
- `chart_review_validation_ref` must state what chart review validates, in which
  sampling frame and review unit, against what reference standard, and with what
  abstraction, adjudication, blinding, and agreement evidence. Positive
  predictive value in a selected sample does not establish sensitivity,
  representativeness, source completeness, or validity for every downstream
  phenotype and outcome.
- `phenotype_outcome_coupling_ref` must show that phenotype assignment and the
  outcome or target signal refer to compatible people, episodes, time windows,
  eligibility rules, denominators, and source coverage. Valid-looking components
  cannot be combined into an unvalidated joint endpoint.
- `availability_mechanism_ref` must distinguish true absence from not
  applicable, structurally unavailable, not ordered, not measured, not
  documented, not extracted, and site/time-specific capture. The statistical
  handling and denominator must follow the actual mechanism rather than treating
  every blank as one missing-data state.
- `observation_opportunity_bias_ref` must examine whether encounter frequency,
  follow-up, testing, referral, access, survival, site workflow, or care pathway
  changes who can acquire a recorded signal. Adjust, stratify, sensitize,
  restrict, or bound the claim when observation opportunity differs materially.
- `source_generation_quality_ref` must bind the signal to clinical workflow,
  measurement/coding/documentation rules, ingestion, deduplication,
  transformation, release/version, lineage, and source-QA evidence. Clean model
  output cannot repair an unidentified or unstable source-generation process.
- `claim_boundary_ref` must state the strongest supported descriptive,
  association, prediction, or causal wording and name forbidden inferences.
  Recorded-field positivity or availability is not automatically prevalence or
  incidence; missing recorded treatment is not automatically non-treatment or a
  treatment gap; site support is not automatically site performance or external
  validity.

Judge the seven member refs as one coupled validity argument. A chart-review
strength in one component cannot waive an availability, observation-opportunity,
source-generation, coupling, or claim-boundary failure elsewhere. When evidence
is incomplete, return a bounded claim downgrade, sensitivity requirement, or
`route_back_candidate` rather than a binary validity label.

Route phenotype-definition and ascertainment inputs to
`medical-cohort-phenotyping`, method decomposition to
`medical-methodology-planner`, source lineage and generation evidence to
`medical-data-governance`, prose calibration to `medical-manuscript-writing`,
and independent pressure testing to `medical-manuscript-review`. The integrated
ref returns here before MAS or the domain owner records acceptance.
`medical-registry-atlas-story-architect` may contribute optional narrative
framing only; it does not produce or own the integrated validity ref. The ref
remains refs-only/no-authority and cannot establish cohort truth, dataset validity,
analysis acceptance, an owner receipt, a typed blocker, a quality verdict, or
publication readiness.

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
