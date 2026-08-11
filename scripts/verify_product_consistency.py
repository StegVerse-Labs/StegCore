from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]

CANONICAL_RUNTIME_IDENTITY = "stegverse:steggate:canonical:three-layer:v1"
CANONICAL_RUNTIME = "stegcore.three_layer.evaluate_three_layer"
REQUIRED_CURRENT_PATHS = (
    "README.md",
    "VERSION",
    "pyproject.toml",
    "src/stegcore/version.py",
    "src/stegcore/steggate.py",
    "src/stegcore/service.py",
    "src/stegcore/cli.py",
    "examples/steggate_allow_request.json",
    "docs/STEGGATE_PORTABLE_PRODUCT.md",
    "docs/STEGGATE_RUNTIME_IDENTITY_CONTRACT.md",
    "STEGCORE_MIRROR_HANDOFF.md",
    "management/steggate-four-app-runtime-binding.json",
)


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _source_version() -> str:
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', _read("src/stegcore/version.py"), re.MULTILINE)
    if not match:
        raise AssertionError("src/stegcore/version.py does not declare __version__")
    return match.group(1)


def check() -> list[str]:
    failures: list[str] = []

    for relative in REQUIRED_CURRENT_PATHS:
        if not (ROOT / relative).exists():
            failures.append(f"missing current-product path: {relative}")

    if failures:
        return failures

    version_file = _read("VERSION").strip()
    package_version = tomllib.loads(_read("pyproject.toml"))["project"]["version"]
    source_version = _source_version()
    if len({version_file, package_version, source_version}) != 1:
        failures.append(
            "portable product version drift: "
            f"VERSION={version_file}, pyproject={package_version}, source={source_version}"
        )

    service = _read("src/stegcore/service.py")
    if "SERVICE_VERSION = __version__" not in service:
        failures.append("service version must derive from stegcore.version.__version__")
    if CANONICAL_RUNTIME_IDENTITY not in service:
        failures.append("service runtime identity drift")
    if CANONICAL_RUNTIME not in service:
        failures.append("service canonical admissibility runtime drift")

    cli = _read("src/stegcore/cli.py")
    for command in ('"evaluate"', '"self-test"', '"identity"', '"serve"'):
        if command not in cli:
            failures.append(f"portable CLI missing command {command}")

    readme = _read("README.md")
    stale_current_claims = (
        "v0.1 is **documentation-first**",
        "Code in `src/stegcore/` is scaffolding and substrate for future runtimes",
    )
    for stale in stale_current_claims:
        if stale in readme:
            failures.append(f"README contains stale current-product claim: {stale}")
    for required in (version_file, CANONICAL_RUNTIME_IDENTITY, CANONICAL_RUNTIME):
        if required not in readme:
            failures.append(f"README missing current-product identity: {required}")

    portable_doc = _read("docs/STEGGATE_PORTABLE_PRODUCT.md")
    for required in (version_file, CANONICAL_RUNTIME_IDENTITY, CANONICAL_RUNTIME):
        if required not in portable_doc:
            failures.append(f"portable product doc missing identity: {required}")

    example = json.loads(_read("examples/steggate_allow_request.json"))
    required_sections = {"candidate", "judgment", "signal", "execution", "capability", "continuity", "approval"}
    missing_sections = sorted(required_sections - set(example))
    if missing_sections:
        failures.append(f"example request missing sections: {', '.join(missing_sections)}")

    pyproject = tomllib.loads(_read("pyproject.toml"))
    scripts = pyproject["project"].get("scripts", {})
    if scripts.get("steggate") != "stegcore.cli:main":
        failures.append("pyproject must expose steggate = stegcore.cli:main")

    return failures


def main() -> int:
    failures = check()
    if failures:
        print("StegGate product consistency: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("StegGate product consistency: PASS")
    print(f"version: {_read('VERSION').strip()}")
    print(f"runtime_identity: {CANONICAL_RUNTIME_IDENTITY}")
    print(f"canonical_runtime: {CANONICAL_RUNTIME}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
