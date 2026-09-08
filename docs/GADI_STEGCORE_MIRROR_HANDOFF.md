# GADI StegCore Mirror Handoff

Status: ACTIVE / THREAT_REASONING_IMPLEMENTATION
Repository: `StegVerse-Labs/StegCore`
Canonical task: `GADI-001`
Parent handoff: `StegVerse-Labs/.github/docs/GADI_MIRROR_HANDOFF.md`
COSV: `10100000100000`
Branch: `gadi-001-stegcore-threat-reasoning`

## Purpose

Implement the StegCore reasoning surface for Governed Autonomous Defensive Intervention (GADI): consume `AUTONOMOUS_THREAT_OBSERVATION`, correlate evidence into a threat state, preserve uncertainty and semantic qualifiers, generate bounded `DEFENSIVE_INTERVENTION_REQUEST` candidates, compare candidate interventions using least-destructive-effective semantics, and hand candidates to the existing canonical StegGate/InTr admissibility path without creating a parallel authority.

## Preflight

- Canonical GADI handoff resolved before mutation.
- Existing StegCore authority boundary inspected: StegCore/StegGate remains the canonical commit-time admissibility runtime.
- No GADI-specific StegCore handoff existed on `main`; creating this file is therefore the first mutation for this bounded owner.
- README impact: **required** because GADI adds a new repository behavior surface (threat correlation and intervention candidate generation) even though it does not add execution or credential authority. README must be updated in the same change set.
- Existing authority boundaries must remain unchanged: no credential minting, no durable receipt minting, no external execution, no parallel policy evaluator.

## Core invariant

StegCore may derive a threat assessment and propose a defensive transition, but it does not grant authority to execute that transition. Every consequential action candidate must still be submitted to the canonical StegGate/InTr governance path and separately bind to an available pre-authorized capability.

## Semantic-integrity defensive posture

External AI observations can be dangerous even when downstream execution uses valid permissions if the originating meaning is materially distorted before governance. GADI therefore preserves semantic qualifiers as evidence rather than silently strengthening them.

Examples that must remain distinguishable:

- `may` must not silently become `is`;
- suspicion must not silently become fact;
- analysis must not silently become instruction;
- recommendation must not silently become authorization;
- bounded scope must not silently broaden;
- inferred motive must not silently become asserted motive.

The reasoning layer records semantic-integrity state as observation evidence. A semantic-integrity finding alone does not authorize intervention; it can only contribute to correlation and threat assessment.

## Planned implementation

- `src/stegcore/gadi.py`
  - typed threat states;
  - observation correlation;
  - uncertainty preservation;
  - semantic-integrity assessment;
  - intervention candidate model;
  - least-destructive-effective candidate selection;
  - fail-closed behavior for incomplete or contradictory evidence.
- `tests/test_gadi.py`
  - non-authorizing observation behavior;
  - qualifier preservation;
  - material semantic drift detection;
  - fail-closed uncertainty behavior;
  - least-destructive-effective selection;
  - canonical-admission handoff metadata.
- `README.md`
  - document GADI reasoning boundary and explicit non-authority semantics.

## Acceptance criteria for this bounded owner

1. A valid threat observation can be correlated into a deterministic threat-state assessment.
2. Missing or contradictory critical evidence cannot produce an `IMMINENT_HARM` assessment.
3. Semantic qualifiers are preserved and material drift is surfaced as evidence.
4. Candidate interventions are ranked only among pre-declared capabilities and choose the least-destructive candidate that satisfies the required effectiveness threshold.
5. Generated intervention requests explicitly require downstream canonical admission and do not claim execution authority.
6. Tests demonstrate the above behavior.
7. README reflects the added behavior and authority boundary.

## Remaining ecosystem work after StegCore

- StegOS contract validation receipt / repository validation path -> `StegVerse-Labs/StegOS`
- Governed Intervention Capability Registry runtime data and TV/TVC bindings -> `StegVerse-Labs/StegOS`, `StegVerse-Labs/TV`, `StegVerse-Labs/TVC`
- Defensive capability custody/runtime bindings -> `StegVerse-Labs/TV`, `StegVerse-Labs/TVC`
- GADI resident executor/reassessment loop -> `StegVerse-002/micro-node-runtime`
- Intervention receipt/reconstruction package -> `StegVerse-Labs/Continuity`
- External-threat/HIL readiness/proof surface -> `StegVerse-Labs/Site`
- Cross-repo closed-loop simulation and activation evidence -> canonical runtime coordination

## Release propagation

When GADI reaches release/tag readiness, verify pertinent semantics are propagated/applied to:

- `StegVerse-Labs/Site`
- `GCAT-BCAT-Engine/Publisher`
- `admissibility-wiki`
- `stegguardian-wiki`
