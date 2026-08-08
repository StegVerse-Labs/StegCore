# StegGate Live Service

## Purpose

`stegcore.service:app` exposes the reconciled canonical StegGate admissibility matrix as an HTTP service.

The service is a decision boundary, not an authority amplifier. It does not implement a second policy engine. Canonical core ALLOW/DENY/FAIL-CLOSED authority comes from `stegcore.three_layer.evaluate_three_layer`; `stegcore.steggate.evaluate_admissibility` normalizes the complete reconstructable matrix, composes existing capability/verified-continuity bindings, and adds candidate-hash-bound `REVIEW` when required human approval is absent.

`src/stegcore/decision.py` remains an intentionally minimal compatibility interface. Its minimal scope is not evidence that StegGate lacks the broader runtime.

## Endpoints

```text
GET  /
GET  /health
GET  /v1/capabilities
POST /v1/evaluate
GET  /v1/self-test
```

`POST /v1/evaluate` returns one of `ALLOW`, `DENY`, `REVIEW`, or `FAIL_CLOSED` and preserves the complete decision surface including candidate hash, material matrix predicates, canonical three-layer request/receipt hashes, reasons, evaluation time, and final decision-state hash.

## Governed consequence boundary

Evaluation and execution remain distinct. For a trusted in-process consequence integration, the full composition is:

```text
evaluate_three_layer
  -> evaluate_admissibility
  -> governed_steggate_execute
  -> coherence_gate
  -> injected mutation callback
```

`src/stegcore/steggate_runtime.py:governed_steggate_execute` makes the mutation callback unreachable for `DENY`, `REVIEW`, `FAIL_CLOSED`, commit-coherence denial, or missing commit authority. Only full StegGate `ALLOW` plus independent coherence `ALLOW` may invoke the callback, and the finalized coherence receipt binds the full StegGate `decision_state_hash`.

The public HTTP service intentionally does not expose arbitrary remote mutation. It mints no Continuity receipt and performs no external effect from `/v1/evaluate`.

## Canonical hosting

```text
provider: Render
service: steggate-core
service_id: srv-d9rlic2jobas73do1q6g
origin: https://steggate-core.onrender.com
repo: StegVerse-Labs/StegCore
branch: main
```

Render auto-deploy is connected, but the service is not live because the workspace has exhausted build-pipeline minutes. Current build failures occur before source build execution and are therefore hosting-capacity failures, not repository-test failures.

## Machine-owned live activation

The remaining hosted verification is repository-native:

```text
scripts/observe_steggate_live_service.py
tests/test_steggate_live_observer.py
.github/workflows/steggate-live-observer.yml
```

The observer runs hourly and on relevant pushes. A single activation cycle must verify:

1. `/health` -> `healthy` and `canonical_three_layer_bound=true`;
2. `/v1/self-test` -> exact ALLOW/DENY/REVIEW/FAIL_CLOSED PASS;
3. deterministic `POST /v1/evaluate` -> ALLOW with the required matrix predicates, candidate hash, canonical three-layer request hash, canonical three-layer receipt hash, decision-state hash, permission/admissibility separation, `continuity_receipt_minted=false`, and `external_execution_performed=false`.

The exact request and responses are retained in `build/steggate-live-observation.json` and uploaded as a workflow artifact. The workflow deliberately fails closed while any check is unavailable or incomplete.

Initial blocked observer evidence:

```text
run_id: 31270353764
job_id: 93135108552
health: TIMEOUTERROR
self_test: TIMEOUTERROR
artifact_id: 9025414196
artifact_digest: sha256:2708b4d4d99763903c85f03eba2402d0e6bf7e932c15979e95f7e339a70f2e5a
```

Full health+self-test+evaluate observer semantics were installed in commits `d4a9e4c7c64315bd50ccea4482c2d3a292c8d936` and `2d022fd04d5f2262affada5dea185bac30469f7c`.

## Repository validation

The full decision-to-coherence runtime integration passed StegCore Tests run `31270401058`, job `93135227329`: `148 passed, 127 subtests passed`. Diagnostics artifact `9025421552`, digest `sha256:4cce13a6ec682d09d9f84d3ca739f297bc942290112d2baedabeafe98cb27220`.

## Completion rule

Do not describe canonical StegGate as fully live merely because source tests pass or the Render service object exists. Functional activation requires a hosted observer receipt with `state=PASS` covering health, the four-outcome self-test, and the complete hosted matrix evaluation.
