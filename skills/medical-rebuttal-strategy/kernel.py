"""Deterministic refs-only helpers for medical rebuttal strategy.

These helpers normalize reviewer-comment refs and scaffold response strategy
candidate refs. They do not sign reviewer receipts, mutate artifacts, or claim
acceptance/readiness.
"""

from __future__ import annotations

import json
import re
from typing import Any, Mapping


REBUTTAL_REFS = (
    "review_comment_inventory_ref",
    "response_route_ref",
    "evidence_response_map_ref",
    "manuscript_delta_plan_ref",
    "rebuttal_strategy_ref",
    "stop_or_continue_recommendation",
)

RESPONSE_ROUTE_RULES = (
    ("analysis_statistics_route_back", ("analysis", "statistics", "sensitivity", "model")),
    ("table_figure_change", ("figure", "table", "panel", "caption")),
    ("literature_support", ("citation", "reference", "literature", "pmid")),
    ("data_source_owner_decision", ("data", "cohort", "access", "source")),
    ("manuscript_revision", ("clarify", "rewrite", "tone", "discussion", "limitation")),
    ("non_actionable_boundary", ("outside scope", "not possible", "policy", "journal")),
)


def normalize_comment_id(value: object) -> str:
    """Normalize reviewer comment ids for deterministic maps."""

    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def normalize_evidence_ref(value: object) -> str:
    """Normalize an evidence ref without resolving it."""

    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .;,")


def review_comment_row(
    comment_id: object,
    source: object,
    requested_action: object,
    *,
    target_ref: object = "",
    evidence_need: object = "",
) -> dict[str, Any]:
    """Return a refs-only reviewer-comment inventory row."""

    return {
        "comment_id": normalize_comment_id(comment_id),
        "source": normalize_evidence_ref(source),
        "target_ref": normalize_evidence_ref(target_ref),
        "requested_action": str(requested_action or "").strip(),
        "evidence_need": normalize_evidence_ref(evidence_need),
        "response_route": "",
        "owner_decision_target": "",
        "writes_authority": False,
    }


def classify_response_route(comment_text: object) -> dict[str, str]:
    """Classify a reviewer comment into a refs-only response route."""

    text = str(comment_text or "").lower()
    for route, keywords in RESPONSE_ROUTE_RULES:
        if any(re.search(rf"\b{re.escape(keyword)}\b", text) for keyword in keywords):
            return {"route": route, "reason": f"matched {route}"}
    return {"route": "answer_in_text", "reason": "default text response route"}


def rebuttal_strategy_skeleton(review_ref: object) -> dict[str, Any]:
    """Return the rebuttal strategy candidate package skeleton."""

    return {
        "surface_kind": "rebuttal_strategy_candidate",
        "review_ref": normalize_evidence_ref(review_ref),
        "required_refs": list(REBUTTAL_REFS),
        "candidate_refs": {ref: None for ref in REBUTTAL_REFS},
        "candidate_package_ref": None,
        "route_back_candidate": None,
        "owner_gate_handoff_ref": None,
        "authority": {
            "refs_only": True,
            "can_sign_reviewer_receipt": False,
            "can_accept_or_reject_reviews": False,
            "can_mutate_final_artifacts": False,
            "can_write_mas_truth": False,
            "can_create_typed_blocker": False,
            "can_claim_publication_readiness": False,
        },
    }


def evidence_response_map(
    comments: list[Mapping[str, object]],
) -> list[dict[str, str | bool]]:
    """Normalize comment-to-response rows for owner-gated rebuttal handoff."""

    rows: list[dict[str, str | bool]] = []
    for comment in comments:
        text = str(comment.get("comment") or comment.get("requested_action") or "")
        rows.append(
            {
                "comment_id": normalize_comment_id(comment.get("comment_id")),
                "current_evidence_ref": normalize_evidence_ref(comment.get("current_evidence_ref")),
                "missing_evidence_ref": normalize_evidence_ref(comment.get("missing_evidence_ref")),
                "response_route": normalize_evidence_ref(
                    comment.get("response_route") or classify_response_route(text)["route"]
                ),
                "proposed_answer_ref": normalize_evidence_ref(comment.get("proposed_answer_ref")),
                "manuscript_delta_ref": normalize_evidence_ref(comment.get("manuscript_delta_ref")),
                "owner_decision_target": normalize_evidence_ref(comment.get("owner_decision_target")),
                "writes_authority": False,
            }
        )
    return rows


def lint_forbidden_rebuttal_claims(text: str) -> list[str]:
    """Return forbidden authority phrases found in rebuttal strategy prose."""

    patterns = (
        r"\breviewer receipt\b",
        r"\breview accepted\b",
        r"\bowner receipt\b",
        r"\btyped blocker\b",
        r"\bpublication-ready\b",
        r"\bpublication readiness\b",
        r"\bcurrent package\b",
    )
    return [pattern for pattern in patterns if re.search(pattern, text, flags=re.I)]


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


if __name__ == "__main__":
    _self_check()
