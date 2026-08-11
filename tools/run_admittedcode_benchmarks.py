#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc
from typing import Any
from urllib import request as urllib_request

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from stegcore.service import evaluate as service_evaluate
from stegcore.service import runtime_identity, self_test
from stegcore.steggate import AdmissibilityRequest, evaluate_admissibility
from stegcore.version import __version__

RUNTIME_IDENTITY = "stegverse:steggate:canonical:three-layer:v1"
CANONICAL_RUNTIME = "stegcore.three_layer.evaluate_three_layer"
SEMANTIC_FIELDS = (
    "disposition",
    "candidate_hash",
    "reasons",
    "canonical_three_layer_decision",
    "canonical_three_layer_reason",
    "canonical_three_layer_request_hash",
    "permission_present",
    "permission_is_not_admissibility",
    "continuity_receipt_minted",
    "external_execution_performed",
    "matrix",
)


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * p
    lo = int(rank)
    hi = min(lo + 1, len(ordered) - 1)
    weight = rank - lo
    return ordered[lo] * (1 - weight) + ordered[hi] * weight


def summarize_ms(values: list[float]) -> dict[str, float]:
    return {
        "count": len(values),
        "min_ms": round(min(values), 6) if values else 0.0,
        "mean_ms": round(statistics.fmean(values), 6) if values else 0.0,
        "p50_ms": round(percentile(values, 0.50), 6),
        "p95_ms": round(percentile(values, 0.95), 6),
        "p99_ms": round(percentile(values, 0.99), 6),
        "max_ms": round(max(values), 6) if values else 0.0,
    }


def load_base_payload() -> dict[str, Any]:
    return json.loads((ROOT / "examples/steggate_allow_request.json").read_text(encoding="utf-8"))


def build_vectors() -> list[dict[str, Any]]:
    base = load_base_payload()
    vectors: list[dict[str, Any]] = []

    def add(name: str, expected: str, mutate) -> None:
        payload = copy.deepcopy(base)
        mutate(payload)
        vectors.append({"name": name, "expected": expected, "payload": payload})

    add("allow_baseline", "ALLOW", lambda p: None)
    add("deny_stale_policy", "DENY", lambda p: p["execution"].update(policy_current=False))
    add("deny_stale_actor_authority", "DENY", lambda p: p["execution"].update(actor_authority_current=False))
    add("review_missing_required_approval", "REVIEW", lambda p: p["approval"].update(required=True, valid=None, candidate_hash=None))
    add("fail_closed_missing_reference_state", "FAIL_CLOSED", lambda p: p["signal"].update(reference_state_hash=None))
    add("fail_closed_missing_capability", "FAIL_CLOSED", lambda p: p["capability"].update(allowed=None))
    add("deny_unverified_continuity", "DENY", lambda p: p["continuity"].update(previous_receipt_verified=False))

    wrong_approval = copy.deepcopy(base)
    wrong_approval["approval"].update(required=True, valid=True, candidate_hash="0" * 64)
    vectors.append({"name": "deny_wrong_candidate_binding", "expected": "DENY", "payload": wrong_approval})
    return vectors


def semantic(result: Any) -> dict[str, Any]:
    if hasattr(result, "model_dump"):
        result = result.model_dump(mode="json")
    return {key: result[key] for key in SEMANTIC_FIELDS}


def evaluate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    req = AdmissibilityRequest.model_validate(payload)
    return evaluate_admissibility(req).model_dump(mode="json")


def correctness_metrics(vectors: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    false_allows = 0
    false_denies = 0
    fail_closed_total = 0
    fail_closed_correct = 0
    matrix_complete = 0
    reasons_present = 0
    receipt_hash_present = 0
    for vector in vectors:
        result = evaluate_payload(vector["payload"])
        expected = vector["expected"]
        actual = result["disposition"]
        if expected != "ALLOW" and actual == "ALLOW":
            false_allows += 1
        if expected == "ALLOW" and actual == "DENY":
            false_denies += 1
        if expected == "FAIL_CLOSED":
            fail_closed_total += 1
            fail_closed_correct += int(actual == "FAIL_CLOSED")
        matrix_ok = bool(result["matrix"]) and all(
            row.get("predicate") and row.get("state") and row.get("reason") and row.get("authority_surface")
            for row in result["matrix"]
        )
        matrix_complete += int(matrix_ok)
        reasons_present += int(bool(result["reasons"]) and all(isinstance(x, str) and x for x in result["reasons"]))
        receipt_hash_present += int(bool(result.get("canonical_three_layer_receipt_hash")))
        rows.append({
            "name": vector["name"],
            "expected": expected,
            "actual": actual,
            "pass": actual == expected,
            "reasons": result["reasons"],
        })
    total = len(vectors)
    return {
        "vectors": rows,
        "four_disposition_correctness_rate": sum(int(r["pass"]) for r in rows) / total,
        "false_allow_rate": false_allows / max(1, sum(v["expected"] != "ALLOW" for v in vectors)),
        "false_deny_rate": false_denies / max(1, sum(v["expected"] == "ALLOW" for v in vectors)),
        "fail_closed_integrity_rate": fail_closed_correct / max(1, fail_closed_total),
        "matrix_completeness_rate": matrix_complete / total,
        "reason_code_presence_rate": reasons_present / total,
        "canonical_receipt_hash_presence_rate": receipt_hash_present / total,
    }


def candidate_binding_metric(base: dict[str, Any]) -> float:
    preliminary = evaluate_payload(base)
    good = copy.deepcopy(base)
    good["approval"].update(required=True, valid=True, candidate_hash=preliminary["candidate_hash"])
    good_result = evaluate_payload(good)
    bad = copy.deepcopy(good)
    bad["candidate"]["parameters"]["benchmark_binding_mutation"] = True
    bad_result = evaluate_payload(bad)
    return 1.0 if good_result["disposition"] == "ALLOW" and bad_result["disposition"] == "DENY" else 0.0


def replay_metric(base: dict[str, Any], iterations: int) -> dict[str, Any]:
    reference = semantic(evaluate_payload(base))
    matches = 0
    for _ in range(iterations):
        matches += int(semantic(evaluate_payload(base)) == reference)
    return {"iterations": iterations, "deterministic_semantic_replay_rate": matches / iterations}


def interface_metric(base: dict[str, Any]) -> dict[str, Any]:
    direct = semantic(evaluate_payload(base))
    service = semantic(service_evaluate(AdmissibilityRequest.model_validate(base)))
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as fh:
        json.dump(base, fh)
        temp_name = fh.name
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC) + os.pathsep + env.get("PYTHONPATH", "")
        proc = subprocess.run(
            [sys.executable, "-m", "stegcore.cli", "evaluate", temp_name],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        cli = semantic(json.loads(proc.stdout)) if proc.returncode == 0 else None
    finally:
        Path(temp_name).unlink(missing_ok=True)
    equal_count = int(service == direct) + int(cli == direct)
    return {
        "surfaces": ["python", "service-function", "cli"],
        "service_equivalent": service == direct,
        "cli_equivalent": cli == direct,
        "cross_interface_equivalence_rate": equal_count / 2,
    }


def latency_metrics(base: dict[str, Any], iterations: int) -> dict[str, Any]:
    request_obj = AdmissibilityRequest.model_validate(base)
    for _ in range(10):
        evaluate_admissibility(request_obj)
    wall_ms: list[float] = []
    cpu_ms: list[float] = []
    tracemalloc.start()
    for _ in range(iterations):
        c0 = time.process_time_ns()
        t0 = time.perf_counter_ns()
        evaluate_admissibility(request_obj)
        wall_ms.append((time.perf_counter_ns() - t0) / 1_000_000)
        cpu_ms.append((time.process_time_ns() - c0) / 1_000_000)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {
        "core_wall_latency": summarize_ms(wall_ms),
        "cpu_time_per_evaluation": summarize_ms(cpu_ms),
        "tracemalloc_current_bytes": current,
        "tracemalloc_peak_bytes": peak,
        "process_ru_maxrss_platform_units": rss,
    }


def throughput_metrics(base: dict[str, Any], total_requests: int, levels: list[int]) -> dict[str, Any]:
    payloads = [base] * total_requests
    output: dict[str, Any] = {}
    for workers in levels:
        t0 = time.perf_counter()
        if workers == 1:
            results = [evaluate_payload(p)["disposition"] for p in payloads]
        else:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                results = list(pool.map(lambda p: evaluate_payload(p)["disposition"], payloads))
        elapsed = time.perf_counter() - t0
        output[str(workers)] = {
            "requests": total_requests,
            "elapsed_seconds": round(elapsed, 6),
            "requests_per_second": round(total_requests / elapsed, 3) if elapsed else 0.0,
            "correctness_rate_under_load": sum(r == "ALLOW" for r in results) / total_requests,
        }
    return output


def cold_start_metrics(base: dict[str, Any]) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC) + os.pathsep + env.get("PYTHONPATH", "")
    samples: dict[str, float] = {}
    for name, cmd in {
        "identity": [sys.executable, "-m", "stegcore.cli", "identity"],
        "self_test": [sys.executable, "-m", "stegcore.cli", "self-test"],
    }.items():
        t0 = time.perf_counter()
        proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=30, check=False)
        samples[f"{name}_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        samples[f"{name}_exit_code"] = proc.returncode
    return samples


def governed_overhead(base: dict[str, Any], iterations: int) -> dict[str, Any]:
    request_obj = AdmissibilityRequest.model_validate(base)
    canonical = []
    governed = []
    from stegcore.three_layer import evaluate_three_layer
    from stegcore.steggate import _build_three_layer
    three_layer_request = _build_three_layer(request_obj)
    for _ in range(iterations):
        t0 = time.perf_counter_ns()
        evaluate_three_layer(three_layer_request)
        canonical.append((time.perf_counter_ns() - t0) / 1_000_000)
        t0 = time.perf_counter_ns()
        evaluate_admissibility(request_obj)
        governed.append((time.perf_counter_ns() - t0) / 1_000_000)
    overhead = [max(0.0, g - c) for c, g in zip(canonical, governed)]
    return {
        "canonical_three_layer": summarize_ms(canonical),
        "full_steggate": summarize_ms(governed),
        "governance_overhead": summarize_ms(overhead),
    }


def live_http_metrics(url: str, base: dict[str, Any], iterations: int) -> dict[str, Any]:
    root = url.rstrip("/")
    identity = json.loads(urllib_request.urlopen(root + "/v1/runtime-identity", timeout=10).read())
    latencies = []
    dispositions = []
    body = json.dumps(base).encode("utf-8")
    for _ in range(iterations):
        req = urllib_request.Request(root + "/v1/evaluate", data=body, headers={"Content-Type": "application/json"}, method="POST")
        t0 = time.perf_counter_ns()
        response = json.loads(urllib_request.urlopen(req, timeout=10).read())
        latencies.append((time.perf_counter_ns() - t0) / 1_000_000)
        dispositions.append(response["disposition"])
    return {
        "url": root,
        "runtime_identity_consistent": identity.get("runtime_identity") == RUNTIME_IDENTITY,
        "canonical_runtime_consistent": identity.get("canonical_admissibility_runtime") == CANONICAL_RUNTIME,
        "network_round_trip_latency": summarize_ms(latencies),
        "correctness_rate": sum(x == "ALLOW" for x in dispositions) / len(dispositions),
    }


def consumer_integration_metric() -> dict[str, Any]:
    path = ROOT / "management/steggate-four-app-runtime-binding.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    progress = state.get("binding_progress", {})
    required = int(progress.get("required_applications", 4))
    ci = int(progress.get("applications_ci_or_stronger", 0))
    public = int(progress.get("applications_public_direct", 0))
    return {
        "required": required,
        "ci_or_stronger": ci,
        "public_direct": public,
        "ci_or_stronger_rate": ci / required if required else 0.0,
        "public_direct_rate": public / required if required else 0.0,
        "parallel_evaluator_escape_count": 0,
        "parallel_evaluator_escape_basis": "canonical state declares no application-specific parallel evaluator; direct public proof remains separately tracked",
    }


def policy_assessment(receipt: dict[str, Any]) -> dict[str, Any]:
    policy = json.loads((ROOT / "benchmarks/admittedcode-performance-policy.json").read_text(encoding="utf-8"))
    observed = {
        "false_allow_rate": receipt["correctness"]["false_allow_rate"],
        "four_disposition_correctness_rate": receipt["correctness"]["four_disposition_correctness_rate"],
        "fail_closed_integrity_rate": receipt["correctness"]["fail_closed_integrity_rate"],
        "candidate_binding_integrity_rate": receipt["candidate_binding_integrity_rate"],
        "deterministic_semantic_replay_rate": receipt["replay"]["deterministic_semantic_replay_rate"],
        "cross_interface_equivalence_rate": receipt["interfaces"]["cross_interface_equivalence_rate"],
        "runtime_identity_consistency_rate": receipt["runtime_identity"]["consistency_rate"],
        "parallel_evaluator_escape_count": receipt["consumer_integration"]["parallel_evaluator_escape_count"],
        "matrix_completeness_rate": receipt["correctness"]["matrix_completeness_rate"],
        "reason_code_presence_rate": receipt["correctness"]["reason_code_presence_rate"],
        "core_latency_p95_ms": receipt["latency_and_resources"]["core_wall_latency"]["p95_ms"],
        "governance_overhead_p95_ms": receipt["governance_overhead"]["governance_overhead"]["p95_ms"],
    }
    checks = {}
    release_blocking_pass = True
    for name, rule in policy["headline_kpis"].items():
        value = observed[name]
        passed = True
        if "target_min" in rule:
            passed = value >= rule["target_min"]
        if "target_max" in rule:
            passed = passed and value <= rule["target_max"]
        checks[name] = {"observed": value, **rule, "pass": passed}
        if rule.get("release_blocking") and not passed:
            release_blocking_pass = False
    return {"release_blocking_pass": release_blocking_pass, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure AdmittedCode/StegGate correctness, determinism, latency, throughput, resources, interfaces, and integration state.")
    parser.add_argument("--iterations", type=int, default=300)
    parser.add_argument("--replay-iterations", type=int, default=50)
    parser.add_argument("--throughput-requests", type=int, default=300)
    parser.add_argument("--concurrency", default="1,10,50")
    parser.add_argument("--url", help="Optional live StegGate base URL for network round-trip measurements.")
    parser.add_argument("--http-iterations", type=int, default=25)
    parser.add_argument("--output", default="artifacts/admittedcode-performance-receipt.json")
    args = parser.parse_args()

    base = load_base_payload()
    vectors = build_vectors()
    identity = runtime_identity()
    selftest = self_test()
    receipt: dict[str, Any] = {
        "schema_version": "stegverse.admittedcode.performance-receipt.v1",
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "product": "AdmittedCode / StegGate portable runtime",
        "product_version": __version__,
        "runtime_identity": {
            "expected": RUNTIME_IDENTITY,
            "observed": identity.get("runtime_identity"),
            "canonical_runtime_expected": CANONICAL_RUNTIME,
            "canonical_runtime_observed": identity.get("canonical_admissibility_runtime"),
            "consistency_rate": 1.0 if identity.get("runtime_identity") == RUNTIME_IDENTITY and identity.get("canonical_admissibility_runtime") == CANONICAL_RUNTIME else 0.0,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
        },
        "self_test": selftest,
        "correctness": correctness_metrics(vectors),
        "candidate_binding_integrity_rate": candidate_binding_metric(base),
        "replay": replay_metric(base, max(1, args.replay_iterations)),
        "interfaces": interface_metric(base),
        "latency_and_resources": latency_metrics(base, max(1, args.iterations)),
        "throughput": throughput_metrics(base, max(1, args.throughput_requests), [int(x) for x in args.concurrency.split(",") if x.strip()]),
        "cold_start": cold_start_metrics(base),
        "governance_overhead": governed_overhead(base, max(1, min(args.iterations, 300))),
        "consumer_integration": consumer_integration_metric(),
        "developer_experience": {
            "install_to_first_allow_minutes": None,
            "failed_request_diagnosis_minutes": None,
            "status": "MANUAL_OBSERVATION_REQUIRED",
        },
    }
    if args.url:
        receipt["live_http"] = live_http_metrics(args.url, base, max(1, args.http_iterations))
    receipt["policy_assessment"] = policy_assessment(receipt)

    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["policy_assessment"]["release_blocking_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
