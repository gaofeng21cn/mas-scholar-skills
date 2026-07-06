# MAS Scholar Skills Operating Model

Owner: `One Person Lab`
Purpose: Explain how `mas-scholar-skills` operates as the MAS Scholar Skills professional-skill enhancement pack without becoming MAS domain truth.
State: `active_operating_model`
Machine boundary: Human-readable operating model. Machine truth stays in `contracts/scholar-skills-capability-modules.json`, `skills/mas-scholar-skills/SKILL.md`, `skills/medical-manuscript-writing/SKILL.md`, `skills/medical-manuscript-review/SKILL.md`, `skills/medical-figure-design/SKILL.md`, `skills/medical-figure-style/SKILL.md`, `skills/medical-figure-composer/SKILL.md`, `skills/medical-research-lit/SKILL.md`, `skills/medical-statistical-review/SKILL.md`, `skills/medical-table-design/SKILL.md`, `skills/medical-submission-prep/SKILL.md`, `skills/medical-data-governance/SKILL.md`, pack manifests, OPL Framework readbacks, and consuming MAS owner surfaces.

## Positioning

`MAS Scholar Skills` is the product and repository name for the OPL-owned `mas-scholar-skills` repository. The historical `opl-scholarskills` name remains a compatibility alias. The repository is narrower than a generic OPL scholarly base: it is the external enhancement pack and professional-skill source for MAS medical-paper capabilities.

It owns enhancement surfaces:

- MAS Scholar Skills module contracts and candidate ref families.
- Source packs such as `packs/medical-display-core`.
- Quality floors, route-back hints, and external-learning absorption.
- Compact human-review refs and templates that MAS can discover.
- Syncable medical-paper professional skills where a stable AI workflow should have one maintained source: `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, `medical-figure-style`, `medical-figure-composer`, `medical-research-lit`, `medical-statistical-review`, `medical-table-design`, `medical-submission-prep`, and `medical-data-governance`.

It does not own MAS study truth, publication truth, owner receipts, typed blockers, human gates, runtime queues, provider attempts, ledgers, current-package authority, or publication readiness.

## Capability Module Classification

MAS Scholar Skills has eight active professional skill-backed capability modules, ten default syncable real Codex specialist skills, and optional specialist skills for named advanced scientific or medical-method tasks. `medical-figure-style` and `medical-figure-composer` are display subskills under `medical-figure-design`, not additional active modules.

| Classification | Members | Role |
| --- | --- | --- |
| Active professional modules | `display`, `tables`, `stats`, `lit`, `write`, `review`, `submit`, `data` | Shared module ids, vocabulary, ref families, checklists, candidate handoff, receipt shape, and owner gates, each backed by a real specialist skill. |
| Default real specialist skills | `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, `medical-figure-style`, `medical-figure-composer`, `medical-research-lit`, `medical-statistical-review`, `medical-table-design`, `medical-submission-prep`, `medical-data-governance` | AI-first professional playbooks that Codex can discover and execute after OPL Connect syncs them into a workspace or quest `.codex/skills/` directory. |
| Optional specialist skills | Advanced scientific specialists and medical-method specialists such as `medical-protocol-and-sap-planner`, `medical-cohort-phenotyping`, `medical-evidence-synthesis-and-claim-map`, `medical-reference-integrity-auditor`, `medical-rebuttal-strategy`, `medical-display-qc`, `medical-causal-inference-plan`, `medical-survival-analysis-plan`, `medical-risk-model-transportability-reviewer`, `medical-registry-atlas-story-architect`, `medical-owner-gate-handoff-reviewer`, `medical-display-regression-debugger`, and `medical-data-freeze-and-analysis-readiness-reviewer` | Real Codex discovery skills for named specialty tasks; refs-only/no-authority, not active modules, and not blockers for ordinary MAS progress. |

Generic source or external-learning intake belongs to OPL Framework or MAS stage/source surfaces and is not kept here as a contract placeholder. Omics belongs in this repository only after MAS has a stable real omics specialist workflow to maintain. Active clinical data governance now uses `medical-data-governance`; the legacy data module id remains a descriptor/readback compatibility key.

## Professional Quality Floor

MAS Scholar Skills now applies an explicit quality floor to the real
specialist skills. The floor is adapted from fresh inspection of
`K-Dense-AI/scientific-agent-skills` commit
`1e024ea8547ada12039edbe8197aaa959d97763f` and
`Yuan1z0825/nature-skills` commit
`c91df241a7a963ea151687ac669c5534404f53e5`.

| Skill | Quality floor |
| --- | --- |
| `medical-figure-design` | Figure contract, evidence chain, archetype, renderer decision, schematic/infographic evidence boundary, style brief, candidate set, critic review, style/composition routing, final-scale visual QA, and reviewer packet. |
| `medical-figure-style` | Style-only visual grammar QA, data fidelity, claim-title truth, label economy, color robustness, final-scale preview, and export-visible style route-back. |
| `medical-figure-composer` | Compose-only multi-panel outline, existing panel render receipt review, layout, panel-letter/gutter/resized-text checks, composite review, and export QA. |
| `medical-manuscript-writing` | One-sentence argument, terminology ledger, paragraph job map, section contract, claim-strength calibration, citation integrity, figure/table binding, and data/code availability audit. |
| `medical-manuscript-review` | Shared fact base, technical/significance/reader/validity/scholar-evaluation reviewer lanes, cross-review synthesis, reviewer action matrix, citation repair, revision-delta audit, and route-back closeout. |
| `medical-research-lit` | PubMed/PMC-first source routing, OPL Connect scientific connector ref consumption, query plan, fallback source refs, fallback reasons, deduplication, retain/reject/watchlist screening, source verification, support-strength matrix, claim-support map, and citation integrity floor. |
| `medical-statistical-review` | Statistical question, estimand/target parameter, analysis plan fit, EDA profile, model specification refs, denominator and missingness review, assumption diagnostics, effect-size and uncertainty reporting, multiplicity/sensitivity review, table/figure consistency, and statistical action matrix. |
| `medical-table-design` | Table job, table shell, source-metric binding, denominator checks, statistical display policy, table QC, claim-table alignment, footnote/abbreviation discipline, and journal table contract. |
| `medical-submission-prep` | Journal instruction mapping, reporting guideline checklist, declaration inventory, data/code availability, package consistency, cover-letter or reviewer-response candidates, author-input fields, and submission action matrix. |
| `medical-data-governance` | Data asset manifest, dataset manifest, data dictionary/codebook, cleaning/normalization readiness, source lineage, version-diff impact, study binding, privacy/access tier, lifecycle/retention guardrails, and owner-gate handoff. |

The K-Dense intake is landed into the same skill family: writing gets
outline-to-prose and citation/reporting contracts; review gets critical
validity/bias, scholar-evaluation, and venue-calibration checks; lit gets
retrieval contracts and identifier provenance; display gets plotting/export QA
from scientific visualization, Matplotlib, Seaborn, schematics, and
infographics; stats gets power, MDE, experimental design, exploratory data
analysis, statsmodels-style model specification, and pseudoreplication
discipline; tables get table-vs-figure and statistical-display checks; submit
gets current venue-instruction provenance; data governance gets database
endpoint/filter/count/provenance discipline.

K-Dense also seeds the external scientific Skill router. When MAS needs a
specialized capability outside these default medical-paper skills, Codex should discover and
inspect the external Skill through OPL Connect before any selective sync. The
router is a task-level capability lookup, not a full K-Dense runtime install.

Data availability checks are active through `medical-data-governance`. Omics-specific source routing should stay with the relevant MAS/OPL owner surface until MAS needs Codex to actively run that workflow as a standalone specialist skill.

## Stage / Specialist / Connector / Contract Boundary

The canonical MAS stage source is the MAS domain-agent repository, specifically `agent/stages/` and `agent/prompts/`. MAS overlay Skills, local workspace or quest `.codex/skills/` copies, and synced compatibility entries are Codex projection surfaces. They can expose a stage or specialist skill to a Codex session, but they must not be treated as the source for stage routing, evidence thresholds, owner gates, route-back semantics, owner receipts, typed blockers, human gates, publication readiness, or artifact authority.

Default ownership for a professional specialist skill is the consuming domain-agent repo, close to the stage prompt that calls it. A specialist skill should move to an external pack only when it is heavy, cross-workspace, or independently releasable. MAS Scholar Skills is that external pack for MAS medical writing, review, figure design, literature, statistics, table, submission, Display/source refs, and reusable source packs. The `medical-*` entries in this repository are real Codex specialist skills, not descriptors, routing labels, or script functions. The aggregate `mas-scholar-skills` skill is the entry and discovery layer for the pack; the historical `opl-scholarskills` entry is only a legacy alias.

Tool connectors are the third boundary. OPL Connect/Fabric owns tool or API invocation, normalized read receipts, connector error semantics, cache/retry metadata, no-authority flags, and resource access. For `medical-research-lit`, the OPL Connect scientific connector profile owns PubMed/PMC, Crossref, and OpenAlex provider access, normalized `scientific_connector_source_refs`, `scientific_connector_invocation_refs`, provider-specific source refs such as `pubmed_source_refs`, and read-only receipt candidates. A connector does not own stage policy, professional judgment, source screening, claim-support mapping, route acceptance, owner receipt, typed blocker, human gate, publication readiness, or artifact authority.

Contract modules are the fourth boundary. `contracts/scholar-skills-capability-modules.json` records the module catalog, active ids, ref vocabulary, no-authority flags, and sync policies. A contract module can say that `display` maps to `medical-figure-design` or that `lit` maps to `medical-research-lit`; it cannot perform specialist judgment, replace a `medical-*` Skill, become a stage prompt, call scientific providers, accept a candidate, sign an owner receipt, create a typed blocker, or claim publication readiness.

## MAS Skill Call Path

The MAS overlay skill and MAS stage operating prompts are the primary runtime and stage entries, with source edits made in MAS `agent/stages/` and `agent/prompts/`. They decide stage validity, evidence thresholds, route-back, owner gates, and acceptance. High-frequency paper work should then use MAS-consumed professional skills maintained in this repository:

- `medical-manuscript-writing` for manuscript writing and revision.
- `medical-manuscript-review` for critique, quality-floor review, and route-back.
- `medical-figure-design` for full figure and display work.
- `medical-figure-style` for style-only visual grammar and export-visible QA.
- `medical-figure-composer` for compose-only multi-panel layout and export QA.
- `medical-research-lit` for literature search strategy, source screening, and evidence maps.
- `medical-statistical-review` for statistical assumptions, estimands, effect sizes, and action matrices.
- `medical-table-design` for clinical table shells, table QC, and table-to-claim alignment.
- `medical-submission-prep` for journal instructions, reporting checklists, declarations, reviewer responses, and package consistency.
- `medical-data-governance` for clinical cohort data manifests, source readiness support, version impact, privacy/access tiers, and lifecycle guardrails.

MAS Scholar Skills is called after that routing point as a professional-skill, discovery, and reference layer:

```text
MAS agent/stages or agent/prompts stage prompt
  -> optional MAS overlay or .codex projection for Codex discovery
  -> medical-manuscript-writing / medical-manuscript-review / medical-figure-design
     / medical-figure-style / medical-figure-composer / medical-research-lit
     / medical-statistical-review / medical-table-design / medical-submission-prep
     / medical-data-governance
  -> optional OPL Connect external-skills search / inspect / single-skill sync
  -> MAS Scholar Skills module refs, packs, templates, and quality floors
  -> optional OPL Connect scientific connector readback
  -> refs-only candidate package or route-back hint
  -> MAS owner gate consume / reject / route back
```

If writing, review, figure, literature, statistics, table, submission, or data-governance execution quality is weak, update the corresponding `medical-*` professional skill in this repository and let MAS consume the synced skill. If the problem is stage validity, routing, owner gate, or acceptance semantics, update the MAS stage operating prompt. If the problem is only module vocabulary, ids, ref names, sync policy, or no-authority flags, update the contract module. If the problem is external access or readback, update OPL Connect/Fabric. This keeps stage prompts, professional specialists, tool connectors, and contract modules as separate owners.

Use `medical-research-lit` when the task needs external literature discovery, source screening, PMID/DOI/PMCID verification, fallback-source reasoning, or a claim-support map. Literature discovery is external-resource heavy, so it belongs in MAS Scholar Skills as a real specialist skill while OPL Connect owns provider access and MAS still owns citation acceptance and manuscript use.

The stable default PubMed/PMC execution path uses the unified scientific connector entry:

```bash
opl connect scientific search --provider pubmed --query "<query>" --limit <n> --json
```

`opl connect pubmed search --query "<query>" --limit <n> --json` remains only the PubMed compatibility entry. `medical-research-lit` records returned normalized metadata as `scientific_connector_source_refs` and `pubmed_source_refs`, and connector read receipts as `scientific_connector_invocation_refs` / `pubmed_connector_invocation_ref`. When PubMed/PMC does not cover the task, Crossref and OpenAlex connector refs may be used for metadata, coverage, or citation graph fallback and recorded as `fallback_source_refs`; those refs are not citation acceptance. MAS Scholar Skills owns query strategy, screening, fallback reasons, evidence maps, `claim_support_map_ref`, and route-back handoff. OPL Connect owns the provider calls, source-ref normalization, connector invocation refs, receipt candidates, cache/retry metadata, connector error semantics, and no-authority flags. MAS owns citation judgment, manuscript use, review ledger updates, owner receipts, typed blockers, and publication decisions. This repo does not claim live provider readiness.

When the default medical-paper professional skills do not cover a named external
scientific capability, such as omics, single-cell analysis, Nextflow, RDKit,
PyHealth, or a specialized database/API connector, use OPL Connect as the
Codex discovery chain:

```bash
opl connect external-skills search --query "<scientific need>" --json
opl connect external-skills inspect --skill <skill_id> --json
opl connect external-skills sync --skill <skill_id> --scope workspace --target-workspace <workspace_root> --json
opl connect external-skills sync --skill <skill_id> --scope quest --target-quest <quest_root> --json
```

Search and inspect are read-only. Sync is selective: choose one inspected skill
for the active workspace or quest. Do not install an entire external source by
default, and do not use an external Skill to replace the default `medical-*`
skills, MAS stage policy, owner receipts, typed blockers, current-package
authority, artifact authority, domain truth, or publication readiness.

## Pack And Default Ownership

Required/default pack selection belongs to the MAS profile or MAS overlay. This repo can publish source packs and declare their no-authority metadata, but it must not decide that a pack is required for a specific study, paper, or runtime owner path.

`packs/medical-display-core` is an OPL-owned source pack for reusable medical display templates. It is not MAS figure truth. MAS or the consuming domain owner binds it to paper-local figure purpose, claim/data refs, visual audit receipts, owner gates, typed blockers, or publication gates.

## Sync And External Resources

OPL Connect owns sync/install into the consuming discovery surface:

```bash
opl connect sync-skills --domain mas-scholar-skills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain mas-scholar-skills --scope quest --target-quest <quest_root> --json
```

The local install should contain the canonical aggregate Skill entry, the professional skills `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, `medical-figure-style`, `medical-figure-composer`, `medical-research-lit`, `medical-statistical-review`, `medical-table-design`, `medical-submission-prep`, and `medical-data-governance`, plugin/module refs, compact gallery review refs, and lightweight manifests needed for MAS discovery and review. Do not copy this whole repository, MAS render outputs, caches, single-figure exports, dependency locks, or intermediate gallery workspaces into a paper workspace or quest.

The legacy `--domain mas-scholar-skills` command remains a compatibility alias for existing workspaces.

Fabric/Connect may expose external resource capability, but external learning remains refs-only unless the MAS owner explicitly requires an executable external artifact. Missing external runtime installation is not a blocker for MAS Scholar Skills candidate refs, quality floors, or route-back recommendations.

## Ledger And Receipt Ownership

Ledger entries, owner receipts, reviewer receipts, typed blockers, human gates, current-package refs, runtime queues, provider attempts, and publication readiness decisions remain with MAS or the relevant OPL/domain owner surface.

MAS Scholar Skills may name downstream ref families such as `owner_receipt_ref`, `typed_blocker_ref`, `reviewer_receipt_ref`, `route_back_evidence_ref`, or `owner_gate_handoff_ref`. Those names identify where MAS should consume or route evidence; they are not MAS Scholar Skills acceptance, blocker creation, owner receipt, ledger authority, or publication readiness.
