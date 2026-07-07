# MAS Scholar Skills No-Authority Boundary

Owner: `One Person Lab`
Purpose: Shared human-readable boundary reference for README and Skill guidance.
State: `active_boundary_ref`
Machine boundary: Machine truth remains in `contracts/capability_map.json#/authority_boundary`, `contracts/capability_map.json#/owner_closeout_boundary`, `contracts/scholar-skills-capability-modules.json#/standard_handoff_ref_families`, and each module authority boundary in `contracts/scholar-skills-capability-modules.json`.

## Canonical Rule

MAS Scholar Skills is a refs-only, authority false capability pack. It can prepare candidate refs, candidate packages, quality hints, `verdict_candidate`, `route_back_candidate`, `stop_or_continue_recommendation`, and `owner_gate_handoff_ref` for the MAS owner gate.

It must not write domain truth, runtime state, artifact bodies, ledgers, current packages, owner receipt, typed blocker, human gate, quality verdict, owner acceptance, artifact authority, publication readiness, runtime readiness, or production readiness.

## Active Skills

The active professional modules are `display`, `tables`, `stats`, `lit`, `write`, `review`, `submit`, and `data`. They are backed by the syncable real Codex skills `medical-manuscript-writing`, `medical-manuscript-review`, `medical-figure-design`, `medical-figure-style`, `medical-figure-composer`, `medical-research-lit`, `medical-statistical-review`, `medical-table-design`, `medical-submission-prep`, and `medical-data-governance`. `medical-figure-style` and `medical-figure-composer` are display subskills, not additional active modules.

Each module uses the standard refs-only handoff family: `source_pack_ref`, `candidate_package_ref`, `execution_receipt_ref`, and `owner_gate_handoff_ref`.

Optional advanced specialist skills such as `medical-structural-biology`,
`medical-protein-design`, `medical-genomics-foundation-models`,
`medical-single-cell-modeling`, `medical-indication-dossier`,
`research-pdf-evidence-explorer`, and `scientific-compute-runner` are
external specialist helpers, not active module owners. Their absence does not
block the default medical-paper skills or MAS ordinary progress. They may emit
specialty candidate refs and deterministic receipt refs only.

Optional medical-method specialist skills such as
`medical-protocol-and-sap-planner`, `medical-cohort-phenotyping`,
`medical-evidence-synthesis-and-claim-map`,
`medical-reference-integrity-auditor`, `medical-rebuttal-strategy`,
`medical-display-qc`, `medical-causal-inference-plan`, and
`medical-survival-analysis-plan`, plus `medical-risk-model-transportability-reviewer`,
`medical-registry-atlas-story-architect`, `medical-owner-gate-handoff-reviewer`,
`medical-display-regression-debugger`, and
`medical-data-freeze-and-analysis-readiness-reviewer`,
`medical-publication-strategy-memory-curator`, and
`medical-evidence-gap-triage-reviewer`,
`medical-research-portfolio-memory-curator`, and
`medical-methodology-routeback-reviewer`, follow the same boundary.
They may emit candidate refs, support maps, `route_back_candidate`, and
`owner_gate_handoff_ref` for named method tasks; they are not active module owners
and cannot sign owner receipts, create typed blockers, write MAS truth, or claim
source, runtime, publication, or production readiness.

## Owner Route

Any `owner_receipt_ref`, `typed_blocker_ref`, `reviewer_receipt_ref`, `route_back_evidence_ref`, or current-package ref named by MAS Scholar Skills is a downstream owner-consumption target only. MAS or the consuming domain owner must consume the candidate refs and issue any owner receipt, typed blocker, route-back, reviewer receipt, current-package update, artifact mutation, or publication decision from its own authority surface.

Stage prompts in MAS `agent/stages/` and `agent/prompts/` own stage policy, evidence thresholds, route-back, owner gates, and acceptance. A `medical-*` professional specialist skill owns only the AI-first playbook and candidate handoff for its specialty. A Tool connector such as OPL Connect/Fabric owns tool/API access, normalized read-only receipts, and scientific connector source refs such as PubMed/PMC-first refs plus Crossref/OpenAlex fallback refs; those refs are not citation acceptance. A contract module owns ids, maps, ref vocabulary, no-authority flags, and sync policy.

Journal-family quality pack refs such as `journal_response_pack`,
`manuscript_argument_pack`, `statistical_reporting_pack`,
`data_availability_fair_pack`, `citation_integrity_pack`,
`figure_evidence_contract_pack`, `paper_reader_grounding_pack`, and
`paper_presentation_pack` are foldback routes into the existing active skills,
not new physical skills and not MAS authority surfaces. The compact mapping
lives in `references/professional-quality-ref-templates.md#mas-journal-family-pack-foldback`.
