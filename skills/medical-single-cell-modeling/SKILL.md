---
name: medical-single-cell-modeling
description: "Use when MAS needs a refs-only single-cell modeling specialist playbook inspired by AcademicForge scgpt and scvi-tools. It prepares AnnData embedding, annotation, batch/model diagnostic, differential-expression candidate refs, and owner-gate handoff only; it cannot write domain truth, sign owner receipts, create typed blockers, or claim publication readiness."
---

# Medical Single-Cell Modeling

Use this optional MAS Scholar Skills specialist when a task needs single-cell
embedding, annotation, batch integration, perturbation interpretation, or
differential-expression candidate evidence. It adapts AcademicForge HEAD
`54a2f333973147a1fd703caea6f12252e1f227d6` patterns from `scgpt` and
`scvi-tools`.

This skill is refs-only and no-authority. It can prepare AnnData embedding refs,
annotation refs, DE candidate refs, model/env/receipt refs, and
`owner_gate_handoff_ref`; it cannot write MAS study truth, mutate clinical data,
sign owner receipt, create typed blocker, claim source readiness, or claim
publication readiness.

Optional skill-local helper: use `kernel.py` for deterministic AnnData key
sanitizing, obs metadata summaries, metadata schema scaffolds, and
batch/label-key diagnostics. It is a no-authority scaffold/diagnostic helper
only; the consuming workspace or compute owner still owns data truth, execution,
model outputs, owner receipts, typed blockers, and readiness labels.

## Workflow

1. Define the single-cell question: annotation, batch correction, latent
   embedding, perturbation response, marker review, or differential expression.
2. Record `anndata_input_ref`, `gene_vocab_ref`, `metadata_schema_ref`,
   `batch_key_ref`, `label_key_ref`, and `model_selection_ref`.
3. Use `scgpt`-style routing for foundation-model embeddings, annotation, and
   perturbation-style diagnostics; use `scvi-tools`-style routing for latent
   variable modeling, integration, and differential-expression candidates.
4. Route execution through the approved compute owner. This skill owns evidence
   framing and diagnostic interpretation, not compute substrate or data truth.
5. Validate candidate outputs with input schema, cell/gene counts, label
   provenance, batch behavior, marker plausibility, and route-back notes.

## Handoff Shape

Return:

- `single_cell_question`
- `anndata_input_ref`
- `metadata_schema_ref`
- `embedding_candidate_ref`
- `annotation_candidate_ref`
- `differential_expression_candidate_ref`
- `batch_diagnostic_ref`
- `model_checkpoint_ref`
- `environment_receipt_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not promote an embedding, annotation, marker list, or DE candidate to clinical
truth, source readiness, owner acceptance, typed blocker, or publication
readiness.
