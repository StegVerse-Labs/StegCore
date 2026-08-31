#!/usr/bin/env python3
from __future__ import annotations

from hashlib import sha1
import json
from pathlib import Path
import sys

from stegcore.three_layer import ExecutionBoundary, JudgmentConditions, SignalAdmission, ThreeLayerRequest
from stegcore.universal_governance_connector import (
    GovernanceConnectorRequest,
    VerifiedTransportBindings,
    evaluate_governance_connector,
    parse_governance_connector_request,
)

ROOT=Path(__file__).resolve().parents[1]
SNAP=ROOT/"contracts/universal_governance_connector_snapshot"


def git_blob_sha(raw: bytes) -> str:
    return sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def transport_bindings(profile):
    return VerifiedTransportBindings(
        interlock_exchange_id="exchange:canonical-snapshot",
        intr_packet_id="intr:canonical-snapshot",
        intr_profile_ref=profile["interlock"]["intr_profile_ref"],
        governed_transition_profile_ref=profile["interlock"]["governed_transition_profile_ref"],
        carrier_profile_ref=profile["interlock"]["carrier_profile_ref"],
    )


def main() -> int:
    try:
        manifest=load(SNAP/"manifest.json")
        if manifest["governance_source_commit"] != "3b0e5f10616fc00f2d91117bbf5ada358b04144d":
            raise ValueError("unexpected Governance source commit")
        for entry in manifest["source_files"]:
            path=ROOT/entry["snapshot_path"]
            raw=path.read_bytes()
            if git_blob_sha(raw) != entry["source_blob_sha"]:
                raise ValueError(f"snapshot blob mismatch: {path}")
        profile=load(SNAP/"profile.example.json")
        payload=load(SNAP/"request.example.json")
        parsed=parse_governance_connector_request(profile, payload, transport_bindings(profile))
        result=evaluate_governance_connector(profile,parsed)
        if result.decision!="ALLOW":
            raise ValueError(f"canonical profile runtime decision {result.decision}: {result.reason_code}")
        if result.execution_authority_granted is not False or result.credential_authority!="TV/TVC":
            raise ValueError("authority boundary drift")
        if result.continuity_receipt_minted is not False:
            raise ValueError("continuity minting drift")
        bad_transport=VerifiedTransportBindings(
            interlock_exchange_id="exchange:canonical-snapshot",
            intr_packet_id="intr:canonical-snapshot",
            intr_profile_ref="mismatch",
            governed_transition_profile_ref=profile["interlock"]["governed_transition_profile_ref"],
            carrier_profile_ref=profile["interlock"]["carrier_profile_ref"],
        )
        try:
            parse_governance_connector_request(profile, payload, bad_transport)
            raise ValueError("negative binding control accepted")
        except ValueError as exc:
            if "intr_profile_mismatch" not in str(exc):
                raise
        forged=dict(payload)
        forged["intr_packet_id"]="self-asserted"
        try:
            parse_governance_connector_request(profile, forged, transport_bindings(profile))
            raise ValueError("payload transport self-assertion accepted")
        except ValueError as exc:
            if "request_field_set_invalid" not in str(exc):
                raise
    except Exception as exc:
        print(f"UNIVERSAL_GOVERNANCE_CONNECTOR_CROSS_REPO: FAIL: {exc}")
        return 1
    print("UNIVERSAL_GOVERNANCE_CONNECTOR_CROSS_REPO: PASS")
    print("governance_commit=3b0e5f10616fc00f2d91117bbf5ada358b04144d")
    print("positive=SERIALIZED_REQUEST_ALLOW_NON_AUTHORIZING")
    print("negative=INTR_PROFILE_MISMATCH_REJECTED")
    print("negative=PAYLOAD_TRANSPORT_SELF_ASSERTION_REJECTED")
    print("authority_effect=NONE")
    return 0


if __name__=="__main__":
    sys.exit(main())
