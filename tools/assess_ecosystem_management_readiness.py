#!/usr/bin/env python3
"""Assess whether StegVerse ecosystem management can handle handoff/completion."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "docs/STEGVERSE_ECOSYSTEM_MANAGEMENT_MIRROR_HANDOFF.md",
    "ecosystem_management/task_registry.yml",
    "tools/assess_ecosystem_management_readiness.py",
    ".github/workflows/assess-ecosystem-management-readiness.yml",
]

CAPABILITIES = [
    "mirror_handoff_present",
    "machine_readable_task_registry_present",
    "completion_criteria_declared",
    "next_integration_candidate_declared",
    "verification_command_declared",
    "report_artifact_declared",
    "parallel_session_non_overlap_declared",
    "archive_readiness_declared",
]


def sha256_json(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    checks = [{"path": path, "exists": (ROOT / path).exists()} for path in REQUIRED]
    missing = [c["path"] for c in checks if not c["exists"]]
    registry_text = (ROOT / "ecosystem_management/task_registry.yml").read_text(encoding="utf-8") if (ROOT / "ecosystem_management/task_registry.yml").exists() else ""
    capability_checks = []
    for cap in CAPABILITIES:
        key = cap.replace("_", "-")
        present = cap in registry_text or key in registry_text
        capability_checks.append({"capability": cap, "declared": present})
    missing_capabilities = [c["capability"] for c in capability_checks if not c["declared"]]
    outcome = "STEGVERSE_ECOSYSTEM_MANAGEMENT_HANDOFF_CAPABLE" if not missing and not missing_capabilities else "STEGVERSE_ECOSYSTEM_MANAGEMENT_HANDOFF_INCOMPLETE"
    report = {
        "receipt_type": "stegverse_ecosystem_management_readiness_report",
        "timestamp_unix": int(time.time()),
        "outcome": outcome,
        "checks": checks,
        "missing_items": missing,
        "capability_checks": capability_checks,
        "missing_capabilities": missing_capabilities,
        "active_chain": "StegFin provider chain",
        "current_repo": "StegVerse-Labs/stegfin-provider-banking",
        "next_integration_candidate": "StegVerse-Labs/stegfin-provider-acquisition-close",
        "handoff_capable_without_current_thread": outcome.endswith("CAPABLE"),
        "archive_readiness": "ready when report outcome is STEGVERSE_ECOSYSTEM_MANAGEMENT_HANDOFF_CAPABLE",
        "doctrine": "management_selects_and_verifies_tasks_but_does_not_grant_execution_authority",
    }
    report["report_sha256"] = sha256_json(report)
    out = ROOT / "brain_reports/stegverse_ecosystem_management_readiness_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(outcome)
    print(f"report_path={out.relative_to(ROOT)}")
    print(f"report_sha256={report['report_sha256']}")
    print(f"next_integration_candidate={report['next_integration_candidate']}")
    return 0 if outcome.endswith("CAPABLE") else 1


if __name__ == "__main__":
    raise SystemExit(main())
