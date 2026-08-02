#!/usr/bin/env python3
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "correctability"
REPORT = ROOT / "brain_reports" / "correctability_layer_report.json"
ALLOWED = {"pause", "deny", "revoke", "quarantine", "rollback", "redirect", "supersede", "compensate", "escalate"}


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def evaluate(record: dict) -> dict:
    required = {
        "correction_id", "transition_id", "authority", "intervention", "detected_at",
        "authorization_latency_ms", "intervention_latency_ms", "irreversible_at",
        "pathway_reachable", "intervention_enforceable", "scope_valid", "evidence_references"
    }
    errors = []
    missing = sorted(required - set(record))
    if missing:
        errors.append(f"missing_required:{','.join(missing)}")
        return {"admissible": False, "errors": errors}

    authority = record.get("authority", {})
    detected = parse_time(record["detected_at"])
    irreversible = parse_time(record["irreversible_at"])
    completion = detected + timedelta(milliseconds=record["authorization_latency_ms"] + record["intervention_latency_ms"])

    if record["intervention"] not in ALLOWED:
        errors.append("intervention_not_allowed")
    if not authority.get("valid", False):
        errors.append("authority_invalid")
    if not (parse_time(authority["not_before"]) <= detected <= parse_time(authority["not_after"])):
        errors.append("authority_outside_validity_window")
    if not record["pathway_reachable"]:
        errors.append("pathway_unreachable")
    if not record["intervention_enforceable"]:
        errors.append("intervention_unenforceable")
    if not record["scope_valid"]:
        errors.append("scope_invalid")
    if not record["evidence_references"]:
        errors.append("evidence_missing")
    if completion >= irreversible:
        errors.append("irreversible_boundary_reached")

    return {
        "admissible": not errors,
        "errors": errors,
        "completion_at": completion.isoformat(),
        "irreversible_at": irreversible.isoformat()
    }


def main() -> int:
    expected = {"valid.json": True, "late.json": False, "invalid_authority.json": False}
    cases = []
    ok = True
    for name, expected_admissible in expected.items():
        data = json.loads((FIXTURES / name).read_text())
        result = evaluate(data)
        passed = result["admissible"] == expected_admissible
        ok = ok and passed
        cases.append({"fixture": name, "expected_admissible": expected_admissible, "passed": passed, "result": result})

    report = {
        "layer": "governed_correctability",
        "status": "pass" if ok else "fail",
        "verification_command": "python tools/verify_correctability_layer.py",
        "cases": cases
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
