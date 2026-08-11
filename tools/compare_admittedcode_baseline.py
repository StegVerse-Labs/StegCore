#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = ROOT / "benchmarks" / "admittedcode-baseline-v0.2.0.json"


def _get(receipt: dict, path: tuple[str, ...]):
    value = receipt
    for key in path:
        value = value[key]
    return value


def compare(receipt: dict, baseline: dict) -> dict:
    bands = baseline["regression_warning_bands"]
    checks = {
        "core_p95_ms": {
            "observed": _get(receipt, ("latency_and_resources", "core_wall_latency", "p95_ms")),
            "max": bands["core_p95_ms_max"],
        },
        "governance_overhead_p95_ms": {
            "observed": _get(receipt, ("governance_overhead", "governance_overhead", "p95_ms")),
            "max": bands["governance_overhead_p95_ms_max"],
        },
        "cold_start_identity_ms": {
            "observed": _get(receipt, ("cold_start", "identity_ms")),
            "max": bands["cold_start_identity_ms_max"],
        },
        "cold_start_self_test_ms": {
            "observed": _get(receipt, ("cold_start", "self_test_ms")),
            "max": bands["cold_start_self_test_ms_max"],
        },
    }
    for concurrency, minimum in bands["throughput_rps_min"].items():
        checks[f"throughput_rps_{concurrency}"] = {
            "observed": _get(receipt, ("throughput", concurrency, "requests_per_second")),
            "min": minimum,
        }

    warnings = []
    for name, check in checks.items():
        if "max" in check:
            passed = check["observed"] <= check["max"]
        else:
            passed = check["observed"] >= check["min"]
        check["pass"] = passed
        if not passed:
            warnings.append(name)

    runtime_compatible = (
        receipt.get("runtime_identity", {}).get("observed") == baseline.get("runtime_identity")
        and receipt.get("runtime_identity", {}).get("canonical_runtime_observed") == baseline.get("canonical_runtime")
    )
    return {
        "schema_version": "stegverse.admittedcode.performance-regression.v1",
        "baseline_state": baseline.get("baseline_state"),
        "baseline_product_version": baseline.get("product_version"),
        "observed_product_version": receipt.get("product_version"),
        "baseline_sample_count": baseline.get("sample_count"),
        "compatible_baseline": runtime_compatible,
        "checks": checks,
        "warning_count": len(warnings),
        "warnings": warnings,
        "regression_warning_pass": runtime_compatible and not warnings,
        "release_blocking_correctness_pass": receipt.get("policy_assessment", {}).get("release_blocking_pass") is True,
        "note": "Regression bands may compare compatible successor product versions when canonical runtime identity is unchanged. Bands are provisional warnings until promotion criteria are met; correctness/security gates remain authoritative.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare an AdmittedCode performance receipt to the accepted hosted baseline.")
    parser.add_argument("receipt", help="Path to admittedcode performance receipt JSON")
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    parser.add_argument("--output")
    parser.add_argument("--fail-on-warning", action="store_true")
    args = parser.parse_args()

    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    report = compare(receipt, baseline)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")

    if not report["compatible_baseline"]:
        return 2
    if args.fail_on_warning and not report["regression_warning_pass"]:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
