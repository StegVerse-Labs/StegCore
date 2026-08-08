"""Machine discovery for the currently usable StegGate HTTP origin.

Persistent hosting is preferred.  When it is unavailable, discovery may use the
machine-updated issue-comment registry populated by the bounded GitHub Actions
fallback runtime.  Discovery never grants execution or policy authority; it
only locates an endpoint and verifies its canonical health declaration.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, asdict
from typing import Callable
from urllib.request import Request, urlopen

PERSISTENT_ORIGIN = "https://steggate-core.onrender.com"
FALLBACK_REGISTRY_URL = (
    "https://api.github.com/repos/StegVerse-Labs/StegCore/issues/comments/5228464425"
)
_ORIGIN_RE = re.compile(r"Current public origin: `(?P<origin>https://[-a-z0-9.]+)`")


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
    with urlopen(request, timeout=timeout) as response:  # nosec B310 - verified HTTPS origins
        return json.loads(response.read().decode("utf-8"))


def _healthy(origin: str, reader: Callable[[str, float], dict], timeout: float) -> bool:
    try:
        payload = reader(f"{origin.rstrip('/')}/health", timeout)
    except Exception:
        return False
    return bool(payload.get("healthy") and payload.get("canonical_three_layer_bound"))


def _healthy_with_retry(
    origin: str,
    reader: Callable[[str, float], dict],
    timeout: float,
    *,
    attempts: int = 3,
    delay: float = 1.0,
) -> bool:
    for attempt in range(attempts):
        if _healthy(origin, reader, timeout):
            return True
        if attempt + 1 < attempts and reader is _read_json:
            time.sleep(delay)
    return False


def resolve_steggate_origin(
    *,
    timeout: float = 10.0,
    reader: Callable[[str, float], dict] = _read_json,
) -> EndpointResolution:
    """Resolve a verified live StegGate origin, preferring persistent hosting.

    Failure is explicit.  A registry declaration is insufficient by itself;
    the discovered fallback origin must independently return canonical health.
    Transient fallback edge propagation is retried before failing closed.
    """

    if _healthy(PERSISTENT_ORIGIN, reader, timeout):
        return EndpointResolution(
            state="LIVE",
            origin=PERSISTENT_ORIGIN,
            source="persistent_render",
            canonical_three_layer_bound=True,
            detail="Persistent canonical origin is healthy.",
        )

    try:
        registry = reader(FALLBACK_REGISTRY_URL, timeout)
        body = str(registry.get("body", ""))
        if "State: `LIVE_ACCEPTANCE_PASS`" not in body:
            raise ValueError("fallback registry does not declare LIVE_ACCEPTANCE_PASS")
        match = _ORIGIN_RE.search(body)
        if not match:
            raise ValueError("fallback registry does not contain a public origin")
        fallback_origin = match.group("origin").rstrip("/")
    except Exception as exc:
        return EndpointResolution(
            state="FAIL_CLOSED",
            origin=None,
            source=None,
            canonical_three_layer_bound=False,
            detail=f"No verified live endpoint: {exc}",
        )

    if not _healthy_with_retry(fallback_origin, reader, timeout):
        return EndpointResolution(
            state="FAIL_CLOSED",
            origin=None,
            source="fallback_registry",
            canonical_three_layer_bound=False,
            detail="Fallback registry resolved an origin that did not pass canonical health after retry.",
        )

    return EndpointResolution(
        state="LIVE",
        origin=fallback_origin,
        source="github_actions_fallback_registry",
        canonical_three_layer_bound=True,
        detail="Rotating public fallback origin is live and canonically bound.",
    )
