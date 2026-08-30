from __future__ import annotations

"""Canonical StegVerse derivation for neutral current-basis comparison vectors.

This module is not a second evaluator. It translates the frozen neutral
cross-framework vector into StegCore's native AdmissibilityRequest and delegates
the actual disposition to canonical StegGate.

The critical boundary is that material change is not itself proof of invalidation
or non-currentness. Native currentness fields are populated only when the common
facts establish them; otherwise they remain unestablished (None).
"""

from typing import Any, Mapping

from .steggate import (
    AdmissibilityEvaluation,
    AdmissibilityRequest,
    ApprovalState,
    Candidate,
    CapabilityState,
    ContinuityState,
    ExecutionState,
    JudgmentState,
    SignalState,
    evaluate_admissibility,
)

VECTOR_SCHEMA = "stegverse.cross-framework-current-basis-vector.v0.4"
RESULT_SCHEMA = "stegcore.current-basis-evaluation.v1"


class CurrentBasisVectorError(ValueError):
    pass


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CurrentBasisVectorError(f"{name} must be an object")
    return value


def _text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise CurrentBasisVectorError(f"{name} is required")
    return text


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _observation_is_explicit_current(value: Any) -> bool | None:
    """Map only explicit currentness observations.

    Neutral states such as SUPPLIED_FOR_EVALUATION or MATERIAL_CHANGE_PRESENT do
    not establish true or false currentness and therefore remain None.
    """
    if value is True:
        return True
    if value is False:
        return False
    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized in {"CURRENT", "VALID_CURRENT", "OPEN", "VERIFIED_CURRENT"}:
            return True
        if normalized in {"NOT_CURRENT", "STALE", "CLOSED", "INVALID_CURRENT"}:
            return False
    return None


def derive_admissibility_request(vector: Mapping[str, Any]) -> AdmissibilityRequest:
    """Derive StegCore-native fields from one frozen neutral comparison vector."""
    vector = _mapping(vector, "vector")
    if vector.get("vector_schema") != VECTOR_SCHEMA:
        raise CurrentBasisVectorError(f"unsupported vector_schema; expected {VECTOR_SCHEMA}")

    initial = _mapping(vector.get("initial_state"), "initial_state")
    if initial.get("state_id") != "S0":
        raise CurrentBasisVectorError("initial_state.state_id must be S0")
    if initial.get("standing") != "DECLARED_VALID_FOR_TEST":
        raise CurrentBasisVectorError("S0 must be DECLARED_VALID_FOR_TEST")
    if "prior_receipt_ref" in initial:
        raise CurrentBasisVectorError("v0.4 initial S0 must not require a prior receipt")

    transition = _mapping(vector.get("transition"), "transition")
    if transition.get("transition_id") != "DELTA-S0-S1":
        raise CurrentBasisVectorError("unexpected transition_id")
    if transition.get("materiality") != "MATERIAL":
        raise CurrentBasisVectorError("comparison transition must be MATERIAL")
    if transition.get("invalidation_asserted_as_input") is not False:
        raise CurrentBasisVectorError("invalidation must not be asserted as input")
    if transition.get("receipt_semantics") != "S0_TO_S1_RECEIPT_IS_POST_OBSERVATION_EVIDENCE":
        raise CurrentBasisVectorError("transition receipt must remain post-observation evidence")

    s1 = _mapping(vector.get("successor_state_observed_inputs"), "successor_state_observed_inputs")
    if s1.get("state_id") != "S1":
        raise CurrentBasisVectorError("successor state must be S1")

    actor = _mapping(s1.get("actor"), "successor_state_observed_inputs.actor")
    policy = _mapping(s1.get("policy"), "successor_state_observed_inputs.policy")
    delegation = _mapping(s1.get("delegation"), "successor_state_observed_inputs.delegation")
    evidence = _mapping(s1.get("evidence"), "successor_state_observed_inputs.evidence")
    validity = _mapping(s1.get("validity_window"), "successor_state_observed_inputs.validity_window")
    judgment = _mapping(s1.get("judgment_context"), "successor_state_observed_inputs.judgment_context")
    signal = _mapping(s1.get("signal_context"), "successor_state_observed_inputs.signal_context")

    evidence_refs = evidence.get("references") or []
    if not isinstance(evidence_refs, list):
        raise CurrentBasisVectorError("evidence.references must be an array")
    admitted_signal_refs = signal.get("admitted_signal_refs") or []
    transformations = signal.get("transformations") or []
    missing_inputs = signal.get("missing_inputs") or []
    for name, value in (
        ("signal_context.admitted_signal_refs", admitted_signal_refs),
        ("signal_context.transformations", transformations),
        ("signal_context.missing_inputs", missing_inputs),
    ):
        if not isinstance(value, list):
            raise CurrentBasisVectorError(f"{name} must be an array")

    # The common artifact deliberately does not establish native currentness.
    # Only an explicit current/not-current observation may populate these fields.
    policy_current = _observation_is_explicit_current(policy.get("currentness"))
    delegation_current = _observation_is_explicit_current(delegation.get("currentness"))
    evidence_current = _observation_is_explicit_current(evidence.get("currentness"))
    validity_window_open = _observation_is_explicit_current(validity.get("currentness"))
    actor_authority_current = _observation_is_explicit_current(actor.get("authority_current"))

    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class=_text(actor.get("class"), "actor.class"),
            action=_text(actor.get("action"), "actor.action"),
            target=_text(actor.get("target"), "actor.target"),
            scope=_text(actor.get("scope"), "actor.scope"),
            parameters={
                "comparison_transition_id": transition["transition_id"],
                "materiality": transition["materiality"],
                "changed_condition": transition.get("changed_condition"),
            },
        ),
        judgment=JudgmentState(
            refusal_available=judgment.get("refusal_available"),
            operator_recoverability=_optional_text(judgment.get("operator_recoverability")),
            workload_state=_optional_text(judgment.get("workload_state")),
            time_pressure=_optional_text(judgment.get("time_pressure")),
            isolation_state=_optional_text(judgment.get("isolation_state")),
            evidence_refs=["state:s0-declared-valid", "transition:DELTA-S0-S1"],
        ),
        signal=SignalState(
            admitted_signal_refs=[str(item) for item in admitted_signal_refs],
            excluded_signal_refs=[],
            transformations=[str(item) for item in transformations],
            missing_inputs=[str(item) for item in missing_inputs],
            uncertainty_state=_optional_text(signal.get("uncertainty_state")),
            reference_state_hash=_optional_text(signal.get("reference_state_hash")),
            expected_reference_state_hash=_optional_text(signal.get("expected_reference_state_hash")),
            reconstruction_available=signal.get("reconstruction_available"),
            transformation_provenance_complete=signal.get("transformation_provenance_complete"),
        ),
        execution=ExecutionState(
            actor_authority_current=actor_authority_current,
            policy_current=policy_current,
            delegation_current=delegation_current,
            evidence_current=evidence_current,
            affected_entity_conditions_represented=None,
            recoverability_profile="unknown",
            validity_window_open=validity_window_open,
            policy_ref=_optional_text(policy.get("reference")),
            delegation_ref=_optional_text(delegation.get("reference")),
            evidence_refs=[str(item) for item in evidence_refs],
        ),
        # This is a bounded evaluation capability, not permission for an external
        # consequence. Holding capability constant prevents the experiment from
        # being decided by an unrelated missing-capability predicate.
        capability=CapabilityState(allowed=True),
        # No prior-state data is supplied by this v0.4 test; S0 is the declared
        # initial test state, so historical continuity proof is not required.
        continuity=ContinuityState(required=False),
        approval=ApprovalState(required=False),
        permission_present=False,
        declared_context={
            "comparison_vector_schema": VECTOR_SCHEMA,
            "s0_origin": "DECLARED_INITIAL_TEST_STATE",
            "material_change_present": transition.get("changed_condition") == "CURRENT_POLICY_BASIS_CHANGED",
            "invalidation_asserted_as_input": False,
            "transition_receipt_pre_execution_input": False,
        },
    )


def evaluate_current_basis_vector(vector: Mapping[str, Any]) -> dict[str, Any]:
    """Derive the native request and evaluate it with canonical StegGate."""
    request = derive_admissibility_request(vector)
    evaluation: AdmissibilityEvaluation = evaluate_admissibility(request)
    return {
        "schema": RESULT_SCHEMA,
        "vector_schema": VECTOR_SCHEMA,
        "canonical_evaluator": "stegcore.steggate.evaluate_admissibility",
        "parallel_evaluator": False,
        "material_change_treated_as_invalidation_input": False,
        "s0_requires_historical_receipt": False,
        "transition_receipt_minted": False,
        "transition_receipt_eligible_after_observation": True,
        "s1_observed": True,
        "native_request": request.model_dump(mode="json", exclude_none=False),
        "evaluation": evaluation.model_dump(mode="json", exclude_none=False),
    }


__all__ = [
    "VECTOR_SCHEMA",
    "RESULT_SCHEMA",
    "CurrentBasisVectorError",
    "derive_admissibility_request",
    "evaluate_current_basis_vector",
]
