# StegCore / StegGate

StegCore is the canonical StegVerse commit-time governance runtime. **StegGate** is its portable product surface for evaluating one proposed consequential transition before execution.

Current portable product version: **0.3.0**.

## Governance coordinate

StegCore evaluates consequential transitions at the canonical governance coordinate:

```text
Governance = Authority × Time
G = (Authority, Time)
```

Authority and Time are the coordinates of governance. Judgment, signal/state, policy, delegation, evidence, capability, continuity, approval, recoverability, and transition geometry are evaluated at that coordinate; they do not replace either coordinate.

Temporal non-causality remains explicit:

```text
Time != Authority
Delta-time -/-> Delta-authority
wall-clock observation != Authority
heartbeat cadence != Authority
```

These statements do not remove Time from governance. Time locates the governance evaluation; clocks, timestamps, freshness, expiry, duration, heartbeat cadence, and other temporal observations do not manufacture Authority.

See `docs/AUTHORITY_TIME_GOVERNANCE_COORDINATE.md` and `MANIFOLD_GOVERNANCE_MIRROR_HANDOFF.md`.

## What it does

StegGate accepts a structured commitment candidate plus current judgment, signal/state, execution, capability, continuity, and approval evidence. It evaluates that request through the canonical StegCore admissibility chain at the applicable Authority × Time coordinate and returns exactly one disposition:

```text
ALLOW | DENY | REVIEW | FAIL_CLOSED
```

The product boundary is intentionally narrow:

```text
candidate
  + applicable (Authority, Time)
  + evaluated context
  -> stegcore.three_layer.evaluate_three_layer
  -> stegcore.steggate.evaluate_admissibility
  -> disposition + reasons + complete predicate matrix + hashes
```

For routes that declare fresh SPE standing as required, canonical execution also re-verifies the bound SDK/SPE/interlock evidence before commit coherence or consequence invocation. Missing, stale, DENY, tampered, or mismatched required standing fails closed before the bounded executor can run.

Interfaces may adapt input or presentation, but they must not implement a separate policy, admissibility engine, or governance-coordinate system.

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
contract_version: stegverse.steggate.runtime-identity.v1
runtime_identity: stegverse:steggate:canonical:three-layer:v1
canonical_owner: StegVerse-Labs/StegCore
canonical_admissibility_runtime: stegcore.three_layer.evaluate_three_layer
```

A host URL, tunnel, heartbeat, lease, UI, CLI, SDK, or application integration is never Authority merely because it exists or is reachable.

## Python API

```python
from stegcore import AdmissibilityRequest, evaluate_admissibility

request = AdmissibilityRequest.model_validate(payload)
result = evaluate_admissibility(request)
print(result.disposition)
```

The Python API, CLI, and HTTP service all terminate in the same canonical evaluation composition.

## Performance and benchmark tracking

Run the canonical AdmittedCode benchmark suite with:

```bash
python tools/run_admittedcode_benchmarks.py
```

It emits `artifacts/admittedcode-performance-receipt.json` and measures correctness, false-ALLOW/false-DENY behavior, FAIL_CLOSED integrity, candidate binding, deterministic semantic replay, cross-interface equivalence, p50/p95/p99 latency, throughput under bounded concurrency, CPU/memory observations, cold start, governance overhead, runtime identity consistency, and four-application integration progress.

A live deployment can be measured separately with:

```bash
python tools/run_admittedcode_benchmarks.py --url https://<steggate-host>
```

Release-blocking benchmark policy is in `benchmarks/admittedcode-performance-policy.json`. False ALLOW, disposition correctness, FAIL_CLOSED integrity, candidate binding, semantic replay, interface equivalence, runtime identity, matrix/reason completeness, and parallel-evaluator escape checks are fail-closed release measures. Hosted receipts are produced by `.github/workflows/admittedcode-performance.yml`.

See `docs/ADMITTEDCODE_PERFORMANCE.md` for the measurement contract and interpretation rules.

## Runtime governance chain

```text
Governance coordinate: (Authority, Time)
  + policy/evidence/state/context
  -> stegcore.three_layer.evaluate_three_layer
  -> stegcore.steggate.evaluate_admissibility
  -> ALLOW | DENY | REVIEW | FAIL_CLOSED
  -> governed execution boundary, when separately admissible at that coordinate
  -> observation / reconciliation
```

`ALLOW` is an admissibility disposition, not proof that execution occurred and not a newly manufactured Authority coordinate. `FAIL_CLOSED` applies when required Authority basis or evidence cannot be established safely for the applicable coordinate.

## Canonical documentation map

Read current-state documents before historical review material:

- `STEGCORE_MIRROR_HANDOFF.md` — live repository source of truth, active claims, validation, and continuation.
- `docs/AUTHORITY_TIME_GOVERNANCE_COORDINATE.md` — canonical runtime binding to Authority × Time.
- `MANIFOLD_GOVERNANCE_MIRROR_HANDOFF.md` — manifold runtime semantics and Authority × Time correction state.
- `docs/STEGGATE_PORTABLE_PRODUCT.md` — supported portable product surface and compatibility rules.
- `docs/STEGGATE_RUNTIME_IDENTITY_CONTRACT.md` — transport-independent runtime identity contract.
- `docs/ADMITTEDCODE_PERFORMANCE.md` — canonical performance, benchmark, and release-measurement contract.
- `docs/STEGGATE_PRODUCT_REVIEW_V4.md` — network-governance architecture that the live runtime follows.
- `docs/STEGGATE_PRODUCT_REVIEW_V5.md` — formalism/research expansion; **not** a replacement for live runtime contracts.
- `management/steggate-four-app-runtime-binding.json` — current cross-application integration state.

Historical receipts, review documents, activation artifacts, and schema-versioned files remain evidence of their own point in time. Their embedded versions must not be interpreted as the current package/service version unless they explicitly say so.

## Current product status

The canonical StegGate runtime, HTTP service, runtime identity contract, four-disposition self-test, initial live activation, portable-product consistency lane, AdmittedCode performance benchmark lane, and standing/interlock fail-closed consequence binding are implemented. The Authority × Time semantic correction is implemented on its dedicated correction branch and exact-head manifold production validation has passed; merge/release remains separately gated. Current integration work is proving complete successor release/custody/POST_RETURN behavior through the same runtime rather than creating per-application decision semantics. See `STEGCORE_MIRROR_HANDOFF.md` for exact machine-owned state.

## Development verification

```bash
pytest -q
python scripts/verify_product_consistency.py
python tools/run_admittedcode_benchmarks.py --iterations 25 --replay-iterations 10 --throughput-requests 50 --concurrency 1,5
```
