"""Deterministic refs-only helpers for reference integrity auditing.

No network lookup, credentials, provider calls, MAS truth writes, owner
receipts, typed blockers, or publication-readiness decisions live here.
"""

from __future__ import annotations

import json
import re
from typing import Any, Iterable, Mapping, Sequence


PLACEHOLDER_RE = re.compile(r"\b(?:tbd|todo|missing|unknown|n/?a|placeholder)\b", re.I)


def normalize_doi(value: object) -> str:
    """Normalize a DOI string without resolving it."""
    text = str(value or "").strip()
    text = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", text, flags=re.I)
    return text.strip().rstrip(".,;").lower()


def normalize_pmid(value: object) -> str:
    """Normalize PMID-like text to digits only."""
    return "".join(re.findall(r"\d+", str(value or "")))


def normalize_pmcid(value: object) -> str:
    """Normalize PMCID-like text to PMC-prefixed uppercase form."""
    digits = "".join(re.findall(r"\d+", str(value or "")))
    return f"PMC{digits}" if digits else ""


def normalize_title(value: object) -> str:
    """Normalize titles for duplicate-key construction."""
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_reference(ref: Mapping[str, object]) -> dict[str, object]:
    """Return a normalized refs-only reference record."""
    out = dict(ref)
    out["doi"] = normalize_doi(out.get("doi") or out.get("DOI"))
    out["pmid"] = normalize_pmid(out.get("pmid") or out.get("PMID"))
    out["pmcid"] = normalize_pmcid(out.get("pmcid") or out.get("PMCID"))
    out["normalized_title"] = normalize_title(out.get("title"))
    return out


def duplicate_key(ref: Mapping[str, object]) -> str:
    """Build a stable duplicate key from PMID, PMCID, DOI, then title/year."""
    item = normalize_reference(ref)
    for field in ("pmid", "pmcid", "doi"):
        if item.get(field):
            return f"{field}:{item[field]}"
    title = str(item.get("normalized_title") or "")
    year = "".join(re.findall(r"\d{4}", str(item.get("year") or "")))
    return f"title_year:{title}:{year}" if title or year else ""


def lint_reference_identifiers(
    references: Iterable[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Flag unresolved identifiers and duplicate reference keys."""
    issues: list[dict[str, object]] = []
    seen: dict[str, int] = {}
    for index, ref in enumerate(references):
        item = normalize_reference(ref)
        key = duplicate_key(item)
        raw_identifier_text = " ".join(str(item.get(k, "")) for k in ("doi", "pmid", "pmcid", "url"))
        if PLACEHOLDER_RE.search(raw_identifier_text):
            issues.append({"index": index, "code": "UNRESOLVED_IDENTIFIER", "field": "identifier"})
        if not any(item.get(field) for field in ("doi", "pmid", "pmcid")):
            issues.append({"index": index, "code": "MISSING_STABLE_IDENTIFIER", "field": "identifier"})
        if key and key in seen:
            issues.append(
                {
                    "index": index,
                    "code": "DUPLICATE_REFERENCE_KEY",
                    "duplicate_key": key,
                    "duplicate_of_index": seen[key],
                }
            )
        elif key:
            seen[key] = index
    return issues


def reference_inventory_skeleton(keys: Iterable[str]) -> list[dict[str, object]]:
    """Create a refs-only reference inventory shell."""
    return [
        {
            "citation_key": key,
            "title": "",
            "authors": [],
            "year": "",
            "journal": "",
            "pmid": "",
            "pmcid": "",
            "doi": "",
            "source_type": "",
            "identifier_integrity_ref": "",
            "owner_gate_handoff_ref": "",
        }
        for key in keys
    ]


def audit_citation_source_coverage(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Close manuscript citations against bibliography, source context, and claims."""

    findings: list[dict[str, object]] = []
    manuscript_keys = _citation_key_set(
        candidate.get("manuscript_citation_keys"),
        "manuscript_citation_keys",
        findings,
    )
    source_context_keys = _citation_key_set(
        candidate.get("source_context_keys"),
        "source_context_keys",
        findings,
    )
    claim_map_keys = _citation_key_set(
        candidate.get("claim_map_keys"),
        "claim_map_keys",
        findings,
    )
    bibliography_records = candidate.get("bibliography_records")
    bibliography_keys: set[str] = set()
    if not isinstance(bibliography_records, Sequence) or isinstance(
        bibliography_records, (str, bytes)
    ):
        findings.append(
            _coverage_finding(
                "CITATION_BIBLIOGRAPHY_RECORDS_INVALID",
                "bibliography_records",
                "provide a list of bibliography records with citation_key",
            )
        )
        bibliography_records = []
    for index, record in enumerate(bibliography_records):
        if not isinstance(record, Mapping):
            findings.append(
                _coverage_finding(
                    "CITATION_BIBLIOGRAPHY_RECORD_INVALID",
                    f"bibliography_records[{index}]",
                    "provide a structured bibliography record",
                )
            )
            continue
        key = _normalize_citation_key(record.get("citation_key"))
        if not key:
            findings.append(
                _coverage_finding(
                    "CITATION_BIBLIOGRAPHY_KEY_MISSING",
                    f"bibliography_records[{index}].citation_key",
                    "bind each bibliography record to a manuscript citation key",
                )
            )
            continue
        if key in bibliography_keys:
            findings.append(
                _coverage_finding(
                    "CITATION_BIBLIOGRAPHY_KEY_DUPLICATE",
                    f"bibliography_records[{index}].citation_key",
                    "deduplicate bibliography citation keys",
                )
            )
        bibliography_keys.add(key)

    if not manuscript_keys:
        findings.append(
            _coverage_finding(
                "CITATION_MANUSCRIPT_KEY_SET_EMPTY",
                "manuscript_citation_keys",
                "bind the initial draft to at least one manuscript citation key or route N/A at the upper preflight gate",
            )
        )
    if not bibliography_keys:
        findings.append(
            _coverage_finding(
                "CITATION_BIBLIOGRAPHY_KEY_SET_EMPTY",
                "bibliography_records",
                "provide at least one verified keyed bibliography record",
            )
        )

    missing_bibliography = sorted(manuscript_keys - bibliography_keys)
    missing_source_context = sorted(manuscript_keys - source_context_keys)
    missing_claim_map = sorted(manuscript_keys - claim_map_keys)
    orphan_bibliography = sorted(bibliography_keys - manuscript_keys)
    orphan_source_context = sorted(source_context_keys - manuscript_keys)
    orphan_claim_map = sorted(claim_map_keys - manuscript_keys)
    for code, field, values, action in (
        (
            "CITATION_KEYS_MISSING_FROM_BIBLIOGRAPHY",
            "bibliography_records",
            missing_bibliography,
            "add verified bibliography records or remove unsupported manuscript citations",
        ),
        (
            "CITATION_KEYS_MISSING_SOURCE_CONTEXT",
            "source_context_keys",
            missing_source_context,
            "bind cited keys to source-context evidence",
        ),
        (
            "CITATION_KEYS_MISSING_CLAIM_MAP",
            "claim_map_keys",
            missing_claim_map,
            "bind cited keys to the claim-citation support map",
        ),
        (
            "ORPHAN_BIBLIOGRAPHY_KEYS",
            "bibliography_records",
            orphan_bibliography,
            "remove uncited bibliography records or add the intended manuscript citation",
        ),
        (
            "ORPHAN_SOURCE_CONTEXT_KEYS",
            "source_context_keys",
            orphan_source_context,
            "reconcile source-context keys with manuscript citations",
        ),
        (
            "ORPHAN_CLAIM_MAP_KEYS",
            "claim_map_keys",
            orphan_claim_map,
            "reconcile claim-map keys with manuscript citations",
        ),
    ):
        if values:
            finding = _coverage_finding(code, field, action)
            finding["citation_keys"] = values
            findings.append(finding)
    if candidate.get("authority") is not False:
        findings.append(
            _coverage_finding(
                "CITATION_SOURCE_COVERAGE_AUTHORITY_FORBIDDEN",
                "authority",
                "keep citation coverage refs-only with authority=false",
            )
        )
    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "citation_source_coverage_ref",
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "manuscript_citation_key_count": len(manuscript_keys),
        "bibliography_key_count": len(bibliography_keys),
        "source_context_key_count": len(source_context_keys),
        "claim_map_key_count": len(claim_map_keys),
        "missing_bibliography_keys": missing_bibliography,
        "missing_source_context_keys": missing_source_context,
        "missing_claim_map_keys": missing_claim_map,
        "orphan_bibliography_keys": orphan_bibliography,
        "orphan_source_context_keys": orphan_source_context,
        "orphan_claim_map_keys": orphan_claim_map,
        "findings": findings,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-reference-integrity-auditor",
            "reason": "citation_source_coverage_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def _citation_key_set(
    value: object,
    field: str,
    findings: list[dict[str, object]],
) -> set[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        findings.append(
            _coverage_finding(
                "CITATION_KEY_SET_INVALID",
                field,
                "provide a citation-key list",
            )
        )
        return set()
    normalized = [_normalize_citation_key(item) for item in value]
    if any(not item for item in normalized):
        findings.append(
            _coverage_finding(
                "CITATION_KEY_EMPTY",
                field,
                "remove empty citation keys",
            )
        )
    if len([item for item in normalized if item]) != len(
        set(item for item in normalized if item)
    ):
        findings.append(
            _coverage_finding(
                "CITATION_KEY_DUPLICATE",
                field,
                "deduplicate citation keys",
            )
        )
    return {item for item in normalized if item}


def _normalize_citation_key(value: object) -> str:
    return re.sub(r"\s+", "", str(value or "")).casefold()


def _coverage_finding(code: str, field: str, action: str) -> dict[str, object]:
    return {
        "code": code,
        "field": field,
        "action": action,
        "writes_authority": False,
    }


def _self_check() -> None:
    assert normalize_doi("https://doi.org/10.1000/ABC.") == "10.1000/abc"
    assert normalize_pmid("PMID: 12345") == "12345"
    assert normalize_pmcid("pmc987") == "PMC987"
    refs = [{"title": "A Trial", "doi": "10.1/A"}, {"title": "B", "doi": "10.1/a"}]
    assert lint_reference_identifiers(refs)[0]["code"] == "DUPLICATE_REFERENCE_KEY"
    assert reference_inventory_skeleton(["ref1"])[0]["citation_key"] == "ref1"
    empty_coverage = audit_citation_source_coverage(
        {
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
    incomplete_coverage = audit_citation_source_coverage(
        {
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
    incomplete_source_context = audit_citation_source_coverage(
        {
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
    complete_coverage = audit_citation_source_coverage(
        {
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
    print(json.dumps({"ok": True, "checks": 13}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
