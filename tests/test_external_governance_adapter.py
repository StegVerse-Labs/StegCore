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
    gate_external_consequence,
    prepare_external_governance_request,
    validate_external_governance_adapter,
)
from stegcore.universal_governance_connector import VerifiedTransportBindings

REGISTRY_PATH=STEGOS/"specs/universal-intr-connector-profiles.v1.json"

def load(name):
    return json.loads((GOV/name).read_text(encoding="utf-8"))

def native_action():
    request=load("request.example.json")
    return NativeGovernanceAction(
        native_operation="native.execute",
        native_action_ref=request["candidate_ref"],
        native_intent_ref=request["intent_ref"],
        native_authority_ref=request["authority_ref"],
        native_parameters={"x": 1},
        native_evidence_refs=tuple(request["evidence_refs"]),
        resolved_governance_facts=request["resolved_facts"],
        consequence_authority_ref="target-authority:example:execute:1",
    )

def transport_for(prepared):
    connector=connector_from_registry(REGISTRY_PATH,"governance-external-action")
    packet=connector.prepare(
        prepared.payload,
        payload_schema="stegverse.governance-connector.request/v1",
        operation="GOVERN_ACTION",
        operation_id="ADAPTER-GOVERN-1",
    )
    receipt=connector.accept_hop(
        packet,
        hop_index=1,
        receipt_id="ADAPTER-INTR-REQUEST-1",
        boundary_identity_ref="StegCore:UniversalGovernanceConnector",
        recorded_at="2026-08-31T16:40:00Z",
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
    return connector,packet,receipt,complete,ref

def verified_bindings(profile,complete,ref):
    return VerifiedTransportBindings(
        interlock_exchange_id=ref["exchange_id"],
        intr_packet_id=complete["packet_id"],
        intr_profile_ref=complete["profile_id"],
        governed_transition_profile_ref=profile["interlock"]["governed_transition_profile_ref"],
        carrier_profile_ref=profile["interlock"]["carrier_profile_ref"],
    )

class ExternalGovernanceAdapterTests(unittest.TestCase):
    def setUp(self):
        self.adapter=load("external-adapter.example.json")
        self.registry=load("universal-governance-connector-profiles.v1.json")
        self.profile=validate_external_governance_adapter(self.adapter,self.registry)

    def test_native_action_through_intr_governance_to_nonexecuting_consequence_gate(self):
        prepared=prepare_external_governance_request(self.adapter,self.registry,native_action())
        self.assertNotIn("consequence_authority_ref",prepared.payload)
        self.assertEqual(prepared.payload["profile_id"],"example.external-system.v1")
        self.assertTrue(prepared.payload["candidate_hash"].startswith("sha256:"))
        self.assertEqual(result_candidate := len(prepared.payload["candidate_hash"]), 71)
        connector,packet,receipt,complete,ref=transport_for(prepared)
        result=evaluate_prepared_external_governance_request(
            self.registry,prepared,verified_bindings(self.profile,complete,ref)
        )
        self.assertEqual(result.decision,"ALLOW")
        gate=gate_external_consequence(self.adapter,self.registry,prepared,result)
        self.assertEqual(gate.state,"ELIGIBLE_FOR_SEPARATE_CONSEQUENCE_AUTHORITY")
        self.assertTrue(gate.eligible_for_separate_consequence_authority)
        self.assertTrue(gate.consequence_authority_ref_present)
        self.assertFalse(gate.consequence_executed)
        self.assertFalse(gate.adapter_grants_execution_authority)
        self.assertFalse(gate.governance_grants_execution_authority)
        self.assertEqual(gate.credential_authority,"TV/TVC")
        self.assertEqual(gate.authority_effect,"NONE")

    def test_unknown_native_operation_fails_closed_before_transport(self):
        action=replace(native_action(),native_operation="native.unknown")
        with self.assertRaisesRegex(ValueError,"native_operation_unknown"):
            prepare_external_governance_request(self.adapter,self.registry,action)

    def test_missing_separate_consequence_authority_fails_closed_before_transport(self):
        action=replace(native_action(),consequence_authority_ref="")
        with self.assertRaisesRegex(ValueError,"consequence_authority_ref_missing"):
            prepare_external_governance_request(self.adapter,self.registry,action)

    def test_enforced_adapter_bypass_is_invalid(self):
        adapter=deepcopy(self.adapter)
        adapter["bypass_path_declared"]=True
        with self.assertRaisesRegex(ValueError,"enforced_bypass_declared"):
            validate_external_governance_adapter(adapter,self.registry)

    def test_stale_governance_authority_blocks_consequence(self):
        action=native_action()
        facts=deepcopy(dict(action.resolved_governance_facts))
        facts["execution_boundary"]["actor_authority_current"]=False
        prepared=prepare_external_governance_request(
            self.adapter,self.registry,replace(action,resolved_governance_facts=facts)
        )
        _,_,_,complete,ref=transport_for(prepared)
        result=evaluate_prepared_external_governance_request(
            self.registry,prepared,verified_bindings(self.profile,complete,ref)
        )
        self.assertEqual(result.decision,"DENY")
        gate=gate_external_consequence(self.adapter,self.registry,prepared,result)
        self.assertEqual(gate.state,"CONSEQUENCE_BLOCKED")
        self.assertFalse(gate.eligible_for_separate_consequence_authority)
        self.assertFalse(gate.consequence_executed)

    def test_governance_result_cannot_escalate_execution_authority(self):
        prepared=prepare_external_governance_request(self.adapter,self.registry,native_action())
        _,_,_,complete,ref=transport_for(prepared)
        result=evaluate_prepared_external_governance_request(
            self.registry,prepared,verified_bindings(self.profile,complete,ref)
        )
        forged=replace(result,execution_authority_granted=True)
        with self.assertRaisesRegex(ValueError,"governance_execution_authority_violation"):
            gate_external_consequence(self.adapter,self.registry,prepared,forged)

if __name__=="__main__":
    unittest.main()
