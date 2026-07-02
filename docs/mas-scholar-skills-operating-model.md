# MAS Scholar Skills Operating Model

Owner: `One Person Lab`
Purpose: Explain how `mas-scholar-skills` operates as the MAS Scholar Skills single-source enhancement pack without becoming MAS domain truth.
State: `active_operating_model`
Machine boundary: Human-readable operating model. Machine truth stays in `contracts/scholar-skills-capability-modules.json`, `skills/mas-scholar-skills/SKILL.md`, `skills/medical-research-write/SKILL.md`, `skills/medical-research-review/SKILL.md`, `skills/medical-research-figure/SKILL.md`, `skills/medical-research-lit/SKILL.md`, pack manifests, OPL Framework readbacks, and consuming MAS owner surfaces.

## Positioning

`MAS Scholar Skills` is the product and repository name for the OPL-owned `mas-scholar-skills` repository. The historical `opl-scholarskills` name remains a compatibility alias. The repository is narrower than a generic OPL scholarly base: it is the single-source external enhancement pack for MAS medical-paper capabilities.

It owns enhancement surfaces:

- MAS Scholar Skills module contracts and candidate ref families.
- Source packs such as `packs/medical-display-core`.
- Quality floors, route-back hints, and external-learning absorption.
- Compact human-review refs and templates that MAS can discover.
- Real syncable medical-paper skills where a stable AI workflow should have one maintained source: `medical-research-write`, `medical-research-review`, `medical-research-figure`, and `medical-research-lit`.

It does not own MAS study truth, publication truth, owner receipts, typed blockers, human gates, runtime queues, provider attempts, ledgers, current-package authority, or publication readiness.

## MAS Skill Call Path

The MAS overlay skill is the primary runtime entry. High-frequency paper work should enter through MAS-consumed skills whose bodies are maintained in this repository:

- `medical-research-write` for manuscript writing and revision.
- `medical-research-review` for critique, quality-floor review, and route-back.
- `medical-research-figure` for figure and display work.

MAS Scholar Skills is called after that routing point as a discovery and reference layer:

```text
MAS overlay skill
  -> medical-research-write / medical-research-review / medical-research-figure
  -> MAS Scholar Skills module refs, packs, templates, and quality floors
  -> refs-only candidate package or route-back hint
  -> MAS owner gate consume / reject / route back
```

Do not introduce `opl-scholar-write`, `opl-scholar-review`, or `opl-scholar-display` as default entries parallel to `medical-research-*`. If writing, review, or figure behavior is weak, update the corresponding skill body in this repository and let MAS consume the synced skill; do not re-create the old MAS-maintained second copy.

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

The local install should contain the canonical aggregate Skill entry, the real skill bodies `medical-research-write`, `medical-research-review`, `medical-research-figure`, and `medical-research-lit`, plugin/module refs, compact gallery review refs, and lightweight manifests needed for MAS discovery and review. Do not copy this whole repository, MAS render outputs, caches, single-figure exports, dependency locks, or intermediate gallery workspaces into a paper workspace or quest.

The legacy `--domain scholarskills` command remains a compatibility alias for existing workspaces.

Fabric/Connect may expose external resource capability, but external learning remains refs-only unless the MAS owner explicitly requires an executable external artifact. Missing external runtime installation is not a blocker for MAS Scholar Skills candidate refs, quality floors, or route-back recommendations.

## Ledger And Receipt Ownership

Ledger entries, owner receipts, reviewer receipts, typed blockers, human gates, current-package refs, runtime queues, provider attempts, and publication readiness decisions remain with MAS or the relevant OPL/domain owner surface.

MAS Scholar Skills may name downstream ref families such as `owner_receipt_ref`, `typed_blocker_ref`, `reviewer_receipt_ref`, `route_back_evidence_ref`, or `owner_gate_handoff_ref`. Those names identify where MAS should consume or route evidence; they are not MAS Scholar Skills acceptance, blocker creation, owner receipt, ledger authority, or publication readiness.
