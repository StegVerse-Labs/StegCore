# Curiosity/Affective Governance Custody Hash Transition Addendum

This addendum is subordinate to `docs/CURIOSITY_AFFECTIVE_GOVERNANCE_MIRROR_HANDOFF.md`. It does not replace or compete with that canonical handoff.

## Transition identity

```text
transition_id: STEGCORE-CUSTODY-HASH-TRANSITION-REFERENCE-001
canonical_registry: master-records/core-lite/records/custody_chain_hash_transition_registry_001.json
local_reference: evidence/custody-hash-transition-reference-001.json
integration_lane: StegVerse-Labs/StegCore#53
canonical_dependency: master-records/core-lite#27
```

## Historical and current identities

The hashes recorded in the completed downstream chain remain valid historical evidence for the exact record versions that existed when that chain completed. They must not be overwritten.

```text
Master Records organization record
historical_hash: f7db74f1a2caafab593f2beacc203901ac5a72d5d0fd44b7e0f9b209170a528f
current_migrated_hash: 216e2c43a572e11109165b5237ef82162b10dc6262b36156e3783dd6879d3103

Master Records acknowledgement
historical_hash: 0a98789be976aad5c18936fe823f9732d683f4e149051e34976eb4743678eb24
current_migrated_hash: b5b26eb34c731c7d195d4a5279cf4239086398bd9032ef9029807834abd11276

GCAT acknowledgement import
historical_hash: 1d65230536d7cc7db60cc544c84d42d9d25fc3c9382b66d703476ac34b88813e
current_migrated_hash: ed597ecde9b7736a610f273774820d662c5bec066bdad5e3980f33bc7ed87996
```

## Resolution rule

A custody hash is resolved only together with its fully qualified repository, path, record version, and transition identity. A historical hash must never be interpreted as the identifier of the current migrated envelope. The migration is append-only and preserves prior completion as historical evidence.

## Authority boundary

This reconciliation creates no runtime activation, execution authority, repository binding, policy or publication authority, occurrence claim, or phenomenal-status claim.

## Completion and release

```text
implementation_state: COMPLETE_ON_BRANCH
validation_state: BLOCKED_PENDING_EXACT_HEAD_HOSTED_RUN
release_condition: PR-head workflow success, inspected jobs/logs/artifact, merge, and exact-main success
```
