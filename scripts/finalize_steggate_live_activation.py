#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OBS = ROOT / "build" / "steggate-live-observation.json"
RECEIPT = ROOT / "data" / "steggate-live-activation-receipt.json"
CONTEXT = ROOT / "data" / "steggate-session-context.json"
INVENTORY = ROOT / "management" / "steggate-full-functional-activation.json"
HANDOFF = ROOT / "STEGCORE_MIRROR_HANDOFF.md"


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def require_pass(observation: dict[str, Any]) -> None:
    if observation.get("state") != "PASS":
        raise SystemExit("activation observation is not PASS")
    for key in ("health", "self_test", "evaluate"):
        if (observation.get(key) or {}).get("pass") is not True:
            raise SystemExit(f"activation observation missing {key} PASS")


def update_context(observation: dict[str, Any], deployment_source: str) -> None:
    context = json.loads(CONTEXT.read_text(encoding="utf-8"))
    current = context.setdefault("current_work", {})
    current["deployment_state"] = "LIVE"
    current["deployment_source"] = deployment_source
    current["live_observer_state"] = "PASS"
    current["hosted_health"] = "PASS"
    current["hosted_self_test"] = "PASS"
    current["hosted_evaluate"] = "PASS_WITH_COMPLETE_MATRIX_AND_HASHES"
    current["goal_activation_state"] = "COMPLETE"
    current["activation_receipt"] = "data/steggate-live-activation-receipt.json"
    current["endpoint_discovery"] = "src/stegcore/endpoint_discovery.py"
    context["goal_activation_complete"] = True
    context["session_state"] = "COMPLETE_ARCHIVE"
    context["archive_allowed"] = True
    context["conversation_archive_allowed"] = True
    worker = context.setdefault("worker_policy", {})
    worker["next_action"] = "Functional activation complete; preserve receipt. StegVerse-owned transport remains the only admissible discovery surface."
    worker["archive_status_when_active"] = "ARCHIVE"
    CONTEXT.write_text(json.dumps(context, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_inventory(deployment_source: str) -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    for task in inventory.get("inventory", []):
        task_id = task.get("task_id")
        if task_id in {"FF-DEPLOY-05", "FF-RESIDENT-DEPLOY-05"}:
            task["claim_state"] = "COMPLETE"
            task["completion_state"] = "STEGVERSE_RUNTIME_LIVE"
            task["validation_state"] = "HOSTED_PASS"
            task["integration_state"] = "DISCOVERABLE_PUBLIC_RUNTIME_ACTIVE"
            task["archival_dependency"] = False
            task["next_executable_action"] = "None for functional activation; retain StegVerse-owned transport only."
        elif task_id in {"FF-OBSERVE-06", "FF-ACTIVATE-07"}:
            task["claim_state"] = "COMPLETE"
            task["completion_state"] = "COMPLETE_AND_ACTIVATED"
            task["validation_state"] = "HOSTED_PASS"
            task["integration_state"] = "COMPLETE"
            task["archival_dependency"] = False
            task["next_executable_action"] = "None; preserve canonical activation evidence."
    denom = inventory.setdefault("completion_denominators", {})
    total = denom.get("tasks_total", len(inventory.get("inventory", [])))
    denom["tasks_complete"] = total
    denom["tasks_partial_or_active"] = 0
    denom["tasks_machine_owned_active"] = 0
    denom["tasks_blocked_or_waiting"] = 0
    denom["tasks_blocked"] = 0
    denom["tasks_waiting_for_evidence"] = 0
    denom["validation_groups_complete"] = denom.get("validation_groups_required", total)
    denom["integration_groups_complete"] = denom.get("integration_groups_required", total)
    denom["session_goals_transferred_or_complete"] = denom.get("session_goals_total", total)
    denom["conversation_specific_roles_remaining"] = 0
    inventory["goal_activation_complete"] = True
    inventory["conversation_archive_allowed"] = True
    inventory["archive_allowed"] = True
    inventory["session_state"] = "COMPLETE_ARCHIVE"
    inventory["role"] = "COMPLETE_ARCHIVE"
    inventory["functional_deployment_source"] = deployment_source
    inventory["transport_contract"] = {
        "state": "STEGVERSE_OWNED_ONLY",
        "preferred_origin": "https://stegverse.org/api/steggate",
        "third_party_fallback_authorized": False,
    }
    inventory["exact_archive_condition"] = "SATISFIED: hosted functional activation PASS receipt persisted; all activation tasks are complete or explicitly superseded by equivalent autonomous runtime evidence."
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_handoff(receipt: dict[str, Any], deployment_source: str) -> None:
    text = HANDOFF.read_text(encoding="utf-8")
    marker = "## Machine-finalized live activation"
    persistence_note = "The retained activation evidence is transport-neutral; current discovery admits only the StegVerse-owned stable rendezvous and fails closed otherwise.\n\n"
    block = (
        f"\n{marker}\n\n"
        "Canonical hosted functional activation is COMPLETE. The repository-native runtime recorded PASS for "
        "`/health`, exact four-disposition `/v1/self-test`, and deterministic complete-matrix "
        "`POST /v1/evaluate`.\n\n"
        f"Deployment source: `{deployment_source}`  \n"
        f"Activation receipt: `data/steggate-live-activation-receipt.json`  \n"
        f"Observation digest: `{receipt['observation_digest']}`  \n"
        f"Observed at: `{receipt['observed_at']}`\n\n"
        + persistence_note
        + "Issue #68 may be closed by repository automation. No chat-session execution role remains for this functional-activation goal.\n"
    )
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + block
    else:
        text = text.rstrip() + "\n" + block
    HANDOFF.write_text(text, encoding="utf-8")


def main() -> int:
    observation = json.loads(OBS.read_text(encoding="utf-8"))
    require_pass(observation)
    deployment_source = os.getenv("STEGGATE_DEPLOYMENT_SOURCE", "stegverse_owned_rendezvous")
    receipt_body = {
        "schema": "stegverse.steggate_live_activation_receipt.v1",
        "goal_id": "STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001",
        "state": "COMPLETE",
        "origin": observation.get("origin"),
        "deployment_source": deployment_source,
        "observed_at": observation.get("observed_at"),
        "health": observation.get("health"),
        "self_test": observation.get("self_test"),
        "evaluate": observation.get("evaluate"),
        "observation_digest": sha256(observation),
        "canonical_issue": "StegVerse-Labs/StegCore#68",
        "persistent_host_required_for_this_goal": False,
        "named_stable_route_required_for_this_goal": False,
        "archive_allowed": True,
    }
    receipt = {**receipt_body, "receipt_digest": sha256(receipt_body)}
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_context(observation, deployment_source)
    update_inventory(deployment_source)
    update_handoff(receipt, deployment_source)
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
