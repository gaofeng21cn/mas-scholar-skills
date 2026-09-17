# MAS Scholar Skills No-Authority Boundary

Owner: `One Person Lab`
Purpose: Shared human-readable boundary reference for README and Skill guidance.
State: `active_boundary_ref`
Machine boundary: Machine truth remains in `contracts/capability_map.json#/authority_boundary`, `contracts/capability_map.json#/owner_closeout_boundary`, `contracts/scholar-skills-capability-modules.json#/standard_handoff_ref_families`, and each module authority boundary in `contracts/scholar-skills-capability-modules.json`.

## Canonical Rule

MAS Scholar Skills is a refs-only, authority-false capability pack. It may prepare
`candidate_refs`, quality hints, `verdict_candidate`, `route_back_candidate`,
`stop_or_continue_recommendation`, and `owner_gate_handoff_ref` for a consuming
domain owner gate.

It must not write domain truth, runtime state, artifact bodies, ledgers, current
packages, owner receipts, typed blockers, human gates, quality verdicts, owner
acceptance, artifact authority, publication readiness, runtime readiness, or
production readiness. OPL validates, installs, syncs, and reads the package. OPL
Connect may run the package's pure reference-provider state machine, but Connect
itself performs every HTTP request and materializes any strict match or receipt;
the package cannot perform I/O, materialize a candidate artifact, or create a
verdict or receipt.

For MAS and MAG, this boundary also forbids study or grant truth, fundability,
quality or export verdicts, strategy-memory writes, consumer typed blockers, and
owner authority. Individual named specialty Skills remain task-selected, and a
missing required dependency edge grants this package no blocker authority over
the consumer or over unrelated Packages; the
[operating model](./mas-scholar-skills-operating-model.md) owns that dependency
semantics.

## Active Surfaces

The active professional modules, their backing skills, and the two machine
companion modules are owned by [the capability catalog](./capability-modules.md)
and `contracts/scholar-skills-capability-modules.json`. `medical-figure-style`
and `medical-figure-composer` are display subskills, not additional active
modules.

Each module uses the standard refs-only handoff family: `source_pack_ref`,
`candidate_refs`, and `owner_gate_handoff_ref`.

Optional advanced and medical-method specialist skills are named-task helpers,
not active module owners. They may emit specialty candidate refs, support maps,
`route_back_candidate`, and `owner_gate_handoff_ref`; their absence does not block
default medical-paper work. Retired optional ids resolve to redirect tombstones
under `tombstones/skills/` and are not discoverable `SKILL.md` surfaces.

The machine companion modules are not professional Skills or Stage owners. They
keep network, environment, filesystem, process, receipt, verdict, blocker,
reference-truth, and domain-authority flags false; their ABIs and provider
coverage are owned by [the capability catalog](./capability-modules.md).

## Owner Route

Any `owner_receipt_ref`, `typed_blocker_ref`, `reviewer_receipt_ref`,
`route_back_evidence_ref`, or current-package ref named by this pack is a
downstream owner-consumption target only. MAS, MAG, or the consuming domain owner
must consume candidate refs and issue any receipt, blocker, route-back, package
update, artifact mutation, grant decision, or publication decision from its own
authority surface.

MAS `agent/stages/` and `agent/prompts/` own stage policy, evidence thresholds,
route-back, owner gates, and acceptance. A `medical-*` skill owns its AI-first
playbook and candidate handoff, and the
[operating model](./mas-scholar-skills-operating-model.md) owns the provider
execution split. None of those provider outputs is paper truth. The contract
owns ids, profile/registry bindings, ref vocabulary, false-authority flags, and
sync policy.

Journal-family quality-pack refs remain foldback routes into existing active
skills, not new physical skills or MAS authority surfaces. The compact mapping is
in `references/professional-quality-ref-templates.md#mas-journal-family-pack-foldback`.
