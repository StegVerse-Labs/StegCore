#!/usr/bin/env python3
"""Validate StegVA session consolidation and canonical work claims.

This validator is deterministic, standard-library only, and fail closed. It does not
access or process veteran data.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONSOLIDATION = ROOT / "stegva" / "session_consolidation.json"
CLAIMS = ROOT / "stegva" / "work_claims.json"
TASKS = ROOT / "stegva" / "task_registry.json"
HANDOFF = ROOT / "docs" / "STEGVA_MIRROR_HANDOFF.md"
OUTPUT = ROOT / "stegva" / "receipts" / "session-consolidation-verification.json"
CLAIM_STATES = {
    "UNCLAIMED", "CLAIMED_FOR_IMPLEMENTATION", "CLAIMED_FOR_VALIDATION",
    "CLAIMED_FOR_INTEGRATION", "MACHINE_OWNED", "BLOCKED", "COMPLETE",
    "SUPERSEDED", "MERGED_INTO_CANONICAL_WORKSTREAM",
}


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing required file: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object required: {path.relative_to(ROOT)}")
    return value


def main() -> int:
    errors: list[str] = []
    try:
        consolidation = load(CONSOLIDATION)
        claims = load(CLAIMS)
        tasks = load(TASKS)
        if not HANDOFF.is_file():
            errors.append("missing authoritative StegVA handoff")

        canonical = consolidation.get("canonical_continuation", {})
        if canonical.get("repository") != "StegVerse-Labs/StegCore":
            errors.append("canonical repository must remain StegVerse-Labs/StegCore until transfer receipt exists")
        if canonical.get("handoff") != "docs/STEGVA_MIRROR_HANDOFF.md":
            errors.append("canonical handoff mismatch")
        if consolidation.get("session_role") != "MERGED_INTO_CANONICAL_WORKSTREAM":
            errors.append("session role must be merged into canonical workstream")
        archive_test = consolidation.get("archive_test", {})
        required_archive_flags = {
            "unique_information_remaining_in_chat": False,
            "unassigned_work_remaining": False,
            "canonical_owner_recorded": True,
            "machine_observers_installed": True,
            "deleting_session_impairs_execution": False,
        }
        for key, expected in required_archive_flags.items():
            if archive_test.get(key) is not expected:
                errors.append(f"archive test mismatch: {key}")

        allowed = set(claims.get("allowed_states", []))
        if allowed != CLAIM_STATES:
            errors.append("claim state vocabulary mismatch")
        task_ids = {t.get("id") for t in tasks.get("tasks", []) if isinstance(t, dict)}
        seen: set[str] = set()
        for claim in claims.get("claims", []):
            task_id = claim.get("task_id")
            if task_id in seen:
                errors.append(f"duplicate claim: {task_id}")
            seen.add(task_id)
            if task_id not in task_ids:
                errors.append(f"claim references unknown task: {task_id}")
            if claim.get("role") not in CLAIM_STATES:
                errors.append(f"invalid claim role: {task_id}")
            for field in ("repository", "branch", "claimant", "claim_timestamp", "claim_expiration", "release_condition", "collision_boundary", "next_task_after_release"):
                if not claim.get(field):
                    errors.append(f"claim {task_id} missing {field}")
            if not claim.get("surfaces") or not claim.get("expected_evidence"):
                errors.append(f"claim {task_id} missing surfaces or expected evidence")

        session_claim = claims.get("session_claim", {})
        if session_claim.get("role") != "MERGED_INTO_CANONICAL_WORKSTREAM":
            errors.append("session claim is not released into canonical workstream")
        if session_claim.get("unique_execution_responsibility_remaining") is not False:
            errors.append("session still claims unique execution responsibility")
    except (ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    receipt = {
        "receipt_version": "1.0.0",
        "goal_id": "STEGVA-BOOTSTRAP-001",
        "status": "COMPLETE" if not errors else "FAILED",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "canonical_continuation": "StegVerse-Labs/StegCore/docs/STEGVA_MIRROR_HANDOFF.md",
        "session_archival_ready": not errors,
        "production_data_processed": False,
        "errors": errors,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
