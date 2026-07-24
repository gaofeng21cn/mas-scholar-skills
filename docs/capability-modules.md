# MAS Scholar Skills Capability Modules

Owner: `One Person Lab`
Purpose: Explain the external capability-pack descriptor, active professional skills, and generic OPL consumption boundary.
State: `active_structural_baseline`
Machine boundary: This is human-readable navigation. Module truth, exposure policy, and false-authority flags live in `contracts/scholar-skills-capability-modules.json`; source truth for the professional playbooks lives in the corresponding `skills/medical-*/SKILL.md`; plugin discovery truth lives in `.codex-plugin/plugin.json`.

## Positioning

`MAS Scholar Skills` is a consumer-neutral framework capability provider. Its
external repository is a maintenance boundary. It is not an OPL runtime base,
an additional brand module, or a MAS/MAG domain-truth owner. It supplies
professional Codex skills, source packs, quality floors, candidate-ref
vocabulary, and external-learning references through required MAS paper and MAG
grant Package dependency profiles. Individual named specialty Skills remain
task-selected; that exposure choice does not make the whole Package optional.

OPL consumes this repository as a generic capability pack. Its public surface
validates the descriptor, distributes or syncs selected skills, and returns
provenance. OPL Connect may also load the package's two read-only provider
companion modules: one verifies a known reference, while the other searches
Crossref or OpenAlex for generic metadata, coverage, or citation-graph fallback
candidates. Framework-owned OPL Connect provides primary PubMed/PMC discovery;
the package search adapter explicitly excludes those providers. Connect executes
HTTP, retry, cache, strict matching where applicable, and receipt materialization;
the package code only builds bounded request descriptions and parses supplied response bytes.
It does not execute a medical stage, materialize
candidate artifacts, or issue verdicts or receipts. Stage policy, domain actions,
candidate acceptance, owner receipts, typed blockers, and artifact authority
remain with MAS or another consuming domain owner.

## Consumer Profiles

The accepted target treats `mas-medical-paper.v1` and
`mag-medical-grant.v1` as required Package presence/callability profiles. The
current manifest still records `required=false` and
`dependency_kind=optional_enhancement`; this is migration truth and must not be
read as the long-term rule. MAS lists an 11-Skill capability set;
MAG lists six Skills for literature, statistics, methodology, evidence
integrity, claim mapping, and reference integrity. In both profiles,
`required_export_ids` and `required_module_ids` identify the capability set each
consumer requires to be callable. They do not impose provider-version equality
or make unrelated Packages part of the same readiness gate.

Missing Package identity or required capability callability blocks only the
affected MAS or MAG consumer and routes to managed install/repair. It does not
block unrelated Packages, compare provider versions/ABIs, or require a lock,
payload, digest, Release Set, or atomic closure. The dependency grants no truth,
fundability, quality/export, strategy-memory, receipt, blocker, publication, or
owner authority to ScholarSkills.

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
| `mas-scholar-skills.scientific-search-adapters` | No Skill entry; package runtime binding | One-step Crossref/OpenAlex generic fallback search normalization; explicitly excludes PubMed/PMC and has no I/O, acceptance, verdict, or receipt authority |

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
Crossref/OpenAlex fallback search mapping. Framework-owned OPL Connect implements
PubMed/PMC discovery and owns all network execution, retry, cache, strict
comparison, normalized receipts, and connector errors. MAS or MAG owns candidate
acceptance, citation acceptance, and domain use.
Provider evidence and search candidates are never literature verdicts or
publication decisions.

## Distribution Readback

```bash
opl packages status --package-id mas --scope workspace --target-workspace <workspace_root> --json
```

MAS and MAG may currently list this package under
`bundled_capability_package_ids` so exports are available for native discovery.
That is a compatibility carrier projection, not the target dependency model or
complete installed truth. The provider owns no consumer status, repair,
activation, admission, route, launch, or readiness authority; the
consumer/platform reports a missing presence/callability edge and blocks only
that consumer.

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
