# Evaluator Path Release Notes — stegcore 0.2.0

Release-set role: `governance_runtime`

Canonical evaluator candidate:

```text
repository: StegVerse-Labs/StegCore
package: stegcore
version: 0.2.0
tag_to_publish: v0.2.0
commit: 083557adec1bdbace09ebd10fb0765eb8e9a9d08
runtime_identity: stegverse:steggate:canonical:three-layer:v1
credential_authority: TV/TVC
non-TV/TVC release credential permitted: false
```

This historical release candidate is the canonical StegCore/StegGate runtime state pinned by the StegVerse SDK governed evaluator lane. It exposes the manifested transaction path used by the upstream SDK/Core-Lite carrier while preserving the canonical three-layer StegGate evaluator and bounded production-validation semantics.

The candidate is distinct from the older `stegcore-v1.0-constitution` release and from later moving `main` development. Later runtime features must receive later distinct releases rather than being substituted into the evaluator packet.

## Release invariant

`v0.2.0` must resolve exactly to `083557adec1bdbace09ebd10fb0765eb8e9a9d08`. Do not move or reuse the tag.

Aggregate release-set identity: `ODA3-EVALUATOR-PATH-2026-08-18-R1`.

This note prepares release metadata only; GitHub source control and CI do not become runtime, control-plane, or credential authority.