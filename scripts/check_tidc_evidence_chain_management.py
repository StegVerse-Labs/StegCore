#!/usr/bin/env python3
"""Fail-closed validator for the StegCore TIDC evidence-chain management layer."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ecosystem_management" / "tidc_evidence_chain_registry.json"
HANDOFF = ROOT / "docs" / "TIDC_EVIDENCE_CHAIN_MIRROR_HANDOFF.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"TIDC_ECOSYSTEM_MANAGEMENT_INVALID: {message}")


def main() -> None:
    require(REGISTRY.exists(), "registry missing")
    require(HANDOFF.exists(), "handoff missing")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    require(registry.get("schema") == "stegverse.stegcore.tidc_evidence_chain_registry.v0.1", "wrong schema")
    require(registry.get("source_repo") == "StegVerse-Labs/Site", "wrong source repo")
    require(registry.get("management_repo") == "StegVerse-Labs/StegCore", "wrong management repo")
    require(registry.get("source_issue") == 126, "source issue missing")
    require(registry.get("authority_effect") == "NONE", "authority boundary invalid")
    require(registry.get("runtime_state") == "IDLE_PENDING_EXTERNAL_RETURN", "unexpected runtime state")

    tasks = registry.get("tasks", [])
    require(len(tasks) == 5, "expected five coordinated tasks")
    expected_ids = [f"TIDC-EC-00{i}" for i in range(1, 6)]
    require([task.get("id") for task in tasks] == expected_ids, "task IDs or order invalid")
    require(tasks[0].get("status") == "BLOCKED_EXTERNAL_INPUT", "external-input blocker not preserved")

    handoff = HANDOFF.read_text(encoding="utf-8")
    for marker in (
        "SITE_LAYER_ACTIVATED",
        "EXTERNAL_RETURN_PENDING",
        "management coordination is not research authority",
        "Do not announce archive readiness",
    ):
        require(marker in handoff, f"handoff missing marker: {marker}")

    print("TIDC_ECOSYSTEM_MANAGEMENT_VALID")
    print("state=MANAGEMENT_LAYER_STARTED runtime=IDLE_PENDING_EXTERNAL_RETURN authority_effect=NONE")


if __name__ == "__main__":
    main()
