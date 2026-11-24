"""Extracted pytest suite for skills/medical-manuscript-writing/kernel.py."""

from __future__ import annotations

from collections.abc import Mapping
from collections.abc import Sequence
import json

from tests.kernels._loader import load_kernel

KERNEL = load_kernel("medical-manuscript-writing")
ANOMALY_SENSITIVITY_FIRST_DRAFT_REFS = KERNEL.ANOMALY_SENSITIVITY_FIRST_DRAFT_REFS
AUTHORING_FREEZE_HANDOFF_ROUTE = KERNEL.AUTHORING_FREEZE_HANDOFF_ROUTE
AUTHORING_FREEZE_INPUT_REFS = KERNEL.AUTHORING_FREEZE_INPUT_REFS
AUTHORING_SNAPSHOT_MANIFEST_KIND = KERNEL.AUTHORING_SNAPSHOT_MANIFEST_KIND
EXTERNAL_VALIDATION_FIRST_DRAFT_REFS = KERNEL.EXTERNAL_VALIDATION_FIRST_DRAFT_REFS
FIRST_DRAFT_STORY_REFS = KERNEL.FIRST_DRAFT_STORY_REFS
FIXED_HORIZON_FIRST_DRAFT_REFS = KERNEL.FIXED_HORIZON_FIRST_DRAFT_REFS
INITIAL_DRAFT_PREFLIGHT_AUTHORITY = KERNEL.INITIAL_DRAFT_PREFLIGHT_AUTHORITY
INITIAL_DRAFT_PREFLIGHT_GATES = KERNEL.INITIAL_DRAFT_PREFLIGHT_GATES
INITIAL_DRAFT_PREFLIGHT_GATE_REF_ALTERNATIVES = KERNEL.INITIAL_DRAFT_PREFLIGHT_GATE_REF_ALTERNATIVES
INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES = KERNEL.INITIAL_DRAFT_PREFLIGHT_GATE_REF_FAMILIES
INITIAL_DRAFT_SPECIALIST_REF_ROUTES = KERNEL.INITIAL_DRAFT_SPECIALIST_REF_ROUTES
PAPER_FACING_DISPLAY_FIRST_DRAFT_REFS = KERNEL.PAPER_FACING_DISPLAY_FIRST_DRAFT_REFS
TERMINOLOGY_SURFACES = KERNEL.TERMINOLOGY_SURFACES
VERIFICATION_SCOPE_FIRST_DRAFT_REFS = KERNEL.VERIFICATION_SCOPE_FIRST_DRAFT_REFS
applicable_initial_draft_specialist_refs = KERNEL.applicable_initial_draft_specialist_refs
audit_applicable_initial_draft_specialist_refs = KERNEL.audit_applicable_initial_draft_specialist_refs
build_authoring_freeze_handoff_candidate = KERNEL.build_authoring_freeze_handoff_candidate
build_medical_initial_draft_applicability_disposition = KERNEL.build_medical_initial_draft_applicability_disposition
claim_strength_lint_lite = KERNEL.claim_strength_lint_lite
external_validation_first_draft_contract_schema = KERNEL.external_validation_first_draft_contract_schema
figure_arc_outline_builder = KERNEL.figure_arc_outline_builder
first_draft_story_contract_schema = KERNEL.first_draft_story_contract_schema
lint_reader_facing_workflow_language = KERNEL.lint_reader_facing_workflow_language
lint_terminology_surface_ledger = KERNEL.lint_terminology_surface_ledger
medical_initial_draft_applicability_disposition_exact_ref = KERNEL.medical_initial_draft_applicability_disposition_exact_ref
medical_initial_draft_preflight_candidate_schema_v3 = KERNEL.medical_initial_draft_preflight_candidate_schema_v3
paper_brief_schema = KERNEL.paper_brief_schema
paragraph_job_map_scaffold = KERNEL.paragraph_job_map_scaffold
section_scaffold = KERNEL.section_scaffold
terminology_surface_ledger_schema = KERNEL.terminology_surface_ledger_schema
validate_author_input_registry = KERNEL.validate_author_input_registry
validate_author_stance_integrity_candidate = KERNEL.validate_author_stance_integrity_candidate
validate_medical_initial_draft_applicability_disposition = KERNEL.validate_medical_initial_draft_applicability_disposition
validate_medical_initial_draft_preflight_candidate = KERNEL.validate_medical_initial_draft_preflight_candidate
validate_medical_initial_draft_preflight_candidate_v2 = KERNEL.validate_medical_initial_draft_preflight_candidate_v2
validate_medical_initial_draft_preflight_candidate_v3 = KERNEL.validate_medical_initial_draft_preflight_candidate_v3

def test_medical_manuscript_writing() -> None:
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
    preflight_schema = medical_initial_draft_preflight_candidate_schema_v3()
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
    satisfied_preflight = validate_medical_initial_draft_preflight_candidate_v3(
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
    prior_v2_candidate = preflight_candidate()
    prior_v2_candidate["gate_items"]["story_contract"]["refs"] = [
        ref
        for ref in prior_v2_candidate["gate_items"]["story_contract"]["refs"]
        if ref["kind"] != "author_stance_integrity_ref"
    ]
    assert validate_medical_initial_draft_preflight_candidate_v2(
        prior_v2_candidate
    )["machine_check_status"] == "candidate_ref_shape_complete"
    prior_v2_under_v3 = validate_medical_initial_draft_preflight_candidate_v3(
        prior_v2_candidate
    )
    assert "PREFLIGHT_REQUIRED_REF_FAMILY_MISSING" in {
        item["code"] for item in prior_v2_under_v3["violations"]
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
    author_stance_audit = validate_author_stance_integrity_candidate(
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
    assert author_stance_audit["machine_check_status"] == "candidate_complete"
    defensive_author_stance_audit = validate_author_stance_integrity_candidate(
        author_input_registry,
        [
            {
                "surface_kind": "manuscript_text",
                "surface_ref": "manuscript.md",
                "text": "This manuscript is not ready because author information is unknown.",
            },
            {
                "surface_kind": "title_page",
                "surface_ref": "title_page.md",
                "text": f"Corresponding author: {title_annotation}",
            },
        ],
    )
    assert defensive_author_stance_audit["machine_check_status"] == "route_back_required"
    assert "DEFENSIVE_AUTHOR_INPUT_META_PROSE" in {
        item["code"] for item in defensive_author_stance_audit["findings"]
    }
    print(json.dumps({"ok": True, "checks": 47}, indent=2, sort_keys=True))
