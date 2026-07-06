"""Deterministic refs-only helpers for the medical-research-lit skill.

No credentials, network calls, provider calls, or MAS authority writes live
here. These helpers only shape candidate literature refs for AI review.
"""

from __future__ import annotations

import html
import re
from typing import Iterable, Mapping


DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'`\]\}<>]+", re.I)


def extract_dois(text: str) -> list[str]:
    """Return sorted DOI-looking strings from free text."""
    decoded = html.unescape(text or "")
    dois: set[str] = set()
    for match in DOI_RE.findall(decoded):
        doi = match.split("</", 1)[0]
        doi = re.sub(r"(?:\*\*|__|[_\]\*>`,;:])+$", "", doi)
        doi = doi[:-1] if doi.endswith(".") else doi
        while doi.endswith(")") and doi.count("(") < doi.count(")"):
            doi = doi[:-1]
        norm = normalize_doi(doi)
        if norm:
            dois.add(norm)
    return sorted(dois)


def normalize_doi(value: object) -> str:
    """Normalize DOI strings without resolving them."""
    text = str(value or "").strip()
    text = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", text, flags=re.I)
    text = text.strip().rstrip(".,;")
    return text.lower()


def normalize_pmid(value: object) -> str:
    """Normalize a PMID to digits only."""
    return "".join(re.findall(r"\d+", str(value or "")))


def normalize_pmcid(value: object) -> str:
    """Normalize PMCID to PMC-prefixed uppercase form."""
    text = str(value or "").strip().upper()
    digits = "".join(re.findall(r"\d+", text))
    return f"PMC{digits}" if digits else ""


def normalize_title(value: object) -> str:
    """Normalize title text for duplicate detection."""
    text = html.unescape(str(value or "")).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_source(source: Mapping[str, object]) -> dict[str, object]:
    """Return a normalized copy of one source record."""
    out = dict(source)
    out["doi"] = normalize_doi(out.get("doi") or out.get("DOI"))
    out["pmid"] = normalize_pmid(out.get("pmid") or out.get("PMID"))
    out["pmcid"] = normalize_pmcid(out.get("pmcid") or out.get("PMCID"))
    out["normalized_title"] = normalize_title(out.get("title"))
    return out


def dedupe_sources(sources: Iterable[Mapping[str, object]]) -> dict[str, list[dict[str, object]]]:
    """Deduplicate by PMID, DOI, then normalized title; keep first record."""
    retained: list[dict[str, object]] = []
    duplicates: list[dict[str, object]] = []
    seen: dict[str, int] = {}

    for source in sources:
        item = normalize_source(source)
        key = ""
        for field in ("pmid", "doi", "normalized_title"):
            if item.get(field):
                key = f"{field}:{item[field]}"
                break
        if not key:
            retained.append(item)
            continue
        if key in seen:
            dup = dict(item)
            dup["duplicate_of_index"] = seen[key]
            dup["duplicate_key"] = key
            duplicates.append(dup)
        else:
            seen[key] = len(retained)
            retained.append(item)
    return {"retained": retained, "duplicates": duplicates}


def lint_citation_support(markdown: str) -> list[dict[str, str]]:
    """Small deterministic lint for citation/support handoff markdown."""
    text = markdown or ""
    issues: list[dict[str, str]] = []
    if re.search(r"\b(?:PMID|DOI|PMCID)\s*:\s*(?:TBD|TODO|N/?A|missing)\b", text, re.I):
        issues.append({"code": "MISSING_IDENTIFIER", "note": "identifier slot is unresolved"})
    if re.search(r"\b(?:pubmed|crossref|openalex)\s+(?:says|proves)\b", text, re.I):
        issues.append({"code": "AUTHORITY_DRIFT", "note": "retrieval source is being written as authority"})
    if re.search(r"\bpublication\s+ready|owner\s+accepted|typed\s+blocker\b", text, re.I):
        issues.append({"code": "AUTHORITY_CLAIM", "note": "lit skill cannot claim downstream authority"})
    if text.count("`support_strength`") and not re.search(
        r"direct_primary|direct_guideline|method_precedent|contextual_background|contradictory|weak|not_applicable",
        text,
        re.I,
    ):
        issues.append({"code": "UNSET_SUPPORT_STRENGTH", "note": "support strength vocabulary is missing"})
    return issues


def support_matrix_skeleton(claims: Iterable[str], sources: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    """Create a refs-only claim/source support matrix skeleton."""
    normalized_sources = [normalize_source(s) for s in sources]
    return [
        {
            "claim": claim,
            "candidate_sources": [
                {
                    "title": src.get("title", ""),
                    "pmid": src.get("pmid", ""),
                    "pmcid": src.get("pmcid", ""),
                    "doi": src.get("doi", ""),
                    "support_strength": "not_applicable",
                    "limitations": "",
                }
                for src in normalized_sources
            ],
            "route_back_candidate": "",
        }
        for claim in claims
    ]


def handoff_skeleton(literature_question: str = "") -> dict[str, object]:
    """Return the standard refs-only Lit handoff shell."""
    return {
        "literature_question": literature_question,
        "literature_retrieval_contract_ref": "",
        "query_plan_ref": "",
        "search_command_ref": "",
        "scientific_connector_source_refs": [],
        "scientific_connector_invocation_refs": [],
        "pubmed_source_refs": [],
        "pubmed_connector_invocation_ref": "",
        "fallback_source_refs": [],
        "connector_receipt_candidate_refs": [],
        "cache_retry_metadata_ref": "",
        "connector_no_authority_flags_ref": "",
        "identifier_resolution_ref": "",
        "database_endpoint_provenance_ref": "",
        "retrieval_count_reconciliation_ref": "",
        "deduplication_ref": "",
        "source_acceptance_decision_ref": "",
        "citation_graph_expansion_ref": "",
        "doi_retraction_version_check_ref": "",
        "pdf_evidence_extraction_ref": "",
        "claim_support_map_ref": "",
        "support_strength_matrix_ref": "",
        "citation_integrity_notes": [],
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def _self_check() -> None:
    assert extract_dois("See https://doi.org/10.1000/ABC). and doi:10.2000/x.") == [
        "10.1000/abc",
        "10.2000/x",
    ]
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
    assert handoff_skeleton()["scientific_connector_source_refs"] == []


if __name__ == "__main__":
    _self_check()
    print("medical-research-lit kernel self-check passed")
