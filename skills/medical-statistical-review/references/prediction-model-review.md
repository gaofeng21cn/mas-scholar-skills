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
For new candidates use `validate_linked_prediction_performance_v2()`.
Judge calibration and prediction-error adequacy against the study population,
outcome, prediction horizon, intended use, uncertainty, and linked evidence.
Bind this professional interpretation through `clinical_assessment`; do not
use a universal IPA cutoff or fixed calibration interval as a clinical verdict.
The unversioned function remains available only for historical candidates with
their existing numerical policy.

Check the Brier ranges and `IPA = 1 - Brier/null Brier` with the unchanged
kernel-owned numerical tolerance. Preserve finite-value, exact-ref, unit, and
not-estimable checks. A positive IPA describes improvement over the null model;
it does not establish clinical utility. Absolute-risk support requires joint
performance and calibration evidence for the declared use, and remains a
candidate judgment for the consuming domain owner.
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

## Study-Bound Interpretation API

`validate_linked_prediction_performance_v2(candidate)` uses performance policy
`scholarskills_linked_prediction_performance.v3` and limiting-evidence policy
`scholarskills_prediction_limiting_evidence.v2`. The callable suffix and policy
version are different because the historical unversioned callable already used
performance policy v2.

Preserve the existing metric panel, finite values or reasoned not-estimable
dispositions, IPA numerical tolerance, limiting-evidence rows, surface text and
no-authority declaration. Omit `calibration_reasonable_bounds`. Add:

| Field in `clinical_assessment` | Meaning |
| --- | --- |
| `study_ref`, `assessment_ref` | Exact evidence refs for the study/protocol and professional interpretation. |
| `population`, `outcome`, `prediction_horizon`, `intended_use` | Nonempty descriptions of the scope actually evaluated. |
| `calibration_status`, `prediction_error_status` | `adequate`, `limited`, or `not_estimable` for this scope. |
| `calibration_rationale`, `prediction_error_rationale` | Evidence-based reasons, including relevant uncertainty, calibration curve and any protocol-specific criteria. |
| `metric_refs` | The same `brier_ref`, `null_brier_ref`, `ipa_ref`, `calibration_slope_ref`, `calibration_intercept_ref`, `oe_ratio_ref`, and `grouped_calibration_ref` as the candidate. |
| `surface_assessments` | For each abstract/main conclusion, bind `text` to the exact current `surface_text`, declare the same `performance_boundary`, set `clinical_use_claimed=false`, and provide a professional `rationale`. |

Read the referenced interpretation and metric evidence; the reference shape
alone does not prove its content or scientific acceptance. A producer cannot
change clinical adequacy merely by writing `adequate`: the domain reviewer
judges the evidence, study context, and actual statements. The kernel checks
binding and consistency, including whether a cited limiting metric belongs to
the family assessed as limited. It does not parse English keywords to decide
scientific meaning or issue an owner verdict.

A complete candidate does not establish utility, treatment benefit, deployment
readiness, or publication approval. Keep those claims outside this performance
assessment and route them to their actual evidence and owner. Failed or missing
interpretation returns review debt; preserve available evidence and continue
the legal repair route.

For historical candidates, `validate_linked_prediction_performance()` retains
its original input, fixed numerical checks, policy IDs and results. Do not
rewrite old receipts or silently evaluate new studies through the historical
entrypoint.

## Methodological Sources

- Van Calster et al. (2019), [Calibration: the Achilles heel of predictive analytics](https://doi.org/10.1186/s12916-019-1466-7),
  PMID 31842878, PMCID PMC6912996. Calibration intercept 0 and slope 1 are
  target values; they do not by themselves guarantee a satisfactory curve.
  Interpretation depends on the population, setting, and intended decision.
- Kattan and Gerds (2018), [The index of prediction accuracy](https://doi.org/10.1186/s41512-018-0029-2),
  PMID 31093557, PMCID PMC6460739. IPA is a rescaled Brier score, depends on
  the marginal outcome probability, and does not itself measure clinical utility.

Both full-text articles were read on 2026-09-06. Neither supplies a universal
2% IPA cutoff or a universal 0.8–1.2 calibration acceptance interval. Retain
study-specific criteria when justified by the protocol and evidence.
