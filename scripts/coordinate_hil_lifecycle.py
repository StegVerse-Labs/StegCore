#!/usr/bin/env python3
"""Observe StegVerse HIL tasks and emit the next internal action queue.

The coordinator never classifies a missing observation as an external blocker.
It converts inaccessible or stale task state into a concrete internal observation,
implementation, fixture, validator, or evidence-import action.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "hil-lifecycle-task-registry.json"
OUTPUT = ROOT / "data" / "hil-lifecycle-action-queue.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def github_issue(repository: str, number: int, token: str | None) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repository}/issues/{number}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "StegCore-HIL-Coordinator/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return {
                "observed": True,
                "http_status": response.status,
                "issue": json.loads(response.read().decode("utf-8")),
            }
    except urllib.error.HTTPError as exc:
        return {
            "observed": False,
            "http_status": exc.code,
            "reason": "ISSUE_OBSERVATION_UNAVAILABLE",
        }
    except (urllib.error.URLError, TimeoutError) as exc:
        return {
            "observed": False,
            "http_status": None,
            "reason": "ISSUE_OBSERVATION_UNAVAILABLE",
            "detail": str(exc),
        }


def classify(task: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    base = {
        "task_id": task["task_id"],
        "location": task["location"],
        "repository": task["repository"],
        "issue_number": task["issue_number"],
    }
    if not observation.get("observed"):
        return {
            **base,
            "state": "ACTIONABLE_INTERNAL_OBSERVATION_GAP",
            "blocking": False,
            "next_action": (
                "Use the registered issue location through an authorized StegVerse "
                "observer, or continue the task's fixture/schema/validator tranche. "
                "Do not classify this as external and do not halt."
            ),
            "fallback_action": task["next_internal_action"],
        }

    issue = observation["issue"]
    state = issue.get("state", "unknown").upper()
    if state == "CLOSED":
        return {
            **base,
            "state": "VERIFY_COMPLETION_EVIDENCE",
            "blocking": False,
            "next_action": "Validate required outputs and identity continuity before marking the task complete.",
        }

    return {
        **base,
        "state": "OPEN_INTERNAL_WORK",
        "blocking": False,
        "updated_at": issue.get("updated_at"),
        "title": issue.get("title"),
        "next_action": task["next_internal_action"],
    }


def main() -> int:
    registry = load_json(REGISTRY)
    token = os.environ.get("STEGVERSE_COORDINATOR_TOKEN") or os.environ.get("GITHUB_TOKEN")
    actions = []
    for task in registry["tasks"]:
        observation = github_issue(task["repository"], int(task["issue_number"]), token)
        actions.append(classify(task, observation))

    open_actions = [item for item in actions if item["state"] != "COMPLETE"]
    queue = {
        "schema_version": "HIL-STEGVERSE-ACTION-QUEUE-v1",
        "registry_id": registry["registry_id"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": "CONTINUE_INTERNAL_DEVELOPMENT" if open_actions else "ARCHIVE_SESSION",
        "external_tasks": [],
        "halted": False,
        "action_count": len(open_actions),
        "actions": actions,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(queue, indent=2))

    if any(item.get("blocking") for item in actions):
        print("ERROR: internal action queue may not contain blocking=true", file=sys.stderr)
        return 1
    if queue["external_tasks"]:
        print("ERROR: external task classification is prohibited", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
