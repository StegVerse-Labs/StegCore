from __future__ import annotations

import importlib.util
from pathlib import Path

from stegcore.steggate import (
    AdmissibilityRequest,
    ApprovalState,
    Candidate,
    CapabilityState,
    ContinuityState,
    ExecutionState,
    JudgmentState,
    SignalState,
)

ROOT = Path(__file__).resolve().parents[1]


def load_legacy_module():
    path = ROOT / "core" / "llm_adapter.py"
    spec = importlib.util.spec_from_file_location("legacy_llm_adapter", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def allowed_request() -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="system",
            action="write_record",
            target="record:llm-adapter",
            scope="test",
            parameters={"value": 1},
        ),
        judgment=JudgmentState(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=["judgment:e1"],
        ),
        signal=SignalState(
            admitted_signal_refs=["signal:s1"],
            transformations=["test:v1"],
            missing_inputs=[],
            uncertainty_state="bounded",
            reference_state_hash="state:1",
            expected_reference_state_hash="state:1",
            reconstruction_available=True,
            transformation_provenance_complete=True,
        ),
        execution=ExecutionState(
            actor_authority_current=True,
            policy_current=True,
            delegation_current=True,
            evidence_current=True,
            affected_entity_conditions_represented=True,
            recoverability_profile="recoverable",
            validity_window_open=True,
            policy_ref="policy:p1",
            delegation_ref="delegation:d1",
            evidence_refs=["execution:e1"],
        ),
        capability=CapabilityState(allowed=True),
        continuity=ContinuityState(
            required=True,
            previous_receipt_verified=True,
            previous_receipt_hash="receipt:r0",
        ),
        approval=ApprovalState(required=False),
        permission_present=False,
    )


def capability_surface():
    return {
        "actions_exposed": ["write_record"],
        "execution_mode": "manual",
        "requires_governed_commit": True,
    }


def authority_resolution():
    return {"status": "approved", "basis_invalidated_by_action": False}


def test_legacy_evaluate_action_fails_closed_without_canonical_request(tmp_path):
    module = load_legacy_module()
    adapter = module.LLMAdapter(
        receipts_path=str(tmp_path / "receipts.jsonl"),
        candidates_path=str(tmp_path / "candidates"),
    )
    result = adapter.evaluate_action(
        prompt="Transfer 100 StegCoin",
        user_id="user-1",
        entity_subject_id="steg:agent/personal:test",
        action_intent="transfer 100 StegCoin",
        activation_tier="stegclaw",
    )

    assert result["decision"] == "FAIL_CLOSED"
    assert result["reason"] == "canonical_admissibility_request_required"
    assert result["receipt"]["admissibility_authority"] is False
    assert result["receipt"]["parallel_evaluator_used"] is False


def test_manifested_method_traverses_canonical_transaction_lifecycle(tmp_path):
    module = load_legacy_module()
    adapter = module.LLMAdapter(
        receipts_path=str(tmp_path / "receipts.jsonl"),
        candidates_path=str(tmp_path / "candidates"),
        transaction_ledger_path=str(tmp_path / "transactions.jsonl"),
    )
    calls: list[str] = []

    result = adapter.evaluate_manifested_action(
        allowed_request(),
        lambda: calls.append("executed") or {"record": "written"},
        prompt="Write this governed record",
        entity_subject_id="steg:agent/personal:test",
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )

    assert result.chain_verified is True
    assert result.replay.expected_disposition == "ALLOW"
    assert result.replay.expected_executor_invoked is True
    assert calls == ["executed"]
    assert [item.stage for item in result.receipts] == [
        "ingestion",
        "steggate",
        "return_ingestion",
    ]
    assert result.manifest.metadata["parallel_evaluator_used"] is False
