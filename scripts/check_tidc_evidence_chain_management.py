#!/usr/bin/env python3
"""Fail-closed validator for the current StegCore TIDC evidence-chain management layer."""
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
    require(registry.get("schema") == "stegverse.stegcore.tidc_evidence_chain_registry.v0.2", "wrong schema")
    require(registry.get("source_repo") == "StegVerse-Labs/Site", "wrong source repo")
    require(registry.get("management_repo") == "StegVerse-Labs/StegCore", "wrong management repo")
    require(registry.get("source_issue") == 126, "source issue missing")
    require(registry.get("authority_effect") == "NONE", "authority boundary invalid")
    require(registry.get("build_state") == "BUILT_IN_SITE_AND_STEGCORE", "unexpected build state")
    require(registry.get("ecosystem_state") == "AUTONOMOUS_OBSERVER_ACTIVATED", "unexpected ecosystem state")
    require(registry.get("runtime_state") == "ACTIVE_OBSERVATION_AND_PARALLEL_ADVANCEMENT", "unexpected runtime state")
    require(registry.get("development_halted") is False, "development must not be halted")

    observer = registry.get("observer") or {}
    require(observer.get("script") == "scripts/observe_and_advance_tidc_evidence_chain.py", "observer script drift")
    require(observer.get("receipt") == "brain_reports/tidc_evidence_chain_observation.json", "observer receipt drift")
    require(observer.get("owner_repo") == "StegVerse-Labs/StegCore", "observer owner drift")

    tasks = registry.get("tasks", [])
    expected_ids = [
        "TIDC-EC-001",
        "TIDC-EC-002",
        "TIDC-EC-003",
        "TIDC-EC-004",
        "TIDC-PAR-001",
        "TIDC-PAR-002",
        "TIDC-PAR-003",
        "TIDC-EC-005",
    ]
    require([task.get("id") for task in tasks] == expected_ids, "task IDs or order invalid")
    require(tasks[0].get("status") == "ACTIVE", "observer task must remain ACTIVE")
    for task in tasks[1:4]:
        require(task.get("status") == "CONDITIONALLY_EXECUTABLE", f"unexpected serial task state: {task.get('id')}")
    for task in tasks[4:7]:
        require(task.get("status") == "READY", f"parallel task not READY: {task.get('id')}")
    require(tasks[7].get("status") == "CONDITIONALLY_EXECUTABLE", "release verification state drift")
    require(tasks[7].get("downstream_repos") == [
        "GCAT-BCAT-Engine/Publisher",
        "admissibility-wiki",
        "stegguardian-wiki",
    ], "downstream verification targets drift")

    handoff = HANDOFF.read_text(encoding="utf-8")
    for marker in (
        "SITE_LAYER_ACTIVATED",
        "OBSERVER_ACTIVE",
        "PARALLEL_ADVANCEMENT_ACTIVE",
        "DEVELOPMENT_HALTED=false",
        "management coordination is not research authority",
        "Do not announce archive readiness",
    ):
        require(marker in handoff, f"handoff missing marker: {marker}")

    print("TIDC_ECOSYSTEM_MANAGEMENT_VALID")
    print("schema=v0.2 runtime=ACTIVE_OBSERVATION_AND_PARALLEL_ADVANCEMENT authority_effect=NONE")
    print("development_halted=false tasks=8")


if __name__ == "__main__":
    main()
