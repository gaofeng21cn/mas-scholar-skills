# MAS Scholar Skills Capability Modules

Owner: `One Person Lab`
Purpose: Explain the external capability-pack descriptor, active professional skills, and generic OPL consumption boundary.
State: `active_structural_baseline`
Machine boundary: This is human-readable navigation. Module truth, exposure policy, and false-authority flags live in `contracts/scholar-skills-capability-modules.json`; source truth for the professional playbooks lives in the corresponding `skills/medical-*/SKILL.md`; plugin discovery truth lives in `.codex-plugin/plugin.json`.

## Positioning

`MAS Scholar Skills` is the external enhancement pack for MAS medical-paper
capabilities. It is not an OPL runtime base, an additional brand module, or a MAS
domain-truth owner. It supplies professional Codex skills, source packs, quality
floors, candidate-ref vocabulary, and external-learning references.

OPL consumes this repository only as a generic capability pack. Its public
surface validates the descriptor, installs or syncs selected skills, and returns
provenance. It does not execute a medical module, build a module-specific runtime
context, materialize candidate artifacts, or issue execution receipts. Stage
policy, domain actions, candidate acceptance, owner receipts, typed blockers, and
artifact authority remain with MAS or another consuming domain owner.

## Active Catalog

The canonical catalog contains eight active module ids. Each is backed by one or
more real, syncable professional Codex skills.

| Module | Professional Skill Source | Output Boundary |
| --- | --- | --- |
| `mas-scholar-skills.display` | `medical-figure-design`, `medical-figure-style`, `medical-figure-composer` | Candidate display refs and route-back hints only |
| `mas-scholar-skills.tables` | `medical-table-design` | Candidate table refs and route-back hints only |
| `mas-scholar-skills.stats` | `medical-statistical-review` | Candidate analysis-review refs only |
| `mas-scholar-skills.lit` | `medical-research-lit` | Candidate source-screening and claim-support refs only |
| `mas-scholar-skills.write` | `medical-manuscript-writing` | Candidate writing and claim-evidence refs only |
| `mas-scholar-skills.review` | `medical-manuscript-review` | Candidate review and repair-route refs only |
| `mas-scholar-skills.submit` | `medical-submission-prep` | Candidate submission-preparation refs only |
| `mas-scholar-skills.data` | `medical-data-governance` | Candidate data-governance refs only |

Historical `opl.scholarskills.*` module ids are provenance aliases only. The
historical aggregate name is likewise not a discoverable skill surface.

Every active module uses the same handoff: `source_pack_ref`, `candidate_refs`,
and `owner_gate_handoff_ref`. The contract can describe ids, mappings, ref
families, sync policy, and no-authority flags. It cannot replace a professional
skill, stage prompt, owner gate, or domain action.

## Provider Boundary

`medical-research-lit` owns literature strategy, screening, support assessment,
and route-back recommendations. MAS owns biomedical provider lookup and
normalization through `research-integrity-reference-verification`; its read-only
outputs are `mas_provider_lookup_ref` and `pubmed_source_refs`. When a concrete
fallback is necessary, OPL Connect may supply Crossref/OpenAlex metadata,
coverage, or citation-graph inputs as `fallback_source_refs`. None of these refs
is citation acceptance, a literature verdict, or a publication decision.

## Generic OPL Readback

```bash
opl connect skills --domain mas-scholar-skills --json
opl connect sync-skills --domain mas-scholar-skills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain mas-scholar-skills --scope quest --target-quest <quest_root> --json
```

The descriptor readback reports package identity, discovery sources, sync
eligibility, provenance, and false-authority state. Sync copies only selected
Codex discovery material. It does not make the pack a default stage entry, write
MAS files, or make any readiness claim.

## Data-Governance Retention Vocabulary

The `data` module keeps the following refs as candidate vocabulary; the owner
still decides all lifecycle actions:

- `data_asset_manifest_ref`, `lifecycle_classification_ref`, `important_result_reproduction_ref`, `data_body_boundary_ref`, and `lifecycle_catalog_ref`.
- `owner_decision_ref`, `study_impact_ref`, `prune_dry_run_ref`, and `post_cleanup_readback_ref`.
- `hot_current_body`, `warm_parent_or_provenance`, `paper_facing_current`, `active_runtime`, `semantic_closed`, `byte_closed`, `delete_safe_cache`, and `retired_tombstone`.

## Gallery And Change Policy

`gallery/medical-display/` is a compact human-review package. Its files can
anchor a template or visual-audit reference, but do not prove a live renderer,
visual parity, paper readiness, or owner acceptance.

Add or change a module only when the module id, specialist mapping, ref
vocabulary, exposure policy, or no-authority boundary changes. Improve medical
judgment in the relevant `medical-*` skill, update stage semantics in MAS, and
change generic package behavior in OPL. This division avoids recreating a second
module runtime or a second medical catalog in the framework.
