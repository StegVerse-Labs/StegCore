from __future__ import annotations

"""Governed mutation-entry adapters for StegCore.

Transport and caller type never confer authority. Every supported entry path is
normalized into the same adapter request, checked for exact execution binding, and
then routed through :func:`stegcore.runtime.governed_execute`.

StegCore consumes already-verified credential/receipt references. It neither verifies
signatures nor mints Continuity receipts here.
"""

from dataclasses import asdict, dataclass, field, replace
from typing import Any, Callable, Generic, Literal, Mapping, Optional, TypeVar

from .commit_governance import canonical_hash
from .decision import DecisionRequest
from .runtime import ExecutionObservation, governed_execute


T = TypeVar("T")
AdapterKind = Literal["ui", "api", "human", "ai", "agent", "batch", "workflow", "replay"]
AdapterState = Literal["executed", "refused", "failed"]
DecisionOutcome = Literal["ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"]
ReconciliationState = Literal["MATCH", "DIVERGENT", "UNKNOWN", "GOVERNANCE_BYPASS", "NOT_APPLICABLE"]


@dataclass(frozen=True)
class ExecutionBinding:
    candidate_id: str
    candidate_hash: str
    credential_id: str
    credential_hash: str
    credential_subject: str
    authority_reference: str
    capability_surface: Mapping[str, Any]
    parameter_bounds: Mapping[str, Any] = field(default_factory=dict)
    previous_receipt_hash: Optional[str] = None


@dataclass(frozen=True)
class GovernedAdapterRequest:
    adapter_kind: AdapterKind
    decision_request: DecisionRequest
    binding: ExecutionBinding
    admitted_binding: ExecutionBinding
    declared_execution_context: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionStateRecord:
    artifact_type: Literal["stegcore.runtime_decision_state"]
    adapter_kind: AdapterKind
    outcome: DecisionOutcome
    phase: Literal["ADAPTER_BINDING", "ADMISSIBILITY", "COMMIT_COHERENCE", "EXECUTION"]
    reason_code: str
    candidate_id: str
    candidate_hash: str
    credential_id: str
    credential_hash: str
    credential_subject: str
    authority_reference: str
    capability_hash: str
    previous_receipt_hash: Optional[str]
    executor_invoked: bool
    commit_state: Literal["NOT_ATTEMPTED", "NOT_COMMITTED", "COMMITTED", "COMMIT_UNKNOWN"]
    observation_state: Literal["NOT_OBSERVED", "OBSERVED", "OBSERVATION_UNKNOWN", "DIVERGENT"]
    reconciliation: ReconciliationState
    decision: Optional[Mapping[str, Any]] = None
    coherence_receipt_hash: Optional[str] = None
    runtime_pre_state_hash: Optional[str] = None
    runtime_post_state_hash: Optional[str] = None


@dataclass(frozen=True)
class AdapterObservation(Generic[T]):
    artifact_type: Literal["stegcore.adapter_observation"]
    status: AdapterState
    decision_state: DecisionStateRecord
    runtime_observation: Optional[ExecutionObservation[T]] = None
    result: Optional[T] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def executed(self) -> bool:
        return self.status == "executed"


def _normalized_surface(surface: Mapping[str, Any]) -> dict[str, Any]:
    normalized = dict(surface)
    normalized["actions_exposed"] = sorted(str(v) for v in normalized.get("actions_exposed", []))
    if "parameter_bounds" in normalized and isinstance(normalized["parameter_bounds"], Mapping):
        normalized["parameter_bounds"] = dict(normalized["parameter_bounds"])
    return normalized


def _binding_failures(request: GovernedAdapterRequest) -> list[str]:
    supplied = request.binding
    admitted = request.admitted_binding
    failures: list[str] = []

    scalar_fields = (
        "candidate_id",
        "candidate_hash",
        "credential_id",
        "credential_hash",
        "credential_subject",
        "authority_reference",
    )
    for field_name in scalar_fields:
        if getattr(supplied, field_name) != getattr(admitted, field_name):
            failures.append(f"{field_name}_mismatch")

    supplied_surface = _normalized_surface(supplied.capability_surface)
    admitted_surface = _normalized_surface(admitted.capability_surface)
    supplied_actions = set(supplied_surface.get("actions_exposed", []))
    admitted_actions = set(admitted_surface.get("actions_exposed", []))
    if not supplied_actions.issubset(admitted_actions):
        failures.append("capability_action_broadening")

    if supplied_surface.get("requires_governed_commit") is not True:
        failures.append("governed_commit_not_required")

    intent = request.decision_request.intent
    if intent is not None:
        if intent.action not in supplied_actions:
            failures.append("unexposed_action")
        bounds = dict(admitted.parameter_bounds or {})
        for key, rule in bounds.items():
            if key not in intent.parameters:
                continue
            value = intent.parameters[key]
            if isinstance(rule, Mapping):
                minimum = rule.get("min")
                maximum = rule.get("max")
                if minimum is not None and value < minimum:
                    failures.append(f"parameter_below_min:{key}")
                if maximum is not None and value > maximum:
                    failures.append(f"parameter_above_max:{key}")

    if supplied.previous_receipt_hash != admitted.previous_receipt_hash:
        failures.append("previous_receipt_pointer_mismatch")

    return failures


def _fail_closed(request: GovernedAdapterRequest, reason: str) -> AdapterObservation[Any]:
    binding = request.binding
    state = DecisionStateRecord(
        artifact_type="stegcore.runtime_decision_state",
        adapter_kind=request.adapter_kind,
        outcome="FAIL_CLOSED",
        phase="ADAPTER_BINDING",
        reason_code=reason,
        candidate_id=binding.candidate_id,
        candidate_hash=binding.candidate_hash,
        credential_id=binding.credential_id,
        credential_hash=binding.credential_hash,
        credential_subject=binding.credential_subject,
        authority_reference=binding.authority_reference,
        capability_hash=canonical_hash(_normalized_surface(binding.capability_surface)),
        previous_receipt_hash=binding.previous_receipt_hash,
        executor_invoked=False,
        commit_state="NOT_ATTEMPTED",
        observation_state="NOT_OBSERVED",
        reconciliation="NOT_APPLICABLE",
    )
    return AdapterObservation(
        artifact_type="stegcore.adapter_observation",
        status="refused",
        decision_state=state,
    )


def _runtime_state(
    request: GovernedAdapterRequest,
    observation: ExecutionObservation[T],
) -> DecisionStateRecord:
    decision_value = observation.decision.decision
    if decision_value == "defer":
        outcome: DecisionOutcome = "REVIEW"
        phase = "ADMISSIBILITY"
        reason = observation.decision.reason_code
    elif decision_value == "deny":
        outcome = "DENY"
        phase = "ADMISSIBILITY"
        reason = observation.decision.reason_code
    elif observation.coherence_receipt and observation.coherence_receipt.get("decision") == "DENY":
        outcome = "DENY"
        phase = "COMMIT_COHERENCE"
        reason = "coherence_failed"
    else:
        outcome = "ALLOW"
        phase = "EXECUTION"
        reason = observation.decision.reason_code

    if observation.status == "executed":
        executor_invoked = True
        commit_state = "COMMITTED"
        observation_state = "OBSERVED"
        reconciliation: ReconciliationState = "MATCH"
    elif observation.status == "failed":
        executor_invoked = True
        commit_state = "COMMIT_UNKNOWN"
        observation_state = "OBSERVATION_UNKNOWN"
        reconciliation = "UNKNOWN"
    else:
        executor_invoked = False
        commit_state = "NOT_ATTEMPTED" if phase == "ADMISSIBILITY" else "NOT_COMMITTED"
        observation_state = "NOT_OBSERVED"
        reconciliation = "NOT_APPLICABLE"

    binding = request.binding
    receipt_hash = None
    if observation.coherence_receipt is not None:
        receipt_hash = observation.coherence_receipt.get("receipt_hash")

    return DecisionStateRecord(
        artifact_type="stegcore.runtime_decision_state",
        adapter_kind=request.adapter_kind,
        outcome=outcome,
        phase=phase,
        reason_code=reason,
        candidate_id=binding.candidate_id,
        candidate_hash=binding.candidate_hash,
        credential_id=binding.credential_id,
        credential_hash=binding.credential_hash,
        credential_subject=binding.credential_subject,
        authority_reference=binding.authority_reference,
        capability_hash=canonical_hash(_normalized_surface(binding.capability_surface)),
        previous_receipt_hash=binding.previous_receipt_hash,
        executor_invoked=executor_invoked,
        commit_state=commit_state,
        observation_state=observation_state,
        reconciliation=reconciliation,
        decision=asdict(observation.decision),
        coherence_receipt_hash=receipt_hash,
        runtime_pre_state_hash=observation.pre_state_hash,
        runtime_post_state_hash=observation.post_state_hash,
    )


def reconcile_effect(
    state: DecisionStateRecord,
    *,
    effect_observed: Optional[bool],
) -> DecisionStateRecord:
    """Reconcile later effect observation without rewriting the governing decision."""

    if effect_observed is None:
        return replace(
            state,
            observation_state="OBSERVATION_UNKNOWN",
            reconciliation="UNKNOWN",
        )

    if state.outcome in {"DENY", "REVIEW", "FAIL_CLOSED"}:
        if effect_observed:
            return replace(
                state,
                observation_state="DIVERGENT",
                reconciliation="GOVERNANCE_BYPASS",
            )
        return replace(
            state,
            observation_state="OBSERVED",
            reconciliation="MATCH",
        )

    if state.outcome == "ALLOW":
        if state.commit_state == "COMMITTED" and effect_observed:
            return replace(
                state,
                observation_state="OBSERVED",
                reconciliation="MATCH",
            )
        if state.commit_state == "COMMITTED" and not effect_observed:
            return replace(
                state,
                observation_state="DIVERGENT",
                reconciliation="DIVERGENT",
            )
        if effect_observed and state.commit_state != "COMMITTED":
            return replace(
                state,
                observation_state="DIVERGENT",
                reconciliation="GOVERNANCE_BYPASS",
            )
        return replace(
            state,
            observation_state="OBSERVED",
            reconciliation="MATCH",
        )

    return replace(
        state,
        observation_state="OBSERVATION_UNKNOWN",
        reconciliation="UNKNOWN",
    )


def execute_adapter(
    request: GovernedAdapterRequest,
    executor: Callable[[], T],
) -> AdapterObservation[T]:
    """Execute one caller/transport path through the single governed boundary."""

    failures = _binding_failures(request)
    if failures:
        return _fail_closed(request, failures[0])

    runtime = governed_execute(
        request.decision_request,
        executor,
        declared_execution_context={
            **dict(request.declared_execution_context),
            "adapter_kind": request.adapter_kind,
            "candidate_id": request.binding.candidate_id,
            "candidate_hash": request.binding.candidate_hash,
            "credential_id": request.binding.credential_id,
            "credential_hash": request.binding.credential_hash,
            "credential_subject": request.binding.credential_subject,
            "authority_reference": request.binding.authority_reference,
        },
        capability_surface=request.binding.capability_surface,
        previous_receipt_hash=request.binding.previous_receipt_hash,
    )
    state = _runtime_state(request, runtime)
    return AdapterObservation(
        artifact_type="stegcore.adapter_observation",
        status=runtime.status,
        decision_state=state,
        runtime_observation=runtime,
        result=runtime.result,
        error_type=runtime.error_type,
        error_message=runtime.error_message,
    )


def execute_http(request: GovernedAdapterRequest, executor: Callable[[], T]) -> AdapterObservation[T]:
    """Bounded HTTP/API transport shim; transport itself grants no authority."""
    if request.adapter_kind != "api":
        return _fail_closed(request, "http_adapter_kind_mismatch")
    return execute_adapter(request, executor)
