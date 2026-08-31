"""Reusable canonical Universal Interlock/InTr transport backbone.

Purpose-specific connectors are declarative profiles over this module.  A
profile may narrow operations, payload schema, endpoints, custody behaviour,
and projection, but it cannot change transport authority or receipt policy.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from stegos.universal_intr_materialization import build_materialization_request
from stegos.universal_intr_transport import (
    build_hop_receipt,
    build_transport_intent,
    canonical_boundary_path,
    canonical_json,
    sha256_uri,
    validate_receipt_chain,
    validate_transport_intent,
)

PROFILE_SCHEMA = "stegverse.universal-intr.connector-profile/v1"
REGISTRY_SCHEMA = "stegverse.universal-intr.connector-profile-registry/v1"
BACKBONE_RESULT_SCHEMA = "stegverse.universal-intr.backbone-result/v1"
QUEUE_RESULT_SCHEMA = "stegverse.universal-intr.queued-packet/v1"

_PROFILE_FIELDS = {
    "schema", "profile_id", "request_class", "payload_schema", "operations",
    "source", "destination", "response", "downstream_owner_ref",
    "custody_mode", "display_projection", "authorization_required",
    "authority_effect",
}
_ENDPOINT_FIELDS = {"boundary", "subsystem"}
_CUSTODY_MODES = {"NONE", "REFERENCE", "EXACT_BYTES", "CANONICAL_STATE_CANDIDATE"}


class UniversalInTrBackboneError(ValueError):
    pass


def canonical_payload_bytes(payload: Any) -> bytes:
    """Preserve supplied bytes; deterministically encode structured payloads."""
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, bytearray):
        return bytes(payload)
    if isinstance(payload, str):
        return payload.encode("utf-8")
    if isinstance(payload, (Mapping, list, tuple)):
        return canonical_json(payload).encode("utf-8")
    raise UniversalInTrBackboneError("payload_type_unsupported")


def payload_hash_uri(payload_bytes: bytes) -> str:
    import hashlib
    return "sha256:" + hashlib.sha256(payload_bytes).hexdigest()


def _validate_endpoint(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, Mapping) or set(value) != _ENDPOINT_FIELDS:
        raise UniversalInTrBackboneError(f"{label}_endpoint_invalid")
    boundary = value.get("boundary")
    subsystem = value.get("subsystem")
    if not isinstance(boundary, str) or not isinstance(subsystem, str) or not subsystem:
        raise UniversalInTrBackboneError(f"{label}_endpoint_invalid")
    try:
        canonical_boundary_path(boundary, boundary)
    except Exception as exc:
        raise UniversalInTrBackboneError(f"{label}_boundary_invalid") from exc
    return {"boundary": boundary, "subsystem": subsystem}


@dataclass(frozen=True)
class ConnectorProfile:
    profile_id: str
    request_class: str
    payload_schema: str
    operations: tuple[str, ...]
    source: dict[str, str]
    destination: dict[str, str]
    response: tuple[dict[str, str], dict[str, str]] | None
    downstream_owner_ref: str
    custody_mode: str
    display_projection: str | None
    authorization_required: bool

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ConnectorProfile":
        if not isinstance(value, Mapping) or set(value) != _PROFILE_FIELDS:
            raise UniversalInTrBackboneError("connector_profile_field_set_invalid")
        if value.get("schema") != PROFILE_SCHEMA:
            raise UniversalInTrBackboneError("connector_profile_schema_invalid")
        if value.get("authority_effect") != "NONE":
            raise UniversalInTrBackboneError("connector_profile_authority_effect_invalid")
        strings = ("profile_id", "request_class", "payload_schema", "downstream_owner_ref")
        if any(not isinstance(value.get(k), str) or not value[k] for k in strings):
            raise UniversalInTrBackboneError("connector_profile_identity_invalid")
        operations = value.get("operations")
        if not isinstance(operations, list) or not operations or len(set(operations)) != len(operations):
            raise UniversalInTrBackboneError("connector_profile_operations_invalid")
        if not all(isinstance(item, str) and item for item in operations):
            raise UniversalInTrBackboneError("connector_profile_operations_invalid")
        source = _validate_endpoint(value.get("source"), "source")
        destination = _validate_endpoint(value.get("destination"), "destination")
        response_value = value.get("response")
        response = None
        if response_value is not None:
            if not isinstance(response_value, Mapping) or set(response_value) != {"source", "destination"}:
                raise UniversalInTrBackboneError("connector_profile_response_invalid")
            response = (
                _validate_endpoint(response_value["source"], "response_source"),
                _validate_endpoint(response_value["destination"], "response_destination"),
            )
        custody_mode = value.get("custody_mode")
        if custody_mode not in _CUSTODY_MODES:
            raise UniversalInTrBackboneError("connector_profile_custody_mode_invalid")
        display = value.get("display_projection")
        if display is not None and (not isinstance(display, str) or not display):
            raise UniversalInTrBackboneError("connector_profile_display_projection_invalid")
        if not isinstance(value.get("authorization_required"), bool):
            raise UniversalInTrBackboneError("connector_profile_authorization_invalid")
        return cls(
            profile_id=value["profile_id"], request_class=value["request_class"],
            payload_schema=value["payload_schema"], operations=tuple(operations),
            source=source, destination=destination, response=response,
            downstream_owner_ref=value["downstream_owner_ref"],
            custody_mode=custody_mode, display_projection=display,
            authorization_required=value["authorization_required"],
        )


@dataclass(frozen=True)
class PreparedPacket:
    profile: ConnectorProfile
    operation: str
    payload_schema: str
    payload_bytes: bytes
    intent: dict[str, Any]

    @property
    def payload_hash(self) -> str:
        return self.intent["payload_hash"]


class CanonicalInTrConnector:
    """One connector implementation parameterized by a validated profile."""

    def __init__(self, profile: ConnectorProfile):
        self.profile = profile

    def prepare(
        self,
        payload: Any,
        *,
        payload_schema: str,
        operation: str,
        operation_id: str,
        prior_receipt_hash: str | None = None,
    ) -> PreparedPacket:
        if operation not in self.profile.operations:
            raise UniversalInTrBackboneError("connector_operation_not_allowed")
        if payload_schema != self.profile.payload_schema:
            raise UniversalInTrBackboneError("connector_payload_schema_mismatch")
        raw = canonical_payload_bytes(payload)
        intent = build_transport_intent(
            operation_id=operation_id,
            payload_hash=payload_hash_uri(raw),
            source_boundary=self.profile.source["boundary"],
            source_subsystem=self.profile.source["subsystem"],
            destination_boundary=self.profile.destination["boundary"],
            destination_subsystem=self.profile.destination["subsystem"],
            prior_transport_receipt_hash=prior_receipt_hash,
        )
        validate_transport_intent(intent)
        return PreparedPacket(self.profile, operation, payload_schema, raw, intent)

    def accept_hop(
        self,
        packet: PreparedPacket,
        *,
        hop_index: int,
        receipt_id: str,
        boundary_identity_ref: str,
        recorded_at: str,
        prior_receipt_hash: str | None,
        transition_state: str = "RECEIVED",
    ) -> dict[str, Any]:
        if payload_hash_uri(packet.payload_bytes) != packet.intent["payload_hash"]:
            raise UniversalInTrBackboneError("exact_packet_hash_mismatch")
        return build_hop_receipt(
            packet.intent, hop_index=hop_index, receipt_id=receipt_id,
            boundary_identity_ref=boundary_identity_ref, recorded_at=recorded_at,
            prior_receipt_hash=prior_receipt_hash,
            transition_state=transition_state,
        )

    def validate_complete(
        self, packet: PreparedPacket, receipts: Sequence[Mapping[str, Any]]
    ) -> dict[str, Any]:
        validate_receipt_chain(packet.intent, receipts)
        required = max(1, len(packet.intent["boundary_path"]) - 1)
        if len(receipts) != required:
            raise UniversalInTrBackboneError("transport_receipt_chain_incomplete")
        return {
            "schema": BACKBONE_RESULT_SCHEMA,
            "state": "TRANSPORT_COMPLETE",
            "profile_id": self.profile.profile_id,
            "request_class": self.profile.request_class,
            "operation": packet.operation,
            "packet_id": packet.intent["packet_id"],
            "payload_hash": packet.payload_hash,
            "terminal_receipt_hash": receipts[-1]["receipt_hash"],
            "custody_mode": self.profile.custody_mode,
            "display_projection": self.profile.display_projection,
            "transport_grants_execution_authority": False,
            "credential_authority": "TV/TVC",
            "authority_effect": "NONE",
        }

    def prepare_response(
        self,
        request_packet: PreparedPacket,
        request_receipts: Sequence[Mapping[str, Any]],
        response_payload: Any,
        *,
        payload_schema: str,
        operation_id: str,
    ) -> PreparedPacket:
        if self.profile.response is None:
            raise UniversalInTrBackboneError("connector_response_not_supported")
        self.validate_complete(request_packet, request_receipts)
        raw = canonical_payload_bytes(response_payload)
        source, destination = self.profile.response
        prior = request_receipts[-1]["receipt_hash"]
        intent = build_transport_intent(
            operation_id=operation_id, payload_hash=payload_hash_uri(raw),
            source_boundary=source["boundary"], source_subsystem=source["subsystem"],
            destination_boundary=destination["boundary"],
            destination_subsystem=destination["subsystem"],
            prior_transport_receipt_hash=prior,
        )
        validate_transport_intent(intent)
        return PreparedPacket(self.profile, "RESPONSE", payload_schema, raw, intent)

    def queue_when_unavailable(
        self,
        packet: PreparedPacket,
        *,
        payload_ref: str,
        queue_writer: Callable[[Mapping[str, Any], bytes], str],
    ) -> dict[str, Any]:
        request = build_materialization_request(
            packet.intent, payload_ref=payload_ref,
            downstream_owner_ref=self.profile.downstream_owner_ref,
        )
        queue_ref = queue_writer(request, packet.payload_bytes)
        if not isinstance(queue_ref, str) or not queue_ref:
            raise UniversalInTrBackboneError("durable_queue_write_failed")
        return {
            "schema": QUEUE_RESULT_SCHEMA,
            "state": "DURABLY_QUEUED",
            "profile_id": self.profile.profile_id,
            "packet_id": packet.intent["packet_id"],
            "payload_hash": packet.payload_hash,
            "queue_ref": queue_ref,
            "materialization_request": request,
            "exact_packet_transport_retry_allowed": True,
            "blind_consequence_retry_allowed": False,
            "request_grants_execution_authority": False,
            "credential_authority": "TV/TVC",
            "authority_effect": "NONE_REQUEST_ONLY",
        }


def load_connector_registry(path: Path) -> dict[str, ConnectorProfile]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema") != REGISTRY_SCHEMA or raw.get("authority_effect") != "NONE":
        raise UniversalInTrBackboneError("connector_registry_invalid")
    if raw.get("credential_authority") != "TV/TVC":
        raise UniversalInTrBackboneError("connector_registry_credential_authority_invalid")
    required = raw.get("canonical_invariants") or {}
    expected = {
        "interlock_required_per_hop": True,
        "receipt_chain_required": True,
        "exact_packet_hash_required": True,
        "always_on_receiver_required": False,
        "second_user_device_required": False,
        "exact_packet_transport_retry_allowed": True,
        "blind_consequence_retry_allowed": False,
        "transport_grants_execution_authority": False,
    }
    if required != expected:
        raise UniversalInTrBackboneError("connector_registry_invariants_invalid")
    profiles = raw.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise UniversalInTrBackboneError("connector_registry_profiles_required")
    parsed = [ConnectorProfile.from_mapping(item) for item in profiles]
    if len({item.profile_id for item in parsed}) != len(parsed):
        raise UniversalInTrBackboneError("connector_profile_id_duplicate")
    return {item.profile_id: item for item in parsed}


def connector_from_registry(path: Path, profile_id: str) -> CanonicalInTrConnector:
    profiles = load_connector_registry(path)
    try:
        return CanonicalInTrConnector(profiles[profile_id])
    except KeyError as exc:
        raise UniversalInTrBackboneError("connector_profile_unknown") from exc
