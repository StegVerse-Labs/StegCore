from stegcore.decision import (
    VerifiedReceiptEnvelope,
    ActionIntent,
    PolicyContext,
    DecisionRequest,
    decide,
)


def test_deny_missing_receipt():
    req = DecisionRequest(
        verified_receipt=None,
        actor_class="human",
        intent=ActionIntent(action="repo.push", target="StegVerse-Labs/StegCore"),
        policy=PolicyContext(shapes=[]),
    )
    res = decide(req)
    assert res.decision == "deny"
    assert res.reason_code == "receipt.missing"


def test_deny_invalid_receipt():
    req = DecisionRequest(
        verified_receipt=VerifiedReceiptEnvelope(
            receipt_id="r1",
            key_id="k1",
            verified=False,
            issued_at="2025-01-01T00:00:00Z",
        ),
        actor_class="human",
        intent=ActionIntent(action="repo.push", target="StegVerse-Labs/StegCore"),
        policy=PolicyContext(shapes=[]),
    )
    res = decide(req)
    assert res.decision == "deny"
    assert res.reason_code == "receipt.invalid"


def test_defer_quorum():
    req = DecisionRequest(
        verified_receipt=VerifiedReceiptEnvelope(
            receipt_id="r1",
            key_id="k1",
            verified=True,
            issued_at="2025-01-01T00:00:00Z",
        ),
        actor_class="ai",
        intent=ActionIntent(action="policy.change", target="stegcore"),
        policy=PolicyContext(shapes=["quorum"]),
    )
    res = decide(req)
    assert res.decision == "defer"
    assert res.reason_code == "requires.quorum"
    assert res.constraints and res.constraints[0].type == "quorum"


def test_allow_default():
    req = DecisionRequest(
        verified_receipt=VerifiedReceiptEnvelope(
            receipt_id="r1",
            key_id="k1",
            verified=True,
            issued_at="2025-01-01T00:00:00Z",
        ),
        actor_class="system",
        intent=ActionIntent(action="node.heartbeat", target="CosDenOS"),
        policy=PolicyContext(shapes=[]),
    )
    res = decide(req)
    assert res.decision == "allow"
