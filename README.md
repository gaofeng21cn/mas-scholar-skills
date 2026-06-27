<p align="center">
  <a href="./README.md"><strong>English</strong></a> | <a href="./README.zh-CN.md">中文</a>
</p>

<h1 align="center">OPL ScholarSkills</h1>

<p align="center"><strong>An OPL skill pack for academic work that needs reusable scholarly capabilities</strong></p>
<p align="center">Display · Tables · Stats · Omics · Literature · Writing · Review · Submission · Data · Intake</p>

<!--
Owner: `opl-scholarskills`
Purpose: `public_repository_entry`
State: `public_entry`
Machine boundary: Human-readable public entry. Machine truth remains in `.codex-plugin/plugin.json`, `skills/opl-scholarskills/SKILL.md`, `contracts/scholar-skills-capability-modules.json`, gallery manifests/fingerprints, OPL Framework CLI readbacks, and domain owner receipts in consuming agents.
-->

<p align="center">
  <img src="assets/branding/opl-scholarskills-overview.png" alt="OPL ScholarSkills academic capability handoff map" width="100%" />
</p>

`OPL ScholarSkills` turns common scholarly capabilities into a Codex-compatible skill pack. It is not a paper system, a study authority, or a publication gate. Its job is to give Codex, MAS, and other OPL agents a stable way to ask for academic support such as figures, tables, statistics, literature, writing, review, submission prep, and data organization.

In practical terms, ScholarSkills says what each capability can help with, what material it needs, what candidate handoff it can prepare, and who must review the result. The domain owner still owns study truth, artifact authority, quality judgment, acceptance, and publication decisions.

<table>
  <tr>
    <td width="33%" valign="top">
      <strong>Who It Serves</strong><br/>
      Codex sessions, MAS research tasks, and OPL-family agents that need reusable academic capability guidance
    </td>
    <td width="33%" valign="top">
      <strong>What It Solves</strong><br/>
      It organizes scattered academic helper skills into ten clear modules that can be reused across studies, workspaces, and agents
    </td>
    <td width="33%" valign="top">
      <strong>What It Produces</strong><br/>
      Candidate refs, review hints, material checklists, gallery examples, and handoff packages; not final paper authority
    </td>
  </tr>
</table>

## Why ScholarSkills Exists

Academic work rarely moves in one shot. A real study may need intake, data understanding, statistical checks, visual design, literature mapping, drafting, review, revision, and submission preparation. Each step needs judgment, but those capabilities should not live as scattered one-off prompts.

ScholarSkills turns them into reusable capability modules:

- Agents can ask for display, table, statistics, literature, writing, review, submission, data, or intake support through one shared vocabulary.
- Each module explains what it is for, what inputs it expects, what candidate output it can prepare, and what review is still required.
- Candidate outputs can move into human or domain-agent review, but they do not become paper truth by themselves.
- The same skill pack can be synced into different workspaces, quests, and OPL agents without copying a second source of truth.

The design keeps reuse and responsibility separate: ScholarSkills prepares the handoff; the domain owner decides what is accepted.

## Ten Capability Modules

| Module | What it is for |
| --- | --- |
| **Scholar Display** | Figure intent, visual structure, display templates, and human-review gallery references. |
| **Scholar Tables** | Baseline tables, statistical summary tables, result tables, and table quality checks. |
| **Scholar Stats** | Analysis plans, model choices, reproducibility checks, and statistical result framing. |
| **Scholar Omics** | Omics matrices, feature selection, pathway hints, and pipeline quality references. |
| **Scholar Lit** | Literature maps, citation manifests, evidence chains, and prior-work comparisons. |
| **Scholar Write** | Candidate manuscript sections with source tracing for introduction, methods, results, discussion, and related text. |
| **Scholar Review** | Review reports, route-back evidence, revision suggestions, and next-step entry points. |
| **Scholar Submit** | Submission packages, checklists, format requirements, and pre-submit preparation. |
| **Scholar Data** | Data source notes, lineage, variable context, processing routes, and reproducibility hints. |
| **Scholar Intake** | New project, source, or external package intake into a governed research workspace. |

These modules are not ten separate products. They are an academic capability map that OPL, Codex, and MAS can discover and call. Final figures, manuscripts, analysis conclusions, review decisions, and submission actions remain with the owning domain system and human owner gate.

## Quick Use

Useful prompts look like this:

- "Use ScholarSkills to prepare a display candidate package for this study, but do not claim publication readiness; route it through the MAS owner gate."
- "For these results, use Display, Tables, and Stats to list the highest-value candidate materials to prepare next."
- "Turn the current literature evidence, writing gaps, and submission prep items into a handoff checklist."

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

- `OPL ScholarSkills` is an OPL-owned scholarly capability skill pack, not a MAS/MAG/RCA domain truth owner.
- This repository owns the distributable Codex plugin/Skill, the ten-module capability catalog, the gallery review package, and human-readable guidance.
- OPL Framework owns executable commands, sync, runtime environment bridges, and workbench actions.
- MAS and other domain agents keep ownership of study truth, publication truth, artifact authority, quality verdicts, owner receipts, human gates, and current package authority.
- ScholarSkills outputs are candidate refs, candidate packages, or review hints only. They cannot by themselves claim runtime readiness, domain readiness, quality verdicts, artifact authority, owner acceptance, publication readiness, or publication-ready status.

<details>
  <summary><strong>Technical Operator Entry</strong></summary>

### Repository Layout

```text
.codex-plugin/plugin.json              Codex plugin manifest
skills/opl-scholarskills/SKILL.md      Codex skill entry
contracts/                             module catalog snapshot
gallery/medical-display/               compact human-review gallery package
docs/                                  capability and operations notes
scripts/verify.sh                      repository verification entry
```

### Workspace Or Quest Sync

The recommended consuming surface is a local Codex discovery copy inside the active paper workspace or runtime quest:

```text
<workspace_root>/.codex/skills/opl-scholarskills/
<quest_root>/.codex/skills/opl-scholarskills/
```

Use OPL Connect from the current OPL Framework checkout:

```bash
opl connect sync-skills --domain scholarskills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain scholarskills --scope quest --target-quest <quest_root> --json
```

The target should receive only the Skill entry, plugin/module refs, and compact gallery review refs needed for local discovery and review. Do not copy the whole source repository, MAS `outputs/display-pack-gallery/`, render caches, single-figure exports, dependency locks, or other gallery intermediates into each paper workspace or quest.

### Common Readbacks

```bash
opl scholar-skills list --json
opl scholar-skills inspect --module opl.scholarskills.display --json
opl scholar-skills materialize --module opl.scholarskills.display --input-ref <ref> --artifact-root <ref-or-path> --output-root <path> --json
opl connect sync-skills --domain scholarskills --scope codex --json
```

Cloning this repository does not install OPL Framework executable surfaces. Prepare the current `one-person-lab` checkout or release bundle when CLI execution is needed.

</details>

## Verify

```bash
scripts/verify.sh
```

The verifier checks the plugin manifest, Skill entry, module catalog, gallery package, no-authority boundary, ignored intermediate-output policy, and gallery artifact fingerprints.

## Further Reading

- [Capability Modules](./docs/capability-modules.md)
- [Candidate Artifact Engines](./docs/candidate-artifact-engines.md)
- [Display Gallery](./docs/gallery/display-gallery.md)
- [Gallery Snapshot](./gallery/medical-display/gallery_snapshot.json)
