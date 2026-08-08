#!/usr/bin/env python3
"""Reconcile bounded downstream verification receipts into StegCore release readiness.

This script may promote only the downstream-verification gate. It never grants
release, tag, production, deployment, continuity, cross-repository mutation, or
receipt-minting authority. Governance freshness and independent release policy remain
separate fail-closed gates.
"""
from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any


HASH_CONVENTION = {
    "algorithm": "SHA-256",
    "excluded_field": "assessment_hash",
    "serialization": {
        "encoding": "UTF-8",
        "format": "JSON",
        "separators": [",", ":"],
        "sort_keys": True,
    },
}


def canonical_hash(value: dict[str, Any]) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: root must be an object")
    return value


def verify_self_hash(record: dict[str, Any], field: str) -> None:
    body = dict(record)
    declared = body.pop(field, None)
    if not declared or declared != canonical_hash(body):
        raise SystemExit(f"invalid {field}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-evidence", type=Path, required=True)
    parser.add_argument("--dispatch", type=Path, required=True)
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    runtime = load(args.runtime_evidence)
    dispatch = load(args.dispatch)
    receipts = load(args.receipts)

    if runtime.get("artifact_type") != "stegcore.runtime_validation_evidence":
        raise SystemExit("runtime evidence artifact_type mismatch")
    if runtime.get("record_type") != "runtime_validation_evidence":
        raise SystemExit("runtime evidence record_type mismatch")
    if runtime.get("status") != "pass" or runtime.get("release_state") != "validated_not_released":
        raise SystemExit("runtime evidence is not passing validated_not_released evidence")
    verify_self_hash(runtime, "evidence_hash")

    if dispatch.get("artifact_type") != "stegcore.downstream_verification_dispatch":
        raise SystemExit("dispatch artifact_type mismatch")
    destinations = dispatch.get("destinations")
    if not isinstance(destinations, list) or not destinations:
        raise SystemExit("dispatch destinations missing")

    if receipts.get("artifact_type") != "stegcore.downstream_verification_receipts":
        raise SystemExit("receipts artifact_type mismatch")
    if receipts.get("source_stegcore_commit") != runtime.get("stegcore_commit"):
        raise SystemExit("receipts source StegCore commit mismatch")
    if receipts.get("source_runtime_evidence_hash") != runtime.get("evidence_hash"):
        raise SystemExit("receipts source runtime evidence hash mismatch")
    if str(receipts.get("source_runtime_validation_run")) != str(runtime.get("run_id")):
        raise SystemExit("receipts source runtime validation run mismatch")

    authority = receipts.get("authority_boundary")
    if not isinstance(authority, dict) or any(value is not False for value in authority.values()):
        raise SystemExit("receipts authority boundary must remain entirely false")

    verification_rows = receipts.get("verifications")
    if not isinstance(verification_rows, list):
        raise SystemExit("verification rows missing")
    by_repository: dict[str, dict[str, Any]] = {}
    for row in verification_rows:
        if not isinstance(row, dict) or not row.get("repository"):
            raise SystemExit("invalid verification row")
        repository = str(row["repository"])
        if repository in by_repository:
            raise SystemExit(f"duplicate verification receipt: {repository}")
        by_repository[repository] = row

    downstream_gates = []
    for destination in destinations:
        if not isinstance(destination, dict) or destination.get("required") is not True:
            continue
        repository = destination.get("repository")
        row = by_repository.get(str(repository))
        if row is None:
            raise SystemExit(f"missing required verification receipt: {repository}")
        if row.get("status") != "pass":
            raise SystemExit(f"verification receipt is not pass: {repository}")
        if row.get("issue_number") != destination.get("issue_number"):
            raise SystemExit(f"issue binding mismatch: {repository}")
        head = row.get("observed_destination_head_sha")
        comment_id = row.get("issue_comment_id")
        if not isinstance(head, str) or len(head) != 40:
            raise SystemExit(f"invalid destination head SHA: {repository}")
        if not isinstance(comment_id, int) or comment_id <= 0:
            raise SystemExit(f"invalid issue comment receipt: {repository}")
        downstream_gates.append(
            {
                "repository": repository,
                "required": True,
                "status": "pass",
                "verification_commit": head,
                "issue_number": row.get("issue_number"),
                "issue_comment_id": comment_id,
                "classification": row.get("classification"),
            }
        )

    required_repositories = {
        str(item.get("repository")) for item in destinations if isinstance(item, dict) and item.get("required") is True
    }
    if set(by_repository) != required_repositories:
        raise SystemExit("receipt set must exactly match required dispatch destinations")

    assessment: dict[str, Any] = {
        "artifact_type": "stegcore.release_readiness_assessment",
        "record_type": "release_readiness_assessment",
        "source_repository": "StegVerse-Labs/StegCore",
        "destination_repository": "StegVerse-Labs/StegCore",
        "hash_convention": HASH_CONVENTION,
        "schema_version": "1.1",
        "state": "downstream_verified_release_blocked",
        "runtime_evidence_hash": runtime.get("evidence_hash"),
        "stegcore_commit": runtime.get("stegcore_commit"),
        "governance_commit": runtime.get("governance_commit"),
        "gates": {
            "runtime_validation": "pass",
            "continuity_mapping": "pass",
            "canonical_governance_contract": "pass",
            "evidence_integrity": "pass",
            "governance_freshness": "pending",
            "independent_release_policy": "pending",
            "downstream_verification": "pass",
        },
        "downstream_gates": downstream_gates,
        "release_permitted": False,
        "tag_permitted": False,
        "production_authority_claimed": False,
        "continuity_authority_claimed": False,
        "receipt_minting_authority_claimed": False,
        "completion_event": "independent release policy permits a versioned tag and Governance freshness is independently confirmed",
    }
    assessment["assessment_hash"] = canonical_hash(assessment)
    args.output.write_text(json.dumps(assessment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("DOWNSTREAM_VERIFICATION_RECONCILIATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
