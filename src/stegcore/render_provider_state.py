from __future__ import annotations

import hashlib
import json
from typing import Any

EXPECTED_SCHEMA = "stegverse.governance.render_provider_state.v1"
FORBIDDEN_TRUE = {
    "environment_values_retained",
    "deploy_hooks_retained",
    "credentials_retained",
    "raw_secret_material_retained",
    "manual_action_required",
    "production_mutation_allowed",
    "execution_authority",
    "traffic_cutover_authority",
    "cancellation_authority",
    "provider_retirement_authority",
    "continuity_receipt_minted",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def evaluate_render_provider_state(report: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if report.get("schema") != EXPECTED_SCHEMA:
        reasons.append("schema_mismatch")
    if report.get("provider_id") != "render":
        reasons.append("provider_mismatch")
    for key in FORBIDDEN_TRUE:
        if report.get(key) is not False:
            reasons.append(f"forbidden_or_missing:{key}")

    claimed = report.get("report_sha256")
    payload = dict(report)
    payload.pop("report_sha256", None)
    if not _valid_hash(claimed) or claimed != _sha256(payload):
        reasons.append("report_hash_invalid")

    configs = report.get("repository_configs")
    services = report.get("services")
    if not isinstance(configs, list) or not isinstance(services, list):
        reasons.append("records_invalid")
        configs, services = [], []

    for record in configs:
        if not isinstance(record, dict):
            reasons.append("config_record_invalid")
            continue
        for config in record.get("config_paths", []):
            if not _valid_hash(config.get("content_sha256")):
                reasons.append("config_hash_invalid")

    api_authenticated = report.get("api_state") == "AUTHENTICATED_RENDER_METADATA"
    full_export = report.get("state") == "RENDER_STATE_EXPORTED" and api_authenticated and len(services) > 0
    if report.get("state") not in {"RENDER_STATE_EXPORTED", "BLOCKED_PARTIAL_RENDER_STATE"}:
        reasons.append("state_invalid")
    if report.get("state") == "RENDER_STATE_EXPORTED" and not full_export:
        reasons.append("authenticated_service_metadata_missing")

    decision = "ALLOW_RENDER_PROVIDER_EVIDENCE_ONLY" if not reasons else "DENY"
    result = {
        "schema": "stegverse.stegcore.render_provider_state_admissibility.v1",
        "decision": decision,
        "reasons": sorted(set(reasons)),
        "source_report_sha256": claimed if _valid_hash(claimed) else None,
        "configuration_discovery_verified": not reasons and len(configs) > 0,
        "authenticated_provider_metadata_verified": not reasons and api_authenticated,
        "export_verified": not reasons and full_export,
        "evidence_only": True,
        "manual_action_required": False,
        "production_mutation_allowed": False,
        "execution_authority": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "continuity_receipt_minted": False,
    }
    result["evidence_sha256"] = _sha256(result)
    return result
