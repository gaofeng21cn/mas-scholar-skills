"""Loader helper for dynamically importing skills/<skill-id>/kernel.py modules in tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
_CACHE: dict[str, ModuleType] = {}


def load_kernel(skill_id: str) -> ModuleType:
    """Import and cache skills/<skill_id>/kernel.py as an importable Python module."""
    if skill_id in _CACHE:
        return _CACHE[skill_id]
    kernel_path = ROOT / "skills" / skill_id / "kernel.py"
    module_name = f"mas_scholar_skill_kernel_{skill_id.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, kernel_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load kernel module for {skill_id}: {kernel_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    _CACHE[skill_id] = module
    return module


def kernel_file(skill_id: str) -> Path:
    """Return the canonical path to skills/<skill_id>/kernel.py."""
    return ROOT / "skills" / skill_id / "kernel.py"
