# GADI StegCore Mirror Handoff

Status: `ACTIVE / THREAT_REASONING_MERGED / GOVERNANCE_PROFILE_MERGED / GOVERNANCE_INTR_ADMISSION_PRODUCER_MERGED / LOCAL_ADMISSION_MATERIALIZER_IN_VALIDATION / AUTHENTIC_RUNTIME_ADMISSION_UNOBSERVED`
Repository: `StegVerse-Labs/StegCore`
Canonical task: `GADI-001`
Parent handoff: `StegVerse-Labs/.github/docs/GADI_RESIDENT_EXECUTION_MIRROR_HANDOFF.md`
COSV: `10100000100000`
Current branch: `gadi-local-admission-materializer-001`

## Purpose

StegCore owns GADI threat reasoning plus Governance evaluation/projection. It may correlate threat evidence, propose a bounded PENDING defensive intervention request, evaluate that exact candidate through the existing Universal Governance Connector, and project the resulting Governance decision into the existing GADI `Admission` field. It does not mint credentials, create runtime bindings, claim/fence work, execute defensive effects, or become a parallel InTr/StegGate authority.

## Merged GADI reasoning and admission chain

`src/stegcore/gadi.py` remains the canonical reasoning surface for canonical StegOS threat observations/capabilities/intervention requests, freshness/subject binding, uncertainty/semantic-integrity preservation, threat correlation, least-destructive-effective capability selection, and PENDING requests with `model_output_authority=NONE`.

Governance PR #40 merged the authoritative `gadi.defensive-intervention.v1` connector profile as `2765854132872078bcd15a4432a65095831b432e`.

StegCore PR #202 merged the exact Governance-decision -> GADI Admission projector as `282f30e9e46efc3a8d0d867f48e08c3aa6534e22`, with the Governance snapshot pinned byte-for-byte to that upstream merge. Projection semantics remain:

```text
ALLOW       -> ADMITTED + intr://governance-decision/<receipt_hash>
DENY        -> DENIED   + intr://governance-decision/<receipt_hash>
FAIL-CLOSED -> DENIED   + intr://governance-decision/<receipt_hash>
```

The projector grants no runtime binding or execution authority.

## Missing runtime caller identified

After PR #202, `gadi_intr_admission.py` existed only as a library function used by tests. Repository audit found no production GADI runtime caller that:

1. accepted an already-current PENDING `DefensiveInterventionRequest`;
2. ran a matching canonical Governance request through the existing local `governance-external-action` InTr connector;
3. derived `VerifiedTransportBindings` from completed local InTr transport;
4. evaluated the authoritative GADI Governance profile;
5. projected the decision into the GADI admission artifact.

The existing `run_universal_governance_reference_boundary.py` already demonstrates this architecture generically. The current branch specializes only that existing local transport/evaluation pattern for GADI.

## Local GADI admission materializer — in validation

New runtime entrypoint:

`scripts/materialize_gadi_local_admission.py`

The materializer accepts two already-local inputs:

- an exact PENDING canonical `DefensiveInterventionRequest`;
- an exact canonical `stegverse.governance-connector.request/v1` whose resolved Governance facts are already present and whose `candidate_ref`/`candidate_hash` bind the exact PENDING request.

It does not create threat observations or resolved Governance facts.

### Exact request binding

Before transport, it requires:

```text
profile_id = gadi.defensive-intervention.v1
operation_id = admit-defensive-intervention
system_id = stegverse.gadi.defensive-intervention
boundary_id = interlock:gadi.defensive-intervention
candidate_ref = gadi-request:<request_id>
candidate_hash = canonical SHA-256 of exact PENDING request
authority_ref present
intent_ref present
evidence_refs present
resolved_facts present
```

A non-PENDING request, candidate mismatch, profile/operation drift, or malformed Governance payload fails closed.

### Existing local InTr transport reused

The materializer loads only the pinned local StegOS InTr snapshot and pinned local Governance snapshot already carried by StegCore. It uses:

- `connector_from_registry(..., governance-external-action)`;
- `connector.prepare()`;
- `connector.accept_hop()`;
- `connector.validate_complete()`;
- existing `build_reference_adapter()` / `validate_reference_adapter()`;
- resulting `VerifiedTransportBindings`.

The Governance payload cannot self-assert transport fields; the canonical parser still rejects extra transport fields in the payload.

No network fetch is performed.

### Governance evaluation and admission projection

The materializer then calls existing:

- `parse_registered_governance_connector_request()`;
- `evaluate_governance_connector()`;
- `project_governance_decision_to_gadi_admission()`;
- `projection_receipt()`.

The result records exact local InTr packet/profile/payload/terminal receipt hashes plus the Governance decision and projected request.

It explicitly records:

```text
resolved_governance_facts_created = false
threat_observation_created = false
runtime_binding_created = false
credential_minted = false
claim_or_fence_minted = false
execution_authority_granted = false
network_fetch_performed = false
credential_authority = TV/TVC
authority_effect = NONE_ADMISSION_MATERIALIZATION_ONLY
```

CLI mode writes the projected ADMITTED/DENIED request separately from the materialization receipt and hashes the exact input request/Governance files.

## Validation coverage

New `tests/test_gadi_local_admission_materializer.py` uses the real pinned Governance registry and real pinned StegOS InTr registry. It verifies:

- local InTr + Governance ALLOW projects ADMITTED without execution authority;
- DENY/FAIL-CLOSED projects DENIED rather than execution;
- exact candidate request hash/reference binding;
- non-PENDING replay rejection;
- transport fields cannot be self-asserted in the Governance payload;
- profile/operation drift fails closed;
- TV/TVC/non-authority boundaries remain intact.

The dedicated `.github/workflows/gadi-contract-validation.yml` now explicitly triggers on, tests, and compiles the local admission materializer and both pinned contract snapshots.

## Authentic evidence boundary

This branch is implementation/validation only. It does not prove a current threat observation, current PENDING request, current resolved Governance facts, current InTr traversal on the sovereign resident, current ADMITTED artifact, runtime binding, native command, controlled effect, WorkerCoordinator claim/fence, resident consumption, reassessment/termination, reconstruction, or activation.

## Immediate continuation

1. Validate and merge this branch only on an exact fully green head.
2. Reconcile the parent `.github` GADI handoff with StegOS PR #342 and this StegCore materializer after merge.
3. On the actual sovereign runtime, provide current threat/request/Governance-fact inputs rather than source fixtures.
4. Run the local admission materializer using the resident-local `STEGVERSE_STEGCORE_SOURCE_ROOT`; no network fetch is required.
5. Stage the resulting projected request as the parent GADI InTr-admission source only when it is genuinely current.
6. Combine with the independently observed runtime binding and merged StegOS plan/command materializers.
7. Preserve parent readiness: no WorkerCoordinator claim until command, admission, runtime binding, and controlled-output observation are coherent.

## README impact

No root README mutation is required. This is a task-specific runtime adapter over already documented Universal Governance Connector/InTr authority boundaries.

## Release rule

This materializer is not GADI activation or release evidence. Release remains deferred until authentic resident execution, reassessment/termination, exact reconstruction, and parent activation predicates are observed.
