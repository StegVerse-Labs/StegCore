from __future__ import annotations

"""Canonical user-facing manifest receipt identifiers for exact governed runs.

A manifest_receipt_id is a locator only. It never grants governance authority.
The registry is append-only and provider-neutral, with optional JSONL backing.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from pydantic import BaseModel

from .steggate import canonical_sha256
from .transaction_lifecycle import ManifestedTransactionResult


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ManifestReceiptRecord(BaseModel):
    artifact_type: str = "stegcore.manifest_receipt_record"
    schema_version: str = "1.0"
    manifest_receipt_id: str
    transaction_id: str
    manifest_hash: str
    receipt_chain_head: str
    canonical_runtime_identity: str
    registered_at: str
    result: dict[str, Any]
    locator_grants_authority: bool = False
    record_hash: str


class ReplayReceipt(BaseModel):
    artifact_type: str = "stegcore.manifest_replay_receipt"
    schema_version: str = "1.0"
    original_manifest_receipt_id: str
    replayed_at: str
    original_transaction_id: str
    original_manifest_hash: str
    original_receipt_chain_head: str
    original_disposition: str
    replay_disposition: str
    input_identity_match: bool
    manifest_identity_match: bool
    deterministic_disposition_match: bool
    consequence_reexecuted: bool = False
    replay_result: dict[str, Any]
    receipt_hash: str


class ReconstructionReceipt(BaseModel):
    artifact_type: str = "stegcore.manifest_reconstruction_receipt"
    schema_version: str = "1.0"
    original_manifest_receipt_id: str
    reconstructed_at: str
    transaction_id: str
    chain_verified: bool
    persisted_evidence: list[dict[str, Any]]
    reconstructed_summary: dict[str, Any]
    consequence_reexecuted: bool = False
    receipt_hash: str


def manifest_receipt_id_for(result: ManifestedTransactionResult) -> str:
    locator_material = {
        "transaction_id": result.transaction_id,
        "manifest_hash": result.manifest.manifest_hash,
        "receipt_chain_head": result.replay.receipt_chain_head,
        "canonical_runtime_identity": result.replay.canonical_runtime_identity,
    }
    return "MR-" + canonical_sha256(locator_material).upper()


class ManifestReceiptRegistry:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._records: dict[str, ManifestReceiptRecord] = {}
        if self.path is not None and self.path.exists():
            self._load()

    def _load(self) -> None:
        assert self.path is not None
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            record = ManifestReceiptRecord.model_validate_json(raw)
            self._validate(record)
            if record.manifest_receipt_id in self._records:
                raise ValueError("duplicate manifest_receipt_id in backing store")
            self._records[record.manifest_receipt_id] = record

    @staticmethod
    def _validate(record: ManifestReceiptRecord) -> None:
        if record.locator_grants_authority:
            raise ValueError("manifest receipt locator cannot grant authority")
        body = record.model_dump(mode="json", exclude={"record_hash"})
        if canonical_sha256(body) != record.record_hash:
            raise ValueError("manifest receipt record hash mismatch")

    def register(self, result: ManifestedTransactionResult) -> ManifestReceiptRecord:
        if not result.chain_verified:
            raise ValueError("cannot register unverified transaction receipt chain")
        receipt_id = manifest_receipt_id_for(result)
        existing = self._records.get(receipt_id)
        result_body = result.model_dump(mode="json", exclude_none=False)
        if existing is not None:
            if canonical_sha256(existing.result) != canonical_sha256(result_body):
                raise ValueError("manifest_receipt_id collision with different immutable run")
            return existing
        body = {
            "artifact_type": "stegcore.manifest_receipt_record",
            "schema_version": "1.0",
            "manifest_receipt_id": receipt_id,
            "transaction_id": result.transaction_id,
            "manifest_hash": result.manifest.manifest_hash,
            "receipt_chain_head": result.replay.receipt_chain_head,
            "canonical_runtime_identity": result.replay.canonical_runtime_identity,
            "registered_at": _now(),
            "result": result_body,
            "locator_grants_authority": False,
        }
        record = ManifestReceiptRecord(**body, record_hash=canonical_sha256(body))
        self._records[receipt_id] = record
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(record.model_dump_json() + "\n")
        return record

    def resolve(self, manifest_receipt_id: str) -> ManifestReceiptRecord:
        record = self._records.get(manifest_receipt_id.strip().upper())
        if record is None:
            raise KeyError("manifest_receipt_id_not_found")
        return record

    def evidence_package(self, manifest_receipt_id: str) -> dict[str, Any]:
        record = self.resolve(manifest_receipt_id)
        result = record.result
        return {
            "manifest_receipt_id": record.manifest_receipt_id,
            "transaction_id": record.transaction_id,
            "manifest": result["manifest"],
            "receipts": result["receipts"],
            "execution_observation": result["execution_observation"],
            "replay_descriptor": result["replay"],
            "chain_verified": result["chain_verified"],
            "receipt_chain_head": record.receipt_chain_head,
            "canonical_runtime_identity": record.canonical_runtime_identity,
            "locator_grants_authority": False,
        }

    def reconstruct(self, manifest_receipt_id: str) -> ReconstructionReceipt:
        record = self.resolve(manifest_receipt_id)
        result = record.result
        receipts = list(result.get("receipts") or [])
        persisted = [
            {
                "sequence": item.get("sequence"),
                "stage": item.get("stage"),
                "state": item.get("state"),
                "processor": item.get("processor"),
                "receipt_hash": item.get("receipt_hash"),
                "evidence_class": "NATIVELY_PERSISTED",
            }
            for item in receipts
        ]
        summary = {
            "manifest_hash": record.manifest_hash,
            "receipt_chain_head": record.receipt_chain_head,
            "states": [item.get("state") for item in receipts],
            "reconstructed_from_retained_record": True,
            "reconstruction_grants_authority": False,
        }
        body = {
            "artifact_type": "stegcore.manifest_reconstruction_receipt",
            "schema_version": "1.0",
            "original_manifest_receipt_id": record.manifest_receipt_id,
            "reconstructed_at": _now(),
            "transaction_id": record.transaction_id,
            "chain_verified": bool(result.get("chain_verified")),
            "persisted_evidence": persisted,
            "reconstructed_summary": summary,
            "consequence_reexecuted": False,
        }
        return ReconstructionReceipt(**body, receipt_hash=canonical_sha256(body))

    def replay(
        self,
        manifest_receipt_id: str,
        replay_handler: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    ) -> ReplayReceipt:
        record = self.resolve(manifest_receipt_id)
        original = record.result
        original_hash_before = canonical_sha256(original)
        replayed = dict(replay_handler(self.evidence_package(manifest_receipt_id)))
        if bool(replayed.get("consequence_executed")):
            raise ValueError("replay_handler_must_not_reexecute_consequence")
        if canonical_sha256(record.result) != original_hash_before:
            raise RuntimeError("original_manifest_record_mutated_during_replay")
        original_observation = original.get("execution_observation") or {}
        evaluation = original_observation.get("evaluation") or {}
        original_disposition = str(evaluation.get("disposition") or "")
        replay_disposition = str(replayed.get("governance_state") or replayed.get("disposition") or "")
        replay_manifest_hash = str(replayed.get("manifest_hash") or record.manifest_hash)
        replay_input_hash = str(replayed.get("input_hash") or original["manifest"].get("input_hash"))
        body = {
            "artifact_type": "stegcore.manifest_replay_receipt",
            "schema_version": "1.0",
            "original_manifest_receipt_id": record.manifest_receipt_id,
            "replayed_at": _now(),
            "original_transaction_id": record.transaction_id,
            "original_manifest_hash": record.manifest_hash,
            "original_receipt_chain_head": record.receipt_chain_head,
            "original_disposition": original_disposition,
            "replay_disposition": replay_disposition,
            "input_identity_match": replay_input_hash == original["manifest"].get("input_hash"),
            "manifest_identity_match": replay_manifest_hash == record.manifest_hash,
            "deterministic_disposition_match": replay_disposition == original_disposition,
            "consequence_reexecuted": False,
            "replay_result": replayed,
        }
        return ReplayReceipt(**body, receipt_hash=canonical_sha256(body))
