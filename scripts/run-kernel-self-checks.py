#!/usr/bin/env python3
"""Run every skill kernel pytest suite in one Python process."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    kernels = sorted((ROOT / "skills").glob("*/kernel.py"))
    exit_code = pytest.main(["-q", str(ROOT / "tests" / "kernels")])
    if exit_code != 0:
        return int(exit_code)
    print(json.dumps({"ok": True, "kernel_self_checks": len(kernels)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
