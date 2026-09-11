#!/usr/bin/env python3
from __future__ import annotations

"""Project exact GADI Governance facts from verified external evidence.

The external-evidence envelope remains evidence-only. This adapter requires a
separate verification binding so the envelope cannot self-assert signer validity,
chain validity, provider authorization, scope, or freshness. It does not create or
sign evidence, perform verification, perform InTr transport, make admission or
execution decisions, mint credentials, create runtime bindings, claim/fence work,
execute an actuator, or grant execution authority.
"""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from stegcore.external_evidence import evaluate_external_evidence, request_from_external_evidence

OUTPUT_SCHEMA = "stegcore.gadi-governance-facts-from-external-evidence/v2"
VERIFIED_BINDING_SCHEMA = "stegcore.gadi-verified-external-evidence-binding/v1"
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


def canonical_envelope_hash(envelope: Mapping[str, Any]) -> str:
    raw = json.dumps(
        envelope,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _verify_independent_binding(envelope: Mapping[str, Any], binding: Mapping[str, Any]) -> None:
    _require(binding.get("schema") == VERIFIED_BINDING_SCHEMA, "verified evidence binding schema mismatch")
    _require(binding.get("task_id") == "GADI-001", "verified evidence binding task mismatch")
    _require(binding.get("envelope_hash") == canonical_envelope_hash(envelope), "verified evidence binding envelope hash mismatch")

    provider = envelope.get("provider")
    integrity = envelope.get("integrity")
    authorization = envelope.get("authorization")
    freshness = envelope.get("freshness")
    _require(isinstance(provider, Mapping), "external evidence provider required")
    _require(isinstance(integrity, Mapping), "external evidence integrity required")
    _require(isinstance(authorization, Mapping), "external evidence authorization required")
    _require(isinstance(freshness, Mapping), "external evidence freshness required")

    _require(binding.get("provider_id") == provider.get("provider_id"), "verified evidence provider mismatch")
    _require(binding.get("public_key_ref") == provider.get("public_key_ref"), "verified evidence public key mismatch")
    _require(binding.get("content_digest") == integrity.get("content_digest"), "verified evidence content digest mismatch")
    _require(binding.get("authorization_ref") == authorization.get("authorization_ref"), "verified evidence authorization reference mismatch")
    _require(binding.get("signature_verified") is True, "external evidence signature not independently verified")
    _require(binding.get("chain_verified") is True, "external evidence chain not independently verified")
    _require(binding.get("provider_authorized") is True, "external evidence provider not independently authorized")
    _require(binding.get("scope_match") is True, "external evidence scope not independently verified")
    _require(binding.get("freshness_verified") is True, "external evidence freshness not independently verified")
    _require(_nonempty(binding.get("verification_receipt_ref")), "verified evidence receipt reference missing")
    _require(_nonempty(binding.get("verifier_authority_ref")), "verified evidence authority reference missing")
    _require(binding.get("execution_authority_granted") is False, "verified evidence binding may not grant execution authority")
    _require(binding.get("authority_effect") == "NONE_EVIDENCE_VERIFICATION_ONLY", "verified evidence binding authority drift")

    # The envelope must remain consistent with the independently verified posture.
    _require(integrity.get("chain_valid") is True, "external evidence envelope chain posture mismatch")
    _require(authorization.get("provider_authorized") is True, "external evidence envelope provider posture mismatch")
    _require(authorization.get("scope_match") is True, "external evidence envelope scope posture mismatch")
    _require(freshness.get("is_current") is True, "external evidence envelope freshness posture mismatch")


def resolved_facts_from_external_evidence(
    envelope: Mapping[str, Any],
    verified_binding: Mapping[str, Any],
) -> dict[str, Any]:
    """Return canonical resolved_facts only from independently verified evidence."""
    _verify_independent_binding(envelope, verified_binding)

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
        "state": "RESOLVED_GOVERNANCE_FACTS_PROJECTED_FROM_VERIFIED_EVIDENCE",
        "resolved_governance_facts": facts,
        "external_evidence_decision": result.decision,
        "external_evidence_reason_code": result.reason_code,
        "external_evidence_receipt": dict(result.receipt),
        "verified_evidence_binding_ref": verified_binding.get("verification_receipt_ref"),
        "verified_evidence_authority_ref": verified_binding.get("verifier_authority_ref"),
        "verified_evidence_envelope_hash": verified_binding.get("envelope_hash"),
        "external_evidence_envelope_created": False,
        "external_evidence_verified_by_projector": False,
        "verified_binding_created": False,
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
    parser.add_argument("--verified-evidence-binding", type=Path, required=True)
    parser.add_argument("--facts-output", type=Path, required=True)
    parser.add_argument("--receipt-output", type=Path, required=True)
    args = parser.parse_args()

    envelope_path = args.external_evidence_envelope.expanduser().resolve()
    binding_path = args.verified_evidence_binding.expanduser().resolve()
    envelope = _load(envelope_path)
    binding = _load(binding_path)
    result = resolved_facts_from_external_evidence(envelope, binding)
    result["external_evidence_source_sha256"] = _sha(envelope_path)
    result["verified_evidence_binding_source_sha256"] = _sha(binding_path)
    _write(args.facts_output, result["resolved_governance_facts"])
    _write(args.receipt_output, result)
    print(json.dumps(result, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
