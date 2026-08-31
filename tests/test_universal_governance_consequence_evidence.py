from __future__ import annotations

from dataclasses import replace
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
GOV=ROOT/"contracts/universal_governance_connector_snapshot"
STEGOS=ROOT/"contracts/stegos_universal_intr_snapshot"
if str(STEGOS) not in sys.path:
    sys.path.insert(0,str(STEGOS))

from stegos.intr_backbone import (
    PreparedPacket,
    UniversalInTrBackboneError,
    connector_from_registry,
)
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
from stegcore.universal_governance_consequence_evidence import (
    SCHEMA,
    build_master_records_projection,
    build_universal_governance_consequence_evidence,
    return_consequence_evidence_via_intr,
    validate_universal_governance_consequence_evidence,
)

INTR_REGISTRY=STEGOS/"specs/universal-intr-connector-profiles.v1.json"


def load(name):
    return json.loads((GOV/name).read_text(encoding="utf-8"))


def build_full_execution():
    adapter=load("external-adapter.example.json")
    registry=load("universal-governance-connector-profiles.v1.json")
    profile=validate_external_governance_adapter(adapter,registry)
    request=load("request.example.json")
    native=NativeGovernanceAction(
        native_operation="native.execute",
        native_action_ref=request["candidate_ref"],
        native_intent_ref=request["intent_ref"],
        native_authority_ref=request["authority_ref"],
        native_parameters={"x":1},
        native_evidence_refs=tuple(request["evidence_refs"]),
        resolved_governance_facts=request["resolved_facts"],
        consequence_authority_ref="target-authority:example:execute:1",
    )
    prepared=prepare_external_governance_request(adapter,registry,native)

    connector=connector_from_registry(INTR_REGISTRY,"governance-external-action")
    packet=connector.prepare(
        prepared.payload,
        payload_schema="stegverse.governance-connector.request/v1",
        operation="GOVERN_ACTION",
        operation_id="CONSEQUENCE-EVIDENCE-REQUEST-1",
    )
    request_receipt=connector.accept_hop(
        packet,
        hop_index=1,
        receipt_id="CONSEQUENCE-EVIDENCE-REQUEST-R1",
        boundary_identity_ref="StegCore:UniversalGovernanceConnector",
        recorded_at="2026-08-31T18:45:00Z",
        prior_receipt_hash=None,
    )
    complete=connector.validate_complete(packet,[request_receipt])
    ref=build_reference_adapter(
        mode="COMPAT",
        exchange_id=packet.intent["packet_id"],
        lineage_id="lineage-"+request_receipt["receipt_hash"][7:31],
        external_system_id=prepared.payload["system_id"],
        external_interface_ref=prepared.payload["boundary_id"],
        wrapper_manifest_ref=packet.intent["packet_id"],
        wrapper_receipt_refs=[request_receipt["receipt_hash"]],
        correspondence_evidence_refs=[packet.payload_hash],
        master_records_evidence_refs=[request_receipt["receipt_hash"]],
    )
    validate_reference_adapter(ref)
    transport=VerifiedTransportBindings(
        interlock_exchange_id=ref["exchange_id"],
        intr_packet_id=complete["packet_id"],
        intr_profile_ref=complete["profile_id"],
        governed_transition_profile_ref=profile["interlock"]["governed_transition_profile_ref"],
        carrier_profile_ref=profile["interlock"]["carrier_profile_ref"],
    )
    governance=evaluate_prepared_external_governance_request(registry,prepared,transport)
    credential=TargetCredentialBinding(
        credential_id="tvc:credential:example:1",
        credential_hash="sha256:"+"2"*64,
        subject_binding="subject:external-system.example:operator:1",
    )
    pe=build_steggate_execution_request(
        adapter,registry,prepared,governance,
        parameters={"x":1},
        credential=credential,
    )
    authority={
        "status":"approved",
        "basis_invalidated_by_action":False,
        "authority_ref":"target-authority:example:execute:1",
        "credential_id":credential.credential_id,
        "credential_hash":credential.credential_hash,
        "subject_binding":credential.subject_binding,
    }
    execution=execute_external_consequence_if_coherent(
        pe,
        prepared_adapter_request=prepared,
        task_runner=lambda task,payload: {"task":task,"payload":payload,"mutated":True},
        authority_resolution=authority,
    )
    return adapter,registry,connector,packet,request_receipt,governance,execution


class UniversalGovernanceConsequenceEvidenceTests(unittest.TestCase):
    def test_consequence_evidence_returns_over_intr_and_projects_to_master_records(self):
        adapter,_,connector,packet,request_receipt,governance,execution=build_full_execution()
        evidence=build_universal_governance_consequence_evidence(
            adapter_id=adapter["adapter_id"],
            governance_result=governance,
            execution=execution,
        )
        self.assertEqual(evidence["schema"],SCHEMA)
        self.assertEqual(evidence["candidate"]["candidate_hash"],governance.candidate_hash)
        self.assertEqual(evidence["governance"]["receipt_hash"],governance.receipt_hash)
        self.assertTrue(evidence["consequence"]["consequence_observed"])
        self.assertFalse(evidence["authority_boundaries"]["master_records_grants_execution_authority"])
        self.assertFalse(evidence["authority_boundaries"]["continuity_receipt_minted"])

        response,receipt,complete=return_consequence_evidence_via_intr(
            connector=connector,
            request_packet=packet,
            request_receipts=[request_receipt],
            evidence=evidence,
            operation_id="CONSEQUENCE-EVIDENCE-RETURN-1",
            receipt_id="CONSEQUENCE-EVIDENCE-RETURN-R1",
            boundary_identity_ref="ExternalSystem:GovernedBoundary",
            recorded_at="2026-08-31T18:45:01Z",
        )
        self.assertEqual(response.payload_schema,SCHEMA)
        self.assertEqual(response.intent["prior_transport_receipt_hash"],request_receipt["receipt_hash"])
        self.assertEqual(complete["state"],"TRANSPORT_COMPLETE")
        self.assertEqual(complete["payload_hash"],response.payload_hash)
        self.assertFalse(complete["transport_grants_execution_authority"])

        projection=build_master_records_projection(
            evidence,
            source_repository="StegVerse-Labs/StegCore",
            source_commit="SOURCE-COMMIT-UNDER-TEST",
            return_intr_packet_id=complete["packet_id"],
            return_payload_hash=complete["payload_hash"],
            return_terminal_receipt_hash=complete["terminal_receipt_hash"],
        )
        self.assertEqual(projection["destination_repository"],"master-records/core-lite")
        self.assertEqual(projection["source_evidence_hash"],evidence["evidence_hash"])
        self.assertEqual(projection["return_intr_packet_id"],complete["packet_id"])
        self.assertEqual(projection["return_terminal_receipt_hash"],complete["terminal_receipt_hash"])
        self.assertEqual(
            projection["travel_lineage"],
            [
                governance.intr_packet_id,
                governance.receipt_hash,
                evidence["evidence_hash"],
                complete["packet_id"],
                complete["terminal_receipt_hash"],
            ],
        )
        self.assertTrue(projection["custody_requested"])
        self.assertFalse(projection["destination_acknowledgement_minted"])
        self.assertFalse(projection["execution_authority_granted"])
        self.assertEqual(projection["authority_effect"],"NONE_SOURCE_PROJECTION_ONLY")

    def test_projection_requires_return_transport_metadata(self):
        adapter,_,_,_,_,governance,execution=build_full_execution()
        evidence=build_universal_governance_consequence_evidence(
            adapter_id=adapter["adapter_id"],
            governance_result=governance,
            execution=execution,
        )
        with self.assertRaisesRegex(ValueError,"return_transport_binding_missing"):
            build_master_records_projection(
                evidence,
                source_repository="StegVerse-Labs/StegCore",
                source_commit="SOURCE-COMMIT-UNDER-TEST",
                return_intr_packet_id="",
                return_payload_hash="",
                return_terminal_receipt_hash="",
            )

    def test_projection_rejects_return_payload_mismatch(self):
        adapter,_,connector,packet,request_receipt,governance,execution=build_full_execution()
        evidence=build_universal_governance_consequence_evidence(
            adapter_id=adapter["adapter_id"],
            governance_result=governance,
            execution=execution,
        )
        _,_,complete=return_consequence_evidence_via_intr(
            connector=connector,
            request_packet=packet,
            request_receipts=[request_receipt],
            evidence=evidence,
            operation_id="CONSEQUENCE-EVIDENCE-RETURN-MISMATCH",
            receipt_id="CONSEQUENCE-EVIDENCE-RETURN-MISMATCH-R1",
            boundary_identity_ref="ExternalSystem:GovernedBoundary",
            recorded_at="2026-08-31T18:45:02Z",
        )
        with self.assertRaisesRegex(ValueError,"return_payload_hash_mismatch"):
            build_master_records_projection(
                evidence,
                source_repository="StegVerse-Labs/StegCore",
                source_commit="SOURCE-COMMIT-UNDER-TEST",
                return_intr_packet_id=complete["packet_id"],
                return_payload_hash="sha256:"+"0"*64,
                return_terminal_receipt_hash=complete["terminal_receipt_hash"],
            )

    def test_completed_execution_cannot_claim_unobserved_consequence(self):
        adapter,_,_,_,_,governance,execution=build_full_execution()
        forged=replace(execution,consequence_observed=False)
        with self.assertRaisesRegex(ValueError,"completed_without_observed_consequence"):
            build_universal_governance_consequence_evidence(
                adapter_id=adapter["adapter_id"],
                governance_result=governance,
                execution=forged,
            )

    def test_candidate_hash_drift_is_rejected(self):
        adapter,_,_,_,_,governance,execution=build_full_execution()
        forged=replace(execution,candidate_hash="sha256:"+"9"*64)
        with self.assertRaisesRegex(ValueError,"candidate_hash_mismatch"):
            build_universal_governance_consequence_evidence(
                adapter_id=adapter["adapter_id"],
                governance_result=governance,
                execution=forged,
            )

    def test_completed_execution_requires_coherence_receipt(self):
        adapter,_,_,_,_,governance,execution=build_full_execution()
        forged=replace(execution,coherence_receipt_hash=None)
        with self.assertRaisesRegex(ValueError,"completed_without_coherence_receipt"):
            build_universal_governance_consequence_evidence(
                adapter_id=adapter["adapter_id"],
                governance_result=governance,
                execution=forged,
            )

    def test_evidence_tamper_is_detected(self):
        adapter,_,_,_,_,governance,execution=build_full_execution()
        evidence=build_universal_governance_consequence_evidence(
            adapter_id=adapter["adapter_id"],
            governance_result=governance,
            execution=execution,
        )
        bad=deepcopy(evidence)
        bad["consequence"]["consequence_observed"]=False
        with self.assertRaisesRegex(ValueError,"hash_mismatch"):
            validate_universal_governance_consequence_evidence(bad)

    def test_return_transport_exact_byte_tamper_is_rejected(self):
        adapter,_,connector,packet,request_receipt,governance,execution=build_full_execution()
        evidence=build_universal_governance_consequence_evidence(
            adapter_id=adapter["adapter_id"],
            governance_result=governance,
            execution=execution,
        )
        response=connector.prepare_response(
            packet,[request_receipt],evidence,
            payload_schema=SCHEMA,
            operation_id="CONSEQUENCE-EVIDENCE-TAMPER",
        )
        tampered=PreparedPacket(
            profile=response.profile,
            operation=response.operation,
            payload_schema=response.payload_schema,
            payload_bytes=response.payload_bytes+b" ",
            intent=response.intent,
        )
        with self.assertRaisesRegex(UniversalInTrBackboneError,"exact_packet_hash_mismatch"):
            connector.accept_hop(
                tampered,
                hop_index=1,
                receipt_id="BAD",
                boundary_identity_ref="ExternalSystem:GovernedBoundary",
                recorded_at="2026-08-31T18:45:01Z",
                prior_receipt_hash=request_receipt["receipt_hash"],
            )


if __name__=="__main__":
    unittest.main()
