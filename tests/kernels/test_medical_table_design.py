"""Extracted pytest suite for skills/medical-table-design/kernel.py."""

from __future__ import annotations

import json

from tests.kernels._loader import load_kernel

KERNEL = load_kernel("medical-table-design")
abbreviations_without_footnote = KERNEL.abbreviations_without_footnote
lint_main_table_information_budget = KERNEL.lint_main_table_information_budget
lint_table_note_inventory = KERNEL.lint_table_note_inventory
lint_table_shell = KERNEL.lint_table_shell
normalize_column_name = KERNEL.normalize_column_name
table_shell_schema = KERNEL.table_shell_schema
table_shell_skeleton = KERNEL.table_shell_skeleton
validate_baseline_table_traceability = KERNEL.validate_baseline_table_traceability

def test_medical_table_design() -> None:
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
    physical_activity_conflict = validate_baseline_table_traceability(
        {
            "rows": [
                {
                    "variable_key": "physical_activity",
                    "unit": "n (%)",
                    "denominator_ref": "denominator:available-records",
                    "source_metric_ref": "metric:physical-activity",
                    "smd_source_ref": "metric:physical-activity-smd",
                    "groups": [
                        {
                            "group_id": "development",
                            "group_n": 5000,
                            "available_n": 4800,
                            "missing_n": 200,
                            "summary_denominator_n": 4800,
                            "source_ref": "table:source-development",
                        },
                        {
                            "group_id": "validation",
                            "group_n": 2408,
                            "available_n": 2300,
                            "missing_n": 108,
                            "summary_denominator_n": 2300,
                            "source_ref": "table:source-validation",
                        },
                    ],
                    "smd_values": [
                        {"surface": "source", "value": 0.07, "source_ref": "metric:smd"},
                        {"surface": "table1", "value": 0.22, "source_ref": "table:T1"},
                        {"surface": "manuscript", "value": 0.22, "source_ref": "text:results"},
                    ],
                }
            ],
            "authority": False,
        }
    )
    assert "BASELINE_SMD_CROSS_SURFACE_CONFLICT" in {
        item["code"] for item in physical_activity_conflict["findings"]
    }
    valid_baseline_trace = validate_baseline_table_traceability(
        {
            "rows": [
                {
                    "variable_key": "age",
                    "unit": "years",
                    "denominator_ref": "denominator:available-age",
                    "source_metric_ref": "metric:age",
                    "smd_source_ref": "metric:age-smd",
                    "groups": [
                        {
                            "group_id": "development",
                            "group_n": 5000,
                            "available_n": 4990,
                            "missing_n": 10,
                            "summary_denominator_n": 4990,
                            "source_ref": "table:source-development",
                        },
                        {
                            "group_id": "validation",
                            "group_n": 2408,
                            "available_n": 2400,
                            "missing_n": 8,
                            "summary_denominator_n": 2400,
                            "source_ref": "table:source-validation",
                        },
                    ],
                    "smd_values": [
                        {"surface": "source", "value": 0.101, "source_ref": "metric:smd"},
                        {"surface": "table1", "value": 0.10, "source_ref": "table:T1"},
                        {"surface": "manuscript", "value": 0.10, "source_ref": "text:results"},
                    ],
                }
            ],
            "authority": False,
        }
    )
    assert valid_baseline_trace["machine_check_status"] == "candidate_complete"
    print(json.dumps({"ok": True, "checks": 13}, indent=2, sort_keys=True))
