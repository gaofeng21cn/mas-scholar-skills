<p align="center">
  <a href="./README.md"><strong>English</strong></a> | <a href="./README.zh-CN.md">中文</a>
</p>

<h1 align="center">OPL ScholarSkills</h1>

<p align="center"><strong>A branded OPL scholarly capability skill pack for Codex, MAS, and OPL-family agents</strong></p>
<p align="center">Display · Tables · Stats · Omics · Literature · Writing · Review · Submission · Data · Intake</p>

<!--
Owner: `opl-scholarskills`
Purpose: `public_repository_entry`
State: `public_entry`
Machine boundary: Human-readable public entry. Machine truth remains in `.codex-plugin/plugin.json`, `skills/opl-scholarskills/SKILL.md`, `contracts/scholar-skills-capability-modules.json`, gallery manifests/fingerprints, OPL Framework CLI readbacks, and domain owner receipts in consuming agents.
-->

`OPL ScholarSkills` packages a narrow set of scholarly capability modules as a Codex-compatible skill pack. This repository is the source of truth for the pack, and MAS or other OPL-family agents consume it through local Codex discovery paths in the paper workspace or runtime quest without moving domain authority out of the owning agent.

Each module is a capability descriptor and handoff pattern. It can guide refs-only candidate packages, dependency/run-context refs, and review handoffs. It does not sign owner receipts, mutate paper artifacts, declare quality verdicts, or claim publication readiness.

<table>
  <tr>
    <td width="33%" valign="top">
      <strong>Who It Serves</strong><br/>
      MAS, OPL-family agents, and Codex sessions that need reusable academic capability guidance
    </td>
    <td width="33%" valign="top">
      <strong>What It Provides</strong><br/>
      A Codex plugin, a Skill entry, ten module descriptors, authority guardrails, and a display gallery review package
    </td>
    <td width="33%" valign="top">
      <strong>How To Use</strong><br/>
      Sync the compact Skill into a workspace or quest-local `.codex/skills/opl-scholarskills` path, then let the domain owner consume or reject candidate refs
    </td>
  </tr>
</table>

## Why It Exists

Research agents need specialized skills, but specialized skills should not become random one-off prompts. ScholarSkills gives those capabilities a common OPL identity, a shared authority boundary, and a consistent handoff contract.

For example, MAS can request a display, table, statistics, writing, review, or submission capability through the same module vocabulary. The skill pack can help prepare candidate refs or review hints, while MAS still owns the study truth, publication truth, paper artifacts, owner receipts, typed blockers, and quality verdicts.

## Core Highlights

**Ten Branded Scholarly Modules**<br/>
The canonical module catalog lives in [`contracts/scholar-skills-capability-modules.json`](./contracts/scholar-skills-capability-modules.json) and is mirrored by [`skills/opl-scholarskills/SKILL.md`](./skills/opl-scholarskills/SKILL.md).

**Codex Plugin Packaging**<br/>
The repository is directly usable as a Codex plugin source through `.codex-plugin/plugin.json` and `skills/opl-scholarskills/SKILL.md`.

**Workspace / Quest-Local Consumption**<br/>
The expected MAS path is a local Codex discovery install inside the active paper workspace or runtime quest. System-level Codex installation and MAS program-repo `plugins/` mirrors are explicit developer or legacy surfaces, not the default consuming-agent path.

**No-Authority By Design**<br/>
All modules keep false authority flags. Outputs are candidates or refs until the consuming domain owner accepts, rejects, or routes them back.

**Display Gallery Included For Human Review**<br/>
The repository carries a compact MAS Display Pack gallery review package under [`gallery/medical-display/`](./gallery/medical-display/), including the PDF, manifest, reference, status, quality audit, and snapshot metadata. Workspace and quest installs should expose only these compact review refs, not renderer intermediates.

## Display Gallery

The display gallery is included here because this repository is the ScholarSkills source of truth and the fastest human review surface for `Scholar Display`. It is a published review package, not the MAS rendering workspace.

Included:

- [`gallery/medical-display/medical_display_gallery.pdf`](./gallery/medical-display/medical_display_gallery.pdf)
- [`gallery/medical-display/gallery_manifest.json`](./gallery/medical-display/gallery_manifest.json)
- [`gallery/medical-display/medical_display_gallery_reference.md`](./gallery/medical-display/medical_display_gallery_reference.md)
- [`gallery/medical-display/display_pack_gallery_status.md`](./gallery/medical-display/display_pack_gallery_status.md)
- [`gallery/medical-display/display_pack_gallery_quality_audit.md`](./gallery/medical-display/display_pack_gallery_quality_audit.md)
- [`gallery/medical-display/gallery_snapshot.json`](./gallery/medical-display/gallery_snapshot.json)

Current snapshot fields and fingerprints live in
[`gallery_manifest.json`](./gallery/medical-display/gallery_manifest.json) and
[`gallery_snapshot.json`](./gallery/medical-display/gallery_snapshot.json).
`scripts/verify.sh` checks the gallery package and keeps publication-ready claims unauthorized.

Not included:

- MAS `outputs/display-pack-gallery/`
- single-figure PNG/SVG/HTML exports
- render caches
- layout sidecars
- dependency locks or run-context files
- generated intermediate asset folders

Those files remain regenerable MAS/OPL operational outputs and are ignored by this repository.

## Boundary

`OPL ScholarSkills` is an OPL-owned capability library. It is not a new OPL brand module and not a MAS domain module.

OPL Framework owns the executable CLI and runtime bridge surfaces such as:

```bash
opl scholar-skills list --json
opl scholar-skills inspect --module opl.scholarskills.display --json
opl scholar-skills materialize --module opl.scholarskills.display --output-root /tmp/scholarskills-display --json
opl connect sync-skills --domain scholarskills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain scholarskills --scope quest --target-quest <quest_root> --json
```

MAS or another domain agent owns:

- domain truth
- study/publication truth
- artifact mutation
- owner receipts
- typed blockers
- human gates
- quality verdicts
- publication-ready claims

## Repository Layout

```text
.codex-plugin/plugin.json              Codex plugin manifest
skills/opl-scholarskills/SKILL.md      Codex skill entry
contracts/                             module catalog snapshot
gallery/medical-display/               compact human-review gallery package
docs/                                  capability and operations notes
scripts/verify.sh                      repository verification entry
```

## Install And Sync

This repository remains the source of truth. The recommended MAS install surface is a compact local Codex discovery copy in the active paper workspace or runtime quest:

```text
<workspace_root>/.codex/skills/opl-scholarskills/
<quest_root>/.codex/skills/opl-scholarskills/
```

Use OPL Connect from the current OPL Framework checkout:

```bash
opl connect sync-skills --domain scholarskills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain scholarskills --scope quest --target-quest <quest_root> --json
```

The target should receive only the Skill entry, plugin/module refs, and compact gallery review refs needed for local discovery and review. Do not copy the whole source repository, MAS `outputs/display-pack-gallery/`, render caches, single-figure exports, dependency locks, or other gallery intermediates into each paper workspace or quest. Do not use a MAS program-repo `plugins/opl-scholarskills/` mirror as the recommended runtime discovery surface.

For direct Codex plugin development, use this repository as a plugin source or let OPL Connect register the plugin explicitly:

```bash
opl connect sync-skills --domain scholarskills --scope codex --json
```

Cloning this repository does not install the OPL Framework executable surfaces. Prepare the current `one-person-lab` checkout or release bundle when CLI execution is needed.

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
