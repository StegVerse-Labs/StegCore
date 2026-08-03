#!/usr/bin/env python3
"""Execute Governance external-evidence fixtures through StegCore."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

from stegcore.external_evidence import evaluate_external_evidence

REQUIRED_FIXTURES = (
    "external_evidence_valid.json",
    "external_evidence_stale.json",
    "external_evidence_drifted.json",
    "external_evidence_incomplete.json",
    "external_evidence_unauthorized.json",
)


def load_json(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def verify(path: pathlib.Path) -> list[str]:
    data = load_json(path)
    expectation = data.get("runtime_expectation")
    if not isinstance(expectation, dict):
        return [f"{path}: missing runtime_expectation"]
    result = evaluate_external_evidence(data)
    errors: list[str] = []
    if result.decision != expectation.get("result"):
        errors.append(f"{path}: {result.decision} != {expectation.get('result')}")
    if result.reason_code != expectation.get("reason_code"):
        errors.append(f"{path}: {result.reason_code} != {expectation.get('reason_code')}")
    if result.receipt.get("continuity_receipt_minted") is not False:
        errors.append(f"{path}: continuity_receipt_minted must be false")
    if result.receipt.get("evidence_provider_execution_authority") is not False:
        errors.append(f"{path}: evidence provider must not receive execution authority")
    if expectation.get("continuity_receipt_minted") is not False:
        errors.append(f"{path}: Governance expectation must prohibit Continuity minting")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("governance_root", type=pathlib.Path)
    args = parser.parse_args()
    fixture_dir = args.governance_root / "docs" / "examples" / "interop"
    errors: list[str] = []
    for name in REQUIRED_FIXTURES:
        path = fixture_dir / name
        if not path.is_file():
            errors.append(f"missing Governance fixture: {path}")
            continue
        try:
            errors.extend(verify(path))
        except Exception as exc:
            errors.append(f"{path}: runtime evaluation failed: {exc}")
    if errors:
        print("Governance external-evidence interoperability verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"External-evidence interoperability passed for {len(REQUIRED_FIXTURES)} Governance fixtures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
