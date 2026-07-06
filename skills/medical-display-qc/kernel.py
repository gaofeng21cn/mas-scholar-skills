"""Deterministic refs-only helpers for medical display QC.

These helpers normalize evidence refs and scaffold QC candidate refs. They do
not inspect files, mutate artifacts, sign receipts, or claim readiness.
"""

from __future__ import annotations

import json
import re
from typing import Any, Mapping


DISPLAY_QC_REFS = (
    "display_artifact_inventory_ref",
    "export_integrity_ref",
    "panel_caption_consistency_ref",
    "claim_display_alignment_ref",
    "accessibility_and_size_ref",
    "display_qc_support_map_ref",
)

QC_ROUTE_RULES = (
    ("artifact_owner_repair", ("blank", "missing", "broken", "export", "link")),
    ("display_redesign", ("overlap", "readability", "font", "contrast", "color")),
    ("source_data_mismatch", ("denominator", "estimate", "uncertainty", "group", "ordering")),
    ("caption_numbering_repair", ("caption", "legend", "panel", "letter", "numbering")),
    ("owner_visual_audit_decision", ("accept", "approve", "publication", "readiness")),
)


def normalize_evidence_ref(value: object) -> str:
    """Normalize a display evidence ref without resolving or reading it."""

    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .;,")


def display_artifact_row(
    artifact_ref: object,
    *,
    page_ref: object = "",
    panel_ref: object = "",
    caption_ref: object = "",
    claim_ref: object = "",
) -> dict[str, Any]:
    """Return a refs-only display artifact inventory row."""

    return {
        "artifact_ref": normalize_evidence_ref(artifact_ref),
        "page_ref": normalize_evidence_ref(page_ref),
        "panel_ref": normalize_evidence_ref(panel_ref),
        "caption_ref": normalize_evidence_ref(caption_ref),
        "claim_ref": normalize_evidence_ref(claim_ref),
        "qc_candidate_ref": "",
        "route_back_candidate": "",
        "writes_authority": False,
    }


def display_qc_skeleton(artifact_ref: object) -> dict[str, Any]:
    """Return the display QC candidate package skeleton."""

    return {
        "surface_kind": "display_qc_candidate",
        "artifact_ref": normalize_evidence_ref(artifact_ref),
        "required_refs": list(DISPLAY_QC_REFS),
        "candidate_refs": {ref: None for ref in DISPLAY_QC_REFS},
        "candidate_package_ref": None,
        "route_back_candidate": None,
        "owner_gate_handoff_ref": None,
        "authority": {
            "refs_only": True,
            "can_mutate_artifacts": False,
            "can_write_mas_truth": False,
            "can_sign_visual_audit_receipt": False,
            "can_sign_owner_receipt": False,
            "can_create_typed_blocker": False,
            "can_claim_publication_readiness": False,
        },
    }


def classify_display_qc_route(issue_text: object) -> dict[str, str]:
    """Classify a QC issue into a route-back hint, not an authority verdict."""

    text = str(issue_text or "").lower()
    for route, keywords in QC_ROUTE_RULES:
        if any(re.search(rf"\b{re.escape(keyword)}\b", text) for keyword in keywords):
            return {"route": route, "reason": f"matched {route}"}
    return {"route": "display_qc_review_hint", "reason": "default refs-only QC hint"}


def display_qc_support_map(
    rows: list[Mapping[str, object]],
) -> list[dict[str, str | bool]]:
    """Normalize artifact-to-evidence rows for display QC handoff."""

    out: list[dict[str, str | bool]] = []
    for row in rows:
        issue = normalize_evidence_ref(row.get("issue") or row.get("finding"))
        route = normalize_evidence_ref(
            row.get("route_back_candidate") or classify_display_qc_route(issue)["route"]
        )
        out.append(
            {
                "artifact_ref": normalize_evidence_ref(row.get("artifact_ref")),
                "evidence_ref": normalize_evidence_ref(row.get("evidence_ref")),
                "issue": issue,
                "route_back_candidate": route,
                "writes_authority": False,
            }
        )
    return out


def lint_forbidden_display_qc_claims(text: str) -> list[str]:
    """Return forbidden authority phrases found in display QC prose."""

    patterns = (
        r"\bfigure accepted\b",
        r"\bartifact accepted\b",
        r"\bvisual audit receipt\b",
        r"\bowner receipt\b",
        r"\btyped blocker\b",
        r"\bpublication-ready\b",
        r"\bpublication readiness\b",
    )
    return [pattern for pattern in patterns if re.search(pattern, text, flags=re.I)]


def _self_check() -> None:
    assert normalize_evidence_ref("  fig:1 ;") == "fig:1"
    row = display_artifact_row("artifact:pdf", page_ref=" page 2 ", panel_ref="A")
    assert row["writes_authority"] is False
    skeleton = display_qc_skeleton("artifact:pdf")
    assert "display_qc_support_map_ref" in skeleton["required_refs"]
    assert skeleton["authority"]["can_sign_visual_audit_receipt"] is False
    assert classify_display_qc_route("blank exported panel")["route"] == "artifact_owner_repair"
    support = display_qc_support_map([{"artifact_ref": "fig:1", "issue": "caption drift"}])
    assert support[0]["route_back_candidate"] == "caption_numbering_repair"
    assert lint_forbidden_display_qc_claims("publication-ready with owner receipt")
    print(json.dumps({"ok": True, "checks": 7}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
