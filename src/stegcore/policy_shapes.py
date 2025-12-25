from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class QuorumShape:
    threshold: int = 1
    eligible_approvers: List[str] = field(default_factory=list)
    scope: Optional[str] = None
    expiry_seconds: Optional[int] = None
    record: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardianShape:
    guardian_set: List[str] = field(default_factory=list)
    review_mode: str = "approve"  # approve | challenge | block
    scope: Optional[str] = None
    audit_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VetoShape:
    veto_set: List[str] = field(default_factory=list)
    window_seconds: int = 0
    scope: Optional[str] = None
    veto_effect: str = "deny"  # deny | escalate | delay


@dataclass
class TimeLockShape:
    delay_seconds: int = 0
    scope: Optional[str] = None
    reason: Optional[str] = None
    cancel_authority: List[str] = field(default_factory=list)


@dataclass
class EscalationShape:
    levels: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    resolution_modes: List[str] = field(default_factory=lambda: ["approve", "deny", "modify_constraints"])
    handoff_artifacts: Dict[str, Any] = field(default_factory=dict)
