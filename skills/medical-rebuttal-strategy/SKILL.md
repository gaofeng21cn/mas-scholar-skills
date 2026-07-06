---
name: medical-rebuttal-strategy
description: "Use when a MAS medical-paper task needs refs-only reviewer response and rebuttal strategy: comment triage, evidence-response map, manuscript delta plan, experiment/analysis route-back, response tone, owner-gate handoff, and stop/continue recommendation. This optional specialist does not sign reviewer receipts, write MAS truth, create typed blockers, or claim acceptance/readiness."
---

# Medical Rebuttal Strategy

Use this optional MAS Scholar Skills specialist when reviewer comments, editorial
requests, or internal critique need a response strategy before MAS/domain owner
acceptance.

This skill is refs-only and no-authority. It can prepare response strategy refs,
manuscript-delta maps, `route_back_candidate`, and `owner_gate_handoff_ref`; it
cannot sign reviewer receipts, accept or reject reviews, write MAS truth, create
typed blockers, mutate final artifacts, or claim publication readiness.

## Workflow

1. Build `review_comment_inventory_ref`: comment id, source, severity, target
   section/table/figure, requested action, and implied evidence need.
2. Classify each comment in `response_route_ref`: answer in text, manuscript
   revision, table/figure change, analysis/statistics route-back, literature
   support, data/source owner decision, or non-actionable boundary.
3. Build `evidence_response_map_ref`: current evidence, missing evidence,
   proposed answer, manuscript delta, and owner decision target.
4. Draft `rebuttal_strategy_ref`: respectful response stance, concession/
   clarification boundary, claim downgrade, and consistency checks.
5. Produce `route_back_candidate` when a comment requires new analysis,
   owner authority, human author input, journal-policy decision, or data access.

## Handoff Shape

Return:

- `review_comment_inventory_ref`
- `response_route_ref`
- `evidence_response_map_ref`
- `manuscript_delta_plan_ref`
- `rebuttal_strategy_ref`
- `stop_or_continue_recommendation`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a rebuttal plan into reviewer acceptance, owner receipt, typed
blocker, publication readiness, or current-package authority.
