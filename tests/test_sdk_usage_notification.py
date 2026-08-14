import importlib.util
from pathlib import Path

import pytest

from stegcore.sdk_operation_events import SDKOperationEventLedger


SCRIPT = Path(__file__).parents[1] / "scripts" / "render_sdk_usage_notification.py"
spec = importlib.util.spec_from_file_location("render_sdk_usage_notification", SCRIPT)
assert spec and spec.loader
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


def _projection():
    ledger = SDKOperationEventLedger()
    started = ledger.begin(
        choice_code="1",
        canonical_runtime_identity="stegverse:steggate:canonical:three-layer:v1",
        source="sdk",
        manifest_receipt_id="MR-EXAMPLE",
        invocation_id="SDK-INV-EXAMPLE",
    )
    terminal = ledger.finish(started.invocation_id, phase="COMPLETED")
    return ledger.notification_projection(terminal)


def test_projection_renders_all_five_choices_and_coverage_boundary():
    body = renderer.render_markdown(_projection())
    for choice in ("000", "00", "0", "1", "2"):
        assert f"`{choice}`" in body
    assert "Observed since" in body
    assert "Core governed operations (`0+1+2`)" in body
    assert "All SDK menu activity" in body
    assert "GitHub is not canonical custody" in body


def test_renderer_rejects_payload_field_even_when_payload_disclosed_is_false():
    projection = _projection()
    projection["event"]["payload"] = {"sensitive": "must-not-project"}
    with pytest.raises(ValueError, match="unsupported fields"):
        renderer.render_markdown(projection)


def test_renderer_rejects_authority_projection():
    projection = _projection()
    projection["notification_grants_authority"] = True
    with pytest.raises(ValueError, match="notification_grants_authority=false"):
        renderer.render_markdown(projection)


def test_renderer_rejects_incomplete_five_choice_census():
    projection = _projection()
    projection["usage"]["choices"] = projection["usage"]["choices"][:-1]
    with pytest.raises(ValueError, match="exactly five"):
        renderer.render_markdown(projection)


def test_renderer_rejects_reconstruct_claiming_consequence_reexecution():
    ledger = SDKOperationEventLedger()
    started = ledger.begin(
        choice_code="2",
        canonical_runtime_identity="stegverse:steggate:canonical:three-layer:v1",
        source="sdk",
        manifest_receipt_id="MR-RECONSTRUCT",
        invocation_id="SDK-INV-RECONSTRUCT",
    )
    terminal = ledger.finish(
        started.invocation_id,
        phase="COMPLETED",
        consequence_reexecuted=False,
    )
    projection = ledger.notification_projection(terminal)
    projection["event"]["consequence_reexecuted"] = True
    with pytest.raises(ValueError, match="cannot claim consequence re-execution"):
        renderer.render_markdown(projection)
