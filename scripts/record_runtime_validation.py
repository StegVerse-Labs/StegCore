#!/usr/bin/env python3
"""Write durable, idempotent evidence for a successful StegCore validation run.

The evidence changes only when the validated StegCore contract commit or canonical
Governance commit changes. It does not grant production authority and does not mint
Continuity receipts.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


def canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(payload.encode("utf-8")).hexdigest()


def load_existing(path: pathlib.Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--stegcore-commit", required=True)
    parser.add_argument("--governance-commit", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--event", required=True)
    parser.add_argument("--issue", default="22")
    args = parser.parse_args()

    existing = load_existing(args.output)
    if (
        existing
        and existing.get("status") == "pass"
        and existing.get("stegcore_commit") == args.stegcore_commit
        and existing.get("governance_commit") == args.governance_commit
    ):
        print("Passing evidence already matches the validated contract commits; no update required.")
        return 0

    evidence: dict[str, Any] = {
        "artifact_type": "stegcore.runtime_validation_evidence",
        "schema_version": "1.0",
        "status": "pass",
        "repository": args.repository,
        "stegcore_commit": args.stegcore_commit,
        "governance_repository": "StegVerse-Labs/Governance",
        "governance_commit": args.governance_commit,
        "workflow": args.workflow,
        "run_id": str(args.run_id),
        "run_attempt": str(args.run_attempt),
        "event": args.event,
        "ref": args.ref,
        "issue": int(args.issue),
        "checks": {
            "continuity_admissibility_mapping": "pass",
            "stegcore_pytest_suite": "pass",
            "canonical_governance_fixture_contract": "pass",
            "positive_control": "ALLOW",
            "replay_mutation": "FAIL-CLOSED",
            "continuity_receipt_minted": False,
        },
        "authority_boundary": {
            "production_authority_claimed": False,
            "continuity_authority_claimed": False,
            "receipt_minting_authority_claimed": False,
        },
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }
    evidence["evidence_hash"] = canonical_hash(evidence)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote passing runtime validation evidence to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
