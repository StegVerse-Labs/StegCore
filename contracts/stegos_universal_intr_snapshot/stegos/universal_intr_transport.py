"""Canonical event-triggered Interlock/InTr data transport invariant.

The invariant is topology and receipt-chain policy, not transport authority.
Every cross-boundary movement follows the canonical adjacent boundary stack:

SKAP_VAULT <-> KV <-> DEVICE_SYSTEM <-> STEGOS_ECOSYSTEM <-> EXTERNAL_SYSTEM

A receiver may be materialized event-ephemerally or the exact packet may be
durably queued. An always-on application receiver and a second user device are
never prerequisites to transport initiation.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

INTENT_SCHEMA = "stegverse.universal-intr-transport/v1"
RECEIPT_SCHEMA = "stegverse.intr.hop_receipt/v1"
BOUNDARIES = (
    "SKAP_VAULT",
    "KV",
    "DEVICE_SYSTEM",
    "STEGOS_ECOSYSTEM",
    "EXTERNAL_SYSTEM",
)
RECEIPT_FIELDS = {
    "schema",
    "receipt_id",
    "packet_id",
    "hop_index",
    "direction",
    "from_role",
    "to_role",
    "operation_hash",
    "payload_hash",
    "prior_receipt_hash",
    "boundary_identity_ref",
    "boundary_verification",
    "transition_state",
    "secret_plaintext_present",
    "authority_transfer",
    "recorded_at",
    "receipt_hash",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_uri(value: Any) -> str:
    if isinstance(value, (bytes, bytearray)):
        data = bytes(value)
    elif isinstance(value, str):
        data = value.encode("utf-8")
    else:
        data = canonical_json(value).encode("utf-8")
    return "sha256:" + sha256(data).hexdigest()


def _require_sha256(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
        raise ValueError(f"{label} must be sha256-prefixed")
    if any(ch not in "0123456789abcdef" for ch in value[7:]):
        raise ValueError(f"{label} must be lowercase hexadecimal")


def canonical_boundary_path(source: str, destination: str) -> list[str]:
    if source not in BOUNDARIES or destination not in BOUNDARIES:
        raise ValueError("unknown StegVerse transport boundary")
    start = BOUNDARIES.index(source)
    stop = BOUNDARIES.index(destination)
    if start <= stop:
        return list(BOUNDARIES[start : stop + 1])
    return list(reversed(BOUNDARIES[stop : start + 1]))


def build_transport_intent(
    *,
    operation_id: str,
    payload_hash: str,
    source_boundary: str,
    source_subsystem: str,
    destination_boundary: str,
    destination_subsystem: str,
    prior_transport_receipt_hash: str | None = None,
) -> dict[str, Any]:
    if not operation_id or not source_subsystem or not destination_subsystem:
        raise ValueError("operation and subsystem identities are required")
    _require_sha256(payload_hash, "payload_hash")
    if prior_transport_receipt_hash is not None:
        _require_sha256(prior_transport_receipt_hash, "prior_transport_receipt_hash")
    boundary_path = canonical_boundary_path(source_boundary, destination_boundary)
    basis = {
        "operation_id": operation_id,
        "payload_hash": payload_hash,
        "source_boundary": source_boundary,
        "source_subsystem": source_subsystem,
        "destination_boundary": destination_boundary,
        "destination_subsystem": destination_subsystem,
        "boundary_path": boundary_path,
    }
    return {
        "schema": INTENT_SCHEMA,
        "protocol": "InTr",
        "operation_id": operation_id,
        "packet_id": "INTR-" + sha256(canonical_json(basis).encode("utf-8")).hexdigest()[:24],
        "payload_hash": payload_hash,
        "prior_transport_receipt_hash": prior_transport_receipt_hash,
        "source": {"boundary": source_boundary, "subsystem": source_subsystem},
        "destination": {"boundary": destination_boundary, "subsystem": destination_subsystem},
        "boundary_path": boundary_path,
        "interlock_required": True,
        "transport_semantics": {
            "event_triggered": True,
            "always_on_receiver_required": False,
            "second_user_device_required": False,
            "receiver_unavailable_disposition": "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION",
            "exact_packet_transport_retry_allowed": True,
            "blind_consequence_retry_allowed": False,
        },
        "authority": {
            "authority_transfer": False,
            "transport_grants_execution_authority": False,
            "credential_authority": "TV/TVC",
        },
        "receipt_chain": {
            "required": True,
            "receipt_schema": RECEIPT_SCHEMA,
            "payload_plaintext_in_receipts": False,
            "prior_hash_required_after_first_hop": True,
        },
    }


def validate_transport_intent(intent: Mapping[str, Any]) -> None:
    if intent.get("schema") != INTENT_SCHEMA or intent.get("protocol") != "InTr":
        raise ValueError("universal transport schema/protocol mismatch")
    _require_sha256(intent.get("payload_hash"), "payload_hash")
    prior_transport_receipt_hash = intent.get("prior_transport_receipt_hash")
    if prior_transport_receipt_hash is not None:
        _require_sha256(prior_transport_receipt_hash, "prior_transport_receipt_hash")
    source = intent.get("source")
    destination = intent.get("destination")
    if not isinstance(source, Mapping) or not isinstance(destination, Mapping):
        raise ValueError("source and destination endpoints are required")
    expected_path = canonical_boundary_path(str(source.get("boundary")), str(destination.get("boundary")))
    if list(intent.get("boundary_path") or []) != expected_path:
        raise ValueError("transport boundary path skips or reorders canonical Interlock boundaries")
    if not source.get("subsystem") or not destination.get("subsystem"):
        raise ValueError("source/destination subsystem identity required")
    if intent.get("interlock_required") is not True:
        raise ValueError("every transport hop requires Interlock")

    semantics = intent.get("transport_semantics")
    if not isinstance(semantics, Mapping):
        raise ValueError("transport semantics required")
    expected_semantics = {
        "event_triggered": True,
        "always_on_receiver_required": False,
        "second_user_device_required": False,
        "receiver_unavailable_disposition": "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION",
        "exact_packet_transport_retry_allowed": True,
        "blind_consequence_retry_allowed": False,
    }
    for key, value in expected_semantics.items():
        if semantics.get(key) != value:
            raise ValueError(f"transport semantic violation: {key}")

    authority = intent.get("authority")
    if not isinstance(authority, Mapping):
        raise ValueError("transport authority block required")
    if authority.get("authority_transfer") is not False:
        raise ValueError("transport cannot transfer authority")
    if authority.get("transport_grants_execution_authority") is not False:
        raise ValueError("transport cannot grant execution authority")
    if authority.get("credential_authority") != "TV/TVC":
        raise ValueError("credential authority must remain TV/TVC")

    receipt_chain = intent.get("receipt_chain")
    if not isinstance(receipt_chain, Mapping):
        raise ValueError("receipt-chain policy required")
    if receipt_chain.get("required") is not True:
        raise ValueError("transport receipt chain is mandatory")
    if receipt_chain.get("receipt_schema") != RECEIPT_SCHEMA:
        raise ValueError("unexpected transport receipt schema")
    if receipt_chain.get("payload_plaintext_in_receipts") is not False:
        raise ValueError("transport receipts may not contain payload plaintext")
    if receipt_chain.get("prior_hash_required_after_first_hop") is not True:
        raise ValueError("receipt chaining cannot be disabled")


def build_hop_receipt(
    intent: Mapping[str, Any],
    *,
    hop_index: int,
    receipt_id: str,
    boundary_identity_ref: str,
    recorded_at: str,
    prior_receipt_hash: str | None,
    transition_state: str = "RECEIVED",
) -> dict[str, Any]:
    validate_transport_intent(intent)
    path = list(intent["boundary_path"])
    hop_count = max(1, len(path) - 1)
    if not 1 <= hop_index <= hop_count:
        raise ValueError("hop index must identify one adjacent boundary or subsystem transition")
    expected_initial_prior = intent.get("prior_transport_receipt_hash")
    if hop_index == 1:
        if prior_receipt_hash != expected_initial_prior:
            raise ValueError("first hop prior receipt must match transport intent lineage")
    else:
        _require_sha256(prior_receipt_hash, "prior_receipt_hash")
    if transition_state not in {"FORWARDED", "RECEIVED", "STAGED"}:
        raise ValueError("unsupported transport transition state")
    operation_hash = sha256_uri(
        {
            "operation_id": intent["operation_id"],
            "packet_id": intent["packet_id"],
            "payload_hash": intent["payload_hash"],
        }
    )
    body = {
        "schema": RECEIPT_SCHEMA,
        "receipt_id": receipt_id,
        "packet_id": intent["packet_id"],
        "hop_index": hop_index,
        "direction": "FORWARD",
        "from_role": path[hop_index - 1] if len(path) > 1 else path[0],
        "to_role": path[hop_index] if len(path) > 1 else path[0],
        "operation_hash": operation_hash,
        "payload_hash": intent["payload_hash"],
        "prior_receipt_hash": prior_receipt_hash,
        "boundary_identity_ref": boundary_identity_ref,
        "boundary_verification": "VERIFIED",
        "transition_state": transition_state,
        "secret_plaintext_present": False,
        "authority_transfer": False,
        "recorded_at": recorded_at,
    }
    return {**body, "receipt_hash": sha256_uri(body)}


def validate_receipt_chain(intent: Mapping[str, Any], receipts: Sequence[Mapping[str, Any]]) -> None:
    validate_transport_intent(intent)
    path = list(intent["boundary_path"])
    hop_count = max(1, len(path) - 1)
    if len(receipts) > hop_count:
        raise ValueError("receipt chain contains more hops than the canonical path")
    prior: str | None = intent.get("prior_transport_receipt_hash")
    operation_hash = sha256_uri(
        {
            "operation_id": intent["operation_id"],
            "packet_id": intent["packet_id"],
            "payload_hash": intent["payload_hash"],
        }
    )
    for index, receipt in enumerate(receipts, start=1):
        if set(receipt) != RECEIPT_FIELDS:
            raise ValueError("transport receipt field set is not canonical")
        if receipt.get("schema") != RECEIPT_SCHEMA:
            raise ValueError("transport receipt schema mismatch")
        if receipt.get("packet_id") != intent["packet_id"] or receipt.get("hop_index") != index:
            raise ValueError("transport receipt packet/hop binding mismatch")
        expected_from = path[index - 1] if len(path) > 1 else path[0]
        expected_to = path[index] if len(path) > 1 else path[0]
        if receipt.get("from_role") != expected_from or receipt.get("to_role") != expected_to:
            raise ValueError("transport receipt boundary adjacency mismatch")
        if receipt.get("operation_hash") != operation_hash or receipt.get("payload_hash") != intent["payload_hash"]:
            raise ValueError("transport receipt operation/payload binding mismatch")
        if receipt.get("prior_receipt_hash") != prior:
            raise ValueError("transport receipt prior-hash chain mismatch")
        if receipt.get("boundary_verification") != "VERIFIED":
            raise ValueError("transport receipt boundary not verified")
        if receipt.get("secret_plaintext_present") is not False or receipt.get("authority_transfer") is not False:
            raise ValueError("transport receipt authority/plaintext violation")
        body = dict(receipt)
        claimed = body.pop("receipt_hash")
        if claimed != sha256_uri(body):
            raise ValueError("transport receipt hash mismatch")
        prior = claimed
