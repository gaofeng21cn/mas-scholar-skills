---
name: medical-publication-strategy-memory-curator
description: "Use when a MAS medical-paper task needs refs-only Publication Strategy Memory review, curation, writeback proposal shaping, accept/reject handoff, stale-card review, or route-memory risk surfacing. This optional specialist does not accept memory, choose routes, write MAS truth, sign owner receipts, create typed blockers, or claim publication readiness."
---

# Medical Publication Strategy Memory Curator

Use this optional MAS Scholar Skills specialist when Publication Strategy Memory
needs review, curation, stale-card inspection, writeback proposal shaping, or
accept/reject handoff to the MAS memory owner.

This skill is refs-only and no-authority. It can prepare memory review refs,
curation notes, writeback proposal refs, `route_back_candidate`, and
`owner_gate_handoff_ref`; it cannot accept or reject memory, choose the
publication route, write MAS truth, sign an owner receipt, create a typed
blocker, mutate memory bodies, or claim publication readiness.

Source-of-truth refs:

- `agent/knowledge/publication_route_memory.md`
- `docs/policies/study-workflow/publication_route_memory_policy.md`

## Workflow

1. Build `publication_strategy_memory_inventory_ref`: memory ids, route family,
   stage applicability, status, freshness, locator refs, and receipt refs.
2. Build `memory_body_review_ref`: card shape, prose usefulness, claim
   boundary, minimum evidence package, reviewer risks, stop/pivot rules, and
   source refs.
3. Build `current_study_alignment_ref`: current study charter, evidence refs,
   source readiness refs, manuscript refs, controller decisions, and where the
   memory is advisory only.
4. Build `writeback_proposal_ref`: source stage, receipt refs, reusable lesson
   body, evidence refs, failed-path refs, proposed accept/reject outcome, and
   target MAS router surface.
5. Build `accept_reject_handoff_ref`: smallest owner-facing packet for MAS
   reviewer/auditor or route authority to accept, reject, refresh, deprecate,
   or route back the proposed memory change.
6. Produce `route_back_candidate` when a card is too thin, stale, lacks receipt
   provenance, mixes current evidence with memory, or would imply route,
   evidence, verdict, or readiness authority.

## Handoff Shape

Return:

- `publication_strategy_memory_inventory_ref`
- `memory_body_review_ref`
- `current_study_alignment_ref`
- `writeback_proposal_ref`
- `accept_reject_handoff_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn Publication Strategy Memory review into route selection, memory
acceptance, MAS truth, owner receipt, typed blocker, quality verdict, current
package authority, or publication readiness.
