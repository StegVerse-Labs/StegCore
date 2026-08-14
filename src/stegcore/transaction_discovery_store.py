from __future__ import annotations

"""Durable shared storage providers for transaction discovery metadata.

This module stores only validated ``DiscoveryRecord`` objects. It does not accept
transaction payloads, grant policy/execution authority, or mint receipts. The
SQLite provider uses WAL mode so independent StegVerse processes can share the
same durable discovery database without relying on one process-local JSONL file.
"""

import json
from pathlib import Path
import sqlite3
from typing import Protocol, runtime_checkable

from .transaction_discovery import DiscoveryQuery, DiscoveryRecord
from .transaction_lifecycle import canonical_sha256


@runtime_checkable
class DiscoveryRecordStore(Protocol):
    """Provider-neutral persistence contract for disclosure-safe discovery records."""

    def append(self, record: DiscoveryRecord) -> DiscoveryRecord: ...

    def get(self, transaction_id: str) -> DiscoveryRecord | None: ...

    def query(self, query: DiscoveryQuery | None = None, **criteria: str) -> list[DiscoveryRecord]: ...

    def records(self) -> list[DiscoveryRecord]: ...

    def safe_summary(self, transaction_id: str) -> dict[str, object] | None: ...


def _validate_record(record: DiscoveryRecord) -> None:
    body = record.model_dump(mode="json", exclude={"record_hash"})
    if canonical_sha256(body) != record.record_hash:
        raise ValueError("transaction discovery record hash mismatch")
    if record.payload_disclosed:
        raise ValueError("discovery store must not persist payload disclosure")
    if record.discovery_grants_authority:
        raise ValueError("discovery store cannot grant authority")


def _matches(record: DiscoveryRecord, query: DiscoveryQuery) -> bool:
    if query.transaction_id and record.transaction_id != query.transaction_id:
        return False
    if query.manifest_hash and record.manifest_hash != query.manifest_hash:
        return False
    if query.candidate_hash and record.candidate_hash != query.candidate_hash:
        return False
    if query.request_hash and record.request_hash != query.request_hash:
        return False
    if query.runtime_identity and record.canonical_runtime_identity != query.runtime_identity:
        return False
    if query.source and record.source != query.source:
        return False
    if query.subject and record.subject != query.subject:
        return False
    if query.stage and query.stage not in record.stages:
        return False
    if query.state and query.state not in record.states:
        return False
    if query.finding_ref and query.finding_ref not in record.finding_refs:
        return False
    if query.remediation_ref and query.remediation_ref not in record.remediation_refs:
        return False
    if query.verification_ref and query.verification_ref not in record.verification_refs:
        return False
    return True


def _safe_summary(record: DiscoveryRecord) -> dict[str, object]:
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


class SqliteDiscoveryStore:
    """Append-only SQLite backing suitable for multiple local StegVerse processes."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS discovery_records (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT NOT NULL UNIQUE,
                    record_hash TEXT NOT NULL UNIQUE,
                    receipt_chain_head TEXT NOT NULL,
                    manifest_hash TEXT NOT NULL,
                    candidate_hash TEXT NOT NULL,
                    request_hash TEXT NOT NULL,
                    runtime_identity TEXT NOT NULL,
                    source TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    record_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_discovery_manifest_hash
                    ON discovery_records(manifest_hash);
                CREATE INDEX IF NOT EXISTS idx_discovery_candidate_hash
                    ON discovery_records(candidate_hash);
                CREATE INDEX IF NOT EXISTS idx_discovery_request_hash
                    ON discovery_records(request_hash);
                CREATE INDEX IF NOT EXISTS idx_discovery_runtime_identity
                    ON discovery_records(runtime_identity);
                CREATE INDEX IF NOT EXISTS idx_discovery_source
                    ON discovery_records(source);
                CREATE INDEX IF NOT EXISTS idx_discovery_subject
                    ON discovery_records(subject);
                """
            )

    @staticmethod
    def _decode(raw: str) -> DiscoveryRecord:
        record = DiscoveryRecord.model_validate_json(raw)
        _validate_record(record)
        return record

    def append(self, record: DiscoveryRecord) -> DiscoveryRecord:
        _validate_record(record)
        encoded = record.model_dump_json()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing_row = connection.execute(
                "SELECT record_json FROM discovery_records WHERE transaction_id = ?",
                (record.transaction_id,),
            ).fetchone()
            if existing_row is not None:
                existing = self._decode(str(existing_row["record_json"]))
                if (
                    existing.record_hash == record.record_hash
                    and existing.receipt_chain_head == record.receipt_chain_head
                ):
                    connection.commit()
                    return existing
                raise ValueError(
                    "transaction identity already registered with a different discovery record"
                )
            connection.execute(
                """
                INSERT INTO discovery_records (
                    transaction_id, record_hash, receipt_chain_head, manifest_hash,
                    candidate_hash, request_hash, runtime_identity, source, subject,
                    record_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.transaction_id,
                    record.record_hash,
                    record.receipt_chain_head,
                    record.manifest_hash,
                    record.candidate_hash,
                    record.request_hash,
                    record.canonical_runtime_identity,
                    record.source,
                    record.subject,
                    encoded,
                ),
            )
            connection.commit()
        return record

    def get(self, transaction_id: str) -> DiscoveryRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT record_json FROM discovery_records WHERE transaction_id = ?",
                (transaction_id,),
            ).fetchone()
        return None if row is None else self._decode(str(row["record_json"]))

    def records(self) -> list[DiscoveryRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record_json FROM discovery_records ORDER BY sequence ASC"
            ).fetchall()
        return [self._decode(str(row["record_json"])) for row in rows]

    def query(self, query: DiscoveryQuery | None = None, **criteria: str) -> list[DiscoveryRecord]:
        q = query or DiscoveryQuery(**criteria)
        clauses: list[str] = []
        values: list[str] = []
        scalar_columns = {
            "transaction_id": "transaction_id",
            "manifest_hash": "manifest_hash",
            "candidate_hash": "candidate_hash",
            "request_hash": "request_hash",
            "runtime_identity": "runtime_identity",
            "source": "source",
            "subject": "subject",
        }
        for field_name, column_name in scalar_columns.items():
            value = getattr(q, field_name)
            if value:
                clauses.append(f"{column_name} = ?")
                values.append(value)
        sql = "SELECT record_json FROM discovery_records"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY sequence ASC"
        with self._connect() as connection:
            rows = connection.execute(sql, values).fetchall()
        candidates = [self._decode(str(row["record_json"])) for row in rows]
        return [record for record in candidates if _matches(record, q)]

    def safe_summary(self, transaction_id: str) -> dict[str, object] | None:
        record = self.get(transaction_id)
        return None if record is None else _safe_summary(record)
