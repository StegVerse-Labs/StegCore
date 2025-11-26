from stegcore import StateEngine, NodeState


def test_state_engine_upsert_and_events():
    engine = StateEngine()

    engine.upsert_node(
        node="CosDenOS",
        status="healthy",
        version="0.1.0",
        metadata={"endpoint": "https://cosden.stegverse.internal"},
        reason="initial",
    )

    state = engine.get_node_state("CosDenOS")
    assert state is not None
    assert state.status == "healthy"
    assert state.version == "0.1.0"

    events = engine.list_events_for_node("CosDenOS")
    assert len(events) == 1
    assert events[0].node == "CosDenOS"
