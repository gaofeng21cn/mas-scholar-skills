# Legacy MAS Data Workspace

Applies only to a confirmed historical workspace that still provides the `medautosci` data controller commands below. These are not current MAS public actions. Check local version/help and the owner runbook first; retain all existing data permissions. Do not apply this layout or checklist to a current hosted MAS study.

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

## Yang/MAS Data Compliance Checklist

For Yang/MAS workspaces, include this concise checklist before recommending
analysis, cleanup, archival, or owner-gate handoff:

- `project_data_plan.yaml` exists or its absence is routed back as the data plan
  gap.
- `memory/portfolio/data_assets/index.sqlite`, `runtime/index.sqlite`, and
  `studies/index.sqlite` are read as indices/read models, not data body truth.
- `medautosci data-lifecycle inspect --workspace-root <workspace_root>` has a
  fresh readback or a named reason it cannot run.
- ScholarSkills install receipt identifies the synced `mas-scholar-skills` and
  `medical-data-governance` skill sources used for the review.
- Stale legacy skill detector confirms old `opl-scholarskills` or
  `opl.scholarskills.*` projections are legacy aliases/provenance only.
- Cleanup candidates stay behind an owner-review boundary: produce
  `prune_dry_run_ref`, `owner_decision_ref`, and `post_cleanup_readback_ref`;
  do not delete, thin, move, or compact clinical data bodies from this skill.
- Source readiness and owner gate refs are explicit before downstream manuscript,
  analysis, table, figure, submission, or lifecycle claims rely on the data.

