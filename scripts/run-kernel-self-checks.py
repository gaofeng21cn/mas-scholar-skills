#!/usr/bin/env python3
"""Run every skill kernel self-check in one isolated Python process."""

from __future__ import annotations

import json
import os
import random
import runpy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_kernel(path: Path) -> None:
    cwd = Path.cwd()
    environ = os.environ.copy()
    sys_path = list(sys.path)
    modules = set(sys.modules)
    random_state = random.getstate()
    try:
        runpy.run_path(str(path), run_name="__main__")
    except SystemExit as exc:
        if exc.code not in (None, 0):
            raise RuntimeError(f"{path.relative_to(ROOT)} exited with {exc.code}") from exc
    finally:
        os.chdir(cwd)
        os.environ.clear()
        os.environ.update(environ)
        sys.path[:] = sys_path
        random.setstate(random_state)
        for name in set(sys.modules) - modules:
            sys.modules.pop(name, None)


def main() -> int:
    kernels = sorted((ROOT / "skills").glob("*/kernel.py"))
    for kernel in kernels:
        run_kernel(kernel)
    print(json.dumps({"ok": True, "kernel_self_checks": len(kernels)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
