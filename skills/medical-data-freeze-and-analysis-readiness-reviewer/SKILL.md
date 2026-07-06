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
6. Build `analysis_readiness_gap_ref`: missing owner decision, unstable body,
   unresolved lineage, variable ambiguity, privacy/access concern, or analysis
   contract gap.
7. Produce `route_back_candidate` for data owner, analysis owner, or study owner
   decisions.

## Handoff Shape

Return:

- `data_freeze_inventory_ref`
- `data_lock_window_ref`
- `analysis_dataset_boundary_ref`
- `dictionary_and_lineage_ref`
- `missingness_and_exclusion_ref`
- `analysis_readiness_gap_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a data-freeze review into source readiness approval, analysis
authority, MAS truth, owner receipt, typed blocker, clinical data mutation,
current-package authority, or publication readiness.
