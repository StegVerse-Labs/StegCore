from __future__ import annotations

"""Shared-backing provider contract for canonical manifest receipt records.

StegCore owns exact-run receipt semantics; Master Records holds the durable
organization record. This module serializes one already-governed immutable run
into the Master Records manifest-receipt record contract without granting new
authority. Wire names follow MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002: the
request carries ``record_requested`` and the response carries ``record_status``
and ``record_grants_*`` under the organization-record receipt schema. Responses
from Master Records deployments that predate the migration are still accepted
through the ``LEGACY_*`` names below.
"""

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol

from .manifest_receipts import ManifestReceiptRecord


MASTER_RECORDS_SUBMISSION_SCHEMA = "stegverse.master-records.manifest-receipt-submission.v1"
MASTER_RECORDS_ORGANIZATION_RECORD_RECEIPT_SCHEMA = "stegverse.master-records.manifest-receipt-organization-record-receipt.v1"
# Pre-migration names accepted from deployed Master Records services
# (MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002). Never emitted.
LEGACY_MASTER_RECORDS_RECEIPT_SCHEMA = "stegverse.master-records.manifest-receipt-custody-receipt.v1"
LEGACY_RECORD_FIELD_PREFIX = "custody_"
RECORD_RESPONSE_SCHEMAS = frozenset({MASTER_RECORDS_ORGANIZATION_RECORD_RECEIPT_SCHEMA, LEGACY_MASTER_RECORDS_RECEIPT_SCHEMA})


def _record_field(response: Mapping[str, Any], name: str) -> Any:
    """Read ``record_<name>``, falling back to the legacy pre-migration field."""
    key = "record_" + name
    if key in response:
        return response[key]
    return response.get(LEGACY_RECORD_FIELD_PREFIX + name)


class ManifestReceiptBacking(Protocol):
    def retain(self, record: ManifestReceiptRecord, evidence_package: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def evidence_package(self, manifest_receipt_id: str) -> Mapping[str, Any]: ...
    def reconstruct(self, manifest_receipt_id: str) -> Mapping[str, Any]: ...


def build_master_records_submission(
    record: ManifestReceiptRecord,
    evidence_package: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the canonical non-authorizing exact-run organization-record request."""
    if record.locator_grants_authority:
        raise ValueError("manifest_receipt_locator_cannot_grant_authority")
    if str(evidence_package.get("manifest_receipt_id") or "").upper() != record.manifest_receipt_id.upper():
        raise ValueError("manifest_receipt_id_mismatch")
    if evidence_package.get("transaction_id") != record.transaction_id:
        raise ValueError("manifest_receipt_transaction_id_mismatch")
    if evidence_package.get("receipt_chain_head") != record.receipt_chain_head:
        raise ValueError("manifest_receipt_chain_head_mismatch")
    if evidence_package.get("canonical_runtime_identity") != record.canonical_runtime_identity:
        raise ValueError("manifest_receipt_runtime_identity_mismatch")

    manifest = evidence_package.get("manifest")
    if not isinstance(manifest, Mapping):
        raise ValueError("manifest_receipt_manifest_missing")
    manifest_hash = str(manifest.get("manifest_hash") or "")
    if manifest_hash != record.manifest_hash:
        raise ValueError("manifest_receipt_manifest_hash_mismatch")

    package = dict(evidence_package)
    package.update(
        {
            "manifest_receipt_id": record.manifest_receipt_id,
            "transaction_id": record.transaction_id,
            "manifest_hash": record.manifest_hash,
            "receipt_chain_head": record.receipt_chain_head,
            "canonical_runtime_identity": record.canonical_runtime_identity,
            "record_hash": record.record_hash,
            "locator_grants_authority": False,
        }
    )
    return {
        "schema": MASTER_RECORDS_SUBMISSION_SCHEMA,
        "evidence_package": package,
        "record_requested": True,
        "authority_requested": False,
    }


def verify_record_response(record: ManifestReceiptRecord, response: Mapping[str, Any]) -> None:
    if response.get("schema") not in RECORD_RESPONSE_SCHEMAS:
        raise ValueError("master_records_record_response_schema_invalid")
    if str(response.get("manifest_receipt_id") or "").upper() != record.manifest_receipt_id.upper():
        raise ValueError("master_records_record_receipt_id_mismatch")
    if response.get("transaction_id") != record.transaction_id:
        raise ValueError("master_records_record_transaction_id_mismatch")
    if _record_field(response, "status") != "RECORDED":
        raise ValueError("master_records_record_not_recorded")
    if response.get("locator_grants_authority") is not False:
        raise ValueError("master_records_record_authority_boundary_invalid:locator_grants_authority")
    for name in ("grants_execution_authority", "grants_admissibility"):
        if _record_field(response, name) is not False:
            raise ValueError(f"master_records_record_authority_boundary_invalid:record_{name}")


# Deprecated alias kept for callers of the pre-migration name.
verify_custody_response = verify_record_response


@dataclass
class MasterRecordsManifestReceiptProvider:
    """Transport-neutral shared-backing adapter.

    The callables may be HTTP, local service, test fixture, or another TV/TVC-
    admitted transport.  This class does not resolve credentials or select a
    provider; it validates the exact-run organization-record contract around that transport.
    """

    submit_call: Callable[[Mapping[str, Any]], Mapping[str, Any]]
    evidence_call: Callable[[str], Mapping[str, Any]]
    reconstruction_call: Callable[[str], Mapping[str, Any]]

    def retain(
        self,
        record: ManifestReceiptRecord,
        evidence_package: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        request = build_master_records_submission(record, evidence_package)
        response = dict(self.submit_call(request))
        verify_record_response(record, response)
        return response

    def evidence_package(self, manifest_receipt_id: str) -> Mapping[str, Any]:
        response = dict(self.evidence_call(manifest_receipt_id.strip().upper()))
        if str(response.get("manifest_receipt_id") or "").upper() != manifest_receipt_id.strip().upper():
            raise ValueError("master_records_evidence_receipt_id_mismatch")
        if response.get("locator_grants_authority") is not False:
            raise ValueError("master_records_evidence_authority_boundary_invalid")
        if not isinstance(response.get("evidence_package"), Mapping):
            raise ValueError("master_records_evidence_package_missing")
        return response

    def reconstruct(self, manifest_receipt_id: str) -> Mapping[str, Any]:
        response = dict(self.reconstruction_call(manifest_receipt_id.strip().upper()))
        if str(response.get("manifest_receipt_id") or "").upper() != manifest_receipt_id.strip().upper():
            raise ValueError("master_records_reconstruction_receipt_id_mismatch")
        if response.get("consequence_reexecuted") is not False:
            raise ValueError("master_records_reconstruction_reexecuted_consequence")
        if response.get("reconstruction_grants_authority") is not False:
            raise ValueError("master_records_reconstruction_authority_boundary_invalid")
        return response
