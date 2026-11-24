"""Extracted pytest suite for skills/medical-reference-integrity-auditor/kernel.py."""

from __future__ import annotations

from pathlib import Path
import json

from tests.kernels._loader import kernel_file, load_kernel

KERNEL = load_kernel("medical-reference-integrity-auditor")
KERNEL_FILE = str(kernel_file("medical-reference-integrity-auditor"))
audit_active_reference_currentness = KERNEL.audit_active_reference_currentness
audit_citation_source_coverage = KERNEL.audit_citation_source_coverage
audit_citation_source_coverage_v2 = KERNEL.audit_citation_source_coverage_v2
audit_claim_citation_edge_completeness = KERNEL.audit_claim_citation_edge_completeness
audit_excluded_reference_ledger = KERNEL.audit_excluded_reference_ledger
audit_reference_lane_active_inventory_binding = KERNEL.audit_reference_lane_active_inventory_binding
lint_reference_identifiers = KERNEL.lint_reference_identifiers
normalize_doi = KERNEL.normalize_doi
normalize_pmcid = KERNEL.normalize_pmcid
normalize_pmid = KERNEL.normalize_pmid
reference_inventory_skeleton = KERNEL.reference_inventory_skeleton
validate_post_csl_reader_semantics = KERNEL.validate_post_csl_reader_semantics

def test_medical_reference_integrity_auditor() -> None:
    def exact_ref(tag: str) -> dict[str, object]:
        return {
            "kind": "reference_evidence",
            "ref": f"evidence://{tag}",
            "size_bytes": 100,
            "sha256": "sha256:" + "a" * 64,
        }

    active_inventory_ref = exact_ref("active-inventory")

    assert normalize_doi("https://doi.org/10.1000/ABC.") == "10.1000/abc"
    assert normalize_pmid("PMID: 12345") == "12345"
    assert normalize_pmcid("pmc987") == "PMC987"
    refs = [{"title": "A Trial", "doi": "10.1/A"}, {"title": "B", "doi": "10.1/a"}]
    assert lint_reference_identifiers(refs)[0]["code"] == "DUPLICATE_REFERENCE_KEY"
    assert reference_inventory_skeleton(["ref1"])[0]["citation_key"] == "ref1"
    empty_coverage = audit_citation_source_coverage_v2(
        {
            "active_inventory_ref": active_inventory_ref,
            "manuscript_citation_keys": [],
            "bibliography_records": [],
            "source_context_keys": [],
            "claim_map_keys": [],
            "authority": False,
        }
    )
    assert {
        "CITATION_MANUSCRIPT_KEY_SET_EMPTY",
        "CITATION_BIBLIOGRAPHY_KEY_SET_EMPTY",
    }.issubset({item["code"] for item in empty_coverage["findings"]})
    manuscript_keys = [f"ref{index:02d}" for index in range(1, 22)]
    incomplete_coverage = audit_citation_source_coverage_v2(
        {
            "active_inventory_ref": active_inventory_ref,
            "manuscript_citation_keys": manuscript_keys,
            "bibliography_records": [
                {"citation_key": key} for key in manuscript_keys[:8]
            ],
            "source_context_keys": manuscript_keys,
            "claim_map_keys": manuscript_keys,
            "authority": False,
        }
    )
    assert incomplete_coverage["manuscript_citation_key_count"] == 21
    assert incomplete_coverage["bibliography_key_count"] == 8
    assert incomplete_coverage["missing_bibliography_keys"] == [
        f"ref{index:02d}" for index in range(9, 22)
    ]
    incomplete_source_context = audit_citation_source_coverage_v2(
        {
            "active_inventory_ref": active_inventory_ref,
            "manuscript_citation_keys": manuscript_keys,
            "bibliography_records": [
                {"citation_key": key} for key in manuscript_keys
            ],
            "source_context_keys": manuscript_keys[:8],
            "claim_map_keys": manuscript_keys,
            "authority": False,
        }
    )
    assert incomplete_source_context["source_context_key_count"] == 8
    assert incomplete_source_context["missing_source_context_keys"] == [
        f"ref{index:02d}" for index in range(9, 22)
    ]
    complete_coverage = audit_citation_source_coverage_v2(
        {
            "active_inventory_ref": active_inventory_ref,
            "manuscript_citation_keys": manuscript_keys,
            "bibliography_records": [
                {"citation_key": key} for key in manuscript_keys
            ],
            "source_context_keys": manuscript_keys,
            "claim_map_keys": manuscript_keys,
            "authority": False,
        }
    )
    assert complete_coverage["machine_check_status"] == "candidate_complete"
    legacy_coverage_candidate = {
        "manuscript_citation_keys": manuscript_keys,
        "bibliography_records": [
            {"citation_key": key} for key in manuscript_keys
        ],
        "source_context_keys": manuscript_keys,
        "claim_map_keys": manuscript_keys,
        "authority": False,
    }
    legacy_coverage = audit_citation_source_coverage(legacy_coverage_candidate)
    strict_legacy_coverage = audit_citation_source_coverage_v2(
        legacy_coverage_candidate
    )
    assert legacy_coverage["machine_check_status"] == "candidate_complete"
    assert "active_inventory_ref" not in legacy_coverage
    assert strict_legacy_coverage["machine_check_status"] == "route_back_required"
    active_currentness = audit_active_reference_currentness(
        {
            "active_inventory_ref": active_inventory_ref,
            "active_keys": ["A", "B"],
            "records": [
                {
                    "citation_key": key,
                    "title": f"Source {key}",
                    "year": "2025",
                    "stable_identifier": f"pmid:{index}",
                    "status": "verified_current",
                    "metadata_source_ref": exact_ref(f"metadata-{key}"),
                    "source_context_ref": exact_ref(f"context-{key}"),
                    "currentness_evidence_ref": exact_ref(f"currentness-{key}"),
                    "reason": None,
                }
                for index, key in enumerate(("A", "B"), start=1)
            ],
            "authority": False,
        }
    )
    assert active_currentness["machine_check_status"] == "candidate_complete"
    open_currentness = audit_active_reference_currentness(
        {
            "active_inventory_ref": active_inventory_ref,
            "active_keys": ["A"],
            "records": [
                {
                    "citation_key": "A",
                    "title": "Source A",
                    "year": "2025",
                    "stable_identifier": "doi:10.1/a",
                    "status": "open_currentness",
                    "metadata_source_ref": exact_ref("metadata-A"),
                    "source_context_ref": exact_ref("context-A"),
                    "currentness_evidence_ref": None,
                    "reason": "publisher status remains unresolved",
                }
            ],
            "authority": False,
        }
    )
    assert open_currentness["open_currentness_keys"] == ["a"]
    malformed_currentness = {
        "active_inventory_ref": active_inventory_ref,
        "active_keys": ["A"],
        "records": [
            {
                "citation_key": "A",
                "title": "Source A",
                "year": "2025",
                "stable_identifier": "doi:10.1/a",
                "status": "verified_current",
                "metadata_source_ref": exact_ref("metadata-A"),
                "source_context_ref": exact_ref("context-A"),
                "currentness_evidence_ref": exact_ref("currentness-A"),
                "reason": None,
            }
        ],
        "authority": False,
    }
    malformed_currentness["records"][0]["currentness_evidence_ref"].pop(
        "size_bytes"
    )
    assert "REFERENCE_EVIDENCE_EXACT_REF_INVALID" in {
        item["code"]
        for item in audit_active_reference_currentness(malformed_currentness)[
            "findings"
        ]
    }
    excluded_ok = audit_excluded_reference_ledger(
        {
            "active_inventory_ref": active_inventory_ref,
            "active_keys": ["A", "B"],
            "excluded_records": [
                {
                    "citation_key": "X",
                    "exclusion_reason": "not needed for active claim set",
                    "prior_role": "background",
                    "unresolved_status": "open_currentness",
                    "reintroduction_gate": "currentness and claim support required",
                    "clearance_status": "uncleared",
                    "currentness_reopened_ref": None,
                    "claim_edge_reopened_ref": None,
                }
            ],
            "authority": False,
        }
    )
    assert excluded_ok["machine_check_status"] == "candidate_complete"
    reintroduced = audit_excluded_reference_ledger(
        {
            "active_inventory_ref": active_inventory_ref,
            "active_keys": ["A", "X"],
            "excluded_records": [
                {
                    "citation_key": "X",
                    "exclusion_reason": "status unresolved",
                    "prior_role": "background",
                    "unresolved_status": "cleared_for_reintroduction",
                    "reintroduction_gate": "currentness and claim support required",
                    "clearance_status": "reintroduced",
                    "currentness_reopened_ref": exact_ref("X-currentness-reopened"),
                    "claim_edge_reopened_ref": exact_ref("X-edge-reopened"),
                }
            ],
            "authority": False,
        }
    )
    assert reintroduced["reintroduced_keys"] == ["x"]
    assert reintroduced["machine_check_status"] == "candidate_complete"
    uncleared_reintroduction = audit_excluded_reference_ledger(
        {
            "active_inventory_ref": active_inventory_ref,
            "active_keys": ["A", "X"],
            "excluded_records": [
                {
                    "citation_key": "X",
                    "exclusion_reason": "status unresolved",
                    "prior_role": "background",
                    "unresolved_status": "open_currentness",
                    "reintroduction_gate": "currentness and claim support required",
                    "clearance_status": "uncleared",
                    "currentness_reopened_ref": None,
                    "claim_edge_reopened_ref": None,
                }
            ],
            "authority": False,
        }
    )
    assert "EXCLUDED_REFERENCE_REINTRODUCED_WITHOUT_CLEARANCE" in {
        item["code"] for item in uncleared_reintroduction["findings"]
    }
    edge = {
        "claim_id": "claim-1",
        "citation_key": "A",
        "claim_text": "A bounded claim",
        "support_type": "direct_primary",
        "locator": "p. 4, Results",
        "excerpt": "Exact supporting passage.",
        "population_fit": "matched",
        "endpoint_fit": "matched",
        "method_fit": "matched",
        "support_boundary": "association only",
        "source_support_ref": exact_ref("claim-1-source-support"),
    }
    edge_audit = audit_claim_citation_edge_completeness(
        {
            "active_inventory_ref": active_inventory_ref,
            "active_keys": ["A"],
            "edges": [edge],
            "authority": False,
        }
    )
    assert edge_audit["machine_check_status"] == "candidate_complete"
    missing_locator = dict(edge, locator="")
    missing_locator_audit = audit_claim_citation_edge_completeness(
        {
            "active_inventory_ref": active_inventory_ref,
            "active_keys": ["A"],
            "edges": [missing_locator],
            "authority": False,
        }
    )
    assert "CLAIM_CITATION_EDGE_FIELD_MISSING" in {
        item["code"] for item in missing_locator_audit["findings"]
    }
    missing_support_hash = json.loads(json.dumps(edge))
    missing_support_hash["source_support_ref"].pop("sha256")
    assert "REFERENCE_EVIDENCE_EXACT_REF_INVALID" in {
        item["code"]
        for item in audit_claim_citation_edge_completeness(
            {
                "active_inventory_ref": active_inventory_ref,
                "active_keys": ["A"],
                "edges": [missing_support_hash],
                "authority": False,
            }
        )["findings"]
    }
    lane_binding_candidate = {
        "lanes": {
            "citation_source_coverage": {
                "active_inventory_ref": active_inventory_ref,
                "manuscript_citation_keys": ["A"],
            },
            "active_reference_currentness": {
                "active_inventory_ref": active_inventory_ref,
                "active_keys": ["A"],
            },
            "excluded_reference_ledger": {
                "active_inventory_ref": active_inventory_ref,
                "active_keys": ["A"],
            },
            "claim_citation_edge_completeness": {
                "active_inventory_ref": active_inventory_ref,
                "active_keys": ["A"],
            },
        },
        "authority": False,
    }
    assert audit_reference_lane_active_inventory_binding(lane_binding_candidate)[
        "machine_check_status"
    ] == "candidate_complete"
    mismatched_lane_inventory = json.loads(json.dumps(lane_binding_candidate))
    mismatched_lane_inventory["lanes"]["claim_citation_edge_completeness"][
        "active_inventory_ref"
    ]["sha256"] = "sha256:" + "b" * 64
    assert "REFERENCE_LANE_ACTIVE_INVENTORY_MISMATCH" in {
        item["code"]
        for item in audit_reference_lane_active_inventory_binding(
            mismatched_lane_inventory
        )["findings"]
    }
    empty_lane_bypass = json.loads(json.dumps(lane_binding_candidate))
    empty_lane_bypass["lanes"]["excluded_reference_ledger"]["active_keys"] = []
    assert {
        "REFERENCE_LANE_ACTIVE_KEY_SET_EMPTY",
        "REFERENCE_LANE_ACTIVE_KEY_SET_MISMATCH",
    }.issubset(
        {
            item["code"]
            for item in audit_reference_lane_active_inventory_binding(
                empty_lane_bypass
            )["findings"]
        }
    )
    post_csl_fixture_path = Path(KERNEL_FILE).with_name("fixtures") / "post-csl-reader-semantics.json"
    post_csl_fixture = json.loads(post_csl_fixture_path.read_text(encoding="utf-8"))
    post_csl_candidate = post_csl_fixture["candidate"]
    post_csl_audit = validate_post_csl_reader_semantics(post_csl_candidate)
    assert post_csl_audit["machine_check_status"] == "candidate_complete"
    for negative in post_csl_fixture["negative_cases"]:
        changed = json.loads(json.dumps(post_csl_candidate))
        entries = changed["output_surfaces"][negative["surface"]]["rendered_entries"]
        entry = next(item for item in entries if item["semantic_id"] == negative["semantic_id"])
        entry[negative["field"]] = negative["replacement"]
        changed_audit = validate_post_csl_reader_semantics(changed)
        assert changed_audit["machine_check_status"] == "route_back_required"
        assert negative["expected_code"] in {
            item["code"] for item in changed_audit["findings"]
        }
    print(json.dumps({"ok": True, "checks": 35}, indent=2, sort_keys=True))
