"""Machine discovery for the currently usable StegGate HTTP origin.

Current discovery is deliberately bounded to the StegVerse-owned stable rendezvous.
No third-party persistent host, tunnel, registry, or fallback runtime is selected.
Discovery grants no execution or policy authority; it only verifies the canonical
health declaration of the StegVerse-owned endpoint.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Callable
from urllib.request import Request, urlopen

STABLE_RENDEZVOUS_ORIGIN = "https://stegverse.org/api/steggate"


@dataclass(frozen=True)
class EndpointResolution:
    state: str
    origin: str | None
    source: str | None
    canonical_three_layer_bound: bool
    detail: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _read_json(url: str, timeout: float = 10.0) -> dict:
    request = Request(url, headers={"User-Agent": "StegCore-endpoint-discovery/1"})
    with urlopen(request, timeout=timeout) as response:  # nosec B310 - verified HTTPS origin
        return json.loads(response.read().decode("utf-8"))


def _healthy(origin: str, reader: Callable[[str, float], dict], timeout: float) -> bool:
    try:
        payload = reader(f"{origin.rstrip('/')}/health", timeout)
    except Exception:
        return False
    return bool(payload.get("healthy") and payload.get("canonical_three_layer_bound"))


def resolve_steggate_origin(
    *,
    timeout: float = 10.0,
    reader: Callable[[str, float], dict] = _read_json,
) -> EndpointResolution:
    """Resolve the verified StegVerse-owned StegGate origin or fail closed."""

    if _healthy(STABLE_RENDEZVOUS_ORIGIN, reader, timeout):
        return EndpointResolution(
            state="LIVE",
            origin=STABLE_RENDEZVOUS_ORIGIN,
            source="stegverse_stable_rendezvous",
            canonical_three_layer_bound=True,
            detail="Stable StegVerse rendezvous is healthy and canonically bound.",
        )

    return EndpointResolution(
        state="FAIL_CLOSED",
        origin=None,
        source=None,
        canonical_three_layer_bound=False,
        detail="StegVerse-owned stable rendezvous is unavailable or not canonically bound.",
    )
