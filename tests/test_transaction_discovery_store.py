from __future__ import annotations

import sqlite3

import pytest

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
from stegcore.transaction_discovery import DiscoveryQuery, DiscoveryRecord, TransactionDiscoveryIndex
from stegcore.transaction_discovery_store import DiscoveryRecordStore, SqliteDiscoveryStore
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


def make_result():
    return run_manifested_transaction(
        request_all_pass(),
        lambda: {"record": "written"},
        input_data={"secret_payload": "must-not-be-indexed"},
        source="sdk:review",
        subject="reviewer:mansoor",
        capability_surface={
            "actions_exposed": ["write_record"],
            "execution_mode": "manual",
            "requires_governed_commit": True,
        },
        authority_resolution={
            "status": "approved",
            "basis_invalidated_by_action": False,
            "authority_ref": "authority:review-finding",
            "target_binding": "review-finding",
            "valid_from": "2026-01-01T00:00:00+00:00",
            "valid_until": "2027-01-01T00:00:00+00:00",
        },
    )


def make_record() -> DiscoveryRecord:
    result = make_result()
    index = TransactionDiscoveryIndex()
    return index.register(
        result,
        finding_refs=["finding:M-001"],
        remediation_refs=["remediation:R-001"],
        verification_refs=["verification:V-001"],
    )


def test_sqlite_store_satisfies_provider_contract(tmp_path):
    store = SqliteDiscoveryStore(tmp_path / "shared" / "discovery.sqlite3")
    assert isinstance(store, DiscoveryRecordStore)


def test_sqlite_store_persists_across_independent_instances(tmp_path):
    path = tmp_path / "shared.sqlite3"
    record = make_record()
    writer = SqliteDiscoveryStore(path)
    writer.append(record)

    reader = SqliteDiscoveryStore(path)
    loaded = reader.get(record.transaction_id)
    assert loaded is not None
    assert loaded.record_hash == record.record_hash
    assert loaded.receipt_chain_head == record.receipt_chain_head
    assert reader.records() == [record]


def test_sqlite_store_queries_scalar_and_lineage_fields(tmp_path):
    record = make_record()
    store = SqliteDiscoveryStore(tmp_path / "shared.sqlite3")
    store.append(record)

    assert store.query(transaction_id=record.transaction_id) == [record]
    assert store.query(runtime_identity=record.canonical_runtime_identity) == [record]
    assert store.query(stage="return_ingestion") == [record]
    assert store.query(state="ALLOW") == [record]
    assert store.query(finding_ref="finding:M-001") == [record]
    assert store.query(remediation_ref="remediation:R-001") == [record]
    assert store.query(DiscoveryQuery(verification_ref="verification:V-001")) == [record]
    assert store.query(finding_ref="finding:missing") == []


def test_sqlite_store_is_idempotent_for_same_record_and_rejects_rewrite(tmp_path):
    record = make_record()
    store = SqliteDiscoveryStore(tmp_path / "shared.sqlite3")
    first = store.append(record)
    second = store.append(record)
    assert first.record_hash == second.record_hash
    assert len(store.records()) == 1

    altered = record.model_copy(
        update={
            "receipt_chain_head": "different-chain-head",
            "record_hash": record.record_hash,
        }
    )
    with pytest.raises(ValueError, match="record hash mismatch"):
        store.append(altered)


def test_sqlite_store_rejects_payload_or_authority_flags(tmp_path):
    record = make_record()
    store = SqliteDiscoveryStore(tmp_path / "shared.sqlite3")

    payload_record = record.model_copy(update={"payload_disclosed": True})
    with pytest.raises(ValueError):
        store.append(payload_record)

    authority_record = record.model_copy(update={"discovery_grants_authority": True})
    with pytest.raises(ValueError):
        store.append(authority_record)


def test_safe_summary_does_not_disclose_payload(tmp_path):
    record = make_record()
    store = SqliteDiscoveryStore(tmp_path / "shared.sqlite3")
    store.append(record)
    summary = store.safe_summary(record.transaction_id)
    assert summary is not None
    assert summary["payload_disclosed"] is False
    assert summary["discovery_grants_authority"] is False
    assert "secret_payload" not in str(summary)


def test_sqlite_database_uses_wal_for_shared_process_access(tmp_path):
    path = tmp_path / "shared.sqlite3"
    SqliteDiscoveryStore(path)
    connection = sqlite3.connect(path)
    mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
    connection.close()
    assert str(mode).lower() == "wal"
