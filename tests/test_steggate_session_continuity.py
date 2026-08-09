from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "guard_steggate_session_continuity.py"

spec = importlib.util.spec_from_file_location("continuity_guard", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def base_context():
    return {
        "schema": "stegverse.steggate_session_context.v1",
        "goal_id": "G",
        "canonical_issue": "StegVerse-Labs/StegCore#68",
        "canonical_handoff": "STEGCORE_MIRROR_HANDOFF.md",
        "session_state": "ACTIVE_UNIQUE_WORK_REMAINS",
        "archive_allowed": False,
        "conversation_archive_allowed": False,
        "goal_activation_complete": False,
        "architectural_context": {
            "decision_py_is_intentionally_minimal": True,
            "minimal_means_interface_scope_not_resource_budget": True,
            "minimal_interface_does_not_prove_missing_system_engine": True,
            "complete_decision_state_is_reconstructable_reality": True,
            "required_dispositions": ["ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"],
            "reality_planes": ["decision", "execution", "observed"],
            "existing_canonical_layers": ["src/stegcore/three_layer.py"],
            "reconciliation_record": "docs/STEGGATE_ARCHITECTURE_RECONCILIATION.md",
        },
        "archive_guard": {
            "historical_context_loss_is_failure": True,
            "required_before_archive": ["a", "b", "c", "d", "e"],
        },
        "current_work": {
            "implementation_owner": "StegVerse-Labs/StegCore#68",
            "architecture_reconciliation_state": "IN_PROGRESS",
            "deployment_state": "BLOCKED",
            "provisional_files": ["src/stegcore/steggate.py"],
        },
        "worker_policy": {
            "archive_status_when_active": "DO_NOT_ARCHIVE_UNTIL_GOAL_ACTIVATED_OR_DURABLY_TRANSFERRED",
            "next_action": "trace call graph",
            "machine_observable_release_conditions": ["architecture complete"],
        },
    }


def base_architecture():
    return {
        "schema": "stegverse.steggate_architecture_reconciliation.v1",
        "goal_id": "G",
        "canonical_issue": "StegVerse-Labs/StegCore#68",
        "state": "IN_PROGRESS",
        "canonical_layers": [{"path": "src/stegcore/three_layer.py"}],
        "provisional_layers": [{"path": "src/stegcore/steggate.py"}],
        "required_classifications": sorted(module.REQUIRED_CLASSIFICATIONS),
        "verified_findings": ["three-layer runtime exists"],
        "next_action": "classify overlap",
        "archive_allowed": False,
    }


def complete_architecture():
    architecture = base_architecture()
    architecture.update(
        state="COMPLETE",
        canonical_call_graph=["three_layer", "steggate", "commit"],
        reconciled_live_service={"classification": "adapter"},
        removed_duplication=["duplicate evaluator removed"],
    )
    architecture.pop("provisional_layers", None)
    architecture.pop("required_classifications", None)
    architecture.pop("verified_findings", None)
    architecture.pop("archive_allowed", None)
    return architecture


def test_incomplete_goal_passes_context_but_archive_remains_false_while_active():
    receipt = module.build_receipt(base_context(), base_architecture())
    assert receipt["state"] == "PASS"
    assert receipt["archive_allowed"] is False
    assert receipt["goal_activation_complete"] is False


def test_incomplete_goal_can_archive_after_all_unique_work_is_durably_transferred():
    context = base_context()
    context["session_state"] = "MERGED_INTO_CANONICAL_WORKSTREAM"
    context["archive_allowed"] = True
    context["conversation_archive_allowed"] = True
    context["session_consolidation"] = {
        "all_unique_context_transferred": True,
        "machine_owned_continuation": True,
        "canonical_locations": ["StegVerse-Labs/StegCore#68", "StegVerse-Labs/Site#24"],
        "remaining_tasks": ["stable endpoint activation"],
    }
    receipt = module.build_receipt(context, complete_architecture())
    assert receipt["state"] == "PASS"
    assert receipt["archive_allowed"] is True
    assert receipt["goal_activation_complete"] is False
    assert receipt["session_state"] == "MERGED_INTO_CANONICAL_WORKSTREAM"


def test_merged_session_without_transfer_evidence_fails_closed():
    context = base_context()
    context["session_state"] = "MERGED_INTO_CANONICAL_WORKSTREAM"
    context["archive_allowed"] = True
    context["conversation_archive_allowed"] = True
    receipt = module.build_receipt(context, complete_architecture())
    assert receipt["state"] == "FAIL_CLOSED"
    assert "merged_session_unique_context_not_transferred" in receipt["findings"]


def test_missing_anti_duplication_context_fails_closed():
    context = base_context()
    context["architectural_context"]["minimal_interface_does_not_prove_missing_system_engine"] = False
    receipt = module.build_receipt(context, base_architecture())
    assert receipt["state"] == "FAIL_CLOSED"
    assert "anti_duplication_context_missing" in receipt["findings"]


def test_active_incomplete_goal_cannot_mark_conversation_archive_allowed():
    context = base_context()
    context["conversation_archive_allowed"] = True
    receipt = module.build_receipt(context, base_architecture())
    assert receipt["state"] == "FAIL_CLOSED"
    assert "active_incomplete_goal_conversation_archive_must_be_false" in receipt["findings"]


def test_complete_decision_surface_is_required():
    context = base_context()
    context["architectural_context"]["required_dispositions"] = ["ALLOW", "DENY"]
    receipt = module.build_receipt(context, base_architecture())
    assert receipt["state"] == "FAIL_CLOSED"
    assert "required_dispositions_incomplete" in receipt["findings"]


def test_missing_architecture_state_fails_closed():
    receipt = module.build_receipt(base_context(), None)
    assert receipt["state"] == "FAIL_CLOSED"
    assert "architecture_state_unavailable" in receipt["findings"]


def test_incomplete_architecture_cannot_allow_archive():
    architecture = base_architecture()
    architecture["archive_allowed"] = True
    receipt = module.build_receipt(base_context(), architecture)
    assert receipt["state"] == "FAIL_CLOSED"
    assert "architecture_incomplete_archive_must_be_false" in receipt["findings"]
