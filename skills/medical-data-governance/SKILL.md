---
name: medical-data-governance
description: "Use when a MAS medical-paper task needs clinical cohort data governance, data asset manifest review, data dictionary and codebook review, cleaning or normalization readiness, data version-diff impact review, study data binding review, privacy/access tier review, retention/lifecycle guardrail review, or refs-only source-readiness route-back. This professional specialist skill is maintained in mas-scholar-skills; MAS keeps clinical data body authority, source readiness verdicts, study truth, irreversible data mutation authorization, owner receipts, typed blockers, human gates, and publication readiness."
---

# Medical Data Governance

Use this skill when MAS needs a professional review of clinical cohort data
before analysis, writing, table/figure design, review, submission, or data
lifecycle closeout.

This professional specialist skill is maintained in `mas-scholar-skills` /
MAS Scholar Skills. MAS stage operating prompts may sync and consume it, while
MAS still owns study truth, clinical source readiness, cohort acceptance, data
body mutation, owner receipts, typed blockers, human gates, current packages,
and publication readiness.

Sibling skill routes are `medical-statistical-review` for estimand,
denominator, missingness, and analysis-plan judgment; `medical-table-design` for
table shells and data-dictionary tables; `medical-figure-design` for data-bound
figures; `medical-manuscript-writing` for data availability and methods prose;
`medical-manuscript-review` for independent source/claim critique; and
`medical-submission-prep` for repository, data/code availability, and
declaration handoff.

## Core Rule

Clinical data governance is a source-readiness and lifecycle discipline. A good
handoff tells MAS what the dataset is, where it lives, which layer is
authoritative, how variables were cleaned or normalized, which version changed,
which study can use it, what privacy/access tier applies, and which owner gate
must accept or reject it.

Do not treat a CSV, SQLite, DuckDB, Parquet, notebook output, registry index, or
cleaned extract as clinical data truth unless the MAS data asset manifest and
owner surface identify it as the authoritative body or an accepted derived
asset.

## OPL Base Lifecycle Fit

Use OPL base lifecycle primitives as locator, index, projection, and receipt
transport only:

- workspace/source locator refs;
- memory/data-asset registry refs;
- artifact lifecycle refs;
- retention, restore, tombstone, and provenance refs;
- refs-only ledger or owner-gate handoff refs.

OPL does not own clinical data bodies, clinical semantic mapping, source
readiness verdicts, data-cleaning acceptance, or irreversible physical delete.
Those decisions stay with MAS or the downstream domain owner.

## MAS Data Planes

When reviewing a MAS workspace, preserve this physical split:

- Data body plane: `data/datasets/<layer>/<version>/`.
- Registry/read-model plane: `memory/portfolio/data_assets/`.
- Study binding plane: `studies/<study-id>/study.yaml` or
  `studies/<study-id>/data_input/dataset_manifest.yaml`.
- Stage output plane:
  `artifacts/stage_outputs/03-data_asset_and_cohort_build/`.

Expected dataset layers are:

- `restricted_raw`
- `deidentified_linkage`
- `master`
- `deidentified_longitudinal`
- `standardized_longitudinal`
- `external`

Do not move data between these layers from this skill. Review the manifest,
dictionary, lineage, and owner-gate requirements, then route MAS to the legal
controller entry.

## MAS Controller Entries

Use MAS controller commands as the authority path when the workspace provides
them:

```bash
medautosci data-assets-status --workspace-root <workspace_root>
medautosci init-data-assets --workspace-root <workspace_root>
medautosci assess-data-asset-impact --workspace-root <workspace_root>
medautosci data-asset-manifest-refs-rebuild --workspace-root <workspace_root>
medautosci apply-data-asset-update --workspace-root <workspace_root> --payload-file <path>
medautosci data-lifecycle inspect --workspace-root <workspace_root>
medautosci data-lifecycle index-assets --workspace-root <workspace_root> --dry-run
```

Prefer read-only or dry-run commands unless the user, MAS owner surface, or
project-specific runbook explicitly authorizes an apply command. Even then,
report the command as an authority route; do not hand-edit registry files or data
bodies from this skill.

## Workflow

1. Identify the workspace root, study id, requested analysis stage, and current
   data owner question.
2. Read existing data asset manifests, dataset manifests, dictionaries,
   codebooks, lineage refs, source readiness receipts, and data lifecycle
   readbacks.
3. Classify every referenced body or copy as authoritative body, accepted
   derived asset, study-local extract, interchange file, working index, runtime
   cache, report output, or tombstone candidate.
4. Check layer and version discipline: source layer, version id, checksum or
   fingerprint, provenance, data dictionary, cleaning/normalization notes,
   derived-variable definitions, privacy tier, and access tier.
5. Review study binding: inclusion/exclusion cohort lock, endpoint/outcome
   definitions, variable ascertainment, analysis window, missingness scope,
   denominator availability, and source readiness receipt refs.
6. Compare version changes when an update is proposed. Flag impact on cohorts,
   denominators, derived variables, statistical analysis, tables, figures,
   manuscript claims, and submission data/code availability.
7. Produce a refs-only governance handoff with missing inputs, safe next command,
   owner gate target, and route-back recommendation.

## Quality Checks

Check:

- every dataset body has a declared layer, version, owner, and manifest ref;
- data dictionary/codebook covers variables used by the study;
- cleaning and normalization steps are tied to source refs or receipt refs;
- derived variables are defined separately from raw source fields;
- missingness, denominator, date window, unit conversion, and coding-system
  assumptions are visible;
- source readiness receipts exist before downstream manuscript claims rely on
  the data;
- study-local extracts do not become a second truth source;
- privacy/access tier and retention guardrails are explicit;
- storage placement is classified as hot, warm, cold, external, or delete-safe
  cache with a reason;
- any proposed delete, compaction, migration, or archive action has owner
  decision, restore proof, and post-cleanup readback refs.

## Handoff Shape

Return refs-only candidate output:

- `data_asset_manifest_ref`
- `dataset_manifest_ref`
- `data_dictionary_ref`
- `codebook_ref`
- `cleaning_normalization_readiness_ref`
- `derived_variable_registry_ref`
- `source_lineage_ref`
- `source_readiness_receipt_ref`
- `cohort_definition_lock_ref`
- `version_diff_impact_ref`
- `study_binding_ref`
- `privacy_access_tier_ref`
- `retention_guardrail_ref`
- `storage_tier_ref`
- `lifecycle_catalog_ref`
- `owner_decision_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

If the task involves clinical data closeout, also include:

- `important_result_reproduction_ref`
- `data_body_boundary_ref`
- `study_impact_ref`
- `prune_dry_run_ref`
- `post_cleanup_readback_ref`
- `cold_restore_proof_ref`

## MAS Boundary

This skill can prepare candidate manifests, review notes, impact summaries,
route-back refs, and safe command recommendations. It must not directly edit
`memory/portfolio/data_assets/**`, sign source readiness, mutate
`data/datasets/**`, create owner receipts, create typed blockers, write human
gates, alter current packages, or claim data/source/publication readiness.

Do not claim cohort acceptance, source readiness, data truth, artifact
authority, owner acceptance, submission readiness, or publication readiness. MAS
or the domain owner must consume the refs and issue any owner receipt, typed
blocker, route-back, data mutation, or publication decision.
