# StegCore / StegGate

StegCore is the canonical StegVerse commit-time governance runtime. **StegGate** is its portable product surface for evaluating one proposed consequential transition before execution.

Current portable product version: **0.2.0**.

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
- `docs/STEGGATE_PORTABLE_PRODUCT.md` — supported portable product surface and compatibility rules.
- `docs/STEGGATE_RUNTIME_IDENTITY_CONTRACT.md` — transport-independent runtime identity contract.
- `docs/STEGGATE_PRODUCT_REVIEW_V4.md` — network-governance architecture that the live runtime follows.
- `docs/STEGGATE_PRODUCT_REVIEW_V5.md` — formalism/research expansion; **not** a replacement for live runtime contracts.
- `management/steggate-four-app-runtime-binding.json` — current cross-application integration state.

Historical receipts, review documents, activation artifacts, and schema-versioned files remain evidence of their own point in time. Their embedded versions must not be interpreted as the current package/service version unless they explicitly say so.

## Current product status

The canonical StegGate runtime, HTTP service, runtime identity contract, four-disposition self-test, and initial live activation are implemented. Current integration work is proving that named consumer applications traverse this same runtime rather than carrying per-application decision semantics. See `STEGCORE_MIRROR_HANDOFF.md` for the exact machine-owned state.

## Development verification

```bash
pytest -q
python scripts/verify_product_consistency.py
```

The consistency verifier fails when current package/service/CLI documentation drifts from the portable product version or canonical runtime identity.

## Legacy substrate

StegCore also contains earlier node-state, registry, orchestration, research, historical release, and ecosystem-management surfaces. They remain available for compatibility and provenance but are not the primary StegGate product entry point. Current product behavior is defined by the canonical files above.
