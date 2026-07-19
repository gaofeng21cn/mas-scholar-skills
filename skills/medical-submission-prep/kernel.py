"""Deterministic refs-only helpers for medical submission prep.

These helpers scaffold package manifests and checklist lint. They do not submit
files, mutate publication evals, or claim submission/publication readiness.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
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
    print(json.dumps({"ok": True, "checks": 7}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
