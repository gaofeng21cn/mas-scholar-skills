"""Deterministic refs-only helpers for medical indication dossiers.

These helpers organize waypoint refs only. They do not write clinical strategy
truth, owner receipts, typed blockers, market verdicts, or publication claims.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


WAYPOINTS = (
    "population_definition_ref",
    "epidemiology_waypoint_ref",
    "biology_soc_waypoint_ref",
    "regulatory_trials_waypoint_ref",
    "patient_population_waypoint_ref",
    "synthesis_candidate_ref",
)
AUTHORITY_RE = re.compile(
    r"\b(clinical\s+recommendation|market\s+verdict|owner\s+(accepted|receipt)|typed\s+blocker|publication\s+ready)\b",
    re.I,
)


def dossier_handoff_skeleton(indication_question: str = "") -> dict[str, Any]:
    """Return the refs-only indication dossier handoff shell."""

    return {
        "indication_question": indication_question,
        "population_definition_ref": "",
        "epidemiology_waypoint_ref": "",
        "biology_soc_waypoint_ref": "",
        "regulatory_trials_waypoint_ref": "",
        "patient_population_waypoint_ref": "",
        "synthesis_candidate_ref": "",
        "source_manifest_ref": "",
        "environment_receipt_ref": "",
        "candidate_refs": [],
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def waypoint_matrix_skeleton(waypoints: Sequence[str] | None = None) -> list[dict[str, str]]:
    """Create waypoint rows without filling evidence or decisions."""

    return [
        {
            "waypoint_ref": waypoint,
            "source_refs": "",
            "summary_ref": "",
            "limitations_ref": "",
            "route_back_candidate": "",
        }
        for waypoint in (waypoints or WAYPOINTS)
    ]


def summarize_source_manifest(sources: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Return deterministic source counts for dossier coverage review."""

    source_types = [str(source.get("source_type") or "unspecified").strip().lower() for source in sources]
    missing_ids = [
        str(index)
        for index, source in enumerate(sources, start=1)
        if not (source.get("source_ref") or source.get("url") or source.get("identifier"))
    ]
    return {
        "n_sources": len(sources),
        "source_type_counts": dict(sorted(Counter(source_types).items())),
        "missing_identifier_records": missing_ids,
        "authority": False,
    }


def lint_forbidden_authority_claims(text: str) -> list[dict[str, str]]:
    """Flag claims a dossier helper must route back."""

    return [{"code": "FORBIDDEN_AUTHORITY_CLAIM", "note": match.group(0)} for match in AUTHORITY_RE.finditer(text or "")]


if __name__ == "__main__":
    import sys
    from pathlib import Path
    _root = str(Path(__file__).resolve().parents[2])
    if _root not in sys.path:
        sys.path.insert(0, _root)
    from runtime.kernel_validation import delegate_self_check
    raise SystemExit(delegate_self_check("medical-indication-dossier", kernel_file=__file__))
