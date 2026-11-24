"""Extracted pytest suite for skills/medical-submission-prep/kernel.py."""

from __future__ import annotations

from pathlib import Path
import json

from tests.kernels._loader import kernel_file, load_kernel

KERNEL = load_kernel("medical-submission-prep")
KERNEL_FILE = str(kernel_file("medical-submission-prep"))
build_author_input_todo_projection = KERNEL.build_author_input_todo_projection
lint_required_documents = KERNEL.lint_required_documents
lint_submission_artifact_roles = KERNEL.lint_submission_artifact_roles
package_manifest_skeleton = KERNEL.package_manifest_skeleton
required_documents = KERNEL.required_documents
select_publication_layout = KERNEL.select_publication_layout
submission_manifest_schema = KERNEL.submission_manifest_schema
validate_author_input_todo_projection = KERNEL.validate_author_input_todo_projection
validate_submission_figure_numbering_binding = KERNEL.validate_submission_figure_numbering_binding

def test_medical_submission_prep() -> None:
    assert "submission_inventory_ref" in submission_manifest_schema()["required"]
    assert "strobe_checklist" in required_documents("observational")
    assert "reviewer_response" in required_documents("observational", "revision")
    manifest = package_manifest_skeleton("Journal", "prediction")
    assert manifest["reporting_guideline_ref"] == "TRIPOD"
    lint = lint_required_documents({"files": [{"kind": "manuscript", "name": "main file.docx"}]})
    assert {item["code"] for item in lint} >= {"MISSING_REQUIRED_DOCUMENT", "FILE_NAME_HAS_SPACES"}
    digest = "1" * 64
    role_findings = lint_submission_artifact_roles(
        [
            {
                "path": "internal/supplement-review.pdf",
                "kind": "review_companion",
                "package_role": "internal_review",
                "included_in_submission": True,
                "sha256": digest,
            },
            {
                "path": "submission/supplement.pdf",
                "kind": "supplementary_document",
                "package_role": "supplementary_material",
                "source_role": "review_companion",
                "document_role": "main_document",
                "visible_title": "Supplementary Table Review Companion",
                "included_in_submission": True,
                "sha256": digest,
            },
        ]
    )
    assert {item["code"] for item in role_findings} == {
        "INTERNAL_REVIEW_ARTIFACT_EXPOSED_TO_JOURNAL",
        "INTERNAL_REVIEW_LANGUAGE_ON_SUBMISSION_ARTIFACT",
        "SUPPLEMENT_ARTIFACT_ROLE_MISMATCH",
        "SUPPLEMENTARY_MEMBER_IN_MAIN_DOCUMENT",
        "CONFLICTING_PACKAGE_ROLES_FOR_SAME_BYTES",
    }
    assert all(item["writes_authority"] is False for item in role_findings)
    default_layout = select_publication_layout(as_of_date="2026-07-20")
    assert default_layout["selected_profile_id"] == "general-medical-reader.v1"
    assert default_layout["core_pdf_outputs"] == [
        "paper.pdf",
        "paper_with_supplementary.pdf",
    ]
    journal_layout = select_publication_layout(
        "JAMA Network Open", as_of_date="2026-07-20"
    )
    assert journal_layout["selected_profile_id"] == "jama-network-research.v1"
    frontiers_layout = select_publication_layout(
        "Frontiers in Cardiology", as_of_date="2026-07-20"
    )
    assert frontiers_layout["selected_profile_id"] == "frontiers-research-article.v1"
    frontier_false_positive = select_publication_layout(
        "Frontier Medicine", as_of_date="2026-07-20"
    )
    assert frontier_false_positive["selected_profile_id"] == "general-medical-reader.v1"
    unknown_layout = select_publication_layout(
        "Unknown Journal", as_of_date="2026-07-20"
    )
    assert unknown_layout["authoring_may_continue"] is True
    assert unknown_layout["official_refresh_required"] is True
    formal_layout = select_publication_layout(
        "NEJM", formal_submission=True, as_of_date="2026-07-20"
    )
    assert formal_layout["official_refresh_required"] is True
    assert formal_layout["can_claim_journal_compliance"] is False
    numbering_fixture_path = (
        Path(KERNEL_FILE).parents[1]
        / "medical-display-qc"
        / "fixtures"
        / "figure-numbering-one-owner.json"
    )
    numbering_fixture = json.loads(numbering_fixture_path.read_text(encoding="utf-8"))
    binding_audit = validate_submission_figure_numbering_binding(
        numbering_fixture["submission_binding_candidate"]
    )
    assert binding_audit["machine_check_status"] == "candidate_complete"
    bad_binding = json.loads(json.dumps(numbering_fixture["submission_binding_candidate"]))
    bad_binding["audit_summary"]["figure_surface_invariants"][0]["occurrence_count"] = 2
    assert "SUBMISSION_FIGURE_NUMBERING_EXACTLY_ONE_VIOLATION" in {
        item["code"] for item in validate_submission_figure_numbering_binding(bad_binding)["findings"]
    }
    registry = {
        "surface_kind": "medical_author_input_registry.v1",
        "schema_version": 1,
        "items": [
            {
                "id": "A01",
                "category": "author_metadata",
                "required_input": "Author names and affiliations",
                "responsible_owner": "author team",
                "blocks_formal_submission": True,
                "placements": [
                    {
                        "placement_id": "A01-M01",
                        "surface_kind": "manuscript_text",
                        "surface_ref": "manuscript.md",
                        "section": "title page",
                        "exact_annotation": "[AUTHOR INPUT: insert author names and affiliations.]",
                    }
                ],
            }
        ],
    }
    todo_projection = build_author_input_todo_projection(registry)
    assert todo_projection["counts"]["main_manuscript_annotation_count"] == 1
    assert (
        validate_author_input_todo_projection(registry, todo_projection)[
            "machine_check_status"
        ]
        == "candidate_complete"
    )
    stale_projection = json.loads(json.dumps(todo_projection))
    stale_projection["counts"]["main_manuscript_annotation_count"] = 0
    assert {
        item["code"]
        for item in validate_author_input_todo_projection(
            registry, stale_projection
        )["findings"]
    } == {"AUTHOR_INPUT_TODO_PROJECTION_MISMATCH"}
    print(json.dumps({"ok": True, "checks": 20}, indent=2, sort_keys=True))
