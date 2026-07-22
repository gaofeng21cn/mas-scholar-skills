"""Deterministic refs-only helpers for medical submission prep.

These helpers scaffold package manifests and checklist lint. They do not submit
files, mutate publication evals, or claim submission/publication readiness.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence


BASE_REQUIRED_DOCS = (
    "manuscript",
    "title_page",
    "figures",
    "tables",
    "supplement",
    "cover_letter",
    "ethics_statement",
    "funding_statement",
    "coi_statement",
    "data_code_availability",
    "reporting_guideline_checklist",
)

GUIDELINE_BY_ARTICLE = {
    "observational": "STROBE",
    "trial": "CONSORT",
    "systematic_review": "PRISMA",
    "prediction": "TRIPOD",
    "case_report": "CARE",
}

INTERNAL_ARTIFACT_ROLES = frozenset(
    {
        "audit",
        "internal_audit",
        "internal_review",
        "quality_control",
        "review_companion",
    }
)

SUPPLEMENTARY_ARTIFACT_ROLES = frozenset(
    {
        "supplement",
        "supplementary_document",
        "supplementary_figure",
        "supplementary_material",
        "supplementary_table",
    }
)

INTERNAL_VISIBLE_MARKER_RE = re.compile(
    r"(?:review companion|bounded review display|deterministic(?:ly)? sampled rows?|"
    r"CSV row(?:s| numbers?)?|exact electronic source|internal audit)",
    re.IGNORECASE,
)

PUBLICATION_LAYOUT_CATALOG_REF = (
    "packs/medical-publication-layouts/publication_layout_catalog.json"
)
PUBLICATION_LAYOUT_CATALOG_PATH = (
    Path(__file__).resolve().parents[2] / PUBLICATION_LAYOUT_CATALOG_REF
)
SUBMISSION_EXACT_REF_FIELDS = frozenset({"kind", "ref", "size_bytes", "sha256"})


def submission_manifest_schema() -> dict[str, Any]:
    """Return the minimal submission package manifest schema."""

    return {
        "type": "object",
        "required": [
            "journal_instruction_ref",
            "submission_inventory_ref",
            "reporting_guideline_ref",
            "package_consistency_ref",
        ],
        "properties": {
            "journal_instruction_ref": {"type": "string"},
            "journal_instruction_source_ref": {"type": "string"},
            "article_type": {"type": "string"},
            "stage": {"type": "string"},
            "files": {"type": "array", "items": {"type": "object"}},
            "reporting_guideline_ref": {"type": "string"},
            "data_code_availability_ref": {"type": "string"},
            "declaration_completeness_ref": {"type": "string"},
            "package_consistency_ref": {"type": "string"},
            "author_input_needed_ref": {"type": "array", "items": {"type": "string"}},
            "route_back_candidate": {"type": "string"},
        },
    }


def required_documents(article_type: str = "observational", stage: str = "first_submission") -> list[str]:
    """Return a deterministic required-document checklist."""

    docs = list(BASE_REQUIRED_DOCS)
    normalized_stage = stage.strip().lower().replace(" ", "_")
    normalized_type = article_type.strip().lower().replace(" ", "_")
    if normalized_stage in {"revision", "resubmission", "appeal"}:
        docs.append("reviewer_response")
    if normalized_type in GUIDELINE_BY_ARTICLE:
        docs.append(f"{GUIDELINE_BY_ARTICLE[normalized_type].lower()}_checklist")
    return docs


def normalize_file_label(value: object) -> str:
    """Normalize a package file label for manifest comparison."""

    text = str(value or "").strip().lower()
    text = re.sub(r"\.[a-z0-9]{1,5}$", "", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def package_manifest_skeleton(
    journal: str = "", article_type: str = "observational", stage: str = "first_submission"
) -> dict[str, object]:
    """Return a refs-only submission package manifest shell."""

    normalized_type = article_type.strip().lower().replace(" ", "_")
    return {
        "journal_instruction_ref": journal,
        "journal_instruction_source_ref": "",
        "article_type": article_type,
        "stage": stage,
        "required_documents": required_documents(article_type, stage),
        "files": [],
        "reporting_guideline_ref": GUIDELINE_BY_ARTICLE.get(normalized_type, ""),
        "data_code_availability_ref": "",
        "declaration_completeness_ref": "",
        "package_consistency_ref": "",
        "author_input_needed_ref": [],
        "route_back_candidate": "",
    }


def select_publication_layout(
    target_journal: str = "",
    *,
    formal_submission: bool = False,
    as_of_date: str | date | None = None,
    catalog_path: str | Path | None = None,
) -> dict[str, object]:
    """Select an offline publication layout profile without claiming compliance.

    A named known journal resolves to its local adaptation profile. An omitted or
    unknown journal keeps ordinary authoring moving with the publication-grade
    default reader profile. Formal submission always requires a fresh official
    instruction check outside this refs-only helper.
    """

    catalog = _load_publication_layout_catalog(catalog_path)
    profiles = {
        str(profile["profile_id"]): profile for profile in catalog["profiles"]
    }
    profile_positions = {
        str(profile["profile_id"]): index
        for index, profile in enumerate(catalog["profiles"])
    }
    default_profile_id = str(catalog["default_profile_id"])
    default_profile = profiles[default_profile_id]
    requested = str(target_journal or "").strip()
    normalized = _normalize_journal_alias(requested)

    alias_index: dict[str, str] = {}
    prefix_index: list[tuple[str, str]] = []
    for profile_id, profile in profiles.items():
        candidates = [profile_id, profile.get("display_name"), *(profile.get("aliases") or [])]
        for candidate in candidates:
            alias = _normalize_journal_alias(candidate)
            if alias:
                alias_index[alias] = profile_id
        for candidate in profile.get("alias_prefixes") or []:
            prefix = _normalize_journal_alias(candidate)
            if prefix:
                prefix_index.append((prefix, profile_id))

    matched_profile_id = alias_index.get(normalized) if normalized else None
    if normalized and matched_profile_id is None:
        prefix_matches = [
            (prefix, profile_id)
            for prefix, profile_id in prefix_index
            if normalized.startswith(f"{prefix} ")
        ]
        if prefix_matches:
            matched_profile_id = max(prefix_matches, key=lambda item: len(item[0]))[1]
    if not requested:
        profile = default_profile
        resolution_status = "default_reader_profile_selected"
        journal_export_status = "not_requested"
    elif matched_profile_id:
        profile = profiles[matched_profile_id]
        resolution_status = "matched_local_journal_profile"
        journal_export_status = "local_profile_selected"
    else:
        profile = default_profile
        resolution_status = "journal_profile_pending_official_mapping"
        journal_export_status = "official_mapping_pending"

    today = _coerce_date(as_of_date)
    freshness = _publication_profile_freshness(profile, today)
    known_journal = bool(requested and matched_profile_id)
    official_refresh_required = bool(
        requested
        and (
            not known_journal
            or formal_submission
            or freshness == "stale"
        )
    )
    if known_journal and official_refresh_required:
        journal_export_status = "local_profile_selected_refresh_pending"

    assets = dict(profile.get("template_assets") or {})
    output_names = [
        str(output["file_name"]) for output in catalog["core_pdf_outputs"]
    ]
    return {
        "surface_kind": "scholarskills_publication_layout_selection_candidate.v1",
        "catalog_ref": PUBLICATION_LAYOUT_CATALOG_REF,
        "requested_journal": requested,
        "formal_submission_requested": bool(formal_submission),
        "resolution_status": resolution_status,
        "selected_profile_id": str(profile["profile_id"]),
        "journal_profile_ref": (
            f"{PUBLICATION_LAYOUT_CATALOG_REF}#/profiles/{profile_positions[matched_profile_id]}"
            if known_journal
            else ""
        ),
        "rendering_profile_ref": str(profile["base_template_ref"]),
        "template_refs": assets,
        "authoring_rules": dict(profile.get("authoring_rules") or {}),
        "official_instruction_sources": list(profile.get("official_sources") or []),
        "profile_freshness": freshness if known_journal else (
            "not_applicable" if not requested else "not_available"
        ),
        "journal_specific_export_status": journal_export_status,
        "official_refresh_required": official_refresh_required,
        "authoring_may_continue": True,
        "core_pdf_outputs": output_names,
        "combined_reader_pdf_is_submission_upload": False,
        "can_claim_journal_compliance": False,
        "can_claim_submission_readiness": False,
        "can_submit": False,
        "owner_gate_required": True,
    }


def _load_publication_layout_catalog(
    catalog_path: str | Path | None,
) -> dict[str, Any]:
    path = Path(catalog_path) if catalog_path is not None else PUBLICATION_LAYOUT_CATALOG_PATH
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("surface_kind") != "mas_scholar_publication_layout_catalog.v1":
        raise ValueError("unsupported publication layout catalog")
    if [item.get("file_name") for item in value.get("core_pdf_outputs") or []] != [
        "paper.pdf",
        "paper_with_supplementary.pdf",
    ]:
        raise ValueError("publication layout catalog must expose exactly two core PDFs")
    return value


def _normalize_journal_alias(value: object) -> str:
    text = str(value or "").strip().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _coerce_date(value: str | date | None) -> date:
    if value is None:
        return date.today()
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _publication_profile_freshness(profile: Mapping[str, object], today: date) -> str:
    policy = profile.get("freshness_policy")
    if not isinstance(policy, Mapping):
        return "not_available"
    reviewed_on = policy.get("reviewed_on")
    max_age_days = policy.get("max_age_days")
    if not reviewed_on or not isinstance(max_age_days, int):
        return "not_applicable"
    age_days = (today - date.fromisoformat(str(reviewed_on))).days
    return "current" if age_days <= max_age_days else "stale"


def lint_required_documents(manifest: Mapping[str, object]) -> list[dict[str, str]]:
    """Flag missing package parts and naming issues without reading the filesystem."""

    article_type = str(manifest.get("article_type") or "observational")
    stage = str(manifest.get("stage") or "first_submission")
    required = set(manifest.get("required_documents") or required_documents(article_type, stage))
    files = list(manifest.get("files") or [])
    present = {_file_kind(item) for item in files}
    findings = [
        {"code": "MISSING_REQUIRED_DOCUMENT", "document": doc}
        for doc in sorted(required - present)
    ]
    for item in files:
        if not isinstance(item, Mapping):
            findings.append({"code": "FILE_ENTRY_NOT_OBJECT", "action": "normalize file manifest row"})
            continue
        name = str(item.get("path") or item.get("name") or "")
        if name and re.search(r"\s", name):
            findings.append({"code": "FILE_NAME_HAS_SPACES", "file": name})
        if str(item.get("status", "")).lower() in {"tbd", "missing", "author_input_needed"}:
            findings.append({"code": "AUTHOR_INPUT_NEEDED", "file": name or _file_kind(item)})
    return findings


def lint_submission_artifact_roles(
    artifacts: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Flag internal-review leakage and main/supplement role conflicts.

    Callers provide structured inventory rows; this helper does not open files
    or infer publication readiness from names alone.
    """

    findings: list[dict[str, object]] = []
    digest_roles: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for index, artifact in enumerate(artifacts, start=1):
        path = str(artifact.get("path") or artifact.get("name") or f"artifact_{index}").strip()
        kind = normalize_file_label(artifact.get("kind") or artifact.get("label"))
        package_role = normalize_file_label(
            artifact.get("package_role") or artifact.get("role") or kind
        )
        source_role = normalize_file_label(artifact.get("source_role"))
        audience = normalize_file_label(artifact.get("audience"))
        document_role = normalize_file_label(
            artifact.get("document_role") or artifact.get("placement")
        )
        included = artifact.get("included_in_submission") is not False
        visible_text = " ".join(
            str(artifact.get(field) or "")
            for field in ("visible_title", "content_markers", "description")
        )
        internal_role = bool(
            {kind, package_role, source_role, audience} & INTERNAL_ARTIFACT_ROLES
        )
        if included and internal_role:
            findings.append(
                _package_role_finding(
                    "INTERNAL_REVIEW_ARTIFACT_EXPOSED_TO_JOURNAL",
                    path,
                    "remove the internal artifact from the journal allowlist and export a reader-facing counterpart",
                )
            )
        if included and INTERNAL_VISIBLE_MARKER_RE.search(visible_text):
            findings.append(
                _package_role_finding(
                    "INTERNAL_REVIEW_LANGUAGE_ON_SUBMISSION_ARTIFACT",
                    path,
                    "replace review-companion content with a curated reader-facing artifact",
                )
            )

        supplementary_role = bool(
            {kind, package_role} & SUPPLEMENTARY_ARTIFACT_ROLES
            or kind.startswith("supplementary_")
            or package_role.startswith("supplementary_")
        )
        if included and supplementary_role and internal_role:
            findings.append(
                _package_role_finding(
                    "SUPPLEMENT_ARTIFACT_ROLE_MISMATCH",
                    path,
                    "bind the supplement path to a reader-facing supplementary source, not an internal review source",
                )
            )
        if included and supplementary_role and document_role in {
            "main",
            "main_document",
            "main_manuscript",
        }:
            findings.append(
                _package_role_finding(
                    "SUPPLEMENTARY_MEMBER_IN_MAIN_DOCUMENT",
                    path,
                    "move the supplementary member out of the main manuscript export",
                )
            )

        digest = str(artifact.get("sha256") or "").strip().lower().removeprefix("sha256:")
        if included and re.fullmatch(r"[0-9a-f]{64}", digest):
            digest_roles[digest].append((path, package_role or kind))

    for digest, members in digest_roles.items():
        roles = {role for _, role in members if role}
        if roles & INTERNAL_ARTIFACT_ROLES and roles - INTERNAL_ARTIFACT_ROLES:
            findings.append(
                {
                    "code": "CONFLICTING_PACKAGE_ROLES_FOR_SAME_BYTES",
                    "sha256": f"sha256:{digest}",
                    "members": [path for path, _ in members],
                    "roles": sorted(roles),
                    "action": "publish one reader-facing role and keep internal aliases outside the submission allowlist",
                    "writes_authority": False,
                }
            )
    return findings


def validate_submission_figure_numbering_binding(
    candidate: Mapping[str, object],
) -> dict[str, Any]:
    """Bind the final DOCX/PDF package to one exact numbering audit."""

    findings: list[dict[str, object]] = []
    if candidate.get("surface_kind") != "submission_figure_numbering_binding_candidate.v1":
        findings.append(
            _package_role_finding(
                "SUBMISSION_FIGURE_NUMBERING_SURFACE_KIND_INVALID",
                "surface_kind",
                "use the submission figure-numbering binding surface",
            )
        )
    for field in ("figure_numbering_audit_ref", "final_docx_ref", "final_pdf_ref"):
        if not _submission_exact_ref_valid(candidate.get(field)):
            findings.append(
                _package_role_finding(
                    "SUBMISSION_FIGURE_NUMBERING_EXACT_REF_INVALID",
                    field,
                    "bind the audit and both final outputs as exact refs",
                )
            )
    audit = candidate.get("audit_summary")
    if not isinstance(audit, Mapping):
        findings.append(
            _package_role_finding(
                "SUBMISSION_FIGURE_NUMBERING_AUDIT_INVALID",
                "audit_summary",
                "consume the structured dual-build numbering audit",
            )
        )
        audit = {}
    else:
        if audit.get("machine_check_status") != "candidate_complete":
            findings.append(
                _package_role_finding(
                    "SUBMISSION_FIGURE_NUMBERING_AUDIT_INCOMPLETE",
                    "audit_summary.machine_check_status",
                    "repair the dual-build numbering audit before package assembly",
                )
            )
        if audit.get("authority") is not False:
            findings.append(
                _package_role_finding(
                    "SUBMISSION_FIGURE_NUMBERING_AUDIT_AUTHORITY_FORBIDDEN",
                    "audit_summary.authority",
                    "consume a refs-only numbering audit",
                )
            )
    output_refs = audit.get("output_artifact_refs") if isinstance(audit, Mapping) else None
    if not isinstance(output_refs, Mapping) or set(output_refs) != {"docx", "pdf"}:
        findings.append(
            _package_role_finding(
                "SUBMISSION_FIGURE_NUMBERING_OUTPUT_BINDING_INVALID",
                "audit_summary.output_artifact_refs",
                "bind the audit to exactly the final DOCX and PDF refs",
            )
        )
    else:
        expected_refs = {
            "docx": candidate.get("final_docx_ref"),
            "pdf": candidate.get("final_pdf_ref"),
        }
        for surface, expected_ref in expected_refs.items():
            if not _submission_exact_ref_valid(output_refs.get(surface)) or output_refs.get(surface) != expected_ref:
                findings.append(
                    _package_role_finding(
                        "SUBMISSION_FIGURE_NUMBERING_OUTPUT_BINDING_MISMATCH",
                        f"audit_summary.output_artifact_refs.{surface}",
                        "consume the audit for these exact final output bytes",
                    )
                )
    invariants_value = audit.get("figure_surface_invariants") if isinstance(audit, Mapping) else None
    invariants = (
        list(invariants_value)
        if isinstance(invariants_value, Sequence)
        and not isinstance(invariants_value, (str, bytes, bytearray))
        else []
    )
    coverage: dict[str, set[str]] = defaultdict(set)
    if not invariants:
        findings.append(
            _package_role_finding(
                "SUBMISSION_FIGURE_NUMBERING_INVARIANTS_MISSING",
                "audit_summary.figure_surface_invariants",
                "consume member-level DOCX/PDF exactly-one results",
            )
        )
    for index, invariant in enumerate(invariants):
        path = f"audit_summary.figure_surface_invariants[{index}]"
        if not isinstance(invariant, Mapping):
            findings.append(
                _package_role_finding(
                    "SUBMISSION_FIGURE_NUMBERING_INVARIANT_INVALID",
                    path,
                    "provide a structured figure and output-surface invariant",
                )
            )
            continue
        figure_id = str(invariant.get("figure_id") or "").strip()
        surface = str(invariant.get("output_surface") or "")
        if not figure_id or surface not in {"docx", "pdf"}:
            findings.append(
                _package_role_finding(
                    "SUBMISSION_FIGURE_NUMBERING_INVARIANT_ID_INVALID",
                    path,
                    "bind every invariant to a figure id and final output surface",
                )
            )
            continue
        if surface in coverage[figure_id]:
            findings.append(
                _package_role_finding(
                    "SUBMISSION_FIGURE_NUMBERING_INVARIANT_DUPLICATE",
                    path,
                    "provide one invariant per figure and output surface",
                )
            )
        coverage[figure_id].add(surface)
        if invariant.get("occurrence_count") != 1:
            findings.append(
                _package_role_finding(
                    "SUBMISSION_FIGURE_NUMBERING_EXACTLY_ONE_VIOLATION",
                    path,
                    "require exactly one final figure-number label",
                )
            )
    for figure_id, surfaces in coverage.items():
        if surfaces != {"docx", "pdf"}:
            findings.append(
                _package_role_finding(
                    "SUBMISSION_FIGURE_NUMBERING_SURFACE_COVERAGE_MISMATCH",
                    f"audit_summary.figure_surface_invariants.{figure_id}",
                    "close both final DOCX and PDF for every figure",
                )
            )
    if candidate.get("authority") is not False:
        findings.append(
            _package_role_finding(
                "SUBMISSION_FIGURE_NUMBERING_AUTHORITY_FORBIDDEN",
                "authority",
                "keep submission numbering QA refs-only with authority=false",
            )
        )

    findings.sort(key=lambda item: (str(item["code"]), str(item["file"])))
    complete = not findings
    return {
        "surface_kind": "submission_figure_numbering_binding_audit_candidate.v1",
        "machine_check_status": "candidate_complete" if complete else "route_back_required",
        "figure_ids": sorted(coverage),
        "findings": findings,
        "route_back_candidate": None
        if complete
        else {
            "route": "medical-submission-prep",
            "reason": "submission_figure_numbering_binding_requires_repair",
            "authority": False,
        },
        "authority": False,
    }


def _submission_exact_ref_valid(value: object) -> bool:
    if not isinstance(value, Mapping) or set(value) != SUBMISSION_EXACT_REF_FIELDS:
        return False
    size_bytes = value.get("size_bytes")
    return bool(
        str(value.get("kind") or "").strip()
        and str(value.get("ref") or "").strip()
        and not isinstance(size_bytes, bool)
        and isinstance(size_bytes, int)
        and size_bytes > 0
        and re.fullmatch(r"sha256:[0-9a-f]{64}", str(value.get("sha256") or ""))
    )


def _package_role_finding(code: str, path: str, action: str) -> dict[str, object]:
    return {
        "code": code,
        "file": path,
        "action": action,
        "writes_authority": False,
    }


def _file_kind(item: object) -> str:
    if isinstance(item, Mapping):
        return normalize_file_label(item.get("kind") or item.get("label") or item.get("name"))
    return normalize_file_label(item)


def _self_check() -> None:
    assert "submission_inventory_ref" in submission_manifest_schema()["required"]
    assert "strobe_checklist" in required_documents("observational")
    assert "reviewer_response" in required_documents("observational", "revision")
    manifest = package_manifest_skeleton("Journal", "prediction")
    assert manifest["reporting_guideline_ref"] == "TRIPOD"
    lint = lint_required_documents({"files": [{"kind": "manuscript", "name": "main file.docx"}]})
    assert {item["code"] for item in lint} >= {"MISSING_REQUIRED_DOCUMENT", "FILE_NAME_HAS_SPACES"}
    digest = "1" * 64
    role_findings = lint_submission_artifact_roles(
        [
            {
                "path": "internal/supplement-review.pdf",
                "kind": "review_companion",
                "package_role": "internal_review",
                "included_in_submission": True,
                "sha256": digest,
            },
            {
                "path": "submission/supplement.pdf",
                "kind": "supplementary_document",
                "package_role": "supplementary_material",
                "source_role": "review_companion",
                "document_role": "main_document",
                "visible_title": "Supplementary Table Review Companion",
                "included_in_submission": True,
                "sha256": digest,
            },
        ]
    )
    assert {item["code"] for item in role_findings} == {
        "INTERNAL_REVIEW_ARTIFACT_EXPOSED_TO_JOURNAL",
        "INTERNAL_REVIEW_LANGUAGE_ON_SUBMISSION_ARTIFACT",
        "SUPPLEMENT_ARTIFACT_ROLE_MISMATCH",
        "SUPPLEMENTARY_MEMBER_IN_MAIN_DOCUMENT",
        "CONFLICTING_PACKAGE_ROLES_FOR_SAME_BYTES",
    }
    assert all(item["writes_authority"] is False for item in role_findings)
    default_layout = select_publication_layout(as_of_date="2026-07-20")
    assert default_layout["selected_profile_id"] == "general-medical-reader.v1"
    assert default_layout["core_pdf_outputs"] == [
        "paper.pdf",
        "paper_with_supplementary.pdf",
    ]
    journal_layout = select_publication_layout(
        "JAMA Network Open", as_of_date="2026-07-20"
    )
    assert journal_layout["selected_profile_id"] == "jama-network-research.v1"
    frontiers_layout = select_publication_layout(
        "Frontiers in Cardiology", as_of_date="2026-07-20"
    )
    assert frontiers_layout["selected_profile_id"] == "frontiers-research-article.v1"
    frontier_false_positive = select_publication_layout(
        "Frontier Medicine", as_of_date="2026-07-20"
    )
    assert frontier_false_positive["selected_profile_id"] == "general-medical-reader.v1"
    unknown_layout = select_publication_layout(
        "Unknown Journal", as_of_date="2026-07-20"
    )
    assert unknown_layout["authoring_may_continue"] is True
    assert unknown_layout["official_refresh_required"] is True
    formal_layout = select_publication_layout(
        "NEJM", formal_submission=True, as_of_date="2026-07-20"
    )
    assert formal_layout["official_refresh_required"] is True
    assert formal_layout["can_claim_journal_compliance"] is False
    numbering_fixture_path = (
        Path(__file__).parents[1]
        / "medical-display-qc"
        / "fixtures"
        / "figure-numbering-one-owner.json"
    )
    numbering_fixture = json.loads(numbering_fixture_path.read_text(encoding="utf-8"))
    binding_audit = validate_submission_figure_numbering_binding(
        numbering_fixture["submission_binding_candidate"]
    )
    assert binding_audit["machine_check_status"] == "candidate_complete"
    bad_binding = json.loads(json.dumps(numbering_fixture["submission_binding_candidate"]))
    bad_binding["audit_summary"]["figure_surface_invariants"][0]["occurrence_count"] = 2
    assert "SUBMISSION_FIGURE_NUMBERING_EXACTLY_ONE_VIOLATION" in {
        item["code"] for item in validate_submission_figure_numbering_binding(bad_binding)["findings"]
    }
    print(json.dumps({"ok": True, "checks": 17}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
