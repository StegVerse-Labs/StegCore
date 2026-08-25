# StegCore 0.3.0 Release Notes

Release-set role: `governance_runtime`  
Target tag: `v0.3.0`  
Credential/release authority: `TV/TVC`

## Exact release binding

```text
source_parent_commit_sha: ef38410505b0ef3e84148892b1d6e3cdef20f300
release_relation: EXACT_ONE_COMMIT_RELEASE_NOTE_ONLY_SUCCESSOR
release_notes_path: RELEASE_NOTES_0_3_0.md
runtime_identity: stegverse:steggate:canonical:three-layer:v1
```

The source parent passed exact-head hosted validation in `StegCore Package Version Identity Validation` run `32911552882`, including:

- exact 0.3.0 package/service identity;
- canonical SPE standing binding tests;
- canonical StegGate runtime tests;
- bounded public interlock traversal tests;
- `scripts/verify_product_consistency.py`;
- artifact build and built-wheel `Version: 0.3.0` verification.

## Included proof-critical capability

The release contains canonical SPE-standing enforcement and bounded public interlock traversal. Proof-critical executable ancestry includes `124ea6b53ff79db8f514cacf1aab295f03cacf74`, which contains the standing/interlock consequence traversal used by the successor proof lane. That ancestor is not substituted for the TVC direct `source_parent_commit_sha` above.

When standing is required, missing, stale, tampered, denied, or differently-bound standing/interlock evidence fails closed before the bounded consequence executor can run.

## Preserved authority boundaries

- SPE standing ALLOW does not authorize execution by itself.
- StegGate ALLOW does not prove execution occurred.
- StegCore does not mint SPE standing, Continuity receipts, Master Records custody authority, credential authority, or release authority.
- Hosted validation is non-authorizing.
- TV/TVC remains the only release/credential authority for the successor aggregate.
