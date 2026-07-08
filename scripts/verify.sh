#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${MAS_SCHOLAR_SKILLS_SKIP_DISPLAY_GALLERY:-0}" != "1" ]]; then
  python3 scripts/verify-display-gallery-pack.py --check
fi

for skill_kernel in skills/*/kernel.py; do
  [[ -e "$skill_kernel" ]] || continue
  python3 "$skill_kernel"
done

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
plugin_exposure = manifest.get("masScholarSkillsExposure") or {}
if plugin_exposure.get("policyRef") != "contracts/scholar-skills-capability-modules.json#/codex_skill_exposure_policy":
    fail("plugin manifest must point to codex skill exposure policy")
if plugin_exposure.get("codexDefaultExposure") is not False:
    fail("plugin manifest codex default exposure must be false")
if plugin_exposure.get("optionalInstallPolicy") != "named_specialty_only":
    fail("plugin manifest optional install policy must be named_specialty_only")

contract = read_json("contracts/scholar-skills-capability-modules.json")
domain_descriptor = read_json("contracts/domain_descriptor.json")
capability_map = read_json("contracts/capability_map.json")
classification_policy = contract.get("capability_module_classification_policy") or {}
contract_text = json.dumps(contract, ensure_ascii=False)
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
submit_skill = capability_skill_texts["medical-submission-prep"]
data_governance_skill = capability_skill_texts["medical-data-governance"]
advanced_specialist_skills = {
    skill_id: read_text(f"skills/{skill_id}/SKILL.md")
    for skill_id in advanced_specialist_skill_ids
}
medical_method_specialist_skills = {
    skill_id: read_text(f"skills/{skill_id}/SKILL.md")
    for skill_id in medical_method_specialist_skill_ids
}
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
professional_ref_templates = read_text("references/professional-quality-ref-templates.md")
if domain_descriptor.get("surface_kind") != "oma_capability_pack_target_descriptor":
    fail("domain descriptor must expose oma_capability_pack_target_descriptor")
if domain_descriptor.get("domain_id") != "mas-scholar-skills":
    fail("domain descriptor domain_id must be mas-scholar-skills")
if domain_descriptor.get("delivery_domain") != "capability_pack":
    fail("domain descriptor delivery_domain must be capability_pack")
if domain_descriptor.get("oma_consumption_policy", {}).get("capability_map_ref") != "contracts/capability_map.json":
    fail("domain descriptor must point OMA to contracts/capability_map.json")
require_all(
    "domain descriptor syncable real skills",
    domain_descriptor.get("capability_pack", {}).get("syncable_real_skills"),
    expected_capability_skills,
)
require_all(
    "domain descriptor advanced specialist skills",
    domain_descriptor.get("capability_pack", {}).get("advanced_specialist_skills"),
    advanced_specialist_skill_ids,
)
if domain_descriptor.get("capability_pack", {}).get("advanced_specialists_block_core_progress_when_missing") is not False:
    fail("advanced specialists must not block core progress when missing")
require_all(
    "domain descriptor medical-method specialist skills",
    domain_descriptor.get("capability_pack", {}).get("medical_method_specialist_skills"),
    medical_method_specialist_skill_ids,
)
if domain_descriptor.get("capability_pack", {}).get("medical_method_specialists_block_core_progress_when_missing") is not False:
    fail("medical-method specialists must not block core progress when missing")
if capability_map.get("surface_kind") != "oma_capability_pack_map":
    fail("capability map must expose oma_capability_pack_map")
if capability_map.get("domain_id") != "mas-scholar-skills":
    fail("capability map domain_id must be mas-scholar-skills")
if capability_map.get("delivery_domain") != "capability_pack":
    fail("capability map delivery_domain must be capability_pack")
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
        fail(f"optional specialist {skill_id} must not be default exposure")
    if item.get("optional_named_specialty_only") is not True:
        fail(f"optional specialist {skill_id} must be named-specialty only")
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
if exposure_policy.get("default_install_policy") != "compact_workspace_or_quest_install_includes_aggregate_and_core_skills_only":
    fail("codex skill exposure policy must keep default install compact")
if exposure_policy.get("aggregate_skill_ids") != aggregate_skill_ids:
    fail("codex skill exposure aggregate skill ids must match")
if exposure_policy.get("core_skill_ids") != expected_capability_skills:
    fail("codex skill exposure core skill ids must match real syncable skills")
if exposure_policy.get("default_exposure_skill_ids") != expected_default_exposure_skill_ids:
    fail("codex skill exposure default skill ids must be aggregate + core skills")
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
    ["named_specialty_workspace", "named_specialty_quest", "explicit_codex_developer"],
)
require_all(
    "codex skill exposure optional named specialty scopes",
    allowed_scopes.get("optional_named_specialty"),
    ["named_specialty_workspace", "named_specialty_quest", "explicit_codex_developer"],
)
redirect_policy = exposure_policy.get("redirect_tombstone_policy", "")
if "Retired optional professional skill metadata" not in redirect_policy or "capability_preserved=true" not in redirect_policy:
    fail("codex skill exposure redirect policy must describe retired optional professional skill redirects")
if "Only opl-scholarskills" not in exposure_policy.get("tombstone_policy", ""):
    fail("codex skill exposure tombstone policy must tombstone only opl-scholarskills")
if plugin_exposure.get("defaultWorkspaceOrQuestInstall") != expected_default_exposure_skill_ids:
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
        ["candidate_package_ref", "execution_receipt_ref", "owner_gate_handoff_ref"],
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
require_all(
    "medical-method specialist required handoff refs",
    method_policy.get("required_handoff_refs"),
    ["candidate_package_ref", "route_back_candidate", "owner_gate_handoff_ref"],
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
    "medical-figure-design": ["figure_contract_template_ref", "figure_contract_ref", "panel_evidence_chain_ref", "candidate_set_ref", "critic_review_ref"],
    "medical-figure-style": ["data_fidelity_ref", "claim_title_truth_ref", "label_economy_ref", "color_vision_check_ref", "export_lint_ref"],
    "medical-figure-composer": ["multi_panel_outline_ref", "panel_render_receipt_ref", "composite_review_ref", "final_size_export_ref", "owner_gate_handoff_ref"],
    "medical-manuscript-writing": ["one_sentence_argument_ref", "terminology_ledger_ref", "paragraph_job_map_ref", "claim_citation_quality_loop_ref", "citation_quality_action_matrix_ref"],
    "medical-manuscript-review": ["review_fact_base_ref", "technical_reviewer_lane", "cross_review_synthesis_ref", "claim_citation_quality_loop_ref", "citation_quality_action_matrix_ref"],
    "medical-research-lit": ["source_ref_chain_template_ref", "fallback_source_refs", "deduplication_ref", "source_acceptance_decision_ref", "support_strength_matrix_ref"],
    "medical-statistical-review": ["estimand_or_target_parameter_ref", "effect_size_and_uncertainty_ref", "statistical_action_matrix_ref"],
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
    "connect_pubmed_search",
    "pubmed_source_refs",
    "pubmed_connector_invocation_ref",
    "read_only_normalized_source_refs_not_literature_verdict_or_domain_truth",
]:
    if token not in contract_text:
        fail(f"contract missing PubMed Connect Lit token: {token}")

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
        "figure_contract_template_ref",
        "source_ref_chain_template_ref",
        "claim_citation_quality_loop_ref",
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

modules = contract.get("modules")
if not isinstance(modules, list) or len(modules) != 8:
    fail("contract must contain exactly 8 active ScholarSkills modules")
active_module_ids = {item.get("module_id") for item in modules}
expected_active_module_ids = {
    "mas-scholar-skills.display",
    "mas-scholar-skills.tables",
    "mas-scholar-skills.stats",
    "mas-scholar-skills.lit",
    "mas-scholar-skills.write",
    "mas-scholar-skills.review",
    "mas-scholar-skills.submit",
    "mas-scholar-skills.data",
}
if active_module_ids != expected_active_module_ids:
    fail("active module ids must use mas-scholar-skills.* canonical ids")
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
    "candidate_package_ref",
    "execution_receipt_ref",
    "owner_gate_handoff_ref",
]
standard_handoff = contract.get("standard_handoff_ref_families") or {}
if standard_handoff.get("policy_id") != "scholarskills_standard_refs_only_handoff.v1":
    fail("contract missing standard refs-only handoff policy")
if standard_handoff.get("applies_to_modules") != "active_professional_skill_modules":
    fail("standard handoff policy must apply to active professional skill modules")
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
    "materialized_candidate_package",
    "External Learning Module Fit",
    "gallery/medical-display/medical_display_gallery.pdf",
    "scholarskills_scientific_figure_quality_floor.v1",
    "brief_first_reference_guided_ai_candidate_not_single_template_reuse",
    "critic_review_ref",
    "external_runtime_install_not_required_before_candidate_refs_or_checklists",
    "FeedbackOps Refs-Only Adapter",
    "target_agent_feedback_external_suite",
    "feedbackops_refs_only_adapter_policy",
    "feedback_self_evolution_trigger",
    "medical-research-lit",
]:
    if token not in skill:
        fail(f"SKILL.md missing required token: {token}")

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
        "candidate_package_ref",
        "execution_receipt_ref",
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
    if token not in skill:
        fail(f"SKILL.md missing Data lifecycle token: {token}")

for relative, text in [
    ("skills/mas-scholar-skills/SKILL.md", skill),
    ("skills/medical-data-governance/SKILL.md", data_governance_skill),
]:
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
    "candidate_package_ref",
    "execution_receipt_ref",
    "owner_gate_handoff_ref",
    "Every module should expose the standard refs-only handoff family",
]:
    if token not in skill:
        fail(f"SKILL.md missing standard handoff token: {token}")

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
    "__pycache__/",
    "*.pyc",
]:
    if pattern not in gitignore:
        fail(f".gitignore missing intermediate-output pattern {pattern}")

print("verify ok: mas-scholar-skills plugin, contract, medical skill sources, gallery package, and no-authority boundaries are valid")
PY
