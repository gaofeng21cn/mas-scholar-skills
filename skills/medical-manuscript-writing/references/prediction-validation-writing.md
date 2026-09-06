# Prediction And External-Validation Writing

Table 1, Table 2 and figure ordering below are template examples. Preserve
cohort-comparison, performance and calibration information jobs using the
current manuscript's numbering and journal format.

For prediction-model or time-to-event manuscripts, ensure the first complete
draft covers target population, prediction horizon, endpoint ascertainment,
candidate predictors, missing-data handling, model family, tuning, validation,
calibration, uncertainty, and clinical utility before claiming package
readiness.

For prediction-model external-validation manuscripts, the first complete draft
must read as an external-validation paper rather than a brief metric note. It
should include:

- an `external_validation_first_draft_contract_ref` that consumes source-model
  provenance, target-population/follow-up, fixed-horizon risk semantics,
  anomaly sensitivity, verification scope, construct comparability,
  claim-family scope qualifiers, calibration/performance, structured
  display-source, renderer provenance, claim-guardrail,
  and negative-or-non-estimable-result refs before prose;
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
- event counts and recorded event fractions labeled as descriptive quantities,
  distinct from Kaplan-Meier, cumulative-incidence, or other censoring-aware
  observed-risk estimates; never call the event fraction a fixed-horizon risk
  when early censoring exists or follow-up completeness is unresolved;
- visible Table 1 cohort comparison, Table 2 validation metrics, and a grouped
  calibration table when grouped calibration drives the claim;
- discrimination and calibration reported separately, with uncertainty for
  C-statistic, observed/expected ratio, Brier or prediction error, calibration
  intercept/slope, and grouped observed risk where available;
- when the transported model retains useful ranking but has poor absolute
  calibration, frame the manuscript around the usable property first
  (higher-risk identification or risk stratification) and then state the
  recalibration boundary for absolute-risk communication or threshold decisions;
- write the title for the medical contribution rather than the implementation
  status: avoid foregrounding words such as `fixed` or `locked` in the title
  unless the target journal or study design makes them clinically essential;
  keep model-locking details in Methods;
- use each quantitative anchor once in Results: put risk-gradient evidence under
  discrimination/risk stratification, put O:E, predicted-risk compression,
  calibration slope/intercept, and Brier under absolute calibration, and avoid
  repeating the same fold-change sentence across adjacent subsections;
- ground cross-population interpretation in Table 1 differences, such as age,
  smoking, observed event rate, HbA1c, comorbidity, treatment context, or other
  accepted descriptive evidence, rather than relying on generic country
  language;
- plain-language interpretation of risk-scale compression when predicted risk
  occupies a narrow range but observed risk separates across groups;
- mark development-cohort calibration intercept/slope as `Not applicable` when
  the row is an external-validation calibration metric rather than a skipped
  estimate for the development cohort;
- keep figure hierarchy explicit: grouped calibration is the primary calibration
  evidence when available; cohort-level two-point calibration displays can stay
  as overview figures only when the text names that limited role;
- recalibration or model-updating policy stated as future/required work unless
  verified recalibration evidence is already accepted;
- decision-curve or threshold-utility displays omitted unless threshold range,
  net-benefit calculation, and calibration basis are verified;
- a `construct_comparability_ref` for every cross-cohort endpoint or secondary
  explanatory construct. Missing accepted codebook mapping or identity-preserving
  linkage makes that comparison not estimable; state the negative result and do
  not imply similarity, difference, or mechanism;
- one `structured_display_source_map_ref` binding every paper-facing table,
  figure, caption, and catalog entry to the current structured numeric source.
  After a numeric or semantic change, regenerate affected displays; do not reuse
  a render request whose payload embeds superseded values.
- one `renderer_provenance_ref` produced by writing as a refs-only aggregation
  of the display producer's structured source fingerprint, exact request/config
  bytes, renderer identity/version, clean-rebuild evidence, and final output
  fingerprints. Writing records this binding for review handoff; it does not
  execute or accept the render, and renderer success or a matching image alone
  does not establish currentness.
- one `claim_family_scope_qualifier_ref` that keeps ranking/discrimination,
  absolute calibration, risk-scale compression, recalibration, clinical
  utility, and causal transport explanations separate. Draft only the wording
  allowed for each evidence-bound family.
- `verification_scope_contract_ref` for every external validation, including
  the exact analyses/displays assessed; add `anomaly_sensitivity_ref` only when
  a material input anomaly is inventoried. State anomaly handling and
  robustness without hiding implausible values.

For near-submission external-validation revisions, prefer a discrete
`Limitations` paragraph when the draft already has stable Methods, Results, and
main displays. Keep the final Conclusion clinically operational: whether the
score can be used for absolute-risk communication, thresholds, or deployment in
the target population.

If any of these items are missing, route the gap to statistical review, table
design, figure design, analysis-campaign, or a MAS owner gate before writing a
submission-shaped conclusion.
