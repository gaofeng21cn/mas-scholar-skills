#!/usr/bin/env python3
"""Validate the ScholarSkills medical-display source pack and review gallery."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import pathlib
import sys
import tomllib

from gallery_policy import verify_gallery_import_policy


ROOT = pathlib.Path(__file__).resolve().parents[1]
PACK_ROOT = ROOT / "packs" / "medical-display-core"
GALLERY_ROOT = ROOT / "gallery" / "medical-display"
PACK_LEVEL_EXECUTION_MODE = "declared_by_template"
EXPECTED_EXAMPLE_TEMPLATE_IDS = [
    "roc_curve_binary",
    "calibration_curve_binary",
    "kaplan_meier_grouped",
    "heatmap_group_comparison",
    "submission_graphical_abstract",
    "table1_baseline_characteristics",
]
EXPECTED_GOLDEN_TEMPLATE_IDS = EXPECTED_EXAMPLE_TEMPLATE_IDS
EXPECTED_TABLE_PREVIEW_TEMPLATE_IDS = {"table1_baseline_characteristics"}
ALLOWED_ADAPTATION_MODES = [
    "declared_template",
    "schema_adapted_template",
    "reference_guided_new_render",
    "original_new_render",
]
NOT_APPLICABLE_NEW_RENDER_REF = "not_applicable:new_render"
ORIGINAL_NEW_RENDER_MODE = "original_new_render"
NO_REUSABLE_SOURCE_REF = "not_applicable:no_reusable_source"
LIVE_REGRESSION_ENGINE_REF = (
    "packs/medical-display-core/src/"
    "fenggaolab_org_medical_display_core/live_regression.py"
)
HARD_STOP_CONDITIONS = [
    "missing_required_evidence",
    "missing_or_unreadable_artifact",
    "blank_artifact",
    "invalid_geometry",
    "unsupported_visible_claim",
    "hard_figure_contract_failure",
]


def fail(message: str) -> None:
    print(f"display gallery pack verify failed: {message}", file=sys.stderr)
    sys.exit(1)


def read_json(path: pathlib.Path) -> dict:
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_toml(path: pathlib.Path) -> dict:
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")
    return tomllib.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_false_flags(container: dict, label: str, keys: list[str]) -> None:
    for key in keys:
        if container.get(key) is not False:
            fail(f"{label} must keep {key}=false")


def require_all_fields(container: dict, label: str, fields: list[str]) -> None:
    actual = set(container.get("required_fields") or [])
    for field in fields:
        if field not in actual:
            fail(f"{label} missing required field {field}")


def require_adaptation_provenance(container: dict, label: str) -> None:
    adaptation_mode = container.get("adaptation_mode")
    if adaptation_mode not in ALLOWED_ADAPTATION_MODES:
        fail(f"{label} has invalid adaptation_mode")
    source_free = adaptation_mode == ORIGINAL_NEW_RENDER_MODE
    if (
        container.get("template_or_asset_ref") == NOT_APPLICABLE_NEW_RENDER_REF
    ) != source_free:
        fail(f"{label} must pair not_applicable:new_render with original_new_render")
    for field in ("semantic_match_ref", "transform_delta_ref"):
        if (container.get(field) == NO_REUSABLE_SOURCE_REF) != source_free:
            fail(
                f"{label} must reserve {NO_REUSABLE_SOURCE_REF} "
                "for source-free provenance"
            )


def verify_receipt_templates() -> dict:
    contract = read_json(ROOT / "contracts" / "display-pack-receipt-templates.json")
    if contract.get("contract_id") != "mas_scholar_skills_display_pack_receipt_templates":
        fail("display-pack receipt templates contract has wrong contract_id")
    if contract.get("schema_version") != "1.6.0":
        fail("display-pack receipt templates contract must use schema_version 1.6.0")
    if contract.get("state") != "active_refs_only_template":
        fail("display-pack receipt templates contract must stay refs-only")
    require_false_flags(
        contract.get("authority_boundary") or {},
        "display-pack receipt templates authority boundary",
        [
            "can_write_domain_truth",
            "can_mutate_artifact_body",
            "can_sign_owner_receipt",
            "can_create_typed_blocker",
            "can_claim_quality_verdict",
            "can_claim_publication_readiness",
            "can_claim_current_package_authority",
        ],
    )
    if contract.get("receipt_chain") != [
        "professional_figure_workflow_ref",
        "figure_contract_ref",
        "render_or_generation_receipt_ref",
        "layout_qc_receipt_ref",
        "visual_qa_receipt_ref",
        "owner_gate_handoff_ref",
    ]:
        fail(
            "display-pack receipt chain must remain "
            "professional_skill->figure->render_or_generation->layout_qc->"
            "visual_qa->owner_gate"
        )
    workflow = contract.get("professional_figure_workflow_ref") or {}
    if workflow.get("schema_ref") != "contracts/professional-figure-workflow.schema.json":
        fail("professional figure workflow must bind the canonical schema")
    if workflow.get("surface_kind") != "mas_scholar_skills_professional_figure_workflow_candidate.v1":
        fail("professional figure workflow has the wrong surface kind")
    if workflow.get("new_or_materially_repaired_figure_requires") != [
        "medical-figure-design"
    ]:
        fail("new or materially repaired figures must consume medical-figure-design")
    if workflow.get("final_visual_qa_requires") != ["medical-figure-style"]:
        fail("final visual QA must consume medical-figure-style")
    conditional_skills = workflow.get("conditional_skill_rules") or {}
    if conditional_skills.get("assembled_panels_requires") != "medical-figure-composer":
        fail("assembled panels must consume medical-figure-composer")
    if conditional_skills.get("single_canvas_direct_forbids_invented_composer_receipt") is not True:
        fail("single-canvas figures must not invent composer receipts")
    template_policy = workflow.get("template_policy") or {}
    for field in (
        "template_use_is_optional",
        "template_is_reference_quality_floor_not_mandatory_layout",
        "record_provenance_only_when_template_used",
        "no_template_use_requires_only_decision_reason",
    ):
        if template_policy.get(field) is not True:
            fail(f"professional figure template policy must keep {field}=true")
    text_policy = workflow.get("evidence_figure_text_policy") or {}
    for field in ("embedded_title", "embedded_subtitle", "embedded_prose_footer"):
        if text_policy.get(field) is not False:
            fail(f"evidence figure text policy must keep {field}=false")
    if text_policy.get("allowed_text_roles") != [
        "panel_label",
        "axis_label",
        "tick_label",
        "legend",
        "necessary_statistical_annotation",
    ]:
        fail("evidence figure text policy has invalid allowed text roles")
    if text_policy.get("graphical_abstract_exempt") is not True:
        fail("graphical abstracts must remain explicitly exempt")
    semantic_flow_policy = workflow.get("semantic_flow_policy") or {}
    for field in (
        "declared_flow_or_schematic_requires_complete_semantic_artist_registry",
        "connector_and_bracket_segments_require_renderer_path_geometry",
        "shared_junction_requires_common_renderer_path_prefix",
        "segmented_band_parent_connector_requires_exact_group_span_contract",
        "segmented_group_requires_full_span_labeled_midpoint_anchor",
        "segmented_group_requires_renderer_bound_actual_path_geometry",
        "unsupported_segmented_group_orientation_or_anchor_mode_fails_closed",
    ):
        if semantic_flow_policy.get(field) is not True:
            fail(f"professional figure semantic-flow policy must require {field}")
    if (
        semantic_flow_policy.get("text_only_bbox_pass_is_sufficient") is not False
        or semantic_flow_policy.get("hard_coded_zero_violation_counts_allowed")
        is not False
    ):
        fail("professional figure workflow must fail closed on semantic flow geometry")
    missing_receipt = workflow.get("missing_or_stale_receipt_behavior") or {}
    if missing_receipt.get("blocks_stage_liveness") is not False:
        fail("missing professional Figure Skill receipt must not block stage liveness")
    for field in (
        "creates_quality_debt",
        "blocks_quality_readiness",
        "blocks_export_readiness",
        "blocks_publication_readiness",
    ):
        if missing_receipt.get(field) is not True:
            fail(f"missing professional Figure Skill receipt must keep {field}=true")
    require_false_flags(workflow, "professional_figure_workflow_ref", ["authority", "publication_ready"])
    adaptation_policy = contract.get("template_asset_adaptation_policy") or {}
    if adaptation_policy.get("allowed_adaptation_modes") != ALLOWED_ADAPTATION_MODES:
        fail("template/asset adaptation policy has invalid adaptation modes")
    if adaptation_policy.get("not_applicable_new_render_mapping") != {
        "fixture_scope": "figure_or_panel_provenance_not_issued_render_receipt",
        "template_or_asset_ref": NOT_APPLICABLE_NEW_RENDER_REF,
        "adaptation_mode": ORIGINAL_NEW_RENDER_MODE,
        "semantic_match_ref": NO_REUSABLE_SOURCE_REF,
        "transform_delta_ref": NO_REUSABLE_SOURCE_REF,
        "pack_render_receipt_requires_actual_outputs": True,
        "forbids_invented_reference_provenance": True,
    }:
        fail("template/asset adaptation policy must map no-source renders without invented provenance")
    require_adaptation_provenance(
        adaptation_policy["not_applicable_new_render_mapping"],
        "source-free figure/panel provenance fixture",
    )
    if adaptation_policy.get("warnings_remain_repair_hints") is not True:
        fail("template/asset adaptation warnings must remain repair hints")
    if adaptation_policy.get("hard_stop_conditions") != HARD_STOP_CONDITIONS:
        fail("template/asset adaptation policy has invalid hard-stop conditions")
    require_all_fields(
        contract.get("figure_contract_ref") or {},
        "figure_contract_ref",
        [
            "core_conclusion_ref",
            "panel_evidence_chain_ref",
            "professional_figure_workflow_ref",
            "figure_text_policy_ref",
            "renderer_decision_ref",
            "owner_gate_handoff_ref",
        ],
    )
    template_selection = (contract.get("figure_contract_ref") or {}).get(
        "template_selection_policy"
    ) or {}
    if template_selection != {
        "required": False,
        "record_only_when_template_or_asset_is_used": True,
        "must_not_invent_template_provenance_for_original_render": True,
    }:
        fail("figure_contract_ref must keep template selection conditional")
    if (contract.get("render_or_generation_receipt_ref") or {}) != {
        "one_of": ["render_receipt_ref", "generation_receipt_ref"],
        "exactly_one_required_per_figure": True,
    }:
        fail("figure workflow must require exactly one render or generation receipt")
    render_receipt = contract.get("render_receipt_ref") or {}
    if render_receipt.get("scope") != "actual_display_pack_render_only":
        fail("render_receipt_ref must be limited to actual Display Pack renders")
    require_all_fields(
        render_receipt,
        "render_receipt_ref",
        [
            "figure_contract_ref",
            "pack_id",
            "template_id",
            "renderer_family",
            "render_mode",
            "outputs",
            "layout_sidecar_ref",
            "template_or_asset_ref",
            "semantic_match_ref",
            "adaptation_mode",
            "transform_delta_ref",
            "source_data_ref",
            "degradation_reason",
            "authority",
            "publication_ready",
        ],
    )
    if render_receipt.get("allowed_render_modes") != ["final", "candidate"]:
        fail("render_receipt_ref allowed_render_modes must be final/candidate")
    if render_receipt.get("allowed_adaptation_modes") != ALLOWED_ADAPTATION_MODES:
        fail("render_receipt_ref has invalid adaptation modes")
    if render_receipt.get("degradation_reason_required_when_fidelity_reduced") is not True:
        fail("render_receipt_ref must require an explicit fidelity degradation reason")
    require_false_flags(render_receipt, "render_receipt_ref", ["authority", "publication_ready"])
    generation_receipt = contract.get("generation_receipt_ref") or {}
    if generation_receipt.get("scope") != "paper_local_or_non_pack_render":
        fail("generation_receipt_ref must cover paper-local or non-pack renders")
    require_all_fields(
        generation_receipt,
        "generation_receipt_ref",
        [
            "receipt_id",
            "renderer_family",
            "renderer_version",
            "source_code_ref",
            "source_code_sha256",
            "input_manifest_ref",
            "input_manifest_sha256",
            "outputs",
        ],
    )
    if generation_receipt.get("required_artifact_formats") != ["PNG", "PDF"]:
        fail("generation_receipt_ref must bind the final PNG/PDF pair")
    if generation_receipt.get("template_fields_required") is not False:
        fail("paper-local generation receipts must not require template fields")
    if generation_receipt.get("must_bind_exact_final_output_sha256") is not True:
        fail("generation_receipt_ref must bind exact final output hashes")
    require_false_flags(
        generation_receipt,
        "generation_receipt_ref",
        ["authority", "publication_ready"],
    )
    layout_qc_receipt = contract.get("layout_qc_receipt_ref") or {}
    if layout_qc_receipt.get("surface_kind") != "layout_qc_receipt_candidate.v1":
        fail("layout_qc_receipt_ref must use the candidate v1 surface")
    require_all_fields(
        layout_qc_receipt,
        "layout_qc_receipt_ref",
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
    if layout_qc_receipt.get("required_artifact_formats") != ["PNG", "PDF"]:
        fail("layout_qc_receipt_ref must bind the final PNG/PDF pair")
    semantic_geometry_checks = {
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
    }
    if not semantic_geometry_checks.issubset(
        set(layout_qc_receipt.get("required_geometry_checks") or [])
    ):
        fail("layout_qc_receipt_ref must require semantic artist geometry checks")
    if (layout_qc_receipt.get("export_policy") or {}) != {
        "canvas_mode": "fixed",
        "matplotlib_bbox_inches": None,
        "equivalent_backend_policy": "fixed_canvas_no_tight_crop",
    }:
        fail("layout_qc_receipt_ref must require a fixed no-tight-crop canvas")
    require_false_flags(
        layout_qc_receipt,
        "layout_qc_receipt_ref",
        ["authority", "publication_ready", "machine_check_is_quality_verdict"],
    )
    layout_authority = layout_qc_receipt.get("authority_boundary") or {}
    if layout_authority.get("refs_only") is not True:
        fail("layout_qc_receipt_ref must remain refs-only")
    require_false_flags(
        layout_authority,
        "layout_qc_receipt_ref authority boundary",
        [
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
        ],
    )
    visual_qa_receipt = contract.get("visual_qa_receipt_ref") or {}
    require_all_fields(
        visual_qa_receipt,
        "visual_qa_receipt_ref",
        [
            "render_receipt_ref",
            "layout_qc_receipt_ref",
            "final_size_export_ref",
            "export_lint_ref",
            "professional_figure_style_invocation_ref",
            "final_output_artifact_bindings",
            "route_back_items",
            "owner_gate_handoff_ref",
            "authority",
            "publication_ready",
        ],
    )
    require_false_flags(visual_qa_receipt, "visual_qa_receipt_ref", ["authority", "publication_ready"])
    return {"receipt_contract_id": contract["contract_id"]}


def format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def load_display_pack() -> dict:
    display_pack = read_toml(PACK_ROOT / "display_pack.toml")
    if display_pack.get("pack_id") != "fenggaolab.org.medical-display-core":
        fail("display_pack.toml has wrong pack_id")
    if display_pack.get("pack_kind") != "display_pack":
        fail("display_pack.toml must declare pack_kind=display_pack")
    if display_pack.get("capability_kind") != "reference_pack":
        fail("display_pack.toml must declare capability_kind=reference_pack")
    if display_pack.get("default_execution_mode") != PACK_LEVEL_EXECUTION_MODE:
        fail(f"display_pack.toml default_execution_mode must be {PACK_LEVEL_EXECUTION_MODE}")
    if display_pack.get("source") != "scholarskills-managed-external-pack":
        fail("display_pack.toml must be ScholarSkills-managed")
    if display_pack.get("opl_pack_descriptor_ref") != "opl_pack.json":
        fail("display_pack.toml must point to opl_pack.json")
    if display_pack.get("supported_actions") != ["render", "gallery"]:
        fail("display_pack.toml supported_actions must be render/gallery")
    if display_pack.get("supported_render_modes") != ["final", "candidate"]:
        fail("display_pack.toml supported_render_modes must be final/candidate")
    require_false_flags(
        display_pack,
        "display_pack.toml",
        [
            "authority",
            "publication_ready",
            "artifact_authority",
            "owner_receipt_authority",
            "typed_blocker_authority",
        ],
    )
    if display_pack.get("heavy_render_intermediates_excluded") is not True:
        fail("display_pack.toml must exclude heavy render intermediates")
    return display_pack


def load_opl_pack(display_pack: dict) -> dict:
    opl_pack = read_json(PACK_ROOT / "opl_pack.json")
    if opl_pack.get("pack_id") != display_pack["pack_id"]:
        fail("opl_pack.json pack_id does not match display_pack.toml")
    if opl_pack.get("pack_kind") != "display_pack":
        fail("opl_pack.json must declare display_pack kind")
    if opl_pack.get("modes") != display_pack["supported_render_modes"]:
        fail("opl_pack.json modes must match display_pack.toml supported_render_modes")
    require_false_flags(
        opl_pack.get("authority_boundary") or {},
        "opl_pack.json authority boundary",
        [
            "can_write_domain_truth",
            "can_mutate_artifact_body",
            "can_sign_domain_owner_receipt",
            "can_authorize_quality_verdict",
            "can_authorize_publication_readiness",
            "can_authorize_grant_readiness",
            "can_authorize_visual_export_readiness",
            "can_authorize_app_release_readiness",
            "provider_completion_is_pack_quality_ready",
        ],
    )
    return opl_pack


def expected_template_resources(
    display_pack: dict,
) -> tuple[list[dict], dict[str, int], dict[str, dict], dict[str, dict]]:
    catalog = read_json(PACK_ROOT / "canonical_template_catalog.json")
    if catalog.get("pack_id") != display_pack["pack_id"]:
        fail("canonical_template_catalog.json pack_id does not match display_pack.toml")
    families = catalog.get("families")
    if not isinstance(families, list) or not families:
        fail("canonical_template_catalog.json must contain template families")

    seen_template_ids: set[str] = set()
    renderer_counts: dict[str, int] = {}
    template_resources: list[dict] = []
    template_facts: dict[str, dict] = {}
    reference_facts: dict[str, dict] = {}
    pack_render_modes = display_pack["supported_render_modes"]
    for family in families:
        template_id = family.get("canonical_template_id")
        if not template_id:
            fail("catalog family missing canonical_template_id")
        if template_id in seen_template_ids:
            fail(f"duplicate canonical_template_id {template_id}")
        seen_template_ids.add(template_id)
        template_dir = PACK_ROOT / "templates" / template_id
        descriptor = read_toml(template_dir / "template.toml")
        if descriptor.get("template_id") != template_id:
            fail(f"{template_id} descriptor template_id mismatch")
        if descriptor.get("full_template_id") != f"{display_pack['pack_id']}::{template_id}":
            fail(f"{template_id} descriptor full_template_id mismatch")
        renderer_family = descriptor.get("renderer_family")
        if not renderer_family:
            fail(f"{template_id} descriptor missing renderer_family")
        kind = descriptor.get("kind")
        if not kind:
            fail(f"{template_id} descriptor missing kind")
        descriptor_inventory_class = descriptor.get("inventory_class", "canonical")
        descriptor_default_visible = descriptor.get("default_visible", True)
        if descriptor_inventory_class != "canonical" or descriptor_default_visible is not True:
            fail(f"canonical template {template_id} descriptor must stay canonical/default-visible")
        family_provenance_refs = family.get("paper_provenance_refs") or []
        if family_provenance_refs:
            if descriptor.get("paper_provenance_refs") != family_provenance_refs:
                fail(f"canonical template {template_id} paper provenance drifted")
        gallery_category = {
            ("evidence_figure", "r_ggplot2"): "evidence",
            ("illustration_shell", "r_ggplot2"): "reporting_flow",
            ("illustration_shell", "python"): "design",
            ("table_shell", "n/a"): "table_shell",
        }.get((kind, renderer_family))
        if gallery_category is None:
            fail(
                f"canonical template {template_id} has unsupported gallery classification "
                f"kind={kind} renderer_family={renderer_family}"
            )
        for field in (
            "family_id",
            "title",
            "category",
            "analysis_responsibility",
        ):
            if not family.get(field):
                fail(f"catalog family {template_id} missing {field}")
        medical_family_ids = family.get("medical_family_ids")
        if not isinstance(medical_family_ids, list) or not medical_family_ids:
            fail(f"catalog family {template_id} missing medical_family_ids")
        if len(medical_family_ids) != len(set(medical_family_ids)):
            fail(f"catalog family {template_id} has duplicate medical_family_ids")
        renderer_counts[renderer_family] = renderer_counts.get(renderer_family, 0) + 1
        if (template_dir / "render_candidate.R").exists():
            fail(f"{template_id} must not carry template-local render_candidate.R")
        if (template_dir / "render.R").exists():
            fail(f"{template_id} must not carry template-local render.R; use pack-level render.R")
        if renderer_family == "r_ggplot2":
            if descriptor.get("supported_render_modes") != pack_render_modes:
                fail(f"{template_id} supported_render_modes must match display_pack.toml")
            if descriptor.get("execution_mode") != "subprocess":
                fail(f"{template_id} must use subprocess execution_mode")
            expected_entrypoint = f"Rscript ../../render.R --template {template_id} --mode {{render_mode}} --request {{request_json}}"
            if descriptor.get("entrypoint") != expected_entrypoint:
                fail(f"{template_id} must use the pack-level render.R entrypoint")
        template_resources.append(
            {
                "resource_id": f"template.{template_id}",
                "role": "template",
                "ref": f"templates/{template_id}/template.toml",
            }
        )
        template_facts[template_id] = {
            "template_id": template_id,
            "kind": kind,
            "renderer_family": renderer_family,
            "gallery_category": gallery_category,
            "family_id": family["family_id"],
            "title": family["title"],
            "category": family["category"],
            "analysis_responsibility": family["analysis_responsibility"],
            "medical_family_ids": medical_family_ids,
        }

    references = catalog.get("paper_derived_references", [])
    if not isinstance(references, list):
        fail("canonical_template_catalog.json paper_derived_references must be a list")
    for reference in references:
        if not isinstance(reference, dict):
            fail("paper_derived_references entries must be objects")
        template_id = reference.get("template_id")
        if not isinstance(template_id, str) or not template_id:
            fail("paper-derived reference missing template_id")
        if template_id in seen_template_ids:
            fail(f"paper-derived reference {template_id} is also canonical")
        if template_id in reference_facts:
            fail(f"duplicate paper-derived reference {template_id}")
        if reference.get("resource_class") != "paper_derived_reference":
            fail(f"paper-derived reference {template_id} has invalid resource_class")
        if reference.get("default_visible") is not False:
            fail(f"paper-derived reference {template_id} must set default_visible=false")
        provenance_refs = reference.get("paper_provenance_refs")
        if not isinstance(provenance_refs, list) or not provenance_refs:
            fail(f"paper-derived reference {template_id} requires paper_provenance_refs")
        template_dir = PACK_ROOT / "templates" / template_id
        descriptor = read_toml(template_dir / "template.toml")
        if descriptor.get("template_id") != template_id:
            fail(f"paper-derived reference {template_id} descriptor template_id mismatch")
        if descriptor.get("kind") != "table_shell":
            fail(f"paper-derived reference {template_id} must remain a table_shell")
        if descriptor.get("inventory_class") != "paper_derived_reference":
            fail(f"paper-derived reference {template_id} descriptor inventory_class mismatch")
        if descriptor.get("default_visible") is not False:
            fail(f"paper-derived reference {template_id} descriptor must set default_visible=false")
        if descriptor.get("paper_provenance_refs") != provenance_refs:
            fail(f"paper-derived reference {template_id} provenance drifted")
        template_resources.append(
            {
                "resource_id": f"template.{template_id}",
                "role": "template",
                "ref": f"templates/{template_id}/template.toml",
                "inventory_class": "paper_derived_reference",
                "default_visible": False,
            }
        )
        reference_facts[template_id] = {
            "template_id": template_id,
            "resource_class": "paper_derived_reference",
            "default_visible": False,
            "paper_provenance_refs": provenance_refs,
        }

    descriptor_template_ids = {
        path.parent.name for path in (PACK_ROOT / "templates").glob("*/template.toml")
    }
    inventory_template_ids = seen_template_ids | set(reference_facts)
    if descriptor_template_ids != inventory_template_ids:
        missing = sorted(inventory_template_ids - descriptor_template_ids)
        extra = sorted(descriptor_template_ids - inventory_template_ids)
        fail(f"template descriptor/catalog mismatch: missing={missing} extra={extra}")

    for template_id in (
        "phenotype_gap_structure_figure",
        "site_held_out_stability_figure",
        "treatment_gap_alignment_figure",
    ):
        descriptor = read_toml(PACK_ROOT / "templates" / template_id / "template.toml")
        exposed_text = " ".join(
            str(descriptor.get(field) or "")
            for field in ("display_name", "input_schema_ref", "qc_profile_ref")
        ).lower()
        if "dpcc" in exposed_text:
            fail(f"canonical template {template_id} exposes DPCC in default descriptor semantics")

    return template_resources, renderer_counts, template_facts, reference_facts


def is_template_resource(resource: dict) -> bool:
    return resource.get("role") == "template" or resource.get("kind") == "template"


def generated_opl_pack(opl_pack: dict, template_resources: list[dict]) -> dict:
    generated = dict(opl_pack)
    resources = opl_pack.get("resources")
    if not isinstance(resources, list):
        fail("opl_pack.json resources must be a list")
    replaced = False
    generated_resources: list[dict] = []
    for resource in resources:
        if is_template_resource(resource):
            if not replaced:
                generated_resources.extend(template_resources)
                replaced = True
            continue
        generated_resources.append(resource)
    if not replaced:
        generated_resources.extend(template_resources)
    generated["resources"] = generated_resources
    return generated


def verify_source_pack() -> dict:
    display_pack = load_display_pack()
    opl_pack = load_opl_pack(display_pack)
    template_resources, renderer_counts, template_facts, reference_facts = expected_template_resources(
        display_pack
    )
    generated = generated_opl_pack(opl_pack, template_resources)
    if opl_pack != generated:
        fail("opl_pack.json template resources drifted; run scripts/verify-display-gallery-pack.py --sync-opl-pack")

    resource_template_ids = {resource["resource_id"].removeprefix("template.") for resource in template_resources}
    opl_template_ids: set[str] = set()
    for resource in opl_pack.get("resources") or []:
        if not is_template_resource(resource):
            continue
        ref = pathlib.PurePosixPath(str(resource.get("ref") or ""))
        parts = ref.parts
        if len(parts) != 3 or parts[0] != "templates" or parts[2] != "template.toml":
            fail(f"opl_pack.json template resource has invalid ref {resource.get('ref')}")
        template_id = parts[1]
        if resource.get("resource_id") != f"template.{template_id}":
            fail(f"opl_pack.json template resource_id mismatch for {template_id}")
        if template_id in opl_template_ids:
            fail(f"opl_pack.json duplicate template resource {template_id}")
        opl_template_ids.add(template_id)
    if opl_template_ids != resource_template_ids:
        missing = sorted(resource_template_ids - opl_template_ids)
        extra = sorted(opl_template_ids - resource_template_ids)
        fail(f"opl_pack.json template resources/catalog mismatch: missing={missing} extra={extra}")

    for required in [
        "opl_pack.json",
        "golden_manifest.json",
        "render.R",
        "fixtures/registry_gallery_cases.json",
        "renderer_dependency_profile.json",
        "renderer_migration_ledger.json",
        "rlib/medicaldisplaycore/evidence_renderer.R",
        "rlib/medicaldisplaycore/evidence_renderer_parts/data_frames.R",
        "rlib/medicaldisplaycore/evidence_renderer_parts/layouts.R",
        "rlib/medicaldisplaycore/evidence_renderer_parts/style.R",
        "rlib/medicaldisplaycore/candidate_renderer.R",
        "rlib/medicaldisplaycore/cohort_flow_renderer.R",
        "rlib/medicaldisplaycore/registry_gallery_renderers.R",
        "rlib/medicaldisplaycore/stratified_display_renderers.R",
        "src/fenggaolab_org_medical_display_core/__init__.py",
        "tests/render_registry_gallery_templates.py",
    ]:
        if not (PACK_ROOT / required).is_file():
            fail(f"missing source pack file packs/medical-display-core/{required}")

    dependency_profile = read_json(PACK_ROOT / "renderer_dependency_profile.json")
    cohort_profiles = [
        profile
        for profile in dependency_profile.get("profiles") or []
        if profile.get("profile_id") == "r_ggplot2_ggconsort_reporting_flow_v1"
    ]
    if len(cohort_profiles) != 1:
        fail("renderer dependency profile must declare one ggconsort reporting-flow profile")
    ggconsort_packages = [
        package
        for package in (cohort_profiles[0].get("language_packages") or {}).get("r") or []
        if package.get("name") == "ggconsort"
    ]
    if len(ggconsort_packages) != 1:
        fail("ggconsort reporting-flow profile must declare one ggconsort package")
    ggconsort_package = ggconsort_packages[0]
    if ggconsort_package.get("minimum_version") != "0.1.0":
        fail("ggconsort reporting-flow profile must require minimum_version 0.1.0")
    if ggconsort_package.get("required_exports") != [
        "cohort_start",
        "consort_box_add",
        "consort_arrow_add",
        "create_consort_data",
        "theme_consort",
    ]:
        fail("ggconsort reporting-flow profile required_exports mismatch")

    for pattern in ["*.png", "*.svg", "*.html", "*.layout.json", "*render_cache*"]:
        matches = list(PACK_ROOT.rglob(pattern))
        if matches:
            fail(f"source pack contains generated artifact {matches[0].relative_to(ROOT)}")

    return {
        "catalog_template_count": len(template_facts),
        "opl_template_resource_count": len(opl_template_ids),
        "paper_derived_reference_count": len(reference_facts),
        "renderer_counts": renderer_counts,
        "template_facts": template_facts,
        "reference_facts": reference_facts,
    }


def verify_one_template_example(template_id: str) -> dict:
    template_dir = PACK_ROOT / "templates" / template_id
    descriptor = read_toml(template_dir / "template.toml")
    example_input = read_json(template_dir / "example_input.json")
    example_receipt = read_json(template_dir / "example_render_receipt.json")
    if example_input.get("example_only") is not True:
        fail(f"{template_id} example_input.json must keep example_only=true")
    if example_input.get("template_id") != template_id:
        fail(f"{template_id} example_input.json template_id mismatch")
    if example_receipt.get("example_only") is not True:
        fail(f"{template_id} example_render_receipt.json must keep example_only=true")
    for key in ["authority", "publication_ready"]:
        if example_receipt.get(key) is not False:
            fail(f"{template_id} example_render_receipt.json must keep {key}=false")
    for key in ["template_id", "renderer_family", "execution_mode"]:
        if example_receipt.get(key) != descriptor.get(key):
            fail(f"{template_id} example_render_receipt.json {key} mismatch")
    if example_receipt.get("pack_id") != "fenggaolab.org.medical-display-core":
        fail(f"{template_id} example_render_receipt.json pack_id mismatch")
    if example_receipt.get("render_mode") not in ["final", "candidate"]:
        fail(f"{template_id} example_render_receipt.json render_mode must be final/candidate")
    if not isinstance(example_receipt.get("outputs"), dict) or not example_receipt["outputs"]:
        fail(f"{template_id} example_render_receipt.json must declare output refs")
    if not str(example_receipt.get("layout_sidecar_ref") or "").startswith("repo-local:examples/not-rendered/"):
        fail(f"{template_id} example_render_receipt.json must use not-rendered layout sidecar ref")
    expected_template_ref = f"repo-local:packs/medical-display-core/templates/{template_id}/template.toml"
    template_or_asset_ref = example_receipt.get("template_or_asset_ref")
    if template_or_asset_ref != expected_template_ref:
        fail(f"{template_id} example_render_receipt.json template_or_asset_ref mismatch")
    expected_source_ref = f"repo-local:packs/medical-display-core/templates/{template_id}/example_input.json"
    if example_receipt.get("source_data_ref") != expected_source_ref:
        fail(f"{template_id} example_render_receipt.json source_data_ref mismatch")
    for key in ["semantic_match_ref", "transform_delta_ref", "degradation_reason"]:
        if not isinstance(example_receipt.get(key), str) or not example_receipt[key].strip():
            fail(f"{template_id} example_render_receipt.json must declare {key}")
    require_adaptation_provenance(
        example_receipt, f"{template_id} example_render_receipt.json"
    )
    return {
        "descriptor": descriptor,
        "example_input_ref": template_dir / "example_input.json",
        "example_render_receipt_ref": template_dir / "example_render_receipt.json",
    }


def verify_template_examples() -> dict:
    for template_id in EXPECTED_EXAMPLE_TEMPLATE_IDS:
        verify_one_template_example(template_id)
    return {"example_template_count": len(EXPECTED_EXAMPLE_TEMPLATE_IDS)}


def verify_golden_manifest() -> dict:
    manifest = read_json(PACK_ROOT / "golden_manifest.json")
    if manifest.get("manifest_id") != "fenggaolab.org.medical-display-core.reference_snapshot_golden.v1":
        fail("golden_manifest.json has wrong manifest_id")
    if manifest.get("pack_id") != "fenggaolab.org.medical-display-core":
        fail("golden_manifest.json pack_id mismatch")
    if manifest.get("state") != "active_reference_snapshot_golden":
        fail("golden_manifest.json state must be active_reference_snapshot_golden")
    if manifest.get("comparison_mode") != "reference_snapshot_hash_only":
        fail("golden_manifest.json comparison_mode must be reference_snapshot_hash_only")
    require_false_flags(
        manifest.get("authority_boundary") or {},
        "golden_manifest authority boundary",
        [
            "authority",
            "publication_ready",
            "can_write_domain_truth",
            "can_sign_owner_receipt",
            "can_create_typed_blocker",
            "can_claim_artifact_authority",
            "can_claim_live_render_regression",
            "can_claim_pixel_or_layout_regression",
        ],
    )

    live_candidate = manifest.get("live_regression_candidate") or {}
    if live_candidate.get("engine_ref") != LIVE_REGRESSION_ENGINE_REF:
        fail("golden_manifest live_regression_candidate engine_ref mismatch")
    if not (ROOT / LIVE_REGRESSION_ENGINE_REF).is_file():
        fail("golden_manifest live_regression_candidate engine is missing")
    if live_candidate.get("fixed_input_source") != "golden_templates[].example_input_ref":
        fail("golden_manifest live_regression_candidate fixed_input_source mismatch")
    if live_candidate.get("render_mode") != "candidate":
        fail("golden_manifest live_regression_candidate render_mode must be candidate")
    if live_candidate.get("execution_issue_field") != "execution_issue_candidate":
        fail("golden_manifest live_regression_candidate must use execution_issue_candidate")
    if live_candidate.get("fresh_run_required_for_ready_or_currentness_claim") is not True:
        fail("golden_manifest live_regression_candidate must require fresh ready/currentness evidence")
    require_false_flags(
        live_candidate,
        "golden_manifest live_regression_candidate",
        [
            "execution_issue_authority",
            "can_create_typed_blocker",
            "authority",
            "publication_ready",
        ],
    )

    snapshot_ref = manifest.get("shared_gallery_snapshot_ref") or {}
    pdf_ref = manifest.get("shared_gallery_pdf_ref") or {}
    if snapshot_ref.get("path") != "gallery/medical-display/gallery_snapshot.json":
        fail("golden_manifest shared_gallery_snapshot_ref path mismatch")
    if pdf_ref.get("path") != "gallery/medical-display/medical_display_gallery.pdf":
        fail("golden_manifest shared_gallery_pdf_ref path mismatch")
    if snapshot_ref.get("sha256") != sha256_file(ROOT / snapshot_ref["path"]):
        fail("golden_manifest shared_gallery_snapshot_ref sha256 mismatch")
    if pdf_ref.get("sha256") != sha256_file(ROOT / pdf_ref["path"]):
        fail("golden_manifest shared_gallery_pdf_ref sha256 mismatch")

    snapshot = read_json(GALLERY_ROOT / "gallery_snapshot.json")
    included_hashes = {item.get("path"): item.get("sha256") for item in snapshot.get("included_files") or []}
    if included_hashes.get("medical_display_gallery.pdf") != pdf_ref.get("sha256"):
        fail("golden_manifest pdf hash must match gallery_snapshot included_files")

    templates = manifest.get("golden_templates")
    if not isinstance(templates, list):
        fail("golden_manifest golden_templates must be a list")
    template_ids = [entry.get("template_id") for entry in templates]
    if template_ids != EXPECTED_GOLDEN_TEMPLATE_IDS:
        fail(f"golden_manifest template order mismatch: {template_ids}")

    for entry in templates:
        template_id = entry["template_id"]
        require_false_flags(entry, f"golden_manifest {template_id}", ["authority", "publication_ready"])
        if entry.get("comparison_mode") != "reference_snapshot_hash_only":
            fail(f"golden_manifest {template_id} comparison_mode mismatch")
        if entry.get("live_render_required_for_pixel_or_layout_regression") is not True:
            fail(f"golden_manifest {template_id} must require live render for pixel/layout regression")
        descriptor_path = PACK_ROOT / "templates" / template_id / "template.toml"
        if entry.get("descriptor_ref") != str(descriptor_path.relative_to(ROOT)):
            fail(f"golden_manifest {template_id} descriptor_ref mismatch")
        if entry.get("example_input_ref") != f"packs/medical-display-core/templates/{template_id}/example_input.json":
            fail(f"golden_manifest {template_id} example_input_ref mismatch")
        if entry.get("example_render_receipt_ref") != f"packs/medical-display-core/templates/{template_id}/example_render_receipt.json":
            fail(f"golden_manifest {template_id} example_render_receipt_ref mismatch")
        if entry.get("gallery_snapshot_ref") != "gallery/medical-display/gallery_snapshot.json":
            fail(f"golden_manifest {template_id} gallery_snapshot_ref mismatch")
        if entry.get("gallery_pdf_ref") != "gallery/medical-display/medical_display_gallery.pdf":
            fail(f"golden_manifest {template_id} gallery_pdf_ref mismatch")
        example = verify_one_template_example(template_id)
        descriptor = example["descriptor"]
        for key in ["kind", "renderer_family", "execution_mode"]:
            if entry.get(key) != descriptor.get(key):
                fail(f"golden_manifest {template_id} {key} mismatch")

    return {"golden_template_count": len(templates)}


def sync_opl_pack() -> None:
    display_pack = load_display_pack()
    opl_pack = load_opl_pack(display_pack)
    template_resources, _renderer_counts, _template_facts, _reference_facts = expected_template_resources(
        display_pack
    )
    generated = generated_opl_pack(opl_pack, template_resources)
    if opl_pack == generated:
        print("opl_pack.json already synchronized")
        return
    write_json(PACK_ROOT / "opl_pack.json", generated)
    print(f"opl_pack.json synchronized: {len(template_resources)} template resources")


def verify_gallery_review_package(
    template_facts: dict[str, dict],
    reference_facts: dict[str, dict],
) -> dict:
    manifest = read_json(GALLERY_ROOT / "gallery_manifest.json")
    snapshot = read_json(GALLERY_ROOT / "gallery_snapshot.json")
    verify_gallery_import_policy(manifest, "gallery_manifest.json", fail)
    verify_gallery_import_policy(snapshot, "gallery_snapshot.json", fail)
    if not str(snapshot.get("source_snapshot_ref") or "").startswith("repo-local:gallery/medical-display/"):
        fail("gallery_snapshot must use a repo-local source_snapshot_ref")
    if "not_self_referential" not in str(snapshot.get("source_commit_policy") or ""):
        fail("gallery_snapshot must not use a self-referential source commit")

    if manifest.get("status") != "rendered" or snapshot.get("status") != "rendered":
        fail("gallery manifest and snapshot must stay rendered")

    expected_ids = {
        category: {
            template_id
            for template_id, fact in template_facts.items()
            if fact["gallery_category"] == category
        }
        for category in ("evidence", "reporting_flow", "design", "table_shell")
    }
    canonical_counts = {
        "current_template_count": len(template_facts),
        "non_visual_canonical_template_count": len(expected_ids["table_shell"]),
        "paper_derived_reference_template_count": len(reference_facts),
    }
    for key, expected in canonical_counts.items():
        for container, label in (
            (manifest, "gallery_manifest"),
            (snapshot, "gallery_snapshot"),
        ):
            if container.get(key) != expected:
                fail(f"{label} {key} must be {expected}")

    category_specs = {
        "evidence": (
            "templates",
            "evidence_gallery_template_count",
            "evidence",
        ),
        "reporting_flow": (
            "reporting_flow_gallery_templates",
            "reporting_flow_gallery_template_count",
            "reporting_flow",
        ),
        "design": (
            "design_gallery_templates",
            "design_gallery_template_count",
            "design",
        ),
        "table_preview": (
            "table_preview_gallery_templates",
            "table_preview_gallery_template_count",
            "table_shell",
        ),
    }
    category_ids: dict[str, list[str]] = {}
    for category, (entries_key, count_key, expected_category) in category_specs.items():
        entries = manifest.get(entries_key)
        if not isinstance(entries, list):
            fail(f"gallery_manifest {entries_key} must be a list")
        ids: list[str] = []
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                fail(f"gallery_manifest {entries_key}[{index}] must be an object")
            template_id = entry.get("template_id")
            if not isinstance(template_id, str) or not template_id:
                fail(f"gallery_manifest {entries_key}[{index}] missing template_id")
            fact = template_facts.get(template_id)
            if fact is None:
                fail(f"{entries_key} contains non-canonical template {template_id}")
            expected_fields = {
                "kind": fact["kind"],
                "canonical_family_id": fact["family_id"],
                "canonical_family_title": fact["title"],
                "canonical_family_category": fact["category"],
                "renderer_family": fact["renderer_family"],
                "analysis_responsibility": fact["analysis_responsibility"],
                "medical_family_ids": fact["medical_family_ids"],
            }
            for field, expected in expected_fields.items():
                if entry.get(field) != expected:
                    fail(
                        f"{entries_key} {template_id} {field} must match "
                        "canonical template metadata"
                    )
            if entry.get("visual_gallery_visible") is not True:
                fail(f"{entries_key} {template_id} must be visual_gallery_visible")
            ids.append(template_id)
        if len(ids) != len(set(ids)):
            fail(f"gallery_manifest {entries_key} has duplicate template IDs")
        actual_ids = set(ids)
        expected_category_ids = expected_ids[expected_category]
        category_ids[category] = ids
        if category == "table_preview":
            extra = sorted(actual_ids - expected_category_ids)
            if extra:
                fail(f"table preview template IDs must be table_shell members: extra={extra}")
            if actual_ids != EXPECTED_TABLE_PREVIEW_TEMPLATE_IDS:
                fail(
                    "table preview template IDs must be exactly "
                    f"{sorted(EXPECTED_TABLE_PREVIEW_TEMPLATE_IDS)}"
                )
        elif actual_ids != expected_category_ids:
            missing = sorted(expected_category_ids - actual_ids)
            extra = sorted(actual_ids - expected_category_ids)
            fail(f"{entries_key} template IDs mismatch: missing={missing} extra={extra}")
        for container, label in (
            (manifest, "gallery_manifest"),
            (snapshot, "gallery_snapshot"),
        ):
            if container.get(count_key) != len(actual_ids):
                fail(f"{label} {count_key} must be {len(actual_ids)}")

    non_visual_entries = manifest.get("non_visual_inventory")
    if not isinstance(non_visual_entries, list):
        fail("gallery_manifest non_visual_inventory must be a list")
    non_visual_ids: list[str] = []
    non_visual_visible_ids: set[str] = set()
    for index, entry in enumerate(non_visual_entries):
        if not isinstance(entry, dict):
            fail(f"gallery_manifest non_visual_inventory[{index}] must be an object")
        template_id = entry.get("template_id")
        fact = template_facts.get(template_id)
        if fact is None or fact["gallery_category"] != "table_shell":
            fail(f"non_visual_inventory contains non-table-shell template {template_id}")
        expected_fields = {
            "kind": fact["kind"],
            "canonical_family_id": fact["family_id"],
            "canonical_family_title": fact["title"],
            "canonical_family_category": fact["category"],
            "renderer_family": fact["renderer_family"],
            "analysis_responsibility": fact["analysis_responsibility"],
            "medical_family_ids": fact["medical_family_ids"],
        }
        for field, expected in expected_fields.items():
            if entry.get(field) != expected:
                fail(
                    f"non_visual_inventory {template_id} {field} must match "
                    "canonical template metadata"
                )
        visible = entry.get("visual_gallery_visible")
        if not isinstance(visible, bool):
            fail(
                f"non_visual_inventory {template_id} visual_gallery_visible "
                "must be a boolean"
            )
        if visible:
            non_visual_visible_ids.add(template_id)
        non_visual_ids.append(template_id)
    if len(non_visual_ids) != len(set(non_visual_ids)):
        fail("gallery_manifest non_visual_inventory has duplicate template IDs")
    if set(non_visual_ids) != expected_ids["table_shell"]:
        missing = sorted(expected_ids["table_shell"] - set(non_visual_ids))
        extra = sorted(set(non_visual_ids) - expected_ids["table_shell"])
        fail(f"non_visual_inventory template IDs mismatch: missing={missing} extra={extra}")
    if non_visual_visible_ids != set(category_ids["table_preview"]):
        fail(
            "non_visual_inventory visual members must match table preview template IDs"
        )

    reference_entries = manifest.get("paper_derived_reference_inventory")
    if not isinstance(reference_entries, list):
        fail("gallery_manifest paper_derived_reference_inventory must be a list")
    reference_ids: list[str] = []
    for index, entry in enumerate(reference_entries):
        if not isinstance(entry, dict):
            fail(f"gallery_manifest paper_derived_reference_inventory[{index}] must be an object")
        template_id = entry.get("template_id")
        fact = reference_facts.get(template_id)
        if fact is None:
            fail(f"paper_derived_reference_inventory contains unknown reference {template_id}")
        if entry.get("resource_class") != "paper_derived_reference":
            fail(f"paper-derived reference {template_id} resource_class mismatch")
        if entry.get("migration_status") != "paper_derived_reference":
            fail(f"paper-derived reference {template_id} migration_status mismatch")
        if entry.get("default_visible") is not False:
            fail(f"paper-derived reference {template_id} must not be default visible")
        if entry.get("visual_gallery_visible") is not False:
            fail(f"paper-derived reference {template_id} must not be Gallery visible")
        if entry.get("paper_provenance_refs") != fact["paper_provenance_refs"]:
            fail(f"paper-derived reference {template_id} provenance mismatch")
        reference_ids.append(template_id)
    if set(reference_ids) != set(reference_facts) or len(reference_ids) != len(set(reference_ids)):
        fail("paper_derived_reference_inventory IDs must match source catalog references")

    all_gallery_ids = [
        template_id for ids in category_ids.values() for template_id in ids
    ]
    if len(all_gallery_ids) != len(set(all_gallery_ids)):
        fail("gallery template IDs must not appear in multiple categories")
    visual_count = len(all_gallery_ids)
    for container, label in (
        (manifest, "gallery_manifest"),
        (snapshot, "gallery_snapshot"),
    ):
        if container.get("visual_gallery_template_count") != visual_count:
            fail(f"{label} visual_gallery_template_count must be {visual_count}")
    responsibility_counts = dict(
        Counter(
            fact["analysis_responsibility"]
            for fact in template_facts.values()
        )
    )
    if manifest.get("analysis_responsibility_counts") != responsibility_counts:
        fail("gallery_manifest analysis_responsibility_counts mismatch")

    renderer_policy = manifest.get("renderer_policy_completion") or {}
    if snapshot.get("evidence_renderer_policy") != renderer_policy:
        fail("gallery manifest/snapshot renderer policy mismatch")
    evidence_count = len(category_ids["evidence"])
    default_visual_count = evidence_count + len(category_ids["reporting_flow"]) + len(
        category_ids["design"]
    )
    expected_renderer_policy_counts = {
        "current_template_count": len(template_facts),
        "current_evidence_template_count": evidence_count,
        "current_r_ggplot2_evidence_template_count": evidence_count,
        "current_python_evidence_template_count": 0,
        "default_visual_template_count": default_visual_count,
        "default_evidence_template_count": evidence_count,
        "default_r_ggplot2_evidence_template_count": evidence_count,
        "default_python_evidence_template_count": 0,
        "default_illustration_shell_count": len(category_ids["reporting_flow"])
        + len(category_ids["design"]),
        "all_evidence_template_count": evidence_count,
        "all_r_ggplot2_evidence_template_count": evidence_count,
        "python_evidence_template_count": 0,
        "python_evidence_retained_count": 0,
    }
    for key, expected in expected_renderer_policy_counts.items():
        if renderer_policy.get(key) != expected:
            fail(f"gallery renderer policy {key} must be {expected}")
    for key in (
        "python_evidence_template_ids",
        "python_only_evidence_family_ids_without_default_r_representative",
    ):
        if renderer_policy.get(key) != []:
            fail(f"gallery renderer policy {key} must stay empty")

    if manifest.get("composition_recipe_gallery_count") != snapshot.get(
        "composition_recipe_gallery_count"
    ):
        fail("gallery manifest/snapshot composition_recipe_gallery_count mismatch")
    if snapshot.get("publication_ready_claim_authorized") is not False:
        fail("gallery snapshot must not authorize publication-ready claims")
    require_false_flags(
        snapshot.get("authority_boundary") or {},
        "gallery_snapshot authority boundary",
        [
            "can_write_domain_truth",
            "can_sign_owner_receipt",
            "can_create_typed_blocker",
            "can_claim_publication_ready",
            "can_claim_artifact_authority",
        ],
    )

    required_files = {
        "medical_display_gallery.pdf",
        "gallery_manifest.json",
        "medical_display_gallery_reference.md",
        "display_pack_gallery_status.md",
        "display_pack_gallery_quality_audit.md",
    }
    included = snapshot.get("included_files")
    if not isinstance(included, list):
        fail("gallery_snapshot included_files must be a list")
    included_paths = {item.get("path") for item in included}
    for required in required_files:
        if required not in included_paths:
            fail(f"gallery_snapshot missing included file {required}")
    for item in included:
        path = GALLERY_ROOT / item["path"]
        actual = sha256_file(path)
        if actual != item.get("sha256"):
            fail(f"{path.relative_to(ROOT)} sha256 mismatch")

    for forbidden in [
        ROOT / "outputs" / "display-pack-gallery",
        GALLERY_ROOT / "medical_display_gallery_assets",
        GALLERY_ROOT / "render-cache",
    ]:
        if forbidden.exists():
            fail(f"forbidden intermediate output present: {forbidden.relative_to(ROOT)}")

    return {
        "visual_gallery_template_count": visual_count,
        "evidence_gallery_template_count": evidence_count,
        "included_file_count": len(included),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate and print a compact summary")
    parser.add_argument("--sync-opl-pack", action="store_true", help="rewrite opl_pack.json template resources from the catalog")
    args = parser.parse_args()
    if args.check == args.sync_opl_pack:
        parser.error("expected exactly one of --check or --sync-opl-pack")
    if args.sync_opl_pack:
        sync_opl_pack()
        return

    verify_receipt_templates()
    pack_summary = verify_source_pack()
    example_summary = verify_template_examples()
    gallery_summary = verify_gallery_review_package(
        pack_summary["template_facts"],
        pack_summary["reference_facts"],
    )
    golden_summary = verify_golden_manifest()
    print(
        "display gallery pack verify ok: "
        f"{pack_summary['catalog_template_count']} catalog templates, "
        f"{pack_summary['opl_template_resource_count']} opl template resources, "
        f"{pack_summary['paper_derived_reference_count']} paper-derived references, "
        f"renderer families {format_counts(pack_summary['renderer_counts'])}, "
        f"{example_summary['example_template_count']} template examples, "
        f"{golden_summary['golden_template_count']} reference-snapshot golden templates, "
        f"{gallery_summary['visual_gallery_template_count']} gallery visuals, "
        f"{gallery_summary['included_file_count']} review files"
    )


if __name__ == "__main__":
    main()
