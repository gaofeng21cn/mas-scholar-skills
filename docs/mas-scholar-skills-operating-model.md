# MAS Scholar Skills Operating Model

Owner: `One Person Lab`
Purpose: Explain how `mas-scholar-skills` supplies required Package capability without becoming MAS or MAG domain truth.
State: `active_operating_model`
Machine boundary: Human-readable operating model. Package identity, ABI, exports, profiles, and content digest live in `contracts/opl_capability_package_manifest.json`; module and Skill truth remain in `contracts/scholar-skills-capability-modules.json`, `.codex-plugin/plugin.json`, the selected `skills/medical-*/SKILL.md`, OPL package readback, and MAS/MAG owner surfaces.

## Role

MAS Scholar Skills is a consumer-neutral framework capability provider. The
separate repository is a development, versioning, and release boundary. It owns
maintained professional playbooks, source packs, quality floors, route-back
hints, and candidate-ref vocabulary. It does not own study or grant truth,
publication truth, runtime attempts, provider attempts, ledgers, owner receipts,
typed blockers, human gates, current-package authority, or readiness. MAS and
MAG consume it through required Package presence/callability edges and
refs-only professional handoffs.

The aggregate `mas-scholar-skills` skill is only a discovery and routing entry.
The selected `medical-*` skills carry professional medical reasoning. Contracts
record package identity, skill mapping, ref vocabulary, exposure policy, and
false-authority flags. These layers do not replace MAS stage prompts or owner
surfaces.

## Consumer Model

| Profile | Relationship | Failure semantics |
| --- | --- | --- |
| `mas-medical-paper.v1` | Required Package dependency; 11 exports describe the callable capability set MAS expects | Missing Package identity or required capability callability blocks MAS only and routes to managed install/repair |
| `mag-medical-grant.v1` | Required Package dependency for the MAG native grant workflow | Missing Package identity or required capability callability blocks MAG only and routes to managed install/repair |

Current machine profiles still use `required=false`,
`dependency_kind=optional_enhancement`, and fail-open fields. Those fields are a
known migration mismatch, not the target composition rule. The target checks
identity presence and required capability callability without provider version,
ABI, lock, payload, digest, Release Set, or atomic-closure solving. The MAG
profile selects only
`medical-research-lit`,
`medical-statistical-review`, `medical-methodology-planner`,
`medical-evidence-integrity-reviewer`,
`medical-evidence-synthesis-and-claim-map`, and
`medical-reference-integrity-auditor`. These Skills can prepare candidate refs;
the Package cannot change consumer domain truth or strategy memory, sign a
consumer owner receipt, or claim fundability, quality/export, publication, or
owner authority. A missing required edge is reported by the consumer/platform
readiness surface, never forged as a ScholarSkills domain blocker.

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
| Optional specialist skills | Advanced and medical-method specialist skills | Named-task helpers; refs-only and never part of consumer readiness |

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
  -> OPL Connect PubMed/PMC discovery returns primary biomedical source refs
  -> optional pure adapter returns Crossref/OpenAlex metadata/coverage/citation-graph fallback candidates[]
  -> domain owner selects a candidate reference
  -> verification companion checks the selected reference through bounded providers
  -> OPL Connect executes HTTP and materializes generic evidence/receipts
  -> source screening and claim-support candidate_refs
  -> MAS citation acceptance and manuscript use
```

Search and reference verification are separate surfaces. Framework-owned OPL
Connect implements PubMed/PMC discovery and executes all HTTP, retry, cache,
strict matching, receipts, and connector errors. The package's one-step search
adapter ABI is intentionally limited to Crossref/OpenAlex generic metadata,
coverage, and citation-graph fallback; it must not implement a second PubMed/PMC
client. The verification adapter accepts a known reference and may describe up to
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
Scope materialization copies all 35 exported skills and compact discovery
material into a workspace or quest so Codex can discover specialties before
execution. Specialty skills still require a matching named task; the historical
aggregate alias is not installed as an active skill. Do not copy the full repository, MAS render outputs,
caches, dependency locks, or intermediate gallery workspaces into a paper
workspace.

When a task needs a named specialty, route to the already-materialized specialist
or its router. Discovery and presence do not replace MAS stage policy, domain
truth, or owner authority.

## Gallery And Ownership

The display gallery is a compact human-review reference. It can anchor a template
or visual-audit candidate ref, but does not prove a live renderer, visual parity,
publication readiness, or owner acceptance.

MAS, MAG, or the consuming domain owner owns all ledger entries, receipts,
blockers, current-package updates, artifact mutations, grant decisions, and
publication decisions. Any such ref named by the pack is only a downstream
destination for owner consumption.
