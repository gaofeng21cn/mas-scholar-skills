---
name: medical-indication-dossier
description: "Use when MAS needs a refs-only indication dossier specialist playbook inspired by AcademicForge indication-dossier. It organizes patient-population waypoints, epidemiology, biology, standard-of-care, trial/regulatory, synthesis, and writing-style candidate refs without writing domain truth, signing owner receipts, creating typed blockers, or claiming publication readiness."
---

# Medical Indication Dossier

Use this optional MAS Scholar Skills specialist when a MAS task needs a
patient-population waypoint dossier for an indication, disease area, or
therapeutic opportunity. It adapts AcademicForge HEAD
`54a2f333973147a1fd703caea6f12252e1f227d6` `indication-dossier` patterns.

This skill is refs-only and no-authority. It can prepare patient-population
waypoint refs, evidence synthesis refs, deterministic receipt refs, and
`owner_gate_handoff_ref`; it cannot write MAS study truth, clinical strategy
truth, owner receipt, typed blocker, quality verdict, or publication readiness.

Optional deterministic helper: `kernel.py` provides dossier handoff shells,
waypoint matrices, source manifest summaries, and authority lints.

## Waypoint Workflow

1. Define `indication_scope_ref`, target geography, timeframe, population, and
   decision question.
2. Build a patient-population waypoint map:
   - `population_definition_ref`
   - `epidemiology_waypoint_ref`
   - `biology_soc_waypoint_ref`
   - `regulatory_trials_waypoint_ref`
   - `unmet_need_waypoint_ref`
   - `synthesis_candidate_ref`
3. Keep sources explicit: guideline, trial registry, label, epidemiology,
   mechanism, standard-of-care, comparator, and patient-subgroup refs.
4. Separate evidence summary from owner decision. Missing or conflicting evidence
   becomes `route_back_candidate`, not a typed blocker.
5. Produce a compact dossier handoff for MAS or the consuming domain owner.

## Handoff Shape

Return:

- `indication_question`
- `population_definition_ref`
- `epidemiology_waypoint_ref`
- `biology_soc_waypoint_ref`
- `regulatory_trials_waypoint_ref`
- `patient_population_waypoint_ref`
- `synthesis_candidate_ref`
- `source_manifest_ref`
- `environment_receipt_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a dossier candidate into clinical recommendation, market verdict,
owner acceptance, typed blocker, or publication readiness.
