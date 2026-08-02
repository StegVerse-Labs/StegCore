#!/usr/bin/env python3
"""Fail-closed StegVA bootstrap validator.

Validates committed machine-owned task state and canonical contract structure without
requiring third-party packages. It never processes production veteran data.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "stegva" / "task_registry.json"
CONTRACTS = [
    ROOT / "stegva" / "contracts" / "synthetic_intake.schema.json",
    ROOT / "stegva" / "contracts" / "cross_repo_exchange_receipt.schema.json",
    ROOT / "stegva" / "contracts" / "public_finance_event.schema.json",
]
HANDOFF = ROOT / "docs" / "STEGVA_MIRROR_HANDOFF.md"
BOUNDARY_RECEIPT = ROOT / "docs" / "STEGVA_VAWATCHDOG_PARALLEL_WORK_RECEIPT.md"
OUTPUT = ROOT / "stegva" / "receipts" / "bootstrap-verification.json"
ALLOWED_STATES = {"COMPLETE", "BLOCKED", "RETRY", "REVIEW_REQUIRED", "FAILED"}


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing required file: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"top-level object required: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "registry_version", "goal_id", "owner_repository", "active_goal",
        "states", "tasks", "next_executable_task", "duplicate_execution_key",
        "production_data_allowed",
    }
    missing = sorted(required - registry.keys())
    if missing:
        errors.append(f"registry missing keys: {missing}")
    if registry.get("production_data_allowed") is not False:
        errors.append("production_data_allowed must be false")
    if set(registry.get("states", [])) != ALLOWED_STATES:
        errors.append("registry states must exactly declare COMPLETE/BLOCKED/RETRY/REVIEW_REQUIRED/FAILED")
    tasks = registry.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("registry tasks must be a non-empty list")
        return errors
    ids: set[str] = set()
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"task[{index}] must be an object")
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id:
            errors.append(f"task[{index}] missing id")
        elif task_id in ids:
            errors.append(f"duplicate task id: {task_id}")
        else:
            ids.add(task_id)
        if task.get("status") not in ALLOWED_STATES:
            errors.append(f"task {task_id} has invalid status")
        if not task.get("location") or not task.get("owner"):
            errors.append(f"task {task_id} must name location and owner")
        if task.get("status") != "COMPLETE" and not task.get("release_condition"):
            errors.append(f"incomplete task {task_id} must define release_condition")
    if registry.get("next_executable_task") not in ids:
        errors.append("next_executable_task must reference a declared task")
    return errors


def validate_contract(path: Path, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append(f"{path.name}: unsupported or missing JSON Schema dialect")
    if schema.get("type") != "object":
        errors.append(f"{path.name}: top-level type must be object")
    if schema.get("additionalProperties") is not False:
        errors.append(f"{path.name}: must fail closed with additionalProperties=false")
    required = schema.get("required")
    properties = schema.get("properties")
    if not isinstance(required, list) or not required:
        errors.append(f"{path.name}: required must be non-empty")
    if not isinstance(properties, dict) or not properties:
        errors.append(f"{path.name}: properties must be non-empty")
    elif isinstance(required, list):
        undeclared = sorted(set(required) - properties.keys())
        if undeclared:
            errors.append(f"{path.name}: required keys not declared in properties: {undeclared}")
    version = properties.get("schema_version", {}) if isinstance(properties, dict) else {}
    if version.get("const") != "1.0.0":
        errors.append(f"{path.name}: schema_version const must be 1.0.0")
    return errors


def main() -> int:
    errors: list[str] = []
    inputs: dict[str, str] = {}
    try:
        registry = load_json(REGISTRY)
        inputs[str(REGISTRY.relative_to(ROOT))] = sha256(REGISTRY)
        errors.extend(validate_registry(registry))
        for path in CONTRACTS:
            schema = load_json(path)
            inputs[str(path.relative_to(ROOT))] = sha256(path)
            errors.extend(validate_contract(path, schema))
        for path in (HANDOFF, BOUNDARY_RECEIPT):
            if not path.is_file():
                errors.append(f"missing required continuity record: {path.relative_to(ROOT)}")
            else:
                inputs[str(path.relative_to(ROOT))] = sha256(path)
    except ValueError as exc:
        errors.append(str(exc))

    status = "COMPLETE" if not errors else "FAILED"
    receipt = {
        "receipt_version": "1.0.0",
        "goal_id": "STEGVA-BOOTSTRAP-001",
        "owner_repository": "StegVerse-Labs/StegCore",
        "status": status,
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "production_data_processed": False,
        "inputs_sha256": inputs,
        "errors": errors,
        "next_task": "observe hosted workflow and transfer bootstrap to dedicated StegVA repository when available" if not errors else "correct validation failures and retry",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
