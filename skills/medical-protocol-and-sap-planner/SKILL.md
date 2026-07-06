---
name: medical-protocol-and-sap-planner
description: "Use when a MAS medical-paper task needs a refs-only clinical protocol or statistical analysis plan planner: study question, population, endpoints, estimand, analysis sets, missingness, sensitivity, reporting standards, SAP outline, and owner-gate handoff. This optional MAS Scholar Skills specialist does not write MAS truth, sign owner receipts, create typed blockers, or claim source, runtime, publication, or production readiness."
---

# Medical Protocol And SAP Planner

Use this optional MAS Scholar Skills specialist when a medical study needs a
protocol or statistical analysis plan candidate before MAS/domain owner review.

This skill is refs-only and no-authority. It can prepare candidate refs,
support maps, `route_back_candidate`, and `owner_gate_handoff_ref`; it cannot
write MAS study truth, approve a protocol, sign an owner receipt, create a
typed blocker, mutate artifacts, or claim source, runtime, publication, or
production readiness.

Optional helper: use `kernel.py` for deterministic PICO, estimand, endpoint,
SAP checklist, and protocol handoff skeletons. It is stdlib-only and
no-authority.

## Workflow

1. Define `protocol_question_ref`: population, exposure/intervention,
   comparator, outcomes, time horizon, setting, and intended paper claim.
2. Build `protocol_scope_ref`: study design, eligibility, index date, follow-up,
   data source, ethics/consent notes, and reporting guideline target.
3. Build `sap_candidate_ref`: estimand, analysis sets, endpoint definitions,
   covariates, missingness plan, multiplicity, subgroup, sensitivity, and
   robustness checks.
4. Map each method choice to `support_map_ref`: source/data refs, literature or
   guideline refs, statistical rationale, and owner decision points.
5. Produce the smallest `route_back_candidate` when protocol/SAP inputs are
   missing, contradictory, or beyond the skill authority.

## Handoff Shape

Return:

- `protocol_question_ref`
- `protocol_scope_ref`
- `eligibility_and_flow_ref`
- `endpoint_definition_ref`
- `estimand_and_analysis_set_ref`
- `sap_candidate_ref`
- `missingness_and_sensitivity_ref`
- `reporting_guideline_ref`
- `support_map_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a protocol or SAP candidate into a study approval, analysis
authority, owner acceptance, typed blocker, or publication readiness claim.
