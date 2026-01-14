#!/usr/bin/env python3
"""
Bump StegCore version (SemVer) by updating VERSION file.

Usage:
  python scripts/release/bump_version.py patch
  python scripts/release/bump_version.py minor
  python scripts/release/bump_version.py major

Also supports explicit version:
  python scripts/release/bump_version.py 1.2.3
"""

from __future__ import annotations
import re
import sys
from pathlib import Path
from datetime import datetime

VERSION_FILE = Path("VERSION")

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def read_version() -> str:
    if not VERSION_FILE.exists():
        die("VERSION file not found at repo root.")
    v = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not SEMVER_RE.match(v):
        die(f"VERSION is not valid semver: {v}")
    return v

def write_version(v: str) -> None:
    VERSION_FILE.write_text(v + "\n", encoding="utf-8")

def bump(v: str, kind: str) -> str:
    m = SEMVER_RE.match(v)
    assert m
    major, minor, patch = map(int, m.groups())
    if kind == "patch":
        patch += 1
    elif kind == "minor":
        minor += 1
        patch = 0
    elif kind == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        die("Bump kind must be: patch | minor | major")
    return f"{major}.{minor}.{patch}"

def main() -> None:
    if len(sys.argv) != 2:
        die("Provide one argument: patch|minor|major OR explicit version X.Y.Z")

    arg = sys.argv[1].strip()
    cur = read_version()

    if SEMVER_RE.match(arg):
        nxt = arg
    else:
        nxt = bump(cur, arg)

    write_version(nxt)
    print(f"Bumped VERSION: {cur} -> {nxt} ({datetime.utcnow().isoformat()}Z)")

if __name__ == "__main__":
    main()
