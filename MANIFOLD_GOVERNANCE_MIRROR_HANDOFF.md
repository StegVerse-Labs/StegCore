# Manifold Governance Runtime Kernel Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: feat/manifold-governance-runtime-kernel-001
goal_id: MANIFOLD-GOVERNANCE-RUNTIME-KERNEL-001
canonical_issue: #91
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

Existing StegCore issue #70 owns four-application runtime binding and does not overlap these files. This claim must not modify application-specific runtime bindings, public transport identity, canonical three-layer policy logic, HIL paths, release/tag machinery, or deployment authority.

## Required implementation

The kernel must:

1. freeze one immutable `base_manifold_hash` for the candidate population;
2. evaluate each candidate transition through the existing canonical `evaluate_admissibility` function;
3. preserve canonical `ALLOW | DENY | REVIEW | FAIL_CLOSED` standing without reinterpretation;
4. build deterministic dependency/conflict structure and stable bundle ordering;
5. remain permutation-invariant for equivalent input populations;
6. fail closed on duplicate identities, stale/mixed base state, unknown dependency/conflict references, and dependency cycles;
7. expose derived coherence/gradient observations as evidence-only metadata with no authority effect;
8. distinguish planning from commit and never perform external execution, mint continuity receipts, or create policy/authority;
9. emit a deterministic plan hash suitable for downstream receipt/reconstruction binding.

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
required developed files: 3
handoff: 1/1 installed
runtime module: 0/1
focused tests: 0/1
hosted validation: 0/1
canonical integration: 0/1
scaffolding/stubs: 0
missing required files: 2
```

## Archive condition

This session may release the StegCore implementation claim when all three required files are canonical, focused/full validation passes, and the upstream implementation-admission/reconciliation continuation has a durable re-observation path. Until then, do not archive this session solely because the local-model/runtime implementation is already complete elsewhere.