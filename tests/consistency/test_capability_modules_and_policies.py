"""Capability modules, Display source pack hygiene, learned policies, and external-fit contracts."""

from __future__ import annotations

import json
import re

from tests.consistency._context import (
    fail,
    load_repo_context,
    read_json,
    require_all,
    verify_gallery_import_policy,
)
def test_capability_modules_and_display_source_pack() -> None:
    ctx = load_repo_context()
    advanced_capability_by_id = ctx.advanced_capability_by_id
    capability_by_id = ctx.capability_by_id
    capability_pack_consumption = ctx.capability_pack_consumption
    contract = ctx.contract
    display_qc_skill = ctx.display_qc_skill
    method_policy = ctx.method_policy
    method_policy_by_id = ctx.method_policy_by_id
    package_manifest = ctx.package_manifest
    profile_adapter_ids = ctx.profile_adapter_ids
    reference_integrity_skill = ctx.reference_integrity_skill
    review_skill = ctx.review_skill
    root = ctx.root
    runtime_binding = ctx.runtime_binding
    runtime_module_id = ctx.runtime_module_id
    runtime_module_ids = ctx.runtime_module_ids
    search_profile_adapter_ids = ctx.search_profile_adapter_ids
    search_runtime_binding = ctx.search_runtime_binding
    search_runtime_module_id = ctx.search_runtime_module_id
    stats_skill = ctx.stats_skill
    submit_skill = ctx.submit_skill
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
    if search_state_machine_contract.get("max_steps") != 2:
        fail("scientific search adapter module must cap provider searches at two steps")
    if search_state_machine_contract.get("http_execution_owner") != "opl_connect":
        fail("OPL Connect must remain the scientific search HTTP execution owner")
    if search_state_machine_contract.get("provider_scope") != "package_owned_primary_biomedical_and_generic_metadata_search":
        fail("scientific search adapter module must own primary biomedical and metadata discovery")
    if search_state_machine_contract.get("framework_core_provider_scope") != "no_scientific_search_provider_logic":
        fail("scientific search adapter module must keep scientific provider logic outside Framework core")
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
            "opl-package.json",
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

    for module in professional_modules:
        module_id = module.get("module_id")
        display_name = module.get("display_name")
        if not module_id:
            fail("Professional module must declare its machine identity")
        if not display_name:
            fail(f"Professional module {module_id} must declare a display name")
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


    read_json("gallery/medical-display/gallery_manifest.json")
    read_json("gallery/medical-display/gallery_snapshot.json")
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

def test_module_learned_policies_and_external_fit() -> None:
    ctx = load_repo_context()
    advanced_capability_by_id = ctx.advanced_capability_by_id
    capability_by_id = ctx.capability_by_id
    display_module = ctx.display_module
    gallery_manifest = ctx.gallery_manifest
    modules = ctx.modules
    snapshot = ctx.snapshot
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
