#!/usr/bin/env python3
"""Evaluate Governance three-layer fixtures through the StegCore runtime contract.

The Governance checkout path is supplied by CI. This script does not modify either
repository and does not verify or mint Continuity receipts.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

from stegcore.three_layer import (
    ExecutionBoundary,
    JudgmentConditions,
    SignalAdmission,
    ThreeLayerRequest,
    evaluate_three_layer,
)

REQUIRED_FIXTURES = (
    "condition_degraded_judgment_gdr.json",
    "signal_admission_drift_gdr.json",
    "governance_validation_of_drift_gdr.json",
    "three_layer_positive_control_gdr.json",
    "three_layer_replay_baseline_gdr.json",
    "three_layer_replay_mutated_gdr.json",
)


def load_json(path: pathlib.Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def _is_supported_isolation(value: str) -> str:
    if value in {"supported", "review_available"}:
        return "supported"
    if value == "isolated":
        return "isolated"
    return "unknown"


def _uncertainty(value: str) -> str:
    if value in {"bounded", "apparently_bounded"}:
        return "bounded"
    if value in {"material", "material_unresolved", "unbounded"}:
        return "material"
    return "unknown"


def _transformations(value: Any) -> tuple[tuple[str, ...], bool]:
    if not isinstance(value, list):
        return (), False
    rendered: list[str] = []
    complete = True
    for item in value:
        if isinstance(item, str):
            rendered.append(item)
            continue
        if isinstance(item, dict):
            rendered.append(str(item.get("type", item.get("transformation_id", "unknown"))))
            if item.get("reconstructable") is not True:
                complete = False
            continue
        rendered.append(str(item))
        complete = False
    return tuple(rendered), complete


def request_from_fixture(data: dict[str, Any]) -> ThreeLayerRequest:
    judgment = data["judgment_conditions"]
    signal = data["signal_admission"]
    boundary = data["execution_boundary"]
    controls = data.get("control_assertions", {})
    transformations, provenance_complete = _transformations(signal.get("transformations", []))

    actor_authority_current = controls.get("authority_check", "pass") == "pass"
    policy_current = controls.get("policy_check", "pass") == "pass"

    return ThreeLayerRequest(
        judgment_conditions=JudgmentConditions(
            refusal_available=bool(judgment.get("refusal_available")),
            operator_recoverability=judgment.get("operator_recoverability", "unknown"),
            workload_state=judgment.get("workload_state", "unknown"),
            time_pressure=judgment.get("time_pressure", "unknown"),
            isolation_state=_is_supported_isolation(judgment.get("isolation_state", "unknown")),
            evidence_refs=tuple(judgment.get("condition_receipt_ids", [])),
        ),
        signal_admission=SignalAdmission(
            admitted_signal_refs=tuple(signal.get("admitted_signal_refs", [])),
            excluded_signal_refs=tuple(signal.get("excluded_signal_refs", [])),
            transformations=transformations,
            missing_inputs=tuple(signal.get("missing_inputs", [])),
            uncertainty_state=_uncertainty(signal.get("uncertainty_state", "unknown")),
            reference_state_hash=signal.get("reference_state_hash", ""),
            expected_reference_state_hash=signal.get("authorized_reference_state_hash", ""),
            reconstruction_available=bool(signal.get("reconstruction_available")),
            transformation_provenance_complete=provenance_complete,
        ),
        execution_boundary=ExecutionBoundary(
            actor_authority_current=actor_authority_current,
            policy_current=policy_current,
            delegation_current=bool(boundary.get("delegation_ref")),
            evidence_current=bool(boundary.get("evidence_refs")),
            affected_entity_conditions_represented=bool(boundary.get("affected_entity_refs")),
            recoverability_profile=(
                boundary.get("recoverability_profile")
                if boundary.get("recoverability_profile") in {"recoverable", "constrained", "irreversible", "unknown"}
                else "unknown"
            ),
            validity_window_open=boundary.get("validity_window") != "closed",
            policy_ref=boundary.get("policy_ref", ""),
            delegation_ref=boundary.get("delegation_ref", ""),
            evidence_refs=tuple(boundary.get("evidence_refs", [])),
        ),
        action=data.get("evaluated_inputs", {}).get("source", "governance.fixture.evaluate"),
        target="StegVerse-Labs/StegCore",
        scope=data.get("decision_id", "unknown-fixture"),
    )


def verify_fixture(path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    data = load_json(path)
    expectation = data.get("runtime_expectation")
    if not isinstance(expectation, dict):
        return [f"{path}: missing runtime_expectation"]

    result = evaluate_three_layer(request_from_fixture(data))
    if result.decision != expectation.get("result"):
        errors.append(
            f"{path}: decision {result.decision} != expected {expectation.get('result')}"
        )
    if result.reason_code != expectation.get("reason_code"):
        errors.append(
            f"{path}: reason {result.reason_code} != expected {expectation.get('reason_code')}"
        )
    if result.receipt.get("continuity_receipt_minted") is not False:
        errors.append(f"{path}: runtime receipt must state continuity_receipt_minted=false")
    if expectation.get("continuity_receipt_minted") is not False:
        errors.append(f"{path}: Governance expectation must forbid Continuity receipt minting")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("governance_root", type=pathlib.Path)
    args = parser.parse_args()

    fixture_dir = args.governance_root / "docs" / "examples" / "fixtures"
    errors: list[str] = []
    for name in REQUIRED_FIXTURES:
        path = fixture_dir / name
        if not path.exists():
            errors.append(f"missing Governance fixture: {path}")
            continue
        try:
            errors.extend(verify_fixture(path))
        except Exception as exc:
            errors.append(f"{path}: contract evaluation failed: {exc}")

    if errors:
        print("Governance/StegCore three-layer contract verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Governance/StegCore three-layer contract verification passed for "
        f"{len(REQUIRED_FIXTURES)} canonical fixtures."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
