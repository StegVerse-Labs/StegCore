#!/usr/bin/env python3
from __future__ import annotations

from hashlib import sha1
import json
from pathlib import Path
import sys

from stegcore.three_layer import ExecutionBoundary, JudgmentConditions, SignalAdmission, ThreeLayerRequest
from stegcore.universal_governance_connector import GovernanceConnectorRequest, evaluate_governance_connector

ROOT=Path(__file__).resolve().parents[1]
SNAP=ROOT/"contracts/universal_governance_connector_snapshot"


def git_blob_sha(raw: bytes) -> str:
    return sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def runtime_request(profile):
    op=next(x for x in profile["operations"] if x["operation_id"]=="execute")
    tl=ThreeLayerRequest(
        judgment_conditions=JudgmentConditions(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=("judgment:canonical-snapshot",),
        ),
        signal_admission=SignalAdmission(
            admitted_signal_refs=("signal:canonical-snapshot",),
            missing_inputs=(),
            uncertainty_state="bounded",
            reference_state_hash="state:canonical",
            expected_reference_state_hash="state:canonical",
            reconstruction_available=True,
            transformation_provenance_complete=True,
        ),
        execution_boundary=ExecutionBoundary(
            actor_authority_current=True,
            policy_current=True,
            delegation_current=True,
            evidence_current=True,
            affected_entity_conditions_represented=True,
            recoverability_profile="recoverable",
            validity_window_open=True,
            policy_ref=op["policy_ref"],
            delegation_ref="delegation:canonical-snapshot",
            evidence_refs=("execution:canonical-snapshot",),
        ),
        action=op["action_class"],
        target=profile["system"]["system_id"],
        scope="snapshot-contract",
    )
    return GovernanceConnectorRequest(
        profile_id=profile["profile_id"],
        operation_id=op["operation_id"],
        system_id=profile["system"]["system_id"],
        boundary_id=profile["system"]["boundary_id"],
        interlock_exchange_id="exchange:canonical-snapshot",
        intr_packet_id="intr:canonical-snapshot",
        intr_profile_ref=profile["interlock"]["intr_profile_ref"],
        governed_transition_profile_ref=profile["interlock"]["governed_transition_profile_ref"],
        carrier_profile_ref=profile["interlock"]["carrier_profile_ref"],
        authority_ref="authority:canonical-snapshot",
        intent_ref="intent:canonical-snapshot",
        candidate_ref="candidate:canonical-snapshot",
        evidence_refs=("evidence:canonical-snapshot",),
        three_layer_request=tl,
    )


def main() -> int:
    try:
        manifest=load(SNAP/"manifest.json")
        if manifest["governance_source_commit"] != "0632ee691711d1fcc38ae8b1729c26b9d78d21e1":
            raise ValueError("unexpected Governance source commit")
        for entry in manifest["source_files"]:
            path=ROOT/entry["snapshot_path"]
            raw=path.read_bytes()
            if git_blob_sha(raw) != entry["source_blob_sha"]:
                raise ValueError(f"snapshot blob mismatch: {path}")
        profile=load(SNAP/"profile.example.json")
        result=evaluate_governance_connector(profile,runtime_request(profile))
        if result.decision!="ALLOW":
            raise ValueError(f"canonical profile runtime decision {result.decision}: {result.reason_code}")
        if result.execution_authority_granted is not False or result.credential_authority!="TV/TVC":
            raise ValueError("authority boundary drift")
        if result.continuity_receipt_minted is not False:
            raise ValueError("continuity minting drift")
        bad=runtime_request(profile)
        bad=GovernanceConnectorRequest(**{**bad.__dict__,"intr_profile_ref":"mismatch"})
        rejected=evaluate_governance_connector(profile,bad)
        if rejected.decision!="FAIL-CLOSED" or rejected.reason_code!="connector.intr_profile_mismatch":
            raise ValueError("negative binding control failed")
    except Exception as exc:
        print(f"UNIVERSAL_GOVERNANCE_CONNECTOR_CROSS_REPO: FAIL: {exc}")
        return 1
    print("UNIVERSAL_GOVERNANCE_CONNECTOR_CROSS_REPO: PASS")
    print("governance_commit=0632ee691711d1fcc38ae8b1729c26b9d78d21e1")
    print("positive=ALLOW_NON_AUTHORIZING")
    print("negative=INTR_PROFILE_MISMATCH_FAIL_CLOSED")
    print("authority_effect=NONE")
    return 0


if __name__=="__main__":
    sys.exit(main())
