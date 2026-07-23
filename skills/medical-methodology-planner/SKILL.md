---
name: medical-methodology-planner
description: "Use when a profiled MAS medical-paper or MAG medical-grant task needs refs-only methodology planning across protocol/SAP, cohort phenotyping, causal design, survival analysis, risk-model transportability, registry design, or data readiness. The consuming Agent retains truth, verdict, receipt, blocker, and readiness authority."
---

# Medical Methodology Planner

Use this optional MAS Scholar Skills router when a named method task needs one
module-level planning pass instead of several narrow specialist skills.

This skill is refs-only and no-authority. It can prepare methodology candidate
refs, support maps, `route_back_candidate`, and `owner_gate_handoff_ref`; it
cannot write MAS truth, approve an analysis, sign an owner receipt, create a
typed blocker, mutate artifacts or data bodies, or claim source, runtime,
publication, production, or current-package readiness.

## Consumer Modes

- MAS paper mode preserves the current paper question, protocol/SAP, analysis,
  reporting, and publication-oriented routes.
- MAG grant mode consumes only owner-supplied grant artifact refs,
  `source_pack_ref`, and any owner-provided epistemic scope. Ignore MAS-only
  manuscript, journal, publication, and reviewer-snapshot refs when absent.
  Plan the proposed aims, design, population, endpoints, feasibility,
  assumptions, alternatives, milestones, and risk mitigations in grant scope.

In MAG grant mode, return `grant_methodology_plan_candidate_ref` through
`candidate_refs` with `route_back_candidate` and
`owner_gate_handoff_ref`. It cannot write grant truth or claim fundability, a
quality verdict, export readiness, methodology approval, a receipt, or a
blocker.

When MAS supplies `registry_signal_validity_pack` or an
`ehr_registry_signal_validity_ref`, use
`references/professional-quality-ref-templates.md#ehr-registry-signal-validity-ref`
as the single rule and route the integrated judgment to
`medical-statistical-review`. This router may select cohort-phenotyping or data-
governance input routes, but it must not reproduce the pack checklist or create
a second methodology validity verdict.

## Routes

- Protocol/SAP: `protocol_question_ref`, `endpoint_definition_ref`,
  `estimand_and_analysis_set_ref`, `sap_candidate_ref`.
- Cohort/phenotyping: `cohort_definition_ref`, `phenotype_logic_ref`,
  `code_list_or_variable_ref`, `denominator_missingness_ref`.
- Causal/survival/risk modeling: `target_trial_candidate_ref`,
  `dag_or_confounder_map_ref`, `time_origin_and_risk_set_ref`,
  `transportability_assessment_ref`.
- Registry/data freeze: `registry_story_contract_ref`,
  `cohort_and_data_lock_ref`, `analysis_dataset_boundary_ref`,
  `analysis_readiness_gap_ref`.

## Workflow

1. Build `methodology_question_ref`: study question, paper claim, data surface,
   target module, and owner decision target.
2. Select the smallest route family that answers the method question.
3. Build `methodology_plan_ref`: assumptions, eligibility, timing, estimand,
   analysis set, source variables, sensitivity checks, and reporting standard.
4. Build `methodology_support_map_ref`: source refs, literature/guideline refs,
   data-owner decisions, and unresolved owner inputs.
5. Produce `route_back_candidate` only when required evidence or owner authority
   is missing.

## Handoff Shape

Return:

- `methodology_question_ref`
- `methodology_route_ref`
- `methodology_plan_ref`
- `methodology_support_map_ref`
- `candidate_refs`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a methodology plan into study truth, source readiness, analysis
approval, owner acceptance, typed blocker, quality verdict, or publication
readiness. This skill cannot claim publication readiness.
