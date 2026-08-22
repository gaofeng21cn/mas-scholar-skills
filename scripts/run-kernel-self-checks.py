#!/usr/bin/env python3
"""Run every skill kernel self-check in one Python process."""

from __future__ import annotations

import json
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_kernel(path: Path) -> None:
    try:
        runpy.run_path(str(path), run_name="__main__")
    except SystemExit as exc:
        if exc.code not in (None, 0):
            raise RuntimeError(f"{path.relative_to(ROOT)} exited with {exc.code}") from exc


def main() -> int:
    kernels = sorted((ROOT / "skills").glob("*/kernel.py"))
    for kernel in kernels:
        run_kernel(kernel)
    print(json.dumps({"ok": True, "kernel_self_checks": len(kernels)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
