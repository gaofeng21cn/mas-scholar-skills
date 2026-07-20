# MAS Scholar Skills Capability Modules

Owner: `One Person Lab`
Purpose: Explain the external capability-pack descriptor, active professional skills, and generic OPL consumption boundary.
State: `active_structural_baseline`
Machine boundary: This is human-readable navigation. Module truth, exposure policy, and false-authority flags live in `contracts/scholar-skills-capability-modules.json`; source truth for the professional playbooks lives in the corresponding `skills/medical-*/SKILL.md`; plugin discovery truth lives in `.codex-plugin/plugin.json`.

## Positioning

`MAS Scholar Skills` is the required capability package for MAS medical-paper
capabilities. Its external repository is a maintenance boundary, not an optional
product boundary. It is not an OPL runtime base, an additional brand module, or a MAS
domain-truth owner. It supplies professional Codex skills, source packs, quality
floors, candidate-ref vocabulary, and external-learning references.

OPL consumes this repository as a generic capability pack. Its public surface
validates the descriptor, installs or syncs selected skills, and returns
provenance. OPL Connect may also load the package's two read-only provider
companion modules: one verifies a known reference, while the other searches
Crossref or OpenAlex for candidate references. Connect executes HTTP, retry,
cache, strict matching where applicable, and receipt materialization; the package
code only builds bounded request descriptions and parses supplied response bytes.
It does not execute a medical stage, materialize
candidate artifacts, or issue verdicts or receipts. Stage policy, domain actions,
candidate acceptance, owner receipts, typed blockers, and artifact authority
remain with MAS or another consuming domain owner.

## Active Catalog

The canonical catalog contains eight professional module ids backed by real,
syncable Codex skills, plus two read-only runtime adapter modules.

| Module | Professional Skill Source | Output Boundary |
| --- | --- | --- |
| `mas-scholar-skills.display` | `medical-figure-design`, `medical-figure-style`, `medical-figure-composer` | Candidate display refs and route-back hints only |
| `mas-scholar-skills.tables` | `medical-table-design` | Candidate table refs and route-back hints only |
| `mas-scholar-skills.stats` | `medical-statistical-review` | Candidate analysis-review refs only |
| `mas-scholar-skills.lit` | `medical-research-lit` | Candidate source-screening and claim-support refs only |
| `mas-scholar-skills.write` | `medical-manuscript-writing` | Candidate writing and claim-evidence refs only |
| `mas-scholar-skills.review` | `medical-manuscript-review` | Candidate review and repair-route refs only |
| `mas-scholar-skills.submit` | `medical-submission-prep` | Candidate submission-preparation and offline publication-layout selection refs only |
| `mas-scholar-skills.data` | `medical-data-governance` | Candidate data-governance refs only |
| `mas-scholar-skills.reference-provider-adapters` | No Skill entry; package runtime binding | Pure request/response normalization for OPL Connect; no I/O, verdict, or receipt authority |
| `mas-scholar-skills.scientific-search-adapters` | No Skill entry; package runtime binding | One-step Crossref/OpenAlex candidate search normalization; no I/O, acceptance, verdict, or receipt authority |

Historical `opl.scholarskills.*` module ids are provenance aliases only. The
historical aggregate name is likewise not a discoverable skill surface.

The eight professional modules use the same handoff: `source_pack_ref`,
`candidate_refs`, and `owner_gate_handoff_ref`. Reference verification uses the
`build_request -> parse_response -> next_step` ABI and returns normalized metadata
evidence. Scientific search uses the independent
`build_search_request -> parse_search_response` ABI and returns `candidates[]`.
Neither companion path can replace a professional skill, stage prompt, owner gate,
or domain action.

## Publication Layout Profiles

Scholar Submit owns one local publication-layout catalog. With a named journal it
selects a matching adaptation profile; without one it selects
`general-medical-reader.v1`. The initial journal set covers JAMA Network, NEJM,
The Lancet, The BMJ, Nature Medicine, Diabetes Care, Cardiovascular Diabetology,
BMC Medicine, and the shared Frontiers journal family. Any `Frontiers in ...`
journal resolves to one family profile instead of requiring per-journal copies.
The profiles keep stable authoring and package conventions available offline,
while formal submission still refreshes changing requirements from each
profile's official source.

The catalog always returns `paper.pdf` and
`paper_with_supplementary.pdf`. The latter is a combined reading copy; separately
addressable supplementary members remain available for journal packaging. These
assets and refs are quality guidance, not publisher-owned templates, journal
compliance, submission readiness, or authority.

## Provider Boundary

`medical-research-lit` owns literature strategy, screening, support assessment,
and route-back recommendations. This package owns the pure provider-specific
mapping for reference verification across Crossref, OpenAlex, PubMed eSummary,
Europe PMC, Semantic Scholar, Crossmark, and DOI landing metadata, plus independent
Crossref/OpenAlex multi-candidate search mapping. OPL Connect owns network
execution, retry, cache, strict comparison, normalized receipts, and connector
errors. MAS owns candidate acceptance, citation acceptance, and manuscript use.
Provider evidence and search candidates are never literature verdicts or
publication decisions.

## OPL Package Readback

```bash
opl packages status --package-id mas --scope workspace --target-workspace <workspace_root> --json
opl packages repair --package-id mas --scope workspace --target-workspace <workspace_root> --json
```

The package is installed, updated, locked, and rolled back as part of the MAS
dependency closure. Missing or incompatible core exports make MAS
`operational_ready=false`; OPL must not silently continue with a reduced product.
Optional named-specialty Skills remain outside this readiness floor.

Provider-source development may additionally use the internal discovery surfaces:

```bash
opl connect skills --domain mas-scholar-skills --json
opl connect sync-skills --domain mas-scholar-skills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain mas-scholar-skills --scope quest --target-quest <quest_root> --json
```

The internal descriptor readback reports package identity, discovery sources, sync
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
