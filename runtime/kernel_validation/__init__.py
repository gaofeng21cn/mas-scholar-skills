"""Shared declarative Pydantic v2 and JSON Schema validation helpers for ScholarSkills kernels."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Annotated, Any, TypeVar

from jsonschema import Draft202012Validator
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    TypeAdapter,
    ValidationError,
)

SHA256_DIGEST_PATTERN = r"^sha256:[0-9a-f]{64}$"

TModel = TypeVar("TModel", bound="StrictKernelModel")


def _check_non_empty_str(value: str) -> str:
    if not value.strip():
        raise ValueError("must be a non-empty string")
    return value


def _strip_non_empty_str(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("must be a string")
    stripped = value.strip()
    if not stripped:
        raise ValueError("must be a non-empty string")
    return stripped


def _normalize_sha256_digest(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("must be a SHA-256 digest string")
    return value.strip().lower()


def _normalize_optional_prefix_sha256(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("must be a SHA-256 digest string")
    text = value.strip().lower()
    raw = text.removeprefix("sha256:")
    return f"sha256:{raw}"


def _check_finite_number(value: int | float) -> float:
    if isinstance(value, bool):
        raise ValueError("must be a finite number, not bool")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("must be a finite number")
    return number


NonEmptyStr = Annotated[StrictStr, AfterValidator(_check_non_empty_str)]
StrippedNonEmptyStr = Annotated[str, BeforeValidator(_strip_non_empty_str)]
Sha256Digest = Annotated[StrictStr, Field(pattern=SHA256_DIGEST_PATTERN)]
NormalizedSha256Digest = Annotated[
    str,
    BeforeValidator(_normalize_sha256_digest),
    Field(pattern=SHA256_DIGEST_PATTERN),
]
FlexibleSha256Digest = Annotated[
    str,
    BeforeValidator(_normalize_optional_prefix_sha256),
    Field(pattern=SHA256_DIGEST_PATTERN),
]
StrictPositiveInt = Annotated[StrictInt, Field(ge=1)]
StrictNonNegativeInt = Annotated[StrictInt, Field(ge=0)]
FiniteNumber = Annotated[StrictInt | StrictFloat, AfterValidator(_check_finite_number)]
PositiveFiniteNumber = Annotated[FiniteNumber, Field(gt=0.0)]
NonNegativeFiniteNumber = Annotated[FiniteNumber, Field(ge=0.0)]
UnitIntervalFloat = Annotated[FiniteNumber, Field(ge=0.0, le=1.0)]
NonEmptyStrTuple = Annotated[tuple[NonEmptyStr, ...], Field(min_length=1)]


class StrictKernelModel(BaseModel):
    """Base Pydantic v2 model with strict typing and forbidden extra keys."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class OpenKernelModel(BaseModel):
    """Strict-typed Pydantic v2 model that allows extra keys when partial checks are required."""

    model_config = ConfigDict(extra="allow", strict=True, frozen=True)


class ExactRefModel(StrictKernelModel):
    """Canonical four-field exact file/artifact reference (strict lowercase sha256)."""

    kind: NonEmptyStr
    ref: NonEmptyStr
    size_bytes: StrictPositiveInt
    sha256: Sha256Digest


class NormalizedExactRefModel(StrictKernelModel):
    """Four-field exact ref normalizing whitespace and hex case on kind/ref/sha256."""

    kind: StrippedNonEmptyStr
    ref: StrippedNonEmptyStr
    size_bytes: StrictPositiveInt
    sha256: NormalizedSha256Digest


class NonNegativeExactRefModel(StrictKernelModel):
    """Four-field exact ref allowing zero-byte size and optional sha256: prefix."""

    kind: StrippedNonEmptyStr
    ref: StrippedNonEmptyStr
    size_bytes: StrictNonNegativeInt
    sha256: FlexibleSha256Digest


class DispositionModel(StrictKernelModel):
    """Canonical three-field unavailable/not-applicable disposition record."""

    status: NonEmptyStr
    ref: None
    reason: NonEmptyStr


_EXACT_REF_ADAPTER = TypeAdapter(ExactRefModel)
_NORMALIZED_EXACT_REF_ADAPTER = TypeAdapter(NormalizedExactRefModel)
_NON_NEGATIVE_EXACT_REF_ADAPTER = TypeAdapter(NonNegativeExactRefModel)
_DISPOSITION_ADAPTER = TypeAdapter(DispositionModel)
_SHA256_ADAPTER = TypeAdapter(Sha256Digest)
_FLEXIBLE_SHA256_ADAPTER = TypeAdapter(FlexibleSha256Digest)
_FINITE_NUMBER_ADAPTER = TypeAdapter(FiniteNumber)
_FINITE_NUMBER_SEQ_ADAPTER = TypeAdapter(list[FiniteNumber])
_NON_EMPTY_STR_ADAPTER = TypeAdapter(NonEmptyStr)
_NON_EMPTY_STR_LIST_ADAPTER = TypeAdapter(list[NonEmptyStr])


def is_exact_ref(
    value: object,
    *,
    expected_kinds: Iterable[str] | None = None,
    normalize_case: bool = False,
) -> bool:
    """Return True if value matches the strict ExactRefModel contract."""
    parsed = parse_exact_ref(
        value, expected_kinds=expected_kinds, normalize_case=normalize_case
    )
    return parsed is not None


def parse_exact_ref(
    value: object,
    *,
    expected_kinds: Iterable[str] | None = None,
    normalize_case: bool = False,
) -> ExactRefModel | NormalizedExactRefModel | None:
    """Validate and return an exact-ref model, or None on schema violation."""
    if not isinstance(value, Mapping):
        return None
    adapter = _NORMALIZED_EXACT_REF_ADAPTER if normalize_case else _EXACT_REF_ADAPTER
    try:
        parsed = adapter.validate_python(dict(value))
    except ValidationError:
        return None
    if expected_kinds is not None and parsed.kind not in set(expected_kinds):
        return None
    return parsed


def parse_non_negative_exact_ref(value: object) -> NonNegativeExactRefModel:
    """Validate a non-negative exact-ref mapping, raising ValidationError on failure."""
    if not isinstance(value, Mapping):
        raise ValueError("must be an exact-ref mapping")
    return _NON_NEGATIVE_EXACT_REF_ADAPTER.validate_python(dict(value))


def parse_disposition(
    value: object,
    *,
    allowed_statuses: Iterable[str] | None = None,
) -> DispositionModel | None:
    """Validate a typed disposition record (status, ref=None, non-empty reason)."""
    if not isinstance(value, Mapping):
        return None
    try:
        parsed = _DISPOSITION_ADAPTER.validate_python(dict(value))
    except ValidationError:
        return None
    if allowed_statuses is not None and parsed.status not in set(allowed_statuses):
        return None
    return parsed


def is_exact_ref_or_disposition(
    value: object,
    *,
    allowed_dispositions: Sequence[str],
    require_disposition: bool = False,
    normalize_case: bool = True,
) -> bool:
    """Validate either a canonical exact ref or an allowed typed disposition."""
    if parse_exact_ref(value, normalize_case=normalize_case) is not None:
        return not require_disposition
    return parse_disposition(value, allowed_statuses=allowed_dispositions) is not None


def is_sha256_digest(value: object) -> bool:
    """Return True when value is a canonical sha256:<64-hex> digest string."""
    try:
        _SHA256_ADAPTER.validate_python(value)
    except ValidationError:
        return False
    return True


def normalize_sha256_digest(value: object, label: str = "sha256") -> str:
    """Normalize a 64-hex or sha256:<64-hex> digest via Pydantic, raising ValueError if invalid."""
    try:
        return _FLEXIBLE_SHA256_ADAPTER.validate_python(value)
    except ValidationError as exc:
        raise ValueError(f"{label} must be a SHA-256 digest") from exc


def is_non_empty_str(value: object) -> bool:
    """Return True when value is a non-whitespace string."""
    try:
        _NON_EMPTY_STR_ADAPTER.validate_python(value)
    except ValidationError:
        return False
    return True


def parse_finite_number(value: object) -> float | None:
    """Return finite float for strict int/float (excluding bool), or None."""
    try:
        return _FINITE_NUMBER_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def parse_number_sequence(value: object, expected_length: int) -> list[float] | None:
    """Validate a strict finite number sequence of exact length, returning None on failure."""
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return None
    if len(value) != expected_length:
        return None
    try:
        return _FINITE_NUMBER_SEQ_ADAPTER.validate_python(list(value))
    except ValidationError:
        return None


def parse_non_empty_str_list(value: object) -> list[str] | None:
    """Validate a strict list of non-empty strings, returning None on failure."""
    if not isinstance(value, list):
        return None
    try:
        return _NON_EMPTY_STR_LIST_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def validate_strict_model(
    model_cls: type[TModel],
    payload: object,
) -> tuple[TModel | None, list[dict[str, Any]]]:
    """Validate payload against a StrictKernelModel and return (model, error_dicts)."""
    if not isinstance(payload, Mapping):
        return None, [{"loc": (), "msg": "Input must be a mapping", "type": "dict_type"}]
    try:
        return model_cls.model_validate(dict(payload)), []
    except ValidationError as exc:
        return None, [dict(err) for err in exc.errors()]


def validate_against_schema(
    schema: Mapping[str, Any],
    payload: object,
) -> list[str]:
    """Validate payload with jsonschema Draft202012Validator and return sorted error strings."""
    validator = Draft202012Validator(dict(schema))
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda err: (tuple(str(part) for part in err.absolute_path), err.message),
    )
    return [
        f"{'/'.join(str(part) for part in err.absolute_path) or '<root>'}: {err.message}"
        for err in errors
    ]


def ensure_repo_root(kernel_file: str | Path) -> Path:
    """Ensure the repository root (two levels above skills/<id>/kernel.py) is on sys.path."""
    root = Path(kernel_file).resolve().parents[2]
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return root


def delegate_self_check(
    skill_id: str,
    *,
    kernel_file: str | Path,
    extra_args: Sequence[str] = (),
) -> int:
    """Thin CLI delegate running the extracted pytest suite for a skill kernel."""
    root = Path(kernel_file).resolve().parents[2]
    slug = skill_id.replace("-", "_")
    dedicated = root / "tests" / "kernels" / f"test_{slug}.py"
    remaining = root / "tests" / "kernels" / "test_remaining_skill_kernels.py"
    if dedicated.is_file():
        target = [str(dedicated)]
    elif remaining.is_file():
        target = [str(remaining), "-k", f"test_{slug}"]
    else:
        print(
            json.dumps(
                {
                    "ok": False,
                    "skill_id": skill_id,
                    "reason": "extracted pytest suite not present in this checkout",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1
    cmd = [sys.executable, "-m", "pytest", "-q", *target, *extra_args]
    return subprocess.run(cmd, cwd=root, check=False).returncode


__all__ = [
    "DispositionModel",
    "ExactRefModel",
    "FiniteNumber",
    "FlexibleSha256Digest",
    "NonEmptyStr",
    "NonEmptyStrTuple",
    "NonNegativeExactRefModel",
    "NonNegativeFiniteNumber",
    "NormalizedExactRefModel",
    "NormalizedSha256Digest",
    "OpenKernelModel",
    "PositiveFiniteNumber",
    "SHA256_DIGEST_PATTERN",
    "Sha256Digest",
    "StrictBool",
    "StrictFloat",
    "StrictInt",
    "StrictKernelModel",
    "StrictNonNegativeInt",
    "StrictPositiveInt",
    "StrictStr",
    "StrippedNonEmptyStr",
    "TypeAdapter",
    "UnitIntervalFloat",
    "ValidationError",
    "delegate_self_check",
    "ensure_repo_root",
    "is_exact_ref",
    "is_exact_ref_or_disposition",
    "is_non_empty_str",
    "is_sha256_digest",
    "normalize_sha256_digest",
    "parse_disposition",
    "parse_exact_ref",
    "parse_finite_number",
    "parse_non_empty_str_list",
    "parse_non_negative_exact_ref",
    "parse_number_sequence",
    "validate_against_schema",
    "validate_strict_model",
]
