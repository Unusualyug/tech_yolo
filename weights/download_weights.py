#!/usr/bin/env python3
"""Fetch Git LFS model weights and verify their SHA-256 object identifiers.

The *.pt files in this checkout are Git LFS pointer files. The pointer's
``oid sha256:...`` is the SHA-256 of the materialized weight file. This script
reads weights/weights_checksums.sha256, optionally runs ``git lfs pull``, and
verifies each materialized file against the expected digest.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "weights" / "weights_checksums.sha256"
POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"


def load_manifest() -> list[tuple[str, str]]:
    entries = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, rel = line.split(None, 1)
        entries.append((digest.strip(), rel.strip()))
    return entries


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_lfs_pointer(path: Path) -> bool:
    if not path.exists():
        return False
    with path.open("rb") as fh:
        return fh.read(len(POINTER_PREFIX)) == POINTER_PREFIX


def fetch_lfs() -> bool:
    commands = [
        ["git", "lfs", "install"],
        ["git", "lfs", "pull"],
    ]
    for cmd in commands:
        try:
            subprocess.run(cmd, cwd=ROOT, check=True)
        except FileNotFoundError:
            print("Git LFS is not installed. Install git-lfs and rerun with --fetch.", file=sys.stderr)
            return False
        except subprocess.CalledProcessError as exc:
            print(f"Command failed: {' '.join(cmd)} (exit {exc.returncode})", file=sys.stderr)
            return False
    return True


def verify(entries: list[tuple[str, str]]) -> bool:
    ok = True
    for digest, rel in entries:
        path = ROOT / rel
        if not path.exists():
            print(f"MISSING   {rel}")
            ok = False
        elif is_lfs_pointer(path):
            print(f"POINTER   {rel} (run with --fetch to materialize)")
            ok = False
        else:
            actual = sha256_file(path)
            status = "OK" if actual == digest else "MISMATCH"
            print(f"{status:8s} {rel}  expected={digest} actual={actual}")
            ok = ok and actual == digest
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="run git lfs install and git lfs pull before verification")
    parser.add_argument("--verify", action="store_true", help="verify materialized weights against the manifest")
    args = parser.parse_args()
    if not args.fetch and not args.verify:
        args.verify = True

    entries = load_manifest()
    if args.fetch and not fetch_lfs():
        return 2
    if args.verify:
        return 0 if verify(entries) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
