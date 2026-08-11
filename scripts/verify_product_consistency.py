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
    "docs/ADMITTEDCODE_PERFORMANCE.md",
    "benchmarks/admittedcode-performance-policy.json",
    "tools/run_admittedcode_benchmarks.py",
    "tests/test_admittedcode_performance.py",
    ".github/workflows/admittedcode-performance.yml",
    "STEGCORE_MIRROR_HANDOFF.md",
    "management/steggate-four-app-runtime-binding.json",
    "scripts/release/bump_version.py",
    "scripts/release/update_changelog.py",
    ".github/workflows/release-bump.yml",
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
    for required in (version_file, CANONICAL_RUNTIME_IDENTITY, CANONICAL_RUNTIME, "run_admittedcode_benchmarks.py"):
        if required not in readme:
            failures.append(f"README missing current-product identity/performance surface: {required}")

    portable_doc = _read("docs/STEGGATE_PORTABLE_PRODUCT.md")
    for required in (version_file, CANONICAL_RUNTIME_IDENTITY, CANONICAL_RUNTIME):
        if required not in portable_doc:
            failures.append(f"portable product doc missing identity: {required}")

    performance_doc = _read("docs/ADMITTEDCODE_PERFORMANCE.md")
    for required in (CANONICAL_RUNTIME_IDENTITY, CANONICAL_RUNTIME, "false-ALLOW", "p95", "admittedcode-performance-receipt.json"):
        if required not in performance_doc:
            failures.append(f"performance contract missing required concept: {required}")

    policy = json.loads(_read("benchmarks/admittedcode-performance-policy.json"))
    if policy.get("runtime_identity") != CANONICAL_RUNTIME_IDENTITY:
        failures.append("performance policy runtime identity drift")
    if policy.get("canonical_runtime") != CANONICAL_RUNTIME:
        failures.append("performance policy canonical runtime drift")
    blocking_required = {
        "false_allow_rate",
        "four_disposition_correctness_rate",
        "fail_closed_integrity_rate",
        "candidate_binding_integrity_rate",
        "deterministic_semantic_replay_rate",
        "cross_interface_equivalence_rate",
        "runtime_identity_consistency_rate",
        "parallel_evaluator_escape_count",
        "matrix_completeness_rate",
        "reason_code_presence_rate",
    }
    headline = policy.get("headline_kpis", {})
    for name in blocking_required:
        if name not in headline or headline[name].get("release_blocking") is not True:
            failures.append(f"performance policy missing release-blocking KPI: {name}")

    benchmark = _read("tools/run_admittedcode_benchmarks.py")
    for required in (
        "stegverse.admittedcode.performance-receipt.v1",
        "deterministic_semantic_replay_rate",
        "cross_interface_equivalence_rate",
        "core_wall_latency",
        "throughput",
        "cold_start",
        "governance_overhead",
        "developer_experience",
        "consumer_integration",
    ):
        if required not in benchmark:
            failures.append(f"benchmark runner missing measurement surface: {required}")

    performance_workflow = _read(".github/workflows/admittedcode-performance.yml")
    if "python tools/run_admittedcode_benchmarks.py" not in performance_workflow:
        failures.append("hosted performance workflow does not run canonical benchmark")
    if "actions/upload-artifact@v4" not in performance_workflow:
        failures.append("hosted performance workflow does not retain benchmark receipt")

    example = json.loads(_read("examples/steggate_allow_request.json"))
    required_sections = {"candidate", "judgment", "signal", "execution", "capability", "continuity", "approval"}
    missing_sections = sorted(required_sections - set(example))
    if missing_sections:
        failures.append(f"example request missing sections: {', '.join(missing_sections)}")

    pyproject = tomllib.loads(_read("pyproject.toml"))
    scripts = pyproject["project"].get("scripts", {})
    if scripts.get("steggate") != "stegcore.cli:main":
        failures.append("pyproject must expose steggate = stegcore.cli:main")

    bump_script = _read("scripts/release/bump_version.py")
    for required_surface in ("VERSION", "pyproject.toml", "src/stegcore/version.py"):
        if required_surface not in bump_script:
            failures.append(f"release bump script does not manage {required_surface}")

    release_workflow = _read(".github/workflows/release-bump.yml")
    required_git_add = "git add VERSION pyproject.toml src/stegcore/version.py CHANGELOG.md"
    if required_git_add not in release_workflow:
        failures.append("release workflow does not commit all portable product version surfaces")
    if "python scripts/verify_product_consistency.py" not in release_workflow:
        failures.append("release workflow does not run product consistency verification")

    changelog = _read("CHANGELOG.md")
    if f"## [{version_file}]" not in changelog:
        failures.append(f"CHANGELOG.md has no entry for current product version {version_file}")
    if "AdmittedCode performance policy" not in changelog:
        failures.append("CHANGELOG.md does not record performance tracking installation")

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
    print("admittedcode_performance_tracking: ACTIVE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
