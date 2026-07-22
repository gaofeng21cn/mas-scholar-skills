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

Optional skill-local helper: use `kernel.py` for deterministic transportability
review skeletons, predictor mapping normalization, and forbidden-authority lint.

## Workflow

1. Build `source_model_ref`: model source, endpoint, time horizon, predictors,
   development population, intended use, and unavailable implementation details.
2. Build `target_population_ref`: target cohort, inclusion/exclusion, outcome
   ascertainment, follow-up completeness, censoring before the prediction
   horizon, missingness, weighting boundary, and case-mix differences.
3. Check `predictor_mapping_ref`: predictor availability, coding, units,
   timing windows, imputation, transformations, and proxy variables.
4. For a fixed-horizon time-to-event validation, consume
   `fixed_horizon_risk_semantics_ref` from `medical-survival-analysis-plan`.
   Keep the recorded fraction, censoring-aware observed risk, O:E,
   Brier/prediction error, grouped calibration, and their assumptions bound to
   separate exact source refs. Use an explicit not-applicable reason only when
   the endpoint is not fixed-horizon time-to-event.
5. Produce `construct_comparability_ref`: compare endpoint and secondary-
   construct definitions, codebooks, units, time windows, ascertainment, and
   identity-preserving linkage. Missing accepted mapping or linkage is a stop
   condition: mark the comparison not estimable, list prohibited
   interpretations, and do not substitute a non-isomorphic proxy. Track
   codebook presence, identity-preserving linkage, field-role semantics,
   accepted mapping, and current evidence as five separate structured layers.
   Run `validate_construct_comparability_currentness()` whenever evidence is
   recovered or refreshed. Old absence reasons must become `invalidated` with
   the exact superseding evidence ref; they cannot remain active. Recovery does
   not authorize estimation: if only field-role acceptance remains open, keep
   the verdict not estimable with exactly that current stop layer.
6. Produce `claim_family_scope_qualifier_ref` with separate rows for ranking or
   discrimination, absolute calibration, risk-scale compression, recalibration,
   clinical utility, and causal or mechanistic transport explanation. Each row
   binds its population, endpoint, horizon, analysis set, weighting boundary,
   evidence refs, allowed wording, and forbidden wording. Evidence for one
   family cannot satisfy another; discrimination does not establish calibrated
   absolute risk, deployment utility, or the cause of transport failure.
7. Review `transportability_assessment_ref`: population shift, endpoint shift,
   setting shift, measurement drift, recalibration need, and applicability.
8. Review `calibration_and_performance_ref`: discrimination, calibration,
   grouped risk, risk-scale compression, uncertainty, and sensitivity analyses.
9. Review `clinical_utility_boundary_ref`: threshold rationale, DCA/support,
   intended action, and whether the paper overclaims decision usefulness.
10. Produce `route_back_candidate` for model provenance, mapping, calibration,
   reporting, or owner analysis decisions.

## Handoff Shape

Return:

- `source_model_ref`
- `target_population_ref`
- `predictor_mapping_ref`
- `fixed_horizon_risk_semantics_ref`
- `construct_comparability_ref`
- `construct_comparability_currentness_ref` with active and invalidated
  member-level stop-reason history
- `claim_family_scope_qualifier_ref`
- `transportability_assessment_ref`
- `calibration_and_performance_ref`
- `clinical_utility_boundary_ref`
- `reporting_alignment_ref`
- `candidate_refs`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a transportability review candidate into model acceptance, analysis
authority, MAS truth, owner receipt, typed blocker, reviewer receipt, or
publication readiness.
