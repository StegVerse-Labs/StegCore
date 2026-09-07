# Authority × Time Governance Coordinate — StegCore Runtime Binding

Status: runtime semantic correction coordinated by `StegVerse-Labs/.github#1154` and `StegVerse-Labs/StegCore#188`.

Canonical governance coordinate:

```text
G = (Authority, Time)
```

StegCore evaluates runtime transitions at this coordinate. State, policy, identity, delegation, evidence, context, dependencies, recoverability, and transition geometry are evaluated inputs; they do not replace either coordinate.

The following remain true:

```text
Time != Authority
wall-clock observation != Authority
heartbeat cadence != Authority
elapsed time alone -/-> authority change
observation != authorization
```

These statements must not be read as `Time != governance`. Time is a governance coordinate; clock observations are representations/evidence associated with it.

A protected boundary crossing therefore requires resolution of the applicable Authority at the applicable Time, followed by the canonical StegGate admissibility evaluation of the transition context at that coordinate.

ALLOW/DENY/REVIEW/FAIL_CLOSED are dispositions produced by governed evaluation. They do not manufacture Authority or Time.
