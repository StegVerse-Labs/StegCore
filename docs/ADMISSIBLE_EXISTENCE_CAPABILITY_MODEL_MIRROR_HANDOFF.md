# Admissible-Existence Capability Model Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: feat/admissible-existence-capability-model-001
goal_id: ADMISSIBLE-EXISTENCE-CAPABILITY-MODEL-001
canonical_issue: #94
originating_session_goal: make Admissible-Existence the structural form by which StegVerse capability grows
formalism_authority: Admissible-Existence/AE + RTG + GTG + TT + STCM
canonical_runtime_authority: stegcore.steggate.evaluate_admissibility
credential_authority: TV/TVC
github_token_runtime_authority: NONE
archive_ready: false
```

This is the canonical continuation record for the first bounded StegCore capability-existence structural primitive. It supplements `STEGCORE_MIRROR_HANDOFF.md` and does not replace AE formalism authority or StegGate runtime authority.

## Active implementation claim

```text
task_id: ADMISSIBLE-EXISTENCE-CAPABILITY-MODEL-001
claimant: current AE structural-integration session
role: CLAIMED_FOR_IMPLEMENTATION
claim_created_at: 2026-08-14T11:08:56-05:00
claim_release_condition: implementation + tests are hosted-validated, admitted to main, and this handoff records final evidence
collision_scope:
  - src/stegcore/admissible_existence.py
  - tests/test_admissible_existence.py
  - src/stegcore/__init__.py AE exports only
  - docs/ADMISSIBLE_EXISTENCE_CAPABILITY_MODEL_MIRROR_HANDOFF.md
```

The active manifold claim owns `src/stegcore/manifold_governance.py`, `tests/test_manifold_governance.py`, and `MANIFOLD_GOVERNANCE_MIRROR_HANDOFF.md`; those surfaces are explicitly excluded here. Issue #70 continues to own four-application binding.

## Installed implementation

```text
src/stegcore/admissible_existence.py
tests/test_admissible_existence.py
src/stegcore/__init__.py
```

The model installs:

1. a deterministic first-class capability-existence declaration;
2. explicit lifecycle phases: DECLARED, STANDING, ADMISSIBLE, ACTIVATED, SUSPENDED, SUPERSEDED, TERMINATED;
3. bounded structural transition rules;
4. mandatory canonical StegGate evaluation for every transition;
5. strict separation between canonical disposition and structural lifecycle outcome;
6. exact candidate-to-capability binding;
7. explicit standing verification before STANDING;
8. explicit integration proof plus activation proof before ACTIVATED;
9. successor lineage binding before SUPERSEDED;
10. deterministic replay-stable transition identity excluding time-bound canonical provenance;
11. no external execution and no continuity-receipt minting;
12. TV/TVC-only credential authority metadata and zero GitHub-token runtime authority.

## Architectural invariant

```text
Admissible-Existence formalism
  -> CapabilityExistenceDeclaration
  -> canonical StegGate admissibility for requested transition
  -> structural lifecycle integrity checks
  -> phase advances only when canonical disposition is ALLOW and structural proof is complete
  -> separate governed execution / receipt / continuity layers
```

This module is not a second evaluator. Structural checks can block lifecycle advancement after canonical ALLOW but can never turn DENY, REVIEW, or FAIL_CLOSED into an allowed transition.

## Local model/runtime convergence

The session requirement to replace descriptive local-runtime selection and formally develop the model locally is already canonical and must not be duplicated:

```text
StegVerse-002/micro-node-runtime/docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md
source state: COMPLETE_RELEASED
language-model validation: workflow 31339534741 SUCCESS
persistent-endpoint validation: workflow 31384116055 SUCCESS
live activation owner: StegVerse-Labs/.github#60 + resident sovereign heartbeat
credential authority: TV/TVC
```

The repository-local model/runtime implementation is complete. Live same-execution activation remains MACHINE_OWNED and is an observation/integration dependency, not a manual source task for this branch.

## Validation commands

```text
pytest -q tests/test_admissible_existence.py
pytest -q
python scripts/verify_product_consistency.py
```

## Cross-repository dependencies and propagation

```text
formalism source: Admissible-Existence/AE/AE_MIRROR_HANDOFF.md
runtime owner: StegVerse-Labs/StegCore/STEGCORE_MIRROR_HANDOFF.md
local model source: StegVerse-002/micro-node-runtime/docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md
live local-model activation: StegVerse-Labs/.github#60
credentials/routes: StegVerse-Labs/TV + StegVerse-Labs/TVC
```

No Site, Publisher, admissibility-wiki, or stegguardian-wiki publication/release propagation is authorized merely from this structural primitive. After merge, the next integration goal is to bind one existing StegCore capability lifecycle through this primitive without duplicating its policy evaluator, then expand only through validated consumer contracts.

## Completion inventory

```text
required developed files: 4
implemented on branch: 4/4
scaffolding/stubs: 0
missing required files: 0
focused local validation: pending hosted execution
hosted workflow validation: pending PR runs
canonical merge: pending
post-merge integration exemplar: pending next goal
```

## Archive condition

This session may release its implementation claim after the PR is hosted-validated and merged to `main`, the handoff records the merge/workflow evidence, and any next integration task is durably assigned. Until then this session owns a unique implementation/integration role.
