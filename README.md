# StegCore

StegCore is the **state engine and truth layer** for the StegVerse ecosystem.

Its responsibilities:

- Track the current state of StegVerse services, AI entities, and devices.
- Provide an append-only event log (`StateEvent`) for changes.
- Offer a simple registry API so other services can announce their status.
- Act as a *logical* source of truth (not a database) that can be persisted by
  any storage backend (files, Redis, Postgres, etc.) later.

> ⚠️ StegCore is **not** a medical or diagnostic system. It is an infrastructure
> component used for orchestration, security, and observability.

## Concepts

- **Node** – a service, AI entity, device, or process that participates in StegVerse.
- **State** – a structured snapshot of a node's status (health, version, metadata).
- **StateEvent** – an append-only record describing a change to some node's state.
- **StateEngine** – in-memory state graph + event log.
- **Registry** – helper API for services to register/unregister and publish heartbeats.

## Quickstart (conceptual)

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

Roadmap
	•	Add persistence (file / DB backends)
	•	Add signing / verification of events
	•	Integrate with StegVerse audit and security systems
	•	Expose an HTTP API (FastAPI) for external services to interact with

---

## 4️⃣ `src/stegcore/__init__.py`

```python
from __future__ import annotations

"""
StegCore – central state engine and registry for StegVerse.

This package provides:

- dataclasses / models describing node states and events
- the StateEngine for in-memory state graph + event log
- a Registry helper for service registration and heartbeats
"""

from .models import NodeState, StateEvent
from .state_engine import StateEngine
from .registry import Registry

__all__ = [
    "NodeState",
    "StateEvent",
    "StateEngine",
    "Registry",
]
