from __future__ import annotations

import argparse
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

from stegcore.commit_governance import canonical_hash
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
from stegcore.fresh_commit_binding import (
    consume_execution_binding,
    evaluate_fresh_commit_binding,
)
from stegcore.universal_governance_connector import VerifiedTransportBindings
from stegcore.universal_governance_consequence_evidence import (
    build_master_records_projection,
    build_universal_governance_consequence_evidence,
    return_consequence_evidence_via_intr,
)

INTR_REGISTRY = STEGOS / "specs" / "universal-intr-connector-profiles.v1.json"
TARGET_BINDING = "target:universal-governance-reference:bounded-state:1"


def load(name: str) -> dict[str, Any]:
    value = json.loads((GOV / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {name}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def hash_uri(value: Any) -> str:
    return "sha256:" + canonical_hash(value)


class BoundedReferenceTarget:
    """Bounded reference consequence target with one shared enforcement boundary.

    The canonical task-runner closure possesses the boundary permit.  The
    alternate route reaches the same mutation primitive but does not possess
    that permit, so it can request the consequence but cannot perform it.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.__boundary_permit = object()
        if not self.path.is_file():
            self._write(
                {
                    "material_state": {
                        "state_version": "V0",
                        "policy_epoch": "P0",
                        "policy": {"mode": "bounded", "revision": 0},
                        "evidence_bundle": {"risk": "baseline", "revision": 0},
                    },
                    "mutation_count": 0,
                    "last": None,
                    "mutation_path": None,
                }
            )

    def _write(self, state: dict[str, Any]) -> None:
        write_json(self.path, state)

    def snapshot(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def commit_binding(self, execution_binding_id: str) -> dict[str, str]:
        material = self.snapshot()["material_state"]
        return {
            "state_version": material["state_version"],
            "state_hash": hash_uri(material),
            "policy_epoch": material["policy_epoch"],
            "policy_hash": hash_uri(material["policy"]),
            "evidence_bundle_hash": hash_uri(material["evidence_bundle"]),
            "execution_binding_id": execution_binding_id,
        }

    def material_transition(self) -> dict[str, Any]:
        before = self.snapshot()
        before_material = dict(before["material_state"])
        after = dict(before)
        after["material_state"] = {
            "state_version": "V1",
            "policy_epoch": "P1",
            "policy": {"mode": "bounded", "revision": 1},
            "evidence_bundle": {"risk": "changed", "revision": 1},
        }
        self._write(after)
        return {
            "schema": "stegcore.reference-material-state-transition.v1",
            "transition": "V0_TO_V1",
            "before_state_hash": hash_uri(before_material),
            "after_state_hash": hash_uri(after["material_state"]),
            "before_state_version": before_material["state_version"],
            "after_state_version": after["material_state"]["state_version"],
            "before_policy_epoch": before_material["policy_epoch"],
            "after_policy_epoch": after["material_state"]["policy_epoch"],
            "consequence_mutation_count_before": before["mutation_count"],
            "consequence_mutation_count_after": after["mutation_count"],
            "authority_effect": "NONE_FIXTURE_STATE_CHANGE_ONLY",
        }

    def _consequence_entry(
        self,
        task: str,
        payload: dict[str, Any],
        *,
        boundary_permit: object | None,
        route: str,
    ) -> dict[str, Any]:
        before = self.snapshot()
        if boundary_permit is not self.__boundary_permit:
            return {
                "accepted": False,
                "reason": "canonical_commit_boundary_permit_missing",
                "route": route,
                "mutation_count": before["mutation_count"],
            }
        state = dict(before)
        state["mutation_count"] = int(before.get("mutation_count", 0)) + 1
        state["last"] = {"task": task, "payload": payload}
        state["mutation_path"] = route
        self._write(state)
        return {"accepted": True, "target_state": state, "route": route}

    def governed_mutate(self, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._consequence_entry(
            task,
            payload,
            boundary_permit=self.__boundary_permit,
            route="GOVERNED_CANONICAL_COMMIT",
        )

    def alternate_route_attempt(self, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._consequence_entry(
            task,
            payload,
            boundary_permit=None,
            route="ALTERNATE_CONSEQUENCE_ROUTE",
        )


def execute(bound_state_root: Path) -> dict[str, Any]:
    bound_state_root = bound_state_root.expanduser().resolve()
    target_path = bound_state_root / "target" / "state.json"
    evidence_path = bound_state_root / "evidence" / "consequence.json"
    projection_path = bound_state_root / "evidence" / "master-records-projection.json"
    transition_path = bound_state_root / "receipts" / "material-state-transition.json"
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
    initial_governance = evaluate_prepared_external_governance_request(registry, prepared, transport)
    if initial_governance.decision != "ALLOW":
        raise RuntimeError(
            f"reference governance did not ALLOW: {initial_governance.reason_code}"
        )

    credential = TargetCredentialBinding(
        credential_id="tvc:credential:reference:1",
        credential_hash="sha256:" + "2" * 64,
        subject_binding="subject:reference-boundary:operator:1",
    )
    authority = {
        "status": "approved",
        "basis_invalidated_by_action": False,
        "authority_ref": "target-authority:example:execute:1",
        "credential_id": credential.credential_id,
        "credential_hash": credential.credential_hash,
        "subject_binding": credential.subject_binding,
        "target_binding": TARGET_BINDING,
        "valid_from": "2026-01-01T00:00:00+00:00",
        "valid_until": "2027-01-01T00:00:00+00:00",
    }

    target = BoundedReferenceTarget(target_path)
    consumed_execution_bindings: set[str] = set()
    initial_binding = target.commit_binding("EXECUTION-BINDING-V0")
    initial_binding_hash = hash_uri(initial_binding)

    # Material state changes after the original ALLOW/binding but before consequence.
    transition_receipt = target.material_transition()
    transition_receipt["receipt_hash"] = hash_uri(transition_receipt)
    write_json(transition_path, transition_receipt)
    observed_with_old_binding_id = target.commit_binding("EXECUTION-BINDING-V0")

    stale_canonical = evaluate_fresh_commit_binding(
        expected=initial_binding,
        observed=observed_with_old_binding_id,
        consumed_execution_bindings=consumed_execution_bindings,
    )
    if stale_canonical.allowed:
        raise RuntimeError("stale canonical binding unexpectedly remained current")
    stale_canonical_executor_invoked = False

    stale_alternate_before = target.snapshot()
    stale_alternate_boundary = target.alternate_route_attempt("native.execute", {"x": 1})
    stale_alternate_after = target.snapshot()
    stale_alternate = evaluate_fresh_commit_binding(
        expected=initial_binding,
        observed=observed_with_old_binding_id,
        consumed_execution_bindings=consumed_execution_bindings,
    )
    if (
        stale_alternate.allowed
        or stale_alternate_boundary["accepted"] is not False
        or stale_alternate_before != stale_alternate_after
    ):
        raise RuntimeError("stale alternate route reached consequence")

    # Re-evaluate the same manifested candidate, then bind execution to the new
    # consequence-time state. Governance remains non-execution authority.
    fresh_governance = evaluate_prepared_external_governance_request(registry, prepared, transport)
    if fresh_governance.decision != "ALLOW":
        raise RuntimeError(f"fresh governance did not ALLOW: {fresh_governance.reason_code}")
    fresh_binding = target.commit_binding("EXECUTION-BINDING-V1")
    fresh_binding_hash = hash_uri(fresh_binding)
    fresh_binding_result = evaluate_fresh_commit_binding(
        expected=fresh_binding,
        observed=target.commit_binding("EXECUTION-BINDING-V1"),
        consumed_execution_bindings=consumed_execution_bindings,
    )
    if not fresh_binding_result.allowed:
        raise RuntimeError(
            "fresh commit binding did not ALLOW: " + ",".join(fresh_binding_result.reasons)
        )

    prepared_execution = build_steggate_execution_request(
        adapter,
        registry,
        prepared,
        fresh_governance,
        parameters={"x": 1},
        credential=credential,
        target_binding=TARGET_BINDING,
    )
    execution = execute_external_consequence_if_coherent(
        prepared_execution,
        prepared_adapter_request=prepared,
        task_runner=target.governed_mutate,
        authority_resolution=authority,
        evidence_current=True,
    )
    if execution.status != "COMPLETED":
        raise RuntimeError(f"reference consequence not completed: {execution.status}")
    if execution.present_state_disposition != "ALLOW":
        raise RuntimeError("reference present-state enforcement did not ALLOW")
    if execution.target_binding != TARGET_BINDING:
        raise RuntimeError("reference target binding drift")
    consume_execution_binding(fresh_binding, consumed_execution_bindings)

    target_state = target.snapshot()
    if target_state.get("mutation_count") != 1:
        raise RuntimeError("governed target mutation count is not exactly one")

    post_commit_binding = evaluate_fresh_commit_binding(
        expected=fresh_binding,
        observed=target.commit_binding("EXECUTION-BINDING-V1"),
        consumed_execution_bindings=consumed_execution_bindings,
    )
    post_commit_before = target.snapshot()
    post_commit_alternate_boundary = target.alternate_route_attempt("native.execute", {"x": 1})
    post_commit_after = target.snapshot()
    if (
        post_commit_binding.allowed
        or "execution_binding_already_consumed" not in post_commit_binding.reasons
        or post_commit_alternate_boundary["accepted"] is not False
        or post_commit_before != post_commit_after
        or post_commit_after.get("mutation_count") != 1
    ):
        raise RuntimeError("fresh binding replay or alternate route produced a second consequence")

    evidence = build_universal_governance_consequence_evidence(
        adapter_id=adapter["adapter_id"],
        governance_result=fresh_governance,
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

    final_material = target.snapshot()["material_state"]
    receipt = {
        "schema": "stegcore.universal-governance-reference-boundary-receipt.v2",
        "reference_enforced_boundary_observed": True,
        "bypass_negative_control_passed": True,
        "alternate_consequence_path_closed": True,
        "stale_binding_rejected": True,
        "fresh_binding_required": True,
        "fresh_binding_single_use": True,
        "governed_target_mutation_count": 1,
        "final_target_mutation_count": target.snapshot()["mutation_count"],
        "real_external_system_enforced_activation": False,
        "resident_execution_observed": False,
        "initial_state_version": initial_binding["state_version"],
        "initial_state_hash": initial_binding["state_hash"],
        "initial_policy_epoch": initial_binding["policy_epoch"],
        "initial_policy_hash": initial_binding["policy_hash"],
        "initial_evidence_bundle_hash": initial_binding["evidence_bundle_hash"],
        "initial_governance_receipt_hash": initial_governance.receipt_hash,
        "initial_binding_hash": initial_binding_hash,
        "material_state_transition_receipt_hash": transition_receipt["receipt_hash"],
        "post_transition_state_version": final_material["state_version"],
        "post_transition_state_hash": hash_uri(final_material),
        "stale_canonical_route_disposition": stale_canonical.disposition,
        "stale_canonical_route_reasons": list(stale_canonical.reasons),
        "stale_canonical_executor_invoked": stale_canonical_executor_invoked,
        "stale_alternate_route_disposition": stale_alternate.disposition,
        "stale_alternate_route_reasons": list(stale_alternate.reasons),
        "stale_alternate_boundary_reason": stale_alternate_boundary["reason"],
        "stale_alternate_executor_invoked": False,
        "fresh_governance_receipt_hash": fresh_governance.receipt_hash,
        "fresh_binding_hash": fresh_binding_hash,
        "fresh_binding_checks": dict(fresh_binding_result.checks),
        "fresh_execution_binding_id": fresh_binding["execution_binding_id"],
        "post_commit_alternate_route_disposition": post_commit_binding.disposition,
        "post_commit_alternate_route_reasons": list(post_commit_binding.reasons),
        "post_commit_alternate_boundary_reason": post_commit_alternate_boundary["reason"],
        "post_commit_alternate_executor_invoked": False,
        "target_binding": execution.target_binding,
        "present_state_disposition": execution.present_state_disposition,
        "present_state_checks": dict(execution.present_state_checks or {}),
        "present_state_reasons": list(execution.present_state_reasons),
        "present_state_evaluated_at": execution.present_state_evaluated_at,
        "target_state_ref": "target/state.json",
        "material_state_transition_ref": "receipts/material-state-transition.json",
        "consequence_evidence_ref": "evidence/consequence.json",
        "master_records_projection_ref": "evidence/master-records-projection.json",
        "candidate_hash": fresh_governance.candidate_hash,
        "governance_receipt_hash": fresh_governance.receipt_hash,
        "governed_execution_receipt_hash": execution.coherence_receipt_hash,
        "request_intr_packet_id": fresh_governance.intr_packet_id,
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
