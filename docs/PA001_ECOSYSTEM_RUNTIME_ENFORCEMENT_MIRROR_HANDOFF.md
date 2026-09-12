# PA-001 Ecosystem Runtime Enforcement Mirror Handoff

## Status

```text
goal_id: PA-001-ECOSYSTEM-RUNTIME-ENFORCEMENT-001
repository: StegVerse-Labs/StegCore
branch: pa001-ecosystem-runtime-enforcement
issue: #208
pull_request: #209
registry: StegVerse-Labs/.github/control/worker-registry.d/pa001-ecosystem-runtime-enforcement-001.json
registry_commit: a6c35cf87329cb4c444cc55266b3c5a8782daec8
registry_state: HANDOFF_READY
state: ACTIVE
runtime_claim: SOURCE_PRESENT_STATE_ENFORCEMENT_VALIDATED_RESIDENT_PROOF_PENDING
release_claim: NOT_YET_PROVEN
```

## Goal

Convert the validated PA-001 permission/admissibility invariant into ecosystem-wide runtime enforcement without creating a second governance authority or conflating publication, documentation, observation, credential custody, or historical approval with execution authority.

## Architecture determination

No replacement-architecture blocker was found. Existing StegCore already owns canonical admissibility, commit coherence, governed runtime wrappers, StegGate execution composition, adapter conformance, and reconstructable receipt chaining. Existing GTG/RTG/TT doctrine already distinguishes proposal-time state from commit-time state.

The conversion is an enforcement/integration task. Two concrete fail-open/incomplete-state defects were found and corrected at source:

1. `GovernedRuntime.evaluate_and_execute()` previously synthesized approved authority when callers omitted `authority_resolution`.
2. `GovernedAdapterRequest` previously carried an authority reference without requiring present-tense authority state.

A broader consistency requirement was also resolved: direct governed runtime and StegGate runtime now reuse the same present-state evaluator rather than maintaining parallel semantics.

## Canonical rule

**Authority and time are state variables.** A consequence-bearing transition is decided from reconstructed commit-time state, not presumed continuity of proposal-time permission or authority.

Materially required state includes, directly or by reconstructably bound references, principal/subject identity, authority state/source, temporal state/validity, standing or consent where required, target binding, continuity, governing conditions, evidence identity/freshness, consequence attribution/reconstruction, and disposition semantics.

Explicit negative state and indeterminate state remain distinct:

- explicit stale, revoked, expired, false, or mismatched required state -> `DENY`;
- materially missing or indeterminate required state -> `FAIL_CLOSED`;
- neither may silently become `ALLOW` merely because invalidation was not observed.

## Source enforcement installed on PR #209

### Shared present-state evaluator

`src/stegcore/commit_governance.py` now provides `evaluate_present_state()` and `parse_state_time()` as shared state-validation primitives. They do not create authority or replace policy/admissibility evaluation. They evaluate:

- current authority status;
- exact authority-to-target binding;
- authority validity window or explicitly declared unbounded temporal scope;
- evidence freshness from exact validity timestamps or an already-governed current-evidence finding;
- `DENY` versus `FAIL_CLOSED` semantics.

### Direct governed runtime

`src/stegcore/runtime.py` now requires present-state establishment before commit coherence and consequence invocation. Missing authority is retained as missing, exact target binding is required, bounded authority windows are enforced, verified continuity evidence carries an optional `valid_until` in `src/stegcore/decision.py`, and stale/indeterminate evidence cannot silently allow execution.

The receipt binds the exact request, authority state, target, evaluation instant, present-state checks/reasons, complete commit-state object, and commit-state hash.

### Governed adapters

`src/stegcore/runtime_adapters.py` now carries explicit `authority_resolution`, preserves runtime `FAIL_CLOSED` distinctly from `DENY`, and treats `authority_reference` as a reference only. Adapter/reconciliation regression tests prove missing authority cannot execute or reconstruct as committed ALLOW; any later observed effect after a non-ALLOW state reconciles as governance bypass where applicable.

### Canonical StegGate execution

`src/stegcore/steggate_runtime.py` uses the same shared present-state evaluator after canonical StegGate ALLOW and before commit coherence. Missing authority fails closed; changed target and expired authority deny; current target/time/authority/evidence state is required before the existing coherence gate can make the executor reachable.

### Dependent paths

Portable SDK/SPE/Interlock traversal, neural governed execution fixtures, manifested transaction/discovery fixtures, direct runtime tests, adapter tests, reconciliation tests, and StegGate runtime tests now supply explicit target- and time-bound authority state where ALLOW is intended.

## Source reconstruction proof

`tests/test_runtime_commit_coherence.py` now proves deterministic non-executing reconstruction of present-state enforcement from the emitted receipt:

1. execute one admitted consequence exactly once;
2. recompute the retained commit-state hash from `receipt.commit_state`;
3. parse the retained evaluation instant;
4. re-run the shared `evaluate_present_state()` from retained authority, target, and evidence validity state;
5. require reconstructed disposition/checks/reasons to equal the receipt;
6. prove the consequence callback is not invoked again during reconstruction.

This is deterministic source-level reconstruction proof. It is **not** an authentic resident same-execution reconstruction claim.

## Hosted validation evidence

Exact code/reconstruction head `5fe92fdca8e61128cf7fe6a9ff238a52f4b3f5d0` passed all observed PR-head validation surfaces:

- Verify Production Runtime Coherence `34713678975` — SUCCESS;
- StegCore Package Version Identity Validation `34713678957` — SUCCESS;
- SPE Standing Canonical Binding Validation `34713678994` — SUCCESS;
- Verify Commit Coherence `34713678942` — SUCCESS;
- Neural End-to-End Governance `34713678956` — SUCCESS.

The immediately preceding documentation/source head `03db5954ef41c6540f595b0bf36c4865e4bcc276` also passed all five corresponding validation workflows (`34713607790`, `34713607797`, `34713607831`, `34713607792`, `34713607781`).

This handoff update is a newer documentation commit and therefore requires its own exact-head validation before PR #209 may be merged.

## Conversion phases

1. **Architecture reconciliation** — PASS FOR CURRENT SCOPE. No replacement architecture required; one shared present-state primitive serves both consequence-bearing runtime paths.
2. **State materialization** — SOURCE INSTALLED AND HOSTED-VALIDATED through `5fe92fd...`.
3. **Runtime enforcement** — SOURCE INSTALLED AND HOSTED-VALIDATED; authentic resident InTr/StegGate execution proof remains pending.
4. **Receipt proof** — SOURCE RECEIPT SHAPE INSTALLED AND HOSTED-VALIDATED; authentic resident receipt remains pending.
5. **Reconstruction proof** — SOURCE DETERMINISTIC RECONSTRUCTION INSTALLED AND HOSTED-VALIDATED; authentic resident same-execution reconstruction remains pending.
6. **Ecosystem propagation** — PENDING merge plus resident enforcement proof. Publication propagation remains non-authorizing and separate from runtime enforcement.

## No-duplicate-authority boundary

- TV/TVC remain credential authority where credentials are required.
- InTr / canonical commit-governance remains transition authority.
- Heartbeat remains a reference/observability surface, not execution authority.
- Site, Publisher, admissibility-wiki, and Guardian documentation/projection surfaces do not become execution authority merely by propagation.
- This goal reuses existing StegCore/StegGate and resident execution ownership rather than creating a competing evaluator or executor.

## FULLY ENFORCED gate

Do not claim FULLY ENFORCED until all are evidenced:

1. canonical commit state reconstructably binds authority and temporal state;
2. exact resident commit path consumes that state;
3. negative cases cover revoked/stale authority, changed target, expired temporal condition, missing material state, and stale evidence;
4. authentic resident execution emits a present-state enforcement receipt;
5. same-execution reconstruction reproduces the resident decision from durable evidence without repeating the consequence;
6. downstream targets have target-native propagation evidence or a named durable machine-owned continuation where runtime enforcement is outside their authority domain;
7. README and this handoff remain current;
8. no duplicate execution, credential, or publication authority is introduced.

## Current evidence / lineage

- Task Registry fragment: `StegVerse-Labs/.github/control/worker-registry.d/pa001-ecosystem-runtime-enforcement-001.json`
- Registry commit: `a6c35cf87329cb4c444cc55266b3c5a8782daec8`
- Tracking issue: `StegVerse-Labs/StegCore#208`
- Source PR: `StegVerse-Labs/StegCore#209`
- shared present-state evaluator: `9981ff3d7ca6cee3090f14fb04a86bc6e9f93751`
- direct runtime shared-evaluator integration: `ee5cabd15e46c363329fca6abaa02140c38d3aa5`
- StegGate runtime present-state integration: `6d6f8c664e78bf2070451da4edab2e9fd286ad00`
- portable traversal binding: `0c8574648a91f302c8d0d14244c49b9a16876ed1`
- transaction fixture binding: `6679c3161d1fe5e1c8fc65ef570a1cc4d364a86f`
- neural fixture binding: `2b37139198e0faa463f0afa6e065edbe6e0670b4`
- deterministic reconstruction regression: `5fe92fdca8e61128cf7fe6a9ff238a52f4b3f5d0`

## Next executable actions

1. Observe exact-head CI for this handoff update; repair any regression.
2. When exact-head validation is green, mark PR #209 ready and merge the source-enforcement slice.
3. Reconcile `main` and this handoff to the exact merge commit.
4. Locate and read the current resident InTr/StegGate execution owner/handoff; bind the merged present-state contract into that existing owner rather than creating a competing executor.
5. Produce one authentic resident decision receipt plus same-execution reconstruction evidence.
6. Only after resident proof create/advance target-native propagation verification for Site, Publisher, admissibility-wiki, and stegguardian-wiki as applicable.

## Manual work

None.
