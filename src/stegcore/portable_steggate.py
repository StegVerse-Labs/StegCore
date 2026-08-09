from __future__ import annotations

"""Portable, ephemeral StegGate micro-node execution.

A governed package carries the exact admissibility request plus a manifest that
pins the StegGate runtime profile/fingerprint required to evaluate it.  The
receiving environment instantiates an ephemeral micro-node from its installed,
known StegCore implementation; the package does not gain authority merely by
transporting executable bytes.

The micro-node is intentionally short-lived: validate package/runtime binding,
evaluate the canonical three-layer StegGate chain, optionally cross the existing
commit-coherence boundary, emit reconstructable evidence, and terminate.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Literal, Mapping, Optional, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

from .steggate import AdmissibilityEvaluation, AdmissibilityRequest, canonical_sha256, evaluate_admissibility
from .steggate_runtime import StegGateExecutionObservation, governed_steggate_execute

T = TypeVar("T")

PORTABLE_PROFILE = "steggate.portable-micronode.v1"
RUNTIME_PROFILE = "stegcore.reconciled-three-layer.v1"
_RUNTIME_COMPONENTS = (
    "three_layer.py",
    "steggate.py",
    "steggate_runtime.py",
    "commit_governance.py",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def runtime_fingerprint() -> str:
    """Fingerprint the canonical implementation components used by the micro-node."""

    base = Path(__file__).resolve().parent
    digest = hashlib.sha256()
    for name in _RUNTIME_COMPONENTS:
        path = base / name
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


class MicroNodeManifest(BaseModel):
    profile: Literal["steggate.portable-micronode.v1"] = PORTABLE_PROFILE
    runtime_profile: Literal["stegcore.reconciled-three-layer.v1"] = RUNTIME_PROFILE
    runtime_fingerprint: str = Field(min_length=64, max_length=64)
    required_capabilities: tuple[str, ...] = (
        "three_layer_admissibility",
        "complete_decision_state",
        "commit_coherence",
        "effect_observation",
    )
    expires_at: Optional[str] = None


class GovernedTransitionPackage(BaseModel):
    artifact_type: Literal["stegcore.governed_transition_package"] = "stegcore.governed_transition_package"
    schema_version: Literal["1.0"] = "1.0"
    package_id: str = Field(min_length=1)
    micronode: MicroNodeManifest
    admissibility_request: AdmissibilityRequest
    declared_execution_context: dict[str, Any] = Field(default_factory=dict)
    capability_surface: dict[str, Any] = Field(default_factory=dict)
    authority_resolution: dict[str, Any] = Field(default_factory=dict)
    package_hash: Optional[str] = None

    def canonical_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"package_hash"}, exclude_none=False)

    def computed_hash(self) -> str:
        return canonical_sha256(self.canonical_payload())


@dataclass(frozen=True)
class PortableMicroNodeReceipt:
    artifact_type: Literal["stegcore.portable_micronode_receipt"]
    schema_version: Literal["1.0"]
    node_instance_id: str
    package_id: str
    package_hash: str
    runtime_profile: str
    runtime_fingerprint: str
    state: Literal["EVALUATED", "EXECUTED", "REFUSED", "FAIL_CLOSED", "FAILED"]
    evaluation: Optional[dict[str, Any]]
    execution_observation: Optional[dict[str, Any]]
    fail_closed_reason: Optional[str]
    instantiated_at: str
    terminated_at: str
    receipt_hash: str


def create_governed_package(
    *,
    package_id: str,
    request: AdmissibilityRequest,
    expires_at: Optional[str] = None,
    declared_execution_context: Optional[Mapping[str, Any]] = None,
    capability_surface: Optional[Mapping[str, Any]] = None,
    authority_resolution: Optional[Mapping[str, Any]] = None,
) -> GovernedTransitionPackage:
    """Create a transportable package pinned to the locally installed canonical runtime."""

    package = GovernedTransitionPackage(
        package_id=package_id,
        micronode=MicroNodeManifest(runtime_fingerprint=runtime_fingerprint(), expires_at=expires_at),
        admissibility_request=request,
        declared_execution_context=dict(declared_execution_context or {}),
        capability_surface=dict(capability_surface or {}),
        authority_resolution=dict(authority_resolution or {}),
    )
    package.package_hash = package.computed_hash()
    return package


def _expired(expires_at: Optional[str]) -> bool:
    if not expires_at:
        return False
    try:
        expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) >= expiry.astimezone(timezone.utc)


def _receipt(
    *,
    node_instance_id: str,
    package: GovernedTransitionPackage,
    state: Literal["EVALUATED", "EXECUTED", "REFUSED", "FAIL_CLOSED", "FAILED"],
    instantiated_at: str,
    evaluation: Optional[AdmissibilityEvaluation] = None,
    observation: Optional[StegGateExecutionObservation[Any]] = None,
    fail_closed_reason: Optional[str] = None,
) -> PortableMicroNodeReceipt:
    terminated_at = datetime.now(timezone.utc).isoformat()
    body: dict[str, Any] = {
        "artifact_type": "stegcore.portable_micronode_receipt",
        "schema_version": "1.0",
        "node_instance_id": node_instance_id,
        "package_id": package.package_id,
        "package_hash": package.computed_hash(),
        "runtime_profile": RUNTIME_PROFILE,
        "runtime_fingerprint": runtime_fingerprint(),
        "state": state,
        "evaluation": evaluation.model_dump(mode="json") if evaluation else None,
        "execution_observation": asdict(observation) if observation else None,
        "fail_closed_reason": fail_closed_reason,
        "instantiated_at": instantiated_at,
        "terminated_at": terminated_at,
    }
    receipt_hash = hashlib.sha256(_canonical(body)).hexdigest()
    return PortableMicroNodeReceipt(**body, receipt_hash=receipt_hash)


def evaluate_governed_package(package: GovernedTransitionPackage) -> PortableMicroNodeReceipt:
    """Instantiate an evaluation-only micro-node and terminate after recording the decision state."""

    instantiated_at = datetime.now(timezone.utc).isoformat()
    node_id = f"SGMU-{uuid4()}"
    local_fingerprint = runtime_fingerprint()
    if package.package_hash != package.computed_hash():
        return _receipt(node_instance_id=node_id, package=package, state="FAIL_CLOSED", instantiated_at=instantiated_at, fail_closed_reason="package_hash_mismatch")
    if package.micronode.runtime_fingerprint != local_fingerprint:
        return _receipt(node_instance_id=node_id, package=package, state="FAIL_CLOSED", instantiated_at=instantiated_at, fail_closed_reason="runtime_fingerprint_mismatch")
    if _expired(package.micronode.expires_at):
        return _receipt(node_instance_id=node_id, package=package, state="FAIL_CLOSED", instantiated_at=instantiated_at, fail_closed_reason="package_expired_or_expiry_invalid")

    evaluation = evaluate_admissibility(package.admissibility_request)
    state: Literal["EVALUATED", "REFUSED", "FAIL_CLOSED"]
    if evaluation.disposition == "FAIL_CLOSED":
        state = "FAIL_CLOSED"
    elif evaluation.disposition == "ALLOW":
        state = "EVALUATED"
    else:
        state = "REFUSED"
    return _receipt(node_instance_id=node_id, package=package, state=state, instantiated_at=instantiated_at, evaluation=evaluation)


def execute_governed_package(package: GovernedTransitionPackage, executor: Callable[[], T]) -> PortableMicroNodeReceipt:
    """Instantiate a micro-node, execute only after canonical ALLOW+coherence ALLOW, then terminate."""

    instantiated_at = datetime.now(timezone.utc).isoformat()
    node_id = f"SGMU-{uuid4()}"
    local_fingerprint = runtime_fingerprint()
    if package.package_hash != package.computed_hash():
        return _receipt(node_instance_id=node_id, package=package, state="FAIL_CLOSED", instantiated_at=instantiated_at, fail_closed_reason="package_hash_mismatch")
    if package.micronode.runtime_fingerprint != local_fingerprint:
        return _receipt(node_instance_id=node_id, package=package, state="FAIL_CLOSED", instantiated_at=instantiated_at, fail_closed_reason="runtime_fingerprint_mismatch")
    if _expired(package.micronode.expires_at):
        return _receipt(node_instance_id=node_id, package=package, state="FAIL_CLOSED", instantiated_at=instantiated_at, fail_closed_reason="package_expired_or_expiry_invalid")

    observation = governed_steggate_execute(
        package.admissibility_request,
        executor,
        declared_execution_context=package.declared_execution_context,
        capability_surface=package.capability_surface,
        authority_resolution=package.authority_resolution,
    )
    if observation.status == "executed":
        state = "EXECUTED"
    elif observation.status == "failed":
        state = "FAILED"
    elif observation.evaluation.disposition == "FAIL_CLOSED":
        state = "FAIL_CLOSED"
    else:
        state = "REFUSED"
    return _receipt(
        node_instance_id=node_id,
        package=package,
        state=state,
        instantiated_at=instantiated_at,
        evaluation=observation.evaluation,
        observation=observation,
    )
