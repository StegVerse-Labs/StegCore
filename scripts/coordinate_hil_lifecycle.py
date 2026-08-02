#!/usr/bin/env python3
"""Observe StegVerse HIL tasks and emit the next internal action queue.

The coordinator never classifies missing evidence or access as an external task.
It converts unavailable observations, stale claims, incomplete evidence, and closed
issues into deterministic internal actions. Archive is permitted only when every
registered task has validated completion evidence and no actionable claim remains.
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
TASK_REGISTRY = ROOT / "data" / "hil-lifecycle-task-registry.json"
CLAIM_REGISTRY = ROOT / "data" / "hil-lifecycle-claim-registry.json"
OUTPUT = ROOT / "data" / "hil-lifecycle-action-queue.json"

TERMINAL_STATES = {"COMPLETE", "SUPERSEDED", "MERGED_INTO_CANONICAL_WORKSTREAM"}
ACTION_STATES = {
    "BLOCKED",
    "RETRY",
    "REVIEW_REQUIRED",
    "FAILED",
    "CLAIMED",
    "VERIFY_COMPLETION_EVIDENCE",
    "OPEN_INTERNAL_WORK",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def github_issue(repository: str, number: int, token: str | None) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repository}/issues/{number}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "StegCore-HIL-Coordinator/2.0",
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


def claim_for(task_id: str, claims: dict[str, Any]) -> dict[str, Any] | None:
    return next((row for row in claims.get("claims", []) if row.get("task_id") == task_id), None)


def classify(
    task: dict[str, Any],
    observation: dict[str, Any],
    claim: dict[str, Any] | None,
    now: datetime,
) -> dict[str, Any]:
    base = {
        "task_id": task["task_id"],
        "location": task["location"],
        "repository": task["repository"],
        "issue_number": task["issue_number"],
        "blocking": False,
        "external": False,
    }

    if claim:
        base["claim_state"] = claim.get("state")
        base["claimant"] = claim.get("claimant")
        base["claim_expires_at"] = claim.get("expires_at")
        if claim.get("state") in TERMINAL_STATES:
            return {
                **base,
                "state": claim["state"],
                "next_action": None,
                "evidence_required": claim.get("expected_evidence", []),
            }
        expires = parse_time(claim.get("expires_at"))
        if expires and now > expires:
            return {
                **base,
                "state": "RETRY",
                "reason": "STALE_CLAIM_EXPIRED",
                "next_action": (
                    "Release or renew the claim with fresh repository mutation, workflow run, "
                    "receipt, or issue evidence; otherwise reassign the next nonconflicting internal lane."
                ),
                "fallback_action": task["next_internal_action"],
            }

    if not observation.get("observed"):
        return {
            **base,
            "state": "RETRY",
            "reason": observation.get("reason", "ISSUE_OBSERVATION_UNAVAILABLE"),
            "next_action": (
                "Retry through the registered repository observer or continue the task's safe "
                "fixture, schema, validator, evidence-import, or deployment-observation tranche."
            ),
            "fallback_action": task["next_internal_action"],
        }

    issue = observation["issue"]
    issue_state = issue.get("state", "unknown").upper()
    updated_at = parse_time(issue.get("updated_at"))

    if issue_state == "CLOSED":
        return {
            **base,
            "state": "VERIFY_COMPLETION_EVIDENCE",
            "updated_at": issue.get("updated_at"),
            "title": issue.get("title"),
            "next_action": (
                "Validate required outputs, workflow evidence, identity continuity, integration, "
                "and authority boundaries before changing the claim to COMPLETE."
            ),
        }

    if updated_at and claim:
        expires = parse_time(claim.get("expires_at"))
        if expires and updated_at > expires:
            return {
                **base,
                "state": "REVIEW_REQUIRED",
                "reason": "ISSUE_ACTIVITY_AFTER_CLAIM_EXPIRY",
                "updated_at": issue.get("updated_at"),
                "title": issue.get("title"),
                "next_action": "Reconcile new issue activity and renew or release the claim with evidence.",
            }

    return {
        **base,
        "state": "CLAIMED" if claim else "OPEN_INTERNAL_WORK",
        "updated_at": issue.get("updated_at"),
        "title": issue.get("title"),
        "next_action": task["next_internal_action"],
    }


def validate_registry(task_registry: dict[str, Any], claim_registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tasks = {row["task_id"] for row in task_registry.get("tasks", [])}
    claims = [row.get("task_id") for row in claim_registry.get("claims", [])]
    duplicates = {task_id for task_id in claims if claims.count(task_id) > 1}
    if duplicates:
        errors.append(f"duplicate_claims:{','.join(sorted(duplicates))}")
    unknown = {task_id for task_id in claims if task_id not in tasks and task_id != "HIL-CLOUDFLARE-LEGACY-001"}
    if unknown:
        errors.append(f"claims_without_tasks:{','.join(sorted(unknown))}")
    if not claim_registry.get("stale_claim_policy", {}).get("indefinite_claims_prohibited"):
        errors.append("indefinite_claims_not_prohibited")
    return errors


def main() -> int:
    task_registry = load_json(TASK_REGISTRY)
    claim_registry = load_json(CLAIM_REGISTRY)
    registry_errors = validate_registry(task_registry, claim_registry)
    now = datetime.now(timezone.utc)
    token = os.environ.get("STEGVERSE_COORDINATOR_TOKEN") or os.environ.get("GITHUB_TOKEN")

    actions = []
    for task in task_registry["tasks"]:
        observation = github_issue(task["repository"], int(task["issue_number"]), token)
        actions.append(classify(task, observation, claim_for(task["task_id"], claim_registry), now))

    actionable = [item for item in actions if item["state"] not in TERMINAL_STATES]
    terminal = [item for item in actions if item["state"] in TERMINAL_STATES]
    decision = "CONTINUE_INTERNAL_DEVELOPMENT" if actionable or registry_errors else "ARCHIVE_SESSION"

    queue = {
        "schema_version": "HIL-STEGVERSE-ACTION-QUEUE-v2",
        "registry_id": task_registry["registry_id"],
        "goal_id": claim_registry["goal_id"],
        "canonical_handoff": claim_registry["canonical_handoff"],
        "generated_at": now.isoformat(),
        "decision": decision,
        "external_tasks": [],
        "halted": False,
        "registry_valid": not registry_errors,
        "registry_errors": registry_errors,
        "action_count": len(actionable),
        "terminal_count": len(terminal),
        "actions": actions,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(queue, indent=2))

    if registry_errors:
        print("ERROR: invalid task or claim registry", file=sys.stderr)
        return 1
    if any(item.get("blocking") for item in actions):
        print("ERROR: action queue may not contain blocking=true", file=sys.stderr)
        return 1
    if any(item.get("external") for item in actions) or queue["external_tasks"]:
        print("ERROR: external task classification is prohibited", file=sys.stderr)
        return 1
    if any(item["state"] not in ACTION_STATES | TERMINAL_STATES for item in actions):
        print("ERROR: unknown action state", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
