#!/usr/bin/env python3
"""Write durable, idempotent evidence for a successful StegCore validation run.

The evidence changes only when the validated StegCore contract commit, canonical
Governance commit, or downstream dispatch changes. It does not grant production,
release, cross-repository mutation, or Continuity authority.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


HASH_CONVENTION = {
    "algorithm": "SHA-256",
    "excluded_field": "evidence_hash",
    "serialization": {
        "encoding": "UTF-8",
        "format": "JSON",
        "separators": [",", ":"],
        "sort_keys": True,
    },
}


def canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(payload.encode("utf-8")).hexdigest()


def load_object(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def load_existing(path: pathlib.Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return load_object(path)
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--dispatch", type=pathlib.Path, required=True)
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

    dispatch = load_object(args.dispatch)
    if dispatch.get("artifact_type") != "stegcore.downstream_verification_dispatch":
        raise SystemExit("downstream dispatch artifact_type is invalid")
    destinations = dispatch.get("destinations")
    if not isinstance(destinations, list) or not destinations:
        raise SystemExit("downstream dispatch must contain destinations")

    dispatch_hash = canonical_hash(dispatch)
    existing = load_existing(args.output)
    if (
        existing
        and existing.get("status") == "pass"
        and existing.get("stegcore_commit") == args.stegcore_commit
        and existing.get("governance_commit") == args.governance_commit
        and existing.get("downstream_dispatch_hash") == dispatch_hash
        and existing.get("record_type") == "runtime_validation_evidence"
        and existing.get("hash_convention", {}).get("excluded_field") == "evidence_hash"
    ):
        print("Passing evidence already matches contract commits and downstream dispatch.")
        return 0

    downstream_verification = []
    for item in destinations:
        if not isinstance(item, dict):
            raise SystemExit("downstream dispatch destinations must be objects")
        downstream_verification.append(
            {
                "repository": item.get("repository"),
                "issue_number": item.get("issue_number"),
                "issue_url": item.get("issue_url"),
                "handoff": item.get("handoff"),
                "required": item.get("required") is True,
                "state": item.get("state"),
                "scope": item.get("scope"),
            }
        )

    evidence: dict[str, Any] = {
        "artifact_type": "stegcore.runtime_validation_evidence",
        "record_type": "runtime_validation_evidence",
        "source_repository": "StegVerse-Labs/StegCore",
        "destination_repository": "StegVerse-Labs/StegCore",
        "hash_convention": HASH_CONVENTION,
        "schema_version": "1.1",
        "status": "pass",
        "release_state": "validated_not_released",
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
            "release_authority_claimed": False,
            "cross_repository_mutation_authority_claimed": False,
        },
        "downstream_dispatch_path": str(args.dispatch),
        "downstream_dispatch_hash": dispatch_hash,
        "downstream_verification": downstream_verification,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }
    evidence["evidence_hash"] = canonical_hash(evidence)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote passing runtime validation evidence to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
