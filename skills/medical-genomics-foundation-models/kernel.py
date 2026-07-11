"""Deterministic refs-only helpers for genomics foundation-model tasks.

These helpers normalize genomic refs and candidate shells only. They do not
run models, mutate clinical data, write source readiness, or claim authority.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


INTERVAL_RE = re.compile(r"^(chr)?(?P<chrom>[0-9XYM]+):(?P<start>[0-9,]+)-(?P<end>[0-9,]+)$", re.I)
AUTHORITY_RE = re.compile(
    r"\b(clinical\s+interpretation|source\s+ready|owner\s+(accepted|receipt)|typed\s+blocker|publication\s+ready)\b",
    re.I,
)


def normalize_interval(interval: str, *, genome_build: str = "") -> dict[str, Any]:
    """Normalize chr:start-end strings for refs-only model handoff."""

    match = INTERVAL_RE.match((interval or "").replace(" ", ""))
    if not match:
        raise ValueError("interval must look like chr1:100-200")
    start = int(match.group("start").replace(",", ""))
    end = int(match.group("end").replace(",", ""))
    if start > end:
        start, end = end, start
    chrom = match.group("chrom").upper()
    return {"chrom": f"chr{chrom}", "start": start, "end": end, "genome_build": genome_build}


def genomics_handoff_skeleton(genomics_question: str = "") -> dict[str, Any]:
    """Return the standard refs-only genomics handoff shell."""

    return {
        "genomics_question": genomics_question,
        "genomic_interval_ref": "",
        "reference_genome_ref": "",
        "variant_or_sequence_ref": "",
        "dna_scoring_candidate_ref": "",
        "track_prediction_candidate_ref": "",
        "model_checkpoint_ref": "",
        "environment_receipt_ref": "",
        "limitations_ref": "",
        "candidate_refs": [],
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def variant_candidate_ref_skeleton(
    variant_id: str = "", *, interval_ref: str = "", reference_genome_ref: str = ""
) -> dict[str, Any]:
    """Return a refs-only variant candidate shell."""

    return {
        "variant_id": variant_id,
        "genomic_interval_ref": interval_ref,
        "reference_genome_ref": reference_genome_ref,
        "dna_scoring_candidate_ref": "",
        "track_prediction_candidate_ref": "",
        "model_checkpoint_ref": "",
        "authority": False,
    }


def lint_genomic_ref_records(records: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Flag missing genome-build or authority drift in candidate records."""

    findings: list[dict[str, str]] = []
    for index, record in enumerate(records, start=1):
        if not (record.get("genome_build") or record.get("reference_genome_ref")):
            findings.append({"code": "MISSING_REFERENCE_GENOME", "record": str(index)})
        text = " ".join(str(value) for value in record.values())
        if AUTHORITY_RE.search(text):
            findings.append({"code": "FORBIDDEN_AUTHORITY_CLAIM", "record": str(index)})
    return findings


def _self_check() -> None:
    assert normalize_interval("1:200-100", genome_build="hg38") == {
        "chrom": "chr1",
        "start": 100,
        "end": 200,
        "genome_build": "hg38",
    }
    assert genomics_handoff_skeleton("score")["model_checkpoint_ref"] == ""
    assert variant_candidate_ref_skeleton("rs1")["authority"] is False
    findings = lint_genomic_ref_records([{"variant": "rs1"}, {"genome_build": "hg38", "note": "source ready"}])
    assert [item["code"] for item in findings] == ["MISSING_REFERENCE_GENOME", "FORBIDDEN_AUTHORITY_CLAIM"]
    print(json.dumps({"ok": True, "checks": 4}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
