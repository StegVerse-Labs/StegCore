from __future__ import annotations

import json
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
    canonical_sha256,
    evaluate_admissibility,
)

ROOT = Path(__file__).resolve().parents[1]
ORIGINATION = ROOT / "examples/governance_lanes/agency_state_relative/origination_manifest.json"
RESULTANT = ROOT / "examples/governance_lanes/agency_state_relative/resultant_manifest.json"


def request(*, action: str, state_hash: str, expected_state_hash: str, human_direction: str) -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="human_governed",
            action=action,
            target="operative_path:agency-demo",
            scope="AGENCY-STATE-RELATIVE-001",
            parameters={"human_direction": human_direction},
        ),
        judgment=JudgmentState(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=["evidence:human-direction"],
        ),
        signal=SignalState(
            admitted_signal_refs=["signal:operative-state"],
            transformations=["state-relative-governance:v1"],
            missing_inputs=[],
            uncertainty_state="bounded",
            reference_state_hash=state_hash,
            expected_reference_state_hash=expected_state_hash,
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
            policy_ref="policy:agency:v1",
            delegation_ref="delegation:human:v1",
            evidence_refs=["execution:agency-demo"],
        ),
        capability=CapabilityState(allowed=True),
        continuity=ContinuityState(
            required=True,
            previous_receipt_verified=True,
            previous_receipt_hash="receipt:agency:previous",
        ),
        approval=ApprovalState(required=False),
        permission_present=True,
        declared_context={"lane_id": "AGENCY-STATE-RELATIVE-001"},
    )


def pack(case_id: str, state_id: str, evaluation, consequence: str) -> dict:
    return {
        "case_id": case_id,
        "state_id": state_id,
        "disposition": evaluation.disposition,
        "reasons": evaluation.reasons,
        "candidate_hash": evaluation.candidate_hash,
        "canonical_three_layer_decision": evaluation.canonical_three_layer_decision,
        "canonical_three_layer_reason": evaluation.canonical_three_layer_reason,
        "canonical_three_layer_request_hash": evaluation.canonical_three_layer_request_hash,
        "canonical_three_layer_receipt_hash": evaluation.canonical_three_layer_receipt_hash,
        "decision_state_hash": evaluation.decision_state_hash,
        "evaluated_at": evaluation.evaluated_at,
        "continuity_receipt_minted": evaluation.continuity_receipt_minted,
        "external_execution_performed": evaluation.external_execution_performed,
        "consequence": consequence,
        "predicate_matrix": [row.model_dump(mode="json") for row in evaluation.matrix],
    }


def run_lane() -> dict:
    origination = json.loads(ORIGINATION.read_text())

    s0 = evaluate_admissibility(
        request(
            action="execute_authorized_path",
            state_hash="state:agency:S0",
            expected_state_hash="state:agency:S0",
            human_direction="PROCEED",
        )
    )
    assert s0.disposition == "ALLOW"

    stale = evaluate_admissibility(
        request(
            action="execute_authorized_path_using_S0_basis",
            state_hash="state:agency:S1",
            expected_state_hash="state:agency:S0",
            human_direction="PROCEED_FROM_S0_RECORD",
        )
    )
    assert stale.disposition in {"DENY", "FAIL_CLOSED"}

    redirect = evaluate_admissibility(
        request(
            action="refuse_and_redirect_for_renewed_determination",
            state_hash="state:agency:S1",
            expected_state_hash="state:agency:S1",
            human_direction="REFUSE_AND_REDIRECT",
        )
    )
    assert redirect.disposition == "ALLOW"

    transitions = [
        {
            "transition_id": "T-S0-ALLOW",
            "from": "S0:authorization-recorded",
            "to": "S0:authorized-path-admissible",
            "trigger": "canonical evaluation",
            "receipt_hash": s0.canonical_three_layer_receipt_hash,
        },
        {
            "transition_id": "T-S0-S1",
            "from": "S0",
            "to": "S1",
            "trigger": "governance-relevant reference-state and human-direction change",
            "effect": "historical record preserved; applicability reopened",
        },
        {
            "transition_id": "T-S1-STALE-BLOCK",
            "from": "S1:attempt-prior-basis",
            "to": "S1:prior-basis-not-admissible",
            "trigger": stale.canonical_three_layer_reason,
            "receipt_hash": stale.canonical_three_layer_receipt_hash,
        },
        {
            "transition_id": "T-S1-HUMAN-REDIRECT",
            "from": "S1:prior-path-blocked",
            "to": "S1:renewed-determination-path",
            "trigger": "current human direction received through admissible governed path",
            "receipt_hash": redirect.canonical_three_layer_receipt_hash,
        },
    ]

    result = {
        "artifact_type": "stegverse.governance_lane.resultant_manifest",
        "schema_version": "1.0",
        "lane_id": origination["lane_id"],
        "origination_manifest_hash": canonical_sha256(origination),
        "canonical_evaluator": "stegcore.steggate.evaluate_admissibility",
        "result": "PASS",
        "cases": [
            pack("CASE-1-HISTORICAL-VALIDITY", "S0", s0, "HISTORICAL_AUTHORIZATION_VALID_IN_S0"),
            pack("CASE-2-STALE-APPLICABILITY", "S1", stale, "PRIOR_AUTHORIZATION_NOT_APPLICABLE_WITHOUT_RENEWED_DETERMINATION"),
            pack("CASE-3-CONSEQUENTIAL-AGENCY", "S1", redirect, "OPERATIVE_PATH_REDIRECTED_TO_RENEWED_DETERMINATION"),
        ],
        "transitions": transitions,
        "consequence": {
            "historical_record": "PRESERVED",
            "historical_authorization_status": "VALID_AS_S0_EVIDENCE",
            "present_applicability": "REQUIRES_RENEWED_DETERMINATION_AFTER_S0_TO_S1",
            "human_direction": "REFUSE_AND_REDIRECT",
            "human_direction_effect": "MATERIAL_OPERATIVE_PATH_CHANGE",
            "final_operational_state": "RENEWED_DETERMINATION_REQUIRED",
        },
        "claims_demonstrated": {
            "time_indexes_record_state_sets_governance_boundary": True,
            "historical_validity_not_present_applicability": True,
            "recording_not_sufficient_for_agency": True,
            "current_human_direction_can_change_permitted_path": True,
        },
        "authority_boundary": {
            "continuity_receipts_minted_by_steggate": False,
            "external_execution_performed": False,
            "test_consequence_is_governance_path_selection": True,
        },
    }
    result["resultant_manifest_hash"] = canonical_sha256(result)
    return result


def main() -> None:
    result = run_lane()
    RESULTANT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
