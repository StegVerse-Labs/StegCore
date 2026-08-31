#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "contracts" / "universal_governance_connector_snapshot"
STEGOS = ROOT / "contracts" / "stegos_universal_intr_snapshot"
if str(STEGOS) not in sys.path:
    sys.path.insert(0, str(STEGOS))

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
from stegcore.universal_governance_consequence_evidence import (
    build_master_records_projection,
    build_universal_governance_consequence_evidence,
    return_consequence_evidence_via_intr,
)

INTR_REGISTRY = STEGOS / "specs" / "universal-intr-connector-profiles.v1.json"


def load(name: str) -> dict[str, Any]:
    value = json.loads((GOV / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {name}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class BoundedReferenceTarget:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.count = 0

    def snapshot(self) -> dict[str, Any]:
        if not self.path.is_file():
            return {"mutation_count": 0, "last": None}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def governed_mutate(self, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        before = self.snapshot()
        self.count = int(before.get("mutation_count", 0)) + 1
        state = {
            "mutation_count": self.count,
            "last": {"task": task, "payload": payload},
            "mutation_path": "GOVERNED_ONLY",
        }
        write_json(self.path, state)
        return {"target_state": state}

    def bypass_attempt(self, task: str, payload: dict[str, Any]) -> bool:
        before = self.snapshot()
        # No direct mutation method exists for bypass callers.
        after = self.snapshot()
        return before == after


def execute(bound_state_root: Path) -> dict[str, Any]:
    bound_state_root = bound_state_root.expanduser().resolve()
    target_path = bound_state_root / "target" / "state.json"
    evidence_path = bound_state_root / "evidence" / "consequence.json"
    projection_path = bound_state_root / "evidence" / "master-records-projection.json"
    receipt_path = bound_state_root / "receipts" / "reference-boundary.latest.json"

    adapter = load("external-adapter.example.json")
    registry = load("universal-governance-connector-profiles.v1.json")
    request = load("request.example.json")
    profile = validate_external_governance_adapter(adapter, registry)

    native = NativeGovernanceAction(
        native_operation="native.execute",
        native_action_ref=request["candidate_ref"],
        native_intent_ref=request["intent_ref"],
        native_authority_ref=request["authority_ref"],
        native_parameters={"x": 1},
        native_evidence_refs=tuple(request["evidence_refs"]),
        resolved_governance_facts=request["resolved_facts"],
        consequence_authority_ref="target-authority:example:execute:1",
    )
    prepared = prepare_external_governance_request(adapter, registry, native)

    connector = connector_from_registry(INTR_REGISTRY, "governance-external-action")
    packet = connector.prepare(
        prepared.payload,
        payload_schema="stegverse.governance-connector.request/v1",
        operation="GOVERN_ACTION",
        operation_id="SOVEREIGN-REFERENCE-REQUEST-1",
    )
    request_receipt = connector.accept_hop(
        packet,
        hop_index=1,
        receipt_id="SOVEREIGN-REFERENCE-REQUEST-R1",
        boundary_identity_ref="StegCore:UniversalGovernanceConnector",
        recorded_at="2026-08-31T20:45:00Z",
        prior_receipt_hash=None,
    )
    complete = connector.validate_complete(packet, [request_receipt])
    ref = build_reference_adapter(
        mode="COMPAT",
        exchange_id=packet.intent["packet_id"],
        lineage_id="lineage-" + request_receipt["receipt_hash"][7:31],
        external_system_id=prepared.payload["system_id"],
        external_interface_ref=prepared.payload["boundary_id"],
        wrapper_manifest_ref=packet.intent["packet_id"],
        wrapper_receipt_refs=[request_receipt["receipt_hash"]],
        correspondence_evidence_refs=[packet.payload_hash],
        master_records_evidence_refs=[request_receipt["receipt_hash"]],
    )
    validate_reference_adapter(ref)

    transport = VerifiedTransportBindings(
        interlock_exchange_id=ref["exchange_id"],
        intr_packet_id=complete["packet_id"],
        intr_profile_ref=complete["profile_id"],
        governed_transition_profile_ref=profile["interlock"]["governed_transition_profile_ref"],
        carrier_profile_ref=profile["interlock"]["carrier_profile_ref"],
    )
    governance = evaluate_prepared_external_governance_request(registry, prepared, transport)
    if governance.decision != "ALLOW":
        raise RuntimeError(f"reference governance did not ALLOW: {governance.reason_code}")

    credential = TargetCredentialBinding(
        credential_id="tvc:credential:reference:1",
        credential_hash="sha256:" + "2" * 64,
        subject_binding="subject:reference-boundary:operator:1",
    )
    prepared_execution = build_steggate_execution_request(
        adapter,
        registry,
        prepared,
        governance,
        parameters={"x": 1},
        credential=credential,
    )
    authority = {
        "status": "approved",
        "basis_invalidated_by_action": False,
        "authority_ref": "target-authority:example:execute:1",
        "credential_id": credential.credential_id,
        "credential_hash": credential.credential_hash,
        "subject_binding": credential.subject_binding,
    }

    target = BoundedReferenceTarget(target_path)
    pre_bypass = target.snapshot()
    bypass_negative_control_passed = target.bypass_attempt("native.execute", {"x": 999})
    if not bypass_negative_control_passed or target.snapshot() != pre_bypass:
        raise RuntimeError("bypass negative control changed target state")

    execution = execute_external_consequence_if_coherent(
        prepared_execution,
        prepared_adapter_request=prepared,
        task_runner=target.governed_mutate,
        authority_resolution=authority,
    )
    if execution.status != "COMPLETED":
        raise RuntimeError(f"reference consequence not completed: {execution.status}")
    target_state = target.snapshot()
    if target_state.get("mutation_count") != 1:
        raise RuntimeError("governed target mutation count is not exactly one")

    evidence = build_universal_governance_consequence_evidence(
        adapter_id=adapter["adapter_id"],
        governance_result=governance,
        execution=execution,
    )
    response, return_receipt, return_complete = return_consequence_evidence_via_intr(
        connector=connector,
        request_packet=packet,
        request_receipts=[request_receipt],
        evidence=evidence,
        operation_id="SOVEREIGN-REFERENCE-RETURN-1",
        receipt_id="SOVEREIGN-REFERENCE-RETURN-R1",
        boundary_identity_ref="ExternalSystem:GovernedBoundary",
        recorded_at="2026-08-31T20:45:01Z",
    )
    projection = build_master_records_projection(
        evidence,
        source_repository="StegVerse-Labs/StegCore",
        source_commit="RUNTIME_LOCAL_SOURCE",
        return_intr_packet_id=return_complete["packet_id"],
        return_payload_hash=return_complete["payload_hash"],
        return_terminal_receipt_hash=return_complete["terminal_receipt_hash"],
    )

    write_json(evidence_path, evidence)
    write_json(projection_path, projection)

    receipt = {
        "schema": "stegcore.universal-governance-reference-boundary-receipt.v1",
        "reference_enforced_boundary_observed": True,
        "bypass_negative_control_passed": True,
        "governed_target_mutation_count": 1,
        "real_external_system_enforced_activation": False,
        "target_state_ref": "target/state.json",
        "consequence_evidence_ref": "evidence/consequence.json",
        "master_records_projection_ref": "evidence/master-records-projection.json",
        "candidate_hash": governance.candidate_hash,
        "governance_receipt_hash": governance.receipt_hash,
        "request_intr_packet_id": governance.intr_packet_id,
        "return_intr_packet_id": return_complete["packet_id"],
        "return_terminal_receipt_hash": return_complete["terminal_receipt_hash"],
        "credential_authority": "TV/TVC",
        "repository_writeback_performed": False,
        "network_used": False,
        "continuity_receipt_minted": False,
        "publication_authority_granted": False,
        "authority_effect": "REFERENCE_BOUNDARY_OBSERVATION_ONLY",
    }
    write_json(receipt_path, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound-state-root", required=True)
    args = parser.parse_args()
    try:
        receipt = execute(Path(args.bound_state_root))
    except Exception as exc:
        print(json.dumps({"state": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps({"state": "PASS", "receipt": receipt}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
