from __future__ import annotations

"""Exact commit-time binding checks for consequence-bearing execution.

This module is deliberately a pure state-binding predicate.  It does not make a
Governance decision, grant execution authority, resolve credentials, or execute
a consequence.  Callers compose it with the existing commit-time governance
path and fail closed before invoking the target runner.
"""

from dataclasses import dataclass
from typing import Any, Mapping, MutableSet


REQUIRED_BINDING_FIELDS = (
    "state_version",
    "state_hash",
    "policy_epoch",
    "policy_hash",
    "evidence_bundle_hash",
    "execution_binding_id",
)


@dataclass(frozen=True)
class FreshCommitBindingResult:
    disposition: str
    checks: Mapping[str, bool]
    reasons: tuple[str, ...]

    @property
    def allowed(self) -> bool:
        return self.disposition == "ALLOW"


def validate_commit_binding(binding: Mapping[str, Any]) -> dict[str, str]:
    if set(binding) != set(REQUIRED_BINDING_FIELDS):
        raise ValueError("fresh_binding.field_set_invalid")
    normalized: dict[str, str] = {}
    for field in REQUIRED_BINDING_FIELDS:
        value = binding.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"fresh_binding.{field}_missing")
        normalized[field] = value.strip()
    return normalized


def evaluate_fresh_commit_binding(
    *,
    expected: Mapping[str, Any] | None,
    observed: Mapping[str, Any] | None,
    consumed_execution_bindings: MutableSet[str] | None,
) -> FreshCommitBindingResult:
    """Compare the authorization-bound state to consequence-time state.

    Unknown/missing required state fails closed.  An established mismatch is a
    DENY.  A previously consumed execution binding is a DENY.  This function is
    intentionally non-authorizing; ALLOW means only that these exact binding
    predicates are current and unconsumed.
    """

    checks: dict[str, bool] = {}
    failures: list[str] = []
    indeterminate: list[str] = []

    if expected is None:
        return FreshCommitBindingResult(
            disposition="FAIL_CLOSED",
            checks={"commit_binding_established": False},
            reasons=("expected_commit_binding_unestablished",),
        )
    if observed is None:
        return FreshCommitBindingResult(
            disposition="FAIL_CLOSED",
            checks={"commit_binding_established": False},
            reasons=("observed_commit_state_unestablished",),
        )

    expected_binding = validate_commit_binding(expected)
    observed_binding = validate_commit_binding(observed)
    checks["commit_binding_established"] = True

    for field in (
        "state_version",
        "state_hash",
        "policy_epoch",
        "policy_hash",
        "evidence_bundle_hash",
    ):
        current = expected_binding[field] == observed_binding[field]
        checks[f"{field}_current"] = current
        if not current:
            failures.append(f"{field}_mismatch")

    if consumed_execution_bindings is None:
        checks["execution_binding_state_established"] = False
        indeterminate.append("execution_binding_consumption_state_unestablished")
    else:
        checks["execution_binding_state_established"] = True
        binding_id = expected_binding["execution_binding_id"]
        unconsumed = binding_id not in consumed_execution_bindings
        checks["execution_binding_unconsumed"] = unconsumed
        if not unconsumed:
            failures.append("execution_binding_already_consumed")

    if indeterminate:
        disposition = "FAIL_CLOSED"
        reasons = tuple(indeterminate + failures)
    elif failures:
        disposition = "DENY"
        reasons = tuple(failures)
    else:
        disposition = "ALLOW"
        reasons = ()

    return FreshCommitBindingResult(
        disposition=disposition,
        checks=checks,
        reasons=reasons,
    )


def consume_execution_binding(
    binding: Mapping[str, Any],
    consumed_execution_bindings: MutableSet[str],
) -> str:
    normalized = validate_commit_binding(binding)
    binding_id = normalized["execution_binding_id"]
    if binding_id in consumed_execution_bindings:
        raise ValueError("fresh_binding.execution_binding_already_consumed")
    consumed_execution_bindings.add(binding_id)
    return binding_id
