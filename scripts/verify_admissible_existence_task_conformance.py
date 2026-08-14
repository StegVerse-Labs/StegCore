#!/usr/bin/env python3
"""Canonical HANDOFF + Worker Task Registry Admissible-Existence verifier.

The verifier is intentionally data-oriented. It does not replace StegGate, infer
activation, execute work, mint receipts, or use credentials. It checks that
continuation surfaces faithfully describe work under the canonical AE lifecycle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


POLICY_PATH = Path("management/admissible-existence-task-conformance-policy.json")


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_obj(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def validate_task(task: dict[str, Any], *, surface: str, policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_key = "handoff_required_fields" if surface == "HANDOFF" else "registry_required_fields"
    required = policy[required_key]
    for field in required:
        if field not in task or not _nonempty(task[field]):
            # activation proof is intentionally nullable until ACTIVATED.
            if field == "activation_proof_ref" and task.get("ae_phase") != "ACTIVATED":
                continue
            errors.append(f"{surface}:{task.get('task_id') or task.get('goal_id') or '<unknown>'}:missing:{field}")

    horizon = task.get("task_horizon")
    if horizon not in policy["task_horizons"]:
        errors.append(f"{surface}:{task.get('task_id') or task.get('goal_id')}:invalid_task_horizon:{horizon}")

    phase = task.get("ae_phase")
    if phase not in policy["ae_phases"]:
        errors.append(f"{surface}:{task.get('task_id') or task.get('goal_id')}:invalid_ae_phase:{phase}")
        return errors

    state = task.get("operational_state", task.get("state"))
    evidence = task.get("evidence_refs") or []
    standing = task.get("standing_evidence_refs") or evidence
    admissibility = task.get("admissibility_evidence_refs") or evidence
    activation = task.get("activation_proof_ref")
    rules = policy["phase_rules"][phase]

    if rules["standing_required"] and not standing:
        errors.append(f"{surface}:{task.get('task_id') or task.get('goal_id')}:standing_evidence_required")
    if rules["admissibility_required"] and not admissibility:
        errors.append(f"{surface}:{task.get('task_id') or task.get('goal_id')}:admissibility_evidence_required")
    if rules["activation_required"] and not _nonempty(activation):
        errors.append(f"{surface}:{task.get('task_id') or task.get('goal_id')}:activation_proof_required")

    if state in policy["terminal_operational_states"] and phase == "DECLARED":
        errors.append(f"{surface}:{task.get('task_id') or task.get('goal_id')}:terminal_state_cannot_remain_declared")

    if phase == "ACTIVATED" and task.get("blockers"):
        errors.append(f"{surface}:{task.get('task_id') or task.get('goal_id')}:activated_with_blockers")

    if surface == "HANDOFF":
        if task.get("credential_authority") != policy["credential_authority"]:
            errors.append(f"HANDOFF:{task.get('goal_id')}:credential_authority_must_be_TV_TVC")
        if task.get("github_token_runtime_authority") is not False:
            errors.append(f"HANDOFF:{task.get('goal_id')}:github_token_runtime_authority_must_be_false")

    if state in policy["active_operational_states"] and not _nonempty(task.get("continuation_owner")):
        errors.append(f"{surface}:{task.get('task_id') or task.get('goal_id')}:active_task_requires_continuation_owner")

    if horizon == "future" and state in policy["terminal_operational_states"]:
        errors.append(f"{surface}:{task.get('task_id') or task.get('goal_id')}:future_task_cannot_be_terminal")

    return errors


def validate_handoff(document: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("artifact_type") != "stegcore.admissible_existence_handoff_conformance_manifest":
        errors.append("HANDOFF:invalid_artifact_type")
    tasks = document.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return errors + ["HANDOFF:tasks_required"]
    seen: set[str] = set()
    for task in tasks:
        goal_id = task.get("goal_id")
        if not goal_id or goal_id in seen:
            errors.append(f"HANDOFF:duplicate_or_missing_goal_id:{goal_id}")
        seen.add(goal_id)
        errors.extend(validate_task(task, surface="HANDOFF", policy=policy))
    return errors


def normalize_registry_worker(worker: dict[str, Any]) -> dict[str, Any]:
    result = dict(worker)
    result.setdefault("task_id", worker.get("task_id") or worker.get("worker_id"))
    result.setdefault("owner", worker.get("owner") or worker.get("worker_id"))
    result.setdefault("collision_boundary", worker.get("collision_boundary"))
    result.setdefault("expected_evidence", worker.get("expected_evidence", []))
    return result


def validate_registry(document: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("artifact_type") != "stegverse_worker_task_registry":
        errors.append("WORKER_TASK_REGISTRY:invalid_artifact_type")
    workers = document.get("workers")
    if not isinstance(workers, list) or not workers:
        return errors + ["WORKER_TASK_REGISTRY:workers_required"]
    seen: set[str] = set()
    for raw in workers:
        task = normalize_registry_worker(raw)
        task_id = task.get("task_id")
        if not task_id or task_id in seen:
            errors.append(f"WORKER_TASK_REGISTRY:duplicate_or_missing_task_id:{task_id}")
        seen.add(task_id)
        errors.extend(validate_task(task, surface="WORKER_TASK_REGISTRY", policy=policy))
    return errors


def build_receipt(*, policy: dict[str, Any], handoff: dict[str, Any], registry: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    status = "PASS" if not errors else "FAIL_CLOSED"
    return {
        "artifact_type": "stegcore.admissible_existence_task_conformance_receipt",
        "schema_version": "1.0",
        "policy_id": policy["policy_id"],
        "status": status,
        "surfaces": ["HANDOFF", "WORKER_TASK_REGISTRY"],
        "handoff_sha256": sha256_obj(handoff),
        "worker_task_registry_sha256": sha256_obj(registry),
        "policy_sha256": sha256_obj(policy),
        "errors": errors,
        "activation_inferred": False,
        "external_execution_performed": False,
        "credential_authority": "TV/TVC",
        "github_token_runtime_authority": False,
    }


def verify(handoff_path: Path, registry_path: Path, policy_path: Path = POLICY_PATH) -> dict[str, Any]:
    policy = load_json(policy_path)
    handoff = load_json(handoff_path)
    registry = load_json(registry_path)
    errors = validate_handoff(handoff, policy) + validate_registry(registry, policy)
    return build_receipt(policy=policy, handoff=handoff, registry=registry, errors=errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handoff", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--policy", default=POLICY_PATH, type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    receipt = verify(args.handoff, args.registry, args.policy)
    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
