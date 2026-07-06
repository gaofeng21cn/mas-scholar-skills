---
name: medical-owner-gate-handoff-reviewer
description: "Use when a MAS medical-paper task needs refs-only owner-gate handoff review: candidate package inventory, authority boundary, evidence-to-owner map, missing owner decision inputs, route-back, residual risk, and handoff shape. This optional specialist does not sign owner receipts, write MAS truth, create typed blockers, or claim readiness."
---

# Medical Owner Gate Handoff Reviewer

Use this optional MAS Scholar Skills specialist when a candidate package,
review packet, artifact bundle, or method handoff needs owner-gate readiness
review before MAS/domain owner consumption.

This skill is refs-only and no-authority. It can prepare handoff review refs,
support maps, `route_back_candidate`, and `owner_gate_handoff_ref`; it cannot
write MAS truth, sign an owner receipt, create a typed blocker, accept a
handoff, or claim publication readiness.

## Workflow

1. Build `handoff_inventory_ref`: candidate refs, artifacts, source refs,
   assumptions, review packets, unsigned receipts, and target owner surface.
2. Build `authority_boundary_ref`: what the skill can suggest, what the
   downstream owner must decide, and which readiness or receipt claims are
   forbidden here.
3. Build `evidence_to_owner_map_ref`: evidence item, owner question, accepted
   ref family, missing input, and legal route-back target.
4. Check `candidate_package_consistency_ref`: stale refs, mixed worktrees,
   mismatched artifact roots, unresolved comments, and duplicate truth sources.
5. Build `residual_risk_ref`: unresolved clinical, statistical, display,
   citation, data, or submission risks that need owner decision or route-back.
6. Produce `route_back_candidate` when owner inputs are missing or the handoff
   would imply authority this repository does not hold.

## Handoff Shape

Return:

- `handoff_inventory_ref`
- `authority_boundary_ref`
- `evidence_to_owner_map_ref`
- `candidate_package_consistency_ref`
- `residual_risk_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a handoff review into MAS truth, owner receipt, typed blocker,
quality verdict, owner acceptance, current-package authority, or publication
readiness.
