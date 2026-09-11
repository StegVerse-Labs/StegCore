#!/usr/bin/env python3
from __future__ import annotations

"""Project exact GADI Governance facts from an already-current external-evidence envelope.

This adapter reuses the existing Governance external-evidence interoperability surface.
It does not create or sign an evidence envelope, invent facts, perform InTr transport,
make a GADI admission decision, mint credentials, create a runtime binding, claim/fence
work, execute an actuator, or grant execution authority.
"""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from stegcore.external_evidence import evaluate_external_evidence, request_from_external_evidence

OUTPUT_SCHEMA = "stegcore.gadi-governance-facts-from-external-evidence/v1"
GADI_ACTION = "ADMIT_DEFENSIVE_INTERVENTION"
GADI_TARGET = "stegverse.gadi.defensive-intervention"
GADI_SCOPE = "operation:admit-defensive-intervention"
GADI_POLICY = "policy.gadi.defensive-intervention.v1"


class GADIExternalEvidenceFactsError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GADIExternalEvidenceFactsError(message)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GADIExternalEvidenceFactsError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name("." + path.name + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def resolved_facts_from_external_evidence(envelope: Mapping[str, Any]) -> dict[str, Any]:
    """Return canonical resolved_facts only from an envelope accepted by the existing adapter."""
    candidate = envelope.get("commitment_candidate")
    _require(isinstance(candidate, Mapping), "external evidence commitment_candidate required")
    _require(candidate.get("action") == GADI_ACTION, "external evidence GADI action mismatch")
    _require(candidate.get("target_ref") == GADI_TARGET, "external evidence GADI target mismatch")
    _require(candidate.get("scope") == GADI_SCOPE, "external evidence GADI scope mismatch")
    _require(candidate.get("policy_ref") == GADI_POLICY, "external evidence GADI policy mismatch")
    _require(candidate.get("evidence_provider_execution_authority") is False, "external evidence provider authority forbidden")

    result = evaluate_external_evidence(envelope)
    _require(result.three_layer_result is not None, f"external evidence envelope not admissible as fact source: {result.reason_code}")

    request = request_from_external_evidence(envelope)
    judgment = request.judgment_conditions
    signal = request.signal_admission
    boundary = request.execution_boundary

    facts = {
        "judgment_conditions": {
            "refusal_available": judgment.refusal_available,
            "operator_recoverability": judgment.operator_recoverability,
            "workload_state": judgment.workload_state,
            "time_pressure": judgment.time_pressure,
            "isolation_state": judgment.isolation_state,
            "evidence_refs": list(judgment.evidence_refs),
        },
        "signal_admission": {
            "admitted_signal_refs": list(signal.admitted_signal_refs),
            "excluded_signal_refs": list(signal.excluded_signal_refs),
            "transformations": list(signal.transformations),
            "missing_inputs": list(signal.missing_inputs),
            "uncertainty_state": signal.uncertainty_state,
            "reference_state_hash": signal.reference_state_hash,
            "expected_reference_state_hash": signal.expected_reference_state_hash,
            "reconstruction_available": signal.reconstruction_available,
            "transformation_provenance_complete": signal.transformation_provenance_complete,
        },
        "execution_boundary": {
            "actor_authority_current": boundary.actor_authority_current,
            "policy_current": boundary.policy_current,
            "delegation_current": boundary.delegation_current,
            "evidence_current": boundary.evidence_current,
            "affected_entity_conditions_represented": boundary.affected_entity_conditions_represented,
            "recoverability_profile": boundary.recoverability_profile,
            "validity_window_open": boundary.validity_window_open,
            "policy_ref": boundary.policy_ref,
            "delegation_ref": boundary.delegation_ref,
            "evidence_refs": list(boundary.evidence_refs),
        },
    }
    _require(facts["execution_boundary"]["policy_ref"] == GADI_POLICY, "projected Governance policy drift")
    return {
        "schema": OUTPUT_SCHEMA,
        "task_id": "GADI-001",
        "state": "RESOLVED_GOVERNANCE_FACTS_PROJECTED",
        "resolved_governance_facts": facts,
        "external_evidence_decision": result.decision,
        "external_evidence_reason_code": result.reason_code,
        "external_evidence_receipt": dict(result.receipt),
        "external_evidence_envelope_created": False,
        "resolved_governance_facts_invented": False,
        "intr_transport_performed": False,
        "gadi_admission_created": False,
        "runtime_binding_created": False,
        "credential_minted": False,
        "claim_or_fence_minted": False,
        "execution_authority_granted": False,
        "network_fetch_performed": False,
        "authority_effect": "NONE_FACT_PROJECTION_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--external-evidence-envelope", type=Path, required=True)
    parser.add_argument("--facts-output", type=Path, required=True)
    parser.add_argument("--receipt-output", type=Path, required=True)
    args = parser.parse_args()

    envelope_path = args.external_evidence_envelope.expanduser().resolve()
    result = resolved_facts_from_external_evidence(_load(envelope_path))
    result["external_evidence_source_sha256"] = _sha(envelope_path)
    _write(args.facts_output, result["resolved_governance_facts"])
    _write(args.receipt_output, result)
    print(json.dumps(result, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
