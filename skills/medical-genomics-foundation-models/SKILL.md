---
name: medical-genomics-foundation-models
description: "Use when MAS needs a refs-only genomics foundation-model specialist playbook inspired by AcademicForge borzoi and evo2. It prepares DNA scoring, variant-effect, track-prediction, model/env/receipt refs, and owner-gate handoff only; it cannot write domain truth, sign owner receipts, create typed blockers, or claim publication readiness."
---

# Medical Genomics Foundation Models

Use this optional MAS Scholar Skills specialist when a task needs DNA sequence
scoring, variant-effect triage, regulatory track prediction, or genomic
foundation-model evidence organization. It adapts AcademicForge HEAD
`54a2f333973147a1fd703caea6f12252e1f227d6` patterns from `borzoi` and `evo2`.

This skill is refs-only and no-authority. It can prepare DNA scoring candidate
refs, track prediction refs, model/env/receipt refs, and `owner_gate_handoff_ref`;
it cannot write MAS study truth, mutate clinical data, sign owner receipt,
create typed blocker, claim source readiness, or claim publication readiness.

Optional deterministic helper: `kernel.py` provides interval normalization,
genomics handoff shells, variant candidate shells, and authority/source lints.

## Workflow

1. Define the genomics question: variant effect, promoter/enhancer track,
   sequence perturbation, regulatory annotation, or long-context sequence
   comparison.
2. Record `genomic_interval_ref`, `reference_genome_ref`,
   `variant_or_sequence_ref`, `track_target_ref`, and `model_selection_ref`.
3. Use `borzoi`-style routing for sequence-to-track or regulatory effect
   prediction; use `evo2`-style routing for long-context DNA scoring and
   sequence perturbation.
4. Keep execution under the approved compute/connect owner. This skill owns
   question framing, evidence packaging, and diagnostic playbook only.
5. Return candidate refs with model, checkpoint, context length, genome build,
   interval, variant, and track provenance.

## Handoff Shape

Return:

- `genomics_question`
- `genomic_interval_ref`
- `reference_genome_ref`
- `variant_or_sequence_ref`
- `dna_scoring_candidate_ref`
- `track_prediction_candidate_ref`
- `model_checkpoint_ref`
- `environment_receipt_ref`
- `limitations_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not turn model-predicted variant effects or track changes into clinical
interpretation, data truth, owner acceptance, typed blocker, or publication
readiness.
