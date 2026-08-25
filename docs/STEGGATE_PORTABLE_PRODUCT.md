# StegGate Portable Product

Status: current product boundary  
Product version: `0.3.0`  
Canonical owner: `StegVerse-Labs/StegCore`

## Purpose

StegGate is the portable product surface for StegCore commit-time admissibility. It gives a caller one stable operation: submit a structured commitment candidate and receive a governed disposition plus reconstruction evidence before any separately authorized consequential execution.

## Canonical operation

```text
AdmissibilityRequest
  -> stegcore.three_layer.evaluate_three_layer
  -> stegcore.steggate.evaluate_admissibility
  -> AdmissibilityEvaluation
```

When a route declares fresh standing as required, canonical execution additionally consumes the bound SDK/SPE/interlock standing context before commit coherence. Required standing that is missing, stale, DENY, tampered, or mismatched converts the canonical evaluation to `FAIL_CLOSED` before the bounded executor is reachable.

Supported dispositions:

```text
ALLOW
DENY
REVIEW
FAIL_CLOSED
```

Every supported interface must terminate in this same evaluation composition. No CLI, HTTP route, browser application, SDK, or consumer application may carry an independent policy/admissibility implementation and still claim canonical StegGate equivalence.

## Supported entry points

### Python

```python
from stegcore import AdmissibilityRequest, evaluate_admissibility
```

### CLI

```text
steggate identity
steggate self-test
steggate evaluate <request.json>
steggate serve [--host HOST] [--port PORT]
```

### HTTP

```text
GET  /health
GET  /v1/runtime-identity
GET  /v1/capabilities
GET  /v1/self-test
POST /v1/evaluate
```

The OpenAPI UI is exposed at `/docs` when the FastAPI service is running.

## Runtime identity

The canonical identity is independent of deployment location:

```text
contract_version: stegverse.steggate.runtime-identity.v1
runtime_identity: stegverse:steggate:canonical:three-layer:v1
canonical_owner: StegVerse-Labs/StegCore
canonical_admissibility_runtime: stegcore.three_layer.evaluate_three_layer
```

The following are transport or orchestration facts, not governance identity:

- URL or hostname;
- tunnel identifier;
- cloud/vendor account;
- heartbeat epoch;
- transport lease carrier;
- application name;
- UI route.

## Version identities

Do not collapse unrelated version domains.

`0.3.0` is the current **portable product/package/service** version and must agree across:

- `VERSION`;
- `pyproject.toml` project version;
- `src/stegcore/version.py`;
- runtime service version;
- current README/changelog product statements.

Other versions remain independent by design, including:

- schema versions embedded in historical or active JSON artifacts;
- receipt contract versions;
- runtime identity contract version;
- StegGate evaluation schema version;
- constitutional release/tag versions;
- review document versions such as Product Review v4/v5.

Historical evidence must not be rewritten merely to match the current product version.

## Result semantics

`ALLOW` means the proposed transition is admitted by the current governed evaluation. It is not evidence that execution happened.

`DENY` means current evidence/authority establishes a blocking condition.

`REVIEW` means the canonical runtime is otherwise admissible but an explicitly required review/approval boundary remains unresolved.

`FAIL_CLOSED` means required evidence, state integrity, binding, or authority cannot be established safely enough to rely on the proposed transition.

Each evaluation preserves:

- candidate hash;
- complete predicate matrix;
- reason codes;
- canonical three-layer request hash;
- canonical three-layer receipt hash;
- decision-state hash;
- explicit non-execution and non-continuity-minting posture.

For standing-required routes, the canonical consequence path also binds the expected package/transition/run/participant/interlock identity to the independently re-hashed SPE envelope, standing receipt, and SDK-to-StegGate bridge before commit coherence.

## Authority boundary

StegGate does not, by virtue of an evaluation:

- execute arbitrary external actions;
- mint Continuity receipts;
- establish identity truth;
- create custody;
- grant publication authority;
- grant provider authority;
- make transport availability authoritative;
- convert permission into admissibility;
- convert admissibility into proof of execution.

SPE standing remains non-authorizing; SDK/interlock continuity remains non-authorizing; Master Records custody remains non-authorizing. Only the canonical consequence composition may reach its bounded executor after both canonical admissibility and commit coherence permit it.

## Stranger-runnable verification

From a clean checkout with Python 3.11+:

```bash
python -m pip install -e .
steggate identity
steggate self-test
steggate evaluate examples/steggate_allow_request.json
```

Expected properties:

1. identity reports the canonical owner/runtime listed above;
2. self-test reports `PASS` and demonstrates all four dispositions;
3. the example request evaluates through the canonical runtime and returns `ALLOW` with matrix/hash evidence.

To observe a negative path without changing the implementation, copy the example and set `execution.policy_current` to `false`; the same interface should return `DENY`.

## Compatibility rule

A change is product-compatible when it preserves the supported request/response and runtime-identity contracts or introduces an explicitly versioned successor contract.

A change is not compatible if it silently:

- removes or renames a disposition;
- changes a binding field in runtime identity;
- makes transport identity authoritative;
- bypasses `evaluate_three_layer` for canonical decisions;
- creates a per-interface or per-application policy engine;
- reports execution or Continuity minting when those actions did not occur.

## Current integration posture

The portable core runtime and identity contract are implemented and CI validated. The 0.3.0 successor adds canonical standing/interlock binding before bounded consequence execution without changing the canonical runtime identity. Consumer integration evidence is tracked separately in:

```text
management/steggate-four-app-runtime-binding.json
```

Consumer completion proves that applications use the portable product correctly; it is not permission for consumers to redefine the core semantics.

## Current-state source order

For present operational state, read in this order:

1. `STEGCORE_MIRROR_HANDOFF.md`
2. `docs/STEGGATE_PORTABLE_PRODUCT.md`
3. `docs/STEGGATE_RUNTIME_IDENTITY_CONTRACT.md`
4. `management/steggate-four-app-runtime-binding.json`
5. live workflow/receipt evidence referenced by the handoff

Architecture/research documents such as Product Review v4/v5 remain valuable context but do not override the live runtime contracts unless their requirements are explicitly implemented and admitted by the canonical owner.
