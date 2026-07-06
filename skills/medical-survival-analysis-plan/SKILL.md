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
4. Build `model_plan_ref`: Kaplan-Meier, cumulative incidence, Cox, flexible
   parametric, Fine-Gray, landmarking, time-varying covariates, or sensitivity.
5. Build `diagnostic_plan_ref`: proportional hazards, informative censoring,
   competing-risk assumptions, sparse events, calibration, and robustness.
6. Produce `route_back_candidate` for undefined time zero, denominator drift,
   missing censoring logic, competing-risk mismatch, or owner analysis decisions.

## Handoff Shape

Return:

- `survival_question_ref`
- `time_origin_and_risk_set_ref`
- `endpoint_and_censoring_ref`
- `competing_risk_ref`
- `model_plan_ref`
- `diagnostic_plan_ref`
- `survival_support_map_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a survival plan into analysis acceptance, clinical conclusion,
owner receipt, typed blocker, quality verdict, or publication readiness.
