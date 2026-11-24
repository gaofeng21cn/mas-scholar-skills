"""Extracted pytest suite for skills/medical-display-qc/kernel.py."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from tempfile import TemporaryDirectory
import json

from tests.kernels._loader import kernel_file, load_kernel

KERNEL = load_kernel("medical-display-qc")
KERNEL_FILE = str(kernel_file("medical-display-qc"))
_font_embedding_state = KERNEL._font_embedding_state
_load_pymupdf = KERNEL._load_pymupdf
audit_layout_registry = KERNEL.audit_layout_registry
build_layout_qc_receipt = KERNEL.build_layout_qc_receipt
build_page_hash_evidence_candidate = KERNEL.build_page_hash_evidence_candidate
classify_display_qc_route = KERNEL.classify_display_qc_route
display_artifact_row = KERNEL.display_artifact_row
display_qc_skeleton = KERNEL.display_qc_skeleton
display_qc_support_map = KERNEL.display_qc_support_map
generate_semantic_wrap = KERNEL.generate_semantic_wrap
inspect_display_artifact = KERNEL.inspect_display_artifact
lint_document_layout_inventory = KERNEL.lint_document_layout_inventory
lint_forbidden_display_qc_claims = KERNEL.lint_forbidden_display_qc_claims
normalize_evidence_ref = KERNEL.normalize_evidence_ref
validate_display_render_integrity = KERNEL.validate_display_render_integrity
validate_document_display_scope_coverage = KERNEL.validate_document_display_scope_coverage
validate_figure_numbering_one_owner = KERNEL.validate_figure_numbering_one_owner

def test_medical_display_qc() -> None:
    digest = "sha256:" + "a" * 64
    def render_exact_ref(artifact_format: str) -> dict[str, object]:
        return {
            "kind": f"final_{artifact_format}_export",
            "ref": f"artifact://figure-1.{artifact_format}",
            "size_bytes": 100,
            "sha256": digest,
        }

    render_integrity_candidate = {
        "font_locks": [
            {"font_file_ref": "font://source-sans", "font_file_sha256": digest}
        ],
        "renderer_lock": {
            "family": "matplotlib",
            "version": "3.x",
            "headless_backend": "Agg",
        },
        "renderer_draw_complete": True,
        "artist_scope": "all_text_artists",
        "single_generation_source_ref": "source://figure-1",
        "paired_exports": [
            {
                "format": artifact_format,
                "artifact_ref": render_exact_ref(artifact_format),
                "visible_payload_sha256": digest,
                "labels_sha256": digest,
                "panel_order_sha256": digest,
                "source_fingerprint": digest,
                "dimensions": {
                    "width": 1800 if artifact_format == "png" else 432,
                    "height": 900 if artifact_format == "png" else 216,
                    "unit": "px" if artifact_format == "png" else "pt",
                },
                "crop_bounds": {
                    "coordinates": (
                        [0, 0, 1800, 900]
                        if artifact_format == "png"
                        else [0, 0, 432, 216]
                    ),
                    "unit": "px" if artifact_format == "png" else "pt",
                },
                "resolution_per_inch": 300 if artifact_format == "png" else None,
                "physical_dimensions_inches": [6, 3],
                "normalized_crop_bounds": [0, 0, 1, 1],
            }
            for artifact_format in ("png", "pdf")
        ],
        "final_scale_visual_note": "Both exports were inspected at final manuscript scale.",
        "authority": False,
    }
    render_integrity = validate_display_render_integrity(render_integrity_candidate)
    assert render_integrity["machine_check_status"] == "candidate_complete"
    payload_tamper = json.loads(json.dumps(render_integrity_candidate))
    payload_tamper["paired_exports"][1]["visible_payload_sha256"] = (
        "sha256:" + "b" * 64
    )
    payload_tamper_audit = validate_display_render_integrity(payload_tamper)
    assert "display_paired_export_parity_mismatch" in {
        item["code"] for item in payload_tamper_audit["findings"]
    }
    malformed_artifact_ref = json.loads(json.dumps(render_integrity_candidate))
    malformed_artifact_ref["paired_exports"][0]["artifact_ref"].pop("size_bytes")
    assert "display_paired_export_exact_ref_invalid" in {
        item["code"]
        for item in validate_display_render_integrity(malformed_artifact_ref)[
            "findings"
        ]
    }
    nonfinite_crop = json.loads(json.dumps(render_integrity_candidate))
    nonfinite_crop["paired_exports"][0]["crop_bounds"]["coordinates"][2] = float("inf")
    assert "display_paired_export_crop_invalid" in {
        item["code"]
        for item in validate_display_render_integrity(nonfinite_crop)["findings"]
    }
    physical_mismatch = json.loads(json.dumps(render_integrity_candidate))
    physical_mismatch["paired_exports"][1]["physical_dimensions_inches"] = [5, 3]
    assert "display_paired_export_parity_mismatch" in {
        item["code"]
        for item in validate_display_render_integrity(physical_mismatch)["findings"]
    }
    unit_mismatch = json.loads(json.dumps(render_integrity_candidate))
    unit_mismatch["paired_exports"][1]["dimensions"]["unit"] = "px"
    assert "display_paired_export_dimensions_invalid" in {
        item["code"]
        for item in validate_display_render_integrity(unit_mismatch)["findings"]
    }
    missing_visual_note = dict(render_integrity_candidate, final_scale_visual_note="")
    assert "display_final_scale_visual_note_missing" in {
        item["code"]
        for item in validate_display_render_integrity(missing_visual_note)["findings"]
    }
    assert normalize_evidence_ref("  fig:1 ;") == "fig:1"
    row = display_artifact_row("artifact:pdf", page_ref=" page 2 ", panel_ref="A")
    assert row["writes_authority"] is False
    skeleton = display_qc_skeleton("artifact:pdf")
    assert "display_qc_support_map_ref" in skeleton["required_refs"]
    assert "programmatic_figure_audit_ref" in skeleton["required_refs"]
    assert "display_render_integrity_ref" in skeleton["required_refs"]
    assert skeleton["authority"]["can_sign_visual_audit_receipt"] is False
    assert classify_display_qc_route("blank exported panel")["route"] == "artifact_owner_repair"
    support = display_qc_support_map([{"artifact_ref": "fig:1", "issue": "caption drift"}])
    assert support[0]["route_back_candidate"] == "caption_numbering_repair"
    assert lint_forbidden_display_qc_claims("publication-ready with owner receipt")
    layout_findings = lint_document_layout_inventory(
        [
            {
                "block_id": "F2-legend",
                "block_kind": "figure_legend",
                "document_role": "main_document",
                "artifact_role": "main_figure",
                "page_start": 22,
                "page_end": 23,
            },
            {
                "block_id": "S1",
                "block_kind": "supplementary_figure",
                "document_role": "main_document",
                "artifact_role": "supplementary_figure",
                "page_start": 25,
                "page_end": 25,
            },
            {
                "block_id": "references",
                "block_kind": "references",
                "document_role": "main_document",
                "artifact_role": "references",
                "page_start": 25,
                "page_end": 26,
            },
            {
                "block_id": "discussion-heading",
                "block_kind": "section_heading",
                "document_role": "main_document",
                "artifact_role": "section_heading",
                "page_start": 30,
                "page_end": 30,
                "text": "Discussion",
            },
            {
                "block_id": "discussion-body",
                "block_kind": "paragraph",
                "document_role": "main_document",
                "artifact_role": "text",
                "page_start": 31,
                "page_end": 31,
            },
            {
                "block_id": "ts25-continuation-title",
                "block_kind": "continuation_title",
                "document_role": "supplement",
                "artifact_role": "supplementary_table",
                "page_start": 32,
                "page_end": 32,
                "panel_count": 1,
                "title_text": "TS25, panel 1 of 1",
            },
        ]
    )
    assert {item["code"] for item in layout_findings} == {
        "FIGURE_LEGEND_SPLIT_ACROSS_PAGES",
        "SUPPLEMENTARY_DISPLAY_IN_MAIN_DOCUMENT",
        "DISPLAY_AND_REFERENCES_SHARE_PAGE",
        "ORPHAN_SECTION_HEADING_AT_PAGE_END",
        "SINGLETON_PANEL_LABEL_IN_CONTINUATION_TITLE",
    }
    assert all(item["writes_authority"] is False for item in layout_findings)
    def exact_ref(kind: str, ref: str, digest: str, size_bytes: int = 100) -> dict[str, object]:
        return {
            "kind": kind,
            "ref": ref,
            "size_bytes": size_bytes,
            "sha256": f"sha256:{digest * 64}",
        }

    def inventory_member(
        member_id: str,
        role: str,
        ref: str,
        digest: str,
        size_bytes: int = 100,
    ) -> dict[str, object]:
        return {
            "member_id": member_id,
            "role": role,
            "ref": ref,
            "size_bytes": size_bytes,
            "sha256": f"sha256:{digest * 64}",
        }

    valid_document_candidate = {
        "requires_reader_pdf": True,
        "canonical_manuscript_ref": exact_ref(
            "canonical_manuscript", "manuscript/paper.md", "1"
        ),
        "table_catalog_ref": exact_ref("table_catalog", "tables/catalog.json", "2"),
        "figure_catalog_ref": exact_ref(
            "figure_catalog", "figures/catalog.json", "3"
        ),
        "caption_legend_manifest_ref": exact_ref(
            "caption_legend_manifest", "manuscript/captions.json", "4"
        ),
        "render_environment_ref": exact_ref(
            "render_environment", "render/environment.json", "5"
        ),
        "font_inventory_ref": exact_ref(
            "font_inventory", "render/fonts.json", "6"
        ),
        "composed_paper_pdf_exact_ref": exact_ref(
            "composed_paper_pdf", "publication/paper.pdf", "7", 700
        ),
        "page_render_evidence_ref": exact_ref(
            "page_render_evidence", "audit/pages.json", "8"
        ),
        "supplement_applicable": True,
        "supplement_not_applicable_reason": None,
        "expected_display_members": [
            {"member_id": "figure-1", "role": "main_figure"},
            {"member_id": "figure-2", "role": "main_figure"},
            {"member_id": "table-1", "role": "main_table"},
        ],
        "snapshot_inventory": [
            inventory_member(
                "paper-main",
                "selected_layout_main_manuscript",
                "publication/paper.pdf",
                "7",
                700,
            ),
            inventory_member(
                "paper-combined",
                "reader_combined_main_and_supplementary",
                "publication/paper_with_supplementary.pdf",
                "9",
                900,
            ),
            inventory_member("figure-1", "main_figure", "figures/F1.pdf", "a"),
            inventory_member("figure-2", "main_figure", "figures/F2.pdf", "b"),
            inventory_member("table-1", "main_table", "tables/T1.docx", "c"),
        ],
        "audit_inventory": [
            inventory_member(
                "paper-main",
                "selected_layout_main_manuscript",
                "audit/paper.pdf",
                "7",
                700,
            ),
            inventory_member(
                "paper-combined",
                "reader_combined_main_and_supplementary",
                "audit/paper_with_supplementary.pdf",
                "9",
                900,
            ),
            inventory_member("figure-1", "main_figure", "audit/F1.png", "d"),
            inventory_member("figure-2", "main_figure", "audit/F2.png", "e"),
            inventory_member("table-1", "main_table", "audit/T1.png", "f"),
        ],
        "authority": False,
    }
    valid_document_scope = validate_document_display_scope_coverage(
        valid_document_candidate
    )
    assert valid_document_scope["machine_check_status"] == "candidate_complete"

    missing_members_candidate = json.loads(json.dumps(valid_document_candidate))
    missing_members_candidate["snapshot_inventory"] = [
        entry
        for entry in missing_members_candidate["snapshot_inventory"]
        if entry["member_id"] != "figure-2"
    ]
    missing_members_candidate["audit_inventory"] = [
        entry
        for entry in missing_members_candidate["audit_inventory"]
        if entry["member_id"] != "table-1"
    ]
    missing_members = validate_document_display_scope_coverage(
        missing_members_candidate
    )
    assert missing_members["missing_snapshot_members"] == ["figure-2:main_figure"]
    assert missing_members["missing_audit_members"] == ["table-1:main_table"]
    assert {item["code"] for item in missing_members["findings"]} >= {
        "DOCUMENT_DISPLAY_EXPECTED_MEMBER_MISSING_FROM_SNAPSHOT",
        "DOCUMENT_DISPLAY_EXPECTED_MEMBER_MISSING_FROM_AUDIT",
    }

    invalid_pdf_pair_candidate = json.loads(json.dumps(valid_document_candidate))
    invalid_pdf_pair_candidate["snapshot_inventory"][0]["role"] = "main_composed_pdf"
    invalid_pdf_pair_candidate["audit_inventory"][0]["ref"] = "audit/manuscript.pdf"
    invalid_pdf_pair = validate_document_display_scope_coverage(
        invalid_pdf_pair_candidate
    )
    assert {item["code"] for item in invalid_pdf_pair["findings"]} >= {
        "DOCUMENT_DISPLAY_PAPER_PDF_MISSING_FROM_SNAPSHOT",
        "DOCUMENT_DISPLAY_PAPER_PDF_MISSING_FROM_AUDIT",
    }

    missing_durable_refs_candidate = json.loads(json.dumps(valid_document_candidate))
    missing_durable_refs_candidate.pop("font_inventory_ref")
    missing_durable_refs_candidate.pop("page_render_evidence_ref")
    missing_durable_refs_candidate["audit_inventory"].append(
        inventory_member(
            "page-audit", "page_render_evidence", "audit/pages.json", "8"
        )
    )
    missing_durable_refs = validate_document_display_scope_coverage(
        missing_durable_refs_candidate
    )
    assert {item["code"] for item in missing_durable_refs["findings"]} >= {
        "DOCUMENT_DISPLAY_REQUIRED_EXACT_REF_INVALID",
        "DOCUMENT_DISPLAY_PAGE_EVIDENCE_MISSING",
    }

    inapplicable_reader_pdf_candidate = json.loads(json.dumps(valid_document_candidate))
    inapplicable_reader_pdf_candidate["requires_reader_pdf"] = False
    inapplicable_reader_pdf_candidate["not_applicable_reason"] = "no reader PDF"
    inapplicable_reader_pdf = validate_document_display_scope_coverage(
        inapplicable_reader_pdf_candidate
    )
    assert inapplicable_reader_pdf["machine_check_status"] == "route_back_required"
    assert "DOCUMENT_DISPLAY_READER_PDF_NOT_APPLICABLE" in {
        item["code"] for item in inapplicable_reader_pdf["findings"]
    }

    valid_supplement_na_candidate = json.loads(json.dumps(valid_document_candidate))
    valid_supplement_na_candidate["supplement_applicable"] = False
    valid_supplement_na_candidate[
        "supplement_not_applicable_reason"
    ] = "the study has no supplement"
    valid_supplement_na_candidate["snapshot_inventory"] = [
        entry
        for entry in valid_supplement_na_candidate["snapshot_inventory"]
        if entry["member_id"] != "paper-combined"
    ]
    valid_supplement_na_candidate["audit_inventory"] = [
        entry
        for entry in valid_supplement_na_candidate["audit_inventory"]
        if entry["member_id"] != "paper-combined"
    ]
    valid_supplement_na = validate_document_display_scope_coverage(
        valid_supplement_na_candidate
    )
    assert valid_supplement_na["machine_check_status"] == "candidate_complete"

    supplement_identity_candidate = json.loads(json.dumps(valid_document_candidate))
    supplement_identity_candidate["audit_inventory"][1]["sha256"] = f"sha256:{'a' * 64}"
    supplement_identity = validate_document_display_scope_coverage(
        supplement_identity_candidate
    )
    assert "DOCUMENT_DISPLAY_SUPPLEMENT_PDF_IDENTITY_MISMATCH" in {
        item["code"] for item in supplement_identity["findings"]
    }
    assert _font_embedding_state("Type3", b"") is None
    assert _font_embedding_state("Type1", b"") is False
    assert _font_embedding_state("Type0", b"font-program") is True

    page_a = {
        "page_number": 1,
        "width": 1224,
        "height": 1584,
        "pixel_format": "RGB8",
        "pixel_sha256": f"sha256:{'1' * 64}",
    }
    page_b = {
        "page_number": 2,
        "width": 1224,
        "height": 1584,
        "pixel_format": "RGB8",
        "pixel_sha256": f"sha256:{'2' * 64}",
    }
    evidence_ref = {
        "kind": "scholarskills_display_evidence",
        "ref": "evidence://display-a",
        "size_bytes": 123,
        "sha256": f"sha256:{'9' * 64}",
    }
    candidate_a = build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_evidence_ref=evidence_ref,
    )
    same_pixels_other_provenance = build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_evidence_ref={
            "kind": "scholarskills_display_evidence",
            "ref": "evidence://different-pdf-metadata",
            "size_bytes": 456,
            "sha256": f"sha256:{'b' * 64}",
        },
    )
    assert candidate_a["cache_key_sha256"] == (
        "sha256:f159ceb039e91fcdf43a3402b195592cbce25841837473284b03760a359a012a"
    )
    assert candidate_a["cache_key_sha256"] == same_pixels_other_provenance[
        "cache_key_sha256"
    ]
    assert set(candidate_a) == {
        "surface_kind",
        "schema_version",
        "review_scope_sha256",
        "rubric_sha256",
        "evidence_payload",
        "cache_key_sha256",
        "origin_reviewer_evidence_ref",
    }
    assert candidate_a["schema_version"] == 3
    assert candidate_a["origin_reviewer_evidence_ref"] == evidence_ref
    changed_pixel = dict(page_b)
    changed_pixel["pixel_sha256"] = f"sha256:{'5' * 64}"
    assert candidate_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [page_a, changed_pixel],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_evidence_ref=evidence_ref,
    )["cache_key_sha256"]
    changed_geometry = dict(page_b, width=1225)
    assert candidate_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [page_a, changed_geometry],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_evidence_ref=evidence_ref,
    )["cache_key_sha256"]
    reordered_a = dict(page_b, page_number=1)
    reordered_b = dict(page_a, page_number=2)
    assert candidate_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [reordered_a, reordered_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_evidence_ref=evidence_ref,
    )["cache_key_sha256"]
    assert candidate_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'6' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
        origin_reviewer_evidence_ref=evidence_ref,
    )["cache_key_sha256"]
    assert candidate_a["cache_key_sha256"] != build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'7' * 64}",
        origin_reviewer_evidence_ref=evidence_ref,
    )["cache_key_sha256"]
    unbound_candidate = build_page_hash_evidence_candidate(
        [page_a, page_b],
        review_scope_sha256=f"sha256:{'3' * 64}",
        rubric_sha256=f"sha256:{'4' * 64}",
    )
    assert unbound_candidate["origin_reviewer_evidence_ref"] is None
    try:
        build_page_hash_evidence_candidate(
            [page_a, page_b],
            review_scope_sha256=f"sha256:{'3' * 64}",
            rubric_sha256=f"sha256:{'4' * 64}",
            origin_reviewer_evidence_ref={
                "kind": "scholarskills_display_evidence",
                "ref": "evidence://missing-size",
                "sha256": f"sha256:{'9' * 64}",
            },
        )
        raise AssertionError("incomplete origin exact ref must fail closed")
    except ValueError:
        pass

    fixture_path = Path(KERNEL_FILE).with_name("fixtures") / "layout_qc_regression.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    long_label = fixture["panels"][0]["text_artists"][1]
    long_label_measurement = long_label["text_measurement"]
    long_label_wrap = long_label_measurement["semantic_wrap"]
    generated_wrap = generate_semantic_wrap(
        long_label["source_text"],
        available_width_px=long_label_measurement["available_width_px"],
        word_widths_px=long_label_wrap["word_widths_px"],
        space_width_px=long_label_wrap["space_width_px"],
    )
    assert generated_wrap["rendered_text"] == long_label["rendered_text"]
    assert generated_wrap["break_after_word_indices"] == [4, 9]
    assert generated_wrap["line_widths_px"] == [265, 252, 85]
    layout_audit = audit_layout_registry(fixture)
    assert layout_audit["machine_check_status"] == "geometry_checks_passed"
    assert layout_audit["registered_text_artist_count"] == 6
    assert layout_audit["checks"]["annotation_lane_separate"] is True
    assert layout_audit["checks"]["measured_wrap_valid"] is True
    assert layout_audit["semantic_artist_applicability"] == "not_applicable"

    semantic_fixture_path = (
        Path(KERNEL_FILE).with_name("fixtures")
        / "semantic_artist_flow_regression.json"
    )
    semantic_fixture = json.loads(semantic_fixture_path.read_text(encoding="utf-8"))
    semantic_audit = audit_layout_registry(semantic_fixture)
    assert semantic_audit["machine_check_status"] == "geometry_checks_passed"
    assert semantic_audit["semantic_flow_contract_required"] is True
    assert semantic_audit["registered_semantic_artist_count"] == 26
    assert semantic_audit["semantic_arrow_count"] == 2
    assert semantic_audit["semantic_segmented_group_span_count"] == 1
    assert semantic_audit["semantic_validated_segmented_group_span_count"] == 1
    for semantic_check in (
        "semantic_artist_applicability_valid",
        "semantic_artist_registry_complete",
        "semantic_artist_kinds_complete",
        "semantic_artists_inside_canvas",
        "semantic_artists_inside_safe_inset",
        "semantic_node_text_contained",
        "semantic_contract_geometry_bound",
        "semantic_lines_clear_of_text",
        "semantic_lines_clear_of_unrelated_nodes",
        "semantic_connectors_non_crossing",
        "semantic_arrowheads_clear_of_text",
        "semantic_relation_encoding_valid",
        "semantic_arrow_budget_met",
        "semantic_incoming_unambiguous",
        "semantic_bracket_spans_exact",
        "semantic_segmented_group_spans_exact",
        "semantic_segmented_group_perceptual_anchors_valid",
    ):
        assert semantic_audit["checks"][semantic_check] is True

    def semantic_violation_codes(candidate: Mapping[str, object]) -> set[str]:
        return {
            str(item["code"])
            for item in audit_layout_registry(candidate)["violations"]
        }

    def semantic_flow_item(
        candidate: Mapping[str, object],
        collection: str,
        identity_key: str,
        identity_value: str,
    ) -> dict[str, object]:
        return next(
            item
            for item in candidate["semantic_flow_contract"][collection]
            if item[identity_key] == identity_value
        )

    def semantic_artist_item(
        candidate: Mapping[str, object], artist_id: str
    ) -> dict[str, object]:
        return next(
            item
            for item in candidate["semantic_artist_registry"]["artists"]
            if item["artist_id"] == artist_id
        )

    missing_segmented_group = json.loads(json.dumps(semantic_fixture))
    missing_segmented_group["semantic_flow_contract"].pop("segmented_group_spans")
    assert "semantic_segmented_group_relation_set_mismatch" in (
        semantic_violation_codes(missing_segmented_group)
    )

    segmented_connector_to_child = json.loads(json.dumps(semantic_fixture))
    child_connector = semantic_flow_item(
        segmented_connector_to_child,
        "connectors",
        "connector_id",
        "band_source_to_group",
    )
    child_connector["destination_node_id"] = "band_child_a"
    child_connector["segments_px"][0] = [900, 420, 870, 280]
    child_segment_artist = semantic_artist_item(
        segmented_connector_to_child,
        "relation.band_partition.segment.1",
    )
    child_segment_artist["bbox_px"] = [870, 280, 900, 420]
    child_segment_artist["geometry_px"] = [900, 420, 870, 280]
    assert "semantic_segmented_group_connector_invalid" in (
        semantic_violation_codes(segmented_connector_to_child)
    )

    segmented_connector_arrowed = json.loads(json.dumps(semantic_fixture))
    semantic_flow_item(
        segmented_connector_arrowed,
        "connectors",
        "connector_id",
        "band_source_to_group",
    )["arrow_bearing"] = True
    assert "semantic_segmented_group_connector_invalid" in (
        semantic_violation_codes(segmented_connector_arrowed)
    )

    segmented_header_narrow = json.loads(json.dumps(semantic_fixture))
    narrow_group_node = semantic_flow_item(
        segmented_header_narrow, "nodes", "node_id", "band_group"
    )
    narrow_group_node["bbox_px"] = [850, 280, 950, 320]
    semantic_artist_item(
        segmented_header_narrow, "node.band_group.patch"
    )["bbox_px"] = [850, 280, 950, 320]
    semantic_flow_item(
        segmented_header_narrow,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["group_header_bbox_px"] = [850, 280, 950, 320]
    assert "semantic_segmented_group_span_mismatch" in (
        semantic_violation_codes(segmented_header_narrow)
    )

    segmented_children_gap = json.loads(json.dumps(semantic_fixture))
    gap_child_node = semantic_flow_item(
        segmented_children_gap, "nodes", "node_id", "band_child_b"
    )
    gap_child_node["bbox_px"] = [910, 180, 960, 280]
    semantic_artist_item(
        segmented_children_gap, "node.band_child_b.patch"
    )["bbox_px"] = [910, 180, 960, 280]
    assert "semantic_segmented_group_children_not_contiguous" in (
        semantic_violation_codes(segmented_children_gap)
    )

    segmented_children_overlap = json.loads(json.dumps(semantic_fixture))
    overlap_child_node = semantic_flow_item(
        segmented_children_overlap, "nodes", "node_id", "band_child_b"
    )
    overlap_child_node["bbox_px"] = [890, 180, 960, 280]
    semantic_artist_item(
        segmented_children_overlap, "node.band_child_b.patch"
    )["bbox_px"] = [890, 180, 960, 280]
    assert "semantic_segmented_group_children_not_contiguous" in (
        semantic_violation_codes(segmented_children_overlap)
    )

    segmented_header_detached = json.loads(json.dumps(semantic_fixture))
    detached_group_node = semantic_flow_item(
        segmented_header_detached, "nodes", "node_id", "band_group"
    )
    detached_group_node["bbox_px"] = [840, 300, 960, 340]
    semantic_artist_item(
        segmented_header_detached, "node.band_group.patch"
    )["bbox_px"] = [840, 300, 960, 340]
    semantic_flow_item(
        segmented_header_detached,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["group_header_bbox_px"] = [840, 300, 960, 340]
    assert "semantic_segmented_group_header_not_adjacent" in (
        semantic_violation_codes(segmented_header_detached)
    )

    segmented_side_anchor = json.loads(json.dumps(semantic_fixture))
    side_connector = semantic_flow_item(
        segmented_side_anchor,
        "connectors",
        "connector_id",
        "band_source_to_group",
    )
    side_connector["segments_px"][0] = [900, 420, 840, 300]
    side_artist = semantic_artist_item(
        segmented_side_anchor, "relation.band_partition.segment.1"
    )
    side_artist["bbox_px"] = [840, 300, 900, 420]
    side_artist["geometry_px"] = [900, 420, 840, 300]
    semantic_flow_item(
        segmented_side_anchor,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["actual_connector_terminal_px"] = [840, 300]
    assert "semantic_segmented_group_anchor_mismatch" in (
        semantic_violation_codes(segmented_side_anchor)
    )

    segmented_first_child_anchor = json.loads(json.dumps(semantic_fixture))
    first_child_connector = semantic_flow_item(
        segmented_first_child_anchor,
        "connectors",
        "connector_id",
        "band_source_to_group",
    )
    first_child_connector["segments_px"][0] = [900, 420, 870, 320]
    first_child_artist = semantic_artist_item(
        segmented_first_child_anchor, "relation.band_partition.segment.1"
    )
    first_child_artist["bbox_px"] = [870, 320, 900, 420]
    first_child_artist["geometry_px"] = [900, 420, 870, 320]
    semantic_flow_item(
        segmented_first_child_anchor,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["actual_connector_terminal_px"] = [870, 320]
    assert "semantic_segmented_group_anchor_mismatch" in (
        semantic_violation_codes(segmented_first_child_anchor)
    )
    assert (
        audit_layout_registry(segmented_first_child_anchor)[
            "semantic_validated_segmented_group_span_count"
        ]
        == 0
    )

    segmented_empty_label = json.loads(json.dumps(semantic_fixture))
    semantic_flow_item(
        segmented_empty_label,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["group_label"] = ""
    assert "semantic_segmented_group_label_empty" in (
        semantic_violation_codes(segmented_empty_label)
    )

    segmented_child_label = json.loads(json.dumps(semantic_fixture))
    child_label_span = semantic_flow_item(
        segmented_child_label,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )
    child_label_span["group_label"] = "Alive n=70"
    child_label_span["perceptual_anchor"][
        "label_artist_id"
    ] = "node.band_child_a.label"
    assert "semantic_segmented_group_label_artist_invalid" in (
        semantic_violation_codes(segmented_child_label)
    )

    segmented_orientation = json.loads(json.dumps(semantic_fixture))
    semantic_flow_item(
        segmented_orientation,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["orientation"] = "vertical"
    assert "semantic_segmented_group_orientation_invalid" in (
        semantic_violation_codes(segmented_orientation)
    )

    segmented_anchor_mode = json.loads(json.dumps(semantic_fixture))
    semantic_flow_item(
        segmented_anchor_mode,
        "segmented_group_spans",
        "relation_id",
        "band_partition",
    )["perceptual_anchor"]["mode"] = "first_child"
    assert "semantic_segmented_group_perceptual_anchor_invalid" in (
        semantic_violation_codes(segmented_anchor_mode)
    )

    segmented_renderer_geometry = json.loads(json.dumps(semantic_fixture))
    semantic_artist_item(
        segmented_renderer_geometry, "relation.band_partition.segment.1"
    )["geometry_px"] = [900, 420, 880, 320]
    assert "semantic_connector_geometry_mismatch" in (
        semantic_violation_codes(segmented_renderer_geometry)
    )

    missing_semantic_registry = json.loads(json.dumps(semantic_fixture))
    missing_semantic_registry.pop("semantic_artist_registry")
    missing_semantic_registry_audit = audit_layout_registry(
        missing_semantic_registry
    )
    assert "semantic_artist_registry_missing" in {
        item["code"] for item in missing_semantic_registry_audit["violations"]
    }

    missing_semantic_prefix = json.loads(json.dumps(semantic_fixture))
    missing_semantic_prefix["semantic_artist_registry"]["artists"] = [
        item
        for item in missing_semantic_prefix["semantic_artist_registry"]["artists"]
        if item["owner_prefix"] != "node.child_b"
    ]
    missing_semantic_prefix_audit = audit_layout_registry(missing_semantic_prefix)
    assert "semantic_artist_prefix_missing" in {
        item["code"] for item in missing_semantic_prefix_audit["violations"]
    }

    missing_semantic_kind = json.loads(json.dumps(semantic_fixture))
    missing_semantic_kind["semantic_flow_contract"]["expected_artist_kinds"].append(
        "ConnectionPatch"
    )
    missing_semantic_kind_audit = audit_layout_registry(missing_semantic_kind)
    assert "semantic_artist_kinds_missing" in {
        item["code"] for item in missing_semantic_kind_audit["violations"]
    }

    semantic_canvas_overflow = json.loads(json.dumps(semantic_fixture))
    semantic_canvas_overflow["semantic_artist_registry"]["artists"][1][
        "bbox_px"
    ] = [100, 180, 1020, 280]
    semantic_canvas_overflow_audit = audit_layout_registry(
        semantic_canvas_overflow
    )
    assert "semantic_artist_canvas_overflow" in {
        item["code"] for item in semantic_canvas_overflow_audit["violations"]
    }

    semantic_safe_inset = json.loads(json.dumps(semantic_fixture))
    semantic_safe_inset["semantic_artist_registry"]["artists"][1]["bbox_px"] = [
        10,
        180,
        300,
        280,
    ]
    semantic_safe_inset_audit = audit_layout_registry(semantic_safe_inset)
    assert "semantic_artist_safe_inset_violation" in {
        item["code"] for item in semantic_safe_inset_audit["violations"]
    }

    node_text_outside = json.loads(json.dumps(semantic_fixture))
    node_text_outside["semantic_flow_contract"]["nodes"][0]["text_artist_ids"] = [
        "node.child_b.label"
    ]
    node_text_outside_audit = audit_layout_registry(node_text_outside)
    assert "semantic_node_text_outside_node" in {
        item["code"] for item in node_text_outside_audit["violations"]
    }

    semantic_line_text = json.loads(json.dumps(semantic_fixture))
    semantic_line_text["semantic_flow_contract"]["connectors"][0]["segments_px"][
        0
    ] = [200, 485, 200, 350]
    semantic_line_text_audit = audit_layout_registry(semantic_line_text)
    assert "semantic_line_text_intersection" in {
        item["code"] for item in semantic_line_text_audit["violations"]
    }

    semantic_geometry_mismatch = json.loads(json.dumps(semantic_fixture))
    semantic_geometry_mismatch["semantic_flow_contract"]["connectors"][0][
        "segments_px"
    ][0] = [220, 420, 220, 350]
    semantic_geometry_mismatch_audit = audit_layout_registry(
        semantic_geometry_mismatch
    )
    assert "semantic_connector_geometry_mismatch" in {
        item["code"] for item in semantic_geometry_mismatch_audit["violations"]
    }

    semantic_artist_direction_mismatch = json.loads(json.dumps(semantic_fixture))
    direction_mismatch_artist = next(
        item
        for item in semantic_artist_direction_mismatch[
            "semantic_artist_registry"
        ]["artists"]
        if item["artist_id"] == "relation.root_partition.child_a.segment.1"
    )
    direction_mismatch_artist["geometry_px"] = [200, 350, 200, 420]
    semantic_artist_direction_mismatch_audit = audit_layout_registry(
        semantic_artist_direction_mismatch
    )
    assert "semantic_connector_geometry_mismatch" in {
        item["code"]
        for item in semantic_artist_direction_mismatch_audit["violations"]
    }

    semantic_source_anchor = json.loads(json.dumps(semantic_fixture))
    semantic_source_anchor["semantic_flow_contract"]["connectors"][0][
        "segments_px"
    ][0] = [200, 410, 200, 350]
    source_anchor_artist = next(
        item
        for item in semantic_source_anchor["semantic_artist_registry"]["artists"]
        if item["artist_id"] == "relation.root_partition.child_a.segment.1"
    )
    source_anchor_artist["bbox_px"] = [200, 350, 200, 410]
    source_anchor_artist["geometry_px"] = [200, 410, 200, 350]
    semantic_source_anchor_audit = audit_layout_registry(semantic_source_anchor)
    assert "semantic_connector_source_not_anchored" in {
        item["code"] for item in semantic_source_anchor_audit["violations"]
    }

    semantic_destination_anchor = json.loads(json.dumps(semantic_fixture))
    semantic_destination_anchor["semantic_flow_contract"]["connectors"][0][
        "segments_px"
    ][1] = [200, 350, 200, 250]
    destination_anchor_artist = next(
        item
        for item in semantic_destination_anchor["semantic_artist_registry"][
            "artists"
        ]
        if item["artist_id"] == "relation.root_partition.child_a.segment.2"
    )
    destination_anchor_artist["bbox_px"] = [200, 250, 200, 350]
    destination_anchor_artist["geometry_px"] = [200, 350, 200, 250]
    semantic_destination_anchor_audit = audit_layout_registry(
        semantic_destination_anchor
    )
    assert "semantic_connector_destination_not_anchored" in {
        item["code"] for item in semantic_destination_anchor_audit["violations"]
    }

    semantic_false_junction = json.loads(json.dumps(semantic_fixture))
    false_junction_connector = semantic_false_junction["semantic_flow_contract"][
        "connectors"
    ][0]
    false_junction_connector["segments_px"] = [
        [250, 420, 250, 350],
        [250, 350, 200, 280],
    ]
    for artist_id, bbox_px, geometry_px in (
        (
            "relation.root_partition.child_a.segment.1",
            [250, 350, 250, 420],
            [250, 420, 250, 350],
        ),
        (
            "relation.root_partition.child_a.segment.2",
            [200, 280, 250, 350],
            [250, 350, 200, 280],
        ),
    ):
        artist = next(
            item
            for item in semantic_false_junction["semantic_artist_registry"][
                "artists"
            ]
            if item["artist_id"] == artist_id
        )
        artist["bbox_px"] = bbox_px
        artist["geometry_px"] = geometry_px
    semantic_false_junction_audit = audit_layout_registry(
        semantic_false_junction
    )
    assert "semantic_junction_group_invalid" in {
        item["code"] for item in semantic_false_junction_audit["violations"]
    }

    semantic_line_node = json.loads(json.dumps(semantic_fixture))
    semantic_line_node["semantic_flow_contract"]["connectors"][0]["segments_px"][
        0
    ] = [600, 500, 600, 200]
    semantic_line_node_audit = audit_layout_registry(semantic_line_node)
    assert "semantic_line_unrelated_node_intersection" in {
        item["code"] for item in semantic_line_node_audit["violations"]
    }

    semantic_crossing = json.loads(json.dumps(semantic_fixture))
    semantic_crossing["semantic_flow_contract"]["connectors"][1][
        "junction_group"
    ] = "independent_connector"
    semantic_crossing["semantic_flow_contract"]["connectors"][1]["segments_px"][
        0
    ] = [100, 385, 300, 385]
    semantic_crossing_audit = audit_layout_registry(semantic_crossing)
    assert "semantic_connector_crossing_unauthorized" in {
        item["code"] for item in semantic_crossing_audit["violations"]
    }

    semantic_arrowhead_text = json.loads(json.dumps(semantic_fixture))
    semantic_arrowhead_text["semantic_artist_registry"]["artists"][10][
        "bbox_px"
    ] = [150, 455, 250, 485]
    semantic_arrowhead_text_audit = audit_layout_registry(
        semantic_arrowhead_text
    )
    assert "semantic_arrowhead_text_intersection" in {
        item["code"] for item in semantic_arrowhead_text_audit["violations"]
    }

    semantic_relation_encoding = json.loads(json.dumps(semantic_fixture))
    next(
        relation
        for relation in semantic_relation_encoding["semantic_flow_contract"][
            "relations"
        ]
        if relation["relation_id"] == "children_identity"
    )["encoding"] = "arrow_split"
    semantic_relation_encoding_audit = audit_layout_registry(
        semantic_relation_encoding
    )
    assert "semantic_relation_encoding_invalid" in {
        item["code"] for item in semantic_relation_encoding_audit["violations"]
    }

    semantic_arrow_budget = json.loads(json.dumps(semantic_fixture))
    semantic_arrow_budget["semantic_flow_contract"]["arrow_budget"] = 1
    semantic_arrow_budget_audit = audit_layout_registry(semantic_arrow_budget)
    assert "semantic_arrow_budget_exceeded" in {
        item["code"] for item in semantic_arrow_budget_audit["violations"]
    }

    semantic_ambiguous_incoming = json.loads(json.dumps(semantic_fixture))
    semantic_ambiguous_incoming["semantic_flow_contract"]["connectors"][1][
        "destination_node_id"
    ] = "child_a"
    semantic_ambiguous_incoming_audit = audit_layout_registry(
        semantic_ambiguous_incoming
    )
    assert "semantic_ambiguous_incoming_connectors" in {
        item["code"] for item in semantic_ambiguous_incoming_audit["violations"]
    }

    semantic_bracket_span = json.loads(json.dumps(semantic_fixture))
    semantic_bracket_span["semantic_flow_contract"]["brackets"][0][
        "observed_span_px"
    ] = [100, 690]
    semantic_bracket_span_audit = audit_layout_registry(semantic_bracket_span)
    assert "semantic_bracket_span_mismatch" in {
        item["code"] for item in semantic_bracket_span_audit["violations"]
    }

    semantic_bracket_geometry = json.loads(json.dumps(semantic_fixture))
    bracket_artist = next(
        item
        for item in semantic_bracket_geometry["semantic_artist_registry"]["artists"]
        if item["artist_id"] == "relation.children_identity.segment.1"
    )
    bracket_artist.pop("geometry_px")
    semantic_bracket_geometry_audit = audit_layout_registry(
        semantic_bracket_geometry
    )
    assert "semantic_bracket_geometry_invalid" in {
        item["code"] for item in semantic_bracket_geometry_audit["violations"]
    }

    fake_png = {
        "display_artifact_inventory_ref": {
            "sha256": "1" * 64,
            "size_bytes": 1000,
            "format": "PNG",
            "dimensions": {"width_px": 1800, "height_px": 1000},
            "page_count": 1,
        },
        "programmatic_figure_audit_ref": {"dpi": {"x": 254, "y": 254}},
        "export_integrity_ref": {"hard_fail": False},
    }
    fake_pdf = {
        "display_artifact_inventory_ref": {
            "sha256": "2" * 64,
            "size_bytes": 800,
            "format": "PDF",
            "dimensions": {
                "unit": "pt",
                "variants": [
                    {
                        "width_pt": 510.2362204724,
                        "height_pt": 283.4645669291,
                        "page_count": 1,
                    }
                ],
            },
            "page_count": 1,
        },
        "programmatic_figure_audit_ref": {"dpi": None},
        "export_integrity_ref": {"hard_fail": False},
    }
    receipt = build_layout_qc_receipt(fixture, [fake_png, fake_pdf])
    assert receipt["machine_check_status"] == "geometry_checks_passed"
    assert receipt["artifact_bindings"][1]["sha256"] == "1" * 64
    assert receipt["authority"] is False
    assert receipt["authority_boundary"]["can_claim_quality_verdict"] is False
    assert (
        receipt["semantic_artist_scope"]
        == "not_applicable:statistical_layout_regression"
    )
    assert receipt == build_layout_qc_receipt(fixture, [fake_pdf, fake_png])
    direct_labels = json.loads(json.dumps(fixture))
    direct_labels["annotation_lane_policy"] = "not_applicable"
    direct_labels["annotation_lane_reason"] = "Direct labels on one shared data canvas"
    direct_labels["lanes"]["plotting_data"]["bbox_px"] = [0, 0, 1800, 1000]
    direct_labels["lanes"].pop("annotation")
    for panel in direct_labels["panels"]:
        for artist in panel["text_artists"]:
            artist["lane"] = "plotting_data"
    assert audit_layout_registry(direct_labels)["violations"] == []
    unexplained_lane = json.loads(json.dumps(direct_labels))
    unexplained_lane.pop("annotation_lane_reason")
    try:
        audit_layout_registry(unexplained_lane)
    except ValueError as exc:
        assert "annotation_lane_reason" in str(exc)
    else:
        raise AssertionError("an inapplicable annotation lane requires its reason")
    overlapping_direct = json.loads(json.dumps(direct_labels))
    first, second = overlapping_direct["panels"][0]["text_artists"][:2]
    second["bbox_px"] = first["bbox_px"]
    assert "text_artist_overlap" in {
        item["code"] for item in audit_layout_registry(overlapping_direct)["violations"]
    }
    direct_labels["validation_scope"] = "artifact_acceptance"
    direct_labels["renderer_baseline_ref"] = {
        "kind": "renderer_regression_baseline",
        "ref": "artifact://renderer/tested-baseline.json",
        "sha256": "sha256:" + "3" * 64,
        "size_bytes": 400,
    }
    direct_labels.pop("fixture_id", None)
    direct_labels.pop("regression_fixture_refs", None)
    content_receipt = build_layout_qc_receipt(direct_labels, [fake_png, fake_pdf])
    assert content_receipt["machine_check_status"] == "geometry_checks_passed"
    assert content_receipt["regression_fixture_refs"] == []
    assert "plotting_data" in content_receipt["lane_bounds_px"]
    assert "annotation" not in content_receipt["lane_bounds_px"]
    direct_labels.pop("renderer_baseline_ref")
    assert "renderer_baseline_ref_invalid" in {
        item["code"]
        for item in build_layout_qc_receipt(direct_labels, [fake_png, fake_pdf])["violations"]
    }
    direct_labels["validation_scope"] = "renderer_regression"
    assert "regression_fixture_ref_missing" in {
        item["code"]
        for item in build_layout_qc_receipt(direct_labels, [fake_png, fake_pdf])["violations"]
    }
    wrong_size_pdf = json.loads(json.dumps(fake_pdf))
    wrong_size_pdf["display_artifact_inventory_ref"]["dimensions"]["variants"][0][
        "width_pt"
    ] = 500
    wrong_size_receipt = build_layout_qc_receipt(
        fixture, [fake_png, wrong_size_pdf]
    )
    assert wrong_size_receipt["machine_check_status"] == "geometry_checks_failed"
    assert "artifact_final_size_mismatch" in {
        item["code"] for item in wrong_size_receipt["violations"]
    }

    manual_wrap = json.loads(json.dumps(fixture))
    manual_wrap["panels"][0]["text_artists"][1]["text_measurement"][
        "manual_breaks"
    ] = True
    failed_layout = audit_layout_registry(manual_wrap)
    assert failed_layout["machine_check_status"] == "geometry_checks_failed"
    assert failed_layout["checks"]["measured_wrap_valid"] is False

    rendered_text_counterexample = json.loads(json.dumps(fixture))
    rendered_text_counterexample["panels"][0]["text_artists"][1][
        "rendered_text"
    ] = long_label["source_text"]
    rendered_text_audit = audit_layout_registry(rendered_text_counterexample)
    assert "semantic_wrap_rendered_text_mismatch" in {
        item["code"] for item in rendered_text_audit["violations"]
    }
    assert rendered_text_audit["checks"]["measured_wrap_valid"] is False

    semantic_break_counterexample = json.loads(json.dumps(fixture))
    semantic_break_counterexample["panels"][0]["text_artists"][1][
        "text_measurement"
    ]["semantic_wrap"]["break_after_word_indices"] = [3, 9]
    semantic_break_audit = audit_layout_registry(semantic_break_counterexample)
    assert "semantic_wrap_break_positions_mismatch" in {
        item["code"] for item in semantic_break_audit["violations"]
    }
    assert semantic_break_audit["checks"]["measured_wrap_valid"] is False

    boolean_line_count_counterexample = json.loads(json.dumps(fixture))
    boolean_line_count_counterexample["panels"][0]["text_artists"][2][
        "text_measurement"
    ]["line_count"] = True
    boolean_line_count_audit = audit_layout_registry(boolean_line_count_counterexample)
    assert "semantic_wrap_line_count_mismatch" in {
        item["code"] for item in boolean_line_count_audit["violations"]
    }
    assert boolean_line_count_audit["checks"]["measured_wrap_valid"] is False

    overlap = json.loads(json.dumps(fixture))
    overlap["panels"][0]["text_artists"][2]["bbox_px"] = [60, 230, 260, 260]
    clipping = json.loads(json.dumps(fixture))
    clipping["panels"][0]["text_artists"][1]["clip_bbox_px"] = [80, 180, 320, 250]
    overflow = json.loads(json.dumps(fixture))
    overflow["panels"][0]["text_artists"][5]["bbox_px"] = [1750, 900, 1810, 925]
    minimum_spacing = json.loads(json.dumps(fixture))
    minimum_spacing["panels"][0]["text_artists"][2]["bbox_px"] = [60, 255, 260, 280]
    unsafe = json.loads(json.dumps(fixture))
    unsafe["panels"][0]["text_artists"][1]["bbox_px"] = [20, 180, 340, 250]
    lane_overlap = json.loads(json.dumps(fixture))
    lane_overlap["lanes"]["annotation"]["bbox_px"] = [1400, 40, 1760, 960]
    wrong_lane = json.loads(json.dumps(fixture))
    wrong_lane["panels"][0]["text_artists"][3]["lane"] = "plotting_data"
    wrong_lane["panels"][0]["text_artists"][3]["bbox_px"] = [1200, 190, 1440, 220]
    wrong_lane["panels"][0]["text_artists"][3]["clip_bbox_px"] = [380, 40, 1460, 960]
    for broken_registry, expected_code in [
        (overlap, "text_artist_overlap"),
        (clipping, "artist_clipped"),
        (overflow, "artist_canvas_overflow"),
        (minimum_spacing, "text_artist_minimum_spacing_violation"),
        (unsafe, "artist_safe_inset_violation"),
        (lane_overlap, "data_annotation_lane_overlap"),
        (wrong_lane, "numeric_annotation_outside_annotation_lane"),
    ]:
        broken_audit = audit_layout_registry(broken_registry)
        assert expected_code in {item["code"] for item in broken_audit["violations"]}

    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        missing = inspect_display_artifact(root / "missing.png")
        assert missing["export_integrity_ref"]["hard_fail"] is True
        assert "artifact_missing" in missing["export_integrity_ref"]["finding_codes"]

        pillow_available = True
        fitz_available = False
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            pillow_available = False
            dependency_probe = root / "dependency-probe.png"
            dependency_probe.write_bytes(b"\x89PNG\r\n\x1a\n")
            dependency = inspect_display_artifact(dependency_probe)
            assert dependency["export_integrity_ref"]["hard_fail"] is False
            assert "dependency_missing" in dependency["export_integrity_ref"]["finding_codes"]
        else:
            blank_path = root / "blank.png"
            Image.new("RGB", (1200, 900), "white").save(blank_path, dpi=(300, 300))
            blank = inspect_display_artifact(blank_path)
            assert blank["export_integrity_ref"]["hard_fail"] is True
            assert "artifact_blank" in blank["export_integrity_ref"]["finding_codes"]

            transparent_path = root / "transparent.png"
            transparent_image = Image.new("RGBA", (1200, 900), (255, 0, 0, 0))
            ImageDraw.Draw(transparent_image).rectangle(
                (100, 100, 1100, 800), fill=(0, 0, 255, 0)
            )
            transparent_image.save(transparent_path, dpi=(300, 300))
            transparent = inspect_display_artifact(transparent_path)
            assert transparent["export_integrity_ref"]["hard_fail"] is True
            assert "artifact_blank" in transparent["export_integrity_ref"][
                "finding_codes"
            ]

            sparse_path = root / "sparse.png"
            sparse_image = Image.new("1", (6000, 6000), 1)
            sparse_image.putpixel((3000, 3000), 0)
            sparse_image.save(sparse_path, dpi=(300, 300))
            sparse = inspect_display_artifact(sparse_path)
            assert sparse["export_integrity_ref"]["hard_fail"] is False
            assert "artifact_blank" not in sparse["export_integrity_ref"]["finding_codes"]

            nonblank_image = Image.new("RGB", (1200, 900), "white")
            ImageDraw.Draw(nonblank_image).rectangle(
                (100, 100, 1100, 800), fill="black"
            )
            nonblank_path = root / "nonblank.png"
            nonblank_image.save(nonblank_path, dpi=(300, 300))
            nonblank = inspect_display_artifact(nonblank_path)
            audit = nonblank["programmatic_figure_audit_ref"]
            assert nonblank["export_integrity_ref"]["hard_fail"] is False
            assert audit["format"] == "PNG"
            assert audit["dimensions"] == {"width_px": 1200, "height_px": 900}
            assert audit["content_density"]["value"] > 0

            mismatched_path = root / "nonblank.jpg"
            mismatched_path.write_bytes(nonblank_path.read_bytes())
            mismatched = inspect_display_artifact(mismatched_path)
            assert mismatched["export_integrity_ref"]["hard_fail"] is False
            assert "artifact_format_suffix_mismatch" in mismatched[
                "export_integrity_ref"
            ]["finding_codes"]
            assert mismatched["programmatic_figure_audit_ref"]["format"] == "PNG"

            pdf_mismatched_path = root / "minimal.png"
            nonblank_image.save(pdf_mismatched_path, "PDF", resolution=150)
            pdf_mismatched = inspect_display_artifact(pdf_mismatched_path)
            assert pdf_mismatched["export_integrity_ref"]["hard_fail"] is False
            assert "artifact_format_suffix_mismatch" in pdf_mismatched[
                "export_integrity_ref"
            ]["finding_codes"]
            assert pdf_mismatched["programmatic_figure_audit_ref"]["format"] == "PDF"

            pdf_path = root / "minimal.pdf"
            nonblank_image.save(pdf_path, "PDF", resolution=150)
            pdf = inspect_display_artifact(pdf_path)
            pdf_audit = pdf["programmatic_figure_audit_ref"]
            assert pdf["export_integrity_ref"]["hard_fail"] is False
            assert pdf_audit["format"] == "PDF"
            if pdf_audit["page_count"] is None:
                assert "dependency_missing" in pdf["export_integrity_ref"]["finding_codes"]
            else:
                fitz_available = True
                assert pdf_audit["page_count"] == 1
                assert len(pdf_audit["page_pixel_hashes"]) == 1
                assert pdf_audit["page_pixel_hashes"][0]["pixel_format"] == "RGB8"
                fitz = _load_pymupdf()
                metadata_pdf_path = root / "minimal-with-metadata.pdf"
                metadata_document = fitz.open(pdf_path)
                metadata = dict(metadata_document.metadata or {})
                metadata["title"] = "metadata-only change"
                metadata_document.set_metadata(metadata)
                metadata_document.save(metadata_pdf_path)
                metadata_document.close()
                metadata_pdf = inspect_display_artifact(metadata_pdf_path)
                assert metadata_pdf["programmatic_figure_audit_ref"][
                    "page_pixel_hashes"
                ] == pdf_audit["page_pixel_hashes"]
                empty_pdf_path = root / "empty.pdf"
                document = fitz.open()
                document.new_page(width=612, height=792)
                document.save(empty_pdf_path)
                document.close()
                empty_pdf = inspect_display_artifact(empty_pdf_path)
                assert empty_pdf["export_integrity_ref"]["hard_fail"] is True

                sparse_pdf_path = root / "sparse.pdf"
                document = fitz.open()
                page = document.new_page(width=612, height=792)
                page.draw_rect(
                    fitz.Rect(300, 400, 300.01, 400.01),
                    color=None,
                    fill=(0, 0, 0),
                    width=0,
                )
                document.save(sparse_pdf_path)
                document.close()
                sparse_pdf = inspect_display_artifact(sparse_pdf_path)
                assert sparse_pdf["export_integrity_ref"]["hard_fail"] is False
                assert "artifact_blank" not in sparse_pdf["export_integrity_ref"][
                    "finding_codes"
                ]

        unsupported_path = root / "notes.txt"
        unsupported_path.write_text("not a rendered artifact", encoding="utf-8")
        unsupported = inspect_display_artifact(unsupported_path)
        assert unsupported["export_integrity_ref"]["hard_fail"] is False
        expected_code = "unsupported_format" if pillow_available else "dependency_missing"
        assert expected_code in unsupported["export_integrity_ref"]["finding_codes"]

    numbering_fixture_path = Path(KERNEL_FILE).with_name("fixtures") / "figure-numbering-one-owner.json"
    numbering_fixture = json.loads(numbering_fixture_path.read_text(encoding="utf-8"))
    numbering_candidate = numbering_fixture["candidate"]
    numbering_audit = validate_figure_numbering_one_owner(numbering_candidate)
    assert numbering_audit["machine_check_status"] == "candidate_complete"
    assert all(
        item["occurrence_count"] == 1
        for item in numbering_audit["figure_surface_invariants"]
    )
    for negative in numbering_fixture["negative_cases"]:
        changed = json.loads(json.dumps(numbering_candidate))
        figure = next(
            item for item in changed["figures"]
            if item["figure_id"] == negative["figure_id"]
        )
        occurrences = figure["output_surfaces"][negative["surface"]]["occurrences"]
        occurrence = next(
            item for item in occurrences if item["source"] == negative["source"]
        )
        occurrence["occurrence_count"] = negative["replacement_count"]
        changed_audit = validate_figure_numbering_one_owner(changed)
        assert negative["expected_code"] in {
            item["code"] for item in changed_audit["findings"]
        }
    checks = 132 if fitz_available else 125 if pillow_available else 112
    print(json.dumps({"ok": True, "checks": checks}, indent=2, sort_keys=True))
