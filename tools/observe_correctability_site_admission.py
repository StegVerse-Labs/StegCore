#!/usr/bin/env python3
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SITE_RAW = "https://raw.githubusercontent.com/StegVerse-Labs/Site/main/data/site-orchestration-state.json"
OUT = Path(__file__).resolve().parents[1] / "brain_reports" / "correctability_site_admission_observer.json"


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "StegVerse-Correctability-Observer/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def main():
    now = datetime.now(timezone.utc).isoformat()
    try:
        state = fetch_json(SITE_RAW)
        seq = state.get("active_sequence", {})
        admission = seq.get("machine_admission", {})
        observation = seq.get("machine_observation", {})
        external_tasks_allowed = admission.get("external_tasks_allowed", False)
        external_session_allowed = admission.get("external_session_ownership_allowed", False)
        admitted = admission.get("admitted_tasks", [])
        site_state = seq.get("state")
        ready = bool(site_state in {"IDLE", "COMPLETE"} and external_tasks_allowed)
        result = {
            "schema_version": "1.0.0",
            "record_type": "stegverse.correctability.site_admission_observer",
            "observed_at": now,
            "source": SITE_RAW,
            "site_active_sequence_state": site_state,
            "site_external_tasks_allowed": external_tasks_allowed,
            "site_external_session_ownership_allowed": external_session_allowed,
            "site_admitted_tasks": admitted,
            "site_active_task_count": observation.get("active_task_count"),
            "site_blocker_count": observation.get("blocker_count"),
            "correctability_site_projection_ready_for_external_install": ready,
            "decision": "READY_FOR_SITE_NATIVE_ADMISSION" if ready else "BLOCKED_BY_SITE_ORCHESTRATION",
            "authority_effect": False,
            "manual_user_action_required": False,
        }
    except Exception as exc:
        result = {
            "schema_version": "1.0.0",
            "record_type": "stegverse.correctability.site_admission_observer",
            "observed_at": now,
            "source": SITE_RAW,
            "decision": "RETRY",
            "error": type(exc).__name__,
            "authority_effect": False,
            "manual_user_action_required": False,
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
