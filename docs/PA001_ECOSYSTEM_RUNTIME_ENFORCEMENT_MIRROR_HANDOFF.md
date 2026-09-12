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
runtime_claim: SOURCE_CONVERSION_STARTED_RUNTIME_PROOF_PENDING
release_claim: NOT_YET_PROVEN
```

## Goal

Convert the already implemented and validated PA-001 permission/admissibility invariant into ecosystem-wide runtime enforcement without creating a second governance authority or conflating documentation/publication with execution authority.

## Existing truth

The canonical PA-001 handoff remains `docs/PERMISSION_ADMISSIBILITY_MIRROR_HANDOFF.md`. It proves the semantic contract, deterministic validator, tests, hosted CI evidence, and StegCore semantic integration. It explicitly does not prove resident commit-path enforcement or runtime activation.

## Architecture determination

No architectural incompatibility has been found that prevents ecosystem-wide enforcement. Existing StegCore already has the required composition points: canonical admissibility, commit coherence, a governed runtime wrapper that invokes the executor only after both gates, adapter conformance work, and reconstructable receipt chaining. Existing GTG/RTG/TT doctrine already requires proposal-time and commit-time state to remain distinguishable.

The conversion is therefore an integration/enforcement problem, not a replacement-architecture problem.

Two concrete fail-open/incomplete-state integration defects were found in the first pass:

1. `GovernedRuntime.evaluate_and_execute()` synthesized an approved authority state when callers omitted `authority_resolution`.
2. `GovernedAdapterRequest` carried an authority reference but no present-tense authority resolution, so adapter callers could reach the runtime without providing the state needed to prove current authority.

Neither defect requires a new architecture. Both are being corrected inside the existing governed runtime and adapter path.

## Architectural rule

Authority and time are state variables. A consequence-bearing execution must be decided from reconstructed commit-time state, not from presumed continuity of proposal-time permission or authority.

The enforced commit-time state must include, directly or by cryptographically/reconstructably bound references, at least:

- principal / subject identity,
- authority state and source,
- temporal state / evaluation instant / validity window,
- standing or consent state when required,
- target binding,
- continuity state,
- governing-condition state,
- evidence identity and freshness where material,
- consequence attribution and reconstruction data,
- disposition semantics.

Missing materially required state must not become ALLOW by absence of observed invalidation. The runtime must distinguish at least ALLOW, DENY, DEFER, FAIL_CLOSED, and ERROR where the owning transition contract supports those states.

## Conversion slices implemented on PR #209

### Governed runtime

`src/stegcore/runtime.py` now:

1. no longer synthesizes `approved` authority when no authority state is supplied;
2. represents missing authority explicitly as `status=missing`, causing the existing coherence authority predicate to fail closed before executor invocation;
3. constructs the commit-time pre-state from the exact request, declared execution context, current authority resolution, and evaluation instant;
4. hashes that commit-time state before consequence-bearing execution;
5. binds the exact target and evaluation time into the coherence receipt;
6. preserves the complete commit-state object plus commit-state hash in the receipt for later same-execution reconstruction.

`tests/test_runtime_commit_coherence.py` requires explicit authority for successful execution, proves omitted authority refuses execution, and asserts authority reference, target, evaluation time, and commit-state hash are preserved in the execution receipt.

### Governed adapters

`src/stegcore/runtime_adapters.py` now carries `authority_resolution` as explicit adapter request state and passes it into the single `governed_execute()` path. An `authority_reference` remains an identity/reference binding only; it no longer substitutes for current authority state.

`tests/test_governed_runtime_adapters.py` and `tests/test_governed_runtime_reconciliation.py` now provide explicit current authority for ALLOW fixtures and add negative controls proving missing adapter authority cannot invoke the executor or reconcile as a committed ALLOW.

This remains source implementation. Hosted exact-head validation, merge, resident execution, downstream propagation, and same-execution reconstruction are not yet claimed. At the latest observation, no exact-head workflow run or commit status had appeared for the current branch head.

## Conversion phases

1. **Architecture reconciliation** — IN PROGRESS / first pass found no replacement-architecture blocker; implicit-authority and adapter-state defects identified and source-corrected.
2. **State materialization** — STARTED / authority + evaluation time + target are bound into the StegCore commit-time state; adapter path now carries explicit authority state.
3. **Runtime enforcement** — STARTED AT SOURCE / omitted authority fails closed before executor invocation through direct runtime and governed adapters; resident proof remains pending.
4. **Receipt proof** — SOURCE SHAPE STARTED / commit state is receipt-bound; authentic resident receipt not yet observed.
5. **Reconstruction proof** — PENDING.
6. **Ecosystem propagation** — PENDING after source validation/merge; existing PA-001 publication propagation remains separate and non-authorizing.

## No-duplicate-authority constraint

- TV/TVC remain credential authority where credentials are required.
- InTr / the canonical commit-governance owner remains transition authority.
- Heartbeat is observability/reference, not execution authority.
- Publisher and documentation surfaces do not become execution authority.
- This task attaches to the existing StegCore governed runtime and existing resident execution ownership rather than instantiating a competing evaluator or executor.

## Evidence required for FULLY ENFORCED

FULLY ENFORCED may be claimed only when all are evidenced:

1. canonical runtime state schema includes or reconstructably binds authority and temporal state at commit;
2. exact resident commit path consumes the state;
3. negative cases prove stale/revoked authority, changed target, expired temporal condition, missing material state, and stale evidence cannot silently ALLOW;
4. authentic resident runtime execution emits a receipt for the enforcement decision;
5. same-execution reconstruction reproduces the decision from durable evidence;
6. downstream targets have target-native propagation evidence or a named durable machine-owned continuation where runtime enforcement is not their authority domain;
7. README and canonical handoff are current;
8. no duplicate execution, credential, or publication authority has been introduced.

## Current evidence

- canonical Task Registry fragment on `.github/main`: `control/worker-registry.d/pa001-ecosystem-runtime-enforcement-001.json`
- registry commit: `a6c35cf87329cb4c444cc55266b3c5a8782daec8`
- StegCore tracking issue: `#208`
- StegCore draft PR: `#209`
- initial handoff commit: `7b0083b9cee68ebaf4a8ca3d8d0129be2050577b`
- runtime conversion commit: `d22694c8f0b6415137639ffb1542f0d0dff94e68`
- direct runtime regression-test commit: `070bee26f95a63595192608cf7545671686baf3c`
- adapter authority-state commit: `86f692209029f81a36db9aa7382609de959b2735`
- adapter regression-test commit: `73df4c4bb13027c3b629428bb911eb3678247162`
- reconciliation regression-test commit: `ff688970c6afc679967b2a65df8cf94d8c04f7cd`
- README conversion documentation commit: `219bc0860c87e4936ffa7cd7a6976b325c8e7881`

## Next executable actions

1. Observe exact-head CI for PR #209 and repair every regression caused by removal of implicit authority.
2. Inventory remaining direct `governed_execute()` and `coherence_gate()` callers for synthetic/implicit authority or mere-reference substitution.
3. Extend temporal enforcement from evaluation-time binding to governed validity-window/freshness semantics; expired or indeterminate authority/evidence must not ALLOW.
4. Add explicit changed-target and stale-evidence negative controls against the canonical runtime.
5. Reconcile the resulting state shape with current InTr/StegGate and resident runtime consumers rather than creating a parallel path.
6. After exact-head source validation and merge, execute the existing resident path and preserve authentic runtime + same-execution reconstruction evidence.
7. Only then start target-native ecosystem propagation.

## Manual work

None at this stage.
