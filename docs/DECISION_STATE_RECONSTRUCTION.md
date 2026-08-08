# Decision-State Reconstruction at the Governed Runtime Boundary

Status: runtime integration requirement
Repository: `StegVerse-Labs/StegCore`
Upstream semantic owner: `StegVerse-Labs/ara-admissibility-interop`
Continuity consumer: `StegVerse-Labs/Continuity`

## Runtime rule

`governed_execute()` is not complete if it records only successful ALLOW-to-effect paths.

For every governed transition attempt, StegCore must make the material admissibility outcome reconstructable, including non-executing outcomes. The decision state is part of system reality even when no external mutation occurs.

## Required distinction

Runtime observations must keep three planes distinct:

- **decision reality** — the admissibility/coherence result produced before mutation;
- **execution reality** — whether the executor/target actually committed an effect;
- **observed reality** — what later observation can establish about that effect.

These planes may diverge and the divergence must be preserved rather than normalized away.

## Terminal outcomes

All of the following require durable state:

- `ALLOW` — admission may proceed to commit subject to topology and commit-coherence requirements;
- `DENY` — execution is prohibited for the evaluated transition;
- `REVIEW` — no execution authority is created; any later approved or modified candidate is a new transition;
- `FAIL_CLOSED` — execution is prevented because required evidence, authority, policy applicability, freshness, coherence, or boundary confidence is insufficient or unavailable.

`FAIL_CLOSED` must never be collapsed into `DENY`, because the two outcomes carry different historical and epistemic meaning.

## Minimum runtime reconstruction surface

For every attempt, StegCore should preserve directly or through immutable references:

- canonical candidate hash;
- decision and reason codes;
- references to the exact admissibility/evidence/authority/policy state evaluated;
- applicability and freshness results where provided by the upstream evaluator;
- unresolved or unknown conditions;
- obligation state;
- topology and admission/TTL state where applicable;
- commit attempt state;
- executor invocation state;
- target result or failure;
- pre/post state hashes where supported;
- prior verified receipt pointer when supplied;
- observation result;
- reconciliation result;
- timestamps sufficient to reconstruct relevant validity intervals.

StegCore does not become the authority verifier or continuity receipt minter by preserving these references.

## Lifecycle

The runtime should support reconstruction equivalent to:

```text
PROPOSED
  -> EVALUATED
  -> ALLOW | DENY | REVIEW | FAIL_CLOSED
  -> [if applicable] ADMITTED
  -> COMMIT_ATTEMPTED
  -> COMMITTED | NOT_COMMITTED | COMMIT_UNKNOWN
  -> OBSERVED | NOT_OBSERVED | OBSERVATION_UNKNOWN | DIVERGENT
  -> RECONCILED | UNRESOLVED
```

A non-ALLOW result normally terminates before executor invocation, but it still produces a decision-state record.

## Bypass and coverage

A complete runtime history makes otherwise invisible governance failures detectable.

Example:

```text
Decision: DENY
Observed target effect: present
Reconciliation: GOVERNANCE_BYPASS
```

Without the DENY record, the observed effect cannot be compared against the governing decision and may look like an ordinary mutation.

Likewise:

```text
Decision: ALLOW
Commit: accepted
Observed target effect: absent
Reconciliation: DIVERGENT
```

This distinction is required for coverage and completeness work. An ALLOW receipt alone does not prove that all relevant mutations were mediated by the gate.

## Issue #21 consequence

The governed adapter work owned by issue #21 must preserve non-ALLOW decision-state records in addition to proving callback unreachability before admissibility plus coherence ALLOW.

Adapter conformance should eventually verify:

1. every governed attempt emits or binds a decision-state record;
2. DENY, REVIEW, FAIL_CLOSED, and coherence-denial paths cannot invoke the executor;
3. the non-execution state is explicit rather than inferred from missing output;
4. ALLOW paths bind the originating decision state to commit and observation records;
5. reconciliation can represent divergent effect, missing effect, unknown observation, and governance bypass;
6. prior receipt-chain references remain preserved without treating StegCore as the receipt verifier or minter.

## Cross-repository source

The normative semantic statement lives at:

`StegVerse-Labs/ara-admissibility-interop/admissibility/decision-state-reconstruction.md`

StegCore implements the runtime side of that contract. `StegVerse-Labs/Continuity` preserves reconstruction semantics and chain relationships downstream.
