# GADI StegCore Mirror Handoff

Status: `ACTIVE / THREAT_REASONING_MERGED / GOVERNANCE_PROFILE_MERGED / GOVERNANCE_INTR_ADMISSION_PRODUCER_MERGED / LOCAL_ADMISSION_MATERIALIZER_MERGED / PENDING_GOVERNANCE_CANDIDATE_MATERIALIZER_MERGED / EXTERNAL_EVIDENCE_FACT_PROJECTOR_MERGED / VERIFIED_EXTERNAL_EVIDENCE_BINDING_IN_VALIDATION / AUTHENTIC_RUNTIME_ADMISSION_UNOBSERVED`
Repository: `StegVerse-Labs/StegCore`
Canonical task: `GADI-001`
Parent handoff: `StegVerse-Labs/.github/docs/GADI_RESIDENT_EXECUTION_MIRROR_HANDOFF.md`
COSV: `10100000100000`
Current branch: `gadi-verified-external-evidence-binding-001`

## Purpose

StegCore owns GADI threat reasoning plus Governance evaluation/projection. It may correlate already-observed threat evidence, select the least-destructive eligible pre-authorized capability, emit a bounded PENDING defensive-intervention request, bind that exact request into the Governance candidate, evaluate it through the existing Universal Governance Connector/InTr path, and project the resulting Governance decision into the existing GADI `Admission` field. It does not observe threats, mint or verify external-evidence envelopes, mint credentials, create runtime bindings, claim/fence work, execute defensive effects, or become a parallel InTr/StegGate authority.

## Merged chain

- Governance PR #40 -> `2765854132872078bcd15a4432a65095831b432e`: authoritative `gadi.defensive-intervention.v1` profile.
- StegCore PR #202 -> `282f30e9e46efc3a8d0d867f48e08c3aa6534e22`: Governance-decision -> GADI Admission projector.
- StegCore PR #204 -> `44f4240c72ae1e64cefd829e469e64a40b5034a3`: local GADI InTr/Governance admission materializer.
- StegCore PR #205 -> `43f61a9feda8944a5551cfbc39b302f8c65ef69c`: PENDING request + hash-bound Governance candidate materializer.
- StegCore PR #206 -> `ed94d900c58c59e316a1591d27404cf372edaeb1`: external-evidence -> exact three-layer Governance facts projector. Exact head `b73a91bcb1a4eabe1a51fc898f33d3ddd5cbe898` passed both observed GADI workflow instances before merge.

## Verified external-evidence binding gap

Post-#206 audit found that `src/stegcore/external_evidence.py` structurally consumes envelope fields including `integrity.chain_valid`, `authorization.provider_authorized`, `authorization.scope_match`, and `freshness.is_current`. No repository-surfaced cryptographic/provider verifier was found. Governance's provider contract explicitly treats cryptographic validity and provider authorization as facts distinct from the evidence payload itself.

Therefore a GADI facts projector must not accept the envelope's self-declared verification posture as sufficient evidence.

## Independent verification binding — in validation

`scripts/materialize_gadi_governance_facts_from_external_evidence.py` now requires two independent local artifacts:

1. the external-evidence envelope;
2. a separate `stegcore.gadi-verified-external-evidence-binding/v1` artifact.

The binding must match the exact canonical envelope hash and the envelope's provider/key/content-digest/authorization identity, and must explicitly establish:

```text
signature_verified = true
chain_verified = true
provider_authorized = true
scope_match = true
freshness_verified = true
verification_receipt_ref = <non-empty>
verifier_authority_ref = <non-empty>
execution_authority_granted = false
authority_effect = NONE_EVIDENCE_VERIFICATION_ONLY
```

The projector also requires the envelope's own posture to remain consistent with those independently verified facts. A binding mismatch, missing verification, authority drift, or stale/unauthorized envelope fails closed before Governance facts are emitted.

The projector does not create the binding or perform cryptographic verification. It only requires and consumes the already-verified artifact, analogous to the existing separation between Governance payloads and `VerifiedTransportBindings` for InTr.

## GADI scope retained

The exact envelope candidate must still match:

```text
action = ADMIT_DEFENSIVE_INTERVENTION
target_ref = stegverse.gadi.defensive-intervention
scope = operation:admit-defensive-intervention
policy_ref = policy.gadi.defensive-intervention.v1
evidence_provider_execution_authority = false
```

Only then may the existing external-evidence mapping project:

```text
judgment_conditions
signal_admission
execution_boundary
```

Unfavorable but valid facts remain preserved and may later yield DENY/FAIL-CLOSED.

## Validation coverage

`tests/test_gadi_governance_facts_from_external_evidence.py` now verifies:

- envelope self-assertion alone is insufficient;
- exact envelope-hash binding is required;
- provider ID/public-key mismatch fails closed;
- signature, chain, provider authorization, scope, and freshness must each be independently verified;
- envelope and verified-binding posture must agree;
- neither envelope nor verification binding may grant execution authority;
- wrong GADI target/policy fails closed;
- valid reference-state drift still projects unfavorable facts without authority.

## Authentic evidence boundary

The source/runtime-adapter chain now requires an independent verified-evidence binding rather than trusting an envelope's own claims. The following remain unobserved on the actual sovereign resident runtime:

```text
CURRENT_GADI_EXTERNAL_EVIDENCE_ENVELOPE_NOT_OBSERVED
CURRENT_GADI_VERIFIED_EXTERNAL_EVIDENCE_BINDING_NOT_OBSERVED
CURRENT_GADI_THREAT_OBSERVATION_NOT_OBSERVED
CURRENT_GADI_RUNTIME_BINDING_NOT_OBSERVED
CURRENT_GADI_PENDING_INTERVENTION_REQUEST_NOT_OBSERVED
CURRENT_GADI_INTR_ADMISSION_NOT_OBSERVED
CURRENT_GADI_NATIVE_COMMAND_NOT_OBSERVED
CONTROLLED_PREAUTHORIZED_ACTUATOR_RESULT_NOT_OBSERVED
CURRENT_GADI_WORKERCOORDINATOR_CLAIM_FENCE_NOT_OBSERVED
CURRENT_GADI_RESIDENT_CONSUMPTION_NOT_OBSERVED
```

Source fixtures, CI, old host self-attest receipts, and controlled simulation do not satisfy those predicates. The retained host self-attest receipt lacks the provider key/signature/chain/freshness/subject/candidate primitives required by this verification boundary.

## Immediate continuation

1. Validate and merge this independent-binding hardening only on an exact fully green head.
2. Reconcile the parent `.github` GADI handoff after merge.
3. Audit existing sovereign/runtime attestation services for a real provider verifier capable of producing the binding; do not fabricate a verifier artifact from source fixtures.
4. When the authorized resident is reachable, require both the current GADI-scoped envelope and independently verified binding.
5. Project exact facts, then use merged #205 -> #204 -> StegOS command path.
6. Preserve parent readiness: no WorkerCoordinator claim until command, admission, runtime binding, and controlled-output observation are coherent.

## Release rule

This hardening is not GADI activation or release evidence. Release remains deferred until authentic resident execution, reassessment/termination, exact reconstruction, and parent activation predicates are observed.
