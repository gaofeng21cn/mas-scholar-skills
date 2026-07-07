---
name: medical-methodology-routeback-reviewer
description: "Use when a MAS medical-paper task needs refs-only AI-first review of terminal methodology blockers, provenance-limited harmonization, clean rebuild routes, stop-loss decisions, or human-gate handoff. This optional specialist reviews methodology route-back candidates but does not write MAS truth, sign owner receipts, create typed blockers, or claim readiness."
---

# Medical Methodology Routeback Reviewer

Use this optional MAS Scholar Skills specialist when a terminal methodology or
source-provenance blocker needs AI-first review before MAS decision, analysis
harmonization, source provenance, or human-gate owner surfaces choose the next
legal route.

This skill is refs-only and no-authority. It can prepare methodology review
refs, route option analysis, stop/continue recommendations,
`route_back_candidate`, and `owner_gate_handoff_ref`; it cannot write MAS
truth, select the route with owner authority, sign an owner receipt, create a
typed blocker, mutate paper or package artifacts, or claim source, runtime,
publication, submission, production, or current-package readiness.

MAS currently keeps the deterministic route shell in
`src/med_autoscience/controllers/stage_outcome_authority_parts/action_execution/methodology_reframe_decision.py`.
That shell materializes `methodology_reframe_route_decision` and route options
such as `provenance_limited_harmonization_audit`,
`rebuild_reproducible_model_route`, `stop_loss_current_transport_claim`, and
`human_gate`. This skill provides the AI reviewer judgment and owner handoff
packet around those options; it does not replace the MAS decision owner or
analysis/source owner surfaces.

## Workflow

1. Build `methodology_blocker_inventory_ref`: blocker source, affected study,
   current owner route, source provenance refs, analysis harmonization refs,
   task-intake refs, and the claims that must not advance.
2. Build `provenance_limited_harmonization_review_ref`: what evidence can be
   interpreted under limited provenance, which transported-model or harmonized
   claims must be downgraded, and what audit output is still useful.
3. Build `clean_rebuild_route_review_ref`: required clean rebuild
   authorization, unit harmonization inputs, reproducible model route,
   accepted prior owner outputs, and minimum rerun evidence expected before
   manuscript claim work.
4. Build `stop_loss_review_ref`: when the current claim should be stopped,
   narrowed, tombstoned, or converted into a negative/provenance limitation
   rather than repaired.
5. Build `human_gate_handoff_ref`: the smallest human decision packet when the
   AI reviewer cannot choose among legal routes without owner confirmation.
6. Build `owner_route_recommendation_ref`: recommended next owner, next work
   unit, legal entry point, required output, and explicit forbidden shortcuts
   such as prose repair, package refresh, or AI reviewer rerun closing a hard
   methodology blocker.
7. Produce `route_back_candidate` when evidence is insufficient, currentness is
   unclear, the candidate would self-loop on `methodology_reframe_route_decision`,
   or the handoff would imply typed-blocker or readiness authority.

## Handoff Shape

Return:

- `methodology_blocker_inventory_ref`
- `provenance_limited_harmonization_review_ref`
- `clean_rebuild_route_review_ref`
- `stop_loss_review_ref`
- `human_gate_handoff_ref`
- `owner_route_recommendation_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn methodology route-back review into MAS truth, owner receipt, typed
blocker, quality verdict, owner acceptance, artifact mutation, current-package
authority, or publication readiness.
