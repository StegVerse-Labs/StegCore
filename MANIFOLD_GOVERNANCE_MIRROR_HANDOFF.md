# Manifold Governance Runtime Kernel Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: main
goal_id: MANIFOLD-GOVERNANCE-RUNTIME-KERNEL-001
canonical_issue: #91 CLOSED_COMPLETED
pull_request: #92 MERGED
merge_commit: 625a6f64b2d35ec81c43b8faac971edd754c2c75
originating_goal: formalism/manifold orchestration implementation admitted by StegVerse-Labs/.github
formalism_authority: Admissible-Existence/AE + RTG + GTG + TT + STCM
canonical_runtime_authority: stegcore.steggate.evaluate_admissibility
credential_authority: TV/TVC
github_token_required: false
implementation_claim: COMPLETE_RELEASED
archive_ready_for_source_claim: true
```

This handoff is the canonical StegCore continuation record for the bounded manifold-orchestration kernel. It supplements `STEGCORE_MIRROR_HANDOFF.md`. Live repository/workflow evidence and the upstream `.github` orchestration handoff supersede stale branch-state prose.

## Authority × Time semantic correction — 2026-09-06

The completed manifold kernel remains historically released, but its governance wording is now bound to the ecosystem correction coordinated by `StegVerse-Labs/.github#1154` and StegCore `#188` / PR `#189`.

Canonical governance coordinate:

```text
Governance = Authority × Time
G = (Authority, Time)
```

State/manifold structure, policy, evidence, dependencies, recoverability, observation, HB cadence, and wall-clock readings are evaluated context or observations at that coordinate. They are not replacement governance coordinates.

Temporal non-causality is preserved:

```text
Time != Authority
Delta-time -/-> Delta-authority
wall-clock observation != Authority
heartbeat cadence != Authority
observation != authorization
```

These statements do **not** mean `Time != governance`. Time is the second governance coordinate. A clock reading, duration, or heartbeat does not manufacture Authority.

Local semantic anchor: `docs/AUTHORITY_TIME_GOVERNANCE_COORDINATE.md`.

## Claim reconciliation

```text
task_id: MANIFOLD-GOVERNANCE-RUNTIME-KERNEL-001
previous_role: CLAIMED_FOR_IMPLEMENTATION
current_role: COMPLETE_RELEASED
claim_created_at: 2026-08-14T05:06:00-05:00
claim_released_at: 2026-08-14T11:26:00-05:00
release_basis:
  - PR #92 merged to main
  - issue #91 closed completed
  - all five hosted StegCore validation gates passed
  - StegVerse-Labs/.github/FORMALISM_MANIFOLD_ORCHESTRATION_MIRROR_HANDOFF.md records branch implementation/validation admission COMPLETE and session_validation_claim RELEASED_COMPLETE
semantic_correction:
  task: AUTHORITY-TIME-GOVERNANCE-COORDINATE-001
  issue: #188
  pull_request: #189
  state: PENDING_EXACT_HEAD_VALIDATION_AND_MERGE
```

The previously claimed collision scope is released. Existing StegCore #70 remains the separate four-application runtime-binding owner. Resident formalism/manifold lane execution remains MACHINE_OWNED in `.github` and must not be duplicated by a chat session. The Authority × Time correction is a bounded semantic/source reconciliation and does not reopen the historical implementation claim.

## Canonical implementation

```text
src/stegcore/manifold_governance.py
tests/test_manifold_governance.py
MANIFOLD_GOVERNANCE_MIRROR_HANDOFF.md
docs/AUTHORITY_TIME_GOVERNANCE_COORDINATE.md
```

The kernel:

1. freezes one immutable `base_manifold_hash` for a candidate population;
2. evaluates every candidate transition through canonical `evaluate_admissibility`;
3. preserves canonical `ALLOW | DENY | REVIEW | FAIL_CLOSED` without reinterpretation;
4. builds deterministic dependency/conflict structure and stable bundle ordering;
5. is permutation-invariant for equivalent input populations;
6. fails closed on duplicate identities, stale/mixed base state, unknown references, self references, and dependency cycles;
7. exposes coherence/gradient observations as evidence-only hashes with no authority effect;
8. separates planning/action resolution from commit and performs no external execution or continuity-receipt minting;
9. emits a replay-stable deterministic plan hash;
10. resolves concurrent production manifold action into continue/review/held/denied/fail-closed classes;
11. permits independent ALLOW branches to continue toward the governed commit boundary while protected REVIEW branches remain reviewable;
12. treats wall-clock readings and HB cadence as non-authorizing observations while preserving Time as a governance coordinate;
13. evaluates transition context at the applicable `(Authority, Time)` coordinate and does not promote State/manifold variables into governance coordinates.

## Production governed-manifold action extension — 2026-08-27

The manifold kernel now includes a production governance action resolver rather than remaining planning-only.

Canonical runtime surface:

```text
src/stegcore/manifold_governance.py
  govern_manifold_action(...)
  ManifoldGovernanceAction
```

This is part of StegVerse governance. It is not an SDK-local evaluator and it does not create a parallel decision path. Every transition still receives its canonical disposition from `stegcore.steggate.evaluate_admissibility`.

The resolver classifies the concurrently evolving transition population into:

```text
continue_transition_ids
review_transition_ids
held_transition_ids
denied_transition_ids
fail_closed_transition_ids
```

The central production invariant is:

```text
Governance = Authority × Time
Time != Authority
Delta-time -/-> Delta-authority
human-in-the-loop timing != Authority
wall-clock observation != Authority
heartbeat cadence != Authority
observation != authorization

independent ALLOW transitions may continue to the separately governed commit boundary
while unrelated REVIEW transitions remain reviewable
and dependent transitions remain held.

protected boundary crossing requires resolution of the separately applicable Authority
at the applicable governing Time.
```

The emitted `stegcore.governed-manifold-projection.v1` is explicitly non-authorizing and reviewable. It represents a multi-variable concurrent transition space; a single linear path is not required. Those variables describe transition geometry/context, not additional governance coordinates.

The resolver itself does not perform external execution, mint continuity/custody receipts, or bypass the existing governed commit boundary. Its role is production governance resolution before that boundary.

Focused validation coverage is installed in `tests/test_manifold_governance.py` for:
- independent ALLOW branches continuing while a protected REVIEW branch is held;
- dependent transitions remaining held behind a review boundary;
- DENY preservation;
- FAIL_CLOSED preservation;
- human presence/timing not manufacturing Authority;
- HB/wall-clock observations not manufacturing Authority.

Authority × Time exact-head validation is additionally required by PR #189 before this semantic correction may merge.

SDK demo/test consumers must call this StegCore production capability rather than duplicate its logic.

## Replay-stability correction retained

The first hosted run exposed time-bound canonical evaluation fields in population-plan identity. The correction preserved canonical StegGate output and changed only the manifold module's internal stable semantic projection.

```text
failing head: 5b7d5adb9bfa7d32a78d0e9213252a611a92376d
failing run: 31791001696
failure: permutation invariance plan hash mismatch
fix commit: 7070ae9cb244a95783ab613e31650eb39c0dde7b
```

This replay-stability behavior does not remove Time from governance; it only prevents volatile time-bound fields from corrupting a deterministic plan identity.

## Hosted validation evidence

```text
StegCore Tests: 31791206611 SUCCESS
Validate StegCore Runtime: 31791206553 SUCCESS
BCAT Gate: 31791206579 SUCCESS
Test Readiness: 31791206582 SUCCESS
Validate StegVerse 001 002 Baseline: 31791206597 SUCCESS
```

This is historical validation of the released manifold implementation. It does not by itself validate the 2026-09-06 Authority × Time correction. Hosted validation proves source correctness only and grants no production/runtime/credential authority.

## Mathematical / functional relationship

```text
Governance coordinate: Authority × Time
  + AE joint/compositional state evaluated as context
  -> RTG relational transition geometry + composition invariants
  -> Admissible Resolution Function / minimum faithful resolution
  -> TT transition-block classification
  -> STCM moment-bound receipt relationships and branched routing
  -> GTG reconstruction
  -> canonical StegGate evaluation per transition at (Authority, Time)
  -> manifold_governance: deterministic population/bundle planning only
  -> separate governed commit boundary
```

## Authority boundary

The module may evaluate canonically, order declared dependencies, surface conflicts, group candidates, and compute deterministic plan hashes. It may not redefine the Authority × Time governance coordinate, AE/RTG/GTG/TT/STCM mathematics, alter StegGate predicates/dispositions, turn analytics into Authority, execute externally, mint continuity/custody receipts, merge/release/deploy/sign/broadcast, or use NON-TV/TVC secrets/tokens.

## Upstream continuation

Canonical upstream continuation is:

```text
StegVerse-Labs/.github/FORMALISM_MANIFOLD_ORCHESTRATION_MIRROR_HANDOFF.md
StegVerse-Labs/.github/data/formalism-manifold-orchestration/task-state.json
StegVerse-Labs/.github/AUTHORITY_TIME_GOVERNANCE_COORDINATE_MIRROR_HANDOFF.md
```

That first handoff records five resident formalism/manifold worker lanes as MACHINE_OWNED. Current unresolved manifold work is resident lane receipt production and reconciliation after prerequisite receipts exist. Those tasks are not StegCore source implementation work. The third handoff separately owns the Authority × Time semantic correction.

## Validation commands

```text
pytest -q tests/test_manifold_governance.py
pytest -q
python scripts/verify_product_consistency.py
```

The correction branch must run these on its exact PR head before merge.

## Completion inventory

```text
historical manifold required developed files: COMPLETE
historical scaffolding/stubs: 0
historical focused implementation: COMPLETE + PRODUCTION ACTION EXTENSION IMPLEMENTED
historical hosted workflow gates: 5/5 PASS
historical canonical StegCore merge: COMPLETE
historical StegCore implementation claim: COMPLETE_RELEASED
resident worker receipts/reconciliation: MACHINE_OWNED / NOT SOURCE-BLOCKING
Authority × Time semantic correction: IMPLEMENTED_IN_BRANCH / VALIDATION_PENDING
```

## Propagation

No Site, Publisher, admissibility-wiki, or stegguardian-wiki release propagation is authorized merely from this kernel. Authority × Time propagation is coordinated separately by `StegVerse-Labs/.github#1156` after source correction merge/validation.

## Archive condition

The historical StegCore manifold source claim remains complete and released. The Authority × Time correction is durably owned by StegCore #188 / PR #189 and the cross-repository `.github` handoff; the originating chat thread is not required to preserve task ownership.

## Production validation continuation — 2026-08-27

```text
production validation workflow: .github/workflows/manifold-governance-production.yml
production source merge: 99397392462b8e39a510ec6d9e543551270bd402
validation trigger branch: manifold-governance-validation-reconcile
validation status: PASS
```

## Hosted production validation evidence

```text
workflow: Manifold Governance Production Validation (Non-Authorizing)
run: 33118809399
result: SUCCESS
validated head: 91c84ff96d797df7f08fa8e702a0e22b845e8130
focused manifold tests: PASS
production reviewable-projection proof: PASS
private-repository checkout: actions/checkout with persist-credentials=false
GitHub production/runtime authority: NONE
credential authority: TV/TVC
```

## Validation reconciliation merge

```text
validation reconciliation PR: #158
validation reconciliation merge: 882a25adf6635a2c61c3fa7b75ddc84c50c30741
validated head: aeeb8f07ee377dd7e3115f88a253838efb8aa6c3
hosted validation run: 33118864638
result: SUCCESS
production manifold action source: IMPLEMENTED / VALIDATED / MERGED
```
