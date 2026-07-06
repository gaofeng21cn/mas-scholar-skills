---
name: medical-protein-design
description: "Use when MAS needs a refs-only protein design specialist playbook inspired by AcademicForge proteinmpnn, ligandmpnn, solublempnn, and fair-esm2. It prepares sequence/design/embedding/fold-back validation refs and owner-gate handoff only; it cannot write domain truth, sign owner receipts, create typed blockers, or claim publication readiness."
---

# Medical Protein Design

Use this optional MAS Scholar Skills specialist when a task needs binder,
enzyme, interface, ligand-aware, or solubility-oriented sequence design
guidance. It adapts AcademicForge HEAD
`54a2f333973147a1fd703caea6f12252e1f227d6` patterns from `proteinmpnn`,
`ligandmpnn`, `solublempnn`, and `fair-esm2`.

This skill is refs-only and no-authority. It can prepare sequence candidates,
design rationale refs, embedding refs, fold-back validation refs, deterministic
receipt refs, and `owner_gate_handoff_ref`; it cannot write MAS study truth,
mutate artifacts, sign owner receipt, create typed blocker, claim quality
verdict, or claim publication readiness.

## Workflow

1. Define the design target: fixed-backbone sequence recovery, interface
   redesign, ligand-aware pocket design, solubility rescue, mutation scoring, or
   embedding comparison.
2. Record `design_target_ref`, `backbone_or_complex_ref`, `fixed_position_ref`,
   `ligand_context_ref`, and `constraint_ref`.
3. Select the smallest design route:
   - `proteinmpnn` for fixed-backbone and interface sequence design.
   - `ligandmpnn` for ligand-aware pocket or small-molecule context.
   - `solublempnn` for solubility-oriented sequence candidates.
   - `fair-esm2` for embeddings, mutation scoring, sequence distance, and
     language-model plausibility checks.
4. Route execution through the approved compute owner when needed; this skill
   owns the AI playbook and deterministic refs, not the substrate.
5. Validate candidate sequences with fold-back or structure-consistency refs,
   sequence diversity checks, constraint checks, and route-back notes for
   missing inputs.

## Handoff Shape

Return:

- `design_question`
- `design_target_ref`
- `backbone_or_complex_ref`
- `constraint_ref`
- `sequence_candidate_refs`
- `design_score_ref`
- `embedding_ref`
- `fold_back_validation_ref`
- `environment_receipt_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not present a designed sequence, model score, embedding cluster, or fold-back
pass as experimental evidence, domain truth, owner acceptance, typed blocker, or
publication readiness.
