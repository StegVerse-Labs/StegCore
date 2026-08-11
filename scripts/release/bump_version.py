#!/usr/bin/env python3
"""Bump the canonical StegGate portable product version consistently.

Updates, as one logical release operation:
- VERSION
- pyproject.toml project.version
- src/stegcore/version.py __version__

Usage:
  python scripts/release/bump_version.py patch
  python scripts/release/bump_version.py minor
  python scripts/release/bump_version.py major
  python scripts/release/bump_version.py 1.2.3
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
import sys
import tomllib

VERSION_FILE = Path("VERSION")
PYPROJECT_FILE = Path("pyproject.toml")
SOURCE_VERSION_FILE = Path("src/stegcore/version.py")
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
SOURCE_RE = re.compile(r'(^__version__\s*=\s*["\'])([^"\']+)(["\']\s*$)', re.MULTILINE)


def die(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def _require(path: Path) -> str:
    if not path.exists():
        die(f"required version surface missing: {path}")
    return path.read_text(encoding="utf-8")


def read_versions() -> tuple[str, str, str]:
    version = _require(VERSION_FILE).strip()
    pyproject_text = _require(PYPROJECT_FILE)
    source_text = _require(SOURCE_VERSION_FILE)

    package_version = tomllib.loads(pyproject_text)["project"]["version"]
    match = SOURCE_RE.search(source_text)
    if not match:
        die("src/stegcore/version.py does not declare __version__")
    source_version = match.group(2)

    for label, value in (
        ("VERSION", version),
        ("pyproject.toml", package_version),
        ("src/stegcore/version.py", source_version),
    ):
        if not SEMVER_RE.fullmatch(value):
            die(f"{label} is not valid semver: {value}")

    return version, package_version, source_version


def bump(version: str, kind: str) -> str:
    match = SEMVER_RE.fullmatch(version)
    assert match
    major, minor, patch = map(int, match.groups())
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
        die("bump kind must be patch | minor | major or an explicit X.Y.Z version")
    return f"{major}.{minor}.{patch}"


def write_versions(version: str) -> None:
    VERSION_FILE.write_text(version + "\n", encoding="utf-8")

    pyproject = _require(PYPROJECT_FILE)
    updated_pyproject, count = re.subn(
        r'(?m)^(version\s*=\s*)"[^"]+"\s*$',
        rf'\1"{version}"',
        pyproject,
        count=1,
    )
    if count != 1:
        die("could not update exactly one pyproject.toml project version")
    PYPROJECT_FILE.write_text(updated_pyproject, encoding="utf-8")

    source = _require(SOURCE_VERSION_FILE)
    updated_source, count = SOURCE_RE.subn(rf'\g<1>{version}\g<3>', source, count=1)
    if count != 1:
        die("could not update exactly one source __version__")
    SOURCE_VERSION_FILE.write_text(updated_source, encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        die("provide one argument: patch|minor|major or explicit version X.Y.Z")

    current_versions = read_versions()
    if len(set(current_versions)) != 1:
        die(
            "current product version surfaces already drift: "
            f"VERSION={current_versions[0]}, pyproject={current_versions[1]}, source={current_versions[2]}"
        )

    current = current_versions[0]
    arg = sys.argv[1].strip()
    next_version = arg if SEMVER_RE.fullmatch(arg) else bump(current, arg)
    write_versions(next_version)

    observed = read_versions()
    if observed != (next_version, next_version, next_version):
        die(f"post-write version verification failed: {observed}")

    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"Bumped portable product version: {current} -> {next_version} ({timestamp})")


if __name__ == "__main__":
    main()
