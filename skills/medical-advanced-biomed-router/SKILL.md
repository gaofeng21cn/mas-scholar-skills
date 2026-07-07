---
name: medical-advanced-biomed-router
description: "Use when MAS needs refs-only routing for advanced biomedical specialties such as structural biology, protein design, genomics foundation models, single-cell modeling, indication dossiers, scientific compute, or AcademicForge-inspired external specialist playbooks. OPL Runway/Connect/Fabric or the consuming workspace owns execution substrate; this optional router does not write domain truth, sign owner receipts, create typed blockers, or claim publication readiness."
---

# Medical Advanced Biomed Router

Use this optional MAS Scholar Skills router when a named advanced biomedical
task needs routing before any external specialist or compute substrate is used.

This skill is refs-only and no-authority. It can prepare advanced biomedical
route refs, execution-intent refs, deterministic receipt refs, and
`owner_gate_handoff_ref`; it cannot write domain truth, mutate artifacts, sign
an owner receipt, create a typed blocker, claim a quality verdict, or claim
publication, runtime, production, or current-package readiness.

The router preserves the AcademicForge source anchor
`54a2f333973147a1fd703caea6f12252e1f227d6`, but does not install or run those
external runtimes. OPL Runway, Connect, Fabric, managed endpoints, or the
consuming workspace compute owner owns substrate, credentials, queues,
endpoints, harvest, and provider errors.

Legacy upstream route tokens include `alphafold2`, `proteinmpnn`, `borzoi`,
`scgpt`, `indication-dossier`, and `compute-env-setup`.

## Routes

- Structure/docking: `structure_candidate_ref`, `docking_candidate_ref`,
  `confidence_metrics_ref`.
- Protein design: `sequence_candidate_refs`, `embedding_ref`,
  `fold_back_validation_ref`.
- Genomics/single-cell: `dna_scoring_candidate_ref`,
  `track_prediction_candidate_ref`, `annotation_candidate_ref`,
  `differential_expression_candidate_ref`.
- Indication/compute: `patient_population_waypoint_ref`,
  `synthesis_candidate_ref`, `compute_requirement_ref`,
  `environment_probe_ref`, `deterministic_receipt_ref`.

## Workflow

1. Build `advanced_biomed_question_ref`: scientific specialty, inputs,
   expected outputs, privacy boundary, and owner-approved compute route.
2. Build `advanced_biomed_route_ref`: selected specialty family, upstream
   pattern refs, minimal execution need, and fallback if execution is not
   authorized.
3. Build `execution_intent_ref`: environment, provider, endpoint, job plan, and
   credential boundary when execution is required.
4. Build `candidate_result_ref`: candidate refs, warnings, limitations, and
   source/compute receipts available for owner review.
5. Produce `route_back_candidate` when owner approval, input provenance,
   credential, provider setup, hardware, or domain interpretation is missing.

## Handoff Shape

Return:

- `advanced_biomed_question_ref`
- `advanced_biomed_route_ref`
- `execution_intent_ref`
- `candidate_result_ref`
- `deterministic_receipt_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not treat a model output, endpoint response, harvested file, or clean helper
receipt as MAS runtime readiness, domain truth, owner acceptance, typed blocker,
quality verdict, or publication readiness.
