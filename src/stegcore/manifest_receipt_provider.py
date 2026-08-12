from __future__ import annotations

"""Shared-backing provider contract for canonical manifest receipt records.

StegCore owns exact-run receipt semantics; Master Records owns durable custody.
This module serializes one already-governed immutable run into the Master Records
manifest-receipt custody contract without granting new authority.
"""

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol

from .manifest_receipts import ManifestReceiptRecord


MASTER_RECORDS_SUBMISSION_SCHEMA = "stegverse.master-records.manifest-receipt-submission.v1"
MASTER_RECORDS_CUSTODY_RECEIPT_SCHEMA = "stegverse.master-records.manifest-receipt-custody-receipt.v1"


class ManifestReceiptBacking(Protocol):
    def retain(self, record: ManifestReceiptRecord, evidence_package: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def evidence_package(self, manifest_receipt_id: str) -> Mapping[str, Any]: ...
    def reconstruct(self, manifest_receipt_id: str) -> Mapping[str, Any]: ...


def build_master_records_submission(
    record: ManifestReceiptRecord,
    evidence_package: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the canonical non-authorizing exact-run custody request."""
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
        "custody_requested": True,
        "authority_requested": False,
    }


def verify_custody_response(record: ManifestReceiptRecord, response: Mapping[str, Any]) -> None:
    if response.get("schema") != MASTER_RECORDS_CUSTODY_RECEIPT_SCHEMA:
        raise ValueError("master_records_custody_response_schema_invalid")
    if str(response.get("manifest_receipt_id") or "").upper() != record.manifest_receipt_id.upper():
        raise ValueError("master_records_custody_receipt_id_mismatch")
    if response.get("transaction_id") != record.transaction_id:
        raise ValueError("master_records_custody_transaction_id_mismatch")
    if response.get("custody_status") != "RECORDED":
        raise ValueError("master_records_custody_not_recorded")
    for key in (
        "locator_grants_authority",
        "custody_grants_execution_authority",
        "custody_grants_admissibility",
    ):
        if response.get(key) is not False:
            raise ValueError(f"master_records_custody_authority_boundary_invalid:{key}")


@dataclass
class MasterRecordsManifestReceiptProvider:
    """Transport-neutral shared-backing adapter.

    The callables may be HTTP, local service, test fixture, or another TV/TVC-
    admitted transport.  This class does not resolve credentials or select a
    provider; it validates the exact-run custody contract around that transport.
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
        verify_custody_response(record, response)
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
