# MAS Scholar Skills Operating Model

Owner: `One Person Lab`
Purpose: Explain how `mas-scholar-skills` operates as the MAS Scholar Skills professional-skill enhancement pack without becoming MAS domain truth.
State: `active_operating_model`
Machine boundary: Human-readable operating model. Machine truth stays in `contracts/scholar-skills-capability-modules.json`, `skills/mas-scholar-skills/SKILL.md`, `skills/medical-manuscript-writing/SKILL.md`, `skills/medical-manuscript-review/SKILL.md`, `skills/medical-figure-design/SKILL.md`, `skills/medical-research-lit/SKILL.md`, pack manifests, OPL Framework readbacks, and consuming MAS owner surfaces.

## Positioning

`MAS Scholar Skills` is the product and repository name for the OPL-owned `mas-scholar-skills` repository. The historical `opl-scholarskills` name remains a compatibility alias. The repository is narrower than a generic OPL scholarly base: it is the external enhancement pack and professional-skill source for MAS medical-paper capabilities.

It owns enhancement surfaces:

- MAS Scholar Skills module contracts and candidate ref families.
- Source packs such as `packs/medical-display-core`.
- Quality floors, route-back hints, and external-learning absorption.
- Compact human-review refs and templates that MAS can discover.
- Syncable medical-paper professional skills where a stable AI workflow should have one maintained source: `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, and `medical-research-lit`.

It does not own MAS study truth, publication truth, owner receipts, typed blockers, human gates, runtime queues, provider attempts, ledgers, current-package authority, or publication readiness.

## Capability Module Classification

MAS Scholar Skills has ten capability-module contracts and four syncable real Codex specialist skills.

| Classification | Members | Role |
| --- | --- | --- |
| Capability-module contracts | `display`, `tables`, `stats`, `omics`, `lit`, `write`, `review`, `submit`, `data`, `intake` | Shared module ids, vocabulary, ref families, checklists, candidate handoff, receipt shape, and owner gates. |
| Real specialist skills | `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, `medical-research-lit` | AI-first professional playbooks that Codex can discover and execute after OPL Connect syncs them into a workspace or quest `.codex/skills/` directory. |
| Contract-layer modules | `tables`, `stats`, `omics`, `submit`, `data`, `intake` | Refs, checklists, candidate packages, quality floors, and owner-gate handoff until a stable active workflow justifies a real skill. |

The six contract-layer modules are not unfinished skills and are not MAS-private implementations. They came from MAS medical-paper workflow needs, OPL capability registry/readback requirements, and external-learning patterns that are useful as refs/checklists. Keep them as the machine contract layer unless Codex needs to actively run a maintained specialist workflow.

## Professional Quality Floor

MAS Scholar Skills now applies an explicit quality floor to the four real
specialist skills. The floor is adapted from fresh inspection of
`K-Dense-AI/scientific-agent-skills` commit
`1e024ea8547ada12039edbe8197aaa959d97763f` and
`Yuan1z0825/nature-skills` commit
`c91df241a7a963ea151687ac669c5534404f53e5`.

| Skill | Quality floor |
| --- | --- |
| `medical-figure-design` | Figure contract, evidence chain, archetype, renderer decision, style brief, candidate set, critic review, final-scale visual QA, and reviewer packet. |
| `medical-manuscript-writing` | One-sentence argument, terminology ledger, paragraph job map, section contract, claim-strength calibration, citation integrity, figure/table binding, and data/code availability audit. |
| `medical-manuscript-review` | Shared fact base, technical/significance/reader reviewer lanes, cross-review synthesis, reviewer action matrix, citation repair, revision-delta audit, and route-back closeout. |
| `medical-research-lit` | PubMed-first source routing, query plan, fallback source refs, deduplication, retain/reject/watchlist screening, source verification, support-strength matrix, and citation integrity floor. |

Statistics, data availability, reviewer response, reporting guideline, and
submission checks are valuable, but they enter this floor first through the
four existing specialist skills. They become new real skills only when MAS
needs Codex to actively run a stable standalone workflow.

## Stage Source Boundary

The canonical MAS stage source is the MAS domain-agent repository, specifically `agent/stages/` and `agent/prompts/`. MAS overlay Skills, local workspace or quest `.codex/skills/` copies, and synced compatibility entries are Codex projection surfaces. They can expose a stage or specialist skill to a Codex session, but they must not be treated as the source for stage routing, evidence thresholds, owner gates, route-back semantics, owner receipts, typed blockers, human gates, publication readiness, or artifact authority.

Default ownership for a professional specialist skill is the consuming domain-agent repo, close to the stage prompt that calls it. A specialist skill should move to an external pack only when it is heavy, cross-workspace, or independently releasable. MAS Scholar Skills is that external pack for MAS medical writing, review, figure design, literature work, Display/source refs, and reusable source packs.

Tool connectors are the third boundary. OPL Connect/Fabric owns tool or API invocation, normalized read receipts, connector error semantics, and resource access, such as the PubMed command used by `medical-research-lit`. A connector does not own stage policy, professional judgment, route acceptance, owner receipt, typed blocker, human gate, publication readiness, or artifact authority.

## MAS Skill Call Path

The MAS overlay skill and MAS stage operating prompts are the primary runtime and stage entries, with source edits made in MAS `agent/stages/` and `agent/prompts/`. They decide stage validity, evidence thresholds, route-back, owner gates, and acceptance. High-frequency paper work should then use MAS-consumed professional skills maintained in this repository:

- `medical-manuscript-writing` for manuscript writing and revision.
- `medical-manuscript-review` for critique, quality-floor review, and route-back.
- `medical-figure-design` for figure and display work.
- `medical-research-lit` for literature search strategy, source screening, and evidence maps.

MAS Scholar Skills is called after that routing point as a professional-skill, discovery, and reference layer:

```text
MAS agent/stages or agent/prompts stage prompt
  -> optional MAS overlay or .codex projection for Codex discovery
  -> medical-manuscript-writing / medical-manuscript-review / medical-figure-design / medical-research-lit
  -> MAS Scholar Skills module refs, packs, templates, and quality floors
  -> optional tool connector readback, such as OPL Connect PubMed
  -> refs-only candidate package or route-back hint
  -> MAS owner gate consume / reject / route back
```

If writing, review, or figure execution quality is weak, update the corresponding professional skill in this repository and let MAS consume the synced skill. If the problem is stage validity, routing, owner gate, or acceptance semantics, update the MAS stage operating prompt. This keeps professional playbooks and MAS stage authority as two clear single sources.

Use `medical-research-lit` when the task needs PubMed-style external literature discovery, source screening, PMID/DOI verification, or a claim-support map. Literature discovery is external-resource heavy, so it belongs in MAS Scholar Skills as a real specialist skill while MAS still owns citation acceptance and manuscript use.

The stable PubMed execution path is:

```bash
opl connect pubmed search --query "<query>" --limit <n> --json
```

`medical-research-lit` records the returned normalized metadata as `pubmed_source_refs` and the connector read receipt as `pubmed_connector_invocation_ref`. MAS Scholar Skills owns query strategy, screening, evidence maps, and route-back handoff. OPL Connect owns the PubMed API call, source-ref normalization, connector error semantics, and read-only receipt candidate. MAS owns citation judgment, manuscript use, review ledger updates, owner receipts, typed blockers, and publication decisions.

## Pack And Default Ownership

Required/default pack selection belongs to the MAS profile or MAS overlay. This repo can publish source packs and declare their no-authority metadata, but it must not decide that a pack is required for a specific study, paper, or runtime owner path.

`packs/medical-display-core` is an OPL-owned source pack for reusable medical display templates. It is not MAS figure truth. MAS or the consuming domain owner binds it to paper-local figure purpose, claim/data refs, visual audit receipts, owner gates, typed blockers, or publication gates.

## Sync And External Resources

OPL Connect owns sync/install into the consuming discovery surface:

```bash
opl connect sync-skills --domain mas-scholar-skills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain mas-scholar-skills --scope quest --target-quest <quest_root> --json
```

The local install should contain the canonical aggregate Skill entry, the professional skills `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, and `medical-research-lit`, plugin/module refs, compact gallery review refs, and lightweight manifests needed for MAS discovery and review. Do not copy this whole repository, MAS render outputs, caches, single-figure exports, dependency locks, or intermediate gallery workspaces into a paper workspace or quest.

The legacy `--domain scholarskills` command remains a compatibility alias for existing workspaces.

Fabric/Connect may expose external resource capability, but external learning remains refs-only unless the MAS owner explicitly requires an executable external artifact. Missing external runtime installation is not a blocker for MAS Scholar Skills candidate refs, quality floors, or route-back recommendations.

## Ledger And Receipt Ownership

Ledger entries, owner receipts, reviewer receipts, typed blockers, human gates, current-package refs, runtime queues, provider attempts, and publication readiness decisions remain with MAS or the relevant OPL/domain owner surface.

MAS Scholar Skills may name downstream ref families such as `owner_receipt_ref`, `typed_blocker_ref`, `reviewer_receipt_ref`, `route_back_evidence_ref`, or `owner_gate_handoff_ref`. Those names identify where MAS should consume or route evidence; they are not MAS Scholar Skills acceptance, blocker creation, owner receipt, ledger authority, or publication readiness.
