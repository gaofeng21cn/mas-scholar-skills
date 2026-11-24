#!/usr/bin/env python3
"""Thin CLI entrypoint delegating repository consistency checks to pytest."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    exit_code = pytest.main(["-q", str(ROOT / "tests" / "consistency")])
    if exit_code != 0:
        return int(exit_code)
    print(
        "verify ok: mas-scholar-skills plugin, contract, medical skill sources, "
        "gallery package, and no-authority boundaries are valid"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
