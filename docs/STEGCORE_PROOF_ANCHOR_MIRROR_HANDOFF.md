# StegCore Proof Anchor Mirror Handoff

## Purpose

This is the canonical continuation source for hardening StegCore as the StegVerse technical proof anchor. It preserves the boundary between verified continuity, governance evaluation, and execution while ensuring refusal remains enforceable and decisions remain independently reproducible.

## Active Goal and Claim

```text
goal_id: STEGCORE-PROOF-ANCHOR-001
organization: StegVerse-Labs
repository: StegCore
branch: stegops/proof-anchor-invariant-map
pull_request: 24
status: bound_proof_implementation_installed_hosted_validation_pending
canonical_task_owner: PR #24 implementation lane
active_implementation_claim: docs/STEGCORE_PROOF_ANCHOR_IMPLEMENTATION_RECEIPT.md
active_validation_owner: .github/workflows/runtime-tests.yml
claim_created_at: 2026-08-02T22:31:00-05:00
claim_release_condition: PR #24 merged, explicitly superseded, or transferred through the implementation receipt
```

## Authority Boundary

StegCore evaluates already-resolved continuity, policy, delegation, authority, evidence, state-integrity, validity, and recoverability facts.

StegCore does not verify or mint Continuity receipts, fetch authority from mutable services, create execution authority, activate another repository, publish, release, tag, deploy, or grant cross-repository mutation authority.

## Durable Decisions

1. StegCore is the single technical proof anchor for governance-before-execution claims.
2. Verified identity or continuity evidence does not independently confer authority.
3. Missing, stale, conflicting, ambiguous, unreconstructable, or discontinuous required inputs fail closed.
4. Refusal is a valid result and must not be negotiable by downstream callbacks or consumer state.
5. Proof decisions must bind canonical requests to explicit policy and delegation versions, immutable artifact hashes, and a decision epoch.
6. GitHub and CI may build and validate proof artifacts but are not the legitimacy source required to verify them.
7. Broad documentation expansion, token-first work, third-party association, or unsupported guarantee claims are outside this workstream.

## Authoritative Files

```text
src/stegcore/three_layer.py
src/stegcore/proof_anchor.py
src/stegcore/runtime.py
src/stegcore/__init__.py
tests/test_three_layer.py
tests/test_proof_anchor.py
docs/STEGCORE_PROOF_ANCHOR_INVARIANT_MATRIX.md
docs/STEGCORE_PROOF_ANCHOR_IMPLEMENTATION_RECEIPT.md
.github/workflows/runtime-tests.yml
```

## Installed Work on PR #24

- Proof-anchor invariant mapping and hostile-assumption gap classification.
- `ProofAnchorBinding` requiring policy version/hash, delegation version/hash, decision epoch, and declared evaluation time.
- Deterministic bound proof hashing over canonical request, immutable binding, and result surface while excluding runtime observation time.
- Local bound-proof re-evaluation.
- Refusal-preserving downstream execution: callbacks run only after `ALLOW`.
- Tests covering stale delegation despite valid contextual evidence, reference-state mutation, repeatable proof hashes, version/epoch substitution, callback non-invocation after refusal, allowed execution, and missing binding failure.
- A durable implementation receipt containing the session execution inventory, claim state, validation state, remaining work, and release condition.

## Validation State

```text
repository_file_installation: complete_on_PR_24_branch
local_reconstructed_subset_test: pass
hosted_PR_workflow: not_observed
full_repository_tests: not_proven_for_current_head
Governance_fixture_integration: not_proven_for_current_head
merge_review: pending
```

The local subset result is supporting evidence only. The canonical hosted validator remains `.github/workflows/runtime-tests.yml`.

## Remaining Work

1. Obtain and inspect a hosted workflow run for the current PR head; correct failures on the same branch.
2. Export a self-contained offline replay proof packet under `proof_packets/offline_replay_v1/`.
3. Add a dependency-free packet verifier and expected `ALLOW`/`FAIL-CLOSED` outputs.
4. Add authoritative schemas for bound proof decisions and packet manifests.
5. Add machine-enforced constitutional semantic-change classification and invariant-diff review.
6. Add exhaustive fail-closed reason-code regression coverage.
7. Add fork identity and StegCore conformance-claim rules.
8. Add bounded downstream consumer fixtures without granting consumer override or mutation authority.

## Machine-Owned Tasks

```text
validation_owner: .github/workflows/runtime-tests.yml
trigger: pull_request synchronization, relevant push to main, schedule, or authorized workflow dispatch
expected_outputs: test result, Governance contract result, workflow jobs and logs
failure_state: repository correction commit on PR #24
release_condition: passing hosted run with inspectable evidence
```

## Cross-Repository Dependencies

- `StegVerse-Labs/Governance`: canonical three-layer fixtures consumed read-only by runtime validation.
- `StegVerse-Labs/Site`: downstream evidence observation only through its existing bounded issue and handoff.
- `GCAT-BCAT-Engine/Publisher`: awareness only through existing queue and authority boundaries.
- `StegVerse-Labs/admissibility-wiki`: documentation verification only.
- `StegVerse-002/stegguardian-wiki`: evidence awareness only.

No new propagation claim is made by PR #24.

## Convergence and Session Consolidation

Earlier session proposals for a separate constitutional-document bundle, BCAT checklist stack, policy-shape hardening, lifecycle hardening, and deployment gates converged with the live three-layer runtime and proof-anchor workstream. Their unique requirements are preserved here, in the invariant matrix, and in the implementation receipt rather than being rebuilt as a competing stack.

```text
MERGED INTO: StegVerse-Labs/StegCore/pull/24
MERGED INTO: docs/STEGCORE_PROOF_ANCHOR_INVARIANT_MATRIX.md
MERGED INTO: docs/STEGCORE_PROOF_ANCHOR_IMPLEMENTATION_RECEIPT.md
```

## Completion and Archive Conditions

This implementation workstream can release its active claim when PR #24 is merged or explicitly superseded after hosted validation. The originating chat session is not required to continue implementation because its unique goal inventory, decisions, installed work, unresolved tasks, ownership, validation boundary, and next executable actions are repository-resident.

## Percentages

```text
developed_files: 5/8 required proof-anchor deliverables
validation: 1/4 levels evidenced (installation/local subset; hosted suite, Governance integration, and merge validation pending)
integration: 1/3 (package export installed; offline packet and downstream consumer fixtures pending)
goal_activation: 62%
session_consolidation: 10/10 session goals durably transferred or merged
```
