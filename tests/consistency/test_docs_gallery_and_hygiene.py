"""Documentation no-authority boundaries, gallery snapshot checksums, and .gitignore hygiene."""

from __future__ import annotations

from tests.consistency._context import (
    fail,
    load_repo_context,
    read_text,
    sha256_file,
)
def test_docs_and_no_authority_boundaries() -> None:
    ctx = load_repo_context()
    advanced_redirect_tombstone_skill_ids = ctx.advanced_redirect_tombstone_skill_ids
    advanced_specialist_skill_ids = ctx.advanced_specialist_skill_ids
    capability_map = ctx.capability_map
    classification_policy = ctx.classification_policy
    domain_descriptor = ctx.domain_descriptor
    expected_capability_skills = ctx.expected_capability_skills
    medical_method_redirect_tombstone_skill_ids = ctx.medical_method_redirect_tombstone_skill_ids
    medical_method_specialist_skill_ids = ctx.medical_method_specialist_skill_ids
    optional_named_specialty_skill_ids = ctx.optional_named_specialty_skill_ids
    root = ctx.root
    runtime_module_ids = ctx.runtime_module_ids
    read_text("README.md")
    read_text("README.zh-CN.md")
    read_text("docs/README.md")
    read_text("docs/mas-scholar-skills-operating-model.md")
    read_text("docs/capability-modules.md")
    read_text("references/professional-quality-ref-templates.md")

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
    {
        item.get("capability_id"): item
        for item in capability_map.get("capabilities", [])
    }
    failure_token_registry_ref = "opl-framework:contracts/opl-framework/agent-lab-failure-token-registry.json"
    if capability_map.get("failure_token_registry_ref") != failure_token_registry_ref:
        fail("capability map must point to the OPL failure token registry ref")
    owner_closeout_boundary = capability_map.get("owner_closeout_boundary") or {}
    if owner_closeout_boundary.get("boundary_kind") != "refs_only_no_authority_owner_closeout":
        fail("capability map must expose refs-only no-authority owner closeout boundary")

def test_gallery_snapshot_checksums_and_gitignore() -> None:
    ctx = load_repo_context()
    root = ctx.root
    snapshot = ctx.snapshot
    if snapshot.get("publication_ready_claim_authorized") is not False:
        fail("snapshot must not authorize publication-ready claims")
    read_text("gallery/medical-display/display_pack_gallery_quality_audit.md")

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
