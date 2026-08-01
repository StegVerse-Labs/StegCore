#!/usr/bin/env python3
"""Observe the repository-bound RTG-TT task chain without producing unlocated pending work."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ecosystem_management" / "rtg_tt_task_ledger.v0.1.json"
REPORT = ROOT / "brain_reports" / "rtg_tt_task_observation.json"
TOKEN = os.getenv("GITHUB_TOKEN", "")
API = os.getenv("GITHUB_API_URL", "https://api.github.com")


def api(repo: str, path: str) -> Any:
    req = urllib.request.Request(
        f"{API}/repos/{repo}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "stegcore-rtg-tt-observer",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def observe(task: dict[str, Any]) -> dict[str, Any]:
    result = dict(task)
    repo = task["repository"]
    if "pull_request" in task:
        pr = api(repo, f"/pulls/{task['pull_request']}")
        result["observed_state"] = "MERGED" if pr.get("merged") else pr.get("state", "UNKNOWN").upper()
        result["observed_head_sha"] = pr.get("head", {}).get("sha")
        result["mergeable"] = pr.get("mergeable")
        if pr.get("merged"):
            result["next_action"] = "advance_to_successor_task"
        elif pr.get("draft"):
            result["next_action"] = "verify_checks_then_mark_ready"
        elif pr.get("mergeable") is True:
            result["next_action"] = "verify_checks_then_merge"
        else:
            result["next_action"] = "inspect_pr_checks_or_merge_conflict"
    elif "issue" in task:
        issue = api(repo, f"/issues/{task['issue']}")
        result["observed_state"] = issue.get("state", "UNKNOWN").upper()
        result["next_action"] = task["current_action"] if issue.get("state") == "open" else "advance_to_successor_task"
    else:
        result["observed_state"] = "LOCAL_PATH"
        result["next_action"] = task["current_action"]
    return result


def main() -> int:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    failures: list[str] = []
    observations: list[dict[str, Any]] = []
    for task in ledger.get("tasks", []):
        for required in ("task_id", "repository", "current_action"):
            if not task.get(required):
                failures.append(f"{task.get('task_id', 'UNKNOWN')}: missing {required}")
        if not any(key in task for key in ("pull_request", "issue", "path")):
            failures.append(f"{task.get('task_id', 'UNKNOWN')}: no executable location")
        try:
            observations.append(observe(task) if TOKEN else {**task, "observed_state": "TOKEN_UNAVAILABLE", "next_action": task["current_action"]})
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            observations.append({**task, "observed_state": "OBSERVATION_ERROR", "next_action": "retry_repository_observation", "error": str(exc)})
            failures.append(f"{task['task_id']}: observation failed")

    report = {
        "schema_version": "0.1.0",
        "layer_id": ledger["layer_id"],
        "status": "FAIL" if failures else "PASS",
        "halt_allowed": False,
        "tasks": observations,
        "failures": failures,
        "rule": "Every incomplete state retains an exact repository location and executable next action.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"RTG_TT_TASK_OBSERVER_{report['status']}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
