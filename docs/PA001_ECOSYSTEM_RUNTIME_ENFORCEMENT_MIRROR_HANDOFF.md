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
runtime_claim: SOURCE_PRESENT_STATE_ENFORCEMENT_INSTALLED_CURRENT_HEAD_VALIDATION_RUNNING
release_claim: NOT_YET_PROVEN
```

## Goal

Convert the already implemented and validated PA-001 permission/admissibility invariant into ecosystem-wide runtime enforcement without creating a second governance authority or conflating documentation/publication with execution authority.

## Existing truth

The canonical PA-001 handoff remains `docs/PERMISSION_ADMISSIBILITY_MIRROR_HANDOFF.md`. It proves the semantic contract, deterministic validator, tests, hosted CI evidence, and StegCore semantic integration. It explicitly does not prove resident commit-path enforcement or runtime activation.

## Architecture determination

No architectural incompatibility has been found that prevents ecosystem-wide enforcement. Existing StegCore already has the required composition points: canonical admissibility, commit coherence, governed runtime wrappers, StegGate execution composition, adapter conformance, and reconstructable receipt chaining. Existing GTG/RTG/TT doctrine already requires proposal-time and commit-time state to remain distinguishable.

The conversion is therefore an integration/enforcement problem, not a replacement-architecture problem.

Two fail-open/incomplete-state defects were confirmed in the first pass and corrected at source:

1. `GovernedRuntime.evaluate_and_execute()` synthesized an approved authority state when callers omitted `authority_resolution`.
2. `GovernedAdapterRequest` carried an authority reference but no present-tense authority resolution, allowing mere-reference substitution for current authority state.

The second pass found a broader consistency requirement: direct governed runtime and StegGate runtime must not maintain separate present-state semantics. Present-state evaluation is therefore now centralized in `src/stegcore/commit_governance.py` and reused by both consequence-bearing paths.

## Architectural rule

Authority and time are state variables. A consequence-bearing execution must be decided from reconstructed commit-time state, not from presumed continuity of proposal-time permission or authority.

The enforced commit-time state must include, directly or by reconstructably bound references, at least:

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

Missing materially required state must not become ALLOW by absence of observed invalidation. Explicit negative state and indeterminate state remain distinct: explicit negative state produces `DENY`; missing or indeterminate required state produces `FAIL_CLOSED`.

## Conversion slices implemented on PR #209

### Shared present-state evaluator

`src/stegcore/commit_governance.py` now exposes one reusable `evaluate_present_state()` primitive used by both governed execution paths. It does not grant authority or replace policy/admissibility evaluation. It checks:

- current authority status;
- authority-to-target binding;
- authority validity window, or explicit unbounded temporal scope;
- evidence freshness from exact evidence validity timestamps or an already-governed current-evidence finding;
- explicit negative versus indeterminate state semantics.

### Direct governed runtime

`src/stegcore/runtime.py` now:

1. no longer synthesizes `approved` authority when authority state is absent;
2. constructs the commit-time pre-state from the exact request, declared execution context, supplied authority state, and evaluation instant;
3. uses the shared present-state evaluator before commit coherence;
4. requires exact authority target binding;
5. enforces bounded authority validity windows;
6. requires continuity evidence freshness through `VerifiedReceiptEnvelope.valid_until`;
7. returns `DENY` for explicitly stale/expired/mismatched state and `FAIL_CLOSED` for materially unestablished state;
8. preserves present-state checks, reasons, target, evaluation time, complete commit state, and commit-state hash in the receipt;
9. leaves the executor unreachable unless admissibility, present-state evaluation, and coherence all permit execution.

`src/stegcore/decision.py` adds optional `valid_until` to the verified continuity envelope. The structural decision interface remains compatible; consequence-bearing runtime enforcement is what requires freshness to be established.

### Governed adapters

`src/stegcore/runtime_adapters.py` carries explicit `authority_resolution` and preserves runtime `FAIL_CLOSED` separately from `DENY`. An authority reference is only an identity/reference binding; it does not substitute for current authority state.

Adapter and reconciliation regressions now prove missing authority cannot execute, cannot become committed ALLOW, and reconciles an externally observed effect as governance bypass.

### Canonical StegGate execution runtime

`src/stegcore/steggate_runtime.py` now consumes the same shared present-state evaluator before commit coherence. For an otherwise canonical StegGate ALLOW:

- missing authority -> `FAIL_CLOSED` before executor;
- changed authority target -> `DENY` before executor;
- expired authority -> `DENY` before executor;
- current target/time/authority/evidence state -> proceeds to the existing coherence gate.

The exact StegGate request, authority state, evaluation time, target, decision-state hash, present-state checks, and commit-state hash are receipt-bound.

### Fixtures and dependent paths

The portable SDK/SPE/Interlock bounded traversal, neural governed path, manifested-transaction discovery fixture, direct runtime tests, adapter tests, reconciliation tests, and StegGate runtime tests have been updated to provide explicit target- and time-bound authority state rather than historical/implicit approval.

## Validation evidence

The earlier conversion head `df788b0f54138f42810399f42a564c548b8e3912` passed:

- `Verify Production Runtime Coherence` run `34708563701` — SUCCESS;
- `StegCore Package Version Identity Validation` run `34708563683` — SUCCESS.

Those runs validate the first source slice only and do not validate the newer temporal/target/freshness changes.

Current source head before this handoff update: `2b37139198e0faa463f0afa6e065edbe6e0670b4`.

Current exact-head workflows observed in progress/queued:

- Neural End-to-End Governance `34713552543` — IN_PROGRESS;
- SPE Standing Canonical Binding Validation `34713552535` — IN_PROGRESS;
- StegCore Package Version Identity Validation `34713552542` — IN_PROGRESS;
- Verify Production Runtime Coherence `34713552582` — IN_PROGRESS;
- Verify Commit Coherence `34713552540` — QUEUED.

No success claim is made for the current source head until these exact-head runs complete and any discovered regressions are repaired.

## Conversion phases

1. **Architecture reconciliation** — PASS FOR CURRENT SCOPE / no replacement-architecture blocker found; one shared present-state primitive now serves direct and StegGate consequence paths.
2. **State materialization** — SOURCE INSTALLED / authority, target, evaluation time, authority validity, and evidence freshness are bound into current commit state.
3. **Runtime enforcement** — SOURCE INSTALLED / missing authority/freshness fails closed; changed target and expired/stale state deny before executor. Authentic resident proof remains pending.
4. **Receipt proof** — SOURCE SHAPE INSTALLED / present-state and commit-state evidence are receipt-bound; authentic resident receipt not yet observed.
5. **Reconstruction proof** — PENDING authentic same-execution reconstruction.
6. **Ecosystem propagation** — PENDING source validation/merge and resident enforcement proof; existing PA-001 publication propagation remains separate and non-authorizing.

## No-duplicate-authority constraint

- TV/TVC remain credential authority where credentials are required.
- InTr / canonical commit-governance remains transition authority.
- Heartbeat remains observability/reference, not execution authority.
- Publisher and documentation surfaces do not become execution authority.
- This task reuses the existing StegCore/StegGate execution composition and existing resident execution ownership rather than instantiating a competing evaluator or executor.

## Evidence required for FULLY ENFORCED

FULLY ENFORCED may be claimed only when all are evidenced:

1. canonical runtime state includes or reconstructably binds authority and temporal state at commit;
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
- first source validation head: `df788b0f54138f42810399f42a564c548b8e3912`
- shared present-state evaluator commit: `9981ff3d7ca6cee3090f14fb04a86bc6e9f93751`
- governed runtime shared-evaluator integration: `ee5cabd15e46c363329fca6abaa02140c38d3aa5`
- StegGate runtime present-state integration: `6d6f8c664e78bf2070451da4edab2e9fd286ad00`
- StegGate present-state regressions: `6f635fd18d23eef3fcce3b18d19f3cdc1b37cd3e`
- portable traversal present-state binding: `0c8574648a91f302c8d0d14244c49b9a16876ed1`
- manifested transaction fixture present-state binding: `6679c3161d1fe5e1c8fc65ef570a1cc4d364a86f`
- neural fixture present-state binding: `2b37139198e0faa463f0afa6e065edbe6e0670b4`

## Next executable actions

1. Observe all exact-head workflows for the current branch and repair every regression caused by the stronger present-state contract.
2. Inspect any remaining StegGate/transaction/portable fixture that still supplies historical-only authority and convert it to explicit target/time state where ALLOW is intended.
3. Add deterministic reconstruction validation proving a receipt's commit-state hash and present-state disposition can be recomputed from the retained state object without invoking the consequence.
4. Update README with the shared present-state enforcement contract after exact-head validation confirms the public description is accurate.
5. Merge PR #209 only after exact-head validation is green and the handoff records the exact validated head.
6. Then bind this source contract into the existing resident InTr/StegGate execution owner and preserve one authentic runtime receipt plus same-execution reconstruction evidence.
7. Only after resident proof begin target-native propagation to Site, Publisher, admissibility-wiki, and Guardian.

## Manual work

None at this stage.
