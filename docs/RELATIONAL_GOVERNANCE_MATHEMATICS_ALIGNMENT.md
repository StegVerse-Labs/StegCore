# Relational Governance Mathematics Alignment

Canonical mathematical source: `Admissible-Existence/AE` goal `AE-AUTO-0011`.

StegCore consumes governance mathematics; it does not define causal ontology. This note fixes the runtime interpretation required by the state-manifold formalization while the AE worker derives and validates the full mathematics.

## Runtime semantic invariants

1. `evaluate_admissibility` evaluates a governance relation over a candidate transition. Its result does not decide whether an already-observed causal transition existed.
2. A finer decomposition of a transition does not retroactively replace an established coarse causal transition merely because more intermediate states are observed.
3. A `DENY` or `FAIL_CLOSED` result for one transition does not automatically propagate as lineage contamination to independent later transitions.
4. Any propagation performed by `manifold_governance.py` must be attributable to an explicit declared dependency, conflict, or bundle rule. That is a higher-order governance constraint, not implicit trajectory taint.
5. Bundle disposition is a governance decision about a declared bundle. It does not rewrite the individual causal identities of its member transitions.
6. Classification has enforcement effect only when `governed_steggate_execute` or another explicitly authorized commit/consequence boundary causally changes the reachable response transition.
7. Clock, lease, freshness, or expiry values are governance evidence/state only when the applicable policy explicitly consumes them; they are not primitive transition-identity variables.

## Mapping to current planner

For population `P={tau_i}` over a frozen base manifold, StegCore computes individual canonical standings

`q_i = A_G(tau_i)`

and then explicit planner relations

`D subset P x P` (dependencies),
`C subset P x P` (conflicts), and
`B : P -> bundle_id`.

The resulting plan is therefore

`Plan(P,G,D,C,B)`

rather than a causal theorem about the trajectory containing `P`.

A dependency effect such as

`q_j = FAIL_CLOSED` and `(tau_j,tau_i) in D`

may cause the planner to fail closed for `tau_i` because `D` is an explicit governance relation. The same result must not be inferred when no dependency, conflict, bundle, or lineage rule relates the transitions.

## Future proof obligation

When AE-AUTO-0011 reaches a validated state, this note must bind to the exact formal definitions for:

- admissible refinement maps;
- governor-indexed transition sets;
- explicit lineage operators;
- decomposition-sensitive governance;
- classification/enforcement separation;
- RTG/TT/STCM/GTG composition.

If those definitions reveal a runtime mismatch, correction requires a distinct StegCore implementation claim and regression evidence. Until then, the existing released manifold kernel remains canonical.
