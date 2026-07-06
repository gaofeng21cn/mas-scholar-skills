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


def verify_source_pack() -> dict:
    display_pack = read_toml(PACK_ROOT / "display_pack.toml")
    if display_pack.get("pack_id") != "fenggaolab.org.medical-display-core":
        fail("display_pack.toml has wrong pack_id")
    if display_pack.get("pack_kind") != "display_pack":
        fail("display_pack.toml must declare pack_kind=display_pack")
    if display_pack.get("capability_kind") != "reference_pack":
        fail("display_pack.toml must declare capability_kind=reference_pack")
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
    opl_pack = read_json(PACK_ROOT / "opl_pack.json")
    if opl_pack.get("pack_id") != display_pack["pack_id"]:
        fail("opl_pack.json pack_id does not match display_pack.toml")
    if opl_pack.get("pack_kind") != "display_pack":
        fail("opl_pack.json must declare display_pack kind")
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

    catalog = read_json(PACK_ROOT / "canonical_template_catalog.json")
    if catalog.get("pack_id") != display_pack["pack_id"]:
        fail("canonical_template_catalog.json pack_id does not match display_pack.toml")
    families = catalog.get("families")
    if not isinstance(families, list) or not families:
        fail("canonical_template_catalog.json must contain template families")

    seen_template_ids: set[str] = set()
    renderer_counts: dict[str, int] = {}
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
            if descriptor.get("supported_render_modes") != ["final", "candidate"]:
                fail(f"{template_id} must declare supported_render_modes final/candidate")
            expected_entrypoint = f"Rscript ../../render.R --template {template_id} --mode {{render_mode}} --request {{request_json}}"
            if descriptor.get("entrypoint") != expected_entrypoint:
                fail(f"{template_id} must use the pack-level render.R entrypoint")

    for required in [
        "opl_pack.json",
        "render.R",
        "renderer_dependency_profile.json",
        "renderer_migration_ledger.json",
        "rlib/medicaldisplaycore/evidence_renderer.R",
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
        "catalog_family_count": len(families),
        "renderer_counts": renderer_counts,
    }


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
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    pack_summary = verify_source_pack()
    gallery_summary = verify_gallery_review_package()
    print(
        "display gallery pack verify ok: "
        f"{pack_summary['catalog_family_count']} catalog families, "
        f"{gallery_summary['visual_gallery_template_count']} gallery visuals, "
        f"{gallery_summary['included_file_count']} review files"
    )


if __name__ == "__main__":
    main()
