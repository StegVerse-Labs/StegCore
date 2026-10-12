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
from stegcore.transaction_discovery import DiscoveryQuery, TransactionDiscoveryIndex
from stegcore.transaction_lifecycle import run_manifested_transaction


def request_all_pass() -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="system",
            action="write_record",
            target="review-finding",
            scope="evaluation",
            parameters={"finding": "boundary-observation"},
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


def make_result():
    return run_manifested_transaction(
        request_all_pass(),
        lambda: {"record": "written"},
        input_data={"secret_payload": "must-not-be-indexed"},
        source="sdk:review",
        subject="reviewer:mansoor",
        processing_capability="governance",
        route_id="stegverse.route.canonical-governed.v1",
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )


def test_discovery_index_persists_and_reloads_without_payload(tmp_path):
    path = tmp_path / "discovery.jsonl"
    result = make_result()
    index = TransactionDiscoveryIndex(path)
    record = index.register(
        result,
        finding_refs=["finding:M-001"],
        remediation_refs=["remediation:R-001"],
        verification_refs=["verification:V-001"],
    )

    assert record.payload_disclosed is False
    assert record.discovery_grants_authority is False
    assert "secret_payload" not in record.model_dump_json()

    reloaded = TransactionDiscoveryIndex(path)
    found = reloaded.get(result.transaction_id)
    assert found is not None
    assert found.record_hash == record.record_hash
    assert found.receipt_chain_head == result.replay.receipt_chain_head


def test_discovery_queries_find_transaction_by_runtime_state_and_finding(tmp_path):
    result = make_result()
    index = TransactionDiscoveryIndex(tmp_path / "discovery.jsonl")
    index.register(result, finding_refs=["finding:M-001"])

    assert len(index.query(transaction_id=result.transaction_id)) == 1
    assert len(index.query(state="ALLOW")) == 1
    assert len(index.query(stage="return_ingestion")) == 1
    assert len(index.query(finding_ref="finding:M-001")) == 1
    assert len(index.query(DiscoveryQuery(runtime_identity="governance@stegverse.route.canonical-governed.v1"))) == 1
    assert index.query(finding_ref="finding:missing") == []


def test_safe_summary_contains_discovery_metadata_not_payload(tmp_path):
    result = make_result()
    index = TransactionDiscoveryIndex(tmp_path / "discovery.jsonl")
    index.register(result, finding_refs=["finding:M-001"])

    summary = index.safe_summary(result.transaction_id)
    assert summary is not None
    assert summary["transaction_id"] == result.transaction_id
    assert summary["payload_disclosed"] is False
    assert summary["discovery_grants_authority"] is False
    assert "secret_payload" not in str(summary)
    assert summary["finding_refs"] == ["finding:M-001"]


def test_duplicate_registration_is_idempotent_only_for_same_chain(tmp_path):
    result = make_result()
    index = TransactionDiscoveryIndex(tmp_path / "discovery.jsonl")
    first = index.register(result)
    second = index.register(result)
    assert first.record_hash == second.record_hash
    assert len(index.records()) == 1
