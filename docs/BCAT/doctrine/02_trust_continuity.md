# Trust Continuity

Trust continuity is the property that trust in an actor or system remains coherent
over time, across changing conditions, custody transitions, and operational states.

Trust continuity is distinct from identity, authentication, and authorization.

A system may remain authenticated and authorized while trust continuity has silently
broken.

## Trust as a Temporal Property

Traditional security models treat trust as a point-in-time decision.
BCAT treats trust as a state that must persist.

Trust continuity requires:
- Consistent operational context
- Coherent custody and responsibility
- Temporal alignment between assumptions and action

When these conditions degrade, trust continuity weakens even if permissions remain valid.

## Continuity Breaks

A continuity break occurs when:
- The context under which authority was granted no longer holds
- Custody transitions without acknowledgment
- Temporal assumptions drift beyond acceptable bounds

Continuity breaks are often silent and non-fatal under traditional models.

BCAT treats continuity breaks as first-class signals.

## Relationship to Authority

Authority depends on trust continuity.

When trust continuity degrades:
- Authority may be constrained
- Authority may degrade
- Authority may be revoked

This can occur without authentication failure or policy violation.

Trust continuity enables systems to reason about *when they should stop acting*.
