"""Deterministic refs-only helpers for medical manuscript review.

These helpers scaffold review facts, matrices, and labels. They do not issue
MAS reviewer receipts, owner receipts, typed blockers, verdicts, or readiness.
"""

from __future__ import annotations

import json
import re
from typing import Any


REVIEW_ACTIONS = (
    "accept_as_is",
    "claim_downgrade",
    "citation_repair",
    "manuscript_repair",
    "display_repair",
    "analysis_campaign_route_back",
    "decision_route_back",
    "human_gate",
    "stop",
)

ISSUE_RULES = (
    ("citation_repair", ("citation", "reference", "pmid", "source", "uncited")),
    ("display_repair", ("figure", "caption", "panel", "table", "display")),
    ("analysis_campaign_route_back", ("analysis", "sensitivity", "model", "calibration")),
    ("claim_downgrade", ("causal", "prove", "burden", "prevalence", "overclaim")),
    ("human_gate", ("ethics", "consent", "coi", "funding", "data availability")),
)


def review_fact_base_schema() -> dict[str, Any]:
    """Return the shared fact-base schema for AI reviewer judgment."""

    return {
        "type": "object",
        "required": [
            "manuscript_type",
            "central_claim",
            "evidence_shown_refs",
            "evidence_missing_refs",
            "surfaces_under_review",
        ],
        "properties": {
            "manuscript_type": {"type": "string"},
            "submission_posture": {"type": "string"},
            "central_claim": {"type": "string"},
            "bounded_contribution": {"type": "string"},
            "evidence_shown_refs": {"type": "array", "items": {"type": "string"}},
            "evidence_missing_refs": {"type": "array", "items": {"type": "string"}},
            "likely_readership": {"type": "string"},
            "technical_gap_refs": {"type": "array", "items": {"type": "string"}},
            "surfaces_under_review": {"type": "array", "items": {"type": "string"}},
        },
    }


def review_matrix_skeleton(
    concerns: list[str] | None = None, lanes: list[str] | None = None
) -> list[dict[str, str]]:
    """Return a reviewer action matrix skeleton."""

    lane_names = lanes or ["technical", "significance", "reader", "validity_bias"]
    if concerns:
        return [_matrix_row(concern, "auto", classify_issue(concern)["action"]) for concern in concerns]
    return [_matrix_row("", lane, "") for lane in lane_names]


def classify_issue(issue_text: str) -> dict[str, str]:
    """Classify a review issue into the narrowest refs-only action label."""

    text = issue_text.lower()
    for action, keywords in ISSUE_RULES:
        if any(re.search(rf"\b{re.escape(keyword)}\b", text) for keyword in keywords):
            return {"action": action, "reason": f"matched {action}"}
    return {"action": "manuscript_repair", "reason": "default manuscript repair"}


def claim_citation_figure_matrix_skeleton(
    claims: list[str | dict[str, Any]]
) -> list[dict[str, str]]:
    """Return claim-citation-figure review rows without judging readiness."""

    rows: list[dict[str, str]] = []
    for index, item in enumerate(claims, start=1):
        if isinstance(item, dict):
            claim_ref = str(item.get("claim_ref") or f"claim_{index}")
            claim = str(item.get("claim", ""))
            citation_ref = str(item.get("citation_ref", ""))
            figure_ref = str(item.get("figure_ref", ""))
        else:
            claim_ref = f"claim_{index}"
            claim = str(item)
            citation_ref = ""
            figure_ref = ""
        rows.append(
            {
                "claim_ref": claim_ref,
                "claim": claim,
                "citation_ref": citation_ref,
                "figure_or_table_ref": figure_ref,
                "support_status": "",
                "review_action": "",
                "route_back_candidate": "",
            }
        )
    return rows


def _matrix_row(concern: str, lane: str, action: str) -> dict[str, str]:
    return {
        "review_lane": lane,
        "concern": concern,
        "evidence_ref": "",
        "affected_text_or_display_ref": "",
        "action": action,
        "owner_surface": "",
        "route_back_candidate": "",
    }


def _self_check() -> None:
    assert "central_claim" in review_fact_base_schema()["required"]
    assert classify_issue("Figure caption drifts")["action"] == "display_repair"
    assert classify_issue("missing citation")["action"] == "citation_repair"
    assert review_matrix_skeleton(["causal overclaim"])[0]["action"] == "claim_downgrade"
    assert claim_citation_figure_matrix_skeleton(["A"])[0]["claim_ref"] == "claim_1"
    print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
