"""Deterministic refs-only helpers for medical submission prep.

These helpers scaffold package manifests and checklist lint. They do not submit
files, mutate publication evals, or claim submission/publication readiness.
"""

from __future__ import annotations

import json
import re
from typing import Any, Mapping


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
    print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
