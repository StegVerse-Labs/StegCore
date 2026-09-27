#!/usr/bin/env python3
"""Synthetic SVG governance-cycle trace benchmark; NEVER an authority evaluator.

This measures deterministic trace bookkeeping on an interchangeable CPU.
It cannot establish real InTr execution or original Master Records custody.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import statistics
import time

STAGES = ("constraint", "observation", "admissibility", "consequence", "evidence", "next_constraint")
OUTCOMES = ("ALLOW", "DENY", "FAIL_CLOSED")


def evaluate_trace(trace: dict) -> dict:
    """Validate a *synthetic* trace; fail closed on missing, stale or broken lineage."""
    if not isinstance(trace, dict):
        return {"disposition": "FAIL_CLOSED", "reason": "INVALID_TRACE"}
    if trace.get("revoked"):
        return {"disposition": "DENY", "reason": "REVOKED"}
    if trace.get("stale_constraint"):
        return {"disposition": "DENY", "reason": "STALE_CONSTRAINT"}
    if trace.get("replay"):
        return {"disposition": "DENY", "reason": "REPLAY"}
    if any(stage not in trace for stage in STAGES):
        return {"disposition": "FAIL_CLOSED", "reason": "MISSING_STAGE"}
    if trace.get("interrupted") or trace.get("partial_recording"):
        return {"disposition": "FAIL_CLOSED", "reason": "INCOMPLETE_CYCLE"}
    decision = trace["admissibility"]
    if decision not in OUTCOMES:
        return {"disposition": "FAIL_CLOSED", "reason": "INVALID_DISPOSITION"}
    expected = hashlib.sha256(json.dumps(
        [trace[s] for s in STAGES[:-1]], sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    if trace["evidence"].get("synthetic_predecessor_hash") != expected:
        return {"disposition": "FAIL_CLOSED", "reason": "LINEAGE_MISMATCH"}
    if decision != "ALLOW" and trace["consequence"] != "PREVENTED":
        return {"disposition": "FAIL_CLOSED", "reason": "UNAUTHORIZED_CONSEQUENCE"}
    return {"disposition": decision, "reason": "SYNTHETIC_TRACE_CONSISTENT"}


def specimen(decision="ALLOW"):
    t = {"constraint": "policy-fixture-v1", "observation": "observation-fixture-v1",
         "admissibility": decision, "consequence": "SIMULATED" if decision == "ALLOW" else "PREVENTED",
         "evidence": {}, "next_constraint": "policy-fixture-v1"}
    # The digest binds stage values, excluding next_constraint; no custody is implied.
    t["evidence"]["synthetic_predecessor_hash"] = hashlib.sha256(json.dumps(
        [t[s] for s in STAGES[:-1]], sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    return t


def benchmark(iterations=1000):
    if iterations < 1:
        raise ValueError("iterations must be positive")
    samples = []
    t = specimen()
    for _ in range(iterations):
        start = time.perf_counter_ns()
        result = evaluate_trace(t)
        samples.append((time.perf_counter_ns() - start) / 1_000_000)
        if result["disposition"] != "ALLOW":
            raise AssertionError(result)
    ordered = sorted(samples)
    percentile = lambda p: ordered[min(len(ordered)-1, max(0, int((len(ordered)-1)*p)))]
    return {"schema": "stegverse.svg.synthetic-source-benchmark/v0.1",
            "evidence_class": "SYNTHETIC_SOURCE_ONLY", "runtime_authority": "NONE",
            "iterations": iterations, "p50_ms": percentile(.50), "p95_ms": percentile(.95),
            "p99_ms": percentile(.99), "mean_ms": statistics.mean(samples)}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--iterations", type=int, default=1000)
    print(json.dumps(benchmark(p.parse_args().iterations), indent=2))
