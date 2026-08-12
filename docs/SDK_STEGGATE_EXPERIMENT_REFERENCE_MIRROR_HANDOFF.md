# SDK / StegGate Experiment Reference Mirror Handoff

## Authority

This is the scoped handoff for the evaluator reference-freeze lane and is subordinate to `docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md` and `STEGCORE_MIRROR_HANDOFF.md` for runtime authority.

```text
goal_id: SDK-STEGGATE-EVALUATOR-REFERENCE-FREEZE-001
originating_goal: freeze the exact SDK/LLM-adapter/StegCore/AdmittedCode and supporting repository state before sending the post-baseline experiment to external evaluators
repository: StegVerse-Labs/StegCore
branch: main
canonical_manifest: evaluation/SDK_STEGGATE_EXPERIMENT_REFERENCE_2026-08-12.json
human_reference: docs/SDK_STEGGATE_EXPERIMENT_REFERENCE.md
canonical_runtime_identity: stegverse:steggate:canonical:three-layer:v1
canonical_evaluator: stegcore.three_layer.evaluate_three_layer
state: COMPLETE_REFERENCE_FROZEN
active_implementation_claim: NONE
active_validation_claim: NONE
```

## Release/tag decision

The gap was closed with immutable exact commit SHA pins plus same-named evaluation branches, not unauthorized product tags. This is deliberate:

- `StegVerse-org/StegVerse-SDK/SDK_MIRROR_HANDOFF.md` states release/tag authority is not granted by that handoff.
- `StegVerse-org/LLM-adapter/LLM_ADAPTER_MIRROR_HANDOFF.md` explicitly blocks release/tag while canonical same-carrier activation evidence remains incomplete.
- `StegVerse-Labs/StegCore/STEGCORE_MIRROR_HANDOFF.md` says not to cut a runtime product tag until applicable release authority and release gates are satisfied.

An evaluation/replay reference therefore uses immutable commit SHAs as authority. Branches are convenience pointers only and must not be treated as stronger than the SHAs.

## Frozen component set

```text
StegVerse-Labs/StegCore
  commit: 26ad1f586092ccca8e399e13ae2e30e28dd35ca9
  branch: eval/sdk-steggate-boundary-2026-08-12

StegVerse-org/StegVerse-SDK
  commit: d13e3d7e20893be08b4eef561ed5e5fc07cb536a
  branch: eval/sdk-steggate-boundary-2026-08-12

StegVerse-org/LLM-adapter
  commit: 70fb19c3c0be49e231a7ce68bb304113f06f6f2d
  branch: eval/sdk-steggate-boundary-2026-08-12

AdmittedCode/code-admit-gate
  commit: 576d40e0f7a178c0f52146a68cf5a491b28921d5
  branch: eval/sdk-steggate-boundary-2026-08-12
  role: historical/reference guard only; not canonical current evaluator

StegVerse-Labs/TV
  commit: a6af854204712030c6575b3e4f8666cdc06b8438
  branch: eval/sdk-steggate-boundary-2026-08-12

StegVerse-Labs/TVC
  commit: 711b19ef9b65df8ee33f20e68496328be097ad52
  branch: eval/sdk-steggate-boundary-2026-08-12

StegVerse-002/micro-node-runtime
  commit: 46593a57e53e1d511cfc6fff67e9e51213607d8d
  branch: eval/sdk-steggate-boundary-2026-08-12

master-records/orchestration
  commit: 1b601dd6d0298726c103cfa379049e5891307313
  branch: eval/sdk-steggate-boundary-2026-08-12
```

## Mansoor baseline preservation

Mansoor's frozen original target is unchanged:

```text
branch: eval/mansoor-admittedcode-0.2.0-2026-08-11
commit: 5d86d7999199b9403a05320710c4d1bb95527327
```

The post-baseline experiment reference is additive and does not move that goalpost.

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

## Validation and evidence

The source components were already validated under their owning handoffs. This lane adds no semantic implementation. Its validation is referential:

1. every named repository has an exact SHA;
2. every canonical participating repository has `eval/sdk-steggate-boundary-2026-08-12` created at that SHA;
3. AdmittedCode historical/reference ownership is now documented in `AdmittedCode/code-admit-gate/ADMITTEDCODE_MIRROR_HANDOFF.md`;
4. the machine-readable reference manifest and human-readable guide are committed in StegCore;
5. Mansoor's original baseline remains separate and unchanged.

## Evaluator readiness

```text
Eduardo experiment package: READY_TO_SEND
Mansoor baseline-preservation notification: READY_TO_SEND
Mansoor detailed post-baseline architecture disclosure: HOLD_UNTIL_BLIND_NEWCOMER_OBSERVATION_IF_STILL_PENDING
```

## Cross-repository propagation

This reference freeze is not a product release and does not trigger Site/Publisher/wiki release propagation. Product-release propagation remains gated by the owning release/activation handoffs.

## Completion

```text
required reference components: 8
exact SHA pins: 8/8
evaluation branches created: 8/8
machine-readable manifest: COMPLETE
human-readable guide: COMPLETE
AdmittedCode missing mirror handoff: CREATED
Mansoor baseline preserved: COMPLETE
product tags created: 0 (intentionally unauthorized)
scaffolding_or_stubs: 0
missing_required_reference_files: 0
reference_freeze: 100%
```

MERGED INTO canonical continuation: `docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md`, `MANSOOR_EVALUATION_MIRROR_HANDOFF.md`, and `evaluation/SDK_STEGGATE_EXPERIMENT_REFERENCE_2026-08-12.json`.
