"""Extracted pytest suites for the 20 compact skill kernels."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tests.kernels._loader import kernel_file, load_kernel


def test_medical_causal_inference_plan() -> None:
    _kernel = load_kernel("medical-causal-inference-plan")
    bias_flag_lint = _kernel.bias_flag_lint
    causal_handoff_skeleton = _kernel.causal_handoff_skeleton
    dag_skeleton = _kernel.dag_skeleton
    estimand_checklist_skeleton = _kernel.estimand_checklist_skeleton
    parse_dag_edges = _kernel.parse_dag_edges
    def _self_check() -> None:
        edges = parse_dag_edges("Age -> Treatment; Treatment causes Outcome.")
        assert edges[0]["source"] == "Age"
        assert edges[1]["target"] == "Outcome"
        assert dag_skeleton(edges)["edges"][0]["target"] == "Treatment"
        assert estimand_checklist_skeleton()[0]["item"] == "population"
        assert bias_flag_lint("check positivity and confounding")[0]["code"] == "CONFOUNDING"
        assert "sensitivity_plan_ref" in causal_handoff_skeleton()
        print(json.dumps({"ok": True, "checks": 6}, indent=2, sort_keys=True))
    _self_check()


def test_medical_clinical_note_abstraction() -> None:
    _kernel = load_kernel("medical-clinical-note-abstraction")
    clinical_note_handoff_skeleton = _kernel.clinical_note_handoff_skeleton
    note_abstraction_skeleton = _kernel.note_abstraction_skeleton
    validate_note_abstraction = _kernel.validate_note_abstraction
    def _self_check() -> None:
        payload = note_abstraction_skeleton("note-1", "schema-1", ["smoking", "age"])
        assert validate_note_abstraction("No tobacco use.", payload)["ok"] is True

        payload["records"][0].update(
            {
                "null_reason": "explicitly_absent",
                "verbatim_span": "No tobacco use",
                "span_start": 0,
                "span_end": 14,
                "presence": "absent",
                "temporality": "current",
                "experiencer": "patient",
            }
        )
        payload["completeness"]["evidenced_field_count"] = 1
        assert validate_note_abstraction("No tobacco use.", payload)["ok"] is True

        payload["records"][0]["verbatim_span"] = "tobacco"
        assert "records[0]:span_mismatch" in validate_note_abstraction("No tobacco use.", payload)["errors"]

        closed_shape = note_abstraction_skeleton("note-2", "schema-1", ["age"])
        closed_shape["unexpected"] = True
        assert "payload_shape" in validate_note_abstraction("Age 42.", closed_shape)["errors"]

        null_consistency = note_abstraction_skeleton("note-3", "schema-1", ["age"])
        null_consistency["records"][0]["candidate_value"] = 42
        assert "records[0]:non_null_with_null_reason" in validate_note_abstraction(
            "Age 42.", null_consistency
        )["errors"]

        assertion_enum = note_abstraction_skeleton("note-4", "schema-1", ["age"])
        assertion_enum["records"][0]["presence"] = "confirmed"
        assert "records[0]:presence" in validate_note_abstraction("Age 42.", assertion_enum)["errors"]

        count_consistency = note_abstraction_skeleton("note-5", "schema-1", ["age"])
        count_consistency["completeness"]["null_field_count"] = 0
        assert "completeness_mismatch" in validate_note_abstraction(
            "Age 42.", count_consistency
        )["errors"]
        assert "chart_review_validation_candidate_ref" in clinical_note_handoff_skeleton()
        print(json.dumps({"ok": True, "checks": 8}, indent=2, sort_keys=True))
    _self_check()


def test_medical_cohort_phenotyping() -> None:
    _kernel = load_kernel("medical-cohort-phenotyping")
    cohort_attrition_table_skeleton = _kernel.cohort_attrition_table_skeleton
    criteria_table_skeleton = _kernel.criteria_table_skeleton
    normalize_criterion = _kernel.normalize_criterion
    phenotype_handoff_skeleton = _kernel.phenotype_handoff_skeleton
    def _self_check() -> None:
        assert normalize_criterion("Exclude prior cancer")["kind"] == "exclusion"
        assert normalize_criterion("Inclusion: adults")["criterion"] == "adults"
        assert len(criteria_table_skeleton(["age >= 18"], ["missing index date"])) == 2
        assert cohort_attrition_table_skeleton(["source"])[0]["n_remaining"] is None
        assert "phenotype_logic_ref" in phenotype_handoff_skeleton()
        print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))
    _self_check()


def test_medical_data_governance() -> None:
    _kernel = load_kernel("medical-data-governance")
    KERNEL_FILE = str(kernel_file("medical-data-governance"))
    classify_sensitive_field = _kernel.classify_sensitive_field
    data_dictionary_schema = _kernel.data_dictionary_schema
    lint_source_readiness = _kernel.lint_source_readiness
    missingness_profile_skeleton = _kernel.missingness_profile_skeleton
    normalize_field_name = _kernel.normalize_field_name
    validate_governed_source_reconstruction = _kernel.validate_governed_source_reconstruction
    def _self_check() -> None:
        assert "variables" in data_dictionary_schema()["required"]
        assert normalize_field_name("Date of Birth") == "date_of_birth"
        assert classify_sensitive_field("patient_email") == "direct_identifier"
        assert missingness_profile_skeleton(["HbA1c lab"])[0]["sensitivity_class"] == "clinical_sensitive"
        lint = lint_source_readiness({"source_layer": "csv", "variables": [{"name": "MRN"}]})
        assert {item["code"] for item in lint} >= {
            "MISSING_GOVERNANCE_REF",
            "UNKNOWN_SOURCE_LAYER",
            "SENSITIVE_FIELD_WITHOUT_PRIVACY_REF",
        }
        fixture_path = Path(KERNEL_FILE).with_name("fixtures") / "governed-source-reconstruction.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        case_results = {
            case["case_id"]: validate_governed_source_reconstruction(case["candidate"])
            for case in fixture["reconstruction_cases"]
        }
        assert case_results["recoverable_identity_provenance"]["machine_check_status"] == "candidate_complete"
        assert case_results["recoverable_identity_provenance"]["reconstruction_outcome"] == "reconstructed"
        assert case_results["declared_recovery_outside_tolerance"]["machine_check_status"] == "route_back_required"
        assert "RECONSTRUCTION_OUTCOME_MISMATCH" in {
            item["code"] for item in case_results["declared_recovery_outside_tolerance"]["findings"]
        }
        print(json.dumps({"ok": True, "checks": 9}, indent=2, sort_keys=True))
    _self_check()


def test_medical_display_regression_debugger() -> None:
    _kernel = load_kernel("medical-display-regression-debugger")
    artifact_diff_row = _kernel.artifact_diff_row
    display_regression_skeleton = _kernel.display_regression_skeleton
    lint_forbidden_display_claims = _kernel.lint_forbidden_display_claims
    def _self_check() -> None:
        row = artifact_diff_row("artifact:new", "artifact:old", "blank panel")
        assert row["writes_authority"] is False
        skeleton = display_regression_skeleton("artifact:new")
        assert skeleton["authority"]["can_mutate_artifacts"] is False
        assert "repair_route_ref" in skeleton["required_refs"]
        assert lint_forbidden_display_claims("artifact fixed with visual audit receipt")
        print({"checks": 4, "ok": True})
    _self_check()


def test_medical_evidence_synthesis_and_claim_map() -> None:
    _kernel = load_kernel("medical-evidence-synthesis-and-claim-map")
    claim_evidence_matrix_skeleton = _kernel.claim_evidence_matrix_skeleton
    claim_inventory_skeleton = _kernel.claim_inventory_skeleton
    evidence_synthesis_handoff_skeleton = _kernel.evidence_synthesis_handoff_skeleton
    support_strength_vocab_lint = _kernel.support_strength_vocab_lint
    def _self_check() -> None:
        rows = claim_evidence_matrix_skeleton(["A"], ["source:1"])
        assert rows[0]["claim_ref"] == "claim_1"
        assert rows[0]["support_strength"] == "missing"
        assert support_strength_vocab_lint([{"support_strength": "strong"}])[0]["code"]
        assert not support_strength_vocab_lint([{"support_strength": "direct_primary"}])
        assert claim_inventory_skeleton(["A"])[0]["claim"] == "A"
        assert "owner_gate_handoff_ref" in evidence_synthesis_handoff_skeleton()
        print(json.dumps({"ok": True, "checks": 6}, indent=2, sort_keys=True))
    _self_check()


def test_medical_figure_style() -> None:
    _kernel = load_kernel("medical-figure-style")
    DEFAULT_FOCAL_COLOR = _kernel.DEFAULT_FOCAL_COLOR
    contrast_ratio = _kernel.contrast_ratio
    crop_box_ref = _kernel.crop_box_ref
    focal_palette = _kernel.focal_palette
    lint_readability = _kernel.lint_readability
    matplotlib_style_rcparams = _kernel.matplotlib_style_rcparams
    panel_letter_plan = _kernel.panel_letter_plan
    def _self_check() -> None:
        assert matplotlib_style_rcparams(frame="boxed")["axes.spines.top"] is True
        assert matplotlib_style_rcparams()["savefig.bbox"] is None
        assert focal_palette(["A", "B"], "A")["A"] == DEFAULT_FOCAL_COLOR
        assert panel_letter_plan(2, case="upper")[1]["letter"] == "B"
        assert crop_box_ref("a", (10, 10, 20, 20), image_size_px=(24, 24))["box_px"] == (6, 6, 24, 24)
        assert contrast_ratio("#000000", "#FFFFFF") > 20
        assert lint_readability([{"label": "n", "color": "#BBBBBB", "font_pt": 5}])
    _self_check()


def test_medical_genomics_foundation_models() -> None:
    _kernel = load_kernel("medical-genomics-foundation-models")
    genomics_handoff_skeleton = _kernel.genomics_handoff_skeleton
    lint_genomic_ref_records = _kernel.lint_genomic_ref_records
    normalize_interval = _kernel.normalize_interval
    variant_candidate_ref_skeleton = _kernel.variant_candidate_ref_skeleton
    def _self_check() -> None:
        assert normalize_interval("1:200-100", genome_build="hg38") == {
            "chrom": "chr1",
            "start": 100,
            "end": 200,
            "genome_build": "hg38",
        }
        assert genomics_handoff_skeleton("score")["model_checkpoint_ref"] == ""
        assert variant_candidate_ref_skeleton("rs1")["authority"] is False
        findings = lint_genomic_ref_records([{"variant": "rs1"}, {"genome_build": "hg38", "note": "source ready"}])
        assert [item["code"] for item in findings] == ["MISSING_REFERENCE_GENOME", "FORBIDDEN_AUTHORITY_CLAIM"]
        print(json.dumps({"ok": True, "checks": 4}, indent=2, sort_keys=True))
    _self_check()


def test_medical_indication_dossier() -> None:
    _kernel = load_kernel("medical-indication-dossier")
    dossier_handoff_skeleton = _kernel.dossier_handoff_skeleton
    lint_forbidden_authority_claims = _kernel.lint_forbidden_authority_claims
    summarize_source_manifest = _kernel.summarize_source_manifest
    waypoint_matrix_skeleton = _kernel.waypoint_matrix_skeleton
    def _self_check() -> None:
        assert dossier_handoff_skeleton("x")["indication_question"] == "x"
        assert waypoint_matrix_skeleton()[0]["waypoint_ref"] == "population_definition_ref"
        summary = summarize_source_manifest(
            [{"source_type": "Guideline", "source_ref": "pmid:1"}, {"source_type": "guideline"}]
        )
        assert summary["source_type_counts"] == {"guideline": 2}
        assert summary["missing_identifier_records"] == ["2"]
        assert lint_forbidden_authority_claims("clinical recommendation")
        print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))
    _self_check()


def test_medical_manuscript_review() -> None:
    _kernel = load_kernel("medical-manuscript-review")
    KERNEL_FILE = str(kernel_file("medical-manuscript-review"))
    claim_citation_figure_matrix_skeleton = _kernel.claim_citation_figure_matrix_skeleton
    classify_issue = _kernel.classify_issue
    review_fact_base_schema = _kernel.review_fact_base_schema
    review_matrix_skeleton = _kernel.review_matrix_skeleton
    validate_anomaly_evidence_parity = _kernel.validate_anomaly_evidence_parity
    validate_receipt_version_member_delta = _kernel.validate_receipt_version_member_delta
    def _self_check() -> None:
        assert "central_claim" in review_fact_base_schema()["required"]
        assert classify_issue("Figure caption drifts")["action"] == "display_repair"
        assert classify_issue("missing citation")["action"] == "citation_repair"
        assert review_matrix_skeleton(["causal overclaim"])[0]["action"] == "claim_downgrade"
        assert claim_citation_figure_matrix_skeleton(["A"])[0]["claim_ref"] == "claim_1"
        anomaly_fixture_path = Path(KERNEL_FILE).with_name("fixtures") / "anomaly-evidence-parity.json"
        anomaly_fixture = json.loads(anomaly_fixture_path.read_text(encoding="utf-8"))
        anomaly_candidate = anomaly_fixture["candidate"]
        assert validate_anomaly_evidence_parity(anomaly_candidate)["machine_check_status"] == "candidate_complete"
        for negative in anomaly_fixture["negative_cases"]:
            changed = json.loads(json.dumps(anomaly_candidate))
            surface = changed["output_surfaces"][negative["surface"]]
            if negative["field"] == "result_delta":
                result = next(
                    item for item in surface["result_deltas"]
                    if item["result_id"] == negative["result_id"]
                )
                result["delta"] = negative["replacement"]
            else:
                surface[negative["field"]] = negative["replacement"]
            audit = validate_anomaly_evidence_parity(changed)
            assert "ANOMALY_EVIDENCE_PARITY_MISMATCH" in {
                item["code"] for item in audit["findings"]
            }

        receipt_fixture_path = Path(KERNEL_FILE).with_name("fixtures") / "receipt-version-member-delta.json"
        receipt_fixture = json.loads(receipt_fixture_path.read_text(encoding="utf-8"))
        receipt_candidate = receipt_fixture["candidate"]
        receipt_audit = validate_receipt_version_member_delta(receipt_candidate)
        assert receipt_audit["machine_check_status"] == "candidate_complete"
        assert all(receipt_audit["normalized_member_delta"][key] for key in ("added", "removed", "changed", "unchanged"))
        digest_only = json.loads(json.dumps(receipt_candidate))
        digest_only["member_delta"] = receipt_fixture["digest_only_member_delta"]
        assert "RECEIPT_DELTA_MEMBER_DELTA_INVALID" in {
            item["code"] for item in validate_receipt_version_member_delta(digest_only)["findings"]
        }
        print(json.dumps({"ok": True, "checks": 13}, indent=2, sort_keys=True))
    _self_check()


def test_medical_protein_design() -> None:
    _kernel = load_kernel("medical-protein-design")
    design_handoff_skeleton = _kernel.design_handoff_skeleton
    lint_forbidden_authority_claims = _kernel.lint_forbidden_authority_claims
    normalize_design_constraints = _kernel.normalize_design_constraints
    summarize_sequence_candidates = _kernel.summarize_sequence_candidates
    def _self_check() -> None:
        constraints = normalize_design_constraints({"fixed_positions": ["3", 1], "allowed_mutations": {"2": ["a", "G"]}})
        assert constraints["fixed_positions"] == [1, 3]
        assert constraints["allowed_mutations"]["2"] == ["A", "G"]
        summary = summarize_sequence_candidates(["ACD", "acd", "AC$"])
        assert summary["duplicate_count"] == 1
        assert summary["invalid_sequences"] == ["AC$"]
        assert design_handoff_skeleton("binder")["sequence_candidate_refs"] == []
        assert lint_forbidden_authority_claims("owner accepted")
        print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))
    _self_check()


def test_medical_protocol_and_sap_planner() -> None:
    _kernel = load_kernel("medical-protocol-and-sap-planner")
    endpoint_sap_checklist_skeleton = _kernel.endpoint_sap_checklist_skeleton
    estimand_checklist_skeleton = _kernel.estimand_checklist_skeleton
    interventional_design_checklist_skeleton = _kernel.interventional_design_checklist_skeleton
    pico_skeleton = _kernel.pico_skeleton
    protocol_handoff_skeleton = _kernel.protocol_handoff_skeleton
    safety_oversight_checklist_skeleton = _kernel.safety_oversight_checklist_skeleton
    schedule_of_activities_skeleton = _kernel.schedule_of_activities_skeleton
    trial_registry_evidence_map_skeleton = _kernel.trial_registry_evidence_map_skeleton
    def _self_check() -> None:
        assert pico_skeleton("q1")["protocol_question_ref"] == "q1"
        assert estimand_checklist_skeleton()[0]["item"] == "treatment_condition"
        assert endpoint_sap_checklist_skeleton(["endpoint"])[0]["item"] == "endpoint"
        assert interventional_design_checklist_skeleton()[2]["item"] == "allocation_concealment"
        assert schedule_of_activities_skeleton(["baseline"])[0]["target_day"] is None
        assert safety_oversight_checklist_skeleton()[0]["item"] == "ae_definition_and_collection_window"
        assert trial_registry_evidence_map_skeleton(["trial_registry"])[0]["currentness_status"] == "unverified"
        assert "sap_candidate_ref" in protocol_handoff_skeleton()
        assert "trial_registry_evidence_map_ref" in protocol_handoff_skeleton()
        print(json.dumps({"ok": True, "checks": 9}, indent=2, sort_keys=True))
    _self_check()


def test_medical_rebuttal_strategy() -> None:
    _kernel = load_kernel("medical-rebuttal-strategy")
    classify_response_route = _kernel.classify_response_route
    evidence_response_map = _kernel.evidence_response_map
    lint_forbidden_rebuttal_claims = _kernel.lint_forbidden_rebuttal_claims
    normalize_comment_id = _kernel.normalize_comment_id
    rebuttal_strategy_skeleton = _kernel.rebuttal_strategy_skeleton
    review_comment_row = _kernel.review_comment_row
    def _self_check() -> None:
        assert normalize_comment_id("Reviewer 2 / Major #1") == "reviewer_2_major_1"
        row = review_comment_row("R1.1", "reviewer", "clarify methods", target_ref="Methods")
        assert row["writes_authority"] is False
        skeleton = rebuttal_strategy_skeleton("review:round1")
        assert "evidence_response_map_ref" in skeleton["required_refs"]
        assert skeleton["authority"]["can_sign_reviewer_receipt"] is False
        assert classify_response_route("add sensitivity analysis")["route"] == "analysis_statistics_route_back"
        mapped = evidence_response_map([{"comment_id": "R1", "requested_action": "add citation"}])
        assert mapped[0]["response_route"] == "literature_support"
        assert lint_forbidden_rebuttal_claims("review accepted with reviewer receipt")
        print(json.dumps({"ok": True, "checks": 7}, indent=2, sort_keys=True))
    _self_check()


def test_medical_registry_atlas_story_architect() -> None:
    _kernel = load_kernel("medical-registry-atlas-story-architect")
    figure_table_story_row = _kernel.figure_table_story_row
    lint_center_sensitivity_claim_binding = _kernel.lint_center_sensitivity_claim_binding
    lint_overclaim_terms = _kernel.lint_overclaim_terms
    registry_story_skeleton = _kernel.registry_story_skeleton
    story_axis_key = _kernel.story_axis_key
    def _self_check() -> None:
        assert story_axis_key("Treatment Gap / 2024") == "treatment_gap_2024"
        row = figure_table_story_row("table1", "claim:a", "denom:b")
        assert row["writes_authority"] is False
        assert registry_story_skeleton("question:x")["authority"]["refs_only"] is True
        assert lint_overclaim_terms("causal service quality claim")
        central_claim = {
            "claim_ref": "claim:center-dependence",
            "locations": ["abstract", "conclusion"],
            "expected_display_refs": ["T4", "TS4"],
        }
        missing_row = lint_center_sensitivity_claim_binding([central_claim], [])
        assert {item["code"] for item in missing_row} == {
            "CENTRAL_SENSITIVITY_CLAIM_ROW_MISSING"
        }
        incomplete_row = lint_center_sensitivity_claim_binding(
            [central_claim], [{"claim_ref": "claim:center-dependence"}]
        )
        assert {item["code"] for item in incomplete_row} >= {
            "CENTRAL_SENSITIVITY_ANALYSIS_SOURCE_MISSING",
            "CENTRAL_SENSITIVITY_DISPLAY_REFS_MISSING",
        }
        complete_row = lint_center_sensitivity_claim_binding(
            [central_claim],
            [
                {
                    "claim_ref": "claim:center-dependence",
                    "analysis_source_ref": "analysis://center-sensitivity",
                    "display_refs": ["T4", "TS4"],
                }
            ],
        )
        assert complete_row == []
        assert all(item["writes_authority"] is False for item in missing_row)
        print({"checks": 8, "ok": True})
    _self_check()


def test_medical_research_lit() -> None:
    _kernel = load_kernel("medical-research-lit")
    dedupe_sources = _kernel.dedupe_sources
    extract_dois = _kernel.extract_dois
    handoff_skeleton = _kernel.handoff_skeleton
    lint_citation_support = _kernel.lint_citation_support
    normalize_pmcid = _kernel.normalize_pmcid
    normalize_pmid = _kernel.normalize_pmid
    def _self_check() -> None:
        assert extract_dois("See https://doi.org/10.1000/ABC). and doi:10.2000/x.") == [
            "10.1000/abc",
            "10.2000/x",
        ]
        assert extract_dois(f"doi:10.1000/x{'*' * 10_000}") == ["10.1000/x"]
        assert normalize_pmid("PMID: 12345") == "12345"
        assert normalize_pmcid("pmc987") == "PMC987"
        deduped = dedupe_sources(
            [
                {"title": "A Trial", "pmid": "PMID 7"},
                {"title": "Different", "pmid": "7"},
                {"title": "A  trial!"},
            ]
        )
        assert len(deduped["retained"]) == 2
        assert len(deduped["duplicates"]) == 1
        assert lint_citation_support("PMID: TBD\npublication ready")
        assert handoff_skeleton("x")["literature_question"] == "x"
        handoff = handoff_skeleton()
        assert handoff["opl_connect_search_ref"] == ""
        assert handoff["opl_connect_reference_verification_ref"] == ""
        assert handoff["pubmed_source_refs"] == []
        assert not any("connector_invocation" in field for field in handoff)
    _self_check()


def test_medical_risk_model_transportability_reviewer() -> None:
    _kernel = load_kernel("medical-risk-model-transportability-reviewer")
    KERNEL_FILE = str(kernel_file("medical-risk-model-transportability-reviewer"))
    lint_forbidden_authority_claims = _kernel.lint_forbidden_authority_claims
    normalize_predictor_name = _kernel.normalize_predictor_name
    predictor_mapping_row = _kernel.predictor_mapping_row
    transportability_review_skeleton = _kernel.transportability_review_skeleton
    validate_construct_comparability_currentness = _kernel.validate_construct_comparability_currentness
    def _self_check() -> None:
        assert normalize_predictor_name("LDL-C (mg/dL)") == "ldl_c_mg_dl"
        row = predictor_mapping_row("Age", "age_years")
        assert row["writes_authority"] is False
        skeleton = transportability_review_skeleton("model:abc", "cohort:def")
        assert skeleton["authority"]["refs_only"] is True
        assert lint_forbidden_authority_claims("model accepted with owner receipt")
        fixture_path = Path(KERNEL_FILE).with_name("fixtures") / "construct-comparability-currentness.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        results = {
            case["case_id"]: validate_construct_comparability_currentness(case["candidate"])
            for case in fixture["cases"]
        }
        recovered = results["recovered_codebook_and_linkage_field_role_open"]
        assert recovered["machine_check_status"] == "candidate_complete"
        assert recovered["active_stop_layers"] == ["field_role"]
        assert recovered["estimability_status"] == "not_estimable"
        assert recovered["estimation_authorized"] is False
        stale = results["recovered_layers_keep_absence_reasons_active"]
        assert stale["machine_check_status"] == "route_back_required"
        assert "CONSTRUCT_STOP_REASON_STALE_ACTIVE" in {
            item["code"] for item in stale["findings"]
        }
        print(json.dumps({"checks": 10, "ok": True}, sort_keys=True))
    _self_check()


def test_medical_single_cell_modeling() -> None:
    _kernel = load_kernel("medical-single-cell-modeling")
    batch_label_key_diagnostics = _kernel.batch_label_key_diagnostics
    h5ad_safe_obs = _kernel.h5ad_safe_obs
    safe_obs_summary = _kernel.safe_obs_summary
    sanitize_anndata_keys = _kernel.sanitize_anndata_keys
    sanitize_key = _kernel.sanitize_key
    def _self_check() -> None:
        obs = {"Batch ID": ["a", "b", "b"], "cell type": ["T", "B", "T"], "X": [1, 2, 3]}
        assert sanitize_key("Batch ID") == "batch_id"
        assert sanitize_key("X") == "x_key"
        assert sanitize_anndata_keys(["a b", "a-b"]) == {"a b": "a_b", "a-b": "a_b_2"}
        assert safe_obs_summary(obs)["n_obs"] == 3
        assert batch_label_key_diagnostics(obs, "Batch ID", "cell type")["missing_keys"] == []
        optional = _self_check_h5ad_safe_obs()
        print(json.dumps({"ok": True, "checks": 6, "h5ad_safe_obs": optional}, indent=2, sort_keys=True))
    def _self_check_h5ad_safe_obs() -> dict[str, Any]:
        assert callable(h5ad_safe_obs)
        try:
            import pandas as pd
        except ImportError as exc:
            return {"status": "skipped", "reason": str(exc)}
        obs = pd.DataFrame(
            {
                "label": ["T", None, "B"],
                "sample": pd.array(["s1", pd.NA, "s2"], dtype="string"),
                "count": [1, 2, 3],
            },
            index=pd.Index([101, "cell-2", 303], name="cell_id"),
        )
        out = h5ad_safe_obs(obs)
        assert out is not obs
        assert list(out.index) == ["101", "cell-2", "303"]
        assert str(out["label"].dtype) == "category"
        assert str(out["sample"].dtype) == "category"
        assert str(out["count"].dtype) == "int64"
        assert out["label"].isna().tolist() == [False, True, False]
        assert out["sample"].isna().tolist() == [False, True, False]
        return {"status": "checked"}
    _self_check()


def test_medical_structural_biology() -> None:
    _kernel = load_kernel("medical-structural-biology")
    lint_forbidden_authority_claims = _kernel.lint_forbidden_authority_claims
    model_output_manifest_skeleton = _kernel.model_output_manifest_skeleton
    normalize_sequence = _kernel.normalize_sequence
    structure_candidate_skeleton = _kernel.structure_candidate_skeleton
    summarize_confidence_metrics = _kernel.summarize_confidence_metrics
    def _self_check() -> None:
        assert normalize_sequence(" acd ef ") == "ACDEF"
        assert structure_candidate_skeleton("dock")["candidate_refs"] == []
        summary = summarize_confidence_metrics({"plddt": 65, "iptm": 0.5, "pae_mean": 12})
        assert summary["warnings"] == ["low_plddt", "low_iptm", "high_pae_mean"]
        assert model_output_manifest_skeleton(["pdb:1"])["authority"] is False
        assert lint_forbidden_authority_claims("publication ready")
        print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))
    _self_check()


def test_research_pdf_evidence_explorer() -> None:
    _kernel = load_kernel("research-pdf-evidence-explorer")
    KERNEL_FILE = str(kernel_file("research-pdf-evidence-explorer"))
    crop_ref_skeleton = _kernel.crop_ref_skeleton
    guess_outline = _kernel.guess_outline
    lexical_scan = _kernel.lexical_scan
    normalize_page_texts = _kernel.normalize_page_texts
    page_evidence_ref = _kernel.page_evidence_ref
    path_fingerprint = _kernel.path_fingerprint
    regex_grep = _kernel.regex_grep
    def _self_check() -> None:
        pages = normalize_page_texts(
            [
                "Abstract\nThis paper reports alpha beta findings.",
                {"page": 2, "text": "Methods\nWe measured beta and gamma.\nDOI 10.1000/XYZ"},
            ]
        )
        assert pages[0]["page"] == 1
        assert guess_outline(pages)[0]["heading"] == "Abstract"
        assert lexical_scan(pages, "beta gamma", top_k=1)["hits"][0]["page"] == 2
        assert regex_grep(pages, r"10\.\d{4,9}/[^\s]+")[0]["matches"] == ["10.1000/XYZ"]
        assert path_fingerprint(KERNEL_FILE)["sha256"]
        assert page_evidence_ref("pdf:demo", 2)["page"] == 2
        assert crop_ref_skeleton("pdf:demo", 1)["bbox"] is None
    _self_check()


def test_scientific_compute_runner() -> None:
    _kernel = load_kernel("scientific-compute-runner")
    compute_handoff_skeleton = _kernel.compute_handoff_skeleton
    helper_receipt_skeleton = _kernel.helper_receipt_skeleton
    lint_forbidden_authority_claims = _kernel.lint_forbidden_authority_claims
    normalize_env_spec = _kernel.normalize_env_spec
    provider_intent_envelope = _kernel.provider_intent_envelope
    summarize_compute_log = _kernel.summarize_compute_log
    def _self_check() -> None:
        spec = normalize_env_spec(
            {"python": "3.11", "dependencies": ["numpy", " scipy ", "numpy"], "env_vars": ["TOKEN=x"], "hardware": {"gpu": 1}}
        )
        assert spec["packages"] == ["numpy", "scipy"]
        assert spec["env_vars"] == ["TOKEN"]
        assert provider_intent_envelope("fit model", "modal")["authority"] is False
        assert compute_handoff_skeleton("fit")["candidate_refs"] == []
        summary = summarize_compute_log("warning\napi_key=abc\nERROR exit code: 137")
        assert summary["exit_code"] == 137
        assert summary["signals"]["errors"] == 1
        assert lint_forbidden_authority_claims("runtime ready with owner receipt")
        assert helper_receipt_skeleton("cmd")["receipt_kind"] == "scientific_compute_helper_receipt_ref"
        print(json.dumps({"ok": True, "checks": 7}, indent=2, sort_keys=True))
    _self_check()
