### Medical Initial-Draft Preflight

Before producing a complete initial draft, build
`medical_initial_draft_preflight_candidate_ref` against
`contracts/scholarskills-medical-initial-draft-preflight-candidate-v1.schema.json`
and run `validate_medical_initial_draft_preflight_candidate_v3()` when the local
kernel is available. The v1 and v2 validators remain available only for
same-major compatibility with already-produced candidates; new initial drafts
use the v3 semantic policy. The candidate must reconcile seven structural
gates: study identity, data freeze, statistical integrity, citation integrity,
table traceability, display scope, and story contract. The story-contract gate
also binds `author_stance_integrity_ref`, combining reader-facing
workflow-language lint with exact `author_input_registry_ref` closure. Pending
names, affiliations, ethics identifiers, funding, disclosures, or journal
metadata remain local `[AUTHOR INPUT: ...]` annotations and never justify
defensive manuscript prose. Every satisfied gate carries at least one
non-empty exact ref; every route-back gate binds its unresolved item ids; an
inapplicable gate carries a reason and no unresolved item. File presence,
provider completion, or a successful render is not a substitute for these refs.

A satisfied gate must cover every required ref family declared by the package
policy, not merely contain one arbitrary exact ref. Statistical integrity also
requires one explicit fixed-horizon applicability disposition and one decision-
curve applicability disposition. The JSON schema validates the stable v1 shape;
`validate_medical_initial_draft_preflight_candidate_v3()` is mandatory for
current ref-kind family, author-stance, and conditional-disposition semantics.
When either analysis is genuinely inapplicable, use
`build_medical_initial_draft_applicability_disposition()` and bind its canonical
content identity with `medical_initial_draft_applicability_disposition_exact_ref()`.
The v3 preflight validator must receive the disposition candidates and rejects
arbitrary, reused, stale, target-mismatched, or authority-bearing placeholder
refs.
For `initial_complete_draft`, the applicability matrix marks all seven gates
required: no required gate, especially study identity, data freeze, or story
contract, may use `not_applicable_with_reason`, and an aggregate `satisfied`
state cannot contain a required-gate N/A disposition.

Order unresolved work by its owning dependency, not by the order in which it
was noticed: `baseline_data_citation` routes to
`baseline_and_evidence_setup`, `analysis` to `bounded_analysis_campaign`,
`authoring_display` to `manuscript_authoring`, and `review` to
`review_and_quality_gate`. The earliest unresolved canonical owner is the only
`earliest_route_back_owner`; do not trust a caller-supplied alternative.

When the preflight routes back, limit authoring to the story plan, section
contracts, and narrowly bounded candidate prose supported by satisfied gates.
Do not generate or label a complete initial draft from unresolved upstream
identity, data, statistical, citation, table, or display evidence. The
preflight remains refs-only and cannot authorize a full draft, sign an owner
receipt, create a typed blocker, or claim quality/publication readiness.

Run `audit_applicable_initial_draft_specialist_refs()` before placing an
applicable fixed-horizon or external-validation candidate into the seven-gate
preflight. An ordinary initial draft with neither condition requires none of
these specialist refs. A fixed-horizon draft consumes
`fixed_horizon_risk_semantics_ref`; every fixed-horizon or external-validation
draft consumes `verification_scope_contract_ref`; when
`analysis_input_anomaly_inventory_ref` records material anomalies, consume
`anomaly_sensitivity_ref`. An external-validation draft also consumes
`construct_comparability_ref`, `claim_family_scope_qualifier_ref`, and its
model/performance/claim refs. When paper-facing displays exist, consume
`structured_display_source_map_ref` and the active display producer's
`single_generation_source_ref`, `deterministic_render_ref`,
`clean_rebuild_consistency_ref`, and output fingerprints, then aggregate them
as `renderer_provenance_ref` for `medical-manuscript-review`.

For final reader outputs, consume `post_csl_reader_semantics_ref` after the
actual DOCX/PDF citeproc build, and consume `figure_numbering_one_owner_ref`
after final composition. Bibliography keys, source braces, caption source, or a
clean image cannot replace these reader-facing checks. Protected names,
literal group authors, corrections, and official metadata must match the
canonical semantic inventory; every figure and output surface must have one
declared numbering owner and exactly one final label.

When a reviewer response discusses an anomaly sensitivity, build
`anomaly_evidence_parity_ref` before freezing the revision. Manuscript,
supplement, and reviewer response must repeat the same structured flagged
count, extreme-value count, threshold status, source-mutation status, and exact
result deltas. A wording-only response that omits one of these fields is not an
evidence-parallel revision.

Only after the seven-gate preflight is satisfied and the manuscript,
structured evidence, claim map, tables, and figures have been generated, run
`build_authoring_freeze_handoff_candidate()` to produce
`immutable_candidate_snapshot_ref`. Bind the exact generated candidate plus
renderer provenance submitted for independent review and provide an explicit
`immutable_candidate_snapshot_manifest_locator`. The locator identifies the
canonical member manifest but is excluded from snapshot content identity, so a
locator move alone cannot change or prove the frozen bytes. A numeric,
semantic, source, render-request, member, or output change requires a new
authoring candidate snapshot. This downstream writing ref is refs-only and no-authority: it
does not sign an immutable reviewer snapshot, decide review currentness,
invalidate a prior receipt, accept an artifact, or claim readiness. MAS/OPL and the
consuming domain owner retain those decisions. Pass the authoring-freeze ref to
`medical-manuscript-review` only through its immutable reviewer input snapshot.

