---
name: medical-causal-inference-plan
description: "Use when a MAS medical-paper task needs refs-only causal inference planning: target trial emulation, DAG/confounder map, estimand, exposure/outcome timing, bias checks, sensitivity plans, support maps, route-back, and owner-gate handoff. This optional specialist does not claim causality, write MAS truth, sign owner receipts, create typed blockers, or claim readiness."
---

# Medical Causal Inference Plan

Use this optional MAS Scholar Skills specialist when an observational medical
paper needs causal-design pressure testing or a causal analysis plan candidate.

This skill is refs-only and no-authority. It can prepare causal plan refs,
support maps, `route_back_candidate`, and `owner_gate_handoff_ref`; it cannot
claim causality, approve analysis, write MAS truth, sign owner receipts, create
typed blockers, or claim publication readiness.

Optional helper: use `kernel.py` for deterministic DAG edge parsing, estimand
checklists, causal bias flags, and causal-plan handoff skeletons. It is
stdlib-only and no-authority.

## Workflow

1. Define `causal_question_ref`: target population, intervention/exposure,
   comparator, outcome, time zero, follow-up, and intended causal contrast.
2. Build `target_trial_candidate_ref`: eligibility, assignment strategy,
   treatment strategies, outcome, follow-up, causal contrast, and analysis plan.
3. Build `dag_or_confounder_map_ref`: baseline confounders, mediators,
   colliders, time-varying confounding, and unavailable-variable caveats.
4. Build `bias_and_identifiability_ref`: selection, immortal time, reverse
   causation, measurement, informative censoring, positivity, and exchangeability.
5. Build `sensitivity_plan_ref`: negative controls, falsification, E-value,
   unmeasured confounding, competing risks, missingness, or design alternatives.
6. Produce `route_back_candidate` when the design cannot support a causal claim
   or needs owner analysis/data decisions.

## Handoff Shape

Return:

- `causal_question_ref`
- `target_trial_candidate_ref`
- `estimand_ref`
- `dag_or_confounder_map_ref`
- `bias_and_identifiability_ref`
- `sensitivity_plan_ref`
- `claim_strength_calibration_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a causal plan into a causal conclusion, analysis authority, owner
receipt, typed blocker, quality verdict, or publication readiness.
