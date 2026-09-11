#!/usr/bin/env python3
from __future__ import annotations

"""Materialize a GADI admission from exact local Governance/InTr evidence.

This runtime adapter does not create threat observations, resolved governance facts,
credentials, runtime bindings, claim/fence state, or execution authority. It accepts an
already-built PENDING DefensiveInterventionRequest and an already-resolved canonical
Governance connector payload bound to that exact request. The payload traverses the
existing local ``governance-external-action`` InTr connector, producing verified
transport bindings, then the existing Universal Governance Connector evaluator and
GADI admission projector are reused unchanged.
"""

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
STEGOS_SNAPSHOT = ROOT / "contracts" / "stegos_universal_intr_snapshot"
GOV_SNAPSHOT = ROOT / "contracts" / "universal_governance_connector_snapshot"
for candidate in (SRC, STEGOS_SNAPSHOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from stegos.intr_backbone import connector_from_registry
from stegos.interlock_reference_adapter import build_reference_adapter, validate_reference_adapter

from stegcore.gadi import DefensiveInterventionRequest
from stegcore.gadi_intr_admission import (
    GADI_BOUNDARY_ID,
    GADI_OPERATION_ID,
    GADI_PROFILE_ID,
    GADI_SYSTEM_ID,
    canonical_request_hash,
    expected_candidate_ref,
    project_governance_decision_to_gadi_admission,
    projection_receipt,
)
from stegcore.universal_governance_connector import (
    VerifiedTransportBindings,
    evaluate_governance_connector,
    parse_registered_governance_connector_request,
    resolve_governance_connector_profile,
)

INTR_REGISTRY = STEGOS_SNAPSHOT / "specs" / "universal-intr-connector-profiles.v1.json"
GOVERNANCE_REGISTRY = GOV_SNAPSHOT / "universal-governance-connector-profiles.v1.json"
OUTPUT_SCHEMA = "stegcore.gadi-local-admission-materialization/v1"


class GADILocalAdmissionError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GADILocalAdmissionError(message)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GADILocalAdmissionError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def _file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _payload_sha256(value: Mapping[str, Any]) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def materialize_local_admission(
    *,
    pending_request_payload: Mapping[str, Any],
    governance_payload: Mapping[str, Any],
    governance_registry: Mapping[str, Any],
    intr_registry_path: Path,
    recorded_at: str,
) -> dict[str, Any]:
    """Run exact local GADI request bytes through existing InTr + Governance planes."""
    try:
        pending = DefensiveInterventionRequest.model_validate(dict(pending_request_payload))
    except Exception as exc:
        raise GADILocalAdmissionError(f"pending GADI request invalid: {exc}") from exc
    _require(pending.admission.state == "PENDING", "GADI local admission requires PENDING request")
    _require(pending.admission.intr_decision_ref is None, "PENDING GADI request cannot carry intr_decision_ref")

    profile = resolve_governance_connector_profile(governance_registry, GADI_PROFILE_ID)
    _require(profile.get("profile_id") == GADI_PROFILE_ID, "GADI profile mismatch")
    _require(profile.get("system", {}).get("system_id") == GADI_SYSTEM_ID, "GADI system mismatch")
    _require(profile.get("system", {}).get("boundary_id") == GADI_BOUNDARY_ID, "GADI boundary mismatch")

    payload = dict(governance_payload)
    expected_hash = canonical_request_hash(pending)
    expected_ref = expected_candidate_ref(pending)
    _require(payload.get("schema_version") == "stegverse.governance-connector.request/v1", "governance request schema mismatch")
    _require(payload.get("profile_id") == GADI_PROFILE_ID, "governance request profile mismatch")
    _require(payload.get("operation_id") == GADI_OPERATION_ID, "governance request operation mismatch")
    _require(payload.get("system_id") == GADI_SYSTEM_ID, "governance request system mismatch")
    _require(payload.get("boundary_id") == GADI_BOUNDARY_ID, "governance request boundary mismatch")
    _require(payload.get("candidate_ref") == expected_ref, "governance request candidate_ref mismatch")
    _require(payload.get("candidate_hash") == expected_hash, "governance request candidate_hash mismatch")
    _require(isinstance(payload.get("resolved_facts"), Mapping), "governance request resolved_facts required")
    _require(isinstance(payload.get("evidence_refs"), list) and bool(payload["evidence_refs"]), "governance request evidence_refs required")
    _require(isinstance(payload.get("authority_ref"), str) and bool(payload["authority_ref"]), "governance request authority_ref required")
    _require(isinstance(payload.get("intent_ref"), str) and bool(payload["intent_ref"]), "governance request intent_ref required")
    _require(isinstance(recorded_at, str) and bool(recorded_at.strip()), "recorded_at required")

    registry_path = intr_registry_path.expanduser().resolve()
    _require(registry_path.is_file(), "local InTr registry path missing")
    connector = connector_from_registry(registry_path, profile["interlock"]["intr_profile_ref"])
    operation_id = f"GADI-GOVERNANCE-{pending.request_id}"
    packet = connector.prepare(
        payload,
        payload_schema="stegverse.governance-connector.request/v1",
        operation="GOVERN_ACTION",
        operation_id=operation_id,
    )
    ingress_receipt = connector.accept_hop(
        packet,
        hop_index=1,
        receipt_id=f"{operation_id}-R1",
        boundary_identity_ref="StegCore:GADIAdmissionMaterializer",
        recorded_at=recorded_at,
        prior_receipt_hash=None,
    )
    complete = connector.validate_complete(packet, [ingress_receipt])

    reference = build_reference_adapter(
        mode="COMPAT",
        exchange_id=packet.intent["packet_id"],
        lineage_id="lineage-" + ingress_receipt["receipt_hash"][7:31],
        external_system_id=GADI_SYSTEM_ID,
        external_interface_ref=GADI_BOUNDARY_ID,
        wrapper_manifest_ref=packet.intent["packet_id"],
        wrapper_receipt_refs=[ingress_receipt["receipt_hash"]],
        correspondence_evidence_refs=[packet.payload_hash],
        master_records_evidence_refs=[ingress_receipt["receipt_hash"]],
    )
    validate_reference_adapter(reference)

    transport = VerifiedTransportBindings(
        interlock_exchange_id=reference["exchange_id"],
        intr_packet_id=complete["packet_id"],
        intr_profile_ref=complete["profile_id"],
        governed_transition_profile_ref=profile["interlock"]["governed_transition_profile_ref"],
        carrier_profile_ref=profile["interlock"]["carrier_profile_ref"],
    )
    resolved_profile, parsed = parse_registered_governance_connector_request(
        governance_registry,
        payload,
        transport,
    )
    _require(resolved_profile == profile, "GADI governance registry resolution drift")
    governance = evaluate_governance_connector(profile, parsed)
    projected = project_governance_decision_to_gadi_admission(pending, governance)
    projection = projection_receipt(pending, projected, governance)

    return {
        "schema": OUTPUT_SCHEMA,
        "task_id": "GADI-001",
        "state": "ADMITTED" if projected.admission.state == "ADMITTED" else "DENIED",
        "pending_request_sha256": expected_hash,
        "governance_request_sha256": _payload_sha256(payload),
        "governance_decision": asdict(governance),
        "projected_request": projected.model_dump(mode="json"),
        "projection_receipt": projection,
        "intr_transport": {
            "profile_id": complete["profile_id"],
            "packet_id": complete["packet_id"],
            "payload_hash": complete["payload_hash"],
            "terminal_receipt_hash": complete["terminal_receipt_hash"],
            "interlock_exchange_id": reference["exchange_id"],
            "ingress_receipt_hash": ingress_receipt["receipt_hash"],
            "registry_sha256": _file_sha256(registry_path),
        },
        "resolved_governance_facts_created": False,
        "threat_observation_created": False,
        "runtime_binding_created": False,
        "credential_minted": False,
        "claim_or_fence_minted": False,
        "execution_authority_granted": False,
        "network_fetch_performed": False,
        "credential_authority": "TV/TVC",
        "authority_effect": "NONE_ADMISSION_MATERIALIZATION_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pending-request", type=Path, required=True)
    parser.add_argument("--governance-request", type=Path, required=True)
    parser.add_argument("--recorded-at", required=True)
    parser.add_argument("--projected-request-output", type=Path, required=True)
    parser.add_argument("--receipt-output", type=Path, required=True)
    args = parser.parse_args()

    pending_path = args.pending_request.expanduser().resolve()
    governance_path = args.governance_request.expanduser().resolve()
    result = materialize_local_admission(
        pending_request_payload=_load(pending_path),
        governance_payload=_load(governance_path),
        governance_registry=_load(GOVERNANCE_REGISTRY),
        intr_registry_path=INTR_REGISTRY,
        recorded_at=args.recorded_at,
    )
    result["pending_request_source_sha256"] = _file_sha256(pending_path)
    result["governance_request_source_sha256"] = _file_sha256(governance_path)
    _write(args.projected_request_output, result["projected_request"])
    _write(args.receipt_output, result)
    print(json.dumps(result, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
