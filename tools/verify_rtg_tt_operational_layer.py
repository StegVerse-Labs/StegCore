#!/usr/bin/env python3
"""Fail-closed verifier for the StegVerse RTG-TT operational layer."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "ecosystem_management" / "rtg_tt_operational_layer.v0.1.json"
REPORT_PATH = ROOT / "brain_reports" / "rtg_tt_operational_layer_report.json"

EXPECTED_COMMITS = {
    "rtg_tests": "2fd7099bb3b6d2d7aa8ce7d72f7f71f6dfd4566a",
    "transition_table": "19720bae935ef9881ce5b239e0b66423fcd8bfab",
    "validation_factory": "5ca6ac0442809c5902f9765d2f865e5fa03d9c60",
}
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


def main() -> int:
    failures: list[str] = []
    if not STATE_PATH.exists():
        failures.append("missing operational-layer state")
        state: dict = {}
    else:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))

    if state.get("contract_version") != "rtg-tt-v0.1":
        failures.append("unexpected contract_version")

    sources = state.get("canonical_sources", {})
    for key, expected in EXPECTED_COMMITS.items():
        observed = sources.get(key, {}).get("commit")
        if observed != expected:
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

    if state.get("activation_effect") is not False:
        failures.append("activation_effect must remain false before activation receipt")

    report = {
        "schema_version": "0.1.0",
        "layer_id": state.get("layer_id"),
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "canonical_source_commits": EXPECTED_COMMITS,
        "authority_effect": False,
        "activation_effect": False,
    }
    report["report_hash"] = "sha256:" + hashlib.sha256(canonical(report)).hexdigest()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"STEGVERSE_RTG_TT_OPERATIONAL_LAYER_{report['status']}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
