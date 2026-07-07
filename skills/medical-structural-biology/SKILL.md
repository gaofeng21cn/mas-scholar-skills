---
name: medical-structural-biology
description: "Use when MAS needs a refs-only structural biology specialist playbook for protein structure, complex co-folding, confidence review, and docking candidate refs inspired by AcademicForge alphafold2, openfold3, boltz, chai1, esmfold2, and diffdock. This optional external specialist skill prepares structure/docking candidate refs, model/env/receipt refs, and owner-gate handoff only; it cannot write domain truth, sign owner receipts, create typed blockers, or claim publication readiness."
---

# Medical Structural Biology

Use this optional MAS Scholar Skills specialist when a MAS task needs structure
prediction, protein/ligand co-folding, interface confidence review, or docking
triage. It adapts AcademicForge HEAD
`54a2f333973147a1fd703caea6f12252e1f227d6` patterns from `alphafold2`,
`openfold3`, `boltz`, `chai1`, `esmfold2`, and `diffdock`.

This skill is refs-only and no-authority. It can prepare candidate refs,
diagnostic notes, deterministic receipt refs, and `owner_gate_handoff_ref`; it
cannot write MAS study truth, mutate artifacts, sign owner receipt, create typed
blocker, claim quality verdict, or claim publication readiness.

Optional deterministic helper: `kernel.py` provides sequence hygiene, structure
candidate shells, confidence summaries, manifest shells, and authority lints.

## Workflow

1. Define the structural question: monomer fold, multimer interface,
   protein-ligand complex, antibody-antigen model, design fold-back check, or
   docking triage.
2. Record input provenance as `sequence_input_ref`, `ligand_input_ref`,
   `template_or_msa_ref`, and `model_selection_ref`.
3. Pick the smallest model route that answers the question:
   - `alphafold2` for MSA-backed monomer or multimer checks.
   - `openfold3`, `boltz`, or `chai1` for protein, nucleic-acid, and ligand
     co-folding.
   - `esmfold2` for single-sequence or ESM embedding-backed fold checks.
   - `diffdock` for docking candidate triage after receptor/ligand readiness.
4. If execution is required, route compute and model substrate through OPL
   Runway, Connect, Fabric, managed endpoints, or the consuming workspace's
   approved compute owner. This skill owns the AI diagnostic playbook only.
5. Review confidence and failure evidence: pLDDT, pTM/ipTM, PAE, clash or
   confidence JSON, affinity/docking score, pose consistency, and input
   readiness warnings.
6. Produce structure/docking candidate refs and a route-back note when evidence
   is insufficient.

## Handoff Shape

Return a compact refs-only handoff:

- `structural_question`
- `sequence_input_ref`
- `ligand_input_ref`
- `model_selection_ref`
- `environment_receipt_ref`
- `structure_candidate_ref`
- `docking_candidate_ref`
- `confidence_metrics_ref`
- `model_output_manifest_ref`
- `failure_or_warning_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn a predicted model, docking pose, confidence threshold, or clean
environment receipt into MAS artifact authority, clinical interpretation, owner
acceptance, typed blocker, or publication readiness.
