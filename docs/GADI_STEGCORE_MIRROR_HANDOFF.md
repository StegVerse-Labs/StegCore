# GADI StegCore Mirror Handoff

Status: `ACTIVE / THREAT_REASONING_MERGED / GOVERNANCE_PROFILE_MERGED / GOVERNANCE_INTR_ADMISSION_PRODUCER_MERGED / LOCAL_ADMISSION_MATERIALIZER_MERGED / PENDING_GOVERNANCE_CANDIDATE_MATERIALIZER_MERGED / EXTERNAL_EVIDENCE_FACT_PROJECTOR_IN_VALIDATION / AUTHENTIC_RUNTIME_ADMISSION_UNOBSERVED`
Repository: `StegVerse-Labs/StegCore`
Canonical task: `GADI-001`
Parent handoff: `StegVerse-Labs/.github/docs/GADI_RESIDENT_EXECUTION_MIRROR_HANDOFF.md`
COSV: `10100000100000`
Current branch: `gadi-external-evidence-facts-projector-001`

## Purpose

StegCore owns GADI threat reasoning plus Governance evaluation/projection. It may correlate already-observed threat evidence, select the least-destructive eligible pre-authorized capability, emit a bounded PENDING defensive-intervention request, bind that exact request into the Governance candidate, evaluate it through the existing Universal Governance Connector/InTr path, and project the resulting Governance decision into the existing GADI `Admission` field. It does not observe threats, mint external-evidence envelopes, invent Governance facts, mint credentials, create runtime bindings, claim/fence work, execute defensive effects, or become a parallel InTr/StegGate authority.

## Merged chain

- Governance PR #40 -> `2765854132872078bcd15a4432a65095831b432e`: authoritative `gadi.defensive-intervention.v1` profile.
- StegCore PR #202 -> `282f30e9e46efc3a8d0d867f48e08c3aa6534e22`: Governance-decision -> GADI Admission projector.
- StegCore PR #204 -> `44f4240c72ae1e64cefd829e469e64a40b5034a3`: local GADI InTr/Governance admission materializer.
- StegCore PR #205 -> `43f61a9feda8944a5551cfbc39b302f8c65ef69c`: PENDING intervention-request + hash-bound Governance-candidate materializer over canonical GADI reasoning. Exact head `dc9aa47feeded541fae0311581b4b7dc7ea193ed` passed both observed GADI workflow instances before merge.

## External evidence -> Governance facts audit

After #205, the only remaining hand-authored pre-admission input was `resolved_governance_facts`.

Repository audit found:

- `external_governance_adapter.py` forwards already-resolved facts but does not derive them;
- `steggate.py` evaluates an already-populated `AdmissibilityRequest` but does not collect facts;
- `external_evidence.py` already provides the generic `request_from_external_evidence()` path that maps a current authorized Governance external-evidence envelope into the canonical three-layer request without granting provider execution authority;
- no repository-surfaced resident producer of a current external-evidence envelope was found. Examples/validators are source fixtures only.

Therefore the safe remaining adapter is serialization/projection from an already-authentic envelope, not a new evaluator or synthetic fact generator.

## External evidence facts projector — in validation

New entrypoint:

`scripts/materialize_gadi_governance_facts_from_external_evidence.py`

It accepts only an already-local Governance external-evidence envelope and requires its commitment candidate to match the exact GADI Governance scope:

```text
action = ADMIT_DEFENSIVE_INTERVENTION
target_ref = stegverse.gadi.defensive-intervention
scope = operation:admit-defensive-intervention
policy_ref = policy.gadi.defensive-intervention.v1
evidence_provider_execution_authority = false
```

The script reuses existing:

- `evaluate_external_evidence()` for fail-closed envelope/provider/freshness validation;
- `request_from_external_evidence()` for canonical three-layer fact derivation.

Envelope-level failures such as incomplete evidence, stale evidence, unauthorized provider, or provider execution-authority claims are rejected before projection.

A valid envelope may still project facts that later produce a DENY/FAIL-CLOSED Governance decision (for example reference-state drift). The projector preserves those facts rather than converting them into favorable observations.

Output contains exactly:

```text
judgment_conditions
signal_admission
execution_boundary
```

plus a non-authorizing projection receipt. It explicitly records:

```text
external_evidence_envelope_created = false
resolved_governance_facts_invented = false
intr_transport_performed = false
gadi_admission_created = false
runtime_binding_created = false
credential_minted = false
claim_or_fence_minted = false
execution_authority_granted = false
network_fetch_performed = false
authority_effect = NONE_FACT_PROJECTION_ONLY
```

CLI mode hashes the exact source envelope bytes and atomically writes the facts artifact and receipt.

## Validation coverage

`tests/test_gadi_governance_facts_from_external_evidence.py` verifies:

- valid/current/authorized GADI-scoped external evidence projects the exact three-layer facts;
- stale envelopes fail closed;
- unauthorized providers fail closed;
- evidence providers cannot claim execution authority;
- wrong GADI policy or target fails closed;
- valid evidence with reference-state drift can project denial facts without granting authority.

The dedicated GADI workflow now tests and compiles the projector and includes the pinned Governance external-evidence snapshot in its trigger surface.

## Authentic evidence boundary

The source/runtime-adapter chain no longer requires hand-authored Governance facts. The remaining authentic input boundary is the runtime evidence itself:

```text
CURRENT_GADI_EXTERNAL_EVIDENCE_ENVELOPE_NOT_OBSERVED
CURRENT_GADI_THREAT_OBSERVATION_NOT_OBSERVED
CURRENT_GADI_RUNTIME_BINDING_NOT_OBSERVED
CURRENT_GADI_PENDING_INTERVENTION_REQUEST_NOT_OBSERVED
CURRENT_GADI_INTR_ADMISSION_NOT_OBSERVED
CURRENT_GADI_NATIVE_COMMAND_NOT_OBSERVED
CONTROLLED_PREAUTHORIZED_ACTUATOR_RESULT_NOT_OBSERVED
CURRENT_GADI_WORKERCOORDINATOR_CLAIM_FENCE_NOT_OBSERVED
CURRENT_GADI_RESIDENT_CONSUMPTION_NOT_OBSERVED
```

Source fixtures, examples, CI, and controlled simulation do not satisfy those predicates.

## Immediate continuation

1. Validate this projector on the exact branch head and merge only if all applicable GADI checks pass.
2. Reconcile the parent `.github` handoff after merge.
3. When an authorized sovereign resident is reachable, require a current runtime-produced Governance external-evidence envelope rather than source fixtures.
4. Project that exact envelope to three-layer Governance facts with this adapter.
5. Feed current threat observations + capability evidence + projected facts through merged PR #205 to create the PENDING request/Governance candidate.
6. Run merged PR #204 for actual local InTr transport + Governance admission.
7. Combine an ADMITTED request with the independently observed runtime binding and merged StegOS command CLI.
8. Preserve parent readiness: no WorkerCoordinator claim until command, admission, runtime binding, and controlled-output observation are coherent.

## README impact

No root README mutation is required. This is a task-specific adapter over the existing Governance external-evidence interoperability and GADI reasoning surfaces.

## Release rule

This projector is not GADI activation or release evidence. Release remains deferred until authentic resident execution, reassessment/termination, exact reconstruction, and parent activation predicates are observed.
