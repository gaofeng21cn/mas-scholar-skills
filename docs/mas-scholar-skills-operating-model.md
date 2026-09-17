# MAS Scholar Skills Operating Model

Owner: `One Person Lab`
Purpose: Explain how `mas-scholar-skills` supplies required Package capability without becoming MAS or MAG domain truth.
State: `active_operating_model`
Machine boundary: Human-readable operating model. Package identity, ABI, exports, profiles, and content digest live in `contracts/opl_capability_package_manifest.json`; module and Skill truth remain in `contracts/scholar-skills-capability-modules.json`, `.codex-plugin/plugin.json`, the selected `skills/medical-*/SKILL.md`, OPL package readback, and MAS/MAG owner surfaces.

## Role

MAS Scholar Skills is a consumer-neutral capability package. The separate
repository is a development, versioning, and release boundary: it owns
maintained professional playbooks, source packs, quality floors, route-back
hints, and candidate-ref vocabulary. MAS and MAG consume it through required
Package presence/callability edges and refs-only professional handoffs; the
[no-authority boundary](./no-authority-boundary.md) owns the full list of
claims and writes this package must not make.

The aggregate `mas-scholar-skills` skill is only a discovery and routing entry.
The selected `medical-*` skills carry professional medical reasoning. Contracts
record package identity, skill mapping, ref vocabulary, exposure policy, and
false-authority flags, and the
[capability catalog](./capability-modules.md) holds the human-readable module
list. These layers do not replace MAS stage prompts or owner surfaces.

## Consumer Model

| Profile | Relationship | Failure semantics |
| --- | --- | --- |
| `mas-medical-paper.v1` | Required Package dependency for the MAS medical-paper workflow | Missing Package identity or required capability callability fails closed for MAS only and routes to managed install/repair |
| `mag-medical-grant.v1` | Required Package dependency for the MAG native grant workflow | Missing Package identity or required capability callability fails closed for MAG only and routes to managed install/repair |

`contracts/opl_capability_package_manifest.json` is the only owner of each
profile's `required_export_ids` and `required_module_ids`; this table does not
restate them. Current profiles use `required=true`,
`dependency_kind=required_runtime_dependency`, and fail-closed fields. The
consumer gate checks identity presence and required capability callability
without provider version, ABI, lock, payload, digest, Release Set, or
atomic-closure solving. A missing required edge is reported by the
consumer/platform readiness surface, never forged as a ScholarSkills domain
blocker.

## Handoff

The selected specialist skill makes evidence-fit, negative-finding,
quality-review, route-back, figure/table/source QA, and citation-support
judgments, and returns candidate material for a domain owner to consume. The
standard handoff is `source_pack_ref`, `candidate_refs`, and
`owner_gate_handoff_ref`.

The package cannot accept sources, sign a receipt, create a typed blocker, mutate
an artifact, schedule a runtime attempt, or claim readiness. OPL provides only
generic descriptor validation, selected-skill sync, and provenance readback;
there is no pack-specific medical module execution surface.

## Catalog And Change Policy

The [capability catalog](./capability-modules.md) owns module ids, their backing
skills, and the skill exposure classification;
`contracts/scholar-skills-capability-modules.json` owns the machine truth. The
quality floor belongs in the relevant professional skill. Change a module
contract only for an id, mapping, ref vocabulary, exposure policy, or boundary
change, so flexible medical judgment stays out of framework validators.

## Stage, Skill, Provider, And Owner Path

MAS `agent/stages/` and `agent/prompts/` are the canonical stage source. They
own stage validity, evidence thresholds, route-back, owner gates, and acceptance.
A synchronized skill is a Codex discovery projection, not a stage authority.

```text
MAS stage prompt
  -> selected medical-* professional skill
  -> candidate_refs and route-back hint
  -> MAS owner gate consume, reject, or route back
```

For grant work, MAG remains the route owner:

```text
MAG native grant prompt
  -> required ScholarSkills Package and callable grant capability set
  -> selected medical-* Skill for the task
  -> refs-only candidate handoff
  -> MAG owner surface consumes, rejects, or routes back
```

For literature work, the provider split is explicit:

```text
medical-research-lit strategy
  -> Package-owned pure adapter builds PubMed/PMC primary-search or Crossref/OpenAlex fallback requests
  -> OPL Connect executes the bounded requests and returns parsed source candidates[]
  -> domain owner selects a candidate reference
  -> verification companion checks the selected reference through bounded providers
  -> OPL Connect executes HTTP and materializes generic evidence/receipts
  -> source screening and claim-support candidate_refs
  -> MAS citation acceptance and manuscript use
```

Search and reference verification are separate surfaces. The Package-owned
scientific-search adapter describes PubMed ESearch -> ESummary and Europe PMC
search as well as Crossref/OpenAlex fallback requests; its next-step state is
serializable and bounded. OPL Connect executes all declared HTTP, retry, cache,
strict matching, receipts, and connector errors without embedding provider search
logic. The verification adapter accepts a known reference and may describe up to
two provider steps. MAS still decides candidate selection, source acceptance, and
manuscript use. All provider outputs are read-only inputs, not a citation verdict,
owner receipt, blocker, or publication claim.

## Distribution And Discovery

```bash
opl packages status --package-id mas --scope workspace --target-workspace <workspace_root> --json
```

The target distribution is complete, independently owner-published Package
bytes in the ScholarSkills GHCR `latest-stable`. Codex Skill materialization is
one carrier projection, not Package identity or complete installed truth.
Current consumers may still use `bundled_capability_package_ids`; that is a
compatibility carrier input. The provider owns no consumer status, repair,
admission, route, launch, or readiness authority. The consumer/platform reports
a missing required presence/callability edge and blocks only MAS or MAG.

Framework development and diagnostics may still inspect the provider source:

```bash
opl connect skills --domain mas-scholar-skills --json
opl connect sync-skills --domain mas-scholar-skills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain mas-scholar-skills --scope quest --target-quest <quest_root> --json
```

These are internal descriptor/materialization surfaces, not alternative user
installation interfaces. The first command is descriptor/provenance readback.
Scope materialization copies the primary routing Skill by default and adds a
selected stage or specialty Skill only for the matching task. The package keeps
all 36 source Skill entries for dependency callability and on-demand routing,
but they do not become one project-wide discovery set. Do not copy the full repository, MAS render outputs,
caches, dependency locks, or intermediate gallery workspaces into a paper
workspace.

When a task needs a named specialty, route to the already-materialized specialist
or its router. Discovery and presence do not replace MAS stage policy, domain
truth, or owner authority.

## Gallery

`docs/gallery/display-gallery.md` owns the compact human-review reference
package and its maintenance route. The gallery can anchor a template or
visual-audit candidate ref, but it does not prove a live renderer, visual
parity, publication readiness, or owner acceptance. Owner-side consumption of
any pack ref follows the
[no-authority boundary](./no-authority-boundary.md).
