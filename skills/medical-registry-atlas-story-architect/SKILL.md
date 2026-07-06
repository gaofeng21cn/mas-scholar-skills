---
name: medical-registry-atlas-story-architect
description: "Use when a MAS medical-paper task needs refs-only registry or atlas story architecture: data-lock/enrollment boundary, phenotype axes, descriptive claim boundary, figure/table story map, treatment-gap framing, discussion compression, route-back, and owner-gate handoff. This optional specialist does not write MAS truth, sign owner receipts, create typed blockers, or claim readiness."
---

# Medical Registry Atlas Story Architect

Use this optional MAS Scholar Skills specialist when a registry, cohort atlas,
phenotype atlas, service-variation, or treatment-gap manuscript needs a
defensible descriptive clinical story before MAS/domain owner review.

This skill is refs-only and no-authority. It can prepare registry story refs,
support maps, `route_back_candidate`, and `owner_gate_handoff_ref`; it cannot
write MAS truth, sign an owner receipt, create a typed blocker, accept claims,
or claim publication readiness.

## Workflow

1. Build `registry_story_contract_ref`: one-sentence discovery contract,
   clinical audience, registry role, descriptive scope, and forbidden claim
   types.
2. Build `cohort_and_data_lock_ref`: data source, enrollment/data-lock window,
   inclusion/exclusion flow, available fields, subcohort limits, and ethics or
   consent references.
3. Build `phenotype_axis_ref`: registry variables, diagnostic fields,
   recorded status, treatment exposure, severity strata, missingness, and
   denominator rules.
4. Build `figure_table_story_map_ref`: each table/figure job, claim served,
   required denominator, missingness display, and caption boundary.
5. Check `claim_boundary_ref`: avoid prevalence, burden, causality, prediction,
   guideline nonadherence, or service-quality claims unsupported by registry
   design.
6. Build `discussion_theme_ref`: compress findings into registry structure,
   clinical phenotype, service-review mismatch, and subcohort-depth themes.
7. Produce `route_back_candidate` for missing data-lock, weak story contract,
   overclaim, figure/table drift, or owner manuscript decisions.

## Handoff Shape

Return:

- `registry_story_contract_ref`
- `cohort_and_data_lock_ref`
- `phenotype_axis_ref`
- `figure_table_story_map_ref`
- `claim_boundary_ref`
- `discussion_theme_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a registry story candidate into MAS truth, clinical burden truth,
owner receipt, typed blocker, reviewer receipt, publication readiness, or
current-package authority.
