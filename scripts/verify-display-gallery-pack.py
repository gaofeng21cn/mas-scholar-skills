#!/usr/bin/env python3
"""Validate the ScholarSkills medical-display source pack and review gallery."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import tomllib


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
ALLOWED_ADAPTATION_MODES = [
    "declared_template",
    "schema_adapted_template",
    "reference_guided_new_render",
    "original_new_render",
]
NOT_APPLICABLE_NEW_RENDER_REF = "not_applicable:new_render"
ORIGINAL_NEW_RENDER_MODE = "original_new_render"
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


def verify_receipt_templates() -> dict:
    contract = read_json(ROOT / "contracts" / "display-pack-receipt-templates.json")
    if contract.get("contract_id") != "mas_scholar_skills_display_pack_receipt_templates":
        fail("display-pack receipt templates contract has wrong contract_id")
    if contract.get("schema_version") != "1.2.0":
        fail("display-pack receipt templates contract must use schema_version 1.2.0")
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
        "figure_contract_ref",
        "render_receipt_ref",
        "visual_qa_receipt_ref",
        "owner_gate_handoff_ref",
    ]:
        fail("display-pack receipt chain must remain figure->render->visual_qa->owner_gate")
    adaptation_policy = contract.get("template_asset_adaptation_policy") or {}
    if adaptation_policy.get("allowed_adaptation_modes") != ALLOWED_ADAPTATION_MODES:
        fail("template/asset adaptation policy has invalid adaptation modes")
    if adaptation_policy.get("not_applicable_new_render_mapping") != {
        "template_or_asset_ref": NOT_APPLICABLE_NEW_RENDER_REF,
        "adaptation_mode": ORIGINAL_NEW_RENDER_MODE,
        "semantic_match_ref": "not_applicable:no_reusable_source",
        "transform_delta_ref": "not_applicable:no_reusable_source",
        "forbids_invented_reference_provenance": True,
    }:
        fail("template/asset adaptation policy must map no-source renders without invented provenance")
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
            "template_selection_ref",
            "renderer_decision_ref",
            "owner_gate_handoff_ref",
        ],
    )
    render_receipt = contract.get("render_receipt_ref") or {}
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
    visual_qa_receipt = contract.get("visual_qa_receipt_ref") or {}
    require_all_fields(
        visual_qa_receipt,
        "visual_qa_receipt_ref",
        [
            "render_receipt_ref",
            "final_size_export_ref",
            "export_lint_ref",
            "route_back_items",
            "owner_gate_handoff_ref",
            "authority",
            "publication_ready",
        ],
    )
    require_false_flags(visual_qa_receipt, "visual_qa_receipt_ref", ["authority", "publication_ready"])
    return {"receipt_contract_id": contract["contract_id"]}


def require_review_policy(container: dict, label: str) -> None:
    policy = container.get("opl_scholarskills_import_policy") or {}
    if policy.get("policy_id") != "opl_scholarskills_display_gallery_refs_only_source_manifest.v1":
        fail(f"{label} missing ScholarSkills gallery refs-only policy")
    if policy.get("import_role") != "pack_native_human_review_ref_and_source_snapshot":
        fail(f"{label} must be a pack-native human review snapshot")
    if policy.get("source_repo") != "mas-scholar-skills":
        fail(f"{label} source_repo must be mas-scholar-skills")
    if policy.get("source_authority") != "opl_scholarskills_display_pack_review_surface":
        fail(f"{label} source_authority must be the ScholarSkills display review surface")
    if not str(policy.get("source_snapshot_ref") or "").startswith("repo-local:gallery/medical-display/"):
        fail(f"{label} must use a repo-local gallery source_snapshot_ref")
    if "not_self_referential" not in str(policy.get("source_commit_policy") or ""):
        fail(f"{label} must not use a self-referential source commit")
    if policy.get("no_second_truth") is not True:
        fail(f"{label} policy must forbid second truth")
    require_false_flags(
        policy.get("authority_boundary") or {},
        f"{label} review policy authority boundary",
        [
            "can_write_domain_truth",
            "can_sign_owner_receipt",
            "can_create_typed_blocker",
            "can_claim_publication_ready",
            "can_claim_artifact_authority",
        ],
    )
    forbidden = set(policy.get("forbidden_uses") or [])
    for item in [
        "mas_display_truth",
        "publication_ready_claim",
        "owner_receipt",
        "typed_blocker",
        "artifact_authority",
        "runtime_or_package_authority",
    ]:
        if item not in forbidden:
            fail(f"{label} review policy must forbid {item}")


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


def expected_template_resources(display_pack: dict) -> tuple[list[dict], dict[str, int]]:
    catalog = read_json(PACK_ROOT / "canonical_template_catalog.json")
    if catalog.get("pack_id") != display_pack["pack_id"]:
        fail("canonical_template_catalog.json pack_id does not match display_pack.toml")
    families = catalog.get("families")
    if not isinstance(families, list) or not families:
        fail("canonical_template_catalog.json must contain template families")

    seen_template_ids: set[str] = set()
    renderer_counts: dict[str, int] = {}
    template_resources: list[dict] = []
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

    descriptor_template_ids = {
        path.parent.name for path in (PACK_ROOT / "templates").glob("*/template.toml")
    }
    if descriptor_template_ids != seen_template_ids:
        missing = sorted(seen_template_ids - descriptor_template_ids)
        extra = sorted(descriptor_template_ids - seen_template_ids)
        fail(f"template descriptor/catalog mismatch: missing={missing} extra={extra}")

    return template_resources, renderer_counts


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
    template_resources, renderer_counts = expected_template_resources(display_pack)
    generated = generated_opl_pack(opl_pack, template_resources)
    if opl_pack != generated:
        fail("opl_pack.json template resources drifted; run scripts/verify-display-gallery-pack.py --sync-opl-pack")

    seen_template_ids = {resource["resource_id"].removeprefix("template.") for resource in template_resources}
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
    if opl_template_ids != seen_template_ids:
        missing = sorted(seen_template_ids - opl_template_ids)
        extra = sorted(opl_template_ids - seen_template_ids)
        fail(f"opl_pack.json template resources/catalog mismatch: missing={missing} extra={extra}")

    for required in [
        "opl_pack.json",
        "golden_manifest.json",
        "render.R",
        "renderer_dependency_profile.json",
        "renderer_migration_ledger.json",
        "rlib/medicaldisplaycore/evidence_renderer.R",
        "rlib/medicaldisplaycore/evidence_renderer_parts/data_frames.R",
        "rlib/medicaldisplaycore/evidence_renderer_parts/layouts.R",
        "rlib/medicaldisplaycore/evidence_renderer_parts/style.R",
        "rlib/medicaldisplaycore/candidate_renderer.R",
        "src/fenggaolab_org_medical_display_core/__init__.py",
    ]:
        if not (PACK_ROOT / required).is_file():
            fail(f"missing source pack file packs/medical-display-core/{required}")

    for pattern in ["*.png", "*.svg", "*.html", "*.layout.json", "*render_cache*"]:
        matches = list(PACK_ROOT.rglob(pattern))
        if matches:
            fail(f"source pack contains generated artifact {matches[0].relative_to(ROOT)}")

    return {
        "catalog_template_count": len(seen_template_ids),
        "opl_template_resource_count": len(opl_template_ids),
        "renderer_counts": renderer_counts,
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
    adaptation_mode = example_receipt.get("adaptation_mode")
    if adaptation_mode not in ALLOWED_ADAPTATION_MODES:
        fail(f"{template_id} example_render_receipt.json has invalid adaptation_mode")
    if (template_or_asset_ref == NOT_APPLICABLE_NEW_RENDER_REF) != (
        adaptation_mode == ORIGINAL_NEW_RENDER_MODE
    ):
        fail(
            f"{template_id} example_render_receipt.json must pair "
            "not_applicable:new_render with original_new_render"
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
    template_resources, _renderer_counts = expected_template_resources(display_pack)
    generated = generated_opl_pack(opl_pack, template_resources)
    if opl_pack == generated:
        print("opl_pack.json already synchronized")
        return
    write_json(PACK_ROOT / "opl_pack.json", generated)
    print(f"opl_pack.json synchronized: {len(template_resources)} template resources")


def verify_gallery_review_package() -> dict:
    manifest = read_json(GALLERY_ROOT / "gallery_manifest.json")
    snapshot = read_json(GALLERY_ROOT / "gallery_snapshot.json")
    require_review_policy(manifest, "gallery_manifest.json")
    require_review_policy(snapshot, "gallery_snapshot.json")
    if not str(snapshot.get("source_snapshot_ref") or "").startswith("repo-local:gallery/medical-display/"):
        fail("gallery_snapshot must use a repo-local source_snapshot_ref")
    if "not_self_referential" not in str(snapshot.get("source_commit_policy") or ""):
        fail("gallery_snapshot must not use a self-referential source commit")

    if manifest.get("status") != "rendered" or snapshot.get("status") != "rendered":
        fail("gallery manifest and snapshot must stay rendered")
    for key in [
        "visual_gallery_template_count",
        "evidence_gallery_template_count",
        "composition_recipe_gallery_count",
    ]:
        if manifest.get(key) != snapshot.get(key):
            fail(f"gallery manifest/snapshot {key} mismatch")
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
        "visual_gallery_template_count": snapshot["visual_gallery_template_count"],
        "evidence_gallery_template_count": snapshot["evidence_gallery_template_count"],
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
    gallery_summary = verify_gallery_review_package()
    golden_summary = verify_golden_manifest()
    print(
        "display gallery pack verify ok: "
        f"{pack_summary['catalog_template_count']} catalog templates, "
        f"{pack_summary['opl_template_resource_count']} opl template resources, "
        f"renderer families {format_counts(pack_summary['renderer_counts'])}, "
        f"{example_summary['example_template_count']} template examples, "
        f"{golden_summary['golden_template_count']} reference-snapshot golden templates, "
        f"{gallery_summary['visual_gallery_template_count']} gallery visuals, "
        f"{gallery_summary['included_file_count']} review files"
    )


if __name__ == "__main__":
    main()
