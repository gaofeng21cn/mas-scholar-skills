<p align="center">
  <img src="assets/branding/mas-scholar-skills-logo.png" alt="MAS Scholar Skills logo" width="132" />
</p>

<p align="center">
  <a href="./README.md"><strong>English</strong></a> | <a href="./README.zh-CN.md">中文</a>
</p>

<h1 align="center">MAS Scholar Skills</h1>

<p align="center"><strong>Professional medical-research skills for MAS</strong></p>
<p align="center">Figures · Tables · Statistics · Literature · Writing · Review · Submission · Data Governance</p>

<!--
Owner: `mas-scholar-skills`
Purpose: `public_repository_entry`
State: `public_entry`
Machine boundary: Human-readable public entry. Package identity, exports, module ids, skill bodies, authority flags, gallery bytes, installed-package currentness, and consuming-domain decisions remain in contracts, source, manifests, OPL package readback, repo-native verification, and MAS/domain owner surfaces.
-->

<p align="center">
  <img src="assets/branding/mas-scholar-skills-overview-v2.png" alt="MAS Scholar Skills support across the medical-research journey" width="100%" />
</p>

MAS Scholar Skills gives MAS reusable, task-focused expertise for producing and
reviewing medical-paper work. MAG consumes a narrower required capability set
for grant work. In both cases, the package helps
Codex choose an appropriate specialist, work from explicit evidence, prepare
inspectable candidate material, and route the result back to the consuming
domain owner.

The package is a consumer-neutral framework capability provider designed for
independent release so its skills, quality references, display pack, and
specialist catalog can evolve independently. The target publication route is
complete Package bytes in the owner's GHCR `latest-stable`; Codex Plugin/Skill
materialization is only a carrier projection. Fresh owner publication and
complete actual-carrier readback remain unproven. The target MAS and MAG
dependency edge requires Package identity presence and required capability
callability, not cross-Package version/ABI solving, lock, payload, digest,
Release Set, or atomic closure. The current manifest models both profiles as
required runtime dependencies with fail-closed identity/callability gates; the
domain agents retain all stage, quality, artifact, and readiness authority.
The historical `opl-scholarskills` name is provenance only and is not an active
skill.
The cross-repository migration SSOT is the App
[`opl-package-platform-composition-migration.md`](https://github.com/gaofeng21cn/one-person-lab-app/blob/main/docs/active/opl-package-platform-composition-migration.md);
Framework's same-named document remains its repo-local compatibility and
deletion inventory.

## What It Covers

| Module | Typical work |
| --- | --- |
| Display | Figure design, style, composition, export checks, and visual-review candidates |
| Tables | Table shells, denominator and metric traceability, and consistency checks |
| Statistics | Analysis-plan and result review, assumptions, uncertainty, and reproducibility |
| Literature | Search strategy, source screening, citation verification, and claim-support mapping |
| Writing | Evidence-traced manuscript sections and revision candidates |
| Review | Independent review packets, defect routing, and revision priorities |
| Submission | Offline journal-layout profiles, default reader layout, file inventory, declarations, and response preparation |
| Data Governance | Data manifests, dictionaries, lineage, lifecycle, access, and reproducibility candidates |

The current source exports 36 discoverable Codex skills: 11 aggregate/core
skills and 25 routers or named-specialty skills. Specialty skills are present
for discovery but selected only when a task actually needs that specialty.
The machine catalog also includes two pure adapter modules for scientific search
and reference verification; OPL Connect performs their network I/O and records
receipts. Framework-owned OPL Connect handles primary PubMed/PMC discovery; the
package's scientific-search adapter is deliberately limited to Crossref/OpenAlex
metadata, coverage, and citation-graph fallback.

See [Capability Modules](./docs/capability-modules.md) for the current mapping.

For EHR or registry evidence, `registry_signal_validity_pack` folds into one
`ehr_registry_signal_validity_ref`; `medical-statistical-review` is its sole
professional producer and owner route. Other specialists may consume that ref
without creating a parallel validity judgment.

## For Codex

This repository is a standard Codex Plugin marketplace and the repository root
is the plugin root. The marketplace points directly to that root, so
`skills/` remains the only source of truth for all 36 active Skills; there is no
second copied Skill tree under `plugins/`.

Add the repository marketplace, inspect the available entry, and install it:

```bash
codex plugin marketplace add gaofeng21cn/mas-scholar-skills --ref main
codex plugin list --marketplace mas-scholar-skills --available --json
codex plugin add mas-scholar-skills@mas-scholar-skills --json
codex plugin list --marketplace mas-scholar-skills --json
```

Start a new Codex task after installation so the installed Skills are picked
up. Remove the plugin and marketplace independently:

```bash
codex plugin remove mas-scholar-skills@mas-scholar-skills --json
codex plugin marketplace remove mas-scholar-skills --json
```

For local development, replace the GitHub shorthand in `marketplace add` with
the absolute checkout path. Use an isolated `HOME` and `CODEX_HOME` for
installation tests; Codex copies installed bytes into its plugin cache instead
of loading the marketplace source in place.

## For Agents

Agents that consume repository sources directly should start from
`skills/mas-scholar-skills/SKILL.md`, then route to the selected
`skills/<skill-id>/SKILL.md`. Read package identity and exported Skill ids from
`contracts/opl_capability_package_manifest.json`, and read exposure, routing,
and no-authority policy from
`contracts/scholar-skills-capability-modules.json`. Do not derive Package
identity, consumer dependency status, or domain readiness from marketplace
metadata.

The Plugin is a carrier projection only. Installing or enabling it establishes
Codex discovery of the packaged Skills; it does not install MAS or MAG, satisfy
a consumer dependency by itself, write study or grant truth, or issue an owner
receipt.

## Use With MAS

MAS requires this Package, while individual named specialty Skills remain
task-selected. Installing MAS must therefore ensure the ScholarSkills Package
identity and the required MAS capability set are present and callable; missing
capability blocks MAS only and routes to managed install/repair. It does not
block unrelated Packages or introduce a version/ABI/lock/payload gate. The
package dependency edge is enforced through the consumer's required
identity/callability gate; carrier installation alone is not sufficient:

```bash
opl packages install mas --scope workspace --target-workspace <workspace_root> --json
opl packages install mas --scope quest --target-quest <quest_root> --json
```

Read the bundled state from the MAS package surface rather than inferring it
from this checkout:

```bash
opl packages status --package-id mas --scope workspace --target-workspace <workspace_root> --json
```

Cloning this repository alone does not install MAS or prove that complete
ScholarSkills bytes are installed. A Codex Skill projection alone is also
insufficient. Missing required Package identity or capability callability
blocks MAS, while unrelated Packages remain available.

Use each surface only for the state it owns:

| Surface | What a positive readback proves | What it does not prove |
| --- | --- | --- |
| `codex plugin list --marketplace mas-scholar-skills --json` | The Codex Plugin carrier is installed and enabled in that Codex home. | OPL Package identity/currentness, MAS/MAG dependency closure, or domain readiness. |
| OPL Package/App maintenance status and its receipt | Installed Package identity, selected source/version/digest, and payload verification recorded by that runtime. | Consumer capability callability or a study/grant verdict. |
| MAS or MAG dependency/capability readback | The consumer's required edge and selected capability set are callable for that consumer. | Publication, submission, fundability, or owner acceptance. |
| MAS, MAG, or study/grant owner receipts | Only the exact domain state and artifact bytes bound by that receipt. | Broader Package, Plugin, or production state not named by the receipt. |

The `opl packages ...` examples above are valid only on Framework runtimes that
actually expose that command surface. When the installed `opl` reports
`unknown_command`, use the current OPL App/Framework maintenance and receipt
surface rather than treating a checkout, Plugin install, or stale command
example as Package status.

Inside a MAS task, the normal path is:

```text
MAS stage goal and evidence
  -> matching medical-* specialist skill
  -> candidate refs, review findings, or route-back recommendation
  -> MAS/domain owner accepts, rejects, or routes the work
```

The aggregate `mas-scholar-skills` skill is a discovery and routing entry. The
selected `medical-*` skill carries the detailed professional workflow; MAS stage
prompts remain the owner of stage validity, evidence thresholds, and acceptance.

## Use With MAG

MAG keeps its native grant workflow as the only stage and authority owner. Its
required ScholarSkills capability set includes
`medical-research-lit`, `medical-statistical-review`,
`medical-methodology-planner`, `medical-evidence-integrity-reviewer`,
`medical-evidence-synthesis-and-claim-map`, or
`medical-reference-integrity-auditor`.

```text
MAG grant prompt
  -> required ScholarSkills Package and callable grant capability set
  -> matching medical-* Skill selected for the task
  -> refs-only candidate handoff
  -> MAG accepts, rejects, or routes back through its own authority surface
```

Missing Package identity or required capability callability blocks MAG only and
routes to managed install/repair; it does not block unrelated Packages or grant
ScholarSkills any domain authority. Named specialty exposure remains
task-selected. The required machine profile is now the current owner contract.
It does not transfer domain truth, quality verdict, artifact authority, or
readiness to this capability provider.

`medical-submission-prep` includes an offline-first publication-layout catalog.
Named journals use a matching local adaptation profile; an unspecified journal
uses the publication-grade `general-medical-reader.v1` template. The core reader
outputs are always `paper.pdf` and `paper_with_supplementary.pdf`. Formal
submission refreshes the linked official instructions before any compliance
claim. Frontiers is represented once as a publisher-family profile, so any
`Frontiers in ...` journal can use the same maintained baseline without a
network lookup during ordinary authoring.

## Authority Boundary

This package prepares candidate material. It does not write study or grant
truth or artifact bodies, sign owner or reviewer receipts, create typed
blockers, mutate runtime state or strategy memory, choose the current package,
or claim fundability, quality/export, or publication readiness. Those decisions
remain with MAS, MAG, or the consuming domain owner.

Use [No-Authority Boundary](./docs/no-authority-boundary.md) for the durable rule
and machine references.

## Medical Display Gallery

[`gallery/medical-display/`](./gallery/medical-display/) is a compact human-review
package for template and visual-audit references. Its manifest and snapshot own
the exact current members and fingerprints. A gallery item is a design reference,
not proof of a live renderer, paper quality, owner acceptance, or publication
readiness.

See [Display Gallery](./docs/gallery/display-gallery.md) for maintenance and
consumption boundaries.

## Repository Map

```text
skills/                         aggregate, core, router, and specialty skills
contracts/                      package identity, module catalog, and boundaries
references/                     shared quality and handoff references
packs/medical-display-core/     Display source pack and renderer verification
packs/medical-publication-layouts/  reader template, journal profiles, and citation assets
gallery/medical-display/        compact human-review package
docs/                           operating, catalog, boundary, and active-truth docs
scripts/verify.sh               repository verification entry
```

## Verify

```bash
scripts/verify.sh fast
scripts/verify.sh render
scripts/verify.sh full
```

`fast` checks contracts, adapters, repository consistency, and skill kernels.
`render` checks gallery and renderer regressions. `full` runs both. Passing any
lane is repository evidence only; it is not runtime, domain, artifact,
publication, or production readiness.

## Documentation

- [Docs Index](./docs/README.md)
- [Active Truth](./docs/active/mas-scholar-skills-ideal-state-gap-plan.md)
- [Operating Model](./docs/mas-scholar-skills-operating-model.md)
- [Capability Modules](./docs/capability-modules.md)
- [No-Authority Boundary](./docs/no-authority-boundary.md)
- [Display Gallery](./docs/gallery/display-gallery.md)
