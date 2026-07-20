"""Deterministic refs-only helpers for medical manuscript writing.

These helpers scaffold prompts, schemas, and lint hints. They do not create
MAS truth, owner receipts, typed blockers, artifacts, or publication readiness.
"""

from __future__ import annotations

import json
import re
from typing import Any, Mapping, Sequence


SECTION_TYPES = (
    "title",
    "abstract",
    "introduction",
    "methods",
    "results",
    "discussion",
    "conclusion",
)

PARAGRAPH_JOBS = (
    "context",
    "gap",
    "approach",
    "result",
    "comparison",
    "implication",
    "limitation",
    "route-back",
)

STRONG_VERBS = ("prove", "establish", "confirm", "demonstrate")
MODERATE_VERBS = ("show", "support", "indicate")
WEAK_VERBS = ("suggest", "may", "could", "is consistent with")

FIRST_DRAFT_STORY_REFS = (
    "unique_scientific_claim_ref",
    "clinical_or_operational_value_ref",
    "falsifiable_boundary_ref",
    "result_paragraph_job_map_ref",
    "figure_table_narrative_arc_ref",
    "main_supplement_placement_ref",
    "terminology_surface_ledger_ref",
)

EXTERNAL_VALIDATION_FIRST_DRAFT_REFS = (
    "source_model_provenance_ref",
    "target_population_and_followup_ref",
    "fixed_horizon_risk_semantics_ref",
    "construct_comparability_ref",
    "calibration_and_performance_ref",
    "structured_display_source_map_ref",
    "claim_guardrail_ref",
    "negative_or_non_estimable_result_ref",
)

TERMINOLOGY_SURFACES = (
    "manuscript_text",
    "table_titles",
    "figure_legends",
    "csv_headers",
    "machine_readable_endpoints",
    "supplement",
)

INITIAL_DRAFT_PREFLIGHT_STATUSES = (
    "satisfied",
    "route_back_required",
    "not_applicable_with_reason",
)

INITIAL_DRAFT_PREFLIGHT_GATES = (
    "study_identity",
    "data_freeze",
    "statistical_integrity",
    "citation_integrity",
    "table_traceability",
    "display_scope",
    "story_contract",
)

INITIAL_DRAFT_PREFLIGHT_DEPENDENCY_TIERS = {
    "baseline_data_citation": 10,
    "analysis": 20,
    "authoring_display": 30,
    "review": 40,
}

INITIAL_DRAFT_PREFLIGHT_DEPENDENCY_OWNERS = {
    "baseline_data_citation": "baseline_and_evidence_setup",
    "analysis": "bounded_analysis_campaign",
    "authoring_display": "manuscript_authoring",
    "review": "review_and_quality_gate",
}

INITIAL_DRAFT_PREFLIGHT_AUTHORITY = {
    "refs_only": True,
    "can_write_domain_truth": False,
    "can_sign_owner_receipt": False,
    "can_create_typed_blocker": False,
    "can_claim_quality_verdict": False,
    "can_claim_publication_readiness": False,
    "can_authorize_full_draft": False,
}

EXACT_REF_FIELDS = frozenset({"kind", "ref", "size_bytes", "sha256"})

REGISTRY_BOUNDARY_TERMS = (
    "gap",
    "intensity",
    "burden",
    "adherence",
    "nonadherence",
    "workload",
    "quality ranking",
)

READER_FACING_SURFACES = frozenset(
    {
        "manuscript_text",
        "table_titles",
        "table_notes",
        "figure_legends",
        "supplement",
    }
)

READER_SURFACE_PROHIBITIONS = (
    (
        "INTERNAL_WORKFLOW_LANGUAGE_IN_READER_SURFACE",
        re.compile(
            r"(?:analytical authoring process|human study owner|explicit human gate|"
            r"formal_submission_authority|runtime_authority|owner receipt|quality debt|"
            r"generation[_ -]?id|source hash)",
            re.IGNORECASE,
        ),
        "move workflow, authority, and generation metadata to a checklist or receipt",
    ),
    (
        "AUTHORING_INSTRUCTION_IN_READER_SURFACE",
        re.compile(
            r"(?:\bshould be reported\b|(?:^|[.!?]\s+)report\s+cross[- ]fitted\b|"
            r"\[insert\s+(?:table|figure|supplement)|\bTODO\b|\breplace with\b)",
            re.IGNORECASE,
        ),
        "replace author instructions with final reader-facing prose or remove them",
    ),
    (
        "INTERNAL_REVIEW_LANGUAGE_IN_READER_SURFACE",
        re.compile(
            r"(?:supplementary table review companion|bounded review display|"
            r"deterministic(?:ly)? sampled rows?|CSV row(?:s| numbers?)?|"
            r"exact electronic source)",
            re.IGNORECASE,
        ),
        "keep review-companion and row-trace language on the internal audit surface",
    ),
)


def paper_brief_schema() -> dict[str, Any]:
    """Return the compact paper brief schema expected from AI judgment."""

    return {
        "type": "object",
        "required": [
            "one_sentence_argument_ref",
            "reader_question_ref",
            "evidence_refs",
            "section_outline_ref",
            "claim_strength_calibration_ref",
        ],
        "properties": {
            "one_sentence_argument_ref": {"type": "string"},
            "reader_question_ref": {"type": "string"},
            "audience_ref": {"type": "string"},
            "evidence_refs": {"type": "array", "items": {"type": "string"}},
            "figure_table_refs": {"type": "array", "items": {"type": "string"}},
            "section_outline_ref": {"type": "array", "items": {"type": "object"}},
            "claim_strength_calibration_ref": {
                "type": "array",
                "items": {"type": "object"},
            },
            "route_back_candidate": {"type": "string"},
        },
    }


def first_draft_story_contract_schema() -> dict[str, Any]:
    """Return the handling-editor story contract required before prose."""

    return {
        "type": "object",
        "required": list(FIRST_DRAFT_STORY_REFS),
        "properties": {
            ref: {"type": "string"} for ref in FIRST_DRAFT_STORY_REFS
        }
        | {
            "external_validation_contract_ref": {"type": "string"},
            "route_back_candidate": {"type": "object"},
            "authority": {"const": False},
        },
    }


def external_validation_first_draft_contract_schema() -> dict[str, Any]:
    """Return the specialist inputs required before external-validation prose."""

    return {
        "type": "object",
        "required": list(EXTERNAL_VALIDATION_FIRST_DRAFT_REFS),
        "properties": {
            ref: {"type": "string"} for ref in EXTERNAL_VALIDATION_FIRST_DRAFT_REFS
        }
        | {
            "route_back_candidate": {"type": "object"},
            "authority": {"const": False},
        },
    }


def terminology_surface_ledger_schema() -> dict[str, Any]:
    """Return the cross-surface terminology-ledger candidate schema."""

    return {
        "type": "object",
        "required": ["surface_refs", "canonical_terms", "boundary_terms"],
        "properties": {
            "surface_refs": {
                "type": "object",
                "required": list(TERMINOLOGY_SURFACES),
                "description": (
                    "Inventory every terminology surface; absent surfaces use an "
                    "explicit not-applicable record with a reason."
                ),
            },
            "canonical_terms": {"type": "array", "items": {"type": "object"}},
            "boundary_terms": {"type": "array", "items": {"type": "object"}},
            "route_back_candidate": {"type": "object"},
            "authority": {"const": False},
        },
    }


def medical_initial_draft_preflight_candidate_schema() -> dict[str, Any]:
    """Return the package-owned machine contract locator for draft preflight."""

    return {
        "$ref": (
            "contracts/"
            "scholarskills-medical-initial-draft-preflight-candidate-v1.schema.json"
        ),
        "surface_kind": "medical_initial_draft_preflight_candidate_ref",
        "schema_version": 1,
        "statuses": list(INITIAL_DRAFT_PREFLIGHT_STATUSES),
        "required_gate_items": list(INITIAL_DRAFT_PREFLIGHT_GATES),
        "dependency_tiers": dict(INITIAL_DRAFT_PREFLIGHT_DEPENDENCY_TIERS),
        "dependency_owners": dict(INITIAL_DRAFT_PREFLIGHT_DEPENDENCY_OWNERS),
        "authority_boundary": dict(INITIAL_DRAFT_PREFLIGHT_AUTHORITY),
    }


def validate_medical_initial_draft_preflight_candidate(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Validate exact refs, dependency order, and no-authority preflight shape."""

    if not isinstance(candidate, Mapping):
        raise ValueError("medical initial draft preflight candidate must be an object")

    violations: list[dict[str, object]] = []
    expected_top_fields = {
        "surface_kind",
        "schema_version",
        "manuscript_mode",
        "status",
        "source_pack_ref",
        "gate_items",
        "unresolved_items",
        "earliest_route_back_owner",
        "not_applicable_reason",
        "owner_gate_handoff_ref",
        "authority_boundary",
    }
    _check_exact_fields(candidate, expected_top_fields, "candidate", violations)

    if candidate.get("surface_kind") != "medical_initial_draft_preflight_candidate_ref":
        violations.append(_preflight_violation("PREFLIGHT_SURFACE_KIND_INVALID", "surface_kind"))
    if candidate.get("schema_version") != 1:
        violations.append(_preflight_violation("PREFLIGHT_SCHEMA_VERSION_INVALID", "schema_version"))
    if not str(candidate.get("manuscript_mode") or "").strip():
        violations.append(_preflight_violation("PREFLIGHT_MANUSCRIPT_MODE_MISSING", "manuscript_mode"))

    status = str(candidate.get("status") or "")
    if status not in INITIAL_DRAFT_PREFLIGHT_STATUSES:
        violations.append(_preflight_violation("PREFLIGHT_STATUS_INVALID", "status"))

    for field in ("source_pack_ref", "owner_gate_handoff_ref"):
        violations.extend(_validate_exact_ref(candidate.get(field), field))

    unresolved_raw = candidate.get("unresolved_items")
    unresolved_items = (
        list(unresolved_raw)
        if isinstance(unresolved_raw, Sequence) and not isinstance(unresolved_raw, (str, bytes))
        else []
    )
    if not isinstance(unresolved_raw, Sequence) or isinstance(unresolved_raw, (str, bytes)):
        violations.append(_preflight_violation("PREFLIGHT_UNRESOLVED_ITEMS_INVALID", "unresolved_items"))

    unresolved_by_id: dict[str, Mapping[str, object]] = {}
    unresolved_expected_fields = {
        "item_id",
        "domain",
        "severity",
        "finding",
        "evidence_refs",
        "dependency_tier",
        "dependency_rank",
        "route_back_owner",
        "required_evidence",
    }
    unresolved_dependency_keys: list[tuple[int, str]] = []
    canonical_owner_by_item: dict[str, str] = {}
    for index, item in enumerate(unresolved_items):
        label = f"unresolved_items[{index}]"
        if not isinstance(item, Mapping):
            violations.append(_preflight_violation("PREFLIGHT_UNRESOLVED_ITEM_INVALID", label))
            continue
        _check_exact_fields(item, unresolved_expected_fields, label, violations)
        item_id = str(item.get("item_id") or "").strip()
        if not item_id:
            violations.append(_preflight_violation("PREFLIGHT_UNRESOLVED_ITEM_ID_MISSING", f"{label}.item_id"))
        elif item_id in unresolved_by_id:
            violations.append(_preflight_violation("PREFLIGHT_UNRESOLVED_ITEM_ID_DUPLICATE", f"{label}.item_id"))
        else:
            unresolved_by_id[item_id] = item
        if str(item.get("domain") or "") not in INITIAL_DRAFT_PREFLIGHT_GATES:
            violations.append(_preflight_violation("PREFLIGHT_UNRESOLVED_DOMAIN_INVALID", f"{label}.domain"))
        if str(item.get("severity") or "") not in {"blocker", "major", "minor"}:
            violations.append(_preflight_violation("PREFLIGHT_UNRESOLVED_SEVERITY_INVALID", f"{label}.severity"))
        for field in ("finding", "route_back_owner", "required_evidence"):
            if not str(item.get(field) or "").strip():
                violations.append(_preflight_violation("PREFLIGHT_UNRESOLVED_FIELD_MISSING", f"{label}.{field}"))
        evidence_refs = item.get("evidence_refs")
        if not isinstance(evidence_refs, Sequence) or isinstance(evidence_refs, (str, bytes)):
            violations.append(_preflight_violation("PREFLIGHT_EVIDENCE_REFS_INVALID", f"{label}.evidence_refs"))
        else:
            for ref_index, ref in enumerate(evidence_refs):
                violations.extend(_validate_exact_ref(ref, f"{label}.evidence_refs[{ref_index}]"))
        dependency_tier = str(item.get("dependency_tier") or "")
        expected_rank = INITIAL_DRAFT_PREFLIGHT_DEPENDENCY_TIERS.get(dependency_tier)
        dependency_rank = item.get("dependency_rank")
        if expected_rank is None:
            violations.append(
                _preflight_violation(
                    "PREFLIGHT_DEPENDENCY_TIER_INVALID",
                    f"{label}.dependency_tier",
                )
            )
        elif isinstance(dependency_rank, bool) or dependency_rank != expected_rank:
            violations.append(
                _preflight_violation(
                    "PREFLIGHT_DEPENDENCY_RANK_INVALID",
                    f"{label}.dependency_rank",
                )
            )
        route_back_owner = str(item.get("route_back_owner") or "").strip()
        expected_owner = INITIAL_DRAFT_PREFLIGHT_DEPENDENCY_OWNERS.get(
            dependency_tier
        )
        if expected_owner is not None and route_back_owner != expected_owner:
            violations.append(
                _preflight_violation(
                    "PREFLIGHT_DEPENDENCY_OWNER_INVALID",
                    f"{label}.route_back_owner",
                )
            )
        if expected_rank is not None and expected_owner is not None and item_id:
            unresolved_dependency_keys.append((expected_rank, item_id))
            canonical_owner_by_item[item_id] = expected_owner

    if unresolved_dependency_keys != sorted(unresolved_dependency_keys):
        violations.append(
            _preflight_violation(
                "PREFLIGHT_UNRESOLVED_DEPENDENCY_ORDER_INVALID",
                "unresolved_items",
            )
        )

    gate_items = candidate.get("gate_items")
    referenced_unresolved_ids: list[str] = []
    if not isinstance(gate_items, Mapping):
        violations.append(_preflight_violation("PREFLIGHT_GATE_ITEMS_INVALID", "gate_items"))
        gate_items = {}
    _check_exact_fields(gate_items, set(INITIAL_DRAFT_PREFLIGHT_GATES), "gate_items", violations)
    gate_expected_fields = {"status", "refs", "unresolved_item_ids", "not_applicable_reason"}
    for gate_name in INITIAL_DRAFT_PREFLIGHT_GATES:
        gate = gate_items.get(gate_name)
        label = f"gate_items.{gate_name}"
        if not isinstance(gate, Mapping):
            violations.append(_preflight_violation("PREFLIGHT_GATE_ITEM_INVALID", label))
            continue
        _check_exact_fields(gate, gate_expected_fields, label, violations)
        gate_status = str(gate.get("status") or "")
        if gate_status not in INITIAL_DRAFT_PREFLIGHT_STATUSES:
            violations.append(_preflight_violation("PREFLIGHT_GATE_STATUS_INVALID", f"{label}.status"))
        refs = gate.get("refs")
        if not isinstance(refs, Sequence) or isinstance(refs, (str, bytes)):
            violations.append(_preflight_violation("PREFLIGHT_GATE_REFS_INVALID", f"{label}.refs"))
            refs = []
        for ref_index, ref in enumerate(refs):
            violations.extend(_validate_exact_ref(ref, f"{label}.refs[{ref_index}]"))
        unresolved_ids_raw = gate.get("unresolved_item_ids")
        unresolved_ids = (
            [str(value).strip() for value in unresolved_ids_raw]
            if isinstance(unresolved_ids_raw, Sequence)
            and not isinstance(unresolved_ids_raw, (str, bytes))
            else []
        )
        if not isinstance(unresolved_ids_raw, Sequence) or isinstance(unresolved_ids_raw, (str, bytes)):
            violations.append(_preflight_violation("PREFLIGHT_GATE_UNRESOLVED_IDS_INVALID", f"{label}.unresolved_item_ids"))
        if len(unresolved_ids) != len(set(unresolved_ids)) or any(not value for value in unresolved_ids):
            violations.append(_preflight_violation("PREFLIGHT_GATE_UNRESOLVED_IDS_INVALID", f"{label}.unresolved_item_ids"))
        referenced_unresolved_ids.extend(unresolved_ids)
        for item_id in unresolved_ids:
            item = unresolved_by_id.get(item_id)
            if item is None:
                violations.append(_preflight_violation("PREFLIGHT_GATE_UNRESOLVED_ID_UNKNOWN", f"{label}.unresolved_item_ids"))
            elif item.get("domain") != gate_name:
                violations.append(_preflight_violation("PREFLIGHT_GATE_UNRESOLVED_DOMAIN_MISMATCH", f"{label}.unresolved_item_ids"))
        na_reason = gate.get("not_applicable_reason")
        if gate_status == "satisfied":
            if not refs:
                violations.append(_preflight_violation("PREFLIGHT_SATISFIED_GATE_REF_MISSING", f"{label}.refs"))
            if unresolved_ids or na_reason is not None:
                violations.append(_preflight_violation("PREFLIGHT_SATISFIED_GATE_CONTRADICTORY", label))
        elif gate_status == "route_back_required":
            if not unresolved_ids or na_reason is not None:
                violations.append(_preflight_violation("PREFLIGHT_ROUTE_BACK_GATE_INCOMPLETE", label))
        elif gate_status == "not_applicable_with_reason":
            if unresolved_ids or not str(na_reason or "").strip():
                violations.append(_preflight_violation("PREFLIGHT_NOT_APPLICABLE_GATE_REASON_MISSING", label))

    if sorted(referenced_unresolved_ids) != sorted(unresolved_by_id):
        violations.append(_preflight_violation("PREFLIGHT_UNRESOLVED_ITEMS_NOT_EXACTLY_BOUND", "unresolved_items"))

    gate_statuses = {
        str(gate.get("status") or "")
        for gate in gate_items.values()
        if isinstance(gate, Mapping)
    }
    expected_status = (
        "route_back_required"
        if "route_back_required" in gate_statuses or unresolved_items
        else "not_applicable_with_reason"
        if gate_statuses == {"not_applicable_with_reason"}
        else "satisfied"
    )
    if status in INITIAL_DRAFT_PREFLIGHT_STATUSES and status != expected_status:
        violations.append(_preflight_violation("PREFLIGHT_AGGREGATE_STATUS_INCONSISTENT", "status"))

    earliest_owner = candidate.get("earliest_route_back_owner")
    computed_earliest_owner: str | None = None
    if unresolved_dependency_keys:
        earliest_item_id = min(unresolved_dependency_keys)[1]
        computed_earliest_owner = canonical_owner_by_item.get(earliest_item_id)
    top_na_reason = candidate.get("not_applicable_reason")
    if status == "route_back_required":
        if not computed_earliest_owner or earliest_owner != computed_earliest_owner:
            violations.append(_preflight_violation("PREFLIGHT_EARLIEST_OWNER_INVALID", "earliest_route_back_owner"))
        if top_na_reason is not None:
            violations.append(_preflight_violation("PREFLIGHT_ROUTE_BACK_REASON_CONTRADICTORY", "not_applicable_reason"))
    elif status == "satisfied":
        if unresolved_items or earliest_owner is not None or top_na_reason is not None:
            violations.append(_preflight_violation("PREFLIGHT_SATISFIED_STATE_CONTRADICTORY", "status"))
    elif status == "not_applicable_with_reason":
        if unresolved_items or earliest_owner is not None or not str(top_na_reason or "").strip():
            violations.append(_preflight_violation("PREFLIGHT_NOT_APPLICABLE_STATE_INVALID", "status"))

    authority = candidate.get("authority_boundary")
    if not isinstance(authority, Mapping) or dict(authority) != INITIAL_DRAFT_PREFLIGHT_AUTHORITY:
        violations.append(_preflight_violation("PREFLIGHT_AUTHORITY_BOUNDARY_INVALID", "authority_boundary"))

    violations.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not violations
    return {
        "surface_kind": "medical_initial_draft_preflight_kernel_audit_candidate.v1",
        "machine_check_status": (
            "candidate_ref_shape_complete" if complete else "candidate_ref_shape_incomplete"
        ),
        "candidate_status": status,
        "earliest_route_back_owner": computed_earliest_owner,
        "violations": violations,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-manuscript-writing",
            "reason": "medical_initial_draft_preflight_candidate_requires_repair",
            "authority": False,
        },
        "authority": False,
        "authority_boundary": dict(INITIAL_DRAFT_PREFLIGHT_AUTHORITY),
    }


def _check_exact_fields(
    value: Mapping[str, object],
    expected: set[str],
    label: str,
    violations: list[dict[str, object]],
) -> None:
    actual = set(value)
    for field in sorted(expected - actual):
        violations.append(_preflight_violation("PREFLIGHT_FIELD_MISSING", f"{label}.{field}"))
    for field in sorted(actual - expected):
        violations.append(_preflight_violation("PREFLIGHT_FIELD_UNEXPECTED", f"{label}.{field}"))


def _validate_exact_ref(value: object, label: str) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    if not isinstance(value, Mapping):
        return [_preflight_violation("PREFLIGHT_EXACT_REF_INVALID", label)]
    _check_exact_fields(value, set(EXACT_REF_FIELDS), label, violations)
    for field in ("kind", "ref"):
        if not str(value.get(field) or "").strip():
            violations.append(_preflight_violation("PREFLIGHT_EXACT_REF_FIELD_INVALID", f"{label}.{field}"))
    size_bytes = value.get("size_bytes")
    if isinstance(size_bytes, bool) or not isinstance(size_bytes, int) or size_bytes < 1:
        violations.append(_preflight_violation("PREFLIGHT_EXACT_REF_FIELD_INVALID", f"{label}.size_bytes"))
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(value.get("sha256") or "")):
        violations.append(_preflight_violation("PREFLIGHT_EXACT_REF_FIELD_INVALID", f"{label}.sha256"))
    return violations


def _preflight_violation(code: str, field: str) -> dict[str, object]:
    return {
        "code": code,
        "field": field,
        "writes_authority": False,
    }


def section_scaffold(section_type: str, claim_refs: list[str] | None = None) -> dict[str, Any]:
    """Return a minimal section contract scaffold."""

    normalized = section_type.strip().lower().replace(" ", "_")
    if normalized not in SECTION_TYPES:
        normalized = "custom"
    return {
        "section_type": normalized,
        "purpose": "",
        "reader_question_ref": "",
        "required_claim_refs": claim_refs or [],
        "required_evidence_refs": [],
        "figure_table_refs": [],
        "citation_gap_refs": [],
        "route_back_candidate": "",
    }


def paragraph_job_map_scaffold(
    section_type: str, jobs: list[str] | None = None
) -> list[dict[str, str]]:
    """Return one paragraph slot per job."""

    selected = jobs or list(PARAGRAPH_JOBS)
    return [
        {
            "section_type": section_type,
            "paragraph_job": job,
            "claim_ref": "",
            "evidence_ref": "",
            "citation_action": "",
            "draft_instruction": "",
        }
        for job in selected
    ]


def figure_arc_outline_builder(
    abstract_text: str, figure_claims: list[dict[str, str]]
) -> dict[str, Any]:
    """Build the handling-editor figure arc prompt used by the writing skill."""

    figure_lines = "\n".join(
        f"- {item.get('key', '?')}: {item.get('claim') or item.get('caption', '')}"
        for item in figure_claims
    )
    prompt = (
        "Derive a refs-only paper_narrative_arc_ref from the abstract and "
        "figure claims. Name fig1_hook_ref, figure_moves_ref, missing_panels_ref, "
        "kill_list_ref, and the narrowest prose repair. Do not claim publication "
        "readiness.\n\n"
        f"Abstract:\n{abstract_text.strip()}\n\nFigure claims:\n{figure_lines}"
    )
    return {
        "prompt": prompt,
        "outline": {
            "fig1_hook_ref": "",
            "figure_moves_ref": [],
            "missing_panels_ref": [],
            "kill_list_ref": [],
            "section_repair_refs": [],
            "route_back_candidate": "",
        },
    }


def claim_strength_lint_lite(claims: list[str | dict[str, Any]]) -> list[dict[str, str]]:
    """Flag claims whose wording may be stronger than their evidence label."""

    findings: list[dict[str, str]] = []
    for item in claims:
        if isinstance(item, dict):
            text = str(item.get("claim", ""))
            evidence = str(item.get("evidence_strength", "")).lower()
            ref = str(item.get("claim_ref", ""))
        else:
            text = str(item)
            evidence = ""
            ref = ""
        lowered = text.lower()
        verbs = _matched_terms(lowered, STRONG_VERBS + MODERATE_VERBS + WEAK_VERBS)
        action = "keep"
        if evidence in {"weak", "associational", "descriptive", "missing"} and _matched_terms(
            lowered, STRONG_VERBS
        ):
            action = "downgrade"
        elif not evidence and _matched_terms(lowered, STRONG_VERBS):
            action = "check_evidence_strength"
        findings.append(
            {
                "claim_ref": ref,
                "wording_terms": ", ".join(verbs),
                "evidence_strength": evidence,
                "action": action,
            }
        )
    return findings


def lint_terminology_surface_ledger(
    items: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Flag missing surfaces and unbounded registry terms without judging truth."""

    findings: list[dict[str, object]] = []
    seen_surfaces: set[str] = set()
    for index, item in enumerate(items, start=1):
        surface_kind = str(item.get("surface_kind") or "").strip()
        if surface_kind not in TERMINOLOGY_SURFACES:
            findings.append(
                _terminology_finding(
                    "TERMINOLOGY_SURFACE_UNKNOWN",
                    surface_kind or f"item_{index}",
                    "use one canonical terminology surface kind",
                )
            )
            continue
        seen_surfaces.add(surface_kind)
        if item.get("applicable") is False:
            if not str(item.get("not_applicable_reason") or "").strip():
                findings.append(
                    _terminology_finding(
                        "TERMINOLOGY_NOT_APPLICABLE_REASON_MISSING",
                        surface_kind,
                        "record why this terminology surface does not exist",
                    )
                )
            continue
        text = " ".join(
            str(item.get(field) or "")
            for field in ("text", "label", "header", "identifier", "endpoint")
        )
        normalized = re.sub(r"[_/\-]+", " ", text.lower())
        has_boundary = bool(
            str(item.get("claim_boundary_ref") or "").strip()
            or str(item.get("term_justification_ref") or "").strip()
        )
        if has_boundary:
            continue
        for term in REGISTRY_BOUNDARY_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", normalized):
                findings.append(
                    _terminology_finding(
                        "TERMINOLOGY_BOUNDARY_UNJUSTIFIED",
                        surface_kind,
                        "add a bounded definition or use candidate-audit-signal wording",
                        term=term,
                    )
                )

    for surface_kind in TERMINOLOGY_SURFACES:
        if surface_kind not in seen_surfaces:
            findings.append(
                _terminology_finding(
                    "TERMINOLOGY_SURFACE_MISSING",
                    surface_kind,
                    "add the surface ref to the terminology ledger",
                )
            )
    return sorted(
        findings,
        key=lambda item: (
            str(item["code"]),
            str(item["surface_kind"]),
            str(item.get("term") or ""),
        ),
    )


def lint_reader_facing_workflow_language(
    surfaces: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Flag authoring, workflow, or review-companion prose on reader surfaces."""

    findings: list[dict[str, object]] = []
    for index, surface in enumerate(surfaces, start=1):
        surface_kind = str(surface.get("surface_kind") or "").strip()
        if surface_kind not in READER_FACING_SURFACES:
            continue
        surface_ref = str(surface.get("surface_ref") or f"surface_{index}").strip()
        text = str(surface.get("text") or "")
        for code, pattern, action in READER_SURFACE_PROHIBITIONS:
            match = pattern.search(text)
            if not match:
                continue
            findings.append(
                {
                    "code": code,
                    "surface_kind": surface_kind,
                    "surface_ref": surface_ref,
                    "matched_text": match.group(0),
                    "action": action,
                    "writes_authority": False,
                }
            )
    return findings


def _terminology_finding(
    code: str, surface_kind: str, action: str, *, term: str = ""
) -> dict[str, object]:
    return {
        "code": code,
        "surface_kind": surface_kind,
        "term": term,
        "action": action,
        "writes_authority": False,
    }


def _matched_terms(text: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if re.search(rf"\b{re.escape(term)}\b", text)]


def _self_check() -> None:
    def exact_ref(tag: str) -> dict[str, object]:
        return {
            "kind": "self_check_ref",
            "ref": f"artifact://{tag}",
            "size_bytes": 1,
            "sha256": f"sha256:{tag * 64}",
        }

    def preflight_candidate(
        unresolved_items: Sequence[Mapping[str, object]] = (),
    ) -> dict[str, object]:
        gate_items: dict[str, dict[str, object]] = {
            gate_name: {
                "status": "satisfied",
                "refs": [exact_ref("a")],
                "unresolved_item_ids": [],
                "not_applicable_reason": None,
            }
            for gate_name in INITIAL_DRAFT_PREFLIGHT_GATES
        }
        for item in unresolved_items:
            domain = str(item["domain"])
            gate_items[domain]["status"] = "route_back_required"
            gate_items[domain]["unresolved_item_ids"].append(item["item_id"])
        return {
            "surface_kind": "medical_initial_draft_preflight_candidate_ref",
            "schema_version": 1,
            "manuscript_mode": "initial_complete_draft",
            "status": "route_back_required" if unresolved_items else "satisfied",
            "source_pack_ref": exact_ref("b"),
            "gate_items": gate_items,
            "unresolved_items": list(unresolved_items),
            "earliest_route_back_owner": (
                str(unresolved_items[0]["route_back_owner"])
                if unresolved_items
                else None
            ),
            "not_applicable_reason": None,
            "owner_gate_handoff_ref": exact_ref("c"),
            "authority_boundary": dict(INITIAL_DRAFT_PREFLIGHT_AUTHORITY),
        }

    analysis_gap = {
        "item_id": "analysis-gap",
        "domain": "statistical_integrity",
        "severity": "blocker",
        "finding": "validation tuning is unresolved",
        "evidence_refs": [exact_ref("d")],
        "dependency_tier": "analysis",
        "dependency_rank": 20,
        "route_back_owner": "bounded_analysis_campaign",
        "required_evidence": "validation partition integrity ref",
    }
    authoring_gap = {
        "item_id": "authoring-gap",
        "domain": "story_contract",
        "severity": "major",
        "finding": "the bounded claim is unresolved",
        "evidence_refs": [exact_ref("e")],
        "dependency_tier": "authoring_display",
        "dependency_rank": 30,
        "route_back_owner": "manuscript_authoring",
        "required_evidence": "first draft story contract ref",
    }

    assert "one_sentence_argument_ref" in paper_brief_schema()["required"]
    assert set(first_draft_story_contract_schema()["required"]) == set(
        FIRST_DRAFT_STORY_REFS
    )
    assert set(external_validation_first_draft_contract_schema()["required"]) == set(
        EXTERNAL_VALIDATION_FIRST_DRAFT_REFS
    )
    assert terminology_surface_ledger_schema()["properties"]["authority"] == {
        "const": False
    }
    preflight_schema = medical_initial_draft_preflight_candidate_schema()
    assert preflight_schema["dependency_tiers"] == {
        "baseline_data_citation": 10,
        "analysis": 20,
        "authoring_display": 30,
        "review": 40,
    }
    assert preflight_schema["dependency_owners"] == {
        "baseline_data_citation": "baseline_and_evidence_setup",
        "analysis": "bounded_analysis_campaign",
        "authoring_display": "manuscript_authoring",
        "review": "review_and_quality_gate",
    }
    satisfied_preflight = validate_medical_initial_draft_preflight_candidate(
        preflight_candidate()
    )
    assert satisfied_preflight["machine_check_status"] == "candidate_ref_shape_complete"
    route_back_preflight = validate_medical_initial_draft_preflight_candidate(
        preflight_candidate([analysis_gap, authoring_gap])
    )
    assert route_back_preflight["machine_check_status"] == "candidate_ref_shape_complete"
    assert route_back_preflight["earliest_route_back_owner"] == (
        "bounded_analysis_campaign"
    )

    unprefixed_sha = json.loads(json.dumps(preflight_candidate()))
    unprefixed_sha["source_pack_ref"]["sha256"] = "a" * 64
    unprefixed_codes = {
        item["code"]
        for item in validate_medical_initial_draft_preflight_candidate(unprefixed_sha)[
            "violations"
        ]
    }
    assert "PREFLIGHT_EXACT_REF_FIELD_INVALID" in unprefixed_codes

    zero_byte_ref = json.loads(json.dumps(preflight_candidate()))
    zero_byte_ref["source_pack_ref"]["size_bytes"] = 0
    zero_byte_codes = {
        item["code"]
        for item in validate_medical_initial_draft_preflight_candidate(zero_byte_ref)[
            "violations"
        ]
    }
    assert "PREFLIGHT_EXACT_REF_FIELD_INVALID" in zero_byte_codes

    wrong_rank = json.loads(json.dumps(preflight_candidate([analysis_gap])))
    wrong_rank["unresolved_items"][0]["dependency_rank"] = 30
    wrong_rank_codes = {
        item["code"]
        for item in validate_medical_initial_draft_preflight_candidate(wrong_rank)[
            "violations"
        ]
    }
    assert "PREFLIGHT_DEPENDENCY_RANK_INVALID" in wrong_rank_codes

    wrong_owner = json.loads(json.dumps(preflight_candidate([analysis_gap])))
    wrong_owner["unresolved_items"][0]["route_back_owner"] = (
        "manuscript_authoring"
    )
    wrong_owner["earliest_route_back_owner"] = "manuscript_authoring"
    wrong_owner_audit = validate_medical_initial_draft_preflight_candidate(
        wrong_owner
    )
    assert {
        "PREFLIGHT_DEPENDENCY_OWNER_INVALID",
        "PREFLIGHT_EARLIEST_OWNER_INVALID",
    }.issubset({item["code"] for item in wrong_owner_audit["violations"]})
    assert wrong_owner_audit["earliest_route_back_owner"] == (
        "bounded_analysis_campaign"
    )

    unsorted_preflight = preflight_candidate([authoring_gap, analysis_gap])
    unsorted_preflight["earliest_route_back_owner"] = "bounded_analysis_campaign"
    unsorted_codes = {
        item["code"]
        for item in validate_medical_initial_draft_preflight_candidate(
            unsorted_preflight
        )["violations"]
    }
    assert "PREFLIGHT_UNRESOLVED_DEPENDENCY_ORDER_INVALID" in unsorted_codes
    assert "PREFLIGHT_EARLIEST_OWNER_INVALID" not in unsorted_codes

    wrong_earliest = preflight_candidate([analysis_gap, authoring_gap])
    wrong_earliest["earliest_route_back_owner"] = "manuscript_authoring"
    wrong_earliest_codes = {
        item["code"]
        for item in validate_medical_initial_draft_preflight_candidate(wrong_earliest)[
            "violations"
        ]
    }
    assert "PREFLIGHT_EARLIEST_OWNER_INVALID" in wrong_earliest_codes
    assert section_scaffold("Results")["section_type"] == "results"
    assert paragraph_job_map_scaffold("results", ["result"])[0]["paragraph_job"] == "result"
    assert figure_arc_outline_builder("A.", [{"key": "F1", "claim": "B"}])["outline"][
        "fig1_hook_ref"
    ] == ""
    lint = claim_strength_lint_lite(
        [{"claim_ref": "c1", "claim": "These data prove benefit.", "evidence_strength": "weak"}]
    )
    assert lint[0]["action"] == "downgrade"
    machine_drift = lint_terminology_surface_ledger(
        [
            {
                "surface_kind": "machine_readable_endpoints",
                "identifier": "treatment_gap_intensity_burden",
            }
        ]
    )
    assert {
        (item["code"], item.get("term")) for item in machine_drift
    } >= {
        ("TERMINOLOGY_BOUNDARY_UNJUSTIFIED", "gap"),
        ("TERMINOLOGY_BOUNDARY_UNJUSTIFIED", "intensity"),
        ("TERMINOLOGY_BOUNDARY_UNJUSTIFIED", "burden"),
    }
    complete_ledger = lint_terminology_surface_ledger(
        [
            {
                "surface_kind": surface,
                **(
                    {
                        "applicable": False,
                        "not_applicable_reason": "this paper has no machine endpoint",
                    }
                    if surface == "machine_readable_endpoints"
                    else {"text": "candidate audit signal"}
                ),
            }
            for surface in TERMINOLOGY_SURFACES
        ]
    )
    assert complete_ledger == []
    missing_na_reason = lint_terminology_surface_ledger(
        [
            {
                "surface_kind": surface,
                **(
                    {"applicable": False}
                    if surface == "csv_headers"
                    else {"text": "candidate audit signal"}
                ),
            }
            for surface in TERMINOLOGY_SURFACES
        ]
    )
    assert {item["code"] for item in missing_na_reason} == {
        "TERMINOLOGY_NOT_APPLICABLE_REASON_MISSING"
    }
    assert all(item["writes_authority"] is False for item in machine_drift)
    reader_findings = lint_reader_facing_workflow_language(
        [
            {
                "surface_kind": "manuscript_text",
                "surface_ref": "manuscript.md#declarations",
                "text": "The human study owner must close this explicit human gate.",
            },
            {
                "surface_kind": "table_notes",
                "surface_ref": "T3.md",
                "text": "Report cross-fitted discrimination and calibration.",
            },
            {
                "surface_kind": "supplement",
                "surface_ref": "supplement.pdf",
                "text": "Bounded review display with deterministic sampled rows.",
            },
            {
                "surface_kind": "audit_receipt",
                "surface_ref": "audit.json",
                "text": "runtime_authority=false",
            },
        ]
    )
    assert {item["code"] for item in reader_findings} == {
        "INTERNAL_WORKFLOW_LANGUAGE_IN_READER_SURFACE",
        "AUTHORING_INSTRUCTION_IN_READER_SURFACE",
        "INTERNAL_REVIEW_LANGUAGE_IN_READER_SURFACE",
    }
    assert all(item["writes_authority"] is False for item in reader_findings)
    print(json.dumps({"ok": True, "checks": 23}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
