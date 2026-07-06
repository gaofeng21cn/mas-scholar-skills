---
name: medical-cohort-phenotyping
description: "Use when a MAS medical-paper task needs refs-only cohort phenotype planning: inclusion/exclusion logic, index dates, diagnostic/code/measurement definitions, medication exposure windows, missingness, phenotype validation checks, support maps, route-back, and owner-gate handoff. This optional specialist does not write MAS truth, sign owner receipts, create typed blockers, or claim readiness."
---

# Medical Cohort Phenotyping

Use this optional MAS Scholar Skills specialist when a cohort, registry, EHR,
claims, or real-world-data paper needs phenotype definition candidates.

This skill is refs-only and no-authority. It can prepare phenotype candidate
refs, support maps, `route_back_candidate`, and `owner_gate_handoff_ref`; it
cannot define the final cohort truth, mutate clinical data bodies, sign owner
receipts, create typed blockers, or claim source, runtime, publication, or
production readiness.

## Workflow

1. Define `phenotype_question_ref`: clinical condition, population, data source,
   intended use, and claim boundary.
2. Build `cohort_definition_ref`: inclusion/exclusion rules, index date,
   baseline and follow-up windows, and release/data-lock refs.
3. Build `phenotype_logic_ref`: diagnosis codes, measurements, procedures,
   medications, labs, thresholds, repeated-measure handling, and hierarchy.
4. Check `ascertainment_support_map_ref`: source fields, code lists, clinical
   rationale, literature/guideline refs, and validation evidence.
5. Check `denominator_missingness_ref`: field availability, missingness,
   implausible values, site/year drift, and sensitivity candidates.
6. Produce `route_back_candidate` for missing code lists, undefined dates,
   denominator drift, unsupported clinical definitions, or data-owner decisions.

## Handoff Shape

Return:

- `phenotype_question_ref`
- `cohort_definition_ref`
- `index_and_window_ref`
- `phenotype_logic_ref`
- `code_list_or_variable_ref`
- `ascertainment_support_map_ref`
- `denominator_missingness_ref`
- `validation_check_ref`
- `sensitivity_candidate_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn phenotype candidates into cohort truth, source readiness, data
mutation authority, owner acceptance, typed blocker, or publication readiness.
