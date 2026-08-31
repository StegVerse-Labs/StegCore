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
