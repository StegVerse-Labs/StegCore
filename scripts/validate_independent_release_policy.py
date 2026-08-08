#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

ARTIFACT_TYPE = "stegcore.independent_release_policy_evidence"
GOVERNANCE = "StegVerse-Labs/Governance"


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def validate(decision: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    required = (
        "artifact_type", "schema_version", "status", "decision", "policy_id",
        "decision_owner", "source_repository", "source_commit", "source_path",
        "decision_hash", "candidate_version", "candidate_tag", "candidate_commit",
        "next_permitted_action", "release_created", "tag_created",
        "deployment_authorized", "continuity_receipt_minted",
    )
    for key in required:
        if key not in decision or decision.get(key) in (None, ""):
            errors.append(f"missing:{key}")

    checks = {
        "artifact_type": decision.get("artifact_type") == ARTIFACT_TYPE,
        "schema_version": decision.get("schema_version") == "1.0",
        "status_pass": decision.get("status") == "pass",
        "decision_allow": decision.get("decision") == "ALLOW",
        "decision_owner": decision.get("decision_owner") == GOVERNANCE,
        "source_repository": decision.get("source_repository") == GOVERNANCE,
        "candidate_binding": decision.get("candidate_commit") == readiness.get("stegcore_commit"),
        "tag_version_binding": decision.get("candidate_tag") == f"v{decision.get('candidate_version')}",
        "next_action_bounded": decision.get("next_permitted_action") == "create annotated tag only",
        "release_not_created": decision.get("release_created") is False,
        "tag_not_created": decision.get("tag_created") is False,
        "deployment_not_authorized": decision.get("deployment_authorized") is False,
        "continuity_not_minted": decision.get("continuity_receipt_minted") is False,
        "source_commit_shape": isinstance(decision.get("source_commit"), str) and len(decision.get("source_commit")) == 40,
        "decision_hash_shape": isinstance(decision.get("decision_hash"), str) and len(decision.get("decision_hash")) == 64,
    }
    for name, passed in checks.items():
        if not passed:
            errors.append(name)

    status = "PASS" if not errors else "BLOCKED"
    return {
        "schema_version": "stegcore.independent-release-policy-validation.v1",
        "status": status,
        "policy_id": decision.get("policy_id"),
        "decision_hash": decision.get("decision_hash"),
        "source_repository": decision.get("source_repository"),
        "source_commit": decision.get("source_commit"),
        "source_path": decision.get("source_path"),
        "candidate_commit": decision.get("candidate_commit"),
        "candidate_tag": decision.get("candidate_tag"),
        "exact_candidate_binding": checks["candidate_binding"],
        "next_permitted_action": decision.get("next_permitted_action") if status == "PASS" else None,
        "errors": errors,
        "release_policy_gate": "pass" if status == "PASS" else "pending_or_denied",
        "release_authority_created": False,
        "tag_authority_created": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", type=pathlib.Path, required=True)
    parser.add_argument("--readiness", type=pathlib.Path, default=pathlib.Path("evidence/release-readiness.json"))
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()

    if not args.decision.exists():
        result = {
            "schema_version": "stegcore.independent-release-policy-validation.v1",
            "status": "BLOCKED",
            "errors": ["independent_policy_decision_missing"],
            "release_policy_gate": "pending_or_denied",
            "release_authority_created": False,
            "tag_authority_created": False,
        }
    else:
        result = validate(load(args.decision), load(args.readiness))

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
