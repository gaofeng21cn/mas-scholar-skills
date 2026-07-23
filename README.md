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
reviewing medical-paper work. MAG may also consume a narrow set of these Skills
as an optional refs-only grant enhancement. In both cases, the package helps
Codex choose an appropriate specialist, work from explicit evidence, prepare
inspectable candidate material, and route the result back to the consuming
domain owner.

The package is a consumer-neutral framework capability provider released
separately so its skills, quality references, display pack, and specialist
catalog can evolve independently. Both MAS and MAG profiles are optional
enhancements. The historical `opl-scholarskills` name is provenance only and is
not an active skill.

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

The current source exports 35 discoverable Codex skills: 11 aggregate/core
skills and 24 routers or named-specialty skills. Specialty skills are present
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

## Use With MAS

MAS may list this package under `bundled_capability_package_ids` so the Skills
are available by default. Bundling and materialization are distribution
conveniences, not dependency or readiness semantics. Installing MAS may
therefore materialize the exported Skills into the selected workspace or quest:

```bash
opl packages install mas --scope workspace --target-workspace <workspace_root> --json
opl packages install mas --scope quest --target-quest <quest_root> --json
```

Read the bundled state from the MAS package surface rather than inferring it
from this checkout:

```bash
opl packages status --package-id mas --scope workspace --target-workspace <workspace_root> --json
```

Cloning this repository alone does not install MAS or prove that bundled bytes
are current. Missing or incompatible Scholar Skills must not block MAS
admission, route, launch, or native paper work; MAS may record a non-blocking
diagnostic and continue.

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

## Optional Use With MAG

MAG keeps its native grant workflow as the only stage and authority owner. When
that workflow selects a matching enhancement, it may use
`medical-research-lit`, `medical-statistical-review`,
`medical-methodology-planner`, `medical-evidence-integrity-reviewer`,
`medical-evidence-synthesis-and-claim-map`, or
`medical-reference-integrity-auditor`.

```text
MAG grant prompt
  -> optional matching medical-* Skill when available
  -> refs-only candidate handoff
  -> MAG accepts, rejects, or routes back through its own authority surface
```

Like the MAS profile, this profile is not an install, activation, admission,
route, launch, or readiness dependency. MAG may bundle it under the same
consumer field for default availability. A missing or incompatible Skill
returns control to the MAG native workflow and may record only a non-blocking
diagnostic. It cannot create a typed blocker or change grant truth, fundability,
quality/export verdicts, strategy memory, receipts, or owner authority.

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
