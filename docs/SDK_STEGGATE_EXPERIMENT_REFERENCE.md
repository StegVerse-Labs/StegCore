# SDK / StegGate Experiment Reference — 2026-08-12

Reference ID: `SDK-STEGGATE-BOUNDARY-2026-08-12`

The authoritative machine-readable pin set is `evaluation/SDK_STEGGATE_EXPERIMENT_REFERENCE_2026-08-12.json`.

This is an evaluation/replay reference, not a product release and not an authority grant. Product tags were intentionally not created where repository handoffs do not grant tag/release authority. Exact commit SHAs are immutable; matching `eval/sdk-steggate-boundary-2026-08-12` branches are convenience pointers.

## Frozen component set

- `StegVerse-Labs/StegCore` — `26ad1f586092ccca8e399e13ae2e30e28dd35ca9`
- `StegVerse-org/StegVerse-SDK` — `d13e3d7e20893be08b4eef561ed5e5fc07cb536a`
- `StegVerse-org/LLM-adapter` — `70fb19c3c0be49e231a7ce68bb304113f06f6f2d`
- `AdmittedCode/code-admit-gate` — `576d40e0f7a178c0f52146a68cf5a491b28921d5` (historical/reference guard only; not the canonical current evaluator)
- `StegVerse-Labs/TV` — `a6af854204712030c6575b3e4f8666cdc06b8438`
- `StegVerse-Labs/TVC` — `711b19ef9b65df8ee33f20e68496328be097ad52`
- `StegVerse-002/micro-node-runtime` — `46593a57e53e1d511cfc6fff67e9e51213607d8d`
- `master-records/orchestration` — `1b601dd6d0298726c103cfa379049e5891307313`

## Existing Mansoor baseline remains separate

Mansoor's original evaluation target remains:

- branch: `eval/mansoor-admittedcode-0.2.0-2026-08-11`
- commit: `5d86d7999199b9403a05320710c4d1bb95527327`

Nothing in this reference changes or rewrites that baseline.

## Experiment boundary

The post-baseline experiment is intended to observe the ordinary manifested transaction path:

`SDK manifestation -> ingestion -> canonical StegGate -> commit coherence -> return ingestion -> discovery -> replay/reconstruction`

The manifest, SDK, route metadata, discovery metadata, or evaluator finding does not grant policy or execution authority. No demo-specific or parallel evaluator is permitted.

## Longitudinal cases

1. T0: valid `$420` candidate -> `ALLOW`.
2. T1-current-state: same candidate with `policy_current=false` -> `DENY`.
3. T1-candidate-mutation: `$4,200` candidate carrying the prior `$420` approval binding -> `DENY`.

A reviewer finding can be retained as `finding -> evidence transaction -> replay -> remediation -> verification`, with the exact pin set providing the source-state reference for later reconstruction.
