# Universal Governance Connector Runtime Mirror Handoff

Updated: 2026-08-31
Repository: StegVerse-Labs/StegCore
Issue: #163
Branch: feature/universal-governance-connector-runtime
State: SOURCE_IMPLEMENTATION_IN_PROGRESS
Authority effect: NONE
Execution authority: NONE
Credential authority: TV/TVC

## Goal

Implement the generic StegCore runtime adapter for the Governance-owned Universal Governance Connector Profile.

## Canonical upstream

```text
StegVerse-Labs/Governance#26
docs/governance/UNIVERSAL_GOVERNANCE_CONNECTOR_PROFILE.md
schemas/universal_governance_connector_profile.schema.json
```

## Runtime composition

```text
system-specific thin adapter
 -> Interlock/InTr-bound connector request
 -> profile/binding validation
 -> canonical ThreeLayerRequest
 -> stegcore.three_layer.evaluate_three_layer
 -> connector decision receipt
 -> Interlock egress
 -> separately authorized consequence
```

## Runtime responsibilities

The runtime validates:

- profile identity/version;
- target system and boundary identity;
- operation identity;
- Interlock exchange identity;
- InTr profile binding;
- StegGate governed-transition profile binding;
- HB/carrier profile binding;
- authority reference presence;
- evidence reference presence;
- operation policy reference binding;
- enforcement/bypass invariants.

It then calls the existing canonical three-layer evaluator.

## Non-authority invariants

```text
connector profile != authority
connector runtime != credential authority
connector runtime != consequence executor
ALLOW != execution authority
ALLOW != credential authority
ALLOW != Continuity receipt
Interlock/InTr/HB carrier != governance authority
Master Records != governance authority
```

A runtime ALLOW result means only:

```text
eligible_for_separate_consequence_authorization=true
execution_authority_granted=false
```

## Planned source surfaces

```text
src/stegcore/universal_governance_connector.py
tests/test_universal_governance_connector.py
.github/workflows/universal-governance-connector-runtime.yml
```

## Lifecycle

```text
IMPLEMENTED: IN_PROGRESS
VALIDATED: false
MERGED: false
CROSS_REPO_PROFILE_CONTRACT: PENDING
LIVE_EXTERNAL_SYSTEM: false
ENFORCED_BOUNDARY_OBSERVED: false
ACTIVATED: false
COMPLETE: false
```


## Pinned canonical Governance contract

```text
Governance merge: 0632ee691711d1fcc38ae8b1729c26b9d78d21e1
profile source blob: 53b69017caaa566fdd2ac22f9546760aa810f670
schema source blob: 034069f86db871f0f48096e2417bd15dc1373366

contracts/universal_governance_connector_snapshot/profile.example.json
contracts/universal_governance_connector_snapshot/universal_governance_connector_profile.schema.json
contracts/universal_governance_connector_snapshot/manifest.json
scripts/verify_universal_governance_connector_contract.py
```

The snapshot is evidence/contract input only; Governance authority is not transferred to StegCore.

Cross-repository validation requires both:

```text
canonical profile positive path -> ALLOW with execution_authority_granted=false
InTr profile mismatch negative control -> FAIL-CLOSED
```


## Canonical serialized request parser — issue #165

The runtime now parses the merged Governance request contract:

```text
Governance merge: 3b0e5f10616fc00f2d91117bbf5ada358b04144d
profile blob: 389078bdbafc2558df562a2529c710af32e383bd
request blob: 2d63c081555b498a70f3c7ba35e1bd2a90940e5a
profile schema blob: 034069f86db871f0f48096e2417bd15dc1373366
request schema blob: 07de89923923ca4590cd59405e5c2261c80fd560
canonical InTr profile: governance-external-action
StegOS profile merge: 5231765d07b5b69b3ef52ad9912251d956a513d1
```

`VerifiedTransportBindings` supplies Interlock exchange identity, InTr packet identity, InTr profile, governed-transition profile, and carrier profile from the verified transport runtime. Those fields are intentionally prohibited from the serialized Governance payload.

`parse_governance_connector_request()` maps the Governance-owned payload and transport-owned bindings into the existing `GovernanceConnectorRequest` and canonical `ThreeLayerRequest`.

Negative controls reject payload self-asserted transport fields, InTr profile mismatch, profile/system/boundary mismatch, unknown operation, policy mismatch, missing authority/evidence/intent/candidate, and missing transport bindings.

No parser result grants execution or credential authority.

## Updated lifecycle

```text
PROFILE_SCHEMA: MERGED_VALIDATED
INTR_PROFILE: MERGED_VALIDATED
SERIALIZED_REQUEST_SCHEMA: MERGED_VALIDATED
GENERIC_RUNTIME: MERGED_VALIDATED
SERIALIZED_REQUEST_PARSER: IMPLEMENTED_VALIDATION_PENDING
CROSS_REPO_PROFILE_REQUEST_CONTRACT: IMPLEMENTED_VALIDATION_PENDING
LIVE_EXTERNAL_SYSTEM: false
ENFORCED_BOUNDARY_OBSERVED: false
ACTIVATED: false
COMPLETE: false
```


## Universal InTr vertical slice — issue #167

Pinned transport source:

```text
StegOS merge: 5231765d07b5b69b3ef52ad9912251d956a513d1
profile: governance-external-action
contracts/stegos_universal_intr_snapshot/
```

The deterministic integration test executes:

```text
Governance request.example.json
 -> CanonicalInTrConnector(governance-external-action)
 -> exact canonical payload bytes
 -> InTr transport intent / packet_id / payload_hash
 -> complete adjacent-hop receipt chain
 -> COMPAT Interlock reference adapter
 -> VerifiedTransportBindings
 -> parse_governance_connector_request()
 -> evaluate_governance_connector()
 -> ALLOW / DENY / FAIL-CLOSED
 -> governance decision payload
 -> canonical Universal InTr return intent
 -> complete return receipt chain
```

Negative controls cover incomplete receipt chains, exact-byte tampering, wrong InTr profile, payload self-asserted transport identity, stale authority, and ENFORCED-profile bypass.

This is deterministic software/integration execution. It does not establish a live external-system ENFORCED deployment.

## Lifecycle after #167 source

```text
PROFILE_SCHEMA: MERGED_VALIDATED
INTR_PROFILE: MERGED_VALIDATED
SERIALIZED_REQUEST_SCHEMA: MERGED_VALIDATED
GENERIC_RUNTIME: MERGED_VALIDATED
SERIALIZED_REQUEST_PARSER: MERGED_VALIDATED
CROSS_REPO_GOVERNANCE_INTR_VERTICAL_SLICE: IMPLEMENTED_VALIDATION_PENDING
LIVE_EXTERNAL_SYSTEM: false
ENFORCED_BOUNDARY_OBSERVED: false
ACTIVATED: false
COMPLETE: false
```


## Governance profile registry consumer — issue #169

The runtime no longer requires applications to supply a hard-coded connector profile object.

Pinned Governance registry:

```text
Governance merge: 16ee2517cfcfe567fcf7065fbcbc8077d3651341
registry blob: 3fdabf87fadde86aee4cd6906fb6dd57ae6f1881
registry schema blob: febe9caf9362220ac1475ee7c897d79c76bce64c
registry snapshot:
  contracts/universal_governance_connector_snapshot/
    universal-governance-connector-profiles.v1.json
    universal_governance_connector_registry.schema.json
```

Runtime API:

```text
resolve_governance_connector_profile(registry, profile_id)
parse_registered_governance_connector_request(registry, payload, transport)
```

Resolution validates registry schema/version, `credential_authority=TV/TVC`, `authority_effect=NONE`, unique profile ids, and every embedded profile through the existing profile invariants. Unknown profiles fail closed.

The canonical Governance/InTr vertical slice now selects `payload.profile_id` through this registry before parsing and evaluation.

```text
registry lookup != authority
registered profile != activated profile
profile discovery != execution permission
unknown profile -> FAIL_CLOSED
```

## Updated lifecycle after #169 source

```text
PROFILE_SCHEMA: MERGED_VALIDATED
PROFILE_REGISTRY: MERGED_VALIDATED
INTR_PROFILE: MERGED_VALIDATED
SERIALIZED_REQUEST_SCHEMA: MERGED_VALIDATED
GENERIC_RUNTIME: MERGED_VALIDATED
SERIALIZED_REQUEST_PARSER: MERGED_VALIDATED
REGISTRY_RUNTIME_CONSUMER: IMPLEMENTED_VALIDATION_PENDING
CROSS_REPO_GOVERNANCE_INTR_VERTICAL_SLICE: MERGED_VALIDATED_PREDECESSOR
LIVE_EXTERNAL_SYSTEM: false
ENFORCED_BOUNDARY_OBSERVED: false
ACTIVATED: false
COMPLETE: false
```


## Thin external-system adapter runtime — issue #171

Pinned Governance adapter contract:

```text
Governance merge: 9f49f5b102e5eeb30d5ea7dbcd6265fa97ca8896
adapter fixture blob: b586497b10e4c7001357a55fa04a995c5c152b32
adapter schema blob: 43995b1fbeaf9a3e19dc67fe5bba57afd77ca073
```

Runtime source:

```text
src/stegcore/external_governance_adapter.py
tests/test_external_governance_adapter.py
```

The reference machine-executable path is:

```text
NativeGovernanceAction
 -> validate external adapter
 -> prepare canonical registered Governance request
 -> Universal InTr exact packet + receipt
 -> Interlock reference binding
 -> registered Governance profile resolution
 -> StegCore evaluation
 -> GovernanceConnectorResult
 -> gate_external_consequence()
 -> ELIGIBLE_FOR_SEPARATE_CONSEQUENCE_AUTHORITY
```

The consequence gate never executes the target consequence.

```text
consequence_executed=false
adapter_grants_execution_authority=false
governance_grants_execution_authority=false
credential_authority=TV/TVC
authority_effect=NONE
```

Negative controls cover unknown native operations, missing separate consequence authority, ENFORCED bypass, stale Governance authority, and forged Governance execution authority.

This is a deterministic enforced-source-boundary proof, not live external-system activation.


## StegGate consequence-boundary binding — issue #173

The Universal Governance adapter now converges on the existing canonical deterministic StegGate execution profile rather than defining a parallel consequence engine.

Pinned execution semantics:

```text
profile: SG-EXECUTION-DETERMINISTIC-v1
profile blob: aaa9d7192d4a845c786188c7625bab4e3166bbdc
request schema blob: c77a7d78df1c57b17c82ab81223f6ec904a42da1
runtime owner: stegcore.commit_governance
```

Candidate identity is now exact-state bound across the complete chain:

```text
native action + parameters
 -> stegverse.external-native-action-candidate.v1
 -> candidate_hash
 -> Governance request
 -> Governance result
 -> StegGate execution request
 -> commit coherence
```

The same `candidate_hash` must survive every stage. Reusing the same `candidate_ref` with changed parameters is rejected before target execution.

The target runner is reachable only after all independent predicates hold:

```text
Governance ALLOW
AND adapter consequence eligibility
AND exact candidate hash equality
AND target credential id/hash/subject equality
AND target consequence authority_ref equality
AND bounded exposed capability
AND requires_governed_commit=true
AND commit coherence ALLOW
```

The composite consequence evidence records candidate/credential/authority bindings, Governance receipt hash, InTr packet id, coherence receipt hash, executor invocation, and consequence observation.

Authority separation remains:

```text
Governance ALLOW != target authority
adapter != target authority
Interlock/InTr/HB != target authority
credential_authority = TV/TVC
adapter authority_effect = NONE
target authority_effect exists only for the bounded consequence
```

Negative controls cover candidate mutation, Governance DENY, target authority mismatch, credential mismatch, forbidden automatic capability mode, and ENFORCED bypass.

Lifecycle for this lane is IMPLEMENTED_VALIDATION_REQUESTED until #173/#174 CI passes and the merge completes. Live external-system ENFORCED observation remains separate.


## Post-consequence evidence return — issue #175

The Universal Governance external-system lane now produces a canonical post-consequence evidence artifact:

```text
schema: stegcore.universal-governance-consequence-evidence.v1
producer: src/stegcore/universal_governance_consequence_evidence.py
```

The evidence binds:

```text
adapter_id
Governance profile/system/boundary
candidate_ref + exact candidate_hash
credential_id + credential_hash + TV/TVC authority
target consequence authority_ref
Governance decision + receipt hash
request InTr packet id/profile
StegGate execution profile
coherence receipt hash
execution status
executor invocation
consequence observation
execution result hash
authority-boundary invariants
```

For a completed consequence, `executor_invoked=true`, `consequence_observed=true`, a coherence receipt is required, and the target authority effect is exactly `TARGET_CONSEQUENCE_ONLY`.

The artifact is canonical-hashed with `sha256-canonical-json-without-evidence_hash`.

The already-existing Universal InTr response path returns the exact evidence bytes and validates a complete response receipt chain linked to the request terminal receipt. No new transport profile is introduced.

The source-side Master Records projection names `master-records/core-lite`, binds the exact evidence hash and source commit, and sets:

```text
record_requested=true
destination_acknowledgement_minted=false
execution_authority_granted=false
credential_authority=TV/TVC
authority_effect=NONE_SOURCE_PROJECTION_ONLY
```

Master Records must independently validate and record the artifact as an organization record before any destination acknowledgement exists.

Negative controls cover false completion/observation, candidate hash drift, missing coherence receipt, evidence tamper, and exact-byte return transport tamper.

Continuity minting and publication authority remain false.


## Return transport lineage projection — issue #177

The source-side Master Records projection now binds the actual consequence-evidence travel path rather than only the request packet.

Required lineage:

```text
request_intr_packet_id
 -> governance_receipt_hash
 -> source_evidence_hash
 -> return_intr_packet_id
 -> return_terminal_receipt_hash
```

The projection also binds `return_payload_hash` and requires it to equal the exact canonical hash of the returned consequence-evidence payload.

The projection cannot be built without:

```text
return_intr_packet_id
return_payload_hash
return_terminal_receipt_hash
```

and a mismatched return payload hash fails closed.

Destination semantics remain unchanged:

```text
record_requested=true
destination_acknowledgement_minted=false
execution_authority_granted=false
credential_authority=TV/TVC
authority_effect=NONE_SOURCE_PROJECTION_ONLY
```

This closes the source-side travel-reporting gap. Master Records still must independently validate and record it as an organization record.


## Sovereign reference-boundary runner — issue #179

The merged Universal Governance architecture now has a bounded local-source runner under `scripts/run_universal_governance_reference_boundary.py`. It writes only to a caller-supplied bound-state root and is intended for `StegVerse-Labs/.github#690 / SHWP-UNIVERSAL-GOVERNANCE-ENFORCED-REFERENCE-001`.

The runner proves exactly one governed target mutation, a bypass-negative-control that leaves target state unchanged, consequence evidence return over Universal InTr, and a Master Records source projection. It explicitly records `real_external_system_enforced_activation=false`; source/CI validation of this runner is not resident observation.


## Master Records destination organization record — master-records/core-lite #33 / PR #34

Destination organization-record machinery is now merged and independently validated.

```text
Destination repository: master-records/core-lite
Issue: #33 CLOSED_COMPLETED
PR: #34 MERGED
Merge commit: 78abdcad9ee4a82f6ae71cc68bcfdfb867f86880
Focused workflow: Universal Governance Consequence Custody
Focused PR run: 33427730279 PASS
Focused PR job: 99605309994 PASS
```

The destination validates the canonical consequence evidence plus source projection, exact source commit/evidence hash, candidate and Governance bindings, request/return InTr lineage, return payload equality, TV/TVC credential authority, completed consequence observation/coherence, and all non-authority boundaries before minting a destination-owned organization-record acknowledgement.

Destination organization-record semantics remain bounded:

```text
destination_custody_accepted=true
destination_acknowledgement_minted=true
independent_validation_complete=true
runtime_activation=false
execution_authority_granted=false
continuity_receipt_minted=false
publication_authority_granted=false
credential_authority=TV/TVC
authority_effect=NONE_ORGANIZATION_RECORD_ONLY
```

`NONE_ORGANIZATION_RECORD_ONLY` replaces the legacy wire value `NONE_CUSTODY_ONLY` (MASTER-RECORDS-BULK-SEMANTIC-REMEDIATION-002). `destination_custody_accepted` is the destination's field name as merged; it means the destination recorded the artifact as an organization record.

No synthetic live organization record was committed. Authentic organization-record materialization still requires an authentic external-system consequence evidence/projection instance. The generic source/destination organization-record contract is therefore MERGED_VALIDATED, while live ENFORCED observation remains a deployment/runtime task.

Updated lifecycle:

```text
UNIVERSAL_GOVERNANCE_GENERIC_SOURCE_PATH: MERGED_VALIDATED
MASTER_RECORDS_DESTINATION_ORGANIZATION_RECORD_VALIDATOR: MERGED_VALIDATED
SOVEREIGN_REFERENCE_BOUNDARY_RUNNER: MERGED_VALIDATED_SOURCE
LIVE_EXTERNAL_SYSTEM: false
ENFORCED_BOUNDARY_OBSERVED: false
AUTHENTIC_MASTER_RECORDS_ORGANIZATION_RECORD: false
ACTIVATED: false
COMPLETE: false
```
