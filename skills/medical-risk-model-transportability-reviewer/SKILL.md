---
name: medical-risk-model-transportability-reviewer
description: "Use when a MAS medical-paper task needs refs-only risk model transportability review: source model provenance, target cohort fit, predictor mapping, calibration/discrimination, clinical utility, TRIPOD-style reporting, route-back, and owner-gate handoff. This optional specialist does not accept models, write MAS truth, sign owner receipts, create typed blockers, or claim readiness."
---

# Medical Risk Model Transportability Reviewer

Use this optional MAS Scholar Skills specialist when a prediction model,
external validation, recalibration, or clinical utility section needs
transportability review before MAS/domain owner use.

This skill is refs-only and no-authority. It can prepare transportability
review refs, support maps, `route_back_candidate`, and
`owner_gate_handoff_ref`; it cannot accept a model, write MAS truth, sign an
owner receipt, create a typed blocker, or claim publication readiness.

## Workflow

1. Build `source_model_ref`: model source, endpoint, time horizon, predictors,
   development population, intended use, and unavailable implementation details.
2. Build `target_population_ref`: target cohort, inclusion/exclusion, outcome
   ascertainment, follow-up, censoring, missingness, and case-mix differences.
3. Check `predictor_mapping_ref`: predictor availability, coding, units,
   timing windows, imputation, transformations, and proxy variables.
4. Review `transportability_assessment_ref`: population shift, endpoint shift,
   setting shift, measurement drift, recalibration need, and applicability.
5. Review `calibration_and_performance_ref`: discrimination, calibration,
   grouped risk, risk-scale compression, uncertainty, and sensitivity analyses.
6. Review `clinical_utility_boundary_ref`: threshold rationale, DCA/support,
   intended action, and whether the paper overclaims decision usefulness.
7. Produce `route_back_candidate` for model provenance, mapping, calibration,
   reporting, or owner analysis decisions.

## Handoff Shape

Return:

- `source_model_ref`
- `target_population_ref`
- `predictor_mapping_ref`
- `transportability_assessment_ref`
- `calibration_and_performance_ref`
- `clinical_utility_boundary_ref`
- `reporting_alignment_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a transportability review candidate into model acceptance, analysis
authority, MAS truth, owner receipt, typed blocker, reviewer receipt, or
publication readiness.
