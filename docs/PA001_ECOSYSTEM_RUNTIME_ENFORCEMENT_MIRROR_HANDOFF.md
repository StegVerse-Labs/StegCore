# PA-001 Ecosystem Runtime Enforcement Mirror Handoff

## Status

```text
provisional_goal_id: PA-001-ECOSYSTEM-RUNTIME-ENFORCEMENT-001
repository: StegVerse-Labs/StegCore
branch: pa001-ecosystem-runtime-enforcement
issue: #208
state: ACTIVE
runtime_claim: NOT_YET_PROVEN
release_claim: NOT_YET_PROVEN
```

## Goal

Convert the already implemented and validated PA-001 permission/admissibility invariant into ecosystem-wide runtime enforcement without creating a second governance authority or conflating documentation/publication with execution authority.

## Existing truth

The canonical PA-001 handoff remains `docs/PERMISSION_ADMISSIBILITY_MIRROR_HANDOFF.md`. It proves the semantic contract, deterministic validator, tests, hosted CI evidence, and StegCore semantic integration. It explicitly does not prove resident commit-path enforcement or runtime activation.

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

## Conversion phases

1. **Architecture reconciliation** — verify existing commit-governance, GTG/RTG/TT, InTr, TV/TVC, and resident-runtime contracts can carry the required present-tense state without introducing duplicate authority.
2. **State materialization** — bind authority/time/target/standing/continuity/governing-condition inputs into the canonical commit-time state object or references consumed by the existing decision path.
3. **Runtime enforcement** — make the resident consequence-bearing commit path consume that state and refuse/defer/fail closed when current admissibility cannot be established.
4. **Receipt proof** — emit an authentic runtime receipt identifying the evaluated state, governing evidence, disposition, and exact execution/commit relationship; no synthetic success receipts.
5. **Reconstruction proof** — reconstruct the same-execution determination from durable evidence.
6. **Ecosystem propagation** — propagate the enforcement contract to Site, Publisher, admissibility-wiki, and Guardian through their canonical handoffs without granting those surfaces execution authority.

## No-duplicate-authority constraint

- TV/TVC remain credential authority where credentials are required.
- InTr / the canonical commit-governance owner remains transition authority.
- Heartbeat is observability, not execution authority.
- Publisher and documentation surfaces do not become execution authority.
- This task must attach to existing resident execution ownership rather than instantiate a competing executor.

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

## Current work

- Branch created: `pa001-ecosystem-runtime-enforcement`.
- Tracking issue created: `StegVerse-Labs/StegCore#208`.
- This handoff created before implementation mutation so the conversion has a durable continuation surface.
- Runtime code has not yet been changed and no runtime enforcement claim is made.

## Next executable actions

1. Verify the canonical Goal Task ID in the GitHub Task Registry and replace the provisional ID above if necessary.
2. Inspect the current commit-governance / InTr / GTG runtime path and its state schema.
3. Identify the narrowest existing state object and enforcement hook; do not create a second evaluator if one already exists.
4. Add failing tests for authority/time/target drift before implementation.
5. Implement the smallest non-authorizing adapter/state extension needed to feed current state into the canonical commit path.
6. Run exact-head validation and update this handoff with evidence.

## Manual work

None at this stage.
