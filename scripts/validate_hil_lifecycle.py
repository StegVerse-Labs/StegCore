#!/usr/bin/env python3
"""Validate monotonic HIL lifecycle evidence and emit a StegCore decision."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data" / "hil-lifecycle-state-contract.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def validate(evidence: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    states = contract["states"]
    observed = evidence.get("observed_states", [])
    if not observed:
        errors.append("missing_observed_states")
    indexes = []
    for state in observed:
        if state not in states:
            errors.append(f"unknown_state:{state}")
        else:
            indexes.append(states.index(state))
    if indexes != sorted(set(indexes)):
        errors.append("state_regression_or_replay")
    if indexes and indexes != list(range(indexes[-1] + 1)):
        errors.append("skipped_state")

    identities = evidence.get("identities", {})
    for field in contract["required_identity_fields"]:
        value = identities.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"missing_identity:{field}")
    for receipt in evidence.get("receipts", []):
        receipt_identity = receipt.get("identities", {})
        for field, expected in identities.items():
            actual = receipt_identity.get(field)
            if actual is not None and actual != expected:
                errors.append(f"identity_drift:{receipt.get('receipt_id','unknown')}:{field}")

    authority = evidence.get("authority", {})
    for field in contract["authority_fields"]:
        if not isinstance(authority.get(field), bool):
            errors.append(f"missing_boolean_authority:{field}")
    if authority.get("publication_authorized") and not evidence.get("publication_decision_receipt"):
        errors.append("publication_without_separate_decision")
    if authority.get("release_authorized") and not evidence.get("release_decision_receipt"):
        errors.append("release_without_separate_decision")
    if "STEGCORE_ACTIVATED" in observed and (authority.get("publication_authorized") or authority.get("release_authorized")):
        errors.append("activation_must_not_grant_publication_or_release")

    complete = observed == states
    decision = "ACTIVATED" if complete and not errors else "CONTINUE_INTERNAL_DEVELOPMENT"
    internal_actions = []
    if not complete:
        next_index = len(observed)
        if next_index < len(states):
            internal_actions.append({"state_needed": states[next_index], "classification": "INTERNAL_EXECUTABLE_TASK"})
    for error in errors:
        internal_actions.append({"repair": error, "classification": "INTERNAL_EXECUTABLE_TASK"})
    result = {
        "schema_version": "HIL-STEGCORE-ACTIVATION-DECISION-v1",
        "decision": decision,
        "valid": not errors,
        "errors": errors,
        "external_tasks": [],
        "halted": False,
        "next_internal_actions": internal_actions,
        "evidence_sha256": hashlib.sha256(canonical(evidence)).hexdigest(),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(load(args.evidence), load(CONTRACT))
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
