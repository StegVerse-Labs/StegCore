from __future__ import annotations

from copy import deepcopy
import unittest

from stegcore.three_layer import (
    ExecutionBoundary,
    JudgmentConditions,
    SignalAdmission,
    ThreeLayerRequest,
)
from stegcore.universal_governance_connector import (
    GovernanceConnectorRequest,
    evaluate_governance_connector,
)


def profile():
    return {
        "schema_version": "stegverse.governance-connector-profile.v1",
        "profile_id": "example.external-system.v1",
        "profile_version": "1.0.0",
        "system": {
            "system_id": "external-system.example",
            "system_kind": "EXTERNAL_API",
            "boundary_id": "interlock:external-system.example",
            "enforcement_class": "ENFORCED",
            "bypass_path_declared": False,
        },
        "interlock": {
            "required": True,
            "intr_profile_ref": "stegos.universal-intr.external-system.v1",
            "governed_transition_profile_ref": "steggate.transition.v1",
            "carrier_profile_ref": "heartbeat-derived-intr.v1",
            "fail_closed_on_binding_error": True,
        },
        "runtime": {
            "evaluator_ref": "stegcore.three_layer.evaluate_three_layer",
            "decision_surface": ["ALLOW", "DENY", "FAIL-CLOSED"],
            "execution_requires_separate_authority": True,
        },
        "operations": [{
            "operation_id": "execute",
            "action_class": "EXECUTE",
            "policy_ref": "policy.external-system.execute.v1",
            "required_governance_classes": ["G0","G1","G2","G3","G4","G5"],
            "required_admissibility_stages": ["A0","A1","A2","A3","A4","A5","A6","A7","A8"],
            "authority_ref_required": True,
            "evidence_refs_required": True,
            "reversibility": "compensable",
            "protected_consequence": True,
            "bypass_disposition": "FAIL_CLOSED",
        }],
        "evidence": {
            "ingress_receipt_required": True,
            "decision_receipt_required": True,
            "egress_receipt_required": True,
            "reconstruction_required": True,
            "master_records_projection": True,
        },
        "authority_boundaries": {
            "profile_grants_execution_authority": False,
            "interlock_grants_execution_authority": False,
            "intr_grants_execution_authority": False,
            "carrier_grants_execution_authority": False,
            "governance_allow_grants_credential_authority": False,
            "credential_authority": "TV/TVC",
        },
    }


def three_layer(*, authority=True, policy=True, evidence=True):
    return ThreeLayerRequest(
        judgment_conditions=JudgmentConditions(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=("judgment:1",),
        ),
        signal_admission=SignalAdmission(
            admitted_signal_refs=("signal:1",),
            missing_inputs=(),
            uncertainty_state="bounded",
            reference_state_hash="state:abc",
            expected_reference_state_hash="state:abc",
            reconstruction_available=True,
            transformation_provenance_complete=True,
        ),
        execution_boundary=ExecutionBoundary(
            actor_authority_current=authority,
            policy_current=policy,
            delegation_current=True,
            evidence_current=evidence,
            affected_entity_conditions_represented=True,
            recoverability_profile="compensable" if False else "recoverable",
            validity_window_open=True,
            policy_ref="policy.external-system.execute.v1",
            delegation_ref="delegation:1",
            evidence_refs=("execution:1",),
        ),
        action="EXECUTE",
        target="external-system.example",
        scope="operation:execute",
    )


def request(tl=None):
    return GovernanceConnectorRequest(
        profile_id="example.external-system.v1",
        operation_id="execute",
        system_id="external-system.example",
        boundary_id="interlock:external-system.example",
        interlock_exchange_id="exchange:1",
        intr_packet_id="intr:packet:1",
        intr_profile_ref="stegos.universal-intr.external-system.v1",
        governed_transition_profile_ref="steggate.transition.v1",
        carrier_profile_ref="heartbeat-derived-intr.v1",
        authority_ref="authority:1",
        intent_ref="intent:1",
        candidate_ref="candidate:1",
        evidence_refs=("evidence:1",),
        three_layer_request=tl or three_layer(),
    )


class UniversalGovernanceConnectorTests(unittest.TestCase):
    def test_allow_is_non_authorizing_and_hash_bound(self):
        result = evaluate_governance_connector(profile(), request())
        self.assertEqual(result.decision, "ALLOW")
        self.assertTrue(result.eligible_for_separate_consequence_authorization)
        self.assertFalse(result.execution_authority_granted)
        self.assertEqual(result.credential_authority, "TV/TVC")
        self.assertFalse(result.continuity_receipt_minted)
        self.assertEqual(result.authority_effect, "NONE")
        self.assertEqual(len(result.receipt_hash), 64)
        self.assertIsNotNone(result.three_layer_receipt)
        self.assertFalse(result.three_layer_receipt["continuity_receipt_minted"])

    def test_unknown_operation_fails_closed(self):
        r = request()
        r = GovernanceConnectorRequest(**{**r.__dict__, "operation_id": "delete"})
        result = evaluate_governance_connector(profile(), r)
        self.assertEqual(result.decision, "FAIL-CLOSED")
        self.assertEqual(result.reason_code, "connector.operation_unknown")

    def test_intr_profile_mismatch_fails_closed(self):
        r = request()
        r = GovernanceConnectorRequest(**{**r.__dict__, "intr_profile_ref": "wrong"})
        result = evaluate_governance_connector(profile(), r)
        self.assertEqual(result.decision, "FAIL-CLOSED")
        self.assertEqual(result.reason_code, "connector.intr_profile_mismatch")

    def test_missing_authority_and_evidence_fail_closed(self):
        r = request()
        r = GovernanceConnectorRequest(**{**r.__dict__, "authority_ref": ""})
        self.assertEqual(evaluate_governance_connector(profile(), r).reason_code, "connector.authority_ref_missing")
        r = request()
        r = GovernanceConnectorRequest(**{**r.__dict__, "evidence_refs": ()})
        self.assertEqual(evaluate_governance_connector(profile(), r).reason_code, "connector.evidence_refs_missing")

    def test_policy_mismatch_fails_closed_before_three_layer(self):
        tl = three_layer()
        wrong = ThreeLayerRequest(
            judgment_conditions=tl.judgment_conditions,
            signal_admission=tl.signal_admission,
            execution_boundary=ExecutionBoundary(
                **{**tl.execution_boundary.__dict__, "policy_ref": "policy.wrong"}
            ),
            action=tl.action,
            target=tl.target,
            scope=tl.scope,
        )
        result = evaluate_governance_connector(profile(), request(wrong))
        self.assertEqual(result.decision, "FAIL-CLOSED")
        self.assertEqual(result.reason_code, "connector.policy_ref_mismatch")

    def test_three_layer_deny_propagates_without_execution_authority(self):
        result = evaluate_governance_connector(profile(), request(three_layer(authority=False)))
        self.assertEqual(result.decision, "DENY")
        self.assertEqual(result.reason_code, "execution.authority_stale")
        self.assertFalse(result.eligible_for_separate_consequence_authorization)
        self.assertFalse(result.execution_authority_granted)

    def test_enforced_profile_with_bypass_fails_closed(self):
        p = deepcopy(profile())
        p["system"]["bypass_path_declared"] = True
        result = evaluate_governance_connector(p, request())
        self.assertEqual(result.decision, "FAIL-CLOSED")
        self.assertEqual(result.reason_code, "connector.enforced_bypass_declared")

    def test_carrier_binding_mismatch_fails_closed(self):
        r = request()
        r = GovernanceConnectorRequest(**{**r.__dict__, "carrier_profile_ref": "wrong"})
        result = evaluate_governance_connector(profile(), r)
        self.assertEqual(result.decision, "FAIL-CLOSED")
        self.assertEqual(result.reason_code, "connector.carrier_profile_mismatch")


if __name__ == "__main__":
    unittest.main()
