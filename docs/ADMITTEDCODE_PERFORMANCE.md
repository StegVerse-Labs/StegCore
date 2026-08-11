# AdmittedCode Performance and Benchmark Contract

Status: ACTIVE MEASUREMENT CONTRACT  
Owner: `StegVerse-Labs/StegCore`  
Canonical runtime identity: `stegverse:steggate:canonical:three-layer:v1`  
Canonical admissibility runtime: `stegcore.three_layer.evaluate_three_layer`

## Purpose

AdmittedCode performance is measured as correctness, fail-closed safety, deterministic semantics, interface equivalence, runtime cost, operational portability, and consumer integration. Raw speed never outranks correctness or governance integrity.

The canonical benchmark runner is:

```bash
python tools/run_admittedcode_benchmarks.py
```

It emits:

```text
artifacts/admittedcode-performance-receipt.json
```

The receipt schema identifier is `stegverse.admittedcode.performance-receipt.v1`.

## Release-blocking correctness measures

The policy in `benchmarks/admittedcode-performance-policy.json` makes these release blocking:

- false-ALLOW rate = 0;
- four-disposition correctness = 100%;
- FAIL_CLOSED integrity = 100%;
- candidate/approval binding integrity = 100%;
- deterministic semantic replay = 100%;
- Python/service/CLI semantic equivalence = 100%;
- canonical runtime identity consistency = 100%;
- known parallel-evaluator escapes = 0;
- predicate-matrix completeness = 100%;
- reason-code presence = 100%.

False DENY is measured separately. It is not treated as equivalent to false ALLOW because a false ALLOW crosses the governance boundary while a false DENY primarily harms availability/usability.

## Timing and resource measures

The benchmark records direct core evaluation latency as min, mean, p50, p95, p99, and max. CPU time per evaluation, Python traced memory peak, and process `ru_maxrss` are also retained.

Throughput is measured at bounded concurrency levels (default 1, 10, and 50 workers) and always reports correctness under load with requests/second. A faster result that changes dispositions is a failed benchmark.

Cold-start measurements record fresh CLI process time to canonical runtime identity and deterministic self-test.

## Governance overhead

The benchmark separately measures:

```text
canonical three-layer evaluator latency
full StegGate admissibility latency
difference = governance composition overhead
```

This is a local evaluator comparison, not provider/model execution latency. It makes the incremental cost of capability, continuity, approval, matrix, and result composition visible without conflating it with network or model-provider time.

## Network measurements

A live runtime can be measured without changing the local benchmark semantics:

```bash
python tools/run_admittedcode_benchmarks.py --url https://<steggate-host>
```

The live lane first verifies runtime identity, then records `/v1/evaluate` network round-trip latency and correctness. Transport latency remains separate from core evaluator latency because transport is not governance authority.

## Determinism rule

`decision_state_hash` contains `evaluated_at`, so it is intentionally time-specific and is not the semantic replay comparator.

Semantic replay requires equality of the material decision surface:

- disposition;
- candidate hash;
- reason codes;
- canonical three-layer decision and reason;
- canonical request and receipt hashes;
- permission/admissibility boundary fields;
- continuity/execution non-authority fields;
- complete predicate matrix semantics.

## Cross-interface equivalence

The benchmark sends the same candidate through:

1. direct Python `evaluate_admissibility`;
2. the service evaluation function used by `/v1/evaluate`;
3. the `steggate evaluate` CLI.

These must be semantically identical. Browser, SDK, API, or application consumers must preserve the same rule and must not implement a parallel admissibility engine.

## Developer-experience measures

Two human-observation fields are reserved in every receipt:

- install-to-first-ALLOW time, target <= 5 minutes;
- failed-request diagnosis time, target <= 15 minutes.

They remain `null` until measured by an actual unfamiliar operator. CI does not fabricate these numbers.

## Consumer portability measures

The receipt reads `management/steggate-four-app-runtime-binding.json` and records:

- required application count;
- CI-or-stronger binding count/rate;
- public-direct binding count/rate;
- known parallel-evaluator escape count.

The final target is 4/4 canonical integrations, 4/4 public-direct proofs, and zero parallel evaluators.

## Release use

The hosted workflow `.github/workflows/admittedcode-performance.yml` runs on relevant product changes and manual dispatch. It uploads the JSON receipt as immutable workflow evidence. Release candidates should compare the new receipt with the prior accepted baseline and investigate regressions even when a non-blocking latency guardrail still passes.

Performance numbers are environment-specific. Receipts therefore include Python version, platform, machine architecture, processor metadata, and CPU count. Never compare raw latency numbers across unlike environments without qualification.
