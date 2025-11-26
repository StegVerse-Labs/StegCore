from stegcore import StateEngine, Registry


def test_registry_register_and_heartbeat():
    engine = StateEngine()
    registry = Registry(engine=engine)

    registry.register(
        node="CosDenOS",
        version="0.1.0",
        metadata={"endpoint": "https://cosden.stegverse.internal"},
    )

    state = engine.get_node_state("CosDenOS")
    assert state is not None
    assert state.status == "healthy"

    registry.heartbeat(
        node="CosDenOS",
        version="0.1.1",
        metadata={"endpoint": "https://cosden.stegverse.internal"},
    )

    state2 = engine.get_node_state("CosDenOS")
    assert state2 is not None
    assert state2.version == "0.1.1"
