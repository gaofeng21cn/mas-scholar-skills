---
name: medical-survival-analysis-plan
description: "Use when a MAS medical-paper task needs refs-only survival or time-to-event analysis planning: time origin, risk set, censoring, competing risks, endpoint definitions, model/diagnostic plans, support maps, route-back, and owner-gate handoff. This optional specialist does not approve analysis, write MAS truth, sign owner receipts, create typed blockers, or claim readiness."
---

# Medical Survival Analysis Plan

Use this optional MAS Scholar Skills specialist when a medical paper needs a
time-to-event, survival, cumulative-incidence, or competing-risk plan candidate.

This skill is refs-only and no-authority. It can prepare survival plan refs,
support maps, `route_back_candidate`, and `owner_gate_handoff_ref`; it cannot
approve analysis, write MAS truth, sign owner receipts, create typed blockers,
or claim source, runtime, publication, or production readiness.

Optional helper: use `kernel.py` for deterministic time-zero/event/censoring
schemas, follow-up/person-time scaffolds, KM/Cox model-plan shells, and
reporting lint. It is stdlib-only and no-authority.

## Workflow

1. Define `survival_question_ref`: population, exposure/group, endpoint,
   time origin, follow-up horizon, censoring event, and intended claim.
2. Build `time_origin_and_risk_set_ref`: index date, delayed entry, eligibility,
   baseline covariates, and risk-set construction.
3. Build `endpoint_and_censoring_ref`: event ascertainment, competing events,
   censoring rules, loss to follow-up, and administrative censoring.
4. Produce `fixed_horizon_risk_semantics_ref` before a fixed-horizon result is
   interpreted. Bind the horizon and analysis set; recorded event count and
   count fraction; number censored before the horizon; Kaplan-Meier risk for an
   all-cause endpoint or cumulative incidence when a competing event precludes
   the endpoint; IPCW Brier or another named censoring-aware prediction-error
   estimator; O:E convention; censoring model, positivity/weight handling, and
   independent-censoring assumption. A recorded event fraction is descriptive,
   not a Kaplan-Meier or cumulative-incidence risk estimate, whenever early
   censoring exists or horizon completeness is unknown. Route the ref to
   `medical-statistical-review` and `medical-manuscript-writing` for consumption;
   neither consumer may silently replace its estimand.
5. Build `model_plan_ref`: Kaplan-Meier, cumulative incidence, Cox, flexible
   parametric, Fine-Gray, landmarking, time-varying covariates, or sensitivity.
6. Build `diagnostic_plan_ref`: proportional hazards, informative censoring,
   competing-risk assumptions, sparse events, calibration, and robustness.
   Declare proportional-hazards applicability explicitly; require PH evidence
   for Cox, Fine-Gray, and other proportional-hazards families, and use a
   reasoned not-applicable disposition only for a genuinely non-PH model.
   Require nonlinearity evidence when continuous predictors are present.
7. When competing events can preclude the endpoint, build
   `competing_risk_ref` with the competing event, estimand, cause-specific or
   subdistribution boundary, and cumulative-incidence interpretation. Do not
   silently treat a competing event as non-informative censoring.
8. When decision curves are reported, consume or produce
   `decision_curve_validity_ref` with fixed-horizon censoring handling,
   uncertainty, calibration basis, threshold range, net-benefit source, and a
   concrete clinical action scenario. A curve alone is not clinical utility.
9. Produce `route_back_candidate` for undefined time zero, denominator drift,
   missing censoring logic, competing-risk mismatch, or owner analysis decisions.

## Handoff Shape

Return:

- `survival_question_ref`
- `time_origin_and_risk_set_ref`
- `endpoint_and_censoring_ref`
- `fixed_horizon_risk_semantics_ref`
- `competing_risk_ref`
- `model_plan_ref`
- `diagnostic_plan_ref`
- `survival_estimand_plan_ref`
- `decision_curve_validity_ref` when decision curves are reported
- `survival_support_map_ref`
- `candidate_refs`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a survival plan into analysis acceptance, clinical conclusion,
owner receipt, typed blocker, quality verdict, or publication readiness.
