# StegCore GLM Boundary Declaration Workstream

## Purpose

This directory documents the StegCore GLM boundary declaration workstream.

The workstream installs a hypothetical StegVerse Governance Layer Manifest packet for transition admissibility and commit-time governance review.

## Target Repository

```text
Repository: StegVerse-Labs/StegCore
Reason: StegCore decides whether an actor can perform an action now, under constraints and consent. The GLM packet describes the boundary of that transition-admissibility decision.
```

This does not belong in `StegVerse-Labs/Site` because it is not a Site mirror or paper-display artifact.

## Installed Paths

```text
glm/org-index.json
glm/layers/transition-admissibility.glm.json
schemas/glm/transition-receipt.schema.json
schemas/glm/authority-class.schema.json
schemas/glm/policy-reference.schema.json
examples/glm/transition-receipt.allow.example.json
examples/glm/transition-receipt.deny.example.json
tools/glm/check_glm_packet.py
docs/glm/STEGVERSE_GLM_BOUNDARY_NOTE.md
docs/glm/STEGVERSE_GLM_VALIDATION_CHECKLIST.md
docs/glm/STEGVERSE_GLM_REVIEW_RUBRIC.md
docs/glm/STEGVERSE_GLM_FEEDBACK_PLAN.md
docs/glm/emanuel-review-note.md
docs/STEGCORE_GLM_MIRROR_HANDOFF.md
```

## Boundary Position

The GLM organization index answers only a discovery question:

```text
What governance layer declarations does StegVerse publish?
```

The transition-admissibility manifest answers a governance-boundary question:

```text
What does this layer claim, what does it observe, what does it assume, what does it exclude, and where does its authority or evidentiary visibility end?
```

## Non-Claims

This workstream does not claim:

- final GLM compliance;
- certification;
- automatic interoperability;
- EVIDE integration;
- universal admissibility;
- authority inheritance;
- semantic merging;
- legal sufficiency.

## Validation

Run:

```bash
python tools/glm/check_glm_packet.py
```

Expected result:

```text
valid: StegCore GLM boundary packet
```

## Archive Readiness

This README and `docs/STEGCORE_GLM_MIRROR_HANDOFF.md` contain the forward state for the GLM boundary declaration workstream. Prior chat context is not required to continue.
