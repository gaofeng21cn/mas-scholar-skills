#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "contracts" / "opl_capability_package_manifest.json"
CANONICAL_CONTENT_LOCK = "ordered_path_length_file_length_bytes"


def content_digest(manifest: dict[str, object]) -> str:
    content_lock = manifest.get("content_lock")
    if not isinstance(content_lock, dict):
        raise ValueError("manifest content_lock must be an object")
    if content_lock.get("algorithm") != "sha256":
        raise ValueError("manifest content_lock.algorithm must be sha256")
    if content_lock.get("canonicalization") != CANONICAL_CONTENT_LOCK:
        raise ValueError(
            "manifest content_lock.canonicalization must be "
            f"{CANONICAL_CONTENT_LOCK}"
        )
    paths = content_lock.get("paths")
    if not isinstance(paths, list) or not paths:
        raise ValueError("manifest content_lock.paths must be a non-empty array")

    digest = hashlib.sha256()
    for raw_path in paths:
        if not isinstance(raw_path, str) or not raw_path:
            raise ValueError("manifest content_lock.paths must contain non-empty strings")
        relative_path = Path(raw_path)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(f"content lock path must stay inside the repository: {raw_path}")
        source_path = ROOT / relative_path
        if not source_path.is_file():
            raise ValueError(f"content lock path does not exist: {raw_path}")
        path_bytes = raw_path.encode("utf-8")
        file_bytes = source_path.read_bytes()
        digest.update(len(path_bytes).to_bytes(8, byteorder="big"))
        digest.update(path_bytes)
        digest.update(len(file_bytes).to_bytes(8, byteorder="big"))
        digest.update(file_bytes)
    return f"sha256:{digest.hexdigest()}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected = content_digest(manifest)
    content_lock = manifest["content_lock"]
    actual = content_lock.get("digest")
    if args.write:
        content_lock["digest"] = expected
        MANIFEST_PATH.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(expected)
        return 0
    if actual != expected:
        raise SystemExit(
            "capability package content digest mismatch: "
            f"manifest={actual!r}, expected={expected!r}; "
            "run scripts/verify-capability-package-manifest.py --write"
        )
    print(json.dumps({"ok": True, "content_digest": expected}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
