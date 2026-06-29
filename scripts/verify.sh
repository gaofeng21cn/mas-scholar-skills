#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

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

manifest = read_json(".codex-plugin/plugin.json")
if manifest.get("name") != "opl-scholarskills":
    fail("plugin name must be opl-scholarskills")
if manifest.get("skills") != "./skills/":
    fail("plugin skills path must be ./skills/")
if manifest.get("interface", {}).get("displayName") != "OPL ScholarSkills":
    fail("plugin displayName must be OPL ScholarSkills")

skill = read_text("skills/opl-scholarskills/SKILL.md")
if not re.search(r"^---\n[\s\S]*?^name:\s+opl-scholarskills$", skill, re.MULTILINE):
    fail("SKILL.md frontmatter must expose name: opl-scholarskills")

contract = read_json("contracts/scholar-skills-capability-modules.json")
modules = contract.get("modules")
if not isinstance(modules, list) or len(modules) != 10:
    fail("contract must contain exactly 10 ScholarSkills modules")
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
    ]:
        if boundary.get(key) is not False:
            fail(f"{module_id} authority flag {key} must be false")

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

modules_by_id = {item.get("module_id"): item for item in modules}

def require_all(label: str, actual, expected) -> None:
    actual_set = set(actual or [])
    for item in expected:
        if item not in actual_set:
            fail(f"{label} missing {item}")

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
        "output_schema_refs": ["scholarskills_review_external_learning_refs.v1#adversarial_revision_route_back"],
        "refs": ["reviewer_report_ref", "adversarial_review_ref", "revision_action_ref", "halt_or_revert_rule_ref", "route_back_ref", "residual_risk_ref"],
        "policy_id": "scholarskills_review_external_learning_policy.v1",
        "sources": ["Imbad0202/academic-research-skills", "Ar9av/PaperOrchestra"],
        "boundary_tokens": ["quality_verdict", "reviewer_receipt"],
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
    "data_dictionary_ref",
    "agent_log_aggregation_ref",
    "privacy_access_tier_ref",
    "read_model_boundary_ref",
    "storage_tier_ref",
    "authoritative_body_boundary_ref",
    "derived_copy_inventory_ref",
    "analytical_format_strategy_ref",
    "cold_restore_proof_ref",
]
data_module = require_module("opl.scholarskills.data")
require_output_schema(data_module, ["scholarskills_data_external_learning_refs.v1", "scholarskills_data_asset_refs.v1"])
require_quality_refs(data_module, data_refs)
require_artifact_refs(data_module, ["scholarskills_data_manifest_candidate", "scholarskills_data_lineage_candidate"])
require_external_fit(data_module, ["Future-Scholars/paperlib", "Ar9av/PaperOrchestra", "littlepeachs/NaturePanelForge"])

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
    if policy.get("import_role") != "human_review_ref_and_source_snapshot":
        fail(f"{label} gallery import role must stay refs/source snapshot only")
    if policy.get("source_repo") != "med-autoscience":
        fail(f"{label} gallery source repo must remain med-autoscience")
    if policy.get("source_authority") != "mas_display_pack_owner_surfaces":
        fail(f"{label} gallery source authority must remain MAS display pack owner surfaces")
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
    ],
    "README.zh-CN.md": [
        "progress-first",
        "AI auto-judgment-first",
        "AI-consumable evidence",
        "verdict_candidate",
        "route_back_candidate",
        "stop/continue recommendations",
    ],
    "skills/opl-scholarskills/SKILL.md": [
        "MAS Progress And AI Judgment Rules",
        "AI auto-judgment-first",
        "stop_or_continue_recommendation",
        "Missing external runtime installation is not a blocker",
        "Only authority surfaces block ScholarSkills progression",
    ],
    "docs/capability-modules.md": [
        "progress_first_ai_auto_judgment_first",
        "AI-consumable evidence",
        "verdict_candidate",
        "route_back_candidate",
        "stop_or_continue_recommendation",
        "Parsifal",
        "paper-search-mcp",
        "LocalCitationNetwork",
        "lit-review-orchestrator",
        "AI-Scientist",
        "FAROS",
        "AutoR",
    ],
    "docs/candidate-artifact-engines.md": [
        "AI-consumable evidence",
        "verdict_candidate",
        "route_back_candidate",
        "stop_or_continue_recommendation",
        "Parsifal",
        "paper-search-mcp",
        "LocalCitationNetwork",
        "lit-review-orchestrator",
        "AI-Scientist",
        "FAROS",
        "AutoR",
        "不接 runtime",
    ],
}
for relative, tokens in required_doc_tokens.items():
    text = read_text(relative)
    for token in tokens:
        if token not in text:
            fail(f"{relative} missing required AI judgment token: {token}")

print("verify ok: opl-scholarskills plugin, contract, gallery package, and no-authority boundaries are valid")
PY
