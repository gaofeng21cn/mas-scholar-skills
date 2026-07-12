# MAS Scholar Skills Operating Model

Owner: `One Person Lab`
Purpose: Explain how `mas-scholar-skills` supplies professional skill capability without becoming MAS domain truth.
State: `active_operating_model`
Machine boundary: Human-readable operating model. Package identity, ABI, core exports, and content digest live in `contracts/opl_capability_package_manifest.json`; module and Skill truth remain in `contracts/scholar-skills-capability-modules.json`, `.codex-plugin/plugin.json`, the selected `skills/medical-*/SKILL.md`, OPL package readback, and MAS owner surfaces.

## Role

MAS Scholar Skills is the required capability package for MAS medical-paper
work. The separate repository is a development, versioning, and release boundary,
not an optional product boundary. It owns maintained professional playbooks, source packs, quality floors,
route-back hints, and candidate-ref vocabulary. It does not own study truth,
publication truth, runtime attempts, provider attempts, ledgers, owner receipts,
typed blockers, human gates, current-package authority, or publication readiness.

The aggregate `mas-scholar-skills` skill is only a discovery and routing entry.
The selected `medical-*` skills carry professional medical reasoning. Contracts
record package identity, skill mapping, ref vocabulary, exposure policy, and
false-authority flags. These layers do not replace MAS stage prompts or owner
surfaces.

## AI-First Boundary

The specialist skills make evidence-fit, negative-finding, quality-review,
route-back, figure/table/source QA, and citation-support judgments. They return
candidate material for a domain owner to consume. The standard handoff is
`source_pack_ref`, `candidate_refs`, and `owner_gate_handoff_ref`.

The package cannot accept sources, sign a receipt, create a typed blocker, mutate
an artifact, schedule a runtime attempt, or claim readiness. OPL provides only
generic descriptor validation, selected-skill sync, and provenance readback;
there is no pack-specific medical module execution surface.

## Skill Classification

| Classification | Members | Role |
| --- | --- | --- |
| Active professional modules | `display`, `tables`, `stats`, `lit`, `write`, `review`, `submit`, `data` | Contract ids and candidate-ref vocabulary backed by real skills |
| Default professional skills | `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, `medical-figure-style`, `medical-figure-composer`, `medical-research-lit`, `medical-statistical-review`, `medical-table-design`, `medical-submission-prep`, `medical-data-governance` | AI-first playbooks that can be selectively synchronized for Codex discovery |
| Optional specialist skills | Advanced and medical-method specialist skills | Named-task helpers; refs-only and never part of the MAS hard-dependency readiness floor |

The quality floor belongs in the relevant professional skill. Change a module
contract only for an id, mapping, ref vocabulary, exposure policy, or boundary
change. This keeps flexible medical judgment out of framework validators.

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

For literature work, the provider split is explicit:

```text
medical-research-lit strategy
  -> MAS research-integrity-reference-verification for PubMed/PMC
  -> mas_provider_lookup_ref + pubmed_source_refs
  -> optional OPL Connect Crossref/OpenAlex fallback_source_refs
  -> source screening and claim-support candidate_refs
  -> MAS citation acceptance and manuscript use
```

PubMed/PMC lookup and normalization are MAS domain actions. OPL Connect may
provide explicit generic fallback metadata, coverage, or citation-graph inputs;
it does not decide source acceptance. All provider outputs are read-only evidence
inputs, not a citation verdict, owner receipt, blocker, or publication claim.

## Package Lifecycle And Discovery

```bash
opl packages status --package-id mas --scope workspace --target-workspace <workspace_root> --json
opl packages repair --package-id mas --scope workspace --target-workspace <workspace_root> --json
```

Installing MAS is the single user action. OPL resolves and installs this package
inside the MAS dependency closure, records compatible version and content locks,
and prevents disabling or uninstalling it while MAS remains installed. Missing or
incompatible core exports make MAS operationally unavailable and route to the
repair command above; there is no partial or silent-degradation mode.

Framework development and diagnostics may still inspect the provider source:

```bash
opl connect skills --domain mas-scholar-skills --json
opl connect sync-skills --domain mas-scholar-skills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain mas-scholar-skills --scope quest --target-quest <quest_root> --json
```

These are internal descriptor/materialization surfaces, not alternative user
installation interfaces. The first command is descriptor/provenance readback. The other commands copy
only selected skills and compact discovery material into a workspace or quest.
Optional specialists require a named task; the historical aggregate alias is not
installed as an active skill. Do not copy the full repository, MAS render outputs,
caches, dependency locks, or intermediate gallery workspaces into a paper
workspace.

When a named specialty is not covered by the default pack, discover and inspect
one external skill through OPL Connect before selectively syncing it. This is a
refs-only capability lookup, not a replacement for MAS stage policy, domain truth,
or owner authority.

## Gallery And Ownership

The display gallery is a compact human-review reference. It can anchor a template
or visual-audit candidate ref, but does not prove a live renderer, visual parity,
publication readiness, or owner acceptance.

MAS or the consuming domain owner owns all ledger entries, receipts, blockers,
current-package updates, artifact mutations, and publication decisions. Any such
ref named by the pack is only a downstream destination for owner consumption.
