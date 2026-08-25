# StegCore 0.3.0 Release Notes

Release-set role: `governance_runtime`
Target tag: `v0.3.0`
Credential authority: `TV/TVC`

Executable/runtime coordinate used by the frozen SDK successor candidate:

```text
repository: StegVerse-Labs/StegCore
package: stegcore
version: 0.3.0
executable_source_commit: 124ea6b53ff79db8f514cacf1aab295f03cacf74
release_preparation_parent: ec349be317cea0593e787f53935c22876bac636a
runtime_identity: stegverse:steggate:canonical:three-layer:v1
```

`124ea6b...` contains both PR #146 canonical SPE-standing enforcement and PR #148 bounded public interlock traversal. The later `ec349be...` commit changed only package/version validation metadata and documentation; Git comparison shows no `src/` change. Therefore the SDK's frozen governed-test pin remains the exact executable runtime coordinate while `ec349be...` is only the release-preparation parent.

## Included proof-critical capability

`0.3.0` contains the canonical SPE standing enforcement introduced by PR #146:

```text
capability: STEGCORE_SPE_STANDING_BINDING_V1
feature_commit: f09eb36abcd3b317f35638e5c0b0c4a802d0aecf
```

When `declared_execution_context.standing_required=true`, canonical StegCore independently verifies the SDK->SPE envelope, SPE standing receipt, SDK->StegGate bridge, identity continuity, current ALLOW standing, canonical runtime identity, and non-authority constraints. Missing, stale, tampered, DENY, or differently-bound standing fails closed before the consequence executor can run.

## Public interlock traversal

The candidate also contains PR #148, which exercises a public-SDK-derived interlock/reference-participant bundle through the canonical standing verifier and bounded consequence path. That source proof intentionally stops before reciprocal SDK interlock return assembly; the downstream successor SDK production runner owns Master Records custody, reciprocal ACK, POST_RETURN exchange, replay, and reconstruction.

## Release invariant

The eventual `v0.3.0` tag must resolve exactly to the separately validated release-candidate merge commit produced from release-preparation parent `ec349be317cea0593e787f53935c22876bac636a`. TVC successor release policy must use `124ea6b53ff79db8f514cacf1aab295f03cacf74` as the executable/source coordinate so it exactly matches the frozen SDK 1.2 governed-test pin. Moving `main` may not be substituted.

This release metadata grants no tag, publication, runtime, admissibility, or credential authority. Release execution remains behind the TV/TVC guarded successor aggregate-release path.
