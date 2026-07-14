#!/usr/bin/env python3
"""Verify AURI-004 gateway invariants without external services."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stegcore.auri_gateway import canonical_sha256, evaluate_auri_candidate
from stegcore.decision import VerifiedReceiptEnvelope


def candidate() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "candidate_id": "auri:verification",
        "prepared_by": "stegverse:auri",
        "action": "prepare_repository_change",
        "target": "StegVerse-Labs/StegTalk",
        "scope": "advisory_only",
        "policy_ref": "policy:auri-l1",
        "delegation_ref": "delegation:advisory-only",
        "execution_context": {"consequential": False},
        "auri_posture": {
            "execution_authority": False,
            "final_consequence_authority": False,
            "requires_external_admissibility": True,
        },
    }


def verified_receipt() -> VerifiedReceiptEnvelope:
    return VerifiedReceiptEnvelope(
        receipt_id="receipt:verified",
        key_id="key:verification",
        verified=True,
        issued_at="2026-07-14T00:00:00Z",
    )


def verify() -> dict[str, object]:
    value = candidate()
    allowed = evaluate_auri_candidate(
        value,
        verified_receipt=verified_receipt(),
        commit_candidate_sha256=canonical_sha256(value),
    )
    if allowed.decision != "allow" or allowed.execution_performed is not False:
        raise ValueError("valid advisory candidate did not allow without execution")

    mismatch = evaluate_auri_candidate(
        value,
        verified_receipt=verified_receipt(),
        commit_candidate_sha256="0" * 64,
    )
    if mismatch.decision != "deny" or mismatch.reason_code != "commit.candidate_hash_mismatch":
        raise ValueError("commit-time mismatch did not deny")

    deferred = evaluate_auri_candidate(
        value,
        verified_receipt=verified_receipt(),
        policy_shapes=["guardian"],
    )
    if deferred.decision != "defer":
        raise ValueError("guardian policy did not defer")

    forbidden = candidate()
    forbidden["auri_posture"]["execution_authority"] = True
    denied = evaluate_auri_candidate(forbidden, verified_receipt=verified_receipt())
    if denied.reason_code != "auri.execution_authority.forbidden":
        raise ValueError("Auri execution-authority claim did not deny")

    return {
        "result": "PASS",
        "scope": "AURI-004 StegCore gateway",
        "allow_verified": True,
        "deny_commit_mismatch_verified": True,
        "defer_policy_verified": True,
        "no_execution_verified": True,
        "next_task": "AURI-005 Continuity receipts",
    }


def main() -> int:
    try:
        report = verify()
    except (KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"result": "FAIL", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
