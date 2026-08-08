# StegCore Mirror Handoff

## Repository

- Organization: StegVerse-Labs
- Repository: StegCore
- Canonical branch: `main`
- Commit-coherence PR #18: MERGED.
- Production runtime PR #20: MERGED.
- StegGate Goal 0 coordination issue #54: COMPLETE / CLOSED.
- Current governed-runtime continuation owner: issue #21, `Enforce governed runtime adapters and verified receipt chaining across mutation entry points`.

## Source of Truth

This file is the current handoff and task source of truth for StegCore continuation work.

Before changing runtime decisions, commit governance, receipts, adapters, tests, or related workflows, read this file and the authoritative design documents under `docs/` plus the active issue that owns the exact runtime surface.

## Architectural Decisions

1. StegCore governs whether a proposed transition may become system reality.
2. UI presentation is not standardized or governed as a visual surface.
3. Governance binds to the declared capability surface and the consequence-bearing commit.
4. Any UI, API, human, AI, agent, batch, workflow, or replay path may compose intent, but no state-mutating path may bypass the same commit boundary.
5. A transition is coherent only when it preserves authority validity, denial reachability, and governable continuation.
6. Coherence evaluation occurs after existing admissibility returns allow and before execution.
7. StegCore consumes already-verified continuity evidence; it does not verify or mint continuity receipts.
8. The existing `decide()` interface remains intact.
9. `src/stegcore/runtime.py#governed_execute` is the merged production mutation boundary; injected executors are invoked only after admissibility and commit coherence both ALLOW.
10. Transport, adapter, hosting, or reachability never create execution authority.
11. The complete material admissibility decision state is itself part of reconstructable system reality; runtime history must not be limited to successful ALLOW-to-effect paths.
12. Decision reality, execution reality, and observed reality are distinct planes and may diverge without being normalized into one another.

## Merged Runtime State

### PR #18 — commit coherence

PR #18, `Add accountable commit-coherence boundary`, merged into `main` on 2026-07-14.

- head SHA: `a495c0034906a828794491e7575ef0885caa09db`
- merge commit: `5f78b489c51a99af7b76b0b9e3979da820c9a296`
- installed runtime contract: `src/stegcore/commit_governance.py`
- tests: `tests/test_commit_governance.py`
- contract: `docs/COMMIT_COHERENCE.md`
- dedicated workflow: `.github/workflows/verify_commit_coherence.yml`

Dedicated hosted acceptance evidence:
- Verify Commit Coherence run `29308236624`, job `87006244615`: SUCCESS.
- exact command `python -m pytest -q tests/test_commit_governance.py`.
- result: `7 passed in 0.03s`.

A generic full-repository test run on the PR head (`29308236597`, job `87006323507`) failed during test collection because `tests/test_stegverse_spec_conformance.py` could not import `scripts.check_stegverse_spec_conformance` (`ModuleNotFoundError: No module named 'scripts'`). This was not a failure of the seven commit-coherence acceptance tests and must not be silently represented as an all-green repository state.

### PR #20 — production runtime binding

PR #20, `Bind production runtime to commit coherence`, is MERGED.

- head SHA: `05698a0972adc19c6276b0b1205e693598aec529`
- merge commit: `8d5178507c86efe98c359f957ab20475e55ca9f2`
- merged production boundary: `src/stegcore/runtime.py`
- `GovernedRuntime.evaluate_and_execute()` and `governed_execute()` call existing `decide()` first, then commit coherence, and invoke the injected executor only after both gates permit execution.
- resulting observations bind pre/post state hashes, decision, coherence receipt, previous receipt pointer where supplied, execution result/failure, and observation time.
- StegCore still does not verify or mint continuity receipts.

## StegGate / ara Interop State

StegCore issue #54, `STEGGATE-GOAL0-INTEROP`, is COMPLETE / CLOSED. It supplied canonical decision/coherence references to `StegVerse-Labs/ara-admissibility-interop` without transferring runtime ownership.

Ara now has hosted-green deterministic execution-profile semantics on `feat/steggate-v46-schema-foundation`:

- `schemas/execution-request.v1.json`
- `profiles/execution-deterministic.v1.yaml`
- `claims/execution-deterministic.yaml`
- `fixtures/execution/execution-profile-cases.json`
- `invariants/profile-execution.yaml`
- `tools/validate_execution_profile.py`
- `reports/execution-profile-validation.json`

Ara execution evidence:
- validated head `63af5b2568aa206e571f53fb172ab840fe97b7cc`;
- Schema Foundation run `31238487769`, job `93055293539`: SUCCESS;
- Repo Check run `31238487749`, job `93055293490`: SUCCESS;
- 7 execution cases = 1 ALLOW / 5 DENY / 1 FAIL_CLOSED;
- exact candidate and credential binding true;
- capability narrowing true;
- governed commit required true;
- real bounded consequence observation consumed;
- StegCore runtime ownership preserved;
- `authority_effect=false`.

## Active Runtime Claim / Convergence

Issue #21 is the canonical runtime owner for reusable mutation-entry adapters and receipt-chain binding.

Claim classification for the runtime-adapter capability: `CLAIMED_FOR_IMPLEMENTATION` by the issue-owned StegCore execution lane.

Issue #21 already requires:
- a narrow adapter protocol for UI, API, human, AI, agent, batch, workflow, and replay callers;
- every adapter to invoke `governed_execute()` rather than the raw executor;
- callback unreachability before admissibility + coherence ALLOW;
- previously verified receipt-chain pointer preservation;
- deterministic API/agent/batch/workflow conformance;
- fail-closed behavior for missing/inconsistent chain declarations and bypass attempts;
- non-interactive CI.

The formerly separate ara sequencing requirement `HTTP ALLOW-only / bounded runtime transport` has been merged into issue #21 through durable comment `5224430822`.

`MERGED INTO: StegVerse-Labs/StegCore#21#issuecomment-5224430822`

Transferred HTTP/API requirements include:
- transport is not authority;
- only final ALLOW after admissibility + coherence may invoke mutation;
- REVIEW/defer, DENY, coherence denial, and fail-closed states cannot invoke mutation;
- no raw HTTP route may bypass `governed_execute()`;
- exact candidate/credential/capability/action/parameter/authority binding is retained;
- downstream capability may only preserve or narrow;
- HTTP/API fixtures cover exact-bound ALLOW, candidate/credential mismatch, action/parameter excess, capability broadening, non-ALLOW non-execution, fail-closed non-execution, and direct-runner bypass;
- execution observations preserve the prior verified receipt pointer without making StegCore a receipt verifier/minter.

Machine-observable release condition: issue #21 produces committed HTTP/API adapter code, deterministic conformance tests, and dedicated hosted CI proving callback unreachability before both gates ALLOW and preservation of bound observation/receipt-pointer fields.

## Complete Decision-State Reconstruction

Installed runtime contract: `docs/DECISION_STATE_RECONSTRUCTION.md`, commit `b10ca617d4de3e35d992c9252234f833e54e8655`.

Upstream semantic contract: `StegVerse-Labs/ara-admissibility-interop/admissibility/decision-state-reconstruction.md` on `feat/steggate-v46-schema-foundation`, commit `3fbf916f42189ca6c045c6e3220ae3c2ff021a22`.

Downstream continuity handoff: `StegVerse-Labs/Continuity/STEGGATE_CONTINUITY_MIRROR_HANDOFF.md` with `docs/STEGGATE_DECISION_STATE_RECONSTRUCTION.md` and Continuity issue #5 (`STEGGATE-CONT-001`).

Issue #21 has been extended by durable comment `5224765289`.

The governing requirement is now:

- every governed transition attempt produces or binds a decision-state record, including `ALLOW`, `DENY`, `REVIEW`, `FAIL_CLOSED`, and coherence-denial paths;
- the record preserves enough material admissibility state to reconstruct why that disposition existed at that time;
- non-ALLOW paths remain non-executing, but non-execution does not erase the attempted transition;
- `FAIL_CLOSED` remains distinct from `DENY`;
- a reviewed successor candidate is a new transition and does not rewrite the earlier `REVIEW` state;
- ALLOW paths bind the originating decision state to commit and observation records;
- reconciliation can represent match, divergence, unknown observation, and governance-bypass-equivalent states;
- an ALLOW receipt does not by itself prove complete mediation or coverage.

The #21 release condition is therefore strengthened: in addition to callback unreachability and receipt-pointer preservation, hosted deterministic adapter conformance must prove durable decision-state binding across executing and non-executing paths and preserve separation between decision, execution, and observed reality.

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

```text
docs/PERSONAL_DATA_CONTROL_DECISION_BOUNDARY.md
schemas/personal-data-control-decision.schema.json
runtime/personal-data-control-decision.v1.json
scripts/check_personal_data_control_decision.py
tests/test_personal_data_control_decision.py
.github/workflows/stegcore-tests.yml
```

Next coordinated task remains repository-owned as `SC-PDCL-002`; it is distinct from StegGate adapter issue #21 and must not be conflated.

## Remaining Integration Work

1. Issue #21 owns governed adapter implementation and the transferred HTTP/API bounded-transport requirement.
2. Preserve `governed_execute()` as the only production mutation callback boundary for supported adapters.
3. Add and host-validate the #21 deterministic adapter/chain suite, now including complete decision-state binding for ALLOW and all non-ALLOW outcomes; do not mark adapter integration complete from PR #18/#20 alone.
4. Add explicit observation/reconciliation semantics sufficient to distinguish expected effect, missing effect, unknown effect, divergence, and governance bypass without overclaiming target observability.
5. Resolve or supersede the generic repository test import-path failure under its owning repository automation/task lane; do not misclassify dedicated commit-coherence success as full-suite success.
6. Continue `SC-PDCL-002` only under its distinct repository task ownership.
7. Mirror public documentation through the existing Governance/Site placement rules only after the applicable runtime contract and publication authority are separately ready.

## Permitted Continuation Scope

Continue work on StegCore decision contracts, capability-surface binding, commit coherence, governed runtime adapters, deterministic observations/receipts, replay checks, decision-state reconstruction, personal-data request transition decisions, tests, and repository-owned workflows. Do not add UI restrictions, behavioral scoring, identity verification, external deletion execution, continuity-receipt minting, or authority derived from transport/provider reachability.

## Completion Assessment

- PR #18 commit-coherence contract: COMPLETE / MERGED; dedicated 7/7 hosted acceptance suite green.
- PR #20 production `governed_execute()` boundary: COMPLETE / MERGED.
- StegGate Goal 0 issue #54: COMPLETE / CLOSED.
- Ara deterministic execution profile: COMPLETE / HOSTED GREEN; runtime ownership remains here.
- Decision-state reconstruction semantics: DOCUMENTED / CROSS-REPO BOUND; runtime implementation extension remains ACTIVE under issue #21.
- Governed adapter/HTTP transport layer: ACTIVE under StegCore issue #21; not complete until committed adapter code + dedicated hosted conformance evidence exist.
- Generic full-repository test status on the PR #18 historical head: FAILED from an import-path collection error; this is explicitly separate from the green commit-coherence suite.

## Session Consolidation

The StegGate Goal 0, HTTP transport, and complete decision-state reconstruction requirements are durably represented without relying on chat history. Ara owns interoperable schema/profile semantics; StegCore issue #21 owns runtime adapter execution and decision-state production; Continuity issue #5 owns downstream reconstruction integration. No duplicate runtime implementation should be initiated from ara, Continuity, or another session while #21 remains active.

Archive-safe transfer for this cross-repository slice requires no chat-specific information: continuation is `StegVerse-Labs/StegCore#21`, this handoff, `docs/DECISION_STATE_RECONSTRUCTION.md`, ara's `ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md`, and Continuity's `STEGGATE_CONTINUITY_MIRROR_HANDOFF.md` / issue #5.
