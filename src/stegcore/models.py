from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Optional, Any
import uuid


@dataclass
class NodeState:
    """
    Snapshot of a node's (service/entity/device) current state.

    Examples of nodes:
    - "CosDenOS"
    - "SCW"
    - "StegVerseNavigator"
    - "CosDenVisionDevice-123"
    """
    status: str  # e.g. "healthy", "degraded", "down"
    version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["updated_at"] = self.updated_at.isoformat()
        return d


@dataclass
class StateEvent:
    """
    Append-only record of a change to a node's state.

    This is the core building block of StegCore's truth layer.
    """
    id: str
    node: str
    status: str
    version: Optional[str]
    reason: str
    metadata: Dict[str, Any]
    timestamp: datetime

    @staticmethod
    def create(
        node: str,
        state: NodeState,
        reason: str,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> "StateEvent":
        md = dict(state.metadata)
        if extra_metadata:
            md.update(extra_metadata)
        return StateEvent(
            id=str(uuid.uuid4()),
            node=node,
            status=state.status,
            version=state.version,
            reason=reason,
            metadata=md,
            timestamp=datetime.now(timezone.utc),
        )

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "id": self.id,
            "node": self.node,
            "status": self.status,
            "version": self.version,
            "reason": self.reason,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }
        return d
