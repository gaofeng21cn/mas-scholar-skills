---
name: medical-data-freeze-and-analysis-readiness-reviewer
description: "Use when a MAS medical-paper task needs refs-only data freeze and analysis readiness review: data-lock window, dataset boundary, lineage, dictionary, exclusions, missingness, analysis inputs, route-back, and owner-gate handoff. This optional specialist does not approve source readiness, write MAS truth, sign owner receipts, create typed blockers, or claim readiness."
---

# Medical Data Freeze And Analysis Readiness Reviewer

Use this optional MAS Scholar Skills specialist when a clinical dataset,
registry extract, analysis table, or paper-facing cohort needs data-freeze and
analysis-readiness review before MAS/domain owner decisions.

This skill is refs-only and no-authority. It can prepare data freeze and
analysis readiness refs, support maps, `route_back_candidate`, and
`owner_gate_handoff_ref`; it cannot approve source readiness, write MAS truth,
sign an owner receipt, create a typed blocker, mutate clinical data bodies, or
claim publication readiness.

Optional skill-local helper: use `kernel.py` for deterministic data-freeze
review skeletons, lineage rows, and forbidden-authority lint.

## Workflow

1. Build `data_freeze_inventory_ref`: authoritative body ref, extract refs,
   freeze label, hashes or manifests, owner-supplied lock note, and derived
   working copies.
2. Build `data_lock_window_ref`: enrollment period, data extraction date,
   follow-up closure, outcome ascertainment window, and post-freeze change
   policy.
3. Build `analysis_dataset_boundary_ref`: paper-facing cohort, analysis tables,
   inclusion/exclusion flow, subcohorts, denominator rules, and non-authority
   convenience copies.
4. Build `dictionary_and_lineage_ref`: variable dictionary, codebook, source
   lineage, transformations, units, coding, and known unavailable variables.
5. Check `missingness_and_exclusion_ref`: missingness profile, exclusion
   reasons, adult/child or known-age sensitivity, and site/year/threshold
   sensitivity needs.
6. Build `clinical_analysis_input_identity_ref` with an explicit
   `study_context`: whether the study has longitudinal follow-up, is
   multicenter, and requires separate endpoint adjudication. Cohort/enrollment,
   extract date, disease definition, endpoint ascertainment, dictionary,
   lineage, ethics/governance, and analysis-set boundary must be present and
   cannot be waived as not applicable. Follow-up closure/completeness, center
   inventory, and endpoint-adjudication evidence are required only when their
   context trigger is true; otherwise record a reasoned not-applicable
   disposition. Use the three explicit states `present`, `missing`, and
   `not_applicable_with_reason`; every `present` item must carry an exact
   kind/ref/size/SHA-256 ref.
   Bind the three study-context triggers to an exact `study_context_ref`; a
   false trigger cannot contradict present longitudinal, center, adjudication,
   fixed-horizon, or full-follow-up evidence.
   An all-N/A inventory never satisfies identity closure. Record
   cohort/unit/deduplication, center, endpoint, follow-up, and
   governance identity separately so one coarse ref cannot hide a missing
   clinical identity component. Add `endpoint_state_counts` with analysis N,
   declared time basis, target events, competing events, unknown cause, early
   censoring, event-free count, exact
   source-policy ref, and exact regeneration ref; the four states must exhaust
   analysis N. Early censoring is a separate state only under fixed-horizon
   accounting.
   Run `validate_clinical_analysis_input_identity_candidate_v2()` for new
   candidates. The unversioned validator preserves the earlier compact-string
   v1 input contract for same-major callers.
7. Build `analysis_readiness_gap_ref`: missing owner decision, unstable body,
   unresolved lineage, variable ambiguity, privacy/access concern, or analysis
   contract gap.
8. Produce `route_back_candidate` for data owner, analysis owner, or study owner
   decisions.

## Handoff Shape

Return:

- `data_freeze_inventory_ref`
- `data_lock_window_ref`
- `analysis_dataset_boundary_ref`
- `dictionary_and_lineage_ref`
- `missingness_and_exclusion_ref`
- `analysis_readiness_gap_ref`
- `clinical_analysis_input_identity_ref`
- `candidate_refs`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a data-freeze review into source readiness approval, analysis
authority, MAS truth, owner receipt, typed blocker, clinical data mutation,
current-package authority, or publication readiness.
