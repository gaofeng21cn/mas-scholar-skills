---
name: medical-evidence-synthesis-and-claim-map
description: "Use when a profiled MAS medical-paper or MAG medical-grant task needs refs-only evidence synthesis and claim mapping: claim inventory, support grading, gaps, contradictions, route-back, and owner-gate handoff. The consuming Agent retains truth, verdict, receipt, blocker, and readiness authority."
---

# Medical Evidence Synthesis And Claim Map

Use this optional MAS Scholar Skills specialist when manuscript claims,
literature refs, results, tables, figures, and limitations need a compact
evidence synthesis map before MAS/domain owner consumption.

This skill is refs-only and no-authority. It can prepare claim-map candidate
refs, support grading, `route_back_candidate`, and `owner_gate_handoff_ref`; it
cannot accept citations, write MAS truth, issue quality verdicts, sign owner
receipts, create typed blockers, or claim publication readiness.

## Consumer Modes

- MAS paper mode preserves manuscript claim families, result/table/figure
  support, citation integration, limitations, and publication routes.
- MAG grant mode consumes only owner-supplied grant artifact refs,
  `source_pack_ref`, and any owner-provided epistemic scope. Ignore MAS-only
  manuscript, journal, publication, and reviewer-snapshot refs when absent.
  Map significance, innovation, aims, approach, feasibility, preliminary
  evidence, alternatives, and risk claims to their actual support.

In MAG grant mode, return `grant_claim_map_candidate_ref` through
`candidate_refs` with `route_back_candidate` and
`owner_gate_handoff_ref`. It cannot write grant truth or claim fundability, a
quality verdict, export readiness, evidence acceptance, a receipt, or a
blocker. The consuming Agent alone may issue an owner receipt.

Optional helper: use `kernel.py` for deterministic claim/evidence matrix
scaffolds, support-strength vocabulary lint, and claim-map handoff skeletons.
It is stdlib-only and no-authority.

## Workflow

1. Inventory claims into `claim_inventory_ref`: background, method, result,
   interpretation, limitation, guideline, and causal/predictive claims.
2. Link each claim to `source_support_ref`: manuscript location, result/table/
   figure refs, literature/source refs, and required support type.
3. Grade support in `support_strength_map_ref`: direct primary, direct
   guideline, method precedent, contextual, contradictory, weak, or missing.
4. Build `contradiction_and_gap_ref`: unsupported claims, overclaim risk,
   source mismatch, stale evidence, circular support, and missing identifiers.
5. Produce `route_back_candidate` for claims that require owner downgrading,
   source repair, analysis/table/figure repair, or manuscript revision.

## Handoff Shape

Return:

- `claim_inventory_ref`
- `claim_type_map_ref`
- `source_support_ref`
- `support_strength_map_ref`
- `contradiction_and_gap_ref`
- `claim_revision_candidate_ref`
- `evidence_synthesis_summary_ref`
- `candidate_refs`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not convert a claim map into citation authority, quality verdict, owner
acceptance, typed blocker, publication readiness, or current-package authority.
