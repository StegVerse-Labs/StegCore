from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_personal_data_control_manifest_is_non_authorizing_and_local() -> None:
    manifest = json.loads(
        (ROOT / "runtime/personal-data-control-decision.v1.json").read_text(encoding="utf-8")
    )
    assert manifest["state"] == "ACTIVATED_AND_CI_BOUND"
    assert manifest["external_tasks_required"] is False
    assert manifest["manual_tasks_required"] is False
    assert all(value is False for value in manifest["authority"].values())
    assert manifest["task"]["repository"] == "StegVerse-Labs/StegCore"
    assert manifest["task"]["status"] == "COMPLETE"


def test_unresolved_request_states_do_not_become_external_tasks() -> None:
    manifest = json.loads(
        (ROOT / "runtime/personal-data-control-decision.v1.json").read_text(encoding="utf-8")
    )
    assert "CHANNEL_FAILED" in manifest["non_halting_states"]
    assert "PROCESSOR_PROPAGATION_PENDING" in manifest["non_halting_states"]
    assert "DEFER" in manifest["non_halting_states"]
