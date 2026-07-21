from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List

REQUIRED_GATES = [
    "asset_inventory_complete",
    "export_verified",
    "successor_health_verified",
    "parallel_operation_passed",
    "rollback_verified",
    "secrets_rotated",
    "traffic_cutover_verified",
    "master_records_custody_recorded",
]

FORBIDDEN_TRUE_FIELDS = {
    "manual_action_required",
    "production_mutation_allowed",
    "execution_authority",
    "traffic_cutover_authority",
    "cancellation_authority",
    "provider_retirement_authority",
    "continuity_receipt_minted",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _walk_forbidden(value: Any, path: str = "$") -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_FIELDS and child is True:
                yield child_path
            yield from _walk_forbidden(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_forbidden(child, f"{path}[{index}]")


def evaluate_provider_migration_gate_evidence(report: Dict[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if report.get("schema") != "stegverse.governance.provider_migration_gate_evidence.v1":
        reasons.append("unsupported_schema")

    forbidden = list(_walk_forbidden(report))
    if forbidden:
        reasons.append("forbidden_authority_present")

    providers = report.get("providers")
    if not isinstance(providers, list) or not providers:
        reasons.append("missing_providers")
        providers = []

    seen = set()
    verified_gate_count = 0
    blocked_gate_count = 0
    provider_results: List[Dict[str, Any]] = []

    for provider in providers:
        provider_id = provider.get("provider_id") if isinstance(provider, dict) else None
        provider_reasons: List[str] = []
        if not isinstance(provider_id, str) or not provider_id:
            provider_reasons.append("missing_provider_id")
        elif provider_id in seen:
            provider_reasons.append("duplicate_provider_id")
        else:
            seen.add(provider_id)

        gates = provider.get("gates") if isinstance(provider, dict) else None
        if not isinstance(gates, list):
            provider_reasons.append("missing_gates")
            gates = []

        actual_gate_ids = [gate.get("gate") for gate in gates if isinstance(gate, dict)]
        if actual_gate_ids != REQUIRED_GATES:
            provider_reasons.append("gate_order_or_coverage_mismatch")

        for gate in gates:
            if not isinstance(gate, dict):
                provider_reasons.append("invalid_gate_record")
                continue
            state = gate.get("verification_state")
            evidence_hash = gate.get("evidence_hash")
            refs = gate.get("evidence_refs")
            if state == "EVIDENCE_VERIFIED":
                verified_gate_count += 1
                if not _is_sha256(evidence_hash):
                    provider_reasons.append(f"invalid_verified_hash:{gate.get('gate')}")
                if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) and ref for ref in refs):
                    provider_reasons.append(f"missing_verified_refs:{gate.get('gate')}")
            elif state == "BLOCKED_MISSING_EVIDENCE":
                blocked_gate_count += 1
                if evidence_hash not in (None, ""):
                    provider_reasons.append(f"blocked_gate_has_hash:{gate.get('gate')}")
                if refs not in ([], None):
                    provider_reasons.append(f"blocked_gate_has_refs:{gate.get('gate')}")
            else:
                provider_reasons.append(f"unsupported_state:{gate.get('gate')}")

        expected_set_hash = _sha256(gates)
        if provider.get("gate_set_hash") != expected_set_hash:
            provider_reasons.append("gate_set_hash_mismatch")

        provider_results.append({
            "provider_id": provider_id,
            "decision": "ALLOW_EVIDENCE_REGISTRY_ONLY" if not provider_reasons else "DENY",
            "reasons": provider_reasons,
        })
        reasons.extend(f"{provider_id or 'unknown'}:{reason}" for reason in provider_reasons)

    expected_registry_hash = _sha256(providers)
    if report.get("registry_hash") != expected_registry_hash:
        reasons.append("registry_hash_mismatch")

    decision = "ALLOW_EVIDENCE_REGISTRY_ONLY" if not reasons else "DENY"
    return {
        "schema": "stegverse.stegcore.provider_migration_gate_evidence_admissibility.v1",
        "decision": decision,
        "evidence_only": True,
        "provider_count": len(providers),
        "verified_gate_count": verified_gate_count,
        "blocked_gate_count": blocked_gate_count,
        "provider_results": provider_results,
        "reasons": reasons,
        "source_registry_hash": report.get("registry_hash"),
        "manual_action_required": False,
        "production_mutation_allowed": False,
        "execution_authority": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "continuity_receipt_minted": False,
    }
