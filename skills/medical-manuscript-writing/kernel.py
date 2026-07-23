"""Deterministic refs-only helpers for medical manuscript writing.

These helpers scaffold prompts, schemas, and lint hints. They do not create
MAS truth, owner receipts, typed blockers, artifacts, or publication readiness.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
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

FIXED_HORIZON_FIRST_DRAFT_REFS = (
    "fixed_horizon_risk_semantics_ref",
)

ANOMALY_SENSITIVITY_FIRST_DRAFT_REFS = (
    "anomaly_sensitivity_ref",
)

VERIFICATION_SCOPE_FIRST_DRAFT_REFS = (
    "verification_scope_contract_ref",
)

EXTERNAL_VALIDATION_FIRST_DRAFT_REFS = (
    "source_model_provenance_ref",
    "target_population_and_followup_ref",
    "construct_comparability_ref",
    "calibration_and_performance_ref",
    "claim_family_scope_qualifier_ref",
    "claim_guardrail_ref",
    "negative_or_non_estimable_result_ref",
)

PAPER_FACING_DISPLAY_FIRST_DRAFT_REFS = (
    "structured_display_source_map_ref",
    "renderer_provenance_ref",
)

AUTHORING_FREEZE_INPUT_REFS = (
    "medical_initial_draft_preflight_candidate_ref",
    "manuscript_ref",
    "structured_evidence_ref",
    "claim_map_ref",
    "table_bundle_ref",
    "figure_bundle_ref",
    "renderer_provenance_ref",
)

INITIAL_DRAFT_SPECIALIST_REF_ROUTES = {
    "fixed_horizon_risk_semantics_ref": {
        "producer": "medical-survival-analysis-plan",
        "consumers": ("medical-statistical-review", "medical-manuscript-writing"),
    },
    "anomaly_sensitivity_ref": {
        "producer": "medical-statistical-review",
        "consumers": ("medical-manuscript-writing", "medical-manuscript-review"),
    },
    "verification_scope_contract_ref": {
        "producer": "medical-statistical-review",
        "consumers": (
            "medical-evidence-integrity-reviewer",
            "medical-manuscript-writing",
        ),
    },
    "construct_comparability_ref": {
        "producer": "medical-risk-model-transportability-reviewer",
        "consumers": (
            "medical-evidence-integrity-reviewer",
            "medical-manuscript-writing",
        ),
    },
    "claim_family_scope_qualifier_ref": {
        "producer": "medical-risk-model-transportability-reviewer",
        "consumers": (
            "medical-evidence-integrity-reviewer",
            "medical-manuscript-writing",
        ),
    },
    "structured_display_source_map_ref": {
        "producer": "medical-manuscript-writing",
        "consumers": ("medical-manuscript-review",),
    },
    "renderer_provenance_ref": {
        "producer": "medical-manuscript-writing",
        "consumers": ("medical-manuscript-review",),
    },
}

AUTHORING_FREEZE_HANDOFF_ROUTE = {
    "producer": "medical-manuscript-writing",
    "consumers": ("medical-manuscript-review", "consuming_domain_owner"),
    "refs_only": True,
    "writes_authority": False,
    "signs_review_currentness": False,
}

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

INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES = {
    "study_identity": ("study_charter_ref", "paper_identity_ref"),
    "data_freeze": ("clinical_analysis_input_identity_ref",),
    "statistical_integrity": (
        "validation_partition_integrity_ref",
        "endpoint_analysis_set_reconciliation_ref",
        "model_complexity_sparse_event_ref",
        "linked_prediction_performance_ref",
    ),
    "citation_integrity": (
        "citation_source_coverage_ref",
        "active_reference_currentness_ref",
        "excluded_reference_ledger_ref",
        "claim_citation_edge_completeness_ref",
        "reference_lane_active_inventory_binding_ref",
    ),
    "table_traceability": ("baseline_table_traceability_ref",),
    "display_scope": (
        "document_display_scope_coverage_ref",
        "display_render_integrity_ref",
    ),
    "story_contract": ("first_draft_story_contract_ref",),
}

INITIAL_DRAFT_PREFLIGHT_GATE_REF_ALTERNATIVES = {
    "statistical_integrity": (
        ("fixed_horizon_risk_semantics_ref", "fixed_horizon_not_applicable_ref"),
        ("decision_curve_validity_ref", "decision_curve_not_applicable_ref"),
    ),
}

INITIAL_DRAFT_APPLICABILITY_DISPOSITION_SURFACE_KIND = (
    "medical_initial_draft_applicability_disposition_candidate.v1"
)
INITIAL_DRAFT_APPLICABILITY_DISPOSITION_TARGETS = {
    "fixed_horizon_not_applicable_ref": "fixed_horizon_risk_semantics_ref",
    "decision_curve_not_applicable_ref": "decision_curve_validity_ref",
}

INITIAL_DRAFT_PREFLIGHT_MANUSCRIPT_MODE_APPLICABILITY = {
    "initial_complete_draft": {
        gate_name: "required" for gate_name in INITIAL_DRAFT_PREFLIGHT_GATES
    },
}

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
AUTHORING_SNAPSHOT_MANIFEST_LOCATOR_FIELDS = frozenset({"kind", "locator"})
AUTHORING_SNAPSHOT_MANIFEST_KIND = "authoring_candidate_snapshot_manifest"

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

AUTHOR_INPUT_ANNOTATION_RE = re.compile(r"\[AUTHOR INPUT: [^\[\]\r\n]+\]")
AUTHOR_INPUT_SURFACES = frozenset(
    {
        "manuscript_text",
        "title_page",
        "declarations",
        "cover_letter",
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
    (
        "DEFENSIVE_AUTHOR_INPUT_META_PROSE",
        re.compile(
            r"(?:status\s*:\s*(?:author|owner|institutional)[^.\n]{0,40}"
            r"(?:input|confirmation)\s+required|title page placeholder|"
            r"(?:frozen|current) candidate (?:does not establish|contains no verified)|"
            r"(?:manuscript|paper) (?:is|remains) (?:not |un)?ready [^.\n]{0,80}"
            r"(?:missing|unknown|unavailable)|"
            r"(?:author|institutional) (?:information|details|facts) "
            r"(?:are|remain) (?:unknown|unavailable))",
            re.IGNORECASE,
        ),
        "write in the authors' voice and replace the meta-commentary with one local [AUTHOR INPUT: ...] annotation",
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


def applicable_initial_draft_specialist_refs(
    *,
    fixed_horizon: bool,
    external_validation: bool,
    paper_facing_displays: bool,
    analysis_input_anomalies: bool = False,
) -> tuple[str, ...]:
    """Return specialist refs only for applicable fixed-horizon or validation drafts."""

    refs: list[str] = []
    if fixed_horizon:
        refs.extend(FIXED_HORIZON_FIRST_DRAFT_REFS)
    if external_validation:
        refs.extend(EXTERNAL_VALIDATION_FIRST_DRAFT_REFS)
    if fixed_horizon or external_validation:
        refs.extend(VERIFICATION_SCOPE_FIRST_DRAFT_REFS)
    if (fixed_horizon or external_validation) and analysis_input_anomalies:
        refs.extend(ANOMALY_SENSITIVITY_FIRST_DRAFT_REFS)
    if (fixed_horizon or external_validation) and paper_facing_displays:
        refs.extend(PAPER_FACING_DISPLAY_FIRST_DRAFT_REFS)
    return tuple(dict.fromkeys(refs))


def audit_applicable_initial_draft_specialist_refs(
    candidate_refs: Mapping[str, object] | Sequence[str],
    *,
    fixed_horizon: bool,
    external_validation: bool,
    paper_facing_displays: bool,
    analysis_input_anomalies: bool = False,
) -> dict[str, Any]:
    """Audit applicable specialist ref names without changing the v1 preflight shape."""

    present = (
        {str(key) for key in candidate_refs}
        if isinstance(candidate_refs, Mapping)
        else {str(value) for value in candidate_refs}
    )
    required = applicable_initial_draft_specialist_refs(
        fixed_horizon=fixed_horizon,
        external_validation=external_validation,
        paper_facing_displays=paper_facing_displays,
        analysis_input_anomalies=analysis_input_anomalies,
    )
    missing = [ref for ref in required if ref not in present]
    return {
        "surface_kind": "initial_draft_specialist_ref_audit_candidate.v1",
        "applicability": {
            "fixed_horizon": fixed_horizon,
            "external_validation": external_validation,
            "paper_facing_displays": paper_facing_displays,
            "analysis_input_anomalies": analysis_input_anomalies,
        },
        "required_refs": list(required),
        "missing_refs": missing,
        "producer_consumer_routes": {
            ref: INITIAL_DRAFT_SPECIALIST_REF_ROUTES[ref]
            for ref in required
            if ref in INITIAL_DRAFT_SPECIALIST_REF_ROUTES
        },
        "machine_check_status": (
            "candidate_ref_names_complete" if not missing else "route_back_required"
        ),
        "route_back_candidate": None
        if not missing
        else {
            "route": INITIAL_DRAFT_SPECIALIST_REF_ROUTES.get(
                missing[0], {"producer": "manuscript_authoring"}
            )["producer"],
            "reason": "applicable_initial_draft_specialist_ref_missing",
            "authority": False,
        },
        "authority": False,
    }


def external_validation_first_draft_contract_schema(
    *,
    fixed_horizon: bool = False,
    paper_facing_displays: bool = True,
    analysis_input_anomalies: bool = False,
) -> dict[str, Any]:
    """Return the specialist inputs required before external-validation prose."""

    required_refs = applicable_initial_draft_specialist_refs(
        fixed_horizon=fixed_horizon,
        external_validation=True,
        paper_facing_displays=paper_facing_displays,
        analysis_input_anomalies=analysis_input_anomalies,
    )
    return {
        "type": "object",
        "required": list(required_refs),
        "properties": {
            ref: {"type": "string"} for ref in required_refs
        }
        | {
            "route_back_candidate": {"type": "object"},
            "authority": {"const": False},
        },
    }


def build_authoring_freeze_handoff_candidate(
    candidate_refs: Mapping[str, object],
    *,
    preflight_candidate: Mapping[str, object],
    snapshot_manifest_locator: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    """Freeze generated draft inputs for review only after preflight succeeds."""

    missing = [ref for ref in AUTHORING_FREEZE_INPUT_REFS if ref not in candidate_refs]
    ref_violations: dict[str, list[dict[str, object]]] = {}
    for ref_name in AUTHORING_FREEZE_INPUT_REFS:
        if ref_name not in candidate_refs:
            continue
        violations = _validate_exact_ref(candidate_refs[ref_name], ref_name)
        if violations:
            ref_violations[ref_name] = violations
    manifest_locator_findings = _validate_authoring_snapshot_manifest_locator(
        snapshot_manifest_locator
    )
    normalized_manifest_locator = (
        {
            "kind": str(snapshot_manifest_locator["kind"]).strip(),
            "locator": str(snapshot_manifest_locator["locator"]).strip(),
        }
        if not manifest_locator_findings and snapshot_manifest_locator is not None
        else None
    )

    preflight_audit = validate_medical_initial_draft_preflight_candidate(
        preflight_candidate
    )
    preflight_satisfied = (
        preflight_audit["machine_check_status"] == "candidate_ref_shape_complete"
        and preflight_candidate.get("status") == "satisfied"
        and not preflight_candidate.get("unresolved_items")
    )
    if missing or ref_violations or manifest_locator_findings or not preflight_satisfied:
        return {
            "surface_kind": "authoring_freeze_handoff_audit_candidate.v1",
            "machine_check_status": "route_back_required",
            "missing_refs": missing,
            "invalid_ref_findings": ref_violations,
            "snapshot_manifest_locator_findings": manifest_locator_findings,
            "preflight_satisfied": preflight_satisfied,
            "immutable_candidate_snapshot_ref": None,
            "immutable_candidate_snapshot_manifest_locator": normalized_manifest_locator,
            "producer_consumer_route": dict(AUTHORING_FREEZE_HANDOFF_ROUTE),
            "route_back_candidate": {
                "route": "medical-manuscript-writing",
                "reason": "authoring_candidate_not_ready_to_freeze",
                "authority": False,
            },
            "authority": False,
        }

    frozen_inputs = {
        ref_name: dict(candidate_refs[ref_name])
        for ref_name in AUTHORING_FREEZE_INPUT_REFS
    }
    payload = json.dumps(
        frozen_inputs,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    snapshot_sha256 = hashlib.sha256(payload).hexdigest()
    return {
        "surface_kind": "authoring_freeze_handoff_audit_candidate.v1",
        "machine_check_status": "candidate_frozen_for_independent_review",
        "missing_refs": [],
        "invalid_ref_findings": {},
        "snapshot_manifest_locator_findings": [],
        "preflight_satisfied": True,
        "immutable_candidate_snapshot_ref": {
            "kind": "immutable_candidate_snapshot_ref",
            "ref": f"opl-content://sha256/{snapshot_sha256}",
            "size_bytes": len(payload),
            "sha256": f"sha256:{snapshot_sha256}",
        },
        "immutable_candidate_snapshot_manifest_locator": normalized_manifest_locator,
        "frozen_input_refs": frozen_inputs,
        "producer_consumer_route": dict(AUTHORING_FREEZE_HANDOFF_ROUTE),
        "route_back_candidate": None,
        "authority": False,
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


def medical_initial_draft_applicability_disposition_schema() -> dict[str, Any]:
    """Return the versioned no-authority applicability disposition schema."""

    return {
        "surface_kind": INITIAL_DRAFT_APPLICABILITY_DISPOSITION_SURFACE_KIND,
        "schema_version": 1,
        "required": [
            "surface_kind",
            "schema_version",
            "target_ref_kind",
            "status",
            "reason",
            "evidence_ref",
            "authority",
        ],
        "target_ref_kinds": sorted(
            INITIAL_DRAFT_APPLICABILITY_DISPOSITION_TARGETS.values()
        ),
        "status": "not_applicable_with_reason",
        "authority": False,
    }


def build_medical_initial_draft_applicability_disposition(
    target_ref_kind: str,
    reason: str,
    evidence_ref: Mapping[str, object],
) -> dict[str, object]:
    """Build a deterministic disposition candidate without creating authority."""

    candidate: dict[str, object] = {
        "surface_kind": INITIAL_DRAFT_APPLICABILITY_DISPOSITION_SURFACE_KIND,
        "schema_version": 1,
        "target_ref_kind": target_ref_kind,
        "status": "not_applicable_with_reason",
        "reason": reason,
        "evidence_ref": dict(evidence_ref),
        "authority": False,
    }
    audit = validate_medical_initial_draft_applicability_disposition(candidate)
    if audit["machine_check_status"] != "candidate_complete":
        raise ValueError("invalid medical initial-draft applicability disposition")
    return candidate


def validate_medical_initial_draft_applicability_disposition(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Validate disposition content while preserving the no-authority boundary."""

    violations: list[dict[str, object]] = []
    expected_fields = set(
        medical_initial_draft_applicability_disposition_schema()["required"]
    )
    _check_exact_fields(candidate, expected_fields, "candidate", violations)
    if (
        candidate.get("surface_kind")
        != INITIAL_DRAFT_APPLICABILITY_DISPOSITION_SURFACE_KIND
    ):
        violations.append(
            _preflight_violation(
                "PREFLIGHT_DISPOSITION_SURFACE_KIND_INVALID", "surface_kind"
            )
        )
    if candidate.get("schema_version") != 1:
        violations.append(
            _preflight_violation(
                "PREFLIGHT_DISPOSITION_SCHEMA_VERSION_INVALID", "schema_version"
            )
        )
    if candidate.get("target_ref_kind") not in set(
        INITIAL_DRAFT_APPLICABILITY_DISPOSITION_TARGETS.values()
    ):
        violations.append(
            _preflight_violation(
                "PREFLIGHT_DISPOSITION_TARGET_REF_KIND_INVALID", "target_ref_kind"
            )
        )
    if candidate.get("status") != "not_applicable_with_reason":
        violations.append(
            _preflight_violation(
                "PREFLIGHT_DISPOSITION_STATUS_INVALID", "status"
            )
        )
    if not str(candidate.get("reason") or "").strip():
        violations.append(
            _preflight_violation(
                "PREFLIGHT_DISPOSITION_REASON_MISSING", "reason"
            )
        )
    violations.extend(_validate_exact_ref(candidate.get("evidence_ref"), "evidence_ref"))
    if candidate.get("authority") is not False:
        violations.append(
            _preflight_violation(
                "PREFLIGHT_DISPOSITION_AUTHORITY_FORBIDDEN", "authority"
            )
        )
    violations.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not violations
    return {
        "surface_kind": "medical_initial_draft_applicability_disposition_audit.v1",
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "violations": violations,
        "authority": False,
    }


def medical_initial_draft_applicability_disposition_exact_ref(
    candidate: Mapping[str, object], ref: str
) -> dict[str, object]:
    """Bind a validated disposition candidate to its canonical content identity."""

    audit = validate_medical_initial_draft_applicability_disposition(candidate)
    if audit["machine_check_status"] != "candidate_complete" or not ref.strip():
        raise ValueError("cannot bind an invalid applicability disposition")
    target_ref_kind = str(candidate["target_ref_kind"])
    alias_kind = next(
        alias
        for alias, target in INITIAL_DRAFT_APPLICABILITY_DISPOSITION_TARGETS.items()
        if target == target_ref_kind
    )
    payload = _medical_initial_draft_applicability_disposition_payload(candidate)
    return {
        "kind": alias_kind,
        "ref": ref.strip(),
        "size_bytes": len(payload),
        "sha256": f"sha256:{hashlib.sha256(payload).hexdigest()}",
    }


def _medical_initial_draft_applicability_disposition_payload(
    candidate: Mapping[str, object],
) -> bytes:
    return json.dumps(
        candidate, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def medical_initial_draft_preflight_candidate_schema() -> dict[str, Any]:
    """Return the stable v1 structural preflight contract locator."""

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


def medical_initial_draft_preflight_candidate_schema_v2() -> dict[str, Any]:
    """Return the strict v2 semantic policy over the stable v1 JSON shape."""

    return {
        **medical_initial_draft_preflight_candidate_schema(),
        "semantic_policy_id": "scholarskills_medical_initial_draft_preflight.v2",
        "required_gate_ref_families": {
            gate: list(refs)
            for gate, refs in INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES.items()
        },
        "conditional_gate_ref_alternatives": {
            gate: [list(group) for group in groups]
            for gate, groups in INITIAL_DRAFT_PREFLIGHT_GATE_REF_ALTERNATIVES.items()
        },
    }


def validate_medical_initial_draft_preflight_candidate(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Validate the stable v1 preflight semantics for same-major callers."""

    return _validate_medical_initial_draft_preflight_candidate(
        candidate, strict_v2=False, applicability_disposition_candidates=None
    )


def validate_medical_initial_draft_preflight_candidate_v2(
    candidate: Mapping[str, object],
    *,
    applicability_disposition_candidates: Mapping[
        str, Mapping[str, object]
    ] | None = None,
) -> dict[str, Any]:
    """Validate v2 ref-family and initial-complete-draft semantics."""

    return _validate_medical_initial_draft_preflight_candidate(
        candidate,
        strict_v2=True,
        applicability_disposition_candidates=applicability_disposition_candidates,
    )


def _validate_medical_initial_draft_preflight_candidate(
    candidate: Mapping[str, object],
    *,
    strict_v2: bool,
    applicability_disposition_candidates: Mapping[
        str, Mapping[str, object]
    ] | None,
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
    manuscript_mode = str(candidate.get("manuscript_mode") or "").strip()
    applicability = (
        INITIAL_DRAFT_PREFLIGHT_MANUSCRIPT_MODE_APPLICABILITY.get(manuscript_mode)
        if strict_v2
        else {}
    )
    if strict_v2 and applicability is None:
        violations.append(
            _preflight_violation(
                "PREFLIGHT_MANUSCRIPT_MODE_INVALID", "manuscript_mode"
            )
        )
        applicability = {}
    elif not strict_v2 and not manuscript_mode:
        violations.append(
            _preflight_violation(
                "PREFLIGHT_MANUSCRIPT_MODE_MISSING", "manuscript_mode"
            )
        )

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
    disposition_identities: set[tuple[str, str]] = set()
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
            if strict_v2:
                ref_kinds = {
                    str(ref.get("kind") or "").strip()
                    for ref in refs
                    if isinstance(ref, Mapping)
                }
                for required_kind in INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES.get(
                    gate_name, ()
                ):
                    if required_kind not in ref_kinds:
                        violations.append(
                            _preflight_violation(
                                "PREFLIGHT_REQUIRED_REF_FAMILY_MISSING",
                                f"{label}.refs[{required_kind}]",
                            )
                        )
                for alternatives in INITIAL_DRAFT_PREFLIGHT_GATE_REF_ALTERNATIVES.get(
                    gate_name, ()
                ):
                    alternative_instances = [
                        (ref_index, ref)
                        for ref_index, ref in enumerate(refs)
                        if isinstance(ref, Mapping)
                        and ref.get("kind") in set(alternatives)
                    ]
                    if not alternative_instances:
                        violations.append(
                            _preflight_violation(
                                "PREFLIGHT_CONDITIONAL_REF_DISPOSITION_MISSING",
                                f"{label}.refs[{'|'.join(alternatives)}]",
                            )
                        )
                    elif len(alternative_instances) > 1:
                        violations.append(
                            _preflight_violation(
                                "PREFLIGHT_CONDITIONAL_REF_ALTERNATIVES_NOT_EXCLUSIVE",
                                f"{label}.refs[{'|'.join(alternatives)}]",
                            )
                        )
                    for ref_index, ref in alternative_instances:
                        if ref.get("kind") not in set(
                            INITIAL_DRAFT_APPLICABILITY_DISPOSITION_TARGETS
                        ):
                            continue
                        locator = str(ref.get("ref") or "")
                        disposition = (
                            applicability_disposition_candidates.get(locator)
                            if isinstance(
                                applicability_disposition_candidates, Mapping
                            )
                            else None
                        )
                        if isinstance(disposition, Mapping):
                            disposition_identity = (
                                str(disposition.get("target_ref_kind") or ""),
                                "sha256:"
                                + hashlib.sha256(
                                    _medical_initial_draft_applicability_disposition_payload(
                                        disposition
                                    )
                                ).hexdigest(),
                            )
                            if disposition_identity in disposition_identities:
                                violations.append(
                                    _preflight_violation(
                                        "PREFLIGHT_APPLICABILITY_DISPOSITION_REUSED",
                                        f"{label}.refs[{ref_index}]",
                                    )
                                )
                            disposition_identities.add(disposition_identity)
                        violations.extend(
                            _validate_applicability_disposition_binding(
                                ref,
                                applicability_disposition_candidates,
                                f"{label}.refs[{ref_index}]",
                            )
                        )
            if unresolved_ids or na_reason is not None:
                violations.append(_preflight_violation("PREFLIGHT_SATISFIED_GATE_CONTRADICTORY", label))
        elif gate_status == "route_back_required":
            if not unresolved_ids or na_reason is not None:
                violations.append(_preflight_violation("PREFLIGHT_ROUTE_BACK_GATE_INCOMPLETE", label))
        elif gate_status == "not_applicable_with_reason":
            if unresolved_ids or not str(na_reason or "").strip():
                violations.append(_preflight_violation("PREFLIGHT_NOT_APPLICABLE_GATE_REASON_MISSING", label))
            if strict_v2 and applicability.get(gate_name) == "required":
                violations.append(
                    _preflight_violation(
                        "PREFLIGHT_REQUIRED_GATE_NOT_APPLICABLE",
                        f"{label}.status",
                    )
                )

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
        if strict_v2:
            required_na_gates = sorted(
                gate_name
                for gate_name, gate in gate_items.items()
                if applicability.get(gate_name) == "required"
                and isinstance(gate, Mapping)
                and gate.get("status") == "not_applicable_with_reason"
            )
            if required_na_gates:
                violation = _preflight_violation(
                    "PREFLIGHT_SATISFIED_REQUIRED_GATE_NOT_APPLICABLE", "status"
                )
                violation["gate_names"] = required_na_gates
                violations.append(violation)
    elif status == "not_applicable_with_reason":
        if unresolved_items or earliest_owner is not None or not str(top_na_reason or "").strip():
            violations.append(_preflight_violation("PREFLIGHT_NOT_APPLICABLE_STATE_INVALID", "status"))

    authority = candidate.get("authority_boundary")
    if not isinstance(authority, Mapping) or dict(authority) != INITIAL_DRAFT_PREFLIGHT_AUTHORITY:
        violations.append(_preflight_violation("PREFLIGHT_AUTHORITY_BOUNDARY_INVALID", "authority_boundary"))

    violations.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not violations
    return {
        "surface_kind": (
            "medical_initial_draft_preflight_kernel_audit_candidate.v2"
            if strict_v2
            else "medical_initial_draft_preflight_kernel_audit_candidate.v1"
        ),
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


def _validate_authoring_snapshot_manifest_locator(
    value: object,
) -> list[dict[str, object]]:
    if not isinstance(value, Mapping) or set(value) != AUTHORING_SNAPSHOT_MANIFEST_LOCATOR_FIELDS:
        return [
            _preflight_violation(
                "AUTHORING_SNAPSHOT_MANIFEST_LOCATOR_INVALID",
                "snapshot_manifest_locator",
            )
        ]
    if (
        str(value.get("kind") or "").strip() != AUTHORING_SNAPSHOT_MANIFEST_KIND
        or not str(value.get("locator") or "").strip()
    ):
        return [
            _preflight_violation(
                "AUTHORING_SNAPSHOT_MANIFEST_LOCATOR_INVALID",
                "snapshot_manifest_locator",
            )
        ]
    return []


def _validate_applicability_disposition_binding(
    ref_value: Mapping[str, object],
    disposition_candidates: Mapping[str, Mapping[str, object]] | None,
    label: str,
) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    alias_kind = str(ref_value.get("kind") or "")
    expected_target = INITIAL_DRAFT_APPLICABILITY_DISPOSITION_TARGETS.get(alias_kind)
    locator = str(ref_value.get("ref") or "")
    if expected_target is None:
        return violations
    disposition = (
        disposition_candidates.get(locator)
        if isinstance(disposition_candidates, Mapping)
        else None
    )
    if not isinstance(disposition, Mapping):
        return [
            _preflight_violation(
                "PREFLIGHT_APPLICABILITY_DISPOSITION_CANDIDATE_MISSING", label
            )
        ]
    audit = validate_medical_initial_draft_applicability_disposition(disposition)
    if audit["machine_check_status"] != "candidate_complete":
        violation = _preflight_violation(
            "PREFLIGHT_APPLICABILITY_DISPOSITION_CANDIDATE_INVALID", label
        )
        violation["candidate_violation_codes"] = sorted(
            {str(item["code"]) for item in audit["violations"]}
        )
        violations.append(violation)
        return violations
    if disposition.get("target_ref_kind") != expected_target:
        violations.append(
            _preflight_violation(
                "PREFLIGHT_APPLICABILITY_DISPOSITION_TARGET_MISMATCH", label
            )
        )
        return violations
    expected_ref = medical_initial_draft_applicability_disposition_exact_ref(
        disposition, locator
    )
    if dict(ref_value) != expected_ref:
        violations.append(
            _preflight_violation(
                "PREFLIGHT_APPLICABILITY_DISPOSITION_IDENTITY_MISMATCH", label
            )
        )
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


def validate_author_input_registry(
    registry: Mapping[str, object],
    surfaces: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Validate exact author-input annotation closure without claiming authority."""

    findings: list[dict[str, object]] = []
    items = registry.get("items")
    if (
        registry.get("surface_kind") != "medical_author_input_registry.v1"
        or registry.get("schema_version") != 1
        or not isinstance(items, list)
    ):
        findings.append(
            _author_input_finding(
                "AUTHOR_INPUT_REGISTRY_SHAPE_INVALID",
                "registry",
                "use the v1 registry shape with an items array",
            )
        )
        items = []

    surface_index: dict[tuple[str, str], str] = {}
    for index, surface in enumerate(surfaces, start=1):
        surface_kind = str(surface.get("surface_kind") or "").strip()
        surface_ref = str(surface.get("surface_ref") or f"surface_{index}").strip()
        key = (surface_kind, surface_ref)
        if key in surface_index:
            findings.append(
                _author_input_finding(
                    "AUTHOR_INPUT_SURFACE_DUPLICATE",
                    f"{surface_kind}:{surface_ref}",
                    "provide each reader-facing surface exactly once",
                )
            )
            continue
        surface_index[key] = str(surface.get("text") or "")

    item_ids: set[str] = set()
    placement_ids: set[str] = set()
    registered_by_surface: dict[tuple[str, str], list[str]] = defaultdict(list)
    item_count = 0
    placement_count = 0
    main_count = 0
    supporting_count = 0
    for item_index, item in enumerate(items, start=1):
        item_count += 1
        if not isinstance(item, Mapping):
            findings.append(
                _author_input_finding(
                    "AUTHOR_INPUT_ITEM_INVALID",
                    f"items[{item_index}]",
                    "use an object for every grouped input item",
                )
            )
            continue
        item_id = str(item.get("id") or "").strip()
        required_fields = ("category", "required_input", "responsible_owner")
        if (
            not item_id
            or item_id in item_ids
            or any(not str(item.get(field) or "").strip() for field in required_fields)
        ):
            findings.append(
                _author_input_finding(
                    "AUTHOR_INPUT_ITEM_ID_OR_FIELD_INVALID",
                    item_id or f"items[{item_index}]",
                    "use a unique stable id and complete objective-fact fields",
                )
            )
        item_ids.add(item_id)
        placements = item.get("placements")
        if not isinstance(placements, list):
            findings.append(
                _author_input_finding(
                    "AUTHOR_INPUT_PLACEMENTS_INVALID",
                    item_id or f"items[{item_index}]",
                    "provide a placements array, which may be empty only for package-only inputs",
                )
            )
            continue
        for placement_index, placement in enumerate(placements, start=1):
            placement_count += 1
            if not isinstance(placement, Mapping):
                findings.append(
                    _author_input_finding(
                        "AUTHOR_INPUT_PLACEMENT_INVALID",
                        f"{item_id}.placements[{placement_index}]",
                        "use an object for every placement",
                    )
                )
                continue
            placement_id = str(placement.get("placement_id") or "").strip()
            surface_kind = str(placement.get("surface_kind") or "").strip()
            surface_ref = str(placement.get("surface_ref") or "").strip()
            annotation = str(placement.get("exact_annotation") or "")
            if (
                not placement_id
                or placement_id in placement_ids
                or surface_kind not in AUTHOR_INPUT_SURFACES
                or not surface_ref
                or AUTHOR_INPUT_ANNOTATION_RE.fullmatch(annotation) is None
            ):
                findings.append(
                    _author_input_finding(
                        "AUTHOR_INPUT_PLACEMENT_FIELDS_INVALID",
                        placement_id or f"{item_id}.placements[{placement_index}]",
                        "bind a unique placement id, supported surface, ref, and exact [AUTHOR INPUT: ...] annotation",
                    )
                )
                continue
            placement_ids.add(placement_id)
            key = (surface_kind, surface_ref)
            registered_by_surface[key].append(annotation)
            if surface_kind == "manuscript_text":
                main_count += 1
            else:
                supporting_count += 1
            text = surface_index.get(key)
            if text is None:
                findings.append(
                    _author_input_finding(
                        "AUTHOR_INPUT_SURFACE_MISSING",
                        placement_id,
                        "provide the exact registered surface for validation",
                    )
                )
                continue
            occurrences = text.count(annotation)
            if occurrences != 1:
                findings.append(
                    _author_input_finding(
                        "AUTHOR_INPUT_ANNOTATION_CARDINALITY_INVALID",
                        placement_id,
                        f"require the exact registered annotation once, observed {occurrences}",
                    )
                )
    for key, text in surface_index.items():
        actual = AUTHOR_INPUT_ANNOTATION_RE.findall(text)
        expected = registered_by_surface.get(key, [])
        for annotation in sorted(set(actual) - set(expected)):
            findings.append(
                _author_input_finding(
                    "AUTHOR_INPUT_ANNOTATION_ORPHANED",
                    f"{key[0]}:{key[1]}",
                    f"register or remove orphan annotation {annotation}",
                )
            )
        if len(actual) != len(expected):
            findings.append(
                _author_input_finding(
                    "AUTHOR_INPUT_SURFACE_COUNT_MISMATCH",
                    f"{key[0]}:{key[1]}",
                    f"expected {len(expected)} annotations, observed {len(actual)}",
                )
            )

    declared_counts = registry.get("counts")
    expected_counts = {
        "grouped_item_count": item_count,
        "placement_count": placement_count,
        "main_manuscript_annotation_count": main_count,
        "supporting_document_annotation_count": supporting_count,
    }
    if declared_counts != expected_counts:
        findings.append(
            _author_input_finding(
                "AUTHOR_INPUT_DECLARED_COUNTS_MISMATCH",
                "counts",
                f"declare exact counts {expected_counts}",
            )
        )

    findings.sort(key=lambda item: (str(item["code"]), str(item["surface_ref"])))
    return {
        "surface_kind": "medical_author_input_registry_audit_candidate.v1",
        "machine_check_status": "candidate_complete" if not findings else "route_back_required",
        "counts": expected_counts,
        "findings": findings,
        "authority": False,
    }


def _author_input_finding(
    code: str, surface_ref: str, action: str
) -> dict[str, object]:
    return {
        "code": code,
        "surface_ref": surface_ref,
        "action": action,
        "writes_authority": False,
    }


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
    def exact_ref(tag: str, *, kind: str = "self_check_ref") -> dict[str, object]:
        return {
            "kind": kind,
            "ref": f"artifact://{tag}",
            "size_bytes": 1,
            "sha256": f"sha256:{tag * 64}",
        }

    def preflight_candidate(
        unresolved_items: Sequence[Mapping[str, object]] = (),
    ) -> dict[str, object]:
        gate_items: dict[str, dict[str, object]] = {}
        tag_index = 0
        for gate_name in INITIAL_DRAFT_PREFLIGHT_GATES:
            required_kinds = list(
                INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES[gate_name]
            )
            required_kinds.extend(
                alternatives[0]
                for alternatives in INITIAL_DRAFT_PREFLIGHT_GATE_REF_ALTERNATIVES.get(
                    gate_name, ()
                )
            )
            refs = []
            for kind in required_kinds:
                tag = format(tag_index % 16, "x")
                tag_index += 1
                refs.append(exact_ref(tag, kind=kind))
            gate_items[gate_name] = {
                "status": "satisfied",
                "refs": refs,
                "unresolved_item_ids": [],
                "not_applicable_reason": None,
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
    ordinary_audit = audit_applicable_initial_draft_specialist_refs(
        {},
        fixed_horizon=False,
        external_validation=False,
        paper_facing_displays=True,
        analysis_input_anomalies=False,
    )
    assert ordinary_audit["required_refs"] == []
    assert ordinary_audit["machine_check_status"] == "candidate_ref_names_complete"
    fixed_horizon_required = applicable_initial_draft_specialist_refs(
        fixed_horizon=True,
        external_validation=False,
        paper_facing_displays=False,
        analysis_input_anomalies=False,
    )
    assert fixed_horizon_required == (
        *FIXED_HORIZON_FIRST_DRAFT_REFS,
        *VERIFICATION_SCOPE_FIRST_DRAFT_REFS,
    )
    assert "immutable_candidate_snapshot_ref" not in fixed_horizon_required
    non_horizon_external_required = set(
        applicable_initial_draft_specialist_refs(
            fixed_horizon=False,
            external_validation=True,
            paper_facing_displays=False,
            analysis_input_anomalies=False,
        )
    )
    assert "fixed_horizon_risk_semantics_ref" not in non_horizon_external_required
    assert "anomaly_sensitivity_ref" not in non_horizon_external_required
    assert "verification_scope_contract_ref" in non_horizon_external_required
    assert "construct_comparability_ref" in non_horizon_external_required
    assert "immutable_candidate_snapshot_ref" not in non_horizon_external_required
    external_required = set(
        external_validation_first_draft_contract_schema(
            fixed_horizon=True,
            paper_facing_displays=True,
            analysis_input_anomalies=True,
        )["required"]
    )
    assert external_required == {
        *FIXED_HORIZON_FIRST_DRAFT_REFS,
        *ANOMALY_SENSITIVITY_FIRST_DRAFT_REFS,
        *VERIFICATION_SCOPE_FIRST_DRAFT_REFS,
        *EXTERNAL_VALIDATION_FIRST_DRAFT_REFS,
        *PAPER_FACING_DISPLAY_FIRST_DRAFT_REFS,
    }
    assert "immutable_candidate_snapshot_ref" not in external_required
    assert "immutable_candidate_snapshot_ref" not in (
        external_validation_first_draft_contract_schema(
            fixed_horizon=True,
            paper_facing_displays=True,
            analysis_input_anomalies=True,
        )["required"]
    )
    missing_specialist_audit = audit_applicable_initial_draft_specialist_refs(
        {ref: "artifact://candidate" for ref in external_required - {"anomaly_sensitivity_ref"}},
        fixed_horizon=True,
        external_validation=True,
        paper_facing_displays=True,
        analysis_input_anomalies=True,
    )
    assert missing_specialist_audit["missing_refs"] == ["anomaly_sensitivity_ref"]
    assert missing_specialist_audit["route_back_candidate"]["route"] == (
        "medical-statistical-review"
    )
    assert missing_specialist_audit["authority"] is False
    assert "immutable_candidate_snapshot_ref" not in INITIAL_DRAFT_SPECIALIST_REF_ROUTES
    assert AUTHORING_FREEZE_HANDOFF_ROUTE == {
        "producer": "medical-manuscript-writing",
        "consumers": ("medical-manuscript-review", "consuming_domain_owner"),
        "refs_only": True,
        "writes_authority": False,
        "signs_review_currentness": False,
    }
    assert INITIAL_DRAFT_SPECIALIST_REF_ROUTES["renderer_provenance_ref"] == {
        "producer": "medical-manuscript-writing",
        "consumers": ("medical-manuscript-review",),
    }
    assert INITIAL_DRAFT_SPECIALIST_REF_ROUTES["structured_display_source_map_ref"] == {
        "producer": "medical-manuscript-writing",
        "consumers": ("medical-manuscript-review",),
    }
    assert terminology_surface_ledger_schema()["properties"]["authority"] == {
        "const": False
    }
    preflight_schema = medical_initial_draft_preflight_candidate_schema_v2()
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
    satisfied_preflight = validate_medical_initial_draft_preflight_candidate_v2(
        preflight_candidate()
    )
    assert satisfied_preflight["machine_check_status"] == "candidate_ref_shape_complete"
    legacy_preflight = preflight_candidate()
    legacy_preflight["manuscript_mode"] = "legacy_complete_draft"
    for gate in legacy_preflight["gate_items"].values():
        gate["refs"] = [exact_ref("a")]
    legacy_v1_audit = validate_medical_initial_draft_preflight_candidate(
        legacy_preflight
    )
    legacy_v2_audit = validate_medical_initial_draft_preflight_candidate_v2(
        legacy_preflight
    )
    assert legacy_v1_audit["machine_check_status"] == "candidate_ref_shape_complete"
    assert legacy_v1_audit["surface_kind"].endswith(".v1")
    assert legacy_v2_audit["machine_check_status"] == "candidate_ref_shape_incomplete"
    assert "PREFLIGHT_MANUSCRIPT_MODE_INVALID" in {
        item["code"] for item in legacy_v2_audit["violations"]
    }
    fixed_horizon_disposition = (
        build_medical_initial_draft_applicability_disposition(
            "fixed_horizon_risk_semantics_ref",
            "the manuscript does not report a fixed prediction horizon",
            exact_ref("d", kind="study_design_evidence_ref"),
        )
    )
    decision_curve_disposition = (
        build_medical_initial_draft_applicability_disposition(
            "decision_curve_validity_ref",
            "the manuscript does not report a decision-curve analysis",
            exact_ref("e", kind="analysis_scope_evidence_ref"),
        )
    )
    invalid_disposition = dict(fixed_horizon_disposition, authority=True)
    assert "PREFLIGHT_DISPOSITION_AUTHORITY_FORBIDDEN" in {
        item["code"]
        for item in validate_medical_initial_draft_applicability_disposition(
            invalid_disposition
        )["violations"]
    }
    fixed_horizon_disposition_ref = (
        medical_initial_draft_applicability_disposition_exact_ref(
            fixed_horizon_disposition, "artifact://disposition/fixed-horizon"
        )
    )
    decision_curve_disposition_ref = (
        medical_initial_draft_applicability_disposition_exact_ref(
            decision_curve_disposition, "artifact://disposition/decision-curve"
        )
    )
    disposition_preflight = preflight_candidate()
    disposition_preflight["gate_items"]["statistical_integrity"]["refs"] = [
        ref
        for ref in disposition_preflight["gate_items"]["statistical_integrity"][
            "refs"
        ]
        if ref["kind"]
        not in {"fixed_horizon_risk_semantics_ref", "decision_curve_validity_ref"}
    ] + [fixed_horizon_disposition_ref, decision_curve_disposition_ref]
    disposition_registry = {
        fixed_horizon_disposition_ref["ref"]: fixed_horizon_disposition,
        decision_curve_disposition_ref["ref"]: decision_curve_disposition,
    }
    disposition_preflight_audit = (
        validate_medical_initial_draft_preflight_candidate_v2(
            disposition_preflight,
            applicability_disposition_candidates=disposition_registry,
        )
    )
    assert disposition_preflight_audit["machine_check_status"] == (
        "candidate_ref_shape_complete"
    )
    fixed_horizon_xor_violation = preflight_candidate()
    fixed_horizon_xor_violation["gate_items"]["statistical_integrity"][
        "refs"
    ].append(fixed_horizon_disposition_ref)
    fixed_horizon_xor_audit = validate_medical_initial_draft_preflight_candidate_v2(
        fixed_horizon_xor_violation,
        applicability_disposition_candidates=disposition_registry,
    )
    assert "PREFLIGHT_CONDITIONAL_REF_ALTERNATIVES_NOT_EXCLUSIVE" in {
        item["code"] for item in fixed_horizon_xor_audit["violations"]
    }
    decision_curve_xor_violation = preflight_candidate()
    decision_curve_xor_violation["gate_items"]["statistical_integrity"][
        "refs"
    ].append(decision_curve_disposition_ref)
    decision_curve_xor_audit = validate_medical_initial_draft_preflight_candidate_v2(
        decision_curve_xor_violation,
        applicability_disposition_candidates=disposition_registry,
    )
    assert "PREFLIGHT_CONDITIONAL_REF_ALTERNATIVES_NOT_EXCLUSIVE" in {
        item["code"] for item in decision_curve_xor_audit["violations"]
    }
    arbitrary_disposition_preflight = json.loads(json.dumps(disposition_preflight))
    arbitrary_disposition_preflight["gate_items"]["statistical_integrity"]["refs"][
        -2
    ] = exact_ref("a", kind="fixed_horizon_not_applicable_ref")
    arbitrary_disposition_preflight["gate_items"]["statistical_integrity"]["refs"][
        -1
    ] = exact_ref("a", kind="decision_curve_not_applicable_ref")
    arbitrary_disposition_audit = validate_medical_initial_draft_preflight_candidate_v2(
        arbitrary_disposition_preflight
    )
    assert "PREFLIGHT_APPLICABILITY_DISPOSITION_CANDIDATE_MISSING" in {
        item["code"] for item in arbitrary_disposition_audit["violations"]
    }
    duplicate_fixed_horizon_ref = (
        medical_initial_draft_applicability_disposition_exact_ref(
            fixed_horizon_disposition,
            "artifact://disposition/fixed-horizon-second-locator",
        )
    )
    duplicate_disposition_preflight = json.loads(json.dumps(disposition_preflight))
    duplicate_disposition_preflight["gate_items"]["statistical_integrity"][
        "refs"
    ].append(duplicate_fixed_horizon_ref)
    duplicate_disposition_registry = dict(disposition_registry)
    duplicate_disposition_registry[duplicate_fixed_horizon_ref["ref"]] = (
        fixed_horizon_disposition
    )
    duplicate_disposition_audit = validate_medical_initial_draft_preflight_candidate_v2(
        duplicate_disposition_preflight,
        applicability_disposition_candidates=duplicate_disposition_registry,
    )
    assert {
        "PREFLIGHT_CONDITIONAL_REF_ALTERNATIVES_NOT_EXCLUSIVE",
        "PREFLIGHT_APPLICABILITY_DISPOSITION_REUSED",
    }.issubset({item["code"] for item in duplicate_disposition_audit["violations"]})
    stale_disposition_registry = json.loads(json.dumps(disposition_registry))
    stale_disposition_registry[fixed_horizon_disposition_ref["ref"]]["reason"] = (
        "a different reason after the exact ref was frozen"
    )
    stale_disposition_audit = validate_medical_initial_draft_preflight_candidate_v2(
        disposition_preflight,
        applicability_disposition_candidates=stale_disposition_registry,
    )
    assert "PREFLIGHT_APPLICABILITY_DISPOSITION_IDENTITY_MISMATCH" in {
        item["code"] for item in stale_disposition_audit["violations"]
    }
    missing_family = preflight_candidate()
    missing_family["gate_items"]["statistical_integrity"]["refs"] = [
        ref
        for ref in missing_family["gate_items"]["statistical_integrity"]["refs"]
        if ref["kind"] != "linked_prediction_performance_ref"
    ]
    missing_family_audit = validate_medical_initial_draft_preflight_candidate_v2(
        missing_family
    )
    assert "PREFLIGHT_REQUIRED_REF_FAMILY_MISSING" in {
        item["code"] for item in missing_family_audit["violations"]
    }
    missing_disposition = preflight_candidate()
    missing_disposition["gate_items"]["statistical_integrity"]["refs"] = [
        ref
        for ref in missing_disposition["gate_items"]["statistical_integrity"]["refs"]
        if ref["kind"] != "decision_curve_validity_ref"
    ]
    missing_disposition_audit = validate_medical_initial_draft_preflight_candidate_v2(
        missing_disposition
    )
    assert "PREFLIGHT_CONDITIONAL_REF_DISPOSITION_MISSING" in {
        item["code"] for item in missing_disposition_audit["violations"]
    }
    na_bypass = preflight_candidate()
    for gate_name in INITIAL_DRAFT_PREFLIGHT_GATES:
        if gate_name == "story_contract":
            continue
        na_bypass["gate_items"][gate_name] = {
            "status": "not_applicable_with_reason",
            "refs": [],
            "unresolved_item_ids": [],
            "not_applicable_reason": "caller declared the required gate inapplicable",
        }
    na_bypass_audit = validate_medical_initial_draft_preflight_candidate_v2(
        na_bypass
    )
    assert {
        "PREFLIGHT_REQUIRED_GATE_NOT_APPLICABLE",
        "PREFLIGHT_SATISFIED_REQUIRED_GATE_NOT_APPLICABLE",
    }.issubset({item["code"] for item in na_bypass_audit["violations"]})

    freeze_inputs = {
        ref_name: exact_ref(tag)
        for ref_name, tag in zip(
            AUTHORING_FREEZE_INPUT_REFS,
            ("0", "1", "2", "3", "4", "5", "6"),
            strict=True,
        )
    }
    snapshot_manifest_locator = {
        "kind": AUTHORING_SNAPSHOT_MANIFEST_KIND,
        "locator": "paper/review/authoring-candidate-snapshot-manifest.json",
    }
    freeze_handoff = build_authoring_freeze_handoff_candidate(
        freeze_inputs,
        preflight_candidate=preflight_candidate(),
        snapshot_manifest_locator=snapshot_manifest_locator,
    )
    assert freeze_handoff["machine_check_status"] == (
        "candidate_frozen_for_independent_review"
    )
    assert freeze_handoff["immutable_candidate_snapshot_ref"]["kind"] == (
        "immutable_candidate_snapshot_ref"
    )
    assert freeze_handoff["immutable_candidate_snapshot_manifest_locator"] == (
        snapshot_manifest_locator
    )
    alternate_locator_handoff = build_authoring_freeze_handoff_candidate(
        freeze_inputs,
        preflight_candidate=preflight_candidate(),
        snapshot_manifest_locator={
            "kind": AUTHORING_SNAPSHOT_MANIFEST_KIND,
            "locator": "other/authoring-candidate-snapshot-manifest.json",
        },
    )
    assert alternate_locator_handoff["immutable_candidate_snapshot_ref"] == (
        freeze_handoff["immutable_candidate_snapshot_ref"]
    )
    missing_locator_handoff = build_authoring_freeze_handoff_candidate(
        freeze_inputs,
        preflight_candidate=preflight_candidate(),
    )
    assert missing_locator_handoff["machine_check_status"] == "route_back_required"
    assert missing_locator_handoff["snapshot_manifest_locator_findings"][0]["code"] == (
        "AUTHORING_SNAPSHOT_MANIFEST_LOCATOR_INVALID"
    )
    assert freeze_handoff["producer_consumer_route"] == AUTHORING_FREEZE_HANDOFF_ROUTE
    assert freeze_handoff["authority"] is False
    route_back_preflight = validate_medical_initial_draft_preflight_candidate(
        preflight_candidate([analysis_gap, authoring_gap])
    )
    assert route_back_preflight["machine_check_status"] == "candidate_ref_shape_complete"
    assert route_back_preflight["earliest_route_back_owner"] == (
        "bounded_analysis_campaign"
    )
    unfrozen_handoff = build_authoring_freeze_handoff_candidate(
        freeze_inputs,
        preflight_candidate=preflight_candidate([analysis_gap, authoring_gap]),
        snapshot_manifest_locator=snapshot_manifest_locator,
    )
    assert unfrozen_handoff["machine_check_status"] == "route_back_required"
    assert unfrozen_handoff["immutable_candidate_snapshot_ref"] is None

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
    defensive_findings = lint_reader_facing_workflow_language(
        [
            {
                "surface_kind": "manuscript_text",
                "surface_ref": "manuscript.md#funding",
                "text": "Status: author input required. The frozen candidate contains no verified funding statement.",
            }
        ]
    )
    assert {item["code"] for item in defensive_findings} == {
        "DEFENSIVE_AUTHOR_INPUT_META_PROSE"
    }
    assert lint_reader_facing_workflow_language(
        [
            {
                "surface_kind": "manuscript_text",
                "surface_ref": "manuscript.md#ethics",
                "text": "The study was approved by [AUTHOR INPUT: insert committee name and approval identifier.]",
            }
        ]
    ) == []
    manuscript_annotation = "[AUTHOR INPUT: insert author names and affiliations.]"
    title_annotation = "[AUTHOR INPUT: insert the corresponding author details.]"
    author_input_registry = {
        "surface_kind": "medical_author_input_registry.v1",
        "schema_version": 1,
        "counts": {
            "grouped_item_count": 1,
            "placement_count": 2,
            "main_manuscript_annotation_count": 1,
            "supporting_document_annotation_count": 1,
        },
        "items": [
            {
                "id": "A01",
                "category": "author_metadata",
                "required_input": "Author names, affiliations, and corresponding-author details",
                "responsible_owner": "author team",
                "placements": [
                    {
                        "placement_id": "A01-M01",
                        "surface_kind": "manuscript_text",
                        "surface_ref": "manuscript.md",
                        "section": "title page",
                        "exact_annotation": manuscript_annotation,
                    },
                    {
                        "placement_id": "A01-T01",
                        "surface_kind": "title_page",
                        "surface_ref": "title_page.md",
                        "section": "corresponding author",
                        "exact_annotation": title_annotation,
                    },
                ],
            }
        ],
    }
    author_input_audit = validate_author_input_registry(
        author_input_registry,
        [
            {
                "surface_kind": "manuscript_text",
                "surface_ref": "manuscript.md",
                "text": f"Authors: {manuscript_annotation}",
            },
            {
                "surface_kind": "title_page",
                "surface_ref": "title_page.md",
                "text": f"Corresponding author: {title_annotation}",
            },
        ],
    )
    assert author_input_audit["machine_check_status"] == "candidate_complete"
    orphan_audit = validate_author_input_registry(
        author_input_registry,
        [
            {
                "surface_kind": "manuscript_text",
                "surface_ref": "manuscript.md",
                "text": (
                    f"Authors: {manuscript_annotation}\n"
                    "[AUTHOR INPUT: insert an unregistered fact.]"
                ),
            },
            {
                "surface_kind": "title_page",
                "surface_ref": "title_page.md",
                "text": f"Corresponding author: {title_annotation}",
            },
        ],
    )
    assert {
        "AUTHOR_INPUT_ANNOTATION_ORPHANED",
        "AUTHOR_INPUT_SURFACE_COUNT_MISMATCH",
    }.issubset({item["code"] for item in orphan_audit["findings"]})
    print(json.dumps({"ok": True, "checks": 45}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
