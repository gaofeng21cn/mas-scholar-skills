"""Shared repository fixtures, loaders, and helpers for consistency pytest modules."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = str(ROOT / "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from gallery_policy import verify_gallery_import_policy  # noqa: E402


def fail(message: str) -> None:
    """Fail a repository consistency check with a clear pytest AssertionError."""
    raise AssertionError(f"verify failed: {message}")


def read_json(relative: str) -> Any:
    path = ROOT / relative
    if not path.is_file():
        fail(f"missing {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"missing {relative}")
    text = path.read_text(encoding="utf-8")
    if path.name == "SKILL.md":
        for reference in re.findall(r"\]\((references/[^)#]+\.md)(?:#[^)]*)?\)", text):
            target = (path.parent / reference).resolve()
            if not target.is_relative_to(path.parent.resolve()) or not target.is_file():
                fail(f"unresolved package-local Skill reference: {relative}: {reference}")
            text += "\n" + target.read_text(encoding="utf-8")
    return text


def sha256_file(relative: str) -> str:
    digest = hashlib.sha256()
    with (ROOT / relative).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_all(label: str, actual: Any, expected: Any) -> None:
    actual_set = set(actual or [])
    for item in expected:
        if item not in actual_set:
            fail(f"{label} missing {item}")


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


def validate_contract_json_schemas() -> list[str]:
    """Validate every JSON Schema file under contracts/ against Draft 2020-12."""
    checked: list[str] = []
    for schema_path in sorted((ROOT / "contracts").rglob("*.schema.json")):
        payload = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(payload)
        checked.append(schema_path.relative_to(ROOT).as_posix())
    return checked


@lru_cache(maxsize=1)
def load_repo_context() -> SimpleNamespace:
    """Load shared repository manifests, skill catalogs, and lookup indices."""
    contract = read_json("contracts/scholar-skills-capability-modules.json")
    contract_text = read_text("contracts/scholar-skills-capability-modules.json")
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
    domain_descriptor = read_json("contracts/domain_descriptor.json")
    capability_map = read_json("contracts/capability_map.json")
    package_manifest = read_json("contracts/opl_capability_package_manifest.json")
    reference_provider_profile = read_json(
        "contracts/reference-provider-adapters/scientific-metadata.json"
    )
    reference_provider_registry = read_json(
        "contracts/reference-provider-adapters/reference-provider-adapter-registry.json"
    )
    scientific_search_profile = read_json(
        "contracts/scientific-search-adapters/scientific-search.json"
    )
    scientific_search_registry = read_json(
        "contracts/scientific-search-adapters/scientific-search-adapter-registry.json"
    )
    gallery_manifest = read_json("gallery/medical-display/gallery_manifest.json")
    snapshot = read_json("gallery/medical-display/gallery_snapshot.json")

    classification_policy = contract.get("capability_module_classification_policy") or {}
    expected_capability_skills = (
        classification_policy.get("real_syncable_specialist_skills") or []
    )
    aggregate_skill_ids = ["mas-scholar-skills"]
    advanced_specialist_skill_ids = (
        classification_policy.get("optional_external_specialist_skills") or []
    )
    medical_method_specialist_skill_ids = (
        classification_policy.get("optional_medical_method_specialist_skills") or []
    )
    advanced_router_skill_ids = (
        classification_policy.get("optional_external_router_skill_ids") or []
    )
    medical_method_router_skill_ids = (
        classification_policy.get("optional_medical_method_router_skill_ids") or []
    )
    optional_router_skill_ids = [
        *advanced_router_skill_ids,
        *medical_method_router_skill_ids,
    ]
    optional_named_specialty_skill_ids = [
        *(classification_policy.get("optional_external_named_specialist_skills") or []),
        *(
            classification_policy.get("optional_medical_method_named_specialist_skills")
            or []
        ),
    ]
    advanced_redirect_tombstone_skill_ids = (
        classification_policy.get("optional_external_redirect_tombstone_skills") or []
    )
    medical_method_redirect_tombstone_skill_ids = (
        classification_policy.get("optional_medical_method_redirect_tombstone_skills")
        or []
    )
    redirect_tombstone_skill_ids = [
        *advanced_redirect_tombstone_skill_ids,
        *medical_method_redirect_tombstone_skill_ids,
    ]
    expected_optional_skill_ids = [
        *optional_router_skill_ids,
        *optional_named_specialty_skill_ids,
    ]
    expected_discoverable_skill_ids = [
        *aggregate_skill_ids,
        *expected_capability_skills,
        *expected_optional_skill_ids,
    ]
    expected_all_skill_ids = expected_discoverable_skill_ids
    expected_default_exposure_skill_ids = ["mas-scholar-skills"]

    mag_required_skill_ids = [
        "medical-research-lit",
        "medical-statistical-review",
        "medical-methodology-planner",
        "medical-evidence-integrity-reviewer",
        "medical-evidence-synthesis-and-claim-map",
        "medical-reference-integrity-auditor",
    ]
    runtime_module_id = "mas-scholar-skills.reference-provider-adapters"
    search_runtime_module_id = "mas-scholar-skills.scientific-search-adapters"
    runtime_module_ids = [runtime_module_id, search_runtime_module_id]

    package_exports = package_manifest.get("exports") or {}
    runtime_bindings = package_exports.get("runtime_module_bindings") or []
    runtime_binding = runtime_bindings[0] if len(runtime_bindings) > 0 else {}
    search_runtime_binding = runtime_bindings[1] if len(runtime_bindings) > 1 else {}

    capability_skill_texts = {
        skill_id: read_text(f"skills/{skill_id}/SKILL.md")
        for skill_id in expected_capability_skills
    }
    advanced_specialist_skills = {
        skill_id: read_text(f"skills/{skill_id}/SKILL.md")
        for skill_id in advanced_specialist_skill_ids
    }
    medical_method_specialist_skills = {
        skill_id: read_text(f"skills/{skill_id}/SKILL.md")
        for skill_id in medical_method_specialist_skill_ids
    }
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

    modules = contract.get("modules") or []
    modules_by_id = {item.get("module_id"): item for item in modules}
    capabilities = capability_map.get("capabilities") or []
    capability_by_id = {item.get("capability_id"): item for item in capabilities}
    advanced_policy = contract.get("advanced_specialist_pack_policy") or {}
    advanced_policy_by_id = {
        item.get("skill_id"): item
        for item in (advanced_policy.get("specialists") or [])
    }
    advanced_capability_by_id = {
        item.get("skill_id"): item
        for item in capability_map.get("optional_specialist_skills", [])
    }
    method_policy = contract.get("medical_method_specialist_pack_policy") or {}
    method_policy_by_id = {
        item.get("skill_id"): item
        for item in (method_policy.get("specialists") or [])
    }

    profile_adapter_ids = (
        reference_provider_profile.get("adapter_package") or {}
    ).get("adapter_ids") or []
    search_profile_adapter_ids = (
        scientific_search_profile.get("adapter_package") or {}
    ).get("adapter_ids") or []

    return SimpleNamespace(
        root=ROOT,
        contract=contract,
        contract_text=contract_text,
        page_hash_evidence_schema=page_hash_evidence_schema,
        initial_draft_preflight_schema=initial_draft_preflight_schema,
        display_receipt_templates=display_receipt_templates,
        professional_figure_workflow_schema=professional_figure_workflow_schema,
        layout_qc_fixture=layout_qc_fixture,
        semantic_artist_flow_fixture=semantic_artist_flow_fixture,
        revision_learning_fixture_refs=revision_learning_fixture_refs,
        domain_descriptor=domain_descriptor,
        capability_map=capability_map,
        package_manifest=package_manifest,
        package_exports=package_exports,
        reference_provider_profile=reference_provider_profile,
        reference_provider_registry=reference_provider_registry,
        scientific_search_profile=scientific_search_profile,
        scientific_search_registry=scientific_search_registry,
        gallery_manifest=gallery_manifest,
        snapshot=snapshot,
        classification_policy=classification_policy,
        capability_pack_consumption=contract.get("capability_pack_consumption_policy")
        or {},
        descriptor_pack=domain_descriptor.get("capability_pack") or {},
        expected_capability_skills=expected_capability_skills,
        aggregate_skill_ids=aggregate_skill_ids,
        advanced_router_skill_ids=advanced_router_skill_ids,
        medical_method_router_skill_ids=medical_method_router_skill_ids,
        optional_router_skill_ids=optional_router_skill_ids,
        advanced_specialist_skill_ids=advanced_specialist_skill_ids,
        medical_method_specialist_skill_ids=medical_method_specialist_skill_ids,
        optional_named_specialty_skill_ids=optional_named_specialty_skill_ids,
        advanced_redirect_tombstone_skill_ids=advanced_redirect_tombstone_skill_ids,
        medical_method_redirect_tombstone_skill_ids=medical_method_redirect_tombstone_skill_ids,
        redirect_tombstone_skill_ids=redirect_tombstone_skill_ids,
        expected_optional_skill_ids=expected_optional_skill_ids,
        expected_discoverable_skill_ids=expected_discoverable_skill_ids,
        expected_all_skill_ids=expected_all_skill_ids,
        expected_default_exposure_skill_ids=expected_default_exposure_skill_ids,
        mag_required_skill_ids=mag_required_skill_ids,
        runtime_module_id=runtime_module_id,
        search_runtime_module_id=search_runtime_module_id,
        runtime_module_ids=runtime_module_ids,
        runtime_binding=runtime_binding,
        search_runtime_binding=search_runtime_binding,
        profile_adapter_ids=profile_adapter_ids,
        search_profile_adapter_ids=search_profile_adapter_ids,
        capability_skill_texts=capability_skill_texts,
        advanced_specialist_skills=advanced_specialist_skills,
        medical_method_specialist_skills=medical_method_specialist_skills,
        first_draft_quality_sources=first_draft_quality_sources,
        write_skill=capability_skill_texts["medical-manuscript-writing"],
        review_skill=capability_skill_texts["medical-manuscript-review"],
        figure_skill=capability_skill_texts["medical-figure-design"],
        figure_style_skill=capability_skill_texts["medical-figure-style"],
        figure_composer_skill=capability_skill_texts["medical-figure-composer"],
        lit_skill=capability_skill_texts["medical-research-lit"],
        stats_skill=capability_skill_texts["medical-statistical-review"],
        table_skill=capability_skill_texts["medical-table-design"],
        submit_skill=capability_skill_texts["medical-submission-prep"],
        data_governance_skill=capability_skill_texts["medical-data-governance"],
        cohort_phenotyping_skill=read_text("skills/medical-cohort-phenotyping/SKILL.md"),
        methodology_planner_skill=read_text("skills/medical-methodology-planner/SKILL.md"),
        display_qc_skill=medical_method_specialist_skills["medical-display-qc"],
        reference_integrity_skill=medical_method_specialist_skills[
            "medical-reference-integrity-auditor"
        ],
        display_qc_kernel=read_text("skills/medical-display-qc/kernel.py"),
        modules=modules,
        modules_by_id=modules_by_id,
        display_module=modules_by_id.get("mas-scholar-skills.display") or {},
        stats_module=modules_by_id.get("mas-scholar-skills.stats") or {},
        display_quality_floor=(
            (modules_by_id.get("mas-scholar-skills.display") or {}).get(
                "display_quality_floor_policy"
            )
            or {}
        ),
        capability_by_id=capability_by_id,
        advanced_policy=advanced_policy,
        advanced_policy_by_id=advanced_policy_by_id,
        advanced_capability_by_id=advanced_capability_by_id,
        method_policy=method_policy,
        method_policy_by_id=method_policy_by_id,
        workflow_template=display_receipt_templates.get(
            "professional_figure_workflow_ref"
        )
        or {},
        owner_closeout_boundary=capability_map.get("owner_closeout_boundary") or {},
        failure_token_registry_ref="opl-framework:contracts/opl-framework/agent-lab-failure-token-registry.json",
        expected_capability_token_policy={
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
        },
    )


__all__ = [
    "ROOT",
    "fail",
    "load_repo_context",
    "read_json",
    "read_text",
    "require_all",
    "require_unversioned_v1_binding",
    "sha256_file",
    "validate_contract_json_schemas",
    "verify_gallery_import_policy",
]
