# GADI StegCore Mirror Handoff

Status: `ACTIVE / THREAT_REASONING_MERGED / GOVERNANCE_PROFILE_MERGED / GOVERNANCE_INTR_ADMISSION_PRODUCER_MERGED / LOCAL_ADMISSION_MATERIALIZER_MERGED / PENDING_GOVERNANCE_CANDIDATE_MATERIALIZER_IN_VALIDATION / AUTHENTIC_RUNTIME_ADMISSION_UNOBSERVED`
Repository: `StegVerse-Labs/StegCore`
Canonical task: `GADI-001`
Parent handoff: `StegVerse-Labs/.github/docs/GADI_RESIDENT_EXECUTION_MIRROR_HANDOFF.md`
COSV: `10100000100000`
Current branch: `gadi-pending-governance-candidate-materializer-001`

## Purpose

StegCore owns GADI threat reasoning plus Governance evaluation/projection. It may correlate already-observed threat evidence, select the least-destructive eligible pre-authorized capability, emit a bounded PENDING defensive-intervention request, bind that exact request into the Governance candidate, evaluate it through the existing Universal Governance Connector/InTr path, and project the result into the existing GADI `Admission` field. It does not observe threats, resolve Governance facts, mint credentials, create runtime bindings, claim/fence work, execute defensive effects, or become a parallel InTr/StegGate authority.

## Merged chain

- Governance PR #40 -> `2765854132872078bcd15a4432a65095831b432e`: authoritative `gadi.defensive-intervention.v1` profile.
- StegCore PR #202 -> `282f30e9e46efc3a8d0d867f48e08c3aa6534e22`: exact Governance-decision -> GADI Admission projector.
- StegCore PR #204 -> `44f4240c72ae1e64cefd829e469e64a40b5034a3`: local GADI `governance-external-action` InTr/Governance admission materializer. Repaired exact head `661a1e9736db4262c91c8246068ed6061217eae8` passed both observed task-specific workflow instances before merge.

Projection remains:

```text
ALLOW       -> ADMITTED + intr://governance-decision/<receipt_hash>
DENY        -> DENIED
FAIL-CLOSED -> DENIED
```

No runtime binding, credential, claim/fence, or execution authority is minted.

## Newly identified pre-admission production gap

Repository audit after #204 found that all three canonical pre-admission reasoning functions in `src/stegcore/gadi.py` remained library-only in production:

```text
correlate_threat()
choose_least_destructive_effective_capability()
build_intervention_request()
```

Their only callers were tests. Therefore an authentic current threat observation and authentic local capability evidence could not yet be transformed into the canonical PENDING intervention request expected by the merged local admission materializer without custom Python glue.

## Pending Governance candidate materializer — in validation

New entrypoint:

`scripts/materialize_gadi_pending_governance_candidate.py`

It consumes only already-local inputs:

1. one or more canonical `stegos.autonomous_threat_observation.v1` objects;
2. one or more canonical `stegos.governed_intervention_capability.v1` objects;
3. an already-resolved Governance facts object containing exactly `judgment_conditions`, `signal_admission`, and `execution_boundary`;
4. the pinned authoritative Governance registry.

The adapter reuses the existing GADI functions to:

```text
current observations
-> correlate_threat()
-> choose_least_destructive_effective_capability()
-> build_intervention_request() [PENDING]
-> exact canonical request SHA-256
-> hash-bound gadi.defensive-intervention.v1 Governance request
```

It does not create the observations or resolved Governance facts. It validates the resolved-facts structure and requires the exact authoritative GADI policy reference before candidate emission.

The emitted Governance request contains only the canonical payload fields; it does not self-assert InTr transport bindings. Those remain the responsibility of the already-merged local admission materializer.

The adapter explicitly records:

```text
threat_observation_created = false
resolved_governance_facts_created = false
intr_transport_performed = false
admission_created = false
runtime_binding_created = false
credential_minted = false
claim_or_fence_minted = false
execution_authority_granted = false
network_fetch_performed = false
credential_authority = TV/TVC
authority_effect = NONE_PENDING_REQUEST_AND_CANDIDATE_ONLY
```

CLI mode atomically writes the PENDING request, Governance request, and materialization receipt and hashes the exact observations, capabilities, resolved-facts, and pinned Governance-registry source bytes.

## Validation coverage

`tests/test_gadi_pending_governance_candidate_materializer.py` verifies:

- fresh bound imminent-harm observations can produce an intervention-eligible assessment;
- authoritative simulation-only safe-state capability is selected in simulation mode;
- the request remains exactly PENDING with no InTr reference;
- the Governance candidate hash equals the canonical exact PENDING request hash;
- material uncertainty blocks intervention materialization;
- expired capabilities are rejected;
- simulation-only capability cannot be promoted to production;
- Governance policy mismatch fails closed;
- incomplete resolved-facts objects are rejected;
- observation/fact/admission/runtime/claim/execution authority remains uncreated.

The dedicated GADI workflow explicitly tests and compiles the new materializer.

## Authentic evidence boundary

All work in this handoff remains source/runtime-adapter evidence only. The following still require actual sovereign-runtime observation:

```text
CURRENT_GADI_THREAT_OBSERVATION_NOT_OBSERVED
CURRENT_GADI_RESOLVED_GOVERNANCE_FACTS_NOT_OBSERVED
CURRENT_GADI_PENDING_INTERVENTION_REQUEST_NOT_OBSERVED
CURRENT_GADI_INTR_ADMISSION_NOT_OBSERVED
CURRENT_GADI_RUNTIME_BINDING_NOT_OBSERVED
CURRENT_GADI_NATIVE_COMMAND_NOT_OBSERVED
CONTROLLED_PREAUTHORIZED_ACTUATOR_RESULT_NOT_OBSERVED
CURRENT_GADI_WORKERCOORDINATOR_CLAIM_FENCE_NOT_OBSERVED
CURRENT_GADI_RESIDENT_CONSUMPTION_NOT_OBSERVED
```

Source fixtures, CI, controlled simulation, and merged adapters do not satisfy those predicates.

## Immediate continuation

1. Validate this branch on its exact head and merge only when every applicable GADI check is green.
2. Reconcile the parent `.github` handoff with StegOS PR #344 plus this materializer after merge.
3. When the authorized resident runtime is reachable, provide actual current threat observations and current resolved Governance facts; do not synthesize them from source fixtures.
4. Run this materializer to emit the exact PENDING request + hash-bound Governance candidate.
5. Run merged `materialize_gadi_local_admission.py` to obtain the current ADMITTED/DENIED projection through actual local InTr transport.
6. Combine an ADMITTED request with the independently observed runtime binding and merged StegOS command CLI.
7. Preserve parent readiness: no WorkerCoordinator claim until command, admission, runtime binding, and controlled-output observation are coherent.

## README impact

No root README mutation is required. This is a task-specific local artifact adapter over already documented GADI reasoning and Universal Governance authority boundaries.

## Release rule

This materializer is not GADI activation or release evidence. Release remains deferred until authentic resident execution, reassessment/termination, exact reconstruction, and parent activation predicates are observed.
