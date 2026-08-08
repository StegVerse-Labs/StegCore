#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "steggate-live-observation.json"
ORIGIN = os.getenv("STEGGATE_ORIGIN", "https://steggate-core.onrender.com").rstrip("/")
TIMEOUT = float(os.getenv("STEGGATE_OBSERVER_TIMEOUT", "20"))


def fetch_json(path: str) -> tuple[bool, dict | None, str | None]:
    url = ORIGIN + path
    req = request.Request(url, headers={"User-Agent": "StegGate-Live-Observer/1.0"})
    try:
        with request.urlopen(req, timeout=TIMEOUT) as response:
            raw = response.read().decode("utf-8")
            status = int(getattr(response, "status", 0) or 0)
        value = json.loads(raw)
        if not isinstance(value, dict):
            return False, None, "response_not_object"
        if status < 200 or status >= 300:
            return False, value, f"HTTP_{status}"
        return True, value, None
    except error.HTTPError as exc:
        return False, None, f"HTTP_{exc.code}"
    except (error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return False, None, type(exc).__name__.upper()


def evaluate_observation() -> dict:
    health_ok, health, health_error = fetch_json("/health")
    self_ok, self_test, self_error = fetch_json("/v1/self-test")

    health_pass = bool(
        health_ok
        and health
        and health.get("state") == "healthy"
        and health.get("canonical_three_layer_bound") is True
    )
    expected = {"ALLOW": "ALLOW", "DENY": "DENY", "REVIEW": "REVIEW", "FAIL_CLOSED": "FAIL_CLOSED"}
    self_test_pass = bool(
        self_ok
        and self_test
        and self_test.get("state") == "PASS"
        and self_test.get("canonical_three_layer_bound") is True
        and self_test.get("observed") == expected
    )

    state = "PASS" if health_pass and self_test_pass else "BLOCKED"
    return {
        "schema": "stegverse.steggate_live_observation.v1",
        "origin": ORIGIN,
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "state": state,
        "health": {"pass": health_pass, "error": health_error, "response": health},
        "self_test": {"pass": self_test_pass, "error": self_error, "response": self_test},
        "evaluate_required_after_live": True,
        "archive_allowed": False,
        "next_action": (
            "Exercise /v1/evaluate and persist full matrix evidence."
            if state == "PASS"
            else "Retry observation; deployment remains unavailable or unhealthy."
        ),
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    observation = evaluate_observation()
    OUT.write_text(json.dumps(observation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(observation, sort_keys=True))
    return 0 if observation["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
