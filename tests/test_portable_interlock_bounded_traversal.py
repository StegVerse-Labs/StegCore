import copy
import json
from pathlib import Path

import pytest

from tools.run_portable_interlock_bounded_traversal import build_execution_context, run_traversal
from stegcore.steggate import AdmissibilityRequest
from stegcore.steggate_runtime import governed_steggate_execute

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "portable_interlock_bounded_traversal.v1.json"
REQUEST = ROOT / "examples" / "steggate_allow_request.json"


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_public_interlock_bundle_executes_bounded_canonical_path():
    evidence = run_traversal(FIXTURE, REQUEST)
    assert evidence["proof_state"] == "PASS"
    assert evidence["execution"]["status"] == "executed"
    assert evidence["execution"]["executor_invoked"] is True
    assert evidence["execution"]["coherence_receipt"]["decision"] == "ALLOW"
    assert evidence["next_boundary"] == "SDK_INTERLOCK_RETURN_ASSEMBLY"
    assert evidence["master_records_custody_claimed"] is False


def test_tampered_ingress_hash_is_rejected_before_runtime():
    bundle = load_fixture()
    bundle["interlock_transition"]["manifest"]["source_state_hash"] = "sha256:" + "0" * 64
    with pytest.raises(ValueError, match="ingress interlock hash mismatch"):
        build_execution_context(bundle)


def test_tampered_spe_receipt_fails_closed_before_executor():
    bundle = load_fixture()
    context = build_execution_context(bundle)
    context["standing_evidence"]["spe_receipt"]["reasons"] = ["tampered"]
    request = AdmissibilityRequest.model_validate(json.loads(REQUEST.read_text(encoding="utf-8")))
    calls = []
    result = governed_steggate_execute(
        request,
        lambda: calls.append("executed"),
        declared_execution_context=context,
        capability_surface={"actions_exposed": [request.candidate.action], "execution_mode": "manual", "requires_governed_commit": True},
        authority_resolution={"status": "approved", "basis_invalidated_by_action": False},
    )
    assert result.evaluation.disposition == "FAIL_CLOSED"
    assert result.executor_invoked is False
    assert calls == []


def test_wrong_participant_identity_fails_closed_before_executor():
    bundle = load_fixture()
    context = build_execution_context(bundle)
    context["standing_evidence"]["expected_interlock"]["participant_id"] = "other-participant"
    request = AdmissibilityRequest.model_validate(json.loads(REQUEST.read_text(encoding="utf-8")))
    calls = []
    result = governed_steggate_execute(
        request,
        lambda: calls.append("executed"),
        declared_execution_context=context,
        capability_surface={"actions_exposed": [request.candidate.action], "execution_mode": "manual", "requires_governed_commit": True},
        authority_resolution={"status": "approved", "basis_invalidated_by_action": False},
    )
    assert result.evaluation.disposition == "FAIL_CLOSED"
    assert result.executor_invoked is False
    assert calls == []
