import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("hil_validator", ROOT / "scripts" / "validate_hil_lifecycle.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(mod)

CONTRACT = json.loads((ROOT / "data" / "hil-lifecycle-state-contract.json").read_text())
FIXTURE = json.loads((ROOT / "data" / "hil-lifecycle-evidence.fixture.json").read_text())


def test_current_fixture_continues_without_halting():
    result = mod.validate(FIXTURE, CONTRACT)
    assert result["valid"] is True
    assert result["decision"] == "CONTINUE_INTERNAL_DEVELOPMENT"
    assert result["halted"] is False
    assert result["external_tasks"] == []
    assert result["next_internal_actions"][0]["state_needed"] == "PRIVATE_REVIEW_ACCEPTED"


def test_skipped_state_fails_closed_but_emits_internal_repairs():
    evidence = copy.deepcopy(FIXTURE)
    evidence["observed_states"].append("MASTER_RECORD_CANDIDATE_VALIDATED")
    result = mod.validate(evidence, CONTRACT)
    assert result["valid"] is False
    assert "skipped_state" in result["errors"]
    assert result["decision"] == "CONTINUE_INTERNAL_DEVELOPMENT"
    assert result["next_internal_actions"]


def test_identity_drift_rejected():
    evidence = copy.deepcopy(FIXTURE)
    evidence["receipts"][0]["identities"]["response_sha256"] = "0" * 64
    result = mod.validate(evidence, CONTRACT)
    assert result["valid"] is False
    assert any(e.startswith("identity_drift:") for e in result["errors"])


def test_activation_does_not_grant_publication_or_release():
    evidence = copy.deepcopy(FIXTURE)
    evidence["observed_states"] = CONTRACT["states"]
    evidence["authority"]["publication_authorized"] = True
    evidence["publication_decision_receipt"] = "PUB-1"
    result = mod.validate(evidence, CONTRACT)
    assert result["valid"] is False
    assert "activation_must_not_grant_publication_or_release" in result["errors"]
