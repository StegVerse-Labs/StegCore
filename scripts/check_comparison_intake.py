#!/usr/bin/env python3
"""Validate StegCore comparison package intake readiness.

This checker does not validate the package content itself. It confirms that the
repository has a governed intake location and that required package targets are
listed before comparison-package activation is claimed.
"""

from pathlib import Path
import sys

INTAKE_README = Path("docs/comparisons/README.md")
REQUIRED_TARGETS = [
    "docs/comparisons/STEGVERSE_001_AND_CONTEMPORARY_AI_SYSTEMS.md",
    "docs/comparisons/README_COMPARISON_EXCERPT.md",
    "docs/comparisons/INDEX.md",
    "docs/comparisons/INSTALL.md",
    "docs/comparisons/comparison_manifest.json",
    "docs/comparisons/stegverse_001_ai_systems_comparison.json",
    "docs/comparisons/GITHUB_TARGET_PROBE_REPORT.md",
    "docs/comparisons/CONFIRMED_REPO_ADAPTER_STEGCORE.md",
    "docs/comparisons/INSTALL_DECISION_RECORD.md",
    "docs/comparisons/PROGRESS_LINE_4_SPEC.md",
    "docs/comparisons/REPO_STRUCTURE_DELTA_REPORT.md",
    "docs/comparisons/LINE_4_ADOPTION_RECEIPT.md",
]
REQUIRED_BOUNDARIES = [
    "Do not invent comparison package content.",
    "package_artifacts_absent",
    "Install package artifacts when available.",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> None:
    if not INTAKE_README.exists():
        fail(f"missing intake README: {INTAKE_README}")

    text = INTAKE_README.read_text(encoding="utf-8")

    for target in REQUIRED_TARGETS:
        if target not in text:
            fail(f"missing required target: {target}")

    for boundary in REQUIRED_BOUNDARIES:
        if boundary not in text:
            fail(f"missing intake boundary: {boundary}")

    present_targets = [target for target in REQUIRED_TARGETS if Path(target).exists()]
    missing_targets = [target for target in REQUIRED_TARGETS if not Path(target).exists()]

    print(f"OK: {INTAKE_README}")
    print(f"present_targets={len(present_targets)}")
    print(f"missing_targets={len(missing_targets)}")

    if missing_targets:
        print("STATUS: package_artifacts_absent_or_incomplete")
    else:
        print("STATUS: package_artifacts_present")


if __name__ == "__main__":
    main()
