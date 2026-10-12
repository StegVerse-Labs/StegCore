from __future__ import annotations

"""Provider-neutral durable discovery index for manifested transactions.

The index stores continuity metadata only. Registration and discovery never grant
policy, execution, or payload-disclosure authority. Payloads remain outside this
surface; consumers receive hashes, route/state summaries, and evidence pointers.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Iterable, Optional

from pydantic import BaseModel, Field

from .transaction_lifecycle import ManifestedTransactionResult, canonical_sha256


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DiscoveryRecord(BaseModel):
    artifact_type: str = "stegcore.transaction_discovery_record"
    schema_version: str = "1.0"
    transaction_id: str
    registered_at: str
    manifest_hash: str
    input_hash: str
    candidate_hash: str
    request_hash: str
    canonical_runtime_identity: str
    canonical_evaluator: str
    source: str
    subject: str
    stages: list[str]
    states: list[str]
    receipt_hashes: list[str]
    receipt_chain_head: str
    decision_refs: list[str] = Field(default_factory=list)
    finding_refs: list[str] = Field(default_factory=list)
    remediation_refs: list[str] = Field(default_factory=list)
    verification_refs: list[str] = Field(default_factory=list)
    payload_disclosed: bool = False
    discovery_grants_authority: bool = False
    record_hash: str


class DiscoveryQuery(BaseModel):
    transaction_id: Optional[str] = None
    manifest_hash: Optional[str] = None
    candidate_hash: Optional[str] = None
    request_hash: Optional[str] = None
    runtime_identity: Optional[str] = None
    source: Optional[str] = None
    subject: Optional[str] = None
    stage: Optional[str] = None
    state: Optional[str] = None
    finding_ref: Optional[str] = None
    remediation_ref: Optional[str] = None
    verification_ref: Optional[str] = None


class TransactionDiscoveryIndex:
    """Append-only discovery index with JSONL persistence and reload support."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._records: list[DiscoveryRecord] = []
        self._by_transaction: dict[str, DiscoveryRecord] = {}
        if self.path is not None and self.path.exists():
            self._load()

    def _load(self) -> None:
        assert self.path is not None
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            record = DiscoveryRecord.model_validate_json(raw)
            self._validate_record(record)
            if record.transaction_id in self._by_transaction:
                raise ValueError(f"duplicate transaction discovery record: {record.transaction_id}")
            self._records.append(record)
            self._by_transaction[record.transaction_id] = record

    @staticmethod
    def _validate_record(record: DiscoveryRecord) -> None:
        body = record.model_dump(mode="json", exclude={"record_hash"})
        if canonical_sha256(body) != record.record_hash:
            raise ValueError("transaction discovery record hash mismatch")
        if record.payload_disclosed:
            raise ValueError("discovery index must not persist payload disclosure")
        if record.discovery_grants_authority:
            raise ValueError("discovery index cannot grant authority")

    def register(
        self,
        result: ManifestedTransactionResult,
        *,
        finding_refs: Iterable[str] = (),
        remediation_refs: Iterable[str] = (),
        verification_refs: Iterable[str] = (),
    ) -> DiscoveryRecord:
        if not result.chain_verified:
            raise ValueError("cannot register an unverified transaction receipt chain")
        if result.transaction_id in self._by_transaction:
            existing = self._by_transaction[result.transaction_id]
            if existing.receipt_chain_head == result.replay.receipt_chain_head:
                return existing
            raise ValueError("transaction identity already registered with a different chain head")

        decision_refs = [
            receipt.decision_ref
            for receipt in result.receipts
            if receipt.decision_ref is not None
        ]
        body = {
            "artifact_type": "stegcore.transaction_discovery_record",
            "schema_version": "1.0",
            "transaction_id": result.transaction_id,
            "registered_at": _now(),
            "manifest_hash": result.manifest.manifest_hash,
            "input_hash": result.manifest.input_hash,
            "candidate_hash": result.manifest.candidate_hash,
            "request_hash": result.manifest.request_hash,
            # The manifest no longer declares runtime semantics (SDK-MANIFEST-STEGCORE-ENTRY-
            # CONFORMANCE-001); the replay descriptor and the StegGate-stage receipt record them.
            "canonical_runtime_identity": result.replay.canonical_runtime_identity,
            "canonical_evaluator": next(
                (receipt.processor for receipt in result.receipts if receipt.stage == "steggate"), ""),
            "source": result.manifest.source,
            "subject": result.manifest.subject,
            "stages": [receipt.stage for receipt in result.receipts],
            "states": [receipt.state for receipt in result.receipts],
            "receipt_hashes": [receipt.receipt_hash for receipt in result.receipts],
            "receipt_chain_head": result.replay.receipt_chain_head,
            "decision_refs": decision_refs,
            "finding_refs": list(dict.fromkeys(finding_refs)),
            "remediation_refs": list(dict.fromkeys(remediation_refs)),
            "verification_refs": list(dict.fromkeys(verification_refs)),
            "payload_disclosed": False,
            "discovery_grants_authority": False,
        }
        record = DiscoveryRecord(**body, record_hash=canonical_sha256(body))
        self._records.append(record)
        self._by_transaction[record.transaction_id] = record
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(record.model_dump_json() + "\n")
        return record

    def get(self, transaction_id: str) -> DiscoveryRecord | None:
        return self._by_transaction.get(transaction_id)

    def query(self, query: DiscoveryQuery | None = None, **criteria: str) -> list[DiscoveryRecord]:
        q = query or DiscoveryQuery(**criteria)
        records = list(self._records)

        def matches(record: DiscoveryRecord) -> bool:
            if q.transaction_id and record.transaction_id != q.transaction_id:
                return False
            if q.manifest_hash and record.manifest_hash != q.manifest_hash:
                return False
            if q.candidate_hash and record.candidate_hash != q.candidate_hash:
                return False
            if q.request_hash and record.request_hash != q.request_hash:
                return False
            if q.runtime_identity and record.canonical_runtime_identity != q.runtime_identity:
                return False
            if q.source and record.source != q.source:
                return False
            if q.subject and record.subject != q.subject:
                return False
            if q.stage and q.stage not in record.stages:
                return False
            if q.state and q.state not in record.states:
                return False
            if q.finding_ref and q.finding_ref not in record.finding_refs:
                return False
            if q.remediation_ref and q.remediation_ref not in record.remediation_refs:
                return False
            if q.verification_ref and q.verification_ref not in record.verification_refs:
                return False
            return True

        return [record for record in records if matches(record)]

    def safe_summary(self, transaction_id: str) -> dict[str, object] | None:
        record = self.get(transaction_id)
        if record is None:
            return None
        return {
            "transaction_id": record.transaction_id,
            "manifest_hash": record.manifest_hash,
            "candidate_hash": record.candidate_hash,
            "request_hash": record.request_hash,
            "canonical_runtime_identity": record.canonical_runtime_identity,
            "source": record.source,
            "subject": record.subject,
            "stages": list(record.stages),
            "states": list(record.states),
            "receipt_chain_head": record.receipt_chain_head,
            "finding_refs": list(record.finding_refs),
            "remediation_refs": list(record.remediation_refs),
            "verification_refs": list(record.verification_refs),
            "payload_disclosed": False,
            "discovery_grants_authority": False,
        }

    def records(self) -> list[DiscoveryRecord]:
        return list(self._records)
