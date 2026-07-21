---
name: medical-evidence-integrity-reviewer
description: "Use when a MAS medical-paper task needs refs-only evidence integrity review across claim maps, citation/reference integrity, evidence-gap triage, source support, or PDF evidence exploration. This optional reviewer does not accept citations, write MAS truth, sign owner receipts, create typed blockers, or claim readiness."
---

# Medical Evidence Integrity Reviewer

Use this optional MAS Scholar Skills reviewer when a named evidence task needs a
single integrity pass over claims, references, source support, gaps, or PDF
evidence locations.

This skill is refs-only and no-authority. It can prepare evidence integrity
refs, `verdict_candidate`, `route_back_candidate`, and
`owner_gate_handoff_ref`; it cannot accept references, write MAS truth, sign an
owner receipt, create a typed blocker, mutate manuscript/source artifacts, or
claim source, runtime, publication, production, or current-package readiness.

Use this reviewer as a narrow evidence-integrity aggregator. Claim/evidence,
source-support, citation, PDF, and evidence-gap judgment should normally land in
`medical-manuscript-review`, `medical-research-lit`, `medical-data-governance`,
or `medical-manuscript-writing` when those skills already own the work. This
skill should only unify the refs into a `verdict_candidate` and
`route_back_candidate`; it must not become a new active module or authority
surface.

## Routes

- Claim/source mapping: `claim_inventory_ref`, `source_support_ref`,
  `support_strength_map_ref`.
- Reference integrity: `reference_inventory_ref`, `identifier_integrity_ref`,
  `claim_citation_support_map_ref`.
- Evidence gaps: `evidence_gap_inventory_ref`,
  `evidence_gap_decision_candidate_ref`, `nonblocking_gap_candidate_ref`.
- PDF evidence exploration: `pdf_parse_manifest_ref`, `pdf_outline_ref`,
  `page_evidence_refs`.
- Fixed-horizon or external-validation initial drafts: consume
  `verification_scope_contract_ref` and check that every claim cites evidence
  inside the declared verified scope. For external validation, also consume
  `claim_family_scope_qualifier_ref` and `construct_comparability_ref`; check
  that no claim family borrows evidence from another and that a not-estimable
  construct stop remains visible. This reviewer aggregates these refs; their producers remain
  `medical-statistical-review` and
  `medical-risk-model-transportability-reviewer`.

## Evidence-Gap Triage Mode

Use this mode for the former `medical-evidence-gap-triage-reviewer` scope.
Classify incomplete evidence against the MAS evidence-gap decision policy and
consumption ABI as exactly one of `authority_gate`, `human_gate`,
`proceed_with_assumption`, `soft_quality_gap`, `observability_backlog`, or
`evidence_tail`.

Source-of-truth refs:

- `contracts/evidence-gap-decision-policy.json`
- `contracts/evidence-gap-consumption-abi.json`
- `contracts/schemas/evidence-gap-decision.schema.json`

For `authority_gate` or `human_gate`, build `hard_gate_candidate_ref` with the
repair owner and legal entry point. For nonblocking classes, build
`nonblocking_gap_candidate_ref` with the assumption, soft ledger,
observability backlog, or tail-evidence follow-up. Always include
`claim_boundary_ref` for forbidden readiness, owner receipt, paper progress,
or provider-running claims.

## Workflow

1. Build `evidence_integrity_inventory_ref`: claim, citation, source, PDF, and
   missing-evidence refs in scope.
2. Build `source_support_map_ref`: source-to-claim fit, population/method match,
   endpoint support, contradiction, and support strength.
3. Build `identifier_integrity_ref`: DOI/PMID/PMCID/title/year consistency,
   placeholders, duplicates, preprint/published versions, and retractions.
4. Build `evidence_gap_decision_candidate_ref`: whether the gap is an owner
   gate, human gate, proceed-with-assumption, soft quality gap, observability
   backlog, or evidence tail.
5. For fixed-horizon or external-validation initial drafts, consume
   `verification_scope_contract_ref` and reject
   evidence claims about analyses, sensitivities, displays, or reruns outside
   its declared assessed scope. For external validation, consume
   `claim_family_scope_qualifier_ref` and `construct_comparability_ref` without
   widening their allowed claims.
6. Produce `route_back_candidate` when the evidence cannot support the claim or
   the next action belongs to a source/domain owner.

## Handoff Shape

Return:

- `evidence_integrity_inventory_ref`
- `source_support_map_ref`
- `identifier_integrity_ref`
- `evidence_gap_decision_candidate_ref`
- consumed `verification_scope_contract_ref` when applicable
- consumed `claim_family_scope_qualifier_ref` when applicable
- consumed `construct_comparability_ref` when applicable
- `verdict_candidate`
- `candidate_refs`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not treat an evidence integrity candidate as source truth, citation
acceptance, typed blocker, owner receipt, reviewer receipt, quality verdict, or
publication readiness. This skill cannot claim publication readiness.
