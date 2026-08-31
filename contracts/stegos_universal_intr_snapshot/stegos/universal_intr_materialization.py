"""Deterministic event-ephemeral materialization requests for Universal InTr.

This module bridges canonical transport intent to a durable request for the
existing subsystem execution owner. The request is non-authorizing: it does not
mint claims/fences, start workers, grant execution authority, or change TV/TVC
credential authority.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from stegos.universal_intr_transport import (
    INTENT_SCHEMA,
    canonical_json,
    sha256_uri,
    validate_transport_intent,
)

MATERIALIZATION_SCHEMA = "stegverse.universal-intr-materialization-request/v1"
MATERIALIZATION_STATE = "QUEUED_FOR_EVENT_EPHEMERAL_MATERIALIZATION"


class UniversalInTrMaterializationError(ValueError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")


def _request_hash(value: Mapping[str, Any]) -> str:
    return sha256_uri(dict(value))


def build_materialization_request(
    intent: Mapping[str, Any],
    *,
    payload_ref: str,
    downstream_owner_ref: str,
) -> dict[str, Any]:
    """Build one non-authorizing request from a canonical Universal InTr intent."""
    try:
        validate_transport_intent(intent)
    except Exception as exc:
        raise UniversalInTrMaterializationError(f"transport_intent_invalid:{exc}") from exc

    if intent.get("schema") != INTENT_SCHEMA:
        raise UniversalInTrMaterializationError("transport_intent_schema_invalid")
    if not isinstance(payload_ref, str) or not payload_ref.strip():
        raise UniversalInTrMaterializationError("payload_ref_required")
    if not isinstance(downstream_owner_ref, str) or not downstream_owner_ref.strip():
        raise UniversalInTrMaterializationError("downstream_owner_ref_required")

    semantics = intent["transport_semantics"]
    if semantics.get("event_triggered") is not True:
        raise UniversalInTrMaterializationError("event_triggered_required")
    if semantics.get("always_on_receiver_required") is not False:
        raise UniversalInTrMaterializationError("always_on_receiver_forbidden")
    if semantics.get("receiver_unavailable_disposition") != "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION":
        raise UniversalInTrMaterializationError("receiver_unavailable_disposition_invalid")

    intent_hash = sha256_uri(dict(intent))
    identity_basis = {
        "transport_intent_hash": intent_hash,
        "operation_id": intent["operation_id"],
        "packet_id": intent["packet_id"],
        "payload_hash": intent["payload_hash"],
        "destination": intent["destination"],
    }
    materialization_id = "INTR-MAT-" + sha256(_canonical_bytes(identity_basis)).hexdigest()[:24]

    body = {
        "schema": MATERIALIZATION_SCHEMA,
        "materialization_id": materialization_id,
        "state": MATERIALIZATION_STATE,
        "transport_schema": INTENT_SCHEMA,
        "transport_protocol": "InTr",
        "transport_intent_hash": intent_hash,
        "operation_id": intent["operation_id"],
        "packet_id": intent["packet_id"],
        "payload_hash": intent["payload_hash"],
        "payload_ref": payload_ref.strip(),
        "destination": dict(intent["destination"]),
        "boundary_path": list(intent["boundary_path"]),
        "downstream_owner_ref": downstream_owner_ref.strip(),
        "event_triggered": True,
        "always_on_receiver_required": False,
        "second_user_device_required": False,
        "receiver_unavailable_disposition": "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION",
        "exact_packet_transport_retry_allowed": True,
        "blind_consequence_retry_allowed": False,
        "interlock_required": True,
        "request_grants_execution_authority": False,
        "claim_or_fence_minted": False,
        "transport_grants_execution_authority": False,
        "credential_authority": "TV/TVC",
        "github_token_runtime_authority": "NONE",
        "authority_transfer": False,
        "authority_effect": "NONE_REQUEST_ONLY",
    }
    return {**body, "request_hash": _request_hash(body)}


def validate_materialization_request(
    request: Mapping[str, Any],
    *,
    intent: Mapping[str, Any],
) -> None:
    expected = build_materialization_request(
        intent,
        payload_ref=str(request.get("payload_ref") or ""),
        downstream_owner_ref=str(request.get("downstream_owner_ref") or ""),
    )
    if dict(request) != expected:
        raise UniversalInTrMaterializationError("materialization_request_binding_mismatch")


def persist_materialization_request(
    root: Path,
    request: Mapping[str, Any],
) -> Path:
    """Persist exactly once; identical retry is idempotent, mismatch fails closed."""
    if request.get("schema") != MATERIALIZATION_SCHEMA:
        raise UniversalInTrMaterializationError("materialization_schema_invalid")
    materialization_id = request.get("materialization_id")
    if not isinstance(materialization_id, str) or not materialization_id.startswith("INTR-MAT-"):
        raise UniversalInTrMaterializationError("materialization_id_invalid")

    body = dict(request)
    claimed = body.pop("request_hash", None)
    if claimed != _request_hash(body):
        raise UniversalInTrMaterializationError("materialization_request_hash_invalid")

    directory = root.expanduser().resolve() / "intr-materialization"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{materialization_id}.json"
    serialized = json.dumps(dict(request), indent=2, sort_keys=True) + "\n"
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing == serialized:
            return path
        raise UniversalInTrMaterializationError("materialization_write_once_collision")
    path.write_text(serialized, encoding="utf-8")
    if path.read_text(encoding="utf-8") != serialized:
        raise UniversalInTrMaterializationError("materialization_persistence_verification_failed")
    return path
