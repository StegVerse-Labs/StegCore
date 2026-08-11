# AdmittedCode Performance and Benchmark Contract

Status: ACTIVE MEASUREMENT CONTRACT  
Owner: `StegVerse-Labs/StegCore`  
Canonical runtime identity: `stegverse:steggate:canonical:three-layer:v1`  
Canonical admissibility runtime: `stegcore.three_layer.evaluate_three_layer`

## Purpose

AdmittedCode performance is measured as correctness, fail-closed safety, deterministic semantics, interface equivalence, runtime cost, operational portability, consumer integration, and newcomer usability. Raw speed never outranks correctness or governance integrity.

The canonical benchmark runner is:

```bash
python tools/run_admittedcode_benchmarks.py
```

It emits `artifacts/admittedcode-performance-receipt.json` using schema `stegverse.admittedcode.performance-receipt.v1`.

## Release-blocking correctness measures

`benchmarks/admittedcode-performance-policy.json` makes these release blocking:

- false-ALLOW rate = 0;
- four-disposition correctness = 100%;
- FAIL_CLOSED integrity = 100%;
- candidate/approval binding integrity = 100%;
- deterministic stable-semantic replay = 100%;
- Python/service/CLI semantic equivalence = 100%;
- canonical runtime identity consistency = 100%;
- known parallel-evaluator escapes = 0;
- predicate-matrix completeness = 100%;
- reason-code presence = 100%.

False DENY is measured separately. A false ALLOW crosses the governance boundary; a false DENY primarily harms availability/usability.

## Timing, resources, and throughput

The benchmark records direct core evaluation latency as min, mean, p50, p95, p99, and max, plus CPU time/evaluation, Python traced memory, and process max-RSS observation. Throughput is measured at bounded concurrency levels 1, 10, and 50 with correctness under load. Cold-start measurements record fresh CLI process time to runtime identity and self-test.

## Governance overhead

The benchmark separately measures canonical three-layer evaluator latency and full StegGate admissibility latency. Their difference is the incremental governance-composition overhead for capability, continuity, approval, matrix, and result composition. It is not model/provider latency.

## Hosted HTTP measurement

The hosted performance workflow starts the packaged HTTP service on `127.0.0.1:8000`, verifies `/health` and `/v1/runtime-identity`, and runs the benchmark with:

```bash
python tools/run_admittedcode_benchmarks.py --url http://127.0.0.1:8000
```

The resulting `live_http` section records HTTP round-trip p50/p95/p99/max latency, runtime identity consistency, canonical-runtime consistency, and response correctness. This proves the packaged HTTP path without claiming public-Internet transport performance.

When a currently selected public transport endpoint exists, the same runner may be pointed at that endpoint. Historical tunnel URLs are evidence, not current endpoints, and must not be reused as if they were live.

## Determinism rule

`decision_state_hash` and the canonical three-layer receipt hash are time-bound provenance. They are required to exist but are not required to repeat across independent evaluations.

Stable semantic replay compares disposition, candidate hash, reason codes, canonical three-layer decision/reason, canonical request hash, permission/admissibility boundary fields, continuity/execution non-authority fields, and complete predicate-matrix semantics. Receipt-hash presence is measured separately.

## Cross-interface equivalence

The same candidate is evaluated through direct Python `evaluate_admissibility`, the service evaluation function used by `/v1/evaluate`, and `steggate evaluate`. Those surfaces must be semantically identical on the stable material decision surface. Browser, SDK, API, and application consumers must preserve the same rule and must not implement a parallel evaluator.

## Provisional hosted regression baseline

The accepted initial baseline is:

```text
benchmarks/admittedcode-baseline-v0.2.0.json
```

It is grounded in two successful comparable hosted receipts:

```text
run 31507071754 / artifact 9107472044
run 31507106362 / artifact 9107494384
```

Observed initial hosted envelope:

```text
core p95 latency:               0.773312 .. 1.129262 ms
governance-overhead p95:        0.131866 .. 0.225686 ms
throughput concurrency 1:       2948.276 .. 4752.710 req/s
throughput concurrency 10:      2826.126 .. 4615.006 req/s
throughput concurrency 50:      2692.303 .. 4467.080 req/s
identity cold start:            254.511 .. 394.152 ms
self-test cold start:           254.632 .. 381.578 ms
```

Because two hosted samples are too few for a hard performance SLO, the baseline establishes provisional warning bands rather than release-blocking timing thresholds. `tools/compare_admittedcode_baseline.py` writes a versioned regression report. Timing/throughput bands may only be promoted toward release-blocking status after at least 10 comparable successful receipts across at least 3 distinct commits or release candidates. Correctness/security gates remain release blocking throughout.

## Newcomer / developer experience

The automated mechanical rehearsal is:

```bash
python tools/run_admittedcode_onboarding_rehearsal.py
```

It creates a fresh virtual environment, installs the local package, resolves runtime identity, obtains a first ALLOW, induces a stale-policy DENY, and confirms reason evidence. This measures packaging mechanics, not human comprehension.

Actual unfamiliar-human measures remain separate:

- install-to-first-ALLOW target <= 5 minutes;
- deliberate-failure diagnosis target <= 15 minutes.

Use `benchmarks/admittedcode-stranger-observation-template.json`. Those fields remain null until an actual unfamiliar operator performs the exercise. CI and automated rehearsal timings must never be substituted for human usability data.

## Consumer portability measures

The benchmark reads `management/steggate-four-app-runtime-binding.json` and records required application count, CI-or-stronger binding count/rate, public-direct binding count/rate, and known parallel-evaluator escape count. Final target: 4/4 canonical integrations, 4/4 public-direct proofs, zero parallel evaluators.

## Release use

`.github/workflows/admittedcode-performance.yml` produces the benchmark receipt, localhost HTTP evidence, baseline regression report, and automated onboarding rehearsal as retained workflow artifacts. `.github/workflows/release-bump.yml` runs the same correctness/performance and compatible-baseline comparison before opening a release PR.

Regression warnings are visible even while provisional timing bands are non-blocking. An incompatible canonical runtime identity is not treated as a performance regression; it requires an explicitly versioned successor baseline/contract review.

Performance numbers are environment-specific. Receipts include Python version, platform, machine architecture, processor metadata, and CPU count. Never compare raw latency numbers across unlike environments without qualification.
