import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "render_sdk_usage_notification_v11.py"
spec = importlib.util.spec_from_file_location("render_sdk_usage_notification_v11", SCRIPT)
assert spec and spec.loader
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


def _projection(choice="1", activity_kind="MENU_SELECTION"):
    labels = {
        "000": "Demo test sequence without user-supplied manifest",
        "00": "User-defined run parameters",
        "0": "Submit data for governance",
        "1": "Replay previously run set",
        "2": "Reconstruct previously run set",
    }
    rows = []
    for code in ("000", "00", "0", "1", "2"):
        selected = 1 if code == choice else 0
        rows.append({
            "choice_code": code,
            "choice_label": labels[code],
            "lifetime_invocations": selected,
            "trailing_30_day_invocations": selected,
            "percent_of_total": 100.0 if selected else 0.0,
            "last_used_at": "2026-08-14T20:00:00+00:00" if selected else None,
            "unique_runtime_identities": selected,
            "completed": selected,
            "failed": 0,
            "cancelled": 0,
            "in_progress": 0,
            "menu_selections": selected if activity_kind == "MENU_SELECTION" and code == choice else 0,
            "governed_operations": selected if activity_kind == "GOVERNED_OPERATION" and code == choice else 0,
        })
    return {
        "schema_version": "stegcore.sdk_usage_notification.v1.1",
        "event": {
            "event_id": "SDK-EVT-EXAMPLE",
            "invocation_id": "SDK-INV-EXAMPLE",
            "occurred_at": "2026-08-14T20:00:00+00:00",
            "choice_code": choice,
            "choice_label": labels[choice],
            "phase": "COMPLETED",
            "activity_kind": activity_kind,
            "canonical_runtime_identity": "stegverse-sdk:governance-navigation:v1",
            "source": "sdk-governance-navigation",
            "manifest_receipt_id": "MR-ABCDEF0123456789" if activity_kind == "GOVERNED_OPERATION" and choice in {"1", "2"} else None,
            "transaction_id": None,
            "receipt_chain_head": None,
            "consequence_reexecuted": False if activity_kind == "GOVERNED_OPERATION" and choice == "2" else None,
        },
        "usage": {
            "artifact_type": "stegverse.sdk_usage_summary",
            "schema_version": "1.1",
            "generated_at": "2026-08-14T20:00:01+00:00",
            "observed_since": "2026-08-14T20:00:00+00:00",
            "historical_coverage": "OBSERVED_ONLY",
            "lifetime_all_menu_invocations": 1,
            "trailing_30_day_all_menu_invocations": 1,
            "lifetime_core_governed_invocations": 1 if choice in {"0", "1", "2"} else 0,
            "trailing_30_day_core_governed_invocations": 1 if choice in {"0", "1", "2"} else 0,
            "choices": rows,
            "payload_disclosed": False,
            "observation_grants_authority": False,
        },
        "payload_disclosed": False,
        "notification_grants_authority": False,
    }


def test_menu_replay_does_not_require_receipt_and_is_labeled_selection():
    body = renderer.render_markdown(_projection("1", "MENU_SELECTION"))
    assert "MENU_SELECTION" in body
    assert "Menu selection is not proof a governed operation occurred" in body


def test_governed_replay_requires_manifest_receipt():
    projection = _projection("1", "GOVERNED_OPERATION")
    projection["event"]["manifest_receipt_id"] = None
    with pytest.raises(ValueError, match="requires manifest_receipt_id"):
        renderer.render_markdown(projection)


def test_all_five_canonical_labels_are_rendered():
    body = renderer.render_markdown(_projection("000", "MENU_SELECTION"))
    for code in ("000", "00", "0", "1", "2"):
        assert f"`{code}`" in body
    assert "Demo test sequence without user-supplied manifest" in body
    assert "User-defined run parameters" in body


def test_payload_field_is_rejected():
    projection = _projection()
    projection["event"]["payload"] = {"forbidden": True}
    with pytest.raises(ValueError, match="unsupported fields"):
        renderer.render_markdown(projection)


def test_activity_kind_counts_must_reconcile():
    projection = _projection("00", "MENU_SELECTION")
    row = next(row for row in projection["usage"]["choices"] if row["choice_code"] == "00")
    row["governed_operations"] = 1
    with pytest.raises(ValueError, match="reconcile"):
        renderer.render_markdown(projection)
