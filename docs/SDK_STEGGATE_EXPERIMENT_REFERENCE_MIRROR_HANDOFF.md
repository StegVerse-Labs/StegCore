# SDK / StegGate Experiment Reference Mirror Handoff

## Authority

```text
goal_id: SDK-STEGGATE-EVALUATOR-REFERENCE-FREEZE-001
repository: StegVerse-Labs/StegCore
branch: main
canonical_manifest: evaluation/SDK_STEGGATE_EXPERIMENT_REFERENCE_2026-08-12.json
canonical_runtime_identity: stegverse:steggate:canonical:three-layer:v1
canonical_evaluator: stegcore.three_layer.evaluate_three_layer
state: COMPLETE_REFERENCE_FROZEN
```

This scoped handoff is subordinate to `docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md` and `docs/STEGCORE_MIRROR_HANDOFF.md` for runtime authority.

The evaluation reference uses immutable commit SHAs rather than product tags. The frozen component set remains StegCore, StegVerse-SDK, LLM-adapter, AdmittedCode/code-admit-gate, TV, TVC, micro-node-runtime, and master-records/orchestration at the exact SHAs recorded in the machine-readable experiment manifest.

## Experiment contract

```text
SDK manifestation
-> ingestion
-> canonical StegGate / AdmittedCode evaluation
-> commit coherence
-> return ingestion
-> discovery
-> replay / reconstruction
```

Required invariants:

```text
manifest grants authority: false
discovery grants authority: false
demo-specific evaluator: prohibited
parallel evaluator: prohibited
GitHub token runtime authority: NONE
credential authority: TV/TVC
```

## External evaluator readiness

The post-baseline experiment package may be provided to an external evaluator only after the ordinary exact-run path and canonical custody requirements are satisfied. Public repository records use neutral evaluator identifiers unless an individual has explicitly agreed to public attribution.

A separate preserved baseline for any evaluator already working against an earlier frozen state remains unchanged and must not be rewritten by this handoff.

## Cross-repository propagation

This reference freeze is not a product release and does not trigger Site/Publisher/wiki release propagation. Product-release propagation remains gated by the owning release/activation handoffs.

## Completion

The reference freeze remains complete. This privacy revision changes public attribution only; it does not change frozen case semantics, runtime authority, or evaluator interpretation.
