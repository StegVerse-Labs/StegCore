# StegCore

StegCore decides what actions are permitted, given verified continuity.

StegCore consumes verified continuity output (e.g., from StegID) and answers:

- Can this actor do this now?
- Under what constraints?
- With whose consent?

StegCore may also maintain **internal state/audit signals** about StegVerse nodes
(services, agents, devices) to support orchestration and observability — but it is
**not** the continuity truth system.

## What StegCore does NOT do

StegCore does **not**:
- verify receipts
- mint receipts
- store identity

Continuity receipts and verification belong to StegID.

> ⚠️ StegCore is **not** a medical or diagnostic system. It is infrastructure used
> for orchestration, security, and observability.

## v0.1 Scope (tight)

v0.1 is **documentation-first**. The authoritative spec lives in `/docs`:

- `docs/DECISION_MODEL.md`
- `docs/POLICY_SHAPES.md`
- `docs/WHY_STEGCORE_EXISTS.md`

Code in `src/stegcore/` is scaffolding and substrate for future runtimes. It must
eventually conform to the docs (docs win if there is disagreement).

## Concepts

- **VerifiedReceipt** – verified continuity evidence provided by StegID (input)
- **Actor class** – human / ai / system (context, not identity)
- **Action intent** – structured request describing what is being attempted
- **Decision** – allow / deny / defer + machine-readable reason code
- **Policy shapes** – quorum / guardian / veto / time-lock / escalation (structure only in v0)

### Supporting substrate (non-authoritative in v0)
- **Node** – a service, AI entity, device, or process in StegVerse
- **NodeState** – a snapshot of a node’s status (health, version, metadata)
- **StateEvent** – append-only record describing a node state change
- **StateEngine** – in-memory state graph + event log (scaffolding)

## Quickstart (scaffold: node state signals)

```python
from stegcore import StateEngine, NodeState

engine = StateEngine()

engine.apply_event(
    node="CosDenOS",
    state=NodeState(
        status="healthy",
        version="0.1.0",
        metadata={"endpoint": "https://cosden.stegverse.internal"},
    ),
    reason="initial_register",
)

snapshot = engine.get_node_state("CosDenOS")
print(snapshot)
