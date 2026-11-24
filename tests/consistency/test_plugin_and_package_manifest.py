"""Plugin metadata, JSON Schema Draft 2020-12 checks, capability package manifest, and runtime adapters."""

from __future__ import annotations

import re
import subprocess
from urllib.parse import urlparse

from tests.consistency._context import (
    fail,
    load_repo_context,
    read_json,
    read_text,
    require_all,
    validate_contract_json_schemas,
)
def test_all_contract_json_schemas_valid_draft_2020_12() -> None:
    checked = validate_contract_json_schemas()
    assert checked, "expected at least one JSON Schema under contracts/"


def test_shared_kernel_validation_module_is_content_locked() -> None:
    ctx = load_repo_context()
    locked = (ctx.package_manifest.get("content_lock") or {}).get("paths") or []
    assert "runtime/kernel_validation/__init__.py" in locked


def test_plugin_manifest_metadata() -> None:
    manifest = read_json(".codex-plugin/plugin.json")
    if manifest.get("name") != "mas-scholar-skills":
        fail("plugin name must be mas-scholar-skills")
    if manifest.get("version") != "0.2.32":
        fail("plugin version must be 0.2.32")
    if manifest.get("skills") != "./skills/":
        fail("plugin skills path must be ./skills/")
    if manifest.get("interface", {}).get("displayName") != "MAS Scholar Skills":
        fail("plugin displayName must be MAS Scholar Skills")
    default_prompts = manifest.get("interface", {}).get("defaultPrompt") or []
    if (
        not default_prompts
        or len(default_prompts) > 3
        or any(not isinstance(prompt, str) or len(prompt) > 128 for prompt in default_prompts)
    ):
        fail("plugin defaultPrompt entries must be non-empty strings of at most 128 characters")

def test_package_manifest_content_lock_and_runtime_adapters() -> None:
    ctx = load_repo_context()
    contract = ctx.contract
    expected_all_skill_ids = ctx.expected_all_skill_ids
    package_exports = ctx.package_exports
    package_manifest = ctx.package_manifest
    reference_provider_profile = ctx.reference_provider_profile
    reference_provider_registry = ctx.reference_provider_registry
    root = ctx.root
    scientific_search_profile = ctx.scientific_search_profile
    scientific_search_registry = ctx.scientific_search_registry
    profile_policy = contract.get("consumer_profile_policy") or {}
    if profile_policy.get("profile_source_ref") != "contracts/opl_capability_package_manifest.json#/consumer_profiles":
        fail("capability catalog must reference the canonical consumer profiles")
    for key in [
        "all_profiles_are_required_dependencies",
        "global_core_and_specialty_classification_is_not_consumer_readiness",
        "required_ids_are_selected_profile_capability_sets_not_domain_quality_floors",
        "required_profile_defines_consumer_dependency_gates_not_domain_readiness",
        "consumer_stage_overlay_required",
        "outputs_are_refs_only_candidates",
        "consuming_domain_owner_retains_authority",
        "consumer_missing_or_incompatible_fail_closed",
        "consumer_may_bundle_or_materialize_as_carrier_projection",
    ]:
        if profile_policy.get(key) is not True:
            fail(f"capability catalog consumer profile policy {key} must be true")
    runtime_module_id = "mas-scholar-skills.reference-provider-adapters"
    search_runtime_module_id = "mas-scholar-skills.scientific-search-adapters"
    runtime_module_ids = [runtime_module_id, search_runtime_module_id]
    runtime_bindings = package_exports.get("runtime_module_bindings") or []
    if [binding.get("module_id") for binding in runtime_bindings] != runtime_module_ids:
        fail("capability package must export the reference verification and scientific search runtime bindings in canonical order")
    runtime_binding = runtime_bindings[0]
    search_runtime_binding = runtime_bindings[1]
    expected_runtime_handler = {
        "kind": "typescript_export",
        "file": "runtime/reference-provider-adapters/index.ts",
        "export": "runReferenceProviderAdapterStep",
    }
    if runtime_binding.get("module_id") != runtime_module_id:
        fail("runtime binding must use the canonical reference-provider adapter module id")
    if runtime_binding.get("module_kind") != "opl_connect_reference_provider_adapter":
        fail("runtime binding must declare the OPL Connect reference-provider adapter kind")
    if runtime_binding.get("adapter_abi") != "opl-connect-reference-provider-adapter.v1":
        fail("runtime binding must use the v1 reference-provider adapter ABI")
    if runtime_binding.get("handler") != expected_runtime_handler:
        fail("runtime binding must expose the canonical TypeScript handler")
    if runtime_binding.get("max_steps") != 2:
        fail("runtime binding must cap all provider state machines at two steps")
    if runtime_binding.get("exports") != [
        "runReferenceProviderAdapterStep",
        "build_request",
        "parse_response",
        "next_step",
    ]:
        fail("runtime binding must expose handler and three state-machine operations")
    expected_runtime_sandbox = {
        "network_io": False,
        "environment_read": False,
        "filesystem_read": False,
        "filesystem_write": False,
        "process_spawn": False,
        "dynamic_module_load": False,
        "input_output_policy": "serializable_request_state_response_only",
    }
    if runtime_binding.get("sandbox") != expected_runtime_sandbox:
        fail("reference-provider runtime binding sandbox must forbid direct I/O and process access")
    if any(value is not False for value in (runtime_binding.get("authority_boundary") or {}).values()):
        fail("reference-provider runtime binding authority flags must all be false")
    expected_search_runtime_handler = {
        "kind": "typescript_export",
        "file": "runtime/scientific-search-adapters/index.ts",
        "export": "runScientificSearchAdapterStep",
    }
    if search_runtime_binding.get("module_kind") != "opl_connect_scientific_search_adapter":
        fail("scientific search binding must declare the OPL Connect search adapter kind")
    if search_runtime_binding.get("adapter_abi") != "opl-connect-scientific-search-adapter.v1":
        fail("scientific search binding must use the v1 search adapter ABI")
    if search_runtime_binding.get("handler") != expected_search_runtime_handler:
        fail("scientific search binding must expose the canonical TypeScript handler")
    if search_runtime_binding.get("max_steps") != 2:
        fail("scientific search binding must cap every provider search at two HTTP steps")
    if search_runtime_binding.get("exports") != [
        "runScientificSearchAdapterStep",
        "build_search_request",
        "parse_search_response",
    ]:
        fail("scientific search binding must expose its handler and two state-machine operations")
    if search_runtime_binding.get("sandbox") != expected_runtime_sandbox:
        fail("scientific search runtime binding sandbox must forbid direct I/O and process access")
    if any(value is not False for value in (search_runtime_binding.get("authority_boundary") or {}).values()):
        fail("scientific search runtime binding authority flags must all be false")
    if package_manifest.get("exports", {}).get("runtime_module_bindings") != runtime_bindings:
        fail("capability package manifest must own the runtime module bindings")
    runtime_contract_paths = [
        "contracts/reference-provider-adapters/scientific-metadata.json",
        "contracts/reference-provider-adapters/reference-provider-profile.schema.json",
        "contracts/reference-provider-adapters/reference-provider-adapter-registry.json",
        "contracts/reference-provider-adapters/reference-provider-adapter-registry.schema.json",
        "contracts/reference-provider-adapters/reference-provider-adapter-step.schema.json",
    ]
    runtime_source_paths = runtime_binding.get("contained_implementation_files") or []
    if runtime_source_paths != reference_provider_registry.get("contained_implementation_files"):
        fail("manifest and adapter registry must lock the same implementation files")
    search_runtime_contract_paths = [
        "contracts/scientific-search-adapters/scientific-search.json",
        "contracts/scientific-search-adapters/scientific-search-provider-profile.schema.json",
        "contracts/scientific-search-adapters/scientific-search-adapter-registry.json",
        "contracts/scientific-search-adapters/scientific-search-adapter-registry.schema.json",
        "contracts/scientific-search-adapters/scientific-search-adapter-step.schema.json",
    ]
    search_runtime_source_paths = search_runtime_binding.get("contained_implementation_files") or []
    if search_runtime_source_paths != scientific_search_registry.get("contained_implementation_files"):
        fail("manifest and scientific search registry must lock the same implementation files")
    all_runtime_contract_paths = [*runtime_contract_paths, *search_runtime_contract_paths]
    all_runtime_source_paths = list(dict.fromkeys([*runtime_source_paths, *search_runtime_source_paths]))
    for relative in [*all_runtime_contract_paths, *all_runtime_source_paths]:
        if not (root / relative).is_file():
            fail(f"package runtime source is missing: {relative}")
    content_lock = package_manifest.get("content_lock") or {}
    if content_lock.get("algorithm") != "sha256":
        fail("capability package content lock must use sha256")
    if content_lock.get("canonicalization") != "ordered_path_length_file_length_bytes":
        fail("capability package content lock must use the length-prefixed canonical boundary")
    content_lock_paths = content_lock.get("paths") or []
    if len(content_lock_paths) != len(set(content_lock_paths)):
        fail("capability package content lock paths must be unique")
    exported_skill_roots = [f"skills/{skill_id}" for skill_id in expected_all_skill_ids]
    tracked_result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--stage", "-z", "--", *exported_skill_roots],
        check=False,
        capture_output=True,
    )
    tracked_exported_skill_files = []
    if tracked_result.returncode == 0:
        for raw_entry in tracked_result.stdout.split(b"\0"):
            if not raw_entry:
                continue
            try:
                raw_metadata, raw_path = raw_entry.split(b"\t", 1)
                mode, _object_id, stage = raw_metadata.decode("ascii").split(" ")
                relative = raw_path.decode("utf-8")
            except (UnicodeDecodeError, ValueError):
                fail("git returned an invalid tracked exported Skill entry")
            if mode not in {"100644", "100755"} or stage != "0":
                fail(f"exported Skill entry must be a tracked regular file: {relative} mode={mode} stage={stage}")
            source = root / relative
            if source.is_symlink() or not source.is_file():
                fail(f"exported Skill entry must resolve to a regular file: {relative}")
            tracked_exported_skill_files.append(relative)
    elif (root / ".git").exists():
        fail(
            "cannot inspect tracked exported Skill files: "
            + tracked_result.stderr.decode("utf-8", errors="replace").strip()
        )
    else:
        for relative_root in exported_skill_roots:
            skill_root = root / relative_root
            for source in sorted(skill_root.rglob("*")):
                if source.is_symlink():
                    fail(f"exported Skill archive entry must not be a symbolic link: {source.relative_to(root)}")
                if source.is_file() and "__pycache__" not in source.parts and source.suffix != ".pyc":
                    tracked_exported_skill_files.append(source.relative_to(root).as_posix())
    locked_skill_files = [relative for relative in content_lock_paths if relative.startswith("skills/")]
    if set(locked_skill_files) != set(tracked_exported_skill_files):
        missing = sorted(set(tracked_exported_skill_files) - set(locked_skill_files))
        unexpected = sorted(set(locked_skill_files) - set(tracked_exported_skill_files))
        fail(
            "capability package content lock must exactly cover tracked exported Skill files: "
            f"missing={missing} unexpected={unexpected}"
        )

    canonical_skill_shared_files = {
        "references/professional-quality-ref-templates.md": (
            root / "references/professional-quality-ref-templates.md"
        ),
        "docs/no-authority-boundary.md": root / "docs/no-authority-boundary.md",
        "docs/mas-scholar-skills-operating-model.md": (
            root / "docs/mas-scholar-skills-operating-model.md"
        ),
        "docs/capability-modules.md": root / "docs/capability-modules.md",
    }
    expected_skill_local_shared_files = set()
    actual_skill_local_shared_files = set()
    for skill_id in expected_all_skill_ids:
        skill_root = root / "skills" / skill_id
        skill_text = read_text(f"skills/{skill_id}/SKILL.md")
        for shared_ref, canonical_path in canonical_skill_shared_files.items():
            skill_local_path = skill_root / shared_ref
            skill_local_relative = skill_local_path.relative_to(root).as_posix()
            if skill_local_path.is_symlink() or skill_local_path.exists():
                actual_skill_local_shared_files.add(skill_local_relative)
            if shared_ref not in skill_text:
                continue
            expected_skill_local_shared_files.add(skill_local_relative)
            if skill_local_path.is_symlink() or not skill_local_path.is_file():
                fail(
                    f"exported Skill shared ref must resolve inside its own directory: "
                    f"{skill_local_relative}"
                )
            if skill_local_path.read_bytes() != canonical_path.read_bytes():
                fail(
                    f"exported Skill shared ref copy must equal canonical package bytes: "
                    f"{skill_local_relative} != {shared_ref}"
                )
            if skill_local_relative not in content_lock_paths:
                fail(f"exported Skill shared ref copy must be content locked: {skill_local_relative}")
    if actual_skill_local_shared_files != expected_skill_local_shared_files:
        missing = sorted(expected_skill_local_shared_files - actual_skill_local_shared_files)
        unexpected = sorted(actual_skill_local_shared_files - expected_skill_local_shared_files)
        fail(
            "exported Skill shared ref copies must exactly match SKILL.md package-local refs: "
            f"missing={missing} unexpected={unexpected}"
        )
    consuming_mas_skill_refs = {
        "medical-research-portfolio-memory-curator": [
            "docs/policies/study-workflow/publication_route_memory_policy.md",
        ],
    }
    for skill_id, refs in consuming_mas_skill_refs.items():
        skill_text = read_text(f"skills/{skill_id}/SKILL.md")
        for consuming_ref in refs:
            if consuming_ref not in skill_text:
                fail(f"{skill_id} must retain consuming MAS ref: {consuming_ref}")
            skill_local_path = root / "skills" / skill_id / consuming_ref
            if skill_local_path.is_symlink() or skill_local_path.exists():
                fail(
                    f"consuming MAS ref must not be copied into the ScholarSkills package: "
                    f"{skill_local_path.relative_to(root)}"
                )
    for relative in content_lock_paths:
        source = root / relative
        if source.is_symlink() or not source.is_file():
            fail(f"capability package content lock entry must be a regular file: {relative}")
    require_all(
        "capability package runtime content lock",
        content_lock_paths,
        [*all_runtime_contract_paths, *all_runtime_source_paths],
    )
    require_all(
        "capability package initial-draft contract content lock",
        content_lock_paths,
        ["contracts/scholarskills-medical-initial-draft-preflight-candidate-v1.schema.json"],
    )

    profile_package = reference_provider_profile.get("adapter_package") or {}
    if reference_provider_profile.get("adapter_abi") is not None:
        fail("reference provider profile must keep adapter ABI inside adapter_package")
    if profile_package.get("package_id") != "mas-scholar-skills":
        fail("reference provider profile must bind the installed ScholarSkills package")
    if profile_package.get("module_id") != runtime_module_id:
        fail("reference provider profile must bind the canonical runtime module")
    if profile_package.get("adapter_abi") != runtime_binding.get("adapter_abi"):
        fail("profile and package runtime binding adapter ABIs must match")
    if profile_package.get("registry_ref") != runtime_binding.get("registry_ref"):
        fail("profile and package runtime binding registry refs must match")
    if profile_package.get("handler_ref") != "runtime/reference-provider-adapters/index.ts#runReferenceProviderAdapterStep":
        fail("reference provider profile must select the canonical state-machine handler")
    if profile_package.get("byte_authority") != "installed_capability_package_source_commit_and_content_digest":
        fail("reference provider profile byte authority must bind source commit and package content digest")
    profile_adapter_ids = profile_package.get("adapter_ids") or []
    registry_adapters = reference_provider_registry.get("adapters") or []
    registry_adapter_ids = [item.get("adapter_id") for item in registry_adapters]
    if profile_adapter_ids != registry_adapter_ids:
        fail("reference provider profile and registry adapter ids must match in canonical order")
    if reference_provider_registry.get("module_id") != runtime_module_id:
        fail("reference provider registry must use the canonical runtime module id")
    if reference_provider_registry.get("adapter_abi") != runtime_binding.get("adapter_abi"):
        fail("reference provider registry and package adapter ABIs must match")
    if reference_provider_registry.get("handler") != expected_runtime_handler:
        fail("reference provider registry must expose the canonical TypeScript handler")
    if reference_provider_registry.get("state_machine_exports") != [
        "build_request",
        "parse_response",
        "next_step",
    ]:
        fail("reference provider registry must expose the bounded state-machine phases")
    if reference_provider_registry.get("max_steps") != 2:
        fail("reference provider registry must cap provider state machines at two steps")
    if reference_provider_registry.get("sandbox") != expected_runtime_sandbox:
        fail("reference provider registry sandbox must match the package runtime binding")
    if any(value is not False for value in (reference_provider_registry.get("no_authority_boundary") or {}).values()):
        fail("reference provider registry authority flags must all be false")
    if any(value is not False for value in (reference_provider_profile.get("no_authority_boundary") or {}).values()):
        fail("reference provider profile authority flags must all be false")
    if len(profile_adapter_ids) != 7 or len(set(profile_adapter_ids)) != 7:
        fail("scientific reference provider package must export exactly seven unique adapters")
    provider_rows = reference_provider_profile.get("providers") or []
    provider_ids = [item.get("provider_id") for item in provider_rows]
    if len(provider_ids) != len(set(provider_ids)):
        fail("reference provider profile provider ids must be unique")
    if reference_provider_profile.get("default_provider_ids") != provider_ids:
        fail("reference provider defaults must follow the canonical provider order")
    for provider in provider_rows:
        if provider.get("adapter_id") not in profile_adapter_ids:
            fail(f"provider {provider.get('provider_id')} selects an unexported adapter")
        endpoint = provider.get("endpoint") or {}
        default_origin = urlparse(endpoint.get("default_base_url") or "").scheme + "://" + urlparse(endpoint.get("default_base_url") or "").netloc
        if default_origin not in (endpoint.get("allowed_origins") or []):
            fail(f"provider {provider.get('provider_id')} default origin must be allowlisted")

    search_profile_package = scientific_search_profile.get("adapter_package") or {}
    if search_profile_package.get("package_id") != "mas-scholar-skills":
        fail("scientific search profile must bind the installed ScholarSkills package")
    if search_profile_package.get("module_id") != search_runtime_module_id:
        fail("scientific search profile must bind the canonical runtime module")
    if search_profile_package.get("adapter_abi") != search_runtime_binding.get("adapter_abi"):
        fail("scientific search profile and package binding adapter ABIs must match")
    if search_profile_package.get("registry_ref") != search_runtime_binding.get("registry_ref"):
        fail("scientific search profile and package binding registry refs must match")
    if search_profile_package.get("handler_ref") != "runtime/scientific-search-adapters/index.ts#runScientificSearchAdapterStep":
        fail("scientific search profile must select the canonical state-machine handler")
    if search_profile_package.get("byte_authority") != "installed_capability_package_source_commit_and_content_digest":
        fail("scientific search profile byte authority must bind source commit and package content digest")
    search_profile_adapter_ids = search_profile_package.get("adapter_ids") or []
    search_registry_adapters = scientific_search_registry.get("adapters") or []
    search_registry_adapter_ids = [item.get("adapter_id") for item in search_registry_adapters]
    if search_profile_adapter_ids != search_registry_adapter_ids:
        fail("scientific search profile and registry adapter ids must match in canonical order")
    if scientific_search_registry.get("module_id") != search_runtime_module_id:
        fail("scientific search registry must use the canonical runtime module id")
    if scientific_search_registry.get("adapter_abi") != search_runtime_binding.get("adapter_abi"):
        fail("scientific search registry and package adapter ABIs must match")
    if scientific_search_registry.get("handler") != expected_search_runtime_handler:
        fail("scientific search registry must expose the canonical TypeScript handler")
    if scientific_search_registry.get("state_machine_exports") != ["build_search_request", "parse_search_response"]:
        fail("scientific search registry must expose its two bounded state-machine phases")
    if scientific_search_registry.get("max_steps") != 2:
        fail("scientific search registry must cap provider searches at two steps")
    if scientific_search_registry.get("sandbox") != expected_runtime_sandbox:
        fail("scientific search registry sandbox must match the package runtime binding")
    if any(value is not False for value in (scientific_search_registry.get("no_authority_boundary") or {}).values()):
        fail("scientific search registry authority flags must all be false")
    if any(value is not False for value in (scientific_search_profile.get("no_authority_boundary") or {}).values()):
        fail("scientific search profile authority flags must all be false")
    expected_search_provider_scope = {
        "role": "package_owned_primary_biomedical_and_generic_metadata_search",
        "provider_ids": ["crossref", "openalex", "pubmed", "pmc"],
        "framework_core_provider_ids": [],
    }
    if scientific_search_profile.get("provider_scope") != expected_search_provider_scope:
        fail("scientific search package profile must own all four scientific providers")
    if len(search_profile_adapter_ids) != 4 or len(set(search_profile_adapter_ids)) != 4:
        fail("scientific search package must export exactly four unique adapters")
    search_provider_rows = scientific_search_profile.get("providers") or []
    search_provider_ids = [item.get("provider_id") for item in search_provider_rows]
    if scientific_search_profile.get("default_provider_ids") != search_provider_ids:
        fail("scientific search defaults must follow the canonical provider order")
    if len(search_provider_ids) != len(set(search_provider_ids)):
        fail("scientific search provider ids must be unique")
    expected_search_provider_bindings = [
        ("crossref", "crossref_search_rest", "Crossref"),
        ("openalex", "openalex_search_rest", "OpenAlex"),
        ("pubmed", "ncbi_pubmed_search", "PubMed"),
        ("pmc", "europe_pmc_search", "Europe PMC"),
    ]
    if [
        (item.get("provider_id"), item.get("adapter_id"), item.get("source_provider"))
        for item in search_provider_rows
    ] != expected_search_provider_bindings:
        fail("scientific search profile must preserve canonical provider and adapter pairings")
    if [
        (item.get("provider_id"), item.get("adapter_id"))
        for item in search_registry_adapters
    ] != [(provider_id, adapter_id) for provider_id, adapter_id, _ in expected_search_provider_bindings]:
        fail("scientific search registry must preserve canonical provider and adapter pairings")
    for provider in search_provider_rows:
        if provider.get("adapter_id") not in search_profile_adapter_ids:
            fail(f"scientific search provider {provider.get('provider_id')} selects an unexported adapter")
        endpoint = provider.get("endpoint") or {}
        parsed_default = urlparse(endpoint.get("default_base_url") or "")
        default_origin = parsed_default.scheme + "://" + parsed_default.netloc
        if default_origin not in (endpoint.get("allowed_origins") or []):
            fail(f"scientific search provider {provider.get('provider_id')} default origin must be allowlisted")

    for relative in all_runtime_source_paths:
        source = read_text(relative)
        if re.search(r"(?:from|import\s*)\s*['\"](?:node:)?(?:fs|http|https|net|tls|child_process|worker_threads)", source):
            fail(f"{relative} must not import direct I/O or process modules")
        for token in [
            "fetch(",
            "XMLHttpRequest",
            "process.env",
            "Deno.",
            "Bun.",
            "request_json",
            "request_text",
            "writeFile(",
            "spawn(",
            "exec(",
        ]:
            if token in source:
                fail(f"{relative} must not expose direct I/O surface {token}")
    if package_exports.get("optional_skills_installed_by_default") is not False:
        fail("specialty skills must not be installed by default")
    if package_exports.get("default_materialization_policy") != "core_skills_only":
        fail("capability package must use core-only default materialization")
    if package_exports.get("specialty_routing_policy") != "materialized_only_for_matching_tasks":
        fail("capability package must keep specialty routing task-selective")
    if "lifecycle" in package_manifest:
        fail("framework capability provider must not own consumer install, repair, activation, or readiness lifecycle")
    codex_surface = package_manifest.get("codex_surface") or {}
    expected_configured_codex_plugin_carrier = {
        "kind": "codex_plugin_manager",
        "plugin_selector": "mas-scholar-skills@mas-scholar-skills",
        "marketplace_source": "gaofeng21cn/mas-scholar-skills",
        "publication_ref": "ghcr.io/gaofeng21cn/one-person-lab-packages/mas-scholar-skills:latest-stable",
        "executor_route": "codex_cli",
    }
    expected_codex_surface = {
        "plugin_id": "mas-scholar-skills",
        "carrier_source_role": "codex_plugin_carrier_not_package_truth",
        "consumer_profiles_ref": "#/consumer_profiles",
        "default_materialized_skill_ids_ref": "#/exports/default_materialized_skill_ids",
        "codex_default_exposure": False,
        "optional_install_policy": "core_skills_only",
        "interaction_mode": "headless_internal",
        "configured_codex_plugin_carrier": expected_configured_codex_plugin_carrier,
    }
    if codex_surface != expected_codex_surface:
        fail("Codex package surface must preserve its metadata and expose the exact nested native carrier")
    for carrier_key in expected_configured_codex_plugin_carrier:
        if carrier_key in package_manifest:
            fail(f"Codex carrier field must stay under codex_surface: {carrier_key}")
    if "configured_codex_plugin_carrier" in package_manifest:
        fail("configured Codex carrier must stay under codex_surface")
