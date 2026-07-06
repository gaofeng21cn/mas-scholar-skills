"""Deterministic refs-only helpers for medical single-cell modeling.

These helpers inspect metadata shape and key hygiene. They do not depend on
anndata or scvi, run models, mutate data truth, or claim publication readiness.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


RESERVED_KEYS = {"obs", "var", "x", "raw", "layers", "uns", "obsm", "varm"}


def sanitize_key(key: Any) -> str:
    """Return a stable AnnData-friendly metadata key."""

    cleaned = re.sub(r"[^0-9A-Za-z_]+", "_", str(key).strip()).strip("_").lower()
    if not cleaned:
        cleaned = "field"
    if cleaned[0].isdigit():
        cleaned = f"k_{cleaned}"
    if cleaned in RESERVED_KEYS:
        cleaned = f"{cleaned}_key"
    return cleaned


def sanitize_anndata_keys(keys: Sequence[Any] | Mapping[Any, Any]) -> dict[str, str]:
    """Return original-to-sanitized key mapping with deterministic suffixes."""

    source_keys = list(keys.keys()) if isinstance(keys, Mapping) else list(keys)
    used: dict[str, int] = {}
    mapping: dict[str, str] = {}
    for original in source_keys:
        base = sanitize_key(original)
        count = used.get(base, 0)
        used[base] = count + 1
        mapping[str(original)] = base if count == 0 else f"{base}_{count + 1}"
    return mapping


def h5ad_safe_obs(df: Any) -> Any:
    """Return a copied obs/var dataframe safe for AnnData H5AD string writing.

    The helper imports pandas/numpy lazily, never writes files, and never mutates
    the input dataframe. Callers must assign or pass the returned copy explicitly.
    """

    import numpy as np
    import pandas as pd

    out = df.copy()
    out.index = pd.Index(
        np.asarray(out.index, dtype=object).astype(str), name=out.index.name
    )
    for column in out.columns:
        dtype = str(out[column].dtype)
        if dtype in {"object", "str"} or "string" in dtype:
            mask = out[column].notna()
            values = np.asarray(
                out[column].astype(object).where(mask, None), dtype=object
            ).copy()
            values[mask.to_numpy()] = np.asarray(
                out[column][mask].astype(str), dtype=object
            )
            out[column] = pd.Categorical(values)
    return out


def safe_obs_summary(obs: Any, max_values: int = 8) -> dict[str, Any]:
    """Summarize dict or dataframe-like obs without importing pandas."""

    columns = _column_names(obs)
    row_count = _row_count(obs, columns)
    return {
        "n_obs": row_count,
        "columns": [
            {
                "key": key,
                "sanitized_key": sanitize_key(key),
                "non_null_count": sum(value is not None for value in _values(obs, key)),
                "example_values": _unique_examples(_values(obs, key), max_values),
            }
            for key in columns
        ],
    }


def metadata_schema_skeleton(obs_keys: Sequence[str] | None = None) -> dict[str, Any]:
    """Return the refs-only metadata schema shape expected before modeling."""

    return {
        "anndata_input_ref": "",
        "metadata_schema_ref": {
            "obs_keys": [
                {
                    "key": key,
                    "sanitized_key": sanitize_key(key),
                    "role": "",
                    "provenance_ref": "",
                    "allowed_missingness": "",
                }
                for key in (obs_keys or [])
            ],
            "var_keys": [],
            "batch_key_ref": "",
            "label_key_ref": "",
        },
        "route_back_candidate": "",
        "owner_gate_handoff_ref": "",
    }


def batch_label_key_diagnostics(
    obs: Any, batch_key: str, label_key: str | None = None
) -> dict[str, Any]:
    """Return batch and label key diagnostics from dict/dataframe-like obs."""

    columns = set(_column_names(obs))
    diagnostics = {
        "batch_key": batch_key,
        "label_key": label_key or "",
        "missing_keys": [],
        "warnings": [],
        "batch_levels": _unique_examples(_values(obs, batch_key), 20) if batch_key in columns else [],
        "label_levels": _unique_examples(_values(obs, label_key), 20)
        if label_key and label_key in columns
        else [],
    }
    if batch_key not in columns:
        diagnostics["missing_keys"].append(batch_key)
    elif len(diagnostics["batch_levels"]) < 2:
        diagnostics["warnings"].append("batch_key_has_fewer_than_two_levels")
    if label_key and label_key not in columns:
        diagnostics["missing_keys"].append(label_key)
    elif label_key and len(diagnostics["label_levels"]) < 2:
        diagnostics["warnings"].append("label_key_has_fewer_than_two_levels")
    return diagnostics


def _column_names(obj: Any) -> list[str]:
    if isinstance(obj, Mapping):
        return [str(key) for key in obj.keys()]
    columns = getattr(obj, "columns", None)
    if columns is not None:
        return [str(key) for key in list(columns)]
    return []


def _row_count(obj: Any, columns: list[str]) -> int:
    shape = getattr(obj, "shape", None)
    if shape:
        return int(shape[0])
    if not columns:
        return 0
    return len(_values(obj, columns[0]))


def _values(obj: Any, key: str | None) -> list[Any]:
    if not key:
        return []
    if isinstance(obj, Mapping):
        value = obj.get(key, [])
    else:
        try:
            value = obj[key]
        except Exception:
            return []
    if isinstance(value, str) or not isinstance(value, Sequence):
        to_list = getattr(value, "tolist", None)
        if callable(to_list):
            value = to_list()
        else:
            value = [value]
    return list(value)


def _unique_examples(values: list[Any], limit: int) -> list[str]:
    seen: list[str] = []
    for value in values:
        if value is None:
            continue
        text = str(value)
        if text not in seen:
            seen.append(text)
        if len(seen) >= limit:
            break
    return seen


def _self_check() -> None:
    obs = {"Batch ID": ["a", "b", "b"], "cell type": ["T", "B", "T"], "X": [1, 2, 3]}
    assert sanitize_key("Batch ID") == "batch_id"
    assert sanitize_key("X") == "x_key"
    assert sanitize_anndata_keys(["a b", "a-b"]) == {"a b": "a_b", "a-b": "a_b_2"}
    assert safe_obs_summary(obs)["n_obs"] == 3
    assert batch_label_key_diagnostics(obs, "Batch ID", "cell type")["missing_keys"] == []
    optional = _self_check_h5ad_safe_obs()
    print(json.dumps({"ok": True, "checks": 6, "h5ad_safe_obs": optional}, indent=2, sort_keys=True))


def _self_check_h5ad_safe_obs() -> dict[str, Any]:
    assert callable(h5ad_safe_obs)
    try:
        import pandas as pd
    except ImportError as exc:
        return {"status": "skipped", "reason": str(exc)}
    obs = pd.DataFrame(
        {
            "label": ["T", None, "B"],
            "sample": pd.array(["s1", pd.NA, "s2"], dtype="string"),
            "count": [1, 2, 3],
        },
        index=pd.Index([101, "cell-2", 303], name="cell_id"),
    )
    out = h5ad_safe_obs(obs)
    assert out is not obs
    assert list(out.index) == ["101", "cell-2", "303"]
    assert str(out["label"].dtype) == "category"
    assert str(out["sample"].dtype) == "category"
    assert str(out["count"].dtype) == "int64"
    assert out["label"].isna().tolist() == [False, True, False]
    assert out["sample"].isna().tolist() == [False, True, False]
    return {"status": "checked"}


if __name__ == "__main__":
    _self_check()
