"""Deterministic refs-only helpers for cohort phenotyping.

These helpers normalize criteria text and scaffold attrition tables. They do
not define final cohort truth, mutate data, sign receipts, or claim readiness.
"""

from __future__ import annotations

import json
import re
from typing import Iterable


def normalize_criterion(text: object, *, default_kind: str = "inclusion") -> dict[str, str]:
    """Normalize one inclusion/exclusion criterion for refs-only review."""
    raw = str(text or "").strip()
    lowered = raw.lower()
    kind = default_kind
    if lowered.startswith(("exclude ", "exclusion:", "without ")):
        kind = "exclusion"
    elif lowered.startswith(("include ", "inclusion:", "with ")):
        kind = "inclusion"
    normalized = re.sub(r"^(?:include|exclude|inclusion:|exclusion:)\s*", "", raw, flags=re.I)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return {"kind": kind, "criterion": normalized, "support_ref": "", "owner_gate_handoff_ref": ""}


def criteria_table_skeleton(
    inclusions: Iterable[object] = (),
    exclusions: Iterable[object] = (),
) -> list[dict[str, str]]:
    """Return normalized inclusion/exclusion rows."""
    rows = [normalize_criterion(item, default_kind="inclusion") for item in inclusions]
    rows.extend(normalize_criterion(item, default_kind="exclusion") for item in exclusions)
    return rows


def cohort_attrition_table_skeleton(stages: Iterable[str]) -> list[dict[str, object]]:
    """Create a cohort attrition table shell."""
    return [
        {
            "stage": stage,
            "n_remaining": None,
            "n_excluded": None,
            "exclusion_reason": "",
            "cohort_definition_ref": "",
            "validation_check_ref": "",
        }
        for stage in stages
    ]


def phenotype_handoff_skeleton() -> dict[str, object]:
    """Return the standard refs-only phenotype handoff shell."""
    return {
        "phenotype_question_ref": "",
        "cohort_definition_ref": "",
        "index_and_window_ref": "",
        "phenotype_logic_ref": "",
        "code_list_or_variable_ref": "",
        "ascertainment_support_map_ref": "",
        "denominator_missingness_ref": "",
        "validation_check_ref": "",
        "sensitivity_candidate_ref": "",
        "candidate_package_ref": "",
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def _self_check() -> None:
    assert normalize_criterion("Exclude prior cancer")["kind"] == "exclusion"
    assert normalize_criterion("Inclusion: adults")["criterion"] == "adults"
    assert len(criteria_table_skeleton(["age >= 18"], ["missing index date"])) == 2
    assert cohort_attrition_table_skeleton(["source"])[0]["n_remaining"] is None
    assert "phenotype_logic_ref" in phenotype_handoff_skeleton()
    print(json.dumps({"ok": True, "checks": 5}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
