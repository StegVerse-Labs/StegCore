# GADI StegCore Mirror Handoff

Status: `ACTIVE / THREAT_REASONING_MERGED / GOVERNANCE_INTR_ADMISSION_PRODUCER_IN_VALIDATION / RUNTIME_ADMISSION_UNOBSERVED`
Repository: `StegVerse-Labs/StegCore`
Canonical task: `GADI-001`
Parent handoff: `StegVerse-Labs/.github/docs/GADI_RESIDENT_EXECUTION_MIRROR_HANDOFF.md`
COSV: `10100000100000`
Current branch: `gadi-intr-admission-producer-001`
Current PR: `StegVerse-Labs/StegCore#202`

## Purpose

StegCore owns GADI threat reasoning plus governance evaluation/projection. It may correlate threat evidence, propose a bounded defensive intervention request, evaluate that candidate through the existing Universal Governance Connector, and project the resulting governance decision into the existing GADI `Admission` field. It does not transport packets, mint credentials, create runtime bindings, execute defensive effects, or become a parallel InTr/StegGate authority.

## Existing merged reasoning surface

`src/stegcore/gadi.py` remains the canonical GADI reasoning implementation for:

- canonical StegOS threat-observation/capability/intervention-request contracts;
- freshness, subject binding, uncertainty, and semantic-integrity preservation;
- deterministic threat correlation;
- least-destructive-effective capability selection;
- PENDING defensive intervention requests;
- explicit `model_output_authority=NONE` and admission-before-actuation semantics.

The existing reasoning source remains source-valid only. It does not prove a current InTr decision or runtime execution.

## Missing producer identified

The parent resident trajectory established that the GADI resident bundle requires a current canonical intervention admission with an exact `intr_decision_ref`. Repository inspection found:

1. `StegCore/src/stegcore/gadi.py` could emit only `PENDING` admission requests;
2. `StegOS/stegos/gadi_native_defense.py` correctly required an already-observed canonical InTr admission plus concrete runtime binding before materializing a native command;
3. the Universal InTr connector registry already contained `governance-external-action`, but no GADI-specific governance profile existed;
4. the existing Universal Governance Connector already returned hash-bound `ALLOW / DENY / FAIL-CLOSED` decisions while explicitly granting no execution authority;
5. no source path projected that canonical decision into the GADI `Admission(state, intr_decision_ref)` contract.

That missing decision-to-admission projection is the scope of PR #202.

## Current repair

### GADI governance profile

`contracts/universal_governance_connector_snapshot/universal-governance-connector-profiles.v1.json` now contains:

```text
profile_id = gadi.defensive-intervention.v1
system_id = stegverse.gadi.defensive-intervention
boundary_id = interlock:gadi.defensive-intervention
intr_profile_ref = governance-external-action
governed_transition_profile_ref = gadi.defensive-transition.v1
carrier_profile_ref = heartbeat-derived-intr.v1
operation_id = admit-defensive-intervention
action_class = ADMIT_DEFENSIVE_INTERVENTION
policy_ref = policy.gadi.defensive-intervention.v1
protected_consequence = true
bypass_disposition = FAIL_CLOSED
execution_requires_separate_authority = true
credential_authority = TV/TVC
```

The profile reuses the existing Universal InTr transport and existing three-layer governance evaluator. It does not introduce a new transport, evaluator, heartbeat, credential route, or execution authority.

### GADI admission projector

`src/stegcore/gadi_intr_admission.py` binds an already-produced `GovernanceConnectorResult` to the exact PENDING `DefensiveInterventionRequest` using:

- GADI profile / operation / system / boundary identity;
- exact candidate reference `gadi-request:<request_id>`;
- SHA-256 of the canonical request payload;
- `execution_authority_granted=false`;
- `credential_authority=TV/TVC`;
- `authority_effect=NONE`;
- no continuity-authority minting.

Projection semantics:

```text
ALLOW       -> ADMITTED + intr://governance-decision/<receipt_hash>
DENY        -> DENIED   + intr://governance-decision/<receipt_hash>
FAIL-CLOSED -> DENIED   + intr://governance-decision/<receipt_hash>
```

Any request binding or authority mismatch fails closed. An already-projected non-PENDING request cannot be projected again.

The accompanying projection receipt explicitly records:

```text
runtime_binding_minted = false
execution_authority_granted = false
credential_authority = TV/TVC
authority_effect = NONE_ADMISSION_PROJECTION_ONLY
```

## Runtime-binding boundary

This repair intentionally does **not** create the GADI `runtime_binding_ref`. The parent runtime profile `runtime-node:gadi-resident-execution-001` is only a source/profile declaration and does not itself prove a concrete runtime instance. The native StegOS command must continue to require an independently observed concrete runtime binding before resident execution becomes eligible.

## Validation coverage

`tests/test_gadi_intr_admission.py` verifies:

- canonical registry resolution of the narrow GADI governance profile;
- reuse of `governance-external-action` transport;
- separate consequence authorization remains required;
- ALLOW projects only GADI admission, not execution authority;
- DENY projects deterministic DENIED admission;
- exact candidate hash mismatch fails closed;
- execution-authority drift fails closed;
- non-PENDING requests cannot be reprojected.

## Evidence boundary

PR #202 is source/contract work only. It does not prove:

- a current threat observation;
- a current governance request traversal;
- a current Universal InTr transport receipt chain;
- a current `ALLOW` decision;
- a current GADI admission artifact;
- a concrete resident runtime binding;
- a native StegOS command;
- a controlled actuator effect;
- WorkerCoordinator claim/fence;
- resident consumption;
- GADI activation.

## Immediate continuation

1. Validate PR #202 on its exact head and merge only if all applicable checks pass.
2. Reconcile the parent `.github` GADI handoff with the merged admission producer.
3. Inspect the canonical resident/runtime-node surface for the concrete GADI runtime-instance binding producer.
4. Only after an authentic governance decision plus concrete runtime binding exist should StegOS materialize the native GADI command.
5. Preserve the parent readiness gate: no targeted WorkerCoordinator claim until current command, InTr admission, runtime binding, and controlled-output evidence are locally coherent.

## README impact

The existing README already documents the GADI reasoning boundary and Universal Governance Connector authority separation. This change specializes an existing internal governance path and adds no new operator-facing interface, so no README mutation is required.

## Release rule

This admission-producer repair is not GADI activation or release evidence. Release/tag propagation remains deferred until authentic resident execution, closed-loop reassessment/termination, Continuity/Master Records reconstruction, and parent activation predicates are satisfied.
