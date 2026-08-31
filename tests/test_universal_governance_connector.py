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
    VerifiedTransportBindings,
    evaluate_governance_connector,
    parse_governance_connector_request,
    parse_registered_governance_connector_request,
    resolve_governance_connector_profile,
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
            "intr_profile_ref": "governance-external-action",
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


def registry():
    return {
        "schema_version": "stegverse.governance-connector-registry.v1",
        "state": "DEFINED_SOURCE_ONLY",
        "credential_authority": "TV/TVC",
        "authority_effect": "NONE",
        "profiles": [profile()],
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
        intr_profile_ref="governance-external-action",
        governed_transition_profile_ref="steggate.transition.v1",
        carrier_profile_ref="heartbeat-derived-intr.v1",
        authority_ref="authority:1",
        intent_ref="intent:1",
        candidate_ref="candidate:1",
        candidate_hash="sha256:1111111111111111111111111111111111111111111111111111111111111111",
        evidence_refs=("evidence:1",),
        three_layer_request=tl or three_layer(),
    )


def serialized_payload():
    return {
        "schema_version": "stegverse.governance-connector.request/v1",
        "profile_id": "example.external-system.v1",
        "operation_id": "execute",
        "system_id": "external-system.example",
        "boundary_id": "interlock:external-system.example",
        "authority_ref": "authority:1",
        "intent_ref": "intent:1",
        "candidate_ref": "candidate:1",
        "candidate_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
        "evidence_refs": ["evidence:1"],
        "resolved_facts": {
            "judgment_conditions": {
                "refusal_available": True,
                "operator_recoverability": "available",
                "workload_state": "supported",
                "time_pressure": "normal",
                "isolation_state": "supported",
                "evidence_refs": ["judgment:1"],
            },
            "signal_admission": {
                "admitted_signal_refs": ["signal:1"],
                "excluded_signal_refs": [],
                "transformations": ["canonicalize"],
                "missing_inputs": [],
                "uncertainty_state": "bounded",
                "reference_state_hash": "state:abc",
                "expected_reference_state_hash": "state:abc",
                "reconstruction_available": True,
                "transformation_provenance_complete": True,
            },
            "execution_boundary": {
                "actor_authority_current": True,
                "policy_current": True,
                "delegation_current": True,
                "evidence_current": True,
                "affected_entity_conditions_represented": True,
                "recoverability_profile": "recoverable",
                "validity_window_open": True,
                "policy_ref": "policy.external-system.execute.v1",
                "delegation_ref": "delegation:1",
                "evidence_refs": ["execution:1"],
            },
        },
    }


def transport_bindings():
    return VerifiedTransportBindings(
        interlock_exchange_id="exchange:1",
        intr_packet_id="intr:packet:1",
        intr_profile_ref="governance-external-action",
        governed_transition_profile_ref="steggate.transition.v1",
        carrier_profile_ref="heartbeat-derived-intr.v1",
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


    def test_serialized_request_parses_and_evaluates(self):
        parsed = parse_governance_connector_request(profile(), serialized_payload(), transport_bindings())
        self.assertEqual(parsed.intr_profile_ref, "governance-external-action")
        self.assertEqual(parsed.interlock_exchange_id, "exchange:1")
        result = evaluate_governance_connector(profile(), parsed)
        self.assertEqual(result.decision, "ALLOW")
        self.assertFalse(result.execution_authority_granted)

    def test_payload_cannot_self_assert_transport_bindings(self):
        payload = serialized_payload()
        payload["intr_packet_id"] = "forged"
        with self.assertRaisesRegex(ValueError, "request_field_set_invalid"):
            parse_governance_connector_request(profile(), payload, transport_bindings())

    def test_verified_transport_binding_mismatch_is_rejected(self):
        tb = VerifiedTransportBindings(
            interlock_exchange_id="exchange:1",
            intr_packet_id="intr:packet:1",
            intr_profile_ref="wrong",
            governed_transition_profile_ref="steggate.transition.v1",
            carrier_profile_ref="heartbeat-derived-intr.v1",
        )
        with self.assertRaisesRegex(ValueError, "intr_profile_mismatch"):
            parse_governance_connector_request(profile(), serialized_payload(), tb)

    def test_serialized_policy_drift_is_rejected(self):
        payload = serialized_payload()
        payload["resolved_facts"]["execution_boundary"]["policy_ref"] = "policy.wrong"
        with self.assertRaisesRegex(ValueError, "policy_ref_mismatch"):
            parse_governance_connector_request(profile(), payload, transport_bindings())

    def test_invalid_candidate_hash_is_rejected(self):
        payload = serialized_payload()
        payload["candidate_hash"] = "sha256:bad"
        with self.assertRaisesRegex(ValueError, "candidate_hash_invalid"):
            parse_governance_connector_request(profile(), payload, transport_bindings())


    def test_registry_resolves_profile_and_registered_request(self):
        resolved = resolve_governance_connector_profile(registry(), "example.external-system.v1")
        self.assertEqual(resolved["profile_id"], "example.external-system.v1")
        resolved_profile, parsed = parse_registered_governance_connector_request(
            registry(), serialized_payload(), transport_bindings()
        )
        self.assertEqual(resolved_profile["profile_id"], "example.external-system.v1")
        self.assertEqual(evaluate_governance_connector(resolved_profile, parsed).decision, "ALLOW")

    def test_registry_unknown_profile_and_duplicates_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "registry_profile_unknown"):
            resolve_governance_connector_profile(registry(), "unknown.profile")
        dup = registry()
        dup["profiles"].append(profile())
        with self.assertRaisesRegex(ValueError, "registry_profile_duplicate"):
            resolve_governance_connector_profile(dup, "example.external-system.v1")

    def test_registry_cannot_change_authority_or_credentials(self):
        bad = registry()
        bad["authority_effect"] = "EXECUTE"
        with self.assertRaisesRegex(ValueError, "registry_authority_effect_invalid"):
            resolve_governance_connector_profile(bad, "example.external-system.v1")
        bad = registry()
        bad["credential_authority"] = "PROVIDER"
        with self.assertRaisesRegex(ValueError, "registry_credential_authority_mismatch"):
            resolve_governance_connector_profile(bad, "example.external-system.v1")


if __name__ == "__main__":
    unittest.main()
