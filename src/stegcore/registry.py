from __future__ import annotations

from typing import Dict, Optional

from .models import NodeState, StateEvent
from .state_engine import StateEngine


class Registry:
    """
    Helper API for StegVerse services, AI entities, and devices to announce
    their presence and emit state/audit signals.

    Registry is a convenience layer over StateEngine.
    It does NOT:
    - verify continuity
    - enforce policy
    - execute actions

    It simply records state transitions as append-only events.
    """

    def __init__(self, engine: StateEngine) -> None:
        self.engine = engine

    # -------------------------
    # Registration / liveness
    # -------------------------

    def register(
        self,
        node: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
    ) -> StateEvent:
        """
        Register a node as healthy.

        Intended for first appearance or startup.
        """
        state = NodeState(
            status="healthy",
            version=version,
            metadata=metadata or {},
        )
        return self.engine.apply_event(
            node=node,
            state=state,
            reason="register",
        )

    def heartbeat(
        self,
        node: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
    ) -> StateEvent:
        """
        Emit a liveness signal for an existing node.
        """
        state = NodeState(
            status="healthy",
            version=version,
            metadata=metadata or {},
        )
        return self.engine.apply_event(
            node=node,
            state=state,
            reason="heartbeat",
        )

    # -------------------------
    # Degradation / failure
    # -------------------------

    def mark_degraded(
        self,
        node: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
    ) -> StateEvent:
        """
        Mark a node as degraded.
        """
        state = NodeState(
            status="degraded",
            version=version,
            metadata=metadata or {},
        )
        return self.engine.apply_event(
            node=node,
            state=state,
            reason="degraded",
        )

    def mark_down(
        self,
        node: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
    ) -> StateEvent:
        """
        Mark a node as down or unreachable.
        """
        state = NodeState(
            status="down",
            version=version,
            metadata=metadata or {},
        )
        return self.engine.apply_event(
            node=node,
            state=state,
            reason="down",
        )

    # -------------------------
    # Read helpers
    # -------------------------

    def get_state(self, node: str) -> Optional[NodeState]:
        """
        Return the latest known state for a node, if any.
        """
        return self.engine.get_node_state(node)
