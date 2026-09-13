from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json

from stegcore.cge_decision_issuer import issue_service_decision, sha256


def route() -> dict:
    return {
        "request_id": "CONTROL-PLANE-SOURCE-PACKAGE-1",
        "request_sha256": "1" * 64,
        "route_sha256": "2" * 64,
        "service_id": "stegverse-sovereign-relay",
        "provider": {"provider_id": "tvc"},
    }


def authority(r: dict) -> dict:
    value = {
        "request_id": r["request_id"],
        "request_sha256": r["request_sha256"],
        "route_sha256": r["route_sha256"],
        "service_id": r["service_id"],
        "provider_id": "tvc",
        "authority_valid": True,
        "authority_refs": ["TVC:relay-authority"],
    }
    value["authority_evidence_sha256"] = sha256(value)
    return value


def request(*, policy_current: bool = True) -> dict:
    return {
        "candidate": {
            "actor_class": "system",
            "action": "stegverse-sovereign-relay",
            "target": "stegverse.control-plane",
            "scope": "source-package-transport",
            "parameters": {"opaque_payload": True},
        },
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": ["evidence:relay-request"],
        },
        "signal": {
            "admitted_signal_refs": ["signal:content-addressed-package"],
            "excluded_signal_refs": [],
            "transformations": ["exact-byte-package:v1"],
            "missing_inputs": [],
            "uncertainty_state": "bounded",
            "reference_state_hash": "state:relay-ready",
            "expected_reference_state_hash": "state:relay-ready",
            "reconstruction_available": True,
            "transformation_provenance_complete": True,
        },
        "execution": {
            "actor_authority_current": True,
            "policy_current": policy_current,
            "delegation_current": True,
            "evidence_current": True,
            "affected_entity_conditions_represented": True,
            "recoverability_profile": "recoverable",
            "validity_window_open": True,
            "policy_ref": "policy:sovereign-relay-source-package",
            "delegation_ref": "delegation:tvc-relay",
            "evidence_refs": ["execution:relay-binding"],
        },
        "capability": {"allowed": True},
        "continuity": {
            "required": True,
            "previous_receipt_verified": True,
            "previous_receipt_hash": "receipt:prior-relay-state",
        },
        "approval": {"required": False, "valid": None, "candidate_hash": None},
        "permission_present": True,
    }


def test_allow_issues_tvc_bindable_cge_decision_without_execution() -> None:
    r = route()
    a = authority(r)
    result = issue_service_decision(
        route=r,
        authority_evidence=a,
        admissibility_request=request(),
        subject_request_ref="runtime://control-plane-source-package/1",
        repository_state_sha256="a" * 64,
        now=datetime(2026, 9, 13, 23, 0, tzinfo=timezone.utc),
    )
    decision = result["cge_decision"]
    assert result["state"] == "CGE_REVIEW_ACCEPTED"
    assert decision["admissibility"] == "ADMIT"
    assert decision["execution_scope"] == ["stegverse-sovereign-relay"]
    assert decision["authority_evidence_sha256"] == a["authority_evidence_sha256"]
    assert decision["decision_sha256"] == sha256({k: v for k, v in decision.items() if k != "decision_sha256"})
    assert result["commit_time_admissibility_receipt"]["decision"] == "PROCEED"
    assert result["authority_context_receipt"]["execution_authority_granted"] is False
    assert result["execution_performed"] is False
    assert result["canonical_state_mutated"] is False
    assert result["transition_executor"] == "Interlock/InTr"


def test_policy_failure_denies_without_execution_scope() -> None:
    r = route()
    result = issue_service_decision(
        route=r,
        authority_evidence=authority(r),
        admissibility_request=request(policy_current=False),
        subject_request_ref="runtime://control-plane-source-package/1",
        repository_state_sha256="b" * 64,
        now=datetime(2026, 9, 13, 23, 0, tzinfo=timezone.utc),
    )
    assert result["state"] == "CGE_REVIEW_DENIED"
    assert result["cge_decision"]["admissibility"] == "DENY"
    assert result["cge_decision"]["execution_scope"] == []
    assert result["commit_time_admissibility_receipt"]["decision"] == "DENY"


def test_invalid_authority_evidence_fails_closed_before_evaluation() -> None:
    r = route()
    a = authority(r)
    a["authority_valid"] = False
    a["authority_evidence_sha256"] = sha256({k: v for k, v in a.items() if k != "authority_evidence_sha256"})
    try:
        issue_service_decision(
            route=r,
            authority_evidence=a,
            admissibility_request=request(),
            subject_request_ref="runtime://control-plane-source-package/1",
            repository_state_sha256="c" * 64,
        )
    except ValueError as exc:
        assert "authority_evidence_not_valid" in str(exc)
    else:
        raise AssertionError("invalid authority evidence must fail closed")
