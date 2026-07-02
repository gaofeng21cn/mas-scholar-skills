# MAS Scholar Skills Operating Model

Owner: `One Person Lab`
Purpose: Explain how `opl-scholarskills` operates as the MAS Scholar Skills single-source enhancement pack without becoming MAS domain truth.
State: `active_operating_model`
Machine boundary: Human-readable operating model. Machine truth stays in `contracts/scholar-skills-capability-modules.json`, `skills/opl-scholarskills/SKILL.md`, pack manifests, OPL Framework readbacks, and consuming MAS owner surfaces.

## Positioning

`MAS Scholar Skills` is the current product-stage name for the OPL-owned `opl-scholarskills` repository. The repository remains named `opl-scholarskills`, but its job is narrower than a generic OPL scholarly base: it is the single-source external enhancement pack for MAS medical-paper capabilities.

It owns enhancement surfaces:

- ScholarSkills module contracts and candidate ref families.
- Source packs such as `packs/medical-display-core`.
- Quality floors, route-back hints, and external-learning absorption.
- Compact human-review refs and templates that MAS can discover.

It does not own MAS study truth, publication truth, owner receipts, typed blockers, human gates, runtime queues, provider attempts, ledgers, current-package authority, or publication readiness.

## MAS Skill Call Path

The MAS overlay skill is the primary entry. High-frequency paper work should enter through MAS-owned skills:

- `medical-research-write` for manuscript writing and revision.
- `medical-research-review` for critique, quality-floor review, and route-back.
- `medical-research-figure` for figure and display work.

ScholarSkills is called after that routing point as a discovery and reference layer:

```text
MAS overlay skill
  -> medical-research-write / medical-research-review / medical-research-figure
  -> ScholarSkills module refs, packs, templates, and quality floors
  -> refs-only candidate package or route-back hint
  -> MAS owner gate consume / reject / route back
```

Do not introduce `opl-scholar-write`, `opl-scholar-review`, or `opl-scholar-display` as default entries parallel to MAS `medical-research-*`. If writing, review, or figure behavior is weak, improve the MAS medical-research skill and update ScholarSkills refs or quality floors as supporting material.

## Pack And Default Ownership

Required/default pack selection belongs to the MAS profile or MAS overlay. This repo can publish source packs and declare their no-authority metadata, but it must not decide that a pack is required for a specific study, paper, or runtime owner path.

`packs/medical-display-core` is an OPL-owned source pack for reusable medical display templates. It is not MAS figure truth. MAS or the consuming domain owner binds it to paper-local figure purpose, claim/data refs, visual audit receipts, owner gates, typed blockers, or publication gates.

## Sync And External Resources

OPL Connect owns sync/install into the consuming discovery surface:

```bash
opl connect sync-skills --domain scholarskills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain scholarskills --scope quest --target-quest <quest_root> --json
```

The local install should contain only the Skill entry, plugin/module refs, compact gallery review refs, and lightweight manifests needed for MAS discovery and review. Do not copy this whole repository, MAS render outputs, caches, single-figure exports, dependency locks, or intermediate gallery workspaces into a paper workspace or quest.

Fabric/Connect may expose external resource capability, but external learning remains refs-only unless the MAS owner explicitly requires an executable external artifact. Missing external runtime installation is not a blocker for ScholarSkills candidate refs, quality floors, or route-back recommendations.

## Ledger And Receipt Ownership

Ledger entries, owner receipts, reviewer receipts, typed blockers, human gates, current-package refs, runtime queues, provider attempts, and publication readiness decisions remain with MAS or the relevant OPL/domain owner surface.

ScholarSkills may name downstream ref families such as `owner_receipt_ref`, `typed_blocker_ref`, `reviewer_receipt_ref`, `route_back_evidence_ref`, or `owner_gate_handoff_ref`. Those names identify where MAS should consume or route evidence; they are not ScholarSkills acceptance, blocker creation, owner receipt, ledger authority, or publication readiness.
