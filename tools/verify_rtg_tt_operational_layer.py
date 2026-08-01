#!/usr/bin/env python3
"""Fail-closed verifier for the active StegVerse RTG-TT operational layer."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "ecosystem_management" / "rtg_tt_operational_layer.v0.1.json"
RECEIPT_PATH = ROOT / "brain_reports" / "rtg_tt_activation_receipt.json"
REPORT_PATH = ROOT / "brain_reports" / "rtg_tt_operational_layer_report.json"

EXPECTED_COMMITS = {
    "rtg_tests": "2fd7099bb3b6d2d7aa8ce7d72f7f71f6dfd4566a",
    "transition_table": "19720bae935ef9881ce5b239e0b66423fcd8bfab",
    "validation_factory": "5ca6ac0442809c5902f9765d2f865e5fa03d9c60",
}
EXPECTED_SITE_MERGE = "50d417b2dbf29d3812bdae8c3d1942b1ce5a5162"
EXPECTED_MAPPING = {
    "RESOLUTION_SATISFIED": "ALLOW",
    "FAIL_CLOSED": "DENY",
    "QUARANTINE": "DEFER",
}
AUTHORITY_KEYS = {
    "formalism", "allocation", "commitment", "execution",
    "custody", "publication", "release",
}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def load(path: Path, label: str, failures: list[str]) -> dict:
    if not path.exists():
        failures.append(f"missing {label}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid {label}: {exc}")
        return {}
    return value if isinstance(value, dict) else {}


def main() -> int:
    failures: list[str] = []
    state = load(STATE_PATH, "operational-layer state", failures)
    receipt = load(RECEIPT_PATH, "activation receipt", failures)

    if state.get("contract_version") != "rtg-tt-v0.1":
        failures.append("unexpected contract_version")
    if state.get("state") != "ACTIVE":
        failures.append("operational layer is not ACTIVE")

    sources = state.get("canonical_sources", {})
    for key, expected in EXPECTED_COMMITS.items():
        if sources.get(key, {}).get("commit") != expected:
            failures.append(f"canonical commit mismatch: {key}")

    if state.get("bounded_result_mapping") != EXPECTED_MAPPING:
        failures.append("bounded result mapping mismatch")

    authority = state.get("authority", {})
    if set(authority) != AUTHORITY_KEYS:
        failures.append("authority key set mismatch")
    for key in AUTHORITY_KEYS:
        if authority.get(key) is not False:
            failures.append(f"authority must remain false: {key}")

    coordination = state.get("coordination", {})
    required_refs = {
        "stegcore_issue", "ae_public_index", "site_projection",
        "admissibility_projection", "guardian_projection", "publisher_projection",
    }
    missing_refs = sorted(required_refs - set(coordination))
    if missing_refs:
        failures.append("missing coordination refs: " + ",".join(missing_refs))
    if coordination.get("site_projection") != f"StegVerse-Labs/Site@{EXPECTED_SITE_MERGE}":
        failures.append("Site mainline binding mismatch")

    observation = state.get("task_observation", {})
    for key in ("ledger", "observer", "workflow"):
        path = observation.get(key)
        if not path or not (ROOT / path).exists():
            failures.append(f"missing task-observation component: {key}")
    if observation.get("halt_allowed") is not False:
        failures.append("task observation must forbid halt")

    if state.get("activation_receipt") != "brain_reports/rtg_tt_activation_receipt.json":
        failures.append("activation receipt path mismatch")
    if state.get("activation_effect") is not True:
        failures.append("activation_effect must be true for ACTIVE layer")

    if receipt.get("state") != "ACTIVE" or receipt.get("activation_effect") is not True:
        failures.append("activation receipt does not establish ACTIVE state")
    if receipt.get("authority_effect") is not False:
        failures.append("activation receipt must not create authority")
    if receipt.get("site", {}).get("merge_commit") != EXPECTED_SITE_MERGE:
        failures.append("activation receipt Site merge mismatch")
    receipt_authority = receipt.get("authority", {})
    for key in AUTHORITY_KEYS:
        if receipt_authority.get(key) is not False:
            failures.append(f"activation receipt authority must remain false: {key}")

    report = {
        "schema_version": "0.2.0",
        "layer_id": state.get("layer_id"),
        "state": state.get("state"),
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "canonical_source_commits": EXPECTED_COMMITS,
        "site_merge_commit": EXPECTED_SITE_MERGE,
        "authority_effect": False,
        "activation_effect": state.get("activation_effect") is True and not failures,
        "halt_allowed": False,
    }
    report["report_hash"] = "sha256:" + hashlib.sha256(canonical(report)).hexdigest()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"STEGVERSE_RTG_TT_OPERATIONAL_LAYER_{report['status']}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
