"""Shared verifier for the committed Gallery import/no-authority policy."""

from __future__ import annotations

from collections.abc import Callable


REQUIRED_ALLOWED_USES = {"gallery_review_ref", "source_manifest_ref", "quality_floor_ref"}
REQUIRED_FORBIDDEN_USES = {
    "mas_display_truth",
    "publication_ready_claim",
    "owner_receipt",
    "typed_blocker",
    "artifact_authority",
    "runtime_or_package_authority",
}
REQUIRED_FALSE_AUTHORITY_FLAGS = {
    "can_write_domain_truth",
    "can_sign_owner_receipt",
    "can_create_typed_blocker",
    "can_claim_publication_ready",
    "can_claim_artifact_authority",
}


def verify_gallery_import_policy(
    container: dict,
    label: str,
    fail: Callable[[str], None],
) -> None:
    policy = container.get("opl_scholarskills_import_policy") or {}
    expected = {
        "policy_id": "opl_scholarskills_display_gallery_refs_only_source_manifest.v1",
        "import_role": "pack_native_human_review_ref_and_source_snapshot",
        "source_repo": "mas-scholar-skills",
        "source_authority": "opl_scholarskills_display_pack_review_surface",
        "no_second_truth": True,
    }
    for field, value in expected.items():
        if policy.get(field) != value:
            fail(f"{label} gallery import policy requires {field}={value!r}")
    if not str(policy.get("source_snapshot_ref") or "").startswith(
        "repo-local:gallery/medical-display/"
    ):
        fail(f"{label} gallery import policy must use a repo-local source_snapshot_ref")
    if "not_self_referential" not in str(policy.get("source_commit_policy") or ""):
        fail(f"{label} gallery import policy must not use a self-referential source commit")
    missing_allowed = REQUIRED_ALLOWED_USES - set(policy.get("allowed_uses") or [])
    if missing_allowed:
        fail(f"{label} gallery import policy missing allowed uses: {sorted(missing_allowed)}")
    missing_forbidden = REQUIRED_FORBIDDEN_USES - set(policy.get("forbidden_uses") or [])
    if missing_forbidden:
        fail(f"{label} gallery import policy missing forbidden uses: {sorted(missing_forbidden)}")
    boundary = policy.get("authority_boundary") or {}
    for field in REQUIRED_FALSE_AUTHORITY_FLAGS:
        if boundary.get(field) is not False:
            fail(f"{label} gallery import authority flag {field} must be false")
