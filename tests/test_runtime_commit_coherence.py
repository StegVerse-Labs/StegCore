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
            issued_at="2026-01-01T00:00:00+00:00",
            valid_until="2027-01-01T00:00:00+00:00",
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


def authority(**overrides):
    value = {
        "status": "approved",
        "basis_invalidated_by_action": False,
        "authority_ref": "authority-1",
        "target_binding": "demo_target",
        "valid_from": "2026-01-01T00:00:00+00:00",
        "valid_until": "2027-01-01T00:00:00+00:00",
    }
    value.update(overrides)
    return value


def test_allow_executes_once():
    calls = []

    def executor():
        calls.append("called")
        return {"ok": True}

    result = governed_execute(
        request(),
        executor,
        capability_surface=allow_surface(),
        authority_resolution=authority(),
    )

    assert result.status == "executed"
    assert calls == ["called"]
    assert result.coherence_receipt["decision"] == "ALLOW"
    assert result.coherence_receipt["execution_status"] == "executed"
    assert result.coherence_receipt["commit_state"]["authority_resolution"]["authority_ref"] == "authority-1"
    assert result.coherence_receipt["commit_state"]["request"]["intent"]["target"] == "demo_target"
    assert result.coherence_receipt["evaluation_time"] == result.observed_at
    assert result.coherence_receipt["commit_state_hash"] == result.pre_state_hash
    assert all(result.coherence_receipt["present_state_checks"].values())


def test_missing_authority_fails_closed_before_execution():
    called = False

    def executor():
        nonlocal called
        called = True

    result = governed_execute(
        request(),
        executor,
        capability_surface=allow_surface(),
    )

    assert result.status == "refused"
    assert called is False
    assert result.coherence_receipt["decision"] == "FAIL_CLOSED"
    assert result.coherence_receipt["authority_resolution"]["status"] == "missing"
    assert result.coherence_receipt["commit_state"]["authority_resolution"]["status"] == "missing"
    assert "authority_state_unestablished" in result.coherence_receipt["present_state_reasons"]


def test_changed_target_denies_before_execution():
    called = False
    result = governed_execute(
        request(),
        lambda: called,
        capability_surface=allow_surface(),
        authority_resolution=authority(target_binding="different_target"),
    )

    assert result.status == "refused"
    assert result.coherence_receipt["decision"] == "DENY"
    assert "authority_target_mismatch" in result.coherence_receipt["present_state_reasons"]
    assert result.coherence_receipt["present_state_checks"]["target_current"] is False


def test_expired_authority_denies_before_execution():
    calls = []
    result = governed_execute(
        request(),
        lambda: calls.append("called"),
        capability_surface=allow_surface(),
        authority_resolution=authority(
            valid_from="2025-01-01T00:00:00+00:00",
            valid_until="2026-01-02T00:00:00+00:00",
        ),
    )

    assert result.status == "refused"
    assert calls == []
    assert result.coherence_receipt["decision"] == "DENY"
    assert "authority_expired" in result.coherence_receipt["present_state_reasons"]
    assert result.coherence_receipt["present_state_checks"]["authority_temporal_current"] is False


def test_missing_authority_temporal_state_fails_closed():
    calls = []
    auth = authority()
    auth.pop("valid_until")
    result = governed_execute(
        request(),
        lambda: calls.append("called"),
        capability_surface=allow_surface(),
        authority_resolution=auth,
    )

    assert result.status == "refused"
    assert calls == []
    assert result.coherence_receipt["decision"] == "FAIL_CLOSED"
    assert "authority_temporal_state_unestablished" in result.coherence_receipt["present_state_reasons"]


def test_stale_continuity_evidence_denies_before_execution():
    calls = []
    req = request()
    req.verified_receipt.valid_until = "2026-01-02T00:00:00+00:00"
    result = governed_execute(
        req,
        lambda: calls.append("called"),
        capability_surface=allow_surface(),
        authority_resolution=authority(),
    )

    assert result.status == "refused"
    assert calls == []
    assert result.coherence_receipt["decision"] == "DENY"
    assert "continuity_evidence_stale" in result.coherence_receipt["present_state_reasons"]
    assert result.coherence_receipt["present_state_checks"]["evidence_current"] is False


def test_missing_evidence_freshness_fails_closed():
    calls = []
    req = request()
    req.verified_receipt.valid_until = None
    result = governed_execute(
        req,
        lambda: calls.append("called"),
        capability_surface=allow_surface(),
        authority_resolution=authority(),
    )

    assert result.status == "refused"
    assert calls == []
    assert result.coherence_receipt["decision"] == "FAIL_CLOSED"
    assert "continuity_evidence_freshness_unestablished" in result.coherence_receipt["present_state_reasons"]


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
        authority_resolution=authority(),
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

    result = governed_execute(
        req,
        executor,
        capability_surface=allow_surface(),
        authority_resolution=authority(),
    )

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
        authority_resolution=authority(basis_invalidated_by_action=True),
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
        authority_resolution=authority(),
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
        authority_resolution=authority(),
        previous_receipt_hash="prev-123",
    )

    assert result.coherence_receipt["previous_receipt_hash"] == "prev-123"
