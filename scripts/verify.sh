#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 scripts/verify-display-gallery-pack.py --check

python3 - <<'PY'
import hashlib
import json
import pathlib
import re
import sys

root = pathlib.Path.cwd()

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
if manifest.get("skills") != "./skills/":
    fail("plugin skills path must be ./skills/")
if manifest.get("interface", {}).get("displayName") != "MAS Scholar Skills":
    fail("plugin displayName must be MAS Scholar Skills")

skill = read_text("skills/mas-scholar-skills/SKILL.md")
if not re.search(r"^---\n[\s\S]*?^name:\s+mas-scholar-skills$", skill, re.MULTILINE):
    fail("SKILL.md frontmatter must expose name: mas-scholar-skills")
write_skill = read_text("skills/medical-manuscript-writing/SKILL.md")
if not re.search(r"^---\n[\s\S]*?^name:\s+medical-manuscript-writing$", write_skill, re.MULTILINE):
    fail("medical-manuscript-writing must be a real Codex skill")
review_skill = read_text("skills/medical-manuscript-review/SKILL.md")
if not re.search(r"^---\n[\s\S]*?^name:\s+medical-manuscript-review$", review_skill, re.MULTILINE):
    fail("medical-manuscript-review must be a real Codex skill")
figure_skill = read_text("skills/medical-figure-design/SKILL.md")
if not re.search(r"^---\n[\s\S]*?^name:\s+medical-figure-design$", figure_skill, re.MULTILINE):
    fail("medical-figure-design must be a real Codex skill")
lit_skill = read_text("skills/medical-research-lit/SKILL.md")
if not re.search(r"^---\n[\s\S]*?^name:\s+medical-research-lit$", lit_skill, re.MULTILINE):
    fail("medical-research-lit must be a real Codex skill")
legacy_skill = read_text("skills/opl-scholarskills/SKILL.md")
if not re.search(r"^---\n[\s\S]*?^name:\s+opl-scholarskills$", legacy_skill, re.MULTILINE):
    fail("legacy alias must expose name: opl-scholarskills")

contract = read_json("contracts/scholar-skills-capability-modules.json")
contract_text = json.dumps(contract, ensure_ascii=False)
readme = read_text("README.md")
readme_zh = read_text("README.zh-CN.md")
docs_index = read_text("docs/README.md")
operating_model = read_text("docs/mas-scholar-skills-operating-model.md")
capability_modules = read_text("docs/capability-modules.md")
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
    "role": "opl_owned_external_enhancement_pack_for_mas_medical_paper_capabilities",
    "primary_mas_entry_policy": "MAS_stage_operating_prompts_remain_in_med_autoscience_and_may_consume_specialist_skills_from_mas_scholar_skills",
    "canonical_mas_stage_source_policy": "MAS_domain_agent_repo_agent_stages_and_agent_prompts_are_the_canonical_stage_prompt_source",
    "codex_projection_policy": "MAS_overlay_skills_and_workspace_or_quest_dot_codex_skill_copies_are_codex_projection_or_compatibility_surfaces_not_stage_prompt_source",
    "no_parallel_entry_policy": "do_not_create_parallel_stage_authority_entries_in_mas_scholar_skills",
    "professional_skill_location_policy": "professional_specialist_skills_default_to_the_consuming_domain_agent_repo; heavy_cross_workspace_or_independently_released_skills_may_be_externalized_to_pack_repos_such_as_mas_scholar_skills",
    "tool_connector_policy": "OPL_Connect_or_Fabric_owns_tool_invocation_normalized_read_receipts_and_connector_errors_not_stage_policy_specialist_judgment_owner_receipts_typed_blockers_human_gates_publication_readiness_or_artifact_authority",
    "sync_owner": "OPL Connect",
    "required_or_default_pack_owner": "MAS_profile_or_overlay",
    "ledger_and_owner_receipt_owner": "MAS_or_relevant_OPL_domain_owner",
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
require_all(
    "syncable real skills",
    specialist_skill_policy.get("syncable_real_skills"),
    ["medical-manuscript-writing", "medical-manuscript-review", "medical-figure-design", "medical-research-lit"],
)
require_all(
    "medical paper specialist skill sources",
    specialist_skill_policy.get("medical_paper_specialist_skill_sources"),
    ["medical-manuscript-writing", "medical-manuscript-review", "medical-figure-design"],
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
    "external_pack_split_policy": "heavy_cross_workspace_or_independently_released_professional_skills_may_be_split_to_external_pack_repos; mas_scholar_skills_is_the_pack_for_MAS_medical_writing_review_figure_lit_Display_and_source_refs",
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
classification_policy = contract.get("capability_module_classification_policy") or {}
if classification_policy.get("policy_id") != "mas_scholar_skills_capability_module_classification.v1":
    fail("contract missing capability module classification policy")
require_all(
    "capability module contracts",
    classification_policy.get("capability_module_contracts"),
    ["display", "tables", "stats", "omics", "lit", "write", "review", "submit", "data", "intake"],
)
require_all(
    "real syncable specialist skills",
    classification_policy.get("real_syncable_specialist_skills"),
    ["medical-manuscript-writing", "medical-manuscript-review", "medical-figure-design", "medical-research-lit"],
)
require_all(
    "contract-layer modules",
    classification_policy.get("contract_layer_modules"),
    ["tables", "stats", "omics", "submit", "data", "intake"],
)
expected_real_skill_backed_modules = {
    "display": "medical-figure-design",
    "lit": "medical-research-lit",
    "write": "medical-manuscript-writing",
    "review": "medical-manuscript-review",
}
if classification_policy.get("real_skill_backed_module_map") != expected_real_skill_backed_modules:
    fail("classification policy must map the four real-skill-backed modules")
for token in [
    "not_from_ten_preexisting_real_MAS_skills",
    "without_claiming_to_be_active_specialist_skills",
    "promote_contract_layer_module_to_real_codex_skill_only_when",
    "dot_codex_skills_sync_remains_required_for_Codex_discovery",
]:
    if token not in json.dumps(classification_policy, ensure_ascii=False):
        fail(f"classification policy missing {token}")
for key in [
    "can_claim_contract_layer_modules_are_real_skills",
    "can_move_contract_layer_modules_back_to_MAS_private_implementation",
    "can_replace_mas_stage_prompts",
    "can_claim_owner_acceptance",
    "can_claim_publication_readiness",
]:
    if classification_policy.get(key) is not False:
        fail(f"classification policy flag {key} must be false")
for relative, text in [
    ("README.md", readme),
    ("README.zh-CN.md", readme_zh),
    ("docs/README.md", docs_index),
    ("docs/mas-scholar-skills-operating-model.md", operating_model),
    ("skills/mas-scholar-skills/SKILL.md", skill),
    ("skills/medical-manuscript-writing/SKILL.md", write_skill),
    ("skills/medical-manuscript-review/SKILL.md", review_skill),
    ("skills/medical-figure-design/SKILL.md", figure_skill),
]:
    for token in [
        "MAS Scholar Skills",
        "medical-manuscript-writing",
        "medical-manuscript-review",
        "medical-figure-design",
    ]:
        if token not in text:
            fail(f"{relative} missing MAS Scholar Skills positioning token: {token}")
    for token in [
        "owner receipt",
        "typed blocker",
        "publication readiness",
    ]:
        if token not in text:
            fail(f"{relative} missing no-authority boundary token: {token}")
for forbidden in [
    "default opl-scholar-write",
    "default opl-scholar-review",
    "default opl-scholar-display",
]:
    if forbidden in "\n".join([readme, readme_zh, docs_index, operating_model, skill]):
        fail(f"docs must not create a parallel ScholarSkills default entry: {forbidden}")
for relative, text in [
    ("README.md", readme),
    ("README.zh-CN.md", readme_zh),
    ("docs/mas-scholar-skills-operating-model.md", operating_model),
    ("docs/capability-modules.md", capability_modules),
]:
    for token in [
        "agent/stages/",
        "agent/prompts/",
        ".codex/skills/",
        "professional specialist",
        "Tool connector",
    ]:
        if token.lower() not in text.lower():
            fail(f"{relative} missing stage/professional/tool boundary token: {token}")
for relative, text in [
    ("README.md", readme),
    ("README.zh-CN.md", readme_zh),
    ("docs/README.md", docs_index),
    ("docs/mas-scholar-skills-operating-model.md", operating_model),
    ("skills/mas-scholar-skills/SKILL.md", skill),
    ("skills/medical-manuscript-writing/SKILL.md", write_skill),
    ("skills/medical-manuscript-review/SKILL.md", review_skill),
    ("skills/medical-figure-design/SKILL.md", figure_skill),
    ("skills/medical-research-lit/SKILL.md", lit_skill),
]:
    for token in [
        "opl connect pubmed search",
        "pubmed_source_refs",
        "pubmed_connector_invocation_ref",
    ]:
        if token not in text:
            fail(f"{relative} missing PubMed Connect positioning token: {token}")
for token in [
    "connect_pubmed_search",
    "pubmed_source_refs",
    "pubmed_connector_invocation_ref",
    "read_only_normalized_source_refs_not_literature_verdict_or_domain_truth",
]:
    if token not in contract_text:
        fail(f"contract missing PubMed Connect Lit token: {token}")
modules = contract.get("modules")
if not isinstance(modules, list) or len(modules) != 10:
    fail("contract must contain exactly 10 ScholarSkills modules")

standard_handoff_refs = [
    "source_pack_ref",
    "candidate_package_ref",
    "execution_receipt_ref",
    "owner_gate_handoff_ref",
]
standard_handoff = contract.get("standard_handoff_ref_families") or {}
if standard_handoff.get("policy_id") != "scholarskills_standard_refs_only_handoff.v1":
    fail("contract missing standard refs-only handoff policy")
if standard_handoff.get("applies_to_modules") != "all_ten_scholarskills_modules":
    fail("standard handoff policy must apply to all ten modules")
require_all("standard handoff refs", standard_handoff.get("required_ref_shapes"), standard_handoff_refs)
if standard_handoff.get("no_authority_policy") != "source_pack_candidate_package_execution_receipt_and_owner_gate_handoff_refs_only":
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

for module in modules:
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
    if quality.get("handoff_policy") != "standard_refs_only_source_pack_candidate_package_execution_receipt_owner_gate_handoff":
        fail(f"{module_id} quality evidence missing standard handoff policy")
    require_all(f"{module_id} standard handoff refs", quality.get("required_ref_shapes"), standard_handoff_refs)

contract_boundary = contract.get("authority_boundary") or {}
for key in [
    "can_claim_publication_readiness",
    "can_claim_owner_acceptance",
    "can_claim_current_package_authority",
]:
    if contract_boundary.get(key) is not False:
        fail(f"top-level authority flag {key} must be false")
bridge = contract.get("runtime_environment_bridge") or {}
bridge_policy = bridge.get("bridge_envelope_policy") or {}
for container, label in [(bridge, "runtime bridge"), (bridge_policy, "bridge envelope")]:
    for key in [
        "can_claim_publication_readiness",
        "can_claim_owner_acceptance",
        "can_claim_current_package_authority",
    ]:
        if container.get(key) is not False:
            fail(f"{label} authority flag {key} must be false")

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

for token in [
    "authority false",
    "MAS owner gate",
    "refs-only",
    "materialized_candidate_package",
    "External Learning Module Fit",
    "gallery/medical-display/medical_display_gallery.pdf",
    "scholarskills_scientific_figure_quality_floor.v1",
    "brief_first_reference_guided_ai_candidate_not_single_template_reuse",
    "critic_review_ref",
    "external_runtime_install_not_required_before_candidate_refs_or_checklists",
    "downstream owner-consumption refs only",
    "FeedbackOps Refs-Only Adapter",
    "target_agent_feedback_external_suite",
    "feedbackops_refs_only_adapter_policy",
    "medical-research-lit",
]:
    if token not in skill:
        fail(f"SKILL.md missing required token: {token}")

gallery_manifest = read_json("gallery/medical-display/gallery_manifest.json")
snapshot = read_json("gallery/medical-display/gallery_snapshot.json")
display_module = next(
    (item for item in modules if item.get("module_id") == "opl.scholarskills.display"),
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
    'source = "scholarskills-managed-external-pack"',
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
    "packs/medical-display-core/templates/roc_curve_binary/template.toml",
    "packs/medical-display-core/templates/roc_curve_binary/render.R",
    "packs/medical-display-core/rlib/medicaldisplaycore/evidence_renderer.R",
    "packs/medical-display-core/src/fenggaolab_org_medical_display_core/__init__.py",
    "packs/medical-display-core/canonical_template_catalog.json",
    "packs/medical-display-core/renderer_dependency_profile.json",
]:
    if not (root / relative).is_file():
        fail(f"missing Display source pack file {relative}")
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
    "opl.scholarskills.display": {
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
    "opl.scholarskills.tables": {
        "output_schema_refs": ["scholarskills_tables_learned_pattern_refs.v1#table_shell_metric_alignment_qc"],
        "refs": ["table_shell_ref", "metric_extraction_ref", "booktabs_or_minimal_ink_table_ref", "table_qc_ref", "claim_table_alignment_ref"],
        "policy_id": "scholarskills_tables_external_learning_refs.v1",
        "sources": ["Master-cai/Research-Paper-Writing-Skills", "Ar9av/PaperOrchestra"],
        "boundary_tokens": ["table_truth", "publication_ready"],
    },
    "opl.scholarskills.stats": {
        "output_schema_refs": ["scholarskills_stats_learned_pattern_refs.v1#analysis_plan_metric_reproducibility_review"],
        "refs": ["analysis_plan_ref", "effect_size_or_metric_extraction_ref", "reproducibility_check_ref", "statistical_review_ref"],
        "policy_id": "scholarskills_stats_external_learning_refs.v1",
        "sources": ["Ar9av/PaperOrchestra", "Imbad0202/academic-research-skills"],
        "boundary_tokens": ["statistical_conclusion", "domain_truth"],
    },
    "opl.scholarskills.omics": {
        "output_schema_refs": ["scholarskills_omics_learned_pattern_refs.v1#feature_matrix_visualization_pathway_review"],
        "refs": ["feature_matrix_qc_ref", "omics_visualization_plan_ref", "pathway_context_ref", "domain_review_ref"],
        "policy_id": "scholarskills_omics_external_learning_refs.v1",
        "sources": ["Marsilea-viz/marsilea", "Boom5426/Awesome-Virtual-Cell"],
        "boundary_tokens": ["omics_truth", "domain_truth"],
    },
    "opl.scholarskills.lit": {
        "output_schema_refs": ["scholarskills_lit_external_learning_refs.v1#query_citation_evidence_map"],
        "refs": ["query_ref", "citation_manifest_ref", "source_verification_ref", "citation_coverage_ref", "evidence_map_ref", "metadata_scrape_ref", "claim_support_ref"],
        "policy_id": "scholarskills_lit_external_learning_policy.v1",
        "sources": ["Imbad0202/academic-research-skills", "Imbad0202/academic-research-skills-codex", "Ar9av/PaperOrchestra", "Future-Scholars/paperlib"],
        "boundary_tokens": ["literature_verdict"],
    },
    "opl.scholarskills.write": {
        "output_schema_refs": ["scholarskills_write_external_learning_refs.v1#outline_trace_draft"],
        "refs": ["section_outline_ref", "reverse_outline_ref", "claim_evidence_map_ref", "source_trace_ref", "unsupported_claim_route_back_ref", "section_draft_manifest_ref"],
        "policy_id": "scholarskills_write_external_learning_policy.v1",
        "sources": ["Master-cai/Research-Paper-Writing-Skills", "Imbad0202/academic-research-skills", "Ar9av/PaperOrchestra"],
        "boundary_tokens": ["paper_body_authority"],
    },
    "opl.scholarskills.review": {
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
    "opl.scholarskills.submit": {
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

medical_sci_initial_draft_requirements = {
    "opl.scholarskills.display": {
        "refs": ["figure_table_volume_and_clinical_value_ref", "figure_polish_alignment_ref"],
    },
    "opl.scholarskills.lit": {
        "output_schema_refs": ["scholarskills_lit_medical_sci_draft_refs.v1#reference_integrity_floor"],
        "refs": ["reference_integrity_floor_ref"],
    },
    "opl.scholarskills.write": {
        "output_schema_refs": ["scholarskills_write_medical_sci_draft_refs.v1#body_volume_and_prose_floor"],
        "refs": ["manuscript_body_volume_floor_ref", "internal_report_prose_route_back_ref"],
    },
    "opl.scholarskills.review": {
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

review_medical_floor = require_module("opl.scholarskills.review").get("medical_sci_initial_draft_quality_floor_policy") or {}
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
    "opl.scholarskills.lit": {
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
    "opl.scholarskills.write": {
        "output_schema_refs": ["scholarskills_write_source_verification_refs.v1#confirm_drop_before_draft_use"],
        "refs": ["confirm_or_drop_source_verification_ref"],
        "sources": ["kennethkhoocy/lit-review-orchestrator"],
        "policy": "learned",
    },
    "opl.scholarskills.review": {
        "output_schema_refs": ["scholarskills_review_source_verification_refs.v1#confirm_drop_adversarial_check"],
        "refs": ["confirm_or_drop_source_verification_ref"],
        "sources": ["kennethkhoocy/lit-review-orchestrator"],
        "policy": "learned",
    },
    "opl.scholarskills.data": {
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
    "opl.scholarskills.stats": {
        "output_schema_refs": ["scholarskills_stats_metric_registry_refs.v1#dataset_metric_benchmark_result_registry"],
        "refs": ["dataset_metric_benchmark_ref", "result_metric_registry_ref"],
        "sources": ["Papers-with-Code/SOTA"],
        "policy": "learned",
    },
    "opl.scholarskills.tables": {
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

if require_module("opl.scholarskills.stats").get("quality_evidence", {}).get("can_claim_statistical_conclusion") is not False:
    fail("Stats must not claim statistical conclusion")
if require_module("opl.scholarskills.omics").get("quality_evidence", {}).get("can_claim_omics_truth") is not False:
    fail("Omics must not claim omics truth")
submit_policy = require_module("opl.scholarskills.submit").get("learned_pattern_policy", {})
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
data_module = require_module("opl.scholarskills.data")
require_output_schema(
    data_module,
    [
        "scholarskills_data_external_learning_refs.v1",
        "scholarskills_data_asset_refs.v1",
        "scholarskills_data_lifecycle_refs.v1#asset_manifest_classification_reproduction_prune_readback",
    ],
)
require_quality_refs(data_module, data_refs)
require_artifact_refs(
    data_module,
    [
        "scholarskills_data_manifest_candidate",
        "scholarskills_data_lineage_candidate",
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
    if token not in skill:
        fail(f"SKILL.md missing Data lifecycle token: {token}")

for token in [
    "source_pack_ref",
    "candidate_package_ref",
    "execution_receipt_ref",
    "owner_gate_handoff_ref",
    "Every module should expose the standard refs-only handoff family",
]:
    if token not in skill:
        fail(f"SKILL.md missing standard handoff token: {token}")

intake_refs = [
    "source_snapshot_ref",
    "source_manifest_ref",
    "upstream_commit_ref",
    "vendor_provenance_ref",
    "included_excluded_paths_ref",
    "dry_run_readback_ref",
    "input_contract_ref",
    "adoption_contract_ref",
    "scope_boundary_ref",
]
intake_module = require_module("opl.scholarskills.intake")
require_output_schema(intake_module, ["scholarskills_intake_external_learning_refs.v1"])
require_quality_refs(intake_module, intake_refs)
require_artifact_refs(intake_module, ["scholarskills_intake_source_manifest_candidate", "scholarskills_intake_adoption_candidate"])
require_external_fit(intake_module, ["Imbad0202/academic-research-skills-codex", "Ar9av/PaperOrchestra", "littlepeachs/NaturePanelForge"])

if gallery_manifest.get("status") != "rendered":
    fail("gallery manifest status must be rendered")

def require_gallery_import_policy(container: dict, label: str) -> None:
    policy = container.get("opl_scholarskills_import_policy") or {}
    if policy.get("policy_id") != "opl_scholarskills_display_gallery_refs_only_source_manifest.v1":
        fail(f"{label} missing ScholarSkills gallery refs-only import policy")
    if policy.get("import_role") != "pack_native_human_review_ref_and_source_snapshot":
        fail(f"{label} gallery import role must stay pack-native refs/source snapshot only")
    if policy.get("source_repo") != "mas-scholar-skills":
        fail(f"{label} gallery source repo must remain mas-scholar-skills")
    if policy.get("source_authority") != "opl_scholarskills_display_pack_review_surface":
        fail(f"{label} gallery source authority must remain ScholarSkills display review surface")
    if not str(policy.get("source_snapshot_ref") or "").startswith("repo-local:gallery/medical-display/"):
        fail(f"{label} gallery import policy must use a repo-local source_snapshot_ref")
    if "not_self_referential" not in str(policy.get("source_commit_policy") or ""):
        fail(f"{label} gallery import policy must not use a self-referential source commit")
    if policy.get("no_second_truth") is not True:
        fail(f"{label} gallery import policy must explicitly forbid second truth")
    require_all(
        f"{label} gallery allowed uses",
        policy.get("allowed_uses"),
        ["gallery_review_ref", "source_manifest_ref", "quality_floor_ref"],
    )
    forbidden_uses = set(policy.get("forbidden_uses") or [])
    for forbidden in [
        "mas_display_truth",
        "publication_ready_claim",
        "owner_receipt",
        "typed_blocker",
        "artifact_authority",
        "runtime_or_package_authority",
    ]:
        if forbidden not in forbidden_uses:
            fail(f"{label} gallery import policy must forbid {forbidden}")
    boundary = policy.get("authority_boundary") or {}
    for key in [
        "can_write_domain_truth",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_publication_ready",
        "can_claim_artifact_authority",
    ]:
        if boundary.get(key) is not False:
            fail(f"{label} gallery import authority flag {key} must be false")

require_gallery_import_policy(gallery_manifest, "gallery_manifest")
require_gallery_import_policy(snapshot, "gallery_snapshot")

expected_counts = {
    "visual_gallery_template_count": 37,
    "evidence_gallery_template_count": 34,
    "composition_recipe_gallery_count": 6,
}
for key, expected in expected_counts.items():
    if gallery_manifest.get(key) != expected:
        fail(f"gallery manifest {key} must be {expected}")
    if snapshot.get(key) != expected:
        fail(f"gallery snapshot {key} must be {expected}")
renderer_policy = gallery_manifest.get("renderer_policy_completion", {})
if renderer_policy.get("current_r_ggplot2_evidence_template_count") != 34:
    fail("gallery must keep 34 current R/ggplot2 evidence templates")
if renderer_policy.get("current_python_evidence_template_count") != 0:
    fail("gallery must keep current Python evidence templates at 0")
quality_summary = gallery_manifest.get("quality_summary", {})
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
]:
    if pattern not in gitignore:
        fail(f".gitignore missing intermediate-output pattern {pattern}")

for relative in ["README.md", "README.zh-CN.md", "AGENTS.md"]:
    text = read_text(relative)
    lower = text.lower()
    if "publication ready" not in lower and "publication-ready" not in lower and "publication readiness" not in lower:
        fail(f"{relative} must mention publication readiness boundary")

required_doc_tokens = {
    "README.md": [
        "progress-first",
        "AI auto-judgment-first",
        "AI-consumable evidence",
        "verdict_candidate",
        "route_back_candidate",
        "stop/continue recommendations",
        "downstream owner-consumption target",
        "source_pack_ref",
        "candidate_package_ref",
        "execution_receipt_ref",
        "owner_gate_handoff_ref",
    ],
    "README.zh-CN.md": [
        "progress-first",
        "AI auto-judgment-first",
        "AI-consumable evidence",
        "verdict_candidate",
        "route_back_candidate",
        "stop/continue recommendations",
        "下游 owner-consumption 目标",
        "source_pack_ref",
        "candidate_package_ref",
        "execution_receipt_ref",
        "owner_gate_handoff_ref",
    ],
    "skills/opl-scholarskills/SKILL.md": [
        "Legacy Alias",
        "mas-scholar-skills",
        "medical-manuscript-writing",
        "medical-manuscript-review",
        "medical-figure-design",
        "medical-research-lit",
        "not treat this alias as a separate source of truth",
    ],
    "skills/mas-scholar-skills/SKILL.md": [
        "MAS Progress And AI Judgment Rules",
        "medical-research-lit",
        "AI auto-judgment-first",
        "source_pack_ref",
        "candidate_package_ref",
        "execution_receipt_ref",
        "owner_gate_handoff_ref",
        "all ten modules",
    ],
    "skills/medical-research-lit/SKILL.md": [
        "PubMed",
        "PMID",
        "DOI",
        "claim_support_map_ref",
        "owner_gate_handoff_ref",
        "Do not fabricate citations",
    ],
    "skills/medical-manuscript-writing/SKILL.md": [
        "professional specialist",
        "AI-native medical authorship",
        "claim_evidence_map.json",
        "section_contracts.md",
        "opl connect pubmed search",
        "pubmed_source_refs",
        "pubmed_connector_invocation_ref",
        "submission_minimal_required",
        "Do not polish fiction",
    ],
    "skills/medical-manuscript-review/SKILL.md": [
        "professional specialist",
        "adversarial medical pressure test",
        "Reviewer Action Matrix",
        "sci_clinical_registry_review",
        "revision_delta_audit",
        "opl connect pubmed search",
        "pubmed_source_refs",
        "pubmed_connector_invocation_ref",
        "Do not fabricate citations",
    ],
    "skills/medical-figure-design/SKILL.md": [
        "professional specialist",
        "Medical figures are evidence surfaces",
        "Figure Intent And Claim",
        "Panel Plan",
        "Visual QA",
        "opl connect pubmed search",
        "pubmed_source_refs",
        "pubmed_connector_invocation_ref",
        "Do not silently fallback",
    ],
    "docs/capability-modules.md": [
        "progress_first_ai_auto_judgment_first",
        "AI-consumable evidence",
        "verdict_candidate",
        "route_back_candidate",
        "stop_or_continue_recommendation",
        "source_pack_ref",
        "candidate_package_ref",
        "execution_receipt_ref",
        "owner_gate_handoff_ref",
        "Parsifal",
        "paper-search-mcp",
        "LocalCitationNetwork",
        "lit-review-orchestrator",
        "AI-Scientist",
        "FAROS",
        "AutoR",
        "feedbackops_refs_only_adapter_policy",
        "target_agent_feedback_external_suite",
        "feedbackops_intake_ref",
        "MAS/OMA",
    ],
    "docs/gallery/display-gallery.md": [
        "source pack",
        "compact gallery review refs",
        "scripts/verify-display-gallery-pack.py --check",
        "publication gate",
    ],
    "packs/medical-display-core/README.md": [
        "MAS Scholar Skills-owned externalized medical display source pack",
        "gallery/medical-display/gallery_snapshot.json",
        "scripts/verify-display-gallery-pack.py --check",
        "authority = false",
        "publication_ready = false",
    ],
    "docs/candidate-artifact-engines.md": [
        "AI-consumable evidence",
        "verdict_candidate",
        "route_back_candidate",
        "stop_or_continue_recommendation",
        "source_pack_ref",
        "candidate_package_ref",
        "execution_receipt_ref",
        "owner_gate_handoff_ref",
        "Parsifal",
        "paper-search-mcp",
        "LocalCitationNetwork",
        "lit-review-orchestrator",
        "AI-Scientist",
        "FAROS",
        "AutoR",
        "不接 runtime",
        "target_agent_feedback_external_suite",
        "feedbackops_intake_ref",
        "MAS/OMA",
        "不能写 MAS/current_package",
    ],
}
for relative, tokens in required_doc_tokens.items():
    text = read_text(relative)
    for token in tokens:
        if token not in text:
            fail(f"{relative} missing required AI judgment token: {token}")

print("verify ok: mas-scholar-skills plugin, contract, medical skill sources, gallery package, and no-authority boundaries are valid")
PY
