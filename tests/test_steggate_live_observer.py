import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "observe_steggate_live_service.py"
spec = importlib.util.spec_from_file_location("live_observer", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def valid_evaluation():
    return {
        "disposition": "ALLOW",
        "canonical_three_layer_decision": "ALLOW",
        "candidate_hash": "candidate-hash",
        "canonical_three_layer_request_hash": "request-hash",
        "canonical_three_layer_receipt_hash": "receipt-hash",
        "decision_state_hash": "decision-hash",
        "permission_is_not_admissibility": True,
        "continuity_receipt_minted": False,
        "external_execution_performed": False,
        "matrix": [
            {"predicate": "judgment.refusal_available"},
            {"predicate": "signal.reference_state_match"},
            {"predicate": "execution.actor_authority_current"},
            {"predicate": "capability.allowed"},
            {"predicate": "continuity.previous_receipt_verified"},
            {"predicate": "approval.candidate_hash_binding"},
            {"predicate": "permission.present"},
        ],
    }


def responder(responses):
    def _fetch(path, payload=None):
        assert payload is None or path == "/v1/evaluate"
        return responses[path]
    return _fetch


def test_observer_pass_requires_health_self_test_and_complete_evaluation(monkeypatch):
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
        "/v1/evaluate": (True, valid_evaluation(), None),
    }
    monkeypatch.setattr(module, "fetch_json", responder(responses))
    result = module.evaluate_observation()
    assert result["state"] == "PASS"
    assert result["activation_complete"] is True
    assert result["health"]["pass"] is True
    assert result["self_test"]["pass"] is True
    assert result["evaluate"]["pass"] is True
    assert result["archive_allowed"] is False


def test_observer_blocks_when_service_is_unavailable(monkeypatch):
    monkeypatch.setattr(module, "fetch_json", lambda path, payload=None: (False, None, "HTTP_503"))
    result = module.evaluate_observation()
    assert result["state"] == "BLOCKED"
    assert result["activation_complete"] is False
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
        "/v1/evaluate": (True, valid_evaluation(), None),
    }
    monkeypatch.setattr(module, "fetch_json", responder(responses))
    result = module.evaluate_observation()
    assert result["state"] == "BLOCKED"


def test_observer_blocks_incomplete_matrix_or_hashes(monkeypatch):
    evaluation = valid_evaluation()
    evaluation["decision_state_hash"] = ""
    evaluation["matrix"] = [{"predicate": "judgment.refusal_available"}]
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
        "/v1/evaluate": (True, evaluation, None),
    }
    monkeypatch.setattr(module, "fetch_json", responder(responses))
    result = module.evaluate_observation()
    assert result["state"] == "BLOCKED"
    assert result["evaluate"]["pass"] is False
