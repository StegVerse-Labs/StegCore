#!/usr/bin/env python3
"""Validate the StegCore Continuity admissibility receipt mapping document.

This checker intentionally stays local and dependency-free. It verifies that the
mapping document preserves the boundary between Continuity receipts and StegCore
admissibility checks, and that it contains proceed, pause, deny, and commit-time
criteria needed for ecosystem-managed continuation.
"""

from pathlib import Path
import sys

REQUIRED_TERMS = [
    "Continuity receipt",
    "StegCore admissibility check",
    "Proceed Conditions",
    "Pause Conditions",
    "Deny Conditions",
    "Commit-Time Check",
    "does not mint continuity receipts",
    "receipt_id",
    "source_repository",
    "target_repository",
    "current_goal",
    "activation_state",
    "standing_basis",
    "files_built",
    "files_pending",
    "completion_assessment",
    "thread_archive_ready",
]

DENY_TERMS = [
    "bypasses a repository-local handoff",
    "chat memory as the sole source of truth",
    "hides pending work while claiming completion",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def check(path_name: str) -> None:
    path = Path(path_name)
    if not path.exists():
        fail(f"missing file: {path_name}")

    text = path.read_text(encoding="utf-8")

    for term in REQUIRED_TERMS:
        if term not in text:
            fail(f"missing required mapping term: {term}")

    for term in DENY_TERMS:
        if term not in text:
            fail(f"missing required deny boundary: {term}")

    if "production authority" not in text or "receipt-minting" not in text:
        fail("missing authority non-claim boundary")

    print(f"OK: {path_name}")


if __name__ == "__main__":
    target = "docs/CONTINUITY_ADMISSIBILITY_RECEIPT_MAPPING.md"
    if len(sys.argv) > 1:
        target = sys.argv[1]
    check(target)
