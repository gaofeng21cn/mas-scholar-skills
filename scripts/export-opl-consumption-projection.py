#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "contracts/scholar-skills-capability-modules.json"
DEFAULT_OUTPUT = ROOT / "contracts/scholar-skills-opl-consumption-projection.json"

PROJECTED_MODULE_FIELDS = (
    "module_id",
    "brand_family",
    "display_name",
    "specialist_skill_id",
    "legacy_module_ids",
    "legacy_module_id_policy",
    "stage_fit",
    "input_schema_refs",
    "output_schema_refs",
    "dependency_profile_refs",
    "run_context_refs",
    "invocation_entries",
    "artifact_refs",
    "receipt_policy",
    "quality_evidence",
    "authority_boundary",
    "allowed_writes",
    "forbidden_writes",
    "data_governance_assessment_policy",
)


class ProjectionError(ValueError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ProjectionError(f"{path} must contain a JSON object")
    return value


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProjectionError(f"{field} must be an object")
    return value


def _array(value: Any, field: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (nonempty and not value):
        qualifier = "a non-empty array" if nonempty else "an array"
        raise ProjectionError(f"{field} must be {qualifier}")
    return value


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectionError(f"{field} must be a non-empty string")
    return value.strip()


def _field(value: dict[str, Any], path: str) -> Any:
    current: Any = value
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ProjectionError(f"missing field: {path}")
        current = current[part]
    return current


def _require_false_fields(value: dict[str, Any], fields: list[Any], context: str) -> None:
    for raw_field in fields:
        field = _string(raw_field, f"{context}.false_fields[]")
        if value.get(field) is not False:
            raise ProjectionError(f"{context}.{field} must be false")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _project_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace("--paper-root", "--artifact-root")
    if isinstance(value, list):
        return [_project_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _project_value(item) for key, item in value.items()}
    return value


def _projection_inputs(source: dict[str, Any]) -> dict[str, Any]:
    policy = _object(source.get("opl_consumption_projection_policy"), "opl_consumption_projection_policy")
    validator = _object(source.get("opl_consumption_validation_policy"), "opl_consumption_validation_policy")
    engine_policy = _object(source.get("candidate_artifact_engine_policy"), "candidate_artifact_engine_policy")
    module_ids = [
        _string(item, "opl_consumption_projection_policy.module_ids[]")
        for item in _array(policy.get("module_ids"), "opl_consumption_projection_policy.module_ids", nonempty=True)
    ]
    modules = _array(source.get("modules"), "modules", nonempty=True)
    modules_by_id: dict[str, dict[str, Any]] = {}
    for index, raw_module in enumerate(modules):
        module = _object(raw_module, f"modules[{index}]")
        module_id = _string(module.get("module_id"), f"modules[{index}].module_id")
        if module_id in modules_by_id:
            raise ProjectionError(f"duplicate module id: {module_id}")
        modules_by_id[module_id] = module
    if list(modules_by_id) != module_ids:
        raise ProjectionError("modules must match opl_consumption_projection_policy.module_ids in order")
    specs = _object(engine_policy.get("engine_specs"), "candidate_artifact_engine_policy.engine_specs")
    if list(specs) != module_ids:
        raise ProjectionError("artifact engine specs must match canonical module ids in order")
    return {
        "policy": policy,
        "validator": validator,
        "engine_policy": engine_policy,
        "module_ids": module_ids,
        "modules_by_id": modules_by_id,
        "specs": specs,
    }


def _validate_source(source: dict[str, Any], inputs: dict[str, Any]) -> None:
    validator = inputs["validator"]
    for raw_field in _array(validator.get("required_root_fields"), "validator.required_root_fields", nonempty=True):
        _field(source, _string(raw_field, "validator.required_root_fields[]"))
    for field, expected in _object(validator.get("root_exact_values"), "validator.root_exact_values").items():
        if _field(source, field) != expected:
            raise ProjectionError(f"{field} must equal {expected!r}")
    _require_false_fields(
        _object(source.get("authority_boundary"), "authority_boundary"),
        _array(validator.get("authority_false_fields"), "validator.authority_false_fields", nonempty=True),
        "authority_boundary",
    )
    bridge = _object(source.get("runtime_environment_bridge"), "runtime_environment_bridge")
    for field, expected in _object(validator.get("runtime_bridge_exact_values"), "validator.runtime_bridge_exact_values").items():
        if _field(bridge, field) != expected:
            raise ProjectionError(f"runtime_environment_bridge.{field} must equal {expected!r}")
    _require_false_fields(
        bridge,
        _array(validator.get("runtime_bridge_false_fields"), "validator.runtime_bridge_false_fields", nonempty=True),
        "runtime_environment_bridge",
    )

    required_module_fields = _array(validator.get("required_module_fields"), "validator.required_module_fields", nonempty=True)
    nonempty_module_arrays = _array(validator.get("nonempty_module_array_fields"), "validator.nonempty_module_array_fields", nonempty=True)
    module_authority_fields = _array(validator.get("authority_false_fields"), "validator.authority_false_fields", nonempty=True)
    receipt_false_fields = _array(validator.get("receipt_false_fields"), "validator.receipt_false_fields", nonempty=True)
    quality_false_fields = _array(validator.get("quality_false_fields"), "validator.quality_false_fields", nonempty=True)
    prefix = _string(validator.get("module_id_prefix"), "validator.module_id_prefix")
    allowed_formats = {
        _string(item, "validator.allowed_artifact_body_formats[]")
        for item in _array(validator.get("allowed_artifact_body_formats"), "validator.allowed_artifact_body_formats", nonempty=True)
    }
    required_engine_fields = _array(validator.get("required_artifact_engine_fields"), "validator.required_artifact_engine_fields", nonempty=True)
    engine_ids: set[str] = set()

    for module_id in inputs["module_ids"]:
        module = inputs["modules_by_id"][module_id]
        if not module_id.startswith(prefix):
            raise ProjectionError(f"module id must start with {prefix}: {module_id}")
        for raw_field in required_module_fields:
            _field(module, _string(raw_field, "validator.required_module_fields[]"))
        for raw_field in nonempty_module_arrays:
            field = _string(raw_field, "validator.nonempty_module_array_fields[]")
            _array(_field(module, field), f"{module_id}.{field}", nonempty=True)
        _require_false_fields(
            _object(module.get("authority_boundary"), f"{module_id}.authority_boundary"),
            module_authority_fields,
            f"{module_id}.authority_boundary",
        )
        _require_false_fields(
            _object(module.get("receipt_policy"), f"{module_id}.receipt_policy"),
            receipt_false_fields,
            f"{module_id}.receipt_policy",
        )
        _require_false_fields(
            _object(module.get("quality_evidence"), f"{module_id}.quality_evidence"),
            quality_false_fields,
            f"{module_id}.quality_evidence",
        )

        spec = _object(inputs["specs"][module_id], f"engine_specs.{module_id}")
        for raw_field in required_engine_fields:
            _field(spec, _string(raw_field, "validator.required_artifact_engine_fields[]"))
        engine_id = _string(spec.get("engine_id"), f"engine_specs.{module_id}.engine_id")
        if engine_id in engine_ids:
            raise ProjectionError(f"duplicate artifact engine id: {engine_id}")
        engine_ids.add(engine_id)
        if spec.get("body_format") not in allowed_formats:
            raise ProjectionError(f"unsupported artifact body format for {module_id}: {spec.get('body_format')!r}")
        for field in (
            "required_artifact_ref_families",
            "execution_receipt_ref_families",
            "required_payload_fields",
            "optional_payload_fields",
            "quality_checks",
            "candidate_sections",
        ):
            values = [
                _string(item, f"engine_specs.{module_id}.{field}[]")
                for item in _array(spec.get(field), f"engine_specs.{module_id}.{field}", nonempty=True)
            ]
            if len(values) != len(set(values)):
                raise ProjectionError(f"engine_specs.{module_id}.{field} must not contain duplicates")

    _require_false_fields(
        _object(inputs["engine_policy"].get("authority_flags"), "candidate_artifact_engine_policy.authority_flags"),
        _array(validator.get("artifact_authority_false_fields"), "validator.artifact_authority_false_fields", nonempty=True),
        "candidate_artifact_engine_policy.authority_flags",
    )


def build_projection(source: dict[str, Any]) -> dict[str, Any]:
    inputs = _projection_inputs(source)
    _validate_source(source, inputs)
    policy = inputs["policy"]
    engine_policy = inputs["engine_policy"]
    module_projections = []
    for index, module_id in enumerate(inputs["module_ids"]):
        module = inputs["modules_by_id"][module_id]
        spec = inputs["specs"][module_id]
        projected_module = {
            key: _project_value(module[key])
            for key in PROJECTED_MODULE_FIELDS
            if key in module
        }
        projected_module.update(
            {
                "profile_id": module_id.removeprefix("mas-scholar-skills."),
                "source_module_ref": f"contracts/scholar-skills-capability-modules.json#/modules/{index}",
                "required_artifact_ref_families": spec["required_artifact_ref_families"],
                "execution_receipt_ref_families": spec["execution_receipt_ref_families"],
                "artifact_engine": {
                    key: spec[key]
                    for key in (
                        "engine_id",
                        "engine_version",
                        "body_format",
                        "output_kind",
                        "required_payload_fields",
                        "optional_payload_fields",
                        "quality_checks",
                        "candidate_sections",
                    )
                },
            }
        )
        module_projections.append(
            projected_module
        )
    fingerprint_input = {
        "contract_id": source["contract_id"],
        "schema_version": source["schema_version"],
        "brand_family": source["brand_family"],
        "projection_policy": policy,
        "validator_policy": inputs["validator"],
        "artifact_engine_policy": engine_policy,
        "modules": module_projections,
    }
    source_projection_sha256 = hashlib.sha256(_canonical_json(fingerprint_input).encode("utf-8")).hexdigest()
    return {
        "contract_id": source["contract_id"],
        "projection_kind": "mas_scholar_skills_opl_consumption_projection.v1",
        "schema_version": "1.0.0",
        "state": "active_refs_only_consumer_projection",
        "owner": source["owner"],
        "brand_family": source["brand_family"],
        "purpose": "Generated consumer projection for OPL generic validation, catalog projection, runtime preparation, candidate artifact materialization, skill sync, and provenance.",
        "machine_boundary": "MAS Scholar Skills owns the medical module catalog, validator policy, candidate artifact engine rules, and professional skill truth. OPL consumes this generated projection and must not treat it as domain truth, quality verdict, artifact authority, owner receipt, typed blocker, current-package authority, publication readiness, or a second canonical owner source.",
        "canonical_owner_repo": policy["canonical_owner_repo"],
        "framework_owner": source["owner"],
        "consumer": policy["consumer"],
        "consumer_role": policy["consumer_role"],
        "source_contract_ref": policy["source_contract_ref"],
        "source_projection_sha256": source_projection_sha256,
        "source_projection_contract": {
            "contract_id": "mas_scholar_skills_opl_consumption_projection",
            "schema_version": "1.0.0",
            "canonical_source": {
                "owner_repo": policy["canonical_owner_repo"],
                "contract_path": policy["source_contract_ref"],
                "fingerprint_algorithm": "sha256",
                "fingerprint": source_projection_sha256,
            },
            "projection_owner": "OPL Framework",
            "projection_role": "generated_consumer_projection_not_canonical_owner_truth",
            "projected_command_vocabulary": "artifact_root",
            "source_command_vocabulary": "paper_root_compatibility_allowed",
            "currentness_boundary": {
                "snapshot_kind": "source_contract_fingerprint",
                "projection_current_only_for_recorded_fingerprint": True,
                "projection_claims_live_owner_currentness": False,
                "sibling_repo_required_in_ci": False,
            },
        },
        "ownership_boundary": {
            "opl_owned_surfaces": [
                "generic_contract_validation",
                "generic_module_catalog_projection",
                "generic_candidate_artifact_materialization",
                "runtime_environment_bridge",
                "skill_sync_projection",
                "provenance",
            ],
            "package_descriptor_owner": policy["canonical_owner_repo"],
            "skill_sync_owner": "OPL Framework",
            "runtime_environment_bridge_owner": "OPL Framework",
            "professional_skill_truth_owner": policy["canonical_owner_repo"],
            "citation_judgment_owner": "MAS_or_consuming_domain_owner",
            "domain_truth_owner": "consuming_domain_owner",
            "no_authority_policy": "projection_and_framework_receipts_are_refs_only_and_require_consuming_domain_owner_authority",
            "pack_or_bridge_receipt_counts_as_domain_truth": False,
            "pack_or_bridge_receipt_counts_as_citation_truth": False,
        },
        "runtime_environment_bridge": _project_value(source["runtime_environment_bridge"]),
        "module_ids": inputs["module_ids"],
        "projection_policy": policy,
        "validator_policy": inputs["validator"],
        "candidate_artifact_policy": {
            "policy_id": engine_policy["policy_id"],
            "body_policy": engine_policy["body_policy"],
            "authority_flags": engine_policy["authority_flags"],
        },
        "modules": module_projections,
        "authority_boundary": source["authority_boundary"],
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export the deterministic MAS Scholar Skills projection consumed by OPL.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    source = _read_json(args.source.resolve())
    rendered = _render(build_projection(source))
    output = (args.output or DEFAULT_OUTPUT).resolve()
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
            raise ProjectionError(f"projection is stale: {output}")
        print(f"ScholarSkills OPL consumption projection is current: {output}")
        return 0
    if args.output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(output)
        return 0
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProjectionError as exc:
        raise SystemExit(f"projection export failed: {exc}") from exc
