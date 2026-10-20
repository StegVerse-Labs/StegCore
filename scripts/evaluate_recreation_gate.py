#!/usr/bin/env python3
"""Evaluate a StegCore recreation gate request fail-closed."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

# Vendored StegVerse-SDK structural validator (contract 1.6, stdlib only); loaded by
# path so this script runs without installing StegCore or any third-party package.
VALIDATOR_PATH = Path(__file__).resolve().parents[1] / "src" / "stegcore" / "_vendor" / "structural_validator.py"


class SchemaError(ValueError):
    """A schema the vendored validator refuses (invalid or outside its contract)."""


class ValidationError(ValueError):
    """An instance with structural findings against an admitted schema."""


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_validator():
    spec = importlib.util.spec_from_file_location("_stegcore_vendored_structural_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def admit(validator, schema) -> str:
    """Return the schema digest, or raise SchemaError: unsupported keywords/formats fail closed."""
    digest = hashlib.sha256(validator.canonical_bytes(schema)).hexdigest()
    admitted = validator.check_schema(schema, digest)
    if not admitted["valid"]:
        raise SchemaError([f"{e['path'] or '/'}:{e['code']}" for e in admitted["errors"]])
    return digest


def findings(validator, instance, schema, digest) -> list[str]:
    result = validator.validate(instance, schema, digest)
    return sorted(f"{e['path'] or '/'}:{e['code']}" for e in result["errors"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    parser.add_argument("--request-schema", type=Path, required=True)
    parser.add_argument("--receipt-schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        request = load(args.request)
        request_schema = load(args.request_schema)
        receipt_schema = load(args.receipt_schema)
        validator = load_validator()
        request_digest = admit(validator, request_schema)
        receipt_digest = admit(validator, receipt_schema)
    except (OSError, ImportError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({
            "disposition": "FAIL_CLOSED",
            "failed_predicate": "RECREATION_SOURCE_EVIDENCE_VALID",
            "error_type": type(exc).__name__,
            "authority_effect": "NONE",
        }, sort_keys=True))
        return 2
    try:
        # format date/date-time is asserted by the vendored contract (FormatChecker parity).
        request_errors = findings(validator, request, request_schema, request_digest)
    except (TypeError, ValueError, KeyError, RecursionError) as exc:
        print(json.dumps({
            "disposition": "FAIL_CLOSED",
            "failed_predicate": "RECREATION_REQUEST_SCHEMA_VALID",
            "error_type": type(exc).__name__,
            "authority_effect": "NONE",
        }, sort_keys=True))
        return 2
    if request_errors:
        print(json.dumps({
            "disposition": "FAIL_CLOSED",
            "failed_predicate": "RECREATION_REQUEST_SCHEMA_VALID",
            "errors": request_errors,
            "authority_effect": "NONE",
        }, sort_keys=True))
        return 2

    try:
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

    except (KeyError, TypeError, ValueError, RecursionError) as exc:
        print(json.dumps({
            "disposition": "FAIL_CLOSED",
            "failed_predicate": "RECREATION_REQUEST_REQUIRED_EVIDENCE_PRESENT",
            "error_type": type(exc).__name__,
            "authority_effect": "NONE",
        }, sort_keys=True))
        return 2

    try:
        receipt_errors = findings(validator, receipt, receipt_schema, receipt_digest)
        if receipt_errors:
            raise ValidationError(receipt_errors)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, TypeError, ValueError, RecursionError) as exc:
        print(json.dumps({
            "disposition": "FAIL_CLOSED",
            "failed_predicate": "RECREATION_RECEIPT_VALID_AND_PERSISTED",
            "error_type": type(exc).__name__,
            "authority_effect": "NONE",
        }, sort_keys=True))
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["decision"] == "ALLOW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
