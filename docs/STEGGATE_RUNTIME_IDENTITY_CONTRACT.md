# StegGate Runtime Identity Contract

Status: **ACTIVE IMPLEMENTATION CONTRACT**  
Owner: `StegVerse-Labs/StegCore`  
Portable product version: `0.2.0`  
Integration goal: `StegVerse-Labs/StegCore#70`  
Parent product proof: `StegVerse-Labs/Site#239`

## Purpose

Consumers must prove that they traverse one canonical StegGate authority chain rather than application-specific parallel evaluators. Transport endpoints may change under heartbeat lease, tunnel reconstruction, or future stable-rendezvous work, so a host URL is not runtime identity.

The canonical transport-independent identity is exposed by:

```text
GET /v1/runtime-identity
```

Required application binding tuple:

```json
{
  "contract_version": "stegverse.steggate.runtime-identity.v1",
  "runtime_identity": "stegverse:steggate:canonical:three-layer:v1",
  "canonical_owner": "StegVerse-Labs/StegCore",
  "canonical_admissibility_runtime": "stegcore.three_layer.evaluate_three_layer"
}
```

`/v1/capabilities`, `/health`, `/v1/self-test`, CLI identity output, Python evaluation, and governed evaluation evidence must remain consistent with this tuple.

## Version-domain rule

The portable package/service version (`0.2.0`) and runtime identity contract version (`stegverse.steggate.runtime-identity.v1`) are intentionally different version domains.

- Product version changes track packaged software releases.
- Contract-version changes track compatibility of this binding tuple and its semantics.
- A product patch/minor release does not require a runtime-identity contract bump when the binding contract remains compatible.
- A breaking change to binding fields or semantics requires an explicitly versioned successor contract rather than silent drift.

See `docs/STEGGATE_PORTABLE_PRODUCT.md` for the current supported product surface.

## Authority rules

- Runtime identity is semantic identity, not transport identity.
- A heartbeat tunnel, stable rendezvous, Render host, proxy, browser route, CLI, or application adapter does not become StegGate policy authority by carrying requests.
- Application-specific adapters may supply candidate attributes, evidence, policy references, authority/delegation state, and action context; they may not mint a different canonical StegGate runtime identity.
- Canonical dispositions remain `ALLOW`, `DENY`, `REVIEW`, and `FAIL_CLOSED`.
- Permission remains distinct from admissibility.
- `ALLOW` is not evidence that execution occurred.
- The evaluation service does not expose arbitrary external execution authority and does not mint Continuity receipts.

## Consumer acceptance

For each reference application—Ecosystem Chat, VACC / VA Claims Chat, Math Solver, and HIL—direct retained evidence must establish:

1. the application fetched or otherwise consumed the canonical runtime identity tuple;
2. the governed request reached canonical StegGate evaluation semantics;
3. returned decision evidence carries the canonical decision/matrix identity expected by the application;
4. the application did not substitute a parallel evaluator when canonical identity or transport was unavailable;
5. public end-to-end execution evidence references the same canonical runtime identity.

Issue `StegVerse-Labs/StegCore#70` remains open until direct evidence exists for all four surfaces. Static files, schemas, unit tests, or this contract alone do not satisfy that issue.
