from datetime import datetime, timedelta, timezone

import pytest

from stegcore.sdk_operation_events import (
    CHOICE_LABELS,
    SDK_CHOICE_CODES,
    SDKOperationEventLedger,
)


RUNTIME_A = "stegverse:steggate:canonical:three-layer:v1"
RUNTIME_B = "stegverse:steggate:canonical:three-layer:v1:test-peer"
SOURCE = "sdk"
NOW = datetime(2026, 8, 14, 19, 0, tzinfo=timezone.utc)


def _complete(
    ledger: SDKOperationEventLedger,
    choice: str,
    when: datetime,
    *,
    runtime: str = RUNTIME_A,
    invocation_id: str,
):
    kwargs = {}
    if choice in {"1", "2"}:
        kwargs["manifest_receipt_id"] = f"MR-{choice}-{invocation_id}"
    started = ledger.begin(
        choice_code=choice,
        canonical_runtime_identity=runtime,
        source=SOURCE,
        occurred_at=when,
        invocation_id=invocation_id,
        **kwargs,
    )
    return ledger.finish(
        started.invocation_id,
        phase="COMPLETED",
        occurred_at=when + timedelta(seconds=1),
        receipt_chain_head=f"CHAIN-{invocation_id}",
        consequence_reexecuted=False if choice == "2" else None,
    )


def test_all_five_choices_are_counted_independently():
    ledger = SDKOperationEventLedger()
    for index, choice in enumerate(SDK_CHOICE_CODES):
        _complete(
            ledger,
            choice,
            NOW - timedelta(days=index),
            invocation_id=f"inv-{choice}",
        )

    summary = ledger.summary(now=NOW)
    rows = {row.choice_code: row for row in summary.choices}

    assert tuple(rows) == SDK_CHOICE_CODES
    assert summary.lifetime_all_menu_invocations == 5
    assert summary.trailing_30_day_all_menu_invocations == 5
    assert summary.lifetime_core_governed_invocations == 3
    assert summary.trailing_30_day_core_governed_invocations == 3
    for choice in SDK_CHOICE_CODES:
        assert rows[choice].lifetime_invocations == 1
        assert rows[choice].trailing_30_day_invocations == 1
        assert rows[choice].percent_of_total == pytest.approx(20.0)
        assert rows[choice].completed == 1


def test_trailing_30_days_and_observed_since_are_not_inferred():
    ledger = SDKOperationEventLedger()
    _complete(ledger, "0", NOW - timedelta(days=45), invocation_id="old")
    _complete(ledger, "0", NOW - timedelta(days=2), invocation_id="recent")

    summary = ledger.summary(now=NOW)
    row = next(item for item in summary.choices if item.choice_code == "0")

    assert summary.historical_coverage == "OBSERVED_ONLY"
    assert summary.observed_since == (NOW - timedelta(days=45)).isoformat()
    assert row.lifetime_invocations == 2
    assert row.trailing_30_day_invocations == 1
    assert summary.trailing_30_day_all_menu_invocations == 1


def test_started_and_terminal_events_count_as_one_invocation():
    ledger = SDKOperationEventLedger()
    started = ledger.begin(
        choice_code="1",
        canonical_runtime_identity=RUNTIME_A,
        source=SOURCE,
        occurred_at=NOW,
        manifest_receipt_id="MR-REPLAY",
        invocation_id="replay-one",
    )
    before = ledger.summary(now=NOW)
    assert before.lifetime_all_menu_invocations == 1
    assert before.choices[3].in_progress == 1

    ledger.finish(
        started.invocation_id,
        phase="FAILED",
        occurred_at=NOW + timedelta(seconds=3),
    )
    after = ledger.summary(now=NOW + timedelta(seconds=4))
    replay = next(item for item in after.choices if item.choice_code == "1")
    assert after.lifetime_all_menu_invocations == 1
    assert replay.failed == 1
    assert replay.in_progress == 0


def test_terminal_event_cannot_be_appended_twice():
    ledger = SDKOperationEventLedger()
    started = ledger.begin(
        choice_code="0",
        canonical_runtime_identity=RUNTIME_A,
        source=SOURCE,
        occurred_at=NOW,
        invocation_id="once",
    )
    ledger.finish(started.invocation_id, phase="COMPLETED", occurred_at=NOW + timedelta(seconds=1))
    with pytest.raises(ValueError, match="terminal"):
        ledger.finish(started.invocation_id, phase="FAILED", occurred_at=NOW + timedelta(seconds=2))


def test_replay_and_reconstruct_require_receipt_locator():
    ledger = SDKOperationEventLedger()
    for choice in ("1", "2"):
        with pytest.raises(ValueError, match="manifest_receipt_id"):
            ledger.begin(
                choice_code=choice,
                canonical_runtime_identity=RUNTIME_A,
                source=SOURCE,
                invocation_id=f"missing-{choice}",
                occurred_at=NOW,
            )


def test_reconstruction_cannot_claim_consequence_reexecution():
    ledger = SDKOperationEventLedger()
    started = ledger.begin(
        choice_code="2",
        canonical_runtime_identity=RUNTIME_A,
        source=SOURCE,
        manifest_receipt_id="MR-RECONSTRUCT",
        invocation_id="reconstruct",
        occurred_at=NOW,
    )
    with pytest.raises(ValueError, match="consequence re-execution"):
        ledger.finish(
            started.invocation_id,
            phase="COMPLETED",
            occurred_at=NOW + timedelta(seconds=1),
            consequence_reexecuted=True,
        )


def test_unknown_choice_labels_may_be_observed_without_inventing_semantics():
    ledger = SDKOperationEventLedger()
    first = ledger.begin(
        choice_code="000",
        choice_label="observed menu entry A",
        canonical_runtime_identity=RUNTIME_A,
        source=SOURCE,
        invocation_id="unknown-000",
        occurred_at=NOW,
    )
    ledger.finish(first.invocation_id, phase="COMPLETED", occurred_at=NOW + timedelta(seconds=1))
    summary = ledger.summary(now=NOW + timedelta(seconds=2))
    row = next(item for item in summary.choices if item.choice_code == "000")

    assert CHOICE_LABELS["000"] is None
    assert row.choice_label is None
    assert row.lifetime_invocations == 1


def test_known_choice_label_cannot_be_overridden():
    ledger = SDKOperationEventLedger()
    with pytest.raises(ValueError, match="cannot be overridden"):
        ledger.begin(
            choice_code="0",
            choice_label="something else",
            canonical_runtime_identity=RUNTIME_A,
            source=SOURCE,
            invocation_id="bad-label",
            occurred_at=NOW,
        )


def test_unique_runtime_identities_and_status_breakdown():
    ledger = SDKOperationEventLedger()
    _complete(ledger, "00", NOW - timedelta(hours=2), runtime=RUNTIME_A, invocation_id="a")
    _complete(ledger, "00", NOW - timedelta(hours=1), runtime=RUNTIME_B, invocation_id="b")
    started = ledger.begin(
        choice_code="00",
        canonical_runtime_identity=RUNTIME_A,
        source=SOURCE,
        invocation_id="c",
        occurred_at=NOW,
    )
    ledger.finish(started.invocation_id, phase="CANCELLED", occurred_at=NOW + timedelta(seconds=1))

    row = next(item for item in ledger.summary(now=NOW + timedelta(seconds=2)).choices if item.choice_code == "00")
    assert row.lifetime_invocations == 3
    assert row.unique_runtime_identities == 2
    assert row.completed == 2
    assert row.cancelled == 1


def test_jsonl_round_trip_preserves_append_only_event_integrity(tmp_path):
    path = tmp_path / "sdk-operation-events.jsonl"
    ledger = SDKOperationEventLedger(path)
    _complete(ledger, "0", NOW, invocation_id="persisted")

    reloaded = SDKOperationEventLedger(path)
    assert len(reloaded.events()) == 2
    assert reloaded.summary(now=NOW + timedelta(seconds=2)).lifetime_all_menu_invocations == 1


def test_notification_projection_contains_no_payload_or_authority():
    ledger = SDKOperationEventLedger()
    terminal = _complete(ledger, "1", NOW, invocation_id="notify")
    projection = ledger.notification_projection(terminal, now=NOW + timedelta(seconds=2))

    assert projection["payload_disclosed"] is False
    assert projection["notification_grants_authority"] is False
    assert "payload" not in projection["event"]
    assert projection["event"]["manifest_receipt_id"] == "MR-1-notify"
    assert len(projection["usage"]["choices"]) == 5
