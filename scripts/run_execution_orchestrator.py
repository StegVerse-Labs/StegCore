#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

from stegcore.execution_orchestrator import Task, derive_execution_state

ROOT = Path(__file__).resolve().parents[1]
TASKS_PATH = ROOT / "data" / "execution-orchestrator-tasks.json"
STATE_PATH = ROOT / "data" / "execution-orchestrator-state.json"
API = "https://api.github.com"
TOKEN = os.getenv("STEGVERSE_ORCHESTRATOR_TOKEN") or os.getenv("GITHUB_TOKEN", "")


def observe(repository: str, path: str) -> tuple[bool, dict | None, str | None]:
    url = f"{API}/repos/{repository}/contents/{path}?ref=main"
    headers = {"Accept": "application/vnd.github.raw+json", "User-Agent": "StegVerse-Execution-Orchestrator/1.0"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    try:
        with request.urlopen(request.Request(url, headers=headers), timeout=30) as response:
            value = json.loads(response.read().decode("utf-8"))
        return True, value if isinstance(value, dict) else None, None
    except error.HTTPError as exc:
        return False, None, f"HTTP_{exc.code}"
    except (error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return False, None, type(exc).__name__.upper()


def main() -> int:
    registry = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    tasks: list[Task] = []
    observations: dict[str, dict | None] = {}
    observation_errors: dict[str, str] = {}
    for row in registry["tasks"]:
        task = Task(
            task_id=row["task_id"], repository=row["repository"], issue=row["issue"],
            workflow=row["workflow"], evidence_path=row["evidence_path"],
            stop_condition=row["stop_condition"], dependencies=tuple(row.get("dependencies", [])),
            resolver=row.get("resolver", "repository_workflow"), successor=row.get("successor"),
            retry_policy=row.get("retry_policy", "hourly"),
            authority_required=bool(row.get("authority_required", False)),
        )
        tasks.append(task)
        available, evidence, reason = observe(task.repository, task.evidence_path)
        if available:
            observations[task.task_id] = evidence
        else:
            observation_errors[task.task_id] = reason or "UNKNOWN"

    state = derive_execution_state(tasks, observations)
    state.update({
        "schema": "stegverse.execution_orchestrator.state.v1",
        "controller_issue": "StegVerse-Labs/StegCore#42",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "observation_errors": observation_errors,
        "observation_failure_is_task_failure": False,
    })
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"state": state["state"], "tasks": len(tasks), "development_halt": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
