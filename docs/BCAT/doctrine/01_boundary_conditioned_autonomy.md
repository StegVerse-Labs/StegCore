# Boundary-Conditioned Autonomy

Boundary-Conditioned Autonomy defines autonomy as an **earned and revocable capability**
that exists only while explicit boundary conditions remain satisfied.

Unlike traditional autonomous system design — which emphasizes capability,
optimization, and correctness — boundary-conditioned autonomy emphasizes
**legitimacy under constraints**.

## Autonomy as a Conditioned State

In BCAT, an autonomous system is not classified as autonomous or non-autonomous.

Instead, autonomy exists on a conditional basis:

- Autonomy is granted when boundary conditions are satisfied
- Autonomy degrades as boundary conditions weaken
- Autonomy is revoked when boundary conditions are violated

This framing enables graceful degradation rather than catastrophic failure.

## Boundary Conditions

Boundary conditions may include, but are not limited to:
- Trust continuity
- Context stability
- Custody coherence
- Temporal alignment
- Human accountability presence

Boundary conditions are:
- Explicit
- Inspectable
- Subject to revision
- Enforced continuously

They are not static rules, but maintained constraints.

## Why Conditioning Matters

Systems that act correctly in isolation may behave illegitimately at scale.
Boundary conditioning prevents systems from acting beyond the assumptions
under which their authority was granted.

This mirrors historical engineering practices in which systems are trusted
only within defined operational envelopes.

## Non-Action as Success

In BCAT, refusal to act due to boundary degradation is not a failure.
It is a correct and explainable outcome.

Boundary-conditioned autonomy therefore enables:
- Predictable disengagement
- Early degradation
- Human-readable justification for non-action

Autonomy that cannot refuse itself is not governable.
