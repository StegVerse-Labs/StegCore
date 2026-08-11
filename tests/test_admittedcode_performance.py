from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def _load_module(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_benchmark_module():
    return _load_module("tools/run_admittedcode_benchmarks.py", "admittedcode_benchmarks")


def test_correctness_and_binding_metrics_are_fail_closed():
    bench = _load_benchmark_module()
    base = bench.load_base_payload()
    metrics = bench.correctness_metrics(bench.build_vectors())
    assert metrics["four_disposition_correctness_rate"] == 1.0
    assert metrics["false_allow_rate"] == 0.0
    assert metrics["fail_closed_integrity_rate"] == 1.0
    assert metrics["matrix_completeness_rate"] == 1.0
    assert metrics["reason_code_presence_rate"] == 1.0
    assert metrics["canonical_receipt_hash_presence_rate"] == 1.0
    assert bench.candidate_binding_metric(base) == 1.0


def test_replay_and_interface_equivalence_are_deterministic():
    bench = _load_benchmark_module()
    base = bench.load_base_payload()
    assert bench.replay_metric(base, 5)["deterministic_semantic_replay_rate"] == 1.0
    interfaces = bench.interface_metric(base)
    assert interfaces["service_equivalent"] is True
    assert interfaces["cli_equivalent"] is True
    assert interfaces["cross_interface_equivalence_rate"] == 1.0


def test_performance_policy_has_release_blocking_security_kpis():
    policy = json.loads((ROOT / "benchmarks/admittedcode-performance-policy.json").read_text(encoding="utf-8"))
    kpis = policy["headline_kpis"]
    assert kpis["false_allow_rate"]["target_max"] == 0.0
    assert kpis["false_allow_rate"]["release_blocking"] is True
    assert kpis["fail_closed_integrity_rate"]["target_min"] == 1.0
    assert kpis["candidate_binding_integrity_rate"]["target_min"] == 1.0
    assert kpis["deterministic_semantic_replay_rate"]["target_min"] == 1.0
    assert kpis["cross_interface_equivalence_rate"]["target_min"] == 1.0
    assert kpis["parallel_evaluator_escape_count"]["target_max"] == 0


def test_provisional_hosted_baseline_is_versioned_and_non_fabricated():
    baseline = json.loads((ROOT / "benchmarks/admittedcode-baseline-v0.2.0.json").read_text(encoding="utf-8"))
    assert baseline["schema_version"] == "stegverse.admittedcode.performance-baseline.v1"
    assert baseline["product_version"] == "0.2.0"
    assert baseline["sample_count"] == len(baseline["samples"])
    assert baseline["sample_count"] >= 2
    assert baseline["developer_experience"]["human_install_to_first_allow_minutes"] is None
    assert baseline["developer_experience"]["human_failed_request_diagnosis_minutes"] is None
    assert baseline["developer_experience"]["status"] == "UNMEASURED_REQUIRES_UNFAMILIAR_OPERATOR"


def test_baseline_comparator_accepts_observed_band_values():
    comparator = _load_module("tools/compare_admittedcode_baseline.py", "admittedcode_baseline")
    baseline = json.loads((ROOT / "benchmarks/admittedcode-baseline-v0.2.0.json").read_text(encoding="utf-8"))
    receipt = {
        "product_version": "0.2.0",
        "runtime_identity": {
            "observed": baseline["runtime_identity"],
            "canonical_runtime_observed": baseline["canonical_runtime"],
        },
        "latency_and_resources": {"core_wall_latency": {"p95_ms": 1.5}},
        "governance_overhead": {"governance_overhead": {"p95_ms": 0.4}},
        "cold_start": {"identity_ms": 500.0, "self_test_ms": 500.0},
        "throughput": {
            "1": {"requests_per_second": 2500.0},
            "10": {"requests_per_second": 2500.0},
            "50": {"requests_per_second": 2500.0},
        },
        "policy_assessment": {"release_blocking_pass": True},
    }
    report = comparator.compare(receipt, baseline)
    assert report["compatible_baseline"] is True
    assert report["regression_warning_pass"] is True
    assert report["warning_count"] == 0


def test_benchmark_runner_emits_versioned_receipt(tmp_path):
    output = tmp_path / "receipt.json"
    proc = subprocess.run(
        [
            sys.executable,
            "tools/run_admittedcode_benchmarks.py",
            "--iterations",
            "5",
            "--replay-iterations",
            "3",
            "--throughput-requests",
            "10",
            "--concurrency",
            "1,2",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert receipt["schema_version"] == "stegverse.admittedcode.performance-receipt.v1"
    assert receipt["policy_assessment"]["release_blocking_pass"] is True
    assert receipt["developer_experience"]["status"] == "MANUAL_OBSERVATION_REQUIRED"
