from stegcore.commit_governance import (
    coherence_gate,
    execute_if_coherent,
    verify_coherence_receipt,
    verify_receipt_integrity,
)


def authority():
    return {
        "status": "approved",
        "basis_invalidated_by_action": False,
    }


def allow_surface():
    return {
        "actions_exposed": ["demo_task"],
        "execution_mode": "manual",
        "requires_governed_commit": True,
    }


def deny_surface():
    return {
        "actions_exposed": ["demo_task"],
        "execution_mode": "auto",
        "requires_governed_commit": True,
    }


def test_allow_gate():
    gate = coherence_gate(
        task="demo_task",
        payload={},
        capability_surface=allow_surface(),
        state_hash="state-1",
        actor_binding="actor-1",
        authority_resolution=authority(),
    )
    assert gate["allowed"] is True
    assert gate["receipt"]["decision"] == "ALLOW"
    assert gate["receipt"]["coherent"] is True
    assert all(gate["receipt"]["coherence_checks"].values())
    assert verify_receipt_integrity(gate["receipt"])


def test_deny_gate_stops_runner():
    called = False

    def runner(task, payload):
        nonlocal called
        called = True
        return {"ok": True}

    result = execute_if_coherent(
        task_runner=runner,
        task="demo_task",
        payload={},
        capability_surface=deny_surface(),
        state_hash="state-1",
        actor_binding="actor-1",
        authority_resolution=authority(),
    )
    assert result["status"] == "DENIED"
    assert called is False
    assert result["receipt"]["decision"] == "DENY"
    assert result["receipt"]["coherence_checks"]["denial_preserved"] is False


def test_allow_executes_runner():
    calls = []

    def runner(task, payload):
        calls.append((task, payload))
        return {"ok": True}

    result = execute_if_coherent(
        task_runner=runner,
        task="demo_task",
        payload={"x": 1},
        capability_surface=allow_surface(),
        state_hash="state-1",
        actor_binding="actor-1",
        authority_resolution=authority(),
    )
    assert result["status"] == "COMPLETED"
    assert calls == [("demo_task", {"x": 1})]
    assert result["receipt"]["execution_result"] == {"ok": True}
    assert verify_receipt_integrity(result["receipt"])


def test_authority_failure():
    gate = coherence_gate(
        task="demo_task",
        payload={},
        capability_surface=allow_surface(),
        state_hash="state-1",
        actor_binding="actor-1",
        authority_resolution={
            "status": "approved",
            "basis_invalidated_by_action": True,
        },
    )
    assert gate["allowed"] is False
    assert gate["receipt"]["coherence_checks"]["authority_preserved"] is False


def test_unguarded_continuation_failure():
    gate = coherence_gate(
        task="demo_task",
        payload={},
        capability_surface=allow_surface(),
        state_hash="state-1",
        actor_binding="actor-1",
        authority_resolution=authority(),
        governance_mode="unguarded",
    )
    assert gate["allowed"] is False
    assert gate["receipt"]["coherence_checks"]["continuation_preserved"] is False


def test_receipt_tamper_detected():
    gate = coherence_gate(
        task="demo_task",
        payload={},
        capability_surface=allow_surface(),
        state_hash="state-1",
        actor_binding="actor-1",
        authority_resolution=authority(),
    )
    receipt = dict(gate["receipt"])
    receipt["decision"] = "DENY"
    assert verify_receipt_integrity(receipt) is False


def test_replay_recomputes_coherence():
    gate = coherence_gate(
        task="demo_task",
        payload={},
        capability_surface=allow_surface(),
        state_hash="state-1",
        actor_binding="actor-1",
        authority_resolution=authority(),
    )
    ok, failures = verify_coherence_receipt(
        gate["receipt"],
        capability_surface=gate["capability_surface"],
        action=gate["action"],
        next_state=gate["next_state"],
        authority_resolution=authority(),
    )
    assert ok is True
    assert failures == []
