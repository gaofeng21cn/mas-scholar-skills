---
name: mas-scholar-skills
description: "Route optional MAS medical-paper or MAG medical-grant enhancements to maintained MAS Scholar Skills specialists. Use for pack-level discovery, consumer-profile routing, specialist selection, or refs-only no-authority guidance. Invoke the routed medical-* skill rather than keeping this aggregate active."
---

# MAS Scholar Skills

Use this skill as the thin discovery and routing entry for an OPL-owned
framework capability pack with optional MAS paper and MAG grant profiles. Route
the task through the consuming Agent's own stage overlay to a concrete
`medical-*` skill, then follow that skill's playbook. Do not copy specialist
checklists, CLI instructions, gallery details, or data-governance rules into
this aggregate.

`opl-scholarskills` and `opl.scholarskills.*` are legacy provenance aliases,
not active discovery or authority surfaces.

## Consumer Profiles

- `mas-medical-paper.v1` declares the 11-Skill compatibility set used when MAS
  selects this optional enhancement. It is not a MAS readiness floor.
- `mag-medical-grant.v1` is an optional refs-only enhancement that may use
  `medical-research-lit`,
  `medical-statistical-review`, `medical-methodology-planner`,
  `medical-evidence-integrity-reviewer`,
  `medical-evidence-synthesis-and-claim-map`, and
  `medical-reference-integrity-auditor`.

Both profiles are `required=false` optional enhancements. Missing or
incompatible Skills must fail open to the consuming Agent's native workflow and
may produce only a consumer-owned non-blocking diagnostic. Bundling or
materializing the pack for discovery is allowed, but it must not create an
install, activation, admission, route, launch, or readiness gate. The consuming
Agent owns stage routing and domain acceptance. This pack never calls MAS on
MAG's behalf and never converts a candidate into study or grant truth,
fundability, quality, export/publication readiness, strategy memory, a receipt,
a blocker, or owner authority.

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

Start from the consuming Agent's overlay or stage operating prompt. For MAS,
that is the paper stage prompt; for optional MAG use, it is the native grant
prompt. The consuming prompt owns stage validity, evidence thresholds,
route-back, and acceptance. Use the routed specialist only for professional
judgment and candidate handoff preparation.

For a new or materially repaired paper-facing figure, routing is not complete
until `medical-figure-design` has been consumed and the final export has a
`medical-figure-style` receipt. Use `medical-figure-composer` only for assembly
from separately rendered panels. Figure templates are optional references and
quality floors; they are never mandatory layouts. If hosted discovery is
unavailable, use the currently materialized canonical Skill and record its
identity instead of bypassing the professional workflow.

## Optional Routing

When the pack is bundled or materialized, all exported specialty Skills are
available for native discovery. Use them only when a named specialty is not
covered by the core skills. Start from the closest router/reviewer:

- `medical-methodology-planner`
- `medical-evidence-integrity-reviewer`
- `medical-publication-routeback-reviewer`
- `medical-advanced-biomed-router`

Let that router select one narrow specialty skill. Neither a profile
compatibility set nor a materialized specialty defines consumer readiness.
OPL Framework owns distribution, refresh, scope materialization, CLI, connector
access, and runtime bridge behavior; this aggregate only identifies the route.

## Handoff And Authority

Use the shared refs-only handoff family when the routed skill prepares a
handoff: `source_pack_ref`, `candidate_refs`, and
`owner_gate_handoff_ref`.

MAS Scholar Skills may prepare candidate refs, quality hints, candidate
packages, and route-back recommendations. It must not write domain or study
truth, mutate authoritative artifacts or clinical data bodies, sign owner
receipts, create typed blockers, accept citations, update current packages, or
claim runtime, quality, artifact, publication, owner, or production readiness.
MAS, MAG, or another consuming domain owner must consume, reject, or route back
the candidate through its own authority surface.

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
