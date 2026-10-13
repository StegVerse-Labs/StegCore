"""Regression tests: receipt validation and persistence never silently authorize."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "evaluate_recreation_gate.py"
spec = importlib.util.spec_from_file_location("recreation_gate_under_test", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def _request():
    return {
        "request_id": "test",
        "recreation_complete": True,
        "recovery_proof_complete": True,
        "verification_margin_complete": True,
        "external_exposures_complete": True,
        "trusted_pre_state_hash": "same",
        "recreated_state_hash": "same",
        "divergence_detected": False,
        "divergence_resolution_status": "not_needed",
        "authority_current": True,
        "consent_current": True,
        "policy_current": True,
        "unresolved_conditions_evaluated": True,
        "continuity_receipt_ref": "continuity",
        "recovery_receipt_ref": "recovery",
        "divergence_report_ref": "divergence",
    }


def _run(tmp_path, monkeypatch, capsys, output, receipt_schema):
    request = tmp_path / "request.json"
    req_schema = tmp_path / "request-schema.json"
    rec_schema = tmp_path / "receipt-schema.json"
    request.write_text(json.dumps(_request()))
    req_schema.write_text("{}")
    rec_schema.write_text(json.dumps(receipt_schema))
    monkeypatch.setattr("sys.argv", [
        "evaluate_recreation_gate", str(request),
        "--request-schema", str(req_schema),
        "--receipt-schema", str(rec_schema),
        "--output", str(output),
    ])
    result = gate.main()
    return result, capsys.readouterr().out


def test_receipt_schema_rejection_fails_closed(tmp_path, monkeypatch, capsys):
    output = tmp_path / "receipt.json"
    code, stdout = _run(tmp_path, monkeypatch, capsys, output, {"not": {}})
    assert code == 2
    assert not output.exists()
    payload = json.loads(stdout.strip().splitlines()[-1])
    assert payload["disposition"] == "FAIL_CLOSED"
    assert payload["failed_predicate"] == "RECREATION_RECEIPT_VALID_AND_PERSISTED"
    assert payload["authority_effect"] == "NONE"


def test_receipt_write_failure_fails_closed(tmp_path, monkeypatch, capsys):
    parent = tmp_path / "occupied"
    parent.write_text("not a directory")
    output = parent / "receipt.json"
    code, stdout = _run(tmp_path, monkeypatch, capsys, output, {})
    assert code == 2
    payload = json.loads(stdout.strip().splitlines()[-1])
    assert payload["disposition"] == "FAIL_CLOSED"
    assert payload["failed_predicate"] == "RECREATION_RECEIPT_VALID_AND_PERSISTED"
    assert not output.exists()

def test_missing_request_field_fails_closed(tmp_path, monkeypatch, capsys):
    incomplete = _request()
    incomplete.pop("recreation_complete")
    monkeypatch.setattr(gate, "load", lambda path: incomplete if path.name == "request.json" else {})
    code, stdout = _run(tmp_path, monkeypatch, capsys, tmp_path / "receipt.json", {})
    assert code == 2
    payload = json.loads(stdout.strip().splitlines()[-1])
    assert payload["disposition"] == "FAIL_CLOSED"
    assert payload["failed_predicate"] == "RECREATION_REQUEST_REQUIRED_EVIDENCE_PRESENT"
    assert payload["authority_effect"] == "NONE"
    assert not (tmp_path / "receipt.json").exists()
