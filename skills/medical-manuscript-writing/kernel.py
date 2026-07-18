"""Deterministic refs-only helpers for medical manuscript writing.

These helpers scaffold prompts, schemas, and lint hints. They do not create
MAS truth, owner receipts, typed blockers, artifacts, or publication readiness.
"""

from __future__ import annotations

import json
import re
from typing import Any, Mapping, Sequence


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

FIRST_DRAFT_STORY_REFS = (
    "unique_scientific_claim_ref",
    "clinical_or_operational_value_ref",
    "falsifiable_boundary_ref",
    "result_paragraph_job_map_ref",
    "figure_table_narrative_arc_ref",
    "main_supplement_placement_ref",
    "terminology_surface_ledger_ref",
)

TERMINOLOGY_SURFACES = (
    "manuscript_text",
    "table_titles",
    "figure_legends",
    "csv_headers",
    "machine_readable_endpoints",
    "supplement",
)

REGISTRY_BOUNDARY_TERMS = (
    "gap",
    "intensity",
    "burden",
    "adherence",
    "nonadherence",
    "workload",
    "quality ranking",
)


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


def first_draft_story_contract_schema() -> dict[str, Any]:
    """Return the handling-editor story contract required before prose."""

    return {
        "type": "object",
        "required": list(FIRST_DRAFT_STORY_REFS),
        "properties": {
            ref: {"type": "string"} for ref in FIRST_DRAFT_STORY_REFS
        }
        | {
            "route_back_candidate": {"type": "object"},
            "authority": {"const": False},
        },
    }


def terminology_surface_ledger_schema() -> dict[str, Any]:
    """Return the cross-surface terminology-ledger candidate schema."""

    return {
        "type": "object",
        "required": ["surface_refs", "canonical_terms", "boundary_terms"],
        "properties": {
            "surface_refs": {
                "type": "object",
                "required": list(TERMINOLOGY_SURFACES),
                "description": (
                    "Inventory every terminology surface; absent surfaces use an "
                    "explicit not-applicable record with a reason."
                ),
            },
            "canonical_terms": {"type": "array", "items": {"type": "object"}},
            "boundary_terms": {"type": "array", "items": {"type": "object"}},
            "route_back_candidate": {"type": "object"},
            "authority": {"const": False},
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


def lint_terminology_surface_ledger(
    items: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Flag missing surfaces and unbounded registry terms without judging truth."""

    findings: list[dict[str, object]] = []
    seen_surfaces: set[str] = set()
    for index, item in enumerate(items, start=1):
        surface_kind = str(item.get("surface_kind") or "").strip()
        if surface_kind not in TERMINOLOGY_SURFACES:
            findings.append(
                _terminology_finding(
                    "TERMINOLOGY_SURFACE_UNKNOWN",
                    surface_kind or f"item_{index}",
                    "use one canonical terminology surface kind",
                )
            )
            continue
        seen_surfaces.add(surface_kind)
        if item.get("applicable") is False:
            if not str(item.get("not_applicable_reason") or "").strip():
                findings.append(
                    _terminology_finding(
                        "TERMINOLOGY_NOT_APPLICABLE_REASON_MISSING",
                        surface_kind,
                        "record why this terminology surface does not exist",
                    )
                )
            continue
        text = " ".join(
            str(item.get(field) or "")
            for field in ("text", "label", "header", "identifier", "endpoint")
        )
        normalized = re.sub(r"[_/\-]+", " ", text.lower())
        has_boundary = bool(
            str(item.get("claim_boundary_ref") or "").strip()
            or str(item.get("term_justification_ref") or "").strip()
        )
        if has_boundary:
            continue
        for term in REGISTRY_BOUNDARY_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", normalized):
                findings.append(
                    _terminology_finding(
                        "TERMINOLOGY_BOUNDARY_UNJUSTIFIED",
                        surface_kind,
                        "add a bounded definition or use candidate-audit-signal wording",
                        term=term,
                    )
                )

    for surface_kind in TERMINOLOGY_SURFACES:
        if surface_kind not in seen_surfaces:
            findings.append(
                _terminology_finding(
                    "TERMINOLOGY_SURFACE_MISSING",
                    surface_kind,
                    "add the surface ref to the terminology ledger",
                )
            )
    return sorted(
        findings,
        key=lambda item: (
            str(item["code"]),
            str(item["surface_kind"]),
            str(item.get("term") or ""),
        ),
    )


def _terminology_finding(
    code: str, surface_kind: str, action: str, *, term: str = ""
) -> dict[str, object]:
    return {
        "code": code,
        "surface_kind": surface_kind,
        "term": term,
        "action": action,
        "writes_authority": False,
    }


def _matched_terms(text: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if re.search(rf"\b{re.escape(term)}\b", text)]


def _self_check() -> None:
    assert "one_sentence_argument_ref" in paper_brief_schema()["required"]
    assert set(first_draft_story_contract_schema()["required"]) == set(
        FIRST_DRAFT_STORY_REFS
    )
    assert terminology_surface_ledger_schema()["properties"]["authority"] == {
        "const": False
    }
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
    print(json.dumps({"ok": True, "checks": 11}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
