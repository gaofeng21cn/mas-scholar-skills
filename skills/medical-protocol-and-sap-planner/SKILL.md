---
name: medical-protocol-and-sap-planner
description: "Use when a MAS medical-paper task needs a refs-only clinical protocol or statistical analysis plan planner for observational or drug/device interventional studies: study question, population, endpoints, estimand, analysis sets, randomization/blinding, schedule of activities, safety oversight, missingness, sensitivity, reporting standards, SAP outline, and owner-gate handoff. This optional MAS Scholar Skills specialist does not write MAS truth, sign owner receipts, create typed blockers, or claim regulatory, source, runtime, publication, or production readiness."
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
interventional-design, schedule-of-activities, safety-oversight, SAP checklist,
and protocol handoff skeletons. It is stdlib-only and no-authority.

## Workflow

1. Define `protocol_question_ref`: population, exposure/intervention,
   comparator, outcomes, time horizon, setting, and intended paper claim.
2. Build `protocol_scope_ref`: study design, eligibility, index/randomization
   date, follow-up, data source, ethics/consent notes, intervention category,
   registry refs, and reporting guideline target.
3. Build `sap_candidate_ref`: estimand, analysis sets, endpoint definitions,
   covariates, missingness plan, multiplicity, subgroup, sensitivity, and
   robustness checks.
4. For a drug/device interventional study, add `interventional_design_ref`:
   intervention/comparator details, allocation sequence and concealment,
   randomization unit and stratification, blinding, controlled unblinding,
   adherence/accountability, concomitant care, and protocol deviations.
5. Build `schedule_of_activities_ref`: visits, windows, intervention delivery,
   efficacy and safety assessments, sample/specimen timing, and early
   withdrawal/follow-up. Keep it traceable to endpoint and safety definitions.
6. Build `safety_oversight_ref`: AE/SAE definitions and collection windows,
   expedited reporting route, DSMB/independent monitoring need, interim and
   stopping rules, medical monitoring, and intervention/device accountability.
7. Map each method choice to `support_map_ref`: source/data refs, literature,
   current trial-registry or regulator refs, statistical rationale, applicable
   current formal standard refs, and owner decision points.
8. Produce the smallest `route_back_candidate` when protocol/SAP inputs are
   missing, contradictory, or beyond the skill authority.

## Interventional Mode

Use the interventional additions only when the design actually assigns a drug,
biologic, procedure, behavioral intervention, or device. Observational studies
may mark these refs `not_applicable` rather than invent trial machinery.

Refresh current formal standards and regulator/registry requirements at time of
use. SPIRIT, ICH, CONSORT extensions, ClinicalTrials.gov, WHO registry, FDA, EMA,
NMPA, ethics-board, sponsor, and device-specific requirements may change and
are jurisdiction- and study-specific; this skill does not freeze their wording
or convert a generic checklist into regulatory compliance.

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
- `interventional_design_ref`
- `schedule_of_activities_ref`
- `safety_oversight_ref`
- `trial_registry_evidence_map_ref`
- `support_map_ref`
- `candidate_refs`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a protocol or SAP candidate into study approval, regulatory or
registry compliance, analysis authority, owner acceptance, typed blocker, or
publication readiness.
