from __future__ import annotations

from typing import Dict, Optional

from .models import NodeState
from .state_engine import StateEngine


class Registry:
    """
    Helper API for StegVerse services/AI entities to register their presence
    and update their status in the StateEngine.

    This is what CosDenOS, SCW, PatentAI, etc. would talk to in-process or
    via a thin HTTP layer later.
    """

    def __init__(self, engine: StateEngine) -> None:
        self.engine = engine

    def register(
        self,
        node: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        self.engine.upsert_node(
            node=node,
            status="healthy",
            version=version,
            metadata=metadata,
            reason="register",
        )

    def heartbeat(
        self,
        node: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        self.engine.upsert_node(
            node=node,
            status="healthy",
            version=version,
            metadata=metadata,
            reason="heartbeat",
        )

    def mark_degraded(
        self,
        node: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        self.engine.mark_degraded(
            node=node,
            version=version,
            metadata=metadata,
            reason="degraded",
        )

    def mark_down(
        self,
        node: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        self.engine.mark_down(
            node=node,
            version=version,
            metadata=metadata,
            reason="down",
        )

    def get_state(self, node: str) -> Optional[NodeState]:
        return self.engine.get_node_state(node)
