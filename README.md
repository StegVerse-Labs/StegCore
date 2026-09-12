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

For routes that declare fresh SPE standing as required, canonical execution also re-verifies the bound SDK/SPE/interlock evidence before commit coherence or consequence invocation. Missing, stale, DENY, tampered, or mismatched required standing fails closed before the bounded executor can run.

Execution-boundary predicates preserve the distinction between **unknown** and **affirmatively false**. An unestablished applicable predicate remains `UNKNOWN` and produces `FAIL_CLOSED / execution.probe_required` until evidence or a governed probe establishes it; it is never coerced into a stale/false finding. An explicitly observed `False` predicate still follows its applicable DENY rule. This preserves fail-closed governance without converting absence of evidence into evidence of invalidity.

Interfaces may adapt input or presentation, but they must not implement a separate policy or admissibility engine.

StegCore does **not** mint continuity receipts, establish identity truth, grant provider authority, execute arbitrary external actions, publish content, or become durable evidence custody.

## Present-tense runtime enforcement conversion

The active `PA-001-ECOSYSTEM-RUNTIME-ENFORCEMENT-001` workstream is converting the already validated permission/admissibility invariant into explicit commit-time runtime enforcement. The governing rule is that **authority and time are state variables**: consequence-bearing execution must be decided from the reconstructed commit-time state rather than presumed continuity of proposal-time approval.

The first conversion slice removes implicit authority approval from `GovernedRuntime`, binds current authority state plus the evaluation instant into the commit-state hash, preserves target binding in the receipt, and fails closed before executor invocation when authority state is absent. Source changes do not by themselves prove resident runtime activation or ecosystem-wide enforcement. Current coordination and evidence requirements are recorded in `docs/PA001_ECOSYSTEM_RUNTIME_ENFORCEMENT_MIRROR_HANDOFF.md`.

## GADI defensive reasoning surface

StegCore also contains the bounded reasoning surface for `GADI-001` (Governed Autonomous Defensive Intervention). This layer can correlate manifested external autonomous-system observations, preserve uncertainty and semantic qualifiers, classify threat state, compare declared defensive capabilities using least-destructive-effective semantics, and construct `DEFENSIVE_INTERVENTION_REQUEST` candidates.

This reasoning layer is **not execution authority and is not a parallel evaluator**. A threat assessment or intervention candidate cannot itself cause an external consequence. Every consequential defensive transition must still pass the canonical `stegcore.steggate.evaluate_admissibility` / InTr governance path and separately bind to a pre-authorized capability.

Semantic-integrity evidence is preserved as part of threat reasoning. Qualified statements such as `may`, `might`, `possible`, or `likely` must not silently become stronger assertions during correlation. Material semantic drift can contribute evidence to a threat assessment, but it never independently authorizes intervention.

Current bounded implementation and continuation state are recorded in `docs/GADI_STEGCORE_MIRROR_HANDOFF.md`.

## Install

Python 3.11+ is required.

The public PyPI distribution is **`stegverse-stegcore`** while the Python import/module namespace remains **`stegcore`**:

```bash
python -m pip install stegverse-stegcore
```

For editable development from a repository checkout:

```bash
python -m pip install -e .
```

Either installation exposes the `stegcore` Python API and the `steggate` CLI.

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

A host URL, tunnel, heartbeat, lease, UI, CLI, SDK, or application integration is never policy authority.

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

## Runtime authority chain

```text
Governance policy/evidence
  -> stegcore.three_layer.evaluate_three_layer
  -> stegcore.steggate.evaluate_admissibility
  -> ALLOW | DENY | REVIEW | FAIL_CLOSED
  -> governed execution boundary, when separately authorized
  -> observation / reconciliation
```

`ALLOW` is admissibility, not proof that execution occurred. `FAIL_CLOSED` applies when required authority or evidence cannot be established safely.

## Canonical documentation map

Read current-state documents before historical review material:

- `STEGCORE_MIRROR_HANDOFF.md` — live repository source of truth, active claims, validation, and continuation.
- `docs/PA001_ECOSYSTEM_RUNTIME_ENFORCEMENT_MIRROR_HANDOFF.md` — active conversion from the PA-001 semantic invariant to commit-time and ecosystem runtime enforcement.
- `docs/GADI_STEGCORE_MIRROR_HANDOFF.md` — bounded GADI threat-reasoning implementation and continuation.
- `docs/STEGCORE_UNKNOWN_PROBE_SEMANTICS_MIRROR_HANDOFF.md` — UNKNOWN-versus-false governance semantics and frozen-v0.4 longitudinal regression evidence.
- `docs/STEGGATE_PORTABLE_PRODUCT.md` — supported portable product surface and compatibility rules.
- `docs/STEGGATE_RUNTIME_IDENTITY_CONTRACT.md` — transport-independent runtime identity contract.
- `docs/ADMITTEDCODE_PERFORMANCE.md` — canonical performance, benchmark, and release-measurement contract.
- `docs/STEGGATE_PRODUCT_REVIEW_V4.md` — network-governance architecture that the live runtime follows.
- `docs/STEGGATE_PRODUCT_REVIEW_V5.md` — formalism/research expansion; **not** a replacement for live runtime contracts.
- `management/steggate-four-app-runtime-binding.json` — current cross-application integration state.

Historical receipts, review documents, activation artifacts, and schema-versioned files remain evidence of their own point in time. Their embedded versions must not be interpreted as the current package/service version unless they explicitly say so.

## Current product status

The canonical StegGate runtime, HTTP service, runtime identity contract, four-disposition self-test, initial live activation, portable-product consistency lane, AdmittedCode performance benchmark lane, standing/interlock fail-closed consequence binding, and UNKNOWN-preserving probe-required execution semantics are implemented. GADI threat reasoning is being integrated as a bounded proposal-generation surface that preserves the same authority boundary; it does not replace or bypass canonical admission. Current integration work is proving complete successor release/custody/POST_RETURN behavior through the same runtime rather than creating per-application decision semantics. The PA-001 ecosystem-enforcement conversion has started at source level by removing implicit approval for missing authority and binding authority/time/target into the commit-state evidence; resident and ecosystem-wide enforcement proof remain pending. See `STEGCORE_MIRROR_HANDOFF.md`, `docs/STEGCORE_UNKNOWN_PROBE_SEMANTICS_MIRROR_HANDOFF.md`, `docs/GADI_STEGCORE_MIRROR_HANDOFF.md`, and `docs/PA001_ECOSYSTEM_RUNTIME_ENFORCEMENT_MIRROR_HANDOFF.md` for exact machine-owned state.

## Development verification

```bash
pytest -q
python scripts/verify_product_consistency.py
python tools/run_admittedcode_benchmarks.py --iterations 25 --replay-iterations 10 --throughput-requests 50 --concurrency 1,5
```

The consistency verifier fails when current package/service/CLI documentation drifts from the portable product version or canonical runtime identity. The benchmark exits non-zero when a release-blocking performance invariant fails.

## Legacy substrate

StegCore also contains earlier node-state, registry, orchestration, research, historical release, and ecosystem-management surfaces. They remain available for compatibility and provenance but are not the primary StegGate product entry point. Current product behavior is defined by the canonical files above.
