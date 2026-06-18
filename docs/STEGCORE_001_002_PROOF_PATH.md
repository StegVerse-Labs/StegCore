# StegCore 001/002 Proof Path

Generated: 2026-06-17

## Assumptions

Active repo: `StegVerse-Labs/StegCore`.

This proof path builds on the 001/002 adapter and decision bridge already staged on the current branch.

## Done Definition

This proof path is complete when a reviewer can see:

1. The input schema owner.
2. The expected entity boundary.
3. The native StegCore decision.
4. The reason code.
5. The governance principle preserved.

## Proof Path Cases

| Case | Entity | Native Decision | Reason Code |
|---|---|---|---|
| Valid continuity record | StegVerse-001 | allow | entity_001_002.allow |
| Evidence requires review | StegVerse-001 | defer | entity_001_002.stale |
| Restricted records access violation | StegVerse-002 | deny | entity_001_002.deny |
| Reviewer refusal | StegVerse-002 | defer | entity_001_002.refusal |
| Override authority not verified | StegVerse-002 | defer | entity_001_002.override_required |

## Governance Rules Preserved

Continuity is not approval.

Execution is not admissibility.

Visibility is not governance.

Discovery is not execution authority.

Reviewer is not override authority.

A refusal must bind consequence unless explicit override authority exists.

## Next Repo Step

Add a runner that emits a deterministic JSON proof-path report once the branch vocabulary is accepted by the connector and CI.
