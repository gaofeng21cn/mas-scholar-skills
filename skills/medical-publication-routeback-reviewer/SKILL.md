---
name: medical-publication-routeback-reviewer
description: "Use when a MAS medical-paper task needs refs-only publication route-back review across rebuttal strategy, owner-gate handoff, display QC/regression, publication strategy memory, portfolio memory, or terminal methodology route decisions. This optional reviewer does not write MAS truth, sign owner receipts, create typed blockers, or claim readiness."
---

# Medical Publication Routeback Reviewer

Use this optional MAS Scholar Skills reviewer when a named publication,
revision, display, memory, or owner-gate handoff task needs one route-back
review instead of several narrow optional specialists.

This skill is refs-only and no-authority. It can prepare route-back review refs,
residual risk refs, `stop_or_continue_recommendation`, `route_back_candidate`,
and `owner_gate_handoff_ref`; it cannot write MAS truth, choose the publication
route with owner authority, sign an owner receipt, create a typed blocker,
mutate artifacts, accept memory, or claim publication, submission, runtime,
production, or current-package readiness.

Use this reviewer only when one publication route-back pass is enough. If the
problem is primary writing, review, stats, table, figure, literature,
submission, or data/source judgment, route to the corresponding professional
skill instead of creating a parallel module. This reviewer may aggregate AI
candidate judgments, but it does not replace them or expand default exposure.

## Routes

- Revision/rebuttal: `review_comment_inventory_ref`, `response_route_ref`,
  `manuscript_delta_plan_ref`.
- Owner handoff: `handoff_inventory_ref`, `authority_boundary_ref`,
  `evidence_to_owner_map_ref`, `residual_risk_ref`.
- Display route-back: `display_artifact_inventory_ref`,
  `export_integrity_ref`, `artifact_diff_ref`, `repair_route_ref`.
- Strategy and memory: `publication_strategy_memory_inventory_ref`,
  `study_recall_index_ref`, `writeback_proposal_ref`.
- Terminal methodology route-back: `methodology_blocker_inventory_ref`,
  `owner_route_recommendation_ref`, `human_gate_handoff_ref`.

## Workflow

1. Build `publication_routeback_inventory_ref`: candidate package, review
   comments, artifacts, memory cards, terminal blockers, and target owner.
2. Build `authority_boundary_ref`: allowed refs-only advice and forbidden
   owner/readiness claims.
3. Build `routeback_option_map_ref`: revise, repair, rerun, narrow, stop-loss,
   human gate, owner gate, or memory writeback proposal.
4. Build `residual_risk_ref`: clinical, statistical, display, citation, data,
   submission, or currentness risks that remain owner decisions.
5. Produce `stop_or_continue_recommendation` and the smallest
   `route_back_candidate` without creating a typed blocker.

## Handoff Shape

Return:

- `publication_routeback_inventory_ref`
- `authority_boundary_ref`
- `routeback_option_map_ref`
- `residual_risk_ref`
- `stop_or_continue_recommendation`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn route-back review into MAS truth, owner receipt, typed blocker,
quality verdict, owner acceptance, current-package authority, memory
acceptance, or publication readiness. This skill cannot claim publication readiness.
