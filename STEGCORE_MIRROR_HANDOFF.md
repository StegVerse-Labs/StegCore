# StegCore Mirror Handoff

## Repository and source of truth

- Organization: `StegVerse-Labs`
- Repository: `StegCore`
- Canonical branch: `main`
- Commit-coherence PR #18: MERGED.
- Production runtime PR #20: MERGED.
- StegGate Goal 0 coordination issue #54: COMPLETE / CLOSED.
- Governed-runtime adapter issue #21: COMPLETE / CLOSED.
- Governed-runtime adapter PR #55: MERGED at `8435279b194b9b15e0be66ef2c6f6668a842afdc`.
- Runtime-validation evidence-persistence defect: issue #23, MACHINE_OWNED / OPEN.

This file is the current handoff and task source of truth for StegCore continuation work. Before changing runtime decisions, commit governance, receipts, adapters, tests, workflows, or release state, read this file, the authoritative design documents under `docs/`, and the active issue owning the exact surface.

## Architectural decisions

1. StegCore governs whether a proposed transition may become system reality.
2. Governance binds to the declared capability surface and consequence-bearing commit; UI/transport/provider reachability does not create authority.
3. UI, API, human, AI, agent, batch, workflow, or replay paths may compose intent, but no mutation path may bypass the same governed commit boundary.
4. Coherence is evaluated after admissibility and before execution.
5. `src/stegcore/runtime.py#governed_execute` is the production mutation boundary; an executor is invoked only after admissibility and commit coherence both ALLOW.
6. StegCore consumes already-verified continuity evidence; it does not mint or independently authorize from continuity receipts.
7. The complete material admissibility decision state is part of reconstructable system reality; runtime history is not limited to successful ALLOW-to-effect paths.
8. Decision reality, execution reality, and observed reality are distinct planes and may diverge without normalization.

## Merged runtime state

### PR #18 — commit coherence

- merge commit `5f78b489c51a99af7b76b0b9e3979da820c9a296`;
- runtime contract `src/stegcore/commit_governance.py`;
- tests `tests/test_commit_governance.py`;
- contract `docs/COMMIT_COHERENCE.md`;
- dedicated workflow `.github/workflows/verify_commit_coherence.yml`;
- acceptance run `29308236624`, job `87006244615`: SUCCESS, `7 passed in 0.03s`.

Historical generic repo run `29308236597` / job `87006323507` failed during test collection because `tests/test_stegverse_spec_conformance.py` could not import `scripts.check_stegverse_spec_conformance`. It must not be represented as an all-green full-repository state.

### PR #20 — production runtime binding

- merge commit `8d5178507c86efe98c359f957ab20475e55ca9f2`;
- merged production boundary `src/stegcore/runtime.py`;
- `GovernedRuntime.evaluate_and_execute()` and `governed_execute()` call existing `decide()`, then commit coherence, then the injected executor only after both gates permit execution;
- observations bind pre/post state hashes, decision, coherence receipt, previous receipt pointer where supplied, execution result/failure, and observation time.

### PR #55 — governed runtime adapters

Issue #21 is complete and its implementation claim is released.

```text
task_id: STEGCORE-21-GOVERNED-RUNTIME-ADAPTERS
claim_state: COMPLETE
canonical_issue: StegVerse-Labs/StegCore#21 (CLOSED / COMPLETED)
merged_pr: StegVerse-Labs/StegCore#55
merge_commit: 8435279b194b9b15e0be66ef2c6f6668a842afdc
post_merge_conformance: SUCCESS
adjacent_runtime_validation_persistence_owner: StegVerse-Labs/StegCore#23
```

Merged surfaces:

- `src/stegcore/runtime_adapters.py`;
- `tests/test_governed_runtime_adapters.py`;
- `tests/test_governed_runtime_reconciliation.py`;
- `docs/GOVERNED_RUNTIME_ADAPTERS.md`;
- `.github/workflows/governed-runtime-adapters.yml`;
- `management/governed-runtime-adapters-task.json`.

Merged properties:

- one normalized UI/API/human/AI/agent/batch/workflow/replay entry protocol;
- no adapter invokes an injected executor directly; all mutation-capable adapter execution delegates to `governed_execute()`;
- exact candidate, credential, credential-subject, authority, capability, parameter-bound, and prior verified receipt-pointer binding;
- capability broadening and binding mismatch fail closed before the production runtime boundary;
- ALLOW, DENY, REVIEW, adapter-level FAIL_CLOSED, coherence denial, execution failure, commit state, observation state, and receipt-pointer state remain reconstructable;
- later effect reconciliation preserves MATCH, DIVERGENT, UNKNOWN, and GOVERNANCE_BYPASS without rewriting the governing decision;
- HTTP/API transport is a bounded shim and never an authority source.

Final pre-merge validation head `b43fc1edc88bdf9908b4b7b01cc7e49065fca3f3`:

- Governed Runtime Adapter Conformance `31260733795`: SUCCESS;
- Validate StegCore Runtime `31260733794`: SUCCESS;
- StegCore Tests `31260733883`: SUCCESS;
- Test Readiness `31260733819`: SUCCESS;
- BCAT Gate `31260733796`: SUCCESS;
- Validate StegVerse 001 002 Baseline `31260733797`: SUCCESS.

Post-merge dedicated evidence on `8435279b194b9b15e0be66ef2c6f6668a842afdc`:

- Governed Runtime Adapter Conformance `31260775199`, job `93111118343`: SUCCESS;
- compile, merged runtime-boundary tests, governed adapter/reconciliation tests, and no-direct-executor static guard all passed.

Post-merge `Validate StegCore Runtime` run `31260775205` executed continuity mapping validation, downstream dispatch validation, runtime tests, Governance snapshot validation, Governance three-layer verification, and evidence generation successfully. It then failed only at `Commit durable validation evidence` because repository automation attempted to push generated evidence directly to protected `main`. Issue #23 was reopened by automation and remains the machine-owned correction path. This persistence failure does not invalidate PR #55's dedicated post-merge conformance or reopen issue #21.

An earlier candidate revision was initially placed under `src/stegcore/adapters/**`, triggering the distinct legacy `Validate 001/002 adapter` workflow. That placement was removed before merge. The final issue #21 implementation lives at `src/stegcore/runtime_adapters.py`; no legacy 001/002 adapter implementation or workflow was changed.

## Complete decision-state reconstruction

Installed StegCore runtime contract:

- `docs/DECISION_STATE_RECONSTRUCTION.md`, commit `b10ca617d4de3e35d992c9252234f833e54e8655`.

The runtime contract preserves:

- ALLOW, DENY, REVIEW, FAIL_CLOSED, and coherence-denial paths;
- executor-unreachability and explicit non-execution on non-ALLOW paths;
- FAIL_CLOSED distinct from DENY;
- REVIEW successors as new transitions rather than retroactive rewrites;
- originating decision binding to commit and observation records;
- match, divergence, unknown state, and governance-bypass-equivalent reconciliation;
- the rule that an ALLOW receipt alone does not prove complete mediation or coverage.

### Upstream ara dependency — COMPLETE / HOSTED GREEN

Canonical interop owner: `StegVerse-Labs/ara-admissibility-interop` on `feat/steggate-v46-schema-foundation`.

Installed surfaces:

- `admissibility/decision-state-reconstruction.md`;
- `schemas/decision-state.v1.json`;
- `fixtures/decision-state/reconstruction-cases.json`;
- `tools/validate_decision_state_reconstruction.py`;
- `reports/decision-state-reconstruction-validation.json`;
- `management/steggate-decision-state-session-inventory.json`.

Evidence:

- executable decision-state implementation head `4d861c9a1dc86f4f879187394f001109f113e505`;
- Schema Foundation `31242496468` / job `93065680897`: SUCCESS;
- Repo Check `31242494602`: SUCCESS;
- handoff/task-state head `8017e22083b7f9d8fb07090aa29f2b96ba6cc57f`;
- Schema Foundation `31242687145` / job `93066153500`: SUCCESS;
- Repo Check `31242687163` / job `93066153551`: SUCCESS.

### Downstream Continuity dependency — COMPLETE / CLOSED / HOSTED GREEN

Canonical consumer: `StegVerse-Labs/Continuity`.

- handoff `STEGGATE_CONTINUITY_MIRROR_HANDOFF.md`;
- contract `docs/STEGGATE_DECISION_STATE_RECONSTRUCTION.md`;
- schema `schemas/steggate-decision-state-receipt.schema.json`;
- fixtures `examples/steggate-decision-state/reconstruction-cases.json`;
- verifier `scripts/verify_steggate_decision_state.py`;
- workflow `.github/workflows/validate-steggate-decision-state.yml`;
- issue #5 `STEGGATE-CONT-001`: CLOSED / COMPLETED;
- dedicated run `31242432042`: Python 3.11 and 3.12 SUCCESS;
- artifacts `9017444663` and `9017445027`;
- later handoff validation `31242588709`: SUCCESS.

A legacy Continuity bootstrap workflow failed independently on an earlier push; it is not part of the dedicated decision-state acceptance path and is not represented as repository-wide green.

## Deterministic execution-profile dependency

Ara execution-profile semantics remain COMPLETE / HOSTED GREEN:

- validated head `63af5b2568aa206e571f53fb172ab840fe97b7cc`;
- Schema Foundation `31238487769` / job `93055293539`: SUCCESS;
- Repo Check `31238487749` / job `93055293490`: SUCCESS;
- 7 cases = 1 ALLOW / 5 DENY / 1 FAIL_CLOSED;
- exact candidate and credential binding, capability narrowing, governed commit, and real-boundary observation are true;
- `authority_effect=false`.

## Personal Data Control Decision Layer

```text
Layer: personal-data control and deletion decision boundary
Current state: ACTIVATED_AND_CI_BOUND
Task: SC-PDCL-001
External tasks required: false
Manual tasks required: false
Authority granted: false
```

Installed locations:

- `docs/PERSONAL_DATA_CONTROL_DECISION_BOUNDARY.md`
- `schemas/personal-data-control-decision.schema.json`
- `runtime/personal-data-control-decision.v1.json`
- `scripts/check_personal_data_control_decision.py`
- `tests/test_personal_data_control_decision.py`
- `.github/workflows/stegcore-tests.yml`

Next coordinated task `SC-PDCL-002` is distinct from StegGate runtime-adapter completion and must not be conflated.

## Current continuation

StegGate runtime-adapter goal #21 is complete. The nearest repository-native unresolved item exposed by this integration is not a StegGate semantic/runtime gap but automation defect #23:

```text
owner: StegVerse-Labs/StegCore#23
state: MACHINE_OWNED / OPEN
defect: generated runtime-validation evidence cannot be pushed directly to protected main
machine release condition: a successor runtime-validation run persists its evidence through an allowed repository path and closes #23 automatically
```

Do not reopen issue #21 or duplicate its runtime-adapter implementation to solve #23.

Public documentation propagation remains gated by applicable release/publication authority; source/runtime validation alone does not authorize Site/Publisher/admissibility-wiki/stegguardian-wiki mirroring, tagging, or release.

## Completion assessment and session consolidation

- PR #18 commit coherence: COMPLETE / MERGED / dedicated hosted green.
- PR #20 production governed boundary: COMPLETE / MERGED.
- StegGate Goal 0 #54: COMPLETE / CLOSED.
- Ara deterministic execution profile: COMPLETE / HOSTED GREEN.
- Ara complete decision-state interop: COMPLETE / HOSTED GREEN.
- Continuity decision-state consumer #5: COMPLETE / CLOSED / HOSTED GREEN.
- Governed adapter/runtime producer #21: COMPLETE / CLOSED / MERGED / post-merge dedicated hosted green.
- Runtime-validation evidence persistence #23: distinct MACHINE_OWNED blocker.

Canonical continuation for the completed StegGate runtime-adapter slice is this handoff, `management/governed-runtime-adapters-task.json`, merge `8435279b194b9b15e0be66ef2c6f6668a842afdc`, and closed issue #21. The remaining #23 automation defect is independently durable and does not require reconstructing this session.
