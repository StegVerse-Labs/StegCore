#!/usr/bin/env python3
"""Evaluate a StegCore recreation gate request fail-closed."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import jsonschema


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    parser.add_argument("--request-schema", type=Path, required=True)
    parser.add_argument("--receipt-schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    request = load(args.request)
    request_schema = load(args.request_schema)
    receipt_schema = load(args.receipt_schema)

    jsonschema.Draft202012Validator(
        request_schema,
        format_checker=jsonschema.FormatChecker(),
    ).validate(request)

    checks = {
        "recreation_complete": request["recreation_complete"],
        "recovery_proof_complete": request["recovery_proof_complete"],
        "verification_margin_complete": request["verification_margin_complete"],
        "external_exposures_complete": request["external_exposures_complete"],
        "state_hash_match": request["trusted_pre_state_hash"] == request["recreated_state_hash"],
        "divergence_resolved": (
            not request["divergence_detected"]
            or request["divergence_resolution_status"] == "resolved_by_admissible_transition"
        ),
        "authority_current": request["authority_current"],
        "consent_current": request["consent_current"],
        "policy_current": request["policy_current"],
        "unresolved_conditions_evaluated": request["unresolved_conditions_evaluated"],
    }

    failed = [name for name, passed in checks.items() if not passed]
    receipt = {
        "gate_id": f"recreation-gate:{request['request_id']}",
        "request_id": request["request_id"],
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "decision": "ALLOW" if not failed else "BLOCK",
        "standing_basis": "SV-CONTINUITY-109 evidence evaluated under StegCore fail-closed recreation gate",
        "checks": checks,
        "reasons": [] if not failed else [f"failed:{name}" for name in failed],
        "source_refs": [
            request["continuity_receipt_ref"],
            request["recovery_receipt_ref"],
            request["divergence_report_ref"],
        ],
    }

    jsonschema.Draft202012Validator(
        receipt_schema,
        format_checker=jsonschema.FormatChecker(),
    ).validate(receipt)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["decision"] == "ALLOW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
