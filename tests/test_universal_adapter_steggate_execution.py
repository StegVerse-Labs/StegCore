from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
GOV=ROOT/"contracts/universal_governance_connector_snapshot"
STEGOS=ROOT/"contracts/stegos_universal_intr_snapshot"
if str(STEGOS) not in sys.path:
    sys.path.insert(0,str(STEGOS))

from stegos.intr_backbone import connector_from_registry
from stegos.interlock_reference_adapter import build_reference_adapter, validate_reference_adapter

from stegcore.external_governance_adapter import (
    NativeGovernanceAction,
    evaluate_prepared_external_governance_request,
    prepare_external_governance_request,
    validate_external_governance_adapter,
)
from stegcore.external_adapter_steggate_execution import (
    TargetCredentialBinding,
    build_steggate_execution_request,
    execute_external_consequence_if_coherent,
)
from stegcore.universal_governance_connector import VerifiedTransportBindings

INTR_REGISTRY=STEGOS/"specs/universal-intr-connector-profiles.v1.json"
TARGET_BINDING="target:external-system.example:bounded:1"


def load(name):
    return json.loads((GOV/name).read_text(encoding="utf-8"))


def native_action(*, authority_current=True):
    request=load("request.example.json")
    facts=deepcopy(request["resolved_facts"])
    facts["execution_boundary"]["actor_authority_current"]=authority_current
    return NativeGovernanceAction(
        native_operation="native.execute",
        native_action_ref=request["candidate_ref"],
        native_intent_ref=request["intent_ref"],
        native_authority_ref=request["authority_ref"],
        native_parameters={"x":1},
        native_evidence_refs=tuple(request["evidence_refs"]),
        resolved_governance_facts=facts,
        consequence_authority_ref="target-authority:example:execute:1",
    )


def evaluate_native(action):
    adapter=load("external-adapter.example.json")
    registry=load("universal-governance-connector-profiles.v1.json")
    profile=validate_external_governance_adapter(adapter,registry)
    prepared=prepare_external_governance_request(adapter,registry,action)

    connector=connector_from_registry(INTR_REGISTRY,"governance-external-action")
    packet=connector.prepare(
        prepared.payload,
        payload_schema="stegverse.governance-connector.request/v1",
        operation="GOVERN_ACTION",
        operation_id="ADAPTER-STEGGATE-1",
    )
    receipt=connector.accept_hop(
        packet,
        hop_index=1,
        receipt_id="ADAPTER-STEGGATE-INTR-1",
        boundary_identity_ref="StegCore:UniversalGovernanceConnector",
        recorded_at="2026-08-31T18:36:00Z",
        prior_receipt_hash=None,
    )
    complete=connector.validate_complete(packet,[receipt])
    ref=build_reference_adapter(
        mode="COMPAT",
        exchange_id=packet.intent["packet_id"],
        lineage_id="lineage-"+receipt["receipt_hash"][7:31],
        external_system_id=prepared.payload["system_id"],
        external_interface_ref=prepared.payload["boundary_id"],
        wrapper_manifest_ref=packet.intent["packet_id"],
        wrapper_receipt_refs=[receipt["receipt_hash"]],
        correspondence_evidence_refs=[packet.payload_hash],
        master_records_evidence_refs=[receipt["receipt_hash"]],
    )
    validate_reference_adapter(ref)
    transport=VerifiedTransportBindings(
        interlock_exchange_id=ref["exchange_id"],
        intr_packet_id=complete["packet_id"],
        intr_profile_ref=complete["profile_id"],
        governed_transition_profile_ref=profile["interlock"]["governed_transition_profile_ref"],
        carrier_profile_ref=profile["interlock"]["carrier_profile_ref"],
    )
    result=evaluate_prepared_external_governance_request(registry,prepared,transport)
    return adapter,registry,prepared,result


def credential():
    return TargetCredentialBinding(
        credential_id="tvc:credential:example:1",
        credential_hash="sha256:"+"2"*64,
        subject_binding="subject:external-system.example:operator:1",
    )


def authority_resolution(cred=None, **changes):
    cred=cred or credential()
    value={
        "status":"approved",
        "basis_invalidated_by_action":False,
        "authority_ref":"target-authority:example:execute:1",
        "credential_id":cred.credential_id,
        "credential_hash":cred.credential_hash,
        "subject_binding":cred.subject_binding,
        "target_binding":TARGET_BINDING,
        "valid_from":"2026-01-01T00:00:00+00:00",
        "valid_until":"2027-01-01T00:00:00+00:00",
    }
    value.update(changes)
    return value


def build_execution(adapter,registry,prepared,result,**kwargs):
    return build_steggate_execution_request(
        adapter,registry,prepared,result,
        parameters={"x":1},
        credential=credential(),
        target_binding=TARGET_BINDING,
        **kwargs,
    )


class UniversalAdapterStegGateExecutionTests(unittest.TestCase):
    def test_exact_candidate_target_time_and_authority_execute_once(self):
        adapter,registry,prepared,result=evaluate_native(native_action())
        self.assertEqual(result.decision,"ALLOW")
        pe=build_execution(adapter,registry,prepared,result)
        calls=[]
        evidence=execute_external_consequence_if_coherent(
            pe,
            prepared_adapter_request=prepared,
            task_runner=lambda task,payload: calls.append((task,payload)) or {"mutated":True},
            authority_resolution=authority_resolution(),
            evidence_current=True,
        )
        self.assertEqual(evidence.status,"COMPLETED")
        self.assertEqual(calls,[("native.execute",{"x":1})])
        self.assertTrue(evidence.executor_invoked)
        self.assertTrue(evidence.consequence_observed)
        self.assertEqual(evidence.target_binding,TARGET_BINDING)
        self.assertEqual(evidence.present_state_disposition,"ALLOW")
        self.assertTrue(evidence.present_state_checks["authority_current"])
        self.assertTrue(evidence.present_state_checks["target_current"])
        self.assertTrue(evidence.present_state_checks["authority_temporal_current"])
        self.assertTrue(evidence.present_state_checks["evidence_current"])
        self.assertEqual(evidence.candidate_hash,prepared.payload["candidate_hash"])
        self.assertEqual(evidence.governance_receipt_hash,result.receipt_hash)
        self.assertEqual(evidence.intr_packet_id,result.intr_packet_id)
        self.assertEqual(evidence.credential_authority,"TV/TVC")
        self.assertEqual(evidence.adapter_authority_effect,"NONE")
        self.assertEqual(evidence.target_authority_effect,"TARGET_CONSEQUENCE_ONLY")

    def test_same_candidate_ref_with_mutated_parameters_never_reaches_runner(self):
        adapter,registry,prepared,result=evaluate_native(native_action())
        pe=build_execution(adapter,registry,prepared,result)
        bad=deepcopy(dict(pe.execution_request))
        bad["action"]["parameters"]={"x":2}
        mutated=replace(pe,execution_request=bad)
        calls=[]
        with self.assertRaisesRegex(ValueError,"candidate_binding_mismatch"):
            execute_external_consequence_if_coherent(
                mutated,
                prepared_adapter_request=prepared,
                task_runner=lambda task,payload: calls.append((task,payload)),
                authority_resolution=authority_resolution(),
                evidence_current=True,
            )
        self.assertEqual(calls,[])

    def test_wrong_target_authority_never_reaches_runner(self):
        adapter,registry,prepared,result=evaluate_native(native_action())
        pe=build_execution(adapter,registry,prepared,result)
        auth=authority_resolution()
        auth["authority_ref"]="target-authority:wrong"
        calls=[]
        evidence=execute_external_consequence_if_coherent(
            pe,
            prepared_adapter_request=prepared,
            task_runner=lambda task,payload: calls.append((task,payload)),
            authority_resolution=auth,
            evidence_current=True,
        )
        self.assertTrue(evidence.status.startswith("DENIED:AUTHORITY_REF_MISMATCH"))
        self.assertFalse(evidence.executor_invoked)
        self.assertFalse(evidence.consequence_observed)
        self.assertEqual(calls,[])

    def test_changed_target_is_denied_by_shared_present_state_component(self):
        adapter,registry,prepared,result=evaluate_native(native_action())
        pe=build_execution(adapter,registry,prepared,result)
        calls=[]
        evidence=execute_external_consequence_if_coherent(
            pe,
            prepared_adapter_request=prepared,
            task_runner=lambda task,payload: calls.append((task,payload)),
            authority_resolution=authority_resolution(target_binding="target:changed"),
            evidence_current=True,
        )
        self.assertIn("PRESENT_STATE_DENY:authority_target_mismatch",evidence.status)
        self.assertEqual(evidence.present_state_disposition,"DENY")
        self.assertEqual(calls,[])

    def test_expired_authority_is_denied_by_shared_present_state_component(self):
        adapter,registry,prepared,result=evaluate_native(native_action())
        pe=build_execution(adapter,registry,prepared,result)
        calls=[]
        evidence=execute_external_consequence_if_coherent(
            pe,
            prepared_adapter_request=prepared,
            task_runner=lambda task,payload: calls.append((task,payload)),
            authority_resolution=authority_resolution(valid_until="2026-02-01T00:00:00+00:00"),
            evidence_current=True,
        )
        self.assertIn("PRESENT_STATE_DENY:authority_expired",evidence.status)
        self.assertEqual(calls,[])

    def test_unestablished_evidence_freshness_fails_closed(self):
        adapter,registry,prepared,result=evaluate_native(native_action())
        pe=build_execution(adapter,registry,prepared,result)
        calls=[]
        evidence=execute_external_consequence_if_coherent(
            pe,
            prepared_adapter_request=prepared,
            task_runner=lambda task,payload: calls.append((task,payload)),
            authority_resolution=authority_resolution(),
            evidence_current=None,
        )
        self.assertIn("PRESENT_STATE_FAIL_CLOSED:evidence_current_state_unestablished",evidence.status)
        self.assertEqual(evidence.present_state_disposition,"FAIL_CLOSED")
        self.assertEqual(calls,[])

    def test_wrong_credential_never_reaches_runner(self):
        adapter,registry,prepared,result=evaluate_native(native_action())
        pe=build_execution(adapter,registry,prepared,result)
        auth=authority_resolution()
        auth["credential_hash"]="sha256:"+"3"*64
        calls=[]
        evidence=execute_external_consequence_if_coherent(
            pe,
            prepared_adapter_request=prepared,
            task_runner=lambda task,payload: calls.append((task,payload)),
            authority_resolution=auth,
            evidence_current=True,
        )
        self.assertTrue(evidence.status.startswith("DENIED:CREDENTIAL_HASH_MISMATCH"))
        self.assertFalse(evidence.executor_invoked)
        self.assertEqual(calls,[])

    def test_auto_capability_mode_is_rejected_before_runner(self):
        adapter,registry,prepared,result=evaluate_native(native_action())
        with self.assertRaisesRegex(ValueError,"capability_mode_forbidden"):
            build_steggate_execution_request(
                adapter,registry,prepared,result,
                parameters={"x":1},
                credential=credential(),
                target_binding=TARGET_BINDING,
                capability_surface={
                    "actions_exposed":["native.execute"],
                    "execution_mode":"auto",
                    "requires_governed_commit":True,
                },
            )

    def test_governance_deny_cannot_construct_execution_request(self):
        adapter,registry,prepared,result=evaluate_native(native_action(authority_current=False))
        self.assertEqual(result.decision,"DENY")
        with self.assertRaisesRegex(ValueError,"governance_or_adapter_gate_not_eligible"):
            build_steggate_execution_request(
                adapter,registry,prepared,result,
                parameters={"x":1},
                credential=credential(),
                target_binding=TARGET_BINDING,
            )


if __name__=="__main__":
    unittest.main()
