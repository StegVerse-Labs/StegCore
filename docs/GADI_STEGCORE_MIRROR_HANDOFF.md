# GADI StegCore Mirror Handoff

Status: `ACTIVE / THREAT_REASONING_MERGED / GOVERNANCE_PROFILE_UPSTREAM_MERGED / GOVERNANCE_INTR_ADMISSION_PRODUCER_IN_REVALIDATION / RUNTIME_ADMISSION_UNOBSERVED`
Repository: `StegVerse-Labs/StegCore`
Canonical task: `GADI-001`
Parent handoff: `StegVerse-Labs/.github/docs/GADI_RESIDENT_EXECUTION_MIRROR_HANDOFF.md`
COSV: `10100000100000`
Current branch: `gadi-intr-admission-producer-001`
Current PR: `StegVerse-Labs/StegCore#202`

## Purpose

StegCore owns GADI threat reasoning plus governance evaluation/projection. It may correlate threat evidence, propose a bounded defensive intervention request, evaluate that candidate through the existing Universal Governance Connector, and project the resulting governance decision into the existing GADI `Admission` field. It does not transport packets, mint credentials, create runtime bindings, execute defensive effects, or become a parallel InTr/StegGate authority.

## Existing merged reasoning surface

`src/stegcore/gadi.py` remains the canonical GADI reasoning implementation for canonical StegOS threat-observation/capability/intervention-request contracts, freshness and subject binding, uncertainty and semantic-integrity preservation, deterministic threat correlation, least-destructive-effective capability selection, and PENDING intervention requests with `model_output_authority=NONE`.

## Missing producer identified

The parent resident trajectory requires a current canonical GADI intervention admission with an exact `intr_decision_ref`. Inspection established that:

1. StegCore could emit only `PENDING` GADI intervention requests;
2. StegOS correctly requires canonical InTr admission plus a concrete runtime binding before native command materialization;
3. the existing Universal Governance Connector already returns hash-bound `ALLOW / DENY / FAIL-CLOSED` decisions while granting no execution authority;
4. no GADI-specific Governance profile or decision-to-`Admission` projection existed.

## Governance-owned profile — merged upstream

The first PR #202 exact head `787e4a1180dfccd31d00909a8991a6fcac24f8c2` passed local compile/connector tests but failed `Verify pinned Governance connector contract` with an exact snapshot blob mismatch. This was a correct custody failure: StegCore consumes a pinned Governance-owned contract and may not mutate that snapshot independently.

The authoritative registry was therefore updated first in `StegVerse-Labs/Governance` PR #40. Exact head `8bcd3f6586872c3c73d49242c9ec682319cedd14` passed all four observed Governance validation/smoke checks and squash-merged as:

`2765854132872078bcd15a4432a65095831b432e`

The merged Governance registry preserves its existing profiles and adds:

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

All profile/Interlock/InTr/carrier execution-authority grants remain false.

## StegCore pinned snapshot repair

PR #202 now refreshes the Governance snapshot from exact authoritative merge `2765854132872078bcd15a4432a65095831b432e` and exact registry blob:

`16c459103b1dfd580fa5ac4c2ad519728a1f9f17`

The snapshot manifest and `verify_universal_governance_connector_contract.py` are repinned to that Governance merge. Cross-repository byte-level custody remains enforced; the verifier was not weakened.

## GADI admission projector

`src/stegcore/gadi_intr_admission.py` binds an already-produced `GovernanceConnectorResult` to the exact PENDING `DefensiveInterventionRequest` using profile/operation/system/boundary identity, exact candidate reference, canonical request SHA-256, `execution_authority_granted=false`, `credential_authority=TV/TVC`, `authority_effect=NONE`, and no continuity-authority minting.

Projection semantics:

```text
ALLOW       -> ADMITTED + intr://governance-decision/<receipt_hash>
DENY        -> DENIED   + intr://governance-decision/<receipt_hash>
FAIL-CLOSED -> DENIED   + intr://governance-decision/<receipt_hash>
```

Any binding or authority mismatch fails closed. Already-projected non-PENDING requests cannot be reprojected.

The projection receipt explicitly records:

```text
runtime_binding_minted = false
execution_authority_granted = false
credential_authority = TV/TVC
authority_effect = NONE_ADMISSION_PROJECTION_ONLY
```

## Runtime-binding boundary

This repair intentionally does not create the GADI `runtime_binding_ref`. The parent runtime profile `runtime-node:gadi-resident-execution-001` is a profile declaration only and does not prove a concrete current resident runtime instance. The native StegOS command must continue to require an independently observed concrete runtime binding.

## Validation coverage

`tests/test_gadi_intr_admission.py` verifies authoritative profile resolution, reuse of `governance-external-action`, separate consequence authorization, ALLOW/ADMITTED and DENY/DENIED projection, exact request-hash binding, execution-authority drift rejection, and non-PENDING replay rejection.

## Evidence boundary

PR #202 and Governance PR #40 are source/contract evidence only. They do not prove a current governance traversal, current `ALLOW`, current GADI admission artifact, concrete runtime binding, native StegOS command, controlled actuator effect, WorkerCoordinator claim/fence, resident consumption, or activation.

## Immediate continuation

1. Revalidate PR #202 on the new exact head after the authoritative Governance repin and merge only if all applicable checks pass.
2. Reconcile the parent `.github` GADI handoff with Governance PR #40 and StegCore PR #202.
3. Inspect the existing resident/runtime-node surfaces for a concrete current GADI runtime-instance binding producer.
4. Only after an authentic governance decision plus concrete runtime binding exist may StegOS materialize the native GADI command.
5. Preserve the parent readiness gate: no targeted WorkerCoordinator claim until command, InTr admission, runtime binding, and controlled-output evidence are locally coherent.

## README impact

Existing README content already documents GADI reasoning and Universal Governance Connector authority separation. This remains an internal specialization of those existing boundaries; no README mutation is required.

## Release rule

This admission-producer repair is not GADI activation or release evidence. Release/tag propagation remains deferred until authentic resident execution, closed-loop reassessment/termination, Continuity/Master Records reconstruction, and parent activation predicates are satisfied.
