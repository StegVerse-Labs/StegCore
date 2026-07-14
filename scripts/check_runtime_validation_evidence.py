#!/usr/bin/env python3
"""Validate StegCore runtime evidence before it is committed or consumed."""
from __future__ import annotations

import argparse
import json
import pathlib
from hashlib import sha256
from typing import Any

EXPECTED_DESTINATIONS = {
    "StegVerse-Labs/Site",
    "GCAT-BCAT-Engine/Publisher",
    "StegVerse-Labs/admissibility-wiki",
    "StegVerse-Labs/stegguardian-wiki",
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
    if evidence.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if evidence.get("status") != "pass":
        errors.append("status must be pass")
    if evidence.get("release_state") != "validated_not_released":
        errors.append("release_state must remain validated_not_released")

    for field in ("stegcore_commit", "governance_commit", "run_id", "validated_at"):
        if not evidence.get(field):
            errors.append(f"missing {field}")

    checks = evidence.get("checks")
    if not isinstance(checks, dict):
        errors.append("checks must be an object")
    else:
        expected_checks = {
            "continuity_admissibility_mapping": "pass",
            "stegcore_pytest_suite": "pass",
            "canonical_governance_fixture_contract": "pass",
            "positive_control": "ALLOW",
            "replay_mutation": "FAIL-CLOSED",
            "continuity_receipt_minted": False,
        }
        for key, expected in expected_checks.items():
            if checks.get(key) != expected:
                errors.append(f"checks.{key} must be {expected!r}")

    authority = evidence.get("authority_boundary")
    if not isinstance(authority, dict):
        errors.append("authority_boundary must be an object")
    else:
        for key in (
            "production_authority_claimed",
            "continuity_authority_claimed",
            "receipt_minting_authority_claimed",
            "release_authority_claimed",
        ):
            if authority.get(key) is not False:
                errors.append(f"authority_boundary.{key} must be false")

    tasks = evidence.get("downstream_verification_tasks")
    if not isinstance(tasks, list):
        errors.append("downstream_verification_tasks must be a list")
    else:
        destinations = {
            task.get("destination")
            for task in tasks
            if isinstance(task, dict) and task.get("state") == "pending_release_readiness"
        }
        if destinations != EXPECTED_DESTINATIONS:
            errors.append(
                "downstream verification destinations must exactly match the required release follow-up set"
            )

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
