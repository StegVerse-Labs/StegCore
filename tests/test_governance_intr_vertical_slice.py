from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
STEGOS_SNAPSHOT = ROOT / "contracts/stegos_universal_intr_snapshot"
if str(STEGOS_SNAPSHOT) not in sys.path:
    sys.path.insert(0, str(STEGOS_SNAPSHOT))

from stegos.intr_backbone import (
    PreparedPacket,
    UniversalInTrBackboneError,
    connector_from_registry,
    payload_hash_uri,
)
from stegos.interlock_reference_adapter import build_reference_adapter, validate_reference_adapter

from stegcore.universal_governance_connector import (
    VerifiedTransportBindings,
    evaluate_governance_connector,
    parse_governance_connector_request,
    parse_registered_governance_connector_request,
    resolve_governance_connector_profile,
)

REGISTRY = STEGOS_SNAPSHOT / "specs/universal-intr-connector-profiles.v1.json"
GOV_SNAPSHOT = ROOT / "contracts/universal_governance_connector_snapshot"


def load(name: str):
    return json.loads((GOV_SNAPSHOT / name).read_text(encoding="utf-8"))


def load_registry():
    return load("universal-governance-connector-profiles.v1.json")


def request_packet(payload: dict):
    connector = connector_from_registry(REGISTRY, "governance-external-action")
    packet = connector.prepare(
        payload,
        payload_schema="stegverse.governance-connector.request/v1",
        operation="GOVERN_ACTION",
        operation_id="GOVERN-EXECUTE-1",
    )
    receipt = connector.accept_hop(
        packet,
        hop_index=1,
        receipt_id="INTR-GOV-REQUEST-1",
        boundary_identity_ref="StegCore:UniversalGovernanceConnector",
        recorded_at="2026-08-31T15:45:00Z",
        prior_receipt_hash=None,
    )
    complete = connector.validate_complete(packet, [receipt])
    adapter = build_reference_adapter(
        mode="COMPAT",
        exchange_id=packet.intent["packet_id"],
        lineage_id="lineage-" + receipt["receipt_hash"][7:31],
        external_system_id=payload["system_id"],
        external_interface_ref=payload["boundary_id"],
        wrapper_manifest_ref=packet.intent["packet_id"],
        wrapper_receipt_refs=[receipt["receipt_hash"]],
        correspondence_evidence_refs=[packet.payload_hash],
        master_records_evidence_refs=[receipt["receipt_hash"]],
    )
    validate_reference_adapter(adapter)
    return connector, packet, receipt, complete, adapter


def transport_bindings(profile: dict, complete: dict, adapter: dict):
    return VerifiedTransportBindings(
        interlock_exchange_id=adapter["exchange_id"],
        intr_packet_id=complete["packet_id"],
        intr_profile_ref=complete["profile_id"],
        governed_transition_profile_ref=profile["interlock"]["governed_transition_profile_ref"],
        carrier_profile_ref=profile["interlock"]["carrier_profile_ref"],
    )


class GovernanceInTrVerticalSliceTests(unittest.TestCase):
    def test_request_governance_and_return_are_complete_non_authorizing_chains(self):
        registry = load_registry()
        payload = load("request.example.json")
        profile = resolve_governance_connector_profile(registry, payload["profile_id"])
        connector, packet, receipt, complete, adapter = request_packet(payload)

        self.assertEqual(complete["state"], "TRANSPORT_COMPLETE")
        self.assertEqual(complete["profile_id"], "governance-external-action")
        self.assertEqual(complete["credential_authority"], "TV/TVC")
        self.assertFalse(complete["transport_grants_execution_authority"])
        self.assertEqual(packet.payload_hash, payload_hash_uri(packet.payload_bytes))
        self.assertEqual(adapter["authority_effect"], "NONE")
        self.assertEqual(adapter["exchange_id"], packet.intent["packet_id"])

        resolved_profile, parsed = parse_registered_governance_connector_request(
            registry,
            payload,
            transport_bindings(profile, complete, adapter),
        )
        self.assertEqual(resolved_profile["profile_id"], profile["profile_id"])
        result = evaluate_governance_connector(profile, parsed)
        self.assertEqual(result.decision, "ALLOW")
        self.assertTrue(result.eligible_for_separate_consequence_authorization)
        self.assertFalse(result.execution_authority_granted)
        self.assertEqual(result.credential_authority, "TV/TVC")
        self.assertFalse(result.continuity_receipt_minted)

        response = connector.prepare_response(
            packet,
            [receipt],
            asdict(result),
            payload_schema="stegverse.governance-connector.decision/v1",
            operation_id="GOVERN-EXECUTE-1-RETURN",
        )
        response_receipt = connector.accept_hop(
            response,
            hop_index=1,
            receipt_id="INTR-GOV-RETURN-1",
            boundary_identity_ref="ExternalSystem:GovernedBoundary",
            recorded_at="2026-08-31T15:45:01Z",
            prior_receipt_hash=receipt["receipt_hash"],
        )
        returned = connector.validate_complete(response, [response_receipt])
        self.assertEqual(returned["state"], "TRANSPORT_COMPLETE")
        self.assertEqual(returned["credential_authority"], "TV/TVC")
        self.assertFalse(returned["transport_grants_execution_authority"])
        self.assertEqual(response.intent["prior_transport_receipt_hash"], receipt["receipt_hash"])

    def test_incomplete_receipt_chain_is_rejected(self):
        payload = load("request.example.json")
        connector = connector_from_registry(REGISTRY, "governance-external-action")
        packet = connector.prepare(
            payload,
            payload_schema="stegverse.governance-connector.request/v1",
            operation="GOVERN_ACTION",
            operation_id="GOVERN-INCOMPLETE",
        )
        with self.assertRaisesRegex(UniversalInTrBackboneError, "incomplete"):
            connector.validate_complete(packet, [])

    def test_altered_exact_packet_is_rejected_before_receipt(self):
        payload = load("request.example.json")
        connector = connector_from_registry(REGISTRY, "governance-external-action")
        packet = connector.prepare(
            payload,
            payload_schema="stegverse.governance-connector.request/v1",
            operation="GOVERN_ACTION",
            operation_id="GOVERN-TAMPER",
        )
        tampered = PreparedPacket(
            profile=packet.profile,
            operation=packet.operation,
            payload_schema=packet.payload_schema,
            payload_bytes=packet.payload_bytes + b" ",
            intent=packet.intent,
        )
        with self.assertRaisesRegex(UniversalInTrBackboneError, "exact_packet_hash_mismatch"):
            connector.accept_hop(
                tampered,
                hop_index=1,
                receipt_id="BAD",
                boundary_identity_ref="StegCore",
                recorded_at="2026-08-31T15:45:00Z",
                prior_receipt_hash=None,
            )

    def test_wrong_intr_profile_binding_is_rejected(self):
        profile = load("profile.example.json")
        payload = load("request.example.json")
        _, _, _, complete, adapter = request_packet(payload)
        bad = VerifiedTransportBindings(
            interlock_exchange_id=adapter["exchange_id"],
            intr_packet_id=complete["packet_id"],
            intr_profile_ref="wrong",
            governed_transition_profile_ref=profile["interlock"]["governed_transition_profile_ref"],
            carrier_profile_ref=profile["interlock"]["carrier_profile_ref"],
        )
        with self.assertRaisesRegex(ValueError, "intr_profile_mismatch"):
            parse_governance_connector_request(profile, payload, bad)

    def test_payload_transport_self_assertion_is_rejected(self):
        profile = load("profile.example.json")
        payload = load("request.example.json")
        _, _, _, complete, adapter = request_packet(payload)
        forged = deepcopy(payload)
        forged["intr_packet_id"] = complete["packet_id"]
        with self.assertRaisesRegex(ValueError, "request_field_set_invalid"):
            parse_governance_connector_request(
                profile,
                forged,
                transport_bindings(profile, complete, adapter),
            )

    def test_stale_authority_propagates_deny_after_valid_transport(self):
        profile = load("profile.example.json")
        payload = load("request.example.json")
        payload["resolved_facts"]["execution_boundary"]["actor_authority_current"] = False
        _, _, _, complete, adapter = request_packet(payload)
        parsed = parse_governance_connector_request(
            profile,
            payload,
            transport_bindings(profile, complete, adapter),
        )
        result = evaluate_governance_connector(profile, parsed)
        self.assertEqual(result.decision, "DENY")
        self.assertEqual(result.reason_code, "execution.authority_stale")
        self.assertFalse(result.execution_authority_granted)

    def test_enforced_profile_bypass_remains_fail_closed(self):
        profile = load("profile.example.json")
        payload = load("request.example.json")
        profile["system"]["bypass_path_declared"] = True
        _, _, _, complete, adapter = request_packet(payload)
        parsed = parse_governance_connector_request(
            profile,
            payload,
            transport_bindings(profile, complete, adapter),
        )
        result = evaluate_governance_connector(profile, parsed)
        self.assertEqual(result.decision, "FAIL-CLOSED")
        self.assertEqual(result.reason_code, "connector.enforced_bypass_declared")


if __name__ == "__main__":
    unittest.main()
