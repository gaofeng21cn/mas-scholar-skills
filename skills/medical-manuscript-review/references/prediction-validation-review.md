## Prediction Model External Validation Review

For prediction-model external-validation manuscripts, run a specific review
lane before clearing draft, paper, or submission readiness. Major or blocker
findings include:

- unclear source-model origin, missing equation, missing coefficient table,
  missing predictor coding, or missing baseline survival / absolute-risk
  extraction;
- validation cohort described without source years, eligibility, diabetes or
  disease definition, endpoint ascertainment, follow-up completeness, censoring
  policy, missingness, or survey-weighting policy when relevant;
- a recorded event percentage labeled as observed fixed-horizon risk despite
  early censoring or unresolved follow-up completeness;
- discrimination reported as if it proves calibrated absolute risk;
- calibration slope, O:E, Brier score, grouped calibration, or recalibration
  claims lacking uncertainty or denominator support;
- a title that foregrounds implementation status such as "fixed" or "locked"
  when the clinically useful contribution is higher-risk identification,
  recalibration need, or external validation;
- a results narrative that repeats the same grouped-risk-gradient sentence in
  adjacent subsections instead of separating risk stratification from absolute
  calibration;
- discussion that invokes population transportability without anchoring the
  interpretation to Table 1 case-mix or event-rate differences when those
  differences are available;
- performance tables that label development-cohort external-validation-only
  calibration intercept/slope as "not estimated" instead of "not applicable";
- a cohort-level two-point calibration figure presented as if it were the
  calibration plot when grouped calibration by validation quantile is available;
- risk groups that mix development-cohort bins with validation self-quantiles
  without showing occupancy and calibration separately;
- decision-curve or threshold-utility figures shown while Methods/Results say
  clinical utility was not estimated, or while severe miscalibration makes the
  threshold basis unverified;
- cross-cohort cause, endpoint, phenotype, or attribution constructs treated as
  equivalent without an accepted codebook map and identity-preserving linkage;
- a non-estimable secondary comparison silently dropped or rewritten as evidence
  of similarity, difference, or mechanism;
- a table or figure regenerated from a stale render request with embedded old
  values instead of the current structured source and catalog generation;
- discussion that stops at "transportability failed" without explaining the
  bounded interpretation, case-mix/support possibilities, baseline-risk
  mismatch, and why clinical deployment or absolute-risk communication is not
  supported.

Route these findings to `medical-statistical-review`, `medical-table-design`,
`medical-figure-design`, `medical-manuscript-writing`, `analysis-campaign`, or
human gate as appropriate. Do not smooth them into prose-only caveats.

