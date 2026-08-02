#!/usr/bin/env python3
"""Deterministic validator for StegCore Originating Choice receipts.

The validator intentionally uses only the Python standard library so the
repository-native workflow has no network or package-install dependency.
It validates the required schema subset and the semantic boundaries that
JSON Schema alone cannot safely express.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

VALID_MODES = {"DISCOVERY", "INVENTION", "IMAGINATION", "CHOICE"}
VALID_ADMISSIBILITY = {"ADMIT", "DENY", "REVIEW_REQUIRED"}
VALID_REVERSIBILITY = {
    "REVERSIBLE",
    "PARTIALLY_REVERSIBLE",
    "IRREVERSIBLE",
    "UNKNOWN",
}
VALID_OUTCOMES = {"SELECT", "REFUSE", "DEFER"}
REQUIRED_TOP_LEVEL = {
    "receipt_id",
    "goal_id",
    "mode",
    "current_state_evidence",
    "insufficiency_statement",
    "candidates",
    "prospective_admissibility",
    "standing_refs",
    "consequence_assessment",
    "reversibility",
    "decision",
    "realization_boundary",
}
ALLOWED_TOP_LEVEL = REQUIRED_TOP_LEVEL


class ValidationError(Exception):
    """Raised when a receipt violates the deterministic contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _nonempty_strings(value: Any, field: str) -> None:
    _require(isinstance(value, list) and bool(value), f"{field} must be a non-empty array")
    _require(
        all(isinstance(item, str) and item.strip() for item in value),
        f"{field} entries must be non-empty strings",
    )


def validate_schema_document(schema: Any) -> None:
    _require(isinstance(schema, dict), "schema must be a JSON object")
    _require(schema.get("type") == "object", "schema root type must be object")
    _require(schema.get("additionalProperties") is False, "schema must fail closed on unknown top-level properties")
    required = schema.get("required")
    _require(isinstance(required, list), "schema.required must be an array")
    _require(set(required) == REQUIRED_TOP_LEVEL, "schema.required does not match the canonical field set")
    properties = schema.get("properties")
    _require(isinstance(properties, dict), "schema.properties must be an object")
    _require(REQUIRED_TOP_LEVEL.issubset(properties), "schema is missing canonical properties")


def validate_receipt(receipt: Any) -> None:
    _require(isinstance(receipt, dict), "receipt must be a JSON object")
    keys = set(receipt)
    _require(REQUIRED_TOP_LEVEL.issubset(keys), f"missing fields: {sorted(REQUIRED_TOP_LEVEL - keys)}")
    _require(keys.issubset(ALLOWED_TOP_LEVEL), f"unknown fields: {sorted(keys - ALLOWED_TOP_LEVEL)}")

    receipt_id = receipt["receipt_id"]
    goal_id = receipt["goal_id"]
    _require(isinstance(receipt_id, str) and len(receipt_id.strip()) >= 8, "receipt_id must contain at least 8 characters")
    _require(isinstance(goal_id, str) and goal_id.startswith("OC-") and goal_id[3:].isdigit() and len(goal_id[3:]) >= 3, "goal_id must match OC- followed by at least three digits")
    _require(receipt["mode"] in VALID_MODES, "mode is not recognized")

    _nonempty_strings(receipt["current_state_evidence"], "current_state_evidence")
    _require(isinstance(receipt["insufficiency_statement"], str) and len(receipt["insufficiency_statement"].strip()) >= 20, "insufficiency_statement must contain at least 20 characters")
    _nonempty_strings(receipt["standing_refs"], "standing_refs")
    _nonempty_strings(receipt["consequence_assessment"], "consequence_assessment")
    _require(receipt["reversibility"] in VALID_REVERSIBILITY, "reversibility is not recognized")
    _require(isinstance(receipt["realization_boundary"], str) and len(receipt["realization_boundary"].strip()) >= 20, "realization_boundary must contain at least 20 characters")

    candidates = receipt["candidates"]
    _require(isinstance(candidates, list) and bool(candidates), "candidates must be a non-empty array")
    candidate_ids: list[str] = []
    for index, candidate in enumerate(candidates):
        _require(isinstance(candidate, dict), f"candidates[{index}] must be an object")
        expected = {"candidate_id", "description", "novelty_basis", "expected_advance"}
        _require(set(candidate) == expected, f"candidates[{index}] fields must equal {sorted(expected)}")
        candidate_id = candidate["candidate_id"]
        _require(isinstance(candidate_id, str) and candidate_id.strip(), f"candidates[{index}].candidate_id must be non-empty")
        for field in ("description", "novelty_basis", "expected_advance"):
            _require(isinstance(candidate[field], str) and len(candidate[field].strip()) >= 20, f"candidates[{index}].{field} must contain at least 20 characters")
        candidate_ids.append(candidate_id)
    _require(len(candidate_ids) == len(set(candidate_ids)), "candidate_id values must be unique")

    admissibility = receipt["prospective_admissibility"]
    _require(isinstance(admissibility, dict), "prospective_admissibility must be an object")
    _require(set(admissibility) == {"status", "basis"}, "prospective_admissibility has incorrect fields")
    _require(admissibility["status"] in VALID_ADMISSIBILITY, "prospective_admissibility.status is not recognized")
    _nonempty_strings(admissibility["basis"], "prospective_admissibility.basis")

    decision = receipt["decision"]
    _require(isinstance(decision, dict), "decision must be an object")
    _require(set(decision).issubset({"outcome", "candidate_id", "reason"}), "decision contains unknown fields")
    _require({"outcome", "reason"}.issubset(decision), "decision requires outcome and reason")
    outcome = decision["outcome"]
    _require(outcome in VALID_OUTCOMES, "decision.outcome is not recognized")
    _require(isinstance(decision["reason"], str) and len(decision["reason"].strip()) >= 20, "decision.reason must contain at least 20 characters")

    selected = decision.get("candidate_id")
    if outcome == "SELECT":
        _require(isinstance(selected, str) and selected in candidate_ids, "SELECT requires a candidate_id present in candidates")
        _require(admissibility["status"] != "DENY", "SELECT is forbidden when prospective admissibility is DENY")
    else:
        _require(selected is None, f"{outcome} must not identify a candidate_id")

    if admissibility["status"] == "DENY":
        _require(outcome == "REFUSE", "DENY requires a REFUSE decision")
    if receipt["reversibility"] == "IRREVERSIBLE":
        _require(admissibility["status"] != "ADMIT", "irreversible candidates cannot be directly ADMIT without review")


def validate_files(schema_path: Path, receipt_path: Path) -> dict[str, Any]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    validate_schema_document(schema)
    validate_receipt(receipt)
    return {
        "status": "COMPLETE",
        "validator": "originating-choice-v1",
        "schema": str(schema_path),
        "receipt": str(receipt_path),
        "goal_id": receipt["goal_id"],
        "receipt_id": receipt["receipt_id"],
        "decision": receipt["decision"]["outcome"],
        "next_executable_task": "OC-001-WORKFLOW",
    }


def self_test() -> dict[str, Any]:
    base = {
        "receipt_id": "oc-test-0001",
        "goal_id": "OC-999",
        "mode": "CHOICE",
        "current_state_evidence": ["evidence/ref"],
        "insufficiency_statement": "The existing option set cannot produce the required governed future state.",
        "candidates": [{
            "candidate_id": "candidate-a",
            "description": "A sufficiently detailed candidate state for deterministic validation.",
            "novelty_basis": "The candidate introduces a capability absent from the current recorded state.",
            "expected_advance": "The candidate expands governed choice without granting execution authority.",
        }],
        "prospective_admissibility": {"status": "REVIEW_REQUIRED", "basis": ["Review remains required before realization."]},
        "standing_refs": ["standing/ref"],
        "consequence_assessment": ["No runtime mutation occurs during receipt validation."],
        "reversibility": "REVERSIBLE",
        "decision": {"outcome": "SELECT", "candidate_id": "candidate-a", "reason": "The candidate is selected for specification and review rather than execution."},
        "realization_boundary": "Validation authorizes no deployment, financial action, or irreversible execution.",
    }
    validate_receipt(base)

    failures = 0
    cases: list[tuple[str, dict[str, Any]]] = []

    missing_candidate = json.loads(json.dumps(base))
    missing_candidate["decision"]["candidate_id"] = "absent"
    cases.append(("unknown selected candidate", missing_candidate))

    deny_select = json.loads(json.dumps(base))
    deny_select["prospective_admissibility"]["status"] = "DENY"
    cases.append(("deny cannot select", deny_select))

    refuse_with_candidate = json.loads(json.dumps(base))
    refuse_with_candidate["decision"]["outcome"] = "REFUSE"
    cases.append(("refuse cannot select candidate", refuse_with_candidate))

    duplicate_candidate = json.loads(json.dumps(base))
    duplicate_candidate["candidates"].append(json.loads(json.dumps(duplicate_candidate["candidates"][0])))
    cases.append(("candidate identifiers must be unique", duplicate_candidate))

    for name, case in cases:
        try:
            validate_receipt(case)
        except ValidationError:
            failures += 1
        else:
            raise ValidationError(f"self-test expected rejection: {name}")

    return {
        "status": "COMPLETE",
        "validator": "originating-choice-v1",
        "positive_cases": 1,
        "negative_cases": failures,
        "next_executable_task": "OC-001-WORKFLOW",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", nargs="?", type=Path)
    parser.add_argument("receipt", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--receipt-output", type=Path)
    args = parser.parse_args()

    try:
        if args.self_test:
            result = self_test()
        else:
            if args.schema is None or args.receipt is None:
                parser.error("schema and receipt are required unless --self-test is used")
            result = validate_files(args.schema, args.receipt)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        result = {
            "status": "FAILED",
            "validator": "originating-choice-v1",
            "error": str(exc),
            "next_executable_task": "REVIEW_REQUIRED",
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.receipt_output:
        args.receipt_output.parent.mkdir(parents=True, exist_ok=True)
        args.receipt_output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
