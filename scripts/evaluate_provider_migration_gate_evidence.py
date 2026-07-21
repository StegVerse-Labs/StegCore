#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from stegcore.provider_migration_gate_evidence import evaluate_provider_migration_gate_evidence


def blocked(reason: str):
    return {
        "schema": "stegverse.stegcore.provider_migration_gate_evidence_admissibility.v1",
        "decision": "DENY",
        "evidence_only": True,
        "provider_count": 0,
        "verified_gate_count": 0,
        "blocked_gate_count": 0,
        "provider_results": [],
        "reasons": [reason],
        "source_registry_hash": None,
        "manual_action_required": False,
        "production_mutation_allowed": False,
        "execution_authority": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "continuity_receipt_minted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    source = Path(args.source)
    if not source.exists():
        result = blocked("source_registry_unavailable")
    else:
        try:
            result = evaluate_provider_migration_gate_evidence(json.loads(source.read_text()))
        except Exception as exc:
            result = blocked(f"source_registry_parse_failed:{type(exc).__name__}")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
