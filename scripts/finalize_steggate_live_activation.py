#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
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


def update_context(observation: dict[str, Any]) -> None:
    context = json.loads(CONTEXT.read_text(encoding="utf-8"))
    current = context.setdefault("current_work", {})
    current["deployment_state"] = "LIVE"
    current["live_observer_state"] = "PASS"
    current["hosted_health"] = "PASS"
    current["hosted_self_test"] = "PASS"
    current["hosted_evaluate"] = "PASS_WITH_COMPLETE_MATRIX_AND_HASHES"
    current["goal_activation_state"] = "COMPLETE"
    current["activation_receipt"] = "data/steggate-live-activation-receipt.json"
    context["session_state"] = "MERGED_INTO_CANONICAL_WORKSTREAM"
    context["archive_allowed"] = True
    worker = context.setdefault("worker_policy", {})
    worker["next_action"] = "Activation complete; preserve receipt and close canonical issue #68."
    worker["archive_status_when_active"] = "ARCHIVE"
    CONTEXT.write_text(json.dumps(context, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_inventory() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    for task in inventory.get("inventory", []):
        if task.get("task_id") in {"FF-DEPLOY-05", "FF-OBSERVE-06", "FF-ACTIVATE-07"}:
            task["claim_state"] = "COMPLETE"
            task["completion_state"] = "COMPLETE_AND_ACTIVATED"
            task["validation_state"] = "HOSTED_PASS"
            task["integration_state"] = "COMPLETE"
            task["archival_dependency"] = False
            task["next_executable_action"] = "None; preserve canonical activation evidence."
    denom = inventory.setdefault("completion_denominators", {})
    denom["tasks_complete"] = denom.get("tasks_total", 7)
    denom["tasks_machine_owned_active"] = 0
    denom["tasks_blocked"] = 0
    denom["tasks_waiting_for_evidence"] = 0
    denom["validation_groups_complete"] = denom.get("validation_groups_required", 7)
    denom["integration_groups_complete"] = denom.get("integration_groups_required", 7)
    inventory["session_state"] = "COMPLETE_ARCHIVE"
    inventory["archive_allowed"] = True
    inventory["role"] = "COMPLETE_ARCHIVE"
    inventory["exact_archive_condition"] = "SATISFIED: hosted activation PASS receipt persisted and all seven activation tasks complete."
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_handoff(receipt: dict[str, Any]) -> None:
    text = HANDOFF.read_text(encoding="utf-8")
    marker = "## Machine-finalized live activation"
    block = (
        f"\n{marker}\n\n"
        "Canonical hosted activation is COMPLETE. The repository-native observer recorded PASS for "
        "`/health`, exact four-disposition `/v1/self-test`, and deterministic complete-matrix "
        "`POST /v1/evaluate`.\n\n"
        f"Activation receipt: `data/steggate-live-activation-receipt.json`  \n"
        f"Observation digest: `{receipt['observation_digest']}`  \n"
        f"Observed at: `{receipt['observed_at']}`\n\n"
        "Issue #68 may be closed by repository automation. No chat-session execution role remains.\n"
    )
    if marker in text:
        text = text.split(marker, 1)[0].rstrip() + block
    else:
        text = text.rstrip() + "\n" + block
    HANDOFF.write_text(text, encoding="utf-8")


def main() -> int:
    observation = json.loads(OBS.read_text(encoding="utf-8"))
    require_pass(observation)
    receipt_body = {
        "schema": "stegverse.steggate_live_activation_receipt.v1",
        "goal_id": "STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001",
        "state": "COMPLETE",
        "origin": observation.get("origin"),
        "observed_at": observation.get("observed_at"),
        "health": observation.get("health"),
        "self_test": observation.get("self_test"),
        "evaluate": observation.get("evaluate"),
        "observation_digest": sha256(observation),
        "canonical_issue": "StegVerse-Labs/StegCore#68",
        "archive_allowed": True,
    }
    receipt = {**receipt_body, "receipt_digest": sha256(receipt_body)}
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    update_context(observation)
    update_inventory()
    update_handoff(receipt)
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
