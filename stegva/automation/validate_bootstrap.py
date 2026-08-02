#!/usr/bin/env python3
"""Fail-closed StegVA bootstrap validator.

Validates committed machine-owned task state, canonical contracts, required
continuity/specification records, and synthetic-only fixtures without third-party
packages. It never processes production veteran data.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "stegva" / "task_registry.json"
CONTROL_MAP = ROOT / "stegva" / "compliance" / "current_law_control_map.json"
CONTRACTS = [
    ROOT / "stegva" / "contracts" / "synthetic_intake.schema.json",
    ROOT / "stegva" / "contracts" / "cross_repo_exchange_receipt.schema.json",
    ROOT / "stegva" / "contracts" / "public_finance_event.schema.json",
]
TEXT_RECORDS = [
    ROOT / "docs" / "STEGVA_MIRROR_HANDOFF.md",
    ROOT / "docs" / "STEGVA_VAWATCHDOG_PARALLEL_WORK_RECEIPT.md",
    ROOT / "stegva" / "docs" / "SPLIT_IDENTITY_THREAT_MODEL.md",
    ROOT / "stegva" / "docs" / "PUBLIC_FINANCE_LEDGER_SPEC.md",
]
VALID_FIXTURE = ROOT / "stegva" / "examples" / "synthetic_intake.valid.json"
INVALID_FIXTURE = ROOT / "stegva" / "examples" / "synthetic_intake.invalid-production.json"
OUTPUT = ROOT / "stegva" / "receipts" / "bootstrap-verification.json"
ALLOWED_STATES = {"COMPLETE", "BLOCKED", "RETRY", "REVIEW_REQUIRED", "FAILED"}
ALLOWED_CONTROL_STATES = {"COMPLETE", "IMPLEMENTED_UNVALIDATED", "MISSING", "BLOCKED", "REVIEW_REQUIRED"}


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
    if registry.get("goal_id") != "STEGVA-BOOTSTRAP-001":
        errors.append("registry goal_id must be STEGVA-BOOTSTRAP-001")
    if registry.get("owner_repository") != "StegVerse-Labs/StegCore":
        errors.append("registry owner_repository must remain StegVerse-Labs/StegCore until transfer")
    if registry.get("production_data_allowed") is not False:
        errors.append("production_data_allowed must be false")
    if set(registry.get("states", [])) != ALLOWED_STATES:
        errors.append("registry states must exactly declare COMPLETE/BLOCKED/RETRY/REVIEW_REQUIRED/FAILED")
    tasks = registry.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("registry tasks must be a non-empty list")
        return errors
    ids: set[str] = set()
    locations: set[str] = set()
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
        status = task.get("status")
        if status not in ALLOWED_STATES:
            errors.append(f"task {task_id} has invalid status")
        location = task.get("location")
        if not location or not task.get("owner"):
            errors.append(f"task {task_id} must name location and owner")
        elif location in locations and status == "COMPLETE":
            errors.append(f"duplicate completed task location: {location}")
        else:
            locations.add(str(location))
        if status == "COMPLETE" and not task.get("completion_evidence"):
            errors.append(f"complete task {task_id} must define completion_evidence")
        if status != "COMPLETE" and not task.get("release_condition"):
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


def validate_control_map(control_map: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "control_map_version", "goal_id", "owner_repository", "as_of",
        "production_authorization", "review_status", "controls",
        "required_human_reviews", "next_machine_task",
    }
    missing = sorted(required - control_map.keys())
    if missing:
        errors.append(f"control map missing keys: {missing}")
    if control_map.get("production_authorization") is not False:
        errors.append("control map must deny production authorization")
    if control_map.get("review_status") != "REVIEW_REQUIRED":
        errors.append("control map review_status must remain REVIEW_REQUIRED until qualified review")
    controls = control_map.get("controls")
    if not isinstance(controls, list) or not controls:
        errors.append("control map controls must be a non-empty list")
        return errors
    ids: set[str] = set()
    for index, control in enumerate(controls):
        if not isinstance(control, dict):
            errors.append(f"control[{index}] must be an object")
            continue
        control_id = control.get("control_id")
        if not isinstance(control_id, str) or not control_id:
            errors.append(f"control[{index}] missing control_id")
        elif control_id in ids:
            errors.append(f"duplicate control_id: {control_id}")
        else:
            ids.add(control_id)
        if control.get("implementation_status") not in ALLOWED_CONTROL_STATES:
            errors.append(f"control {control_id} has invalid implementation_status")
        urls = control.get("source_urls")
        if not isinstance(urls, list) or not urls or any(not isinstance(url, str) or not url.startswith("https://") for url in urls):
            errors.append(f"control {control_id} must name official HTTPS source URLs")
        if not control.get("implementation_location") or not control.get("release_condition"):
            errors.append(f"control {control_id} must name implementation_location and release_condition")
    return errors


def validate_synthetic_fixture(value: dict[str, Any], *, expected_valid: bool) -> list[str]:
    errors: list[str] = []
    is_synthetic = value.get("synthetic") is True
    consent = value.get("consent") if isinstance(value.get("consent"), dict) else {}
    evidence = value.get("evidence_items") if isinstance(value.get("evidence_items"), list) else []
    all_evidence_synthetic = bool(evidence) and all(isinstance(item, dict) and item.get("synthetic") is True for item in evidence)
    record_ok = isinstance(value.get("record_id"), str) and bool(re.fullmatch(r"SYN-[A-Z0-9-]{8,64}", value["record_id"]))
    accepted = (
        value.get("schema_version") == "1.0.0"
        and is_synthetic
        and record_ok
        and consent.get("purpose") == "stegva_synthetic_demonstration"
        and consent.get("granted") is True
        and all_evidence_synthetic
    )
    if expected_valid and not accepted:
        errors.append("valid synthetic intake fixture was rejected")
    if not expected_valid and accepted:
        errors.append("production-data rejection fixture was incorrectly accepted")
    return errors


def validate_text_record(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing required continuity/specification record: {path.relative_to(ROOT)}"]
    text = path.read_text(encoding="utf-8")
    if len(text.strip()) < 500:
        errors.append(f"{path.relative_to(ROOT)} appears to be a stub")
    if "Production authorization" in text and "DENIED" not in text and "NOT AUTHORIZED" not in text:
        errors.append(f"{path.relative_to(ROOT)} does not clearly deny production authorization")
    return errors


def main() -> int:
    errors: list[str] = []
    inputs: dict[str, str] = {}
    try:
        registry = load_json(REGISTRY)
        inputs[str(REGISTRY.relative_to(ROOT))] = sha256(REGISTRY)
        errors.extend(validate_registry(registry))

        control_map = load_json(CONTROL_MAP)
        inputs[str(CONTROL_MAP.relative_to(ROOT))] = sha256(CONTROL_MAP)
        errors.extend(validate_control_map(control_map))

        for path in CONTRACTS:
            schema = load_json(path)
            inputs[str(path.relative_to(ROOT))] = sha256(path)
            errors.extend(validate_contract(path, schema))

        valid_fixture = load_json(VALID_FIXTURE)
        invalid_fixture = load_json(INVALID_FIXTURE)
        inputs[str(VALID_FIXTURE.relative_to(ROOT))] = sha256(VALID_FIXTURE)
        inputs[str(INVALID_FIXTURE.relative_to(ROOT))] = sha256(INVALID_FIXTURE)
        errors.extend(validate_synthetic_fixture(valid_fixture, expected_valid=True))
        errors.extend(validate_synthetic_fixture(invalid_fixture, expected_valid=False))

        for path in TEXT_RECORDS:
            errors.extend(validate_text_record(path))
            if path.is_file():
                inputs[str(path.relative_to(ROOT))] = sha256(path)
    except ValueError as exc:
        errors.append(str(exc))

    status = "COMPLETE" if not errors else "FAILED"
    receipt = {
        "receipt_version": "1.1.0",
        "goal_id": "STEGVA-BOOTSTRAP-001",
        "owner_repository": "StegVerse-Labs/StegCore",
        "status": status,
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "production_data_processed": False,
        "production_authorization": False,
        "inputs_sha256": dict(sorted(inputs.items())),
        "errors": errors,
        "next_task": (
            "inspect hosted workflow job, logs, and receipt artifact; then transfer to the dedicated StegVA repository when available"
            if not errors
            else "correct validation failures and retry"
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
