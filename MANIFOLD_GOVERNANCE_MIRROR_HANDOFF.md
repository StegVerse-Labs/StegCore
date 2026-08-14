# Manifold Governance Runtime Kernel Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: feat/manifold-governance-runtime-kernel-001
goal_id: MANIFOLD-GOVERNANCE-RUNTIME-KERNEL-001
canonical_issue: #91
pull_request: #92
originating_goal: formalism/manifold orchestration implementation admitted by StegVerse-Labs/.github
formalism_authority: Admissible-Existence/AE + RTG + GTG + TT + STCM
canonical_runtime_authority: stegcore.steggate.evaluate_admissibility
credential_authority: TV/TVC
github_token_required: false
archive_ready: false
```

This handoff is the canonical continuation record for the first bounded StegCore manifold-orchestration kernel. It supplements, and does not replace, `STEGCORE_MIRROR_HANDOFF.md`.

## Active implementation claim

```text
task_id: MANIFOLD-GOVERNANCE-RUNTIME-KERNEL-001
claimant: current formalism/manifold continuation session
role: CLAIMED_FOR_IMPLEMENTATION
claim_created_at: 2026-08-14T05:06:00-05:00
claim_release_condition: source + deterministic tests are hosted-validated, admitted to main, and the corresponding .github owner-work/reconciliation continuation can re-observe the capability
collision_scope:
  - MANIFOLD_GOVERNANCE_MIRROR_HANDOFF.md
  - src/stegcore/manifold_governance.py
  - tests/test_manifold_governance.py
```

Existing StegCore issue #70 owns four-application runtime binding and does not overlap these files. This claim does not modify application-specific runtime bindings, public transport identity, canonical three-layer policy logic, HIL paths, release/tag machinery, or deployment authority.

## Installed implementation

```text
MANIFOLD_GOVERNANCE_MIRROR_HANDOFF.md
src/stegcore/manifold_governance.py
tests/test_manifold_governance.py
```

The kernel:

1. freezes one immutable `base_manifold_hash` for the candidate population;
2. evaluates every candidate transition through existing canonical `evaluate_admissibility`;
3. preserves canonical `ALLOW | DENY | REVIEW | FAIL_CLOSED` standing without reinterpretation;
4. builds deterministic dependency/conflict structure and stable bundle ordering;
5. is permutation-invariant for equivalent input populations;
6. fails closed on duplicate identities, stale/mixed base state, unknown dependency/conflict references, self references, and dependency cycles;
7. exposes derived coherence/gradient observations as evidence-only hashes with no authority effect;
8. separates planning from commit and never performs external execution or mints continuity receipts;
9. emits a deterministic replay-stable plan hash.

## Replay-stable semantic binding correction

The first hosted test run exposed a real implementation defect: the population plan hash incorporated canonical evaluation fields that are intentionally time-bound (`evaluated_at`, `decision_state_hash`, and canonical three-layer receipt hash), so equivalent candidate permutations produced different plan hashes.

The correction does **not** alter canonical StegGate output. `src/stegcore/manifold_governance.py` now derives its internal `evaluation_hash` from an explicit stable semantic projection containing the canonical disposition, candidate hash, predicate matrix, reasons, canonical three-layer decision/reason/request hash, and permission/continuity/execution flags while excluding only time/provenance-bound values from population-plan identity. Canonical time-bound evaluation evidence remains untouched at its source.

```text
failing head: 5b7d5adb9bfa7d32a78d0e9213252a611a92376d
failing StegCore Tests run: 31791001696
observed result: 1 failed, 218 passed, 144 subtests passed
failure: permutation invariance plan hash mismatch
fix commit: 7070ae9cb244a95783ab613e31650eb39c0dde7b
```

## Hosted validation evidence

All required current-head workflows passed on `7070ae9cb244a95783ab613e31650eb39c0dde7b`:

```text
StegCore Tests
run: 31791206611
result: SUCCESS

Validate StegCore Runtime
run: 31791206553
result: SUCCESS

BCAT Gate
run: 31791206579
result: SUCCESS

Test Readiness
run: 31791206582
result: SUCCESS

Validate StegVerse 001 002 Baseline
run: 31791206597
result: SUCCESS
```

The StegCore Tests job executed the repository test suite successfully after the replay-stability fix. Hosted validation does not create production/runtime/merge authority and does not grant credential authority.

## Mathematical / functional relationship

```text
AE joint/compositional state
  -> RTG relational transition geometry + composition invariants
  -> Admissible Resolution Function / minimum faithful resolution
  -> TT transition-block classification
  -> STCM moment-bound receipt relationships and branched routing
  -> GTG reconstruction
  -> StegCore canonical StegGate evaluation per transition
  -> this module: deterministic population/bundle planning only
  -> separate governed commit boundary
```

The manifold kernel is not a second evaluator. It is a population-level planner over canonical transition evaluations. Derived group/gradient/coherence observations are evidence only and can never grant authority, widen scope, change a canonical disposition, or bypass a commit boundary.

## Authority boundary

```text
may:
  - call canonical StegGate evaluation
  - order already-declared dependencies deterministically
  - surface conflicts
  - group candidates into bundles
  - compute deterministic plan hashes

may_not:
  - redefine AE/RTG/GTG/TT/STCM mathematics
  - alter canonical StegGate predicates/dispositions
  - turn coherence or gradients into authority
  - perform external execution
  - mint continuity/custody receipts
  - merge, release, deploy, sign, or broadcast
  - use or accept NON-TV/TVC secrets or tokens
```

## Validation commands

```text
pytest -q tests/test_manifold_governance.py
pytest -q
python scripts/verify_product_consistency.py
```

## Cross-repository dependencies

```text
upstream admission: StegVerse-Labs/.github/control/formalism-manifold-implementation-admission.json
upstream reconciliation: StegVerse-Labs/.github/FORMALISM_MANIFOLD_ORCHESTRATION_MIRROR_HANDOFF.md
formalism authority: Admissible-Existence repository-local canonical handoffs/specs
runtime authority: StegVerse-Labs/StegCore/STEGCORE_MIRROR_HANDOFF.md
transport credentials: TV/TVC only
```

## Integration and propagation obligations

After canonical merge, `.github` formalism/manifold implementation admission must re-observe this owner capability and record that the seed delta entered the canonical owner repository. No Site, Publisher, admissibility-wiki, or stegguardian-wiki release propagation is authorized merely from this implementation slice; those surfaces are evaluated only after the broader governed runtime/release criteria are satisfied.

## Completion inventory

```text
required developed files: 3/3
scaffolding/stubs: 0
missing required files: 0
focused implementation: COMPLETE
hosted workflow gates: 5/5 PASS
canonical StegCore merge: PENDING
upstream .github re-observation: PENDING
```

## Archive condition

The source/validation portion is complete. This session releases the StegCore implementation claim only after PR #92 is admitted to `main` and the upstream `.github` formalism/manifold continuation has a durable re-observation/continuation record. Until then, this session retains a bounded integration role.