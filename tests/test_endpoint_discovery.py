from stegcore.endpoint_discovery import STABLE_RENDEZVOUS_ORIGIN, resolve_steggate_origin


def test_uses_stable_rendezvous_when_healthy():
    def reader(url, timeout):
        assert timeout == 1
        assert url == f"{STABLE_RENDEZVOUS_ORIGIN}/health"
        return {"healthy": True, "canonical_three_layer_bound": True}

    result = resolve_steggate_origin(timeout=1, reader=reader)
    assert result.state == "LIVE"
    assert result.origin == STABLE_RENDEZVOUS_ORIGIN
    assert result.source == "stegverse_stable_rendezvous"


def test_fails_closed_when_stable_rendezvous_is_unavailable():
    def reader(url, timeout):
        assert timeout == 1
        assert url == f"{STABLE_RENDEZVOUS_ORIGIN}/health"
        raise OSError("stable rendezvous unavailable")

    result = resolve_steggate_origin(timeout=1, reader=reader)
    assert result.state == "FAIL_CLOSED"
    assert result.origin is None
    assert result.source is None
    assert result.canonical_three_layer_bound is False
