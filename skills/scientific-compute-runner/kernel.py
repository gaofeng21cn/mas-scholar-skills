"""Deterministic refs-only helpers for scientific compute runner.

No credentials, network calls, provider lifecycle, remote execution, runtime
attempts, MAS truth, owner receipts, or typed blockers live here.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


AUTHORITY_PATTERNS = (
    ("RUNTIME_READINESS_CLAIM", r"\b(runtime|production|endpoint)\s+ready\b"),
    ("OWNER_AUTHORITY_CLAIM", r"\b(owner\s+(accepted|approved|receipt)|signed\s+receipt)\b"),
    ("TYPED_BLOCKER_CLAIM", r"\btyped\s+blocker\b"),
    ("DOMAIN_TRUTH_CLAIM", r"\b(domain|study|clinical)\s+truth\b"),
    ("PUBLICATION_READINESS_CLAIM", r"\bpublication\s+ready\b"),
)
SECRET_PATTERN = re.compile(r"\b(api[_-]?key|token|secret|password)\s*[:=]\s*\S+", re.I)


def normalize_env_spec(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Return a stable environment spec without provider execution semantics."""

    packages = _sorted_strings(spec.get("packages") or spec.get("dependencies") or [])
    env_vars = _sorted_strings(spec.get("env_vars") or spec.get("environment_variables") or [])
    commands = [str(item).strip() for item in _as_list(spec.get("commands")) if str(item).strip()]
    hardware = spec.get("hardware") if isinstance(spec.get("hardware"), Mapping) else {}
    return {
        "python_version": str(spec.get("python_version") or spec.get("python") or "").strip(),
        "packages": packages,
        "env_vars": [name.split("=", 1)[0].strip() for name in env_vars],
        "hardware": {str(key): hardware[key] for key in sorted(hardware)},
        "container_ref": str(spec.get("container_ref") or spec.get("container") or "").strip(),
        "commands": commands,
        "limitations_ref": str(spec.get("limitations_ref") or "").strip(),
    }


def provider_intent_envelope(
    compute_question: str,
    provider_route: str,
    *,
    command_ref: str = "",
    input_refs: Sequence[str] | None = None,
    expected_output_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Create a refs-only provider intent envelope for Runway/Connect/Fabric."""

    return {
        "compute_question": compute_question,
        "provider_route": provider_route,
        "provider_intent_ref": "",
        "command_ref": command_ref,
        "input_refs": list(input_refs or []),
        "expected_output_refs": list(expected_output_refs or []),
        "substrate_owner": "OPL Runway/Connect/Fabric or consuming compute owner",
        "authority": False,
        "owner_gate_handoff_ref": "",
    }


def compute_handoff_skeleton(compute_question: str = "") -> dict[str, Any]:
    """Return the standard refs-only compute runner handoff shell."""

    return {
        "compute_question": compute_question,
        "compute_requirement_ref": "",
        "provider_selection_ref": "",
        "environment_probe_ref": "",
        "job_plan_ref": "",
        "endpoint_request_ref": "",
        "deterministic_receipt_ref": "",
        "candidate_package_ref": "",
        "execution_receipt_ref": "",
        "output_manifest_ref": "",
        "failure_classification_ref": "",
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def summarize_compute_log(log_text: str, *, tail_lines: int = 12) -> dict[str, Any]:
    """Summarize local log text without classifying provider attempts."""

    text = SECRET_PATTERN.sub(r"\1=<redacted>", log_text or "")
    lines = text.splitlines()
    joined = "\n".join(lines)
    exit_match = re.search(r"\bexit(?:\s+code)?\s*[:=]\s*(-?\d+)\b", joined, re.I)
    patterns = {
        "errors": r"\b(error|exception|traceback|failed|fatal)\b",
        "warnings": r"\b(warning|warn)\b",
        "oom_signals": r"\b(out of memory|oom|killed)\b",
        "credential_signals": r"\b(permission denied|unauthorized|forbidden|credential)\b",
    }
    return {
        "exit_code": int(exit_match.group(1)) if exit_match else None,
        "n_lines": len(lines),
        "signals": {key: len(re.findall(pattern, joined, re.I)) for key, pattern in patterns.items()},
        "tail": lines[-tail_lines:],
    }


def helper_receipt_skeleton(
    command_ref: str,
    *,
    input_refs: Sequence[str] | None = None,
    output_manifest_ref: str = "",
    exit_code: int | None = None,
) -> dict[str, Any]:
    """Return an unsigned deterministic helper receipt skeleton."""

    return {
        "receipt_kind": "scientific_compute_helper_receipt_ref",
        "authority": False,
        "command_ref": command_ref,
        "input_refs": list(input_refs or []),
        "output_manifest_ref": output_manifest_ref,
        "exit_code": exit_code,
        "sha256_ref": "",
        "limitations_ref": "",
        "owner_gate_handoff_ref": "",
    }


def lint_forbidden_authority_claims(text: str) -> list[dict[str, str]]:
    """Flag claims this skill must route back instead of asserting."""

    findings = [
        {"code": code, "note": "forbidden authority claim"}
        for code, pattern in AUTHORITY_PATTERNS
        if re.search(pattern, text or "", re.I)
    ]
    if SECRET_PATTERN.search(text or ""):
        findings.append({"code": "SECRET_LIKE_VALUE", "note": "credential-like value must be redacted"})
    return findings


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value) if isinstance(value, Sequence) else [value]


def _sorted_strings(value: Any) -> list[str]:
    return sorted({str(item).strip() for item in _as_list(value) if str(item).strip()})


def _self_check() -> None:
    spec = normalize_env_spec(
        {"python": "3.11", "dependencies": ["numpy", " scipy ", "numpy"], "env_vars": ["TOKEN=x"], "hardware": {"gpu": 1}}
    )
    assert spec["packages"] == ["numpy", "scipy"]
    assert spec["env_vars"] == ["TOKEN"]
    assert provider_intent_envelope("fit model", "modal")["authority"] is False
    assert compute_handoff_skeleton("fit")["execution_receipt_ref"] == ""
    summary = summarize_compute_log("warning\napi_key=abc\nERROR exit code: 137")
    assert summary["exit_code"] == 137
    assert summary["signals"]["errors"] == 1
    assert lint_forbidden_authority_claims("runtime ready with owner receipt")
    assert helper_receipt_skeleton("cmd")["receipt_kind"] == "scientific_compute_helper_receipt_ref"
    print(json.dumps({"ok": True, "checks": 7}, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_check()
