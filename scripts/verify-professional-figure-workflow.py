#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import math
import pathlib
import re
import sys
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_REF = "contracts/professional-figure-workflow.schema.json"
SURFACE_KIND = "mas_scholar_skills_professional_figure_workflow_candidate.v1"
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
EVIDENCE_TEXT_ROLES = {
    "panel_label",
    "axis_label",
    "tick_label",
    "legend",
    "necessary_statistical_annotation",
}


class WorkflowValidationError(ValueError):
    pass


def _fail(message: str) -> None:
    raise WorkflowValidationError(message)


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{label} must be an object")
    return value


def _sequence(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        _fail(f"{label} must be a non-empty array")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{label} must be a non-empty string")
    return value


def _sha256(value: Any, label: str) -> str:
    text = _text(value, label)
    if not SHA256_RE.fullmatch(text):
        _fail(f"{label} must be sha256:<64 lowercase hex>")
    return text


def _number(value: Any, label: str, *, minimum_exclusive: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _fail(f"{label} must be a number")
    number = float(value)
    if not math.isfinite(number) or number <= minimum_exclusive:
        _fail(f"{label} must be greater than {minimum_exclusive}")
    return number


def _artifact(value: Any, label: str) -> tuple[str, str, int, str]:
    artifact = _mapping(value, label)
    if set(artifact) != {"artifact_id", "format", "path_ref", "size_bytes", "sha256"}:
        _fail(f"{label} has invalid fields")
    artifact_id = _text(artifact.get("artifact_id"), f"{label}.artifact_id")
    artifact_format = artifact.get("format")
    if artifact_format not in {"PNG", "PDF"}:
        _fail(f"{label}.format must be PNG or PDF")
    _text(artifact.get("path_ref"), f"{label}.path_ref")
    size_bytes = artifact.get("size_bytes")
    if isinstance(size_bytes, bool) or not isinstance(size_bytes, int) or size_bytes < 1:
        _fail(f"{label}.size_bytes must be a positive integer")
    digest = _sha256(artifact.get("sha256"), f"{label}.sha256")
    return artifact_id, artifact_format, size_bytes, digest


def _artifact_inventory(value: Any, label: str) -> dict[str, tuple[str, int, str]]:
    inventory: dict[str, tuple[str, int, str]] = {}
    formats: set[str] = set()
    for index, row in enumerate(_sequence(value, label)):
        artifact_id, artifact_format, size_bytes, digest = _artifact(
            row, f"{label}[{index}]"
        )
        if artifact_id in inventory:
            _fail(f"{label} has duplicate artifact_id {artifact_id}")
        inventory[artifact_id] = (artifact_format, size_bytes, digest)
        formats.add(artifact_format)
    if formats != {"PNG", "PDF"}:
        _fail(f"{label} must bind a PNG/PDF pair")
    return inventory


def _invocation(
    value: Any,
    label: str,
    expected_skill_id: str,
    expected_outputs: dict[str, tuple[str, int, str]],
) -> set[str]:
    invocation = _mapping(value, label)
    required = {
        "receipt_id",
        "skill_id",
        "skill_source_ref",
        "skill_version",
        "skill_sha256",
        "invocation_id",
        "input_contract_ref",
        "input_sha256",
        "consumed_rule_refs",
        "output_artifacts",
        "status",
        "refs_only",
        "authority",
        "publication_ready",
    }
    if set(invocation) != required:
        _fail(f"{label} has invalid fields")
    if invocation.get("skill_id") != expected_skill_id:
        _fail(f"{label}.skill_id must be {expected_skill_id}")
    for field in (
        "receipt_id",
        "skill_source_ref",
        "skill_version",
        "invocation_id",
        "input_contract_ref",
    ):
        _text(invocation.get(field), f"{label}.{field}")
    _sha256(invocation.get("skill_sha256"), f"{label}.skill_sha256")
    _sha256(invocation.get("input_sha256"), f"{label}.input_sha256")
    rules = _sequence(invocation.get("consumed_rule_refs"), f"{label}.consumed_rule_refs")
    if any(not isinstance(item, str) or not item.strip() for item in rules):
        _fail(f"{label}.consumed_rule_refs must contain non-empty strings")
    if len(rules) != len(set(rules)):
        _fail(f"{label}.consumed_rule_refs must be unique")
    if _artifact_inventory(invocation.get("output_artifacts"), f"{label}.output_artifacts") != expected_outputs:
        _fail(f"{label}.output_artifacts must bind the exact final PNG/PDF bytes")
    if invocation.get("status") != "completed":
        _fail(f"{label}.status must be completed")
    if invocation.get("refs_only") is not True:
        _fail(f"{label}.refs_only must be true")
    for field in ("authority", "publication_ready"):
        if invocation.get(field) is not False:
            _fail(f"{label}.{field} must be false")
    return set(rules)


def _template_usage(value: Any, label: str) -> None:
    usage = _mapping(value, label)
    if usage.get("used") is False:
        if set(usage) != {"used", "decision_reason"}:
            _fail(f"{label} must omit template provenance when no template was used")
        _text(usage.get("decision_reason"), f"{label}.decision_reason")
        return
    if usage.get("used") is not True:
        _fail(f"{label}.used must be boolean")
    required = {
        "used",
        "template_id",
        "template_ref",
        "adaptation_mode",
        "semantic_match_ref",
        "transform_delta_ref",
    }
    if set(usage) != required:
        _fail(f"{label} must carry complete provenance only when a template was used")
    for field in required - {"used", "adaptation_mode"}:
        _text(usage.get(field), f"{label}.{field}")
    if usage.get("adaptation_mode") not in {
        "declared_template",
        "schema_adapted_template",
        "reference_guided_new_render",
    }:
        _fail(f"{label}.adaptation_mode is invalid")


def _text_policy(value: Any, label: str, figure_kind: str) -> None:
    policy = _mapping(value, label)
    if set(policy) != {
        "embedded_title",
        "embedded_subtitle",
        "embedded_prose_footer",
        "allowed_text_roles",
    }:
        _fail(f"{label} has invalid fields")
    roles = policy.get("allowed_text_roles")
    if not isinstance(roles, list) or len(roles) != len(set(roles)):
        _fail(f"{label}.allowed_text_roles must be a unique array")
    if figure_kind == "evidence_figure":
        for field in ("embedded_title", "embedded_subtitle", "embedded_prose_footer"):
            if policy.get(field) is not False:
                _fail(f"{label}.{field} must be false for an evidence figure")
        if set(roles) != EVIDENCE_TEXT_ROLES:
            _fail(f"{label}.allowed_text_roles violates the evidence-figure text policy")
    elif figure_kind != "graphical_abstract":
        _fail(f"{label} has unsupported figure_kind {figure_kind}")


def _final_scale_projection(value: Any, label: str) -> None:
    projection = _mapping(value, label)
    required = {
        "source_width_inches",
        "minimum_final_embed_width_inches",
        "embed_scale",
        "minimum_source_font_points",
        "minimum_projected_font_points",
        "required_minimum_font_points",
        "target_minimum_font_points",
        "minimum_source_safe_inset_points",
        "minimum_projected_safe_inset_points",
        "required_minimum_safe_inset_points",
        "all_text_extents_passed",
        "overflow_count",
        "collision_count",
        "spacing_violation_count",
    }
    if set(projection) != required:
        _fail(f"{label} has invalid fields")

    source_width = _number(projection.get("source_width_inches"), f"{label}.source_width_inches")
    embed_width = _number(
        projection.get("minimum_final_embed_width_inches"),
        f"{label}.minimum_final_embed_width_inches",
    )
    scale = _number(projection.get("embed_scale"), f"{label}.embed_scale")
    if embed_width > source_width + 1e-9 or scale > 1.0 + 1e-9:
        _fail(f"{label} must project from the source width to an equal or narrower width")
    if not math.isclose(scale, embed_width / source_width, rel_tol=0.0, abs_tol=1e-6):
        _fail(f"{label}.embed_scale must equal minimum_final_embed_width_inches/source_width_inches")

    source_font = _number(
        projection.get("minimum_source_font_points"),
        f"{label}.minimum_source_font_points",
    )
    projected_font = _number(
        projection.get("minimum_projected_font_points"),
        f"{label}.minimum_projected_font_points",
    )
    required_font = _number(
        projection.get("required_minimum_font_points"),
        f"{label}.required_minimum_font_points",
    )
    target_font = _number(
        projection.get("target_minimum_font_points"),
        f"{label}.target_minimum_font_points",
    )
    if not math.isclose(projected_font, source_font * scale, rel_tol=0.0, abs_tol=0.01):
        _fail(f"{label}.minimum_projected_font_points does not match the declared scale")
    if target_font + 1e-9 < required_font or projected_font + 1e-9 < target_font:
        _fail(f"{label} misses the required or target projected font floor")

    source_inset = _number(
        projection.get("minimum_source_safe_inset_points"),
        f"{label}.minimum_source_safe_inset_points",
    )
    projected_inset = _number(
        projection.get("minimum_projected_safe_inset_points"),
        f"{label}.minimum_projected_safe_inset_points",
    )
    required_inset = _number(
        projection.get("required_minimum_safe_inset_points"),
        f"{label}.required_minimum_safe_inset_points",
    )
    if not math.isclose(projected_inset, source_inset * scale, rel_tol=0.0, abs_tol=0.01):
        _fail(f"{label}.minimum_projected_safe_inset_points does not match the declared scale")
    if projected_inset + 1e-9 < required_inset:
        _fail(f"{label} misses the required projected safe inset")

    if projection.get("all_text_extents_passed") is not True:
        _fail(f"{label}.all_text_extents_passed must be true")
    for field in ("overflow_count", "collision_count", "spacing_violation_count"):
        count = projection.get(field)
        if isinstance(count, bool) or not isinstance(count, int) or count != 0:
            _fail(f"{label}.{field} must be integer zero")


def _flow_accounting_integrity(value: Any, label: str) -> bool:
    integrity = _mapping(value, label)
    if integrity.get("applicable") is False:
        if set(integrity) != {"applicable", "decision_reason"}:
            _fail(f"{label} must omit accounting proof when not applicable")
        _text(integrity.get("decision_reason"), f"{label}.decision_reason")
        return False
    if integrity.get("applicable") is not True:
        _fail(f"{label}.applicable must be boolean")
    required = {
        "applicable",
        "unit_levels",
        "quantitative_state_count",
        "connected_quantitative_state_count",
        "unconnected_satellite_state_count",
        "all_quantitative_states_connected",
        "denominator_identities_passed",
        "unit_transitions_declared",
        "accounting_receipt_ref",
    }
    if set(integrity) != required:
        _fail(f"{label} must carry complete accounting proof when applicable")
    units = _sequence(integrity.get("unit_levels"), f"{label}.unit_levels")
    if any(not isinstance(item, str) or not item.strip() for item in units):
        _fail(f"{label}.unit_levels must contain non-empty strings")
    if len(units) != len(set(units)):
        _fail(f"{label}.unit_levels must be unique")
    counts: dict[str, int] = {}
    for field in ("quantitative_state_count", "connected_quantitative_state_count"):
        count = integrity.get(field)
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            _fail(f"{label}.{field} must be a positive integer")
        counts[field] = count
    if counts["quantitative_state_count"] != counts["connected_quantitative_state_count"]:
        _fail(f"{label} leaves a quantitative state disconnected from its parent denominator")
    satellite_count = integrity.get("unconnected_satellite_state_count")
    if isinstance(satellite_count, bool) or not isinstance(satellite_count, int) or satellite_count != 0:
        _fail(f"{label}.unconnected_satellite_state_count must be integer zero")
    for field in (
        "all_quantitative_states_connected",
        "denominator_identities_passed",
        "unit_transitions_declared",
    ):
        if integrity.get(field) is not True:
            _fail(f"{label}.{field} must be true")
    _text(integrity.get("accounting_receipt_ref"), f"{label}.accounting_receipt_ref")
    return True


def _generation_receipt(
    value: Any,
    label: str,
    expected_outputs: dict[str, tuple[str, int, str]],
) -> None:
    receipt = _mapping(value, label)
    required = {
        "receipt_id",
        "renderer_family",
        "renderer_version",
        "source_code_ref",
        "source_code_sha256",
        "input_manifest_ref",
        "input_manifest_sha256",
        "outputs",
    }
    if set(receipt) != required:
        _fail(f"{label} has invalid fields")
    for field in (
        "receipt_id",
        "renderer_family",
        "renderer_version",
        "source_code_ref",
        "input_manifest_ref",
    ):
        _text(receipt.get(field), f"{label}.{field}")
    _sha256(receipt.get("source_code_sha256"), f"{label}.source_code_sha256")
    _sha256(receipt.get("input_manifest_sha256"), f"{label}.input_manifest_sha256")
    if _artifact_inventory(receipt.get("outputs"), f"{label}.outputs") != expected_outputs:
        _fail(f"{label}.outputs must bind the exact final PNG/PDF bytes")


def validate_workflow(value: Any) -> dict[str, Any]:
    workflow = _mapping(value, "workflow")
    required = {
        "surface_kind",
        "schema_ref",
        "schema_version",
        "workflow_id",
        "generation_id",
        "package_identity",
        "figures",
        "authority_boundary",
    }
    if set(workflow) != required:
        _fail("workflow has invalid fields")
    if workflow.get("surface_kind") != SURFACE_KIND:
        _fail(f"workflow.surface_kind must be {SURFACE_KIND}")
    if workflow.get("schema_ref") != SCHEMA_REF:
        _fail(f"workflow.schema_ref must be {SCHEMA_REF}")
    if workflow.get("schema_version") != 1:
        _fail("workflow.schema_version must be 1")
    _text(workflow.get("workflow_id"), "workflow.workflow_id")
    _text(workflow.get("generation_id"), "workflow.generation_id")

    package = _mapping(workflow.get("package_identity"), "workflow.package_identity")
    if set(package) != {"package_id", "version", "source_ref", "source_sha256"}:
        _fail("workflow.package_identity has invalid fields")
    if package.get("package_id") != "mas-scholar-skills":
        _fail("workflow.package_identity.package_id must be mas-scholar-skills")
    _text(package.get("version"), "workflow.package_identity.version")
    _text(package.get("source_ref"), "workflow.package_identity.source_ref")
    _sha256(package.get("source_sha256"), "workflow.package_identity.source_sha256")

    seen_figure_ids: set[str] = set()
    for index, item in enumerate(_sequence(workflow.get("figures"), "workflow.figures")):
        label = f"workflow.figures[{index}]"
        figure = _mapping(item, label)
        allowed = {
            "figure_id",
            "figure_kind",
            "composition_mode",
            "figure_contract_ref",
            "template_usage",
            "text_policy",
            "final_scale_projection",
            "flow_accounting_integrity",
            "design_invocation",
            "generation_receipt",
            "composer_invocation",
            "style_invocation",
            "outputs",
        }
        required_figure = allowed - {"composer_invocation"}
        if not required_figure.issubset(figure) or not set(figure).issubset(allowed):
            _fail(f"{label} has invalid fields")
        figure_id = _text(figure.get("figure_id"), f"{label}.figure_id")
        if figure_id in seen_figure_ids:
            _fail(f"workflow has duplicate figure_id {figure_id}")
        seen_figure_ids.add(figure_id)
        figure_kind = figure.get("figure_kind")
        composition_mode = figure.get("composition_mode")
        if composition_mode not in {"single_canvas_direct", "assembled_panels"}:
            _fail(f"{label}.composition_mode is invalid")
        _text(figure.get("figure_contract_ref"), f"{label}.figure_contract_ref")
        _template_usage(figure.get("template_usage"), f"{label}.template_usage")
        _text_policy(figure.get("text_policy"), f"{label}.text_policy", figure_kind)
        _final_scale_projection(
            figure.get("final_scale_projection"), f"{label}.final_scale_projection"
        )
        accounting_flow = _flow_accounting_integrity(
            figure.get("flow_accounting_integrity"),
            f"{label}.flow_accounting_integrity",
        )
        outputs = _artifact_inventory(figure.get("outputs"), f"{label}.outputs")
        design_rules = _invocation(
            figure.get("design_invocation"),
            f"{label}.design_invocation",
            "medical-figure-design",
            outputs,
        )
        _generation_receipt(
            figure.get("generation_receipt"), f"{label}.generation_receipt", outputs
        )
        if composition_mode == "assembled_panels":
            if "composer_invocation" not in figure:
                _fail(f"{label}.composer_invocation is required for assembled panels")
            _invocation(
                figure.get("composer_invocation"),
                f"{label}.composer_invocation",
                "medical-figure-composer",
                outputs,
            )
        elif "composer_invocation" in figure:
            _fail(f"{label}.composer_invocation is only valid for assembled panels")
        style_rules = _invocation(
            figure.get("style_invocation"),
            f"{label}.style_invocation",
            "medical-figure-style",
            outputs,
        )
        if "medical-figure-design#narrowest-final-embedding-projection" not in design_rules:
            _fail(f"{label}.design_invocation must consume the final-scale projection rule")
        if "medical-figure-style#narrowest-final-embedding-projection" not in style_rules:
            _fail(f"{label}.style_invocation must consume the final-scale projection rule")
        if accounting_flow and "medical-figure-design#connected-accounting-flow" not in design_rules:
            _fail(f"{label}.design_invocation must consume the connected accounting-flow rule")

    boundary = _mapping(workflow.get("authority_boundary"), "workflow.authority_boundary")
    if set(boundary) != {
        "refs_only",
        "can_mutate_artifacts",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_quality_readiness",
        "can_claim_export_readiness",
        "can_claim_publication_readiness",
    }:
        _fail("workflow.authority_boundary has invalid fields")
    if boundary.get("refs_only") is not True:
        _fail("workflow.authority_boundary.refs_only must be true")
    for field in set(boundary) - {"refs_only"}:
        if boundary.get(field) is not False:
            _fail(f"workflow.authority_boundary.{field} must be false")

    return {
        "status": "valid",
        "workflow_id": workflow["workflow_id"],
        "generation_id": workflow["generation_id"],
        "figure_count": len(workflow["figures"]),
    }


def _self_test() -> None:
    fixture_path = ROOT / "tests" / "fixtures" / "professional-figure-workflow.valid.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    validate_workflow(fixture)

    cases: list[tuple[str, dict[str, Any], str]] = []
    missing_design = copy.deepcopy(fixture)
    missing_design["figures"][0].pop("design_invocation")
    cases.append(("missing design invocation", missing_design, "invalid fields"))

    unbound_output = copy.deepcopy(fixture)
    unbound_output["figures"][0]["style_invocation"]["output_artifacts"][0][
        "sha256"
    ] = "sha256:" + "a" * 64
    cases.append(("unbound final output", unbound_output, "exact final PNG/PDF bytes"))

    invented_template = copy.deepcopy(fixture)
    invented_template["figures"][0]["template_usage"]["template_id"] = "invented"
    cases.append(("template provenance while unused", invented_template, "omit template provenance"))

    embedded_prose = copy.deepcopy(fixture)
    embedded_prose["figures"][0]["text_policy"]["embedded_prose_footer"] = True
    cases.append(("evidence prose footer", embedded_prose, "must be false"))

    missing_composer = copy.deepcopy(fixture)
    missing_composer["figures"][0]["composition_mode"] = "assembled_panels"
    cases.append(("assembled panels without composer", missing_composer, "composer_invocation is required"))

    narrow_projection = copy.deepcopy(fixture)
    narrow_projection["figures"][0]["final_scale_projection"][
        "minimum_final_embed_width_inches"
    ] = 4.0
    cases.append(("stale final-scale projection", narrow_projection, "embed_scale must equal"))

    disconnected_flow = copy.deepcopy(fixture)
    disconnected_flow["figures"][0]["flow_accounting_integrity"][
        "connected_quantitative_state_count"
    ] -= 1
    cases.append(("disconnected accounting state", disconnected_flow, "disconnected from its parent"))

    missing_projection_rule = copy.deepcopy(fixture)
    missing_projection_rule["figures"][0]["style_invocation"]["consumed_rule_refs"].remove(
        "medical-figure-style#narrowest-final-embedding-projection"
    )
    cases.append(("missing style projection rule", missing_projection_rule, "consume the final-scale projection rule"))

    for name, candidate, expected in cases:
        try:
            validate_workflow(candidate)
        except WorkflowValidationError as error:
            if expected not in str(error):
                raise AssertionError(f"{name}: unexpected error: {error}") from error
        else:
            raise AssertionError(f"{name}: invalid workflow was accepted")
    print(f"professional figure workflow self-checks passed: 1 positive, {len(cases)} negative")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", nargs="?", type=pathlib.Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            _self_test()
        if args.workflow is not None:
            result = validate_workflow(json.loads(args.workflow.read_text(encoding="utf-8")))
            print(json.dumps(result, sort_keys=True))
        if not args.self_test and args.workflow is None:
            parser.error("provide --self-test or a workflow JSON path")
    except (OSError, json.JSONDecodeError, WorkflowValidationError, AssertionError) as error:
        print(f"professional figure workflow verify failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
