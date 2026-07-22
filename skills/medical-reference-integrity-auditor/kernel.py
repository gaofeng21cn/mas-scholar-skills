"""Deterministic refs-only helpers for reference integrity auditing.

No network lookup, credentials, provider calls, MAS truth writes, owner
receipts, typed blockers, or publication-readiness decisions live here.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PLACEHOLDER_RE = re.compile(r"\b(?:tbd|todo|missing|unknown|n/?a|placeholder)\b", re.I)
REFERENCE_CURRENTNESS_STATUSES = (
    "verified_current",
    "open_currentness",
    "corrected_or_updated",
    "retracted",
    "not_applicable_with_reason",
)
EXCLUDED_REFERENCE_CLEARANCE_STATUSES = (
    "uncleared",
    "cleared",
    "reintroduced",
)
POST_CSL_SEMANTIC_KINDS = (
    "protected_proper_noun",
    "corporate_author",
    "group_author",
    "corrected_metadata",
)
POST_CSL_OUTPUT_SURFACES = ("docx", "pdf")


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
    """Close the stable v1 four-set citation coverage contract."""

    return _audit_citation_source_coverage(candidate, strict_v2=False)


def audit_citation_source_coverage_v2(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Close four-set coverage against an exact active inventory ref."""

    return _audit_citation_source_coverage(candidate, strict_v2=True)


def _audit_citation_source_coverage(
    candidate: Mapping[str, object], *, strict_v2: bool
) -> dict[str, Any]:
    """Close manuscript citations against bibliography, source context, and claims."""

    findings: list[dict[str, object]] = []
    active_inventory_ref = (
        _active_inventory_exact_ref(candidate.get("active_inventory_ref"), findings)
        if strict_v2
        else None
    )
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
        **({"active_inventory_ref": active_inventory_ref} if strict_v2 else {}),
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


def audit_active_reference_currentness(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Audit metadata and currentness for every active citation key."""

    findings: list[dict[str, object]] = []
    active_inventory_ref = _active_inventory_exact_ref(
        candidate.get("active_inventory_ref"), findings
    )
    active_keys = _citation_key_set(
        candidate.get("active_keys"), "active_keys", findings
    )
    records = candidate.get("records")
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
        findings.append(
            _coverage_finding(
                "REFERENCE_CURRENTNESS_RECORDS_INVALID",
                "records",
                "provide one currentness record per active key",
            )
        )
        records = []
    seen: set[str] = set()
    open_keys: list[str] = []
    for index, record in enumerate(records):
        field = f"records[{index}]"
        if not isinstance(record, Mapping):
            findings.append(
                _coverage_finding(
                    "REFERENCE_CURRENTNESS_RECORD_INVALID",
                    field,
                    "provide a structured currentness record",
                )
            )
            continue
        key = _normalize_citation_key(record.get("citation_key"))
        if not key or key in seen:
            findings.append(
                _coverage_finding(
                    "REFERENCE_CURRENTNESS_KEY_INVALID",
                    f"{field}.citation_key",
                    "provide one unique active citation key",
                )
            )
            continue
        seen.add(key)
        for metadata_field in ("title", "year", "stable_identifier"):
            if not str(record.get(metadata_field) or "").strip():
                findings.append(
                    _coverage_finding(
                        "REFERENCE_ACTIVE_METADATA_MISSING",
                        f"{field}.{metadata_field}",
                        "bind active sources to verified title, year, and stable identifier",
                    )
                )
        for ref_field in ("metadata_source_ref", "source_context_ref"):
            _validate_reference_evidence_ref(
                record.get(ref_field),
                f"{field}.{ref_field}",
                findings,
                allowed_dispositions=(),
            )
        status = str(record.get("status") or "")
        if status not in REFERENCE_CURRENTNESS_STATUSES:
            findings.append(
                _coverage_finding(
                    "REFERENCE_CURRENTNESS_STATUS_INVALID",
                    f"{field}.status",
                    "use a canonical currentness status",
                )
            )
        evidence_ref = record.get("currentness_evidence_ref")
        reason = str(record.get("reason") or "").strip()
        if status in {"verified_current", "corrected_or_updated"}:
            _validate_reference_evidence_ref(
                evidence_ref,
                f"{field}.currentness_evidence_ref",
                findings,
                allowed_dispositions=(),
            )
        elif status == "not_applicable_with_reason":
            _validate_reference_evidence_ref(
                evidence_ref,
                f"{field}.currentness_evidence_ref",
                findings,
                allowed_dispositions=("not_applicable_with_reason",),
                require_disposition=True,
            )
            if not reason:
                findings.append(
                    _coverage_finding(
                        "REFERENCE_CURRENTNESS_REASON_MISSING",
                        f"{field}.reason",
                        "state why currentness checking is not applicable",
                    )
                )
        elif evidence_ref is not None:
            _validate_reference_evidence_ref(
                evidence_ref,
                f"{field}.currentness_evidence_ref",
                findings,
                allowed_dispositions=(),
            )
        if status in {"open_currentness", "retracted"}:
            open_keys.append(key)
            findings.append(
                _coverage_finding(
                    "REFERENCE_ACTIVE_CURRENTNESS_OPEN",
                    f"{field}.status",
                    "resolve, replace, or exclude the active source before citation closure",
                )
            )
    missing = sorted(active_keys - seen)
    orphan = sorted(seen - active_keys)
    if missing:
        finding = _coverage_finding(
            "REFERENCE_CURRENTNESS_ACTIVE_KEY_MISSING",
            "records",
            "add currentness records for every active key",
        )
        finding["citation_keys"] = missing
        findings.append(finding)
    if orphan:
        finding = _coverage_finding(
            "REFERENCE_CURRENTNESS_ORPHAN_KEY",
            "records",
            "remove non-active records or move them to the excluded ledger",
        )
        finding["citation_keys"] = orphan
        findings.append(finding)
    if candidate.get("authority") is not False:
        findings.append(
            _coverage_finding(
                "REFERENCE_CURRENTNESS_AUTHORITY_FORBIDDEN",
                "authority",
                "keep source status refs-only with authority=false",
            )
        )
    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "active_reference_currentness_ref",
        "active_inventory_ref": active_inventory_ref,
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "active_key_count": len(active_keys),
        "record_count": len(seen),
        "open_currentness_keys": sorted(open_keys),
        "findings": findings,
        "route_back_candidate": None if complete else {
            "route": "medical-reference-integrity-auditor",
            "reason": "active_reference_currentness_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def audit_excluded_reference_ledger(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Keep excluded sources outside active surfaces until their gate is satisfied."""

    findings: list[dict[str, object]] = []
    active_inventory_ref = _active_inventory_exact_ref(
        candidate.get("active_inventory_ref"), findings
    )
    active_keys = _citation_key_set(candidate.get("active_keys"), "active_keys", findings)
    records = candidate.get("excluded_records")
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
        findings.append(
            _coverage_finding(
                "EXCLUDED_REFERENCE_RECORDS_INVALID",
                "excluded_records",
                "provide a separate excluded-source ledger",
            )
        )
        records = []
    excluded_keys: set[str] = set()
    reintroduced_keys: set[str] = set()
    for index, record in enumerate(records):
        field = f"excluded_records[{index}]"
        if not isinstance(record, Mapping):
            findings.append(
                _coverage_finding(
                    "EXCLUDED_REFERENCE_RECORD_INVALID",
                    field,
                    "provide a structured excluded-source record",
                )
            )
            continue
        key = _normalize_citation_key(record.get("citation_key"))
        if not key or key in excluded_keys:
            findings.append(
                _coverage_finding(
                    "EXCLUDED_REFERENCE_KEY_INVALID",
                    f"{field}.citation_key",
                    "provide a unique excluded citation key",
                )
            )
            continue
        excluded_keys.add(key)
        for required in (
            "exclusion_reason",
            "prior_role",
            "unresolved_status",
            "reintroduction_gate",
            "clearance_status",
        ):
            if not str(record.get(required) or "").strip():
                findings.append(
                    _coverage_finding(
                        "EXCLUDED_REFERENCE_FIELD_MISSING",
                        f"{field}.{required}",
                        "preserve exclusion provenance and the explicit reintroduction gate",
                    )
                )
        clearance_status = str(record.get("clearance_status") or "")
        currentness_reopened_ref = record.get("currentness_reopened_ref")
        claim_edge_reopened_ref = record.get("claim_edge_reopened_ref")
        if clearance_status not in EXCLUDED_REFERENCE_CLEARANCE_STATUSES:
            findings.append(
                _coverage_finding(
                    "EXCLUDED_REFERENCE_CLEARANCE_STATUS_INVALID",
                    f"{field}.clearance_status",
                    "use uncleared, cleared, or reintroduced",
                )
            )
        elif clearance_status in {"uncleared", "cleared"}:
            if key in active_keys:
                findings.append(
                    _coverage_finding(
                        "EXCLUDED_REFERENCE_REINTRODUCED_WITHOUT_CLEARANCE",
                        f"{field}.citation_key",
                        "mark the cleared source reintroduced and reopen currentness and claim-edge review",
                    )
                )
            if currentness_reopened_ref is not None or claim_edge_reopened_ref is not None:
                findings.append(
                    _coverage_finding(
                        "EXCLUDED_REFERENCE_REOPENED_REF_CONTRADICTORY",
                        field,
                        "keep reopened refs null until the source is reintroduced",
                    )
                )
        elif clearance_status == "reintroduced":
            if key not in active_keys:
                findings.append(
                    _coverage_finding(
                        "EXCLUDED_REFERENCE_REINTRODUCED_KEY_NOT_ACTIVE",
                        f"{field}.citation_key",
                        "add the reintroduced key to the shared active inventory",
                    )
                )
            for ref_field, ref_value in (
                ("currentness_reopened_ref", currentness_reopened_ref),
                ("claim_edge_reopened_ref", claim_edge_reopened_ref),
            ):
                _validate_reference_evidence_ref(
                    ref_value,
                    f"{field}.{ref_field}",
                    findings,
                    allowed_dispositions=(),
                )
            reintroduced_keys.add(key)
    reintroduced = sorted(reintroduced_keys)
    if candidate.get("authority") is not False:
        findings.append(
            _coverage_finding(
                "EXCLUDED_REFERENCE_AUTHORITY_FORBIDDEN",
                "authority",
                "keep the excluded ledger refs-only with authority=false",
            )
        )
    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "excluded_reference_ledger_ref",
        "active_inventory_ref": active_inventory_ref,
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "excluded_key_count": len(excluded_keys),
        "reintroduced_keys": reintroduced,
        "findings": findings,
        "route_back_candidate": None if complete else {
            "route": "medical-reference-integrity-auditor",
            "reason": "excluded_reference_ledger_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def audit_claim_citation_edge_completeness(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Require located, excerpted, scope-bounded support for active citation edges."""

    findings: list[dict[str, object]] = []
    active_inventory_ref = _active_inventory_exact_ref(
        candidate.get("active_inventory_ref"), findings
    )
    active_keys = _citation_key_set(candidate.get("active_keys"), "active_keys", findings)
    edges = candidate.get("edges")
    if not isinstance(edges, Sequence) or isinstance(edges, (str, bytes)) or not edges:
        findings.append(
            _coverage_finding(
                "CLAIM_CITATION_EDGES_INVALID",
                "edges",
                "provide at least one located claim-source edge",
            )
        )
        edges = []
    represented: set[str] = set()
    required_fields = (
        "claim_id",
        "citation_key",
        "claim_text",
        "support_type",
        "locator",
        "excerpt",
        "population_fit",
        "endpoint_fit",
        "method_fit",
        "support_boundary",
        "source_support_ref",
    )
    for index, edge in enumerate(edges):
        field = f"edges[{index}]"
        if not isinstance(edge, Mapping):
            findings.append(
                _coverage_finding(
                    "CLAIM_CITATION_EDGE_INVALID",
                    field,
                    "provide a structured claim-source edge",
                )
            )
            continue
        for required in required_fields:
            if required == "source_support_ref":
                _validate_reference_evidence_ref(
                    edge.get(required),
                    f"{field}.{required}",
                    findings,
                    allowed_dispositions=(),
                )
            elif not str(edge.get(required) or "").strip():
                findings.append(
                    _coverage_finding(
                        "CLAIM_CITATION_EDGE_FIELD_MISSING",
                        f"{field}.{required}",
                        "bind claim text, exact source passage, fit, and support boundary",
                    )
                )
        key = _normalize_citation_key(edge.get("citation_key"))
        if key:
            represented.add(key)
            if key not in active_keys:
                findings.append(
                    _coverage_finding(
                        "CLAIM_CITATION_EDGE_NONACTIVE_KEY",
                        f"{field}.citation_key",
                        "use only active source keys in the active claim map",
                    )
                )
    missing = sorted(active_keys - represented)
    if missing:
        finding = _coverage_finding(
            "CLAIM_CITATION_ACTIVE_KEY_WITHOUT_EDGE",
            "edges",
            "add at least one complete claim-source edge for every active key",
        )
        finding["citation_keys"] = missing
        findings.append(finding)
    if candidate.get("authority") is not False:
        findings.append(
            _coverage_finding(
                "CLAIM_CITATION_EDGE_AUTHORITY_FORBIDDEN",
                "authority",
                "keep claim support refs-only with authority=false",
            )
        )
    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "claim_citation_edge_completeness_ref",
        "active_inventory_ref": active_inventory_ref,
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "edge_count": len(edges),
        "active_key_count": len(active_keys),
        "findings": findings,
        "route_back_candidate": None if complete else {
            "route": "medical-evidence-synthesis-and-claim-map",
            "reason": "claim_citation_edges_require_repair",
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


def _validate_reference_evidence_ref(
    value: object,
    field: str,
    findings: list[dict[str, object]],
    *,
    allowed_dispositions: Sequence[str],
    require_disposition: bool = False,
) -> None:
    exact_fields = {"kind", "ref", "size_bytes", "sha256"}
    disposition_fields = {"status", "ref", "reason"}
    if isinstance(value, Mapping) and set(value) == exact_fields:
        size_bytes = value.get("size_bytes")
        valid = (
            bool(str(value.get("kind") or "").strip())
            and bool(str(value.get("ref") or "").strip())
            and not isinstance(size_bytes, bool)
            and isinstance(size_bytes, int)
            and size_bytes > 0
            and re.fullmatch(
                r"sha256:[0-9a-f]{64}",
                str(value.get("sha256") or "").strip().lower(),
            )
            is not None
            and not require_disposition
        )
    elif isinstance(value, Mapping) and set(value) == disposition_fields:
        valid = (
            str(value.get("status") or "") in allowed_dispositions
            and value.get("ref") is None
            and bool(str(value.get("reason") or "").strip())
        )
    else:
        valid = False
    if not valid:
        findings.append(
            _coverage_finding(
                "REFERENCE_EVIDENCE_EXACT_REF_INVALID",
                field,
                "bind kind/ref/size_bytes/sha256 evidence or an allowed explicit disposition",
            )
        )


def _active_inventory_exact_ref(
    value: object, findings: list[dict[str, object]]
) -> dict[str, object] | None:
    before = len(findings)
    _validate_reference_evidence_ref(
        value,
        "active_inventory_ref",
        findings,
        allowed_dispositions=(),
    )
    if len(findings) != before or not isinstance(value, Mapping):
        return None
    return {
        "kind": str(value["kind"]).strip(),
        "ref": str(value["ref"]).strip(),
        "size_bytes": value["size_bytes"],
        "sha256": str(value["sha256"]).strip().lower(),
    }


def audit_reference_lane_active_inventory_binding(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Require four citation-integrity lanes to consume one active inventory."""

    findings: list[dict[str, object]] = []
    lanes = candidate.get("lanes")
    required_lanes = {
        "citation_source_coverage",
        "active_reference_currentness",
        "excluded_reference_ledger",
        "claim_citation_edge_completeness",
    }
    if not isinstance(lanes, Mapping) or set(lanes) != required_lanes:
        findings.append(
            _coverage_finding(
                "REFERENCE_LANE_SET_INVALID",
                "lanes",
                "provide exactly the four citation-integrity lanes",
            )
        )
        lanes = {}
    identities: dict[str, tuple[str, str, int, str]] = {}
    active_key_sets: dict[str, set[str]] = {}
    for lane_name in sorted(required_lanes):
        lane = lanes.get(lane_name)
        if not isinstance(lane, Mapping):
            findings.append(
                _coverage_finding(
                    "REFERENCE_LANE_INVALID",
                    f"lanes.{lane_name}",
                    "provide the lane candidate and its active inventory ref",
                )
            )
            continue
        lane_findings: list[dict[str, object]] = []
        normalized_ref = _active_inventory_exact_ref(
            lane.get("active_inventory_ref"), lane_findings
        )
        if normalized_ref is None:
            findings.extend(
                {
                    **finding,
                    "field": f"lanes.{lane_name}.{finding['field']}",
                }
                for finding in lane_findings
            )
        else:
            identities[lane_name] = (
                str(normalized_ref["kind"]),
                str(normalized_ref["ref"]),
                int(normalized_ref["size_bytes"]),
                str(normalized_ref["sha256"]),
            )
        key_field = (
            "manuscript_citation_keys"
            if lane_name == "citation_source_coverage"
            else "active_keys"
        )
        key_findings: list[dict[str, object]] = []
        active_keys = _citation_key_set(lane.get(key_field), key_field, key_findings)
        if key_findings:
            findings.extend(
                {
                    **finding,
                    "field": f"lanes.{lane_name}.{finding['field']}",
                }
                for finding in key_findings
            )
        active_key_sets[lane_name] = active_keys
        if not active_keys:
            findings.append(
                _coverage_finding(
                    "REFERENCE_LANE_ACTIVE_KEY_SET_EMPTY",
                    f"lanes.{lane_name}.{key_field}",
                    "bind every lane to the non-empty active inventory",
                )
            )
    if identities and len(set(identities.values())) != 1:
        findings.append(
            _coverage_finding(
                "REFERENCE_LANE_ACTIVE_INVENTORY_MISMATCH",
                "lanes",
                "use one exact active inventory ref and digest across all four lanes",
            )
        )
    if active_key_sets and len({frozenset(keys) for keys in active_key_sets.values()}) != 1:
        findings.append(
            _coverage_finding(
                "REFERENCE_LANE_ACTIVE_KEY_SET_MISMATCH",
                "lanes",
                "use the same active citation-key set across all four lanes",
            )
        )
    if candidate.get("authority") is not False:
        findings.append(
            _coverage_finding(
                "REFERENCE_LANE_BINDING_AUTHORITY_FORBIDDEN",
                "authority",
                "keep lane binding refs-only with authority=false",
            )
        )
    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    shared_identity = (
        next(iter(identities.values()))
        if len(identities) == len(required_lanes)
        and len(set(identities.values())) == 1
        else None
    )
    return {
        "surface_kind": "reference_lane_active_inventory_binding_ref",
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "active_inventory_ref": None
        if shared_identity is None
        else {
            "kind": shared_identity[0],
            "ref": shared_identity[1],
            "size_bytes": shared_identity[2],
            "sha256": shared_identity[3],
        },
        "findings": findings,
        "route_back_candidate": None if complete else {
            "route": "medical-reference-integrity-auditor",
            "reason": "reference_lane_active_inventory_binding_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def validate_post_csl_reader_semantics(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Audit reader-facing post-CSL semantics on final DOCX and PDF exports."""

    findings: list[dict[str, object]] = []
    if candidate.get("surface_kind") != "post_csl_reader_semantics_candidate.v1":
        findings.append(
            _coverage_finding(
                "POST_CSL_SURFACE_KIND_INVALID",
                "surface_kind",
                "use the post-CSL reader-semantics candidate surface",
            )
        )

    semantic_records_value = candidate.get("semantic_records")
    semantic_records = (
        list(semantic_records_value)
        if isinstance(semantic_records_value, Sequence)
        and not isinstance(semantic_records_value, (str, bytes, bytearray))
        else []
    )
    if not semantic_records:
        findings.append(
            _coverage_finding(
                "POST_CSL_SEMANTIC_RECORDS_INVALID",
                "semantic_records",
                "provide the complete reader-facing semantic inventory",
            )
        )
    records_by_id: dict[str, Mapping[str, object]] = {}
    normalized_records: list[dict[str, object]] = []
    for index, record in enumerate(semantic_records):
        path = f"semantic_records[{index}]"
        if not isinstance(record, Mapping):
            findings.append(
                _coverage_finding(
                    "POST_CSL_SEMANTIC_RECORD_INVALID",
                    path,
                    "provide a structured semantic record",
                )
            )
            continue
        semantic_id = str(record.get("semantic_id") or "").strip()
        semantic_kind = str(record.get("semantic_kind") or "")
        canonical_text = str(record.get("canonical_text") or "")
        author_mode = str(record.get("author_mode") or "")
        correction_status = str(record.get("correction_status") or "")
        if not semantic_id:
            findings.append(
                _coverage_finding(
                    "POST_CSL_SEMANTIC_ID_MISSING",
                    f"{path}.semantic_id",
                    "bind each reader-facing semantic to a stable id",
                )
            )
        elif semantic_id in records_by_id:
            findings.append(
                _coverage_finding(
                    "POST_CSL_SEMANTIC_ID_DUPLICATE",
                    f"{path}.semantic_id",
                    "use one canonical record per semantic id",
                )
            )
        else:
            records_by_id[semantic_id] = record
        if semantic_kind not in POST_CSL_SEMANTIC_KINDS:
            findings.append(
                _coverage_finding(
                    "POST_CSL_SEMANTIC_KIND_INVALID",
                    f"{path}.semantic_kind",
                    "classify the semantic using the supported structured kinds",
                )
            )
        if not canonical_text:
            findings.append(
                _coverage_finding(
                    "POST_CSL_CANONICAL_TEXT_MISSING",
                    f"{path}.canonical_text",
                    "record the exact reader-facing text from official metadata",
                )
            )
        expected_author_mode = (
            "literal"
            if semantic_kind in {"corporate_author", "group_author"}
            else "not_applicable"
        )
        if author_mode != expected_author_mode:
            findings.append(
                _coverage_finding(
                    "POST_CSL_AUTHOR_MODE_INVALID",
                    f"{path}.author_mode",
                    "use literal mode for corporate or group authors only",
                )
            )
        expected_correction_status = (
            "corrected" if semantic_kind == "corrected_metadata" else "not_corrected"
        )
        if correction_status != expected_correction_status:
            findings.append(
                _coverage_finding(
                    "POST_CSL_CORRECTION_STATUS_INVALID",
                    f"{path}.correction_status",
                    "align correction status with the semantic record kind",
                )
            )
        _validate_reference_evidence_ref(
            record.get("official_metadata_ref"),
            f"{path}.official_metadata_ref",
            findings,
            allowed_dispositions=(),
        )
        correction_ref = record.get("correction_ref")
        if correction_status == "corrected":
            _validate_reference_evidence_ref(
                correction_ref,
                f"{path}.correction_ref",
                findings,
                allowed_dispositions=(),
            )
        elif correction_ref is not None:
            findings.append(
                _coverage_finding(
                    "POST_CSL_CORRECTION_REF_UNEXPECTED",
                    f"{path}.correction_ref",
                    "omit correction evidence when no correction applies",
                )
            )
        normalized_records.append(
            {
                "semantic_id": semantic_id,
                "semantic_kind": semantic_kind,
                "canonical_text": canonical_text,
                "author_mode": author_mode,
                "correction_status": correction_status,
            }
        )

    output_surfaces_value = candidate.get("output_surfaces")
    output_surfaces = output_surfaces_value if isinstance(output_surfaces_value, Mapping) else {}
    if set(output_surfaces) != set(POST_CSL_OUTPUT_SURFACES):
        findings.append(
            _coverage_finding(
                "POST_CSL_OUTPUT_SURFACE_SET_INVALID",
                "output_surfaces",
                "provide exactly the final DOCX and PDF post-CSL exports",
            )
        )
    normalized_surfaces: dict[str, dict[str, object]] = {}
    expected_ids = set(records_by_id)
    for surface in POST_CSL_OUTPUT_SURFACES:
        surface_value = output_surfaces.get(surface)
        path = f"output_surfaces.{surface}"
        if not isinstance(surface_value, Mapping):
            findings.append(
                _coverage_finding(
                    "POST_CSL_OUTPUT_SURFACE_INVALID",
                    path,
                    "provide exact artifact and post-CSL export refs plus rendered entries",
                )
            )
            continue
        for field in ("artifact_ref", "post_csl_export_ref"):
            _validate_reference_evidence_ref(
                surface_value.get(field),
                f"{path}.{field}",
                findings,
                allowed_dispositions=(),
            )
        entries_value = surface_value.get("rendered_entries")
        entries = (
            list(entries_value)
            if isinstance(entries_value, Sequence)
            and not isinstance(entries_value, (str, bytes, bytearray))
            else []
        )
        entries_by_id: dict[str, list[Mapping[str, object]]] = {}
        for entry_index, entry in enumerate(entries):
            entry_path = f"{path}.rendered_entries[{entry_index}]"
            if not isinstance(entry, Mapping):
                findings.append(
                    _coverage_finding(
                        "POST_CSL_RENDERED_ENTRY_INVALID",
                        entry_path,
                        "provide a structured reader-facing rendered entry",
                    )
                )
                continue
            semantic_id = str(entry.get("semantic_id") or "").strip()
            entries_by_id.setdefault(semantic_id, []).append(entry)
        if set(entries_by_id) != expected_ids:
            findings.append(
                _coverage_finding(
                    "POST_CSL_RENDERED_SEMANTIC_COVERAGE_MISMATCH",
                    f"{path}.rendered_entries",
                    "render every canonical semantic exactly once and no others",
                )
            )
        for semantic_id in sorted(expected_ids | set(entries_by_id)):
            matching = entries_by_id.get(semantic_id, [])
            entry_path = f"{path}.rendered_entries.{semantic_id}"
            if len(matching) != 1:
                findings.append(
                    _coverage_finding(
                        "POST_CSL_RENDERED_SEMANTIC_CARDINALITY_INVALID",
                        entry_path,
                        "render each canonical semantic exactly once",
                    )
                )
                continue
            record = records_by_id.get(semantic_id)
            if record is None:
                continue
            entry = matching[0]
            if str(entry.get("rendered_text") or "") != str(record.get("canonical_text") or ""):
                findings.append(
                    _coverage_finding(
                        "POST_CSL_READER_TEXT_MISMATCH",
                        f"{entry_path}.rendered_text",
                        "preserve the exact official reader-facing text after CSL rendering",
                    )
                )
            if str(entry.get("author_mode") or "") != str(record.get("author_mode") or ""):
                findings.append(
                    _coverage_finding(
                        "POST_CSL_READER_AUTHOR_MODE_MISMATCH",
                        f"{entry_path}.author_mode",
                        "preserve literal group or corporate author semantics",
                    )
                )
            if str(entry.get("correction_status") or "") != str(record.get("correction_status") or ""):
                findings.append(
                    _coverage_finding(
                        "POST_CSL_READER_CORRECTION_STATUS_MISMATCH",
                        f"{entry_path}.correction_status",
                        "render the current corrected metadata status on every final surface",
                    )
                )
        normalized_surfaces[surface] = {
            "artifact_ref": dict(surface_value.get("artifact_ref"))
            if isinstance(surface_value.get("artifact_ref"), Mapping)
            else None,
            "rendered_semantic_ids": sorted(entries_by_id),
        }

    if candidate.get("authority") is not False:
        findings.append(
            _coverage_finding(
                "POST_CSL_AUTHORITY_FORBIDDEN",
                "authority",
                "keep reader-semantics QA refs-only with authority=false",
            )
        )
    findings.sort(key=lambda item: (str(item["code"]), str(item["field"])))
    complete = not findings
    return {
        "surface_kind": "post_csl_reader_semantics_audit_candidate.v1",
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "semantic_records": normalized_records,
        "output_surfaces": normalized_surfaces,
        "findings": findings,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-reference-integrity-auditor",
            "reason": "post_csl_reader_semantics_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def _self_check() -> None:
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
    post_csl_fixture_path = Path(__file__).with_name("fixtures") / "post-csl-reader-semantics.json"
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


if __name__ == "__main__":
    _self_check()
