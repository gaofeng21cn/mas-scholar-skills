# MAS Scholar Skills No-Authority Boundary

Owner: `One Person Lab`
Purpose: Shared human-readable boundary reference for README and Skill guidance.
State: `active_boundary_ref`
Machine boundary: Machine truth remains in `contracts/capability_map.json#/authority_boundary`, `contracts/capability_map.json#/owner_closeout_boundary`, `contracts/scholar-skills-capability-modules.json#/standard_handoff_ref_families`, and each module authority boundary in `contracts/scholar-skills-capability-modules.json`.

## Canonical Rule

MAS Scholar Skills is a refs-only, authority-false capability pack. It may prepare
`candidate_refs`, quality hints, `verdict_candidate`, `route_back_candidate`,
`stop_or_continue_recommendation`, and `owner_gate_handoff_ref` for a MAS owner
gate.

It must not write domain truth, runtime state, artifact bodies, ledgers, current
packages, owner receipts, typed blockers, human gates, quality verdicts, owner
acceptance, artifact authority, publication readiness, runtime readiness, or
production readiness. OPL only validates, installs, syncs, and reads the package
descriptor; it does not run a module, materialize a candidate artifact, or create
a module receipt for this pack.

## Active Skills

The active professional modules are `display`, `tables`, `stats`, `lit`, `write`,
`review`, `submit`, and `data`. They are backed by the syncable real Codex skills
`medical-manuscript-writing`, `medical-manuscript-review`,
`medical-figure-design`, `medical-figure-style`, `medical-figure-composer`,
`medical-research-lit`, `medical-statistical-review`, `medical-table-design`,
`medical-submission-prep`, and `medical-data-governance`. `medical-figure-style`
and `medical-figure-composer` are display subskills, not additional active modules.

Each module uses the standard refs-only handoff family: `source_pack_ref`,
`candidate_refs`, and `owner_gate_handoff_ref`.

Optional advanced and medical-method specialist skills are named-task helpers,
not active module owners. They may emit specialty candidate refs, support maps,
`route_back_candidate`, and `owner_gate_handoff_ref`; their absence does not block
default medical-paper work. Retired optional ids remain redirect tombstones only,
not discoverable `SKILL.md` surfaces.

## Owner Route

Any `owner_receipt_ref`, `typed_blocker_ref`, `reviewer_receipt_ref`,
`route_back_evidence_ref`, or current-package ref named by this pack is a
downstream owner-consumption target only. MAS or the consuming domain owner must
consume candidate refs and issue any receipt, blocker, route-back, package update,
artifact mutation, or publication decision from its own authority surface.

MAS `agent/stages/` and `agent/prompts/` own stage policy, evidence thresholds,
route-back, owner gates, and acceptance. A `medical-*` skill owns its AI-first
playbook and candidate handoff. For biomedical source lookup, MAS
`research-integrity-reference-verification` owns the PubMed/PMC request and
normalization, returning `mas_provider_lookup_ref` and `pubmed_source_refs` as
read-only evidence inputs. OPL Connect may provide explicit Crossref or OpenAlex
fallback metadata/coverage refs as `fallback_source_refs`; none of these refs is
citation acceptance. The contract owns only ids, ref vocabulary, false-authority
flags, and sync policy.

Journal-family quality-pack refs remain foldback routes into existing active
skills, not new physical skills or MAS authority surfaces. The compact mapping is
in `references/professional-quality-ref-templates.md#mas-journal-family-pack-foldback`.
