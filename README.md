<p align="center">
  <img src="assets/branding/mas-scholar-skills-logo.png" alt="MAS Scholar Skills logo" width="132" />
</p>

<p align="center">
  <a href="./README.md"><strong>English</strong></a> | <a href="./README.zh-CN.md">中文</a>
</p>

<h1 align="center">MAS Scholar Skills</h1>

<p align="center"><strong>An OPL-owned external enhancement pack for MAS medical-paper capabilities</strong></p>
<p align="center">Display · Tables · Stats · Literature · Writing · Review · Submission · Data Governance</p>

<!--
Owner: `mas-scholar-skills`
Purpose: `public_repository_entry`
State: `public_entry`
Machine boundary: Human-readable public entry. Machine truth remains in `.codex-plugin/plugin.json`, `skills/mas-scholar-skills/SKILL.md`, `skills/medical-manuscript-writing/SKILL.md`, `skills/medical-manuscript-review/SKILL.md`, `skills/medical-figure-design/SKILL.md`, `skills/medical-research-lit/SKILL.md`, `skills/medical-statistical-review/SKILL.md`, `skills/medical-table-design/SKILL.md`, `skills/medical-submission-prep/SKILL.md`, `skills/medical-data-governance/SKILL.md`, `contracts/domain_descriptor.json`, `contracts/capability_map.json`, `contracts/scholar-skills-capability-modules.json`, gallery manifests/fingerprints, OPL Framework CLI readbacks, and domain owner receipts in consuming agents.
-->

<p align="center">
  <img src="assets/branding/mas-scholar-skills-overview.png" alt="MAS Scholar Skills academic capability handoff map" width="100%" />
</p>

`MAS Scholar Skills` is the canonical product and repository name for the OPL-owned, Codex-compatible external enhancement pack that serves MAS medical-paper work. The historical `opl-scholarskills` name remains only as a compatibility alias. This repository is the single source for MAS Scholar Skills refs, packs, quality floors, templates, external-learning absorption, module contracts, and the syncable professional skills `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, `medical-research-lit`, `medical-statistical-review`, `medical-table-design`, `medical-submission-prep`, and `medical-data-governance`.

The MAS stage operating prompts stay in the MAS domain-agent repository. The canonical stage sources are MAS `agent/stages/` and `agent/prompts/`; MAS overlay Skills and workspace or quest `.codex/skills/` copies are Codex discovery projections and compatibility surfaces, not the source of stage authority. That sync step must stay because Codex discovers local skills through `.codex/skills/`. `write`, `review`, `figure`, `scout`, and related stages decide when the stage is valid, what evidence is enough, where the output goes next, what routes back, and what needs an owner gate. The eight `medical-*` skills in this repository are professional skills for doing the assigned writing, review, figure, literature, statistics, table, submission, and clinical data governance work well.

In practical terms, MAS Scholar Skills says what each capability can help with, what material it needs, what candidate handoff it can prepare, and who must review the result. The domain owner still owns study truth, artifact authority, quality judgment, acceptance, and publication decisions.

The operating rule is progress-first and AI auto-judgment-first. MAS should let AI judge everything that can be judged from available evidence, and MAS Scholar Skills should supply AI-consumable evidence, `verdict_candidate`, `route_back_candidate`, and stop/continue recommendations. Work goes to the domain owner or human only when the next action would cross into domain truth, publication readiness, owner receipt, typed blocker creation, or a real human gate.

Display is one active professional module. MAS Scholar Skills is also the source, contract, and documentation home for Lit, Tables, Stats, Submit, Write, Review, and Data Governance. Every active module uses the same refs-only handoff frame: `source_pack_ref`, `candidate_package_ref`, `execution_receipt_ref`, and `owner_gate_handoff_ref`. Those refs describe candidate material and the next owner gate; they do not create runtime authority or acceptance.

The current classification is fixed: eight active professional modules, all backed by syncable real Codex specialist skills. Their active ids are `mas-scholar-skills.display`, `mas-scholar-skills.tables`, `mas-scholar-skills.stats`, `mas-scholar-skills.lit`, `mas-scholar-skills.write`, `mas-scholar-skills.review`, `mas-scholar-skills.submit`, and `mas-scholar-skills.data`; historical `opl.scholarskills.*` ids remain legacy aliases/provenance only. `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, `medical-research-lit`, `medical-statistical-review`, `medical-table-design`, `medical-submission-prep`, and `medical-data-governance` are the active skill sources. Generic source or external-learning intake belongs to OPL Framework or MAS stage/source surfaces and is not kept here as a contract placeholder. Omics will enter MAS Scholar Skills only when MAS has a stable real omics specialist workflow to maintain.

For literature work, `medical-research-lit` now uses the stable OPL Connect PubMed path: `opl connect pubmed search --query <query> --limit <n> --json`. The connector returns `pubmed_source_refs` and `pubmed_connector_invocation_ref`; MAS Scholar Skills keeps the AI workflow around query design, source screening, evidence maps, and route-back handoff.

The current professional quality floor is concentrated in those eight real skills. Figure, writing, review, and literature skills keep their AI-first contracts. Statistical review adds estimand, denominator, assumption, effect-size, multiplicity, and action-matrix discipline. Table design adds table shell, source metric, denominator, footnote, QC, and table-to-claim discipline. Submission prep adds journal instruction, reporting checklist, declaration, data/code availability, reviewer response, and package consistency discipline. Data governance adds clinical data manifest, dictionary/codebook, cleaning/normalization readiness, version impact, study binding, privacy/access, and lifecycle guardrail discipline.

<table>
  <tr>
    <td width="33%" valign="top">
      <strong>Who It Serves</strong><br/>
      MAS overlay sessions and MAS medical-paper skills that need OPL-owned enhancement material
    </td>
    <td width="33%" valign="top">
      <strong>What It Solves</strong><br/>
      It keeps MAS Scholar Skills refs, packs, quality floors, external-learning patterns, and module contracts in one source
    </td>
    <td width="33%" valign="top">
      <strong>What It Produces</strong><br/>
      Candidate refs, templates, quality-floor hints, gallery examples, and handoff packages; not MAS owner authority
    </td>
  </tr>
</table>

## Why MAS Scholar Skills Exists

Academic work rarely moves in one shot. A real study may need source intake, data understanding, statistical checks, visual design, literature mapping, drafting, review, revision, and submission preparation. Each step needs judgment, but reusable professional capability should not live as scattered one-off prompts.

MAS Scholar Skills turns the reusable support material into active professional modules and specialist skills:

- MAS overlay and MAS medical-research skills can ask for display, table, statistics, literature, writing, review, submission, or data governance support through one shared vocabulary.
- Each module explains what it is for, what inputs it expects, what candidate output it can prepare, and what review is still required.
- `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, `medical-research-lit`, `medical-statistical-review`, `medical-table-design`, `medical-submission-prep`, and `medical-data-governance` are real Codex skills in this repo; they are not only module descriptors.
- Source/external-learning intake is handled by OPL Framework or MAS stage/source surfaces, not as an active module or contract placeholder here; future omics support should be added here as a real professional skill when a stable MAS workflow exists.
- By default, a professional specialist skill belongs in the consuming domain-agent repo next to the stage prompts. MAS Scholar Skills is the external pack exception for MAS writing, review, figure, literature, statistics, table, submission, Display, and source refs because these surfaces are reusable across workspaces and independently syncable.
- Candidate outputs can move into human or domain-agent review, but they do not become paper truth by themselves.
- The same skill pack can be synced into different MAS workspaces or quests without copying a second source of truth.

The design keeps reuse and responsibility separate: MAS Scholar Skills prepares the handoff; the domain owner decides what is accepted. The shared refs-only/no-authority rule lives in [No-Authority Boundary](./docs/no-authority-boundary.md).

## Active Professional Modules

| Module | What it is for |
| --- | --- |
| **Scholar Display** | Figure intent, visual structure, display templates, and human-review gallery references. |
| **Scholar Tables** | Baseline tables, statistical summary tables, result tables, and table quality checks. |
| **Scholar Stats** | Analysis plans, model choices, reproducibility checks, and statistical result framing. |
| **Scholar Lit** | Literature maps, citation manifests, evidence chains, and prior-work comparisons. |
| **Scholar Write** | Candidate manuscript sections with source tracing for introduction, methods, results, discussion, and related text. |
| **Scholar Review** | Review reports, route-back evidence, revision suggestions, and next-step entry points. |
| **Scholar Submit** | Submission packages, checklists, format requirements, and pre-submit preparation. |
| **Medical Data Governance** | Clinical data asset manifests, dataset manifests, data dictionary/codebook, cleaning/normalization readiness, lineage, version impact, study binding, privacy/access tiers, lifecycle guardrails, owner-gate handoff, and reproducibility hints. |

These modules are not separate products and they are not default entries parallel to MAS stage operating prompts. They are the MAS Scholar Skills enhancement map that MAS can discover and call. Final figures, manuscripts, analysis conclusions, review decisions, and submission actions remain with the owning MAS/domain system and human owner gate.

## External Learning Module Fit

External projects such as ARS, PaperOrchestra, Research-Paper-Writing-Skills, Paperlib, SciPilot Figure, NaturePanelForge, Marsilea, and curated figure/resource lists inform MAS Scholar Skills as refs-only module fit. The lessons land as stronger candidate refs and checklists for Display, Tables, Stats, Lit, Write, Review, Submit, and Data.

The specialist-skill floor also absorbs maintainable patterns from `K-Dense-AI/scientific-agent-skills` and `Yuan1z0825/nature-skills`: discoverable scientific skill packs, figure contracts, argument-first writing, reviewer fact bases, critical-thinking validity checks, source-routing and citation verification, retrieval contracts, plotting/export QA, power and experimental-design discipline, venue-instruction mapping, clinical table discipline, data availability checks, database provenance, and reviewer-response discipline. These patterns are adapted into MAS-consumed skills instead of imported as a second runtime.

These additions improve progress without forcing agents to install external runtimes first. They add reviewable candidate surfaces such as visual QA previews, citation verification, claim-evidence maps, submission sanity refs, source lineage, and data lifecycle refs; they do not bypass MAS or another domain owner gate.

The K-Dense-specific intake map is documented in [K-Dense scientific-agent-skills intake](./docs/kdense-scientific-agent-skills-intake.md). It records which patterns landed in the eight real `medical-*` skills and which foreign defaults remain rejected.

## Default Boundary Defense

Every new or disputed MAS Scholar Skills surface should point back to [No-Authority Boundary](./docs/no-authority-boundary.md) and keep four owners separate:

1. **Stage prompt**: MAS `agent/stages/` and `agent/prompts/` own stage entry, routing, evidence thresholds, owner gates, route-back, owner receipt, typed blocker, human gate, publication readiness, and artifact authority.
2. **Professional specialist skill**: MAS Scholar Skills owns the reusable external-pack `medical-*` skills and Display/source refs as candidate-producing playbooks, not acceptance authority.
3. **Tool connector**: OPL Connect/Fabric or another connector owns tool/API invocation, normalized read receipts, connector errors, and resource access.
4. **Contract module**: `contracts/scholar-skills-capability-modules.json` owns module ids, maps, ref vocabulary, no-authority flags, and sync policy.

`mas-scholar-skills` is the aggregate entry and discovery layer for this pack. `opl-scholarskills` is only a legacy alias/provenance entry, not a second truth source.

## Quick Use

Useful prompts look like this:

- "In the MAS overlay, use `medical-figure-design` as the primary entry and pull MAS Scholar Skills Display refs for the candidate package; do not claim publication readiness."
- "For these results, ask the MAS medical-research skills to use MAS Scholar Skills Display, Tables, and Stats refs to list the highest-value candidate materials."
- "Turn the current literature evidence, writing gaps, and submission prep items into a refs-only MAS handoff checklist."

## Included Review Example

This repository includes a compact medical display gallery so users and operators can inspect the current Scholar Display examples directly. It is a human-review reference package, not publication authorization.

- [`gallery/medical-display/medical_display_gallery.pdf`](./gallery/medical-display/medical_display_gallery.pdf)
- [`gallery/medical-display/medical_display_gallery_reference.md`](./gallery/medical-display/medical_display_gallery_reference.md)
- [`gallery/medical-display/display_pack_gallery_status.md`](./gallery/medical-display/display_pack_gallery_status.md)
- [`gallery/medical-display/display_pack_gallery_quality_audit.md`](./gallery/medical-display/display_pack_gallery_quality_audit.md)
- [`gallery/medical-display/gallery_manifest.json`](./gallery/medical-display/gallery_manifest.json)
- [`gallery/medical-display/gallery_snapshot.json`](./gallery/medical-display/gallery_snapshot.json)

The gallery keeps only the final review package. Renderer intermediates, single-figure exports, caches, layout sidecars, and dependency locks do not belong in this repository.

## Boundary

- `MAS Scholar Skills` is the canonical name for this repository and enhancement pack, not a generic OPL base and not a MAS/MAG/RCA domain truth owner.
- This repository owns the distributable Codex plugin/Skills, the MAS-consumed medical writing/review/figure/literature/statistics/table/submission/data-governance professional skills, the eight-module active capability catalog, the gallery review package, and human-readable guidance.
- OPL Framework owns executable commands, sync, runtime environment bridges, Connect/Fabric resource plumbing, and workbench actions.
- MAS overlay remains the runtime owner entry. MAS maintains the stage operating prompts outside this repository and consumes the eight syncable `medical-*` professional specialist skills from this repository.
- MAS Scholar Skills outputs are candidate refs, candidate packages, or review hints only; [No-Authority Boundary](./docs/no-authority-boundary.md) is the common reference for owner receipt, typed blocker, publication readiness, current package, artifact authority, and owner acceptance limits.

<details>
  <summary><strong>Technical Operator Entry</strong></summary>

### Repository Layout

```text
.codex-plugin/plugin.json              Codex plugin manifest
skills/mas-scholar-skills/SKILL.md     Canonical aggregate Codex skill entry
skills/medical-manuscript-writing/SKILL.md Medical manuscript writing specialist skill
skills/medical-manuscript-review/SKILL.md Medical manuscript review specialist skill
skills/medical-figure-design/SKILL.md Medical figure design specialist skill
skills/medical-research-lit/SKILL.md   Medical literature specialist skill
skills/medical-statistical-review/SKILL.md Medical statistical review specialist skill
skills/medical-table-design/SKILL.md   Medical table design specialist skill
skills/medical-submission-prep/SKILL.md Medical submission preparation specialist skill
skills/medical-data-governance/SKILL.md Medical data governance specialist skill
skills/opl-scholarskills/SKILL.md      Legacy alias entry
contracts/domain_descriptor.json       OMA target descriptor
contracts/capability_map.json          OMA capability target map
contracts/                             module catalog snapshot
gallery/medical-display/               compact human-review gallery package
docs/                                  capability and operations notes
scripts/verify.sh                      repository verification entry
```

### Workspace Or Quest Sync

The recommended consuming surface is a local Codex discovery copy inside the active paper workspace or runtime quest:

```text
<workspace_root>/.codex/skills/mas-scholar-skills/
<workspace_root>/.codex/skills/medical-manuscript-writing/
<workspace_root>/.codex/skills/medical-manuscript-review/
<workspace_root>/.codex/skills/medical-figure-design/
<workspace_root>/.codex/skills/medical-research-lit/
<workspace_root>/.codex/skills/medical-statistical-review/
<workspace_root>/.codex/skills/medical-table-design/
<workspace_root>/.codex/skills/medical-submission-prep/
<workspace_root>/.codex/skills/medical-data-governance/
<quest_root>/.codex/skills/mas-scholar-skills/
<quest_root>/.codex/skills/medical-manuscript-writing/
<quest_root>/.codex/skills/medical-manuscript-review/
<quest_root>/.codex/skills/medical-figure-design/
<quest_root>/.codex/skills/medical-research-lit/
<quest_root>/.codex/skills/medical-statistical-review/
<quest_root>/.codex/skills/medical-table-design/
<quest_root>/.codex/skills/medical-submission-prep/
<quest_root>/.codex/skills/medical-data-governance/
```

Use OPL Connect from the current OPL Framework checkout:

```bash
opl connect sync-skills --domain mas-scholar-skills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain mas-scholar-skills --scope quest --target-quest <quest_root> --json
```

The target should receive only the Skill entry, plugin/module refs, and compact gallery review refs needed for local discovery and review. Do not copy the whole source repository, MAS `outputs/display-pack-gallery/`, render caches, single-figure exports, dependency locks, or other gallery intermediates into each paper workspace or quest.

### Common Readbacks

```bash
opl scholar-skills list --json
opl scholar-skills inspect --module mas-scholar-skills.display --json
opl scholar-skills materialize --module mas-scholar-skills.display --input-ref <ref> --artifact-root <ref-or-path> --output-root <path> --json
opl connect sync-skills --domain mas-scholar-skills --scope codex --json
```

Cloning this repository does not install OPL Framework executable surfaces. Prepare the current `one-person-lab` checkout or release bundle when CLI execution is needed. The legacy `--domain mas-scholar-skills` form remains accepted for existing workspaces.

</details>

## Verify

```bash
scripts/verify.sh
```

The verifier checks the plugin manifest, Skill entry, module catalog, gallery package, no-authority boundary, ignored intermediate-output policy, and gallery artifact fingerprints.

## Further Reading

- [Capability Modules](./docs/capability-modules.md)
- [No-Authority Boundary](./docs/no-authority-boundary.md)
- [MAS Scholar Skills Operating Model](./docs/mas-scholar-skills-operating-model.md)
- [Candidate Artifact Engines](./docs/candidate-artifact-engines.md)
- [Display Gallery](./docs/gallery/display-gallery.md)
- [Gallery Snapshot](./gallery/medical-display/gallery_snapshot.json)
