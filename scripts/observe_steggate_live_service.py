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

LIVE_EVALUATION = {
    "candidate": {
        "actor_class": "system",
        "action": "live_observer",
        "target": "steggate-core",
        "scope": "activation-observation",
        "parameters": {"purpose": "verify-complete-hosted-matrix"},
    },
    "judgment": {
        "refusal_available": True,
        "operator_recoverability": "available",
        "workload_state": "supported",
        "time_pressure": "normal",
        "isolation_state": "supported",
        "evidence_refs": ["observer:judgment:v1"],
    },
    "signal": {
        "admitted_signal_refs": ["observer:signal:v1"],
        "transformations": ["observer:v1"],
        "missing_inputs": [],
        "uncertainty_state": "bounded",
        "reference_state_hash": "observer-state-v1",
        "expected_reference_state_hash": "observer-state-v1",
        "reconstruction_available": True,
        "transformation_provenance_complete": True,
    },
    "execution": {
        "actor_authority_current": True,
        "policy_current": True,
        "delegation_current": True,
        "evidence_current": True,
        "affected_entity_conditions_represented": True,
        "recoverability_profile": "recoverable",
        "validity_window_open": True,
        "policy_ref": "observer:policy:v1",
        "delegation_ref": "observer:delegation:v1",
        "evidence_refs": ["observer:execution:v1"],
    },
    "capability": {"allowed": True},
    "continuity": {
        "required": True,
        "previous_receipt_verified": True,
        "previous_receipt_hash": "observer:receipt:v0",
    },
    "approval": {"required": False},
    "permission_present": False,
    "declared_context": {"observer": "steggate-live-observer-v1"},
}


def fetch_json(path: str, payload: dict | None = None) -> tuple[bool, dict | None, str | None]:
    url = ORIGIN + path
    headers = {"User-Agent": "StegGate-Live-Observer/1.0"}
    body = None
    method = "GET"
    if payload is not None:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
        method = "POST"
    req = request.Request(url, data=body, headers=headers, method=method)
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


def _evaluation_pass(value: dict | None) -> bool:
    if not value:
        return False
    matrix = value.get("matrix")
    predicates = {
        row.get("predicate")
        for row in matrix
        if isinstance(matrix, list) and isinstance(row, dict)
    } if isinstance(matrix, list) else set()
    required_predicates = {
        "judgment.refusal_available",
        "signal.reference_state_match",
        "execution.actor_authority_current",
        "capability.allowed",
        "continuity.previous_receipt_verified",
        "approval.candidate_hash_binding",
        "permission.present",
    }
    hashes = (
        value.get("candidate_hash"),
        value.get("canonical_three_layer_request_hash"),
        value.get("canonical_three_layer_receipt_hash"),
        value.get("decision_state_hash"),
    )
    return bool(
        value.get("disposition") == "ALLOW"
        and value.get("canonical_three_layer_decision") == "ALLOW"
        and value.get("permission_is_not_admissibility") is True
        and value.get("continuity_receipt_minted") is False
        and value.get("external_execution_performed") is False
        and isinstance(matrix, list)
        and len(matrix) >= len(required_predicates)
        and required_predicates.issubset(predicates)
        and all(isinstance(item, str) and item for item in hashes)
    )


def evaluate_observation() -> dict:
    health_ok, health, health_error = fetch_json("/health")
    self_ok, self_test, self_error = fetch_json("/v1/self-test")
    eval_ok, evaluation, eval_error = fetch_json("/v1/evaluate", LIVE_EVALUATION)

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
    evaluation_pass = bool(eval_ok and _evaluation_pass(evaluation))

    state = "PASS" if health_pass and self_test_pass and evaluation_pass else "BLOCKED"
    return {
        "schema": "stegverse.steggate_live_observation.v2",
        "origin": ORIGIN,
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "state": state,
        "health": {"pass": health_pass, "error": health_error, "response": health},
        "self_test": {"pass": self_test_pass, "error": self_error, "response": self_test},
        "evaluate": {
            "pass": evaluation_pass,
            "error": eval_error,
            "request": LIVE_EVALUATION,
            "response": evaluation,
        },
        "activation_complete": state == "PASS",
        "archive_allowed": False,
        "next_action": (
            "Persist activation evidence into the canonical handoff and issue #68."
            if state == "PASS"
            else "Retry observation; deployment remains unavailable, unhealthy, or incomplete."
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
