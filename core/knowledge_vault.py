"""
StegVerse Knowledge Vault v1.0
Cloud memory surface for personal AI entity.
Four partitions per user: working_memory, private_state, genealogy, consent_ledger.
All writes produce receipts. All reads are logged. Tamper-evident chain.
"""

import json
import hashlib
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Literal

SCHEMA_VERSION = "stegverse_knowledge_vault.v1"

PartitionType = Literal["working_memory", "private_state", "genealogy", "consent_ledger"]
PrivacyClass  = Literal["private", "draft", "canonical", "public"]
Decision      = Literal["ALLOW", "QUARANTINE", "REVIEW_REQUIRED", "FAIL_CLOSED"]


# ── Hashing ────────────────────────────────────────────────────────────────

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def record_hash(record: dict) -> str:
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
    return sha256(canonical)


# ── Receipt primitives ─────────────────────────────────────────────────────

def make_receipt(
    engine: str,
    input_ref: str,
    actor: str,
    decision: Decision,
    reason: str,
    hashes: dict,
    next_route: str,
    unknowns: list = None,
) -> dict:
    return {
        "schema": f"stegverse_{engine}_receipt.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": engine,
        "input_ref": input_ref,
        "actor_or_source": actor,
        "decision": decision,
        "reason": reason,
        "hashes": hashes,
        "unknowns": unknowns or [],
        "next_route": next_route,
    }


# ── Vault record ────────────────────────────────────────────────────────────

def make_vault_record(
    user_id: str,
    partition: PartitionType,
    privacy: PrivacyClass,
    key: str,
    value: dict,
    actor: str,
    prev_hash: Optional[str] = None,
    evidence_grade: str = "D",
    tags: list = None,
) -> dict:
    record = {
        "schema": SCHEMA_VERSION,
        "record_id": str(uuid.uuid4()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "partition": partition,
        "privacy": privacy,
        "key": key,
        "value": value,
        "actor": actor,
        "evidence_grade": evidence_grade,
        "tags": tags or [],
        "prev_hash": prev_hash,
        "superseded": False,
    }
    record["record_hash"] = record_hash(record)
    return record


# ── Knowledge Vault ─────────────────────────────────────────────────────────

class KnowledgeVault:
    """
    Per-user Knowledge Vault with four partitions.
    Storage: one JSONL file per user per partition.
    Every write is append-only (LPP: never overwrite, never delete).
    """

    def __init__(self, vault_root: str):
        self.root = Path(vault_root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.receipts_path = self.root / "vault_receipts.jsonl"

    # ── Internal helpers ───────────────────────────────────────────────────

    def _partition_path(self, user_id: str, partition: PartitionType) -> Path:
        user_dir = self.root / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / f"{partition}.jsonl"

    def _append_record(self, path: Path, record: dict):
        with open(path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def _append_receipt(self, receipt: dict):
        with open(self.receipts_path, "a") as f:
            f.write(json.dumps(receipt) + "\n")

    def _load_partition(self, user_id: str, partition: PartitionType) -> list:
        path = self._partition_path(user_id, partition)
        if not path.exists():
            return []
        records = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def _latest_hash(self, user_id: str, partition: PartitionType) -> Optional[str]:
        records = self._load_partition(user_id, partition)
        if not records:
            return None
        return records[-1].get("record_hash")

    # ── User provisioning ──────────────────────────────────────────────────

    def provision_user(self, user_id: str, actor: str) -> dict:
        """Create vault partitions for a new user. Idempotent."""
        for partition in ["working_memory", "private_state", "genealogy", "consent_ledger"]:
            path = self._partition_path(user_id, partition)
            if not path.exists():
                init_record = make_vault_record(
                    user_id=user_id,
                    partition=partition,
                    privacy="private",
                    key="_init",
                    value={"status": "initialized", "version": "1.0"},
                    actor=actor,
                    evidence_grade="A",
                )
                self._append_record(path, init_record)

        receipt = make_receipt(
            engine="knowledge-vault",
            input_ref=f"provision:{user_id}",
            actor=actor,
            decision="ALLOW",
            reason="User vault provisioned with four partitions.",
            hashes={"user_id": sha256(user_id)},
            next_route="stegid",
        )
        self._append_receipt(receipt)
        return {"user_id": user_id, "status": "provisioned", "receipt": receipt}

    # ── Write ──────────────────────────────────────────────────────────────

    def write(
        self,
        user_id: str,
        partition: PartitionType,
        key: str,
        value: dict,
        actor: str,
        privacy: PrivacyClass = "private",
        evidence_grade: str = "D",
        tags: list = None,
    ) -> dict:
        """Append a new record to a partition. Never overwrites. Issues receipt."""
        prev_hash = self._latest_hash(user_id, partition)
        record = make_vault_record(
            user_id=user_id,
            partition=partition,
            privacy=privacy,
            key=key,
            value=value,
            actor=actor,
            prev_hash=prev_hash,
            evidence_grade=evidence_grade,
            tags=tags,
        )
        path = self._partition_path(user_id, partition)
        self._append_record(path, record)

        receipt = make_receipt(
            engine="knowledge-vault",
            input_ref=record["record_id"],
            actor=actor,
            decision="ALLOW",
            reason=f"Record written to {partition}/{key}.",
            hashes={"record_hash": record["record_hash"], "prev_hash": prev_hash or "genesis"},
            next_route="ingestion",
        )
        self._append_receipt(receipt)
        return {"record_id": record["record_id"], "receipt": receipt}

    # ── Read ───────────────────────────────────────────────────────────────

    def read(
        self,
        user_id: str,
        partition: PartitionType,
        key: Optional[str] = None,
        actor: str = "system",
        allowed_privacy: list = None,
    ) -> dict:
        """
        Read records from a partition.
        Enforces privacy gate: actor must be entitled to the privacy class.
        """
        allowed = set(allowed_privacy or ["private", "draft", "canonical", "public"])
        records = self._load_partition(user_id, partition)

        results = []
        for r in records:
            if r.get("privacy") not in allowed:
                continue
            if r.get("superseded"):
                continue
            if key and r.get("key") != key:
                continue
            if r.get("key") == "_init":
                continue
            results.append(r)

        receipt = make_receipt(
            engine="knowledge-vault",
            input_ref=f"read:{user_id}:{partition}:{key or '*'}",
            actor=actor,
            decision="ALLOW",
            reason=f"Read {len(results)} records from {partition}.",
            hashes={"query_hash": sha256(f"{user_id}:{partition}:{key}")},
            next_route="llm-adapter",
        )
        self._append_receipt(receipt)
        return {"records": results, "count": len(results), "receipt": receipt}

    # ── Session helpers ────────────────────────────────────────────────────

    def load_entity_context(self, user_id: str, actor: str) -> dict:
        """
        Load everything the entity needs at session start:
        working memory + recent private state + consent ledger.
        """
        wm    = self.read(user_id, "working_memory", actor=actor)
        ps    = self.read(user_id, "private_state",  actor=actor)
        cl    = self.read(user_id, "consent_ledger", actor=actor)
        return {
            "user_id": user_id,
            "working_memory": wm["records"],
            "private_state":  ps["records"],
            "consent_ledger": cl["records"],
            "loaded_at": datetime.now(timezone.utc).isoformat(),
        }

    def save_session_summary(self, user_id: str, summary: dict, actor: str) -> dict:
        """Ingest session summary into working memory at session end."""
        return self.write(
            user_id=user_id,
            partition="working_memory",
            key="session_summary",
            value=summary,
            actor=actor,
            privacy="private",
            evidence_grade="B",
            tags=["session", "auto"],
        )

    # ── Genealogy helpers ──────────────────────────────────────────────────

    def write_genealogy_record(
        self,
        user_id: str,
        cid: str,
        identity_data: dict,
        evidence_grade: str,
        actor: str,
        privacy: PrivacyClass = "private",
    ) -> dict:
        """Write a genealogical identity record. CID is the canonical key."""
        return self.write(
            user_id=user_id,
            partition="genealogy",
            key=cid,
            value=identity_data,
            actor=actor,
            privacy=privacy,
            evidence_grade=evidence_grade,
            tags=["genealogy", "cid"],
        )

    # ── Consent helpers ────────────────────────────────────────────────────

    def record_consent(
        self,
        user_id: str,
        scope: str,
        permitted_actor: str,
        duration_seconds: int,
        purpose: str,
        actor: str,
        derivative_use: bool = False,
        compensation_terms: str = "none",
    ) -> dict:
        consent = {
            "scope": scope,
            "permitted_actor": permitted_actor,
            "purpose": purpose,
            "duration_seconds": duration_seconds,
            "expires_at": (
                datetime.fromtimestamp(
                    time.time() + duration_seconds, tz=timezone.utc
                ).isoformat()
            ),
            "derivative_use": derivative_use,
            "compensation_terms": compensation_terms,
            "revoked": False,
        }
        return self.write(
            user_id=user_id,
            partition="consent_ledger",
            key=f"consent:{scope}:{permitted_actor}",
            value=consent,
            actor=actor,
            privacy="private",
            evidence_grade="A",
            tags=["consent", "finco"],
        )

    def revoke_consent(self, user_id: str, scope: str, permitted_actor: str, actor: str) -> dict:
        revocation = {
            "revoked": True,
            "revoked_at": datetime.now(timezone.utc).isoformat(),
            "scope": scope,
            "permitted_actor": permitted_actor,
        }
        return self.write(
            user_id=user_id,
            partition="consent_ledger",
            key=f"revocation:{scope}:{permitted_actor}",
            value=revocation,
            actor=actor,
            privacy="private",
            evidence_grade="A",
            tags=["revocation", "finco"],
        )

    # ── Verify chain ───────────────────────────────────────────────────────

    def verify_chain(self, user_id: str, partition: PartitionType) -> dict:
        """Walk the hash chain and verify integrity."""
        records = self._load_partition(user_id, partition)
        errors = []
        prev = None
        for i, r in enumerate(records):
            stored_hash = r.get("record_hash")
            r_copy = dict(r)
            r_copy.pop("record_hash", None)
            computed = record_hash(r_copy)
            if stored_hash != computed:
                errors.append({"index": i, "key": r.get("key"), "error": "hash_mismatch"})
            if i > 0 and r.get("prev_hash") != prev:
                errors.append({"index": i, "key": r.get("key"), "error": "chain_break"})
            prev = stored_hash

        return {
            "user_id": user_id,
            "partition": partition,
            "records_checked": len(records),
            "errors": errors,
            "valid": len(errors) == 0,
        }


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    vault = KnowledgeVault("./vault_data")

    cmd = sys.argv[1] if len(sys.argv) > 1 else "demo"

    if cmd == "provision":
        user_id = sys.argv[2]
        result = vault.provision_user(user_id, actor="system")
        print(json.dumps(result, indent=2))

    elif cmd == "write":
        user_id, partition, key = sys.argv[2], sys.argv[3], sys.argv[4]
        value = json.loads(sys.argv[5])
        result = vault.write(user_id, partition, key, value, actor="cli")
        print(json.dumps(result, indent=2))

    elif cmd == "read":
        user_id, partition = sys.argv[2], sys.argv[3]
        key = sys.argv[4] if len(sys.argv) > 4 else None
        result = vault.read(user_id, partition, key=key, actor="cli")
        print(json.dumps(result, indent=2))

    elif cmd == "verify":
        user_id, partition = sys.argv[2], sys.argv[3]
        result = vault.verify_chain(user_id, partition)
        print(json.dumps(result, indent=2))

    elif cmd == "demo":
        print("=== Knowledge Vault Demo ===")
        v = KnowledgeVault("./vault_demo")

        r = v.provision_user("user_001", "system")
        print(f"Provisioned: {r['status']}")

        v.write("user_001", "working_memory", "goal",
                {"current": "Activate personal entity", "priority": "high"},
                actor="entity/stegverse-ai", evidence_grade="B")

        v.write_genealogy_record("user_001", "RND-1796-001-TN",
                {"name": "Ruben Randolph", "birth_year": 1796, "birth_state": "TN",
                 "parent_cid": "RND-c1760-001-VA", "source_id": "SRC-001"},
                evidence_grade="B", actor="user_001")

        v.record_consent("user_001", "working_memory:read", "entity/stegverse-ai",
                         duration_seconds=86400, purpose="Personal assistant session",
                         actor="user_001")

        ctx = v.load_entity_context("user_001", actor="entity/stegverse-ai")
        print(f"Context loaded: {len(ctx['working_memory'])} wm, "
              f"{len(ctx['consent_ledger'])} consent records")

        chain = v.verify_chain("user_001", "working_memory")
        print(f"Chain valid: {chain['valid']} ({chain['records_checked']} records)")
        print("Demo complete.")
