"""Transport-neutral external reference adapters for SV-INTERLOCK.

COMPAT wraps an external surface that does not natively emit StegVerse lineage.
LINEAGE binds corresponding external manifest/receipt lineage when a peer does.
Neither mode transfers authority, route admission, credential authority, or KV standing.
"""

from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

SCHEMA = "stegos.interlock_reference_adapter.v1"
PROTOCOL_VERSION = "SV-INTERLOCK-v0.4-candidate"
MODES = frozenset({"COMPAT", "LINEAGE"})


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def build_reference_adapter(
    *,
    mode: str,
    exchange_id: str,
    lineage_id: str,
    external_system_id: str,
    external_interface_ref: str,
    wrapper_manifest_ref: str,
    wrapper_receipt_refs: Sequence[str],
    external_manifest_ref: str | None = None,
    external_receipt_refs: Sequence[str] = (),
    correspondence_evidence_refs: Sequence[str] = (),
    master_records_evidence_refs: Sequence[str] = (),
) -> dict[str, Any]:
    if mode not in MODES:
        raise ValueError("unsupported reference adapter mode")
    if not all((exchange_id, lineage_id, external_system_id, external_interface_ref, wrapper_manifest_ref)):
        raise ValueError("reference adapter identity bindings are required")
    wrapper_receipts = list(dict.fromkeys(wrapper_receipt_refs))
    if not wrapper_receipts:
        raise ValueError("reference adapter requires StegVerse wrapper receipt evidence")

    external_receipts = list(dict.fromkeys(external_receipt_refs))
    native_lineage = mode == "LINEAGE"
    if native_lineage:
        if not external_manifest_ref:
            raise ValueError("LINEAGE mode requires external manifest lineage")
        if not external_receipts:
            raise ValueError("LINEAGE mode requires external receipt lineage")
    elif external_manifest_ref is not None or external_receipts:
        raise ValueError("COMPAT mode cannot claim native external lineage")

    basis = {
        "mode": mode,
        "exchange_id": exchange_id,
        "lineage_id": lineage_id,
        "external_system_id": external_system_id,
        "external_interface_ref": external_interface_ref,
        "wrapper_manifest_ref": wrapper_manifest_ref,
        "wrapper_receipt_refs": wrapper_receipts,
        "external_manifest_ref": external_manifest_ref,
        "external_receipt_refs": external_receipts,
    }

    return {
        "schema": SCHEMA,
        "protocol_version": PROTOCOL_VERSION,
        "adapter_id": "adapter-" + _digest(basis)[:24],
        **basis,
        "native_external_lineage": native_lineage,
        "correspondence_evidence_refs": list(dict.fromkeys(correspondence_evidence_refs)),
        "master_records_projection": {
            "required": True,
            "authority_effect": "NONE",
            "evidence_refs": list(dict.fromkeys(master_records_evidence_refs)),
        },
        "shared_authority": False,
        "credential_authority": "TV/TVC",
        "authority_effect": "NONE",
    }


def validate_reference_adapter(adapter: Mapping[str, Any]) -> None:
    if adapter.get("schema") != SCHEMA:
        raise ValueError("reference adapter schema is not canonical")
    if adapter.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("reference adapter protocol version mismatch")
    mode = adapter.get("mode")
    if mode not in MODES:
        raise ValueError("unsupported reference adapter mode")
    if not all(
        adapter.get(field)
        for field in (
            "adapter_id",
            "exchange_id",
            "lineage_id",
            "external_system_id",
            "external_interface_ref",
            "wrapper_manifest_ref",
        )
    ):
        raise ValueError("reference adapter identity bindings are incomplete")
    wrapper_receipts = adapter.get("wrapper_receipt_refs")
    if not isinstance(wrapper_receipts, list) or not wrapper_receipts:
        raise ValueError("reference adapter requires wrapper receipt lineage")

    if adapter.get("credential_authority") != "TV/TVC":
        raise ValueError("reference adapter cannot replace TV/TVC credential authority")
    if adapter.get("shared_authority") is not False:
        raise ValueError("corresponding lineage cannot create shared authority")
    if adapter.get("authority_effect") != "NONE":
        raise ValueError("reference adapter cannot grant authority")
    projection = adapter.get("master_records_projection")
    if not isinstance(projection, Mapping) or projection.get("authority_effect") != "NONE":
        raise ValueError("Master Records projection cannot grant authority")

    external_manifest = adapter.get("external_manifest_ref")
    external_receipts = adapter.get("external_receipt_refs")
    if mode == "LINEAGE":
        if adapter.get("native_external_lineage") is not True:
            raise ValueError("LINEAGE mode must declare native external lineage")
        if not external_manifest:
            raise ValueError("LINEAGE mode requires external manifest lineage")
        if not isinstance(external_receipts, list) or not external_receipts:
            raise ValueError("LINEAGE mode requires external receipt lineage")
    else:
        if adapter.get("native_external_lineage") is not False:
            raise ValueError("COMPAT mode cannot claim native external lineage")
        if external_manifest is not None or external_receipts not in ([], None):
            raise ValueError("COMPAT mode cannot smuggle native external lineage")


def validate_adapter_lineage_binding(*, adapter: Mapping[str, Any], lineage: Mapping[str, Any]) -> None:
    validate_reference_adapter(adapter)
    if adapter.get("exchange_id") != lineage.get("exchange_id"):
        raise ValueError("reference adapter exchange identity mismatch")
    if adapter.get("lineage_id") != lineage.get("lineage_id"):
        raise ValueError("reference adapter lineage identity mismatch")
    if lineage.get("authority_effect") != "NONE":
        raise ValueError("bound universal lineage cannot grant authority")
