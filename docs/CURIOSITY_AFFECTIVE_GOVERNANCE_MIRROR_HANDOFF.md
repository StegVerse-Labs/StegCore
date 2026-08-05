# Curiosity and Affective Governance Mirror Handoff

## Source of Truth

This file is the canonical continuation source for the Curiosity/Motive/Affective Governance workstream in `StegVerse-Labs/StegCore`.

## Active Goal

```text
goal_id: STEGCORE-CURIOSITY-MOTIVE-GOV-001
originating_goal: make internally coherent motive claims replayable and reconstructable while keeping execution authority, observer judgment, and phenomenal inference separate
repository: StegVerse-Labs/StegCore
branch: feat/curiosity-affective-governance-v6
canonical_issue: 48
canonical_pull_request: 49
activation_state: IMPLEMENTED_ON_BRANCH_PENDING_HOSTED_VALIDATION_AND_MERGE
```

## Authority Boundary

```text
functional_motive_attribution != execution_authority
observer_description != actor_motive
normative_denial != motive_disproof
reconstruction != occurrence
phenomenal_status: not_inferred
```

StegCore may reconstruct a transition, attribute a functional motive with bounded confidence, and adjudicate commit-time authority. It does not infer consciousness, grant authority from curiosity or affect, mint Continuity receipts, or allow the observer's existential description to overwrite the actor-side causal finding.

## Installed Surfaces

```text
src/stegcore/motive_governance.py
tests/test_motive_governance.py
examples/curiosity-governance/unauthorized-curiosity-witness.json
.github/workflows/curiosity-motive-governance.yml
docs/CURIOSITY_AFFECTIVE_GOVERNANCE_MIRROR_HANDOFF.md
```

## Implemented Behavior

- canonical hash-linked transition witnesses;
- deterministic replay and tamper detection;
- earliest motive-to-execution conversion-point detection;
- bounded functional curiosity attribution using core and discriminating evidence;
- independent commit-time authority adjudication;
- explicit observer records that do not define actor motive;
- four-finding governance records;
- fail-closed verifier disagreement handling;
- no phenomenal inference and no motive-derived authority.

## Validation Command

```text
pytest -q tests/test_motive_governance.py
```

## Remaining Work

```text
StegCore repository automation
  -> execute hosted workflow on pull request 49
  -> preserve exact failure evidence if any check fails
  -> merge only after tests pass

master-records/core-lite
  -> anchor the exact merged StegCore commit and contract hashes
  -> return anchor receipt without claiming runtime activation

StegVerse-002/core-lite and GCAT-BCAT-Engine/core-lite-prod
  -> destination-owned runtime and admission integration after the merged StegCore contract is anchored
```

## Completion and Archive Conditions

The workstream is ready for archival only after the branch is merged, hosted validation is successful, and the exact merge commit is recorded in this handoff and issue 48. Master-record anchoring and downstream activation remain separate governed transitions.
