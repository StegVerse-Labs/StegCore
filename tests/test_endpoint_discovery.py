from stegcore.endpoint_discovery import (
    FALLBACK_REGISTRY_URL,
    PERSISTENT_ORIGIN,
    STABLE_RENDEZVOUS_ORIGIN,
    resolve_steggate_origin,
)


def test_prefers_stable_rendezvous_when_healthy():
    def reader(url, timeout):
        assert timeout == 1
        if url == f"{STABLE_RENDEZVOUS_ORIGIN}/health":
            return {"healthy": True, "canonical_three_layer_bound": True}
        raise AssertionError(f"unexpected URL {url}")

    result = resolve_steggate_origin(timeout=1, reader=reader)
    assert result.state == "LIVE"
    assert result.origin == STABLE_RENDEZVOUS_ORIGIN
    assert result.source == "stegverse_stable_rendezvous"


def test_uses_persistent_origin_when_rendezvous_is_down():
    def reader(url, timeout):
        assert timeout == 1
        if url == f"{STABLE_RENDEZVOUS_ORIGIN}/health":
            raise OSError("stable rendezvous unavailable")
        if url == f"{PERSISTENT_ORIGIN}/health":
            return {"healthy": True, "canonical_three_layer_bound": True}
        raise AssertionError(f"unexpected URL {url}")

    result = resolve_steggate_origin(timeout=1, reader=reader)
    assert result.state == "LIVE"
    assert result.origin == PERSISTENT_ORIGIN
    assert result.source == "persistent_render"


def test_uses_verified_fallback_when_stable_and_persistent_are_down():
    fallback = "https://example-fallback.trycloudflare.com"

    def reader(url, timeout):
        if url == f"{STABLE_RENDEZVOUS_ORIGIN}/health":
            raise OSError("stable rendezvous unavailable")
        if url == f"{PERSISTENT_ORIGIN}/health":
            raise OSError("persistent unavailable")
        if url == FALLBACK_REGISTRY_URL:
            return {
                "body": (
                    "State: `LIVE_ACCEPTANCE_PASS`\n\n"
                    f"Current public origin: `{fallback}`\n"
                )
            }
        if url == f"{fallback}/health":
            return {"healthy": True, "canonical_three_layer_bound": True}
        raise AssertionError(f"unexpected URL {url}")

    result = resolve_steggate_origin(timeout=1, reader=reader)
    assert result.state == "LIVE"
    assert result.origin == fallback
    assert result.source == "github_actions_fallback_registry"


def test_fails_closed_when_registry_is_stale_or_endpoint_unhealthy():
    fallback = "https://stale-fallback.trycloudflare.com"

    def reader(url, timeout):
        if url == f"{STABLE_RENDEZVOUS_ORIGIN}/health":
            raise OSError("stable rendezvous unavailable")
        if url == f"{PERSISTENT_ORIGIN}/health":
            raise OSError("persistent unavailable")
        if url == FALLBACK_REGISTRY_URL:
            return {
                "body": (
                    "State: `LIVE_ACCEPTANCE_PASS`\n\n"
                    f"Current public origin: `{fallback}`\n"
                )
            }
        if url == f"{fallback}/health":
            raise OSError("expired tunnel")
        raise AssertionError(f"unexpected URL {url}")

    result = resolve_steggate_origin(timeout=1, reader=reader)
    assert result.state == "FAIL_CLOSED"
    assert result.origin is None
    assert result.canonical_three_layer_bound is False


def test_registry_without_live_acceptance_never_routes():
    def reader(url, timeout):
        if url == f"{STABLE_RENDEZVOUS_ORIGIN}/health":
            raise OSError("stable rendezvous unavailable")
        if url == f"{PERSISTENT_ORIGIN}/health":
            raise OSError("persistent unavailable")
        if url == FALLBACK_REGISTRY_URL:
            return {"body": "State: `PENDING_FIRST_EPHEMERAL_RUNTIME`"}
        raise AssertionError(f"unexpected URL {url}")

    result = resolve_steggate_origin(timeout=1, reader=reader)
    assert result.state == "FAIL_CLOSED"
    assert result.origin is None
