<p align="center">
  <img src="assets/branding/mas-scholar-skills-logo.png" alt="MAS Scholar Skills logo" width="132" />
</p>

<p align="center">
  <a href="./README.md"><strong>English</strong></a> | <a href="./README.zh-CN.md">中文</a>
</p>

<h1 align="center">MAS Scholar Skills</h1>

<p align="center"><strong>The required capability package for MAS medical-paper work</strong></p>
<p align="center">Display · Tables · Stats · Literature · Writing · Review · Submission · Data Governance</p>

<!--
Owner: `mas-scholar-skills`
Purpose: `public_repository_entry`
State: `public_entry`
Machine boundary: Human-readable public entry. Machine truth remains in `.codex-plugin/plugin.json`, `skills/mas-scholar-skills/SKILL.md`, `skills/medical-manuscript-writing/SKILL.md`, `skills/medical-manuscript-review/SKILL.md`, `skills/medical-figure-design/SKILL.md`, `skills/medical-figure-style/SKILL.md`, `skills/medical-figure-composer/SKILL.md`, `skills/medical-research-lit/SKILL.md`, `skills/medical-statistical-review/SKILL.md`, `skills/medical-table-design/SKILL.md`, `skills/medical-submission-prep/SKILL.md`, `skills/medical-data-governance/SKILL.md`, `contracts/domain_descriptor.json`, `contracts/capability_map.json`, `contracts/scholar-skills-capability-modules.json`, gallery manifests/fingerprints, OPL Framework CLI readbacks, and domain owner receipts in consuming agents.
-->

<p align="center">
  <img src="assets/branding/mas-scholar-skills-overview.png" alt="MAS Scholar Skills academic capability handoff map" width="100%" />
</p>

`MAS Scholar Skills` is the canonical product and repository name for the required, Codex-compatible capability package used by MAS medical-paper work. The separate repository is a development, versioning, and release boundary, not an optional product boundary: installing MAS must resolve this package in the same `opl packages` transaction, and MAS is not operational when its core package is missing or incompatible. The historical `opl-scholarskills` name remains only as history/tombstone/provenance, not as an active Codex skill. This repository is the single source for MAS Scholar Skills refs, packs, quality floors, templates, external-learning absorption, module contracts, the syncable professional skills `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, `medical-figure-style`, `medical-figure-composer`, `medical-research-lit`, `medical-statistical-review`, `medical-table-design`, `medical-submission-prep`, and `medical-data-governance`, plus optional router/reviewer skills and 20 optional named-specialty skills for methodology, evidence integrity, publication route-back, advanced biomedical, and medical-method work.

The aggregate `mas-scholar-skills` Skill is intentionally a thin discovery and routing entry. It maps a module to the concrete `medical-*` skill and preserves the shared owner boundary; specialist checklists stay in the selected skill, module and exposure details stay in contracts, and install, CLI, gallery, and operating guidance stay in `docs/`. This prevents the aggregate entry from becoming a second copy of every workflow.

The MAS stage operating prompts stay in the MAS domain-agent repository. The canonical stage sources are MAS `agent/stages/` and `agent/prompts/`; MAS overlay Skills and workspace or quest `.codex/skills/` copies are Codex discovery projections and compatibility surfaces, not the source of stage authority. That sync step must stay because Codex discovers local skills through `.codex/skills/`. `write`, `review`, `figure`, `scout`, and related stages decide when the stage is valid, what evidence is enough, where the output goes next, what routes back, and what needs an owner gate. The `medical-*` skills in this repository are professional skills for doing the assigned writing, review, figure, style, composition, literature, statistics, table, submission, and clinical data governance work well.

In practical terms, MAS Scholar Skills says what each capability can help with, what material it needs, what candidate handoff it can prepare, and who must review the result. The reusable owner-boundary summary is [No-Authority Boundary](./docs/no-authority-boundary.md); machine routing and false-authority flags live in `contracts/capability_map.json`.

The operating rule is progress-first and AI auto-judgment-first. MAS should let AI judge everything that can be judged from available evidence, and MAS Scholar Skills should supply AI-consumable evidence, `verdict_candidate`, `route_back_candidate`, and stop/continue recommendations. Work goes to the domain owner or human only when the next action would cross into domain truth, publication readiness, owner receipt, typed blocker creation, or a real human gate.

Display is one active professional module. MAS Scholar Skills is also the source, contract, and documentation home for Lit, Tables, Stats, Submit, Write, Review, and Data Governance. Every active module uses the same refs-only handoff frame: `source_pack_ref`, `candidate_refs`, and `owner_gate_handoff_ref`. Those refs describe candidate material and the next owner gate; they do not create runtime authority or acceptance.

The current classification is fixed: eight active professional modules, all backed by syncable real Codex specialist skills. Their active ids are `mas-scholar-skills.display`, `mas-scholar-skills.tables`, `mas-scholar-skills.stats`, `mas-scholar-skills.lit`, `mas-scholar-skills.write`, `mas-scholar-skills.review`, `mas-scholar-skills.submit`, and `mas-scholar-skills.data`; historical `opl.scholarskills.*` ids remain legacy aliases/provenance only. `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, `medical-figure-style`, `medical-figure-composer`, `medical-research-lit`, `medical-statistical-review`, `medical-table-design`, `medical-submission-prep`, and `medical-data-governance` define the hard core. Every active MAS workspace or quest receives all 35 exported skills for native Codex discovery; the other 24 remain specialty-routed and outside the 11-skill hard readiness floor. `opl-scholarskills` has no active `SKILL.md`. Generic source or external-learning intake belongs to OPL Framework or MAS stage/source surfaces and is not kept here as a contract placeholder.

For literature work, `medical-research-lit` is the real AI-first specialist skill. PubMed/PMC stays first for biomedical sources through MAS `research-integrity-reference-verification`, which returns `mas_provider_lookup_ref` and `pubmed_source_refs` as non-authoritative evidence inputs. Crossref and OpenAlex are optional OPL Connect fallback refs for metadata, coverage, or citation graph needs, not citation acceptance. `medical-research-lit` owns query strategy, source screening, fallback reasons, `claim_support_map_ref`, and `owner_gate_handoff_ref`; MAS owns provider lookup, citation acceptance, and manuscript use.

The current professional quality floor lives in the real skills. Shared
handoff shapes live in
[`references/professional-quality-ref-templates.md`](./references/professional-quality-ref-templates.md)
so each `medical-*` skill can point to the common refs instead of copying a long
checklist.
MAS journal-family pack refs fold back through that same reference into the
existing `medical-*` skills; they are route hints, not new physical skills or
MAS authority surfaces.

Optional named-specialty work starts from four router/reviewer skills:
`medical-methodology-planner`, `medical-evidence-integrity-reviewer`,
`medical-publication-routeback-reviewer`, and `medical-advanced-biomed-router`.
They are real Codex skills with frontmatter, but they are refs-only /
no-authority candidate helpers. They do not replace the default medical-paper
skills, do not become MAS authority owners, and do not block MAS ordinary
progress when absent.

The 20 narrower specialty skills, such as `medical-structural-biology`,
`medical-protocol-and-sap-planner`, `medical-reference-integrity-auditor`,
`medical-display-qc`, and `scientific-compute-runner`, remain real
named-specialty `SKILL.md` playbooks. They are materialized by default so Codex
can discover them before execution starts, but a router should select one only
for a matching specialty task.

Four formerly separate optional professional skills are now reviewer modes
rather than independent Codex metadata: evidence-gap triage is covered by
`medical-evidence-integrity-reviewer`; methodology routeback and owner-gate
handoff are covered by `medical-publication-routeback-reviewer`; publication
strategy memory is covered by `medical-research-portfolio-memory-curator`.
Their retired directories keep `TOMBSTONE.md` redirect records only.

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
- `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, `medical-figure-style`, `medical-figure-composer`, `medical-research-lit`, `medical-statistical-review`, `medical-table-design`, `medical-submission-prep`, and `medical-data-governance` are real Codex skills in this source repository; they are not only module descriptors, plugin mirrors, or connector descriptors.
- Specialty work uses four router/reviewer skills: `medical-methodology-planner`, `medical-evidence-integrity-reviewer`, `medical-publication-routeback-reviewer`, and `medical-advanced-biomed-router`, plus 20 named-specialty `SKILL.md` playbooks. All are materialized for discovery, but selected only for matching tasks; four narrower legacy capabilities are retained as modes under the broader reviewers.
- `opl-scholarskills` is a tombstone/provenance alias only. It is not installed or discovered as an active Codex skill.
- Source/external-learning intake is handled by OPL Framework or MAS stage/source surfaces, not as an active module or contract placeholder here; future omics support should be added here as a real professional skill when a stable MAS workflow exists.
- By default, a professional specialist skill belongs in the consuming domain-agent repo next to the stage prompts. MAS Scholar Skills is the external pack exception for MAS writing, review, figure, literature, statistics, table, submission, Display, and source refs because these surfaces are reusable across workspaces and independently syncable.
- Candidate outputs can move into human or domain-agent review, but they do not become paper truth by themselves.
- The same skill pack can be synced into different MAS workspaces or quests without copying a second source of truth. OPL plugin installs and MAS mirrors are sync/discovery projections of this repository, not competing skill sources.

The design keeps reuse and responsibility separate: MAS Scholar Skills prepares the handoff; the domain owner decides what is accepted. Use [No-Authority Boundary](./docs/no-authority-boundary.md) for the shared refs-only/no-authority rule instead of restating it in each module.

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

The specialist-skill floor also absorbs maintainable patterns from `K-Dense-AI/scientific-agent-skills` and `Yuan1z0825/nature-skills`: discoverable scientific skill packs, figure contracts, schematic boundaries, argument-first writing, reviewer fact bases, critical-thinking and scholar-evaluation checks, source-routing and citation verification, retrieval contracts, plotting/export QA, EDA/model-specification discipline, power and experimental-design discipline, venue-instruction mapping, clinical table discipline, data availability checks, database provenance, and reviewer-response discipline. These patterns are adapted into MAS-consumed skills instead of imported as a second runtime.

These additions improve progress without forcing agents to install external runtimes first. They add reviewable candidate surfaces such as visual QA previews, citation verification, claim-evidence maps, submission sanity refs, source lineage, and data lifecycle refs; they do not bypass MAS or another domain owner gate.

The K-Dense-specific intake map is documented in [K-Dense scientific-agent-skills intake](./docs/kdense-scientific-agent-skills-intake.md). It records which patterns landed in the real `medical-*` skills, which biomedical specialist families stay discoverable through OPL Connect on demand, and which foreign defaults remain rejected.

## Default Boundary Defense

Every new or disputed MAS Scholar Skills surface should point back to
[No-Authority Boundary](./docs/no-authority-boundary.md): Stage prompt sources
(`agent/stages/`, `agent/prompts/`) own MAS authority, each Professional
specialist skill owns refs-only candidate playbooks, each Tool connector owns
read-only access receipts, and the contract module owns ids/ref vocabulary.
`opl-scholarskills` remains only a history/tombstone/provenance name.

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
- This repository owns the distributable Codex plugin/Skills, the MAS-consumed medical writing/review/figure/style/composition/literature/statistics/table/submission/data-governance professional skills, the eight-module active capability catalog, the gallery review package, and human-readable guidance.
- OPL Framework owns executable commands, sync, runtime environment bridges, Connect/Fabric resource plumbing, and workbench actions.
- MAS overlay remains the runtime owner entry. MAS maintains the stage operating prompts outside this repository and consumes the syncable `medical-*` professional specialist skills from this repository.
- MAS Scholar Skills outputs are candidate refs, candidate packages, or review hints only; [No-Authority Boundary](./docs/no-authority-boundary.md) is the common owner-boundary reference, and `contracts/capability_map.json` is the machine-readable routing and false-authority source.

<details>
  <summary><strong>Technical Operator Entry</strong></summary>

### Repository Layout

```text
.codex-plugin/plugin.json              Codex plugin manifest
skills/mas-scholar-skills/SKILL.md     Canonical aggregate Codex skill entry
skills/medical-manuscript-writing/SKILL.md Medical manuscript writing specialist skill
skills/medical-manuscript-review/SKILL.md Medical manuscript review specialist skill
skills/medical-figure-design/SKILL.md Medical figure design specialist skill
skills/medical-figure-style/SKILL.md Medical figure style subskill
skills/medical-figure-composer/SKILL.md Medical figure composition subskill
skills/medical-research-lit/SKILL.md   Medical literature specialist skill
skills/medical-statistical-review/SKILL.md Medical statistical review specialist skill
skills/medical-table-design/SKILL.md   Medical table design specialist skill
skills/medical-submission-prep/SKILL.md Medical submission preparation specialist skill
skills/medical-data-governance/SKILL.md Medical data governance specialist skill
skills/medical-methodology-planner/SKILL.md Optional methodology router skill
skills/medical-evidence-integrity-reviewer/SKILL.md Optional evidence integrity reviewer skill
skills/medical-publication-routeback-reviewer/SKILL.md Optional publication route-back reviewer skill
skills/medical-advanced-biomed-router/SKILL.md Optional advanced biomed router skill
contracts/scholar-skills-capability-modules.json Codex exposure policy and module contract
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
<workspace_root>/.codex/skills/medical-figure-style/
<workspace_root>/.codex/skills/medical-figure-composer/
<workspace_root>/.codex/skills/medical-research-lit/
<workspace_root>/.codex/skills/medical-statistical-review/
<workspace_root>/.codex/skills/medical-table-design/
<workspace_root>/.codex/skills/medical-submission-prep/
<workspace_root>/.codex/skills/medical-data-governance/
<quest_root>/.codex/skills/mas-scholar-skills/
<quest_root>/.codex/skills/medical-manuscript-writing/
<quest_root>/.codex/skills/medical-manuscript-review/
<quest_root>/.codex/skills/medical-figure-design/
<quest_root>/.codex/skills/medical-figure-style/
<quest_root>/.codex/skills/medical-figure-composer/
<quest_root>/.codex/skills/medical-research-lit/
<quest_root>/.codex/skills/medical-statistical-review/
<quest_root>/.codex/skills/medical-table-design/
<quest_root>/.codex/skills/medical-submission-prep/
<quest_root>/.codex/skills/medical-data-governance/
```

Use the unified OPL Packages surface. Installing MAS resolves this required
package and materializes all 35 exported Skills into the selected scope:

```bash
opl packages install mas --scope workspace --target-workspace <workspace_root> --json
opl packages install mas --scope quest --target-quest <quest_root> --json
```

The target receives all 35 exported skills for native discovery, plus only the compact plugin/module and gallery review refs needed by the package. Specialty skills remain task-routed even though they are present. Do not copy the whole source repository, MAS `outputs/display-pack-gallery/`, render caches, single-figure exports, dependency locks, or other gallery intermediates into each paper workspace or quest.

### Common Readbacks

```bash
opl packages status --package-id mas --scope workspace --target-workspace <workspace_root> --json
opl packages repair --package-id mas --scope workspace --target-workspace <workspace_root> --json
```

Cloning this repository does not install MAS or OPL Framework executable surfaces. Provider-source development may inspect internal OPL Connect descriptor/materialization primitives, but those are not a second user installation interface. The package does not expose a module execution CLI.

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
- [Academic Figure Skill Learning Landing](./docs/academic-figure-skill-landing.md)
- [Display Gallery](./docs/gallery/display-gallery.md)
- [Gallery Snapshot](./gallery/medical-display/gallery_snapshot.json)
