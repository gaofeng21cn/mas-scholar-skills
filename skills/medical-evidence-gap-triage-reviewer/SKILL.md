---
name: medical-evidence-gap-triage-reviewer
description: "Use when a MAS medical-paper task needs refs-only evidence-gap triage against the MAS evidence-gap decision policy and ABI: authority_gate, human_gate, proceed_with_assumption, soft_quality_gap, observability_backlog, and evidence_tail classification advice. This optional specialist does not create typed blockers, declare progress, or claim readiness."
---

# Medical Evidence Gap Triage Reviewer

Use this optional MAS Scholar Skills specialist when incomplete evidence needs
AI-first classification advice against the MAS evidence-gap decision policy,
consumption ABI, and decision schema.

This skill is refs-only and no-authority. It can prepare evidence-gap triage
refs, decision candidate refs, `route_back_candidate`, and
`owner_gate_handoff_ref`; it cannot create a typed blocker, write MAS truth,
sign an owner receipt, declare paper progress, or claim source, runtime,
submission, production, or publication readiness.

Source-of-truth refs:

- `contracts/evidence-gap-decision-policy.json`
- `contracts/evidence-gap-consumption-abi.json`
- `contracts/schemas/evidence-gap-decision.schema.json`

## Workflow

1. Build `evidence_gap_inventory_ref`: source surface, missing ref family,
   affected action, evidence refs, diagnostic refs, and claim boundary.
2. Classify `evidence_gap_decision_candidate_ref` into exactly one MAS class:
   `authority_gate`, `human_gate`, `proceed_with_assumption`,
   `soft_quality_gap`, `observability_backlog`, or `evidence_tail`.
3. Build `hard_gate_candidate_ref` only for `authority_gate` or `human_gate`
   cases, naming the repair owner, legal entry point, and why current action
   cannot continue.
4. Build `nonblocking_gap_candidate_ref` for `proceed_with_assumption`,
   `soft_quality_gap`, `observability_backlog`, or `evidence_tail`, naming the
   assumption, soft ledger, observability backlog, or tail evidence follow-up
   while preserving forbidden readiness claims.
5. Build `claim_boundary_ref`: forbidden claims such as owner receipt closure,
   paper progress, publication ready, submission ready, live runtime ready,
   production ready, or provider running.
6. Produce `route_back_candidate` when the evidence refs are insufficient to
   classify, the owner surface is unclear, or the candidate would materialize a
   typed blocker for a nonblocking gap class.

## Handoff Shape

Return:

- `evidence_gap_inventory_ref`
- `evidence_gap_decision_candidate_ref`
- `hard_gate_candidate_ref`
- `nonblocking_gap_candidate_ref`
- `claim_boundary_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn evidence-gap triage into a typed blocker, owner receipt, paper
progress claim, quality verdict, current package authority, or readiness claim.
