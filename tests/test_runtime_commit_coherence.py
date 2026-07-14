from stegcore.decision import (
    ActionIntent,
    DecisionRequest,
    PolicyContext,
    VerifiedReceiptEnvelope,
)
from stegcore.runtime import governed_execute


def request() -> DecisionRequest:
    return DecisionRequest(
        verified_receipt=VerifiedReceiptEnvelope(
            receipt_id="r-1",
            key_id="k-1",
            verified=True,
            issued_at="2026-07-14T00:00:00+00:00",
        ),
        actor_class="ai",
        intent=ActionIntent(
            action="demo_task",
            target="demo_target",
            parameters={"x": 1},
        ),
        policy=PolicyContext(),
    )


def allow_surface():
    return {
        "actions_exposed": ["demo_task"],
        "execution_mode": "manual",
        "requires_governed_commit": True,
    }


def test_allow_executes_once():
    calls = []

    def executor():
        calls.append("called")
        return {"ok": True}

    result = governed_execute(
        request(),
        executor,
        capability_surface=allow_surface(),
    )

    assert result.status == "executed"
    assert calls == ["called"]
    assert result.coherence_receipt["decision"] == "ALLOW"
    assert result.coherence_receipt["execution_status"] == "executed"


def test_coherence_deny_never_invokes_executor():
    called = False

    def executor():
        nonlocal called
        called = True
        return {"ok": True}

    result = governed_execute(
        request(),
        executor,
        capability_surface={
            "actions_exposed": ["demo_task"],
            "execution_mode": "auto",
            "requires_governed_commit": True,
        },
    )

    assert result.status == "refused"
    assert called is False
    assert result.coherence_receipt["decision"] == "DENY"
    assert result.coherence_receipt["coherence_checks"]["denial_preserved"] is False


def test_admissibility_deny_never_reaches_coherence_or_executor():
    called = False
    req = request()
    req.verified_receipt.verified = False

    def executor():
        nonlocal called
        called = True

    result = governed_execute(req, executor, capability_surface=allow_surface())

    assert result.status == "refused"
    assert result.decision.decision == "deny"
    assert result.coherence_receipt is None
    assert called is False


def test_authority_loss_denies_before_execution():
    called = False

    def executor():
        nonlocal called
        called = True

    result = governed_execute(
        request(),
        executor,
        capability_surface=allow_surface(),
        authority_resolution={
            "status": "approved",
            "basis_invalidated_by_action": True,
        },
    )

    assert result.status == "refused"
    assert called is False
    assert result.coherence_receipt["coherence_checks"]["authority_preserved"] is False


def test_executor_failure_is_observed_and_receipted():
    def executor():
        raise RuntimeError("boom")

    result = governed_execute(
        request(),
        executor,
        capability_surface=allow_surface(),
    )

    assert result.status == "failed"
    assert result.error_type == "RuntimeError"
    assert result.coherence_receipt["execution_status"] == "failed"
    assert result.coherence_receipt["error_message"] == "boom"


def test_previous_receipt_hash_is_bound():
    result = governed_execute(
        request(),
        lambda: "ok",
        capability_surface=allow_surface(),
        previous_receipt_hash="prev-123",
    )

    assert result.coherence_receipt["previous_receipt_hash"] == "prev-123"
