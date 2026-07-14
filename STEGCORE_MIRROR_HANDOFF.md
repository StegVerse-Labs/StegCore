# StegCore Mirror Handoff

## Repository

- Organization: StegVerse-Labs
- Repository: StegCore
- Branch in progress: `feat/commit-coherence-boundary`
- Current goal: establish an accountable commit boundary for human/AI execution while preserving interface and device freedom.

## Source of Truth

This file is the current handoff and task source of truth for StegCore continuation work.

Before changing runtime decisions, commit governance, receipts, tests, or related workflows, read this file and the authoritative design documents under `docs/`.

## Architectural Decisions

1. StegCore governs whether a proposed transition may become system reality.
2. UI presentation is not standardized or governed as a visual surface.
3. Governance binds to the declared capability surface and the consequence-bearing commit.
4. Any UI, API, human, AI, agent, or batch path may compose intent, but no state-mutating path may bypass the same commit boundary.
5. A transition is coherent only when it preserves:
   - authority validity;
   - denial reachability;
   - governable continuation.
6. Coherence evaluation occurs after existing admissibility returns allow and before execution.
7. StegCore consumes already-verified continuity evidence; it does not verify or mint continuity receipts.
8. The existing `decide()` interface remains intact. Commit coherence is added as a separate deterministic module until a later resolver integration is explicitly approved.

## Current Build State

The repository already contains:

- documentation-first StegCore decision contracts;
- deterministic allow/deny/defer scaffolding in `src/stegcore/decision.py`;
- continuity-to-admissibility mapping;
- state/audit substrate;
- validation scripts and comparison documentation.

This branch adds:

- `src/stegcore/commit_governance.py`;
- `tests/test_commit_governance.py`;
- `docs/COMMIT_COHERENCE.md`;
- `.github/workflows/verify_commit_coherence.yml`.

## Acceptance Criteria

- Existing `decide()` behavior remains compatible.
- Manual capability mode yields a coherent ALLOW test result.
- Autonomous/unbounded capability mode yields DENY before a runner is invoked.
- Authority self-invalidation yields DENY.
- Ungovernable successor state yields DENY.
- Decision receipts include `capability_hash`, `coherent`, `coherence_checks`, and `receipt_hash`.
- Receipt tampering is detected.
- Replay recomputes coherence sub-checks.
- GitHub Actions exposes one manual choice input: `allow` or `deny`.

## Remaining Integration Work

1. Validate the new module and tests in GitHub Actions.
2. Decide which future executable runner calls the gate after StegCore `decide()` returns allow.
3. Ensure any raw executor is unreachable from production mutation paths.
4. Add previous-receipt chain verification when the continuity receipt-governance layer exposes the required verified inputs.
5. Mirror public documentation through the existing Governance/Site placement rules only after the runtime contract is stable.

## Permitted Continuation Scope

Continue work on StegCore decision contracts, capability-surface binding, commit coherence, deterministic receipts, replay checks, and tests. Do not add UI restrictions, behavioral scoring, identity verification, or receipt minting to StegCore.

## Completion Assessment

- Fully developed: commit-coherence contract, portable deterministic predicates, receipt hashing, replay comparison, tests, and iPhone-triggerable verification workflow.
- Scaffolding: connection to a production executor remains intentionally deferred until that executor is identified in its owning repository.
