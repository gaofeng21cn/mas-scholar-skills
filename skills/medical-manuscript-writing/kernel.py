"""Deterministic refs-only helpers for medical manuscript writing.

These helpers scaffold prompts, schemas, and lint hints. They do not create
MAS truth, owner receipts, typed blockers, artifacts, or publication readiness.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from runtime.kernel_validation import (  # noqa: E402
    ExactRefModel,
    NonEmptyStr,
    OpenKernelModel,
    StrictKernelModel,
    StrictNonNegativeInt,
    StrippedNonEmptyStr,
    ValidationError,
    is_sha256_digest,
    parse_exact_ref,
)


class _AuthoringSnapshotManifestLocatorModel(StrictKernelModel):
    kind: Literal["authoring_candidate_snapshot_manifest"]
    locator: StrippedNonEmptyStr


class _ApplicabilityDispositionModel(StrictKernelModel):
    surface_kind: Literal["medical_initial_draft_applicability_disposition_candidate.v1"]
    schema_version: Literal[1]
    target_ref_kind: NonEmptyStr
    status: Literal["not_applicable_with_reason"]
    reason: StrippedNonEmptyStr
    evidence_ref: ExactRefModel
    authority: Literal[False]


class _AuthorInputRegistryHeaderModel(OpenKernelModel):
    surface_kind: Literal["medical_author_input_registry.v1"]
    schema_version: Literal[1]
    items: list[Any]


class _AuthorInputItemModel(OpenKernelModel):
    id: StrippedNonEmptyStr
    category: StrippedNonEmptyStr
    required_input: StrippedNonEmptyStr
    responsible_owner: StrippedNonEmptyStr


class _AuthorInputCountsModel(StrictKernelModel):
    grouped_item_count: StrictNonNegativeInt
    placement_count: StrictNonNegativeInt
    main_manuscript_annotation_count: StrictNonNegativeInt
    supporting_document_annotation_count: StrictNonNegativeInt


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

INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES_V2 = {
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
INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES = {
    **INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES_V2,
    "story_contract": (
        *INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES_V2["story_contract"],
        "author_stance_integrity_ref",
    ),
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
    valid_targets = set(INITIAL_DRAFT_APPLICABILITY_DISPOSITION_TARGETS.values())
    try:
        parsed = _ApplicabilityDispositionModel.model_validate(dict(candidate))
        if parsed.target_ref_kind not in valid_targets:
            violations.append(
                _preflight_violation(
                    "PREFLIGHT_DISPOSITION_TARGET_REF_KIND_INVALID", "target_ref_kind"
                )
            )
    except ValidationError:
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
        if candidate.get("target_ref_kind") not in valid_targets:
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


def medical_initial_draft_preflight_candidate_schema_v3() -> dict[str, Any]:
    """Return the current semantic policy with author-stance integrity."""

    return {
        **medical_initial_draft_preflight_candidate_schema(),
        "semantic_policy_id": "scholarskills_medical_initial_draft_preflight.v3",
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
        candidate,
        strict_v2=False,
        audit_version=1,
        required_gate_ref_families=INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES_V2,
        applicability_disposition_candidates=None,
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
        audit_version=2,
        required_gate_ref_families=INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES_V2,
        applicability_disposition_candidates=applicability_disposition_candidates,
    )


def validate_medical_initial_draft_preflight_candidate_v3(
    candidate: Mapping[str, object],
    *,
    applicability_disposition_candidates: Mapping[
        str, Mapping[str, object]
    ] | None = None,
) -> dict[str, Any]:
    """Validate current ref families, including author-stance integrity."""

    return _validate_medical_initial_draft_preflight_candidate(
        candidate,
        strict_v2=True,
        audit_version=3,
        required_gate_ref_families=INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES,
        applicability_disposition_candidates=applicability_disposition_candidates,
    )


def _validate_medical_initial_draft_preflight_candidate(
    candidate: Mapping[str, object],
    *,
    strict_v2: bool,
    audit_version: int,
    required_gate_ref_families: Mapping[str, Sequence[str]],
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
                for required_kind in required_gate_ref_families.get(
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
            f"medical_initial_draft_preflight_kernel_audit_candidate.v{audit_version}"
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
    if not isinstance(value, Mapping):
        return [_preflight_violation("PREFLIGHT_EXACT_REF_INVALID", label)]
    if parse_exact_ref(value) is not None:
        return []
    violations: list[dict[str, object]] = []
    _check_exact_fields(value, set(EXACT_REF_FIELDS), label, violations)
    for field in ("kind", "ref"):
        if not str(value.get(field) or "").strip():
            violations.append(_preflight_violation("PREFLIGHT_EXACT_REF_FIELD_INVALID", f"{label}.{field}"))
    size_bytes = value.get("size_bytes")
    if isinstance(size_bytes, bool) or not isinstance(size_bytes, int) or size_bytes < 1:
        violations.append(_preflight_violation("PREFLIGHT_EXACT_REF_FIELD_INVALID", f"{label}.size_bytes"))
    if not is_sha256_digest(value.get("sha256")):
        violations.append(_preflight_violation("PREFLIGHT_EXACT_REF_FIELD_INVALID", f"{label}.sha256"))
    return violations


def _validate_authoring_snapshot_manifest_locator(
    value: object,
) -> list[dict[str, object]]:
    if not isinstance(value, Mapping):
        return [
            _preflight_violation(
                "AUTHORING_SNAPSHOT_MANIFEST_LOCATOR_INVALID",
                "snapshot_manifest_locator",
            )
        ]
    try:
        _AuthoringSnapshotManifestLocatorModel.model_validate(dict(value))
    except ValidationError:
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
    try:
        header = _AuthorInputRegistryHeaderModel.model_validate(dict(registry))
        items = header.items
    except ValidationError:
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
        item_valid = True
        try:
            _AuthorInputItemModel.model_validate(dict(item))
        except ValidationError:
            item_valid = False
        if not item_valid or item_id in item_ids:
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
    expected_counts = _AuthorInputCountsModel(
        grouped_item_count=item_count,
        placement_count=placement_count,
        main_manuscript_annotation_count=main_count,
        supporting_document_annotation_count=supporting_count,
    ).model_dump()
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


def validate_author_stance_integrity_candidate(
    registry: Mapping[str, object],
    surfaces: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Validate authorial voice and objective-fact annotation closure."""

    workflow_findings = lint_reader_facing_workflow_language(surfaces)
    registry_audit = validate_author_input_registry(registry, surfaces)
    findings: list[dict[str, object]] = [
        {
            **finding,
            "source": "reader_facing_workflow_language",
        }
        for finding in workflow_findings
    ]
    findings.extend(
        {
            **finding,
            "source": "author_input_registry",
        }
        for finding in registry_audit["findings"]
    )
    findings.sort(
        key=lambda item: (
            str(item.get("source") or ""),
            str(item.get("code") or ""),
            str(item.get("surface_ref") or ""),
        )
    )
    return {
        "surface_kind": "medical_author_stance_integrity_candidate.v1",
        "machine_check_status": "candidate_complete" if not findings else "route_back_required",
        "reader_facing_workflow_language_findings": workflow_findings,
        "author_input_registry_audit": registry_audit,
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


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = str(Path(__file__).resolve().parents[2])
    if _root not in sys.path:
        sys.path.insert(0, _root)
    from runtime.kernel_validation import delegate_self_check
    raise SystemExit(delegate_self_check("medical-manuscript-writing", kernel_file=__file__))
