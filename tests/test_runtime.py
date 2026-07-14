from __future__ import annotations

from stegcore.decision import (
    ActionIntent,
    DecisionRequest,
    PolicyContext,
    VerifiedReceiptEnvelope,
)
from stegcore.runtime import governed_execute


def verified_receipt() -> VerifiedReceiptEnvelope:
    return VerifiedReceiptEnvelope(
        receipt_id="receipt-001",
        key_id="stegid-key-001",
        verified=True,
        issued_at="2026-07-14T00:00:00+00:00",
    )


def request(*, shapes: list[str] | None = None, receipt_verified: bool = True) -> DecisionRequest:
    receipt = verified_receipt()
    receipt.verified = receipt_verified
    return DecisionRequest(
        verified_receipt=receipt,
        actor_class="system",
        intent=ActionIntent(
            action="repo.test",
            target="StegVerse-Labs/StegCore",
            requested_at="2026-07-14T00:00:00+00:00",
        ),
        policy=PolicyContext(shapes=shapes or []),
    )


def test_allow_executes_exactly_once() -> None:
    calls: list[str] = []

    observation = governed_execute(
        request(),
        lambda: calls.append("executed") or {"ok": True},
        declared_execution_context={"commit": "candidate"},
    )

    assert calls == ["executed"]
    assert observation.executed is True
    assert observation.status == "executed"
    assert observation.decision.decision == "allow"
    assert observation.result == {"ok": True}
    assert observation.pre_state_hash
    assert observation.post_state_hash


def test_deny_never_invokes_executor() -> None:
    calls: list[str] = []

    observation = governed_execute(
        request(receipt_verified=False),
        lambda: calls.append("must-not-run"),
    )

    assert calls == []
    assert observation.executed is False
    assert observation.status == "refused"
    assert observation.decision.decision == "deny"
    assert observation.decision.reason_code == "receipt.invalid"


def test_defer_never_invokes_executor() -> None:
    calls: list[str] = []

    observation = governed_execute(
        request(shapes=["quorum"]),
        lambda: calls.append("must-not-run"),
    )

    assert calls == []
    assert observation.executed is False
    assert observation.status == "refused"
    assert observation.decision.decision == "defer"
    assert observation.decision.reason_code == "requires.quorum"


def test_observation_is_explicitly_not_a_continuity_receipt() -> None:
    observation = governed_execute(request(), lambda: "ok")

    assert observation.artifact_type == "stegcore.execution_observation"
    assert not hasattr(observation, "receipt_id")
    assert not hasattr(observation, "signature")


def test_executor_failure_is_observed_without_becoming_allow_success() -> None:
    def fail() -> None:
        raise RuntimeError("execution failed")

    observation = governed_execute(request(), fail)

    assert observation.executed is False
    assert observation.status == "failed"
    assert observation.decision.decision == "allow"
    assert observation.error_type == "RuntimeError"
    assert observation.error_message == "execution failed"
