# Commit Coherence Contract

## Purpose

StegCore must preserve interface freedom while ensuring that every consequence-bearing human or AI commit is accountable, transparent, and governable at the moment it becomes real.

The interface is not standardized. The commit contract is.

## Boundary

```text
Any UI / API / human / AI / agent
                |
                v
       Capability declaration
                |
                v
       Existing admissibility
                |
                v
          Coherence gate
                |
          ALLOW or DENY
                |
                v
          State transition
```

No origin may bypass the boundary.

## Capability Surface

The governed abstraction is the capability surface, not visual UI state.

A minimal declaration is:

```json
{
  "actions_exposed": ["example_action"],
  "execution_mode": "manual",
  "requires_governed_commit": true
}
```

Layout, color, device, framework, and control placement remain outside this contract unless they alter effective capability exposure.

The canonicalized capability declaration is hashed and bound to the decision receipt.

## Coherence Invariant

A proposed transition is coherent only when it preserves:

1. **Authority validity** — the transition does not rely on stale, self-invalidating, or laundered authority.
2. **Denial reachability** — consequential continuation cannot escape the next governed decision point.
3. **Governable continuation** — the successor state remains reconstructable and retains resolvable actor, capability, governance, and state bindings.

```text
Coherent(S, C, A, S') =
    AuthorityPreserved(S, A, S')
    AND DenialPreserved(C, A, S')
    AND ContinuationPreserved(S')
```

Any unresolved predicate fails closed.

## Required Ordering

```text
verified continuity input
intent validation
state binding
policy/admissibility decision
capability-surface binding
coherence evaluation
commit decision
execution
receipt emission
```

A preflight-only or post-hoc-only coherence check does not satisfy this contract.

## Receipt Fields

Each coherence decision binds at least:

```json
{
  "decision": "ALLOW",
  "state_hash": "...",
  "capability_hash": "...",
  "coherent": true,
  "coherence_checks": {
    "authority_preserved": true,
    "denial_preserved": true,
    "continuation_preserved": true
  },
  "receipt_hash": "...",
  "previous_receipt_hash": "..."
}
```

A denial identifies the failed predicate or unresolved basis.

## Determinism

For identical bound state, action, capability declaration, authority basis, and policy inputs, the coherence decision must be identical regardless of originating UI, API, device, human, AI, or agent.

## Replay

Independent replay must verify receipt integrity, recompute each coherence predicate from bound inputs, compare the result, and fail closed on mismatch or missing evidence.

## Relationship to Existing StegCore

- `decision.py` remains the existing documentation-aligned allow/deny/defer interface.
- `commit_governance.py` adds the execution-boundary invariant.
- StegCore consumes verified continuity evidence but does not verify or mint continuity receipts.
- A production executor should call the coherence gate only after the existing decision path returns allow and immediately before state mutation.

## Non-goals

This contract does not standardize UI design, approve vendors or devices, govern expression, add behavioral scoring, verify identity, or define a universal substantive policy.

It governs consequence, not expression.
