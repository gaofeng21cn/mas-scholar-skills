"""Active skill sources, kernel API/token boundaries, and capability map / specialist ownership."""

from __future__ import annotations

import json
import re

from tests.consistency._context import (
    fail,
    load_repo_context,
    read_text,
    require_all,
    require_unversioned_v1_binding,
)
def test_initial_draft_preflight_specialist_ref_exclusions_behavior() -> None:
    from tests.kernels._loader import load_kernel

    write_kernel = load_kernel("medical-manuscript-writing")
    fixed_horizon_required = write_kernel.applicable_initial_draft_specialist_refs(
        fixed_horizon=True,
        external_validation=False,
        paper_facing_displays=False,
        analysis_input_anomalies=False,
    )
    external_required = write_kernel.applicable_initial_draft_specialist_refs(
        fixed_horizon=False,
        external_validation=True,
        paper_facing_displays=False,
        analysis_input_anomalies=False,
    )
    assert "immutable_candidate_snapshot_ref" not in fixed_horizon_required
    assert "immutable_candidate_snapshot_ref" not in external_required
    zero_byte_violations = write_kernel._validate_exact_ref(
        {
            "kind": "self_check_ref",
            "ref": "artifact://zero",
            "size_bytes": 0,
            "sha256": "sha256:" + "a" * 64,
        },
        "zero_ref",
    )
    assert any(item["field"] == "zero_ref.size_bytes" for item in zero_byte_violations)

    stats_kernel = load_kernel("medical-statistical-review")
    mixed = stats_kernel.lint_denominator_semantic_separation(
        [
            {
                "metric_ref": "resolved-rate",
                "metric_kind": "resolved_percent",
                "numerator_ref": "n:resolved",
                "denominator_ref": "n:all",
                "denominator_semantics_ref": "denom:all",
                "denominator_role": "candidate_records",
                "visual_semantic_ref": "bar:rate",
                "unit": "percent",
                "formula": {
                    "numerator_ref": "n:resolved",
                    "denominator_ref": "n:candidate",
                    "denominator_role": "candidate_records",
                    "unit": "percent",
                },
            }
        ]
    )
    assert "FORMULA_DENOMINATOR_REF_MISMATCH" in {item["code"] for item in mixed}


def test_skill_sources_and_kernel_surface_contracts() -> None:
    ctx = load_repo_context()
    advanced_specialist_skill_ids = ctx.advanced_specialist_skill_ids
    expected_capability_skills = ctx.expected_capability_skills
    expected_discoverable_skill_ids = ctx.expected_discoverable_skill_ids
    medical_method_specialist_skill_ids = ctx.medical_method_specialist_skill_ids
    redirect_tombstone_skill_ids = ctx.redirect_tombstone_skill_ids
    root = ctx.root
    skill = read_text("skills/mas-scholar-skills/SKILL.md")
    if not re.search(r"^---\n[\s\S]*?^name:\s+mas-scholar-skills$", skill, re.MULTILINE):
        fail("SKILL.md frontmatter must expose name: mas-scholar-skills")
    capability_skill_texts = {
        skill_id: read_text(f"skills/{skill_id}/SKILL.md")
        for skill_id in expected_capability_skills
    }
    capability_skill_texts["medical-manuscript-writing"]
    capability_skill_texts["medical-manuscript-review"]
    capability_skill_texts["medical-figure-design"]
    capability_skill_texts["medical-figure-style"]
    capability_skill_texts["medical-figure-composer"]
    lit_skill = capability_skill_texts["medical-research-lit"]
    stats_skill = capability_skill_texts["medical-statistical-review"]
    capability_skill_texts["medical-table-design"]
    table_kernel = read_text("skills/medical-table-design/kernel.py")
    for token in [
        "TABLE_NOTE_BUDGET_EXCEEDED",
        "INTERNAL_AUDIT_METADATA_IN_READER_NOTE",
        "REPEATED_GLOBAL_TABLE_NOTE",
        "MAIN_TABLE_ROW_BUDGET_EXCEEDED",
        "MAIN_TABLE_COLUMN_BUDGET_EXCEEDED",
        "MAIN_TABLE_BODY_WORD_BUDGET_EXCEEDED",
        "MAIN_TABLE_FOOTNOTE_WORD_BUDGET_EXCEEDED",
        "MAIN_TABLE_SUPPLEMENTARY_ROUTE_MISSING",
        "MAIN_TABLE_STANDALONE_NOTES_HEADING_PRESENT",
        "MAIN_TABLE_FINAL_EMBEDDING_NOT_ONE_PAGE",
    ]:
        if token not in table_kernel:
            fail(f"medical-table-design kernel missing table-note lint token: {token}")
    capability_skill_texts["medical-submission-prep"]
    submit_kernel = read_text("skills/medical-submission-prep/kernel.py")
    write_kernel = read_text("skills/medical-manuscript-writing/kernel.py")
    for token in [
        "validate_author_input_registry",
        "validate_author_stance_integrity_candidate",
        "DEFENSIVE_AUTHOR_INPUT_META_PROSE",
        "AUTHOR_INPUT_ANNOTATION_ORPHANED",
        "AUTHOR_INPUT_ANNOTATION_CARDINALITY_INVALID",
        "AUTHOR_INPUT_DECLARED_COUNTS_MISMATCH",
    ]:
        if token not in write_kernel:
            fail(f"medical-manuscript-writing kernel missing author-input gate token: {token}")
    for token in [
        "build_author_input_todo_projection",
        "validate_author_input_todo_projection",
        "AUTHOR_INPUT_TODO_PROJECTION_MISMATCH",
    ]:
        if token not in submit_kernel:
            fail(f"medical-submission-prep kernel missing author-input projection gate token: {token}")
    capability_skill_texts["medical-data-governance"]
    read_text("skills/medical-cohort-phenotyping/SKILL.md")
    read_text("skills/medical-methodology-planner/SKILL.md")
    read_text("skills/medical-registry-atlas-story-architect/SKILL.md")
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
    advanced_specialist_skills = {
        skill_id: read_text(f"skills/{skill_id}/SKILL.md")
        for skill_id in advanced_specialist_skill_ids
    }
    medical_method_specialist_skills = {
        skill_id: read_text(f"skills/{skill_id}/SKILL.md")
        for skill_id in medical_method_specialist_skill_ids
    }
    mag_grant_skill_candidate_refs = {
        "medical-research-lit": "grant_literature_evidence_candidate_ref",
        "medical-statistical-review": "grant_statistical_review_candidate_ref",
        "medical-methodology-planner": "grant_methodology_plan_candidate_ref",
        "medical-evidence-integrity-reviewer": "grant_evidence_integrity_candidate_ref",
        "medical-evidence-synthesis-and-claim-map": "grant_claim_map_candidate_ref",
        "medical-reference-integrity-auditor": "grant_reference_integrity_candidate_ref",
    }
    {
        "medical-research-lit": lit_skill,
        "medical-statistical-review": stats_skill,
        **{
            skill_id: medical_method_specialist_skills[skill_id]
            for skill_id in mag_grant_skill_candidate_refs
            if skill_id in medical_method_specialist_skills
        },
    }
    medical_method_specialist_skills["medical-display-qc"]
    display_qc_kernel = read_text("skills/medical-display-qc/kernel.py")
    medical_method_specialist_skills[
        "medical-reference-integrity-auditor"
    ]
    reference_integrity_kernel = read_text(
        "skills/medical-reference-integrity-auditor/kernel.py"
    )
    survival_kernel = read_text("skills/medical-survival-analysis-plan/kernel.py")
    data_freeze_kernel = read_text(
        "skills/medical-data-freeze-and-analysis-readiness-reviewer/kernel.py"
    )

    initial_draft_kernel_tokens = {
        "medical-manuscript-writing": (
            write_kernel,
            [
                "validate_medical_initial_draft_preflight_candidate",
                "validate_medical_initial_draft_preflight_candidate_v2",
                "build_medical_initial_draft_applicability_disposition",
                "validate_medical_initial_draft_applicability_disposition",
                "medical_initial_draft_applicability_disposition_exact_ref",
                "medical_initial_draft_applicability_disposition_candidate.v1",
                "PREFLIGHT_APPLICABILITY_DISPOSITION_CANDIDATE_MISSING",
                "PREFLIGHT_APPLICABILITY_DISPOSITION_IDENTITY_MISMATCH",
                "PREFLIGHT_APPLICABILITY_DISPOSITION_REUSED",
                "PREFLIGHT_CONDITIONAL_REF_ALTERNATIVES_NOT_EXCLUSIVE",
                "INITIAL_DRAFT_PREFLIGHT_DEPENDENCY_OWNERS",
                "PREFLIGHT_SATISFIED_GATE_REF_MISSING",
                "PREFLIGHT_ROUTE_BACK_GATE_INCOMPLETE",
                "PREFLIGHT_NOT_APPLICABLE_GATE_REASON_MISSING",
                "PREFLIGHT_DEPENDENCY_OWNER_INVALID",
                "PREFLIGHT_REQUIRED_GATE_NOT_APPLICABLE",
                "INITIAL_DRAFT_PREFLIGHT_MANUSCRIPT_MODE_APPLICABILITY",
                "size_bytes < 1",
                "applicable_initial_draft_specialist_refs",
                "audit_applicable_initial_draft_specialist_refs",
                "INITIAL_DRAFT_SPECIALIST_REF_ROUTES",
                "build_authoring_freeze_handoff_candidate",
                "AUTHORING_FREEZE_HANDOFF_ROUTE",
                '"signs_review_currentness": False',
            ],
        ),
        "medical-statistical-review": (
            first_draft_quality_sources["skills/medical-statistical-review/kernel.py"],
            [
                "validate_validation_partition_integrity",
                "VALIDATION_SELECTION_POLICY_MISSING",
                "validate_endpoint_analysis_set_reconciliation",
                "validate_endpoint_analysis_set_reconciliation_v2",
                "validate_model_complexity_sparse_event",
                "ph_assessment_applicability",
                "continuous_predictor_count",
                "validate_decision_curve_validity",
                "PREDICTION_IPA_IDENTITY_MISMATCH",
                "PREDICTION_IPA_TOLERANCE_CALLER_OVERRIDE_FORBIDDEN",
                "PREDICTION_CALIBRATION_BOUNDS_CALLER_OVERRIDE_FORBIDDEN",
                "PREDICTION_PERFORMANCE_POLICY_ID",
                "scholarskills_linked_prediction_performance.v2",
                "PREDICTION_DISCRIMINATION_METRIC_TYPES",
                "PREDICTION_DISCRIMINATION_RANGE_INVALID",
                "PREDICTION_LIMITING_EVIDENCE_METRIC_REF_INVALID",
                "PREDICTION_LIMITING_EVIDENCE_METRIC_NOT_IN_PANEL",
                "PREDICTION_LIMITING_EVIDENCE_PHRASE_UNSUPPORTED",
                "PREDICTION_LIMITING_EVIDENCE_POLICY_ID",
                "PREDICTION_LIMITED_IPA_UPPER_BOUND",
                "PREDICTION_LIMITING_POLICY_CALLER_OVERRIDE_FORBIDDEN",
                "PREDICTION_RANKING_LIMITING_METRIC_MISSING",
                "PREDICTION_IPA_CONSISTENCY_TOLERANCE",
                "PREDICTION_CALIBRATION_REASONABLE_BOUNDS",
                "ABSOLUTE_RISK_SUPPORT_CONTRADICTS_LINKED_PERFORMANCE",
            ],
        ),
        "medical-survival-analysis-plan": (
            survival_kernel,
            [
                "validate_survival_estimand_plan",
                "fixed_horizon_risk_semantics_ref",
                "competing_risk_ref",
                "decision_curve_validity_ref",
            ],
        ),
        "medical-data-freeze-and-analysis-readiness-reviewer": (
            data_freeze_kernel,
            [
                "validate_clinical_analysis_input_identity_candidate",
                "validate_clinical_analysis_input_identity_candidate_v2",
                "has_longitudinal_follow_up",
                "is_multicenter",
                "requires_endpoint_adjudication",
                "CLINICAL_INPUT_IDENTITY_ALL_NOT_APPLICABLE",
                "CLINICAL_INPUT_STUDY_CONTEXT_EXACT_REF_INVALID",
                "early_censored_count",
            ],
        ),
        "medical-reference-integrity-auditor": (
            reference_integrity_kernel,
            [
                "audit_citation_source_coverage",
                "audit_citation_source_coverage_v2",
                "CITATION_MANUSCRIPT_KEY_SET_EMPTY",
                "CITATION_BIBLIOGRAPHY_KEY_SET_EMPTY",
                "citation_source_coverage_ref",
                "audit_reference_lane_active_inventory_binding",
                "EXCLUDED_REFERENCE_CLEARANCE_STATUS_INVALID",
            ],
        ),
        "medical-table-design": (
            table_kernel,
            [
                "validate_baseline_table_traceability",
                "BASELINE_AVAILABLE_MISSING_N_IDENTITY_VIOLATION",
                "BASELINE_SUMMARY_DENOMINATOR_MISMATCH",
                "BASELINE_SMD_CROSS_SURFACE_CONFLICT",
            ],
        ),
        "medical-display-qc": (
            display_qc_kernel,
            [
                "DISPLAY_QC_REFS",
                "display_render_integrity_ref",
                "validate_document_display_scope_coverage",
                "requires_reader_pdf",
                "expected_display_members",
                "DOCUMENT_DISPLAY_EXPECTED_MEMBER_MISSING_FROM_SNAPSHOT",
                "DOCUMENT_DISPLAY_EXPECTED_MEMBER_MISSING_FROM_AUDIT",
                "DOCUMENT_DISPLAY_PAGE_EVIDENCE_MISSING",
                "composed_paper_pdf_exact_ref",
                "physical_dimensions_inches",
                "normalized_crop_bounds",
            ],
        ),
    }
    for skill_id, (kernel_text, tokens) in initial_draft_kernel_tokens.items():
        for token in tokens:
            if token not in kernel_text:
                fail(f"{skill_id} kernel missing initial-draft preflight token: {token}")


    require_unversioned_v1_binding(
        "clinical input identity",
        data_freeze_kernel,
        "validate_clinical_analysis_input_identity_candidate",
        "_validate_clinical_analysis_input_identity_candidate",
    )
    require_unversioned_v1_binding(
        "citation source coverage",
        reference_integrity_kernel,
        "audit_citation_source_coverage",
        "_audit_citation_source_coverage",
    )

    {
        skill_id: read_text(f"tombstones/skills/{skill_id}/TOMBSTONE.md")
        for skill_id in redirect_tombstone_skill_ids
    }
    actual_discoverable_skill_ids = sorted(
        path.parent.name
        for path in (root / "skills").glob("*/SKILL.md")
    )
    if actual_discoverable_skill_ids != sorted(expected_discoverable_skill_ids):
        fail(
            "discoverable SKILL.md set must match aggregate + core + optional exposure policy; "
            f"actual={actual_discoverable_skill_ids}"
        )
    if (root / "skills/opl-scholarskills/SKILL.md").exists():
        fail("opl-scholarskills must not be an active discoverable SKILL.md")
    for skill_id in redirect_tombstone_skill_ids:
        if (root / f"skills/{skill_id}/SKILL.md").exists():
            fail(f"{skill_id} is a tombstone and must not expose SKILL.md metadata")
        if (root / f"skills/{skill_id}").exists():
            fail(f"{skill_id} tombstone must stay outside the active skills tree")
        if not (root / f"tombstones/skills/{skill_id}/TOMBSTONE.md").exists():
            fail(f"{skill_id} tombstone must keep non-discoverable TOMBSTONE.md")
    for skill_id, text in {
        **capability_skill_texts,
        **advanced_specialist_skills,
        **medical_method_specialist_skills,
    }.items():
        if not re.search(rf"^---\n[\s\S]*?^name:\s+{re.escape(skill_id)}$", text, re.MULTILINE):
            fail(f"{skill_id} must be a real Codex skill")

def test_capability_map_and_specialist_boundaries() -> None:
    ctx = load_repo_context()
    advanced_redirect_tombstone_skill_ids = ctx.advanced_redirect_tombstone_skill_ids
    advanced_router_skill_ids = ctx.advanced_router_skill_ids
    advanced_specialist_skill_ids = ctx.advanced_specialist_skill_ids
    aggregate_skill_ids = ctx.aggregate_skill_ids
    capability_by_id = ctx.capability_by_id
    capability_map = ctx.capability_map
    classification_policy = ctx.classification_policy
    cohort_phenotyping_skill = ctx.cohort_phenotyping_skill
    contract = ctx.contract
    contract_text = ctx.contract_text
    data_governance_skill = ctx.data_governance_skill
    descriptor_pack = ctx.descriptor_pack
    display_receipt_templates = ctx.display_receipt_templates
    expected_capability_skills = ctx.expected_capability_skills
    expected_capability_token_policy = ctx.expected_capability_token_policy
    expected_default_exposure_skill_ids = ctx.expected_default_exposure_skill_ids
    expected_optional_skill_ids = ctx.expected_optional_skill_ids
    failure_token_registry_ref = ctx.failure_token_registry_ref
    figure_composer_skill = ctx.figure_composer_skill
    figure_skill = ctx.figure_skill
    figure_style_skill = ctx.figure_style_skill
    first_draft_quality_sources = ctx.first_draft_quality_sources
    lit_skill = ctx.lit_skill
    medical_method_redirect_tombstone_skill_ids = ctx.medical_method_redirect_tombstone_skill_ids
    medical_method_router_skill_ids = ctx.medical_method_router_skill_ids
    medical_method_specialist_skill_ids = ctx.medical_method_specialist_skill_ids
    methodology_planner_skill = ctx.methodology_planner_skill
    optional_named_specialty_skill_ids = ctx.optional_named_specialty_skill_ids
    optional_router_skill_ids = ctx.optional_router_skill_ids
    owner_closeout_boundary = ctx.owner_closeout_boundary
    professional_figure_workflow_schema = ctx.professional_figure_workflow_schema
    redirect_tombstone_skill_ids = ctx.redirect_tombstone_skill_ids
    review_skill = ctx.review_skill
    stats_skill = ctx.stats_skill
    submit_skill = ctx.submit_skill
    table_skill = ctx.table_skill
    write_skill = ctx.write_skill
    if owner_closeout_boundary.get("closeout_authority_owner") != "consuming_domain_owner":
        fail("owner closeout boundary must route closeout to the consuming domain owner")
    for key in [
        "capability_pack_may_sign_owner_receipt",
        "capability_pack_may_create_typed_blocker",
        "capability_pack_may_claim_publication_readiness",
        "capability_pack_may_claim_current_package_authority",
    ]:
        if owner_closeout_boundary.get(key) is not False:
            fail(f"owner closeout boundary flag {key} must be false")
    advanced_capability_by_id = {
        item.get("skill_id"): item
        for item in capability_map.get("optional_specialist_skills", [])
    }
    capability_map_optional_skill_ids = [
        item.get("skill_id")
        for item in capability_map.get("optional_specialist_skills", [])
    ]
    if capability_map_optional_skill_ids != expected_optional_skill_ids:
        fail("capability map optional specialist Skills must match discoverable exports exactly")
    if capability_map.get("optional_named_specialty_skill_ids") != optional_named_specialty_skill_ids:
        fail("capability map optional named specialties must exclude redirect tombstones")
    capability_map_no_regression_ids = [
        item.get("skill_id")
        for item in capability_map.get("optional_specialist_no_regression_map", [])
    ]
    if capability_map_no_regression_ids != optional_named_specialty_skill_ids:
        fail("capability map no-regression rows must describe only real named specialty Skills")
    expected_redirect_tombstones = [
        *(contract.get("advanced_specialist_pack_policy", {}).get("redirect_tombstone_skills", [])),
        *(contract.get("medical_method_specialist_pack_policy", {}).get("redirect_tombstone_skills", [])),
    ]
    if capability_map.get("optional_specialist_redirect_tombstones") != expected_redirect_tombstones:
        fail("capability map redirect tombstones must match the canonical contract rows")
    advanced_expected = {
        "medical-advanced-biomed-router": {
            "sources": ["alphafold2", "proteinmpnn", "borzoi", "scgpt", "indication-dossier", "compute-env-setup"],
            "refs": ["advanced_biomed_question_ref", "advanced_biomed_route_ref", "execution_intent_ref", "deterministic_receipt_ref"],
            "tokens": ["advanced_biomed", "structure", "protein_design", "genomics", "single_cell", "scientific_compute"],
        },
    }
    method_expected = {
        "medical-methodology-planner": {
            "tokens": ["methodology_planner", "protocol", "SAP", "cohort", "causal_inference", "survival_analysis", "risk_model"],
            "refs": ["methodology_question_ref", "methodology_route_ref", "methodology_plan_ref", "methodology_support_map_ref"],
        },
        "medical-evidence-integrity-reviewer": {
            "tokens": ["evidence_integrity", "claim_map", "source_support", "reference_integrity", "PMID", "DOI", "evidence_gap"],
            "refs": ["evidence_integrity_inventory_ref", "source_support_map_ref", "identifier_integrity_ref", "evidence_gap_decision_candidate_ref"],
        },
        "medical-publication-routeback-reviewer": {
            "tokens": ["publication_routeback", "rebuttal", "reviewer_response", "owner_gate", "display_qc", "display_regression", "human_gate"],
            "refs": ["publication_routeback_inventory_ref", "authority_boundary_ref", "routeback_option_map_ref", "residual_risk_ref"],
        },
    }
    for skill_id, expected in advanced_expected.items():
        item = advanced_capability_by_id.get(skill_id)
        if item is None:
            fail(f"capability map optional specialists missing {skill_id}")
        if item.get("canonical_path") != f"skills/{skill_id}/SKILL.md":
            fail(f"optional specialist canonical path for {skill_id} must point to its SKILL.md")
        require_all(f"optional specialist tokens for {skill_id}", item.get("tokens"), [skill_id, *expected["sources"]])
        require_all(f"optional specialist refs for {skill_id}", item.get("candidate_ref_families"), expected["refs"])
        if item.get("optional_external_specialist") is not True:
            fail(f"{skill_id} must be marked optional external specialist")
        if item.get("blocks_core_progress_when_missing") is not False:
            fail(f"{skill_id} must not block core progress when missing")
        for key in [
            "can_write_domain_truth",
            "can_write_runtime_state",
            "can_mutate_artifact_body",
            "can_sign_owner_receipt",
            "can_create_typed_blocker",
            "can_claim_quality_verdict",
            "can_claim_publication_readiness",
            "can_claim_current_package_authority",
            "can_claim_owner_closeout",
        ]:
            if (item.get("authority_boundary") or {}).get(key) is not False:
                fail(f"optional specialist authority flag {key} must be false for {skill_id}")
    for skill_id, expected in method_expected.items():
        item = advanced_capability_by_id.get(skill_id)
        if item is None:
            fail(f"capability map optional medical-method specialists missing {skill_id}")
        if item.get("canonical_path") != f"skills/{skill_id}/SKILL.md":
            fail(f"optional medical-method specialist canonical path for {skill_id} must point to its SKILL.md")
        require_all(f"optional medical-method specialist tokens for {skill_id}", item.get("tokens"), [skill_id, *expected["tokens"]])
        require_all(f"optional medical-method specialist refs for {skill_id}", item.get("candidate_ref_families"), expected["refs"])
        if item.get("optional_medical_method_specialist") is not True:
            fail(f"{skill_id} must be marked optional medical-method specialist")
        if item.get("blocks_core_progress_when_missing") is not False:
            fail(f"{skill_id} must not block core progress when missing")
        for key in [
            "can_replace_default_eight_skills",
            "can_block_default_core_progress_when_missing",
            "can_write_domain_truth",
            "can_write_runtime_state",
            "can_mutate_artifact_body",
            "can_sign_owner_receipt",
            "can_create_typed_blocker",
            "can_claim_quality_verdict",
            "can_claim_publication_readiness",
            "can_claim_current_package_authority",
            "can_claim_owner_closeout",
        ]:
            if (item.get("authority_boundary") or {}).get(key) is not False:
                fail(f"optional medical-method specialist authority flag {key} must be false for {skill_id}")
    for skill_id in expected_optional_skill_ids:
        item = advanced_capability_by_id.get(skill_id)
        if item is None:
            fail(f"capability map optional specialist missing {skill_id}")
        if item.get("canonical_path") != f"skills/{skill_id}/SKILL.md":
            fail(f"optional specialist canonical path for {skill_id} must point to its SKILL.md")
        if item.get("external_repo_ref") != f"external_repo:mas-scholar-skills/skills/{skill_id}/SKILL.md":
            fail(f"optional specialist external repo ref for {skill_id} must point to its SKILL.md")
        if item.get("default_exposure") is not False:
            fail(f"optional specialist {skill_id} must not be selected for generic tasks")
        if item.get("optional_named_specialty_only") is not True:
            fail(f"optional specialist {skill_id} must remain named-specialty routed")
        if item.get("blocks_core_progress_when_missing") is not False:
            fail(f"optional specialist {skill_id} must not block core progress when missing")
        for key in [
            "can_replace_default_eight_skills",
            "can_block_default_core_progress_when_missing",
            "can_write_domain_truth",
            "can_write_runtime_state",
            "can_mutate_artifact_body",
            "can_sign_owner_receipt",
            "can_create_typed_blocker",
            "can_claim_quality_verdict",
            "can_claim_publication_readiness",
            "can_claim_current_package_authority",
            "can_claim_owner_closeout",
        ]:
            if (item.get("authority_boundary") or {}).get(key) is not False:
                fail(f"optional specialist authority flag {key} must be false for {skill_id}")
    for skill_id in expected_capability_skills:
        item = capability_by_id.get(skill_id)
        if item is None:
            fail(f"capability map missing {skill_id}")
        if item.get("canonical_path") != f"skills/{skill_id}/SKILL.md":
            fail(f"capability map canonical path for {skill_id} must point to its SKILL.md")
        if item.get("external_repo_ref") != f"external_repo:mas-scholar-skills/skills/{skill_id}/SKILL.md":
            fail(f"capability map external repo ref for {skill_id} must point to mas-scholar-skills")
        require_all(f"capability map tokens for {skill_id}", item.get("tokens"), [skill_id])
        token_policy = expected_capability_token_policy[skill_id]
        require_all(
            f"capability map improvement tokens for {skill_id}",
            item.get("improvement_tokens"),
            [skill_id, f"mas-scholar-skills.{token_policy['module']}", *token_policy["required_improvement_tokens"]],
        )
        require_all(
            f"capability map failure tokens for {skill_id}",
            item.get("failure_tokens"),
            token_policy["required_failure_tokens"],
        )
        require_all(
            f"capability map failure token refs for {skill_id}",
            item.get("failure_token_refs"),
            [
                f"{failure_token_registry_ref}#/medical_failure_types/{failure_type}"
                for failure_type in token_policy["failure_types"]
            ],
        )
        require_all(
            f"capability map verification refs for {skill_id}",
            item.get("verification_refs"),
            ["scripts/verify.sh#capability-map-token-policy", failure_token_registry_ref],
        )
        require_all(
            f"capability map canonical paths for {skill_id}",
            item.get("canonical_paths"),
            [
                f"skills/{skill_id}/SKILL.md",
                token_policy.get(
                    "contract_ref",
                    f"contracts/scholar-skills-capability-modules.json#/capability_module_classification_policy/real_skill_backed_module_map/{token_policy['module']}",
                ),
            ],
        )
        if item.get("owner_closeout_boundary_ref") != "contracts/capability_map.json#/owner_closeout_boundary":
            fail(f"capability map owner closeout boundary ref missing for {skill_id}")
        item_authority = item.get("authority_boundary") or {}
        for key in [
            "can_write_domain_truth",
            "can_write_runtime_state",
            "can_mutate_artifact_body",
            "can_sign_owner_receipt",
            "can_create_typed_blocker",
            "can_claim_quality_verdict",
            "can_claim_publication_readiness",
            "can_claim_current_package_authority",
            "can_claim_owner_closeout",
        ]:
            if item_authority.get(key) is not False:
                fail(f"capability map authority flag {key} must be false for {skill_id}")
    if "figure_quality" not in set(capability_by_id["medical-figure-design"].get("feedback_targets", [])):
        fail("capability map must route figure_quality to medical-figure-design")
    if "manuscript_quality" not in set(capability_by_id["medical-manuscript-writing"].get("feedback_targets", [])):
        fail("capability map must route manuscript_quality to medical-manuscript-writing")
    if "review_quality" not in set(capability_by_id["medical-manuscript-review"].get("feedback_targets", [])):
        fail("capability map must route review_quality to medical-manuscript-review")
    if not {"citation", "literature"}.issubset(set(capability_by_id["medical-research-lit"].get("feedback_targets", []))):
        fail("capability map must route citation/literature to medical-research-lit")
    if "cold_store_catalog_ref" in contract_text:
        fail("contract must use lifecycle_catalog_ref instead of cold_store_catalog_ref")
    if "cold_store_catalog_declared" in contract_text:
        fail("contract must use lifecycle_catalog_declared instead of cold_store_catalog_declared")
    if contract.get("brand_family") != "MAS Scholar Skills":
        fail("contract brand_family must be MAS Scholar Skills")
    positioning_policy = contract.get("positioning_policy") or {}
    expected_positioning = {
        "product_stage_name": "MAS Scholar Skills",
        "repository_id": "mas-scholar-skills",
        "role": "framework_capability_provider_for_required_mas_paper_and_mag_grant_dependencies",
        "primary_mas_entry_policy": "MAS_stage_operating_prompts_remain_in_med_autoscience_and_may_consume_specialist_skills_from_mas_scholar_skills",
        "canonical_mas_stage_source_policy": "MAS_domain_agent_repo_agent_stages_and_agent_prompts_are_the_canonical_stage_prompt_source",
        "codex_projection_policy": "MAS_overlay_skills_and_workspace_or_quest_dot_codex_skill_copies_are_codex_projection_or_compatibility_surfaces_not_stage_prompt_source",
        "no_parallel_entry_policy": "do_not_create_parallel_stage_authority_entries_in_mas_scholar_skills",
        "professional_skill_location_policy": "professional_specialist_skills_default_to_the_consuming_domain_agent_repo; heavy_cross_workspace_or_independently_released_skills_may_be_externalized_to_pack_repos_such_as_mas_scholar_skills",
        "tool_connector_policy": "OPL_Connect_or_Fabric_owns_tool_invocation_normalized_read_receipts_and_connector_errors_not_stage_policy_specialist_judgment_owner_receipts_typed_blockers_human_gates_publication_readiness_or_artifact_authority",
        "sync_owner": "OPL Connect",
        "bundled_or_materialized_pack_owner": "consumer_distribution_profile",
        "ledger_and_owner_receipt_owner": "MAS_MAG_or_relevant_OPL_domain_owner",
    }
    for key, expected in expected_positioning.items():
        if positioning_policy.get(key) != expected:
            fail(f"positioning policy {key} must be {expected}")
    require_all(
        "positioning default boundary defense",
        positioning_policy.get("default_boundary_defense"),
        ["stage_prompt", "professional_specialist_skill", "tool_connector"],
    )
    require_all(
        "positioning policy provided surfaces",
        positioning_policy.get("provided_surfaces"),
        [
            "real_codex_skills",
            "syncable_real_skills",
            "medical_paper_professional_specialist_skills",
            "references",
            "packs",
            "quality_floors",
            "templates",
            "external_learning_absorption",
            "module_contract",
            "candidate_refs",
            "route_back_hints",
        ],
    )
    if "opl-scholarskills" not in positioning_policy.get("legacy_repository_ids", []):
        fail("positioning policy must keep opl-scholarskills as legacy alias")
    specialist_skill_policy = contract.get("specialist_skill_policy") or {}
    if specialist_skill_policy.get("canonical_aggregate_skill") != "mas-scholar-skills":
        fail("specialist skill policy must name mas-scholar-skills as canonical aggregate skill")
    if specialist_skill_policy.get("legacy_aggregate_skill_alias") != "opl-scholarskills":
        fail("specialist skill policy must keep opl-scholarskills as legacy alias")
    if specialist_skill_policy.get("legacy_alias_policy") != "opl_scholarskills_is_history_tombstone_provenance_only_not_active_install_or_codex_discovery_surface":
        fail("specialist skill policy must mark opl-scholarskills as history/tombstone provenance only")
    require_all(
        "syncable real skills",
        specialist_skill_policy.get("syncable_real_skills"),
        [
            "medical-manuscript-writing",
            "medical-manuscript-review",
            "medical-figure-design",
            "medical-figure-style",
            "medical-figure-composer",
            "medical-research-lit",
            "medical-statistical-review",
            "medical-table-design",
            "medical-submission-prep",
            "medical-data-governance",
        ],
    )
    require_all(
        "medical paper specialist skill sources",
        specialist_skill_policy.get("medical_paper_specialist_skill_sources"),
        [
            "medical-manuscript-writing",
            "medical-manuscript-review",
            "medical-figure-design",
            "medical-figure-style",
            "medical-figure-composer",
            "medical-statistical-review",
            "medical-table-design",
            "medical-submission-prep",
            "medical-data-governance",
        ],
    )
    require_all(
        "external resource specialist skills",
        specialist_skill_policy.get("external_resource_specialist_skills"),
        ["medical-research-lit"],
    )
    require_all(
        "canonical MAS stage source roots",
        specialist_skill_policy.get("canonical_mas_stage_source_roots"),
        ["agent/stages/", "agent/prompts/"],
    )
    expected_specialist_boundary = {
        "stage_specialist_boundary_policy": "MAS_owns_stage_operating_prompts_for_write_review_figure_scout_and_route_authority; mas_scholar_skills_owns_professional_specialist_playbooks_and_refs_only_candidate_outputs",
        "codex_projection_policy": "MAS_overlay_skills_and_workspace_or_quest_dot_codex_skill_copies_are_codex_projection_or_compatibility_surfaces_not_stage_prompt_source",
        "default_skill_home_policy": "professional_specialist_skills_default_to_the_consuming_domain_agent_repo_next_to_stage_prompts",
        "external_pack_split_policy": "heavy_cross_workspace_or_independently_released_professional_skills_may_be_split_to_external_pack_repos; mas_scholar_skills_is_the_pack_for_MAS_medical_writing_review_figure_lit_stats_tables_submit_data_governance_Display_and_source_refs",
        "tool_connector_boundary_policy": "tool_connectors_own_tool_or_API_invocation_normalized_read_receipts_and_resource_errors_not_stage_policy_professional_judgment_owner_receipts_typed_blockers_human_gates_publication_readiness_or_artifact_authority",
    }
    for key, expected in expected_specialist_boundary.items():
        if specialist_skill_policy.get(key) != expected:
            fail(f"specialist skill policy {key} must be {expected}")
    require_all(
        "specialist default boundary defense",
        specialist_skill_policy.get("default_boundary_defense"),
        ["stage_prompt", "professional_specialist_skill", "tool_connector"],
    )
    if "mas_owned_primary_skills" in specialist_skill_policy:
        fail("specialist skill policy must not keep legacy mas_owned_primary_skills wording")
    if specialist_skill_policy.get("mas_consumes_specialist_skills") is not True:
        fail("specialist skill policy must state MAS consumes synced professional specialist skills")
    if specialist_skill_policy.get("mas_maintains_write_review_figure_stage_operating_prompts") is not True:
        fail("specialist skill policy must state MAS keeps write/review/figure stage operating prompts")
    for key in [
        "can_replace_mas_overlay_skill",
        "can_replace_mas_runtime_owner_surface",
        "can_claim_literature_authority",
        "can_claim_medical_writing_authority",
        "can_claim_medical_review_authority",
        "can_claim_figure_artifact_authority",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_publication_readiness",
    ]:
        if specialist_skill_policy.get(key) is not False:
            fail(f"specialist skill authority flag {key} must be false")
    exposure_policy = contract.get("codex_skill_exposure_policy") or {}
    if exposure_policy.get("policy_id") != "mas_scholar_skills_codex_skill_exposure.v1":
        fail("contract missing codex skill exposure policy")
    if exposure_policy.get("source_of_truth") != "contracts/scholar-skills-capability-modules.json":
        fail("codex skill exposure policy must be contract-sourced")
    if exposure_policy.get("plugin_manifest_ref") != ".codex-plugin/plugin.json":
        fail("codex skill exposure policy must point to plugin manifest")
    if exposure_policy.get("codex_default_exposure") is not False:
        fail("codex skill exposure policy default exposure must be false")
    if exposure_policy.get("default_install_policy") != "workspace_or_quest_install_includes_primary_routing_skill_only":
        fail("codex skill exposure policy must install only the primary routing skill by default")
    if exposure_policy.get("aggregate_skill_ids") != aggregate_skill_ids:
        fail("codex skill exposure aggregate skill ids must match")
    if exposure_policy.get("core_skill_ids") != expected_capability_skills:
        fail("codex skill exposure core skill ids must match real syncable skills")
    if exposure_policy.get("default_exposure_skill_ids") != expected_default_exposure_skill_ids:
        fail("codex skill exposure default skill ids must include only the aggregate routing skill")
    if exposure_policy.get("optional_skills_installed_by_default") is not False:
        fail("codex skill exposure must keep specialty skills opt-in")
    if exposure_policy.get("specialty_routing_policy") != "materialized_only_for_matching_tasks":
        fail("codex skill exposure must separate materialization from specialty routing")
    for policy_name, policy_value in [
        (
            "optional_external_specialist_policy",
            classification_policy.get("optional_external_specialist_policy"),
        ),
        (
            "optional_medical_method_specialist_policy",
            classification_policy.get("optional_medical_method_specialist_policy"),
        ),
        (
            "advanced_specialist_pack_policy.codex_discovery_policy",
            contract.get("advanced_specialist_pack_policy", {}).get(
                "codex_discovery_policy"
            ),
        ),
        (
            "medical_method_specialist_pack_policy.codex_discovery_policy",
            contract.get("medical_method_specialist_pack_policy", {}).get(
                "codex_discovery_policy"
            ),
        ),
    ]:
        if "materialized_only_for_matching_tasks" not in (policy_value or ""):
            fail(
                f"{policy_name} must separate default materialization from task routing"
            )
    for policy_name, policy_value in [
        (
            "capability_module_classification_policy.optional_specialist_router_policy",
            classification_policy.get("optional_specialist_router_policy"),
        ),
        (
            "domain_descriptor.capability_pack.optional_router_policy",
            descriptor_pack.get("optional_router_policy"),
        ),
    ]:
        normalized_policy = str(policy_value or "").lower()
        if not all(
            token in normalized_policy
            for token in (
                "primary routing skill is materialized by default",
                "default_exposure=false",
                "matching tasks",
            )
        ):
            fail(
                f"{policy_name} must distinguish default materialization from automatic routing"
            )
        if "sync one" in normalized_policy or "installs preserve" in normalized_policy:
            fail(f"{policy_name} retains a stale named-scope materialization policy")
    if exposure_policy.get("optional_skill_ids") != expected_optional_skill_ids:
        fail("codex skill exposure optional skill ids must match optional specialist policies")
    if exposure_policy.get("optional_router_skill_ids") != optional_router_skill_ids:
        fail("codex skill exposure optional router skill ids must match router policy")
    if exposure_policy.get("optional_named_specialty_skill_ids") != optional_named_specialty_skill_ids:
        fail("codex skill exposure optional named specialty skill ids must match named specialist policy")
    if sorted(exposure_policy.get("optional_redirect_tombstone_skill_ids") or []) != sorted(redirect_tombstone_skill_ids):
        fail("codex skill exposure redirect tombstone ids must match classification policy")
    if sorted(exposure_policy.get("tombstone_skill_ids") or []) != ["opl-scholarskills"]:
        fail("codex skill exposure policy must tombstone only opl-scholarskills")
    allowed_scopes = exposure_policy.get("allowed_scopes") or {}
    for category in ["aggregate", "core"]:
        require_all(
            f"codex skill exposure {category} scopes",
            allowed_scopes.get(category),
            ["workspace", "quest", "explicit_codex_developer"],
        )
    require_all(
        "codex skill exposure optional scopes",
        allowed_scopes.get("optional"),
        ["workspace", "quest", "explicit_codex_developer"],
    )
    require_all(
        "codex skill exposure optional named specialty scopes",
        allowed_scopes.get("optional_named_specialty"),
        ["workspace", "quest", "explicit_codex_developer"],
    )
    redirect_policy = exposure_policy.get("redirect_tombstone_policy", "")
    if "Retired optional professional skill metadata" not in redirect_policy or "capability_preserved=true" not in redirect_policy:
        fail("codex skill exposure redirect policy must describe retired optional professional skill redirects")
    if "Only opl-scholarskills" not in exposure_policy.get("tombstone_policy", ""):
        fail("codex skill exposure tombstone policy must tombstone only opl-scholarskills")
    for key in [
        "can_replace_mas_overlay_skill",
        "can_replace_mas_runtime_owner_surface",
        "can_claim_required_pack_for_study",
        "can_write_owner_ledger",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_publication_readiness",
    ]:
        if positioning_policy.get(key) is not False:
            fail(f"positioning authority flag {key} must be false")
    if classification_policy.get("policy_id") != "mas_scholar_skills_professional_skill_classification.v1":
        fail("contract missing professional skill classification policy")
    require_all(
        "active professional skill modules",
        classification_policy.get("active_professional_skill_modules"),
        ["display", "tables", "stats", "lit", "write", "review", "submit", "data"],
    )
    require_all(
        "real syncable specialist skills",
        classification_policy.get("real_syncable_specialist_skills"),
        [
            "medical-manuscript-writing",
            "medical-manuscript-review",
            "medical-figure-design",
            "medical-figure-style",
            "medical-figure-composer",
            "medical-research-lit",
            "medical-statistical-review",
            "medical-table-design",
            "medical-submission-prep",
            "medical-data-governance",
        ],
    )
    expected_real_skill_backed_modules = {
        "display": "medical-figure-design",
        "lit": "medical-research-lit",
        "stats": "medical-statistical-review",
        "tables": "medical-table-design",
        "write": "medical-manuscript-writing",
        "review": "medical-manuscript-review",
        "submit": "medical-submission-prep",
        "data": "medical-data-governance",
    }
    if classification_policy.get("real_skill_backed_module_map") != expected_real_skill_backed_modules:
        fail("classification policy must map the eight real-skill-backed modules")
    display_subskill_routes = classification_policy.get("display_subskill_routes") or {}
    expected_display_subskill_routes = {
        "style_only": "medical-figure-style",
        "compose_only": "medical-figure-composer",
        "full_figure_work": "medical-figure-design",
        "subskill_module_id": "mas-scholar-skills.display",
        "can_add_active_module": False,
        "can_claim_figure_artifact_authority": False,
        "can_claim_publication_readiness": False,
    }
    if display_subskill_routes != expected_display_subskill_routes:
        fail("classification policy must route display subskills without adding active modules")
    if "capability_module_contracts" in classification_policy:
        fail("classification policy must not keep legacy capability_module_contracts")
    if classification_policy.get("contract_layer_modules"):
        fail("classification policy must not expose active contract-layer modules")
    if "retired_or_deferred_modules" in classification_policy:
        fail("classification policy must not keep retired/deferred module placeholders")
    if not classification_policy.get("non_active_scope_policy"):
        fail("classification policy must state non-active scope without module placeholders")
    for token in [
        "not_from_a_fixed_ten_module_catalog",
        "source_or_external_learning_intake_belongs_to_OPL_Framework_or_MAS_stage_source_surfaces",
        "omics_enters_mas_scholar_skills_only_as_a_future_real_professional_skill_when_MAS_has_a_stable_workflow",
        "dot_codex_skills_sync_remains_required_for_Codex_discovery",
    ]:
        if token not in json.dumps(classification_policy, ensure_ascii=False):
            fail(f"classification policy missing {token}")
    for key in [
        "can_expose_contract_layer_modules_without_real_skill",
        "can_claim_non_active_scope_is_active",
        "can_replace_mas_stage_prompts",
        "can_claim_owner_acceptance",
        "can_claim_publication_readiness",
    ]:
        if classification_policy.get(key) is not False:
            fail(f"classification policy flag {key} must be false")
    require_all(
        "classification optional external specialist skills",
        classification_policy.get("optional_external_specialist_skills"),
        advanced_specialist_skill_ids,
    )
    if "do_not_block_default_core_progress" not in classification_policy.get("optional_external_specialist_policy", ""):
        fail("classification optional specialist policy must not block default core progress")
    require_all(
        "classification optional medical-method specialist skills",
        classification_policy.get("optional_medical_method_specialist_skills"),
        medical_method_specialist_skill_ids,
    )
    if "do_not_block_default_core_progress" not in classification_policy.get("optional_medical_method_specialist_policy", ""):
        fail("classification optional medical-method specialist policy must not block default core progress")
    advanced_policy = contract.get("advanced_specialist_pack_policy") or {}
    if advanced_policy.get("policy_id") != "mas_scholar_skills_advanced_specialist_pack.v1":
        fail("contract missing advanced specialist pack policy")
    if advanced_policy.get("source_head_commit") != "54a2f333973147a1fd703caea6f12252e1f227d6":
        fail("advanced specialist pack must pin AcademicForge source head")
    if advanced_policy.get("classification") != "optional_external_router_and_named_specialist_skills_refs_only_no_authority":
        fail("advanced specialist pack must be optional router + named specialist refs-only no-authority")
    if "replace the eight default medical-paper skills" not in advanced_policy.get("relationship_to_active_modules", ""):
        fail("advanced specialist pack must not replace the default eight skills")
    if "OPL_Runway_Connect_Fabric" not in advanced_policy.get("runtime_substrate_owner_policy", ""):
        fail("advanced compute boundary must keep OPL substrate ownership")
    if sorted(item.get("skill_id") for item in advanced_policy.get("redirect_tombstone_skills", [])) != sorted(advanced_redirect_tombstone_skill_ids):
        fail("advanced specialist redirect tombstones must match classification policy")
    if advanced_policy.get("optional_router_skill_ids") != advanced_router_skill_ids:
        fail("advanced specialist router ids must match classification policy")
    if advanced_policy.get("optional_named_specialist_skill_ids") != classification_policy.get("optional_external_named_specialist_skills"):
        fail("advanced named specialist ids must match classification policy")
    advanced_policy_by_id = {
        item.get("skill_id"): item
        for item in advanced_policy.get("optional_specialist_skills", [])
    }
    for skill_id, expected in advanced_expected.items():
        item = advanced_policy_by_id.get(skill_id)
        if item is None:
            fail(f"advanced specialist policy missing {skill_id}")
        if item.get("canonical_path") != f"skills/{skill_id}/SKILL.md":
            fail(f"advanced specialist policy path wrong for {skill_id}")
        require_all(f"advanced specialist upstream refs for {skill_id}", item.get("upstream_skill_refs"), expected["sources"])
        require_all(f"advanced specialist candidate refs for {skill_id}", item.get("candidate_ref_families"), expected["refs"])
        require_all(
            f"advanced specialist required handoff refs for {skill_id}",
            item.get("required_handoff_refs"),
            ["candidate_refs", "owner_gate_handoff_ref"],
        )
        for key in [
            "can_replace_default_eight_skills",
            "can_block_default_core_progress_when_missing",
            "can_write_domain_truth",
            "can_write_runtime_state",
            "can_mutate_artifact_body",
            "can_sign_owner_receipt",
            "can_create_typed_blocker",
            "can_claim_quality_verdict",
            "can_claim_publication_readiness",
            "can_claim_current_package_authority",
            "can_claim_owner_closeout",
        ]:
            if (item.get("authority_boundary") or {}).get(key) is not False:
                fail(f"advanced specialist policy authority flag {key} must be false for {skill_id}")
    for key in [
        "can_replace_default_eight_skills",
        "can_block_default_core_progress_when_missing",
        "can_write_domain_truth",
        "can_write_runtime_state",
        "can_mutate_artifact_body",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_quality_verdict",
        "can_claim_publication_readiness",
        "can_claim_current_package_authority",
        "can_claim_owner_closeout",
    ]:
        if advanced_policy.get(key) is not False:
            fail(f"advanced specialist pack authority flag {key} must be false")
    method_policy = contract.get("medical_method_specialist_pack_policy") or {}
    if method_policy.get("policy_id") != "mas_scholar_skills_medical_method_specialist_pack.v1":
        fail("contract missing medical-method specialist pack policy")
    if method_policy.get("classification") != "optional_medical_method_router_and_named_specialist_skills_refs_only_no_authority":
        fail("medical-method specialist pack must be optional router + named specialist refs-only no-authority")
    if "do not add active professional modules" not in method_policy.get("relationship_to_active_modules", ""):
        fail("medical-method specialist pack must not add active modules")
    method_policy_by_id = {
        item.get("skill_id"): item
        for item in method_policy.get("optional_specialist_skills", [])
    }
    if sorted(item.get("skill_id") for item in method_policy.get("redirect_tombstone_skills", [])) != sorted(medical_method_redirect_tombstone_skill_ids):
        fail("medical-method redirect tombstones must match classification policy")
    if method_policy.get("optional_router_skill_ids") != medical_method_router_skill_ids:
        fail("medical-method router ids must match classification policy")
    if method_policy.get("optional_named_specialist_skill_ids") != classification_policy.get("optional_medical_method_named_specialist_skills"):
        fail("medical-method named specialist ids must match classification policy")
    for skill_id, expected in method_expected.items():
        item = method_policy_by_id.get(skill_id)
        if item is None:
            fail(f"medical-method specialist policy missing {skill_id}")
        if item.get("canonical_path") != f"skills/{skill_id}/SKILL.md":
            fail(f"medical-method specialist policy path wrong for {skill_id}")
        require_all(f"medical-method specialist routing tokens for {skill_id}", item.get("routing_tokens"), expected["tokens"])
        require_all(f"medical-method specialist candidate refs for {skill_id}", item.get("candidate_ref_families"), expected["refs"])
    initial_draft_optional_refs = {
        "medical-reference-integrity-auditor": ["citation_source_coverage_ref"],
        "medical-display-qc": [
            "document_display_scope_coverage_ref",
            "display_render_integrity_ref",
        ],
        "medical-survival-analysis-plan": [
            "fixed_horizon_risk_semantics_ref",
            "survival_estimand_plan_ref",
            "decision_curve_validity_ref",
        ],
        "medical-data-freeze-and-analysis-readiness-reviewer": [
            "clinical_analysis_input_identity_ref"
        ],
    }
    for skill_id, refs in initial_draft_optional_refs.items():
        capability_item = advanced_capability_by_id.get(skill_id)
        policy_item = method_policy_by_id.get(skill_id)
        if capability_item is None or policy_item is None:
            fail(f"initial-draft optional specialist catalogs missing {skill_id}")
        require_all(
            f"capability map initial-draft optional refs for {skill_id}",
            capability_item.get("candidate_ref_families"),
            refs,
        )
        require_all(
            f"module contract initial-draft optional refs for {skill_id}",
            policy_item.get("candidate_ref_families"),
            refs,
        )
        if capability_item.get("candidate_ref_families") != policy_item.get(
            "candidate_ref_families"
        ):
            fail(f"optional specialist candidate ref catalogs diverge for {skill_id}")
    require_all(
        "medical-method specialist required handoff refs",
        method_policy.get("required_handoff_refs"),
        ["candidate_refs", "route_back_candidate", "owner_gate_handoff_ref"],
    )
    for key in [
        "can_replace_default_eight_skills",
        "can_block_default_core_progress_when_missing",
        "can_write_domain_truth",
        "can_write_runtime_state",
        "can_mutate_artifact_body",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_quality_verdict",
        "can_claim_source_readiness",
        "can_claim_runtime_readiness",
        "can_claim_publication_readiness",
        "can_claim_production_readiness",
        "can_claim_current_package_authority",
        "can_claim_owner_closeout",
    ]:
        if method_policy.get(key) is not False:
            fail(f"medical-method specialist pack authority flag {key} must be false")
    quality_policy = contract.get("professional_skill_quality_upgrade_policy") or {}
    if quality_policy.get("policy_id") != "mas_scholar_skills_professional_quality_upgrade.v1":
        fail("contract missing professional skill quality upgrade policy")
    quality_policy_text = json.dumps(quality_policy, ensure_ascii=False)
    registry_signal_member_refs = [
        "paper_identity_ref",
        "chart_review_validation_ref",
        "phenotype_outcome_coupling_ref",
        "availability_mechanism_ref",
        "observation_opportunity_bias_ref",
        "source_generation_quality_ref",
        "claim_boundary_ref",
    ]
    registry_signal_foldback = quality_policy.get("registry_signal_validity_pack_foldback") or {}
    if registry_signal_foldback.get("pack_ref") != "registry_signal_validity_pack":
        fail("professional quality policy missing registry signal validity pack ref")
    if registry_signal_foldback.get("ref_family") != "ehr_registry_signal_validity_ref":
        fail("registry signal validity pack must expose one EHR/registry ref family")
    if registry_signal_foldback.get("producer_skill") != "medical-statistical-review":
        fail("registry signal validity pack producer must be medical-statistical-review")
    if registry_signal_foldback.get("owner_route") != "medical-statistical-review":
        fail("registry signal validity pack must route integrated judgment to statistical review")
    if registry_signal_foldback.get("reference_contract") != "references/professional-quality-ref-templates.md#ehr-registry-signal-validity-ref":
        fail("registry signal validity pack must bind the canonical reference contract")
    require_all("registry signal validity member refs", registry_signal_foldback.get("member_refs"), registry_signal_member_refs)
    require_all(
        "registry signal validity consumer routes",
        [item.get("skill_id") for item in registry_signal_foldback.get("consumer_routes") or []],
        [
            "medical-cohort-phenotyping",
            "medical-methodology-planner",
            "medical-data-governance",
            "medical-manuscript-writing",
            "medical-manuscript-review",
            "medical-registry-atlas-story-architect",
        ],
    )
    if registry_signal_foldback.get("refs_only") is not True:
        fail("registry signal validity pack must remain refs-only")
    for key in [
        "can_write_domain_truth",
        "can_claim_statistical_conclusion",
        "can_claim_quality_verdict",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_publication_readiness",
    ]:
        if registry_signal_foldback.get(key) is not False:
            fail(f"registry signal validity pack authority flag {key} must be false")
    stats_module = next(
        (item for item in contract.get("modules") or [] if item.get("module_id") == "mas-scholar-skills.stats"),
        {},
    )
    require_all(
        "stats module registry signal validity artifacts",
        [item.get("ref_id") for item in stats_module.get("artifact_refs") or []],
        ["ehr_registry_signal_validity_ref"],
    )
    require_all(
        "stats module registry signal validity quality refs",
        (stats_module.get("quality_evidence") or {}).get("required_ref_shapes"),
        ["ehr_registry_signal_validity_ref"],
    )
    display_module = next(
        (item for item in contract.get("modules") or [] if item.get("module_id") == "mas-scholar-skills.display"),
        {},
    )
    display_quality_floor = display_module.get("display_quality_floor_policy") or {}
    scientific_figure_quality_floor = display_quality_floor.get("scientific_figure_quality_floor_policy") or {}
    display_text_safe_area_surfaces = {
        "display artifact refs": [item.get("ref_id") for item in display_module.get("artifact_refs") or []],
        "display quality evidence": (display_module.get("quality_evidence") or {}).get("required_ref_shapes"),
        "display minimum candidate refs": display_quality_floor.get("minimum_candidate_refs"),
        "scientific figure required refs": scientific_figure_quality_floor.get("required_before_gallery_or_paper_use"),
        "display learned pattern refs": (display_module.get("learned_pattern_policy") or {}).get("required_ref_shapes"),
    }
    for label, refs in display_text_safe_area_surfaces.items():
        require_all(label, refs, ["text_extent_safe_area_ref", "layout_qc_receipt_ref"])
    require_all(
        "scientific figure learned patterns",
        scientific_figure_quality_floor.get("learned_scientific_figure_patterns"),
        [
            "text_extent_safe_area_after_final_renderer_draw",
            "layout_qc_receipt_after_fixed_canvas_export",
        ],
    )
    for token in [
        "K-Dense-AI/scientific-agent-skills",
        "Yuan1z0825/nature-skills",
        "1e024ea8547ada12039edbe8197aaa959d97763f",
        "c91df241a7a963ea151687ac669c5534404f53e5",
        "figure_contract_ref",
        "figure_contract_template_ref",
        "panel_evidence_chain_ref",
        "one_sentence_argument_ref",
        "claim_citation_quality_loop_ref",
        "citation_quality_action_matrix_ref",
        "review_fact_base_ref",
        "source_ref_chain_template_ref",
        "source_acceptance_decision_ref",
        "support_strength_matrix_ref",
        "data_availability_and_FAIR_metadata_checks",
        "reviewer_response_delta_audit",
        "statistical_action_matrix_ref",
        "table_shell_ref",
        "submission_action_matrix_ref",
        "medical-data-governance",
        "data_asset_manifest_ref",
        "version_diff_impact_ref",
    ]:
        if token not in quality_policy_text:
            fail(f"professional skill quality upgrade policy missing {token}")
    expected_quality_skill_refs = {
        "medical-figure-design": [
            "figure_contract_template_ref",
            "figure_contract_ref",
            "panel_evidence_chain_ref",
            "candidate_set_ref",
            "critic_review_ref",
            "text_extent_safe_area_ref",
            "layout_qc_receipt_ref",
        ],
        "medical-figure-style": [
            "data_fidelity_ref",
            "claim_title_truth_ref",
            "label_economy_ref",
            "color_vision_check_ref",
            "export_lint_ref",
            "layout_qc_receipt_ref",
        ],
        "medical-figure-composer": [
            "multi_panel_outline_ref",
            "panel_render_receipt_ref",
            "composite_review_ref",
            "final_size_export_ref",
            "layout_qc_receipt_ref",
            "owner_gate_handoff_ref",
        ],
        "medical-manuscript-writing": ["one_sentence_argument_ref", "terminology_ledger_ref", "paragraph_job_map_ref", "claim_citation_quality_loop_ref", "citation_quality_action_matrix_ref"],
        "medical-manuscript-review": ["review_fact_base_ref", "technical_reviewer_lane", "cross_review_synthesis_ref", "claim_citation_quality_loop_ref", "citation_quality_action_matrix_ref"],
        "medical-research-lit": ["source_ref_chain_template_ref", "fallback_source_refs", "deduplication_ref", "source_acceptance_decision_ref", "support_strength_matrix_ref"],
        "medical-statistical-review": ["estimand_or_target_parameter_ref", "effect_size_and_uncertainty_ref", "statistical_action_matrix_ref", "ehr_registry_signal_validity_ref"],
        "medical-table-design": ["table_shell_ref", "table_qc_ref", "claim_table_alignment_ref"],
        "medical-submission-prep": ["journal_instruction_ref", "reporting_guideline_ref", "submission_action_matrix_ref"],
        "medical-data-governance": [
            "data_asset_manifest_ref",
            "data_dictionary_ref",
            "data_governance_assessment_ref",
            "data_operation_receipt_ref",
            "manifest_completeness_check_ref",
            "privacy_tier_check_ref",
            "study_impact_check_ref",
            "version_diff_impact_ref",
            "owner_gate_handoff_ref",
        ],
    }
    for skill_id, refs in expected_quality_skill_refs.items():
        require_all(f"quality refs for {skill_id}", (quality_policy.get("skill_quality_refs") or {}).get(skill_id), refs)
    for key in [
        "can_add_parallel_stage_skill_authority",
        "can_require_external_runtime_install_before_candidate_refs",
        "can_claim_quality_verdict",
        "can_sign_owner_receipt",
        "can_create_typed_blocker",
        "can_claim_publication_readiness",
    ]:
        if quality_policy.get(key) is not False:
            fail(f"professional quality policy flag {key} must be false")
    for relative, skill_id, text in [
        ("skills/medical-manuscript-writing/SKILL.md", "medical-manuscript-writing", write_skill),
        ("skills/medical-manuscript-review/SKILL.md", "medical-manuscript-review", review_skill),
        ("skills/medical-figure-design/SKILL.md", "medical-figure-design", figure_skill),
        ("skills/medical-figure-style/SKILL.md", "medical-figure-style", figure_style_skill),
        ("skills/medical-figure-composer/SKILL.md", "medical-figure-composer", figure_composer_skill),
        ("skills/medical-research-lit/SKILL.md", "medical-research-lit", lit_skill),
        ("skills/medical-statistical-review/SKILL.md", "medical-statistical-review", stats_skill),
        ("skills/medical-table-design/SKILL.md", "medical-table-design", table_skill),
        ("skills/medical-submission-prep/SKILL.md", "medical-submission-prep", submit_skill),
        ("skills/medical-data-governance/SKILL.md", "medical-data-governance", data_governance_skill),
    ]:
        for shared_ref in [
            "docs/no-authority-boundary.md",
            "references/professional-quality-ref-templates.md",
        ]:
            if shared_ref not in text:
                fail(f"{relative} missing shared skill ref {shared_ref}")
    for skill_id in redirect_tombstone_skill_ids:
        text = read_text(f"tombstones/skills/{skill_id}/TOMBSTONE.md")
        target = next(
            (
                item.get("redirect_to")
                for item in [
                    *advanced_policy.get("redirect_tombstone_skills", []),
                    *method_policy.get("redirect_tombstone_skills", []),
                ]
                if item.get("skill_id") == skill_id
            ),
            None,
        )
        if not target:
            fail(f"redirect tombstone missing contract target for {skill_id}")
    for token in [
        "opl_connect_pubmed_pmc_search",
        "opl_connect_reference_verification",
        "opl_connect_search_ref",
        "opl_connect_reference_verification_ref",
        "pubmed_source_refs",
        "opl_connect_read_only_provider_transport_not_citation_acceptance_literature_verdict_or_domain_truth",
    ]:
        if token not in contract_text:
            fail(f"contract missing unified OPL Connect literature token: {token}")
    for retired_token in [
        "opl scholar-skills",
        "connect_pubmed_search",
        "pubmed_connector_invocation_ref",
        "scientific_connector_invocation_refs",
        "candidate_package_ref",
        "execution_receipt_ref",
        "mas_domain_provider_lookup",
        "domain_owned_source_lookup",
        "mas_provider_lookup_ref",
        "research-integrity-reference-verification",
        "mas_domain_owned_read_only_provider_evidence_not_citation_acceptance_literature_verdict_or_domain_truth",
    ]:
        if retired_token in contract_text:
            fail(f"contract must not retain retired execution or PubMed token: {retired_token}")

    professional_template_requirements = {
        "contracts/scholar-skills-capability-modules.json": [
            "scholarskills_display_professional_ref_templates.v1#figure_contract_panel_evidence_chain",
            "scholarskills_lit_professional_ref_templates.v1#source_ref_chain",
            "scholarskills_write_professional_ref_templates.v1#claim_citation_quality_loop",
            "scholarskills_review_professional_ref_templates.v1#claim_citation_quality_loop",
        ],
        "contracts/capability_map.json": [
            "references/professional-quality-ref-templates.md#figure-contract-template",
            "references/professional-quality-ref-templates.md#claim-citation-quality-loop",
            "references/professional-quality-ref-templates.md#literature-sourceref-chain",
        ],
    }
    professional_text_by_relative = {
        "contracts/scholar-skills-capability-modules.json": contract_text,
        "contracts/capability_map.json": json.dumps(capability_map, ensure_ascii=False),
    }
    for relative, tokens in professional_template_requirements.items():
        text = professional_text_by_relative[relative]
        for token in tokens:
            if token not in text:
                fail(f"{relative} missing professional quality template token: {token}")



    registry_signal_consumers = {
        "skills/medical-cohort-phenotyping/SKILL.md": cohort_phenotyping_skill,
        "skills/medical-methodology-planner/SKILL.md": methodology_planner_skill,
        "skills/medical-data-governance/SKILL.md": data_governance_skill,
        "skills/medical-manuscript-writing/SKILL.md": write_skill,
        "skills/medical-manuscript-review/SKILL.md": review_skill,
    }
    for relative, text in registry_signal_consumers.items():
        duplicated_members = [token for token in registry_signal_member_refs if token in text]
        if duplicated_members:
            fail(f"{relative} must consume the canonical registry signal rule without copying member refs: {duplicated_members}")


    first_draft_quality_tokens = {
        "skills/medical-manuscript-writing/kernel.py": [
            "lint_terminology_surface_ledger",
            "machine_readable_endpoints",
            "TERMINOLOGY_BOUNDARY_UNJUSTIFIED",
            "TERMINOLOGY_NOT_APPLICABLE_REASON_MISSING",
            "writes_authority",
        ],
        "skills/medical-registry-atlas-story-architect/kernel.py": [
            "lint_center_sensitivity_claim_binding",
            "CENTRAL_SENSITIVITY_CLAIM_ROW_MISSING",
            "analysis_source_ref",
            "display_refs",
            "writes_authority",
        ],
        "skills/medical-statistical-review/kernel.py": [
            "lint_denominator_semantic_separation",
            "AMBIGUOUS_PERCENT_COUNT_VISUAL_SEMANTIC",
            "writes_authority",
        ],
    }
    for relative, tokens in first_draft_quality_tokens.items():
        for token in tokens:
            if token not in first_draft_quality_sources[relative]:
                fail(f"{relative} missing first-draft deterministic token: {token}")


    if display_receipt_templates.get("schema_version") != "1.6.0":
        fail("display receipt templates must use schema_version 1.6.0")
    require_all(
        "display receipt chain",
        display_receipt_templates.get("receipt_chain"),
        [
            "professional_figure_workflow_ref",
            "figure_contract_ref",
            "render_or_generation_receipt_ref",
            "layout_qc_receipt_ref",
            "visual_qa_receipt_ref",
            "owner_gate_handoff_ref",
        ],
    )
    if professional_figure_workflow_schema.get("$schema") != (
        "https://json-schema.org/draft/2020-12/schema"
    ):
        fail("professional figure workflow must use JSON Schema draft 2020-12")
    workflow_surface = (
        professional_figure_workflow_schema.get("properties", {})
        .get("surface_kind", {})
        .get("const")
    )
    if workflow_surface != "mas_scholar_skills_professional_figure_workflow_candidate.v1":
        fail("professional figure workflow schema has wrong surface kind")
    workflow_template = display_receipt_templates.get("professional_figure_workflow_ref") or {}
    if workflow_template.get("schema_ref") != "contracts/professional-figure-workflow.schema.json":
        fail("display receipt contract must bind the professional figure workflow schema")
    if workflow_template.get("new_or_materially_repaired_figure_requires") != [
        "medical-figure-design"
    ]:
        fail("professional figure workflow must require medical-figure-design")
