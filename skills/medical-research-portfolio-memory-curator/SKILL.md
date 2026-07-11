---
name: medical-research-portfolio-memory-curator
description: "Use when a MAS cross-study research portfolio needs refs-only memory curation across topic landscape, dataset-question maps, venue intelligence, study recall indices, external reports, reuse proposals, stale-card review, or writeback proposal handoff. This optional specialist does not write MAS truth, accept or reject memory, sign owner receipts, create typed blockers, or claim publication readiness."
---

# Medical Research Portfolio Memory Curator

Use this optional MAS Scholar Skills specialist when a cross-study research
portfolio or publication strategy memory needs memory review, reuse/stale
assessment, external report alignment, or writeback proposal shaping before MAS
or the portfolio owner decides whether to accept, reject, refresh, or route
back the material.

This skill is refs-only and no-authority. It can prepare portfolio memory refs,
curation notes, reuse/stale proposals, `route_back_candidate`, and
`owner_gate_handoff_ref`; it cannot write MAS truth, accept or reject memory,
choose a study route, sign an owner receipt, create a typed blocker, mutate
memory bodies, or claim publication readiness.

Source-of-truth refs are the consuming MAS or portfolio workspace's current
memory, docs, contracts, external report refs, and owner surfaces. Treat local
notes, prior reports, and cross-study memories as advisory until the owning
surface accepts them.

## Publication Strategy Memory Mode

Use this mode for the former `medical-publication-strategy-memory-curator`
scope. Review Publication Strategy Memory cards, route-family applicability,
stale-card risk, writeback proposals, and accept/reject handoff packets before
the MAS memory owner decides.

Typical source refs:

- `agent/knowledge/publication_route_memory.md`
- `docs/policies/study-workflow/publication_route_memory_policy.md`

Build `publication_strategy_memory_inventory_ref`, `memory_body_review_ref`,
`current_study_alignment_ref`, `writeback_proposal_ref`, and
`accept_reject_handoff_ref`. Route back when a card is thin, stale, lacks
receipt provenance, mixes current study evidence with memory, or implies route,
evidence, verdict, or readiness authority.

## Workflow

1. Build `topic_landscape_ref`: topic families, clinical questions, recurring
   evidence patterns, known negative routes, and reusable scope boundaries.
2. Build `dataset_question_map_ref`: dataset bodies or manifests, study
   questions they can and cannot answer, cohort/version caveats, and owner
   surfaces that must accept any reuse.
3. Build `venue_intelligence_ref`: journal or venue expectations, article
   archetypes, reviewer risks, reporting standards, and where these are only
   strategy hints rather than publication authority.
4. Build `study_recall_index_ref`: study ids, memory ids, source refs, prior
   decisions, stale markers, and enough locator context for a MAS owner to
   inspect the original evidence.
5. Build `external_reports_ref`: imported report ids, provenance, applicable
   scope, stale or superseded claims, and conflicts with current study truth.
6. Build `reuse_stale_writeback_proposal_ref`: what to reuse, refresh, retire,
   or route back; required evidence refs; proposed target owner surface; and
   forbidden authority claims.
7. Produce `route_back_candidate` when the portfolio memory is stale, lacks
   provenance, mixes studies without source boundaries, implies owner
   acceptance, or would turn an external report into MAS truth.

## Handoff Shape

Return:

- `topic_landscape_ref`
- `dataset_question_map_ref`
- `venue_intelligence_ref`
- `study_recall_index_ref`
- `external_reports_ref`
- `reuse_stale_writeback_proposal_ref`
- `candidate_refs`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn research portfolio memory curation into memory acceptance, MAS
truth, owner receipt, typed blocker, human gate, quality verdict, current
package authority, or publication readiness.
