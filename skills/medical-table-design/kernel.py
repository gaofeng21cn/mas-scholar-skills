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
INTERNAL_AUDIT_NOTE_RE = re.compile(
    r"(?:source generation|generation[_ -]?id|formal_submission_authority|"
    r"runtime_authority|submit_ready|candidate display only|owner receipt)",
    re.IGNORECASE,
)
REPEATED_LONG_NOTE_MIN_CHARS = 80
TABLE_NOTE_BUDGETS = {"main": 2, "main_text": 2, "supplementary": 3}
MAIN_TABLE_ROLES = {"main", "main_text"}
DEFAULT_MAIN_TABLE_INFORMATION_BUDGET = {
    "max_body_rows": 15,
    "max_columns": 8,
    "max_body_words": 350,
    "max_cell_words": 24,
    "max_footnote_words": 45,
    "reader_question_count": 1,
    "max_page_span": 1,
}
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[./'-][A-Za-z0-9]+)*")


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


def _word_count(value: object) -> int:
    return len(WORD_RE.findall(str(value or "")))


def _row_cells(row: object, columns: Sequence[object]) -> list[object]:
    if isinstance(row, Mapping):
        keys = [
            str(column.get("key") or column.get("label") or "")
            if isinstance(column, Mapping)
            else str(column)
            for column in columns
        ]
        return [row.get(key, "") for key in keys]
    if isinstance(row, Sequence) and not isinstance(row, (str, bytes)):
        return list(row)
    return [row]


def summarize_main_table_information_load(
    table: Mapping[str, object],
) -> dict[str, object]:
    """Return a deterministic, refs-only information-load assessment."""

    columns = list(table.get("columns") or [])
    rows = list(table.get("rows") or [])
    cells = [cell for row in rows for cell in _row_cells(row, columns)]
    raw_notes = table.get("footnotes")
    if raw_notes is None:
        raw_notes = table.get("notes")
    notes = [str(note).strip() for note in raw_notes or [] if str(note).strip()]
    reader_question = str(table.get("reader_question") or "").strip()
    supplementary_refs = [
        str(ref).strip()
        for ref in table.get("supplementary_detail_refs") or []
        if str(ref).strip()
    ]
    final_embedding = table.get("final_embedding")
    embedding = final_embedding if isinstance(final_embedding, Mapping) else {}
    return {
        "table_id": str(table.get("table_id") or "table").strip(),
        "role": str(table.get("role") or "main").strip().lower(),
        "reader_question": reader_question,
        "row_count": len(rows),
        "column_count": len(columns),
        "body_word_count": sum(_word_count(cell) for cell in cells),
        "max_cell_word_count": max((_word_count(cell) for cell in cells), default=0),
        "footnote_word_count": sum(_word_count(note) for note in notes),
        "supplementary_detail_refs": supplementary_refs,
        "final_embedding_status": str(embedding.get("status") or "pending"),
        "final_embedding_page_span": embedding.get("page_span"),
        "budget_status": str(table.get("budget_status") or "within_default_budget").strip(),
        "exception_reason": str(table.get("exception_reason") or "").strip(),
        "standalone_notes_heading_present": bool(
            table.get("standalone_notes_heading_present", False)
        ),
        "default_budget": dict(DEFAULT_MAIN_TABLE_INFORMATION_BUDGET),
    }


def lint_main_table_information_budget(
    tables: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Flag overloaded main tables without prescribing a fixed template."""

    findings: list[dict[str, object]] = []
    budget = DEFAULT_MAIN_TABLE_INFORMATION_BUDGET
    for table in tables:
        summary = summarize_main_table_information_load(table)
        if summary["role"] not in MAIN_TABLE_ROLES:
            continue
        table_id = str(summary["table_id"])
        checks = (
            ("row_count", "max_body_rows", "MAIN_TABLE_ROW_BUDGET_EXCEEDED"),
            ("column_count", "max_columns", "MAIN_TABLE_COLUMN_BUDGET_EXCEEDED"),
            ("body_word_count", "max_body_words", "MAIN_TABLE_BODY_WORD_BUDGET_EXCEEDED"),
            ("max_cell_word_count", "max_cell_words", "MAIN_TABLE_CELL_WORD_BUDGET_EXCEEDED"),
            ("footnote_word_count", "max_footnote_words", "MAIN_TABLE_FOOTNOTE_WORD_BUDGET_EXCEEDED"),
        )
        exceeded_checks = []
        for observed_key, limit_key, code in checks:
            observed = int(summary[observed_key])
            limit = int(budget[limit_key])
            if observed > limit:
                exceeded_checks.append((code, observed, limit))
        budget_status = str(summary["budget_status"])
        exception_reason = str(summary["exception_reason"])
        documented_exception = (
            budget_status == "documented_exception" and bool(exception_reason)
        )
        if budget_status not in {"within_default_budget", "documented_exception"}:
            findings.append(
                {
                    "code": "MAIN_TABLE_BUDGET_STATUS_INVALID",
                    "table_id": table_id,
                    "action": "use within_default_budget or a documented_exception",
                }
            )
        if budget_status == "documented_exception" and not exception_reason:
            findings.append(
                {
                    "code": "MAIN_TABLE_EXCEPTION_REASON_MISSING",
                    "table_id": table_id,
                    "action": "state the journal- or table-specific readability reason",
                }
            )
        if not documented_exception:
            for code, observed, limit in exceeded_checks:
                findings.append(
                    {
                        "code": code,
                        "table_id": table_id,
                        "observed": observed,
                        "limit": limit,
                        "action": "compact the main table or document a readable journal-specific exception",
                    }
                )
        if not summary["reader_question"]:
            findings.append(
                {
                    "code": "MAIN_TABLE_READER_QUESTION_INVALID",
                    "table_id": table_id,
                    "action": "state the single reader question answered by this main table",
                }
            )
        if exceeded_checks and not documented_exception and not summary["supplementary_detail_refs"]:
            findings.append(
                {
                    "code": "MAIN_TABLE_SUPPLEMENTARY_ROUTE_MISSING",
                    "table_id": table_id,
                    "action": "route the complete detail to a named supplementary table",
                }
            )
        if summary["standalone_notes_heading_present"]:
            findings.append(
                {
                    "code": "MAIN_TABLE_STANDALONE_NOTES_HEADING_PRESENT",
                    "table_id": table_id,
                    "action": "render concise general or keyed footnotes without a Notes heading",
                }
            )
        if (
            summary["final_embedding_status"] != "passed"
            or not isinstance(summary["final_embedding_page_span"], int)
            or int(summary["final_embedding_page_span"]) > budget["max_page_span"]
        ):
            findings.append(
                {
                    "code": "MAIN_TABLE_FINAL_EMBEDDING_NOT_ONE_PAGE",
                    "table_id": table_id,
                    "action": "inspect the final-size embedded table and keep it to one readable page",
                }
            )
    return findings


def lint_table_note_inventory(
    tables: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Flag overloaded, repeated, or internal reader-visible table notes.

    The result is refs-only quality debt. It does not decide whether a table is
    accepted, authoritative, or publication ready.
    """

    findings: list[dict[str, object]] = []
    note_locations: dict[str, list[str]] = {}
    note_originals: dict[str, str] = {}
    for index, table in enumerate(tables, start=1):
        table_id = str(table.get("table_id") or f"table_{index}").strip()
        role = str(table.get("role") or "main").strip().lower()
        raw_notes = table.get("notes") or []
        if not isinstance(raw_notes, Sequence) or isinstance(raw_notes, (str, bytes)):
            findings.append(
                {
                    "code": "TABLE_NOTES_NOT_LIST",
                    "table_id": table_id,
                    "action": "represent reader-visible notes as a string list",
                }
            )
            continue
        notes = [str(note).strip() for note in raw_notes if str(note).strip()]
        budget = TABLE_NOTE_BUDGETS.get(role)
        if budget is not None and len(notes) > budget:
            findings.append(
                {
                    "code": "TABLE_NOTE_BUDGET_EXCEEDED",
                    "table_id": table_id,
                    "role": role,
                    "note_count": len(notes),
                    "budget": budget,
                    "action": "retain only table-specific reading aids and move methods or global caveats out",
                }
            )
        for note in notes:
            if INTERNAL_AUDIT_NOTE_RE.search(note):
                findings.append(
                    {
                        "code": "INTERNAL_AUDIT_METADATA_IN_READER_NOTE",
                        "table_id": table_id,
                        "action": "move generation, runtime, authority, or readiness metadata to a manifest or receipt",
                    }
                )
            normalized = re.sub(r"\s+", " ", note).strip().casefold()
            note_locations.setdefault(normalized, []).append(table_id)
            note_originals.setdefault(normalized, note)

    for normalized, table_ids in note_locations.items():
        unique_table_ids = sorted(set(table_ids))
        if len(unique_table_ids) < 2 or len(normalized) < REPEATED_LONG_NOTE_MIN_CHARS:
            continue
        findings.append(
            {
                "code": "REPEATED_GLOBAL_TABLE_NOTE",
                "table_ids": unique_table_ids,
                "note": note_originals[normalized],
                "action": "state the global interpretation boundary once in Methods or Limitations",
            }
        )
    return findings


def _self_check() -> None:
    assert "columns" in table_shell_schema()["required"]
    assert normalize_column_name("HbA1c (%)") == "hba1c_percent"
    shell = table_shell_skeleton("baseline", ["N", "Female (%)"])
    assert shell["columns"][1]["format_hint"] == "percentage with denominator"
    findings = lint_table_shell(shell)
    assert {item["code"] for item in findings} >= {"MISSING_TITLE", "MISSING_PERCENT_DENOMINATOR"}
    assert abbreviations_without_footnote(["BMI"], ["BMI, body mass index"]) == []
    global_note = (
        "These recorded candidate states do not establish actual medication use, "
        "guideline nonadherence, care quality, or facility performance."
    )
    note_findings = lint_table_note_inventory(
        [
            {
                "table_id": "T1",
                "role": "main",
                "notes": [global_note, "Data are median [Q1, Q3].", "Abbreviation: BMI."],
            },
            {
                "table_id": "T2",
                "role": "main",
                "notes": [global_note, "Source generation: internal."],
            },
        ]
    )
    assert {item["code"] for item in note_findings} == {
        "TABLE_NOTE_BUDGET_EXCEEDED",
        "INTERNAL_AUDIT_METADATA_IN_READER_NOTE",
        "REPEATED_GLOBAL_TABLE_NOTE",
    }
    assert lint_table_note_inventory(
        [
            {
                "table_id": "T1",
                "role": "main",
                "notes": ["Data are n/N (%).", "Abbreviation: BMI, body mass index."],
            }
        ]
    ) == []
    overloaded_rows = [
        ["very long reader-facing cell text " * 5 for _ in range(9)]
        for _ in range(23)
    ]
    overloaded = lint_main_table_information_budget(
        [
            {
                "table_id": "T1",
                "role": "main",
                "reader_question": "Who is in the cohort?",
                "columns": [f"column_{index}" for index in range(9)],
                "rows": overloaded_rows,
                "footnotes": ["Methods details " * 30],
                "standalone_notes_heading_present": True,
                "final_embedding": {"status": "pending", "page_span": 2},
            }
        ]
    )
    overloaded_codes = {item["code"] for item in overloaded}
    assert {
        "MAIN_TABLE_ROW_BUDGET_EXCEEDED",
        "MAIN_TABLE_COLUMN_BUDGET_EXCEEDED",
        "MAIN_TABLE_BODY_WORD_BUDGET_EXCEEDED",
        "MAIN_TABLE_FOOTNOTE_WORD_BUDGET_EXCEEDED",
        "MAIN_TABLE_SUPPLEMENTARY_ROUTE_MISSING",
        "MAIN_TABLE_STANDALONE_NOTES_HEADING_PRESENT",
        "MAIN_TABLE_FINAL_EMBEDDING_NOT_ONE_PAGE",
    }.issubset(overloaded_codes)
    compact = {
        "table_id": "T2",
        "role": "main_text",
        "reader_question": "How do the four phenotypes differ on the core signals?",
        "columns": ["Phenotype", "n (%)", "Age", "HbA1c", "Mismatch"],
        "rows": [
            ["A", "100 (25.0)", "62", "7.2", "30/80 (37.5)"],
            ["B", "100 (25.0)", "63", "7.4", "28/75 (37.3)"],
            ["C", "100 (25.0)", "61", "7.1", "20/70 (28.6)"],
            ["D", "100 (25.0)", "64", "7.5", "35/85 (41.2)"],
        ],
        "footnotes": ["Data are n/N (%) or median."],
        "supplementary_detail_refs": ["TS28"],
        "final_embedding": {"status": "passed", "page_span": 1},
    }
    assert lint_main_table_information_budget([compact]) == []
    documented_exception = {
        **compact,
        "table_id": "T3",
        "rows": compact["rows"] * 4,
        "budget_status": "documented_exception",
        "exception_reason": "The target journal permits this readable baseline table.",
    }
    assert lint_main_table_information_budget([documented_exception]) == []
    print(json.dumps({"ok": True, "checks": 10}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
