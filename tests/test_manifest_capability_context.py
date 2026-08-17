from __future__ import annotations

import pytest

from stegcore.admissible_existence import CapabilityExistenceDeclaration
from stegcore.capability_registry import (
    CapabilityExistenceRegistry,
    CapabilityPhaseEvidence,
    CapabilityRegistryEntry,
)
from stegcore.manifest_capability_context import (
    resolve_manifest_capability_context,
)
from stegcore.manifest_receipts import ManifestReceiptRegistry
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
from stegcore.transaction_lifecycle import run_manifested_transaction


def _registry(*, phase: str = "ACTIVATED") -> CapabilityExistenceRegistry:
    declaration = CapabilityExistenceDeclaration(
        capability_id="stegverse:capability:test:v1",
        capability_version="1.0.0",
        owner_repository="StegVerse-Labs/StegCore",
        purpose="test manifested AE capability resolution",
    )
    evidence = CapabilityPhaseEvidence(
        standing_evidence_refs=["test:standing"],
        admissibility_evidence_refs=["test:admissibility"],
        integration_evidence_refs=["test:integration"] if phase == "ACTIVATED" else [],
        activation_proof_ref="test:activation" if phase == "ACTIVATED" else None,
        blockers=[] if phase == "ACTIVATED" else ["TEST_NOT_ACTIVATED"],
        continuation_owner="StegVerse-Labs/StegCore",
    )
    return CapabilityExistenceRegistry(
        entries=[
            CapabilityRegistryEntry(
                declaration=declaration,
                existence_hash=declaration.existence_hash,
                phase=phase,
                evidence=evidence,
            )
        ]
    )


def _allowed_request() -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="system",
            action="write_record",
            target="manifest-capability-context-test",
            scope="evaluation",
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


def _runtime_kwargs() -> dict:
    return {
        "capability_surface": {
            "actions_exposed": ["write_record"],
            "execution_mode": "manual",
            "requires_governed_commit": True,
        },
        "authority_resolution": {
            "status": "approved",
            "basis_invalidated_by_action": False,
        },
    }


def test_resolver_uses_registry_state_and_never_grants_authority():
    context = resolve_manifest_capability_context(
        _registry(),
        [{"capability_id": "stegverse:capability:test:v1", "required_phase": "ACTIVATED"}],
    )
    assert context.all_required_phases_satisfied is True
    assert context.grants_authority is False
    assert context.caller_phase_claims_authoritative is False
    resolved = context.resolved_capabilities[0]
    assert resolved.existence_phase == "ACTIVATED"
    assert resolved.activation_proof_ref == "test:activation"
    assert resolved.credential_authority == "TV/TVC"
    assert resolved.github_token_runtime_authority is False
    assert resolved.resolution_grants_authority is False


def test_unknown_capability_fails_closed():
    with pytest.raises(ValueError, match="capability_not_found"):
        resolve_manifest_capability_context(
            _registry(),
            [{"capability_id": "stegverse:capability:missing:v1"}],
        )


def test_required_activation_cannot_be_asserted_over_admissible_registry_state():
    calls: list[str] = []
    with pytest.raises(ValueError, match="capability_required_phase_not_satisfied"):
        run_manifested_transaction(
            _allowed_request(),
            lambda: calls.append("executed"),
            input_data={"value": 1},
            source="sdk:test",
            subject="capability-context",
            capability_registry=_registry(phase="ADMISSIBLE"),
            requested_capabilities=[
                {"capability_id": "stegverse:capability:test:v1", "required_phase": "ACTIVATED"}
            ],
            **_runtime_kwargs(),
        )
    assert calls == []


def test_manifested_run_receipts_canonical_capability_context():
    result = run_manifested_transaction(
        _allowed_request(),
        lambda: {"written": True},
        input_data={"value": 1},
        source="sdk:test",
        subject="capability-context",
        capability_registry=_registry(),
        requested_capabilities=[
            {"capability_id": "stegverse:capability:test:v1", "required_phase": "ACTIVATED"}
        ],
        **_runtime_kwargs(),
    )
    assert result.chain_verified is True
    assert result.capability_context is not None
    context_hash = result.capability_context.context_hash
    assert result.receipts[0].details["capability_context_hash"] == context_hash
    assert result.receipts[0].details["capability_resolution_grants_authority"] is False
    assert result.receipts[1].details["capability_context_hash"] == context_hash
    assert result.receipts[2].details["capability_context_hash"] == context_hash
    assert result.replay.capability_context_hash == context_hash


def test_exact_run_package_and_reconstruction_preserve_original_capability_state():
    result = run_manifested_transaction(
        _allowed_request(),
        lambda: {"written": True},
        input_data={"value": 1},
        source="sdk:test",
        subject="capability-context",
        capability_registry=_registry(),
        requested_capabilities=[{"capability_id": "stegverse:capability:test:v1"}],
        **_runtime_kwargs(),
    )
    registry = ManifestReceiptRegistry()
    record = registry.register(result)
    package = registry.evidence_package(record.manifest_receipt_id)
    assert package["capability_context"]["context_hash"] == result.capability_context.context_hash
    assert package["capability_context"]["resolved_capabilities"][0]["existence_phase"] == "ACTIVATED"

    reconstruction = registry.reconstruct(record.manifest_receipt_id)
    summary = reconstruction.reconstructed_summary
    assert summary["capability_context_hash"] == result.capability_context.context_hash
    assert summary["capability_state_is_original_run_evidence"] is True
    assert summary["current_capability_state_substituted"] is False
    assert reconstruction.consequence_reexecuted is False
