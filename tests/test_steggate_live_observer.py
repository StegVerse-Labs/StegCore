import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "observe_steggate_live_service.py"
spec = importlib.util.spec_from_file_location("live_observer", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_observer_pass_requires_health_and_full_self_test(monkeypatch):
    responses = {
        "/health": (True, {"state": "healthy", "canonical_three_layer_bound": True}, None),
        "/v1/self-test": (
            True,
            {
                "state": "PASS",
                "canonical_three_layer_bound": True,
                "observed": {"ALLOW": "ALLOW", "DENY": "DENY", "REVIEW": "REVIEW", "FAIL_CLOSED": "FAIL_CLOSED"},
            },
            None,
        ),
    }
    monkeypatch.setattr(module, "fetch_json", lambda path: responses[path])
    result = module.evaluate_observation()
    assert result["state"] == "PASS"
    assert result["health"]["pass"] is True
    assert result["self_test"]["pass"] is True
    assert result["archive_allowed"] is False


def test_observer_blocks_when_service_is_unavailable(monkeypatch):
    monkeypatch.setattr(module, "fetch_json", lambda path: (False, None, "HTTP_503"))
    result = module.evaluate_observation()
    assert result["state"] == "BLOCKED"
    assert result["archive_allowed"] is False


def test_observer_blocks_partial_disposition_self_test(monkeypatch):
    responses = {
        "/health": (True, {"state": "healthy", "canonical_three_layer_bound": True}, None),
        "/v1/self-test": (
            True,
            {
                "state": "PASS",
                "canonical_three_layer_bound": True,
                "observed": {"ALLOW": "ALLOW", "DENY": "DENY"},
            },
            None,
        ),
    }
    monkeypatch.setattr(module, "fetch_json", lambda path: responses[path])
    result = module.evaluate_observation()
    assert result["state"] == "BLOCKED"
