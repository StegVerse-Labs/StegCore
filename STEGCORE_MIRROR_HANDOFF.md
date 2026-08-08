# StegCore Mirror Handoff

## Repository and source of truth

- Organization: `StegVerse-Labs`
- Repository: `StegCore`
- Canonical branch: `main`
- Commit-coherence PR #18: MERGED.
- Production runtime PR #20: MERGED.
- StegGate Goal 0 coordination issue #54: COMPLETE / CLOSED.
- Current governed-runtime continuation owner: issue #21, `Enforce governed runtime adapters and verified receipt chaining across mutation entry points`.

This file is the current handoff and task source of truth for StegCore continuation work. Before changing runtime decisions, commit governance, receipts, adapters, tests, or workflows, read this file, the authoritative design documents under `docs/`, and the active issue owning the exact runtime surface.

## Architectural decisions

1. StegCore governs whether a proposed transition may become system reality.
2. Governance binds to the declared capability surface and consequence-bearing commit; UI/transport/provider reachability does not create authority.
3. UI, API, human, AI, agent, batch, workflow, or replay paths may compose intent, but no mutation path may bypass the same governed commit boundary.
4. Coherence is evaluated after admissibility and before execution.
5. `src/stegcore/runtime.py#governed_execute` is the merged production mutation boundary; an executor is invoked only after admissibility and commit coherence both ALLOW.
6. StegCore consumes already-verified continuity evidence; it does not mint or independently authorize from continuity receipts.
7. The complete material admissibility decision state is itself part of reconstructable system reality; runtime history cannot be limited to successful ALLOW-to-effect paths.
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

## Active runtime claim / collision boundary

Issue #21 is the canonical implementation owner for reusable mutation-entry adapters, HTTP/API bounded transport, receipt-chain binding, and complete runtime decision-state production.

```text
claim_state: CLAIMED_FOR_IMPLEMENTATION
canonical_owner: StegVerse-Labs/StegCore#21
collision_rule: no ara, Continuity, or parallel chat lane may implement competing runtime adapters/producer semantics while #21 remains active
release_condition: committed adapter/runtime producer code + deterministic dedicated hosted CI proving callback unreachability before admissibility+coherence ALLOW and preserving complete decision/commit/observation/reconciliation bindings
```

The HTTP/API requirement was transferred through comment `5224430822`.

The complete decision-state runtime requirement was initially transferred through comment `5224765289` and reconciled with hosted upstream/downstream evidence through comment `5224812524`.

`MERGED INTO: StegVerse-Labs/StegCore#21#issuecomment-5224812524`

## Complete decision-state reconstruction

Installed StegCore runtime contract:

- `docs/DECISION_STATE_RECONSTRUCTION.md`, commit `b10ca617d4de3e35d992c9252234f833e54e8655`.

The runtime requirement is:

- every governed transition attempt emits or binds complete material decision state, including ALLOW, DENY, REVIEW, FAIL_CLOSED, and coherence-denial paths;
- non-ALLOW paths remain executor-unreachable while explicit non-execution remains reconstructable;
- FAIL_CLOSED remains distinct from DENY;
- REVIEW successor candidates are new transitions, not retroactive rewrites;
- ALLOW binds the originating decision state to commit and observation records;
- reconciliation preserves match, divergence, unknown state, and governance-bypass-equivalent outcomes;
- an ALLOW receipt alone is not proof of complete mediation/coverage.

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

The first decision-state workflow attempt failed because fixture records omitted `schema_version`; commit `4d861c9a1dc86f4f879187394f001109f113e505` corrected the defect, and succeeding hosted runs are green.

### Downstream Continuity dependency — COMPLETE / CLOSED / HOSTED GREEN

Canonical consumer: `StegVerse-Labs/Continuity`.

- handoff `STEGGATE_CONTINUITY_MIRROR_HANDOFF.md`;
- contract `docs/STEGGATE_DECISION_STATE_RECONSTRUCTION.md`;
- schema `schemas/steggate-decision-state-receipt.schema.json`;
- fixtures `examples/steggate-decision-state/reconstruction-cases.json`;
- verifier `scripts/verify_steggate_decision_state.py`;
- workflow `.github/workflows/validate-steggate-decision-state.yml`;
- issue #5 `STEGGATE-CONT-001`: CLOSED / COMPLETED.

Hosted evidence:

- dedicated run `31242432042`;
- Python 3.11 job `93065513964`: SUCCESS;
- Python 3.12 job `93065513976`: SUCCESS;
- artifacts `9017444663` and `9017445027`;
- later handoff validation run `31242588709`: SUCCESS.

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

Next coordinated task `SC-PDCL-002` is distinct from issue #21 and must not be conflated.

## Remaining integration work

1. Issue #21 implements governed adapters and runtime decision-state production.
2. Preserve `governed_execute()` as the only production mutation callback boundary for supported adapters.
3. Add and host-validate deterministic adapter/chain tests covering ALLOW and every non-ALLOW outcome, explicit non-execution, decision→commit→observation binding, divergence/unknown/bypass reconciliation, and prior receipt-pointer preservation.
4. Resolve or supersede the historical generic repository import-path failure under its owning automation lane; do not infer full-suite green from dedicated suites.
5. Continue `SC-PDCL-002` only under its distinct repository owner.
6. Public documentation propagation remains gated by applicable release/publication authority; source validation alone does not authorize Site/Publisher/wiki mirroring.

## Completion assessment and session consolidation

- PR #18 commit coherence: COMPLETE / MERGED / dedicated hosted green.
- PR #20 production governed boundary: COMPLETE / MERGED.
- StegGate Goal 0 #54: COMPLETE / CLOSED.
- Ara deterministic execution profile: COMPLETE / HOSTED GREEN.
- Ara complete decision-state interop: COMPLETE / HOSTED GREEN.
- Continuity decision-state consumer #5: COMPLETE / CLOSED / HOSTED GREEN.
- Governed adapter/runtime producer: ACTIVE under issue #21; not complete until its machine release condition is satisfied.

The decision-state reconstruction session owns no remaining StegCore runtime implementation role. Its unique requirements have been transferred into #21 and validated dependencies are repository-native. No duplicate runtime implementation should be initiated from that session.

Archive-safe canonical continuation is `StegVerse-Labs/StegCore#21`, this handoff, `docs/DECISION_STATE_RECONSTRUCTION.md`, ara `ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md`, and Continuity `STEGGATE_CONTINUITY_MIRROR_HANDOFF.md`.
