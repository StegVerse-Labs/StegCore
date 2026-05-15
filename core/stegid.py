"""
StegVerse StegID v1.0
Identity, role, authority, key, subject, and provenance records.
Binds every action to an identity with explicit scope.
"""

import json
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Literal

SCHEMA_VERSION = "stegverse_stegid.v1"

RoleType    = Literal["user", "agent/personal", "agent/stegclaw", "agent/system", "service", "repo", "org"]
ScopeType   = Literal[
    "ALLOW_OBSERVE", "ALLOW_QUEUE", "ALLOW_ROUTE", "ALLOW_INSTALL",
    "ALLOW_CONFIRM", "ALLOW_PROMOTE", "ALLOW_RELEASE_PAYLOAD",
    "ALLOW_QUARANTINE", "ALLOW_REPAIR_CANDIDATE",
    "ALLOW_VAULT_READ", "ALLOW_VAULT_WRITE", "ALLOW_CONSENT_GRANT",
    "ALLOW_TRIAD_GATE", "ALLOW_FINCO_TRANSITION",
]


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class StegIDRegistry:
    """
    Append-only identity registry.
    Every identity record is hash-linked.
    Revocation creates a new record — original is preserved.
    """

    def __init__(self, registry_path: str = "./stegid_registry.jsonl"):
        self.path = Path(registry_path)
        self.receipts_path = self.path.parent / "stegid_receipts.jsonl"

    def _append(self, record: dict):
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def _append_receipt(self, receipt: dict):
        with open(self.receipts_path, "a") as f:
            f.write(json.dumps(receipt) + "\n")

    def _load_all(self) -> list:
        if not self.path.exists():
            return []
        records = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def _make_receipt(self, decision: str, reason: str, subject_id: str, actor: str) -> dict:
        return {
            "schema": "stegverse_stegid_receipt.v1",
            "generated_at": now_iso(),
            "engine": "stegid",
            "input_ref": subject_id,
            "actor_or_source": actor,
            "decision": decision,
            "reason": reason,
            "hashes": {"subject_hash": sha256(subject_id)},
            "unknowns": [],
            "next_route": "ingestion",
        }

    # ── Register ────────────────────────────────────────────────────────────

    def register(
        self,
        display_name: str,
        role: RoleType,
        allowed_scopes: list,
        actor: str,
        key_ref: Optional[str] = None,
        parent_subject_id: Optional[str] = None,
        metadata: dict = None,
    ) -> dict:
        """Register a new identity. Returns subject_id."""
        subject_id = f"steg:{role}:{uuid.uuid4().hex[:12]}"
        record = {
            "schema": SCHEMA_VERSION,
            "subject_id": subject_id,
            "display_name": display_name,
            "role": role,
            "allowed_scopes": allowed_scopes,
            "key_ref": key_ref,
            "parent_subject_id": parent_subject_id,
            "metadata": metadata or {},
            "status": "active",
            "created_at": now_iso(),
            "actor": actor,
        }
        record["record_hash"] = sha256(json.dumps(record, sort_keys=True))
        self._append(record)

        receipt = self._make_receipt("ALLOW", f"Identity '{display_name}' registered as {role}.", subject_id, actor)
        self._append_receipt(receipt)
        return {"subject_id": subject_id, "record": record, "receipt": receipt}

    # ── Lookup ──────────────────────────────────────────────────────────────

    def lookup(self, subject_id: str) -> Optional[dict]:
        """Return the most recent active record for a subject_id."""
        records = self._load_all()
        matches = [r for r in records if r.get("subject_id") == subject_id]
        if not matches:
            return None
        # Return last (most recent) non-revoked
        active = [r for r in matches if r.get("status") == "active"]
        return active[-1] if active else None

    # ── Authorize ───────────────────────────────────────────────────────────

    def authorize(self, subject_id: str, required_scope: str, actor: str = "system") -> dict:
        """
        Check whether subject_id has the required scope.
        Returns ALLOW or FAIL_CLOSED with receipt.
        """
        identity = self.lookup(subject_id)

        if not identity:
            receipt = self._make_receipt(
                "FAIL_CLOSED",
                f"Subject '{subject_id}' not found in registry.",
                subject_id, actor
            )
            self._append_receipt(receipt)
            return {"decision": "FAIL_CLOSED", "receipt": receipt}

        if identity.get("status") != "active":
            receipt = self._make_receipt(
                "FAIL_CLOSED",
                f"Subject '{subject_id}' is {identity.get('status')}, not active.",
                subject_id, actor
            )
            self._append_receipt(receipt)
            return {"decision": "FAIL_CLOSED", "receipt": receipt}

        if required_scope not in identity.get("allowed_scopes", []):
            receipt = self._make_receipt(
                "FAIL_CLOSED",
                f"Subject '{subject_id}' lacks scope '{required_scope}'.",
                subject_id, actor
            )
            self._append_receipt(receipt)
            return {"decision": "FAIL_CLOSED", "receipt": receipt}

        receipt = self._make_receipt(
            "ALLOW",
            f"Subject '{subject_id}' authorized for '{required_scope}'.",
            subject_id, actor
        )
        self._append_receipt(receipt)
        return {"decision": "ALLOW", "identity": identity, "receipt": receipt}

    # ── Revoke ──────────────────────────────────────────────────────────────

    def revoke(self, subject_id: str, reason: str, actor: str) -> dict:
        """Revoke an identity. Creates revocation record; never deletes original."""
        identity = self.lookup(subject_id)
        if not identity:
            return {"decision": "FAIL_CLOSED", "reason": "Subject not found."}

        revocation = dict(identity)
        revocation["status"] = "revoked"
        revocation["revoked_at"] = now_iso()
        revocation["revocation_reason"] = reason
        revocation["revoked_by"] = actor
        revocation["record_hash"] = sha256(json.dumps(revocation, sort_keys=True))
        self._append(revocation)

        receipt = self._make_receipt(
            "ALLOW", f"Identity '{subject_id}' revoked: {reason}.", subject_id, actor
        )
        self._append_receipt(receipt)
        return {"subject_id": subject_id, "status": "revoked", "receipt": receipt}

    # ── Delegate ────────────────────────────────────────────────────────────

    def delegate(
        self,
        parent_subject_id: str,
        delegated_name: str,
        delegated_role: RoleType,
        delegated_scopes: list,
        actor: str,
    ) -> dict:
        """
        Create a delegated identity. Delegated scopes must be subset of parent's scopes.
        """
        parent = self.lookup(parent_subject_id)
        if not parent:
            return {"decision": "FAIL_CLOSED", "reason": "Parent subject not found."}

        parent_scopes = set(parent.get("allowed_scopes", []))
        requested = set(delegated_scopes)
        if not requested.issubset(parent_scopes):
            excess = requested - parent_scopes
            return {
                "decision": "FAIL_CLOSED",
                "reason": f"Delegation exceeds parent authority. Excess scopes: {excess}",
            }

        return self.register(
            display_name=delegated_name,
            role=delegated_role,
            allowed_scopes=delegated_scopes,
            actor=actor,
            parent_subject_id=parent_subject_id,
        )


# ── Predefined entity records ───────────────────────────────────────────────

def provision_ecosystem_identities(registry_path: str = "./stegid_registry.jsonl"):
    """
    Create the canonical StegVerse ecosystem identity records.
    Idempotent — checks before creating.
    """
    reg = StegIDRegistry(registry_path)

    # System identity
    sys_result = reg.register(
        display_name="StegVerse System",
        role="agent/system",
        allowed_scopes=[
            "ALLOW_OBSERVE", "ALLOW_QUEUE", "ALLOW_ROUTE", "ALLOW_INSTALL",
            "ALLOW_CONFIRM", "ALLOW_PROMOTE", "ALLOW_QUARANTINE",
            "ALLOW_VAULT_READ", "ALLOW_VAULT_WRITE", "ALLOW_TRIAD_GATE",
        ],
        actor="genesis",
        metadata={"description": "Core system actor for StegVerse ecosystem."}
    )

    # Personal AI entity (base — per-user instances are delegated from this)
    entity_result = reg.register(
        display_name="StegVerse Personal AI Entity (Base)",
        role="agent/personal",
        allowed_scopes=[
            "ALLOW_OBSERVE", "ALLOW_QUEUE", "ALLOW_ROUTE",
            "ALLOW_VAULT_READ", "ALLOW_VAULT_WRITE", "ALLOW_TRIAD_GATE",
        ],
        actor="genesis",
        metadata={
            "description": "Base identity for personal AI assistant entities.",
            "activation_tier": "assist",
            "stegclaw_enabled": False,
        }
    )

    # StegClaw entity (base — for users who enable StegClaw tier)
    claw_result = reg.register(
        display_name="StegClaw Entity (Base)",
        role="agent/stegclaw",
        allowed_scopes=[
            "ALLOW_OBSERVE", "ALLOW_QUEUE", "ALLOW_ROUTE",
            "ALLOW_VAULT_READ", "ALLOW_VAULT_WRITE", "ALLOW_TRIAD_GATE",
            "ALLOW_CONSENT_GRANT", "ALLOW_FINCO_TRANSITION",
            "ALLOW_CONFIRM", "ALLOW_REPAIR_CANDIDATE",
        ],
        actor="genesis",
        metadata={
            "description": "Full autonomous entity tier. Requires Triad gate on every transition.",
            "activation_tier": "stegclaw",
            "stegclaw_enabled": True,
        }
    )

    print(json.dumps({
        "system": sys_result["subject_id"],
        "personal_entity_base": entity_result["subject_id"],
        "stegclaw_base": claw_result["subject_id"],
    }, indent=2))
    return reg


if __name__ == "__main__":
    import sys
    reg_path = sys.argv[1] if len(sys.argv) > 1 else "./stegid_registry.jsonl"

    cmd = sys.argv[2] if len(sys.argv) > 2 else "provision"

    if cmd == "provision":
        provision_ecosystem_identities(reg_path)

    elif cmd == "authorize":
        reg = StegIDRegistry(reg_path)
        subject_id, scope = sys.argv[3], sys.argv[4]
        result = reg.authorize(subject_id, scope)
        print(json.dumps(result, indent=2))

    elif cmd == "lookup":
        reg = StegIDRegistry(reg_path)
        result = reg.lookup(sys.argv[3])
        print(json.dumps(result, indent=2))

    elif cmd == "revoke":
        reg = StegIDRegistry(reg_path)
        result = reg.revoke(sys.argv[3], reason=sys.argv[4], actor="cli")
        print(json.dumps(result, indent=2))
