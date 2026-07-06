"""Deterministic refs-only helpers for medical table design.

These helpers scaffold table shells, column names, and lint hints. They do not
create table artifacts, accept denominators, or claim publication readiness.
"""

from __future__ import annotations

import json
import re
from typing import Any, Mapping, Sequence


TABLE_JOBS = (
    "baseline",
    "cohort_flow",
    "result_summary",
    "model_result",
    "sensitivity",
    "missingness",
    "data_dictionary",
    "submission",
)

ABBREVIATION_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,}\b")


def table_shell_schema() -> dict[str, Any]:
    """Return the minimal table shell schema for refs-only handoff."""

    return {
        "type": "object",
        "required": [
            "table_job_ref",
            "table_shell_ref",
            "columns",
            "source_metric_ref",
            "denominator_ref",
            "footnotes",
        ],
        "properties": {
            "table_job_ref": {"type": "string"},
            "table_shell_ref": {"type": "string"},
            "title": {"type": "string"},
            "columns": {"type": "array", "items": {"type": "object"}},
            "rows": {"type": "array", "items": {"type": "object"}},
            "source_metric_ref": {"type": "string"},
            "denominator_ref": {"type": "string"},
            "statistical_display_ref": {"type": "string"},
            "footnotes": {"type": "array", "items": {"type": "string"}},
            "route_back_candidate": {"type": "string"},
        },
    }


def normalize_column_name(value: object) -> str:
    """Normalize a table column label to a stable snake_case key."""

    text = str(value or "").strip().lower()
    text = text.replace("%", " percent ")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def table_shell_skeleton(table_job: str, columns: Sequence[str]) -> dict[str, object]:
    """Return a table shell without filling data values."""

    normalized_job = table_job.strip().lower().replace(" ", "_")
    if normalized_job not in TABLE_JOBS:
        normalized_job = "custom"
    return {
        "table_job_ref": normalized_job,
        "table_shell_ref": "",
        "title": "",
        "columns": [
            {
                "label": column,
                "key": normalize_column_name(column),
                "unit": "",
                "format_hint": numeric_format_hint(column),
                "source_metric_ref": "",
                "denominator_ref": "",
            }
            for column in columns
        ],
        "rows": [],
        "footnotes": [],
        "route_back_candidate": "",
    }


def numeric_format_hint(label: object) -> str:
    """Return a simple display-format hint from a metric label."""

    text = str(label or "").lower()
    key_parts = normalize_column_name(text).split("_")
    if "p" in key_parts or "p_value" in normalize_column_name(text):
        return "p-value, 3 decimals or threshold"
    if any(term in text for term in ("percent", "%", "proportion", "rate")):
        return "percentage with denominator"
    if any(term in text for term in ("n", "count", "events")):
        return "integer count"
    if any(term in text for term in ("ci", "confidence interval", "estimate", "or", "hr", "rr")):
        return "estimate with uncertainty"
    return "declare unit and decimal policy"


def lint_table_shell(shell: Mapping[str, object]) -> list[dict[str, str]]:
    """Flag table-shell completeness issues without validating source truth."""

    findings: list[dict[str, str]] = []
    if not str(shell.get("title", "")).strip():
        findings.append({"code": "MISSING_TITLE", "action": "add descriptive table title"})
    columns = list(shell.get("columns") or [])
    if not columns:
        findings.append({"code": "NO_COLUMNS", "action": "define table columns"})
    for index, column in enumerate(columns, start=1):
        if not isinstance(column, Mapping):
            findings.append({"code": "COLUMN_NOT_OBJECT", "action": f"normalize column {index}"})
            continue
        label = str(column.get("label") or column.get("key") or f"column_{index}")
        if not str(column.get("source_metric_ref", "")).strip():
            findings.append({"code": "MISSING_SOURCE_METRIC", "column": label})
        if "percent" in normalize_column_name(label) and not str(column.get("denominator_ref", "")).strip():
            findings.append({"code": "MISSING_PERCENT_DENOMINATOR", "column": label})
    undefined = abbreviations_without_footnote(
        [str(c.get("label", "")) for c in columns if isinstance(c, Mapping)],
        [str(note) for note in shell.get("footnotes") or []],
    )
    for abbreviation in undefined:
        findings.append({"code": "UNDEFINED_ABBREVIATION", "column": abbreviation})
    return findings


def abbreviations_without_footnote(labels: Sequence[str], footnotes: Sequence[str]) -> list[str]:
    """Return uppercase abbreviations not mentioned in footnotes."""

    note_text = " ".join(footnotes)
    abbreviations = sorted({term for label in labels for term in ABBREVIATION_RE.findall(label)})
    return [term for term in abbreviations if term not in note_text]


def _self_check() -> None:
    assert "columns" in table_shell_schema()["required"]
    assert normalize_column_name("HbA1c (%)") == "hba1c_percent"
    shell = table_shell_skeleton("baseline", ["N", "Female (%)"])
    assert shell["columns"][1]["format_hint"] == "percentage with denominator"
    findings = lint_table_shell(shell)
    assert {item["code"] for item in findings} >= {"MISSING_TITLE", "MISSING_PERCENT_DENOMINATOR"}
    assert abbreviations_without_footnote(["BMI"], ["BMI, body mass index"]) == []
    print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
