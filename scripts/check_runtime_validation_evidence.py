#!/usr/bin/env python3
"""Validate StegCore runtime evidence before it is committed or consumed."""
from __future__ import annotations

import argparse
import json
import pathlib
from hashlib import sha256
from typing import Any

EXPECTED_DESTINATIONS = {
    "StegVerse-Labs/Site": 14,
    "GCAT-BCAT-Engine/Publisher": 4,
    "StegVerse-Labs/admissibility-wiki": 19,
    "StegVerse-002/stegguardian-wiki": 4,
}


def canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path)
    args = parser.parse_args()

    try:
        evidence = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Invalid evidence file: {exc}")
        return 1

    errors: list[str] = []
    if not isinstance(evidence, dict):
        print("Evidence root must be an object.")
        return 1

    if evidence.get("artifact_type") != "stegcore.runtime_validation_evidence":
        errors.append("artifact_type is invalid")
    if evidence.get("schema_version") != "1.1":
        errors.append("schema_version must be 1.1")
    if evidence.get("status") != "pass":
        errors.append("status must be pass")
    if evidence.get("release_state") != "validated_not_released":
        errors.append("release_state must remain validated_not_released")

    for field in (
        "stegcore_commit",
        "governance_commit",
        "run_id",
        "validated_at",
        "downstream_dispatch_path",
        "downstream_dispatch_hash",
    ):
        if not evidence.get(field):
            errors.append(f"missing {field}")

    checks = evidence.get("checks")
    expected_checks = {
        "continuity_admissibility_mapping": "pass",
        "stegcore_pytest_suite": "pass",
        "canonical_governance_fixture_contract": "pass",
        "positive_control": "ALLOW",
        "replay_mutation": "FAIL-CLOSED",
        "continuity_receipt_minted": False,
    }
    if not isinstance(checks, dict):
        errors.append("checks must be an object")
    else:
        for key, expected in expected_checks.items():
            if checks.get(key) != expected:
                errors.append(f"checks.{key} must be {expected!r}")

    authority = evidence.get("authority_boundary")
    required_false = (
        "production_authority_claimed",
        "continuity_authority_claimed",
        "receipt_minting_authority_claimed",
        "release_authority_claimed",
        "cross_repository_mutation_authority_claimed",
    )
    if not isinstance(authority, dict):
        errors.append("authority_boundary must be an object")
    else:
        for key in required_false:
            if authority.get(key) is not False:
                errors.append(f"authority_boundary.{key} must be false")

    downstream = evidence.get("downstream_verification")
    if not isinstance(downstream, list):
        errors.append("downstream_verification must be a list")
    else:
        observed: dict[str, int] = {}
        for item in downstream:
            if not isinstance(item, dict):
                errors.append("downstream verification entries must be objects")
                continue
            repository = item.get("repository")
            issue_number = item.get("issue_number")
            if isinstance(repository, str) and isinstance(issue_number, int):
                observed[repository] = issue_number
            if item.get("required") is not True:
                errors.append(f"{repository}: required must be true")
            if item.get("state") != "queued":
                errors.append(f"{repository}: state must be queued")
            if not item.get("issue_url") or not item.get("handoff"):
                errors.append(f"{repository}: issue_url and handoff are required")
        if observed != EXPECTED_DESTINATIONS:
            errors.append("downstream repositories and issue numbers must match the dispatch record")

    supplied_hash = evidence.get("evidence_hash")
    hash_basis = dict(evidence)
    hash_basis.pop("evidence_hash", None)
    if supplied_hash != canonical_hash(hash_basis):
        errors.append("evidence_hash does not match the canonical evidence payload")

    if errors:
        print("Runtime validation evidence check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Runtime validation evidence check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
