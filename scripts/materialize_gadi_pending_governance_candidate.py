#!/usr/bin/env python3
from __future__ import annotations

"""Materialize a canonical PENDING GADI request and hash-bound Governance candidate.

This local-only adapter consumes already-observed canonical threat observations,
already-materialized canonical defensive capability records, and already-resolved
Governance facts. It reuses the existing GADI reasoning functions to correlate the
threat, select the least-destructive effective capability, and build the canonical
PENDING intervention request. It then binds that exact request into the existing
GADI Governance connector request shape.

It does not observe a threat, resolve Governance facts, perform InTr transport,
admit a request, mint credentials, create a runtime binding, claim WorkerCoordinator
work, execute an actuator, or grant execution authority.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from stegcore.gadi import (
    DefensiveCapability,
    ThreatObservation,
    build_intervention_request,
    choose_least_destructive_effective_capability,
    correlate_threat,
)
from stegcore.gadi_intr_admission import (
    GADI_BOUNDARY_ID,
    GADI_OPERATION_ID,
    GADI_PROFILE_ID,
    GADI_SYSTEM_ID,
    canonical_request_hash,
    expected_candidate_ref,
)
from stegcore.universal_governance_connector import resolve_governance_connector_profile

ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_REGISTRY = ROOT / "contracts" / "universal_governance_connector_snapshot" / "universal-governance-connector-profiles.v1.json"
OUTPUT_SCHEMA = "stegcore.gadi-pending-governance-candidate-materialization/v1"


class GADIPendingCandidateError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GADIPendingCandidateError(message)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception as exc:
        raise GADIPendingCandidateError("as_of invalid date-time") from exc
    _require(parsed.tzinfo is not None and parsed.utcoffset() is not None, "as_of must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name("." + path.name + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _objects(value: Any, label: str) -> list[dict[str, Any]]:
    if isinstance(value, Mapping):
        return [dict(value)]
    if isinstance(value, list) and value and all(isinstance(item, Mapping) for item in value):
        return [dict(item) for item in value]
    raise GADIPendingCandidateError(f"{label} must be a JSON object or non-empty array of objects")


def _validate_resolved_facts(value: Mapping[str, Any], *, policy_ref: str) -> dict[str, Any]:
    required = {"judgment_conditions", "signal_admission", "execution_boundary"}
    _require(set(value) == required, "resolved Governance facts must contain exactly judgment_conditions, signal_admission, execution_boundary")
    judgment = value.get("judgment_conditions")
    signal = value.get("signal_admission")
    boundary = value.get("execution_boundary")
    _require(all(isinstance(item, Mapping) for item in (judgment, signal, boundary)), "resolved Governance fact layers must be objects")
    _require(boundary.get("policy_ref") == policy_ref, "resolved Governance policy_ref mismatch")
    for field in ("evidence_refs",):
        refs = judgment.get(field)
        _require(isinstance(refs, list) and all(_nonempty(item) for item in refs), "judgment evidence_refs must be list[str]")
    for field in ("admitted_signal_refs", "excluded_signal_refs", "transformations", "missing_inputs"):
        refs = signal.get(field, [])
        _require(isinstance(refs, list) and all(_nonempty(item) for item in refs), f"signal {field} must be list[str]")
    refs = boundary.get("evidence_refs")
    _require(isinstance(refs, list) and all(_nonempty(item) for item in refs), "execution boundary evidence_refs must be list[str]")
    return {
        "judgment_conditions": dict(judgment),
        "signal_admission": dict(signal),
        "execution_boundary": dict(boundary),
    }


def materialize_pending_governance_candidate(
    *,
    observation_payloads: list[Mapping[str, Any]],
    capability_payloads: list[Mapping[str, Any]],
    resolved_governance_facts: Mapping[str, Any],
    governance_registry: Mapping[str, Any],
    as_of: datetime,
    mode: str,
    target_class: str,
    request_id: str,
    governed_principal_id: str,
    receipt_correlation_id: str,
    intent_ref: str,
    threatened_subject_ref: str | None = None,
    minimum_effectiveness: float = 0.70,
) -> dict[str, Any]:
    _require(mode in {"simulation", "production"}, "mode must be simulation or production")
    for value, label in (
        (target_class, "target_class"),
        (request_id, "request_id"),
        (governed_principal_id, "governed_principal_id"),
        (receipt_correlation_id, "receipt_correlation_id"),
        (intent_ref, "intent_ref"),
    ):
        _require(_nonempty(value), f"{label} required")
    _require(0.0 <= minimum_effectiveness <= 1.0, "minimum_effectiveness out of range")

    try:
        observations = [ThreatObservation.model_validate(dict(item)) for item in observation_payloads]
        capabilities = [DefensiveCapability.model_validate(dict(item)) for item in capability_payloads]
    except Exception as exc:
        raise GADIPendingCandidateError(f"canonical GADI input invalid: {exc}") from exc

    assessment = correlate_threat(observations, as_of=as_of)
    selected = choose_least_destructive_effective_capability(
        assessment,
        capabilities,
        as_of=as_of,
        mode=mode,
        target_class=target_class,
        minimum_effectiveness=minimum_effectiveness,
    )
    _require(selected is not None, "no eligible defensive capability selected")
    request = build_intervention_request(
        assessment,
        selected,
        request_id=request_id,
        governed_principal_id=governed_principal_id,
        receipt_correlation_id=receipt_correlation_id,
        threatened_subject_ref=threatened_subject_ref,
    )

    profile = resolve_governance_connector_profile(governance_registry, GADI_PROFILE_ID)
    operation = next((item for item in profile.get("operations", []) if isinstance(item, Mapping) and item.get("operation_id") == GADI_OPERATION_ID), None)
    _require(isinstance(operation, Mapping), "GADI Governance operation missing")
    policy_ref = str(operation.get("policy_ref") or "")
    _require(_nonempty(policy_ref), "GADI Governance policy_ref missing")
    facts = _validate_resolved_facts(resolved_governance_facts, policy_ref=policy_ref)

    evidence_refs = list(dict.fromkeys([
        *assessment.evidence_refs,
        *(facts["judgment_conditions"].get("evidence_refs") or []),
        *(facts["signal_admission"].get("admitted_signal_refs") or []),
        *(facts["execution_boundary"].get("evidence_refs") or []),
    ]))
    _require(bool(evidence_refs), "Governance candidate evidence_refs required")

    governance_request = {
        "schema_version": "stegverse.governance-connector.request/v1",
        "profile_id": GADI_PROFILE_ID,
        "operation_id": GADI_OPERATION_ID,
        "system_id": GADI_SYSTEM_ID,
        "boundary_id": GADI_BOUNDARY_ID,
        "authority_ref": selected.authorization_evidence_ref,
        "intent_ref": intent_ref,
        "candidate_ref": expected_candidate_ref(request),
        "candidate_hash": canonical_request_hash(request),
        "evidence_refs": evidence_refs,
        "resolved_facts": facts,
    }

    return {
        "schema": OUTPUT_SCHEMA,
        "task_id": "GADI-001",
        "state": "PENDING_GOVERNANCE_CANDIDATE_MATERIALIZED",
        "assessment": assessment.model_dump(mode="json"),
        "selected_capability": selected.model_dump(mode="json"),
        "pending_request": request.model_dump(mode="json"),
        "governance_request": governance_request,
        "threat_observation_created": False,
        "resolved_governance_facts_created": False,
        "intr_transport_performed": False,
        "admission_created": False,
        "runtime_binding_created": False,
        "credential_minted": False,
        "claim_or_fence_minted": False,
        "execution_authority_granted": False,
        "network_fetch_performed": False,
        "credential_authority": "TV/TVC",
        "authority_effect": "NONE_PENDING_REQUEST_AND_CANDIDATE_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--capabilities", type=Path, required=True)
    parser.add_argument("--resolved-governance-facts", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--mode", choices=("simulation", "production"), required=True)
    parser.add_argument("--target-class", required=True)
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--governed-principal-id", required=True)
    parser.add_argument("--receipt-correlation-id", required=True)
    parser.add_argument("--intent-ref", required=True)
    parser.add_argument("--threatened-subject-ref")
    parser.add_argument("--minimum-effectiveness", type=float, default=0.70)
    parser.add_argument("--pending-request-output", type=Path, required=True)
    parser.add_argument("--governance-request-output", type=Path, required=True)
    parser.add_argument("--receipt-output", type=Path, required=True)
    args = parser.parse_args()

    observations_path = args.observations.expanduser().resolve()
    capabilities_path = args.capabilities.expanduser().resolve()
    facts_path = args.resolved_governance_facts.expanduser().resolve()
    result = materialize_pending_governance_candidate(
        observation_payloads=_objects(_load(observations_path), "observations"),
        capability_payloads=_objects(_load(capabilities_path), "capabilities"),
        resolved_governance_facts=dict(_load(facts_path)),
        governance_registry=dict(_load(GOVERNANCE_REGISTRY)),
        as_of=_utc(args.as_of),
        mode=args.mode,
        target_class=args.target_class,
        request_id=args.request_id,
        governed_principal_id=args.governed_principal_id,
        receipt_correlation_id=args.receipt_correlation_id,
        intent_ref=args.intent_ref,
        threatened_subject_ref=args.threatened_subject_ref,
        minimum_effectiveness=args.minimum_effectiveness,
    )
    result.update({
        "observations_source_sha256": _sha(observations_path),
        "capabilities_source_sha256": _sha(capabilities_path),
        "resolved_governance_facts_source_sha256": _sha(facts_path),
        "governance_registry_source_sha256": _sha(GOVERNANCE_REGISTRY),
    })
    _write(args.pending_request_output, result["pending_request"])
    _write(args.governance_request_output, result["governance_request"])
    _write(args.receipt_output, result)
    print(json.dumps(result, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
