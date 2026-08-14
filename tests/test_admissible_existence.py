from stegcore.admissible_existence import (
    CapabilityExistenceDeclaration,
    CapabilityExistenceTransition,
    evaluate_capability_existence,
)
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


def _allow_request(target: str) -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(actor_class="worker", action="advance", target=target),
        judgment=JudgmentState(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=["e:j"],
        ),
        signal=SignalState(
            admitted_signal_refs=["e:s"],
            missing_inputs=[],
            uncertainty_state="bounded",
            reference_state_hash="state-1",
            expected_reference_state_hash="state-1",
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
            policy_ref="policy:v1",
            delegation_ref="delegation:v1",
            evidence_refs=["e:x"],
        ),
        capability=CapabilityState(allowed=True),
        continuity=ContinuityState(required=False),
        approval=ApprovalState(required=False),
        permission_present=True,
    )


def _declaration() -> CapabilityExistenceDeclaration:
    return CapabilityExistenceDeclaration(
        capability_id="stegverse:capability:example:v1",
        capability_version="1.0.0",
        owner_repository="StegVerse-Labs/StegCore",
        purpose="prove structural capability growth",
    )


def test_existence_hash_is_deterministic():
    assert _declaration().existence_hash == _declaration().existence_hash


def test_declared_to_standing_advances_only_after_canonical_allow_and_standing_proof():
    declaration = _declaration()
    result = evaluate_capability_existence(
        CapabilityExistenceTransition(
            declaration=declaration,
            from_phase="DECLARED",
            target_phase="STANDING",
            admissibility=_allow_request(declaration.capability_id),
            standing_verified=True,
        )
    )
    assert result.canonical_disposition == "ALLOW"
    assert result.lifecycle_outcome == "ADVANCED"
    assert result.resulting_phase == "STANDING"
    assert result.transition_admitted is True
    assert result.external_execution_performed is False
    assert result.continuity_receipt_minted is False


def test_candidate_must_bind_to_exact_existence():
    declaration = _declaration()
    result = evaluate_capability_existence(
        CapabilityExistenceTransition(
            declaration=declaration,
            from_phase="DECLARED",
            target_phase="STANDING",
            admissibility=_allow_request("different-capability"),
            standing_verified=True,
        )
    )
    assert result.canonical_disposition == "ALLOW"
    assert result.lifecycle_outcome == "BLOCKED_STRUCTURE"
    assert "candidate_target_not_bound_to_capability_existence" in result.structural_reasons


def test_activation_requires_integration_and_proof():
    declaration = _declaration()
    result = evaluate_capability_existence(
        CapabilityExistenceTransition(
            declaration=declaration,
            from_phase="ADMISSIBLE",
            target_phase="ACTIVATED",
            admissibility=_allow_request(declaration.capability_id),
        )
    )
    assert result.lifecycle_outcome == "BLOCKED_STRUCTURE"
    assert set(result.structural_reasons) >= {"integration_not_verified", "activation_proof_missing"}


def test_activation_advances_with_required_proof():
    declaration = _declaration()
    result = evaluate_capability_existence(
        CapabilityExistenceTransition(
            declaration=declaration,
            from_phase="ADMISSIBLE",
            target_phase="ACTIVATED",
            admissibility=_allow_request(declaration.capability_id),
            integration_verified=True,
            activation_proof_ref="receipt:activation:1",
        )
    )
    assert result.lifecycle_outcome == "ADVANCED"
    assert result.resulting_phase == "ACTIVATED"
    assert result.credential_authority == "TV/TVC"
    assert result.github_token_runtime_authority is False
