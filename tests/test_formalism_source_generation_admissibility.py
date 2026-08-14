import json
from pathlib import Path

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

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data" / "formalism-source-generation-admissibility-evaluation.json"
CAPABILITY_ID = "stegverse:capability:formalism-source-generation:v1"
EXISTENCE_HASH = "5d6c4976e69fa958ddacc417195a9c8604a79931fbe0689a3e469e34064690ca"


def _declaration() -> CapabilityExistenceDeclaration:
    return CapabilityExistenceDeclaration(
        capability_id=CAPABILITY_ID,
        capability_version="1.0.0",
        owner_repository="StegVerse-Labs/.github",
        purpose="Least-stable governed local source generation for admitted formalism owner mutations",
        dependencies=[
            "stegverse:capability:steggate:canonical:v1",
            "stegverse:capability:sovereign-local-model:v1",
        ],
        authority={
            "credential_authority": "TV/TVC",
            "github_token_runtime_authority": False,
            "may": [],
            "may_not": [
                "credential_authority",
                "repository_transport_authority",
                "merge_authority",
                "release_authority",
                "wallet_authority",
            ],
        },
        evidence_refs=[
            "StegVerse-Labs/.github#137",
            "commit:eb37e12d63850d820054e2c85c1ff35dc666a2c3",
            "StegVerse-Labs/StegCore#120",
        ],
        metadata={
            "execution_posture": "least_stable_one_shot_or_short_lived",
            "source_packet_schema": "stegverse.owner-source-generation-packet/v0.1",
            "orchestration_owner": "StegVerse-Labs/.github#137",
        },
    )


def _allow_request() -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(actor_class="worker", action="advance", target=CAPABILITY_ID),
        judgment=JudgmentState(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=["StegVerse-Labs/.github#137", "StegVerse-Labs/.github#144"],
        ),
        signal=SignalState(
            admitted_signal_refs=[str(EVIDENCE.relative_to(ROOT))],
            missing_inputs=[],
            uncertainty_state="bounded",
            reference_state_hash=EXISTENCE_HASH,
            expected_reference_state_hash=EXISTENCE_HASH,
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
            policy_ref="docs/ADMISSIBLE_EXISTENCE_CAPABILITY_MODEL_MIRROR_HANDOFF.md",
            delegation_ref="docs/FORMALISM_SOURCE_GENERATION_CAPABILITY_MIRROR_HANDOFF.md",
            evidence_refs=[str(EVIDENCE.relative_to(ROOT))],
        ),
        capability=CapabilityState(allowed=True),
        continuity=ContinuityState(required=False),
        approval=ApprovalState(required=False),
        permission_present=True,
    )


def test_evidence_manifest_preserves_tv_tvc_boundary_and_no_activation_claim():
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert payload["capability_id"] == CAPABILITY_ID
    assert payload["existence_hash"] == EXISTENCE_HASH
    assert payload["standing"]["verified"] is True
    assert payload["activation"]["claimed"] is False
    assert payload["activation"]["activation_proof_ref"] is None
    assert payload["credential_authority"] == "TV/TVC"
    assert payload["non_tv_tvc_secret_or_token_used"] is False
    assert payload["github_token_runtime_authority"] is False


def test_declared_to_standing_is_canonically_admitted_with_current_standing_evidence():
    declaration = _declaration()
    assert declaration.existence_hash == EXISTENCE_HASH
    result = evaluate_capability_existence(
        CapabilityExistenceTransition(
            declaration=declaration,
            from_phase="DECLARED",
            target_phase="STANDING",
            admissibility=_allow_request(),
            standing_verified=True,
            transition_evidence_refs=[str(EVIDENCE.relative_to(ROOT))],
        )
    )
    assert result.canonical_disposition == "ALLOW"
    assert result.lifecycle_outcome == "ADVANCED"
    assert result.resulting_phase == "STANDING"


def test_standing_to_admissible_is_canonically_admitted_without_claiming_activation():
    declaration = _declaration()
    result = evaluate_capability_existence(
        CapabilityExistenceTransition(
            declaration=declaration,
            from_phase="STANDING",
            target_phase="ADMISSIBLE",
            admissibility=_allow_request(),
            transition_evidence_refs=[str(EVIDENCE.relative_to(ROOT))],
        )
    )
    assert result.canonical_disposition == "ALLOW"
    assert result.lifecycle_outcome == "ADVANCED"
    assert result.resulting_phase == "ADMISSIBLE"
    assert result.external_execution_performed is False
    assert result.continuity_receipt_minted is False


def test_activation_remains_blocked_without_live_integration_and_proof():
    declaration = _declaration()
    result = evaluate_capability_existence(
        CapabilityExistenceTransition(
            declaration=declaration,
            from_phase="ADMISSIBLE",
            target_phase="ACTIVATED",
            admissibility=_allow_request(),
            integration_verified=False,
            activation_proof_ref=None,
            transition_evidence_refs=[str(EVIDENCE.relative_to(ROOT))],
        )
    )
    assert result.canonical_disposition == "ALLOW"
    assert result.lifecycle_outcome == "BLOCKED_STRUCTURE"
    assert result.resulting_phase == "ADMISSIBLE"
    assert set(result.structural_reasons) >= {"integration_not_verified", "activation_proof_missing"}
