from __future__ import annotations

from typing import Dict, List, Optional

from .models import NodeState, StateEvent


class StateEngine:
    """
    In-memory state graph + append-only event log for StegVerse nodes.

    This does NOT impose a specific storage backend – it can be wrapped by
    adapters that persist events/states as needed (files, DB, etc.).
    """

    def __init__(self) -> None:
        # Latest known state per node
        self._nodes: Dict[str, NodeState] = {}
        # Append-only event log (in memory)
        self._events: List[StateEvent] = []

    # -------------------------
    # Events + state application
    # -------------------------

    def apply_event(
        self,
        node: str,
        state: NodeState,
        reason: str,
        extra_metadata: Optional[Dict[str, object]] = None,
    ) -> StateEvent:
        """
        Apply a new state for a node. Creates and records a StateEvent.
        """
        event = StateEvent.create(
            node=node,
            state=state,
            reason=reason,
            extra_metadata=extra_metadata,
        )
        self._events.append(event)
        self._nodes[node] = state
        return event

    # -------------------------
    # Read state / events
    # -------------------------

    def get_node_state(self, node: str) -> Optional[NodeState]:
        return self._nodes.get(node)

    def list_nodes(self) -> Dict[str, NodeState]:
        return dict(self._nodes)

    def list_events(self) -> List[StateEvent]:
        return list(self._events)

    def list_events_for_node(self, node: str) -> List[StateEvent]:
        return [e for e in self._events if e.node == node]

    # -------------------------
    # Convenience helpers
    # -------------------------

    def upsert_node(
        self,
        node: str,
        status: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
        reason: str = "update",
    ) -> StateEvent:
        m = metadata or {}
        state = NodeState(status=status, version=version, metadata=m)
        return self.apply_event(node=node, state=state, reason=reason)

    def mark_healthy(
        self,
        node: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
        reason: str = "health_check",
    ) -> StateEvent:
        return self.upsert_node(
            node=node,
            status="healthy",
            version=version,
            metadata=metadata,
            reason=reason,
        )

    def mark_degraded(
        self,
        node: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
        reason: str = "degraded",
    ) -> StateEvent:
        return self.upsert_node(
            node=node,
            status="degraded",
            version=version,
            metadata=metadata,
            reason=reason,
        )

    def mark_down(
        self,
        node: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
        reason: str = "down",
    ) -> StateEvent:
        return self.upsert_node(
            node=node,
            status="down",
            version=version,
            metadata=metadata,
            reason=reason,
        )
