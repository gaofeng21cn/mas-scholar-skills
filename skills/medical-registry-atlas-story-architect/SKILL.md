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

Optional skill-local helper: use `kernel.py` for deterministic registry story
map skeletons, claim-boundary labels, and forbidden-authority lint.

When MAS supplies `registry_signal_validity_pack` or an
`ehr_registry_signal_validity_ref`, consume the single canonical rule at
`references/professional-quality-ref-templates.md#ehr-registry-signal-validity-ref`
for optional framing only. This skill may contribute registry-story and
narrative-boundary candidates, but it does not produce or own the integrated
validity ref; route that judgment to `medical-statistical-review`. Its local
`claim_boundary_ref` remains a story-framing input and cannot substitute for the
aggregate validity judgment.

## Workflow

1. Build `handling_editor_first_draft_contract_ref` before sentences: one
   unique scientific claim, clinical or operational value, falsifiable
   boundary, Results-paragraph jobs, figure/table narrative arc, and main-text
   versus supplement placement. Templates are references, not substitutes for
   professional story judgment.
2. Build `registry_story_contract_ref`: one-sentence discovery contract,
   clinical audience, registry role, descriptive scope, and forbidden claim
   types. Treat denominator architecture and missing, unresolved, resolved,
   and unavailable states as scientific results when they define what the
   registry can support.
3. Build `cohort_and_data_lock_ref`: data source, enrollment/data-lock window,
   inclusion/exclusion flow, available fields, subcohort limits, and ethics or
   consent references.
4. Build `phenotype_axis_ref`: registry variables, diagnostic fields,
   recorded status, treatment exposure, severity strata, missingness, and
   denominator rules.
5. Build `denominator_state_architecture_ref`: separate eligible, candidate,
   resolved, unresolved, missing/unavailable, and absolute flagged-record
   counts. Name each numerator, denominator, unit, and visual semantic.
6. Build `figure_table_story_map_ref`: each table/figure job, claim served,
   required denominator, missingness display, and caption boundary.
7. Build `center_sensitivity_claim_binding_ref` whenever center/site dependence
   reaches the abstract or conclusion. Require a claim-evidence-map row with
   analysis source and all supporting main/supplement display refs.
8. Check `claim_boundary_ref`: avoid prevalence, burden, causality, prediction,
   guideline nonadherence, or service-quality claims unsupported by registry
   design. Treat `gap`, `intensity`, `burden`, `adherence`, `workload`, and
   `quality ranking` as boundary terms across manuscript, tables, figures, CSV
   headers, machine endpoints, and supplements. Without direct evidence, use
   `candidate audit signal`, `recorded-field signal`, or `absolute flagged-record
   count`; actual treatment, adherence, workload, and quality ranking remain
   unmeasured.
9. Build `discussion_theme_ref`: compress findings into registry structure,
   clinical phenotype, service-review mismatch, and subcohort-depth themes.
10. Produce `route_back_candidate` for missing data-lock, weak story contract,
   overclaim, figure/table drift, or owner manuscript decisions.

## Handoff Shape

Return:

- `registry_story_contract_ref`
- `handling_editor_first_draft_contract_ref`
- `cohort_and_data_lock_ref`
- `phenotype_axis_ref`
- `denominator_state_architecture_ref`
- `figure_table_story_map_ref`
- `center_sensitivity_claim_binding_ref`
- `claim_boundary_ref`
- `discussion_theme_ref`
- `candidate_refs`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a registry story candidate into MAS truth, clinical burden truth,
owner receipt, typed blocker, reviewer receipt, publication readiness, or
current-package authority.
