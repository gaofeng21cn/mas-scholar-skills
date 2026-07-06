"""Deterministic refs-only helpers for medical manuscript writing.

These helpers scaffold prompts, schemas, and lint hints. They do not create
MAS truth, owner receipts, typed blockers, artifacts, or publication readiness.
"""

from __future__ import annotations

import json
import re
from typing import Any


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


def _matched_terms(text: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if re.search(rf"\b{re.escape(term)}\b", text)]


def _self_check() -> None:
    assert "one_sentence_argument_ref" in paper_brief_schema()["required"]
    assert section_scaffold("Results")["section_type"] == "results"
    assert paragraph_job_map_scaffold("results", ["result"])[0]["paragraph_job"] == "result"
    assert figure_arc_outline_builder("A.", [{"key": "F1", "claim": "B"}])["outline"][
        "fig1_hook_ref"
    ] == ""
    lint = claim_strength_lint_lite(
        [{"claim_ref": "c1", "claim": "These data prove benefit.", "evidence_strength": "weak"}]
    )
    assert lint[0]["action"] == "downgrade"
    print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
