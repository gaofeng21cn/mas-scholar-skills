---
name: mas-scholar-skills
description: "Route MAS medical-paper tasks to the maintained MAS Scholar Skills specialist skills and inspect their refs-only, owner-gated boundaries. Use when Codex needs pack-level capability discovery, module-to-skill routing, optional specialist selection, or no-authority/owner-surface guidance. For a named writing, review, figure, literature, statistics, table, submission, data-governance, or specialty task, invoke the routed medical-* skill rather than keeping the aggregate skill active."
---

# MAS Scholar Skills

Use this skill as the thin discovery and routing entry for the OPL-owned MAS
medical-paper enhancement pack. Route the task to a concrete `medical-*` skill,
then follow that skill's playbook. Do not copy specialist checklists, CLI
instructions, gallery details, or data-governance rules into this aggregate.

`opl-scholarskills` and `opl.scholarskills.*` are legacy provenance aliases,
not active discovery or authority surfaces.

## Core Routing

| Module | Specialist skill |
| --- | --- |
| `mas-scholar-skills.display` (Scholar Display) | `medical-figure-design`; use `medical-figure-style` for style-only QA or `medical-figure-composer` for existing-panel composition |
| `mas-scholar-skills.tables` (Scholar Tables) | `medical-table-design` |
| `mas-scholar-skills.stats` (Scholar Stats) | `medical-statistical-review` |
| `mas-scholar-skills.lit` (Scholar Lit) | `medical-research-lit` |
| `mas-scholar-skills.write` (Scholar Write) | `medical-manuscript-writing` |
| `mas-scholar-skills.review` (Scholar Review) | `medical-manuscript-review` |
| `mas-scholar-skills.submit` (Scholar Submit) | `medical-submission-prep` |
| `mas-scholar-skills.data` (Medical Data Governance) | `medical-data-governance` |

Start from the MAS overlay or stage operating prompt when one exists. It owns
stage validity, evidence thresholds, route-back, and acceptance. Use the routed
specialist for professional judgment and candidate handoff preparation.

## Optional Routing

Use optional skills only for a named specialty that the core skills do not
cover. Start from the closest router/reviewer:

- `medical-methodology-planner`
- `medical-evidence-integrity-reviewer`
- `medical-publication-routeback-reviewer`
- `medical-advanced-biomed-router`

Let that router select one narrow optional skill. Missing optional skills do
not block ordinary MAS medical-paper work. OPL Framework and OPL Connect own
installation, sync, CLI, connector access, and runtime bridge behavior; this
aggregate only identifies the route.

## Handoff And Authority

Use the shared refs-only handoff family when the routed skill prepares a
handoff: `source_pack_ref`, `candidate_refs`, and
`owner_gate_handoff_ref`.

MAS Scholar Skills may prepare candidate refs, quality hints, candidate
packages, and route-back recommendations. It must not write domain or study
truth, mutate authoritative artifacts or clinical data bodies, sign owner
receipts, create typed blockers, accept citations, update current packages, or
claim runtime, quality, artifact, publication, owner, or production readiness.
MAS or the consuming domain owner must consume, reject, or route back the
candidate through its own authority surface.

## Owner References

Read only the reference needed for the task:

- Module ids, exposure policy, optional specialist inventory, and machine
  authority flags: `contracts/scholar-skills-capability-modules.json` and
  `contracts/capability_map.json`.
- Stage, specialist, connector, contract, and runtime ownership:
  `docs/mas-scholar-skills-operating-model.md`.
- Shared human-readable owner limits: `docs/no-authority-boundary.md`.
- Human-readable module and CLI/install navigation:
  `docs/capability-modules.md`.
- Shared candidate-ref shapes used by concrete skills:
  `references/professional-quality-ref-templates.md`.
- Detailed quality floors and workflows: the selected `medical-*` skill and
  its directly linked references.

Do not use this aggregate as a second contract, a specialist workflow, or an
authority verdict.
