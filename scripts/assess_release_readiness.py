#!/usr/bin/env python3
"""Assess StegCore release readiness from durable runtime validation evidence.

This script never creates a release or grants authority. It emits a deterministic
machine-readable state that remains blocked until independent release policy,
Governance freshness, and all declared downstream verification tasks are satisfied.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from hashlib import sha256
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
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(payload.encode("utf-8")).hexdigest()


def load_object(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()

    evidence = load_object(args.evidence)
    if evidence.get("status") != "pass":
        raise SystemExit("runtime validation evidence must have status=pass")
    if evidence.get("release_state") != "validated_not_released":
        raise SystemExit("runtime evidence must preserve validated_not_released")
    if evidence.get("record_type") != "runtime_validation_evidence":
        raise SystemExit("runtime evidence must use the custody-envelope record_type")
    if evidence.get("hash_convention", {}).get("excluded_field") != "evidence_hash":
        raise SystemExit("runtime evidence must declare evidence_hash exclusion")

    body = dict(evidence)
    declared_evidence_hash = body.pop("evidence_hash", None)
    if not declared_evidence_hash or declared_evidence_hash != canonical_hash(body):
        raise SystemExit("runtime evidence self-hash is invalid")

    downstream = evidence.get("downstream_verification")
    if not isinstance(downstream, list) or not downstream:
        raise SystemExit("runtime evidence must declare downstream verification tasks")

    downstream_gates = [
        {
            "repository": item.get("repository"),
            "required": item.get("required") is True,
            "status": "pending",
        }
        for item in downstream
        if isinstance(item, dict)
    ]

    assessment: dict[str, Any] = {
        "artifact_type": "stegcore.release_readiness_assessment",
        "record_type": "release_readiness_assessment",
        "source_repository": "StegVerse-Labs/StegCore",
        "destination_repository": "StegVerse-Labs/StegCore",
        "hash_convention": HASH_CONVENTION,
        "schema_version": "1.1",
        "state": "validated_not_released",
        "runtime_evidence_hash": evidence.get("evidence_hash"),
        "stegcore_commit": evidence.get("stegcore_commit"),
        "governance_commit": evidence.get("governance_commit"),
        "gates": {
            "runtime_validation": "pass",
            "continuity_mapping": "pass",
            "canonical_governance_contract": "pass",
            "evidence_integrity": "pass",
            "governance_freshness": "pending",
            "independent_release_policy": "pending",
            "downstream_verification": "pending",
        },
        "downstream_gates": downstream_gates,
        "release_permitted": False,
        "tag_permitted": False,
        "production_authority_claimed": False,
        "continuity_authority_claimed": False,
        "receipt_minting_authority_claimed": False,
        "completion_event": (
            "independent release policy permits a versioned tag, Governance freshness "
            "is independently confirmed, and every required downstream verification "
            "gate is durably recorded as pass"
        ),
    }
    assessment["assessment_hash"] = canonical_hash(assessment)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(assessment, indent=2, sort_keys=True) + "\n"
    if args.output.exists() and args.output.read_text(encoding="utf-8") == rendered:
        print("Release-readiness assessment is unchanged.")
        return 0
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Wrote release-readiness assessment to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
