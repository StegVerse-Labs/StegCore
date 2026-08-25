# StegCore 0.3.0 Release Notes

Release-set role: `governance_runtime`
Target tag: `v0.3.0`
Credential authority: `TV/TVC`

Executable/source-parent candidate:

```text
repository: StegVerse-Labs/StegCore
package: stegcore
version: 0.3.0
source_parent_commit: ec349be317cea0593e787f53935c22876bac636a
runtime_identity: stegverse:steggate:canonical:three-layer:v1
```

## Included proof-critical capability

`0.3.0` contains the canonical SPE standing enforcement introduced by PR #146:

```text
capability: STEGCORE_SPE_STANDING_BINDING_V1
feature_commit: f09eb36abcd3b317f35638e5c0b0c4a802d0aecf
```

When `declared_execution_context.standing_required=true`, canonical StegCore independently verifies the SDK->SPE envelope, SPE standing receipt, SDK->StegGate bridge, identity continuity, current ALLOW standing, canonical runtime identity, and non-authority constraints. Missing, stale, tampered, DENY, or differently-bound standing fails closed before the consequence executor can run.

## Public interlock traversal

The candidate also contains PR #148, merged before the source-parent freeze, which exercises a public-SDK-derived interlock/reference-participant bundle through the canonical standing verifier and bounded consequence path. That source proof intentionally stops before reciprocal SDK interlock return assembly; the downstream successor SDK production runner owns Master Records custody, reciprocal ACK, POST_RETURN exchange, replay, and reconstruction.

## Release invariant

The eventual `v0.3.0` tag must resolve exactly to the separately validated release-candidate commit produced from source parent `ec349be317cea0593e787f53935c22876bac636a`. Moving `main` may not be substituted.

This release metadata grants no tag, publication, runtime, admissibility, or credential authority. Release execution remains behind the TV/TVC guarded successor aggregate-release path.
