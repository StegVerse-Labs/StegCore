import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "finalize_steggate_live_activation.py"
spec = importlib.util.spec_from_file_location("finalize_activation", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_finalizer_promotes_only_complete_pass(tmp_path, monkeypatch):
    obs = tmp_path / "observation.json"
    receipt = tmp_path / "receipt.json"
    context = tmp_path / "context.json"
    inventory = tmp_path / "inventory.json"
    handoff = tmp_path / "handoff.md"

    observation = {
        "state": "PASS",
        "origin": "https://example.invalid",
        "observed_at": "2026-08-08T18:00:00Z",
        "health": {"pass": True},
        "self_test": {"pass": True},
        "evaluate": {"pass": True},
    }
    obs.write_text(json.dumps(observation), encoding="utf-8")
    context.write_text(json.dumps({
        "current_work": {},
        "worker_policy": {},
        "session_state": "ACTIVE_UNIQUE_WORK_REMAINS",
        "archive_allowed": False,
    }), encoding="utf-8")
    inventory.write_text(json.dumps({
        "inventory": [
            {"task_id": "FF-DEPLOY-05"},
            {"task_id": "FF-OBSERVE-06"},
            {"task_id": "FF-ACTIVATE-07"},
        ],
        "completion_denominators": {
            "tasks_total": 7,
            "validation_groups_required": 7,
            "integration_groups_required": 7,
        },
    }), encoding="utf-8")
    handoff.write_text("# Handoff\n", encoding="utf-8")

    monkeypatch.setattr(module, "OBS", obs)
    monkeypatch.setattr(module, "RECEIPT", receipt)
    monkeypatch.setattr(module, "CONTEXT", context)
    monkeypatch.setattr(module, "INVENTORY", inventory)
    monkeypatch.setattr(module, "HANDOFF", handoff)

    assert module.main() == 0
    final_receipt = json.loads(receipt.read_text(encoding="utf-8"))
    assert final_receipt["state"] == "COMPLETE"
    assert final_receipt["receipt_digest"].startswith("sha256:")

    final_context = json.loads(context.read_text(encoding="utf-8"))
    assert final_context["current_work"]["goal_activation_state"] == "COMPLETE"
    assert final_context["archive_allowed"] is True

    final_inventory = json.loads(inventory.read_text(encoding="utf-8"))
    assert final_inventory["completion_denominators"]["tasks_complete"] == 7
    assert final_inventory["archive_allowed"] is True
    assert "Machine-finalized live activation" in handoff.read_text(encoding="utf-8")


def test_finalizer_rejects_partial_observation():
    partial = {
        "state": "PASS",
        "health": {"pass": True},
        "self_test": {"pass": True},
        "evaluate": {"pass": False},
    }
    try:
        module.require_pass(partial)
    except SystemExit as exc:
        assert "evaluate PASS" in str(exc)
    else:
        raise AssertionError("partial hosted observation must fail closed")
