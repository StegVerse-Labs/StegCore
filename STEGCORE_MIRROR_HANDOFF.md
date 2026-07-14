# StegCore Mirror Handoff

## Repository

- Organization: StegVerse-Labs
- Repository: StegCore
- Branch in progress: `feat/commit-coherence-boundary`
- Draft pull request: #18, `Add accountable commit-coherence boundary`
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

Draft PR #18 adds:

- `src/stegcore/commit_governance.py`;
- `tests/test_commit_governance.py`;
- `docs/COMMIT_COHERENCE.md`;
- `.github/workflows/verify_commit_coherence.yml`.

The implementation is isolated from `decision.py`, so existing allow/deny/defer behavior is not replaced.

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

## Validation State

- Portable predecessor module: all six local validation cases passed before repository installation.
- Repository branch tests: seven pytest cases are committed.
- GitHub Actions workflow: committed and configured for push, pull request, and manual dispatch.
- Current observation: no workflow run or combined status was returned immediately after PR creation; this remains pending CI observation rather than a code-completion claim.

## Remaining Integration Work

1. Observe and verify the GitHub Actions run for PR #18.
2. Correct any CI failure on the same branch.
3. After green CI, mark PR #18 ready for review or merge according to repository policy.
4. Decide which future executable runner calls the gate after StegCore `decide()` returns allow.
5. Ensure any raw executor is unreachable from production mutation paths.
6. Add previous-receipt chain verification when the continuity receipt-governance layer exposes the required verified inputs.
7. Mirror public documentation through the existing Governance/Site placement rules only after the runtime contract is stable.

## Permitted Continuation Scope

Continue work on StegCore decision contracts, capability-surface binding, commit coherence, deterministic receipts, replay checks, tests, and PR #18 validation. Do not add UI restrictions, behavioral scoring, identity verification, or receipt minting to StegCore.

## Completion Assessment

- Fully developed: handoff, commit-coherence contract, deterministic predicates, capability hashing, decision receipt hashing, replay comparison, seven tests, and iPhone-triggerable verification workflow.
- Scaffolding: connection to a production executor remains intentionally deferred until that executor is identified in its owning repository.
- Activation blocker: PR #18 CI must be observed and verified.

## Initial Boundary and Public-Launch Session Record

The earlier session that established StegCore's initial public posture made and completed the following decisions and work:

- StegID proves verified continuity; StegCore consumes that evidence and decides permission.
- Initial decision outcomes were defined as `allow`, `deny`, and first-class `defer` with machine-readable reasons.
- Initial policy shapes were quorum, guardian, veto, time-lock, and escalation.
- Execution remained outside StegCore.
- Node state and append-only events were retained as internal state/audit substrate, not continuity truth.
- Public positioning was limited to: `StegVerse enables AI systems that are accountable, recoverable, and constrained by verifiable continuity.` No AGI claim was made.
- At the initial v0.1 stage, docs were authoritative over scaffold code, while later safe/future/scaffold annotations were deliberately deferred to avoid blocking functional progress.
- The session created or aligned the README, decision model, policy shapes, rationale, agent lifecycle, decision interface, policy-shape dataclasses, package initializer, registry, decision tests, and package metadata.
- Initial CI evidence shown in that session was green on Python 3.11 with six tests passing across decision, registry, and state-engine tests.
- GitHub Discussion #1 was created as the durable public feedback venue: https://github.com/StegVerse-Labs/StegCore/discussions/1
- A Show HN submission was published with the decision-boundary framing; the session did not preserve its HN URL.
- Traffic screenshots were observational and subject to GitHub's displayed traffic-metrics warning. Recorded snapshots included 92 clones / 60 unique cloners / 128 views / 15 unique visitors for an early snapshot, and a later screenshot showing 1,230 clones / 374 unique cloners / 1,317 views. These figures must not be treated as validated adoption counts.
- The earlier session owns no remaining mutation, validation, monitoring, or response obligation. Its deferred ideas—future module annotation, concrete examples, later runtime milestones, Books, and StegTalk work—are not active claims and must be reconstructed from current issues, workflows, and newer handoffs.

This historical section preserves the unique decisions and evidence from that session without superseding the active PR #18 continuation state above.
