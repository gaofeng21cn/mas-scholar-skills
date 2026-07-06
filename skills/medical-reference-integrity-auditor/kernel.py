"""Deterministic refs-only helpers for reference integrity auditing.

No network lookup, credentials, provider calls, MAS truth writes, owner
receipts, typed blockers, or publication-readiness decisions live here.
"""

from __future__ import annotations

import json
import re
from typing import Iterable, Mapping


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


def _self_check() -> None:
    assert normalize_doi("https://doi.org/10.1000/ABC.") == "10.1000/abc"
    assert normalize_pmid("PMID: 12345") == "12345"
    assert normalize_pmcid("pmc987") == "PMC987"
    refs = [{"title": "A Trial", "doi": "10.1/A"}, {"title": "B", "doi": "10.1/a"}]
    assert lint_reference_identifiers(refs)[0]["code"] == "DUPLICATE_REFERENCE_KEY"
    assert reference_inventory_skeleton(["ref1"])[0]["citation_key"] == "ref1"
    print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
