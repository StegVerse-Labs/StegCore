# StegCore / StegGate

StegCore is the canonical StegVerse commit-time governance runtime. **StegGate** is its portable product surface for evaluating one proposed consequential transition before execution.

Current portable product version: **0.3.0**.

## What it does

StegGate accepts a structured commitment candidate plus current judgment, signal/state, execution, capability, continuity, and approval evidence. It evaluates that request through the canonical StegCore admissibility chain and returns exactly one disposition:

```text
ALLOW | DENY | REVIEW | FAIL_CLOSED
```

The product boundary is intentionally narrow:

```text
candidate
  -> stegcore.three_layer.evaluate_three_layer
  -> stegcore.steggate.evaluate_admissibility
  -> disposition + reasons + complete predicate matrix + hashes
```

When a route declares fresh SPE standing as required, the canonical runtime additionally re-verifies the bound SDK/SPE/interlock evidence before consequence execution. Missing, stale, DENY, tampered, or mismatched required standing fails closed before commit coherence or executor invocation.

Interfaces may adapt input or presentation, but they must not implement a separate policy or admissibility engine.

StegCore does **not** mint continuity receipts, establish identity truth, grant provider authority, execute arbitrary external actions, publish content, or become durable evidence custody.

## Install

Python 3.11+ is required.

```bash
python -m pip install -e .
```

This installs the `steggate` CLI.

## Fastest verification

```bash
steggate identity
steggate self-test
```

`self-test` deterministically exercises ALLOW, DENY, REVIEW, and FAIL_CLOSED against the same canonical runtime used by the HTTP service.

## Evaluate a candidate

```bash
steggate evaluate examples/steggate_allow_request.json
```

The result contains the disposition, reason codes, candidate hash, canonical three-layer request/receipt hashes, decision-state hash, and complete predicate matrix.

## Run the HTTP service

```bash
steggate serve --host 127.0.0.1 --port 8000
```

Equivalent direct launch:

```bash
uvicorn stegcore.service:app --host 127.0.0.1 --port 8000
```

Canonical endpoints:

```text
GET  /health
GET  /v1/runtime-identity
GET  /v1/capabilities
GET  /v1/self-test
POST /v1/evaluate
GET  /docs
```

The runtime identity is transport-independent:

```text
stegverse:steggate:canonical:three-layer:v1
```

Canonical admissibility runtime:

```text
stegcore.three_layer.evaluate_three_layer
```

## AdmittedCode performance and regression evidence

The repository-owned benchmark path remains:

```bash
python tools/run_admittedcode_benchmarks.py
python tools/compare_admittedcode_baseline.py artifacts/admittedcode-performance-receipt.json
```

Performance observations, standing/interlock proof, package-version identity, and release metadata are evidence about the canonical product; none create a second evaluator or independently grant execution, credential, custody, or release authority.
