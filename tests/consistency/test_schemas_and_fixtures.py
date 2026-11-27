"""Core contract schema invariants, display layout QC fixtures, and semantic artist flow regression fixtures."""

from __future__ import annotations

import json

from tests.consistency._context import (
    fail,
    load_repo_context,
    read_json,
    read_text,
    require_all,
)
def test_contract_and_schema_invariants() -> None:
    ctx = load_repo_context()
    capability_map = ctx.capability_map
    contract = ctx.contract
    initial_draft_preflight_schema = ctx.initial_draft_preflight_schema
    package_manifest = ctx.package_manifest
    page_hash_evidence_schema = ctx.page_hash_evidence_schema
    revision_learning_fixture_refs = ctx.revision_learning_fixture_refs
    root = ctx.root
    read_json("contracts/scientific-search-adapters/scientific-search-adapter-registry.schema.json")
    read_json("contracts/scientific-search-adapters/scientific-search-adapter-step.schema.json")
    classification_policy = contract.get("capability_module_classification_policy") or {}
    json.dumps(contract, ensure_ascii=False)
    retired_execution_projection_fields = [
        "runtime_environment_bridge",
        "opl_consumption_projection_policy",
        "opl_consumption_validation_policy",
        "candidate_artifact_engine_policy",
    ]
    for field in retired_execution_projection_fields:
        if field in contract:
            fail(f"contract must retire {field} in favor of generic capability-pack consumption")

    snapshot_evidence_policy = contract.get("reviewer_snapshot_and_page_evidence_policy") or {}
    expected_snapshot_reviewer_skills = [
        "medical-manuscript-review",
        "medical-statistical-review",
        "medical-reference-integrity-auditor",
        "medical-display-qc",
        "medical-submission-prep",
    ]
    if snapshot_evidence_policy.get("reviewer_skill_ids") != expected_snapshot_reviewer_skills:
        fail("reviewer snapshot policy must cover the five canonical reviewer skills")
    if snapshot_evidence_policy.get("snapshot_manifest_surface_kind") != "opl_reviewer_input_snapshot_manifest":
        fail("reviewer snapshot policy must consume the OPL immutable snapshot manifest")
    if snapshot_evidence_policy.get("snapshot_read_policy") != "read_only_opl_immutable_snapshot_refs_never_live_workspace_locators":
        fail("reviewer snapshot policy must forbid live locator reads")
    page_evidence_policy = snapshot_evidence_policy.get("page_hash_evidence_candidate") or {}
    if page_evidence_policy.get("surface_kind") != "scholarskills_page_hash_evidence_candidate":
        fail("page evidence candidate must use the canonical ScholarSkills surface kind")
    if page_evidence_policy.get("schema_version") != 3:
        fail("page evidence candidate must use the owner-published schema 3")
    if page_evidence_policy.get("schema_owner") != "mas-scholar-skills":
        fail("page evidence candidate schema owner must be mas-scholar-skills")
    if page_evidence_policy.get("schema_ref") != "contracts/scholarskills-page-hash-evidence-candidate-v3.schema.json":
        fail("page evidence candidate must reference the ScholarSkills-owned schema")
    expected_page_hash_fields = {
        "surface_kind",
        "schema_version",
        "review_scope_sha256",
        "rubric_sha256",
        "evidence_payload",
        "cache_key_sha256",
        "origin_reviewer_evidence_ref",
    }
    if set(page_evidence_policy.get("candidate_fields") or []) != expected_page_hash_fields:
        fail("page evidence policy fields must match schema 3 ABI")
    if page_evidence_policy.get("evidence_payload_fields") != ["raster_contract", "pages"]:
        fail("page evidence candidate payload must contain raster contract and pages")
    if page_evidence_policy.get("cache_key_fields") != [
        "ordered_page_pixel_hashes",
        "raster_contract",
        "review_scope_sha256",
        "rubric_sha256",
    ]:
        fail("page evidence key must bind ordered pixels, raster contract, scope, and rubric")
    if page_evidence_policy.get("origin_reviewer_evidence_ref_policy") != "nullable_provenance_only":
        fail("page evidence origin ref must remain nullable provenance only")
    if page_evidence_policy.get("currentness_policy") != "content_identity_and_origin_provenance_do_not_establish_review_currentness":
        fail("page evidence policy must keep currentness outside content identity")
    expected_composed_pdf_pairs = [
        {
            "filename": "paper.pdf",
            "role": "selected_layout_main_manuscript",
            "required_when": "requires_reader_pdf",
        },
        {
            "filename": "paper_with_supplementary.pdf",
            "role": "reader_combined_main_and_supplementary",
            "required_when": "supplement_applicable",
        },
    ]
    if snapshot_evidence_policy.get("composed_pdf_exact_pairs") != expected_composed_pdf_pairs:
        fail("reviewer snapshot policy must bind the two canonical composed PDF filename/role pairs")
    if snapshot_evidence_policy.get("expected_display_member_identity_fields") != [
        "member_id",
        "role",
    ]:
        fail("reviewer snapshot policy must identify expected displays by member_id and role")
    if snapshot_evidence_policy.get("expected_main_display_member_roles") != [
        "main_figure",
        "main_table",
    ]:
        fail("reviewer snapshot policy must cover expected main figure and table members")
    if snapshot_evidence_policy.get("expected_members_must_close_in") != [
        "snapshot_inventory",
        "audit_inventory",
    ]:
        fail("reviewer snapshot policy must close every display member in snapshot and audit")
    if snapshot_evidence_policy.get("role_membership_can_replace_member_identity") is not False:
        fail("reviewer snapshot policy must not let a role replace display member identity")
    expected_display_scope_exact_refs = [
        "canonical_manuscript_ref",
        "table_catalog_ref",
        "figure_catalog_ref",
        "caption_legend_manifest_ref",
        "render_environment_ref",
        "font_inventory_ref",
        "composed_paper_pdf_exact_ref",
    ]
    if snapshot_evidence_policy.get("display_scope_required_exact_ref_fields") != expected_display_scope_exact_refs:
        fail("reviewer snapshot policy must bind the complete document display exact-ref scope")
    if snapshot_evidence_policy.get("display_scope_page_evidence_any_of") != [
        "page_render_evidence_ref",
        "page_hash_evidence_candidate_ref",
    ]:
        fail("reviewer snapshot policy must require page-render or page-hash evidence")
    if snapshot_evidence_policy.get("audit_inventory_can_replace_page_render_or_hash_evidence") is not False:
        fail("reviewer snapshot audit inventory must not replace page-render/page-hash evidence")

    expected_preflight_statuses = [
        "satisfied",
        "route_back_required",
        "not_applicable_with_reason",
    ]
    expected_preflight_gates = [
        "study_identity",
        "data_freeze",
        "statistical_integrity",
        "citation_integrity",
        "table_traceability",
        "display_scope",
        "story_contract",
    ]
    expected_preflight_dependency_order = [
        {
            "tier": "baseline_data_citation",
            "rank": 10,
            "owner": "baseline_and_evidence_setup",
        },
        {
            "tier": "analysis",
            "rank": 20,
            "owner": "bounded_analysis_campaign",
        },
        {
            "tier": "authoring_display",
            "rank": 30,
            "owner": "manuscript_authoring",
        },
        {
            "tier": "review",
            "rank": 40,
            "owner": "review_and_quality_gate",
        },
    ]
    preflight_policy = contract.get("medical_initial_draft_preflight_policy") or {}
    if capability_map.get("medical_initial_draft_preflight_policy") != preflight_policy:
        fail("capability map and canonical module contract must expose one identical initial-draft preflight policy")
    if preflight_policy.get("policy_id") != "scholarskills_medical_initial_draft_preflight.v3":
        fail("initial-draft preflight policy id is missing")
    if preflight_policy.get("schema_ref") != "contracts/scholarskills-medical-initial-draft-preflight-candidate-v1.schema.json":
        fail("initial-draft preflight policy must point to the owner schema")
    if preflight_policy.get("schema_version") != 1:
        fail("initial-draft preflight policy must freeze schema version 1")
    if preflight_policy.get("surface_kind") != "medical_initial_draft_preflight_candidate_ref":
        fail("initial-draft preflight policy surface kind is wrong")
    if preflight_policy.get("stable_v1_compatibility") != {
        "structural_schema_unchanged": True,
        "legacy_validator": "validate_medical_initial_draft_preflight_candidate",
        "prior_semantic_validator": "validate_medical_initial_draft_preflight_candidate_v2",
        "current_semantic_validator": "validate_medical_initial_draft_preflight_candidate_v3",
    }:
        fail("initial-draft preflight policy must preserve the stable v1 validator")
    if preflight_policy.get("statuses") != expected_preflight_statuses:
        fail("initial-draft preflight policy statuses are wrong")
    if preflight_policy.get("gates") != expected_preflight_gates:
        fail("initial-draft preflight policy gates are wrong")
    if preflight_policy.get("canonical_dependency_order") != expected_preflight_dependency_order:
        fail("initial-draft preflight policy dependency owner order is wrong")
    if preflight_policy.get("gate_ref_families") != {
        "study_identity": ["study_charter_ref", "paper_identity_ref"],
        "data_freeze": ["clinical_analysis_input_identity_ref"],
        "statistical_integrity": [
            "validation_partition_integrity_ref",
            "endpoint_analysis_set_reconciliation_ref",
            "model_complexity_sparse_event_ref",
            "linked_prediction_performance_ref",
        ],
        "citation_integrity": [
            "citation_source_coverage_ref",
            "active_reference_currentness_ref",
            "excluded_reference_ledger_ref",
            "claim_citation_edge_completeness_ref",
            "reference_lane_active_inventory_binding_ref",
        ],
        "table_traceability": ["baseline_table_traceability_ref"],
        "display_scope": [
            "document_display_scope_coverage_ref",
            "display_render_integrity_ref",
        ],
        "story_contract": [
            "first_draft_story_contract_ref",
            "author_stance_integrity_ref",
        ],
    }:
        fail("initial-draft preflight policy gate ref families are wrong")
    if preflight_policy.get("conditional_gate_ref_families") != {
        "statistical_integrity": [
            ["fixed_horizon_risk_semantics_ref", "fixed_horizon_not_applicable_ref"],
            ["decision_curve_validity_ref", "decision_curve_not_applicable_ref"],
        ]
    }:
        fail("initial-draft preflight conditional ref families are wrong")
    if preflight_policy.get("manuscript_mode_applicability") != {
        "initial_complete_draft": {
            gate_name: "required" for gate_name in expected_preflight_gates
        }
    }:
        fail("initial-draft preflight manuscript-mode applicability is wrong")
    if preflight_policy.get("schema_validation_scope") != "structural_shape_and_exact_ref_only":
        fail("initial-draft preflight schema scope must stay structural")
    if preflight_policy.get("semantic_family_validation") != {
        "mandatory": True,
        "kernel": "skills/medical-manuscript-writing/kernel.py",
        "function": "validate_medical_initial_draft_preflight_candidate_v3",
    }:
        fail("initial-draft preflight semantic family kernel must be mandatory")
    if preflight_policy.get("producer_skill_id") != "medical-manuscript-writing":
        fail("initial-draft preflight producer must be medical-manuscript-writing")
    if preflight_policy.get("independent_review_consumer_skill_id") != "medical-manuscript-review":
        fail("initial-draft preflight independent consumer must be medical-manuscript-review")
    if preflight_policy.get("provider_or_render_completion_can_satisfy_preflight") is not False:
        fail("provider or render completion must not satisfy initial-draft preflight")
    if preflight_policy.get("route_back_full_draft_policy") != "route_back_required_limits_output_to_story_plan_section_contracts_and_bounded_candidate_prose":
        fail("route-back preflight must limit output rather than authorize a full draft")
    expected_applicability_disposition_policy = {
        "surface_kind": "medical_initial_draft_applicability_disposition_candidate.v1",
        "schema_version": 1,
        "producer_function": "build_medical_initial_draft_applicability_disposition",
        "validator_function": "validate_medical_initial_draft_applicability_disposition",
        "exact_ref_function": "medical_initial_draft_applicability_disposition_exact_ref",
        "binding_policy": "strict_v2_validates_candidate_content_target_and_canonical_size_sha_ref_identity",
        "authority": False,
    }
    if preflight_policy.get("applicability_disposition_policy") != expected_applicability_disposition_policy:
        fail("canonical contract applicability disposition policy is wrong")
    if (
        (capability_map.get("medical_initial_draft_preflight_policy") or {}).get(
            "applicability_disposition_policy"
        )
        != expected_applicability_disposition_policy
    ):
        fail("capability map applicability disposition policy is wrong")
    preflight_authority = preflight_policy.get("authority_boundary") or {}
    if preflight_authority != {
        "refs_only": True,
        "can_write_domain_truth": False,
        "can_sign_owner_receipt": False,
        "can_create_typed_blocker": False,
        "can_claim_quality_verdict": False,
        "can_claim_publication_readiness": False,
        "can_authorize_full_draft": False,
    }:
        fail("initial-draft preflight policy must remain refs-only and no-authority")

    revision_learning_policy = contract.get("revision_learning_delta_policy") or {}
    if capability_map.get("revision_learning_delta_policy") != revision_learning_policy:
        fail("capability map and canonical contract must expose one revision-learning policy")
    if revision_learning_policy.get("policy_id") != "scholarskills_revision_learning_delta.v1":
        fail("revision-learning policy id is wrong")
    expected_learning_ids = [
        "REV-LEARN-009",
        "REV-LEARN-010",
        "REV-LEARN-011",
        "REV-LEARN-012",
        "REV-LEARN-013",
    ]
    if revision_learning_policy.get("learning_ids") != expected_learning_ids:
        fail("revision-learning policy must expose REV-LEARN-009 through 013 in order")
    if revision_learning_policy.get("semantic_qa_policy") != {
        "structured_fields_required": True,
        "fixture_values_define_expected_semantics": True,
        "single_english_wording_can_satisfy": False,
    }:
        fail("revision-learning semantic QA must be structured and wording independent")
    revision_learning_rules = revision_learning_policy.get("rules") or {}
    if set(revision_learning_rules) != set(expected_learning_ids):
        fail("revision-learning policy rule set is incomplete")
    expected_revision_validators_and_fixtures = {
        "REV-LEARN-009": (
            [
                "validate_governed_source_reconstruction",
                "validate_recoverable_gap_disposition",
            ],
            revision_learning_fixture_refs[0],
        ),
        "REV-LEARN-010": (
            ["validate_construct_comparability_currentness"],
            revision_learning_fixture_refs[1],
        ),
        "REV-LEARN-011": (
            ["validate_post_csl_reader_semantics"],
            revision_learning_fixture_refs[2],
        ),
        "REV-LEARN-012": (
            [
                "validate_figure_numbering_one_owner",
                "validate_submission_figure_numbering_binding",
            ],
            revision_learning_fixture_refs[3],
        ),
        "REV-LEARN-013": (
            ["validate_anomaly_evidence_parity"],
            revision_learning_fixture_refs[4],
        ),
    }
    for learning_id, (validators, fixture_ref) in expected_revision_validators_and_fixtures.items():
        rule = revision_learning_rules.get(learning_id) or {}
        if rule.get("validator_functions") != validators:
            fail(f"{learning_id} validator functions are wrong")
        if rule.get("fixture_ref") != fixture_ref:
            fail(f"{learning_id} fixture ref is wrong")
    if revision_learning_rules["REV-LEARN-009"].get("reconstructed_gap_policy") != "close_gap_and_remove_limitation_and_human_todo":
        fail("REV-LEARN-009 must close reconstructed gaps and remove stale TODOs")
    if revision_learning_rules["REV-LEARN-010"].get("evidence_layers") != [
        "codebook",
        "identity_linkage",
        "field_role",
        "accepted_mapping",
        "current_evidence",
    ]:
        fail("REV-LEARN-010 must preserve five separate construct evidence layers")
    if revision_learning_rules["REV-LEARN-010"].get("source_recovery_can_authorize_estimation") is not False:
        fail("REV-LEARN-010 source recovery cannot authorize estimation")
    if revision_learning_rules["REV-LEARN-011"].get("required_output_surfaces") != ["docx", "pdf"]:
        fail("REV-LEARN-011 must audit both final DOCX and PDF")
    if revision_learning_rules["REV-LEARN-011"].get("official_metadata_exact_ref_required") is not True:
        fail("REV-LEARN-011 must bind official metadata as exact refs")
    if revision_learning_rules["REV-LEARN-012"].get("numbering_sources") != [
        "image_alt_text",
        "structured_legend_text",
        "renderer_caption_prefix",
    ]:
        fail("REV-LEARN-012 must account for all three numbering sources")
    if revision_learning_rules["REV-LEARN-012"].get("final_occurrence_cardinality") != 1:
        fail("REV-LEARN-012 final figure labels must have cardinality one")
    if revision_learning_rules["REV-LEARN-013"].get("required_output_surfaces") != [
        "manuscript",
        "supplement",
        "reviewer_response",
    ]:
        fail("REV-LEARN-013 must close all three evidence surfaces")
    if revision_learning_rules["REV-LEARN-013"].get("parity_fields") != [
        "flagged_count",
        "extreme_value_count",
        "threshold_status",
        "source_mutation_status",
        "result_deltas",
    ]:
        fail("REV-LEARN-013 parity fields are incomplete")
    if revision_learning_policy.get("authoring_snapshot_manifest_policy") != {
        "builder_function": "build_authoring_freeze_handoff_candidate",
        "locator_output_field": "immutable_candidate_snapshot_manifest_locator",
        "locator_kind": "authoring_candidate_snapshot_manifest",
        "locator_required": True,
        "locator_in_content_identity": False,
    }:
        fail("authoring snapshot must expose a locator outside content identity")
    if revision_learning_policy.get("receipt_supersedence_policy") != {
        "validator_function": "validate_receipt_version_member_delta",
        "fixture_ref": revision_learning_fixture_refs[5],
        "previous_and_current_receipt_exact_refs_required": True,
        "member_delta_classes": ["added", "removed", "changed", "unchanged"],
        "digest_or_summary_can_replace_member_delta": False,
    }:
        fail("receipt supersedence must expose exact refs and normalized member delta")
    if revision_learning_policy.get("authority_boundary") != {
        "refs_only": True,
        "can_write_domain_truth": False,
        "can_mutate_artifact_body": False,
        "can_sign_owner_receipt": False,
        "can_create_typed_blocker": False,
        "can_claim_quality_verdict": False,
        "can_claim_publication_readiness": False,
        "can_claim_current_package_authority": False,
    }:
        fail("revision-learning policy must remain refs-only and no-authority")

    preflight_defs = initial_draft_preflight_schema.get("$defs") or {}
    if (
        (initial_draft_preflight_schema.get("properties") or {})
        .get("surface_kind", {})
        .get("const")
        != "medical_initial_draft_preflight_candidate_ref"
    ):
        fail("initial-draft preflight schema must freeze the candidate surface kind")
    if initial_draft_preflight_schema.get("additionalProperties") is not False:
        fail("initial-draft preflight schema must reject unknown top-level fields")
    if set((preflight_defs.get("status") or {}).get("enum") or []) != set(expected_preflight_statuses):
        fail("initial-draft preflight schema statuses must match policy")
    if (
        (initial_draft_preflight_schema.get("properties") or {})
        .get("manuscript_mode", {})
        .get("minLength")
        != 1
    ):
        fail("stable v1 preflight schema must retain non-empty manuscript-mode compatibility")
    gate_items_schema = (
        (initial_draft_preflight_schema.get("properties") or {}).get("gate_items") or {}
    )
    if set((gate_items_schema.get("properties") or {}).keys()) != set(expected_preflight_gates):
        fail("initial-draft preflight schema gate properties must match policy")
    if set(gate_items_schema.get("required") or []) != set(expected_preflight_gates):
        fail("initial-draft preflight schema must require every policy gate")
    gate_item_schema = preflight_defs.get("gate_item") or {}
    gate_disposition_rules = {}
    for rule in gate_item_schema.get("allOf") or []:
        status = (
            (rule.get("if") or {})
            .get("properties", {})
            .get("status", {})
            .get("const")
        )
        if status:
            gate_disposition_rules[status] = (rule.get("then") or {}).get("properties") or {}
    if set(gate_disposition_rules) != set(expected_preflight_statuses):
        fail("initial-draft preflight gate schema must encode all three dispositions")
    satisfied_gate_rule = gate_disposition_rules["satisfied"]
    if (satisfied_gate_rule.get("refs") or {}).get("minItems") != 1:
        fail("satisfied initial-draft gate must require at least one exact ref")
    if (satisfied_gate_rule.get("unresolved_item_ids") or {}).get("maxItems") != 0:
        fail("satisfied initial-draft gate must forbid unresolved ids")
    if (satisfied_gate_rule.get("not_applicable_reason") or {}).get("type") != "null":
        fail("satisfied initial-draft gate must forbid an N/A reason")
    route_back_gate_rule = gate_disposition_rules["route_back_required"]
    if (route_back_gate_rule.get("unresolved_item_ids") or {}).get("minItems") != 1:
        fail("route-back initial-draft gate must require unresolved ids")
    if (route_back_gate_rule.get("not_applicable_reason") or {}).get("type") != "null":
        fail("route-back initial-draft gate must forbid an N/A reason")
    not_applicable_gate_rule = gate_disposition_rules["not_applicable_with_reason"]
    if (not_applicable_gate_rule.get("unresolved_item_ids") or {}).get("maxItems") != 0:
        fail("N/A initial-draft gate must forbid unresolved ids")
    if (not_applicable_gate_rule.get("not_applicable_reason") or {}).get("minLength") != 1:
        fail("N/A initial-draft gate must require a non-empty reason")
    if (preflight_defs.get("exact_ref") or {}).get("properties", {}).get("size_bytes", {}).get("minimum") != 1:
        fail("initial-draft exact refs must contain at least one byte")
    schema_owner_map = {}
    for rule in (preflight_defs.get("unresolved_item") or {}).get("allOf") or []:
        tier = (
            (rule.get("if") or {})
            .get("properties", {})
            .get("dependency_tier", {})
            .get("const")
        )
        then_properties = (rule.get("then") or {}).get("properties") or {}
        if tier:
            schema_owner_map[tier] = {
                "rank": (then_properties.get("dependency_rank") or {}).get("const"),
                "owner": (then_properties.get("route_back_owner") or {}).get("const"),
            }
    if schema_owner_map != {
        item["tier"]: {"rank": item["rank"], "owner": item["owner"]}
        for item in expected_preflight_dependency_order
    }:
        fail("initial-draft schema owner mapping must match canonical policy")
    schema_authority_properties = (
        (preflight_defs.get("authority_boundary") or {}).get("properties") or {}
    )
    if {key: value.get("const") for key, value in schema_authority_properties.items()} != {
        "refs_only": True,
        "can_write_domain_truth": False,
        "can_sign_owner_receipt": False,
        "can_create_typed_blocker": False,
        "can_claim_quality_verdict": False,
        "can_claim_publication_readiness": False,
        "can_authorize_full_draft": False,
    }:
        fail("initial-draft preflight schema must encode the no-authority boundary")
    if page_hash_evidence_schema.get("additionalProperties") is not False:
        fail("page evidence candidate owner schema must reject unknown top-level fields")
    if set(page_hash_evidence_schema.get("required") or []) != expected_page_hash_fields:
        fail("page evidence candidate owner schema required fields do not match schema 3 ABI")
    if set((page_hash_evidence_schema.get("properties") or {}).keys()) != expected_page_hash_fields:
        fail("page evidence candidate owner schema properties do not match schema 3 ABI")
    if (
        (page_hash_evidence_schema.get("properties") or {})
        .get("schema_version", {})
        .get("const")
        != 3
    ):
        fail("page evidence candidate owner schema must freeze schema_version 3")
    origin_ref_schema = (page_hash_evidence_schema.get("$defs") or {}).get("origin_ref") or {}
    if origin_ref_schema.get("additionalProperties") is not False:
        fail("page evidence origin exact ref must reject unknown fields")
    if set(origin_ref_schema.get("required") or []) != {
        "kind",
        "ref",
        "size_bytes",
        "sha256",
    }:
        fail("page evidence origin exact ref must bind kind, ref, size, and digest")
    if (root / "contracts/scholarskills-page-hash-evidence-candidate-v2.schema.json").exists():
        fail("retired page evidence candidate schema 2 must be absent")
    if (root / "contracts/scholar-skills-opl-consumption-projection.json").exists():
        fail("generated ScholarSkills OPL execution projection must be absent")
    if (root / "scripts/export-opl-consumption-projection.py").exists():
        fail("ScholarSkills execution projection exporter must be absent")
    capability_pack_consumption = contract.get("capability_pack_consumption_policy") or {}
    if capability_pack_consumption.get("policy_id") != "mas_scholar_skills_capability_pack_descriptor.v1":
        fail("contract must declare the generic capability-pack descriptor policy")
    if capability_pack_consumption.get("descriptor_readback_command") != "opl connect skills --domain mas-scholar-skills --json":
        fail("capability-pack descriptor policy must use the generic OPL Connect readback")
    if capability_pack_consumption.get("consumer_role") != "validation_install_sync_and_provenance_only":
        fail("capability-pack descriptor consumer must remain generic and provenance-only")
    expected_capability_skills = classification_policy.get("real_syncable_specialist_skills") or []
    classification_policy.get("optional_external_specialist_skills") or []
    classification_policy.get("optional_medical_method_specialist_skills") or []
    advanced_router_skill_ids = classification_policy.get("optional_external_router_skill_ids") or []
    medical_method_router_skill_ids = classification_policy.get("optional_medical_method_router_skill_ids") or []
    optional_router_skill_ids = [*advanced_router_skill_ids, *medical_method_router_skill_ids]
    optional_named_specialty_skill_ids = classification_policy.get("optional_external_named_specialist_skills") or []
    optional_named_specialty_skill_ids = [
        *optional_named_specialty_skill_ids,
        *(classification_policy.get("optional_medical_method_named_specialist_skills") or []),
    ]
    classification_policy.get("optional_external_redirect_tombstone_skills") or []
    classification_policy.get("optional_medical_method_redirect_tombstone_skills") or []
    aggregate_skill_ids = ["mas-scholar-skills"]
    expected_required_skill_ids = [*aggregate_skill_ids, *expected_capability_skills]
    expected_default_exposure_skill_ids = [*aggregate_skill_ids]
    expected_optional_skill_ids = [*optional_router_skill_ids, *optional_named_specialty_skill_ids]
    expected_all_skill_ids = [*expected_required_skill_ids, *expected_optional_skill_ids]

    if package_manifest.get("surface_kind") != "opl_capability_package_manifest.v2":
        fail("capability package manifest must use opl_capability_package_manifest.v2")
    if package_manifest.get("package_id") != "mas-scholar-skills":
        fail("capability package manifest package_id must be mas-scholar-skills")
    if package_manifest.get("package_role") != "capability_package":
        fail("capability package must use the consumer-neutral capability role")
    if "primary_consumer" in package_manifest:
        fail("framework capability provider must not declare a required primary consumer")
    capability_abi = package_manifest.get("capability_abi") or {}
    if capability_abi.get("id") != "mas-scholar-skills.v1":
        fail("capability package must expose the canonical provider ABI")
    consumer_policy = package_manifest.get("consumer_policy") or {}
    if consumer_policy.get("compatibility_commitment") != "declared_required_consumer_profiles":
        fail("provider compatibility must be bound to declared required consumer profiles")
    if consumer_policy.get("supported_required_by") != ["mas", "mag"]:
        fail("MAS and MAG must be declared as required consumers")
    if consumer_policy.get("non_primary_runtime_dependency_supported") is not True:
        fail("declared consumers must receive a runtime dependency promise")
    package_exports = package_manifest.get("exports") or {}
    if package_exports.get("core_skill_ids") != expected_required_skill_ids:
        fail("capability package core skills must match the required capability closure")
    if package_exports.get("default_materialized_skill_ids") != expected_default_exposure_skill_ids:
        fail("capability package default materialized skills must match the primary routing policy")
    if package_exports.get("specialty_skill_ids") != expected_optional_skill_ids:
        fail("capability package specialty skills must match the canonical optional skill catalog")
    if package_exports.get("all_skill_ids") != expected_all_skill_ids:
        fail("capability package all skills must equal core plus specialty skills")
    expected_module_ids = [module.get("module_id") for module in contract.get("modules") or []]
    if package_exports.get("core_module_ids") != expected_module_ids:
        fail("capability package core modules must match the canonical module catalog order")
    mag_required_skill_ids = [
        "medical-research-lit",
        "medical-statistical-review",
        "medical-methodology-planner",
        "medical-evidence-integrity-reviewer",
        "medical-evidence-synthesis-and-claim-map",
        "medical-reference-integrity-auditor",
    ]
    mag_compatibility_module_ids = [
        "mas-scholar-skills.lit",
        "mas-scholar-skills.stats",
        "mas-scholar-skills.review",
        "mas-scholar-skills.data",
        "mas-scholar-skills.reference-provider-adapters",
        "mas-scholar-skills.scientific-search-adapters",
    ]
    required_profile_common = {
        "profile_kind": "required_refs_only_dependency",
        "required": True,
        "dependency_kind": "required_runtime_dependency",
        "required_ids_semantics": "selected_profile_required_capability_set",
        "missing_or_incompatible_behavior": "consumer_fail_closed",
        "diagnostic_role": "consumer_owned_required_dependency_readiness",
        "distribution_behavior": "consumer_requires_identity_and_capability_callability",
        "blocks_install": True,
        "blocks_activation": True,
        "blocks_admission": True,
        "blocks_route": True,
        "blocks_launch": True,
        "blocks_readiness": True,
        "authority_boundary": {
            "can_write_consumer_domain_truth": False,
            "can_claim_consumer_fundability": False,
            "can_claim_consumer_quality_verdict": False,
            "can_claim_consumer_export_or_publication_readiness": False,
            "can_sign_consumer_owner_receipt": False,
            "can_create_consumer_typed_blocker": False,
            "can_write_consumer_strategy_memory": False,
            "can_claim_consumer_owner_authority": False,
        },
    }
    expected_consumer_profiles = [
        {
            "profile_id": "mas-medical-paper.v1",
            "consumer_agent_id": "mas",
            "required_export_ids": expected_required_skill_ids,
            "required_module_ids": expected_module_ids,
            **required_profile_common,
        },
        {
            "profile_id": "mag-medical-grant.v1",
            "consumer_agent_id": "mag",
            "required_export_ids": mag_required_skill_ids,
            "required_module_ids": mag_compatibility_module_ids,
            **required_profile_common,
        },
    ]
    if package_manifest.get("consumer_profiles") != expected_consumer_profiles:
        fail("MAS and MAG profiles must share required, refs-only, authority-false, fail-closed semantics")
    if "optional_refs_only_consumer_profiles" in package_manifest:
        fail("optional consumer profiles must use the single canonical consumer_profiles surface")
    if any(skill_id not in expected_all_skill_ids for skill_id in mag_required_skill_ids):
        fail("MAG required consumer profile may reference only real exported Skills")

def test_display_layout_and_semantic_artist_fixtures() -> None:
    ctx = load_repo_context()
    display_receipt_templates = ctx.display_receipt_templates
    layout_qc_fixture = ctx.layout_qc_fixture
    semantic_artist_flow_fixture = ctx.semantic_artist_flow_fixture
    workflow_template = ctx.workflow_template
    if workflow_template.get("final_visual_qa_requires") != ["medical-figure-style"]:
        fail("professional figure workflow must require medical-figure-style")
    if (workflow_template.get("conditional_skill_rules") or {}).get(
        "assembled_panels_requires"
    ) != "medical-figure-composer":
        fail("assembled professional figures must require medical-figure-composer")
    template_policy = workflow_template.get("template_policy") or {}
    if template_policy.get("template_use_is_optional") is not True:
        fail("professional figure templates must remain optional")
    if template_policy.get("record_provenance_only_when_template_used") is not True:
        fail("template provenance must be conditional on actual template use")
    semantic_flow_policy = workflow_template.get("semantic_flow_policy") or {}
    for key in [
        "pure_statistical_plot_may_declare_not_applicable",
        "declared_flow_or_schematic_requires_complete_semantic_artist_registry",
        "connector_and_bracket_segments_require_renderer_path_geometry",
        "shared_junction_requires_common_renderer_path_prefix",
        "segmented_band_parent_connector_requires_exact_group_span_contract",
        "segmented_group_requires_full_span_labeled_midpoint_anchor",
        "segmented_group_requires_renderer_bound_actual_path_geometry",
        "unsupported_segmented_group_orientation_or_anchor_mode_fails_closed",
    ]:
        if semantic_flow_policy.get(key) is not True:
            fail(f"professional figure workflow semantic-flow policy must require {key}")
    for key in [
        "text_only_bbox_pass_is_sufficient",
        "hard_coded_zero_violation_counts_allowed",
    ]:
        if semantic_flow_policy.get(key) is not False:
            fail(f"professional figure workflow semantic-flow policy must forbid {key}")
    missing_receipt_policy = workflow_template.get("missing_or_stale_receipt_behavior") or {}
    if missing_receipt_policy.get("blocks_stage_liveness") is not False:
        fail("missing professional Figure Skill evidence must remain progress-first")
    for key in [
        "creates_quality_debt",
        "blocks_quality_readiness",
        "blocks_export_readiness",
        "blocks_publication_readiness",
    ]:
        if missing_receipt_policy.get(key) is not True:
            fail(f"missing professional Figure Skill evidence must keep {key}=true")
    figure_contract_template = display_receipt_templates.get("figure_contract_ref") or {}
    if "template_selection_ref" in (figure_contract_template.get("required_fields") or []):
        fail("figure contracts must not require a template selection")
    template_selection_policy = figure_contract_template.get("template_selection_policy") or {}
    if template_selection_policy.get("required") is not False:
        fail("figure template selection must be optional")
    generation_receipt_template = display_receipt_templates.get("generation_receipt_ref") or {}
    if generation_receipt_template.get("template_fields_required") is not False:
        fail("paper-local generation receipts must not require template fields")
    if generation_receipt_template.get("must_bind_exact_final_output_sha256") is not True:
        fail("paper-local generation receipts must bind exact final output hashes")
    layout_qc_receipt_template = (
        display_receipt_templates.get("layout_qc_receipt_ref") or {}
    )
    if layout_qc_receipt_template.get("surface_kind") != "layout_qc_receipt_candidate.v1":
        fail("layout QC receipt template must use the candidate v1 surface")
    require_all(
        "layout QC receipt required fields",
        layout_qc_receipt_template.get("required_fields"),
        [
            "receipt_id",
            "generation_source_ref",
            "registry_sha256",
            "artifact_bindings",
            "final_canvas",
            "safe_inset_px",
            "lane_bounds_px",
            "semantic_artist_scope",
            "bbox_registry_summary",
            "semantic_flow_summary",
            "checks",
            "violations",
            "regression_fixture_refs",
            "machine_check_status",
            "authority",
            "authority_boundary",
            "publication_ready",
        ],
    )
    require_all(
        "layout QC receipt geometry checks",
        layout_qc_receipt_template.get("required_geometry_checks"),
        [
            "registry_complete",
            "measured_wrap_valid",
            "annotation_lane_separate",
            "no_text_overlap",
            "minimum_spacing_met",
            "no_canvas_overflow",
            "no_clipping",
            "safe_inset_met",
            "semantic_artist_applicability_valid",
            "semantic_artist_registry_complete",
            "semantic_artist_kinds_complete",
            "semantic_artists_inside_canvas",
            "semantic_artists_inside_safe_inset",
            "semantic_node_text_contained",
            "semantic_contract_geometry_bound",
            "semantic_lines_clear_of_text",
            "semantic_lines_clear_of_unrelated_nodes",
            "semantic_connectors_non_crossing",
            "semantic_arrowheads_clear_of_text",
            "semantic_relation_encoding_valid",
            "semantic_arrow_budget_met",
            "semantic_incoming_unambiguous",
            "semantic_bracket_spans_exact",
            "semantic_segmented_group_spans_exact",
            "semantic_segmented_group_perceptual_anchors_valid",
            "fixed_canvas_export",
            "png_pdf_final_size_and_sha_bound",
        ],
    )
    if layout_qc_receipt_template.get("required_artifact_formats") != ["PNG", "PDF"]:
        fail("layout QC receipt must bind final PNG and PDF artifacts")
    for key in ["authority", "publication_ready", "machine_check_is_quality_verdict"]:
        if layout_qc_receipt_template.get(key) is not False:
            fail(f"layout QC receipt flag {key} must be false")
    layout_qc_authority = layout_qc_receipt_template.get("authority_boundary") or {}
    if layout_qc_authority.get("refs_only") is not True:
        fail("layout QC receipt must remain refs-only")
    for key in [
        "can_mutate_artifacts",
        "can_write_mas_truth",
        "can_sign_visual_audit_receipt",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_mas_visual_authority",
        "can_claim_submission_authority",
        "can_claim_artifact_authority",
        "can_claim_quality_verdict",
        "can_claim_publication_readiness",
    ]:
        if layout_qc_authority.get(key) is not False:
            fail(f"layout QC receipt authority flag {key} must be false")
    if "layout_qc_receipt_ref" not in (
        (display_receipt_templates.get("visual_qa_receipt_ref") or {}).get("required_fields")
        or []
    ):
        fail("visual QA receipt must consume layout_qc_receipt_ref")

    if layout_qc_fixture.get("fixture_only") is not True:
        fail("layout QC regression fixture must remain non-issued")
    if not str(layout_qc_fixture.get("semantic_artist_scope") or "").startswith(
        "not_applicable:"
    ):
        fail("statistical layout regression fixture must declare semantic artists not applicable")
    require_all(
        "layout QC regression fixture cases",
        layout_qc_fixture.get("regression_cases"),
        ["long_category_label", "extreme_numeric_annotation", "full_width_layout"],
    )
    fixture_export_policy = layout_qc_fixture.get("export_policy") or {}
    if fixture_export_policy != {
        "canvas_mode": "fixed",
        "bbox_inches": None,
        "tight_crop": False,
    }:
        fail("layout QC regression fixture must use the fixed no-tight-crop canvas")
    fixture_canvas = layout_qc_fixture.get("final_canvas") or {}
    if fixture_canvas.get("unit") != "mm" or fixture_canvas.get("width", 0) < 170:
        fail("layout QC regression fixture must exercise a full-width manuscript canvas")
    fixture_artists = [
        artist
        for panel in layout_qc_fixture.get("panels") or []
        for artist in panel.get("text_artists") or []
    ]
    long_label = next(
        (item for item in fixture_artists if item.get("artist_id") == "a.category.long"),
        {},
    )
    long_measurement = long_label.get("text_measurement") or {}
    if not (
        long_measurement.get("measured_unwrapped_width_px", 0)
        > long_measurement.get("available_width_px", 0)
        and long_measurement.get("line_count", 0) > 1
        and long_measurement.get("manual_breaks") is False
        and "\n" not in str(long_label.get("source_text") or "")
    ):
        fail("layout QC regression fixture must exercise renderer-measured automatic wrapping")
    extreme_annotation = next(
        (
            item
            for item in fixture_artists
            if item.get("artist_id") == "a.annotation.extreme"
        ),
        {},
    )
    if not (
        extreme_annotation.get("artist_kind") == "numeric_annotation"
        and extreme_annotation.get("lane") == "annotation"
        and "e+308" in str(extreme_annotation.get("source_text") or "")
    ):
        fail("layout QC regression fixture must exercise an extreme right annotation")

    if semantic_artist_flow_fixture.get("semantic_fixture_only") is not True:
        fail("semantic artist flow regression fixture must remain non-issued")
    if not any(
        token in str(semantic_artist_flow_fixture.get("figure_archetype") or "").lower()
        for token in ("flow", "schematic")
    ):
        fail("semantic artist regression fixture must declare a flow or schematic")
    semantic_fixture_registry = (
        semantic_artist_flow_fixture.get("semantic_artist_registry") or {}
    )
    semantic_fixture_contract = (
        semantic_artist_flow_fixture.get("semantic_flow_contract") or {}
    )
    if not semantic_fixture_registry.get("expected_prefixes"):
        fail("semantic artist regression fixture must declare expected prefixes")
    if not semantic_fixture_registry.get("artists"):
        fail("semantic artist regression fixture must register visible artists")
    semantic_fixture_artists = {
        str(artist.get("artist_id") or ""): artist
        for artist in semantic_fixture_registry.get("artists") or []
    }
    require_all(
        "semantic artist regression fixture kinds",
        semantic_fixture_contract.get("expected_artist_kinds"),
        ["FancyArrowPatch", "FancyBboxPatch", "Line2D", "Text"],
    )
    semantic_fixture_grammar = (
        semantic_fixture_contract.get("relation_encoding_grammar") or {}
    )
    if semantic_fixture_grammar.get("analysis_set_identity") != ["span_bracket"]:
        fail("semantic artist regression fixture must encode identity with a bracket")
    if "arrow_split" not in (semantic_fixture_grammar.get("partition") or []):
        fail("semantic artist regression fixture must encode partition as an arrow split")
    if semantic_fixture_contract.get("arrow_budget") != 2:
        fail("semantic artist regression fixture must exercise an explicit arrow budget")
    for node in semantic_fixture_contract.get("nodes") or []:
        if not node.get("patch_artist_id") or not node.get("text_artist_ids"):
            fail("semantic artist regression nodes must bind patch and text artists")
    for connector in semantic_fixture_contract.get("connectors") or []:
        if len(connector.get("segments_px") or []) != len(
            connector.get("segment_artist_ids") or []
        ):
            fail("semantic artist regression connectors must bind every segment artist")
        for segment, segment_artist_id in zip(
            connector.get("segments_px") or [],
            connector.get("segment_artist_ids") or [],
        ):
            artist = semantic_fixture_artists.get(str(segment_artist_id)) or {}
            if artist.get("geometry_px") != segment:
                fail(
                    "semantic artist regression connector geometry must bind "
                    "the renderer path endpoints"
                )
    segmented_relations = {
        str(relation.get("relation_id") or ""): relation
        for relation in semantic_fixture_contract.get("relations") or []
        if relation.get("encoding") == "segmented_band"
    }
    segmented_spans = semantic_fixture_contract.get("segmented_group_spans") or []
    if set(segmented_relations) != {"band_partition"} or len(segmented_spans) != 1:
        fail("semantic artist regression fixture must exercise one segmented group")
    segmented_span = segmented_spans[0]
    segmented_relation = segmented_relations["band_partition"]
    if (
        segmented_span.get("relation_id") != "band_partition"
        or segmented_span.get("orientation") != "horizontal"
        or segmented_span.get("entry_edge") != "top"
        or segmented_span.get("child_node_ids")
        != segmented_relation.get("destination_node_ids")
    ):
        fail("semantic artist regression segmented group identity is invalid")
    perceptual_anchor = segmented_span.get("perceptual_anchor") or {}
    if (
        perceptual_anchor.get("mode") != "labeled_full_span_header"
        or perceptual_anchor.get("anchor_position") != "midpoint"
    ):
        fail("semantic artist regression segmented group anchor mode is invalid")
    semantic_fixture_nodes = {
        str(node.get("node_id") or ""): node
        for node in semantic_fixture_contract.get("nodes") or []
    }
    group_node = semantic_fixture_nodes.get(str(segmented_span.get("group_node_id"))) or {}
    child_nodes = [
        semantic_fixture_nodes.get(str(node_id)) or {}
        for node_id in segmented_span.get("child_node_ids") or []
    ]
    group_bbox = group_node.get("bbox_px") or []
    child_bboxes = [node.get("bbox_px") or [] for node in child_nodes]
    if (
        len(group_bbox) != 4
        or any(len(bbox) != 4 for bbox in child_bboxes)
        or group_bbox[0] != min(bbox[0] for bbox in child_bboxes)
        or group_bbox[2] != max(bbox[2] for bbox in child_bboxes)
        or group_bbox[1] != child_bboxes[0][3]
        or any(
            left[2] != right[0]
            for left, right in zip(child_bboxes[:-1], child_bboxes[1:], strict=True)
        )
    ):
        fail("semantic artist regression segmented group span must be exact")
    label_artist_id = str(perceptual_anchor.get("label_artist_id") or "")
    semantic_fixture_text = {
        str(artist.get("artist_id") or ""): str(artist.get("source_text") or "")
        for panel in semantic_artist_flow_fixture.get("panels") or []
        for artist in panel.get("text_artists") or []
    }
    if (
        not str(segmented_span.get("group_label") or "").strip()
        or label_artist_id not in (group_node.get("text_artist_ids") or [])
        or semantic_fixture_text.get(label_artist_id) != segmented_span.get("group_label")
    ):
        fail("semantic artist regression segmented group label anchor is invalid")
    segmented_connectors = [
        connector
        for connector in semantic_fixture_contract.get("connectors") or []
        if connector.get("relation_id") == "band_partition"
    ]
    if len(segmented_connectors) != 1:
        fail("semantic artist regression segmented group requires one connector")
    segmented_connector = segmented_connectors[0]
    expected_group_anchor = [
        (group_bbox[0] + group_bbox[2]) / 2,
        group_bbox[3],
    ]
    if (
        segmented_connector.get("connector_id") != segmented_span.get("connector_id")
        or segmented_connector.get("arrow_bearing") is not False
        or segmented_connector.get("arrowhead_artist_ids") != []
        or segmented_connector.get("destination_node_id")
        != segmented_span.get("group_node_id")
        or (segmented_connector.get("segments_px") or [])[-1][2:]
        != expected_group_anchor
        or segmented_span.get("expected_group_anchor_px") != expected_group_anchor
        or segmented_span.get("actual_connector_terminal_px") != expected_group_anchor
    ):
        fail("semantic artist regression segmented group connector is invalid")
    for bracket in semantic_fixture_contract.get("brackets") or []:
        if not bracket.get("segment_artist_ids"):
            fail("semantic artist regression brackets must bind registered segment artists")
        for segment_artist_id in bracket.get("segment_artist_ids") or []:
            artist = semantic_fixture_artists.get(str(segment_artist_id)) or {}
            if not artist.get("geometry_px"):
                fail(
                    "semantic artist regression bracket geometry must bind "
                    "renderer path endpoints"
                )

    figure_style_kernel = read_text("skills/medical-figure-style/kernel.py")
    display_qc_kernel = read_text("skills/medical-display-qc/kernel.py")
    if '"savefig.bbox": None' not in figure_style_kernel:
        fail("medical-figure-style kernel must default to a fixed savefig canvas")
    if '"savefig.bbox": "tight"' in figure_style_kernel:
        fail("medical-figure-style kernel must not default to tight-crop export")
    for token in [
        "audit_layout_registry",
        "build_layout_qc_receipt",
        "layout_qc_receipt_candidate.v1",
        "_audit_semantic_artist_registry",
        "semantic_artist_registry_missing",
        "semantic_line_text_intersection",
        "semantic_line_unrelated_node_intersection",
        "semantic_connector_crossing_unauthorized",
        "semantic_arrowhead_text_intersection",
        "semantic_node_text_outside_node",
        "semantic_connector_artist_geometry_invalid",
        "semantic_connector_geometry_mismatch",
        "semantic_connector_source_not_anchored",
        "semantic_connector_destination_not_anchored",
        "semantic_junction_group_invalid",
        "semantic_bracket_geometry_invalid",
        "semantic_relation_encoding_invalid",
        "semantic_arrow_budget_exceeded",
        "semantic_ambiguous_incoming_connectors",
        "semantic_bracket_span_mismatch",
        "semantic_segmented_group_relation_set_mismatch",
        "semantic_segmented_group_connector_invalid",
        "semantic_segmented_group_children_not_contiguous",
        "semantic_segmented_group_header_not_adjacent",
        "semantic_segmented_group_anchor_mismatch",
        "semantic_segmented_group_label_artist_invalid",
        "semantic_segmented_group_perceptual_anchors_valid",
        "can_claim_quality_verdict",
        "build_page_hash_evidence_candidate",
        "scholarskills_page_hash_evidence_candidate",
        "evidence_payload",
        "origin_reviewer_evidence_ref",
        '"schema_version": 3',
    ]:
        if token not in display_qc_kernel:
            fail(f"medical-display-qc kernel missing layout QC token: {token}")
