from __future__ import annotations

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
from stegcore.transaction_lifecycle import (
    TransactionLedger,
    manifest_transaction,
    run_manifested_transaction,
)


def allowed_request(amount: int = 420) -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="system",
            action="write_record",
            target="vendor-payment",
            scope="evaluation",
            parameters={"amount": amount, "currency": "USD"},
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
            transformations=["canonicalize:v1"],
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


def test_manifest_declares_route_but_never_grants_authority():
    request = allowed_request()
    manifest = manifest_transaction(
        request,
        {"payment": 420},
        source="sdk:test",
        subject="evaluation:eduardo",
    )
    assert manifest.manifest_grants_authority is False
    assert manifest.declared_route == [
        "sdk",
        "ingestion",
        "steggate",
        "return_ingestion",
        "sdk_output",
    ]
    assert manifest.candidate_hash
    assert manifest.request_hash
    assert manifest.manifest_hash


def test_manifest_rejects_test_route_that_bypasses_ingestion():
    request = allowed_request()
    try:
        manifest_transaction(
            request,
            {"payment": 420},
            source="sdk:test",
            subject="evaluation:eduardo",
            declared_route=("sdk", "steggate", "return_ingestion"),
        )
    except ValueError as exc:
        assert "ingestion" in str(exc)
    else:
        raise AssertionError("manifest must reject an ingestion bypass")


def test_normal_manifested_allow_traverses_canonical_runtime_and_returns():
    ledger = TransactionLedger()
    calls: list[str] = []

    result = run_manifested_transaction(
        allowed_request(),
        lambda: calls.append("executed") or {"payment": "committed"},
        input_data={"payment": 420},
        source="sdk:test",
        subject="evaluation:eduardo",
        ledger=ledger,
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )

    assert result.chain_verified is True
    assert result.execution_observation["status"] == "executed"
    assert result.execution_observation["executor_invoked"] is True
    assert calls == ["executed"]
    assert [receipt.stage for receipt in result.receipts] == [
        "ingestion",
        "steggate",
        "return_ingestion",
    ]
    assert result.receipts[1].processor == "stegcore.steggate_runtime.governed_steggate_execute"
    assert result.replay.receipt_count == 3
    assert result.replay.expected_disposition == "ALLOW"
    assert result.replay.expected_executor_invoked is True


def test_prior_validity_can_remain_replayable_while_current_execution_is_refused():
    ledger = TransactionLedger()

    t0 = run_manifested_transaction(
        allowed_request(),
        lambda: {"payment": "committed"},
        input_data={"payment": 420, "phase": "t0"},
        source="sdk:test",
        subject="evaluation:eduardo",
        ledger=ledger,
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )
    assert t0.replay.expected_disposition == "ALLOW"
    assert t0.execution_observation["executor_invoked"] is True

    t1_request = allowed_request()
    t1_request.execution.policy_current = False
    calls: list[str] = []
    t1 = run_manifested_transaction(
        t1_request,
        lambda: calls.append("executed"),
        input_data={"payment": 420, "phase": "t1", "policy_current": False},
        source="sdk:test",
        subject="evaluation:eduardo",
        ledger=ledger,
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )

    assert t1.replay.expected_disposition == "DENY"
    assert t1.execution_observation["executor_invoked"] is False
    assert calls == []
    assert t0.transaction_id != t1.transaction_id
    assert t0.chain_verified and t1.chain_verified

    reconstructed_t0 = ledger.reconstruct(t0.transaction_id)
    reconstructed_t1 = ledger.reconstruct(t1.transaction_id)
    assert reconstructed_t0["chain_verified"] is True
    assert reconstructed_t1["chain_verified"] is True
    assert reconstructed_t0["states"][1]["state"] == "ALLOW"
    assert reconstructed_t1["states"][1]["state"] == "DENY"


def test_candidate_mutation_breaks_prior_approval_binding_without_erasing_prior_receipt():
    first = allowed_request(420)
    from stegcore.steggate import evaluate_admissibility

    original = evaluate_admissibility(first)
    first.approval.required = True
    first.approval.valid = True
    first.approval.candidate_hash = original.candidate_hash

    allowed = run_manifested_transaction(
        first,
        lambda: {"payment": "committed"},
        input_data={"payment": 420},
        source="sdk:test",
        subject="evaluation:eduardo",
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )
    assert allowed.replay.expected_disposition == "ALLOW"

    changed = allowed_request(4200)
    changed.approval.required = True
    changed.approval.valid = True
    changed.approval.candidate_hash = original.candidate_hash
    calls: list[str] = []
    denied = run_manifested_transaction(
        changed,
        lambda: calls.append("executed"),
        input_data={"payment": 4200},
        source="sdk:test",
        subject="evaluation:eduardo",
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )

    assert denied.replay.expected_disposition == "DENY"
    assert denied.execution_observation["executor_invoked"] is False
    assert calls == []
    assert allowed.manifest.candidate_hash != denied.manifest.candidate_hash
