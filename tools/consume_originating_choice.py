#!/usr/bin/env python3
"""Validate and route an Originating Choice receipt without granting execution authority."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def load_validator(path: Path):
    spec = importlib.util.spec_from_file_location("originating_choice_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load originating choice validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def route_receipt(receipt: dict[str, Any]) -> str:
    status = receipt["prospective_admissibility"]["status"]
    outcome = receipt["decision"]["outcome"]
    reversibility = receipt["reversibility"]
    if status == "DENY" and outcome == "REFUSE":
        return "CLOSED_REFUSAL"
    if outcome == "DEFER":
        return "DEFERRED_REVIEW"
    if status == "REVIEW_REQUIRED" or reversibility in {"IRREVERSIBLE", "PARTIALLY_REVERSIBLE", "UNKNOWN"}:
        return "GOVERNED_REVIEW"
    if status == "ADMIT" and outcome == "SELECT" and reversibility == "REVERSIBLE":
        return "REALIZATION_REVIEW"
    return "REVIEW_REQUIRED"


def consume(schema_path: Path, receipt_path: Path, validator_path: Path) -> dict[str, Any]:
    validator = load_validator(validator_path)
    validator.validate_files(schema_path, receipt_path)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    route = route_receipt(receipt)
    return {
        "integration_receipt_id": f"integration-{receipt['receipt_id']}",
        "goal_id": receipt["goal_id"],
        "source_receipt_id": receipt["receipt_id"],
        "validation_status": "COMPLETE",
        "route": route,
        "execution_authority": False,
        "next_executable_task": {
            "CLOSED_REFUSAL": "NONE",
            "DEFERRED_REVIEW": "REVIEW_WHEN_RELEASE_CONDITION_EXISTS",
            "GOVERNED_REVIEW": "ASSIGN_EXISTING_GOVERNED_REVIEW_BOUNDARY",
            "REALIZATION_REVIEW": "REQUEST_SEPARATE_EXECUTION_AUTHORITY",
            "REVIEW_REQUIRED": "REVIEW_REQUIRED",
        }[route],
    }


def self_test() -> dict[str, Any]:
    base = {
        "prospective_admissibility": {"status": "REVIEW_REQUIRED"},
        "decision": {"outcome": "SELECT"},
        "reversibility": "REVERSIBLE",
    }
    cases = [
        (base, "GOVERNED_REVIEW"),
        ({**base, "prospective_admissibility": {"status": "DENY"}, "decision": {"outcome": "REFUSE"}}, "CLOSED_REFUSAL"),
        ({**base, "decision": {"outcome": "DEFER"}}, "DEFERRED_REVIEW"),
        ({**base, "prospective_admissibility": {"status": "ADMIT"}}, "REALIZATION_REVIEW"),
        ({**base, "prospective_admissibility": {"status": "ADMIT"}, "reversibility": "UNKNOWN"}, "GOVERNED_REVIEW"),
    ]
    for receipt, expected in cases:
        actual = route_receipt(receipt)
        if actual != expected:
            raise RuntimeError(f"expected {expected}, got {actual}")
    return {"status": "COMPLETE", "positive_routes": len(cases), "execution_authority": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", nargs="?", type=Path)
    parser.add_argument("receipt", nargs="?", type=Path)
    parser.add_argument("--validator", type=Path, default=Path("tools/validate_originating_choice.py"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        result = self_test() if args.self_test else consume(args.schema, args.receipt, args.validator)
    except Exception as exc:
        result = {"status": "FAILED", "error": str(exc), "execution_authority": False}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
