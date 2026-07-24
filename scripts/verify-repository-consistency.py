#!/usr/bin/env python3
import ast
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from urllib.parse import urlparse

from gallery_policy import verify_gallery_import_policy

root = pathlib.Path(__file__).resolve().parents[1]

def fail(message: str) -> None:
    print(f"verify failed: {message}", file=sys.stderr)
    sys.exit(1)

def read_json(relative: str):
    path = root / relative
    if not path.is_file():
        fail(f"missing {relative}")
    return json.loads(path.read_text(encoding="utf-8"))

def read_text(relative: str) -> str:
    path = root / relative
    if not path.is_file():
        fail(f"missing {relative}")
    return path.read_text(encoding="utf-8")

def sha256_file(relative: str) -> str:
    h = hashlib.sha256()
    with (root / relative).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def require_all(label: str, actual, expected) -> None:
    actual_set = set(actual or [])
    for item in expected:
        if item not in actual_set:
            fail(f"{label} missing {item}")

manifest = read_json(".codex-plugin/plugin.json")
if manifest.get("name") != "mas-scholar-skills":
    fail("plugin name must be mas-scholar-skills")
if manifest.get("version") != "0.2.22":
    fail("plugin version must be 0.2.22")
if manifest.get("skills") != "./skills/":
    fail("plugin skills path must be ./skills/")
if manifest.get("interface", {}).get("displayName") != "MAS Scholar Skills":
    fail("plugin displayName must be MAS Scholar Skills")
default_prompts = manifest.get("interface", {}).get("defaultPrompt") or []
if not default_prompts or any(not isinstance(prompt, str) or len(prompt) > 128 for prompt in default_prompts):
    fail("plugin defaultPrompt entries must be non-empty strings of at most 128 characters")
plugin_exposure = manifest.get("masScholarSkillsExposure") or {}
if plugin_exposure.get("policyRef") != "contracts/scholar-skills-capability-modules.json#/codex_skill_exposure_policy":
    fail("plugin manifest must point to codex skill exposure policy")
if plugin_exposure.get("codexDefaultExposure") is not False:
    fail("plugin manifest codex default exposure must be false")
if plugin_exposure.get("optionalInstallPolicy") != "all_exported_skills":
    fail("plugin manifest must materialize all exported skills by default")
if plugin_exposure.get("specialtyRoutingPolicy") != "materialized_by_default_selected_only_for_matching_tasks":
    fail("plugin manifest must separate specialty discovery from task routing")

contract = read_json("contracts/scholar-skills-capability-modules.json")
page_hash_evidence_schema = read_json(
    "contracts/scholarskills-page-hash-evidence-candidate-v3.schema.json"
)
initial_draft_preflight_schema = read_json(
    "contracts/scholarskills-medical-initial-draft-preflight-candidate-v1.schema.json"
)
display_receipt_templates = read_json("contracts/display-pack-receipt-templates.json")
professional_figure_workflow_schema = read_json(
    "contracts/professional-figure-workflow.schema.json"
)
layout_qc_fixture = read_json(
    "skills/medical-display-qc/fixtures/layout_qc_regression.json"
)
semantic_artist_flow_fixture = read_json(
    "skills/medical-display-qc/fixtures/semantic_artist_flow_regression.json"
)
revision_learning_fixture_refs = [
    "skills/medical-data-governance/fixtures/governed-source-reconstruction.json",
    "skills/medical-risk-model-transportability-reviewer/fixtures/construct-comparability-currentness.json",
    "skills/medical-reference-integrity-auditor/fixtures/post-csl-reader-semantics.json",
    "skills/medical-display-qc/fixtures/figure-numbering-one-owner.json",
    "skills/medical-manuscript-review/fixtures/anomaly-evidence-parity.json",
    "skills/medical-manuscript-review/fixtures/receipt-version-member-delta.json",
]
for revision_learning_fixture_ref in revision_learning_fixture_refs:
    read_json(revision_learning_fixture_ref)
domain_descriptor = read_json("contracts/domain_descriptor.json")
capability_map = read_json("contracts/capability_map.json")
package_manifest = read_json("contracts/opl_capability_package_manifest.json")
reference_provider_profile = read_json("contracts/reference-provider-adapters/scientific-metadata.json")
reference_provider_registry = read_json("contracts/reference-provider-adapters/reference-provider-adapter-registry.json")
read_json("contracts/reference-provider-adapters/reference-provider-profile.schema.json")
read_json("contracts/reference-provider-adapters/reference-provider-adapter-registry.schema.json")
read_json("contracts/reference-provider-adapters/reference-provider-adapter-step.schema.json")
scientific_search_profile = read_json("contracts/scientific-search-adapters/scientific-search.json")
scientific_search_registry = read_json("contracts/scientific-search-adapters/scientific-search-adapter-registry.json")
read_json("contracts/scientific-search-adapters/scientific-search-provider-profile.schema.json")
read_json("contracts/scientific-search-adapters/scientific-search-adapter-registry.schema.json")
read_json("contracts/scientific-search-adapters/scientific-search-adapter-step.schema.json")
classification_policy = contract.get("capability_module_classification_policy") or {}
contract_text = json.dumps(contract, ensure_ascii=False)
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
advanced_specialist_skill_ids = classification_policy.get("optional_external_specialist_skills") or []
medical_method_specialist_skill_ids = classification_policy.get("optional_medical_method_specialist_skills") or []
advanced_router_skill_ids = classification_policy.get("optional_external_router_skill_ids") or []
medical_method_router_skill_ids = classification_policy.get("optional_medical_method_router_skill_ids") or []
optional_router_skill_ids = [*advanced_router_skill_ids, *medical_method_router_skill_ids]
optional_named_specialty_skill_ids = classification_policy.get("optional_external_named_specialist_skills") or []
optional_named_specialty_skill_ids = [
    *optional_named_specialty_skill_ids,
    *(classification_policy.get("optional_medical_method_named_specialist_skills") or []),
]
advanced_redirect_tombstone_skill_ids = classification_policy.get("optional_external_redirect_tombstone_skills") or []
medical_method_redirect_tombstone_skill_ids = classification_policy.get("optional_medical_method_redirect_tombstone_skills") or []
redirect_tombstone_skill_ids = [
    *advanced_redirect_tombstone_skill_ids,
    *medical_method_redirect_tombstone_skill_ids,
]
aggregate_skill_ids = ["mas-scholar-skills"]
expected_default_exposure_skill_ids = [*aggregate_skill_ids, *expected_capability_skills]
expected_optional_skill_ids = [*optional_router_skill_ids, *optional_named_specialty_skill_ids]
expected_discoverable_skill_ids = [*expected_default_exposure_skill_ids, *expected_optional_skill_ids]
expected_all_skill_ids = [*expected_default_exposure_skill_ids, *expected_optional_skill_ids]

if package_manifest.get("surface_kind") != "opl_capability_package_manifest.v2":
    fail("capability package manifest must use opl_capability_package_manifest.v2")
if package_manifest.get("package_id") != "mas-scholar-skills":
    fail("capability package manifest package_id must be mas-scholar-skills")
if package_manifest.get("version") != "0.2.22":
    fail("capability package version must be 0.2.22")
if package_manifest.get("package_role") != "framework_capability_package":
    fail("capability package must use the consumer-neutral framework capability role")
if package_manifest.get("schema_ref") != "one-person-lab/contracts/opl-framework/capability-package-manifest.schema.json":
    fail("capability package manifest must point to the OPL capability package schema")
if "primary_consumer" in package_manifest:
    fail("framework capability provider must not declare a required primary consumer")
capability_abi = package_manifest.get("capability_abi") or {}
if capability_abi.get("id") != "mas-scholar-skills.v1":
    fail("capability package must expose the canonical provider ABI")
consumer_policy = package_manifest.get("consumer_policy") or {}
if consumer_policy.get("compatibility_commitment") != "declared_optional_consumer_profiles":
    fail("provider compatibility must be bound to declared optional consumer profiles")
if consumer_policy.get("supported_required_by") != []:
    fail("framework capability provider must not declare a required consumer")
if consumer_policy.get("supported_optional_consumer_agent_ids") != ["mas", "mag"]:
    fail("MAS and MAG must be declared as optional enhancement consumers")
if consumer_policy.get("non_primary_runtime_dependency_supported") is not False:
    fail("consumer profiles must not receive a runtime dependency promise")
package_exports = package_manifest.get("exports") or {}
if package_exports.get("core_skill_ids") != expected_default_exposure_skill_ids:
    fail("capability package core skills must match the canonical default exposure policy")
if package_exports.get("specialty_skill_ids") != expected_optional_skill_ids:
    fail("capability package specialty skills must match the canonical optional skill catalog")
if package_exports.get("all_skill_ids") != expected_all_skill_ids:
    fail("capability package all skills must equal core plus specialty skills")
expected_module_ids = [module.get("module_id") for module in contract.get("modules") or []]
if package_exports.get("core_module_ids") != expected_module_ids:
    fail("capability package core modules must match the canonical module catalog order")
mag_optional_skill_ids = [
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
optional_profile_common = {
    "profile_kind": "optional_refs_only_enhancement",
    "required": False,
    "dependency_kind": "optional_enhancement",
    "required_ids_semantics": "selected_profile_compatibility_set_not_consumer_readiness",
    "missing_or_incompatible_behavior": "consumer_fail_open",
    "diagnostic_role": "consumer_owned_non_blocking_diagnostic",
    "distribution_behavior": "consumer_may_bundle_or_materialize_without_dependency_or_readiness_effect",
    "blocks_install": False,
    "blocks_activation": False,
    "blocks_admission": False,
    "blocks_route": False,
    "blocks_launch": False,
    "blocks_readiness": False,
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
        "required_export_ids": expected_default_exposure_skill_ids,
        "required_module_ids": expected_module_ids,
        **optional_profile_common,
    },
    {
        "profile_id": "mag-medical-grant.v1",
        "consumer_agent_id": "mag",
        "required_export_ids": mag_optional_skill_ids,
        "required_module_ids": mag_compatibility_module_ids,
        **optional_profile_common,
    },
]
if package_manifest.get("consumer_profiles") != expected_consumer_profiles:
    fail("MAS and MAG profiles must share optional, refs-only, authority-false, fail-open semantics")
if "optional_refs_only_consumer_profiles" in package_manifest:
    fail("optional consumer profiles must use the single canonical consumer_profiles surface")
if any(skill_id not in expected_all_skill_ids for skill_id in mag_optional_skill_ids):
    fail("MAG optional consumer profile may reference only real exported Skills")
profile_policy = contract.get("consumer_profile_policy") or {}
if profile_policy.get("profile_source_ref") != "contracts/opl_capability_package_manifest.json#/consumer_profiles":
    fail("capability catalog must reference the canonical optional consumer profiles")
for key in [
    "all_profiles_are_optional_enhancements",
    "global_core_and_specialty_classification_is_not_consumer_readiness",
    "required_ids_are_selected_profile_compatibility_sets_not_readiness_floors",
    "no_profile_defines_consumer_admission_route_launch_or_readiness",
    "consumer_stage_overlay_required",
    "outputs_are_refs_only_candidates",
    "consuming_domain_owner_retains_authority",
    "consumer_missing_or_incompatible_fail_open",
    "consumer_may_bundle_or_materialize_without_dependency_or_readiness_effect",
]:
    if profile_policy.get(key) is not True:
        fail(f"capability catalog consumer profile policy {key} must be true")
runtime_module_id = "mas-scholar-skills.reference-provider-adapters"
search_runtime_module_id = "mas-scholar-skills.scientific-search-adapters"
runtime_module_ids = [runtime_module_id, search_runtime_module_id]
runtime_bindings = package_exports.get("runtime_module_bindings") or []
if [binding.get("module_id") for binding in runtime_bindings] != runtime_module_ids:
    fail("capability package must export the reference verification and scientific search runtime bindings in canonical order")
runtime_binding = runtime_bindings[0]
search_runtime_binding = runtime_bindings[1]
expected_runtime_handler = {
    "kind": "typescript_export",
    "file": "runtime/reference-provider-adapters/index.ts",
    "export": "runReferenceProviderAdapterStep",
}
if runtime_binding.get("module_id") != runtime_module_id:
    fail("runtime binding must use the canonical reference-provider adapter module id")
if runtime_binding.get("module_kind") != "opl_connect_reference_provider_adapter":
    fail("runtime binding must declare the OPL Connect reference-provider adapter kind")
if runtime_binding.get("adapter_abi") != "opl-connect-reference-provider-adapter.v1":
    fail("runtime binding must use the v1 reference-provider adapter ABI")
if runtime_binding.get("handler") != expected_runtime_handler:
    fail("runtime binding must expose the canonical TypeScript handler")
if runtime_binding.get("max_steps") != 2:
    fail("runtime binding must cap all provider state machines at two steps")
if runtime_binding.get("exports") != [
    "runReferenceProviderAdapterStep",
    "build_request",
    "parse_response",
    "next_step",
]:
    fail("runtime binding must expose handler and three state-machine operations")
expected_runtime_sandbox = {
    "network_io": False,
    "environment_read": False,
    "filesystem_read": False,
    "filesystem_write": False,
    "process_spawn": False,
    "dynamic_module_load": False,
    "input_output_policy": "serializable_request_state_response_only",
}
if runtime_binding.get("sandbox") != expected_runtime_sandbox:
    fail("reference-provider runtime binding sandbox must forbid direct I/O and process access")
if any(value is not False for value in (runtime_binding.get("authority_boundary") or {}).values()):
    fail("reference-provider runtime binding authority flags must all be false")
expected_search_runtime_handler = {
    "kind": "typescript_export",
    "file": "runtime/scientific-search-adapters/index.ts",
    "export": "runScientificSearchAdapterStep",
}
if search_runtime_binding.get("module_kind") != "opl_connect_scientific_search_adapter":
    fail("scientific search binding must declare the OPL Connect search adapter kind")
if search_runtime_binding.get("adapter_abi") != "opl-connect-scientific-search-adapter.v1":
    fail("scientific search binding must use the v1 search adapter ABI")
if search_runtime_binding.get("handler") != expected_search_runtime_handler:
    fail("scientific search binding must expose the canonical TypeScript handler")
if search_runtime_binding.get("max_steps") != 1:
    fail("scientific search binding must cap every provider search at one HTTP step")
if search_runtime_binding.get("exports") != [
    "runScientificSearchAdapterStep",
    "build_search_request",
    "parse_search_response",
]:
    fail("scientific search binding must expose its handler and two state-machine operations")
if search_runtime_binding.get("sandbox") != expected_runtime_sandbox:
    fail("scientific search runtime binding sandbox must forbid direct I/O and process access")
if any(value is not False for value in (search_runtime_binding.get("authority_boundary") or {}).values()):
    fail("scientific search runtime binding authority flags must all be false")
plugin_runtime_modules = manifest.get("oplRuntimeModules") or {}
if plugin_runtime_modules != {
    "manifestRef": "contracts/opl_capability_package_manifest.json#/exports/runtime_module_bindings",
    "moduleIds": runtime_module_ids,
}:
    fail("plugin runtime module projection must point to both package runtime bindings")
runtime_contract_paths = [
    "contracts/reference-provider-adapters/scientific-metadata.json",
    "contracts/reference-provider-adapters/reference-provider-profile.schema.json",
    "contracts/reference-provider-adapters/reference-provider-adapter-registry.json",
    "contracts/reference-provider-adapters/reference-provider-adapter-registry.schema.json",
    "contracts/reference-provider-adapters/reference-provider-adapter-step.schema.json",
]
runtime_source_paths = runtime_binding.get("contained_implementation_files") or []
if runtime_source_paths != reference_provider_registry.get("contained_implementation_files"):
    fail("manifest and adapter registry must lock the same implementation files")
search_runtime_contract_paths = [
    "contracts/scientific-search-adapters/scientific-search.json",
    "contracts/scientific-search-adapters/scientific-search-provider-profile.schema.json",
    "contracts/scientific-search-adapters/scientific-search-adapter-registry.json",
    "contracts/scientific-search-adapters/scientific-search-adapter-registry.schema.json",
    "contracts/scientific-search-adapters/scientific-search-adapter-step.schema.json",
]
search_runtime_source_paths = search_runtime_binding.get("contained_implementation_files") or []
if search_runtime_source_paths != scientific_search_registry.get("contained_implementation_files"):
    fail("manifest and scientific search registry must lock the same implementation files")
all_runtime_contract_paths = [*runtime_contract_paths, *search_runtime_contract_paths]
all_runtime_source_paths = list(dict.fromkeys([*runtime_source_paths, *search_runtime_source_paths]))
for relative in [*all_runtime_contract_paths, *all_runtime_source_paths]:
    if not (root / relative).is_file():
        fail(f"package runtime source is missing: {relative}")
content_lock = package_manifest.get("content_lock") or {}
if content_lock.get("algorithm") != "sha256":
    fail("capability package content lock must use sha256")
if content_lock.get("canonicalization") != "ordered_path_length_file_length_bytes":
    fail("capability package content lock must use the length-prefixed canonical boundary")
content_lock_paths = content_lock.get("paths") or []
if len(content_lock_paths) != len(set(content_lock_paths)):
    fail("capability package content lock paths must be unique")
exported_skill_roots = [f"skills/{skill_id}" for skill_id in expected_all_skill_ids]
tracked_result = subprocess.run(
    ["git", "-C", str(root), "ls-files", "--stage", "-z", "--", *exported_skill_roots],
    check=False,
    capture_output=True,
)
tracked_exported_skill_files = []
if tracked_result.returncode == 0:
    for raw_entry in tracked_result.stdout.split(b"\0"):
        if not raw_entry:
            continue
        try:
            raw_metadata, raw_path = raw_entry.split(b"\t", 1)
            mode, _object_id, stage = raw_metadata.decode("ascii").split(" ")
            relative = raw_path.decode("utf-8")
        except (UnicodeDecodeError, ValueError):
            fail("git returned an invalid tracked exported Skill entry")
        if mode not in {"100644", "100755"} or stage != "0":
            fail(f"exported Skill entry must be a tracked regular file: {relative} mode={mode} stage={stage}")
        source = root / relative
        if source.is_symlink() or not source.is_file():
            fail(f"exported Skill entry must resolve to a regular file: {relative}")
        tracked_exported_skill_files.append(relative)
elif (root / ".git").exists():
    fail(
        "cannot inspect tracked exported Skill files: "
        + tracked_result.stderr.decode("utf-8", errors="replace").strip()
    )
else:
    for relative_root in exported_skill_roots:
        skill_root = root / relative_root
        for source in sorted(skill_root.rglob("*")):
            if source.is_symlink():
                fail(f"exported Skill archive entry must not be a symbolic link: {source.relative_to(root)}")
            if source.is_file() and "__pycache__" not in source.parts and source.suffix != ".pyc":
                tracked_exported_skill_files.append(source.relative_to(root).as_posix())
locked_skill_files = [relative for relative in content_lock_paths if relative.startswith("skills/")]
if set(locked_skill_files) != set(tracked_exported_skill_files):
    missing = sorted(set(tracked_exported_skill_files) - set(locked_skill_files))
    unexpected = sorted(set(locked_skill_files) - set(tracked_exported_skill_files))
    fail(
        "capability package content lock must exactly cover tracked exported Skill files: "
        f"missing={missing} unexpected={unexpected}"
    )

canonical_skill_shared_files = {
    "references/professional-quality-ref-templates.md": (
        root / "references/professional-quality-ref-templates.md"
    ),
    "docs/no-authority-boundary.md": root / "docs/no-authority-boundary.md",
    "docs/mas-scholar-skills-operating-model.md": (
        root / "docs/mas-scholar-skills-operating-model.md"
    ),
    "docs/capability-modules.md": root / "docs/capability-modules.md",
}
expected_skill_local_shared_files = set()
actual_skill_local_shared_files = set()
for skill_id in expected_all_skill_ids:
    skill_root = root / "skills" / skill_id
    skill_text = read_text(f"skills/{skill_id}/SKILL.md")
    for shared_ref, canonical_path in canonical_skill_shared_files.items():
        skill_local_path = skill_root / shared_ref
        skill_local_relative = skill_local_path.relative_to(root).as_posix()
        if skill_local_path.is_symlink() or skill_local_path.exists():
            actual_skill_local_shared_files.add(skill_local_relative)
        if shared_ref not in skill_text:
            continue
        expected_skill_local_shared_files.add(skill_local_relative)
        if skill_local_path.is_symlink() or not skill_local_path.is_file():
            fail(
                f"exported Skill shared ref must resolve inside its own directory: "
                f"{skill_local_relative}"
            )
        if skill_local_path.read_bytes() != canonical_path.read_bytes():
            fail(
                f"exported Skill shared ref copy must equal canonical package bytes: "
                f"{skill_local_relative} != {shared_ref}"
            )
        if skill_local_relative not in content_lock_paths:
            fail(f"exported Skill shared ref copy must be content locked: {skill_local_relative}")
if actual_skill_local_shared_files != expected_skill_local_shared_files:
    missing = sorted(expected_skill_local_shared_files - actual_skill_local_shared_files)
    unexpected = sorted(actual_skill_local_shared_files - expected_skill_local_shared_files)
    fail(
        "exported Skill shared ref copies must exactly match SKILL.md package-local refs: "
        f"missing={missing} unexpected={unexpected}"
    )
consuming_mas_skill_refs = {
    "medical-research-portfolio-memory-curator": [
        "docs/policies/study-workflow/publication_route_memory_policy.md",
    ],
}
for skill_id, refs in consuming_mas_skill_refs.items():
    skill_text = read_text(f"skills/{skill_id}/SKILL.md")
    for consuming_ref in refs:
        if consuming_ref not in skill_text:
            fail(f"{skill_id} must retain consuming MAS ref: {consuming_ref}")
        skill_local_path = root / "skills" / skill_id / consuming_ref
        if skill_local_path.is_symlink() or skill_local_path.exists():
            fail(
                f"consuming MAS ref must not be copied into the ScholarSkills package: "
                f"{skill_local_path.relative_to(root)}"
            )
for relative in content_lock_paths:
    source = root / relative
    if source.is_symlink() or not source.is_file():
        fail(f"capability package content lock entry must be a regular file: {relative}")
require_all(
    "capability package runtime content lock",
    content_lock_paths,
    [*all_runtime_contract_paths, *all_runtime_source_paths],
)
require_all(
    "capability package initial-draft contract content lock",
    content_lock_paths,
    ["contracts/scholarskills-medical-initial-draft-preflight-candidate-v1.schema.json"],
)

profile_package = reference_provider_profile.get("adapter_package") or {}
if reference_provider_profile.get("adapter_abi") is not None:
    fail("reference provider profile must keep adapter ABI inside adapter_package")
if profile_package.get("package_id") != "mas-scholar-skills":
    fail("reference provider profile must bind the installed ScholarSkills package")
if profile_package.get("module_id") != runtime_module_id:
    fail("reference provider profile must bind the canonical runtime module")
if profile_package.get("adapter_abi") != runtime_binding.get("adapter_abi"):
    fail("profile and package runtime binding adapter ABIs must match")
if profile_package.get("registry_ref") != runtime_binding.get("registry_ref"):
    fail("profile and package runtime binding registry refs must match")
if profile_package.get("handler_ref") != "runtime/reference-provider-adapters/index.ts#runReferenceProviderAdapterStep":
    fail("reference provider profile must select the canonical state-machine handler")
if profile_package.get("byte_authority") != "installed_capability_package_source_commit_and_content_digest":
    fail("reference provider profile byte authority must bind source commit and package content digest")
profile_adapter_ids = profile_package.get("adapter_ids") or []
registry_adapters = reference_provider_registry.get("adapters") or []
registry_adapter_ids = [item.get("adapter_id") for item in registry_adapters]
if profile_adapter_ids != registry_adapter_ids:
    fail("reference provider profile and registry adapter ids must match in canonical order")
if reference_provider_registry.get("module_id") != runtime_module_id:
    fail("reference provider registry must use the canonical runtime module id")
if reference_provider_registry.get("adapter_abi") != runtime_binding.get("adapter_abi"):
    fail("reference provider registry and package adapter ABIs must match")
if reference_provider_registry.get("handler") != expected_runtime_handler:
    fail("reference provider registry must expose the canonical TypeScript handler")
if reference_provider_registry.get("state_machine_exports") != [
    "build_request",
    "parse_response",
    "next_step",
]:
    fail("reference provider registry must expose the bounded state-machine phases")
if reference_provider_registry.get("max_steps") != 2:
    fail("reference provider registry must cap provider state machines at two steps")
if reference_provider_registry.get("sandbox") != expected_runtime_sandbox:
    fail("reference provider registry sandbox must match the package runtime binding")
if any(value is not False for value in (reference_provider_registry.get("no_authority_boundary") or {}).values()):
    fail("reference provider registry authority flags must all be false")
if any(value is not False for value in (reference_provider_profile.get("no_authority_boundary") or {}).values()):
    fail("reference provider profile authority flags must all be false")
if len(profile_adapter_ids) != 7 or len(set(profile_adapter_ids)) != 7:
    fail("scientific reference provider package must export exactly seven unique adapters")
provider_rows = reference_provider_profile.get("providers") or []
provider_ids = [item.get("provider_id") for item in provider_rows]
if len(provider_ids) != len(set(provider_ids)):
    fail("reference provider profile provider ids must be unique")
if reference_provider_profile.get("default_provider_ids") != provider_ids:
    fail("reference provider defaults must follow the canonical provider order")
for provider in provider_rows:
    if provider.get("adapter_id") not in profile_adapter_ids:
        fail(f"provider {provider.get('provider_id')} selects an unexported adapter")
    endpoint = provider.get("endpoint") or {}
    default_origin = urlparse(endpoint.get("default_base_url") or "").scheme + "://" + urlparse(endpoint.get("default_base_url") or "").netloc
    if default_origin not in (endpoint.get("allowed_origins") or []):
        fail(f"provider {provider.get('provider_id')} default origin must be allowlisted")

search_profile_package = scientific_search_profile.get("adapter_package") or {}
if search_profile_package.get("package_id") != "mas-scholar-skills":
    fail("scientific search profile must bind the installed ScholarSkills package")
if search_profile_package.get("module_id") != search_runtime_module_id:
    fail("scientific search profile must bind the canonical runtime module")
if search_profile_package.get("adapter_abi") != search_runtime_binding.get("adapter_abi"):
    fail("scientific search profile and package binding adapter ABIs must match")
if search_profile_package.get("registry_ref") != search_runtime_binding.get("registry_ref"):
    fail("scientific search profile and package binding registry refs must match")
if search_profile_package.get("handler_ref") != "runtime/scientific-search-adapters/index.ts#runScientificSearchAdapterStep":
    fail("scientific search profile must select the canonical state-machine handler")
if search_profile_package.get("byte_authority") != "installed_capability_package_source_commit_and_content_digest":
    fail("scientific search profile byte authority must bind source commit and package content digest")
search_profile_adapter_ids = search_profile_package.get("adapter_ids") or []
search_registry_adapters = scientific_search_registry.get("adapters") or []
search_registry_adapter_ids = [item.get("adapter_id") for item in search_registry_adapters]
if search_profile_adapter_ids != search_registry_adapter_ids:
    fail("scientific search profile and registry adapter ids must match in canonical order")
if scientific_search_registry.get("module_id") != search_runtime_module_id:
    fail("scientific search registry must use the canonical runtime module id")
if scientific_search_registry.get("adapter_abi") != search_runtime_binding.get("adapter_abi"):
    fail("scientific search registry and package adapter ABIs must match")
if scientific_search_registry.get("handler") != expected_search_runtime_handler:
    fail("scientific search registry must expose the canonical TypeScript handler")
if scientific_search_registry.get("state_machine_exports") != ["build_search_request", "parse_search_response"]:
    fail("scientific search registry must expose its two bounded state-machine phases")
if scientific_search_registry.get("max_steps") != 1:
    fail("scientific search registry must cap provider searches at one step")
if scientific_search_registry.get("sandbox") != expected_runtime_sandbox:
    fail("scientific search registry sandbox must match the package runtime binding")
if any(value is not False for value in (scientific_search_registry.get("no_authority_boundary") or {}).values()):
    fail("scientific search registry authority flags must all be false")
if any(value is not False for value in (scientific_search_profile.get("no_authority_boundary") or {}).values()):
    fail("scientific search profile authority flags must all be false")
expected_search_provider_scope = {
    "role": "generic_metadata_coverage_and_citation_graph_fallback_only",
    "excluded_provider_ids": ["pubmed", "pmc"],
    "excluded_provider_route": "opl_connect_framework_unified_scientific_search",
}
if scientific_search_profile.get("provider_scope") != expected_search_provider_scope:
    fail("scientific search package profile must exclude PubMed/PMC and remain a generic fallback adapter")
if len(search_profile_adapter_ids) != 2 or len(set(search_profile_adapter_ids)) != 2:
    fail("scientific search package must export exactly two unique adapters")
search_provider_rows = scientific_search_profile.get("providers") or []
search_provider_ids = [item.get("provider_id") for item in search_provider_rows]
if scientific_search_profile.get("default_provider_ids") != search_provider_ids:
    fail("scientific search defaults must follow the canonical provider order")
if len(search_provider_ids) != len(set(search_provider_ids)):
    fail("scientific search provider ids must be unique")
expected_search_provider_bindings = [
    ("crossref", "crossref_search_rest", "Crossref"),
    ("openalex", "openalex_search_rest", "OpenAlex"),
]
if [
    (item.get("provider_id"), item.get("adapter_id"), item.get("source_provider"))
    for item in search_provider_rows
] != expected_search_provider_bindings:
    fail("scientific search profile must preserve canonical provider and adapter pairings")
if [
    (item.get("provider_id"), item.get("adapter_id"))
    for item in search_registry_adapters
] != [(provider_id, adapter_id) for provider_id, adapter_id, _ in expected_search_provider_bindings]:
    fail("scientific search registry must preserve canonical provider and adapter pairings")
for provider in search_provider_rows:
    if provider.get("adapter_id") not in search_profile_adapter_ids:
        fail(f"scientific search provider {provider.get('provider_id')} selects an unexported adapter")
    endpoint = provider.get("endpoint") or {}
    parsed_default = urlparse(endpoint.get("default_base_url") or "")
    default_origin = parsed_default.scheme + "://" + parsed_default.netloc
    if default_origin not in (endpoint.get("allowed_origins") or []):
        fail(f"scientific search provider {provider.get('provider_id')} default origin must be allowlisted")

for relative in all_runtime_source_paths:
    source = read_text(relative)
    if re.search(r"(?:from|import\s*)\s*['\"](?:node:)?(?:fs|http|https|net|tls|child_process|worker_threads)", source):
        fail(f"{relative} must not import direct I/O or process modules")
    for token in [
        "fetch(",
        "XMLHttpRequest",
        "process.env",
        "Deno.",
        "Bun.",
        "request_json",
        "request_text",
        "writeFile(",
        "spawn(",
        "exec(",
    ]:
        if token in source:
            fail(f"{relative} must not expose direct I/O surface {token}")
if package_exports.get("optional_skills_installed_by_default") is not True:
    fail("all specialty skills must be installed by default")
if package_exports.get("default_materialization_policy") != "all_exported_skills":
    fail("capability package must use all-exported-skills materialization")
if package_exports.get("specialty_routing_policy") != "materialized_by_default_selected_only_for_matching_tasks":
    fail("capability package must keep specialty routing task-selective")
if "lifecycle" in package_manifest:
    fail("framework capability provider must not own consumer install, repair, activation, or readiness lifecycle")
codex_surface = package_manifest.get("codex_surface") or {}
if codex_surface.get("consumer_profiles_ref") != "#/consumer_profiles":
    fail("Codex package surface must reference the canonical optional consumer profiles")
if "required_skill_ids_ref" in codex_surface:
    fail("Codex package surface must not expose a provider-owned required Skill floor")
plugin_package_ref = plugin_exposure.get("capabilityPackageManifestRef")
if plugin_package_ref != "contracts/opl_capability_package_manifest.json":
    fail("plugin manifest must point to the capability package manifest")
if plugin_exposure.get("capabilityAbi") != capability_abi.get("id"):
    fail("plugin manifest capability ABI must match the capability package manifest")
if plugin_exposure.get("requiredBy") != []:
    fail("plugin manifest must not declare a required consumer")
if plugin_exposure.get("consumerProfilesRef") != "contracts/opl_capability_package_manifest.json#/consumer_profiles":
    fail("plugin manifest must reference the canonical optional consumer profiles")
if "optionalRefsOnlyConsumerProfilesRef" in plugin_exposure:
    fail("plugin manifest must not create a second optional consumer profile surface")


def without_redirect_tombstones(skill_ids):
    return [
        skill_id
        for skill_id in (skill_ids or [])
        if skill_id not in redirect_tombstone_skill_ids
    ]

skill = read_text("skills/mas-scholar-skills/SKILL.md")
if not re.search(r"^---\n[\s\S]*?^name:\s+mas-scholar-skills$", skill, re.MULTILINE):
    fail("SKILL.md frontmatter must expose name: mas-scholar-skills")
capability_skill_texts = {
    skill_id: read_text(f"skills/{skill_id}/SKILL.md")
    for skill_id in expected_capability_skills
}
write_skill = capability_skill_texts["medical-manuscript-writing"]
review_skill = capability_skill_texts["medical-manuscript-review"]
figure_skill = capability_skill_texts["medical-figure-design"]
figure_style_skill = capability_skill_texts["medical-figure-style"]
figure_composer_skill = capability_skill_texts["medical-figure-composer"]
lit_skill = capability_skill_texts["medical-research-lit"]
stats_skill = capability_skill_texts["medical-statistical-review"]
table_skill = capability_skill_texts["medical-table-design"]
table_kernel = read_text("skills/medical-table-design/kernel.py")
for token in [
    "Journal Footnote Discipline",
    "Main-Table Information Budget",
    "lint_table_note_inventory()",
    "lint_main_table_information_budget()",
    "templates and gallery examples as a reference quality floor",
    "reader-facing table Markdown",
    "same long disclaimer below multiple tables",
    "Do not render a standalone `Notes` heading",
]:
    if token not in table_skill:
        fail(f"medical-table-design missing journal footnote discipline token: {token}")
for token in [
    "TABLE_NOTE_BUDGET_EXCEEDED",
    "INTERNAL_AUDIT_METADATA_IN_READER_NOTE",
    "REPEATED_GLOBAL_TABLE_NOTE",
    "MAIN_TABLE_ROW_BUDGET_EXCEEDED",
    "MAIN_TABLE_COLUMN_BUDGET_EXCEEDED",
    "MAIN_TABLE_BODY_WORD_BUDGET_EXCEEDED",
    "MAIN_TABLE_FOOTNOTE_WORD_BUDGET_EXCEEDED",
    "MAIN_TABLE_SUPPLEMENTARY_ROUTE_MISSING",
    "MAIN_TABLE_STANDALONE_NOTES_HEADING_PRESENT",
    "MAIN_TABLE_FINAL_EMBEDDING_NOT_ONE_PAGE",
]:
    if token not in table_kernel:
        fail(f"medical-table-design kernel missing table-note lint token: {token}")
submit_skill = capability_skill_texts["medical-submission-prep"]
submit_kernel = read_text("skills/medical-submission-prep/kernel.py")
write_kernel = read_text("skills/medical-manuscript-writing/kernel.py")
for token in [
    "Manuscript-Author Stance",
    "scientific_evidence_gap",
    "author_supplied_objective_fact",
    "author_input_registry_ref",
    "[AUTHOR INPUT: ...]",
]:
    if token not in write_skill:
        fail(f"medical-manuscript-writing missing author-input policy token: {token}")
for token in [
    "validate_author_input_registry",
    "validate_author_stance_integrity_candidate",
    "DEFENSIVE_AUTHOR_INPUT_META_PROSE",
    "AUTHOR_INPUT_ANNOTATION_ORPHANED",
    "AUTHOR_INPUT_ANNOTATION_CARDINALITY_INVALID",
    "AUTHOR_INPUT_DECLARED_COUNTS_MISMATCH",
]:
    if token not in write_kernel:
        fail(f"medical-manuscript-writing kernel missing author-input gate token: {token}")
for token in [
    "Author-Input Projection Contract",
    "author_input_registry_ref",
    "author_input_todo_projection_ref",
]:
    if token not in submit_skill:
        fail(f"medical-submission-prep missing author-input projection token: {token}")
for token in [
    "build_author_input_todo_projection",
    "validate_author_input_todo_projection",
    "AUTHOR_INPUT_TODO_PROJECTION_MISMATCH",
]:
    if token not in submit_kernel:
        fail(f"medical-submission-prep kernel missing author-input projection gate token: {token}")
data_governance_skill = capability_skill_texts["medical-data-governance"]
cohort_phenotyping_skill = read_text("skills/medical-cohort-phenotyping/SKILL.md")
methodology_planner_skill = read_text("skills/medical-methodology-planner/SKILL.md")
registry_story_architect_skill = read_text("skills/medical-registry-atlas-story-architect/SKILL.md")
first_draft_quality_sources = {
    "skills/medical-manuscript-writing/kernel.py": read_text(
        "skills/medical-manuscript-writing/kernel.py"
    ),
    "skills/medical-registry-atlas-story-architect/kernel.py": read_text(
        "skills/medical-registry-atlas-story-architect/kernel.py"
    ),
    "skills/medical-statistical-review/kernel.py": read_text(
        "skills/medical-statistical-review/kernel.py"
    ),
}
advanced_specialist_skills = {
    skill_id: read_text(f"skills/{skill_id}/SKILL.md")
    for skill_id in advanced_specialist_skill_ids
}
medical_method_specialist_skills = {
    skill_id: read_text(f"skills/{skill_id}/SKILL.md")
    for skill_id in medical_method_specialist_skill_ids
}
mag_grant_skill_candidate_refs = {
    "medical-research-lit": "grant_literature_evidence_candidate_ref",
    "medical-statistical-review": "grant_statistical_review_candidate_ref",
    "medical-methodology-planner": "grant_methodology_plan_candidate_ref",
    "medical-evidence-integrity-reviewer": "grant_evidence_integrity_candidate_ref",
    "medical-evidence-synthesis-and-claim-map": "grant_claim_map_candidate_ref",
    "medical-reference-integrity-auditor": "grant_reference_integrity_candidate_ref",
}
mag_grant_skill_texts = {
    "medical-research-lit": lit_skill,
    "medical-statistical-review": stats_skill,
    **{
        skill_id: medical_method_specialist_skills[skill_id]
        for skill_id in mag_grant_skill_candidate_refs
        if skill_id in medical_method_specialist_skills
    },
}
for skill_id, candidate_ref in mag_grant_skill_candidate_refs.items():
    skill_text = mag_grant_skill_texts.get(skill_id, "")
    for token in [
        "MAG grant mode",
        "source_pack_ref",
        candidate_ref,
        "candidate_refs",
        "owner_gate_handoff_ref",
        "grant truth",
        "fundability",
        "quality verdict",
        "export readiness",
    ]:
        if token not in skill_text:
            fail(f"{skill_id} missing MAG grant consumer token: {token}")
display_qc_skill = medical_method_specialist_skills["medical-display-qc"]
display_qc_kernel = read_text("skills/medical-display-qc/kernel.py")
reference_integrity_skill = medical_method_specialist_skills[
    "medical-reference-integrity-auditor"
]
reference_integrity_kernel = read_text(
    "skills/medical-reference-integrity-auditor/kernel.py"
)
survival_skill = medical_method_specialist_skills["medical-survival-analysis-plan"]
survival_kernel = read_text("skills/medical-survival-analysis-plan/kernel.py")
data_freeze_skill = medical_method_specialist_skills[
    "medical-data-freeze-and-analysis-readiness-reviewer"
]
data_freeze_kernel = read_text(
    "skills/medical-data-freeze-and-analysis-readiness-reviewer/kernel.py"
)
initial_draft_skill_tokens = {
    "medical-manuscript-writing": (
        write_skill,
        [
            "medical_initial_draft_preflight_candidate_ref",
            "scholarskills-medical-initial-draft-preflight-candidate-v1.schema.json",
            "baseline_data_citation",
            "bounded_analysis_campaign",
            "review_and_quality_gate",
            "cannot authorize a full draft",
            "initial_complete_draft",
            "all seven gates",
            "audit_applicable_initial_draft_specialist_refs()",
            "immutable_candidate_snapshot_ref",
            "does not sign an immutable reviewer snapshot",
        ],
    ),
    "medical-manuscript-review": (
        review_skill,
        [
            "medical_initial_draft_preflight_candidate_ref",
            "immutable reviewer",
            "Figure 1-N",
            "Table 1-N",
            "cannot sign first-draft readiness",
        ],
    ),
    "medical-statistical-review": (
        stats_skill,
        [
            "validation_partition_integrity_ref",
            "endpoint_analysis_set_reconciliation_ref",
            "model_complexity_sparse_event_ref",
            "decision_curve_validity_ref",
            "linked prediction performance",
            "calibration slope alone",
            "kernel-owned tolerance",
            "Candidate producers cannot override either policy",
            "no_tuning_prespecified",
            "not a mechanical 5- or 10-events-per-variable pass rule",
            "anomaly_sensitivity_ref",
            "verification_scope_contract_ref",
            "does not establish artifact currentness",
        ],
    ),
    "medical-survival-analysis-plan": (
        survival_skill,
        [
            "fixed_horizon_risk_semantics_ref",
            "competing_risk_ref",
            "survival_estimand_plan_ref",
            "decision_curve_validity_ref",
            "non-informative censoring",
            "IPCW Brier",
            "recorded event fraction is descriptive",
        ],
    ),
    "medical-data-freeze-and-analysis-readiness-reviewer": (
        data_freeze_skill,
        [
            "clinical_analysis_input_identity_ref",
            "study_context",
            "study_context_ref",
            "Early censoring is a separate state",
            "An all-N/A inventory never satisfies identity closure",
        ],
    ),
    "medical-reference-integrity-auditor": (
        reference_integrity_skill,
        [
            "citation_source_coverage_ref",
            "four keyed sets",
            "four empty sets",
            "reference_lane_active_inventory_binding_ref",
            "reintroduced",
        ],
    ),
    "medical-table-design": (
        table_skill,
        [
            "baseline_table_traceability_ref",
            "available_n + missing_n = group_n",
            "variable-level denominators",
        ],
    ),
    "medical-display-qc": (
        display_qc_skill,
        [
            "document_display_scope_coverage_ref",
            "display_render_integrity_ref",
            "requires_reader_pdf=true",
            "member_id",
            "selected_layout_main_manuscript",
            "reader_combined_main_and_supplementary",
            "cannot substitute for page-render/page-hash evidence",
            "PNG pixels directly",
        ],
    ),
}
for skill_id, (skill_text, tokens) in initial_draft_skill_tokens.items():
    for token in tokens:
        if token not in skill_text:
            fail(f"{skill_id} missing initial-draft preflight token: {token}")

initial_draft_kernel_tokens = {
    "medical-manuscript-writing": (
        write_kernel,
        [
            "validate_medical_initial_draft_preflight_candidate",
            "validate_medical_initial_draft_preflight_candidate_v2",
            "build_medical_initial_draft_applicability_disposition",
            "validate_medical_initial_draft_applicability_disposition",
            "medical_initial_draft_applicability_disposition_exact_ref",
            "medical_initial_draft_applicability_disposition_candidate.v1",
            "PREFLIGHT_APPLICABILITY_DISPOSITION_CANDIDATE_MISSING",
            "PREFLIGHT_APPLICABILITY_DISPOSITION_IDENTITY_MISMATCH",
            "PREFLIGHT_APPLICABILITY_DISPOSITION_REUSED",
            "PREFLIGHT_CONDITIONAL_REF_ALTERNATIVES_NOT_EXCLUSIVE",
            "INITIAL_DRAFT_PREFLIGHT_DEPENDENCY_OWNERS",
            "PREFLIGHT_SATISFIED_GATE_REF_MISSING",
            "PREFLIGHT_ROUTE_BACK_GATE_INCOMPLETE",
            "PREFLIGHT_NOT_APPLICABLE_GATE_REASON_MISSING",
            "PREFLIGHT_DEPENDENCY_OWNER_INVALID",
            "PREFLIGHT_REQUIRED_GATE_NOT_APPLICABLE",
            "INITIAL_DRAFT_PREFLIGHT_MANUSCRIPT_MODE_APPLICABILITY",
            "size_bytes < 1",
            "applicable_initial_draft_specialist_refs",
            "audit_applicable_initial_draft_specialist_refs",
            "INITIAL_DRAFT_SPECIALIST_REF_ROUTES",
            "ordinary_audit",
            "fixed_horizon_required",
            'assert "immutable_candidate_snapshot_ref" not in fixed_horizon_required',
            'assert "immutable_candidate_snapshot_ref" not in external_required',
            "build_authoring_freeze_handoff_candidate",
            "AUTHORING_FREEZE_HANDOFF_ROUTE",
            '"signs_review_currentness": False',
        ],
    ),
    "medical-statistical-review": (
        first_draft_quality_sources["skills/medical-statistical-review/kernel.py"],
        [
            "validate_validation_partition_integrity",
            "VALIDATION_SELECTION_POLICY_MISSING",
            "validate_endpoint_analysis_set_reconciliation",
            "validate_endpoint_analysis_set_reconciliation_v2",
            "validate_model_complexity_sparse_event",
            "ph_assessment_applicability",
            "continuous_predictor_count",
            "validate_decision_curve_validity",
            "PREDICTION_IPA_IDENTITY_MISMATCH",
            "PREDICTION_IPA_TOLERANCE_CALLER_OVERRIDE_FORBIDDEN",
            "PREDICTION_CALIBRATION_BOUNDS_CALLER_OVERRIDE_FORBIDDEN",
            "PREDICTION_PERFORMANCE_POLICY_ID",
            "scholarskills_linked_prediction_performance.v2",
            "PREDICTION_DISCRIMINATION_METRIC_TYPES",
            "PREDICTION_DISCRIMINATION_RANGE_INVALID",
            "PREDICTION_LIMITING_EVIDENCE_METRIC_REF_INVALID",
            "PREDICTION_LIMITING_EVIDENCE_METRIC_NOT_IN_PANEL",
            "PREDICTION_LIMITING_EVIDENCE_PHRASE_UNSUPPORTED",
            "PREDICTION_LIMITING_EVIDENCE_POLICY_ID",
            "PREDICTION_LIMITED_IPA_UPPER_BOUND",
            "PREDICTION_LIMITING_POLICY_CALLER_OVERRIDE_FORBIDDEN",
            "PREDICTION_RANKING_LIMITING_METRIC_MISSING",
            "PREDICTION_IPA_CONSISTENCY_TOLERANCE",
            "PREDICTION_CALIBRATION_REASONABLE_BOUNDS",
            "ABSOLUTE_RISK_SUPPORT_CONTRADICTS_LINKED_PERFORMANCE",
        ],
    ),
    "medical-survival-analysis-plan": (
        survival_kernel,
        [
            "validate_survival_estimand_plan",
            "fixed_horizon_risk_semantics_ref",
            "competing_risk_ref",
            "decision_curve_validity_ref",
        ],
    ),
    "medical-data-freeze-and-analysis-readiness-reviewer": (
        data_freeze_kernel,
        [
            "validate_clinical_analysis_input_identity_candidate",
            "validate_clinical_analysis_input_identity_candidate_v2",
            "has_longitudinal_follow_up",
            "is_multicenter",
            "requires_endpoint_adjudication",
            "CLINICAL_INPUT_IDENTITY_ALL_NOT_APPLICABLE",
            "CLINICAL_INPUT_STUDY_CONTEXT_EXACT_REF_INVALID",
            "early_censored_count",
        ],
    ),
    "medical-reference-integrity-auditor": (
        reference_integrity_kernel,
        [
            "audit_citation_source_coverage",
            "audit_citation_source_coverage_v2",
            "CITATION_MANUSCRIPT_KEY_SET_EMPTY",
            "CITATION_BIBLIOGRAPHY_KEY_SET_EMPTY",
            "citation_source_coverage_ref",
            "audit_reference_lane_active_inventory_binding",
            "EXCLUDED_REFERENCE_CLEARANCE_STATUS_INVALID",
        ],
    ),
    "medical-table-design": (
        table_kernel,
        [
            "validate_baseline_table_traceability",
            "BASELINE_AVAILABLE_MISSING_N_IDENTITY_VIOLATION",
            "BASELINE_SUMMARY_DENOMINATOR_MISMATCH",
            "BASELINE_SMD_CROSS_SURFACE_CONFLICT",
        ],
    ),
    "medical-display-qc": (
        display_qc_kernel,
        [
            "DISPLAY_QC_REFS",
            "display_render_integrity_ref",
            "validate_document_display_scope_coverage",
            "requires_reader_pdf",
            "expected_display_members",
            "DOCUMENT_DISPLAY_EXPECTED_MEMBER_MISSING_FROM_SNAPSHOT",
            "DOCUMENT_DISPLAY_EXPECTED_MEMBER_MISSING_FROM_AUDIT",
            "DOCUMENT_DISPLAY_PAGE_EVIDENCE_MISSING",
            "composed_paper_pdf_exact_ref",
            "physical_dimensions_inches",
            "normalized_crop_bounds",
        ],
    ),
}
for skill_id, (kernel_text, tokens) in initial_draft_kernel_tokens.items():
    for token in tokens:
        if token not in kernel_text:
            fail(f"{skill_id} kernel missing initial-draft preflight token: {token}")

def require_unversioned_v1_binding(
    label: str,
    source_text: str,
    function_name: str,
    internal_function_name: str,
) -> None:
    tree = ast.parse(source_text)
    function = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == function_name
        ),
        None,
    )
    if function is None:
        fail(f"{label} missing unversioned v1 entrypoint {function_name}")
    calls = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == internal_function_name
    ]
    if len(calls) != 1:
        fail(f"{label} unversioned entrypoint must call one internal validator")
    strict_keyword = next(
        (keyword for keyword in calls[0].keywords if keyword.arg == "strict_v2"),
        None,
    )
    if (
        strict_keyword is None
        or not isinstance(strict_keyword.value, ast.Constant)
        or strict_keyword.value.value is not False
    ):
        fail(f"{label} unversioned entrypoint must bind strict_v2=false")

require_unversioned_v1_binding(
    "clinical input identity",
    data_freeze_kernel,
    "validate_clinical_analysis_input_identity_candidate",
    "_validate_clinical_analysis_input_identity_candidate",
)
require_unversioned_v1_binding(
    "citation source coverage",
    reference_integrity_kernel,
    "audit_citation_source_coverage",
    "_audit_citation_source_coverage",
)

transportability_skill = medical_method_specialist_skills[
    "medical-risk-model-transportability-reviewer"
]
evidence_integrity_skill = medical_method_specialist_skills[
    "medical-evidence-integrity-reviewer"
]
initial_draft_learning_skill_tokens = {
    "medical-survival-analysis-plan": (
        survival_skill,
        [
            "fixed_horizon_risk_semantics_ref",
            "Kaplan-Meier risk",
            "cumulative incidence",
            "IPCW Brier",
            "medical-statistical-review",
            "medical-manuscript-writing",
        ],
    ),
    "medical-risk-model-transportability-reviewer": (
        transportability_skill,
        [
            "claim_family_scope_qualifier_ref",
            "construct_comparability_ref",
            "not estimable",
            "identity-preserving linkage",
            "family cannot satisfy another; discrimination does not establish calibrated",
            "absolute risk, deployment utility, or the cause of transport failure",
        ],
    ),
    "medical-data-governance": (
        data_governance_skill,
        [
            "analysis_input_anomaly_inventory_ref",
            "medical-statistical-review",
            "Do not silently delete, winsorize, recode, or repair observations",
        ],
    ),
    "medical-statistical-review": (
        stats_skill,
        [
            "analysis_input_anomaly_inventory_ref",
            "anomaly_sensitivity_ref",
            "verification_scope_contract_ref",
            "medical-evidence-integrity-reviewer",
            "medical-manuscript-writing",
        ],
    ),
    "medical-evidence-integrity-reviewer": (
        evidence_integrity_skill,
        [
            "verification_scope_contract_ref",
            "claim_family_scope_qualifier_ref",
            "construct_comparability_ref",
            "medical-statistical-review",
            "medical-risk-model-transportability-reviewer",
        ],
    ),
    "medical-manuscript-writing": (
        write_skill,
        [
            "immutable_candidate_snapshot_ref",
            "Only after the seven-gate preflight is satisfied",
            "build_authoring_freeze_handoff_candidate()",
            "refs-only and no-authority",
            "renderer_provenance_ref",
            "structured_display_source_map_ref",
            "does not sign an immutable reviewer snapshot",
        ],
    ),
}
for skill_id, (skill_text, tokens) in initial_draft_learning_skill_tokens.items():
    for token in tokens:
        if token not in skill_text:
            fail(f"{skill_id} missing Study 002 initial-draft learning token: {token}")
for skill_id, skill_text in {
    "medical-manuscript-review": review_skill,
    "medical-statistical-review": stats_skill,
    "medical-reference-integrity-auditor": reference_integrity_skill,
    "medical-display-qc": display_qc_skill,
    "medical-submission-prep": submit_skill,
}.items():
    for token in [
        "review_input_snapshot_binding",
        "opl_reviewer_input_snapshot_manifest",
        "live",
        "typed blocker",
    ]:
        if token not in skill_text:
            fail(f"{skill_id} missing immutable snapshot boundary token: {token}")
for source_label, source_text, tokens in [
    (
        "medical-manuscript-writing skill",
        write_skill,
        ["lint_reader_facing_workflow_language()", "review-companion"],
    ),
    (
        "medical-manuscript-writing kernel",
        write_kernel,
        [
            "INTERNAL_WORKFLOW_LANGUAGE_IN_READER_SURFACE",
            "AUTHORING_INSTRUCTION_IN_READER_SURFACE",
            "INTERNAL_REVIEW_LANGUAGE_IN_READER_SURFACE",
        ],
    ),
    (
        "medical-submission-prep skill",
        submit_skill,
        ["lint_submission_artifact_roles()", "journal allowlist"],
    ),
    (
        "medical-submission-prep kernel",
        submit_kernel,
        [
            "INTERNAL_REVIEW_ARTIFACT_EXPOSED_TO_JOURNAL",
            "SUPPLEMENT_ARTIFACT_ROLE_MISMATCH",
            "SUPPLEMENTARY_MEMBER_IN_MAIN_DOCUMENT",
        ],
    ),
    (
        "medical-display-qc skill",
        display_qc_skill,
        ["editorial_page_composition_ref", "lint_document_layout_inventory()"],
    ),
    (
        "medical-display-qc kernel",
        display_qc_kernel,
        [
            "FIGURE_LEGEND_SPLIT_ACROSS_PAGES",
            "SUPPLEMENTARY_DISPLAY_IN_MAIN_DOCUMENT",
            "DISPLAY_AND_REFERENCES_SHARE_PAGE",
            "ORPHAN_SECTION_HEADING_AT_PAGE_END",
            "SINGLETON_PANEL_LABEL_IN_CONTINUATION_TITLE",
        ],
    ),
]:
    for token in tokens:
        if token not in source_text:
            fail(f"{source_label} missing publication-surface quality token: {token}")
redirect_tombstone_skills = {
    skill_id: read_text(f"skills/{skill_id}/TOMBSTONE.md")
    for skill_id in redirect_tombstone_skill_ids
}
actual_discoverable_skill_ids = sorted(
    path.parent.name
    for path in (root / "skills").glob("*/SKILL.md")
)
if actual_discoverable_skill_ids != sorted(expected_discoverable_skill_ids):
    fail(
        "discoverable SKILL.md set must match aggregate + core + optional exposure policy; "
        f"actual={actual_discoverable_skill_ids}"
    )
if (root / "skills/opl-scholarskills/SKILL.md").exists():
    fail("opl-scholarskills must not be an active discoverable SKILL.md")
for skill_id in redirect_tombstone_skill_ids:
    if (root / f"skills/{skill_id}/SKILL.md").exists():
        fail(f"{skill_id} is a tombstone and must not expose SKILL.md metadata")
    if not (root / f"skills/{skill_id}/TOMBSTONE.md").exists():
        fail(f"{skill_id} tombstone must keep non-discoverable TOMBSTONE.md")
for skill_id, text in {
    **capability_skill_texts,
    **advanced_specialist_skills,
    **medical_method_specialist_skills,
}.items():
    if not re.search(rf"^---\n[\s\S]*?^name:\s+{re.escape(skill_id)}$", text, re.MULTILINE):
        fail(f"{skill_id} must be a real Codex skill")

readme = read_text("README.md")
readme_zh = read_text("README.zh-CN.md")
docs_index = read_text("docs/README.md")
operating_model = read_text("docs/mas-scholar-skills-operating-model.md")
capability_modules_doc = read_text("docs/capability-modules.md")
professional_ref_templates = read_text("references/professional-quality-ref-templates.md")

# The pack is descriptor/provenance-only. Do not let skill-local skeletons or
# human-facing active docs revive the retired module execution transport.
retired_execution_transport_tokens = [
    "candidate_package_ref",
    "execution_receipt_ref",
    "scientific_connector_invocation_refs",
    "pubmed_connector_invocation_ref",
]
active_surface_paths = [
    root / "AGENTS.md",
    root / "README.md",
    root / "README.zh-CN.md",
    root / "docs/README.md",
    root / "docs/no-authority-boundary.md",
    root / "docs/capability-modules.md",
    root / "docs/mas-scholar-skills-operating-model.md",
    *sorted((root / "skills").glob("*/SKILL.md")),
    *sorted((root / "skills").glob("*/kernel.py")),
]
for path in active_surface_paths:
    text = path.read_text(encoding="utf-8")
    for token in retired_execution_transport_tokens:
        if token in text:
            fail(f"{path.relative_to(root)} must not retain retired execution transport token: {token}")

if domain_descriptor.get("surface_kind") != "oma_capability_pack_target_descriptor":
    fail("domain descriptor must expose oma_capability_pack_target_descriptor")
if domain_descriptor.get("domain_id") != "mas-scholar-skills":
    fail("domain descriptor domain_id must be mas-scholar-skills")
if domain_descriptor.get("delivery_domain") != "capability_pack":
    fail("domain descriptor delivery_domain must be capability_pack")
if domain_descriptor.get("oma_consumption_policy", {}).get("capability_map_ref") != "contracts/capability_map.json":
    fail("domain descriptor must point OMA to contracts/capability_map.json")
descriptor_pack = domain_descriptor.get("capability_pack", {})
if descriptor_pack.get("default_consumers") != [
    "med-autoscience",
    "med-autogrant",
    "opl-meta-agent",
    "one-person-lab.agent_lab",
]:
    fail("domain descriptor default consumers must include MAS and MAG")
if descriptor_pack.get("syncable_real_skills") != expected_capability_skills:
    fail("domain descriptor syncable real skills must match the canonical Skill catalog")
if domain_descriptor.get("capability_pack", {}).get("runtime_module_ids") != runtime_module_ids:
    fail("domain descriptor must expose both package runtime modules")
if domain_descriptor.get("capability_pack", {}).get("runtime_module_bindings_ref") != "contracts/opl_capability_package_manifest.json#/exports/runtime_module_bindings":
    fail("domain descriptor must point to the package runtime module bindings")
if domain_descriptor.get("capability_pack", {}).get("runtime_module_consumption_mode") != "opl_connect_executes_http_package_adapter_builds_and_parses_bounded_steps":
    fail("domain descriptor must preserve the provider adapter execution split")
if descriptor_pack.get("advanced_specialist_skills") != advanced_specialist_skill_ids:
    fail("domain descriptor advanced specialist skills must match the canonical Skill catalog")
if domain_descriptor.get("capability_pack", {}).get("advanced_specialists_block_core_progress_when_missing") is not False:
    fail("advanced specialists must not block core progress when missing")
if descriptor_pack.get("medical_method_specialist_skills") != medical_method_specialist_skill_ids:
    fail("domain descriptor medical-method specialist skills must exclude redirect tombstones")
if descriptor_pack.get("advanced_specialist_redirect_tombstones") != advanced_redirect_tombstone_skill_ids:
    fail("domain descriptor advanced redirect tombstones must match the canonical classification")
if descriptor_pack.get("medical_method_specialist_redirect_tombstones") != medical_method_redirect_tombstone_skill_ids:
    fail("domain descriptor medical-method redirect tombstones must match the canonical classification")
if descriptor_pack.get("advanced_named_specialist_skills") != classification_policy.get("optional_external_named_specialist_skills"):
    fail("domain descriptor advanced named specialists must match the canonical classification")
if descriptor_pack.get("medical_method_named_specialist_skills") != classification_policy.get("optional_medical_method_named_specialist_skills"):
    fail("domain descriptor medical-method named specialists must exclude redirect tombstones")
if descriptor_pack.get("optional_named_specialty_skill_ids") != optional_named_specialty_skill_ids:
    fail("domain descriptor optional named specialties must exclude redirect tombstones")
if domain_descriptor.get("capability_pack", {}).get("medical_method_specialists_block_core_progress_when_missing") is not False:
    fail("medical-method specialists must not block core progress when missing")
if capability_map.get("surface_kind") != "oma_capability_pack_map":
    fail("capability map must expose oma_capability_pack_map")
if capability_map.get("domain_id") != "mas-scholar-skills":
    fail("capability map domain_id must be mas-scholar-skills")
if capability_map.get("delivery_domain") != "capability_pack":
    fail("capability map delivery_domain must be capability_pack")
if "MAS, MAG, and Agent Lab" not in capability_map.get("purpose", ""):
    fail("capability map purpose must describe MAS and MAG consumers")
if capability_map.get("source_contract_ref") != "contracts/scholar-skills-capability-modules.json":
    fail("capability map must point to the canonical module contract")
if capability_map.get("skill_exposure_policy_ref") != "contracts/scholar-skills-capability-modules.json#/codex_skill_exposure_policy":
    fail("capability map must point to the codex skill exposure policy")
if capability_map.get("codex_default_exposure") is not False:
    fail("capability map codex default exposure must be false")
capability_by_id = {
    item.get("capability_id"): item
    for item in capability_map.get("capabilities", [])
}
failure_token_registry_ref = "opl-framework:contracts/opl-framework/agent-lab-failure-token-registry.json"
expected_capability_token_policy = {
    "medical-figure-design": {
        "module": "display",
        "required_improvement_tokens": ["figure_quality", "display_quality", "visual_quality"],
        "required_failure_tokens": ["medical_failure:figure", "figure_quality"],
        "failure_types": ["figure"],
    },
    "medical-figure-style": {
        "module": "display",
        "contract_ref": "contracts/scholar-skills-capability-modules.json#/capability_module_classification_policy/display_subskill_routes/style_only",
        "required_improvement_tokens": ["figure_style", "figure_quality", "display_quality", "visual_quality"],
        "required_failure_tokens": ["medical_failure:figure", "figure_style", "figure_quality"],
        "failure_types": ["figure"],
    },
    "medical-figure-composer": {
        "module": "display",
        "contract_ref": "contracts/scholar-skills-capability-modules.json#/capability_module_classification_policy/display_subskill_routes/compose_only",
        "required_improvement_tokens": ["figure_composition", "figure_quality", "display_quality", "visual_quality"],
        "required_failure_tokens": ["medical_failure:figure", "figure_composition", "figure_quality"],
        "failure_types": ["figure"],
    },
    "medical-manuscript-writing": {
        "module": "write",
        "required_improvement_tokens": ["manuscript_quality", "medical_manuscript_quality", "writing_quality"],
        "required_failure_tokens": ["medical_failure:writing", "manuscript_quality"],
        "failure_types": ["writing"],
    },
    "medical-manuscript-review": {
        "module": "review",
        "required_improvement_tokens": ["review_quality", "manuscript_review", "quality_review"],
        "required_failure_tokens": ["medical_failure:review", "review_quality"],
        "failure_types": ["review"],
    },
    "medical-research-lit": {
        "module": "lit",
        "required_improvement_tokens": ["citation", "literature", "citation_quality", "literature_quality"],
        "required_failure_tokens": ["medical_failure:citation", "medical_failure:literature"],
        "failure_types": ["citation", "literature"],
    },
    "medical-statistical-review": {
        "module": "stats",
        "required_improvement_tokens": ["stats", "statistical_review", "stats_quality", "analysis_quality"],
        "required_failure_tokens": ["medical_failure:statistics", "stats"],
        "failure_types": ["statistics"],
    },
    "medical-table-design": {
        "module": "tables",
        "required_improvement_tokens": ["table", "tables", "table_quality", "reporting_table_quality"],
        "required_failure_tokens": ["medical_failure:table", "table"],
        "failure_types": ["table"],
    },
    "medical-submission-prep": {
        "module": "submit",
        "required_improvement_tokens": ["submission", "submission_quality", "submission_package", "journal_package"],
        "required_failure_tokens": ["medical_failure:submission", "submission"],
        "failure_types": ["submission"],
    },
    "medical-data-governance": {
        "module": "data",
        "required_improvement_tokens": ["data_governance", "data_quality", "source_data_governance", "clinical_data_governance"],
        "required_failure_tokens": ["medical_failure:data_governance", "data_governance"],
        "failure_types": ["data_governance"],
    },
}
if capability_map.get("failure_token_registry_ref") != failure_token_registry_ref:
    fail("capability map must point to the OPL failure token registry ref")
owner_closeout_boundary = capability_map.get("owner_closeout_boundary") or {}
if owner_closeout_boundary.get("boundary_kind") != "refs_only_no_authority_owner_closeout":
    fail("capability map must expose refs-only no-authority owner closeout boundary")
if owner_closeout_boundary.get("closeout_authority_owner") != "consuming_domain_owner":
    fail("owner closeout boundary must route closeout to the consuming domain owner")
for key in [
    "capability_pack_may_sign_owner_receipt",
    "capability_pack_may_create_typed_blocker",
    "capability_pack_may_claim_publication_readiness",
    "capability_pack_may_claim_current_package_authority",
]:
    if owner_closeout_boundary.get(key) is not False:
        fail(f"owner closeout boundary flag {key} must be false")
advanced_capability_by_id = {
    item.get("skill_id"): item
    for item in capability_map.get("optional_specialist_skills", [])
}
capability_map_optional_skill_ids = [
    item.get("skill_id")
    for item in capability_map.get("optional_specialist_skills", [])
]
if capability_map_optional_skill_ids != expected_optional_skill_ids:
    fail("capability map optional specialist Skills must match discoverable exports exactly")
if capability_map.get("optional_named_specialty_skill_ids") != optional_named_specialty_skill_ids:
    fail("capability map optional named specialties must exclude redirect tombstones")
capability_map_no_regression_ids = [
    item.get("skill_id")
    for item in capability_map.get("optional_specialist_no_regression_map", [])
]
if capability_map_no_regression_ids != optional_named_specialty_skill_ids:
    fail("capability map no-regression rows must describe only real named specialty Skills")
expected_redirect_tombstones = [
    *(contract.get("advanced_specialist_pack_policy", {}).get("redirect_tombstone_skills", [])),
    *(contract.get("medical_method_specialist_pack_policy", {}).get("redirect_tombstone_skills", [])),
]
if capability_map.get("optional_specialist_redirect_tombstones") != expected_redirect_tombstones:
    fail("capability map redirect tombstones must match the canonical contract rows")
advanced_expected = {
    "medical-advanced-biomed-router": {
        "sources": ["alphafold2", "proteinmpnn", "borzoi", "scgpt", "indication-dossier", "compute-env-setup"],
        "refs": ["advanced_biomed_question_ref", "advanced_biomed_route_ref", "execution_intent_ref", "deterministic_receipt_ref"],
        "tokens": ["advanced_biomed", "structure", "protein_design", "genomics", "single_cell", "scientific_compute"],
    },
}
method_expected = {
    "medical-methodology-planner": {
        "tokens": ["methodology_planner", "protocol", "SAP", "cohort", "causal_inference", "survival_analysis", "risk_model"],
        "refs": ["methodology_question_ref", "methodology_route_ref", "methodology_plan_ref", "methodology_support_map_ref"],
    },
    "medical-evidence-integrity-reviewer": {
        "tokens": ["evidence_integrity", "claim_map", "source_support", "reference_integrity", "PMID", "DOI", "evidence_gap"],
        "refs": ["evidence_integrity_inventory_ref", "source_support_map_ref", "identifier_integrity_ref", "evidence_gap_decision_candidate_ref"],
    },
    "medical-publication-routeback-reviewer": {
        "tokens": ["publication_routeback", "rebuttal", "reviewer_response", "owner_gate", "display_qc", "display_regression", "human_gate"],
        "refs": ["publication_routeback_inventory_ref", "authority_boundary_ref", "routeback_option_map_ref", "residual_risk_ref"],
    },
}
for skill_id, expected in advanced_expected.items():
    item = advanced_capability_by_id.get(skill_id)
    if item is None:
        fail(f"capability map optional specialists missing {skill_id}")
    if item.get("canonical_path") != f"skills/{skill_id}/SKILL.md":
        fail(f"optional specialist canonical path for {skill_id} must point to its SKILL.md")
    require_all(f"optional specialist tokens for {skill_id}", item.get("tokens"), [skill_id, *expected["sources"]])
    require_all(f"optional specialist refs for {skill_id}", item.get("candidate_ref_families"), expected["refs"])
    if item.get("optional_external_specialist") is not True:
        fail(f"{skill_id} must be marked optional external specialist")
    if item.get("blocks_core_progress_when_missing") is not False:
        fail(f"{skill_id} must not block core progress when missing")
    for key in [
        "can_write_domain_truth",
        "can_write_runtime_state",
        "can_mutate_artifact_body",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_quality_verdict",
        "can_claim_publication_readiness",
        "can_claim_current_package_authority",
        "can_claim_owner_closeout",
    ]:
        if (item.get("authority_boundary") or {}).get(key) is not False:
            fail(f"optional specialist authority flag {key} must be false for {skill_id}")
for skill_id, expected in method_expected.items():
    item = advanced_capability_by_id.get(skill_id)
    if item is None:
        fail(f"capability map optional medical-method specialists missing {skill_id}")
    if item.get("canonical_path") != f"skills/{skill_id}/SKILL.md":
        fail(f"optional medical-method specialist canonical path for {skill_id} must point to its SKILL.md")
    require_all(f"optional medical-method specialist tokens for {skill_id}", item.get("tokens"), [skill_id, *expected["tokens"]])
    require_all(f"optional medical-method specialist refs for {skill_id}", item.get("candidate_ref_families"), expected["refs"])
    if item.get("optional_medical_method_specialist") is not True:
        fail(f"{skill_id} must be marked optional medical-method specialist")
    if item.get("blocks_core_progress_when_missing") is not False:
        fail(f"{skill_id} must not block core progress when missing")
    for key in [
        "can_replace_default_eight_skills",
        "can_block_default_core_progress_when_missing",
        "can_write_domain_truth",
        "can_write_runtime_state",
        "can_mutate_artifact_body",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_quality_verdict",
        "can_claim_publication_readiness",
        "can_claim_current_package_authority",
        "can_claim_owner_closeout",
    ]:
        if (item.get("authority_boundary") or {}).get(key) is not False:
            fail(f"optional medical-method specialist authority flag {key} must be false for {skill_id}")
for skill_id in expected_optional_skill_ids:
    item = advanced_capability_by_id.get(skill_id)
    if item is None:
        fail(f"capability map optional specialist missing {skill_id}")
    if item.get("canonical_path") != f"skills/{skill_id}/SKILL.md":
        fail(f"optional specialist canonical path for {skill_id} must point to its SKILL.md")
    if item.get("external_repo_ref") != f"external_repo:mas-scholar-skills/skills/{skill_id}/SKILL.md":
        fail(f"optional specialist external repo ref for {skill_id} must point to its SKILL.md")
    if item.get("default_exposure") is not False:
        fail(f"optional specialist {skill_id} must not be selected for generic tasks")
    if item.get("optional_named_specialty_only") is not True:
        fail(f"optional specialist {skill_id} must remain named-specialty routed")
    if item.get("blocks_core_progress_when_missing") is not False:
        fail(f"optional specialist {skill_id} must not block core progress when missing")
    for key in [
        "can_replace_default_eight_skills",
        "can_block_default_core_progress_when_missing",
        "can_write_domain_truth",
        "can_write_runtime_state",
        "can_mutate_artifact_body",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_quality_verdict",
        "can_claim_publication_readiness",
        "can_claim_current_package_authority",
        "can_claim_owner_closeout",
    ]:
        if (item.get("authority_boundary") or {}).get(key) is not False:
            fail(f"optional specialist authority flag {key} must be false for {skill_id}")
for skill_id in expected_capability_skills:
    item = capability_by_id.get(skill_id)
    if item is None:
        fail(f"capability map missing {skill_id}")
    if item.get("canonical_path") != f"skills/{skill_id}/SKILL.md":
        fail(f"capability map canonical path for {skill_id} must point to its SKILL.md")
    if item.get("external_repo_ref") != f"external_repo:mas-scholar-skills/skills/{skill_id}/SKILL.md":
        fail(f"capability map external repo ref for {skill_id} must point to mas-scholar-skills")
    require_all(f"capability map tokens for {skill_id}", item.get("tokens"), [skill_id])
    token_policy = expected_capability_token_policy[skill_id]
    require_all(
        f"capability map improvement tokens for {skill_id}",
        item.get("improvement_tokens"),
        [skill_id, f"mas-scholar-skills.{token_policy['module']}", *token_policy["required_improvement_tokens"]],
    )
    require_all(
        f"capability map failure tokens for {skill_id}",
        item.get("failure_tokens"),
        token_policy["required_failure_tokens"],
    )
    require_all(
        f"capability map failure token refs for {skill_id}",
        item.get("failure_token_refs"),
        [
            f"{failure_token_registry_ref}#/medical_failure_types/{failure_type}"
            for failure_type in token_policy["failure_types"]
        ],
    )
    require_all(
        f"capability map verification refs for {skill_id}",
        item.get("verification_refs"),
        ["scripts/verify.sh#capability-map-token-policy", failure_token_registry_ref],
    )
    require_all(
        f"capability map canonical paths for {skill_id}",
        item.get("canonical_paths"),
        [
            f"skills/{skill_id}/SKILL.md",
            token_policy.get(
                "contract_ref",
                f"contracts/scholar-skills-capability-modules.json#/capability_module_classification_policy/real_skill_backed_module_map/{token_policy['module']}",
            ),
        ],
    )
    if item.get("owner_closeout_boundary_ref") != "contracts/capability_map.json#/owner_closeout_boundary":
        fail(f"capability map owner closeout boundary ref missing for {skill_id}")
    item_authority = item.get("authority_boundary") or {}
    for key in [
        "can_write_domain_truth",
        "can_write_runtime_state",
        "can_mutate_artifact_body",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_quality_verdict",
        "can_claim_publication_readiness",
        "can_claim_current_package_authority",
        "can_claim_owner_closeout",
    ]:
        if item_authority.get(key) is not False:
            fail(f"capability map authority flag {key} must be false for {skill_id}")
if "figure_quality" not in set(capability_by_id["medical-figure-design"].get("feedback_targets", [])):
    fail("capability map must route figure_quality to medical-figure-design")
if "manuscript_quality" not in set(capability_by_id["medical-manuscript-writing"].get("feedback_targets", [])):
    fail("capability map must route manuscript_quality to medical-manuscript-writing")
if "review_quality" not in set(capability_by_id["medical-manuscript-review"].get("feedback_targets", [])):
    fail("capability map must route review_quality to medical-manuscript-review")
if not {"citation", "literature"}.issubset(set(capability_by_id["medical-research-lit"].get("feedback_targets", []))):
    fail("capability map must route citation/literature to medical-research-lit")
if "cold_store_catalog_ref" in contract_text:
    fail("contract must use lifecycle_catalog_ref instead of cold_store_catalog_ref")
if "cold_store_catalog_declared" in contract_text:
    fail("contract must use lifecycle_catalog_declared instead of cold_store_catalog_declared")
if contract.get("brand_family") != "MAS Scholar Skills":
    fail("contract brand_family must be MAS Scholar Skills")
positioning_policy = contract.get("positioning_policy") or {}
expected_positioning = {
    "product_stage_name": "MAS Scholar Skills",
    "repository_id": "mas-scholar-skills",
    "role": "framework_capability_provider_for_optional_mas_paper_and_mag_grant_enhancements",
    "primary_mas_entry_policy": "MAS_stage_operating_prompts_remain_in_med_autoscience_and_may_consume_specialist_skills_from_mas_scholar_skills",
    "canonical_mas_stage_source_policy": "MAS_domain_agent_repo_agent_stages_and_agent_prompts_are_the_canonical_stage_prompt_source",
    "codex_projection_policy": "MAS_overlay_skills_and_workspace_or_quest_dot_codex_skill_copies_are_codex_projection_or_compatibility_surfaces_not_stage_prompt_source",
    "no_parallel_entry_policy": "do_not_create_parallel_stage_authority_entries_in_mas_scholar_skills",
    "professional_skill_location_policy": "professional_specialist_skills_default_to_the_consuming_domain_agent_repo; heavy_cross_workspace_or_independently_released_skills_may_be_externalized_to_pack_repos_such_as_mas_scholar_skills",
    "tool_connector_policy": "OPL_Connect_or_Fabric_owns_tool_invocation_normalized_read_receipts_and_connector_errors_not_stage_policy_specialist_judgment_owner_receipts_typed_blockers_human_gates_publication_readiness_or_artifact_authority",
    "sync_owner": "OPL Connect",
    "bundled_or_materialized_pack_owner": "consumer_distribution_profile",
    "ledger_and_owner_receipt_owner": "MAS_MAG_or_relevant_OPL_domain_owner",
}
for key, expected in expected_positioning.items():
    if positioning_policy.get(key) != expected:
        fail(f"positioning policy {key} must be {expected}")
require_all(
    "positioning default boundary defense",
    positioning_policy.get("default_boundary_defense"),
    ["stage_prompt", "professional_specialist_skill", "tool_connector"],
)
require_all(
    "positioning policy provided surfaces",
    positioning_policy.get("provided_surfaces"),
    [
        "real_codex_skills",
        "syncable_real_skills",
        "medical_paper_professional_specialist_skills",
        "references",
        "packs",
        "quality_floors",
        "templates",
        "external_learning_absorption",
        "module_contract",
        "candidate_refs",
        "route_back_hints",
    ],
)
if "opl-scholarskills" not in positioning_policy.get("legacy_repository_ids", []):
    fail("positioning policy must keep opl-scholarskills as legacy alias")
specialist_skill_policy = contract.get("specialist_skill_policy") or {}
if specialist_skill_policy.get("canonical_aggregate_skill") != "mas-scholar-skills":
    fail("specialist skill policy must name mas-scholar-skills as canonical aggregate skill")
if specialist_skill_policy.get("legacy_aggregate_skill_alias") != "opl-scholarskills":
    fail("specialist skill policy must keep opl-scholarskills as legacy alias")
if specialist_skill_policy.get("legacy_alias_policy") != "opl_scholarskills_is_history_tombstone_provenance_only_not_active_install_or_codex_discovery_surface":
    fail("specialist skill policy must mark opl-scholarskills as history/tombstone provenance only")
require_all(
    "syncable real skills",
    specialist_skill_policy.get("syncable_real_skills"),
    [
        "medical-manuscript-writing",
        "medical-manuscript-review",
        "medical-figure-design",
        "medical-figure-style",
        "medical-figure-composer",
        "medical-research-lit",
        "medical-statistical-review",
        "medical-table-design",
        "medical-submission-prep",
        "medical-data-governance",
    ],
)
require_all(
    "medical paper specialist skill sources",
    specialist_skill_policy.get("medical_paper_specialist_skill_sources"),
    [
        "medical-manuscript-writing",
        "medical-manuscript-review",
        "medical-figure-design",
        "medical-figure-style",
        "medical-figure-composer",
        "medical-statistical-review",
        "medical-table-design",
        "medical-submission-prep",
        "medical-data-governance",
    ],
)
require_all(
    "external resource specialist skills",
    specialist_skill_policy.get("external_resource_specialist_skills"),
    ["medical-research-lit"],
)
require_all(
    "canonical MAS stage source roots",
    specialist_skill_policy.get("canonical_mas_stage_source_roots"),
    ["agent/stages/", "agent/prompts/"],
)
expected_specialist_boundary = {
    "stage_specialist_boundary_policy": "MAS_owns_stage_operating_prompts_for_write_review_figure_scout_and_route_authority; mas_scholar_skills_owns_professional_specialist_playbooks_and_refs_only_candidate_outputs",
    "codex_projection_policy": "MAS_overlay_skills_and_workspace_or_quest_dot_codex_skill_copies_are_codex_projection_or_compatibility_surfaces_not_stage_prompt_source",
    "default_skill_home_policy": "professional_specialist_skills_default_to_the_consuming_domain_agent_repo_next_to_stage_prompts",
    "external_pack_split_policy": "heavy_cross_workspace_or_independently_released_professional_skills_may_be_split_to_external_pack_repos; mas_scholar_skills_is_the_pack_for_MAS_medical_writing_review_figure_lit_stats_tables_submit_data_governance_Display_and_source_refs",
    "tool_connector_boundary_policy": "tool_connectors_own_tool_or_API_invocation_normalized_read_receipts_and_resource_errors_not_stage_policy_professional_judgment_owner_receipts_typed_blockers_human_gates_publication_readiness_or_artifact_authority",
}
for key, expected in expected_specialist_boundary.items():
    if specialist_skill_policy.get(key) != expected:
        fail(f"specialist skill policy {key} must be {expected}")
require_all(
    "specialist default boundary defense",
    specialist_skill_policy.get("default_boundary_defense"),
    ["stage_prompt", "professional_specialist_skill", "tool_connector"],
)
if "mas_owned_primary_skills" in specialist_skill_policy:
    fail("specialist skill policy must not keep legacy mas_owned_primary_skills wording")
if specialist_skill_policy.get("mas_consumes_specialist_skills") is not True:
    fail("specialist skill policy must state MAS consumes synced professional specialist skills")
if specialist_skill_policy.get("mas_maintains_write_review_figure_stage_operating_prompts") is not True:
    fail("specialist skill policy must state MAS keeps write/review/figure stage operating prompts")
for key in [
    "can_replace_mas_overlay_skill",
    "can_replace_mas_runtime_owner_surface",
    "can_claim_literature_authority",
    "can_claim_medical_writing_authority",
    "can_claim_medical_review_authority",
    "can_claim_figure_artifact_authority",
    "can_sign_owner_receipt",
    "can_create_typed_blocker",
    "can_claim_publication_readiness",
]:
    if specialist_skill_policy.get(key) is not False:
        fail(f"specialist skill authority flag {key} must be false")
exposure_policy = contract.get("codex_skill_exposure_policy") or {}
if exposure_policy.get("policy_id") != "mas_scholar_skills_codex_skill_exposure.v1":
    fail("contract missing codex skill exposure policy")
if exposure_policy.get("source_of_truth") != "contracts/scholar-skills-capability-modules.json":
    fail("codex skill exposure policy must be contract-sourced")
if exposure_policy.get("plugin_manifest_ref") != ".codex-plugin/plugin.json":
    fail("codex skill exposure policy must point to plugin manifest")
if exposure_policy.get("codex_default_exposure") is not False:
    fail("codex skill exposure policy default exposure must be false")
if exposure_policy.get("default_install_policy") != "workspace_or_quest_install_includes_all_exported_skills":
    fail("codex skill exposure policy must install all exported skills")
if exposure_policy.get("aggregate_skill_ids") != aggregate_skill_ids:
    fail("codex skill exposure aggregate skill ids must match")
if exposure_policy.get("core_skill_ids") != expected_capability_skills:
    fail("codex skill exposure core skill ids must match real syncable skills")
if exposure_policy.get("default_exposure_skill_ids") != expected_all_skill_ids:
    fail("codex skill exposure default skill ids must include all exported skills")
if exposure_policy.get("optional_skills_installed_by_default") is not True:
    fail("codex skill exposure must install specialty skills by default")
if exposure_policy.get("specialty_routing_policy") != "materialized_by_default_selected_only_for_matching_tasks":
    fail("codex skill exposure must separate materialization from specialty routing")
for policy_name, policy_value in [
    (
        "optional_external_specialist_policy",
        classification_policy.get("optional_external_specialist_policy"),
    ),
    (
        "optional_medical_method_specialist_policy",
        classification_policy.get("optional_medical_method_specialist_policy"),
    ),
    (
        "advanced_specialist_pack_policy.codex_discovery_policy",
        contract.get("advanced_specialist_pack_policy", {}).get(
            "codex_discovery_policy"
        ),
    ),
    (
        "medical_method_specialist_pack_policy.codex_discovery_policy",
        contract.get("medical_method_specialist_pack_policy", {}).get(
            "codex_discovery_policy"
        ),
    ),
]:
    if (
        "materialized_by_default" not in (policy_value or "")
        or "selected_only_for_matching_tasks" not in (policy_value or "")
    ):
        fail(
            f"{policy_name} must separate default materialization from task routing"
        )
for policy_name, policy_value in [
    (
        "capability_module_classification_policy.optional_specialist_router_policy",
        classification_policy.get("optional_specialist_router_policy"),
    ),
    (
        "domain_descriptor.capability_pack.optional_router_policy",
        descriptor_pack.get("optional_router_policy"),
    ),
]:
    normalized_policy = str(policy_value or "").lower()
    if not all(
        token in normalized_policy
        for token in (
            "materialized by default",
            "default_exposure=false",
            "matching tasks",
        )
    ):
        fail(
            f"{policy_name} must distinguish default materialization from automatic routing"
        )
    if "sync one" in normalized_policy or "installs preserve" in normalized_policy:
        fail(f"{policy_name} retains a stale named-scope materialization policy")
if exposure_policy.get("optional_skill_ids") != expected_optional_skill_ids:
    fail("codex skill exposure optional skill ids must match optional specialist policies")
if exposure_policy.get("optional_router_skill_ids") != optional_router_skill_ids:
    fail("codex skill exposure optional router skill ids must match router policy")
if exposure_policy.get("optional_named_specialty_skill_ids") != optional_named_specialty_skill_ids:
    fail("codex skill exposure optional named specialty skill ids must match named specialist policy")
if sorted(exposure_policy.get("optional_redirect_tombstone_skill_ids") or []) != sorted(redirect_tombstone_skill_ids):
    fail("codex skill exposure redirect tombstone ids must match classification policy")
if sorted(exposure_policy.get("tombstone_skill_ids") or []) != ["opl-scholarskills"]:
    fail("codex skill exposure policy must tombstone only opl-scholarskills")
allowed_scopes = exposure_policy.get("allowed_scopes") or {}
for category in ["aggregate", "core"]:
    require_all(
        f"codex skill exposure {category} scopes",
        allowed_scopes.get(category),
        ["workspace", "quest", "explicit_codex_developer"],
    )
require_all(
    "codex skill exposure optional scopes",
    allowed_scopes.get("optional"),
    ["workspace", "quest", "explicit_codex_developer"],
)
require_all(
    "codex skill exposure optional named specialty scopes",
    allowed_scopes.get("optional_named_specialty"),
    ["workspace", "quest", "explicit_codex_developer"],
)
redirect_policy = exposure_policy.get("redirect_tombstone_policy", "")
if "Retired optional professional skill metadata" not in redirect_policy or "capability_preserved=true" not in redirect_policy:
    fail("codex skill exposure redirect policy must describe retired optional professional skill redirects")
if "Only opl-scholarskills" not in exposure_policy.get("tombstone_policy", ""):
    fail("codex skill exposure tombstone policy must tombstone only opl-scholarskills")
if plugin_exposure.get("defaultWorkspaceOrQuestInstall") != expected_all_skill_ids:
    fail("plugin manifest default workspace/quest install must match exposure policy")
if plugin_exposure.get("optionalRouterSkillIds") != optional_router_skill_ids:
    fail("plugin manifest optional router skill ids must match exposure policy")
if without_redirect_tombstones(plugin_exposure.get("optionalNamedSpecialtySkillIds")) != optional_named_specialty_skill_ids:
    fail("plugin manifest optional named specialty skill ids must match exposure policy after retired redirects are filtered")
if without_redirect_tombstones(plugin_exposure.get("optionalSkillIds")) != expected_optional_skill_ids:
    fail("plugin manifest optional skill ids must match exposure policy after retired redirects are filtered")
plugin_redirect_ids = plugin_exposure.get("optionalRedirectTombstoneSkillIds") or []
if plugin_redirect_ids and sorted(plugin_redirect_ids) != sorted(redirect_tombstone_skill_ids):
    fail("plugin manifest optional redirect tombstone skill ids must be empty or match exposure policy")
if plugin_exposure.get("tombstoneSkillIds") != exposure_policy.get("tombstone_skill_ids"):
    fail("plugin manifest tombstone skill ids must match exposure policy")
for key in [
    "can_replace_mas_overlay_skill",
    "can_replace_mas_runtime_owner_surface",
    "can_claim_required_pack_for_study",
    "can_write_owner_ledger",
    "can_sign_owner_receipt",
    "can_create_typed_blocker",
    "can_claim_publication_readiness",
]:
    if positioning_policy.get(key) is not False:
        fail(f"positioning authority flag {key} must be false")
if classification_policy.get("policy_id") != "mas_scholar_skills_professional_skill_classification.v1":
    fail("contract missing professional skill classification policy")
require_all(
    "active professional skill modules",
    classification_policy.get("active_professional_skill_modules"),
    ["display", "tables", "stats", "lit", "write", "review", "submit", "data"],
)
require_all(
    "real syncable specialist skills",
    classification_policy.get("real_syncable_specialist_skills"),
    [
        "medical-manuscript-writing",
        "medical-manuscript-review",
        "medical-figure-design",
        "medical-figure-style",
        "medical-figure-composer",
        "medical-research-lit",
        "medical-statistical-review",
        "medical-table-design",
        "medical-submission-prep",
        "medical-data-governance",
    ],
)
expected_real_skill_backed_modules = {
    "display": "medical-figure-design",
    "lit": "medical-research-lit",
    "stats": "medical-statistical-review",
    "tables": "medical-table-design",
    "write": "medical-manuscript-writing",
    "review": "medical-manuscript-review",
    "submit": "medical-submission-prep",
    "data": "medical-data-governance",
}
if classification_policy.get("real_skill_backed_module_map") != expected_real_skill_backed_modules:
    fail("classification policy must map the eight real-skill-backed modules")
display_subskill_routes = classification_policy.get("display_subskill_routes") or {}
expected_display_subskill_routes = {
    "style_only": "medical-figure-style",
    "compose_only": "medical-figure-composer",
    "full_figure_work": "medical-figure-design",
    "subskill_module_id": "mas-scholar-skills.display",
    "can_add_active_module": False,
    "can_claim_figure_artifact_authority": False,
    "can_claim_publication_readiness": False,
}
if display_subskill_routes != expected_display_subskill_routes:
    fail("classification policy must route display subskills without adding active modules")
if "capability_module_contracts" in classification_policy:
    fail("classification policy must not keep legacy capability_module_contracts")
if classification_policy.get("contract_layer_modules"):
    fail("classification policy must not expose active contract-layer modules")
if "retired_or_deferred_modules" in classification_policy:
    fail("classification policy must not keep retired/deferred module placeholders")
if not classification_policy.get("non_active_scope_policy"):
    fail("classification policy must state non-active scope without module placeholders")
for token in [
    "not_from_a_fixed_ten_module_catalog",
    "source_or_external_learning_intake_belongs_to_OPL_Framework_or_MAS_stage_source_surfaces",
    "omics_enters_mas_scholar_skills_only_as_a_future_real_professional_skill_when_MAS_has_a_stable_workflow",
    "dot_codex_skills_sync_remains_required_for_Codex_discovery",
]:
    if token not in json.dumps(classification_policy, ensure_ascii=False):
        fail(f"classification policy missing {token}")
for key in [
    "can_expose_contract_layer_modules_without_real_skill",
    "can_claim_non_active_scope_is_active",
    "can_replace_mas_stage_prompts",
    "can_claim_owner_acceptance",
    "can_claim_publication_readiness",
]:
    if classification_policy.get(key) is not False:
        fail(f"classification policy flag {key} must be false")
require_all(
    "classification optional external specialist skills",
    classification_policy.get("optional_external_specialist_skills"),
    advanced_specialist_skill_ids,
)
if "do_not_block_default_core_progress" not in classification_policy.get("optional_external_specialist_policy", ""):
    fail("classification optional specialist policy must not block default core progress")
require_all(
    "classification optional medical-method specialist skills",
    classification_policy.get("optional_medical_method_specialist_skills"),
    medical_method_specialist_skill_ids,
)
if "do_not_block_default_core_progress" not in classification_policy.get("optional_medical_method_specialist_policy", ""):
    fail("classification optional medical-method specialist policy must not block default core progress")
advanced_policy = contract.get("advanced_specialist_pack_policy") or {}
if advanced_policy.get("policy_id") != "mas_scholar_skills_advanced_specialist_pack.v1":
    fail("contract missing advanced specialist pack policy")
if advanced_policy.get("source_head_commit") != "54a2f333973147a1fd703caea6f12252e1f227d6":
    fail("advanced specialist pack must pin AcademicForge source head")
if advanced_policy.get("classification") != "optional_external_router_and_named_specialist_skills_refs_only_no_authority":
    fail("advanced specialist pack must be optional router + named specialist refs-only no-authority")
if "replace the eight default medical-paper skills" not in advanced_policy.get("relationship_to_active_modules", ""):
    fail("advanced specialist pack must not replace the default eight skills")
if "OPL_Runway_Connect_Fabric" not in advanced_policy.get("runtime_substrate_owner_policy", ""):
    fail("advanced compute boundary must keep OPL substrate ownership")
if sorted(item.get("skill_id") for item in advanced_policy.get("redirect_tombstone_skills", [])) != sorted(advanced_redirect_tombstone_skill_ids):
    fail("advanced specialist redirect tombstones must match classification policy")
if advanced_policy.get("optional_router_skill_ids") != advanced_router_skill_ids:
    fail("advanced specialist router ids must match classification policy")
if advanced_policy.get("optional_named_specialist_skill_ids") != classification_policy.get("optional_external_named_specialist_skills"):
    fail("advanced named specialist ids must match classification policy")
advanced_policy_by_id = {
    item.get("skill_id"): item
    for item in advanced_policy.get("optional_specialist_skills", [])
}
for skill_id, expected in advanced_expected.items():
    item = advanced_policy_by_id.get(skill_id)
    if item is None:
        fail(f"advanced specialist policy missing {skill_id}")
    if item.get("canonical_path") != f"skills/{skill_id}/SKILL.md":
        fail(f"advanced specialist policy path wrong for {skill_id}")
    require_all(f"advanced specialist upstream refs for {skill_id}", item.get("upstream_skill_refs"), expected["sources"])
    require_all(f"advanced specialist candidate refs for {skill_id}", item.get("candidate_ref_families"), expected["refs"])
    require_all(
        f"advanced specialist required handoff refs for {skill_id}",
        item.get("required_handoff_refs"),
        ["candidate_refs", "owner_gate_handoff_ref"],
    )
    for key in [
        "can_replace_default_eight_skills",
        "can_block_default_core_progress_when_missing",
        "can_write_domain_truth",
        "can_write_runtime_state",
        "can_mutate_artifact_body",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_quality_verdict",
        "can_claim_publication_readiness",
        "can_claim_current_package_authority",
        "can_claim_owner_closeout",
    ]:
        if (item.get("authority_boundary") or {}).get(key) is not False:
            fail(f"advanced specialist policy authority flag {key} must be false for {skill_id}")
for key in [
    "can_replace_default_eight_skills",
    "can_block_default_core_progress_when_missing",
    "can_write_domain_truth",
    "can_write_runtime_state",
    "can_mutate_artifact_body",
    "can_sign_owner_receipt",
    "can_create_typed_blocker",
    "can_claim_quality_verdict",
    "can_claim_publication_readiness",
    "can_claim_current_package_authority",
    "can_claim_owner_closeout",
]:
    if advanced_policy.get(key) is not False:
        fail(f"advanced specialist pack authority flag {key} must be false")
method_policy = contract.get("medical_method_specialist_pack_policy") or {}
if method_policy.get("policy_id") != "mas_scholar_skills_medical_method_specialist_pack.v1":
    fail("contract missing medical-method specialist pack policy")
if method_policy.get("classification") != "optional_medical_method_router_and_named_specialist_skills_refs_only_no_authority":
    fail("medical-method specialist pack must be optional router + named specialist refs-only no-authority")
if "do not add active professional modules" not in method_policy.get("relationship_to_active_modules", ""):
    fail("medical-method specialist pack must not add active modules")
method_policy_by_id = {
    item.get("skill_id"): item
    for item in method_policy.get("optional_specialist_skills", [])
}
if sorted(item.get("skill_id") for item in method_policy.get("redirect_tombstone_skills", [])) != sorted(medical_method_redirect_tombstone_skill_ids):
    fail("medical-method redirect tombstones must match classification policy")
if method_policy.get("optional_router_skill_ids") != medical_method_router_skill_ids:
    fail("medical-method router ids must match classification policy")
if method_policy.get("optional_named_specialist_skill_ids") != classification_policy.get("optional_medical_method_named_specialist_skills"):
    fail("medical-method named specialist ids must match classification policy")
for skill_id, expected in method_expected.items():
    item = method_policy_by_id.get(skill_id)
    if item is None:
        fail(f"medical-method specialist policy missing {skill_id}")
    if item.get("canonical_path") != f"skills/{skill_id}/SKILL.md":
        fail(f"medical-method specialist policy path wrong for {skill_id}")
    require_all(f"medical-method specialist routing tokens for {skill_id}", item.get("routing_tokens"), expected["tokens"])
    require_all(f"medical-method specialist candidate refs for {skill_id}", item.get("candidate_ref_families"), expected["refs"])
initial_draft_optional_refs = {
    "medical-reference-integrity-auditor": ["citation_source_coverage_ref"],
    "medical-display-qc": [
        "document_display_scope_coverage_ref",
        "display_render_integrity_ref",
    ],
    "medical-survival-analysis-plan": [
        "fixed_horizon_risk_semantics_ref",
        "survival_estimand_plan_ref",
        "decision_curve_validity_ref",
    ],
    "medical-data-freeze-and-analysis-readiness-reviewer": [
        "clinical_analysis_input_identity_ref"
    ],
}
for skill_id, refs in initial_draft_optional_refs.items():
    capability_item = advanced_capability_by_id.get(skill_id)
    policy_item = method_policy_by_id.get(skill_id)
    if capability_item is None or policy_item is None:
        fail(f"initial-draft optional specialist catalogs missing {skill_id}")
    require_all(
        f"capability map initial-draft optional refs for {skill_id}",
        capability_item.get("candidate_ref_families"),
        refs,
    )
    require_all(
        f"module contract initial-draft optional refs for {skill_id}",
        policy_item.get("candidate_ref_families"),
        refs,
    )
    if capability_item.get("candidate_ref_families") != policy_item.get(
        "candidate_ref_families"
    ):
        fail(f"optional specialist candidate ref catalogs diverge for {skill_id}")
require_all(
    "medical-method specialist required handoff refs",
    method_policy.get("required_handoff_refs"),
    ["candidate_refs", "route_back_candidate", "owner_gate_handoff_ref"],
)
for key in [
    "can_replace_default_eight_skills",
    "can_block_default_core_progress_when_missing",
    "can_write_domain_truth",
    "can_write_runtime_state",
    "can_mutate_artifact_body",
    "can_sign_owner_receipt",
    "can_create_typed_blocker",
    "can_claim_quality_verdict",
    "can_claim_source_readiness",
    "can_claim_runtime_readiness",
    "can_claim_publication_readiness",
    "can_claim_production_readiness",
    "can_claim_current_package_authority",
    "can_claim_owner_closeout",
]:
    if method_policy.get(key) is not False:
        fail(f"medical-method specialist pack authority flag {key} must be false")
quality_policy = contract.get("professional_skill_quality_upgrade_policy") or {}
if quality_policy.get("policy_id") != "mas_scholar_skills_professional_quality_upgrade.v1":
    fail("contract missing professional skill quality upgrade policy")
quality_policy_text = json.dumps(quality_policy, ensure_ascii=False)
registry_signal_member_refs = [
    "paper_identity_ref",
    "chart_review_validation_ref",
    "phenotype_outcome_coupling_ref",
    "availability_mechanism_ref",
    "observation_opportunity_bias_ref",
    "source_generation_quality_ref",
    "claim_boundary_ref",
]
registry_signal_foldback = quality_policy.get("registry_signal_validity_pack_foldback") or {}
if registry_signal_foldback.get("pack_ref") != "registry_signal_validity_pack":
    fail("professional quality policy missing registry signal validity pack ref")
if registry_signal_foldback.get("ref_family") != "ehr_registry_signal_validity_ref":
    fail("registry signal validity pack must expose one EHR/registry ref family")
if registry_signal_foldback.get("producer_skill") != "medical-statistical-review":
    fail("registry signal validity pack producer must be medical-statistical-review")
if registry_signal_foldback.get("owner_route") != "medical-statistical-review":
    fail("registry signal validity pack must route integrated judgment to statistical review")
if registry_signal_foldback.get("reference_contract") != "references/professional-quality-ref-templates.md#ehr-registry-signal-validity-ref":
    fail("registry signal validity pack must bind the canonical reference contract")
require_all("registry signal validity member refs", registry_signal_foldback.get("member_refs"), registry_signal_member_refs)
require_all(
    "registry signal validity consumer routes",
    [item.get("skill_id") for item in registry_signal_foldback.get("consumer_routes") or []],
    [
        "medical-cohort-phenotyping",
        "medical-methodology-planner",
        "medical-data-governance",
        "medical-manuscript-writing",
        "medical-manuscript-review",
        "medical-registry-atlas-story-architect",
    ],
)
if registry_signal_foldback.get("refs_only") is not True:
    fail("registry signal validity pack must remain refs-only")
for key in [
    "can_write_domain_truth",
    "can_claim_statistical_conclusion",
    "can_claim_quality_verdict",
    "can_sign_owner_receipt",
    "can_create_typed_blocker",
    "can_claim_publication_readiness",
]:
    if registry_signal_foldback.get(key) is not False:
        fail(f"registry signal validity pack authority flag {key} must be false")
stats_module = next(
    (item for item in contract.get("modules") or [] if item.get("module_id") == "mas-scholar-skills.stats"),
    {},
)
require_all(
    "stats module registry signal validity artifacts",
    [item.get("ref_id") for item in stats_module.get("artifact_refs") or []],
    ["ehr_registry_signal_validity_ref"],
)
require_all(
    "stats module registry signal validity quality refs",
    (stats_module.get("quality_evidence") or {}).get("required_ref_shapes"),
    ["ehr_registry_signal_validity_ref"],
)
display_module = next(
    (item for item in contract.get("modules") or [] if item.get("module_id") == "mas-scholar-skills.display"),
    {},
)
display_quality_floor = display_module.get("display_quality_floor_policy") or {}
scientific_figure_quality_floor = display_quality_floor.get("scientific_figure_quality_floor_policy") or {}
display_text_safe_area_surfaces = {
    "display artifact refs": [item.get("ref_id") for item in display_module.get("artifact_refs") or []],
    "display quality evidence": (display_module.get("quality_evidence") or {}).get("required_ref_shapes"),
    "display minimum candidate refs": display_quality_floor.get("minimum_candidate_refs"),
    "scientific figure required refs": scientific_figure_quality_floor.get("required_before_gallery_or_paper_use"),
    "display learned pattern refs": (display_module.get("learned_pattern_policy") or {}).get("required_ref_shapes"),
}
for label, refs in display_text_safe_area_surfaces.items():
    require_all(label, refs, ["text_extent_safe_area_ref", "layout_qc_receipt_ref"])
require_all(
    "scientific figure learned patterns",
    scientific_figure_quality_floor.get("learned_scientific_figure_patterns"),
    [
        "text_extent_safe_area_after_final_renderer_draw",
        "layout_qc_receipt_after_fixed_canvas_export",
    ],
)
for token in [
    "K-Dense-AI/scientific-agent-skills",
    "Yuan1z0825/nature-skills",
    "1e024ea8547ada12039edbe8197aaa959d97763f",
    "c91df241a7a963ea151687ac669c5534404f53e5",
    "figure_contract_ref",
    "figure_contract_template_ref",
    "panel_evidence_chain_ref",
    "one_sentence_argument_ref",
    "claim_citation_quality_loop_ref",
    "citation_quality_action_matrix_ref",
    "review_fact_base_ref",
    "source_ref_chain_template_ref",
    "source_acceptance_decision_ref",
    "support_strength_matrix_ref",
    "data_availability_and_FAIR_metadata_checks",
    "reviewer_response_delta_audit",
    "statistical_action_matrix_ref",
    "table_shell_ref",
    "submission_action_matrix_ref",
    "medical-data-governance",
    "data_asset_manifest_ref",
    "version_diff_impact_ref",
]:
    if token not in quality_policy_text:
        fail(f"professional skill quality upgrade policy missing {token}")
expected_quality_skill_refs = {
    "medical-figure-design": [
        "figure_contract_template_ref",
        "figure_contract_ref",
        "panel_evidence_chain_ref",
        "candidate_set_ref",
        "critic_review_ref",
        "text_extent_safe_area_ref",
        "layout_qc_receipt_ref",
    ],
    "medical-figure-style": [
        "data_fidelity_ref",
        "claim_title_truth_ref",
        "label_economy_ref",
        "color_vision_check_ref",
        "export_lint_ref",
        "layout_qc_receipt_ref",
    ],
    "medical-figure-composer": [
        "multi_panel_outline_ref",
        "panel_render_receipt_ref",
        "composite_review_ref",
        "final_size_export_ref",
        "layout_qc_receipt_ref",
        "owner_gate_handoff_ref",
    ],
    "medical-manuscript-writing": ["one_sentence_argument_ref", "terminology_ledger_ref", "paragraph_job_map_ref", "claim_citation_quality_loop_ref", "citation_quality_action_matrix_ref"],
    "medical-manuscript-review": ["review_fact_base_ref", "technical_reviewer_lane", "cross_review_synthesis_ref", "claim_citation_quality_loop_ref", "citation_quality_action_matrix_ref"],
    "medical-research-lit": ["source_ref_chain_template_ref", "fallback_source_refs", "deduplication_ref", "source_acceptance_decision_ref", "support_strength_matrix_ref"],
    "medical-statistical-review": ["estimand_or_target_parameter_ref", "effect_size_and_uncertainty_ref", "statistical_action_matrix_ref", "ehr_registry_signal_validity_ref"],
    "medical-table-design": ["table_shell_ref", "table_qc_ref", "claim_table_alignment_ref"],
    "medical-submission-prep": ["journal_instruction_ref", "reporting_guideline_ref", "submission_action_matrix_ref"],
    "medical-data-governance": [
        "data_asset_manifest_ref",
        "data_dictionary_ref",
        "data_governance_assessment_ref",
        "data_operation_receipt_ref",
        "manifest_completeness_check_ref",
        "privacy_tier_check_ref",
        "study_impact_check_ref",
        "version_diff_impact_ref",
        "owner_gate_handoff_ref",
    ],
}
for skill_id, refs in expected_quality_skill_refs.items():
    require_all(f"quality refs for {skill_id}", (quality_policy.get("skill_quality_refs") or {}).get(skill_id), refs)
for key in [
    "can_add_parallel_stage_skill_authority",
    "can_require_external_runtime_install_before_candidate_refs",
    "can_claim_quality_verdict",
    "can_sign_owner_receipt",
    "can_create_typed_blocker",
    "can_claim_publication_readiness",
]:
    if quality_policy.get(key) is not False:
        fail(f"professional quality policy flag {key} must be false")
for relative, skill_id, text in [
    ("skills/medical-manuscript-writing/SKILL.md", "medical-manuscript-writing", write_skill),
    ("skills/medical-manuscript-review/SKILL.md", "medical-manuscript-review", review_skill),
    ("skills/medical-figure-design/SKILL.md", "medical-figure-design", figure_skill),
    ("skills/medical-figure-style/SKILL.md", "medical-figure-style", figure_style_skill),
    ("skills/medical-figure-composer/SKILL.md", "medical-figure-composer", figure_composer_skill),
    ("skills/medical-research-lit/SKILL.md", "medical-research-lit", lit_skill),
    ("skills/medical-statistical-review/SKILL.md", "medical-statistical-review", stats_skill),
    ("skills/medical-table-design/SKILL.md", "medical-table-design", table_skill),
    ("skills/medical-submission-prep/SKILL.md", "medical-submission-prep", submit_skill),
    ("skills/medical-data-governance/SKILL.md", "medical-data-governance", data_governance_skill),
]:
    for token in ["MAS Scholar Skills", skill_id]:
        if token not in text:
            fail(f"{relative} missing skill identity token: {token}")
    for shared_ref in [
        "docs/no-authority-boundary.md",
        "references/professional-quality-ref-templates.md",
    ]:
        if shared_ref not in text:
            fail(f"{relative} missing shared skill ref {shared_ref}")
for skill_id, text in advanced_specialist_skills.items():
    for token in [
        skill_id,
        "refs-only",
        "no-authority",
        "owner_gate_handoff_ref",
        "cannot write",
        "domain truth",
        "owner receipt",
        "typed blocker",
        "publication readiness",
        "54a2f333973147a1fd703caea6f12252e1f227d6",
    ]:
        if token not in text:
            fail(f"skills/{skill_id}/SKILL.md missing advanced specialist no-authority token: {token}")
    for token in (advanced_expected.get(skill_id, {}).get("sources") or []):
        if token not in text:
            fail(f"skills/{skill_id}/SKILL.md missing AcademicForge source token: {token}")
for skill_id, text in medical_method_specialist_skills.items():
    for token in [
        skill_id,
        "refs-only",
        "no-authority",
        "owner_gate_handoff_ref",
        "MAS truth",
        "owner receipt",
        "typed blocker",
        "publication readiness",
    ]:
        if token not in text:
            fail(f"skills/{skill_id}/SKILL.md missing medical-method specialist no-authority token: {token}")
for skill_id in redirect_tombstone_skill_ids:
    text = read_text(f"skills/{skill_id}/TOMBSTONE.md")
    target = next(
        (
            item.get("redirect_to")
            for item in [
                *advanced_policy.get("redirect_tombstone_skills", []),
                *method_policy.get("redirect_tombstone_skills", []),
            ]
            if item.get("skill_id") == skill_id
        ),
        None,
    )
    if not target:
        fail(f"redirect tombstone missing contract target for {skill_id}")
    for token in [
        skill_id,
        target,
        "redirect/tombstone",
        "refs-only",
        "no-authority",
        "owner_gate_handoff_ref",
        "MAS truth",
        "owner receipt",
        "typed blocker",
        "publication readiness",
    ]:
        if token not in text:
            fail(f"skills/{skill_id}/TOMBSTONE.md missing redirect tombstone token: {token}")
for forbidden in [
    "default opl-scholar-write",
    "default opl-scholar-review",
    "default opl-scholar-display",
]:
    if forbidden in "\n".join([readme, readme_zh, docs_index, operating_model, skill]):
        fail(f"docs must not create a parallel ScholarSkills default entry: {forbidden}")
for token in [
    "opl_connect_pubmed_pmc_search",
    "opl_connect_reference_verification",
    "opl_connect_search_ref",
    "opl_connect_reference_verification_ref",
    "pubmed_source_refs",
    "opl_connect_read_only_provider_transport_not_citation_acceptance_literature_verdict_or_domain_truth",
]:
    if token not in contract_text:
        fail(f"contract missing unified OPL Connect literature token: {token}")
for retired_token in [
    "opl scholar-skills",
    "connect_pubmed_search",
    "pubmed_connector_invocation_ref",
    "scientific_connector_invocation_refs",
    "candidate_package_ref",
    "execution_receipt_ref",
    "mas_domain_provider_lookup",
    "domain_owned_source_lookup",
    "mas_provider_lookup_ref",
    "research-integrity-reference-verification",
    "mas_domain_owned_read_only_provider_evidence_not_citation_acceptance_literature_verdict_or_domain_truth",
]:
    if retired_token in contract_text:
        fail(f"contract must not retain retired execution or PubMed token: {retired_token}")

professional_template_requirements = {
    "references/professional-quality-ref-templates.md": [
        "refs_only_lightweight_reference",
        "figure_contract_template_ref",
        "panel_evidence_chain_ref",
        "source_ref_chain_template_ref",
        "source_acceptance_decision_ref",
        "claim_citation_quality_loop_ref",
        "citation_quality_action_matrix_ref",
        "cannot write domain",
        "owner receipt",
        "typed blocker",
        "publication readiness",
    ],
    "skills/mas-scholar-skills/SKILL.md": [
        "references/professional-quality-ref-templates.md",
    ],
    "skills/medical-figure-design/SKILL.md": [
        "references/professional-quality-ref-templates.md",
        "figure_contract_template_ref",
        "panel_evidence_chain_ref",
    ],
    "skills/medical-research-lit/SKILL.md": [
        "references/professional-quality-ref-templates.md",
        "source_ref_chain_template_ref",
        "source_acceptance_decision_ref",
    ],
    "skills/medical-manuscript-writing/SKILL.md": [
        "references/professional-quality-ref-templates.md",
        "claim_citation_quality_loop_ref",
        "citation_quality_action_matrix_ref",
    ],
    "skills/medical-manuscript-review/SKILL.md": [
        "references/professional-quality-ref-templates.md",
        "claim_citation_quality_loop_ref",
        "citation_quality_action_matrix_ref",
    ],
    "contracts/scholar-skills-capability-modules.json": [
        "scholarskills_display_professional_ref_templates.v1#figure_contract_panel_evidence_chain",
        "scholarskills_lit_professional_ref_templates.v1#source_ref_chain",
        "scholarskills_write_professional_ref_templates.v1#claim_citation_quality_loop",
        "scholarskills_review_professional_ref_templates.v1#claim_citation_quality_loop",
    ],
    "contracts/capability_map.json": [
        "references/professional-quality-ref-templates.md#figure-contract-template",
        "references/professional-quality-ref-templates.md#claim-citation-quality-loop",
        "references/professional-quality-ref-templates.md#literature-sourceref-chain",
    ],
}
professional_text_by_relative = {
    "references/professional-quality-ref-templates.md": professional_ref_templates,
    "skills/mas-scholar-skills/SKILL.md": skill,
    "skills/medical-figure-design/SKILL.md": figure_skill,
    "skills/medical-research-lit/SKILL.md": lit_skill,
    "skills/medical-manuscript-writing/SKILL.md": write_skill,
    "skills/medical-manuscript-review/SKILL.md": review_skill,
    "contracts/scholar-skills-capability-modules.json": contract_text,
    "contracts/capability_map.json": json.dumps(capability_map, ensure_ascii=False),
}
for relative, tokens in professional_template_requirements.items():
    text = professional_text_by_relative[relative]
    for token in tokens:
        if token not in text:
            fail(f"{relative} missing professional quality template token: {token}")

registry_signal_template_tokens = [
    "registry_signal_validity_pack",
    "ehr_registry_signal_validity_ref",
    *registry_signal_member_refs,
    "producer_skill: medical-statistical-review",
    "owner_route: medical-statistical-review",
    "refs-only/no-authority",
]
for token in registry_signal_template_tokens:
    if token not in professional_ref_templates:
        fail(f"professional quality templates missing registry signal validity token: {token}")

for token in [
    "registry_signal_validity_pack",
    "ehr_registry_signal_validity_ref",
    *registry_signal_member_refs,
    "EHR And Registry Signal Validity Rule",
    "sole producer and professional owner route",
    "refs-only/no-authority",
]:
    if token not in stats_skill:
        fail(f"medical-statistical-review missing registry signal validity rule token: {token}")

registry_signal_consumers = {
    "skills/medical-cohort-phenotyping/SKILL.md": cohort_phenotyping_skill,
    "skills/medical-methodology-planner/SKILL.md": methodology_planner_skill,
    "skills/medical-data-governance/SKILL.md": data_governance_skill,
    "skills/medical-manuscript-writing/SKILL.md": write_skill,
    "skills/medical-manuscript-review/SKILL.md": review_skill,
}
for relative, text in registry_signal_consumers.items():
    for token in [
        "registry_signal_validity_pack",
        "ehr_registry_signal_validity_ref",
        "references/professional-quality-ref-templates.md#ehr-registry-signal-validity-ref",
        "medical-statistical-review",
    ]:
        if token not in text:
            fail(f"{relative} missing registry signal validity consumption route token: {token}")
    duplicated_members = [token for token in registry_signal_member_refs if token in text]
    if duplicated_members:
        fail(f"{relative} must consume the canonical registry signal rule without copying member refs: {duplicated_members}")

for token in [
    "registry_signal_validity_pack",
    "ehr_registry_signal_validity_ref",
    "references/professional-quality-ref-templates.md#ehr-registry-signal-validity-ref",
    "optional framing only",
    "does not produce or own",
    "medical-statistical-review",
]:
    if token not in registry_story_architect_skill:
        fail(f"medical-registry-atlas-story-architect missing optional framing boundary token: {token}")

first_draft_quality_tokens = {
    "skills/medical-manuscript-writing/kernel.py": [
        "lint_terminology_surface_ledger",
        "machine_readable_endpoints",
        "TERMINOLOGY_BOUNDARY_UNJUSTIFIED",
        "TERMINOLOGY_NOT_APPLICABLE_REASON_MISSING",
        "writes_authority",
    ],
    "skills/medical-registry-atlas-story-architect/kernel.py": [
        "lint_center_sensitivity_claim_binding",
        "CENTRAL_SENSITIVITY_CLAIM_ROW_MISSING",
        "analysis_source_ref",
        "display_refs",
        "writes_authority",
    ],
    "skills/medical-statistical-review/kernel.py": [
        "lint_denominator_semantic_separation",
        "AMBIGUOUS_PERCENT_COUNT_VISUAL_SEMANTIC",
        "FORMULA_DENOMINATOR_REF_MISMATCH",
        "shared_denominator_is_valid",
        "absolute_flagged_count",
        "writes_authority",
    ],
}
for relative, tokens in first_draft_quality_tokens.items():
    for token in tokens:
        if token not in first_draft_quality_sources[relative]:
            fail(f"{relative} missing first-draft deterministic token: {token}")

for relative, text, tokens in [
    (
        "skills/medical-manuscript-writing/SKILL.md",
        write_skill,
        [
            "first_draft_story_contract_ref",
            "terminology_surface_ledger_ref",
            "center_sensitivity_claim_binding_ref",
            "denominator_semantics_matrix_ref",
            "quality_debt_candidate_refs",
            "completed_with_quality_debt",
        ],
    ),
    (
        "skills/medical-registry-atlas-story-architect/SKILL.md",
        registry_story_architect_skill,
        [
            "handling_editor_first_draft_contract_ref",
            "denominator_state_architecture_ref",
            "center_sensitivity_claim_binding_ref",
            "candidate audit signal",
        ],
    ),
    (
        "skills/medical-statistical-review/SKILL.md",
        stats_skill,
        [
            "denominator_semantics_matrix_ref",
            "denominator_role",
            "formula",
            "center_sensitivity_claim_binding_ref",
        ],
    ),
    (
        "skills/medical-table-design/SKILL.md",
        table_skill,
        [
            "denominator_semantics_matrix_ref",
            "final_embedding_readability_ref",
            "Programmatic non-overflow",
        ],
    ),
    (
        "skills/medical-manuscript-review/SKILL.md",
        review_skill,
        [
            "first_draft_pre_review_ref",
            "quality_debt_candidate_refs",
            "terminology_surface_ledger_ref",
            "center_sensitivity_claim_binding_ref",
            "denominator_semantics_matrix_ref",
            "completed_with_quality_debt",
        ],
    ),
]:
    for token in tokens:
        if token not in text:
            fail(f"{relative} missing first-draft quality rule token: {token}")

for relative, text in [("README.md", readme), ("README.zh-CN.md", readme_zh)]:
    for token in ["registry_signal_validity_pack", "ehr_registry_signal_validity_ref", "medical-statistical-review"]:
        if token not in text:
            fail(f"{relative} missing registry signal validity documentation token: {token}")

registry_foldback_row = next(
    (line for line in professional_ref_templates.splitlines() if line.startswith("| `registry_signal_validity_pack`")),
    "",
)
require_all(
    "registry signal validity foldback row",
    [token for token in ["ehr_registry_signal_validity_ref", "medical-statistical-review", "owner_gate_handoff_ref"] if token in registry_foldback_row],
    ["ehr_registry_signal_validity_ref", "medical-statistical-review", "owner_gate_handoff_ref"],
)
figure_foldback_row = next(
    (line for line in professional_ref_templates.splitlines() if line.startswith("| `figure_evidence_contract_pack`")),
    "",
)
for ref in ["text_extent_safe_area_ref", "layout_qc_receipt_ref"]:
    if ref not in figure_foldback_row:
        fail(f"figure evidence foldback row missing {ref}")

deterministic_figure_closeout_tokens = [
    "deterministic_render_ref",
    "font_file_sha256",
    "headless_backend",
    "final_size_layout_ref",
    "single_generation_source_ref",
    "paired_export_qa_ref",
    "clean_rebuild_consistency_ref",
    "source_fingerprint",
    "output_fingerprints",
    "programmatic_figure_audit_ref",
    "layout_qc_receipt_ref",
    "final_scale_visual_qa_ref",
    "annotation_headroom",
    "boundary_clipping",
    "line_text_intersection",
    "tick_label_overlap",
    "pdf.fonttype=42",
    "PNG/PDF",
    "catalog/manifest",
    "route_back_candidate",
]
deterministic_figure_closeout_texts = {
    "skills/medical-figure-design/SKILL.md": figure_skill,
    "skills/medical-display-qc/SKILL.md": display_qc_skill,
    "references/professional-quality-ref-templates.md": professional_ref_templates,
}
for relative, text in deterministic_figure_closeout_texts.items():
    for token in deterministic_figure_closeout_tokens:
        if token not in text:
            fail(f"{relative} missing deterministic figure closeout token: {token}")

professional_projection_and_flow_tokens = [
    "final_scale_projection_ref",
    "minimum_final_embed_width_inches",
    "minimum_projected_safe_inset_points",
    "flow_accounting_integrity_ref",
    "all_quantitative_states_connected",
    "unconnected_satellite_state_count",
    "denominator_identities_passed",
    "unit_transitions_declared",
]
for relative, text in {
    "skills/medical-figure-design/SKILL.md": figure_skill,
    "references/professional-quality-ref-templates.md": professional_ref_templates,
}.items():
    for token in professional_projection_and_flow_tokens:
        if token not in text:
            fail(f"{relative} missing final-scale or accounting-flow token: {token}")

text_extent_safe_area_tokens = [
    "text_extent_safe_area_ref",
    "final_canvas",
    "safe_inset",
    "wrap_policy=automatic_semantic_wrap",
    "artist_scope=all_text_artists",
    "renderer_draw_complete",
    "artist_extent_report",
    "overflow_count=0",
    "annotation_lane",
    "composed_page_check",
    "renderer draw",
    "text bounding box",
    "tight_layout",
    "bbox_inches=tight",
    "clip_on",
    "PNG/PDF",
    "DOCX/PDF",
]
for relative, text in deterministic_figure_closeout_texts.items():
    for token in text_extent_safe_area_tokens:
        if token not in text:
            fail(f"{relative} missing text-extent safe-area token: {token}")

layout_qc_constraint_texts = {
    "skills/medical-figure-design/SKILL.md": figure_skill,
    "skills/medical-figure-style/SKILL.md": figure_style_skill,
    "skills/medical-figure-composer/SKILL.md": figure_composer_skill,
    "skills/medical-display-qc/SKILL.md": display_qc_skill,
    "references/professional-quality-ref-templates.md": professional_ref_templates,
}
for relative, text in layout_qc_constraint_texts.items():
    for token in [
        "layout_qc_receipt_ref",
        "bbox registry",
        "annotation",
        "plotting/data",
        "minimum",
        "fixed canvas",
        "PNG/PDF",
    ]:
        if token not in text:
            fail(f"{relative} missing fixed-canvas layout QC token: {token}")

for relative, text in deterministic_figure_closeout_texts.items():
    for token in [
        "renderer-measured",
        "manual line breaks",
        "bbox_inches=None",
        "tight-crop",
        "long-string",
        "extreme-value",
        "full-width",
        "SHA-256",
    ]:
        if token not in text:
            fail(f"{relative} missing measured-layout regression token: {token}")

if display_receipt_templates.get("schema_version") != "1.6.0":
    fail("display receipt templates must use schema_version 1.6.0")
require_all(
    "display receipt chain",
    display_receipt_templates.get("receipt_chain"),
    [
        "professional_figure_workflow_ref",
        "figure_contract_ref",
        "render_or_generation_receipt_ref",
        "layout_qc_receipt_ref",
        "visual_qa_receipt_ref",
        "owner_gate_handoff_ref",
    ],
)
if professional_figure_workflow_schema.get("$schema") != (
    "https://json-schema.org/draft/2020-12/schema"
):
    fail("professional figure workflow must use JSON Schema draft 2020-12")
workflow_surface = (
    professional_figure_workflow_schema.get("properties", {})
    .get("surface_kind", {})
    .get("const")
)
if workflow_surface != "mas_scholar_skills_professional_figure_workflow_candidate.v1":
    fail("professional figure workflow schema has wrong surface kind")
workflow_template = display_receipt_templates.get("professional_figure_workflow_ref") or {}
if workflow_template.get("schema_ref") != "contracts/professional-figure-workflow.schema.json":
    fail("display receipt contract must bind the professional figure workflow schema")
if workflow_template.get("new_or_materially_repaired_figure_requires") != [
    "medical-figure-design"
]:
    fail("professional figure workflow must require medical-figure-design")
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

modules = contract.get("modules")
if not isinstance(modules, list) or len(modules) != 10:
    fail("contract must contain eight professional modules and two package runtime adapter modules")
active_module_ids = {item.get("module_id") for item in modules}
expected_active_module_order = [
    "mas-scholar-skills.display",
    "mas-scholar-skills.tables",
    "mas-scholar-skills.stats",
    "mas-scholar-skills.lit",
    "mas-scholar-skills.write",
    "mas-scholar-skills.review",
    "mas-scholar-skills.submit",
    "mas-scholar-skills.data",
    "mas-scholar-skills.reference-provider-adapters",
    "mas-scholar-skills.scientific-search-adapters",
]
expected_active_module_ids = set(expected_active_module_order)
if active_module_ids != expected_active_module_ids:
    fail("active module ids must use mas-scholar-skills.* canonical ids")
if [item.get("module_id") for item in modules] != expected_active_module_order:
    fail("active modules must keep the canonical projection order")
professional_modules = modules[:-2]
runtime_adapter_module = modules[-2]
search_runtime_adapter_module = modules[-1]
if runtime_adapter_module.get("module_id") != runtime_module_id:
    fail("reference-provider adapter module must follow the professional module catalog")
if runtime_adapter_module.get("module_kind") != "opl_connect_reference_provider_adapter":
    fail("reference-provider adapter module must declare its runtime module kind")
if runtime_adapter_module.get("profile_ref") != runtime_binding.get("profile_ref"):
    fail("module catalog and runtime binding profile refs must match")
if runtime_adapter_module.get("registry_ref") != runtime_binding.get("registry_ref"):
    fail("module catalog and runtime binding registry refs must match")
if runtime_adapter_module.get("adapter_abi") != runtime_binding.get("adapter_abi"):
    fail("module catalog and runtime binding adapter ABIs must match")
if runtime_adapter_module.get("adapter_ids") != profile_adapter_ids:
    fail("module catalog and provider profile adapter ids must match")
state_machine_contract = runtime_adapter_module.get("state_machine_contract") or {}
if state_machine_contract.get("operations") != ["build_request", "parse_response", "next_step"]:
    fail("reference-provider adapter module must expose the three bounded state-machine phases")
if state_machine_contract.get("max_steps") != 2:
    fail("reference-provider adapter module must cap provider state machines at two steps")
if state_machine_contract.get("http_execution_owner") != "opl_connect":
    fail("OPL Connect must remain the HTTP execution owner")
if any(value is not False for value in (runtime_adapter_module.get("authority_boundary") or {}).values()):
    fail("reference-provider adapter module authority flags must all be false")
if runtime_adapter_module.get("allowed_writes") != []:
    fail("reference-provider adapter module must not declare writes")
if search_runtime_adapter_module.get("module_id") != search_runtime_module_id:
    fail("scientific search adapter module must follow the reference-provider adapter module")
if search_runtime_adapter_module.get("module_kind") != "opl_connect_scientific_search_adapter":
    fail("scientific search adapter module must declare its runtime module kind")
if search_runtime_adapter_module.get("profile_ref") != search_runtime_binding.get("profile_ref"):
    fail("scientific search module catalog and runtime binding profile refs must match")
if search_runtime_adapter_module.get("registry_ref") != search_runtime_binding.get("registry_ref"):
    fail("scientific search module catalog and runtime binding registry refs must match")
if search_runtime_adapter_module.get("adapter_abi") != search_runtime_binding.get("adapter_abi"):
    fail("scientific search module catalog and runtime binding adapter ABIs must match")
if search_runtime_adapter_module.get("adapter_ids") != search_profile_adapter_ids:
    fail("scientific search module catalog and provider profile adapter ids must match")
search_state_machine_contract = search_runtime_adapter_module.get("state_machine_contract") or {}
if search_state_machine_contract.get("operations") != ["build_search_request", "parse_search_response"]:
    fail("scientific search adapter module must expose its two bounded state-machine phases")
if search_state_machine_contract.get("max_steps") != 1:
    fail("scientific search adapter module must cap provider searches at one step")
if search_state_machine_contract.get("http_execution_owner") != "opl_connect":
    fail("OPL Connect must remain the scientific search HTTP execution owner")
if search_state_machine_contract.get("provider_scope") != "crossref_openalex_generic_metadata_coverage_and_citation_graph_fallback_only":
    fail("scientific search adapter module must remain limited to Crossref/OpenAlex fallback discovery")
if search_state_machine_contract.get("excluded_primary_biomedical_discovery_route") != "opl_connect_pubmed_pmc_framework_search":
    fail("scientific search adapter module must route PubMed/PMC discovery to Framework-owned OPL Connect")
if any(value is not False for value in (search_runtime_adapter_module.get("authority_boundary") or {}).values()):
    fail("scientific search adapter module authority flags must all be false")
if search_runtime_adapter_module.get("allowed_writes") != []:
    fail("scientific search adapter module must not declare writes")

if capability_pack_consumption.get("canonical_owner_repo") != "mas-scholar-skills":
    fail("capability-pack descriptor policy must keep mas-scholar-skills as canonical owner")
if capability_pack_consumption.get("consumer") != "one-person-lab":
    fail("capability-pack descriptor policy must name one-person-lab as consumer")
require_all(
    "capability-pack descriptor sources",
    capability_pack_consumption.get("descriptor_sources"),
    [
        ".codex-plugin/plugin.json",
        "skills/mas-scholar-skills/SKILL.md",
        "contracts/scholar-skills-capability-modules.json",
        "contracts/opl_capability_package_manifest.json",
        "contracts/reference-provider-adapters/scientific-metadata.json",
        "contracts/reference-provider-adapters/reference-provider-adapter-registry.json",
        "contracts/scientific-search-adapters/scientific-search.json",
        "contracts/scientific-search-adapters/scientific-search-adapter-registry.json",
    ],
)
for key in [
    "module_execution_projection",
    "candidate_artifact_materialization",
    "runtime_bridge_projection",
    "can_write_domain_truth",
    "can_mutate_artifact_body",
    "can_sign_owner_receipt",
    "can_create_typed_blocker",
    "can_claim_quality_verdict",
    "can_claim_publication_readiness",
    "can_claim_current_package_authority",
]:
    if capability_pack_consumption.get(key) is not False:
        fail(f"capability-pack descriptor policy flag {key} must be false")
if capability_pack_consumption.get("module_execution_projection_scope") != "professional_skill_modules_only":
    fail("retired module execution projection flag must be scoped to professional skill modules")
if capability_pack_consumption.get("runtime_adapter_module_projection") is not True:
    fail("capability package must expose its pure runtime adapter modules")
if capability_pack_consumption.get("runtime_adapter_module_ids") != runtime_module_ids:
    fail("capability package runtime adapter module ids must match the package binding")
if capability_pack_consumption.get("runtime_adapter_execution_owner") != "opl_connect":
    fail("OPL Connect must execute adapter-declared HTTP requests")
expected_legacy_module_ids = {
    "mas-scholar-skills.display": "opl.scholarskills.display",
    "mas-scholar-skills.tables": "opl.scholarskills.tables",
    "mas-scholar-skills.stats": "opl.scholarskills.stats",
    "mas-scholar-skills.lit": "opl.scholarskills.lit",
    "mas-scholar-skills.write": "opl.scholarskills.write",
    "mas-scholar-skills.review": "opl.scholarskills.review",
    "mas-scholar-skills.submit": "opl.scholarskills.submit",
    "mas-scholar-skills.data": "opl.scholarskills.data",
}
for item in modules:
    module_id = item.get("module_id")
    expected_legacy = expected_legacy_module_ids.get(module_id)
    if expected_legacy and expected_legacy not in (item.get("legacy_module_ids") or []):
        fail(f"{module_id} must retain {expected_legacy} only as a legacy alias")
for retired_module_id in ["mas-scholar-skills.omics", "mas-scholar-skills.intake"]:
    if retired_module_id in active_module_ids:
        fail(f"{retired_module_id} must not be an active ScholarSkills module")

standard_handoff_refs = [
    "source_pack_ref",
    "candidate_refs",
    "owner_gate_handoff_ref",
]
epistemic_review_scope_ref = "epistemic_review_scope_ref"
retired_input_scope_signature_ref = "input_scope_signature_ref"
standard_handoff = contract.get("standard_handoff_ref_families") or {}
if standard_handoff.get("policy_id") != "scholarskills_standard_refs_only_handoff.v3":
    fail("contract missing standard refs-only handoff policy")
if standard_handoff.get("applies_to_modules") != "active_professional_skill_modules":
    fail("standard handoff policy must apply to active professional skill modules")
require_all("standard handoff refs", standard_handoff.get("required_ref_shapes"), standard_handoff_refs)
require_all(
    "standard optional epistemic context refs",
    standard_handoff.get("optional_context_refs"),
    [epistemic_review_scope_ref],
)
if "optional_ref_shapes" in standard_handoff:
    fail("ScholarSkills must not publish a second optional review handoff surface")
if standard_handoff.get("no_authority_policy") != "source_pack_candidate_refs_and_owner_gate_handoff_only":
    fail("standard handoff policy must stay refs-only/no-authority")
for key in [
    "can_write_domain_truth",
    "can_write_runtime_state",
    "can_mutate_artifact_body",
    "can_sign_owner_receipt",
    "can_create_typed_blocker",
    "can_claim_publication_readiness",
    "can_claim_owner_acceptance",
    "can_claim_current_package_authority",
]:
    if standard_handoff.get(key) is not False:
        fail(f"standard handoff authority flag {key} must be false")

epistemic_policy = standard_handoff.get("epistemic_provenance_context_policy") or {}
expected_epistemic_policy = {
    "context_ref": epistemic_review_scope_ref,
    "surface_kind": "opl_epistemic_review_scope",
    "version": "opl-epistemic-review-scope.v2",
    "contract_ref": (
        "opl-framework:contracts/opl-framework/"
        "epistemic-review-scope-v2.schema.json"
    ),
    "purpose": (
        "prevent_ai_hallucination_and_support_audit_recalculation_and_"
        "reproduction"
    ),
    "evidence_profile": "epistemic_provenance",
    "trust_model": "trusted_local_workspace",
    "relationship_to_skill": (
        "optional_owner_supplied_context_not_skill_produced_handoff_or_"
        "currentness_control"
    ),
    "skill_records_only_refs_actually_inspected": True,
    "optional_artifact_hash_role": "locator_stale_hint_and_deduplication_only",
    "hash_change_alone_invalidates_review": False,
    "governance_metadata_layout_or_package_wrapper_invalidates_scientific_review": False,
    "release_integrity_is_separate": True,
    "missing_context_blocks_skill_use": False,
    "skill_can_compute_scope_digest": False,
    "skill_can_build_upstream_hash_closure": False,
    "skill_can_decide_review_currentness": False,
    "skill_can_invalidate_prior_review": False,
    "skill_can_schedule_review_or_retry": False,
    "skill_can_enforce_attempt_budget": False,
    "ownership": {
        "generic_scope_validation_currentness_and_attempt_enforcement": "opl_framework",
        "domain_dependencies_and_verdict": "consuming_domain_owner",
        "professional_quality_rules": "mas_scholar_skills",
    },
}
if epistemic_policy != expected_epistemic_policy:
    fail("ScholarSkills epistemic context must stay lightweight and Framework-owned")

retired_aliases = standard_handoff.get("retired_optional_ref_aliases") or {}
if retired_aliases != {
    retired_input_scope_signature_ref: {
        "state": "retired_read_only_compatibility",
        "must_not_be_generated": True,
        "must_not_drive_currentness_or_receipt_reuse": True,
        "must_not_create_blocker_or_retry": True,
    }
}:
    fail("legacy input scope signature must remain read-only compatibility only")
for retired_digest_field in [
    "input_scope_signature_policy",
    "canonical_digest_member_fields",
    "canonical_payload_exact_keys",
    "canonical_upstream_binding_exact_keys",
    "scope_signature_sha256",
    "upstream_scope_bindings",
    "golden_vector",
]:
    if retired_digest_field in standard_handoff:
        fail(f"ScholarSkills must not own review digest field {retired_digest_field}")

require_all(
    "package content lock epistemic reference",
    (package_manifest.get("content_lock") or {}).get("paths"),
    ["references/professional-quality-ref-templates.md"],
)

require_all(
    "medical-method optional epistemic context refs",
    method_policy.get("optional_context_refs"),
    [epistemic_review_scope_ref],
)
for skill_id in ["medical-reference-integrity-auditor", "medical-display-qc"]:
    for candidate_refs, label in [
        (
            (method_policy_by_id.get(skill_id) or {}).get("candidate_ref_families") or [],
            f"{skill_id} owner contract candidate refs",
        ),
        (
            (advanced_capability_by_id.get(skill_id) or {}).get("candidate_ref_families") or [],
            f"{skill_id} capability map candidate refs",
        ),
    ]:
        if retired_input_scope_signature_ref in candidate_refs:
            fail(f"{label} must not generate the retired input scope signature")
        if epistemic_review_scope_ref in candidate_refs:
            fail(f"{label} must not emit owner-supplied epistemic context")

scope_skill_texts = {
    "manuscript_review": review_skill,
    "statistical_review": stats_skill,
    "reference_integrity": reference_integrity_skill,
    "display_qc": display_qc_skill,
    "submission_prep": submit_skill,
}
for scope_id, text in scope_skill_texts.items():
    for token in [
        epistemic_review_scope_ref,
        "scope digest",
    ]:
        if token not in text:
            fail(f"{scope_id} skill missing lightweight epistemic token: {token}")
    if retired_input_scope_signature_ref in text:
        fail(f"{scope_id} skill must not generate the retired input scope signature")
for capability_id in [
    "medical-manuscript-review",
    "medical-statistical-review",
    "medical-submission-prep",
]:
    require_all(
        f"{capability_id} epistemic context verification ref",
        (capability_by_id.get(capability_id) or {}).get("verification_refs"),
        ["references/professional-quality-ref-templates.md#epistemic-provenance-context"],
    )
for skill_id in ["medical-reference-integrity-auditor", "medical-display-qc"]:
    require_all(
        f"{skill_id} epistemic context verification ref",
        (advanced_capability_by_id.get(skill_id) or {}).get("verification_refs"),
        ["references/professional-quality-ref-templates.md#epistemic-provenance-context"],
    )
for token in [
    "prevent AI hallucination",
    "trusted local workspace",
    "do not copy the whole scope",
    "must not invalidate medical, statistical, or reference review",
    "release and installation integrity use a separate OPL contract",
    "Do not generate it",
]:
    if token not in professional_ref_templates:
        fail(f"professional quality templates missing epistemic provenance token: {token}")

for module in professional_modules:
    module_id = module.get("module_id")
    display_name = module.get("display_name")
    if not module_id or module_id not in skill:
        fail(f"SKILL.md missing module id {module_id}")
    if not display_name or display_name not in skill:
        fail(f"SKILL.md missing display name {display_name}")
    boundary = module.get("authority_boundary", {})
    for key in [
        "can_write_domain_truth",
        "can_write_runtime_state",
        "can_mutate_artifact_body",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_publication_readiness",
        "can_claim_owner_acceptance",
        "can_claim_current_package_authority",
    ]:
        if boundary.get(key) is not False:
            fail(f"{module_id} authority flag {key} must be false")
    receipt_policy = module.get("receipt_policy") or {}
    if receipt_policy.get("refs_role") != "downstream_owner_consumption_refs_only_not_scholarskills_acceptance_or_signature":
        fail(f"{module_id} receipt refs must be downstream owner-consumption refs only")
    if receipt_policy.get("owner_consumption_policy") != "MAS_or_domain_owner_must_issue_owner_receipt_typed_blocker_route_back_or_artifact_mutation":
        fail(f"{module_id} receipt policy must route authority back to MAS/domain owner")
    for key in [
        "can_claim_owner_acceptance",
        "can_claim_publication_readiness",
        "can_claim_current_package_authority",
        "can_create_typed_blocker",
    ]:
        if receipt_policy.get(key) is not False:
            fail(f"{module_id} receipt policy flag {key} must be false")
    quality = module.get("quality_evidence") or {}
    if quality.get("handoff_policy") != "standard_refs_only_source_pack_candidate_refs_owner_gate_handoff":
        fail(f"{module_id} quality evidence missing standard handoff policy")
    require_all(f"{module_id} standard handoff refs", quality.get("required_ref_shapes"), standard_handoff_refs)

expected_descriptor_entry = {
    "entry_id": "capability_pack_descriptor",
    "entry_kind": "capability_pack_descriptor_readback",
    "command": "opl connect skills --domain mas-scholar-skills --json",
    "mutation": False,
    "descriptor_only": True,
}
for module in professional_modules:
    entries = module.get("invocation_entries") or []
    if not entries or entries[0] != expected_descriptor_entry:
        fail(f"{module.get('module_id')} must begin with the generic capability-pack descriptor readback")
    if any(str(entry.get("command") or "").startswith("opl scholar-skills") for entry in entries):
        fail(f"{module.get('module_id')} must not retain the retired OPL ScholarSkills CLI")
    if module.get("module_id") == "mas-scholar-skills.lit":
        expected_search = {
            "entry_id": "opl_connect_pubmed_pmc_search",
            "entry_kind": "opl_connect_scientific_search",
            "command": "opl connect scientific search --provider <pubmed|pmc> --query <query> --limit <n> --json",
            "mutation": False,
            "descriptor_only": False,
            "provider_priority": [
                "pubmed_pmc_first",
                "crossref_metadata_fallback",
                "openalex_coverage_or_citation_graph_fallback",
            ],
            "authority_boundary": "opl_connect_read_only_provider_transport_not_citation_acceptance_literature_verdict_or_domain_truth",
        }
        expected_verification = {
            "entry_id": "opl_connect_reference_verification",
            "entry_kind": "opl_connect_reference_verification",
            "command": "opl connect references verify --references-file <path> --providers pubmed,pmc --json",
            "mutation": False,
            "descriptor_only": False,
            "authority_boundary": "opl_connect_metadata_provider_receipt_only_not_citation_acceptance_literature_verdict_or_domain_truth",
        }
        if entries != [expected_descriptor_entry, expected_search, expected_verification]:
            fail("Lit must expose only the package descriptor and unified OPL Connect search/verification entries")
    elif entries != [expected_descriptor_entry]:
        fail(f"{module.get('module_id')} must not project a module execution surface")

contract_boundary = contract.get("authority_boundary") or {}
for key in [
    "can_claim_publication_readiness",
    "can_claim_owner_acceptance",
    "can_claim_current_package_authority",
]:
    if contract_boundary.get(key) is not False:
        fail(f"top-level authority flag {key} must be false")
feedbackops = contract.get("feedbackops_refs_only_adapter_policy") or {}
if feedbackops.get("policy_id") != "scholarskills_feedbackops_refs_only_adapter.v1":
    fail("contract missing FeedbackOps refs-only adapter policy")
if feedbackops.get("adapter_role") != "opl_feedbackops_refs_only_capability_adapter":
    fail("FeedbackOps adapter role must stay refs-only capability adapter")
if feedbackops.get("evidence_profile") != "target_agent_feedback_external_suite":
    fail("FeedbackOps adapter must declare target_agent_feedback_external_suite profile")
require_all(
    "FeedbackOps input refs",
    feedbackops.get("input_ref_families"),
    [
        "delivery_feedback_ref",
        "feedbackops_intake_ref",
        "target_agent_feedback_external_suite_ref",
    ],
)
require_all(
    "FeedbackOps output refs",
    feedbackops.get("output_ref_families"),
    [
        "candidate_refs",
        "quality_hints",
        "display_capability_suggestion_ref",
        "write_capability_suggestion_ref",
        "review_capability_suggestion_ref",
        "route_back_candidate_ref",
        "stop_or_continue_recommendation_ref",
    ],
)
route_back_policy = feedbackops.get("route_back_ref_policy") or {}
require_all("FeedbackOps consuming owners", route_back_policy.get("consuming_owners"), ["MAS", "OMA"])
if route_back_policy.get("feedbackops_intake_refs_consumed_as") != "evidence_input":
    fail("FeedbackOps intake refs must be consumed as evidence input")
if route_back_policy.get("route_back_refs_consumed_as") != "owner_surface_routing_input":
    fail("FeedbackOps route-back refs must be consumed as owner-surface routing input")
route_back_consumption = route_back_policy.get("consumption_policy") or ""
for token in ["MAS_or_OMA", "owner_receipt", "typed_blocker", "quality_verdict", "current_package_update", "own_authority_surface"]:
    if token not in route_back_consumption:
        fail(f"FeedbackOps route-back consumption policy missing {token}")
no_authority_policy = feedbackops.get("no_authority_policy") or ""
for token in [
    "candidate_refs",
    "quality_hints",
    "display_write_review_capability_suggestions",
    "cannot_sign_owner_receipt",
    "create_typed_blocker",
    "claim_quality_verdict",
    "write_MAS_current_package",
]:
    if token not in no_authority_policy:
        fail(f"FeedbackOps no-authority policy missing {token}")
for key in [
    "can_generate_candidate_refs",
    "can_generate_quality_hints",
    "can_suggest_display_write_review_capabilities",
    "can_act_as_evidence_input",
]:
    if feedbackops.get(key) is not True:
        fail(f"FeedbackOps allowed capability flag {key} must be true")
for key in [
    "can_sign_owner_receipt",
    "can_create_typed_blocker",
    "can_claim_quality_verdict",
    "can_write_mas_current_package",
    "can_write_domain_truth",
    "can_write_runtime_state",
    "can_mutate_artifact_body",
    "can_claim_owner_acceptance",
    "can_claim_publication_readiness",
    "can_claim_current_package_authority",
]:
    if feedbackops.get(key) is not False:
        fail(f"FeedbackOps authority flag {key} must be false")

trigger = contract.get("feedback_self_evolution_trigger") or {}
if trigger.get("surface_kind") != "opl_foundry_agent_feedback_self_evolution_trigger":
    fail("contract missing feedback_self_evolution_trigger surface")
if trigger.get("series_membership") != "framework_capability_package":
    fail("feedback self evolution trigger must declare framework_capability_package membership")
if trigger.get("policy_id") != "standard_agent_feedback_self_evolution_trigger.v1":
    fail("feedback self evolution trigger must pin the standard policy id")
if trigger.get("feedbackops_event_kind") != "target_agent_feedback_external_suite":
    fail("feedback self evolution trigger must consume target_agent_feedback_external_suite")
if trigger.get("accepted_feedback_profile") != "target_agent_feedback_external_suite":
    fail("feedback self evolution trigger accepted profile must stay target_agent_feedback_external_suite")
if trigger.get("adapter_kind") != "framework_capability_feedback_adapter":
    fail("feedback self evolution trigger must expose framework_capability_feedback_adapter")
if trigger.get("repo_fix_execution_requires_opl_developer_mode") is not True:
    fail("feedback self evolution trigger must require OPL developer mode for repo fixes")
require_all(
    "feedback self evolution trigger developer mode gate refs",
    trigger.get("developer_mode_execution_gate_refs"),
    [
        "opl-developer-mode:repo-fix-execution",
        "opl-developer-mode:direct-fix-or-fork-pr-route",
    ],
)
require_all(
    "feedback self evolution trigger owner closeout readback refs",
    trigger.get("owner_closeout_readback_refs"),
    [
        "contracts/scholar-skills-capability-modules.json#/feedbackops_refs_only_adapter_policy/route_back_ref_policy",
        "contracts/capability_map.json#/owner_closeout_boundary",
        "docs/no-authority-boundary.md",
    ],
)
if trigger.get("contract_can_trigger_execution") is not False:
    fail("feedback self evolution trigger contract must stay non-executing")
trigger_boundary = trigger.get("authority_boundary") or {}
for key in [
    "refs_only",
]:
    if trigger_boundary.get(key) is not True:
        fail(f"feedback self evolution trigger authority flag {key} must be true")
for key in [
    "can_write_domain_truth",
    "can_mutate_artifact_body",
    "can_authorize_quality_or_export",
    "can_create_owner_receipt",
    "can_create_typed_blocker",
    "can_execute_repo_patch_without_developer_mode",
]:
    if trigger_boundary.get(key) is not False:
        fail(f"feedback self evolution trigger authority flag {key} must be false")

for token in [
    "docs/no-authority-boundary.md",
    "docs/mas-scholar-skills-operating-model.md",
    "docs/capability-modules.md",
    "contracts/scholar-skills-capability-modules.json",
    "contracts/capability_map.json",
    "medical-manuscript-writing",
    "medical-manuscript-review",
    "medical-figure-design",
    "medical-research-lit",
    "medical-statistical-review",
    "medical-table-design",
    "medical-submission-prep",
    "medical-data-governance",
]:
    if token not in skill:
        fail(f"aggregate SKILL.md missing routing or owner-reference token: {token}")

gallery_manifest = read_json("gallery/medical-display/gallery_manifest.json")
snapshot = read_json("gallery/medical-display/gallery_snapshot.json")
display_module = next(
    (item for item in modules if item.get("module_id") == "mas-scholar-skills.display"),
    None,
)
if display_module is None:
    fail("contract missing Display module")

display_pack_manifest = root / "packs/medical-display-core/display_pack.toml"
if not display_pack_manifest.is_file():
    fail("missing Scholar Display source pack manifest")
display_pack_text = display_pack_manifest.read_text(encoding="utf-8")
for token in [
    'pack_id = "fenggaolab.org.medical-display-core"',
    'pack_kind = "display_pack"',
    'capability_kind = "reference_pack"',
    'source = "scholarskills-managed-external-pack"',
    'opl_pack_descriptor_ref = "opl_pack.json"',
    'supported_actions = ["render", "gallery"]',
    'supported_render_modes = ["final", "candidate"]',
    'authority = false',
    'publication_ready = false',
    'artifact_authority = false',
    'owner_receipt_authority = false',
    'typed_blocker_authority = false',
    'heavy_render_intermediates_excluded = true',
]:
    if token not in display_pack_text:
        fail(f"Display source pack manifest missing token: {token}")
for relative in [
    "packs/medical-display-core/opl_pack.json",
    "packs/medical-display-core/render.R",
    "packs/medical-display-core/templates/roc_curve_binary/template.toml",
    "packs/medical-display-core/rlib/medicaldisplaycore/evidence_renderer.R",
    "packs/medical-display-core/src/fenggaolab_org_medical_display_core/__init__.py",
    "packs/medical-display-core/canonical_template_catalog.json",
    "packs/medical-display-core/renderer_dependency_profile.json",
]:
    if not (root / relative).is_file():
        fail(f"missing Display source pack file {relative}")
for forbidden_wrapper in (root / "packs/medical-display-core/templates").glob("*/render*.R"):
    fail(f"Display source pack must use pack-level render.R, found {forbidden_wrapper.relative_to(root)}")
for forbidden in [
    "packs/medical-display-core/outputs",
    "packs/medical-display-core/medical_display_gallery_assets",
    "packs/medical-display-core/render-cache",
]:
    if (root / forbidden).exists():
        fail(f"forbidden Display source pack intermediate present: {forbidden}")
for forbidden_pattern in ["*.png", "*.svg", "*.html", "*.layout.json", "*render_cache*"]:
    if list((root / "packs/medical-display-core").rglob(forbidden_pattern)):
        fail(f"forbidden generated Display source pack artifact matched {forbidden_pattern}")
display_refs = json.dumps(display_module.get("artifact_refs") or [], ensure_ascii=False)
if "scholar_display_pack_source_ref" not in display_refs:
    fail("Display module missing scholar_display_pack_source_ref")
if "scholar_display_gallery_review_package_ref" not in display_refs:
    fail("Display module missing scholar_display_gallery_review_package_ref")
display_floor = display_module.get("display_quality_floor_policy") or {}
if display_floor.get("source_pack_ref") != "packs/medical-display-core/display_pack.toml":
    fail("Display module source_pack_ref must point at Scholar Display source pack")
if display_floor.get("gallery_review_package_ref") != "gallery/medical-display/gallery_snapshot.json":
    fail("Display module gallery_review_package_ref must point at Scholar Display review package")
if display_floor.get("source_pack_policy") != "generic_template_renderer_source_authority_false":
    fail("Display module source_pack_policy must keep authority false")
if display_floor.get("gallery_review_package_policy") != "compact_review_refs_authority_false":
    fail("Display module gallery_review_package_policy must keep authority false")

modules_by_id = {item.get("module_id"): item for item in modules}

def require_module(module_id: str) -> dict:
    module = modules_by_id.get(module_id)
    if module is None:
        fail(f"contract missing {module_id}")
    return module

def require_artifact_refs(module: dict, refs) -> None:
    actual = [item.get("ref_id") for item in module.get("artifact_refs") or []]
    require_all(f"{module.get('module_id')} artifact_refs", actual, refs)

def require_quality_refs(module: dict, refs) -> None:
    require_all(
        f"{module.get('module_id')} quality refs",
        module.get("quality_evidence", {}).get("required_ref_shapes"),
        refs,
    )
    if module.get("quality_evidence", {}).get("can_claim_quality_verdict") is not False:
        fail(f"{module.get('module_id')} must not claim quality verdict")

def require_output_schema(module: dict, refs) -> None:
    require_all(f"{module.get('module_id')} output schema refs", module.get("output_schema_refs"), refs)

def require_learned_policy(module: dict, policy_id: str, expected_refs, source_tokens=(), boundary_tokens=()) -> None:
    policy = module.get("learned_pattern_policy") or {}
    if policy.get("policy_id") != policy_id:
        fail(f"{module.get('module_id')} learned pattern policy id must be {policy_id}")
    if policy.get("classification") != "adapt_refs_only":
        fail(f"{module.get('module_id')} learned pattern policy must be adapt_refs_only")
    if expected_refs:
        require_all(f"{module.get('module_id')} learned pattern required refs", policy.get("required_ref_shapes"), expected_refs)
    policy_blob = json.dumps(policy, ensure_ascii=False)
    for token in source_tokens:
        if token not in policy_blob:
            fail(f"{module.get('module_id')} learned pattern missing source token {token}")
    for token in boundary_tokens:
        if token not in policy_blob:
            fail(f"{module.get('module_id')} learned pattern boundary missing {token}")

def require_external_fit(module: dict, expected_sources) -> None:
    external_fit = module.get("external_learning_module_fit") or {}
    if external_fit.get("policy_id") != "scholarskills_external_learning_module_fit.v1":
        fail(f"{module.get('module_id')} missing external learning module fit policy")
    if external_fit.get("progress_policy") != "external_runtime_install_not_required_before_candidate_refs_or_checklists":
        fail(f"{module.get('module_id')} external runtime progress policy is wrong")
    if external_fit.get("no_authority_policy") != "candidate_refs_only_requires_domain_owner_gate":
        fail(f"{module.get('module_id')} no-authority external learning policy is wrong")
    source_blob = json.dumps(external_fit.get("sources") or [], ensure_ascii=False)
    for source in expected_sources:
        if source not in source_blob:
            fail(f"{module.get('module_id')} external fit missing source {source}")

def require_ai_judgment_candidate_policy(module: dict, policy: dict) -> None:
    token = policy.get("ai_judgment_policy")
    if not token:
        fail(f"{module.get('module_id')} missing ai judgment candidate policy")
    for required in ["candidate", "route_back"]:
        if required not in token and required.replace("_", "-") not in token:
            fail(f"{module.get('module_id')} ai judgment policy missing {required}")
    for forbidden in ["domain_truth", "owner_receipt", "publication_readiness"]:
        if not re.search(rf"cannot(?:_claim|_sign|_write)?_[a-z_]*{forbidden}", token):
            fail(f"{module.get('module_id')} ai judgment policy must forbid {forbidden}")

def require_external_fit_ai_policy(module: dict) -> None:
    require_ai_judgment_candidate_policy(module, module.get("external_learning_module_fit") or {})

initial_draft_module_refs = {
    "mas-scholar-skills.display": [
        "document_display_scope_coverage_ref",
        "display_render_integrity_ref",
    ],
    "mas-scholar-skills.tables": ["baseline_table_traceability_ref"],
    "mas-scholar-skills.stats": [
        "validation_partition_integrity_ref",
        "endpoint_analysis_set_reconciliation_ref",
        "model_complexity_sparse_event_ref",
        "linked_prediction_performance_ref",
        "decision_curve_validity_ref",
    ],
    "mas-scholar-skills.write": ["medical_initial_draft_preflight_candidate_ref"],
    "mas-scholar-skills.review": ["medical_initial_draft_preflight_candidate_ref"],
}
for module_id, refs in initial_draft_module_refs.items():
    module = require_module(module_id)
    require_artifact_refs(module, refs)
    require_quality_refs(module, refs)

initial_draft_core_capability_refs = {
    "medical-manuscript-writing": ["medical_initial_draft_preflight_candidate_ref"],
    "medical-manuscript-review": ["medical_initial_draft_preflight_candidate_ref"],
    "medical-statistical-review": [
        "validation_partition_integrity_ref",
        "endpoint_analysis_set_reconciliation_ref",
        "model_complexity_sparse_event_ref",
        "linked_prediction_performance_ref",
        "decision_curve_validity_ref",
    ],
    "medical-table-design": ["baseline_table_traceability_ref"],
}
for capability_id, refs in initial_draft_core_capability_refs.items():
    capability = capability_by_id.get(capability_id)
    if capability is None:
        fail(f"capability map missing initial-draft capability {capability_id}")
    if capability.get("candidate_ref_families") != refs:
        fail(f"capability map initial-draft ref families diverge for {capability_id}")

stats_capability = capability_by_id["medical-statistical-review"]
expected_endpoint_validator_binding = {
    "legacy_validator": "validate_endpoint_analysis_set_reconciliation",
    "current_semantic_validator": "validate_endpoint_analysis_set_reconciliation_v2",
}
if stats_capability.get("candidate_validator_bindings") != {
    "endpoint_analysis_set_reconciliation_ref": expected_endpoint_validator_binding,
}:
    fail("statistical capability endpoint validator binding is wrong")
if "fixed_horizon_risk_semantics_ref" in set(
    stats_capability.get("candidate_ref_families") or []
):
    fail("statistical capability must not own fixed-horizon risk semantics")
survival_capability = advanced_capability_by_id.get("medical-survival-analysis-plan") or {}
if "fixed_horizon_risk_semantics_ref" not in set(
    survival_capability.get("candidate_ref_families") or []
):
    fail("survival specialist must own fixed-horizon risk semantics")

stats_module = require_module("mas-scholar-skills.stats")
stats_artifacts = {
    item.get("ref_id"): item for item in stats_module.get("artifact_refs") or []
}
endpoint_artifact = stats_artifacts.get("endpoint_analysis_set_reconciliation_ref")
if endpoint_artifact is None:
    fail("canonical stats module missing endpoint reconciliation artifact")
if {
    "legacy_validator": endpoint_artifact.get("legacy_validator"),
    "current_semantic_validator": endpoint_artifact.get(
        "current_semantic_validator"
    ),
} != expected_endpoint_validator_binding:
    fail("canonical stats endpoint artifact validator binding is wrong")
if "fixed_horizon_risk_semantics_ref" in stats_artifacts:
    fail("canonical stats module must not own fixed-horizon risk semantics")
if "fixed_horizon_risk_semantics_ref" in set(
    (stats_module.get("quality_evidence") or {}).get("required_ref_shapes") or []
):
    fail("canonical stats quality evidence must not require fixed-horizon risk semantics")

display_quality_floor = display_module.get("display_quality_floor_policy", {})
if display_quality_floor.get("graphical_abstract_strategy") != "brief_first_reference_guided_ai_candidate_not_single_template_reuse":
    fail("Display graphical abstract strategy must avoid single-template reuse")
if display_quality_floor.get("current_gallery_graphical_abstract_status") != "lower_bound_design_shell_not_reusable_template_authority":
    fail("Display graphical abstract gallery status must be lower-bound only")
scientific_floor = display_quality_floor.get("scientific_figure_quality_floor_policy", {})
if scientific_floor.get("policy_id") != "scholarskills_scientific_figure_quality_floor.v1":
    fail("Display scientific figure quality floor policy id is missing")
if scientific_floor.get("scope") != "all_scientific_display_candidates_not_only_graphical_abstract":
    fail("Display scientific figure quality floor must cover all scientific display candidates")
learned_patterns = set(scientific_floor.get("learned_scientific_figure_patterns") or [])
for pattern in [
    "figure_contract_before_plotting",
    "reference_selection_and_style_brief",
    "candidate_generation_before_owner_gate",
    "critic_review_or_route_back",
    "reference_target_preserve_list",
    "final_size_readability_inspection",
    "vector_export_when_possible",
    "source_data_statistics_and_claim_refs_preserved",
    "figure_table_count_and_clinical_value_floor",
    "figure_polish_skill_alignment_before_owner_gate",
]:
    if pattern not in learned_patterns:
        fail(f"Display scientific figure quality floor missing pattern {pattern}")
minimum_candidate_refs = set(display_quality_floor.get("minimum_candidate_refs") or [])
for ref in [
    "core_claim_and_evidence_chain_ref",
    "figure_contract_ref",
    "reference_selection_ref",
    "style_brief_ref",
    "critic_review_ref",
    "final_size_inspection_ref",
    "domain_owner_gate_ref",
]:
    if ref not in minimum_candidate_refs:
        fail(f"Display quality floor missing minimum candidate ref {ref}")
scientific_required_refs = set(scientific_floor.get("required_before_gallery_or_paper_use") or [])
for ref in [
    "figure_contract_ref",
    "reference_selection_ref",
    "style_brief_ref",
    "critic_review_ref",
    "final_size_inspection_ref",
    "source_preservation_ref",
    "domain_owner_gate_ref",
    "figure_table_volume_and_clinical_value_ref",
    "figure_polish_alignment_ref",
]:
    if ref not in scientific_required_refs:
        fail(f"Display scientific figure quality floor missing required ref {ref}")
external_learning_sources = {
    item.get("source") for item in display_quality_floor.get("external_learning_refs") or []
}
for source in [
    "K-Dense-AI/scientific-agent-skills",
    "Yuan1z0825/nature-skills",
    "google-research/papervizagent",
    "dwzhu-pku/PaperBanana",
    "VILA-Lab/FigMirror",
    "dazhiyang/scientific-plotting-skill",
]:
    if source not in external_learning_sources:
        fail(f"Display quality floor missing external learning source {source}")

module_learning_requirements = {
    "mas-scholar-skills.display": {
        "output_schema_refs": ["scholarskills_display_learned_pattern_refs.v1#visual_qa_preview_programmatic_audit_panel_code_review"],
        "refs": [
            "visual_qa_preview_ref",
            "programmatic_figure_audit_ref",
            "grayscale_color_vision_check_ref",
            "panel_to_code_review_ref",
            "complex_heatmap_or_oncoprint_ref",
        ],
        "policy_id": "scholarskills_display_external_learning_refs.v1",
        "sources": ["Haojae/scipilot-figure-skill", "littlepeachs/NaturePanelForge", "Marsilea-viz/marsilea", "Boom5426/Awesome-Virtual-Cell"],
        "boundary_tokens": ["quality_verdict", "publication_ready"],
    },
    "mas-scholar-skills.tables": {
        "output_schema_refs": ["scholarskills_tables_learned_pattern_refs.v1#table_shell_metric_alignment_qc"],
        "refs": ["table_shell_ref", "metric_extraction_ref", "booktabs_or_minimal_ink_table_ref", "table_qc_ref", "claim_table_alignment_ref"],
        "policy_id": "scholarskills_tables_external_learning_refs.v1",
        "sources": ["Master-cai/Research-Paper-Writing-Skills", "Ar9av/PaperOrchestra"],
        "boundary_tokens": ["table_truth", "publication_ready"],
    },
    "mas-scholar-skills.stats": {
        "output_schema_refs": ["scholarskills_stats_learned_pattern_refs.v1#analysis_plan_metric_reproducibility_review"],
        "refs": ["analysis_plan_ref", "effect_size_or_metric_extraction_ref", "reproducibility_check_ref", "statistical_review_ref"],
        "policy_id": "scholarskills_stats_external_learning_refs.v1",
        "sources": ["Ar9av/PaperOrchestra", "Imbad0202/academic-research-skills"],
        "boundary_tokens": ["statistical_conclusion", "domain_truth"],
    },
    "mas-scholar-skills.lit": {
        "output_schema_refs": ["scholarskills_lit_external_learning_refs.v1#query_citation_evidence_map"],
        "refs": ["query_ref", "citation_manifest_ref", "source_verification_ref", "citation_coverage_ref", "evidence_map_ref", "metadata_scrape_ref", "claim_support_ref"],
        "policy_id": "scholarskills_lit_external_learning_policy.v1",
        "sources": ["Imbad0202/academic-research-skills", "Imbad0202/academic-research-skills-codex", "Ar9av/PaperOrchestra", "Future-Scholars/paperlib"],
        "boundary_tokens": ["literature_verdict"],
    },
    "mas-scholar-skills.write": {
        "output_schema_refs": ["scholarskills_write_external_learning_refs.v1#outline_trace_draft"],
        "refs": ["section_outline_ref", "reverse_outline_ref", "claim_evidence_map_ref", "source_trace_ref", "unsupported_claim_route_back_ref", "section_draft_manifest_ref"],
        "policy_id": "scholarskills_write_external_learning_policy.v1",
        "sources": ["Master-cai/Research-Paper-Writing-Skills", "Imbad0202/academic-research-skills", "Ar9av/PaperOrchestra"],
        "boundary_tokens": ["paper_body_authority"],
    },
    "mas-scholar-skills.review": {
        "output_schema_refs": [
            "scholarskills_review_external_learning_refs.v1#adversarial_revision_route_back",
            "scholarskills_review_registry_initial_draft_refs.v1#registry_quality_floor",
        ],
        "refs": ["reviewer_report_ref", "adversarial_review_ref", "revision_action_ref", "halt_or_revert_rule_ref", "route_back_ref", "residual_risk_ref", "registry_initial_draft_quality_floor_ref"],
        "policy_id": "scholarskills_review_external_learning_policy.v1",
        "sources": ["Imbad0202/academic-research-skills", "Ar9av/PaperOrchestra"],
        "boundary_tokens": [
            "quality_verdict",
            "reviewer_receipt",
            "workflow/tool-pipeline prose",
            "conclusion self-evaluation",
            "calendar enrollment period is not promoted",
            "MAS display-pack renderer",
            "TRIPOD is cited only as a boundary reference",
            "defensible clinical story",
        ],
    },
    "mas-scholar-skills.submit": {
        "output_schema_refs": ["scholarskills_submit_external_learning_refs.v1#checklist_disclosure_export"],
        "refs": ["submission_checklist_ref", "journal_rule_ref", "format_sanity_ref", "ai_disclosure_ref", "rebuttal_audit_ref", "export_package_ref"],
        "policy_id": "scholarskills_submit_external_learning_policy.v1",
        "sources": ["Imbad0202/academic-research-skills", "Ar9av/PaperOrchestra"],
        "boundary_tokens": ["publication_readiness"],
    },
}

for module_id, requirement in module_learning_requirements.items():
    module = require_module(module_id)
    require_output_schema(module, requirement["output_schema_refs"])
    require_artifact_refs(module, requirement["refs"])
    require_quality_refs(module, requirement["refs"])
    require_learned_policy(
        module,
        requirement["policy_id"],
        requirement["refs"],
        source_tokens=requirement["sources"],
        boundary_tokens=requirement["boundary_tokens"],
    )

professional_ref_template_module_requirements = {
    "mas-scholar-skills.display": {
        "output_schema_refs": ["scholarskills_display_professional_ref_templates.v1#figure_contract_panel_evidence_chain"],
        "refs": ["figure_contract_template_ref", "panel_evidence_chain_ref"],
    },
    "mas-scholar-skills.lit": {
        "output_schema_refs": ["scholarskills_lit_professional_ref_templates.v1#source_ref_chain"],
        "refs": ["source_ref_chain_template_ref", "source_acceptance_decision_ref"],
    },
    "mas-scholar-skills.write": {
        "output_schema_refs": ["scholarskills_write_professional_ref_templates.v1#claim_citation_quality_loop"],
        "refs": ["claim_citation_quality_loop_ref", "citation_quality_action_matrix_ref"],
    },
    "mas-scholar-skills.review": {
        "output_schema_refs": ["scholarskills_review_professional_ref_templates.v1#claim_citation_quality_loop"],
        "refs": ["claim_citation_quality_loop_ref", "citation_quality_action_matrix_ref"],
    },
}

for module_id, requirement in professional_ref_template_module_requirements.items():
    module = require_module(module_id)
    require_output_schema(module, requirement["output_schema_refs"])
    require_artifact_refs(module, requirement["refs"])
    require_quality_refs(module, requirement["refs"])

medical_sci_initial_draft_requirements = {
    "mas-scholar-skills.display": {
        "refs": ["figure_table_volume_and_clinical_value_ref", "figure_polish_alignment_ref"],
    },
    "mas-scholar-skills.lit": {
        "output_schema_refs": ["scholarskills_lit_medical_sci_draft_refs.v1#reference_integrity_floor"],
        "refs": ["reference_integrity_floor_ref"],
    },
    "mas-scholar-skills.write": {
        "output_schema_refs": ["scholarskills_write_medical_sci_draft_refs.v1#body_volume_and_prose_floor"],
        "refs": ["manuscript_body_volume_floor_ref", "internal_report_prose_route_back_ref"],
    },
    "mas-scholar-skills.review": {
        "output_schema_refs": ["scholarskills_review_medical_sci_initial_draft_refs.v1#citation_body_display_prose_boundary"],
        "refs": [
            "reference_integrity_floor_ref",
            "manuscript_body_volume_floor_ref",
            "figure_table_volume_and_clinical_value_ref",
            "internal_report_prose_route_back_ref",
            "figure_polish_alignment_ref",
            "registry_descriptive_scientific_boundary_ref",
        ],
    },
}

for module_id, requirement in medical_sci_initial_draft_requirements.items():
    module = require_module(module_id)
    if requirement.get("output_schema_refs"):
        require_output_schema(module, requirement["output_schema_refs"])
    require_artifact_refs(module, requirement["refs"])
    require_quality_refs(module, requirement["refs"])

review_medical_floor = require_module("mas-scholar-skills.review").get("medical_sci_initial_draft_quality_floor_policy") or {}
if review_medical_floor.get("policy_id") != "scholarskills_medical_sci_initial_draft_quality_floor.v1":
    fail("Review missing medical SCI initial draft quality floor policy")
if review_medical_floor.get("classification") != "adapt_refs_only":
    fail("Review medical SCI initial draft policy must be adapt_refs_only")
require_all(
    "Review medical SCI initial draft required refs",
    review_medical_floor.get("required_refs"),
    [
        "reference_integrity_floor_ref",
        "manuscript_body_volume_floor_ref",
        "figure_table_volume_and_clinical_value_ref",
        "internal_report_prose_route_back_ref",
        "figure_polish_alignment_ref",
        "registry_descriptive_scientific_boundary_ref",
        "route_back_ref",
        "owner_gate_handoff_ref",
    ],
)
require_all(
    "Review medical SCI initial draft route-back triggers",
    review_medical_floor.get("route_back_candidate_triggers"),
    [
        "missing_reference_entries",
        "unresolved_citation_placeholders",
        "manuscript_body_below_section_floor",
        "result_figures_or_tables_too_sparse_for_claims",
        "result_figures_lack_clinical_interpretability",
        "internal_report_or_workflow_prose_in_manuscript_body",
        "figure_polish_skill_contract_drift",
        "registry_descriptive_paper_claims_exceed_descriptive_evidence",
        "diagnostic_or_prediction_framing_without_corresponding_design",
    ],
)
for key in [
    "can_claim_quality_verdict",
    "can_claim_publication_readiness",
    "can_claim_owner_acceptance",
    "can_claim_current_package_authority",
    "can_create_typed_blocker",
    "can_sign_owner_receipt",
]:
    if review_medical_floor.get(key) is not False:
        fail(f"Review medical SCI initial draft authority flag {key} must be false")

slr_citation_data_requirements = {
    "mas-scholar-skills.lit": {
        "output_schema_refs": ["scholarskills_lit_slr_citation_external_refs.v1#protocol_snowball_search_confirm_drop"],
        "refs": [
            "systematic_review_protocol_ref",
            "inclusion_exclusion_criteria_ref",
            "data_extraction_schema_ref",
            "quality_appraisal_ref",
            "citation_graph_snowball_ref",
            "multi_source_paper_search_ref",
            "confirm_or_drop_source_verification_ref",
        ],
        "sources": ["vitorfs/parsifal", "openags/paper-search-mcp", "LocalCitationNetwork", "kennethkhoocy/lit-review-orchestrator"],
        "policy": "learned",
    },
    "mas-scholar-skills.write": {
        "output_schema_refs": ["scholarskills_write_source_verification_refs.v1#confirm_drop_before_draft_use"],
        "refs": ["confirm_or_drop_source_verification_ref"],
        "sources": ["kennethkhoocy/lit-review-orchestrator"],
        "policy": "learned",
    },
    "mas-scholar-skills.review": {
        "output_schema_refs": ["scholarskills_review_source_verification_refs.v1#confirm_drop_adversarial_check"],
        "refs": ["confirm_or_drop_source_verification_ref"],
        "sources": ["kennethkhoocy/lit-review-orchestrator"],
        "policy": "learned",
    },
    "mas-scholar-skills.data": {
        "output_schema_refs": ["scholarskills_data_slr_metric_refs.v1#extraction_schema_quality_appraisal_metric_registry"],
        "refs": [
            "systematic_review_protocol_ref",
            "inclusion_exclusion_criteria_ref",
            "data_extraction_schema_ref",
            "quality_appraisal_ref",
            "dataset_metric_benchmark_ref",
            "result_metric_registry_ref",
        ],
        "sources": ["vitorfs/parsifal", "Papers-with-Code/SOTA"],
        "policy": "external_fit",
    },
    "mas-scholar-skills.stats": {
        "output_schema_refs": ["scholarskills_stats_metric_registry_refs.v1#dataset_metric_benchmark_result_registry"],
        "refs": ["dataset_metric_benchmark_ref", "result_metric_registry_ref"],
        "sources": ["Papers-with-Code/SOTA"],
        "policy": "learned",
    },
    "mas-scholar-skills.tables": {
        "output_schema_refs": ["scholarskills_tables_metric_registry_refs.v1#result_metric_table_alignment"],
        "refs": ["dataset_metric_benchmark_ref", "result_metric_registry_ref"],
        "sources": ["Papers-with-Code/SOTA"],
        "policy": "learned",
    },
}

for module_id, requirement in slr_citation_data_requirements.items():
    module = require_module(module_id)
    require_output_schema(module, requirement["output_schema_refs"])
    require_artifact_refs(module, requirement["refs"])
    require_quality_refs(module, requirement["refs"])
    if requirement["policy"] == "learned":
        policy = module.get("learned_pattern_policy") or {}
        require_all(f"{module_id} learned SLR/citation/data refs", policy.get("required_ref_shapes"), requirement["refs"])
        policy_blob = json.dumps(policy, ensure_ascii=False)
    else:
        policy = module.get("external_learning_module_fit") or {}
        policy_blob = json.dumps(policy.get("sources") or [], ensure_ascii=False)
        require_external_fit_ai_policy(module)
    for source in requirement["sources"]:
        if source not in policy_blob:
            fail(f"{module_id} missing SLR/citation/data source token {source}")
    if requirement["policy"] == "learned":
        require_ai_judgment_candidate_policy(module, policy)

if require_module("mas-scholar-skills.stats").get("quality_evidence", {}).get("can_claim_statistical_conclusion") is not False:
    fail("Stats must not claim statistical conclusion")
submit_policy = require_module("mas-scholar-skills.submit").get("learned_pattern_policy", {})
publication_authority = submit_policy.get("publication_readiness_authority", {})
if publication_authority.get("can_authorize_publication_readiness") is not False:
    fail("Submit learned policy must not authorize publication readiness")

data_refs = [
    "data_manifest_ref",
    "dataset_manifest_ref",
    "metadata_scrape_ref",
    "source_lineage_ref",
    "artifact_bundle_manifest_ref",
    "data_asset_manifest_ref",
    "lifecycle_classification_ref",
    "data_dictionary_ref",
    "agent_log_aggregation_ref",
    "data_governance_handoff_ref",
    "data_governance_assessment_ref",
    "data_operation_receipt_ref",
    "manifest_completeness_check_ref",
    "privacy_tier_check_ref",
    "study_impact_check_ref",
    "privacy_access_tier_ref",
    "read_model_boundary_ref",
    "storage_tier_ref",
    "authoritative_body_boundary_ref",
    "derived_copy_inventory_ref",
    "analytical_format_strategy_ref",
    "cold_restore_proof_ref",
    "important_result_reproduction_ref",
    "data_body_boundary_ref",
    "study_impact_ref",
    "owner_decision_ref",
    "post_cleanup_readback_ref",
    "prune_dry_run_ref",
    "lifecycle_catalog_ref",
]
data_module = require_module("mas-scholar-skills.data")
if data_module.get("specialist_skill_id") != "medical-data-governance":
    fail("Data module must point to real specialist skill medical-data-governance")
if "opl.scholarskills.data" not in (data_module.get("legacy_module_ids") or []):
    fail("Data module must retain opl.scholarskills.data only as legacy alias/provenance")
if data_module.get("legacy_module_id_policy") != "opl.scholarskills.data remains a legacy alias/provenance key only; active module id is mas-scholar-skills.data and active specialist work uses medical-data-governance":
    fail("Data module legacy id policy must keep opl.scholarskills.data alias-only")
require_output_schema(
    data_module,
    [
        "scholarskills_data_external_learning_refs.v1",
        "scholarskills_data_asset_refs.v1",
        "scholarskills_data_lifecycle_refs.v1#asset_manifest_classification_reproduction_prune_readback",
        "scholarskills_data_governance_assessment_refs.v1#handoff_assessment_operation_checks",
    ],
)
require_quality_refs(data_module, data_refs)
require_artifact_refs(
    data_module,
    [
        "scholarskills_data_manifest_candidate",
        "scholarskills_data_lineage_candidate",
        "data_governance_handoff_ref",
        "data_governance_assessment_ref",
        "data_operation_receipt_ref",
        "manifest_completeness_check_ref",
        "privacy_tier_check_ref",
        "study_impact_check_ref",
        "data_asset_manifest_ref",
        "lifecycle_classification_ref",
        "important_result_reproduction_ref",
        "data_body_boundary_ref",
        "study_impact_ref",
        "owner_decision_ref",
        "post_cleanup_readback_ref",
        "prune_dry_run_ref",
        "lifecycle_catalog_ref",
    ],
)
require_external_fit(data_module, ["Future-Scholars/paperlib", "Ar9av/PaperOrchestra", "littlepeachs/NaturePanelForge"])
data_assessment_policy = data_module.get("data_governance_assessment_policy") or {}
if data_assessment_policy.get("policy_id") != "scholarskills_data_governance_assessment.v1":
    fail("Data module missing machine-readable governance assessment policy")
if data_assessment_policy.get("active_module_id") != "mas-scholar-skills.data":
    fail("Data assessment policy must pin active_module_id mas-scholar-skills.data")
if data_assessment_policy.get("real_specialist_skill_id") != "medical-data-governance":
    fail("Data assessment policy must pin real specialist skill medical-data-governance")
if "opl.scholarskills.data" not in (data_assessment_policy.get("legacy_module_ids") or []):
    fail("Data assessment policy must keep opl.scholarskills.data as legacy alias/provenance")
if data_assessment_policy.get("legacy_id_policy") != "legacy_alias_provenance_only_not_active_module_id":
    fail("Data assessment policy legacy id policy must be alias/provenance only")
data_assessment_refs = [
    "data_governance_handoff_ref",
    "data_governance_assessment_ref",
    "data_operation_receipt_ref",
    "manifest_completeness_check_ref",
    "privacy_tier_check_ref",
    "study_impact_check_ref",
]
require_all(
    "Data assessment handoff refs",
    data_assessment_policy.get("required_handoff_refs"),
    [
        "source_pack_ref",
        "candidate_refs",
        "owner_gate_handoff_ref",
        "data_governance_handoff_ref",
    ],
)
require_all(
    "Data assessment refs",
    data_assessment_policy.get("assessment_ref_families"),
    [
        "data_governance_assessment_ref",
        "data_operation_receipt_ref",
        "manifest_completeness_check_ref",
        "privacy_tier_check_ref",
        "study_impact_check_ref",
    ],
)
data_operation_categories = [
    "ingest",
    "clean",
    "deidentify",
    "normalize",
    "update",
    "diff",
    "release",
    "retire",
]
require_all("Data operation receipt categories", data_assessment_policy.get("operation_receipt_categories"), data_operation_categories)
data_assessment_checks = [
    "manifest_completeness_declared",
    "privacy_access_tier_declared",
    "study_impact_declared",
    "operation_receipt_category_declared",
    "legacy_opl_scholarskills_data_alias_only",
    "no_authority_flags_false",
]
require_all("Data machine assessment checks", data_assessment_policy.get("required_checks"), data_assessment_checks)
for key in [
    "can_write_domain_truth",
    "can_mutate_clinical_data_body",
    "can_sign_owner_receipt",
    "can_create_typed_blocker",
    "can_claim_source_readiness",
    "can_claim_publication_readiness",
]:
    if data_assessment_policy.get(key) is not False:
        fail(f"Data assessment authority flag {key} must be false")
retention_policy = data_module.get("retention_closeout_policy") or {}
data_lifecycle_refs = [
    "data_asset_manifest_ref",
    "lifecycle_classification_ref",
    "important_result_reproduction_ref",
    "data_body_boundary_ref",
    "lifecycle_catalog_ref",
    "owner_decision_ref",
    "study_impact_ref",
    "prune_dry_run_ref",
    "post_cleanup_readback_ref",
]
require_all("Data retention lifecycle required refs", retention_policy.get("required_refs"), data_lifecycle_refs)
require_all(
    "Data retention lifecycle checks",
    retention_policy.get("required_checks"),
    [
        "data_asset_manifest_declared",
        "lifecycle_classification_declared",
        "important_result_reproduction_path_declared",
        "data_body_boundary_declared",
        "lifecycle_catalog_declared",
        "owner_decision_target_declared",
        "study_impact_declared",
        "prune_dry_run_declared",
        "post_cleanup_readback_declared",
        "no_authority_flags_false",
    ],
)
require_all(
    "Data lifecycle states",
    retention_policy.get("lifecycle_states"),
    [
        "hot_current_body",
        "warm_parent_or_provenance",
        "paper_facing_current",
        "active_runtime",
        "semantic_closed",
        "byte_closed",
        "delete_safe_cache",
        "retired_tombstone",
    ],
)
for token in [
    *data_lifecycle_refs,
    "hot_current_body",
    "warm_parent_or_provenance",
    "paper_facing_current",
    "active_runtime",
    "semantic_closed",
    "byte_closed",
    "delete_safe_cache",
    "retired_tombstone",
]:
    if token not in capability_modules_doc:
        fail(f"docs/capability-modules.md missing Data lifecycle token: {token}")

for relative, text in [("skills/medical-data-governance/SKILL.md", data_governance_skill)]:
    for token in [
        "mas-scholar-skills.data",
        "medical-data-governance",
        "opl.scholarskills.data",
        *data_assessment_refs,
        *data_operation_categories,
        *data_assessment_checks,
    ]:
        if token not in text:
            fail(f"{relative} missing Data governance assessment token: {token}")

for token in [
    "source_pack_ref",
    "candidate_refs",
    "owner_gate_handoff_ref",
]:
    if token not in skill:
        fail(f"SKILL.md missing standard handoff token: {token}")

if gallery_manifest.get("status") != "rendered":
    fail("gallery manifest status must be rendered")

verify_gallery_import_policy(gallery_manifest, "gallery_manifest", fail)
verify_gallery_import_policy(snapshot, "gallery_snapshot", fail)

for key in [
    "current_template_count",
    "visual_gallery_template_count",
    "non_visual_canonical_template_count",
    "evidence_gallery_template_count",
    "reporting_flow_gallery_template_count",
    "design_gallery_template_count",
    "table_preview_gallery_template_count",
    "composition_recipe_gallery_count",
]:
    manifest_value = gallery_manifest.get(key)
    if not isinstance(manifest_value, int):
        fail(f"gallery manifest {key} must be an integer")
    if manifest_value != snapshot.get(key):
        fail(f"gallery manifest/snapshot {key} mismatch")
if gallery_manifest.get("composition_recipe_gallery_count") != 6:
    fail("gallery must keep 6 composition recipes")
renderer_policy = gallery_manifest.get("renderer_policy_completion", {})
if renderer_policy.get("current_r_ggplot2_evidence_template_count") != gallery_manifest.get(
    "evidence_gallery_template_count"
):
    fail("gallery R/ggplot2 evidence count must match evidence gallery count")
if renderer_policy.get("current_python_evidence_template_count") != 0:
    fail("gallery must keep current Python evidence templates at 0")
quality_summary = gallery_manifest.get("quality_audit") or gallery_manifest.get("quality_summary", {})
if quality_summary.get("publication_ready_claim_authorized") is not False:
    fail("gallery must not authorize publication-ready claims")
if snapshot.get("publication_ready_claim_authorized") is not False:
    fail("snapshot must not authorize publication-ready claims")
quality_audit = read_text("gallery/medical-display/display_pack_gallery_quality_audit.md")
for token in [
    "通用科研做图 Quality Floor",
    "mas_scientific_figure_quality_floor.v1",
    "reference_target_preserve_list",
    "source_preservation_ref",
]:
    if token not in quality_audit:
        fail(f"gallery quality audit missing scientific quality-floor token: {token}")

for item in snapshot.get("included_files", []):
    relative = "gallery/medical-display/" + item["path"]
    actual = sha256_file(relative)
    if actual != item["sha256"]:
        fail(f"sha256 mismatch for {relative}: {actual} != {item['sha256']}")

required_gallery_files = [
    "gallery/medical-display/medical_display_gallery.pdf",
    "gallery/medical-display/gallery_manifest.json",
    "gallery/medical-display/medical_display_gallery_reference.md",
    "gallery/medical-display/display_pack_gallery_status.md",
    "gallery/medical-display/display_pack_gallery_quality_audit.md",
    "gallery/medical-display/gallery_snapshot.json",
]
for relative in required_gallery_files:
    if not (root / relative).is_file():
        fail(f"missing gallery file {relative}")

for forbidden in [
    "outputs/display-pack-gallery",
    "gallery/medical-display/medical_display_gallery_assets",
    "gallery/medical-display/render-cache",
]:
    if (root / forbidden).exists():
        fail(f"forbidden intermediate output present: {forbidden}")

gitignore = read_text(".gitignore")
for pattern in [
    "outputs/",
    "render-cache/",
    "gallery/**/assets/",
    "gallery/**/*.png",
    "gallery/**/*.svg",
    "gallery/**/*.html",
    "gallery/**/*.sidecar.json",
    "gallery/**/*.layout.json",
    ".worktrees/",
    "__pycache__/",
    "*.pyc",
]:
    if pattern not in gitignore:
        fail(f".gitignore missing intermediate-output pattern {pattern}")

print("verify ok: mas-scholar-skills plugin, contract, medical skill sources, gallery package, and no-authority boundaries are valid")
